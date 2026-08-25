# Identity recovery — the search arm, .edu corroboration, and function mechanics

## The reverse-lookup arm (try first, expect misses)

Managed **Enrich Person** — declared inputs: `Professional Profile URL`, `Email`
(trust the declared inputSchema; the prose description claims name+company works — it
does not). Run via CLI: `clay routines runs start` with the items envelope
`{"items":[{"id":"<your-key>","inputs":{"Email":"..."}}]}` piped via `--input -`.

Verified realities:
- **Low yield on email**: real corporate addresses routinely return `complete` + `{}`
  in seconds. The miss is the normal path — that's why the recovery arm exists.
- **Two-level gating**: check run status AND per-item status AND value presence — a
  `complete` run can wrap a `failed` or empty item.
- **Multiple current roles**: when it DOES resolve, the payload can carry more than one
  `is_current: true` experience (board seats, portfolio execs). Read
  `latest_experience` for the primary role; treat multiple current entries as
  multi-role, never as a job change.
- The routines surface exposes **no per-run cost fields** — record the declared
  `estimatedCreditCost` as an estimate and say so.

## The search-recovery arm (work + education rows only)

`clay search filters-mode create --source-type people` with:
- `names`: [best available name] — CSV name first, else the classifier's `guessedName`
  (a hint; if the only name is a non-name handle, skip recovery — searching "Kc
  Builds" is a guess factory);
- `company_identifier`: [the email domain] — **both keys take ARRAYS**; a bare string
  is a validation error.

Reading results:
- Costs **search-result quota, not credits**; an empty result consumes nothing.
- Each record carries `url` (LinkedIn), name, current title, and role start date —
  filters-mode records have URLs; query-mode records do NOT.
- **Gate on match count**: exactly 1 → candidate identity with evidence attached;
  0 → could-not-identify; 2+ → narrow with `job_title_keywords` or flag for review —
  never pick one silently.
- **Ship the canonical URL**: the same person carries different LinkedIn slugs across
  sources; enrich the search hit before shipping its URL, or mark it raw.
- The record's `domain` field **echoes your search anchor**, not current employment —
  employment reads come from the `latest_experience_*` fields only.
- Employment cross-check: compare domains, never name strings; a mismatch may be a job
  change OR a concurrent role (multi-role) — resolve through person enrichment and emit
  `multi-role` / `departed` / `employment unconfirmed` explicitly.

## .edu corroboration (the education branch)

The `.edu` domain is the **school**. Rules:
1. Never use it as `company_identifier` for an employer claim, and never blank the
   signal entirely — search with the available name, then corroborate the candidate by
   the school appearing in their **education history**, not employment.
2. The identified person's *current employer* (from their profile) becomes the company
   candidate — it will usually differ from the `.edu` domain, and that is correct.
3. A candidate whose education doesn't include the school stays unconfirmed — the tie
   was the whole anchor.

## Company resolution mechanics

- Managed **Company Domain** (input: `Company Name*` → `Domain`): use when a row has an
  employer name but no domain. Sanity-check the output — company-name lookups can
  resolve the wrong entity; on low confidence emit `unresolved`, never a proxy.
- Managed **Enrich Company** (input: `Company Identifier*`): once per unique domain
  (Step 5 dedupe), joined back to rows. Headcount arrives as a band string — parse
  bands/ordinals; unparseable → `unresolved` visibly.
- Multi-signup detection is the same computation as the dedupe: count rows per unique
  domain before enrichment; count > 1 → flag the account as a PLG signal and carry the
  count into routing rank.
