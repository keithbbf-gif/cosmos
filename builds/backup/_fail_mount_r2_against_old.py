#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New mount-clock R2 pins MUST FAIL against the staged predecessor.

Staged at builds/backup/_delme/predispose_mount_clock_r2_20260831T183114Z/

Predecessor (measured): cosmos_mount_clock tick() drives gdx/odx/es3 from
backup_targets.json only. It has no r2_transport_factory, never emits a
target_kind=r2 row, and selfcheck injects dests={"gdx": dest} with no
MemoryTransport. The nightly 03:00 task therefore cannot push to R2.

    py -3.14 builds/backup/_fail_mount_r2_against_old.py
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_mount_r2_against_old.json"
OLD = HERE / "_delme" / "predispose_mount_clock_r2_20260831T183114Z"

NEW_PINS = (
    "tick_has_r2_transport_factory_param",
    "selfcheck_passes_r2_override",
    "scheduled_tick_emits_r2_row",
    "absent_credential_is_NO_CREDENTIALS",
    "injected_memory_transport_pushes_r2",
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    sys.path.insert(0, str(HERE))
    if not (OLD / "cosmos_mount_clock.py").is_file():
        raise SystemExit(f"missing predecessor {OLD}")
    old = _load(OLD / "cosmos_mount_clock.py", "old_mount_clock_r2")
    import cosmos_backup_mounts as mounts  # noqa: E402
    import cosmos_backup_r2 as r2          # noqa: E402

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_fail_mount_r2_"))
    pins = {k: False for k in NEW_PINS}
    detail: dict = {}
    try:
        root = tmp / "live"
        root.mkdir()
        (root / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-test",
                        "schema_version": 1}), encoding="utf-8")
        for role in ("logs", "config", "work", "state"):
            (root / role).mkdir()
        src = tmp / "src"
        (src / "sub").mkdir(parents=True)
        (src / "a.txt").write_text("alpha\n", encoding="utf-8")
        (src / "sub" / "b.txt").write_text("bravo\n", encoding="utf-8")
        dest = tmp / "gdx"
        dest.mkdir()
        probe = mounts.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest): "vol:GDX", str(dest.resolve()): "vol:GDX",
        })
        paths = old.CosmosPaths(root)
        cfg = paths.config(old.CONFIG_NAME)
        scopes = [{"name": "src", "source": str(src),
                   "excludes": (".git", "__pycache__")}]
        cfg.write_text(json.dumps({
            "schema": mounts.SCHEMA,
            "targets": {"gdx": {"dest": str(dest)},
                        "odx": {"dest": ""},
                        "es3": {"dest": ""}},
        }), encoding="utf-8")

        sig = inspect.signature(old.tick)
        pins["tick_has_r2_transport_factory_param"] = (
            "r2_transport_factory" in sig.parameters)

        sc_src = inspect.getsource(old.selfcheck)
        pins["selfcheck_passes_r2_override"] = (
            "r2_credentials_override" in sc_src
            or "MemoryTransport" in sc_src)

        rec = old.tick(paths, scopes, cfg, probe=probe)
        kinds = [r.get("target_kind") for r in rec.get("targets") or []]
        detail["scheduled_kinds"] = kinds
        detail["scheduled_state"] = rec.get("state")
        r2_rows = [r for r in (rec.get("targets") or [])
                   if r.get("target_kind") == "r2"]
        pins["scheduled_tick_emits_r2_row"] = bool(r2_rows)
        pins["absent_credential_is_NO_CREDENTIALS"] = (
            bool(r2_rows) and r2_rows[0].get("kind") == "NO_CREDENTIALS")

        try:
            creds = r2.R2Credentials(
                "selfcheckaccount", r2.SELFCHECK_ID, r2.SELFCHECK_ID,
                "selfcheck-bucket")
            rec2 = old.tick(
                paths, scopes, cfg, probe=probe, dests={"gdx": dest},
                r2_transport_factory=r2.MemoryTransport,
                r2_credentials_override=creds, force=True)
            r2b = [r for r in (rec2.get("targets") or [])
                   if r.get("target_kind") == "r2"]
            pins["injected_memory_transport_pushes_r2"] = (
                bool(r2b) and r2b[0].get("state") == "PUSHED"
                and r2b[0].get("readback_verified") == 2)
            detail["injected_r2"] = r2b[0] if r2b else rec2.get("kind")
        except TypeError as e:
            detail["injected_typeerror"] = str(e)[:200]
            pins["injected_memory_transport_pushes_r2"] = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec_out = {
        "what": "new mount-clock R2 pins FAIL against predecessor (gdx/odx/es3 only)",
        "predecessor": str(OLD),
        "pins": pins,
        "failed_pins": [k for k in NEW_PINS if pins[k] is False],
        "passed_pins": [k for k in NEW_PINS if pins[k] is True],
        "detail": detail,
    }
    rec_out["all_new_pins_failed"] = all(pins[k] is False for k in NEW_PINS)
    OUT.write_text(json.dumps(rec_out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_new_pins_failed": rec_out["all_new_pins_failed"],
        "failed": rec_out["failed_pins"],
        "passed": rec_out["passed_pins"],
    }, indent=2))
    return 0 if rec_out["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
