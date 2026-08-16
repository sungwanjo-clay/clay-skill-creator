# Prerequisites

Required for the table path. Not needed if you are answering the interview from scratch.

## 0. If you have Clay's MCP server, you do not have the CLI

These are different things, and having one gives you nothing toward the other:

| | What it is | What it gives you |
|---|---|---|
| **Clay MCP server** | Clay tools available inside a chat client | tool calls in a conversation |
| **Clay CLI** | a `clay` executable on your `PATH` | a terminal command |

This flow needs the terminal command. Stated first because it is the most likely silent failure in
the whole setup: everything looks configured, and then a documented command reports
`clay: command not found` with nothing explaining why.

## 1. Get the CLI — Claude Code, Codex and Cursor all work

Check whether you already have it:

```
clay --version
```

A version string means you are done — skip to step 2. If you already have it but a command reports
`upgrade_required`, run `clay update`.

If `clay --version` prints nothing, install the **Clay agent plugin**, which bundles the CLI and
supports all three hosts. The install differs per host; everything after it is identical, because the
plugin ships one `clay` launcher shared by all of them.

| Host | Install |
|---|---|
| **Claude Code** | `/plugin marketplace add clay-run/agent-plugins` then `/plugin install clay@clay-plugins` (needs Claude Code v2.1.91+) |
| **Codex** | `codex plugin marketplace add clay-run/agent-plugins`, then install **clay** from the Plugins panel |
| **Cursor** | do **not** hand-copy into `~/.cursor/plugins/local/` — org policy can block sideloading silently. Clone the marketplace and follow the bundled `setup` skill, which reads the effective policy and picks a path that works |

Clay's own instructions are the source of truth and are written to be handed to an agent:
**<https://github.com/clay-run/agent-plugins/blob/main/GETTING_STARTED.md>**. Read that rather than
trusting this table if the two ever disagree — this file is a pointer, not a second copy, because two
copies of an install procedure drift and the stale one is the one you will find.

After installing, run the plugin's bundled **`setup` skill** (`clay:setup`, or locate its `SKILL.md`
and follow it as a runbook). It puts `clay` on `PATH` and signs you in. On Codex and Cursor this step
is not optional: neither host adds a plugin's `bin/` to `PATH` on its own, so `clay` stays
"command not found" until `setup` writes the forwarder.

## 1b. Preflight: check the table path is open to you before you spend anything

**Do this immediately after signing in, before reading any table.** The three commands the table path
needs are served by Clay's public observability API, and the CLI's own help says that API is
**enabled per workspace and available on Enterprise plans**. If your workspace does not have it, all
three return `auth_forbidden` (exit 3).

```
clay whoami                                                   # read your user id out of the JSON
clay tables list --limit 1 --filter owner.id=<that id>; echo "exit=$?"
```

If you have `jq`, that collapses to one line — but `jq` is not a requirement of this flow, so the
two-step form above is the one to follow if you do not:

```
clay tables list --limit 1 --filter owner.id="$(clay whoami | jq -r .user.id)"; echo "exit=$?"
```

| exit | What it means |
|---|---|
| **0** | the table path is open. Continue. |
| **3** | `auth_forbidden` — either your key lacks the `cli:all` scope or the observability API is off for this workspace. **The table path is closed to you; take the interview path**, which needs none of this. |
| **5** | a network problem, not a permission one. Retry; do not re-run sign-in. |

This is one scoped, free call and it is deliberately placed *before* the cost paragraph below. The
worst version of this flow is one where you spend half an hour on setup and find out at the last
command that your plan never included the thing you installed it for. It also doubles as a
demonstration of step 2 of [`START-HERE.md`](START-HERE.md): note that even the preflight passes the
owner filter.

## 2. Authenticate into your own workspace

```
clay login
clay whoami
```

`clay whoami` must return your user id. That id is what scopes every table read — see step 2 of
[`START-HERE.md`](START-HERE.md), which is the one step in the flow that cannot be undone by
repeating it.

`clay login` pins the session to whichever workspace you pick on the consent screen. If the table you
want lives in another one, run `clay login` again and pick that one. No need to log out first.

## 3. What this costs

Reading table configuration is **free** — no credits, no action runs, no enrichment. The commands
this flow uses are metadata reads.

## Why the CLI is required, stated plainly

It is a real cost and worth naming rather than pretending otherwise: if you live in Clay's UI rather
than a terminal, install plus authentication is 15–30 minutes before you convert anything, and that
filters out some of the people this is most for.

Two honest answers. **The interview path needs none of it** — if the setup is not worth it, you can
reach a finished skill from a conversation alone. And the CLI requirement is about *transport*, not
about the conversion: if an in-product path arrives later, the same conversion runs behind it and
nothing you learn here is wasted.
