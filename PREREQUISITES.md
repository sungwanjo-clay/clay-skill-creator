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

## 1. Get the CLI

Check whether you already have it:

```
clay --version
```

A version string means you are done — skip to step 2. If you already have it but a command reports
`upgrade_required`, run `clay update`.

If `clay --version` prints nothing, the CLI is not installed. It is distributed by Clay, not from
this repository. If you use Claude Code with Clay's plugin, the plugin's `setup` skill installs and
authenticates it in one step, which is the shortest route. Otherwise ask in your Clay workspace for
the current install command for your platform — it changes, and a stale command in a file like this
one would be worse than none.

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
