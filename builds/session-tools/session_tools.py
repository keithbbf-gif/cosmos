#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""session-tools Slice-1 — scan + load for cowork (catalog wrap) and grok_tui.

    py -3.14 builds/session-tools/session_tools.py scan --family cowork --store <fixture>
    py -3.14 builds/session-tools/session_tools.py scan --family grok_tui --store <fixture>
    py -3.14 builds/session-tools/session_tools.py load --id cow-... --store <fixture>
    py -3.14 builds/session-tools/session_tools.py load --id grok-... --store <fixture>

Canonical on disk (CCr dispose): {id}.ctr.jsonl + {id}.ctr.decl.json (sha-only).
load stdout is a JSON view of that JSONL inside cosmos-session-tools-result/1.

Does not write cosmos_kernel / ledger / sched / service. Does not bounce Core.
Does not re-ingest 666. Does not recode cowork_to_openwork.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from adapters import REJECT, UNMEASURED, get as get_adapter  # noqa: E402
from declared import read_verified, sha256_bytes, write_declared  # noqa: E402
from refusals import (  # noqa: E402
    GUESSED_ROOT, LEGAL_OMITTED, NO_STORE, NOT_A_KERNEL, SCHEMA_UNKNOWN,
    TRUNCATED, UNMEASURED as KIND_UNMEASURED, UNKNOWN, Refusal, ok, refuse,
)
from schema import (  # noqa: E402
    encode_jsonl, encode_turns_body, family_of_id, jsonl_paths,
    sidecar_payload, view,
)

PRODUCED_BY = "session-tools/1"
DEFAULT_FAMILIES = ("cowork", "grok_tui")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _families_from(vals: list[str] | None) -> list[str]:
    if not vals:
        return list(DEFAULT_FAMILIES)
    out: list[str] = []
    for v in vals:
        for part in str(v).split(","):
            p = part.strip()
            if p and p not in out:
                out.append(p)
    return out or list(DEFAULT_FAMILIES)


def _locator_or_guessed(store, root, verb: str) -> dict | None:
    """--store for vendor-only. --root when touching a COSMOS tree.
    Neither → GUESSED_ROOT (never default live/)."""
    if store:
        return None
    if root:
        return None
    return refuse(
        verb, GUESSED_ROOT,
        "--root is required when touching a COSMOS tree; "
        "pass --store for vendor-only scan/load (no guessed live path)",
        gate={},
    )


def _kernel_touch(argv: list[str]) -> dict | None:
    joined = " ".join(argv).lower()
    if "--write-ledger" in joined or "cosmos_kernel" in joined:
        return refuse("scan", NOT_A_KERNEL,
                      "session-tools is not a kernel writer")
    return None


def scan_family(family: str, store: Path | None) -> dict:
    if family in REJECT:
        return {
            "family": family, "status": "UNKNOWN", "path": None, "n": None,
            "n_legal": None, "bytes": None, "sample_ids": [],
            "detail": "not a transcript family",
        }
    if family in UNMEASURED:
        return {
            "family": family, "status": KIND_UNMEASURED,
            "path": UNMEASURED.get(family),
            "n": None, "n_legal": None, "bytes": None, "sample_ids": [],
        }
    adapter = get_adapter(family)
    if adapter is None:
        return {
            "family": family, "status": UNKNOWN, "path": str(store) if store else None,
            "n": None, "n_legal": None, "bytes": None, "sample_ids": [],
        }
    if store is None:
        raise Refusal(
            NO_STORE,
            f"{family}: --store required (will not guess recents n_shown=200 "
            f"or a live COSMOS path)",
            n=None,
        )
    rec = adapter.discover(store)
    rec["family"] = family
    rec.pop("hits", None)  # Hits stay internal; scan prints the family row
    return rec


def do_scan(families: list[str], store: Path | None) -> dict:
    rows = []
    first_refuse = None
    for fam in families:
        try:
            row = scan_family(fam, store)
        except Refusal as e:
            row = {
                "family": fam, "status": e.kind, "path": e.extra.get("path", str(store) if store else None),
                "n": e.extra.get("n"), "n_legal": None, "bytes": None,
                "sample_ids": [], "detail": e.detail,
            }
            if first_refuse is None:
                first_refuse = e
        rows.append(row)

    if len(families) == 1:
        row = rows[0]
        status = row.get("status")
        gate = {
            "n": row.get("n"),
            "n_legal": row.get("n_legal"),
            "path": row.get("path"),
            "sample_ids": row.get("sample_ids") or [],
        }
        legal_omitted = row.get("n_legal") or 0
        if status == "OK":
            return ok("scan", gate, legal_omitted=legal_omitted, families={families[0]: row})
        kind = status if status in (
            KIND_UNMEASURED, UNKNOWN, NO_STORE, GUESSED_ROOT,
        ) else (first_refuse.kind if first_refuse else status)
        return refuse("scan", kind, row.get("detail") or "",
                      legal_omitted=legal_omitted, gate=gate,
                      families={families[0]: row})

    families_map = {r["family"]: r for r in rows}
    any_ok = any(r.get("status") == "OK" for r in rows)
    gate = {r["family"]: {"n": r.get("n"), "n_legal": r.get("n_legal")} for r in rows}
    legal_omitted = sum(int(r["n_legal"]) for r in rows if r.get("n_legal"))
    if any_ok and all(r.get("status") in ("OK", KIND_UNMEASURED, UNKNOWN) or r.get("n") is not None for r in rows):
        # Mixed: still OK if at least one wired family scanned.
        if any(r.get("status") == "OK" for r in rows):
            return ok("scan", gate, legal_omitted=legal_omitted, families=families_map)
    if first_refuse:
        return refuse("scan", first_refuse.kind, first_refuse.detail,
                      legal_omitted=legal_omitted, gate=gate, families=families_map)
    # All UNMEASURED / UNKNOWN
    kind = rows[0].get("status") if rows else UNKNOWN
    return refuse("scan", kind, "", legal_omitted=legal_omitted, gate=gate,
                  families=families_map)


def _write_canonical(out_dir: Path, head: dict, turns: list[dict]) -> dict:
    sid = head["id"]
    jsonl_path, decl_path = jsonl_paths(out_dir, sid)
    out_dir.mkdir(parents=True, exist_ok=True)
    blob = encode_jsonl(head, turns)
    decl = write_declared(jsonl_path, blob)
    body_sha = sha256_bytes(encode_turns_body(turns))
    sources = head.get("sources") or []
    source_sha = sources[0]["sha256"] if sources else None
    payload = sidecar_payload(
        jsonl_decl=decl,
        body_sha=body_sha,
        source_sha=source_sha,
        n_turns=len(turns),
        fidelity=(sources[0].get("fidelity") if sources else "span") or "span",
        produced_at=_now_iso(),
        produced_by=PRODUCED_BY,
    )
    decl_bytes = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
                  + "\n").encode("utf-8")
    write_declared(decl_path, decl_bytes)
    # Verify the jsonl against the sidecar (sha-only).
    read_verified(jsonl_path, expect_len=payload["len"], expect_sha=payload["sha"])
    return {
        "jsonl": str(jsonl_path),
        "decl": str(decl_path),
        "len": payload["len"],
        "sha": payload["sha"],
        "body_sha": body_sha,
        "source_sha": source_sha,
        "n_turns": len(turns),
    }


def _source_sha_on_disk(head: dict) -> str | None:
    sources = head.get("sources") or []
    if not sources:
        return None
    p = Path(sources[0]["path"])
    data = p.read_bytes()
    got = sha256_bytes(data)
    declared = sources[0].get("sha256")
    if declared and got != declared:
        raise Refusal("HASH_MISMATCH",
                      f"source.sha256 {declared[:12]} != disk {got[:12]}",
                      path=str(p))
    return got


def do_load(*, sid: str | None, path: Path | None, family: str | None,
            store: Path | None, out_dir: Path | None) -> dict:
    fam = family or (family_of_id(sid) if sid else None)
    if not fam:
        return refuse("load", UNKNOWN, "pass --family or an id with cow-/grok- prefix")
    if fam in UNMEASURED:
        return refuse("load", KIND_UNMEASURED, f"{fam} is UNMEASURED this sit",
                      path=UNMEASURED.get(fam), n=None)
    adapter = get_adapter(fam)
    if adapter is None:
        return refuse("load", UNKNOWN, f"unknown family {fam}")
    if store is None:
        return refuse("load", GUESSED_ROOT,
                      "--store required for vendor load (no guessed live path)")
    try:
        rec = adapter.load(store, sid=sid, path=path)
    except Refusal as e:
        extra = dict(e.extra)
        extra.pop("kind", None)
        return refuse("load", e.kind, e.detail,
                      legal_omitted=(e.kind == LEGAL_OMITTED),
                      **extra)

    head = rec["head"]
    turns = rec["turns"]
    if head.get("n_turns") != len(turns):
        head = dict(head)
        head["n_turns"] = len(turns)

    disk_sha = _source_sha_on_disk(head)
    blob = encode_jsonl(head, turns)
    jsonl_sha = sha256_bytes(blob)
    written = None
    if out_dir is not None:
        written = _write_canonical(out_dir, head, turns)
        jsonl_sha = written["sha"]

    gate = {
        "schema": head.get("schema"),
        "n_turns": len(turns),
        "sha": jsonl_sha,
        "source_sha": disk_sha,
        "id": head.get("id"),
    }
    kind_extra = {}
    kind = "OK"
    if rec.get("truncated"):
        kind = TRUNCATED
        kind_extra["detail"] = "jsonl ended mid-line; n_turns is complete lines only"
    if rec.get("unknown_roles"):
        kind = SCHEMA_UNKNOWN
        kind_extra["unmapped_roles"] = rec["unknown_roles"]
        kind_extra["detail"] = "unmappable vendor role (not silently folded)"

    body = view(head, turns)
    if kind == "OK":
        rec_out = ok("load", gate, legal_omitted=False)
    else:
        rec_out = refuse("load", kind, kind_extra.get("detail", ""),
                         legal_omitted=False, gate=gate)
        if "unmapped_roles" in kind_extra:
            rec_out["unmapped_roles"] = kind_extra["unmapped_roles"]
    # Transcript view fields live beside the result envelope. Do not clobber
    # result schema/kind with cosmos-transcript/1's schema/kind.
    for k, v in body.items():
        if k in ("schema", "kind"):
            continue
        rec_out[k] = v
    rec_out["transcript_schema"] = body.get("schema")
    rec_out["transcript_kind"] = body.get("kind")
    if written:
        rec_out["out"] = written
    rec_out["hmac"] = False
    return rec_out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="session_tools.py",
        description="COSMOS session-tools Slice-1: scan + load (cowork, grok_tui).",
    )
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--root", default=None,
                        help="COSMOS runtime root (required when touching a COSMOS tree)")
    shared.add_argument("--store", default=None,
                        help="vendor store (catalog dir or grok sessions root)")
    shared.add_argument("--family", action="append", default=None,
                        help="repeatable; default cowork,grok_tui")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan", parents=[shared], help="discover stores without write")
    ld = sub.add_parser("load", parents=[shared],
                        help="one session → cosmos-transcript/1 view")
    ld.add_argument("--id", default=None, help="cow-<session_id> or grok-<uuid>")
    ld.add_argument("--path", default=None, help="vendor session path")
    ld.add_argument("--out", default=None,
                    help="write {id}.ctr.jsonl + {id}.ctr.decl.json here")
    return p


def dispatch(args, argv: list[str] | None = None) -> dict:
    hit = _kernel_touch(argv or [])
    if hit:
        return hit
    families = _families_from(args.family)
    store = Path(args.store) if args.store else None
    guessed = _locator_or_guessed(args.store, args.root, args.cmd)
    if guessed:
        return guessed
    if args.cmd == "scan":
        return do_scan(families, store)
    sid = getattr(args, "id", None)
    path = Path(args.path) if getattr(args, "path", None) else None
    if not sid and not path:
        return refuse("load", UNKNOWN, "load requires --id or --path")
    fam = None
    if args.family:
        fams = _families_from(args.family)
        fam = fams[0] if len(fams) == 1 else None
    out_dir = Path(args.out) if getattr(args, "out", None) else None
    return do_load(sid=sid, path=path, family=fam, store=store, out_dir=out_dir)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = build_parser()
    try:
        args = p.parse_args(argv)
    except SystemExit as e:
        # argparse usage — still not a guessed root
        return int(e.code) if isinstance(e.code, int) else 1
    rec = dispatch(args, argv)
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0 if rec.get("kind") == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
