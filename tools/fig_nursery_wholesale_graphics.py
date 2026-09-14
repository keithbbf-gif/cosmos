#!/usr/bin/env python3
"""Download cleared rasters and embed <figure> blocks for fig-nursery-wholesale-ops."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.parse
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content" / "fig-nursery-wholesale-ops"
ASSETS = PACK / "assets" / "images"
DRAFTS = PACK / "drafts"
UA = "BuyfigsNurseryPack/1.0 (educational staging; nursery wholesale cuttings)"

DOWNLOADS: list[tuple[str, str]] = [
    ("2012_USDA_Plant_Hardiness_Zone_Map_(USA).jpg", "shared/usda-phzm-2012.jpg"),
    ("Pomological_Watercolor_POM00007441.jpg", "cultivars/usda-pom-celeste.jpg"),
    ("Pomological_Watercolor_POM00001043.jpg", "cultivars/usda-pom-magnolia.jpg"),
    ("Pomological_Watercolor_POM00007440.jpg", "cultivars/usda-pom-calimyrna-1912.jpg"),
    ("Pomological_Watercolor_POM00001044.jpg", "cultivars/usda-pom-nameless.jpg"),
    ("Pomological_Watercolor_POM00001045.jpg", "cultivars/usda-pom-royal-black.jpg"),
    ("Pomological_Watercolor_POM00001042.jpg", "propagation/usda-pom-cutting.jpg"),
    ("Pomological_Watercolor_POM00001168.jpg", "cultivars/usda-pom-toulousienne.jpg"),
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
    },
    "cultivars/usda-pom-celeste.jpg": {
        "credit": "Elsie Lower Pomeroy; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00007441.jpg",
    },
    "cultivars/usda-pom-magnolia.jpg": {
        "credit": "Mary Daisy Arnold; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001043.jpg",
    },
    "cultivars/usda-pom-calimyrna-1912.jpg": {
        "credit": "Elsie Lower Pomeroy; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00007440.jpg",
    },
    "cultivars/usda-pom-nameless.jpg": {
        "credit": "Mary Daisy Arnold; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001044.jpg",
    },
    "cultivars/usda-pom-royal-black.jpg": {
        "credit": "Elsie Lower Pomeroy; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001045.jpg",
    },
    "propagation/usda-pom-cutting.jpg": {
        "credit": "James Marion Shull; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001042.jpg",
    },
    "cultivars/usda-pom-toulousienne.jpg": {
        "credit": "Deborah Griscom Passmore; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001168.jpg",
    },
    "botanical/wellcome-v0044761.jpg": {
        "credit": "Wellcome Collection V0044761",
        "license": "CC BY 4.0",
        "source": "https://commons.wikimedia.org/wiki/File:A_fig_plant_(Ficus_carica);_fruiting_stem_and_halved_fruit._Wellcome_V0044761.jpg",
    },
    "botanical/ehret-trew-1771.jpg": {
        "credit": "G. D. Ehret; C. J. Trew, Plantae selectae (1771)",
        "license": "Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:Ficus_carica_L,_1771.jpg",
    },
    "botanical/eb1911-moraceae-diagram.jpg": {
        "credit": "Encyclopaedia Britannica 1911",
        "license": "Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:EB1911_Moraceae_-_Ficus_carica.jpg",
    },
    "botanical/kohler-type-med-plate.jpg": {
        "credit": "Köhler-type medicinal plate (Commons scan)",
        "license": "Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:Illustration_Ficus_carica0.jpg",
    },
    "botanical/denoncin-figuier-plate.jpg": {
        "credit": "Denoncin, figuier plate (Commons)",
        "license": "Public domain (as tagged on Commons)",
        "source": "https://commons.wikimedia.org/wiki/File:11-Figuier-Ficus_carica.jpg",
    },
    "living/amwell-fig-tree.jpg": {
        "credit": "Hopefully Acceptable Use (Wikimedia Commons)",
        "license": "CC BY-SA 4.0",
        "source": "https://commons.wikimedia.org/wiki/File:Amwell_Fig_(1).jpg",
    },
    "living/hortus-leiden-fig-2021.jpg": {
        "credit": "Rudolphous (Wikimedia Commons)",
        "license": "CC BY-SA 4.0",
        "source": "https://commons.wikimedia.org/wiki/File:20210731_Hortus_botanicus_Leiden_-_Ficus_carica.jpg",
    },
}

# draft id -> (asset rel, alt, figcaption body without credit, D:\FIGS orchard slot)
FIGURES: dict[str, tuple[str, str, str, str]] = {
    "d01": (
        "propagation/usda-pom-cutting.jpg",
        "Bundled dormant fig cutting wood graded for wholesale trade on a USDA propagation plate",
        "Figure 1. A wholesale brick is counted lignified wood in trade lengths — not hobby envelopes of green tips.",
        r"D:\FIGS\Figs",
    ),
    "d02": (
        "living/amwell-fig-tree.jpg",
        "Mature common fig tree Ficus carica in a temperate garden — dormant-season trade context",
        "Figure 1. The dormant window is the product: winter wood taken while the tree is asleep, not summer growth rushed into a bag.",
        r"D:\FIGS\Greenhouse photos",
    ),
    "d03": (
        "propagation/usda-pom-cutting.jpg",
        "One-year lignified fig cutting wood with nodes visible on USDA watercolor plate",
        "Figure 1. One-year wood carries the nodes a bench needs; pretty green tips belong in the compost, not the invoice.",
        r"D:\FIGS\Figs",
    ),
    "d04": (
        "living/amwell-fig-tree.jpg",
        "Mother fig tree with multiple stems available for limited winter cutting",
        "Figure 1. A mother block is a factory with a budget — how much wood you spare this January is next summer's canopy.",
        r"D:\FIGS\Figs",
    ),
    "d05": (
        "cultivars/usda-pom-celeste.jpg",
        "USDA Celeste fig watercolor used as grade and cultivar voucher",
        "Figure 1. Grade is a promise tied to a name — a USDA plate is documentation, not proof your bundle matches this stick.",
        r"D:\FIGS\Fig Fruit",
    ),
    "d06": (
        "propagation/usda-pom-cutting.jpg",
        "Pencil-thick fig propagation sticks on USDA cutting plate with cull context",
        "Figure 1. Pencil-thick wood with two honest culls beside it beats a bag of pretty twigs that will not root.",
        r"D:\FIGS\Figs",
    ),
    "d07": (
        "propagation/usda-pom-cutting.jpg",
        "Dormant fig cuttings staged for cut-to-order versus cooler inventory",
        "Figure 1. Cut-to-order wood leaves the blade warm; cooler inventory is a bet that labels and temps hold until the slip prints.",
        r"D:\FIGS\Greenhouse photos",
    ),
    "d08": (
        "living/amwell-fig-tree.jpg",
        "Row of mature fig trees representing a mother block in production",
        "Figure 1. The mother block is the factory floor — every wholesale SKU you ship this winter walked out of these stems.",
        r"D:\FIGS\Figs",
    ),
    "d09": (
        "botanical/ehret-trew-1771.jpg",
        "Historic botanical plate of Ficus carica — bench hygiene when cultivar changes",
        "Figure 1. Wipe the blade when the name changes; sap on steel is how Celeste becomes Turkey in a mixed afternoon.",
        r"D:\FIGS\Fig Labels",
    ),
    "d10": (
        "botanical/eb1911-moraceae-diagram.jpg",
        "Moraceae stem diagram showing nodes and polarity on fig wood",
        "Figure 1. Mark the basal end like you mean it — polarity errors are silent until March when every stick points the wrong way.",
        r"D:\FIGS\Figs",
    ),
    "d11": (
        "cultivars/usda-pom-nameless.jpg",
        "USDA Nameless fig watercolor — identity before the blade falls",
        "Figure 1. The name goes on before the cut; anonymous wood is how a bench lies to itself in February.",
        r"D:\FIGS\Fig Labels",
    ),
    "d12": (
        "cultivars/usda-pom-magnolia.jpg",
        "USDA Magnolia fig plate — three-label discipline for wholesale lots",
        "Figure 1. Three labels or you will lie in March: mother, bundle, and slip must still agree when the box is wet.",
        r"D:\FIGS\Fig Labels",
    ),
    "d13": (
        "cultivars/usda-pom-nameless.jpg",
        "USDA plate with lot-style cultivar documentation for traceability",
        "Figure 1. A lot code a stranger can read beats a clever nickname on a tag that smears in a damp bag.",
        r"D:\FIGS\Fig Labels",
    ),
    "d14": (
        "cultivars/usda-pom-toulousienne.jpg",
        "USDA Toulousienne fig watercolor — synonyms are not extra SKUs",
        "Figure 1. Synonyms are not extra SKUs; one stick, one trade name on the invoice, or you are running a guessing game.",
        r"D:\FIGS\Fig Labels",
    ),
    "d15": (
        "cultivars/usda-pom-royal-black.jpg",
        "Dark-fruited USDA fig plate — color ties need a written legend",
        "Figure 1. Color ties without a legend are a future mix-up — ribbon color is a tool, not a cultivar name.",
        r"D:\FIGS\Fig Labels",
    ),
    "d16": (
        "cultivars/usda-pom-nameless.jpg",
        "USDA documentation plate — packing slip, invoice, and stick must match",
        "Figure 1. Slip, invoice, and stick must agree before tape; paper that disagrees is a chargeback waiting on a porch.",
        r"D:\FIGS\Fig Labels",
    ),
    "d17": (
        "cultivars/usda-pom-nameless.jpg",
        "Unnamed USDA fig voucher — honest unknown-until-fruit language",
        "Figure 1. Unknown until it fruits is a nursery sentence — ship the honesty on the tag, not a celebrity name you hope is right.",
        r"D:\FIGS\Fig Labels",
    ),
    "d18": (
        "botanical/wellcome-v0044761.jpg",
        "Fig stem and fruit anatomy plate — tags that must survive a wet box",
        "Figure 1. A pulp tag is not a label; ink that survives a wet box is part of the cultivar promise.",
        r"D:\FIGS\Fig Labels",
    ),
    "d19": (
        "propagation/usda-pom-cutting.jpg",
        "Dormant fig cutting wood moisture context on USDA plate — damp not wet",
        "Figure 1. If you can wring the paper, you packed a mushroom farm — dormant wood needs fog, not a pond in the bag.",
        r"D:\FIGS\FigRoots",
    ),
    "d20": (
        "propagation/usda-pom-cutting.jpg",
        "Counted bundles of fig cuttings — tens and fifties as trade units",
        "Figure 1. Ten is a handful; fifty is a trade unit — count bands exist so wholesale does not devolve into handful math.",
        r"D:\FIGS\FigRoots",
    ),
    "d21": (
        "botanical/wellcome-v0044761.jpg",
        "Fig wood and fruit stem — kraft paper and film choices at pack-out",
        "Figure 1. Paper, film, and what we skip are moisture decisions — the stem plate is a reminder that bark, not fruit, rides in January.",
        r"D:\FIGS\FigRoots",
    ),
    "d22": (
        "propagation/usda-pom-cutting.jpg",
        "Fig cutting ends on USDA plate — wax, film, or clean cut choices",
        "Figure 1. Ends: wax, film, or a clean cut — exposed pith dries in transit; sealed ends rot if the bag is already wet.",
        r"D:\FIGS\FigRoots",
    ),
    "d23": (
        "botanical/eb1911-moraceae-diagram.jpg",
        "Fig structure diagram — void fill and crush in shipping cartons",
        "Figure 1. Empty air in a box is a hammer — void is acceleration; staged wood still needs something between sticks and cardboard.",
        r"D:\FIGS\FigRoots",
    ),
    "d24": (
        "cultivars/usda-pom-celeste.jpg",
        "Two cultivar vouchers on USDA plates — mixed boxes need internal walls",
        "Figure 1. Two varieties in one box need a wall — mixed cartons without dividers become March synonym soup.",
        r"D:\FIGS\FigRoots",
    ),
    "d25": (
        "propagation/usda-pom-cutting.jpg",
        "Open-bundle fig cuttings — bench photograph as packing receipt",
        "Figure 1. Count twice, photograph once, then tape — an open-box bench photo beats reconstructing Tuesday from memory.",
        r"D:\FIGS\FigRoots",
    ),
    "d26": (
        "propagation/usda-pom-cutting.jpg",
        "Retail sleeve versus wholesale brick of dormant fig cuttings",
        "Figure 1. A retail sleeve is a conversation; a brick is a count — different dunnage, different label density, same damp-not-wet rule.",
        r"D:\FIGS\FigRoots",
    ),
    "d27": (
        "living/hortus-leiden-fig-2021.jpg",
        "Potted and field fig trees — soil weight and quarantine packing",
        "Figure 1. Dirt is weight, quarantine, and a different box — potted plants are not sticks with roots tucked in for free.",
        r"D:\FIGS\Greenhouse photos",
    ),
    "d28": (
        "botanical/wellcome-v0044761.jpg",
        "Fig stem with roots implied — liners versus unrooted dormant wood",
        "Figure 1. A liner has roots; a cutting does not — do not invoice one as the other because the bag looks similar.",
        r"D:\FIGS\Greenhouse photos",
    ),
    "d29": (
        "propagation/usda-pom-cutting.jpg",
        "Dormant fig wood held in cooler storage — delay not hospital",
        "Figure 1. The cooler holds wood; it does not heal it — storage is a pause on the DOA clock, not a mold cure.",
        r"D:\FIGS\Greenhouse photos",
    ),
    "d30": (
        "shared/usda-phzm-2012.jpg",
        "USDA Plant Hardiness Zone Map — cooler temperature band context",
        "Figure 1. 36–40°F is a reading, not a sticker — map bands remind you why a drawer thermometer beats a logo on the door.",
        r"D:\FIGS\Greenhouse photos",
    ),
    "d31": (
        "botanical/wellcome-v0044761.jpg",
        "Fig stem cross-section — condensation after warm pack meets cold truck",
        "Figure 1. Warm wood in a cold bag sweats — fog on plastic is normal; a pond at the bottom is a repack.",
        r"D:\FIGS\Greenhouse photos",
    ),
    "d32": (
        "propagation/usda-pom-cutting.jpg",
        "Weekend-held dormant cuttings in a tote — Friday wood to Monday ship",
        "Figure 1. Friday wood in a tote until Monday is a decision — every extra day in plastic is a vote for mold.",
        r"D:\FIGS\Greenhouse photos",
    ),
    "d33": (
        "propagation/usda-pom-cutting.jpg",
        "Cull fig sticks on USDA plate — inventory that must leave the trade",
        "Figure 1. Some inventory has to go in the burn pile — fuzzy wood at pack-out is not a wholesale discount, it is trash.",
        r"D:\FIGS\Figs",
    ),
    "d34": (
        "botanical/ehret-trew-1771.jpg",
        "Botanical Ficus carica plate — mailable dormant plants not produce snacks",
        "Figure 1. We ship plants, not snacks — dormant wood and liners ride under plant rules, not grocery fantasy.",
        r"D:\FIGS\FigRoots",
    ),
    "d35": (
        "shared/usda-phzm-2012.jpg",
        "USDA hardiness zone map for weather-driven ship holds",
        "Figure 1. The forecast can cancel a paid order — zone context is background when polar air crosses your lane mid-week.",
        r"D:\FIGS\FigRoots",
    ),
    "d36": (
        "shared/usda-phzm-2012.jpg",
        "USDA zone map — heat pack risk against dormant bark in cold snaps",
        "Figure 1. A heat pack against bark is an oven — mild map bands do not mean every stick wants bottom heat in the mail.",
        r"D:\FIGS\FigRoots",
    ),
    "d37": (
        "shared/usda-phzm-2012.jpg",
        "USDA Plant Hardiness Zone Map — Friday drop into Monday freeze timing",
        "Figure 1. A Friday drop into a Monday freeze is a scheduling scar — the map is not the forecast, but it frames whose porch is still in play.",
        r"D:\FIGS\FigRoots",
    ),
    "d38": (
        "living/amwell-fig-tree.jpg",
        "Garden fig tree at delivery — porch care beats tracking numbers",
        "Figure 1. Tracking is not care; the porch is care — a scanned label does not unwrap a box on the other bench.",
        r"D:\FIGS\FigRoots",
    ),
    "d39": (
        "cultivars/usda-pom-calimyrna-1912.jpg",
        "USDA Calimyrna plate — state soil and quarantine paperwork context",
        "Figure 1. Some states want paper; some want no soil — destination rules are not uniform, and fruit plates are not phytosanitary certificates.",
        r"D:\FIGS\Fig Labels",
    ),
    "d40": (
        "cultivars/usda-pom-nameless.jpg",
        "USDA voucher plate — official documents versus vibe certificates",
        "Figure 1. A phytosanitary certificate is a document with an inspector's name — not a sticker you print because the buyer sounded serious.",
        r"D:\FIGS\Fig Labels",
    ),
    "d41": (
        "cultivars/usda-pom-nameless.jpg",
        "USDA Nameless fig plate — do not ship unnamed wood as a celebrity SKU",
        "Figure 1. If I cannot name it, I do not ship it as a name — honesty on the slip beats a hopeful cultivar on the invoice.",
        r"D:\FIGS\Fig Labels",
    ),
    "d42": (
        "propagation/usda-pom-cutting.jpg",
        "Aging dormant fig cuttings — three days changes the product class",
        "Figure 1. Three days in a warm back room turns a cutting into compost math — the plate is dormant wood, not what Thursday smells like.",
        r"D:\FIGS\FigRoots",
    ),
    "d43": (
        "propagation/usda-pom-cutting.jpg",
        "Fig cuttings unpacked on the receiving bench — open box inspection",
        "Figure 1. Open the box on the bench before peanuts hit the floor — receiving starts with counts, not feelings.",
        r"D:\FIGS\FigRoots",
    ),
    "d44": (
        "propagation/usda-pom-cutting.jpg",
        "Dormant fig sticks for DOA clock and replacement claims",
        "Figure 1. DOA is a clock — two bench photos and a timestamp beat a paragraph of polite rage.",
        r"D:\FIGS\FigRoots",
    ),
    "d45": (
        "botanical/kohler-type-med-plate.jpg",
        "Historic medicinal fig plate — this lane is not human pharmacy copy",
        "Figure 1. This lane is not a pharmacy — fig wood ships as plants; human medicine and supplement claims stay off the buyfigs table.",
        r"D:\FIGS\FigRoots",
    ),
    "d46": (
        "shared/usda-phzm-2012.jpg",
        "USDA zone map as seasonal wall calendar for take-mark-pack-hold-ship-land",
        "Figure 1. The season on one wall — take, mark, pack, hold, ship, land — is how a trade year stays legible when the inbox is loud.",
        r"D:\FIGS\Fig Labels",
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


def figure_html(draft_id: str, asset_rel: str, alt: str, caption: str, orchard: str) -> str:
    rights = RIGHTS[asset_rel]
    credit = rights["credit"]
    lic = rights["license"]
    fig_id = f"{draft_id}.{asset_rel.split('/')[-1].rsplit('.', 1)[0]}"
    return (
        f'<!-- figure-id: {fig_id} -->\n'
        f"<!-- orchard_slot: {orchard} — hero still before publish -->\n"
        f"<figure>\n"
        f'<img src="../assets/images/{asset_rel}" alt="{alt}">\n'
        f"<figcaption>{caption} Historic plate — not our pack bench. Credit: {credit}. License: {lic} — see RIGHTS.md.</figcaption>\n"
        f"</figure>\n\n"
    )


def embed_figures() -> None:
    for path in sorted(DRAFTS.glob("d*.md")):
        draft_id = path.stem.split("-")[0]
        if draft_id not in FIGURES:
            raise SystemExit(f"missing figure spec for {draft_id}")
        asset, alt, cap, orchard = FIGURES[draft_id]
        block = figure_html(draft_id, asset, alt, cap, orchard)
        text = path.read_text(encoding="utf-8")
        if "<figure>" in text:
            text = re.sub(
                r"<!-- figure-id:.*?-->\s*(?:<!-- orchard_slot:.*?-->\s*)?<figure>.*?</figure>\s*\n*",
                "",
                text,
                count=1,
                flags=re.S,
            )
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
        "# RIGHTS — fig-nursery-wholesale-ops",
        "",
        "Every file under `assets/images/` must have a row here before WordPress import.",
        "**`D:\\FIGS` stills are the publish heroes** (see `PHOTO_NOTES.md`). USDA NAL pomological",
        "watercolors, Britannica diagrams, and Wellcome plates in this pass are **reference fills** —",
        "caption as historic documentation, never as “Jack’s taped carton on the bench.”",
        "",
        "No AI-generated images. Re-check Wikimedia Commons and NAL tags before live publish.",
        "",
        "| Asset path | Commons / source | Credit | License | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    meta_path = ASSETS / "_download_meta.json"
    sha_by_rel: dict[str, str] = {}
    if meta_path.exists():
        for row in json.loads(meta_path.read_text(encoding="utf-8")):
            p = row["path"]
            rel = p.split("assets/images/", 1)[-1] if "assets/images/" in p else p
            sha_by_rel[rel] = row["sha256"]
    for rel, info in sorted(RIGHTS.items()):
        sha = sha_by_rel.get(rel, "(run download)")
        src = info.get("source", "")
        lines.append(
            f"| `assets/images/{rel}` | {src} | {info['credit']} | {info['license']} | `{sha}` |"
        )
    lines.extend(
        [
            "",
            "## Reserved (do not scrape)",
            "",
            "- Stock photos of taped shipping cartons without `D:\\FIGS` proof",
            "- Marketplace cultivar fraud shots",
            "- AI-generated bench, box, or label imagery",
            "",
        ]
    )
    (PACK / "RIGHTS.md").write_text("\n".join(lines), encoding="utf-8")


def write_graphics_index() -> None:
    lines = [
        "# GRAPHICS_INDEX — fig-nursery-wholesale-ops",
        "",
        "| Figure ID | Draft | File | Orchard slot | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for draft_id in sorted(FIGURES):
        asset, _, _, orchard = FIGURES[draft_id]
        fig_id = f"{draft_id}.{asset.split('/')[-1].rsplit('.', 1)[0]}"
        lines.append(
            f"| `{fig_id}` | `{draft_id}` | `assets/images/{asset}` | `{orchard}` | staged |"
        )
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
