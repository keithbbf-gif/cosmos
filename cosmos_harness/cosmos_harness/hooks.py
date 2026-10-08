"""Eight hooks. The order is the control flow.

The model is sampled in between these hooks. It does not choose which hook
runs, and it does not clear a hook that already refused. That is the
deterministic 95 percent: given the same stack, the same tool arguments, and
the same oracle and checker rows, these functions return the same decision.

The remaining input is the model sample itself. It enters only as text and
tool-call arguments, and the next hook either accepts those arguments or
latches.

=====  ============  =========================================================
Order  Hook          When it runs
=====  ============  =========================================================
1      prompt_in     Before any sample. Task shape, no pointer, no live root.
2      prompt_bound  Eight layers present. Pin locked. Wrapper is system.
3      pre_tool      One hand, one path, oracle already red for a mutation.
4      post_tool     The hand result is the record. A refusal latches.
5      stop          No tool debt. A held latch does not sample again.
6      seat_scar     One provider observation. One SOP from the G47 table.
7      verify        Post-oracle is green. The four checker rows are PASS.
8      done          The five bundle hashes are present. Prose is not done.
=====  ============  =========================================================

Claude Code clears a compaction latch and loops. These hooks do not.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_harness.layers import HANDS, LAYER_NAMES, PLAN_HANDS, Stack
from cosmos_harness.refuse import Refuse

HOOK_ORDER = (
    "prompt_in",
    "prompt_bound",
    "pre_tool",
    "post_tool",
    "stop",
    "seat_scar",
    "verify",
    "done",
)


@dataclass(frozen=True)
class Decision:
    """``allow`` false means the loop latches or halts. ``reason`` is the token."""

    hook: str
    allow: bool
    reason: str


def prompt_in(stack: Stack) -> Decision:
    """Refuse an empty mission, a pointer, or a live root. The stack is already bound."""
    if not stack.task.strip():
        return Decision("prompt_in", False, "PACK_INCOMPLETE")
    if stack.where.name.lower() == "live":
        return Decision("prompt_in", False, "LIVE_TREE")
    return Decision("prompt_in", True, "task")


# Doors the loop may sample. grok is absent: grok.exe is not a worker.
SEAT_DOORS = frozenset({
    "cosmos-harness",
    "codex",
    "pi",
    "opencode",
    "dsh",
    "claude",
    "copilot",
})


def prompt_bound(stack: Stack) -> Decision:
    """The eight layers have languages and the pin is a door this loop can sample."""
    if len(LAYER_NAMES) != 8:
        return Decision("prompt_bound", False, "PACK")
    if stack.door not in SEAT_DOORS:
        return Decision("prompt_bound", False, "DOOR")
    if not stack.model or not stack.wrap or not stack.first_line:
        return Decision("prompt_bound", False, "PACK_INCOMPLETE")
    return Decision("prompt_bound", True, stack.model)


def pre_tool(name: str, *, mode: str, oracle_red: bool) -> Decision:
    """Refuse a hand the host does not own, a plan-mode edit, or an edit before red."""
    if name not in HANDS:
        return Decision("pre_tool", False, "NOT_A_HAND")
    if mode == "plan" and name not in PLAN_HANDS:
        return Decision("pre_tool", False, "PLAN_MODE")
    if name in {"edit", "write", "archive"} and not oracle_red:
        return Decision("pre_tool", False, "ORACLE_NOT_RED")
    return Decision("pre_tool", True, name)


def post_tool(ok: bool, reason: str = "") -> Decision:
    """A failed hand is the latch. The next sample does not run."""
    if not ok:
        return Decision("post_tool", False, reason or "HAND_FAIL")
    return Decision("post_tool", True, "recorded")


def stop(*, debt: int, latch: bool, sop_applied: bool) -> Decision:
    """Stop is a gate. Debt, a latch, or a seating SOP already used ends the loop."""
    if latch:
        return Decision("stop", False, "HALT_GUARD_HELD")
    if debt != 0:
        return Decision("stop", False, "ORPHANED_DEBT")
    if sop_applied:
        return Decision("stop", False, "SOP_HELD")
    return Decision("stop", True, "turn_closed")


def seat_scar(*, again: bool, sop: str) -> Decision:
    """The seating table already chose the one SOP. This hook only admits it.

    ``again`` false means the table said stop. The hook does not invent a
    second method. ``again`` true is the one confirming call, and the caller
    must record ``sop`` on ``applied`` before that call returns.
    """
    if not sop:
        return Decision("seat_scar", False, "UNMAPPED")
    if not again:
        return Decision("seat_scar", False, sop)
    return Decision("seat_scar", True, sop)


def verify(*, oracle_green: bool, checks: tuple[str, ...]) -> Decision:
    """Generation is over. The oracle passed and each of the four rows is PASS.

    Any other status blocks. The reason is that status. A row list that is
    not the four checkers blocks with ``CHECKS`` when every present token is
    already ``PASS``.
    """
    if not oracle_green:
        return Decision("verify", False, "ORACLE_STILL_RED")
    blocked = [item for item in checks if item != "PASS"]
    if len(checks) != 4 or blocked:
        return Decision("verify", False, blocked[0] if blocked else "CHECKS")
    return Decision("verify", True, "verified")


def done(fields: dict[str, str]) -> Decision:
    """Five hashes, all non-empty. A missing field is not a bundle."""
    required = ("diff_hash", "oracle_id", "oracle_log_hash", "pack_hash", "cmd_hash")
    missing = [name for name in required if not str(fields.get(name, "")).strip()]
    if missing:
        return Decision("done", False, "INCOMPLETE_BUNDLE")
    return Decision("done", True, "bundle")


def require(decision: Decision) -> Decision:
    """Raise when a hook that must pass at the door has refused."""
    if not decision.allow:
        raise Refuse(decision.reason, decision.hook)
    return decision
