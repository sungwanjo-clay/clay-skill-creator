# Interview → skill

For when there is no table, or the table has too little in it to convert. See step 4 of
[`table-to-skill.md`](table-to-skill.md) for what "too little" means and how it is measured.

No CLI needed.

## What you will be asked

The order matters: purpose before mechanics, because mechanics without purpose produces a skill that
runs and helps nobody.

1. **The job.** What does someone want done, in their words? A skill is found by how people ask for
   it, so this becomes the description that decides when it triggers.
2. **The input.** What does the installer start with — a CSV of domains, a single company, a list of
   people? Name the fields.
3. **The steps.** What happens, in order, and what each step needs from the ones before it.
4. **The decisions.** Every threshold, band, tier or cutoff, and *why* that number. A skill that
   says "score highly" is not runnable; one that says "50 or more employees" is.
5. **The honest edges.** What should it refuse to guess at? What does it cost per row? What does it
   do when data is missing — and "returns nothing" is a real answer that should be stated, not
   padded.
6. **The boundary.** What should it NOT be used for? Naming the neighbours is what stops the wrong
   skill being picked.

## What comes out, and its limits

A complete `SKILL.md` whose **What this skill does not claim** section names the interview as the
source of its logic.

That gap is not a formality. Interview-derived logic has **no ground truth anywhere** — it is your
stated intent, and nothing can check it against a system that already ran. A table-derived skill at
least has its thresholds compared against real formulas. This one does not, and the package says so
rather than implying a check that never happened.
