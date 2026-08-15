---
name: route-inbound-demo-requests
description: |
  Route inbound demo requests to the right queue — enterprise sales, mid-market, or self-serve —
  using company size and the requester's role, with an explicit needs_human_review outcome for
  requests that fit no rule. Use whenever someone asks: route our demo requests, who should follow up
  on this inbound, split inbound by segment, or set up demo request triage. Do NOT use it to enrich
  the signup first (enrich-signup-users), to score lead quality (score-inbound-leads), or to write
  the follow-up email (personalized outbound skills).
category: route-and-automate
type: task
tags: [csv, none, persona:revops, persona:marketing]
keyword: route-inbound-demo-requests
proof_status: partial
proof_gaps:
  - stage: stage_p
    reason: Logic came from the creator interview, which has no ground truth in a table — it is the
      creator's stated intent, not a mechanism verified against a system that already ran.
  - stage: stage_e
    reason: No deterministic claims existed to compare, so no threshold was checked against a source
      formula. Never run against real inbound.
---

# Route inbound demo requests

> **This skill came from an interview, not from a table.** The source table carried no formulas, so
> the yield check routed to the interview rather than converting. Its thresholds are the creator's
> stated intent — nothing compared them against a system that already ran, and `proof_gaps` says so.
> This example exists to show what that outcome looks like: a complete, usable skill with an honest
> label, instead of a skill fabricated from column names.

The insight: **the request that fits no rule is the one worth a human.** Most routing skills force
every row into a queue, which means the ambiguous ones land wherever the last `else` points.

## Step 1 — Take the request

Fields: `email`, `company_name` (optional), `job_title` (optional).

## Step 2 — Route, in precedence order. First match wins.

1. `needs_human_review` — free-email domain with no company name, or a role reading as a student, a
   job seeker, or a competitor. **Checked first**, deliberately.
2. `enterprise` — company size **1,000 or more**, or a director-level-and-above title.
3. `mid_market` — company size **50 or more**.
4. `self_serve` — everything else.

## What good looks like

- `needs_human_review` has a real, non-zero rate. If it is always empty, rule 1 is not firing and
  ambiguous requests are being routed by accident.
- Every routed request carries the field values the decision used.
- The common failure: routing on company name alone. "Acme Consulting" says nothing about size.

## Rules

- MUST evaluate `needs_human_review` before any segment rule.
- MUST emit the values the routing decision used.
- NEVER route a free-email request to enterprise on title alone.
