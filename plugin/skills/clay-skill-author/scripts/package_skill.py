#!/usr/bin/env python3
"""Package contract + deterministic manifest/ZIP export for a generated skill.

Scope discipline: this module implements the PACKAGE SHAPE only. Every content check —
workspace handles, dangling relative references, bare credentials, endpoints, stale action keys —
is delegated to `eval/validators/portability.py`, which already carries four things this would
otherwise reimplement and get wrong at least once:

  * fence masking, so a handle quoted inside a fenced example does not fire
  * URL span masking (1.4.0), so a URL containing digits is not read as a workspace id
  * severity classes, so heuristic evidence reports instead of blocking
  * system-failure separation with the attribution triple

A standalone re-implementation would reproduce at least one of those bugs. It already cost six
`built` skills a false BLOCK once.

DETERMINISM means **content-manifest equality**, not archive-byte equality:
same relative paths, same per-file SHA-256, manifest verification succeeds. Archive bytes are
*additionally* stable here because entry order and timestamps are deliberately normalized — but
the contract a caller may rely on is the manifest, because a ZIP's bytes depend on the writer's
compression library version and that is not something a creator's machine can be held to.

ZIP intake is server-side. This writes files and reads them back; it touches no service.

Usage:
  package_skill.py validate <dir> [--action-catalog <actions.json>]
  package_skill.py manifest <dir>
  package_skill.py zip      <dir> <out.zip>
  package_skill.py verify   <out.zip> [--manifest <manifest.json>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile

class _MissingDependency(Exception):
    """A hard dependency is absent. Raised at import time, which is BEFORE any handler in
    `__main__` exists — so the import-time call site catches it inline. See below."""


def _validators_dir() -> str:
    """Locate `portability.py`, in either layout this file legitimately lives in.

    SIBLING FIRST, canonical second — and the order is the fix, not a nicety. An earlier version
    only walked up looking for an `eval/validators/` directory, a layout this file does not ship
    in. That made the tool robust in one place and *unusable* where it actually runs, beside
    `portability.py` in the same directory — so the very first command a creator runs died on
    import. Replacing a hard-coded level count with a hard-coded directory
    name is not a fix; both bind to a layout, and the second bound to the one layout the recipient
    does not have.

    Checking the sibling first also means one file serves both trees, so there is no second copy
    to drift.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile(os.path.join(here, "portability.py")):
        return here
    d = here
    while True:
        cand = os.path.join(d, "eval", "validators")
        if os.path.isfile(os.path.join(cand, "portability.py")):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            # Mirrors the shim's glibc-loader check: a missing hard dependency fails with a
            # categorical error naming what is absent, not a crash the caller has to parse.
            raise _MissingDependency(
                f"cannot locate portability.py: not beside {os.path.abspath(__file__)}, and no "
                "eval/validators/portability.py in any parent directory. It ships beside this file "
                "— re-download the skill or fetch tools/portability.py from the "
                "clay-skill-creator repository")
        d = parent


# Resolved AT IMPORT TIME, so the `__main__` handler below does not exist yet and cannot catch a
# failure here. An earlier version of this file carried a comment claiming it would — the test
# disproved the comment, not the code. So the envelope is emitted inline, which is what the shim
# does too: it validates its preconditions and dies with the contract BEFORE exec'ing anything.
try:
    _VALIDATORS_DIR = _validators_dir()
except _MissingDependency as _exc:
    print(json.dumps({"error": {"code": "internal_error", "message": str(_exc)}}), file=sys.stderr)
    raise SystemExit(1)

sys.path.insert(0, _VALIDATORS_DIR)

try:
    import portability as P  # noqa: E402
except Exception as _exc:  # a broken dependency is still ours, not the caller's
    print(json.dumps({"error": {"code": "internal_error", "message":
                                f"portability.py found at {_VALIDATORS_DIR} but failed to import: "
                                f"{type(_exc).__name__}: {_exc}"}}), file=sys.stderr)
    raise SystemExit(1)

PACKAGE_VERSION = "skill-package/1.0.0"
MANIFEST_VERSION = "package-manifest/1.0.0"

ROOT_FILE = "SKILL.md"

# An answer sheet, by name or by shape. Deliberately narrow in both directions: the name pattern only
# matches a file that announces itself, and the body pattern requires a top-level `answers:` mapping
# with at least one child — so a reference file that merely discusses answers is untouched, while a
# sheet somebody renamed to `config.yml` is not.
_ANSWER_SHEET_NAME = re.compile(r"(?i)^(?:answers?|answer[-_]sheet|my[-_]answers)\.(?:ya?ml|json|txt)$")
_ANSWER_SHEET_BODY = re.compile(r"(?m)^answers:\s*$\s*^\s+\S+\s*:")

# An ALLOWLIST of supporting directories, per RULE 0b's own lesson applied to paths: a denylist of
# "bad" locations fails the moment someone invents a new one. Widening this is a deliberate edit.
PORTABLE_DIRS = ("references", "scripts")

# The ZIP epoch. Fixed so entry metadata carries no build clock — a timestamp is the usual reason
# two byte-identical trees produce different archives.
FIXED_DATE = (1980, 1, 1, 0, 0, 0)

# Description length. There is NO KNOWN CAP, and the history here is the reason this constant is
# named after evidence rather than after a limit.
#
# A 1024 cap was real at both submission doors and was removed ~45 minutes before this check
# shipped. The check went out asserting "submission is rejected at this cap" — false when written,
# and it hard-BLOCKED descriptions the platform accepts. Two of the three skills trimmed to satisfy
# it are the two that had already been submitted successfully at 1,187 and 1,182 characters and
# proved the cap was gone.
#
# So: 1,187 is not a limit. It is the longest description DEMONSTRATED to be stored intact,
# byte-for-byte, at submission. Above it we have no evidence either way — a client-side
# check was removed, and whether a higher server limit exists is unverified. Reporting past the edge of the
# evidence is honest; naming a ceiling we have not seen would repeat the defect with a bigger number.
DESCRIPTION_LONGEST_DEMONSTRATED = 1187


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def walk_package(root: str) -> list[str]:
    """Relative paths of every regular file, sorted. Excludes nothing — an unexpected file must
    surface as a finding, not be silently skipped, or the manifest and the package disagree."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            out.append(os.path.relpath(os.path.join(dirpath, fn), root))
    return sorted(out)


def _description_chars(skill_md: str) -> int | None:
    """Length of the frontmatter description as the form will see it, or None if absent.

    A block scalar (`description: |`) is measured with its lines joined by single spaces, because
    that is what the value becomes once parsed — counting the raw bytes would include the indentation
    and over-report by roughly the line count.
    """
    m = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
    if not m:
        return None
    fm = m.group(1)
    block = re.search(r"^description:\s*[|>][-+]?\s*\n((?:[ \t]+.*\n?)+)", fm, re.M)
    if block:
        return len(" ".join(l.strip() for l in block.group(1).rstrip().split("\n")))
    one = re.search(r"^description:[ \t]*(.+)$", fm, re.M)
    return len(one.group(1).strip().strip("\"'")) if one else None


def validate(root: str, action_catalog: dict | None = None) -> dict:
    """Package-shape findings plus delegated content findings. `blocking` decides generation."""
    findings: list[dict] = []
    files = walk_package(root)

    def add(kind: str, severity: str, detail: str, path: str | None = None) -> None:
        findings.append({"check": kind, "severity": severity, "detail": detail, "path": path})

    # 1 — exactly one root SKILL.md.
    roots = [f for f in files if f == ROOT_FILE]
    if not roots:
        add("root_skill_md", "block", f"no {ROOT_FILE} at the package root")
    stray = [f for f in files if os.path.basename(f) == ROOT_FILE and f != ROOT_FILE]
    for f in stray:
        add("root_skill_md", "block",
            f"a second {ROOT_FILE} exists at {f}; a package has exactly one, at the root", f)

    # 2 — supporting files live under an allowlisted portable directory, and nowhere escapes.
    for f in files:
        if f == ROOT_FILE:
            continue
        norm = f.replace(os.sep, "/")
        top = norm.split("/", 1)[0]
        if norm.startswith("/") or ".." in norm.split("/"):
            add("portable_path", "block", f"path escapes the package: {f}", f)
        elif "/" not in norm:
            add("portable_path", "block",
                f"{f} sits at the package root; supporting files belong under "
                f"{'/, '.join(PORTABLE_DIRS)}/", f)
        elif top not in PORTABLE_DIRS:
            # "is not an allowlisted supporting directory" described OUR config, not their package;
            # a creator has never seen the allowlist and cannot act on the word. Phrased to match
            # the sits-at-the-root sibling above, so the two read as one rule rather than two.
            add("portable_path", "block",
                f"{f} sits under {top}/; supporting files belong under "
                f"{'/, '.join(PORTABLE_DIRS)}/", f)
        if os.path.islink(os.path.join(root, f)):
            add("portable_path", "block", f"{f} is a symlink; a package carries real files", f)

    body = ""
    if roots:
        with open(os.path.join(root, ROOT_FILE), encoding="utf-8") as fh:
            body = fh.read()

        # 2b — description length. REPORT, never block: the kit must not reject what the
        # marketplace accepts, and a local checker that overrules the platform has authority it does
        # not have. The mirror of an under-recognizing extractor certifying rather than missing — a
        # check stricter than its contract rejects rather than passes, and either way the check wins
        # an argument it should lose.
        n = _description_chars(body)
        if n is None:
            add("description_missing", "block",
                f"no `description` in the frontmatter of {ROOT_FILE}; it is what decides when the "
                "skill is chosen, so a skill without one is unreachable", ROOT_FILE)
        elif n > DESCRIPTION_LONGEST_DEMONSTRATED:
            add("description_unusually_long", "report",
                f"description is {n} characters. The longest we have verified stored intact through "
                f"submission is {DESCRIPTION_LONGEST_DEMONSTRATED}; beyond that we have no evidence "
                "either way, so this is a heads-up rather than a limit. If you want to trim anyway, "
                "cut restatements and mechanism detail — the trigger phrases and the "
                "\"do NOT use it for\" list are what earn their length, because they decide whether "
                "your skill gets chosen at all", ROOT_FILE)

        # 2b — a declared-inputs section. REPORT, never block, and the severity is the whole point.
        #
        # This exists here rather than only server-side because of WHEN each runs. The server
        # validator runs after submission, so it can tell a REVIEWER that a section is missing; it
        # structurally cannot tell the CREATOR before they send. This one can, which is the only
        # reason a local check earns its place now that the server owns authoritative validation.
        #
        # Never blocking, for a reason that generalises: no check can tell a considered threshold
        # from a hardcoded one, so the section's PRESENCE is mechanical while its QUALITY is not. A
        # blocking check on presence would buy an empty heading, and an empty heading is worse than
        # an absent one because it looks answered. Presence is a nudge; a person reads the content.
        if not re.search(r"(?im)^#{2,3}\s+declared inputs\b", body):
            add("missing_declared_inputs", "report",
                "no `## Declared inputs` section. This is the section that decides whether anyone "
                "else can run this: every value that is yours rather than theirs — table and column "
                "ids, auth accounts, and equally the CRM, the ICP, the weights, the thresholds, what "
                "counts as senior — needs a row saying what they supply and what happens without it. "
                "A hardcoded threshold is indistinguishable from a considered one to every check "
                "downstream, so this is the part only you can get right. All four worked examples "
                "model it", ROOT_FILE)

        # 3 — every supporting file must be REFERENCED from the body. This is the mechanical form
        # of "never add supporting files merely to make a package look complete": an unreferenced
        # file is either decoration or dead weight, and both mislead a reader about the package's
        # real surface. The inverse (a reference with no file) is portability's `missing_file`.
        #
        # THE MESSAGE NAMES NO FILE TYPE, DELIBERATELY. The case that prompted this rewrite was a
        # creator packaging an internal notes file, and the temptation was to special-case it and
        # say so. Two reasons not to. The check cannot know what the file IS — only that nothing
        # points at it — so any name it guessed would sometimes be wrong. And "internal record" is
        # OUR word for OUR eval notes: it means nothing to someone who has never seen one, and a
        # finding written in the vocabulary of the tool rather than the reader is a finding they
        # cannot act on. State the fact that is actually known, from their side: they shipped a
        # file their skill never mentions.
        for f in files:
            if f == ROOT_FILE:
                continue
            if f.replace(os.sep, "/") not in body:
                add("unreferenced_file", "block",
                    f"nothing in {ROOT_FILE} points at {f}, so whoever installs this skill gets "
                    f"the file and never opens it. Link to it from the body if it earns its "
                    f"place, or leave it out of the package — a file that ships unread "
                    f"misrepresents what the skill actually is", f)

        # 3a — AN ANSWER SHEET MUST NEVER BE IN THE PACKAGE, and until now nothing checked.
        #
        # THE PROMISE EXISTED WITHOUT THE MECHANISM, which is the exact distinction the promise makes
        # about itself. `SUBMITTING.md` says the sheet is "structurally excluded rather than promised
        # out: a sheet inside a package fails validation before anything can be sent", and the flow
        # repeats it. Measured: a filled sheet at `references/answers.yml`, referenced from the body
        # like any supporting file, validated `ok` with zero findings.
        #
        # The exposure is NEW and the kit created it. Before answer sheets there was no reason for a
        # creator to have a YAML of live CRM field names, table ids and thresholds sitting beside a
        # package. Now the kit tells them to make one, and the only thing standing between that file
        # and a public repository was putting it in the wrong folder — `answers.yml` at the root
        # happens to trip the path contract, `references/answers.yml` does not.
        #
        # SHAPE, NOT JUST NAME. A renamed sheet is still a sheet, so the content test carries the
        # check and the filename is a second way in rather than the only one. Both are narrow: a
        # top-level `answers:` key with at least one child, or a filename that says what it is.
        for f in files:
            if f == ROOT_FILE:
                continue
            looks_named = _ANSWER_SHEET_NAME.search(os.path.basename(f)) is not None
            looks_shaped = False
            if f.lower().endswith((".yml", ".yaml", ".json", ".txt", ".md")):
                try:
                    with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                        looks_shaped = _ANSWER_SHEET_BODY.search(fh.read(8192)) is not None
                except OSError:
                    looks_shaped = False          # cannot read it, so cannot claim it is one
            if not (looks_named or looks_shaped):
                continue
            add("answer_sheet_in_package", "block",
                f"{f} looks like a filled answer sheet. Those hold real values — field names, table "
                f"ids, thresholds — and a package is published, so shipping one publishes your "
                f"workspace's shape to anyone who installs the skill. It belongs BESIDE the package, "
                f"not inside it: move it one directory up, out of the skill folder, and send it to a "
                f"teammate the way you send any other file. Nothing about it is submitted, and the "
                f"skill still finds it there", f)

    # 3b — PAGE COPY IS NO LONGER THIS FILE'S CONCERN, and the deletion is recorded because an
    # absent check reads as an oversight otherwise.
    #
    # There was a `## Listing` block here: five declared page fields, checked at `report` severity.
    # It existed because page copy used to be mined out of agent-facing prose, and every extraction
    # round found the same defect one layer down. Declaring it fixed that.
    #
    # It is gone because the ownership moved rather than because the problem went away. The
    # marketplace writes the page now, from the skill, for a person; `SKILL.md` is written for an
    # agent end to end. A validator here would be enforcing a contract this repo no longer owns, and
    # the five-field shape was the last thing making one section of an agent-facing file secretly
    # human-facing.
    #
    # DO NOT REINSTATE A PAGE-COPY CHECK HERE. A page that reads badly is a defect for whoever owns
    # the page. If the marketplace ever hands page authorship back, that is a contract change and it
    # arrives with its own checker.

    # 4a — the one PACKAGE-scoped content check, run here because only here are the files on disk.
    #
    # Whether a skill names the Clay command it spends money on is a question about the package, not
    # about `SKILL.md`: a command named in `references/sourcing-arms.md` is named, and two of the five
    # skills this first fired on did exactly that. `check_portability` receives the body alone, so it
    # goes deliberately quiet when the body points at files it cannot see. This is the caller that
    # supplies the rest. A reference we cannot open degrades to the same silence — a check run on text
    # that failed to read is not a check.
    ref_text: str | None = ""
    for rel in files:
        if rel == ROOT_FILE or not rel.lower().endswith((".md", ".txt", ".py")):
            continue
        try:
            with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
                ref_text += "\n" + fh.read()
        except OSError:
            ref_text = None
            break
    if body and ref_text is not None:
        for fnd in P._resolve_mechanism(body, ref_text):
            findings.append({
                "check": "portability/mechanism", "severity": fnd.severity,
                "detail": fnd.detail[:300], "evidence": fnd.evidence[:120], "line": fnd.line,
            })

    # 4 — delegated content checks. Not reimplemented; see the module docstring.
    port = P.check_portability(body, files, action_catalog)
    for fnd in port.findings:
        d = fnd if isinstance(fnd, dict) else getattr(fnd, "__dict__", {})
        findings.append({
            "check": "portability/" + str(d.get("resolver", "?")),
            "severity": str(d.get("severity", "report")),
            "detail": str(d.get("detail", ""))[:300],
            "evidence": str(d.get("evidence", ""))[:120],
            "line": d.get("line"),
        })
    sysfail = [str(s) for s in (getattr(port, "system_failures", None) or [])]

    blocking = [f for f in findings if f["severity"] == "block"]
    return {
        "schema": PACKAGE_VERSION,
        "portability": P.attribution() if hasattr(P, "attribution") else {"version": P.VERSION},
        "files": files,
        "findings": findings,
        "blocking": blocking,
        "system_failures": sysfail,
        # A system failure is not a pass and not a content defect: it means a check did not run.
        "verdict": ("blocked" if blocking else "system_failure" if sysfail else "ok"),
    }


def scan_content(root: str, exts: tuple[str, ...] = (".md", ".txt", ".yml", ".yaml")) -> dict:
    """Content checks over a TREE that is not a skill package — e.g. the public projection.

    `validate()` asserts package shape (one root SKILL.md, allowlisted dirs), which a repo does not
    have and should not be forced into. But the content half applies to anything we publish: no
    workspace identifiers, no credentials, no private endpoints. So this runs the delegated
    resolvers over each file and skips the shape rules.

    `missing_file` is dropped here deliberately. It resolves relative references against a package
    manifest, and in a repo a link to a sibling document is correct rather than dangling — keeping
    it would flag every internal cross-link as a defect. Shape and content are different questions;
    this answers only the second.
    """
    findings = []
    scanned = []
    for rel in walk_package(root):
        if not rel.lower().endswith(exts):
            continue
        scanned.append(rel)
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
            body = fh.read()
        res = P.check_portability(body, [rel], None)
        for fnd in res.findings:
            d = fnd if isinstance(fnd, dict) else getattr(fnd, "__dict__", {})
            if str(d.get("resolver")) == "missing_file":
                continue
            findings.append({
                "file": rel,
                "check": "portability/" + str(d.get("resolver", "?")),
                "severity": str(d.get("severity", "report")),
                "evidence": str(d.get("evidence", ""))[:120],
                "detail": str(d.get("detail", ""))[:200],
                "line": d.get("line"),
            })
    blocking = [f for f in findings if f["severity"] == "block"]
    return {
        "schema": PACKAGE_VERSION,
        "portability": P.attribution() if hasattr(P, "attribution") else {"version": P.VERSION},
        "scanned": scanned,
        "findings": findings,
        "blocking": blocking,
        "verdict": "blocked" if blocking else "ok",
    }


def manifest(root: str) -> dict:
    """Content manifest — the determinism contract.

    `manifest_sha256` digests the canonical (path, sha256) pairs only: not file order as walked,
    not mtimes, not sizes. Two builds of identical content therefore agree even if produced on
    different machines by different ZIP writers.
    """
    entries = []
    for rel in walk_package(root):
        with open(os.path.join(root, rel), "rb") as fh:
            data = fh.read()
        entries.append({"path": rel.replace(os.sep, "/"),
                        "sha256": _sha256(data), "bytes": len(data)})
    canonical = "\n".join(f"{e['path']}\t{e['sha256']}" for e in entries)
    return {
        "schema": MANIFEST_VERSION,
        "files": entries,
        "file_count": len(entries),
        "manifest_sha256": _sha256(canonical.encode()),
    }


def write_zip(root: str, out_path: str) -> dict:
    """Deterministic archive. Entry order sorted, timestamps fixed, compression pinned.

    Byte-stability is a bonus, not the contract — see the module docstring. It is still worth
    having, because a caller diffing two archives should see nothing rather than see noise.
    """
    m = manifest(root)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for e in m["files"]:
            zi = zipfile.ZipInfo(filename=e["path"], date_time=FIXED_DATE)
            zi.external_attr = 0o644 << 16
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3  # fixed, so the writer's OS does not leak into the bytes
            with open(os.path.join(root, e["path"].replace("/", os.sep)), "rb") as fh:
                z.writestr(zi, fh.read())
    with open(out_path, "rb") as fh:
        m["archive_sha256"] = _sha256(fh.read())
    m["archive_path"] = out_path
    return m


def verify_zip(zip_path: str, expected: dict | None = None) -> dict:
    """Recompute the manifest FROM the archive and compare. Reports per-path divergence."""
    entries = []
    with zipfile.ZipFile(zip_path) as z:
        for name in sorted(z.namelist()):
            data = z.read(name)
            entries.append({"path": name, "sha256": _sha256(data), "bytes": len(data)})
    canonical = "\n".join(f"{e['path']}\t{e['sha256']}" for e in entries)
    got = {"schema": MANIFEST_VERSION, "files": entries, "file_count": len(entries),
           "manifest_sha256": _sha256(canonical.encode())}
    if expected is None:
        return {"manifest": got, "verified": None}

    exp_map = {e["path"]: e["sha256"] for e in expected.get("files", [])}
    got_map = {e["path"]: e["sha256"] for e in entries}
    return {
        "manifest": got,
        "verified": got["manifest_sha256"] == expected.get("manifest_sha256"),
        "missing_paths": sorted(set(exp_map) - set(got_map)),
        "extra_paths": sorted(set(got_map) - set(exp_map)),
        "changed_paths": sorted(p for p in set(exp_map) & set(got_map)
                                if exp_map[p] != got_map[p]),
    }


# ── Failure contract, mirrored from the Clay plugin's `bin/clay` bootstrapper ─────────────
#
# That shim emits a JSON error envelope on stderr with a CATEGORICAL exit code on every failure
# path, explicitly so "an agent that branches on the first `clay` invocation sees the same shape
# the binary emits". Ours did the opposite: measured across four failure modes, every one exited
# 1, and three dumped a raw Python traceback. So "your package has a blocking defect", "this tool
# is broken", "you gave me a path that does not exist" and "that file is not a zip" were
# indistinguishable to the caller — and an agent cannot decide whether to fix the skill, fix the
# invocation, or stop.
#
# Codes follow the Clay CLI's own space where the meanings line up, so an agent already branching
# on Clay exit codes needs no new vocabulary:
#
#   0  ok                 clean
#   1  internal_error     THIS TOOL is broken or a dependency is missing. Not the creator's fault.
#   2  validation_error   the INVOCATION is wrong: no such directory, unreadable manifest, not a zip
#   4  blocked            the PACKAGE has blocking findings. Not an error — a verdict, and the one
#                         outcome a creator is expected to act on.
#
# BACKWARDS COMPATIBLE on purpose: 0 still means clean and every failure is still non-zero, so
# `if exit != 0` logic already published in VALIDATION.md keeps working. The codes only ADD the
# ability to tell the cases apart.
EXIT_OK = 0
EXIT_INTERNAL = 1
EXIT_VALIDATION = 2
EXIT_BLOCKED = 4


def _envelope(code: str, message: str, exit_code: int) -> int:
    """Emit the plugin's envelope shape on stderr and return the categorical code.

    Escaping matters for the same reason it does in the shim: messages interpolate paths, and a
    stray quote or backslash would hand the caller invalid JSON at exactly the moment it is trying
    to find out what went wrong.
    """
    print(json.dumps({"error": {"code": code, "message": message}}), file=sys.stderr)
    return exit_code


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="mode", required=True)
    v = sub.add_parser("validate"); v.add_argument("dir"); v.add_argument("--action-catalog")
    sc = sub.add_parser("scan", help="content-only checks over a tree that is not a package")
    sc.add_argument("dir")
    mf = sub.add_parser("manifest"); mf.add_argument("dir")
    z = sub.add_parser("zip"); z.add_argument("dir"); z.add_argument("out")
    vz = sub.add_parser("verify"); vz.add_argument("zip"); vz.add_argument("--manifest")
    a = ap.parse_args()

    def need_dir(d: str) -> int | None:
        if os.path.isdir(d):
            return None
        return _envelope("validation_error", f"no such directory: {d}", EXIT_VALIDATION)

    def load_json(path: str, what: str):
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            raise _BadInvocation(f"{what} not found: {path}")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise _BadInvocation(f"{what} is not readable JSON ({path}): {exc}")

    if a.mode in ("validate", "scan", "manifest", "zip"):
        bad = need_dir(a.dir)
        if bad is not None:
            return bad

    if a.mode == "validate":
        cat = load_json(a.action_catalog, "action catalog") if a.action_catalog else None
        res = validate(a.dir, cat)
        print(json.dumps(res, indent=1))
        # `blocked` and `system_failure` are DIFFERENT dispositions and now say so. A blocking
        # finding is the creator's to fix; a system failure means a check did not run, which is
        # ours, and neither is "this tool crashed".
        if res["verdict"] == "ok":
            return EXIT_OK
        if res["verdict"] == "system_failure":
            return _envelope("internal_error",
                             "a required check did not run, so this package is unverified rather "
                             "than clean: " + "; ".join(res.get("system_failures") or ["unknown"]),
                             EXIT_INTERNAL)
        return EXIT_BLOCKED
    if a.mode == "scan":
        res = scan_content(a.dir)
        print(json.dumps(res, indent=1))
        return EXIT_OK if res["verdict"] == "ok" else EXIT_BLOCKED
    if a.mode == "manifest":
        print(json.dumps(manifest(a.dir), indent=1))
        return EXIT_OK
    if a.mode == "zip":
        print(json.dumps(write_zip(a.dir, a.out), indent=1))
        return EXIT_OK
    if not os.path.isfile(a.zip):
        return _envelope("validation_error", f"no such file: {a.zip}", EXIT_VALIDATION)
    try:
        exp = load_json(a.manifest, "manifest") if a.manifest else None
        res = verify_zip(a.zip, exp)
    except zipfile.BadZipFile as exc:
        return _envelope("validation_error", f"{a.zip} is not a zip archive: {exc}",
                         EXIT_VALIDATION)
    print(json.dumps(res, indent=1))
    return EXIT_OK if res["verified"] in (True, None) else EXIT_BLOCKED


class _BadInvocation(Exception):
    """The caller gave us something unusable. Distinct from a package defect."""


if __name__ == "__main__":
    try:
        sys.exit(main())
    except _BadInvocation as exc:
        sys.exit(_envelope("validation_error", str(exc), EXIT_VALIDATION))
    except _MissingDependency as exc:
        sys.exit(_envelope("internal_error", str(exc), EXIT_INTERNAL))
    except KeyboardInterrupt:
        sys.exit(EXIT_INTERNAL)
    except Exception as exc:  # noqa: BLE001 — a traceback is not a contract
        sys.exit(_envelope("internal_error", f"{type(exc).__name__}: {exc}", EXIT_INTERNAL))
