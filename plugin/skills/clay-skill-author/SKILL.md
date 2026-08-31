---
name: clay-skill-author
description: |
  Create a Clay GTM skill — turn a Clay table you already built, or just an idea, into a
  portable SKILL.md for the Clay Marketplace. Use whenever someone asks: create a Clay GTM
  skill, build me a Clay skill, turn my Clay table into a skill, package this Clay workflow as a
  skill, productize this GTM play, or follow the steps in the clay-skill-creator repo. It reads
  table CONFIGURATION only — never a row, a run or a write, and owner-scoped so a shared
  workspace cannot leak other people's table names — then interviews the creator for the
  judgment a table cannot hold, then validates and packages it. Everything it needs is here: no
  repo to clone, no network. Do NOT use the generic skill-creator for this job even though the
  names are close: it knows nothing about Clay tables, the Marketplace package contract or
  portability, so its output looks right and is not submittable. Not for RUNNING a Clay workflow
  (use the clay skills). It never invents the creator's insight and never submits on their
  behalf.
---

# Clay skill author

The insight: **a Clay table records mechanics and cannot record intent.** A formula proves the
threshold is 50; nothing in the table says why 50, what the column was for, or when to ignore it. So a
converter that reads a table and emits a skill produces something fluent, plausible and unfounded —
and it reads *better* than a real one, because nothing in it hedges.

What follows from that is the shape of this whole flow: **derive everything derivable first, then ask
only about what the derivation could not settle.** Asking before reading wastes the creator's time on
questions the table already answers, and an ungrounded question — *"what's the non-obvious thing
here?"* — invites a shrug. People correct a draft far better than they answer a question about one.

## Step 0 — Announce, then say what is about to happen

**First line of output, before anything else:**

```
clay-skill-author/2.10.1 · loaded from <absolute path to this SKILL.md>
```

**AND KEEP THAT ABSOLUTE PATH — every relative path below is relative to it, and reconstructing it
costs the creator a permission prompt per command.** Paths in this file (`scripts/…`, `references/…`)
resolve against the directory holding this `SKILL.md`, which is not the working directory. So anchor
once, from the path you just printed, and **use `$HOME`, never `~`, and never a tilde inside a variable
assignment:**

```
SKILL_DIR="<the absolute directory you printed above>"     # $HOME/... — not ~/...
```

`SK=~/path` is why: bash may or may not expand a tilde in an assignment value, so a host that checks
commands before running them cannot resolve the path and asks the creator to approve it. Measured on a
real run — a creator approving the same shape repeatedly, once per command, through a whole build. It
reads as the tool malfunctioning. `"$HOME/path"` resolves statically and never prompts.

Then two or three sentences on the shape of the next few minutes. Do not wait for permission — this is
orientation, not a gate.

> "I'll ask one question about where you're starting from, then write you a complete draft and show it
> to you to correct before anything is final. If we're working from a Clay table, I'll read its settings
> only — no rows, no runs, no writes."

**It must not promise work the route may not involve.** This opened for a while with *"I'll get Clay set
up if it isn't already, then read your table's configuration"* — announced before anyone had been asked
whether a table existed. On the from-scratch route that describes work which never happens, and the
first thing the creator hears is a claim the tool does not keep.

## Step 1 — Route: one question, four answers

> **Where are you starting from?**

| Answer | Route |
|---|---|
| **From a Clay table** | Step 2 |
| **From scratch** | `references/interview-to-skill.md` — no Clay setup, no table, no preflight — then back here for Steps 8 and 9 |
| **I already have a `SKILL.md`** | Step 8 — validate and package, then Step 9; needs no Clay setup either |
| **Show me my tables** | Step 2, then list their tables, flag which have formulas **and** prompts, re-ask |

**THE ROUTE IS ASKED BEFORE ANYTHING IS SET UP.** Clay setup used to run first, unconditionally, and
two of these four routes never touch Clay. Measured on a real from-scratch run: a repo clone, a
`which clay`, a `clay whoami`, one permission prompt and about two minutes — after which the agent
itself observed that *"interview path needs no Clay CLI, so the rejected commands cost us nothing."*
It knew, one step too late. **Setup that the answer might make unnecessary comes after the answer.**

Nothing about what the creator sees changed here: same question, same four rows, same order. Only the
setup moved.

**THE QUESTION ENUMERATES NOTHING. THIS TABLE IS THE OPTION LIST.** Corrected after watching a real
run: the host renders these rows as a picker, and it appends its own **Other** row for free-text. So
a question that also spells the options out puts them on screen twice and competes with the picker.

An earlier fix here did exactly that, on the theory that an option missing from the question is an
option nobody picks. That theory was wrong on this host — the picker had always shown all four,
because it reads this table. What the creator actually reported was five options with two of them
meaning the same thing: `Not sure — show me` sitting next to the host's `Other`, both reading as
*I don't know*. Hence the relabel: **`Show me my tables` promises an action**, which is what
distinguishes it from an escape hatch that promises nothing.

Keep the question to one short line. If a host has no picker, the agent still has this table and
will read it out — that case never needed the question to duplicate it.

`I already have a SKILL.md` is not "upload a skill you already have". Nothing is uploaded on that
route — it goes to Step 8, which validates and packages, and then to Step 9. Naming the action wrong sends a creator
looking for a file dialog that does not exist and hides the check that does.

The fourth answer is the most common real state and must not be a dead end. Flagging is free: a table
with neither formulas nor prompts is knowably thin before the creator invests anything.

**And it has to survive `auth_forbidden`.** `Show me my tables` promises a table listing, which the
Step 2 preflight can refuse with exit `3` on some accounts, for reasons we cannot name. When that happens,
say the listing is unavailable on this workspace and move to the interview — never leave a creator
who asked to be shown their tables looking at a failure they did not cause and cannot fix.

### When the answer is already in front of you, state the route — do not re-ask it

Sometimes the route is settled before the question: the creator opened with a full written spec, or
named a table, or pasted a `SKILL.md`. Asking anyway is the friction this flow exists to remove, and
Step 6's rule — *a question is allowed only if the answer changes what gets written* — says not to.

**So infer it, and say which one you took, in one line, with the correction attached:**

> "Treating this as **from scratch** — you gave me a complete spec, so there's no table to read. Say
> *table* if you'd rather convert one."

Not a question, not a picker: a handle. Watched failing in a real run, where the route was inferred
correctly and never mentioned, so the creator had no cheap way to redirect and would have discovered
a wrong guess only after a full draft existed. **Guessing right is fine; guessing silently is not.**

## Step 2 — Set Clay up (table routes only)

Reached from **From a Clay table** and **Show me my tables**. The other two routes skip this step
entirely — do not run any of it "just to check".

```
clay whoami          # exit 0 with a user id? go to the preflight below
```

**Plugin installed but signed out?** Its bundled `setup` skill does PATH and sign-in in one step.
Check first, because that skill only exists once the plugin does:

```
find ~/.codex ~/.cursor ~/.claude ~/.config -type f \
  \( -path '*/clay/skills/setup/SKILL.md' -o -path '*/clay/*/skills/setup/SKILL.md' \) 2>/dev/null | sort | tail -n1
```

Something printed → run `clay:setup`, or follow the `SKILL.md` that printed. **Nothing printed → no
plugin. Install it:**

```
Claude Code    /plugin marketplace add clay-run/agent-plugins
               /plugin install clay@clay-plugins

Codex CLI      codex plugin marketplace add clay-run/agent-plugins
               then open Plugins and install clay

Cursor         do NOT hand-copy into ~/.cursor/plugins/local/ — org policy blocks sideloading
               silently. Use Clay's setup skill.
```

Then `clay login` (browser once) and `clay whoami`. One sign-in covers the CLI and the `clay mcp`
server **the plugin registers** — but a Clay connector configured separately in the host is a
different login, and the two can sit on different workspaces with nothing on screen saying so
(measured: CLI on `1349187`, host connector on `4515`, same session). **So name the workspace the CLI
reports, and if the host has its own Clay connector, check that it agrees before reading a column.** Some hosts need a restart before a new plugin registers. If any of it fails, Clay's procedure
is authoritative and carries what moves — version pin, Cursor policy, `PATH` forwarder,
troubleshooting:

```
curl -fsSL https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md
```

If that fetch returns nothing the sandbox has no network, so the CLI cannot download its binary and
**the table path is unavailable here** — say so and go to the interview path.

**Do not continue until `clay whoami` returns a user id.** Then say which workspace, out loud.

**Preflight before any table work**, because the surface is gated:

```
clay tables list --limit 1 --filter owner.id=<id from clay whoami>; echo "exit=$?"
```

`0` open · `3` `auth_forbidden`, an account-level limit whose trigger is unknown and **is not a plan
tier** — **the table path is closed, go to the interview and never mention tables again** · `5`
network, retry.

**Do not tell the creator this needs Enterprise.** It was written here as fact and it is false:
measured on a brand-new non-onboarded workspace at the bottom of the range, `tables list`,
`columns list` and `columns get` all returned `0`, recipes and input bindings included. A `3` is
something about that account we cannot name, so name nothing.

## Step 3 — Confirm the table, and state the boundaries first

List owner-scoped tables, name the one they mean, and get a yes. Before reading, say plainly, in one
short paragraph:

- this reads **column configuration only** — never a row, never a run, never a write;
- **no credential and no personal detail will be repeated back**, in whole or in part;
- workspace-specific handles become **declared inputs** the installer supplies, never literals.

**RULE 0 — the owner filter goes on the first call, always.** An unscoped `clay tables list` is
workspace-wide, and table *names* encode customers and deals. **Reading is the irreversible part, not
filtering** — narrowing afterwards does not unsee them.

## Step 4 — Read the configuration

**RULE 0b — these four commands and no others.**

```
clay whoami
clay tables list --filter owner.id=<me>
clay tables columns list <tableId>
clay tables columns get  <tableId>
```

`clay tables rows` is their data and is never needed. `clay tables update` is a **write** despite how
it reads. Read **prompts first** (intent), **formulas second** (mechanics), **names last** (evidence of
nothing). Never infer a step, threshold or purpose from a column name. Detail: `references/table-to-skill.md`.

**If a credential is in the configuration**, reading it was unavoidable; what follows is a choice.
Never print any part of it, truncated or not. One sentence inline, no warning banner. Never instruct
rotation — you cannot see what that key touches, so the decision is theirs. No unsolicited debugging of
their table.

## Step 5 — Derive the complete draft, before asking anything

```
python3 scripts/derive_recipe.py derive <tableId>
```

Write a **complete** `SKILL.md` to `build/<slug>/` — not an outline, not a plan. It must carry a
**`## Declared inputs` section**: a three-column table of every value the installer supplies — the
input, what they supply, and what happens if it is missing. That section is what makes the skill
portable, and it is the only body section a submission is required to have. All four worked examples
model it.

**A file you name, you write — in this step, before anything else happens.** If the draft says *copy
`references/node-code.md`*, that file exists on disk by the end of Step 5. If you are not going to
write it, inline the content and name no file. **Never emit a reference to something that does not
exist yet.**

Observed end to end: a draft named a `references/` file that was never created, the creator asked for
"just the SKILL.md", and an installer three hops later hit an instruction to copy a file that exists
nowhere. The draft was broken the moment it was written, and everything downstream inherited it. A
promise the next step has to keep is a promise the creator can walk away with unkept — and asking for
the main file is the most natural thing they will do.

Two nets catch this later and neither is a substitute: `package_skill.py validate` blocks on it in
Step 8, and `submit_skill.py` refuses to send it. Both sit *after* the point where a finished-looking
file exists.

**And the draft has to be able to READ one, or writing it accomplishes nothing.** Emitting a sheet and
shipping a skill that ignores it produces a file the next person deletes: they run the skill, it asks
them everything anyway, and the sheet is dead weight. This was measured — the flow wrote sheets and no
generated skill loaded one — so the instruction goes IN THE BODY, in the step that collects the
definition, and it says three things:

> **If an answer sheet is present beside this skill, load it and ask only for what it does not
> cover.** A partial sheet is normal; a value it is missing gets asked for on its own rather than
> restarting the interview. **Say which values came from the sheet** before using them — a sheet
> applied silently is a wrong field nobody catches. **If there is no sheet, say nothing about
> sheets** — run the interview as though the feature did not exist. At delivery, offer to save the
> answers back, in words that explain the offer rather than naming it.

**And SAY WHAT THE FILE IS, because "in words that explain the offer" was not enough — a creator got the
offer, accepted it, and still asked what the file was for.** Four beats, in this order: it is not part
of the skill · what it holds · what it saves them · what it lets a colleague do. Then the line about
credentials, which is not optional. Something close to:

> "Want me to save your answers to a file alongside this?
>
> It isn't part of the skill — it's a short note of what you told me: your CRM, the field names, the
> thresholds you picked. Two reasons to keep it. **You** never answer these questions again when you
> re-run this. And if you **send it to a teammate** next to the skill, the skill reads it and asks them
> only what the file doesn't cover — so they can run your work without knowing your setup.
>
> It stays with you: never submitted, never published, and it holds no passwords or API keys."

Adapt the wording; keep all five beats. **The credential line is the one that stops someone pasting a
key into it** — and if a creator offers one anyway, refuse it and say why, per the rule above.

**Two clauses in there are about the installer who has never heard of an answer sheet, and they are
the difference between a feature and an irritation.** The check is a file lookup, not a question, so
someone without a sheet is never asked for one — but nothing stopped a draft from *announcing the
absence*, and "I couldn't find an answer sheet, so I'll ask you directly" introduces a concept only to
report it missing. Hence **silent when absent**.

The exposure is at the *end*, not the start: the save-back offer fires for everyone, including the
first-timer who just answered nine questions and has met no such term. Keep the offer — that person is
exactly who benefits — but make it self-describing. *"Want me to save your answers to a file, so the
next person on your team doesn't have to answer these again?"* needs no glossary. *"Shall I write an
answer sheet?"* earns a "what?".

**It skips questions. It never skips a gate.** The batch, the cost and the write approval are runtime
and still run: somebody working from a sheet is answering fewer questions, which makes them exactly
the person who most needs the pause. A draft that lets a sheet suppress a gate is the four-halt
defect arriving from the other direction.

**Every draft names the SHAPE of its output — the columns, or the fields per item — and shows two or
three rows of obvious placeholders.** Not the values: a shape.

```
| Rank | Account | Renewal in | Signals fired | Evidence |
|---|---|---|---|---|
| 1 | Northwind | 21 days | champion moved · headcount fell | champion now VP at a competitor; 512 → 470 |
```

**This is the highest-leverage paragraph for how the skill LOOKS on the marketplace, and it was
measured rather than assumed.** Two published skills, same renderer, same day: the one carrying a table
like the above got that table rendered on its page, columns and all. The one that described its output
in prose only got a generated sentence — *"a plausible candidate list based on the defined criteria"* —
which says nothing the outputs field had not already said. The difference was entirely whether the
skill named a shape.

**Placeholders, never real values.** `Northwind` and `Contoso` are transparently invented, which is the
point: three rows show the columns, real rows bloat the file and ship whatever the creator's data
happened to be. If the output is a list rather than a table, name the fields per item the same way.

**BUT A PLACEHOLDER IS A CELL, NEVER A WHOLE DELIVERABLE. When the output is prose — a brief, a
summary, a recommendation, a memo — the shape rule inverts: show ONE FILLED INSTANCE.** This was
measured too, and it is the failure this clause exists to stop. A skill whose output section was a
bracketed skeleton — `**Quick finding:** [1–2 paragraphs…]`, `**Title tag (~N chars):** \`[title]\``,
`**[Existing section name]** — [one line of guidance]` — had that skeleton rendered on its marketplace
page verbatim, brackets and all. The renderer did exactly what it was told: it found a shape and
re-rendered it. The shape was an empty form.

**`Northwind` in a table cell reads as a placeholder because the column header beside it carries the
meaning. `[title]` in a prose brief carries nothing** — the sentence around it was the meaning, and it
is the part that got left out. So:

| Output is | Show | Because |
|---|---|---|
| a table or a per-item list | headers plus two or three placeholder rows | the headers are the content; the cells are interchangeable |
| prose, a brief, a narrative | one worked instance, written out, with plausible-shaped numbers | the prose *is* the content and a blank frame demonstrates nothing |

For the prose case, invent the numbers — `426 clicks against 6,218 impressions, holding position 1` —
but keep the subject transparently fake, the same contract as `Northwind`. **A creator who has a real
example of the output they want should hand it over and have it written in, generalised: their figures
are the fastest way to show an agent what "good" looks like, and the second-fastest is nothing.**

**AND IF THE OUTPUT RANKS ANYTHING: A CAVEAT BESIDE THE NUMBER DOES NOT CHANGE THE NUMBER.** Watched on
a live run of a scoring skill, and it is the most reader-hostile failure an honest skill can produce.
The deliverable was scrupulous in prose — *"current role has moved off paid onto web/CRO"*, *"paid
social, not paid search"*, *"19 years in and titled Principal, likely over-level"*, *"her about section
says four years, below the floor she was filtered on"* — and **every one of those still sat in the top
band, ranked by a score the caveat had not touched.** Nothing was hidden and nothing was corrected.

**A reader going down a ranked table acts on the order.** They contact rows one, two and three; the
evidence column is what they read *after* deciding, if at all. So a caveat that would change who gets
contacted has to live where the decision is made:

- **In the sort** — it lowers the score, and the weights say why.
- **Or in its own bucket** — the way a thin profile or a mismatched identity already gets one, kept out
  of the ranking entirely rather than ranked with an asterisk.
- **Never only in prose beside the rank.** If it does not move the row, it is a footnote on a
  recommendation the skill is still making.

The tell that this is happening: **the draft's own evidence line contradicts its own band.** Write the
check in: any row whose evidence names a mismatch with a stated criterion is either rescored or
bucketed, and a skill that finds itself explaining why its top pick does not fit the brief has found a
scoring bug, not a nuance. **And check the weights against the words the creator used** — the run above
weighted the brief's own headline phrase fourth out of five, which is how an off-discipline candidate
clears the bar honestly.

**Every draft carries a `## What this skill touches` section — Reads, Writes, Never — and the
validator looks for it.** Three labelled lines, all three named even where the answer is one word.
Write `Writes: nothing` explicitly when the play only reads; it is the most reassuring line a
read-only skill has and leaving it implied throws it away. Derive it from the steps you just drafted
rather than asking the creator: you know what the play reads and writes, because you wrote it.

**Decide the shape before the steps, and derive it from the job rather than defaulting to it.** Two
shapes exist — call the functions, or build a workflow — and `DETERMINISM.md` names two forcing
conditions for the second: **something has to run when no agent is present**, or the volume and cadence
exceed what one conversation can hold.

**It has been going unasked, and the number says so.** Across 36 published skills, five build a
workflow — and two more, `inbound-triggers-monitor` and `hiring-radar`, are monitors by name and call
functions in fact. A skill whose whole job is to notice something next Tuesday, drafted as a loop that
only runs while a person is in the conversation, does not do its job; it does its job once. The forcing
condition was written down and never asked, which is a different defect from a wrong default and has a
cheaper fix.

**Put it to them as one thing: who starts it — them, or a signal?** That is the forcing condition in
words a creator already owns. `no agent present`, `unattended` and `cadence` are all our vocabulary for
it, and a creator reading any of them has to decode before they can answer.

> **Who starts this — you, or a signal?**
>
> - **You** — *`<what they would do to ask for it>`*  ← *assuming this*
> - **A signal** — *`<the event that would fire it instead>`*
>
> Say *signal* to flip it.

**BOTH BRANCHES ARE WRITTEN FROM THE SKILL IN HAND. Neither is boilerplate, and reusing the examples
below is the specific way this goes wrong.** The point of the pair is that it is one skill described
twice, so nothing needs defining — both halves are already things the creator wants. Told about
somebody else's skill, they learn that the tool is reading from a script:

| If the skill is… | **You** | **A signal** |
|---|---|---|
| writing cold-email openers | you paste a list and ask for openers | a new job posting appears, and the opener is waiting |
| deduping a CRM | you point it at an export when it feels messy | a record lands and it checks for a twin on the way in |
| tracking champion job changes | you ask which champions moved this quarter | a title changes and you hear about it that day |

**Name no other skill in this message.** `hiring-radar` explains the distinction perfectly to us and
means nothing to a creator who has never seen the library — it spends their attention on a thing they
now feel behind on. Their own skill is the only example that needs no introduction.

**Then state the shape you chose and why, in one line, and let them correct it.** A creator corrects
that line instantly if it is wrong, which is the whole reason it is a statement with a handle rather
than a question. **It is not one of Step 6's three.**

**A workflow is the right shape and the rougher road, so choose it with your eyes open.** The node
defects in `DETERMINISM.md` are measured, not cautionary: an asymmetric merge node stays pending
forever, a tool node does not echo its own inputs, a pin two hops back resolves to null. Where the
cadence forces a workflow, write it and route around them. Where it does not, functions are not a
consolation prize — they are the shape that runs on the most machines.

### When the work is all judgment, the Clay belongs in the INPUT, not in the wrapper

Some skills are genuinely all logic: write the email, score the row, pick the tier. Seven of the 36
published skills call no Clay function at all, and that is allowed — `mechanism: logic-only` is a real
value, not a failing grade.

**The wrong repair is a wrapper.** Taking a copywriting skill and giving it a CSV trigger so it becomes
"a workflow" adds a thing to maintain and changes nothing about the output. The installer could have
pasted the CSV into the conversation and been finished. Worse, the judgment then has to live in a
workflow LLM node, and `DETERMINISM.md` is explicit that the LLM node is for prose and **never** for
extraction, comparison or routing — so the same instinct applied to a scorer or a router puts the
deciding logic in the one node that must not hold it.

**The right repair is an input.** Ask what the judgment is operating on, and whether a better version of
that input exists behind an enrichment call:

| A skill that decides… | …decides better when the input carries |
|---|---|
| what to say in a first line | a funding round, a job posting, a stack change — a reason to write *today* |
| which tier a row belongs in | headcount trend and hiring signal, not just the self-reported band |
| whether a signup is worth a rep | the company behind the personal email address |
| which competitor moved | the page as it reads now, not as it read when the list was built |

That is a real dependency: it spends real credits, it is the reason the output is better than the same
prompt without it, and it survives the question *"why not just ask Claude?"* — which a CSV trigger does
not. **So when a draft comes out `logic-only`, do not go looking for a shape. Go looking for the input
that would make the judgment better, name the call that fetches it, and price it.** If no such input
exists, the skill is honestly all judgment and says so — a good logic-only skill beats a padded one.

**Every draft states its read/write posture at Step 0 — a statement, not a question.** Two sentences
at the top of the generated skill: what it reads, what it writes, what it never touches. A read-only
skill says so, because that is the thing an installer most wants to hear before pointing a new tool at
their CRM, and it must not sit at the end of the file where seeing it depends on somebody having read
the whole thing first. Nothing is asked here and nothing waits — it costs the installer nothing.

**And Step 0 is a gate, not a repair shop — so bound it in the draft.** Watched on a real run of a
shipped skill: told the installed CLI was below the server's minimum, the agent spent ninety seconds
fetching a *different* marketplace repository hunting for a newer release. The diagnosis was correct
and the installer read it as a hang. **A broken environment is the installer's to fix, and every
draft says so in one line:** name the component, name the version required, name the one command that
fixes it, and stop. Never install, upgrade, clone or fetch anything to repair the platform — a skill
that starts rebuilding its own prerequisites has stopped being the thing that was reviewed.

**Every draft runs a small batch first, and the kind depends on whether the step can be taken back.**
A read-only or reversible step gets **a real 10-row batch** whose output the installer inspects — that
catches a field mapped to the wrong column or an enrichment returning noise, which no estimate reveals.
An **irreversible** step — an enrollment, a sent message, a CRM write — gets **a dry run** first, then a
small live batch, because a ten-row "test" of an enrollment is ten real people really enrolled and
there is no version of that anyone gets to take back.

**Then exactly one gate before anything bills or mutates, and it carries everything.** Not one gate for
the cost and another for the write. Everything free runs first — the reads, the bucketing, the sender
resolution, the batch — then a single message holds the batch result, the full cost, exactly what will
be written and where, and the ask. **Name the write in the word**, because an action on the installer's
own connected account often costs no Clay credits and a cost gate reporting a truthful zero would
otherwise wave a hundred CRM records through in silence. Then stop and wait. **Never fold away the
ask; never split it into three.** A second stop is right only when the batch reveals something the
installer could not have anticipated — a count far off the estimate, a class of record nobody named.

**And two things never go in a draft, whatever the creator asks for.** No step that **destroys data** —
no delete, no cleared field, no populated value overwritten with a blank, and an update that empties a
field *is* a deletion however the action is named. And no step that **moves the installer's data
somewhere they did not name** — not to a third-party endpoint, not into an author's workspace, and no
more real customer detail into a model prompt than the job needs. If a creator describes either, say
what the draft will do instead: emit a reviewed list and let them run the destructive part in the
system that has their audit log. See `references/skill-contract.md`.

**Any step that spends money must name what runs.** *"Enrich the author to get an email"* is a
sentence about intent that every reader resolves differently — a different function, different inputs, a
different bill. Four things per paid step: **what runs** (the function, by name), **what goes in** (which
fields, from which declared input), **what to verify in the response** (a run can complete and return
nothing), and **what it costs**. Discover them while drafting — `clay routines list`, then
`clay routines get <id>` for the cost the list call omits, and `clay workflows actions schema` for the
real inputs — then write down what you found. Never carry a catalogue of function names into a skill:
names and prices rot, the procedure does not. Full detail and the verified traps:
`references/determinism.md`.

**AND IF THE DRAFT'S FIRST STEP IS A SEARCH RATHER THAN AN ENRICHMENT, OPEN
`references/functions/search-people.md` — or `references/functions/search.md` for company search and population
sizing — AND READ IT BEFORE WRITING THE STEP.** Everything above is about enrichment: a function, a row
in, a priced row out. Search is the seam between finding and enriching, and this file deliberately does
not summarise it: **read the leaf and take the specifics from there rather than from here**, because a
paraphrase in this file is one more copy to drift.

**One thing from the leaf belongs here, because it changes the cost gate:** the search row is **thinner
than the set of fields you can filter on**, so anything the skill judges or links to beyond what it
filtered is a per-row enrichment. The two search modes return different fields, which makes the mode
choice a pricing decision as much as a capability one. **Price that where the search is designed, not at
the gate.**

**The reason this routing line exists is a measured failure, and the failure was ours.** A published
skill built entirely on the search surface re-derived, from live runs and spent credits, at least three
things the leaf already documents — that the plan quota rides on every response, that query-mode rows
carry no profile URL, and that the industry taxonomy does not encode the concept the creator meant.
**The leaf was there, dated, shipped inside the plugin, and never opened.** The flow named the decision
file, the decision file named the leaf index, and the one leaf that mattered was two hops away and never
called by name.

So: **when a draft's first step is a search, name that leaf and open it.** The general rule this is an
instance of has been arrived at from four directions in this file — *guidance that exists but is not
routed to is guidance that does not bind* — and a reference nobody is sent to is indistinguishable, to
the creator paying for the rediscovery, from one that was never written.

**And a caveat on the leaf itself, recorded here because it bears on how far to trust it.** It carries at
least one internal disagreement with a live-verified skill: the leaf says `limit` clauses are refused in
query mode, and a published skill uses a `limit … by` clause as a per-employer cap and reports it
working. **Confirm against the live query reference — `clay search query-mode reference` — rather than
resolving it from either document.** That command is already the rule for writing any query; it is also
how a disagreement between two of our own files gets settled.

**And "what to verify" must name WHERE — the exact path to the payload, not just the field to look
for.** Watched on a live run: a skill said *"check for a `url`, not for success"*, the agent checked,
found nothing, and reported the run had returned empty. The run was fine. The payload was nested one
level deeper than the agent guessed, and it took a raw dump to find it. **"Completed and returned
nothing" and "you read the wrong key" look identical from outside**, and only one of them is worth
telling the installer about — so the draft has to record the path it actually saw in the response,
verbatim, beside the field name.

**AND SOME STEPS CANNOT BE PRICED BEFORE THEY RUN. Those need a cap, not a multiplication.** The four
things above quietly assume the row count is an input. For a **fan-out** step it is the *output*, and
the rule as written produces a confident wrong number.

Measured on a live run, 2026-08-28: a skill told its installer **6 credits** and spent **33**. The
action's `creditCost: 1` is **per returned row, not per call** — and two calls of identical shape
returned **4 rows and 25 rows**, a six-fold spread from the same query. The arithmetic was right and the
premise was wrong: there was nothing to multiply, because the thing being counted did not exist yet.

So when drafting any step whose row count it does not control, the draft must:

- **Say the cost is unbounded**, and give the per-row price rather than a total.
- **Carry a cap the installer sets** — a maximum row count, or a maximum spend — and stop at it.
- **Approve in two stages where a cap will not do**: run one call, report actual rows and actual spend,
  then ask before the rest. One call is a measurement; a batch is a bill.
- **Re-read the balance after the step and report the real figure**, not the estimate. An estimate that
  is never reconciled is how a six-fold overrun goes unnoticed.

**AND ASK IT IN PLAIN WORDS. "Unbounded" is a word for this file, not for the person paying.** The four
bullets above are the mechanism; below is what the creator actually hears. Someone deciding how much of
their money to spend is the last person who should have to decode a term first — and *"this step has
unbounded per-row cost"* earns a *"what?"*, which costs a turn and teaches them nothing.

| Do not say | Say |
|---|---|
| "This step has unbounded cost." | *"This one charges for each person it finds, and I can't tell you how many it'll find until it runs — the same search found 4 people one time and 25 the next."* |
| "Set a cap on the fan-out." | *"What's the most you'd want to spend here? I'll stop when I hit it."* |
| "Two-stage approval on the batch." | *"Let me do one and tell you what it actually cost, then you decide about the rest."* |
| "Reconciling estimated against actual spend." | *"That cost 33, not the 6 I told you. You had 1,002 and you've got 969. Here's what I got wrong."* |

**Ask in the unit the person already thinks in.** They think *how many people do I want* or *how much
money is this*. They do not think in rows times a per-row price, and **they must never be asked to do
the multiplication** — if a number can be computed, compute it and show the total. The question is
theirs; the arithmetic is not.

**One question, one decision, and the honest number in it.** Not a paragraph about how the pricing works
with a question buried at the end. A creator who has to read three sentences to find what they are being
asked will pick whichever option ends the conversation, which is not consent — it is fatigue.

**And never present an unbounded step as the cheap path.** The skill above did worse than misprice it —
its plan-tier guidance recommended that same action as *"the one path the ceiling does not touch"*, so
the tightest plan was pointed at the only step whose cost nobody could predict. **A step you cannot
price is not a step you can call free**, and a constrained plan is exactly where that error lands
hardest.

**Two kinds of thing belong in it, and the second is the one that gets missed.** Technical handles —
table ids, column ids, saved views, auth accounts — have a shape, so the validator catches them.
**Business context does not**: the CRM, the ICP, the weights, the tier cut-offs, what counts as
senior. A hardcoded `1000` is indistinguishable from a considered `1000`, so nothing downstream can
catch it and it has to be caught here.

### A named tool becomes an interview instruction, not a dependency and not a classification

When the source names a specific tool — a CRM, a sequencer, a warehouse, a scraper, an SEO provider —
do **not** preserve the vendor, and do **not** try to work out what category of thing it is. Both are
wrong for the same reason: the skill does not need to know, and neither do you.

Write the *asking* into the skill instead, so the published skill asks whoever installs it:

| The source says | The skill says |
|---|---|
| `read the HubSpot company record` | ask which CRM they run, and which object and fields hold the account record |
| `push to the Outreach sequence` | ask where sequences live for them, and what identifies the right one |
| `query the Snowflake table` | ask where their citation data lives and how to read a row from it |

Two things happen at once and both are required: the tool becomes a **declared input**, and the skill
carries the **instruction to elicit it at install time**. A declared input with nothing asking for it is
a form nobody fills in.

**The test for whether a vendor name survives — apply it per sentence, not per word:** *if the installer
does not have this vendor, does the sentence stop being true?*

- **In a boundary or a carve** — *"do NOT use for Salesforce hygiene"* — it stops being true, and
  wrongly excludes them. **Generalise it.**
- **As an illustrative value** — *"`uses Salesforce` is a technographic enrichment, not an ICP filter"* —
  still true, still teaches. **Keep it.**
- **In the trigger phrases of a description** — *"do they run Shopify or HubSpot"* — still true, and it
  is how the skill gets found at all. **Keep it, and removing it is a defect.**
- **Where the behaviour is genuinely that vendor's** — a quirk of one API — the sentence is *about* the
  vendor. **Keep it, and say in the declared inputs that the skill is vendor-specific.** Rare, and real.

This is the same rule the technical half already follows: a table id becomes a declared input rather
than a literal. A vendor is the business half of the same idea. Use the tool's output
rather than re-deriving by hand: `topo_steps` for dependency order (**never column order**),
`source_claims` for thresholds taken from `formulaText`, `yield_gate` for the thin-table decision.

**The boundary is derived here, not asked, and it is carved against JOBS — never against another
skill.** The `do NOT use` list exists for one reason: an installed agent picks a skill by matching its
`description`, so two skills that answer the same request give it nothing to choose between. The carve
is what separates them. Write it as the adjacent *jobs* this skill is not for — *"not for scoring a
list you already have, not for auditing whether the fields are accurate, not for writing a score back
to a CRM"* — which is the thing that actually mis-fires when somebody asks loosely.

**NO CATALOGUE, NO SLUGS, NO SIBLINGS.** There is no list of other skills in this kit, deliberately.
Do not go looking for one, do not fetch one, and never name another skill — not in the description, not
in the draft, and above all not in your own narration to the creator. Naming a skill they have never
seen spends their attention on something they now feel behind on, and it points at something most
readers cannot look up. The generic job is the half they can check.

**THE FAILURE THIS REPLACES WAS NARRATION, NOT DESIGN.** The rule against showing a creator sibling
slugs was already here, in Step 7's table, and a real run broke it anyway — the agent announced *"there
are three very close siblings"* and listed three by name while reasoning out loud. A prohibition on the
OUTPUT does not bind the THINKING, and the thinking is on screen. So the material is gone rather than
forbidden: with nothing to match against, there is nothing to leak.

**The creator cannot answer this and must never be asked to.** *"Where should I draw the line?"* hands
them our bookkeeping. If the derivation leaves a genuine ambiguity, it becomes a gap in `## What this
skill does not claim`, or at most **one closed question phrased entirely inside their world** (*"if
someone asked for X instead, should this handle it — yes or no?"*).

**The traceability rule, which is what keeps this honest.** Every substantive claim is exactly one of:

1. **derived** — traceable to a formula, prompt or input binding you actually read;
2. **supplied** — the creator said it in Step 6;
3. **a gap** — named in a `## What this skill does not claim` body section, one plain sentence each.

There is no fourth category. Drafting before asking makes invention *easier*, so this is enforced
mechanically, not by good intentions: `compare_claims` fails in **both** directions — a threshold the
draft states but the table does not contain, and one the table contains but the draft dropped — and
`proof` raises rather than emitting a shippable-looking block. **A threshold that disagrees with its
formula is a build failure.**

### The insight is a substantive claim, and it is the one that escapes

`compare_claims` checks numbers. The insight is prose, so nothing mechanical catches it, and it is the
single most consequential line in the skill — it goes in the title and everything downstream follows
from it. **Sharpening what the creator said into a claim they did not make is invention, however good
the claim is.**

Caught in a real from-scratch run. The brief said *"a badge scan gets a generic nurture"* — a tier
assignment. The draft shipped **"a badge scan is proximity, not interest — raffles and walk-bys scan
too"**, which is a different and much stronger claim, with supporting detail (raffles, walk-bys) that
appeared nowhere in the brief. The skeleton then told the creator that everything on screen came from
their brief, their answers, or was marked as nobody's. All three false for that line.

**It reads better than what the creator said. That is the danger, not the defence.** A generated
insight is the most likely thing in the skill to be acted on and the least likely to be questioned,
because it sounds like expertise.

**So it does not get a fourth provenance value — it gets asked.** One closed question, in their world,
the same shape the boundary question uses:

> "You said a badge scan gets generic nurture. I'd sharpen that to *a scan is proximity, not
> interest* — raffles and walk-bys scan too, so treating a scan as engagement is what produces the
> two-week blast. Is that what you meant, or is it more than you'd claim?"

A yes makes it **supplied** and the skill is stronger for it. Anything else and the creator's own
weaker phrasing ships, with the sharper reading recorded as a gap. **It never ships as theirs on a
guess**, and this question does not count against Step 6's budget of three — it is a confirmation of
something already written, not a new unknown.

**The gaps go in the BODY, under `## What this skill does not claim`, in plain sentences** — read by
the person deciding whether to trust the skill. Keep every gap; drop the field names and stage labels.

**THE FRONTMATTER IS EXACTLY THESE SEVEN FIELDS. Anything else is read by nothing.**

```yaml
---
name: your-skill-slug          # lowercase, hyphens, matches the directory name
description: |                 # what it does; "Use whenever someone asks: …"; "Do NOT use it for …"
category: enrich               # one of ten
personas: [revops, founder]    # one or two of eight, never three
mechanism: functions           # workflow | functions | logic-only — derived from the steps
touches: writes-own-output     # read-only | writes-own-output | writes-records
keywords: [plg]                # at most five, from the managed set
---
```

`type` and `tags` are RETIRED and go in no draft. `type` was unvalidated free text, so `type: banana`
passed clean; `tags` carried three unrelated jobs in one bag, and six skills ended up tagged `workflow`
while building no workflow. **Naming a retired field in a draft is the failure this note exists to stop,
so do not reach for either as a place to put something the five cannot hold** — that thing belongs in
the body, where a reader can see it.

**Derive all five; ask for none of them.** `touches` and `mechanism` come off the steps you just wrote,
`category` and `personas` off the description, `keywords` from the managed set. A creator is told
plainly there is no taxonomy homework, so a question here breaks a promise the kit makes in writing.

Full field guidance is in `SKILL-TEMPLATE.md`. **This block is the whole list** — an eighth key is not
a richer skill, it is a field with no reader. `tools/portability.py` reports any it finds, names it and
gives the line, and it checks the VALUES of the five against their lists, so this is checked rather
than remembered.

**And a gap declared in `SKILL.md` must not be contradicted by a supporting file.** Observed on a real
submission: the skill said *"no conversion rate is claimed anywhere"* while its own reference file said
one variant *"converts better"*. The main file is where the discipline gets applied and the supporting
files are where it leaks, so re-read every reference against the gap list before packaging.

If `yield_gate` says the table is too thin, say so and offer the interview. Do not pad a draft out of
four columns; `references/examples/low-yield-fallback/SKILL.example.md` is what the honest version of that outcome looks like.

## Step 6 — Ask only what the draft could not settle

**A question is allowed only if the answer changes what gets written.** These four classes qualify and
nothing else does:

| Class | Why the tool cannot answer it |
|---|---|
| A decisive threshold with no derivable justification | the value is in the formula; the *why* is nowhere |
| A gate whose condition is visible but whose reason is not | `NOT(ISBLANK(Video ID))` is readable; "a page without a video is pointless" is not |
| A hardcoded count that may be an editorial rule or an accident | three step-columns vs "N steps, discovered" are **different skills** |
| An orphan column | a dependency graph cannot tell an abandoned experiment from an optional input |

Everything else becomes a gap in `## What this skill does not claim`. Not every number needs a
justification; the justified ones get stated and the rest get marked.

- **At most three, and the boundary is not one of them** — it is derived in Step 5. Budget by class,
  not by turn count.
- **One decision is one question, even when it has two moving parts.** A rule with a ladder *and* a
  tie-break is a single decision: put the tie-break inside each option rather than asking for it
  afterwards. Watched costing a turn on a real run — three candidate ladders offered, then a separate
  message asking how two dimensions combine, when *"depth sets the rung, fit sorts within it"* could
  have been the distinguishing clause of one option. **Two messages for one answer is the same defect
  as two questions in one message, arriving from the other side.**
- **Keep option text short enough for a picker to render.** The host builds its chooser from the
  options, and it rejects the call outright if they are oversized — the creator sees a red
  `Invalid tool parameters`, which is not a failure they caused or can fix. One short label per
  option, with the reasoning in the question body above it, never inside the options themselves.
- **Order by insight yield, not impact.** A gate question returns intent; an orphan-column question
  returns bookkeeping. Ask the intent-bearing ones first — the insight arrives as a by-product of a
  specific question, which is why there is no separate abstract "what do others miss" question.
- **One question per message. Then stop and wait.** A message with two questions is a defect: they
  answer the easy one and the other is lost.
- **ELI5 the context in one sentence** — what the column does, the options, the tradeoff. *"Titles cap
  at six words. Longer reads better in the CMS but wraps on cards — hard rule, or is eight fine?"* A
  question they must go read their own table to answer is a failed question.
- **"Draft it" ends this step immediately**, and so do one-word answers. Read impatience and move on.
- **Never supply an answer the creator did not give.** If they answer nothing, the draft ships with a
  prominent gap saying the intent behind the thresholds was never confirmed.

**"I don't know, that was arbitrary" is a genuinely useful answer** — it becomes a documented gap
instead of a fake rationale.

**Warm framing, identical labels.** Positive tone means crediting the creator for what they supplied,
never softening what is unestablished. `unknown` stays `unknown`, an unmeasured tier stays unmeasured,
and a gap keeps its plain sentence. The honesty is the product; if the tone ever costs a label, the
tone loses.

## Step 7 — Show the skeleton, confirm, then build

Show the **skeleton of the actual draft**, never a prose summary of the workflow — a summary hides the
problems it is summarising, and people correct documents.

**In plain language, not field names.** The creator has never seen the package contract and has no
reason to learn it. Every one of these reached a creator in a real run, because this step used to say
"show the `proof_gaps` in full":

| Never say | Say |
|---|---|
| `proof_gaps` | **What this skill does not claim** |
| `stage_p` · `stage_e` · `intake` | nothing — drop the label; the sentence must stand without it |
| "the 4 machine-comparable claims" | "the four numbers I could check against your formulas" |
| "not creator-confirmed" | "you didn't confirm this — I worked it out" |
| `proof_status: partial` | say what was and wasn't checked, in the list below |
| any other skill, by name or slug, in the draft OR in your own narration | the boundary as adjacent jobs. There is no catalogue here and no sibling to name |
| "two portability flags are false positives" | nothing. Fix it or report the one that matters — a creator cannot adjudicate our checker |
| "the description ran 55 chars past the verified-intact length" | "I shortened the description" — the measurement is ours |
| "derived from the library rather than handed to you" | nothing. Where an answer came from is only worth saying when it is THEIR answer |

**THE FOUR ROWS ABOVE ARE VERBATIM FROM ONE REAL RUN.** Every one is true, and every one spends the
creator's attention on our bookkeeping: which sibling skills the boundary was computed against, how
many findings our checker produced and which we overrode, a character count, and a note that the
derivation was ours rather than theirs. They are also all *reassurance about process* — the failure
mode is not that they mislead, it is that they read as showing your work to someone who did not ask
to grade it.

**The test before any sentence about how the draft was made: would they act differently if they knew
this?** The boundary line, yes — they can correct it. The five slugs it was derived from, no.

**It must fit on one screen:**

- the title, and one line on what it produces;
- **the insight, with its provenance stated like every number's** — *your words* / *my sharpening of
  your words, confirmed* / *your words as you put them, because you didn't confirm the sharper
  reading*. The provenance table used to cover numbers only, which left the most consequential claim
  in the skill as the one line on screen with no source attached — under a sentence promising that
  everything shown had one. **If the insight is not the creator's phrasing, the screen says so.**
- the steps as one-liners, in dependency order;
- **every number and where it came from** — *your formula* / *you told me* / *nobody established
  this*. **These are three provenances, not three grades.** *You told me* is the strongest thing in
  a skill built from an interview, not a weaker version of a formula: a table records mechanics and
  cannot record intent, which is the reason this flow exists at all. Report it as the source it is;
- **never apologise for a creator's own judgment.** "The logic came from you rather than from a table
  that already ran" tells someone their expertise is a shortfall against a spreadsheet. It is the
  opposite: the thresholds nobody could derive are the ones worth shipping, and the skill is more
  trustworthy for saying who set them. Say *"these are your thresholds — that's what makes them worth
  shipping, and the skill says so"*;
- **what this skill does not claim** — one plain sentence each, no labels. A gap that becomes
  unreadable once its stage label is removed was written badly: the label was carrying the meaning;
- **what the installer has to supply**, naming anything that was a credential or a workspace handle;
- **the boundary as one line in their language** (*"not for X, not for Y"*), so a wrong carve gets
  corrected by reading rather than by being interrogated.

Then **one** question: *"anything wrong?"* Not a checklist. If it does not fit on one screen it is too
long, and the confirm step has regrown into the wall this flow exists to remove.

**None of this becomes frontmatter.** Provenance and gaps live in the conversation and in the
`## What this skill does not claim` body section — never in a frontmatter field. The submission door
does not read such fields and no skill in the library carries them, so a draft that emits them is
adding weight that nothing downstream will ever look at.

## Step 7b — Write nothing for the marketplace page. That is not this file's job.

**`SKILL.md` is written for the agent, end to end. The marketplace writes for the human.** This step
used to emit a `## Listing` block — five fields of page copy — and it is gone on purpose.

The reason it existed: the marketplace's copy generation reached into an agent-facing body and rendered
what it found, so a page once showed `keywords_overview`, *"Step 2:"* and a raw `**Quick finding:**`.
A creator-authored block was the fix. **The reason it is gone: that fixed the symptom by making one
section of an agent-facing file secretly human-facing**, and a hybrid file serves neither reader well.
Two audiences, two artifacts, one owner each.

**So do not add page copy back under any name** — not `## Listing`, not `## Marketing`, not a "for the
reader" section. If a future run finds the marketplace page reading badly, that is a defect to report
to whoever owns the page, not a section to reintroduce here. **A file with one audience is the whole
point of the split.**

What this file still owes a human is unchanged and lives elsewhere: `description` stays a routing
string for a model, `## What this skill touches` stays a disclosure, and `## What good looks like`
stays the creator's own standard for a correct run. None of those are page copy.


## Step 8 — Validate, package, hand back

**FIRST, BEFORE VALIDATING: emit the answer sheet. Both routes reach this step and only this step.**
Every specific the creator gave you that became a declared input — a field name, a table id, a
threshold, a CRM, a scoring weight — you hold both halves of right now: the question that will ship,
and their own value for it. Write the pairs to an answer sheet **beside** the package, keyed to the
declared-input names, so the creator can re-run their own skill without re-answering and can hand it
to a teammate who could not answer at all. **Never inside the package and never in `SKILL.md`** — a
sheet in the package is a blocking finding, and a value in the body is the portability defect the
declared-input discipline exists to remove. Identifiers only: if a creator offers a token or a
password, refuse it and say why.

**This paragraph lived in Step 5 and that made it unreachable for most creators.** The from-scratch
route leaves at Step 1, interviews in `references/interview-to-skill.md`, and returns here — so it never
read Step 5, and `interview-to-skill.md` never mentioned a sheet. Measured on a real creator: he
finished a skill, found no sheet, and reverse-engineered one by publishing the skill, installing it,
running it a second time to be interviewed by his own work, and saving the answers from that. Six steps
to recover a file the creation conversation already had every value for.

It is here rather than copied into both routes because two copies of one rule drift, and the copy the
creator did not read is the one that goes stale.

**MARK WHICH VALUES ARE THEIRS, AND SAY SO WHEN THERE IS LITTLE TO STORE.** A sheet that lists the
skill's own defaults back at the creator looks like a feature that did nothing. Measured on a real
sheet: every value in it — the integration stack, a volume floor, a CTR curve — came from the
specification the creator pasted in, and the sheet's own comment said the per-page inputs were
"intentionally not stored here". Correct on both counts, and the creator read it as broken.

So two things. **Annotate each value as a decision they made or a default they accepted** — a teammate
cannot otherwise tell which numbers are load-bearing. And **if the skill has little durable
configuration, say that out loud** rather than emitting a thin file silently:

> "There's not much worth saving for this one — its inputs are per-page rather than per-person, so
> most of what you'd re-enter changes every run anyway. I've kept the three settings that don't: [x, y,
> z]. It'll still save a teammate those."

**The sheet earns its keep where a skill has installer-specific configuration that outlives a run** — a
CRM, a field name, a scoring weight, a threshold somebody argued about. It earns almost nothing on a
skill whose every input is per-run, and pretending otherwise teaches the creator to distrust it.

**Hand back BOTH, and say what each is for in one line each:** the package is what gets installed or
submitted; the sheet stays with them and travels to a teammate however they already send files. Never
submit the sheet, never publish it, never offer to host it.

**Until this step runs, what is on disk is a draft, and say so if they ask for it.** A creator asking
for "just the `SKILL.md`" is asking for the most natural thing in the world and will get something
that looks finished. Hand it over — it is theirs — and say in the same breath that it has not been
checked yet, and that **if it has supporting files it cannot travel as one file**: the reference
resolves on your disk and nowhere else. One sentence, at the moment they ask.

```
python3 scripts/package_skill.py validate build/<slug>
```

**If `scripts/package_skill.py` is not beside this file**, this host did not carry the tools.
Fetch them from <https://github.com/sungwanjo-clay/clay-skill-creator> (`tools/`) and run there, or
hand over the finished `SKILL.md` and say plainly that it was **not machine-checked**. Never skip
validation silently.

`0` clean · `4` your package has blocking findings · `2` bad invocation · `1` the tool is broken, not
the package.

**BLOCKING findings you fix. REPORT findings you MENTION, once, and leave.** They are information for
the creator, not a to-do list for you, and the difference is the whole reason two severities exist. A
report says *we noticed this, you decide* — an over-long description, a thin declared input, a
name that reads like a workspace artifact. Say what it flagged in one line at the skeleton and let the
creator answer. **Never edit the draft to clear one, and never validate twice to watch a number fall.**

**THE COST OF GETTING THIS WRONG, MEASURED ON A REAL RUN.** A draft came back `ok` with two reports —
a long description and a one-liner eight characters over. The agent trimmed, re-validated, trimmed
again, re-validated, four rounds: **six and a half minutes, 26,000 tokens, four separate edit
approvals for the creator to click, and the verdict went from `ok` to `ok`.** Nothing was wrong before
it started. It even narrated the mistake out loud — *"still a heads-up, not a limit, but I'll get it
under the verified bar"* — reading the guidance and overriding it, because the number looked like a
target and nothing here said not to chase it.

**Write the file ONCE.** Compose the whole draft in memory, then write it in a single pass. Do not
converge on it by successive small edits: each one is a permission prompt, a round trip, and a diff the
creator has to read, and none of them is the correction that Step 7 actually asks for. If you decide
something needs changing mid-draft, change it before you write, not after.

Multi-file skills need packaging, because the form takes one file:

```
python3 scripts/package_skill.py zip    build/<slug> <slug>.zip
python3 scripts/package_skill.py verify <slug>.zip --manifest manifest.json
```

Compare **manifests, not archives**. `references/submitting.md` covers what to expect.

### Sending it from here, if that is the path they pick

**Never submit without an explicit yes — and make that yes the only stop between "build it" and
sending.**

This tail used to hold four separate halts: confirm the skeleton, go read the file, run `preview`,
then confirm the send. **Four consecutive confirmations protect less than one does**, because by the
third the creator is acknowledging rather than reading, and the one that carries the actual lock is
last — arriving at exactly the point where attention has run out. So run the validate and the
`preview` without stopping, and put everything in front of them **once**:

**ASK FOR THEIR NAME. THAT IS THE WHOLE PROFILE INTERVIEW.** `workEmail` you already have; `company`
comes free off the email domain, deterministically, with no lookup — `sungwan.jo@clay.com` is Clay.
Everything else on the profile — LinkedIn, byline, title, avatar — **is filled in on our side from the
name and the email and confirmed by a person before anything publishes.** Do not ask for them, not
even as optional: a field offered as optional is still a field somebody now has to think about, and
this one is ours.

Watched costing a real run three extra questions. The agent read `--help`, saw five profile keys, read
`_profile()`, saw two were required, and split the difference by asking for the name and offering the
other three as optional. Every part of that was reasonable and the whole of it was avoidable — nothing
told it the other three are derived rather than merely optional.

```
python3 scripts/submit_skill.py preview <package> --profile '<fullName, workEmail, company>'
```

That prints exactly what would be sent — the package digest, the file inventory, their details, the
consent text — and sends nothing. **One message: where the file is, that it validated clean, that
they are its last reviewer, the full `preview` block including the consent text, and the ask.** Then
stop, and wait. Only on a yes:

```
python3 scripts/submit_skill.py send <package> --profile '…' \
        --confirm <the token preview printed> --rights-confirmed
```

`send` refuses without the token from `preview`, and the token stops matching if the package changed
after they saw it — so *show, ask, send* is the only sequence that works.

**This is the gate that does not get collapsed, and it is not politeness.** The token is random,
minted only by `preview`, bound to the package digest and the creator's identity, and consumed on
use — so it cannot be derived by anything that merely controls the request. That is what makes
*"nothing is submitted without your explicit yes"* a mechanism rather than a sentence in a document,
and it is the specific defence against an instruction hidden in a table configuration or a supporting
file driving a submission on the creator's behalf. **Fold the showing into one message; never fold
away the ask.**

**No `--endpoint` — it defaults to production.** It used to be required and named no default, so a
creator who followed every step reached the last command and had to supply a URL that appeared in no
document they had been given. Pass `--endpoint` only to reach a different deployment.

**Never build the request yourself.** The package is base64 in the body: at the documented ceilings
that is ~1.9–2.7 million tokens for a zip and ~100 thousand for a `SKILL.md`, and a truncated encode
arrives as an apparently **corrupt archive** rather than as an obvious limit. The script reads from
disk. Same reason the retry secret comes from `secrets.token_hex(32)` inside it and not from you:
**anything needing exact bytes or real randomness comes from code, never from the model.**

The receipt holds a private retry secret. It is written beside the package at `0600` and its value is
never printed — report the path. And say plainly what happened: **submitted for review, not
published.** A person reviews it and verifies identity before anything is public.

## Step 9 — Name both ways to submit. This step is not optional.

**A validated package is not a finished job.** Every route ends here — from a table, from scratch,
or arriving with a `SKILL.md` already written. Do not stop at *"here is your file, it validated
clean."* Measured on two real runs from opposite routes: both ended with a package on disk and no
stated next step, and the from-scratch route did not reach this step at all, because
`references/interview-to-skill.md` finished at *"what comes out, and its limits"* and never came back.
A creator who has just spent twenty minutes on a skill and is told only where the file landed has
been handed a dead end.

**Required: name both paths, ask which. Still forbidden: sending without a yes.** Those are not in
tension — what became mandatory is the *offer*, not the submission. Presenting a choice is not
submitting, and the token gate in the section above is untouched.

| Path | What happens |
|---|---|
| **You upload it** | the form at `https://marketplace.clay.com/submit` takes the package |
| **I send it** | the `preview` → show → yes → `send` sequence above, from this session |

**Give them the URL, not the noun.** Say `https://marketplace.clay.com/submit`. "The Clay Marketplace
submission form" is a thing a creator cannot find by being told it exists, and a creator outside Clay
has nobody to ask where it is. Also tell them a first response takes **two business days**.

**Neither is the default and neither is recommended over the other.** A creator who wants to read the
consent text on a web page and click the button themselves is making a reasonable choice, and a flow
that nudges toward the path it can drive itself is selling convenience it benefits from. Ask, then do
what they say.

**If they decline both, the step still completes.** Say where the package is, that nothing has been
sent, and that either path is still open whenever they want it — then stop. *"Not now"* is a finished
outcome; *"here's your file"* with nothing after it is an unfinished one.

**And do not re-offer.** One clear statement of both options, once. A creator who said no and gets
asked again is being pressured, which is the opposite of the promise this flow is built on.

### When it is a correction to something already submitted — do NOT just send it again

**Measured in production on 2026-08-28, by the marketplace team, on the real route.** Changed bytes,
same creator, same `name:` returned `201` with a new submission id, a new version id, **and a new slug
with `-2` appended**. So:

**A resubmission is not a new version. It is a second, independent listing, and its slug is
permanently mangled.** The route is purely additive and has no supersede or replace behaviour.

- **`name:` does not carry identity.** It only *requests* a slug. Identity is the submission id, which
  the creator does not control and cannot reuse. Do not tell anyone that keeping `name:` stable
  preserves their listing — it does not, and that claim was in this file until it was measured false.
- **If their earlier submission is already published, it stays live** and the correction sits beside it
  as a separate pending listing. Two listings for one skill, and the good slug is on the stale one.
- **The supported revision route is not available.** A `revisions` endpoint exists and takes a skill id
  and a base version, but it needs a management link and management-token resolution is returning `404`.
  **Do not describe it to a creator as something they can use.**

**So the instruction is: stop, and say why.** A creator who wants to correct a submitted skill should
speak to whoever invited them and have the earlier submission removed first — deletion of an unpublished
submission exists on the review side. Resending is the one thing not to do, because the `-2` slug is
public and permanent and no creator would have chosen it.

**And if they resubmit anyway, that is their call to make with the cost stated.** Say what they get: two
listings, the `-2` slug, no self-service withdraw. Then do what they say — this flow states costs, it
does not overrule people.

`preview` still has to run again in any case: the consent token is per-preview and `send` refuses a
stale one. Never reuse the first submission's token, and never treat "they consented once" as consent.

## Rules

- **NEVER** read a row, run a column, write to a table, or execute a Clay action.
- **NEVER** run `clay tables list` without `--filter owner.id=`.
- **NEVER** print any part of a credential, or instruct the creator to rotate one.
- **NEVER** infer a step, threshold or purpose from a column name.
- **NEVER** state a claim that is not derived, supplied, or marked as a gap.
- **NEVER** ask a question outside the four classes in Step 6, and never two in one message.
- **NEVER** name another skill, to the creator or in the draft, and never ask them to reason about
  how a description gets matched or where the boundary goes. That is our bookkeeping, not theirs:
  derive the boundary as adjacent JOBS and show it as one line.
- **NEVER** show the creator a field name, a stage label or a tool name — `stage_p`, `stage_e`,
  `intake`, `derive_recipe.py`. Say what it means. They are reviewing their own workflow, not our
  package format.
- **NEVER** narrate our bookkeeping: the sibling slugs a boundary was derived from, how many findings
  the checker returned or which were overridden, character counts, or that a derivation was ours
  rather than theirs. Show the conclusion they can correct; the working is not theirs to grade.
- **NEVER** frame creator-supplied logic as a deficiency. Provenance is stated, never ranked — and
  their judgment is the input a table cannot hold, which is the premise of this whole flow.
- **NEVER** submit without an explicit yes, and never imply a skill was accepted or published.
- **NEVER** construct the submission request yourself, and never generate its retry secret.
- **NEVER** write a paid step without naming the function, its inputs, what to verify and its cost.
  "Enrich through Clay" is intent, not an instruction.
- **NEVER** quote a total for a step whose row count is its output. A per-row price times a number
  nobody has yet is a guess wearing arithmetic — measured at 6 credits told, 33 spent. Say it charges
  per result and the count is unknown until it runs, carry a cap, reconcile the balance afterwards, and
  **never call such a step free or cheap.**
- **NEVER** ask about money in vocabulary the person paying has to decode — no "unbounded", no
  "fan-out", no "per-row", no "reconcile". One question, one decision, the real number in it, and the
  arithmetic already done. **A creator too tired to parse the question is not a creator who consented.**
- **NEVER** carry a named tool through as a dependency, and never classify it into a category either.
  Convert it to a declared input **plus** an instruction telling the skill to ask for it at install
  time. A vendor name survives only where the sentence stops being true without it.
- **NEVER** state something as settled in a supporting file that the main file lists as unestablished.
- **ALWAYS** put the gaps in a `## What this skill does not claim` body section — never in retired
  frontmatter fields outside the six-key block above, which nothing downstream reads.
- **ALWAYS** write a `## Declared inputs` section covering both workspace handles and business
  context — thresholds, weights, verticals and tool choices are the installer's, never the author's.
- **ALWAYS** derive the full draft before asking anything.
- **ALWAYS** draft — with gaps if needed. Unanswered items are gaps, not blockers. The only thing that
  must never happen is inventing an answer.

## What good looks like

The creator reads the skeleton and says "yes, except one thing." Three questions or fewer were asked,
each naming a specific column, and the boundary was derived rather than handed back. Every threshold traces to a formula or sits in the does-not-claim section. The common
failure is a skill that is fluent everywhere and grounded nowhere — and it passes validation, because
validation checks form.

## Worked example

A 47-column table publishing walkthrough pages. `topo_steps` returns eight steps in dependency order,
not the 47 columns in table order. `source_claims` finds a six-word title cap, a 200-character hero
limit and two gates. Four columns are orphans. The draft is written complete, then three questions:
*is three steps an editorial rule or what this table happened to hardcode* (a different skill either
way), *why does a missing video block creation*, and *are these two orphans dead or optional*. The
answer to the second is the insight and it was never asked for directly. The boundary is derived as the adjacent jobs this skill is not for, and shown as one line in the
skeleton. Skeleton shown, one correction, validated,
handed over — three questions total.
