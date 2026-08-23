"""Plant a scratch COSMOS root + machine-local installation record.

Used by the selftest and the measured demo. Not invoked at import time.
Never searches for a place to plant; caller names both paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .absence import AbsenceKind, TypedRefusal
from .platform import PlatformAdapter, looks_like_windows_path
from .records import new_record, new_sentinel, sha256_hex, write_json
from .roles import MESH_IDENTITY_NAME, ROLE_MARKER_NAME, ROLE_SPECS, SENTINEL_NAME
from .stamp import ArtifactStamp, now_stamp, worker_identity


@dataclass(frozen=True)
class PlantedInstall:
    root: Path
    record_path: Path
    installation_id: str
    sentinel_digest: str
    stamp: ArtifactStamp


def plant_installation(
    root: Path,
    record_path: Path,
    *,
    installation_id: str | None = None,
    adapter: PlatformAdapter | None = None,
    omit_roles: frozenset[str] | None = None,
    skip_mesh_identity: bool = False,
    skip_role_markers: bool = False,
    skip_sentinel: bool = False,
    empty_mesh: bool = False,
    worker_id: str | None = None,
) -> PlantedInstall:
    """Create one explicit install. Refuses a Windows-letter root on POSIX."""
    _ = adapter or PlatformAdapter()
    root = Path(root)
    record_path = Path(record_path)
    if looks_like_windows_path(str(root)):
        raise TypedRefusal(
            AbsenceKind.REFUSED,
            "plant_installation will not write a Windows-letter path as a POSIX filename",
            path=str(root),
        )
    if not root.is_absolute() or not record_path.is_absolute():
        raise TypedRefusal(
            AbsenceKind.REFUSED,
            "plant paths must be absolute — no cwd-relative guessing",
            root=str(root),
            record=str(record_path),
        )
    inst = installation_id or str(uuid4())
    stamp = now_stamp(worker_id or worker_identity("plant"))
    root.mkdir(parents=True, exist_ok=True)
    omitted = omit_roles or frozenset()
    sentinel = new_sentinel(inst, root_identity=f"root:{inst}", stamp=stamp)
    role_ids = {k: v for k, v in sentinel.role_identities.items() if k not in omitted}

    for name, spec in ROLE_SPECS.items():
        if name in omitted:
            continue
        role_dir = root.joinpath(*spec.relative_parts)
        role_dir.mkdir(parents=True, exist_ok=True)
        if not skip_role_markers:
            write_json(
                role_dir / ROLE_MARKER_NAME,
                {
                    "role": name,
                    "role_identity": role_ids[name],
                    "installation_id": inst,
                    **stamp.as_dict(),
                },
            )
        if spec.requires_content_sentinel and spec.content_sentinel_name and not skip_mesh_identity and not empty_mesh:
            write_json(
                role_dir / spec.content_sentinel_name,
                {
                    "role": name,
                    "phrase": spec.content_phrase,
                    "installation_id": inst,
                    "role_identity": role_ids[name],
                    **stamp.as_dict(),
                },
            )
        if empty_mesh and name == "mesh":
            # Directory exists. Identity file absent. This is the mesh() trap.
            marker = role_dir / MESH_IDENTITY_NAME
            if marker.exists():
                marker.unlink()

    digest = "sha256:" + ("0" * 64)
    if not skip_sentinel:
        sentinel_bytes = write_json(root / SENTINEL_NAME, {**sentinel.as_dict(), "role_identities": role_ids})
        digest = sha256_hex(sentinel_bytes)

    record = new_record(
        installation_id=inst,
        configured_root=str(root),
        sentinel_digest=digest,
        stamp=stamp,
        role_identities=role_ids,
    )
    write_json(record_path, record.as_dict())
    return PlantedInstall(
        root=root,
        record_path=record_path,
        installation_id=inst,
        sentinel_digest=digest,
        stamp=stamp,
    )
