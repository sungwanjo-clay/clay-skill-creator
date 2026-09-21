# Connect the user's own audience or contact table

Choose the exact source at installation. A generic portable package must not contain the
author's segment ID, table ID, field IDs or real contacts. A source_kind label alone is
not a connection. A source record ID alone does not perform lookup or writeback.

## Shared brief versus record fields

| Shared setup, editable at the beginning | Each record |
| --- | --- |
| Offer, ICP, CTA, greeting, signature, sender name, settings | Employer domain, company name, first name, role, stable contact/row ID, optional evidence receipts |

A row-specific override can be mapped intentionally. By default, one brief applies to the
selected audience/table. Do not infer an employer from a personal email domain. If the
company relation is missing, resolve it in the source before running. Do not enrich every
record just to test the mapping.

## Audience installation

1. Ask which existing audience if it has not been named. Inspect it with `clay audiences get`.
   Confirm people versus companies and the selected scope. Read the real field definitions
   and trigger output schema; do not guess contact/company JSON paths.
2. Save the shared brief as a JSON object of the manual input names. Save a field-map JSON
   object from input names to observed source paths. Only scalar object-key paths are
   supported, starting with `$.`. Required mappings: company_domain and source_record_id.
   Optional: company_name, recipient_name, recipient_role, evidence_json.
3. Preview installation:

   ```bash
   python3 scripts/install.py --workspace WORKSPACE --state RECEIPT \
     --audience SELECTED_SEGMENT --entity-type CONTACT \
     --brief SHARED_BRIEF --field-map CONFIRMED_MAP
   ```

   Use ACCOUNT for a companies audience. Add `--create` when creation is authorized.
   The installer makes a dedicated audience-triggered draft with a first Python adapter.
   It does not change the manual demo installation or publish the trigger.
4. Read the created trigger's actual output schema and the adapter/validation bindings.
   If a supplied path is absent, correct the mapping before running. The adapter rejects
   missing fields rather than silently substituting another person's data. Keep the install
   receipt and brief private. If changing the saved adapter after install, use a read-modify-
   write node update; do not rerun installation with a different digest into the same receipt.
5. Run one explicitly selected or approved sample record using the native audience test command.
   Inspect the input identity, output source_record_id and exact greeting. A graph validator
   cannot establish that a real contact mapping works.
6. Only activate the audience trigger for the user's intended scope. Publishing an audience
   trigger can process new members. Report whether it is draft, tested, or activated separately.

The source adapter template is `source-adapter.py`. Its settings are editable in the first
native node. Updating those settings changes future runs; prior evidence/drafts are not
silently relabeled. The adapter is bounded, deterministic and requires actual source identity.
No automatic writeback is installed. Review outputs in run history; writeback would require
explicit field selection and a separate tested native action.

## Contact table: native Invoke Workflow

Clay table triggers are created from the table UI, not through the current workflow CLI.
Do not work around that limitation with a custom webhook or external API.

1. Select the exact contact table and inspect its columns. Preserve existing columns and copy.
2. In that table, add the native **Invoke Workflow** action and select this installation.
3. Map the target company domain, company name, first name, job title and stable row ID to
   company_domain, company_name, recipient_name, recipient_role and source_record_id.
   Set source_kind to table. Map Offer, ICP, CTA, greeting and signature from shared settings
   columns or explicit action constants, according to the user's preference.
4. Inspect the generated clay_table trigger. Verify the first executable node receives the
   mapped values from that trigger, not the unrelated manual trigger. Rebind first-node
   sourceNodeId/sourcePath to the actual table-trigger schema if needed. Do not leave an
   unconnected trigger or a reference unavailable on that execution path.
5. Keep auto-run off during setup. Test one selected row and inspect the exact invocation/run
   receipt. Verify source_record_id, contact identity, personalized greeting, chosen CTA,
   signature, terminal verdict and returned subject/body. If the table action exposes only a
   run reference, follow it to the terminal output; do not claim body columns were populated.
6. Only map results to new review columns if the native action exposes those outputs and the
   user requested that writeback. Never overwrite existing campaign copy or turn on sending.

Until steps 2–5 happen against the selected table, describe this as a documented connection
path, not a connected/tested table. If the action is unavailable in that workspace, report
that exact capability limit. The standalone manual workflow remains usable.

## Pick a people segment or table without typing its ID

Run the setup picker from this package:

```bash
python3 scripts/setup.py --kind audience --output PRIVATE_SETUP_DIRECTORY
python3 scripts/setup.py --kind table --output PRIVATE_SETUP_DIRECTORY
```

The picker displays one page of named native sources at a time; choose a number or load
another page. Audience choices contain **people segments only**. Table choices display
workbook names to distinguish duplicate table names. Selecting a table does not prove it
contains people: inspect the saved column schema before connecting it.
The picker reads the selected source configuration, writes `source.json` and `brief.json`
privately, and collects offer/ICP, CTA, greeting, signature and comparison preferences once.
It does not copy contacts, connect a source, publish, or launch a batch.
Use `--source-id` for an exact known source, or `--brief` to reuse a brief.

After confirming real audience trigger paths, add `--field-map CONFIRMED_MAP --install`
to create a dedicated audience draft. The table path uses the native UI steps above.
Both paths use the same copy graph; no per-person prompt editing is necessary.

### Per-person comparison mapping

Map the employer domain, first name, role and stable contact/row ID from each person.
Map optional `past_observation_json` and `current_observation_json` from that person's
company evidence columns, or map `evidence_json`. Do not combine duplicate receipt IDs.
The adapter supports JSON strings in scalar fields. It never assigns another company's
observations or a shared contact name to every person. Company evidence can be shared
across coworkers only through a verified employer relationship in the source.
Use `source_id` for the segment/table and `batch_id` for the shared version/run label.
These, plus `source_record_id`, survive into ready and held outputs.
See `time-machine.md` for the comparison contract.

### Run at volume in Clay

1. Select the intended people segment or filtered contact table, then preview the scope.
2. Configure the shared brief and map the person/company columns once.
3. Test selected contacts and review identity, greeting, before/after claims, exact CTA,
   signature and holds. A table/segment mapping is not proven by a manual company test.
4. Use Clay's audience bulk-run UI or the table's native action run controls for the chosen
   scope. The workflow test CLI is a bounded QA tool, not the batch runner. Source publication
   for new audience members is a separate choice from a one-time bulk run.
5. Inspect run history for every processed contact. Ready/held/failed are separate outcomes;
   completion is not sending. Configure new output columns only if Invoke Workflow exposes
   those outputs; otherwise review terminal results via the run references.

This version runs research per person. It does **not** automatically deduplicate company
research, prevent replay, write results back, schedule recurrence, or prove batch throughput.
Do not claim those optimizations. Reuse source evidence columns to avoid mismatching company
observations, but do not call that an automatic shared research cache. Actual runtime and
charges vary with branching, research and Clay capacity. Confirm scope before large runs.
