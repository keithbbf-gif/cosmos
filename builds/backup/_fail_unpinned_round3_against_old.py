#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-3 backup pins MUST FAIL against the staged predecessor.

Staged at builds/backup/_delme/predispose_unpinned_round3_20260831T135200Z/

  * keep=True without the bool guard is keep=1 (True is int)
  * pack dest-is-a-file is untyped FileExistsError
  * identity.kind=volume_serial stripped falls through to BAD_CONFIG
  * FakeProbe unknown volume without the raise discovers a real vol id

    py -3.14 builds/backup/_fail_unpinned_round3_against_old.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "_fail_unpinned_round3_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round3_20260831T135200Z"


def _exec(path: Path, name: str, src: str | None = None):
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    text = src if src is not None else path.read_text(encoding="utf-8")
    exec(compile(text, str(path), "exec"), mod.__dict__)
    return mod


def main() -> int:
    failed = []
    ran = []
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(REPO / "cosmos"))

    old_bk = _exec(OLD / "cosmos_backup.py", "cb_old_r3")
    src_bk = (OLD / "cosmos_backup.py").read_text(encoding="utf-8")
    stripped = src_bk.replace(" or isinstance(keep, bool)", "")
    if stripped == src_bk:
        failed.append("keep_true:bool_guard_not_found")
    old_bk_s = _exec(OLD / "cosmos_backup.py", "cb_old_r3s", stripped)

    tdd = Path(tempfile.mkdtemp(prefix="cosmos_failold_r3_"))
    try:
        dest = tdd / "dest"
        dest.mkdir()
        ran.append("KEEP_TOO_SMALL_bool")
        try:
            old_bk_s.do_retire(dest, True, key=b"k")
            failed.append("KEEP_TOO_SMALL_bool:did_not_raise")
        except old_bk_s.BackupRefusal as e:
            if e.kind != "KEEP_TOO_SMALL":
                failed.append(f"KEEP_TOO_SMALL_bool:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"KEEP_TOO_SMALL_bool:{type(e).__name__}")

        old_so_src = (OLD / "cosmos_state_offsite.py").read_text(encoding="utf-8")
        # Bind the staged pack() against the live BackupRefusal class so
        # a typed refusal (if any) is comparable. The staged pack has no
        # dest-is-file guard.
        ns = {}
        exec(compile(
            "from pathlib import Path\nimport shutil\n"
            + old_so_src.split("def pack(", 1)[0].split("PAYLOAD =")[-1][:0]
            + "",
            "<skip>", "exec"), ns)
        # Direct: call staged pack by execing just the function against
        # a dest-that-is-a-file using live imports.
        sys.path.insert(0, str(OLD))
        # Isolate: run staged file as module (it imports sibling backup).
        # The staged file lives next to copies of cosmos_backup.py.
        pack_file = tdd / "pack_is_file"
        pack_file.write_text("not-a-dir", encoding="utf-8")
        state = tdd / "state"
        state.mkdir()
        (state / "SEED.json").write_text("{}", encoding="utf-8")

        class _P:
            def role(self, *_a):
                return state / _a[-1]

        ran.append("pack_DEST_NOT_DIR")
        old_so = _exec(OLD / "cosmos_state_offsite.py", "so_old_r3")
        try:
            old_so.pack(_P(), pack_file)
            failed.append("pack_DEST_NOT_DIR:did_not_raise")
        except old_so.cb.BackupRefusal as e:
            if e.kind != "DEST_NOT_DIR":
                failed.append(f"pack_DEST_NOT_DIR:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"pack_DEST_NOT_DIR:{type(e).__name__}")

        old_m_src = (OLD / "cosmos_backup_mounts.py").read_text(encoding="utf-8")
        stripped_m = old_m_src.replace(
            '    if kind == "volume_serial":\n',
            '    if kind == "volume_serial_STRIPPED":\n',
        )
        if stripped_m == old_m_src:
            failed.append("volume_serial:branch_not_found")
        old_m = _exec(OLD / "cosmos_backup_mounts.py", "mnt_old_r3", stripped_m)
        src = tdd / "src"
        src.mkdir()
        (src / "a.txt").write_text("a\n", encoding="utf-8")
        gdx = tdd / "gdx"
        gdx.mkdir()
        probe = old_m.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(gdx): "vol:AAAA1111", str(gdx.resolve()): "vol:AAAA1111",
        })
        cfg = tdd / "backup_targets.json"
        cfg.write_text(json.dumps({
            "schema": old_m.SCHEMA,
            "targets": {"gdx": {"dest": str(gdx),
                                "identity": {"kind": "volume_serial",
                                             "value": "vol:BBBB2222"}}},
        }), encoding="utf-8")
        ran.append("volume_serial_IDENTITY_MISMATCH")
        try:
            old_m.bind("gdx", config_path=cfg, probe=probe)
            failed.append("volume_serial_IDENTITY_MISMATCH:did_not_raise")
        except old_m.BackupRefusal as e:
            if e.kind != "IDENTITY_MISMATCH":
                failed.append(f"volume_serial_IDENTITY_MISMATCH:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"volume_serial_IDENTITY_MISMATCH:{type(e).__name__}")

        stripped_fp = old_m_src.replace(
            '        raise BackupRefusal("DRIVE_NOT_MOUNTED", '
            'f"FakeProbe has no volume id for {path}")',
            '        return "vol:DISCOVERED"',
        )
        if stripped_fp == old_m_src:
            failed.append("fakeprobe:raise_not_found")
        old_m2 = _exec(OLD / "cosmos_backup_mounts.py", "mnt_old_r3b", stripped_fp)
        ran.append("fakeprobe_DRIVE_NOT_MOUNTED")
        probe2 = old_m2.FakeProbe(volumes={})
        try:
            vid = probe2.volume_id(gdx)
            failed.append(f"fakeprobe_DRIVE_NOT_MOUNTED:returned:{vid}")
        except old_m2.BackupRefusal as e:
            if e.kind != "DRIVE_NOT_MOUNTED":
                failed.append(f"fakeprobe_DRIVE_NOT_MOUNTED:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"fakeprobe_DRIVE_NOT_MOUNTED:{type(e).__name__}")
    finally:
        shutil.rmtree(tdd, ignore_errors=True)

    out = {
        "schema": "cosmos-fail-against-old/1",
        "what": "round3 backup pins FAIL against staged predecessor / stripped guards",
        "predecessor": str(OLD),
        "ran": ran,
        "failed": failed,
        "all_new_pins_failed": bool(ran) and len(failed) == len(ran),
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0 if out["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
