#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic GET/POST /api/v1/openwork via Core Service (no live :8770)."""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))
sys.path.insert(0, str(REPO / "builds" / "cdeck"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="openwork_api_"))
    state = td / "openwork-server-state.json"
    state.write_text(
        json.dumps({"version": 3, "workspacePorts": {"ws_x": 59002}}),
        encoding="utf-8",
    )
    root = install(td / "live", tree_id="openwork-api")
    k = Kernel(root, worker="core")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    base = f"http://127.0.0.1:{svc.port}"

    import cosmos_openwork_panel as ow  # noqa: E402

    orig = ow._default_state_path
    ow._default_state_path = lambda: state  # type: ignore[assignment]

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"ok": True}).encode("utf-8")

    ow.probe_health = lambda host, port, **kw: {  # type: ignore[assignment]
        "port": port,
        "ok": port == 59002,
        "url": f"http://{host}:{port}/health",
    }

    def get(path):
        req = urllib.request.Request(base + path)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def post(path, body):
        req = urllib.request.Request(
            base + path,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    try:
        st, body = get("/api/v1/openwork")
        check(
            "GET /api/v1/openwork 200 live on measured port",
            lambda: st == 200 and body.get("ok") is True and body.get("live") is True
            and body.get("tree_id") == "openwork-api",
        )
        check(
            "GET body refuses /tui/open-sessions",
            lambda: "/tui/open-sessions" in (body.get("does_not_use") or []),
        )
        pst, pbody = post("/api/v1/openwork", {"action": "focus"})
        check(
            "POST focus never spawns",
            lambda: pst in (200, 503) and pbody.get("spawned") is False,
        )
    finally:
        ow._default_state_path = orig  # type: ignore[assignment]
        svc.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_openwork_panel_api():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
