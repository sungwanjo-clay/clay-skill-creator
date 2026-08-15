# Skills that already exist

**Read this before you build.** Generated from the live library — do not edit by hand.

Two reasons it matters more than it looks:

**Duplication is the main way a good skill fails.** If one of these already does your job,
yours will not get picked and neither will theirs, because an agent choosing between two
overlapping descriptions picks unpredictably. Check here first; if something is close,
consider whether yours is genuinely different or whether the existing one needs a change.

**Name your neighbours in your description.** These skills carry **99 cross-references** to
each other (3.3 per skill on average) in the form
*"Do NOT use it for X (`other-skill`)"*. That is not decoration — it is what makes the right
skill get chosen. Find the two or three nearest to yours below and carve against them by name.

30 skills:

| Skill | Category | Type | What it does |
|---|---|---|---|
| `account-health-audit` | verify-and-clean | play | Audit what your account records CLAIM against independently re-derived evidence, and deliver a reviewable field-by-field delta — never a silent overwrite. |
| `account-intelligence-analyst` | research | play | Answer a specific question about a list of accounts with graded, sourced evidence — not a dossier. |
| `account-tier-scoring` | score-and-qualify | play | Tier a book of accounts with Clay — turn a raw account list plus your ICP definition into tuned, auditable tiers (1–4 or A–F) with every score decomposed into visible, editable weights. |
| `build-prospect-list` | build-lists | play | Build a validated prospect list with Clay from a target definition: an ICP (vertical + geography + size band) plus buyer personas → a deduped, suppression-aware list of companies and the rig |
| `buyer-classification` | score-and-qualify | task | Classify each contact in a list as buyer / influencer / not-a-buyer FOR YOUR PRODUCT — is_buyer, a buyer-persona label, confidence, and a one-line rationale per contact, from job title plus  |
| `clean-and-refresh-contact-data` | verify-and-clean | play | Clean and refresh an existing contact list or CRM export with Clay — verify each person is still who the record says (right employer, right title, working email), refresh what changed, repla |
| `clean-email-list` | verify-and-clean | task | Clean a CSV or table of email addresses into keep / risky / remove segments with per-row evidence — free deterministic passes first (dedupe, syntax, role and disposable screens, domain MX ch |
| `company-research-brief` | research | task | Produce a structured, evidence-linked research brief on one company from its domain using Clay — what it does, who it sells to, value prop and products, cleaned name, firmographics (industry |
| `competitive-intelligence-radar` | signals | play | Run a standing radar on a named competitor set with Clay — sweep each competitor's public exhaust (announcements, pricing and positioning changes, leadership hires, funding/M&A, hiring patte |
| `dedupe-contacts` | verify-and-clean | task | Find duplicate contacts in a CSV, Clay table, or CRM list and produce a merge plan — which records are the same person, which record survives, and the evidence for every decision. |
| `detect-tech-stack` | research | task | Detect the technologies a company runs on its website — CMS, ecommerce platform, analytics, chat, marketing and ad tools — from a domain, using Clay's managed Website Technology Stack functi |
| `enrich-account-list` | enrich | play | Enrich a list of accounts with validated firmographics using Clay — industry, headcount, revenue, HQ, founded — one clean row per company, from a CSV or CRM export of domains or names. |
| `enrich-signup-users` | enrich | play | Turn raw product signups — often just an email, frequently a personal one — into routed, evidence-backed leads using Clay: classify every email into a routing enum first, identify the person |
| `find-decision-makers-at-company` | find-contact-data | task | Find the actual decision-makers at a specific company with Clay — the named people, with title, LinkedIn, seniority, and current-employment evidence — for the thing YOU sell, not just whoeve |
| `find-linkedin-profile` | find-contact-data | task | Find a person's LinkedIn profile URL with Clay — from their name and company, or from an email — and validate it before reporting. |
| `find-work-email` | find-contact-data | task | Find and verify a person's work email address using Clay — from their name and company, or their LinkedIn URL. |
| `find-work-phone` | find-contact-data | task | Find a person's work phone number — ideally a validated mobile — using Clay, from their LinkedIn URL or name and company. |
| `headcount-growth` | enrich | task | Measure a company's headcount growth with Clay — employee count plus percent change across 3/6/12/24-month windows, bucketed (shrinking / flat / growing / high-growth / hyper-growth) with a  |
| `hiring-radar` | signals | task | Turn open job postings into a hiring signal you can rank on — pick the arm whose filters can express the roles you care about, count them inside a stated time window, compare against the com |
| `icp-matrix-builder` | score-and-qualify | task | Turn an ICP described in your own words into an executable matrix — every dimension translated into the exact field and allowed value the platform will accept, classified as filterable now,  |
| `inbound-triggers-monitor` | signals | play | Find the people already engaging with you on social and turn each interaction into a dated, deduplicated inbound trigger — pull your team's recent posts, pull who reacted, commented and resh |
| `monitor-buying-signals` | signals | play | Watch a fixed list of target accounts for buying signals with Clay — funding rounds, M&A, executive hires, expansion and other news events — and turn each sweep into an evidence-backed diges |
| `resolve-company-domain` | find-contact-data | task | Resolve a company name to its single canonical operating-company domain with Clay — validated, evidence-backed, or an honest "ambiguous", "not found", or "acquired" flag with the candidates  |
| `score-inbound-leads` | score-and-qualify | play | Turn enriched inbound leads (person + company + ICP fields) into a composite score, an A/B/C/D tier, and a per-lead evidence trail — deterministic weights the user approves, every point trac |
| `scrape-any-website` | research | task | Extract structured data from any web page or site using Clay — pull the fields you name off a URL, a list of URLs, or a directory, and return clean rows. |
| `signal-sourcer` | signals | play | Source net-new accounts from live buying signals with Clay — no starting list: define the events that matter (funding, breach/incident, expansion, leadership change) plus ICP guardrails, and |
| `source-local-businesses` | build-lists | play | Build a deduped, validated list of local businesses with Clay — gyms, restaurants, clinics, retailers, agencies, any physical-location category — from a business type plus locations, or from |
| `tam-builder` | build-lists | play | Enumerate a total addressable market from an ICP definition and report how much of it you can prove you have — a population figure with a per-slice coverage receipt, not a list of whatever f |
| `track-champion-job-changes` | — | — | Build a recurring Clay workflow that watches your champions — past buyers, power users, and key contacts at existing customers — and tells you the moment one changes jobs, then turns each mo |
| `verify-email-deliverability` | verify-and-clean | task | Check whether an email address actually accepts mail before you send to it, using a free MX pre-check plus a real mailbox-level validator through Clay. |

Two of these ship as worked examples in [`examples/`](examples/): `find-linkedin-profile` (single-file) and `resolve-company-domain` (multi-file).
