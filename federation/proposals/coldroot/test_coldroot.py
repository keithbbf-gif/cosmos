"""Cold-root install: sentinel and record, no key material."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from coldroot import SCHEMA, InstallPlan, apply, plan
from cosmos_federation import ROLES, PathJail, Refuse


def test_plan_describes_sentinel_roles_and_record_keys(scratch: Path) -> None:
    planned = plan("Peer-1", 1_700_000_000)
    assert isinstance(planned, InstallPlan)
    assert planned.sentinel.system == "COSMOS"
    assert planned.sentinel.tree_id == "Peer-1"
    assert planned.sentinel.schema_version == 1
    assert planned.record.tree_id == "Peer-1"
    assert planned.record.installed_epoch == 1_700_000_000
    assert isinstance(planned.record.installed_epoch, int)
    assert planned.record_keys == ("tree_id", "installed_epoch")
    assert "root" not in planned.record_keys
    assert planned.roles[0].name == "root"
    assert planned.roles[0].directory == "."
    assert tuple((role.name, role.directory) for role in planned.roles) == tuple(ROLES.items())
    tools = [role for role in planned.roles if role.name == "tools"]
    assert tools[0].directory == "cosmos"
    assert SCHEMA == "cosmos-federation-coldroot/1"
    assert list(scratch.iterdir()) == []
    assert "sk-" not in repr(planned)
    assert "Bearer" not in repr(planned)
    assert "api_key" not in repr(planned)


def test_apply_writes_sentinel_and_record_without_a_path_or_a_key(scratch: Path) -> None:
    jail = PathJail(scratch)
    planned = apply(jail, "Peer-1", 1_700_000_000)
    assert planned == plan("Peer-1", 1_700_000_000)
    sentinel_expected = json.dumps(
        {"system": "COSMOS", "tree_id": "Peer-1", "schema_version": 1},
        indent=1,
    ).encode("utf-8")
    record_expected = json.dumps(
        {"tree_id": "Peer-1", "installed_epoch": 1700000000},
        indent=1,
    ).encode("utf-8")
    sentinel_bytes = (scratch / ".cosmos-root.json").read_bytes()
    record_bytes = (scratch / "config" / "install_record.json").read_bytes()
    assert sentinel_bytes == sentinel_expected
    assert record_bytes == record_expected
    loaded: object = json.loads(record_bytes.decode("utf-8"))
    assert isinstance(loaded, dict)
    assert tuple(loaded) == ("tree_id", "installed_epoch")
    assert loaded["installed_epoch"] == 1_700_000_000
    assert not isinstance(loaded["installed_epoch"], bool)
    text = record_bytes.decode("utf-8")
    assert str(scratch) not in text
    assert scratch.drive not in text
    assert "\\\\" not in text
    for role in planned.roles:
        if role.directory == ".":
            continue
        assert (scratch / role.directory).is_dir()
    assert (scratch / "cosmos").is_dir()
    assert not (scratch / "tools").exists()
    assert list(scratch.rglob("install_key.bin")) == []
    assert list(scratch.rglob("api_token.txt")) == []
    names = sorted(path.name for path in (scratch / "config").iterdir())
    assert names == ["install_record.json"]


def test_same_tree_id_is_idempotent(scratch: Path) -> None:
    jail = PathJail(scratch)
    first = apply(jail, "Peer-1", 1_700_000_000)
    sentinel_bytes = (scratch / ".cosmos-root.json").read_bytes()
    record_bytes = (scratch / "config" / "install_record.json").read_bytes()
    second = apply(jail, "Peer-1", 1_700_000_000)
    assert first == second
    assert (scratch / ".cosmos-root.json").read_bytes() == sentinel_bytes
    assert (scratch / "config" / "install_record.json").read_bytes() == record_bytes
    assert list(scratch.rglob("install_key.bin")) == []
    assert list(scratch.rglob("api_token.txt")) == []


def test_later_epoch_keeps_the_same_identity(scratch: Path) -> None:
    jail = PathJail(scratch)
    apply(jail, "Peer-1", 100)
    apply(jail, "Peer-1", 200)
    loaded: object = json.loads((scratch / "config" / "install_record.json").read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    assert loaded["tree_id"] == "Peer-1"
    assert loaded["installed_epoch"] == 200
    assert "root" not in loaded
    sentinel: object = json.loads((scratch / ".cosmos-root.json").read_text(encoding="utf-8"))
    assert isinstance(sentinel, dict)
    assert sentinel["tree_id"] == "Peer-1"
    assert list(scratch.rglob("install_key.bin")) == []


def test_different_tree_id_refuses(scratch: Path) -> None:
    jail = PathJail(scratch)
    apply(jail, "Peer-1", 1_700_000_000)
    before_sentinel = (scratch / ".cosmos-root.json").read_bytes()
    before_record = (scratch / "config" / "install_record.json").read_bytes()
    try:
        apply(jail, "Peer-2", 1_700_000_100)
    except Refuse as exc:
        assert exc.code == "IDENTITY_MISMATCH"
        assert "Peer-1" not in exc.detail
        assert "Peer-2" not in exc.detail
    else:
        raise AssertionError("mismatch")
    assert (scratch / ".cosmos-root.json").read_bytes() == before_sentinel
    assert (scratch / "config" / "install_record.json").read_bytes() == before_record
    assert list(scratch.rglob("install_key.bin")) == []


def test_record_alone_with_another_tree_id_refuses(scratch: Path) -> None:
    jail = PathJail(scratch)
    (scratch / "config").mkdir()
    target = scratch / "config" / "install_record.json"
    target.write_text(
        json.dumps({"tree_id": "Other-1", "installed_epoch": 1}),
        encoding="utf-8",
    )
    before = target.read_bytes()
    try:
        apply(jail, "Peer-1", 20)
    except Refuse as exc:
        assert exc.code == "IDENTITY_MISMATCH"
    else:
        raise AssertionError("record mismatch")
    assert target.read_bytes() == before
    assert not (scratch / ".cosmos-root.json").exists()


def test_empty_tree_id_can_be_finished(scratch: Path) -> None:
    jail = PathJail(scratch)
    (scratch / ".cosmos-root.json").write_text(
        json.dumps({"system": "COSMOS", "tree_id": "", "schema_version": 1}),
        encoding="utf-8",
    )
    apply(jail, "Peer-1", 50)
    loaded: object = json.loads((scratch / ".cosmos-root.json").read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    assert loaded["tree_id"] == "Peer-1"
    assert loaded["system"] == "COSMOS"
    assert loaded["schema_version"] == 1


def test_taken_tree_id_does_not_write(scratch: Path) -> None:
    jail = PathJail(scratch)
    try:
        apply(jail, "KMesh-COSMOS-live", 10)
    except Refuse as exc:
        assert exc.code == "TREE_ID"
    else:
        raise AssertionError("taken")
    assert list(scratch.iterdir()) == []


def test_bool_and_far_epoch_refuse() -> None:
    try:
        plan("Peer-1", True)
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("bool")
    try:
        plan("Peer-1", 10**18)
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("far")
    assert plan("Peer-1", 0).record.installed_epoch == 0
    assert plan("Peer-1", 4_102_444_800).record.installed_epoch == 4_102_444_800


def test_torn_sentinel_refuses(scratch: Path) -> None:
    jail = PathJail(scratch)
    target = scratch / ".cosmos-root.json"
    target.write_text("{", encoding="utf-8")
    try:
        apply(jail, "Peer-1", 10)
    except Refuse as exc:
        assert exc.code == "UNPARSEABLE"
    else:
        raise AssertionError("torn")
    assert target.read_text(encoding="utf-8") == "{"
    assert not (scratch / "config" / "install_record.json").exists()


def test_non_string_tree_id_refuses(scratch: Path) -> None:
    jail = PathJail(scratch)
    (scratch / ".cosmos-root.json").write_text(
        json.dumps({"system": "COSMOS", "tree_id": 1, "schema_version": 1}),
        encoding="utf-8",
    )
    try:
        apply(jail, "Peer-1", 10)
    except Refuse as exc:
        assert exc.code == "UNPARSEABLE"
    else:
        raise AssertionError("number")


def test_file_where_a_role_directory_belongs_refuses(scratch: Path) -> None:
    jail = PathJail(scratch)
    (scratch / "state").write_text("x", encoding="utf-8")
    try:
        apply(jail, "Peer-1", 10)
    except Refuse as exc:
        assert exc.code == "NOT_A_DIRECTORY"
    else:
        raise AssertionError("dir")
    assert not (scratch / ".cosmos-root.json").exists()


def test_apply_leaves_an_existing_key_file_alone(scratch: Path) -> None:
    jail = PathJail(scratch)
    config = scratch / "config"
    config.mkdir()
    key = config / "install_key.bin"
    payload = b"not-written-by-coldroot-0123456789"
    key.write_bytes(payload)
    apply(jail, "Peer-1", 40)
    assert key.read_bytes() == payload
    assert not (config / "api_token.txt").exists()


def test_apply_requires_a_path_jail(scratch: Path) -> None:
    try:
        apply(cast(PathJail, scratch), "Peer-1", 10)
    except Refuse as exc:
        assert exc.code == "JAIL"
    else:
        raise AssertionError("jail")
    assert list(scratch.iterdir()) == []
