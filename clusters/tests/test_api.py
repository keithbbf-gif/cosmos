"""HTTP API against a fake console. Loopback only."""

from __future__ import annotations

import json
import socket
import threading
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from clusters.api import make_handler, serve
from clusters.refuse import Refuse

_LISTS = {
    "list_projects",
    "list_clusters",
    "list_sessions",
    "list_tasks",
    "list_changes",
    "list_doors",
    "list_mcp",
    "list_shortcuts",
    "list_notifications",
    "list_skills",
    "skill_pack",
    "list_titles",
    "list_subtasks",
    "list_bookmarks",
    "list_attention",
    "list_instructions",
    "list_conflicts",
}


class _Health:
    def health(self):
        return {"status": "ok", "service": "clusters"}


class _SessionCap:
    def __init__(self):
        self.calls = []

    def open_session(self, **kwargs):
        self.calls.append(kwargs)
        raise Refuse("SESSION_CAP", "50")


class _Recorder:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(**kwargs):
            self.calls.append((name, kwargs))
            if name in _LISTS:
                return [name]
            return {"ok": name}

        return _call


def _serve(console):
    server = serve(console, port=0)
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.05},
        daemon=True,
    )
    thread.start()
    return server, thread


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def _request(server, method, path, payload=None, raw=None):
    host, port = server.server_address[:2]
    conn = HTTPConnection(host, port, timeout=5)
    try:
        if raw is not None:
            conn.request(method, path, body=raw, headers={"Content-Type": "application/json"})
        elif payload is not None:
            data = json.dumps(payload).encode("utf-8")
            conn.request(method, path, body=data, headers={"Content-Type": "application/json"})
        else:
            conn.request(method, path)
        resp = conn.getresponse()
        raw_body = resp.read()
        ctype = resp.getheader("Content-Type") or ""
        status = resp.status
    finally:
        conn.close()
    assert ctype.startswith("application/json"), (path, ctype, raw_body)
    return status, json.loads(raw_body.decode("utf-8"))


def test_bind_refuses_before_listen(monkeypatch):
    created = []

    def _no_socket(*args, **kwargs):
        created.append(args)
        raise OSError("listen blocked")

    monkeypatch.setattr(socket, "socket", _no_socket)
    for host in ("0.0.0.0", "localhost"):
        with pytest.raises(Refuse) as caught:
            serve(object(), host=host, port=0)
        assert caught.value.code == "BIND"
        assert caught.value.detail == host
    assert created == []


def test_health_returns_the_fake_dict():
    handler = make_handler(_Health())
    assert issubclass(handler, BaseHTTPRequestHandler)
    server, thread = _serve(_Health())
    try:
        assert isinstance(server, ThreadingHTTPServer)
        assert server.server_address[0] == "127.0.0.1"
        status, body = _request(server, "GET", "/v1/health")
        assert status == 200
        assert body == {"status": "ok", "service": "clusters"}
    finally:
        _stop(server, thread)


def test_missing_route():
    fake = _Recorder()
    server, thread = _serve(fake)
    try:
        status, body = _request(server, "GET", "/v1/missing")
        assert status == 404
        assert body == {"error": "ROUTE", "detail": "/v1/missing"}
        status, body = _request(server, "GET", "/v1/missing?x=1")
        assert status == 404
        assert body == {"error": "ROUTE", "detail": "/v1/missing"}
        assert fake.calls == []
    finally:
        _stop(server, thread)


def test_session_cap_passes_json_kwargs():
    fake = _SessionCap()
    server, thread = _serve(fake)
    try:
        status, body = _request(
            server,
            "POST",
            "/v1/sessions",
            {"project_id": "proj-1", "door": "cursor", "hero": "sol", "task": "ship the api"},
        )
        assert status == 409
        assert body == {"error": "SESSION_CAP", "detail": "50"}
        assert fake.calls == [{
            "project_id": "proj-1",
            "door": "cursor",
            "hero": "sol",
            "model": "",
            "task": "ship the api",
            "role": "worker",
            "account_id": "",
            "cluster_id": "",
            "parent_id": "",
            "title": "",
        }]
    finally:
        _stop(server, thread)


def test_bad_json():
    fake = _SessionCap()
    server, thread = _serve(fake)
    try:
        for raw in (b"{", b"[1]", b"null"):
            status, body = _request(server, "POST", "/v1/sessions", raw=raw)
            assert status == 400
            assert set(body) == {"error", "detail"}
            assert body["error"] == "JSON"
            assert isinstance(body["detail"], str) and body["detail"]
        assert fake.calls == []
    finally:
        _stop(server, thread)


def test_import_does_not_load_console():
    import sys

    assert "clusters.console" not in sys.modules


_CASES = (
    ("GET", "/v1/health", None, "health", {}),
    ("GET", "/v1/features", None, "features", {}),
    ("POST", "/v1/projects", {"name": "Demo", "root": "V:/work/demo"}, "create_project", {
        "name": "Demo",
        "root": "V:/work/demo",
    }),
    ("GET", "/v1/projects", None, "list_projects", {}),
    ("POST", "/v1/projects/p1/shortcut", {"slot": 3}, "shortcut", {
        "project_id": "p1",
        "slot": 3,
    }),
    ("POST", "/v1/clusters", {"name": "core", "project_id": "p1"}, "create_cluster", {
        "name": "core",
        "project_id": "p1",
        "parent_id": "",
    }),
    ("GET", "/v1/clusters?project=p9", None, "list_clusters", {"project_id": "p9"}),
    ("GET", "/v1/clusters", None, "list_clusters", {"project_id": ""}),
    ("POST", "/v1/clusters/c1/members", {
        "member_kind": "agent",
        "member_id": "sol",
    }, "add_member", {
        "cluster_id": "c1",
        "member_kind": "agent",
        "member_id": "sol",
    }),
    ("POST", "/v1/clusters/c1/manager", {"session_id": "ses"}, "set_manager", {
        "cluster_id": "c1",
        "session_id": "ses",
    }),
    ("POST", "/v1/packs", {"scope": "project", "target_id": "p1", "rules": ["no-live"]}, "attach_pack", {
        "scope": "project",
        "target_id": "p1",
        "rules": ["no-live"],
        "skills": None,
        "wrappers": None,
        "environments": None,
    }),
    ("POST", "/v1/sessions", {
        "project_id": "p1",
        "door": "codex",
        "hero": "luna",
        "model": "m1",
        "task": "t",
        "role": "coordinator",
        "account_id": "a",
        "cluster_id": "c",
        "parent_id": "parent",
        "title": "Title",
    }, "open_session", {
        "project_id": "p1",
        "door": "codex",
        "hero": "luna",
        "model": "m1",
        "task": "t",
        "role": "coordinator",
        "account_id": "a",
        "cluster_id": "c",
        "parent_id": "parent",
        "title": "Title",
    }),
    ("GET", "/v1/sessions?project=my%20proj", None, "list_sessions", {"project_id": "my proj"}),
    ("GET", "/v1/sessions", None, "list_sessions", {"project_id": ""}),
    ("POST", "/v1/sessions/ses/status", {
        "status": "finished",
        "evidence": {"source": "diff", "observed": "sha256:abc"},
    }, "set_status", {
        "session_id": "ses",
        "status": "finished",
        "evidence": {"source": "diff", "observed": "sha256:abc"},
    }),
    ("POST", "/v1/sessions/ses/title", {"title": "Shown"}, "set_title", {
        "session_id": "ses",
        "title": "Shown",
        "evidence": None,
    }),
    ("POST", "/v1/sessions/ses/layout", {"view": "tabs", "bounds": {"x": 0, "y": 1, "w": 2, "h": 3}}, "put_layout", {
        "session_id": "ses",
        "view": "tabs",
        "bounds": {"x": 0, "y": 1, "w": 2, "h": 3},
    }),
    ("POST", "/v1/sessions/ses/close", {}, "close_session", {
        "session_id": "ses",
        "confirm": False,
    }),
    ("POST", "/v1/sessions/ses/close", {"confirm": True}, "close_session", {
        "session_id": "ses",
        "confirm": True,
    }),
    ("POST", "/v1/coordinators", {
        "scope": "project",
        "project_id": "p1",
        "hero": "sol",
        "door": "cursor",
        "model": "m",
    }, "open_coordinator", {
        "scope": "project",
        "project_id": "p1",
        "hero": "sol",
        "door": "cursor",
        "model": "m",
    }),
    ("POST", "/v1/coordinators/co1/goal", {"text": "ship"}, "submit_goal", {
        "coordinator_id": "co1",
        "text": "ship",
    }),
    ("POST", "/v1/coordinators/co1/plan", {"plan": {"steps": ["a"]}}, "accept_plan", {
        "coordinator_id": "co1",
        "plan": {"steps": ["a"]},
        "evidence": None,
    }),
    ("POST", "/v1/coordinators/co1/report", {}, "report", {"coordinator_id": "co1"}),
    ("POST", "/v1/coordinators/co1/close-worker", {"worker_id": "w1"}, "close_worker", {
        "coordinator_id": "co1",
        "worker_id": "w1",
        "confirm": False,
    }),
    ("POST", "/v1/comms", {
        "sender_id": "a",
        "target_id": "b",
        "question": "status?",
    }, "ask_session", {
        "sender_id": "a",
        "target_id": "b",
        "question": "status?",
    }),
    ("POST", "/v1/comms/setting", {"enabled": True}, "set_session_comms", {"enabled": True}),
    ("POST", "/v1/board/tasks", {"project_id": "p1", "title": "Fix"}, "add_task", {
        "project_id": "p1",
        "title": "Fix",
        "body": "",
        "column": "pending",
        "door": "",
        "hero": "",
        "model": "",
        "labels": None,
        "workspace": "",
    }),
    ("GET", "/v1/board/tasks?project=p1", None, "list_tasks", {"project_id": "p1"}),
    ("GET", "/v1/board/tasks", None, "list_tasks", {"project_id": ""}),
    ("POST", "/v1/board/tasks/t1/move", {"column": "testing"}, "move_task", {
        "task_id": "t1",
        "column": "testing",
        "evidence": None,
    }),
    ("POST", "/v1/board/auto", {}, "auto_tick", {"limit": None, "project_id": ""}),
    ("POST", "/v1/board/auto", {"limit": 2, "project_id": "p1"}, "auto_tick", {
        "limit": 2,
        "project_id": "p1",
    }),
    ("POST", "/v1/history/messages", {
        "session_id": "ses",
        "role": "user",
        "kind": "user",
        "body": "hi",
    }, "add_message", {
        "session_id": "ses",
        "role": "user",
        "kind": "user",
        "body": "hi",
        "resume_of": "",
    }),
    ("GET", "/v1/history/search?q=title&project=p1", None, "search", {
        "query": "title",
        "project_id": "p1",
    }),
    ("GET", "/v1/history/search?q=title", None, "search", {
        "query": "title",
        "project_id": "",
    }),
    ("GET", "/v1/history/ses/resume", None, "resume_pointer", {"session_id": "ses"}),
    ("POST", "/v1/changes", {
        "session_id": "ses",
        "path": "a.py",
        "before": "a",
        "after": "b",
        "diff": "+b",
    }, "record_change", {
        "session_id": "ses",
        "path": "a.py",
        "before": "a",
        "after": "b",
        "diff": "+b",
    }),
    ("GET", "/v1/changes?session=ses", None, "list_changes", {"session_id": "ses"}),
    ("GET", "/v1/changes", None, "list_changes", {"session_id": ""}),
    ("POST", "/v1/git/worktree", {"session_id": "ses", "repo": "V:/work/demo"}, "plan_worktree", {
        "session_id": "ses",
        "repo": "V:/work/demo",
    }),
    ("POST", "/v1/git/commit-proposal", {"session_id": "ses", "summary": "add api"}, "propose_commit", {
        "session_id": "ses",
        "summary": "add api",
    }),
    ("POST", "/v1/git/push", {"session_id": "ses", "branch": "feature"}, "request_push", {
        "session_id": "ses",
        "branch": "feature",
        "confirmed": False,
    }),
    ("POST", "/v1/git/push", {
        "session_id": "ses",
        "branch": "feature",
        "confirmed": True,
    }, "request_push", {
        "session_id": "ses",
        "branch": "feature",
        "confirmed": True,
    }),
    ("POST", "/v1/policy/check", {"command": "git status"}, "check_command", {
        "command": "git status",
        "turbo": False,
        "branch": "",
    }),
    ("POST", "/v1/policy/limits", {"allow": ["git status"]}, "set_limits", {
        "allow": ["git status"],
        "deny": None,
    }),
    ("POST", "/v1/spend/budget", {"provider": "openai", "daily_cap_usd": 2.5}, "set_budget", {
        "provider": "openai",
        "daily_cap_usd": 2.5,
        "daily_cap_tokens": 0,
        "mode": "cap",
        "on_limit": "pause",
        "window_days": 1,
        "day_index": 0,
    }),
    ("POST", "/v1/spend/budget", {
        "provider": "anthropic",
        "daily_cap_usd": 4,
        "daily_cap_tokens": 100,
        "mode": "smart_pace",
        "on_limit": "stop",
        "window_days": 3,
        "day_index": 2,
    }, "set_budget", {
        "provider": "anthropic",
        "daily_cap_usd": 4,
        "daily_cap_tokens": 100,
        "mode": "smart_pace",
        "on_limit": "stop",
        "window_days": 3,
        "day_index": 2,
    }),
    ("POST", "/v1/spend/observe", {"provider": "openai", "usd": 0.1}, "observe_spend", {
        "provider": "openai",
        "usd": 0.1,
        "tokens": 0,
        "source": "",
        "observed": "",
        "day_index": 0,
    }),
    ("POST", "/v1/spend/bump", {"provider": "openai", "nope": 1}, "bump_today", {
        "provider": "openai",
    }),
    ("POST", "/v1/spend/check", {"provider": "openai"}, "check_spend", {
        "provider": "openai",
        "usd": 0,
        "tokens": 0,
    }),
    ("GET", "/v1/spend", None, "spend_report", {}),
    ("GET", "/v1/doors", None, "list_doors", {}),
    ("POST", "/v1/accounts", {
        "provider": "openai",
        "label": "work",
        "profile_dir": "V:/profiles/work",
    }, "add_account", {
        "provider": "openai",
        "label": "work",
        "profile_dir": "V:/profiles/work",
    }),
    ("POST", "/v1/accounts/acc/bind", {"session_id": "ses"}, "bind_account", {
        "account_id": "acc",
        "session_id": "ses",
    }),
    ("POST", "/v1/mcp", {"project_id": "p1", "server_id": "box", "enabled": False}, "set_mcp", {
        "project_id": "p1",
        "server_id": "box",
        "enabled": False,
    }),
    ("POST", "/v1/mcp/enable-all", {"project_id": "p1"}, "enable_all_mcp", {"project_id": "p1"}),
    ("GET", "/v1/mcp?project=p1", None, "list_mcp", {"project_id": "p1"}),
    ("GET", "/v1/mcp", None, "list_mcp", {"project_id": ""}),
    ("POST", "/v1/shortcuts", {"kind": "global", "binding": "ctrl+1", "target": "p1"}, "add_shortcut", {
        "kind": "global",
        "binding": "ctrl+1",
        "target": "p1",
    }),
    ("GET", "/v1/shortcuts", None, "list_shortcuts", {}),
    ("POST", "/v1/mobile/pair", {}, "pair_mobile", {}),
    ("POST", "/v1/mobile/desktop", {"online": False}, "set_desktop", {"online": False}),
    ("POST", "/v1/mobile/message", {
        "token": "pair-token",
        "session_id": "ses",
        "body": "ping",
    }, "mobile_message", {
        "token": "pair-token",
        "session_id": "ses",
        "body": "ping",
    }),
    ("GET", "/v1/notifications", None, "list_notifications", {}),
    ("POST", "/v1/notifications/note%201/see", {}, "see_notification", {"note_id": "note 1"}),
    ("POST", "/v1/harness/plan", {"hero": "sol", "task": "t", "where": "V:/work"}, "plan_harness", {
        "hero": "sol",
        "task": "t",
        "where": "V:/work",
        "via": "cosmos-code",
        "execute": False,
    }),
    ("POST", "/v1/harness/plan", {
        "hero": "sol",
        "task": "t",
        "where": "V:/work",
        "via": "direct",
        "execute": True,
    }, "plan_harness", {
        "hero": "sol",
        "task": "t",
        "where": "V:/work",
        "via": "direct",
        "execute": True,
    }),
    ("POST", "/v1/policy/matrix", {}, "set_matrix", {
        "file": "ask",
        "shell": "ask",
        "git": "ask",
        "network": "ask",
        "mcp": "ask",
    }),
    ("POST", "/v1/policy/decide", {"category": "git", "command": "git status"}, "decide", {
        "category": "git",
        "command": "git status",
        "turbo": False,
    }),
    ("POST", "/v1/sessions/ses/link", {"status": "finished"}, "link_status", {
        "session_id": "ses",
        "status": "finished",
        "evidence": None,
        "detail": "",
    }),
    ("POST", "/v1/skills", {"project_id": "p1", "path": "skills/pytest.md"}, "enable_skill", {
        "project_id": "p1",
        "path": "skills/pytest.md",
        "enabled": True,
    }),
    ("GET", "/v1/skills/pack?project=p1", None, "skill_pack", {"project_id": "p1"}),
    ("GET", "/v1/skills?project=p1", None, "list_skills", {"project_id": "p1"}),
    ("GET", "/v1/skills", None, "list_skills", {"project_id": ""}),
    ("POST", "/v1/quota/window", {
        "provider": "openai",
        "limit_usd": 1.5,
        "period_seconds": 86400,
        "resets_at": 100.0,
        "source": "operator",
        "observed": "1.5",
    }, "set_quota_window", {
        "provider": "openai",
        "limit_usd": 1.5,
        "period_seconds": 86400,
        "resets_at": 100.0,
        "source": "operator",
        "observed": "1.5",
    }),
    ("POST", "/v1/quota/used", {
        "provider": "openai",
        "used_usd": 0.2,
        "source": "cli",
        "observed": "0.2",
    }, "mark_quota_used", {
        "provider": "openai",
        "used_usd": 0.2,
        "source": "cli",
        "observed": "0.2",
    }),
    ("POST", "/v1/quota/prorata", {"provider": "openai", "now": 50.0}, "quota_prorata", {
        "provider": "openai",
        "now": 50.0,
    }),
    ("POST", "/v1/relay/worker", {
        "coordinator_id": "co",
        "worker_id": "w",
        "text": "fix",
        "kind": "followup",
    }, "send_worker", {
        "coordinator_id": "co",
        "worker_id": "w",
        "text": "fix",
        "kind": "followup",
    }),
    ("POST", "/v1/relay/small", {"coordinator_id": "co", "text": "typo"}, "keep_small", {
        "coordinator_id": "co",
        "text": "typo",
    }),
    ("POST", "/v1/relay/delegate", {
        "global_id": "g",
        "project_id": "p1",
        "text": "ship",
        "door": "codex",
        "hero": "sol",
        "model": "m",
    }, "delegate_project", {
        "global_id": "g",
        "project_id": "p1",
        "text": "ship",
        "door": "codex",
        "hero": "sol",
        "model": "m",
    }),
    ("POST", "/v1/sessions/ses/mode", {"mode": "plan"}, "set_mode", {
        "session_id": "ses",
        "mode": "plan",
    }),
    ("POST", "/v1/sessions/ses/cancel", {}, "cancel_session", {"session_id": "ses"}),
    ("POST", "/v1/mobile/follow", {"token": "pair-token"}, "follow_mobile", {
        "token": "pair-token",
    }),
    ("POST", "/v1/shortcuts/seed", {}, "seed_keys", {}),
    ("POST", "/v1/board/defaults", {"project_id": "p1", "door": "codex"}, "set_lane_defaults", {
        "project_id": "p1",
        "door": "codex",
        "hero": "",
        "model": "",
        "reasoning": "medium",
        "permission": "default",
        "workspace": "worktree",
    }),
    ("POST", "/v1/board/tasks/t1/drag", {}, "queue_drag", {"task_id": "t1"}),
    ("POST", "/v1/board/tasks/t1/lightning", {"reasoning": "high"}, "queue_lightning", {
        "task_id": "t1",
        "door": "",
        "hero": "",
        "model": "",
        "reasoning": "high",
        "permission": "",
        "workspace": "",
    }),
    ("POST", "/v1/board/queue", {"project_id": "p1", "title": "Fix"}, "queue_new", {
        "project_id": "p1",
        "title": "Fix",
        "body": "",
        "door": "",
        "hero": "",
        "model": "",
        "reasoning": "",
        "permission": "",
        "workspace": "",
        "labels": None,
    }),
    ("POST", "/v1/git/classify", {"command": "git status"}, "classify_git", {
        "command": "git status",
    }),
    ("POST", "/v1/git/message", {"session_id": "ses"}, "propose_message", {
        "session_id": "ses",
        "evidence": None,
        "style": "detailed",
    }),
    ("POST", "/v1/git/review", {
        "session_id": "ses",
        "summary": "Review 1 file(s)",
    }, "propose_review", {
        "session_id": "ses",
        "summary": "Review 1 file(s)",
    }),
    ("GET", "/v1/sessions/ses/titles", None, "list_titles", {"session_id": "ses"}),
    ("POST", "/v1/board/tasks/t1/subtasks", {"title": "Child"}, "add_subtask", {
        "parent_id": "t1",
        "title": "Child",
        "body": "",
    }),
    ("GET", "/v1/board/tasks/t1/subtasks", None, "list_subtasks", {"parent_id": "t1"}),
    ("POST", "/v1/bookmarks", {"session_id": "ses"}, "add_bookmark", {
        "session_id": "ses",
        "message_id": "",
        "note": "",
    }),
    ("POST", "/v1/bookmarks/bmk1/hide", {}, "hide_bookmark", {"bookmark_id": "bmk1"}),
    ("GET", "/v1/bookmarks?session=ses", None, "list_bookmarks", {"session_id": "ses"}),
    ("GET", "/v1/bookmarks", None, "list_bookmarks", {"session_id": ""}),
    ("POST", "/v1/spend/admit", {"provider": "openai", "now": 50}, "admit", {
        "provider": "openai",
        "now": 50,
        "usd": 0,
        "tokens": 0,
    }),
    ("POST", "/v1/git/confirm", {
        "session_id": "ses",
        "branch": "main",
        "clean": True,
    }, "record_confirm", {
        "session_id": "ses",
        "branch": "main",
        "clean": True,
        "evidence": None,
    }),
    ("POST", "/v1/board/tasks/t1/isolation", {
        "base_ref": "origin/main",
        "share": "own",
        "workspace": "worktree",
    }, "plan_isolation", {
        "task_id": "t1",
        "base_ref": "origin/main",
        "share": "own",
        "workspace": "worktree",
        "why": "",
        "paths": None,
    }),
    ("POST", "/v1/sessions/ses/binding", {"door": "codex", "model": "gpt"}, "bind_seat", {
        "session_id": "ses",
        "door": "codex",
        "model": "gpt",
    }),
    ("GET", "/v1/sessions/ses/binding", None, "get_binding", {"session_id": "ses"}),
    ("POST", "/v1/attention", {"session_id": "ses", "reason": "question"}, "note_attention", {
        "session_id": "ses",
        "reason": "question",
    }),
    ("GET", "/v1/attention?session=ses", None, "list_attention", {"session_id": "ses"}),
    ("GET", "/v1/attention", None, "list_attention", {"session_id": ""}),
    ("POST", "/v1/sessions/ses/thread", {"state": "active"}, "set_thread", {
        "session_id": "ses",
        "state": "active",
        "until": 0,
    }),
    ("GET", "/v1/sessions/ses/thread", None, "get_thread", {"session_id": "ses"}),
    ("POST", "/v1/projects/p1/preset", {
        "colour": "blue",
        "icon": "bug",
        "door": "codex",
    }, "set_preset", {
        "project_id": "p1",
        "colour": "blue",
        "icon": "bug",
        "door": "codex",
        "resume": False,
        "turbo": False,
    }),
    ("GET", "/v1/projects/p1/preset", None, "get_preset", {"project_id": "p1"}),
    ("POST", "/v1/board/tasks/t1/attach", {"work_style": "Normal"}, "attach_task", {
        "task_id": "t1",
        "work_style": "Normal",
        "style_text": "",
        "images": None,
    }),
    ("POST", "/v1/sessions/ses/seen", {"path": "src/app.py"}, "mark_seen", {
        "session_id": "ses",
        "path": "src/app.py",
        "seen": True,
    }),
    ("GET", "/v1/sessions/ses/review", None, "review_paths", {"session_id": "ses"}),
    ("POST", "/v1/instructions", {
        "project_id": "p1",
        "kind": "agents",
        "path": "AGENTS.md",
    }, "add_instruction", {
        "project_id": "p1",
        "kind": "agents",
        "path": "AGENTS.md",
    }),
    ("GET", "/v1/instructions?project=p1", None, "list_instructions", {"project_id": "p1"}),
    ("POST", "/v1/projects/p1/import", {"result": "skipped"}, "set_import", {
        "project_id": "p1",
        "result": "skipped",
    }),
    ("POST", "/v1/sessions/ses/door-id", {
        "conversation_id": "thr-1",
        "home": "native",
    }, "set_door_id", {
        "session_id": "ses",
        "conversation_id": "thr-1",
        "home": "native",
    }),
    ("GET", "/v1/sessions/ses/door-id", None, "get_door_id", {"session_id": "ses"}),
    ("POST", "/v1/sessions/ses/route", {
        "route": "browser-login",
        "path": "C:/Users/me/.codex",
    }, "set_route", {
        "session_id": "ses",
        "route": "browser-login",
        "path": "C:/Users/me/.codex",
    }),
    ("GET", "/v1/sessions/ses/route", None, "get_route", {"session_id": "ses"}),
    ("POST", "/v1/quota/shape", {
        "provider": "anthropic",
        "shape": "weekly",
        "limit_label": "weekly cap",
        "source": "usage",
        "observed": "weekly cap",
    }, "set_shape", {
        "provider": "anthropic",
        "shape": "weekly",
        "limit_label": "weekly cap",
        "source": "usage",
        "observed": "weekly cap",
    }),
    ("POST", "/v1/quota/shape/gate", {
        "provider": "anthropic",
        "shape": "weekly",
    }, "shape_gate", {
        "provider": "anthropic",
        "shape": "weekly",
    }),
    ("POST", "/v1/sessions/ses/caps", {"mode": "plan"}, "set_caps", {
        "session_id": "ses",
        "mode": "plan",
        "provider": "",
        "subagents": True,
        "worktree": "",
        "command_path": "",
    }),
    ("GET", "/v1/sessions/ses/caps", None, "get_caps", {"session_id": "ses"}),
    ("POST", "/v1/sessions/ses/host", {
        "host": "windows",
        "fact": "voice",
        "enabled": False,
    }, "set_host", {
        "session_id": "ses",
        "host": "windows",
        "fact": "voice",
        "enabled": False,
    }),
    ("POST", "/v1/sessions/ses/env", {"name": "BASE_URL"}, "set_env_name", {
        "session_id": "ses",
        "name": "BASE_URL",
    }),
    ("POST", "/v1/conflicts", {
        "session_id": "ses",
        "path": "src/app.py",
        "outcome": "unresolved",
    }, "record_conflict", {
        "session_id": "ses",
        "path": "src/app.py",
        "outcome": "unresolved",
    }),
    ("GET", "/v1/conflicts?session=ses", None, "list_conflicts", {"session_id": "ses"}),
    ("GET", "/v1/conflicts", None, "list_conflicts", {"session_id": ""}),
    ("POST", "/v1/tools", {
        "project_id": "p1",
        "server_id": "playwright",
        "tool": "browse",
        "level": "deny",
    }, "set_tool", {
        "project_id": "p1",
        "server_id": "playwright",
        "tool": "browse",
        "level": "deny",
    }),
    ("GET", "/v1/tools?project=p1&server=playwright&tool=browse", None, "tool_level", {
        "project_id": "p1",
        "server_id": "playwright",
        "tool": "browse",
    }),
    ("POST", "/v1/sessions/ses/headless", {}, "plan_headless", {
        "session_id": "ses",
        "output_format": "plain",
        "max_turns": 1,
        "sandbox": "",
    }),
    ("GET", "/v1/sessions/ses/headless", None, "get_headless", {"session_id": "ses"}),
    ("POST", "/v1/sessions/ses/flags", {}, "set_seat_flags", {
        "session_id": "ses",
        "channel": "stable",
        "role": "",
        "tool_search": False,
        "web_fetch": False,
        "hooks_off": False,
        "auto_update": False,
        "lock_path": "",
    }),
    ("GET", "/v1/sessions/ses/flags", None, "get_seat_flags", {"session_id": "ses"}),
    ("POST", "/v1/quota/meter", {
        "provider": "openai",
        "reading": "capped",
        "pool": "window",
    }, "set_meter", {
        "provider": "openai",
        "reading": "capped",
        "pool": "window",
        "auto_reload": False,
        "source": "",
        "observed": "",
    }),
    ("POST", "/v1/quota/meter/gate", {
        "provider": "openai",
        "pool": "window",
    }, "meter_gate", {
        "provider": "openai",
        "pool": "window",
    }),
)


def test_routes_call_console_with_named_arguments():
    fake = _Recorder()
    server, thread = _serve(fake)
    try:
        for method, path, payload, fn, kwargs in _CASES:
            status, body = _request(server, method, path, payload)
            assert status == 200, path
            assert fake.calls[-1] == (fn, kwargs), (path, fake.calls[-1])
            if fn in _LISTS:
                assert body == {"items": [fn]}, path
            else:
                assert body == {"ok": fn}, path
        assert len(fake.calls) == len(_CASES)
    finally:
        _stop(server, thread)
