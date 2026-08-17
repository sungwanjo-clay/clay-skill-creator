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

### 1. One question decides the route

> **Do you have a Clay table that already does this?**

**Yes** → step 2, then step 3. **No** → step 3. Either way you end up in the same interview: a table
changes how it *opens*, never whether it happens.

### 2. If yes — read the table's configuration

Configuration only. **Never a row, never a run, never a write.**

```
clay tables list --filter owner.id=<me>    always owner-scoped, on the FIRST call
clay tables columns list <tableId>         ids, names, types
clay tables columns get  <tableId>         the recipe: formulas, prompts, input wiring
```

Those three plus `clay whoami` are the whole surface. An unscoped `clay tables list` is
workspace-wide and table *names* encode customers and deals — and **reading is the irreversible
part, not filtering.** `clay tables rows` is never needed; `clay tables update` is a write despite
how it reads.

Read **prompts first** (intent), **formulas second** (mechanics), **names last** (evidence of
nothing). Never infer a step, a threshold or a purpose from a column name. Full procedure:
`workflows/table-to-skill.md`.

### 3. The interview — this always happens

**Don't transcribe a process — extract judgment.** A skill that is only steps is the part anyone
could have guessed. So: **one question per message**, never a numbered wall, and keep going until the
answers stop producing anything new rather than until a counter runs out — roughly five to eight
exchanges for a real play. Anything the configuration already showed is proposed back for
confirmation, not asked. Anything unconfirmed becomes a `proof_gap` rather than another question.
"Draft it" ends the interview immediately. Full script: `workflows/interview-to-skill.md`.

**Ask in this order** — the first two are where the value is:

1. **The tell** — *"what do you notice first here that other people miss?"*
2. **The mediocre version** — *"what does the bad version look like, the common mistake?"* People
   describe a failure they have watched far more vividly than a rule they follow.
3. **The time it went wrong** — one worked case, one that broke. Thresholds come out of the second;
   asking "why 50?" directly gets "it depends".
4. **The one or two decisive thresholds**, framed as a tradeoff rather than a spec request.
5. **The quality bar** — *"how do you know the output is good?"* This becomes **What good looks like**.
6. **The boundary**, as a yes/no over neighbours you propose from `EXISTING-SKILLS.md`.

**Depth belongs in `references/`, and its absence is a signal.** The strongest skills carry one to
three reference pages — rubrics with real numbers, worked examples, edge-case playbooks. A skill with
nothing to put in a reference file usually means the interview stopped early, not that the job was
simple.

What the finished skill must **answer** — which is not the same as what to ask, since most of it is
derivable: the job in the creator's words, the declared inputs, the steps in dependency order, every
threshold and why that number, the honest edges (cost, refusals, missing data), and the boundary.

If a table was read, continue from what it found — never restart. Quote their prompts back and quote
each threshold; that makes it a conversation about their work rather than a form.

**Never supply an answer the creator did not give.** That is the rule — not "never draft until every
question is answered", which is what turns an interview into a deadlock. Drafting with honest
`proof_gaps` is the normal outcome; inventing a rationale is the failure. If the conversation produces
no real insight at all, say so plainly and stop — `examples/low-yield-fallback/` is what that outcome
looks like written honestly.

### 4. Write, then validate

Write `build/<slug>/SKILL.md` following `SKILL-TEMPLATE.md`. Read `examples/` first — three real
shipped skills plus the low-yield outcome.

```
python3 tools/package_skill.py validate build/<slug>
```

`0` clean · `4` your package has blocking findings · `2` the command was wrong · `1` the tool is
broken, not your package. Multi-file skills also need packaging, because the form takes one file:

```
python3 tools/package_skill.py zip    build/<slug> <slug>.zip
python3 tools/package_skill.py verify <slug>.zip --manifest manifest.json
```

Compare **manifests, not archives** — a ZIP's bytes depend on the local compression library.
`VALIDATION.md` and `PACKAGE-LAYOUT.md` have the detail.

### 5. Submit

Read your `SKILL.md` end to end first — you are the last reviewer, and the only one who knows what
the table was for. Then upload or paste it into the Marketplace form.

**Nothing submits on your behalf** — not the CLI, not an agent, not this repo. `SUBMITTING.md` covers
what to expect, including that submitting is not publishing and that overlap is not a rejection.

## What's next

**Install the skill instead of fetching these docs.** [`clay-skill-author/`](clay-skill-author/) in
this repository is this whole procedure as an installable skill — the flow, its own validator, the
worked examples — and it needs no clone and no network. A sandbox with no outbound access cannot read
this page at all; an installed skill does not have to.

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
