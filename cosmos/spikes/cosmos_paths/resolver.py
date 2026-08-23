"""Explicit-instantiation RootResolver.

ONE configured root from a machine-local installation record. Sentinel
CONTENT is verified (digest + installation UUID + system identity), not
mere existence. Roles refuse unknown names. No import-time side effect,
no env fallback, no parent walk, no second-tree search.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .absence import AbsenceKind, Absent, Found, TypedRefusal, TypedResult
from .platform import PlatformAdapter
from .records import InstallationRecord, RootSentinel, parse_installation_record, parse_sentinel, sha256_hex
from .roles import (
    PUBLISH_ROLE,
    ROLE_MARKER_NAME,
    ROLE_SPECS,
    REQUIRED_ROLES,
    SECRETS_ROLE,
    SENTINEL_NAME,
    RoleSpec,
)
from .stamp import ArtifactStamp


@dataclass(frozen=True)
class VerifiedRoot:
    root: Path
    record: InstallationRecord
    sentinel: RootSentinel
    sentinel_digest: str
    stamp: ArtifactStamp


class RootResolver:
    """Fail-fast at instantiate. Ready only after sentinel-verified root."""

    def __init__(self, verified: VerifiedRoot, adapter: PlatformAdapter) -> None:
        self._verified = verified
        self._adapter = adapter
        self.ready = True

    @property
    def installation_id(self) -> str:
        return self._verified.record.installation_id

    @property
    def root_path(self) -> Path:
        return self._verified.root

    @property
    def record(self) -> InstallationRecord:
        return self._verified.record

    @property
    def sentinel(self) -> RootSentinel:
        return self._verified.sentinel

    @property
    def adapter(self) -> PlatformAdapter:
        return self._adapter

    @classmethod
    def instantiate(
        cls,
        record_path: Path | str,
        *,
        adapter: PlatformAdapter | None = None,
    ) -> RootResolver:
        """Boot-composition entry. The record path is explicit. Nothing is guessed."""
        adapter = adapter or PlatformAdapter()
        record_text = str(record_path)
        # A Windows-letter record path on POSIX is the two-universes defect.
        native_record = adapter.native_root_text(record_text) if _looks_absolute_or_windows(record_text) else None
        if isinstance(native_record, Absent) and native_record.kind is AbsenceKind.REFUSED and "backslash" in native_record.detail:
            raise TypedRefusal(native_record.kind, native_record.detail, native_record.observed)

        path = Path(record_path)
        if not path.is_absolute():
            raise TypedRefusal(
                AbsenceKind.REFUSED,
                "installation record path must be absolute; cwd and COSMOS_ROOT are not consulted",
                path=str(record_path),
            )
        loaded = _load_record(adapter, path)
        if isinstance(loaded, Absent):
            raise TypedRefusal(loaded.kind, loaded.detail, loaded.observed)
        record = loaded.value

        native = adapter.native_root_text(record.configured_root)
        if isinstance(native, Absent):
            raise TypedRefusal(native.kind, native.detail, native.observed)
        root = Path(native.value)

        root_probe = adapter.probe(root)
        if isinstance(root_probe, Absent):
            raise TypedRefusal(root_probe.kind, "configured root missing or unreadable", {**dict(root_probe.observed), "configured_root": record.configured_root})
        if not adapter.is_dir(root):
            raise TypedRefusal(AbsenceKind.UNREADABLE, "configured root exists but is not a directory", path=str(root))

        sentinel_path = root / SENTINEL_NAME
        sentinel_bytes = adapter.read_bytes(sentinel_path)
        if isinstance(sentinel_bytes, Absent):
            if sentinel_bytes.kind is AbsenceKind.NOT_FOUND:
                # Directory exists, required content missing — mesh() lesson at root.
                raise TypedRefusal(
                    AbsenceKind.EMPTY_DIR_TRAP,
                    "root exists but sentinel content is absent — existence is not identity",
                    path=str(sentinel_path),
                    trap="EMPTY_DIR_SENTINEL",
                )
            raise TypedRefusal(sentinel_bytes.kind, sentinel_bytes.detail, sentinel_bytes.observed)

        digest = sha256_hex(sentinel_bytes.value)
        if digest != record.sentinel_digest:
            raise TypedRefusal(
                AbsenceKind.IDENTITY_MISMATCH,
                "sentinel digest does not match the installation record",
                expected=record.sentinel_digest,
                observed_digest=digest,
            )

        parsed = parse_sentinel(sentinel_bytes.value)
        if isinstance(parsed, Absent):
            raise TypedRefusal(parsed.kind, parsed.detail, parsed.observed)
        sentinel = parsed.value
        if sentinel.installation_id != record.installation_id:
            raise TypedRefusal(
                AbsenceKind.IDENTITY_MISMATCH,
                "sentinel installation_id does not match the installation record",
                record_id=record.installation_id,
                sentinel_id=sentinel.installation_id,
            )
        if sentinel.role_identities != record.role_identities:
            raise TypedRefusal(
                AbsenceKind.IDENTITY_MISMATCH,
                "sentinel role_identities do not match the installation record",
                record_roles=sorted(record.role_identities),
                sentinel_roles=sorted(sentinel.role_identities),
            )

        missing_required = sorted(REQUIRED_ROLES - set(record.role_identities))
        if missing_required:
            raise TypedRefusal(
                AbsenceKind.NOT_IN_RECORD,
                "installation record omits required roles",
                missing=missing_required,
            )

        for name, spec in ROLE_SPECS.items():
            if name not in record.role_identities:
                continue
            _verify_role_dir(adapter, root, spec, record)

        verified = VerifiedRoot(
            root=root.resolve(),
            record=record,
            sentinel=sentinel,
            sentinel_digest=digest,
            stamp=record.stamp,
        )
        return cls(verified, adapter)

    def role(self, name: str) -> Path:
        """Role API. Unknown names are REFUSED — never joined onto the root."""
        if name == "root":
            return self._verified.root
        if name not in ROLE_SPECS:
            raise TypedRefusal(
                AbsenceKind.REFUSED,
                f"unknown role {name!r} — refuse, do not guess a path",
                role=name,
            )
        if name not in self._verified.record.role_identities:
            raise TypedRefusal(
                AbsenceKind.NOT_IN_RECORD,
                f"role {name!r} is not in this installation record",
                role=name,
                installation_id=self.installation_id,
            )
        spec = ROLE_SPECS[name]
        path = self._verified.root.joinpath(*spec.relative_parts)
        under = self._adapter.normalize_under_root(self._verified.root, path)
        if isinstance(under, Absent):
            raise TypedRefusal(under.kind, under.detail, under.observed)
        if spec.requires_content_sentinel:
            self._assert_mesh_content(path, spec)
        return path

    def _assert_mesh_content(self, path: Path, spec: RoleSpec) -> None:
        if not self._adapter.is_dir(path):
            kind = AbsenceKind.NOT_FOUND if not self._adapter.exists(path) else AbsenceKind.UNREADABLE
            raise TypedRefusal(kind, f"role {spec.name!r} is missing or not a directory", path=str(path))
        names = self._adapter.listdir(path)
        if isinstance(names, Absent):
            raise TypedRefusal(names.kind, names.detail, names.observed)
        identity_name = spec.content_sentinel_name or ""
        if identity_name not in names.value:
            raise TypedRefusal(
                AbsenceKind.EMPTY_DIR_TRAP,
                "mesh directory exists but content sentinel is absent — the mesh() trap",
                path=str(path),
                trap="EMPTY_DIR_SENTINEL",
                listed=list(names.value),
            )
        raw = self._adapter.read_bytes(path / identity_name)
        if isinstance(raw, Absent):
            raise TypedRefusal(raw.kind, raw.detail, raw.observed)
        try:
            payload = json.loads(raw.value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TypedRefusal(AbsenceKind.UNPARSEABLE, f"mesh identity torn: {exc}", path=str(path)) from exc
        if not isinstance(payload, dict):
            raise TypedRefusal(AbsenceKind.UNPARSEABLE, "mesh identity is not an object", path=str(path))
        phrase = payload.get("phrase")
        inst = payload.get("installation_id")
        if phrase != spec.content_phrase or inst != self.installation_id:
            raise TypedRefusal(
                AbsenceKind.IDENTITY_MISMATCH,
                "mesh identity content does not match this installation",
                expected_phrase=spec.content_phrase,
                observed_phrase=phrase,
                installation_id=self.installation_id,
                observed_id=inst,
            )

    def root(self) -> Path:
        return self.role("root")

    def mesh(self) -> Path:
        return self.role("mesh")

    def queue(self) -> Path:
        return self.role("queue")

    def board(self) -> Path:
        return self.role("board")

    def secrets(self) -> Path:
        return self.role(SECRETS_ROLE)

    def archive(self) -> Path:
        return self.role("archive")

    def working(self) -> Path:
        return self.role("working")

    def control(self) -> Path:
        return self.role("control")

    def state(self) -> Path:
        return self.role("state")

    def ledger(self) -> Path:
        return self.role("ledger")

    def work(self) -> Path:
        return self.role("work")

    def logs(self) -> Path:
        return self.role("logs")

    def registry(self) -> Path:
        return self.role("registry")

    def backups(self) -> Path:
        return self.role("backups")

    def publish(self) -> Path:
        return self.role(PUBLISH_ROLE)

    def tools(self) -> Path:
        return self.role("tools")

    def config(self) -> Path:
        return self.role("config")

    def secrets_is_sibling_of_publish(self) -> bool:
        """Location safety: secrets is not under publish, and is not a blocklist."""
        try:
            self.secrets().resolve().relative_to(self.publish().resolve())
        except ValueError:
            return True
        return False

    def report(self) -> dict[str, object]:
        roles = {name: str(self.role(name)) for name in sorted(self._verified.record.role_identities)}
        roles["root"] = str(self.root())
        return {
            "ready": self.ready,
            "installation_id": self.installation_id,
            "configured_root": str(self.root()),
            "sentinel_digest": self._verified.sentinel_digest,
            "roles": roles,
            "secrets_sibling_of_publish": self.secrets_is_sibling_of_publish(),
            **self._verified.stamp.as_dict(),
        }


def _looks_absolute_or_windows(text: str) -> bool:
    return text.startswith("/") or (len(text) >= 2 and text[1] == ":") or text.startswith("\\\\")


def _load_record(adapter: PlatformAdapter, path: Path) -> TypedResult[InstallationRecord]:
    raw = adapter.read_bytes(path)
    if isinstance(raw, Absent):
        return raw
    return parse_installation_record(raw.value)


def _verify_role_dir(adapter: PlatformAdapter, root: Path, spec: RoleSpec, record: InstallationRecord) -> None:
    path = root.joinpath(*spec.relative_parts)
    under = adapter.normalize_under_root(root, path)
    if isinstance(under, Absent):
        raise TypedRefusal(under.kind, under.detail, under.observed)
    if not adapter.exists(path):
        raise TypedRefusal(AbsenceKind.NOT_FOUND, f"required role directory {spec.name!r} is missing", path=str(path))
    if not adapter.is_dir(path):
        raise TypedRefusal(AbsenceKind.UNREADABLE, f"required role {spec.name!r} is not a directory", path=str(path))
    names = adapter.listdir(path)
    if isinstance(names, Absent):
        raise TypedRefusal(names.kind, names.detail, names.observed)
    if ROLE_MARKER_NAME not in names.value:
        raise TypedRefusal(
            AbsenceKind.EMPTY_DIR_TRAP,
            f"role directory {spec.name!r} exists but has no identity marker",
            path=str(path),
            trap="EMPTY_DIR_SENTINEL",
        )
    raw = adapter.read_bytes(path / ROLE_MARKER_NAME)
    if isinstance(raw, Absent):
        raise TypedRefusal(raw.kind, raw.detail, raw.observed)
    try:
        payload = json.loads(raw.value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TypedRefusal(AbsenceKind.UNPARSEABLE, f"role marker torn for {spec.name}: {exc}", path=str(path)) from exc
    if not isinstance(payload, dict):
        raise TypedRefusal(AbsenceKind.UNPARSEABLE, f"role marker for {spec.name} is not an object", path=str(path))
    expected = record.role_identities[spec.name]
    if payload.get("role") != spec.name or payload.get("role_identity") != expected:
        raise TypedRefusal(
            AbsenceKind.IDENTITY_MISMATCH,
            f"role marker identity is wrong for {spec.name}",
            expected=expected,
            observed=payload.get("role_identity"),
        )
    if spec.requires_content_sentinel:
        identity_name = spec.content_sentinel_name or ""
        if identity_name not in names.value:
            raise TypedRefusal(
                AbsenceKind.EMPTY_DIR_TRAP,
                "mesh directory exists but content sentinel is absent — the mesh() trap",
                path=str(path),
                trap="EMPTY_DIR_SENTINEL",
            )
        mesh_raw = adapter.read_bytes(path / identity_name)
        if isinstance(mesh_raw, Absent):
            raise TypedRefusal(mesh_raw.kind, mesh_raw.detail, mesh_raw.observed)
        try:
            mesh_payload = json.loads(mesh_raw.value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TypedRefusal(AbsenceKind.UNPARSEABLE, f"mesh identity torn: {exc}", path=str(path)) from exc
        if not isinstance(mesh_payload, dict) or mesh_payload.get("phrase") != spec.content_phrase:
            raise TypedRefusal(
                AbsenceKind.IDENTITY_MISMATCH,
                "mesh identity phrase mismatch",
                expected=spec.content_phrase,
                observed=mesh_payload.get("phrase") if isinstance(mesh_payload, dict) else None,
            )
        if mesh_payload.get("installation_id") != record.installation_id:
            raise TypedRefusal(
                AbsenceKind.IDENTITY_MISMATCH,
                "mesh identity installation_id mismatch",
                expected=record.installation_id,
                observed=mesh_payload.get("installation_id"),
            )
