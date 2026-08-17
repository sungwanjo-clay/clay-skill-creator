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
threshold is 50; nothing in the table says why 50, what the column was for, or when it should
be ignored. So a converter that reads a table and emits a skill produces something fluent,
plausible and unfounded — and it reads *better* than a real one, because nothing in it hedges.

Two consequences shape this whole flow:

1. **The interview is not optional and never gets skipped, table or no table.** A table changes
   how the interview *opens* — your own prompts read back to you, your own thresholds quoted —
   never whether it happens.
2. **If no real insight comes out of the conversation, say so and stop.** A skill whose central
   claim was generated to fill a gap is worse than no skill, because somebody downstream will
   act on it. `references/examples/low-yield-fallback/SKILL.example.md` is what that outcome looks
   like written honestly.

## Step 0 — Say which skill you are, then set Clay up

**Print this as your very first line of output, before running anything:**

```
clay-skill-author/1.1.0 · loaded from <absolute path to this SKILL.md>
```

It costs one line and settles two questions that otherwise take a whole run to answer: whether this
skill ran at all or a generic `skill-creator` took the request, and whether the copy that ran is
current or a stale install. Do not skip it and do not paraphrase it.

Then set Clay up.

```
clay whoami          # exit 0 with a user id? go to Step 1
```

**If the plugin is already installed and you are only signed out**, its bundled `setup` skill does
PATH and sign-in in one step. Check before calling it, because the skill only exists once the plugin
does:

```
find ~/.codex ~/.cursor ~/.claude ~/.config -type f \
  \( -path '*/clay/skills/setup/SKILL.md' -o -path '*/clay/*/skills/setup/SKILL.md' \) 2>/dev/null | sort | tail -n1
```

Something printed → run `clay:setup` by name, or follow the `SKILL.md` that just printed.

**Nothing printed → no plugin yet. Install it inline.** These are stable strings, so they are here
rather than behind a fetch that can fail:

```
Claude Code    /plugin marketplace add clay-run/agent-plugins
               /plugin install clay@clay-plugins

Codex CLI      codex plugin marketplace add clay-run/agent-plugins
               then open Plugins and install clay

Cursor         do NOT hand-copy into ~/.cursor/plugins/local/ — org policy can block
               sideloading silently. Use Clay's setup skill instead.
```

Then:

```
clay login           # opens a browser once
clay whoami          # must return a user id
```

**If any of that fails, Clay's own procedure is authoritative** and carries the parts that do move —
the Claude Code version pin, the Cursor org-policy path, the `PATH` forwarder, troubleshooting:

```
curl -fsSL https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md
```

If that fetch also returns nothing, the sandbox has no outbound network, so the CLI cannot download
its own binary and **the table path is unavailable here.** Say so plainly and go to Step 3, which
needs none of it.

One sign-in covers both surfaces — the `clay` command and the Clay MCP server read the same session.
Some hosts need a restart before a freshly installed plugin registers.

**Do not continue until `clay whoami` returns a user id.** Then say which workspace the creator is
in, out loud, before reading anything.

## Step 0a — Say what is about to happen, before doing any of it

After the announce line and before any command, tell them the shape of the next few minutes. It went
straight into execution once and read as an interrogation.

Three sentences, no more:

> "I'll get Clay set up if it isn't already, then read your table's configuration — settings only, no
> rows and no runs. Then I'll ask you about two or three things the table can't tell me, write the
> `SKILL.md`, and validate it. Usually five minutes and under five questions."

Then continue. Do not wait for permission to proceed — this is orientation, not a gate.

## Step 1 — Preflight, before spending their time

Table reads go through Clay's public observability API, which the CLI's help states is enabled
per workspace and available on Enterprise plans. Settle it in one free, scoped call:

```
clay tables list --limit 1 --filter owner.id=<id from clay whoami>; echo "exit=$?"
```

Exit `0` → the table path is open. Exit `3` (`auth_forbidden`) → **it is closed to this
workspace; go to Step 3 and never mention the table path again.** Exit `5` → network, retry.

Say which happened. A creator who installed a CLI for a path they cannot use should hear it
from you at the start, not discover it at the last command.

## Step 2 — One question decides the route

> **Do you have a Clay table that already does this?**

That is the whole branch, and it needs no knowledge of what a `SKILL.md` is.

| Answer | Route |
|---|---|
| **Yes**, and preflight passed | Step 2a, then Step 3 |
| **No**, or preflight returned 3 | Step 3 |
| *"I already have a `SKILL.md`"* | Step 4 |

### Step 2a — Read the table's configuration

**RULE 0 — always pass the owner filter, and pass it on the first call.** An unscoped
`clay tables list` is workspace-wide (*"With no `--filter`, every table is listed"*), and table
*names* routinely encode customers, deals and colleagues. **Reading is the irreversible part,
not filtering:** once that list is in front of you those names have been read, and narrowing
afterwards does not unsee them.

**RULE 0b — these four commands and no others.**

```
clay whoami
clay tables list --filter owner.id=<me>
clay tables columns list <tableId>
clay tables columns get  <tableId>
```

`clay tables rows` is the creator's data and is never needed — output shape is derivable from
configuration alone. `clay tables update` is a **write** despite reading like a settings change.

Read in this order, because the order decides what you recover:

| Read | Evidence of | Not evidence of |
|---|---|---|
| **prompts** first | *intent* — why a column exists, in their words | mechanics; a prompt can state a goal it never achieves |
| **formulas** second | *mechanics* — thresholds, comparators, dependencies | intent; a formula cannot say why 50 |
| column **names** last | nothing on their own | anything at all |

**Never infer a step, a threshold or a purpose from a column name.** Names are free text with
no contract. Full procedure in `references/table-to-skill.md`.

### If the configuration contains a credential

Reading it is unavoidable — it lives in the column config, and you had to read the config. What
happens next is a choice, and all four of these are rules:

- **Never print any part of it.** Not the first bytes, not the last, not an ellipsis in between. A
  truncated token in a transcript is still a disclosure, and the transcript may be pasted anywhere.
- **One sentence, inline, in the normal flow.** No warning banner, no incident framing. This is a
  portability fact, not an emergency, and escalating it derails a creative task.
- **Never instruct them to rotate it.** You cannot see what that key touches or what rotating it
  breaks. State that it passed through an agent and that the decision is theirs.
- **No unsolicited debugging of their table.** A malformed header or a column that looks broken is
  off-task. You were asked for a skill.

What you owe them is the portability consequence, because that is why it matters at all:

> "These HTTP columns carry an auth token and two collection IDs. In the skill those become declared
> inputs the installer supplies, never literals. Separately, it did pass through an agent just now,
> so whether to rotate it is your call."

## Step 3 — The interview: ONE question per message, five maximum

**Say the plan before you ask anything.** Two or three sentences: what you are about to do, roughly
how many questions, and what they walk away with. A creative task that opens with execution feels
like an interrogation.

> "I've read the configuration and I can already see most of the mechanics. I'll ask you about three
> things the table can't tell me — the thing you know that it doesn't, one or two numbers that
> actually change the output, and which skills this shouldn't be confused with. Then I'll write the
> `SKILL.md` and validate it. Say 'draft it' at any point and I'll write it with what I have and mark
> the rest as gaps."

**Then derive, propose, and ask only what is left.** The six items below are what the finished skill
must ANSWER. They are **not** a list of questions to ask. Anything the configuration already told you
is stated back as a proposal for confirmation, not raised as a question.

1. The job, in the creator's words · 2. the declared inputs · 3. the steps in dependency order ·
4. every threshold **and why that number** · 5. the honest edges — cost, refusals, missing data ·
6. the boundary, naming two or three neighbours by slug from `references/existing-skills.md`.

### The hard rules of this step

- **ONE question per message. Then stop and wait.** Never a numbered list of questions. A message
  containing two questions is a defect, not efficiency — the creator answers the easy one and the
  other is lost.
- **Five follow-ups maximum.** If you have not got what you need in five, you have enough to draft
  with gaps. Draft it.
- **Never ask what you can derive.** Propose it instead: *"the inputs look like Keyword, Templates
  URL, Video ID and Transcript — right?"* is one exchange. Asking them to list their inputs is a
  worse version of work you already did.
- **An unconfirmed detail becomes a `proof_gap`, never a question.** You do not need every number
  justified. You need the justified ones stated and the rest honestly marked.
- **"Draft it" ends the interview immediately**, at any point, and the unanswered items become gaps.

### Ask in this order, because it is the order of decreasing value

1. **The insight.** The one thing they know that the table does not record. This is the whole skill —
   ask for it first and plainly: *"what do you know about this that the table can't tell me?"*
2. **The one or two decisive thresholds.** Not every number — the ones where a different value
   changes the output. Frame each as a tradeoff in plain language, not as a request for a spec:
   *"titles cap at six words — is that a hard editorial rule, or would eight be fine?"*
3. **The boundary, as a yes/no.** Propose the neighbours yourself: *"I'll say this is not for
   `scrape-any-website` or `company-research-brief` — sound right?"*

If a table was read, open from what it found — never restart. Quote their prompts back and quote each
threshold; that is what makes this feel like a conversation about their work rather than a form.

**Never supply an answer the creator did not give.** If the conversation produces no real insight,
say so plainly and stop — `references/examples/low-yield-fallback/SKILL.example.md` is what that
outcome looks like written honestly.

**If an answer is "I don't know, that was arbitrary," that is genuinely useful** — it becomes a
documented `proof_gap` instead of a fake rationale.

## Step 4 — Write it

Write `build/<slug>/SKILL.md` following `references/skill-contract.md`, plus
`build/<slug>/references/` only if the material warrants it. Set `proof_status` to match how the
logic was actually obtained: interview-derived logic carries a gap naming the interview, because
it has no ground truth anywhere; table-derived thresholds were compared against real formulas and
say so.

Read `references/examples/` first — three real shipped skills chosen for the quality of their
reasoning, plus the honest low-yield outcome. Each one's body is `SKILL.example.md`, named that
way only so this skill can be uploaded (the door permits exactly one file called `SKILL.md`);
what you write is a real `SKILL.md`. `account-tier-scoring` is one file and is one of the best;
long is not the bar.

## Step 5 — Validate, then package

```
python3 scripts/package_skill.py validate build/<slug>
```

Exit `0` means shape and content pass. `block` findings must be fixed; `report` findings are
heuristics worth a look. Single-file skill → done. Supporting files → package, because the form
takes one file:

```
python3 scripts/package_skill.py zip    build/<slug> <slug>.zip
python3 scripts/package_skill.py verify <slug>.zip --manifest manifest.json
```

Two builds of the same content always produce the same **manifest**; archive bytes depend on the
local zip library, so **compare manifests, not archives.** Details in
`references/validation.md` and `references/package-layout.md`.

## Step 6 — Hand it back

**Never submit on the creator's behalf.** There is no submission API and this skill does not have
one. Tell them to read the `SKILL.md` end to end — they are the last reviewer and the only person
who knows what the table was for — then upload or paste it into the Marketplace form themselves.
`references/submitting.md` covers what to expect, including that submitting is not publishing.

## Rules

- **NEVER** read a table row, run a column, write to a table, or execute a Clay action.
- **NEVER** run `clay tables list` without `--filter owner.id=`.
- **NEVER** infer a step, threshold or purpose from a column name.
- **NEVER** state an insight the creator did not say. If the conversation produced none, say so
  and stop — a generated insight reads better than a real one and is worth less than nothing.
- **NEVER** claim a threshold was verified when it came from the interview. `proof_status` and
  `proof_gaps` are how a reader knows what was checked; an empty gap list on interview logic is
  a false claim.
- **NEVER** submit, and never imply the skill was accepted.
- **ALWAYS** state which workspace, and what the preflight returned.
- **ALWAYS** draft once you have the insight, or once five follow-ups are spent, whichever comes
  first. "Finish the interview before drafting" was the earlier wording and it deadlocked a real
  run: six questions asked at once, nothing answered, nothing written. Unanswered items are gaps,
  not blockers — the only thing that must never happen is inventing an answer.

## What good looks like

The creator recognises the central claim as *theirs*, the thresholds trace to something they
said or to a formula that was actually read, `proof_gaps` name what nobody checked, and the
description names two or three neighbours by slug. The common failure is a skill that is fluent
everywhere and grounded nowhere — and it passes validation, because validation checks form.

## Worked example

Creator has a table scoring inbound leads. Preflight exits `0`. Reading prompts first recovers
*"is this person a decision maker at a company we'd actually sell to"*; formulas then give
`employee_count >= 50` and a three-band ladder; two columns are referenced by nothing. The
interview asks why 50 — *"below that they buy on a credit card and churn"* — which is the
insight, and is nowhere in the table. Played back, the orphan columns turn out to be one
abandoned experiment and one optional CRM field. The skill states the 50 threshold with the
churn reason, carries `proof_status: partial` with a gap saying the comparison ran locally at
generation time and cannot be replayed downstream, and names `buyer-classification` and
`account-tier-scoring` as neighbours. Validation exits `0`. The creator uploads it.
