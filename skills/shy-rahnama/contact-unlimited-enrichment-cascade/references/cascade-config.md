# The config schema

One JSON file describes the whole graph. `scripts/cascade-config.example.json` is a working
copy of everything below, at placeholder values.

The build writes `build-state.json` beside the config the moment each node is created.
**Never delete that file to "start clean"** — it is the only record of which Clay node is
which, and without it the build cannot recognise the graph it made. It refuses rather than
creating a duplicate.

## Top level

| Key | Required | What it is |
|---|---|---|
| `workspace_id` | yes | The Clay workspace this config belongs to. The build reads `clay whoami` and **refuses** if they disagree, so a config can never be applied to the wrong workspace by accident. |
| `workflow_name` | yes | The workflow's name. Also the orphan guard's key: if a workflow of this name exists but `build-state.json` does not, the build stops instead of making a second one. |
| `clay_config_home` | no | Only when this workspace's Clay credential is deliberately kept separate from the default `clay login`. Omit to use the ambient one. |
| `verified_statuses` | no | Which verifier verdicts count as verified. Default `["deliverable","valid"]`. A catch-all or risky verdict is deliberately **not** in the default — add one only as a declared decision. |
| `capture_prefix` | no | The prefix marking fields a leg captured beyond its own. Default `person_`. Emit lists them in `captured_fields`. |
| `sentinels` | no | Response values that mean "nothing", not a value. Default `["n/a","none","null"]`. |
| `callback` | no | `{"enabled": true}` by default, and **leave it that way** — the callback nodes cost nothing to build and `callback_url` is a **per-record** input, so the caller decides per record whether anything is sent. A record without one routes to `Done`. `{"enabled": false}` exists for a workspace that must not have the nodes at all; it is not how you say "we do not use callbacks". `app_account` sets a Clay account if the destination needs auth. |
| `legs` | yes | The cascade, in order. |

## A leg

| Key | Required | What it is |
|---|---|---|
| `key` | yes | Unique. Names this leg's four nodes and its `need_<key>` flag. **Renaming a key orphans the old nodes**, which the build reports rather than silently deleting. |
| `field` | yes | Which record field this leg fills. Must be in the record contract below. **Several legs may share a field — that is how a waterfall is expressed.** |
| `want` | no | Which caller opt-IN asks for this leg's field as an output, from the list below. For an enabling lookup — a field nobody asks for on its own — this is the right flag: the leg fires whenever a downstream leg requires its field, and otherwise only when the caller sets this. A leg carries `skip` or `want`, never both. |
| `skip` | no | Which caller opt-out switches this leg off, from the list below. **Omit both for a pure enabling lookup** — a field nobody asks for that exists because legs after it cannot run without it. An enabler fires only when a leg requiring its field is still wanted and still empty, and reports `not_needed` otherwise. That is what stops it spending on a record whose consumers were all skipped. |
| `source` | yes | The provenance label written to `<field>_source` on a hit. Give each provider its own — this is what makes hit rates measurable. |
| `tool_name` | yes | Human label for the tool node, shown in Clay's graph. |
| `requires` | no | Record fields that must be populated before this leg may run. Missing one means the leg **skips** and reports `blocked_missing_input`, rather than firing with an empty required input and killing the run. |
| `provider` | yes | How the call is made. Four types, below. |
| `tool_inputs` | for `clay_function` / `clay_action` | `{provider's parameter name: record field}`. Validated against the provider's live schema before anything is built. |
| `out_paths` | yes | Ordered candidate response paths, scanned until one yields a value. Dotted; a list is indexed at `[0]`. |
| `capture` | no | `{record field: response path}` for data the provider returned beyond this leg's own field. Keeps what has already been paid for. |

## Provider types

**`clay_function`** — a Clay cascade or workspace function.

```json
{ "type": "clay_function", "names": ["Work Email", "<a workspace-specific fallback>"] }
```

Resolved **by name**, case-insensitively, in order. A function's id is workspace-local, so a
hardcoded id is a build that only works where it was written. `names` being a list lets one
config say "the native cascade, or this workspace's own function if that is better here".
Nothing matching is a loud failure listing what the workspace does have.

**`clay_action`** — a vendor with a native Clay action.

```json
{ "type": "clay_action", "actionKey": "…", "actionPackageId": "…" }
```

Both, always: resolve by the **pair**, since the same key can appear in more than one
package. Get them from `clay workflows actions list`.

**`http`** — any provider reachable over HTTP. The generic adapter.

```json
{ "type": "http", "method": "POST",
  "url": "https://api.example.test/v1/person-email",
  "app_account": "<Clay HTTP API account name>",
  "body": { "person_linkedin_url": "contact_linkedin" },
  "body_static": { "country": "US" },
  "query": { "full_name": "contact_name" },
  "query_static": {},
  "headers": { "Accept": "application/json" } }
```

| Field | Notes |
|---|---|
| `app_account` | **Required.** The Clay HTTP API account holding the credential. Clay injects the auth header from it. The build refuses an http leg without one, and has no path that accepts a key. |
| `method` | Defaults to `POST`. |
| `body` / `body_static` | `body` maps provider property → record field; `body_static` adds literals. The JSON body is rebuilt in every node that emits the record, so a leg can reference a field an earlier leg resolved. If any mapped field is empty the body is empty, which is why `requires` matters. |
| `query` / `query_static` | Same, for `GET` endpoints. Sent as an object. |
| `headers` | Static, non-auth headers only, merged over `Content-Type: application/json`. **Auth never goes here.** |

Responses come back wrapped with response metadata, so a top-level provider field is usually
at `body.<name>` — list both spellings in `out_paths` and let the scan decide.

**`none`** — the leg is omitted from the graph entirely. **This means "no provider is available
for this", not "a field the installer does not want".** Keeping the leg in the file with
`"type": "none"` documents a provider that could be bound later; the build prunes its nodes only
when `--allow-prune` is passed.

Never reach for `none` to switch a field off. What gets attempted is a **run-time** decision made
by the skip flags on each record, so a field nobody is interested in this week still gets its leg
built and they simply set its flag. Using `none` for that forces a rebuild the moment they change
their mind, and it hides from the plan that a provider for that field exists at all.

## The record contract

Fixed, not a per-config knob. This is a *contact* cascade, and these are what a contact is.

**The interface** — what a webhook sends and what a Clay table maps its columns onto:
`contact_name` and `company_name` (required) · `contact_email` · `contact_linkedin` ·
`contact_phone` · `company_domain` · `job_title` · the three skip flags · `source_ref` ·
`callback_url`.

**The record** adds what the cascade derives and fills internally: `first_name` · `last_name` ·
`company_linkedin` · `contact_email_verify_status`.

A table needs no build-time action. It binds in Clay's UI by adding the workflow and choosing
`0a Intake` as the starting node, which creates the table trigger on its own — so the cascade
can be built before any table exists, and one cascade serves many tables.

Opt-out flags: `skip_linkedin` · `skip_email` · `skip_phone` — **absent means false, so the work
happens.**

Opt-in flags: `want_company_domain` · `want_company_linkedin` — **absent means false, so nothing
is fetched for its own sake.** These fields still fire whenever a leg downstream requires them;
the flag only asks for one when nothing else needs it. Only an explicit `true`/`1`/`yes`/`on` switches a field off, which means a caller who
has never heard of these gets the full cascade rather than silent empty fields.

The three contact fields are what the cascade exists to fill, so they are opt-out. The two
company fields are plumbing that can also be requested, so they are opt-in — the opposite
polarity would fetch a domain on every record where one happened to be missing.

**A skipped field is still fetched when a non-skipped field requires it.** `skip_linkedin` means
"do not fill this for its own sake"; if email is wanted and the email provider needs a profile
URL, the URL is still resolved, because the alternative is that email silently cannot run. To
stop every LinkedIn lookup, skip the fields that depend on one too. Say this at the plan rather
than letting someone discover it in a bill.

`contact_name` and `company_name` are required on every record; first and last name are derived
from the one name. Everything else supplied is one lookup not made.

## What comes out

Every field at its final value, plus `<field>_source` for each. **The source is a closed
set, and every value means something different:**

| Value | Means |
|---|---|
| `supplied` | it arrived populated; nothing was looked up |
| *a provider's label* | that provider found it |
| `not_found` | a leg ran and came back empty |
| `skipped` | the caller switched the leg off |
| `blocked_missing_input` | a field the leg depends on was never found, so it never ran |
| `not_needed` | an enabling lookup nothing downstream asked for — it cost nothing |

A seventh value, `unknown`, exists **inside the workflow only**: intake stamps it on any field
that arrived empty, and each leg's resolve overwrites it. It never reaches the output contract,
because a field with no leg has its source stripped on the way out — so a source key existing in
the output tells you a leg for that field exists. Verified by running the generated code.

**`supplied`, `skipped`, `blocked_missing_input`, `not_needed` and `not_found` must never be
conflated.** "We already had it", "you told us not to look", "we could not even try", "nothing
wanted it" and "we looked and found nothing" are five different facts, and folding any of them
together makes every provider hit rate downstream meaningless — which is the whole reason for
running a waterfall rather than one call.

Plus, from emit: `contact_email_verified` · `contact_email_verified_only` (blank unless
actually verified — **this is what downstream automation should consume**) ·
`contact_email_domain_match` · `captured_fields` · `filled_fields` · `filled_count` ·
`record_json` · `source_ref` echoed back so a caller can join the result.
