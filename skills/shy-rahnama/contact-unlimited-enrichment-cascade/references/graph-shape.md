# The graph, and the traps that shape it

Every rule here exists because breaking it cost a real debugging session. None of them is
obvious from the outside, and several fail *silently* — which is why they are written down
rather than left to be rediscovered.

## The leg

```
gate ──rule_need──> tool ──> pass ──┐
     └─rule_have────────────────────┴──> resolve ──> (next gate)
```

| Node | Type | Does |
|---|---|---|
| `<n> <field> gate` | conditional, 2 rules | `rule_need` → look it up · `rule_have` → skip to resolve |
| `<n>a <tool name>` | tool | the provider call |
| `<n>p <field> looked up` | conditional, 2 rules | `rule_found` and `rule_empty`, **both to resolve** |
| `<n>r <field> resolve` | code | merge supplied-vs-found, label provenance, re-emit the record |

**Why `pass` exists.** `resolve` must be reachable whether the lookup ran and found
something, ran and found nothing, or never ran. `pass` makes both post-lookup lanes
conditional, so `resolve` has three *conditional* parents. A **plain** edge into that join
hangs the run whenever a sibling lane is pending — the run does not error, it simply never
finishes, which is the most expensive failure to diagnose.

**Why `pass` has two rules that go to the same place.** A conditional with no matching rule
hard-fails. A lookup that found nothing must still continue, so "nothing found" is an
explicit routed rule rather than a fall-through.

**`resolve` is a plain code node with three incoming edges. Never put a merge node there.**
Three edges converging is exactly the shape that invites one, and an asymmetric merge stays
pending forever.

## The carry contract

**Every `resolve` re-emits the COMPLETE record**, not just its own field. That is what lets
every downstream node pin from exactly one upstream node instead of accumulating a pin per
leg, and it is why adding a provider is an append rather than a rewrite: the pin count stays
flat as the cascade grows.

It also means **`need` is recomputed by every node that emits the record.** A gate therefore
pins one boolean and nothing else. This is the mechanism that makes several legs on one
field into a waterfall with no extra machinery: a later leg's `need` is false the moment an
earlier leg filled the field.

## Pin paths

| Pinning from | Path |
|---|---|
| a tool node | `$.result.<path>` |
| a code node or a trigger | `$.<path>` |

Mixing them resolves to **null**, silently. A tool node's whole result is `$.result`; a code
node's whole output is `$`.

A node may pin from a node that is not its edge parent — a leg's tool node pins the record
from the previous `resolve` while its only edge comes from its gate, and that is the proven
shape this build uses throughout.

## Scan, don't pin, the response

`resolve` walks an ordered list of candidate paths and takes the first non-empty,
non-sentinel value. **This is deliberate and it is not defensive programming.** A wrong
pinned response path resolves to null, which reads as "not found" — a genuine miss and a
mis-wired pin look identical, so the bug survives review and shows up as a bad hit rate
months later. A scan either finds the value or genuinely did not get one.

The same reasoning covers sentinels: a provider returning the literal string `n/a` has not
found anything, and treating it as a value poisons the record and every count built on it.

## Attribution must not be overwritten

When several legs fill one field, every later leg sees the value already present. Labelling
it `supplied` at that point erases which provider actually found it — and with it any
ability to judge provider hit rates, which is the entire reason for running a waterfall.
So a leg only sets `supplied` when the existing provenance is empty or `unknown`.

This was a live bug, not a hypothetical.

## Triggers

**A trigger create mints the trigger node but leaves it UNCONNECTED.** Wire it explicitly or
every run dies with "Workflow has no initial node".

**The trigger's input schema must be COMPLETE.** Fields absent from it are stripped at
intake. A bare `{"type":"object"}` accepts POSTs and then dies with the same misleading
"no initial node" error.

**Wire intake from EVERY trigger node, not just the one you created.** Binding a Clay table
to the workflow is done in the UI and is invisible to the config, but it adds its own trigger
node. An edge list containing only the webhook node severs that binding on every rebuild.
Seen in production: a rebuild disconnected a bound table and every run died until the edge
was restored.

**Intake takes FLAT fields, not one `payload` object.** A Clay table binds to a *node* and
maps columns onto that node's inputs; a payload object would mean hand-writing JSON per row.
The webhook path pins the same flat fields, so either entry point works.

## Writing nodes

**Send every pin on every schema write.** An `inputSchema` write rebuilds the binding map
from exactly what the call contains. Omit a pin and it is destroyed — and the call reports
success. The success echo is not proof, which is why every write is read back and verified.

**Clay rejects changing a tool node's `toolType` in place** ("Delete this node and create a
new one"). Swapping a leg from a Clay function to a direct HTTP call — exactly what adding a
flat-rate provider involves — needs a delete and recreate, then a rewire.

**A tool node cannot be trusted to report its own type.** `nodes get` reads `tools` back as
`null` on `clay_function` nodes, which made every rebuild delete and recreate them. So the
type each node was created with is recorded in `build-state.json` and preferred over the
live read.

## The code runtime

**No `datetime`, `urllib`, `hashlib` or `base64`.** Plain string work, plus `json`.

**The code-test sandbox has modules the runtime does not**, so a passing sandbox run is not
evidence the node works in a real run. Verify in a real run.

**Required inputs reject an empty string outright.** This is why `requires` exists: a leg
whose input was never found must skip, not fire with an empty value and kill the run.

## Draft versus published

**A test run fires the DRAFT. A webhook or a bound table fires the PUBLISHED version.** So a
green test proves nothing about live traffic, and an edit is not live until it is published.
The build leaves a draft and says so unless `--publish` is passed.

## Verifying before you build

`scripts/test_codegen.py` generates every code node the build would write, parses it, and
runs the handlers against a fake context — no Clay, no credentials, no network, no cost.
Run it after changing a config or the build. A syntax error or a leftover substitution
marker otherwise produces a graph that builds perfectly and dies on every row.
