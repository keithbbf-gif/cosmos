"""Worker identity plus offset-aware timestamps on every artifact.

A naked local timestamp was twice misread as five hours stale. Every stamp
carries aware-local, UTC, epoch, and the time-source name.
"""

from __future__ import annotations

import os
import socket
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from time import time as epoch_now


SPIKE_NAME = "cosmos_paths"
WORKER_FAMILY = "cursor-cloud"


@dataclass(frozen=True)
class ArtifactStamp:
    worker_id: str
    written_at: str
    utc_written_at: str
    epoch: float
    time_source: str
    spike: str = SPIKE_NAME

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def worker_identity(extra: str | None = None) -> str:
    host = socket.gethostname()
    parts = [WORKER_FAMILY, SPIKE_NAME, host, str(os.getpid())]
    if extra:
        parts.append(extra)
    return ":".join(parts)


def now_stamp(worker_id: str | None = None) -> ArtifactStamp:
    local = datetime.now().astimezone()
    utc = datetime.now(timezone.utc)
    return ArtifactStamp(
        worker_id=worker_id or worker_identity(),
        written_at=local.isoformat(timespec="milliseconds"),
        utc_written_at=utc.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        epoch=float(epoch_now()),
        time_source="host-local-aware",
    )
