#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_rolled — read the ROLLED.md milestone feed.

Schema: rolled-event/1 lines, pipe-separated: t | seat | kind | title | ref
Default file: live/state/ROLLED.md. Override: COSMOS_ROLLED_FEED (env path).
Parse lines directly. Order (t, seq). Empty ref → UNRESOLVED. Absent → explicit empty.

GET /api/v1/rolled is read-only; it never mkdir or write.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

SCHEMA = "cosmos-rolled/1"
EVENT_SCHEMA = "rolled-event/1"
FEED_ENV = "COSMOS_ROLLED_FEED"
_ROLLED_MD = "ROLLED.md"
_STATE_ROLE = "state"


def parse_event_line(line: str, seq: int) -> dict | None:
    """Parse one `rolled-event/1 t | seat | kind | title | ref` line.

    seq is the line index (stable tie-break). Empty/missing ref is UNRESOLVED.
    Returns None if the line does not match the schema.
    """
    stripped = line.strip()
    if not stripped.startswith(EVENT_SCHEMA):
        return None
    body = stripped[len(EVENT_SCHEMA):].strip()
    parts = [p.strip() for p in body.split("|")]
    if len(parts) < 4:
        return None
    t = parts[0] if len(parts) > 0 else ""
    seat = parts[1] if len(parts) > 1 else ""
    kind = parts[2] if len(parts) > 2 else ""
    title = parts[3] if len(parts) > 3 else ""
    ref = parts[4] if len(parts) > 4 else ""
    unresolved = not ref
    return {
        "t": t,
        "seq": int(seq),
        "seat": seat,
        "kind": kind,
        "title": title,
        "ref": "UNRESOLVED" if unresolved else ref,
        "ref_status": "UNRESOLVED" if unresolved else "OK",
    }


def parse_feed_text(text: str) -> list[dict]:
    """Parse rolled-event/1 lines directly; order by (t, seq)."""
    events: list[dict] = []
    for i, line in enumerate(text.splitlines()):
        ev = parse_event_line(line, i)
        if ev is not None:
            events.append(ev)
    events.sort(key=lambda e: (str(e.get("t") or ""), int(e.get("seq") or 0)))
    return events


def _resolve_feed_path(paths) -> tuple[Path | None, str, str]:
    """Return (path_or_None, source_label, kind_if_unresolved).

    COSMOS_ROLLED_FEED wins when set. GET never mkdir.
    """
    env = (os.environ.get(FEED_ENV) or "").strip()
    if env:
        return Path(env), FEED_ENV, ""
    if paths is None:
        return None, "NO_PATHS", "PATH_ERROR"
    try:
        return paths.state(_ROLLED_MD), _ROLLED_MD, ""
    except Exception:  # noqa: BLE001
        return None, "PATH_ERROR", "PATH_ERROR"


def snapshot(paths) -> dict:
    """Return the ROLLED feed as a structured dict.

    Always returns a valid dict. Events list is empty when the file is absent
    (explicit empty — kind=NO_SOURCE). GET never writes or mkdir.
    """
    result: dict = {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "available": False,
        "kind": "NO_SOURCE",
        "events": [],
        "n": 0,
        "source": None,
    }
    rolled_path, source, path_kind = _resolve_feed_path(paths)
    if path_kind:
        result["kind"] = path_kind
        result["source"] = source
        return result
    if rolled_path is None:
        return result

    result["source"] = source
    if not rolled_path.exists():
        return result

    result["available"] = True
    try:
        text = rolled_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        result["available"] = False
        result["kind"] = "READ_ERROR"
        result["detail"] = str(exc)[:300]
        return result

    events = parse_feed_text(text)
    result["kind"] = "OK"
    result["events"] = events
    result["n"] = len(events)
    return result


def _selftest() -> int:
    """Timeline parse pin: order (t, seq), UNRESOLVED refs, empty explicit."""
    import tempfile

    results: list[tuple[str, bool, str]] = []

    def check(label: str, ok: bool, detail: str = "") -> None:
        results.append((label, bool(ok), detail))

    fixture = "\n".join((
        "# comment — not a rolled-event/1 line",
        "rolled-event/1 2026-09-14T12:00:00Z | Cm | APPLIED | later-empty |",
        "rolled-event/1 2026-09-14T11:00:00Z | CCr | OK | earlier | ledger#seq=1",
        "rolled-event/1 2026-09-14T12:00:00Z | Cm | WARN | later-ref | docs/X.md",
        "not-schema",
        "rolled-event/1 only|two|parts",
    ))
    evs = parse_feed_text(fixture)
    check("parse three rolled-event/1 lines (junk dropped)", len(evs) == 3)
    check(
        "order (t, seq) — earlier first; same-t keeps file seq",
        [e["title"] for e in evs] == ["earlier", "later-empty", "later-ref"]
        and evs[1]["seq"] < evs[2]["seq"],
    )
    check(
        "empty ref marked UNRESOLVED; present ref stays",
        evs[1]["ref"] == "UNRESOLVED"
        and evs[1]["ref_status"] == "UNRESOLVED"
        and evs[0]["ref"] == "ledger#seq=1"
        and evs[0]["ref_status"] == "OK"
        and evs[2]["ref"] == "docs/X.md",
    )
    check("empty text is explicit empty list", parse_feed_text("") == [])

    td = Path(tempfile.mkdtemp(prefix="cosmos_rolled_"))
    feed = td / "ROLLED.md"
    feed.write_text(fixture + "\n", encoding="utf-8")
    prev = os.environ.get(FEED_ENV)
    os.environ[FEED_ENV] = str(feed)

    class _NoPaths:
        def state(self, *a, **k):
            raise AssertionError("COSMOS_ROLLED_FEED must win")

    try:
        rec = snapshot(_NoPaths())
        check(
            "COSMOS_ROLLED_FEED env path wins; n=3 ordered",
            rec.get("source") == FEED_ENV
            and rec.get("kind") == "OK"
            and rec.get("available") is True
            and rec.get("n") == 3
            and [e["title"] for e in rec["events"]]
            == ["earlier", "later-empty", "later-ref"],
        )
        os.environ[FEED_ENV] = str(td / "missing.md")
        missing = snapshot(_NoPaths())
        check(
            "missing COSMOS_ROLLED_FEED is explicit empty NO_SOURCE",
            missing.get("kind") == "NO_SOURCE"
            and missing.get("available") is False
            and missing.get("events") == []
            and missing.get("n") == 0
            and missing.get("source") == FEED_ENV,
        )
    finally:
        if prev is None:
            os.environ.pop(FEED_ENV, None)
        else:
            os.environ[FEED_ENV] = prev

    failed = [r for r in results if not r[1]]
    for label, ok, detail in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              (" — " + detail) if detail and not ok else ""))
    print("SELFTEST %s - %d checks (rolled feed parse)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
