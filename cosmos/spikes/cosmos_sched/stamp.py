"""Worker identity plus offset-aware timestamps and Unix epoch.

Every spike artifact carries all three. Naive datetimes are OUT_OF_CLOCK.
"""

from __future__ import annotations

import os
import socket
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SPIKE_NAME = "cosmos_sched"
SPIKE_WORKER_PREFIX = "cosmos_sched-spike"


def _local_tz() -> timezone | ZoneInfo:
    name = os.environ.get("TZ")
    if name:
        try:
            return ZoneInfo(name)
        except ZoneInfoNotFoundError:
            pass
    local = datetime.now().astimezone()
    tz = local.tzinfo
    if tz is None:
        return timezone.utc
    return tz


@dataclass(frozen=True)
class WorkerIdentity:
    worker_id: str
    instance_id: str
    host: str
    spike: str = SPIKE_NAME

    @classmethod
    def mint(cls, worker_id: str | None = None) -> WorkerIdentity:
        wid = worker_id or f"{SPIKE_WORKER_PREFIX}-{uuid.uuid4().hex[:8]}"
        return cls(
            worker_id=wid,
            instance_id=uuid.uuid4().hex,
            host=socket.gethostname(),
            spike=SPIKE_NAME,
        )


@dataclass(frozen=True)
class ArtifactStamp:
    worker_id: str
    instance_id: str
    host: str
    spike: str
    written_at_local: str
    written_at_utc: str
    epoch: float
    offset: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "instance_id": self.instance_id,
            "host": self.host,
            "spike": self.spike,
            "written_at_local": self.written_at_local,
            "written_at_utc": self.written_at_utc,
            "epoch": self.epoch,
            "offset": self.offset,
        }


def classify_timestamp(raw: object) -> str:
    """Return Absence name for a timestamp payload. Never collapses states."""
    if raw is None:
        return "NOT_FOUND"
    if not isinstance(raw, str) or raw.strip() == "":
        return "UNPARSEABLE"
    text = raw.strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return "UNPARSEABLE"
    if parsed.tzinfo is None:
        return "OUT_OF_CLOCK"
    now = datetime.now(timezone.utc)
    skew = (parsed.astimezone(timezone.utc) - now).total_seconds()
    # More than one hour in the future is clock failure, not "stale".
    if skew > 3600:
        return "OUT_OF_CLOCK"
    return "FOUND"


def now_stamp(identity: WorkerIdentity) -> ArtifactStamp:
    tz = _local_tz()
    local = datetime.now(tz)
    utc = local.astimezone(timezone.utc)
    offset = local.strftime("%z")
    if offset and len(offset) == 5:
        offset = f"{offset[:3]}:{offset[3:]}"
    elif not offset:
        offset = "+00:00"
    return ArtifactStamp(
        worker_id=identity.worker_id,
        instance_id=identity.instance_id,
        host=identity.host,
        spike=identity.spike,
        written_at_local=local.isoformat(timespec="milliseconds"),
        written_at_utc=utc.isoformat(timespec="milliseconds"),
        epoch=time.time(),
        offset=offset,
    )


@dataclass
class Clock:
    """Injectable clock for stale/expiry tests. Default is wall clock."""

    _offset_s: float = 0.0
    _frozen_epoch: float | None = None
    _events: list[str] = field(default_factory=list)

    def now_epoch(self) -> float:
        if self._frozen_epoch is not None:
            return self._frozen_epoch + self._offset_s
        return time.time() + self._offset_s

    def advance(self, seconds: float) -> None:
        self._offset_s += seconds
        self._events.append(f"advance:{seconds}")

    def freeze(self, epoch: float | None = None) -> None:
        self._frozen_epoch = time.time() if epoch is None else epoch
