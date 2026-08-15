# Prerequisites

Required for **table → skill**. Not needed for interview → skill.

## 1. Install the Clay CLI

Follow Clay's own CLI installation instructions for your platform.

## 2. Authenticate into your own workspace

```
clay login
clay whoami
```

`clay whoami` must return your user id. That id is what scopes every table read — see step 1 of
[`workflows/table-to-skill.md`](workflows/table-to-skill.md).

`clay login` pins the session to whichever workspace you pick on the consent screen. If the table
you want lives somewhere else, run `clay login` again and pick that workspace.

## 3. Know what this costs you

Reading table configuration is **free**. No credits, no action runs, no enrichment. The four
commands used are metadata reads.

## Why the CLI is required, stated plainly

It is a real cost and we would rather name it than pretend otherwise: if you live in Clay's UI
rather than a terminal, installing a CLI and authenticating is 15–30 minutes of setup before you
convert anything. That filters out some of the people this feature is most for.

Two honest answers. **Interview → skill needs none of it** — if the setup is not worth it, that path
reaches a finished skill from a conversation. And the CLI requirement is about *transport*, not
about the conversion: if an in-product path arrives later, the same conversion runs behind it and
nothing you learn here is wasted.
