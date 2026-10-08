"""Door capability records. Nothing launches.

Storing yolo or full-access does not apply it. A command path is not executed.
applied and started stay false.
"""

from __future__ import annotations

import pytest

from clusters.doorcap import MODES, get_caps, set_caps
from clusters.mesh import create_project
from clusters.refuse import HARD_FLAGS, Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _session(tmp_path, door="codex"):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door=door, task="caps")
    return store, session["id"]


def test_yolo_and_full_access_stay_unapplied(tmp_path):
    # Nothing launches. The mode name is stored and applied stays false.
    store, session_id = _session(tmp_path, door="kimi")
    saved = set_caps(
        store,
        session_id=session_id,
        mode="yolo",
        subagents=False,
        worktree="lane-a",
    )
    assert saved["id"] == f"caps-{session_id}"
    assert saved["session_id"] == session_id
    assert saved["mode"] == "yolo"
    assert saved["provider"] == ""
    assert saved["subagents"] is False
    assert saved["worktree"] == "lane-a"
    assert saved["command_path"] == ""
    assert saved["applied"] is False
    assert saved["started"] is False
    again = set_caps(store, session_id=session_id, mode="full-access")
    assert again["mode"] == "full-access"
    assert again["applied"] is False
    assert again["started"] is False
    shown = get_caps(store, session_id)
    assert shown["mode"] == "full-access"
    assert shown["applied"] is False
    assert shown["started"] is False
    bodies = [row["body"] for row in store.fold("door_cap")]
    assert bodies[0]["mode"] == "yolo"
    assert bodies[0]["applied"] is False
    assert bodies[0]["started"] is False
    assert bodies[1]["applied"] is False
    assert "command" not in bodies[0]
    text = store.path.read_text(encoding="utf-8")
    for flag in HARD_FLAGS:
        assert flag not in text
    assert {row["kind"] for row in store.fold()} == {"project", "session", "door_cap"}


def test_bad_mode_refuses(tmp_path):
    store, session_id = _session(tmp_path)
    assert "bypass" not in MODES
    with pytest.raises(Refuse) as refused:
        set_caps(store, session_id=session_id, mode="bypass")
    assert refused.value.code == "MODE"
    assert store.view("door_cap") == {}


def test_live_command_path_refuses(tmp_path):
    # Nothing launches. A live path is refused before a row is written.
    store, session_id = _session(tmp_path)
    path = r"V:\A\Ai\COSMOS\live\bin\tool.exe"
    with pytest.raises(Refuse) as refused:
        set_caps(store, session_id=session_id, mode="plan", command_path=path)
    assert refused.value.code == "LIVE_TREE"
    assert store.view("door_cap") == {}


def test_grok_exe_path_is_stored_and_not_started(tmp_path):
    # Nothing launches. The resolved grok.exe path is a name, not a start.
    store, session_id = _session(tmp_path, door="grok")
    path = str(tmp_path / "grok.exe")
    saved = set_caps(store, session_id=session_id, mode="plan", command_path=path)
    folded = path.replace("\\", "/").rstrip("/").lower()
    assert folded.endswith("grok.exe")
    assert saved["command_path"] == path
    assert saved["mode"] == "plan"
    assert saved["started"] is False
    assert saved["applied"] is False
    assert get_caps(store, session_id)["started"] is False
    assert store.fold("door_cap")[-1]["body"]["started"] is False
    assert store.fold("door_cap")[-1]["body"]["command_path"] == path


def test_provider_openai(tmp_path):
    store, session_id = _session(tmp_path, door="opencode")
    saved = set_caps(
        store,
        session_id=session_id,
        mode="default",
        provider="openai",
    )
    assert saved["provider"] == "openai"
    assert saved["mode"] == "default"
    assert saved["applied"] is False
    assert saved["started"] is False
    assert get_caps(store, session_id)["provider"] == "openai"
    with pytest.raises(Refuse) as refused:
        set_caps(store, session_id=session_id, mode="default", provider="azure")
    assert refused.value.code == "PROVIDER"
    assert get_caps(store, session_id)["provider"] == "openai"


def test_missing_session_and_missing_row(tmp_path):
    store = Store(tmp_path / "s")
    with pytest.raises(Refuse) as refused:
        set_caps(store, session_id="ses-missing", mode="plan")
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="pi", task="caps")
    with pytest.raises(Refuse) as missing_session:
        get_caps(store, "ses-missing")
    assert missing_session.value.code == "SESSION"
    assert missing_session.value.detail == ""
    with pytest.raises(Refuse) as missing_row:
        get_caps(store, session["id"])
    assert missing_row.value.code == "CAPS"
    assert missing_row.value.detail == "missing"


def test_worktree_and_subagents_refuse(tmp_path):
    store, session_id = _session(tmp_path)
    with pytest.raises(Refuse) as newline:
        set_caps(store, session_id=session_id, mode="auto-edits", worktree="a\nb")
    assert newline.value.code == "CAPS"
    assert newline.value.detail == "worktree"
    with pytest.raises(Refuse) as too_long:
        set_caps(store, session_id=session_id, mode="suggest", worktree="w" * 81)
    assert too_long.value.code == "CAPS"
    assert too_long.value.detail == "worktree"
    with pytest.raises(Refuse) as flag:
        set_caps(store, session_id=session_id, mode="auto", subagents=1)
    assert flag.value.code == "CAPS"
    assert flag.value.detail == "subagents"
    assert store.view("door_cap") == {}
    kept = set_caps(store, session_id=session_id, mode="manual", worktree="w" * 80)
    assert kept["worktree"] == "w" * 80
    assert kept["subagents"] is True
    assert kept["applied"] is False
    assert kept["started"] is False


def test_hard_flag_is_not_stored(tmp_path):
    # Nothing launches. A hard launch flag is refused and is not a row.
    store, session_id = _session(tmp_path)
    flag = HARD_FLAGS[0]
    path = str(tmp_path / f"tool{flag}.exe")
    with pytest.raises(Refuse) as refused:
        set_caps(store, session_id=session_id, mode="manual", command_path=path)
    assert refused.value.code == "FLAG"
    assert refused.value.detail == flag
    assert flag not in store.path.read_text(encoding="utf-8")
    assert store.view("door_cap") == {}


def test_get_caps_forces_applied_and_started_false(tmp_path):
    store, session_id = _session(tmp_path)
    store.append(
        "door_cap",
        {
            "id": f"caps-{session_id}",
            "session_id": session_id,
            "mode": "yolo",
            "provider": "",
            "subagents": True,
            "worktree": "",
            "command_path": "",
            "applied": True,
            "started": True,
        },
    )
    shown = get_caps(store, session_id)
    assert shown["mode"] == "yolo"
    assert shown["applied"] is False
    assert shown["started"] is False
