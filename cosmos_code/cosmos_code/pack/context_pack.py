"""ContextPack pin — map_hash over git HEAD + WO paths (freeze spine Q4).

mtime-only packs = forbidden.
Full-tree sneak-back into draft context = forbidden.
Unsigned richer prompt not in map_hash / property_id = forbid.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


class ContextPackError(RuntimeError):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


def git_head(repo: str | Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise ContextPackError("NO_GIT_HEAD", proc.stderr.strip() or "rev-parse failed")
    return proc.stdout.strip()


def map_hash(head: str, wo_paths: Sequence[str], *, property_id: str = "") -> str:
    """Canonical map_hash = sha256(HEAD + sorted WO paths [+ property_id])."""
    if not head or head == "mtime-only":
        raise ContextPackError("MTIME_ONLY_FORBIDDEN", "map_hash requires git HEAD")
    normalized = sorted({p.replace("\\", "/") for p in wo_paths})
    payload = json.dumps(
        {"head": head, "wo_paths": normalized, "property_id": property_id},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class ContextPack:
    head: str
    wo_paths: list[str]
    property_id: str = ""
    pin_kind: str = "head_wo"  # never mtime_only
    extra_paths: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.pin_kind == "mtime_only" or self.pin_kind == "mtime-only":
            raise ContextPackError("MTIME_ONLY_FORBIDDEN", "mtime-only packs forbidden")
        if not self.head:
            raise ContextPackError("MTIME_ONLY_FORBIDDEN", "empty HEAD")

    @property
    def hash(self) -> str:
        return map_hash(self.head, self.wo_paths, property_id=self.property_id)

    def assert_no_full_tree_sneak(self, allowed_closure: Sequence[str] | None = None) -> None:
        """Refuse draft pack that includes paths outside WO closure."""
        closure = set(p.replace("\\", "/") for p in (allowed_closure or self.wo_paths))
        # also allow 1-hop implied? freeze says WO touch paths — strict for sneak test
        for p in self.extra_paths:
            pn = p.replace("\\", "/")
            if pn not in closure and not any(
                pn.startswith(c.rstrip("/") + "/") for c in closure
            ):
                raise ContextPackError("FULL_TREE_SNEAK", pn)
        for p in self.wo_paths:
            pass  # wo_paths define the closure

    @staticmethod
    def build(
        repo: str | Path,
        wo_paths: Sequence[str],
        *,
        property_id: str = "",
        pin_kind: str = "head_wo",
        extra_paths: Sequence[str] | None = None,
        allowed_closure: Sequence[str] | None = None,
    ) -> "ContextPack":
        if pin_kind in ("mtime_only", "mtime-only"):
            raise ContextPackError("MTIME_ONLY_FORBIDDEN", "mtime-only packs forbidden")
        head = git_head(repo)
        pack = ContextPack(
            head=head,
            wo_paths=list(wo_paths),
            property_id=property_id,
            pin_kind=pin_kind,
            extra_paths=list(extra_paths or []),
        )
        pack.assert_no_full_tree_sneak(allowed_closure or wo_paths)
        return pack

    def as_dict(self) -> dict[str, Any]:
        return {
            "head": self.head,
            "wo_paths": list(self.wo_paths),
            "property_id": self.property_id,
            "pin_kind": self.pin_kind,
            "map_hash": self.hash,
        }
