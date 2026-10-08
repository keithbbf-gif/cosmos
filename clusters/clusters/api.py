"""Local JSON API. Binds 127.0.0.1 only.

A list result is wrapped as {"items": ...}. A dict is returned as itself.
"""

from __future__ import annotations

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from clusters.refuse import Refuse

_REQUIRED = object()
_SPEC = (
    ("GET", r"/v1/health", "health", (), ()),
    ("GET", r"/v1/features", "features", (), ()),
    ("POST", r"/v1/projects", "create_project", (), (
        ("name", "str", _REQUIRED),
        ("root", "str", _REQUIRED),
    )),
    ("GET", r"/v1/projects", "list_projects", (), ()),
    ("POST", r"/v1/projects/(?P<project_id>[^/]+)/shortcut", "shortcut", (), (
        ("slot", "int", _REQUIRED),
    )),
    ("POST", r"/v1/clusters", "create_cluster", (), (
        ("name", "str", _REQUIRED),
        ("project_id", "str", _REQUIRED),
        ("parent_id", "str", ""),
    )),
    ("GET", r"/v1/clusters", "list_clusters", (("project", "project_id", ""),), ()),
    ("POST", r"/v1/clusters/(?P<cluster_id>[^/]+)/members", "add_member", (), (
        ("member_kind", "str", _REQUIRED),
        ("member_id", "str", _REQUIRED),
    )),
    ("POST", r"/v1/clusters/(?P<cluster_id>[^/]+)/manager", "set_manager", (), (
        ("session_id", "str", _REQUIRED),
    )),
    ("POST", r"/v1/packs", "attach_pack", (), (
        ("scope", "str", _REQUIRED),
        ("target_id", "str", _REQUIRED),
        ("rules", "json", None),
        ("skills", "json", None),
        ("wrappers", "json", None),
        ("environments", "json", None),
    )),
    ("POST", r"/v1/sessions", "open_session", (), (
        ("project_id", "str", _REQUIRED),
        ("door", "str", _REQUIRED),
        ("hero", "str", ""),
        ("model", "str", ""),
        ("task", "str", ""),
        ("role", "str", "worker"),
        ("account_id", "str", ""),
        ("cluster_id", "str", ""),
        ("parent_id", "str", ""),
        ("title", "str", ""),
    )),
    ("GET", r"/v1/sessions", "list_sessions", (("project", "project_id", ""),), ()),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/status", "set_status", (), (
        ("status", "str", _REQUIRED),
        ("evidence", "evidence", None),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/title", "set_title", (), (
        ("title", "str", _REQUIRED),
        ("evidence", "evidence", None),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/layout", "put_layout", (), (
        ("view", "str", _REQUIRED),
        ("bounds", "json", _REQUIRED),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/close", "close_session", (), (
        ("confirm", "bool", False),
    )),
    ("POST", r"/v1/coordinators", "open_coordinator", (), (
        ("scope", "str", _REQUIRED),
        ("project_id", "str", _REQUIRED),
        ("hero", "str", _REQUIRED),
        ("door", "str", _REQUIRED),
        ("model", "str", _REQUIRED),
    )),
    ("POST", r"/v1/coordinators/(?P<coordinator_id>[^/]+)/goal", "submit_goal", (), (
        ("text", "str", _REQUIRED),
    )),
    ("POST", r"/v1/coordinators/(?P<coordinator_id>[^/]+)/plan", "accept_plan", (), (
        ("plan", "json", _REQUIRED),
        ("evidence", "evidence", None),
    )),
    ("POST", r"/v1/coordinators/(?P<coordinator_id>[^/]+)/report", "report", (), ()),
    ("POST", r"/v1/coordinators/(?P<coordinator_id>[^/]+)/close-worker", "close_worker", (), (
        ("worker_id", "str", _REQUIRED),
        ("confirm", "bool", False),
    )),
    ("POST", r"/v1/comms", "ask_session", (), (
        ("sender_id", "str", _REQUIRED),
        ("target_id", "str", _REQUIRED),
        ("question", "str", _REQUIRED),
    )),
    ("POST", r"/v1/comms/setting", "set_session_comms", (), (
        ("enabled", "bool", _REQUIRED),
    )),
    ("POST", r"/v1/board/tasks", "add_task", (), (
        ("project_id", "str", _REQUIRED),
        ("title", "str", _REQUIRED),
        ("body", "str", ""),
        ("column", "str", "pending"),
        ("door", "str", ""),
        ("hero", "str", ""),
        ("model", "str", ""),
        ("labels", "json", None),
        ("workspace", "str", ""),
    )),
    ("GET", r"/v1/board/tasks", "list_tasks", (("project", "project_id", ""),), ()),
    ("POST", r"/v1/board/tasks/(?P<task_id>[^/]+)/move", "move_task", (), (
        ("column", "str", _REQUIRED),
        ("evidence", "evidence", None),
    )),
    ("POST", r"/v1/board/auto", "auto_tick", (), (
        ("limit", "int?", None),
        ("project_id", "str", ""),
    )),
    ("POST", r"/v1/history/messages", "add_message", (), (
        ("session_id", "str", _REQUIRED),
        ("role", "str", _REQUIRED),
        ("kind", "str", _REQUIRED),
        ("body", "str", _REQUIRED),
        ("resume_of", "str", ""),
    )),
    ("GET", r"/v1/history/search", "search", (
        ("q", "query", ""),
        ("project", "project_id", ""),
    ), ()),
    ("GET", r"/v1/history/(?P<session_id>[^/]+)/resume", "resume_pointer", (), ()),
    ("POST", r"/v1/changes", "record_change", (), (
        ("session_id", "str", _REQUIRED),
        ("path", "str", _REQUIRED),
        ("before", "json", _REQUIRED),
        ("after", "json", _REQUIRED),
        ("diff", "json", _REQUIRED),
    )),
    ("GET", r"/v1/changes", "list_changes", (("session", "session_id", ""),), ()),
    ("POST", r"/v1/git/worktree", "plan_worktree", (), (
        ("session_id", "str", _REQUIRED),
        ("repo", "str", _REQUIRED),
    )),
    ("POST", r"/v1/git/commit-proposal", "propose_commit", (), (
        ("session_id", "str", _REQUIRED),
        ("summary", "str", _REQUIRED),
    )),
    ("POST", r"/v1/git/push", "request_push", (), (
        ("session_id", "str", _REQUIRED),
        ("branch", "str", _REQUIRED),
        ("confirmed", "bool", False),
    )),
    ("POST", r"/v1/policy/check", "check_command", (), (
        ("command", "str", _REQUIRED),
        ("turbo", "bool", False),
        ("branch", "str", ""),
    )),
    ("POST", r"/v1/policy/limits", "set_limits", (), (
        ("allow", "json", None),
        ("deny", "json", None),
    )),
    ("POST", r"/v1/spend/budget", "set_budget", (), (
        ("provider", "str", _REQUIRED),
        ("daily_cap_usd", "num", _REQUIRED),
        ("daily_cap_tokens", "int", 0),
        ("mode", "str", "cap"),
        ("on_limit", "str", "pause"),
        ("window_days", "int", 1),
        ("day_index", "int", 0),
    )),
    ("POST", r"/v1/spend/observe", "observe_spend", (), (
        ("provider", "str", _REQUIRED),
        ("usd", "num", _REQUIRED),
        ("tokens", "int", 0),
        ("source", "str", ""),
        ("observed", "str", ""),
        ("day_index", "int", 0),
    )),
    ("POST", r"/v1/spend/bump", "bump_today", (), (
        ("provider", "str", _REQUIRED),
    )),
    ("POST", r"/v1/spend/check", "check_spend", (), (
        ("provider", "str", _REQUIRED),
        ("usd", "num", 0),
        ("tokens", "int", 0),
    )),
    ("GET", r"/v1/spend", "spend_report", (), ()),
    ("GET", r"/v1/doors", "list_doors", (), ()),
    ("POST", r"/v1/accounts", "add_account", (), (
        ("provider", "str", _REQUIRED),
        ("label", "str", _REQUIRED),
        ("profile_dir", "str", _REQUIRED),
    )),
    ("POST", r"/v1/accounts/(?P<account_id>[^/]+)/bind", "bind_account", (), (
        ("session_id", "str", _REQUIRED),
    )),
    ("POST", r"/v1/mcp/enable-all", "enable_all_mcp", (), (
        ("project_id", "str", _REQUIRED),
    )),
    ("POST", r"/v1/mcp", "set_mcp", (), (
        ("project_id", "str", _REQUIRED),
        ("server_id", "str", _REQUIRED),
        ("enabled", "bool", _REQUIRED),
    )),
    ("GET", r"/v1/mcp", "list_mcp", (("project", "project_id", ""),), ()),
    ("POST", r"/v1/shortcuts", "add_shortcut", (), (
        ("kind", "str", _REQUIRED),
        ("binding", "str", _REQUIRED),
        ("target", "str", _REQUIRED),
    )),
    ("GET", r"/v1/shortcuts", "list_shortcuts", (), ()),
    ("POST", r"/v1/mobile/pair", "pair_mobile", (), ()),
    ("POST", r"/v1/mobile/desktop", "set_desktop", (), (
        ("online", "bool", _REQUIRED),
    )),
    ("POST", r"/v1/mobile/message", "mobile_message", (), (
        ("token", "str", _REQUIRED),
        ("session_id", "str", _REQUIRED),
        ("body", "str", _REQUIRED),
    )),
    ("GET", r"/v1/notifications", "list_notifications", (), ()),
    ("POST", r"/v1/notifications/(?P<note_id>[^/]+)/see", "see_notification", (), ()),
    ("POST", r"/v1/harness/plan", "plan_harness", (), (
        ("hero", "str", _REQUIRED),
        ("task", "str", _REQUIRED),
        ("where", "str", _REQUIRED),
        ("via", "str", "cosmos-code"),
        ("execute", "bool", False),
    )),
    ("POST", r"/v1/policy/matrix", "set_matrix", (), (
        ("file", "str", "ask"),
        ("shell", "str", "ask"),
        ("git", "str", "ask"),
        ("network", "str", "ask"),
        ("mcp", "str", "ask"),
    )),
    ("POST", r"/v1/policy/decide", "decide", (), (
        ("category", "str", _REQUIRED),
        ("command", "str", _REQUIRED),
        ("turbo", "bool", False),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/link", "link_status", (), (
        ("status", "str", _REQUIRED),
        ("evidence", "evidence", None),
        ("detail", "str", ""),
    )),
    ("POST", r"/v1/skills", "enable_skill", (), (
        ("project_id", "str", _REQUIRED),
        ("path", "str", _REQUIRED),
        ("enabled", "bool", True),
    )),
    ("GET", r"/v1/skills/pack", "skill_pack", (("project", "project_id", ""),), ()),
    ("GET", r"/v1/skills", "list_skills", (("project", "project_id", ""),), ()),
    ("POST", r"/v1/quota/window", "set_quota_window", (), (
        ("provider", "str", _REQUIRED),
        ("limit_usd", "num", _REQUIRED),
        ("period_seconds", "int", _REQUIRED),
        ("resets_at", "num", _REQUIRED),
        ("source", "str", _REQUIRED),
        ("observed", "str", _REQUIRED),
    )),
    ("POST", r"/v1/quota/used", "mark_quota_used", (), (
        ("provider", "str", _REQUIRED),
        ("used_usd", "num", _REQUIRED),
        ("source", "str", _REQUIRED),
        ("observed", "str", _REQUIRED),
    )),
    ("POST", r"/v1/quota/prorata", "quota_prorata", (), (
        ("provider", "str", _REQUIRED),
        ("now", "num", _REQUIRED),
    )),
    ("POST", r"/v1/relay/worker", "send_worker", (), (
        ("coordinator_id", "str", _REQUIRED),
        ("worker_id", "str", _REQUIRED),
        ("text", "str", _REQUIRED),
        ("kind", "str", _REQUIRED),
    )),
    ("POST", r"/v1/relay/small", "keep_small", (), (
        ("coordinator_id", "str", _REQUIRED),
        ("text", "str", _REQUIRED),
    )),
    ("POST", r"/v1/relay/delegate", "delegate_project", (), (
        ("global_id", "str", _REQUIRED),
        ("project_id", "str", _REQUIRED),
        ("text", "str", _REQUIRED),
        ("door", "str", _REQUIRED),
        ("hero", "str", _REQUIRED),
        ("model", "str", _REQUIRED),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/mode", "set_mode", (), (
        ("mode", "str", _REQUIRED),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/cancel", "cancel_session", (), ()),
    ("POST", r"/v1/mobile/follow", "follow_mobile", (), (
        ("token", "str", _REQUIRED),
    )),
    ("POST", r"/v1/shortcuts/seed", "seed_keys", (), ()),
    ("POST", r"/v1/board/defaults", "set_lane_defaults", (), (
        ("project_id", "str", _REQUIRED),
        ("door", "str", _REQUIRED),
        ("hero", "str", ""),
        ("model", "str", ""),
        ("reasoning", "str", "medium"),
        ("permission", "str", "default"),
        ("workspace", "str", "worktree"),
    )),
    ("POST", r"/v1/board/tasks/(?P<task_id>[^/]+)/drag", "queue_drag", (), ()),
    ("POST", r"/v1/board/tasks/(?P<task_id>[^/]+)/lightning", "queue_lightning", (), (
        ("door", "str", ""),
        ("hero", "str", ""),
        ("model", "str", ""),
        ("reasoning", "str", ""),
        ("permission", "str", ""),
        ("workspace", "str", ""),
    )),
    ("POST", r"/v1/board/queue", "queue_new", (), (
        ("project_id", "str", _REQUIRED),
        ("title", "str", _REQUIRED),
        ("body", "str", ""),
        ("door", "str", ""),
        ("hero", "str", ""),
        ("model", "str", ""),
        ("reasoning", "str", ""),
        ("permission", "str", ""),
        ("workspace", "str", ""),
        ("labels", "json", None),
    )),
    ("POST", r"/v1/git/classify", "classify_git", (), (
        ("command", "str", _REQUIRED),
    )),
    ("POST", r"/v1/git/message", "propose_message", (), (
        ("session_id", "str", _REQUIRED),
        ("evidence", "evidence", None),
        ("style", "str", "detailed"),
    )),
    ("POST", r"/v1/git/review", "propose_review", (), (
        ("session_id", "str", _REQUIRED),
        ("summary", "str", _REQUIRED),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/titles", "list_titles", (), ()),
    ("POST", r"/v1/board/tasks/(?P<parent_id>[^/]+)/subtasks", "add_subtask", (), (
        ("title", "str", _REQUIRED),
        ("body", "str", ""),
    )),
    ("GET", r"/v1/board/tasks/(?P<parent_id>[^/]+)/subtasks", "list_subtasks", (), ()),
    ("POST", r"/v1/bookmarks", "add_bookmark", (), (
        ("session_id", "str", _REQUIRED),
        ("message_id", "str", ""),
        ("note", "str", ""),
    )),
    ("POST", r"/v1/bookmarks/(?P<bookmark_id>[^/]+)/hide", "hide_bookmark", (), ()),
    ("GET", r"/v1/bookmarks", "list_bookmarks", (("session", "session_id", ""),), ()),
    ("POST", r"/v1/spend/admit", "admit", (), (
        ("provider", "str", _REQUIRED),
        ("now", "num", _REQUIRED),
        ("usd", "num", 0),
        ("tokens", "int", 0),
    )),
    ("POST", r"/v1/git/confirm", "record_confirm", (), (
        ("session_id", "str", _REQUIRED),
        ("branch", "str", _REQUIRED),
        ("clean", "bool", _REQUIRED),
        ("evidence", "evidence", None),
    )),
    ("POST", r"/v1/board/tasks/(?P<task_id>[^/]+)/isolation", "plan_isolation", (), (
        ("base_ref", "str", _REQUIRED),
        ("share", "str", _REQUIRED),
        ("workspace", "str", _REQUIRED),
        ("why", "str", ""),
        ("paths", "json", None),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/binding", "bind_seat", (), (
        ("door", "str", _REQUIRED),
        ("model", "str", _REQUIRED),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/binding", "get_binding", (), ()),
    ("POST", r"/v1/attention", "note_attention", (), (
        ("session_id", "str", _REQUIRED),
        ("reason", "str", _REQUIRED),
    )),
    ("GET", r"/v1/attention", "list_attention", (("session", "session_id", ""),), ()),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/thread", "set_thread", (), (
        ("state", "str", _REQUIRED),
        ("until", "num", 0),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/thread", "get_thread", (), ()),
    ("POST", r"/v1/projects/(?P<project_id>[^/]+)/preset", "set_preset", (), (
        ("colour", "str", _REQUIRED),
        ("icon", "str", _REQUIRED),
        ("door", "str", _REQUIRED),
        ("resume", "bool", False),
        ("turbo", "bool", False),
    )),
    ("GET", r"/v1/projects/(?P<project_id>[^/]+)/preset", "get_preset", (), ()),
    ("POST", r"/v1/board/tasks/(?P<task_id>[^/]+)/attach", "attach_task", (), (
        ("work_style", "str", _REQUIRED),
        ("style_text", "str", ""),
        ("images", "json", None),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/seen", "mark_seen", (), (
        ("path", "str", _REQUIRED),
        ("seen", "bool", True),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/review", "review_paths", (), ()),
    ("POST", r"/v1/instructions", "add_instruction", (), (
        ("project_id", "str", _REQUIRED),
        ("kind", "str", _REQUIRED),
        ("path", "str", _REQUIRED),
    )),
    ("GET", r"/v1/instructions", "list_instructions", (("project", "project_id", ""),), ()),
    ("POST", r"/v1/projects/(?P<project_id>[^/]+)/import", "set_import", (), (
        ("result", "str", _REQUIRED),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/door-id", "set_door_id", (), (
        ("conversation_id", "str", _REQUIRED),
        ("home", "str", _REQUIRED),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/door-id", "get_door_id", (), ()),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/route", "set_route", (), (
        ("route", "str", _REQUIRED),
        ("path", "str", _REQUIRED),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/route", "get_route", (), ()),
    ("POST", r"/v1/quota/shape", "set_shape", (), (
        ("provider", "str", _REQUIRED),
        ("shape", "str", _REQUIRED),
        ("limit_label", "str", _REQUIRED),
        ("source", "str", _REQUIRED),
        ("observed", "str", _REQUIRED),
    )),
    ("POST", r"/v1/quota/shape/gate", "shape_gate", (), (
        ("provider", "str", _REQUIRED),
        ("shape", "str", _REQUIRED),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/caps", "set_caps", (), (
        ("mode", "str", _REQUIRED),
        ("provider", "str", ""),
        ("subagents", "bool", True),
        ("worktree", "str", ""),
        ("command_path", "str", ""),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/caps", "get_caps", (), ()),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/host", "set_host", (), (
        ("host", "str", _REQUIRED),
        ("fact", "str", _REQUIRED),
        ("enabled", "bool", _REQUIRED),
    )),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/env", "set_env_name", (), (
        ("name", "str", _REQUIRED),
    )),
    ("POST", r"/v1/conflicts", "record_conflict", (), (
        ("session_id", "str", _REQUIRED),
        ("path", "str", _REQUIRED),
        ("outcome", "str", _REQUIRED),
    )),
    ("GET", r"/v1/conflicts", "list_conflicts", (("session", "session_id", ""),), ()),
    ("POST", r"/v1/tools", "set_tool", (), (
        ("project_id", "str", _REQUIRED),
        ("server_id", "str", _REQUIRED),
        ("tool", "str", _REQUIRED),
        ("level", "str", _REQUIRED),
    )),
    ("GET", r"/v1/tools", "tool_level", (
        ("project", "project_id", ""),
        ("server", "server_id", ""),
        ("tool", "tool", ""),
    ), ()),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/headless", "plan_headless", (), (
        ("output_format", "str", "plain"),
        ("max_turns", "int", 1),
        ("sandbox", "str", ""),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/headless", "get_headless", (), ()),
    ("POST", r"/v1/sessions/(?P<session_id>[^/]+)/flags", "set_seat_flags", (), (
        ("channel", "str", "stable"),
        ("role", "str", ""),
        ("tool_search", "bool", False),
        ("web_fetch", "bool", False),
        ("hooks_off", "bool", False),
        ("auto_update", "bool", False),
        ("lock_path", "str", ""),
    )),
    ("GET", r"/v1/sessions/(?P<session_id>[^/]+)/flags", "get_seat_flags", (), ()),
    ("POST", r"/v1/quota/meter", "set_meter", (), (
        ("provider", "str", _REQUIRED),
        ("reading", "str", _REQUIRED),
        ("pool", "str", _REQUIRED),
        ("auto_reload", "bool", False),
        ("source", "str", ""),
        ("observed", "str", ""),
    )),
    ("POST", r"/v1/quota/meter/gate", "meter_gate", (), (
        ("provider", "str", _REQUIRED),
        ("pool", "str", _REQUIRED),
    )),
)

_ROUTES = tuple(
    (method, re.compile(path), fn, query, fields)
    for method, path, fn, query, fields in _SPEC
)


class _BadJson(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def _coerce(kind: str, value, name: str):
    if kind == "str":
        if isinstance(value, str):
            return value
        raise _BadJson(name)
    if kind == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise _BadJson(name)
        return value
    if kind == "int?":
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise _BadJson(name)
        return value
    if kind == "bool":
        if isinstance(value, bool):
            return value
        raise _BadJson(name)
    if kind == "num":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise _BadJson(name)
        return value
    if kind == "evidence":
        if value is None or isinstance(value, dict):
            return value
        raise _BadJson(name)
    if kind == "json":
        return value
    raise _BadJson(name)


def _fields(payload: dict, fields) -> dict:
    kwargs = {}
    for name, kind, default in fields:
        if name not in payload:
            if default is _REQUIRED:
                raise _BadJson("missing " + name)
            kwargs[name] = default
            continue
        kwargs[name] = _coerce(kind, payload[name], name)
    return kwargs


def _query(text: str, spec) -> dict:
    if not spec:
        return {}
    parsed = parse_qs(text, keep_blank_values=True)
    kwargs = {}
    for qname, key, default in spec:
        values = parsed.get(qname)
        kwargs[key] = values[0] if values else default
    return kwargs


def _read_body(handler: BaseHTTPRequestHandler) -> dict:
    raw_length = handler.headers.get("Content-Length")
    if raw_length is None or str(raw_length).strip() == "":
        return {}
    try:
        length = int(raw_length)
    except (TypeError, ValueError) as exc:
        raise _BadJson("content-length") from exc
    if length < 0:
        raise _BadJson("content-length")
    if length == 0:
        return {}
    data = handler.rfile.read(length)
    if not data.strip():
        return {}
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _BadJson("utf-8") from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise _BadJson(exc.msg) from exc
    if not isinstance(parsed, dict):
        raise _BadJson("object")
    return parsed


def _shape(result):
    if isinstance(result, list):
        return {"items": result}
    if isinstance(result, dict):
        return result
    if result is None:
        return {}
    return {"result": result}


def _find(method: str, path: str):
    for route_method, pattern, fn, query, fields in _ROUTES:
        if route_method != method:
            continue
        match = pattern.fullmatch(path)
        if match is not None:
            return fn, query, fields, match
    return None


def _send(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Connection", "close")
    handler.end_headers()
    handler.wfile.write(raw)


def _dispatch(handler: BaseHTTPRequestHandler, console, method: str) -> None:
    parsed = urlparse(handler.path)
    path = parsed.path
    found = _find(method, path)
    if found is None:
        _send(handler, 404, {"error": "ROUTE", "detail": path})
        return
    fn, query, fields, match = found
    try:
        kwargs = {key: unquote(value) for key, value in match.groupdict().items()}
        kwargs.update(_query(parsed.query, query))
        if method == "POST":
            kwargs.update(_fields(_read_body(handler), fields))
        result = getattr(console, fn)(**kwargs)
    except _BadJson as exc:
        _send(handler, 400, {"error": "JSON", "detail": exc.detail})
        return
    except Refuse as exc:
        _send(handler, 409, exc.to_public())
        return
    except Exception as exc:  # noqa: BLE001 — an unknown fault stays a 500 with the type name only
        _send(handler, 500, {"error": "FAULT", "detail": type(exc).__name__})
        return
    _send(handler, 200, _shape(result))


def make_handler(console) -> type[BaseHTTPRequestHandler]:
    """Return a handler class closed over this console."""

    class ClusterHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            _dispatch(self, console, "GET")

        def do_POST(self) -> None:
            _dispatch(self, console, "POST")

        def log_message(self, format: str, *args) -> None:
            return

    return ClusterHandler


def serve(console, host: str = "127.0.0.1", port: int = 8780) -> ThreadingHTTPServer:
    """Listen on 127.0.0.1. Any other host refuses before a socket exists."""
    if host != "127.0.0.1":
        raise Refuse("BIND", host)
    return ThreadingHTTPServer((host, port), make_handler(console))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="clusters.api")
    parser.add_argument("--root", required=True)
    parser.add_argument("--port", type=int, default=8780)
    args = parser.parse_args(argv)
    from clusters.console import Console

    server = serve(Console(args.root), port=args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
