# Adding a provider — derive the adapter from its own spec

**Read this before writing a single leg for a provider.** A leg written from memory of what
an API "probably" looks like builds a graph that runs and returns nothing, and a `not_found`
caused by a wrong request field is indistinguishable from a genuine miss.

The procedure is seven steps. The first five cost nothing and touch no credential.

---

## 1. Find the spec, in this order

| Try | Why it is first |
|---|---|
| `llms.txt` / `llms-full.txt` on the docs host | Written to be read by a machine; usually complete and current |
| An OpenAPI document (`/openapi.json`, `/api-reference/*.openapi.json`) | Authoritative on required-vs-optional and exact property names |
| The docs pages themselves | Fine, but watch for pages describing an older version |

**Documentation before probing.** Do not discover an API by firing requests at paths that
might exist. Probing comes at step 6, to *verify* what the docs said — not to find it.

**If the spec cannot be read, say so and stop.** Some docs sites render entirely in the
browser and return nothing useful to a fetch. That is a real outcome: ask the installer to
paste the endpoint list or the OpenAPI file. **Never infer an endpoint path.** A fabricated
URL produces a leg that fails silently on every row, and the graph will look correct.

## 2. Enumerate the endpoints

For each one, record: method · path · auth header name and format · request shape (which
properties, which required) · response shape (where the value actually sits).

## 3. Classify each endpoint by what it PRODUCES

Map it onto the record contract. An endpoint that produces nothing in this list is not part
of this cascade, however useful it is elsewhere:

| Record field | What counts |
|---|---|
| `company_domain` | a company's web domain from its name |
| `company_linkedin` | a company's LinkedIn URL |
| `contact_linkedin` | a person's profile URL — **the pivot** |
| `contact_email` | a work email address |
| `contact_phone` | a mobile or direct number |
| `contact_email_verify_status` | a deliverability verdict on an address you already hold |

Note the **response path** the value arrives on, and note more than one where the shape
varies. That list becomes the leg's `out_paths`, which is scanned rather than pinned.

## 4. Classify each endpoint by what it REQUIRES

This is the half that decides placement, and it is the half most easily skipped:

- a person's LinkedIn URL
- name + company name
- name + company domain
- an email address
- a bare domain

Whatever it requires becomes the leg's `requires` list, in record-field terms. `requires` is
what makes a leg **skip** rather than fire and die: Clay inputs marked required reject an
empty string outright, so a leg whose input was never found must not run at all.

## 5. Place the leg

Two rules, and the second is where the value is:

**An endpoint that needs the pivot lands after the pivot finders**, with
`requires: ["contact_linkedin"]`. Most flat-rate email and phone endpoints are this shape.

**An endpoint that works from name + company can ALSO be a pivot finder.** Add it a second
time, with `field: "contact_linkedin"`. This is the case worth hunting for: the pivot gates
everything downstream of it, so a provider that can fill the pivot itself is worth more than
its own email endpoint. One provider legitimately produces four or five legs in different
positions — that is the point, not duplication.

**Then order by the one boundary that costs money.** Every flat-rate leg goes above every
credit-billed leg. Inside the flat-rate tier, ordering saves nothing at all — every call
costs the same zero — so order by measured hit rate and say that the order was measured
rather than chosen. Claiming a cost saving from ordering free calls is a claim the installer
cannot check and that is not true.

## 6. Verify with one probe per endpoint — because docs lie

Measured, and not an edge case: one provider's published docs named the request property
`linkedin_url`; the live API rejects that and names `person_linkedin_url`. The docs were
simply wrong, and the failure mode was an empty result rather than an error.

So probe each endpoint once with an identity whose answer you already know, then:

- confirm the request shape the docs claimed
- read the **raw** response and confirm or extend `out_paths` from what actually came back
- check a miss as well as a hit — some providers return `200` with a `not_found` status
  rather than an error, and the leg must read that as empty, not as a value

**The probe runs through Clay, never from a shell.** Call the generic HTTP action with the
provider's Clay HTTP API account attached, so the credential stays inside Clay and never
reaches this conversation, a file, or a process listing. If the probe cannot be run that
way, the first smoke-test record after the build is the verification instead — one step
later, same purpose. Either way it is verified before anyone relies on it.

## 6b. Close the input gaps — solve for the free tier's preconditions

Steps 3 and 4 give you, per endpoint, what it produces and what it needs. Now solve the needs,
because **a free endpoint whose input you cannot get is not free — it is absent.**

For every required input that is not always supplied, in order:

| Try | Outcome |
|---|---|
| **The same provider's other endpoints** | Best, and the one most often missed. A vendor whose email endpoint wants a profile URL usually sells a finder for that URL on the same flat plan. Check its whole endpoint list, not just the one you came for. |
| **Any other free provider** | Still free. Add it as an extra leg on that field — several legs on one field is how a waterfall is expressed and costs nothing extra when they are all flat-rate. |
| **A credit-billed Clay cascade** | Acceptable, and frequently the *cheapest* option overall. Price it: one paid lookup that yields a profile URL can convert the email and phone legs behind it from billed to free. Put that arithmetic in the plan. |
| **Nothing can produce it** | Say which fields become unreachable. Do not build legs that will always report `blocked_missing_input`. |

**The arithmetic to show, every time:** cost of the enabling lookup, against the cost of the
billed legs it displaces. A profile URL at ~2 credits that saves a ~1.1 billed email and a ~9.9
billed phone is a clear win on any record wanting a phone number, and a marginal one on a record
wanting only an email. Those are different recommendations — make them separately rather than
quoting one number.

**An enabling leg carries no caller opt-out.** Nobody asks for a company domain. It runs when a
leg requiring it is still wanted and still empty, and reports `not_needed` otherwise — which is
what keeps it from spending on a record whose dependent fields were all skipped.

## 7. Emit the leg

See `references/cascade-config.md` for every field. The shape of an HTTP leg:

```json
{
  "key": "email_flat_c",
  "field": "contact_email",
  "skip": "skip_email",
  "source": "<short provider label>",
  "tool_name": "Work email (<provider>)",
  "requires": ["contact_linkedin"],
  "provider": {
    "type": "http",
    "method": "POST",
    "url": "<exact endpoint from the spec>",
    "app_account": "<the Clay HTTP API account name>",
    "body": { "<provider's property name>": "<record field>" }
  },
  "out_paths": ["body.email", "email"]
}
```

`source` is a label, and it is how hit rates become measurable — give each provider its own.

---

## Connecting the credential — a Clay UI step, not a CLI one

**There is no CLI surface for provider connections.** Checked: `clay workflows`, `tables`,
`functions`, `routines`, `webhooks` and `api-keys` manage none of them. So this part is done
by the installer, in Clay, and the build only ever learns the account's **name**.

The object you need is called an **HTTP API (Headers) account** — that is Clay's own term for
it, and it is what the build's `app_account` names.

### First: do they already have one?

Send them to look before asking them to make one. Two places show it:

**Settings → Connections** — click the profile picture top-right, choose **Settings**, then the
**Connections** tab in the sidebar. This is the workspace-wide list and the place to check a
spelling.

**Tell them to filter that list by account type = user-added.** Unfiltered it is dominated by
Clay's own built-in integrations, and the one account they are looking for is buried among
things they never created. This is the difference between "it is not there" and "I could not
find it".

(The same accounts also appear in the `Select header account` dropdown inside an HTTP API
enrichment, but there is no reason to go looking there.)

**Ask for the name as it appears in that list**, not from memory. Editing an account there
propagates to every enrichment using it, workspace-wide, so the name is shared state.

### If they do not have one, this is the path

1. **Settings → Connections → Create.** A **Connect an account** dialog opens with a search box.
2. **Search `http`** and choose **HTTP API (Headers)**. (The other hit, **HTTP API with JWT
   Auth**, is for providers that exchange a username and password for a short-lived token — see
   below.)
3. **Name the connection after the provider** — `blitz-api`, `huntr`, `moltsets`. Short and
   unmistakable; this is the name the build will reference and the one they will paste back.
4. **Set the header values.** Add the auth credential as a key/value pair under the request
   headers. **Give them the exact header** — you read it off the provider's spec at step 1 of the
   derivation above, so say `x-api-key` or `Authorization` with a `Bearer …` value or whatever
   that provider actually wants. Do not make them go and find out, and never ask them for the
   value itself.

**Do not send them into a table to do this.** Clay's own documentation describes creating the
account from inside an HTTP API enrichment panel, which works but is the long way round — and
in this skill it is worse than long, because a cascade needs no table at all. Telling someone to
open a table to create a credential contradicts the thing you told them at Step 0.

Then have them paste the name back **exactly as Clay displays it**, and repeat it to them
against the leg it will authenticate.

A name shared across two providers, or reused later for a different one, is a silent mis-auth
waiting to happen — so one account per provider, named after it.

### The header differs per provider — read the spec, do not guess

Four observed on 2026-09-11, as illustrations of the *shapes* you will meet rather than a list
to consult instead of the spec. **Any of these can change, and one is unverified:**

| Provider | Header observed |
|---|---|
| BlitzAPI | `x-api-key` — also confirmed against a live call |
| Huntr (tryhuntr.com) | `x-api-key`, with a vendor-prefixed token as the value |
| MoltSets | `Authorization`, with a `Bearer ` + vendor-prefixed token as the value |
| QuickEnrich | `Authorization`, with a `Bearer ` + token as the value |
| GetLeads | **could not confirm** — its docs render client-side and returned nothing readable |

Header names only, deliberately. **Never write an example token into a file** — not even a
fake one shaped like a real prefix. Anything token-shaped in a package gets flagged by a
credential scanner, and a reader who copies a plausible-looking placeholder into a live
connection has a connection that silently does not authenticate.

The point of the table is that the two shapes are not interchangeable and a provider will simply
answer as though no auth was sent if you pick the wrong one. Always take the header from the spec
you read for *that* provider.

### If the provider needs a token exchange rather than a static header

Clay has a separate account type for that — **HTTP API with JWT Auth**, the second hit when you
search `http` — which stores a username, password and token endpoint instead of fixed headers. If the spec describes a login
call that returns a short-lived token, that is the account type to create, and say so rather than
trying to express it as a static header.

Clay injects the header server-side at call time. Verified live: a node configured this way
sent only `{"Content-Type": "application/json"}` and the provider still answered `200`.

### The name cannot be verified before the build — plan around it

**Measured: Clay accepts an `appAccountName` that matches no account.** The tool node is created
without complaint, `graph validate` passes, and nothing surfaces until a row runs. There is no
CLI surface that lists HTTP API accounts, so there is nothing to check the name against either —
which is why the installer reads the name off **Settings → Connections** rather than recalling it.

Clay's docs are explicit that connecting an account is optional and that an API needing auth
will error when none is selected — so the *likely* failure is a visible auth error. But a
production build was observed picking up the workspace's only HTTP API account without being
told to, which if it generalises means a name that fails to match could fall through to a
*different provider's* credential instead of erroring. **That behaviour is not documented and we
have not confirmed it**, so treat it as a risk to rule out at the smoke test rather than a fact:
check the raw response and confirm the provider you expected is the one that answered.

So: state plainly that the name is unverified until the smoke test, and at the smoke test read
the **raw response** of each HTTP leg. A `401` or `403` is a name that matched nothing. A
provider you expect to hit returning nothing is the same suspect until ruled out.

### What CAN be detected, and what cannot

Be precise about this with the installer — assuming the wrong half was checked is how a broken
connection ships:

| | Detected? |
|---|---|
| Clay functions and cascades in the workspace | **Yes** — listed by name, paged, resolved before anything is built |
| Their declared inputs | **Yes** — validated against the provider's live schema |
| Clay actions and their package ids | **Yes** — read from the live action catalogue |
| **HTTP API accounts / provider connections** | **No.** Not listable, not checkable. Asked for, and taken on trust until a row runs |

**Three rules, and they are not negotiable.**

- **Never ask for a key in chat, and never accept one.** If a key is offered, it goes into
  the Clay account instead. The build has no code path that takes one.
- **Never put a key in a node, a config file, or a header literal.** Node source is stored
  by Clay and readable by anyone who can open the workflow. The build refuses a
  credential-shaped config field for this reason.
- **Always set `app_account` explicitly.** Clay will auto-pick an HTTP account when only one
  exists, which works right up until a second one is added and then becomes a coin toss
  between providers. An explicit name never silently changes meaning.

## What to tell the installer when a provider adds nothing

A provider whose endpoints all need the pivot, on a workspace that has no pivot finder, adds
nothing until a finder exists. **Say that rather than wiring it in for completeness** — a
leg that can never fire is a node to maintain and a line in the graph that misleads whoever
reads it next. The same goes for a provider whose only endpoint duplicates one already
ahead of it in the same tier at the same hit rate.
