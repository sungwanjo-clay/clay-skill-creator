# Prerequisites

Required for the table path. **Not needed if you are answering the interview from scratch** — that
route needs nothing but a conversation.

## This file does not tell you how to install Clay. Clay does.

Setup is **Clay's own procedure**, run exactly as Clay documents it. There is no second version of
it here, on purpose: an install procedure written down twice drifts, and the stale copy is the one
you will find. Clay's is also simply better than a summary — it handles Cursor's org-policy traps,
the Codex `PATH` forwarder, and a troubleshooting table for symptoms this file would not think to
mention.

**Follow this, and nothing else:**
**<https://github.com/clay-run/agent-plugins/blob/main/GETTING_STARTED.md>**

That page is written to be handed to an agent — *"installing, putting `clay` on PATH, and signing in
are all things the agent can do on your behalf by following the steps below."* So paste the link to
your agent and let it work.

Two things from it worth knowing before you start, because they are where people stall:

**Installation differs per host; everything after it does not.** All three run the same bundled
`clay`.

| Host | Install |
|---|---|
| **Claude Code** | `/plugin marketplace add clay-run/agent-plugins` then `/plugin install clay@clay-plugins` — from *inside* Claude Code, no separate terminal (needs v2.1.91+) |
| **Codex** | `codex plugin marketplace add clay-run/agent-plugins`, then install **clay** from the Plugins panel |
| **Cursor** | Do **not** hand-copy into `~/.cursor/plugins/local/` — org policy can block sideloading silently. Clone the marketplace and follow the bundled `setup` skill, which reads the effective policy and picks a path that works |

**Then run the plugin's own `setup` skill, and do not skip it.** Clay: *"Once installed, run the
bundled `setup` skill now, in this session, before anything else."* It puts `clay` on `PATH`, signs
you in, and verifies the CLI works. Invoke it as **`clay:setup`**; if your host does not resolve
that, Clay gives you the fallback:

```
find ~/.codex ~/.cursor ~/.claude ~/.config -type f \
  \( -path '*/clay/skills/setup/SKILL.md' -o -path '*/clay/*/skills/setup/SKILL.md' \) 2>/dev/null | sort | tail -n1
```

Read the path that prints and follow it as a runbook.

**One login covers both surfaces.** `clay login` authenticates the CLI *and* the Clay MCP server —
the plugin registers `clay mcp` as the server and both read the same session from disk. You do not
choose between them and you do not authenticate twice. (Note the corollary: having Clay's MCP server
configured *separately*, without the plugin, does not give you the `clay` command.)

---

## When setup is done — the two things this file adds

Everything above is Clay's. These two are ours, and neither belongs in Clay's docs.

### 1. Confirm you are where you think you are

```
clay whoami
```

Must return a user id. Say which workspace out loud before reading anything — the owner filter in
the next step is derived from this id.

### 2. Preflight the table path before spending your time on it

```
clay tables list --limit 1 --filter owner.id=<the id from clay whoami>; echo "exit=$?"
```

| exit | Meaning |
|---|---|
| **0** | The table path is open. Continue. |
| **3** | `auth_forbidden` — the `clay tables` query surface needs API table sync, **available on Enterprise plans**. The table path is closed to this workspace; **take the interview path**, which needs none of this and reaches the same finished skill. |
| **5** | Network, not permission. Retry; do not re-run sign-in. |

Clay's own `tables` skill states the gate plainly: *"That's an account limitation, not a bug or an
auth problem — don't retry or re-login."* Finding out here costs one free call; finding out at the
last command costs the whole setup.

**A caveat we have not resolved.** The CLI's help for `tables columns get` cites *"the public
observability API"* while Clay's `tables` skill cites *"API table sync"*. Those may be two separate
Enterprise flags, which would mean reading columns and querying rows can fail independently. If your
preflight passes but `clay tables columns get` still returns exit 3, that is this — not a mistake you
made.

## What this reads, and what it never touches

```
clay whoami                              your identity
clay tables list --filter owner.id=<me>  your tables, never a bare list
clay tables columns list <tableId>       column ids, names, types
clay tables columns get  <tableId>       the recipe: formulas, prompts, input wiring
```

Four commands, all reads. It never reads a row, never runs a column, never writes, and never
executes a Clay action. Nor could it write if it tried: Clay's own docs are explicit that creating a
table, adding fields, inserting rows and updating cells are **not supported** through the CLI, MCP, or
the Public API — rows only enter through the Clay app.
