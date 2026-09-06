#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""session-tools Slice-1 — scan + load (cowork wrap, grok_tui).

    py -3.14 builds/session-tools/session_tools.py scan --family cowork --store <dir>
    py -3.14 builds/session-tools/session_tools.py load --id cow-abc --store <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

from adapters import cowork, grok_tui  # noqa: E402
from refusals import SessionToolsRefusal  # noqa: E402
import verbs  # noqa: E402
from schema import RESULT_SCHEMA, encode_jsonl, view, write_canonical  # noqa: E402

FAMILIES = {"cowork": cowork, "grok_tui": grok_tui}
DEFAULT_FAMS = ("cowork", "grok_tui")


def _result(verb: str, kind: str, gate, legal_omitted=0, **extra) -> dict:
    rec = {"schema": RESULT_SCHEMA, "verb": verb, "kind": kind,
           "gate": gate, "legal_omitted": legal_omitted}
    rec.update(extra)
    return rec


def cmd_scan(fams: list[str], store: Path | None, root: str | None) -> dict:
    if root is None and store is None:
        raise SessionToolsRefusal("GUESSED_ROOT", "--store or --root is required")
    families = []
    omitted = 0
    for name in fams:
        mod = FAMILIES.get(name)
        if mod is None:
            families.append({"family": name, "status": "UNMEASURED", "path": None, "n": None})
            continue
        if store is None:
            raise SessionToolsRefusal("NO_STORE", f"--store required for {name} this slice")
        row = mod.scan(store)
        omitted += int(row.get("n_legal") or 0)
        families.append(row)
    return _result("scan", "OK", {"families": families}, legal_omitted=omitted, families=families)


def cmd_load(rec_id: str, store: Path, out_dir: Path | None) -> dict:
    if rec_id.startswith("cow-"):
        fam = "cowork"
    elif rec_id.startswith("grok-"):
        fam = "grok_tui"
    else:
        raise SessionToolsRefusal("NOT_FOUND", rec_id)
    h, turns = FAMILIES[fam].load(store, rec_id)
    kind = "TRUNCATED" if h.pop("_truncated", False) else "OK"
    payload = encode_jsonl(h, turns)
    written = None
    if out_dir is not None:
        written = write_canonical(out_dir, h["id"], payload)
    gate = {
        "schema": h["schema"],
        "n_turns": len(turns),
        "id": h["id"],
        "source_sha": (h.get("sources") or [{}])[0].get("sha256"),
    }
    if written:
        gate["out_sha"] = written["sha"]
        gate["out_len"] = written["len"]
    return _result("load", kind, gate, legal_omitted=0, record=view(h, turns), written=written)


def _loader(rec_id: str):
    if rec_id.startswith("cow-"):
        return cowork.load
    if rec_id.startswith("grok-"):
        return grok_tui.load
    raise SessionToolsRefusal("NOT_FOUND", rec_id)


def cmd_convert(rec_id: str, store: Path, out_dir: Path, force: bool) -> dict:
    gate = verbs.convert(_loader(rec_id), rec_id, store, out_dir, force=force)
    return _result("convert", "OK", gate)


def cmd_diff(left: Path, right: Path) -> dict:
    gate = verbs.diff_payloads(left.read_bytes(), right.read_bytes())
    return _result("diff", "OK", gate)


def cmd_check(what: str, path: Path, chair: str | None) -> dict:
    if what == "catalog":
        gate = verbs.check_catalog(path)
    elif what == "sqlite":
        gate = verbs.check_sqlite(path)
    elif what == "seed":
        gate = verbs.check_seed(path)
    elif what == "sit":
        gate = verbs.check_sit(path, chair or "ccr")
    else:
        raise SessionToolsRefusal("UNMEASURED", what)
    return _result("check", gate.get("kind") or "VERIFIED", gate)


def cmd_anonymize(rec_id: str, store: Path, out_dir: Path) -> dict:
    gate = verbs.anonymize(_loader(rec_id), rec_id, store, out_dir)
    return _result("anonymize", "OK", gate)


def cmd_crash_recover(target: Path, bak: Path | None, stage: Path) -> dict:
    gate = verbs.crash_recover(target, bak, stage)
    return _result("crash-recover", "OK", gate)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="session_tools.py")
    p.add_argument("--root", default=None, help="COSMOS live root (required if no --store)")
    p.add_argument("--json", action="store_true", default=True)
    sub = p.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan")
    sc.add_argument("--family", action="append", dest="families")
    sc.add_argument("--store", default=None)
    ld = sub.add_parser("load")
    ld.add_argument("--id", required=True)
    ld.add_argument("--store", required=True)
    ld.add_argument("--out", default=None, help="write {id}.ctr.jsonl + .decl.json")
    cv = sub.add_parser("convert")
    cv.add_argument("--id", required=True)
    cv.add_argument("--store", required=True)
    cv.add_argument("--out-dir", required=True)
    cv.add_argument("--force", action="store_true")
    df = sub.add_parser("diff")
    df.add_argument("--left", required=True)
    df.add_argument("--right", required=True)
    ck = sub.add_parser("check")
    ck.add_argument("--what", required=True, choices=["catalog", "sqlite", "seed", "sit"])
    ck.add_argument("--path", required=True)
    ck.add_argument("--sit", dest="chair", default="ccr")
    an = sub.add_parser("anonymize")
    an.add_argument("--id", required=True)
    an.add_argument("--store", required=True)
    an.add_argument("--out-dir", required=True)
    cr = sub.add_parser("crash-recover")
    cr.add_argument("--target", required=True)
    cr.add_argument("--bak", default=None)
    cr.add_argument("--stage", default=str(REPO / "_delme" / "session-tools"))
    a = p.parse_args(argv)
    store = Path(a.store) if getattr(a, "store", None) else None
    try:
        if a.cmd == "scan":
            fams = a.families or list(DEFAULT_FAMS)
            rec = cmd_scan(fams, store, a.root)
        elif a.cmd == "load":
            rec = cmd_load(a.id, store, Path(a.out) if a.out else None)
        elif a.cmd == "convert":
            rec = cmd_convert(a.id, Path(a.store), Path(a.out_dir), a.force)
        elif a.cmd == "diff":
            rec = cmd_diff(Path(a.left), Path(a.right))
        elif a.cmd == "check":
            rec = cmd_check(a.what, Path(a.path), getattr(a, "chair", None))
        elif a.cmd == "anonymize":
            rec = cmd_anonymize(a.id, Path(a.store), Path(a.out_dir))
        else:
            rec = cmd_crash_recover(Path(a.target), Path(a.bak) if a.bak else None, Path(a.stage))
    except SessionToolsRefusal as e:
        rec = _result(a.cmd, e.kind, {"detail": str(e)}, legal_omitted=int(e.kind == "LEGAL_OMITTED"))
        print(json.dumps(rec, indent=2))
        return 2 if e.kind != "LEGAL_OMITTED" else 2
    print(json.dumps(rec, indent=2))
    return 0 if rec["kind"] in ("OK", "TRUNCATED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
