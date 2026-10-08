"""Grade a reply against the output contract.

A python-opening test and a NONE-first contract cannot both be required.
Text and ping accept NONE first. Python accepts a code opening. A fence is a fail.
Worktree doors are not applied on mouth text alone.
"""

from __future__ import annotations

from dataclasses import dataclass

from g47.contracts import FIRST_LINE, OutputContract


@dataclass(frozen=True)
class Grade:
    mouth_ok: bool
    applied: bool
    reason: str
    # A ping can be mouth-correct and still not be a finished task.
    task_pass: bool = False


def _py_first(line: str) -> bool:
    return line.startswith(("```", "'''", "#", "import ", "from ", "def ", "class "))


def _fence(line: str) -> bool:
    return line.startswith("```")


def grade(
    mouth: str,
    contract: OutputContract,
    *,
    door_grade: str = "filed_text",
    worktree_obeyed: bool | None = None,
    served_model: str | None = None,
    expected_model: str | None = None,
    prefill_injected: bool = False,
) -> Grade:
    text = mouth.replace("\r\n", "\n").strip("\n")
    if not text.strip():
        return Grade(False, False, "EMPTY")
    lines = text.splitlines()
    # A prefill we wrote is not the model's first line. Grade what follows it.
    if prefill_injected and lines and lines[0].strip() == "NONE":
        lines = lines[1:]
        if not lines or not lines[0].strip():
            return Grade(False, False, "PREFILL_ONLY")
    first = lines[0].strip()
    if _fence(first):
        return Grade(False, False, "FENCE")

    if contract.ping:
        ok = (
            first == "NONE"
            and len(lines) >= 2
            and lines[1].strip().startswith("HERO_OK")
        )
        reason = "PING_OK" if ok else "PING_SHAPE"
        return _apply(ok, reason, door_grade, worktree_obeyed, task=False, served_model=served_model, expected_model=expected_model)

    if contract.what == "python":
        ok = _py_first(first) and not _fence(first)
        reason = "PYTHON_OK" if ok else "PYTHON_OPENING"
        return _apply(ok, reason, door_grade, worktree_obeyed, task=True, served_model=served_model, expected_model=expected_model)

    if contract.what == "no_prose":
        allowed = FIRST_LINE.get(contract.role, ())
        ok = first in allowed and len(lines) == 1
        reason = "RECORD_OK" if ok else "RECORD_SHAPE"
        return _apply(ok, reason, door_grade, worktree_obeyed, task=True, served_model=served_model, expected_model=expected_model)

    allowed = FIRST_LINE.get(contract.role, ())
    ok = first in allowed
    reason = "TEXT_OK" if ok else "FIRST_LINE"
    return _apply(ok, reason, door_grade, worktree_obeyed, task=True, served_model=served_model, expected_model=expected_model)


def _sku(served_model: str | None, expected_model: str | None) -> str | None:
    if served_model is None and expected_model is None:
        return None
    served = (served_model or "").strip()
    if served in {"", "None", "null"}:
        return "SKU_UNBOUND"
    if expected_model:
        want = expected_model.removeprefix("openrouter/").strip()
        got = served.removeprefix("openrouter/").strip()
        if got != want:
            return "SKU_MISMATCH"
    return None


def _apply(
    ok: bool,
    reason: str,
    door_grade: str,
    worktree_obeyed: bool | None,
    *,
    task: bool,
    served_model: str | None,
    expected_model: str | None,
) -> Grade:
    if not ok:
        return Grade(False, False, reason, False)
    sku = _sku(served_model, expected_model)
    if sku:
        return Grade(True, False, sku, False)
    if door_grade == "filed_text":
        return Grade(True, True, reason, task)
    if worktree_obeyed is True:
        return Grade(True, True, reason, task)
    return Grade(True, False, "NEED_WORKTREE", False)
