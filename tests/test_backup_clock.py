#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin SNAPSHOT_INCOMPLETE and SECRETS_IN_SCOPE on the scheduled backup clock.

F-43 leftover (2) was closed in prose: cosmos_backup_clock.assemble_snapshot
REFUSES SNAPSHOT_INCOMPLETE on cap / unreadable / oversize rather than
handing a truncated scope to a function whose next act is BACKUP_VERIFIED.

F-43 leftover (clock secrets, 2026-08-31T16:32Z): the scheduled cosmos/
clock staged install_key.bin and sealed BACKUP_VERIFIED with no secret
scan. builds/backup/cosmos_backup.py already refused SECRETS_IN_SCOPE;
the live 4x-daily path did not. Bite first against
  _delme/predispose_f43_secrets_clock_20260831T102247Z/
7/7 new pins FAIL (cosmos/_fail_f43_secrets_clock_against_old.json
all_new_pins_failed=true), including old poll_once state=VERIFIED over
a planted key.

Run:  py -3.14 tests/test_backup_clock.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_backup import Backup, BackupError, scan_secrets  # noqa: E402
from cosmos_backup_clock import (  # noqa: E402
    HEARTBEAT_NAME, MAX_STAGE_BYTES, STAGE_LIMIT, _copy_tree_files,
    assemble_snapshot, poll_once,
)
from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

EVIDENCE = REPO / "cosmos" / "_f_snapshot_incomplete.json"
RESULTS: list = []
LIVE_VALUE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def expect_kind(kind):
    def wrap(f):
        def inner():
            try:
                f()
            except BackupError as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def _root() -> Path:
    td = Path(tempfile.mkdtemp(prefix="cosmos_snapinc_"))
    return install(td / "live", tree_id="spike-snapshot-incomplete")


def _fill_manifests(root: Path, n: int) -> None:
    man = root / "queue" / "manifests"
    man.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        (man / ("m%d.json" % i)).write_text("{}", encoding="utf-8")


def run() -> int:
    root = _root()
    paths = CosmosPaths(root)
    stage = paths.backups("_snapshot")

    rec = _copy_tree_files(root / "queue" / "manifests", stage / "probe0")
    check("_copy_tree_files returns a RECORD, not a bare int",
          lambda: isinstance(rec, dict)
          and {"copied", "truncated", "unreadable", "skipped_large"} <= set(rec))

    many = Path(tempfile.mkdtemp(prefix="cosmos_snapcap_"))
    for i in range(STAGE_LIMIT + 1):
        (many / ("f%04d.txt" % i)).write_text("x", encoding="utf-8")
    cap = _copy_tree_files(many, Path(tempfile.mkdtemp(prefix="cosmos_snapcapd_")))
    check("hitting the real STAGE_LIMIT declares truncated (never silent omit)",
          lambda: cap["copied"] == STAGE_LIMIT and cap["truncated"] is True)

    _fill_manifests(root, 3)
    n = assemble_snapshot(paths, stage)
    check("a whole scope still assembles (no-regression)",
          lambda: n >= 3 and (stage / "queue" / "manifests" / "m0.json").is_file())

    clock = sys.modules["cosmos_backup_clock"]
    _fill_manifests(root, 5)

    def _cap_two():
        with mock.patch.object(clock, "STAGE_LIMIT", 2):
            assemble_snapshot(paths, stage)

    check("truncated scope raises SNAPSHOT_INCOMPLETE (kind, not a message)",
          expect_kind("SNAPSHOT_INCOMPLETE")(_cap_two))

    _fill_manifests(root, 5)
    try:
        with mock.patch.object(clock, "STAGE_LIMIT", 2):
            assemble_snapshot(paths, stage)
        cap_kind, cap_detail = None, ""
    except BackupError as e:
        cap_kind, cap_detail = e.kind, str(e)
    check("SNAPSHOT_INCOMPLETE names the truncated subtree queue/manifests",
          lambda: cap_kind == "SNAPSHOT_INCOMPLETE"
          and "queue/manifests" in cap_detail
          and "TRUNCATED" in cap_detail)

    _fill_manifests(root, 3)
    real_stat = os.stat

    def flaky_manifest(p, *a, **k):
        if str(p).replace("\\", "/").endswith("m1.json"):
            raise PermissionError(13, "denied", str(p))
        return real_stat(p, *a, **k)

    def _unread_tree():
        with mock.patch.object(os, "stat", flaky_manifest):
            assemble_snapshot(paths, stage)

    check("unreadable tree file raises SNAPSHOT_INCOMPLETE (a hole, not a skip)",
          expect_kind("SNAPSHOT_INCOMPLETE")(_unread_tree))

    _fill_manifests(root, 2)
    (root / "queue" / "manifests" / "huge.bin").write_bytes(b"\0" * 8)

    def _oversize():
        with mock.patch.object(clock, "MAX_STAGE_BYTES", 1):
            assemble_snapshot(paths, stage)

    check("oversize file in a bounded scope raises SNAPSHOT_INCOMPLETE",
          expect_kind("SNAPSHOT_INCOMPLETE")(_oversize))
    (root / "queue" / "manifests" / "huge.bin").unlink()

    _fill_manifests(root, 2)
    real_stat2 = os.stat

    def flaky_named(p, *a, **k):
        if str(p).replace("\\", "/").endswith("install_record.json"):
            raise PermissionError(13, "denied", str(p))
        return real_stat2(p, *a, **k)

    def _unread_named():
        with mock.patch.object(os, "stat", flaky_named):
            assemble_snapshot(paths, stage)

    check("unreadable named config is SOURCE_UNREADABLE (absent != unreadable)",
          expect_kind("SOURCE_UNREADABLE")(_unread_named))

    check("absent optional SEED.json is not a hole",
          lambda: not (root / "state" / "SEED.json").exists()
          and assemble_snapshot(paths, stage) >= 2)

    _fill_manifests(root, 5)
    with mock.patch.object(sys.modules["cosmos_backup_clock"], "STAGE_LIMIT", 2):
        r = poll_once(str(root), force=True)
    hb_path = root / "logs" / HEARTBEAT_NAME
    hb = json.loads(hb_path.read_text(encoding="utf-8")) if hb_path.is_file() else {}
    led = root / "ledger" / "authority.jsonl"
    led_txt = led.read_text(encoding="utf-8") if led.is_file() else ""
    check("poll_once over a truncated scope is FAILED SNAPSHOT_INCOMPLETE",
          lambda: r.get("ok") is False and r.get("state") == "FAILED"
          and r.get("kind") == "SNAPSHOT_INCOMPLETE")
    check("heartbeat records FAILED, never VERIFIED over a hole",
          lambda: hb.get("state") == "FAILED")
    check("no BACKUP_VERIFIED ledger event over a truncated scope",
          lambda: "BACKUP_VERIFIED" not in led_txt)

    _fill_manifests(root, 3)
    r_ok = poll_once(str(root), force=True)
    check("poll_once still VERIFIES a whole scope (no-regression)",
          lambda: r_ok.get("ok") is True and r_ok.get("state") == "VERIFIED"
          and int(r_ok.get("files") or 0) == int(r_ok.get("staged") or -1))
    led_ok = led.read_text(encoding="utf-8") if led.is_file() else ""
    verified_nodes = []
    for line in led_ok.splitlines():
        rec = json.loads(line)
        if rec.get("event") == "BACKUP_VERIFIED":
            verified_nodes.append((rec.get("payload") or {}).get("node"))
    check("BACKUP_VERIFIED.node is sentinel.system (FOLLOW_KEYS)",
          lambda: verified_nodes == [paths.sentinel.system]
          and paths.sentinel.system == "COSMOS")

    # ---- F-43 clock SECRETS_IN_SCOPE (COVERAGE gap 4 on the scheduled path)
    n_clean = assemble_snapshot(paths, stage)
    check("assemble_snapshot does not copy install_key.bin (still reads it to open ledger)",
          lambda: n_clean >= 3
          and (root / "config" / "install_key.bin").is_file()
          and not (stage / "config" / "install_key.bin").is_file())

    hits = scan_secrets({"files": {
        "config/install_key.bin": {"sha256": "abc", "size": 32},
        "a.txt": {"sha256": "def", "size": 1},
    }})
    check("scan_secrets matches install_key.bin by path name, never opens the file",
          lambda: hits == ["config/install_key.bin"])

    src_p = Path(tempfile.mkdtemp(prefix="cosmos_f43sec_src_"))
    (src_p / "a.txt").write_text("alpha", encoding="utf-8")
    (src_p / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
    tgt_p = Path(tempfile.mkdtemp(prefix="cosmos_f43sec_tgt_"))
    from cosmos_ledger import Ledger
    KEY = (root / "config" / "install_key.bin").read_bytes()
    bled = Ledger(Path(tempfile.mkdtemp(prefix="cosmos_f43sec_led_")) / "bk.jsonl",
                  KEY, "f43-secrets")
    try:
        Backup(bled).run(src_p, tgt_p)
        run_kind, run_detail = None, ""
    except BackupError as e:
        run_kind, run_detail = e.kind, str(e)
    check("Backup.run planted install_key.bin is SECRETS_IN_SCOPE",
          lambda: run_kind == "SECRETS_IN_SCOPE"
          and "install_key.bin" in run_detail)
    check("SECRETS_IN_SCOPE happens before a dest set is created",
          lambda: run_kind == "SECRETS_IN_SCOPE"
          and list(tgt_p.iterdir()) == [])

    _fill_manifests(root, 2)
    (root / "queue" / "manifests" / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
    try:
        assemble_snapshot(paths, stage)
        plant_kind = None
    except BackupError as e:
        plant_kind = e.kind
    check("planted manifests/install_key.bin is SECRETS_IN_SCOPE (not SNAPSHOT_INCOMPLETE)",
          lambda: plant_kind == "SECRETS_IN_SCOPE")

    r_sec = poll_once(str(root), force=True)
    hb_sec_path = root / "logs" / HEARTBEAT_NAME
    hb_sec = json.loads(hb_sec_path.read_text(encoding="utf-8")) if hb_sec_path.is_file() else {}
    led_after = led.read_text(encoding="utf-8") if led.is_file() else ""
    verified_after_plant = [
        json.loads(line) for line in led_after.splitlines()
        if line.strip() and json.loads(line).get("event") == "BACKUP_VERIFIED"
    ]
    check("poll_once over a planted key is FAILED SECRETS_IN_SCOPE",
          lambda: r_sec.get("ok") is False and r_sec.get("state") == "FAILED"
          and r_sec.get("kind") == "SECRETS_IN_SCOPE")
    check("heartbeat records FAILED SECRETS_IN_SCOPE, never VERIFIED over a key",
          lambda: hb_sec.get("state") == "FAILED"
          and hb_sec.get("kind") == "SECRETS_IN_SCOPE")
    check("no additional BACKUP_VERIFIED after the planted-key poll",
          lambda: len(verified_after_plant) == 1)

    LIVE_VALUE.update({
        "checks": len(RESULTS),
        "refusal_kinds": ["SNAPSHOT_INCOMPLETE", "SOURCE_UNREADABLE",
                          "SECRETS_IN_SCOPE"],
        "stage_limit": STAGE_LIMIT,
        "max_stage_bytes": MAX_STAGE_BYTES,
        "truncated_kind": r.get("kind"),
        "truncated_state": r.get("state"),
        "whole_scope_state": r_ok.get("state"),
        "whole_scope_files": r_ok.get("files"),
        "whole_scope_node": verified_nodes[0] if verified_nodes else None,
        "secrets_kind": r_sec.get("kind"),
        "secrets_state": r_sec.get("state"),
        "snapshot_copies_install_key": (stage / "config" / "install_key.bin").is_file(),
        "heartbeat": HEARTBEAT_NAME,
    })

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % (
            "OK  " if ok else "FAIL", label,
            ("  [" + err + "]") if err else ""))
    evidence = {
        "ok": not bad,
        "probe": "tests/test_backup_clock.py — SNAPSHOT_INCOMPLETE pin",
        "live_value": LIVE_VALUE,
        "passed": len(RESULTS) - len(bad),
        "tests_run": len(RESULTS),
        "tests_passed": len(RESULTS) - len(bad),
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print("live_value: " + repr(LIVE_VALUE))
    print("result: %s  %d/%d on SNAPSHOT_INCOMPLETE+SECRETS_IN_SCOPE" % (
        "ok" if not bad else "FAIL",
        len(RESULTS) - len(bad), len(RESULTS)))
    return 1 if bad else 0


def main() -> int:
    from cosmos_test_guard import sandbox_heartbeats
    with sandbox_heartbeats():
        return run()


def test_backup_clock_snapshot_incomplete():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
