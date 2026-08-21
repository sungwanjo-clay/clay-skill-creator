# Engagement on your own social content

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that spent the credits. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

**A different job from third-party news about accounts**, and the machinery differs accordingly:
person-grain rather than company-grain, first-party rather than third-party, per-post recall caps, a
composite interaction key, and self-suppression. A skill built on the wrong reading of that boundary is a
materially different skill.

## The family

Seven `social-posts-*` actions in one package, **`creditCost: 0.5`** each, `paymentType: Clay Credits`.

| Read | Value |
|---|---|
| reactions per post | max **50**, default 10 |
| comments per post | max **10**, default 10 |
| shares per post | max **10**, default 10 |
| stage-1 activities per profile | max **25**, default 10 |
| stage-1 input | `socialUrl`, documented as a **person** profile |
| stage-1 date filter | **none** — the window is enforced downstream, by you |

Output paths: `reactions[].author.{name,url,type,profile_picture_url}`, plus `interaction_type`,
`reaction`, `preview_text`.

**Cost is per profile plus per post per interaction type**, which compounds faster than it reads: 3
profiles × 30 posts × 3 types is `0.5×3 + 0.5×30×3` = **46.5 credits**. A comments-only pass over the same
posts is `0.5 × posts`. State the arithmetic before spending, because the multiplier is the number people
get wrong.

## Three corrections a single 0.5-credit probe forced

None of these was reachable from the schema, and the second is the one that justifies probing at all.

1. **An undeclared field is returned, and it is the most useful one.** Eight fields delivered against
   seven promised; the extra is the interactor's **headline**, which is the field that actually resolves
   identity. **The declared list is a floor, not a ceiling** — use it, and say it is undeclared so a
   future reader knows why it might disappear.
2. **`preview_text` on a reaction is a synthesised label, not content.** It reads `"Like by <name>"` —
   a restatement of two fields already in the payload. A static schema read gives you a field named
   `preview_text` on a reactions endpoint, and every reasonable author infers comment text. **Quoting it
   as what someone said would be fabrication with a real field name attached.**
3. **48 returned against a requested 50.** Below-cap does not mean complete. **Cap-equality is
   *sufficient* evidence of truncation and never *necessary*** — a short return is unexplained rather
   than reassuring, because the provider returns what it can reach.

Also measured on that call: `author.type` populated `"Person"` on all 48, `profile_picture_url` **null on
roughly a quarter**, and the observed `reaction` value space was `like`, `celebrate`, `love`, `support`.

## What is not in the catalogue, so do not promise it

- **Brand-mention discovery is absent.** The in-app trigger mode that watches for mentions of an
  organisation has no action-catalogue equivalent.
- **No review-site intent feed**, and no identified-website-visitor feed. Two actions match on name and
  answer different questions — one is company enrichment, the other is traffic volume only.
- **Whether `socialUrl` accepts a company page** is unverified. One further 0.5-credit probe would settle
  it; until then a skill should mark it unverified rather than guessing.
- **Six of the seven actions in the family are unprobed.** Their declared shapes are all that is known.

## Scoring interactions

Weighting by interaction type is a judgment call, but two things about it are mechanical. **Dedupe on a
composite `(post, interaction_type)` key** before summing, or one person reacting to three posts inflates
against one person commenting once. And **suppress your own people** — colleagues engaging with company
posts are the largest false-positive population in the payload, and they look exactly like buyers.

One worked weighting that enumerated cleanly: comment 3, share 2, reaction 1, with bands at ≥5 / 3–4 /
1–2. Every reachable sum from 1 to 20 lands in exactly one band, and 0 is unreachable by construction
because a row exists only when an interaction does. That last property is worth reproducing whatever
weights you choose — a band set with an unreachable floor hides rows.
