#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_principles - the Cm-stream principles, canonized IN CODE.

Keith, 2026-08-25: "Canonize these in code in COSMOS now. Enumerate them.
Encode them in .py and toml. Prove they are all encoded."

The enumerated principles live beside this file in cosmos_principles.toml. This
module loads them and gives each one an EXECUTABLE CHECK bound to a real
artifact in the tree (a canon file, a source marker, a live heartbeat, a
measured line count) — so a principle is a GATE, not a wish, and "encoded" is
proven by running it, never asserted (no fabricated compliance).

    py -3.14 cosmos\\cosmos_principles.py --list
    py -3.14 cosmos\\cosmos_principles.py --audit --root V:\\A\\Ai\\COSMOS\\live
    py -3.14 cosmos\\cosmos_principles.py --check P3 --root ...

Depends on stdlib only (tomllib is 3.11+). Adds nothing to core logic.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import tomllib
from pathlib import Path

PKG = Path(__file__).resolve().parent
REPO = PKG.parent
TOML = PKG / "cosmos_principles.toml"
FRESH_S = 180.0  # a daemon heartbeat older than this is stale, not proof of life

PASS, FAIL, UNPROVEN, NA = "PASS", "FAIL", "UNPROVEN", "NA"


def load() -> dict:
    return tomllib.loads(TOML.read_text(encoding="utf-8"))


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def _canon_files_exist(principle: dict) -> dict:
    """Every file a principle cites as its canon must actually exist."""
    cites = re.split(r"[;,]", str(principle.get("canon", "")))
    out = {}
    for c in cites:
        c = c.strip()
        m = re.match(r"^([\w./\\-]+\.(?:md|toml))", c)
        if not m:
            continue
        rel = m.group(1)
        out[rel] = (REPO / rel).exists()
    return out


def _heartbeat(root: Path, name: str) -> dict:
    p = root / "logs" / name
    if not p.exists():
        return {"exists": False, "path": str(p)}
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        return {"exists": True, "path": str(p), "unreadable": str(e)}
    age = None
    if "last_run_epoch" in rec:
        age = round(time.time() - float(rec["last_run_epoch"]), 1)
    return {"exists": True, "path": str(p), "age_s": age,
            "interval_s": rec.get("interval_s"), "pid": rec.get("pid"),
            "state": rec.get("state") or rec.get("tick")}


def _py_files() -> list[Path]:
    return [p for p in (REPO / "cosmos").glob("*.py")
            if p.name != "__init__.py"]


# --------------------------------------------------------------------------
# one check per principle — each returns {status, evidence}
# --------------------------------------------------------------------------

def activity_clock_15s(ctx) -> dict:
    src = _read(ctx["wd2"])
    encoded = "DEFAULT_INTERVAL_S = 15.0" in src or "DEFAULT_INTERVAL_S=15.0" in src
    hb = _heartbeat(ctx["root"], "watchdog2_heartbeat.json")
    return {"status": PASS if encoded else FAIL,
            "evidence": {"wd2_default_interval_15s": encoded,
                         "live_heartbeat": hb}}


def pause_formal(ctx) -> dict:
    src = _read(ctx["wd2"])
    proto = (REPO / "docs" / "PAUSE_PROTOCOL.md").exists()
    honors = ("def pause_flag" in src and '"PAUSED"' in src
              and "write_heartbeat" in src)
    return {"status": PASS if (proto and honors) else FAIL,
            "evidence": {"PAUSE_PROTOCOL.md": proto,
                         "wd2_reads_flag_and_beats_PAUSED": honors}}


def resume_gate(ctx) -> dict:
    src = _read(ctx["wd2"])
    has_fn = "def maybe_auto_resume" in src
    has_modes = "resume_gate" in src and "auto_resume_at" in src
    canon = "Resession resume gate" in _read(REPO / "CLAUDE.md")
    ok = has_fn and has_modes and canon
    return {"status": PASS if ok else FAIL,
            "evidence": {"wd2.maybe_auto_resume": has_fn,
                         "modes_hold_and_resume_gate": has_modes,
                         "claude_md_canon": canon}}


def no_bts_imports(ctx) -> dict:
    pat = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
    offenders = {}
    for p in _py_files():
        hits = pat.findall(_read(p))
        if hits:
            offenders[p.name] = hits
    return {"status": PASS if not offenders else FAIL,
            "evidence": {"cosmos_py_files_scanned": len(_py_files()),
                         "bts_importers": offenders or "none"}}


def anti_loss_daemons(ctx) -> dict:
    root = ctx["root"]
    coll = _heartbeat(root, "collector_heartbeat.json")
    run = _heartbeat(root, "cosmos_runner_heartbeat.json")

    def fresh(h):
        return bool(h.get("exists") and isinstance(h.get("age_s"), (int, float))
                    and h["age_s"] < FRESH_S)
    reconcile = "reconcile" in _read(REPO / "BUCm.toml")
    live = fresh(coll) and fresh(run)
    return {"status": PASS if (live and reconcile) else UNPROVEN,
            "evidence": {"collector": coll, "runner": run,
                         "reconcile_in_bucm": reconcile,
                         "note": "PASS needs both daemons fresh (<180s) AND the "
                                 "resession reconcile step in the handoff."}}


def self_build_process(ctx) -> dict:
    wl = REPO / "docs" / "WISHLIST.md"
    text = _read(wl)
    open_wishes = len(re.findall(r"^- \[ \]", text, re.M))
    canon = "process, not an endpoint" in _read(REPO / "CLAUDE.md").lower()
    ok = wl.exists() and canon
    return {"status": PASS if ok else FAIL,
            "evidence": {"WISHLIST.md": wl.exists(),
                         "open_wishes": open_wishes,
                         "claude_md_process_not_endpoint": canon}}


def keep_afloat(ctx) -> dict:
    lock = (REPO / "cosmos" / "cosmos_lock.py").exists()
    canon = "afloat" in _read(REPO / "CLAUDE.md").lower()
    return {"status": PASS if (lock and canon) else FAIL,
            "evidence": {"cosmos_lock.py_one_writer": lock,
                         "claude_md_keep_afloat": canon}}


def improvement_not_bloat(ctx) -> dict:
    """Measured, over time: total cosmos/ LOC vs a recorded baseline. First run
    records the baseline (PASS); later runs report the trend and FLAG growth."""
    total = 0
    per = {}
    for p in _py_files():
        n = sum(1 for ln in _read(p).splitlines() if ln.strip())
        per[p.name] = n
        total += n
    base_dir = ctx["root"] / "state" / "principles"
    base_dir.mkdir(parents=True, exist_ok=True)
    base = base_dir / "loc_baseline.json"
    prev = None
    if base.exists():
        try:
            prev = json.loads(base.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            prev = None
    now_rec = {"measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "total_loc": total, "files": len(per)}
    delta = None
    status = PASS
    if prev and isinstance(prev.get("total_loc"), int):
        delta = total - prev["total_loc"]
        # trend UP without a recorded justification is a flag, not a hard fail
        status = PASS if delta <= 0 else "WATCH"
    base.write_text(json.dumps(now_rec, indent=1), encoding="utf-8")
    canon = "improvement is not bloat" in _read(REPO / "CLAUDE.md").lower()
    return {"status": status if canon else FAIL,
            "evidence": {"total_code_loc": total, "files": len(per),
                         "prev_total_loc": (prev or {}).get("total_loc"),
                         "delta_loc": delta, "canon": canon,
                         "baseline": str(base),
                         "note": "WATCH = code grew since last audit; justify "
                                 "against the feature added or subtract weight."}}


def orchestrator_only(ctx) -> dict:
    """P9: the role contract is encoded (canon) AND the box exists (mechanism).
    This is the auditable, hard-wired form — it proves the contract is in place
    and dispatchable; it does not police every COW action."""
    claude = _read(REPO / "CLAUDE.md").lower()
    canon = ("cow's role is a hard contract" in claude
             and "other agents execute" in claude)
    disp = (REPO / "cosmos" / "cosmos_dispatch.py").exists()
    dhx = (REPO / "docs" / "AGENT_BRIEF.md").exists()
    return {"status": PASS if (canon and disp and dhx) else FAIL,
            "evidence": {"role_contract_in_claude_md": canon,
                         "box_dispatch_cosmos_dispatch_py": disp,
                         "box_dhx_agent_brief_md": dhx}}


def agents_propose_only(ctx) -> dict:
    """P10: the AI work order — agents propose, the Orchestrator disposes. The
    boundaries addendum exists and the DHx carries the propose rule."""
    boundaries = (REPO / "docs" / "AGENT_BOUNDARIES.md").exists()
    dhx = "propose, don't touch the tree" in _read(REPO / "docs" / "AGENT_BRIEF.md").lower()
    canon = "agents propose" in _read(REPO / "CLAUDE.md").lower()
    return {"status": PASS if (boundaries and dhx and canon) else FAIL,
            "evidence": {"AGENT_BOUNDARIES.md": boundaries,
                         "dhx_propose_rule": dhx, "claude_md_agents_propose": canon}}


def prompt_cache_prefix(ctx) -> dict:
    """P11: prompt cache is a gate — prefix file, boundaries item, rail key."""
    doc = _read(REPO / "docs" / "PROMPT_CACHE.md")
    bounds = _read(REPO / "docs" / "AGENT_BOUNDARIES.md")
    prefix = _read(REPO / "work_orders" / "ccr" / "CREW" / "IN" / "PREFIX.md")
    rule = _read(REPO / "work_orders" / "ccr" / "CREW" / "IN" / "CACHE_RULE.md")
    rail = _read(REPO / "cosmos" / "cosmos_openrouter_rail.py")
    farm = _read(REPO / "work_orders" / "ccr" / "_propose_seat.py")
    ok = (
        "Static first, volatile last" in doc
        and "cached_tokens" in doc
        and "prompt cache prefix" in bounds.lower()
        and "CACHE PREFIX" in prefix
        and "policy:v1" in rule
        and "prompt_cache_key" in rail
        and "prompt_cache_key" in farm
        and "cached_tokens" in rail
    )
    return {"status": PASS if ok else FAIL,
            "evidence": {
                "PROMPT_CACHE.md": bool(doc),
                "boundaries_item_15": "prompt cache prefix" in bounds.lower(),
                "PREFIX.md": "CACHE PREFIX" in prefix,
                "CACHE_RULE.md": "policy:v1" in rule,
                "rail_prompt_cache_key": "prompt_cache_key" in rail,
                "farm_prompt_cache_key": "prompt_cache_key" in farm,
            }}


def pen_disables_other_writers(ctx) -> dict:
    """P12: pen grant → exclusive occupancy first, then write."""
    ccr = _read(REPO / "docs" / "CCR.md")
    bounds = _read(REPO / "docs" / "AGENT_BOUNDARIES.md")
    claude = _read(REPO / "CLAUDE.md")
    ok = (
        "DISABLE OTHER WRITERS FIRST" in ccr.upper()
        and "assert_pen" in ccr
        and "Pen grant disables other writers first" in bounds
        and "disable other writers first" in claude.lower()
    )
    return {"status": PASS if ok else FAIL,
            "evidence": {
                "ccr_first_acts": "DISABLE OTHER WRITERS FIRST" in ccr.upper(),
                "boundaries_18": "Pen grant disables other writers first" in bounds,
                "claude_md": "disable other writers first" in claude.lower(),
            }}


def gitur_then_judge(ctx) -> dict:
    """P13: do not go around Gitur; do not bypass the judge (WOMBAT SOP)."""
    ccr = _read(REPO / "docs" / "CCR.md")
    bounds = _read(REPO / "docs" / "AGENT_BOUNDARIES.md")
    claude = _read(REPO / "CLAUDE.md")
    ok = (
        "Do not go around Gitur" in bounds
        and "bypass the judge" in bounds.lower()
        and "save for the judge" in bounds.lower()
        and "rerun on the hot cache" in bounds.lower()
        and "Do not bypass the judge" in ccr
        and "saved for the judge" in claude.lower()
    )
    return {"status": PASS if ok else FAIL,
            "evidence": {
                "boundaries_19": "Do not go around Gitur" in bounds,
                "wombat_save": "save for the judge" in bounds.lower(),
                "wombat_rerun": "rerun on the hot cache" in bounds.lower(),
                "ccr": "Do not bypass the judge" in ccr,
                "claude_md": "saved for the judge" in claude.lower(),
            }}


CHECKS = {
    "activity_clock_15s": activity_clock_15s,
    "orchestrator_only": orchestrator_only,
    "agents_propose_only": agents_propose_only,
    "pause_formal": pause_formal,
    "resume_gate": resume_gate,
    "no_bts_imports": no_bts_imports,
    "anti_loss_daemons": anti_loss_daemons,
    "self_build_process": self_build_process,
    "keep_afloat": keep_afloat,
    "improvement_not_bloat": improvement_not_bloat,
    "prompt_cache_prefix": prompt_cache_prefix,
    "pen_disables_other_writers": pen_disables_other_writers,
    "gitur_then_judge": gitur_then_judge,
}


def audit(root: Path, only: str | None = None) -> dict:
    doc = load()
    ctx = {"root": Path(root), "repo": REPO, "pkg": PKG,
           "wd2": PKG / "cosmos_watchdog2.py"}
    results = []
    for pr in doc.get("principle", []):
        if only and pr["id"] != only and pr["name"] != only:
            continue
        chk = pr.get("check")
        fn = CHECKS.get(chk)
        row = {"id": pr["id"], "name": pr["name"], "check": chk,
               "severity": pr.get("severity"),
               "canon_files": _canon_files_exist(pr)}
        # meta: a principle with no implemented check is NOT encoded as a gate
        if fn is None:
            row["status"] = FAIL
            row["evidence"] = {"error": "no executable check implemented"}
        else:
            try:
                r = fn(ctx)
                row["status"] = r["status"]
                row["evidence"] = r["evidence"]
            except Exception as e:  # noqa: BLE001
                row["status"] = FAIL
                row["evidence"] = {"exception": f"{type(e).__name__}: {e}"}
        # a cited canon file that does not exist breaks the encoding claim
        if any(v is False for v in row["canon_files"].values()):
            row.setdefault("evidence", {})["missing_canon"] = [
                k for k, v in row["canon_files"].items() if v is False]
            if row["status"] == PASS:
                row["status"] = FAIL
        results.append(row)
    n = len(results)
    passed = sum(1 for r in results if r["status"] == PASS)
    watch = sum(1 for r in results if r["status"] == "WATCH")
    unproven = sum(1 for r in results if r["status"] == UNPROVEN)
    failed = sum(1 for r in results if r["status"] == FAIL)
    return {
        "schema": doc.get("schema"), "ratified": doc.get("ratified"),
        "audited_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "root": str(root), "toml": str(TOML),
        "counts": {"principles": n, "PASS": passed, "WATCH": watch,
                   "UNPROVEN": unproven, "FAIL": failed},
        "all_encoded": failed == 0,
        "results": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_principles")
    ap.add_argument("--root", default=str(REPO / "live"))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--check", default=None, help="one principle id or name")
    a = ap.parse_args()
    if a.list:
        doc = load()
        for pr in doc.get("principle", []):
            print(f"{pr['id']}  {pr['name']:<26} check={pr.get('check')}")
            print(f"      {pr['statement']}")
        return 0
    if a.audit or a.check:
        out = audit(Path(a.root), only=a.check)
        print(json.dumps(out, indent=1, default=str))
        return 0 if out["all_encoded"] else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
