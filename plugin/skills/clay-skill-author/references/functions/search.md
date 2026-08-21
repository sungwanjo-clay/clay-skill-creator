# Search: the vocabulary gap, and the only real coverage oracle

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that ran the searches. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

**Search bills quota, not credits — metering is exactly per row returned.** One build's load-bearing
evidence cost **zero credits and 33 rows**, read from `clay search filters-mode fields --source-type
{companies,people}`: free field metadata, and the cheapest useful evidence on the platform. It is routinely
unread.

## The vocabulary gap, measured

**The industry taxonomy is 457 closed values. Of 25 common go-to-market industry terms, 6 exist — a 24% hit
rate.**

| Present | Absent |
|---|---|
| Manufacturing, Insurance, Retail, Real Estate, Education, Hospitality | SaaS, B2B, B2C, Fintech, Healthcare, Cybersecurity, Software, MarTech, HR Tech, E-commerce, Logistics, Legal, Media, Gaming, Biotech, Telecom, Energy, Nonprofit, Government |

**Only 11% of the taxonomy (52 of 457) is a single word.** That is the shape of the mismatch: the taxonomy
is compound-phrase shaped and go-to-market vocabulary is single-word shaped.

**Two failure modes needing different handling.** *Concept absent* — SaaS, B2B, Fintech have no
representation at all, not even as a substring, and need a **user decision** about what to substitute.
*Word-form mismatch* — `Biotech` misses while `Biotechnology` is a value; `Software` misses while six
"… Software Products" compounds exist. The concept is present and the spelling is not, so a candidate list
resolves it cheaply.

**Short terms are dangerous under substring matching:** `AI` matched **53** values including "Airlines and
Aviation", "Air, Water, and Waste Program Management" and "Blockchain Services". Do not substring-match
terms under about five characters.

## Why the failure is silent — from the platform's own guidance

Identical on both axes:

```
Each top-level filter narrows the result set (AND).
Multiple values in one string[] filter broaden matches (OR).
Omit fields instead of passing empty arrays; empty arrays do not restrict results.
```

**An unmatched enum value narrows to nothing and an empty array restricts nothing — opposite directions,
both silent, and both readable as a market-size fact.** That mechanism is what makes the vocabulary gap
consequential rather than cosmetic.

## The two axes spell the same bands differently

| Band | Account axis (`sizes`) | Persona axis (`company_sizes`) |
|---|---|---|
| 51–200 | `'50'` | `'51-200'` |
| 1,001–5,000 | `'1000'` | `'1,001-5,000'` |
| 10,001+ | `'10000'` | `'10,001+'` |

Nine identical bands, two vocabularies. **Revenue bands share spellings exactly**, which is precisely what
makes the headcount split easy to miss — one axis pair agrees, the other does not.

**Band alignment is always outward.** Selecting floors `['50','200','500','1000']` covers **50 through
4,999**, so a band-aligned filter is *wider* than the stated definition, never narrower. The error inflates
the market rather than shrinking it — the direction nobody checks. A stated ceiling can only be enforced by
a per-row exact-count call, which is a priced choice: accept the wider band, or pay per row on rows the
refinement will then discard.

**Numeric filters and returned bands disagree.** A 50–500 numeric member-count filter returned **3 of 8**
companies outside it, in the 11–50 and 501–1,000 bands. Post-validate on the record's own band.

## Not filters, per the platform

Lookalike search, **funding stage**, Fortune 500, unicorn status, technographics, email addresses, phone
numbers, employer lookalikes. Note that `funding_amounts` **is** a filter while funding *stage* is not —
the amount filters, the Series A/B label does not. Each of these is a paid per-row verify, or nothing.

**Low-coverage AI-derived fields need an `is_null` fallback in the same block**, or matching records are
silently excluded — which looks identical to a small market.

**Aggregates are filters, not projections.** `people.count(…)`, `people.exists(…)`, `jobs.count(…)`,
`jobs.exists(…)`. Do not nest them.

**Count queries are forbidden**, and so are `limit` clauses in query mode — which means
`exhaustionReason: query_limit` is **never your limit**, it is the platform's cap under that name.

## Coverage is knowable, and this is the one place with a real oracle

**`total` is always null**, so it tells you nothing. What tells you something:

| State | Meaning |
|---|---|
| `hasMore: true`, reason null | mid-enumeration |
| `hasMore: false`, `exhaustionReason: no_more_results` | **the slice is genuinely exhausted** |
| `hasMore: false`, `exhaustionReason: query_limit` | capped — a floor, not a total |

That distinction is the difference between a population figure that is an estimate and one that is a **sum
of proven-complete slices**, and it is why a population skill can report `exact` at all. Expect `exact` to
be rare: over 39 slice-set combinations only 3 were `exact` and 36 `lower_bound`, which is correct, because
`exact` requires every slice to have exhausted.

Verified live: page 1 at `--limit 5` returned 5 rows with `hasMore: true` and a null reason; page 2 at
`--limit 50` returned 28 rows with `hasMore: false` and `no_more_results`.

**The iterator is forward-only, server-side, has no cursor, and cannot be replayed.** `--limit` accepts
1–500 and defaults to 20; **it does not change spend**, because metering is per row — it only multiplies
your call count by up to 25×. `periodQuota {limit, used, remaining, resetsAt}` rides on every page.
`quota_exceeded` is **terminal on both create and run — do not retry.**

**Result limits are plan-dependent**, and the free tier caps a single search at 50 rows as a hard stop, so
a skill that assumes 500 silently under-enumerates for some installers.

## Row shapes

**Companies:** 12 fields; `size`, `annual_revenue` and `total_funding_amount_range_usd` are **bands** and
there is **no exact headcount**. Records also carry name, domain, profile URL, location and industry —
enough to post-validate every dimension from the record itself, which is how you catch the numeric-filter
disagreement above.

**People:** `company_identifier` is an **array**, so one search covers a whole company list; there is a
14-value seniority vocabulary with `exact` and `floor` match modes; records carry the profile URL,
`latest_experience_{title,company,start_date}` and the `matched_experience` that satisfied the filter.
**Query-mode records carry no URL** — only filters-mode does.

**`domain` on a people record echoes your search anchor**, not the person's employer. Read employment from
`latest_experience_*`.

## Two more things worth knowing before you promise a list

**`hasMore: false` is how a shortfall becomes a fact rather than an apology.** A deliberately narrow
definition exhausted at 3 companies; the honest deliverable is "3 of 10, the company universe is the
binding constraint" plus the levers to widen it, with zero off-definition rows added.

**`filters-mode` and `query-mode` may not expose identical capability**, and one build translated for
filters-mode only. If a dimension is missing from one, check the other before declaring it unfilterable.
