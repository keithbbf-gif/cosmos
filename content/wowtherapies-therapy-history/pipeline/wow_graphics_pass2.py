#!/usr/bin/env python3
"""Generate pass-2 era SVG infographics under assets/ and draft embeds.

Rights: all output SVGs are original editorial schematics (CC0). No AI faces.
Run from repo root:
  python3 content/wowtherapies-therapy-history/pipeline/wow_graphics_pass2.py
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DRAFTS = ROOT / "drafts" / "articles"
ART = ROOT / "articles"

# Shared palette (STYLE_GUIDE)
INK = "#1C1A17"
MUTED = "#5C564C"
PAPER = "#F7F2E8"
ACCENT = "#6B2D3E"
BANDS = {
    "psycho": "#E8DCC8",
    "behav": "#D4E3D0",
    "human": "#D8E0EB",
    "cog": "#E9D4DC",
    "wave": "#EDE6F2",
    "sys": "#F0E4D4",
}


def svg_header(w: int, h: int, title: str, desc: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">{title}</title>
  <desc id="d">{desc}</desc>
  <defs>
    <style>
      .paper {{ fill: {PAPER}; }}
      .ink {{ fill: {INK}; font-family: Georgia, 'Palatino Linotype', serif; }}
      .muted {{ fill: {MUTED}; font-family: Georgia, serif; }}
      .caps {{ font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; }}
      .rule {{ stroke: {INK}; stroke-width: 1; fill: none; }}
      .tick {{ stroke: {INK}; stroke-width: 0.8; }}
    </style>
  </defs>
  <rect class="paper" width="{w}" height="{h}"/>
  <rect x="0" y="0" width="{w}" height="6" fill="{ACCENT}"/>
"""


def footer_caption(w: int, y: int, caption: str) -> str:
    return f"""
  <rect x="40" y="{y}" width="{w - 80}" height="56" fill="#FFF" stroke="{INK}" stroke-width="0.6" opacity="0.92"/>
  <text x="52" y="{y + 20}" class="muted caps">Caption</text>
  <text x="52" y="{y + 40}" class="ink" font-size="12">{caption}</text>
</svg>
"""


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def humoral_schematic() -> str:
    w, h = 1000, 520
    s = svg_header(w, h, "Humoral temperament schematic", "Four humors teaching chart, editorial schematic not a historical artifact")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 01</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Before the clinic: humors as a shared language</text>
  <text x="48" y="100" class="muted" font-size="12">Schematic — not to scale. Dates are approximate literary traditions, not laboratory facts.</text>
  <g font-family="Georgia" font-size="13">
    <rect x="60" y="140" width="200" height="90" fill="#D8E0EB" stroke="{INK}" stroke-width="0.8"/>
    <text x="72" y="168" class="ink" font-weight="bold">Blood</text>
    <text x="72" y="190" class="muted">Sanguine — warm, moist</text>
    <text x="72" y="210" class="muted">Associated: spring, air</text>
    <rect x="280" y="140" width="200" height="90" fill="#E8DCC8" stroke="{INK}" stroke-width="0.8"/>
    <text x="292" y="168" class="ink" font-weight="bold">Yellow bile</text>
    <text x="292" y="190" class="muted">Choleric — hot, dry</text>
    <text x="292" y="210" class="muted">Associated: summer, fire</text>
    <rect x="500" y="140" width="200" height="90" fill="#D4E3D0" stroke="{INK}" stroke-width="0.8"/>
    <text x="512" y="168" class="ink" font-weight="bold">Phlegm</text>
    <text x="512" y="190" class="muted">Phlegmatic — cold, moist</text>
    <text x="512" y="210" class="muted">Associated: winter, water</text>
    <rect x="720" y="140" width="200" height="90" fill="#E9D4DC" stroke="{INK}" stroke-width="0.8"/>
    <text x="732" y="168" class="ink" font-weight="bold">Black bile</text>
    <text x="732" y="190" class="muted">Melancholic — cold, dry</text>
    <text x="732" y="210" class="muted">Melancholy as physiology</text>
  </g>
  <line x1="80" y1="280" x2="920" y2="280" class="rule"/>
  <text x="80" y="268" class="muted caps">Parallel care settings (not psychotherapy)</text>
  <text x="100" y="310" class="ink" font-size="13">• Asklepian incubation — dream interpretation at sanctuaries (c. 5th c. BCE–)</text>
  <text x="100" y="334" class="ink" font-size="13">• Galenic medicine — temperament + regimen (2nd c. CE onward)</text>
  <text x="100" y="358" class="ink" font-size="13">• Pastoral confession / spiritual direction — speech without a fee-for-service hour</text>
  <text x="100" y="382" class="ink" font-size="13">• Islamic bimaristans — institutional wards, not consulting rooms</text>
  <text x="100" y="406" class="ink" font-size="13">• Burton, <tspan font-style="italic">Anatomy of Melancholy</tspan> (1621) — literary melancholy as a door to rumination</text>
"""
    s += footer_caption(
        w,
        430,
        "Fig. 1. Editorial humoral schematic summarizing how pre-modern clinicians named inner states. Original ink drawing (CC0). No patient likenesses.",
    )
    return s


def asylum_reform_timeline() -> str:
    w, h = 1100, 480
    s = svg_header(w, h, "Asylum reform timeline", "Moral treatment and asylum reform milestones")
    s += """
  <text x="48" y="44" class="ink caps">Era 02</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Asylums, moral treatment, and reform pressure</text>
  <line x1="80" y1="200" x2="1020" y2="200" class="rule" marker-end="url(#arrow)"/>
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#1C1A17"/></marker></defs>
"""
    milestones = [
        (120, "1793", "Pinel at Bicêtre", "Unchaining narrative — see Weiner on legend"),
        (280, "1796", "York Retreat", "Tuke family — moral management"),
        (420, "1841", "Dix memorials", "US asylum inspection campaign"),
        (560, "1908", "Beers memoir", "A Mind That Found Itself"),
        (720, "1909", "National Committee", "Mental hygiene movement"),
        (880, "1950s", "Deinstitutionalization", "Community care debates"),
    ]
    for x, year, title, note in milestones:
        s += f"""
  <line x1="{x}" y1="200" x2="{x}" y2="160" class="tick"/>
  <circle cx="{x}" cy="154" r="5" fill="{ACCENT}"/>
  <text x="{x - 18}" y="130" class="ink" font-size="12" font-weight="bold">{year}</text>
  <text x="{x - 40}" y="230" class="ink" font-size="12" font-weight="bold">{title}</text>
  <text x="{x - 55}" y="248" class="muted" font-size="11">{note}</text>
"""
    s += footer_caption(
        w,
        360,
        "Fig. 1. Selected asylum-reform milestones (schematic). Do not treat Robert-Fleury’s 1876 canvas as documentary evidence. Original SVG (CC0).",
    )
    return s


def hypnosis_salpetriere() -> str:
    w, h = 1000, 440
    s = svg_header(w, h, "Hypnosis and the talking cure schematic", "Salpêtrière lecture hall as architectural schematic without portraits")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 03</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Hypnosis, hysteria, and the birth of a talking method</text>
  <rect x="80" y="130" width="840" height="180" fill="#EDE6F2" stroke="{INK}" stroke-width="0.8"/>
  <text x="100" y="160" class="ink" font-weight="bold">Amphitheater lecture (schematic floor plan)</text>
  <ellipse cx="500" cy="220" rx="120" ry="50" fill="#FFF" stroke="{INK}"/>
  <text x="500" y="224" text-anchor="middle" class="muted" font-size="12">Demonstration bed</text>
  <text x="120" y="250" class="muted" font-size="12">Tiered seating — physicians &amp; students observe symptoms</text>
  <path d="M200,280 Q500,320 800,280" fill="none" stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="6 4"/>
  <text x="100" y="340" class="ink" font-size="13">Charcot’s Tuesday lectures (Salpêtrière) → Janet’s dissociation → Freud &amp; Breuer, <tspan font-style="italic">Studies on Hysteria</tspan> (1895)</text>
  <text x="100" y="364" class="muted" font-size="12">No patient likenesses in this plate — architecture and citation chain only.</text>
"""
    s += footer_caption(
        w,
        370,
        "Fig. 1. Editorial schematic of lecture-demonstration settings. Brouillet’s 1887 painting may be cited separately under PD; this diagram is original (CC0).",
    )
    return s


def psychoanalytic_branches() -> str:
    w, h = 1000, 500
    s = svg_header(w, h, "Psychoanalytic branches", "Neo-Freudian and analytic schools branching schematic")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 04</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">The psychoanalytic century — branches, not a single church</text>
  <rect x="420" y="120" width="160" height="56" fill="{BANDS['psycho']}" stroke="{INK}"/>
  <text x="500" y="152" text-anchor="middle" class="ink" font-weight="bold">Freudian core</text>
  <line x1="500" y1="176" x2="500" y2="210" class="rule"/>
  <line x1="200" y1="210" x2="800" y2="210" class="rule"/>
  <line x1="200" y1="210" x2="200" y2="250" class="rule"/>
  <line x1="350" y1="210" x2="350" y2="250" class="rule"/>
  <line x1="500" y1="210" x2="500" y2="250" class="rule"/>
  <line x1="650" y1="210" x2="650" y2="250" class="rule"/>
  <line x1="800" y1="210" x2="800" y2="250" class="rule"/>
"""
    boxes = [
        (120, "Jung", "Analytical psychology"),
        (270, "Adler", "Individual psychology"),
        (420, "Klein", "Object relations"),
        (570, "Horney", "Cultural psychoanalysis"),
        (720, "Anna Freud", "Ego psychology"),
    ]
    for x, title, sub in boxes:
        s += f"""
  <rect x="{x}" y="250" width="160" height="70" fill="{BANDS['psycho']}" stroke="{INK}" stroke-width="0.8"/>
  <text x="{x + 12}" y="278" class="ink" font-weight="bold">{title}</text>
  <text x="{x + 12}" y="300" class="muted" font-size="12">{sub}</text>
"""
    s += f"""
  <text x="80" y="360" class="ink" font-size="13">Institutional spread: Vienna → Zurich → London → New York training institutes (dates vary by society).</text>
  <text x="80" y="384" class="muted" font-size="12">Winnicott and object-relations lineages continue off this chart — see figure essays.</text>
"""
    s += footer_caption(w, 400, "Fig. 1. Branching schematic of analytic schools (simplified). Original SVG (CC0); photograph embeds only per PORTRAIT_SOURCES.md.")
    return s


def behavior_clinic_flow() -> str:
    w, h = 1000, 420
    s = svg_header(w, h, "Behavior therapy in the clinic", "Learning-theory to exposure flow")
    steps = [
        "Functional analysis",
        "Target behavior",
        "Contingency map",
        "Exposure / skills",
        "Behavioral experiment",
        "Outcome measure",
    ]
    s += """
  <text x="48" y="44" class="ink caps">Era 05</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Behaviorism enters the consulting room</text>
"""
    x = 60
    for i, label in enumerate(steps):
        s += f"""
  <rect x="{x}" y="150" width="130" height="52" fill="{BANDS['behav']}" stroke="{INK}" stroke-width="0.8"/>
  <text x="{x + 10}" y="182" class="ink" font-size="12">{label}</text>
"""
        if i < len(steps) - 1:
            s += f'<line x1="{x + 130}" y1="176" x2="{x + 150}" y2="176" class="rule" marker-end="url(#a)"/>'
        x += 150
    s += '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#1C1A17"/></marker></defs>'
    s += f"""
  <text x="60" y="250" class="muted" font-size="12">Landmarks: Wolpe systematic desensitization (1958); Eysenck outcome debates; DSM-III behavioral anchors.</text>
  <text x="60" y="274" class="ink" font-size="13">Ethical line: no reproduction of child-laboratory imagery (Little Albert) as illustration.</text>
"""
    s += footer_caption(w, 320, "Fig. 1. Editorial flow from learning theory to manualized behavior therapy. Original schematic (CC0).")
    return s


def humanistic_axes() -> str:
    w, h = 900, 460
    s = svg_header(w, h, "Humanistic therapies axes", "Rogerian core conditions schematic")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 06</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Humanistic and existential « third force »</text>
  <polygon points="450,140 620,360 280,360" fill="{BANDS['human']}" stroke="{INK}" stroke-width="0.8"/>
  <text x="450" y="200" text-anchor="middle" class="ink" font-weight="bold">Congruence</text>
  <text x="330" y="340" class="ink" font-weight="bold">Empathy</text>
  <text x="540" y="340" class="ink" font-weight="bold">Unconditional</text>
  <text x="540" y="358" class="ink" font-weight="bold">positive regard</text>
  <text x="80" y="400" class="muted" font-size="12">Existential strand (Frankl, Yalom): meaning, mortality, choice — parallel, not identical to Rogerian posture.</text>
"""
    s += footer_caption(w, 410, "Fig. 1. Rogerian « core conditions » as an editorial triangle. Original SVG (CC0); no therapist or client likenesses.")
    return s


def systems_map() -> str:
    w, h = 1000, 480
    s = svg_header(w, h, "Family systems map", "Circular causality schematic")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 07</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Families, systems, and circular causality</text>
  <circle cx="500" cy="250" r="140" fill="none" stroke="{INK}" stroke-width="1"/>
  <circle cx="500" cy="110" r="36" fill="{BANDS['sys']}" stroke="{INK}"/>
  <text x="500" y="115" text-anchor="middle" class="ink" font-size="11">Parent A</text>
  <circle cx="640" cy="250" r="36" fill="{BANDS['sys']}" stroke="{INK}"/>
  <text x="640" y="255" text-anchor="middle" class="ink" font-size="11">Child</text>
  <circle cx="500" cy="390" r="36" fill="{BANDS['sys']}" stroke="{INK}"/>
  <text x="500" y="395" text-anchor="middle" class="ink" font-size="11">Parent B</text>
  <circle cx="360" cy="250" r="36" fill="{BANDS['sys']}" stroke="{INK}"/>
  <text x="360" y="255" text-anchor="middle" class="ink" font-size="11">School</text>
  <path d="M500,146 Q580,180 610,230" fill="none" stroke="{ACCENT}" stroke-width="1.2" marker-end="url(#m)"/>
  <path d="M610,270 Q580,320 500,354" fill="none" stroke="{ACCENT}" stroke-width="1.2"/>
  <path d="M500,354 Q420,320 390,270" fill="none" stroke="{ACCENT}" stroke-width="1.2"/>
  <path d="M390,230 Q420,180 500,146" fill="none" stroke="{ACCENT}" stroke-width="1.2"/>
  <defs><marker id="m" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#6B2D3E"/></marker></defs>
  <text x="80" y="440" class="muted" font-size="12">Satir, Minuchin, Haley — structural &amp; strategic schools add boundaries and coalitions (see figure essays).</text>
"""
    s += footer_caption(w, 448, "Fig. 1. Circular causality among family and institution nodes. Abstract shapes only (CC0 editorial).")
    return s


def cbt_model() -> str:
    w, h = 900, 400
    s = svg_header(w, h, "CBT model schematic", "Thought feeling behavior triangle")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 08</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Cognitive therapy and the empirical turn</text>
  <polygon points="450,130 620,300 280,300" fill="{BANDS['cog']}" stroke="{INK}" stroke-width="0.8"/>
  <text x="450" y="160" text-anchor="middle" class="ink" font-weight="bold">Automatic thoughts</text>
  <text x="310" y="290" class="ink" font-weight="bold">Emotions</text>
  <text x="560" y="290" class="ink" font-weight="bold">Behaviors</text>
  <text x="80" y="340" class="muted" font-size="12">Beck depression trials (1970s–) and Ellis REBT (1962) — manual + measurement, not brain CGI stock art.</text>
"""
    s += footer_caption(w, 350, "Fig. 1. Cognitive-behavioral reciprocity (editorial triangle). Original SVG (CC0).")
    return s


def attachment_dyad() -> str:
    w, h = 900, 420
    s = svg_header(w, h, "Attachment dyad schematic", "Caregiver-child secure base abstract")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 09</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Attachment: nurseries to the therapy hour</text>
  <rect x="200" y="160" width="120" height="80" rx="8" fill="{BANDS['human']}" stroke="{INK}"/>
  <text x="260" y="205" text-anchor="middle" class="ink">Caregiver</text>
  <rect x="520" y="160" width="120" height="80" rx="8" fill="{BANDS['human']}" stroke="{INK}"/>
  <text x="580" y="205" text-anchor="middle" class="ink">Child</text>
  <line x1="320" y1="200" x2="520" y2="200" class="rule" stroke-width="1.4"/>
  <text x="420" y="190" text-anchor="middle" class="muted" font-size="11">secure base</text>
  <text x="80" y="280" class="ink" font-size="13">Bowlby wartime nurseries → Robertson films → Strange Situation (Ainsworth) → AAI in adult therapy discourse.</text>
"""
    s += footer_caption(w, 330, "Fig. 1. Abstract secure-base dyad (no faces or photographs). Original schematic (CC0).")
    return s


def trauma_timeline() -> str:
    return asylum_reform_timeline().replace("Era 02", "Era 10").replace(
        "Asylums, moral treatment, and reform pressure",
        "Trauma lineages: shell shock to complex PTSD",
    ).replace(
        "Pinel at Bicêtre",
        "WWI shell shock clinics",
    ).replace(
        "York Retreat",
        "Combat stress units",
    ).replace(
        "Dix memorials",
        "Vietnam PTSD recognition",
    ).replace(
        "Beers memoir",
        "Herman, Trauma and Recovery",
    ).replace(
        "National Committee",
        "DSM-III PTSD",
    ).replace(
        "Deinstitutionalization",
        "Complex PTSD debates",
    ).replace(
        "asylum-reform milestones",
        "trauma-naming milestones",
    )


def feminist_relational() -> str:
    w, h = 900, 400
    s = svg_header(w, h, "Feminist relational axes", "Power and mutuality schematic")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 11</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Feminist and relational therapies</text>
  <line x1="100" y1="220" x2="800" y2="220" class="rule"/>
  <text x="100" y="200" class="muted" font-size="11">Hierarchical expert</text>
  <text x="720" y="200" class="muted" font-size="11">Mutual / relational</text>
  <text x="80" y="260" class="ink" font-size="13">Chesler (1972), Miller (1976), Jordan et al. — critique of neutrality myths &amp; power in the room.</text>
  <text x="80" y="284" class="muted" font-size="12">No stock « Rosie » clipart — conceptual axis only.</text>
"""
    s += footer_caption(w, 310, "Fig. 1. Editorial axis from hierarchical to relational models. Original SVG (CC0).")
    return s


def liberation_map() -> str:
    w, h = 1000, 440
    s = svg_header(w, h, "Liberation psychology map", "Global south clinical critique schematic")
    s += f"""
  <text x="48" y="44" class="ink caps">Era 12</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Multicultural, liberation, and decolonial psychologies</text>
  <rect x="80" y="140" width="260" height="100" fill="{BANDS['wave']}" stroke="{INK}"/>
  <text x="92" y="168" class="ink" font-weight="bold">Fanon — colonial wound</text>
  <text x="92" y="190" class="muted" font-size="12">Algeria / Black Skin, White Masks</text>
  <rect x="370" y="140" width="260" height="100" fill="{BANDS['wave']}" stroke="{INK}"/>
  <text x="382" y="168" class="ink" font-weight="bold">Martín-Baró — lib. psychology</text>
  <text x="382" y="190" class="muted" font-size="12">UCA, El Salvador</text>
  <rect x="660" y="140" width="260" height="100" fill="{BANDS['wave']}" stroke="{INK}"/>
  <text x="672" y="168" class="ink" font-weight="bold">Sue &amp; Sue — multicultural counseling</text>
  <text x="672" y="190" class="muted" font-size="12">US training &amp; competence models</text>
  <text x="80" y="280" class="ink" font-size="13">Morita therapy &amp; Bose (Calcutta) appear in figure essays — not reduced to a flag collage.</text>
"""
    s += footer_caption(w, 350, "Fig. 1. Three liberation/multicultural anchors (schematic). Original SVG (CC0); no AI faces or flag stock.")
    return s


def third_wave_stack() -> str:
    w, h = 900, 420
    s = svg_header(w, h, "Third wave stack", "DBT ACT mindfulness layering")
    s += """
  <text x="48" y="44" class="ink caps">Era 13</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Third-wave therapies and mindfulness in the room</text>
"""
    layers = [
        "Traditional CBT skills",
        "Mindfulness / acceptance",
        "Values &amp; dialectics",
        "Community / skills group",
    ]
    y = 130
    for lab in layers:
        s += f'<rect x="200" y="{y}" width="500" height="48" fill="{BANDS["wave"]}" stroke="{INK}" stroke-width="0.8"/>'
        s += f'<text x="220" y="{y + 30}" class="ink" font-size="13">{lab}</text>'
        y += 56
    s += footer_caption(
        w,
        360,
        "Fig. 1. Layered third-wave stack (DBT, ACT, mindfulness integrations). Original schematic (CC0).",
    )
    return s


def counseling_profession_timeline() -> str:
    w, h = 1100, 460
    s = svg_header(w, h, "Counseling profession timeline", "Credentialing and professional associations")
    s += """
  <text x="48" y="44" class="ink caps">Era 14</text>
  <text x="48" y="74" class="ink" font-size="24" font-weight="bold">Counseling as a profession</text>
  <line x1="80" y1="210" x2="1020" y2="210" class="rule"/>
"""
    items = [
        (120, "1909", "Parsons vocational guidance", "Boston"),
        (300, "1952", "APGA founded", "→ ACA lineage"),
        (480, "1976", "CACREP accreditation", "Training standards"),
        (660, "1980s", "Licensure spread", "State boards"),
        (840, "2010s", "Telemental health", "Policy & ethics codes"),
    ]
    for x, year, title, note in items:
        s += f"""
  <line x1="{x}" y1="210" x2="{x}" y2="170" class="tick"/>
  <text x="{x - 20}" y="155" class="ink" font-weight="bold">{year}</text>
  <text x="{x - 50}" y="240" class="ink" font-size="12" font-weight="bold">{title}</text>
  <text x="{x - 55}" y="258" class="muted" font-size="11">{note}</text>
"""
    s += footer_caption(w, 340, "Fig. 1. Counseling profession milestones (selected). Original timeline SVG (CC0).")
    return s


ERA_SPECS: list[tuple[str, str, str, callable]] = [
    ("before-consulting-room", "humoral-four-humors-schematic.svg", humoral_schematic),
    ("asylums-moral-treatment", "asylum-reform-timeline.svg", asylum_reform_timeline),
    ("hypnosis-hysteria-talking-cure", "salpetriere-lecture-schematic.svg", hypnosis_salpetriere),
    ("psychoanalytic-century", "psychoanalytic-branches.svg", psychoanalytic_branches),
    ("behaviorism-in-the-clinic", "behavior-clinic-flow.svg", behavior_clinic_flow),
    ("humanistic-existential-therapies", "humanistic-core-triangle.svg", humanistic_axes),
    ("families-systems-therapy", "family-systems-cycle.svg", systems_map),
    ("cognitive-therapy-empirical-turn", "cbt-thought-emotion-behavior.svg", cbt_model),
    ("attachment-therapy-hour", "attachment-secure-base-dyad.svg", attachment_dyad),
    ("trauma-lineages", "trauma-naming-timeline.svg", trauma_timeline),
    ("feminist-relational-therapies", "feminist-relational-axis.svg", feminist_relational),
    ("multicultural-liberation-psychology", "liberation-psychology-map.svg", liberation_map),
    ("third-wave-mindfulness-clinic", "third-wave-stack.svg", third_wave_stack),
    ("counseling-as-a-profession", "counseling-profession-timeline.svg", counseling_profession_timeline),
]

# Map article file prefix to slug folder name
ARTICLE_FILES = [
    "01-before-the-consulting-room.md",
    "02-asylum-and-moral-treatment.md",
    "03-hypnosis-hysteria-talking-cure.md",
    "04-psychoanalytic-century.md",
    "05-behaviorism-in-the-clinic.md",
    "06-humanistic-existential.md",
    "07-systems-and-families.md",
    "08-cognitive-empirical-turn.md",
    "09-attachment-in-the-room.md",
    "10-trauma-lineages.md",
    "11-feminist-relational.md",
    "12-multicultural-liberation.md",
    "13-third-wave.md",
    "14-counseling-as-a-profession.md",
]


def deepen_shared_timeline() -> None:
    src = ROOT / "staged" / "graphics" / "fig-01-timeline-psychotherapy.svg"
    dst = ASSETS / "shared" / "svg" / "timeline-psychotherapy-master.svg"
    if not src.exists():
        return
    text = src.read_text(encoding="utf-8")
    extra = """
    <line x1="180" y1="280" x2="180" y2="330" class="tick"/>
    <circle cx="180" cy="336" r="5" fill="#6B2D3E"/>
    <text x="100" y="352" class="label ink">Dix — asylum inspection</text>
    <text x="100" y="368" class="note muted">US memorials — 1840s</text>
    <line x1="600" y1="280" x2="600" y2="330" class="tick"/>
    <circle cx="600" cy="336" r="5" fill="#3D5A80"/>
    <text x="520" y="352" class="label ink">Bowlby attachment theory</text>
    <text x="520" y="368" class="note muted">1969–73 monographs</text>
    <line x1="720" y1="280" x2="720" y2="220" class="tick"/>
    <circle cx="720" cy="214" r="5" fill="#5C4D7A"/>
    <text x="640" y="200" class="label ink">Herman — trauma recovery</text>
    <text x="640" y="216" class="note muted">1992</text>
"""
    if "Dix — asylum inspection" not in text:
        text = text.replace("  <rect x=\"48\" y=\"430\"", extra + "\n  <rect x=\"48\" y=\"430\"")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")

    src2 = ROOT / "staged" / "graphics" / "fig-02-schools-of-thought.svg"
    dst2 = ASSETS / "shared" / "svg" / "schools-of-thought-map.svg"
    if src2.exists():
        t2 = src2.read_text(encoding="utf-8")
        if "Integrative" not in t2:
            t2 = t2.replace(
                "</svg>",
                """
  <rect x="420" y="540" width="360" height="48" fill="#FFF" stroke="#1C1A17" stroke-width="0.8"/>
  <text x="432" y="568" class="ink" font-size="12">Integrative / multicultural practice — dashed ties across boxes (editorial note).</text>
</svg>""",
            )
        dst2.write_text(t2, encoding="utf-8")


def figure_block(slug: str, fig_name: str, alt: str, caption: str, rel: str) -> str:
    fid = f"{slug}.{fig_name.replace('.svg', '').replace('-', '_')}"
    return textwrap.dedent(
        f"""
<!-- figure-id: {fid} -->
![{alt}]({rel})

*{caption}*

*Rights: original editorial SVG (CC0). No AI-generated faces or likenesses.*
"""
    ).strip() + "\n\n"


def inject_drafts() -> None:
    DRAFTS.mkdir(parents=True, exist_ok=True)
    for i, (slug, fname, builder) in enumerate(ERA_SPECS):
        art_file = ART / ARTICLE_FILES[i]
        if not art_file.exists():
            continue
        rel = f"../../assets/era/{slug}/{fname}"
        alt = f"Editorial schematic for {slug.replace('-', ' ')}"
        caption = f"Figure 1. Pass-2 infographic for era essay « {slug} » (see GRAPHICS_INDEX.md)."
        block = figure_block(slug, fname, alt, caption, rel)
        body = art_file.read_text(encoding="utf-8")
        marker = "**Educational note.**"
        if marker in body and block not in body:
            parts = body.split(marker, 1)
            # After first paragraph following educational note
            rest = parts[1]
            para_end = rest.find("\n\n", rest.find("\n") + 1)
            if para_end == -1:
                para_end = 0
            insert_at = len(parts[0]) + len(marker) + para_end
            new_body = body[:insert_at] + "\n\n" + block + body[insert_at:]
        else:
            new_body = body.rstrip() + "\n\n" + block
        header = (
            f"<!-- graphics-pass: 2 | source: articles/{ARTICLE_FILES[i]} | do not publish without editor merge -->\n"
        )
        (DRAFTS / ARTICLE_FILES[i]).write_text(header + new_body, encoding="utf-8")


def main() -> None:
    for slug, fname, builder in ERA_SPECS:
        out = ASSETS / "era" / slug / fname
        write(out, builder())
    deepen_shared_timeline()
    # Copy portrait plates to assets/figures (monogram only)
    staged = ROOT / "staged" / "graphics"
    for svg in staged.glob("fig-0*-portrait*.svg"):
        write(ASSETS / "figures" / "monogram" / svg.name, svg.read_text(encoding="utf-8"))
    inject_drafts()
    print(f"Wrote {len(ERA_SPECS)} era SVGs under {ASSETS}")
    print(f"Drafts with embeds: {DRAFTS}")


if __name__ == "__main__":
    main()
