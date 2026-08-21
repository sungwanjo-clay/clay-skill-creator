# Submitting

## Three routes in, and they converge here

Whichever way you built it, submission is the same:

| Route | Start from | The flow calls it |
|---|---|---|
| **From scratch** | an idea, and a conversation | the interview — no Clay table, no sign-in, no CLI |
| **From a Clay table** | a table or workflow you already built | reads column *configuration* only, never a row |
| **Package an existing skill** | a `SKILL.md` you already have | straight to validate and package |

## The steps

1. Validate locally — [`VALIDATION.md`](validation.md).
2. **Read your `SKILL.md` end to end.** You are the last reviewer before it goes out, and the only
   one who knows what the table was actually for.
3. **Then pick how it goes.** Either upload it yourself through the Clay Marketplace submission form,
   or have the agent send it from the session. The flow is required to put both in front of you; you
   are never required to pick the second.
4. If the agent sends it: it shows you the exact payload and the consent text first, and cannot send
   without your yes. See below for why that is a mechanism rather than a promise.

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

| Field | Notes |
|---|---|
| `name` | how you want to be credited |
| `title` | your role |
| `company` | editable; never part of a path |
| `companyDomain` | for the listing, not for your slug |
| `linkedinUrl` | **required**, and see below |
| `avatarUrl` | optional |

**No email field, deliberately.** A public repository is a permanent, crawlable, forkable copy —
contributor addresses published there are published for good, in git history and in every fork, long
after anyone stops maintaining the file. Ours stay private. If you have seen a marketplace that does
publish them, that is not a precedent we are following.

**LinkedIn is required as a verification signal, not as authentication.** Possession of a URL proves
nothing on its own. What it gives the person reviewing your submission is somewhere to check that the
claimed author is a real person doing the work they say they do. It is evidence a human reads, and it
is worth saying plainly that it is only that.

**You do not create either file.** Clay's publisher writes `author.md` and everything under
`skills/`. This document tells you the convention so the shape is not a surprise; it is not a
checklist of files to add to your package. Your package is your `SKILL.md` and its supporting files,
nothing more.

## The listing block

A published skill has two audiences and they read different things. **`SKILL.md` stays the executable
skill.** The marketplace copy — what someone sees before they install anything — comes from a
`## Listing` section, and separating them is what stops a skill's instructions being bent into
marketing.

Five fields:

| Field | What it is |
|---|---|
| `one-liner` | the job, in one sentence |
| `problem` | what goes wrong without this |
| `delivers` | what the installer ends up holding |
| `example prompt` | something a real person would actually type |
| `also asked as` | the other ways people phrase the same request |

**A missing field renders as absent. It is never filled with a generated placeholder.** That is the
whole design: an empty `problem` is visibly empty and someone fixes it, while a plausible invented
one reads as yours and nobody ever does. If a field is not worth writing, the listing is honest about
not having it.

## Three things to expect

**Nothing is submitted without your explicit confirmation.** There *is* a submission API, and the
skill can call it — what it cannot do is call it without you saying yes first.

The mechanism, so the promise is checkable rather than a claim: `submit_skill.py preview` prints
exactly what would be sent, including the consent text, and mints a random one-use token bound to
that package and those details. `send` refuses without it. Edit the package after the preview and
the token stops matching. The token is deliberately **not** computable from the request, so nothing
that merely controls the request can produce one.

That is not proof a human read the screen — nothing over an API can be. It is proof that a value
only the preview can mint was presented, which is the strongest checkable form of "you were asked".

**A submission is reviewed.** It goes through automated checks and a human read, and can come back
with revision requests. The local validator exists so the automated half rarely surprises you.

**Submitting is not publishing, and overlap is not a rejection.** We do not promise to publish
every submission. What we *don't* do is turn you away for building something we already have —
the skill carries the neighbour list and names your neighbours for you, rather than telling you
which jobs are taken. Where two skills do the same job we compare them on that job's own axes —
completeness, correctness, cost — and publish the one that wins. That comparison is on results, not
on which description sounds closer, which is exactly why it is not a judgment you should have to
make before you start. A near-duplicate that turns out better than ours is the outcome we want most.
