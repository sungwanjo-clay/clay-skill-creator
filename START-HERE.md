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

**Only if you are starting from a Clay table.** Two of the four routes below — *from scratch* and
*I already have a `SKILL.md`* — touch Clay at no point, so none of this applies to them. Skip straight
to **Create the skill**; a from-scratch skill needs no sign-in, no CLI and no plugin. This section runs
after you know your route, not before.

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

> **Where are you starting from?**

| Answer | Route |
|---|---|
| **From a Clay table** | sign in and preflight, then step 2 |
| **From scratch** | `workflows/interview-to-skill.md` — no sign-in, no table, no preflight |
| **I already have a `SKILL.md`** | step 5 — no sign-in either |
| **Show me my tables** | sign in, then your tables get listed, with the ones carrying formulas *and* prompts flagged |

The last one is the most common place to actually be, and if your workspace cannot list tables the
answer is the interview rather than an error — you are not stuck.

**The route is asked before anything is set up**, because two of its four answers make the setup
unnecessary. Asked the other way round it costs a sign-in, a permission prompt and a couple of minutes
to reach an answer that discards all of it. If your agent starts installing things before asking you
this, it is running an older version of the flow.

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

**The boundary is derived, not asked.** The skill comes with a "don't use this for…" list written
against the nearest existing Marketplace skills. You are never asked where the line goes — you are shown
it and can correct it, because that answer lives in the catalogue rather than in your head.

**A file it names, it writes.** If the draft says to copy `references/something.md`, that file is
written in the same step — **never emit a reference to something that does not exist**. A `SKILL.md`
that promises a file nobody wrote reads as finished and fails on first use, and it fails for whoever
installed it rather than for you. Validation does block on it, at the end; a file you have already
sent a friend never got that far.

**It carries a `## What this skill touches` section — Reads, Writes, Never** — derived from the steps
rather than asked of you, with all three named even where the answer is one word. `Writes: nothing` is
the most reassuring line a read-only skill has, so it gets said rather than implied. The validator
looks for it, and it is what a safety review compares the body against: a skill that declares nothing
cannot be contradicted.

**It states the read/write posture at Step 0 — a statement, not a question.** Two sentences at the top
of your skill: what it reads, what it writes, what it never touches. Nothing waits on an answer.

**It runs a small batch before the full one, and gets exactly one gate before anything bills or
mutates.** A read-only or reversible step gets a real **10-row batch** whose output you look at; an
irreversible one — an enrollment, a sent message, a CRM write — gets a **dry run** first, because a
ten-row test of an enrollment is ten real people really enrolled. Then one message carries the batch
result, the full cost, what will be written and where, and the ask. **One gate, not three** — and it
names the write out loud, because an action on your own connected account often costs no Clay credits,
so a cost-only gate can report a truthful zero while a hundred records change.

**And two things never reach a draft, whatever you ask for.** No step that **destroys data** — no
delete, no cleared field, no populated value overwritten with a blank, and an update that empties a
field is a deletion however the action is named. No step that **moves the installer's data somewhere
they did not name**. Ask for either and you get a reviewed list instead, so the destructive part runs
in the system that has your audit log.

**Every claim in it is one of three things: derived from something actually read, supplied by you, or
marked as a gap.** There is no fourth category, and it is enforced rather than promised: a threshold
the draft states that your formula does not contain is a **build failure**, and so is one your formula
contains that the draft dropped.

**That includes the insight — the claim in the title, which nothing mechanical can check.** If
sharpening what you said produces a stronger claim than you actually made, you get asked whether that
is what you meant, in one closed question. A yes and it is yours. Anything else and your own wording
ships with the sharper reading recorded as a gap. **It is never shipped as yours on a guess**, because
a generated insight reads better than a real one and is the line downstream readers are most likely to
act on.

### 4. Then a few questions — and only these

A question is asked only if the answer changes what gets written: a decisive threshold with no
derivable reason, a gate whose condition is readable but whose purpose is not, a hardcoded count that
might be an editorial rule or an accident, and an orphan column nothing references. Everything else
becomes a documented gap.

**At most three. One question per message.** Each one explains its own context in a sentence
— what the column does, the options, the tradeoff — so you never have to go read your own table to
answer. Saying **"draft it"** ends the questions immediately and the rest becomes gaps.

**"I don't know, that was arbitrary" is a useful answer** — the skill records it as something nobody
established, instead of inventing a rationale for it.

### 5. You see the skeleton, then it builds

The title and what it produces, the steps as one-liners, **every number and where it came from**
(*your formula* · *you told me* · *nobody established this*), **what the skill does not claim**, and
what an installer will have to supply — on one screen, in plain language, not field names. You are
reviewing your own workflow, not our package format, so nothing on that screen should be a term you
have to look up. Then one question: *anything wrong?*

```
python3 tools/package_skill.py validate build/<slug>
```

`0` clean · `4` blocking findings in your package · `2` the command was wrong · `1` the tool is broken,
not your package. Multi-file skills also need `zip` then `verify`, and you compare **manifests, not
archives**. Read the file end to end before uploading — you are the last reviewer. **Nothing submits without an explicit yes from you.** You can upload it yourself, or the agent can send it — but only after showing you exactly what would go, including the consent text, and asking. It cannot send without that step: the send command refuses without a token the preview prints, and the token stops matching if the file changed after you saw it.

**You get one stop here, not four.** Where the file is, that it validated clean, that you are its last
reviewer, and exactly what would be sent — all in one message, then the ask. This used to be four
consecutive halts, which protected less than one does: by the third you are acknowledging rather than
reading, and the one carrying the actual lock arrives last. **Fold the showing into one message; never
fold away the ask** — the token is the mechanism that keeps "nothing submits without your yes" true
rather than merely written down.

**You always get both ways to submit, and picking is yours.** Either you upload it at
[`marketplace.clay.com/submit`](https://marketplace.clay.com/submit), or the agent sends it from the
session with `tools/submit_skill.py`. Both reach the same review queue. **Naming both is required of
the flow; sending is never required of you** — those are different things, and only the first is
mandatory. Two real runs ended with a validated package on disk and no stated next step, which is a
dead end after twenty minutes of work, so the handoff is now a step rather than an afterthought. "Not
now" is a complete answer and you will not be asked twice.

**Two things to know before you send.** Your submission carries your name and work email, because
someone has to be able to reach you about your own skill; nothing publishes without an approval, and a
first response takes two business days during early access. And there is no self-service withdrawal
yet — if you want something pulled back, ask the person who invited you. `SUBMITTING.md` has the rest.

**And it will not paste your package through the chat.** Submitting sends the file itself, and at the size limits that means well over a million tokens of encoded data — which does not fit, and fails looking like a corrupt archive rather than an obvious limit. The agent runs a script that reads the file from disk instead. **Never build the request yourself** is a rule written into the skill, for the same reason the retry secret is generated by that script: anything needing exact bytes or real randomness comes from code, never from the model.

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

### Getting the current version, once it is installed

**Nothing updates on its own.** Plugin auto-update is off by default for third-party marketplaces, so
an install stays on whatever version it fetched until you replace it — and the symptom is a run that
behaves like an older document than the one you are reading.

The version is the first line of output, and it is also in the path the skill loaded from:

```
clay-skill-author/<version> · loaded from …/clay-skill-author/<version>/skills/clay-skill-author/SKILL.md
```

**The example above is deliberately not pinned to a number.** A version written into a document
goes stale the next time one ships, and a stale example reads as the version you should be on.
The two places that agree are the announce line and the directory it loaded from — compare those
to each other, not to anything written here.

**The version appears in that path because it is the cache key**, so a stale install is visible
without any command: the directory name is the version you are actually running. To move:

```
/plugin marketplace update clay-skill-creator
/plugin uninstall clay-skill-author@clay-skill-creator
/plugin install clay-skill-author@clay-skill-creator
```

**Uninstall before installing.** There are two caches — the marketplace's local clone of this repo,
and the installed copy — and refreshing the first does not replace the second. Updating alone can
leave you running the old version while the clone reports the new one, which reads as the update
having failed when it half-succeeded.

**A run from a stale version is not evidence about the current one.** Check the announce line before
concluding anything is broken; behaviour we have already changed will otherwise look like a live
defect.

**Two prompts, not one.** Install is a separate job from doing the work, and trying to make one line
do both is what kept failing:

```
1.  Set up the Clay skill creator by following the steps in
    https://github.com/sungwanjo-clay/clay-skill-creator

2.  Create a Clay GTM skill
```

**Which surfaces support which path, and which we have actually run:**

| Surface | Interview → skill | Table → skill | Install verified |
|---|---|---|---|
| Claude Code | yes | yes | **yes** — marketplace add, plugin install, skill loaded by name |
| Codex CLI | yes | yes | **not yet** — the manifest is declared, the install is untested |
| Cursor | yes | yes | **not yet** — same |
| Codex web app | yes | **no** — no terminal to install the plugin, and no network for the CLI to fetch its binary | n/a |

**Why that column exists.** Three plugin manifests are declared and one host has been verified. A
declared manifest is not a working install — that is the same mistake as trusting an action's
described inputs over its schema, and it has cost us four times. If a host in that list fails for you,
it is news rather than a known state; the other hosts are unaffected, and the interview path needs no
plugin at all.

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
