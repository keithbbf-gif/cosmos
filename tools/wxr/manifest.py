# -*- coding: utf-8 -*-
"""Configurable content-pack manifest for WXR draft export."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST = Path("content/_ops/wxr/manifest.toml")


@dataclass(frozen=True)
class ManifestPack:
    id: str
    label: str
    posts_glob: str
    site_url: str
    site_title: str
    site_description: str = ""
    language: str = "en-US"
    default_author: str = "cosmos-export"
    sample_posts_glob: str | None = None


@dataclass(frozen=True)
class Manifest:
    version: int
    repo_root: Path
    manifest_path: Path
    packs: tuple[ManifestPack, ...]


def _pack_from_row(row: dict[str, Any]) -> ManifestPack:
    pid = str(row["id"]).strip()
    if not pid:
        raise ValueError("pack id must be non-empty")
    return ManifestPack(
        id=pid,
        label=str(row.get("label", pid)),
        posts_glob=str(row.get("posts_glob", f"content/{pid}/posts/**/*.md")),
        site_url=str(row.get("site_url", "https://example.invalid")),
        site_title=str(row.get("site_title", pid)),
        site_description=str(row.get("site_description", "")),
        language=str(row.get("language", "en-US")),
        default_author=str(row.get("default_author", "cosmos-export")),
        sample_posts_glob=row.get("sample_posts_glob"),
    )


def load_manifest(
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> Manifest:
    root = (repo_root or Path.cwd()).resolve()
    path = (manifest_path or (root / DEFAULT_MANIFEST)).resolve()
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    version = int(raw.get("version", 1))
    packs_raw = raw.get("packs") or raw.get("pack") or []
    if not isinstance(packs_raw, list):
        raise ValueError("manifest packs must be a list")
    packs = tuple(_pack_from_row(p) for p in packs_raw)
    if not packs:
        raise ValueError("manifest must declare at least one pack")
    return Manifest(
        version=version,
        repo_root=root,
        manifest_path=path,
        packs=packs,
    )


def get_pack(manifest: Manifest, pack_id: str) -> ManifestPack:
    for p in manifest.packs:
        if p.id == pack_id:
            return p
    known = ", ".join(x.id for x in manifest.packs)
    raise KeyError(f"unknown pack {pack_id!r}; known: {known}")
