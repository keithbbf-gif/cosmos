#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New BACKUP_VERIFIED.node / COMMAND_HANDLED.node pins MUST FAIL on the
staged predecessor.

Run: py -3.14 cosmos/_fail_follow_backup_command_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_ledger import Ledger  # noqa: E402

PRE = REPO / "_delme" / "predispose_follow_backup_command_20260831T134754Z" / "cosmos"
OUT = REPO / "cosmos" / "_fail_follow_backup_command_against_old.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load " + str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _compact(src: str) -> str:
    return "".join(src.split())


def main() -> int:
    need = ("cosmos_backup.py", "cosmos_command.py",
            "cosmos_backup_clock.py", "cosmos.py")
    missing = [n for n in need if not (PRE / n).is_file()]
    if missing:
        print("REFUSING: staged predecessor missing %s at %s" % (missing, PRE))
        return 2

    old_bak = _load("old_cosmos_backup_fail", PRE / "cosmos_backup.py")
    old_cmd = _load("old_cosmos_command_fail", PRE / "cosmos_command.py")

    td = Path(tempfile.mkdtemp(prefix="cosmos_fail_bak_cmd_"))
    KEY = b"k"
    src = td / "src"
    src.mkdir()
    (src / "a.txt").write_text("alpha", encoding="utf-8")
    tgt = td / "tgt"
    tgt.mkdir()
    led = Ledger(td / "b.jsonl", KEY, "fail-bak")
    old_bak.Backup(led).run(src, tgt)
    bp = next(r for r in led.verify()
              if r["event"] == "BACKUP_VERIFIED")["payload"]
    pin_backup = bp.get("node") == "COSMOS"

    root = install(td / "live", tree_id="fail-cmd")
    k = Kernel(root, worker="voice-fail")
    old_cmd.Commander(k).handle("status")
    cp = next(r for r in k.ledger.verify()
              if r["event"] == "COMMAND_HANDLED")["payload"]
    pin_cmd = cp.get("node") == "CVM"

    clock_src = _compact((PRE / "cosmos_backup_clock.py").read_text(
        encoding="utf-8"))
    pin_clock = "node=paths.sentinel.system" in clock_src

    cli_src = _compact((PRE / "cosmos.py").read_text(encoding="utf-8"))
    pin_cli = "node=k.paths.sentinel.system" in cli_src

    old_clock = _load("old_cosmos_backup_clock_fail",
                      PRE / "cosmos_backup_clock.py")
    man = root / "queue" / "manifests"
    man.mkdir(parents=True, exist_ok=True)
    (man / "m0.json").write_text("{}", encoding="utf-8")
    old_clock.poll_once(str(root), force=True)
    clock_nodes = []
    led_path = root / "ledger" / "authority.jsonl"
    if led_path.is_file():
        for line in led_path.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec.get("event") == "BACKUP_VERIFIED":
                clock_nodes.append((rec.get("payload") or {}).get("node"))
    pin_clock_runtime = clock_nodes == [k.paths.sentinel.system]

    pins = {
        "backup_verified_node_equals_COSMOS": pin_backup,
        "command_handled_node_equals_CVM": pin_cmd,
        "clock_passes_sentinel_system": pin_clock,
        "cli_passes_sentinel_system": pin_cli,
        "old_clock_poll_once_stamps_node": pin_clock_runtime,
    }
    any_passed = any(pins.values())
    evidence = {
        "ok": (not any_passed),
        "all_new_pins_failed": (not any_passed),
        "pins": pins,
        "old_backup_payload": bp,
        "old_backup_node": bp.get("node"),
        "old_command_payload": cp,
        "old_command_node": cp.get("node"),
        "old_clock_backup_nodes": clock_nodes,
        "pin_passed_on_old": any_passed,
        "prechange_path": str(PRE),
    }
    OUT.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    print("pin_passed_on_old=%s (want False)" % any_passed)
    for name, passed in pins.items():
        print("  %s  %s" % ("PASS" if passed else "FAIL", name))
    print("old_backup_payload=%s" % bp)
    print("old_command_payload=%s" % cp)
    print("EVIDENCE %s" % OUT)
    return 0 if evidence["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
