---
name: verify-email-deliverability
description: |
  Check whether an email address actually accepts mail before you send to it, using a free
  MX pre-check plus a real mailbox-level validator through Clay. Use whenever someone asks:
  verify this email, is this address deliverable, will this bounce, check if these emails
  are valid, or validate a handful of addresses before a send. It returns a verdict tier —
  valid, catch-all (risky, escalatable), do-not-mail (role/disposable/suppressed), invalid,
  unknown — never a bare yes/no, and it tells you which tiers are safe at volume. Do NOT
  use it to find someone's email in the first place (find-work-email), to bulk-clean and
  refresh a whole list or CRM (clean-email-list), or to identify who owns an address
  (reverse enrichment). It never pattern-guesses addresses and states cost before spending
  any credits.
category: verify-and-clean
personas: [revops, marketing]
mechanism: functions
touches: read-only
keywords: [catch-all-domains]
---

# Verify email deliverability

The insight: **"deliverable" is a tier, not a boolean — and every validator hides the
riskiest tier behind its safest-looking field, in opposite directions.** Verified live:
ZeroBounce returns catch-all as `status: valid` (risk in `sub_status`); Enrichley returns
it as `valid: false` (signal in `result`). Reading one top field either blesses bounces or
discards live mailboxes — the verdict is always the field pair. The reverse trap: a live,
monitored `support@` comes back `do_not_mail` — validators grade for cold-list hygiene,
not readership.

## Declared inputs

**Nothing here ships with a value.** Each one is the installer's, not the author's: ask for it, never
substitute a plausible default, and where an answer does not exist say which step becomes unavailable
rather than guessing. Where a default IS defensible it is named below, and using it means saying so in
the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **The addresses** | exact strings, one per row | no default, and **never construct or repair an address** — a corrected address is a different address |
| **What they are for** | a one-off reply, or a volume send | ask. It changes which confidence tiers are usable at all, not just the reporting |

**If an answer sheet is present beside this skill, load it and ask only for what it does not cover.**
A partial sheet is normal; a value it is missing gets asked for on its own rather than restarting the
interview. **Say which values came from the sheet** before using them — a sheet applied silently is a
wrong field nobody catches. **If there is no sheet, say nothing about sheets** — the check is a file
lookup, not a question, so run the interview as though the feature did not exist rather than reporting
an absence. At delivery, offer to save the answers back (identifiers only — never a token or a
password), private and never published — and phrase the offer so it explains itself: *"want me to save
your answers to a file, so the next person on your team doesn't have to answer these again?"*

## What this skill touches

- **Reads** — the addresses you supply, and the verification providers it runs them through.
- **Writes** — nothing. The deliverable is handed back to you.
- **Never** — writes to a CRM, or sends to an address to test it.

## Step 0 — Verify Clay is working

Run `clay whoami; echo "exit_code=$?"`. If it fails or Clay tools are missing, run the
Clay plugin's `setup` skill (or follow
https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md), restart
if told to, and re-run this skill. Tell the user which workspace you're in.

## Step 1 — Collect the inputs

1. **The address(es) to verify** — exact strings; never construct or "fix" an address.
2. **What they're for**: one-off reply vs volume send changes which tiers are usable.

## Step 2 — Free MX pre-check (zero credits)

Before paying, resolve MX for each distinct domain (any DNS tool). Three shapes:
**NXDOMAIN / no MX** → guaranteed bounce — report invalid free, skip the paid check.
**Null MX** (single record `0 .`) → the domain *declares* it takes no mail — invalid, even
though a record "exists". **Real MX** → proceed.

## Step 3 — Pick a validator (tier AND vocabulary)

Validators are catalog actions, not a managed function — workspaces differ. Discover with
`clay workflows actions list`; fetch the input schema with `clay workflows actions
schema` — never guess field names. Prefer the lowest `priorityTier` (tier 2 =
Clay-managed account, typically ZeroBounce or Enrichley at ~0.1 credits/check; tier 4 =
user's own key — never ask for a key in chat). Vocabulary matters as much as price: you
need a validator that separates catch-all from valid — a binary provider can't produce
the tiers. State per-check cost before running; report the actual charge from run usage
metadata (billing differs even within a tier).

## Step 4 — Run it

For 1–20 addresses, run the action directly (Clay MCP `execute_clay_action`; input
`{"email": "..."}`). Leave "only safe to send" switches OFF — they collapse the tiers
you're here to report. Checks return in seconds, every verdict. For hundreds, recurring
cleans, or addresses you're *finding* rather than checking, hand off to
`clean-email-list` or `find-work-email` and say so.

## Step 5 — Catch-all escalation (optional, ~0.1 credits)

Catch-all isn't a dead end. If the send matters, run Enrichley on the same address: it
probes the specific mailbox — `result: catch_all_validated` means confirmed live (treat
as valid, verified live); plain `catch_all` stays unconfirmable. Production builds send
to the former, throttle or skip the latter.

## What good looks like

Map the observed fields to the verdict:

- ZeroBounce `valid` + `sub_status: ""` (empty string, not null), or Enrichley
  `result: ok` / `catch_all_validated` → **valid**.
- ZeroBounce `valid` + `sub_status: catch_all`, or Enrichley `result: catch_all` →
  **catch-all (risky)** — never report as plain valid; offer Step 5.
- `do_not_mail` (+ `role_based`, `role_based_catch_all`, `disposable`,
  `global_suppression`) → **flagged** — may be genuinely read (support@!) but poison for
  volume; report the sub-reason, the user decides per use.
- `invalid` (+ `mailbox_not_found`, `does_not_accept_mail`) → **invalid**.
- `unknown`, timeouts, empty payloads → **could not verify** — never round either way,
  and never gate on run status: it reports SUCCESS for every verdict; only payload fields
  are data.
- The common mistake: treating the validator as a spam-safety oracle. It answers the
  recipient half only — the top spam causes are sender-side (DNS auth, warming,
  reputation); never promise inbox placement.

## Rules

- MUST run the free MX pre-check before any paid check.
- MUST state per-check and total cost, and get approval before multi-address runs.
- MUST report the raw provider fields alongside the verdict tier.
- NEVER "correct" a typo'd address and verify the corrected version silently.
- NEVER report catch-all, role, or disposable results as plain valid.

## Output

Per address: `email · verdict (valid / catch-all risky / catch-all validated / flagged:
reason / invalid / could not verify) · raw fields · provider`. Multi-address runs add %
per tier plus a one-line recommendation for the stated use.

## Worked example

Ask: "Can I send to jordan.lee@northfield.example and hello@initech-consulting.example?"
MX pre-check: both domains have real MX — proceed. ZeroBounce (~0.1 credits each,
approved): first returns `valid` / `sub_status: ""` → **valid**. Second returns `valid` /
`sub_status: catch_all`; the send matters, so Enrichley on the same address returns
`catch_all_validated` → **valid (probe-confirmed)**. Summary: 2 sendable, ~0.3 credits.

## Listing
- **one-liner:** Check whether an address accepts mail, and report which tier it lands in.
- **problem:** Deliverable is a tier, not a yes or no, and every validator hides its riskiest tier behind its safest-looking field — in opposite directions. One reports catch-all as valid, another reports it as invalid, so reading a single field gets you a confident wrong answer either way.
- **delivers:** A verdict per address across the tiers that matter — valid, catch-all with an escalation path, do-not-mail, invalid, or genuinely unknown — with the provider's raw fields shown and guidance on which tiers are safe to send at volume.
- **example prompt:** Will these thirty addresses bounce if we send to them tomorrow?
- **also asked as:** Is this address deliverable? | Check if these emails are valid | Validate a handful of addresses before a send
