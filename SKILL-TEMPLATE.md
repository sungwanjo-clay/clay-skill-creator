# SKILL.md — the contract

## Frontmatter

```yaml
---
name: your-skill-slug          # lowercase, hyphens, matches the directory name
description: |                 # no known cap; 1,187 chars is the longest verified intact
  What it does, in one dense paragraph. Then: "Use whenever someone asks: the actual
  phrases people use." Then: "Do NOT use it for a-neighbouring-skill, another-one."
category: enrich               # one of the marketplace categories
type: task                     # task (one job) | play (a multi-step motion)
tags: [csv, domain]            # input shapes and personas
keyword: your-skill-slug
proof_status: partial          # complete | partial | not_exercised
proof_gaps:                    # required and non-empty unless proof_status is complete
  - stage: stage_e
    reason: A plain sentence saying what was not verified.
---
```

**There is no length limit we can point you at.** `python3 tools/package_skill.py validate` measures
your description the way the form does — a block scalar counts as its lines joined by spaces, not as
raw bytes — and *reports* anything past **1,187 characters**, which is simply the longest description
we have verified is stored intact, byte for byte, through submission. Past that we have no evidence
either way, so treat the report as a heads-up and not a rule. If you do want to trim, cut restatements
and mechanism detail, which belongs in the body; the trigger phrases and the "do NOT use it for" list
are the parts that earn their length, because they decide whether your skill is chosen at all.

An earlier version of this file said 1024 was a hard cap enforced at the door. That was true for a
while and is not true now, and the correction is here rather than silently swapped because a number
you wrote a description around is worth knowing the status of.

**Avoid angle brackets in the description.** We cannot show you a check that rejects them, so this is
convention rather than a constraint — but a description written as `<placeholder>` reads as an
unfinished template, and prose beats slots for the one field a router reads. Write "for a given
intent", not "for `<intent>`".

**The description is the trigger.** It is what decides whether your skill is chosen, so write the
phrases people actually type, and name the skills yours should *not* be confused with. A vague
description is the most common reason a good skill never gets used.

**`proof_gaps` entries need both a stage and a reason.** A gap that says only "incomplete" tells a
reader something was not proven but not what to do about it.

The two field names above are the only jargon in this file, and they are read by machines rather than
by people: `proof_gaps` is *what this skill does not claim*, and `stage` says at which point the
checking stopped — `intake` at submission, `stage_p` when the package was inspected, `stage_e` when it
was actually run. **Write the `reason` so it reads correctly with the stage removed**, because that is
how a person will read it.

## Body

No section list is required. What follows is the shape the strongest skills in the library
converge on — read off them rather than designed in advance, and the three in
[`examples/`](examples/) all follow it. Take it as a checklist of things worth having, not a form
to fill in.

```
# Title (a parenthetical stating the move: "declare the measurement, then count")

The insight: <one bold claim>, then the evidence for it, then what follows from it.

## Step 0 — Check the platform works, and say where the work runs
## Step 1 — Collect the definition (interview; do not guess)
## Step 2 — <the decision this skill exists to make>
## Step 3 — Free checks before anything paid
## Step 4 — State the cost, get approval
## Step 5 — Do the work
## Step 6 — Grade / verdict, single-valued
## Step 7 — Deliver
## What good looks like
## Rules
## Worked example
```

**The insight, with its evidence.** One claim, stated in bold, followed by *why you believe it*.
This is the single biggest quality difference in the library. "Job counts can be unreliable" is
not an insight — nothing can be built on it. "There is no such thing as the number of jobs open at
a company, and here are four providers returning 8,945 / 737 / 384 / 332 for one company on one
day" is, because every later step is forced by it. If you cannot state a claim and say what made
you believe it, the skill is probably one enrichment call and does not need to be a skill.

**Put the insight in the title too.** A parenthetical — *(declare the measurement, then count)*,
*(claims vs independently re-derived evidence)*, *(enumerate, then prove coverage)* — so a reader
scanning headings gets the move before the prose.

**Step 0: check the platform, and state where the work runs.** Every good skill starts by
confirming the tooling is alive and telling the user which workspace they are in. The best ones
also state *where computation happens*, because that is what it costs: arithmetic in the agent is
free, the same arithmetic in a per-row column bills per row. Cost is a design property, not a
footnote.

**Interview steps that say "do not guess."** Where a step needs the user's definition — their ICP,
their thresholds, which fields they rely on — say so, and say that the skill stops rather than
inventing one. Skills that quietly supply a default for a decision the user was supposed to make
are the ones that produce confident wrong answers.

**Free before paid, and the gate is a step of its own.** Order the work so everything free runs
first and can eliminate rows before anything bills. Give it a numbered step so it cannot be
skipped, and name what it saves.

**A cost step with an explicit approval.** State the estimate in both currencies where they differ
(credits and per-row charges), and wait. Anything that spends the user's money should have asked.

**Verdicts from a fixed set, resolved in a stated order.** Enumerate the values — *"five values, no
sixth"* — and rank the rules so the first match wins. "Score highly" is not runnable. Neither are
two bands that both match. Add a value for *"could not measure this"*: abstention is a real answer
and a skill without one will fabricate rather than admit a gap.

**Deliver, and say what was and was not covered.** Sample sizes, skipped rows, unmeasured accounts.
The output should let a reader see the shape of what is missing.

**What good looks like / Rules / Worked example.** The common failure mode, the MUSTs and NEVERs so
the boundaries survive being skimmed, and one example with real values carried end to end.

**Push mechanics out to `references/`.** Field paths, provider rosters, per-arm quirks, schemas.
Keep the body about *decisions*; a body that is mostly field names is a reference file with the
wrong name. If nothing warrants a reference file, do not create one — `account-tier-scoring` is one
file and is one of the best skills we have.

## Hard requirements

- Exactly one `SKILL.md` at the package root.
- Every relative reference resolves to a file inside the package.
- No workspace identifiers: table ids, column ids, workspace ids, saved-view names, auth handles.
- No credentials, no private hostnames.
- Everything the installer must supply is a **declared input**, named in the body.

See [`PACKAGE-LAYOUT.md`](PACKAGE-LAYOUT.md) for layout and [`VALIDATION.md`](VALIDATION.md) to
check all of the above locally.
