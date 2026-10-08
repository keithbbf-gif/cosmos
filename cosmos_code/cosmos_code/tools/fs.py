"""Minimal jailed read/edit stubs — attempt workspace only; never live/."""

from __future__ import annotations

from pathlib import Path

from cosmos_code.safety.pathjail import PathJail
from cosmos_code.verify.oracle import OracleGate, OracleSpec


class LiveTreeWriteRefused(RuntimeError):
    pass


class JailedFS:
    def __init__(self, jail: PathJail, attempt_root: str | Path, oracle_gate: OracleGate | None = None):
        self.jail = jail
        self.attempt_root = Path(attempt_root)
        self.oracle_gate = oracle_gate

    def _refuse_live(self, path: Path) -> None:
        s = str(path).replace("\\", "/").lower()
        if "/live/" in s or s.rstrip("/").endswith("/live"):
            raise LiveTreeWriteRefused(f"CODE propose-only; never write live/: {path}")

    def read(self, raw: str) -> str:
        p = self.jail.resolve(raw)
        return p.read_text(encoding="utf-8")

    def write(self, raw: str, content: str, *, spec: OracleSpec | None = None) -> Path:
        if self.oracle_gate is not None:
            self.oracle_gate.allow_edit(spec)
        p = self.jail.resolve(raw)
        self._refuse_live(p)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def edit(self, raw: str, old: str, new: str, *, spec: OracleSpec | None = None) -> Path:
        if self.oracle_gate is not None:
            self.oracle_gate.allow_edit(spec)
        p = self.jail.resolve(raw)
        self._refuse_live(p)
        text = p.read_text(encoding="utf-8")
        if old not in text:
            raise ValueError(f"edit: old text not found in {raw}")
        if text.count(old) != 1:
            raise ValueError(f"edit: ambiguous match in {raw}")
        p.write_text(text.replace(old, new, 1), encoding="utf-8")
        return p
