#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only client of Core's recents route. Core stays the one authority.

The app never computes recents and never writes the runtime root: it GETs
`/api/v1/recents` (list) and `/api/v1/recents?open=1&id=<id>` (open) from the
resident Core and projects what came back. Core down is CORE_UNREACHABLE with a
null count — never an empty list dressed as "no sessions".

Huge open payloads are refused BEFORE `read()` when the declared Content-Length
exceeds MAX_RESPONSE_BYTES (typed TOO_LARGE + size + cap). An absent or lying
declaration is still hard-capped on the read itself so a chunked or mis-sized
response cannot allocate unbounded memory in this process.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

from sessions_refusals import SessionsAppRefusal

DEFAULT_CORE = "http://127.0.0.1:8770"
RECENTS_PATH = "/api/v1/recents"
TIMEOUT_S = 15
# Mirrors Core's general POST body cap. An open of a multi-MB transcript must
# not land as one in-process buffer on either Sessions surface.
MAX_RESPONSE_BYTES = 1 << 20


def read_token(root: str | Path | None, explicit: str | None = None) -> str | None:
    """Bearer for a non-loopback Core. Loopback /api/v1 auto-connects (DT), so
    None is a normal answer, not a failure."""
    if explicit:
        return explicit.strip() or None
    if root is None:
        return None
    p = Path(root) / "config" / "api_token.txt"
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8").strip() or None


def _declared_size(headers) -> int | None:
    """Content-Length when present and well-formed; BAD_LENGTH otherwise."""
    raw = headers.get("Content-Length") if headers is not None else None
    if raw is None:
        return None
    try:
        n = int(raw)
    except (TypeError, ValueError) as e:
        raise SessionsAppRefusal(
            "BAD_LENGTH", f"Content-Length is not an integer: {str(raw)[:64]!r}"
        ) from e
    if n < 0:
        raise SessionsAppRefusal("BAD_LENGTH", "Content-Length must be non-negative")
    return n


def _read_capped(resp, *, cap: int = MAX_RESPONSE_BYTES) -> bytes:
    """Refuse on declared size before any body read; hard-cap the read itself."""
    declared = _declared_size(getattr(resp, "headers", None))
    if declared is not None and declared > cap:
        # Close without consuming — the declaration alone is the refuse signal.
        try:
            resp.close()
        except Exception:  # noqa: BLE001
            pass
        raise SessionsAppRefusal(
            "TOO_LARGE",
            f"response of {declared} bytes exceeds the {cap}-byte cap",
            size=declared, cap=cap)
    # cap+1 detects overflow without allocating the whole remote body.
    raw = resp.read(cap + 1)
    if len(raw) > cap:
        raise SessionsAppRefusal(
            "TOO_LARGE",
            f"response exceeds the {cap}-byte cap (read {len(raw)} bytes)",
            size=len(raw), cap=cap)
    return raw


def _get(base: str, path: str, query: dict | None, token: str | None) -> tuple[int, dict]:
    url = base.rstrip("/") + path
    if query:
        url += "?" + urlencode(query)
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            raw = _read_capped(resp)
            code = resp.status
    except SessionsAppRefusal:
        raise
    except urllib.error.HTTPError as e:
        try:
            raw = _read_capped(e)
        except SessionsAppRefusal:
            raise
        code = e.code
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise SessionsAppRefusal("CORE_UNREACHABLE", f"{url}: {e}") from e
    try:
        body = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise SessionsAppRefusal("CORE_UNPARSEABLE", f"{url}: {e}") from e
    if not isinstance(body, dict):
        raise SessionsAppRefusal("CORE_UNPARSEABLE", f"{url}: body is not an object")
    if code == 401:
        raise SessionsAppRefusal("CORE_REFUSED", f"{url}: UNAUTHORIZED (bearer required)")
    return code, body


def recents(base: str = DEFAULT_CORE, token: str | None = None) -> tuple[int, dict]:
    """The list projection, verbatim from Core."""
    return _get(base, RECENTS_PATH, None, token)


def recents_open(rec_id: str, base: str = DEFAULT_CORE,
                 token: str | None = None) -> tuple[int, dict]:
    """One session, verbatim from Core. `rec_id` goes on the wire, never onto a
    filesystem path — Core owns the store."""
    return _get(base, RECENTS_PATH, {"open": "1", "id": rec_id}, token)


def source_url(base: str = DEFAULT_CORE) -> str:
    return base.rstrip("/") + RECENTS_PATH
