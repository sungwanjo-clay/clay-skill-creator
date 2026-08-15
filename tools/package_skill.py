#!/usr/bin/env python3
"""Package contract + deterministic manifest/ZIP export for a generated skill.

Scope discipline: this module implements the PACKAGE SHAPE only. Every content check —
workspace handles, dangling relative references, bare credentials, endpoints, stale action keys —
is delegated to `eval/validators/portability.py`, which already carries four things this would
otherwise reimplement and get wrong at least once:

  * fence masking, so a handle quoted inside a fenced example does not fire
  * URL span masking (1.4.0, a recorded finding), so a URL containing digits is not read as a workspace id
  * severity classes, so heuristic evidence reports instead of blocking
  * system-failure separation with the attribution triple

A standalone re-implementation would reproduce at least one of those bugs. It already cost six
`built` skills a false BLOCK once.

DETERMINISM means **content-manifest equality**, not archive-byte equality:
same relative paths, same per-file SHA-256, manifest verification succeeds. Archive bytes are
*additionally* stable here because entry order and timestamps are deliberately normalized — but
the contract a caller may rely on is the manifest, because a ZIP's bytes depend on the writer's
compression library version and that is not something a creator's machine can be held to.

Ploy owns ZIP intake. This writes files and reads them back; it touches no service.

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

def _validators_dir() -> str:
    """Locate `portability.py`, in either layout this file legitimately lives in.

    SIBLING FIRST, canonical second — and the order is the fix, not a nicety. An earlier version
    only walked up looking for `eval/validators/`, which exists in the source repo and nowhere
    else. That made the tool robust inside our tree and *unusable* in the projection, where it
    ships as `tools/package_skill.py` beside `tools/portability.py` — so the very first command a
    creator runs died on import. Replacing a hard-coded level count with a hard-coded directory
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
            raise ModuleNotFoundError(
                f"cannot locate portability.py: not beside {os.path.abspath(__file__)}, and no "
                "eval/validators/portability.py in any parent directory")
        d = parent


sys.path.insert(0, _validators_dir())

import portability as P  # noqa: E402

PACKAGE_VERSION = "skill-package/1.0.0"
MANIFEST_VERSION = "package-manifest/1.0.0"

ROOT_FILE = "SKILL.md"

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
# byte-for-byte, at submission. Above it we have no evidence either way — Ploy removed a client
# check, and whether a higher server limit exists is unverified. Reporting past the edge of the
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
            add("portable_path", "block",
                f"{top}/ is not an allowlisted supporting directory "
                f"({', '.join(PORTABLE_DIRS)})", f)
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

        # 3 — every supporting file must be REFERENCED from the body. This is the mechanical form
        # of "never add supporting files merely to make a package look complete": an unreferenced
        # file is either decoration or dead weight, and both mislead a reader about the package's
        # real surface. The inverse (a reference with no file) is portability's `missing_file`.
        for f in files:
            if f == ROOT_FILE:
                continue
            if f.replace(os.sep, "/") not in body:
                add("unreferenced_file", "block",
                    f"{f} is never referenced from {ROOT_FILE}; remove it or reference it", f)

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

    if a.mode == "validate":
        cat = json.load(open(a.action_catalog)) if a.action_catalog else None
        res = validate(a.dir, cat)
        print(json.dumps(res, indent=1))
        # 1 = the package must not ship. A system failure is also non-zero: a check that did not
        # run is not a check that passed.
        return 0 if res["verdict"] == "ok" else 1
    if a.mode == "scan":
        res = scan_content(a.dir)
        print(json.dumps(res, indent=1))
        return 0 if res["verdict"] == "ok" else 1
    if a.mode == "manifest":
        print(json.dumps(manifest(a.dir), indent=1))
        return 0
    if a.mode == "zip":
        print(json.dumps(write_zip(a.dir, a.out), indent=1))
        return 0
    exp = json.load(open(a.manifest)) if a.manifest else None
    res = verify_zip(a.zip, exp)
    print(json.dumps(res, indent=1))
    return 0 if res["verified"] in (True, None) else 1


if __name__ == "__main__":
    sys.exit(main())
