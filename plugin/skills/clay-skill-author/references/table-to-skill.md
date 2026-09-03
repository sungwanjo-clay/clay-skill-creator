# Table → skill

Converts one Clay table into a portable `SKILL.md`. Reads configuration only — never a row, never a
run, never a write.

Prerequisite: [`../PREREQUISITES.md`](prerequisites.md). You need the CLI installed and
authenticated into the workspace holding the table.

## 1. Find your table

```
clay whoami
clay tables list --filter owner.id=<your user id>
```

**Always pass the owner filter.** `clay tables list` is workspace-wide by default, and in a shared
workspace it returns other people's tables — with names that often encode customers, deals and
colleagues. The filter is the only mechanism that scopes it: `owner` comes back `null` on every list
row, so you cannot filter a list you already fetched. Getting the order wrong cannot be repaired
afterwards.

If your workspace has more than one table owner, confirm which owner you mean *before* choosing a
table.

### 1b. Several at once — rank silently, offer the strongest three

**THE DOOR IS THE `Show me my tables` ROUTE**, which already lists tables and flags the ones carrying
formulas **and** prompts. That flag is the beginning of a ranking, and it is on the right signal —
formulas are where thresholds live, prompts are where judgment lives — so finish the job: rank them,
draft the strongest few, and offer a short start instead of handing back a list to choose from.
Somebody asking to be shown their tables is telling you they cannot pick.

The second door is plurality they state themselves: several table ids at once, or *all my tables*.

Score each off its configuration alone. Every signal is already read by §2 and §5:

| Signal | Read from | Why it ranks |
|---|---|---|
| a real decision exists | a comparison inside `formulaText`, or a prompt that classifies | a table of pasted values and lookups is a list, and a list productizes into nothing |
| thresholds are written down | the numbers §5 extracts via `source_claims` | a skill can carry a number it can find; it cannot carry one that was never written |
| the columns do work | how many are derived rather than pasted | a wide table of imported fields is thinner than a narrow one that computes |
| not a scratch copy | untitled, or matching *test*, *scratch*, *copy of*, *demo* | the same noise the workflow listing measures |

**A TABLE'S ROW COUNT IS NOT A SIGNAL.** It is the obvious proxy and it is the wrong one: this route
reads configuration and never a row, so a row count says nothing about whether the judgment is
portable. §4's yield check is a different question — whether the source held enough to convert — asked
later and per table.

Then say it in two short paragraphs:

> All 9 read and drafted. The mechanical half batches fine — the columns, the thresholds, the
> dependency order, the packaging.
>
> These three look strongest — `renewal-risk`, `icp-scoring`, `signup-triage`. Want to start with
> them?

**No count of what was cut, no ranking criterion, and no time estimate**, for the reasons
[`workflow-to-skill.md`](workflow-to-skill.md) records against its own drafts of the same line: a
criterion grades their work, and a duration is a number nobody measured.

**Then run §2 onward per table, one at a time, best first.** Batching removed the reading and the
drafting and nothing from the interview or from §4's yield check — both still happen per table, and a
table that fails the yield check fails it on its own. The answer sheet makes the second one fast.

## 2. Read the recipe

```
clay tables columns list <tableId>    # ids, names, types, last-updated
clay tables columns get  <tableId>    # the actual recipe
```

`columns get` is where the substance is: per column, the formula text, the AI prompt, the input
wiring, the output type. The dependency graph is derivable from the `{{f_…}}` references inside
formulas — that is what turns a left-to-right table into an ordered sequence of steps.

Two things this deliberately does **not** read. `clay tables rows` (your data — never needed, since
output shape is derivable from configuration). And `clay tables update`, which despite the name is a
**write**: it toggles query sync. It reads like a settings change, which is exactly why it is worth
naming.

## 3. What gets read, in what order

Prompts first, formulas second, column names last — and the order matters.

| Read | Evidence of | Not evidence of |
|---|---|---|
| your **prompts** | *intent* — why the column exists, in your words, including judgment you never expressed as arithmetic | the mechanics; a prompt can state a goal it does not achieve |
| your **formulas** | *mechanics* — thresholds, comparators, arithmetic, dependencies | intent; a formula cannot say why 50 was chosen |
| column **names** | nothing on their own | anything |

A prompt preserves your reasoning; a formula preserves the threshold and discards the argument for
it. Both are kept, separately: if a prompt says you exclude enterprise accounts but no formula does
it, that gap becomes a question for you rather than a silent correction.

## 4. The yield check — and the fallback that is not a failure

Before drafting anything, the converter measures whether your table can support a skill at all. Two
axes, and falling short on either routes you to the interview:

| Axis | Needs |
|---|---|
| **intent** | at least one substantial prompt, or a purpose you state yourself |
| **mechanics** | at least two columns whose behaviour is derivable — a formula, or a resolvable action |

Both numbers are reported, so if you are routed to the interview you are told which axis fell short
and by how much. "Nothing recoverable here" without a number is indistinguishable from a broken tool.

**A fallback is the expected outcome for a meaningful share of tables, not an error.** Measured
across a real sample: a quarter of tables carry no formulas at all, and the yield is lumpy — one
table held more than half the logic in the whole sample. If yours falls short, the interview reaches
the same destination from a different direction.

One thing it will never do: infer a step, a threshold or a purpose from a column *name*. Names are
free text with no contract, and a skill assembled from them is fluent, plausible and unfounded —
worse than no skill, because it reads as derived from your table.

## 5. Thresholds are extracted, then checked

Every threshold, comparator and constant becomes a structured **claim**:

```yaml
deterministic_claims:
  - id: t1
    kind: threshold
    subject: "employee count"
    comparator: ">="
    value: 50
    source: { evidence: formula, digest: "sha256:…" }
```

Two consequences worth understanding, because they are the reason this is trustworthy:

**The prose is generated from the claim, not the other way round.** "50 or more" is rendered from
`{">=", 50}`. Nothing ever reads a number back out of finished English, so the sentence and the
claim cannot drift apart.

**The claim is compared against your formula before the package is produced, and a mismatch stops
generation.** Both sides are structured, so the check is exact. It fails in both directions: a
wrong number *and* a dropped one, because to whoever installs your skill those are the same defect.

Your formula text itself does not ship — it can contain column references, auth handles and prose
about real customers. The package carries the extracted comparator and value plus a digest of the
source, which records *which* formula was compared without disclosing it.

## 6. Steps come out in dependency order

Your table is spatial: columns sit wherever you added them. A skill is procedural: step 3 may only
use what steps 1–2 produced. If you added a correction column at the far right, that is a step-2
operation sitting in the last position — so ordering follows the dependency graph, not the column
list.

Root inputs (referenced by others, referencing nothing) become the skill's declared inputs and open
it. Columns nothing references are **played back to you** rather than dropped: a dependency graph
cannot tell an abandoned experiment from an optional input you never filled, so you decide.

## 7. Review, then submit

You get a complete `SKILL.md`. Read it. Then [`../VALIDATION.md`](validation.md) to check it
locally, and [`../SUBMITTING.md`](submitting.md) to upload it.

**If any step in it spends credits, read [`../DETERMINISM.md`](determinism.md) before you ship.**
Your table's recipe says which function ran; it does not say what that function costs, what its real
input schema is, or which of its outputs you can trust — and a step that names none of those resolves
differently for every installer. That file carries the discovery commands, the two cost meters, and
the traps: display names that are not keys, a plural action name that accepts one item, a description
that contradicts its own schema.

**Two ways to submit, and you pick.** Upload it yourself through the Clay Marketplace submission
form, or have the agent send it from the session — which shows you the exact payload and the consent
text first and cannot send without your yes. Nothing goes out on its own either way, and the flow is
required to put both in front of you rather than leaving you with a validated file and no next step.

And note what the local check does *not* cover: it sees the file as generated. If you edit a
threshold afterwards, nothing re-checks it against your formula — the comparison happened at
generation time, on your machine, and cannot be replayed later by anyone else.
