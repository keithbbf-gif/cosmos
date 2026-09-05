#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the tests/test_core_supervisor.py failures are a STATE CASCADE from the
intended default flip -- not a functional break in _supervise_serve.

tests/test_core_supervisor.py section 1 calls `poll_once(root)` with no
`supervise=` argument and asserts "OFF is inert -- no state file". With the
default flipped ON that call now legitimately spawns and writes
`logs/core_serve.json` with a future `next_attempt_epoch`. Every later assertion
in that file then fails for a reason that has nothing to do with the code:

  - "direct call without supervise -> DISABLED"  fails on `not state_file.exists()`
  - "port already listening -> ALREADY_UP"       fails on `not state_file.exists()`
  - "port down + enabled -> SPAWNED"             gets BACKOFF (deadline still open)
  - "SPAWNED spawned exactly once" / the 3 argv checks -> CALLS empty -> IndexError

This harness replays the SAME sequence on a CLEAN root (no default-ON poll first)
with the same injected probe/spawn. If every one passes here, the code is intact
and only the old default-OFF contract moved.

    py -3.14 builds\\health\\test_cascade_isolation.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

import cosmos_health_clock as hc                                    # noqa: E402
from cosmos_kernel import install                                   # noqa: E402
from cosmos_paths import CosmosPaths                                # noqa: E402

CALLS: list[dict] = []
PORT_UP = [False]
RESULTS: list[tuple[str, bool, str]] = []


def fake_probe(host, port, timeout_s=0.25):
    return {"ok": PORT_UP[0], "host": host, "port": port, "rtt_s": 0.0,
            "error": None if PORT_UP[0] else "injected: not listening"}


def fake_spawn(argv, cwd, log_path):
    CALLS.append({"argv": list(argv), "cwd": str(cwd), "log": str(log_path)})
    return {"ok": True, "pid": 0, "method": "injected"}


def check(label, fn):
    try:
        ok = bool(fn())
        detail = ""
    except Exception as e:  # noqa: BLE001
        ok, detail = False, "%s: %s" % (type(e).__name__, e)
    RESULTS.append((label, ok, detail))
    print("  %-52s %s %s" % (label, "OK  " if ok else "FAIL", detail))


def main() -> int:
    # Never touch the live port or start a real Core.
    hc._probe_port = fake_probe
    hc.spawn_detached = fake_spawn

    td = Path(tempfile.mkdtemp(prefix="cosmos_cascade_"))
    root = install(td / "live", tree_id="spike-cascade-isolation")
    paths = CosmosPaths(str(root))
    state_file = root / "logs" / hc.SERVE_STATE_NAME

    print("clean root:", root, "\n")

    # ---- the same calls tests/test_core_supervisor.py makes, minus the
    # ---- section-1 default-ON poll that now writes state first.
    del CALLS[:]
    d = hc._supervise_serve(paths, False, False, False, None)
    check("clean: without supervise -> DISABLED",
          lambda: d["kind"] == "DISABLED" and CALLS == []
          and not state_file.exists())

    u = hc._supervise_serve(paths, True, True, False, None)
    check("clean: port already listening -> ALREADY_UP",
          lambda: u["kind"] == "ALREADY_UP" and CALLS == []
          and not state_file.exists())

    del CALLS[:]
    s = hc._supervise_serve(paths, False, True, False, None)
    check("clean: port down + enabled -> SPAWNED",
          lambda: s["kind"] == "SPAWNED")
    check("clean: spawned exactly once", lambda: len(CALLS) == 1)

    argv = CALLS[0]["argv"] if CALLS else []
    check("clean: argv execs THIS tree's cosmos.py serve",
          lambda: Path(argv[1]).name == "cosmos.py"
          and Path(argv[1]).is_file() and argv[2] == "serve")
    check("clean: argv carries the resolved root, not a literal",
          lambda: argv[argv.index("--root") + 1] == str(paths.root))
    check("clean: argv carries --port 8770 from the probed constant",
          lambda: argv[argv.index("--port") + 1] == str(hc.SERVE_PORT))

    # ---- and now demonstrate the cascade itself, so the claim is measured:
    # a fresh root where the FIRST call is a default poll_once (supervise now ON)
    # must leave state behind -- which is exactly what breaks the old assertions.
    root2 = install(td / "live2", tree_id="spike-cascade-isolation-2")
    state2 = root2 / "logs" / hc.SERVE_STATE_NAME
    del CALLS[:]
    PORT_UP[0] = False
    r2 = hc.poll_once(str(root2))              # no supervise= -> new default ON
    check("cascade: default poll_once now supervises (row present)",
          lambda: r2["rows"]["serve_supervisor"]["kind"] == "SPAWNED")
    check("cascade: default poll_once now WRITES core_serve.json",
          lambda: state2.is_file())
    check("cascade: written state carries a future backoff deadline",
          lambda: json.loads(state2.read_text(encoding="utf-8"))
          ["next_attempt_epoch"] > 0)
    nxt = hc._supervise_serve(CosmosPaths(str(root2)), False, True, False, None)
    check("cascade: THIS is why the old suite saw BACKOFF, not SPAWNED",
          lambda: nxt["kind"] == "BACKOFF")

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print("\n%d/%d passed" % (passed, total))
    print(json.dumps({"tests_run": total, "tests_passed": passed}))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
