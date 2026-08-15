# Validate before you submit

Run this on your package from the root of this repository. It catches, locally, the things that
would otherwise come back as a rejection.

The tools are not on your `PATH` — invoke them by path with `python3`, as written below. An earlier
version of this file documented `package_skill.py validate your-skill/`, which fails with
`command not found` at precisely the moment you are trying to check your work.

```
python3 tools/package_skill.py validate build/<slug>
```

Exit `0` means the package shape and content checks pass. Non-zero prints every finding with its
file and line.

## What it checks

**Shape** — one root `SKILL.md`, supporting files under `references/` or `scripts/`, every
supporting file referenced, nothing loose at the root, no symlinks.

**Content** — every relative reference resolves inside the package; no workspace identifiers
(table ids, column ids, workspace ids, saved-view names, auth handles); no bare credentials; no
private or unreachable endpoints.

Findings come in two severities. **`block`** must be fixed — the package will not be accepted.
**`report`** is a heuristic worth a look: it can be a false positive, and it does not stop you.

## Thresholds, if you converted a table

```
python3 tools/derive_recipe.py compare <table-config.json> <claims.json>
```

Exit `3` means a threshold in your skill does not match the formula it came from. That is a
transcription error, and it is the one class of defect you are least likely to spot yourself —
your table works, so a skill that misquotes it still reads as correct.

## What validation does NOT tell you

It checks that the package is **well-formed and portable**. It does not check that the skill is
*good*: whether the logic is right for the job, whether the thresholds are the ones you want,
whether it helps anyone. A clean validation is a floor, not a verdict.
