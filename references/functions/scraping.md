# Scraping

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that spent the credits. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

A four-rung ladder, cheapest first, and the discipline is that **an API-shaped target never touches a
scraper**. Live proof that the discipline is worth having: the API target cost **0** where a scraper would
have cost 1 credit per page, and the soft-404 below shows the bare scraper returning wrong-but-plausible
data.

| Rung | Reach for | Cost |
|---|---|---|
| 1 | a true or hidden API — `http-api-v2` | **free** — no `creditCost` field, the free-utility shape |
| 2 | URL interpolation | free |
| 3 | static fetch — `scrape-website` | 1 credit |
| 4 | rendered / anti-bot — a rendering scraper | 1 credit |

**Rung 1 needs a `User-Agent`.** One target 403'd without it — an honest, diagnosable failure, unlike the
next item.

## `scrape-website` swallows the HTTP status

It returned **SUCCESS and a full body for a URL that genuinely 404s**, with no HTTP status exposed anywhere
in the response, while the free `http-api-v2` probe on the same URL honestly errored with the 404. The
vendor answering varies per call — `specificVendor` reveals a hidden multi-vendor waterfall — so the same
URL can behave differently on two calls.

**A served-content gate plus a free status probe is mandatory, not defensive.** This is the single finding
that earns a scraping skill its existence: the bare action serves a soft-404 as data.

## `outputFields` — an invalid value silently no-ops *while billing*

The real enum includes `bodyText`, `title`, `links`, `emails`, `phoneNumbers`, `customRegex`. **The folk
value `"text"` bills and returns nothing** — two calls proved it. Read the enum from the live schema; it is
both different from and richer than the remembered config.

## `css_extractor` is accepted and ignored

On a rendering scrape it was accepted and the output was the generic field set anyway. **Parsing the target
region out of `bodyText` by regex was both cheaper and more robust** — 17 of 17 rows with rating and review
count from one page at 1 credit measured — and it removes the selector-rot dependency entirely.

Two more from the same probe:

- **Pin the locale** (`&hl=en` or equivalent). An unpinned locale bled localised interface strings into the
  extracted business names, concatenated into the values themselves.
- **A dead selector path fails silently** in the same way the ignored extractor does: you get a generic
  payload, not an error.

## Silent truncation

One string output ended **mid-name at exactly 8,192 characters** with no truncation flag. Flag exact-8KB
results as incomplete. Formula cells have a comparable ~8 KB ceiling — route large arrays through an action
cell container rather than a formula.

## A nonexistent domain is expensive to discover by scraping

The vendor waterfall ground past a **60-second timeout with no verdict**, where a free DNS or status check
answers in under a second. Pre-gate. (Reserved and invented test TLDs are rejected at input validation on
some actions, so they are not usable as fixtures there.)

## What was deliberately not exercised

The anti-bot rung was never fired live — no legitimate anti-bot target belongs in an evaluation — so its
configuration carries from production builds rather than from a measurement here, and only its catalogue
presence and 1-credit cost were verified. Browser-extension and hosted-browser paths are a different
surface entirely.
