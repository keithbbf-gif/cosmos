"""Navbar shortcut outfits. A colour, icon, door, resume, and Turbo are stored.

Nothing here launches. Resume stored on the outfit does not claim a resume.
Turbo stored on the outfit does not apply policy or skip permissions.
"""

from __future__ import annotations

import pytest

from clusters.mesh import create_project
from clusters.presets import get_preset, set_preset
from clusters.refuse import Refuse
from clusters.store import Store


def _project(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="repo", root=str(tmp_path / "repo"))
    return store, project["id"]


def test_good_preset_stores_outfit_and_does_not_claim(tmp_path):
    store, project_id = _project(tmp_path)
    saved = set_preset(
        store,
        project_id=project_id,
        colour="#336699",
        icon="folder",
        door="codex",
        resume=True,
        turbo=True,
    )
    assert saved["id"] == f"preset-{project_id}"
    assert saved["op"] == "set"
    assert saved["project_id"] == project_id
    assert saved["colour"] == "#336699"
    assert saved["icon"] == "folder"
    assert saved["door"] == "codex"
    assert saved["resume"] is True
    assert saved["turbo"] is True
    assert saved["resume_claimed"] is False
    assert saved["applied"] is False
    assert all(not str(key).startswith("_") for key in saved)
    again = get_preset(store, project_id)
    assert again["resume_claimed"] is False
    assert again["applied"] is False
    assert again["colour"] == "#336699"
    assert again["turbo"] is True
    event = store.fold("preset")[-1]["body"]
    assert event["op"] == "set"
    assert event["door"] == "codex"
    assert event["resume"] is True
    assert event["turbo"] is True
    assert event.get("resume_claimed") is not True
    assert event.get("applied") is not True
    assert {row["kind"] for row in store.fold()} == {"project", "preset"}
    assert store.view("session") == {}


def test_bad_door_refuses(tmp_path):
    store, project_id = _project(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_preset(
            store,
            project_id=project_id,
            colour="blue",
            icon="folder",
            door="not-a-door",
        )
    assert refused.value.code == "UNKNOWN_DOOR"
    assert refused.value.detail == "not-a-door"
    assert store.view("preset") == {}


def test_newline_in_colour_refuses(tmp_path):
    store, project_id = _project(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_preset(
            store,
            project_id=project_id,
            colour="blue\ngreen",
            icon="folder",
            door="codex",
        )
    assert refused.value.code == "PRESET"
    assert refused.value.detail == "colour"
    assert store.fold("preset") == []


def test_missing_project_and_missing_preset(tmp_path):
    store = Store(tmp_path / "s")
    with pytest.raises(Refuse) as refused:
        set_preset(
            store,
            project_id="prj-missing",
            colour="blue",
            icon="folder",
            door="codex",
        )
    assert refused.value.code == "PROJECT"
    assert refused.value.detail == "prj-missing"
    project = create_project(store, name="repo", root=str(tmp_path / "repo"))
    with pytest.raises(Refuse) as missing_project:
        get_preset(store, "prj-missing")
    assert missing_project.value.code == "PROJECT"
    assert missing_project.value.detail == ""
    with pytest.raises(Refuse) as missing:
        get_preset(store, project["id"])
    assert missing.value.code == "PRESET"
    assert missing.value.detail == "missing"


def test_flag_must_be_bool(tmp_path):
    store, project_id = _project(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_preset(
            store,
            project_id=project_id,
            colour="blue",
            icon="folder",
            door="codex",
            turbo=1,
        )
    assert refused.value.code == "PRESET"
    assert refused.value.detail == "flag"
    assert store.view("preset") == {}
