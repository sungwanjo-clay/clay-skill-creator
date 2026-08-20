# Interaction mechanics — the verified action contract

Everything here was read from the live catalog on **2026-08-13** via
`clay workflows actions list` and `clay workflows actions schema <packageId> <actionKey>`.
Nothing in this file is inferred from documentation or from how the in-app version behaves.
Re-verify with the same two commands before trusting it after a catalog change — the caps in
particular are the whole design constraint of this play.

## The family

Seven actions share one package. All seven are priced identically.

| Action key | Answers | Cost |
|---|---|---|
| `social-posts-get-post-activity-posts-and-shares` | what did this profile post | 0.5 cr |
| `social-posts-get-post-activity-comments` | what did this profile comment on | 0.5 cr |
| `social-posts-get-post-activity-reactions` | what did this profile react to | 0.5 cr |
| `social-posts-get-post-interaction-reactions` | who reacted to this post | 0.5 cr |
| `social-posts-get-post-interaction-comments` | who commented on this post | 0.5 cr |
| `social-posts-get-post-interaction-shares` | who reshared this post | 0.5 cr |
| `social-posts-enrich-post` | what is in this post | 0.5 cr |

`paymentType: Clay Credits` on all seven, `creditCost: 0.5`. This is a **declared** cost read
from the catalog, not a measured one.

**`activity-*` vs `interaction-*` is the axis that matters.** `activity-*` is keyed on a
profile and tells you what that profile did. `interaction-*` is keyed on a post and tells you
who engaged with it. This play runs one `activity-*` call to find the posts, then
`interaction-*` calls to find the people. Swapping them inverts the question while still
returning plausible data.

**`get-post-details` is not in this family.** It is a **Hacker News** post scraper. The name
is the trap; the description is the tell.

## Inputs, verbatim

### `social-posts-get-post-activity-posts-and-shares` — stage 1

| Parameter | Required | Notes |
|---|---|---|
| `socialUrl` | yes | "The professional URL of the **person** from whom to get posts and shares" — the documented example is an `/in/` profile |
| `maxActivitiesLimit` | no | "Default is 10, maximum is **25**" |

**No date parameter.** The action returns the most recent activities; the window is enforced
downstream by reading each post's date. A user asking for "last quarter" gets at most the 25
most recent posts, which may not reach back a quarter — say that instead of reporting a thin
result.

**Company page URLs are UNVERIFIED.** The parameter is documented as a person profile. The
in-app trigger-source equivalent accepts a company URL with a `mentionsOrganization` mode,
but that is a different surface and does not transfer. If a user has only a company page,
try it and report the actual response — do not claim it works and do not claim it fails.

### `social-posts-get-post-interaction-reactions` — stage 2

| Parameter | Required | Notes |
|---|---|---|
| `postUrl` | yes | Accepts both post-URL shapes: the `/posts/<slug>-activity-<id>-<hash>` form and the `/feed/update/urn:li:ugcPost:<id>` form |
| `maxInteractionsLimit` | no | "Default is **10**, maximum is **50**" |

### `social-posts-get-post-interaction-comments` / `-shares`

Same two parameters. Both are **"Default is 10, maximum is 10"** — the cap and the default
coincide, so these two cannot be under-requested, only truncated by the platform.

## The caps, and why they are the design

| Type | Max per post |
|---|---|
| Reactions | 50 |
| Comments | 10 |
| Shares | 10 |

Ceiling per post: **70 interactions**, and that is a hard platform limit, not a budget knob.
Consequences the play is built around:

1. **Reactions default to 10 of a possible 50.** Not passing `maxInteractionsLimit` costs 80%
   of the available recall and produces output that looks exactly like a quiet post.
2. **A returned count equal to the cap means truncated, not complete.** 50 reactions back
   means ≥50 exist. Record the equality per post; it is the only truncation signal available.
   **And below-cap proves nothing either** — verified: a request for 50 returned 48 on a
   well-engaged post. The provider returns what it can reach. So cap-equality is sufficient
   evidence of truncation and never necessary, and a short return is unexplained rather than
   complete.
3. **Popular posts are less observable.** A post with 400 reactions surfaces 12.5% of its
   engagers; one with 30 surfaces all of them. Ranking accounts by raw engagement volume
   therefore ranks partly by how much the platform truncated, which is why intensity is scored
   per person over distinct interactions rather than by counting rows.

## Outputs (reactions action, per returned item)

```
reactions[].author.name                  display name
reactions[].author.url                   profile URL          ← canonicalize before keying
reactions[].author.type                  person vs organization discriminator
reactions[].author.profile_picture_url   nullable — observed null on ~1 in 4
reactions[].interaction_type             uniformly "reaction" on this action
reactions[].reaction                     observed live: like / celebrate / love / support
reactions[].preview_text                 "<Reaction> by <name>" — a LABEL, not content
```

**Verified against a live call (2026-08-13, one 0.5-credit probe, public vendor post).** Two
corrections to the declared contract:

- **`author.title` is returned and is NOT in the catalog's `outputParameters`.** It carries the
  person's headline — the single most useful field for identity resolution. The declared output
  list is a SUBSET of the live payload, so read the declared list as a floor, never a ceiling.
  Undeclared fields can be used, but never depended on: nothing promises they persist.
- **`preview_text` on a reaction is synthesized**, not content — `"Like by <name>"`,
  `"Celebrate by <name>"`. It restates `reaction` and `author.name`. Only a comment's
  `preview_text` is the person's own words.

`author.type` is a provider field: present in the schema, not guaranteed in a payload. The
URL-shape test (`/in/` → person, `/company/` → organization) is the independent second test,
and the play requires both.

## Canonicalization

Strip the query string, strip the trailing slash, lowercase. Verified as necessary in
production social-signal capture, where the same interactor arrives with and without tracking
parameters across posts and un-canonicalized URLs inflate one human into several.

The composite interaction key is
`clean_profile_url | interaction_type | canonical_post_url` — stable across re-runs, which is
what makes a weekly cadence additive instead of duplicative.

## What this surface does NOT have

Named explicitly, because each absence is a thing a user may ask for and the honest answer is
"not on this surface":

- **No brand-mention discovery.** There is no action that finds posts *mentioning* your
  company. The in-app `trigger-source` subscription does this (`companyPostType:
  mentionsOrganization`); the action catalog does not expose it. Stage 1 here is "posts BY a
  profile we name", not "posts ABOUT us".
- **No review-site intent feed.** `trustradius-enrich-company` is company enrichment, not the
  category-scoped intent source.
- **No identified website visitors.** `similarweb-get-website-visits` returns traffic volume,
  not who visited.
- **No standing subscription.** These are pull actions. Recurrence is a schedule you run, not
  a feed that pushes — which is why the interaction key has to carry the idempotency.
