#!/usr/bin/env py -3.14
"""XTalk stream: GET never mkdir. Transport A is a hole. Transport B appends."""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import Kernel, install
from cosmos_service import Service
from cosmos_xtalk import _selftest


def test_xtalk_selftest():
    assert _selftest() == 0


def test_service_declares_xtalk_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/xtalk"' in src
    assert "POST /api/v1/xtalk" in src
    assert "GET never mkdir" in src
    assert "cosmos_xtalk" in src
    assert "NOT_COMPOSED" in src
    assert "overwrite POST /api/v1/orc" in src


def _http(svc, method, path, obj=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{svc.port}{path}",
        data=(json.dumps(obj).encode("utf-8") if obj is not None else None),
        method=method,
    )
    req.add_header("Authorization", "Bearer " + svc.token)
    if obj is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def test_http_unmeasured_then_b_then_a_hole():
    td = Path(tempfile.mkdtemp(prefix="xtalk_http_"))
    root = install(td / "live", tree_id="xtalk-http")
    k = Kernel(root, worker="core")
    stream = k.paths.role("state") / "xtalk.jsonl"
    assert not stream.is_file()
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        st, rec = _http(svc, "GET", "/api/v1/xtalk")
        assert st == 200
        assert rec["kind"] == "UNMEASURED"
        assert not stream.is_file()
        st, rec = _http(svc, "POST", "/api/v1/xtalk",
                        {"from": "captain", "to": "orc", "body": "hi"})
        assert st == 400
        assert rec["error"] == "BAD_ROLE"
        roles = k.paths.role("state") / "roles.json"
        roles.write_text(json.dumps({
            "orc": {"harness": "grok", "owner": "leader", "alive": True},
        }), encoding="utf-8")
        st, rec = _http(svc, "POST", "/api/v1/xtalk",
                        {"from": "captain", "to": "orc", "body": "hello", "nonce": "n1"})
        assert st == 200
        assert rec["kind"] == "ACCEPTED"
        assert rec["transport"] == "B"
        st, rec = _http(svc, "POST", "/api/v1/xtalk",
                        {"from": "captain", "to": "orc", "body": "hello", "nonce": "n1"})
        assert st == 200
        assert rec.get("duplicate") is True
        st, rec = _http(svc, "GET", "/api/v1/xtalk?role=orc")
        assert st == 200
        assert rec["kind"] == "MEASURED"
        assert rec["n"] == 1
        assert rec["inbox"][0]["msg"]["to"] == "orc"
        assert rec.get("roles", {}).get("orc", {}).get("transport") == "B"
        assert "session" not in (rec.get("roles") or {}).get("orc", {})
        assert rec.get("seq") == 1
        assert str(rec.get("head") or "").startswith("sha256:")
        roles.write_text(json.dumps({
            "orc": {"harness": "grok", "owner": "leader", "alive": True},
            "crew": {"harness": "opencode", "owner": "server", "alive": True},
        }), encoding="utf-8")
        st, rec = _http(svc, "POST", "/api/v1/xtalk",
                        {"from": "captain", "to": "crew", "body": "hi"})
        assert st == 200
        assert rec["kind"] == "DRY_RUN"
        assert rec["transport"] == "A"
        assert rec.get("inject") is False
        st, rec = _http(svc, "POST", "/api/v1/xtalk",
                        {"from": "captain", "to": "crew", "body": "hi", "inject": True})
        assert st == 501
        assert rec["error"] == "NOT_COMPOSED"
        # standalone page (no bearer on loopback)
        req = urllib.request.Request(f"http://127.0.0.1:{svc.port}/xtalk/")
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")
            assert resp.status == 200
            assert "initXTalkStandalone" in html
            assert "xtalk.js" in html
    finally:
        svc.shutdown()


def test_three_surfaces_exist():
    ui = ROOT / "builds" / "cdeck" / "ui"
    assert (ROOT / "builds" / "xtalk" / "index.html").is_file()
    assert (ROOT / "builds" / "xtalk" / "xtalk.js").is_file()
    assert (ui / "deck_xtalk.js").is_file()
    more = (ui / "deck_more.html").read_text(encoding="utf-8")
    tabs = (ui / "deck_tabs.js").read_text(encoding="utf-8")
    head = (ui / "header.js").read_text(encoding="utf-8")
    svc = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'id="panel-xtalk"' in more
    assert 'id: "xtalk"' in tabs
    assert "initDeckXtalk" in head
    assert "deck_xtalk.js" in svc
    assert "_XTALK_ROUTES" in svc
    plug = ROOT / "builds" / "xtalk-plugin"
    assert (plug / "src" / "tools.ts").is_file()
    assert (plug / ".opencode" / "plugins" / "cosmos_xtalk.ts").is_file()
    js = (ui / "deck_xtalk.js").read_text(encoding="utf-8")
    assert "GET /api/v1/xtalk" in js
    assert "createElement(\"iframe\")" not in js
    assert "no iframe" in js.lower() or "No iframe" in js


if __name__ == "__main__":
    raise SystemExit(_selftest())
