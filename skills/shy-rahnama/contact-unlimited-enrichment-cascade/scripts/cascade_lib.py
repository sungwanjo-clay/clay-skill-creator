"""
Build helpers for the contact enrichment cascade.

Two things make the build portable across workspaces, and both matter more than they look:

  * Provider bindings resolve by NAME at run time. A Clay function's id is workspace-local,
    so a hardcoded id makes a build that only works in the workspace it was written in.
  * Nothing about the machine is assumed. The Clay credential comes from the ambient
    `clay login`, or from a config-supplied config dir when one workspace needs isolating
    from another.

Credential rule, and it is absolute: this module never reads, holds, or writes an API key.
A provider's key lives in a Clay HTTP API account that the installer creates, and a tool
node references that account BY NAME (`appAccountName`). Clay injects the auth header
server-side. There is deliberately no code path that puts a key into node source, because
node source is stored by Clay and visible to anyone who can open the workflow.

Resumability contract: every created node id is written to build-state.json the moment the
create succeeds, so an interrupted build re-runs as a no-op over what already exists and
creates only the gap. Nothing that would be lost is held in memory.
"""
import json
import os
import subprocess

# Clay's built-in generic HTTP action — the adapter every flat-rate provider is called
# through. Its package id is resolved from the LIVE catalogue at build time and deliberately
# not pinned here: an id written into source is an environment assumption nobody can see, and
# if the catalogue cannot be read the honest outcome is to stop rather than to build a graph
# against a guess.
HTTP_ACTION_KEY = "http-api-v2"

MIN_CLI = (0, 17, 0)


class Build:
    def __init__(self, config_path):
        self.cfg = json.load(open(config_path))
        self.dir = os.path.dirname(os.path.abspath(config_path))
        self.state_path = os.path.join(self.dir, "build-state.json")
        self.env = dict(os.environ)
        # Optional. Present only when this workspace's Clay credential is deliberately
        # kept separate from the default login; absent means use the ambient one.
        if self.cfg.get("clay_config_home"):
            self.env["XDG_CONFIG_HOME"] = self.cfg["clay_config_home"]
        self._fn_cache = None
        self._http_pkg = None

    # ---------- clay CLI ----------

    def clay(self, *args, inp=None):
        cmd = ["clay", *args]
        if inp is not None:
            cmd += ["--input", json.dumps(inp) if not isinstance(inp, str) else inp]
        r = subprocess.run(cmd, capture_output=True, text=True, env=self.env)
        if r.returncode != 0:
            raise SystemExit("clay %s failed (%s):\n%s"
                             % (" ".join(args), r.returncode, r.stderr or r.stdout))
        try:
            return json.loads(r.stdout or "{}")
        except json.JSONDecodeError:
            return {"raw": r.stdout}

    def paged(self, *args, limit=100):
        """Walk every page of a list command.

        A single page is the wrong default for anything a name resolves against: a
        workspace with more functions than one page would fail to find a provider that is
        right there, and the error would name the wrong cause. Page caps differ per
        command, so the caller states the limit."""
        rows, cursor, seen = [], None, 0
        while True:
            call = list(args) + ["--limit", str(limit)]
            if cursor:
                call += ["--cursor", cursor]
            d = self.clay(*call)
            rows.extend(d.get("data") or [])
            cursor = d.get("cursor")
            seen += 1
            if not cursor or seen > 50:
                return rows

    def check_cli(self):
        """Report the platform and stop. Never install, upgrade, or fetch anything to
        repair it — an environment the installer has to fix is not this build's job, and a
        script that starts rebuilding its own prerequisites reads as a hang."""
        r = subprocess.run(["clay", "--version"], capture_output=True, text=True, env=self.env)
        if r.returncode != 0:
            raise SystemExit(
                "The `clay` CLI is not on PATH.\n"
                "Install the Clay plugin and run its `setup` skill, then re-run this build.")
        raw = (r.stdout or "").strip()
        try:
            got = tuple(int(x) for x in raw.split("+")[0].split(".")[:3])
        except ValueError:
            print("clay %s (could not parse a version; continuing)" % raw)
            return
        if got < MIN_CLI:
            raise SystemExit(
                "clay %s is below the minimum this build needs (%s).\n"
                "Fix: run `clay update`, then re-run this build."
                % (raw, ".".join(str(x) for x in MIN_CLI)))
        print("clay %s" % raw)

    def check_workspace(self):
        """Refuse to build into the wrong workspace. When a config dir is what separates
        two Clay accounts, it is the only thing standing between them — so verify it rather
        than trusting it."""
        who = self.clay("whoami")
        got = str((who.get("workspace") or {}).get("id"))
        want = str(self.cfg["workspace_id"])
        if got != want:
            where = self.cfg.get("clay_config_home") or "the ambient clay login"
            raise SystemExit(
                "WORKSPACE MISMATCH: %s resolves to workspace %s, the config expects %s.\n"
                "Refusing to build. Sign in to the right workspace and re-run."
                % (where, got, want))
        print("workspace %s verified" % got)

    # ---------- state ----------

    def state(self):
        if os.path.exists(self.state_path):
            return json.load(open(self.state_path))
        return {"nodes": {}, "meta": {}}

    def save(self, st):
        tmp = self.state_path + ".tmp"
        json.dump(st, open(tmp, "w"), indent=1, sort_keys=True)
        os.replace(tmp, self.state_path)

    def set_meta(self, **kv):
        st = self.state()
        st["meta"].update(kv)
        self.save(st)

    @property
    def wf(self):
        return self.state()["meta"]["workflow_id"]

    def guard_orphan(self):
        """If state has no workflow but one already carries this config's name, STOP.

        build-state.json is the only record of which Clay node is which. Without it the
        build cannot tell an existing graph's nodes apart, so creating a second workflow
        would silently orphan the first — which is still live and still billing. Refusing
        and saying why beats either guess."""
        if "workflow_id" in self.state()["meta"]:
            return
        name = str(self.cfg["workflow_name"]).strip().lower()
        for w in self.paged("workflows", "list", limit=200):
            if str(w.get("name", "")).strip().lower() == name:
                raise SystemExit(
                    "A workflow named %r already exists (%s) but build-state.json is missing,\n"
                    "so this build cannot tell which node is which.\n"
                    "Either restore build-state.json beside this config, or rename/delete that\n"
                    "workflow in Clay and re-run to build fresh. Refusing to create a second one."
                    % (self.cfg["workflow_name"], w.get("id")))

    def warn_duplicate_cascade(self):
        """Warn when this workspace already holds a cascade built by this skill.

        `guard_orphan` only catches a workflow with the SAME NAME as this config. Two configs
        in two directories, named differently, each legitimately create their own workflow —
        which is how a workspace ends up with two near-identical cascades, both with live
        webhooks, and nobody noticing. Seen in a real run.

        Recognition is by the skill's OWN emitted node names, not the author's: every graph
        this build produces has a node called `0a Intake` and one ending in ` Emit`. That is a
        shape we define, so it is portable by construction.

        This WARNS rather than refuses: a second cascade is a legitimate thing to want, and
        the build cannot tell a deliberate one from an accident. Refusing would block a real
        use; saying nothing is how the accident happened."""
        mine = self.state()["meta"].get("workflow_id")
        others = []
        for w in self.paged("workflows", "list", limit=200):
            if w.get("id") == mine:
                continue
            try:
                g = self.clay("workflows", "graph", "get", w["id"])
            except SystemExit:
                continue
            names = [n.get("name", "") for n in (g.get("summary") or {}).get("nodes") or []]
            if any(n == "0a Intake" for n in names) and any(n.endswith(" Emit") for n in names):
                others.append((w["id"], w.get("name")))
        if others:
            print("\nNOTE: this workspace already has %d cascade(s) built by this skill:"
                  % len(others))
            for wid, nm in others:
                print("  %s  %s" % (wid, nm))
            print("Building another is fine if you meant to. If you did not, stop now and point\n"
                  "this config at the existing one instead — two cascades both carrying live\n"
                  "webhooks is a thing nobody notices until both are running.\n")

    def reconcile(self):
        """Drop state entries whose node no longer exists in Clay.

        A node deleted in the UI leaves a stale id in state; the next run would then try to
        update an id that resolves to nothing and die on the first write. One graph read
        makes the build self-healing instead."""
        st = self.state()
        if "workflow_id" not in st["meta"] or not st["nodes"]:
            return
        g = self.clay("workflows", "graph", "get", self.wf)
        live = {n["id"] for n in (g.get("summary") or {}).get("nodes") or []}
        gone = [k for k, nid in st["nodes"].items() if nid not in live]
        if not gone:
            return
        for k in gone:
            st["nodes"].pop(k, None)
            (st.get("tooltypes") or {}).pop(k, None)
            print("  ! %-26s missing in Clay; will be recreated" % k)
        self.save(st)

    # ---------- provider resolution ----------

    def functions(self):
        if self._fn_cache is None:
            # 100 is this command's per-page cap.
            self._fn_cache = self.paged("functions", "list", limit=100)
        return self._fn_cache

    def http_package(self):
        """Resolve the generic HTTP action's package id from the live catalogue.

        Matching an action by key alone is not safe in general — the same key can appear in
        more than one package — but the reverse failure is worse here: a package id pinned in
        source is an environment assumption nobody can see, and wrong in any workspace that
        does not match the one it was written in. So read it, and stop if it is not there."""
        if self._http_pkg:
            return self._http_pkg
        for a in self.clay("workflows", "actions", "list").get("data") or []:
            if a.get("actionKey") == HTTP_ACTION_KEY and a.get("actionPackageId"):
                self._http_pkg = a["actionPackageId"]
                return self._http_pkg
        raise SystemExit(
            "Could not resolve the generic HTTP action (%r) in this workspace's action\n"
            "catalogue, so an http leg cannot be built. Check `clay workflows actions list`.\n"
            "Refusing to guess at a package id." % HTTP_ACTION_KEY)

    def resolve_function(self, names):
        """Resolve the first matching workspace function by NAME (case-insensitive).

        `names` is an ordered preference list, so a config can say "use the native cascade,
        and fall back to this workspace's own function". Returns None when none match — the
        caller decides whether that disables a leg or fails the build."""
        if isinstance(names, str):
            names = [names]
        have = {str(f.get("name", "")).strip().lower(): (f.get("id") or f.get("functionId"))
                for f in self.functions()}
        for n in names:
            fid = have.get(str(n).strip().lower())
            if fid:
                return fid
        return None

    def require_function(self, leg, names):
        fid = self.resolve_function(names)
        if not fid:
            avail = sorted(str(f.get("name")) for f in self.functions())
            raise SystemExit(
                "Leg '%s' wants one of %s but this workspace has none of them.\n"
                "Available functions:\n  %s\n"
                "Either bind one in Clay, point the leg at a different provider in the "
                "config, or switch the leg off." % (leg, names, "\n  ".join(avail)))
        return fid

    # ---------- nodes ----------

    def ensure_node(self, key, spec):
        """Create the node if this key has no id yet; persist the id immediately.
        Idempotent — re-running the build never duplicates a node."""
        st = self.state()
        if key in st["nodes"]:
            return st["nodes"][key]
        out = self.clay("workflows", "nodes", "create", self.wf, inp=spec)
        nid = out.get("nodeId")
        if not nid:
            raise SystemExit("create %s returned no nodeId: %s" % (key, out))
        st = self.state()          # re-read: the create may have taken time
        st["nodes"][key] = nid
        self.save(st)
        print("  + %-26s %s  %s" % (key, nid, spec.get("name", "")))
        return nid

    def ensure_tool_node(self, key, spec):
        """Like ensure_node, but recreates the node when the toolType changed.

        Clay rejects changing a tool node's toolType in place ("Delete this node and create
        a new one"), so swapping a leg from a Clay function to a direct HTTP call — exactly
        what adding a flat-rate provider involves — needs a recreate, not an update. Edges
        are rewired by the caller immediately afterwards.

        The live node cannot be trusted to report its own type: `nodes get` reads `tools`
        back as null on clay_function nodes, which made every rebuild delete and recreate
        them. So the toolType each node was created with is recorded in build-state and
        preferred over the live read; the live read remains the fallback for state written
        before this record existed.
        """
        st = self.state()
        want = (spec.get("tools") or [{}])[0].get("toolType")
        if key in st["nodes"]:
            have = (st.get("tooltypes") or {}).get(key)
            if have is None:
                node = self.clay("workflows", "nodes", "get", self.wf, st["nodes"][key])["node"]
                have = ((node.get("tools") or [{}])[0] or {}).get("toolType")
            if have == want:
                return st["nodes"][key]
            self.clay("workflows", "nodes", "delete", self.wf, st["nodes"][key])
            st = self.state()
            st["nodes"].pop(key, None)
            (st.get("tooltypes") or {}).pop(key, None)
            self.save(st)
            print("  ! %-26s recreated (%s -> %s)" % (key, have, want))
        nid = self.ensure_node(key, spec)
        st = self.state()
        st.setdefault("tooltypes", {})[key] = want
        self.save(st)
        return nid

    def pin(self, source_key, path, typ="string"):
        """One pinned inputSchema property. Every input must carry its pin on EVERY schema
        write — a partial send silently destroys the omitted bindings."""
        st = self.state()
        return {"type": typ, "sourceNodeId": st["nodes"][source_key], "sourcePath": path}

    def wire(self, key, input_schema=None, edges=None, **fields):
        """Apply pins and/or parents to an existing node, then READ IT BACK.

        Reads back because a schema write rebuilds the binding map from exactly what the
        call contains: it can report success and still have destroyed the pins the call
        omitted. The success echo is not proof."""
        st = self.state()
        nid = st["nodes"][key]
        payload = dict(fields)
        if input_schema is not None:
            payload["inputSchema"] = input_schema
        if edges is not None:
            # An edge is either a plain node key, or a dict for a conditional branch:
            #   {"from": key, "rule": "rule_id", "name": "label"} -> that rule's lane
            #   {"from": key, "default": True}                    -> the fall-through lane
            # A plain edge out of a conditional silently becomes an unrouted lane.
            out = []
            for e in edges:
                if isinstance(e, str):
                    out.append({"sourceNode": st["nodes"][e]})
                    continue
                if "sourceNode" in e:          # raw node id, e.g. a trigger node
                    out.append(dict(e))
                    continue
                ed = {"sourceNode": st["nodes"][e["from"]]}
                if e.get("default"):
                    ed["isDefaultRoute"] = True
                else:
                    ed["ruleId"] = e["rule"]
                    if e.get("name"):
                        ed["ruleName"] = e["name"]
                out.append(ed)
            payload["incomingEdges"] = out
        self.clay("workflows", "nodes", "update", self.wf, nid, inp=payload)
        back = self.clay("workflows", "nodes", "get", self.wf, nid)["node"]
        if input_schema is not None:
            want = {k for k, v in input_schema.get("properties", {}).items()
                    if "sourceNodeId" in v}
            got = {k for k, v in ((back.get("inputSchema") or {}).get("properties") or {}).items()
                   if v.get("sourceNodeId")}
            lost = want - got
            if lost:
                raise SystemExit("PINS LOST on %s: %s — re-send every pin on every write"
                                 % (key, sorted(lost)))
        print("  ~ %-26s wired" % key)
        return back

    def publish(self):
        self.clay("workflows", "publish", self.wf)
        print("published %s" % self.wf)
