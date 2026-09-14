#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI: markdown+frontmatter content packs → WordPress WXR (draft posts only)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .generator import generate_wxr
from .manifest import DEFAULT_MANIFEST, load_manifest


def _repo_root(arg: str | None) -> Path:
    return Path(arg).resolve() if arg else Path.cwd().resolve()


def cmd_list_packs(args: argparse.Namespace) -> int:
    manifest = load_manifest(
        Path(args.manifest) if args.manifest else None,
        _repo_root(args.root),
    )
    for pack in manifest.packs:
        print(f"{pack.id}\t{pack.label}")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    root = _repo_root(args.root)
    use_samples = args.samples or args.dry_run
    result = generate_wxr(
        args.pack,
        manifest_path=Path(args.manifest) if args.manifest else None,
        repo_root=root,
        output=Path(args.output) if args.output else None,
        dry_run=args.dry_run,
        use_samples=use_samples,
    )
    if args.dry_run:
        summary = {
            "pack": result.pack_id,
            "post_count": result.post_count,
            "wxr_bytes": result.wxr_bytes,
            "dry_run": True,
            "use_samples": use_samples,
            "posts": [
                {
                    "source": str(p.source_path.relative_to(root)),
                    "title": p.title,
                    "slug": p.slug,
                    "status": "draft",
                    "stripped_keys": p.stripped_keys,
                    "figure_paths": p.figure_paths,
                }
                for p in result.posts
            ],
        }
        print(json.dumps(summary, indent=2))
        return 0

    assert result.output_path is not None
    print(f"wrote {result.output_path} ({result.post_count} draft posts, {result.wxr_bytes} bytes)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        help="Repository root (default: current working directory)",
    )
    common.add_argument(
        "--manifest",
        help=f"Path to manifest.toml (default: {DEFAULT_MANIFEST})",
    )

    p = argparse.ArgumentParser(
        prog="cosmos-wxr",
        description="Generate WordPress WXR draft imports for COSMOS content packs.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    lp = sub.add_parser("list-packs", help="List pack ids from manifest", parents=[common])
    lp.set_defaults(func=cmd_list_packs)

    gen = sub.add_parser("generate", help="Build WXR for one pack", parents=[common])
    gen.add_argument("pack", help="Pack id from manifest (e.g. figroots-blog)")
    gen.add_argument(
        "--dry-run",
        action="store_true",
        help="Print JSON summary only; do not write WXR (uses sample posts when set)",
    )
    gen.add_argument(
        "--samples",
        action="store_true",
        help="Use sample_posts_glob instead of live pack posts",
    )
    gen.add_argument(
        "--output",
        "-o",
        help="Output .wxr.xml path (default: content/_ops/wxr/out/<pack>-draft.wxr.xml)",
    )
    gen.set_defaults(func=cmd_generate)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
