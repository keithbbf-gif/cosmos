#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-43 SECRETS_IN_SCOPE pins FAIL against the staged pre-change clock.

A pin that PASSES on the old module is not a pin.

  py -3.14 cosmos/_fail_f43_secrets_clock_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
REPO = HERE.parent
OLD_DIR = REPO / "_delme" / "predispose_f43_secrets_clock_20260831T102247Z"
OLD_CLOCK = OLD_DIR / "cosmos_backup_clock.py"
OLD_BAK = OLD_DIR / "cosmos_backup.py"
OUT = HERE / "_fail_f43_secrets_clock_against_old.json"

sys.path.insert(0, str(HERE))


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from cosmos_ledger import Ledger

    # Clock does `from cosmos_backup import Backup`. Bind the STAGED
    # predecessor under that name so poll_once is the old engine, not a
    # mixed old-clock + new-Backup pair.
    old_bak = _load(OLD_BAK, "cosmos_backup")
    old_clock = _load(OLD_CLOCK, "cosmos_backup_clock_old_f43")
    td = Path(tempfile.mkdtemp(prefix="cosmos_fail_f43sec_"))
    root = install(td / "live", tree_id="fail-f43-secrets-clock")
    man = root / "queue" / "manifests"
    man.mkdir(parents=True, exist_ok=True)
    (man / "m0.json").write_text("{}", encoding="utf-8")
    paths = CosmosPaths(root)
    stage = paths.backups("_snapshot")
    pins = []

    def pin(name, fn):
        try:
            ok = bool(fn())
            err = ""
        except Exception as e:  # noqa: BLE001
            ok = False
            err = "%s: %s" % (type(e).__name__, e)
        pins.append({"name": name, "passed_on_old": ok, "err": err})

    pin("Backup.scan_secrets exists",
        lambda: callable(getattr(old_bak, "scan_secrets", None)))
    pin("BackupError kinds name SECRETS_IN_SCOPE",
        lambda: "SECRETS_IN_SCOPE" in (old_bak.BackupError.__doc__ or ""))

    n = old_clock.assemble_snapshot(paths, stage)
    pin("assemble_snapshot does not copy install_key.bin into the snapshot",
        lambda: n >= 1 and not (stage / "config" / "install_key.bin").is_file())

    src = td / "plant_src"
    src.mkdir()
    (src / "a.txt").write_text("alpha", encoding="utf-8")
    (src / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
    tgt = td / "plant_tgt"
    tgt.mkdir()
    KEY = (root / "config" / "install_key.bin").read_bytes()
    led = Ledger(td / "bk.jsonl", KEY, "fail-f43")
    try:
        rec = old_bak.Backup(led).run(src, tgt)
        sealed = rec.get("files", 0) >= 2
        dest_made = Path(rec["dest"]).is_dir()
        kind = None
    except Exception as e:  # noqa: BLE001
        sealed, dest_made = False, False
        kind = getattr(e, "kind", type(e).__name__)
    pin("Backup.run raises SECRETS_IN_SCOPE on planted install_key.bin",
        lambda: kind == "SECRETS_IN_SCOPE" and sealed is False)
    pin("Backup.run does not create a dest over a planted key",
        lambda: kind == "SECRETS_IN_SCOPE" and dest_made is False
        and not any(tgt.iterdir()))

    plant = man / "install_key.bin"
    plant.write_bytes(b"NOT-A-REAL-KEY")
    try:
        old_clock.assemble_snapshot(paths, stage)
        plant_kind = None
    except Exception as e:  # noqa: BLE001
        plant_kind = getattr(e, "kind", type(e).__name__)
    pin("assemble_snapshot raises SECRETS_IN_SCOPE on planted manifests/install_key.bin",
        lambda: plant_kind == "SECRETS_IN_SCOPE")

    r = old_clock.poll_once(str(root), force=True)
    pin("poll_once over a planted key is FAILED SECRETS_IN_SCOPE",
        lambda: r.get("ok") is False and r.get("state") == "FAILED"
        and r.get("kind") == "SECRETS_IN_SCOPE")

    failed = [p for p in pins if not p["passed_on_old"]]
    out = {
        "old_clock": str(OLD_CLOCK),
        "old_backup": str(OLD_BAK),
        "pins": pins,
        "pin_count": len(pins),
        "failed_on_old": len(failed),
        "all_new_pins_failed": len(failed) == len(pins) and len(pins) > 0,
        "old_poll_kind": r.get("kind"),
        "old_poll_state": r.get("state"),
        "old_run_kind": kind,
        "planted_assemble_kind": plant_kind,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if out["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
