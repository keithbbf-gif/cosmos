#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: a REMOTE (non-loopback) bind refuses --no-auth. Typed refusal, no flag past it.

Earned 2026-08-31 by measurement, not by review. The trial Core on :8791 was serving
0.0.0.0 with `--no-auth --insecure-http`; from a LAN address, with NO credentials, it
returned all 2,349 of its ledger records (208 conversation turns) and accepted a
state-mutating `POST /api/v1/kill` that flipped `mic_off`/`clear_queue`. The prose in
cosmos_service said "the tailnet/LAN is the access control"; the socket said 0.0.0.0.
See docs/CORE_SERVE_SUPERVISOR.md.

The regression proof is not "the new code passes" - it is that assertions 1-4 FAIL
against the staged pre-fix module in _delme/predispose_cosmos_service_*/ and pass
against the tree. This file runs BOTH and says so.

Run: py -3.14 cosmos\test_remote_bind_gate.py
"""
from __future__ import annotations
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cosmos_kernel import Kernel, install                          # noqa: E402
import cosmos_service                                              # noqa: E402

REMOTE_HOSTS = ("0.0.0.0", "192.168.1.107", "::")
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> bool:
    try:
        ok = bool(fn())
        RESULTS.append((label, ok, ""))
        return ok
    except Exception as e:                                          # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))
        return False


def _fresh_kernel(tag: str) -> Kernel:
    root = Path(tempfile.mkdtemp(prefix=f"cosmos_bindgate_{tag}_")) / "Cosmos"
    install(root, tree_id="bindgate")
    k = Kernel(root, worker="core")
    # A remote bind with auth ENABLED needs install-config bearer material present;
    # this is throwaway test material in a temp dir, never read back or printed.
    k.paths.config("api_token.txt").write_text("bindgate-test-bearer",
                                               encoding="utf-8")
    return k


def _raises_kind(mod, kind: str, **kw) -> bool:
    """Construct a Service expecting a typed refusal. Any Service that DOES get
    built is closed immediately - never left holding a socket."""
    svc = None
    try:
        svc = mod.Service(**kw)
        return False
    except mod.ServiceError as e:
        return e.kind == kind
    finally:
        if svc is not None:
            svc.httpd.server_close()


def _builds(mod, **kw) -> bool:
    svc = None
    try:
        svc = mod.Service(**kw)
        return True
    finally:
        if svc is not None:
            svc.httpd.server_close()


def run_suite(mod, label: str) -> list[tuple[str, bool, str]]:
    """The four gate assertions + two no-over-removal assertions, against `mod`."""
    out: list[tuple[str, bool, str]] = []

    def sub(name, fn):
        try:
            out.append((f"{label}: {name}", bool(fn()), ""))
        except Exception as e:                                       # noqa: BLE001
            out.append((f"{label}: {name}", False, f"{type(e).__name__}: {e}"))

    # 1-3. every non-loopback host shape refuses --no-auth, whatever else is set.
    for host in REMOTE_HOSTS:
        sub(f"REMOTE_OPEN_ACCESS on host={host!r}",
            lambda h=host: _raises_kind(mod, "REMOTE_OPEN_ACCESS",
                                        kernel=_fresh_kernel("a"), host=h, port=0,
                                        open_access=True, insecure_http=True))
    # 4. TLS does not buy the door open: encryption is not authentication.
    sub("REMOTE_OPEN_ACCESS is absolute (tls=True does not open it)",
        lambda: _raises_kind(mod, "REMOTE_OPEN_ACCESS",
                             kernel=_fresh_kernel("b"), host="0.0.0.0", port=0,
                             open_access=True, tls=True))
    # 5. NOT over-removed: the loopback no-auth trial still works (Keith's local mic).
    sub("loopback + open_access still builds (trial preserved)",
        lambda: _builds(mod, kernel=_fresh_kernel("c"), host="127.0.0.1", port=0,
                        open_access=True))
    # 6. NOT over-removed: remote + REAL bearer + --insecure-http still builds.
    sub("remote + bearer + insecure_http still builds (flag preserved)",
        lambda: _builds(mod, kernel=_fresh_kernel("d"), host="0.0.0.0", port=0,
                        open_access=False, insecure_http=True))
    return out


def _load_staged() -> tuple[object, Path] | tuple[None, None]:
    """Newest staged pre-fix cosmos_service.py, imported under its own name."""
    delme = HERE.parent / "_delme"
    cands = sorted(delme.glob("predispose_cosmos_service_*/cosmos_service.py"))
    if not cands:
        return None, None
    p = cands[-1]
    spec = importlib.util.spec_from_file_location("cosmos_service__prefix", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cosmos_service__prefix"] = mod
    spec.loader.exec_module(mod)
    return mod, p


def main() -> int:
    # ---- A. the gate fires before the socket is bound ------------------------
    # Not decoration: a refusal that binds first has already exposed the port for
    # the length of the check, and on a busy port would fail with EADDRINUSE
    # instead of the typed refusal.
    def gate_precedes_bind():
        real = cosmos_service.ThreadingHTTPServer
        bound = []

        def trap(*a, **kw):
            bound.append(a)
            return real(*a, **kw)
        cosmos_service.ThreadingHTTPServer = trap
        try:
            hit = _raises_kind(cosmos_service, "REMOTE_OPEN_ACCESS",
                               kernel=_fresh_kernel("z"), host="0.0.0.0", port=0,
                               open_access=True, insecure_http=True)
        finally:
            cosmos_service.ThreadingHTTPServer = real
        return hit and not bound
    check("refusal precedes the socket bind (no port ever opened)",
          gate_precedes_bind)

    # ---- B. the six assertions against the TREE ------------------------------
    RESULTS.extend(run_suite(cosmos_service, "TREE"))

    # ---- C. the same six against the STAGED PRE-FIX module ------------------
    old, old_path = _load_staged()
    if old is None:
        RESULTS.append(("staged pre-fix module found for regression proof",
                        False, "no _delme/predispose_cosmos_service_*/ copy"))
        old_rows = []
    else:
        old_rows = run_suite(old, "PREFIX")

    # ---- D. the regression proof itself -------------------------------------
    # Assertions 1-4 (the gate) MUST fail against pre-fix code. If they pass there
    # too, this test proves nothing and says so.
    gate_rows = [r for r in old_rows if "REMOTE_OPEN_ACCESS" in r[0]]
    check("regression proof: gate assertions FAIL against pre-fix code",
          lambda: bool(gate_rows) and not any(ok for _, ok, _ in gate_rows))
    keep_rows = [r for r in old_rows if "still builds" in r[0]]
    check("no over-removal: 'still builds' cases pass on BOTH old and new",
          lambda: bool(keep_rows) and all(ok for _, ok, _ in keep_rows))

    print(f"staged pre-fix module: {old_path}")
    print()
    for label, ok, err in RESULTS + old_rows:
        tag = "PASS" if ok else "FAIL"
        expected = " (EXPECTED FAIL - proves the regression)" if (
            not ok and label.startswith("PREFIX: REMOTE_OPEN_ACCESS")) else ""
        print(f"  [{tag}] {label}{expected}{(' :: ' + err) if err else ''}")

    # PREFIX gate rows are expected to fail; they are not scored as failures.
    scored = [r for r in RESULTS + old_rows
              if not r[0].startswith("PREFIX: REMOTE_OPEN_ACCESS")]
    passed = sum(1 for _, ok, _ in scored if ok)
    print(f"\n{passed}/{len(scored)} scored assertions passed "
          f"({len(gate_rows)} pre-fix gate assertions failed AS REQUIRED)")
    return 0 if passed == len(scored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
