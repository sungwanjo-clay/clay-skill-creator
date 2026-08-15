# SKILL.md — the contract

## Frontmatter

```yaml
---
name: your-skill-slug          # lowercase, hyphens, matches the directory name
description: |                 # no known cap; 1,187 chars is the longest verified intact
  What it does, in one dense paragraph. Then: "Use whenever someone asks: the actual
  phrases people use." Then: "Do NOT use it for a-neighbouring-skill, another-one."
category: enrich               # one of the marketplace categories
type: task                     # task (one job) | play (a multi-step motion)
tags: [csv, domain]            # input shapes and personas
keyword: your-skill-slug
proof_status: partial          # complete | partial | not_exercised
proof_gaps:                    # required and non-empty unless proof_status is complete
  - stage: stage_e
    reason: A plain sentence saying what was not verified.
---
```

**There is no length limit we can point you at.** `python3 tools/package_skill.py validate` measures
your description the way the form does — a block scalar counts as its lines joined by spaces, not as
raw bytes — and *reports* anything past **1,187 characters**, which is simply the longest description
we have verified is stored intact, byte for byte, through submission. Past that we have no evidence
either way, so treat the report as a heads-up and not a rule. If you do want to trim, cut restatements
and mechanism detail, which belongs in the body; the trigger phrases and the "do NOT use it for" list
are the parts that earn their length, because they decide whether your skill is chosen at all.

An earlier version of this file said 1024 was a hard cap enforced at the door. That was true for a
while and is not true now, and the correction is here rather than silently swapped because a number
you wrote a description around is worth knowing the status of.

**Avoid angle brackets in the description.** We cannot show you a check that rejects them, so this is
convention rather than a constraint — but a description written as `<placeholder>` reads as an
unfinished template, and prose beats slots for the one field a router reads. Write "for a given
intent", not "for `<intent>`".

**The description is the trigger.** It is what decides whether your skill is chosen, so write the
phrases people actually type, and name the skills yours should *not* be confused with. A vague
description is the most common reason a good skill never gets used.

**`proof_gaps` entries need both a stage and a reason.** A gap that says only "incomplete" tells a
reader something was not proven but not what to do about it.

## Body

There is no required section list, but skills that work tend to share a shape:

- **The insight** — the one thing that makes this hard, stated up front. If there isn't one, the
  skill is probably a single enrichment call and does not need to be a skill.
- **Steps, numbered, in dependency order.** Each names what it needs from earlier steps.
- **Decision rules that resolve to exactly one answer.** No overlapping bands, no undefined gaps.
- **What good looks like**, including the common failure mode.
- **Rules** — the MUSTs and NEVERs, so the boundaries survive being skimmed.
- **A worked example** with real values.

## Hard requirements

- Exactly one `SKILL.md` at the package root.
- Every relative reference resolves to a file inside the package.
- No workspace identifiers: table ids, column ids, workspace ids, saved-view names, auth handles.
- No credentials, no private hostnames.
- Everything the installer must supply is a **declared input**, named in the body.

See [`PACKAGE-LAYOUT.md`](PACKAGE-LAYOUT.md) for layout and [`VALIDATION.md`](VALIDATION.md) to
check all of the above locally.
