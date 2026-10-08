"""Skill path flags. A path is stored. A body is not."""

from __future__ import annotations

import hashlib
import json

import pytest

from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.skills import enable_skill, list_skills, skill_for_pack
from clusters.store import Store


def _store(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    return store, project["id"]


def test_newline_path_refuses(tmp_path):
    store, project_id = _store(tmp_path)
    with pytest.raises(Refuse) as refused:
        enable_skill(store, project_id=project_id, path="skills\npytest.md")
    assert refused.value.code == "SKILL"


def test_path_longer_than_240_refuses(tmp_path):
    store, project_id = _store(tmp_path)
    with pytest.raises(Refuse) as refused:
        enable_skill(store, project_id=project_id, path="p" * 241)
    assert refused.value.code == "SKILL"


def test_live_tree_skill_refuses(tmp_path):
    store, project_id = _store(tmp_path)
    with pytest.raises(Refuse) as refused:
        enable_skill(
            store,
            project_id=project_id,
            path=r"V:\A\Ai\COSMOS\live\skill.md",
        )
    assert refused.value.code == "LIVE_TREE"


def test_enable_then_list_shows_enabled(tmp_path):
    store, project_id = _store(tmp_path)
    path = str(tmp_path / "skills" / "pytest.md")
    assert list_skills(store, project_id) == []
    row = enable_skill(store, project_id=project_id, path=path)
    digest = hashlib.sha256(path.encode()).hexdigest()[:12]
    assert row["id"] == f"skill-{project_id}-{digest}"
    assert row["op"] == "set"
    assert row["path"] == path
    assert row["enabled"] is True
    listed = list_skills(store, project_id)
    assert len(listed) == 1
    assert listed[0]["enabled"] is True
    assert listed[0]["path"] == path
    # The projection is JSON, so a Windows path is stored with escaped slashes.
    text = store.path.read_text(encoding="utf-8")
    assert json.dumps(path)[1:-1] in text
    assert "body" not in listed[0]


def test_skill_for_pack_returns_only_the_enabled_path(tmp_path):
    store, project_id = _store(tmp_path)
    kept = str(tmp_path / "skills" / "pytest.md")
    dropped = str(tmp_path / "skills" / "other.md")
    enable_skill(store, project_id=project_id, path=kept)
    enable_skill(store, project_id=project_id, path=dropped, enabled=False)
    assert skill_for_pack(store, project_id) == [kept]


def test_disabling_removes_it_from_skill_for_pack(tmp_path):
    store, project_id = _store(tmp_path)
    path = str(tmp_path / "skills" / "pytest.md")
    enable_skill(store, project_id=project_id, path=path)
    assert skill_for_pack(store, project_id) == [path]
    enable_skill(store, project_id=project_id, path=path, enabled=False)
    assert skill_for_pack(store, project_id) == []
    listed = list_skills(store, project_id)
    assert listed[0]["path"] == path
    assert listed[0]["enabled"] is False


def test_missing_project_refuses(tmp_path):
    store = Store(tmp_path / "c")
    with pytest.raises(Refuse) as refused:
        enable_skill(store, project_id="prj-missing", path="skills/pytest.md")
    assert refused.value.code == "PROJECT"
