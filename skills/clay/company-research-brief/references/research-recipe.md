# The research recipe — phases, entity edge cases, schema, arms

Distilled from production company-overview builds (domain-anchored Claygent research
with structured output); mechanics re-verified live 2026-08-11 — costs and schemas
drift per workspace, re-check before quoting.

## The three research phases (order is load-bearing)

1. **Domain anchoring — visit the domain first. Always. No exceptions.** Homepage,
   then /about, /product(s), /customers or /case-studies if linked. Non-English
   content gets translated, not abandoned. Only if the homepage fails to load fall
   back to `site:<domain>` searches. Everything in the brief keys off what this
   phase establishes.
2. **Third-party expansion** — only after phase 1 anchors the entity: the enrichment
   payload, LinkedIn company page, press/news (date-windowed), registries where
   relevant. Third-party facts that contradict the site are flags to surface, not
   silent overrides.
3. **Assembly** — structured output; empty strings for indeterminable fields (never
   "N/A" or prose filler); an anti-fabrication pass: is every filled field traceable
   to phase-1 or phase-2 evidence gathered THIS run?

## Pre-gate the anchor (free, before any paid fetch)

An unknown or suspect domain gets a free existence check BEFORE the first scrape: a
DNS resolution (any DNS tool) or a free `http-api-v2` GET (real HTTP status, set a
User-Agent). Verified live: scraping a nonexistent domain does not fail fast — the
scraper's vendor waterfall ground past a 60-second timeout; the dead-anchor verdict
was available for free in under a second. NXDOMAIN / no-resolve → dead anchor,
report, stop. (Note: reserved test TLDs like .example are rejected by the scrape
action's input validation outright.)

## Entity edge cases (the wrong-entity traps)

| Shape | Trap | Handling |
|---|---|---|
| Name collision | three companies share the name | domain wins; given only a name, present candidates before spend |
| Holding vs operating co | brief describes the parent, user means the operator | say which entity the domain hosts; note the hierarchy if visible |
| Franchise / regional clone | site is a local franchisee | brand vs operator called out explicitly |
| Rebrand / acquisition | old name redirects, memory says the old story | report the rebrand as a finding; brief the CURRENT entity |
| Parked / for-sale / dead domain | scrape returns bytes that aren't a company | dead anchor — report it, stop; never brief a parking page |
| Solo practitioner / tiny co | thin site, thin data | brief what exists; open-questions carries the rest — small ≠ fabricate |
| Name-boundary collisions | "Asana Partners" (real-estate firm), "MT Asana" (a ship) surfacing for account "Asana" — live-verified | exact-name boundary: the account name must not be a prefix of a longer org name or a vessel/product name; org-suffix tokens (Partners/Group/Capital/Holdings) after the name = different entity |
| Aggregator/database pages | funding-directory, stock-forecast, stock-roundup pages date-stamped like news | NOT events and NOT developments — a page about the company's history is not something that happened; exclude from developments, usable only as lookup leads |

## Brief schema (structured output)

```
identity:      cleaned_name · domain · entity_type · anchor_evidence
what_they_do:  description · primary_products_or_services · value_prop      [source: their site]
who_they_sell_to: icp · target_personas · target_industries                 [labeled inference]
firmographics: industry · headcount_band · hq · founded · company_type      [source: enrichment payload]
developments:  [{date · event · classification · source_url}]               [date-windowed]
open_questions: [what could not be established, and where it was looked for]
```

Empty string = looked, not found. Every filled field names its source class.

## Arms + live-verified mechanics

| Arm | Cost (live 2026-08-11) | Notes |
|---|---|---|
| Own web access / `scrape-website` | free / ~1 credit per page | `outputFields: ["bodyText","title","links"]` (the enum's body text is `bodyText`; invalid values silently no-op AND bill). SUCCESS ≠ page-exists — the action swallows HTTP status; a 404 can scrape as content. Existence checks: a free `http-api-v2` GET reports real status (set a User-Agent) |
| Managed **Enrich Company** | ~1 credit | input `Company Identifier`; headcount is a band string; the payload's `domain` field can echo a shortener — match identity on `website` |
| News: `find-google-news-results` | ~1 credit | relative-bucket windows (qdr:w/m/y) + RELATIVE date strings — parse to absolute, post-filter to the window; quiet = result field ABSENT (still bills) |
| Premium news: managed **Company News** | ~6.7 credits | true ISO date-time windows (full ISO required despite "YYYY MM DD" field names); Max News Events is ignored; ~1/3 of events undated — route undated out |

Standard brief = anchor (free-2cr) + Enrich Company (1cr) + news window (1cr) ≈ 3
credits; state before running. Read actual charges from usage metadata per call.
