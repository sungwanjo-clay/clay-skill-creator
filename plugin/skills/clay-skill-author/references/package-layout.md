# Package layout

## Shape

```
your-skill/
  SKILL.md              exactly one, at the root
  references/           optional
  scripts/              optional
```

Rules, all mechanically checked:

- **Exactly one `SKILL.md`, at the root.** Not two, not one nested.
- **Supporting files live under `references/` or `scripts/`.** Nowhere else, and not loose at the
  root.
- **Every supporting file must be referenced from `SKILL.md`.** An unreferenced file is either
  decoration or dead weight, and both misrepresent what the package actually is. This is the
  mechanical form of "do not add files to look thorough" — if it earns its place, link to it.
- **And every reference must resolve to a file that ships.** The converse, and the one that actually
  bites: a `SKILL.md` naming `references/node-code.md` when no such file exists is a skill that reads
  as complete and stalls on first use — or worse, the agent invents the missing content, which looks
  like success. `portability/missing_file` blocks on it and names the file — but it blocks when you
  validate, and a `SKILL.md` you have already handed to someone has not been validated yet. If you
  are not going to write the file, inline what it says and name no file.
- **No references outside the package.** A link to a file on your machine, or in a repo, is not
  something the installer has.
- **No symlinks.**

A single-file skill is a perfectly good skill. Most are.

## Deterministic packaging

Package identity is the **content manifest**: the set of relative paths plus a SHA-256 per file.

```
package_skill.py manifest your-skill/
package_skill.py zip      your-skill/ your-skill.zip
package_skill.py verify   your-skill.zip --manifest manifest.json
```

Two builds of identical content produce an identical `manifest_sha256`, regardless of when they ran
or on which machine. That is the property that matters: it lets anyone confirm the package they
received is the package you built.

Archive bytes also happen to be stable here, because entry order, timestamps and permissions are
normalized. Do not rely on that across tool versions — a ZIP's bytes depend on the compression
library. **Compare manifests, not archives.**
