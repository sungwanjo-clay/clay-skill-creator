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

**[`START-HERE.md`](START-HERE.md)** — the whole flow in seven steps. If you are pasting a link to
someone, paste that one.

The rest is reference, in the order you will want it:

1. [`PREREQUISITES.md`](PREREQUISITES.md) — get the Clay CLI and authenticate. **If you have Clay's
   MCP server configured, you do not have the CLI** — they are different things, and that is the most
   common way setup fails silently.
2. [`workflows/table-to-skill.md`](workflows/table-to-skill.md) or
   [`workflows/interview-to-skill.md`](workflows/interview-to-skill.md).
3. [`PACKAGE-LAYOUT.md`](PACKAGE-LAYOUT.md) — what a package may and may not contain.
4. [`VALIDATION.md`](VALIDATION.md) — check it locally before you submit.
5. [`SUBMITTING.md`](SUBMITTING.md) — the form.

Worked outputs live in [`examples/`](examples/): a single-file skill, a multi-file skill, and one
showing what a **low-yield** table produces when there is not enough in it to convert.

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
