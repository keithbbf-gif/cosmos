"""Follow-up, correction, and a goal handed to the project coordinator."""

from __future__ import annotations

import pytest

from clusters.coordinators import accept_plan, open_coordinator
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.relay import delegate_project, keep_small, send_worker
from clusters.sessions import get_session, list_sessions, open_session
from clusters.store import Store


def _world(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    lead = open_coordinator(
        store,
        scope="global",
        project_id=project["id"],
        hero="sol",
        door="cosmos-code",
        model="grok-4.7",
    )
    return store, project["id"], lead


def _plan(project_id):
    return {
        "workers": [
            {
                "door": "cosmos-code",
                "hero": "sol",
                "model": "x",
                "task": "implement",
                "project_id": project_id,
            }
        ]
    }


def test_send_worker_followup_queues(tmp_path):
    store, project_id, lead = _world(tmp_path)
    assert lead["comms"] is False
    assert lead["role"] == "global_coordinator"
    planned = accept_plan(store, lead["id"], _plan(project_id), evidence=None)
    worker_id = planned["worker_ids"][0]
    worker = get_session(store, worker_id)
    assert worker["parent_id"] == lead["id"]
    assert worker["comms"] is False
    assert planned["plan_verdict"] == "UNMEASURED"
    assert planned["source"] == "operator"
    sent = send_worker(
        store,
        coordinator_id=lead["id"],
        worker_id=worker_id,
        text="check the edge case",
        kind="followup",
    )
    assert sent == {"kind": "followup", "worker_id": worker_id, "queued": True}
    assert get_session(store, worker_id)["queued"] == 1
    notes = [
        row
        for row in store.view("message").values()
        if row.get("session_id") == worker_id and row.get("kind") == "followup"
    ]
    assert len(notes) == 1
    assert notes[0]["role"] == "coordinator"
    assert notes[0]["kind"] == "followup"
    assert notes[0]["body"] == "check the edge case"
    corrected = send_worker(
        store,
        coordinator_id=lead["id"],
        worker_id=worker_id,
        text="use the public helper",
        kind="correction",
    )
    assert corrected["kind"] == "correction"
    assert corrected["queued"] is True
    assert get_session(store, worker_id)["queued"] == 2
    with pytest.raises(Refuse) as empty:
        send_worker(
            store,
            coordinator_id=lead["id"],
            worker_id=worker_id,
            text="",
            kind="followup",
        )
    assert empty.value.code == "MESSAGE"


def test_send_worker_assignment_refuses_kind(tmp_path):
    store, project_id, lead = _world(tmp_path)
    planned = accept_plan(store, lead["id"], _plan(project_id), evidence=None)
    worker_id = planned["worker_ids"][0]
    before = [
        row["kind"]
        for row in store.view("message").values()
        if row.get("session_id") == worker_id
    ]
    with pytest.raises(Refuse) as refused:
        send_worker(
            store,
            coordinator_id=lead["id"],
            worker_id=worker_id,
            text="this is not a follow-up",
            kind="assignment",
        )
    assert refused.value.code == "KIND"
    after = [
        row["kind"]
        for row in store.view("message").values()
        if row.get("session_id") == worker_id
    ]
    assert after == before
    assert get_session(store, worker_id)["queued"] == 0


def test_send_worker_other_parent_refuses_owner(tmp_path):
    store, project_id, lead = _world(tmp_path)
    other = open_session(
        store,
        project_id=project_id,
        door="cosmos-code",
        hero="sol",
        model="x",
        task="implement",
        role="worker",
    )
    stranger = open_session(
        store,
        project_id=project_id,
        door="cosmos-code",
        hero="sol",
        model="x",
        task="implement",
        role="worker",
        parent_id=other["id"],
    )
    with pytest.raises(Refuse) as refused:
        send_worker(
            store,
            coordinator_id=lead["id"],
            worker_id=stranger["id"],
            text="check the edge case",
            kind="followup",
        )
    assert refused.value.code == "OWNER"
    assert get_session(store, stranger["id"])["queued"] == 0
    assert get_session(store, stranger["id"])["parent_id"] == other["id"]


def test_keep_small_does_not_grow_sessions(tmp_path):
    store, _project_id, lead = _world(tmp_path)
    before = len(list_sessions(store))
    held = keep_small(store, coordinator_id=lead["id"], text="Answer the status question here")
    assert held == {"delegated": False, "opened": 0}
    assert len(list_sessions(store)) == before
    assert len(store.view("session")) == before
    notes = [
        row for row in store.view("message").values() if row.get("session_id") == lead["id"]
    ]
    assert notes[-1]["role"] == "coordinator"
    assert notes[-1]["kind"] == "system"
    assert notes[-1]["body"] == "Answer the status question here"
    outsider = open_session(
        store,
        project_id=lead["project_id"],
        door="cosmos-code",
        hero="sol",
        model="x",
        task="implement",
    )
    grown = len(list_sessions(store))
    with pytest.raises(Refuse) as refused:
        keep_small(store, coordinator_id=outsider["id"], text="do not open anyone")
    assert refused.value.code == "ROLE"
    assert len(list_sessions(store)) == grown


def test_delegate_project_reuses_coordinator(tmp_path):
    store, project_id, lead = _world(tmp_path)
    before = len(list_sessions(store))
    first = delegate_project(
        store,
        global_id=lead["id"],
        project_id=project_id,
        text="Ship the login fix",
        door="cosmos-code",
        hero="sol",
        model="grok-4.7",
    )
    assert first["delegated"] is True
    assert first["reused"] is False
    assert len(list_sessions(store)) == before + 1
    seat = get_session(store, first["coordinator_id"])
    assert seat["role"] == "coordinator"
    assert seat["project_id"] == project_id
    assert seat["door"] == "cosmos-code"
    assert seat["hero"] == "sol"
    assert seat["model"] == "grok-4.7"
    assert seat["comms"] is False
    second = delegate_project(
        store,
        global_id=lead["id"],
        project_id=project_id,
        text="Ship the login fix again",
        door="codex",
        hero="luna",
        model="other-model",
    )
    assert second == {
        "delegated": True,
        "coordinator_id": first["coordinator_id"],
        "reused": True,
    }
    assert len(list_sessions(store)) == before + 1
    again = get_session(store, second["coordinator_id"])
    assert again["door"] == "cosmos-code"
    assert again["model"] == "grok-4.7"
    roles = [row.get("role") for row in store.view("session").values()]
    assert roles.count("global_coordinator") == 1
    assert roles.count("coordinator") == 1
    assert "worker" not in roles
    goal = store.view("goal")[f"goal-{first['coordinator_id']}"]
    assert goal["text"] == "Ship the login fix again"
    assert goal["coordinator_id"] == first["coordinator_id"]
    with pytest.raises(Refuse) as refused:
        delegate_project(
            store,
            global_id=first["coordinator_id"],
            project_id=project_id,
            text="Ship a third coordinator",
            door="cosmos-code",
            hero="sol",
            model="grok-4.7",
        )
    assert refused.value.code == "ROLE"
    roles = [row.get("role") for row in store.view("session").values()]
    assert roles.count("global_coordinator") == 1
    assert roles.count("coordinator") == 1
    assert "worker" not in roles
    assert len(list_sessions(store)) == before + 1
