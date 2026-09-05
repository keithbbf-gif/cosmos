#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P3 CVM additive routes parser (docs/CVM_ARCH.md sec 8.2, 8.3, 10).

Asserts GET /api/v1/cvm/pull and POST /api/v1/cvm/snapshot are registered
additively (parsed.path for the query; no self.path == pull), helpers exist,
no ledger append, no existing-handler rewrite, kinds validate fail-closed.
rc=0 here is not the live gate - see CVM P3 runtime-binding (projection_mtime).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

SERVICE = ROOT / "cosmos" / "cosmos_service.py"
PROJECTION = ROOT / "cosmos" / "cosmos_cvm_projection.py"

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _cvm_section(src: str) -> str:
    """Helper block lives on cosmos_cvm_projection (PHASE 4 seam)."""
    start = src.find("# ---------------- CVM projection")
    if start < 0:
        raise AssertionError("CVM helper block missing")
    return src[start:]


def main() -> int:
    src = SERVICE.read_text(encoding="utf-8")
    proj = PROJECTION.read_text(encoding="utf-8")
    section = _cvm_section(proj)

    check("service file on disk", lambda: SERVICE.is_file())
    check("projection module on disk (PHASE 4 seam)",
          lambda: PROJECTION.is_file())
    check("GET /api/v1/cvm/pull registered",
          lambda: "/api/v1/cvm/pull" in src)
    check("POST /api/v1/cvm/snapshot registered",
          lambda: "/api/v1/cvm/snapshot" in src)
    check("GET pull matches parsed.path (query-safe, like /control)",
          lambda: 'parsed.path == "/api/v1/cvm/pull"' in src)
    check("GET pull does NOT use self.path == (would drop ?client_id=)",
          lambda: 'self.path == "/api/v1/cvm/pull"' not in src)
    # Assert the PROPERTY (query-safe routing), not a spelling. The handler was
    # refactored to route snapshot+push through one urlparse-derived variable via
    # tuple membership -- equivalent and better -- and a literal `.path == "..."`
    # match called that a failure. A test that pins spelling breaks on every valid
    # refactor; this one pins behaviour. (2026-08-30)
    _pv = None
    for _line in src.splitlines():
        if "urlparse(self.path).path" in _line and "=" in _line:
            _pv = _line.split("=")[0].strip()
            break
    check("POST snapshot is routed from a parsed path (query-safe)",
          lambda: bool(_pv) and any(
              _pv in L and "/api/v1/cvm/snapshot" in L
              for L in src.splitlines()))
    check("POST snapshot does NOT use raw self.path (would drop ?query)",
          lambda: 'self.path == "/api/v1/cvm/snapshot"' not in src)

    # existing handlers still present and still keyed the same way
    check("existing GET /status handler unmodified (self.path ==)",
          lambda: 'if self.path == "/api/v1/status":' in src)
    check("existing GET /control handler unmodified (parsed.path)",
          lambda: 'if parsed.path == "/api/v1/control":' in src)
    check("existing POST /voice handler unmodified",
          lambda: 'if self.path == "/api/v1/voice":' in src)
    check("existing POST /control/resume unmodified",
          lambda: 'if self.path == "/api/v1/control/resume":' in src)

    check("resolver role state/cvm (no path literals, no new role)",
          lambda: 'kernel.paths.state("cvm", "pull.json")' in proj
          and 'kernel.paths.state("cvm", "phone.json")' in proj)
    check("CVM helpers never ledger.append",
          lambda: "ledger.append" not in section)
    check("no CVM_SNAPSHOT event name (projection-only this slice)",
          lambda: "CVM_SNAPSHOT" not in src and "CVM_SNAPSHOT" not in proj)
    check("GET does not rewrite pull.json",
          lambda: "atomic_json" not in proj.split(
              "def _cvm_pull_response")[1].split("def _cvm_store_snapshot")[0])
    check("snapshot write reuses cosmos_clock.atomic_json",
          lambda: "from cosmos_clock import atomic_json" in section)
    check("does not import the CVM clock satellite",
          lambda: "cosmos_cvm_clock" not in src
          and "cosmos_cvm_clock" not in proj)
    check("service re-exports projection helpers (same objects)",
          lambda: "from cosmos_cvm_projection import" in src
          and "def _cvm_pull_response" not in src)

    import cosmos_service as cs

    check("known kinds include device+notifications (P3 mule)",
          lambda: {"device", "notifications"} <= cs._CVM_KNOWN_KINDS)

    def _ok_device():
        return cs._cvm_filter_kinds({
            "device": {"battery_pct": 80, "net": "tailscale",
                       "audio_route": "none"},
            "notifications": {"status": "ok", "items": []},
            "future_kind": {"status": "ok"},
        }) == {
            "device": {"battery_pct": 80, "net": "tailscale",
                       "audio_route": "none"},
            "notifications": {"status": "ok", "items": []},
        }

    check("filter keeps device+notifications, drops unknown kind", _ok_device)

    def _perm():
        out = cs._cvm_filter_kinds({"sms": {"status": "PERM_DENIED:sms"}})
        return out == {"sms": {"status": "PERM_DENIED:sms"}}

    check("PERM_DENIED:<kind> is stored, not emptied", _perm)

    def _bad_empty():
        try:
            cs._cvm_filter_kinds({"device": {}})
        except cs.CvmError as e:
            return e.kind == "BAD_SNAPSHOT"
        return False

    check("empty declared kind -> BAD_SNAPSHOT", _bad_empty)

    def _bad_kinds():
        try:
            cs._cvm_filter_kinds(None)
        except cs.CvmError as e:
            return e.kind == "BAD_SNAPSHOT"
        return False

    check("missing kinds object -> BAD_SNAPSHOT", _bad_kinds)

    def _pcm_inline():
        try:
            cs._cvm_filter_kinds({"pcm": {"status": "ok", "bytes": "AAAA"}})
        except cs.CvmError as e:
            return e.kind == "BAD_SNAPSHOT"
        return False

    check("inline pcm bytes -> BAD_SNAPSHOT (pointer only)", _pcm_inline)

    def _pcm_ptr():
        out = cs._cvm_filter_kinds(
            {"pcm": {"status": "ok", "sha256": "abc", "n_bytes": 0}})
        return list(out) == ["pcm"] and cs._cvm_blob_ptrs(out) == ["abc"]

    check("pcm sha256 pointer is accepted", _pcm_ptr)

    # GET 404 and POST 404 still the fallthrough after the new branches
    gets = [m.start() for m in re.finditer(
        r'return self\._send\(404, \{"error": "NOT_FOUND"', src)]
    pull_at = src.find('parsed.path == "/api/v1/cvm/pull"')
    snap_at = src.find('"/api/v1/cvm/snapshot"')
    check("GET pull sits before GET 404",
          lambda: pull_at > 0 and any(pull_at < g for g in gets))
    check("POST snapshot sits before POST 404",
          lambda: snap_at > 0 and any(snap_at < g for g in gets))

    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + f"  {sum(1 for _, p, _ in RESULTS if p)}/{len(RESULTS)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
