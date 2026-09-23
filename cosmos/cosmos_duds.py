#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DUDs — the outfit. Slang for the clothes an agent puts on (not a loser).

Legend (layers 1–7) plus the Mission (layer 8) are those clothes.
Agent + DUDs = HERO. No complete outfit, no summon. Wrapper is layer 4 only.

The daemon writes the eight layers on the WOMB, then summons one session
of that model in the harness the DUDs name. WOMBAT watches the spawn and
the saved reply. Three CPU checks read the reply before any model grades
it: py_compile, fence, tokenize. A fail is a scar plus an xFORM back to
that same session. Five fails, or a server / deprecated error, closes the
session and files a new HERO only when its DUDs are complete. At 40
CPU-passing sets WOMBAT summons the Judge HERO. The Judge records the
card and files Gitur. An empty pile retires the Judge. ORC does not file
Gitur.

    py -3.14 cosmos\\cosmos_duds.py --selftest
"""
from __future__ import annotations

import ast
import io
import json
import re
import tokenize
from datetime import datetime
from pathlib import Path

SCHEMA = "cosmos-duds/1"
JUDGE_FLOOR = 40
ATTEMPT_CAP = 5
ROLES = ("ORC", "WOMBAT", "CODER", "JUDGE", "CCR", "DAEMON")
HERO_ROLES = ("WOMBAT", "CODER", "JUDGE", "CCR")
WHAT = ("text", "python", "no_prose")
PLACEHOLDER_MISSION = ("filled per gitur wo", "unseated", "tbd")
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
SERVER_MARK = re.compile(
    r"\b(429|500|502|503|504|UNREACHABLE|rate.?limit|deprecated|model_not_found)\b",
    re.I,
)
LAYER_NAMES = (
    "l1_role", "l2_model", "l3_harness", "l4_wrapper",
    "l5_skills", "l6_tools", "l7_enviro", "l8_mission",
)


class DudsError(RuntimeError):
    def __init__(self, kind: str, detail: str = ""):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail or kind}")


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def womb_root(paths) -> Path:
    root = paths.state("womb")
    root.mkdir(parents=True, exist_ok=True)
    for name in ("spawn", "candidates", "gitur_inbox"):
        (root / name).mkdir(parents=True, exist_ok=True)
    return root


def _append(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _read_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")


def layers_of(rec: dict) -> dict:
    """Normalize a blueprint (l1_…) or a DUD.toml-shaped dict."""
    rec = rec or {}
    leg = rec.get("legend") if isinstance(rec.get("legend"), dict) else {}
    tail = rec.get("tail") if isinstance(rec.get("tail"), dict) else {}
    mission = rec.get("mission") if isinstance(rec.get("mission"), dict) else {}
    if "l1_role" in leg or "l8_mission" in tail:
        enviro = leg.get("l7_environment") if isinstance(leg.get("l7_environment"), dict) else {}
        return {
            "l1_role": leg.get("l1_role"),
            "l2_model": leg.get("l2_model"),
            "l3_harness": leg.get("l3_harness"),
            "l4_wrapper": leg.get("l4_wrapper_path"),
            "l5_skills": leg.get("l5_skills"),
            "l6_tools": leg.get("l6_tools"),
            "l7_enviro": enviro,
            "l8_mission": tail.get("l8_mission"),
        }
    output = leg.get("output") if isinstance(leg.get("output"), dict) else {}
    enviro = dict(leg.get("enviro") or {})
    if output.get("what") and "what" not in enviro:
        enviro["what"] = output.get("what")
    if output.get("optimum") is not None and "optimum" not in enviro:
        enviro["optimum"] = output.get("optimum")
    item = mission.get("item") or tail.get("l8_mission") or ""
    return {
        "l1_role": leg.get("role"),
        "l2_model": leg.get("model"),
        "l3_harness": leg.get("harness_via") or leg.get("harness"),
        "l4_wrapper": leg.get("wrapper"),
        "l5_skills": leg.get("skills"),
        "l6_tools": leg.get("tools"),
        "l7_enviro": enviro,
        "l8_mission": item,
    }


def require_duds(rec: dict, *, repo: Path | None = None) -> dict:
    """All eight layers written. Empty Role or Model refuses. Optimum 0 refuses."""
    got = layers_of(rec)
    missing = []
    role = str(got.get("l1_role") or "").strip().upper()
    if role not in ROLES:
        missing.append("l1_role")
    model = str(got.get("l2_model") or "").strip()
    if role != "DAEMON" and not model:
        missing.append("l2_model")
    harness = str(got.get("l3_harness") or "").strip()
    if role != "DAEMON" and not harness:
        missing.append("l3_harness")
    wrapper = str(got.get("l4_wrapper") or "").strip()
    if not wrapper:
        missing.append("l4_wrapper")
    else:
        path = Path(wrapper)
        if not path.is_file() and repo is not None:
            path = repo / wrapper
        if not path.is_file():
            missing.append("l4_wrapper")
        else:
            wrapper = str(path)
    skills = got.get("l5_skills")
    if not isinstance(skills, list):
        missing.append("l5_skills")
    tools = got.get("l6_tools")
    if not isinstance(tools, dict) or "allow" not in tools:
        missing.append("l6_tools")
    enviro = got.get("l7_enviro")
    if not isinstance(enviro, dict) or not enviro:
        missing.append("l7_enviro")
    else:
        opt = enviro.get("optimum")
        if opt in (0, "0"):
            missing.append("l7_enviro.optimum")
        what = enviro.get("what")
        if what is not None and str(what) not in WHAT:
            missing.append("l7_enviro.what")
    mission = str(got.get("l8_mission") or "").strip()
    if not mission or mission.lower() in PLACEHOLDER_MISSION:
        missing.append("l8_mission")
    if missing:
        raise DudsError("LAYERS_INCOMPLETE", ",".join(missing))
    if role == "ORC" and harness and "cod" in harness.lower():
        raise DudsError("ORC_NO_CODING", harness)
    return {
        "schema": SCHEMA,
        "l1_role": role,
        "l2_model": model,
        "l3_harness": harness,
        "l4_wrapper": wrapper,
        "l5_skills": list(skills),
        "l6_tools": dict(tools),
        "l7_enviro": dict(enviro),
        "l8_mission": mission,
    }


def cpu_first_pass(text: str, *, filename: str = "reply.py") -> list[dict]:
    """Three CPU checks on the saved reply. No model call."""
    body = text or ""
    rows = []
    if not body.strip():
        detail = "saved reply is empty"
        return [
            {"name": "py_compile", "status": "FAIL", "detail": detail},
            {"name": "fence", "status": "FAIL", "detail": detail},
            {"name": "tokenize", "status": "FAIL", "detail": detail},
        ]
    stripped = body.lstrip()
    first = stripped.splitlines()[0]
    if BTS_IMPORT.search(body):
        rows.append({"name": "fence", "status": "FAIL", "detail": "reply imports bts_*"})
    else:
        rows.append({"name": "fence", "status": "PASS", "detail": "no bts_ import"})
    if first.startswith("NONE") or first.startswith("diff --git"):
        rows.append({"name": "py_compile", "status": "PASS", "detail": first[:80]})
        rows.append({"name": "tokenize", "status": "PASS", "detail": "coder form, not a module"})
        return _order_cpu(rows)
    if stripped.startswith("{"):
        try:
            json.loads(body)
            rows.append({"name": "py_compile", "status": "PASS", "detail": "JSON parses"})
            rows.append({"name": "tokenize", "status": "PASS", "detail": "JSON, lexer skipped"})
        except json.JSONDecodeError as e:
            rows.append({"name": "py_compile", "status": "FAIL", "detail": e.msg})
            rows.append({"name": "tokenize", "status": "FAIL", "detail": "JSON does not parse"})
        return _order_cpu(rows)
    try:
        ast.parse(body, filename=filename)
        rows.append({"name": "py_compile", "status": "PASS", "detail": "ast.parse ok"})
    except SyntaxError as e:
        rows.append({
            "name": "py_compile", "status": "FAIL",
            "detail": f"syntax line {e.lineno}: {e.msg}",
        })
    try:
        list(tokenize.generate_tokens(io.StringIO(body).readline))
        rows.append({"name": "tokenize", "status": "PASS", "detail": "lexer ok"})
    except (tokenize.TokenError, SyntaxError, IndentationError) as e:
        rows.append({"name": "tokenize", "status": "FAIL", "detail": str(e)[:200]})
    return _order_cpu(rows)


def _order_cpu(rows: list[dict]) -> list[dict]:
    want = ("py_compile", "fence", "tokenize")
    by = {r["name"]: r for r in rows}
    return [by[name] for name in want if name in by]


def cpu_pass(rows: list[dict]) -> bool:
    return bool(rows) and all(r.get("status") == "PASS" for r in rows)


def xform(initial_prompt: str, error: str, attempt: int) -> str:
    """output/input. initial prompt + checker error → the next prompt. CPU only."""
    n = int(attempt or 1)
    return (
        str(initial_prompt or "").rstrip()
        + f"\n\n[xFORM attempt {n} — correct this output. Checker error:\n"
        + str(error or "").strip()
        + "\nReturn only the corrected output.]\n"
    )


def _sessions(paths) -> dict:
    return dict(_read_json(womb_root(paths) / "sessions.json", {}))


def _save_sessions(paths, board: dict) -> None:
    _write_json(womb_root(paths) / "sessions.json", board)


def _candidates(paths) -> list:
    raw = _read_json(womb_root(paths) / "candidates.json", [])
    return list(raw) if isinstance(raw, list) else []


def _save_candidates(paths, rows: list) -> None:
    _write_json(womb_root(paths) / "candidates.json", rows)


def _judge_seat(paths) -> dict:
    seat = _read_json(womb_root(paths) / "judge_seat.json", {})
    return seat if isinstance(seat, dict) else {}


def _model_of(rec: dict, duds: dict | None) -> str:
    if duds and duds.get("l2_model"):
        return str(duds["l2_model"])
    agent = rec.get("_agent") if isinstance(rec.get("_agent"), dict) else {}
    return str(rec.get("model") or agent.get("version") or agent.get("raw") or "unspecified")


def _session_id_of(rec: dict) -> str:
    run = rec.get("run") if isinstance(rec.get("run"), dict) else {}
    return str(rec.get("session_id") or run.get("session_id") or "")


def _area_of(rec: dict) -> str:
    return str(rec.get("area") or rec.get("target") or "")


def _server_blob(rec: dict) -> str:
    run = rec.get("run") if isinstance(rec.get("run"), dict) else {}
    return " ".join([
        str(rec.get("fail_kind") or ""),
        str(rec.get("fail_detail") or ""),
        str(run.get("err") or ""),
        str(run.get("out") or ""),
    ])


def _initial_prompt(rec: dict, duds: dict | None) -> str:
    if duds and duds.get("l8_mission"):
        return str(duds["l8_mission"])
    return str(rec.get("prompt") or rec.get("task") or "")


def watch_spawn(paths, duds: dict) -> dict:
    """WOMBAT row: a daemon summoned this HERO. Does not exec the model."""
    row = {
        "schema": SCHEMA,
        "at": _iso_now(),
        "action": "watch_spawn",
        "role": duds.get("l1_role"),
        "model": duds.get("l2_model"),
        "harness": duds.get("l3_harness"),
        "mission": str(duds.get("l8_mission") or "")[:240],
    }
    _append(womb_root(paths) / "wombat.jsonl", row)
    return row


def summon_hero(paths, rec: dict, *, repo: Path | None = None) -> dict:
    """Write the HERO on the WOMB and open its one session. No model exec."""
    duds = require_duds(rec, repo=repo)
    role = duds["l1_role"]
    if role not in HERO_ROLES:
        raise DudsError("NOT_A_HERO", role)
    model = duds["l2_model"]
    session_id = _session_id_of(rec) or f"{model}-{_iso_now()}"
    board = _sessions(paths)
    cur = board.get(model) if isinstance(board.get(model), dict) else None
    if cur and cur.get("state") == "open":
        raise DudsError("SESSION_BUSY", f"{model} session {cur.get('session_id')} is open")
    board[model] = {
        "session_id": session_id,
        "state": "open",
        "busy": False,
        "attempts": 0,
        "area": _area_of(rec),
        "role": role,
        "harness": duds["l3_harness"],
    }
    _save_sessions(paths, board)
    spawn = {
        "schema": SCHEMA, "session_id": session_id,
        "duds": duds, "source": rec,
    }
    _write_json(womb_root(paths) / "spawn" / f"{session_id}.json", spawn)
    watch_spawn(paths, duds)
    return {"session_id": session_id, "duds": duds, "action": "summoned"}


def _spawn_source(paths, session_id: str) -> dict | None:
    saved = _read_json(womb_root(paths) / "spawn" / f"{session_id}.json", {})
    src = saved.get("source") if isinstance(saved, dict) else None
    return src if isinstance(src, dict) else None


def _close_for_new_hero(paths, model: str, session: dict, reason: str) -> dict:
    old_id = str(session.get("session_id") or "")
    source = _spawn_source(paths, old_id)
    session["state"] = "closed"
    session["busy"] = False
    session["closed_reason"] = reason
    board = _sessions(paths)
    board[model] = session
    _save_sessions(paths, board)
    action = "spawn_new_hero"
    detail = reason
    if source:
        fresh = dict(source)
        fresh["session_id"] = f"{model}-hero-{int(session.get('attempts') or 0) + 1}"
        try:
            spawned = summon_hero(paths, fresh)
            detail = f"{reason}; new session {spawned['session_id']}"
        except DudsError as e:
            action = "hold_no_duds"
            detail = f"{reason}; {e.kind}: {e.detail}"
    else:
        action = "hold_no_duds"
        detail = reason + "; DUDs not written, no new HERO"
    return {"action": action, "detail": detail, "session_id": old_id}


def on_saved_reply(paths, rec: dict, text: str, *, force_error: str = "") -> dict:
    """CPU trio, then WOMBAT. Judge stays unseated under 40 passing sets."""
    rec = rec or {}
    duds = None
    if isinstance(rec.get("legend"), dict) or isinstance(rec.get("duds"), dict):
        try:
            duds = require_duds(rec.get("duds") or rec)
        except DudsError:
            duds = None
    model = _model_of(rec, duds)
    asked = _session_id_of(rec)
    area = _area_of(rec)
    board = _sessions(paths)
    cur = board.get(model) if isinstance(board.get(model), dict) else None
    if cur and cur.get("state") == "open":
        if asked and asked != cur.get("session_id"):
            raise DudsError(
                "SESSION_BUSY",
                f"WOMBAT reuses {model} session {cur.get('session_id')}",
            )
        session_id = str(cur.get("session_id"))
    else:
        session_id = asked or f"{model}-session"
        cur = {
            "session_id": session_id,
            "state": "open",
            "busy": False,
            "attempts": 0,
            "area": area,
            "role": (duds or {}).get("l1_role") or "CODER",
            "harness": (duds or {}).get("l3_harness") or "",
        }
    cur["area"] = area or cur.get("area") or ""
    fname = Path(str(rec.get("_output_path") or "reply.py")).name
    rows = cpu_first_pass(text, filename=fname)
    if force_error:
        rows = list(rows) + [{
            "name": "legacy_rail", "status": "FAIL", "detail": force_error[:240],
        }]
    passed = cpu_pass(rows) and not force_error
    server = bool(SERVER_MARK.search(_server_blob(rec)))
    root = womb_root(paths)
    oid = str(rec.get("order_id") or "unknown")
    crew = {
        "reaches_judge": False,
        "stage": "checked",
        "wombat": "watch",
        "session_id": session_id,
        "model": model,
        "cpu": rows,
    }
    if server or (not passed and int(cur.get("attempts") or 0) + 1 >= ATTEMPT_CAP):
        if not passed:
            cur["attempts"] = int(cur.get("attempts") or 0) + 1
        reason = "server_or_deprecated" if server else f"attempts={ATTEMPT_CAP}"
        if not passed:
            err = "; ".join(
                f"{r['name']}: {r['detail']}" for r in rows if r["status"] != "PASS"
            )
            _append(root / "scars.jsonl", {
                "schema": SCHEMA, "at": _iso_now(), "order_id": oid,
                "model": model, "session_id": session_id,
                "attempt": cur["attempts"], "error": err[:500],
            })
        closed = _close_for_new_hero(paths, model, cur, reason)
        crew.update({
            "wombat": closed["action"],
            "stage": "closed_session",
            "detail": closed["detail"],
            "reaches_judge": False,
        })
        _append(root / "wombat.jsonl", {
            "schema": SCHEMA, "at": _iso_now(), "order_id": oid,
            "action": closed["action"], "model": model,
            "session_id": session_id, "note": closed["detail"],
        })
        return {"crew_pipe": crew}

    if not passed:
        cur["attempts"] = int(cur.get("attempts") or 0) + 1
        cur["state"] = "open"
        err = "; ".join(
            f"{r['name']}: {r['detail']}" for r in rows if r["status"] != "PASS"
        )
        prompt = xform(_initial_prompt(rec, duds), err, cur["attempts"])
        _append(root / "scars.jsonl", {
            "schema": SCHEMA, "at": _iso_now(), "order_id": oid,
            "model": model, "session_id": session_id,
            "attempt": cur["attempts"], "error": err[:500],
        })
        _write_json(root / "reprompt" / f"{oid}.json", {
            "schema": SCHEMA,
            "order_id": oid,
            "session_id": session_id,
            "model": model,
            "attempt": cur["attempts"],
            "xform": prompt,
        })
        board[model] = cur
        _save_sessions(paths, board)
        crew.update({
            "wombat": "reprompt_session",
            "stage": "reprompt",
            "attempt": cur["attempts"],
            "xform": prompt,
        })
        _append(root / "wombat.jsonl", {
            "schema": SCHEMA, "at": _iso_now(), "order_id": oid,
            "action": "reprompt_session", "model": model,
            "session_id": session_id, "attempt": cur["attempts"],
        })
        return {"crew_pipe": crew}

    cur["attempts"] = 0
    cur["state"] = "open"
    board[model] = cur
    _save_sessions(paths, board)
    pile = _candidates(paths)
    pile.append({
        "order_id": oid,
        "model": model,
        "session_id": session_id,
        "area": cur.get("area") or "",
        "question": _initial_prompt(rec, duds)[:500],
        "reply_path": rec.get("_output_path"),
        "cpu": rows,
    })
    _save_candidates(paths, pile)
    crew.update({"wombat": "candidate", "stage": "candidate", "pile": len(pile)})
    _append(root / "wombat.jsonl", {
        "schema": SCHEMA, "at": _iso_now(), "order_id": oid,
        "action": "candidate", "model": model, "session_id": session_id,
        "pile": len(pile),
    })
    if len(pile) >= JUDGE_FLOOR and not _judge_seat(paths).get("seated"):
        crew["wombat"] = "summon_judge"
        crew["stage"] = "judge_waiting_duds"
    return {"crew_pipe": crew}


def summon_judge(paths, judge_rec: dict, *, repo: Path | None = None) -> dict:
    """WOMBAT summons the Judge HERO once 40 sets are waiting. No model exec."""
    pile = _candidates(paths)
    if len(pile) < JUDGE_FLOOR:
        raise DudsError("JUDGE_NOT_DUE", f"pile={len(pile)} floor={JUDGE_FLOOR}")
    if _judge_seat(paths).get("seated"):
        raise DudsError("JUDGE_SEATED", "retire the open Judge before a second summon")
    duds = require_duds(judge_rec, repo=repo)
    if duds["l1_role"] != "JUDGE":
        raise DudsError("NOT_A_JUDGE", duds["l1_role"])
    opened = summon_hero(paths, judge_rec, repo=repo)
    seat = {
        "schema": SCHEMA,
        "seated": True,
        "at": _iso_now(),
        "model": duds["l2_model"],
        "harness": duds["l3_harness"],
        "session_id": opened["session_id"],
        "pile": len(pile),
    }
    _write_json(womb_root(paths) / "judge_seat.json", seat)
    _append(womb_root(paths) / "wombat.jsonl", {
        "schema": SCHEMA, "at": seat["at"], "action": "summon_judge",
        "model": duds["l2_model"], "harness": duds["l3_harness"],
        "pile": len(pile),
    })
    return seat


def grade_pile(paths, *, best_order_id: str, corrected: str, comment: str,
               scores: dict, role: str, methodology: str = "") -> dict:
    """Judge files Gitur and the card. ORC cannot. Empty pile retires the Judge."""
    if str(role or "").strip().upper() == "ORC":
        raise DudsError("ORC_NO_GITUR", "the Judge files Gitur")
    seat = _judge_seat(paths)
    if not seat.get("seated"):
        raise DudsError("JUDGE_UNSEATED", "WOMBAT summons the Judge at 40")
    pile = _candidates(paths)
    ids = {row.get("order_id") for row in pile}
    if best_order_id not in ids:
        raise DudsError("NOT_IN_PILE", best_order_id)
    coders = sorted({str(row.get("model") or "") for row in pile})
    questions = [str(row.get("question") or "")[:200] for row in pile]
    answers = [str(row.get("reply_path") or "") for row in pile]
    card = {
        "schema": SCHEMA,
        "at": _iso_now(),
        "who": seat.get("model"),
        "harness": seat.get("harness"),
        "best_order_id": best_order_id,
        "scores": scores,
        "coders": coders,
        "questions": questions,
        "answers": answers,
        "comment": str(comment or "")[:800],
        "methodology": methodology or "cpu trio, then Judge HERO, then Gitur",
        "corrected": corrected,
    }
    root = womb_root(paths)
    _append(root / "judge_records.jsonl", card)
    _write_json(root / "gitur_inbox" / f"{best_order_id}.json", {
        "schema": SCHEMA,
        "order_id": best_order_id,
        "stage": "gitur",
        "filed_by": "JUDGE",
        "who": seat.get("model"),
        "corrected": corrected,
        "comment": card["comment"],
    })
    rest = [row for row in pile if row.get("order_id") != best_order_id]
    _save_candidates(paths, rest)
    retired = False
    if not rest:
        seat["seated"] = False
        seat["retired_at"] = _iso_now()
        _write_json(root / "judge_seat.json", seat)
        model = str(seat.get("model") or "")
        board = _sessions(paths)
        if model in board:
            board[model]["state"] = "closed"
            board[model]["closed_reason"] = "pile_zero"
            _save_sessions(paths, board)
        retired = True
        _append(root / "wombat.jsonl", {
            "schema": SCHEMA, "at": seat["retired_at"],
            "action": "judge_retire", "model": model,
        })
    return {"card": card, "retired": retired, "pile": len(rest)}


def _sample_duds(folder: Path, *, role: str, model: str, harness: str,
                 mission: str) -> dict:
    wrap = folder / f"{role}.md"
    wrap.write_text(f"# {role}\n", encoding="utf-8")
    return {
        "legend": {
            "l1_role": role,
            "l2_model": model,
            "l3_harness": harness,
            "l4_wrapper_path": str(wrap),
            "l5_skills": ["propose-diff"] if role == "CODER" else [],
            "l6_tools": {"allow": ["read"], "forbid": ["git_push"]},
            "l7_environment": {"cwd": str(folder), "what": "python", "optimum": "float"},
        },
        "tail": {"l8_mission": mission},
    }


def _selftest() -> int:
    import tempfile

    from cosmos_paths import CosmosPaths, write_sentinel

    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + label)
        if not cond:
            ok = False

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write_sentinel(root, tree_id="duds-test")
        (root / "state").mkdir()
        paths = CosmosPaths(root)
        pack = root / "pack"
        pack.mkdir()
        bare = {"legend": {"l1_role": "CODER"}, "tail": {}}
        refused = False
        try:
            require_duds(bare)
        except DudsError as e:
            refused = e.kind == "LAYERS_INCOMPLETE" and "l8_mission" in e.detail
        check("incomplete DUDs refuse summon", refused)

        coder = _sample_duds(pack, role="CODER", model="glm-5.3-flash",
                             harness="cli:pi", mission="write ping")
        coder["session_id"] = "glm-1"
        summoned = summon_hero(paths, coder)
        check("complete DUDs summon one HERO",
              summoned["session_id"] == "glm-1"
              and summoned["duds"]["l1_role"] == "CODER")
        busy = False
        try:
            summon_hero(paths, coder)
        except DudsError as e:
            busy = e.kind == "SESSION_BUSY"
        check("second session of the same model refuses", busy)

        good = "def ping():\n    return 1\n"
        reply = {
            "order_id": "wo-1",
            "state": "DONE",
            "session_id": "glm-1",
            "model": "glm-5.3-flash",
            "prompt": "write ping",
            "_output_path": "ping.py",
        }
        held = on_saved_reply(paths, dict(reply, order_id="wo-bad"), "def ping(\n")
        check("syntax fail xFORMs the same session",
              held["crew_pipe"]["wombat"] == "reprompt_session"
              and held["crew_pipe"]["session_id"] == "glm-1"
              and "write ping" in held["crew_pipe"]["xform"]
              and "syntax" in held["crew_pipe"]["xform"])
        check("scar recorded",
              (womb_root(paths) / "scars.jsonl").is_file())
        other = False
        try:
            on_saved_reply(paths, dict(reply, session_id="glm-2"), good)
        except DudsError as e:
            other = e.kind == "SESSION_BUSY"
        check("a second model session is not opened", other)

        for n in range(2, 5):
            on_saved_reply(paths, dict(reply, order_id=f"wo-bad-{n}"), "def ping(\n")
        closed = on_saved_reply(paths, dict(reply, order_id="wo-bad-5"), "def ping(\n")
        check("fifth fail closes the session and files a new HERO",
              closed["crew_pipe"]["wombat"] == "spawn_new_hero")

        ds = _sample_duds(pack, role="CODER", model="deepseek-v4-flash",
                          harness="cli:dsh", mission="write ping")
        ds["session_id"] = "ds-1"
        summon_hero(paths, ds)
        server = on_saved_reply(paths, {
            "order_id": "wo-server",
            "session_id": "ds-1",
            "model": "deepseek-v4-flash",
            "run": {"err": "503 unavailable"},
            "_output_path": "ping.py",
        }, good)
        check("server error closes that session and files a new HERO",
              server["crew_pipe"]["wombat"] == "spawn_new_hero")

        sid = _sessions(paths)["glm-5.3-flash"]["session_id"]
        for i in range(JUDGE_FLOOR):
            on_saved_reply(
                paths,
                dict(reply, order_id=f"wo-ok-{i}", session_id=sid),
                good,
            )
        check("40 candidates wait until WOMBAT summons the Judge",
              len(_candidates(paths)) == JUDGE_FLOOR
              and not _judge_seat(paths).get("seated"))
        judge = _sample_duds(pack, role="JUDGE", model="gpt-5.6-luna",
                             harness="codex exec", mission="grade the pile")
        judge["session_id"] = "luna-1"
        seat = summon_judge(paths, judge)
        check("40 sets summon the Judge in its harness",
              seat["seated"] is True and seat["harness"] == "codex exec"
              and seat["model"] == "gpt-5.6-luna")
        orc = False
        try:
            grade_pile(
                paths, best_order_id="wo-ok-0", corrected=good,
                comment="fine", scores={"wo-ok-0": 1}, role="ORC",
            )
        except DudsError as e:
            orc = e.kind == "ORC_NO_GITUR"
        check("ORC does not file Gitur", orc)
        graded = grade_pile(
            paths, best_order_id="wo-ok-0", corrected=good,
            comment="best of the pile", scores={"wo-ok-0": 1}, role="JUDGE",
        )
        check("Judge files Gitur and records who judged",
              graded["pile"] == JUDGE_FLOOR - 1
              and (womb_root(paths) / "gitur_inbox" / "wo-ok-0.json").is_file()
              and "gpt-5.6-luna" in (womb_root(paths) / "judge_records.jsonl").read_text(encoding="utf-8"))
        # Drain the rest without a second grade API loop: mark remaining judged.
        rest_ids = [row["order_id"] for row in _candidates(paths)]
        for oid in rest_ids:
            grade_pile(
                paths, best_order_id=oid, corrected=good,
                comment="accepted", scores={oid: 1}, role="JUDGE",
            )
        check("empty pile retires the Judge",
              _judge_seat(paths).get("seated") is False
              and _candidates(paths) == [])
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_duds: --selftest", file=sys.stderr)
    raise SystemExit(2)
