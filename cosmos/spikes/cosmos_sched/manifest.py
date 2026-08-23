"""Immutable job manifests. Priority is a field, never a filename.

State changes are ledger events, not edits to the manifest.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.stamp import ArtifactStamp, WorkerIdentity, now_stamp


SCHEMA = "cosmos_sched.manifest.v1"
HELPER_PREFIX = "_"
TIMEOUT_RE = re.compile(r"__t(\d{1,5})")
TIMEOUT_CAP_S = 21600
RAILS = ("CLI", "API", "DOM", "CHAT", "OTHER", "COMPAT")


@dataclass(frozen=True)
class JobManifest:
    job_id: str
    request_id: str
    lane: str
    priority: int
    rail: str
    command: tuple[str, ...]
    timeout_s: int
    submitter: str
    idempotency_key: str
    helper: bool
    artifact_path: str
    dependencies: tuple[str, ...] = ()
    input_hashes: dict[str, str] = field(default_factory=dict)
    schema_version: str = SCHEMA
    stamp: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "job_id": self.job_id,
            "request_id": self.request_id,
            "lane": self.lane,
            "priority": self.priority,
            "rail": self.rail,
            "command": list(self.command),
            "timeout_s": self.timeout_s,
            "submitter": self.submitter,
            "idempotency_key": self.idempotency_key,
            "helper": self.helper,
            "artifact_path": self.artifact_path,
            "dependencies": list(self.dependencies),
            "input_hashes": dict(self.input_hashes),
            "stamp": dict(self.stamp),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobManifest:
        return cls(
            job_id=str(data["job_id"]),
            request_id=str(data["request_id"]),
            lane=str(data["lane"]),
            priority=int(data["priority"]),
            rail=str(data["rail"]),
            command=tuple(str(x) for x in data["command"]),
            timeout_s=int(data["timeout_s"]),
            submitter=str(data["submitter"]),
            idempotency_key=str(data["idempotency_key"]),
            helper=bool(data["helper"]),
            artifact_path=str(data["artifact_path"]),
            dependencies=tuple(str(x) for x in data.get("dependencies", ())),
            input_hashes={str(k): str(v) for k, v in data.get("input_hashes", {}).items()},
            schema_version=str(data.get("schema_version", SCHEMA)),
            stamp=dict(data.get("stamp") or {}),
        )


def timeout_from_filename(name: str, default: int = 3600) -> int:
    match = TIMEOUT_RE.search(name)
    if match is None:
        return default
    return min(int(match.group(1)), TIMEOUT_CAP_S)


def is_helper_name(name: str) -> bool:
    return Path(name).name.startswith(HELPER_PREFIX)


class ManifestStore:
    def __init__(self, root: Path, identity: WorkerIdentity) -> None:
        self.root = root
        self.identity = identity
        self.dir = root / "manifests"
        self.dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, job_id: str) -> Path:
        return self.dir / f"{job_id}.json"

    def submit(
        self,
        *,
        lane: str,
        priority: int,
        rail: str,
        command: list[str] | tuple[str, ...],
        timeout_s: int,
        submitter: str,
        artifact_path: str,
        helper: bool = False,
        job_id: str | None = None,
        dependencies: tuple[str, ...] = (),
        input_hashes: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> TypedResult[JobManifest]:
        if rail not in RAILS:
            return TypedResult(Absence.REFUSED, f"unknown rail {rail!r}")
        if helper:
            return TypedResult(Absence.REFUSED, "helper files are not jobs")
        stamp: ArtifactStamp = now_stamp(self.identity)
        manifest = JobManifest(
            job_id=job_id or uuid.uuid4().hex,
            request_id=uuid.uuid4().hex,
            lane=lane,
            priority=int(priority),
            rail=rail,
            command=tuple(command),
            timeout_s=int(timeout_s),
            submitter=submitter,
            idempotency_key=idempotency_key or uuid.uuid4().hex,
            helper=False,
            artifact_path=artifact_path,
            dependencies=dependencies,
            input_hashes=input_hashes or {},
            stamp=stamp.to_dict(),
        )
        dest = self.path_for(manifest.job_id)
        if dest.exists():
            return TypedResult(Absence.REFUSED, f"manifest already exists: {dest}")
        payload = json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n"
        tmp = dest.with_suffix(".json.tmp")
        tmp.write_text(payload, encoding="utf-8")
        fd = os.open(str(tmp), os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(str(tmp), str(dest))
        return TypedResult(Absence.FOUND, "submitted", manifest)

    def load(self, job_id: str) -> TypedResult[JobManifest]:
        path = self.path_for(job_id)
        if not path.exists():
            return TypedResult(Absence.NOT_FOUND, f"manifest missing: {job_id}")
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"manifest unreadable {job_id}: {exc}")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return TypedResult(Absence.UNPARSEABLE, f"torn manifest {job_id}: {exc}")
        try:
            return TypedResult(Absence.FOUND, job_id, JobManifest.from_dict(data))
        except (KeyError, TypeError, ValueError) as exc:
            return TypedResult(Absence.UNPARSEABLE, f"manifest schema {job_id}: {exc}")

    def list_pending(self) -> TypedResult[list[JobManifest]]:
        if not self.dir.exists():
            return TypedResult(Absence.NOT_FOUND, f"manifest dir missing: {self.dir}")
        try:
            names = os.listdir(self.dir)
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"manifest dir unreadable: {exc}")
        jobs: list[JobManifest] = []
        for name in names:
            if not name.endswith(".json") or name.endswith(".tmp"):
                continue
            loaded = self.load(name[: -len(".json")])
            if loaded.kind is Absence.FOUND and loaded.value is not None:
                if not loaded.value.helper:
                    jobs.append(loaded.value)
            elif loaded.kind in (Absence.UNREADABLE, Absence.UNPARSEABLE):
                return TypedResult(loaded.kind, loaded.detail)
        if not jobs:
            return TypedResult(Absence.EMPTY, "no pending manifests", [])
        jobs.sort(key=lambda j: (-j.priority, j.stamp.get("epoch", 0.0), j.job_id))
        return TypedResult(Absence.FOUND, f"n={len(jobs)}", jobs)
