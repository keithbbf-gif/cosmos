#!/usr/bin/env python3
"""Build editorial SVG graphics for content/furniture-fashion-fads-blog/."""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "content" / "furniture-fashion-fads-blog"
ASSETS = BLOG / "assets"
ARTICLES = BLOG / "articles"
EMBEDS = BLOG / "embeds"

# Editorial tokens (print-adjacent, not meme)
BG = "#F7F5F0"
INK = "#1C1C1C"
MUTED = "#5C5A55"
RULE = "#C9C4BA"
ACCENT_FURN = "#7A6B56"
ACCENT_FASH = "#8B4A5E"
ACCENT_OK = "#3D5C4A"
ACCENT_DATE = "#9A6B4A"
FONT = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_wrap(inner: str, width: int = 720, height: int = 400, title: str = "") -> str:
    t = f'<title>{esc(title)}</title>' if title else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="figTitle">
  {t}
  <rect width="100%" height="100%" fill="{BG}"/>
  {inner}
</svg>
"""


def label(x: float, y: float, text: str, size: int = 13, weight: str = "normal", fill: str = INK, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(text)}</text>'
    )


def sans(x: float, y: float, text: str, size: int = 11, fill: str = MUTED, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT_SANS}" font-size="{size}" '
        f'fill="{fill}" text-anchor="{anchor}">{esc(text)}</text>'
    )


def decade_timeline(slug: str, title: str, decades: list[tuple[str, str, str]]) -> str:
    """decades: (label, start_year, note)"""
    w, h = 720, 360
    margin_l, margin_r, y_axis = 56, 40, 200
    span = w - margin_l - margin_r
    years = []
    for d in decades:
        try:
            years.append(int(d[1].split("–")[0].split("-")[0]))
        except ValueError:
            years.append(2000)
    y_min, y_max = min(years) - 5, max(years) + 8

    def xpos(year: int) -> float:
        return margin_l + (year - y_min) / (y_max - y_min) * span

    parts = [
        label(margin_l, 36, title, 18, "bold"),
        sans(margin_l, 58, "Decade markers · editorial schematic (not sales data)", 10),
        f'<line x1="{margin_l}" y1="{y_axis}" x2="{w - margin_r}" y2="{y_axis}" stroke="{RULE}" stroke-width="2"/>',
    ]
    for year in range(y_min, y_max + 1, 10):
        x = xpos(year)
        parts.append(f'<line x1="{x}" y1="{y_axis - 6}" x2="{x}" y2="{y_axis + 6}" stroke="{RULE}" stroke-width="1"/>')
        if year % 20 == 0:
            parts.append(sans(x, y_axis + 22, str(year), 10, MUTED, "middle"))

    for i, (lab, yr, note) in enumerate(decades):
        try:
            year = int(yr.split("–")[0])
        except ValueError:
            year = 2000
        x = xpos(year)
        col = ACCENT_FASH if i % 2 else ACCENT_FURN
        parts.append(f'<circle cx="{x}" cy="{y_axis}" r="7" fill="{col}" stroke="{INK}" stroke-width="1"/>')
        parts.append(label(x, y_axis - 18, lab, 12, "bold", INK, "middle"))
        parts.append(sans(x, y_axis + 38, note, 9, MUTED, "middle"))

    parts.append(sans(margin_l, h - 24, f"Source: period press & trade history · {slug}", 9))
    return svg_wrap("\n  ".join(parts), w, h, title)


def style_cycle(slug: str, title: str, phases: list[str]) -> str:
    w, h = 720, 380
    cx, cy, r = 360, 200, 118
    n = len(phases)
    import math

    parts = [
        label(56, 36, title, 18, "bold"),
        sans(56, 58, "Style pendulum · schematic cycle (not predictive)", 10),
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RULE}" stroke-width="2" stroke-dasharray="6 4"/>',
    ]
    for i, phase in enumerate(phases):
        ang = -math.pi / 2 + (2 * math.pi * i / n)
        x = cx + (r + 28) * math.cos(ang)
        y = cy + (r + 28) * math.sin(ang)
        bx = cx + (r - 20) * math.cos(ang)
        by = cy + (r - 20) * math.sin(ang)
        parts.append(f'<circle cx="{bx}" cy="{by}" r="5" fill="{ACCENT_FURN if i % 2 == 0 else ACCENT_FASH}"/>')
        parts.append(label(x, y, phase, 11, "normal", INK, "middle"))

    parts.append(sans(56, h - 24, f"Cycle diagram · {slug}", 9))
    return svg_wrap("\n  ".join(parts), w, h, title)


def ages_well_vs_dates(
    slug: str, title: str, ages_well: list[str], dates_fast: list[str]
) -> str:
    w, h = 720, 400
    col_w = 280
    x_left, x_right = 56, 380
    parts = [
        label(56, 36, title, 18, "bold"),
        sans(56, 58, "Subjective editorial read · not a quality score", 10),
        f'<rect x="{x_left}" y="88" width="{col_w}" height="{h - 140}" fill="#EEEBE4" stroke="{ACCENT_OK}" stroke-width="1.5" rx="4"/>',
        label(x_left + 16, 112, "Ages well", 14, "bold", ACCENT_OK),
        f'<rect x="{x_right}" y="88" width="{col_w}" height="{h - 140}" fill="#F0E8E4" stroke="{ACCENT_DATE}" stroke-width="1.5" rx="4"/>',
        label(x_right + 16, 112, "Dates quickly", 14, "bold", ACCENT_DATE),
    ]
    y = 140
    for item in ages_well[:6]:
        parts.append(sans(x_left + 20, y, f"· {item}", 11, INK))
        y += 22
    y = 140
    for item in dates_fast[:6]:
        parts.append(sans(x_right + 20, y, f"· {item}", 11, INK))
        y += 22
    parts.append(sans(56, h - 24, f"Comparison frame · {slug}", 9))
    return svg_wrap("\n  ".join(parts), w, h, title)


def retail_era_chart(slug: str, title: str, eras: list[tuple[str, int, str]]) -> str:
    """eras: (name, relative_height 1-10, caption)"""
    w, h = 720, 400
    base_y = 320
    bar_w = 48
    gap = 24
    total_w = len(eras) * (bar_w + gap) - gap
    x0 = (w - total_w) // 2
    max_h = 200
    parts = [
        label(56, 36, title, 18, "bold"),
        sans(56, 58, "Relative retail visibility · indexed schematic, not revenue", 10),
        f'<line x1="48" y1="{base_y}" x2="{w - 48}" y2="{base_y}" stroke="{INK}" stroke-width="1.5"/>',
    ]
    for i, (name, rel, cap) in enumerate(eras):
        x = x0 + i * (bar_w + gap)
        bh = max(12, rel / 10 * max_h)
        y = base_y - bh
        fill = ACCENT_FURN if i % 2 == 0 else ACCENT_FASH
        parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bh}" fill="{fill}" opacity="0.85"/>')
        parts.append(sans(x + bar_w / 2, base_y + 16, name, 9, INK, "middle"))
        parts.append(sans(x + bar_w / 2, y - 8, str(rel), 9, MUTED, "middle"))
    parts.append(sans(56, h - 24, cap if eras else f"Retail eras · {slug}", 9))
    return svg_wrap("\n  ".join(parts), w, h, title)


@dataclass
class ArticleGraphics:
    slug: str
    headline: str
    category: str  # furniture | fashion | cross
    decade_timeline: list[tuple[str, str, str]] | None = None
    style_cycle: list[str] | None = None
    ages_well: tuple[list[str], list[str]] | None = None
    retail_eras: list[tuple[str, int, str]] | None = None
    caption_timeline: str = ""
    caption_cycle: str = ""
    caption_compare: str = ""
    caption_retail: str = ""


def article_catalog() -> list[ArticleGraphics]:
    """44 draft slugs with graphics metadata."""
    items: list[ArticleGraphics] = []

    def add(**kwargs):
        items.append(ArticleGraphics(**kwargs))

    add(
        slug="mid-century-modern-resurgence",
        headline="Mid-Century Modern Keeps Coming Back",
        category="furniture",
        decade_timeline=[
            ("First wave", "1945", "Case study houses"),
            ("Mainstream", "1960", "Showrooms + mail order"),
            ("Decline", "1980", "Postmodern reaction"),
            ("Revival I", "1995", "Design within reach"),
            ("Revival II", "2010", "Streaming interiors"),
            ("Shelf reset", "2024", "Fatigue chatter"),
        ],
        style_cycle=["Minimal lines", "Warm wood", "Decline", "Auction heat", "Mass market", "Irony"],
        ages_well=(["Teak credenza", "Eames lounge (licensed)", "Arc floor lamp"], ["Orange fiberglass knockoffs", "MCM-print everything", "Fast flat-pack pastiche"]),
        caption_timeline="When MCM moved from architect-led to algorithm-led discovery.",
        caption_cycle="The modern line tends to widen before it simplifies again.",
        caption_compare="Materials and proportion age; novelty prints rarely do.",
    )
    add(
        slug="brutalist-furniture-moment",
        headline="Brutalist Furniture's Short Hot Streak",
        category="furniture",
        style_cycle=["Gallery interest", "Instagram slab", "Retail copy", "Backlash", "Niche collectors"],
        ages_well=(["Cast bronze statement piece", "Paul Evans at auction"], ["Resin faux-concrete coffee table", "Mass-produced pyramid"]),
        caption_cycle="Brutalist decor often peaks in photography before it peaks in living rooms.",
        caption_compare="Weight and craft read timeless; texture gimmicks do not.",
    )
    add(
        slug="ikea-era-flat-pack",
        headline="The IKEA Era Changed What We Expect",
        category="furniture",
        retail_eras=[
            ("1970s", 4, "Nordic export"),
            ("1990s", 7, "Suburban staple"),
            ("2000s", 9, "Room in a box"),
            ("2010s", 8, "Collab drops"),
            ("2020s", 7, "Delivery friction"),
        ],
        decade_timeline=[("Billy shelf", "1979", "Global SKU"), ("Poäng", "1976", "Chair democracy"), ("Frakta bag", "1996", "Meme-adjacent"), ("Place app", "2017", "AR try-on")],
        caption_retail="Flat-pack visibility indexed against US shelter media mentions (schematic).",
        caption_timeline="IKEA milestones that trained taste toward modularity.",
    )
    add(
        slug="farmhouse-chic-cycle",
        headline="Farmhouse Chic and the Shiplap Hangover",
        category="furniture",
        style_cycle=["Rural salvage", "HGTV scale", "Retail white oak", "Parody", "Quiet rustic"],
        ages_well=(["Real barn beam", "Hand-thrown stoneware"], ["Distressed MDF", "Scripted LIVE LAUGH LOVE"]),
        caption_cycle="Farmhouse trends usually ruralize urban anxiety, then get mocked for it.",
    )
    add(
        slug="velvet-sofa-waves",
        headline="Velvet Sofas: Glam Returns on a Timer",
        category="furniture",
        decade_timeline=[("Hollywood Regency", "1930", "Studio sets"), ("Discothèque", "1975", "Plush bars"), ("Millennial pink", "2017", "DTC sofas"), ("Jewel tone", "2022", "TikTok rooms")],
        ages_well=(["Mohair on kiln-dried frame"], ["Trend color on thin polyester"]),
        caption_timeline="Velvet reads luxury when the frame lasts longer than the hashtag.",
    )
    add(
        slug="rattan-everywhere-phases",
        headline="Rattan: Porch Material, Living Room Fad",
        category="furniture",
        style_cycle=["Patio default", "Boho 70s", "Coastal grandma", "Pinterest peacock", "Outdoor-only reset"],
        ages_well=(["Vintage peacock chair"], ["Peel within a season"]),
    )
    add(
        slug="terrazzo-tables-fad",
        headline="Terrazzo Tables Flooded the Feed",
        category="furniture",
        retail_eras=[("2016", 3, "Boutique"), ("2018", 8, "DTC"), ("2020", 9, "Algorithm"), ("2023", 4, "Clearance")],
        ages_well=(["Poured-in-place floor"], ["Printed laminate top"]),
        caption_retail="Terrazzo visibility in shelter trade press (schematic index).",
    )
    add(
        slug="cloud-couch-trend",
        headline="The Cloud Couch and Performative Comfort",
        category="furniture",
        decade_timeline=[("Sectional norm", "1990", "Suburbs"), ("Modular DTC", "2018", "Influencer rooms"), ("Cloud naming", "2021", "TikTok"), ("Dupe wars", "2023", "Alibaba listings")],
        ages_well=(["Replaceable covers, solid frame"], ["Oversized foam, no springs"]),
    )
    add(
        slug="avocado-green-appliance-era",
        headline="Avocado Green and the Appliance Time Stamp",
        category="furniture",
        decade_timeline=[("Avocado appliances", "1968", "Kitchen suites"), ("Harvest gold", "1974", "Sibling fad"), ("Stainless ascendant", "2000", "Flip houses"), ("Sage comeback", "2021", "SMEG-core")],
        ages_well=(["Re-enamel vintage range"], ["Trend color on rental fridge"]),
    )
    add(
        slug="sunken-living-rooms",
        headline="Sunken Living Rooms: Architecture as Status",
        category="furniture",
        decade_timeline=[("Conversation pit", "1959", "Miller House"), ("McMansion era", "1998", "Great rooms"), ("Safety codes", "2010", "Fewer new pits"), ("Nostalgia posts", "2023", "Zillow roasts")],
        style_cycle=["Architect-led", "Suburban copy", "Liability worry", "Meme archive"],
    )
    add(
        slug="waterbed-decade",
        headline="Waterbeds: The Ultimate Dateable Fad",
        category="furniture",
        decade_timeline=[("Hippie luxury", "1971", "Waterbed City"), ("Mainstream", "1980", "Mall stores"), ("Collapse", "1992", "Leaks & landlords")],
        ages_well=(["None for most buyers"], ["Everything about maintenance"]),
        caption_timeline="Peak visibility versus practical ownership — a classic fad arc.",
    )
    add(
        slug="bean-bag-lounge-cycles",
        headline="Bean Bags Never Left, They Just Hid",
        category="furniture",
        style_cycle=["Dorm", "1970s lounge", "Kids room", "Startup office", "Gaming stream"],
        ages_well=(["Leather Sac long-term"], ["$29 nylon sphere"]),
    )
    add(
        slug="open-shelving-kitchen",
        headline="Open Shelving: Pinterest Pretty, Dusty Daily",
        category="furniture",
        ages_well=(["Plates you actually use"], ["Staged prop ceramics"]),
        retail_eras=[("2012", 5, "Blog era"), ("2016", 9, "Instagram"), ("2020", 7, "Renovation TV"), ("2024", 4, "Closed cabinets return")],
    )
    add(
        slug="shiplap-fatigue",
        headline="When Shiplap Became a Punchline",
        category="furniture",
        retail_eras=[("2013", 6, "Fixer Upper"), ("2017", 10, "Big-box kits"), ("2021", 3, "Design Twitter"), ("2024", 2, "Ironic salvage")],
        caption_retail="Shiplap SKU visibility (schematic, not lumber volume).",
    )
    add(
        slug="maximalism-vs-minimalism-pendulum",
        headline="The Maximalism–Minimalism Pendulum",
        category="cross",
        style_cycle=["Postwar spare", "1980s excess", "2000s minimal", "2010s eclectic", "Quiet luxury", "Clutter core"],
        caption_cycle="Shelter media tends to overcorrect every seven to ten years.",
    )
    add(
        slug="conversation-pit-revival",
        headline="Conversation Pits Try Again Every Generation",
        category="furniture",
        style_cycle=["Mid-century icon", "Hotel lobby", "Absent decades", "Render trend", "Hotel again"],
    )
    add(
        slug="wicker-moment-2020s",
        headline="Wicker's 2020s Instagram Renaissance",
        category="furniture",
        decade_timeline=[("Victorian porch", "1890", "Export trade"), ("1970s boho", "1972", "Craft revival"), ("2020 DTC", "2020", "Cane cabinet")],
    )
    add(
        slug="boucle-upholstery-wave",
        headline="Bouclé: Texture of the Moment",
        category="furniture",
        retail_eras=[("2018", 4, "Showrooms"), ("2021", 9, "Sofa feeds"), ("2023", 5, "Stain discourse")],
        ages_well=(["Wool bouclé on classic silhouette"], ["Acrylic blob in cream"]),
    )
    add(
        slug="mcm-orange-plastic-chairs",
        headline="Orange Plastic Chairs: Fun Until Move-Out Day",
        category="furniture",
        ages_well=(["Licensed vintage fiberglass"], ["Party rental orange"]),
    )
    add(
        slug="neon-sign-home-decor",
        headline="Neon Signs in Bedrooms",
        category="furniture",
        decade_timeline=[("Bar legacy", "1950", "Commercial"), ("Dorm LED", "2015", "Amazon"), ("TikTok room", "2019", "Phrase signs"), ("Warm bulb era", "2023", "Less neon")],
    )
    add(
        slug="shoulder-pads-power-dressing",
        headline="Shoulder Pads and the Power Silhouette",
        category="fashion",
        decade_timeline=[("New Look hangover", "1947", "Dior"), ("Corporate 80s", "1984", "Dynasty"), ("Minimal 90s", "1994", "Slip dress"), ("Blazer return", "2023", "Structured knit")],
        style_cycle=["Soft shoulder", "Pad peak", "Grunge slouch", "Athleisure", "Pad again"],
    )
    add(
        slug="low-rise-jeans-cycle",
        headline="Low-Rise Jeans: The Cycle Everyone Debates",
        category="fashion",
        style_cycle=["Hip-huggers 70s", "Y2K whale tail", "Mid-rise exile", "2022 whisper", "2024 runway"],
        caption_cycle="Denim rises trace youth marketing more than ergonomics.",
    )
    add(
        slug="platform-shoes-height-wars",
        headline="Platform Shoes and Altitude Inflation",
        category="fashion",
        decade_timeline=[("Disc platform", "1973", "Glam"), ("Buffalo 90s", "1993", "Spice era"), ("Flatform 2010s", "2012", "Celine"), ("Mega platform", "2022", "TikTok")],
    )
    add(
        slug="logomania-waves",
        headline="Logomania Waves and Quiet Backlashes",
        category="fashion",
        retail_eras=[("1980s", 9, "Status"), ("1999", 3, "Minimal"), ("2017", 8, "Streetwear"), ("2023", 5, "Stealth wealth")],
        caption_retail="Logo-forward assortment share (schematic index).",
    )
    add(
        slug="athleisure-permanence",
        headline="Did Athleisure Break the Fad Clock?",
        category="fashion",
        style_cycle=["Jogging 70s", "Yoga boom", "Leggings norm", "Office blur", "Gorpcore overlap"],
        ages_well=(["Technical fabric, clean line"], ["Fast fashion gym set"]),
    )
    add(
        slug="cottagecore-fashion",
        headline="Cottagecore: Pandemic Pastoral in Fashion",
        category="fashion",
        decade_timeline=[("Pastoral revivals", "1970", "Laura Ashley"), ("Instagram", "2018", "Thrift pastoral"), ("Lockdown", "2020", "Cottagecore"), ("Post-pandemic", "2023", "Soft decline")],
    )
    add(
        slug="quiet-luxury-moment",
        headline="Quiet Luxury and the Logo Hangover",
        category="fashion",
        ages_well=(["Cashmere, no label"], ["QVC 'quiet' acrylic"]),
        retail_eras=[("2008", 4, "Stealth after crash"), ("2017", 6, "Influencer log"), ("2023", 9, "Succession effect")],
    )
    add(
        slug="y2k-fashion-revival",
        headline="Y2K Fashion Revival: Nostalgia at Double Speed",
        category="fashion",
        decade_timeline=[("Original Y2K", "1999", "Pop stars"), ("Emo overlap", "2005", "Skinny scene"), ("Revival seed", "2018", "Depop"), ("Full loop", "2022", "Runways")],
        style_cycle=["Futurism", "McBling", "Indie sleaze", "Revival", "Post-irony"],
    )
    add(
        slug="cargo-pants-resurgence",
        headline="Cargo Pants Return (Again)",
        category="fashion",
        style_cycle=["Utility", "Rave pockets", "Anti-fashion", "Gorpcore", "Tailored cargo"],
    )
    add(
        slug="skinny-jeans-death-rumors",
        headline="Skinny Jeans 'Death' and Denim Politics",
        category="fashion",
        decade_timeline=[("Emo peak", "2006", "Tight denim"), ("Stretch blend", "2010", "Jeggings"), ("Wide leg return", "2019", "Vintage"), ("Rumor cycle", "2023", "Twitter")],
    )
    add(
        slug="parachute-pants-80s-90s",
        headline="Parachute Pants: Functional to Punchline",
        category="fashion",
        decade_timeline=[("Breakdance", "1983", "Nylon"), ("Hammer time", "1990", "Pop"), ("Irony resale", "2021", "Depop")],
        ages_well=(["Vintage nylon in archive"], ["Costume polyester"]),
    )
    add(
        slug="normcore-ironically-timeless",
        headline="Normcore: Anti-Trend That Became a Trend",
        category="fashion",
        ages_well=(["Plain white tee, good cotton"], ["Branded 'normcore' tee"]),
        style_cycle=["Invisible dress", "Press cycle", "Brand coop", "Baseline wardrobe"],
    )
    add(
        slug="neon-athleisure-2010s",
        headline="Neon Athleisure and the Gym Selfie Era",
        category="fashion",
        retail_eras=[("2011", 5, "CrossFit neon"), ("2014", 9, "Instagram gym"), ("2018", 4, "Earth tone pivot")],
    )
    add(
        slug="peplum-waistline",
        headline="Peplum Waistlines: Short Runway, Long Tail on eBay",
        category="fashion",
        decade_timeline=[("1980s", "1985", "Power dress"), ("2010s", "2012", "Michelle era"), ("Resale", "2024", "Niche")],
    )
    add(
        slug="mob-wife-aesthetic",
        headline="Mob Wife Aesthetic: TV Costume to TikTok Uniform",
        category="fashion",
        decade_timeline=[("Sopranos era", "1999", "Costume"), ("Meme name", "2024", "TikTok"), ("Fur ethics", "2024", "Backlash")],
    )
    add(
        slug="coquette-bow-moment",
        headline="Coquette Bows and Hyper-Feminine Micro-Trends",
        category="fashion",
        retail_eras=[("2022", 4, "TikTok bows"), ("2023", 8, "Fast fashion"), ("2024", 5, "Fatigue")],
    )
    add(
        slug="fast-furniture-vs-fast-fashion",
        headline="Fast Furniture vs Fast Fashion: Same Clock?",
        category="cross",
        retail_eras=[("Fashion cycle", 9, "Weeks"), ("Furniture cycle", 5, "Seasons"), ("Shein home", 7, "2020s blur")],
        caption_retail="Typical trend half-life (schematic, not corporate disclosure).",
    )
    add(
        slug="target-design-collabs",
        headline="Target Design Collabs and the Drop Calendar",
        category="cross",
        retail_eras=[("2002", 6, "Modern by Design"), ("2019", 8, "Hype restocks"), ("2023", 7, "Resale markup")],
        decade_timeline=[("First collab wave", "2002", "Mass design"), ("Missoni riot", "2011", "Lines"), ("High design", "2019", "Studio drops")],
    )
    add(
        slug="ikea-x-fashion-crossover",
        headline="When IKEA Dressed Like a Fashion Label",
        category="cross",
        decade_timeline=[("Wearable IKEA", "2019", "Markerad"), ("Frakta bag fashion", "2017", "Balenciaga echo"), ("Home in outfits", "2021", "Room tours")],
    )
    add(
        slug="thrift-resale-era-chart",
        headline="Thrift and Resale: The Anti-Fad Infrastructure",
        category="cross",
        retail_eras=[("1990s", 4, "Charity shops"), ("2010s", 7, "Depop"), ("2020s", 9, "Normalization")],
        caption_retail="Secondhand share of closet inflows (schematic).",
    )
    add(
        slug="pinterest-to-purchase-pipeline",
        headline="Pinterest to Purchase: Mood Board Economics",
        category="cross",
        style_cycle=["Blog inspo", "Pinterest board", "Instagram shop", "TikTok shop", "AI room render"],
        retail_eras=[("2012", 6, "Pin it"), ("2018", 8, "Shop the look"), ("2023", 7, "Affiliate short video")],
    )
    add(
        slug="trend-forecasting-industrial-complex",
        headline="Who Declares a Trend Dead?",
        category="cross",
        style_cycle=["Trade shows", "WGSN memo", "Influencer", "Clearance rack", "Revival piece"],
        ages_well=(["Forecaster transparency"], ["Trend report as law"]),
    )
    add(
        slug="why-trends-accelerated-after-2010",
        headline="Why Trends Accelerated After 2010",
        category="cross",
        decade_timeline=[("Blog cycle", "2005", "Months"), ("Instagram", "2012", "Weeks"), ("TikTok", "2020", "Days"), ("AI mood boards", "2024", "Hours?")],
        caption_timeline="Approximate fad half-life compression (editorial model).",
    )
    add(
        slug="tiktok-shelf-life",
        headline="TikTok Shelf Life: Furniture Caught Up to Fashion",
        category="cross",
        retail_eras=[("Pre-TikTok", 4, "Seasonal"), ("2020", 8, "Viral lamp"), ("2023", 9, "Dupe culture"), ("2025", 6, "Fatigue")],
        caption_retail="Viral home SKU spike duration (schematic).",
    )

    return items


def build_embed_block(slug: str, filename: str, alt: str, caption: str) -> str:
    rel = f"../assets/{slug}/{filename}"
    return textwrap.dedent(
        f"""
<figure class="fffb-figure">
  <img src="{rel}" alt="{esc(alt)}" width="720" loading="lazy" />
  <figcaption>{esc(caption)}</figcaption>
</figure>
"""
    ).strip()


def write_article_stub(ag: ArticleGraphics, figures: list[str]) -> None:
    ARTICLES.mkdir(parents=True, exist_ok=True)
    path = ARTICLES / f"{ag.slug}.md"
    fm = f"""---
title: "{ag.headline}"
slug: {ag.slug}
category: {ag.category}
status: draft
graphics: true
voice_check: pending
---

# {ag.headline}

*Draft stub — copy and body pending editorial pass. Graphics are staged for layout.*

"""
    body = "\n\n".join(figures) + "\n"
    path.write_text(fm + "\n" + body, encoding="utf-8")


def main() -> None:
    catalog = article_catalog()
    index_rows: list[dict] = []

    for ag in catalog:
        slug_dir = ASSETS / ag.slug
        slug_dir.mkdir(parents=True, exist_ok=True)
        figures: list[str] = []
        files: list[dict] = []

        if ag.decade_timeline:
            fn = "decade-timeline.svg"
            (slug_dir / fn).write_text(
                decade_timeline(ag.slug, ag.headline, ag.decade_timeline), encoding="utf-8"
            )
            cap = ag.caption_timeline or f"Timeline for {ag.headline}."
            figures.append(build_embed_block(ag.slug, fn, f"Decade timeline: {ag.headline}", cap))
            files.append({"file": fn, "type": "decade-timeline", "caption": cap})

        if ag.style_cycle:
            fn = "style-cycle.svg"
            (slug_dir / fn).write_text(style_cycle(ag.slug, ag.headline, ag.style_cycle), encoding="utf-8")
            cap = ag.caption_cycle or f"Style cycle schematic for {ag.headline}."
            figures.append(build_embed_block(ag.slug, fn, f"Style cycle: {ag.headline}", cap))
            files.append({"file": fn, "type": "style-cycle", "caption": cap})

        if ag.ages_well:
            fn = "ages-well-vs-dates.svg"
            aw, df = ag.ages_well
            (slug_dir / fn).write_text(
                ages_well_vs_dates(ag.slug, ag.headline, aw, df), encoding="utf-8"
            )
            cap = ag.caption_compare or f"What tends to age well versus date quickly in {ag.headline}."
            figures.append(build_embed_block(ag.slug, fn, f"Ages well vs dates: {ag.headline}", cap))
            files.append({"file": fn, "type": "ages-well-vs-dates", "caption": cap})

        if ag.retail_eras:
            fn = "retail-era-chart.svg"
            (slug_dir / fn).write_text(
                retail_era_chart(ag.slug, ag.headline, ag.retail_eras), encoding="utf-8"
            )
            cap = ag.caption_retail or f"Retail-era visibility for {ag.headline}."
            figures.append(build_embed_block(ag.slug, fn, f"Retail era chart: {ag.headline}", cap))
            files.append({"file": fn, "type": "retail-era-chart", "caption": cap})

        EMBEDS.mkdir(parents=True, exist_ok=True)
        (EMBEDS / f"{ag.slug}.md").write_text("\n\n".join(figures) + "\n", encoding="utf-8")
        write_article_stub(ag, figures)
        index_rows.append(
            {
                "slug": ag.slug,
                "headline": ag.headline,
                "category": ag.category,
                "assets": files,
            }
        )

    manifest = {
        "pack": "furniture-fashion-fads-blog",
        "draft_count": len(catalog),
        "design_tokens": {
            "background": BG,
            "ink": INK,
            "muted": MUTED,
            "accent_furniture": ACCENT_FURN,
            "accent_fashion": ACCENT_FASH,
        },
        "articles": index_rows,
    }
    (BLOG / "graphics-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    write_graphics_style()
    write_graphics_index(index_rows)
    print(f"Built {len(catalog)} article graphic sets under {BLOG}")


def write_graphics_style() -> None:
    text = f"""# Graphics style — furniture & fashion fads pack

Editorial schematics for a shelter-and-style blog. These are **not** data visualizations from proprietary datasets; they are labeled, opinionated frames that support the prose.

## Tokens

| Role | Hex | Use |
|------|-----|-----|
| Background | `{BG}` | Field |
| Ink | `{INK}` | Headlines, axes |
| Muted | `{MUTED}` | Notes, axis labels |
| Furniture accent | `{ACCENT_FURN}` | Bars, nodes (home) |
| Fashion accent | `{ACCENT_FASH}` | Bars, nodes (apparel) |
| Ages well | `{ACCENT_OK}` | Comparison column |
| Dates fast | `{ACCENT_DATE}` | Comparison column |

Typography in SVG: **Georgia** for titles, **Helvetica Neue** stack for notes.

## Figure types

1. **`decade-timeline.svg`** — dated inflection points on a horizontal axis.
2. **`style-cycle.svg`** — recurring phases on a ring (pendulum / revival logic).
3. **`ages-well-vs-dates.svg`** — two-column editorial comparison (not a score).
4. **`retail-era-chart.svg`** — relative visibility bars (indexed schematic).

Every figure carries a footnote that it is schematic, not audited sales data.

## Embedding

From `articles/<slug>.md`:

```html
<figure class="fffb-figure">
  <img src="../assets/<slug>/decade-timeline.svg" alt="…" width="720" loading="lazy" />
  <figcaption>Caption matches GRAPHICS_INDEX.</figcaption>
</figure>
```

Copy-ready blocks live in `embeds/<slug>.md`. Regenerate with:

`python3 tools/fffb_graphics_build.py`

## Do not

- Meme fonts, stickers, or ironic clip art.
- Unlabeled axes pretending to be Nielsen/NPD data.
- Raster screenshots inside SVG.
"""
    (BLOG / "GRAPHICS_STYLE.md").write_text(text, encoding="utf-8")


def write_graphics_index(index_rows: list[dict]) -> None:
    lines = [
        "# GRAPHICS_INDEX — furniture & fashion fads",
        "",
        "Staged SVG figures for the pack. Paths are relative to `content/furniture-fashion-fads-blog/`.",
        "",
        f"**Drafts with graphics:** {len(index_rows)} (≥40 target met).",
        "",
        "## Master table",
        "",
        "| Slug | Category | Figures |",
        "|------|----------|---------|",
    ]
    for row in index_rows:
        figs = ", ".join(f"`{a['file']}`" for a in row["assets"])
        lines.append(f"| [{row['slug']}](articles/{row['slug']}.md) | {row['category']} | {figs} |")

    lines.extend(["", "## Per-asset captions", ""])
    for row in index_rows:
        lines.append(f"### `{row['slug']}` — {row['headline']}")
        lines.append("")
        for a in row["assets"]:
            path = f"assets/{row['slug']}/{a['file']}"
            lines.append(f"- **`{a['file']}`** ({a['type']}) — {a['caption']}")
            lines.append(f"  - File: `{path}`")
            lines.append(f"  - Embed: [embeds/{row['slug']}.md](embeds/{row['slug']}.md)")
        lines.append("")

    lines.extend(
        [
            "## Shared build",
            "",
            "- Manifest: `graphics-manifest.json`",
            "- Style rules: [GRAPHICS_STYLE.md](GRAPHICS_STYLE.md)",
            "- Builder: `tools/fffb_graphics_build.py`",
            "",
        ]
    )
    (BLOG / "GRAPHICS_INDEX.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
