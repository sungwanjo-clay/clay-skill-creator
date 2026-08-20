# Refresh mechanics — gates, verifier rules, arms, loop caps

Live-verified mechanics 2026-08-12 (this workspace); re-verify per workspace.

## The two staleness gates (state comparison, never a timer)

Per field being refreshed, two complementary gates:

```javascript
// RE-ENRICH — should I fetch a new value for this row/field?
// new value empty AND old value exists → prior fetch failed/decayed, try again
// OR the current-state check contradicts the record's claim
!newValue && !!oldValue  ||  claimContradicted

// OVERWRITE — should the new value replace the old?
// non-empty AND materially different; empties never clobber values
!!newValue && normalize(newValue) !== normalize(oldValue)
```

Time-based gates ("older than 90 days") re-buy unchanged data and trust changed
data — use them only as a scheduling hint for WHEN to run this play, never as the
per-row test.

## The employment verifier (the verdict that orders everything)

Over the enriched person payload:
- **Domain-match takes precedence over name-match** — acquisitions and rebrands
  rename companies without moving people; compare the record's account domain to
  the person's current employer domain.
- **Multiple concurrent current roles are real** (board seats, advisors): the
  primary/latest experience decides employment; extra current roles → `multi-role`
  flag, never "departed".
- **Empty enrichment = `unverifiable`**, an honest state — absence of evidence is
  not evidence of departure (and completion status is not data: complete runs wrap
  empty or failed items routinely; gate on values at both levels).
- Title drift with the same employer = `changed` (refresh), not a mover.

## Arms + costs (verify per workspace)

| Arm | Cost | Role |
|---|---|---|
| Managed Enrich Person (URL/email input) | ~1 credit | the current-state read; the email input arm is LOW-YIELD — prefer the LinkedIn URL path; a miss on the email arm is not a departure verdict |
| Role-scoped people search (filters-mode: company anchor + title keywords) | quota, 0 credits | the replacement arm (same-account re-source) + a recovery identifier arm; records carry URL/title/start date; substring recall — post-validate role identity |
| Email validators (catalog actions) | ~0.1-1 credit | one validator's vocabulary end to end; catch-all → `unverified`, never `valid`; test addresses are honored only by their own validator |
| Free liveness probes (DNS + the HTTP probe) | free | account-domain sanity when an employer domain looks dead — status-honesty lives in the probe's error channel |

## Replacement loop discipline (the freshness loop, capped)

```
departed → role-scoped search at the SAME account (lost contact's function ×
seniority) → verify the candidate's employment (same verifier) →
  verified → replaced (evidence attached)
  failed → attempt++ ; attempt < CAP(2) → widen title vocabulary once → retry
  cap hit → seat = unfilled (report), never cycle
```

Recover vs replace: a cleaner identifier for the SAME person (better LinkedIn URL,
corrected email) is recovery — do it in place. A DIFFERENT person filling the seat
is replacement — policy-gated, capped, evidenced. The mover themself is a FOLLOW
lead for the job-change play, not this loop's problem.

## Overwrite + conflict rules (the change-log contract)

- Every applied change logs `field · old → new · evidence · date`.
- Empty-over-value is structurally impossible (the overwrite gate).
- Two non-empty values disagreeing without a resolution rule → `conflict` flag with
  both values shipped; recency reorders whole records, never per-field (per-field
  most-recent-wins fabricates states that never existed on any source).
- Validity absence FLAGS (`validity: unverified`), never gates a row out — gate only
  on positive invalidity evidence.
