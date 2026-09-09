#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage the MOTIF public pack into live/publish/. Does not post.

    py -3.14 cosmos\\cosmos_publish_stage.py --root V:\\A\\Ai\\COSMOS

GET never mkdir the dest. live/publish must already exist. Nested arxiv/_preview
copies are allowed under that dest. This TUI does not click X, LinkedIn, arXiv,
USPTO, or GitHub visibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

PACK_FILES = (
    Path("README.md"),
    Path("MOTIF_WHITEPAPER.md"),
    Path("MOTIF_WHITEPAPER.pdf"),
    Path("MOTIF_X.md"),
    Path("MOTIF_LINKEDIN.md"),
    Path("arxiv") / "motif_swiss_cheese.tex",
    Path("arxiv") / "motif_swiss_cheese.pdf",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _files(source: Path) -> list[Path]:
    out = list(PACK_FILES)
    preview = source / "_preview"
    if preview.is_dir():
        out.extend(sorted(
            p.relative_to(source) for p in preview.rglob("*") if p.is_file()
        ))
    return out


def stage(repo: Path) -> dict:
    source = repo / "docs" / "publish"
    dest = repo / "live" / "publish"
    if not source.is_dir():
        raise RuntimeError("missing docs/publish")
    if not dest.is_dir():
        raise RuntimeError("live/publish must already exist; refusing mkdir")

    rows = []
    for rel in _files(source):
        src = source / rel
        if not src.is_file():
            raise RuntimeError("missing pack file: %s" % rel.as_posix())
        target = dest / rel
        if not target.parent.exists():
            target.parent.mkdir(parents=True)
        shutil.copy2(src, target)
        rows.append({
            "path": rel.as_posix(),
            "sha256": _sha256(src),
            "bytes": src.stat().st_size,
        })

    manifest = {
        "kind": "COSMOS_MOTIF_STAGED_PACK",
        "destination": "live/publish",
        "dest": "staged",
        "publish": False,
        "github_visibility_flip": False,
        "uspto": False,
        "chatbot": False,
        "n": len(rows),
        "rows": rows,
    }
    (dest / "STAGED_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ns = ap.parse_args()
    rec = stage(Path(ns.root).resolve())
    print(json.dumps({
        "ok": True,
        "n": rec["n"],
        "dest": str(Path(ns.root).resolve() / "live" / "publish"),
        "publish": False,
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
