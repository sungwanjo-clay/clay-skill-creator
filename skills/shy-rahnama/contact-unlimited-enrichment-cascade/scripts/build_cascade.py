#!/usr/bin/env python3
"""
Build the contact enrichment cascade in a Clay workspace from a declarative config.

Graph, one four-node group per leg:

    gate ──rule_need──> tool ──> pass ──┐
         └─rule_have────────────────────┴──> resolve ──> (next gate)

`pass` exists so `resolve` sees two CONDITIONAL parents rather than one conditional and one
plain node, which hangs the run whenever the sibling lane is pending.

Every `resolve` emits the COMPLETE record, so each downstream node pins from exactly one
upstream node instead of accumulating a pin per leg. That is what keeps the pin count flat
as legs are added, and it is why adding a provider is an append rather than a rewrite.

Several legs may name the same `field`. That is how a waterfall is expressed: each leg's
`need` is recomputed by the previous resolve, so a later leg fires only if the earlier ones
came back empty. No extra machinery.

Credentials: a leg calling a provider over HTTP MUST name `app_account` — a Clay HTTP API
account the installer created, which Clay uses to inject the auth header server-side. This
script has no code path that accepts, reads, or writes an API key, because node source is
stored by Clay and readable by anyone who can open the workflow.

Usage:
    python3 build_cascade.py --config cascade-config.json --dry-run
    python3 build_cascade.py --config cascade-config.json
    python3 build_cascade.py --config cascade-config.json --publish
"""
import argparse
import json
import os
import re
import sys

# Importing cascade_lib would otherwise leave scripts/__pycache__ inside the package, and a
# file nothing references is a BLOCKING validator finding. Running the build must not break
# the package that ships it.
sys.dont_write_bytecode = True

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cascade_lib import Build, HTTP_ACTION_KEY  # noqa: E402

# THE INTERFACE. Prescribed, identical in every workspace, and the whole reason this build
# needs nothing from the caller at build time: a Clay table binds to the intake node in Clay's
# UI and maps its own columns onto these inputs, whatever they happen to be called, whenever
# somebody wants to. There is nothing to read and nothing to ask.
REQUIRED_IN = ["contact_name", "company_name"]
OPTIONAL_IN = ["contact_email", "contact_linkedin", "contact_phone",
               # Accepted, never required. Each is a lookup not made, and a domain is the
               # cheapest lever there is.
               "company_domain", "job_title"]

# The six the cascade always returns, blank when skipped or not found. A consumer written
# against these works against any cascade this build produces.
GUARANTEED_OUT = ["contact_name", "company_name", "contact_email", "contact_linkedin",
                  "contact_phone", "contact_email_verified"]

# The record contract: the interface plus what the cascade derives and fills internally.
FIELDS = ["contact_name", "first_name", "last_name", "job_title", "company_name",
          "company_domain", "company_linkedin", "contact_linkedin",
          "contact_email", "contact_phone", "contact_email_verify_status"]
# Caller opt-OUTS, for the three fields the cascade exists to fill. Absent means FALSE — do
# the work — so a caller who has never heard of these gets the full cascade.
SKIPS = ["skip_linkedin", "skip_email", "skip_phone"]

# Caller opt-INS, for the two company fields. These are enabling lookups: they exist because
# the legs after them need a domain or a company profile, and nobody asks for one on its own.
# So they default OFF and fire anyway whenever something downstream requires them — which
# keeps "an enabler costs nothing when nothing needs it" true.
#
# They get a flag at all because without one a field can never be REQUESTED, only inherited
# from whatever happens to need it: a provider that returns a company LinkedIn URL for free
# had no way to be asked for one. Opt-in rather than opt-out because the opposite polarity
# would fire these on every record where the field is missing, adding cost nobody asked for.
WANTS = ["want_company_domain", "want_company_linkedin"]
FLAGS = SKIPS + WANTS

# Config keys that used to carry credentials. Present in an old config, they are a hard
# failure with a migration message rather than a silent downgrade.
RETIRED_KEYS = ("http_secrets", "http_secret_header", "client_env")
CREDENTIAL_SHAPED = re.compile(
    r"(api[_-]?key|secret|token|bearer|authorization|passwo?rd)", re.I)

# ---------------------------------------------------------------- code bodies

INTAKE = r'''
def handler(context):
    # No datetime / urllib / hashlib / base64 in the Clay runtime - plain string work only,
    # plus json. Inputs are FLAT rather than one `payload` object because a Clay table binds
    # to a NODE and maps columns onto that node's inputs; a payload object would mean
    # hand-writing JSON per row. The webhook path pins the same flat fields.
    p = context.get_input("payload") or {}

    def s(v):
        return v.strip() if isinstance(v, str) else ""

    def either(k):
        return s(context.get_input(k)) or s(p.get(k))

    def skip(k):
        # Absent means do the work. Only an explicit true-ish value switches a field off, so
        # a caller that knows nothing about these flags gets the full cascade.
        v = str(context.get_input(k) if context.get_input(k) is not None
                else p.get(k, "")).strip().lower()
        return v in ("true", "1", "yes", "on")

    def domain(v):
        v = s(v).lower().replace("https://", "").replace("http://", "").strip("/")
        return v.split("/")[0]

    contact_name = either("contact_name")
    parts = contact_name.split()
    rec = {
        "contact_name": contact_name,
        # Derived, not part of the interface — a caller supplies one name, not three.
        "first_name": parts[0] if parts else "",
        "last_name": " ".join(parts[1:]) if len(parts) > 1 else "",
        "job_title": either("job_title"),
        "company_name": either("company_name"),
        "company_domain": domain(either("company_domain")),
        "company_linkedin": either("company_linkedin"),
        "contact_linkedin": either("contact_linkedin"),
        "contact_email": either("contact_email").lower(),
        "contact_phone": either("contact_phone"),
    }
    if not rec["contact_name"] or not rec["company_name"]:
        raise Exception("contact_name and company_name are required")

    for k in __FLAGS__:
        rec[k] = skip(k)

    # Provenance starts as supplied-or-unknown; each resolve overwrites its own field.
    for f in __FIELDS__:
        rec[f + "_source"] = "supplied" if rec.get(f) else "unknown"

    rec["source_ref"] = either("source_ref") or "n/a"
    rec["callback_url"] = either("callback_url") or ""
    rec["record_json"] = ""
    return _needs(rec)
'''


def needs_code(legs):
    """Generate _needs() from the leg list.

    A leg runs only when: the caller wants it, the field is still missing, AND every field
    it depends on is populated. That last clause is what stops a cascade erroring on an
    input it never got. Clay inputs marked required reject an empty string outright, so a
    leg whose pivot was never found must SKIP rather than fire and die.

    Request bodies are built here rather than in intake because a leg's body can reference a
    field an EARLIER leg resolved. _needs() runs in every node that emits the record, so by
    the time a leg's tool node reads its body, the body was rebuilt from the current record.
    """
    lines = ["import json as _cj", "", "",
             "def _needs(rec):",
             "    def val(f):",
             "        return str(rec.get(f) or '').strip()",
             "",
             "    def missing(f):",
             "        return not val(f)",
             ""]
    for l in legs:
        # A leg is eligible when the caller did not switch its field off, OR when some other
        # leg REQUIRES this field and is itself still wanted. That second clause is what makes
        # an enabling lookup happen: a profile URL nobody asked for still gets fetched when
        # the email leg cannot run without one. Without it, every leg keyed off that input
        # reports blocked_missing_input and the cascade quietly does nothing.
        consumers = [c for c in legs
                     if c is not l and l["field"] in (c.get("requires") or [])]
        cons = " or ".join(
            "(%s and missing(%r))" % (
                ("not rec.get(%r)" % c["skip"]) if c.get("skip")
                else ("bool(rec.get(%r))" % c["want"]) if c.get("want") else "True",
                c["field"])
            for c in consumers) or "False"
        if l.get("skip"):
            own = "not rec.get(%r)" % l["skip"]          # opt-out: on unless switched off
        elif l.get("want"):
            own = "bool(rec.get(%r))" % l["want"]        # opt-in: off unless asked for
        else:
            own = "False"                                 # pure enabler: demand only
        conds = ["(%s or (%s))" % (own, cons), "missing(%r)" % l["field"]]
        for r in l.get("requires", []):
            conds.append("not missing(%r)" % r)
        lines.append("    rec[%r] = (%s)" % (l["need"], " and ".join(conds)))
    lines.append("    rec['has_callback'] = bool(val('callback_url'))")
    for l in legs:
        pv = l["provider"]
        if pv["type"] != "http":
            continue
        k = l["key"]
        bmap, bstat = pv.get("body") or {}, pv.get("body_static") or {}
        if bmap or bstat:
            lines.append("    _b = dict(%r)" % (bstat,))
            for param, field in bmap.items():
                lines.append("    if val(%r): _b[%r] = val(%r)" % (field, param, field))
            cond = (" and ".join("val(%r)" % f for f in bmap.values()) if bmap else "True")
            lines.append("    rec['_body_%s'] = _cj.dumps(_b) if (%s) else ''" % (k, cond))
        else:
            lines.append("    rec['_body_%s'] = ''" % k)
        qmap, qstat = pv.get("query") or {}, pv.get("query_static") or {}
        if qmap or qstat:
            lines.append("    _q = dict(%r)" % (qstat,))
            for param, field in qmap.items():
                lines.append("    if val(%r): _q[%r] = val(%r)" % (field, param, field))
            lines.append("    rec['_query_%s'] = _q" % k)
    lines += ["    return rec", ""]
    return "\n".join(lines)


RESOLVE = r'''
import json

__NEEDS__

def handler(context):
    prev = context.get_input("prev") or {}
    found = context.get_input("found")
    rec = dict(prev)

    FIELD = "__FIELD__"
    SOURCE = "__SOURCE__"
    PATHS = __PATHS__
    SENTINELS = __SENTINELS__
    SKIP_KEY = __SKIPKEY__
    WANT_KEY = __WANTKEY__
    REQUIRES = __REQUIRES__
    # Extra data this leg contributes beyond its primary field. Providers often return far
    # more than the one value the leg exists to fill, and throwing it away means paying for
    # it twice when a later stage wants it. A dict or list is JSON-stringified so it can
    # ride through the record and out of emit.
    CAPTURE = __CAPTURE__

    def dig(obj, path):
        cur = obj
        for part in path.split("."):
            if isinstance(cur, list):
                cur = cur[0] if cur else None
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        return cur

    value = ""
    if isinstance(found, (dict, list)):
        # Scan a list of candidate paths rather than trusting one pinned response path. A
        # wrong pin resolves to null and reads as "not found", which is the failure hardest
        # to spot; a scan either finds the value or genuinely did not get one.
        for p in PATHS:
            v = dig(found, p)
            if isinstance(v, list):
                v = v[0] if v else None
            if v and str(v).strip() and str(v).strip().lower() not in SENTINELS:
                value = str(v).strip()
                break

    already = str(rec.get(FIELD) or "").strip()
    if already:
        # Do NOT clobber an attribution an earlier leg already set. When several legs fill
        # the same field (a provider waterfall), every later leg sees the value present and
        # would relabel it "supplied", erasing which provider actually found it - and with
        # it any ability to judge provider hit rates.
        cur = str(rec.get(FIELD + "_source") or "")
        if cur in ("", "unknown"):
            rec[FIELD + "_source"] = "supplied"
    elif value:
        rec[FIELD] = value
        rec[FIELD + "_source"] = SOURCE
    elif not prev.get("__NEED__"):
        # The leg never ran, and there are three different reasons why. Collapsing them
        # would make every provider hit rate downstream meaningless.
        if SKIP_KEY and rec.get(SKIP_KEY):
            rec[FIELD + "_source"] = "skipped"              # the caller switched it off
        elif WANT_KEY and not rec.get(WANT_KEY):
            rec[FIELD + "_source"] = "not_needed"           # opt-in, not asked for
        elif any(not str(rec.get(r) or "").strip() for r in REQUIRES):
            rec[FIELD + "_source"] = "blocked_missing_input"  # an input it needs never arrived
        else:
            rec[FIELD + "_source"] = "not_needed"          # nothing downstream wanted it
    else:
        rec[FIELD + "_source"] = "not_found"

    for out_key, path in CAPTURE.items():
        if str(rec.get(out_key) or "").strip():
            continue
        v = dig(found, path) if isinstance(found, (dict, list)) else None
        if v is None or v == [] or v == {}:
            continue
        rec[out_key] = (json.dumps(v, ensure_ascii=False)
                        if isinstance(v, (dict, list)) else str(v))

    return _needs(rec)
'''

EMIT = r'''
import json


def handler(context):
    rec = dict(context.get_input("prev") or {})
    rec.pop("record_json", None)
    out = dict(rec)

    # The record travelling between nodes carries machinery: the per-leg request bodies, the
    # need_* gates, the pinned constants. None of that is the deliverable, and a callback that
    # POSTs it is shipping this build's internals to somebody else's endpoint. So the OUTPUT
    # CONTRACT is built by exclusion here, and it is what record_json carries.
    ENRICHED = __ENRICHED__
    GUARANTEED = __GUARANTEED__
    noise = set(f + "_source" for f in __FIELDS__ if f not in ENRICHED)
    contract = {k: v for k, v in rec.items()
                if not k.startswith("_") and not k.startswith("need_") and k not in noise}
    # The guaranteed six are present even when empty. A consumer should never have to test
    # whether a key exists before reading it — blank means skipped or not found, and that is
    # a value, not an absence.
    for g in GUARANTEED:
        contract.setdefault(g, "")

    # The callback body is assembled here so the POST node stays a dumb transport.
    out["record_json"] = json.dumps(contract, ensure_ascii=False)
    out["callback_url"] = str(rec.get("callback_url") or "")
    out["has_callback"] = bool(out["callback_url"])
    out["_method_post"] = "POST"
    out["_headers_json"] = {"Content-Type": "application/json"}
    # Verification is reported, never destructive. The found address is always emitted so a
    # human can look at it; the VERIFIED slot is what downstream automation should consume,
    # and it is blank unless a verifier actually said so. A wrong address that silently
    # reaches a sending tool is worse than a blank one, and a "risky" or catch-all verdict
    # is not a pass unless the installer declared it one.
    vs = str(rec.get("contact_email_verify_status") or "").strip().lower()
    verified = vs in __VERIFIED_STATUSES__
    out["contact_email_verified"] = "true" if verified else "false"
    out["contact_email_verified_only"] = rec.get("contact_email", "") if verified else ""
    out["contact_email_verify_status"] = vs or "not_checked"

    # Deliverability is not correctness. A mailbox can verify perfectly and belong to a
    # different person at a different company, so the domain comparison is reported
    # separately: verified true with domain_match false is suspect, not clean.
    em = str(rec.get("contact_email") or "").strip().lower()
    dom = str(rec.get("company_domain") or "").strip().lower()
    if em and "@" in em and dom:
        em_dom = em.split("@")[-1]
        root = lambda h: ".".join(h.split(".")[-2:]) if h.count(".") >= 1 else h
        out["contact_email_domain_match"] = "true" if root(em_dom) == root(dom) else "false"
    else:
        out["contact_email_domain_match"] = "unknown"

    # Anything a leg captured beyond its own field, by the agreed prefix.
    pfx = "__CAPTURE_PREFIX__"
    out["captured_fields"] = ",".join(sorted(k for k in rec
                                             if k.startswith(pfx) and rec.get(k))) or "none"
    filled = [f for f in __FIELDS__
              if str(rec.get(f) or "").strip() and rec.get(f + "_source") not in ("supplied",)]
    out["filled_fields"] = ",".join(filled) or "none"
    out["filled_count"] = len(filled)
    # Re-assemble record_json now that the reporting fields exist, so the callback payload and
    # the node output describe the same record rather than differing by a few keys.
    for k in ("contact_email_verified", "contact_email_verified_only",
              "contact_email_verify_status", "contact_email_domain_match",
              "captured_fields", "filled_fields", "filled_count"):
        contract[k] = out[k]
    out["record_json"] = json.dumps(contract, ensure_ascii=False)
    return out
'''

DONE = r'''
def handler(context):
    # Terminal lane for records with no callback destination. Returns the record unchanged
    # so a run's final output is the same shape either way.
    return dict(context.get_input("prev") or {})
'''


def rules_gate(name, need_key, label):
    return {
        "nodeType": "conditional", "name": name, "conditionalMode": "rules",
        "rulesConditionalConfig": {"rules": [
            {"id": "rule_need", "name": "%s is missing - look it up" % label,
             "condition": {"type": "GroupOp", "combinationMode": "And", "items": [
                 {"type": "BinOp", "dataPath": [need_key], "operator": "Equal", "value": True}]}},
            {"id": "rule_have", "name": "%s already known or leg switched off" % label,
             "condition": {"type": "GroupOp", "combinationMode": "And", "items": [
                 {"type": "BinOp", "dataPath": [need_key], "operator": "NotEqual", "value": True}]}},
        ]},
    }


def rules_pass(name):
    # Two rules to the same target so EVERY outcome is routed. A conditional with no
    # matching rule hard-fails, and a lookup that found nothing must still continue.
    return {
        "nodeType": "conditional", "name": name, "conditionalMode": "rules",
        "rulesConditionalConfig": {"rules": [
            {"id": "rule_found", "name": "found",
             "condition": {"type": "GroupOp", "combinationMode": "And", "items": [
                 {"type": "BinOp", "dataPath": ["ran"], "operator": "Equal", "value": True}]}},
            {"id": "rule_empty", "name": "nothing found - continue anyway",
             "condition": {"type": "GroupOp", "combinationMode": "And", "items": [
                 {"type": "BinOp", "dataPath": ["ran"], "operator": "NotEqual", "value": True}]}},
        ]},
    }


def rules_callback(name):
    return {
        "nodeType": "conditional", "name": name, "conditionalMode": "rules",
        "rulesConditionalConfig": {"rules": [
            {"id": "rule_send", "name": "a callback URL was supplied - POST the record",
             "condition": {"type": "GroupOp", "combinationMode": "And", "items": [
                 {"type": "BinOp", "dataPath": ["has_callback"], "operator": "Equal",
                  "value": True}]}},
            {"id": "rule_none", "name": "no callback URL - finish here",
             "condition": {"type": "GroupOp", "combinationMode": "And", "items": [
                 {"type": "BinOp", "dataPath": ["has_callback"], "operator": "NotEqual",
                  "value": True}]}},
        ]},
    }


def validate(b, legs):
    """Everything checkable before anything is created. A guess that fails at run time
    fails AFTER the graph exists, which is the expensive order to find out."""
    problems = []

    for k in RETIRED_KEYS:
        if k in b.cfg:
            problems.append(
                "config key %r is retired: it carried an API key, and this build has no "
                "path that accepts one. Delete it and give each http leg an `app_account` "
                "naming the Clay HTTP API account that holds the credential." % k)

    for l in legs:
        pv = l["provider"]
        for key, v in pv.items():
            if CREDENTIAL_SHAPED.search(str(key)):
                problems.append(
                    "%s: provider field %r looks like a credential. A key never goes in "
                    "this config — put it in a Clay HTTP API account and name the account "
                    "in `app_account`." % (l["key"], key))
        if pv["type"] == "http" and not pv.get("app_account"):
            problems.append(
                "%s: an http leg must name `app_account` — the Clay HTTP API account "
                "holding this provider's credential. Clay injects the auth header from it, "
                "which is the only supported way to authenticate a leg." % l["key"])

    # Validate declared inputs against the provider's REAL schema. Guessing a parameter
    # name fails at run time as a missing-input error, long after the graph is built.
    for l in legs:
        pv = l["provider"]
        if pv["type"] != "clay_function":
            continue
        sch = b.clay("functions", "get", pv["_tableId"]).get("inputSchema") or {}
        known = set((sch.get("properties") or {}).keys())
        required = set(sch.get("required") or [])
        declared = set(l.get("tool_inputs") or {})
        if declared - known:
            problems.append("%s: unknown input(s) %s; provider accepts %s"
                            % (l["key"], sorted(declared - known), sorted(known)))
        if required - declared:
            problems.append("%s: required input(s) not mapped %s"
                            % (l["key"], sorted(required - declared)))

    # A leg that names a field outside the record contract would write a value nothing
    # downstream reads, and would look like it worked.
    for l in legs:
        if l["field"] not in FIELDS:
            problems.append("%s: field %r is not part of the record contract %s"
                            % (l["key"], l["field"], FIELDS))
        if l.get("skip") and l["skip"] not in SKIPS:
            problems.append("%s: skip flag %r is not one of %s"
                            % (l["key"], l["skip"], SKIPS))
        if l.get("want") and l["want"] not in WANTS:
            problems.append("%s: want flag %r is not one of %s"
                            % (l["key"], l["want"], WANTS))
        if l.get("skip") and l.get("want"):
            problems.append("%s: a leg carries either `skip` (opt-out) or `want` (opt-in), "
                            "never both" % l["key"])
        for r in l.get("requires", []):
            if r not in FIELDS:
                problems.append("%s: requires %r, which is not a record field"
                                % (l["key"], r))

    if problems:
        raise SystemExit("config will not build:\n  " + "\n  ".join(problems))
    print("config validated against live provider schemas")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve providers and validate inputs; create nothing")
    ap.add_argument("--publish", action="store_true",
                    help="publish the draft as live. Without it the build leaves a DRAFT: "
                         "a test run fires the draft, but a webhook or table fires the "
                         "published version, so changes are not live until this is passed.")
    ap.add_argument("--allow-prune", action="store_true",
                    help="permit deleting nodes for legs no longer in the config. Required "
                         "because a renamed leg key is indistinguishable from a removed one.")
    a = ap.parse_args()

    b = Build(a.config)
    b.check_cli()
    b.check_workspace()

    legs = [l for l in b.cfg["legs"] if l.get("provider", {}).get("type") != "none"]
    for l in legs:
        # Two legs may fill the SAME field (primary then fallback). They must not share a
        # need key, or the fallback's gate would be recomputed by the primary's resolve.
        l["need"] = "need_" + l["key"]
    if not legs:
        raise SystemExit("no legs enabled: every leg's provider type is 'none'. "
                         "There is nothing to build.")
    print("legs enabled: %s" % ", ".join(l["key"] for l in legs))

    # Resolve every provider BEFORE creating anything, so a missing binding fails the build
    # up front instead of leaving a half-built graph.
    for l in legs:
        pv = l["provider"]
        if pv["type"] == "clay_function":
            pv["_tableId"] = b.require_function(l["key"], pv["names"])
            print("  %-24s -> function %s" % (l["key"], pv["_tableId"]))
        elif pv["type"] == "clay_action":
            print("  %-24s -> action %s" % (l["key"], pv["actionKey"]))
        elif pv["type"] == "http":
            print("  %-24s -> %s %s  via account %r"
                  % (l["key"], pv.get("method", "POST"), pv["url"], pv["app_account"]))
        else:
            raise SystemExit("leg %s: unknown provider type %r" % (l["key"], pv["type"]))

    validate(b, legs)

    if a.dry_run:
        print("\ndry run: providers resolve and inputs validate. Nothing was created.")
        return

    b.guard_orphan()
    b.warn_duplicate_cascade()
    st = b.state()
    if "workflow_id" not in st["meta"]:
        wf = b.clay("workflows", "create", "--name", b.cfg["workflow_name"])
        b.set_meta(workflow_id=wf["id"], url=wf.get("url"))
        print("created workflow %s" % wf["id"])
    print("workflow %s" % b.wf)
    b.reconcile()

    NEEDS = needs_code(legs)
    verified_statuses = tuple(s.lower() for s in
                              (b.cfg.get("verified_statuses") or ["deliverable", "valid"]))
    capture_prefix = b.cfg.get("capture_prefix") or "person_"
    sentinels = [s.lower() for s in (b.cfg.get("sentinels") or ["n/a", "none", "null"])]

    def code(tpl, **kv):
        s = tpl.replace("__NEEDS__", NEEDS)
        s = (s.replace("__FIELDS__", json.dumps(FIELDS))
              .replace("__FLAGS__", json.dumps(FLAGS))
              .replace("__SENTINELS__", json.dumps(sentinels))
              .replace("__VERIFIED_STATUSES__", repr(verified_statuses))
              .replace("__CAPTURE_PREFIX__", capture_prefix)
              .replace("__ENRICHED__", json.dumps(sorted({l["field"] for l in legs})))
              .replace("__GUARANTEED__", json.dumps(GUARANTEED_OUT)))
        for k, v in kv.items():
            s = s.replace("__%s__" % k, v)
        return s

    def resolve_code(l):
        return code(RESOLVE, FIELD=l["field"], SOURCE=l["source"],
                    PATHS=json.dumps(l["out_paths"]),
                    SKIPKEY=repr(l.get("skip") or ""),
                    WANTKEY=repr(l.get("want") or ""),
                    REQUIRES=json.dumps(l.get("requires") or []),
                    NEED=l["need"], CAPTURE=json.dumps(l.get("capture") or {}))

    # ---- webhook trigger ----------------------------------------------------
    # A Clay TABLE binds to a node (pick "0a Intake" as the starting node) and needs no
    # trigger. A webhook caller does. Build both so either entry point works, and so
    # `graph validate` passes rather than reporting no_trigger_node.
    st = b.state()
    if "trigger_id" not in st["meta"]:
        iface = REQUIRED_IN + OPTIONAL_IN + FLAGS + ["source_ref", "callback_url"]
        props = {f: {"type": "string"} for f in iface}
        t = b.clay("workflows", "triggers", "create", b.wf, inp={
            "triggerType": "webhook",
            # The schema must be COMPLETE. Fields absent from it are stripped at intake, and
            # a bare {"type":"object"} accepts POSTs then dies with the misleading
            # "Workflow has no initial node".
            "inputSchema": {"type": "object", "properties": props,
                            "required": REQUIRED_IN},
        })
        tid = t["resourceId"]
        got = b.clay("workflows", "triggers", "get", tid)
        b.set_meta(trigger_id=tid, trigger_node=got["workflowNodeId"],
                   webhook_url=got["webhookUrl"])
        print("  + trigger %s  %s" % (tid, got["webhookUrl"]))

    # ---- intake -------------------------------------------------------------
    # Per-leg constants that never change during a run live here. Bodies and query strings
    # do NOT: they can reference a field a later leg resolves, so _needs() rebuilds them in
    # every node that emits the record.
    consts = ["    out = _needs(rec)", "    out['_true'] = True"]
    for l in legs:
        pv = l["provider"]
        if pv["type"] != "http":
            continue
        headers = {"Content-Type": "application/json"}
        headers.update(pv.get("headers") or {})
        consts.append("    out['_url_%s'] = %r" % (l["key"], pv["url"]))
        consts.append("    out['_method_%s'] = %r" % (l["key"], pv.get("method", "POST")))
        # Auth is never here. The Clay HTTP API account named in `app_account` injects it.
        consts.append("    out['_headers_%s'] = %r" % (l["key"], headers))
    consts.append("    return out")
    INTAKE_FULL = code(INTAKE).replace("    return _needs(rec)", "\n".join(consts))

    b.ensure_node("intake", {
        "nodeType": "code", "name": "0a Intake", "codeTimeoutMs": 30000,
        "code": NEEDS + INTAKE_FULL,
    })
    # A trigger create mints the trigger node but leaves it UNCONNECTED; wire it explicitly
    # or every run dies with "Workflow has no initial node".
    #
    # Wire intake from EVERY trigger node, not only the webhook this build created. Binding
    # a Clay table to the workflow (done in the UI, invisible to this config) adds its own
    # trigger node; an edge list containing only the webhook node severs that binding on
    # every rebuild. Seen in production: a rebuild disconnected the table trigger and every
    # run died with "Workflow has no initial node" until the edge was restored.
    tnode = b.state()["meta"]["trigger_node"]
    tnodes = [tnode]
    g = b.clay("workflows", "graph", "get", b.wf)
    for t in (g.get("summary") or {}).get("triggers") or []:
        nid = b.clay("workflows", "triggers", "get", t["id"]).get("workflowNodeId")
        if nid and nid not in tnodes:
            tnodes.append(nid)
    if len(tnodes) > 1:
        print("  intake wired from %d trigger nodes" % len(tnodes))
    b.wire("intake",
           code=NEEDS + INTAKE_FULL,
           input_schema={"type": "object", "properties": {
               f: {"type": "string", "sourceNodeId": tnode, "sourcePath": "$." + f}
               for f in REQUIRED_IN + OPTIONAL_IN + FLAGS + ["source_ref", "callback_url"]}},
           edges=[{"sourceNode": n} for n in tnodes])

    # ---- one group per leg --------------------------------------------------
    prev = "intake"
    for i, l in enumerate(legs, 1):
        k, pv = l["key"], l["provider"]
        if pv["type"] == "clay_function":
            tools = [{"toolType": "clay_function", "tableId": pv["_tableId"]}]
        elif pv["type"] == "http":
            tools = [{"toolType": "clay_action", "actionKey": HTTP_ACTION_KEY,
                      "actionPackageId": b.http_package(),
                      "appAccountName": pv["app_account"]}]
        else:
            tools = [{"toolType": "clay_action", "actionKey": pv["actionKey"],
                      "actionPackageId": pv["actionPackageId"]}]

        gate_spec = rules_gate("%d %s gate" % (i, l["field"]), l["need"], l["field"])
        pass_spec = rules_pass("%dp %s looked up" % (i, l["field"]))
        tool_name = "%da %s" % (i, l["tool_name"])
        resolve_name = "%dr %s resolve" % (i, l["field"])

        b.ensure_node(k + "_gate", gate_spec)
        b.ensure_tool_node(k + "_tool", {"nodeType": "tool", "name": tool_name,
                                         "tools": tools})
        b.ensure_node(k + "_pass", pass_spec)
        b.ensure_node(k + "_resolve", {"nodeType": "code", "name": resolve_name,
                                       "codeTimeoutMs": 30000, "code": resolve_code(l)})

        # The gate reads the record from the previous resolve.
        b.wire(k + "_gate", **gate_spec,
               input_schema={"type": "object", "properties": {
                   l["need"]: b.pin(prev, "$." + l["need"], "boolean")}},
               edges=[prev])
        # Tool inputs, by the provider's own parameter names.
        if pv["type"] == "http":
            # `headers` and `queryString` are OBJECT parameters. Pinning a JSON string makes
            # the value vanish silently and the API answers as though nothing was sent.
            props = {
                "url": b.pin("intake", "$._url_" + k),
                "method": b.pin("intake", "$._method_" + k),
                "headers": b.pin("intake", "$._headers_" + k, "object"),
                "returnResponseMetadata": b.pin("intake", "$._true", "boolean"),
            }
            if pv.get("body") or pv.get("body_static"):
                props["body"] = b.pin(prev, "$._body_" + k)
            if pv.get("query") or pv.get("query_static"):
                props["queryString"] = b.pin(prev, "$._query_" + k, "object")
        else:
            props = {pname: b.pin(prev, "$." + rfield)
                     for pname, rfield in (l.get("tool_inputs") or {}).items()}
        b.wire(k + "_tool", tools=tools, name=tool_name,
               input_schema={"type": "object", "properties": props},
               edges=[{"from": k + "_gate", "rule": "rule_need", "name": "look it up"}])
        b.wire(k + "_pass", **pass_spec,
               input_schema={"type": "object", "properties": {"ran": {"type": "boolean"}}},
               edges=[k + "_tool"])
        b.wire(k + "_resolve", name=resolve_name, code=resolve_code(l),
               input_schema={"type": "object", "properties": {
                   "prev": b.pin(prev, "$", "object"),
                   "found": b.pin(k + "_tool", "$.result", "object")}},
               edges=[{"from": k + "_pass", "rule": "rule_found", "name": "found"},
                      {"from": k + "_pass", "rule": "rule_empty", "name": "empty"},
                      {"from": k + "_gate", "rule": "rule_have", "name": "skip"}])
        prev = k + "_resolve"

    # ---- emit ---------------------------------------------------------------
    n = len(legs) + 1
    emit_name = "%d Emit" % n
    b.ensure_node("emit", {"nodeType": "code", "name": emit_name, "codeTimeoutMs": 30000,
                           "code": code(EMIT)})
    b.wire("emit", name=emit_name, code=code(EMIT),
           input_schema={"type": "object", "properties": {"prev": b.pin(prev, "$", "object")}},
           edges=[prev])

    # ---- optional callback --------------------------------------------------
    # Two terminal lanes rather than a join: a record with a callback URL is POSTed, one
    # without finishes at a pass-through. Nothing merges, so nothing can hang waiting for a
    # sibling lane. The destination is whatever the CALLER supplied per record — this build
    # never invents one.
    cb = b.cfg.get("callback")
    cb_enabled = True if cb is None else bool(cb.get("enabled", True))
    expected = {"intake", "emit"}
    if cb_enabled:
        expected |= {"callback_gate", "callback_post", "callback_done"}
        gate_spec = rules_callback("%d Callback gate" % (n + 1))
        b.ensure_node("callback_gate", gate_spec)
        cb_tools = [{"toolType": "clay_action", "actionKey": HTTP_ACTION_KEY,
                     "actionPackageId": b.http_package()}]
        if (cb or {}).get("app_account"):
            cb_tools[0]["appAccountName"] = cb["app_account"]
        post_name = "%da Callback POST" % (n + 1)
        b.ensure_tool_node("callback_post", {"nodeType": "tool", "name": post_name,
                                             "tools": cb_tools})
        done_name = "%db Done" % (n + 1)
        b.ensure_node("callback_done", {"nodeType": "code", "name": done_name,
                                        "codeTimeoutMs": 30000, "code": DONE})
        b.wire("callback_gate", **gate_spec,
               input_schema={"type": "object", "properties": {
                   "has_callback": b.pin("emit", "$.has_callback", "boolean")}},
               edges=["emit"])
        b.wire("callback_post", tools=cb_tools, name=post_name,
               input_schema={"type": "object", "properties": {
                   "url": b.pin("emit", "$.callback_url"),
                   "method": b.pin("emit", "$._method_post"),
                   "headers": b.pin("emit", "$._headers_json", "object"),
                   "body": b.pin("emit", "$.record_json")}},
               edges=[{"from": "callback_gate", "rule": "rule_send", "name": "POST it"}])
        b.wire("callback_done", name=done_name, code=DONE,
               input_schema={"type": "object", "properties": {
                   "prev": b.pin("emit", "$", "object")}},
               edges=[{"from": "callback_gate", "rule": "rule_none", "name": "no callback"}])

    # ---- prune --------------------------------------------------------------
    # Nodes from legs no longer in the config. Without pruning, reconfiguring leaves orphans
    # wired to nothing, which `graph validate` flags and which make the graph unreadable.
    # But a RENAMED leg key looks exactly like a removed one from here, so deleting is
    # gated: this is the only step that destroys anything.
    for l in legs:
        expected |= {l["key"] + s for s in ("_gate", "_tool", "_pass", "_resolve")}
    st = b.state()
    stale = [k for k in st["nodes"] if k not in expected]
    if stale and not a.allow_prune:
        print("\n%d node(s) belong to legs no longer in the config:" % len(stale))
        for k in stale:
            print("  - %-26s %s" % (k, st["nodes"][k]))
        print("They were LEFT IN PLACE. If those legs were removed on purpose, re-run with\n"
              "--allow-prune to delete them. If a leg key was merely RENAMED, fix the config\n"
              "instead: pruning would delete the working node and rebuild it from scratch.")
    elif stale:
        for k in stale:
            b.clay("workflows", "nodes", "delete", b.wf, st["nodes"][k])
            print("  - %-26s pruned" % k)
        st = b.state()
        for k in stale:
            st["nodes"].pop(k, None)
            (st.get("tooltypes") or {}).pop(k, None)
        b.save(st)

    if a.publish:
        b.publish()
    else:
        print("\nNOT PUBLISHED. The graph is a DRAFT: a test run fires the draft, but a\n"
              "webhook or a bound table fires the PUBLISHED version, so this build is not\n"
              "live yet. Re-run with --publish when you are ready for real traffic.")

    print("\ndone. %d nodes. %s"
          % (len(b.state()["nodes"]), b.state()["meta"].get("url") or ""))


if __name__ == "__main__":
    main()
