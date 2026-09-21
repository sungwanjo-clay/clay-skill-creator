# Optional Exa Time Machine

The base combined workflow uses fresh Claygent research. To compare historical and current
observations automatically, use a dedicated Exa account saved in Clay.

1. In Clay's HTTP API enrichment, choose **Select header account → Add account**.
2. Save `x-api-key` with your Exa key in that secure account, named **Exa — Alpha Campaign**.
   Manage it through Settings → Connections. Do not paste the key into chat, plain Headers,
   a contact row, a shared brief, or a workflow prompt.
3. Pass only the selected account ID (or an inspected native tool ID already bound to that exact Exa account) to this package's installer:

```bash
python3 scripts/install.py --workspace WORKSPACE --state PRIVATE_EXA_INSTALLATION.json \
  --exa-account SELECTED_EXA_HEADER_ACCOUNT --create
```

This creates a separate pair of workflows. Do not reuse an installation receipt for another
version. The account is bound explicitly to both native HTTP actions in the per-person helper.
The code never sees the key. Exa requests run only after the person's email passes verification.

In brief_json set comparison_mode to before_after, comparison_as_of to a past YYYY-MM-DD,
comparison_focus to the kind of shift that matters, and optionally comparison_page_path
(default `/`, for example `/pricing`). The employer domain comes from the actual person.

Two native HTTP API actions POST to https://api.exa.ai/contents. Each requests exactly one
same-company URL: the historical call uses snapshotAsOf; the current call uses maxAgeHours=0.
The native normalizer requires successful responses, matching URLs, request IDs, substantive
text and a freshly crawled current response. In strict `before_after` mode it fails on unknown response envelopes or
unavailable history. In `auto` mode it preserves available valid observations, records
why a side is unavailable, and allows Claygent to find an independently verified dated
event. Missing history never supports a comparison. Copy independently checks that the observations support a real shift.

snapshotAsOf is a retrieval cutoff, not a capture date or the date the business changed.
Published dates do not establish historical captures. Changed messaging does not prove a
new operational need. No history means no before-and-after claim. Strict comparison holds; auto may use a verified dated event.

The API key must have applicable Snapshot access. Coverage, trial caps and entitlement vary.
Run one real company and inspect both native HTTP outputs before scaling. Fixture tests do
not prove an authenticated call. Exa and Clay usage are separate; no fixed price is promised.

Official references: https://university.clay.com/docs/http-api-integration-overview and
https://exa.ai/docs/reference/get-contents.
