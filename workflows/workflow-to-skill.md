# Workflow → skill

**Every number in this file was measured on 97 real workflows, 840 nodes, in one shared workspace on
2026-08-31.** Where it says most or rarely, there is a rate behind it.

A workflow tells you the MECHANISM and usually not the PURPOSE. **57% of workflows carry no agent
prompt anywhere**, and for those the config cannot say what the workflow is for — only what it does.
So reading a workflow replaces the derivation half of the interview and never the judgment half.

## 1. Find the workflow

```
clay whoami
clay workflows list --filter creator.id=<me>     NOT owner.id — see below
```

**The scope field is `creator.id`, not `owner.id`.** Tables use `owner.id` and workflows do not.
Copy the table rule here and you get an unscoped list of a shared workspace's workflows, whose names
encode customers and deals exactly as table names do.

Expect noise. In the measured workspace, of the first 200 workflows **92 were untitled** and 37 more
matched *test*, *scratch*, *copy of* or *demo*. **And a good name proves nothing**: 13 of 110 probed
had a sensible GTM name and zero nodes.

**BUT ONLY THE LIST IS SCOPED. THE READ IS NOT — and that is the common case, not the exception.**
`graph get` works on any workflow the account can see, whoever created it. So a creator who already
knows which workflow they mean **pastes its id or URL and skips the listing entirely**, and that is
the better path: it is faster, it needs no scope decision, and it cannot surface a colleague's
workflow they did not ask for.

Verified rather than assumed: all 97 workflows measured for this file were created by other people
and read cleanly from an account owning none of them.

**So ask for the workflow before offering to list.** A scoped list is the fallback for *"I know I
built one, show me"*, and in a real shared workspace it can legitimately return nothing at all — one
account in the measured workspace had **zero** of 2,403 under its own `creator.id`. An empty list is
not a failure and must not read as one.

**Widening the list is the creator's call, taken out loud.** The table route already sets this
precedent: where a workspace has several owners, owner confirmation is the first interview question,
before any read. Same here. If they want a teammate's workflow, ask for the id — never widen the
listing silently, because workflow names encode customers and deals exactly as table names do.

## 2. Read the graph

```
clay workflows graph get <id> --mode summary    shape, triggers, node types, edges
clay workflows graph get <id> --mode full       THE CONFIGURATION. Required.
```

**`clay workflows get` is not the config read.** It returns id, name, url, createdAt, creator, and
nothing else. Two things follow that cost a whole pass if you learn them late:

- **`--mode full` is mandatory, not an optimisation.** In summary mode `routingCriteria` was empty on
  **all 97** workflows while 45 carried conditional nodes. Branch logic is never on the edge.
- Size is about 3.5 kB per node, so a 31-node workflow is one 127 kB read. No pagination needed.

**Read-only allowlist, and it is an allowlist because this surface writes far more than tables do:**
`list`, `graph get`, `graph validate`, `nodes get`, `diagram`. **Never** `runs` (spends), **never
`nodes test`** (executes, and reads like a read), never `code`, never `graph format` (mutates
layout), never any `create` / `update` / `delete` / `publish` / `triggers` write form.

## 3. Evidence precedence — the same rule, renamed

| Order | Read | Evidence of | NOT evidence of |
|---|---|---|---|
| 1 | `agentPrompt`, node `description` | **intent** — why the node exists | the mechanics |
| 2 | `rulesConditionalConfig`, `code`, `tools`, edges, `mapConfig` | **mechanics** — ground truth for every deterministic claim | intent |
| 3 | node names | nothing on their own | anything |

**Intent may be wrong and still be faithfully recorded; mechanics may not.** Measured, not assumed:
a 5-node workflow described its conditional as routing *"high-value, mid-market and lower-tier leads
with different follow-up strategies"* while its code read

```python
if tier == "Tier 1":
    context.transition_to("Notify rep in Slack", "tier1")
```

One tier routed. Two computed, named, and dropped. **A reading that trusted that description would
have shipped a skill confidently wrong about the only thing it does.** So quote a description as the
author's stated purpose and never as behaviour.

## 4. Branch logic is in two places and you need both

| Where the condition lives | Share of 116 conditional nodes |
|---|---:|
| `rulesConditionalConfig` — machine-readable | 72% |
| `code` — must be read as code | **26%** |
| no description at all | 32% |

**A reader that only parses `rulesConditionalConfig` silently loses a quarter of every decision in
the library.** And the loss is not spread evenly across unimportant branches: in the best-designed
workflow read, the two undocumented code conditionals were **both human approval gates** — the nodes
deciding whether anything got sent at all. Code, so no rules. No description, so no prose.

`endRunOnNoMatch` is the fallthrough policy and it is the difference between a routed lead and a
dropped one. `false` means unmatched continues to whatever node has no rule; `true` means the run
stops. State which, always.

## 5. Three things a structural read gets wrong

**Loops are usually in node names.** 11% of workflows carry loop language in node names with no
`map` node, and only **1 of 97** used a real `map` node — an abandoned stub with default names. So
implicit iteration is the normal case and the correct expression is the rarity. A reader going by
`nodeType` sees ordinary tool calls and **mis-prices the run by a factor of the row count**.

**And the correct form is the only place fan-out is quantified.** A real `map` node carries
`maxConcurrency`, `maxRetries`, `gatherResults`. The 11% expressed in names carry none of it, so
there is nothing to price against.

**Cost is not in a workflow.** Credit figures appeared in a prose description in **1 of 97**. Treat
that as a freak rather than a source: **always ask what a run costs, never derive it.**

**Prompts can grant override authority over deterministic fields.** One classifier prompt told the
agent to *"use the website content to sanity-check or override when the employee count looks stale"* —
a judgment override of a firmographic number, invisible to any structural read and the most
important behavioural fact in that workflow. Read every prompt for permissions, not just for intent.

## 6. Where thresholds come from, and why you cannot inherit them

Extract every number from mechanics, then check it against the prose that mentions it. One workflow
had `foundedYear >= 2011` in its rule and *"founded in 2011 or later (within the last 15 years)"* in
its prompt. **Those agree in 2026 and diverge every year after.** So a threshold read out of a
workflow becomes a **declared input with the read value as its default**, never a constant, and
never the relative phrasing.

## 7. The low-yield boundary

A workflow is too thin to build from when the config gives you names and nothing else. The stub with
`New Enrich Node` and `New Map Node` is the clear case: four nodes, no descriptions, no prompts, one
tool. **A skill assembled from names like that is invention wearing a citation.** Say the workflow is
too thin, say which of the two things is missing — the purpose or the mechanics — and offer the
interview instead. That is a real answer and not a failure.

## 8. Which thresholds earn a question

**The budget is three CLASSES, not three questions** — the flow says *budget by class, not by turn
count*, and *one decision is one question even when it has two moving parts*. So the four thresholds
in a ten-node workflow are one class and one question, shown together with the config's values as
defaults. Do not re-derive that rule here; it already holds.

What this route adds is **which** thresholds belong in that question at all, because a workflow hands
you more numbers than a table does and most of them are not decisions:

| Read from the config | In the question? |
|---|---|
| a size cut-off that switches which path a record takes | **yes** — it changes who gets contacted |
| an activity window deciding what counts as flagged | **yes** |
| a country or segment list that switches routing | **yes** |
| tier values on a score **nothing branches on** | **no** — ask why it is computed, not what it should be |
| retry counts, concurrency, timeouts, page sizes | **no** — declare with the read value as default |

**The test is what changes, not what is unknown.** A number earns its place in the question when
changing it changes who gets contacted or what gets spent. Everything else is a declared input
carrying the read value, shown rather than asked.

**The insight is not one of the three.** It is the Step 1 question, it comes first, and on this route
it is the thing most likely to be missing altogether — 57% of workflows have no prompt to carry it.

## 9. What the interview must still ask

Because the config does not hold it, at these measured rates:

- **The insight and the ICP** — 57% of workflows have no prompt to carry either.
- **What a run costs** — 99% have no figure anywhere.
- **What the unused branches are for** — a workflow that computes a tier it never routes is not a
  spec, it is a question.
- **Who the destinations are** — one router assigned nine owners; 9 of 10 owner nodes had no
  description saying who they are.
- **Which steps halt** — declared by the creator, never inferred. See `## What this skill touches`.

Everything else — topology, tools, thresholds, gates, fallthrough, output shape — comes out of the
graph and does not need asking.
