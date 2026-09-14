#!/usr/bin/env python3
"""Build RIGHTS.md, figures/registry.json, and per-essay <figure> HTML from draft plans.

Sources: Metropolitan Museum Open Access (CC0), Wikimedia Commons (PD/CC), museum object
pages when images are not redistributable. No AI-generated images.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
FIGURES = ROOT / "figures"
REGISTRY_PATH = FIGURES / "registry.json"
RIGHTS_PATH = ROOT / "RIGHTS.md"
IMAGE_SEO_PATH = ROOT / "IMAGE_SEO.md"

UA = "COSMOS-mission-furniture-image-seo/1.0 (staged; contact: bbf-furniture-lane)"

ALLOWED_IMG_HOSTS = (
    "images.metmuseum.org",
    "upload.wikimedia.org",
    "loc.gov",
    "tile.loc.gov",
    "cdn.loc.gov",
    "ids.si.edu",
    "library.si.edu",
)

# Curated Commons / Met URLs (verified 2026-09-14). Keys: (chapter, fig) or substring match.
CURATED: dict[tuple[int, int] | str, dict] = {
    (10, 1): {
        "image": "https://upload.wikimedia.org/wikipedia/commons/8/8e/The_Craftsman_Issue_01_october_1901.jpg",
        "license": "Public domain (US, 1901 periodical cover)",
        "source_page": "https://commons.wikimedia.org/wiki/File:The_Craftsman_Issue_01_october_1901.jpg",
        "credit": "Wikimedia Commons",
    },
    (36, 1): {
        "image": "https://upload.wikimedia.org/wikipedia/commons/f/f9/Adjustable-Back_Chair_No._2342%2C_Gustav_Stickley%2C_1900-1904_-_IMG_1632.JPG",
        "license": "CC BY-SA 4.0 (Wikimedia contributor photograph of museum object)",
        "source_page": "https://commons.wikimedia.org/wiki/File:Adjustable-Back_Chair_No._2342,_Gustav_Stickley,_1900-1904_-_IMG_1632.JPG",
        "credit": "Wikimedia Commons",
    },
    "united crafts, poltrona": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Gustav_stickley_per_united_crafts%2C_poltrona%2C_eastwood_NY_1901.jpg",
        "license": "CC BY-SA 4.0",
        "source_page": "https://commons.wikimedia.org/wiki/File:Gustav_stickley_per_united_crafts,_poltrona,_eastwood_NY_1901.jpg",
        "credit": "Wikimedia Commons",
    },
    "armchair_met_dp216214": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Armchair_MET_DP216214.jpg",
        "license": "CC0 (Met Open Access, via Wikimedia)",
        "source_page": "https://commons.wikimedia.org/wiki/File:Armchair_MET_DP216214.jpg",
        "credit": "The Metropolitan Museum of Art / Wikimedia Commons",
    },
    "gustav stickley portrait": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Gustav_Stickley.jpg",
        "license": "Public domain",
        "source_page": "https://commons.wikimedia.org/wiki/File:Gustav_Stickley.jpg",
        "credit": "Wikimedia Commons",
    },
    "music cabinet ellis": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Gustav_Stickley%2C_possibly_Harvey_Ellis._Music_Cabinet%2C_1902-1904.jpg",
        "license": "No restrictions (Cleveland Museum of Art, via Commons)",
        "source_page": "https://commons.wikimedia.org/wiki/File:Gustav_Stickley,_possibly_Harvey_Ellis._Music_Cabinet,_1902-1904.jpg",
        "credit": "Cleveland Museum of Art / Wikimedia Commons",
    },
    "dropfront desk": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Gustav_Stickley._Dropfront_Desk%2C_ca._1903..jpg",
        "license": "No restrictions (Cleveland Museum of Art, via Commons)",
        "source_page": "https://commons.wikimedia.org/wiki/File:Gustav_Stickley._Dropfront_Desk,_ca._1903..jpg",
        "credit": "Cleveland Museum of Art / Wikimedia Commons",
    },
    (19, 1): {
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4f/RoycroftInnSign.JPG",
        "license": "CC BY-SA 3.0",
        "source_page": "https://commons.wikimedia.org/wiki/File:RoycroftInnSign.JPG",
        "credit": "Wikimedia Commons contributor",
    },
    (20, 1): {
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4f/RoycroftInnSign.JPG",
        "license": "CC BY-SA 3.0",
        "source_page": "https://commons.wikimedia.org/wiki/File:RoycroftInnSign.JPG",
        "credit": "Wikimedia Commons contributor",
    },
    (4, 1): {
        "image": "https://upload.wikimedia.org/wikipedia/commons/9/92/Japanese_Dwelling_from_The_Centennial_Exposition_Guide_%281876%29.jpg",
        "license": "Public domain",
        "source_page": "https://commons.wikimedia.org/wiki/File:Japanese_Dwelling_from_The_Centennial_Exposition_Guide_(1876).jpg",
        "credit": "Wikimedia Commons",
    },
    (5, 1): {
        "image": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Oscar_Wilde_by_Sarony_1882_01.jpg",
        "license": "Public domain",
        "source_page": "https://commons.wikimedia.org/wiki/File:Oscar_Wilde_by_Sarony_1882_01.jpg",
        "credit": "Napoleon Sarony / Wikimedia Commons",
    },
    "mission-style decor and fireplace": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Parlor_interior_with_mission-style_decor_and_fireplace.jpg",
        "license": "Public domain",
        "source_page": "https://commons.wikimedia.org/wiki/File:Parlor_interior_with_mission-style_decor_and_fireplace.jpg",
        "credit": "Wikimedia Commons",
    },
}

MET_CACHE: dict[str, dict | None] = {
    # Pre-seeded Open Access (API verified 2026-09-14)
    "2000.58": {
        "accessionNumber": "2000.58",
        "title": "Desk",
        "isPublicDomain": True,
        "primaryImage": "https://images.metmuseum.org/CRDImages/ad/original/DT257587.jpg",
        "objectURL": "https://www.metmuseum.org/art/collection/search/10414",
    },
    "1991.311.1": {
        "accessionNumber": "1991.311.1",
        "title": "Linen Press",
        "isPublicDomain": True,
        "primaryImage": "https://images.metmuseum.org/CRDImages/ad/original/DT184.jpg",
        "objectURL": "https://www.metmuseum.org/art/collection/search/14336",
    },
    "1991.145": {
        "accessionNumber": "1991.145",
        "title": "Library Table",
        "isPublicDomain": True,
        "primaryImage": "https://images.metmuseum.org/CRDImages/ad/original/DT185.jpg",
        "objectURL": "https://www.metmuseum.org/art/collection/search/14282",
    },
    "65.186": {
        "accessionNumber": "65.186",
        "title": "Chair",
        "isPublicDomain": True,
        "primaryImage": "https://images.metmuseum.org/CRDImages/ad/original/ADA4655.jpg",
        "objectURL": "https://www.metmuseum.org/art/collection/search/7551",
    },
    "2014.633": {
        "accessionNumber": "2014.633",
        "title": "Armchair",
        "isPublicDomain": False,
        "primaryImage": None,
        "objectURL": "https://www.metmuseum.org/art/collection/search/19007",
    },
}


@dataclass
class FigureRow:
    chapter: int
    slug: str
    fig: int
    title: str
    body_lines: list[str]
    license_line: str
    alt: str
    caption: str
    rights_id: str = ""
    import_status: str = "hold"
    image_url: str | None = None
    source_page: str | None = None
    license_resolved: str = ""
    credit: str = ""
    width: int | None = None
    height: int | None = None


def front_matter(text: str) -> str:
    parts = re.split(r"^---\s*$", text, flags=re.M)
    return parts[1] if len(parts) > 2 else ""


def parse_figure_plans(path: Path) -> list[FigureRow]:
    text = path.read_text(encoding="utf-8")
    fm = front_matter(text)
    ch_m = re.search(r"^chapter:\s*0*(\d+)", fm, re.M)
    slug_m = re.search(r"^slug:\s*(\S+)", fm, re.M)
    chapter = int(ch_m.group(1)) if ch_m else 0
    slug = slug_m.group(1) if slug_m else path.stem
    if "## Figure plan" not in text:
        return []
    block = text.split("## Figure plan", 1)[1]
    rows: list[FigureRow] = []
    for part in re.split(r"\n\*\*Fig\.", block):
        m = re.match(r"\s*(\d+)\.\*\*\s*(.*)", part)
        if not m:
            continue
        fig = int(m.group(1))
        rest = m.group(2).strip()
        lines = [ln.strip() for ln in part.split("\n") if ln.strip()]
        title = rest.split("\n")[0].strip()
        license_line = next((l for l in lines if l.lower().startswith("license:")), "")
        alt = next((l.replace("Alt:", "", 1).strip() for l in lines if l.lower().startswith("alt:")), "")
        caption = next((l.replace("Caption:", "", 1).strip() for l in lines if l.lower().startswith("caption:")), "")
        rid = f"ch{chapter:02d}-fig{fig:02d}"
        rows.append(
            FigureRow(
                chapter=chapter,
                slug=slug,
                fig=fig,
                title=title,
                body_lines=lines[1:],
                license_line=license_line,
                alt=alt,
                caption=caption,
                rights_id=rid,
            )
        )
    return rows


def met_by_accession(accession: str) -> dict | None:
    if accession in MET_CACHE:
        return MET_CACHE[accession]
    q = urllib.parse.quote(accession)
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q={q}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.load(resp)
    except OSError:
        MET_CACHE[accession] = None
        return None
    for oid in (data.get("objectIDs") or [])[:30]:
        obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"
        req2 = urllib.request.Request(obj_url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req2, timeout=25) as resp2:
                obj = json.load(resp2)
        except OSError:
            continue
        if obj.get("accessionNumber") == accession:
            MET_CACHE[accession] = obj
            time.sleep(0.05)
            return obj
    MET_CACHE[accession] = None
    return None


def find_met_accessions(text: str) -> list[str]:
    """Pull museum accession numbers only when the line names a collection (avoid 5.5 vol refs)."""
    low = text.lower()
    if not any(
        k in low
        for k in (
            "metropolitan museum",
            "met museum",
            " cooper hewitt",
            "lacma",
            "accession",
            "acc.",
        )
    ) and not re.search(r"\bMet\s+[0-9]", text):
        return []
    found: list[str] = []
    for m in re.finditer(r"\b(\d{2,4}\.\d{2,4}(?:\.\d+)?[a-z]?)\b", text, re.I):
        acc = m.group(1)
        if acc not in found:
            found.append(acc)
    return found


def resolve_row(row: FigureRow) -> None:
    blob = " ".join([row.title] + row.body_lines).lower()
    full = " ".join([row.title] + row.body_lines)
    key = (row.chapter, row.fig)
    if key in CURATED:
        apply_curated(row, CURATED[key])
        return
    for sub, meta in CURATED.items():
        if isinstance(sub, str) and sub in blob:
            apply_curated(row, meta)
            return

    for acc in find_met_accessions(full):
        obj = met_by_accession(acc)
        if not obj:
            continue
        row.source_page = obj.get("objectURL")
        row.credit = "The Metropolitan Museum of Art"
        if obj.get("isPublicDomain") and obj.get("primaryImage"):
            row.image_url = obj["primaryImage"]
            row.license_resolved = "CC0 (Met Open Access)"
            row.import_status = "hotlink_ok"
            return
        row.license_resolved = row.license_line.replace("License:", "", 1).strip() or "Met terms"
        row.import_status = "museum_page_only"
        return

    lic = row.license_line.lower()
    if "reserved" in lic:
        row.import_status = "reserved"
        row.license_resolved = row.license_line.replace("License:", "", 1).strip()
        return
    if "confirm" in lic or "museum terms" in lic or "lacma" in lic or "huntington" in lic or "smart" in lic:
        row.import_status = "hold"
        row.license_resolved = row.license_line.replace("License:", "", 1).strip()
        return
    if "public domain" in lic or "cc0" in lic or lic.strip() == "license: pd":
        row.import_status = "pd_unverified"
        row.license_resolved = row.license_line.replace("License:", "", 1).strip()
        return
    row.import_status = "hold"
    row.license_resolved = row.license_line.replace("License:", "", 1).strip() or "unspecified"


def apply_curated(row: FigureRow, meta: dict) -> None:
    row.image_url = meta.get("image")
    row.source_page = meta.get("source_page")
    row.license_resolved = meta.get("license", "")
    row.credit = meta.get("credit", "")
    row.import_status = "hotlink_ok"


def figure_html(row: FigureRow) -> str:
    alt = html.escape(row.alt or row.title)
    cap = html.escape(row.caption or row.title)
    credit = html.escape(row.credit) if row.credit else ""
    lic = html.escape(row.license_resolved)
    src_page = html.escape(row.source_page or "", quote=True)
    attrs = (
        f' id="{row.rights_id}"'
        f' data-chapter="{row.chapter}"'
        f' data-slug="{html.escape(row.slug)}"'
        f' data-fig="{row.fig}"'
        f' data-import="{row.import_status}"'
    )
    parts = [f"<figure{attrs}>"]
    if row.image_url and row.import_status == "hotlink_ok":
        src = html.escape(row.image_url.split("?")[0], quote=True)
        parts.append(
            f'  <img src="{src}" alt="{alt}" loading="lazy" decoding="async" '
            f'width="1200" height="900" />'
        )
    elif row.source_page:
        parts.append(
            f'  <p class="figure-source"><a href="{src_page}" rel="noopener">'
            f"View object at source museum</a></p>"
        )
    parts.append(f"  <figcaption>{cap}")
    if credit:
        parts.append(f" <cite>{credit}</cite>.")
    if lic:
        parts.append(f" <span class=\"figure-license\">({lic})</span>")
    parts.append("</figcaption>")
    parts.append("</figure>")
    return "\n".join(parts)


def write_essay_html(slug: str, rows: list[FigureRow]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    out = FIGURES / f"{slug}.figures.html"
    chunks = [
        "<!-- Staged figure SEO block. Do not publish until RIGHTS.md import_status is cleared. -->",
        f'<!-- voice_check: human; no AI-generated images; series: arts-crafts-mission-furniture-deep -->',
        f'<section class="essay-figures" data-slug="{html.escape(slug)}">',
    ]
    for row in rows:
        chunks.append(figure_html(row))
    chunks.append("</section>")
    out.write_text("\n".join(chunks) + "\n", encoding="utf-8")


def write_registry(all_rows: list[FigureRow]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": "build_figure_seo.py",
        "series": "arts-crafts-mission-furniture-deep",
        "no_ai_images": True,
        "figures": [
            {
                "rights_id": r.rights_id,
                "chapter": r.chapter,
                "slug": r.slug,
                "fig": r.fig,
                "title": r.title,
                "alt": r.alt,
                "caption": r.caption,
                "import_status": r.import_status,
                "license": r.license_resolved,
                "image_url": r.image_url,
                "source_page": r.source_page,
                "credit": r.credit,
            }
            for r in all_rows
        ],
    }
    REGISTRY_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_rights_md(all_rows: list[FigureRow]) -> None:
    hotlink = sum(1 for r in all_rows if r.import_status == "hotlink_ok")
    hold = sum(1 for r in all_rows if r.import_status in ("hold", "museum_page_only", "pd_unverified"))
    reserved = sum(1 for r in all_rows if r.import_status == "reserved")
    lines = [
        "---",
        "title: Image rights register",
        "series: American Arts and Crafts / Mission Furniture",
        "status: staged",
        "voice_check: human",
        "lane: bbf-furniture",
        "rights_pass: 2026-09-14",
        "---",
        "",
        "# RIGHTS.md",
        "",
        "Machine-readable twin: `figures/registry.json`. HTML `<figure>` blocks: `figures/*.figures.html`.",
        "",
        "## Policy",
        "",
        "- **No AI-generated images.** Only museum, library, and Commons assets with traceable licenses.",
        "- **Hotlink** only when `import_status` is `hotlink_ok` (Met CC0, Commons PD/CC BY-SA as noted).",
        "- **`hold` / `museum_page_only` / `pd_unverified`:** caption and alt ship for SEO; image file stays off the CMS until a human confirms.",
        "- **`reserved`:** Gamble House / Huntington interiors and similar — do not upload as free stock.",
        "",
        f"Totals: **{len(all_rows)}** figures — **{hotlink}** hotlink-ready, **{hold}** held or page-only, **{reserved}** reserved.",
        "",
        "## Corrections from API check (Met)",
        "",
        "- **Met 2014.633** (Ellis inlaid armchair): **not** Met Open Access (`isPublicDomain: false`). Hero row in `PHOTO_CAPTIONS.md` corrected to **museum terms / hold**.",
        "- **Met 65.672.2** in the writer table is the Osgood *Hints* volume; verify accession against the object page before import (search by title if needed).",
        "",
        "## Register",
        "",
        "| rights_id | ch | slug | fig | import_status | license | image | source |",
        "| --- | ---: | --- | ---: | --- | --- | --- | --- |",
    ]
    for r in all_rows:
        img = "yes" if r.image_url and r.import_status == "hotlink_ok" else "—"
        src = r.source_page or "—"
        if len(src) > 48:
            src = src[:45] + "…"
        lines.append(
            f"| `{r.rights_id}` | {r.chapter} | `{r.slug}` | {r.fig} | {r.import_status} | "
            f"{r.license_resolved.replace('|', '/')} | {img} | {src} |"
        )
    lines.append("")
    lines.append("Regenerate: `python3 content/arts-crafts-mission-furniture-deep/build_figure_seo.py`")
    lines.append("")
    RIGHTS_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_image_seo_md(all_rows: list[FigureRow]) -> None:
    hotlink = [r for r in all_rows if r.import_status == "hotlink_ok"]
    lines = [
        "---",
        "title: Image SEO pass notes",
        "series: American Arts and Crafts / Mission Furniture",
        "status: staged",
        "voice_check: human",
        "lane: bbf-furniture",
        "---",
        "",
        "# IMAGE + SEO",
        "",
        "Per-essay `<figure>` HTML lives in `figures/<slug>.figures.html` for WordPress/block import.",
        "Each block includes `alt`, `figcaption`, lazy-loaded `img` when rights allow, and `data-import` for the CMS gate.",
        "",
        "## WordPress",
        "",
        "1. Import body from `drafts/*.md` as today (figure plans stay in markdown until cleared).",
        "2. When a row in `RIGHTS.md` is `hotlink_ok`, paste the matching `<figure>` from the `.figures.html` file.",
        "3. Featured image: first `hotlink_ok` figure in the chapter, or a Commons hero from `PHOTO_CAPTIONS.md`.",
        "",
        "## Hotlink-ready count",
        "",
        f"{len(hotlink)} of {len(all_rows)} figures have a verified `image_url` (Met CC0 or curated Commons).",
        "",
        "Validator: `python3 content/arts-crafts-mission-furniture-deep/validate_image_seo.py`",
        "",
    ]
    IMAGE_SEO_PATH.write_text("\n".join(lines), encoding="utf-8")


def patch_photo_captions() -> None:
    path = ROOT / "PHOTO_CAPTIONS.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "| 12 | Inlay armchair | Met 2014.633 | CC0 | Ellis myth; collaborative shop |",
        "| 12 | Inlay armchair | Met 2014.633 | Met terms (not CC0) | Ellis myth; collaborative shop |",
    )
    if "RIGHTS.md" not in text:
        text = text.replace(
            "Rights register for figure plans inside `drafts/`.",
            "Rights register for figure plans inside `drafts/`. Authoritative pass: `RIGHTS.md` + `figures/registry.json`.",
        )
    path.write_text(text, encoding="utf-8")


def prefetch_accessions(rows: list[FigureRow]) -> None:
    needed: set[str] = set()
    for row in rows:
        blob = " ".join([row.title] + row.body_lines)
        for acc in find_met_accessions(blob):
            if acc not in MET_CACHE:
                needed.add(acc)
    for acc in sorted(needed):
        met_by_accession(acc)


def main() -> int:
    all_rows: list[FigureRow] = []
    by_slug: dict[str, list[FigureRow]] = {}
    for path in sorted(DRAFTS.glob("*.md")):
        rows = parse_figure_plans(path)
        if not rows:
            continue
        all_rows.extend(rows)
        by_slug[rows[0].slug] = rows
    prefetch_accessions(all_rows)
    for row in all_rows:
        resolve_row(row)
    for slug, rows in by_slug.items():
        write_essay_html(slug, rows)

    write_registry(all_rows)
    write_rights_md(all_rows)
    write_image_seo_md(all_rows)
    patch_photo_captions()
    hotlink = sum(1 for r in all_rows if r.import_status == "hotlink_ok")
    print(f"figures: {len(all_rows)} rows, {len(by_slug)} essays, {hotlink} hotlink_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
