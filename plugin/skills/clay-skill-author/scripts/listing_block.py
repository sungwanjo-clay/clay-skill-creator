"""The `## Listing` block: the five page fields a skill DECLARES instead of us mining its prose.

WHY DECLARATION REPLACED EXTRACTION, because the measurement is the whole argument. The detail pages
were built by pulling structure out of SKILL.md that SKILL.md never promised. The trigger-phrase
extractor keyed on `Use whenever someone says:` and across the thirty seed skills the phrasing was
SAYS 1, ASKS 20, OTHER 8, NONE 1 — and the single skill using "says" is the one the extractor was
written against. Three rounds of fixes each moved the same defect one layer down. So the skill states
its page fields and the page renders a declaration.

THE OTHER HALF, and it is the one that makes this a content rule rather than a schema rule. SKILL.md
is AGENT-FACING everywhere else: `description` is a keyword-dense router string written for a model,
and it was being rendered to customers as page copy. The Listing block is the only HUMAN-FACING part
of the file. So the checks below reject trigger-string habits leaking in — "Use whenever someone
asks", a do-NOT list naming sibling skills, a bare slug where a sentence belongs. A schema check
alone would pass a block that is five fields of router text.

Report coverage BY SLUG. "29 of 29, listing each" — never an aggregate pass line, which is how a
single failing row hides.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

FIELDS = ("one-liner", "problem", "delivers", "example prompt", "also asked as")

# Trigger-string habits. Each one is legitimate in `description` and wrong in page copy.
_ROUTER_HABITS = (
    (re.compile(r"(?i)\buse whenever\b"), "router phrasing 'Use whenever' — this is page copy"),
    (re.compile(r"(?i)\bsomeone (?:asks|says)\b"), "router phrasing 'someone asks/says'"),
    (re.compile(r"(?i)\bdo NOT use\b"), "a do-NOT routing list belongs in `description`"),
    (re.compile(r"\(([a-z0-9]+-){2,}[a-z0-9]+\)"), "a bare sibling slug in parentheses"),
    (re.compile(r"(?i)\busing clay\b|\bwith clay\b"), "'with Clay' is router filler in page copy"),
)

_MIN = {"one-liner": 30, "problem": 90, "delivers": 90, "example prompt": 20, "also asked as": 20}
_MAX = {"one-liner": 160, "problem": 420, "delivers": 420, "example prompt": 200, "also asked as": 260}


@dataclass
class Result:
    slug: str
    present: bool = False
    fields: dict = field(default_factory=dict)
    problems: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.present and not self.problems


def _extract(body: str) -> dict | None:
    m = re.search(r"^## Listing\s*$", body, re.M)
    if not m:
        return None
    rest = body[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    if nxt:
        rest = rest[:nxt.start()]
    out = {}
    for line in rest.splitlines():
        lm = re.match(r"\s*-\s+\*\*([^*]+?):\*\*\s*(.+?)\s*$", line)
        if lm:
            out[lm.group(1).strip().lower()] = lm.group(2).strip()
    return out


def check(slug: str, body: str) -> Result:
    r = Result(slug)
    found = _extract(body)
    if found is None:
        r.problems.append("no `## Listing` block")
        return r
    r.present = True
    r.fields = found

    for f in FIELDS:
        if f not in found:
            r.problems.append(f"missing field `{f}`")
            continue
        v = found[f]
        if len(v) < _MIN[f]:
            r.problems.append(f"`{f}` is {len(v)} chars, under {_MIN[f]}")
        if len(v) > _MAX[f]:
            r.problems.append(f"`{f}` is {len(v)} chars, over {_MAX[f]}")
        for rx, why in _ROUTER_HABITS:
            if rx.search(v):
                r.problems.append(f"`{f}`: {why}")

    for f in ("unknown",):
        pass
    for k in found:
        if k not in FIELDS:
            r.problems.append(f"unknown field `{k}`")

    # An example prompt is what a customer would type. A label is not a request.
    ex = found.get("example prompt", "")
    if ex and len(ex.split()) < 5:
        r.problems.append("`example prompt` is a label, not something a person would type")

    # Three alternatives, so the page has a phrase set rather than one guess.
    also = found.get("also asked as", "")
    if also:
        parts = [p.strip() for p in also.split("|") if p.strip()]
        if len(parts) < 3:
            r.problems.append(f"`also asked as` has {len(parts)} variants, needs 3")
        if any(len(p) < 8 for p in parts):
            r.problems.append("`also asked as` contains a variant too short to be a phrasing")

    # The one-liner is the card title line; a full stop is wanted, a paragraph is not.
    ol = found.get("one-liner", "")
    if ol.count(".") > 1:
        r.problems.append("`one-liner` is more than one sentence")
    return r


def render(results: list) -> str:
    lines = []
    ok = sum(1 for r in results if r.ok)
    lines.append(f"Listing-block coverage: {ok} of {len(results)}, by slug")
    for r in sorted(results, key=lambda x: x.slug):
        mark = "ok  " if r.ok else "FAIL"
        lines.append(f"  {mark} {r.slug}")
        for p in r.problems:
            lines.append(f"         {p}")
    return "\n".join(lines)
