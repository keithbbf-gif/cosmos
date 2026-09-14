#!/usr/bin/env python3
"""Download Commons stand-ins, write RIGHTS.md, and inject <figure> + seo frontmatter."""
from __future__ import annotations

import io
import re
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
STAND_IN = ROOT / "images" / "stand-in"
ASSETS_PATH = ROOT / "images" / "_assets.yaml"
RIGHTS_PATH = ROOT / "RIGHTS.md"
UA = "COSMOS-fig-content-bot/1.0 (https://github.com/keithbbf-gif/cosmos)"

# Slug → asset key (see images/_assets.yaml). Tuned for topic honesty, not literal gear photos.
SLUG_ASSET: dict[str, str] = {
    "industry-fig-cutting-six-eight-three": "amwell_trunk",
    "lignified-vs-dormant-fig-cuttings": "amwell_trunk",
    "when-zone-8a-fig-wood-is-ready": "amwell_canopy_2",
    "green-fig-cuttings-root-now": "leiden_fig",
    "which-fig-cane-to-cut": "amwell_canopy_1",
    "pencil-thick-fig-cuttings": "amwell_trunk",
    "fig-cutting-polarity": "bucharest_tree",
    "pruning-figs-for-cuttings": "amwell_canopy_1",
    "how-many-cuttings-from-one-fig": "la_figuera",
    "wash-fig-cuttings-before-rooting": "amwell_trunk",
    "inspecting-mail-order-fig-cuttings": "figs_small",
    "storing-vs-sticking-fig-cuttings-8a": "amwell_trunk",
    "labeling-fig-cuttings": "figuier_label",
    "fig-variety-cutting-behavior": "bowl_figs",
    "fig-rooting-mix-squeeze-test": "sphagnum",
    "heat-mat-thermostat-fig-cuttings": "bucharest_tree",
    "citing-the-2023-coir-de-test": "bucharest_tree",
    "fig-cutting-cup-as-climate": "bucharest_tree",
    "fig-cutting-callus-vs-root": "amwell_trunk",
    "fig-cutting-leaves-before-roots": "figuier_label",
    "water-rooting-fig-cuttings": "bucharest_tree",
    "outdoor-bulk-fig-starts": "la_figuera",
    "light-for-fig-cuttings": "leiden_fig",
    "fig-rooting-hormone-optional": "amwell_trunk",
    "scoring-and-planting-depth-fig-cuttings": "bucharest_tree",
    "humidity-covers-fig-cuttings-8a": "leiden_fig",
    "fungus-gnats-algae-fig-cups": "bucharest_tree",
    "stop-peeking-at-fig-cuttings": "bucharest_tree",
    "slow-rooting-fig-varieties": "figuier_label",
    "winter-shop-fig-cuttings": "leiden_fig",
    "air-layer-vs-fig-cutting": "amwell_canopy_1",
    "air-layer-june-not-august": "amwell_canopy_2",
    "sphagnum-for-fig-air-layers": "sphagnum",
    "how-to-wound-a-fig-air-layer": "amwell_trunk",
    "when-to-cut-a-fig-air-layer": "sphagnum",
    "air-layer-failure-dry-wrap": "amwell_canopy_2",
    "trunk-air-layer-figs-8a": "la_figuera",
    "potting-a-fig-air-layer": "bucharest_tree",
    "pot-up-fig-before-june": "bucharest_tree",
    "first-two-weeks-after-fig-pot-up": "bucharest_tree",
    "planting-figs-in-clay-8a": "la_figuera",
    "transplanting-a-fruiting-fig": "incir_fruit",
    "transplanting-fig-suckers": "basal_shoots",
    "fig-pot-size-jump": "bucharest_tree",
    "do-not-transplant-figs-in-august": "amwell_canopy_2",
    "when-a-fig-is-established-8a": "la_figuera",
}

MAX_EDGE = 1600
JPEG_QUALITY = 88


def load_assets() -> dict:
    return yaml.safe_load(ASSETS_PATH.read_text(encoding="utf-8"))


def download_asset(asset: dict) -> Image.Image:
    req = urllib.request.Request(asset["url"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_EDGE:
        scale = MAX_EDGE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    return img


def split_frontmatter(text: str) -> tuple[dict, str, str]:
    if not text.startswith("---"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("unclosed frontmatter")
    fm_raw = text[3:end]
    rest = text[end + 4 :]
    if rest.startswith("\n"):
        rest = rest[1:]
    meta = yaml.safe_load(fm_raw) or {}
    return meta, fm_raw, rest


def strip_existing_hero(rest: str) -> str:
    rest = re.sub(
        r"^<!--\s*hero:.*?\s*-->\s*\n<figure[^>]*>.*?</figure>\s*\n+",
        "",
        rest,
        count=1,
        flags=re.DOTALL,
    )
    return rest


def seo_title(title: str, stage: str) -> str:
    core = textwrap.shorten(title.strip(), width=44, placeholder="…")
    return f"{core} | Zone 8a figs"


def seo_description(title: str, stage: str, author: str) -> str:
    stage_blurb = {
        "take": "Cutting wood for trays that survive Arkansas 8a.",
        "root": "Rooting cups, mix, and shop mistakes—8a humidity included.",
        "layer": "Air-layer timing for common figs in Zone 8a.",
        "move": "Pot-up and in-ground moves after the cup—PapaFig calendar.",
    }.get(stage, "Zone 8a fig propagation.")
    base = f"{title}. {stage_blurb}"
    if len(base) > 158:
        base = textwrap.shorten(base, width=158, placeholder="…")
    return base


def commons_page(asset: dict) -> str:
    title = asset["commons_title"].replace(" ", "_")
    return f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title)}"


def figure_html(
    slug: str,
    asset: dict,
    dims: tuple[int, int],
    editor_caption: str,
) -> str:
    w, h = dims
    rel = f"../images/stand-in/{slug}.jpg"
    alt = (
        f"{asset['depicts']} Library stand-in; replace with D:\\FIGS per PHOTO_NOTES.md."
    )
    alt = re.sub(r"\s+", " ", alt)
    cap = editor_caption.strip()
    if cap:
        cap = f"{cap} "
    cap += (
        "This is a Wikimedia Commons stand-in—not our tree, not our bench. "
        f"License: {asset['license']}."
    )
    page = commons_page(asset)
    return (
        f"<!-- hero: stand-in until D:\\FIGS pick -->\n"
        f'<figure class="fig-hero fig-stand-in" id="hero-{slug}" '
        f'itemscope itemtype="https://schema.org/ImageObject">\n'
        f'  <img src="{rel}" alt="{alt}" width="{w}" height="{h}" '
        f'loading="eager" fetchpriority="high" decoding="async" '
        f'itemprop="contentUrl" />\n'
        f"  <figcaption>\n"
        f'    <span itemprop="caption">{cap}</span>\n'
        f'    <span class="photo-credit" itemprop="creditText">{asset["credit"]} '
        f'<a href="{page}" rel="license noopener" itemprop="license">Source</a>.</span>\n'
        f"  </figcaption>\n"
        f"</figure>\n\n"
    )


def editor_caption_from_meta(meta: dict) -> str:
    imgs = meta.get("images") or []
    if imgs and isinstance(imgs[0], dict):
        return str(imgs[0].get("caption") or "")
    return ""


def write_rights(rows: list[dict]) -> None:
    lines = [
        "# RIGHTS — fig propagation & rooting (stand-in library)",
        "",
        "Staged drafts use **Wikimedia Commons** stills until KC-PC picks land from "
        "`D:\\FIGS` (see [`PHOTO_NOTES.md`](PHOTO_NOTES.md)). **No AI-generated images.** "
        "Every stand-in caption says **not our tree** where applicable.",
        "",
        "Replace flow: shoot or pick from `D:\\FIGS` → upload to WordPress media → swap "
        "`../images/stand-in/<slug>.jpg` for the production URL → update this row.",
        "",
        "| Draft | Slug | File | Commons | License | Credit |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in sorted(rows, key=lambda x: x["id"]):
        lines.append(
            f"| {r['id']} | `{r['slug']}` | `{r['file']}` | "
            f"[{r['commons_title']}]({r['page']}) | {r['license']} | {r['credit']} |"
        )
    lines.extend(
        [
            "",
            "## Rules (carry into WordPress)",
            "",
            "1. **Ours first** — `D:\\FIGS` folders in `PHOTO_NOTES.md` beat any row here.",
            "2. **Stand-ins stay honest** — do not caption success, variety, or gear that "
            "is not in the frame.",
            "3. **CC licenses** — keep photographer credit and license link in "
            "`<figcaption class=\"photo-credit\">`.",
            "4. **No success-rate art** — no “92% rooted” watermarks; cite the 2023 post in prose.",
            "",
        ]
    )
    RIGHTS_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    assets = load_assets()
    STAND_IN.mkdir(parents=True, exist_ok=True)
    rights_rows: list[dict] = []
    cached: dict[str, tuple[Image.Image, tuple[int, int]]] = {}

    for path in sorted(DRAFTS.glob("d*.md")):
        text = path.read_text(encoding="utf-8")
        meta, _fm_raw, rest = split_frontmatter(text)
        slug = meta.get("slug")
        if not slug or slug not in SLUG_ASSET:
            raise SystemExit(f"{path.name}: missing or unknown slug {slug!r}")
        asset_key = SLUG_ASSET[slug]
        asset = assets[asset_key]
        if asset_key not in cached:
            img = download_asset(asset)
            cached[asset_key] = (img, img.size)
        img, _ = cached[asset_key]
        out_path = STAND_IN / f"{slug}.jpg"
        img.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
        w, h = Image.open(out_path).size

        meta["seo"] = {
            "title": seo_title(str(meta.get("title", "")), str(meta.get("stage", ""))),
            "description": seo_description(
                str(meta.get("title", "")),
                str(meta.get("stage", "")),
                str(meta.get("author", "")),
            ),
            "robots": "noindex, nofollow",
        }
        meta["hero_image"] = {
            "file": f"images/stand-in/{slug}.jpg",
            "stand_in": True,
            "asset_key": asset_key,
            "alt": re.sub(
                r"\s+",
                " ",
                f"{asset['depicts']} Stand-in; not our tree.",
            ),
            "width": w,
            "height": h,
            "license": asset["license"],
            "source": "wikimedia-commons",
            "commons_title": asset["commons_title"],
        }

        rest = strip_existing_hero(rest)
        block = figure_html(slug, asset, (w, h), editor_caption_from_meta(meta))
        new_text = "---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True) + "---\n" + block + rest
        path.write_text(new_text, encoding="utf-8")

        rights_rows.append(
            {
                "id": meta.get("id", path.stem),
                "slug": slug,
                "file": f"images/stand-in/{slug}.jpg",
                "commons_title": asset["commons_title"],
                "page": commons_page(asset),
                "license": asset["license"],
                "credit": asset["credit"],
            }
        )
        print(f"OK {path.name} → {slug}.jpg ({asset_key})")

    write_rights(rights_rows)
    print(f"Wrote {RIGHTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
