# The scraper ladder — configs, costs, rung tests, failure shapes

Live-verified 2026-08-11 in the eval workspace; costs DRIFT — re-read the catalog per
workspace (`clay workflows actions list`) before quoting. Note the drift already
observed: an older figure of ~0.005-0.1 credits for these actions is still in
circulation; the live
catalog bills BOTH scraper actions at 1 credit, and `http-api-v2` carries no
creditCost field at all (the free-utility shape). Trust the catalog + per-call usage
metadata, never a remembered price.

## Rung 1 — `http-api-v2` (free; true APIs and hidden APIs)

- Config: `{method, url, headers, body}`; parameterize query/page fields per row.
- Finding a hidden API: Chrome DevTools → Network → filter Fetch/XHR → perform the
  search in the UI → copy the request that returns the result JSON → replicate,
  parameterized. Most directories are a thin front-end over exactly this.
- Also the right rung for HTTP HEAD/GET header checks and public REST (GitHub etc.),
  and the STATUS-HONEST probe: non-2xx ERRORS with the status named ("Clay
  received a 404 error"), unlike rung 3's scraper — but a 2xx returns the BODY
  ONLY (no statusCode/finalUrl fields; redirects are followed silently — recover
  the destination from the body's canonical/og:url tags). Some APIs (GitHub) 403 without a User-Agent
  header — always set one.
- Credential hygiene (hard rule): auth headers go in Clay **Named Credentials**,
  referenced — never inlined in a column, a chat, or a skill: an inlined Basic header
  is readable by anyone with table access and WILL eventually leak.

## Rung 2 — URL interpolation (cost = rung 3/4 × fewer pages)

When URL structure is predictable (`/companies/<slug>`, `?page=N`,
`/<city-slug>/listings`), build the URL list by formula from a seed/slug table and
fetch ONLY those pages. Keep 1-2 slug variants when the form is ambiguous. Pagination
idiom: generate `start=0,20,...` URL arrays bounded to a stated page cap.

## Rung 3 — `scrape-website` (~1 credit/page live; static HTML)

- Config: `{url, outputFields: [...], enableJavaScriptRendering, waitFor,
  keepNonText, customRegex}`. The REAL outputFields enum (live schema — the folk
  "text"/"html" values do NOT exist): `title, keywords, description, favicon,
  socialLinks, extractedKeywords, links, emails, phoneNumbers, images, bodyText,
  languagesDetectedFormatted`. Body text is `bodyText`. Bonus fields the folklore
  misses: `emails`, `phoneNumbers`, `socialLinks`, and `customRegex` for arbitrary
  pattern extraction.
- **Invalid outputFields values silently no-op AND still bill** (verified live:
  `["text"]` returned SUCCESS with no content field, 1 credit charged). Validate
  values against the schema before running; an all-empty result may be a wrong enum,
  not an empty page.
- **SUCCESS means "a vendor served bytes", never "the page exists"**: the action is
  a hidden multi-vendor waterfall (`specificVendor`: zenrows-standard, crawlbase
  observed — varies call to call) and exposes NO HTTP status. A genuine 404 URL
  scraped as SUCCESS with a full body in live testing. When page-existence matters,
  corroborate with a free rung-1 status probe — `http-api-v2` GET reports the real
  HTTP status honestly.
- `outputFields: ["links"]` = the canonical index-page move: every link out, filter
  in code, then fetch only the survivors.
- Use for static pages without bot protection; if the body comes back empty with JS
  disabled, try `enableJavaScriptRendering: true` before escalating to rung 4.

## Rung 4 — `zenrows-run-scrape` (~1 credit/page live; rendered + anti-bot)

- Flags: `js_render` (SPAs/dynamic), `premium_proxy` + `anti_bot` (Cloudflare-class
  protection; enable all three for Google-SERP-class targets), `wait_for` (CSS
  selector to await — free reliability).
- `css_extractor` (JSON string of `{field: selector}`) returns named fields instead
  of raw HTML — **column-major parallel arrays** (`{name: [...], title: [...]}`);
  zip them back to row-major before delivering.
- Selector debt: public sites change class names routinely (Google roughly
  quarterly). Ship any selector map with its expiry warning; when extraction goes
  empty, inspect the live DOM and update — don't retry harder.

## Rung tests (spend nothing before the rung is chosen)

1. DevTools Network pass for a JSON API (rung 1) — two minutes, free.
2. Two sample URLs of the same kind: identical structure → interpolate (rung 2).
3. `curl`-grade fetch of one page: real content in plain HTML → rung 3; empty
   body/JS shell → rung 3 with JS rendering; challenge page → rung 4.

## Failure shapes (gate on served content, not call success)

| Shape | Looks like | Verdict |
|---|---|---|
| Soft 404 | HTTP 200 + "not found" page body | failed page, say so |
| Consent/cookie interstitial | 200 + consent boilerplate, none of the expected fields | not the data — retry with rendering/wait, else report |
| Bot challenge | 200 + challenge/captcha markup | blocked — rung 4 with anti_bot is the ONLY sanctioned escalation; still blocked → report blocked |
| Empty extraction | 200 + fields all empty | selectors rotted or wrong rung — inspect, don't deliver empties silently |
| End of pagination | 404/empty past page N | normal — report the boundary, stop |

A run summary must count these per shape; "10 pages, 7 extracted, 2 blocked, 1
soft-404" is an honest result. Silently delivering 7 rows as if 7 was the universe
is not.
