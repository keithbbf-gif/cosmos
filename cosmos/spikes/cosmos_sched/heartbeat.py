"""Per-worker glob-discoverable heartbeats.

A checker that is not told the worker names still finds them:
    runner_heartbeat__*.json
Every tick carries aware-local + epoch + UTC + offset + lane + worker.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.stamp import WorkerIdentity, classify_timestamp, now_stamp


class HeartbeatDir:
    def __init__(self, root: Path, identity: WorkerIdentity) -> None:
        self.root = root
        self.identity = identity
        self.dir = root / "heartbeats"
        self.dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, worker_id: str) -> Path:
        return self.dir / f"runner_heartbeat__{worker_id}.json"

    def write(self, lane: str) -> TypedResult[Path]:
        stamp = now_stamp(self.identity)
        payload = {
            "lane": lane,
            "worker_id": self.identity.worker_id,
            "instance_id": self.identity.instance_id,
            "host": self.identity.host,
            "spike": self.identity.spike,
            "written_at_local": stamp.written_at_local,
            "written_at_utc": stamp.written_at_utc,
            "epoch": stamp.epoch,
            "offset": stamp.offset,
        }
        dest = self.path_for(self.identity.worker_id)
        text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        dest.write_text(text, encoding="utf-8")
        fd = os.open(str(dest), os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return TypedResult(Absence.FOUND, "heartbeat", dest)

    def discover(self) -> TypedResult[list[dict[str, Any]]]:
        """Glob discovery — do not require the caller to know worker names."""
        if not self.dir.exists():
            return TypedResult(Absence.NOT_FOUND, f"heartbeat dir missing: {self.dir}")
        try:
            matches = sorted(self.dir.glob("runner_heartbeat__*.json"))
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"heartbeat glob failed: {exc}")
        if not matches:
            return TypedResult(Absence.EMPTY, "no heartbeats", [])
        found: list[dict[str, Any]] = []
        for path in matches:
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                return TypedResult(Absence.UNREADABLE, f"heartbeat unreadable {path.name}: {exc}")
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                return TypedResult(Absence.UNPARSEABLE, f"torn heartbeat {path.name}: {exc}")
            clock = classify_timestamp(data.get("written_at_local"))
            if clock == "OUT_OF_CLOCK":
                return TypedResult(
                    Absence.OUT_OF_CLOCK,
                    f"heartbeat {path.name} has naive or future timestamp",
                    [data],
                )
            if clock == "UNPARSEABLE":
                return TypedResult(Absence.UNPARSEABLE, f"heartbeat {path.name} timestamp")
            found.append(data)
        return TypedResult(Absence.FOUND, f"n={len(found)}", found)

    def workers_for_lane(self, lane: str) -> TypedResult[list[str]]:
        discovered = self.discover()
        if discovered.kind is not Absence.FOUND or discovered.value is None:
            return TypedResult(discovered.kind, discovered.detail, [])
        ids = [row["worker_id"] for row in discovered.value if row.get("lane") == lane]
        if not ids:
            return TypedResult(Absence.NOT_FOUND, f"no worker heartbeat for lane {lane}", [])
        return TypedResult(Absence.FOUND, lane, ids)
