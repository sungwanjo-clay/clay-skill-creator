#!/usr/bin/env python3
"""Rewrap a submitted `SKILL.md` into the contract shape — and refuse to write the rest.

WHY THIS EXISTS, measured rather than assumed. Across the live corpus, **40 of 40** skills carry a
`## Declared inputs` heading and **5 of 40** carry `## Representative output`. The marketplace page
matches those headings exactly, so on thirty-five of forty published pages the representative output
is not the creator's — a model is asked to produce one, and it does.

Seen on a real submission, in a screenshot: a skill with no `## Representative output` at all got a
page carrying a contact table, a task id, and an **"Enrichment Approval Queue"** marked *Approved*.
That skill has no approval step, no queue and no task states. The fabrication sits under the
creator's byline, and it lifted a real person's name out of the file's own `.vcf` example while it
was at it.

So the cheapest fix at this end is to stop handing the page a heading it cannot read, when the
content is already there under a different name.

THE LINE THIS TOOL WILL NOT CROSS, and it is the whole design:

    RENAME what the author wrote.  NEVER AUTHOR what they did not.

The consent text creators agree to permits editing "for clarity, house voice, formatting, safety,
and compatibility **while keeping my substantive judgment and intended workflow intact**". Renaming
a heading is formatting. Writing a missing section is substantive judgment, and it is judgment only
the author holds — a `## Declared inputs` row needs its third column, *what happens when this input
is absent*, which is a claim about degrade behaviour nobody else can make. The kit's own rule:
"never supply an answer the creator did not give."

FOUR CLASSES, and the last two are the interesting ones:

  1. SAFE — applied. Slugify `name`; retitle a heading whose alias is unambiguous.
  2. PROPOSED — printed, never applied without `--apply`, and always shown as a diff first.
     Taxonomy fields (`category`, `personas`, `keywords`) are derived by keyword match, which is a
     GUESS. A wrong `category` mis-files a skill, which is worse than an absent one, so these are
     never silent.
  3. AUTHOR-ONLY — reported, never touched. `touches` and `mechanism` are in here DELIBERATELY and
     this is a correction to an earlier plan that had them auto-derived. The flow derives them when
     the authoring agent wrote the steps itself; this tool did not. `touches` is a safety
     declaration, and a regex that guesses `read-only` on a skill that writes records is the worst
     failure this file could have. Same for any section that does not exist at all.
  4. FLAGGED — a real person's name used as example data. Reported with its line, never replaced:
     choosing the placeholder is a content edit, and the author may have had permission.

A file this tool cannot fully rewrap is the normal case, and the residue is exactly the part that
had to go back to the author anyway. Getting most of the way there is the point; pretending to get
all the way there is the failure.

Usage:
  normalise_skill.py <dir>            report only — prints the diff, writes nothing
  normalise_skill.py <dir> --apply    apply classes 1 and 2
  normalise_skill.py <dir> --json     machine-readable
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _cand in (HERE, os.path.abspath(os.path.join(HERE, "..", "..", "..", "eval", "validators"))):
    if os.path.isfile(os.path.join(_cand, "portability.py")):
        sys.path.insert(0, _cand)
        break
import portability as P  # noqa: E402

ROOT_FILE = "SKILL.md"

# HEADING ALIASES — a CLOSED map, and every entry has to be unambiguous in one direction.
#
# `## Guardrails` is deliberately absent. It reads like `## Rules`, and it also reads like
# `## What this skill does not claim`, and a rename that picks wrong moves content under a heading
# that makes a different promise. Ambiguous stays untouched and gets reported.
# TWO MAPS, SPLIT BY CONFIDENCE, and the split came from running this on the live corpus.
#
# `## Output` appears on 11 of the 40 published skills and holds a PROSE description of the output
# shape — "per person: name · domain · email · status …". Renaming it to `## Representative output`
# makes the page render the creator's own words instead of asking a model to invent an artifact,
# which is a large improvement on today. But the contract means something narrower by that heading:
# a literal worked instance, with its own `### Input` / `### Output` / `### What it does not include`.
# Prose under that title is true and is not quite what the heading promises.
#
# So it is PROPOSED rather than applied. An alias that is certainly the same thing (`example output`)
# is safe; an alias that is probably the same thing (`output`) is shown and waits for a yes. The
# distinction is not pedantry — applying the second silently would edit what 11 published pages
# present as a worked example, on this tool's own authority.
#
# `## Guardrails` is in NEITHER map. It reads like `## Rules` and equally like
# `## What this skill does not claim`, and those headings make different promises.
SAFE_ALIASES: dict[str, tuple[str, ...]] = {
    "Declared inputs": (
        "declared input", "required input", "required inputs",
        "what you supply", "what the installer supplies",
    ),
    "Representative output": (
        "example output", "example outputs", "sample output", "sample outputs",
        "representative outputs", "example result",
    ),
    "What this skill touches": ("what it touches", "read/write posture"),
    "What this skill does not claim": ("what it does not claim",),
    "What good looks like": ("what success looks like",),
}
PROPOSED_ALIASES: dict[str, tuple[str, ...]] = {
    "Declared inputs": ("input", "inputs", "parameters"),
    "Representative output": ("output", "outputs", "what it returns"),
    "What this skill touches": ("reads and writes", "data access"),
    "What this skill does not claim": ("limitations", "known limitations", "caveats"),
    "What good looks like": ("success criteria", "definition of done"),
}
HEADING_ALIASES = {k: SAFE_ALIASES.get(k, ()) + PROPOSED_ALIASES.get(k, ())
                   for k in set(SAFE_ALIASES) | set(PROPOSED_ALIASES)}
_SAFE_TO_CANON = {a: c for c, al in SAFE_ALIASES.items() for a in al}
_PROPOSED_TO_CANON = {a: c for c, al in PROPOSED_ALIASES.items() for a in al}

# Frontmatter keys, in the order the contract prints them.
FM_ORDER = ("name", "description", "category", "personas", "mechanism", "touches", "keywords")
# Never guessed. See class 3 in the module docstring.
AUTHOR_ONLY_FM = ("mechanism", "touches")

# Keyword match for the taxonomy guess. Intentionally small: a big table reads as authority the
# match does not have. Ties and misses produce no proposal rather than a coin flip.
_CATEGORY_CUES = {
    "enrich": ("enrich", "waterfall", "fill in missing", "contact detail", "append"),
    "find-contact-data": ("work email", "phone number", "mobile", "email address", "find email"),
    "verify-and-clean": ("verify", "validate", "dedupe", "deliverab", "hygiene", "clean"),
    "build-lists": ("build a list", "source", "prospect list", "tam", "audience"),
    "score-and-qualify": ("score", "qualify", "tier", "rank", "icp fit"),
    "research": ("research", "brief", "one-pager", "summarise", "summarize"),
    "signals": ("signal", "trigger", "job change", "funding", "hiring", "intent"),
    "route-and-automate": ("route", "workflow", "automate", "unattended", "webhook"),
    "personalize-outbound": ("personalis", "personaliz", "cold email", "first line", "sequence"),
    "paid-ads": ("ad ", "ads ", "audience push", "campaign audience"),
}
_PERSONA_CUES = {
    "gtm-engineer": ("workflow", "graph", "code node", "api", "build"),
    "revops": ("crm", "pipeline", "routing", "ops", "data hygiene"),
    "sales-development": ("prospect", "outbound", "sequencer", "cold"),
    "account-executive": ("deal", "opportunity", "account plan"),
    "marketing": ("campaign", "webinar", "event", "nurture"),
    "recruiter": ("candidate", "recruit", "hiring pipeline"),
    "founder": ("founder", "small team", "solo"),
    "sales-leader": ("forecast", "territory", "quota"),
}
_KEYWORD_CUES = {
    "waterfall": ("waterfall", "cascade", "fall through", "fallback provider"),
    "find-phone-number": ("phone", "mobile"),
    "cold-email": ("cold email", "cold outreach"),
    "crm-hygiene": ("hygiene", "dedupe", "duplicate"),
    "job-change": ("job change", "changed jobs", "new role"),
    "lead-scoring": ("lead scor", "score inbound"),
    "sequencer": ("sequencer", "outreach", "salesloft", "smartlead"),
    "tech-stack": ("tech stack", "technograph"),
    "csv": ("csv",),
    "plg": ("signup", "sign-up", "free trial", "product-led"),
    "webinar": ("webinar",),
    "event-follow-up": ("event follow", "post-event", "attendee"),
    "catch-all-domains": ("catch-all", "catchall"),
    "local-business": ("local business", "google maps"),
    "livestream": ("livestream",),
}

# A person's full name used as example data. TWO capitalised tokens beside a filename or a vCard
# field — narrow on purpose, because "Contact Summary" is two capitalised tokens and is not a name.
_NAME_AS_EXAMPLE = re.compile(
    r"\b([A-Z][a-z]{1,15})[_ ]([A-Z][a-z]{1,15})\b(?=[^\n]{0,24}\.vcf)"
    r"|(?:^|\n)\s*(?:FN|N):\s*([A-Z][a-z]{1,15}[; ][A-Z][a-z]{1,15})"
)


def _split_frontmatter(text: str) -> tuple[str, str]:
    m = re.match(r"(?s)\A---\n(.*?)\n---\n?", text)
    return (m.group(1), text[m.end():]) if m else ("", text)


def _fm_get(fm: str, key: str) -> str | None:
    m = re.search(rf"(?ms)^{re.escape(key)}:\s*(.*?)(?=^[A-Za-z_][\w-]*:\s|\Z)", fm)
    return m.group(0).rstrip("\n") if m else None


def _slugify(value: str) -> str:
    s = re.sub(r"\([^)]*\)", " ", value)           # drop parentheticals
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def _guess(cues: dict[str, tuple[str, ...]], haystack: str, limit: int) -> list[str]:
    scored = []
    for value, needles in cues.items():
        n = sum(1 for needle in needles if needle in haystack)
        if n:
            scored.append((n, value))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [v for _, v in scored[:limit]]


def normalise(root: str) -> dict:
    """Return the plan. Writes nothing."""
    path = os.path.join(root, ROOT_FILE)
    with open(path, encoding="utf-8") as fh:
        original = fh.read()

    fm, body = _split_frontmatter(original)
    applied: list[dict] = []
    proposed: list[dict] = []
    author_only: list[dict] = []
    flagged: list[dict] = []

    # ---- class 1a: the slug ---------------------------------------------------------------
    name_line = _fm_get(fm, "name")
    new_fm = fm
    if name_line:
        raw = name_line.split(":", 1)[1].strip()
        if raw and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", raw):
            slug = _slugify(raw)
            if slug:
                new_fm = new_fm.replace(name_line, f"name: {slug}", 1)
                applied.append({"change": "slugify_name", "from": raw, "to": slug,
                                "why": "`name` is the slug and the directory name; the contract is "
                                       "lowercase and hyphens. The prose title stays as the H1."})

    # ---- class 1b: heading aliases -------------------------------------------------------
    new_body = body
    for m in list(re.finditer(r"(?m)^(#{2,3})\s+(.+?)\s*$", body)):
        title = m.group(2).strip()
        key = title.lower().rstrip(":").strip()
        canon = _SAFE_TO_CANON.get(key) or _PROPOSED_TO_CANON.get(key)
        if not canon or title.lower() == canon.lower():
            continue
        if re.search(rf"(?im)^#{{2,3}}\s+{re.escape(canon)}\b", body):
            author_only.append({
                "issue": "alias_and_canonical_both_present",
                "detail": f"`{title}` looks like `{canon}`, which the file already has. "
                          "Merging two sections is a content decision.",
            })
            continue
        if key in _SAFE_TO_CANON:
            new_body = new_body.replace(m.group(0), f"{m.group(1)} {canon}", 1)
            applied.append({"change": "retitle_heading", "from": title, "to": canon,
                            "why": "the page matches this heading exactly, and this alias means "
                                   "the same thing"})
        else:
            proposed.append({"change": "retitle_heading", "field": f"heading:{title}",
                             "value": canon, "from": title, "to": canon,
                             "why": "probably the same section, not certainly — the contract means "
                                    "a literal worked instance by this heading, and this may be "
                                    "prose about the output. Your call."})

    # ---- class 3: sections that do not exist, and the two author-only fields -------------
    # A SECTION WITH A PENDING RETITLE IS NOT ABSENT. The first version reported `Declared inputs`
    # as both proposed-and-absent in the same run, because this check read the body before the
    # proposals were applied. Contradicting itself in one report is how a reader decides the tool
    # does not know, and then ignores both halves.
    pending = {x["to"] for x in proposed if x.get("change") == "retitle_heading"}
    for canon in ("Declared inputs", "What this skill touches", "Representative output",
                  "What this skill does not claim", "What good looks like"):
        if canon in pending:
            continue
        if not re.search(rf"(?im)^#{{2,3}}\s+{re.escape(canon)}\b", new_body):
            author_only.append({
                "issue": "section_absent",
                "section": canon,
                "detail": "not present under this or any alias this tool recognises. NOT written "
                          "here: the content is the author's judgment, not a format.",
            })
    for key in AUTHOR_ONLY_FM:
        if not _fm_get(new_fm, key):
            author_only.append({
                "issue": "frontmatter_absent",
                "field": key,
                "detail": "derived from the steps by whoever wrote them. This tool did not write "
                          "them, and guessing `touches` could under-declare a write.",
            })

    # ---- class 2: the taxonomy guess ------------------------------------------------------
    hay = (original.lower())
    for key, cues, limit in (("category", _CATEGORY_CUES, 1),
                             ("personas", _PERSONA_CUES, P.MAX_PERSONAS),
                             ("keywords", _KEYWORD_CUES, P.MAX_KEYWORDS)):
        if _fm_get(new_fm, key):
            continue
        picks = _guess(cues, hay, limit)
        if not picks:
            author_only.append({"issue": "frontmatter_absent", "field": key,
                                "detail": "no cue matched, so nothing is proposed rather than a "
                                          "value picked at random."})
            continue
        value = picks[0] if key == "category" else "[" + ", ".join(picks) + "]"
        proposed.append({"change": "derive_frontmatter", "field": key, "value": value,
                         "why": "keyword match against the body — a GUESS, shown rather than "
                                "applied, because a wrong value mis-files the skill"})

    # ---- class 4: a real name as example data --------------------------------------------
    for m in _NAME_AS_EXAMPLE.finditer(original):
        # The whole match, not the first non-empty group: the alternation captures the
        # given and family names separately, so a group is half a name.
        hit = m.group(0).strip().lstrip("FN:").lstrip("N:").strip()
        flagged.append({
            "issue": "personal_name_as_example",
            "evidence": hit,
            "line": original[:m.start()].count("\n") + 1,
            "detail": "reads as a real person's name used as example data. NOT replaced — picking "
                      "the placeholder is a content edit, and the author may have permission. "
                      "Reserved names are in references/scrubbing.md.",
        })

    rewritten = (f"---\n{new_fm}\n---\n{new_body}" if fm else new_body)
    diff = list(difflib.unified_diff(original.splitlines(True), rewritten.splitlines(True),
                                     fromfile=f"a/{ROOT_FILE}", tofile=f"b/{ROOT_FILE}"))
    return {
        "schema": "skill-normalise/1.0.0",
        "package": root,
        "applied": applied,
        "proposed": proposed,
        "author_only": author_only,
        "flagged": flagged,
        "diff": "".join(diff),
        "rewritten": rewritten,
        "changed": rewritten != original,
        # A file with nothing in `author_only` is contract-shaped after this runs. Anything in it
        # has to go back, and saying so is the point rather than a caveat.
        "submittable_after_apply": not author_only,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--apply", action="store_true", help="write classes 1 and 2")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    plan = normalise(args.dir)

    if args.apply:
        # REORDER BY KEY BLOCK, NEVER BY LINE, and the first version of this corrupted the file.
        # `description: >-` owns every indented line beneath it. Sorting lines individually moved
        # three new keys in between the key and its own continuation, leaving orphaned prose inside
        # the frontmatter and a description that ended at the fold marker. On a creator's submission
        # that is worse than any formatting problem it was fixing: the tool that rewraps a file has
        # to be the last thing that could break it.
        fm, body = _split_frontmatter(plan["rewritten"])
        blocks: list[tuple[str, list[str]]] = []
        for line in fm.splitlines():
            if re.match(r"^[A-Za-z_][\w-]*:", line):
                blocks.append((line.split(":", 1)[0].strip(), [line]))
            elif blocks:
                blocks[-1][1].append(line)     # a continuation belongs to the key above it
            else:
                blocks.append(("", [line]))
        have = {k for k, _ in blocks}
        # Proposed HEADING retitles act on the body, not the frontmatter.
        for prop in plan["proposed"]:
            if prop.get("change") == "retitle_heading":
                body = re.sub(rf"(?m)^(#{{2,3}})\s+{re.escape(prop['from'])}\s*$",
                              rf"\1 {prop['to']}", body, count=1)
        for prop in plan["proposed"]:
            if prop.get("change") == "retitle_heading":
                continue
            if prop["field"] not in have:
                blocks.append((prop["field"], [f"{prop['field']}: {prop['value']}"]))
        order = {k: i for i, k in enumerate(FM_ORDER)}
        blocks.sort(key=lambda kv: order.get(kv[0], len(FM_ORDER)))
        fm_out = "\n".join(ln for _, lines in blocks for ln in lines)
        out = f"---\n{fm_out}\n---\n{body}"
        with open(os.path.join(args.dir, ROOT_FILE), "w", encoding="utf-8") as fh:
            fh.write(out)
        plan["written"] = True

    if args.json:
        print(json.dumps({k: v for k, v in plan.items() if k != "rewritten"}, indent=1))
        return 0

    print(f"\n{'APPLIED' if args.apply else 'WOULD APPLY'} — formatting only")
    for a in plan["applied"] or [{"change": "(nothing)"}]:
        print(f"  · {a['change']}: {a.get('from','')} -> {a.get('to','')}".rstrip(" ->"))
    print("\nPROPOSED — a guess, needs your yes")
    for p in plan["proposed"] or [{"field": "(nothing)", "value": ""}]:
        print(f"  ? {p['field']}: {p['value']}")
    print("\nAUTHOR ONLY — not written here, send these back")
    for a in plan["author_only"] or [{"issue": "(nothing)"}]:
        print(f"  ! {a.get('section') or a.get('field') or a['issue']}"
              f"{' — ' + a['detail'] if a.get('detail') else ''}")
    if plan["flagged"]:
        print("\nFLAGGED — read, not changed")
        for f in plan["flagged"]:
            print(f"  ⚑ line {f['line']}: {f['evidence']!r} — {f['detail'][:80]}")
    print(f"\nsubmittable after apply: {plan['submittable_after_apply']}")
    if plan["diff"] and not args.apply:
        print("\n--- diff ---")
        print(plan["diff"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
