#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mesh_blockers.py -- WHY each node rail does not prove live. Measured, never asserted.

WISHLIST "WIRE THE MESH (nodes mapped at RUNTIME)". `Registry.file_runtime` projects
ONLY nodes that passed `proof_ok` (ok + rc==0 + non-empty body + the model that
answered). Every rail that is absent from `live/registry/nodes.json` is absent for a
REASON, and that reason is a typed refusal the rail itself emits. This tool collects
those refusals verbatim and renders MESH_STATUS.md from them, so the document cannot
drift from the machine.

It does NOT weaken the prove gate and it does NOT fabricate reachability:
  * it never calls `Registry.prove` and never appends to the ledger (read-only open);
  * it never dispatches a metered model rail (no spend) -- only each rail's own
    cheapest liveness probe, plus the ledger's last recorded measurement;
  * a rail it did not measure is reported UNMEASURED, never green.

Blocker kinds (machine-readable, branch on `kind`):
  NONE          proven live in the authority ledger, proof fresh
  STALE_PROOF   proven once, now older than the proof TTL; listed under the
                projection's `stale` list (F-25), not counted live
  NOT_WIRED     no prove() call path exists -- link_id is not in WIRED_NODES, so the
                prober never asks it for a proof no matter how healthy it is
  NO_PROOF      wired and probe-green, but no passing proof recorded yet
  NO_KEY / UNREACHABLE / BROKE / BAD_SPEC / AUTH_REQUIRED / REFUSED
                the rail's own typed refusal, quoted verbatim in `blocker`
  UNMEASURED    not probed on this run (see `detail`); never counted as live

    py -3.14 builds\\probe\\mesh_blockers.py --root V:\\A\\Ai\\COSMOS\\live
    py -3.14 builds\\probe\\mesh_blockers.py --root ... --deep --write-md

Writes only under this directory. Windowless on Windows (the rails' own _real_run).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_paths import CosmosPaths, CosmosPathError            # noqa: E402
from cosmos_rails_prober import (  # noqa: E402
    NODE_PROOF_TTL_S, WIRED_NODES, probe_module_for,
)

WIRED = {w["link_id"]: w for w in WIRED_NODES}
# Ordered SPECIFIC CAUSE first, generic wrapper last. Rails nest their refusals
# ("UNREACHABLE: NO_KEY: [NO_KEY] key missing at ..."), and the wrapper is the least
# actionable half of that sentence: "unreachable" sends someone hunting a network,
# "no key" names the file to create.
KNOWN_KINDS = ("NO_KEY", "AUTH_REQUIRED", "BAD_SPEC", "EMPTY_OUTPUT",
               "UNREACHABLE", "BROKE", "REFUSED")

# Every node rail COSMOS owns. The wired four come from the prober itself (never a
# second copy of that table); these are the rails it does NOT ask for a proof. Their
# rail_type/route are read off the ledger's own LINK_REGISTERED claim, not guessed
# here -- one truth, and a row this tool invented would be exactly the fabrication
# the mesh gate exists to refuse.
UNWIRED_ROWS = (
    {"link_id": "gw-api", "probe_with": "bts_gw",
     "note": "wired as an adapter by cosmos_node_rails.register_node_rails "
             "(budget $5) but absent from cosmos_rails_prober.WIRED_NODES, so "
             "nothing ever asks it for a proof"},
    {"link_id": "cursor-api", "probe_with": "cosmos_cursor_rail"},
    {"link_id": "codex-cli", "probe_with": "cosmos_codex_rail"},
    {"link_id": "firecrawl-web", "probe_with": "cosmos_firecrawl_rail"},
    {"link_id": "playwright-dom", "probe_with": "cosmos_playwright_rail"},
)

# Nuances that a refusal string alone does not carry.
NOTES = {
    "claude-cli":
        "Two paths, one link_id: ClaudeRail.dispatch needs config/"
        "anthropic_api_key.txt, but cosmos_rails_prober._claude_live_call falls "
        "back to the prepaid SEAT (`claude -p` with ANTHROPIC_API_KEY unset). The "
        "recorded proof came from the seat path, so ClaudeRail.probe() refusing "
        "NO_KEY does not contradict the registry row.",
    "gem-api":
        "GEM via Vertex (Joanna GCP credit ~Oct 13). Prove path is "
        "cosmos_vertex_rail generateContent binding vendor modelVersion. "
        "bts_gem is failover when vertex_key.txt / VERTEX_API_KEY is absent. "
        "A missing credential is UNMEASURED, never GREEN.",
}


def rows() -> list[dict]:
    """The wired four (from the prober's own table) + the rails it never asks."""
    out = []
    for w in WIRED_NODES:
        out.append(dict(w, probe_with=probe_module_for(w),
                        route=f"{w['src']}->{w['dst']}", note=NOTES.get(w["link_id"])))
    # A rail that has since been WIRED must leave the unasked list, or rows()
    # reports it twice in contradictory states -- once wired, once "no prove()
    # call path exists". Measured 2026-08-31: wiring gw-api, cursor-api,
    # firecrawl-web and playwright-dom (F-24) left all four in BOTH tables, so
    # rows() returned 13 entries for 9 rails. The wired table is authoritative;
    # UNWIRED_ROWS is only the set nobody asks YET.
    wired_ids = {w["link_id"] for w in WIRED_NODES}
    out += [dict(u) for u in UNWIRED_ROWS if u["link_id"] not in wired_ids]
    return out


def _kind_of(detail: str, default: str) -> str:
    """The most specific refusal kind present in the rail's own message.

    Reads KNOWN_KINDS in priority order, not text order, so a wrapper cannot bury
    the cause. Invents nothing: a message carrying no known kind gets the caller's
    default.
    """
    up = str(detail or "").upper()
    return next((k for k in KNOWN_KINDS if k in up), default)


# ---------------- per-rail probes (cheap, read-only, no spend) ----------------

def probe_node_rail(paths, module: str) -> dict:
    """Incumbent import-liveness + ask() presence. Never dispatches (no spend)."""
    from cosmos_node_rails import NodeRail, resolve_incumbent_root
    root = resolve_incumbent_root(paths)
    rail = NodeRail(module, paths=paths)
    ok, detail = rail.probe()
    ev = {"incumbent_root": root, "module": module}
    if not ok:
        return {"ok": False, "detail": detail, "evidence": ev}
    mod = rail._mod                                   # set by the probe's own import
    ev["module_file"] = getattr(mod, "__file__", None)
    if not callable(getattr(mod, "ask", None)):
        return {"ok": False, "evidence": ev,
                "detail": f"BROKE: {module} has no ask() -- NodeRail.dispatch "
                          f"cannot produce a body or a model"}
    ev["has_ask"] = True
    return {"ok": True, "detail": detail, "evidence": ev}


def probe_binary_rail(paths, which_mod: str) -> dict:
    """claude / codex: key shape then `<bin> --version`. Never -p / exec."""
    mod = __import__(which_mod)
    from cosmos_rail_base import _real_which
    spec = mod.load_spec(mod.spec_path_for(paths) if mod.spec_path_for(paths).exists()
                         else None)
    keyp = mod.key_path_for(paths, spec)
    rail = getattr(mod, "ClaudeRail", None) or mod.CodexRail
    ok, detail = rail(keyp, spec, live_root=paths.root).probe()
    return {"ok": ok, "detail": detail,
            "evidence": {"key_path": str(keyp), "key_present": keyp.exists(),
                         "binary": mod.BINARY,
                         "binary_on_path": _real_which(mod.BINARY)}}


def probe_http_rail(paths, which_mod: str) -> dict:
    """cursor / firecrawl: the rail's own cheap GET. Never launches an agent/crawl."""
    mod = __import__(which_mod)
    sp = mod.spec_path_for(paths)
    spec = mod.load_spec(sp if sp.exists() else None)
    keyp = mod.key_path_for(paths, spec)
    rail = (getattr(mod, "CursorRail", None) or mod.FirecrawlRail)(keyp, spec)
    ok, detail = rail.probe()
    return {"ok": ok, "detail": detail,
            "evidence": {"key_path": str(keyp), "key_present": keyp.exists(),
                         "base": spec.get("base"), "identity": rail.last_identity()}}


def probe_playwright(paths, deep: bool) -> dict:
    """tools/list over the MCP server. Spawns npx, so it is --deep only."""
    import cosmos_playwright_rail as m
    from cosmos_rail_base import _real_which
    sp = m.spec_path_for(paths)
    spec = m.load_spec(sp if sp.exists() else None)
    ev = {"spec_path": str(sp), "spec_present": sp.exists(),
          "npx_on_path": _real_which("npx")}
    if not deep:
        return {"ok": False, "kind": "UNMEASURED", "evidence": ev,
                "detail": "UNMEASURED: MCP tools/list not attempted (pass --deep; "
                          "the probe spawns the npx MCP server)"}
    rail = m.PlaywrightRail(spec, output_dir=HERE / "_ws_playwright")
    try:
        ok, detail = rail.probe()
        ev["last"] = rail.last_identity()
    finally:
        rail.close()
    return {"ok": ok, "detail": detail, "evidence": ev}


def probe_vertex_rail(paths) -> dict:
    """Key/spec identity only. Never generateContent (that is --live prove)."""
    import cosmos_vertex_rail as m
    spec = m.load_spec(paths)
    keyp = paths.config(m.KEY_NAME)
    ev = {"key_path": str(keyp), "key_present": keyp.exists(),
          "account": spec.get("account"), "project": spec.get("project")}
    if not keyp.exists() and not str(
            os.environ.get("VERTEX_API_KEY") or "").strip():
        return {"ok": False, "kind": "UNMEASURED", "evidence": ev,
                "detail": "UNMEASURED: vertex_key.txt / VERTEX_API_KEY absent"}
    return {"ok": True,
            "detail": f"vertex key present project={spec.get('project')}",
            "evidence": ev}


def measure(paths, row: dict, *, deep: bool) -> dict:
    mod = row["probe_with"]
    try:
        if mod.startswith("bts_"):
            return probe_node_rail(paths, mod)
        if mod == "cosmos_playwright_rail":
            return probe_playwright(paths, deep)
        if mod == "cosmos_vertex_rail":
            return probe_vertex_rail(paths)
        if mod in ("cosmos_cursor_rail", "cosmos_firecrawl_rail"):
            return probe_http_rail(paths, mod)
        return probe_binary_rail(paths, mod)
    except Exception as e:                                        # noqa: BLE001
        # This tool's own failure is reported as this tool's own failure.
        return {"ok": False, "evidence": {"probe_with": mod},
                "detail": f"BROKE: mesh_blockers probe raised "
                          f"{type(e).__name__}: {e}"}


# ---------------- the authority side (read-only) ----------------

def registry_view(paths) -> dict:
    """live_nodes() + last recorded measurement per link, straight off the ledger.

    Opened read-only: this tool never appends, so running it cannot manufacture a
    proof for anything.
    """
    keyfile = paths.config("install_key.bin")
    if not keyfile.exists():
        return {"error": f"NO_KEY: {keyfile} absent -- the ledger cannot be opened",
                "live": {}, "state": {}}
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    reg = Registry(Ledger(paths.ledger() / "authority.jsonl", keyfile.read_bytes(),
                          "mesh-blockers-readonly"))
    # F-25 leftover: live_nodes() no longer contains expired proofs. The
    # classifier needs stale_nodes() or it relabels them NO_PROOF.
    stale = reg.stale_nodes() if hasattr(reg, "stale_nodes") else {}
    return {"error": None, "live": reg.live_nodes(), "stale": stale,
            "state": reg.state()}


def classify(row: dict, probe: dict, live: dict, state: dict,
             stale: dict | None = None) -> dict:
    """The question is 'does this node prove live', so the LEDGER answers first.

    A rail can be in the registry while its own probe refuses (claude-cli: proven
    through the seat path, ClaudeRail.probe refusing NO_KEY). Both facts are kept --
    `kind` is the proof status, `probe_kind` is what the rail says right now.

    `live` is Registry.live_nodes() (F-25: freshness already applied). `stale` is
    Registry.stale_nodes() -- rows live_nodes() dropped. Passing a stale row in
    `live` is still classified STALE_PROOF (age > TTL), which is how the offline
    suite pins the TTL itself without standing up a Registry.
    """
    lid = row["link_id"]
    wired = lid in WIRED
    stale = stale or {}
    lrow = live.get(lid)
    stale_row = stale.get(lid)
    srow = state.get(lid) or {}
    detail = str(probe.get("detail") or "")
    probe_kind = ("UNMEASURED" if probe.get("kind") == "UNMEASURED"
                  else "OK" if probe.get("ok") else _kind_of(detail, "BROKE"))
    if lrow:
        age = lrow.get("age_s")
        kind = ("STALE_PROOF" if age is not None and age > NODE_PROOF_TTL_S
                else "NONE")
    elif stale_row:
        # F-25: live_nodes() omitted this row. Naming it STALE_PROOF is the
        # whole leftover -- without this branch the live path called it NO_PROOF.
        lrow = stale_row
        kind = "STALE_PROOF"
    elif probe_kind not in ("OK", "UNMEASURED"):
        kind = probe_kind
    elif not wired:
        kind = "NOT_WIRED"
    elif probe_kind == "UNMEASURED":
        kind = "UNMEASURED"
    else:
        kind = "NO_PROOF"
    claim = srow.get("claim") or {}
    blocker = {
        "NONE": "",
        "STALE_PROOF": (
            f"proof age {round(lrow['age_s'], 1) if lrow else '?'}s exceeds the "
            f"{int(NODE_PROOF_TTL_S)}s proof TTL; Registry.file_runtime lists this "
            f"row under 'stale' (verified:false, proof_state:STALE), not under "
            f"'nodes'. The F-25 freshness filter dropped it from count; it is "
            f"named, not deleted"),
        "NOT_WIRED": (
            f"no prove() call path: {lid} is absent from "
            f"cosmos_rails_prober.WIRED_NODES, so nothing ever asks it for a proof. "
            f"The ledger holds its LINK_REGISTERED claim and "
            f"{'zero' if srow.get('ok') is None else 'no passing'} PROBE_RESULT "
            f"rows. Its probe() returns (ok, detail) -- no body, no model -- so "
            f"proof_ok can never pass on a probe alone"),
        "NO_PROOF": ("wired for prove() and probe-green, but no passing proof is "
                     "recorded on the ledger"),
    }.get(kind, detail)
    if not wired and kind not in ("NONE", "STALE_PROOF", "NOT_WIRED"):
        # Fixing the refusal alone would not put this node in the registry.
        blocker += (f"  [AND: {lid} is absent from "
                    f"cosmos_rails_prober.WIRED_NODES, so clearing the refusal "
                    f"above still leaves nothing asking it for a proof]")
    return {
        "link_id": lid,
        "rail_type": claim.get("rail_type") or row.get("rail_type"),
        "route": (f"{claim['src']}->{claim['dst']}" if claim.get("src")
                  else row.get("route") or "unclaimed"),
        "probed_via": row["probe_with"],
        "wired_for_prove": wired,
        "claimed_in_ledger": bool(srow),
        "in_registry": bool(live.get(lid)),
        "in_stale": bool(stale_row) or kind == "STALE_PROOF",
        "kind": kind,
        "probe_kind": probe_kind,
        "blocker": blocker,
        "probe_detail": detail,
        "evidence": probe.get("evidence") or {},
        "ledger_last": {
            "ok": srow.get("ok"), "rc": srow.get("rc"),
            "model": srow.get("model"), "body_bytes": srow.get("body_bytes"),
            "age_s": (round(lrow["age_s"], 1)
                      if lrow and lrow.get("age_s") is not None else None),
            "probe_results_recorded": srow.get("ok") is not None,
        } if srow else None,
        "note": row.get("note"),
    }


def collect(root: str, *, deep: bool = False) -> dict:
    paths = CosmosPaths(root)
    view = registry_view(paths)
    t0 = time.time()
    out = [classify(r, measure(paths, r, deep=deep), view["live"], view["state"],
                    stale=view.get("stale") or {})
           for r in rows()]
    proj = paths.role("registry") / "nodes.json"
    return {
        "schema": "cosmos-mesh-blockers/1",
        "measured_at": datetime.now().astimezone().isoformat(),
        "root": str(paths.root),
        "deep": bool(deep),
        "ledger_error": view["error"],
        "projection": str(proj),
        "projection_count": (json.loads(proj.read_text(encoding="utf-8")).get("count")
                             if proj.exists() else None),
        "proof_ttl_s": NODE_PROOF_TTL_S,
        "live_count": sum(1 for r in out if r["kind"] == "NONE"),
        "stale_count": sum(1 for r in out if r["kind"] == "STALE_PROOF"),
        "total": len(out),
        "elapsed_s": round(time.time() - t0, 2),
        "nodes": out,
    }


# ---------------- rendering ----------------

UNBLOCK = {
    "NO_KEY": "Keith places the credential at the `key_path` in the evidence above "
              "(credentials are his domain -- COSMOS opens the door, never a bat).",
    "AUTH_REQUIRED": "The key present is rejected by the vendor; rotate it at the "
                     "`key_path` in the evidence above.",
    "UNREACHABLE": "Install/expose the binary or endpoint the refusal names. No "
                   "code change makes an absent hand answer.",
    "BROKE": "The hand answered but not in the shape the rail requires; fix the "
             "adapter, not the gate.",
    "NOT_WIRED": "Add the row to `cosmos_rails_prober.WIRED_NODES` **with a "
                 "prove-shaped live_call** returning {ok, rc, body, model}. A "
                 "`probe()` returning (ok, detail) can never satisfy `proof_ok` -- "
                 "it carries no body and no model.",
    "NO_PROOF": "Wired and probe-green: run the prober with `--live` to spend one "
                "call and record the proof.",
    "STALE_PROOF": "Re-prove: `file_runtime` already dropped this row from "
                   "`count`/`nodes` (F-25 freshness filter) and lists it under "
                   "`stale`. Run the rails prober with `--live` to record a "
                   "fresh proof.",
    "UNMEASURED": "Re-run this tool with `--deep`.",
    "NONE": "Nothing -- proven live.",
}


def render_md(rec: dict) -> str:
    L = [
        "# MESH_STATUS -- why each node rail does or does not prove live",
        "",
        "**Generated** by `builds/probe/mesh_blockers.py` (do not hand-edit; re-run it).",
        f"**Measured** {rec['measured_at']}  ·  root `{rec['root']}`  ·  "
        f"deep={rec['deep']}  ·  {rec['elapsed_s']}s",
        f"**Projection** `{rec['projection']}` count={rec['projection_count']}  ·  "
        f"proof TTL {int(rec['proof_ttl_s'])}s",
        "",
        "The gate is `cosmos_registry.proof_ok`: **ok AND rc==0 AND a non-empty body "
        "AND the model that answered.** Nothing here weakens it, and nothing here "
        "asserts reachability -- a rail this tool did not measure is UNMEASURED, "
        "never green.",
        "",
        "Two columns, two different facts. **blocker kind** is why the node does or "
        "does not carry a passing proof on the authority ledger. **the rail's own "
        "probe** is the line that rail emitted during this run, verbatim -- a rail "
        "can be perfectly healthy and still never prove live, because nothing asks "
        "it (`NOT_WIRED`).",
        "",
        "| node | type | route | wired for prove | proven live | blocker kind | "
        "the rail's own probe, right now |",
        "|---|---|---|---|---|---|---|",
    ]
    for n in rec["nodes"]:
        d = (n["probe_detail"] or "").replace("|", "\\|").replace("\n", " ")
        while True:                    # rails nest kinds; the column already has it
            head = d.split(":", 1)[0].strip().strip("[]")
            if head in KNOWN_KINDS + ("UNMEASURED", "OK") and ":" in d:
                d = d.split(":", 1)[1].strip()
                continue
            break
        L.append(f"| `{n['link_id']}` | {n['rail_type']} | {n['route']} | "
                 f"{'yes' if n['wired_for_prove'] else '**NO**'} | "
                 f"{'yes' if n['in_registry'] else 'no'} | **{n['kind']}** | "
                 f"{n['probe_kind']}: {d[:110] or '--'} |")
    L += ["", f"**{rec['live_count']} of {rec['total']} node rails carry a passing "
              f"proof** (the projection counts {rec['projection_count']}).", ""]
    unwired = [n["link_id"] for n in rec["nodes"] if n["kind"] == "NOT_WIRED"]
    silent = [n["link_id"] for n in rec["nodes"]
              if n["ledger_last"] and not n["ledger_last"]["probe_results_recorded"]]
    healthy_unwired = [n["link_id"] for n in rec["nodes"]
                       if n["kind"] == "NOT_WIRED" and n["probe_kind"] == "OK"]
    stale = [n["link_id"] for n in rec["nodes"] if n["kind"] == "STALE_PROOF"]
    L += ["## What the ledger says, structurally", ""]
    if silent:
        L.append(f"* **{len(silent)} links hold a `LINK_REGISTERED` claim and ZERO "
                 f"`PROBE_RESULT` rows** -- {', '.join('`%s`' % s for s in silent)}. "
                 f"The claim is in the authority ledger; no measurement ever "
                 f"followed it, so `live_nodes()` drops every one. Registration is "
                 f"not capability, exactly as designed.")
    if unwired:
        L.append(f"* **{len(unwired)} links have no prove() call path at all** -- "
                 f"{', '.join('`%s`' % s for s in unwired)} are absent from "
                 f"`cosmos_rails_prober.WIRED_NODES`. This is the single biggest "
                 f"reason the registry is small: not refusal, not credentials -- "
                 f"nobody asks.")
    if healthy_unwired:
        L.append(f"* **{len(healthy_unwired)} of those answered their own probe on "
                 f"this run** -- {', '.join('`%s`' % s for s in healthy_unwired)}. "
                 f"Wiring them needs a prove-shaped `live_call` (returning a body "
                 f"and the model), not a credential.")
    if stale:
        L.append(f"* **{len(stale)} link{'s' if len(stale) > 1 else ''} "
                 f"{'sit' if len(stale) != 1 else 'sits'} in the projection's "
                 f"`stale` list** -- {', '.join('`%s`' % s for s in stale)}. "
                 f"`Registry.file_runtime` applies the proof TTL "
                 f"(`proof_ttl_s`); a stale row is `verified: false` and is "
                 f"not in `count`/`nodes`. Re-prove to move it back.")
    L.append("")
    if rec["ledger_error"]:
        L += [f"> Ledger unreadable: `{rec['ledger_error']}` -- every row below is "
              f"probe-only.", ""]
    L.append("## Per node")
    for n in rec["nodes"]:
        L += ["", f"### `{n['link_id']}` -- {n['kind']}", ""]
        if n.get("note"):
            L += [f"*{n['note']}*", ""]
        L += ["**Blocker:**",
              "", "```", (n["blocker"] or "none -- this node proves live").strip(),
              "```", "",
              f"**What `{n['probed_via']}` emitted on this run** "
              f"({n['probe_kind']}):",
              "", "```", (n["probe_detail"] or "(nothing emitted)").strip(),
              "```", ""]
        ev = {k: v for k, v in (n["evidence"] or {}).items() if k != "identity"}
        if ev:
            L += ["Evidence:", "",
                  "```json", json.dumps(ev, indent=1, default=str), "```", ""]
        if n["ledger_last"]:
            L += ["Ledger's last measurement for this link:", "",
                  "```json", json.dumps(n["ledger_last"], indent=1, default=str),
                  "```", ""]
        L.append(f"**Unblocked by:** {UNBLOCK.get(n['kind'], 'see the refusal above.')}")
    L += ["", "---", "",
          "Regenerate: `py -3.14 builds\\probe\\mesh_blockers.py --root "
          "<runtime-root> --deep --write-md`", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(prog="mesh_blockers")
    ap.add_argument("--root", required=True, help="COSMOS runtime root")
    ap.add_argument("--deep", action="store_true",
                    help="also spawn the playwright MCP server for tools/list")
    ap.add_argument("--write-md", action="store_true",
                    help="render MESH_STATUS.md beside this tool")
    ap.add_argument("--json", default=None, help="also write the raw record here")
    a = ap.parse_args()
    rec = collect(a.root, deep=a.deep)
    sys.path.insert(0, str(HERE))
    import artifact_freshness as af                                    # noqa: WPS433
    af.stamp(rec, REPO, ["builds/probe/mesh_blockers.py"])
    if a.write_md:
        (HERE / "MESH_STATUS.md").write_text(render_md(rec), encoding="utf-8")
    if a.json:
        Path(a.json).write_text(json.dumps(rec, indent=1, default=str),
                                encoding="utf-8")
    print(json.dumps(rec, indent=1, default=str))
    # rc reflects the MEASUREMENT, not the mesh: 0 means every rail was measured.
    return 0 if not rec["ledger_error"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
