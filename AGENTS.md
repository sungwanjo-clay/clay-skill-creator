# Working in this repository

This repository is the kit for authoring a Clay GTM skill and submitting it to the marketplace.
If you are helping someone build a skill, read `START-HERE.md` first — it is the entry point, and
this file only points at things.

## What this repository is

**Generated.** Every file here is produced from a private source repository and mirrored in, so a
hand-edit will not survive the next rebuild. Read freely and treat the tree as read-only; a change
that should stick belongs in the source, not here.

## Three things worth knowing before writing a skill

- **One `SKILL.md` at the package root.** Supporting files go under `references/` or `scripts/`,
  and every one of them must be referenced from the body. `PACKAGE-LAYOUT.md` is the contract.
- **A skill has to run on someone else's machine.** No table ids, column ids, account handles or
  credentials in the body — those belong to whoever wrote it, not whoever installs it. Everything
  the installer supplies goes in a `## Declared inputs` table, with what happens when it is absent.
- **Nothing is sent without an explicit yes.** `tools/submit_skill.py` previews first and refuses to
  send without a token that only the preview mints, so a submission cannot happen as a side effect.

## Checking a package

    python3 tools/package_skill.py validate <package-dir>   # shape, plus the content checks
    python3 tools/run_identity_checks.py                    # name/folder identity across skills/
    python3 tools/run_injection_conformance.py              # the safety rules, self-checked

`VALIDATION.md` says what each exit code means and which findings block. `DETERMINISM.md` covers
choosing between Clay functions when more than one would do the job.

## Where the worked examples are

`examples/` is a curated set of finished skills — the format demonstrated rather than described —
including a low-yield case: what an honest skill looks like when the source table did not hold
enough to convert. `skills/` is published skills, written by whoever published them, and is not
part of this kit.
