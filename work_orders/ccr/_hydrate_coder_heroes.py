#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write missing HERO files into hero_coders/* from PACK.toml / DUD.toml.
Does not exec models. Does not spawn grok.exe.
"""
from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_coders")
WRAP_SRC = ROOT / "_CODER_WRAP.md"


def _load(d: Path) -> dict:
    for name in ("DUD.toml", "PACK.toml"):
        p = d / name
        if p.is_file():
            return tomllib.loads(p.read_bytes().decode("utf-8"))
    return {}


def _write(p: Path, text: str) -> bool:
    if p.is_file():
        return False
    p.write_text(text, encoding="utf-8", newline="\n")
    return True


def hydrate(d: Path) -> dict:
    rec = _load(d)
    leg = rec.get("legend") or {}
    role = str(leg.get("role") or "CODER")
    model = str(leg.get("model") or "")
    via = str(leg.get("harness_via") or "")
    wrote = []
    if _write(d / "WRAP.md", WRAP_SRC.read_text(encoding="utf-8") if WRAP_SRC.is_file() else "role = CODER\n"):
        wrote.append("WRAP.md")
    style = (
        f"# STYLES/{model or d.name}\nfamily = default\nmodel = {model}\n"
        "note = First line NONE or diff --git. No essay. No grok.exe.\n"
    )
    if _write(d / "STYLE.md", style):
        wrote.append("STYLE.md")
    skill = (
        "---\nname: none-extra\ndescription: No COSMOS SkillRegistry overlay this spawn.\n"
        "---\nNone extra. Do not activate COSMOS skills this spawn.\n"
    )
    if _write(d / "SKILL.md", skill):
        wrote.append("SKILL.md")
    agents = f"""# AGENTS.md — {role} {model}. No dates. No WO ids.

You are a HERO. Read WRAP.md STYLE.md SKILL.md TASK.md.

## 1 Role
{role}. First line NONE or diff --git. No pen. No merge. Not JUDGE. Not WOMBAT. Not CCR.

## 2 Model
{model}

## 3 Harness
{via}. Isolated worktree. Not extra grok.exe.

## 4 Wrapper
WRAP.md. What is the intent, and the best execution of this intent?

## 5 Skills
None extra.

## 6 Tools
Kind-gate coding worktree. Forbid git push, merge, grok.exe, USPTO.

## 7 Enviro
Isolated cwd. PREFIX stable. Mission in TASK.md.

## Context pointer
Small PREFIX. Need more context:
<pointer>path [read*]</pointer>
read_budget_tokens = min(0.15×window, remaining − 0.20×window).
Follow-on cache PREFIX = legend + pointed bytes + this prompt + this output.
"""
    if _write(d / "AGENTS.md", agents):
        wrote.append("AGENTS.md")
    task = (
        "# Mission ping\n\nReply with exactly two lines:\nNONE\n"
        f"HERO_OK {model}\n"
    )
    if _write(d / "TASK.md", task):
        wrote.append("TASK.md")
    return {"dir": d.name, "model": model, "via": via, "wrote": wrote}


def main() -> int:
    rows = []
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name != "skills"):
        if not ((d / "DUD.toml").is_file() or (d / "PACK.toml").is_file()):
            continue
        rows.append(hydrate(d))
    print(json.dumps({"ok": True, "n": len(rows), "rows": rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
