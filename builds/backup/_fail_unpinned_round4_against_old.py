#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-4 backup pins MUST FAIL against stripped current / predecessor.

Staged at builds/backup/_delme/predispose_unpinned_round4_20260831T142253Z/

The guards already live in current code; stripping them is the pre-fix.
A pin that still PASSES after the strip is not pinning the refusal.

    py -3.14 builds/backup/_fail_unpinned_round4_against_old.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round4_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round4_20260831T142253Z"


def _exec(path: Path, name: str, src: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(src, str(path), "exec"), mod.__dict__)
    return mod


def _strip_mounts(src: str) -> str:
    src = src.replace(
        '        if got != str(expect):\n'
        '            raise BackupRefusal("IDENTITY_MISMATCH",\n'
        '                                f"{spec[\'kind\']} model {got!r} != declared {expect!r}")\n',
        '        if False and got != str(expect):\n'
        '            raise BackupRefusal("IDENTITY_MISMATCH",\n'
        '                                f"{spec[\'kind\']} model {got!r} != declared {expect!r}")\n',
    )
    src = src.replace(
        '        for k, v in (expect_obj or {}).items():\n'
        '            if obj.get(k) != v:\n'
        '                raise BackupRefusal("IDENTITY_MISMATCH",\n'
        '                                    f"sentinel field {k}={obj.get(k)!r} != {v!r}")\n',
        '        for k, v in (expect_obj or {}).items():\n'
        '            if False and obj.get(k) != v:\n'
        '                raise BackupRefusal("IDENTITY_MISMATCH",\n'
        '                                    f"sentinel field {k}={obj.get(k)!r} != {v!r}")\n',
    )
    src = src.replace(
        '    if ident is not None and not isinstance(ident, dict):\n'
        '        raise BackupRefusal("BAD_CONFIG", f"targets.{kind}.identity is not an object")\n',
        '    if False and ident is not None and not isinstance(ident, dict):\n'
        '        raise BackupRefusal("BAD_CONFIG", f"targets.{kind}.identity is not an object")\n',
    )
    src = src.replace(
        '    if not isinstance(obj, dict):\n'
        '        raise BackupRefusal("BAD_CONFIG", f"{p} is not a JSON object")\n',
        '    if False and not isinstance(obj, dict):\n'
        '        raise BackupRefusal("BAD_CONFIG", f"{p} is not a JSON object")\n',
    )
    src = src.replace(
        '    if not isinstance(targets, dict):\n'
        '        raise BackupRefusal("BAD_CONFIG", f"{p} has no \'targets\' object")\n',
        '    if False and not isinstance(targets, dict):\n'
        '        raise BackupRefusal("BAD_CONFIG", f"{p} has no \'targets\' object")\n',
    )
    return src


def _strip_r2(src: str) -> str:
    src = src.replace(
        '            if not isinstance(val, str) or not val.strip():\n'
        '                raise BackupRefusal("BAD_CREDENTIALS", f"field {name!r} is empty or not a string")\n',
        '            if False and (not isinstance(val, str) or not val.strip()):\n'
        '                raise BackupRefusal("BAD_CREDENTIALS", f"field {name!r} is empty or not a string")\n',
    )
    src = src.replace(
        '    if not isinstance(obj, dict):\n'
        '        raise BackupRefusal("BAD_CREDENTIALS", f"{p} is not a JSON object")\n',
        '    if False and not isinstance(obj, dict):\n'
        '        raise BackupRefusal("BAD_CREDENTIALS", f"{p} is not a JSON object")\n',
    )
    return src


def _expect_kind(ran, failed, name, fn, want):
    ran.append(name)
    try:
        fn()
        failed.append(f"{name}:did_not_raise")
    except Exception as e:                                            # noqa: BLE001
        kind = getattr(e, "kind", None)
        if kind != want:
            failed.append(f"{name}:{kind or type(e).__name__}")


def main() -> int:
    failed = []
    ran = []
    sys.path.insert(0, str(HERE))
    mounts_src = (OLD / "cosmos_backup_mounts.py").read_text(encoding="utf-8")
    r2_src = (OLD / "cosmos_backup_r2.py").read_text(encoding="utf-8")
    stripped_m = _strip_mounts(mounts_src)
    stripped_r = _strip_r2(r2_src)
    if stripped_m == mounts_src:
        failed.append("mounts:strip_noop")
    if stripped_r == r2_src:
        failed.append("r2:strip_noop")
    old_m = _exec(OLD / "cosmos_backup_mounts.py", "mnt_old_r4", stripped_m)
    old_r = _exec(OLD / "cosmos_backup_r2.py", "r2_old_r4", stripped_r)

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_failold_r4_"))
    try:
        src = tmp / "src"
        src.mkdir()
        (src / "a.txt").write_text("a\n", encoding="utf-8")
        dest = tmp / "gdx"
        dest.mkdir()

        probe = old_m.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest): "vol:ES3", str(dest.resolve()): "vol:ES3",
        })
        probe.models[str(dest)] = "WRONG-MODEL"
        cfg = tmp / "backup_targets.json"
        cfg.write_text(json.dumps({
            "schema": old_m.SCHEMA,
            "targets": {"es3": {"dest": str(dest),
                                "identity": {"kind": "model",
                                             "value": old_m.ES3_MODEL}}},
        }), encoding="utf-8")
        _expect_kind(ran, failed, "model_IDENTITY_MISMATCH",
                     lambda: old_m.bind("es3", config_path=cfg, probe=probe),
                     "IDENTITY_MISMATCH")

        dest2 = tmp / "odx"
        dest2.mkdir()
        (dest2 / ".cosmos-backup-target.json").write_text(
            json.dumps({"kind": "gdx"}), encoding="utf-8")
        probe2 = old_m.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest2): "vol:ODX", str(dest2.resolve()): "vol:ODX",
        })
        cfg.write_text(json.dumps({
            "schema": old_m.SCHEMA,
            "targets": {"odx": {"dest": str(dest2),
                                "identity": {"kind": "sentinel",
                                             "expect": {"kind": "odx"}}}},
        }), encoding="utf-8")
        _expect_kind(ran, failed, "sentinel_IDENTITY_MISMATCH",
                     lambda: old_m.bind("odx", config_path=cfg, probe=probe2),
                     "IDENTITY_MISMATCH")

        probe3 = old_m.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest): "vol:GDX", str(dest.resolve()): "vol:GDX",
        })
        cfg.write_text(json.dumps({
            "schema": old_m.SCHEMA,
            "targets": {"gdx": {"dest": str(dest),
                                "identity": "volume_serial"}},
        }), encoding="utf-8")
        _expect_kind(ran, failed, "ident_not_obj_BAD_CONFIG",
                     lambda: old_m.bind("gdx", config_path=cfg, probe=probe3),
                     "BAD_CONFIG")

        arr = tmp / "array.json"
        arr.write_text("[]", encoding="utf-8")
        _expect_kind(ran, failed, "cfg_array_BAD_CONFIG",
                     lambda: old_m.load_config(arr),
                     "BAD_CONFIG")

        lst = tmp / "targets_list.json"
        lst.write_text(json.dumps({"schema": old_m.SCHEMA, "targets": ["gdx"]}),
                       encoding="utf-8")
        _expect_kind(ran, failed, "targets_list_BAD_CONFIG",
                     lambda: old_m.load_config(lst),
                     "BAD_CONFIG")

        _expect_kind(ran, failed, "empty_field_BAD_CREDENTIALS",
                     lambda: old_r.R2Credentials("acct", "AKIAFAKE", "   ", "b"),
                     "BAD_CREDENTIALS")

        cred_true = tmp / "creds.json"
        cred_true.write_text("true", encoding="utf-8")
        _expect_kind(ran, failed, "cred_true_BAD_CREDENTIALS",
                     lambda: old_r.load_credentials(cred_true),
                     "BAD_CREDENTIALS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out = {
        "schema": "cosmos-fail-against-old/1",
        "what": "round4 backup pins FAIL against stripped predecessor",
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
