# Bring your own Exa key

Choose this optional installation when you want Alpha Copy to retrieve historical and
current observations automatically. It runs inside Clay using two native **HTTP API**
actions authenticated by your saved Exa header account, followed by the normal Claygent
research, audit, score and copy steps. The ordinary installation still works without Exa.

## Add your key once in Clay

1. In Clay, add an **HTTP API** enrichment and open **Select header account → Add account**.
   Existing connections can also be managed in **Settings → Connections**.
2. Name the account **Exa — Alpha Copy**. In its secure request headers, add `x-api-key`
   with your own Exa API key as the value. Save it in the account dialog.
3. Select that dedicated Exa account for the historical and current requests. Do not select
   a header account belonging to another provider. Do not put the key in a table column,
   ordinary Headers field, workflow trigger, prompt, shared brief, chat or package.
4. The installer takes the resulting Clay **account ID**, never the API key. An installing
   agent can identify the selected account through Clay's connection UI or accessible action
   catalog metadata. If the catalog does not list a newly saved account, inspect the selected
   HTTP action's connection in the UI; do not guess or use another account as a fallback.

Clay documents encrypted reusable header accounts here:
https://university.clay.com/docs/http-api-integration-overview.
Exa documents `x-api-key`, `snapshotAsOf` and fresh content retrieval here:
https://exa.ai/docs/reference/get-contents.
An API key alone does not guarantee Snapshot entitlement or coverage for a particular date.

## Install the Exa-enabled version

Preview a separate installation, using your selected Clay connection ID:

```bash
python3 scripts/install.py --workspace WORKSPACE --state PRIVATE_RECEIPT \
  --name "Alpha Copy — Exa Time Machine" --exa-account SELECTED_EXA_HEADER_ACCOUNT
```

Add `--create` to build it. The base manual installation is not changed. This option creates
four additional native nodes; it never publishes or runs the workflow. The connection is
explicit on each HTTP node, so installation does not inherit a workspace's unrelated default
HTTP credentials. Authorization failures from Clay stop installation; select an accessible
Exa connection instead of bypassing access controls.

For a people segment, combine `--exa-account` with the existing `--audience`,
`--entity-type CONTACT`, `--brief` and `--field-map` options. The setup picker also accepts
`--exa-account` with `--install`. For a contact table, select the Exa-enabled installation
in **Invoke Workflow** and map the same person/company inputs.

The Exa graph builder is `../scripts/exa.py`. Native request preparation and response checks
are in `exa-prepare.py` and `exa-normalize.py`; `../scripts/install.py` attaches them.

## Configure the comparison at the beginning

- **Offer / ICP / greeting / CTA / signature:** unchanged; set once for the batch.
- **Company domain:** comes from each person's employer.
- **Comparison as of:** required past date (`comparison_as_of`, YYYY-MM-DD).
- **Page path:** optional (`comparison_page_path`), default `/`; use `/pricing` for pricing.
- **Comparison focus:** the type of change you want investigated.

No evidence JSON columns are needed in automatic Exa mode. Leave imported receipt inputs
empty so the workflow cannot mix a supplied historical claim with an unrelated fresh pair.
The same-company URL and cutoff are generated per run; one URL is requested per call.
The Exa installation requires the historical comparison and cannot silently fall back to a
current-state pitch when history is missing.

## The two calls and checks

Both HTTP actions use POST to the fixed endpoint `https://api.exa.ai/contents`.
The historical body has `urls`, `text=true` and `snapshotAsOf`; the current body has
`urls`, `text=true` and `maxAgeHours=0`. Request headers contain only nonsecret content type
in the graph; the secure connection supplies authentication. Endpoint overrides, HTTP
redirects and automatic request retries are disabled in this installation.

The response check requires one successful result for the exact requested HTTPS page,
a provider request ID and substantive text. Current content must be marked freshly crawled.
It retains the actual request receipts and observation time. `publishedDate` is **not** used
as the historical capture time. Exact capture time stays unknown unless independently supplied
and verified; requested cutoff is still not the change date.

The native HTTP action does not declare a fixed response schema. The parser accepts direct
Exa results or the usual body/data/response metadata wrappers and fails on unknown shapes.
Before a real batch, run one authorized company with the saved account, inspect both native
HTTP outputs, and confirm the actual output shape and fresh/history semantics. Local or
synthetic code tests are not proof of an authenticated provider call.

A failed key, unavailable Snapshot entitlement, trial cap, unavailable historical page,
title-only result, changed URL, stale current response or unrecognized envelope stops at
retrieval/normalization. It does not become an approved draft or a fictional observation.
The usual evidence gates still reject unchanged content and unsupported commercial connections.

Each person processed by this version can make two Exa requests. It does not deduplicate
coworkers' company lookups. Exa usage and Clay usage are separate; verify actual plan limits
and a bounded test before scaling. Provider response cost fields are estimates, not a complete
billing reconciliation. No fixed price or successful historical coverage is promised.
