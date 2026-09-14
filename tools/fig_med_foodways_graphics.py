#!/usr/bin/env python3
"""Download cleared rasters and embed <figure> blocks for fig-mediterranean-foodways."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content" / "fig-mediterranean-foodways"
ASSETS = PACK / "assets" / "images"
REGISTRY = PACK / "figures_registry.json"
UA = "FigRootsMedFoodways/1.0 (educational staging; Mediterranean fig foodways)"

DOWNLOADS: list[tuple[str, str]] = [
    ("Incir.jpg", "fresh/incir-turkey.jpg"),
    ("Dried_figs.jpg", "drying/dried-figs-pile.jpg"),
    ("Dried_Figs_(1).jpg", "drying/dried-figs-tray.jpg"),
    ("Dried_fig.png", "drying/dried-fig-cut-tiia-monto.png"),
    ("DriedFigs1.JPG", "drying/dried-figs-pd-still.jpg"),
    ("Dreid_figs.jpg", "drying/dreid-figs-string.jpg"),
    ("2014-01-04-Figen_(11748534465).jpg", "fresh/figen-market-2014.jpg"),
    ("A_closeup_of_fig_fruit.JPG", "fresh/fig-syconium-closeup.jpg"),
    ("Blastophaga_psenes.jpg", "botanical/blastophaga-psenes.jpg"),
    ("Pomological_Watercolor_POM00007440.jpg", "usda/usda-pom-calimyrna-1912.jpg"),
    ("Pomological_Watercolor_POM00007439.jpg", "usda/usda-pom-calimyrna-ship.jpg"),
    (
        "Wall_painting_-_still_life_with_bread_and_figs_-_Herculaneum_-_Napoli_MAN_8625.jpg",
        "historic/herculaneum-bread-figs-man8625.jpg",
    ),
    ("Bartolomeo_Bimbi_(figs).jpg", "historic/bimbi-figs-1696.jpg"),
    (
        "Luis Meléndez, Still Life with Figs and Bread, c. 1770, NGA 111627.jpg",
        "historic/melendez-figs-bread-nga.jpg",
    ),
    ("Ficus_carica_L,_1771.jpg", "botanical/ehret-trew-1771.jpg"),
    ("Spice_Bazaar,_Istanbul.jpg", "markets/spice-bazaar-istanbul.jpg"),
    ("Mercat_de_la_Boqueria_01.jpg", "markets/la-boqueria-barcelona.jpg"),
    ("Opuntia_ficus-indica_1.jpg", "caution/opuntia-prickly-pear-fruit.jpg"),
    ("11-Figuier-Ficus_carica.jpg", "botanical/denoncin-figuier-plate.jpg"),
    ("Illustration_Ficus_carica0.jpg", "botanical/kohler-type-med-plate.jpg"),
    ("Marseille_Vieux_Port_Night.jpg", "markets/marseille-vieux-port-night.jpg"),
    ("Izmir_03.jpg", "markets/izmir-konak-waterfront.jpg"),
    ("The_old_Port_(Vieux_Port)_of_Marseille.jpg", "markets/marseille-vieux-port-day.jpg"),
    ("13-Marseille-Torpilleurs_dans_le_Vieux-port-1907.JPG", "historic/marseille-port-1907-torpedo-boats.jpg"),
]

RIGHTS_STATIC: dict[str, dict[str, str]] = {
    "fresh/incir-turkey.jpg": {
        "credit": "See Commons file page",
        "license": "See Commons (recheck before import)",
        "source": "https://commons.wikimedia.org/wiki/File:Incir.jpg",
    },
    "drying/dried-fig-cut-tiia-monto.png": {
        "credit": "Tiia Monto",
        "license": "CC BY-SA 4.0",
        "source": "https://commons.wikimedia.org/wiki/File:Dried_fig.png",
    },
    "historic/herculaneum-bread-figs-man8625.jpg": {
        "credit": "Photo: ArchaiOptix (Commons). Fresco: MAN Naples inv. 8625",
        "license": "CC BY-SA 4.0 (photo); fresco PD",
        "source": "https://commons.wikimedia.org/wiki/File:Wall_painting_-_still_life_with_bread_and_figs_-_Herculaneum_-_Napoli_MAN_8625.jpg",
    },
    "usda/usda-pom-calimyrna-1912.jpg": {
        "credit": "Elsie Lower Pomeroy; USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00007440.jpg",
    },
    "usda/usda-pom-calimyrna-ship.jpg": {
        "credit": "USDA NAL Pomological Watercolor Collection",
        "license": "Public domain (U.S. government work)",
        "source": "https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00007439.jpg",
    },
    "botanical/blastophaga-psenes.jpg": {
        "credit": "See Commons file page",
        "license": "See Commons (scientific illustration)",
        "source": "https://commons.wikimedia.org/wiki/File:Blastophaga_psenes.jpg",
    },
    "caution/opuntia-prickly-pear-fruit.jpg": {
        "credit": "See Commons file page",
        "license": "See Commons",
        "source": "https://commons.wikimedia.org/wiki/File:Opuntia_ficus-indica_1.jpg",
        "subject": "Opuntia ficus-indica (prickly pear) — NOT Ficus carica. Draft 45 only.",
    },
    "historic/melendez-figs-bread-nga.jpg": {
        "credit": "Luis Meléndez, c. 1770; National Gallery of Art 111627",
        "license": "CC0 (NGA Open Access, as tagged on Commons)",
        "source": "https://commons.wikimedia.org/wiki/File:Luis_Mel%C3%A9ndez,_Still_Life_with_Figs_and_Bread,_c._1770,_NGA_111627.jpg",
    },
    "historic/bimbi-figs-1696.jpg": {
        "credit": "Bartolomeo Bimbi; Villa Medicea di Poggio a Caiano",
        "license": "Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:Bartolomeo_Bimbi_(figs).jpg",
    },
    "botanical/ehret-trew-1771.jpg": {
        "credit": "G. D. Ehret; C. J. Trew, Plantae selectae (1771)",
        "license": "Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:Ficus_carica_L,_1771.jpg",
    },
    "markets/spice-bazaar-istanbul.jpg": {
        "credit": "See Commons file page",
        "license": "See Commons",
        "source": "https://commons.wikimedia.org/wiki/File:Spice_Bazaar,_Istanbul.jpg",
    },
    "markets/la-boqueria-barcelona.jpg": {
        "credit": "See Commons file page",
        "license": "See Commons",
        "source": "https://commons.wikimedia.org/wiki/File:Mercat_de_la_Boqueria_01.jpg",
    },
}


def fetch_commons(commons_name: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    enc = urllib.parse.quote(commons_name)
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=1600"
    for attempt in range(5):
        try:
            subprocess.run(["curl", "-fsSL", "-A", UA, "-o", str(dest), url], check=True)
            break
        except subprocess.CalledProcessError:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    time.sleep(0.6)
    data = dest.read_bytes()
    if len(data) < 3000 and "blastophaga" not in str(dest).lower():
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
        print("GET", commons[:60])
        meta.append(fetch_commons(commons, dest))
    (ASSETS / "_download_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def figure_html(draft_id: str, asset_rel: str, alt: str, caption: str) -> str:
    info = RIGHTS_STATIC.get(asset_rel, {})
    credit = info.get("credit", "See RIGHTS.md")
    lic = info.get("license", "See RIGHTS.md")
    fig_id = f"{draft_id}.{asset_rel.split('/')[-1].rsplit('.', 1)[0]}"
    return (
        f'<!-- figure-id: {fig_id} -->\n'
        f"<figure>\n"
        f'<img src="assets/images/{asset_rel}" alt="{alt}">\n'
        f"<figcaption>{caption} Credit: {credit}. License: {lic} — see RIGHTS.md.</figcaption>\n"
        f"</figure>\n\n"
    )


def embed_figures() -> None:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for path in sorted(PACK.glob("[0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        draft_id = None
        if text.startswith("---"):
            fm = text.split("---", 2)[1]
            for line in fm.splitlines():
                if line.startswith("id:"):
                    draft_id = line.split(":", 1)[1].strip()
                    break
        if not draft_id:
            raise SystemExit(f"{path.name}: no id in front matter")
        if draft_id not in reg:
            raise SystemExit(f"missing registry entry for {draft_id}")
        row = reg[draft_id]
        block = figure_html(draft_id, row["asset"], row["alt"], row["caption"])
        if "<figure>" in text:
            text = re.sub(r"<!-- figure-id:.*?-->\s*<figure>.*?</figure>\s*\n*", "", text, count=1, flags=re.S)
        end = text.find("\n---", 3)
        if end == -1:
            raise SystemExit(f"{path.name}: bad front matter")
        insert_at = end + 4
        if insert_at < len(text) and text[insert_at] == "\n":
            insert_at += 1
        path.write_text(text[:insert_at] + "\n" + block + text[insert_at:].lstrip("\n"), encoding="utf-8")
        print("embedded", path.name)


def write_rights_md() -> None:
    meta = json.loads((ASSETS / "_download_meta.json").read_text(encoding="utf-8"))
    sha = {row["path"].split("assets/images/", 1)[-1]: row["sha256"] for row in meta}
    lines = [
        "# RIGHTS — fig-mediterranean-foodways",
        "",
        "Cleared rasters staged for desk review. **Recheck Commons, USDA, and museum pages before live import.**",
        "User `D:\\FIGS` notes were not mounted in the cloud agent; selections follow `IMAGE_SOURCES.md`",
        "and public-domain / CC sources (USDA NAL, Wellcome-class plates, Wikimedia Commons).",
        "",
        "Subjects are *Ficus carica* foodways unless `figures_registry.json` marks draft **fig-med-45**",
        "(*Opuntia ficus-indica* — prickly pear — intentional contrast).",
        "",
        "| Pack path | Source | Credit | License | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in meta:
        rel = row["path"].split("assets/images/", 1)[-1]
        info = RIGHTS_STATIC.get(rel, {})
        src = info.get("source", f"Commons: {row['commons']}")
        credit = info.get("credit", "See Commons file page")
        lic = info.get("license", "See Commons file page")
        lines.append(f"| `assets/images/{rel}` | {src} | {credit} | {lic} | `{sha.get(rel,'')}` |")
    lines.append("")
    (PACK / "RIGHTS.md").write_text("\n".join(lines), encoding="utf-8")


def write_graphics_index() -> None:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    lines = [
        "# GRAPHICS_INDEX — fig-mediterranean-foodways",
        "",
        "| Figure ID | Draft | File | Status |",
        "| --- | --- | --- | --- |",
    ]
    for draft_id, row in sorted(reg.items()):
        asset = row["asset"]
        fig_id = f"{draft_id}.{asset.split('/')[-1].rsplit('.', 1)[0]}"
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
