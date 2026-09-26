#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANON spawn layers. Fail-closed: no agent call without Role→Enviro applied.

CCr: copy to cosmos/cosmos_spawn.py. Hook work_order_run before any argv.
GET never mkdir. No grok.exe. Unique HEAD / GitHub: P10 propose until accepted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROLES = ("WOMBAT", "CODER", "JUDGE")
# daemon is not an LLM spawn
GROK_ARGV_SCAR = ("grok.exe", "grok --single", "--single")
CTX_CONCAT_SCAR = " · "


class SpawnError(Exception):
    def __init__(self, kind: str, detail: str = "") -> None:
        self.kind = kind
        super().__init__(detail or kind)


@dataclass
class SpawnSpec:
    role: str = ""
    model: str = ""
    wrapper: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    enviro: dict[str, Any] = field(default_factory=dict)

    def complete(self) -> bool:
        return bool(
            self.role in ROLES
            and self.model.strip()
            and self.wrapper
            and self.enviro.get("applied") is True
        )


def defaults(role: str, model: str, *, wrap_root: Path | None = None) -> SpawnSpec:
    role = (role or "CODER").upper()
    if role not in ROLES:
        raise SpawnError("NO_ROLE", role)
    model = (model or "").strip()
    if not model:
        raise SpawnError("NO_MODEL", "defaults require a model")
    root = wrap_root or Path(r"V:\A\Ai\COSMOS\work_orders\ccr\CREW\IN")
    wrap = [str(root / "WRAP" / (role + ".md"))]
    style = root / "STYLES" / (model.replace("/", "-").replace(":", "-") + ".md")
    if not style.is_file():
        style = root / "STYLES" / "_TEMPLATE.md"
    wrap.append(str(style))
    skills = {
        "WOMBAT": ["wombat-womb-board", "scar-empty-output"],
        "CODER": ["coder-propose-diff"],
        "JUDGE": ["judge-pair-ballot"],
    }[role]
    enviro = {
        "applied": True,
        "pack": "house",
        "budget_out_usd_per_m": 1.0,
        "need_resume": False,
        "no_grok_exe": True,
    }
    return SpawnSpec(role=role, model=model, wrapper=wrap, skills=skills,
                     tools=[], enviro=enviro)


def apply(role: str, model: str, **over: Any) -> SpawnSpec:
    spec = defaults(role, model, wrap_root=over.pop("wrap_root", None))
    if over.get("tools"):
        spec.tools = list(over["tools"])
    if over.get("skills"):
        spec.skills = list(over["skills"])
    spec.enviro.update(over.get("enviro") or {})
    spec.enviro["applied"] = True
    if not spec.complete():
        raise SpawnError("LAYERS_INCOMPLETE", spec.role)
    return spec


def refuse_grok_argv(argv: list[str] | str) -> None:
    blob = " ".join(argv) if isinstance(argv, list) else str(argv)
    low = blob.lower()
    if "grok.exe" in low or "grok --single" in low:
        raise SpawnError("GROK_EXE_SCAR", blob[:200])


def refuse_concat_ctx(ctx: Any) -> None:
    if isinstance(ctx, str) and CTX_CONCAT_SCAR in ctx:
        raise SpawnError("NO_CONTEXT", "Context source must be a list")
    if isinstance(ctx, str) and ctx.strip():
        raise SpawnError("NO_CONTEXT", "Context source must be a list")


def preflight_session(seed_exists: bool, bu_resume: bool) -> dict:
    return {"need_resume": bool(seed_exists or bu_resume), "applied": True}


def _selftest() -> None:
    n = 0
    s = apply("CODER", "z-ai/glm-5.3-flash")
    assert s.complete() and s.enviro["applied"]
    n += 1
    try:
        apply("DAEMON", "x")
        raise SystemExit("role")
    except SpawnError as e:
        assert e.kind == "NO_ROLE"
        n += 1
    try:
        refuse_grok_argv(["grok", "--single", "Drive MOTIF"])
        raise SystemExit("grok")
    except SpawnError as e:
        assert e.kind == "GROK_EXE_SCAR"
        n += 1
    try:
        refuse_concat_ctx("docs/A.md [read*] · docs/B.md [read*]")
        raise SystemExit("ctx")
    except SpawnError as e:
        assert e.kind == "NO_CONTEXT"
        n += 1
    pf = preflight_session(True, False)
    assert pf["need_resume"] is True
    n += 1
    print("spawn selftest %d/5" % n)


if __name__ == "__main__":
    _selftest()
