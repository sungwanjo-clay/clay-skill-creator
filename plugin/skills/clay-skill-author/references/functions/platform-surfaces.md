# The four surfaces, and what bites when you query them

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that ran the commands. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

Read this before the job leaf. Most wasted build time traces to asking the wrong surface — a function
present on one is routinely absent from another, and they do not bill alike.

| Surface | Command | What lives there | Billing |
|---|---|---|---|
| **Action catalogue** | `clay workflows actions list` · `clay workflows actions schema` | per-provider actions; the large surface | credits and/or action executions, per call |
| **Managed functions** | `clay functions list` (paginated, ~100/page) | Clay-built multi-step functions | declared `estimatedCreditCost` |
| **Routines** — managed functions enabled for API/CLI | `clay routines list --limit 100` · `clay routines get <id>` · `clay routines runs start` | the subset runnable from the CLI | declared `estimatedCreditCost`; **no per-run actuals exist here** |
| **Search** | `clay search filters-mode` · `clay search query-mode` · `clay search filters-mode fields --source-type {companies,people}` | company and people indexes, plus **free field metadata** | search-result quota, **not credits** |

**Catalogue size is not a fixed number and you cannot infer completeness from it.** One read of
`clay workflows actions list` reported **656 actions**; a fuller read of the same workspace on a different
day reported **~1,700**. Page it.

## Listing the catalogue

- **`clay routines list` omits things, and the default page hides it.** A default page returned 20 rows
  without a managed function that `clay routines get function:<id>` then fetched without complaint. And a
  **null cursor at exactly the default page size is not completeness** — the same command with
  `--limit 100` returned **36 more rows**. Always pass an explicit high limit; fetch by id as the fallback.
- **Enablement is a separate thing from existence, and fixing it is permanent.**
  `clay functions list` showed a managed phone function while `clay routines get function:<id>` returned
  not_found — the runs-start help names the cause: not enabled for API and CLI.
  `clay routines create function <id> --entity-type contact` registers it and **there is no
  `routines delete`**, so registration is a permanent workspace mutation. Prefer an already-registered
  routine covering the same capability, or run from a table or workflow.
- **Workspace-custom functions can be catalogue tools and invisible to routines.** One appeared in the
  action catalogue as a `function`-type tool, absent from the routines list, not_found on fetch. Same
  rule.

## Running

- **`clay routines runs start` needs an items envelope:** `{"items": [{"id": "<string>", "inputs": {…}}]}`.
  A bare inputs object is rejected. The help text's example does not show the shape; the error message
  does.
- **The bulk API caps 100 items per run.** A "single bulk run" over 182 rows executes as two, and a skill
  that promises one run is describing something that did not happen.
- **The single-action probe path is capped at 25 test runs per day, workspace-wide**, shared with everyone
  else working in that workspace. The rejection is free and names a retry-after of about 17 hours.
- **When the cap is reached, the platform's own refusal tells you where the action belongs: a workflow
  node.** That is product guidance, not a workaround — the same call, on the surface built to run it at
  volume, and it also exposes per-step billing metadata the ad-hoc path does not, which makes it the
  right place for anything you intend to measure. A loud label on the workflow keeps it identifiable.

## Environment

- **Behind an egress proxy the CLI needs `NODE_USE_ENV_PROXY=1`** — Node's fetch ignores `HTTPS_PROXY` by
  default, and the failure looks like the platform being down.
- **DNS-over-HTTPS endpoints are blocked in some sandboxes.** Never hardcode one; "any DNS tool" is the
  correct instruction, and a ~30-line raw UDP query suffices where no `dig` or `host` is installed.
- **Reserved and invented test TLDs are rejected at input validation** on some actions, so they are not
  available as honest-failure fixtures there.
- **A shared workspace makes balance-delta measurement invalid**, which is why the reported-cost rule in
  `DETERMINISM.md` exists. If you need a measurement, get exclusivity or use the workflow surface's
  per-step metadata.

## Workflow wiring, where a skill graduates to a table or workflow

Six things that each cost a debug cycle:

- Code nodes must define `handler(context)` returning a dict; a top-level `return` is a syntax error.
- **Pinned inputs that resolve to undefined *or empty string* fail the whole run.** Pin container objects
  rather than deep paths, and emit non-empty sentinels.
- Raw array pins into agent prompts may not render — flatten to strings first.
- Tool parameters sourced two or more hops upstream need **both** an input-mapping reference and a matching
  schema pin on the tool node.
- `automapInputs`, which appears in plugin documentation, **is not accepted by the deployed MCP server.**
  Documentation drift; verify against live schemas.
- **Deterministic code beats a model for comparison tasks.** Two models given a domain-comparison job
  wandered off to web search instead of using the inputs they were handed.
