#!/usr/bin/env python3
"""Embed SEO <figure> blocks and figures: YAML for fig pruning calendar drafts."""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

ASSETS = {
    "usda-phzm-southeast": {
        "file": "assets/images/shared/usda-phzm-southeast.jpg",
        "width": 3300,
        "height": 2550,
        "credit": "USDA Plant Hardiness Zone Map (Southeast), PD.",
    },
    "fig-winter-snow-hood": {
        "file": "assets/images/shared/fig-winter-snow-hood.jpg",
        "width": 2736,
        "height": 3648,
        "credit": "Photo: 4028mdk09, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "usda-pom-winter-cutting": {
        "file": "assets/images/shared/usda-pom-winter-cutting.jpg",
        "width": 2707,
        "height": 4000,
        "credit": "USDA NAL Pomological Watercolor POM00001042, J. Marion Shull, PD.",
    },
    "usda-pom-celeste-1911": {
        "file": "assets/images/shared/usda-pom-celeste-1911.jpg",
        "width": 2659,
        "height": 4000,
        "credit": "USDA NAL POM00007441 (Celeste), Mary Daisy Arnold, PD.",
    },
    "usda-pom-magnolia-1913": {
        "file": "assets/images/shared/usda-pom-magnolia-1913.jpg",
        "width": 2625,
        "height": 4000,
        "credit": "USDA NAL POM00001043 (Magnolia), Mary Daisy Arnold, PD.",
    },
    "ficus-carica-canopy": {
        "file": "assets/images/shared/ficus-carica-canopy.jpg",
        "width": 2848,
        "height": 4288,
        "credit": "Photo: Alvesgaspar, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "ficus-carica-bark": {
        "file": "assets/images/shared/ficus-carica-bark.jpg",
        "width": 1317,
        "height": 1756,
        "credit": "Photo: Kenraiz, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "fig-potted-tree-la-figuera": {
        "file": "assets/images/shared/fig-potted-tree-la-figuera.jpg",
        "width": 2816,
        "height": 2112,
        "credit": "Photo: Archaeodontosaurus, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "fig-dormant-canopy-pajara-01": {
        "file": "assets/images/shared/fig-dormant-canopy-pajara-01.jpg",
        "width": 5616,
        "height": 3744,
        "credit": "Photo: Frank Vincentz, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "fig-dormant-canopy-pajara-02": {
        "file": "assets/images/shared/fig-dormant-canopy-pajara-02.jpg",
        "width": 5616,
        "height": 3744,
        "credit": "Photo: Frank Vincentz, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "fig-dormant-canopy-pajara-03": {
        "file": "assets/images/shared/fig-dormant-canopy-pajara-03.jpg",
        "width": 5616,
        "height": 3744,
        "credit": "Photo: Frank Vincentz, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "kohler-ficus-carica-plate": {
        "file": "assets/images/shared/kohler-ficus-carica-plate.jpg",
        "width": 1469,
        "height": 2318,
        "credit": "Köhler-type Ficus carica plate, Wikimedia Commons, PD.",
    },
}

# draft_id -> (asset_key, figs_folder, figs_shot_note)
PLAN: dict[str, tuple[str, str, str]] = {
    "01": ("usda-phzm-southeast", r"D:\FIGS\Figs", "month-by-month pruning calendar pinned near tools"),
    "02": ("fig-dormant-canopy-pajara-03", r"D:\FIGS\Figs", "March green-tip wait before cutting gray wood"),
    "03": ("fig-dormant-canopy-pajara-02", r"D:\FIGS\Figs", "7b yard with mixed live and dead tips"),
    "04": ("usda-pom-winter-cutting", r"D:\FIGS\Figs", "late January dormant cut to a bud"),
    "05": ("ficus-carica-canopy", r"D:\FIGS\Fig Fruit", "9a tips left on for breba wood"),
    "06": ("usda-pom-winter-cutting", r"D:\FIGS\Figs", "9b hard heading with season left to regrow"),
    "07": ("kohler-ficus-carica-plate", r"D:\FIGS\More Fig Pictures", "overwintering breba beads on last year's nodes"),
    "08": ("ficus-carica-canopy", r"D:\FIGS\Fig Fruit", "main crop on current-season shoots"),
    "09": ("usda-pom-celeste-1911", r"D:\FIGS\Fig Labels", "breba vs main tradeoff on one tree"),
    "10": ("kohler-ficus-carica-plate", r"D:\FIGS\Fig Fruit", "San Pedro breba-only habit"),
    "11": ("usda-pom-magnolia-1913", r"D:\FIGS\Figs", "Chicago Hardy resprout after cane cut"),
    "12": ("usda-pom-celeste-1911", r"D:\FIGS\Fig Fruit", "Celeste light winter hands"),
    "13": ("usda-pom-magnolia-1913", r"D:\FIGS\Figs", "Brown Turkey dual-crop wood"),
    "14": ("ficus-carica-canopy", r"D:\FIGS\Figs-summer-23", "LSU-type open canopy in humidity"),
    "15": ("usda-pom-magnolia-1913", r"D:\FIGS\Fig Labels", "Mission look-alike not suited to Southeast"),
    "16": ("ficus-carica-canopy", r"D:\FIGS\Fig Fruit", "breba-heavy variety tips preserved"),
    "17": ("ficus-carica-bark", r"D:\FIGS\Figs", "October cut pushing soft bark into frost"),
    "18": ("fig-dormant-canopy-pajara-01", r"D:\FIGS\Figs", "Zone 7 hard January heading damage"),
    "19": ("ficus-carica-bark", r"D:\FIGS\Damaged Cuttings", "scratch test before trusting brown bark"),
    "20": ("ficus-carica-bark", r"D:\FIGS\More Fig Pictures", "fresh cut latex — no wound paint"),
    "21": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "multi-trunk stool after winter kill"),
    "22": ("fig-dormant-canopy-pajara-01", r"D:\FIGS\Figs", "thicket of competing leaders thinned"),
    "23": ("ficus-carica-canopy", r"D:\FIGS\Figs-summer-23", "August heading delaying ripeness"),
    "24": ("kohler-ficus-carica-plate", r"D:\FIGS\Fig Labels", "fig training not apple central leader"),
    "25": ("fig-dormant-canopy-pajara-02", r"D:\FIGS\Figs", "suckers left as replacement canes"),
    "26": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "years 1–3 training cuts"),
    "27": ("fig-dormant-canopy-pajara-01", r"D:\FIGS\Figs", "neglected giant before renewal prune"),
    "28": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "container root and top balance"),
    "29": ("ficus-carica-canopy", r"D:\FIGS\Figs", "south-wall fan or espalier"),
    "30": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "bush form sized for winter wrap"),
    "31": ("fig-dormant-canopy-pajara-03", r"D:\FIGS\Figs", "April freeze burned breba wood"),
    "32": ("fig-dormant-canopy-pajara-02", r"D:\FIGS\Damaged Cuttings", "ice-storm split leader repair"),
    "33": ("ficus-carica-canopy", r"D:\FIGS\Figs-summer-23", "June pinch on whippy shoots"),
    "34": ("ficus-carica-bark", r"D:\FIGS\More Fig Pictures", "latex on gloves in sun"),
    "35": ("usda-phzm-southeast", r"D:\FIGS\Figs", "frost date note beside zone map"),
    "36": ("usda-phzm-southeast", r"D:\FIGS\Figs", "inland 8a vs coastal 8a same zone number"),
    "37": ("usda-phzm-southeast", r"D:\FIGS\Figs", "Piedmont vs Gulf vs Ozarks 8a"),
    "38": ("fig-dormant-canopy-pajara-03", r"D:\FIGS\Figs", "dieback height already chosen by winter"),
    "39": ("ficus-carica-canopy", r"D:\FIGS\Fig Fruit", "short-season main crop on new wood"),
    "40": ("usda-pom-celeste-1911", r"D:\FIGS\Fig Labels", "mixed varieties different cuts same yard"),
    "41": ("kohler-ficus-carica-plate", r"D:\FIGS\More Fig Pictures", "bud swell week last structural cuts"),
    "42": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "unwrap then prune order"),
    "43": ("usda-pom-winter-cutting", r"D:\FIGS\Damaged Cuttings", "reading last season's pruning scars"),
    "44": ("fig-dormant-canopy-pajara-01", r"D:\FIGS\Figs", "November shears in the drawer"),
    "45": ("ficus-carica-canopy", r"D:\FIGS\Fig Fruit", "Alma late ripener light summer hands"),
    "46": ("usda-pom-celeste-1911", r"D:\FIGS\Fig Fruit", "closed-eye vs open-eye canopy air"),
}

FIGURE_RE = re.compile(r"\n<figure>.*?</figure>\n", re.DOTALL)
DRAFT_GLOB = re.compile(r"^\d{2}-.+\.md$")


def parse_front(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        raise ValueError("missing front matter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("unclosed front matter")
    fm = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    return fm, body


def title_from_fm(fm: str) -> str:
    m = re.search(r'^title:\s*"(.*)"\s*$', fm, re.M)
    if m:
        return m.group(1)
    m = re.search(r"^title:\s*(.+)\s*$", fm, re.M)
    return m.group(1).strip() if m else "Fig pruning"


def alt_text(draft_id: str, title: str, asset_key: str) -> str:
    hooks = {
        "usda-phzm-southeast": "USDA zones 7–9 fig pruning — Southeast hardiness map for frost-calendar planning",
        "fig-winter-snow-hood": "Winter-wrapped Ficus carica — prune-after-wrap order for zones 7–8",
        "usda-pom-winter-cutting": "USDA fig pruning watercolor — dormant cut to outward bud, zones 7–9",
        "usda-pom-celeste-1911": "Celeste fig USDA plate — closed-eye variety winter pruning reference",
        "usda-pom-magnolia-1913": "Magnolia fig USDA plate — Brown Turkey class pruning reference",
        "ficus-carica-canopy": "Summer Ficus carica canopy — breba and main-crop pruning timing zones 8a–9b",
        "ficus-carica-bark": "Fig bark and latex — live-wood test before winter pruning",
        "fig-potted-tree-la-figuera": "Potted fig training cuts — container pruning zones 7–9",
        "fig-dormant-canopy-pajara-01": "Dormant fig canopy — structural pruning and leader thinning",
        "fig-dormant-canopy-pajara-02": "Leaf-off fig tree — ice damage and sucker management",
        "fig-dormant-canopy-pajara-03": "Winter fig wood — wait-for-green pruning in Zone 7a–8a",
        "kohler-ficus-carica-plate": "Ficus carica buds and fruit — breba wood ID for pruning",
    }
    base = hooks.get(asset_key, f"Fig pruning zones 7–9 — {title}")
    return f"{base} ({title})"


def caption_text(
    draft_id: str, title: str, asset_key: str, figs_folder: str, figs_note: str
) -> str:
    asset = ASSETS[asset_key]
    fig_id = f"prune.{draft_id}.{asset_key}"
    return (
        f"Figure 1. {title}. Staged stand-in ({fig_id}); {asset['credit']} "
        f"Prefer publish photo from {figs_folder} — {figs_note}. "
        f"See RIGHTS.md."
    )


def _yaml_quote(s: str) -> str:
    return s.replace('"', "'")


def yaml_figures_block(
    draft_id: str, asset_key: str, alt: str, figs_folder: str, figs_note: str
) -> str:
    asset = ASSETS[asset_key]
    fig_id = f"prune.{draft_id}.{asset_key}"
    return (
        "figures:\n"
        f"  - id: {fig_id}\n"
        f"    file: {asset['file']}\n"
        f'    alt: "{_yaml_quote(alt)}"\n'
        f'    figs_pick: "{_yaml_quote(figs_folder)}"\n'
        f'    figs_note: "{_yaml_quote(figs_note)}"\n'
    )


def figure_html(asset_key: str, alt: str, caption: str) -> str:
    a = ASSETS[asset_key]
    return (
        "<figure>\n"
        f'<img src="{a["file"]}" alt="{_yaml_quote(alt)}" '
        f'width="{a["width"]}" height="{a["height"]}" loading="lazy" decoding="async">\n'
        f"<figcaption>{caption}</figcaption>\n"
        "</figure>\n"
    )


def patch_file(path: Path) -> None:
    draft_id = path.name.split("-", 1)[0]
    if draft_id not in PLAN:
        raise KeyError(draft_id)
    asset_key, figs_folder, figs_note = PLAN[draft_id]
    text = path.read_text(encoding="utf-8")
    fm, body = parse_front(text)
    body = FIGURE_RE.sub("\n", body)
    if "figures:" in fm:
        fm = re.sub(r"\nfigures:\n(?:  .*\n)+", "\n", fm)
    title = title_from_fm(fm)
    alt = alt_text(draft_id, title, asset_key)
    cap = caption_text(draft_id, title, asset_key, figs_folder, figs_note)
    fm = fm.rstrip() + "\n" + yaml_figures_block(draft_id, asset_key, alt, figs_folder, figs_note)
    path.write_text(f"---\n{fm}\n---\n\n{figure_html(asset_key, alt, cap)}{body}", encoding="utf-8")


def main() -> None:
    for path in sorted(HERE.glob("*.md")):
        if path.name == "README.md":
            continue
        if not DRAFT_GLOB.match(path.name):
            continue
        patch_file(path)
        print("patched", path.name)


if __name__ == "__main__":
    main()
