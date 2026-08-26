#!/usr/bin/env python3
"""Identity checks over the canonical `skills/` tree — name↔folder, and `name:` uniqueness.

Borrowed in shape from `swan-gtm/gtm-skills`' `tools/validate.mjs`, whose wording names the reason
better than ours did: **`name:` must equal the folder name — one identity, nothing to drift.**
Nothing else about that validator is adopted; it has no credential or content checks at all, which
is where our other suites are strong and it is not.

BOTH CHECKS PASS VACUOUSLY ON TODAY'S CORPUS, and that is the whole reason this file is shaped the
way it is. 30 of 30 names already match their directory and all 30 are distinct, so a green run
here proves nothing about the rules — it proves only that the corpus happens to be clean. A green
field over an untested rule is the `axes_exercised` mistake, so the deliverable is the four
POSITIVE CONTROLS below: three deliberately-broken synthetic trees that must fail, and the real tree
that must pass with an ASSERTED count so a walker that silently stops walking cannot read as a pass.

WHAT COUNTS AS A SKILL, and this is a correction to the brief rather than a detail. The brief said
the tree is flat and every `skills/**/SKILL.md` is a skill. It is not: `skills/` also holds
`canaries/` and `fixtures/`, and `skills/canaries/missing-reference/SKILL.md` carries
`name: weekly-pipeline-account-review` — a DELIBERATE mismatch, since it is a fixture for a
different check. A `skills/**/SKILL.md` glob therefore fails on day one against a file that is
supposed to be broken. So the rule here is the one the projection builder already uses: a skill is
a directory DIRECTLY under `skills/` that contains a `SKILL.md`. Same definition in both places, so
what publishes and what gets identity-checked cannot diverge.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

VERSION = "identity-checks/1.0.0"

_NAME = re.compile(r"^name:\s*(.+?)\s*$", re.M)


# CANONICAL REPO, OR A DISTRIBUTION? The same signal `run_injection_conformance.py` uses, on purpose:
# two suites answering the same question two ways is how they drift apart, and a reader who learns
# the tell once should not have to learn it twice.
#
# WHY THIS EXISTS HERE, AND IT IS NOT THE SAME PROBLEM THE INJECTION SUITE HAS. Case 4 walks the real
# corpus and asserts its size, purely as a tripwire on the WALKER — a silent empty list would
# otherwise read as a pass, which is exactly the bug it caught once (walked 31, expected 30). That
# corpus is canonical `skills/`. In a published copy the walker finds a DIFFERENT `skills/` tree, of a
# different size, so the assertion failed there for a reason that has nothing to do with the walker,
# and the summary then printed "Identity is not enforced" while cases 1-3 had in fact enforced it.
#
# TWO CANDIDATE FIXES WERE MEASURED AND BOTH REJECTED. Re-pointing at `examples/` fails on principle
# rather than on size: it walks to 4 but reports `identity_broken`, because `low-yield-fallback/`
# declares `name: route-inbound-demo-requests`. Those directory names are LESSON LABELS, not
# installable slugs, so an install-identity rule does not apply to them and forcing it would either
# fire falsely or rename a directory whose name is doing the teaching. And shipping a fixture corpus
# purely so the assertion passes is the same move as tuning a threshold until the corpus stops
# complaining — it calibrates the check to what we already have.
#
# So the case is canonical-only and says so. It keeps its value where the corpus lives and where a
# walker regression would actually be introduced, and it stops making a false claim everywhere else.
IS_CANONICAL = os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "contracts"))

CANONICAL_CORPUS_SIZE = 30


def corpus_root() -> str | None:
    """The directory holding `skills/`, found by walking up from this file.

    NOT anchored on the validator directory, which is what the first version did and which made
    this file runnable from one location only: published alongside the other tools there is no
    such directory above it, so the walk reached `/` and exited. A checker a creator cannot run is
    not a checker, and the whole point of publishing this one is that they can check placement.

    `skills/` is the right anchor because it is the thing being checked and it exists under both
    names this file lives at. Returns None rather than exiting when there is no corpus — a
    creator running this inside a single package has no `skills/` tree, and that is a fact to
    report, not a crash.
    """
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(d, "skills")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def _frontmatter_name(path: str) -> str | None:
    """The `name:` value, read only from the frontmatter block.

    Scoped to the block on purpose: `name:` also appears in body prose and in declared-input
    tables, and a whole-file search would pick the wrong one and report a mismatch that is not
    there. Absent frontmatter returns None, which the caller reports as missing rather than
    treating as an empty match.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    m = _NAME.search(text[3:end])
    return m.group(1) if m else None


def discover(skills_root: str) -> list[tuple[str, str]]:
    """Every skill in one tree, as (label, path-to-SKILL.md).

    THE LAYOUT IS DECIDED ONCE FOR THE WHOLE TREE, and the first version of this function got that
    wrong in a way worth keeping written down. It decided per-directory — take a `SKILL.md` if the
    directory has one, otherwise descend a level and take the children's — which reads as
    accommodating and is actually two rules fighting. Over the canonical tree it descended into
    `skills/canaries/`, whose `missing-reference/SKILL.md` is a DELIBERATELY mismatched fixture, and
    reported it as the corpus's only identity defect. 31 skills where 30 were expected.

    The asserted count in control 4 is what caught it. Without that number the run would have been
    a confident FAIL naming a real file, and the obvious next move — "exclude canaries/" — would
    have papered over a walker that was wrong about every nested tree rather than fixing it.

    So: if ANY directory directly under `skills/` holds a `SKILL.md`, the tree is FLAT and only
    those directories are skills — which is exactly the projection builder's own rule, so what
    publishes and what gets identity-checked cannot diverge, and helper directories like
    `canaries/` and `fixtures/` fall out without being named. Otherwise the tree is NESTED
    (`skills/<creator>/<slug>/`, the published layout) and skills live one level down.
    """
    out: list[tuple[str, str]] = []
    if not os.path.isdir(skills_root):
        return out
    tops = sorted(d for d in os.listdir(skills_root)
                  if os.path.isdir(os.path.join(skills_root, d)))
    flat = [d for d in tops if os.path.isfile(os.path.join(skills_root, d, "SKILL.md"))]
    if flat:
        return [(d, os.path.join(skills_root, d, "SKILL.md")) for d in flat]
    for first in tops:
        p1 = os.path.join(skills_root, first)
        for second in sorted(os.listdir(p1)):
            p2 = os.path.join(p1, second)
            if os.path.isdir(p2) and os.path.isfile(os.path.join(p2, "SKILL.md")):
                out.append((f"{first}/{second}", os.path.join(p2, "SKILL.md")))
    return out


def check_tree(skills_root: str) -> dict:
    """Both identity checks over one tree. Messages address the skill's author, not us."""
    findings: list[dict] = []
    skills = discover(skills_root)
    by_name: dict[str, list[str]] = {}

    for label, md in skills:
        folder = os.path.basename(os.path.dirname(md))
        name = _frontmatter_name(md)
        rel = os.path.relpath(md, skills_root).replace(os.sep, "/")
        if name is None:
            findings.append({
                "check": "name_missing", "path": rel,
                "detail": f"no `name:` in the frontmatter of {rel}. An agent installs and triggers "
                          f"this skill by its `name:`, so without one it can never be selected. "
                          f"Add `name: {folder}` to match the folder it lives in.",
            })
            continue
        by_name.setdefault(name, []).append(rel)
        if name != folder:
            findings.append({
                "check": "name_folder_mismatch", "path": rel,
                "detail": f"{rel} declares `name: {name}` but sits in a folder called "
                          f"`{folder}`. These are two identities for one skill and they will "
                          f"drift. Rename the folder to `{name}`, or change `name:` to "
                          f"`{folder}` — whichever is the name you want installers to use.",
            })

    for name, paths in sorted(by_name.items()):
        if len(paths) > 1:
            findings.append({
                "check": "name_collision", "name": name, "paths": paths,
                "detail": f"{len(paths)} skills declare `name: {name}` — {', '.join(paths)}. "
                          f"Skills install into one shared namespace by `name:`, not by folder, so "
                          f"separate directories do not keep them apart: whichever installs second "
                          f"shadows the first. One of them needs a different name.",
            })

    return {"skills": len(skills), "findings": findings,
            "verdict": "ok" if not findings else "identity_broken"}


# ─────────────────────────────────────────────────────────────────────────────────────────
# Positive controls. Synthetic trees, built in a temp dir — the repo is never mutated, and
# nothing here carries a workspace id, a real person or customer data.
# ─────────────────────────────────────────────────────────────────────────────────────────

def _write(root: str, rel: str, name: str | None) -> None:
    path = os.path.join(root, rel, "SKILL.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    head = "---\n" + (f"name: {name}\n" if name else "") + "description: synthetic probe\n---\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(head + "\n# probe\n")


def controls() -> list[dict]:
    out: list[dict] = []

    def case(cid: str, why: str, passed: bool, reasons: list[str], detail: str = "") -> None:
        out.append({"id": cid, "passed": passed, "reasons": reasons, "why": why, "detail": detail,
                    "ran": True})

    def skipped(cid: str, why_not: str) -> None:
        """A THIRD STATE, counted in neither column. A case that could not run must not be reported
        as one that ran and passed — that is the failure this repo has hit most — and it must not be
        reported as a failure either, or a reader concludes the tool is broken when it is being
        honest. So it prints as NOT RUN and says what is unverified."""
        out.append({"id": cid, "passed": True, "ran": False, "reasons": [], "why": "",
                    "detail": why_not})

    # 1 — name disagrees with folder, and the message must name BOTH values or it cannot be acted on
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "resolve-company-domain", "resolve-company-domains")
        res = check_tree(tmp)
        reasons, detail = [], ""
        kinds = [f["check"] for f in res["findings"]]
        if res["verdict"] != "identity_broken":
            reasons.append(f"a name/folder mismatch passed: verdict={res['verdict']}")
        if "name_folder_mismatch" not in kinds:
            reasons.append(f"wrong check fired: {kinds}")
        else:
            detail = next(f["detail"] for f in res["findings"]
                          if f["check"] == "name_folder_mismatch")
            for token in ("resolve-company-domains", "resolve-company-domain"):
                if token not in detail:
                    reasons.append(f"the message does not name {token!r}, so it cannot be acted on")
        case("mismatch-fails-and-names-both-values",
             "One identity, nothing to drift. A message that says 'mismatch' without both values "
             "makes the reader go and look up what they already told us.",
             not reasons, reasons, detail)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 2 — no `name:` at all
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "tam-builder", None)
        res = check_tree(tmp)
        reasons, detail = [], ""
        kinds = [f["check"] for f in res["findings"]]
        if res["verdict"] != "identity_broken":
            reasons.append(f"a skill with no name: passed: verdict={res['verdict']}")
        if "name_missing" not in kinds:
            reasons.append(f"wrong check fired: {kinds}")
        else:
            detail = next(f["detail"] for f in res["findings"] if f["check"] == "name_missing")
        case("absent-name-fails",
             "Absence is the case a regex over present values silently skips, and a skill with no "
             "name: is unreachable by every router rather than merely inconsistent.",
             not reasons, reasons, detail)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 3 — two creators, one slug. THE check the flat canonical tree cannot produce, because the
    # filesystem forbids two identical directory names in one parent. Only the nested published
    # layout can hold it, which is exactly why it has to be synthesised to be tested at all.
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "clay/resolve-company-domain", "resolve-company-domain")
        _write(tmp, "acme-gtm/resolve-company-domain", "resolve-company-domain")
        res = check_tree(tmp)
        reasons, detail = [], ""
        kinds = [f["check"] for f in res["findings"]]
        if res["verdict"] != "identity_broken":
            reasons.append(f"two skills sharing a name: passed: verdict={res['verdict']}")
        if "name_collision" not in kinds:
            reasons.append(f"wrong check fired: {kinds}")
        else:
            f = next(x for x in res["findings"] if x["check"] == "name_collision")
            detail = f["detail"]
            for token in ("clay/resolve-company-domain", "acme-gtm/resolve-company-domain"):
                if token not in detail:
                    reasons.append(f"the message does not name the path {token!r}")
        if res["skills"] != 2:
            reasons.append(f"expected to walk 2 skills, walked {res['skills']}")
        case("cross-creator-name-collision-fails-and-names-both-paths",
             "Skills install by `name:` into one namespace, so two creators' identically-named "
             "skills collide in an installed agent however separate their directories are. This "
             "is the failure that can reach a user, and it is unreachable in today's flat tree.",
             not reasons, reasons, detail)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 4 — the RULE, on whatever corpus is actually here. Unconditional.
    #
    # THIS WAS THE ONE CASE THAT MATTERED AND IT WAS SWITCHED OFF WHERE IT MATTERED. Case 4 used to
    # be one case asserting two different things — that the corpus is clean, and that the walker
    # walked the expected NUMBER of skills — and it was gated whole on `IS_CANONICAL` because only
    # the canonical tree has an asserted size. So on the published tree, the only tree with a nested
    # layout and therefore the only tree that can hold a cross-creator collision, the rule did not
    # run at all. It reported NOT RUN, honestly, and everyone read past it.
    #
    # It cost a real defect: two skills published under two author directories with the same
    # `name:`, sitting in the tree while case 3 proved on synthetic fixtures that exactly that
    # shape is caught. A guard that fires on a fixture and is disabled on the corpus is a guard
    # that documents a rule instead of enforcing it.
    #
    # So the two assertions are now two cases. The rule runs wherever there is a corpus; only the
    # count tripwire is canonical-only, because only the count is canonical-specific.
    root = corpus_root()
    if root is None:
        skipped("real-corpus-has-no-identity-defects",
                "no `skills/` tree above this file, so there is no corpus to check. Running inside "
                "a single package is the normal way to see this; cases 1-3 still enforced the rule")
    else:
        res = check_tree(os.path.join(root, "skills"))
        reasons = []
        if res["verdict"] != "ok":
            reasons = [f"{f['check']}: {f.get('name') or f.get('path')} — "
                       f"{', '.join(f.get('paths', []))or f.get('path')}" for f in res["findings"]]
        case("real-corpus-has-no-identity-defects",
             "The published layout is the only one that can hold a cross-creator collision — a flat "
             "tree cannot, because a filesystem forbids two identical directory names in one "
             "parent. Checking fixtures and skipping the corpus tests the regex and ships the bug.",
             not reasons, reasons, f"{res['skills']} skills, {len(res['findings'])} findings")

    # 5 — the WALKER, guarded by an asserted count. Canonical-only, because the number is.
    if not IS_CANONICAL:
        skipped("walker-reads-the-whole-asserted-corpus",
                f"the asserted size ({CANONICAL_CORPUS_SIZE}) belongs to the canonical seed tree "
                f"and is not distributed, so the walker tripwire is UNMEASURED here. The rule "
                f"itself ran in case 4 above, on this tree")
    elif root is None:
        case("walker-reads-the-whole-asserted-corpus",
             "A silent empty list would otherwise read as a pass.",
             False, ["no `skills/` tree found above this file in the canonical repo"], "0 skills")
    else:
        n = check_tree(os.path.join(root, "skills"))["skills"]
        reasons = [] if n == CANONICAL_CORPUS_SIZE else [
            f"walked {n} skills, expected {CANONICAL_CORPUS_SIZE} — either the corpus changed "
            f"(update CANONICAL_CORPUS_SIZE deliberately) or the walker stopped reading the tree"]
        case("walker-reads-the-whole-asserted-corpus",
             "Guards the WALKER, not the rule. Every canonical name matches its folder and all are "
             "distinct, so without the count this would still read PASS on an empty list — which is "
             "the failure where a check stops reading the tree and reports success for it.",
             not reasons, reasons, f"{n} skills")

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--tree", help="check one tree and report, instead of running the controls")
    args = ap.parse_args()

    if args.tree:
        res = check_tree(args.tree)
        print(json.dumps(res, indent=2))
        return 1 if res["verdict"] != "ok" else 0

    results = controls()
    failed = [r for r in results if not r["passed"]]
    not_run = [r for r in results if not r.get("ran", True)]
    ran = [r for r in results if r.get("ran", True)]

    if args.json:
        print(json.dumps({"version": VERSION, "results": results,
                          "enforced": len(ran) - len(failed), "not_run": len(not_run)}, indent=2))
    else:
        print(f"identity checks — {VERSION}\n")
        for r in results:
            state = "PASS" if r.get("ran", True) else "NOT RUN"
            if not r["passed"]:
                state = "FAIL"
            print(f"  [{state}] {r['id']}")
            if r["detail"]:
                print(f"         {'message' if r.get('ran', True) else 'why not'}: "
                      f"{r['detail'][:170]}")
            if not r["passed"]:
                print(f"         why it exists: {r['why']}")
                for reason in r["reasons"]:
                    print(f"         → {reason}")
        tail = f", {len(not_run)} NOT RUN" if not_run else ""
        print(f"\n{len(ran) - len(failed)}/{len(ran)} enforced{tail}")
        if failed:
            print("\nIdentity is not enforced. A published corpus can carry two skills that "
                  "collide on install.")
        elif not_run:
            print("\nIdentity IS enforced on the cases that ran. What did not run is named above, "
                  "and is unverified rather than passing.")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
