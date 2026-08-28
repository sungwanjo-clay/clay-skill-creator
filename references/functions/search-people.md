# People search: the two modes return different fields, and that is a pricing decision

> **Read from Clay's published docs, OpenAPI schema and query reference on 2026-08-28**, plus one live
> sourcing run. Different provenance from the other leaves, which are build observations over a shared
> window: where this says *published* it was read from the schema, not measured. **Report what you read;
> never quote a figure here as anyone's price or as a promise of yield.** If the live catalogue or the
> query reference disagrees with anything below, **the catalogue wins and this file is wrong.**
>
> `search.md` is the companion leaf: the industry-vocabulary gap, the size-band mismatch and the
> coverage oracle. Read that one if you are sizing a population rather than building a list of people.

## Read the source. It is free, machine-readable, and more current than this file.

```
https://developers.clay.com/llms-full.txt     the whole doc set as plain text
https://developers.clay.com/openapi.json      required fields, enums, closed objects
GET  /search/query-mode/reference             THE QUERY GRAMMAR AND FIELD LIST — needs an API key
GET  /search/filters-mode/fields?source_type= filter fields, PLUS machine-readable guidance
```

**The fields endpoint also returns `guidance {behavior[], field_guidance[], create_examples[]}` beside
the field list — Clay ships the per-field behavioural notes that skills keep rediscovering at their own
expense.** Reading them costs nothing.

## The projection difference, and why it is the first decision

Both modes create a search, return a `search_id`, and page a stateful iterator. They do **not** return
the same person.

| | filters mode | query mode (advanced, beta) |
|---|---|---|
| profile URL | **`url`** ✓ | **absent** |
| current role | `latest_experience_{title,company,start_date}` | only `matched_experiences[]` — what matched |
| location | `structured_location {city,state,country}` | `location {name,city,state_or_province}` |
| identifier | — | `clay_profile_id` |
| cross-entity criteria | no | **yes** — `experiences.any(…)`, `company.technographics.any(…)` |
| nested Boolean | no | **yes** |

The query-mode person is **closed** — `additionalProperties: false` over exactly six fields. So there is
no profile URL, no headline, no summary and no years-of-experience in the row, **and several of those are
filterable.** You can filter on a field the response will not return.

**Clay's guidance is to use advanced query mode by default**, and for a definition that needs employer
attributes or nested alternatives that is right. But the choice costs something specific:

> **Anything the skill judges on, or links to, beyond what it filtered on, is a per-row enrichment.**

**Measured on one live run:** a sourcing skill on query mode paid a per-row enrichment across all 36
rows it kept, and the first thing it bought was the profile link filters mode returns free. Not an
argument for filters mode — that skill's precision needed query mode. An argument for **naming the trade
where the search is designed, not at the cost gate.**

## Response keys: the API is snake_case, the CLI is camelCase

The CLI normalises and neither surface says so: `has_more`/`hasMore`, `search_id`/`searchId`,
`source_type`/`sourceType`, `exhaustion_reason`/`exhaustionReason`, `period_quota`/`periodQuota`,
`resets_at`/`resetsAt`. Every skill in this corpus documents the CLI spelling. **Portability is the
premise of a skill, so this bites:** notes from CLI output name keys the API does not have, and a missing
key reads as an absent *value* rather than a wrong name — the failure that looks like an empty result.
**When a draft names a response key, say which surface it came from.**

## `period_quota` is optional. Read it defensively.

Published as **not required** — only `data`, `has_more` and `source_type` are. When present it carries
`{limit, used, remaining, resets_at}`, which is the cheapest way to reconcile spend after a step. A skill
that dereferences it unconditionally gets `undefined` on the page that omits it.

`exhaustion_reason` is a closed enum of exactly two values: `query_limit` and `no_more_results`.

## Result limits are published per plan. Transcribe them; do not measure them.

| Plan | Per request | Per search | Per period | Resets |
|---|---|---|---|---|
| Free | 50 | 50 | 100 / month | 1st of the month (UTC) |
| Trial | 50 | 50 | 10,000 / trial | — |
| Paid | 500 | up to the period limit | 1,000,000 / year | 1 January (UTC) |
| Enterprise | 500 | up to the period limit | 10,000,000 / year | 1 January (UTC) |

**Per search catches people out:** it is the total across every page of one `search_id`, so on Free and
Trial a single search cannot exceed 50 rows however you page it — **a skill assuming 500 silently
under-enumerates for some installers.** Exceeding a limit returns **402** naming which one; malformed
input is still **400**. The run-body `limit` is 1–500, default 20, and does not change spend.

## The query reference is 22,000 words and authoritative. Fetch it; never restate it.

It arrives as one markdown document carrying its own skill frontmatter (`name: clay-search-query`),
because Clay ships it to be handed straight to an agent: formal grammar, operator semantics, per-field
docs for people, companies **and jobs**, per-entity guardrails, worked examples. Below is only where our
corpus contradicts it.

**`count` and `limit` are in the grammar and forbidden by the policy — follow the policy.** The grammar
admits `mode = select | count`, `limit N`, and a separate `limit N by clay_company_id`; the reference's
**Query mode policy** then says always `select`, never count-mode, **never include `limit` clauses.** So a
published skill using `limit 2 by clay_company_id` as a per-employer cap is relying on something the
grammar parses and the guidance says not to write. The policy does not distinguish `limit` from
`limit … by`, so **treat the cap as unsupported** and cap per employer after the fact.

**`is_similar_to` on `job_title` expands deliberately and is not bounded by your list.** It "expands the
title into related synonyms, abbreviations, and variants", and the reference says **default to it for
`job_title` — best recall.** So finding that a narrower input list does not narrow the expansion is the
feature working. **For literal titles use `contains`, AND-joined one required word per predicate** —
`job_title contains "engineer" and job_title contains "automation"` — a cheaper precision lever than
moving keywords into a role description. Exception: a **jobs**-result query has no title `is_similar_to`.

**Three operator facts our files get wrong or omit.** `contains` is token-based, whole-word, and takes a
parenthesized OR list — prefer `field contains ("a","b")` over an `or` chain. **`starts_with` and
`ends_with` ARE substring-based**, so there is a substring path and `contains` is not it. **Enum fields
accept only `=`, `!=`, `in`, `not_in`** — never a numeric or text operator.

**Clay's own policy confirms the rule against keyword proxies.** On unmeasurable quality asks — *"top
performers"*, *"proven track record"* — it says omit them and **"do not invent quota/award keyword
proxies."** A skill in this corpus reached that conclusion independently; it is now platform guidance.

**And one place to diverge from it deliberately:** it says not to tell the user those soft criteria
were dropped, nor to mention approximations. **Right for a query generator, wrong for a skill** whose
reader is deciding whether to trust a list. Disclose both anyway — knowing you are choosing to.
