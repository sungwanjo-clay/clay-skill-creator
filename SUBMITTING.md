# Submitting

1. Validate locally — [`VALIDATION.md`](VALIDATION.md).
2. **Read your `SKILL.md` end to end.** You are the last reviewer before it goes out, and the only
   one who knows what the table was actually for.
3. Open the Clay Marketplace submission form.
4. Upload the package, or paste the `SKILL.md` contents.
5. Submit.

## Three things to expect

**Nothing is submitted without your explicit confirmation.** There *is* a submission API, and the
skill can call it — what it cannot do is call it without you saying yes first.

The mechanism, so the promise is checkable rather than a claim: `submit_skill.py preview` prints
exactly what would be sent, including the consent text, and mints a random one-use token bound to
that package and those details. `send` refuses without it. Edit the package after the preview and
the token stops matching. The token is deliberately **not** computable from the request, so nothing
that merely controls the request can produce one.

That is not proof a human read the screen — nothing over an API can be. It is proof that a value
only the preview can mint was presented, which is the strongest checkable form of "you were asked".

**A submission is reviewed.** It goes through automated checks and a human read, and can come back
with revision requests. The local validator exists so the automated half rarely surprises you.

**Submitting is not publishing, and overlap is not a rejection.** We do not promise to publish
every submission. What we *don't* do is turn you away for building something we already have —
the skill carries the neighbour list and names your neighbours for you, rather than telling you
which jobs are taken. Where two skills do the same job we compare them on that job's own axes —
completeness, correctness, cost — and publish the one that wins. That comparison is on results, not
on which description sounds closer, which is exactly why it is not a judgment you should have to
make before you start. A near-duplicate that turns out better than ours is the outcome we want most.
