#!/usr/bin/env python3
"""Embed <figure> blocks and figures: front matter for staged hardiness drafts."""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRAFTS = HERE / "drafts"

ASSETS = {
    "usda-phzm-southeast": {
        "file": "../assets/images/shared/usda-phzm-southeast.jpg",
        "width": 3300,
        "height": 2550,
        "credit": "USDA Plant Hardiness Zone Map (Southeast), PD.",
    },
    "fig-winter-snow-hood": {
        "file": "../assets/images/shared/fig-winter-snow-hood.jpg",
        "width": 2736,
        "height": 3648,
        "credit": "Photo: 4028mdk09, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "usda-pom-winter-cutting": {
        "file": "../assets/images/shared/usda-pom-winter-cutting.jpg",
        "width": 2707,
        "height": 4000,
        "credit": "USDA NAL Pomological Watercolor POM00001042, J. Marion Shull, PD.",
    },
    "usda-pom-celeste-1911": {
        "file": "../assets/images/shared/usda-pom-celeste-1911.jpg",
        "width": 2659,
        "height": 4000,
        "credit": "USDA NAL POM00007441 (Celeste), Mary Daisy Arnold, PD.",
    },
    "usda-pom-magnolia-1913": {
        "file": "../assets/images/shared/usda-pom-magnolia-1913.jpg",
        "width": 2625,
        "height": 4000,
        "credit": "USDA NAL POM00001043 (Magnolia), Mary Daisy Arnold, PD.",
    },
    "ficus-carica-canopy": {
        "file": "../assets/images/shared/ficus-carica-canopy.jpg",
        "width": 2848,
        "height": 4288,
        "credit": "Photo: Alvesgaspar, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "ficus-carica-bark": {
        "file": "../assets/images/shared/ficus-carica-bark.jpg",
        "width": 1317,
        "height": 1756,
        "credit": "Photo: Kenraiz, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "fig-potted-tree-la-figuera": {
        "file": "../assets/images/shared/fig-potted-tree-la-figuera.jpg",
        "width": 2816,
        "height": 2112,
        "credit": "Photo: Archaeodontosaurus, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "fig-dormant-canopy-pajara-01": {
        "file": "../assets/images/shared/fig-dormant-canopy-pajara-01.jpg",
        "width": 5616,
        "height": 3744,
        "credit": "Photo: Frank Vincentz, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "fig-dormant-canopy-pajara-02": {
        "file": "../assets/images/shared/fig-dormant-canopy-pajara-02.jpg",
        "width": 5616,
        "height": 3744,
        "credit": "Photo: Frank Vincentz, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "fig-dormant-canopy-pajara-03": {
        "file": "../assets/images/shared/fig-dormant-canopy-pajara-03.jpg",
        "width": 5616,
        "height": 3744,
        "credit": "Photo: Frank Vincentz, Wikimedia Commons, CC BY-SA 3.0.",
    },
    "kohler-ficus-carica-plate": {
        "file": "../assets/images/shared/kohler-ficus-carica-plate.jpg",
        "width": 1469,
        "height": 2318,
        "credit": "Köhler-type Ficus carica plate, Wikimedia Commons, PD.",
    },
}

# draft_id -> (asset_key, figs_folder, figs_shot_note)
PLAN: dict[str, tuple[str, str, str]] = {
    "d01": ("usda-phzm-southeast", r"D:\FIGS\Figs", "yard context showing inland 8a cold pocket"),
    "d02": ("usda-phzm-southeast", r"D:\FIGS\Figs", "min–max thermometer beside the shed"),
    "d03": ("kohler-ficus-carica-plate", r"D:\FIGS\More Fig Pictures", "winter twig with buds and bark close-up"),
    "d04": ("fig-dormant-canopy-pajara-01", r"D:\FIGS\Figs", "dieback height after a hard 8a night"),
    "d05": ("ficus-carica-canopy", r"D:\FIGS\Fig Fruit", "breba-sized fruit still on leafed wood"),
    "d06": ("ficus-carica-bark", r"D:\FIGS\More Fig Pictures", "wet bark after a cold rain — no sealed plastic"),
    "d07": ("fig-dormant-canopy-pajara-02", r"D:\FIGS\Figs", "wind-exposed cane on the north side"),
    "d08": ("fig-dormant-canopy-pajara-03", r"D:\FIGS\Figs", "same tree after a multi-night cold spell"),
    "d09": ("usda-pom-celeste-1911", r"D:\FIGS\Fig Labels", "catalog tag next to real winter wood"),
    "d10": ("usda-pom-magnolia-1913", r"D:\FIGS\Figs", "resprout after top kill — Chicago-class story"),
    "d11": ("usda-pom-celeste-1911", r"D:\FIGS\Fig Fruit", "closed-eye Celeste-class fruit if labeling is honest"),
    "d12": ("usda-pom-magnolia-1913", r"D:\FIGS\Fig Labels", "Brown Turkey look-alike wood in winter"),
    "d13": ("ficus-carica-canopy", r"D:\FIGS\Figs-summer-23", "LSU-type canopy before first real freeze"),
    "d14": ("ficus-carica-bark", r"D:\FIGS\Figs", "sulking variety with thin winter bark"),
    "d15": ("fig-dormant-canopy-pajara-01", r"D:\FIGS\Figs", "in-ground stool with crown mulch"),
    "d16": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "pot rim freeze line on dormant wood"),
    "d17": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "in-ground vs pot side-by-side"),
    "d18": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "first-year #3 before its first real winter"),
    "d19": ("ficus-carica-canopy", r"D:\FIGS\Figs", "south-wall fig stealing degrees"),
    "d20": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "raised-bed pot that still freezes at the rim"),
    "d21": ("usda-pom-celeste-1911", r"D:\FIGS\Figs", "three keepers after a normal 8a winter"),
    "d22": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "dormant wood ready — leaves off before the coat"),
    "d23": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "wrap that breathes — no sealed plastic tent"),
    "d24": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "leaf-filled hardware-cloth cage with dry leaves"),
    "d25": ("fig-dormant-canopy-pajara-02", r"D:\FIGS\Figs", "tip-and-lay branch under soil mound"),
    "d26": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "what not to use — black plastic removed"),
    "d27": ("fig-winter-snow-hood", r"D:\FIGS\Greenhouse photos", "heat cable and bulb — fire-safe spacing"),
    "d28": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "layers: cloth, leaves, hat — open bottom"),
    "d29": ("fig-winter-snow-hood", r"D:\FIGS\Greenhouse photos", "winter kit staged on the porch"),
    "d30": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "runaway wrap torn by dogs — repair shot"),
    "d31": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "Zone 7-style cage taller than an 8a stool needs"),
    "d32": ("ficus-carica-canopy", r"D:\FIGS\Figs-summer-23", "Zone 9 tree that should not stay wrapped"),
    "d33": ("usda-phzm-southeast", r"D:\FIGS\Figs", "8a vs 8b yard comparison if both exist"),
    "d34": ("fig-dormant-canopy-pajara-03", r"D:\FIGS\Figs", "midwinter check — mice, ice, loose cloth"),
    "d35": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "last drink before dormancy — dry pot weight"),
    "d36": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "garage line — dormant, barely moist"),
    "d37": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "pot buried to the rim in mulch"),
    "d38": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "large pot vs #3 freeze-through"),
    "d39": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "porch concrete vs soil line"),
    "d40": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "snow on wrap — open bottom visible"),
    "d41": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "after polar vortex — legal dieback height"),
    "d42": ("fig-dormant-canopy-pajara-02", r"D:\FIGS\Figs", "unwrap day with late-freeze cloth ready"),
    "d43": ("usda-pom-winter-cutting", r"D:\FIGS\Damaged Cuttings", "do not panic-prune — mark live wood"),
    "d44": ("usda-pom-winter-cutting", r"D:\FIGS\Damaged Cuttings", "stick autopsy on the bench"),
    "d45": ("fig-dormant-canopy-pajara-03", r"D:\FIGS\Figs", "late frost after leaf-out — cover staged"),
    "d46": ("fig-potted-tree-la-figuera", r"D:\FIGS\Greenhouse photos", "yard fig vs patio pot policy"),
    "d47": ("fig-dormant-canopy-pajara-01", r"D:\FIGS\Figs", "box-store hardy label vs March wood"),
    "d48": ("usda-phzm-southeast", r"D:\FIGS\Figs", "season calendar pinned near the tools"),
    "d49": ("ficus-carica-bark", r"D:\FIGS\Figs", "mulch at crown — not a substitute for wrap"),
    "d50": ("fig-winter-snow-hood", r"D:\FIGS\Figs", "before/after wrap comparison two winters"),
}

FIGURE_RE = re.compile(
    r"\n<figure>.*?</figure>\n",
    re.DOTALL,
)


def parse_front(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        raise ValueError("missing front matter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("unclosed front matter")
    fm = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    return fm, body


def title_from_fm(fm: str) -> str:
    for line in fm.splitlines():
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip()
    return "Zone 8a fig winter"


def alt_text(draft_id: str, title: str, asset_key: str) -> str:
    zone = "USDA Zone 8a fig cold hardiness"
    hooks = {
        "usda-phzm-southeast": f"{zone} — Southeast USDA Plant Hardiness Zone Map for 10–15°F winter planning",
        "fig-winter-snow-hood": f"{zone} fig tree winter protection — snow hood wrap on dormant Ficus carica",
        "usda-pom-winter-cutting": f"{zone} — dormant fig cutting and winter twig (USDA pomology plate)",
        "usda-pom-celeste-1911": f"Zone 8a winter fig variety — Celeste pomological watercolor (hardy common type)",
        "usda-pom-magnolia-1913": f"Eastern hardy fig type — Magnolia cultivar plate for Zone 7–8a siting",
        "ficus-carica-canopy": f"Ficus carica canopy — leaf-on context for Zone 8a breba and late-season cold",
        "ficus-carica-bark": f"Dormant fig bark and trunk — Zone 8a dieback and mulch-at-crown reference",
        "fig-potted-tree-la-figuera": f"Potted Ficus carica winter storage — Zone 8a garage and freeze-at-rim risk",
        "fig-dormant-canopy-pajara-01": f"Leaf-off Ficus carica in winter — Zone 8a dieback and in-ground stool",
        "fig-dormant-canopy-pajara-02": f"Dormant fig tree silhouette — Zone 8a unwrap and spring frost watch",
        "fig-dormant-canopy-pajara-03": f"Winter fig canopy without leaves — Zone 8a midwinter inspection",
        "kohler-ficus-carica-plate": f"Ficus carica buds and fruit morphology — what freezes first in Zone 8a",
    }
    base = hooks.get(asset_key, f"{zone} — {title}")
    return f"{base} ({title})"


def caption_text(
    draft_id: str, title: str, asset_key: str, figs_folder: str, figs_note: str
) -> str:
    asset = ASSETS[asset_key]
    fig_id = f"zone8a.{draft_id}.{asset_key}"
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
    fig_id = f"zone8a.{draft_id}.{asset_key}"
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
    draft_id = path.stem.split("-")[0]  # d22-when... -> d22? wrong
    draft_id = path.name[:3]  # d22
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
    block = figure_html(asset_key, alt, cap)
    path.write_text(f"---\n{fm}\n---\n\n{block}\n{body}", encoding="utf-8")


def main() -> None:
    for path in sorted(DRAFTS.glob("d*.md")):
        patch_file(path)
        print("patched", path.name)


if __name__ == "__main__":
    main()
