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

> **Four ways in — which fits?**
> — **From a Clay table** you have already built
> — **From scratch**, no table
> — **I already have a `SKILL.md`** and want it checked and submitted
> — **Not sure** — show me my tables and which are worth converting

| Answer | Route |
|---|---|
| **From a table** | Step 3 |
| **From scratch** | `references/interview-to-skill.md` — no table, no preflight, nothing here applies |
| **I already have a `SKILL.md`** | Step 8 |
| **Not sure — show me** | preflight, list their tables, flag which have formulas **and** prompts, re-ask |

**ASK ALL FOUR OUT LOUD.** The heading has said "four answers" since this step was written, and the
question offered three — the missing one was `Not sure`, which the paragraph below calls the most
common real state. So the route existed, was reachable only by a creator who volunteered a state
nobody had offered them, and the flow's own note explained why that was the wrong one to hide. An
option that exists in the routing table and not in the question is an option nobody picks.

`I already have a SKILL.md` also used to be offered as "upload a skill you already have". Nothing is
uploaded on that route — it goes to Step 8, which validates and packages. Naming the action wrong
sends a creator looking for a file dialog that does not exist and hides the check that does.

The fourth answer is the most common real state and must not be a dead end. Flagging is free: a table
with neither formulas nor prompts is knowably thin before the creator invests anything.

**And it has to survive `auth_forbidden`.** `Not sure — show me` promises a table listing, which the
preflight below can refuse with exit `3` on a workspace without API table sync. When that happens,
say the listing is unavailable on this workspace and move to the interview — never leave a creator
who asked to be shown their tables looking at a failure they did not cause and cannot fix.

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

Write a **complete** `SKILL.md` to `build/<slug>/` — not an outline, not a plan. It must carry a
**`## Declared inputs` section**: a three-column table of every value the installer supplies — the
input, what they supply, and what happens if it is missing. That section is what makes the skill
portable, and it is the only body section a submission is required to have. All four worked examples
model it.

**Any step that spends money must name what runs.** *"Enrich the author to get an email"* is a
sentence about intent that every reader resolves differently — a different function, different inputs, a
different bill. Four things per paid step: **what runs** (the function, by name), **what goes in** (which
fields, from which declared input), **what to verify in the response** (a run can complete and return
nothing), and **what it costs**. Discover them while drafting — `clay routines list`, then
`clay routines get <id>` for the cost the list call omits, and `clay workflows actions schema` for the
real inputs — then write down what you found. Never carry a catalogue of function names into a skill:
names and prices rot, the procedure does not. Full detail and the verified traps:
`references/determinism.md`.

**Two kinds of thing belong in it, and the second is the one that gets missed.** Technical handles —
table ids, column ids, saved views, auth accounts — have a shape, so the validator catches them.
**Business context does not**: the CRM, the ICP, the weights, the tier cut-offs, what counts as
senior. A hardcoded `1000` is indistinguishable from a considered `1000`, so nothing downstream can
catch it and it has to be caught here.

### A named tool becomes an interview instruction, not a dependency and not a classification

When the source names a specific tool — a CRM, a sequencer, a warehouse, a scraper, an SEO provider —
do **not** preserve the vendor, and do **not** try to work out what category of thing it is. Both are
wrong for the same reason: the skill does not need to know, and neither do you.

Write the *asking* into the skill instead, so the published skill asks whoever installs it:

| The source says | The skill says |
|---|---|
| `read the HubSpot company record` | ask which CRM they run, and which object and fields hold the account record |
| `push to the Outreach sequence` | ask where sequences live for them, and what identifies the right one |
| `query the Snowflake table` | ask where their citation data lives and how to read a row from it |

Two things happen at once and both are required: the tool becomes a **declared input**, and the skill
carries the **instruction to elicit it at install time**. A declared input with nothing asking for it is
a form nobody fills in.

**The test for whether a vendor name survives — apply it per sentence, not per word:** *if the installer
does not have this vendor, does the sentence stop being true?*

- **In a boundary or a carve** — *"do NOT use for Salesforce hygiene"* — it stops being true, and
  wrongly excludes them. **Generalise it.**
- **As an illustrative value** — *"`uses Salesforce` is a technographic enrichment, not an ICP filter"* —
  still true, still teaches. **Keep it.**
- **In the trigger phrases of a description** — *"do they run Shopify or HubSpot"* — still true, and it
  is how the skill gets found at all. **Keep it, and removing it is a defect.**
- **Where the behaviour is genuinely that vendor's** — a quirk of one API — the sentence is *about* the
  vendor. **Keep it, and say in the declared inputs that the skill is vendor-specific.** Rare, and real.

This is the same rule the technical half already follows: a table id becomes a declared input rather
than a literal. A vendor is the business half of the same idea. Use the tool's output
rather than re-deriving by hand: `topo_steps` for dependency order (**never column order**),
`source_claims` for thresholds taken from `formulaText`, `yield_gate` for the thin-table decision.

**The boundary is derived here, not asked.** The bundled `existing-skills.md` is the neighbour map:
match on category, tags and keyword, take the two or three nearest, and write the `do NOT use` list
against them **job first, slug second in parentheses** — *"not for scoring a list you already have
(`account-tier-scoring`)"*. Those are library skills and most are not published yet, so a carve that
names only a slug points at something the reader cannot look up; the job is the half they can check. If nothing is near, that is itself the finding — say the space is uncontested and
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
3. **a gap** — named in a `## What this skill does not claim` body section, one plain sentence each.

There is no fourth category. Drafting before asking makes invention *easier*, so this is enforced
mechanically, not by good intentions: `compare_claims` fails in **both** directions — a threshold the
draft states but the table does not contain, and one the table contains but the draft dropped — and
`proof` raises rather than emitting a shippable-looking block. **A threshold that disagrees with its
formula is a build failure.**

**The gaps go in the BODY, under `## What this skill does not claim`, in plain sentences** — read by
the person deciding whether to trust the skill. Keep every gap; drop the field names and stage labels.

**THE FRONTMATTER IS EXACTLY THESE SIX FIELDS. Anything else is read by nothing.**

```yaml
---
name: your-skill-slug      # lowercase, hyphens, matches the directory name
description: |             # what it does; "Use whenever someone asks: …"; "Do NOT use it for …"
category: enrich           # one marketplace category
type: task                 # task (one job) | play (a multi-step motion)
tags: [csv, domain]        # input shapes and personas
keyword: your-skill-slug
---
```

Full field guidance is in `SKILL-TEMPLATE.md`. **This block is the whole list** — a seventh key is
not a richer skill, it is a field with no reader. `tools/portability.py` reports any it finds, names
it, and gives the line, so this is checked rather than remembered.

**And a gap declared in `SKILL.md` must not be contradicted by a supporting file.** Observed on a real
submission: the skill said *"no conversion rate is claimed anywhere"* while its own reference file said
one variant *"converts better"*. The main file is where the discipline gets applied and the supporting
files are where it leaks, so re-read every reference against the gap list before packaging.

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

**In plain language, not field names.** The creator has never seen the package contract and has no
reason to learn it. Every one of these reached a creator in a real run, because this step used to say
"show the `proof_gaps` in full":

| Never say | Say |
|---|---|
| `proof_gaps` | **What this skill does not claim** |
| `stage_p` · `stage_e` · `intake` | nothing — drop the label; the sentence must stand without it |
| "the 4 machine-comparable claims" | "the four numbers I could check against your formulas" |
| "not creator-confirmed" | "you didn't confirm this — I worked it out" |
| `proof_status: partial` | say what was and wasn't checked, in the list below |

**It must fit on one screen:**

- the title, and one line on what it produces;
- the steps as one-liners, in dependency order;
- **every number and where it came from** — *your formula* / *you told me* / *nobody established this*;
- **what this skill does not claim** — one plain sentence each, no labels. A gap that becomes
  unreadable once its stage label is removed was written badly: the label was carrying the meaning;
- **what the installer has to supply**, naming anything that was a credential or a workspace handle;
- **the boundary as one line in their language** (*"not for X, not for Y"*), so a wrong carve gets
  corrected by reading rather than by being interrogated.

Then **one** question: *"anything wrong?"* Not a checklist. If it does not fit on one screen it is too
long, and the confirm step has regrown into the wall this flow exists to remove.

**The file does NOT carry these as frontmatter — the submission door does not read them, and no
skill in the library has them. What the conversation never
does.**

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

Compare **manifests, not archives**. Then tell them to read it end to end — they are the last
reviewer. `references/submitting.md` covers what to expect.

### Submitting, if they want to

**Never submit without an explicit yes.** They can upload it themselves, or this can send it — and
sending is three steps in that order, never fewer:

```
python3 scripts/submit_skill.py preview <package> --profile '<their details as JSON>'
```

That prints exactly what would be sent — the package digest, the file inventory, their details, the
consent text — and sends nothing. **Show them that block, including the consent text, and ask.** Only
on a yes:

```
python3 scripts/submit_skill.py send <package> --profile '…' --endpoint <url> \
        --confirm <the token preview printed> --rights-confirmed
```

`send` refuses without the token from `preview`, and the token stops matching if the package changed
after they saw it — so *show, ask, send* is the only sequence that works.

**Never build the request yourself.** The package is base64 in the body: at the documented ceilings
that is ~1.9–2.7 million tokens for a zip and ~100 thousand for a `SKILL.md`, and a truncated encode
arrives as an apparently **corrupt archive** rather than as an obvious limit. The script reads from
disk. Same reason the retry secret comes from `secrets.token_hex(32)` inside it and not from you:
**anything needing exact bytes or real randomness comes from code, never from the model.**

The receipt holds a private retry secret. It is written beside the package at `0600` and its value is
never printed — report the path. And say plainly what happened: **submitted for review, not
published.** A person reviews it and verifies identity before anything is public.

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
- **NEVER** show the creator a field name, a stage label or a tool name — `proof_gaps`, `stage_p`,
  `stage_e`, `intake`, `derive_recipe.py`. Say what it means. They are reviewing their own workflow,
  not our package format.
- **NEVER** submit without an explicit yes, and never imply a skill was accepted or published.
- **NEVER** construct the submission request yourself, and never generate its retry secret.
- **NEVER** write a paid step without naming the function, its inputs, what to verify and its cost.
  "Enrich through Clay" is intent, not an instruction.
- **NEVER** carry a named tool through as a dependency, and never classify it into a category either.
  Convert it to a declared input **plus** an instruction telling the skill to ask for it at install
  time. A vendor name survives only where the sentence stops being true without it.
- **NEVER** state something as settled in a supporting file that the main file lists as unestablished.
- **ALWAYS** put the gaps in a `## What this skill does not claim` body section — never in retired
  frontmatter fields outside the six-key block above, which nothing downstream reads.
- **ALWAYS** write a `## Declared inputs` section covering both workspace handles and business
  context — thresholds, weights, verticals and tool choices are the installer's, never the author's.
- **ALWAYS** derive the full draft before asking anything.
- **ALWAYS** draft — with gaps if needed. Unanswered items are gaps, not blockers. The only thing that
  must never happen is inventing an answer.

## What good looks like

The creator reads the skeleton and says "yes, except one thing." Three questions or fewer were asked,
each naming a specific column, and the boundary was derived rather than handed back. Every threshold traces to a formula or sits in the does-not-claim section. The common
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
