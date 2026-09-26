#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One coding-harness contract for every HERO door.

Claude Code and these packs are the same kind of harness: a loop, a tool
pool, a permission gate, a worktree. They are not the same binary. This
module is the join. COSMOS CODE (PathJail, hooks-as-law) is the standalone
safety half. Each door binds the eight layers in that door's own way.

Do not import leaked Claude Code source. Do not start grok.exe.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CODE_ROOT = Path(r"V:\A\COSMOS_Harness\code\cosmos_code_scaffold")

# Read from the v2.1.88 TypeScript (query.ts, bashPermissions.ts, yoloClassifier.ts).
# Do not port these. The mistakes are the reason this module stays small.
DO_NOT_PORT = {
    "query.ts while(true)": "1729 lines of continue-sites. A reset of hasAttemptedReactiveCompact looped compact → error → stop-hook → compact and burned thousands of calls. Cap the loop. Never clear the already-failed guard.",
    "fallbackModel": "On FallbackTriggeredError the loop assigns currentModel = fallbackModel and retries the same turn. A named pin does not change under the caller.",
    "bashPermissions cap 50": "Over 50 subcommands returns ask, not deny. splitCommand strips redirects, so per-subcommand checks miss them. Two parsers. Do not parse bash to decide safety.",
    "yoloClassifier fast allow": "Stage 1 allow returns immediately and skips the thinking stage. A second model is not the fence. Unparseable must deny. Allow-on-fast-path must not exist.",
    "npm 2.1.88 source map": "Not a breach. Bun emits a source map by default. *.map was missing from .npmignore, so cli.js.map (sourcesContent = the TypeScript) shipped on the public registry. The map also pointed at a public R2 zip. 2.1.88 is no longer on the registry (2.1.87 and 2.1.89 are). Do not republish a map of the fence. Do not unpack their tree into this repo.",
}

# How each door puts the same contract on the wire. Not one JSON shape.
BIND = {
    "openrouter": {
        "loop": "system=WRAP, user=TASK, tools, tool-result",
        "tools": "allow-list only; write is the offered tool",
        "wrapper": "system turn is WRAP.md bytes; STYLE stays off",
        "skills": "SKILL.md on disk; not stuffed into system",
        "writes": "COSMOS CODE PathJail under the worktree",
        "grade": "after the call; HTTP ok is not applied",
    },
    "pi": {
        "loop": "pi.cmd -p; built-in tools; then read the worktree",
        "tools": "--tools read,write,edit; built-ins exist, so the flag is the pool",
        "wrapper": "--system-prompt is WRAP.md bytes when the pack has it",
        "skills": "not a second system sentence",
        "writes": "cwd is the worktree; grade reads files after the process exits",
        "grade": "mouth.txt is not the check",
    },
    "opencode": {
        "loop": "opencode run --dir worktree; built-in write",
        "tools": "built-in; do not pretend an outbound tools array is the pool",
        "wrapper": "AGENTS.md in the worktree (native load). Copy WRAP only if AGENTS.md is absent",
        "skills": "SKILL.md by name, not argv",
        "writes": "cwd/--dir is the worktree",
        "grade": "read the worktree after the process exits",
    },
    "dsh": {
        "loop": "dsh.cmd --profile headless when the key exists",
        "tools": "native via; unbound = do not invent a chat call",
        "wrapper": "same WRAP.md file",
        "skills": "none extra until accepted",
        "writes": "worktree only",
        "grade": "same applied rule",
    },
    "vertex": {
        "loop": "generateContent; no tools array was applied",
        "tools": "none; the caller files the reply",
        "wrapper": "prompt carries WRAP then TASK; do not claim a tools layer",
        "skills": "not a tools schema",
        "writes": "caller write through PathJail, not the model",
        "grade": "filed text, not a phantom tool call",
    },
    "codex": {
        "loop": "codex exec; Windows stamps read-only",
        "tools": "host harvest writes; do not claim the sandbox wrote the file",
        "wrapper": "isolated CODEX_HOME; no --ignore-user-config",
        "skills": "not this door until Keith opts in",
        "writes": "host harvest into the worktree, then PathJail",
        "grade": "same applied rule",
    },
    "cosmos-code": {
        "loop": "standalone coding harness; HERO doors call this half for jail and stop",
        "tools": "propose-only; CCr is the live pen",
        "wrapper": "does not replace WRAP.md",
        "skills": "hooks-as-law, not prompt advice",
        "writes": "PathJail + archive_only; never live/",
        "grade": "OracleSpec / DoneBundle when a work order has an oracle; sample pings use the reply-form grade",
    },
}


def _code():
    root = str(CODE_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    from cosmos_code.safety.pathjail import PathJail, PathJailError
    from cosmos_code.safety.hooks import install_defaults
    return PathJail, PathJailError, install_defaults


def system_for(pack: Path) -> str:
    """Wrapper bytes. Empty if the pack has no WRAP.md."""
    p = pack / "WRAP.md"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def mission_for(pack: Path) -> str:
    p = pack / "TASK.md"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def bind_native(pack: Path, kind: str) -> dict:
    """Record which door ran, and give OpenCode a wrapper file it will load."""
    if kind not in BIND:
        raise SystemExit("REFUSED unknown harness " + kind)
    pack.mkdir(parents=True, exist_ok=True)
    if kind == "opencode":
        agents = pack / "AGENTS.md"
        wrap = system_for(pack)
        if wrap and not agents.is_file():
            agents.write_text(wrap, encoding="utf-8", newline="\n")
    rec = {"kind": kind, "bind": BIND[kind], "has_wrap": bool(system_for(pack)), "has_task": bool(mission_for(pack))}
    (pack / "bind.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def jail_write(pack: Path, name: str, content: str) -> Path:
    """Write one file inside the worktree. COSMOS CODE PathJail is the fence."""
    PathJail, PathJailError, install_defaults = _code()
    raw = str(name or "").replace("\\", "/").strip()
    decision = install_defaults().pre("write", {"path": raw, "content": content})
    if decision.deny:
        raise PathJailError(raw, "hook:" + (decision.reason or "deny"))
    jail = PathJail(grants=[pack.resolve()])
    try:
        jail.check_shape(raw)
    except PathJailError:
        raise
    if not raw or raw.startswith("/") or ":" in raw:
        raise PathJailError(raw, "not_a_filename")
    dest = jail.resolve(str((pack / raw)))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8", newline="\n")
    return dest
