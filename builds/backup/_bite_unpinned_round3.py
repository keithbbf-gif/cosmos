#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-3 unpinned backup refusals against CURRENT code.

  * do_retire(keep=True) — bool is an int; without the bool guard this is keep=1
  * do_retire dest-is-a-file — list_backup_sets DEST_NOT_DIR vs untyped listdir
  * pack() dest-is-a-file — currently an untyped FileExistsError (the defect)
  * identity.kind=volume_serial mismatch — IDENTITY_MISMATCH (unpinned)
  * FakeProbe unknown volume — DRIVE_NOT_MOUNTED (unpinned)

    py -3.14 builds/backup/_bite_unpinned_round3.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round3.json"

import cosmos_backup as cb                                            # noqa: E402
import cosmos_backup_mounts as mounts                                 # noqa: E402
import cosmos_state_offsite as so                                     # noqa: E402
from cosmos_backup import BackupRefusal                               # noqa: E402

KEY = b"test-hmac-key-not-a-real-secret"


class _FakePaths:
    def __init__(self, state: Path):
        self._state = state

    def role(self, *_parts):
        name = _parts[-1] if _parts else ""
        return self._state / name


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite3_"))
    rec = {"schema": "cosmos-bite/1",
           "what": "round3 unpinned backup refusals — current vs claimed"}
    try:
        dest_dir = tmp / "dest"
        dest_dir.mkdir()
        rec["keep_true_is_int"] = isinstance(True, int)
        rec["keep_true_equals_one"] = (True == 1)
        try:
            cb.do_retire(dest_dir, True, key=KEY)
            rec["keep_true_kind"] = None
            rec["keep_true_crash"] = None
        except BackupRefusal as e:
            rec["keep_true_kind"] = e.kind
            rec["keep_true_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["keep_true_kind"] = None
            rec["keep_true_crash"] = type(e).__name__

        dest_file = tmp / "dest_is_file"
        dest_file.write_text("not-a-dir", encoding="utf-8")
        try:
            cb.do_retire(dest_file, 1, key=KEY)
            rec["retire_dest_file_kind"] = None
            rec["retire_dest_file_crash"] = None
        except BackupRefusal as e:
            rec["retire_dest_file_kind"] = e.kind
            rec["retire_dest_file_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["retire_dest_file_kind"] = None
            rec["retire_dest_file_crash"] = type(e).__name__
        rec["retire_dest_file_untouched"] = dest_file.read_text(encoding="utf-8") == "not-a-dir"

        pack_file = tmp / "pack_is_file"
        pack_file.write_text("not-a-dir", encoding="utf-8")
        state = tmp / "state"
        state.mkdir()
        (state / "SEED.json").write_text("{}", encoding="utf-8")
        try:
            so.pack(_FakePaths(state), pack_file)
            rec["pack_dest_file_kind"] = None
            rec["pack_dest_file_crash"] = None
        except BackupRefusal as e:
            rec["pack_dest_file_kind"] = e.kind
            rec["pack_dest_file_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["pack_dest_file_kind"] = None
            rec["pack_dest_file_crash"] = type(e).__name__
        rec["pack_dest_file_untouched"] = pack_file.read_text(encoding="utf-8") == "not-a-dir"

        src = tmp / "src"
        src.mkdir()
        (src / "a.txt").write_text("a\n", encoding="utf-8")
        dest = tmp / "gdx"
        dest.mkdir()
        probe = mounts.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest): "vol:WRONG", str(dest.resolve()): "vol:WRONG",
        })
        cfg = tmp / "backup_targets.json"
        cfg.write_text(json.dumps({
            "schema": mounts.SCHEMA,
            "targets": {"gdx": {"dest": str(dest),
                                "identity": {"kind": "volume_serial",
                                             "value": "vol:WANT"}}},
        }), encoding="utf-8")
        try:
            mounts.bind("gdx", config_path=cfg, probe=probe)
            rec["volume_serial_kind"] = None
            rec["volume_serial_crash"] = None
        except BackupRefusal as e:
            rec["volume_serial_kind"] = e.kind
            rec["volume_serial_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["volume_serial_kind"] = None
            rec["volume_serial_crash"] = type(e).__name__

        empty_probe = mounts.FakeProbe(volumes={})
        try:
            empty_probe.volume_id(dest)
            rec["fake_unknown_vol_kind"] = None
            rec["fake_unknown_vol_crash"] = None
        except BackupRefusal as e:
            rec["fake_unknown_vol_kind"] = e.kind
            rec["fake_unknown_vol_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["fake_unknown_vol_kind"] = None
            rec["fake_unknown_vol_crash"] = type(e).__name__
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = (
        rec.get("keep_true_is_int") is True
        and rec.get("keep_true_equals_one") is True
        and rec.get("pack_dest_file_crash") is not None
        and rec.get("pack_dest_file_kind") is None
        and rec.get("pack_dest_file_untouched") is True
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
