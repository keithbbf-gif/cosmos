"""Spend hook. This module does not keep a ledger or a balance.

Production composes the hook over Core ``SpendGate.guarded_call``, the same
way ``VoiceMode`` receives its asker. A deny leaves the session closed.
The phone and the plugin may read a snapshot. They do not write one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SpendDecision:
    allow: bool
    reason: str = ""
    usd: float = 0.0


class SpendHook(Protocol):
    def before_open(self, rail: str) -> SpendDecision: ...

    def on_audio_ms(self, ms: int) -> SpendDecision: ...

    def snapshot(self) -> dict[str, object]: ...


class AllowSpend:
    """Test and offline default. Records milliseconds and never denies."""

    def __init__(self) -> None:
        self.opened: list[str] = []
        self.ms = 0

    def before_open(self, rail: str) -> SpendDecision:
        self.opened.append(rail)
        return SpendDecision(True, "allow", 0.0)

    def on_audio_ms(self, ms: int) -> SpendDecision:
        self.ms += ms
        return SpendDecision(True, "allow", 0.0)

    def snapshot(self) -> dict[str, object]:
        return {"rail_opens": list(self.opened), "audio_ms": self.ms, "authority": "none"}


class CeilingSpend:
    """Deny a new session when the caller-supplied ceiling is already met.

    ``used_usd`` is injected. This object does not read TokenCTR or the ledger.
    """

    def __init__(self, ceiling_usd: float, used_usd: float = 0.0) -> None:
        self.ceiling_usd = ceiling_usd
        self.used_usd = used_usd

    def before_open(self, rail: str) -> SpendDecision:
        if rail == "local":
            return SpendDecision(True, "local", self.used_usd)
        if self.used_usd >= self.ceiling_usd:
            return SpendDecision(False, "ceiling", self.used_usd)
        return SpendDecision(True, "allow", self.used_usd)

    def on_audio_ms(self, ms: int) -> SpendDecision:
        return SpendDecision(True, "meter-elsewhere", self.used_usd)

    def snapshot(self) -> dict[str, object]:
        return {"ceiling_usd": self.ceiling_usd, "used_usd": self.used_usd}
