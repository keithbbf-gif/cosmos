#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_cvm_projection -- PHASE 4 CVM-projection seam.

Moved out of cosmos_service.py with the module (docs/CORE_RESTRUCTURE.md):
a split does not land without its tests moving with it. cosmos_service
re-exports the SAME objects, not copies, so cosmos_cvm_push.py and
tests/test_cvm_push.py (`CvmError`, `_cvm_pull_response`,
`_cvm_store_snapshot`) keep working unchanged.

F-29 lesson: a location/shape change that keeps boot green can still break
CALLERS. This suite pins:
  * cosmos_service re-exports the SAME objects
  * cosmos_service.py no longer defines the moved helpers
  * cosmos_cvm_push still imports from cosmos_service (same CvmError)
  * HTTP GET /api/v1/cvm/pull and POST /api/v1/cvm/snapshot still answer
    (boot-green is not route-green)

Bite: cosmos/_fail_f39_cvm_against_old.py against
_delme/predispose_service_f39_cvm_*/ (all_new_pins_failed).

    py -3.14 tests/test_cvm_projection.py
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from http.client import HTTPConnection
from pathlib import Path


def _imports_module(src: str, name: str) -> bool:
    """True iff `src` has an import of `name` (docstring mentions do not count)."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] == name for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] == name:
                return True
    return False

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

import cosmos_service  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import (  # noqa: E402
    CvmError, Service, _cvm_filter_kinds, _cvm_pull_response,
    _cvm_store_snapshot,
)

RESULTS = []

REEXPORTED = (
    "CvmError",
    "_CVM_KNOWN_KINDS",
    "_CVM_PCM_INLINE",
    "_cvm_read_json",
    "_cvm_stat",
    "_cvm_status_prewarm",
    "_cvm_filter_kinds",
    "_cvm_blob_ptrs",
    "_cvm_pull_response",
    "_cvm_store_snapshot",
)

TREE_ID = "KMesh-COSMOS-live"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _raw(port, method, path, token=None, body=None):
    c = HTTPConnection("127.0.0.1", port, timeout=15)
    try:
        hdrs = {}
        if token:
            hdrs["Authorization"] = "Bearer " + token
        payload = None
        if body is not None:
            payload = json.dumps(body).encode("utf-8")
            hdrs["Content-Type"] = "application/json"
        c.request(method, path, body=payload, headers=hdrs)
        r = c.getresponse()
        raw = r.read()
        try:
            obj = json.loads(raw.decode("utf-8"))
        except ValueError:
            obj = {"_raw": raw.decode("utf-8", "replace")[:400]}
        return r.status, obj
    finally:
        c.close()


def _seam_rows() -> None:
    svc_src = (REPO / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    proj_path = REPO / "cosmos" / "cosmos_cvm_projection.py"
    proj_src = proj_path.read_text(encoding="utf-8") if proj_path.is_file() else ""
    push_src = (REPO / "cosmos" / "cosmos_cvm_push.py").read_text(encoding="utf-8")
    p3_src = (HERE / "test_cvm_p3.py").read_text(encoding="utf-8")
    push_test = (HERE / "test_cvm_push.py").read_text(encoding="utf-8")

    check("projection module exists on disk",
          lambda: proj_path.is_file() and len(proj_src) > 200)
    try:
        import cosmos_cvm_projection as proj
    except Exception as e:  # noqa: BLE001
        RESULTS.append(("import cosmos_cvm_projection", False,
                        f"{type(e).__name__}: {e}"))
        proj = None
    else:
        RESULTS.append(("import cosmos_cvm_projection", True, ""))

    if proj is not None:
        for name in REEXPORTED:
            check(
                f"cosmos_service still exports {name} (same object)",
                (lambda n=name: getattr(cosmos_service, n)
                 is getattr(proj, n)),
            )
        check("projection defines CvmError",
              lambda: "class CvmError" in proj_src)
        check("projection defines _cvm_pull_response",
              lambda: "def _cvm_pull_response" in proj_src)
        check("projection defines _cvm_store_snapshot",
              lambda: "def _cvm_store_snapshot" in proj_src)
        check("projection never ledger.append",
              lambda: "ledger.append" not in proj_src)
        check("projection does not import the CVM clock satellite",
              lambda: "cosmos_cvm_clock" not in proj_src)
        check("projection does not import cosmos_service (no cycle)",
              lambda: not _imports_module(proj_src, "cosmos_service"))
        check("CvmError imported from cosmos_service is the projection class",
              lambda: CvmError is proj.CvmError)

    check("service source no longer defines CvmError",
          lambda: "class CvmError" not in svc_src)
    check("service source no longer defines _cvm_pull_response",
          lambda: "def _cvm_pull_response" not in svc_src)
    check("service source no longer defines _cvm_store_snapshot",
          lambda: "def _cvm_store_snapshot" not in svc_src)
    check("service source no longer defines _cvm_filter_kinds",
          lambda: "def _cvm_filter_kinds" not in svc_src)
    check("service re-exports via cosmos_cvm_projection import",
          lambda: "from cosmos_cvm_projection import" in svc_src)
    check("service still owns make_handler (HTTP not moved)",
          lambda: "def make_handler" in svc_src)
    check("GET /api/v1/cvm/pull still registered on the service",
          lambda: 'parsed.path == "/api/v1/cvm/pull"' in svc_src)
    check("POST snapshot still query-safe on the service",
          lambda: '"/api/v1/cvm/snapshot"' in svc_src
          and 'self.path == "/api/v1/cvm/snapshot"' not in svc_src)
    check("POST push still query-safe on the service",
          lambda: '"/api/v1/cvm/push"' in svc_src)

    # F-29 caller pins: the exact import lines other modules use.
    check("cosmos_cvm_push still imports CvmError from cosmos_service",
          lambda: "from cosmos_service import" in push_src
          and "CvmError" in push_src
          and "_cvm_pull_response" in push_src
          and "_cvm_store_snapshot" in push_src)
    check("test_cvm_push still imports helpers from cosmos_service",
          lambda: "from cosmos_service import" in push_test
          and "_cvm_pull_response" in push_test)
    check("test_cvm_p3 still binds cosmos_service as cs",
          lambda: "import cosmos_service as cs" in p3_src)

    check("known kinds still include device+notifications via re-export",
          lambda: {"device", "notifications"} <= cosmos_service._CVM_KNOWN_KINDS)

    def _filter_same():
        kinds = {
            "device": {"battery_pct": 80, "net": "tailscale",
                       "audio_route": "none"},
            "future_kind": {"status": "ok"},
        }
        out = _cvm_filter_kinds(kinds)
        return list(out) == ["device"] and "future_kind" not in out

    check("filter keeps device, drops unknown kind (re-export)", _filter_same)

    def _pcm_inline():
        try:
            _cvm_filter_kinds({"pcm": {"status": "ok", "bytes": "AAAA"}})
        except CvmError as e:
            return e.kind == "BAD_SNAPSHOT"
        return False

    check("inline pcm bytes still BAD_SNAPSHOT via re-export", _pcm_inline)


def _caller_http() -> None:
    """The HTTP caller, not just the helper. F-29 shape pin."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_cvm_proj_seam_"))
    install(td, tree_id=TREE_ID)
    k = Kernel(td, worker="f39-cvm-proj")
    k.paths.config("api_token.txt").write_text("proj-token\n", encoding="utf-8")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        token = "proj-token"
        code, body = _raw(svc.port, "GET", "/api/v1/cvm/pull?client_id=phone-a",
                          token=token)
        check("GET /cvm/pull with client_id is HTTP 200 (no ticket => pull false)",
              lambda: code == 200 and body.get("pull") is False
              and body.get("tree_id") == TREE_ID
              and body.get("client_id") == "phone-a")
        check("GET /cvm/pull did not rewrite pull.json",
              lambda: not k.paths.state("cvm", "pull.json").is_file())

        miss, miss_body = _raw(svc.port, "GET", "/api/v1/cvm/pull", token=token)
        check("GET /cvm/pull without client_id is 400 CLIENT_ID_REQUIRED",
              lambda: miss == 400
              and miss_body.get("error") == "CLIENT_ID_REQUIRED")

        unauth, unauth_body = _raw(
            svc.port, "GET", "/api/v1/cvm/pull?client_id=phone-a")
        check("GET /cvm/pull without bearer is 200 on loopback (DT auto-connect)",
              lambda: unauth == 200 and unauth_body.get("client_id") == "phone-a")

        snap = {
            "cvm": 1,
            "client_id": "phone-a",
            "request_id": "f39-snap-1",
            "kinds": {"device": {"status": "ok", "audio_route": "none"}},
        }
        scode, sbody = _raw(svc.port, "POST", "/api/v1/cvm/snapshot",
                            token=token, body=snap)
        check("POST /cvm/snapshot is HTTP 200 and stores device",
              lambda: scode == 200 and sbody.get("cursor_out")
              and "device" in (sbody.get("stored") or []))
        phone = json.loads(
            k.paths.state("cvm", "phone.json").read_text(encoding="utf-8"))
        check("snapshot landed state/cvm/phone.json (projection, not ledger)",
              lambda: phone.get("request_id") == "f39-snap-1"
              and phone.get("tree_id") == TREE_ID
              and "device" in (phone.get("kinds") or {}))
        check("snapshot did not append a CVM_SNAPSHOT ledger event",
              lambda: k.ledger.last()["event"] != "CVM_SNAPSHOT")

        replay_code, replay = _raw(svc.port, "POST", "/api/v1/cvm/snapshot",
                                   token=token, body=snap)
        check("snapshot is idempotent on request_id",
              lambda: replay_code == 200 and replay.get("idempotent") is True
              and replay.get("cursor_out") == sbody.get("cursor_out"))

        # The helper itself, called the way cosmos_cvm_push calls it.
        pulled = _cvm_pull_response(k, "phone-a")
        check("cosmos_cvm_push import line still resolves (_cvm_pull_response)",
              lambda: pulled.get("pull") is False
              and pulled.get("client_id") == "phone-a")
        rec = _cvm_store_snapshot(k, snap)
        check("cosmos_cvm_push import line still resolves (_cvm_store_snapshot)",
              lambda: rec.get("idempotent") is True)
    finally:
        svc.shutdown()


def main() -> int:
    _seam_rows()
    _caller_http()
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    svc_path = REPO / "cosmos" / "cosmos_service.py"
    proj_path = REPO / "cosmos" / "cosmos_cvm_projection.py"
    print("live_value: " + json.dumps({
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "reexported": len(REEXPORTED),
        "cvmerror_same": (
            hasattr(cosmos_service, "CvmError")
            and "cosmos_cvm_projection" in sys.modules
            and cosmos_service.CvmError
            is sys.modules["cosmos_cvm_projection"].CvmError
        ) if "cosmos_cvm_projection" in sys.modules else False,
        "svc_lines": svc_path.read_text(encoding="utf-8").count("\n") + 1,
        "proj_lines": (
            proj_path.read_text(encoding="utf-8").count("\n") + 1
            if proj_path.is_file() else 0),
        "proj_exists": proj_path.is_file(),
        "tree_id": TREE_ID,
    }, sort_keys=True))
    print(("PASS" if not bad else "FAIL")
          + f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
