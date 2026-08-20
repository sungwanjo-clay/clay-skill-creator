# Sourcing arms — live configs, costs, selectors, graduation

Live-verified 2026-08-11 in the eval workspace. Costs and even ACTION CONTRACTS
drift per workspace — the discovery-vs-brand split below was a live schema finding
that contradicts the folklore; re-verify both before quoting.

## Category discovery — Google SERP local results (UDM) via Zenrows

`zenrows-run-scrape` (~1 credit/page live — folklore says 0.005; it drifted 200×),
~20 results/page → ≈0.05 credits/business raw.

- URL shape: `google.com/search?q=<category>+in+<location>&udm=1&num=20&start=<N>`;
  paginate start=0,20,40… to the stated cap.
- Config: `premium_proxy: true, anti_bot: true, js_render: true` — all three, or
  results go missing. Pin the SERP locale with `&hl=en` in the URL: an unpinned
  locale renders localized UI strings that CONCATENATE into business names
  ("Entrega a domicilio<Name>", "Para llevar<Name>" — observed live); strip known
  UI tokens defensively either way.
- **`css_extractor` is accepted and IGNORED on this workspace's action** (verified
  live): the output is the generic extractor field set (bodyText,
  links, emails, phoneNumbers, socialLinks, title…), not the folklore's parallel
  arrays. **Parse the local pack from `bodyText` in code** — the row pattern
  `<Name> <rating>(<review count>)` extracts cleanly by regex (17/17 businesses on
  a live page) and is MORE robust than the rotting CSS-selector map, which is dead
  on this surface anyway. All-empty bodyText = consent/challenge page or locale
  issue, not an empty market — inspect, don't deliver empties.
- Phone/website are inconsistent in list results — get them from the review
  enrichment on survivors instead.

## Brand locations — `openmart-find-local-businesses` (1 credit/call, max 30)

LIVE CONTRACT (schema-verified; NOT a category-discovery action despite the name).
Billing shape: a no-data call returns `SUCCESS_NO_DATA` with **`isRefunded: true`**
— the charge is refunded (net 0); read `isRefunded`, not just totalCost. Payload
per location: full parsed address + place IDs (Google/Yelp), per-location phone,
ratings from both indexes, `ownership_type` (FRANCHISE/…), `brand_id`, and
`parent_company_locations_count` — the franchise-grain dedupe keys ship in-band.
Inputs are the PARENT company's `website` (top-level domain, e.g. "subway.com") or
social URLs, plus `location` (zip/city/state/country) and `limit` (max 30, default
10). It lists locations OF A KNOWN BRAND in a geo — use it for the brand-grain job
and franchise mapping, never expect it to answer "gyms in Brooklyn". Companion:
`openmart-find-smb-decision-makers` (1 credit) for the owner/operator at a location
— hand off to find-decision-makers-at-company semantics.

## Depth on survivors — review enrichments (~1 credit each)

`company-to-google-review-score` / `get-google-review-text` fill rating detail;
the Maps review enrichment fills website/phone/hours where list results are thin.
Survivors only — the funnel exists so this spend is minimal.

## Dedupe mechanics (free; the linchpin)

- Domain normalization: strip scheme/www/query, registrable label via a
  PUBLIC-SUFFIX-AWARE extraction (a naive split kills co.uk/com.au-family domains),
  collapse subpaths (`brand.example/locations/providence` → `brand.example`).
- Grain: location grain keys on name+address (site-less SMBs are normal); brand
  grain collapses on normalized domain / brand name with `location_count` carried.
- Multi-level dedupe for bulk hauls: place id → lat/lon → name+address (the order
  matters; each level catches what the previous missed).

## Scale + graduation

- Ad-hoc sweep ceiling: ~3 cities / ~10 pages per location. Beyond that, or for any
  recurring refresh: in-app table sources (the OpenMart discovery source and native
  Google Maps source exist as TABLE sources, not agent actions — that's where
  category discovery with real filters lives at scale) or a bulk Places pipeline in
  Python (Serper/DataForSEO class; power-user escape hatch — unstable scraping
  services, 1-2 req/s, stop after 4 empty/duplicate pages, multi-level dedupe; no
  Clay credit benefit, so not the enterprise recommendation).
- Native Google Maps enrichment exists but is the weakest-filter, ~1 credit/company
  path — last resort, and its domains need normalization badly (same business under
  different prefixes/subpaths).
