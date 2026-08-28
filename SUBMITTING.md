# Submitting

## Three routes in, and they converge here

Whichever way you built it, submission is the same:

| Route | Start from | The flow calls it |
|---|---|---|
| **From scratch** | an idea, and a conversation | the interview — no Clay table, no sign-in, no CLI |
| **From a Clay table** | a table or workflow you already built | reads column *configuration* only, never a row |
| **Package an existing skill** | a `SKILL.md` you already have | straight to validate and package |

## The steps

1. Validate locally — [`VALIDATION.md`](VALIDATION.md).
2. **Read your `SKILL.md` end to end.** You are the last reviewer before it goes out, and the only
   one who knows what the table was actually for. This is not a formality: **nobody downstream runs
   your skill.** Review validates the source, not the behaviour, so the run you did while building it
   is the only run it gets before somebody installs it.
3. **Then pick how it goes.** Two live routes, and they reach the same queue:
   - **The form** — [`marketplace.clay.com/submit`](https://marketplace.clay.com/submit). Upload the
     `SKILL.md`, or a ZIP if the skill has supporting files.
   - **From the session** — `python3 tools/submit_skill.py preview <package>`, then `send`. The agent
     runs this for you if you ask it to.

   The flow is required to put both in front of you; you are never required to pick the second.
4. If the agent sends it: it shows you the exact payload and the consent text first, and cannot send
   without your yes. See below for why that is a mechanism rather than a promise.

## What your submission carries

**Your name and your work email**, because a person has to be able to reach you about your own
skill. That is the whole of what you are asked for. Your company follows from the email's domain, and
the rest of your author profile — title, LinkedIn, avatar — is looked up from those two and confirmed
by a person before publication, never attached silently. Nothing is published without an explicit
approval: submitting puts your skill in front of a person, it does not put it on the marketplace.

**And not your answer sheet — that never reaches us, and we never host one.** It holds your field
names, table ids and thresholds: identifiers, never an API token or a password. Keep it wherever your
team already keeps that sort of thing, and send it to a colleague the way you send anything else. We do
not store it, index it, or offer a place to share it — the moment we hold your schema we own an
access-control problem and you get nothing for it. It is also structurally excluded rather than
promised out: a sheet inside a package fails validation before anything can be sent.

## Where a published skill lives

```
skills/<your-slug>/<skill-slug>/SKILL.md
```

**Person first, two segments, never three.** Not a company segment, not a branch of your own, and
never a path derived from your email domain — because the first person at any company would then own
that company's namespace permanently, on a public marketplace, for everyone who came after.

**Both slugs are permanent.** The author directory name *is* your creator slug, and the skill slug is
the name people install by. Moving a skill later — under an agency, under a new employer — is a new
publication plus a withdrawal, and it breaks every install command already in the wild. So the shape
is chosen once, deliberately, and it is chosen to be the thing least likely to change: you.

**Your company is metadata, not a path.** It lives on your author profile as an editable field, so
changing employers means editing one line and keeping every skill you have published.

## Your author profile

```
skills/<your-slug>/author.md
```

| Field | Where it comes from |
|---|---|
| `name` | **you** — the one thing you are asked for |
| `company` | your work email's domain, no lookup |
| `companyDomain` | the same |
| `title` | filled in from your name and email, then confirmed |
| `linkedinUrl` | the same, and see below |
| `avatarUrl` | the same |

**One question, and it is your name.** Everything else on this profile is either free (your company
is your email's domain) or filled in on our side and checked by a person before it publishes. You are
welcome to supply any of it yourself and what you supply is never overwritten — but you are not asked,
because a field offered as optional is still a field you have to think about, and these are ours.

**No email field, deliberately.** A public repository is a permanent, crawlable, forkable copy —
contributor addresses published there are published for good, in git history and in every fork, long
after anyone stops maintaining the file. **Your address is never written into the repository**, which
is the specific thing this avoids, and it is the specific thing we can state. If you have seen a
marketplace that does publish them, that is not a precedent we are following.

The submission you send does carry your name and work email, because a person has to be able to
reach you about your own skill. That is a different surface from the repository, and this file makes
no claim about it beyond that.

**LinkedIn is a verification signal, not authentication — and it is required at publication rather
than required from you.** Possession of a URL proves nothing on its own. What it gives the person
reviewing your submission is somewhere to check that the claimed author is a real person doing the work
they say they do. It is evidence a human reads, and it is worth saying plainly that it is only that.

**Which is exactly why a derived one is confirmed before it is used.** We look yours up from your name
and work email rather than asking you to paste it. A guess nobody checked would be worse than an
absent one: the reviewer would be checking our lookup against our lookup, and a wrong profile attached
to your published skill is a misattribution on a public page. So it is derived, marked as derived, and
a person confirms it — and if you supplied one yourself, that is the one that stands.

**You do not create either file.** Clay's publisher writes `author.md` and everything under
`skills/`. This document tells you the convention so the shape is not a surprise; it is not a
checklist of files to add to your package. Your package is your `SKILL.md` and its supporting files,
nothing more.

## What you write, and what gets worked out for you

**There is no taxonomy homework.** You are not asked to pick a category, guess which personas apply, or
invent a keyword. Those are worked out from what you wrote, and a person checks them before anything
goes live. You cannot get them wrong, because you are not asked.

| You supply | Worked out for you |
|---|---|
| the `SKILL.md` itself | category, personas, what it touches, what it runs on |
| your skill's title and description | keywords, and the URL slug, taken from your title |
| your name | your byline, role, LinkedIn and avatar — see the profile section above |

**Two different things are called a title in this document, and the difference matters.** Your
**skill's** title is yours and is never rewritten. The `title` on your author profile is your job
title, and that is one of the fields filled in for you.

**Your skill's title and description are kept verbatim, never rewritten.** If the description needs to
be shorter for a card, the card gets shortened; your text does not. Anything you choose to supply about
yourself is treated the same way — supplied beats derived, always.

**There is no free tag field, and that is a reversal worth stating.** An earlier version of this page
promised one — your own words kept exactly as typed, beside a tidied set that the filters actually ran
on. Two lists meant the one attributed to you was the one nothing used, which is a worse deal than it
reads as: your words on display, somebody else's words deciding whether anyone finds you. So there is
one set, `keywords`, it is managed, and a term missing from it gets **added** rather than mapped onto
the nearest term that fits. Where your own words are load-bearing is the description and the `## Listing`
block — both verbatim, both yours, and both read by a person rather than by a filter.

## The listing block

A published skill has two audiences and they read different things. **`SKILL.md` stays the executable
skill.** The marketplace copy — what someone sees before they install anything — comes from a
`## Listing` section, and separating them is what stops a skill's instructions being bent into
marketing.

**These five are derived from your skill, not collected from you.** The interview does not ask for
them, on purpose: it has a budget of three questions and none of them should be spent on copy that can
be read off the thing you already wrote.

| Field | What it is | Length |
|---|---|---|
| `one-liner` | the job, in one sentence | 30–160 |
| `problem` | what goes wrong without this | 90–420 |
| `delivers` | what the installer ends up holding | 90–420 |
| `example prompt` | something a real person would actually type, not a label | 20–200 |
| `also asked as` | three other phrasings of the same request | 20–260 |

**Write one yourself and it stands.** A field you declare is never regenerated — not reworded, not
"improved". That is the whole point of the block existing as text you can edit rather than a form
someone else fills in. **Only an omitted field gets filled, and a filled one is marked as derived**, so
a reader can always tell which sentences are yours.

**A missing field renders as absent, never as a generated placeholder** on the page itself. An empty
`problem` is visibly empty and someone fixes it; a plausible invented one reads as yours and nobody
ever does.

`python3 tools/package_skill.py validate` reports each field it cannot find, at report severity rather
than blocking — so you can see what will be derived before you decide whether to write it yourself.

## Which fields are yours, in one table

Three levels, and the difference between them is who is allowed to change the words.

| | Fields | Rule |
|---|---|---|
| **Verbatim** | title, description, byline | never touched, by anyone, for any reason |
| **Yours if you write them** | the five `## Listing` fields | a declared value is never regenerated; an omitted one is filled and marked derived |
| **Worked out, then checked** | category, personas, mechanism, touches, keywords, inputs, outputs, workflow summary | derived from your skill; a person confirms before publication |

## Sending a new version of a skill you already submitted

**The same two commands. There is no separate update route, and no flag that says "this is version
two".**

```
python3 tools/submit_skill.py preview <package>   # then send, with the token it prints
```

What makes it work is that **duplicate detection is by package digest**, not by name: an unchanged
package comes back `duplicate_submission`, and a genuinely changed one is a new submission. So a new
version is nothing more than the changed package, sent again.

Two things to get right, and one of them costs you the skill's identity if you get it wrong:

- **Keep `name:` in the frontmatter exactly as it was.** That is what the marketplace uses as your
  skill's slug. Change it and you have submitted a *different skill*, not a new version of this one.
- **`preview` has to run again.** The consent token is minted per preview and `send` will not take a
  stale one. That is deliberate — it is the same rule that stops a first submission happening as a
  side effect, and a resubmission is not exempt from it.

**What we cannot yet tell you: whether the second submission attaches to the existing skill as a new
version, or arrives as a second listing beside it.** The response carries a `versionId` and the review
surface shows a version number, so there is a version concept on our side — but we have not measured a
same-name resubmission end to end, and we would rather say so than describe behaviour we have inferred
from a field name. Ask the person who invited you before you resend something already under review.

That matters because of the three gaps in the next section: there is **no withdraw**. If a resubmission
lands as a duplicate listing rather than a version, removing the wrong one is a manual request, not a
button. It is recoverable; it is not self-service.

## What to expect

**Nothing is submitted without your explicit confirmation.** There *is* a submission API, and the
skill can call it — what it cannot do is call it without you saying yes first.

The mechanism, so the promise is checkable rather than a claim: `submit_skill.py preview` prints
exactly what would be sent, including the consent text, and mints a random one-use token bound to
that package and those details. `send` refuses without it. Edit the package after the preview and
the token stops matching. The token is deliberately **not** computable from the request, so nothing
that merely controls the request can produce one.

That is not proof a human read the screen — nothing over an API can be. It is proof that a value
only the preview can mint was presented, which is the strongest checkable form of "you were asked".

**A submission is read by a person, and a first response takes two business days during early
access.** Two days is the response, not necessarily the verdict — a review that needs a conversation
starts inside two days rather than finishing inside them.

**What runs on our side is narrower than you might assume: validation of the source and the
frontmatter.** That is the whole of it. **We do not execute your skill** — there is no test run, no
sample workspace, nothing that exercises it against real data. So the substantive automated check is
the local validator, on your machine, before you send anything: your own agent is what tells you
what is wrong with your package. That is faster than hearing it from us, and it is the honest
division — we can check that a skill is well-formed, and only you can check that it works.

**There is no self-service way to withdraw a submission.** No command and no button pulls one back —
it is on the list, and it is not done. If you send something and want it removed, ask the person who
invited you and it gets handled by hand. We would rather say that than describe a button you would go
looking for.

**Also not built:** a notification when the state changes, or a channel that returns revision
requests to you automatically. A review can conclude that something needs changing, and today that
reaches you through the person who invited you rather than through the system. Ask them; that is the
whole mechanism, and describing it as more than that would send you waiting for an email that has
nobody to send it.

**Submitting is not publishing, and overlap is not a rejection.** We do not promise to publish every
submission. What we *don't* do is turn you away for building something that already exists. **You are
never asked to check whether a job is taken, and there is no list of taken jobs to check** — build the
thing you know works, describe it in your own words, and let it stand on that. A skill that covers
ground something else already covers, and covers it better, is the outcome we want most.
