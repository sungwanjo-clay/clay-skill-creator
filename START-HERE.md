# Start here

Turn GTM judgment you already have into a Clay skill. One paste, then a conversation.

```
Create a Clay GTM skill by following the steps in
https://github.com/sungwanjo-clay/clay-skill-creator
```

**If you fetched only this file, you can fetch the others.** Every document named below is a
sibling in the same repository, and over HTTP a relative name resolves to nothing — which is what
produces a "file not found" partway through a run that started fine. The pattern:

```
curl -fsSL https://raw.githubusercontent.com/sungwanjo-clay/clay-skill-creator/main/<NAME>
```

So `PREREQUISITES.md`, `SKILL-TEMPLATE.md`, `EXISTING-SKILLS.md` and `PACKAGE-LAYOUT.md` are all one
fetch away. **You should not need any of them for a normal run** — the steps below are self-contained
— but fetch on demand rather than guessing at content you could not read.

Everything below is addressed to the agent you pasted that into. Read it yourself too — it is
exactly what your agent is about to do, in order, and the last section tells you how to spot it
going wrong.

**If your agent cannot reach this page, install the skill instead of lengthening the prompt.** That
line is deliberately one line, and on its first real run an agent could not fetch this repository —
its sandbox had no outbound network — and rather than stopping it announced it would *"continue with
the standard skill packaging workflow rather than blocking on access"*, then invented a process. It
had somewhere plausible to fall: several hosts ship a built-in skill whose name nearly collides, and
a local skill always beats a URL fetch.

**First, try the other fetch mechanism.** A blob page and a `git clone` can both fail where a raw
fetch succeeds, and they are genuinely different paths:

```
curl -fsSL https://raw.githubusercontent.com/sungwanjo-clay/clay-skill-creator/main/START-HERE.md
```

**If that also returns nothing, stop fetching and install instead.** Wording cannot fix this, because
the prompt is a routing input rather than a specification. What fixes it is being the local skill:
**`clay-skill-author`** carries this whole procedure, its own validator and the worked examples, and
needs no clone and no network. Install that and the same one-liner routes to it offline. This
repository is then the human-readable copy of what it does.

**How to tell which one you got.** Ask your agent to name the files it read. Real filenames from here
— `PREREQUISITES.md`, `SKILL-TEMPLATE.md`, `EXISTING-SKILLS.md` — or the skill's own
`prerequisites.md` and `examples/`, mean it is working from this material. A confident plan that names
none of them means it fell back to a generic skill-creation workflow, and the `SKILL.md` it produces
will look correct and have nothing to do with any of this. Stop it and fix access first.

---

## What you need

`git`, `python3`, and the **Clay agent plugin**. Step 1 installs it and signs you in; you click one
consent screen.

**Step 1 carries the commands, not a pointer to them.** An earlier version sent you to Clay's own
document for everything, which added a fetch that can fail — and it did. So the split is by what
actually moves: the install commands, `clay login` and `clay whoami` are stable strings and live
inline in step 1, while the parts that genuinely drift stay with
[Clay's GETTING_STARTED.md](https://github.com/clay-run/agent-plugins/blob/main/GETTING_STARTED.md),
which remains authoritative — the Claude Code version pin, the Cursor org-policy path, the `PATH`
forwarder, and troubleshooting. **A creator on a normal machine never needs a second fetch.**

**The interview path works on every host. The table path needs a terminal.** The plugin installs on
Claude Code, Codex and Cursor, and only the install command differs — all three then run the same
bundled `clay`. On Claude Code you install from *inside* Claude Code, no separate terminal.

| Surface | Interview → skill | Table → skill |
|---|---|---|
| **Claude Code** · **Codex CLI** · **Cursor** | yes | yes |
| **Codex web app** | yes | **no** |

The Codex web app has no terminal, so `codex plugin marketplace add` cannot run and the plugin cannot
be installed there by any route — and its sandbox has no outbound network, so even a manually placed
`clay` could not download its own binary on first use. That closes the table path on that surface for
reasons that have nothing to do with this repo. **It is a routing note, not a dead end:** the
interview path needs none of it and reaches the same finished skill.

Nothing in this repo is host-specific; it is documents and two Python scripts.

**One login covers both surfaces.** `clay login` authenticates the `clay` command *and* the Clay MCP
server — the plugin registers `clay mcp` as the server and both read the same session. You do not
choose between them and you do not sign in twice. The trap is narrower than it used to look: if you
configured Clay's MCP server **separately, without the plugin**, you have the tools but no `clay`
command, and the table path needs the command. That is the one case where everything looks configured
and a documented command still reports `clay: command not found`.

**What setup costs you.** If you live in Clay's UI rather than a terminal, this is real setup — call
it 15–30 minutes the first time, and we would rather name that than hide it. Two things make it pay.
Reading your table's configuration is **free**: no credits, no runs, no enrichment, because these are
metadata reads. And the plugin is the same substrate every later Clay path uses, so you install it
once for more than this one job. **If it is not worth it, the interview path needs none of it** and
reaches the same finished skill.

---

## 1. Set up Clay

```
clay whoami          # exit 0 with a user id? skip to the preflight below
```

**Not installed yet?** Install the plugin for your host. These are stable strings — a repository
identifier does not move — so they are here rather than behind another fetch:

```
Claude Code    /plugin marketplace add clay-run/agent-plugins
               /plugin install clay@clay-plugins

Codex CLI      codex plugin marketplace add clay-run/agent-plugins
               then open Plugins and install clay

Cursor         do NOT hand-copy into ~/.cursor/plugins/local/ — org policy can block
               sideloading silently. Use Clay's setup skill, which reads the effective
               policy and picks a path that works.
```

Then sign in and verify:

```
clay login           # opens a browser once
clay whoami          # must return your user id
```

One sign-in covers both surfaces: the `clay` command and the Clay MCP server read the same session
from disk. Some hosts need a restart before a freshly installed plugin registers, so if `clay` is
still missing straight after installing, that is why rather than a failed install.

**If anything above fails, Clay's own procedure is authoritative** — and it carries the parts that
genuinely do move: the Claude Code version pin, the Cursor org-policy path, the `PATH` forwarder, and
a troubleshooting table.

```
curl -fsSL https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md
```

If the plugin is already installed but you are signed out, its bundled `setup` skill does install,
PATH and sign-in in one step — invoke it as `clay:setup`.

### Then preflight the table path, before reading anything

```
clay tables list --limit 1 --filter owner.id=<the id from clay whoami>; echo "exit=$?"
```

Exit `0` and you are through. Exit `3` (`auth_forbidden`) means the `clay tables` query surface is
not enabled for this workspace — it needs API table sync, available on Enterprise plans — so **skip
to step 5 and take the interview path**, which needs none of this and reaches the same finished
skill. Exit `5` is a network problem, not a permission one: retry, do not re-run sign-in.

Finding that out here costs one free call. Finding it out at step 4 costs the whole setup.

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
