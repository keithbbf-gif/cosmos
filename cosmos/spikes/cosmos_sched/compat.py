"""Legacy Job Adapter — file-drop to immutable manifests.

Maps incumbent exit codes to worded outcomes. Helper `_` files are never
jobs. Timeout from `__tNNNN` (cap 21600). Skips are printed, never silent.
Compatibility lane is SERIALIZED until a behavior card earns parallelism.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.manifest import (
    ManifestStore,
    is_helper_name,
    timeout_from_filename,
)
from cosmos.spikes.cosmos_sched.stamp import WorkerIdentity


RUNNABLE = {".py", ".cmd", ".ps1"}  # .bat banned by spike ground rules


class LegacyAdapter:
    def __init__(
        self,
        drop_root: Path,
        manifests: ManifestStore,
        identity: WorkerIdentity,
    ) -> None:
        self.drop_root = drop_root
        self.manifests = manifests
        self.identity = identity
        self.skips: list[str] = []

    def ingest_lane(self, lane: str) -> TypedResult[list[str]]:
        drop = self.drop_root / lane
        if not drop.exists():
            return TypedResult(Absence.NOT_FOUND, f"drop lane missing: {drop}", [])
        try:
            names = sorted(os_listdir_safe(drop))
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"drop lane unreadable: {exc}", [])
        accepted: list[str] = []
        for name in names:
            path = drop / name
            if not path.is_file():
                continue
            if is_helper_name(name):
                msg = f"SKIP helper {path} (never claimed)"
                self.skips.append(msg)
                print(msg, flush=True)
                continue
            if path.suffix.lower() not in RUNNABLE:
                msg = f"SKIP not-runnable {path}"
                self.skips.append(msg)
                print(msg, flush=True)
                continue
            priority = _priority_sidecar(path)
            timeout_s = timeout_from_filename(name)
            command = [sys.executable, str(path)]
            submitted = self.manifests.submit(
                lane="compat" if lane == "compat" else lane,
                priority=priority,
                rail="COMPAT",
                command=command,
                timeout_s=timeout_s,
                submitter=self.identity.worker_id,
                artifact_path=str(path),
                helper=False,
            )
            if submitted.kind is Absence.FOUND and submitted.value is not None:
                accepted.append(submitted.value.job_id)
            elif submitted.kind is Absence.REFUSED and "already exists" in submitted.detail:
                continue
            else:
                return TypedResult(submitted.kind, submitted.detail, accepted)
        if not accepted and not self.skips:
            return TypedResult(Absence.EMPTY, f"drop lane {lane} empty", [])
        return TypedResult(Absence.FOUND, f"ingested={len(accepted)} skips={len(self.skips)}", accepted)


def os_listdir_safe(path: Path) -> list[str]:
    return [p.name for p in path.iterdir()]


def _priority_sidecar(path: Path) -> int:
    """Priority is a manifest/sidecar field, never inferred from the filename."""
    sidecar = path.with_suffix(path.suffix + ".priority.json")
    if not sidecar.exists():
        return 0
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    try:
        return int(data["priority"])
    except (KeyError, TypeError, ValueError):
        return 0
