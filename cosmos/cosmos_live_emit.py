#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P04 live emit: values only Core :8770 can produce (not pytest rc=0).

    from cosmos_live_emit import require_live_emit, LiveEmitError, quote_tree_id
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_CORE_URL = "http://127.0.0.1:8770"
STATUS_PATH = "/api/v1/status"
EXPECTED_TREE_ID = "KMesh-COSMOS-live"
DEFAULT_TIMEOUT_S = 8.0


class LiveEmitError(Exception):
    """kind in {MISSING_EMIT, CORE_UNREACHABLE, BAD_EMIT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _read_api_token(paths) -> str | None:
    try:
        p = paths.config("api_token.txt")
    except Exception:  # noqa: BLE001
        return None
    if not Path(p).is_file():
        return None
    try:
        text = Path(p).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _fetch_status(*, base_url: str, token: str | None, timeout_s: float,
                  http=None) -> tuple[int, dict]:
    url = str(base_url).rstrip("/") + STATUS_PATH
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if http is not None:
        status, parsed = http("GET", url, None, headers)
        if not isinstance(parsed, dict):
            parsed = {}
        return int(status), parsed
    try:
        req = urllib.request.Request(url, method="GET", headers=headers)
        with urllib.request.urlopen(req, timeout=float(timeout_s)) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            try:
                parsed = json.loads(raw)
            except ValueError:
                parsed = {}
            return int(resp.status), parsed if isinstance(parsed, dict) else {}
    except urllib.error.HTTPError as e:
        raw = (e.read() or b"").decode("utf-8", "replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except ValueError:
            parsed = {}
        if not isinstance(parsed, dict):
            parsed = {}
        return int(e.code), parsed
    except Exception as e:  # noqa: BLE001
        raise LiveEmitError(
            "CORE_UNREACHABLE",
            f"{type(e).__name__}: {e}"[:200],
        ) from e


def quote_tree_id(status: dict) -> str | None:
    """Quote tree_id from a parsed /api/v1/status body (test helper)."""
    if not isinstance(status, dict):
        return None
    tid = status.get("tree_id")
    return str(tid) if tid is not None and str(tid).strip() else None


def require_live_emit(*, paths=None, base_url: str | None = None,
                      token: str | None = None, timeout_s: float = DEFAULT_TIMEOUT_S,
                      http=None) -> dict:
    """GET Core /api/v1/status; ready + tree_id=KMesh-COSMOS-live or MISSING_EMIT."""
    url_base = str(base_url or DEFAULT_CORE_URL)
    tok = token
    if tok is None and paths is not None:
        tok = _read_api_token(paths)
    status_code, status = _fetch_status(
        base_url=url_base, token=tok, timeout_s=timeout_s, http=http)
    if status_code != 200:
        raise LiveEmitError(
            "MISSING_EMIT",
            f"status HTTP {status_code} (want 200 ready {EXPECTED_TREE_ID})")
    if status.get("ready") is not True:
        raise LiveEmitError(
            "MISSING_EMIT",
            f"ready={status.get('ready')!r} (want True)")
    tid = quote_tree_id(status)
    if tid != EXPECTED_TREE_ID:
        raise LiveEmitError(
            "MISSING_EMIT",
            f"tree_id={tid!r} (want {EXPECTED_TREE_ID!r})")
    return {
        "ok": True,
        "tree_id": tid,
        "ready": True,
        "http": status_code,
        "url": url_base.rstrip("/") + STATUS_PATH,
    }
