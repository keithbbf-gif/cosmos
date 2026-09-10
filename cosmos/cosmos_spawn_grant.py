#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P07 Layer A: spawn grant is a folder pen, not a fencing token.

Layer B (commit) stays `cosmos_lock.Lease.token` — monotonic int, STALE_TOKEN /
NO_LEASE at publish. Layer A is issued at worker spawn and caps writes to one
granted folder. Folder grant = pen. No IAM, no AD, no extra Windows logins.

A spawn grant MUST NOT be presented as a fencing token. A fencing token MUST
NOT be presented as a spawn grant. Collapsing A into B is the predecessor.
"""
from __future__ import annotations

from pathlib import Path

KIND = "layer-a-folder-grant"


class SpawnGrantError(RuntimeError):
    """kind in {GRANT_DENIED, NOT_A_GRANT, LAYER_COLLAPSE, BAD_GRANT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class SpawnGrant:
    """OS-level meaning: this process may write under `root` only.

    Distinct type from `cosmos_lock.Lease`. `token` is never an int fencing
    token; it is the granted folder as text so the two cannot be swapped by
    accident and still type-check.
    """

    kind = KIND

    def __init__(self, root: str | Path, sid: str):
        r = str(root or "").strip()
        s = str(sid or "").strip()
        if not r or not s:
            raise SpawnGrantError("BAD_GRANT", "spawn grant needs root and sid")
        self.root = Path(r).resolve()
        self.sid = s

    def allows(self, path: str | Path) -> bool:
        try:
            Path(path).resolve().relative_to(self.root)
        except (OSError, ValueError):
            return False
        return True


def assert_granted(grant, path: str | Path) -> None:
    """Layer A: write outside the granted folder REFUSES. A lock token is not a grant."""
    if isinstance(grant, (int, float)) or type(grant).__name__ == "Lease":
        raise SpawnGrantError(
            "NOT_A_GRANT",
            "Layer B fencing token is not a Layer A spawn grant",
        )
    if not isinstance(grant, SpawnGrant):
        raise SpawnGrantError(
            "NOT_A_GRANT",
            f"need SpawnGrant, got {type(grant).__name__}",
        )
    if not grant.allows(path):
        raise SpawnGrantError(
            "GRANT_DENIED",
            f"write {path} is outside grant {grant.root}",
        )


def refuse_as_fencing_token(obj) -> None:
    """Layer B: a spawn grant is not a fencing token. Do not collapse A into B."""
    if isinstance(obj, SpawnGrant):
        raise SpawnGrantError(
            "LAYER_COLLAPSE",
            "spawn grant is Layer A; fencing token is Layer B (cosmos_lock)",
        )
