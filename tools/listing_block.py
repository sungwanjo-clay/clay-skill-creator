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

WHAT THIS MEASURES, AND WHAT IT DOES NOT. Read the paragraph above carefully and you can already see
the gap: every check listed is a check for ROUTER TEXT. "Use whenever", "someone asks", a do-NOT
list, a sibling slug, "with Clay" — router-speak, all five. There is no check anywhere in this file
for whether the copy is written from the reader's seat. So:

    A PASS MEANS: the five fields are present, within their length bounds, and free of the five
                  router habits. It is a floor, and a narrow one.
    A PASS DOES NOT MEAN: the copy is good, or human-facing, or ready to publish.

**`29 of 29` IS NOT A QUALITY NUMBER AND MUST NOT BE QUOTED AS ONE.** It circulated as one, which is
how this got found. Measured on the corpus that passes 29 of 29:

  | field | median clauses | max | begins with an imperative verb |
  |---|---|---|---|
  | one-liner | 2 | 4 | **19/29** |
  | problem | 4 | 7 | 0/29 |
  | delivers | **8** | **13** | 2/29 |
  | example prompt | 3 | 6 | 12/29 |
  | also asked as | 1 | 3 | 11/29 |

`delivers` at a median of eight clauses is the clearest of it — nobody speaks in eight clauses, and
one in this corpus reads "Employee count and percent change across 3, 6, 12 and 24-month windows,
bucketed from shrinking to hyper-growth, with base counts always shown, the matched company verified,
two windows read together so a recent turn is visible, and unverifiable rows named as such." That
passes every check here. The one-liner's tell is different and is not length: 19 of 29 open with an
imperative verb, which is an author describing the tool's action rather than a reader learning what
they get. One of them puts a methodology caveat in the headline slot — "…with the base counts the
percentage rests on".

AND WHY NO PATTERN CAN FIX IT, which is the useful part. 12 of 29 `example prompt`s ALSO open with an
imperative verb, and there it is correct: from the reader's seat an imperative is a request ("Find me
the domains for these"), while in a one-liner the same token is a product description. **Identical
surface form, opposite voice.** Any pattern sharp enough to catch one would fire on the other, so the
property is not expressible here. Prose quality is measured by the LLM projection; this file is the
floor it is measured against, plus a fallback if it is unavailable.

The two fields that DO come out in the reader's voice are the two whose brief names a person — "a
sentence a real person would type", "three other ways people phrase the same request" — against three
briefs that ask what the artifact does. The lever is the elicitation, not the checker, and it lives in
`SKILL-TEMPLATE.md`.

Report coverage BY SLUG. "29 of 29, listing each" — never an aggregate pass line, which is how a
single failing row hides.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

FIELDS = ("one-liner", "problem", "delivers", "example prompt", "also asked as")

# PUBLISHED SLUGS, FROZEN. The sibling-slug rule needs to know a slug when it sees one, and its
# first form was a hyphen-shape pattern — `\(([a-z0-9]+-){2,}[a-z0-9]+\)` — which fires on
# `(end-to-end)`, `(day-to-day)`, `(one-to-one)`, `(business-to-business)` and `(out-of-the-box)`.
# Those are ordinary page copy, so between "a routing cross-reference" and "an English compound in
# parentheses" the rule had no discriminating power at all: it matched the SHAPE of a slug, and a
# slug shares its shape with any hyphenated phrase. Measured before any out-of-sample submission
# arrived, from a probe written for the pre-registration rather than in answer to a complaint.
#
# A LITERAL LIST rather than a directory read, because this module is projected into the kit and runs
# on a creator's machine where `skills/` does not exist. It goes stale, and the DIRECTION of the
# staleness is the argument for freezing it: a slug missing from this list makes the rule UNDER-fire
# on a genuine cross-reference, costing one review comment. A shape heuristic OVER-fires on
# "(end-to-end)" and costs an author's confidence in every check in this file. Given that asymmetry,
# missing a new slug is the cheaper failure.
PUBLISHED_SLUGS = frozenset((
    "account-health-audit", "account-intelligence-analyst", "account-tier-scoring",
    "build-prospect-list", "buyer-classification", "clean-and-refresh-contact-data",
    "clean-email-list", "company-research-brief", "competitive-intelligence-radar",
    "dedupe-contacts", "detect-tech-stack", "enrich-account-list", "enrich-signup-users",
    "find-decision-makers-at-company", "find-linkedin-profile", "find-work-email",
    "find-work-phone", "headcount-growth", "hiring-radar", "icp-matrix-builder",
    "inbound-triggers-monitor", "monitor-buying-signals", "resolve-company-domain",
    "score-inbound-leads", "scrape-any-website", "signal-sourcer", "source-local-businesses",
    "tam-builder", "track-champion-job-changes", "verify-email-deliverability",
))

_PARENTHESISED = re.compile(r"\(([a-z0-9][a-z0-9-]*[a-z0-9])\)")


def _names_a_sibling_skill(value: str) -> bool:
    """A parenthesised token that is an actual published slug, not merely hyphenated."""
    return any(m.group(1) in PUBLISHED_SLUGS for m in _PARENTHESISED.finditer(value))


# Trigger-string habits. Each one is legitimate in `description` and wrong in page copy.
_ROUTER_HABITS = (
    (re.compile(r"(?i)\buse whenever\b"), "router phrasing 'Use whenever' — this is page copy"),
    (re.compile(r"(?i)\bsomeone (?:asks|says)\b"), "router phrasing 'someone asks/says'"),
    (re.compile(r"(?i)\bdo NOT use\b"), "a do-NOT routing list belongs in `description`"),
    (re.compile(r"(?i)\busing clay\b|\bwith clay\b"), "'with Clay' is router filler in page copy"),
)

# Held apart from the regex tuple because it is not a regex — it is a set-membership test, and saying
# so keeps the pattern list honest about what each entry actually is.
_ROUTER_PREDICATES = (
    (_names_a_sibling_skill, "a bare sibling skill slug in parentheses"),
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
        for pred, why in _ROUTER_PREDICATES:
            if pred(v):
                r.problems.append(f"`{f}`: {why}")

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
    # THE SCOPE RIDES WITH THE NUMBER. A docstring nobody opens does not stop "29 of 29" being
    # quoted as a quality claim — which is exactly what happened — so the qualifier is printed on
    # the same line every run, and the word "router" is in it rather than implied.
    lines.append(f"Listing-block coverage: {ok} of {len(results)}, by slug "
                 f"— fields present, in bounds, no router habits. NOT a measure of whether the "
                 f"copy reads from the reader's seat; that is the projection's job.")
    for r in sorted(results, key=lambda x: x.slug):
        mark = "ok  " if r.ok else "FAIL"
        lines.append(f"  {mark} {r.slug}")
        for p in r.problems:
            lines.append(f"         {p}")
    return "\n".join(lines)
