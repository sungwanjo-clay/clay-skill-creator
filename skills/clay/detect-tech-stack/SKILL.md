---
name: detect-tech-stack
description: |
  Detect the technologies a company runs on its website — CMS, ecommerce platform,
  analytics, chat, marketing and ad tools — from a domain, using Clay's managed Website
  Technology Stack function. Use whenever someone asks: what tech stack does this company
  use, do they run Shopify or HubSpot or Marketo, detect technologies on this domain, get
  technographics for these accounts, or find displacement targets from their current
  tools. It returns detected technologies grouped for GTM use, graded by how well the
  evidence supports *current* usage, plus an explicit list of what this method cannot
  see. Do NOT use it to prove a company does NOT use a tool (website detection cannot
  show absence), to detect back-office SaaS — finance, HR, ERP, most CRMs (invisible to
  website scanning; that needs deeper research), or to find people at the company
  (people search). It never pads sparse results and states cost before spending credits.
category: research
type: task
tags: [domain, managed-function, persona:sales-reps, persona:marketing]
keyword: detect-tech-stack
---

# Detect a company's tech stack

The insight: **technographics answer "what can the website prove?", never "what does the
company use?" — and the raw answer is a lifetime archive, not a snapshot.** The managed
function reads the site's source code (BuiltWith-backed), so it sees what runs in a
visitor's browser and is blind to everything server-side or back-office (finance, HR,
ERP always; CRM unless a form embeds it). And it returns *every technology ever
detected*, current and historical, indistinguishably — a current Shopify Plus store
still lists Magento and WordPress from years past. Both verdicts are traps: **detected**
may be history, and **not detected is never evidence of non-use**.

## Declared inputs

**Nothing here ships with a value.** Each one is the installer's, not the author's: ask for it, never
substitute a plausible default, and where an answer does not exist say which step becomes unavailable
rather than guessing. Where a default IS defensible it is named below, and using it means saying so in
the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **Domains** | one hostname per row | given only a company name, resolve the domain first and sanity-check it — a wrong domain returns a confidently wrong stack with no error |
| **The GTM question** | map the visible stack, confirm one named tool, look below the SaaS layer, or detect a back-office competitor | ask **before** spending. This surface fully answers the first, answers the second only when the tool is website-visible, and only contributes partial evidence to the last two |

## Step 0 — Verify Clay is working

Run `clay whoami; echo "exit_code=$?"`. If it fails or Clay tools are missing, run the
Clay plugin's `setup` skill (or follow
https://raw.githubusercontent.com/clay-run/agent-plugins/main/GETTING_STARTED.md),
restart if told to, and re-run this skill. Tell the user which workspace you're in.

## Step 1 — Collect the inputs

1. **Domain(s)** — the function's declared schema takes exactly one input,
   `Company Domain` (hostname). Given only a company name, resolve the domain first (a
   managed Company Domain function exists) and sanity-check it: a wrong domain returns a
   confidently wrong stack with no error.
2. **The GTM question** — which scenario, because it sets the confidence bar:
   (a) map the visible stack; (b) confirm one named tool; (c) infrastructure below the
   SaaS layer; (d) back-office competitor detection. This function fully answers (a),
   answers (b) only when the named tool is website-visible, and only contributes partial
   evidence to (c) and (d) — say which case applies *before* spending, not after.

## Step 2 — Run the managed function

Use the workspace's managed **Website Technology Stack** function — confirm it exists
with `clay routines list` / `get`. ~2 credits per domain, and website-scan providers
**charge on a miss too**; state total cost and get approval before multi-domain runs
(the routines surface reports no measured billing — quote the declared rate as an
estimate). CLI envelope: `{"items":[{"id":"<key>","inputs":{"Company Domain":
"acme.example"}}]}` via `clay routines runs start ... --input -`. Runs return in seconds.
For hundreds of domains or a recurring refresh, move to a table/workflow and say so.

## Step 3 — Read the raw output for what it is

The result is one flat comma-separated string in `Website Tech Stack` — no categories,
no dates. Know its three defects before reporting anything:
- **Not-found is an empty string** with run status still `complete` — gate on content,
  never on status.
- **Silent truncation**: big stacks cut off at exactly 8,192 characters, mid-name — an
  exact-8KB string means the list is incomplete; say so.
- **Pseudo-entries**: BuiltWith metadata rides along (Copyright Year ..., CrUX/Common
  Crawl ranks, stock-exchange listings, hreflang tags, "403 Error"). Filter these out;
  they are not technologies.

Then grade each real finding:
- **Detected, corroborated** — multiple same-family entries (Shopify + Shopify Hosted +
  Shop Pay...) or a structural role you can confirm on the live site. Safe to cite.
- **Detected, uncorroborated** — a single mention; may be years old (the archive
  problem). Usable for whitespace/ICP inference, never quoted as current usage in
  outreach without a live-site check. Contradictory sets (Magento *and* Shopify; three
  different web servers) are the archive showing itself — pick what the live evidence
  supports.
- **Not detected (visible category)** — weak evidence of absence, still not proof.
- **Not assessable (invisible category)** — the scan proves nothing either way; name
  these explicitly when they're what the user asked about.

## What good looks like

- Displacement outreach cites only corroborated detections — a stale archive entry
  quoted as current is the mistake that burns the email.
- A sparse result on a real but minimal site is a finding ("little detectable
  technology"), not a failure to fix by re-running or padding.
- The common mistake: reporting "no CRM detected" as "no CRM". The honest line is "no
  CRM visible on the website — most CRM usage isn't."

## Rules

- MUST state per-domain cost before running, including that misses still bill.
- MUST filter metadata pseudo-entries and flag 8KB-truncated lists as incomplete.
- NEVER report "not detected" as "does not use".
- NEVER present an uncorroborated (possibly historical) detection as current usage.
- NEVER pad a sparse result with plausible-sounding technologies.

## Output

Per domain: technologies grouped by GTM-relevant category (commerce, marketing/ads,
analytics, support, infrastructure), each as `technology · evidence (corroborated /
uncorroborated)`, a truncation note when applicable, then a **not-assessable line**
naming the invisible layers relevant to the user's question, then a one-line readout
tied to their stated scenario.

## Worked example

Ask: "Does northfield-outfitters.example run Shopify? We sell a Shopify competitor."
Scenario (b), website-visible — this surface can answer. Run (~2 credits, approved):
the list includes Shopify, Shopify Hosted, Shop Pay, Shopify Custom Theme → corroborated
current storefront — displacement-qualified. The same list also contains "Magento":
archive noise, contradicted by the corroborated Shopify family — not reported as in
use. Counter-case: "Do they use Workday?" → not assessable — HR systems don't appear in
website source; recommend job-postings/provider research instead of spending here.
