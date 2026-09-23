#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WOMB HERO runner. Blueprint JSON → terminal.

Layer 7: cd + wallet env only. No CLI strings from L7.
Layer 3: harness command (the execution vector).
Layer 2: model switch.
Layer 4: wrapper file copied into cwd as system instruction (GEMINI.md / AGENTS.md).
Layer 4-adjacent: COSMOS_KB ACTIVE scars for this seat appended to the mission
    (kb_hazards(); read-only DB open; fail-open on KB outage; cap 12 rows).
Layer 6: allow/forbid (printed; enforced by harness policy where the CLI supports it).
Layer 8: mission text as the runtime prompt (extracted; not @file::json.path).

    py -3.14 work_orders\\ccr\\run_work_order.py --wo V:\\abs\\wo.json [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


KB_DB = Path(os.environ.get(
    "COSMOS_KB_DB", r"V:\A\Ai\COSMOS\live\state\cosmos_kb.db"))
# Cap is a runaway guard, not a routine cut: the ACTIVE set is DEFINED as
# live hazards every spawn must see. Audit 2026-09-21: cap 12 silently
# dropped SEPT-05..12 (incl. JUDGE_EMPTY, ASIS_RETRY) for matched seats.
KB_MAX_ROWS = 24
KB_SYMPTOM_CHARS = 300
KB_FIX_CHARS = 200


def kb_hazards(model: str, role: str) -> str:
    """LIVE HAZARDS block: ACTIVE KB scars for this seat + system scope.

    Read-only open (mode=ro URI — this query can never write). Fail-open:
    any KB problem returns "" with a stderr WARN; the spawn's fail-closed
    rules (Role/Model/Harness/Enviro) are untouched. Seat match is a
    case-insensitive substring in either direction so provider prefixes
    (openrouter/, google/, z-ai/) never break the join.
    """
    try:
        con = sqlite3.connect(f"file:{KB_DB}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT id, model_id, kind, symptom, corrective FROM scars "
            "WHERE status='ACTIVE' ORDER BY id").fetchall()
        con.close()
    except Exception as e:  # noqa: BLE001 — KB outage must not kill a spawn
        print(f"WARN: kb-hazards unreachable ({KB_DB}): {e}", file=sys.stderr)
        return ""
    m = (model or "").lower()
    # Relevance order (audit 2026-09-21): seat-match first, then universal
    # (model_id NULL — relevant to every seat), then other seats' rows last.
    # Id-ordering alone buried universal pipeline hazards (SEPT-05 JUDGE_EMPTY,
    # SEPT-07 ASIS_RETRY) below other seats' model quirks.
    seat, universal, other = [], [], []
    for r in rows:
        mid = (r["model_id"] or "").lower()
        if not mid:
            universal.append(r)
        elif bool(m) and (m in mid or mid in m):
            seat.append(r)
        else:
            other.append(r)
    picked = (seat + universal + other)[:KB_MAX_ROWS]
    if not picked:
        return ""
    lines = ["[LIVE HAZARDS — COSMOS_KB ACTIVE scars for "
             f"{role or '?'} / {model or '?'} — do not repeat these failures]"]
    for r in picked:
        sym = (r["symptom"] or "").replace("\n", " ")[:KB_SYMPTOM_CHARS]
        fix = (r["corrective"] or "").replace("\n", " ")[:KB_FIX_CHARS]
        lines.append(f"- {r['id']} {r['kind']}: {sym}"
                     + (f" | Fix: {fix}" if fix else ""))
    return "\n".join(lines)


def load_wo(path: Path) -> dict:
    rec = json.loads(path.read_text(encoding="utf-8"))
    if "legend" not in rec or "tail" not in rec:
        raise SystemExit("ERROR: blueprint needs legend + tail")
    return rec


def run(wo_path: Path, dry_run: bool) -> int:
    rec = load_wo(wo_path)
    cosmos_dir = Path(__file__).resolve().parents[2] / "cosmos"
    if str(cosmos_dir) not in sys.path:
        sys.path.insert(0, str(cosmos_dir))
    from cosmos_duds import DudsError, require_duds
    try:
        duds = require_duds(rec, repo=cosmos_dir.parent)
    except DudsError as e:
        print(f"ERROR: {e.kind}: {e.detail}", file=sys.stderr)
        return 2
    legend = rec["legend"]
    tail = rec["tail"]
    env7 = legend.get("l7_environment") or {}
    cwd = Path(env7.get("cwd") or "")
    model = str(legend.get("l2_model") or "")
    harness = str(legend.get("l3_harness") or "")
    wrapper = Path(str(legend.get("l4_wrapper_path") or ""))
    mission = str(tail.get("l8_mission") or "")
    allow = legend.get("l6_tools", {}).get("allow") or []
    forbid = legend.get("l6_tools", {}).get("forbid") or []
    wallet = str(env7.get("wallet_keys_vault") or env7.get("wallet") or "")

    if not cwd.is_dir():
        print(f"ERROR: L7 cwd missing: {cwd}", file=sys.stderr)
        return 1
    (cwd / "_womb_spawn.json").write_text(json.dumps({
        "action": "watch_spawn",
        "role": duds["l1_role"],
        "model": duds["l2_model"],
        "harness": duds["l3_harness"],
    }, indent=1), encoding="utf-8")
    print(f"Role: {legend.get('l1_role')}")
    print(f"Model: {model}")
    print(f"cwd: {cwd}")
    print(f"Harness: {harness}")
    print(f"allow: {allow}")
    print(f"forbid: {forbid}")

    # KB LIVE HAZARDS (L4-adjacent): ACTIVE scars for this seat ride the
    # mission so every HERO inherits the scars without re-learning them.
    # One hook point — all five harness branches below consume `mission`.
    hazards = kb_hazards(model, str(legend.get("l1_role") or ""))
    if hazards:
        print(f"kb-hazards: {hazards.count(chr(10))} rows injected")
        mission = mission + "\n\n" + hazards
    else:
        print("kb-hazards: none (KB unreachable or no ACTIVE rows)")

    os.chdir(cwd)

    if wrapper.is_file():
        # Gemini CLI hydrates system instruction from GEMINI.md; Pi/OpenCode from AGENTS.md.
        shutil.copy(wrapper, cwd / "GEMINI.md")
        shutil.copy(wrapper, cwd / "AGENTS.md")

    # Wallet: set env from a key *file* without printing the secret.
    wallet_p = Path(wallet) if wallet else None
    extra_env = os.environ.copy()
    if wallet_p and wallet_p.is_file():
        key = wallet_p.read_text(encoding="utf-8").strip()
        extra_env["OPENROUTER_API_KEY"] = extra_env.get("OPENROUTER_API_KEY") or key
        extra_env["GEMINI_API_KEY"] = extra_env.get("GEMINI_API_KEY") or key
        extra_env["DEEPSEEK_API_KEY"] = extra_env.get("DEEPSEEK_API_KEY") or key
    base_url = str(env7.get("deepseek_base_url") or "")
    if base_url:
        extra_env["DEEPSEEK_BASE_URL"] = base_url
    dsh_home = str(env7.get("dsh_home") or "")
    if dsh_home:
        extra_env["DSH_HOME"] = dsh_home
    dsh_model = str(env7.get("dsh_model") or "")
    if dsh_model:
        extra_env["DSH_MODEL"] = dsh_model
    opencode_config = str(env7.get("opencode_config") or "")
    if opencode_config:
        extra_env["OPENCODE_CONFIG"] = opencode_config
        extra_env["OPENCODE_CONFIG_DIR"] = str(Path(opencode_config).parent)

    argv: list[str]
    h = harness.strip().lower()
    if h.startswith("gemini") or model.startswith("gemini"):
        argv = ["gemini.cmd", "--model", model, "--prompt", mission, "--approval-mode", "plan"]
    elif h.startswith("pi"):
        argv = ["pi.cmd", "-p", "--provider", "openrouter", "--model", model, "--", mission]
    elif h.startswith("opencode") or "opencode" in h:
        oc_model = model if model.startswith("openrouter/") else (
            f"openrouter/{model}" if "/" in model else model
        )
        # Keep the argv prompt short; L8 lives in TASK.md in cwd (OpenCode drops long -- tails).
        (cwd / "TASK.md").write_text(mission, encoding="utf-8")
        argv = [
            "opencode.cmd", "run", "--dir", str(cwd), "-m", oc_model,
            "--format", "default", "--",
            "Read AGENTS.md and TASK.md in this directory. Complete TASK.md. Stay in this directory.",
        ]
    elif h.startswith("dsh"):
        extra_env.setdefault("DSH_MODEL", extra_env.get("DSH_MODEL") or "deepseek-v4-flash")
        (cwd / "TASK.md").write_text(mission, encoding="utf-8")
        argv = [
            "dsh.cmd", "--profile", "headless",
            "Read AGENTS.md and TASK.md in this directory. Complete TASK.md. Stay in this directory.",
        ]
    elif h.startswith("codex"):
        argv = [
            "codex.cmd", "exec",
            "--ignore-user-config", "--skip-git-repo-check",
            "--sandbox", "read-only", "-m", model, "--", mission,
        ]
    else:
        print(f"ERROR: unknown L3 harness: {harness}", file=sys.stderr)
        return 2

    print("exec:", argv[0], argv[1:4], "...")
    if dry_run:
        print("dry-run: not spawning")
        return 0
    proc = subprocess.run(argv, env=extra_env, cwd=str(cwd))
    return int(proc.returncode or 0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wo", required=True, help="absolute path to blueprint JSON")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    return run(Path(a.wo), a.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
