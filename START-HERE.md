# Getting started with Clay skills

> This file is written to be handed to your coding agent. Point it here — paste the link or the
> file itself — and ask it to create a Clay skill with you. Installing the Clay plugin, signing in,
> reading your table's configuration and writing the file are all things the agent does by
> following the steps below.

Turn a Clay table you already built, or just an idea, into a portable `SKILL.md` you can submit to
the Marketplace.

```
Create a Clay GTM skill by following the steps in
https://github.com/sungwanjo-clay/clay-skill-creator
```

**If you fetched only this file, the rest are one fetch away.** Over HTTP a relative name resolves
to nothing, which is what produces a "file not found" partway through a run that started fine:

```
curl -fsSL https://raw.githubusercontent.com/sungwanjo-clay/clay-skill-creator/main/<NAME>
```

Nothing below requires another file. Fetch on demand rather than guessing at content you could not
read.

## Installation

Skip to **Sign in** if `clay whoami` already returns a user id.

### Claude Code

Requires **Claude Code v2.1.91+**. Runs from inside Claude Code — no separate terminal.

```
/plugin marketplace add clay-run/agent-plugins
/plugin install clay@clay-plugins
```

### Codex

```
codex plugin marketplace add clay-run/agent-plugins
```

Then open **Plugins** and install **clay**. This needs a terminal, so the Codex web app cannot do it
— see the surface table under *What's next*.

### Cursor

Do **not** hand-copy into `~/.cursor/plugins/local/` — org policy can block sideloading silently.
Use the plugin's own `setup` skill, which reads the effective policy and picks a path that works.

### If any of that fails

Clay's procedure is authoritative, and it carries the parts that move — the version pin, the Cursor
policy path, the `PATH` forwarder, troubleshooting:

```
curl -fsSL https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md
```

## Sign in, then check the table path

```
clay login           # opens a browser once
clay whoami          # must return a user id
```

One sign-in covers both the `clay` command and the Clay MCP server — they read the same session.
Some hosts need a restart before a freshly installed plugin registers. If the plugin is installed but
you are signed out, `clay:setup` does PATH and sign-in in one step.

Then one free, scoped call, **before reading anything**:

```
clay tables list --limit 1 --filter owner.id=<the id from clay whoami>; echo "exit=$?"
```

| exit | Meaning |
|---|---|
| **0** | The table path is open. Continue. |
| **3** | `auth_forbidden` — needs API table sync, **available on Enterprise plans**. Skip to the interview, which needs none of this and reaches the same finished skill. |
| **5** | Network, not permission. Retry; do not re-run sign-in. |

Say which happened. Finding out here costs one command; finding out at the last step costs the whole
setup.

## Create the skill

**The shape: derive everything derivable first, then ask only what the derivation could not settle.**
Asking before reading wastes your time on questions your table already answers, and an ungrounded
question invites a shrug. You will be shown a complete draft to correct rather than a form to fill in —
people correct documents far better than they answer questions about them.

### 1. Route — one question, four answers

> **From a Clay table, from scratch, or uploading a skill you already have?**

| Answer | Route |
|---|---|
| **From a table** | step 2 |
| **From scratch** | `workflows/interview-to-skill.md` — no table, no preflight |
| **I already have a `SKILL.md`** | step 5 |
| **Not sure — show me** | your tables get listed, with the ones carrying formulas *and* prompts flagged |

### 2. Confirm the table, then read its configuration

Boundaries are stated before anything is read: **configuration only** — never a row, never a run, never
a write — **no credential or personal detail repeated back**, in whole or in part, and workspace
handles become declared inputs rather than literals.

```
clay tables list --filter owner.id=<me>    always owner-scoped, on the FIRST call
clay tables columns list <tableId>         ids, names, types
clay tables columns get  <tableId>         the recipe: formulas, prompts, input wiring
```

Those three plus `clay whoami` are the whole surface. An unscoped list is workspace-wide and table
*names* encode customers and deals — **reading is the irreversible part, not filtering.** Prompts are
read first (intent), formulas second (mechanics), names last (evidence of nothing).

### 3. A complete draft is written before you are asked anything

`tools/derive_recipe.py` produces the steps in **dependency order** (not column order), the thresholds
taken from your formulas, and the thin-table decision. That becomes a complete `SKILL.md` — not an
outline.

**Every claim in it is one of three things: derived from something actually read, supplied by you, or
marked as a gap.** There is no fourth category, and it is enforced rather than promised: a threshold
the draft states that your formula does not contain is a **build failure**, and so is one your formula
contains that the draft dropped.

### 4. Then a few questions — and only these

A question is asked only if the answer changes what gets written: a decisive threshold with no
derivable reason, a gate whose condition is readable but whose purpose is not, a hardcoded count that
might be an editorial rule or an accident, an orphan column nothing references, and the boundary.
Everything else becomes a documented gap.

**At most three, plus the boundary. One question per message.** Each one explains its own context in a sentence
— what the column does, the options, the tradeoff — so you never have to go read your own table to
answer. Saying **"draft it"** ends the questions immediately and the rest becomes gaps.

**"I don't know, that was arbitrary" is a useful answer** — it becomes a documented `proof_gap` instead
of a fake rationale.

### 5. You see the skeleton, then it builds

The title, the steps as one-liners, each decision with its value and source (`formula` / `you said` /
`gap`), the gaps in full, and the declared inputs — on one screen. Then one question: *anything wrong?*

```
python3 tools/package_skill.py validate build/<slug>
```

`0` clean · `4` blocking findings in your package · `2` the command was wrong · `1` the tool is broken,
not your package. Multi-file skills also need `zip` then `verify`, and you compare **manifests, not
archives**. Read the file end to end before uploading — you are the last reviewer. **Nothing submits on
your behalf.**

## What's next

**Install it instead of fetching these docs.** This repository declares itself a plugin
marketplace, so the whole flow installs — no clone, no network at runtime:

```
codex plugin marketplace add sungwanjo-clay/clay-skill-creator
```

or `/plugin marketplace add sungwanjo-clay/clay-skill-creator` in Claude Code, then install
**`clay-skill-author`**. The skill is at
[`plugin/skills/clay-skill-author/`](plugin/skills/clay-skill-author/): the flow, its own validator
and the worked examples. **A sandbox with no outbound access cannot read this page at all; an
installed skill does not have to.**

**Two prompts, not one.** Install is a separate job from doing the work, and trying to make one line
do both is what kept failing:

```
1.  Set up the Clay skill creator by following the steps in
    https://github.com/sungwanjo-clay/clay-skill-creator

2.  Create a Clay GTM skill
```

**Which surfaces support which path:**

| Surface | Interview → skill | Table → skill |
|---|---|---|
| Claude Code · Codex CLI · Cursor | yes | yes |
| Codex web app | yes | **no** — no terminal to install the plugin, and no network for the CLI to fetch its binary |

**Three ways this goes wrong, and how to spot them.**

- **Your agent names no files from here.** Ask which files it read. A confident plan with no
  filenames means it fell back to a generic skill-creation workflow, and its output will look
  correct and be unrelated to any of this. Stop it and fix access first.
- **The `SKILL.md` states an insight you never said.** That is the failure, not a bonus. A generated
  insight reads better than a real one and is worth less than nothing, because somebody downstream
  will act on it.
- **A clean validation gets read as a verdict.** It checks that the package is well-formed and
  portable. It does not check whether the logic fits the job, whether the thresholds are the ones you
  want, or whether the skill helps anyone.
