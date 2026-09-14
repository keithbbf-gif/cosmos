#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`cdeck-recents/1` → `sessions-app-list/1` / `sessions-app-open/1`.

Three invariants this module exists to hold:

  * **id-stable.** A row id is Core's id (`cow-<session_id>` for the Cowork
    family). A blank or duplicated id is ID_UNSTABLE; the projection never mints
    one from a `seq`. No fake ids.
  * **UNMEASURED is null, never 0.** An unavailable feed has `n_shown: null` and
    a `kind`. Zero rows on an available feed is a measured `0`.
  * **Legal is counted, not opened.** `omission.opened` is 0 by construction and
    `omission.counted` is null when Core did not report a count.
"""
from __future__ import annotations

import re

from sessions_refusals import SessionsAppRefusal

LIST_SCHEMA = "sessions-app-list/1"
OPEN_SCHEMA = "sessions-app-open/1"
PRODUCT = "Sessions"
UPSTREAM_SCHEMA = "cdeck-recents/1"
ROW_FIELDS = ("id", "date", "stream", "title")
ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
# Default open page: enough to read, never the whole transcript on the wire.
DEFAULT_TURN_FROM = 0
DEFAULT_TURN_TO = 20
TURN_PAGE_MAX = 100


def valid_id(rec_id: str) -> str:
    """An id goes to Core on the wire. Reject anything that is not id-shaped
    before it leaves this process."""
    rec_id = (rec_id or "").strip()
    if not ID_RE.match(rec_id):
        raise SessionsAppRefusal("BAD_ID", f"not id-shaped: {rec_id[:64]!r}")
    return rec_id


def parse_turn_range(turn_from, turn_to) -> tuple[int, int]:
    """Half-open [turn_from, turn_to). Defaults + hard page cap."""
    try:
        start = DEFAULT_TURN_FROM if turn_from is None else int(turn_from)
        end = DEFAULT_TURN_TO if turn_to is None else int(turn_to)
    except (TypeError, ValueError) as e:
        raise SessionsAppRefusal("BAD_TURN_RANGE",
                                 f"turn_from/turn_to must be integers: {e}") from e
    if start < 0 or end < 0:
        raise SessionsAppRefusal("BAD_TURN_RANGE",
                                 f"turn range must be non-negative: [{start}, {end})")
    if end < start:
        raise SessionsAppRefusal("BAD_TURN_RANGE",
                                 f"turn_to {end} is before turn_from {start}")
    if end - start > TURN_PAGE_MAX:
        raise SessionsAppRefusal(
            "BAD_TURN_RANGE",
            f"page of {end - start} turns exceeds the {TURN_PAGE_MAX}-turn cap")
    return start, end


def _turns_from_body(body: dict) -> list[dict]:
    """Prefer Core's structured turns; else split flat text on blank lines."""
    raw = body.get("turns")
    if isinstance(raw, list):
        out: list[dict] = []
        for i, t in enumerate(raw):
            if isinstance(t, dict):
                out.append({
                    "seq": int(t["seq"]) if isinstance(t.get("seq"), int) else i,
                    "role": t.get("role"),
                    "text": t.get("text") if isinstance(t.get("text"), str) else "",
                })
            elif isinstance(t, str):
                out.append({"seq": i, "role": None, "text": t})
        return out
    text = body.get("text")
    if not isinstance(text, str) or text == "":
        return []
    parts = text.split("\n\n")
    return [{"seq": i, "role": None, "text": p} for i, p in enumerate(parts)]


def _int_or_none(value) -> int | None:
    """A count Core did not report stays None. int(None) would be the 0 lie."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _omission(counted: int | None) -> dict:
    if counted is None:
        reason = "UNMEASURED"
    elif counted == 0:
        reason = "NONE_OMITTED"
    else:
        reason = "LEGAL_OMITTED"
    return {"reason": reason, "counted": counted, "opened": 0}


def _rows(raw) -> list[dict]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise SessionsAppRefusal("CORE_UNPARSEABLE", "rows is not a list")
    out: list[dict] = []
    seen: set[str] = set()
    for i, row in enumerate(raw):
        if not isinstance(row, dict):
            raise SessionsAppRefusal("CORE_UNPARSEABLE", f"row {i} is not an object")
        rec_id = row.get("id")
        if not isinstance(rec_id, str) or not rec_id.strip():
            raise SessionsAppRefusal("ID_UNSTABLE", f"row {i} carries no id")
        rec_id = rec_id.strip()
        if rec_id in seen:
            raise SessionsAppRefusal("ID_UNSTABLE", f"duplicate id {rec_id}")
        sid = row.get("session_id")
        if isinstance(sid, str) and sid and rec_id != f"cow-{sid}" \
                and rec_id.startswith("cow-"):
            raise SessionsAppRefusal(
                "ID_UNSTABLE", f"{rec_id} is not cow-{sid}")
        seen.add(rec_id)
        out.append({f: (rec_id if f == "id" else row.get(f)) for f in ROW_FIELDS})
    return out


def project_list(code: int, body: dict, source: str) -> dict:
    """Core's recents body → the app's list projection."""
    if body.get("error"):
        return {
            "schema": LIST_SCHEMA, "product": PRODUCT, "source": source,
            "http": code, "available": False,
            "kind": str(body["error"]), "tree_id": body.get("tree_id"),
            "n_shown": None, "omission": _omission(None), "rows": [],
            "upstream_schema": body.get("schema"),
            "detail": str(body.get("detail") or "")[:400] or None,
        }
    available = bool(body.get("available"))
    rows = _rows(body.get("rows")) if available else []
    counted = _int_or_none(body.get("n_omitted_legal"))
    return {
        "schema": LIST_SCHEMA,
        "product": PRODUCT,
        "source": source,
        "http": code,
        "available": available,
        "kind": str(body.get("kind") or ("OK" if available else "UNMEASURED")),
        "tree_id": body.get("tree_id"),
        # an unavailable feed has no measured count - null, not 0
        "n_shown": len(rows) if available else None,
        "omission": _omission(counted),
        "rows": rows,
        "upstream_schema": body.get("schema"),
        "detail": str(body.get("detail") or "")[:400] or None,
    }


def project_open(code: int, body: dict, rec_id: str, source: str,
                 turn_from=None, turn_to=None) -> dict:
    """Core's open body → the app's open projection. A legal (omitted) session
    is reported as omitted with opened=0, never rendered as empty text.

    The full transcript is never re-serialized onto the wire: only the requested
    turn range is projected. `text` stays None; `text_len` / `n_turns` keep the
    measured totals so a surface can page without guessing.
    """
    kind = str(body.get("kind") or body.get("error") or "UNMEASURED")
    text = body.get("text")
    omitted = kind == "LEGAL_OMITTED"
    start, end = parse_turn_range(turn_from, turn_to)
    all_turns = [] if omitted else _turns_from_body(body)
    page = all_turns[start:end]
    return {
        "schema": OPEN_SCHEMA,
        "product": PRODUCT,
        "source": source,
        "http": code,
        "ok": bool(body.get("ok")) and not omitted,
        "kind": kind,
        "id": rec_id,
        "opencode_id": body.get("opencode_id"),
        "title": body.get("title"),
        # Never dump the full transcript — the UI streams only `turns`.
        "text": None,
        "text_len": len(text) if isinstance(text, str) else None,
        "n_turns": len(all_turns),
        "turn_from": start,
        "turn_to": end,
        "turns": page,
        "openwork": body.get("openwork"),
        "omission": _omission(1 if omitted else None) if omitted else None,
        "detail": str(body.get("detail") or "")[:400] or None,
    }
