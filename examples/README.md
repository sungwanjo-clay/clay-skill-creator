# Examples

Two of these are **real shipped skills**, projected from the live library. One is **illustrative**.
The distinction is stated because it is the same distinction your own skill will carry in
`proof_status`, and because an example that claims more than it has proven teaches the wrong lesson.

| Example | Provenance | Shape |
|---|---|---|
| [`find-linkedin-profile/`](find-linkedin-profile/) | **shipped skill**, built through the factory pipeline and static-checked | single-file |
| [`resolve-company-domain/`](resolve-company-domain/) | **shipped skill**, same, plus a reference file | multi-file |
| [`low-yield-fallback/`](low-yield-fallback/) | **illustrative** — written for this repo, never evaluated | single-file |

## Why two are real and one is not

The two real ones exist because we should not teach "here is what good looks like" with something we
made up for the occasion. Both went through the same authoring path, the same portability and
decidability checks, and both are `built` in the library. Read them for **form**: the insight stated
first, steps in dependency order, decision rules that resolve to exactly one answer, abstention as a
real outcome rather than a fallback, and a description that names the neighbouring skills it should
not be confused with.

`low-yield-fallback/` has no real counterpart because none of the shipped skills came from a
low-yield table — the library was authored directly, not converted. It shows the *shape* of what the
converter produces when your table has too little in it to convert: a complete, usable skill whose
`proof_gaps` name the interview as the source of its logic. Treat it as a template for that outcome,
not as a validated skill.

## What these are NOT

They are not a menu to copy. The library already contains 30 skills — see
[`../EXISTING-SKILLS.md`](../EXISTING-SKILLS.md) before you build, because a near-duplicate helps
nobody: an agent choosing between two overlapping descriptions picks unpredictably, and both skills
lose.
