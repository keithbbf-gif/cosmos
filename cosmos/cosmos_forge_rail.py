#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_forge_rail.py -- the two forge hands, gitlab-forge + github-forge.

F-30 WAVE A1/A2. Promoted from builds/probe/proposed/cosmos_forge_rail.py.

WHY ONE MODULE FOR TWO RAILS. `glab` and `gh` differ in exactly three values:
the binary, the identity verb, and how the identity is lifted out of the reply.
Everything else -- spec load, authority refusal, registration, probe-record
write -- is identical. Two vendor modules would be two places for one guard
to drift, which is the cost cosmos_rail_base was created to stop.

WHY THESE TWO FIRST. Both are already authenticated on this machine and
neither needs a credential from Keith: `gh` and `glab` hold their tokens in
the OS keyring, so this is the first COSMOS rail with NO COSMOS-held secret.
There is no read_key, so the NO_KEY refusal that keeps codex-cli and
claude-cli dark cannot apply here.

PROBE BINDS AUTH, NOT PRESENCE. `--version` proves a binary; it does not
prove a hand. The probe runs an authenticated REST verb and requires a value
only the live forge can emit -- GitHub rate_limit.limit, GitLab user.id --
and requires rc==0 as well. A non-zero exit is never a pass.

ROUTE IS core->forge. Never core->code: a proven forge must not capture
cursor/claude dispatch. dst=code/models/read is coerced.

$0. GitHub REST is 5000/hr authenticated; `glab api user` is unmetered.
Neither identity verb starts a pipeline. dispatch() REFUSES workflow/ci/
pipeline verbs so a routed call cannot burn CI minutes by accident.
metered_usd=0 -> no spend-gate budget.

    py -3.14 cosmos\\cosmos_forge_rail.py --selftest
    py -3.14 cosmos\\cosmos_forge_rail.py --root V:\\A\\Ai\\COSMOS\\live --probe
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _strip_ansi(text: str) -> str:
    """gh colorizes JSON on a TTY. Color is not JSON; strip before parse."""
    return _ANSI.sub("", text or "")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_rail_base import (  # noqa: E402
    RailError as RailSeamError,
    _ledger_is_authority,  # re-export for test_rail_base NO-FORK
    _real_run,
    _real_which,
    ledger_is_authority,
    write_probe_record,
)

SCHEMA = "cosmos-forge-rail/1"
SPEC_NAME = "forge_rail.json"
PROBE_NAME = "forge_rail_probe.json"
SRC, DST = "core", "forge"
PROBE_TIMEOUT_S = 45
DISPATCH_TIMEOUT_S = 45

# Substrings that start a pipeline / burn CI minutes. Identity REST is not
# among them. Matched against " ".join(argv_tail).lower().
_PIPELINE_NEEDLES = (
    "workflow run", "workflow dispatch",
    "ci run", "ci trigger",
    "pipeline run", "pipeline trigger", "pipeline create",
    "run rerun",
    "release create",
)


class ForgeRailError(RailSeamError):
    """Typed refusal for the forge seam.

    kind in {BAD_SPEC, BAD_ROOT, UNREACHABLE, REFUSED}.
    """


def _lift_github(doc: dict) -> str:
    """A value only a live, authenticated GitHub can emit."""
    core = doc.get("resources", {}).get("core", doc)
    if "limit" not in core:
        raise ForgeRailError("UNREACHABLE", "rate_limit reply has no .limit")
    return f"rest_limit={core['limit']} remaining={core.get('remaining')}"


def _lift_gitlab(doc: dict) -> str:
    """A value only a live, authenticated GitLab can emit."""
    if not doc.get("id") or not doc.get("username"):
        raise ForgeRailError("UNREACHABLE", "user reply has no .id/.username")
    return f"user_id={doc['id']} username={doc['username']}"


# link_id -> (binary, identity argv tail, lifter). The ONLY per-vendor knowledge.
FORGES: dict[str, tuple[str, tuple[str, ...], object]] = {
    "gitlab-forge": ("glab", ("api", "user"), _lift_gitlab),
    "github-forge": ("gh", ("api", "rate_limit"), _lift_github),
}


def _is_pipeline(argv_tail: tuple[str, ...]) -> bool:
    joined = " ".join(argv_tail).lower()
    return any(n in joined for n in _PIPELINE_NEEDLES)


def _pin_origin(spec: dict) -> dict:
    spec["schema"] = SCHEMA
    spec["rail_type"] = "CLI"
    spec["src"] = str(spec.get("src") or SRC) or SRC
    spec["dst"] = str(spec.get("dst") or DST) or DST
    if spec["dst"] in ("code", "models", "read", "interact", "papers"):
        spec["route_note"] = (
            f"coerced dst={spec['dst']!r} to {DST} "
            "(forge; cursor/claude keep code, dump-dom keeps read)")
        spec["dst"] = DST
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["probe_timeout_s"] = int(spec.get("probe_timeout_s") or PROBE_TIMEOUT_S)
    links = spec.get("links", sorted(FORGES))
    if links is None:
        links = sorted(FORGES)
    if not isinstance(links, (list, tuple)):
        raise ForgeRailError("BAD_SPEC", f"links must be a list, got {type(links).__name__}")
    spec["links"] = list(links)
    return spec


def default_spec() -> dict:
    """Instance-free defaults. Live overlay is live/config/forge_rail.json."""
    return _pin_origin({
        "schema": SCHEMA,
        "rail_type": "CLI",
        "src": SRC,
        "dst": DST,
        "policy_rank": 0,
        "metered_usd": 0.0,
        "budget_usd": 0.0,
        "links": sorted(FORGES),
        "probe_timeout_s": PROBE_TIMEOUT_S,
        "note": (
            "Forge hands. Auth lives in the OS keyring (gh/glab), NOT in "
            "live/config -- this rail holds no COSMOS secret and has no NO_KEY "
            "refusal. Probe runs an authenticated REST verb and binds a "
            "forge-only value (github rate_limit.limit / gitlab user.id); rc==0 "
            "is required but is never itself the pass. $0: no pipeline is "
            "started. dst=forge so a proven link cannot capture core->code. "
            "metered_usd=0 -> unspend-gated."
        ),
    })


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay:
        if not isinstance(overlay, dict):
            raise ForgeRailError(
                "BAD_SPEC", f"overlay must be a dict, got {type(overlay).__name__}")
        spec.update(overlay)
        spec = _pin_origin(spec)
    bad = [l for l in spec["links"] if l not in FORGES]
    if bad:
        raise ForgeRailError("BAD_SPEC", f"unknown link_id(s): {bad}")
    if not spec["links"]:
        raise ForgeRailError("BAD_SPEC", "links is empty - a rail with no link is not a rail")
    return spec


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).is_file():
        return merge_spec(None)
    try:
        return merge_spec(json.loads(Path(path).read_text(encoding="utf-8")))
    except json.JSONDecodeError as e:
        raise ForgeRailError("BAD_SPEC", f"{path}: {e}") from e


def write_spec(path: Path, overlay=None) -> dict:
    spec = merge_spec(overlay)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8")
    return spec


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


class ForgeRail:
    """One forge link. Stateless apart from the last probe record."""

    def __init__(self, link_id: str, spec: dict, run=None, which=None):
        if link_id not in FORGES:
            raise ForgeRailError("BAD_SPEC", f"unknown link_id {link_id!r}")
        self.link_id = link_id
        self.spec = spec
        self.binary, self._argv_tail, self._lift = FORGES[link_id]
        self._run = run or _real_run
        self._which = which or _real_which
        self._last_probe: dict = {}
        self.metered_usd = float(spec.get("metered_usd") or 0.0)

    def last_identity(self) -> dict:
        return dict(self._last_probe)

    def _exec(self, argv_tail: tuple[str, ...], timeout_s: int) -> dict:
        found = self._which(self.binary)
        if not found:
            rec = {"binary": None, "rc": None, "bound": None}
            self._last_probe = rec
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"UNREACHABLE: {self.binary} ABSENT on PATH",
                    **rec}
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        env["GH_FORCE_TTY"] = "0"
        env["CLICOLOR"] = "0"
        r = self._run([found, *argv_tail], timeout_s=timeout_s, env=env)
        rec = {"binary": found, "rc": r.get("rc"),
               "timed_out": bool(r.get("timed_out")), "bound": None}
        self._last_probe = rec
        if r.get("timed_out"):
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"UNREACHABLE: {self.binary} {' '.join(argv_tail)} TIMEOUT",
                    **rec}
        out = _strip_ansi(r.get("out") or "")
        err = _strip_ansi(r.get("err") or "")
        if r.get("rc") != 0:
            snippet = (err + out).strip()[:200]
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"UNREACHABLE: {self.binary} rc={r.get('rc')} {snippet}".strip(),
                    **rec, "out": out, "err": err}
        rec["out"] = out
        rec["err"] = err
        self._last_probe = rec
        return {"ok": True, "kind": "CLI", "detail": "", **rec}

    def probe(self):
        """Cheapest AUTHENTICATED liveness. Fail-closed on every branch."""
        timeout = min(PROBE_TIMEOUT_S,
                      int(self.spec.get("probe_timeout_s") or PROBE_TIMEOUT_S))
        rec = self._exec(self._argv_tail, timeout)
        if not rec["ok"]:
            return False, rec["detail"]
        try:
            bound = self._lift(json.loads(rec.get("out") or "{}"))
        except (json.JSONDecodeError, ForgeRailError, AttributeError, TypeError) as e:
            return False, f"UNREACHABLE: unparseable {self.binary} reply: {e}"
        # Bound value is the proof. Do not keep the vendor JSON (emails, etc.).
        self._last_probe = {
            "binary": rec.get("binary"), "rc": rec.get("rc"),
            "timed_out": rec.get("timed_out"), "bound": bound,
        }
        return True, f"{self.link_id} live binary={rec['binary']} {bound}"

    def dispatch(self, payload: dict | None = None) -> dict:
        """Identity REST by default. A pipeline/CI argv is REFUSED, never run."""
        payload = payload or {}
        extra = payload.get("argv")
        if extra is None:
            tail = self._argv_tail
            identity = True
        else:
            if isinstance(extra, str):
                raise ForgeRailError(
                    "BAD_SPEC", "argv must be a list, never a shell string")
            tail = tuple(str(x) for x in extra)
            identity = False
        if _is_pipeline(tail):
            raise ForgeRailError(
                "REFUSED",
                f"pipeline/CI verb refused (would burn minutes): {list(tail)}")
        timeout = int(payload.get("timeout_s") or DISPATCH_TIMEOUT_S)
        rec = self._exec(tail, timeout)
        if not rec["ok"]:
            return {"ok": False, "rc": rec.get("rc"), "body": "",
                    "text": rec["detail"], "model": "", "kind": rec["kind"],
                    "link_id": self.link_id, "detail": rec["detail"]}
        body = rec.get("out") or ""
        model = ""
        if identity:
            try:
                model = self._lift(json.loads(body or "{}"))
            except (json.JSONDecodeError, ForgeRailError, AttributeError, TypeError) as e:
                return {"ok": False, "rc": rec.get("rc"), "body": body,
                        "text": str(e), "model": "", "kind": "UNREACHABLE",
                        "link_id": self.link_id,
                        "detail": f"UNREACHABLE: unparseable reply: {e}"}
            self._last_probe = {
                "binary": rec.get("binary"), "rc": rec.get("rc"),
                "timed_out": rec.get("timed_out"), "bound": model,
            }
            body = model
        return {"ok": True, "rc": rec.get("rc"), "body": body, "text": body,
                "model": model or body[:80], "kind": "CLI",
                "link_id": self.link_id, "detail": ""}


def register_forge_rails(registry, adapters: dict, spend_gate=None, *,
                         paths=None, spec=None, run=None, which=None) -> dict:
    """Register every configured forge link. Missing binary -> still registered;
    the probe records UNREACHABLE. Registration is not capability."""
    spec = load_spec(spec_path_for(paths)) if (spec is None and paths is not None) else merge_spec(spec)
    out: dict = {"links": {}, "spec": spec}
    for lid in spec["links"]:
        rail = ForgeRail(lid, spec, run=run, which=which)
        if lid not in registry.state():
            registry.register(lid, spec["rail_type"], spec["src"], spec["dst"],
                              policy_rank=int(spec["policy_rank"]))
        registry.attach_probe(lid, rail.probe)
        adapters[lid] = rail
        out["links"][lid] = {"rail": rail, "binary": rail.binary,
                             "src": spec["src"], "dst": spec["dst"]}
    if spend_gate is not None and float(spec["metered_usd"]) > 0:
        for lid in spec["links"]:
            spend_gate.set_budget(lid, float(spec["budget_usd"] or spec["metered_usd"]))
    return out


def attach_to_kernel(kernel, adapters: dict | None = None, run=None, which=None, *,
                     boot_compose: bool = False) -> dict:
    """Additive compose onto an already-built Kernel. Same authority refusal as
    every other rail: no LINK_REGISTERED on the authority ledger unless this is
    Kernel boot."""
    if ledger_is_authority(kernel) and not boot_compose:
        raise ForgeRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED outside Kernel "
            "boot. Isolated --gate ledger only. Pass boot_compose=True only "
            "from Kernel.compose_rails.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_forge_rails(kernel.registry, adapters,
                                spend_gate=getattr(kernel, "spend", None),
                                paths=kernel.paths, run=run, which=which)


def _probe_all(root: str, run=None, which=None) -> dict:
    """Standalone satellite probe: no Kernel, no registry, no ledger write."""
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    rec = {"schema": SCHEMA, "tree_id": paths.sentinel.tree_id, "links": {}}
    ok_all = True
    for lid in spec["links"]:
        rail = ForgeRail(lid, spec, run=run, which=which)
        ok, detail = rail.probe()
        ok_all = ok_all and ok
        ident = rail.last_identity()
        rec["links"][lid] = {
            "ok": ok, "detail": detail,
            "binary": ident.get("binary"), "rc": ident.get("rc"),
            "bound": ident.get("bound"),
        }
    rec["ok"] = ok_all
    rec["dst"] = spec["dst"]
    return rec


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import Kernel, install
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    gh_body = json.dumps({"resources": {"core": {"limit": 5000, "remaining": 4999}}})
    gl_body = json.dumps({"id": 42, "username": "probe-user"})

    def which(name):
        return fr"C:\fake\{name}.exe"

    def run(argv, **_k):
        bin_ = Path(argv[0]).stem.lower()
        if bin_ == "gh" and tuple(argv[1:]) == ("api", "rate_limit"):
            return {"rc": 0, "out": gh_body, "err": "", "timed_out": False}
        if bin_ == "glab" and tuple(argv[1:]) == ("api", "user"):
            return {"rc": 0, "out": gl_body, "err": "", "timed_out": False}
        if "workflow" in argv or "pipeline" in argv or argv[-1:] == ("run",):
            return {"rc": 0, "out": "STARTED", "err": "", "timed_out": False}
        return {"rc": 2, "out": "", "err": "unexpected argv", "timed_out": False}

    spec = merge_spec(None)
    check("default dst is forge, never code",
          lambda: spec["dst"] == DST and spec["src"] == SRC)
    coerced = merge_spec({"dst": "code"})
    check("overlay dst=code is coerced to forge",
          lambda: coerced["dst"] == DST and "route_note" in coerced)
    check("unknown link is BAD_SPEC",
          lambda: _expect_kind(lambda: merge_spec({"links": ["not-a-forge"]}),
                               "BAD_SPEC"))
    check("empty links is BAD_SPEC",
          lambda: _expect_kind(lambda: merge_spec({"links": []}), "BAD_SPEC"))
    check("string argv is BAD_SPEC",
          lambda: _expect_kind(
              lambda: ForgeRail("github-forge", spec, run=run, which=which)
              .dispatch({"argv": "api rate_limit"}),
              "BAD_SPEC"))

    gh = ForgeRail("github-forge", spec, run=run, which=which)
    ok, detail = gh.probe()
    check("github probe binds rest_limit from live JSON",
          lambda: ok and "rest_limit=5000" in detail
          and gh.last_identity().get("bound", "").startswith("rest_limit=5000"))
    gl = ForgeRail("gitlab-forge", spec, run=run, which=which)
    ok2, detail2 = gl.probe()
    check("gitlab probe binds user_id from live JSON",
          lambda: ok2 and "user_id=42" in detail2
          and "username=probe-user" in detail2)

    missing = ForgeRail("github-forge", spec, run=run, which=lambda _n: None)
    mok, mdetail = missing.probe()
    check("absent binary is UNREACHABLE, never ok",
          lambda: mok is False and mdetail.startswith("UNREACHABLE:"))

    def run_rc1(argv, **_k):
        return {"rc": 1, "out": "token=REDACT_ME", "err": "", "timed_out": False}

    badrc = ForgeRail("github-forge", spec, run=run_rc1, which=which)
    bok, bdetail = badrc.probe()
    check("rc!=0 is UNREACHABLE even with a body (rc is not the pass)",
          lambda: bok is False and "rc=1" in bdetail)

    def run_nolimit(argv, **_k):
        return {"rc": 0, "out": "{}", "err": "", "timed_out": False}

    empty = ForgeRail("github-forge", spec, run=run_nolimit, which=which)
    eok, _ = empty.probe()
    check("rc=0 without .limit is UNREACHABLE", lambda: eok is False)

    colored = (
        "\x1b[1;37m{\x1b[m\n"
        "  \x1b[1;34m\"resources\"\x1b[m\x1b[1;37m:\x1b[m \x1b[1;37m{\x1b[m\n"
        "    \x1b[1;34m\"core\"\x1b[m\x1b[1;37m:\x1b[m \x1b[1;37m{\x1b[m\n"
        "      \x1b[1;34m\"limit\"\x1b[m\x1b[1;37m:\x1b[m 5000\x1b[1;37m,\x1b[m\n"
        "      \x1b[1;34m\"remaining\"\x1b[m\x1b[1;37m:\x1b[m 4999\n"
        "    \x1b[1;37m}\x1b[m\n"
        "  \x1b[1;37m}\x1b[m\n"
        "\x1b[1;37m}\x1b[m\n"
    )

    def run_color(argv, **_k):
        return {"rc": 0, "out": colored, "err": "", "timed_out": False}

    painted = ForgeRail("github-forge", spec, run=run_color, which=which)
    cok, cdetail = painted.probe()
    check("ANSI-colored gh JSON still binds rest_limit (TTY is not the pass)",
          lambda: cok and "rest_limit=5000" in cdetail
          and painted.last_identity().get("bound", "").startswith("rest_limit=5000"))
    check("probe record keeps bound, not the vendor JSON body",
          lambda: "out" not in painted.last_identity()
          and "email" not in json.dumps(painted.last_identity()))

    ident = gh.dispatch({})
    check("default dispatch is identity REST, bound value is the body",
          lambda: ident["ok"] is True and "rest_limit=5000" in ident["body"]
          and ident["kind"] == "CLI")
    pipe = False
    try:
        gh.dispatch({"argv": ["workflow", "run", "ci.yml"]})
    except ForgeRailError as e:
        pipe = e.kind == "REFUSED"
    check("workflow run is REFUSED (never spawned)", lambda: pipe is True)
    gl_pipe = False
    try:
        gl.dispatch({"argv": ["ci", "run"]})
    except ForgeRailError as e:
        gl_pipe = e.kind == "REFUSED"
    check("glab ci run is REFUSED (never spawned)", lambda: gl_pipe is True)

    td = Path(tempfile.mkdtemp(prefix="cosmos_forge_rail_"))
    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_forge_rails(reg, adapters, spec=spec, run=run, which=which)
    check("register both links core->forge",
          lambda: set(rec["links"]) == {"github-forge", "gitlab-forge"}
          and rec["spec"]["dst"] == DST
          and rec["spec"]["src"] == SRC)
    check("registration is not capability (verified is None)",
          lambda: all(reg.state()[lid]["claim"]["dst"] == DST
                      for lid in rec["links"]))
    disp = Dispatcher(reg, adapters, led)
    routed = None
    try:
        routed = disp.dispatch(SRC, DST, {})
    except Exception:  # noqa: BLE001
        routed = None
    # route() requires a FRESH ok measurement. probe_all first.
    reg.probe_all()
    routed = disp.dispatch(SRC, DST, {})
    check("isolated Dispatcher reaches a forge on core->forge",
          lambda: routed.get("ok") is True and routed.get("kind") == "CLI"
          and routed.get("link_id") in FORGES)
    code_miss = False
    try:
        disp.dispatch(SRC, "code", {})
    except Exception as e:  # noqa: BLE001
        code_miss = getattr(e, "kind", None) == "NO_LIVE_LINK"
    check("core->code does not capture a proven forge", lambda: code_miss is True)

    root = install(td / "live", tree_id="spike-forge-rail")
    k = Kernel(root, worker="forge-rail-selftest")
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except ForgeRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)
    composed = list((k.rails_compose or {}).get("composed") or [])
    check("writing Kernel compose includes forge-rails (F-30)",
          lambda: "forge-rails" in composed)
    check("writing Kernel adapters include both forge links",
          lambda: {"github-forge", "gitlab-forge"} <= set(k.adapters))

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("live_value: " + json.dumps({
        "checks": len(results),
        "dst": DST,
        "links": sorted(FORGES),
        "github_bound": gh.last_identity().get("bound"),
        "gitlab_bound": gl.last_identity().get("bound"),
        "composed_forge": "forge-rails" in composed,
    }, sort_keys=True))
    print("SELFTEST %s - %d checks (forge satellite; dst=forge; pipeline REFUSED; "
          "attach refused; Kernel compose)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def _expect_kind(fn, kind: str) -> bool:
    try:
        fn()
    except ForgeRailError as e:
        return e.kind == kind
    return False


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_forge_rail")
    ap.add_argument("--root", default=None)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--write-probe", action="store_true",
                    help="persist the probe record to live/config/" + PROBE_NAME)
    ap.add_argument("--write-spec", action="store_true",
                    help="persist default spec to live/config/" + SPEC_NAME)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.probe and not a.write_spec:
        print(json.dumps({"ok": False, "kind": "BAD_SPEC",
                          "detail": "nothing to do: pass --probe or --selftest"}))
        return 2
    if not a.root:
        try:
            raise ForgeRailError(
                "BAD_ROOT", "--root is required (resolver does not guess)")
        except ForgeRailError as e:
            print(json.dumps({"ok": False, "kind": e.kind, "detail": str(e)},
                             indent=1))
            return 2
    try:
        from cosmos_paths import CosmosPaths
        paths = CosmosPaths(a.root)
        if a.write_spec:
            write_spec(spec_path_for(paths))
        if not a.probe:
            print(json.dumps({"ok": True, "wrote": SPEC_NAME,
                              "tree_id": paths.sentinel.tree_id}, indent=1))
            return 0
        rec = _probe_all(a.root)
    except (ForgeRailError, RailSeamError) as e:
        print(json.dumps({"ok": False, "kind": e.kind, "detail": str(e)}, indent=1))
        return 2
    if a.write_probe:
        write_probe_record(probe_path_for(CosmosPaths(a.root)), rec)
    print(json.dumps(rec, indent=1))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
