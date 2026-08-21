# Funding, executive changes and news

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that spent the credits. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

| Need | Reach for | Trap |
|---|---|---|
| funding rounds | an AI research pass first, then a provider waterfall | **use the typed `company/fundingRound` waterfall** or you get `Series B` from one provider and `series_b` from another |
| news, cheap | a general news-results action, 1 credit | quiet is **field-absence**, not an empty list — and quiet still bills. Dates arrive as **relative strings** |
| news, structured | the managed Company News function, ~6.7 credits declared | returns 100 events and **ignores the max-events input**; ~1/3 of events arrive **undated** |
| executive changes | a people-index lookup for new hires, seniority-filtered, plus an AI departures pass | ~0.5 credits per people call |

## The finding that governs this whole family: topical relevance is not evidence

Asked about a specific hiring event at a named company, a news arm returned — among ten results — a
**different company hiring former employees of the target**, which argues the opposite, plus opinion pieces
merely mentioning it, plus aggregator pages.

Hand those ten to a model and ask "is this company building a team here?" and it finds abundant on-topic
text about the right company and answers **yes**. **The proxy fired; the question went unanswered.** Any
skill that routes news through a model needs a deterministic entity and event discipline in front of it,
not a better prompt.

The four discriminations that discipline needs:

- **Crawl date is not event date.** A years-old roundup surfaced inside a one-week window carrying a fresh
  relative stamp. Aggregator, database and roundup pages are date-stamped like news and are not events.
- **Name boundaries matter.** A real-estate firm sharing the account's name as a *prefix*, and a hijacked
  vessel carrying it as a ship name, both passed a naive name match. So did a story about a *former* exec's
  new venture, and a supplier's story mentioning the account.
- **One event arrives 3–4 times** across outlets, plus derivative coverage. Dedupe on an **event
  fingerprint** — scale figure, geography, timing — across differing or missing names, because one live
  cluster named a parent organisation in one outlet and its subsidiary in another.
- **Order the pipeline: classify → dedupe into event clusters → date the merged candidate on its
  best-basis source → window-check.** Dating article-by-article kills cluster members on their weakest
  source. Derivative sources — law-firm releases, lawsuit coverage — never date a candidate and never kill
  one; and for an incident signal the **disclosure** dates the event, with a prior filing date counting.

**A provider's own signal date can trail the call date** — 18 days stale in one observation. Carry
`signalDate` into the output and **diff scheduled runs on it, not on the run date**, or a stepwise signal
reads flat for weeks and then jumps.

## Funding

**An AI research pass first is both the cheapest and the broadest arm** — it costs a fraction of the
providers and covers non-US and early rounds the pure providers miss. Each downstream provider then runs
only if the pass returned nothing, and its condition checks **both** that the pass ran **and** that the
prior providers did not hit.

**The hard error on this signal is investor-versus-investee**, and it is a model error rather than a data
one: a venture firm investing in a portfolio company is **not** a funding event for the firm; the firm
raising from its own investors **is**. Handle it with explicit rules and worked examples, not a warning.

**Normalise the round name through the typed waterfall.** Without it the same round arrives as `Series B`
and `series_b` from two arms and no threshold works.

Enforce a **window on every time-bounded fact**: an undated match is not a match. "New executive" with no
window matches a change from four years ago.

## Executive changes

Two arms with different failure modes, and both are needed. A **people-index lookup** filtered by seniority
returns structured new-hire rows with start dates. An **AI departures pass** is the only way to get
departures at all, and it needs a stated **source-credibility order** — company releases first, then the
profile index, then major news, then trade press, then filings — because the same departure is reported
with different dates by different tiers.

**A seniority vocabulary is a closed set and may not contain what you want.** One recipe's stated band was
inexpressible on the live arm. Check the values before promising a filter.

Any function filter is likely hardcoded to whichever function the original build cared about; swapping it
for another vertical does not change the action contract or the downstream formulas, but it must be swapped
deliberately rather than inherited.

## News, structured versus cheap

The managed function returns **100 structured, pre-classified, fully sourced events per domain** and:

- **ignores the max-events input** — asked 5, got 100;
- requires **full ISO 8601 date-times** despite field names that read "YYYY MM DD";
- returns **36 of 100 events undated**, and **the window is respected only by the dated ones**.

So the no-date rule is not caution, it is the live-validated guard: an undated event cannot be
window-checked and must not be counted as in-window.

The cheap arm's quiet shape is worth stating precisely: **SUCCESS with no result field at all** — quiet is
field-absence, not an empty list — **and it still bills 1 credit.** A windowed request is honoured: a
past-24h query returned only sub-12-hour events with the weeks-old stories from the same query at a
past-month setting absent, so zero stale leakage. But a *different* arm silently ignored a date filter that
had **no declared value space**, returning five-month-old items for a past-month request. Read the schema
for the value space before trusting a window parameter.

**Engagement on your own social content is a different job** — person-grain and
first-party rather than company-grain and third-party — and lives in
[`engagement-own-posts.md`](engagement-own-posts.md).
