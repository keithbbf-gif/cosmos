#!/usr/bin/env python3
"""Insert SEO YAML + <figure> blocks into fig-soil-irrigation staged drafts."""

from __future__ import annotations

import re
from pathlib import Path

PACK = Path("content/fig-soil-irrigation")
DRAFTS = PACK / "drafts"

# draft filename -> (image rel under assets/images/, alt text for SEO)
FIGURES: dict[str, tuple[str, str]] = {
    "d01-figs-want-air-not-rich-dirt.md": (
        "shared/reference/fig-roots-cc-by-sa.jpg",
        "Shallow fig roots at the soil surface — common figs need air in the root zone, not a buried compost shaft",
    ),
    "d02-clay-is-a-pantry-until-it-is-a-bowl.md": (
        "shared/soil/clay-soil-cc.jpg",
        "Heavy clay soil holds water — fine in a pantry layer, deadly in a sealed planting bowl",
    ),
    "d03-sand-is-a-sieve-and-a-hotel.md": (
        "shared/soil/sandy-soil-cc.jpg",
        "Sandy soil drains fast — a sieve for water and a hotel for root-knot nematodes in zone 8a",
    ),
    "d04-ribbon-test-and-the-jar.md": (
        "shared/soil/texture-samples-cc.jpg",
        "Loam, sand, and clay soil texture samples — the jar and ribbon test before you buy a truck of mix",
    ),
    "d05-ph-is-a-window-not-a-religion.md": (
        "shared/soil/silt-loam-surface-cc.jpg",
        "Silt-loam surface texture — figs are lime-tolerant; pH is a window on salt and boron, not a cult",
    ),
    "d06-dig-fill-come-back-in-the-morning.md": (
        "shared/drainage/french-drain-cc.jpg",
        "French drain trench — if the planting hole is still a puddle tomorrow, fix drainage before the fig",
    ),
    "d07-salt-boron-and-the-well.md": (
        "shared/soil/salinity-diagram-cc.png",
        "Soil salinization diagram — excess sodium and boron show up on leaves before the well feels salty",
    ),
    "d08-what-a-soil-test-is-worth.md": (
        "shared/soil/texture-samples-cc.jpg",
        "Soil texture comparison — a county soil test names salt, pH, and texture; it does not sell you mix",
    ),
    "d09-compaction-is-a-soil-type-you-made.md": (
        "shared/soil/compacted-soil-cc.jpg",
        "Compacted soil surface — parking and foot traffic make a soil type harder than your native clay",
    ),
    "d10-what-the-top-two-inches-already-say.md": (
        "shared/soil/silt-loam-surface-cc.jpg",
        "Surface soil crust and texture — the top two inches tell you mulch and hose before the lab report",
    ),
    "d11-plant-high-clay-is-the-wall.md": (
        "shared/drainage/vegetated-berm-cc-by.jpg",
        "Vegetated berm — planting high on clay is the wall that keeps the crown out of the bowl",
    ),
    "d12-a-berm-is-not-a-raised-bed.md": (
        "shared/drainage/raised-bed-cc.jpg",
        "Raised bed with defined sides — not the same as a low berm on native grade in zone 8a",
    ),
    "d13-the-pretty-hole-is-a-bathtub.md": (
        "shared/drainage/potting-soil-cc.jpg",
        "Bagged potting mix — a pretty amended hole in clay is an underground pot with no drain holes",
    ),
    "d14-planting-depth-tamus-inches-and-the-berm.md": (
        "shared/reference/ficus-carica-tree-cc.jpg",
        "Common fig tree in the landscape — planting depth and berm shape matter more than variety hype",
    ),
    "d15-hardpan-and-the-first-two-feet.md": (
        "shared/soil/hardpan-profile-cc-by-sa.jpg",
        "Soil profile with dense layer — hardpan in the first two feet stops water and roots cold",
    ),
    "d16-when-a-french-drain-is-overkill.md": (
        "shared/drainage/french-drain-cc.jpg",
        "French drain installation — sometimes a berm is enough; sometimes you need a real drain line",
    ),
    "d17-do-not-add-sand-to-clay.md": (
        "shared/soil/texture-samples-cc.jpg",
        "Sand, loam, and clay samples — mixing sand into sticky clay makes concrete, not drainage",
    ),
    "d18-gypsum-will-not-drain-a-puddle.md": (
        "shared/soil/gypsum-load-cc-by.jpg",
        "Gypsum stockpile — gypsum adjusts chemistry on some sodic soils; it does not empty a bathtub hole",
    ),
    "d19-compost-as-a-topping-not-a-burial.md": (
        "shared/soil/compost-cc.jpg",
        "Finished compost — a thin topping for shallow fig roots, not a two-foot burial in clay",
    ),
    "d20-first-two-summers-in-the-hole.md": (
        "shared/irrigation/watering-plants-cc.jpg",
        "Hand watering a garden plant — the first two in-ground summers are still pot logic with no handles",
    ),
    "d21-shallow-roots-a-blanket-they-can-breathe.md": (
        "shared/reference/fig-roots-cc-by-sa.jpg",
        "Fig roots near the surface — mulch is a blanket on the mat, not a smother on the trunk",
    ),
    "d22-chips-hay-straw-leaves.md": (
        "shared/mulch/wood-chips-cc.jpg",
        "Wood chip mulch texture — chips, hay, and straw each change how fast the top two inches dry",
    ),
    "d23-keep-mulch-off-the-trunk.md": (
        "shared/mulch/volcano-mulching-cc-by.jpg",
        "Volcano mulch piled on a tree trunk — the habit that cooks bark and invites rot on figs",
    ),
    "d24-landscape-fabric-under-mulch.md": (
        "shared/mulch/landscape-fabric-era-cc.jpg",
        "Historic garden illustration — landscape fabric under mulch blocks the shallow root mat figs need",
    ),
    "d25-grass-is-a-competitor.md": (
        "shared/mulch/lawn-turf-cc.jpg",
        "Mowed lawn turf — grass at the drip line competes for water with shallow fig roots",
    ),
    "d26-compost-twice-mulch-all-year.md": (
        "shared/mulch/chips-on-bed-cc-by.jpg",
        "Wood chips on a garden bed — compost twice, mulch all year in humid zone 8a",
    ),
    "d27-rust-leaves-are-not-a-gift.md": (
        "shared/trouble/fig-rust-leaf-cc0.jpg",
        "Fig rust on foliage — rust litter under the tree is not free mulch for next year",
    ),
    "d28-mulch-changes-the-irrigation-clock.md": (
        "shared/mulch/straw-mulch-cc.jpg",
        "Straw mulch on a garden row — thick mulch slows evaporation and shifts your hose schedule",
    ),
    "d29-deep-and-infrequent-once-it-has-a-county.md": (
        "shared/irrigation/drip-irrigation-cc.jpg",
        "Drip irrigation line — deep, infrequent water once roots own the county, not the pot",
    ),
    "d30-year-one-water-is-a-different-job.md": (
        "shared/irrigation/watering-plants-cc.jpg",
        "Watering young plants — year-one fig water is establishment, not the July drought game",
    ),
    "d31-finger-not-tuesday.md": (
        "shared/irrigation/drip-irrigation-cc.jpg",
        "Drip emitter on irrigation tubing — check the top two inches with a finger, not the calendar",
    ),
    "d32-fruit-swell-is-not-the-drought-week.md": (
        "shared/reference/fig-fruit-halved-cc.jpg",
        "Halved common fig — fruit swell needs water; ripening week is a different hose decision",
    ),
    "d33-split-after-the-drought-then-storm.md": (
        "shared/irrigation/garden-hose-season-cc-by.jpg",
        "Garden hose at season close — split fruit often follows drought then a thunderstorm soak",
    ),
    "d34-overhead-water-and-rust.md": (
        "shared/irrigation/sprinkler-head-cc.jpg",
        "Sprinkler irrigation head — overhead water wets leaves and feeds rust in sticky zone 8a air",
    ),
    "d35-drip-soaker-hose-and-a-count.md": (
        "shared/irrigation/drip-irrigation-cc.jpg",
        "Drip irrigation — count gallons or minutes; soaker hose and emitters each wet a different footprint",
    ),
    "d36-afternoon-wilt-is-not-always-a-cry.md": (
        "shared/reference/fig-tree-cc.jpg",
        "Fig tree canopy — afternoon wilt on hot days is not always a call for more water",
    ),
    "d37-cut-water-to-ripen-the-california-argument.md": (
        "shared/irrigation/drip-irrigation-cc.jpg",
        "Drip line in a garden — California deficit-irrigation logic does not map to an Arkansas #3 pot",
    ),
    "d38-rain-souring-skip-a-cycle.md": (
        "shared/irrigation/garden-hose-season-cc-by.jpg",
        "Coiled garden hose — after a soaking rain, skip a cycle before sour roots in a heavy pot",
    ),
    "d39-water-before-a-hard-freeze.md": (
        "shared/irrigation/watering-plants-cc.jpg",
        "Watering before cold — moist soil holds heat around roots better than dry dust before a hard freeze",
    ),
    "d40-yellow-leaves-wet-dry-or-occupied.md": (
        "shared/trouble/fig-leaves-yellow-cc-by-sa.jpg",
        "Yellowing fig leaves — wet feet, drought, and rust each paint a different yellow pattern",
    ),
    "d41-yard-dirt-in-a-can-is-a-brick.md": (
        "shared/drainage/potting-soil-cc.jpg",
        "Bagged potting soil — yard clay in a container turns into a brick, not a fig mix",
    ),
    "d42-if-water-stands-on-top-the-pot-is-lying.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Potted common fig — if water pools on the mix surface, drainage and media are lying to you",
    ),
    "d43-promix-hp-and-the-seventy-percent-feel.md": (
        "shared/drainage/potting-soil-cc.jpg",
        "Commercial potting mix — Promix HP and ~70% field capacity are a feel, not a religion",
    ),
    "d44-moisture-control-mix-is-a-drowning-kit.md": (
        "shared/drainage/potting-soil-cc.jpg",
        "Moisture-retaining potting mix — moisture-control bags are a drowning kit in humid summers",
    ),
    "d45-coir-is-a-cup-language.md": (
        "shared/media/coir-fiber-cc-by-sa.jpg",
        "Coconut coir fiber — coir holds water like a cup; language matters when you compare to perlite",
    ),
    "d46-perlite-you-can-see.md": (
        "shared/media/perlite-cc.jpg",
        "Horticultural perlite — white particles you can see mean air space in a fig potting mix",
    ),
    "d47-lift-the-pot-and-what-the-pot-is.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Potted fig on a bench — lift the #3 or #5 to learn weight; the pot is part of the irrigation plan",
    ),
    "d48-saucers-collapse-and-pots-that-water-themselves.md": (
        "shared/media/potted-fig-cc-by-sa.jpg",
        "Container fig — saucers and self-watering pots keep roots wet longer than summer rain in 8a",
    ),
}

ORCHARD_SLOTS: dict[str, str] = {
    "d01-figs-want-air-not-rich-dirt.md": r"D:\FIGS\Figs",
    "d02-clay-is-a-pantry-until-it-is-a-bowl.md": r"D:\FIGS\Figs",
    "d03-sand-is-a-sieve-and-a-hotel.md": r"D:\FIGS\Figs",
    "d04-ribbon-test-and-the-jar.md": r"D:\FIGS\Figs",
    "d05-ph-is-a-window-not-a-religion.md": r"D:\FIGS\Figs",
    "d06-dig-fill-come-back-in-the-morning.md": r"D:\FIGS\Figs",
    "d07-salt-boron-and-the-well.md": r"D:\FIGS\Figs",
    "d08-what-a-soil-test-is-worth.md": r"D:\FIGS\Figs",
    "d09-compaction-is-a-soil-type-you-made.md": r"D:\FIGS\Greenhouse photos",
    "d10-what-the-top-two-inches-already-say.md": r"D:\FIGS\Figs-summer-23",
    "d11-plant-high-clay-is-the-wall.md": r"D:\FIGS\Figs",
    "d12-a-berm-is-not-a-raised-bed.md": r"D:\FIGS\Figs",
    "d13-the-pretty-hole-is-a-bathtub.md": r"D:\FIGS\Greenhouse photos",
    "d14-planting-depth-tamus-inches-and-the-berm.md": r"D:\FIGS\Figs",
    "d15-hardpan-and-the-first-two-feet.md": r"D:\FIGS\Figs",
    "d16-when-a-french-drain-is-overkill.md": r"D:\FIGS\Figs",
    "d17-do-not-add-sand-to-clay.md": r"D:\FIGS\Figs",
    "d18-gypsum-will-not-drain-a-puddle.md": r"D:\FIGS\Figs",
    "d19-compost-as-a-topping-not-a-burial.md": r"D:\FIGS\Figs",
    "d20-first-two-summers-in-the-hole.md": r"D:\FIGS\Figs",
    "d21-shallow-roots-a-blanket-they-can-breathe.md": r"D:\FIGS\Figs-summer-23",
    "d22-chips-hay-straw-leaves.md": r"D:\FIGS\Figs",
    "d23-keep-mulch-off-the-trunk.md": r"D:\FIGS\Figs",
    "d24-landscape-fabric-under-mulch.md": r"D:\FIGS\Figs",
    "d25-grass-is-a-competitor.md": r"D:\FIGS\Figs",
    "d26-compost-twice-mulch-all-year.md": r"D:\FIGS\Figs",
    "d27-rust-leaves-are-not-a-gift.md": r"D:\FIGS\Figs-summer-23",
    "d28-mulch-changes-the-irrigation-clock.md": r"D:\FIGS\Figs",
    "d29-deep-and-infrequent-once-it-has-a-county.md": r"D:\FIGS\Greenhouse photos",
    "d30-year-one-water-is-a-different-job.md": r"D:\FIGS\Figs",
    "d31-finger-not-tuesday.md": r"D:\FIGS\Greenhouse photos",
    "d32-fruit-swell-is-not-the-drought-week.md": r"D:\FIGS\Fig Fruit",
    "d33-split-after-the-drought-then-storm.md": r"D:\FIGS\Fig Fruit",
    "d34-overhead-water-and-rust.md": r"D:\FIGS\Figs-summer-23",
    "d35-drip-soaker-hose-and-a-count.md": r"D:\FIGS\Greenhouse photos",
    "d36-afternoon-wilt-is-not-always-a-cry.md": r"D:\FIGS\Figs-summer-23",
    "d37-cut-water-to-ripen-the-california-argument.md": r"D:\FIGS\Fig Fruit",
    "d38-rain-souring-skip-a-cycle.md": r"D:\FIGS\Greenhouse photos",
    "d39-water-before-a-hard-freeze.md": r"D:\FIGS\Greenhouse photos",
    "d40-yellow-leaves-wet-dry-or-occupied.md": r"D:\FIGS\Figs-summer-23",
    "d41-yard-dirt-in-a-can-is-a-brick.md": r"D:\FIGS\Greenhouse photos",
    "d42-if-water-stands-on-top-the-pot-is-lying.md": r"D:\FIGS\Greenhouse photos",
    "d43-promix-hp-and-the-seventy-percent-feel.md": r"D:\FIGS\Greenhouse photos",
    "d44-moisture-control-mix-is-a-drowning-kit.md": r"D:\FIGS\Greenhouse photos",
    "d45-coir-is-a-cup-language.md": r"D:\FIGS\Greenhouse photos",
    "d46-perlite-you-can-see.md": r"D:\FIGS\Greenhouse photos",
    "d47-lift-the-pot-and-what-the-pot-is.md": r"D:\FIGS\Greenhouse photos",
    "d48-saucers-collapse-and-pots-that-water-themselves.md": r"D:\FIGS\Greenhouse photos",
}

META: dict[str, str] = {
    "d01-figs-want-air-not-rich-dirt.md": "Figs want airflow in the root zone, not a truck of rich garden soil. Zone 8a clay, drainage, and what Mediterranean roots expect.",
    "d02-clay-is-a-pantry-until-it-is-a-bowl.md": "Clay soil for figs in zone 8a: when heavy ground works, when a clay bowl drowns roots, and why rich is not the same as open.",
    "d03-sand-is-a-sieve-and-a-hotel.md": "Sandy soil and figs: fast drainage, nematode risk on sand, and why zone 8a growers should not envy beach dirt.",
    "d04-ribbon-test-and-the-jar.md": "Ribbon test and jar test for soil texture before you plant a fig — read clay, sand, and loam with your hands.",
    "d05-ph-is-a-window-not-a-religion.md": "Soil pH for common figs: lime tolerance, boron and salt on the lab report, and why pH is not a cult in zone 8a.",
    "d06-dig-fill-come-back-in-the-morning.md": "The fig planting-hole drainage test: fill with water, come back in the morning. If it is still a puddle, fix the hole first.",
    "d07-salt-boron-and-the-well.md": "Well water, soil salt, and boron sensitivity for figs — what yellow leaves and edge burn mean in zone 8a.",
    "d08-what-a-soil-test-is-worth.md": "What a county soil test is worth for fig growers: texture, salt, pH, and what it cannot buy you at the garden center.",
    "d09-compaction-is-a-soil-type-you-made.md": "Soil compaction under figs: parking, foot traffic, and wet clay turned into a hardpan you made yourself.",
    "d10-what-the-top-two-inches-already-say.md": "Read the top two inches of soil before you water a fig — crust, color, and mulch tell you wet, dry, or sour.",
    "d11-plant-high-clay-is-the-wall.md": "Plant figs high on clay in zone 8a — berm and crown height keep the trunk out of the bowl that holds rain.",
    "d12-a-berm-is-not-a-raised-bed.md": "A planting berm is not a raised bed for figs — sides, drainage, and when each shape wins in the South.",
    "d13-the-pretty-hole-is-a-bathtub.md": "Amended planting holes in clay are bathtubs — Promix in a pit without drainage drowns fig roots after the first big rain.",
    "d14-planting-depth-tamus-inches-and-the-berm.md": "Fig planting depth on a berm: Texas A&M inches, crown height, and why the pretty deep hole is wrong.",
    "d15-hardpan-and-the-first-two-feet.md": "Hardpan and the first two feet under a fig — when water stops and roots hit a wall in zone 8a clay.",
    "d16-when-a-french-drain-is-overkill.md": "French drains for figs: when a berm is enough, when you need tile, and when you are fixing the wrong yard.",
    "d17-do-not-add-sand-to-clay.md": "Why you do not add sand to clay for fig planting — brick soil, not drainage, in humid zone 8a.",
    "d18-gypsum-will-not-drain-a-puddle.md": "Gypsum and fig drainage myths — chemistry on some sodic soils, not a fix for a bathtub planting hole.",
    "d19-compost-as-a-topping-not-a-burial.md": "Compost on figs: thin topping for shallow roots, not a two-foot burial that holds water in clay.",
    "d20-first-two-summers-in-the-hole.md": "Watering a new in-ground fig: the first two summers in zone 8a are still establishment, not drought games.",
    "d21-shallow-roots-a-blanket-they-can-breathe.md": "Shallow fig roots and mulch — a breathable blanket on the mat, not a volcano on the trunk.",
    "d22-chips-hay-straw-leaves.md": "Mulch choices for figs: wood chips, hay, straw, and leaves — how each shifts drying in zone 8a.",
    "d23-keep-mulch-off-the-trunk.md": "Keep mulch off the fig trunk — volcano mulching, bark rot, and the air gap the crown needs.",
    "d24-landscape-fabric-under-mulch.md": "Landscape fabric under mulch and figs — why the shallow root mat needs to breathe in humid 8a.",
    "d25-grass-is-a-competitor.md": "Grass at the drip line competes with fig roots for water — lawn vs tree in zone 8a summers.",
    "d26-compost-twice-mulch-all-year.md": "Compost twice, mulch all year for potted and in-ground figs in the humid South.",
    "d27-rust-leaves-are-not-a-gift.md": "Fig rust litter is not free mulch — rake infected leaves instead of recycling rust under zone 8a trees.",
    "d28-mulch-changes-the-irrigation-clock.md": "Mulch changes how often you water figs — evaporation, hose math, and zone 8a thunderstorm weeks.",
    "d29-deep-and-infrequent-once-it-has-a-county.md": "Deep, infrequent irrigation for established figs — drip and soaker logic once roots own the county.",
    "d30-year-one-water-is-a-different-job.md": "Year-one fig watering in zone 8a — establishment schedule vs the July drought week on mature trees.",
    "d31-finger-not-tuesday.md": "Water figs when the top two inches say so — finger test beats Tuesday on the calendar in 8a.",
    "d32-fruit-swell-is-not-the-drought-week.md": "Fruit swell needs water on figs; the ripening drought week is a different hose decision in zone 8a.",
    "d33-split-after-the-drought-then-storm.md": "Split figs after drought then rain — skip a cycle, storm soak, and zone 8a summer fruit quality.",
    "d34-overhead-water-and-rust.md": "Overhead sprinklers, wet leaves, and fig rust in humid zone 8a — drip when you can.",
    "d35-drip-soaker-hose-and-a-count.md": "Drip vs soaker hose for figs — count minutes or gallons instead of guessing in zone 8a.",
    "d36-afternoon-wilt-is-not-always-a-cry.md": "Afternoon wilt on figs is not always thirst — heat, new wood, and wet feet in zone 8a.",
    "d37-cut-water-to-ripen-the-california-argument.md": "Deficit irrigation for fig ripening — California logic vs Arkansas pots and humid 8a main crop.",
    "d38-rain-souring-skip-a-cycle.md": "After heavy rain on potted figs, skip a watering cycle before sour roots in zone 8a humidity.",
    "d39-water-before-a-hard-freeze.md": "Water figs before a hard freeze in zone 8a — moist soil, crown protection, and what extension guides say.",
    "d40-yellow-leaves-wet-dry-or-occupied.md": "Yellow fig leaves: wet feet, drought stress, rust, or salt — tell them apart in zone 8a.",
    "d41-yard-dirt-in-a-can-is-a-brick.md": "Do not fill fig pots with yard clay — container media that drains in zone 8a summers.",
    "d42-if-water-stands-on-top-the-pot-is-lying.md": "Water pooling on potting mix means the fig pot is lying — drainage, perlite, and lift test in 8a.",
    "d43-promix-hp-and-the-seventy-percent-feel.md": "Promix HP and ~70% field capacity for fig pots — FigRoots mix language without a new trial.",
    "d44-moisture-control-mix-is-a-drowning-kit.md": "Moisture-control potting mix drowns figs in humid zone 8a — why plain draining mix wins in #3 pots.",
    "d45-coir-is-a-cup-language.md": "Coconut coir vs perlite in fig pots — water-holding language for zone 8a collectors.",
    "d46-perlite-you-can-see.md": "Perlite in fig potting mix — visible air space and drainage for 3–5 gallon pots in 8a.",
    "d47-lift-the-pot-and-what-the-pot-is.md": "Lift the fig pot to learn weight — #3 and #5 gallons as part of irrigation in zone 8a.",
    "d48-saucers-collapse-and-pots-that-water-themselves.md": "Saucers and self-watering pots for figs — wet feet, collapse, and summer rain in zone 8a.",
}


def slug_from_name(name: str) -> str:
    return name.replace(".md", "").split("-", 1)[1]


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
    fm = upsert_yaml_field(fm, "meta_description", META[name].replace('"', "'"))
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
            f'<img src="../assets/images/{rel_img}" alt="{alt}">\n'
            f"<figcaption>Figure 1. {alt}. PD/CC staging fill — swap for a Keith still from PHOTO_NOTES "
            f"(`D:\\FIGS` first) before publish. Credits: RIGHTS.md.</figcaption>\n"
            f"</figure>\n"
        )
        new_body = block + "\n" + body

    path.write_text(f"---\n{fm.strip()}\n---\n\n{new_body}", encoding="utf-8")


def main() -> None:
    missing = sorted(set(f.name for f in DRAFTS.glob("d*.md")) - set(FIGURES))
    if missing:
        raise SystemExit(f"missing figure map: {missing}")
    for path in sorted(DRAFTS.glob("d*.md")):
        process(path)
        print("OK", path.name)


if __name__ == "__main__":
    main()
