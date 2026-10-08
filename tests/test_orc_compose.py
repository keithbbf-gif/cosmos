#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compose orch routes that already have modules. Temp root only.

    py -3.14 -m pytest -q -p no:cacheprovider --basetemp C:\\Users\\Papa\\AppData\\Local\\Temp\\c4-orc tests\\test_orc_compose.py
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_approval import ApprovalGate  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402

BASE = Path(r"C:\Users\Papa\AppData\Local\Temp\c4-orc")
LIVE = Path(r"V:\A\Ai\COSMOS\live")
APPROVER = "captain:c4orc"
PUSH = {"kind": "git", "command": "git push origin ccr/seat-mcp"}


def _dirs(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_dir()}


def _http(port: int, method: str, path: str, body=None, token: str | None = None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        "http://127.0.0.1:%d%s" % (port, path),
        data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw.decode("utf-8"))


def _no_secret(rec: dict, token: str) -> None:
    blob = json.dumps(rec)
    assert token not in blob


def test_orc_compose():
    BASE.mkdir(parents=True, exist_ok=True)
    run = BASE / ("orc-" + uuid.uuid4().hex[:12])
    root = install(run / "root", tree_id="c4-orc-compose")
    assert root.resolve().is_relative_to(BASE.resolve())
    assert not str(root.resolve()).lower().startswith(str(LIVE.resolve()).lower())

    kernel = Kernel(root, worker="core")
    svc = Service(kernel, host="127.0.0.1", port=0)
    svc.serve_background()
    token = svc.token
    try:
        port = svc.port
        before = _dirs(root)

        code, rec = _http(port, "GET", "/api/v1/status")
        assert code == 200 and rec.get("ready") is True
        assert rec.get("tree_id") == "c4-orc-compose"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/spend")
        assert code == 200 and rec.get("error") != "NOT_FOUND"
        _no_secret(rec, token)

        code, rec = _http(
            port, "GET", "/api/v1/recall?q=hello&principal=captain:c4orc")
        assert code == 200
        assert rec.get("schema") == "cosmos-recall/1"
        assert rec.get("kind") == "UNMEASURED"
        assert rec.get("results") is None
        assert rec.get("error") != "RECALL_NOT_COMPOSED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/skills")
        assert code == 200
        assert rec.get("schema") == "cosmos-skills/1"
        assert rec.get("kind") == "MEASURED"
        assert rec.get("skills") == []
        assert rec.get("error") != "SKILLS_NOT_COMPOSED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/sandbox")
        assert code == 200
        assert rec.get("schema") == "cosmos-sandbox/1"
        assert rec.get("kind") == "MEASURED"
        assert rec.get("modal") == "NOT_COMPOSED"
        assert "modal" in (rec.get("named_not_composed") or [])
        assert rec.get("error") != "SANDBOX_NOT_COMPOSED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/delegate")
        assert code == 200
        assert rec.get("schema") == "cosmos-delegate/1"
        assert "policy" in rec and "children" in rec
        assert rec.get("children") == []
        assert rec.get("error") != "DELEGATE_NOT_COMPOSED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/approvals/pending")
        assert code == 200
        assert rec.get("schema") == "cosmos-approval/1"
        assert rec.get("pending") == []
        assert rec.get("error") != "APPROVALS_NOT_COMPOSED"
        _no_secret(rec, token)

        assert not (root / "state" / "recall").exists()
        assert not (root / "state" / "skills").exists()
        assert not (root / "config" / "sandbox_backend.json").exists()
        assert _dirs(root) == before

        code, rec = _http(port, "GET", "/api/v1/chamber?room=Cm")
        assert code == 200
        assert rec.get("schema") == "cosmos-chamber/1"
        assert rec.get("room") == "Cm"
        assert rec.get("kind") == "UNMEASURED"
        assert rec.get("presence") == {}
        assert rec.get("posts") == []
        assert rec.get("tickets") == []
        assert rec.get("error") != "CHAMBER_NOT_COMPOSED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/chamber")
        assert code == 200 and rec.get("room") == "Cm"
        assert rec.get("kind") == "UNMEASURED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/chamber?room=plumbing")
        assert code == 200 and rec.get("room") == "plumbing"
        assert rec.get("kind") == "UNMEASURED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/chamber?room=legal")
        assert code == 400 and code != 200
        assert rec.get("error") == "STREAM_REFUSED"
        assert rec.get("kind") == "STREAM_REFUSED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/temporal")
        assert code == 200
        assert rec.get("schema") == "cosmos-temporal-fold/1"
        assert rec.get("kind") == "UNMEASURED"
        assert rec.get("live") == []
        assert rec.get("invalidated") == []
        assert isinstance(rec.get("at"), (int, float))
        assert rec.get("error") != "TEMPORAL_NOT_COMPOSED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/temporal?at=1500")
        assert code == 200 and rec.get("at") == 1500.0
        assert rec.get("kind") == "UNMEASURED"
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/temporal?at=nope")
        assert code == 400 and code != 200
        assert rec.get("error") == "BAD_AT"
        _no_secret(rec, token)

        # join / assert_fact / invalidate append. POST stays the 501 table.
        for path, err in (
            ("/api/v1/chamber", "CHAMBER_NOT_COMPOSED"),
            ("/api/v1/temporal", "TEMPORAL_NOT_COMPOSED"),
        ):
            code, rec = _http(port, "POST", path, token=token)
            assert code == 501, path
            assert rec.get("kind") == "UNMEASURED"
            assert rec.get("error") == err
            _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/seats?stream=Cm")
        assert code == 501
        assert rec.get("kind") == "UNMEASURED"
        assert rec.get("error") == "SEATS_NOT_COMPOSED"
        _no_secret(rec, token)
        assert _dirs(root) == before

        absent = {"request_id": "ap-not-pending", "approver": APPROVER}
        for path in ("/api/v1/approvals/grant", "/api/v1/approvals/deny"):
            code, rec = _http(port, "POST", path, absent)
            assert code == 401 and code != 200
            assert rec.get("ok") is False
            assert rec.get("kind") == "NO_BEARER"
            _no_secret(rec, token)
            code, rec = _http(port, "POST", path, absent, token=token)
            assert code == 403 and code != 200
            assert rec.get("ok") is False
            assert rec.get("error") == "NO_REQUEST"
            _no_secret(rec, token)

        gate = ApprovalGate(kernel.ledger, clock=kernel._clock)
        made = gate.request("worker:c4orc", PUSH)
        rid = made["request_id"]
        assert rid and rid in {row["request_id"] for row in gate.pending()}

        code, rec = _http(port, "GET", "/api/v1/approvals/pending")
        assert code == 200
        assert rid in {row["request_id"] for row in rec.get("pending") or []}

        code, rec = _http(
            port, "POST", "/api/v1/approvals/grant",
            {"request_id": rid, "approver": APPROVER}, token=token)
        assert code == 200
        assert rec.get("ok") is True and rec.get("granted") is True
        assert rec.get("request_id") == rid
        assert isinstance(rec.get("nonce"), str) and rec["nonce"]
        _no_secret(rec, token)

        code, rec = _http(port, "GET", "/api/v1/approvals/pending")
        assert rid not in {row["request_id"] for row in rec.get("pending") or []}
        assert "ap-not-pending" not in {
            row["request_id"] for row in rec.get("pending") or []}

        made2 = gate.request("worker:c4orc", PUSH)
        rid2 = made2["request_id"]
        assert rid2 in {row["request_id"] for row in gate.pending()}
        code, rec = _http(
            port, "POST", "/api/v1/approvals/deny",
            {"request_id": rid2, "approver": APPROVER, "reason": "no"},
            token=token)
        assert code == 200 and rec.get("denied") is True
        _no_secret(rec, token)
        code, rec = _http(
            port, "POST", "/api/v1/approvals/grant",
            {"request_id": rid2, "approver": APPROVER}, token=token)
        assert code == 403 and code != 200
        assert rec.get("error") == "ALREADY_DECIDED"
        assert "DENIED" in (rec.get("detail") or "")
        assert _dirs(root) == before
    finally:
        svc.shutdown()
