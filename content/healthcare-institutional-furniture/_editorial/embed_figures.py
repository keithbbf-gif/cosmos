#!/usr/bin/env python3
"""Insert lead <figure class="hif-figure"> blocks and SEO image frontmatter."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets" / "figures" / "REGISTRY.toml"
ASSIGNMENTS_PATH = Path(__file__).resolve().parent / "figure_assignments.toml"
DRAFTS = ROOT / "drafts"
WRITER_SLUGS = ROOT / "writer-slugs.json"

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)
FIGURE_MARK = "<!-- hif-figure:v1 -->"
FIGURE_CLASS = "hif-figure"
IMAGE_PASS = "2026-09-14"


def load_assets() -> dict[str, dict]:
    data = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for section in ("diagrams", "plates"):
        for key, block in data.get(section, {}).items():
            out[f"{section}.{key}"] = dict(block)
    return out


def load_assignments() -> dict[str, tuple[str, str, str]]:
    data = tomllib.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
    out: dict[str, tuple[str, str, str]] = {}
    for slug, block in data.items():
        if slug == "series":
            continue
        out[slug] = (block["asset"], block["alt"], block["caption"])
    return out


def rights_line(asset: dict) -> str:
    return (
        f"{asset['license']}; {asset['institution']}; "
        f'<a href="{asset["source_page"]}">source</a>. {asset["credit"]}'
    )


def figure_html(asset: dict, alt: str, caption: str) -> str:
    w = asset.get("width", 1200)
    h = asset.get("height", 900)
    rights = rights_line(asset)
    return (
        f"{FIGURE_MARK}\n"
        f'<figure class="{FIGURE_CLASS}">\n'
        f'  <img src="{asset["src"]}" alt="{alt}" width="{w}" height="{h}" '
        f'loading="lazy" decoding="async"/>\n'
        f"  <figcaption><strong>Fig. 1.</strong> {caption} "
        f"<em>Rights:</em> {rights}</figcaption>\n"
        f"</figure>\n"
    )


def patch_frontmatter(fm: str, asset_key: str) -> str:
    fields = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M))
    dek = fields.get("meta_description", "").strip().strip('"')
    new_kv = {
        "figure_id": asset_key,
        "image_rights": "documented",
        "image_pass": IMAGE_PASS,
    }
    if dek and "og_image_alt" not in fields:
        new_kv["og_image_alt"] = dek[:155]
    lines = fm.splitlines()
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if ":" in line and not line.startswith(" "):
            key = line.split(":", 1)[0].strip()
            if key in new_kv:
                val = new_kv[key]
                if " " in val or ":" in val:
                    out.append(f'{key}: "{val}"')
                else:
                    out.append(f"{key}: {val}")
                seen.add(key)
                continue
        out.append(line)
    if seen != set(new_kv):
        if out and out[-1].strip():
            out.append("")
        for key, val in new_kv.items():
            if key not in seen:
                if " " in val or ":" in val:
                    out.append(f'{key}: "{val}"')
                else:
                    out.append(f"{key}: {val}")
    return "\n".join(out)


def embed_file(path: Path, assets: dict[str, dict], assignments: dict[str, tuple[str, str, str]]) -> bool:
    raw = path.read_text(encoding="utf-8")
    m = FRONT.match(raw)
    if not m:
        print(f"skip (no frontmatter): {path}", file=sys.stderr)
        return False
    fm = m.group(1)
    body = raw[m.end() :]
    slug = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M)).get("slug", "").strip().strip('"')
    if slug not in assignments:
        print(f"skip (no assignment): {slug} {path}", file=sys.stderr)
        return False
    asset_key, alt, caption = assignments[slug]
    asset = assets[asset_key]
    fig = figure_html(asset, alt, caption)
    if FIGURE_MARK in body:
        body = re.sub(
            rf"{re.escape(FIGURE_MARK)}.*?</figure>\n",
            fig,
            body,
            count=1,
            flags=re.S,
        )
    else:
        lines = body.splitlines()
        out: list[str] = []
        inserted = False
        for line in lines:
            out.append(line)
            if not inserted and line.startswith("# "):
                out.append("")
                out.append(fig.rstrip())
                out.append("")
                inserted = True
        body = "\n".join(out) + ("\n" if raw.endswith("\n") else "")
    new_fm = patch_frontmatter(fm, asset_key)
    path.write_text(f"---\n{new_fm}\n---{body}", encoding="utf-8")
    return True


def main() -> int:
    assets = load_assets()
    assignments = load_assignments()
    missing = {ak for ak, _, _ in assignments.values() if ak not in assets}
    if missing:
        print("registry missing assets:", missing, file=sys.stderr)
        return 2
    slugs = json.loads(WRITER_SLUGS.read_text(encoding="utf-8"))["reading_order"]
    if set(slugs) != set(assignments):
        extra = set(assignments) - set(slugs)
        lacking = set(slugs) - set(assignments)
        if extra or lacking:
            print("slug mismatch extra", extra, "lacking", lacking, file=sys.stderr)
            return 2
    n = 0
    for slug in slugs:
        path = DRAFTS / f"{slug}.md"
        if embed_file(path, assets, assignments):
            n += 1
    print(f"embedded figures in {n} drafts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
