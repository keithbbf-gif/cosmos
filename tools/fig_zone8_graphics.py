#!/usr/bin/env python3
"""Download cleared rasters and embed <figure> blocks for fig-cold-hardiness-zone8."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.parse
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content" / "fig-cold-hardiness-zone8"
ASSETS = PACK / "assets" / "images"
DRAFTS = PACK / "drafts"
UA = "FigRootsZone8Pack/1.0 (educational staging; fig cold-hardiness)"

# Commons filename -> pack-relative path under assets/images/
DOWNLOADS: list[tuple[str, str]] = [
    ("2012_USDA_Plant_Hardiness_Zone_Map_(USA).jpg", "shared/usda-phzm-2012.jpg"),
    ("Pomological_Watercolor_POM00007441.jpg", "varieties/usda-pom-celeste.jpg"),
    ("Pomological_Watercolor_POM00001043.jpg", "varieties/usda-pom-magnolia.jpg"),
    ("Pomological_Watercolor_POM00007440.jpg", "varieties/usda-pom-calimyrna-1912.jpg"),
    ("Pomological_Watercolor_POM00001044.jpg", "varieties/usda-pom-nameless.jpg"),
    ("Pomological_Watercolor_POM00001045.jpg", "varieties/usda-pom-royal-black.jpg"),
    ("Pomological_Watercolor_POM00001042.jpg", "varieties/usda-pom-cutting.jpg"),
    ("Pomological_Watercolor_POM00001168.jpg", "varieties/usda-pom-toulousienne.jpg"),
    ("Pomological_Watercolor_POM00001071.jpg", "varieties/usda-pom-endgere-caprifig.jpg"),
    ("A_fig_plant_(Ficus_carica);_fruiting_stem_and_halved_fruit._Wellcome_V0044761.jpg", "botanical/wellcome-v0044761.jpg"),
    ("Ficus_carica_L,_1771.jpg", "botanical/ehret-trew-1771.jpg"),
    ("EB1911_Moraceae_-_Ficus_carica.jpg", "botanical/eb1911-moraceae-diagram.jpg"),
    ("Illustration_Ficus_carica0.jpg", "botanical/kohler-type-med-plate.jpg"),
    ("11-Figuier-Ficus_carica.jpg", "botanical/denoncin-figuier-plate.jpg"),
    ("Amwell_Fig_(1).jpg", "living/amwell-fig-tree.jpg"),
    ("20210731_Hortus_botanicus_Leiden_-_Ficus_carica.jpg", "living/hortus-leiden-fig-2021.jpg"),
]

RIGHTS: dict[str, dict[str, str]] = {
    "shared/usda-phzm-2012.jpg": {
        "credit": "USDA Agricultural Research Service",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:2012_USDA_Plant_Hardiness_Zone_Map_(USA).jpg",
        "commons": "2012_USDA_Plant_Hardiness_Zone_Map_(USA).jpg",
    },
    "varieties/usda-pom-celeste.jpg": {
        "credit": "Elsie Lower Pomeroy; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00007441.jpg",
        "commons": "Pomological_Watercolor_POM00007441.jpg",
        "subject": "Celeste fig (USDA plate; cultivar identification, not a winter photo).",
    },
    "varieties/usda-pom-magnolia.jpg": {
        "credit": "USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001043.jpg",
        "commons": "Pomological_Watercolor_POM00001043.jpg",
        "subject": "Magnolia / Brown Turkey class fig (USDA plate).",
    },
    "varieties/usda-pom-calimyrna-1912.jpg": {
        "credit": "Elsie Lower Pomeroy; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00007440.jpg",
        "commons": "Pomological_Watercolor_POM00007440.jpg",
        "subject": "Calimyrna-type Smyrna fig (pollination-dependent; not a Zone 8a default).",
    },
    "varieties/usda-pom-nameless.jpg": {
        "credit": "USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001044.jpg",
        "commons": "Pomological_Watercolor_POM00001044.jpg",
    },
    "varieties/usda-pom-royal-black.jpg": {
        "credit": "USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001045.jpg",
        "commons": "Pomological_Watercolor_POM00001045.jpg",
    },
    "varieties/usda-pom-cutting.jpg": {
        "credit": "USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001042.jpg",
        "commons": "Pomological_Watercolor_POM00001042.jpg",
        "subject": "Fig cutting wood (USDA plate) — propagation, not winter wrap.",
    },
    "varieties/usda-pom-toulousienne.jpg": {
        "credit": "USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001168.jpg",
        "commons": "Pomological_Watercolor_POM00001168.jpg",
    },
    "varieties/usda-pom-endgere-caprifig.jpg": {
        "credit": "USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001071.jpg",
        "commons": "Pomological_Watercolor_POM00001071.jpg",
        "subject": "Caprifig (pollinator host); not a table-fig winter subject.",
    },
    "botanical/wellcome-v0044761.jpg": {
        "credit": "Wellcome Collection V0044761",
        "license": "CC BY 4.0",
        "source": "https://commons.wikimedia.org/wiki/File:A_fig_plant_(Ficus_carica);_fruiting_stem_and_halved_fruit._Wellcome_V0044761.jpg",
        "commons": "A_fig_plant_(Ficus_carica);_fruiting_stem_and_halved_fruit._Wellcome_V0044761.jpg",
    },
    "botanical/ehret-trew-1771.jpg": {
        "credit": "G. D. Ehret; C. J. Trew, Plantae selectae (1771)",
        "license": "Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:Ficus_carica_L,_1771.jpg",
        "commons": "Ficus_carica_L,_1771.jpg",
    },
    "botanical/eb1911-moraceae-diagram.jpg": {
        "credit": "Encyclopaedia Britannica 1911",
        "license": "Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:EB1911_Moraceae_-_Ficus_carica.jpg",
        "commons": "EB1911_Moraceae_-_Ficus_carica.jpg",
    },
    "botanical/kohler-type-med-plate.jpg": {
        "credit": "Köhler-type medicinal plate (Commons scan)",
        "license": "Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:Illustration_Ficus_carica0.jpg",
        "commons": "Illustration_Ficus_carica0.jpg",
    },
    "botanical/denoncin-figuier-plate.jpg": {
        "credit": "Denoncin, figuier plate (Commons: 11-Figuier-Ficus carica)",
        "license": "Public domain (as tagged on Commons)",
        "source": "https://commons.wikimedia.org/wiki/File:11-Figuier-Ficus_carica.jpg",
        "commons": "11-Figuier-Ficus_carica.jpg",
    },
    "living/amwell-fig-tree.jpg": {
        "credit": "Hopefully Acceptable Use (Wikimedia Commons)",
        "license": "CC BY-SA 4.0",
        "source": "https://commons.wikimedia.org/wiki/File:Amwell_Fig_(1).jpg",
        "commons": "Amwell_Fig_(1).jpg",
        "subject": "Mature Ficus carica in a UK garden — living tree, not a USDA cultivar voucher.",
    },
    "living/hortus-leiden-fig-2021.jpg": {
        "credit": "Rudolphous (Wikimedia Commons)",
        "license": "CC BY-SA 4.0",
        "source": "https://commons.wikimedia.org/wiki/File:20210731_Hortus_botanicus_Leiden_-_Ficus_carica.jpg",
        "commons": "20210731_Hortus_botanicus_Leiden_-_Ficus_carica.jpg",
    },
}

# draft id -> (asset rel path, alt text, figcaption body without credit line)
FIGURES: dict[str, tuple[str, str, str]] = {
    "d01": (
        "shared/usda-phzm-2012.jpg",
        "USDA Plant Hardiness Zone Map with Zones 7, 8a, 8b, and 9 across the United States",
        "Figure 1. Zone 8a sits between colder Zone 7 and milder Zone 9 on the USDA map — the in-between band where fig winter strategy borrows from both neighbors.",
    ),
    "d02": (
        "shared/usda-phzm-2012.jpg",
        "USDA hardiness zone map showing thirty-year average extreme minimum temperatures",
        "Figure 1. The published zone number is a long average of the coldest night, not a promise for your yard — the map is context for reading forecasts against fig wood.",
    ),
    "d03": (
        "botanical/wellcome-v0044761.jpg",
        "Botanical illustration of Ficus carica fruiting stem, syconia, and halved fruit",
        "Figure 1. Winter damage splits wood, buds, roots, and fruiting positions differently — a common fig anatomy plate labels what can freeze separately.",
    ),
    "d04": (
        "living/amwell-fig-tree.jpg",
        "Mature common fig tree Ficus carica with branching structure in a garden",
        "Figure 1. Dieback to grey sticks is not always death — a living Ficus carica can resprout from lower wood after a hard Zone 8a winter.",
    ),
    "d05": (
        "varieties/usda-pom-celeste.jpg",
        "USDA watercolor plate of Celeste fig fruit and leaves",
        "Figure 1. Breba figs form on last year's wood — when cold kills canes, you lose that bonus crop on cultivars like Celeste.",
    ),
    "d06": (
        "living/hortus-leiden-fig-2021.jpg",
        "Common fig tree Ficus carica in summer leaf at Hortus botanicus Leiden",
        "Figure 1. Wet cold and dry cold stress dormant fig tissue differently — living foliage shows the tree you are trying to keep alive through winter.",
    ),
    "d07": (
        "living/amwell-fig-tree.jpg",
        "Spreading fig tree canopy exposed to open garden air",
        "Figure 1. Wind strips heat from fig wood faster than a still night at the same temperature — open exposure behaves like a colder zone.",
    ),
    "d08": (
        "shared/usda-phzm-2012.jpg",
        "USDA zone map emphasizing mid-South and Mid-Atlantic hardiness bands",
        "Figure 1. Duration below freezing often matters more than the single lowest degree on the thermometer — zone bands are averages of extreme nights, not hours cold.",
    ),
    "d09": (
        "varieties/usda-pom-nameless.jpg",
        "USDA pomological watercolor of an unnamed common fig cultivar",
        "Figure 1. Catalog hardiness ratings and yard hardiness are not the same test — USDA plates document named fruit, not your fence line microclimate.",
    ),
    "d10": (
        "varieties/usda-pom-toulousienne.jpg",
        "USDA watercolor of Toulousienne fig on the branch",
        "Figure 1. Chicago Hardy and other cold-tolerant labels are floors in commerce, not personalities — historic USDA plates show the fruit those names sell.",
    ),
    "d11": (
        "varieties/usda-pom-celeste.jpg",
        "Celeste fig USDA pomological watercolor with closed-eye fruit",
        "Figure 1. Celeste's tight ostiole is often cited for humid summers; in Zone 8a winter, the same plant still needs wood protection to fruit again.",
    ),
    "d12": (
        "varieties/usda-pom-magnolia.jpg",
        "USDA Magnolia fig watercolor — Brown Turkey class fruit in commerce",
        "Figure 1. Brown Turkey in nurseries is a crowd of similar clones — a USDA Magnolia plate is a voucher, not proof your tag matches this wood.",
    ),
    "d13": (
        "varieties/usda-pom-endgere-caprifig.jpg",
        "USDA caprifig watercolor used in Smyrna pollination systems",
        "Figure 1. LSU releases were bred for Gulf humidity and nematodes — caprifig biology still explains why some fig classes need wasps, unlike most backyard 8a trees.",
    ),
    "d14": (
        "varieties/usda-pom-royal-black.jpg",
        "USDA Royal Black fig pomological watercolor",
        "Figure 1. Cultivars that sulk in 8a often want longer seasons or milder winters — dark-fruited plates help you recognize the plant, not guarantee survival.",
    ),
    "d15": (
        "living/amwell-fig-tree.jpg",
        "In-ground common fig tree with trunk and roots in garden soil",
        "Figure 1. In-ground figs use soil mass as a blanket — the trunk and crown sit in earth that buffers sudden drops compared with a raised pot.",
    ),
    "d16": (
        "varieties/usda-pom-cutting.jpg",
        "USDA plate of fig cutting wood for propagation",
        "Figure 1. A container fig has a small root volume that freezes through — cutting wood plates remind you the plant is mostly roots in a pot cliff.",
    ),
    "d17": (
        "living/hortus-leiden-fig-2021.jpg",
        "Potted and field fig trees both Ficus carica — comparison context in a botanic garden",
        "Figure 1. In-ground versus pot is a winter decision: soil volume and mobility trade off before the first killing frost in Zone 8a.",
    ),
    "d18": (
        "varieties/usda-pom-cutting.jpg",
        "Young fig propagation wood on USDA watercolor plate",
        "Figure 1. First-year figs have not hardened wood or roots — treat new plantings colder than your zone map until they survive a full winter cycle.",
    ),
    "d19": (
        "living/amwell-fig-tree.jpg",
        "Fig tree planted along a garden wall with radiant heat potential",
        "Figure 1. South walls and brick steal degrees on sunny days — siting against masonry is a Zone 8a trick that does not show on the USDA map.",
    ),
    "d20": (
        "botanical/eb1911-moraceae-diagram.jpg",
        "Encyclopaedia Britannica 1911 floral diagram of Ficus carica",
        "Figure 1. Raised beds drain well but lift roots toward the air — neither true in-ground mass nor a movable pot for winter protection.",
    ),
    "d21": (
        "varieties/usda-pom-celeste.jpg",
        "Three-cultivar winter planning — Celeste USDA plate as representative hardy common fig",
        "Figure 1. If you could keep only three figs in 8a, start with proven wood survivors — Celeste-class tight-eye fruit on USDA documentation.",
    ),
    "d22": (
        "living/amwell-fig-tree.jpg",
        "Dormant-season fig tree before wrapping — timing reference in a temperate garden",
        "Figure 1. Wrapping too early in October traps moisture — wait until the tree is dormant and forecasts justify protection in Zone 8a.",
    ),
    "d23": (
        "living/hortus-leiden-fig-2021.jpg",
        "Open-centered fig tree structure for winter airflow when wrapped",
        "Figure 1. Burlap and breathable wraps need air gaps — avoid cooking dormant buds under plastic sheeting on sunny winter days.",
    ),
    "d24": (
        "botanical/denoncin-figuier-plate.jpg",
        "Historic French fig wood and fruit plate — winter cage context",
        "Figure 1. Leaf-filled cages insulate without sealing — historic plates show the wood you are enclosing, not the leaves themselves.",
    ),
    "d25": (
        "varieties/usda-pom-cutting.jpg",
        "Flexible fig branches on USDA cutting plate — tip-and-bury candidate wood",
        "Figure 1. Tip-and-bury bends young wood to soil level — a Zone 7 trick some 8a growers still use after polar winters.",
    ),
    "d26": (
        "botanical/ehret-trew-1771.jpg",
        "Ehret 1771 botanical plate of Ficus carica — avoid non-breathable wrap materials",
        "Figure 1. Do not wrap figs in sealed plastic or dark tarps — breathable materials protect without fermenting dormant tissue.",
    ),
    "d27": (
        "botanical/kohler-type-med-plate.jpg",
        "Köhler-type Ficus carica plate — caution with heat cables and lights",
        "Figure 1. Heat cables and incandescent lights need thermostats and fire clearance — electricity is a tool, not a substitute for a bad wrap job.",
    ),
    "d28": (
        "living/amwell-fig-tree.jpg",
        "Multi-stem common fig tree habit for winter tying and wrapping",
        "Figure 1. Split-trunk and bush forms wrap differently — tie stems so burlap follows the real architecture, not an imaginary lollipop.",
    ),
    "d29": (
        "botanical/wellcome-v0044761.jpg",
        "Fig plant parts labeled on Wellcome botanical plate — winter kit reference",
        "Figure 1. A winter kit is twine, breathable wrap, mulch, and a forecast — not a gadget drawer of unlabeled sprays.",
    ),
    "d30": (
        "living/hortus-leiden-fig-2021.jpg",
        "Garden fig tree where pets and children can disturb winter protection",
        "Figure 1. Dogs, kids, and wind undo wraps — stake cages so protection survives the yard, not just the first cold night.",
    ),
    "d31": (
        "shared/usda-phzm-2012.jpg",
        "USDA zone map with Zone 7 north of Zone 8a",
        "Figure 1. Zone 7 growers bury crowns and accept top dieback — 8a can borrow crown mulch without copying every northern ritual.",
    ),
    "d32": (
        "living/hortus-leiden-fig-2021.jpg",
        "Mild-climate fig tree in full leaf — Zone 9 restraint on wrapping",
        "Figure 1. In Zone 9, unnecessary wrapping steams dormant wood — mild winters need shade and water discipline more than burlap habits from 8a.",
    ),
    "d33": (
        "shared/usda-phzm-2012.jpg",
        "USDA map detail for Zone 8a versus 8b minimum temperature bands",
        "Figure 1. Five degrees of average extreme minimum separates 8a from 8b — attitude toward wrapping and variety risk shifts with that band.",
    ),
    "d34": (
        "living/amwell-fig-tree.jpg",
        "Wrapped-season inspection of common fig in a garden without removing protection",
        "Figure 1. Midwinter checks should confirm ties and dryness — peek without stripping insulation during a cold spell.",
    ),
    "d35": (
        "botanical/wellcome-v0044761.jpg",
        "Ficus carica stem and fruit cross-section — drought and freeze stress",
        "Figure 1. Water into dormancy, then avoid bone-dry roots before a hard freeze — stressed wood freezes more readily in 8a pots and margins.",
    ),
    "d36": (
        "varieties/usda-pom-cutting.jpg",
        "Dormant fig wood on USDA plate — garage storage of potted trees",
        "Figure 1. Unheated garage storage trades light for stable cold — dormant potted figs still need occasional moisture checks.",
    ),
    "d37": (
        "living/amwell-fig-tree.jpg",
        "In-ground fig planting depth context for burying pots",
        "Figure 1. Burying pots heel-deep uses soil insulation while keeping the plant movable — different from true in-ground culture.",
    ),
    "d38": (
        "varieties/usda-pom-cutting.jpg",
        "Small-diameter fig wood — pot volume and freeze-through time",
        "Figure 1. Small pots freeze through in one night; larger soil mass buys hours that matter at 12°F in Zone 8a.",
    ),
    "d39": (
        "living/hortus-leiden-fig-2021.jpg",
        "Fig tree on hardscape versus soil — porch and patio winter microclimates",
        "Figure 1. Concrete and porch boards radiate cold under pots — surface matters as much as USDA zone for patio figs.",
    ),
    "d40": (
        "living/amwell-fig-tree.jpg",
        "Temperate garden fig after snow — ice and insulation context",
        "Figure 1. Snow can insulate if it stays; ice and wind strip protection — do not assume white cover always helps wood.",
    ),
    "d41": (
        "shared/usda-phzm-2012.jpg",
        "USDA hardiness map during extreme cold-wave planning for fig growers",
        "Figure 1. Polar vortex years break averages — zone maps are background when forecasts show days below teens in 8a.",
    ),
    "d42": (
        "living/amwell-fig-tree.jpg",
        "Early-spring fig tree before full leaf-out — late freeze unwrap timing",
        "Figure 1. Unwrap on a warming trend but keep material handy — late March freezes hit 8a figs after a mild week.",
    ),
    "d43": (
        "living/amwell-fig-tree.jpg",
        "Common fig with winter dieback wood waiting for late spring pruning",
        "Figure 1. Do not panic-prune brown wood in March — wait until buds show live tissue after the last hard freeze window.",
    ),
    "d44": (
        "varieties/usda-pom-cutting.jpg",
        "Dead fig stick wood on USDA propagation plate — autopsy comparison",
        "Figure 1. Autopsy piles of grey sticks teach more than catalogs — scratch bark and check pith before declaring the roots dead.",
    ),
    "d45": (
        "living/hortus-leiden-fig-2021.jpg",
        "Fig tree with young spring foliage vulnerable to late frost",
        "Figure 1. Late frost after leaf-out burns tender growth — protect or accept setback on breba wood in Zone 8a.",
    ),
    "d46": (
        "living/amwell-fig-tree.jpg",
        "In-ground yard fig beside container culture — two winter regimes",
        "Figure 1. Yard fig and patio fig are different plants in winter — soil mass versus garage mobility in the same USDA zone.",
    ),
    "d47": (
        "varieties/usda-pom-magnolia.jpg",
        "Nursery-labeled Brown Turkey class fig on USDA plate — March box-store hardy tags",
        "Figure 1. Box-store hardy labels in March describe marketing, not your December — verify cultivar against a voucher plate, then plan wraps.",
    ),
    "d48": (
        "shared/usda-phzm-2012.jpg",
        "Seasonal calendar context on USDA Zone 8a hardiness map",
        "Figure 1. September through April is the wall calendar for 8a fig winter — protection, checks, unwrap, and late frost in one loop.",
    ),
    "d49": (
        "botanical/eb1911-moraceae-diagram.jpg",
        "Fig floral structure diagram — mulch over crown versus trunk wrap",
        "Figure 1. Mulch insulates crown roots; it is not a substitute for wrapping upper wood on exposed in-ground figs.",
    ),
    "d50": (
        "living/amwell-fig-tree.jpg",
        "Surviving common fig after winter — evaluating last season's protection",
        "Figure 1. Judge last year's wrap by live wood and breba set, not by whether burlap looked tidy in April.",
    ),
}


def fetch_commons(commons_name: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    enc = urllib.parse.quote(commons_name)
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=1600"
    subprocess.run(
        ["curl", "-fsSL", "-A", UA, "-o", str(dest), url],
        check=True,
    )
    data = dest.read_bytes()
    if len(data) < 5000:
        raise RuntimeError(f"download too small: {dest} ({len(data)} bytes)")
    return {
        "path": str(dest.relative_to(PACK)),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "commons": commons_name,
    }


def download_all() -> list[dict]:
    meta: list[dict] = []
    for commons, rel in DOWNLOADS:
        dest = ASSETS / rel
        print("GET", commons)
        meta.append(fetch_commons(commons, dest))
    out = ASSETS / "_download_meta.json"
    out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def figure_html(draft_id: str, asset_rel: str, alt: str, caption: str) -> str:
    rights = RIGHTS[asset_rel]
    credit = rights["credit"]
    lic = rights["license"]
    fig_id = f"{draft_id}.{asset_rel.split('/')[-1].rsplit('.', 1)[0]}"
    return (
        f'<!-- figure-id: {fig_id} -->\n'
        f"<figure>\n"
        f'<img src="../assets/images/{asset_rel}" alt="{alt}">\n'
        f"<figcaption>{caption} Credit: {credit}. License: {lic} — see RIGHTS.md.</figcaption>\n"
        f"</figure>\n\n"
    )


def embed_figures() -> None:
    for path in sorted(DRAFTS.glob("d*.md")):
        draft_id = path.stem.split("-")[0]
        if draft_id not in FIGURES:
            raise SystemExit(f"missing figure spec for {draft_id}")
        asset, alt, cap = FIGURES[draft_id]
        block = figure_html(draft_id, asset, alt, cap)
        text = path.read_text(encoding="utf-8")
        if "<figure>" in text:
            text = re.sub(r"<!-- figure-id:.*?-->\s*<figure>.*?</figure>\s*\n*", "", text, count=1, flags=re.S)
        if not text.startswith("---"):
            raise SystemExit(f"{path.name}: no front matter")
        end = text.find("\n---", 3)
        if end == -1:
            raise SystemExit(f"{path.name}: bad front matter")
        insert_at = end + 4
        if insert_at < len(text) and text[insert_at] == "\n":
            insert_at += 1
        new_text = text[:insert_at] + "\n" + block + text[insert_at:].lstrip("\n")
        path.write_text(new_text, encoding="utf-8")
        print("embedded", path.name)


def write_rights_md() -> None:
    lines = [
        "# RIGHTS — fig-cold-hardiness-zone8",
        "",
        "Cleared rasters staged for desk review. **Recheck Commons and USDA pages before live WordPress import.**",
        "No D:\\FIGS field notes were available in the cloud agent environment; sources are USDA ARS / NAL,",
        "Wellcome Collection, and Wikimedia Commons as listed.",
        "",
        "All subjects are *Ficus carica* (common fig) or official USDA cultivar documentation plates — no decorative fake fruit.",
        "",
        "| Pack path | Commons / source | Credit | License | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    meta_path = ASSETS / "_download_meta.json"
    sha_by_rel = {}
    if meta_path.exists():
        for row in json.loads(meta_path.read_text(encoding="utf-8")):
            p = row["path"]
            rel = p.split("assets/images/", 1)[-1] if "assets/images/" in p else p
            sha_by_rel[rel] = row["sha256"]
    for rel, info in sorted(RIGHTS.items()):
        sha = sha_by_rel.get(rel, "(run download)")
        src = info.get("source", info.get("commons", ""))
        lines.append(
            f"| `assets/images/{rel}` | {src} | {info['credit']} | {info['license']} | `{sha}` |"
        )
    lines.extend(
        [
            "",
            "## Reuse",
            "",
            "- USDA Pomological Watercolor Collection: U.S. government work; credit USDA/NAL.",
            "- CC BY / CC BY-SA photos: keep author line in caption and this table.",
            "- Historical plates are not photographs of your wrapped tree; captions state that where relevant.",
            "",
        ]
    )
    (PACK / "RIGHTS.md").write_text("\n".join(lines), encoding="utf-8")


def write_graphics_index() -> None:
    lines = [
        "# GRAPHICS_INDEX — fig-cold-hardiness-zone8",
        "",
        "| Figure ID | Draft | File | Status |",
        "| --- | --- | --- | --- |",
    ]
    for draft_id in sorted(FIGURES):
        asset, _, _ = FIGURES[draft_id]
        fig_id = f"{draft_id}.{asset.split('/')[-1].rsplit('.', 1)[0]}"
        fname = f"drafts/{draft_id}-*.md"
        lines.append(f"| `{fig_id}` | `{draft_id}` | `assets/images/{asset}` | staged |")
    lines.append("")
    (PACK / "GRAPHICS_INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("download", "all"):
        download_all()
    if cmd in ("embed", "all"):
        embed_figures()
    if cmd in ("docs", "all"):
        write_rights_md()
        write_graphics_index()


if __name__ == "__main__":
    main()
