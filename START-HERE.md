# Start here

Turn GTM judgment you already have into a Clay skill. One paste, then a conversation.

```
Create a Clay GTM skill by following the steps in
https://github.com/sungwanjo-clay/clay-skill-creator
```

Everything below is addressed to the agent you pasted that into. Read it yourself too — it is
exactly what your agent is about to do, in order, and the last section tells you how to spot it
going wrong.

---

## What you need

`git`, `python3`, and the **Clay CLI**. Step 1 gets you authenticated; you click one consent screen.

**Any agent host works.** The CLI ships in Clay's agent plugin, which installs on **Claude Code,
Codex and Cursor**; the install command differs per host and nothing after it does, because all three
run the same bundled `clay`. `PREREQUISITES.md` has the three commands. Nothing in this repo is
specific to one host — it is documents and two Python scripts.

**If you have Clay's MCP server configured, you do not have the CLI.** They are different things and
having one gives you nothing toward the other: MCP puts Clay tools inside a chat, the CLI puts a
`clay` command in your terminal. This flow needs the terminal command. It is worth stating plainly
because it is the most likely way setup fails silently — everything looks configured, and then a
command that should work reports `clay: command not found` with nothing explaining why.

**What the CLI costs you.** If you live in Clay's UI rather than a terminal, this is real setup —
call it 15–30 minutes the first time, and we would rather name that than hide it. Two things make it
pay. Reading your table's configuration is **free**: no credits, no runs, no enrichment, because
these are metadata reads. And the CLI is the same substrate every later path uses, so you install it
once for more than this one job.

---

## 1. Authenticate, then preflight

```
clay --version      # if this prints nothing, you do not have the CLI yet — see PREREQUISITES.md
clay login
clay whoami         # must return your user id
```

`clay login` pins the session to whichever workspace you pick on the consent screen. If the table you
want lives in a different one, run `clay login` again and pick that one — no need to log out first.

**Then check the table path is open to you, before reading anything.** Table reads are served by
Clay's public observability API, which the CLI's help states is enabled per workspace and available on
Enterprise plans. One free, scoped call settles it:

```
clay tables list --limit 1 --filter owner.id=<the id from clay whoami>; echo "exit=$?"
```

Exit `0` and you are through. Exit `3` (`auth_forbidden`) means the table path is closed to this
workspace — **skip to step 5 and take the interview path**, which needs none of this and reaches the
same finished skill. Finding that out now costs one command; finding it out at step 4 costs the whole
setup.

## 2. Scope to yourself before listing anything

```
clay tables list --filter owner.id=<the id from clay whoami>
```

**Always pass the owner filter, and pass it the first time.** An unscoped `clay tables list` is
workspace-wide — the CLI's own help says so: *"With no `--filter`, every table is listed."* In a shared
workspace that returns other people's tables, and table *names* routinely encode customers, deals and
colleagues.

**The reason to pass it the first time is that reading is the irreversible part, not filtering.** By
the time an unscoped list is in front of you, you have already read those names; narrowing the list
afterwards does not unsee them, whether or not each row happens to carry an `owner` you could filter
on. So this is the one step in the flow that cannot be undone by doing it again — not because a second
attempt is impossible, but because the cost was paid on the first.

`owner.id` accepts a single id or a comma-separated list, and `queryEnabled` and `workbook.id` are the
other two filters, all ANDed. Anything else is a malformed token and fails as `validation_error`
(exit 2) rather than silently listing everything.

If the workspace has more than one table owner, confirm which owner is meant before picking a table.

## 3. One question decides the route

> **Do you have a Clay table that already does this?**

That is the whole branch, and you do not need to know what a `SKILL.md` is to answer it.

| Answer | Go to |
|---|---|
| **Yes** | step 4, then step 5 |
| **No** | step 5 |
| *"I already have a `SKILL.md`"* | step 6, and validate it |

Both answers end up in the same interview. A table does not replace it — it just means the interview
opens with your own prompts already read back to you and your own thresholds already quoted.

## 4. If yes — read the table's configuration

Configuration only. **Never a row, never a run, never a write.**

```
clay tables columns list <tableId>    # ids, names, types
clay tables columns get  <tableId>    # the recipe: formulas, prompts, input wiring
```

Two commands to stay away from. `clay tables rows` is your data, and it is never needed — output
shape is derivable from configuration alone. And `clay tables update` is a **write** despite how it
reads: it toggles query sync, which is easy to miss because it looks like a settings change.

Read in this order, because the order decides what you recover:

| Read | Evidence of | Not evidence of |
|---|---|---|
| **prompts** first | *intent* — why a column exists, in your own words | mechanics; a prompt can state a goal it never achieves |
| **formulas** second | *mechanics* — thresholds, comparators, dependencies | intent; a formula cannot say why 50 |
| column **names** last | nothing on their own | anything at all |

Never infer a step, a threshold or a purpose from a column *name*. Names are free text with no
contract, and a skill assembled from them is fluent, plausible and unfounded — worse than no skill,
because it reads as though it came from your table.

Then continue to step 5.

## 5. The interview — this always happens

Table or no table, the same six questions in the same order. Purpose before mechanics, because
mechanics without purpose produces a skill that runs and helps nobody.

1. **The job.** What does someone want done, in their words? This becomes the description that
   decides when the skill gets picked, so the phrasing matters more than it looks.
2. **The input.** What does the installer start with — a CSV of domains, one company, a list of
   people? Name the fields.
3. **The steps.** What happens, in order, and what each step needs from the ones before it.
4. **The decisions.** Every threshold, band, tier and cutoff — **and why that number.** "Score
   highly" is not runnable. "50 or more employees" is.
5. **The honest edges.** What should it refuse to guess at? What does it cost per row? What does it
   do when the data is missing — and "returns nothing" is a real answer to state rather than pad.
6. **The boundary.** What should it *not* be used for? Naming the neighbours is what stops the wrong
   skill being picked. Check `EXISTING-SKILLS.md` and name two or three by slug.

**If a table was read, the interview continues from what it found — it never restarts.** Quote the
prompts back and ask whether they still describe the intent. Quote each threshold and ask why that
number. Play back the columns nothing references rather than dropping them: a dependency graph cannot
tell an abandoned experiment from an optional input never filled, so the creator decides.

**A thin table is not a wasted install.** Even a four-column table with no formulas yields an action
and a handle graph, which is a real head start on questions 2 and 3. What a thin table lacks is not
volume, it is a **decision** — nothing in it that could be right or wrong. Question 4 supplies
exactly that. No answer to the routing question, and no shape of table, makes installing the CLI a
thing to regret.

### The stop condition

**Do not draft any part of the skill until the interview is finished, and never supply an answer the
creator did not give.** If an answer is too thin to build on, say so and ask again.

If the conversation never produces a real insight — something specific to how this person works,
that could not have been generated for them — **say that plainly and stop.** Do not write a skill
whose substance was invented to fill the gap. `examples/low-yield-fallback/SKILL.md` shows the shape
of that outcome: a complete, usable file whose `proof_gaps` name the interview as the source of its
logic, rather than a confident file resting on nothing.

## 6. Write, then validate

Write to `build/<slug>/SKILL.md` following `SKILL-TEMPLATE.md`, plus `build/<slug>/references/` only
if the material genuinely warrants it. Set `proof_status` to match how the logic was actually
obtained: interview-derived logic carries a gap naming the interview, because it has no ground truth
anywhere; table-derived thresholds were compared against real formulas and say so.

```
python3 tools/package_skill.py validate build/<slug>
```

Exit `0` means the shape and content checks pass. Non-zero prints every finding with its file and
line. `block` must be fixed. `report` is a heuristic worth a look that does not stop you.

**If your skill is a single `SKILL.md`, you are done — go to step 7 and paste it.**

**If it has supporting files, package it**, because the form takes one file:

```
python3 tools/package_skill.py zip    build/<slug> <slug>.zip
python3 tools/package_skill.py verify <slug>.zip --manifest manifest.json
```

`zip` writes the archive and prints a manifest — the relative path and SHA-256 of every file in it.
`verify` reads the archive back and recomputes that manifest, so you know the file you are about to
upload contains exactly what you built. Worth doing once: it is the only check that runs on the
artifact rather than on the folder.

Two builds of the same content always produce the same **manifest**. They usually produce identical
archive bytes too, but do not rely on that — a ZIP's bytes depend on your Python's compression
library, so **compare manifests, not archives.** `PACKAGE-LAYOUT.md` has the layout rules if a
finding sends you there.

## 7. Submit

Read your `SKILL.md` end to end first. You are the last reviewer, and the only person who knows what
the table was actually for. Then open the Clay Marketplace submission form and upload the package or
paste the file.

**Nothing submits on your behalf** — not the CLI, not an agent, not this repo. The step where you
read the file before uploading is deliberate.

---

## What this will not do — and how you can tell

The first item is the one worth knowing how to check, because it is a claim about behaviour rather
than about the tooling, and prose in a file cannot enforce it.

**It will not invent your insight.** A skill's value is the judgment inside it, and that has to come
from you. **Here is the tell:** if you receive a `SKILL.md` whose central insight you never said out
loud — a crisp claim about your market or your motion that you do not recognise as yours — that is
the failure, not a bonus. The file is wrong. Say so and ask it to stop and show you what you actually
gave it. A generated insight reads better than a real one and is worth less than nothing, because
somebody downstream will act on it.

**Reading your table recovers mechanics, never intent.** It can tell you the threshold is 50. It
cannot tell you why 50. Every version of this flow says so, every time.

**A clean validation is a floor, not a verdict.** It checks that the package is well-formed and
portable. It does not check whether the logic fits the job, whether the thresholds are the ones you
want, or whether the skill helps anyone.

**Nothing re-checks a threshold you edit afterwards.** The comparison against your formula happens at
generation time, on your machine, and cannot be replayed later by anyone — including us.
