#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic NL cron parser pins.

every 15s / every 5m / hourly / daily 07:00 / on logon / garbage=UNRECOGNIZED.
Parser only: no task create, no schtasks.exe, no in-process cron.
COSMOS_SCHTASKS_SANDBOX still refuses native writes.
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_clock import plan_create, run_schtasks, tr_cmdline  # noqa: E402
from cosmos_nlcron import NlcronError, parse_cadence, _selftest  # noqa: E402

NLCRON_SRC = ROOT / "cosmos" / "cosmos_nlcron.py"
FORBIDDEN_CALLS = frozenset({
    "create_task", "run_schtasks", "spawn_detached", "spawn_wmi",
    "spawn_popen_detached", "Popen", "run", "system", "Timer",
    "sleep", "add_route", "route",
})
FORBIDDEN_IMPORTS = frozenset({
    "subprocess", "asyncio", "threading", "sched",
})


def test_every_15s_detached_daemon():
    rec = parse_cadence("every 15s")
    assert rec["mode"] == "detached_daemon"
    assert rec["interval_s"] == 15.0
    assert rec["schtasks"] is None
    assert rec["tr_extra"] == ("--loop",)
    assert rec["clocks"] == "COSMOS Activity Clock (Watchdog2)"


def test_every_5m_schtasks_minute():
    rec = parse_cadence("every 5m")
    assert rec["mode"] == "schtasks"
    assert rec["interval_s"] == 300.0
    assert rec["schtasks"] == {"sc": "minute", "mo": 5, "st": None}
    assert rec["tr_extra"] == ("--once",)
    assert rec["clocks"] == "COSMOS Ledger Verify"
    argv = plan_create(
        "COSMOS Ledger Verify", "tr",
        rec["schtasks"]["sc"],
        mo=rec["schtasks"]["mo"],
        st=rec["schtasks"]["st"],
    )
    assert argv[argv.index("/sc") + 1] == "minute"
    assert argv[argv.index("/mo") + 1] == "5"
    assert int(rec["schtasks"]["mo"]) >= 1


def test_hourly_schtasks():
    rec = parse_cadence("hourly")
    assert rec["mode"] == "schtasks"
    assert rec["interval_s"] == 3600.0
    assert rec["schtasks"] == {"sc": "HOURLY", "mo": None, "st": None}
    assert rec["clocks"] is None  # Discovery + Askmine + NEW-AI Scout
    argv = plan_create("COSMOS Mesh Discovery", "tr", rec["schtasks"]["sc"])
    assert argv[argv.index("/sc") + 1] == "HOURLY"


def test_daily_0700_schtasks():
    rec = parse_cadence("daily 07:00")
    assert rec["mode"] == "schtasks"
    assert rec["interval_s"] is None
    assert rec["schtasks"] == {"sc": "DAILY", "mo": None, "st": "07:00"}
    assert rec["clocks"] == "COSMOS Backup"
    argv = plan_create(
        "COSMOS Backup 07", "tr",
        rec["schtasks"]["sc"],
        mo=rec["schtasks"]["mo"],
        st=rec["schtasks"]["st"],
    )
    assert argv[argv.index("/sc") + 1] == "DAILY"
    assert argv[argv.index("/st") + 1] == "07:00"


def test_on_logon():
    rec = parse_cadence("on logon")
    assert rec["mode"] == "onlogon"
    assert rec["interval_s"] is None
    assert rec["schtasks"] == {"sc": "onlogon", "mo": None, "st": None}
    assert rec["tr_extra"] == ("--loop",)
    argv = plan_create(
        "COSMOS Watchdog2 Logon", "tr",
        rec["schtasks"]["sc"],
        mo=rec["schtasks"]["mo"],
        st=rec["schtasks"]["st"],
    )
    assert argv[argv.index("/sc") + 1] == "onlogon"
    tr = tr_cmdline(NLCRON_SRC, ".", *rec["tr_extra"])
    assert "--loop" in tr


def test_garbage_unrecognized():
    try:
        parse_cadence("garbage")
    except NlcronError as e:
        assert e.kind == "UNRECOGNIZED"
    else:
        raise AssertionError("garbage must be UNRECOGNIZED")


def test_no_silent_default():
    for phrase in ("", "   ", "every", "15", "daily", "every 15",
                   "every 15s and hourly", "soon", "cron"):
        try:
            parse_cadence(phrase)
        except NlcronError as e:
            assert e.kind == "UNRECOGNIZED", phrase
        else:
            raise AssertionError(f"silent default for {phrase!r}")


def test_sub_minute_never_schtasks_mo_lt_1():
    for phrase in ("every 15s", "every 30s", "every 5 seconds", "15s"):
        rec = parse_cadence(phrase)
        assert rec["mode"] == "detached_daemon", phrase
        assert rec["schtasks"] is None, phrase
        assert rec["interval_s"] < 60.0, phrase


def test_parser_source_is_fold_only():
    src = NLCRON_SRC.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split(".", 1)[0])
        elif isinstance(n, ast.ImportFrom) and n.module:
            imports.add(n.module.split(".", 1)[0])
    assert not (FORBIDDEN_IMPORTS & imports), imports
    calls = set()
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        if isinstance(n.func, ast.Name):
            calls.add(n.func.id)
        elif isinstance(n.func, ast.Attribute):
            calls.add(n.func.attr)
    assert not (FORBIDDEN_CALLS & calls), calls
    assert "threading.Timer" not in src
    assert "create_task(" not in src
    assert "run_schtasks(" not in src


def test_schtasks_sandbox_still_refuses_and_nlcron_does_not_write():
    prev = os.environ.get("COSMOS_SCHTASKS_SANDBOX")
    os.environ["COSMOS_SCHTASKS_SANDBOX"] = "1"
    try:
        rec = parse_cadence("every 5m")
        assert rec["mode"] == "schtasks"
        refused = run_schtasks(plan_create(
            "COSMOS Nlcron Probe", "echo",
            rec["schtasks"]["sc"],
            mo=rec["schtasks"]["mo"],
            st=rec["schtasks"]["st"],
        ))
    finally:
        if prev is None:
            os.environ.pop("COSMOS_SCHTASKS_SANDBOX", None)
        else:
            os.environ["COSMOS_SCHTASKS_SANDBOX"] = prev
    assert refused.get("ok") is False
    assert refused.get("sandbox") is True
    assert refused.get("kind") == "PROD_WRITE_REFUSED"
    assert refused.get("out") == "PROD_WRITE_REFUSED"


def test_module_selftest_pass():
    assert _selftest() == 0


def main() -> int:
    test_every_15s_detached_daemon()
    test_every_5m_schtasks_minute()
    test_hourly_schtasks()
    test_daily_0700_schtasks()
    test_on_logon()
    test_garbage_unrecognized()
    test_no_silent_default()
    test_sub_minute_never_schtasks_mo_lt_1()
    test_parser_source_is_fold_only()
    test_schtasks_sandbox_still_refuses_and_nlcron_does_not_write()
    test_module_selftest_pass()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
