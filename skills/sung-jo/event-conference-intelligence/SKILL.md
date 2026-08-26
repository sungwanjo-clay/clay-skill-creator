---
name: event-conference-intelligence
description: |
  Turn a conference or event roster into a capacity-bounded who-to-meet list before the
  doors open, and a rung-routed follow-up plan inside 24 hours after. Enriches attendees,
  speakers and sponsors, researches each one against the installer's OWN trigger signals
  rather than generic firmographics, and writes a talking point that quotes the evidence
  it read. After the event it places every person on a five-rung engagement ladder read off
  what they actually did, and drafts follow-up matched to the rung. Use whenever someone asks: who
  should I meet at this conference, prep me for our booth, build a target list for an
  event, rank the attendee list, prioritize badge scans, write event follow-up, who do we
  chase after the show, or turn our conference leads into next steps. Do NOT use it to
  discover accounts from scratch (build-prospect-list, tam-builder), to watch signals on a
  standing basis (monitor-buying-signals, signal-sourcer, inbound-triggers-monitor), to
  score inbound form fills (score-inbound-leads), to tier a permanent account book
  (account-tier-scoring), or to write one company brief (company-research-brief). It never
  sends and never writes to a CRM.
category: score-and-qualify
personas: [marketing, account-executive]
touches: read-only
keywords: [event-follow-up]
---

# Event and conference intelligence (bound the list, then rank what you can actually work)

The insight: **the constraint at an event is never the roster, it is how many conversations
a human can hold — so the deliverable is a capacity-bounded top-K, not a scored roster.**
A ranked list of 3,000 attendees is the same artifact as no list, because nobody works past
the top of it. Two failures follow from ignoring the cap, and both are the reported norm:
before the event, someone reads a couple of dozen LinkedIn profiles the night before and
hopes for serendipity; after it, scans sit in a spreadsheet until a generic "great meeting
you" goes out two weeks later. Bounding the list first is what makes the research budget
land on rows a person will actually reach.

The second claim, which forces the whole post-event half: **a badge scan is proximity, not
interest.** A scan records that two devices were near each other — at a raffle drum, on the
way past the booth, in a queue for coffee. Treating that as engagement is precisely what
produces the undifferentiated blast, because the population it addresses never expressed
anything. So engagement depth here is read off **what a person did**, evidence by evidence,
and a row with no evidence is named as unclassifiable rather than folded into the middle.

Both halves therefore refuse to invent: no talking point without a quoted signal, no rung
without an engagement record, no send at all.

## Declared inputs

**Nothing here ships with a value.** Each one is the installer's, not the author's: ask for
it, never substitute a plausible default, and where an answer does not exist say which step
becomes unavailable rather than guessing. Where a default IS defensible it is named below,
and using it means saying so in the output.

| Input | What the installer supplies | If it is missing |
|---|---|---|
| **The roster** | attendee, speaker, sponsor or exhibitor list as CSV, table or Audience; minimum a person name plus a company name or domain | no default — there is nothing to rank. A roster of companies only is a different job: rank accounts, then find people at the top-K |
| **The trigger signals** | their own signals, in priority order — the thing that means a company is buildable for THEM this quarter (hiring a named role, moved off a competitor, a funding stage, a leadership change inside a stated window) | **no default, and the skill stops here.** Generic firmographics are not signals; if they cannot name signals, that conversation IS the deliverable and Step 5 does not run |
| **Capacity K** | how many conversations a human will actually hold, times how many people are working the event | the author's figure was 20 per person for a single event; ask, and if they have no view use it and SAY it is borrowed. Never rank without a cap |
| **Reachability data** | which roster rows are speaking, staffing a sponsor booth, or confirmed vs inferred attendees | the reachability tiebreak in Step 6 is skipped and said to be skipped; ranking still works |
| **Research budget ceiling** | credits available for per-attendee research | state rows times calls times declared cost and get approval before any paid call |
| **The engagement export** | the post-event file, and **which of its fields carry which engagement type** — the scan tool's own column names, plus what a demo request and a logged conversation look like in their data | no default — rung placement is unavailable and every row goes to rung 5. This mapping is a declaration the skill cannot verify |
| **The handoff** | where drafts go and who owns each rung — which CRM or sequencer, which object, which AE or queue | the plan is delivered as a file and nothing is written anywhere, which is the default behaviour regardless |
| **Permitted use** | that this roster and this badge data may be used for outbound, per their own counsel and the event's terms | no default and no check — see what this skill does not claim |

## Step 0 — Verify Clay is working, and say where the work runs

Run `clay whoami; echo "exit_code=$?"`. If it fails or Clay tools are missing, run the Clay
plugin's `setup` skill, restart if it says to, and re-run this skill. Tell the user which
workspace they are in.

**Where the computation happens decides what it costs**, so state it before anything runs.
The ranking, the cut at K and the rung placement are **arithmetic and rule evaluation in
this agent** — zero Clay credits, no per-row charge — and that is the default this skill
assumes. The per-attendee signal research in Step 5 is the opposite: it is a Claygent or AI
column and it **bills per row**, every row, every re-run. That single distinction is why the
cap comes before the research and not after. If the user wants the rung placement running as
a Clay column instead, it bills per row too and the zero-credit claim stops holding; price it
before switching. For paid enrichment, find managed functions with `clay routines list`, then
read each one's declared cost with `clay routines get` (`estimatedCreditCost`; the list call
does not carry costs) before promising anything.

## Step 1 — Collect the definition (interview; do not guess)

1. **The event and the date.** Everything here is perishable: a signal researched three weeks
   out may be stale on the floor, and the post-event half has a stated 24-hour target. Get the
   date and work backwards.
2. **The roster, and where it came from.** An organizer-provided attendee list, a public
   speaker or exhibitor list, and a scraped "attending" list are three different populations
   with three different coverage stories. Record which one it is verbatim — it goes in the
   delivery, because the skill cannot know what fraction of the room it holds.
3. **Their trigger signals, in priority order.** This is the step that gets skipped and the
   one the skill will not proceed without. Ask for signals, not attributes: "hiring a RevOps
   person" is a signal because it says a team is being built; "uses Salesforce" is a
   technographic attribute and belongs in a filter, not here. For every signal, get the
   observable that would count as a match and the window it must fall inside.
4. **Capacity K, and per whom.** Conversations a person will hold, times people working the
   event. If they answer with the roster size, that is a sign the cap has never been faced;
   say what happens to a list nobody reaches the bottom of.
5. **Exclusions.** Own employees, current customers, competitors, partners, consumer domains.
   These are free to drop and every one dropped before Step 5 is money not spent.
6. **The engagement export shape**, if the post-event half is in scope — the field mapping in
   the declared inputs. Ask for it now rather than the morning after, when it is urgent.

## Step 2 — Resolve the roster, deduplicate to decisions

Normalize company to a domain and deduplicate. Two rules, because both change the row count
and therefore the bill:

- **Dedupe people, not companies.** Five attendees from one account are five conversations, not
  one — keep them all, and mark them as one account so the research in Step 5 runs **once per
  domain** and is reused across its people. Research is per-company; talking points are per
  person.
- **Roster rows without a resolvable company do not proceed to paid research.** No domain means
  no signal research is possible; they are listed as unresolved, not enriched hopefully.

State the counts: rows in, people after dedupe, distinct domains, unresolved.

## Step 3 — The free pass, before anything bills

Everything here costs nothing and is what makes the cap affordable. Drop, in this order,
counting each bucket:

1. No resolvable company domain, or a free-mail or consumer domain
2. The installer's own domain and its known aliases
3. Current customers, competitors and partners, per the exclusion list from Step 1
4. Rows outside any stated hard filter the installer set — geography, size band, function

**Compare band strings as bands.** Enrichment payloads return size and revenue as band strings
("10,001+ employees"); never parse one to an integer to test a threshold. If the same payload
also carries an exact headcount integer, use that for a numeric test and say which field you
used.

**Enrichment presence is not liveness.** An acquired or dead company enriches fine on
last-known data. Flag liveness doubt rather than ranking it as a live target.

Report what the free pass removed. A pass that drops nothing usually means the exclusion list
was never collected.

## Step 4 — State the cost, get approval

Before a single paid call: **surviving distinct domains, times research calls per domain, times
the declared cost per call**, and the total. Say plainly that research runs per domain and is
reused across that domain's people, so the bill scales with accounts and not with roster rows.
Then wait for a yes. If the ceiling from the declared inputs is lower than the estimate, do not
silently sample — say how many domains the ceiling covers, and rank on free fields alone below
that line, marking those rows as researched-no.

## Step 5 — Research each domain against their signals, quoting evidence

One research pass per surviving domain, against the installer's signal list from Step 1 and
nothing else. Per signal, the output is three things and never fewer:

- **matched / not matched / could not determine** — three values, no fourth
- **the phrase it read**, quoted, when matched
- **where it read it**, and when that source is dated

Rules, all mandatory:

- **A signal with no quoted evidence is not a match.** It is `could not determine`, which is a
  real answer and is reported as one. A skill that scores confidence without evidence produces
  exactly the fabricated pretext this play exists to replace.
- **`could not determine` is never a `not matched`.** Not matched means the research looked and
  the thing is absent; could not determine means the research could not see. They rank
  differently in Step 6 and they read differently to a rep on the floor.
- **Honour the window.** "New CMO" without a window matches a change from four years ago. Every
  time-bounded signal carries the installer's window and the observed date, and a match outside
  the window is not a match.
- **Never research a person's private life for a talking point.** Signals are about the company
  and the role. Public professional facts only.

## Step 6 — Rank, then cut at K

Ranking is free arithmetic in this agent. The rank key is evaluated in this order, first
difference wins:

1. **Highest-priority signal matched** — the installer's priority order from Step 1, position 1
   being most decisive. A row's key is the best position it matched.
2. **Count of distinct signals matched** — distinct signals, not distinct pieces of evidence for
   one signal. Two sources naming the same funding round is one match.
3. **Reachability**, when the data exists: speaking, then staffing a sponsor booth, then a
   confirmed attendee, then an inferred or scraped attendee. **This ordering is a convention —
   nobody established it**, and it is a tiebreak only, so it can never move a row past a
   better-matched one. If reachability data was not supplied, skip this level and say so.
4. **A stable tiebreak** on normalized domain then person name, so two runs of the same input
   produce the same order and the list can be diffed.

Then **cut at K**, and this is the part that must not be softened:

- Rows above the cut are the who-to-meet list. Rows below it are **explicitly not for this
  event** — delivered as a named overflow list, never as a long tail that implies someone will
  get to it.
- **Zero-match rows rank below every matched row.** They enter the top-K only if matched rows do
  not fill it, and the delivery must state **how many of the K matched nothing** — that number
  is the honest read on whether the signal set fits this event. If most of K matched nothing,
  the signals are wrong for this room, or this room is wrong; say which you suspect and why.
- **There is no minimum match count to be ranked, and nobody established one.** Rather than
  invent a floor, the skill exposes the count so the installer can set one for next time.

**The talking point, per person in the top-K.** One or two lines, built only from that row's
matched signals, each quoting the evidence phrase, and naming which signal it came from. Then
the rule that keeps the whole thing credible: **a row with no matched signal gets no talking
point.** It is marked "no signal found — approach without a pretext, or skip", because a
manufactured opener is worse than a plain introduction and the person will hear the difference.

## Step 7 — After the event: the engagement ladder

Every person in the engagement export is placed on exactly one rung. **Five values, no sixth.**
The rules resolve in order and the first match wins, so a person who requested a demo and also
scanned a badge is rung 1:

| Rung | The evidence that puts them here | Action |
|---|---|---|
| **1** | a demo request, or a meeting booked | AE, **same day** |
| **2** | a substantive conversation logged by a person — a named human, with notes | AE, **within 24 hours**, signed by the person who had the conversation |
| **3** | session or booth activity **plus** at least one matched signal from Step 5 — attended the session, asked a question, took collateral | marketing follow-up, **within 48 hours**, citing the signal |
| **4** | badge scan only | batched nurture |
| **5** | **cannot classify** — no company resolved, or an engagement record that does not map to any rung above | excluded from follow-up, listed with the reason |

**Depth sets the rung. Fit never moves anyone across one.** The pre-event rank orders the queue
*inside* a rung, so an AE works the highest-signal conversations first — and that is the only
thing it does here. A top-K target who only scanned a badge stays in rung 4, because scanning is
what they did.

Three rules that decide whether this holds up:

- **Rung 3 needs both halves.** Session or booth activity with no matched signal is rung 4. The
  signal is what the follow-up cites; with nothing to cite, rung 3's message has no content and
  becomes the generic email under a better label.
- **Rung 5 is not a failure to be minimized.** A ladder with no rung 5 almost always means
  unmappable records were quietly assigned somewhere. Count it and list it.
- **The mapping is the installer's declaration.** Which export field means "demo requested" comes
  from Step 1 and the skill cannot verify it. If a field's meaning is unclear, the rows go to
  rung 5 and the question gets asked — never resolved by inference from the column name.

**The draft, per person on rungs 1 to 4.** It references what actually happened and, where one
exists, the matched signal with its quoted evidence. No draft references anything the row does
not carry. **Nothing is sent and nothing is written to any system** — drafts are delivered for a
human to review and send.

## Step 8 — Deliver both halves, with the coverage

**Before the event.** The top-K list: `person · company · domain · rank position · highest
signal matched · every signal with matched / not matched / could not determine and its quoted
evidence · reachability tier if known · talking point or the explicit no-signal note`. Plus the
overflow list, the drop ledger from Steps 2 and 3 with a count per bucket, the count of top-K
rows that matched nothing, the roster's provenance in the user's own words, and the signal
list as it was used so it can be re-tuned before the next event.

**After the event.** Per person: `rung · the evidence that placed them · the owner · the
deadline · the drafted follow-up`. Plus the count per rung including rung 5 with reasons, and
the reconciliation that makes the coverage legible: **who was in the top-K and never appeared
in the engagement export, and who engaged and was never in the top-K.** Both lists are the
useful output of the whole play — the first says the targeting missed or the meeting did not
happen, the second says the signal set is blind to a population that walked up on its own.

Offer the standing version: the same signal list against the next event's roster, and note that
signals go stale, so a match researched three weeks out is re-checked or re-dated before anyone
walks the floor.

## What this skill does not claim

- The logic came from an interview with its author, not from a system that has run. No formula,
  table or prior implementation was compared against any number in it.
- It has never been run end to end, so there is no measured per-row cost, credit total or
  latency anywhere in it. The cost step states arithmetic over declared prices, not observations.
- Roster coverage is unknown and unknowable from inside the skill. A scraped, partial or
  speaker-only list ranks the slice that was obtainable, and nothing here can say what fraction
  of the room that is.
- Badge-scan and engagement semantics differ per event platform. The mapping from export fields
  to rungs is the installer's declaration and the skill cannot verify it, so a mis-declared field
  mis-routes every row that carries it.
- The 48-hour target on rung 3 and the same-day target on rung 1 are conventions the author
  chose. They were not derived from any measured response-rate decay.
- No minimum signal-match count is set for entering the ranked list, because nobody established
  one. The skill reports the number of unmatched rows in the top-K instead of inventing a floor.
- The reachability ordering in Step 6 is a convention nobody established. It is confined to a
  tiebreak for that reason.
- It does not prove event ROI. It produces ranked targeting and routed follow-up, which are
  inputs to that argument; attribution, pipeline crediting and cost-per-opportunity are not in
  scope and are not attempted.
- Permitted use of attendee and badge data is the installer's to establish. The skill does not
  check event terms, consent basis, or any jurisdiction's rules on processing it.
- It never sends a message and never writes to a CRM or sequencer, so no claim about reply rates
  or follow-up timing achieved is made or checkable here.

## What good looks like

- A rep can answer "why am I meeting this person?" from the row alone — the signal, the quoted
  phrase, and the date it was read.
- The top-K is short enough that someone finishes it, and the overflow list is named as overflow
  rather than implied to be a queue.
- Rows with no signal say so and carry no talking point. Nobody walks up with a manufactured
  opener.
- Rung counts include rung 5, and the reconciliation lists both misses: top-K who never showed,
  and engagers nobody targeted.
- The common mistake, and the one this play is built against: one AI column per attendee that
  emits a paragraph of "personalized insight" with no quoted source, run on the whole roster
  before anyone asked how many conversations a human can hold. It bills per row for text that
  reads well, cannot be audited, and is mostly about people nobody will reach.

## Rules

- MUST collect the installer's own trigger signals before any research, and MUST stop rather
  than substituting generic firmographics; NEVER treat an attribute like a tech-stack match as
  a signal on its own.
- MUST establish capacity K and cut the ranked list at it, delivering the remainder as a named
  overflow list; NEVER deliver a full-roster ranking as the who-to-meet list.
- MUST run the free pass and the cost gate before any paid research, and MUST state rows times
  calls times declared cost and wait for approval.
- MUST research once per domain and reuse across that domain's people; NEVER bill per roster row
  for company-level research.
- MUST quote the evidence phrase for every signal match, and MUST use the three values matched /
  not matched / could not determine; NEVER collapse could-not-determine into not-matched.
- MUST place every post-event person on exactly one of the five rungs, resolved in order, first
  match wins; NEVER let the pre-event rank move a person between rungs, and NEVER put a row with
  no mappable engagement record anywhere but rung 5.
- MUST report rung 5, the drop ledger, the unmatched count inside the top-K, and both sides of
  the reconciliation.
- NEVER write a talking point or a follow-up draft that references anything the row does not
  carry as evidence.
- NEVER send a message, enroll anyone in a sequence, or write to a CRM. The ranked list and the
  reviewed drafts are the deliverable.
- NEVER research a person's private life. Public professional facts about the company and the
  role only.

## Worked example

Ask: "We are sponsoring a 2,400-person RevOps conference in three weeks. Four of us are working
the booth. Get us a who-to-meet list and follow-up that goes out the day after."

**Step 1.** Roster provenance: the organizer's attendee export plus the public speaker list —
recorded as such, because a scraped list would have changed the coverage statement. Signals, in
their priority order: (1) hiring a RevOps or sales-ops role, posted within 90 days; (2) a
competitor named in a public source within 180 days; (3) Series B or later raised within 12
months; (4) a new CMO or CRO within 90 days. Capacity: 20 conversations each, four people, so
**K = 80** — the author's figure, borrowed, and said out loud in the delivery.

**Step 2.** 2,400 rows to 2,318 people after removing duplicate registrations; 1,742 distinct
domains; 96 rows with no resolvable company.

**Step 3.** Free pass drops 611: 96 unresolved, 88 consumer or free-mail domains, 14 own
employees, 41 current customers, 9 competitors, 363 outside their stated size band. 1,707 people
across 1,204 domains survive.

**Step 4.** 1,204 domains times one research call at the declared cost, stated as a total, with
the note that the 1,707 people share those 1,204 calls. Approved.

**Step 5.** 1,204 researched. 291 domains match at least one signal. One example: signal 1
matched on a quoted job-post line for a Revenue Operations Manager, dated 22 days before the
event; signal 2 matched on a quoted case-study sentence naming the competitor as their current
system, undated, so flagged undated; signals 3 and 4 not matched. Another: all four signals
`could not determine` — no recent public material found — and that row is not treated as a
rejection.

**Step 6.** Ranked. 384 people sit at the 291 matched domains, so matched rows fill K = 80 with
room to spare and **no zero-match row enters the top-K** — reported as 0 of 80, which says the
signal set fits this room. The cut lands inside signal-priority band 1, so the delivery notes
that 47 people matching signal 1 fell into overflow — a capacity outcome, not a quality one, and
the argument for a fifth person on the booth next time. Talking point for the row above: "Saw
you are hiring a Revenue Operations Manager, and a case study has you still on the incumbent —
how is that transition looking?" — every clause traceable to a quoted phrase.

**Step 7.** The morning after, the export carries 511 records. Field mapping from Step 1: their
scan tool's `demo_requested` flag, a free-text `booth_notes` field their reps filled, and a
`session_scan` list. Placement: rung 1, 12 demo requests, to AEs the same day. Rung 2, 38
conversations with named reps and notes. Rung 3, 74 with session or booth activity **and** a
matched signal. Rung 4, 361 badge scans only, batched. Rung 5, 26 — 19 with no resolvable
company and 7 whose only record was a field the mapping did not cover, listed with that reason
rather than guessed into rung 4.

One row that shows the rule doing work: a company that ranked 3rd in the top-K, matching three
signals, appears in the export with a badge scan and nothing else. **Rung 4.** Its rank sorts it
to the front of the nurture batch, and nowhere else.

**Step 8.** Reconciliation: 31 of the 80 top-K never appear in the export — the targeting missed
or the meeting did not happen. And 217 engagers were never in the top-K, 9 of them on rung 1 or 2
— which is the finding that changes next quarter's signal list, because their booth attracted a
population the signals were blind to.
