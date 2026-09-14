#!/usr/bin/env python3
"""Insert lead <figure> blocks and normalize portrait YAML for the image+SEO pass."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "articles"

DOWNLOADED = {
    "francois-magendie": {
        "file": "assets/portraits/francois-magendie.jpg",
        "alt": "Lithograph portrait of François Magendie, nineteenth-century French physiologist.",
        "name": "François Magendie",
        "dates": "1783–1855",
        "tail": "French physiologist who treated deglutition as interruptible physiology in the *Précis* textbooks.",
        "credit": "BIU Santé / Wikimedia Commons. CC0 1.0.",
        "w": 360,
        "h": 357,
    },
    "walter-b-cannon": {
        "file": "assets/portraits/walter-b-cannon.jpg",
        "alt": "Studio photograph of Walter Bradford Cannon in mid career.",
        "name": "Walter B. Cannon",
        "dates": "1871–1945",
        "tail": "Harvard physiologist who stained living meals with bismuth for early fluoroscopic swallow studies.",
        "credit": "Wellcome Collection / Wikimedia Commons. CC BY 4.0.",
        "w": 360,
        "h": 269,
    },
    "gustav-killian": {
        "file": "assets/portraits/gustav-killian.jpg",
        "alt": "Portrait photograph of Gustav Killian, German laryngologist and endoscopist.",
        "name": "Gustav Killian",
        "dates": "1860–1921",
        "tail": "Freiburg laryngologist associated with rigid endoscopy and Killian’s triangle.",
        "credit": "Wikimedia Commons. Public domain.",
        "w": 360,
        "h": 284,
    },
    "chevalier-jackson": {
        "file": "assets/portraits/chevalier-jackson.jpg",
        "alt": "Autographed studio portrait of Chevalier Jackson in later life.",
        "name": "Chevalier Jackson",
        "dates": "1865–1958",
        "tail": "Philadelphia bronchoesophagologist whose foreign-body clinic and manuals shaped American endoscopy.",
        "credit": "Wellcome Collection / Wikimedia Commons. CC BY 4.0.",
        "w": 360,
        "h": 476,
    },
}

PLACEHOLDER_BLOCK = (
    "> **Portrait placeholder.** No public-domain or clearly licensed portrait located as of the pack date. "
    "See `PORTRAIT_SOURCES.md` for hunt status. Do not invent or generate a substitute likeness."
)

FRONT_RE = re.compile(r"^(---\n.*?\n---\n)", re.S)
DISCLAIMER = (
    "*Educational history for SLPWOW. Not a treatment plan and not a substitute for "
    "evaluation by a licensed clinician.*"
)


def figure_html(slug: str, spec: dict) -> str:
    return f"""<!-- figure-id: {slug}.lead-portrait -->
<figure class="slpwow-figure slpwow-figure--portrait">
  <img
    src="../{spec['file']}"
    alt="{spec['alt']}"
    width="{spec['w']}"
    height="{spec['h']}"
    loading="lazy"
  />
  <figcaption>
    <strong>{spec['name']}</strong> ({spec['dates']}), {spec['tail']}
    <span class="figure-credit">{spec['credit']}</span>
  </figcaption>
</figure>
"""


def set_yaml_field(block: str, key: str, value: str) -> str:
    pat = re.compile(rf"^{re.escape(key)}:.*$", re.M)
    if pat.search(block):
        return pat.sub(f"{key}: {value}", block, count=1)
    return block


def strip_portrait_section(body: str) -> str:
    body = re.sub(
        r"\n## Portrait\n\n> \*\*Portrait placeholder\.\*\*[\s\S]*?(?=\n## |\Z)",
        "\n",
        body,
    )
    body = re.sub(r"\n## Portrait\n\nCandidate:[\s\S]*?(?=\n## |\Z)", "\n", body)
    return body.rstrip() + "\n"


def patch_profile(path: Path, slug: str) -> None:
    text = path.read_text(encoding="utf-8")
    m = FRONT_RE.match(text)
    if not m:
        raise SystemExit(f"no front matter: {path}")
    fm_block = m.group(1)
    body = text[m.end() :]

    if slug in DOWNLOADED:
        spec = DOWNLOADED[slug]
        fm_block = set_yaml_field(fm_block, "portrait", spec["file"])
        fm_block = set_yaml_field(fm_block, "portrait_status", "downloaded")
        body = strip_portrait_section(body)
        if "figure-id:" not in body:
            if DISCLAIMER not in body:
                raise SystemExit(f"missing disclaimer: {path}")
            insert = "\n\n" + figure_html(slug, spec) + "\n"
            body = body.replace(DISCLAIMER, DISCLAIMER + insert, 1)
    else:
        fm_block = set_yaml_field(fm_block, "portrait", "null")
        fm_block = set_yaml_field(fm_block, "portrait_status", "placeholder")
        body = strip_portrait_section(body)
        lead = body.split("\n## ", 1)[0]
        if PLACEHOLDER_BLOCK not in lead:
            if DISCLAIMER not in body:
                raise SystemExit(f"missing disclaimer: {path}")
            body = body.replace(
                DISCLAIMER,
                DISCLAIMER + "\n\n" + PLACEHOLDER_BLOCK + "\n",
                1,
            )

    path.write_text(fm_block + body, encoding="utf-8")


def main() -> None:
    for path in sorted(ART.glob("*.md")):
        slug = re.sub(r"^\d+-", "", path.stem)
        fm = FRONT_RE.match(path.read_text(encoding="utf-8"))
        if not fm:
            continue
        if 'type: profile' not in fm.group(1):
            continue
        patch_profile(path, slug)
        print("patched", path.name)


if __name__ == "__main__":
    main()
