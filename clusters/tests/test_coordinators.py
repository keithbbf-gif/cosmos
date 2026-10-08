"""Coordinator scope, goals, plans, and comms."""

from __future__ import annotations

import pytest

from clusters.coordinators import (
    accept_plan,
    ask_session,
    close_worker,
    open_coordinator,
    report,
    set_session_comms,
    submit_goal,
)
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import get_session, open_session, set_status
from clusters.store import Store


def _lead(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    lead = open_coordinator(
        store,
        scope="project",
        project_id=project["id"],
        hero="luna",
        door="codex",
        model="luna",
    )
    return store, project["id"], lead


def test_second_project_coordinator_refuses(tmp_path):
    store, project_id, lead = _lead(tmp_path)
    assert lead["scope"] == "project"
    assert lead["role"] == "coordinator"
    with pytest.raises(Refuse) as refused:
        open_coordinator(
            store,
            scope="project",
            project_id=project_id,
            hero="sol",
            door="codex",
            model="sol",
        )
    assert refused.value.code == "SECOND"


def test_greeting_does_not_start_a_goal(tmp_path):
    store, project_id, lead = _lead(tmp_path)
    greeting = submit_goal(store, lead["id"], "hello")
    assert greeting["started"] is False
    assert greeting["goal"] == "hello"
    assert store.view("goal") == {}
    started = submit_goal(store, lead["id"], "Ship the login fix")
    assert started["started"] is True
    assert started["goal_id"] == f"goal-{lead['id']}"
    assert started["coordinator_id"] == lead["id"]
    goal = store.view("goal")[started["goal_id"]]
    assert goal["state"] == "open"
    assert goal["text"] == "Ship the login fix"
    assert goal["project_id"] == project_id
    assert goal["coordinator_id"] == lead["id"]
    bodies = [row["body"] for row in store.view("message").values()]
    assert bodies == ["hello", "Ship the login fix"]


def test_accept_plan_without_evidence_opens_worker(tmp_path):
    store, project_id, lead = _lead(tmp_path)
    result = accept_plan(
        store,
        lead["id"],
        {
            "workers": [
                {
                    "door": "pi",
                    "hero": "mini",
                    "model": "mini",
                    "task": "write the test",
                    "project_id": project_id,
                }
            ]
        },
        evidence=None,
    )
    assert result["plan_verdict"] == "UNMEASURED"
    assert result["source"] == "operator"
    assert result["coordinator_id"] == lead["id"]
    assert len(result["worker_ids"]) == 1
    worker = get_session(store, result["worker_ids"][0])
    assert worker["parent_id"] == lead["id"]
    assert worker["role"] == "worker"
    assert worker["project_id"] == project_id


def test_accept_plan_with_evidence_is_verified(tmp_path):
    store, project_id, lead = _lead(tmp_path)
    result = accept_plan(
        store,
        lead["id"],
        {
            "workers": [
                {
                    "door": "codex",
                    "hero": "sol",
                    "model": "sol",
                    "task": "implement the fix",
                    "project_id": project_id,
                }
            ]
        },
        evidence={"source": "coordinator", "observed": "delegate the login fix"},
    )
    assert result["plan_verdict"] == "VERIFIED"
    assert result["source"] == "harness"
    assert len(result["worker_ids"]) == 1
    assert get_session(store, result["worker_ids"][0])["parent_id"] == lead["id"]


def test_close_worker_refuses_other_owner(tmp_path):
    store, project_id, lead = _lead(tmp_path)
    other = open_session(store, project_id=project_id, door="codex", task="mine")
    with pytest.raises(Refuse) as refused:
        close_worker(store, lead["id"], other["id"])
    assert refused.value.code == "OWNER"
    assert get_session(store, other["id"])["open"] is True


def test_ask_session_comms_snapshot(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    first = open_session(store, project_id=project["id"], door="codex", task="a")
    second = open_session(store, project_id=project["id"], door="pi", task="b")
    with pytest.raises(Refuse) as refused:
        ask_session(store, sender_id=first["id"], target_id=second["id"], question="status")
    assert refused.value.code == "COMMS_OFF"
    turned = set_session_comms(store, True)
    assert turned["enabled"] is True
    assert turned["applies"] == "sessions opened after this event"
    with pytest.raises(Refuse) as still:
        ask_session(store, sender_id=first["id"], target_id=second["id"], question="again")
    assert still.value.code == "COMMS_OFF"
    left = open_session(store, project_id=project["id"], door="codex", task="c")
    right = open_session(store, project_id=project["id"], door="pi", task="d")
    asked = ask_session(
        store, sender_id=left["id"], target_id=right["id"], question="where is the bug"
    )
    assert asked == {"kind": "request", "sender_id": left["id"], "target_id": right["id"]}
    assert get_session(store, right["id"])["queued"] == 1
    notes = [
        row for row in store.view("message").values() if row.get("session_id") == right["id"]
    ]
    assert notes[0]["kind"] == "request"
    assert notes[0]["sender_id"] == left["id"]
    assert notes[0]["body"] == "where is the bug"


def test_report_sets_polled_false(tmp_path):
    store, project_id, lead = _lead(tmp_path)
    planned = accept_plan(
        store,
        lead["id"],
        {
            "workers": [
                {
                    "door": "opencode",
                    "hero": "glm",
                    "model": "glm",
                    "task": "look",
                    "project_id": project_id,
                }
            ]
        },
        evidence=None,
    )
    worker_id = planned["worker_ids"][0]
    set_status(store, worker_id, "finished", evidence={"source": "log"})
    found = report(store, lead["id"])
    assert found["polled"] is False
    assert found["coordinator_id"] == lead["id"]
    assert len(found["workers"]) == 1
    item = found["workers"][0]
    assert item["id"] == worker_id
    assert item["pending_report"] == "finished"
    assert item["verified_status"] == "idle"
    assert item["verdict"] == "UNMEASURED"
    assert item["title"]
