#!/usr/bin/env python3
"""Submit a finished skill package for review — from a script, never from the model.

WHY THIS IS A SCRIPT AND NOT A REQUEST THE AGENT WRITES
=======================================================
Two things in a submission must come from code. Both break quietly if they come from a model,
which is worse than breaking loudly.

1. THE PACKAGE BYTES. A submission carries the package base64-encoded. Measured against the
   documented limits:

       5 MB ZIP  (the cap)      -> 6.67 MB of base64  -> roughly 1.9-2.7 MILLION tokens
       250 KB SKILL.md (the cap)-> 0.33 MB of base64  -> roughly 95-133 THOUSAND tokens

   A 200k-token context holds about 375 KB of source package. The ZIP ceiling is 13x that, and
   even the MARKDOWN-only ceiling would consume half a context. So inlining is not "fine for
   small files and broken for big ones" — it fails at the contract's own published limits.

   And it fails in the worst available way: the model emits a truncated base64 string, the
   server decodes a short buffer, and the result reads as a MALFORMED ARCHIVE rather than as a
   context limit. The creator is told their zip is corrupt. So the bytes are read from disk,
   encoded here, and never enter the conversation.

2. RETRYSECRET. It is a 64-hex capability token — the bearer proof for a private receipt. A
   model asked for 64 hex characters is sampling a token distribution, not a CSPRNG: the output
   can be predictable and can repeat across sessions, and neither failure is visible. It comes
   from `secrets.token_hex(32)` here. `requestId` is the milder case — a UUID is
   collision-tolerant and the server rejects replays — but it lives in the same place for the
   same reason.

   THE GENERAL RULE: anything that needs exact bytes or real randomness comes from code, never
   from the model.

WHY SENDING REQUIRES A PREVIEW FIRST
====================================
This tool weakens the strongest promise in the kit — that nothing is submitted on the creator's
behalf. The replacement promise is that nothing is submitted WITHOUT THEIR EXPLICIT CONFIRMATION,
and a promise that only exists in prose is enforced nowhere.

So `send` requires a confirm token that only `preview` prints, and the token is derived from the
package digest plus the creator identity being sent. An agent cannot send without having first
rendered exactly what would be sent, and if the package changes after the preview the token stops
matching. It is not proof a human read the screen — nothing over an API can be — but it does make
"show, then ask, then send" the only sequence that works.

WHY AN UNAUTHENTICATED ENDPOINT IS ACCEPTABLE HERE
==================================================
Identity is self-asserted in the payload and consent is a boolean this script sets, so nothing
here proves a human agreed to anything. That is bounded, not ignored: **manual identity
verification gates publication**, and publication is the only irreversible step. The worst case
for a forged submission is a junk row in a review queue. Do not add authentication to the door
without also keeping the gate — the gate is what makes the door safe.

Exit codes match the rest of the kit:
  0  submitted for review
  1  internal error in this tool
  2  invalid invocation, or a missing confirm token
  4  the server rejected the submission (its code and message are reported verbatim)
  5  the server could not be reached; nothing was submitted
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import sys
import urllib.error
import urllib.request
import uuid

EXIT_OK, EXIT_INTERNAL, EXIT_VALIDATION, EXIT_REJECTED, EXIT_NETWORK = 0, 1, 2, 4, 5

# The server's documented ceilings. Checked HERE, before encoding, for the same reason the
# credential scan runs before transmission: a 5 MB package becomes a 6.67 MB request body, and
# discovering it is one byte over after uploading all of it wastes the upload and returns a
# `package_too_large` a creator has to interpret. Named limits, refused locally, with the actual
# measured size in the message.
#
# The server stays authoritative — these are its numbers, not ours. If it lowers a cap and this
# copy is stale, the server still rejects and the message is still correct about what happened.
MAX_ZIP_BYTES = 5 * 1024 * 1024
MAX_MARKDOWN_BYTES = 250 * 1024

# The consent the creator must have seen. Kept here verbatim so the preview cannot show one thing
# while the request asserts another.
CONSENT = (
    "Clay may publish this skill and your public attribution; may edit it for clarity, house "
    "voice and formatting while the substance stays yours; may publish it in a public repository "
    "under an open licence where others may use and adapt it with attribution; and your "
    "attribution and content may persist in git history and in third-party forks after Clay "
    "removes the current files."
)


def _envelope(code: str, message: str, exit_code: int) -> int:
    print(json.dumps({"error": {"code": code, "message": message}}), file=sys.stderr)
    return exit_code


def _inventory(path: str) -> tuple[bytes, str, list[dict]]:
    """The package bytes, its kind, and a file inventory — read from disk, in sorted order."""
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            blob = fh.read()
        kind = "zip" if path.endswith(".zip") else "markdown"
        return blob, kind, [{"path": os.path.basename(path), "bytes": len(blob)}]
    if not os.path.isdir(path):
        raise FileNotFoundError(path)
    # A directory is submitted as its SKILL.md when that is all there is, and otherwise the
    # caller is expected to have zipped it — this tool does not build archives, because the
    # package tool already does and two implementations would drift.
    files = sorted(os.path.relpath(os.path.join(dp, f), path).replace(os.sep, "/")
                   for dp, _, fn in os.walk(path) for f in fn)
    if files == ["SKILL.md"]:
        with open(os.path.join(path, "SKILL.md"), "rb") as fh:
            blob = fh.read()
        return blob, "markdown", [{"path": "SKILL.md", "bytes": len(blob)}]
    raise ValueError(
        f"{path} holds {len(files)} files. Zip it first with "
        f"`package_skill.py zip {path} <slug>.zip`, then submit the zip — this tool does not "
        f"build archives, so there is only one implementation of the package format."
    )


def _too_large(blob: bytes, kind: str) -> str | None:
    """The refusal message if this package is over the documented cap, else None."""
    cap = MAX_ZIP_BYTES if kind == "zip" else MAX_MARKDOWN_BYTES
    if len(blob) <= cap:
        return None
    return (f"the package is {len(blob) / 1024 / 1024:.2f} MB and the limit for a {kind} "
            f"submission is {cap / 1024 / 1024:.2f} MB. Nothing was sent. Trim it, or split "
            f"supporting material out, and submit again — the encoded request would have been "
            f"{len(blob) * 4 / 3 / 1024 / 1024:.2f} MB.")


def _slug(blob: bytes, kind: str) -> str | None:
    if kind != "markdown":
        return None
    for line in blob.decode("utf-8", "replace").split("\n"):
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def _profile(raw: str) -> dict:
    p = json.loads(raw)
    missing = [k for k in ("fullName", "workEmail") if not p.get(k)]
    if missing:
        raise ValueError(f"creator profile is missing required fields: {missing}")
    return p


def _confirm_token(digest: str, profile: dict) -> str:
    """Binds the confirmation to THIS package and THIS identity.

    Derived rather than random on purpose: `send` can recompute it without state, and a package
    edited after the preview produces a different digest and therefore a token that no longer
    matches. That turns "the creator was shown what would be sent" into a checkable condition.
    """
    material = digest + "\n" + json.dumps(profile, sort_keys=True)
    return hashlib.sha256(material.encode()).hexdigest()[:16]


def preview(args) -> int:
    blob, kind, inventory = _inventory(args.package)
    digest = hashlib.sha256(blob).hexdigest()
    profile = _profile(args.profile)
    out = {
        "will_send": {
            "endpoint": args.endpoint or "<not set — pass --endpoint>",
            "sourceInputMethod": "agent_api",
            "packageKind": kind,
            "packageBytes": len(blob),
            "withinDocumentedLimit": _too_large(blob, kind) is None,
            "packageSha256": digest,
            "fileInventory": inventory,
            "skillSlugRequested": _slug(blob, kind),
            "creator": profile,
        },
        "consent_the_creator_must_have_seen": CONSENT,
        "not_sent": "Nothing has been submitted. This printed what WOULD be sent.",
        "confirm_token": _confirm_token(digest, profile),
        "next": ("Show the creator the block above, including the consent text, and ask whether to "
                 "submit. Only if they say yes: re-run with `send --confirm <confirm_token>`."),
    }
    print(json.dumps(out, indent=1))
    return EXIT_OK


def send(args) -> int:
    blob, kind, inventory = _inventory(args.package)
    digest = hashlib.sha256(blob).hexdigest()
    profile = _profile(args.profile)
    expected = _confirm_token(digest, profile)
    if args.confirm != expected:
        return _envelope(
            "confirmation_required",
            "The confirm token does not match this package and creator. Either no preview was "
            "shown, or the package changed after it was. Run `preview` again, show the creator "
            "what it prints, and use the token from that run.",
            EXIT_VALIDATION)
    oversize = _too_large(blob, kind)
    if oversize:
        return _envelope("package_too_large", oversize, EXIT_VALIDATION)
    if not args.rights_confirmed:
        return _envelope(
            "consent_not_confirmed",
            "Pass --rights-confirmed only after the creator has seen the consent text that "
            "`preview` printed and agreed to it.",
            EXIT_VALIDATION)

    body = {
        "sourceInputMethod": "agent_api",
        "requestId": str(uuid.uuid4()),          # from code: replay identity
        "retrySecret": secrets.token_hex(32),    # from code: a capability token, never sampled
        "packageKind": kind,
        "packageBase64": base64.b64encode(blob).decode(),   # never passes through a context
        "packageSha256": digest,
        "fileInventory": inventory,
        "creator": profile,
        "rightsConfirmed": True,
        "consentVersion": args.consent_version,
    }
    req = urllib.request.Request(
        args.endpoint, data=json.dumps(body).encode(),
        headers={"content-type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            payload = json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode() or "{}").get("error", {})
        except Exception:
            err = {}
        return _envelope(err.get("code") or f"http_{e.code}",
                         err.get("message") or "The server rejected the submission.",
                         EXIT_REJECTED)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return _envelope("unreachable",
                         f"Could not reach the submission endpoint ({e}). Nothing was submitted.",
                         EXIT_NETWORK)

    # The receipt carries the retry secret, so it is written to disk and its VALUE is never
    # printed — same rule as any other credential. The agent reports the path.
    receipt = {"receipt": payload, "retrySecret": body["retrySecret"],
               "requestId": body["requestId"], "packageSha256": digest}
    base_dir = os.path.dirname(os.path.abspath(args.package)) or "."
    slug = _slug(blob, kind) or "submission"
    path = os.path.join(base_dir, f"{slug}.receipt.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    os.chmod(path, 0o600)
    print(json.dumps({
        "state": payload.get("status") or "submitted_for_review",
        "submitted": True,
        "published": False,
        "receipt_written_to": path,
        "note": ("Submitted for review — not published. The receipt file holds a private retry "
                 "secret; its value is deliberately not printed here. A person reviews the "
                 "submission and verifies identity before anything is published."),
    }, indent=1))
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    for name, fn in (("preview", preview), ("send", send)):
        p = sub.add_parser(name)
        p.add_argument("package", help="the finished package: a .zip, or a directory holding only SKILL.md")
        p.add_argument("--profile", required=True,
                       help='creator profile as JSON: {"fullName":…,"workEmail":…,"company":…,'
                            '"linkedinUrl":…,"byline":…}')
        p.add_argument("--endpoint", default=None, help="the submission endpoint URL")
        p.add_argument("--consent-version", default="2026-08-18")
        p.add_argument("--timeout", type=float, default=120.0)
        if name == "send":
            p.add_argument("--confirm", required=True, help="the confirm_token printed by `preview`")
            p.add_argument("--rights-confirmed", action="store_true",
                           help="set only after the creator agreed to the consent text")
        p.set_defaults(fn=fn)
    args = ap.parse_args(argv)
    if args.mode == "send" and not args.endpoint:
        return _envelope("invalid_invocation", "send requires --endpoint.", EXIT_VALIDATION)
    try:
        return args.fn(args)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        return _envelope("invalid_invocation", str(e), EXIT_VALIDATION)
    except Exception as e:                                    # noqa: BLE001
        return _envelope("internal_error", f"{type(e).__name__}: {e}", EXIT_INTERNAL)


if __name__ == "__main__":
    sys.exit(main())
