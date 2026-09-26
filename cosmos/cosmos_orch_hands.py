#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fail-closed hands for the orchestrator.

get_session is read-only. select_project, invoke_bootup, dispatch_job,
and dispatch_grokbot do nothing unless confirm is true. dispatch_grokbot
never spawns grok.exe. Coding verbs appear only when a code_root is
injected; they never default to the live tree.

    py -3.14 cosmos\\cosmos_orch_hands.py --selftest
"""
from __future__ import annotations

from cosmos_code_tools import CodeToolError, CodeTools

HANDS = (
    "get_session",
    "select_project",
    "invoke_bootup",
    "dispatch_job",
    "dispatch_grokbot",
)
CODE_VERBS = ("Read", "Write", "Edit", "Glob", "Grep", "Bash")


def _refused(detail: str, kind: str = "REFUSED") -> dict:
    return {"ok": False, "kind": kind, "detail": detail}


def _confirmed(confirm) -> bool:
    return confirm is True or confirm == "true"


def make_hands(*, sessions=None, drop_fn=None, boot_fn=None,
               select_fn=None, code_root=None) -> dict:
    """Callables the model may name. Consequential ones refuse without confirm."""

    def get_session(session_id: str = "") -> dict:
        if sessions is None:
            return {"ok": False, "kind": "UNMEASURED",
                    "detail": "no session store injected",
                    "session_id": session_id or None}
        try:
            rec = sessions(session_id) if callable(sessions) else sessions.get(session_id)
        except Exception as e:  # noqa: BLE001
            return _refused("%s: %s" % (type(e).__name__, e), "UNMEASURED")
        if not rec:
            return {"ok": False, "kind": "UNMEASURED", "session_id": session_id or None,
                    "detail": "session not in the store"}
        return {"ok": True, "kind": "MEASURED", "session": rec}

    def select_project(project: str = "", confirm=False) -> dict:
        if not _confirmed(confirm):
            return _refused("confirm=true required; select_project does not auto-run")
        if not str(project or "").strip():
            return _refused("project is required", "BAD_INPUT")
        if select_fn is None:
            return {"ok": True, "kind": "NAMED", "project": project,
                    "detail": "named only; no setter injected"}
        return select_fn(project)

    def invoke_bootup(confirm=False) -> dict:
        if not _confirmed(confirm):
            return _refused("confirm=true required; BootUP does not auto-run")
        if boot_fn is None:
            return _refused("no BootUP callable injected", "NO_BOOT")
        return boot_fn()

    def dispatch_job(task: str = "", confirm=False, agent: str = "",
                     output: str = "proposals | out.md") -> dict:
        if not _confirmed(confirm):
            return _refused("confirm=true required; dispatch_job does not auto-drop")
        if drop_fn is None:
            return _refused("no work-order desk injected", "NO_DESK")
        if not str(task or "").strip():
            return _refused("task is required", "BAD_INPUT")
        return drop_fn({
            "task": task,
            "agent": agent,
            "output": output,
            "kind": "dispatch_job",
        })

    def dispatch_grokbot(task: str = "", confirm=False) -> dict:
        if not _confirmed(confirm):
            return _refused("confirm=true required; dispatch_grokbot does not auto-run")
        if "grok.exe" in str(task).lower():
            return _refused("grok.exe is not a hand")
        if drop_fn is None:
            return _refused("no mailbox injected", "NO_DESK")
        return drop_fn({
            "task": task,
            "kind": "dispatch_grokbot",
            "spawn": False,
            "note": "mailbox drop only; grok.exe is refused",
        })

    tools = {
        "get_session": get_session,
        "select_project": select_project,
        "invoke_bootup": invoke_bootup,
        "dispatch_job": dispatch_job,
        "dispatch_grokbot": dispatch_grokbot,
    }
    if code_root is not None:
        code = CodeTools([code_root])

        def _wrap(verb):
            def fn(**kwargs):
                try:
                    return getattr(code, verb)(**kwargs)
                except CodeToolError as e:
                    return _refused(e.detail, e.kind)
            return fn

        for verb in CODE_VERBS:
            tools[verb] = _wrap(verb)
    return tools


def hand_schema(include_code: bool = False) -> list:
    rows = [
        {"type": "function", "function": {
            "name": "get_session",
            "description": "Read one session projection. Missing store is UNMEASURED.",
            "parameters": {"type": "object", "properties": {
                "session_id": {"type": "string"}},
                "required": []}}},
        {"type": "function", "function": {
            "name": "select_project",
            "description": "Name the working project. Refuses unless confirm is true.",
            "parameters": {"type": "object", "properties": {
                "project": {"type": "string"},
                "confirm": {"type": "boolean"}},
                "required": ["project", "confirm"]}}},
        {"type": "function", "function": {
            "name": "invoke_bootup",
            "description": "Run BootUP. Refuses unless confirm is true. Never auto-runs.",
            "parameters": {"type": "object", "properties": {
                "confirm": {"type": "boolean"}},
                "required": ["confirm"]}}},
        {"type": "function", "function": {
            "name": "dispatch_job",
            "description": "Drop one work order. Refuses unless confirm is true.",
            "parameters": {"type": "object", "properties": {
                "task": {"type": "string"},
                "confirm": {"type": "boolean"},
                "agent": {"type": "string"},
                "output": {"type": "string"}},
                "required": ["task", "confirm"]}}},
        {"type": "function", "function": {
            "name": "dispatch_grokbot",
            "description": "Mailbox a GrokBot task. Does not spawn grok.exe. confirm required.",
            "parameters": {"type": "object", "properties": {
                "task": {"type": "string"},
                "confirm": {"type": "boolean"}},
                "required": ["task", "confirm"]}}},
    ]
    if include_code:
        for name in CODE_VERBS:
            rows.append({"type": "function", "function": {
                "name": name,
                "description": "Allowlisted coding verb. Paths outside code_root are REFUSED.",
                "parameters": {"type": "object", "properties": {
                    "path": {"type": "string"},
                    "pattern": {"type": "string"},
                    "content": {"type": "string"},
                    "old": {"type": "string"},
                    "new": {"type": "string"}},
                    "required": []}}})
    return rows


def _selftest() -> int:
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, "%s: %s" % (type(e).__name__, e)))

    hands = make_hands()
    check("dispatch without confirm is REFUSED",
          lambda: hands["dispatch_job"](task="x")["kind"] == "REFUSED")
    check("bootup without confirm is REFUSED",
          lambda: hands["invoke_bootup"]()["kind"] == "REFUSED")
    check("grok.exe task is REFUSED even with confirm",
          lambda: hands["dispatch_grokbot"](task="run grok.exe", confirm=True)["kind"] == "REFUSED")
    dropped = []
    desk = make_hands(drop_fn=lambda rec: dropped.append(rec) or {"ok": True, "filed": True})
    filed = desk["dispatch_job"](task="write the gate", confirm=True)
    check("confirm plus a desk files one drop and does not spawn",
          lambda: filed["ok"] is True and len(dropped) == 1
          and dropped[0].get("spawn") is not True
          and dropped[0]["kind"] == "dispatch_job")
    check("get_session with no store is UNMEASURED",
          lambda: hands["get_session"]("ses")["kind"] == "UNMEASURED")
    seen = make_hands(sessions=lambda sid: {"id": sid, "title": "carry"})
    check("get_session reads the injected store",
          lambda: seen["get_session"]("ses")["session"]["title"] == "carry")

    bad = [(label, err) for label, ok, err in results if not ok]
    for label, ok, err in results:
        print(("  OK  " if ok else "  FAIL") + " " + label + (("  " + err) if err else ""))
    print("%d/%d passed" % (len(results) - len(bad), len(results)))
    return 1 if bad else 0


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("usage: py -3.14 cosmos\\cosmos_orch_hands.py --selftest")
    raise SystemExit(2)
