"""Centrally declared roles under ONE configured root.

No role walks from __file__, cwd, or parent-of-another-role. secrets is a
sibling of publish by LOCATION (COSMOS_ROOT/.secrets), not an exclude-list
entry. mesh requires a content sentinel — existence is not identity.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleSpec:
    name: str
    relative_parts: tuple[str, ...]
    requires_content_sentinel: bool
    content_sentinel_name: str | None
    content_phrase: str | None


# Relative parts are single path segments. ".." is refused at load.
_ROLE_TABLE: tuple[RoleSpec, ...] = (
    RoleSpec("state", ("state",), False, None, None),
    RoleSpec("ledger", ("ledger",), False, None, None),
    RoleSpec("queue", ("queue",), False, None, None),
    RoleSpec("work", ("work",), False, None, None),
    RoleSpec("logs", ("logs",), False, None, None),
    RoleSpec("registry", ("registry",), False, None, None),
    RoleSpec("backups", ("backups",), False, None, None),
    RoleSpec("publish", ("publish",), False, None, None),
    RoleSpec("tools", ("tools",), False, None, None),
    RoleSpec("config", ("config",), False, None, None),
    RoleSpec("board", ("board",), False, None, None),
    RoleSpec("archive", ("archive",), False, None, None),
    RoleSpec("working", ("working",), False, None, None),
    RoleSpec("control", ("control",), False, None, None),
    RoleSpec("secrets", (".secrets",), False, None, None),
    RoleSpec(
        "mesh",
        ("mesh",),
        True,
        ".cosmos-mesh-identity.json",
        "COSMOS_MESH_IDENTITY",
    ),
)


def _validate_table() -> dict[str, RoleSpec]:
    out: dict[str, RoleSpec] = {}
    for spec in _ROLE_TABLE:
        if ".." in spec.relative_parts or any("/" in p or "\\" in p for p in spec.relative_parts):
            raise RuntimeError(f"role {spec.name!r} walks or embeds separators")
        if spec.name in out:
            raise RuntimeError(f"duplicate role {spec.name!r}")
        out[spec.name] = spec
    return out


ROLE_SPECS: dict[str, RoleSpec] = _validate_table()
ROLE_NAMES: frozenset[str] = frozenset(ROLE_SPECS)
REQUIRED_ROLES: frozenset[str] = ROLE_NAMES

ROLE_MARKER_NAME = ".cosmos-role.json"
MESH_IDENTITY_NAME = ".cosmos-mesh-identity.json"
SENTINEL_NAME = ".cosmos-sentinel.json"

# secrets must not live under publish. Enforced by layout, asserted in tests.
SECRETS_ROLE = "secrets"
PUBLISH_ROLE = "publish"
