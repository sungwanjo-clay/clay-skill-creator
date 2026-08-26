---
name: clean-and-refresh-contact-data
description: |
  Clean and refresh an existing contact list or CRM export with Clay — verify each
  person is still who the record says (right employer, right title, working email),
  refresh what changed, replace who left, and deliver a current list with per-row
  evidence. Use whenever someone asks: clean up our contact data, refresh our CRM
  contacts, verify these contacts still work there, update stale titles and emails,
  our contact list is old — fix it, or re-enrich our database. Works from a CSV
  or CRM export. It tests staleness by comparing old vs new state (never record
  age), never overwrites good data with empty lookups, and replaces departed
  contacts only under a policy you set. Do NOT use it to clean bare email lists with no refresh intent
  (clean-email-list), to merge duplicates (dedupe-contacts), to watch for job
  changes continuously (track-champion-job-changes), or to enrich net-new signups
  (enrich-signup-users). Built on person enrichment, employment verification,
  email validation, and same-account re-sourcing.
category: verify-and-clean
personas: [revops]
touches: read-only
keywords: [crm-hygiene]
---

# Clean and refresh contact data

The insight: **staleness is a state question, not a time question — and a stale
record is two different problems wearing one flag.** "Rerun anything older than 90
days" re-buys data that hasn't changed and trusts data that has; the honest test is
comparing what the record CLAIMS against what enrichment shows NOW. And when they
disagree, the fork matters: same person, drifted data → REFRESH the fields; person
gone → the record is beyond refresh — REPLACE the contact at the account (or retire
it), per a policy the user chose. Collapsing those two into "update the row" is how
CRMs fill with emails for people who left in 2024.

## Declared inputs

**Nothing here ships with a value.** Each one is the installer's, not the author's: ask for it, never
substitute a plausible default, and where an answer does not exist say which step becomes unavailable
rather than guessing. Where a default IS defensible it is named below, and using it means saying so in
the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **The list** | a CSV or CRM export; per row, ideally name plus company or domain plus email plus profile URL | any subset works — more identifiers make verification cheaper, none makes it impossible |
| **Which fields matter** | employment and title, email deliverability, phone | ask. Every field verified is spend, so verify only what they act on |
| **Replacement policy** | for a departed contact: replace with a same-function equivalent, flag only, or retire | ask **before** finding the first mover — replacement costs a search plus verification per attempt |
| **CRM overwrite policy** | which fields may be overwritten, and which are never touched | this skill delivers a table and a change-log; writing back is their move, and the rules ship with the delivery |
| **Cost ceiling and loop cap** | credits, and how many replacement attempts | state per-row verification cost and the cap, then wait |

## What this skill touches

- **Reads** — the list you supply and the fields you name, plus the enrichment that re-derives them.
- **Writes** — nothing. The deliverable is handed back to you.
- **Never** — writes back to the CRM from this skill — you get the table and the change log.

## Step 0 — Verify Clay is working

Run `clay whoami; echo "exit_code=$?"`. If it fails or Clay tools are missing, run
the Clay plugin's `setup` skill, restart if it says to, and re-run this skill. Tell
the user which workspace you're in. Confirm the person-enrichment arm live and read
declared costs (`references/refresh-mechanics.md` — surfaces drift per workspace).

## Step 1 — Scope (interview; the replacement policy is mandatory)

1. **The list** — CSV/CRM export; per row ideally name + company/domain + email +
   LinkedIn URL (any subset works; more identifiers = cheaper verification).
2. **Which fields matter** — employment/title, email deliverability, phone? Verify
   only what the user acts on; every field verified is spend.
3. **The replacement policy** — departed contact: replace with a same-account
   equivalent (same function/seniority), just flag, or retire? Replacement costs
   search + verification per attempt; get the policy BEFORE finding the first mover.
4. **Overwrite policy for the CRM** — this skill delivers a refreshed table +
  change-log; writing back is the user's move, and the overwrite rules below ship
  with the delivery so nothing good gets clobbered.
5. **Cost + cap** — dedupe first; state per-row verification cost and the
   replacement-loop cap; get approval.

## Step 2 — Verify state per contact (compare, don't assume)

Per unique contact (dedupe on the strongest identifier first — LinkedIn URL beats
email beats name+company):

- **Enrich the person** (LinkedIn URL or email path) and read their CURRENT state:
  employer, title, role start date. Gate on payload values, never run status.
- **Employment verdict — domain-match precedence**: compare the record's account by
  DOMAIN, never name strings (acquisitions and rebrands rename companies without
  moving people); multiple concurrent current roles are real — the primary role
  decides, `multi-role` is a flag, never "departed".
- **Verdict per contact**: `current-confirmed` (employer matches, title may have
  drifted) · `changed` (same account, new title/details) · `departed` (employment
  moved) · `unverifiable` (enrichment empty — an honest state; absence of evidence
  never counts as departed).

## Step 3 — Refresh what drifted (the two-gate discipline)

For current-confirmed and changed rows, per field:

- **Re-enrich gate**: fetch a new value only where the new state is missing or the
  claim is contradicted — not on a timer.
- **Overwrite gate**: the new value replaces the old ONLY when it is non-empty and
  materially different; an empty lookup NEVER clobbers existing data (the classic
  refresh disaster). Contradictions the rules can't resolve → conflict-flagged,
  never silently merged.
- **Email re-validation** on kept rows that will be mailed: one validator's
  vocabulary end to end; catch-all normalizes to `unverified`, never `valid`; a
  role-address never ships as a person's email. Absent validation FLAGS, never
  gates a row out.

## Step 4 — Replace the departed (capped loop, policy-gated)

Per the Step-1 policy, for each `departed` row: source a same-account replacement
matching the lost contact's function × seniority (role-scoped search on the account
domain — quota, not credits), verify the candidate's employment the same way, and
**cap the loop** (max 2 replacement attempts per seat; a seat with no valid
replacement reports `unfilled`, never cycles). The mover themself is
track-champion-job-changes territory — emit them as a FOLLOW lead, don't chase them
here.

## Step 5 — Deliver

Refreshed table: per contact `identity · verdict (current-confirmed / changed /
departed→replaced / departed→unfilled / retired / unverifiable) · refreshed fields
(old → new, per the gates) · email status · flags (multi-role, conflict,
unverified) · evidence (what the enrichment showed, dated)`. Plus the change-log
(every overwrite, with before/after), the movers list (FOLLOW leads), and the
funnel: contacts in, verified, refreshed, replaced, unfilled, unverifiable, credits
measured vs declared. Every input row lands somewhere.

## What good looks like

- **No timer-driven spend** — rows whose state matches their claims cost one
  verification, not a re-enrichment sweep.
- **Nothing good gets clobbered** — the change-log shows zero empty-over-value
  overwrites; conflicts surface as flags.
- **Departed ≠ deleted** — every departed row becomes a replacement, an unfilled
  seat, or a retirement per policy, and the mover ships as a FOLLOW lead.
- **Unverifiable is honest** — thin-coverage people stay flagged, not guessed at
  and not silently dropped.
- The common mistake: refreshing fields on a departed contact. A perfect new email
  for someone who left is polished garbage — the employment verdict comes FIRST.

## Rules

- MUST dedupe and state cost + the replacement policy before any spend; MUST verify
  employment before refreshing any other field.
- MUST compare account identity on domains; MUST treat multi-role as a flag and
  empty enrichment as `unverifiable` — never as departed.
- MUST apply both gates per field: re-enrich only on missing/contradicted, overwrite
  only non-empty-and-different; NEVER let an empty lookup overwrite a value.
- MUST cap replacement loops; NEVER cycle a seat past the cap.
- NEVER write back to the CRM from this skill — deliver the table + change-log; the
  user (or their ops flow) applies it.

## Worked example

Ask: "Refresh our 80-contact target list before the Q4 push — emails and titles."
Policy: replace departed with same-function/seniority; cap 2. Dedupe: 80 → 77
unique. Verification: 61 current-confirmed (9 with title drift → titles refreshed),
6 departed, 10 unverifiable (flagged). Refresh gates: 34 fields fetched (missing or
contradicted only), 31 overwrites (3 conflicts flagged: enrichment title vs a newer
CSV note) — zero empty-over-value events in the change-log. Email pass on the 70
kept: 58 valid, 7 catch-all → `unverified` flag, 5 invalid → re-find queued. The 6
departed: 5 replaced with verified same-account equivalents, 1 unfilled after 2
attempts; all 6 movers delivered as FOLLOW leads. Funnel + change-log + ~70 credits
measured vs declared.
