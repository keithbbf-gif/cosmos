#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite F-43 leftovers against the incumbent (pre SOURCE_MUTATED / do_retire).

Gap 3 (COVERAGE.md): a torn snapshot still seals MANIFEST / VERIFIED.
Gap 5: nothing retires old sets; no do_retire; CLI has no retire verb.

This script mutates a source file AFTER it has been stored (so copy-hash
still matches) and BEFORE the manifest is sealed. The incumbent seals
RESTORE-grade VERIFIED over that mix. Output:
`builds/backup/_bite_f43_mutate_retire.json`.

    py -3.14 builds/backup/_bite_f43_mutate_retire.py
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import cosmos_backup as cb

HERE = Path(__file__).resolve().parent
OUT = HERE / "_bite_f43_mutate_retire.json"
KEY = b"test-hmac-key-not-a-real-secret"


def _tree():
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite_f43_"))
    src = tmp / "src"
    (src / "nested").mkdir(parents=True)
    (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
    (src / "nested" / "b.bin").write_bytes(b"bravo")
    dest = tmp / "dest"
    dest.mkdir()
    return tmp, src, dest


def bite_torn_snapshot():
    tmp, src, dest = _tree()
    orig = cb.LocalDirTarget.store
    mutated = {"rel": None}

    def after_store(self, rel, src_path):
        orig(self, rel, src_path)
        if mutated["rel"] is None:
            mutated["rel"] = rel
            Path(src_path).write_bytes(b"MUTATED-AFTER-COPY\n")

    cb.LocalDirTarget.store = after_store
    sealed = False
    kind = None
    crash = None
    manifest_exists = False
    try:
        set_dir = cb.do_backup(src, dest, key=KEY)
        sealed = True
        manifest_exists = (set_dir / cb.MANIFEST_NAME).is_file()
        kind = "BACKUP_OK"
    except cb.BackupRefusal as e:
        kind = e.kind
        sealed = False
        sets = list(dest.glob("src-*"))
        if sets:
            manifest_exists = (sets[0] / cb.MANIFEST_NAME).is_file()
    except Exception as e:  # noqa: BLE001
        crash = type(e).__name__
        kind = None
    finally:
        cb.LocalDirTarget.store = orig
        shutil.rmtree(tmp, True)
    return {
        "torn_snapshot_sealed": sealed,
        "torn_snapshot_kind": kind,
        "torn_snapshot_crash": crash,
        "torn_snapshot_manifest_exists": manifest_exists,
        "torn_snapshot_mutated_rel": mutated["rel"],
    }


def bite_retire_absent():
    return {
        "has_do_retire": hasattr(cb, "do_retire"),
        "has_list_backup_sets": hasattr(cb, "list_backup_sets"),
        "cli_has_retire": "retire" in (getattr(cb, "__doc__", "") or ""),
    }


def bite_cli_subparser():
    """Parse --help via main's argparse by inspecting a dry parse error.

    Safer: read the source of the staged/current module for add_parser('retire').
    """
    text = Path(cb.__file__).read_text(encoding="utf-8")
    return {
        "source_has_add_parser_retire": 'add_parser("retire"' in text
        or "add_parser('retire'" in text,
        "source_has_do_retire_def": "def do_retire(" in text,
        "source_has_SOURCE_MUTATED": "SOURCE_MUTATED" in text,
    }


def main() -> int:
    torn = bite_torn_snapshot()
    retire = bite_retire_absent()
    cli = bite_cli_subparser()
    rec = {
        "schema": "cosmos-bite/1",
        "what": "F-43 gap 3 torn snapshot seals; gap 5 no retire",
        "module": str(Path(cb.__file__).resolve()),
        **torn,
        **retire,
        **cli,
    }
    rec["all_bite"] = bool(
        rec["torn_snapshot_sealed"]
        and rec["torn_snapshot_kind"] == "BACKUP_OK"
        and rec["torn_snapshot_manifest_exists"]
        and rec["torn_snapshot_crash"] is None
        and not rec["has_do_retire"]
        and not rec["has_list_backup_sets"]
        and not rec["source_has_do_retire_def"]
        and not rec["source_has_add_parser_retire"]
        and not rec["source_has_SOURCE_MUTATED"]
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
