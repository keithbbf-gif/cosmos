#!/usr/bin/env python3
"""Insert <figure> SEO blocks and graphics front matter into drawer-construction-history drafts."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
SPECS = Path(__file__).with_name("dch_graphics_specs.json")


def load_specs() -> dict[str, dict]:
    data = json.loads(SPECS.read_text(encoding="utf-8"))
    return {d["slug"]: d for d in data["diagrams"]}


def split_front_matter(text: str) -> tuple[str, str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing front matter")
    end = text.index("\n---\n", 4)
    return text[:4], text[4:end], text[end + 5 :]


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def fig_schematic(slug: str, spec: dict) -> str:
    alt = spec["desc"]
    cap = spec["title"]
    return f"""<figure class="dch-figure">
  <img src="../assets/{slug}/joinery-diagram.svg" alt="{_esc(alt)}" width="640" height="420" loading="lazy" decoding="async"/>
  <figcaption><strong>Figure 1.</strong> {_esc(cap)}. Pack schematic (CC0).</figcaption>
</figure>
"""


def fig_shop_pending(fig: dict, photo_num: int) -> str:
    cap = fig.get("caption", "")
    credit = fig.get("credit", "")
    pref = fig.get("preferred", "")
    return f"""<figure class="dch-figure dch-shop-pending">
  <img src="../assets/placeholders/bbf-shop-pending.svg" alt="{_esc(cap)}" width="640" height="360" loading="lazy" decoding="async"/>
  <figcaption><strong>Photo {photo_num} (pending).</strong> {_esc(cap)} {_esc(credit)} Slot: {_esc(pref)}</figcaption>
</figure>
"""


def ensure_graphics(fm: str, slug: str, spec: dict) -> str:
    if re.search(r"^graphics:\s*$", fm, re.M) or re.search(r"^graphics:\n", fm, re.M):
        return fm
    block = (
        "graphics:\n"
        f"  - id: fig-sch-01\n"
        f"    path: assets/{slug}/joinery-diagram.svg\n"
        f"    alt: \"{spec['desc']}\"\n"
        f"    license: CC0-1.0\n"
        f"    status: staged\n"
    )
    if "\nfigures:\n" in fm:
        return fm.replace("\nfigures:\n", "\n" + block + "figures:\n", 1)
    return fm + "\n" + block


def process_draft(path: Path, specs: dict[str, dict]) -> None:
    raw = path.read_text(encoding="utf-8")
    _, fm, body = split_front_matter(raw)
    slug_m = re.search(r"^slug:\s*(\S+)\s*$", fm, re.M)
    if not slug_m:
        raise ValueError(f"no slug in {path}")
    slug = slug_m.group(1)
    spec = specs[slug]
    fm = ensure_graphics(fm, slug, spec)

    parsed = yaml.safe_load(fm) or {}
    figure_list = parsed.get("figures") or []
    by_id = {f["id"]: f for f in figure_list}

    photo_re = re.compile(r"<!-- PHOTO:\s*(fig-\d+)\s+(.+?) -->\s*", re.DOTALL)

    def replacer(match: re.Match[str]) -> str:
        fid = match.group(1)
        fig = by_id.get(
            fid,
            {"caption": "", "credit": "", "preferred": match.group(2).strip()},
        )
        parts: list[str] = []
        if fid == "fig-01":
            parts.append(fig_schematic(slug, spec))
            parts.append(fig_shop_pending(fig, 2))
        else:
            parts.append(fig_shop_pending(fig, 3))
        return "\n".join(parts) + "\n\n"

    new_body = photo_re.sub(replacer, body)
    if new_body == body:
        print(f"  skip (no PHOTO tags): {path.name}")
        return
    out = f"---\n{fm.rstrip()}\n---\n\n{new_body.lstrip()}"
    path.write_text(out, encoding="utf-8")
    print(f"  updated {path.name}")


def main() -> None:
    specs = load_specs()
    for draft in sorted(DRAFTS.glob("*.md")):
        process_draft(draft, specs)


if __name__ == "__main__":
    main()
