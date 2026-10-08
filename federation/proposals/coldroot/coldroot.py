"""Day-one cold root: one sentinel, the role directories, and an install record.

`plan` describes the write. `apply` performs it inside a PathJail.
The caller passes `now`. This module does not read the clock and does not
draw random bytes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from cosmos_federation import ROLES, PathJail, Refuse, bound_int, bound_text, check_tree_id

SCHEMA = "cosmos-federation-coldroot/1"

_SYSTEM = "COSMOS"
_SCHEMA_VERSION = 1
_SENTINEL_NAME = ".cosmos-root.json"
_RECORD_REL = "config/install_record.json"
_RECORD_KEYS = ("tree_id", "installed_epoch")
# 2100-01-01 UTC. Seconds, the same unit as the live install clock, but an int
# the caller passes. Milliseconds and booleans fall outside and refuse.
_EPOCH_HI = 4_102_444_800


@dataclass(frozen=True, slots=True)
class SentinelBody:
    """The three keys `write_sentinel` writes. A path is not one of them."""

    system: str
    tree_id: str
    schema_version: int

    def __post_init__(self) -> None:
        if (
            self.system != _SYSTEM
            or isinstance(self.schema_version, bool)
            or self.schema_version != _SCHEMA_VERSION
        ):
            raise Refuse("BOUND", "sentinel")
        check_tree_id(self.tree_id)


@dataclass(frozen=True, slots=True)
class InstallRecord:
    """Identity plus the caller epoch.

    The live record also stores `root`. That path is not an identity: a
    drive letter is how a resolver succeeds into the wrong universe. The
    caller already holds the jail, so the record does not point at a drive.
    """

    tree_id: str
    installed_epoch: int

    def __post_init__(self) -> None:
        check_tree_id(self.tree_id)
        bound_int(self.installed_epoch, lo=0, hi=_EPOCH_HI, name="now")


@dataclass(frozen=True, slots=True)
class RoleDir:
    """One row of the product role table. `tools` is the directory `cosmos`."""

    name: str
    directory: str

    def __post_init__(self) -> None:
        bound_text(self.name, limit=40, name="role")
        bound_text(self.directory, limit=40, name="role")


@dataclass(frozen=True, slots=True)
class InstallPlan:
    """What a cold install writes. `record_keys` is the record object, not a path."""

    sentinel: SentinelBody
    record: InstallRecord
    roles: tuple[RoleDir, ...]
    record_keys: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.roles != _product_roles():
            raise Refuse("BOUND", "roles")
        if self.record_keys != _RECORD_KEYS:
            raise Refuse("BOUND", "record_keys")
        if self.sentinel.tree_id != self.record.tree_id:
            raise Refuse("IDENTITY_MISMATCH", "sentinel and record disagree")


def _product_roles() -> tuple[RoleDir, ...]:
    return tuple(RoleDir(name, directory) for name, directory in ROLES.items())


def plan(tree_id: str, now: int) -> InstallPlan:
    """Describe the sentinel, the role directories, and the record keys."""
    checked = check_tree_id(tree_id)
    epoch = bound_int(now, lo=0, hi=_EPOCH_HI, name="now")
    return InstallPlan(
        sentinel=SentinelBody(
            system=_SYSTEM,
            tree_id=checked,
            schema_version=_SCHEMA_VERSION,
        ),
        record=InstallRecord(tree_id=checked, installed_epoch=epoch),
        roles=_product_roles(),
        record_keys=_RECORD_KEYS,
    )


def _read_object(path: Path, what: str) -> dict[str, object] | None:
    if not path.exists():
        return None
    if not path.is_file():
        raise Refuse("UNPARSEABLE", f"existing {what} is torn")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError:
        raise Refuse("UNPARSEABLE", f"existing {what} is torn") from None
    except OSError:
        raise Refuse("UNREADABLE", f"existing {what} cannot be read") from None
    try:
        parsed: object = json.loads(text)
    except ValueError:
        raise Refuse("UNPARSEABLE", f"existing {what} is torn") from None
    if not isinstance(parsed, dict):
        raise Refuse("UNPARSEABLE", f"existing {what} is torn")
    clean: dict[str, object] = {}
    for key, value in parsed.items():
        if not isinstance(key, str):
            raise Refuse("UNPARSEABLE", f"existing {what} is torn")
        clean[key] = value
    return clean


def _assert_compatible(data: dict[str, object] | None, tree_id: str) -> None:
    """A different tree id is a hijack, not an install.

    Live `install()` restamps a sentinel whose tree_id is an empty string.
    That stamp is not an identity yet. A missing tree_id is not empty: the
    file belongs to something else, and this slot leaves it alone.
    """
    if data is None:
        return
    if "tree_id" not in data:
        raise Refuse(
            "IDENTITY_MISMATCH",
            "refusing to restamp a file that has no tree_id",
        )
    found = data["tree_id"]
    if not isinstance(found, str):
        raise Refuse("UNPARSEABLE", "existing tree_id is not a string")
    if found == "" or found == tree_id:
        return
    raise Refuse(
        "IDENTITY_MISMATCH",
        "refusing to restamp a different tree_id",
    )


def _sentinel_text(body: SentinelBody) -> str:
    payload = {
        "system": body.system,
        "tree_id": body.tree_id,
        "schema_version": body.schema_version,
    }
    return json.dumps(payload, indent=1)


def _record_text(record: InstallRecord) -> str:
    # Keys are tree_id and installed_epoch only. Writing the jail path would
    # store a drive letter as identity. The sentinel content is the identity.
    payload = {
        "tree_id": record.tree_id,
        "installed_epoch": record.installed_epoch,
    }
    return json.dumps(payload, indent=1)


def _write_text(path: Path, text: str) -> None:
    # LF only. Path.write_text would otherwise emit the host line ending,
    # and the same install would not be byte-identical on two machines.
    path.write_text(text, encoding="utf-8", newline="\n")


def _make_roles(jail: PathJail, roles: tuple[RoleDir, ...]) -> None:
    for role in roles:
        if role.directory == ".":
            # The root role is the jail itself. contain(".") refuses, and
            # the directory is already the root the caller passed.
            continue
        dest = jail.contain(role.directory)
        try:
            dest.mkdir(parents=True, exist_ok=True)
        except OSError:
            raise Refuse("NOT_A_DIRECTORY", "role path is not a directory") from None


def apply(jail: PathJail, tree_id: str, now: int) -> InstallPlan:
    """Create the role directories and write the sentinel and the record.

    Live `install()` also writes `config/install_key.bin` from `os.urandom`.
    This slot does not write that file, and it does not write
    `config/api_token.txt`. The secrets slot owns both, so two writers do
    not both claim the key.
    """
    if not isinstance(jail, PathJail):
        raise Refuse("JAIL", "apply requires a PathJail")
    planned = plan(tree_id, now)
    sentinel_path = jail.contain(_SENTINEL_NAME)
    record_path = jail.contain(_RECORD_REL)
    _assert_compatible(_read_object(sentinel_path, "sentinel"), planned.sentinel.tree_id)
    _assert_compatible(_read_object(record_path, "install record"), planned.record.tree_id)
    _make_roles(jail, planned.roles)
    _write_text(sentinel_path, _sentinel_text(planned.sentinel))
    _write_text(record_path, _record_text(planned.record))
    return planned


__all__ = [
    "SCHEMA",
    "InstallPlan",
    "InstallRecord",
    "RoleDir",
    "SentinelBody",
    "apply",
    "plan",
]
