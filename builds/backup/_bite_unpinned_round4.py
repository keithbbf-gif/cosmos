#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-4 unpinned backup refusals against STRIPPED current code.

Kinds that sit in the raise set and in prose, and that tests never named:

  * identity.kind=model mismatch  — IDENTITY_UNMEASURED and match were
    pinned; a measured-but-wrong model bound (existence as identity).
  * identity.kind=sentinel field mismatch — missing and match were pinned;
    a present sentinel with the wrong field bound.
  * targets.<kind>.identity is a string, not an object — BAD_CONFIG.
  * backup_targets.json is a JSON array — BAD_CONFIG (else AttributeError).
  * targets is a list, not an object — BAD_CONFIG (else AttributeError).
  * R2Credentials empty/whitespace field — BAD_CREDENTIALS.
  * credential JSON is an array — BAD_CREDENTIALS (else TypeError).

Expected (and required before belief): all_bite == true.

    py -3.14 builds/backup/_bite_unpinned_round4.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round4.json"


def _exec(path: Path, name: str, src: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(src, str(path), "exec"), mod.__dict__)
    return mod


def _strip_mounts(src: str) -> str:
    # Measured-but-wrong model: drop the mismatch raise so bind succeeds.
    src = src.replace(
        '        if got != str(expect):\n'
        '            raise BackupRefusal("IDENTITY_MISMATCH",\n'
        '                                f"{spec[\'kind\']} model {got!r} != declared {expect!r}")\n',
        '        if False and got != str(expect):\n'
        '            raise BackupRefusal("IDENTITY_MISMATCH",\n'
        '                                f"{spec[\'kind\']} model {got!r} != declared {expect!r}")\n',
    )
    # Sentinel field mismatch: drop the per-field raise.
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


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "round4 unpinned backup refusals — stripped current vs claimed"}
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite4_"))
    try:
        mounts_src = (HERE / "cosmos_backup_mounts.py").read_text(encoding="utf-8")
        r2_src = (HERE / "cosmos_backup_r2.py").read_text(encoding="utf-8")
        stripped_m = _strip_mounts(mounts_src)
        stripped_r = _strip_r2(r2_src)
        rec["mounts_stripped"] = stripped_m != mounts_src
        rec["r2_stripped"] = stripped_r != r2_src
        rec["n_mounts_edits"] = mounts_src.count("if False")  # baseline 0
        rec["strip_model_ok"] = "if False and got != str(expect):" in stripped_m
        rec["strip_sentinel_ok"] = "if False and obj.get(k) != v:" in stripped_m
        rec["strip_ident_obj_ok"] = "if False and ident is not None" in stripped_m
        rec["strip_cfg_obj_ok"] = "if False and not isinstance(obj, dict):" in stripped_m
        rec["strip_targets_ok"] = "if False and not isinstance(targets, dict):" in stripped_m
        rec["strip_empty_field_ok"] = "if False and (not isinstance(val, str)" in stripped_r
        rec["strip_cred_obj_ok"] = "if False and not isinstance(obj, dict):" in stripped_r

        old_m = _exec(HERE / "cosmos_backup_mounts.py", "mnt_bite4", stripped_m)
        old_r = _exec(HERE / "cosmos_backup_r2.py", "r2_bite4", stripped_r)

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
        try:
            got = old_m.bind("es3", config_path=cfg, probe=probe)
            rec["model_mismatch_old_kind"] = None
            rec["model_mismatch_old_bound"] = str(got) == str(dest)
            rec["model_mismatch_old_crash"] = None
        except old_m.BackupRefusal as e:
            rec["model_mismatch_old_kind"] = e.kind
            rec["model_mismatch_old_bound"] = False
            rec["model_mismatch_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["model_mismatch_old_kind"] = None
            rec["model_mismatch_old_bound"] = False
            rec["model_mismatch_old_crash"] = type(e).__name__

        dest2 = tmp / "odx"
        dest2.mkdir()
        sent = dest2 / ".cosmos-backup-target.json"
        sent.write_text(json.dumps({"kind": "gdx"}), encoding="utf-8")
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
        try:
            got = old_m.bind("odx", config_path=cfg, probe=probe2)
            rec["sentinel_mismatch_old_kind"] = None
            rec["sentinel_mismatch_old_bound"] = str(got) == str(dest2)
            rec["sentinel_mismatch_old_crash"] = None
        except old_m.BackupRefusal as e:
            rec["sentinel_mismatch_old_kind"] = e.kind
            rec["sentinel_mismatch_old_bound"] = False
            rec["sentinel_mismatch_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["sentinel_mismatch_old_kind"] = None
            rec["sentinel_mismatch_old_bound"] = False
            rec["sentinel_mismatch_old_crash"] = type(e).__name__

        probe3 = old_m.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest): "vol:GDX", str(dest.resolve()): "vol:GDX",
        })
        cfg.write_text(json.dumps({
            "schema": old_m.SCHEMA,
            "targets": {"gdx": {"dest": str(dest),
                                "identity": "volume_serial"}},
        }), encoding="utf-8")
        try:
            got = old_m.bind("gdx", config_path=cfg, probe=probe3)
            rec["ident_not_obj_old_kind"] = None
            rec["ident_not_obj_old_bound"] = str(got) == str(dest)
            rec["ident_not_obj_old_crash"] = None
        except old_m.BackupRefusal as e:
            rec["ident_not_obj_old_kind"] = e.kind
            rec["ident_not_obj_old_bound"] = False
            rec["ident_not_obj_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["ident_not_obj_old_kind"] = None
            rec["ident_not_obj_old_bound"] = False
            rec["ident_not_obj_old_crash"] = type(e).__name__

        arr = tmp / "array.json"
        arr.write_text("[]", encoding="utf-8")
        try:
            old_m.load_config(arr)
            rec["cfg_array_old_kind"] = None
            rec["cfg_array_old_crash"] = None
        except old_m.BackupRefusal as e:
            rec["cfg_array_old_kind"] = e.kind
            rec["cfg_array_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["cfg_array_old_kind"] = None
            rec["cfg_array_old_crash"] = type(e).__name__

        lst = tmp / "targets_list.json"
        lst.write_text(json.dumps({"schema": old_m.SCHEMA, "targets": ["gdx"]}),
                       encoding="utf-8")
        try:
            cfg_obj = old_m.load_config(lst)
            old_m.spec_for("gdx", cfg_obj, None)
            rec["targets_list_old_kind"] = None
            rec["targets_list_old_crash"] = None
        except old_m.BackupRefusal as e:
            rec["targets_list_old_kind"] = e.kind
            rec["targets_list_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["targets_list_old_kind"] = None
            rec["targets_list_old_crash"] = type(e).__name__

        try:
            old_r.R2Credentials("acct", "AKIAFAKE", "   ", "bucket")
            rec["empty_field_old_kind"] = None
            rec["empty_field_old_accepted"] = True
            rec["empty_field_old_crash"] = None
        except old_r.BackupRefusal as e:
            rec["empty_field_old_kind"] = e.kind
            rec["empty_field_old_accepted"] = False
            rec["empty_field_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["empty_field_old_kind"] = None
            rec["empty_field_old_accepted"] = False
            rec["empty_field_old_crash"] = type(e).__name__

        # A JSON array still hits "missing field(s)" (typed). A JSON
        # non-object that is not a container (`true`) is the untyped hole.
        cred_true = tmp / "creds.json"
        cred_true.write_text("true", encoding="utf-8")
        try:
            old_r.load_credentials(cred_true)
            rec["cred_true_old_kind"] = None
            rec["cred_true_old_crash"] = None
        except old_r.BackupRefusal as e:
            rec["cred_true_old_kind"] = e.kind
            rec["cred_true_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["cred_true_old_kind"] = None
            rec["cred_true_old_crash"] = type(e).__name__
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = (
        rec.get("strip_model_ok") is True
        and rec.get("strip_sentinel_ok") is True
        and rec.get("strip_ident_obj_ok") is True
        and rec.get("strip_cfg_obj_ok") is True
        and rec.get("strip_targets_ok") is True
        and rec.get("strip_empty_field_ok") is True
        and rec.get("strip_cred_obj_ok") is True
        and rec.get("model_mismatch_old_bound") is True
        and rec.get("model_mismatch_old_kind") is None
        and rec.get("sentinel_mismatch_old_bound") is True
        and rec.get("sentinel_mismatch_old_kind") is None
        and rec.get("ident_not_obj_old_kind") is None
        and rec.get("ident_not_obj_old_crash") == "AttributeError"
        and rec.get("cfg_array_old_kind") is None
        and rec.get("cfg_array_old_crash") == "AttributeError"
        and rec.get("targets_list_old_kind") is None
        and rec.get("targets_list_old_crash") == "AttributeError"
        and rec.get("empty_field_old_accepted") is True
        and rec.get("empty_field_old_kind") is None
        and rec.get("cred_true_old_kind") is None
        and rec.get("cred_true_old_crash") is not None
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
