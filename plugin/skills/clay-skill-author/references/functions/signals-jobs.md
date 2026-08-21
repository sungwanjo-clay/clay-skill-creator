# Job postings as a signal, and why "how many roles are open" is not a question

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that spent the credits. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

## Four arms, four "job counts", same company, same day

| Arm and scope | Field | Value |
|---|---|---|
| A, unwindowed | `totalJobsFound` | **8,945** |
| B, unwindowed | `jobCount` | **737** |
| C, unwindowed | `total_job_count` | **384** |
| A, 30-day window | `totalJobsFound` | **332** |
| B, 30-day + Director | `jobCount` | **7** |

**A 23× spread between the three unwindowed totals, and none of them declares its window or the object
it counted.** They are answering different questions — posting events ever observed, currently-tracked
requisitions, network postings of unbounded age — under three names that all read as "how many jobs are
open".

**So the first step of any hiring-signal skill is a forced declaration: object, window, dimension.** A
scope of "count open roles per account" is incoherent as stated, and no amount of care downstream fixes
it.

**And a waterfall is the wrong shape here.** These arms do not share a scale, so a column filled by
whichever resolved first cannot be ranked, thresholded, or diffed over time — which is every use a radar
has for it. Waterfall the boolean and the evidence; never the count. (The general form of this rule is in
`DETERMINISM.md`.)

## Two free consistency checks, and one of them disproves the headline number

**An arm can disprove its own number for free.** Arm A's unwindowed 8,945 ships in the same payload as
`company_object.num_jobs_last_30_days: 332` — and arm A's *windowed* call returns exactly **332**. The
30-day figure is corroborated by two independent paths in one response while the 8,945 is shown not to be
current. Reading the whole payload paid for itself immediately.

**Totals are filter-scoped, and page size does not move them.** Verified in both directions on two arms:
8,945 → 3,136 on a title filter; 737 → 7 on seniority plus a window. And `limit: 1` returned the same
total as `limit: 10`, which is what makes a *filterable* dimension exactly countable.

## Route by filterability, not by price — the arithmetic

| Arm | Cost | Seniority filter | Page cap |
|---|---|---|---|
| A | **0.2** | **none** | 20 |
| B | 1 | yes | returns `jobCount`, the true total, alongside the capped page |
| C | 1 | department only | — |

Arm A dominates on price and **produces an unrankable number for the two dimensions users most often ask
for.** The false-negative rate is computable *before the call*: Director roles were **7 of 332** in the
30-day window, prevalence 2.1%, and with a page cap of 20, `(1 − 0.021)^20` = **65%**. Two times in
three, a seniority read off that page reports **zero against seven open Director requisitions.**

The general rule: `(1 − p)^c` for prevalence `p` and cap `c`. Where the dimension cannot be filtered at
the source, report the figure as a **floor** and exclude it from ranking.

## Per-arm behaviours worth knowing before you pick one

- **Arm B self-reports truncation** — `jobCount` is the true total beside the capped page, so no paging and
  no cap-equality guesswork. Its `identifiers_only` mode **lifts a 10-result cap to 500 at the same price**
  and avoids shipping 6–9 KB of job description per row.
- **Arm C has no usable posting date.** `posted_at` is **null on every row**; only `first_seen_at` and
  `last_seen_at` populate, and first-seen is provider *discovery*, not posting. Posting age is not
  computable from that payload, so a client-side window cross-check is unavailable there.
- **Free riders vanish exactly when you need them.** `company_object` is nested inside each returned job,
  so a query matching **zero** jobs returns no `company_object` — the free 30-day count and employee count
  disappear precisely when the filtered count is zero and a denominator would be most useful.
- **A documented filter set can be mostly absent.** Of four filter parameters a recipe named, one was
  renamed, one was renamed differently, and two were **absent** — function is output-only on that arm, and
  exact-keyword matching does not exist. The recipe's stated architecture (three filter layers, all must
  match) **degrades silently to a keyword search: the call succeeds, a number returns, nothing errors.**
  Its seniority band was also inexpressible — the closest available value carries the C-suite, so
  "director and above but not C-level" can only be post-filtered.

## The growth-rate arms, where the per-unit trap lives

Four arms in one family all report `creditCost: 8`. **Three bill per result found**, and the rate appears
only in a `maxResultsPerSignal` description — default 3, maximum 100 — so a company costs **24 credits at
the default and up to 800** at the cap. The fourth states no basis at all, so its billing is unknown
rather than flat.

**And the derived field corroborates nothing.** 121 new postings against a `historicalAvg` of 108 gives
`changeRatePercent: 12`, which is just 121/108 — the field is computed from the two counts beside it. What
the credits actually buy is `historicalAvg` itself, per department.

**A two-window substitute cost 0.4 credits** and gave +8.4% company-wide (332 against 919/3 = 306.3) —
same direction, different quantity. The 3.6-point gap between two legitimate methods is where a ±25%
verdict band came from, rather than being chosen.

## One negative result worth not re-testing

An arm whose **name, description, inputs and declared output disagree about whether it returns jobs or
people** was never resolved — the probe was blocked by the daily cap. Recorded as a contradiction to
resolve before use, not as a measurement.
