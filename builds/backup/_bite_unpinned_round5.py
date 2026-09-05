#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-5 unpinned backup refusals against CURRENT (pre-fix) code.

Kinds that sit next to a typed seal / artifact path and still crash untyped:

  * check_seal(obj) when obj is a JSON array            — AttributeError
  * check_seal when seal is a string, not an object     — AttributeError
  * LocalDirTarget.get_artifact of `{not json`          — JSONDecodeError
  * LocalDirTarget.get_artifact of `[]`                 — returns a list
  * R2Target.get_artifact of `{not json`                — JSONDecodeError

Expected (and required before belief): all_bite == true.

    py -3.14 builds/backup/_bite_unpinned_round5.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round5.json"

import cosmos_backup as cb                                            # noqa: E402
import cosmos_backup_r2 as r2                                         # noqa: E402


def _catch(fn):
    try:
        got = fn()
        return {"kind": None, "crash": None, "returned": type(got).__name__,
                "value_preview": str(got)[:40]}
    except cb.BackupRefusal as e:
        return {"kind": e.kind, "crash": None, "returned": None}
    except Exception as e:                                            # noqa: BLE001
        return {"kind": None, "crash": type(e).__name__, "returned": None}


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "round5 unpinned backup refusals — current vs claimed"}
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite5_"))
    try:
        a = _catch(lambda: cb.check_seal([]))
        rec["obj_array_old_kind"] = a["kind"]
        rec["obj_array_old_crash"] = a["crash"]

        sealed = cb.seal({"n": 1})
        bad = dict(sealed)
        bad["seal"] = "not-an-object"
        b = _catch(lambda: cb.check_seal(bad))
        rec["seal_str_old_kind"] = b["kind"]
        rec["seal_str_old_crash"] = b["crash"]

        set_dir = tmp / "set"
        (set_dir / cb.DATA_DIR).mkdir(parents=True)
        (set_dir / "a.txt").write_text("x", encoding="utf-8")
        (set_dir / cb.MANIFEST_NAME).write_text("{not json", encoding="utf-8")
        target = cb.LocalDirTarget(set_dir)
        c = _catch(lambda: target.get_artifact(cb.MANIFEST_NAME))
        rec["local_garbage_old_kind"] = c["kind"]
        rec["local_garbage_old_crash"] = c["crash"]

        (set_dir / cb.MANIFEST_NAME).write_text("[]", encoding="utf-8")
        d = _catch(lambda: target.get_artifact(cb.MANIFEST_NAME))
        rec["local_array_old_kind"] = d["kind"]
        rec["local_array_old_crash"] = d["crash"]
        rec["local_array_old_returned"] = d.get("returned")

        tp = r2.MemoryTransport()
        creds = r2.R2Credentials("acct1234", "AKIAFAKE0001",
                                 "SECRET-VALUE-THAT-MUST-NEVER-BE-RENDERED",
                                 "cosmos-bucket")
        rt = r2.R2Target(creds, "cosmos", tp)
        rt.put_artifact(cb.MANIFEST_NAME, {"n": 1})
        rec["r2_object_keys"] = list(tp.objects)
        # Overwrite the stored object in place — same key the GET will hit.
        for k in list(tp.objects):
            tp.objects[k] = b"{not json"
        e = _catch(lambda: rt.get_artifact(cb.MANIFEST_NAME))
        rec["r2_garbage_old_kind"] = e["kind"]
        rec["r2_garbage_old_crash"] = e["crash"]

        for k in list(tp.objects):
            tp.objects[k] = b"true"
        f = _catch(lambda: rt.get_artifact(cb.MANIFEST_NAME))
        rec["r2_true_old_kind"] = f["kind"]
        rec["r2_true_old_crash"] = f["crash"]
        rec["r2_true_old_returned"] = f.get("returned")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = (
        rec.get("obj_array_old_kind") is None
        and rec.get("obj_array_old_crash") == "AttributeError"
        and rec.get("seal_str_old_kind") is None
        and rec.get("seal_str_old_crash") == "AttributeError"
        and rec.get("local_garbage_old_kind") is None
        and rec.get("local_garbage_old_crash") == "JSONDecodeError"
        and rec.get("local_array_old_kind") is None
        and rec.get("local_array_old_returned") == "list"
        and rec.get("r2_garbage_old_kind") is None
        and rec.get("r2_garbage_old_crash") == "JSONDecodeError"
        and rec.get("r2_true_old_kind") is None
        and rec.get("r2_true_old_returned") == "bool"
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
