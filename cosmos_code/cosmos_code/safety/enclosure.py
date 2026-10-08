"""Enclosure detection — honest policy_only until Job Object / bwrap attaches.

Q5 is labeled policy_only only. Do NOT claim wipe-proof / Job Object.
refuse_unsandboxed_retry always raises — the Codex hole we will not copy:
sandbox fails → "retry without sandbox?" → policy evaporates.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import Optional


class UnsandboxedRetryRefused(RuntimeError):
    """Always raised — never retry without sandbox."""


@dataclass(frozen=True)
class EnclosureStatus:
    kind: str  # none | bwrap | seatbelt | job_object
    available: bool
    intended: str
    reason: str  # policy_only until real enclosure
    wipe_proof: bool = False  # NEVER True without Job Object/bwrap attach

    def label(self) -> str:
        return self.reason


def detect_enclosure() -> EnclosureStatus:
    """Host-truth detection. This Linux box: no bwrap attach → policy_only."""
    has_bwrap = shutil.which("bwrap") is not None
    # We detect but do not attach. Until attach lands, status stays policy_only.
    if has_bwrap:
        return EnclosureStatus(
            kind="none",
            available=False,  # detected binary ≠ attached enclosure
            intended="bwrap",
            reason="policy_only",
            wipe_proof=False,
        )
    return EnclosureStatus(
        kind="none",
        available=False,
        intended="bwrap",
        reason="policy_only",
        wipe_proof=False,
    )


def refuse_unsandboxed_retry(*, why: str = "sandbox_unavailable") -> None:
    """Always raises. Missing primitive → original argv + policy_only; never unsandbox."""
    raise UnsandboxedRetryRefused(
        f"refuse_unsandboxed_retry: {why}; enclosure=policy_only; do not evaporate policy"
    )


def enclosure_is_wipe_proof(status: Optional[EnclosureStatus] = None) -> bool:
    status = status or detect_enclosure()
    # Explicit: policy_only is NOT wipe-proof
    return bool(status.wipe_proof and status.available and status.kind != "none")
