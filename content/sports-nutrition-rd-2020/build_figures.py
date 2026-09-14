#!/usr/bin/env python3
"""Generate figures/ SVG heroes and RIGHTS.md for sports-nutrition-rd-2020."""
from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"

W, H = 640, 400
FONT = "system-ui, Segoe UI, Helvetica, Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"

SPECS: dict[str, dict[str, str]] = {
    "daily-protein-targets": {
        "kind": "curve",
        "title": "Daily protein vs lean-mass response (schematic)",
        "subtitle": "Inspired by Morton 2018 / Tagawa 2020 — illustrative, not primary data",
        "alt": "Schematic curve flattening near 1.6 grams protein per kilogram body mass per day.",
        "caption": "Illustrative dose–response: most lean-mass gain in meta-analyses sits below roughly 1.6 g/kg/day when resistance training is present; higher intakes show smaller average increments.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "per-meal-dose-trommelen": {
        "kind": "mps_bars",
        "title": "Muscle protein synthesis after feeding (schematic)",
        "subtitle": "Trommelen 2023 — 25 g vs 100 g milk protein, 12 h window",
        "alt": "Bar chart comparing longer muscle protein synthesis elevation after 100 grams versus 25 grams milk protein.",
        "caption": "Schematic only: a large single meal can sustain aminoacidemia and MPS longer than the old 3–4 h ceiling implied; this is not a hypertrophy outcome trial.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "protein-distribution": {
        "kind": "meals",
        "title": "Protein spread across the day (schematic)",
        "subtitle": "Distribution habit — not a separate law from daily total",
        "alt": "Timeline showing protein grams distributed across four meals in a day.",
        "caption": "Illustrative day pattern: even distribution helps some athletes hit daily totals; acute MPS studies do not by themselves prove superior hypertrophy for four vs three meals.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "leucine-and-quality-scores": {
        "kind": "bars",
        "title": "Protein quality scores (illustrative ranks)",
        "subtitle": "DIAAS-style ordering — not a product label",
        "alt": "Bar chart ranking milk, egg, soy, and wheat illustrative digestibility scores.",
        "caption": "Schematic ranking only: ileal digestibility and leucine content change how much food is needed to trigger synthesis; scores are not permission to ignore total daily protein.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "timing-around-training": {
        "kind": "timeline",
        "title": "Training session on a day clock (schematic)",
        "subtitle": "Session fueling matters more than a 30-minute myth",
        "alt": "Clock diagram with training block and protein-containing meals before and after.",
        "caption": "Illustrative timing: pre- and post-session meals support training and recovery; the narrow “window” is less important than the day’s total protein and energy when those are adequate.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "eaa-vs-intact-protein": {
        "kind": "split",
        "title": "Intact protein vs free EAAs (schematic)",
        "subtitle": "Tool vs meal",
        "alt": "Diagram comparing a plate of food to a measured essential amino acid blend.",
        "caption": "Schematic only: free-form EAAs can raise aminoacidemia quickly; whole-food protein still carries the matrix, micronutrients, and habits most teams want.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "bcaa-when-diet-is-high": {
        "kind": "curve",
        "title": "Marginal benefit when diet is already high (schematic)",
        "subtitle": "BCAAs on top of adequate protein",
        "alt": "Curve showing diminishing incremental benefit of branched-chain amino acids when daily protein is already high.",
        "caption": "Illustrative: when dietary protein and leucine are sufficient, isolated BCAAs add little in most resistance-training contexts cited in ISSN 2023 and related work.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "food-matrix-and-real-meals": {
        "kind": "plate",
        "title": "Whole meal vs isolated powder (schematic)",
        "subtitle": "Matrix effects — not anti-supplement dogma",
        "alt": "Icon plate with mixed foods beside a single supplement scoop icon.",
        "caption": "Schematic only: mixed meals deliver protein within carbohydrate, fat, and fiber matrices that change digestion speed; powders are tools when food is impractical.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "protein-for-strength-hypertrophy": {
        "kind": "stack",
        "title": "Training plus protein (schematic)",
        "subtitle": "Resistance work is the driver",
        "alt": "Stack diagram placing resistance training as primary and dietary protein as supporting.",
        "caption": "Illustrative model: hypertrophy trials that add protein without progressive lifting show small or null effects; protein supports work that is already programmed.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "protein-for-endurance-ultra": {
        "kind": "timeline",
        "title": "Endurance week protein (schematic)",
        "subtitle": "Repair and adaptation between sessions",
        "alt": "Weekly timeline with long sessions and elevated protein on hard days.",
        "caption": "Schematic only: endurance athletes often need adequate daily protein for repair; per-session gel flavor is secondary to total intake and carbohydrate availability.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "concurrent-training": {
        "kind": "split",
        "title": "Strength and endurance same week (schematic)",
        "subtitle": "One amino-acid pool",
        "alt": "Diagram showing strength and endurance sessions sharing recovery nutrition.",
        "caption": "Illustrative: concurrent training raises total protein needs versus either mode alone in many programs; timing protein around the harder session is practical, not magical.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "presleep-protein": {
        "kind": "timeline",
        "title": "Overnight gap (schematic)",
        "subtitle": "Pre-sleep feeding in research diets",
        "alt": "Night timeline highlighting protein intake before sleep.",
        "caption": "Schematic only: pre-sleep protein studies used controlled doses (often casein-rich) in measured protocols; outcomes are not a promise of better sleep or injury treatment.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "cold-water-and-protein": {
        "kind": "contrast",
        "title": "Cold water immersion after lifting (schematic)",
        "subtitle": "Fuchs 2020, 2025 — acute interaction",
        "alt": "Diagram contrasting post-lift cold immersion with dietary amino acid use.",
        "caption": "Illustrative: cold-water immersion after resistance exercise can blunt acute use of ingested protein in some trials; this is recovery strategy trade space, not medical advice.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "disuse-deloads-return": {
        "kind": "curve",
        "title": "Training break and protein (schematic)",
        "subtitle": "Disuse vs return-to-play",
        "alt": "Curve showing higher protein need during immobilization and return phases.",
        "caption": "Schematic only: during disuse, maintaining protein intake helps limit lean-mass loss in research settings; return-to-play still requires progressive loading.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "sleep-and-overnight-recovery": {
        "kind": "timeline",
        "title": "Sleep as recovery block (schematic)",
        "subtitle": "Protein is not a hypnotic",
        "alt": "Night timeline with sleep duration and optional evening protein.",
        "caption": "Illustrative: sleep supports recovery processes; evening protein in studies targets amino acid availability, not treatment of sleep disorders.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "female-athletes": {
        "kind": "band",
        "title": "Reported protein bands in female athletes (schematic)",
        "subtitle": "Mercer 2020 review — illustrative range",
        "alt": "Band chart showing illustrative daily protein grams per kilogram for female athletes.",
        "caption": "Schematic range only: reviews cite roughly 1.3–2.2 g/kg/day depending on method and sport; individual fueling still needs food logs and clinical referral when REDs is suspected.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "menstrual-cycle-protein": {
        "kind": "cycle",
        "title": "Cycle phases on a calendar (schematic)",
        "subtitle": "No proven large protein swing",
        "alt": "Circular calendar diagram of menstrual cycle phases without human figures.",
        "caption": "Illustrative calendar only: luteal phase can shift appetite and energy; evidence for large protein requirement changes across the cycle remains limited.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "masters-athletes": {
        "kind": "meals",
        "title": "Larger meals for smaller appetites (schematic)",
        "subtitle": "Masters — hit daily total",
        "alt": "Chart showing fewer meals with higher protein per meal for masters athletes.",
        "caption": "Schematic habit: older athletes often need deliberate meal size to reach the same g/kg target; this is not a disease treatment claim.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "youth-adolescent-athletes": {
        "kind": "growth",
        "title": "Growth plus training demand (schematic)",
        "subtitle": "Youth — food-first emphasis",
        "alt": "Bar chart comparing growth and training protein needs schematically.",
        "caption": "Illustrative only: adolescents need adequate protein for growth and sport; powders are secondary to meals unless a clinician or sports RD directs otherwise.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "weight-class-sports": {
        "kind": "contrast",
        "title": "Cut week energy vs protein (schematic)",
        "subtitle": "Making weight — deficit context",
        "alt": "Diagram contrasting energy deficit with protein target elevation.",
        "caption": "Schematic only: weight-class cuts raise relative protein needs in many protocols; unsafe dehydration or extreme restriction is out of scope and not endorsed.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "team-sport-match-week": {
        "kind": "timeline",
        "title": "Match-week protein (schematic)",
        "subtitle": "UEFA-style fueling pattern",
        "alt": "Weekly timeline with match day and elevated protein on heavy days.",
        "caption": "Illustrative week: team sports benefit from adequate daily protein across microcycles; match-day shakes do not replace carbohydrates and sleep.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "aesthetic-power-to-weight": {
        "kind": "band",
        "title": "Power-to-weight fueling band (schematic)",
        "subtitle": "Aesthetic sport — deficit risk",
        "alt": "Band chart of protein intake versus energy availability risk zone.",
        "caption": "Schematic only: low energy availability undermines training adaptation; protein targets do not license chronic under-fueling.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "whey-casein-milk": {
        "kind": "photo_note",
        "title": "Dairy protein sources",
        "subtitle": "PD photograph — see RIGHTS.md",
        "alt": "Bowl of milk photographed on a neutral background.",
        "caption": "Photograph for context: milk, whey, and casein differ in digestion speed; dairy allergy and preference still dictate food choice.",
        "credit": "See figure credit in RIGHTS.md.",
        "status": "cleared-pd",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/8/80/Bowl_milk_glass.jpg",
        "rights_extra": "source_url | https://commons.wikimedia.org/wiki/File:Bowl_milk_glass.jpg\nlicense | CC BY-SA 3.0\ncredit_line | Photo: Manfred Heyde. Wikimedia Commons. CC BY-SA 3.0.",
    },
    "plant-proteins-hypertrophy": {
        "kind": "bars",
        "title": "Matched total protein: plant vs animal trials (schematic)",
        "subtitle": "Hevia-Larraín 2021; Pinckaers reviews",
        "alt": "Bar chart showing similar hypertrophy when total protein is matched between plant and animal groups in trials.",
        "caption": "Schematic summary only: when total protein and leucine are matched, many trials show similar training adaptations; food pattern still matters for adherence.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "soy-in-the-2020s": {
        "kind": "photo_note",
        "title": "Soy foods",
        "subtitle": "PD photograph — see RIGHTS.md",
        "alt": "Edamame soybeans in a bowl.",
        "caption": "Photograph for context: soy provides complete plant protein in many forms; athletic use is a food-choice question, not a hormone treatment claim.",
        "credit": "See figure credit in RIGHTS.md.",
        "status": "cleared-pd",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/2/28/Edamame.jpg",
        "rights_extra": "source_url | https://commons.wikimedia.org/wiki/File:Edamame.jpg\nlicense | CC BY-SA 3.0\ncredit_line | Photo: Yutah123. Wikimedia Commons. CC BY-SA 3.0.",
    },
    "potato-pea-fava-wheat": {
        "kind": "bars",
        "title": "Illustrative leucine content by isolate (schematic)",
        "subtitle": "Pinckaers 2021 — isolate context only",
        "alt": "Bar chart of illustrative leucine percentage for potato, pea, corn, and wheat protein isolates.",
        "caption": "Schematic only: isolate leucine percentages do not describe whole potatoes or popcorn; match dose and total daily protein to the food actually eaten.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "mycoprotein": {
        "kind": "plate",
        "title": "Mycoprotein as a food matrix (schematic)",
        "subtitle": "Dunlop 2017; Exeter biopsy work",
        "alt": "Icon diagram of fungal biomass food piece beside amino acid uptake arrow.",
        "caption": "Illustrative: mycoprotein trials show bioavailable amino acids and insulin responses; long hypertrophy trials in trained athletes remain limited.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "collagen-vs-whey": {
        "kind": "split",
        "title": "Collagen vs whey amino profile (schematic)",
        "subtitle": "Connective tissue vs muscle protein",
        "alt": "Diagram contrasting collagen peptide profile with whey essential amino acids.",
        "caption": "Schematic only: collagen is low in leucine relative to whey; connective-tissue studies do not replace resistance training for hypertrophy outcomes.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "insect-protein": {
        "kind": "photo_note",
        "title": "Insect protein ingredients",
        "subtitle": "PD photograph — see RIGHTS.md",
        "alt": "Dried mealworms used as food ingredient.",
        "caption": "Photograph for context: insect meals can be protein-dense; allergen risk, regulation, and athlete acceptance vary by region.",
        "credit": "See figure credit in RIGHTS.md.",
        "status": "cleared-pd",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Mealworms_as_food-2389.jpg",
        "rights_extra": "source_url | https://commons.wikimedia.org/wiki/File:Mealworms_as_food-2389.jpg\nlicense | CC BY-SA 4.0\ncredit_line | Wikimedia Commons contributor. CC BY-SA 4.0.",
    },
    "future-proteins-fermentation": {
        "kind": "flow",
        "title": "Precision fermentation route (schematic)",
        "subtitle": "Future proteins — not on-shelf promises",
        "alt": "Flow diagram from fermentation tank to purified protein ingredient.",
        "caption": "Illustrative process only: fermented and cellular ingredients are emerging; sports claims require the same evidence bar as established proteins.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "energy-deficit": {
        "kind": "contrast",
        "title": "Deficit raises relative protein need (schematic)",
        "subtitle": "Gwin and related deficit work",
        "alt": "Diagram showing lower calories with higher protein fraction target.",
        "caption": "Schematic only: energy deficit increases risk of lean-mass loss; higher protein may help retention in trials when training continues — not a license for extreme cuts.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "energy-availability-reds": {
        "kind": "band",
        "title": "Energy availability zones (schematic)",
        "subtitle": "IOC REDs 2023 — educational",
        "alt": "Band chart of low, moderate, and adequate energy availability without human figures.",
        "caption": "Illustrative zones only: low energy availability harms performance and health; refer athletes with suspected REDs to qualified clinicians.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "travel-camps-hotels": {
        "kind": "timeline",
        "title": "Travel day eating (schematic)",
        "subtitle": "Hotels and camps",
        "alt": "Timeline of flights and meals with protein opportunities marked.",
        "caption": "Schematic habit map: travel disrupts meal timing; shelf-stable protein helps hit daily totals — not a disease claim.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "heat-humidity": {
        "kind": "contrast",
        "title": "Heat stress and appetite (schematic)",
        "subtitle": "Hydration plus protein",
        "alt": "Diagram of heat stress lowering appetite with note to protect protein intake.",
        "caption": "Illustrative only: heat can reduce appetite; maintaining protein and fluid supports training in hot environments within medical guidance.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "altitude-hypoxia": {
        "kind": "curve",
        "title": "Altitude and protein turnover (schematic)",
        "subtitle": "Hypoxic environments — limited sports trials",
        "alt": "Curve showing increased protein turnover at altitude schematically.",
        "caption": "Schematic only: hypoxia can raise protein turnover in some data; field protocols should follow sport-science staff and medical oversight.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "tactical-occupational": {
        "kind": "timeline",
        "title": "Operational day fueling (schematic)",
        "subtitle": "Tactical athletes — load plus sleep",
        "alt": "24-hour timeline with work blocks and protein-containing meals.",
        "caption": "Illustrative schedule: occupational loads resemble sport; protein supports recovery from exertion, not treatment of injury or PTSD.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "time-restricted-ramadan": {
        "kind": "timeline",
        "title": "Compressed eating window (schematic)",
        "subtitle": "Ramadan / TRF context",
        "alt": "Timeline showing night eating window with protein at iftar and suhoor.",
        "caption": "Schematic only: compressed windows require planning to hit protein totals; religious practice decisions stay with the athlete and their advisors.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "food-first-vs-supplements": {
        "kind": "plate",
        "title": "Food-first hierarchy (schematic)",
        "subtitle": "Supplements as gap-fillers",
        "alt": "Pyramid diagram with meals at base and supplements at top.",
        "caption": "Illustrative hierarchy: meals carry the diet; supplements address gaps, travel, or measured deficiency — not disease treatment.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "contamination-batch-testing": {
        "kind": "checklist",
        "title": "Third-party testing marks (schematic)",
        "subtitle": "NSF, Informed Sport — educational",
        "alt": "Checklist graphic for batch-tested supplement labels.",
        "caption": "Schematic only: third-party testing reduces some contamination risk; it does not replace food-first fueling or medical care.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "label-literacy-spiking": {
        "kind": "checklist",
        "title": "Label red flags (schematic)",
        "subtitle": "Amino spiking awareness",
        "alt": "Label diagram highlighting protein source and amino acid listing.",
        "caption": "Illustrative label reading: verify protein source and grams per serving; proprietary blends are not evidence of efficacy.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "protein-plus-carbohydrate": {
        "kind": "split",
        "title": "Protein with carbohydrate after hard work (schematic)",
        "subtitle": "Glycogen plus repair",
        "alt": "Diagram showing combined carbohydrate and protein after glycogen-depleting session.",
        "caption": "Schematic only: adding carbohydrate supports glycogen repletion; protein supports repair — together they address different limits after hard sessions.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "high-intakes-trained-adults": {
        "kind": "curve",
        "title": "Very high protein intakes (schematic)",
        "subtitle": ">3 g/kg in short trials — not default advice",
        "alt": "Curve flattening at very high daily protein intakes.",
        "caption": "Illustrative ceiling: intakes above roughly 2.2–3 g/kg/day show diminishing average benefit in many trained adults unless deficit or special context applies.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "consensus-statements": {
        "kind": "timeline",
        "title": "Consensus documents timeline (schematic)",
        "subtitle": "ISSN, UEFA, IOC — pointers only",
        "alt": "Timeline from 2017 ISSN through 2023 IOC REDs statement.",
        "caption": "Schematic timeline only: position papers summarize evidence bands; they are not personal prescriptions.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "omega-3-and-protein": {
        "kind": "split",
        "title": "Omega-3 and protein recovery (schematic)",
        "subtitle": "Adjacent, not interchangeable",
        "alt": "Diagram placing omega-3 fatty acids beside protein as separate recovery factors.",
        "caption": "Illustrative only: omega-3 trials examine inflammation and recovery markers; they do not replace adequate protein or medical injury care.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
    "open-questions-2026": {
        "kind": "flow",
        "title": "Open questions map (schematic)",
        "subtitle": "2026 research gaps",
        "alt": "Mind-map style diagram listing open protein research topics without human icons.",
        "caption": "Schematic map only: lists active unknowns — ultra-processed matrices, female-specific dose trials, and long plant-only hypertrophy studies — not answered by one figure.",
        "credit": "Original schematic. CC0 1.0.",
        "status": "original-svg",
    },
}


def svg_header(title: str, subtitle: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="figTitle figDesc">
  <title id="figTitle">{title}</title>
  <desc id="figDesc">{subtitle}</desc>
  <rect width="{W}" height="{H}" fill="#f7f5f0"/>
  <rect x="0" y="0" width="{W}" height="56" fill="#2d4a3e"/>
  <text x="20" y="34" font-family="{FONT}" font-size="16" fill="#f7f5f0" font-weight="600">{title}</text>
  <text x="20" y="78" font-family="{FONT}" font-size="12" fill="#5c574f">{subtitle}</text>
"""


def svg_footer() -> str:
    return f'  <text x="20" y="{H - 16}" font-family="{FONT}" font-size="11" fill="#8a8278">Illustrative schematic — not primary data. CC0 1.0.</text>\n</svg>\n'


def render_curve() -> str:
    return (
        svg_header("Daily protein vs response (schematic)", "Illustrative — Morton / Tagawa inspired")
        + f"""  <line x1="80" y1="320" x2="580" y2="320" stroke="#8a8278" stroke-width="1.5"/>
  <line x1="80" y1="100" x2="80" y2="320" stroke="#8a8278" stroke-width="1.5"/>
  <text x="300" y="350" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#4a4540">g protein / kg body mass / day</text>
  <text x="48" y="210" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#4a4540" transform="rotate(-90 48 210)">response (arb.)</text>
  <path d="M 80 300 C 180 180, 320 150, 580 140" fill="none" stroke="#3d6b5a" stroke-width="3"/>
  <line x1="340" y1="100" x2="340" y2="320" stroke="#c45c3e" stroke-width="1" stroke-dasharray="4 4"/>
  <text x="348" y="115" font-family="{FONT}" font-size="11" fill="#c45c3e">~1.6 g/kg (illustrative)</text>
"""
        + svg_footer()
    )


def render_mps_bars() -> str:
    return (
        svg_header("MPS after feeding (schematic)", "25 g vs 100 g — Trommelen 2023 inspired")
        + f"""  <rect x="160" y="180" width="80" height="120" fill="#8fb9a8"/>
  <rect x="360" y="120" width="80" height="180" fill="#3d6b5a"/>
  <text x="200" y="170" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#4a4540">25 g</text>
  <text x="400" y="110" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#4a4540">100 g</text>
  <text x="320" y="340" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#4a4540">12 h integrated MPS (schematic)</text>
"""
        + svg_footer()
    )


def render_meals() -> str:
    bars = [(120, 90), (220, 70), (320, 80), (420, 100)]
    body = ""
    for i, (x, h) in enumerate(bars):
        body += f'  <rect x="{x}" y="{300 - h}" width="60" height="{h}" fill="#3d6b5a" opacity="0.85"/>\n'
        body += f'  <text x="{x + 30}" y="320" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Meal {i + 1}</text>\n'
    return svg_header("Daily protein spread (schematic)", "Distribution habit") + body + svg_footer()


def render_bars() -> str:
    items = [("Milk", 0.9), ("Egg", 0.88), ("Soy", 0.75), ("Wheat", 0.45)]
    body = ""
    for i, (label, frac) in enumerate(items):
        x = 100 + i * 120
        h = int(frac * 180)
        body += f'  <rect x="{x}" y="{300 - h}" width="70" height="{h}" fill="#3d6b5a"/>\n'
        body += f'  <text x="{x + 35}" y="320" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">{label}</text>\n'
    return svg_header("Quality ranks (schematic)", "Illustrative DIAAS-style") + body + svg_footer()


def render_timeline() -> str:
    return (
        svg_header("Day timeline (schematic)", "Training-centered")
        + f"""  <line x1="60" y1="220" x2="580" y2="220" stroke="#8a8278" stroke-width="2"/>
  <rect x="240" y="200" width="120" height="40" fill="#c45c3e" opacity="0.85"/>
  <text x="300" y="225" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#fff">Session</text>
  <circle cx="120" cy="220" r="10" fill="#3d6b5a"/>
  <circle cx="480" cy="220" r="10" fill="#3d6b5a"/>
  <text x="120" y="250" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Protein meal</text>
  <text x="480" y="250" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Protein meal</text>
"""
        + svg_footer()
    )


def render_split() -> str:
    return (
        svg_header("Two routes (schematic)", "Compare options")
        + f"""  <rect x="80" y="140" width="200" height="140" fill="#e8e2d6" stroke="#3d6b5a" stroke-width="2"/>
  <rect x="360" y="140" width="200" height="140" fill="#d6e8df" stroke="#3d6b5a" stroke-width="2"/>
  <text x="180" y="210" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#4a4540">Whole food</text>
  <text x="460" y="210" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#4a4540">Isolated / blend</text>
"""
        + svg_footer()
    )


def render_plate() -> str:
    return (
        svg_header("Meal vs powder (schematic)", "Matrix context")
        + f"""  <ellipse cx="200" cy="220" rx="90" ry="60" fill="#e8e2d6" stroke="#3d6b5a" stroke-width="2"/>
  <text x="200" y="225" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#4a4540">Mixed meal</text>
  <rect x="400" y="180" width="80" height="80" fill="#d6e8df" stroke="#3d6b5a" stroke-width="2"/>
  <text x="440" y="225" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Powder</text>
"""
        + svg_footer()
    )


def render_stack() -> str:
    return (
        svg_header("Drivers of adaptation (schematic)", "Training first")
        + f"""  <rect x="220" y="120" width="200" height="50" fill="#c45c3e"/>
  <text x="320" y="150" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#fff">Resistance training</text>
  <rect x="220" y="190" width="200" height="50" fill="#3d6b5a"/>
  <text x="320" y="220" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#fff">Adequate protein</text>
  <rect x="220" y="260" width="200" height="50" fill="#8fb9a8"/>
  <text x="320" y="290" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#2d4a3e">Energy + sleep</text>
"""
        + svg_footer()
    )


def render_contrast() -> str:
    return (
        svg_header("Competing demands (schematic)", "Context")
        + f"""  <rect x="80" y="150" width="180" height="120" fill="#f0d4c4"/>
  <text x="170" y="215" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#4a4540">Stress A</text>
  <rect x="380" y="150" width="180" height="120" fill="#d6e8df"/>
  <text x="470" y="215" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#4a4540">Nutrition target</text>
"""
        + svg_footer()
    )


def render_band() -> str:
    return (
        svg_header("Target band (schematic)", "Illustrative g/kg range")
        + f"""  <rect x="100" y="180" width="440" height="60" fill="#d6e8df" stroke="#3d6b5a" stroke-width="2"/>
  <text x="320" y="215" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#2d4a3e">Illustrative adequate band</text>
  <rect x="100" y="260" width="200" height="30" fill="#f0d4c4"/>
  <text x="200" y="280" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Risk zone (low EA)</text>
"""
        + svg_footer()
    )


def render_cycle() -> str:
    return (
        svg_header("Cycle calendar (schematic)", "No human figures")
        + f"""  <circle cx="320" cy="220" r="100" fill="none" stroke="#3d6b5a" stroke-width="3"/>
  <text x="320" y="130" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Follicular</text>
  <text x="430" y="225" font-family="{FONT}" font-size="11" fill="#4a4540">Ovulatory</text>
  <text x="320" y="330" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Luteal</text>
"""
        + svg_footer()
    )


def render_growth() -> str:
    return (
        svg_header("Demand stack (schematic)", "Growth + sport")
        + f"""  <rect x="180" y="140" width="120" height="160" fill="#8fb9a8"/>
  <rect x="320" y="180" width="120" height="120" fill="#3d6b5a"/>
  <text x="240" y="230" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#2d4a3e">Growth</text>
  <text x="380" y="230" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#fff">Training</text>
"""
        + svg_footer()
    )


def render_flow() -> str:
    return (
        svg_header("Process map (schematic)", "Ingredient route")
        + f"""  <rect x="60" y="200" width="100" height="50" fill="#e8e2d6" stroke="#3d6b5a"/>
  <text x="110" y="230" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Feedstock</text>
  <path d="M 160 225 L 220 225" stroke="#3d6b5a" marker-end="url(#arrow)"/>
  <rect x="220" y="200" width="100" height="50" fill="#d6e8df" stroke="#3d6b5a"/>
  <text x="270" y="230" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#4a4540">Ferment</text>
  <path d="M 320 225 L 380 225" stroke="#3d6b5a"/>
  <rect x="380" y="200" width="120" height="50" fill="#8fb9a8" stroke="#3d6b5a"/>
  <text x="440" y="230" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#2d4a3e">Protein ingredient</text>
  <defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#3d6b5a"/></marker></defs>
"""
        + svg_footer()
    )


def render_checklist() -> str:
    items = ["Protein source named", "Grams per serving", "Third-party mark", "No proprietary-only blend"]
    body = ""
    for i, item in enumerate(items):
        y = 140 + i * 40
        body += f'  <rect x="120" y="{y}" width="20" height="20" fill="#fff" stroke="#3d6b5a"/>\n'
        body += f'  <text x="155" y="{y + 15}" font-family="{FONT}" font-size="13" fill="#4a4540">{item}</text>\n'
    return svg_header("Label checks (schematic)", "Educational") + body + svg_footer()


KIND_RENDER = {
    "curve": render_curve,
    "mps_bars": render_mps_bars,
    "meals": render_meals,
    "bars": render_bars,
    "timeline": render_timeline,
    "split": render_split,
    "plate": render_plate,
    "stack": render_stack,
    "contrast": render_contrast,
    "band": render_band,
    "cycle": render_cycle,
    "growth": render_growth,
    "flow": render_flow,
    "checklist": render_checklist,
}


def rights_md(slug: str, spec: dict[str, str], filename: str) -> str:
    status = spec["status"]
    if status == "cleared-pd":
        extra_rows = []
        for line in spec.get("rights_extra", "").splitlines():
            if "|" in line:
                k, v = line.split("|", 1)
                extra_rows.append(f"| {k.strip()} | {v.strip()} |")
        extra_block = "\n".join(extra_rows)
        return textwrap.dedent(
            f"""# Rights — {slug} figure

| Field | Value |
|-------|-------|
| slug | {slug} |
| status | cleared-pd |
| file | {filename} |
| ai_generated | no |
| ingested | 2026-09-14 |
{extra_block}
"""
        )
    return textwrap.dedent(
        f"""# Rights — {slug} figure

| Field | Value |
|-------|-------|
| slug | {slug} |
| status | original-svg |
| file | {filename} |
| ai_generated | no |
| created | 2026-09-14 |
| license | CC0 1.0 |
| credit_line | Original schematic for sports-nutrition-rd-2020 editorial draft. CC0 1.0. |
| notes | Illustrative only — not reproduced from copyrighted journal figures. |
"""
    )


def download(url: str, dest: Path) -> None:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "COSMOS-content-ingest/1.0 (editorial)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())


def main() -> None:
    for slug, spec in SPECS.items():
        dest = FIG / slug
        dest.mkdir(parents=True, exist_ok=True)
        if spec["status"] == "cleared-pd" and spec.get("photo_url"):
            jpg = dest / "figure.jpg"
            if not jpg.is_file():
                download(spec["photo_url"], jpg)
            (dest / "RIGHTS.md").write_text(rights_md(slug, spec, "figure.jpg"), encoding="utf-8")
            continue
        kind = spec.get("kind", "curve")
        if kind == "photo_note":
            # fallback to plate if photo missing
            kind = "plate"
        render = KIND_RENDER.get(kind, render_curve)
        svg = render()
        (dest / "figure.svg").write_text(svg, encoding="utf-8")
        (dest / "RIGHTS.md").write_text(rights_md(slug, spec, "figure.svg"), encoding="utf-8")
    print(f"Wrote {len(SPECS)} figure folders under {FIG}")


if __name__ == "__main__":
    main()
