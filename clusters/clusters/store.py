"""Append-only JSONL projection. Views are folds. This is not the COSMOS ledger."""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from pathlib import Path

from clusters.refuse import guard_path, scrub
from clusters.verify import judge


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


class Store:
    def __init__(self, root: str | Path) -> None:
        text = guard_path(str(root))
        self.root = Path(text)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "events.jsonl"
        self._lock = threading.Lock()

    def append(
        self,
        kind: str,
        body: dict,
        evidence: dict | None = None,
        claim: str = "",
    ) -> dict:
        if not kind or not isinstance(body, dict):
            from clusters.refuse import Refuse

            raise Refuse("EVENT", "kind and body are required")
        scrub(body)
        stamped = judge(claim, evidence)
        with self._lock:
            seq = self._last_seq() + 1
            row = {
                "seq": seq,
                "at": time.time(),
                "kind": kind,
                "body": body,
                "claim": claim,
                "verdict": stamped["verdict"],
                "why": stamped["why"],
                "evidence": evidence or {},
            }
            line = json.dumps(row, separators=(",", ":"), sort_keys=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        return row

    def fold(self, kind: str | None = None) -> list[dict]:
        if not self.path.exists():
            return []
        rows: list[dict] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if kind is None or row["kind"] == kind:
                    rows.append(row)
        return rows

    def view(self, kind: str) -> dict[str, dict]:
        """Last write wins per body id, merged onto the earlier snapshot."""
        found: dict[str, dict] = {}
        for row in self.fold(kind):
            item = dict(row["body"])
            item_id = str(item.get("id") or "")
            if not item_id:
                continue
            prior = dict(found.get(item_id, {}))
            prior.update(item)
            prior["_verdict"] = row["verdict"]
            prior["_why"] = row["why"]
            prior["_seq"] = row["seq"]
            prior["_evidence"] = row["evidence"]
            found[item_id] = prior
        return found

    def latest_kind(self, kind: str) -> dict | None:
        rows = self.fold(kind)
        return rows[-1] if rows else None

    def _last_seq(self) -> int:
        if not self.path.exists():
            return 0
        last = 0
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    last = int(json.loads(line)["seq"])
        return last
