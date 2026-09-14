#!/usr/bin/env python3
"""Insert round-2 lead figures into adaptogens essays (PD/CC plates + SVG anchors)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# relative path from stage folder -> figure HTML block (insert after disclaim paragraph if present)
EMBEDS: dict[str, str] = {
    "stage-02-soviet-construct/08-the-three-clause-definition.md": """
<figure class="blog-figure">
  <img src="../assets/shared/svg/soviet-adaptogen-timeline.svg" alt="Schematic timeline of adaptogen word anchors from 1947 dispute through 2008 EMA reflection" width="960" height="320" loading="lazy" />
  <figcaption><strong>Figure.</strong> The three-clause definition landed in a dated Soviet research culture — anchor years are cited in secondary literature, not a complete chronology. <em>Schematic timeline; not to scale.</em></figcaption>
</figure>
""",
    "stage-03-east-asian-materia/16-the-wild-ginseng-economy.md": """
<figure class="blog-figure">
  <img src="../assets/images/panax-in-the-bencao/psm-ginseng-1891.jpg" alt="Late nineteenth-century engraving of ginseng root and leaves" width="700" loading="lazy" />
  <figcaption><strong>Figure.</strong> Wild ginseng scarcity is older than the adaptogen aisle — a popular-science engraving when the root was already a trade object. <em>Popular Science Monthly</em> (1891), public domain, via Wikimedia Commons.</figcaption>
</figure>
""",
    "stage-03-east-asian-materia/18-ciwujia-before-eleuthero.md": """
<figure class="blog-figure">
  <img src="../assets/images/eleuthero-as-type-specimen/doronenko-eleuthero-2006.jpg" alt="Photograph of Eleutherococcus senticosus foliage and stems" width="800" loading="lazy" />
  <figcaption><strong>Figure.</strong> <em>Ciwujia</em> names the shrub before Vladivostok redescribed it — botanical photograph for context only. Photo: Stanislav Doronenko, Wikimedia Commons (CC BY 2.5).</figcaption>
</figure>
""",
    "stage-03-east-asian-materia/21-astragalus-huangqi.md": """
<figure class="blog-figure">
  <img src="../assets/images/astragalus-huangqi/astragalus-membranaceus.jpg" alt="Photograph of Astragalus membranaceus plant habit" width="800" loading="lazy" />
  <figcaption><strong>Figure.</strong> <em>Huangqi</em> as a living legume — illustrates taxonomic context, not identification for harvest or dosing. Photo: Kor!An, Wikimedia Commons (CC BY-SA 3.0).</figcaption>
</figure>
""",
    "stage-03-east-asian-materia/24-cordyceps-and-the-high-trade.md": """
<figure class="blog-figure">
  <img src="../assets/images/cordyceps-and-the-high-trade/berkeley-cordyceps-1859.jpg" alt="Nineteenth-century scientific illustration of Cordyceps sinensis on a caterpillar" width="700" loading="lazy" />
  <figcaption><strong>Figure.</strong> Cordyceps entered European print as a curiosity long before the export boom — historical plate, not a product photo. Miles Joseph Berkeley (1859), public domain, via Wikimedia Commons.</figcaption>
</figure>
""",
    "stage-04-south-asian-and-other/26-rasayana-is-not-adaptogen.md": """
<figure class="blog-figure">
  <img src="../assets/images/ashwagandha-smell-of-a-horse/mhnt-withania-2012.jpg" alt="Herbarium specimen photograph of Withania somnifera" width="800" loading="lazy" />
  <figcaption><strong>Figure.</strong> Rasayana literature and modern ashwagandha marketing are different filing systems — herbarium specimen for botanical context only. Ercé / Muséum de Toulouse, Wikimedia Commons (CC BY-SA 3.0).</figcaption>
</figure>
""",
    "stage-04-south-asian-and-other/31-rhodiolas-thin-trails.md": """
<figure class="blog-figure">
  <img src="../assets/images/rhodiolas-thin-trails/rhodiola-rosea-kz02.jpg" alt="Photograph of Rhodiola rosea succulent rosettes in alpine habitat" width="800" loading="lazy" />
  <figcaption><strong>Figure.</strong> Rhodiola’s thin trails in print start with a plant in habitat — not a clinical outcome. Photo: Kor!An, Wikimedia Commons (CC BY-SA 3.0).</figcaption>
</figure>
""",
    "stage-04-south-asian-and-other/33-licorice-the-diplomat-herb.md": """
<figure class="blog-figure">
  <img src="../assets/images/licorice-the-diplomat-herb/kohler-glycyrrhiza-1887.jpg" alt="Nineteenth-century botanical plate of Glycyrrhiza glabra from Köhler's Medizinal-Pflanzen" width="700" loading="lazy" />
  <figcaption><strong>Figure.</strong> Licorice as a European pharmacopeia plate — diplomacy in trade, not a dosing chart. Franz Eugen Köhler, <em>Medizinal-Pflanzen</em> (1887), public domain, via Wikimedia Commons.</figcaption>
</figure>
""",
    "stage-05-law-aisle-language/35-dshea-and-the-aisle.md": """
<figure class="blog-figure">
  <img src="../assets/shared/svg/soviet-adaptogen-timeline.svg" alt="Schematic timeline from Soviet adaptogen research through U.S. dietary supplement law context" width="960" height="320" loading="lazy" />
  <figcaption><strong>Figure.</strong> DSHEA shaped the U.S. aisle after the Soviet word had already traveled — schematic dates for orientation, not legal advice. <em>Schematic timeline; not to scale.</em></figcaption>
</figure>
""",
    "stage-02-soviet-construct/07-brekhman-in-vladivostok.md": """
<figure class="blog-figure">
  <img src="../assets/images/eleuthero-as-type-specimen/doronenko-eleuthero-2006.jpg" alt="Photograph of Eleutherococcus senticosus foliage and stems" width="800" loading="lazy" />
  <figcaption><strong>Figure.</strong> Far-East pharmacology needed kilograms of shrub, not ceremony — eleuthero as program plant, not a portrait of Brekhman. Photo: Stanislav Doronenko, Wikimedia Commons (CC BY 2.5).</figcaption>
</figure>
""",
}

DISCLAIMER = "This draft does not treat, cure, or prevent any disease."


def insert_block(body: str, block: str) -> str:
    if "<figure class=\"blog-figure\">" in body:
        return body
    if DISCLAIMER in body:
        idx = body.index(DISCLAIMER)
        rest = body[idx + len(DISCLAIMER) :]
        next_para = rest.find("\n\n")
        if next_para == -1:
            return body + "\n\n" + block.strip() + "\n"
        insert_at = idx + len(DISCLAIMER) + next_para + 2
        return body[:insert_at] + block.strip() + "\n\n" + body[insert_at:]
    parts = body.split("\n\n", 1)
    if len(parts) == 1:
        return body + "\n\n" + block.strip() + "\n"
    return parts[0] + "\n\n" + block.strip() + "\n\n" + parts[1]


def main() -> int:
    for rel, block in EMBEDS.items():
        path = ROOT / rel
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"^(---\n.*?\n---\n)(.*)$", raw, re.S)
        if not m:
            raise SystemExit(f"no frontmatter: {rel}")
        fm, body = m.group(1), m.group(2)
        path.write_text(fm + insert_block(body.lstrip("\n"), block), encoding="utf-8")
        print("updated", rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
