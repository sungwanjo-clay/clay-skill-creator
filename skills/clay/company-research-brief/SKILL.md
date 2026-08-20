---
name: company-research-brief
description: |
  Produce a structured, evidence-linked research brief on one company from its domain
  using Clay — what it does, who it sells to, value prop and products, cleaned name,
  firmographics (industry, headcount, HQ, funding), and recent developments, each
  field carrying its source. Use whenever someone asks: research this company, give
  me a brief on this account, what does this company do, prep me for a call with
  them, build an account one-pager, or summarize a company before outreach. Works
  from a bare domain. Do NOT use it to detect their tech stack in depth
  (detect-tech-stack), to watch accounts for new signals over time
  (monitor-buying-signals), to enrich a whole list of accounts
  (enrich-account-list), or to scrape arbitrary pages into rows (scrape-any-website). Built on
  domain-anchored research plus Clay's managed Enrich Company function and news
  catalog actions; unknowns ship as empty fields, never as filler prose.
category: research
type: task
tags: [none, managed-function, clay-action, persona:sales-reps, persona:founders]
keyword: company-research-brief
---

# Company research brief

The insight: **most wrong briefs are right briefs about the wrong entity — or
yesterday's entity.** Company names collide (holdings, franchises, regional clones,
rebrands), and a model's memory of a company drifts stale the day it's written. So
this skill anchors on the DOMAIN — visit it first, always, before any name-keyed
lookup — disambiguates the entity before spending on enrichment, and builds the brief
from what sources actually say today, each claim carrying its source. A field nothing
supports stays **empty** — never "N/A", never filler, never the model's recollection
dressed as research.

## Declared inputs

**Nothing here ships with a value.** Each one is the installer's, not the author's: ask for it, never
substitute a plausible default, and where an answer does not exist say which step becomes unavailable
rather than guessing. Where a default IS defensible it is named below, and using it means saying so in
the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **The anchor** | the company's domain, ideally | given only a name, resolve the domain first and confirm it if several candidates exist. A wrong domain poisons the whole brief |
| **The angle** | selling in, partnering, or competitive | **seller's brief is the defensible default** and must be stated — it decides which sections go deep |
| **Budget** | credits | the standard brief is a handful of credits; state the number before running, not after |

## Step 0 — Verify Clay is working

Run `clay whoami; echo "exit_code=$?"`. If it fails or Clay tools are missing, run
the Clay plugin's `setup` skill, restart if it says to, and re-run this skill. Tell
the user which workspace you're in. Confirm the managed **Enrich Company** function
and the news catalog action exist and read their declared costs (they drift; see
`references/research-recipe.md`).

## Step 1 — Scope (one company; interview, don't guess)

1. **The anchor** — ideally the domain. Given only a name, resolve the domain FIRST
   and confirm it with the user if multiple candidates exist — a wrong domain
   poisons the entire brief.
2. **The angle** — selling into them? partnering? competitive? This weights which
   sections go deep (default: seller's brief).
3. **Depth + budget** — the standard brief costs ~3 credits (enrichment + news);
   state it before running.

## Step 2 — Anchor on the domain (before any paid call)

Pre-gate an unknown domain for FREE first — a DNS resolution or status probe; a
dead domain hangs the scraper for a minute-plus while the free check answers in a
second (mechanics in the reference). Then fetch the company's own site — homepage,
then /about or /product if present (via this agent's web access or the scrape
action). From the company's OWN words:
what they do, who they serve, products, positioning. Two disciplines:

- **Entity check**: does the site match the company the user means? Name collisions,
  holdings vs operating companies, franchises, and rebrands are the classic wrong-
  entity traps (`references/research-recipe.md` §Entity edge cases). Ambiguity goes
  back to the user BEFORE spend, with the candidates named.
- A scrape that returns content proves a vendor served bytes, not that the page
  exists or is current — treat parked/for-sale/soft-404 pages as a dead anchor and
  report it (that IS a finding: the domain doesn't host the company).

## Step 3 — Enrich (paid, gated on the anchor)

With the entity anchored: run managed **Enrich Company** on the domain for
firmographics — industry, headcount (arrives as a BAND STRING — report the band,
never a fake number), HQ, founding year, type. Cross-check the payload's identity
fields against the anchor (the payload's own `domain` field can echo a marketing/
shortener domain — match on `website`, and a mismatch is a flag, not a silent pick).
Pull recent developments with the news arm, date-windowed (default: last 90 days),
classified per the signal menu; each with date + source link. Funding facts come
from the enrichment or dated news — never from memory.

## Step 4 — Compose the brief (structured, sourced, honest)

Sections (schema in `references/research-recipe.md`): identity (cleaned name, domain,
entity type) · what they do (description, products, value prop — from THEIR site) ·
who they sell to (ICP, target personas/industries — inferred from evidence, marked as
inference) · firmographics (from the enrichment payload, quoted) · recent
developments (dated, linked) · open questions (what could NOT be established).

- Every factual claim carries its source (their site / enrichment payload / dated
  news link). Inference is labeled as inference.
- Empty means empty: a field no source supports ships blank in the structured
  output, and "open questions" says so in prose.
- The model's background knowledge may steer WHERE to look, never fill a field.

## What good looks like

- **The entity is provably the right one** — the brief opens with the anchor
  evidence (domain visited, name/site match), because that's the failure mode that
  invalidates everything else.
- **A reader can click every claim** — site sections, payload fields, dated news.
- **Recency is explicit** — developments are dated; firmographics say "as enriched
  today"; nothing pretends the model's memory is current.
- **The open-questions section has content** — a brief with zero unknowns on a
  private company is a fabrication signal, not thoroughness.
- The common mistake: writing the brief from the model's memory and decorating it
  with a logo-colored header. That produces confident, stale, wrong-entity briefs —
  the three failure modes this skill exists to prevent.

## Rules

- MUST pre-gate unknown domains free (DNS/status) and visit the domain first —
  before any name-keyed lookup or paid call; MUST resolve entity ambiguity with the
  user before spend.
- MUST source every factual claim; inference labeled as inference; unknowns empty.
- MUST report band strings as bands and enrichment identity mismatches as flags.
- NEVER fill any field from the model's own knowledge of the company; NEVER
  fabricate funding, headcount, customers, or news.
- NEVER present a parked/dead/soft-404 domain as a researched company.
- This is one company deep — a LIST of companies is a batch motion (table/workflow);
  say so instead of looping this skill.

## Worked example

Ask: "Prep me a brief on brightloop.example before my call tomorrow."
Anchor: homepage + /product fetched — B2B workflow-automation SaaS for logistics
teams, self-described; entity matches (no collisions found). Enrich Company →
industry "Software Development", size "201-500 employees" (band), HQ Rotterdam,
founded 2018. News, 90-day window → one dated event: a Series B announcement with
source link → recent developments. ICP section: "mid-market logistics operators"
— labeled inference from their case-study page. Open questions: revenue (no
source), US presence (site silent). Brief delivered with per-claim sources;
3 credits, stated up front.
Counter-example: "brief on Meridian" — three plausible Meridians (a fintech, a
consultancy, a medical group) → candidates presented, user picks the domain, THEN
the pipeline runs. No spend before the entity is pinned.
