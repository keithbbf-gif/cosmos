#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_rails_wired - F-24 (four answering rails now have a prove() path) and
F-25 (the projection applies a freshness filter), pinned together because they
are one bug seen twice: a rail nobody asks looks identical to a rail whose
answer is three days old, and BOTH read as a confident registry.

Isolated. No network, no spend: every rail call is injected. The two live
satellites are driven through their OWN modules' injection seams
(`http=` for the REST rails, `client_factory=` for the MCP rail), so what is
under test is the real derivation code and not a second implementation of it.

    py -3.14 cosmos\\test_rails_wired.py

Written 2026-08-31 with the F-24/F-25 slice. Belongs beside the other suites in
tests/; it lives here because that slice's fence was cosmos/ only.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cosmos_cursor_rail                                        # noqa: E402
import cosmos_firecrawl_rail                                     # noqa: E402
import cosmos_playwright_rail                                    # noqa: E402
import cosmos_rails_prober as P                                  # noqa: E402
import cosmos_registry                                           # noqa: E402
from cosmos_kernel import install                                # noqa: E402
from cosmos_ledger import Ledger                                 # noqa: E402
from cosmos_paths import CosmosPaths                             # noqa: E402
from cosmos_registry import Registry                             # noqa: E402

# Read defensively so the suite still RUNS against a registry that has no such
# constant: a test that dies on import fails on everything and proves nothing
# about the defect. The pinned-equality check below is what asserts it exists.
PROOF_TTL_S = getattr(cosmos_registry, "PROOF_TTL_S", P.NODE_PROOF_TTL_S)

RESULTS = []

# The four F-24 rails: answered their own probes on 2026-08-30T21:18 and had no
# prove() call path at all. builds/probe/MESH_STATUS.md, blocker kind NOT_WIRED.
F24 = ("gw-api", "cursor-api", "firecrawl-web", "playwright-dom")


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                        # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _call_prober(name, *args):
    """Call a prober helper that MAY NOT EXIST in the module under test.

    `_bite_check_f24_f25.py` runs this suite against the pre-change prober to
    prove it bites. A missing helper there must make its OWN checks fail - not
    abort the run before the later checks get to speak.
    """
    fn = getattr(P, name, None)
    if fn is None:
        return {"__error__": f"cosmos_rails_prober has no {name}"}
    try:
        return fn(*args)
    except Exception as e:                                        # noqa: BLE001
        return {"__error__": f"{type(e).__name__}: {e}"}


def _dead():
    """A rail that answered nothing. Injected wherever a real call would
    otherwise reach the network or the prepaid seat."""
    return {"ok": False, "rc": 2, "body": "", "model": ""}


def _fake(model, body="PONG"):
    def _call():
        return {"ok": True, "rc": 0, "body": body, "model": model}
    return _call


class _Clock:
    """One clock for the ledger AND the registry - two clocks make an age
    meaningless, which is the whole subject of F-25."""

    def __init__(self, t=1_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


def _reg(tmp: Path, clock) -> Registry:
    led = Ledger(tmp / "auth.jsonl", b"test-key", "test", clock=clock)
    return Registry(led, clock=clock)


# ------------------------------------------------------- F-24: the wiring
def wiring(td: Path) -> None:
    ids = [s["link_id"] for s in P.WIRED_NODES]
    check("WIRED_NODES holds the four rails that answered but were never asked",
          lambda: set(F24) <= set(ids))
    check("the original four hands are still wired (additive, not a rewrite)",
          lambda: {"sgh-api", "gem-api", "oa-api", "claude-cli"} <= set(ids))
    check("no link_id is wired twice (a double prove would double-spend)",
          lambda: len(ids) == len(set(ids)))
    check("registry PROOF_TTL_S exists and IS the prober's re-prove cadence "
          "(a shorter TTL would flap every row between every probe)",
          lambda: cosmos_registry.PROOF_TTL_S == P.NODE_PROOF_TTL_S)

    by_id = {s["link_id"]: s for s in P.WIRED_NODES}
    check("cursor-api is wired core->code, never core->models (H3)",
          lambda: (by_id["cursor-api"]["src"], by_id["cursor-api"]["dst"])
          == ("core", "code"))
    check("firecrawl-web is wired core->papers, so route() cannot capture READ",
          lambda: (by_id["firecrawl-web"]["src"], by_id["firecrawl-web"]["dst"])
          == ("core", "papers"))
    check("playwright-dom is wired DOM core->interact",
          lambda: by_id["playwright-dom"]["rail_type"] == "DOM"
          and by_id["playwright-dom"]["dst"] == "interact")
    check("codex-cli is wired CLI core->code, same shape as claude-cli",
          lambda: (by_id["codex-cli"]["rail_type"], by_id["codex-cli"]["src"],
                   by_id["codex-cli"]["dst"], by_id["codex-cli"].get("module"))
          == ("CLI", "core", "code", None))
    check("codex-cli is a satellite so it cannot fall through to Anthropic",
          lambda: by_id["codex-cli"].get("satellite") == "codex")
    check("github-forge is wired CLI core->forge, never core->code",
          lambda: (by_id["github-forge"]["src"], by_id["github-forge"]["dst"],
                   by_id["github-forge"]["rail_type"])
          == ("core", "forge", "CLI"))
    check("gitlab-forge is wired CLI core->forge, never core->code",
          lambda: (by_id["gitlab-forge"]["src"], by_id["gitlab-forge"]["dst"],
                   by_id["gitlab-forge"]["rail_type"])
          == ("core", "forge", "CLI"))
    check("gitlab-duo-com is wired CLI core->com",
          lambda: (by_id["gitlab-duo-com"]["src"], by_id["gitlab-duo-com"]["dst"],
                   by_id["gitlab-duo-com"]["rail_type"],
                   by_id["gitlab-duo-com"].get("satellite"))
          == ("core", "com", "CLI", "gitlab-duo-com"))
    check("gw-api is wired as an incumbent module rail (NodeRail), not a satellite",
          lambda: by_id["gw-api"]["module"] == "bts_gw"
          and not by_id["gw-api"].get("satellite"))

    root = install(td / "wire", tree_id="rails-wired")
    paths = CosmosPaths(root)
    check("every wired row resolves to a callable prove() path",
          lambda: all(callable(P.default_live_call(paths, s))
                      for s in P.WIRED_NODES))
    check("each satellite names a live_call that exists",
          lambda: all(s["satellite"] in getattr(P, "SATELLITES", {})
                      and callable(P.SATELLITES[s["satellite"]][1])
                      for s in P.WIRED_NODES if s.get("satellite")))

    # -- REGRESSION, measured 2026-08-31: the wiring's second escape ----------
    # Moving the four rails out of mesh_blockers.UNWIRED_ROWS (where each named
    # its own probe module) into WIRED_NODES (where none did) left `probe_with`
    # behind, so every consumer deriving it as `module or "cosmos_claude_rail"`
    # probed the three satellites with the ANTHROPIC rail. Ground truth:
    # builds/probe/mesh_blockers.py --root ./live --deep at 2026-08-31T03:27:21
    # reported cursor-api, firecrawl-web AND playwright-dom each refusing
    # "NO_KEY: Anthropic key missing at live\\config\\anthropic_api_key.txt",
    # while all three carried passing proofs on the authority ledger.
    own = {"cursor-api": "cosmos_cursor_rail",
           "firecrawl-web": "cosmos_firecrawl_rail",
           "groq-api": "cosmos_groq_rail",
           "playwright-dom": "cosmos_playwright_rail",
           "github-forge": "cosmos_forge_rail",
           "gitlab-forge": "cosmos_forge_rail",
           "gitlab-duo-com": "cosmos_gitlab_duo_rail",
           "codex-cli": "cosmos_codex_rail"}
    mods = {lid: _call_prober("probe_module_for", by_id[lid]) for lid in by_id}
    check("each satellite is probed with ITS OWN rail module, never the "
          "Anthropic default (the F-24 wiring left probe_with behind)",
          lambda: {k: mods[k] for k in own} == own)
    check("the incumbent rows still name their bts_* module",
          lambda: all(mods[lid] == by_id[lid]["module"]
                      for lid in ("sgh-api", "gem-api", "gw-api", "oa-api")))
    check("claude-cli - module=None and no satellite - is the ONLY row that "
          "falls through to the claude rail",
          lambda: mods["claude-cli"] == "cosmos_claude_rail"
          and [lid for lid, m in mods.items() if m == "cosmos_claude_rail"]
          == ["claude-cli"])
    check("every wired row's probe module is a module that actually imports",
          lambda: all(__import__(m) for m in mods.values()
                      if str(m).startswith("cosmos_")))


# ------------------------- F-24: a bare install must not reach the network
def bare_install_is_offline(td: Path) -> None:
    root = install(td / "bare", tree_id="rails-wired-bare")
    paths = CosmosPaths(root)
    sats = [s for s in P.WIRED_NODES if s.get("satellite")]
    sat_ids = {s["link_id"] for s in sats}
    check("a bare install configures no satellite (existence, never a read)",
          lambda: len(sats) == sum(1 for s in P.WIRED_NODES if s.get("satellite"))
          and not any(_call_prober("_hands_configured", paths, s) for s in sats))

    clock = _Clock()
    reg = _reg(td, clock)
    check("--live cannot force a satellite this root has never configured",
          lambda: sats and not any(
              P._should_live_probe(paths, reg, s, live=True, ttl_s=PROOF_TTL_S)
              for s in sats))
    # Stub every NON-satellite rail: an injected call always runs, so this
    # exercises the satellite gate without letting --live reach the network or
    # the prepaid Anthropic seat.
    stub = {s["link_id"]: _dead for s in P.WIRED_NODES if not s.get("satellite")}
    check("...and they are reported as no-hands-configured, not as fresh",
          lambda: sat_ids and {p["link_id"]: p.get("skipped")
                               for p in P.map_wired_nodes(
                                   paths, reg, live=True, live_calls=stub)
                               if p["link_id"] in sat_ids}
          == {lid: "no-hands-configured" for lid in sat_ids})

    never = {"n": 0}

    def _tick():
        never["n"] += 1
        return {"ok": True, "rc": 0, "body": "PONG", "model": "m"}

    check("live=False with no hands still does not spend, injected or not "
          "(the invariant an 'injected calls always run' rule would break)",
          lambda: P.map_wired_nodes(
              paths, reg, live=False,
              live_calls={s["link_id"]: _tick for s in P.WIRED_NODES})
          is not None and never["n"] == 0)

    # Writing each satellite's own spec file is what configures it.
    cosmos_cursor_rail.write_spec(paths.config(cosmos_cursor_rail.SPEC_NAME))
    paths.config(cosmos_cursor_rail.KEY_NAME).write_text(
        "crsr_" + "a" * 60 + "31ab", encoding="utf-8")
    cosmos_firecrawl_rail.write_spec(
        paths.config(cosmos_firecrawl_rail.SPEC_NAME))
    check("cursor-api hands appear once BOTH its spec and its key file exist",
          lambda: _call_prober("_hands_configured", paths,
                               {"satellite": "cursor", "link_id": "cursor-api"})
          is True)
    check("firecrawl-web is keyless: its spec file alone configures it",
          lambda: _call_prober(
              "_hands_configured", paths,
              {"satellite": "firecrawl", "link_id": "firecrawl-web"}) is True)
    check("a satellite whose spec is absent stays unconfigured",
          lambda: _call_prober(
              "_hands_configured", paths,
              {"satellite": "playwright", "link_id": "playwright-dom"}) is False)


# ------------- F-24: the derivations, driven through each rail's own seam
def responders(td: Path) -> None:
    root = install(td / "resp", tree_id="rails-wired-resp")
    paths = CosmosPaths(root)
    cosmos_cursor_rail.write_spec(paths.config(cosmos_cursor_rail.SPEC_NAME))
    paths.config(cosmos_cursor_rail.KEY_NAME).write_text(
        "crsr_" + "a" * 60 + "31ab", encoding="utf-8")
    cosmos_firecrawl_rail.write_spec(
        paths.config(cosmos_firecrawl_rail.SPEC_NAME))
    cosmos_playwright_rail.write_spec(
        paths.config(cosmos_playwright_rail.SPEC_NAME))

    real_cursor = cosmos_cursor_rail.CursorRail
    real_fire = cosmos_firecrawl_rail.FirecrawlRail
    real_play = cosmos_playwright_rail.PlaywrightRail

    def _bind(module, attr, real, **extra):
        module.__dict__[attr] = (
            lambda *a, **k: real(*a, **{**k, **extra}))

    try:
        # -- cursor: apiKeyName is the responder, and it comes from the vendor
        def cursor_http(name):
            def _h(method, path, body=None):
                if method == "GET" and path == "/v1/me":
                    return 200, {"date": "Mon, 31 Aug 2026 07:56:01 GMT"}, {
                        "apiKeyName": name, "userId": 1,
                        "userEmail": "someone@example.invalid"}
                return 404, {}, {"error": path}
            return _h

        _bind(cosmos_cursor_rail, "CursorRail", real_cursor,
              http=cursor_http(cosmos_cursor_rail.EXPECTED_KEY_NAME))
        cur = _call_prober("_cursor_live_call", paths)
        check("cursor-api proof names the identity the VENDOR emitted",
              lambda: cur.get("ok") and cur["model"] == "Cursor COSMOS 2"
              and cur["model_source"].startswith("apiKeyName"))
        check("cursor-api proof body carries the vendor date, not a config read",
              lambda: "Mon, 31 Aug 2026 07:56:01 GMT" in cur["body"]
              and cur["rc"] == 0 and cur["body_bytes"] == len(cur["body"]))
        check("cursor-api proof carries NO key material, redacted or otherwise",
              lambda: "crsr_" not in json.dumps(cur)
              and "userEmail" not in json.dumps(cur))
        check("cursor-api proof clears the registry runtime-binding gate",
              lambda: __import__("cosmos_registry").proof_ok(cur))

        # -- FAIL-CLOSED: the vendor answers 200 with the WRONG identity
        _bind(cosmos_cursor_rail, "CursorRail", real_cursor,
              http=cursor_http("Cursor BTS 2"))
        bts = _call_prober("_cursor_live_call", paths)
        check("cursor-api: a 200 from the wrong identity is NOT a proof",
              lambda: bts.get("ok") is False and not bts["body"]
              and not __import__("cosmos_registry").proof_ok(bts))

        # -- firecrawl: the endpoint name is emitted ONLY on a live vendor id
        def fire_http(pid):
            def _h(method, path, body=None):
                data = [{"primaryId": pid, "title": "T"}] if pid else []
                return 200, {"date": "d"}, {"success": True, "data": data}
            return _h

        _bind(cosmos_firecrawl_rail, "FirecrawlRail", real_fire,
              http=fire_http("arxiv:gr-qc/9504041"))
        fc = _call_prober("_firecrawl_live_call", paths)
        check("firecrawl-web proof names the endpoint that answered",
              lambda: fc.get("ok")
              and fc["model"] == getattr(P, "FIRECRAWL_RESPONDER", None)
              and "arxiv:gr-qc/9504041" in fc["body"])

        _bind(cosmos_firecrawl_rail, "FirecrawlRail", real_fire,
              http=fire_http(None))
        fc_dead = _call_prober("_firecrawl_live_call", paths)
        check("firecrawl-web: http=200 with no arxiv:/doi:/pmid: id emits NO "
              "model - the constant cannot stand in for a dead rail",
              lambda: fc_dead.get("ok") is False and fc_dead["model"] == ""
              and not __import__("cosmos_registry").proof_ok(fc_dead))

        # -- playwright: the MCP server names and versions ITSELF
        _bind(cosmos_playwright_rail, "PlaywrightRail", real_play,
              client_factory=cosmos_playwright_rail._fake_factory("t"))
        pw = _call_prober("_playwright_live_call", paths)
        check("playwright-dom proof names server+version from MCP serverInfo",
              lambda: pw.get("ok") and pw["model"].startswith("Playwright/")
              and pw["model_source"].startswith("MCP serverInfo"))
        check("playwright-dom proof body quotes the measured tool count",
              lambda: "tools/list n=" in pw["body"] and pw["rc"] == 0)
    finally:
        cosmos_cursor_rail.__dict__["CursorRail"] = real_cursor
        cosmos_firecrawl_rail.__dict__["FirecrawlRail"] = real_fire
        cosmos_playwright_rail.__dict__["PlaywrightRail"] = real_play


# ------------------------ F-24 x F-25: proven, then aged out of the projection
def prove_then_stale(td: Path) -> None:
    root = install(td / "stale", tree_id="rails-wired-stale")
    paths = CosmosPaths(root)
    clock = _Clock()
    reg = _reg(td / "stale_led", clock)
    (td / "stale_led").mkdir(parents=True, exist_ok=True)
    reg = _reg(td / "stale_led", clock)

    models = {"sgh-api": "grok-4.6", "gem-api": "gemini-2.5-flash",
              "gw-api": "grok-build-0.1", "oa-api": "gpt-5.6-terra",
              "claude-cli": "haiku", "codex-cli": "gpt-5.4-codex",
              "cursor-api": "Cursor COSMOS 2",
              "firecrawl-web": getattr(P, "FIRECRAWL_RESPONDER", "firecrawl"),
              "groq-api": "openai/gpt-oss-20b",
              "playwright-dom": "Playwright/1.63.0-alpha-2026-08-05",
              "github-forge": "rest_limit=5000 remaining=4999",
              "gitlab-forge": "user_id=42 username=probe-user",
              "gitlab-duo-com": "trigger_id=7 description=cosmos-gate"}
    ran = {"n": 0}

    def _counted(model):
        inner = _fake(model)

        def _call():
            ran["n"] += 1
            return inner()
        return _call

    calls = {lid: _counted(m) for lid, m in models.items()}
    # live=True is how Kernel.compose_rails drives an injected sweep
    # (`live=live_calls is not None`); live=False must still refuse to spend.
    P.map_wired_nodes(paths, reg, live=True, live_calls=calls)
    check("NEGATIVE CONTROL - every injected rail call actually RAN",
          lambda: ran["n"] == len(P.WIRED_NODES))
    check("all four F-24 rails are now PROVEN, not merely claimed",
          lambda: set(F24) <= set(reg.live_nodes()))
    check("each F-24 row carries the responder that answered",
          lambda: all(reg.live_nodes()[lid]["model"] == models[lid]
                      for lid in F24))

    dest = paths.role("registry")
    fresh = reg.file_runtime(dest)
    check("the projection counts all eight and declares its TTL",
          lambda: fresh["count"] == len(P.WIRED_NODES)
          and fresh["proof_ttl_s"] == PROOF_TTL_S
          and fresh["stale_count"] == 0)

    # ---- F-25: age ONE rail past the TTL and nothing else.
    clock.t += PROOF_TTL_S + 1
    for lid in F24[:3]:
        reg.prove(lid, "API", "core", "code", _fake(models[lid]))
    aged = reg.file_runtime(dest)
    disk = json.loads((dest / "rails.json").read_text(encoding="utf-8"))

    check("F-25: the stale entry is EXCLUDED from the projection",
          lambda: "playwright-dom" not in disk["nodes"]
          and "playwright-dom" not in reg.live_nodes())
    check("F-25: no row in the projection carries verified=True while stale",
          lambda: all(r["verified"] is True and r["age_s"] <= PROOF_TTL_S
                      for r in disk["matrix"]))
    # `.get` not `[]`: a projection with no `stale` key is exactly the F-25
    # defect, and it must FAIL these checks rather than abort the suite.
    stale_by_id = {r["link_id"]: r for r in (disk.get("stale") or [])}
    check("F-25: the excluded row is NAMED and dated, not silently vanished",
          lambda: "playwright-dom" in stale_by_id
          and stale_by_id["playwright-dom"]["verified"] is False
          and stale_by_id["playwright-dom"]["proof_state"] == "STALE"
          and stale_by_id["playwright-dom"]["age_s"] > PROOF_TTL_S)
    check("F-25: EVERY row the TTL dropped is named, not just the one we watch",
          lambda: set(stale_by_id) | set(disk["nodes"])
          == {s["link_id"] for s in P.WIRED_NODES}
          and stale_by_id
          and all(r["age_s"] > PROOF_TTL_S and r["verified"] is False
                  for r in stale_by_id.values()))
    check("F-25: the re-proven rails are untouched (a fresh proof still counts)",
          lambda: set(F24[:3]) == set(disk["nodes"]) and aged["count"] == 3)
    check("F-25: route() and the projection agree about the stale rail",
          lambda: not reg.route("core", "interact")
          and "playwright-dom" not in reg.live_nodes())
    check("F-25: max_age_s=None is still the escape hatch route() documents",
          lambda: "playwright-dom" in reg.live_nodes(max_age_s=None))
    check("F-25 fail-closed: an age that cannot be computed is STALE",
          lambda: Registry._fresh({"age_s": None}, PROOF_TTL_S) is False)

    # ---- the freshness gate flips exactly on the stale row. Hands must be
    # configured for either answer to mean anything, so give the decision one
    # incumbent root and change ONLY which rail it is asked about.
    os.environ["COSMOS_BTS_ROOT"] = str(td)
    try:
        check("unattended clock does not re-ask a stale rail (requires --live)",
              lambda: P._should_live_probe(
                  paths, reg, {"link_id": "playwright-dom", "module": "bts_gw"},
                  live=False, ttl_s=PROOF_TTL_S) is False)
        check("...and a fresh rail is also not re-asked unattended",
              lambda: P._should_live_probe(
                  paths, reg, {"link_id": "gw-api", "module": "bts_gw"},
                  live=False, ttl_s=PROOF_TTL_S) is False)
        check("--live still re-asks a stale rail",
              lambda: P._should_live_probe(
                  paths, reg, {"link_id": "playwright-dom", "module": "bts_gw"},
                  live=True, ttl_s=PROOF_TTL_S) is True)
    finally:
        os.environ.pop("COSMOS_BTS_ROOT", None)


# ----------------------------- fail-closed: answering is not the same as proving
def fail_closed(td: Path) -> None:
    root = install(td / "fc", tree_id="rails-wired-fc")
    paths = CosmosPaths(root)
    (td / "fc_led").mkdir(parents=True, exist_ok=True)
    clock = _Clock()
    reg = _reg(td / "fc_led", clock)

    def _no_model():
        return {"ok": True, "rc": 0, "body": "it answered", "model": ""}

    def _empty_body():
        return {"ok": True, "rc": 0, "body": "   ", "model": "Playwright/9"}

    calls = {lid: _fake("m") for lid in
             (s["link_id"] for s in P.WIRED_NODES)}
    calls["cursor-api"] = _no_model
    calls["playwright-dom"] = _empty_body
    P.map_wired_nodes(paths, reg, live=True, live_calls=calls)
    live = reg.live_nodes()
    check("a rail that answers but names no responder is NOT registered",
          lambda: "cursor-api" not in live)
    check("a rail that answers with an empty body is NOT registered",
          lambda: "playwright-dom" not in live)
    check("the rails that did answer properly ARE registered",
          lambda: {"gw-api", "firecrawl-web"} <= set(live))

    run = reg.file_runtime(paths.role("registry"))
    check("the fail-closed rows are absent from BOTH nodes and stale "
          "(never proven is not the same as gone stale)",
          lambda: "cursor-api" not in run["nodes"]
          and "stale" in run
          and "cursor-api" not in [r["link_id"] for r in run["stale"]])


def main() -> int:
    old_env = os.environ.pop("COSMOS_BTS_ROOT", None)
    try:
        td = Path(tempfile.mkdtemp(prefix="cosmos_rails_wired_"))
        wiring(td)
        bare_install_is_offline(td)
        responders(td)
        prove_then_stale(td)
        fail_closed(td)
    finally:
        if old_env is not None:
            os.environ["COSMOS_BTS_ROOT"] = old_env

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (F-24 four rails have a prove() path with a "
          "vendor-emitted responder; F-25 a stale proof is excluded and named)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
