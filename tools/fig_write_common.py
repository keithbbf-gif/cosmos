"""Shared front matter and figure blocks for fig-history staging articles."""

from __future__ import annotations

from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content" / "fig-history-ancient-to-today"
STAGING = PACK / "articles" / "_staging"

SVG = {
    "timeline": "../../../assets/shared/svg/timeline-fig-cultivation-master.svg",
    "med": "../../../assets/shared/svg/map-mediterranean-fig-belt.svg",
    "silk": "../../../assets/shared/svg/map-silk-road-dried-fig-trade.svg",
    "maritime": "../../../assets/shared/svg/trade-mediterranean-maritime-routes.svg",
    "syconium": "../../../assets/shared/svg/botanical-syconium-morphology-plate.svg",
    "leaf": "../../../assets/shared/svg/botanical-leaf-lobing-plate.svg",
    "drying": "../../../assets/shared/svg/process-drying-sundry-flow.svg",
    "orchard": "../../../assets/shared/svg/schematic-ancient-orchard-irrigation.svg",
    "chart": "../../../assets/shared/svg/chart-variety-regions-comparative.svg",
    "wasp": "../../../assets/shared/svg/caprification-wasp-cycle.svg",
}


def fm(
    title: str,
    slug: str,
    series_no: int,
    dek: str,
    mix: str,
    region: str,
    era: str,
    figures: list[str],
    tags: list[str],
    sources: list[str],
    mix_secondary: str = "",
    status: str = "staging",
) -> str:
    fig_yaml = "\n".join(f"  - {f}" for f in figures)
    tag_yaml = "\n".join(f"  - {t}" for t in tags)
    src_yaml = "\n".join(f"  - {s}" for s in sources)
    sec = f"mix_secondary: {mix_secondary}\n" if mix_secondary else ""
    return f"""---
title: "{title}"
slug: {slug}
series: History of the Fig
series_no: {series_no}
dek: "{dek}"
mix: {mix}
{sec}region: {region}
era: {era}
status: {status}
voice_check: human
author: FigRoots Editorial
canonical_site: figroots.com
wp_type: post
wp_status: draft
figures:
{fig_yaml}
categories:
  - History of the Fig
tags:
{tag_yaml}
sources_key:
{src_yaml}
---
"""


def figure(fid: str, alt: str, path: str, caption: str) -> str:
    return (
        f"<!-- figure-id: {fid} -->\n"
        f"![{alt}]({path})\n\n"
        f"*{caption}*\n"
    )


def write_article(slug: str, text: str) -> Path:
    d = STAGING / slug
    d.mkdir(parents=True, exist_ok=True)
    p = d / "index.md"
    p.write_text(text, encoding="utf-8")
    return p
