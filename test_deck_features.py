#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gitur tab feature probes — static pins + Core GET /api/v1/gitur fixture.

Run:  py -3.14 test_deck_features.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_gitur import snapshot  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402

UI = ROOT / "builds" / "cdeck" / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _fake_gitur_run(argv):
    cmd = " ".join(str(x) for x in argv)
    if "rate_limit" in cmd:
        return 0, json.dumps({"resources": {"core": {"limit": 5000, "remaining": 4999}}}), ""
    if "pr list" in cmd:
        return 0, json.dumps([{"number": 7, "title": "draft", "isDraft": True,
                               "url": "https://github.com/keithbbf-gif/cosmos/pull/7",
                               "headRefName": "ccr/x", "updatedAt": "2026-09-01"}]), ""
    if "run list" in cmd:
        return 0, json.dumps([]), ""
    if "glab" in cmd and "user" in cmd:
        return 0, json.dumps({"id": 1, "username": "keithbbf-gif"}), ""
    if "mr list" in cmd:
        return 0, json.dumps([]), ""
    return 127, "", "NO_CLI"


def _fake_cursor_http(method, path, _body):
    if method == "GET" and path == "/v1/me":
        return 200, {}, {"apiKeyName": "Cursor COSMOS 2"}
    return 503, {}, {"error": "UNREACHABLE"}


class _Reg:
    def matrix(self):
        return [
            {"link_id": "cursor-api", "verified": True, "age_s": 1, "route": "core->code",
             "rail_type": "API"},
            {"link_id": "github-forge", "verified": False, "age_s": 99, "route": "core->forge",
             "rail_type": "CLI"},
        ]


def _gitur_fixture():
    td = Path(tempfile.mkdtemp(prefix="gitur_feat_"))
    root = install(td / "live", tree_id="gitur-feat")
    kernel = SimpleNamespace(
        paths=__import__("cosmos_paths").CosmosPaths(root),
        registry=_Reg(),
        gitur_run=_fake_gitur_run,
        gitur_http=_fake_cursor_http,
    )
    return snapshot(kernel)


def _static_gitur_js() -> str:
    p = UI / "deck_gitur.js"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def main() -> int:
    js = _static_gitur_js()

    check("FEAT-GITUR-01: bind entry cdeckBindGiturTab", lambda: "cdeckBindGiturTab" in js)
    check("FEAT-GITUR-02: panel-gitur mount id", lambda: "panel-gitur" in js)
    check("FEAT-GITUR-03: refreshGitur exported", lambda: "refreshGitur" in js)
    check("FEAT-GITUR-04: filter input gitur-filter", lambda: "gitur-filter" in js)
    check("FEAT-GITUR-05: no Math.random scores", lambda: "Math.random" not in js)

    rec = _gitur_fixture()
    check("FEAT-GITUR-06: Core schema cosmos-gitur/1", lambda: rec.get("schema") == "cosmos-gitur/1")
    check(
        "FEAT-GITUR-07: triad legs present",
        lambda: {L["id"] for L in rec.get("legs") or []}
        >= {"github-forge", "gitlab-forge", "cursor-api"},
    )
    check(
        "FEAT-GITUR-08: note refuses invented PR lists",
        lambda: "invent" in (rec.get("note") or "").lower(),
    )
    check(
        "FEAT-GITUR-09: github live prs is a list from CLI fold",
        lambda: isinstance((rec.get("panes") or {}).get("github", {}).get("live", {}).get("prs"), list),
    )

    td = Path(tempfile.mkdtemp(prefix="gitur_http_"))
    root = install(td / "live", tree_id="gitur-http")
    k = Kernel(root, worker="core")
    k.registry = _Reg()  # type: ignore[attr-defined]
    k.gitur_run = _fake_gitur_run  # type: ignore[attr-defined]
    k.gitur_http = _fake_cursor_http  # type: ignore[attr-defined]
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    base = f"http://127.0.0.1:{svc.port}"

    def get(path):
        req = urllib.request.Request(base + path)
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    try:
        code, body = get("/api/v1/gitur")
        check(
            "FEAT-GITUR-10: GET /api/v1/gitur 200 on loopback fixture",
            lambda: code == 200 and body.get("schema") == "cosmos-gitur/1",
        )
        check(
            "FEAT-GITUR-11: jobs_kind is string (jukebox or measured error)",
            lambda: isinstance(body.get("jobs_kind"), str) and body.get("jobs_kind") != "",
        )
        code_js, _h, raw = 0, {}, b""
        import http.client
        c = http.client.HTTPConnection("127.0.0.1", svc.port, timeout=12)
        try:
            c.request("GET", "/cdeck/deck_gitur.js")
            r = c.getresponse()
            code_js = r.status
            raw = r.read()
        finally:
            c.close()
        disk = (UI / "deck_gitur.js").read_bytes()
        check(
            "FEAT-GITUR-12: Core serves deck_gitur.js bytes",
            lambda: code_js == 200 and raw == disk,
        )
    finally:
        svc.shutdown()

    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print(
        "SELFTEST %s %d/%d"
        % ("PASS" if not bad else "FAIL", len(RESULTS) - len(bad), len(RESULTS))
    )
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
