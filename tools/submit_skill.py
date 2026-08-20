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

So `send` requires a confirm token that only `preview` can mint. The token is **random**, written
to a `0600` file with the package digest and creator identity it is bound to, and **consumed** on
use.

Each of those three properties answers a different attack, and the first one is a correction:

* **Random, not derived.** The first version computed the token as a hash of the package digest and
  the profile — a pure function of inputs the agent already holds, using code the agent can read.
  So `preview` could be skipped and the token derived, which made the token prove *what* would be
  sent and never *that anyone was asked*. The threat is instruction injection: a table
  configuration or a supporting file telling the agent to compute the hash and call `send` defeats
  a derived token entirely, and that is the exact case this rule exists for. Statelessness was a
  convenience; unpredictability is the security property.
* **Bound to the package and identity.** Edit either after the preview and the right token is
  still refused, because what the creator saw is no longer what would be sent.
* **Single-use.** A token captured from a transcript does not stay live.

It is still not proof a human read the screen — nothing over an API can be. What it is now is a
value that cannot be produced by anything which merely controls the request.

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
import re
import secrets
import sys
import urllib.error
import urllib.request
import uuid

EXIT_OK, EXIT_INTERNAL, EXIT_VALIDATION, EXIT_REJECTED, EXIT_NETWORK = 0, 1, 2, 4, 5

# Sent on every request. See the note at the request construction: the stdlib default is blocked
# by the WAF, so this is load-bearing rather than cosmetic. Keep it honest and identifiable — it is
# how the receiving side tells our traffic from a scraper's.
USER_AGENT = "clay-skill-author/1 (+https://github.com/sungwanjo-clay/clay-skill-creator)"

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


def _binding(digest: str, profile: dict) -> str:
    """What the confirmation is bound TO: this package, this identity."""
    material = digest + "\n" + json.dumps(profile, sort_keys=True)
    return hashlib.sha256(material.encode()).hexdigest()[:16]


def _pending_path(package: str) -> str:
    """Beside the package, never inside it, and one file per package.

    NOT inside: a directory package must contain only `SKILL.md` — `_inventory` refuses anything
    else — so a state file written into it would break the very submission it is confirming, and
    would be a candidate for being submitted.

    ONE PER PACKAGE, because a single fixed name in the shared parent collides: preview A, preview
    B, and A's token is refused. That fails safe but is baffling, and it was found by testing two
    packages in one directory rather than by reading the code.
    """
    abspath = os.path.abspath(package)
    base = os.path.dirname(abspath) or "."
    tag = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(abspath)) or "package"
    return os.path.join(base, f".submit-confirm-{tag}.json")


def _issue_confirm(package: str, digest: str, profile: dict) -> str:
    """Mint an UNPREDICTABLE confirmation token and record what it is bound to.

    THE TOKEN USED TO BE DERIVED, AND THAT WAS A DEFECT. It was
    `sha256(digest + sorted-profile)[:16]` — a pure function of inputs the agent already holds,
    computed by code the agent can read. So `send` could recompute it and `preview` could be
    skipped entirely, which means the token proved *what* would be sent and never *that anyone was
    asked*. The docstring claimed the stronger property; only the weaker one was true.

    That gap is the whole point, because the threat is instruction injection. A table
    configuration or a supporting file that tells the agent to compute the hash and call `send`
    defeats a derived token completely — and defeating exactly that is why the
    never-submit-without-an-explicit-yes rule exists.

    So the token is now random. Statelessness was a convenience; **unpredictability is the
    security property**, and a value that cannot be derived from the request cannot be minted by
    something that only controls the request.

    Both properties the derived version had are kept, because the binding is stored alongside:
    edit the package after the preview and the digest no longer matches, so the token is refused
    even though it is the right token.

    The file is `0600` and single-use — `send` consumes it. A replayed token fails on the second
    attempt, so a token captured from a transcript does not stay live.
    """
    token = secrets.token_hex(16)
    path = _pending_path(package)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"confirm_token": token, "binding": _binding(digest, profile)}, fh)
    os.chmod(path, 0o600)
    return token


def _redeem_confirm(package: str, token: str, digest: str, profile: dict) -> str | None:
    """Consume the pending confirmation. Returns None on success, else the reason it failed."""
    path = _pending_path(package)
    try:
        with open(path, encoding="utf-8") as fh:
            pending = json.load(fh)
    except (OSError, ValueError):
        return ("No pending confirmation for this package. `send` requires a token that `preview` "
                "minted — it cannot be computed from the package, deliberately, so that nothing "
                "which merely controls the request can produce one. Run `preview`, show the "
                "creator what it prints, and use the token from that run.")
    if not secrets.compare_digest(str(pending.get("confirm_token", "")), token):
        return ("That confirm token does not match the pending confirmation for this package. Run "
                "`preview` again and use the token it prints.")
    if pending.get("binding") != _binding(digest, profile):
        return ("The package or the creator details changed after the preview, so what the creator "
                "was shown is not what would be sent. Run `preview` again and show them the new "
                "version.")
    # Single-use: consumed on success, so a token seen once cannot be replayed.
    try:
        os.remove(path)
    except OSError:
        pass
    return None


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
        "confirm_token": _issue_confirm(args.package, digest, profile),
        "next": ("Show the creator the block above, including the consent text, and ask whether to "
                 "submit. Only if they say yes: re-run with `send --confirm <confirm_token>`."),
    }
    print(json.dumps(out, indent=1))
    return EXIT_OK


def send(args) -> int:
    blob, kind, inventory = _inventory(args.package)
    digest = hashlib.sha256(blob).hexdigest()
    profile = _profile(args.profile)
    refused = _redeem_confirm(args.package, args.confirm, digest, profile)
    if refused:
        return _envelope("confirmation_required", refused, EXIT_VALIDATION)
    oversize = _too_large(blob, kind)
    if oversize:
        return _envelope("package_too_large", oversize, EXIT_VALIDATION)
    if not args.rights_confirmed:
        return _envelope(
            "consent_not_confirmed",
            "Pass --rights-confirmed only after the creator has seen the consent text that "
            "`preview` printed and agreed to it.",
            EXIT_VALIDATION)

    # THE PAYLOAD FIELD NAME DEPENDS ON THE KIND, and getting it wrong fails obscurely.
    # The server takes `packageBase64` for a zip and `skillMdBase64` for a bare SKILL.md. It
    # validates that field conditionally on `packageKind`, so the wrong key presents as a
    # malformed envelope rather than as "you named the field wrong" — worth knowing if you are
    # ever debugging a rejection that names the whole request instead of one field.
    payload_field = "packageBase64" if kind == "zip" else "skillMdBase64"
    body = {
        "sourceInputMethod": "agent_api",
        "requestId": str(uuid.uuid4()),          # from code: replay identity
        "retrySecret": secrets.token_hex(32),    # from code: a capability token, never sampled
        "packageKind": kind,
        # `sourceFilename` is REQUIRED and was absent. The server's field errors name it, but only
        # once the rest of the envelope parses, so it was invisible behind the payload-field bug.
        "sourceFilename": inventory[0]["path"] if kind != "zip" else os.path.basename(args.package),
        payload_field: base64.b64encode(blob).decode(),     # never passes through a context
        "creator": profile,
        "rightsConfirmed": True,
        "consentVersion": args.consent_version,
        # The server computes the digest and inventory itself, so these are advisory. They are sent
        # anyway, deliberately: if the server's digest ever disagrees with the bytes we read off
        # disk, that is the single most important thing this tool could discover, and it can only
        # discover it by stating its own answer.
        "packageSha256": digest,
        "fileInventory": inventory,
    }
    req = urllib.request.Request(
        args.endpoint, data=json.dumps(body).encode(),
        # A User-Agent IS NOT OPTIONAL, and this is the defect that would have hit every creator.
        # The default `Python-urllib/3.x` is blocked outright by the WAF in front of the submission
        # route — Cloudflare error 1010, a client-fingerprint ban — so a submission failed with a
        # 403 before it was ever read. Measured: default UA 403, any other UA passes to real
        # validation. A named, honest UA is also the cooperative choice: it lets the other side
        # allowlist, rate-limit or debug this client deliberately instead of guessing at traffic.
        headers={"content-type": "application/json", "user-agent": USER_AGENT},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            payload = json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = ""
        try:
            raw = e.read().decode()
            parsed = json.loads(raw or "{}")
            err = parsed.get("error", {}) or {}
            # The route answers rejections at the TOP level (`ok`/`code`/`message`/`issues`), not
            # nested under `error`. Reading only `error` discarded every field error the server
            # sent, so a precise message — which field, what was wrong — was thrown away and
            # replaced with "the server rejected the submission". Read both shapes.
            if not err and parsed.get("code"):
                err = {"code": parsed["code"], "message": parsed.get("message"),
                       "issues": parsed.get("issues"), "remediation": parsed.get("remediation")}
        except Exception:
            err = {}
        # A 403 with no parseable body is almost never a submission verdict. It is the layer in
        # FRONT of the submission route — a WAF or bot filter — refusing the client before anything
        # read the package. Saying "the server rejected the submission" sends the creator to edit a
        # skill that was never looked at, which is the worst possible direction to send them.
        if e.code == 403 and not err.get("code"):
            return _envelope(
                "blocked_before_review",
                "A gateway in front of the submission endpoint refused this client with 403 "
                "before the package was read. Nothing about the skill was evaluated, so do not "
                "change it. This is a transport problem: check that the request carries a "
                "User-Agent, and report the endpoint and time to whoever operates it.",
                EXIT_NETWORK)
        detail = err.get("message") or "The server rejected the submission."
        if err.get("issues"):
            detail += f" Field errors: {json.dumps(err['issues'])}"
        if err.get("remediation"):
            detail += f" {err['remediation']}"
        return _envelope(err.get("code") or f"http_{e.code}", detail, EXIT_REJECTED)
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
    out = {
        "state": payload.get("status") or "submitted_for_review",
        "submitted": True,
        "published": False,
        # The reference the submitter can quote. None of these are secret — the server minted
        # them and shows them on the review side — so withholding them would only mean opening a
        # 0600 file to read your own receipt. The retry secret stays unprinted; that rule holds.
        "submission_id": payload.get("submissionId"),
        "version_id": payload.get("versionId"),
        "skill_slug": payload.get("skillSlug"),
        "creator_slug": payload.get("creatorSlug"),
        # The server computes its own digest. Reporting BOTH sides of the comparison is the point:
        # if they ever differ, the bytes that arrived are not the bytes that were read from disk,
        # and that is worth more than any other line in this output.
        "package_sha256_local": digest,
        "package_sha256_server": payload.get("packageSha256"),
        "digests_agree": payload.get("packageSha256") == digest,
        "idempotent_replay": bool(payload.get("idempotentReplay")),
        "receipt_written_to": path,
        "note": ("Submitted for review — not published. The receipt file holds a private retry "
                 "secret; its value is deliberately not printed here. A person reviews the "
                 "submission and verifies identity before anything is published."),
    }
    print(json.dumps({k: v for k, v in out.items() if v is not None}, indent=1))
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
