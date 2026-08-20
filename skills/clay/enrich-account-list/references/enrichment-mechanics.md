# Enrichment mechanics — call contracts, normalization rules, composition map

Live-verified 2026-08-11; re-verify per workspace.

## Managed Enrich Company (the core call, ~1 credit/domain)

- Input: `Company Identifier` (required — the VALIDATED domain, never the raw CRM
  value). CLI: `{"items":[{"id":"<key>","inputs":{"Company Identifier":"<domain>"}}]}`
  via `clay routines runs start … --input -`.
- Gate on values at both levels: run `complete` wrapping an empty `{}` item is the
  routine miss; a complete run can wrap a `failed` item. Payload presence ≠ entity
  liveness: dead and acquired companies return last-known firmographics.
- Payload facts that bite:
  - `size` is a BAND STRING ("1,001-5,000 employees") — `parseInt` yields 1,
    `Number()` yields NaN, both flow through ternaries as false. Parse bands to
    ordinals; unparseable → `unknown`.
  - `domain` in the payload can echo a marketing/link-shortener domain — the
    canonical is `website` (normalized). Cross-check against the input domain;
    disagreement = possible wrong-entity match → review flag.
  - Field coverage on real lists (250-account golden evidence): ~80% of live
    companies enrich; industry fills on ~99% of enriched rows, size on ~95% —
    plan the unknown column, it will have content.
- The routines surface exposes no per-run cost accounting — declared estimate,
  say so; in a quiet isolated workspace a balance delta can bound a batch.

## Normalization rules (deterministic, free)

- Band → ordinal map: `1-10 → 1 · 11-50 → 2 · 51-200 → 3 · 201-500 → 4 ·
  501-1,000 → 5 · 1,001-5,000 → 6 · 5,001-10,000 → 7 · 10,001+ → 8`; emit BOTH
  raw band and ordinal (+ a midpoint when a number is genuinely needed).
- `unknown` is a value: absent/unparseable fields emit it explicitly; downstream
  gates must route unknown to their own state, never through a comparison
  (unknown-scored-as-zero silently disqualifies real accounts).
- Revenue arrives in mixed shapes (exact vs bands vs null per company class) —
  same discipline: raw + parsed + unknown.
- Enriched-at date rides every row: this is last-known data; freshness claims
  belong to a re-enrichment cadence, not to the payload.

## Identity screen (free, before any spend)

1. Public-suffix-aware domain normalization → dedupe to unique companies.
2. DNS: NXDOMAIN → `dead-domain`. HTTP probe (contract: non-2xx ERRORS with the
   status named; 2xx returns body only — canonical/og tags carry the redirect
   destination): dead/broken → `dead-domain`; a redirect to another registrable
   domain → validate the destination and note the hop.
3. Name-only rows → resolve-company-domain (verdicts flow back; only `resolved`
   rows are enriched).

## Composition map (what this skill does NOT do)

| Ask | Owner |
|---|---|
| messy names → domains | resolve-company-domain |
| tier/score the accounts | score-inbound-leads (formula/code discipline) |
| tech stack per account | detect-tech-stack |
| watch accounts for events | monitor-buying-signals |
| deep single-account brief | company-research-brief |
| find the buyers there | find-decision-makers-at-company |
| CRM writeback | the user's move (or the enrich-and-route play when built) |

The play composes: resolver → THIS SKILL → scorer/researchers, each with its own
eval'd contract — a monolith that re-implements the neighbors is how account
builds rot.
