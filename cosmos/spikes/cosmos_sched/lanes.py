"""Lane probe. A lane with jobs and no worker is FLAGGED.

Empty queue != missing lane != unreadable != not in the ledger.
An unrun queue must not look like an empty one.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.heartbeat import HeartbeatDir
from cosmos.spikes.cosmos_sched.manifest import JobManifest, ManifestStore


@dataclass(frozen=True)
class LanePolicy:
    name: str
    max_inflight: int
    serialized: bool


DEFAULT_POLICIES: dict[str, LanePolicy] = {
    "lg": LanePolicy("lg", max_inflight=8, serialized=False),
    "pb": LanePolicy("pb", max_inflight=8, serialized=False),
    "compat": LanePolicy("compat", max_inflight=1, serialized=True),
}


@dataclass(frozen=True)
class LaneProbe:
    lane: str
    jobs_kind: Absence
    workers_kind: Absence
    pending_job_ids: tuple[str, ...]
    worker_ids: tuple[str, ...]
    flagged: bool
    detail: str


class LaneBoard:
    def __init__(self, manifests: ManifestStore, heartbeats: HeartbeatDir) -> None:
        self.manifests = manifests
        self.heartbeats = heartbeats

    def pending_for_lane(
        self,
        lane: str,
        claimed_ids: set[str],
        completed_ids: set[str],
    ) -> TypedResult[list[JobManifest]]:
        listed = self.manifests.list_pending()
        if listed.kind is Absence.NOT_FOUND:
            return TypedResult(Absence.NOT_FOUND, listed.detail, [])
        if listed.kind is Absence.UNREADABLE:
            return TypedResult(Absence.UNREADABLE, listed.detail, [])
        if listed.kind is Absence.UNPARSEABLE:
            return TypedResult(Absence.UNPARSEABLE, listed.detail, [])
        jobs = [
            j
            for j in (listed.value or [])
            if j.lane == lane and j.job_id not in claimed_ids and j.job_id not in completed_ids
        ]
        if not jobs:
            return TypedResult(Absence.EMPTY, f"lane {lane} has no pending jobs", [])
        return TypedResult(Absence.FOUND, f"lane {lane} pending={len(jobs)}", jobs)

    def probe(
        self,
        lane: str,
        claimed_ids: set[str],
        completed_ids: set[str],
    ) -> TypedResult[LaneProbe]:
        jobs = self.pending_for_lane(lane, claimed_ids, completed_ids)
        workers = self.heartbeats.workers_for_lane(lane)
        flagged = jobs.kind is Absence.FOUND and workers.kind is not Absence.FOUND
        detail = (
            f"LANE {lane} FLAGGED: jobs queued and no worker heartbeat"
            if flagged
            else f"lane {lane} jobs={jobs.kind.value} workers={workers.kind.value}"
        )
        probe = LaneProbe(
            lane=lane,
            jobs_kind=jobs.kind,
            workers_kind=workers.kind,
            pending_job_ids=tuple(j.job_id for j in (jobs.value or [])),
            worker_ids=tuple(workers.value or []),
            flagged=flagged,
            detail=detail,
        )
        kind = Absence.FLAGGED if flagged else Absence.FOUND
        return TypedResult(kind, detail, probe)
