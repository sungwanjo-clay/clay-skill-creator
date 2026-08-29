---
name: source-candidates
description: |
  Turn a hiring conversation into a scored candidate list — start from two or three profiles of
  people they would hire, or from the experience they are looking for, then split every criterion
  into what the people search can filter, what only a scorecard can judge, and what is not
  observable at all, and run one query per population who could do the job. Use whenever someone
  asks: find me candidates for this role, source people for this job, build a candidate list from
  this JD or brief, find me more people like these profiles, who could fill this position, find
  senior engineers in Berlin with eight years experience, build a talent pool or sourcing
  pipeline, or source passive candidates. Outreach lands as drafts with one-click links that
  compose in the recruiter's own mailbox; it sends nothing. Do NOT use
  it to translate a sales ICP into filters (icp-matrix-builder), to build a list of buyers to sell
  to (build-prospect-list), to read job postings as a buying signal (hiring-radar), to find
  decision-makers at one named company (find-decision-makers-at-company), to track when your own
  contacts change jobs (track-champion-job-changes), or to write the job description itself.
category: build-lists
personas: [recruiter, founder]
mechanism: functions
touches: writes-records
keywords: []
---

# Source candidates (every criterion goes in one of three places)

The insight: **the criteria that separate a good candidate from a plausible one are exactly the
ones the search cannot hold — and it does not tell you when it drops them.** This is documented
behaviour of Clay's people-search surface, verified against its own query reference, not a guess:

- Its reference instructs that scoring and ranking language — *score*, *weight*, *rank*,
  *prioritise*, *top performers*, *proven track record* — is soft ranking metadata to be left out
  of the query. Those are the words every hiring brief is written in.
- It separately instructs that when some requested criteria cannot be expressed, **a valid query
  is still produced from the rest.** Correct behaviour, and it means no error is raised.
- The surface documents what it cannot filter at all: **detailed skills beyond what job
  descriptions say**, prior founder exit history, emails and phone numbers.

So a brief goes in, a plausible query comes out, a plausible list comes back, and the half of the
brief that was actually discriminating has evaporated. Nothing in the output looks wrong.

**And the obvious repair makes it worse.** Faced with *"strong quantitative background"*, the
instinct is `about contains ("analytics", "SQL")`. Two things then happen at once. It selects for
people who narrate their own skills, which is not the same population as people who have them. And
`contains` **is token-based, whole-word — not substring**, also documented: `contains "engineer"`
matches "Software Engineer" and **not** "engineering". So the proxy quietly excludes on spelling.
A soft criterion belongs on a scorecard or in a separately-queried population. Never in a keyword.

**A second thing follows, and it is why this skill is a conversation rather than a form.** There
**is** a find-people-like-this-profile action — `find-people-lookalikes`, Clay-owned, seeded with a
profile URL. An earlier version of this file said no such thing existed. It does, and the correction
matters twice over, because the action is both more useful and more expensive than that sentence
implied.

**It bills per returned row, and the row count is the output.** Measured 2026-08-28: two seeds of
identical shape returned **4 rows and 25 rows** at **1 credit each**. So a lookalike step cannot be
priced before it runs — *"multiply by rows, out loud"* has nothing to multiply. Say the cost is
per-result and unknown until it returns, carry a cap the installer sets, and reconcile the balance
afterwards. It is not free and it is not allowance-free.

**And the problem was never that the feature is missing. It is that the action chooses the similarity
axes and does not tell you which.** Seeded with one exemplar it returned 26 people anchored on
exactly two things: the literal job-title token, and the seed's employer industry. Both were axes the
hiring manager had explicitly ruled out — *"that's me recognising logos, not a requirement"*. It
reproduced the over-specification error silently, at speed.

That is the case for the conversation. Three profiles a hiring manager likes share dozens of
attributes and **they care about four of them. Which four is judgment that exists only in their
head** — and neither a decomposition nor a lookalike engine recovers it. One of them at least shows
you its filters. Use lookalikes as **a population you seed and then judge**, never as a substitute
for asking. Note the approximation you must disclose either way: the reference maps a named company
in a similarity ask to an **industry anchor**, not an exact match, so the exemplar's employer arrives
as an approximation.

## Declared inputs

**Nothing here ships with a value.** Every row is the installer's. Ask for it, never substitute a
plausible default, and where an answer does not exist say which step becomes unavailable rather
than guessing. Where a default IS defensible it is named below, and using it means saying so in
the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **The role** | the title, and one line on what the person will own | **stop.** Nothing downstream is derivable |
| **The seed** | either two or three profiles of people they would hire, or the specific experience they are looking for, in their words | **stop.** This is the intake; a JD alone is context, not a definition — see Step 1 |
| **Which shared attributes matter** | of everything the seed profiles have in common, the ones that are the point | the skill cannot guess and must not average them. It proposes and asks |
| **Location** | cities, states, countries, or a region — and whether remote counts, and remote from where | no default. "Anywhere" is a real answer that roughly triples yield; never quietly use the company's HQ |
| **Seniority and experience** | a seniority band and a years-of-experience floor or range | no seniority filter at all, per the platform's own guardrail: an unmentioned level is omitted, never guessed |
| **Scorecard criteria and weights** | the criteria a filter cannot hold, each weighted | no default. Weights nobody stated are this skill's opinion wearing numbers |
| **Band cut-offs** | the score at which a candidate is worth contacting | **70 / 40 out of 100 is a stated default** — strong from 70, possible 40–69, weak below. Nothing validates it against hire outcomes; see the gaps |
| **Per-employer cap** | how many candidates may come from one company | **2 is a stated default.** Without a cap one large employer floods the list; the platform supports the cap natively |
| **Do-not-source list** | companies not to approach — current employer, customers, partners, anyone under agreement | no exclusions applied, and the output must say so. This is the omission a recruiter notices from the wrong side |
| **Suppression list** | optional list of people already in the pipeline, by profile URL, or name plus employer | no dedupe against an existing pipeline |
| **Target list size** | how many candidates they want to review | **100–300 is a stated default** for one open role — enough to show the yield split, small enough to read |
| **Contact address** | personal email, work email, or profile link only | **profile link only.** Never default to a work address — see Step 9 |
| **Sender and pitch facts** | who the mail is from and their relation to the role, plus level, comp band if shareable, hiring manager, team size, remote policy, funding or traction, and the one thing that makes this different | the copy step is skipped rather than filled with invention |
| **Availability heuristic** | on or off, and the tenure threshold if on | **off.** It is a guess, not a signal — see Step 4 |

## What this skill touches

- **Reads** — the role and seed you describe, and Clay's people search plus the per-row profile
  enrichment you approve.
- **Writes** — one workflow in your Clay workspace, wrapping the profile enrichment so it can run on
  more than a handful of rows. It is reused across roles and its id is reported in the delivery.
- **Never** — sends a message, enrolls anyone, writes to a CRM, or builds a table or audience. Outreach
  lands as drafts with one-click links that compose in your own mailbox.

## Step 0 — Verify the platform, pull the field list live, and say where the work runs

```
clay whoami; echo "exit_code=$?"
```

Non-zero or no user id: run the Clay plugin's `setup` skill, then re-run. **Say which workspace,
out loud.**

Pull the query surface fresh every run. **Never write a query from a remembered field list:**

```
clay search query-mode reference
```

**Use advanced query mode, and confirm from the reference you just pulled** that it still carries
a years-of-experience field, an education array, and per-experience seniority. The older filters
mode has **no years-of-experience field at all** — a query written there silently drops the single
most common criterion in any brief, and approximates it with a count of roles, which measures
job-hopping. If advanced mode has lost those fields, say so and stop rather than approximating.

**Three separate meters run in this skill and they are not interchangeable.** Cost is a design
property here, not a footnote:

| The work | Where it runs | What it consumes |
|---|---|---|
| The conversation, decomposing exemplars, writing queries, designing the scorecard | the agent | nothing |
| Creating a search (`create`) | the platform | nothing — it returns a `searchId` and no rows |
| Paging results (`run`) | the platform | plan **result** allowance, not credits — capped per request, per search, and per period |
| Reading an exemplar's profile, if not pasted | a per-row enrichment | **credits, per row** — 2–3 rows, priced live in Step 6 |
| Finding an email address | a per-row enrichment | **credits, per row** — the expensive part; priced live in Step 6 |
| Scoring against the scorecard | the agent over paged results, **or** a per-row table column | **free in the agent**; billed per row as a column |
| Building the compose links | the agent, **or** a per-row action column | **free in the agent**; billed per row as a column |

Scoring 300 candidates in the agent costs nothing. Scoring them as a table column bills 300 rows
for the same arithmetic, and is right only when the table is a working surface a team returns to.
Choose deliberately, and say which you chose.

## Step 1 — Have the conversation. It is the intake, not a formality

**A JD is context, never the definition.** It was written to attract applicants and it is full of
the unfilterable — *ownership*, *bar-raiser*, *thrives in ambiguity*. Read it if there is one, and
still do this step.

Ask for the role and where, then take **one of two entry points. Let them pick; both are real:**

**Seed A — exemplars.** *"Give me two or three profiles of people you'd hire for this."* Then go
to Step 2. This is the faster route and usually the more accurate one, because a hiring manager can
recognise the right person long before they can specify them.

**Seed B — described experience.** *"Tell me the specific experience you're looking for."* Then
follow up on what they actually said, not from a checklist. The useful follow-ups are the ones that
distinguish populations: have they done this exact job before or the adjacent one, at what scale,
building the team or running an existing one, and what would rule someone out.

Then **write the whole definition back to them and let them correct it** — the populations, the
three-way split from Step 3, and the scorecard. Do not keep interviewing first. A hiring manager
corrects a wrong population in four words and answers an abstract question in a paragraph that has
to be reinterpreted anyway.

**Never invent a criterion the conversation did not contain.** A role that was never described as
needing a degree does not get a degree filter because it sounds like it should. Anything the skill
proposes rather than heard is **labelled as proposed, on screen, before it reaches a query.**

## Step 2 — Decompose the exemplars, then ask which parts are the point

Only on Seed A. For each profile, get the attributes — either pasted by the installer, free, or by
running a person enrichment on two or three rows, priced live in Step 6. Read off:

current title · seniority · years of experience · current employer, its industry and size ·
previous employers and the shape of the path · education · **and the words they use about their own
work**, which is the raw material for the scorecard, not for a filter.

Then **lay out what the profiles share, and ask which of it is the point.** This is the question the
skill exists to ask, because the exemplar is over-specified: three people the hiring manager likes
may all have been at Series B companies, all have MBAs, and all be in London — and only one of
those three is a requirement. Averaging them produces a query nobody asked for. Guessing produces
one that looks right.

Where they differ, **that is usually two populations, not noise.** An ex-consultant and a lifelong
operator are not one blurred profile with error bars.

**The exemplar's employer becomes an industry anchor, and you must say so.** There is no
similar-companies-by-domain filter for this: the reference requires mapping the company context to
`company.industry` values inside `experiences.any(...)`, and requires telling the user that an
approximation was applied. Do both. **Only** use `clay.filter_to_companies((...))` when the
installer explicitly wants people *at those exact companies* — a farm list, not a similarity anchor.

## Step 3 — Split every criterion three ways, in front of the person who set them

**Show the table. A criterion that appears nowhere has been dropped, and dropping it silently is
the failure this skill exists to prevent.**

**Filterable — goes in the query.** Confirm each against the reference from Step 0:

- years of experience, as a number
- job title, current or past — and title exclusions, which must never be dropped
- seniority, from the experience ladder: founder, owner, board member, partner, C-suite, VP,
  director, head, manager, senior, mid-level, entry, intern
- employment type — full-time, contract, internship, freelance
- named employers: **current** employer by identifier at the top level; **former or any-tenure**
  employer by domain inside the experience expression
- employer industry and size
- role start and end dates, so "has held this title two years" and "started over 30 months ago"
  are both expressible
- location of the person, and separately the location of the role
- education: school, degree, field of study, dates
- languages on the profile
- keywords in headline, about, and experience descriptions — **whole-word, and this is the trap**

**Scorecard — a real criterion, not filterable, judged after the search.** Everything soft lands
here: depth versus breadth, has-done-this-exact-job versus adjacent, quantitative rigour, ownership
versus execution, scrappiness, whether the scale resembles yours, whether they built the team or
inherited it. Each gets a **weight** and **the profile field its evidence is read from** — headline,
about, or experience descriptions.

**Not observable — named out loud, then dropped.** This is a go-to-market database, not a candidate
database:

- **whether they want a job.** There is no open-to-work signal anywhere in it
- **compensation**, current or expected
- **work authorisation**, visa status, notice period
- **detailed skills beyond what the job descriptions say** — documented as not filterable, so a
  tools-and-technologies checklist is scorecard material at best
- **actual performance** — references, attainment, promotion velocity, whether any of it went well
- **prior founder exit history**, documented as not filterable and specifically **not** to be
  approximated by excluding people who are currently founders

**NEVER move a scorecard criterion into the query as a keyword.** The two reasons are at the top of
this file and both are documented: it selects for self-narration, and `contains` matches whole
tokens, so it also excludes on spelling. If a soft criterion must shape the search, the honest form
is **a separate population** whose people genuinely sit somewhere else — not a keyword bolted on.

## Step 4 — One query per population

A **population** is a group defined by where its people sit right now: title, seniority, and the
kind of employer. It comes out of Step 1 or Step 2 — **however many the conversation actually
produced.** One is a legitimate answer. Do not manufacture a third for symmetry.

**Run each one as its own query, and keep the label on every row it returns.** The yield per
population is the part a hiring manager can act on: *"forty here, six there, none at all from
consulting"* answers whether to widen the location, drop a level, or stop waiting for people who
are not there. A single merged query cannot report it — an `and` across populations asks for the
intersection, an `or` returns rows that no longer say which group they came from.

**Hold location, seniority and the experience floor constant across populations.** Those come from
the brief. What varies is title, employer type, and history — otherwise the yields are not
comparable and the split says nothing.

**The syntax that decides whether the query means what you think.** All of this is from the
reference, and each line is a mistake worth not making:

- **`is_similar_to` is the default for job titles** — it expands into synonyms, abbreviations and
  variants, and takes a list: `job_title is_similar_to ("Head of Growth", "VP Growth")`. Switch to
  `=` or `in (...)` only for an explicit exact-title ask, and to `contains` only when the installer
  phrased it as literal keywords.
- **Current employer is top-level; past employer is not.** `clay.filter_to_companies(("acme.com"))`
  at the top level for people **currently** there. `company.domain` inside `experiences.any(...)`
  for former or any-tenure history. Swapping these silently changes who you get.
- **Tenure scope is not neutral.** A generic role search and anything phrased *currently* means
  `is_current = true`; *former*, *past*, *alumni* mean `is_current = false`; *has experience at*
  and *ever worked* mean omitting it. A population defined by where someone **used to** work is a
  different query from one defined by where they are **now**.
- **Do not guess a seniority level.** If the conversation did not name one, omit the filter — the
  title predicate already carries the role. And keep the ladders apart: individual-contributor
  searches must not carry leadership values, and the experience seniority enum is **not** the same
  value set as the job-posting one.
- **Exclusions go in every population's query, identically**, and are never dropped:
  `not experiences.any(is_current = true and company.domain in ("competitor.com"))`, and
  `not job_title is_similar_to ("...")` for the wrong ladder. `is_similar_to` does **not** exclude
  unrelated titles by itself.
- **Cap per employer AFTER the fact, not in the query.** The grammar admits
  `limit N by clay_company_id`, and it parses — but the query reference's own **Query mode policy**
  says *always `select`, never count-mode clauses, never include `limit` clauses*, and it does not
  distinguish `limit` from `limit … by`. **So treat the in-query cap as unsupported** and enforce the
  cap on the rows you page instead. The need is real: without a cap one large employer can be most of
  a list, and thirty people from the same org is one conversation, not thirty options. Verified
  2026-08-28 against the published reference.

A shape verified against the live endpoint on 2026-08-27 — it validated, which says the syntax
parses, not that it is the right query for anyone's role:

```
select from people
where years_of_experience >= 8
  and location_city in ("London")
  and experiences.any(is_current = true
        and seniority in ("Head", "Director")
        and job_title is_similar_to ("Head of Growth", "VP Growth")
        and company.industry in ("Software Development"))
  and not experiences.any(is_current = true and company.domain in ("competitor.com"))
```

No `limit` clause: the policy forbids one, so the per-employer cap of 2 is applied to the paged rows
rather than asked of the query.

**The availability heuristic is off by default and is a guess when on.** With no open-to-work
signal, the nearest thing is tenure — a current role that started more than roughly 30 months ago.
Turning it on trades a large part of the list for a hunch about restlessness. If the installer
wants it, run it as **a second pass over the same population** so both yields are visible and the
cost of the hunch is on screen. **Label it a guess in the output, every time.**

**If asked to filter on a protected characteristic or a proxy for one: say what it is, offer the
clean equivalent, then build what they asked for.** The two that come up are education dates used
to infer age — in the United States an ADEA age-discrimination exposure, and age is protected under
UK and EU equality law — and school or name used to infer ethnicity or nationality. The clean
equivalents are years of experience and seniority, which measure what a brief actually means.
**Say it once, name the exposure, then do as they asked.** This skill warns; it does not refuse,
and it does not repeat the warning.

## Step 5 — The sample gate: 25 rows per population, before anything else

The only step that catches a query which is syntactically valid and semantically wrong.

```
clay search query-mode create --query '<the population query>'   # free; returns {"searchId": "..."}
clay search query-mode run <searchId> --limit 25                 # spends result allowance
```

**There is no cheap count.** The query grammar documents a `count from ...` mode; the endpoint
rejects it — *"Count queries are not supported"* — verified 2026-08-27. So a yield is measured by
paging, and the 25-row sample is the cheapest honest estimate there is.

**The iterator is forward-only with no cursor.** Its position lives on the server and cannot be
replayed: the rows you spend on a sanity check are spent, the next call returns what comes after,
and re-reading the first page means creating the search again.

**Read the field names off this sample. Do not assume the output shape** — confirm what actually
comes back for a profile URL, current employer and current title, and write the delivery against
those keys.

Report per population before proceeding: **rows returned, whether more exist, and three named
profiles a human can eyeball.** Then one decision each — proceed, rewrite, or drop:

- 25 with more available: the population is real. Proceed.
- Under ten with none more: thin here. Say the number and offer the three levers — widen location,
  drop a level, relax the experience floor — as a choice, not a silent fix.
- Zero: **a real answer, and one of the most useful this skill produces.** Never pad it, never
  loosen the query to avoid reporting it, never fold the population into another one.
- Obviously the wrong ladder or industry: the query is wrong, not the market. Rewrite and re-sample.

**On `quota_exceeded` (exit 1, HTTP 402) do not retry blindly** — backoff never helps. Read the
message. A per-request cap: retry once with a smaller `--limit`. A partial per-search or period
allowance: retry once with a limit no larger than what remains, then stop. Fully exhausted, or a
credit limit: **stop paging and say so** — an upgrade or a period reset is the only path, and a
half-built list reported as complete is worse than a stated shortfall. `validation_error` (exit 2)
is a malformed query. `rate_limited` (exit 4) carries a retry-after and may be retried once.

## Step 6 — State the cost, then wait

Nothing past here is free. Put the whole bill on screen and get an explicit yes.

- **Result allowance**: target size per population, plus the 25 already spent on each sample.
- **Per-row enrichment** — reading exemplar profiles, and finding email addresses. **Discover what
  runs and what it costs live, never from memory, because names and prices drift:**

  ```
  clay routines list                  # prefer source: managed for standard enrichment
  clay routines get <routineId>       # the cost the list call omits
  ```

  Name four things before spending: **what runs** (the routine, by name), **what goes in** (which
  fields, from which population's results), **what to verify in the response** (a run can complete
  and return nothing — check for an address, not for success), and **what it costs per row.**
  Multiply by rows, out loud. **This file deliberately carries no price**; quoting one from memory
  is how a build understates by an order of magnitude.
- **Scoring**: free in the agent, per row as a column. Say which, and why.

Then wait. **Spending someone's money without having asked is a defect, not a style.**

## Step 7 — Page the full set, then score it

Page each population separately, reusing its `searchId`, while more results exist:

```
clay search query-mode run <searchId> --limit <n>
```

Stop at that population's target, or when no more exist, or on the quota rules in Step 5 —
whichever comes first. **Keep the population label on every row**; it is the axis the whole
deliverable is built on and cannot be reconstructed later.

Then score against the Step 3 scorecard and nothing else:

- **Every score quotes the profile text it was read from**, one line, naming the phrase. A number
  with no evidence is not reviewable and cannot be defended to a hiring manager.
- **Score only what the scorecard names.** A criterion nobody weighted does not quietly influence
  the number here.

## Step 8 — Verdicts: evidence status first, then the band

Two verdicts. The second is emitted only when the first is `scored` — a band on an empty profile is
the error this split prevents.

**Part A — evidence status, in precedence order. First match wins.**

1. `identity_conflict` — the returned record contradicts the query that found it: current employer
   or title is not what was filtered for. Profile data goes stale. Check it free, from the row you
   already have, before scoring.
2. `suppressed` — on the do-not-source or existing-pipeline list. Reported, never scored, never
   contacted.
3. `unscoreable` — **the profile carries no text the scorecard can read**: no about section, no
   experience descriptions, a headline that repeats the job title. **Not a zero and not a weak
   candidate.** It skews senior, because the people least likely to narrate their work are often
   the ones who have done the most of it. Excluded from the ranking, reported as its own group,
   worth a human skim on title and employer alone.
4. `scored` — the scorecard had evidence to read.

**Part B — the band, only when Part A is `scored`.** Weights sum to 100.

1. `strong` — 70 and above. Worth contacting.
2. `possible` — 40 to 69. Worth a skim first.
3. `weak` — below 40. Reported; not contacted, and never padded into the list to hit a number.

**The 70 and 40 cut-offs are a stated default, not a measured one.** No hire-outcome data anywhere
in this skill validates them. They exist so it is runnable rather than aspirational, and they are
the installer's to move — say what they are, say they are unvalidated, change them without argument.

## Step 9 — Outreach copy, per population, drafts only

**Copy is per population — not per candidate, and not one template for the role.** That is the
point of splitting them: they are moved by different things. The operator wants scope and budget;
the person who builds wants to own a surface; the consultant wants to stop advising and start
owning. One email to all three lands with none of them.

**Derive the pitch from the brief first, show what you extracted, then ask only for the gaps.** A
JD usually carries the mission, scope, team and remote policy. It almost never carries the three
that matter most, so ask for exactly those: **the comp band if it is shareable, the hiring manager,
and who the mail is from and their relation to the role.** A recruiting email with no level, no
money and no named human is a form letter.

Each draft carries: why **this population** specifically, what the person will own, the concrete
facts (level, band, manager, team size, remote policy, traction), one low-friction ask, and the
sender's real name. **No invention** — a fact that was not supplied does not get a sentence. A
fabricated detail about a role surfaces in the first conversation.

### The one-click compose link

A link per candidate that opens a **pre-filled compose window in the recruiter's own mailbox**. Two
columns, because a plain `mailto:` routes to a desktop client and a browser Gmail user needs a web
compose URL:

```
mailto:<address>?subject=<url-encoded subject>&body=<url-encoded body>
https://mail.google.com/mail/?view=cm&fs=1&to=<address>&su=<url-encoded subject>&body=<url-encoded body>
```

**Cap the link body near 900 characters of raw text.** Encoded compose URLs stop working past
roughly 2,000 characters and every newline costs three as `%0A`, so the cap is closer than it looks.
It is also the right length for a first recruiting email. If a body exceeds it, **keep the full copy
in its own column and say the link version is trimmed** — never ship a link that truncates
mid-sentence.

Two ways to build the encoding, at two prices:

- **In the agent, free.** The delivery is a CSV or a table handed over once: encode both fields in
  the agent and write finished URLs into the columns. Nothing bills.
- **As a table column, per row.** The table is the working surface, bodies are generated per row,
  and links must exist for rows arriving later. Use Clay's own URI-encoding action — **discover it
  in the catalog rather than trusting a name in this file:**

  ```
  clay workflows actions list > /tmp/actions.json     # find the Clay-owned URI encoding action
  clay workflows actions schema <packageId> <actionKey>
  ```

  It takes text plus an optional prefix, which is what makes it work: encode the subject first, then
  encode the body with a prefix carrying the scheme, the address and the already-encoded subject.
  Identify it by the **pair** of package id and action key — action keys collide across packages,
  and the wrong one is a different vendor at a different price.

**Which address, and why the default is neither.** The search **does not return email addresses** —
documented — so every compose link depends on a per-row enrichment priced in Step 6. Ask which
address, and say this when you ask: **a recruiting email sent to a work address is delivered onto
the current employer's mail system**, where it may be scanned, archived, or read by someone other
than the candidate. Personal-address finders exist, cost per row, and hit less often.

1. **Profile link only — the default.** No enrichment, no cost, no compose link; the recruiter
   opens the profile and messages there. For passive senior candidates that is often the better
   channel anyway.
2. **Personal address**, when the installer accepts the per-row cost and the lower hit rate.
3. **Work address**, only after they have heard the line above.

Where no address is found the row keeps its profile URL and **no compose link** — never a `mailto:`
built on a guessed address.

**This skill sends nothing and enrols nobody.** There is no send step; copy lands as drafts. That is
a design choice, not a gap: candidate outreach pushed through a cold sales sequencer burns the
sender's domain reputation and reads, to the candidate, exactly like what it is. A link that
composes in the recruiter's own mailbox sends from a real human, returns replies to a real inbox,
and stops at a human's click.

## Step 10 — Deliver, with the shape of what is missing

Per population, in this order:

1. **The yield line** — rows found, target, whether the population is exhausted. **Including the
   populations that returned nothing.**
2. **The bands** — strong, possible, weak, plus `unscoreable`, `suppressed` and `identity_conflict`
   as their own rows. These do not fold into weak.
3. **The candidates**, ranked within band: name, current title and employer, location, years of
   experience, profile URL, score, the evidence line, and the compose link or the reason there is
   none.
4. **The outreach draft** for that population.

Then once, across the run:

- **Every criterion and where it went** — query, scorecard, or not observable. The part a hiring
  manager should read first and will not think to ask for.
- **Every approximation applied**, named: an industry anchor standing in for "companies like
  theirs", a tenure heuristic standing in for availability.
- **What was spent**, in result allowance and credits, against what was approved.
- **What this list is not**: people who match a shape, not people who want the job. No
  availability, compensation or work-authorisation signal exists in this data.

## What this skill does not claim

- The logic came from an interview with its author, not from a workflow that has run end to end.
  No measured yield, cost, response rate or hire rate exists for any of it.
- What was verified live against the platform on 2026-08-27 is narrow and worth separating from the
  rest: that advanced query mode carries years-of-experience, education and per-experience seniority
  fields; that the worked example's query shape parses; that `count from ...` is refused despite
  appearing in the grammar; and that the field list is as quoted. **Nothing about result quality was
  measured.**
- The claim that keyword-proxying a soft criterion loses most of the qualified population is
  reasoned from two documented behaviours — the ranking-language policy and whole-word `contains`.
  **The size of that loss has not been measured**, and it will differ by role and seniority.
- The author's framing of populations — that a merged query fails in both directions — is the
  author's reading, not the creator's claim. **The creator's instruction was that the definition
  should come out of a conversation with the hiring manager, from exemplar profiles or described
  experience, rather than from the skill decomposing a brief on a theory of its own.** The
  one-query-per-population mechanic is theirs; the strength of the merged-query failure is not
  established.
- The 70 and 40 band cut-offs are defaults chosen so the skill runs. No hire-outcome data validates
  them, and nothing here can say whether they match an installer's bar.
- The per-employer cap of 2 is a stated default with no measurement behind it beyond the platform
  supporting the cap natively.
- The tenure-based availability heuristic has never been checked against whether those people moved.
- Scoring reads a public profile, so it measures what someone wrote about their work, not the work.
  That bias runs against senior and less self-promotional candidates in a direction this skill can
  flag but cannot correct.
- No credit price appears anywhere in this file, deliberately — which also means it cannot tell an
  installer in advance what a run will cost.
- The compliance warning in Step 4 names two common exposures in two jurisdictions. It is not legal
  advice, not a complete list, and does not survey the installer's jurisdiction.

## What good looks like

- **The definition came out of a conversation** — two or three exemplar profiles taken apart with
  the hiring manager saying which shared attributes were the point, or their own description of the
  experience followed back. Not a JD parsed on the skill's authority.
- **Every criterion appears in exactly one of three places, and the split is on screen before any
  query runs.** The not-observable ones are named in the final delivery, not quietly absent from it.
- Each population has its own query, yield, bands and copy — **including the one that returned
  zero**, reported as a finding rather than dropped from the summary.
- Every approximation is disclosed where it was applied, not just in a preamble: "companies like
  theirs" became named industries, and the output says so.
- Every scored candidate quotes the profile phrase behind the score, so a hiring manager can
  disagree with one score instead of distrusting all of them.
- Thin profiles sit in `unscoreable` as their own reviewable group. A bottom band full of senior
  people with empty About sections is a list that scored profile-writing.
- No employer is more than the cap of the list.
- Every compose link opens with real facts in it — a level, a named manager, a real sender — or the
  row carries a profile URL and no link.
- **The commonest failure: taking "strong quantitative background" out of the brief, adding
  `about contains ("SQL", "analytics")`, and shipping a valid query, a plausible list, and the
  silent removal of most of the qualified population.** Nothing in the output looks wrong.
- **The second: one merged query.** Two hundred rows, no way to tell which population they came
  from, and a hiring manager who cannot tell whether the market is thin or the query was.
- **The third: averaging the exemplars.** Three profiles share an MBA, a city and a Series B
  employer; all three go into the query; the list comes back small and nobody knows which filter
  did it.

## Rules

- MUST start from a conversation — exemplar profiles or described experience — and MUST write the
  definition back for correction before running anything. NEVER treat a JD as the definition.
- MUST ask which of the exemplars' shared attributes are the point; NEVER average exemplars into a
  single query, and never guess which attribute mattered.
- MUST use advanced query mode and confirm the years-of-experience, education and per-experience
  seniority fields exist in the reference pulled **this run**; NEVER write a query from a remembered
  field list, and never fall back to filters mode, which has no years-of-experience field.
- MUST show the three-way split of every criterion before running anything, and MUST report the
  not-observable ones in the delivery; NEVER let a criterion disappear without being named.
- NEVER convert a scorecard criterion into a keyword filter. Where a soft criterion must shape the
  search it becomes a separate population, or it stays on the scorecard.
- MUST run one query per population and keep the label on every row; NEVER merge populations with
  `or`, and never `and` traits from different populations.
- MUST hold location, seniority and the experience floor constant across populations.
- MUST use `is_similar_to` for job titles by default; MUST use the exact-company function at the top
  level for current employers and employer-domain-inside-experiences for past ones; MUST omit
  seniority when no level was named; MUST keep every exclusion. NEVER mix the experience seniority
  enum with the job-posting one.
- MUST apply a per-employer cap; NEVER deliver a list where one company is most of it.
- MUST disclose every approximation where it was applied — an industry anchor standing in for
  company similarity, tenure standing in for availability.
- MUST sample 25 rows per population and report the count before the full run; MUST report a zero
  yield as a finding; NEVER pad a thin population, and never loosen a query to avoid reporting one.
- MUST state the full cost — result allowance and per-row credits, discovered live — and wait for an
  explicit yes before the first paid call; NEVER quote a credit price from memory or from this file.
- MUST name the routine, its inputs, what to verify in its response, and its per-row cost before any
  enrichment. "Enrich for emails" is an intention, not an instruction.
- MUST mark a profile with no readable text `unscoreable` and exclude it from the ranking; NEVER
  score it low, and never let it fall into the weak band.
- MUST quote the profile evidence behind every score.
- MUST warn once, name the specific exposure, and offer years-of-experience or seniority as the
  clean equivalent when asked to filter on a protected characteristic or a proxy — and MUST then
  build what was asked for. NEVER refuse, and never repeat the warning.
- MUST default the contact address to profile-link-only, and MUST say that a recruiting email to a
  work address is delivered onto the current employer's mail system before that option is chosen.
- MUST cap the compose-link body near 900 characters and keep the untruncated copy in its own
  column; NEVER ship a link that truncates mid-sentence, and never build one on an address the
  enrichment did not return.
- NEVER send anything, enrol anyone in a sequencer, or write to a CRM. Copy lands as drafts and a
  human clicks.
- NEVER state a pitch fact the installer did not supply.
- NEVER invent a criterion the conversation did not contain; anything proposed is labelled as
  proposed.

## Worked example

Asked: *"We're hiring a Head of Growth in London. Here are three people I'd hire."* Three profile
URLs, plus a JD. **The yields below are the shape of a run, not measurements — this skill has not
been run end to end, which is the first thing its does-not-claim section says. The query is real and
parsed on 2026-08-27.**

**Decomposing the three exemplars** produced eleven shared attributes. Read back, the hiring manager
kept four and killed the rest:

| Shared by all three | Their call |
|---|---|
| 8–12 years, Head or Director level | **keep** — the floor |
| currently at B2B SaaS, roughly 50–500 people | **keep**, as an industry and size anchor |
| owned paid acquisition *and* lifecycle | **keep** |
| in London | **keep** |
| MBA | *"coincidence — two of them, and it's not why I like them"* |
| all worked at a company I've heard of | *"that's me recognising logos, not a requirement"* |
| all posted on LinkedIn in the last month | not a criterion |
| two came through consulting | **not a shared attribute — a second population** |

That last row is the conversation earning its place. Averaging the three would have produced one
query with an MBA filter in it and no consultant population at all.

**The split, shown before anything ran.** Of twelve criteria from the JD and the conversation, five
were filterable, four went to the scorecard — *"owned a number, not a channel"* at weight 25,
*"strong quantitative background"* at 20, *"built a team rather than inherited one"* at 20, *scale
resembling ~$10M ARR* at 20, *scrappiness* at 15 — and three were named not-observable: **whether
they want to leave, their comp expectations, and their right to work in the UK.** Those three are
what a recruiter assumes was handled.

**Two populations, two queries, same floor and location in each.** The first, verified to parse:

```
select from people
where years_of_experience >= 8
  and location_city in ("London")
  and experiences.any(is_current = true
        and seniority in ("Head", "Director")
        and job_title is_similar_to ("Head of Growth", "VP Growth")
        and company.industry in ("Software Development"))
  and not experiences.any(is_current = true and company.domain in ("competitor.com"))
```

No `limit` clause: the policy forbids one, so the per-employer cap of 2 is applied to the paged rows
rather than asked of the query.

Disclosed with it: *"companies like the ones your three exemplars are at"* became named industries,
because similarity-by-domain is not available for people searches.

| Population | Sampled (25 max) | Full yield | Read |
|---|---|---|---|
| In-house growth leaders at B2B SaaS | 25, more available | 140 | the population is here |
| Ex-consultants two to four years in-house | 25, more available | 61 | real, and a different pitch |

**Bands on the 140:** 31 strong, 58 possible, 34 weak, **14 `unscoreable`**, 3 `suppressed`. The
fourteen are not weak — they are profiles with no About section and one-line role entries, several
at companies the hiring manager had named unprompted. They went back as their own group for a skim
on title and employer.

**Contact channel:** profile-link-only on the first pass, so nothing was enriched and the paid part
of the bill was zero. After reading the strong band the installer asked for personal addresses on
those 31 rows only — priced live, approved explicitly, 22 of 31 returned an address. Those 22 rows
carry two compose links each. The other nine carry a profile URL and no link.

**Copy:** two drafts. The in-house draft leads with budget and scope; the consultant draft leads
with owning the number instead of advising on it. Both under 900 characters, both naming the hiring
manager, the level and the band, both from the founder rather than a careers alias. Nothing was sent.
