#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck header control pins + Core path fixture (no live :8770 required).

Run:  py -3.14 builds/cdeck/test_deck_features.py
      py -3.14 test_deck_features.py   (repo-root wrapper)
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from http.client import HTTPConnection
from pathlib import Path

REPO = Path(__file__).resolve().parent
UI = REPO / "ui"
COSMOS = REPO.parents[1] / "cosmos"
sys.path.insert(0, str(COSMOS.parent))
sys.path.insert(0, str(COSMOS))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_service import Service  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def _read(name: str) -> str:
    p = UI / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def static_pins() -> None:
    header = _read("header.js")
    index = _read("index.html")
    backup = _read("deck_backup.js")

    check(
        "HDR-1 apiGet/apiPost exported for pane scripts",
        "window.apiGet = apiGet" in header and "window.apiPost = apiPost" in header,
        "exports=%s" % ("window.apiGet" in header),
    )
    check(
        "HDR-2 kitForTab helper for pane iframes",
        "function kitForTab" in header and "window.kitForTab = kitForTab" in header,
        "kitForTab=%s" % ("function kitForTab" in header),
    )
    check(
        "HDR-3 CONNECT uses documented GET /api/v1/status + /api/v1/health",
        '"/api/v1/status"' in header and '"/api/v1/health"' in header,
        "paths=%s" % ('"/api/v1/status"' in header),
    )
    check(
        "HDR-4 auto-connect on DOM ready",
        "connectOnLoad" in header
        and bool(re.search(r"DOMContentLoaded.*init|init\(\)", header, re.S)),
        "connectOnLoad=%s" % ("connectOnLoad" in header),
    )
    check(
        "HDR-5 RELOAD button wired (btnReload)",
        'id="btnReload"' in index and "btnReload" in header and "onReloadClick" in header,
        "btnReload=%s" % ('id="btnReload"' in index),
    )
    check(
        "HDR-6 honest disabled: refresh buttons gated by setRefreshControlsEnabled",
        "setRefreshControlsEnabled(false)" in header
        or "setRefreshControlsEnabled(!on)" in header
        or "setRefreshControlsEnabled(on)" in header,
        "setter=%s" % ("setRefreshControlsEnabled" in header),
    )
    check(
        "HDR-7 app.js does not override header transport when header loaded first",
        "window.apiGet" in _read("app.js") and "return;" in _read("app.js"),
        "app_guard=%s" % ("return;" in _read("app.js")),
    )
    check(
        "BAK-1 backup pane script shipped and names GET fold contract",
        "deck_backup.js" in index
        and 'apiGet("/api/v1/backup")' in backup
        and "GET never runs a backup" in backup,
        "deck_backup.js",
    )


def core_fixture_pins() -> None:
    td = Path(tempfile.mkdtemp(prefix="cdeck_hdr_"))
    root = install(td / "live", tree_id="cdeck-header-fixture")
    k = Kernel(root, worker="core")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        port = svc.port

        def get(path: str) -> tuple[int, dict]:
            c = HTTPConnection("127.0.0.1", port, timeout=15)
            try:
                c.request("GET", path)
                r = c.getresponse()
                body = r.read()
                try:
                    j = json.loads(body.decode("utf-8"))
                except ValueError:
                    j = {}
                return r.status, j
            finally:
                c.close()

        def post(path: str, payload: dict) -> tuple[int, dict]:
            c = HTTPConnection("127.0.0.1", port, timeout=15)
            try:
                c.request(
                    "POST",
                    path,
                    body=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                r = c.getresponse()
                body = r.read()
                try:
                    j = json.loads(body.decode("utf-8"))
                except ValueError:
                    j = {}
                return r.status, j
            finally:
                c.close()

        st, j = get("/api/v1/status")
        check(
            "FIX-1 loopback GET /api/v1/status ready (CONNECT probe path)",
            st == 200 and j.get("ready") is True and j.get("tree_id") == "cdeck-header-fixture",
            "status=%s ready=%s" % (st, j.get("ready")),
        )
        st_j, j_j = get("/api/v1/jobs")
        check(
            "FIX-2 loopback GET /api/v1/jobs (panel refresh family)",
            st_j == 200 and isinstance(j_j, dict) and "jobs" in j_j,
            "status=%s" % st_j,
        )
        st_js, _ = get("/cdeck/header.js")
        disk = (UI / "header.js").read_bytes()
        c = HTTPConnection("127.0.0.1", port, timeout=15)
        try:
            c.request("GET", "/cdeck/header.js")
            r = c.getresponse()
            body = r.read()
        finally:
            c.close()
        check(
            "FIX-3 Core serves header.js bytes from builds/cdeck/ui/",
            st_js == 200 and body == disk,
            "status=%s bytes=%s disk=%s" % (st_js, len(body), len(disk)),
        )

        hb_path = CosmosPaths(root).logs("backup_clock_heartbeat.json")
        hb_before = hb_path.is_file()
        st_b, j_b = get("/api/v1/backup")
        hb_after = hb_path.is_file()
        check(
            "BAK-2 GET /api/v1/backup returns fold and never runs a backup (no heartbeat mkdir)",
            st_b == 200
            and j_b.get("schema") == "cosmos-backup-fold/1"
            and "never runs a backup" in (j_b.get("note") or "")
            and hb_before == hb_after
            and isinstance(j_b.get("profiles"), list),
            "status=%s kind=%s hb_created=%s"
            % (st_b, j_b.get("kind"), hb_after and not hb_before),
        )

        st_p, j_p = post(
            "/api/v1/backup",
            {"action": "surface_test", "measure_all": True},
        )
        check(
            "BAK-3 POST surface_test measure_all returns SURFACE_TEST",
            st_p == 200
            and j_p.get("kind") == "SURFACE_TEST"
            and j_p.get("measure_all") is True,
            "status=%s kind=%s" % (st_p, j_p.get("kind")),
        )

        st_r, j_r = post("/api/v1/backup", {"action": "restore"})
        check(
            "BAK-4 POST restore without bak is 400 BAK_REQUIRED",
            st_r == 400 and j_r.get("error") == "BAK_REQUIRED",
            "status=%s error=%s" % (st_r, j_r.get("error")),
        )
    finally:
        svc.shutdown()


def main() -> int:
    static_pins()
    core_fixture_pins()
    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print("  %s  %s%s" % (mark, label, ("  [" + detail + "]") if detail and not ok else ""))
    print(
        "SELFTEST %s %d/%d"
        % ("PASS" if not failed else "FAIL", len(RESULTS) - len(failed), len(RESULTS))
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
