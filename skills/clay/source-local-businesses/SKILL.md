---
name: source-local-businesses
description: |
  Build a deduped, validated list of local businesses with Clay — gyms, restaurants,
  clinics, retailers, agencies, any physical-location category — from a business type
  plus locations, or from a known brand whose locations you want. Use whenever
  someone asks: find local businesses in a city, source gyms in Brooklyn, build a
  list of HVAC companies near Austin, get all the coffee shops in these zip codes,
  list every location of a franchise brand, or scrape Google Maps listings.
  It asks the franchise question first (location or brand? — that decides the
  dedupe), discovers via the cheapest viable arm, normalizes domains before
  deduping, and ships unique, post-validated survivors. Do NOT use it to source B2B companies by firmographics
  (build-prospect-list), to find people at a company (find-decision-makers-at-company),
  to scrape an arbitrary non-directory page (scrape-any-website), or to research one
  business deeply (company-research-brief). Built on SERP scraping, OpenMart catalog
  actions, and review enrichments.
category: build-lists
type: play
tags: [none, csv, clay-action, search, persona:founders, persona:sales-reps]
keyword: source-local-businesses
---

# Source local businesses

The insight: **local-business lists die by duplication and staleness, not by
discovery — and the dedupe key is a sales question, not a data question.** Finding
200 "gyms in Brooklyn" is trivial; delivering unique, open, in-category businesses is
the work, and whether 12 Crunch Fitness locations are 12 rows or 1 row depends
entirely on whether you sell to the franchisee or the brand. So this skill asks the
franchise question first, discovers with the cheapest viable arm, normalizes domains
before any dedupe (the same business surfaces under prefixes, subpaths, and vanity
URLs), and spends enrichment credits only on survivors.

## Declared inputs

**Nothing here ships with a value.** Each one is the installer's, not the author's: ask for it, never
substitute a plausible default, and where an answer does not exist say which step becomes unavailable
rather than guessing. Where a default IS defensible it is named below, and using it means saying so in
the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **Category and locations** | the business type in their words, plus cities, postcodes or regions — or a known brand whose locations they want | no default; the brand case is a different route entirely |
| **The franchise question** | sell to the location or to the brand | ask. It decides the dedupe grain, and whether franchise-heavy results are signal or noise |
| **Target count and fields** | how many rows, and what each carries | ask — the fields decide whether the review-enrichment arm runs at all |
| **Cost ceiling and hard cap** | credits | state the arm arithmetic — pages × cost, enrichments × survivors — and a hard cap before anything runs |

## What this skill touches

- **Reads** — the category and locations you name, via local business search.
- **Writes** — nothing. The deliverable is handed back to you.
- **Never** — writes to a CRM, enrolls anyone, or contacts a business it sourced.

## Step 0 — Verify Clay is working

Run `clay whoami; echo "exit_code=$?"`. If it fails or Clay tools are missing, run
the Clay plugin's `setup` skill, restart if it says to, and re-run this skill. Tell
the user which workspace you're in. Verify the arms live before promising them —
catalogs differ per workspace and the discovery-vs-brand distinction below was a
live finding, not folklore (`references/sourcing-arms.md`).

## Step 1 — Scope (interview; the franchise question is mandatory)

1. **Category + locations** — the business type in the user's words plus cities/zips/
   regions; OR a known brand whose locations they want (a different arm entirely).
2. **The franchise question** — sell to the LOCATION (each franchisee = a row; dedupe
   on place) or the BRAND (one row per parent; locations become a count)? This
   decides the dedupe grain and whether franchise-heavy results are signal or noise.
3. **Target count + fields** — how many, and what per row (name, address, rating,
   website, phone…). Fields drive whether the review-enrichment arm runs.
4. **Cost + cap** — state the arm arithmetic (pages × cost, enrichments × survivors)
   and a hard cap before anything runs.

## Step 2 — Pick the arm (references/sourcing-arms.md has live configs + costs)

- **Category discovery** → paginated Google-SERP local results (UDM) via the
  rendering scraper with CSS extraction: ~1 credit/page ≈ 20 results/page. Selectors
  ROT quarterly — the reference carries the current map and the fallback.
- **Brand locations** → the OpenMart locations action: give it the parent's website,
  get its locations in a geo (max 30/call). This is a lookup of a KNOWN brand, not
  category discovery — the two jobs are different arms on this surface.
- **Depth on survivors only** → review enrichment (~1 credit/business) for website/
  phone/hours/score, AFTER dedupe — never enrich the raw haul.
- **Scale/recurrence honesty**: multi-city bulk (3+ cities or 500+ places) or a
  recurring refresh belongs in a table/workflow or a bulk pipeline — say so and
  offer the graduation instead of grinding pages ad hoc.

## Step 3 — Discover, bounded

Paginate with an explicit page cap stated up front. Per page: extract name, rating,
review count, address, and any website/detail fields the arm exposes. Every row
carries its source (page URL / call) and the raw fields. Empty or short pages end
pagination honestly — report the boundary, never loop past it.

## Step 4 — Normalize, dedupe, validate (free, in code)

1. **Normalize domains** before comparing: strip protocol/www/tracking, take the
   registrable label (public-suffix aware — naive split kills international TLDs),
   collapse subpaths; a missing website is normal for SMBs, key those rows on
   name+address instead.
2. **Dedupe per the Step-1 grain**: location grain → collapse exact place repeats
   (name+address); brand grain → collapse to parent (shared domain/brand name),
   carrying `location_count` as a column.
3. **Post-validate the category**: SERP keyword matching over-returns (a "gym"
   query returns physio clinics and supplement shops) — a cheap deterministic
   name/category screen first, and only genuinely ambiguous rows to an LLM pass
   that must quote what it ruled on.
4. Rows dropped at each gate are counted by reason — the funnel ships with the list.

## Step 5 — Enrich survivors and deliver

Only survivors get paid depth (website/phone/score via the review arm — costs
stated). Deliver: per business `name · address · category-as-evidenced · rating ·
reviews · website (normalized) · phone · source`, plus the funnel summary: pages
pulled, raw rows, dupes collapsed (by grain), category rejects, survivors, credits
spent (measured per call). A shortfall against the target is reported with which
locations/pages were exhausted — never padded with off-category rows.

## What good looks like

- **The grain matches the motion** — a franchisee-seller gets locations; a
  brand-seller gets parents with location counts. One list can't serve both.
- **The funnel is visible** — raw → deduped → validated counts per stage; a list
  without its funnel hides how much noise it started as.
- **Domains are normalized before dedupe** — prefix/subpath variants of one business
  never survive as two rows.
- **Category is evidenced** — survivors match the ask by name/category evidence, not
  by having appeared in the search.
- The common mistake: enriching the raw haul. Dedupe and validation are free;
  enrichment isn't — spend order is the whole economics of this play.

## Rules

- MUST ask the franchise/grain question and state arm costs + a page cap before any
  run; MUST paginate bounded.
- MUST normalize domains (public-suffix aware) before dedupe; MUST post-validate
  category before enrichment; enrichment on survivors only.
- MUST ship the funnel (counts by rejection reason) with the list.
- NEVER pad a shortfall with off-category rows; NEVER present stale/closed
  businesses knowingly (a dead website on a survivor is a flag).
- NEVER grind ad-hoc pages past the cap or for recurring refreshes — graduate to
  the table/workflow shape and say so.

## Worked example

Ask: "Get me 50 independent coffee shops in Providence for our POS pitch."
Franchise question: selling to the LOCATION, but "independent" means franchise
brands are NOISE → location grain + brand-count filter (any brand with >3 locations
drops). Arm: UDM discovery, 5 pages × 1 credit stated and approved. Discovery: 96
raw rows. Normalize+dedupe: 81 places; brand filter drops 17 chain locations;
category screen drops 9 (two bakeries, a roastery-only, six restaurants that
serve coffee) → 55 survivors. Review enrichment on the 50 requested (50 × ~1
credit, approved) → websites/phones filled where they exist (12 have none — normal
for SMBs, keyed on name+address). Delivered: 50 rows + funnel (96 → 81 → 64 → 55)
+ ~55 credits measured. Counter-ask: "list every Crunch Fitness in New England" —
brand-locations arm with the parent website, 1 credit per geo call, no scraping.
