"""Installation record and root sentinel — content, not existence.

The machine-local installation record points at exactly one configured root
and names the expected sentinel digest plus installation UUID. The sentinel
at that root carries identity content. Hash mismatch or UUID mismatch is
IDENTITY_MISMATCH, never a guess at another tree.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping
from uuid import UUID

from .absence import AbsenceKind, Absent, Found, TypedResult
from .roles import ROLE_SPECS, SENTINEL_NAME
from .stamp import ArtifactStamp, now_stamp

SCHEMA_VERSION = 1
SYSTEM_NAME = "COSMOS"
CLOCK_FUTURE_GRACE = timedelta(hours=1)
CLOCK_FUTURE_REFUSE = timedelta(hours=24)


@dataclass(frozen=True)
class InstallationRecord:
    schema_version: int
    system: str
    installation_id: str
    configured_root: str
    sentinel_name: str
    sentinel_digest: str
    service_identity: str
    role_identities: dict[str, str]
    stamp: ArtifactStamp

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": self.schema_version,
            "system": self.system,
            "installation_id": self.installation_id,
            "configured_root": self.configured_root,
            "sentinel_name": self.sentinel_name,
            "sentinel_digest": self.sentinel_digest,
            "service_identity": self.service_identity,
            "role_identities": dict(self.role_identities),
        }
        payload.update(self.stamp.as_dict())
        return payload


@dataclass(frozen=True)
class RootSentinel:
    schema_version: int
    system: str
    installation_id: str
    root_identity: str
    role_identities: dict[str, str]
    stamp: ArtifactStamp

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": self.schema_version,
            "system": self.system,
            "installation_id": self.installation_id,
            "root_identity": self.root_identity,
            "role_identities": dict(self.role_identities),
        }
        payload.update(self.stamp.as_dict())
        return payload


def sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def dumps_canonical(payload: Mapping[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def parse_json_bytes(data: bytes, label: str) -> TypedResult[dict[str, object]]:
    if not data.strip():
        return Absent(AbsenceKind.UNPARSEABLE, f"{label} is empty", {"label": label, "bytes": len(data)})
    try:
        raw = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return Absent(AbsenceKind.UNPARSEABLE, f"{label} is torn or not JSON: {exc}", {"label": label})
    if not isinstance(raw, dict):
        return Absent(AbsenceKind.UNPARSEABLE, f"{label} JSON root is not an object", {"label": label})
    return Found(raw, f"{label} parsed", {"label": label})


def _require_str(payload: Mapping[str, object], key: str, label: str) -> TypedResult[str]:
    if key not in payload:
        return Absent(AbsenceKind.NOT_IN_RECORD, f"{label} missing field {key!r}", {"label": label, "field": key})
    value = payload[key]
    if not isinstance(value, str) or not value:
        return Absent(AbsenceKind.UNPARSEABLE, f"{label} field {key!r} is not a non-empty string", {"field": key})
    return Found(value, "field ok", {"field": key})


def _require_int(payload: Mapping[str, object], key: str, label: str) -> TypedResult[int]:
    if key not in payload:
        return Absent(AbsenceKind.NOT_IN_RECORD, f"{label} missing field {key!r}", {"label": label, "field": key})
    value = payload[key]
    if not isinstance(value, int) or isinstance(value, bool):
        return Absent(AbsenceKind.UNPARSEABLE, f"{label} field {key!r} is not an int", {"field": key})
    return Found(value, "field ok", {"field": key})


def _require_roles(payload: Mapping[str, object], label: str) -> TypedResult[dict[str, str]]:
    if "role_identities" not in payload:
        return Absent(AbsenceKind.NOT_IN_RECORD, f"{label} missing role_identities", {"label": label})
    raw = payload["role_identities"]
    if not isinstance(raw, dict) or not raw:
        return Absent(AbsenceKind.UNPARSEABLE, f"{label} role_identities must be a non-empty object", {"label": label})
    out: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not isinstance(value, str) or not value:
            return Absent(AbsenceKind.UNPARSEABLE, f"{label} role_identities entries must be strings", {"role": str(key)})
        if key not in ROLE_SPECS:
            return Absent(AbsenceKind.NOT_IN_RECORD, f"{label} names unknown role {key!r}", {"role": key})
        out[key] = value
    return Found(out, "roles ok", {"count": len(out)})


def _parse_uuid(text: str, label: str) -> TypedResult[str]:
    try:
        return Found(str(UUID(text)), "uuid ok", {"label": label})
    except ValueError:
        return Absent(AbsenceKind.UNPARSEABLE, f"{label} installation_id is not a UUID", {"value": text})


def stamp_from_payload(payload: Mapping[str, object]) -> TypedResult[ArtifactStamp]:
    fields = ("worker_id", "written_at", "utc_written_at", "time_source")
    got: dict[str, str] = {}
    for key in fields:
        result = _require_str(payload, key, "stamp")
        if isinstance(result, Absent):
            return result
        got[key] = result.value
    epoch_raw = payload.get("epoch")
    if not isinstance(epoch_raw, (int, float)):
        return Absent(AbsenceKind.NOT_IN_RECORD, "stamp missing numeric epoch", {"field": "epoch"})
    spike = payload.get("spike")
    return Found(
        ArtifactStamp(
            worker_id=got["worker_id"],
            written_at=got["written_at"],
            utc_written_at=got["utc_written_at"],
            epoch=float(epoch_raw),
            time_source=got["time_source"],
            spike=str(spike) if isinstance(spike, str) else "cosmos_paths",
        ),
        "stamp ok",
        {},
    )


def check_clock(stamp: ArtifactStamp) -> TypedResult[ArtifactStamp]:
    try:
        written = datetime.fromisoformat(stamp.written_at)
    except ValueError:
        return Absent(AbsenceKind.UNPARSEABLE, "written_at is not offset-aware ISO-8601", {"written_at": stamp.written_at})
    if written.tzinfo is None:
        return Absent(AbsenceKind.UNPARSEABLE, "written_at has no timezone offset", {"written_at": stamp.written_at})
    now = datetime.now(written.tzinfo)
    delta = written - now
    if delta > CLOCK_FUTURE_REFUSE:
        return Absent(
            AbsenceKind.OUT_OF_CLOCK,
            "artifact timestamp is more than 24 hours in the future",
            {"written_at": stamp.written_at, "now": now.isoformat(), "delta_s": delta.total_seconds()},
        )
    if delta > CLOCK_FUTURE_GRACE:
        return Absent(
            AbsenceKind.OUT_OF_CLOCK,
            "artifact timestamp exceeds one-hour future grace",
            {"written_at": stamp.written_at, "delta_s": delta.total_seconds()},
        )
    # Epoch vs wall: refuse if they disagree by more than a day (torn / mixed clocks).
    wall_epoch = written.timestamp()
    if abs(wall_epoch - stamp.epoch) > 86400:
        return Absent(
            AbsenceKind.OUT_OF_CLOCK,
            "epoch and written_at disagree by more than one day",
            {"epoch": stamp.epoch, "written_at_epoch": wall_epoch},
        )
    return Found(stamp, "clock ok", {"time_source": stamp.time_source})


def parse_installation_record(data: bytes) -> TypedResult[InstallationRecord]:
    parsed = parse_json_bytes(data, "installation record")
    if isinstance(parsed, Absent):
        return parsed
    payload = parsed.value
    schema = _require_int(payload, "schema_version", "installation record")
    if isinstance(schema, Absent):
        return schema
    if schema.value != SCHEMA_VERSION:
        return Absent(AbsenceKind.IDENTITY_MISMATCH, "installation record schema_version refused", {"got": schema.value})
    system = _require_str(payload, "system", "installation record")
    if isinstance(system, Absent):
        return system
    if system.value != SYSTEM_NAME:
        return Absent(AbsenceKind.IDENTITY_MISMATCH, "installation record system is not COSMOS", {"got": system.value})
    inst = _require_str(payload, "installation_id", "installation record")
    if isinstance(inst, Absent):
        return inst
    uuid_ok = _parse_uuid(inst.value, "installation record")
    if isinstance(uuid_ok, Absent):
        return uuid_ok
    root = _require_str(payload, "configured_root", "installation record")
    if isinstance(root, Absent):
        return root
    sentinel_name = _require_str(payload, "sentinel_name", "installation record")
    if isinstance(sentinel_name, Absent):
        return sentinel_name
    if sentinel_name.value != SENTINEL_NAME:
        return Absent(
            AbsenceKind.IDENTITY_MISMATCH,
            "installation record sentinel_name is not the COSMOS sentinel",
            {"got": sentinel_name.value, "expected": SENTINEL_NAME},
        )
    digest = _require_str(payload, "sentinel_digest", "installation record")
    if isinstance(digest, Absent):
        return digest
    service = _require_str(payload, "service_identity", "installation record")
    if isinstance(service, Absent):
        return service
    roles = _require_roles(payload, "installation record")
    if isinstance(roles, Absent):
        return roles
    stamp = stamp_from_payload(payload)
    if isinstance(stamp, Absent):
        return stamp
    clock = check_clock(stamp.value)
    if isinstance(clock, Absent):
        return clock
    record = InstallationRecord(
        schema_version=schema.value,
        system=system.value,
        installation_id=uuid_ok.value,
        configured_root=root.value,
        sentinel_name=sentinel_name.value,
        sentinel_digest=digest.value,
        service_identity=service.value,
        role_identities=roles.value,
        stamp=clock.value,
    )
    return Found(record, "installation record accepted", {"installation_id": record.installation_id})


def parse_sentinel(data: bytes) -> TypedResult[RootSentinel]:
    parsed = parse_json_bytes(data, "root sentinel")
    if isinstance(parsed, Absent):
        return parsed
    payload = parsed.value
    schema = _require_int(payload, "schema_version", "root sentinel")
    if isinstance(schema, Absent):
        return schema
    if schema.value != SCHEMA_VERSION:
        return Absent(AbsenceKind.IDENTITY_MISMATCH, "sentinel schema_version refused", {"got": schema.value})
    system = _require_str(payload, "system", "root sentinel")
    if isinstance(system, Absent):
        return system
    if system.value != SYSTEM_NAME:
        return Absent(AbsenceKind.IDENTITY_MISMATCH, "sentinel system is not COSMOS", {"got": system.value})
    inst = _require_str(payload, "installation_id", "root sentinel")
    if isinstance(inst, Absent):
        return inst
    uuid_ok = _parse_uuid(inst.value, "root sentinel")
    if isinstance(uuid_ok, Absent):
        return uuid_ok
    root_id = _require_str(payload, "root_identity", "root sentinel")
    if isinstance(root_id, Absent):
        return root_id
    roles = _require_roles(payload, "root sentinel")
    if isinstance(roles, Absent):
        return roles
    stamp = stamp_from_payload(payload)
    if isinstance(stamp, Absent):
        return stamp
    clock = check_clock(stamp.value)
    if isinstance(clock, Absent):
        return clock
    sentinel = RootSentinel(
        schema_version=schema.value,
        system=system.value,
        installation_id=uuid_ok.value,
        root_identity=root_id.value,
        role_identities=roles.value,
        stamp=clock.value,
    )
    return Found(sentinel, "sentinel accepted", {"installation_id": sentinel.installation_id})


def role_identity(role: str, installation_id: str) -> str:
    return f"{role}:{installation_id}"


def default_role_identities(installation_id: str) -> dict[str, str]:
    return {name: role_identity(name, installation_id) for name in sorted(ROLE_SPECS)}


def new_sentinel(installation_id: str, root_identity: str, stamp: ArtifactStamp | None = None) -> RootSentinel:
    return RootSentinel(
        schema_version=SCHEMA_VERSION,
        system=SYSTEM_NAME,
        installation_id=installation_id,
        root_identity=root_identity,
        role_identities=default_role_identities(installation_id),
        stamp=stamp or now_stamp(),
    )


def new_record(
    installation_id: str,
    configured_root: str,
    sentinel_digest: str,
    stamp: ArtifactStamp | None = None,
    service_identity: str = "cosmos-core",
    role_identities: dict[str, str] | None = None,
) -> InstallationRecord:
    return InstallationRecord(
        schema_version=SCHEMA_VERSION,
        system=SYSTEM_NAME,
        installation_id=installation_id,
        configured_root=configured_root,
        sentinel_name=SENTINEL_NAME,
        sentinel_digest=sentinel_digest,
        service_identity=service_identity,
        role_identities=role_identities or default_role_identities(installation_id),
        stamp=stamp or now_stamp(),
    )


def write_json(path: Path, payload: Mapping[str, object]) -> bytes:
    data = dumps_canonical(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data
