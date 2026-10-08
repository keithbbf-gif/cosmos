"""Door table. Flags here were read from the cheat sheets or from Claude Code 2.1.88 main.tsx.

A door that is not seated refuses to execute. Recording its argv is not a seat.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Door:
    id: str
    family: str
    strength: str  # strong | weak | none
    seated: bool
    binary: tuple[str, ...]
    grade: str  # worktree | filed_text
    model_flag: tuple[str, ...] = ()
    prompt_flag: tuple[str, ...] = ()
    work_flag: tuple[str, ...] = ()
    extra: tuple[str, ...] = ()
    agents_file: str | None = None
    system_on_argv: bool = False
    forbid: tuple[str, ...] = ()
    keep_under: int | None = None
    turns: int = 1
    key_file: str | None = None
    note: str = ""


# Claude Code 2.1.88 is a steal-list. ANTHROPIC_OFF. The flags are real; the seat is not.
# Confirmed on main.tsx: -p/--print, --bare, --model, --tools, --permission-mode,
# --add-dir, --output-format, --max-turns, --fallback-model (forbidden here).

DOORS: dict[str, Door] = {
    "cosmos-code": Door(
        id="cosmos-code",
        family="cosmos",
        strength="strong",
        seated=True,
        binary=("python", "-m", "cosmos_code"),
        grade="worktree",
        extra=("propose",),
        agents_file=None,
        turns=8,
        note="Thin pack. Jail, hooks, and DoneBundle stay in the scaffold rail. This module does not start that loop.",
    ),
    "opencode": Door(
        id="opencode",
        family="opencode",
        strength="strong",
        seated=True,
        binary=("opencode.cmd", "run"),
        grade="worktree",
        model_flag=("-m",),
        work_flag=("--dir",),
        agents_file="AGENTS.md",
        turns=8,
        note="Model id is openrouter/<slug>. AGENTS.md is the wrapper. Do not also send a system prompt.",
    ),
    "pi": Door(
        id="pi",
        family="pi",
        strength="strong",
        seated=True,
        binary=("pi.cmd",),
        grade="worktree",
        model_flag=("--model",),
        prompt_flag=("-p",),
        extra=("--provider", "zai", "--tools", "read,write,edit", "--no-session"),
        system_on_argv=True,
        turns=8,
        note="Measured shape: pi.cmd -p --provider zai --model <sku> --tools read,write,edit --system-prompt <wrap> --no-session <item>. Not pi.ps1. Not ZCode. Not an OpenRouter GLM chat.",
    ),
    "dsh": Door(
        id="dsh",
        family="deepseek",
        strength="strong",
        seated=True,
        binary=("dsh.cmd", "--profile", "headless"),
        grade="worktree",
        agents_file="AGENTS.md",
        turns=8,
        key_file=r"V:\A\Ai\COSMOS\live\config\deepseek_api_key.txt",
        note="DeepSeek's harness is dsh, not a raw chat call. Missing key is NO_KEY. A named OpenRouter deepseek pin is a different seat, not a substitute for this binary.",
    ),
    "codex": Door(
        id="codex",
        family="openai",
        strength="strong",
        seated=True,
        binary=("codex", "exec"),
        grade="worktree",
        model_flag=("-m",),
        extra=("--skip-git-repo-check", "--json", "--color", "never", "--ephemeral"),
        agents_file="AGENTS.md",
        forbid=("--ignore-user-config", "--full-auto", "--danger-full-access"),
        turns=8,
        note="Isolated CODEX_HOME. Never --ignore-user-config. Judge/WOMBAT: --sandbox read-only, no --approve-for-me. Write jobs: --approve-for-me and no --sandbox. Windows still stamps read-only; host harvest writes. Stdin stays closed. Do not pass service_tier. OpenRouter pins set wire_api=responses on the argv. wire_api=chat is refused by this Codex.",
    ),
    "copilot": Door(
        id="copilot",
        family="github",
        strength="strong",
        seated=True,
        binary=("copilot.cmd",),
        grade="worktree",
        model_flag=("--model",),
        prompt_flag=("-p",),
        extra=("--allow-all-tools", "-s"),
        agents_file="AGENTS.md",
        turns=8,
        note="cwd is the worktree. --model names were unverified on 2026-09-29. -s returns the response only.",
    ),
    "grok": Door(
        id="grok",
        family="xai",
        strength="strong",
        seated=True,
        binary=("grok.exe",),
        grade="worktree",
        keep_under=200_000,
        forbid=("--single",),
        turns=4,
        note="Plan the pack. Do not execute. grok.exe as a CCrew worker is a refuse. Grok 4.6 BUILD is Gitur. Keep PREFIX+ITEM under 200k.",
    ),
    "openrouter": Door(
        id="openrouter",
        family="openrouter",
        strength="weak",
        seated=True,
        binary=(),
        grade="filed_text",
        turns=1,
        note="Named pin only. WRAP is the system turn. STYLE stays on the user tail. No tools array unless the rail applied one. HTTP 200 is not applied.",
    ),
    "vertex": Door(
        id="vertex",
        family="gemini",
        strength="weak",
        seated=True,
        binary=("gemini.cmd",),
        grade="filed_text",
        model_flag=("-m",),
        prompt_flag=("-p",),
        turns=1,
        forbid=("--harness",),
        note="No --harness on this gemini.cmd. generateContent had no tools array. Caller files the reply.",
    ),
    "claude": Door(
        id="claude",
        family="anthropic",
        strength="strong",
        seated=False,
        binary=("claude",),
        grade="worktree",
        model_flag=("--model",),
        prompt_flag=("-p",),
        work_flag=("--add-dir",),
        extra=(
            "--bare",
            "--output-format", "json",
            "--permission-mode", "default",
            "--tools", "Read,Edit,Write,Glob,Grep,Bash,PowerShell",
            "--max-turns", "8",
        ),
        system_on_argv=False,
        forbid=("--fallback-model", "--dangerously-skip-permissions"),
        turns=8,
        note="Steal-list from Claude Code 2.1.88. ANTHROPIC_OFF. --bare skips CLAUDE.md discovery. Do not pass --fallback-model. Unseated until Keith names it.",
    ),
    "hermes": Door(
        id="hermes",
        family="hermes",
        strength="none",
        seated=False,
        binary=("hermes",),
        grade="filed_text",
        turns=1,
        note="Not installed as a coder door. Credential pools use fill_first so a PREFIX stays on one key. ignore deepinfra. Not a fallback to Anthropic.",
    ),
    "antigravity": Door(
        id="antigravity",
        family="google",
        strength="strong",
        seated=False,
        binary=(),
        grade="worktree",
        agents_file="AGENTS.md",
        turns=4,
        note="SDK LocalAgentConfig or LocalOpenAIAgentConfig. IDE launcher is not an agent run. 401 until Google sign-in. Unseated.",
    ),
    "none": Door(
        id="none",
        family="mouth",
        strength="none",
        seated=False,
        binary=(),
        grade="filed_text",
        turns=1,
        note="Bare mouth. The pack carries the outfit. Do not claim a harness ran.",
    ),
}

ALIASES = {
    "deepseek": "dsh",
    "openai": "codex",
    "gemini": "vertex",
    "ling": "opencode",
    "glm": "pi",
}


def get_door(name: str) -> Door:
    key = ALIASES.get(name, name)
    if key not in DOORS:
        from g47.refuse import Refuse
        raise Refuse("UNKNOWN_DOOR", name)
    return DOORS[key]
