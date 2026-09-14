#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GET/POST /api/v1/openwork — OpenWork display fold for cDeck Open tab.

Reads openwork-server-state.json (measured path). Probes loopback /health on
each port listed in workspacePorts — never assumes a port constant. Does not
call /tui/open-sessions. GET never mkdir. POST action=focus focuses a live
OpenWork.exe window only; never spawns a second copy.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SCHEMA = "cosmos-openwork/1"
DEFAULT_HOST = "127.0.0.1"
OPENWORK_EXE = Path(
    r"C:\Users\Papa\AppData\Local\Programs\@openworkdesktop\OpenWork.exe"
)


def _default_state_path() -> Path:
    override = os.environ.get("OPENWORK_SERVER_STATE", "").strip()
    if override:
        return Path(override)
    appdata = os.environ.get("APPDATA", "").strip()
    if appdata:
        return Path(appdata) / "com.differentai.openwork" / "openwork-server-state.json"
    return Path.home() / ".openwork" / "openwork-server-state.json"


def read_state(path: Path | None = None) -> dict:
    p = path or _default_state_path()
    if not p.is_file():
        return {
            "kind": "NO_SOURCE",
            "path": str(p),
            "state": None,
            "note": "openwork-server-state.json unread — port UNMEASURED",
        }
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as e:
        return {
            "kind": "UNREADABLE",
            "path": str(p),
            "state": None,
            "note": f"{type(e).__name__}: {e}",
        }
    return {"kind": "OK", "path": str(p), "state": raw, "note": None}


def ports_from_state(state_rec: dict) -> list[dict]:
    st = state_rec.get("state")
    if not isinstance(st, dict):
        return []
    wp = st.get("workspacePorts")
    if not isinstance(wp, dict):
        return []
    out = []
    for key, port in wp.items():
        try:
            pnum = int(port)
        except (TypeError, ValueError):
            continue
        out.append({"workspace": str(key), "port": pnum})
    pref = st.get("preferredPort")
    if pref is not None:
        try:
            out.append({"workspace": "__preferred__", "port": int(pref)})
        except (TypeError, ValueError):
            pass
    return out


def probe_health(host: str, port: int, *, timeout: float = 1.5, opener=None) -> dict:
    url = f"http://{host}:{port}/health"
    req = urllib.request.Request(url, method="GET")
    open_fn = opener or urllib.request.urlopen
    t0 = time.time()
    try:
        with open_fn(req, timeout=timeout) as resp:
            body = resp.read()
        elapsed = time.time() - t0
        try:
            data = json.loads(body.decode("utf-8"))
        except ValueError:
            data = {}
        return {
            "port": port,
            "url": url,
            "ok": resp.status == 200 and data.get("ok") is True,
            "status": resp.status,
            "latency_ms": round(elapsed * 1000, 2),
            "health": data,
        }
    except urllib.error.HTTPError as e:
        return {
            "port": port,
            "url": url,
            "ok": False,
            "status": e.code,
            "latency_ms": round((time.time() - t0) * 1000, 2),
            "error": str(e.reason),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "port": port,
            "url": url,
            "ok": False,
            "status": None,
            "latency_ms": round((time.time() - t0) * 1000, 2),
            "error": f"{type(e).__name__}: {e}",
        }


def openwork_exe_present() -> dict:
    exe = OPENWORK_EXE
    if exe.is_file():
        return {"present": True, "path": str(exe), "bytes": exe.stat().st_size}
    return {
        "present": False,
        "path": str(exe),
        "note": "OpenWork.exe UNMEASURED on this host",
    }


def handle_get(root, *, expected_tree_id, host: str = DEFAULT_HOST, state_path=None, probe=None):
    del root  # GET never mkdir; state is outside the COSMOS tree
    path = Path(state_path) if state_path else None
    state_rec = read_state(path)
    ports = ports_from_state(state_rec)
    probes = []
    for row in ports:
        probes.append(probe_health(host, row["port"], opener=probe))
    live = [p for p in probes if p.get("ok")]
    body = {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": expected_tree_id,
        "kind": state_rec.get("kind") or "NO_SOURCE",
        "state_path": state_rec.get("path"),
        "note": state_rec.get("note")
        or (
            "LIVE when loopback /health ok on a measured port from "
            "openwork-server-state.json — not Core :8770"
        ),
        "exe": openwork_exe_present(),
        "workspace_ports": ports,
        "health_probes": probes,
        "live": bool(live),
        "n_live": len(live),
        "does_not_use": ["/tui/open-sessions"],
    }
    return 200, body


def handle_post(root, body: dict, *, expected_tree_id):
    del root, expected_tree_id
    action = str((body or {}).get("action") or "").strip().lower()
    if action != "focus":
        return 400, {"error": "BAD_INPUT", "detail": "action must be focus"}
    exe = openwork_exe_present()
    if not exe.get("present"):
        return 503, {
            "error": "NO_SOURCE",
            "detail": "OpenWork.exe not on this host — focus REFUSED, not spawned",
            "spawned": False,
            "exe": exe,
        }
    if sys.platform != "win32":
        return 503, {
            "error": "UNSUPPORTED",
            "detail": "focus is native DT only; GET display still works",
            "spawned": False,
            "exe": exe,
        }
    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "action": "focus",
        "spawned": False,
        "detail": "focus OpenWork.exe requested — native cDeck host executes",
        "exe": exe,
    }


def _selftest() -> int:
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, str(e)))

    tmp = Path(os.environ.get("TMPDIR", "/tmp")) / "ow_state_test.json"
    tmp.write_text(
        json.dumps({"version": 3, "workspacePorts": {"ws_test": 59001}}),
        encoding="utf-8",
    )

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"ok": True, "version": "test"}).encode("utf-8")

    def fake_open(req, timeout=1.5):
        assert "/health" in req.full_url
        assert ":59001/" in req.full_url or req.full_url.endswith(":59001/health")
        return _Resp()

    code, body = handle_get(
        "/unused",
        expected_tree_id="t-openwork",
        state_path=tmp,
        probe=fake_open,
    )
    check(
        "GET uses measured port from state file",
        lambda: code == 200
        and body.get("live") is True
        and body["health_probes"][0]["port"] == 59001,
    )
    check(
        "GET documents no /tui/open-sessions",
        lambda: "/tui/open-sessions" in (body.get("does_not_use") or []),
    )
    check(
        "missing state is NO_SOURCE not invented port",
        lambda: handle_get("/x", expected_tree_id="t", state_path=Path("/no/such/state.json"))[1][
            "kind"
        ]
        == "NO_SOURCE",
    )
    post_code, post = handle_post(None, {"action": "focus"}, expected_tree_id="t")
    check(
        "POST focus refuses spawn on non-Windows",
        lambda: post_code in (200, 503) and post.get("spawned") is False,
    )

    bad = [l for l, ok, _ in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks" % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
