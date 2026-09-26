#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure HERO pack-applied on a WOMBAT Codex CALL.

Codex --json stream has no model field. --ephemeral drops the rollout, so SKU
stays UNMEASURED. This gate reads turn_context from the newest rollout that is
not older than last.txt, plus first line ITEM|NONE and the five pack files.

    py -3.14 work_orders\\ccr\\_wombat_pack_gate.py
    py -3.14 work_orders\\ccr\\_wombat_pack_gate.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

CCR = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
PACK_CWD = Path(r"V:\A\Ai\COSMOS\live\work\codex\hero-wombat-luna")
CODEX_HOME = PACK_CWD / ".codex-home"
LAST = CCR / "WOMBAT_LUNA_last.txt"
DEST = CCR / "WOMBAT_LUNA_pack.json"
PACK_FILES = ("AGENTS.md", "WRAP.md", "STYLE.md", "SKILL.md", "TASK.md")
HERO_SKILL_REL = Path(".agents") / "skills" / "wombat-womb-board" / "SKILL.md"
EXPECTED_MODEL = "openai/gpt-6-luna:floor"
EXPECTED_EFFORT = "max"
EXPECTED_PROVIDER = "openrouter"
# last.txt is written at exec end; rollout jsonl is created at session start.
# A MAX Flex turn is minutes, not 5s. Leftover rollouts are hours old.
STALE_S = 7200.0


class GateError(RuntimeError):
    pass


def _first_line(last: Path) -> str:
    if not last.is_file():
        return ""
    text = last.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        s = line.strip()
        if s:
            return s.split()[0]
    return ""


def newest_rollout(home: Path, *, expected_model: str | None = None) -> Path | None:
    """Prefer a recent rollout whose turn_context.model matches the HERO SKU.

    Isolated CODEX_HOME is also used by desktop Codex auto-review, which writes
    newer rollouts with model=codex-auto-review. Newest-mtime alone is wrong.
    """
    sess = home / "sessions"
    if not sess.is_dir():
        return None
    files = list(sess.rglob("rollout-*.jsonl"))
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if not expected_model:
        return files[0]
    for path in files[:40]:
        parsed = parse_rollout(path)
        if parsed.get("model") == expected_model:
            return path
    return files[0]


def parse_rollout(path: Path) -> dict:
    model = effort = cwd = provider = None
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            pl = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
            kind = rec.get("type")
            if kind == "session_meta":
                provider = pl.get("model_provider") or provider
                cwd = pl.get("cwd") or cwd
            elif kind == "turn_context":
                model = pl.get("model") or model
                effort = pl.get("effort") or effort
                cwd = pl.get("cwd") or cwd
    return {
        "model": model,
        "effort": effort,
        "cwd": cwd,
        "provider": provider,
        "rollout": str(path),
    }


def _norm(p: str | Path | None) -> str:
    if not p:
        return ""
    return str(Path(p)).rstrip("\\/").lower()


def gate(*, home: Path = CODEX_HOME, cwd: Path = PACK_CWD, last: Path = LAST,
         dest: Path | None = DEST) -> dict:
    missing = [n for n in PACK_FILES if not (cwd / n).is_file()]
    hero_skill = cwd / HERO_SKILL_REL
    hero_skill_added = hero_skill.is_file()
    system_dir = home / "skills" / ".system"
    system_skills = []
    if system_dir.is_dir():
        system_skills = [p.parent.name for p in system_dir.glob("*/SKILL.md")]
    codex_system_intact = bool(system_skills)
    replaced_system = (system_dir / "wombat-womb-board" / "SKILL.md").is_file()
    first = _first_line(last)
    line_ok = first in ("ITEM", "NONE")
    roll = newest_rollout(home, expected_model=EXPECTED_MODEL)
    parsed = parse_rollout(roll) if roll else {
        "model": None, "effort": None, "cwd": None, "provider": None, "rollout": None,
    }
    stale = False
    if roll and last.is_file():
        stale = roll.stat().st_mtime < (last.stat().st_mtime - STALE_S)
    sku = parsed.get("model")
    kind = "UNMEASURED" if (not sku or stale or not roll) else "MEASURED"
    sku_ok = (kind == "MEASURED") and sku == EXPECTED_MODEL
    effort_ok = parsed.get("effort") == EXPECTED_EFFORT
    provider_ok = (parsed.get("provider") or EXPECTED_PROVIDER) == EXPECTED_PROVIDER
    cwd_ok = (not parsed.get("cwd")) or _norm(parsed.get("cwd")) == _norm(cwd)
    ok = bool(
        sku_ok and effort_ok and line_ok and cwd_ok and provider_ok
        and not missing and hero_skill_added and not replaced_system
    )
    rec = {
        "ok": ok,
        "kind": kind,
        "first_line": first,
        "line_ok": line_ok,
        "sku": sku,
        "sku_ok": sku_ok,
        "effort": parsed.get("effort"),
        "effort_ok": effort_ok,
        "provider": parsed.get("provider"),
        "cwd": parsed.get("cwd"),
        "cwd_ok": cwd_ok,
        "pack_missing": missing,
        "hero_skill_added": hero_skill_added,
        "hero_skill": str(hero_skill),
        "codex_system_intact": codex_system_intact,
        "codex_system_skills": system_skills,
        "replaced_system": replaced_system,
        "rollout": parsed.get("rollout"),
        "stale_rollout": stale,
        "expected_model": EXPECTED_MODEL,
        "hero_pack": str(cwd),
    }
    if dest is not None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8", newline="\n")
    return rec


def _selftest() -> int:
    td = Path(tempfile.mkdtemp(prefix="wombat_pack_gate_"))
    cwd = td / "pack"
    home = cwd / ".codex-home"
    sess = home / "sessions" / "2026" / "09" / "24"
    sess.mkdir(parents=True)
    cwd.mkdir(exist_ok=True)
    for n in PACK_FILES:
        (cwd / n).write_text(n + "\n", encoding="utf-8")
    hero = cwd / ".agents" / "skills" / "wombat-womb-board"
    hero.mkdir(parents=True)
    (hero / "SKILL.md").write_text("---\nname: wombat-womb-board\n---\n", encoding="utf-8")
    sysd = home / "skills" / ".system" / "openai-docs"
    sysd.mkdir(parents=True)
    (sysd / "SKILL.md").write_text("system\n", encoding="utf-8")
    last = td / "last.txt"
    last.write_text("ITEM\n[]\n", encoding="utf-8")
    roll = sess / "rollout-ok.jsonl"
    rows = [
        {"type": "session_meta", "payload": {
            "model_provider": "openrouter", "cwd": str(cwd),
        }},
        {"type": "turn_context", "payload": {
            "model": EXPECTED_MODEL, "effort": "max", "cwd": str(cwd),
        }},
    ]
    roll.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    os.utime(roll, None)
    decoy = sess / "rollout-review.jsonl"
    decoy.write_text(json.dumps({
        "type": "turn_context",
        "payload": {"model": "codex-auto-review", "effort": "low", "cwd": str(cwd)},
    }) + "\n", encoding="utf-8")
    os.utime(decoy, (time.time() + 30, time.time() + 30))
    os.utime(last, None)
    good = gate(home=home, cwd=cwd, last=last, dest=td / "pack.json")
    assert good["ok"] is True, good
    assert good["kind"] == "MEASURED", good
    assert good["hero_skill_added"] is True, good
    assert good["replaced_system"] is False, good
    assert good["codex_system_intact"] is True, good
    bad_roll = sess / "rollout-ok.jsonl"
    rows[1]["payload"]["model"] = "openai/gpt-6-sol:floor"
    bad_roll.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    os.utime(bad_roll, None)
    os.utime(last, None)
    wrong = gate(home=home, cwd=cwd, last=last, dest=td / "pack-wrong.json")
    assert wrong["ok"] is False and wrong["sku_ok"] is False, wrong
    last.write_text("KEEP\n", encoding="utf-8")
    rows[1]["payload"]["model"] = EXPECTED_MODEL
    bad_roll.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    os.utime(bad_roll, None)
    os.utime(last, None)
    line = gate(home=home, cwd=cwd, last=last, dest=td / "pack-line.json")
    assert line["ok"] is False and line["line_ok"] is False, line
    last.write_text("ITEM\n", encoding="utf-8")
    now = time.time()
    os.utime(last, (now, now))
    os.utime(bad_roll, (now - STALE_S - 60, now - STALE_S - 60))
    stale = gate(home=home, cwd=cwd, last=last, dest=td / "pack-stale.json")
    assert stale["kind"] == "UNMEASURED" and stale["ok"] is False, stale
    print("wombat_pack_gate: --selftest 4/4", file=sys.stderr)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    rec = gate()
    print(json.dumps(rec, indent=1))
    if rec["kind"] == "UNMEASURED":
        return 2
    if rec.get("sku") and rec["sku"] != EXPECTED_MODEL:
        return 3
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
