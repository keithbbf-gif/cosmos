"""One propose path. G47 builds the call. This module does not start a provider.

A nontrivial edit needs a red oracle and a plan that names a symbol the hunk
touches. Done still requires a DoneBundle. live/ is not a worktree.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from g47.contracts import Legend
from g47.refuse import Refuse
from g47.summon import plan

from cosmos_code.checks4 import fails_of, run_code_checks
from cosmos_code.doorspec import load_all, negotiate
from cosmos_code.quality.ladder import ladder_from_rows
from cosmos_code.safety.pathjail import PathJail
from cosmos_code.session_log import SessionLog
from cosmos_code.tools.fs import JailedFS
from cosmos_code.verify.oracle import OracleGate, OracleSpec


class Provider:
    """The seam a real door would implement. This package ships no caller."""

    def prepare_call(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise Refuse("DISPATCH_LOCKED", "no provider is bound")

    def normalize_tools(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return []

    def fold_usage(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {"cached_tokens": 0, "out_tokens": 0}


def _live(path: Path) -> None:
    text = str(path.resolve()).replace("\\", "/").lower()
    if text.rstrip("/").endswith("/live") or "/live/" in text:
        raise Refuse("LIVE_TREE", text)


def require_ir(log: SessionLog) -> None:
    if not log.has("oracle/red") or not log.has("plan/bound"):
        raise Refuse("NO_SHOT1_IR", "draft has no red oracle and no bound plan")


def dispatch(log: SessionLog, provider: Provider, payload: dict[str, Any]) -> dict[str, Any]:
    """The model call. Refuses without Shot-1, then stays locked (no HTTP)."""
    require_ir(log)
    log.append({"ev": "assistant/attempt", "note": "dispatch refused before HTTP"})
    return provider.prepare_call(payload)


def _symbols_hit(symbols: list[str], files: dict[str, str]) -> None:
    if not symbols:
        raise Refuse("NO_SHOT1_IR", "plan names no symbols")
    blob = "\n".join(files.values())
    if not any(symbol in blob for symbol in symbols):
        raise Refuse("PLAN_UNBOUND", "hunks do not intersect the plan")


def propose(
    legend: Legend,
    door: str,
    worktree: Path,
    *,
    wo: dict[str, Any] | None = None,
    files: dict[str, str] | None = None,
    symbols: list[str] | None = None,
    order_id: str = "local",
) -> dict[str, Any]:
    root = worktree.resolve()
    _live(root)
    root.mkdir(parents=True, exist_ok=True)
    specs = load_all()
    if door not in specs:
        raise Refuse("UNKNOWN_DOOR", door)
    spec = negotiate(specs[door])
    log = SessionLog(root / "session.jsonl")
    log.append({"ev": "session/start", "door": spec.id, "model": legend.model})
    gate = OracleGate(root)
    oracle: OracleSpec | None = None
    nontrivial = bool(wo and wo.get("nontrivial"))
    if nontrivial:
        if not wo or "oracle" not in wo:
            raise Refuse("NO_ORACLE_SPEC", door)
        oracle = OracleSpec.from_mapping(wo["oracle"])
        pre = gate.assert_fail_pre(oracle)
        log.append({"ev": "oracle/red", "oracle_id": oracle.oracle_id, "log_hash": pre.log_hash})
    if files:
        if oracle is None:
            raise Refuse("NO_ORACLE_SPEC", "edit without a red oracle")
        _symbols_hit(list(symbols or []), files)
        log.append({"ev": "plan/bound", "symbols": list(symbols or [])})
        require_ir(log)
        jail = PathJail(grants=[root])
        fs = JailedFS(jail, root, oracle_gate=gate)
        for name, body in files.items():
            fs.write(str(root / name), body, spec=oracle)
    built = plan(legend, door)
    log.append({"ev": "system/message", "bytes": built.system})
    log.append({"ev": "user/message", "bytes": built.user})
    rows: list[dict[str, Any]] = []
    if files:
        for name, body in files.items():
            if name.endswith(".py"):
                rows.extend(run_code_checks(root / "_checks", {"order_id": order_id, "_output_path": name}, body))
    return {
        "door": spec.id,
        "plan": built.to_json(),
        "done": False,
        "checks": rows,
        "blocked": [type(item).__name__ for item in ladder_from_rows(rows)],
        "fails": fails_of(rows),
        "session": str(root / "session.jsonl"),
    }
