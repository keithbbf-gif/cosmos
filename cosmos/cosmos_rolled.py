#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_rolled — read the ROLLED milestone feed.

Schema: rolled-event/1 lines, pipe-separated:
  t | seat | kind | title | ref [| seq]

Sources (first match wins for path list):
  - env COSMOS_ROLLED_FEED — os.pathsep-separated list of .md files
  - else live/state/ROLLED.md

GET /api/v1/rolled is read-only; it never mkdir or write.
Events are ordered by (t, seq). Refs that name missing paths → UNRESOLVED.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

SCHEMA = "cosmos-rolled/1"
EVENT_SCHEMA = "rolled-event/1"
_ROLLED_MD = "ROLLED.md"
_FEED_ENV = "COSMOS_ROLLED_FEED"


def _parse_event_line(line: str) -> dict | None:
    """Parse one `rolled-event/1 t | seat | kind | title | ref [| seq]` line."""
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
    seq: int | None = None
    if len(parts) > 5 and parts[5] != "":
        try:
            seq = int(parts[5])
        except ValueError:
            seq = None
    return {"t": t, "seat": seat, "kind": kind, "title": title, "ref": ref, "seq": seq}


def _resolve_ref(ref: str, paths) -> str:
    """Keep http(s) refs; verify path-like refs against live root; else UNRESOLVED."""
    r = (ref or "").strip()
    if not r:
        return ""
    if r.upper() == "UNRESOLVED":
        return "UNRESOLVED"
    if r.startswith(("http://", "https://")):
        return r
    if paths is None:
        return "UNRESOLVED"
    try:
        root = Path(paths.root)
    except Exception:  # noqa: BLE001
        return "UNRESOLVED"
    candidates = [
        Path(r),
        root / r,
        root / "state" / r,
    ]
    for p in candidates:
        try:
            if p.is_file():
                return r
        except OSError:
            continue
    return "UNRESOLVED"


def parse_feed_text(text: str, *, paths=None, source: str | None = None) -> list[dict]:
    """Parse rolled-event/1 lines from one markdown blob."""
    events: list[dict] = []
    auto_seq = 0
    for line in text.splitlines():
        ev = _parse_event_line(line)
        if ev is None:
            continue
        auto_seq += 1
        if ev.get("seq") is None:
            ev["seq"] = auto_seq
        ev["ref"] = _resolve_ref(ev.get("ref") or "", paths)
        if source:
            ev["source"] = source
        events.append(ev)
    return events


def sort_events(events: list[dict]) -> list[dict]:
    return sorted(
        events,
        key=lambda e: (str(e.get("t") or ""), int(e.get("seq") or 0)),
    )


def _feed_paths(paths) -> list[Path]:
    raw = (os.environ.get(_FEED_ENV) or "").strip()
    if raw:
        out: list[Path] = []
        for part in raw.split(os.pathsep):
            part = part.strip().strip('"')
            if part:
                out.append(Path(part))
        return out
    try:
        return [paths.state(_ROLLED_MD)]
    except Exception:  # noqa: BLE001
        return []


def snapshot(paths) -> dict:
    """Return feed texts + parsed events from COSMOS_ROLLED_FEED or state/ROLLED.md."""
    result: dict = {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "available": False,
        "kind": "NO_SOURCE",
        "events": [],
        "feeds": [],
        "n": 0,
        "sources": [],
        "feed_env": _FEED_ENV,
    }
    feed_paths = _feed_paths(paths)
    if not feed_paths:
        result["kind"] = "PATH_ERROR"
        return result

    feeds: list[dict] = []
    sources: list[str] = []
    any_exists = False
    for p in feed_paths:
        src = str(p)
        sources.append(src)
        if not p.is_file():
            feeds.append({"source": src, "text": "", "present": False})
            continue
        any_exists = True
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            result["kind"] = "READ_ERROR"
            result["detail"] = str(exc)[:300]
            result["sources"] = sources
            result["feeds"] = feeds
            return result
        feeds.append({"source": src, "text": text, "present": True})

    result["sources"] = sources
    result["feeds"] = feeds

    if not any_exists:
        return result

    result["available"] = True
    all_events: list[dict] = []
    for fd in feeds:
        if not fd.get("present"):
            continue
        all_events.extend(
            parse_feed_text(fd.get("text") or "", paths=paths, source=fd.get("source"))
        )
    all_events = sort_events(all_events)
    result["kind"] = "OK" if all_events else "EMPTY"
    result["events"] = all_events
    result["n"] = len(all_events)
    return result


def _selftest() -> int:
    import tempfile

    sys_path = Path(__file__).resolve().parent
    import sys

    sys.path.insert(0, str(sys_path))
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results: list[tuple[str, bool, str]] = []

    def check(label: str, fn) -> None:
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_rolled_"))
    root = install(td / "live", tree_id="spike-rolled")
    paths = CosmosPaths(root)
    md = Path(td / "a.md")
    md.write_text(
        "rolled-event/1 2026-09-01T12:00:00Z | Cm | OK | Alpha | missing.md | 2\n"
        "rolled-event/1 2026-09-01T11:00:00Z | Cm | OK | Beta | https://x.test | 1\n",
        encoding="utf-8",
    )
    prev = os.environ.get(_FEED_ENV)
    os.environ[_FEED_ENV] = str(md)
    try:
        snap = snapshot(paths)
        check("COSMOS_ROLLED_FEED file parsed", lambda: snap.get("kind") == "OK" and snap.get("n") == 2)
        evs = snap.get("events") or []
        check(
            "events sorted by (t, seq)",
            lambda: len(evs) == 2
            and evs[0].get("title") == "Beta"
            and evs[1].get("title") == "Alpha",
        )
        check(
            "missing path ref is UNRESOLVED",
            lambda: evs[1].get("ref") == "UNRESOLVED"
            and evs[0].get("ref") == "https://x.test",
        )
        empty_md = Path(td / "empty.md")
        empty_md.write_text("# no events\n", encoding="utf-8")
        os.environ[_FEED_ENV] = str(empty_md)
        snap_empty = snapshot(paths)
        check("explicit empty when no lines", lambda: snap_empty.get("kind") == "EMPTY")
    finally:
        if prev is None:
            os.environ.pop(_FEED_ENV, None)
        else:
            os.environ[_FEED_ENV] = prev

    failed = [r for r in results if not r[1]]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (rolled feed)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
