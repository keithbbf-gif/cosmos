#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CCrew reply pipe — saved reply → CPU checks → WOMBAT → Judge at 40 → Gitur.

Legacy CHECKED rails (github / cursor / gitlab) stamp CI. They do not read
the saved file. This module reads the reply, runs form checks on the bytes,
and files the next inbox only when those checks pass and no rail is FAIL
or ERROR. UNMEASURED rails stay visible and do not pretend to be a pass.

WOMBAT watches every save (pass or fail): server errors → swap_agent,
incomplete → reassign, otherwise hold the board row. This module does not
spawn a model and does not write LiT.

    py -3.14 cosmos\\cosmos_crew_pipe.py --selftest
"""
from __future__ import annotations

import ast
import json
import re
from datetime import datetime
from pathlib import Path

SCHEMA = "cosmos-crew-pipe/1"
LEGACY_RAILS = ("github", "cursor", "gitlab")
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
SERVER_MARK = re.compile(r"\b(429|500|502|503|504|UNREACHABLE|rate.?limit)\b", re.I)


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def pipe_root(paths) -> Path:
    root = paths.state("crew_pipe")
    root.mkdir(parents=True, exist_ok=True)
    for name in ("judge_inbox", "gitur_inbox", "ccr_inbox"):
        (root / name).mkdir(parents=True, exist_ok=True)
    return root


def _append(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _read_reply(rec: dict) -> str:
    raw = rec.get("_output_path") or ""
    if not raw:
        return ""
    p = Path(str(raw))
    if not p.is_file():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def local_code_checks(text: str, *, filename: str = "reply.py") -> list[dict]:
    """Read the saved reply. These are the checks that look at the code."""
    rows = []
    body = text or ""
    if not body.strip():
        return [{"name": "nonempty", "status": "FAIL", "detail": "saved reply is empty"}]
    rows.append({"name": "nonempty", "status": "PASS", "detail": f"{len(body)} bytes"})
    if BTS_IMPORT.search(body):
        rows.append({
            "name": "no_bts_import", "status": "FAIL",
            "detail": "reply imports bts_*",
        })
    else:
        rows.append({
            "name": "no_bts_import", "status": "PASS",
            "detail": "no bts_ import",
        })
    stripped = body.lstrip()
    if stripped.startswith("{"):
        try:
            json.loads(body)
            rows.append({"name": "json_form", "status": "PASS", "detail": "JSON parses"})
        except json.JSONDecodeError as e:
            rows.append({
                "name": "json_form", "status": "FAIL",
                "detail": f"JSON does not parse: {e.msg}",
            })
    elif stripped.startswith("diff --git") or stripped.startswith("NONE"):
        rows.append({
            "name": "coder_first_line", "status": "PASS",
            "detail": stripped.splitlines()[0][:80],
        })
    elif filename.endswith(".py") or stripped.startswith(("def ", "class ", "import ", "from ")):
        try:
            ast.parse(body, filename=filename)
            rows.append({"name": "py_parse", "status": "PASS", "detail": "ast.parse ok"})
        except SyntaxError as e:
            rows.append({
                "name": "py_parse", "status": "FAIL",
                "detail": f"syntax line {e.lineno}: {e.msg}",
            })
    else:
        rows.append({
            "name": "form", "status": "PASS",
            "detail": "prose reply; no py/json/diff form required",
        })
    return rows


def legacy_rail_view(rec: dict) -> list[dict]:
    """The three CHECKED rails. Status is whatever the runner stamped."""
    checks = rec.get("checks") if isinstance(rec.get("checks"), dict) else {}
    rows = []
    for name in LEGACY_RAILS:
        item = checks.get(name) if isinstance(checks.get(name), dict) else {}
        rows.append({
            "name": name,
            "status": item.get("status") or "UNMEASURED",
            "detail": str(item.get("detail") or "not stamped")[:240],
            "url": item.get("url"),
        })
    return rows


def _local_pass(rows: list[dict]) -> bool:
    return bool(rows) and all(r.get("status") == "PASS" for r in rows)


def _rail_blocks(rows: list[dict]) -> bool:
    return any(r.get("status") in ("FAIL", "ERROR") for r in rows)


def wombat_action(rec: dict, *, reaches_judge: bool) -> str:
    """Board action. Does not spawn."""
    blob = " ".join([
        str(rec.get("fail_kind") or ""),
        str(rec.get("fail_detail") or ""),
        str((rec.get("run") or {}).get("err") or ""),
        str((rec.get("run") or {}).get("out") or ""),
    ])
    if rec.get("state") == "FAILED" or not rec.get("_output_path"):
        return "reassign"
    if (rec.get("run") or {}).get("timed_out") or SERVER_MARK.search(blob):
        return "swap_agent"
    if not reaches_judge:
        return "hold_for_fix"
    return "watch"


def attach_pipe(paths, rec: dict) -> dict:
    """py_compile, ruff, mypy, pytest, then WOMBAT. The Judge waits for 40."""
    rec = dict(rec)
    if rec.get("state") != "DONE":
        return rec
    text = _read_reply(rec)
    local = local_code_checks(text, filename=Path(str(rec.get("_output_path") or "reply.txt")).name)
    rails = legacy_rail_view(rec)
    from cosmos_code_checks import fails_of, run_code_checks
    from cosmos_duds import DudsError, on_saved_reply
    code_rows = run_code_checks(paths, rec, text)
    blocked = [r for r in rails if r.get("status") in ("FAIL", "ERROR")]
    force = "; ".join(
        part for part in (
            fails_of(code_rows),
            "; ".join(f"{r['name']}: {r.get('detail') or ''}" for r in blocked),
        ) if part
    )
    try:
        filed = on_saved_reply(paths, rec, text, force_error=force)
        crew = dict(filed.get("crew_pipe") or {})
    except DudsError as e:
        crew = {
            "reaches_judge": False,
            "wombat": "session_busy",
            "stage": "refused",
            "detail": f"{e.kind}: {e.detail}",
        }
    crew["local"] = local
    crew["code_checks"] = [
        {"tool": r["tool"], "status": r["status"], "returncode": r["returncode"]}
        for r in code_rows
    ]
    crew["legacy_rails"] = rails
    event = {
        "schema": SCHEMA,
        "at": _iso_now(),
        "order_id": rec.get("order_id"),
        "stage": crew.get("stage"),
        "reaches_judge": False,
        "local": local,
        "legacy_rails": rails,
        "wombat": crew.get("wombat"),
        "output_path": rec.get("_output_path"),
    }
    root = pipe_root(paths)
    _append(root / "events.jsonl", event)
    _append(root / "wombat_board.jsonl", {
        "schema": SCHEMA,
        "at": event["at"],
        "order_id": event["order_id"],
        "action": crew.get("wombat"),
        "reaches_judge": False,
        "note": _wombat_note(str(crew.get("wombat") or "")),
    })
    rec["crew_pipe"] = crew
    _persist_assigned(paths, rec)
    return rec


def note_failed(paths, rec: dict) -> dict:
    """WOMBAT row for a reply that never became DONE."""
    action = wombat_action(rec, reaches_judge=False)
    event = {
        "schema": SCHEMA,
        "at": _iso_now(),
        "order_id": rec.get("order_id"),
        "stage": "failed",
        "reaches_judge": False,
        "wombat": action,
        "fail_kind": rec.get("fail_kind"),
    }
    root = pipe_root(paths)
    _append(root / "events.jsonl", event)
    _append(root / "wombat_board.jsonl", {
        "schema": SCHEMA,
        "at": event["at"],
        "order_id": event["order_id"],
        "action": action,
        "reaches_judge": False,
        "note": _wombat_note(action),
    })
    rec = dict(rec)
    rec["crew_pipe"] = {"reaches_judge": False, "wombat": action, "stage": "failed"}
    return rec


def file_judge_correction(paths, order_id: str, corrected: str, *, grade: str) -> dict:
    """Judge save. Refuses unless WOMBAT has seated the Judge at 40."""
    from cosmos_duds import DudsError, _judge_seat
    if not _judge_seat(paths).get("seated"):
        raise DudsError("JUDGE_UNSEATED", "WOMBAT summons the Judge at 40")
    grade_u = str(grade or "").strip().upper()
    root = pipe_root(paths)
    src = root / "judge_inbox" / f"{order_id}.json"
    if not src.is_file():
        raise FileNotFoundError(f"no judge inbox for {order_id}")
    if grade_u not in ("KEEP", "CORRECTED"):
        drop = {
            "schema": SCHEMA, "at": _iso_now(), "order_id": order_id,
            "stage": "judge_drop", "grade": grade_u or "DROP", "wombat": "reassign",
        }
        _append(root / "events.jsonl", drop)
        _append(root / "wombat_board.jsonl", {
            "schema": SCHEMA, "at": drop["at"], "order_id": order_id,
            "action": "reassign", "reaches_judge": False,
            "note": _wombat_note("reassign"),
        })
        return drop
    dest = root / "gitur_inbox" / f"{order_id}.json"
    body = {
        "schema": SCHEMA,
        "order_id": order_id,
        "stage": "gitur",
        "grade": grade_u,
        "corrected": corrected,
        "instruction": (
            "Gitur check: Cursor Composer 2.5 on this corrected text. "
            "CCr (Grok 4.7) writes the local tree only after that check passes."
        ),
    }
    dest.write_text(json.dumps(body, indent=1), encoding="utf-8")
    event = {
        "schema": SCHEMA, "at": _iso_now(), "order_id": order_id,
        "stage": "gitur_inbox", "grade": grade_u, "wombat": "watch",
    }
    _append(root / "events.jsonl", event)
    _append(root / "wombat_board.jsonl", {
        "schema": SCHEMA, "at": event["at"], "order_id": order_id,
        "action": "watch", "reaches_judge": True, "note": _wombat_note("watch"),
    })
    return event


def file_gitur_result(paths, order_id: str, *, status: str, detail: str = "") -> dict:
    """Composer check result. PASS files the CCr inbox. It does not merge."""
    root = pipe_root(paths)
    src = root / "gitur_inbox" / f"{order_id}.json"
    if not src.is_file():
        raise FileNotFoundError(f"no gitur inbox for {order_id}")
    status_u = str(status or "").strip().upper()
    if status_u != "PASS":
        event = {
            "schema": SCHEMA, "at": _iso_now(), "order_id": order_id,
            "stage": "gitur_hold", "status": status_u or "FAIL",
            "detail": detail[:240], "wombat": "hold_for_fix",
        }
        _append(root / "events.jsonl", event)
        _append(root / "wombat_board.jsonl", {
            "schema": SCHEMA, "at": event["at"], "order_id": order_id,
            "action": "hold_for_fix", "reaches_judge": True,
            "note": _wombat_note("hold_for_fix"),
        })
        return event
    packed = json.loads(src.read_text(encoding="utf-8"))
    dest = root / "ccr_inbox" / f"{order_id}.json"
    packed["stage"] = "ccr"
    packed["gitur_status"] = "PASS"
    packed["gitur_detail"] = detail[:240]
    packed["instruction"] = (
        "CCr Grok 4.7 final review, then write the local tree, then sync origin/main."
    )
    dest.write_text(json.dumps(packed, indent=1), encoding="utf-8")
    event = {
        "schema": SCHEMA, "at": _iso_now(), "order_id": order_id,
        "stage": "ccr_inbox", "wombat": "watch",
    }
    _append(root / "events.jsonl", event)
    _append(root / "wombat_board.jsonl", {
        "schema": SCHEMA, "at": event["at"], "order_id": order_id,
        "action": "watch", "reaches_judge": True, "note": _wombat_note("watch"),
    })
    return event


def _wombat_note(action: str) -> str:
    return {
        "watch": "Reply is moving. Keep the board row current.",
        "hold_for_fix": "Checks or Gitur did not pass. Leave the task on the board.",
        "swap_agent": "Server or timeout on the seat. Swap the agent and keep the same task.",
        "reassign": "Task did not complete. Reassign it. Do not drop the board row.",
    }.get(action, action)


def _persist_assigned(paths, rec: dict) -> None:
    if not rec.get("order_id"):
        return
    try:
        from cosmos_work_order import _atomic_json, order_file, work_order_dirs
        dest = order_file(work_order_dirs(paths)["assigned"], rec["order_id"])
        if dest.is_file():
            _atomic_json(dest, rec)
    except Exception:  # noqa: BLE001
        return


def _selftest() -> int:
    import tempfile
    from cosmos_paths import write_sentinel

    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + label)
        if not cond:
            ok = False

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write_sentinel(root, tree_id="crew-pipe-test")
        (root / "state").mkdir()
        from cosmos_paths import CosmosPaths
        paths = CosmosPaths(root)
        reply = root / "out.py"
        reply.write_text("def ping():\n    return 1\n", encoding="utf-8")
        rec = {
            "order_id": "wo-pipe-1",
            "state": "DONE",
            "_output_path": str(reply),
            "checks": {
                "github": {"status": "UNMEASURED", "detail": "no workflow_runs"},
                "cursor": {"status": "UNMEASURED", "detail": "post-DONE POST disabled"},
                "gitlab": {"status": "UNMEASURED", "detail": "no pipeline"},
            },
        }
        out = attach_pipe(paths, rec)
        check("cpu pass is a candidate and does not seat the Judge",
              out["crew_pipe"]["stage"] == "candidate"
              and out["crew_pipe"]["reaches_judge"] is False)
        check("judge inbox stays empty under 40",
              not (pipe_root(paths) / "judge_inbox" / "wo-pipe-1.json").is_file())
        bad = dict(rec)
        bad["order_id"] = "wo-pipe-bad"
        bad["_output_path"] = str(reply)
        reply.write_text("def ping(\n", encoding="utf-8")
        held = attach_pipe(paths, bad)
        check("syntax fail does not reach the Judge",
              held["crew_pipe"]["reaches_judge"] is False)
        check("wombat xFORMs the same session",
              held["crew_pipe"]["wombat"] == "reprompt_session"
              and held["crew_pipe"]["session_id"])
        unseated = False
        try:
            file_judge_correction(paths, "wo-pipe-1", "", grade="KEEP")
        except Exception as e:
            unseated = type(e).__name__ == "DudsError"
        check("an unseated Judge cannot file Gitur", unseated)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_crew_pipe: --selftest", file=sys.stderr)
    raise SystemExit(2)
