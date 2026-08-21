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

**Say what the skill does not claim, in the body.** A `## What this skill does not claim` section, one
plain sentence per gap, is how a reader decides whether to trust it. There is no frontmatter field for
this: `proof_status` and `proof_gaps` are retired, nothing downstream reads them, and a machine field
with no machine is worse than prose because it looks authoritative.

Write each sentence so it stands alone. *"Never run end to end, so no measured cost or latency"* survives
being read cold; *"stage_e — the machine-comparable claims are markup artifacts"* does not, because a
label was carrying the meaning.

**And check your supporting files against it.** A real submission declared that no conversion rate was
claimed anywhere, while one of its own reference files stated that a variant converts better. The main
file is where the discipline gets applied; the references are where it leaks.

## Body

No section list is required. What follows is the shape the strongest skills in the library
converge on — read off them rather than designed in advance, and the three in
[`examples/`](examples/) all follow it. Take it as a checklist of things worth having, not a form
to fill in.

```
# Title (a parenthetical stating the move: "declare the measurement, then count")

The insight: <one bold claim>, then the evidence for it, then what follows from it.

## Declared inputs          <- REQUIRED. See below.
## Step 0 — Check the platform works, and say where the work runs
## Step 1 — Collect the definition (interview; do not guess)
## Step 2 — <the decision this skill exists to make>
## Step 3 — Free checks before anything paid
## Step 4 — State the cost, get approval
## Step 5 — Do the work
## Step 6 — Grade / verdict, single-valued
## Step 7 — Deliver
## What this skill does not claim   <- the gaps, in plain sentences
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

## Declared inputs — the one section that is required

**A skill that only works in the author's workspace is not a skill, it is a note to yourself.** This
section is what makes the difference, and it is the only body section a submission must have.

**It is checked by a person, not by a tool.** No validator can tell a considered threshold from a
hardcoded one, so this is read at review rather than enforced at submission — which means a skill
without it is not rejected by a machine, it is sent back by a human. Writing it well is the cheapest
way to make that review fast.

Every value the installer supplies gets a row. Three columns, because each answers a different
question:

```
## Declared inputs

**Nothing here ships with a value.** Each one is the installer's, not the author's: ask for it,
never substitute a plausible default, and if an answer does not exist say which step becomes
unavailable rather than guessing. Where a default IS defensible it is named below, and using it
means saying so in the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **The book** | CSV, table or Audience of accounts, minimum one domain column | no default — there is nothing to score |
| **Size thresholds** | the headcount cut between segments | the author used 1,000 and 50; ask, and if they have no view use them and SAY they are borrowed |
| **Window** | N days | 30 days is defensible and must be stated; never leave it unset, which silently means all time |
```

**Two kinds of thing belong here, and the second is the one people miss.**

| | Example | Why it is the installer's |
|---|---|---|
| **Technical handles** | table ids, column ids, saved-view names, auth accounts, API tokens | they exist only in your workspace and resolve to nothing in anyone else's |
| **Business context** | the CRM, the ICP, weights, tier cut-offs, verticals, what "senior" means | they are the installer's judgment about their own market, and an author's numbers are borrowed at best |

The technical half the validator can catch, because a workspace id has a shape. **The business half
it cannot** — a hardcoded `1000` is indistinguishable from a considered `1000`. So this is the part
that depends on you, and it is the difference between a skill someone can run and a description of
how *you* run yours.

**Name the job, not the vendor — and write the asking into the skill.** Two things, not one: the
tool becomes a declared input, *and* the skill carries the instruction to elicit it at install time. A
declared input with nothing asking for it is a form nobody fills in.

| Instead of | Write |
|---|---|
| read the HubSpot company record | ask which CRM they run, and which object and fields hold the account record |
| push to the Outreach sequence | ask where sequences live for them, and what identifies the right one |
| query the Snowflake table | ask where the data lives and how to read one row from it |

**The test, applied per sentence rather than per word: if the installer does not have this vendor, does
the sentence stop being true?**

- A **boundary** — "do NOT use for Salesforce hygiene" — stops being true and wrongly excludes them.
  Generalise it.
- An **illustrative value** — "`uses Salesforce` is a technographic enrichment, not an ICP filter" —
  stays true and still teaches. Keep it.
- A **trigger phrase** — "do they run Shopify or HubSpot" — stays true, and it is how anyone finds your
  skill. Keep it; removing it is a defect, not a cleanup.
- A **genuine vendor dependency** — a quirk of one API — is *about* that vendor. Keep it, and say in the
  declared inputs that the skill is vendor-specific. Rare, and real.

Do not try to classify the tool into a category first. The skill does not need to know what kind of
thing it is; it needs to ask.

**The third column is not decoration.** "If it is missing" forces you to state what degrades rather
than marking everything mandatory, and it is the same discipline as saying what a skill does not
claim: a reader can then decide whether they have enough to start.

## Hard requirements

- Exactly one `SKILL.md` at the package root.
- Every relative reference resolves to a file inside the package.
- No workspace identifiers: table ids, column ids, workspace ids, saved-view names, auth handles.
- No credentials, no private hostnames.
- Everything the installer must supply is a **declared input**, named in the body.

## The numbering is a contract, so say so in the body

**A numbered step does not begin until every step before it has its inputs.** That looks self-evident
on the page and turns out not to be. Watched on a real run of a shipped skill: the agent wrote a
204-line implementation of Step 2 before asking Step 1 for the file it was meant to process — and one
of the uncollected inputs decided that code's central policy. It looked finished and was built against
a guess.

So write the rule down rather than trusting the numerals:

> Do not start a step before the steps above it have their answers. If a declared input is missing,
> ask for it — never assume a default and continue.

One line, and it is the difference between a skill that stops and one that produces confident output
from inputs nobody supplied.

See [`PACKAGE-LAYOUT.md`](package-layout.md) for layout, [`DETERMINISM.md`](determinism.md) for what
any step that spends money has to name, and [`VALIDATION.md`](validation.md) to check all of the above
locally.
