#!/usr/bin/env python3
"""Insert SEO YAML + <figure> blocks into fig-container-growing staged drafts."""

from __future__ import annotations

import re
from pathlib import Path

PACK = Path("content/fig-container-growing")

# draft filename -> (image rel under assets/images/, alt text for SEO)
FIGURES: dict[str, tuple[str, str]] = {
    "01-why-pots-in-zone-7-9.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Potted common fig in a movable container — the pot as a climate tool in USDA Zones 7 through 9",
    ),
    "02-how-big-the-pot.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Container-grown fig — pot volume in gallons decides whether the plant fruits or only grows leaves",
    ),
    "03-soil-mix-that-drains.md": (
        "shared/drainage/potting-soil-cc.jpg",
        "Bagged potting mix for containers — fig pots need a mix that drains fast between waterings",
    ),
    "04-pot-materials.md": (
        "shared/media/perlite-cc.jpg",
        "Perlite in potting media — plastic, fabric, clay, and wood pots each change drying speed on a patio",
    ),
    "05-summer-watering.md": (
        "shared/irrigation/watering-plants-cc.jpg",
        "Hand watering container plants — summer hose rhythm for potted figs without daily panic",
    ),
    "06-winter-watering-dormant.md": (
        "shared/irrigation/garden-hose-season-cc-by.jpg",
        "Garden hose at season close — dormant potted figs still need a quiet winter drink",
    ),
    "07-feeding-without-leaf-factory.md": (
        "shared/soil/compost-cc.jpg",
        "Finished compost — feed potted figs for fruit, not a nitrogen hedge on the patio",
    ),
    "08-zone-7-overwinter.md": (
        "shared/reference/ficus-carica-tree-cc.jpg",
        "Landscape common fig tree — overwintering potted wood through a USDA Zone 7 winter",
    ),
    "09-zone-8-awkward-middle.md": (
        "shared/reference/fig-tree-cc.jpg",
        "Fig tree in the landscape — Zone 8 winters that are usually mild until they are not",
    ),
    "10-zone-9-heat-and-roots.md": (
        "shared/trouble/fig-leaves-yellow-cc-by-sa.jpg",
        "Fig foliage in summer heat — cooked roots and stalled fruit on pots in Zone 9",
    ),
    "11-chicago-hardy-in-a-pot.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Potted fig form — Chicago Hardy and other cold-leaning varieties as movable patio plants",
    ),
    "12-brown-turkey-texas-everbearing.md": (
        "cultivars/mission-type-usda-pom-07410-pd.jpg",
        "USDA pomological plate of a brown fig type — staging reference, not a tagged Brown Turkey yard photo",
    ),
    "13-celeste-closed-eye.md": (
        "cultivars/celeste-usda-pom-07441-pd.jpg",
        "USDA pomological watercolor of Celeste-type fig — closed eye and rain resistance in pot culture",
    ),
    "14-true-dwarfs.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Small potted fig form — true dwarf cultivars sized for decks and balconies",
    ),
    "15-violette-de-bordeaux.md": (
        "cultivars/toulousienne-usda-pom-01168-pd.jpg",
        "USDA pomological plate — small dark fig type reference for Violette de Bordeaux in a pot",
    ),
    "16-lsu-figs.md": (
        "shared/reference/fig-fruit-halved-cc.jpg",
        "Halved common fig — LSU and Gulf-humidity varieties in container culture",
    ),
    "17-olympian-and-cold-leaning.md": (
        "shared/reference/ficus-carica-tree-cc.jpg",
        "Common fig tree — cold-leaning potted varieties such as Olympian in Zones 7–9",
    ),
    "18-pruning-bush-form.md": (
        "shared/reference/fig-tree-cc.jpg",
        "Fig tree canopy — bush form pruning that fits a patio pot without a pole saw",
    ),
    "19-breba-vs-main.md": (
        "shared/reference/fig-fruit-halved-cc.jpg",
        "Halved ripe fig — breba crop on old wood versus main crop on new growth in pots",
    ),
    "20-first-year.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Young potted fig — first container year without grocery-store harvest expectations",
    ),
    "21-fruit-drop.md": (
        "shared/reference/fig-fruit-halved-cc.jpg",
        "Common fig fruit — why potted trees abort figs after stress or uneven water",
    ),
    "22-splitting-and-souring.md": (
        "shared/reference/fig-fruit-halved-cc.jpg",
        "Halved fig fruit — split skins and sour hollows after drought then rain on patio pots",
    ),
    "23-fig-rust.md": (
        "shared/trouble/fig-rust-leaf-cc0.jpg",
        "Fig rust on foliage caused by Cerotelium fici — wet summer on container figs",
    ),
    "24-scale-and-mealybug.md": (
        "shared/diagnosis/ants-honeydew-cc.jpg",
        "Ants tending honeydew on a plant — scale and mealybug context on figs overwintered indoors",
    ),
    "25-birds-and-squirrels.md": (
        "shared/reference/fig-fruit-halved-cc.jpg",
        "Ripe fig fruit — birds and squirrels in the last week before harvest on patio trees",
    ),
    "26-rootbound-repot.md": (
        "shared/reference/fig-roots-cc-by-sa.jpg",
        "Shallow fig roots — root-bound pots, root-prune, or step up in gallon size",
    ),
    "27-dollies-weight-deck.md": (
        "shared/pots/wheelbarrow-garden-cc.jpg",
        "Wheelbarrow in a garden — moving heavy potted figs with dollies and deck weight limits",
    ),
    "28-sun-and-reflected-heat.md": (
        "shared/trouble/fig-leaves-yellow-cc-by-sa.jpg",
        "Fig leaves in strong sun — afternoon glare and reflected heat off patio concrete",
    ),
    "29-dormancy-and-wake.md": (
        "shared/reference/fig-tree-cc.jpg",
        "Fig tree form — leaf drop, dormancy, and spring wake for container plants",
    ),
    "30-late-freeze.md": (
        "shared/weather/frost-on-grass-cc.jpg",
        "Frost on grass — warm spell then a late freeze on potted figs in spring",
    ),
    "31-cuttings.md": (
        "cultivars/cutting-winter-twig-usda-pom-01042-pd.jpg",
        "USDA pomological plate of fig cutting wood — winter twigs for propagation",
    ),
    "32-buying-nursery-stock.md": (
        "shared/pots/nursery-pots-stack-cc.jpg",
        "Stacked nursery pots — buying container fig stock that is not a tourist plant",
    ),
    "33-yellow-leaves.md": (
        "shared/trouble/fig-leaves-yellow-cc-by-sa.jpg",
        "Yellowing fig leaves — drought, wet feet, salt, and rust sorted honestly on pots",
    ),
    "34-ripe-fig.md": (
        "shared/reference/fig-fruit-halved-cc.jpg",
        "Halved ripe common fig — knowing ripe from almost on patio-harvested fruit",
    ),
    "35-green-figs-wont-finish.md": (
        "shared/reference/ficus-carica-tree-cc.jpg",
        "Fig tree with developing fruit — green figs that never finish before frost in Zones 7–9",
    ),
    "36-month-by-month-zone-7.md": (
        "shared/irrigation/drip-irrigation-cc.jpg",
        "Drip irrigation line — month-by-month potted fig calendar for USDA Zone 7",
    ),
    "37-month-by-month-zone-8.md": (
        "shared/irrigation/watering-plants-cc.jpg",
        "Hand watering — month-by-month container fig rhythm for USDA Zone 8",
    ),
    "38-month-by-month-zone-9.md": (
        "shared/trouble/fig-leaves-yellow-cc-by-sa.jpg",
        "Fig foliage in heat — month-by-month potted fig care for USDA Zone 9",
    ),
    "39-fabric-grow-bags.md": (
        "shared/pots/fabric-grow-bag-cc.jpg",
        "Fabric grow bag for a tree — air-pruned roots and faster drying on a patio fig",
    ),
    "40-self-watering-and-ollas.md": (
        "shared/pots/flowerpot-saucer-cc.jpg",
        "Flowerpot with saucer — self-watering reservoirs and olla risks for fig roots",
    ),
    "41-nematodes-southern-soil.md": (
        "shared/nematodes/meloidogyne-usda-ars-cc-by.jpg",
        "Root-knot nematode on tomato roots USDA-ARS — why clean pot mix wins in southern soil",
    ),
    "42-espalier-and-column.md": (
        "shared/forms/espalier-fruit-wall-cc.jpg",
        "Espalier fruit trees on a wall — flat and column fig forms on a small patio",
    ),
    "43-salt-crust-and-tap.md": (
        "shared/soil/salinity-diagram-cc.png",
        "Soil salinization diagram — salt crust on pot rims from tap water and fertilizer",
    ),
    "44-first-frost-night.md": (
        "shared/weather/frost-on-grass-cc.jpg",
        "Frost on turf — the first frost night when potted figs must move under cover",
    ),
    "45-short-variety-list.md": (
        "shared/reference/ehret-ficus-carica-1771-pd.jpg",
        "Historical botanical plate of Ficus carica — short variety list for pots, not a catalog",
    ),
    "46-wind-tipping-stake.md": (
        "shared/reference/ficus-carica-tree-cc.jpg",
        "Common fig tree — wind, tipping, and staking tall potted plants on a deck",
    ),
    "47-a-small-collection.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Multiple potted fig forms — keeping a small collection without a patio jungle",
    ),
}

ORCHARD_SLOTS: dict[str, str] = {
    "01-why-pots-in-zone-7-9.md": r"D:\FIGS\Greenhouse photos",
    "02-how-big-the-pot.md": r"D:\FIGS\Greenhouse photos",
    "03-soil-mix-that-drains.md": r"D:\FIGS\Greenhouse photos",
    "04-pot-materials.md": r"D:\FIGS\Greenhouse photos",
    "05-summer-watering.md": r"D:\FIGS\Greenhouse photos",
    "06-winter-watering-dormant.md": r"D:\FIGS\Greenhouse photos",
    "07-feeding-without-leaf-factory.md": r"D:\FIGS\Figs",
    "08-zone-7-overwinter.md": r"D:\FIGS\Figs",
    "09-zone-8-awkward-middle.md": r"D:\FIGS\Figs",
    "10-zone-9-heat-and-roots.md": r"D:\FIGS\Figs-summer-23",
    "11-chicago-hardy-in-a-pot.md": r"D:\FIGS\Greenhouse photos",
    "12-brown-turkey-texas-everbearing.md": r"D:\FIGS\Fig Fruit",
    "13-celeste-closed-eye.md": r"D:\FIGS\Fig Fruit",
    "14-true-dwarfs.md": r"D:\FIGS\Greenhouse photos",
    "15-violette-de-bordeaux.md": r"D:\FIGS\Fig Fruit",
    "16-lsu-figs.md": r"D:\FIGS\Fig Fruit",
    "17-olympian-and-cold-leaning.md": r"D:\FIGS\Figs",
    "18-pruning-bush-form.md": r"D:\FIGS\Figs",
    "19-breba-vs-main.md": r"D:\FIGS\Fig Fruit",
    "20-first-year.md": r"D:\FIGS\Greenhouse photos",
    "21-fruit-drop.md": r"D:\FIGS\Fig Fruit",
    "22-splitting-and-souring.md": r"D:\FIGS\Fig Fruit",
    "23-fig-rust.md": r"D:\FIGS\Figs-summer-23",
    "24-scale-and-mealybug.md": r"D:\FIGS\Figs-summer-23",
    "25-birds-and-squirrels.md": r"D:\FIGS\Fig Fruit",
    "26-rootbound-repot.md": r"D:\FIGS\Greenhouse photos",
    "27-dollies-weight-deck.md": r"D:\FIGS\Greenhouse photos",
    "28-sun-and-reflected-heat.md": r"D:\FIGS\Figs-summer-23",
    "29-dormancy-and-wake.md": r"D:\FIGS\Figs",
    "30-late-freeze.md": r"D:\FIGS\Figs",
    "31-cuttings.md": r"D:\FIGS\Figs",
    "32-buying-nursery-stock.md": r"D:\FIGS\Greenhouse photos",
    "33-yellow-leaves.md": r"D:\FIGS\Figs-summer-23",
    "34-ripe-fig.md": r"D:\FIGS\Fig Fruit",
    "35-green-figs-wont-finish.md": r"D:\FIGS\Fig Fruit",
    "36-month-by-month-zone-7.md": r"D:\FIGS\Figs",
    "37-month-by-month-zone-8.md": r"D:\FIGS\Figs",
    "38-month-by-month-zone-9.md": r"D:\FIGS\Figs-summer-23",
    "39-fabric-grow-bags.md": r"D:\FIGS\Greenhouse photos",
    "40-self-watering-and-ollas.md": r"D:\FIGS\Greenhouse photos",
    "41-nematodes-southern-soil.md": r"D:\FIGS\Figs",
    "42-espalier-and-column.md": r"D:\FIGS\Figs",
    "43-salt-crust-and-tap.md": r"D:\FIGS\Greenhouse photos",
    "44-first-frost-night.md": r"D:\FIGS\Figs",
    "45-short-variety-list.md": r"D:\FIGS\Fig Fruit",
    "46-wind-tipping-stake.md": r"D:\FIGS\Figs",
    "47-a-small-collection.md": r"D:\FIGS\Greenhouse photos",
}


def slug_from_name(name: str) -> str:
    return name.replace(".md", "").split("-", 1)[1]


def title_from_fm(fm: str) -> str:
    for line in fm.splitlines():
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip()
    return slug_from_name("x-" + fm)


def meta_description(fm: str, name: str) -> str:
    title = title_from_fm(fm)
    return (
        f"{title}. Pot-grown common figs in USDA Zones 7–9 — container culture "
        f"draft (staged, not live)."
    ).replace('"', "'")


def upsert_yaml_field(fm: str, key: str, value: str) -> str:
    pattern = rf"^{key}:.*\n"
    line = f"{key}: {value}\n"
    if re.search(pattern, fm, flags=re.M):
        return re.sub(pattern, line, fm, count=1, flags=re.M)
    return fm.rstrip() + "\n" + line


def process(path: Path) -> None:
    name = path.name
    if name not in FIGURES:
        raise KeyError(name)
    rel_img, alt = FIGURES[name]
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"no front matter: {name}")
    end = text.find("\n---", 3)
    fm = text[3:end]
    body = text[end + 4 :].lstrip("\n")

    slug = slug_from_name(name)
    fm = upsert_yaml_field(fm, "slug", slug)
    fm = upsert_yaml_field(fm, "meta_description", meta_description(fm, name))
    folder = ORCHARD_SLOTS[name]
    folder_name = folder.split("\\")[-1]
    if "images:" not in fm:
        fm += (
            "\nimages:\n"
            f"- path: {folder}\n"
            "  caption: Staged hero still — replace PD fill before publish.\n"
            "  source: ours\n"
            f"  folder_pick: {folder_name}\n"
        )

    if "<figure>" in body:
        new_body = body
    else:
        block = (
            f"\n<!-- orchard_slot: {folder} — hero still before publish -->\n"
            f"<figure>\n"
            f'<img src="./assets/images/{rel_img}" alt="{alt}">\n'
            f"<figcaption>Figure 1. {alt}. PD/CC staging fill — swap for a Keith still from PHOTO_NOTES "
            f"(`D:\\FIGS` first) before publish. Credits: RIGHTS.md.</figcaption>\n"
            f"</figure>\n"
        )
        new_body = block + "\n" + body

    path.write_text(f"---\n{fm.strip()}\n---\n\n{new_body}", encoding="utf-8")


def main() -> None:
    drafts = sorted(PACK.glob("[0-9][0-9]-*.md"))
    missing = sorted({p.name for p in drafts} - set(FIGURES))
    if missing:
        raise SystemExit(f"missing figure map: {missing}")
    for path in drafts:
        process(path)
        print("OK", path.name)


if __name__ == "__main__":
    main()
