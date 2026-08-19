# Writing a deterministic skill

**The test, and it fits in one sentence: could two competent installers follow this step and end up
calling different things?** If yes, the step describes what *you* did rather than instructing anyone.

"Enrich the author to get an email" fails that test. Every reader resolves it differently — a different
function, different inputs, a different bill.

## What deterministic does and does not mean

It does **not** mean reproducible output. A company hires, a domain moves, a page is rewritten: same
input, different answer, and that is correct.

It means **the same instruction produces the same calls.** Determinism lives in the mechanism, never in
the data.

## The four things any step that spends money must name

| | Why it cannot be left implicit |
|---|---|
| **What runs** — the function or action key | "enrich" is a category. Several functions do it, at different prices, returning different fields |
| **What goes in** — which fields, from which declared input | otherwise field mapping is a guess, and that is where silent misses come from |
| **What to verify in the response** | a call can succeed and return nothing useful. See below |
| **What it costs, and who confirms before it runs** | spend without a stated number is spend without consent |

One row per paid step, in the skill. A reader can then price the run before starting it.

## Discover the facts; carry only the judgment

**Never write a catalogue of function names into a skill.** Names, prices and input shapes change, and a
stale list is worse than none because it reads as authoritative. What survives is the procedure:

```
clay --version                     keep it current; an outdated CLI refuses to run at all
clay routines list                 what managed functions this workspace has
clay routines get <id>             its declared cost — the LIST call does not carry costs
clay workflows actions list        the action catalogue, greppable
clay workflows actions schema <packageId> <actionKey>    the real input parameters
```

**Treat those command names as a starting point and confirm them with `--help` against your installed
version.** The CLI moves; a skill that hardcodes a subcommand ages the same way a skill that hardcodes
a provider does.

### Discovery output is not trustworthy at face value

Six ways a reasonable reading of the catalogue is wrong. Each has been hit:

- **A default list is not the whole list.** Listing returns a page, and a null cursor at exactly the
  default page size is *not* proof of completeness. Page through, or fetch by id. Never conclude a
  function does not exist from one list call.
- **Present does not mean callable.** A function can sit in the catalogue and still be unavailable to
  the CLI, because it has not been registered as a routine. Check, rather than assuming availability
  follows from existence.
- **Display names are not keys.** The same underlying action appears under different human-facing
  labels. Match on the action key and the schema; never on the label.
- **A plural name does not mean batch.** Actions named for verifying *emails* accept exactly one email.
  Read the schema, not the name.
- **The description can be wrong where the schema is right.** A function described as working from a
  name and company may require a profile URL or an email address, and fail per item without one. The
  declared input schema is the honest signal; the prose is marketing.
- **Undeclared inputs pass silently.** A run that *starts* proves nothing about whether your inputs were
  understood — extra keys are sometimes ignored and sometimes fail per item at run time. Trust the
  declared schema and the per-item result, never the fact that a run began.

### Cost has two meters and neither is on the list call

- **Fetch by id for the declared cost.** The list call omits it.
- **Declared cost and billed cost can differ by plan.** Report what was actually charged rather than the
  catalogue figure.
- **Some actions bill executions rather than credits**, so a per-row estimate in one unit can be wrong
  in the other. Say which unit you are quoting.
- **Probing is finite.** Test-run capacity is capped per workspace per day, so verify the calls that
  matter and note the ones you could not reach rather than planning on unlimited probes.

## The waterfall is the deterministic shape for enrichment

When several providers can answer the same question — company revenue, employee count, a work email,
site traffic — the pattern that is both cheap and reproducible is an **ordered set of calls where each
one's run condition tests the specific output path of the one before it**.

```
call A                          always runs, cheapest of the set
call B    runs only if   A's <named output field> is empty
call C    runs only if   A's and B's named fields are both empty
coalesce  first non-empty of A → B → C, as a typed waterfall column
```

Two details carry the whole pattern:

1. **The gate names a field, not a status.** `A ran` is not the condition; `A returned nothing at this
   path` is. A completed call with an empty value is a **miss**, and gating on completion buys every
   later call for nothing.
2. **Order by cost, ascending.** The spread between the cheapest and dearest provider for one question
   is large — enough that ordering changes the bill severalfold while leaving the output identical.
   Read the real costs at authoring time and say what order you chose and why.

## Traps that cost real debugging

- **A column's name is not evidence of its content.** A production build carries a column named for
  revenue that actually holds an employee count. Read the formula, never the label.
- **Bands arrive as strings.** Size and revenue come back as `"1,001–5,000 employees"`. Compare band to
  band; parsing to an integer invents precision that was never there.
- **Enrichment is not liveness.** A dead or acquired company enriches perfectly well on last-known
  data. A filled row is not a live company.
- **"The current one" can be plural.** A person can hold two concurrent current roles. Code that finds
  *the* current entry is ambiguous by construction; take the field naming the primary one.
- **A wrong-workspace id can return not-found at a success exit code.** Absent and inaccessible look
  identical unless you distinguish them.
- **A pinned input fails the run on an empty string, not only on undefined.** Emit a non-empty sentinel
  for a field that might legitimately be blank.
- **Concurrency has a ceiling that is not yours.** Providers rate-limit; a fan-out that works on ten
  rows fails on a real list. State the cap you used.

## Keeping this file honest

It carries **no function names, no provider names and no prices** — deliberately, because those are the
parts that rot, and a reader who trusts a stale name is worse off than one who runs the discovery. What
is written down here is the procedure and the traps, which have outlived every catalogue change so far.

If a rule here ever contradicts what the live catalogue tells you, **the catalogue wins and this file is
wrong.** Say so in the skill you are writing.

## Before you ship a step, ask it out loud

> Could two competent installers read this and call different things?

If yes, the step is not finished. The fix is never longer prose — it is naming the four things above.
