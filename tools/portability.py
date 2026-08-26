"""The portability check — ONE check, FOUR resolvers.

    "Does this skill reference something the installer will not have?"

This is the reference implementation, and it runs in three places that must not drift:

  1. THE SUBMISSION DOOR   — server-side, synchronous, rejects before anything is stored
  2. THE REVIEW STAGE      — the same check, emitting findings instead of rejecting
  3. HERE                  — local validation, before you submit anything

`fixtures/` plus `run_conformance.py` are the CONTRACT between those three. A port that passes
the conformance suite is conformant; nothing else counts as evidence. Having two callers
protects against a wiring bypass; only the fixtures protect the shared logic.

Design rules, each of which is load-bearing:

  * DETERMINISTIC EVIDENCE BLOCKS; HEURISTIC EVIDENCE REPORTS. A hard block on a regex over
    English is the one failure mode a creator cannot debug.
  * NO NETWORK, EVER. Not DNS, not HTTP. Endpoint reachability is decided on host SYNTAX
    alone. Sandboxes routinely deny outbound access, so a network-dependent check would be
    non-comparable between callers even if it were safe.
  * THE STALE-ACTION RESOLVER REMAPS, IT DOES NOT BLOCK. That dangling reference points at
    OUR surface, so we hold the mapping. Blocking a creator over our own rename
    would be indefensible.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field, asdict
from typing import Iterable, Sequence

VERSION = "portability-check/1.4.0"
RULESET_VERSION = "portability-ruleset/1.2"  # the RULES: resolvers, severities, dispositions


def attribution() -> dict:
    """The structured attribution recorded on EVERY result — clean ones included.

    Requiring attribution only when a finding exists is backwards, and one real escape proves
    it: the result that let a broken skill through **looked clean** — `findings: []`,
    `finding_count: 0`. So the zero-finding verdict is precisely where attribution matters —
    without it there is no way to say which validator produced a clean verdict, which was the
    whole point of versioning the check.

    Three components, because they answer different questions:
      ruleset_version       — did the RULES change? (a disposition change)
      implementation_version— did the CODE change? (a bug fix with identical rules)
      fixture_suite_hash    — did the CONTRACT change? The fixtures ARE the contract between
                              the three callers above, so a silent fixture edit
                              is a silent contract change. Hashing them makes that visible.
    """
    return {
        "ruleset_version": RULESET_VERSION,
        "implementation_version": VERSION,
        "fixture_suite_hash": _fixture_suite_hash(),
    }


def _fixture_suite_hash() -> str:
    import hashlib
    import os

    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
    path = os.path.join(here, "conformance.json")
    try:
        with open(path, "rb") as fh:
            return "sha256:" + hashlib.sha256(fh.read()).hexdigest()[:32]
    except OSError:
        pass
    # PUBLIC-DISTRIBUTION FALLBACK. The fixture suite is a corpus of deliberately-bad inputs, so it
    # embeds real-shaped workspace handles — a live table id, our workspace number, a column id and
    # an auth handle. Those must not leave this repo, but a published checker still has to attribute
    # itself or every verdict it gives a creator carries the fail-closed sentinel. So a distribution
    # may ship a one-line digest sidecar instead of the corpus: identical attribution value, none of
    # the corpus content. Read-only, and it changes nothing where the fixture is present.
    try:
        with open(os.path.join(here, "SUITE_SHA256"), encoding="utf-8") as fh:
            token = fh.read().strip()
        if re.fullmatch(r"sha256:[0-9a-f]{32}", token):
            return token
    except OSError:
        pass
    if True:
        # Absent fixtures is reportable state, never a silent empty string. And it must not
        # ride along on a normal ACCEPTED result either: if
        # attribution is required and validation fails closed, an unverifiable build cannot
        # produce an accept. `check_portability` raises this into a SystemFailure, so the
        # disposition becomes `validation_unavailable` — retriable, no domain rows, no blame.
        return "sha256:UNAVAILABLE"

# ─────────────────────────────────────────────────────────────────────────────────────────
# Findings
# ─────────────────────────────────────────────────────────────────────────────────────────

# block  — deterministic, unrunnable for every installer. Intake rejects synchronously.
# reject — deterministic AND a secret is present. Hard stop until parameterized.
# remap  — our surface drifted; we hold the mapping. Never blocks.
# report — heuristic evidence. Surfaced for a human to read. NEVER a rejection.
SEVERITIES = ("reject", "block", "remap", "report")


@dataclass
class Finding:
    resolver: str  # missing_file | workspace_handle | unfilled_marker | optional_marker
    #                | retired_frontmatter
    #                | endpoint | stale_action
    severity: str  # one of SEVERITIES
    evidence: str  # the exact matched substring — quoted back, never paraphrased
    line: int  # 1-indexed line in the submitted body
    detail: str  # what the installer will experience
    remediation: str  # what makes it portable
    suggested: str | None = None  # only for remap

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class SystemFailure:
    """OUR defect, never the creator's. A separate channel from `findings`.

    This caught a real defect: a fail-closed design turned a
    resolver exception into a `block`-severity *portability finding*. That blocks the submission
    — correct — but attributes our crash to the creator's skill, so they go hunting for a
    portability problem that does not exist. Internal defects must never become false creator
    rejections. Both channels block; only one blames the creator.
    """

    code: str  # resolver_exception | fixture_suite_unavailable
    detail: str
    component: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Result:
    version: str = VERSION
    findings: list[Finding] = field(default_factory=list)
    system_failures: list[SystemFailure] = field(default_factory=list)

    @property
    def blocking(self) -> list[Finding]:
        return [f for f in self.findings if f.severity in ("block", "reject")]

    @property
    def disposition(self) -> str:
        """`validation_unavailable` outranks everything: if the check could not complete, we do
        not know whether the submission is clean, and saying "blocked" would imply we found
        something. Retriable, and it creates no domain rows."""
        if self.system_failures:
            return "validation_unavailable"
        return "blocked" if self.blocking else "ok"

    @property
    def is_portable(self) -> bool:
        # Only a COMPLETED clean check means portable. An incomplete one is not a pass.
        return self.disposition == "ok"

    def as_dict(self) -> dict:
        return {
            "version": self.version,
            # Present on EVERY result, clean or not. Authored here — by the
            # shared component — never claimed by a caller.
            "attribution": attribution(),
            "disposition": self.disposition,
            "retriable": self.disposition == "validation_unavailable",
            "portable": self.is_portable,
            "finding_count": len(self.findings),
            "blocking_count": len(self.blocking),
            "findings": [f.as_dict() for f in self.findings],
            "system_failures": [f.as_dict() for f in self.system_failures],
        }


# ─────────────────────────────────────────────────────────────────────────────────────────
# Line bookkeeping + code-fence masking
# ─────────────────────────────────────────────────────────────────────────────────────────


def _line_of(body: str, index: int) -> int:
    return body.count("\n", 0, index) + 1


def _fenced_spans(body: str) -> list[tuple[int, int]]:
    """Character spans inside ``` fences.

    Fenced blocks are ILLUSTRATIVE, not instructions to the installer's agent — a fenced
    `http://localhost:8080` in an example is not the skill depending on localhost. The fixture
    suite carries code-block false positives; this is the mechanism they exercise.
    """
    spans: list[tuple[int, int]] = []
    open_at: int | None = None
    for m in re.finditer(r"^[ \t]*(?:```|~~~).*$", body, re.MULTILINE):
        if open_at is None:
            open_at = m.end()
        else:
            spans.append((open_at, m.start()))
            open_at = None
    if open_at is not None:  # unterminated fence — treat the remainder as fenced
        spans.append((open_at, len(body)))
    return spans


def _in_fence(index: int, spans: Sequence[tuple[int, int]]) -> bool:
    return any(a <= index < b for a, b in spans)


# ─────────────────────────────────────────────────────────────────────────────────────────
# R1 — missing local file  (deterministic → block).  The missing-reference resolver.
# ─────────────────────────────────────────────────────────────────────────────────────────

# Relative markdown/text paths with a file extension. Anchored so we do not match bare
# words: requires either a leading ./ or a directory segment.
_EXT = r"(?:md|markdown|txt|json|ya?ml|csv|py|js|ts|sql|sh)"
_REL_PATH = re.compile(
    rf"""
    (?P<path>
        /(?:[\w.-]+/)*[\w.-]+\.{_EXT}          # ABSOLUTE — the author's filesystem
      | (?<![\w/.-])
        (?:
            (?:\.\./)+(?:[\w.-]+/)*[\w.-]+\.{_EXT}   # traversal out of the package
          | (?:\./)?(?:[\w.-]+/)+[\w.-]+\.{_EXT}      # nested relative
          | \./[\w.-]+\.{_EXT}                        # ./file.md
        )
    )
    """,
    re.VERBOSE,
)

_URL_ISH = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://")


def _normalize_ref(raw: str) -> str | None:
    """Normalize a claimed reference to a package-relative path, or None if unsafe/absolute.

    Traversal is NOT silently normalized away: `../secrets.md` escapes the package, so it is
    never resolvable and must surface rather than be rewritten into something that resolves.
    """
    p = raw.split("#", 1)[0].split("?", 1)[0]  # strip anchor / query
    if not p or p.startswith("/"):
        return None
    parts: list[str] = []
    for seg in p.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            return None  # traversal — report, never resolve
        parts.append(seg)
    return "/".join(parts) if parts else None


def _url_spans(body: str) -> list[tuple[int, int]]:
    """Character ranges occupied by URLs, so a path INSIDE one is never read as a package path.

    `_in_fence` is span-membership, not fence-specific, so it is reused verbatim here rather than
    duplicating the logic — one implementation, two callers.
    """
    return [(m.start(), m.end()) for m in _URL.finditer(body)]


def _resolve_missing_files(body: str, manifest: Iterable[str], fences) -> list[Finding]:
    url_spans = _url_spans(body)
    have = set()
    for f in manifest:
        n = _normalize_ref(f)
        if n:
            have.add(n)
    out: list[Finding] = []
    seen: set[str] = set()
    for m in _REL_PATH.finditer(body):
        raw = m.group("path")
        start = m.start("path")
        if _in_fence(start, fences):
            continue
        # Skip paths that are part of a URL (those are R3's business, not R1's).
        #
        # This WAS a 12-character lookback, and it could never work: in
        # `https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md`
        # the host alone is 26 characters, so `https://` is far outside the window and the path
        # component was reported as a package-relative missing file — evidence read
        # `/raw.githubusercontent.com/...`, the URL with its scheme and host shaved off.
        #
        # Consequence, found by a library-wide sweep (2026-08-14): SIX skills already marked
        # `built` carried a BLOCKING finding for one boilerplate line linking to public GitHub
        # docs. A blocking finding means intake rejects, so any creator linking to public
        # documentation would have been told their skill references a missing local file. That is
        # a FALSE CREATOR REJECTION — the precise failure this design exists to avoid, and the fix was
        # nearly applied in the wrong direction by editing six correct skills to satisfy it.
        #
        # A fixed-width lookback cannot bound a hostname, so span-masking replaces it: URL spans
        # are computed once and membership is tested, exactly as fences are.
        if _in_fence(start, url_spans):
            continue
        norm = _normalize_ref(raw)
        key = f"{raw}@{_line_of(body, start)}"
        if key in seen:
            continue
        seen.add(key)
        if norm is None:
            out.append(
                Finding(
                    resolver="missing_file",
                    severity="block",
                    evidence=raw,
                    line=_line_of(body, start),
                    detail="Reference escapes the package (absolute path or `..` traversal); "
                    "it can never resolve on an installer's machine.",
                    remediation="Reference a file inside the package, or inline the content.",
                )
            )
        elif norm not in have:
            out.append(
                Finding(
                    resolver="missing_file",
                    severity="block",
                    evidence=raw,
                    line=_line_of(body, start),
                    # The filename is IN the message, not only in `evidence`. Two of these used
                    # to render as the same sentence twice, with the name in a structured field a
                    # reader had to go dig for. That reasoning stays here; a creator does not need
                    # our defect history in a finding they are trying to act on.
                    detail=f"`{raw}` is referenced but is not in the package. The agent will "
                    "stall or INVENT the content — which looks like success.",
                    remediation=f"Add `{raw}` to the submission, or inline what it says. Keep the "
                    "reference relative and in a code span: an absolute URL is not checkable, so "
                    "this guard cannot see it and a missing file would validate clean.",
                )
            )
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────
# R2 — workspace-scoped handle
#      structured ids → block   ·   natural-language prose → report
# ─────────────────────────────────────────────────────────────────────────────────────────

# The `{{f_…}}`, `aa_…` and `t_…` forms were added after reading a REAL Clay table's
# `columns get` output (workspace <id>, 2026-08-13). They are not edge cases — they are the
# dominant shape: one 22-column table carried 74 `{{f_…}}` column references and 5 `aa_…`
# auth-account handles. A converter that transcribes formulas verbatim emits nothing BUT
# these, so a check that missed them would pass every table-derived skill unread.
# Clay SYSTEM columns are PORTABLE and must never be flagged. They carry semantic ids
# (`f_created_at`, `f_updated_at`) and exist identically in every table in every workspace,
# whereas user columns carry random ids (`f_<random-id>`). The patterns below already
# skip them because the alphanumeric class stops at the underscore — but that was ACCIDENT,
# not design, so it is pinned by conformance cases and stated here. A future regex tweak that
# starts blocking `{{f_created_at}}` would reject portable skills for referencing a built-in.
_SYSTEM_COLUMN = re.compile(r"^f_[a-z][a-z0-9_]*$")


def is_system_column(column_id: str) -> bool:
    """True for Clay built-ins, which are portable. Exported: the converter needs this too,
    to keep system columns OUT of its dead-column analysis (see the table-to-skill design note)."""
    return bool(_SYSTEM_COLUMN.match(column_id or ""))


_STRUCTURED_HANDLE = [
    # (regex, human label)
    (re.compile(r"\{\{\s*(?P<v>f_[A-Za-z0-9]{8,})\s*\}\}"), "Clay column reference"),
    (re.compile(r"(?<![\w-])(?P<v>f_[A-Za-z0-9]{12,})(?![\w-])"), "Clay column id"),
    (re.compile(r"(?<![\w-])(?P<v>aa_[A-Za-z0-9]{8,})(?![\w-])"), "Clay auth-account handle"),
    (re.compile(r"(?<![\w-])(?P<v>t_[A-Za-z0-9]{8,})(?![\w-])"), "Clay table id"),
    (re.compile(r"\btable[ _-]?(?:id)?\s*[:=#]?\s*(?P<v>\d{5,})\b", re.I), "table id"),
    (re.compile(r"\bcolumn[ _-]?id\s*[:=]?\s*(?P<v>[\w-]{6,})\b", re.I), "column id"),
    (re.compile(r"\bworkspace[ _-]?(?:id)?\s*[:=#]?\s*(?P<v>\d{4,})\b", re.I), "workspace id"),
    (re.compile(r"\bview[ _-]?id\s*[:=]?\s*(?P<v>[\w-]{6,})\b", re.I), "saved-view id"),
    (re.compile(r"https?://app\.clay\.com/\S*?/tables?/(?P<v>[\w-]+)", re.I), "table URL"),
]

# Heuristic prose. Reports only — never blocks. The converter is supposed to have
# parameterized these already; this catches hand-written (mode C) skills, which have no
# converter in the path.
# TWO DEFECTS, one read, 2026-08-20. This check was 100% of the measured noise floor: 6 findings
# across 30 known-good skills, all 6 wrong — "the email column", "the unknown column", "the evidence
# column".
#
# 1. THE TITLE-CASE REQUIREMENT WAS ALREADY HERE AND A FLAG DEFEATED IT. The old pattern demanded
#    `[A-Z]` for the noun phrase, under `(?ix)` — and `i` makes `[A-Z]` match lowercase. So the
#    discriminating condition was written, then silently switched off by a flag added for the
#    keywords. `i` is now scoped to the literals that want it, with `(?i:...)`, and nowhere else.
#
# 2. THE CANONICAL TRUE POSITIVE MATCHED NOTHING. "the Enterprise Accounts view" — the example this
#    check exists for — hit no branch: the view branch requires `the view called "…"`, with the name
#    AFTER the keyword, and real prose puts it before. So the check was firing only on the sentences
#    it should ignore and silent on the one it was built for. Both halves wrong is worse than either.
#
# The rule now, and it is the whole rule: the noun phrase before column/view/table must be QUOTED
# (any case — quoting is itself the author pointing at a named thing) or TITLE CASE THROUGHOUT.
# "the email column" is generic prose about a column; "the Enterprise Accounts view" names an
# artifact. That distinction is mechanical, which is what makes it worth having in a heuristic —
# and it is still `report` severity, because a capital letter is evidence, not proof.
_PROSE_HANDLE = re.compile(
    r"""(?x)
    \b(?:
        (?i:the|your|our|my)\s+
          (?: [`"'][^`"'\n]{2,40}[`"']                       # quoted — any case
            | [A-Z][\w./-]* (?:\s+[A-Z][\w./-]*){0,5}        # Title Case, every word
          )\s+
          (?i:column|view|table)
      | (?i:saved\s+view|the\s+view)\s+ (?i:called|named)\s+ [`"'][^`"'\n]{2,40}[`"']
      | (?i:in\s+(?:the\s+)?table)\s+ [`"'][^`"'\n]{2,40}[`"']
    )
    """
    # NO TRAILING \b, and that is a THIRD defect this rewrite found rather than introduced.
    # Two of these three branches end with a quote character. `\b` after a non-word character
    # requires a word character next, so at end of line — where a quoted name usually sits —
    # the boundary could never be satisfied and the branch could never match. Both quoted
    # branches were dead in the previous pattern for the same reason, which is why the check
    # fired only on the generic-prose branch: the noise floor was 100% of its output because
    # the signal branches were switched off. Each branch now ends on its own literal, which is
    # anchor enough.
)

# Two marker CLASSES, and the split is by executability. Until now `{{OPTIONAL}}`
# failed to match this regex and therefore did not block — correct behaviour, but by ACCIDENT of
# the character class rather than by agreement. Pinned deliberately so a future tweak cannot
# start blocking it, and so unanswered optional context is still visible to a reviewer.
_UNFILLED_MARKER = re.compile(r"\{\{\s*(?:UNKNOWN|TODO|FILL)\b[^}]*\}\}", re.I)
_OPTIONAL_MARKER = re.compile(r"\{\{\s*OPTIONAL\b[^}]*\}\}", re.I)


def _resolve_prose_handles(body: str, fences) -> list[Finding]:
    out: list[Finding] = []
    for m in _PROSE_HANDLE.finditer(body):
        if _in_fence(m.start(), fences):
            continue
        out.append(
            Finding(
                resolver="workspace_handle",
                severity="report",
                evidence=m.group(0).strip(),
                line=_line_of(body, m.start()),
                detail="Reads like a reference to a workspace artifact by name. This is a guess from "
                "wording alone, so it never blocks — if the name is generic prose rather "
                "than a real artifact, ignore it.",
                remediation="If it is a real workspace artifact, make it a declared input.",
            )
        )
    return out


# The frontmatter fields that are read, and the ones that are not. A CLOSED list on purpose: an
# open one cannot tell "a field we retired" from "a field we never had", and both are the same
# problem for a creator — they wrote something nothing consumes.
# TAXONOMY V2. `type` (task|play) and `tags` are retired: `type` was unvalidated free text —
# `type: banana` passed clean — and `tags` was doing three jobs in one bag, mixing what the installer
# brings, what machinery runs, and who it is for. Six skills were tagged `workflow` while building
# no workflow, which is what an unvalidated shared bag produces. Now: `category` (1 of 10),
# `personas` (1-2 of 8), `touches` (derived from the body block, so it cannot drift), `keywords`
# (<=5, managed registry).
LIVE_FRONTMATTER = ("name", "description", "category", "personas", "touches", "keywords")
# `keyword` (singular) was a slug that duplicated `name` on 34 of 36 — but on two it held a search
# SYNONYM (find-work-phone -> find-phone-number, score-inbound-leads -> lead-scoring), which the
# migration nearly deleted. Both were rescued into `keywords`. They belong in the listing block's
# `also asked as` once every skill has one; until then the long tail is the honest home.
RETIRED_FRONTMATTER = ("proof_status", "proof_gaps", "measure_class", "stage_p", "stage_e",
                       "type", "tags", "keyword")

_FRONTMATTER_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:", re.M)


def _resolve_retired_frontmatter(body: str) -> list[Finding]:
    """A frontmatter field nothing reads.

    REPORTS, never blocks. Nothing consumes these, so the skill runs correctly with them present —
    blocking would be punishing a creator for a field that costs them nothing at run time.

    WHY THIS EXISTS AS A CHECK RATHER THAN MORE PROSE. The authoring flow named `proof_gaps` and
    `proof_status` NINE times, every mention a prohibition, and showed no positive frontmatter
    template at all. A skill authored through that flow emitted both fields anyway. Nine negative
    mentions of a field name are still nine mentions: the prohibition was the exposure, which is the
    same failure already recorded for comments that demonstrate what a check catches and get caught
    by it. So the tenth prohibition is not the fix. A machine that names the field and the line is.

    Scoped to the frontmatter block, not the body: `proof_gaps` discussed in prose is a creator
    explaining what their skill does not claim, which is exactly what we asked them to do.
    """
    if not body.startswith("---"):
        return []
    end = body.find("\n---", 3)
    if end == -1:
        return []
    block = body[3:end]
    out: list[Finding] = []
    for m in _FRONTMATTER_KEY.finditer(block):
        key = m.group(1)
        if key not in RETIRED_FRONTMATTER:
            continue
        out.append(Finding(
            resolver="retired_frontmatter",
            severity="report",
            evidence=key,
            line=body[:3 + m.start()].count("\n") + 1,
            detail=f"`{key}` in the frontmatter is not read by anything. It was a field once and "
                   f"is not one now, so it has no effect on how the skill is routed, validated or "
                   f"published.",
            remediation=f"Delete `{key}`. If it held what the skill does NOT claim, that belongs in "
                        f"the body as a section a reader can see — the frontmatter is "
                        f"{', '.join(LIVE_FRONTMATTER)} and nothing else.",
        ))
    return out


_GOOD_SECTION = re.compile(r"^##+\s*What good looks like\s*$", re.M | re.I)

_TOUCHES_SECTION = re.compile(r"^##+\s*What this skill touches\s*$", re.M | re.I)
_TOUCHES_BODY = re.compile(
    r"^##+\s*What this skill touches\s*$(.*?)(?=^##\s|\Z)", re.M | re.I | re.S)
# The three axes, matched as labels rather than prose so a PARTIAL declaration is visible. `Never` is
# the one authors drop and the one a reviewer most wants.
_TOUCHES_AXES = (
    ("reads",  re.compile(r"(?im)^\W{0,6}\**\s*reads?\b")),
    ("writes", re.compile(r"(?im)^\W{0,6}\**\s*writes?\b")),
    ("never",  re.compile(r"(?im)^\W{0,6}\**\s*never\b")),
)

# WHY THIS REPORTS AND DOES NOT BLOCK, TODAY. Measured before choosing, not assumed: 0 of 39 skills
# in this repository carry the section — not the 30 library skills, not the four curated examples,
# not the three live external submissions. Blocking would reject the entire launch cohort on its
# first day, which is the mid-launch rejection the owner ruled against. Flipping it is this one
# constant, once the corpus has caught up.
#
# WHAT IT IS FOR, WHICH IS NOT WHAT IT LOOKS LIKE. It cannot tell whether a declaration is TRUE — no
# regex can, and the safety read is an LLM pass in the parser. Its job is to guarantee the
# declaration EXISTS, because that converts an unbounded question into a checkable one: "is this
# skill dangerous?" is a judgement call, while "it declares `Writes: nothing` — does any step write?"
# is a contradiction check against a stated claim. The three named axes are the point: something an
# LLM can diff against the body rather than prose it has to interpret.
TOUCHES_BLOCKS = False


def _resolve_what_this_skill_touches(body: str) -> list[Finding]:
    """`## What this skill touches` must be PRESENT, and must name all three axes."""
    sev = "block" if TOUCHES_BLOCKS else "report"
    if not _TOUCHES_SECTION.search(body):
        return [Finding(
            resolver="what_this_skill_touches",
            severity=sev,
            evidence="section absent",
            line=1,
            detail="No `## What this skill touches` section. An installer pointing this at their CRM "
                   "cannot tell what it reads, what it writes, or what it will never go near — and "
                   "the end of the file is too late to find out.",
            remediation="Add it near the top, with three labelled lines: **Reads** — the systems and "
                        "objects it reads. **Writes** — the same, or `nothing`. **Never** — what it "
                        "will not touch under any circumstances. Say `Writes: nothing` explicitly "
                        "where that is true; it is the most reassuring line a read-only skill has.",
        )]
    section = _TOUCHES_BODY.search(body)
    text = section.group(1) if section else ""
    missing = [name for name, rx in _TOUCHES_AXES if not rx.search(text)]
    if not missing:
        return []
    return [Finding(
        resolver="what_this_skill_touches",
        severity="report",
        evidence=", ".join(missing),
        line=body[:section.start()].count("\n") + 1 if section else 1,
        detail=f"`## What this skill touches` does not name: {', '.join(missing)}. A partial "
               f"declaration reads as a complete one, and the axis left out is the one nobody "
               f"checked.",
        remediation="Name all three, even where the answer is one word. `Writes: nothing` and "
                    "`Never: deletes or clears a field` are complete answers.",
    )]


def _resolve_what_good_looks_like(body: str) -> list[Finding]:
    """`## What good looks like` must be PRESENT. Whether it is any good is a reader's call.

    REPORTS, never blocks: absence is the reviewer's signal, and the stated consequence for a thin
    one — it gets sent back — is a human decision, not a regex verdict.

    WHAT THIS DELIBERATELY DOES NOT CHECK, because the first version did and was wrong. It also
    flagged a section as "a bare checklist" when the prose outside its bullets was short. Measured
    against the library that fired on 3 of 30, and reading them settled it: one is
    `account-health-audit`, a curated example, whose section names the two most common failure modes
    — inside its bullets. The bullets WERE the substance. The property that matters is whether a
    reader can tell a good run from a run that merely finished, and prose-words-outside-bullets does
    not measure that.

    The tempting fix was to tune the threshold until the library stopped complaining. That calibrates
    the check to the corpus instead of to the property, and it is how a check comes to encode
    "whatever we already wrote" as the standard. So the heuristic is gone and only the unambiguous
    half ships: the section is there, or it is not.
    """
    if _GOOD_SECTION.search(body):
        return []
    return [Finding(
        resolver="what_good_looks_like",
        severity="report",
        evidence="section absent",
        line=1,
        detail="No `## What good looks like` section. Without it, whoever installs this skill has no "
               "way to tell a run that worked from a run that merely finished — and neither will you, "
               "the next time you come back to it.",
        remediation="Add it, and describe the shape of a good outcome rather than listing steps: what "
                    "the output looks like when the skill worked, what a thin or empty run looks like "
                    "instead, and how to tell those apart at a glance.",
    )]


def _resolve_optional_markers(body: str, fences) -> list[Finding]:
    """`{{OPTIONAL: …}}` — context whose absence does not stop the skill running correctly.

    REPORTS, never blocks. Blocking on a question only memory can answer does not
    extract truth, it applies pressure to invent — and a plausible guess is indistinguishable
    from a real reason once it is prose. So the split is one test: *if the creator answers "I
    don't remember", can the skill still run correctly?* Yes → optional.

    It still surfaces, because a reviewer should be able to see what context is missing without
    that gating the creator.
    """
    out: list[Finding] = []
    for m in _OPTIONAL_MARKER.finditer(body):
        if _in_fence(m.start(), fences):
            continue
        out.append(
            Finding(
                resolver="optional_marker",
                severity="report",
                evidence=" ".join(m.group(0).split())[:110],
                line=_line_of(body, m.start()),
                detail="Optional context you left unanswered. Does NOT block: the skill runs "
                "correctly without it. Surfaced rather than hidden so the gap is visible, "
                "but leaving it is a legitimate answer.",
                remediation="Answer it if you can; leaving it is legitimate.",
            )
        )
    return out


def _resolve_unfilled_markers(body: str, fences) -> list[Finding]:
    """Unfilled unknown markers ARE deterministic — a structured artifact, not prose.

    This is how the interview-as-validation-rule works: the converter emits markers where it
    could not determine something, and intake blocks on any that survive.
    """
    out: list[Finding] = []
    for m in _UNFILLED_MARKER.finditer(body):
        if _in_fence(m.start(), fences):
            continue
        out.append(
            Finding(
                # Its OWN resolver, not workspace_handle. Found during the
                # v1 dogfood: a draft blocked purely on markers read as a "portability
                # problem", when it is the opposite — an honestly-incomplete draft awaiting
                # its author. Mislabelling it would send creators hunting for a handle that
                # is not there.
                resolver="unfilled_marker",
                severity="block",
                evidence=m.group(0).strip(),
                line=_line_of(body, m.start()),
                detail="An unfilled unknown marker from the authoring tool. The skill is "
                "incomplete by its own admission.",
                remediation="Fill the marker in your editor before submitting.",
            )
        )
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────
# R3 — an endpoint the installer cannot reach, and an embedded credential.
# (The internal tier letters are deliberately not used here: they appear nowhere else in
# the published file, so they would name a taxonomy the reader cannot resolve.)
#      SYNTAX ONLY. No DNS. No HTTP. Ever.
# ─────────────────────────────────────────────────────────────────────────────────────────

# "]" is ALLOWED so bracketed IPv6 authorities survive; excluding it truncated
# `http://[::1]:9000` to `http://[::1` and made host extraction raise — a fail-OPEN bug of
# exactly the shape of that escape, caught by the conformance suite against this very file.
_URL = re.compile(r"\b(?P<scheme>https?|ws|wss)://(?P<rest>[^\s`'\"<>)}]+)", re.I)
_URL_TRAILING = ".,;:!?'\""

_PRIVATE_SUFFIX = (".internal", ".local", ".localdomain", ".home.arpa", ".lan", ".intranet")
_LOCAL_NAMES = ("localhost", "localhost.localdomain", "ip6-localhost")

_CRED_IN_QUERY = re.compile(
    r"(?i)[?&](?:api[_-]?key|apikey|access[_-]?token|auth[_-]?token|token|key|secret|"
    r"password|passwd|pwd|signature|sig)=(?P<v>[^&\s]{6,})"
)
# Values that look like a live credential. This list is a deliberately NARROW BLOCKING SUBSET of
# the server-side validator, not parity with it: local only has to refuse to TRANSMIT something
# key-shaped, because a transmitted secret cannot be recalled. Wrong-and-strict is the correct
# direction here — a false positive costs one conversation, a false negative is permanent.
#
# `sk-[A-Za-z0-9]{20,}` used to sit here and it MISSED current OpenAI project keys: the character
# class has no hyphen, so it broke at the second dash of `sk-proj-…`. Verified live.
_CRED_SHAPES = re.compile(
    # The leading boundary is load-bearing: with hyphens inside the `sk-` class, any hyphenated
    # English phrase whose second word begins with "sk" matched from that point on. Found by
    # scanning our own corpus straight after widening the class — one false positive, in prose.
    #
    # SECOND-ORDER, and it happened twice while writing this file: a comment that DEMONSTRATES what
    # a check catches gets caught by the check. Both the assignment example above and the phrase
    # here had to be described rather than shown. If a comment needs the literal to be understood,
    # the check is under-specified, not the comment.
    r"(?<![A-Za-z0-9])(?:sk-ant-[A-Za-z0-9_-]{12,}"
    r"|sk-[A-Za-z0-9_-]{20,}"                      # sk-…, sk-proj-…: hyphens INSIDE the class
    r"|pat-[A-Za-z0-9-]{10,}"
    r"|gh[pousr]_[A-Za-z0-9]{20,}"           # classic PAT plus oauth/user/server/refresh
    r"|github_pat_[A-Za-z0-9_]{20,}"        # fine-grained, underscores are inside the shape
    r"|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{6,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|AIza[A-Za-z0-9_-]{35}"                      # Google API key, fixed 39-char total
    r"|-----BEGIN(?:\s[A-Z]+)*\sPRIVATE KEY-----"  # PEM block, any key type
    r")"
)

# A secret that carries no recognizable prefix, caught by its ASSIGNMENT instead. This is the shape
# most likely to appear in a real Clay column config, and no prefix list can reach it.
#
# Sentinels are excluded rather than the pattern being narrowed: a skill legitimately assigns a
# key name to a stand-in such as "not_observed_in_this_run", and angle-bracket placeholders are
# already outside the value class. Excluding a short list of known stand-ins keeps the check strict
# where it matters without flagging the vocabulary our own corpus uses to mean "absent".
#
# Deliberately described rather than demonstrated: an inline example of the assignment shape trips
# the disclosure scanner's own credential axis, which has no sentinel list. Two checks, one string,
# opposite verdicts — and the comment does not need the literal to make its point.
_CRED_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api[_-]?key|apikey|secret|token|access[_-]?token|auth[_-]?token|authorization"
    r"|bearer|password|passwd)"
    # An optional scheme word, so `authorization: Bearer <token>` is measured on the TOKEN.
    # Without it the value seen is "Bearer" — six characters, under the floor, silently safe.
    r"\s*[:=]\s*(?:Bearer\s+|Token\s+|Basic\s+)?[\"\']?(?P<v>[A-Za-z0-9_\-]{16,})[\"\']?"
)
_CRED_SENTINELS = re.compile(
    r"(?i)^(?:not[_-]?observed|not[_-]?exercised|none|null|example|placeholder|redacted|removed|"
    r"your[_-].*|the[_-].*|installer[_-].*|declared[_-].*|see[_-].*|x{4,}|\.{3,})"
)


def _decode_host_to_ip(host: str) -> ipaddress._BaseAddress | None:
    """Decode a host to an IP, including the encoded forms the fixture suite requires.

    Covers dotted-quad, bracketed IPv6, bare decimal (http://2130706433/), hex
    (0x7f000001), and octal (0177.0.0.1) — all of which resolve to 127.0.0.1 and all of
    which a naive `host.startswith("127.")` check misses.
    """
    h = host.strip().strip("[]")
    try:
        return ipaddress.ip_address(h)
    except ValueError:
        pass
    try:  # bare decimal / hex — int(x, 0) handles 0x and 0o prefixes
        if re.fullmatch(r"(?:0[xX][0-9a-fA-F]+|\d+)", h):
            val = int(h, 0)
            if 0 <= val <= 0xFFFFFFFF:
                return ipaddress.IPv4Address(val)
    except ValueError:
        pass
    if re.fullmatch(r"0[0-7]*(?:\.0[0-7]*){3}", h):  # dotted octal
        try:
            octets = [int(p, 8) for p in h.split(".")]
            if all(0 <= o <= 255 for o in octets):
                return ipaddress.IPv4Address(".".join(str(o) for o in octets))
        except ValueError:
            pass
    # Mixed hex octets, e.g. 0x7f.0.0.1
    if "." in h and any(p.lower().startswith("0x") for p in h.split(".")):
        try:
            octets = [int(p, 0) for p in h.split(".")]
            if len(octets) == 4 and all(0 <= o <= 255 for o in octets):
                return ipaddress.IPv4Address(".".join(str(o) for o in octets))
        except ValueError:
            pass
    return None


def _classify_host(host: str) -> str | None:
    """Return a reason string if the host is syntactically non-portable, else None."""
    h = host.lower().rstrip(".")
    if h in _LOCAL_NAMES:
        return "loopback hostname"
    if any(h.endswith(s) for s in _PRIVATE_SUFFIX):
        return "private/internal domain suffix"
    ip = _decode_host_to_ip(h)
    if ip is not None:
        if ip.is_loopback:
            return "loopback address"
        if ip.is_link_local:
            return "link-local address"
        if ip.is_private:
            return "private address range"
        if ip.is_unspecified:
            return "unspecified address"
        if getattr(ip, "is_reserved", False):
            return "reserved address range"
        # A public literal IP is portable but brittle; report, not block.
        return None
    if "." not in h and h not in ("",):
        return "single-label host (resolves only inside a private network)"
    return None


def _authority_host(authority: str) -> str:
    """Host from an authority component. TOTAL — never raises, whatever the input.

    Bracketed IPv6 keeps its brackets; everything else drops a trailing :port. A partial or
    malformed authority returns something classifiable rather than exploding, because an
    exception in a validator is an accept.
    """
    a = authority.strip()
    if a.startswith("["):
        end = a.find("]")
        return a[: end + 1] if end != -1 else a  # unterminated bracket: hand back as-is
    return a.rsplit(":", 1)[0] if ":" in a else a


def _resolve_endpoints(body: str, fences) -> list[Finding]:
    out: list[Finding] = []
    for m in _URL.finditer(body):
        if _in_fence(m.start(), fences):
            continue
        url = m.group(0).rstrip(_URL_TRAILING)
        rest = m.group("rest").rstrip(_URL_TRAILING)
        authority = rest.split("/", 1)[0]
        line = _line_of(body, m.start())

        userinfo = None
        if "@" in authority:
            userinfo, authority = authority.rsplit("@", 1)

        host = _authority_host(authority)

        if userinfo:
            out.append(
                Finding(
                    resolver="endpoint",
                    severity="reject",
                    evidence=f"{m.group('scheme')}://{userinfo.split(':')[0]}:***@{host}",
                    line=line,
                    detail="Credential embedded in the URL's user-info component.",
                    remediation="Parameterize the credential as an installer-supplied input. If "
                    "this is a real credential rather than a placeholder, rotating it is your "
                    "call — we cannot see what it has access to.",
                )
            )

        cq = _CRED_IN_QUERY.search(url)
        if cq:
            out.append(
                Finding(
                    resolver="endpoint",
                    severity="reject",
                    evidence=url.replace(cq.group("v"), "***"),
                    line=line,
                    detail="Credential embedded in the query string.",
                    remediation="Parameterize the credential as an installer-supplied input. If "
                    "this is a real credential rather than a placeholder, rotating it is your "
                    "call — we cannot see what it has access to.",
                )
            )

        reason = _classify_host(host)
        if reason:
            out.append(
                Finding(
                    resolver="endpoint",
                    severity="block",
                    evidence=url,
                    line=line,
                    detail=f"Non-portable endpoint — {reason}. Unrunnable for every "
                    "installer. Determined from host SYNTAX; we never resolve or call it.",
                    remediation='Make the endpoint a declared input ("your own scoring '
                    'endpoint"), or remove the dependency.',
                )
            )
    return out


def _resolve_bare_credentials(body: str, fences) -> list[Finding]:
    """Credentials are scanned EVERYWHERE, fenced code blocks included.

    The fence exemption this used to carry read: "a fenced example key is illustrative; Stage S
    still reads the body." That was sound while a second pass existed. Stage S is retired, so the
    exemption became a hole in the only check standing in front of an unrecallable action — and a
    fenced block is precisely where a person pastes a config example with a live key in it.
    Verified before removal: bare key -> 1 reject, same key inside a fence -> 0 findings.

    It was never a tested behaviour. The conformance suite's single credential case is unfenced,
    so no fixture encoded the exemption, which is why it survived review.

    Fences stay exempt for the URL and localhost resolvers, where an illustrative example genuinely
    is illustrative: a fenced `http://localhost:8080` is not a dependency on localhost. The
    difference is the cost of being wrong, not the confidence of the match.
    """
    out: list[Finding] = []
    seen: set[int] = set()
    for m in _CRED_SHAPES.finditer(body):
        seen.add(m.start())
        tok = m.group(0)
        out.append(
            Finding(
                resolver="endpoint",
                severity="reject",
                evidence=f"{tok[:8]}…{tok[-2:]} ({len(tok)} chars)",  # never echo the secret
                line=_line_of(body, m.start()),
                detail="A live-looking credential is present in the skill body.",
                remediation="Remove it and declare it as an installer-supplied input. If this is a "
                            "real credential rather than a placeholder, rotating it is your call — "
                            "we cannot see what it has access to.",
            )
        )
    for m in _CRED_ASSIGNMENT.finditer(body):
        val = m.group("v")
        # A query parameter (`?api_key=…` / `&token=…`) is already reported as an embedded credential by the URL
        # resolver, so matching it here too produces TWO findings for ONE secret. Caught by an
        # existing conformance case that expects exactly one — the value of a suite that asserts
        # counts rather than presence. Not a coverage loss: the secret is still rejected, once.
        if m.start() and body[m.start() - 1] in "?&":
            continue
        if _CRED_SENTINELS.match(val) or m.start("v") in seen:
            continue
        out.append(
            Finding(
                resolver="endpoint",
                severity="reject",
                evidence=f"{m.group(0).split(chr(61))[0].split(chr(58))[0].strip()} = "
                         f"{val[:3]}… ({len(val)} chars)",  # the KEY name, never the value
                line=_line_of(body, m.start()),
                detail="A credential-shaped assignment is present in the skill body.",
                remediation="Remove the value and declare it as an installer-supplied input. If it "
                            "is a real credential rather than a placeholder, rotating it is your "
                            "call — we cannot see what it has access to.",
            )
        )
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────
# R4 — stale Clay action / routine key  →  REMAP, never block
# ─────────────────────────────────────────────────────────────────────────────────────────

_ACTION_KEY = re.compile(r"\b(?P<k>[a-z][a-z0-9]*(?:-[a-z0-9]+){2,})\b")


def _resolve_stale_actions(body: str, fences, catalog: dict[str, str] | None) -> list[Finding]:
    """`catalog` maps a known-stale key → its current key. Absent catalog → no findings.

    Deliberately conservative: only keys the catalog explicitly knows are stale produce a
    finding. Guessing that an unrecognized hyphenated token is a Clay action would flood the
    output on ordinary prose.
    """
    if not catalog:
        return []
    out: list[Finding] = []
    seen: set[tuple[str, int]] = set()
    for m in _ACTION_KEY.finditer(body):
        key = m.group("k")
        if key not in catalog:
            continue
        line = _line_of(body, m.start())
        if (key, line) in seen:
            continue
        seen.add((key, line))
        out.append(
            Finding(
                resolver="stale_action",
                severity="remap",
                evidence=key,
                line=line,
                detail="References a Clay action/routine key that has since moved. Our surface "
                "drifted, not your skill — so we remap rather than block.",
                remediation=f"Use `{catalog[key]}`.",
                suggested=catalog[key],
            )
        )
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────────────────


def check_portability(
    skill_md: str,
    package_files: Iterable[str] = (),
    action_catalog: dict[str, str] | None = None,
) -> Result:
    """Run every resolver over a submitted skill body.

    Args:
        skill_md: the submitted body, decoded, exactly as stored.
        package_files: paths present in the package. A single-file submission passes
            ("SKILL.md",) — which is precisely why the canary must block.
        action_catalog: stale-key → current-key map. None disables R4.

    Never performs network I/O. Never raises on malformed input: an exception here would
    fail OPEN, which is how the one real escape got accepted with `intake_findings: []`.
    """
    if skill_md is None:
        skill_md = ""
    try:
        fences = _fenced_spans(skill_md)
    except Exception:
        fences = []
    findings: list[Finding] = []

    # FAIL CLOSED. That escape's signature was `intake_findings: []` with `finding_count: 0` — the
    # shape of a swallowed exception, which ACCEPTS the submission. So an internal error in
    # any resolver becomes a BLOCKING finding, never silence. A validator that cannot
    # complete has not cleared anything.
    resolvers = (
        ("missing_file", lambda: _resolve_missing_files(skill_md, package_files, fences)),
        ("workspace_handle", lambda: _structured_handles(skill_md, fences)),
        ("unfilled_marker", lambda: _resolve_unfilled_markers(skill_md, fences)),
        ("what_good_looks_like", lambda: _resolve_what_good_looks_like(skill_md)),
        ("what_this_skill_touches", lambda: _resolve_what_this_skill_touches(skill_md)),
        ("optional_marker", lambda: _resolve_optional_markers(skill_md, fences)),
        ("retired_frontmatter", lambda: _resolve_retired_frontmatter(skill_md)),
        ("workspace_handle", lambda: _resolve_prose_handles(skill_md, fences)),
        ("endpoint", lambda: _resolve_endpoints(skill_md, fences)),
        ("endpoint", lambda: _resolve_bare_credentials(skill_md, fences)),
        ("stale_action", lambda: _resolve_stale_actions(skill_md, fences, action_catalog)),
    )
    system: list[SystemFailure] = []
    if attribution()["fixture_suite_hash"].endswith("UNAVAILABLE"):
        system.append(
            SystemFailure(
                code="fixture_suite_unavailable",
                component="portability",
                detail="The conformance fixture suite could not be read, so this build cannot "
                "be attributed to a verified contract. Intake must stop with a retriable "
                "system disposition and create no rows.",
            )
        )
    for name, run in resolvers:
        try:
            findings += run()
        except Exception as exc:
            system.append(
                SystemFailure(
                    code="resolver_exception",
                    component=f"portability.{name}",
                    detail=f"The {name} resolver raised {type(exc).__name__}, so this submission "
                    "has NOT been cleared. Fails closed — but as OUR failure, not a "
                    "creator finding.",
                )
            )
    order = {s: i for i, s in enumerate(SEVERITIES)}
    findings.sort(key=lambda f: (order.get(f.severity, 9), f.line, f.resolver))
    return Result(findings=findings, system_failures=system)


def _structured_handles(body: str, fences) -> list[Finding]:
    """One finding per handle. Patterns overlap by design (a Clay table URL also contains a
    `t_...` id), and reporting the same handle twice would double-count the blocking total —
    which the conformance suite checks exactly, because over-blocking is also a defect."""
    out: list[Finding] = []
    claimed: list[tuple[int, int]] = []
    for rx, label in _STRUCTURED_HANDLE:
        for m in rx.finditer(body):
            if _in_fence(m.start(), fences):
                continue
            if any(m.start() < b and a < m.end() for a, b in claimed):
                continue
            claimed.append((m.start(), m.end()))
            out.append(
                Finding(
                    resolver="workspace_handle",
                    severity="block",
                    evidence=m.group(0).strip(),
                    line=_line_of(body, m.start()),
                    detail=f"Names a workspace-scoped {label}. The handle exists only in your "
                    "own workspace, so the skill is unrunnable for every installer "
                    "and unevaluable by us.",
                    remediation="Replace with a declared input the installer supplies, or a "
                    "portable action reference.",
                )
            )
    return out
