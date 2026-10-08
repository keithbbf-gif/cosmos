"""The eight HERO layers, each in the language that layer actually is.

===========  ==========  =====================================================
Layer        Language    What the file is
===========  ==========  =====================================================
l1_role      Markdown    Role and the first line the caller already named.
l2_model     TOML        The pin. No fallback model. No ``:floor`` on ``:free``.
l3_harness   Python      This package. The hook order and the turn cap.
l4_wrapper   Markdown    System text. Style does not go here.
l5_skills    Markdown    Dormant until named. Default body is ``none extra``.
l6_tools     JSON        The hand schemas the host executes. Delete is absent.
l7_enviro    C + Python  Win32 job source, plus the path jail that gates it.
l8_mission   Markdown    The task. The oracle argv sits beside it, not inside it.
===========  ==========  =====================================================

The first-line table is the one ``g47.contracts.FIRST_LINE`` already grades.
``HARNESS.md`` and ``CANON_SPAWN.md`` still disagree. This module does not
invent a third table. A role in the G47 table must use one of its lines.
A role outside that table is refused.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from cosmos_harness.refuse import Refuse

_G47 = Path(__file__).resolve().parents[2] / "harness" / "G47"
if str(_G47) not in sys.path:
    sys.path.insert(0, str(_G47))

from g47.contracts import FIRST_LINE, KIND  # noqa: E402

LAYER_LANGUAGE = {
    "l1_role": "markdown",
    "l2_model": "toml",
    "l3_harness": "python",
    "l4_wrapper": "markdown",
    "l5_skills": "markdown",
    "l6_tools": "json",
    "l7_enviro": "c",
    "l8_mission": "markdown",
}

LAYER_NAMES = tuple(LAYER_LANGUAGE)

# The seated pack law. Turn cap 8 is the budget. It is not a model choice.
TURN_CAP = 8

HANDS = (
    "read",
    "glob",
    "grep",
    "edit",
    "write",
    "archive",
    "oracle",
    "worktree",
)

# Plan mode may look. It may not change the tree.
PLAN_HANDS = frozenset({"read", "glob", "grep", "oracle"})

_SECRET = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
_SHELLS = frozenset({"cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe", "bash", "sh", "sh.exe"})


@dataclass(frozen=True)
class Stack:
    """One attempt. Every field is already decided before the model is sampled.

    ``mode`` is ``plan`` or ``act``. The model does not flip it. ``oracle_argv``
    is a real argument vector. A shell string is refused.
    """

    role: str
    model: str
    what: str
    first_line: str
    wrap: str
    style: str
    skills: tuple[str, ...]
    where: Path
    task: str
    oracle_argv: tuple[str, ...]
    door: str = "cosmos-harness"
    mode: str = "act"

    def contract_line(self) -> str:
        """The one line the user message carries. Style is not in it.

        ``first_line`` is the role's allowed set from ``FIRST_LINE``. The
        bind token is one member of that set. It is not an order to echo it.
        """
        allowed = FIRST_LINE.get(self.role, (self.first_line,))
        return (
            f"CONTRACT role={self.role} what={self.what} "
            f"first_line={'|'.join(allowed)} model={self.model}"
        )


def _live(path: Path) -> bool:
    parts = [part.lower() for part in path.parts]
    return "live" in parts and parts[-1] == "live"


def bind(stack: Stack) -> Stack:
    """Refuse an unbound stack. Return the stack with skills defaulted.

    Refuses
    -------
    UNKNOWN_ROLE, FIRST_LINE, WHAT, EMPTY_PIN, NOT_A_PIN, FLOOR_ON_FREE,
    FALLBACK_MODEL, LIVE_TREE, WHERE, PACK_INCOMPLETE, MODE, SHELL_ORACLE,
    GROK_NOT_A_WORKER.
    """
    if stack.role not in KIND:
        raise Refuse("UNKNOWN_ROLE", stack.role)
    allowed = FIRST_LINE.get(stack.role)
    if allowed is None or stack.first_line not in allowed:
        raise Refuse("FIRST_LINE", f"{stack.role} {stack.first_line}")
    if stack.what not in ("text", "python", "no_prose"):
        raise Refuse("WHAT", stack.what)
    pin = stack.model.strip()
    low = pin.lower()
    if not pin:
        raise Refuse("EMPTY_PIN", "l2_model")
    if low in {"openrouter/free", "free", ":free"} or low.endswith("/free"):
        raise Refuse("NOT_A_PIN", pin)
    if ":free" in low and ":floor" in low:
        raise Refuse("FLOOR_ON_FREE", pin)
    if "fallback" in low:
        raise Refuse("FALLBACK_MODEL", pin)
    if stack.mode not in {"plan", "act"}:
        raise Refuse("MODE", stack.mode)
    if not stack.where:
        raise Refuse("WHERE", "l7_enviro")
    root = Path(stack.where)
    if not root.is_dir():
        raise Refuse("WHERE", str(root))
    resolved = root.resolve()
    if _live(resolved):
        raise Refuse("LIVE_TREE", str(resolved))
    if not stack.task.strip():
        raise Refuse("PACK_INCOMPLETE", "l8_mission")
    if "see docs/" in stack.task.lower() or "<pointer>" in stack.task.lower():
        raise Refuse("POINTER_IN_TASK", "l8_mission")
    if not stack.wrap.strip():
        raise Refuse("PACK_INCOMPLETE", "l4_wrapper")
    if not stack.oracle_argv:
        raise Refuse("PACK_INCOMPLETE", "oracle")
    exe = Path(stack.oracle_argv[0]).name.lower()
    if exe in _SHELLS:
        raise Refuse("SHELL_ORACLE", exe)
    if "grok.exe" in " ".join(stack.oracle_argv).lower():
        raise Refuse("GROK_NOT_A_WORKER", "oracle")
    skills = stack.skills or ("none extra",)
    return Stack(
        role=stack.role,
        model=pin,
        what=stack.what,
        first_line=stack.first_line,
        wrap=stack.wrap.strip(),
        style=stack.style.strip(),
        skills=tuple(skills),
        where=resolved,
        task=stack.task.strip(),
        oracle_argv=tuple(stack.oracle_argv),
        door=stack.door,
        mode=stack.mode,
    )


def scrub_env(env: dict[str, str]) -> dict[str, str]:
    """Drop credential-shaped variables before a child process starts."""
    return {key: value for key, value in env.items() if not any(part in key.upper() for part in _SECRET)}
