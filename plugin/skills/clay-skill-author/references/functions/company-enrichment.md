# Company enrichment and firmographics

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that spent the credits. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

| Need | Reach for | Trap |
|---|---|---|
| firmographics from a domain | the managed Enrich Company function, or catalogue arms — two were measured at 1.0 credit each | headcount arrives as a **band string** |
| website tech stack | the managed Website Technology Stack function, 2 credits/run, no variable pricing | provider is a website-visible scanner, so back-office software is structurally invisible. It declares `entityType: contact` despite being company-level |
| employee growth over time | the dedicated growth action | its schema marks the **domain arm "Lower Accuracy"**; the profile-URL arm is the accurate one. A near-namesake action at 8 credits is easy to grab by mistake |
| corporate hierarchy | a corporate-family action, 2 credits | — |
| traffic | a four-arm waterfall exists | waterfall on **distinct accessors** — each provider's output path differs. Cheapest-first with early exit, per `DETERMINISM.md` |

**Cheapest by price is not cheapest by reachability.** One arm at 0.5 credits requires a profile URL, so
from a domain-anchored list it costs 0.5 *plus a resolution call* — dearer than the 1-credit arms that
accept a bare domain, with one more failure point.

## Two providers disagreed by 5,809 people, and each contradicted itself

Same domain, same day, both `success: true`, neither flagging uncertainty:

| Field | Arm A | Arm B |
|---|---|---|
| exact headcount | 17,112 | 11,303 |
| location count | 12 | 1 |
| follower count | 1,623,116 | 1,345,345 |

And inside single payloads:

- `employee_count: 17112` beside `size: "5,001-10,000 employees"` — **the count sits outside the band the
  same payload reports.**
- `employeeCount: 11303` with `employee_range: "5001 to 10000"` (excludes it) **and**
  `employeeCountRange: {10001, 20000}` (includes it) — two range fields disagreeing in one record.
- `revenue: 999999999` beside `revenue_formatted: "$100M to <$1B"` — a saturation sentinel one below 10⁹,
  not a measurement.
- `founded_year: "2010"` (string) beside `foundedOn.year: 2010` (int) — one value, two types.

A third arm independently reproduced arm A's count *exactly*, so arm B is the outlier across three
readings while arm A's own **band** is the outlier within arm A. **None of that is reachable from one
call.**

**What this forces on any skill that audits a stored field.** There is no "re-derived truth" to grade
against: two mainstream providers are 5,809 people apart on a basic firmographic and neither can reconcile
its own record. So deliver a **graded delta with both values visible**, run a self-consistency check that
**withholds the vote** of an arm contradicting itself, and let a `disputed` verdict resolve toward
nothing. A design that overwrites would have shipped a confident wrong answer. Expect "cannot say" to be
the most common outcome and treat that as correct — in one enumeration of 128 two-arm combinations, 110
landed `unverified`.

## Identity cross-checks

**Read `website`, never `domain`.** In a real payload the `domain` field held a link-shortener domain while
`website` held the canonical one. A rule that reads `domain` raises a false mismatch on a correct record.

**Watch for a saturation sentinel rather than interpreting it.** One field returned **−524**, the exact
negation of a `num_technologies: 524` beside it.

## The tech-stack arm returns something quite different from what its provider is documented to return

Four measured defects, all of which a draft written from documentation got wrong:

1. **Flat comma-separated string** in one field — no categories, no dates. Grouping is the agent's job and
   **date-based recency grading is impossible on this surface.**
2. **A lifetime archive, not a snapshot.** A current storefront also listed three superseded platforms; a
   minimal site listed three web servers simultaneously. Current and historical detections are
   indistinguishable, so a recency grade has to be replaced by a **corroboration** grade — family count
   plus live-site confirmation — and "archive noise" becomes an explicit concept.
3. **Silent truncation at exactly 8,192 characters**, ending mid-name, with no flag. Flag exact-8KB results
   as incomplete.
4. **Metadata pseudo-entries ride along** — copyright-year tags, crawl-rank markers, stock-exchange
   listings, hreflang tags, even a `403 Error` string — and must be filtered before reporting.

Also: not-found returns `status: complete` with the output field **present but empty-string valued**. The
field existing is not data.

The axis that survived contact: **detected ≠ used-now, and not-detected ≠ not-used.** The eval turned that
from a caveat into the skill's central reading procedure.

## Growth over time

**The echo is the only wrong-entity detector** — the general rule is in `DETERMINISM.md`; here is where
the comparator gets built. Compare on the registrable label and **exclude the TLD**: `com`
substring-matches "company" in every profile URL and washes the check out entirely.

**Nine windows, and the 1-month and 48/60-month ones come back null *inside a hit*.** A null is not a zero,
and the most recent window is the one a freshness-minded author reaches for first.

**A miss is empty-success and still bills** — `success: true`, `result: {}`, a "Company Not Found" preview,
1 credit measured. Report `unverifiable` and count the credit.

**Percentages never ship without base counts.** +300% on 3→12 people reads as hyper-growth; a micro base
under about 50 should never headline a verdict. And read two windows together rather than one: a "growing"
12-month figure decomposed to *decelerating* against the 3-month window in the live smoke.
