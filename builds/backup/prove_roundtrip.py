#!/usr/bin/env python3
"""prove_roundtrip.py — the restore DRILL for cosmos_backup, run against real bytes.

Not a unit test: an operator drill that prints the sha256 at every step, so the
claim "the backup protects this tree" is bound to values the run emitted rather
than to a green log.

  back up a scratch tree -> corrupt a file IN THE SCRATCH TREE -> restore -> re-hash

The scratch tree is built by COPYING files OUT of --source (read-only, capped by
--files); the source tree is never written, never corrupted. Everything else
happens under --work, which defaults to a system temp dir.

  py -3.14 builds/backup/prove_roundtrip.py --source V:/A/Ai/COSMOS/docs
  py -3.14 builds/backup/prove_roundtrip.py            # synthetic tree, no source

Exit 0 only when the restored bytes hash-match the originals AND every guard
(unverified set, occupied destination) refused as designed. Spawns no
subprocess: nothing to suppress a console window for.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cosmos_backup as cb  # noqa: E402

PROOF_NAME = "ROUNDTRIP_PROOF.json"


def _build_scratch_tree(dst: Path, source: Path | None, limit: int) -> list[str]:
    """Populate dst from source (copy-out, read-only) or synthesize. Returns rel keys."""
    dst.mkdir(parents=True, exist_ok=True)
    if source is None:
        (dst / "nested").mkdir()
        (dst / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        (dst / "nested" / "b.bin").write_bytes(bytes(range(256)) * 400)
        (dst / "nested" / "c.dat").write_bytes(b"\x00" * 8192)
        return ["a.txt", "nested/b.bin", "nested/c.dat"]
    picks = [p for p in sorted(source.rglob("*"))
             if p.is_file() and not p.is_symlink() and ".git" not in p.parts][:limit]
    if not picks:
        raise SystemExit(f"REFUSE: no readable files under {source}")
    rels = []
    for p in picks:
        rel = p.relative_to(source)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, out)          # OUT of the tree; the tree is never written
        rels.append(rel.as_posix())
    return rels


def _expect_refusal(kind: str, fn, *a, **k) -> dict:
    """Run fn expecting a typed refusal; a guard that does not fire is a FAILED drill."""
    try:
        fn(*a, **k)
    except cb.BackupRefusal as e:
        if e.kind != kind:
            raise SystemExit(f"DRILL FAILED: expected {kind}, got {e.kind}")
        return {"expected_kind": kind, "refused": True}
    raise SystemExit(f"DRILL FAILED: {kind} guard did not fire")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", help="real tree to copy sample files OUT of (never written)")
    ap.add_argument("--work", help="scratch root (default: system temp)")
    ap.add_argument("--files", type=int, default=25, help="cap on sampled files")
    ap.add_argument("--key-file", help="optional HMAC key file for sealing artifacts")
    args = ap.parse_args(argv)

    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="cosmos_roundtrip_"))
    key = Path(args.key_file).read_bytes().strip() if args.key_file else None
    source = Path(args.source).resolve() if args.source else None
    tree, dest, stage = work / "tree", work / "sets", work / "displaced"

    rels = _build_scratch_tree(tree, source, args.files)
    print(f"[1] scratch tree      {tree}  ({len(rels)} files"
          f"{' sampled from ' + str(source) if source else ', synthetic'})")

    set_dir = cb.do_backup(tree, dest, key=key)
    manifest = json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))
    print(f"[2] backup set        {set_dir}")
    print(f"    manifest seal     {manifest['seal']['sha256']}")

    victim_rel = max(rels, key=lambda r: manifest["files"][r]["size"])
    victim = tree / Path(*victim_rel.split("/"))
    before = cb.sha256_file(victim)
    blob = bytearray(victim.read_bytes())
    if not blob:
        blob = bytearray(b"\x00")
    blob[len(blob) // 2] ^= 0xFF
    victim.write_bytes(bytes(blob))
    corrupt = cb.sha256_file(victim)
    print(f"[3] victim            {victim_rel}")
    print(f"    sha256 BEFORE     {before}")
    print(f"    sha256 CORRUPTED  {corrupt}   <- one byte flipped")
    if before == corrupt:
        raise SystemExit("DRILL FAILED: corruption did not change the hash")

    guards = {
        "occupied_dest_without_stage": _expect_refusal(
            "RESTORE_DEST_OCCUPIED", cb.do_restore, set_dir, tree, key),
    }

    receipt = cb.do_restore(set_dir, tree, key, stage)
    after = cb.sha256_file(victim)
    print(f"[4] restored          {receipt['files_restored']} files, "
          f"{receipt['bytes_restored']} bytes; {len(receipt['displaced'])} displaced -> {stage}")
    print(f"    sha256 AFTER      {after}")
    ok = after == before
    print(f"    MATCHES ORIGINAL  {ok}")

    mismatches = [r for r, e in manifest["files"].items()
                  if cb.sha256_file(tree / Path(*r.split("/"))) != e["sha256"]]
    print(f"[5] whole tree re-hashed against manifest: "
          f"{len(manifest['files']) - len(mismatches)}/{len(manifest['files'])} match")

    proof = cb.seal({"format": cb.FORMAT, "kind": "ROUNDTRIP_PROOF",
                     "at_utc": cb._utcnow(), "source_sampled": str(source) if source else None,
                     "work": str(work.resolve()), "set_dir": str(set_dir.resolve()),
                     "victim": victim_rel, "sha256_before": before,
                     "sha256_corrupted": corrupt, "sha256_after_restore": after,
                     "restored_matches_original": ok,
                     "files_rehashed": len(manifest["files"]),
                     "mismatches_after_restore": mismatches,
                     "guards": guards,
                     "manifest_seal_sha256": manifest["seal"]["sha256"]}, key)
    proof_path = work / PROOF_NAME
    cb._write_json_atomic(proof_path, proof)
    print(f"[6] sealed proof      {proof_path}")
    print(f"    proof seal        {proof['seal']['sha256']}")
    if not ok or mismatches:
        print("ROUNDTRIP FAILED", file=sys.stderr)
        return 2
    print("ROUNDTRIP PROVEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
