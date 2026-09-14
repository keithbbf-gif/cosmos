#!/usr/bin/env python3
"""Insert <figure> blocks with SEO alt + figcaption into FigRoots draft markdown."""

from __future__ import annotations

import re
from pathlib import Path

PACKS = {
    "pests": Path("content/fig-pests-diseases-blog"),
    "varieties": Path("content/fig-varieties-profiles"),
}

# slug -> (relative image under assets/images/, alt text stem)
PESTS_PRIMARY: dict[str, tuple[str, str]] = {
    "name-the-fig-problem-before-the-bottle": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Halved common fig showing pulp and ostiole — start with the symptom, not the spray bottle",
    ),
    "root-knot-nematodes-what-roots-look-like": (
        "shared/nematodes/galled-roots-tomato-cc0.jpg",
        "Swollen root knots from root-knot nematode on a susceptible host — same galling pattern on fig roots",
    ),
    "sandy-zone-8a-root-knot-figs": (
        "shared/nematodes/root-knot-nodules-pd.jpg",
        "Root-knot nematode galls on feeder roots in sandy soil",
    ),
    "what-does-not-kill-fig-nematodes": (
        "shared/nematodes/meloidogyne-usda-ars-cc-by.jpg",
        "Juvenile root-knot nematode entering a root — why most homeowner drenches miss the biology",
    ),
    "living-with-galled-fig-roots": (
        "shared/nematodes/galled-roots-tomato-cc0.jpg",
        "Galled roots on a living tree — management is cultural, not a single soil drench",
    ),
    "old-tomato-okra-ground-not-fig-hole": (
        "shared/nematodes/root-knot-nodules-pd.jpg",
        "Nematode galls — why old tomato and okra ground is a bad fig hole in zone 8a",
    ),
    "county-nematode-sample-not-facebook": (
        "shared/nematodes/meloidogyne-usda-ars-cc-by.jpg",
        "Root-knot nematode on a root — what a county soil sample is actually looking for",
    ),
    "fig-rust-orange-dust-august": (
        "shared/rust/cerotelium-fici-underside-cc0.jpg",
        "Orange rust pustules on the underside of a fig leaf — Cerotelium fici in humid August air",
    ),
    "rust-mosaic-sunburn-mite-lookalikes": (
        "shared/rust/cerotelium-fici-leaf-cc0.jpg",
        "Fig rust leaf spots next to healthy green — compare before you spray the wrong problem",
    ),
    "fig-rust-spots-spray-is-late": (
        "shared/rust/cerotelium-fici-leaf-cc0.jpg",
        "Yellow and rusty angular spots on fig foliage — fungicide is usually late once this is loud",
    ),
    "rake-is-the-fig-rust-program": (
        "shared/rust/cerotelium-fici-underside-cc0.jpg",
        "Rust pustules under a fig leaf — why raking litter beats fogging ripe fruit",
    ),
    "fig-rust-copper-label-is-law": (
        "shared/rust/cerotelium-fici-leaf-cc0.jpg",
        "Fig rust on leaves — any copper talk still has to match the label and the host",
    ),
    "fig-rust-late-flush-winter-cold-8a": (
        "shared/rust/cerotelium-fici-underside-cc0.jpg",
        "Late-season rust defoliation — soft winter flush is the zone 8a penalty",
    ),
    "lsu-figs-not-a-rust-vaccine": (
        "shared/rust/cerotelium-fici-leaf-cc0.jpg",
        "Rust on fig leaves — LSU resistance is relative, not immunity",
    ),
    "fig-mosaic-not-a-death-sentence": (
        "shared/mosaic/fig-mosaic-leaf-cc-by-sa.jpg",
        "Mosaic pattern on a fig leaf — oak-leaf yellowing is not always a pull-the-tree verdict",
    ),
    "aceria-ficus-fig-mosaic-mite": (
        "shared/mosaic/fig-mosaic-leaf-cc-by-sa.jpg",
        "Fig mosaic symptoms on foliage — Aceria fig mite is the piece most blogs skip",
    ),
    "cannot-spray-fig-mosaic-off-a-tree": (
        "shared/mosaic/fig-mosaic-leaf-cc-by-sa.jpg",
        "Mosaic-affected fig leaf — viruses and mites do not rinse off with a hose",
    ),
    "clean-fig-stock-vs-inherited-mosaic": (
        "shared/mosaic/fig-mosaic-leaf-cc-by-sa.jpg",
        "Inherited mosaic pattern on fig leaves — why clean wood matters at purchase",
    ),
    "heat-makes-fig-mosaic-louder": (
        "shared/mosaic/fig-mosaic-leaf-cc-by-sa.jpg",
        "Heat-stressed fig leaf showing mosaic pattern — August makes the paint job louder",
    ),
    "green-june-figeater-japanese-beetle-figs": (
        "shared/beetles/green-june-beetle-cc-by-sa.jpg",
        "Green June beetle — not the same insect as Japanese beetle on figs",
    ),
    "sap-beetles-fig-sour-necklace": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Ripe fig cross-section — souring starts at the eye, not as a leaf disease",
    ),
    "handpick-beetles-dont-fog-ripe-figs": (
        "shared/beetles/green-june-beetle-cc-by-sa.jpg",
        "Green June beetle on fruit — hand-pick ripe figs instead of fogging the canopy",
    ),
    "japanese-beetle-traps-not-fig-control": (
        "shared/beetles/japanese-beetle-cc-by.jpg",
        "Japanese beetle — why yard traps attract more beetles than they save on figs",
    ),
    "compost-pile-fig-chafer-grubs": (
        "shared/beetles/green-june-beetle-cc-by-sa.jpg",
        "Green June beetle adult — compost and organic matter feed the grub cycle",
    ),
    "birds-write-the-fig-harvest-calendar": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Ripe fig interior — birds write the harvest calendar on dark fruit first",
    ),
    "fig-bird-netting-that-works": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Ripe fig — netting has to touch the ground, not just drape the shoulders",
    ),
    "green-figs-not-bird-proof": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Green-skinned ripe fig flesh — color fools people, not mockingbirds",
    ),
    "bagging-individual-figs-birds": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Fig fruit cross-section — bagging a few figs beats fighting every bird on the tree",
    ),
    "squirrels-raccoons-deer-fig-harvest": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Ripe fig — mammals take fruit after birds teach them the tree",
    ),
    "fig-souring-is-yeast-not-a-curse": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Split ripe fig interior — souring is yeast at the eye, not a leaf curse",
    ),
    "fig-scale-under-bark-flake": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Fig fruit reference — scale hides under bark flakes, not on the pulp",
    ),
    "spider-mites-dry-zone-8a-august": (
        "shared/diagnosis/two-spotted-spider-mite-csiro.jpg",
        "Two-spotted spider mite — dry August pots and dusty leaves in zone 8a",
    ),
    "ants-honeydew-fig-not-a-disease": (
        "shared/diagnosis/ants-honeydew-cc.jpg",
        "Ants harvesting honeydew on leaves — a symptom of sap feeders, not a fig disease",
    ),
    "fig-anthracnose-leaf-blight-not-rust": (
        "shared/rust/cerotelium-fici-leaf-cc0.jpg",
        "Leaf spots on fig foliage — compare anthracnose and blight to rust before you treat",
    ),
    "fig-limb-blight-frost-stubs": (
        "shared/diagnosis/fig-fruit-halved-reference.jpg",
        "Fig fruit on a stressed tree — limb blight often follows frost stubs and wet wood",
    ),
    "fig-armillaria-mushroom-root-rot": (
        "shared/diagnosis/armillaria-rhizomorphs-cc-by-sa.jpg",
        "Armillaria rhizomorphs at a tree base — mushroom root rot kills standing figs",
    ),
    "zone-8a-fig-pest-scout-calendar": (
        "shared/rust/cerotelium-fici-leaf-cc0.jpg",
        "Fig rust in late summer — one line on an 8a scout calendar",
    ),
    "photograph-fig-problem-for-county-clinic": (
        "shared/mosaic/fig-mosaic-leaf-cc-by-sa.jpg",
        "Fig leaf symptoms — what to photograph before you mail the county clinic",
    ),
    "kids-pets-dont-fog-fig-yard": (
        "shared/beetles/japanese-beetle-cc-by.jpg",
        "Beetle on plants — do not fog ripe figs where kids and pets eat",
    ),
    "fig-pests-after-tropical-rain-week": (
        "shared/rust/cerotelium-fici-underside-cc0.jpg",
        "Rust after a wet week — humidity stacks beetle, rust, and souring problems",
    ),
    "black-fig-fly-arkansas-reader": (
        "shared/biosecurity/oriental-fruit-fly-cc.jpg",
        "Exotic fruit fly — why Arkansas readers should know Bactrocera reports",
    ),
    "when-to-pull-a-fig-tree": (
        "shared/nematodes/galled-roots-tomato-cc0.jpg",
        "Galled roots — one honest reason to pull a fig instead of buying another bottle",
    ),
    "winter-sanitation-after-fig-rust": (
        "shared/rust/cerotelium-fici-underside-cc0.jpg",
        "Rusty fig leaves — winter sanitation is next year's rust program",
    ),
    "fig-irrigation-as-pest-management": (
        "shared/rust/cerotelium-fici-leaf-cc0.jpg",
        "Wet foliage and rust — why irrigation timing is pest management in 8a",
    ),
    "fig-thread-blight-vs-rust": (
        "shared/rust/cerotelium-fici-leaf-cc0.jpg",
        "Early-season leaf spots — thread blight and rust are not the same spray decision",
    ),
}

VARIETY_PRIMARY: dict[str, tuple[str, str]] = {
    "brown-turkey": (
        "cultivars/nameless-usda-pom-01044-pd.jpg",
        "USDA pomological watercolor of a brown common fig type — reference plate, not PapaFig's tagged tree",
    ),
    "celeste": (
        "cultivars/celeste-usda-pom-07441-pd.jpg",
        "USDA Celeste fig watercolor from Cape Charles, Virginia, 1911 — reference cultivar plate",
    ),
    "black-mission": (
        "cultivars/mission-type-usda-pom-07410-pd.jpg",
        "USDA Mission-type fig watercolor — historic reference, not a grocery Mission photo",
    ),
    "kadota": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "USDA pomological plate of a green Kadota-type fig — reference only",
    ),
    "calimyrna": (
        "cultivars/calimyrna-usda-pom-07440-pd.jpg",
        "USDA Calimyrna watercolor, Fresno 1912 — Smyrna-type reference plate",
    ),
    "lsu-gold": (
        "shared/reference/ehret-ficus-carica-1771-pd.jpg",
        "Ehret botanical plate of Ficus carica — LSU Gold needs a D:\\FIGS still; not a Commons stand-in",
    ),
    "lsu-purple": (
        "shared/reference/ehret-ficus-carica-1771-pd.jpg",
        "Ficus carica botanical reference — swap for D:\\FIGS\\Fig Fruit when LSU Purple is plated",
    ),
    "lsu-champagne": (
        "shared/reference/ehret-ficus-carica-1771-pd.jpg",
        "Generic Ficus carica plate — Champagne/Golden Celeste fruit must come from D:\\FIGS",
    ),
    "lsu-tiger": (
        "shared/reference/ehret-ficus-carica-1771-pd.jpg",
        "Botanical Ficus carica reference — Tiger stripe belongs on immature fruit from D:\\FIGS",
    ),
    "lsu-orourke": (
        "cultivars/celeste-usda-pom-07441-pd.jpg",
        "Celeste-type USDA plate — O'Rourke hangs like Improved Celeste; plate our fruit from D:\\FIGS",
    ),
    "lsu-scotts-black": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "USDA Royal Black watercolor — dark LSU-type reference, not Scott's Black in Keith's yard",
    ),
    "lsu-hollier": (
        "shared/reference/ehret-ficus-carica-1771-pd.jpg",
        "Ficus carica botanical plate — Hollier yellow fruit must be photographed on site",
    ),
    "lsu-jack-lily": (
        "shared/reference/ehret-ficus-carica-1771-pd.jpg",
        "Botanical fig reference — Jack Lily tight-eye fruit from D:\\FIGS\\FigRoots or Fig Fruit",
    ),
    "chicago-hardy": (
        "cultivars/cutting-winter-twig-usda-pom-01042-pd.jpg",
        "USDA fig cutting / winter twig watercolor — resprout story for Chicago Hardy",
    ),
    "violette-de-bordeaux": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Dark fig USDA reference plate — Violette de Bordeaux needs D:\\FIGS fruit for the hero",
    ),
    "panache": (
        "shared/reference/holtzbecher-ficus-carica-pd.jpg",
        "Historic Ficus carica painting — Panache stripes must be our immature fruit, not this plate",
    ),
    "desert-king": (
        "cultivars/cutting-winter-twig-usda-pom-01042-pd.jpg",
        "Fig cutting on old wood — Desert King breba context; shoot D:\\FIGS\\Breba 2025",
    ),
    "peters-honey": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Green-yellow USDA fig type — honey figs need D:\\FIGS Lattarula / Italian Honey tags",
    ),
    "alma": (
        "cultivars/celeste-usda-pom-07441-pd.jpg",
        "Closed-eye Celeste-type USDA plate — Alma tight eye after rain from D:\\FIGS",
    ),
    "ronde-de-bordeaux": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Small dark fig USDA reference — Ronde de Bordeaux bowl shots from D:\\FIGS",
    ),
    "malta-black": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Dark fig USDA plate — Malta Black hero must be D:\\FIGS\\Malta_Black_Fig only",
    ),
    "negra-dagde": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Dark berry-type USDA reference — Negra d'Agde fruit from D:\\FIGS or FigRoots reviews",
    ),
    "red-sicilian": (
        "cultivars/toulousienne-usda-pom-01168-pd.jpg",
        "USDA Toulousienne plate — Bordeaux-family reference for Red Sicilian",
    ),
    "nuestra-senora-del-carmen": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Large green USDA fig type — NSDC split-after-rain from D:\\FIGS",
    ),
    "olympian": (
        "cultivars/mission-type-usda-pom-07410-pd.jpg",
        "Mission-type USDA watercolor — Olympian large purple from D:\\FIGS\\Breba 2025 if present",
    ),
    "flanders": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Striped green-yellow USDA reference — Flanders violet stripes from D:\\FIGS",
    ),
    "conadria": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Green pyriform USDA fig — Conadria freeze-resprout from D:\\FIGS",
    ),
    "white-marseilles": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Blanche / Marseilles green-yellow USDA type — tag pile from D:\\FIGS\\Fig Labels",
    ),
    "madeleine-des-deux-saisons": (
        "cultivars/cutting-winter-twig-usda-pom-01042-pd.jpg",
        "Fig wood watercolor — Madeleine two-season claim needs D:\\FIGS breba proof",
    ),
    "col-de-dame-noire": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Dark late fig USDA reference — Col de Dame Noire from D:\\FIGS",
    ),
    "col-de-dame-blanc": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Green fig USDA plate — Col de Dame Blanc honey cut from D:\\FIGS",
    ),
    "bourjassotte-grise": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Gray-violet dark fig USDA reference — Bourjassotte Grise bloom from D:\\FIGS",
    ),
    "noire-de-caromb": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Dark productive fig USDA type — Noire de Caromb eye-after-rain from D:\\FIGS",
    ),
    "pastiliere": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Early dark USDA fig reference — Pastilière drops from D:\\FIGS",
    ),
    "dalmatie": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Large green USDA fig — Dalmatie late strawberry cut from D:\\FIGS",
    ),
    "verte": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Grass-green fig USDA type — Verte split fruit from D:\\FIGS",
    ),
    "smith": (
        "cultivars/fig-x1-cross-section-usda-pom-07442-pd.jpg",
        "USDA fig cross-section watercolor — Smith strawberry-type from D:\\FIGS",
    ),
    "excel": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Yellow Kadota-hybrid USDA reference — Excel early trial from D:\\FIGS",
    ),
    "hunt": (
        "cultivars/cutting-winter-twig-usda-pom-01042-pd.jpg",
        "Long peduncle story needs D:\\FIGS — USDA twig plate for winter context only",
    ),
    "magnolia": (
        "cultivars/magnolia-usda-pom-01043-pd.jpg",
        "USDA Magnolia fig watercolor, Arlington Farm 1913 — preserve type reference plate",
    ),
    "black-madeira": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Dark late berry USDA plate — never a marketplace hero; D:\\FIGS fruit only",
    ),
    "adriatic": (
        "cultivars/fig-x1-cross-section-usda-pom-07442-pd.jpg",
        "Green fig cross-section USDA watercolor — Adriatic strawberry pulp from D:\\FIGS",
    ),
    "yellow-long-neck": (
        "cultivars/kadota-type-usda-pom-07443-pd.jpg",
        "Long-neck types need D:\\FIGS\\Fig Labels — USDA green fig reference only",
    ),
    "syrian-dark-2": (
        "cultivars/royal-black-usda-pom-01045-pd.jpg",
        "Small dark tight-eye USDA reference — Syrian Dark from D:\\FIGS",
    ),
    "maryland-berry": (
        "cultivars/fig-x1-cross-section-usda-pom-07442-pd.jpg",
        "Berry-type cross-section USDA plate — Maryland Berry must be Keith's plated fruit",
    ),
    "italian-258": (
        "shared/reference/ehret-ficus-carica-1771-pd.jpg",
        "I-258 tag from D:\\FIGS\\Fig Labels — Ehret plate until honey cut is plated",
    ),
}

FIGCAPTION_TAIL = (
    " PD/CC fill for staging. Replace with a Keith still from PHOTO_NOTES (`D:\\FIGS` first) "
    "before publish. Full credits: RIGHTS.md."
)


def slug_from_draft(text: str) -> str | None:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    for line in m.group(1).splitlines():
        if line.startswith("slug:"):
            return line.split(":", 1)[1].strip()
    return None


def folder_pick_from_draft(text: str) -> str | None:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    block = m.group(1)
    fm_pick = re.search(r"folder_pick:\s*([^\n]+)", block)
    if fm_pick:
        return fm_pick.group(1).strip().strip('"')
    return None


def build_figure(rel_img: str, alt: str, fig_num: int, folder_pick: str | None) -> str:
    src = f"../assets/images/{rel_img}"
    cap = f"Figure {fig_num}. {alt}.{FIGCAPTION_TAIL}"
    slot = ""
    if folder_pick:
        slot = f"\n<!-- orchard_slot: D:\\FIGS\\{folder_pick} — hero still before publish -->\n"
    return (
        f"{slot}<figure>\n"
        f'<img src="{src}" alt="{alt}">\n'
        f"<figcaption>{cap}</figcaption>\n"
        f"</figure>\n\n"
    )


def embed_pack(pack_key: str, mapping: dict[str, tuple[str, str]]) -> int:
    pack = PACKS[pack_key]
    drafts = pack / "drafts"
    changed = 0
    for path in sorted(drafts.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if "<figure>" in text:
            continue
        slug = slug_from_draft(text)
        if not slug or slug not in mapping:
            print("SKIP no mapping", path.name, slug)
            continue
        rel, alt = mapping[slug]
        img_path = pack / "assets" / "images" / rel
        if not img_path.is_file():
            print("SKIP missing image", slug, rel)
            continue
        folder_pick = folder_pick_from_draft(text)
        figure = build_figure(rel, alt, 1, folder_pick)
        body_m = re.match(r"^---\n.*?\n---\n", text, re.S)
        if not body_m:
            continue
        body = text[body_m.end() :]
        paras = body.split("\n\n", 1)
        if len(paras) < 2:
            new_body = body.rstrip() + "\n\n" + figure
        else:
            new_body = paras[0] + "\n\n" + figure + paras[1]
        path.write_text(text[: body_m.end()] + new_body, encoding="utf-8")
        changed += 1
    return changed


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("pack", choices=("pests", "varieties"))
    args = parser.parse_args()
    if args.pack == "pests":
        n = embed_pack("pests", PESTS_PRIMARY)
    else:
        n = embed_pack("varieties", VARIETY_PRIMARY)
    print("embedded", n, "drafts")


if __name__ == "__main__":
    main()
