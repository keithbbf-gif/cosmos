"""Archive-not-delete — the only legal disappearance.

shutil.move into _delme/delme__YYYY-MM-DD__… plus JSONL ledger row.
Raw unlink that succeeds = crash class (not PASS).
delete_policy=archive_only is the third knob beside sandbox ⊥ approval.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cosmos_code.safety.pathjail import PathJail


class CrashClass(RuntimeError):
    """Raw unlink / irreversible delete observed — harness CRASH, not PASS."""

    def __init__(self, detail: str = "raw_unlink"):
        self.detail = detail
        super().__init__(f"CRASH class: {detail}")


class ArchiveStore:
    """Only legal disappearance path under delete_policy=archive_only."""

    delete_policy = "archive_only"

    def __init__(self, jail: PathJail, delme_root: str | Path, ledger_path: str | Path | None = None):
        self.jail = jail
        self.delme_root = Path(delme_root)
        self.delme_root.mkdir(parents=True, exist_ok=True)
        # ensure delme is a grant
        self.jail.add_grant(self.delme_root)
        if ledger_path is None:
            ledger_path = self.delme_root / "archive_ledger.jsonl"
        self.ledger_path = Path(ledger_path)

    def stage_to_delme(self, src: str | Path, *, reason: str = "archive_rewrite") -> Path:
        """Move *src* into _delme and append ARCHIVE ledger row. Never unlink."""
        raw = str(src)
        self.jail.check_shape(raw)
        src_path = Path(src)
        if not src_path.exists():
            raise FileNotFoundError(raw)
        # must be under a grant (attempt workspace)
        resolved = self.jail.resolve(str(src_path.resolve()), must_be_under_grant=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        dest_name = f"delme__{stamp}__{resolved.name}"
        dest = self.delme_root / dest_name
        # collide-safe
        n = 0
        while dest.exists():
            n += 1
            dest = self.delme_root / f"delme__{stamp}__{n}__{resolved.name}"
        shutil.move(str(resolved), str(dest))
        self._ledger(
            {
                "op": "ARCHIVE",
                "src": str(resolved),
                "dest": str(dest),
                "reason": reason,
                "ts": stamp,
                "delete_policy": self.delete_policy,
            }
        )
        return dest

    def _ledger(self, row: dict[str, Any]) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    def read_ledger(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        rows = []
        for line in self.ledger_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return rows

    @staticmethod
    def raw_unlink(path: str | Path) -> None:
        """Illegal. Always raises CrashClass — never use for deletes."""
        raise CrashClass(f"raw_unlink attempted on {path}")

    @staticmethod
    def mark_crash_if_unlinked(path: str | Path, existed_before: bool) -> None:
        """If a path existed and is now gone without archive → CRASH."""
        p = Path(path)
        if existed_before and not p.exists():
            raise CrashClass(f"untracked_disappearance:{path}")
