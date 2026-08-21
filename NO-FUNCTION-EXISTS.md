# Jobs the platform has no function for

**Read this during the interview, not after drafting.** If someone says "and then score them" and
nothing scores, that has to surface in the conversation. Finding out afterwards means a draft already
names something imaginary, and the repair is a rewrite instead of a sentence.

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that ran the searches.
> Absences are re-checkable in seconds and worth re-checking: a new action would change an answer here
> before it changed anything else in this kit.

- **No question-answering or research-agent action.** Zero matches across ask / question / answer /
  research / analyst / claygent in a 656-action catalogue. A question-shaped skill is an AI column over
  catalogue arms; there is no call that takes a question.
- **No `use-ai` or Claygent action on the CLI and workflow catalogue at all**, and for a skill this is
  a non-problem rather than a gap. A marketplace skill runs inside the installer's agent, so **the agent
  reading the skill is the model**: Clay supplies the facts, the agent supplies the judgment. A recipe
  written around an AI column does not transfer as written — the judgment transfers, the engine is the
  agent instead. Often that is *better*: one build replaced a per-row AI call with deterministic keyword
  gates plus judgment on the residual, at 0 credits, auditable, and reproducible on the same input.
  **Two things this is not.** It is not "no LLM anywhere": the workflow node palette does have an LLM
  node, which is a separate surface from the action catalogue, and it is for prose only — never for
  extraction, comparison or routing. And it is not a reason to reach for a table column, because a table
  is not a surface a skill builds on.
- **No scoring or classification function, managed or general.** A full routine roster held two
  score-named routines, both workspace-internal. The large action catalogue holds dozens of
  *workspace-custom* scorers, which is the tell: scoring is always built per workspace. There is a free
  Clay-native "Score Row in Clay" action whose output shape (`score` + `scoreReasons[]`) natively
  encodes an evidence trail, if you want the column living inside Clay.
- **No dedupe or merge function, and no CRM merge or delete executor anywhere.** Salesforce actions are
  lookup / update / create / convert-lead only. **Clay flags duplicates; the merge executes in the CRM.**
  A skill promising merge execution through Clay is unshippable — the deliverable is a dry-run plan for a
  human.
- **No batch email validation.** No managed list-cleaning function exists, and no catalogue action takes
  a batch of emails; even plural-named validators accept a single `email`. Batch cleaning is a loop or a
  table.
- **No brand-mention discovery, no review-site intent feed, no identified website visitors.** Adjacent
  actions exist and answer different questions — one is company enrichment, another is traffic volume
  only. Matching a name is not the same as matching a capability.
- **No detector mesh** — no RSS, trigger-source or webhook fan-in actions. An event-anchored news query
  is the only net-new detector on this surface, and company search carries no event or date filters.
- **Nothing for budget or approval, renewal dates, team rosters, or category intent.** Each is something
  people ask for by name.

**When a requested dimension has no arm, say so and leave its weight in the denominator.** Dropping it
quietly inflates coverage: the skill then reports high confidence over the subset it could see, which is
the same number it would report if the missing dimension did not matter. One build states its maximum
achievable coverage up front for exactly this reason — 0.80, computed, because one proxy of ten was
unobservable.

**Also worth catching in the interview:** a job that *looks* like it has a function because an action
matches on name. One build found an action whose name matched a post-engagement search and which is in
fact a Hacker News scraper. Match on the schema, never the name.
