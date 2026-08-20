# clay-skill-creator

Turn what you already built in Clay — a table, or just an idea in your head — into a **portable
Clay skill** you can submit to the Marketplace.

A skill is a single Markdown file (`SKILL.md`) plus optional supporting files. It describes a
repeatable job in enough detail that someone else's agent can run it in *their* workspace, with
their own data and their own credentials. That last part is the whole design constraint: a skill
that only works in your workspace is not a skill, it is a note to yourself.

## Two ways in

| | Start from | Use when |
|---|---|---|
| **Table → skill** | an existing Clay table | you already built the thing and want it packaged |
| **Interview → skill** | a conversation | there is no table yet, or the table has little recoverable logic |

Both end the same way: a finished `SKILL.md` **you review**, then upload or paste into the
Marketplace form yourself. Nothing is submitted automatically, and there is no API that submits on
your behalf.

## Start here

**[`START-HERE.md`](START-HERE.md)** — install, sign in, then create the skill. If you are pasting a link to
someone, paste that one.

The rest is reference, in the order you will want it:

1. [`PREREQUISITES.md`](PREREQUISITES.md) — install and authenticate, on **Claude Code, Codex or
   Cursor**. It does not restate Clay's procedure; it links
   [Clay's own](https://github.com/clay-run/agent-plugins/blob/main/GETTING_STARTED.md) and hands you
   to the plugin's `setup` skill. One `clay login` covers both the `clay` command and the Clay MCP
   server. It adds only the two steps that are ours: confirm your workspace, and **preflight** whether
   the table path is open to you — one free call, before you spend anything on setup.
2. [`workflows/table-to-skill.md`](workflows/table-to-skill.md) or
   [`workflows/interview-to-skill.md`](workflows/interview-to-skill.md).
3. [`PACKAGE-LAYOUT.md`](PACKAGE-LAYOUT.md) — what a package may and may not contain.
4. [`VALIDATION.md`](VALIDATION.md) — check it locally before you submit.
5. [`SUBMITTING.md`](SUBMITTING.md) — the form.

**This repo is an installable plugin.** Two commands, and nothing needs to be fetched at runtime:

```
codex plugin marketplace add sungwanjo-clay/clay-skill-creator      # or /plugin marketplace add … in Claude Code
```

then install **`clay-skill-author`**. The skill lives at
[`plugin/skills/clay-skill-author/`](plugin/skills/clay-skill-author/) — the whole flow, its own
validator, the worked examples. Reading it is the fastest way to see exactly what the flow does.

## Two places to read finished skills, and they are not the same thing

**[`skills/clay/`](skills/clay/) is the library** — thirty skills, the format demonstrated rather than
described. Same shape a submission takes (`skills/<creator>/<skill>/`), so ours carry no special case.
If you want to see how a declared-inputs table is written, or how a skill states what it does *not*
claim, read a few of these: four examples tell you the rules and thirty show you the range.

**[`examples/`](examples/) is a curated teaching set** — three of those thirty, picked for the quality
of the reasoning rather than to cover package shapes, plus one that exists nowhere else: a **low-yield**
case, showing what an honest skill looks like when the source table did not hold enough to convert.
That fourth one is the reason this directory survives alongside the library.

Both are generated from the same source, so they cannot disagree. Internal evaluation records
(`EVAL.md`) are excluded from everything published here.

## If your agent cannot read this repository

The one-liner in [`START-HERE.md`](START-HERE.md) hands your agent a GitHub link, and some sandboxes cannot fetch one — no outbound
network, or a blob page it cannot parse. **Then tell it to fetch the raw file instead:**

```
curl -fsSL https://raw.githubusercontent.com/sungwanjo-clay/clay-skill-creator/main/START-HERE.md
```

That is a different mechanism from a `git clone` or a web search, and it is the one that works when
those fail. If it also returns nothing, the sandbox has no egress at all — then **install the skill
instead of fetching the docs**: `clay-skill-author` carries this whole procedure, its own validator
and the worked examples, and loads from disk with no network. See `SUBMITTING.md`.

**The tell that your agent gave up and improvised**: it names no files from this repository. Ask it
which files it read. If the answer is a confident plan with no filenames, it fell back to a generic
skill-creation workflow and whatever it produces will look right and be unrelated to any of this.

## Three things that will save you a rejected submission

**Your table's handles do not travel.** Column ids, table ids, saved-view names and auth-account
handles exist only in your workspace. Every one of them has to become a *declared input* the
installer supplies. The converter does this for you; the local validator catches what it missed.

**Numbers get checked against your formulas.** Any threshold the skill states is compared against
the formula it came from, and a mismatch stops generation. This exists because a transcription error
is invisible to the person best placed to catch it — your table ran in production, so a skill that
misquotes it still looks like it works.

**"Verified" is narrow, on purpose.** A generated skill carries `proof_status` and a list of
`proof_gaps` saying exactly what was and was not checked. A table-derived skill is always
`partial`: the comparison runs on your machine at generation time, the source formula does not
travel with the package, so nobody downstream can re-run it. That is a limit of the method, and the
skill says so rather than implying more.

## What this reads, and what it never touches

Table → skill reads **column configuration only**, scoped to tables you own:

```
clay whoami                              your identity
clay tables list --filter owner.id=<me>  your tables, never a bare list
clay tables columns list <tableId>       column ids, names, types
clay tables columns get  <tableId>       the recipe: formulas, prompts, input wiring
```

Those four commands are the entire surface. It never reads a row, never runs a column, never writes
anything, and never executes a Clay action. The list command is owner-scoped because a shared
workspace lists everyone's tables and table *names* alone can disclose customers and deals.

**Three of those four are served by Clay's public observability API, which the CLI's help states is
enabled per workspace and available on Enterprise plans.** If yours does not have it they return
`auth_forbidden` (exit 3) and the table path is closed to you — the interview path is unaffected and
reaches the same finished skill. `PREREQUISITES.md` step 1b checks this in one call, before you install
anything you would not be able to use.

## Licence

**MIT** — see `LICENSE`. Copy a skill, change it, ship it, sell it; keep the notice.

That applies to everything here, `skills/clay/` included. The thirty skills exist to be taken apart
and reused, and a corpus published as "read these" that grants no right to copy them would be an
invitation that is not one.

Nothing about the licence changes what you owe your own installers: a skill you write from these
still has to name what it runs, what it costs, and what it does not claim. That is a quality bar,
not a legal one.
