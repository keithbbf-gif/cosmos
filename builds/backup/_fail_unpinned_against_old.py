#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the new unpinned-refusal pins against STRIPPED in-memory copies.

The new pins MUST FAIL here. A green run against stripped code means the
tests are not actually asking the claim. Output:
`builds/backup/_fail_unpinned_against_old.json`.

Stripped modules keep the original ``__file__`` so resolvers still find
``cosmos/cosmos_paths.py``. Nothing is written under the live tree.

    py -3.14 builds/backup/_fail_unpinned_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_against_old.json"


def _exec_stripped(src: str, orig_path: Path, name: str):
    """Exec stripped source with the original __file__ so relative resolvers work."""
    mod = types.ModuleType(name)
    mod.__file__ = str(orig_path)
    sys.modules[name] = mod
    exec(compile(src, str(orig_path), "exec"), mod.__dict__)
    return mod


def _load_tests(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _retarget_kind(src: str, kind: str) -> str:
    """BackupRefusal(KIND) becomes BackupRefusal(STRIPPED_KIND) — still raises,
    but not the kind the new pin names."""
    return src.replace(f'"{kind}"', f'"STRIPPED_{kind}"')


def main() -> int:
    for name in ("cosmos_backup", "cosmos_backup_r2", "cosmos_offsite_clock",
                 "cosmos_backup_mounts", "test_cosmos_backup",
                 "test_offsite_clock", "test_cosmos_backup_r2",
                 "test_backup_mounts"):
        sys.modules.pop(name, None)

    sys.path.insert(0, str(HERE))

    src_bk = (HERE / "cosmos_backup.py").read_text(encoding="utf-8")
    src_bk = _retarget_kind(src_bk, "SCRATCH_NOT_EMPTY")
    src_bk = _retarget_kind(src_bk, "COPY_IO_ERROR")
    _exec_stripped(src_bk, HERE / "cosmos_backup.py", "cosmos_backup")

    src_r2 = (HERE / "cosmos_backup_r2.py").read_text(encoding="utf-8")
    src_r2 = _retarget_kind(src_r2, "R2_UNREACHABLE")
    _exec_stripped(src_r2, HERE / "cosmos_backup_r2.py", "cosmos_backup_r2")

    src_oc = (HERE / "cosmos_offsite_clock.py").read_text(encoding="utf-8")
    src_oc = _retarget_kind(src_oc, "BAD_SCOPES")
    _exec_stripped(src_oc, HERE / "cosmos_offsite_clock.py", "cosmos_offsite_clock")

    src_m = (HERE / "cosmos_backup_mounts.py").read_text(encoding="utf-8")
    src_m = src_m.replace(
        'f"identity.kind {kind!r} is not volume_serial|volume_label|"',
        'f"STRIPPED identity.kind {kind!r}"',
    )
    src_m = src_m.replace(
        '        raise BackupRefusal("BAD_CONFIG",\n'
        '                            f"STRIPPED identity.kind {kind!r}"\n'
        '                            "model|sentinel")',
        '        return\n',
    )
    # CRLF-safe fallback: drop the unknown-kind refusal by kind-string retarget
    # if the block replace did not take.
    if 'identity.kind {kind!r} is not volume_serial' in src_m:
        src_m = _retarget_kind(src_m, "BAD_CONFIG")
    _exec_stripped(src_m, HERE / "cosmos_backup_mounts.py", "cosmos_backup_mounts")

    tmod = _load_tests(HERE / "test_cosmos_backup.py", "test_cosmos_backup_against_old")
    omod = _load_tests(HERE / "test_offsite_clock.py", "test_offsite_clock_against_old")
    rmod = _load_tests(HERE / "test_cosmos_backup_r2.py", "test_cosmos_backup_r2_against_old")
    mmod = _load_tests(HERE / "test_backup_mounts.py", "test_backup_mounts_against_old")

    cases = [
        (tmod.TestFailClosed("test_nonempty_scratch_refuses"),
         "test_nonempty_scratch_refuses"),
        (tmod.TestUnpinnedRefusals("test_copy_missing_src_is_COPY_IO_ERROR"),
         "test_copy_missing_src_is_COPY_IO_ERROR"),
        (omod.TestScopeDeclaration("test_malformed_scopes_json_is_BAD_SCOPES"),
         "test_malformed_scopes_json_is_BAD_SCOPES"),
        (omod.TestScopeDeclaration("test_empty_scopes_list_is_BAD_SCOPES_not_a_silent_no_op"),
         "test_empty_scopes_list_is_BAD_SCOPES_not_a_silent_no_op"),
        (omod.TestScopeDeclaration("test_scope_missing_source_is_BAD_SCOPES"),
         "test_scope_missing_source_is_BAD_SCOPES"),
        (omod.TestScopeDeclaration("test_scope_missing_name_is_BAD_SCOPES"),
         "test_scope_missing_name_is_BAD_SCOPES"),
        (rmod.TestSecretNeverEscapes(
            "test_urlopen_OSError_is_R2_UNREACHABLE_not_an_untyped_crash"),
         "test_urlopen_OSError_is_R2_UNREACHABLE_not_an_untyped_crash"),
        (mmod.TestMountAndIdentity("test_unknown_identity_kind_is_BAD_CONFIG"),
         "test_unknown_identity_kind_is_BAD_CONFIG"),
    ]

    suite = unittest.TestSuite()
    ran_names = []
    for test, name in cases:
        suite.addTest(test)
        ran_names.append(name)

    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    failed_names = sorted(
        [t.id().rsplit(".", 1)[-1] for t, _ in result.failures]
        + [t.id().rsplit(".", 1)[-1] for t, _ in result.errors]
    )
    rec = {
        "schema": "cosmos-bite/1",
        "what": "new unpinned-refusal pins FAIL against stripped predecessors",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "failed_names": failed_names,
        "ran_names": ran_names,
        "all_new_pins_failed": (
            result.testsRun == len(ran_names)
            and (len(result.failures) + len(result.errors)) == result.testsRun
            and result.testsRun > 0
        ),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
