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

**If your agent cannot open that page**, fetch the raw file — a blob page is the form that fails in sandboxes that cannot parse GitHub HTML:

```
curl -fsSL https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md
```

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

**`/plugin marketplace add` does nothing if you have added that marketplace before — and that is how
you end up on a version the server rejects.** It is not an update command. The clone it made the first
time stays at whatever commit it had then, so a marketplace added weeks ago keeps installing weeks-old
plugins, including a bundled `clay` older than the minimum the Clay server now accepts. The symptom
does not look like staleness: the CLI is present, it runs, it reports a version, and the server refuses
it anyway.

There are also **two** caches, and clearing one is not enough — the git clone `add` reads from, and the
unpacked install:

```
rm -rf ~/.claude/plugins/marketplaces/clay-plugins
rm -rf ~/.claude/plugins/cache/clay-plugins
```

Then add and install again. `ls ~/.claude/plugins/cache/clay-plugins/*/` tells you which version you
actually got — and if an old version directory is still sitting beside the new one, delete it, because
a stale registration can still resolve to it. (Nothing above is specific to Clay's marketplace; the
same two directories, under the same names, pin `clay-skill-creator` the same way.)

**Then run the plugin's own `setup` skill, and do not skip it.** Clay: *"Once installed, run the
bundled `setup` skill now, in this session, before anything else."* It puts `clay` on `PATH`, signs
you in, and verifies the CLI works. Invoke it as **`clay:setup`**; if your host does not resolve
that, Clay gives you the fallback:

```
find ~/.codex ~/.cursor ~/.claude ~/.config -type f \
  \( -path '*/clay/skills/setup/SKILL.md' -o -path '*/clay/*/skills/setup/SKILL.md' \) 2>/dev/null | sort | tail -n1
```

Read the path that prints and follow it as a runbook.

**One login covers both surfaces — but only when the server is the plugin's.** `clay login`
authenticates the CLI *and* the `clay mcp` server the plugin registers; those two read the same
session from disk, so you do not authenticate twice. (Corollary: having Clay's MCP server configured
*separately*, without the plugin, does not give you the `clay` command.)

**A separately-configured Clay connector is a different login, and the two can point at different
workspaces without saying so.** Measured: a CLI signed in to workspace `1349187` alongside a host
connector pinned to workspace `4515`, in one session, with nothing on screen noting the split. That
matters because this kit reads table *configuration* through the CLI while a skill you build may later
run enrichments through the connector — so a schema read from one workspace can end up driving work in
another. **Check both and name both out loud** before you trust either:

```
clay whoami                      # the CLI's workspace
```

and ask your host which workspace its Clay connector is on. If they differ, decide which one you mean
and fix the other before reading a single column.

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
| **3** | `auth_forbidden` — an account-level limitation on the `clay tables` surface. **We do not know what enables it**, and it is NOT a plan tier — see below. The table path is closed to this workspace; **take the interview path**, which needs none of this and reaches the same finished skill. |
| **5** | Network, not permission. Retry; do not re-run sign-in. |

Clay's own `tables` skill states the gate plainly: *"That's an account limitation, not a bug or an
auth problem — don't retry or re-login."* Finding out here costs one free call; finding out at the
last command costs the whole setup.

**A correction, because this page said "Enterprise" and that was wrong.** An earlier version of this
table attributed exit `3` to API table sync being *"available on Enterprise plans"*. That claim came
from Clay's own `tables` skill rather than from a test, and a test refuted it.

**Measured on a brand-new, non-onboarded workspace on the lowest tier** — all four commands returned
exit `0`:

```
clay whoami                                        0
clay tables list --limit 1 --filter owner.id=<me>   0   (returned the starter table)
clay tables columns list  <tableId>                 0   (5 columns)
clay tables columns get   <tableId>                 0   (formulas AND input bindings)
```

`columns get` returned the recipe in full — `formula: {{Enrich Company}}.url`,
`input binding: company_identifier ← {{Domain}}` — which is exactly what this kit reads. **So the
table path is not plan-gated at the bottom of the range, and the previously unresolved caveat about
"two separate Enterprise flags" is resolved: both surfaces were open on the same workspace.**

**`Query enabled: false` is not the gate either.** The starter table reported that flag and
configuration reading worked anyway. It appears to govern querying *rows*, which this kit never does.
Seeing it is not a reason to stop.

What we still do not know: exit `3` is real — Clay's `tables` skill documents it as *"an account
limitation, not a bug or an auth problem — don't retry or re-login"* — but **nothing we have tested
tells us what turns it on.** So the row above says "account-level limitation" and names no tier. If you
hit exit 3, it is not a mistake you made and not something re-authenticating fixes; take the interview
path.

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

## Getting the current version, once it is installed

**Nothing updates on its own.** Plugin auto-update is off by default for third-party marketplaces, so
an install stays on whatever version it fetched until you replace it — and the symptom is a run that
behaves like an older document than the one you are reading.

**READ IT OFF DISK. Do not trust the announce line, and do not read it off the path.** Both have
been observed lying, on the same run:

```
find "$HOME/.claude" -path '*clay-skill-author*' -name SKILL.md \
  -print -exec grep -m1 -o 'clay-skill-author/[0-9.]*' {} \; 2>/dev/null
```

**It searches rather than naming a path, and that is the point.** The first version of this check
hardcoded the install path, which is the fourth verification method here to break on a layout that
moved — after an `ls` of a cache directory that stopped existing, a version segment that left the
path, and the announce line. **Anything that describes the install can drift; the file cannot.**

**And the output is the diagnosis: a path, then the version in it, per copy.** `-print` is there
because the first version of this printed versions alone, and a creator holding a stale version with
no path had nothing to act on. Two pairs means two installs, which is the case that keeps people on
an old version: a global install and a marketplace one, where removing the second leaves the first
running. One pair naming the version you expect is the pass. No output means nothing is installed,
which is also the right answer immediately after an uninstall.

**The announce line can name a version the agent is not running.** Watched on a real install: asked
to follow a link, the agent fetched this repository, read the version there and announced it, with the
literal `…` from this page's path placeholder still in the line because it had copied the example
rather than filled it in. Its next line, printed after opening the installed file, said a version two
releases older. **That number is evidence about whatever the agent last read.**

**THERE ARE TWO LOCATIONS AND THEY MEAN DIFFERENT THINGS.** This is why the search beats any path
you could be handed:

```
~/.claude/plugins/marketplaces/clay-skill-creator/plugin/skills/…   the repo clone. No version in the path.
~/.claude/plugins/cache/clay-skill-creator/clay-skill-author/<version>/skills/…   the INSTALLED copy.
```

**The second one is what runs, and its version is a path segment.** So a stale install is visible
from the path — but only that path, and an earlier draft of this section denied it after checking the
other one, where the segment genuinely is absent. Both statements were half right and neither was
usable, which is the argument for reading the file instead of reasoning about where it lives.

**Removing the marketplace does not remove the cache.** Observed: the clone was gone, every
documented uninstall reported success, and a two-release-old copy under `plugins/cache/` was still
the one loading. If the search finds a version you did not expect, delete that marketplace's cache
directory outright and reinstall:

```
rm -rf "$HOME/.claude/plugins/cache/clay-skill-creator"
```

To move:

```
/plugin marketplace update clay-skill-creator
/plugin uninstall clay-skill-author@clay-skill-creator
/plugin install clay-skill-author@clay-skill-creator
```

**Uninstall before installing.** There are two caches — the marketplace's local clone of this repo,
and the installed copy — and refreshing the first does not replace the second. Updating alone can
leave you running the old version while the clone reports the new one, which reads as the update
having failed when it half-succeeded.

**AND A GLOBAL INSTALL IS A THIRD PLACE.** Observed: after adding the marketplace fresh, `/plugin
install` answered *"already installed globally"* and the run stayed on the old version — a
marketplace-scoped uninstall does not reach a global one, so the sequence above completes and changes
nothing. On that message, open `/plugin`, remove it there, then check the version off disk.

**A run from a stale version is not evidence about the current one.** Check the version off disk
before concluding anything is broken, or behaviour we already changed reads as a live defect.
