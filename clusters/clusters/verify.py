"""A claim is VERIFIED only when the caller shows source and observed value."""

from __future__ import annotations


def judge(claim: str, evidence: dict | None) -> dict[str, str]:
    """No claim is a record. A claim without both stamps is UNMEASURED."""
    if not str(claim).strip():
        return {"verdict": "RECORDED", "why": "no claim"}
    if not isinstance(evidence, dict):
        return {"verdict": "UNMEASURED", "why": "claim without evidence"}
    source = str(evidence.get("source") or "").strip()
    observed = str(evidence.get("observed") or "").strip()
    if not source or not observed:
        return {"verdict": "UNMEASURED", "why": "claim needs source and observed"}
    return {"verdict": "VERIFIED", "why": "source and observed present"}
