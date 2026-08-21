# Email validators: the field pairs invert

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that spent the credits. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

**A validator read as a boolean is wrong in the most expensive direction.** This leaf is mostly one
finding and its consequences.

## Catch-all hides inside the safest-looking field, in opposite directions per provider

| Verdict | Provider A | Provider B |
|---|---|---|
| catch-all | `status: valid` + `sub_status: catch_all` | `valid: false` + `result: catch_all` |
| plain valid | `valid` + `sub_status: ""` — **empty string, not null** | `valid: true` |
| probed-live catch-all | — | `result: catch_all_validated`, `valid: true` |

**Map field PAIRS, never one field.** On provider A a catch-all address sits under `status: valid`; a
status-only reader blesses it. On provider B the same condition sits under `valid: false`; a
`valid`-only reader discards a real address. The inversion is the whole insight, and the two errors run
in opposite directions.

**Catch-all is a per-validator verdict, not a fact about the domain.** On one real domain, provider A
answered `invalid` / `mailbox_not_found` — a mailbox-level answer — where provider B graded
`catch_all`. **Stay inside one validator's vocabulary end to end;** mixing them produces a domain verdict
neither provider made.

**Catch-all is recoverable at the mailbox level.** `catch_all_validated` distinguishes a probed-live
mailbox from an unconfirmable one, reproduced twice, one call apart from a plain `catch_all` on a public
role address at the same domain. Production builds recover **20–40%** of a catch-all domain this way,
which is the difference between a dead-end and a segment.

## Verdicts that mean something other than what they say

- **`do_not_mail` is not undeliverable.** A genuinely monitored, publicly listed `support@` mailbox came
  back `do_not_mail` / `role_based_catch_all`. **Validators grade for cold-list hygiene, not for
  readership.** Report the tier and the sub-reason; never translate it to "dead". A second observation
  from the same family: a well-known company's public support address returned
  `invalid` / `mailbox_not_found` because they had retired the mailbox in favour of a portal — so
  "known-deliverable" assumptions about role addresses rot too.
- **`unknown` / `mail_server_temporary_error`** is the common retryable shape. It is its own segment,
  never rounded to valid or invalid, and the user decides whether to spend more checks.
- **A freemail address can validate as deliverable** — `valid` / `sub_status: alternate` with
  `free_email: true`. **A mailbox verdict never overrides a policy segment**, and a "valid" verdict on
  freemail is not an identity claim.
- **Disposable providers come back as a suppression tier**, `do_not_mail` / `global_suppression` with
  `free_email: true` — which is the validator agreeing with a free screen you could have run first.
- **Timing is symmetric here** — seconds for every verdict — unlike find-email waterfalls, where
  not-found is the slow path.

## Choose the validator by its vocabulary, not by its price tier

**A binary valid/invalid provider cannot produce the tiers a triage skill reports.** If the deliverable
distinguishes keep / risky / remove / could-not-verify, the validator has to be able to express
catch-all and a suppression reason. Price is the second question.

## Provider test addresses are honoured only by their own validator

One provider's documented `catch_all@example.com` synthetic ran as a **real check** against
`example.com`'s null MX on the other provider and came back invalid. Two consequences: use each
provider's own synthetics to exercise its verdict tiers, and **route those synthetics around any MX
pre-gate** — `example.com` publishes a null MX and the gate would free-block them before the validator
ever saw them.

## The free DNS pre-gate, which pays for itself before any paid call

Three shapes, all reproduced live at zero cost:

| DNS answer | Verdict |
|---|---|
| MX records present | proceed |
| **null MX** — a single `0 .` record, RFC 7505 | **dead** — a record exists *and the domain declares it takes no mail* |
| NXDOMAIN | dead |

The null-MX shape is the one a "does it have MX records?" gate misses, and it is not rare. Use any DNS
tool; never hardcode a DNS-over-HTTPS URL, because some sandboxes block those endpoints.

## The Clay-native classifier, and what its company class actually means

`extract-email-components` returns `domain` plus `isLikelyPersonalEmail` / `isLikelyCompanyEmail` /
`isLikelyEducationEmail`. It billed **0 credits + 0 action executions** on one workspace — read the
metadata anyway.

**Its company class is a residual.** `isLikelyCompanyEmail: true` comes back for **disposable providers
and for nonexistent domains**: "company" means "not freemail and not education", not "real company".
Role local-parts get no flag at all, and `guessedName` capitalises bare handles into name-shaped strings.
The freemail and education flags are reliable; **disposable screening, MX checking and role blocklisting
are your own deterministic layer on top.**

A related screen worth adding deterministically: **typosquats of major freemail domains** pass every list
screen and grade as company candidates through that residual class. Reclassify them as mistyped personal
addresses — no anchor, no spend.

## The layers, in the order that keeps the bill down

Free deterministic passes → the Clay-native classifier → paid per-row validation **only on survivors**.
There is **no batch validator**: no managed list-cleaning function exists, and no catalogue action here
takes more than one `email`. The plural-name trap that explains why is the general catalogue-reading rule
in `DETERMINISM.md`; what is specific to this family is the absence itself. Batch cleaning is a loop.

**Reconciliation is the first check, not the last.** Rows in must equal keep + risky + remove +
could-not-verify. If the numbers do not add up, a row was silently dropped, which is the cardinal failure
of list cleaning.
