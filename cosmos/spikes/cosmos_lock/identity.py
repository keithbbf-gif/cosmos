"""Worker identity and offset-aware stamps.

Every artifact (ledger event, capability, ingress envelope, demo line)
carries who wrote it, an offset-aware timestamp, and an epoch second.
A naked local timestamp was twice misread as five hours stale
(STAGE2A runner heartbeat).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from cosmos.spikes.cosmos_lock.clock import ArbiterClock


def _offset_string(aware: datetime) -> str:
    offset = aware.utcoffset()
    if offset is None:
        raise ValueError("timestamp is naive; COSMOS forbids naive clocks")
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, rem = divmod(total, 3600)
    minutes, _ = divmod(rem, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


@dataclass(frozen=True)
class WorkerIdentity:
    worker_id: str
    instance_id: str
    lane: str
    attempt_id: str | None = None

    def __post_init__(self) -> None:
        if not self.worker_id or not self.instance_id or not self.lane:
            raise ValueError("worker_id, instance_id, and lane are required")

    def as_dict(self) -> dict[str, str | None]:
        return {
            "worker_id": self.worker_id,
            "instance_id": self.instance_id,
            "lane": self.lane,
            "attempt_id": self.attempt_id,
        }

    @staticmethod
    def mint(worker_id: str, *, lane: str, attempt_id: str | None = None) -> WorkerIdentity:
        return WorkerIdentity(
            worker_id=worker_id,
            instance_id=str(uuid4()),
            lane=lane,
            attempt_id=attempt_id,
        )


@dataclass(frozen=True)
class Stamp:
    worker: WorkerIdentity
    aware_iso: str
    epoch_seconds: float
    tz_offset: str
    time_source: str

    def as_dict(self) -> dict[str, object]:
        return {
            "worker": self.worker.as_dict(),
            "aware_iso": self.aware_iso,
            "epoch_seconds": self.epoch_seconds,
            "tz_offset": self.tz_offset,
            "time_source": self.time_source,
        }

    @staticmethod
    def from_clock(worker: WorkerIdentity, clock: ArbiterClock, *, time_source: str) -> Stamp:
        aware = clock.now()
        if aware.tzinfo is None:
            raise ValueError("arbiter clock returned a naive datetime")
        return Stamp(
            worker=worker,
            aware_iso=aware.isoformat(timespec="milliseconds"),
            epoch_seconds=clock.epoch(),
            tz_offset=_offset_string(aware),
            time_source=time_source,
        )

    @staticmethod
    def utc_now(worker: WorkerIdentity, *, time_source: str = "wall") -> Stamp:
        aware = datetime.now(timezone.utc)
        return Stamp(
            worker=worker,
            aware_iso=aware.isoformat(timespec="milliseconds"),
            epoch_seconds=aware.timestamp(),
            tz_offset=_offset_string(aware),
            time_source=time_source,
        )
