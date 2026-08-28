# People search: the two modes return different fields, and that is a pricing decision

> **Read from Clay's published documentation and OpenAPI schema on 2026-08-28**, plus one live sourcing
> run the same day. That is a different provenance from the rest of these leaves, which are build
> observations over a shared window — where this file says *published*, it was read from the schema
> rather than measured, and that is the stronger half. **Report what you read; never quote a figure here
> as anyone's price or as a promise of yield.** If the live catalogue or the query reference disagrees
> with anything below, **the catalogue wins and this file is wrong.**
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

**The reference endpoint is the authority on the query language and this file is not.** Two things worth
knowing about those last two endpoints: the query reference returns markdown written to be handed
straight to an agent, and the fields endpoint returns `guidance {behavior[], field_guidance[],
create_examples[]}` alongside the field list — **Clay ships the per-field behavioural notes that skills
keep rediscovering at their own expense.** Reading them costs nothing.

## The projection difference, and why it is the first decision

Both modes create a search, return a `search_id`, and page a stateful iterator. They do **not** return
the same person.

| | filters mode | query mode (advanced, beta) |
|---|---|---|
| profile URL | **`url`** ✓ | **absent** |
| current role | `latest_experience_{title,company,start_date}` | only `matched_experiences[]` — what matched |
| location | `structured_location {city,state,country}` | `location {name,city,state_or_province}` |
| identifier | — | `clay_profile_id` |
| name | `name`, `first_name`, `last_name` | same |
| cross-entity criteria | no | **yes** — `experiences.any(…)`, `company.technographics.any(…)` |
| nested Boolean | no | **yes** |

The query-mode person is **closed** — `additionalProperties: false` over exactly six fields. So there is
no profile URL, no headline, no summary and no years-of-experience in the row, **and several of those are
filterable.** You can filter on a field the response will not return.

**Clay's guidance is to use advanced query mode by default**, and for a definition that needs employer
attributes or nested alternatives that is right. But the choice costs something specific:

> **Anything the skill judges on, or links to, beyond what it filtered on, is a per-row enrichment.**

**Measured on one live run:** a sourcing skill built on query mode paid a per-row enrichment across all
36 rows it kept, and the first thing that enrichment bought was the profile link — which filters mode
returns in the search row for free. That is not an argument for filters mode; the same skill's precision
came from a query-mode-only construction. It is an argument for **naming the trade where the search is
designed, not at the cost gate.**

## Response keys: the API is snake_case, the CLI is camelCase

The CLI normalises. Nothing in either surface says so, and every skill in this corpus documents the CLI's
spelling:

| CLI | API |
|---|---|
| `hasMore` | `has_more` |
| `searchId` | `search_id` |
| `sourceType` | `source_type` |
| `exhaustionReason` | `exhaustion_reason` |
| `periodQuota` / `resetsAt` | `period_quota` / `resets_at` |

**This matters here more than it looks, because portability is the whole premise of a skill.** Notes
taken from CLI output, handed to somebody wiring the same job against the API, name keys that are not
there — and a missing key reads as an absent *value*, not a wrong name, which is the failure that looks
like an empty result. **When a draft names a response key, say which surface it came from.**

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

**Per search is the row that catches people out:** the total across every page of one `search_id`. On Free
and Trial a single search cannot exceed 50 rows however you page it, so **a skill that assumes 500
silently under-enumerates for some installers.** Exceeding a limit returns **402** with a message naming
which one, and period errors state the reset date; malformed input is still **400**. The run-body `limit`
is 1–500, default 20, and does not change spend — metering is per row returned.

## Two open questions, deliberately not answered here

Both come from a live run and neither appears in the documentation prose, so **settle them from the query
reference rather than from this file or from a skill that reports them.**

1. **A `limit … by <field>` clause in the query text.** `search.md` says query mode refuses `limit`
   clauses; a published skill uses `limit 2 by clay_company_id` as a per-employer cap and reports it
   working. One is wrong.
2. **`is_similar_to` expansion breadth.** The same run reports that narrowing the input title list does
   not narrow the expansion, and that one title expanded across an entire job family. If that holds, the
   input list is not the control surface a draft would assume it is.
