"""Atomic per-job assignment. The loser LOSES CLEANLY and moves on.

O_EXCL create of claims/<job_id>.claim is the single-volume optimization.
The ledger assignment event is the authority. Command is built from the
claimed artifact identity, never a pre-claim path.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.manifest import JobManifest
from cosmos.spikes.cosmos_sched.stamp import WorkerIdentity, now_stamp


STALE_RUNNING_S = 2 * 60 * 60  # incumbent: >2 h in running/ is reported, never retried


@dataclass(frozen=True)
class Claim:
    job_id: str
    worker_id: str
    instance_id: str
    attempt_id: str
    artifact_path: str
    command: tuple[str, ...]
    claimed_epoch: float
    stamp: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "worker_id": self.worker_id,
            "instance_id": self.instance_id,
            "attempt_id": self.attempt_id,
            "artifact_path": self.artifact_path,
            "command": list(self.command),
            "claimed_epoch": self.claimed_epoch,
            "stamp": dict(self.stamp),
        }

    def claimed_command(self) -> list[str]:
        """Command built from the claimed identity — the incumbent scar."""
        return list(self.command)


class ClaimBoard:
    def __init__(self, root: Path, identity: WorkerIdentity, clock_epoch: Any = None) -> None:
        self.root = root
        self.identity = identity
        self.dir = root / "claims"
        self.dir.mkdir(parents=True, exist_ok=True)
        self._epoch = clock_epoch  # callable or None

    def _now(self) -> float:
        if self._epoch is None:
            return now_stamp(self.identity).epoch
        return float(self._epoch())

    def path_for(self, job_id: str) -> Path:
        return self.dir / f"{job_id}.claim"

    def try_claim(self, manifest: JobManifest, attempt_id: str) -> TypedResult[Claim]:
        if manifest.helper:
            return TypedResult(Absence.REFUSED, f"helper not claimable: {manifest.job_id}")
        stamp = now_stamp(self.identity)
        claim = Claim(
            job_id=manifest.job_id,
            worker_id=self.identity.worker_id,
            instance_id=self.identity.instance_id,
            attempt_id=attempt_id,
            artifact_path=manifest.artifact_path,
            command=manifest.command,
            claimed_epoch=stamp.epoch,
            stamp=stamp.to_dict(),
        )
        dest = self.path_for(manifest.job_id)
        payload = (json.dumps(claim.to_dict(), sort_keys=True) + "\n").encode("utf-8")
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(str(dest), flags, 0o644)
        except FileExistsError:
            return TypedResult(
                Absence.LOST_CLEANLY,
                f"job {manifest.job_id} already claimed; loser moves on",
            )
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"claim open failed: {exc}")
        try:
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        return TypedResult(Absence.FOUND, "claimed", claim)

    def load(self, job_id: str) -> TypedResult[Claim]:
        path = self.path_for(job_id)
        if not path.exists():
            return TypedResult(Absence.NOT_FOUND, f"claim missing: {job_id}")
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"claim unreadable {job_id}: {exc}")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return TypedResult(Absence.UNPARSEABLE, f"torn claim {job_id}: {exc}")
        try:
            claim = Claim(
                job_id=str(data["job_id"]),
                worker_id=str(data["worker_id"]),
                instance_id=str(data["instance_id"]),
                attempt_id=str(data["attempt_id"]),
                artifact_path=str(data["artifact_path"]),
                command=tuple(str(x) for x in data["command"]),
                claimed_epoch=float(data["claimed_epoch"]),
                stamp=dict(data.get("stamp") or {}),
            )
        except (KeyError, TypeError, ValueError) as exc:
            return TypedResult(Absence.UNPARSEABLE, f"claim schema {job_id}: {exc}")
        return TypedResult(Absence.FOUND, job_id, claim)

    def stale_claims(self, now_epoch: float, stale_s: float = STALE_RUNNING_S) -> TypedResult[list[Claim]]:
        if not self.dir.exists():
            return TypedResult(Absence.NOT_FOUND, f"claims dir missing: {self.dir}")
        try:
            names = os.listdir(self.dir)
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"claims dir unreadable: {exc}")
        stale: list[Claim] = []
        for name in names:
            if not name.endswith(".claim"):
                continue
            loaded = self.load(name[: -len(".claim")])
            if loaded.kind is Absence.UNPARSEABLE:
                return TypedResult(Absence.UNPARSEABLE, loaded.detail)
            if loaded.kind is Absence.UNREADABLE:
                return TypedResult(Absence.UNREADABLE, loaded.detail)
            if loaded.kind is Absence.FOUND and loaded.value is not None:
                age = now_epoch - loaded.value.claimed_epoch
                if age > stale_s:
                    stale.append(loaded.value)
        if not stale:
            return TypedResult(Absence.EMPTY, "no stale claims", [])
        return TypedResult(Absence.STALE, f"n={len(stale)}", stale)
