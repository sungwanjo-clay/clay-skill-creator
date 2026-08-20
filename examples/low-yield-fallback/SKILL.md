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
---

# Route inbound demo requests

> **This skill came from an interview, not from a table.** The source table carried no formulas, so
> the yield check routed to the interview rather than converting. Its thresholds are the creator's
> stated intent — nothing compared them against a system that already ran, and the section below
> saying what it does not claim is where that is written down.
> This example exists to show what that outcome looks like: a complete, usable skill with an honest
> label, instead of a skill fabricated from column names.

The insight: **the request that fits no rule is the one worth a human.** Most routing skills force
every row into a queue, which means the ambiguous ones land wherever the last `else` points.

## Declared inputs

**Nothing here ships with a value.** Each one is the installer's, not the author's: ask for it, never
substitute a plausible default, and where an answer does not exist say which step becomes unavailable
rather than guessing. Where a default IS defensible it is named below, and using it means saying so in
the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **The requests** | `email` required; `company_name` and `job_title` if they have them | no default — with only an email, rule 1 catches most of the volume and that is the correct outcome, not a failure |
| **Queue names** | what their three destinations are actually called | ask — `enterprise` / `mid_market` / `self_serve` are this author's words, and a skill that hardcodes them routes into queues that do not exist |
| **Size thresholds** | the headcount cut between enterprise and mid-market | the author used **1,000 and 50** and those numbers came from an interview, not from a system that ran. Ask; if the installer has no view, use them **and say they are borrowed** |
| **Seniority definition** | which titles count as senior enough to escalate | the author used director-and-above. Ask, because the same title means different things across companies |
| **Human-review triggers** | what makes a request ambiguous *for them* — competitor domains, student roles, partner enquiries | ask — this is the rule the skill exists for, and it is the one most specific to a business |

**Why a thin skill still has five inputs.** The yield check routed this to an interview because the
table held no formulas — but a routing decision is *all* context, so almost everything in it belongs
to the installer. Thresholds an author states in conversation are the easiest thing to hardcode by
accident and the fastest way to make a skill work for exactly one company.

## Step 1 — Take the request

Fields: `email`, `company_name` (optional), `job_title` (optional).

## Step 2 — Route, in precedence order. First match wins.

1. `needs_human_review` — free-email domain with no company name, or a role reading as a student, a
   job seeker, or a competitor. **Checked first**, deliberately.
2. `enterprise` — company size **1,000 or more**, or a director-level-and-above title.
3. `mid_market` — company size **50 or more**.
4. `self_serve` — everything else.

## What this skill does not claim

- Logic came from the creator interview, which has no ground truth in a table — it is the creator's stated intent, not a mechanism verified against a system that already ran.
- No deterministic claims existed to compare, so no threshold was checked against a source formula. Never run against real inbound.

## What good looks like

- `needs_human_review` has a real, non-zero rate. If it is always empty, rule 1 is not firing and
  ambiguous requests are being routed by accident.
- Every routed request carries the field values the decision used.
- The common failure: routing on company name alone. "Acme Consulting" says nothing about size.

## Rules

- MUST evaluate `needs_human_review` before any segment rule.
- MUST emit the values the routing decision used.
- NEVER route a free-email request to enterprise on title alone.
