#!/usr/bin/env python3
"""One-shot: add figure SEO YAML, meta descriptions, and anchor embeds."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAST_VERIFIED = "2026-09-14"
DEFAULT_FEAT = "assets/_shared/series-featured.svg"
SUFFIX = (
    " Educational creatine research landscape; methods and history only. "
    "Not medical or dosing advice."
)

ANCHORS: dict[str, tuple[str, str, str]] = {
    "draft-01-series-map.md": (
        "map",
        "graphics/fig-05-literature-provinces-map.svg",
        "fig-05",
    ),
    "draft-06-endogenous-synthesis.md": (
        "pathway",
        "graphics/fig-02-endogenous-synthesis-pathway.svg",
        "fig-02",
    ),
    "draft-10-phosphagen-and-ck.md": (
        "reaction",
        "graphics/fig-03-phosphagen-ck-reaction.svg",
        "fig-03",
    ),
    "draft-13-ck-shuttle.md": (
        "pathway",
        "graphics/fig-04-ck-shuttle-schematic.svg",
        "fig-04",
    ),
    "draft-26-exercise-literature-map.md": (
        "map",
        "graphics/fig-06-exercise-task-spectrum.svg",
        "fig-06",
    ),
    "draft-49-landmark-timeline.md": (
        "timeline",
        "graphics/fig-01-landmark-timeline.svg",
        "fig-01",
    ),
}

EMBEDS = {
    "fig-01": """<figure class="crl-figure crl-figure--timeline">
  <img
    src="graphics/fig-01-landmark-timeline.svg"
    alt="Timeline from 1832 Chevreul isolation through 1990s biopsy hinge papers to later reviews and position stands; dates name publications, not personal protocols."
    width="1200"
    height="560"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 1</strong> — Selected landmark dates in the creatine research file (not a dosing guide).
    <span class="figure-credit">Original diagram, creatine research landscape series.</span>
  </figcaption>
</figure>""",
    "fig-02": """<figure class="crl-figure crl-figure--pathway">
  <img
    src="graphics/fig-02-endogenous-synthesis-pathway.svg"
    alt="Schematic of arginine and glycine to guanidinoacetate via AGAT, then methylation to creatine via GAMT using S-adenosylmethionine."
    width="1200"
    height="520"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 2</strong> — Two-enzyme synthesis route (textbook geography; not a clinical pathway claim).
    <span class="figure-credit">Original diagram, creatine research landscape series.</span>
  </figcaption>
</figure>""",
    "fig-03": """<figure class="crl-figure crl-figure--reaction">
  <img
    src="graphics/fig-03-phosphagen-ck-reaction.svg"
    alt="Creatine kinase reaction showing phosphocreatine plus ADP reversibly forming creatine plus ATP near equilibrium in the cytosol."
    width="1200"
    height="480"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 3</strong> — The phosphagen buffer reaction (vocabulary, not a performance promise).
    <span class="figure-credit">Original diagram, creatine research landscape series.</span>
  </figcaption>
</figure>""",
    "fig-04": """<figure class="crl-figure crl-figure--pathway">
  <img
    src="graphics/fig-04-ck-shuttle-schematic.svg"
    alt="Schematic of mitochondrial creatine kinase rebuilding phosphocreatine, phosphocreatine diffusing to cytosolic sites of ATP use, and creatine returning."
    width="1200"
    height="520"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 4</strong> — Spatial PCr shuttle as a working hypothesis (Wallimann vocabulary).
    <span class="figure-credit">Original diagram, creatine research landscape series.</span>
  </figcaption>
</figure>""",
    "fig-05": """<figure class="crl-figure crl-figure--map">
  <img
    src="graphics/fig-05-literature-provinces-map.svg"
    alt="Six labeled provinces: chemistry, distribution, measurement, feeding protocols as methods, exercise tasks, and product statute."
    width="1200"
    height="600"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 5</strong> — Provinces of the published map (methods geography, not a shop shelf).
    <span class="figure-credit">Original diagram, creatine research landscape series.</span>
  </figcaption>
</figure>""",
    "fig-06": """<figure class="crl-figure crl-figure--map">
  <img
    src="graphics/fig-06-exercise-task-spectrum.svg"
    alt="Horizontal spectrum from seconds-long high-intensity tasks toward steady endurance work, marking where phosphagen-limited designs cluster."
    width="1200"
    height="500"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 6</strong> — Task duration vs metabolic bottleneck (why forests should not mix sprints and rides).
    <span class="figure-credit">Original diagram, creatine research landscape series.</span>
  </figcaption>
</figure>""",
}


def meta_description(title: str) -> str:
    base = f"{title}.{SUFFIX}"
    if len(base) <= 165:
        if len(base) >= 100:
            return base
        pad = " Claims: none."
        return (base + pad)[:165]
    trimmed = title[: max(20, 165 - len(SUFFIX) - 1)].rstrip(" ,;:")
    return f"{trimmed}.{SUFFIX}"[:165]


def inject_yaml(fm: str, fields: dict[str, str]) -> str:
    lines = fm.splitlines()
    out: list[str] = []
    keys_done = set()
    for line in lines:
        if ":" in line and not line.strip().startswith("#"):
            key = line.split(":", 1)[0].strip()
            if key in fields:
                out.append(f'{key}: "{fields[key]}"')
                keys_done.add(key)
                continue
        out.append(line)
    for key, val in fields.items():
        if key not in keys_done:
            out.append(f'{key}: "{val}"')
    return "\n".join(out)


def insert_embed(body: str, embed: str) -> str:
    if "crl-figure" in body:
        return body
    marker = "## Learning aims"
    idx = body.find(marker)
    if idx == -1:
        return embed + "\n\n" + body
    rest = body[idx:]
    next_h = re.search(r"\n## ", rest[len(marker) :])
    if not next_h:
        return body + "\n\n" + embed + "\n"
    insert_at = idx + len(marker) + next_h.start()
    return body[:insert_at] + "\n\n" + embed + "\n" + body[insert_at:]


def main() -> None:
    for path in sorted(ROOT.glob("draft-*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        fm, body = parts[1], parts[2]
        title_m = re.search(r'^title:\s*"(.+)"', fm, re.M)
        title = title_m.group(1) if title_m else path.stem
        kind, feat, embed_key = ANCHORS.get(path.name, ("essay", DEFAULT_FEAT, ""))
        fields = {
            "meta_description": meta_description(title),
            "featured_image": feat,
            "graphic_kind": kind,
            "last_verified": LAST_VERIFIED,
        }
        fm = inject_yaml(fm, fields)
        if embed_key:
            body = insert_embed(body, EMBEDS[embed_key])
        fm = fm.rstrip() + "\n"
        path.write_text(f"---\n{fm}---\n{body}", encoding="utf-8")
        print(f"updated {path.name}")


if __name__ == "__main__":
    main()
