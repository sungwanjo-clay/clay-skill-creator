# Identity and domains

> **Observed 2026-08-07 – 2026-08-14**, one workspace, one plan, by builds that spent the credits. Every
> figure was read off a live response. **Report what you read; never quote a figure here as anyone's
> price.** Structural facts do not rot the way prices do. If the live catalogue disagrees, it wins.

**This is the keystone step and it poisons everything downstream.** A wrong domain does not fail — it
enriches, scores and ships, attached to the wrong company.

| Need | Reach for | Read this, not that |
|---|---|---|
| name → domain | the managed Company Domain function | agrees with confident ground truth on only **~60%** of resolvable records. It returned a *careers* subdomain for a well-known consumer brand, and an unrelated company for a weak input. **It never flags dead or acquired.** |
| is this domain alive? | `http-api-v2` — **free**, no `creditCost` field, the free-utility shape | 2xx returns the body only; **non-2xx surfaces as an action error naming the status**, which is the honest channel. Redirect destination is recoverable from canonical/og tags. |
| normalise a URL, company name, phone, or person name | `normalize-url` · `normalize-company-name` · `normalize-phone-number` · `clay-normalize-first-and-last-names` | free tier-1 utilities |
| dedupe a list of *values* | `normalize-and-deduplicate-list` | array or comma-list in, `dedupedListObject`/`dedupedString` out. **Value-level, not record-level** — it does not dedupe contacts |

## The five findings that changed how a skill does this

**A dead domain costs nothing to detect and minutes to detect wrongly.** A scrape of a nonexistent domain
ground past a 60-second timeout with no verdict, while a free DNS-or-status check answers in under a
second. The free pre-gate is mandatory, not defensive.

**Enrichment is not liveness** — the general rule is in `DETERMINISM.md`; here is the specific damage. A
golden run asserted two defunct companies as live because the executor substituted a company enrichment
call for the liveness probe. Dead and acquired companies enrich cleanly on last-known data, so both rows
came back filled and confident, and the only thing wrong with them was the answer.

**`acquired` has to be its own verdict, not a note on a resolved one.** A five-value contract —
`resolved` / `ambiguous` / `not_found` / `acquired` / `mismatch` — where only `resolved` asserts a domain
and the other four abstain. An "acquisition acceptable with reasoning" loophole let three acquired
companies ship their stale old-name domains as answers. A rebrand stays resolvable; an acquisition does
not, and the acquirer's domain is a candidate rather than the answer.

**A live, branded, content-rich page is not evidence a company still exists.** Two rows served full
product pages while being dead or quietly acquired; news screens were silent; nothing but a withheld
lifecycle label distinguished them from healthy companies. From a name and a region those rows are
undetectable, and the honest output is an ambiguity verdict rather than a confident one.
**Bot-blocked is not dead** either — treat a block as no evidence, not as negative evidence.

**`domain` is not an identity.** One enumeration of a single domain returned **33 records, every one
carrying that domain** — unrelated micro-businesses, creators and small organisations whose company page
lists a payment link as its website, one of them reporting a size band of `10,001+`. Deduping on domain
merges dozens of unrelated organisations; deduping on the company id keeps all 33, because they are
genuinely distinct records rather than duplicates. **Neither key resolves it, so flag rather than
resolve:** hold out records that share a domain while their names, countries and size bands are mutually
unrelated, count them, and list them. The tell separated the cases cleanly in one observation and is
presented as a tell, not a rule.

## The output contract that survives whichever path won

One coalesce column — a *validated* domain — laddering **validated input → redirect-resolved →
scraped or recovered**, with every downstream stage referencing only the coalesced column and never the
raw input. Spec it explicitly; it is the seam between identity resolution and everything else.

**A domain recovered for a row that already failed validation goes back through the same validation a
second time.** Recovery never bypasses the gate.

**Redirects that land on a social platform are invalid, not resolved.** Maintain the blocklist explicitly:
`linkedin.com, facebook.com, instagram.com, twitter.com, x.com, t.co, tiktok.com, youtube.com, youtu.be,
pinterest.com, snapchat.com, snap.com, reddit.com, threads.net, whatsapp.com, wechat.com, discord.com,
twitch.tv, vimeo.com, medium.com, vk.com`.

## Free corroboration worth harvesting

A company enrichment call made for other reasons often **echoes the resolved profile URL**. That is a free
high-accuracy identifier for downstream steps that would otherwise pay to resolve it. The echo doubles as
the wrong-entity detector, and that rule is in `DETERMINISM.md`.
