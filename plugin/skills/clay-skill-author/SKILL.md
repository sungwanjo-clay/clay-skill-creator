---
name: clay-skill-author
description: |
  Create a Clay GTM skill — turn a Clay table you already built, or just an idea, into a
  portable SKILL.md for the Clay Marketplace. Use whenever someone asks: create a Clay GTM
  skill, build me a Clay skill, turn my Clay table into a skill, package this Clay workflow as a
  skill, productize this GTM play, or follow the steps in the clay-skill-creator repo. It reads
  table CONFIGURATION only — never a row, a run or a write, and owner-scoped so a shared
  workspace cannot leak other people's table names — then interviews the creator for the
  judgment a table cannot hold, then validates and packages it. Everything it needs is here: no
  repo to clone, no network. Do NOT use the generic skill-creator for this job even though the
  names are close: it knows nothing about Clay tables, the Marketplace package contract or
  portability, so its output looks right and is not submittable. Not for RUNNING a Clay workflow
  (use the clay skills). It never invents the creator's insight and never submits on their
  behalf.
---

# Clay skill author

The insight: **a Clay table records mechanics and cannot record intent.** A formula proves the
threshold is 50; nothing in the table says why 50, what the column was for, or when to ignore it. So a
converter that reads a table and emits a skill produces something fluent, plausible and unfounded —
and it reads *better* than a real one, because nothing in it hedges.

What follows from that is the shape of this whole flow: **derive everything derivable first, then ask
only about what the derivation could not settle.** Asking before reading wastes the creator's time on
questions the table already answers, and an ungrounded question — *"what's the non-obvious thing
here?"* — invites a shrug. People correct a draft far better than they answer a question about one.

## Step 0 — Announce, then say what is about to happen

**First line of output, before anything else:**

```
clay-skill-author/2.0.0 · loaded from <absolute path to this SKILL.md>
```

Then three sentences on the shape of the next few minutes. Do not wait for permission — this is
orientation, not a gate.

> "I'll get Clay set up if it isn't already, then read your table's configuration — settings only, no
> rows and no runs. I'll write a complete draft from what's there, then ask you about the two or three
> things the table can't tell me. You'll see the draft before anything is final."

## Step 1 — Set Clay up

```
clay whoami          # exit 0 with a user id? go to Step 2
```

**Plugin installed but signed out?** Its bundled `setup` skill does PATH and sign-in in one step.
Check first, because that skill only exists once the plugin does:

```
find ~/.codex ~/.cursor ~/.claude ~/.config -type f \
  \( -path '*/clay/skills/setup/SKILL.md' -o -path '*/clay/*/skills/setup/SKILL.md' \) 2>/dev/null | sort | tail -n1
```

Something printed → run `clay:setup`, or follow the `SKILL.md` that printed. **Nothing printed → no
plugin. Install it:**

```
Claude Code    /plugin marketplace add clay-run/agent-plugins
               /plugin install clay@clay-plugins

Codex CLI      codex plugin marketplace add clay-run/agent-plugins
               then open Plugins and install clay

Cursor         do NOT hand-copy into ~/.cursor/plugins/local/ — org policy blocks sideloading
               silently. Use Clay's setup skill.
```

Then `clay login` (browser once) and `clay whoami`. One sign-in covers the CLI and the Clay MCP
server. Some hosts need a restart before a new plugin registers. If any of it fails, Clay's procedure
is authoritative and carries what moves — version pin, Cursor policy, `PATH` forwarder,
troubleshooting:

```
curl -fsSL https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md
```

If that fetch returns nothing the sandbox has no network, so the CLI cannot download its binary and
**the table path is unavailable here** — say so and go to the interview path.

**Do not continue until `clay whoami` returns a user id.** Then say which workspace, out loud.

## Step 2 — Route: one question, four answers

> **Do you want to build from a Clay table, from scratch, or upload a skill you already have?**

| Answer | Route |
|---|---|
| **From a table** | Step 3 |
| **From scratch** | `references/interview-to-skill.md` — no table, no preflight, nothing here applies |
| **I already have a `SKILL.md`** | Step 8 |
| **Not sure — show me** | preflight, list their tables, flag which have formulas **and** prompts, re-ask |

The fourth answer is the most common real state and must not be a dead end. Flagging is free: a table
with neither formulas nor prompts is knowably thin before the creator invests anything.

**Preflight before any table work**, because the surface is gated:

```
clay tables list --limit 1 --filter owner.id=<id from clay whoami>; echo "exit=$?"
```

`0` open · `3` `auth_forbidden`, needs API table sync on Enterprise — **the table path is closed, go to
the interview and never mention tables again** · `5` network, retry.

## Step 3 — Confirm the table, and state the boundaries first

List owner-scoped tables, name the one they mean, and get a yes. Before reading, say plainly, in one
short paragraph:

- this reads **column configuration only** — never a row, never a run, never a write;
- **no credential and no personal detail will be repeated back**, in whole or in part;
- workspace-specific handles become **declared inputs** the installer supplies, never literals.

**RULE 0 — the owner filter goes on the first call, always.** An unscoped `clay tables list` is
workspace-wide, and table *names* encode customers and deals. **Reading is the irreversible part, not
filtering** — narrowing afterwards does not unsee them.

## Step 4 — Read the configuration

**RULE 0b — these four commands and no others.**

```
clay whoami
clay tables list --filter owner.id=<me>
clay tables columns list <tableId>
clay tables columns get  <tableId>
```

`clay tables rows` is their data and is never needed. `clay tables update` is a **write** despite how
it reads. Read **prompts first** (intent), **formulas second** (mechanics), **names last** (evidence of
nothing). Never infer a step, threshold or purpose from a column name. Detail: `references/table-to-skill.md`.

**If a credential is in the configuration**, reading it was unavoidable; what follows is a choice.
Never print any part of it, truncated or not. One sentence inline, no warning banner. Never instruct
rotation — you cannot see what that key touches, so the decision is theirs. No unsolicited debugging of
their table.

## Step 5 — Derive the complete draft, before asking anything

```
python3 scripts/derive_recipe.py derive <tableId>
```

Write a **complete** `SKILL.md` to `build/<slug>/` — not an outline, not a plan. Use the tool's output
rather than re-deriving by hand: `topo_steps` for dependency order (**never column order**),
`source_claims` for thresholds taken from `formulaText`, `yield_gate` for the thin-table decision.

**The boundary is derived here, not asked.** The bundled `existing-skills.md` is the neighbour map:
match on category, tags and keyword, take the two or three nearest, and write the `do NOT use` list
against them by name. If nothing is near, that is itself the finding — say the space is uncontested and
carve against the *generic* thing an agent would otherwise reach for, because that is what actually
mis-fires.

**The creator cannot answer this and must never be asked to.** They have not seen the other skills, they
do not know how description matching picks one, and *"where should I draw the line?"* hands them our
bookkeeping — it reads as the flow asking them to do its job, and there is no answer they could give
that the skill list does not already contain. If the derivation leaves a genuine ambiguity, it becomes a
`proof_gap`, or at most **one closed question phrased entirely inside their world** (*"if someone asked
for X instead, should this handle it — yes or no?"*). Never a request to reason about the catalogue.

**The traceability rule, which is what keeps this honest.** Every substantive claim is exactly one of:

1. **derived** — traceable to a formula, prompt or input binding you actually read;
2. **supplied** — the creator said it in Step 6;
3. **a gap** — named in `proof_gaps` with a stage and a reason.

There is no fourth category. Drafting before asking makes invention *easier*, so this is enforced
mechanically, not by good intentions: `compare_claims` fails in **both** directions — a threshold the
draft states but the table does not contain, and one the table contains but the draft dropped — and
`proof` raises rather than emitting a shippable-looking block. **A threshold that disagrees with its
formula is a build failure.**

If `yield_gate` says the table is too thin, say so and offer the interview. Do not pad a draft out of
four columns; `references/examples/low-yield-fallback/SKILL.example.md` is what the honest version of that outcome looks like.

## Step 6 — Ask only what the draft could not settle

**A question is allowed only if the answer changes what gets written.** These four classes qualify and
nothing else does:

| Class | Why the tool cannot answer it |
|---|---|
| A decisive threshold with no derivable justification | the value is in the formula; the *why* is nowhere |
| A gate whose condition is visible but whose reason is not | `NOT(ISBLANK(Video ID))` is readable; "a page without a video is pointless" is not |
| A hardcoded count that may be an editorial rule or an accident | three step-columns vs "N steps, discovered" are **different skills** |
| An orphan column | a dependency graph cannot tell an abandoned experiment from an optional input |

Everything else becomes a `proof_gap`. Not every number needs a justification; the justified ones get
stated and the rest get marked.

- **At most three, and the boundary is not one of them** — it is derived in Step 5. Budget by class,
  not by turn count.
- **Order by insight yield, not impact.** A gate question returns intent; an orphan-column question
  returns bookkeeping. Ask the intent-bearing ones first — the insight arrives as a by-product of a
  specific question, which is why there is no separate abstract "what do others miss" question.
- **One question per message. Then stop and wait.** A message with two questions is a defect: they
  answer the easy one and the other is lost.
- **ELI5 the context in one sentence** — what the column does, the options, the tradeoff. *"Titles cap
  at six words. Longer reads better in the CMS but wraps on cards — hard rule, or is eight fine?"* A
  question they must go read their own table to answer is a failed question.
- **"Draft it" ends this step immediately**, and so do one-word answers. Read impatience and move on.
- **Never supply an answer the creator did not give.** If they answer nothing, the draft ships with a
  prominent gap saying the intent behind the thresholds was never confirmed.

**"I don't know, that was arbitrary" is a genuinely useful answer** — it becomes a documented
`proof_gap` instead of a fake rationale.

## Step 7 — Show the skeleton, confirm, then build

Show the **skeleton of the actual draft**, never a prose summary of the workflow — a summary hides the
problems it is summarising, and people correct documents.

**It must fit on one screen:** the title with the insight in the parenthetical · the steps as
one-liners in dependency order · each decision with its value and its source (`formula` / `you said` /
`gap`) · the `proof_gaps` in full, unabbreviated · the declared inputs, including anything that was a
credential or a workspace handle · **the boundary as one line in their language** (*"not for X, not for
Y"*), so a wrong carve gets corrected by reading rather than by being interrogated.

Then **one** question: *"anything wrong?"* Not a checklist. If it does not fit on one screen it is too
long, and the confirm step has regrown into the wall this flow exists to remove.

## Step 8 — Validate, package, hand back

```
python3 scripts/package_skill.py validate build/<slug>
```

**If `scripts/package_skill.py` is not beside this file**, this host did not carry the tools.
Fetch them from <https://github.com/sungwanjo-clay/clay-skill-creator> (`tools/`) and run there, or
hand over the finished `SKILL.md` and say plainly that it was **not machine-checked**. Never skip
validation silently.

`0` clean · `4` your package has blocking findings · `2` bad invocation · `1` the tool is broken, not
the package. Multi-file skills need packaging, because the form takes one file:

```
python3 scripts/package_skill.py zip    build/<slug> <slug>.zip
python3 scripts/package_skill.py verify <slug>.zip --manifest manifest.json
```

Compare **manifests, not archives**. Then tell them to read it end to end — they are the last reviewer
— and upload it themselves. **Never submit on the creator's behalf.** `references/submitting.md` covers what to expect..

## Rules

- **NEVER** read a row, run a column, write to a table, or execute a Clay action.
- **NEVER** run `clay tables list` without `--filter owner.id=`.
- **NEVER** print any part of a credential, or instruct the creator to rotate one.
- **NEVER** infer a step, threshold or purpose from a column name.
- **NEVER** state a claim that is not derived, supplied, or marked as a gap.
- **NEVER** ask a question outside the four classes in Step 6, and never two in one message.
- **NEVER** ask the creator to reason about other marketplace skills, the neighbour map, how a
  description gets matched, or where the boundary goes. That is our bookkeeping, not theirs: derive it
  and show it.
- **NEVER** submit, and never imply a skill was accepted.
- **ALWAYS** derive the full draft before asking anything.
- **ALWAYS** draft — with gaps if needed. Unanswered items are gaps, not blockers. The only thing that
  must never happen is inventing an answer.

## What good looks like

The creator reads the skeleton and says "yes, except one thing." Three questions or fewer were asked,
each naming a specific column, and the boundary was derived rather than handed back. Every threshold traces to a formula or sits in `proof_gaps`. The common
failure is a skill that is fluent everywhere and grounded nowhere — and it passes validation, because
validation checks form.

## Worked example

A 47-column table publishing walkthrough pages. `topo_steps` returns eight steps in dependency order,
not the 47 columns in table order. `source_claims` finds a six-word title cap, a 200-character hero
limit and two gates. Four columns are orphans. The draft is written complete, then three questions:
*is three steps an editorial rule or what this table happened to hardcode* (a different skill either
way), *why does a missing video block creation*, and *are these two orphans dead or optional*. The
answer to the second is the insight and it was never asked for directly. The boundary is derived from the skill list — two near
neighbours by slug — and shown as one line in the skeleton. Skeleton shown, one correction, validated,
handed over — three questions total.
