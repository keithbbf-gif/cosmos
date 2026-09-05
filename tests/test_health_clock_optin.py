#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the --supervise fence on cosmos_health_clock (CLI-bound).

Sister suite to test_core_supervisor.py. That one injects the spawner and tests
the supervisor's logic in-process; this one runs the module as the OS runs it --
a real `py cosmos_health_clock.py --once` subprocess against a scratch root --
so the claim "DEFAULT ON; --no-supervise still inert" is bound to the artifact
the CLI emits, not to a reading of the source.

Nothing here can start a Core: the only --supervise run is fenced behind a
mode=hold PAUSE flag, and the test asserts no spawn state was written on any
path.
"""
from __future__ import annotations

import inspect
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_health_clock as hc                                   # noqa: E402
from cosmos_kernel import install                                  # noqa: E402

RESULTS = []
MODULE = Path(hc.__file__).resolve()
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
# The row set the live board has carried since before the supervisor existed.
BASE_ROWS = {"sentinel", "ledger_file", "install_key", "queue", "pause_flag",
             "serve_8770", "peer_heartbeats"}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def run_cli(*args) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.run([sys.executable, str(MODULE), *args],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=90, env=env,
                       stdin=subprocess.DEVNULL, creationflags=NO_WINDOW)
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()


def board_of(root: Path) -> dict:
    return json.loads((root / "state" / "health" / "board.json").read_text(
        encoding="utf-8"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_optin_"))
    off = install(td / "off", tree_id="spike-optin-off")
    on = install(td / "on", tree_id="spike-optin-on")

    # ---- --no-supervise is still inert (DEFAULT is ON since 2026-08-31) ----
    rc, out = run_cli("--root", str(off), "--once", "--no-supervise")
    check("CLI --once exits 0", lambda: rc == 0)
    doc = json.loads(out)
    check("CLI --once emits this clock's schema",
          lambda: doc["schema"] == hc.SCHEMA)
    check("default CLI run reports NO supervisor",
          lambda: "serve_supervisor" not in doc)
    check("default CLI run wrote no spawn state",
          lambda: not (off / "logs" / hc.SERVE_STATE_NAME).exists())
    check("default CLI run took no spawn lock",
          lambda: not (off / "logs" / hc.SERVE_LOCK_NAME).exists())
    check("default board carries exactly the pre-supervisor rows",
          lambda: set(board_of(off)["rows"]) == BASE_ROWS)

    rc2, out2 = run_cli("--root", str(off), "--once", "--no-supervise")
    check("a second default run is identical in shape (no drift)",
          lambda: rc2 == 0 and set(board_of(off)["rows"]) == BASE_ROWS
          and "serve_supervisor" not in json.loads(out2))

    # ---- the flag is real, and PAUSE fences it -----------------------------
    pause = on / "state" / "control" / "PAUSE.flag"
    pause.parent.mkdir(parents=True, exist_ok=True)
    pause.write_text(json.dumps({"mode": "hold",
                                 "reason": "selftest fence"}), encoding="utf-8")
    rc3, out3 = run_cli("--root", str(on), "--once", "--supervise")
    doc3 = json.loads(out3)
    port_up = hc._probe_port("127.0.0.1", hc.SERVE_PORT)["ok"]
    check("CLI --supervise exits 0", lambda: rc3 == 0)
    check("CLI --supervise reports a typed supervisor kind",
          lambda: doc3["serve_supervisor"]["kind"] in
          ("PAUSED_HOLD", "ALREADY_UP"))
    check("with :8770 down, a hold PAUSE refuses the spawn",
          lambda: port_up or doc3["serve_supervisor"]["kind"] == "PAUSED_HOLD")
    check("no Core was spawned on the refusal path",
          lambda: not (on / "logs" / hc.SERVE_STATE_NAME).exists())
    check("--supervise adds exactly one board row and nothing else",
          lambda: set(board_of(on)["rows"]) == BASE_ROWS | {"serve_supervisor"})

    rc4, help_out = run_cli("--root", "x", "--help")
    check("--supervise is documented on the CLI surface",
          lambda: rc4 == 0 and "--supervise" in help_out
          and "--no-supervise" in help_out and "DEFAULT ON" in help_out)

    # ---- the fence is structural, not a convention -------------------------
    for name in ("poll_once", "loop", "standup"):
        sig = inspect.signature(getattr(hc, name))
        check(f"{name}(supervise=) defaults to True",
              lambda s=sig: s.parameters["supervise"].default is True)
    src = inspect.getsource(hc._supervise_serve)
    check("the supervise guard precedes any spawn in _supervise_serve",
          lambda: 0 <= src.index("if not supervise")
          < src.index("spawn_detached("))
    check("every typed kind is named in the supervisor's own docstring",
          lambda: all(k in (hc._supervise_serve.__doc__ or "") for k in
                      ("DISABLED", "ALREADY_UP", "PAUSED_HOLD", "BACKOFF",
                       "CHILD_ALIVE", "SUPERVISOR_BUSY", "SPAWNED",
                       "SPAWN_FAILED")))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
