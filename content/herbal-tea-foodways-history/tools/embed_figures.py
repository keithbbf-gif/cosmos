#!/usr/bin/env python3
"""Insert lead figures and SEO frontmatter for herbal-tea-foodways-history drafts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "assets" / "images" / "_download_meta.json"
IMAGE_PASS = "2026-09-14"
FIGURE_MARKER = "<!-- htf-figure:v1 -->"
FIGURE_CLASS = 'class="htf-figure"'

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_BLOCK_RE = re.compile(
    r"\n<!-- htf-figure:v1 -->.*?</figure>\n",
    re.S,
)

# essay id -> figure spec
ASSIGN: dict[str, dict[str, str | int]] = {
    "01": {
        "figure_id": "svg.foodways-scope-fence",
        "src": "../assets/svg/foodways-scope-fence.svg",
        "w": 880,
        "h": 520,
        "alt": "Schematic of allowed foodways topics versus blocked medical-claim graphics",
        "caption": "The series fence is drawn before the first plant — kitchen, market, and garden rooms only, not disease-payoff art.",
        "meta": "What the herbal tea foodways history folder refuses: educational cups and trade names, not medical advice or cure graphics.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
    "02": {
        "figure_id": "svg.camellia-vs-herbal-bins",
        "src": "../assets/svg/camellia-vs-herbal-bins.svg",
        "w": 880,
        "h": 520,
        "alt": "Diagram of Camellia sinensis bin separate from herbal tisane bin in a grocery aisle",
        "caption": "Tisane is not tea in the botanical sense — the aisle sorts Camellia from everything else the tin calls herbal.",
        "meta": "Why tisane is not tea: Camellia sinensis versus the English herbal tea grocery category, explained as foodways history.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
    "03": {
        "figure_id": "plates.liotard_tea_set_still_life",
        "src": "../assets/images/historic/liotard-tea-set-still-life.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Eighteenth-century still life painting of a porcelain tea set on a table",
        "caption": "Foodways live at the table — a domestic tea set still life, not a materia medica plate hunting an indication.",
        "meta": "Foodways not materia medica: household cups and hospitality hours versus clinical herb marketing.",
        "rights": "plates.liotard_tea_set_still_life",
    },
    "04": {
        "figure_id": "plates.household_tea_still_life_roestraten",
        "src": "../assets/images/historic/household-tea-still-life-roestraten.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Dutch still life with porcelain tea cups and table objects",
        "caption": "A household receipt belongs to the same room as this table — instructions for a kitchen, not proof of a modern finding.",
        "meta": "How to read a household receipt for herbal drinks: kitchen instructions and social context, not disease claims.",
        "rights": "plates.household_tea_still_life_roestraten",
    },
    "05": {
        "figure_id": "svg.ptisan-tisane-timeline",
        "src": "../assets/svg/ptisan-tisane-timeline.svg",
        "w": 880,
        "h": 520,
        "alt": "Timeline from barley ptisan through French tisane to English herbal tea category",
        "caption": "Ptisan begins as barley water; tisane widens in French dictionaries long before the English tin says HERBAL TEA.",
        "meta": "From ptisan to tisane: barley sickroom register, French widening, and the grocery herbal tea aisle as word history.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
    "06": {
        "figure_id": "plates.camellia_sinensis_kohler",
        "src": "../assets/images/botanical/camellia-sinensis-kohler.jpg",
        "w": 900,
        "h": 1200,
        "alt": "Historical botanical plate of Camellia sinensis tea plant",
        "caption": "A Hamburg letterhead that still splits THIE from other infusions is arguing with this leaf — Camellia as the marked default.",
        "meta": "THIE trade categories and the two bins: Camellia sinensis separated from other infusions in commerce and language.",
        "rights": "plates.camellia_sinensis_kohler",
    },
    "07": {
        "figure_id": "plates.tea_bags_envelope",
        "src": "../assets/images/aisle/tea-bags-envelope.jpg",
        "w": 1200,
        "h": 800,
        "alt": "Assorted tea bags in paper envelopes on a neutral surface",
        "caption": "The tea bag taught other leaves to ride in the same envelope — hardware before botanical honesty.",
        "meta": "Tea bags, tins, and the grocery aisle: how packaging taught herbal infusions to look like Camellia tea.",
        "rights": "plates.tea_bags_envelope",
    },
    "08": {
        "figure_id": "plates.camellia_sinensis_kohler",
        "src": "../assets/images/botanical/camellia-sinensis-kohler.jpg",
        "w": 900,
        "h": 1200,
        "alt": "Camellia sinensis botanical illustration from Köhler's Medizinal-Pflanzen",
        "caption": "Camellia stays the unmarked default; herbal is the adjective that knows it stands beside something.",
        "meta": "Camellia sinensis as the unmarked tea default and herbal as the marked grocery adjective beside it.",
        "rights": "plates.camellia_sinensis_kohler",
    },
    "09": {
        "figure_id": "plates.liotard_tea_set_still_life",
        "src": "../assets/images/historic/liotard-tea-set-still-life.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Still life of porcelain tea cups and service on a table",
        "caption": "Infusion, decoction, and sun tea are labor in a kitchen — method as history, not a virtue chart.",
        "meta": "Infusion, decoction, and sun tea as kitchen methods and social choices in herbal drink foodways.",
        "rights": "plates.liotard_tea_set_still_life",
    },
    "10": {
        "figure_id": "plates.mate_gourd_bombilla",
        "src": "../assets/images/vessels/mate-gourd-bombilla.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Calabash mate gourd with metal bombilla straw",
        "caption": "Cup, pot, and strainer assign status — a gourd and bombilla are the social hardware of a drink.",
        "meta": "Tea cups, pots, and strainers as foodways hardware that assign hour, status, and hospitality.",
        "rights": "plates.mate_gourd_bombilla",
    },
    "11": {
        "figure_id": "plates.hibiscus_sabdariffa_calyces",
        "src": "../assets/images/food/hibiscus-sabdariffa-calyces.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Fresh Hibiscus sabdariffa calyces on the plant",
        "caption": "Bissap, zobo, and sobolo share a calyx — street names before the English aisle says hibiscus tea.",
        "meta": "Bissap, zobo, and sobolo: West African roselle drinks as street and table foodways, not one brand name.",
        "rights": "plates.hibiscus_sabdariffa_calyces",
    },
    "12": {
        "figure_id": "svg.hibiscus-atlantic-belt-map",
        "src": "../assets/svg/hibiscus-atlantic-belt-map.svg",
        "w": 880,
        "h": 520,
        "alt": "Schematic map of West African and Caribbean roselle drink regions",
        "caption": "Christmas sorrel and Dakar street red share a plant — the map is names and hours, not a single origin myth.",
        "meta": "Caribbean Christmas sorrel and the Atlantic hibiscus belt: holiday red drink foodways beyond hibiscus tea labels.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
    "13": {
        "figure_id": "plates.dried_hibiscus_calyces",
        "src": "../assets/images/food/dried-hibiscus-calyces.jpg",
        "w": 1200,
        "h": 800,
        "alt": "Dried red hibiscus calyces for brewing agua fresca",
        "caption": "Agua de jamaica is the same calyx as a cooler drink — Mexico's glass, not Christmas-only packaging.",
        "meta": "Agua de jamaica as Mexican agua fresca foodways distinct from diaspora Christmas sorrel alone.",
        "rights": "plates.dried_hibiscus_calyces",
    },
    "14": {
        "figure_id": "plates.dried_hibiscus_calyces",
        "src": "../assets/images/food/dried-hibiscus-calyces.jpg",
        "w": 1200,
        "h": 800,
        "alt": "Dried hibiscus calyces ready to brew a tart red drink",
        "caption": "Karkadeh in the cafe is a street glass and a sugar argument — tourist nicknames flagged, plant unchanged.",
        "meta": "Karkadeh cafe culture in Cairo and Sudanese street glasses: roselle hospitality without wellness copy.",
        "rights": "plates.dried_hibiscus_calyces",
    },
    "15": {
        "figure_id": "plates.rooibos_plant",
        "src": "../assets/images/botanical/rooibos-plant.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Rooibos Aspalathus linearis plant in South African landscape",
        "caption": "Rooibos carries a Cederberg cup and a thin early paper trail — 1904 is a market story, not an invention day.",
        "meta": "Rooibos and the Cederberg cup: Aspalathus linearis trade history without invented origin dates.",
        "rights": "plates.rooibos_plant",
    },
    "16": {
        "figure_id": "plates.honeybush_cyclopia_plate",
        "src": "../assets/images/botanical/honeybush-cyclopia-plate.png",
        "w": 800,
        "h": 1000,
        "alt": "Historical botanical plate of Cyclopia honeybush",
        "caption": "Honeybush is the quieter Cape sibling — Cyclopia without rooibos's export megaphone.",
        "meta": "Honeybush Cyclopia foodways beside rooibos: Cape infusions and export asymmetry.",
        "rights": "plates.honeybush_cyclopia_plate",
    },
    "17": {
        "figure_id": "plates.dried_hibiscus_calyces",
        "src": "../assets/images/food/dried-hibiscus-calyces.jpg",
        "w": 1200,
        "h": 800,
        "alt": "Dried calyces for Sahelian hospitality drinks",
        "caption": "Kinkeliba's English trail is thinner — the guest pot still matters even when the archive is quiet.",
        "meta": "Kinkeliba as Sahelian hospitality drink with a thin colonial paper trail kept at the guest pot.",
        "rights": "plates.dried_hibiscus_calyces",
    },
    "18": {
        "figure_id": "plates.mint_spearmint_kohler",
        "src": "../assets/images/botanical/mint-spearmint-kohler.jpg",
        "w": 900,
        "h": 1200,
        "alt": "Spearmint Mentha botanical plate from Köhler's Medizinal-Pflanzen",
        "caption": "Chiba in the mint pot is local herbs teaching imported leaf how to sit — a Maghrebi foodway, not a single species.",
        "meta": "Maghrebi mint pot foodways: local herbs and imported tea leaves as paired hospitality.",
        "rights": "plates.mint_spearmint_kohler",
    },
    "19": {
        "figure_id": "plates.chamomile_field",
        "src": "../assets/images/garden/chamomile-field.jpg",
        "w": 1200,
        "h": 800,
        "alt": "Wild chamomile and poppies at the edge of a barley field",
        "caption": "Monastery gardens and stillrooms are production rooms — plants in rows, not a medical myth panel.",
        "meta": "Monastery garden and stillroom herb production as European foodways, not miracle cure folklore.",
        "rights": "plates.chamomile_field",
    },
    "20": {
        "figure_id": "plates.linden_tilia_inflorescence",
        "src": "../assets/images/botanical/linden-tilia-inflorescence.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Linden Tilia cordata flowers on a branch",
        "caption": "Tilleul marks a French domestic hour — linden as kitchen time, not a sleep protocol.",
        "meta": "Tilleul linden flower cup as French domestic hour and foodways, not bedtime medical marketing.",
        "rights": "plates.linden_tilia_inflorescence",
    },
    "21": {
        "figure_id": "plates.chamomile_flowers",
        "src": "../assets/images/botanical/chamomile-flowers.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Chamomile Matricaria flower heads close view",
        "caption": "Chamomile sits in cottage and cafe as a grocery category — a cup, not a bedtime indication chart.",
        "meta": "Chamomile as European cottage and cafe drink category without wellness bedtime claims.",
        "rights": "plates.chamomile_flowers",
    },
    "22": {
        "figure_id": "plates.elderflower_sambucus",
        "src": "../assets/images/botanical/elderflower-sambucus.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Elderflower Sambucus nigra botanical illustration",
        "caption": "Elderflower is a season on a calendar — short foraging weeks, not a year-round sachet virtue.",
        "meta": "Elderflower seasonality in European foraging and kitchen calendars as foodways history.",
        "rights": "plates.elderflower_sambucus",
    },
    "23": {
        "figure_id": "plates.greek_mountain_tea_sideritis",
        "src": "../assets/images/botanical/greek-mountain-tea-sideritis.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Sideritis scardica Greek mountain tea plant in botanic garden",
        "caption": "Tsai tou vounou names a mountain breakfast table — harvest pressure and local nouns, not an export slogan.",
        "meta": "Greek mountain tea Sideritis as breakfast table foodways and mountain naming, not export wellness branding.",
        "rights": "plates.greek_mountain_tea_sideritis",
    },
    "24": {
        "figure_id": "plates.fireweed_herbarium",
        "src": "../assets/images/botanical/fireweed-herbarium.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Fireweed Chamerion angustifolium herbarium specimen sheet",
        "caption": "Ivan-chai and Koporye carry a substitute story and a later fashion — fireweed on paper, not one ancestral gesture.",
        "meta": "Ivan-chai fireweed and Koporye trade: Russian substitute drinks and later fermented fashion as foodways.",
        "rights": "plates.fireweed_herbarium",
    },
    "25": {
        "figure_id": "svg.europe-herbal-cup-map",
        "src": "../assets/svg/europe-herbal-cup-map.svg",
        "w": 880,
        "h": 520,
        "alt": "Schematic map of European domestic herbal cup traditions",
        "caption": "Alpine Kräuter on the tin is landscape branding — the meadow printed larger than any one farm.",
        "meta": "Alpine Kräuter herbal tea tins as landscape branding and European grocery storytelling.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
    "26": {
        "figure_id": "plates.barley_grains",
        "src": "../assets/images/food/barley-grains.jpg",
        "w": 1200,
        "h": 800,
        "alt": "Barley grains for roasting or brewing grain tea",
        "caption": "Wartime cupboards learned to call roasted grain tea — stand-ins when the Camellia crate was dear.",
        "meta": "Wartime and blockade herbal tea substitutes: grain cups and cupboard stand-ins as foodways history.",
        "rights": "plates.barley_grains",
    },
    "27": {
        "figure_id": "plates.tea_bags_envelope",
        "src": "../assets/images/aisle/tea-bags-envelope.jpg",
        "w": 1200,
        "h": 800,
        "alt": "Herbal and tea bags in paper envelopes",
        "caption": "Temperance meetings weaponized the herbal cup against the dram shop — a social hour, not a liver chart.",
        "meta": "Temperance movement herbal tea cups as meeting-house foodways versus alcohol trade, not health claims.",
        "rights": "plates.tea_bags_envelope",
    },
    "28": {
        "figure_id": "plates.oswego_bee_balm_monarda",
        "src": "../assets/images/botanical/oswego-bee-balm-monarda.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Red Monarda didyma Oswego tea flower",
        "caption": "Oswego tea is a real plant with a patriotic caption that needs a hedge — Monarda on the table, myth on the margin.",
        "meta": "Oswego tea Monarda and Boston Tea Party folklore: real plant, contested patriotic captions.",
        "rights": "plates.oswego_bee_balm_monarda",
    },
    "29": {
        "figure_id": "svg.americas-cup-geography",
        "src": "../assets/svg/americas-cup-geography.svg",
        "w": 880,
        "h": 520,
        "alt": "Schematic Americas map of yaupon mate guayusa and Andean hierbas drinks",
        "caption": "Yaupon, white drink, black drink — a southeastern holly cup with council form, not an energy bottle.",
        "meta": "Yaupon holly white and black drink foodways in southeastern North America and council cups.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
    "30": {
        "figure_id": "plates.labrador_tea_rhododendron",
        "src": "../assets/images/botanical/labrador-tea-rhododendron.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Labrador tea Rhododendron groenlandicum plant",
        "caption": "Labrador tea on the trapline appears in other people's notebooks — northern camp drink, thin English retail.",
        "meta": "Labrador tea Rhododendron groenlandicum as northern trapline camp drink in ethnographic notebooks.",
        "rights": "plates.labrador_tea_rhododendron",
    },
    "31": {
        "figure_id": "plates.sassafras_leaves",
        "src": "../assets/images/botanical/sassafras-leaves.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Sassafras albidum leaves botanical photograph",
        "caption": "Sassafras as flavor history is a commodity taste — later a food-rule object, not a folk cure poster.",
        "meta": "Sassafras root beer flavor history and FDA safrole food rules as American foodways, not herbal treatment.",
        "rights": "plates.sassafras_leaves",
    },
    "32": {
        "figure_id": "plates.yerba_mate_kohler",
        "src": "../assets/images/botanical/yerba-mate-kohler.jpg",
        "w": 900,
        "h": 1200,
        "alt": "Ilex paraguariensis yerba mate botanical plate",
        "caption": "Yerba mate as form means gourd and bombilla — the social hardware is the drink.",
        "meta": "Yerba mate gourd and bombilla as social form foodways in the Americas, not stimulant marketing.",
        "rights": "plates.yerba_mate_kohler",
    },
    "33": {
        "figure_id": "plates.guayusa_leaves",
        "src": "../assets/images/botanical/guayusa-leaves.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Dried Ilex guayusa leaves for morning brewing",
        "caption": "Guayusa mornings are a circle in the kitchen — not an energy bottle caption.",
        "meta": "Guayusa morning circle drinks in Amazonian foodways versus modern energy drink marketing.",
        "rights": "plates.guayusa_leaves",
    },
    "34": {
        "figure_id": "plates.mint_spearmint_kohler",
        "src": "../assets/images/botanical/mint-spearmint-kohler.jpg",
        "w": 900,
        "h": 1200,
        "alt": "Mint botanical plate for Andean hierbas context",
        "caption": "Andean hierbas in the kettle are market bundles and contested leaves — table drinks, not cleanse copy.",
        "meta": "Andean hierbas kettle bundles as highland market drink foodways without detox marketing.",
        "rights": "plates.mint_spearmint_kohler",
    },
    "35": {
        "figure_id": "plates.chamomile_field",
        "src": "../assets/images/garden/chamomile-field.jpg",
        "w": 1200,
        "h": 800,
        "alt": "Chamomile growing at the edge of a grain field",
        "caption": "Shaker and Moravian herb gardens dried for trade reputation — communal lofts, not secret cures.",
        "meta": "Shaker and Moravian communal herb gardens and drying lofts as American foodways production.",
        "rights": "plates.chamomile_field",
    },
    "36": {
        "figure_id": "plates.chrysanthemum_tea_glass",
        "src": "../assets/images/food/chrysanthemum-tea-glass.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Glass of chrysanthemum tea with dried flowers",
        "caption": "Chrysanthemum as a summer glass beside sweets — cooling as culinary weather-talk, not a body chart.",
        "meta": "Chrysanthemum tea as Chinese summer glass foodways and culinary cooling language, not medical cooling claims.",
        "rights": "plates.chrysanthemum_tea_glass",
    },
    "37": {
        "figure_id": "svg.asia-cha-without-camellia",
        "src": "../assets/svg/asia-cha-without-camellia.svg",
        "w": 880,
        "h": 520,
        "alt": "Diagram of East Asian barley and flower teas without Camellia",
        "caption": "Mugicha, sobacha, and cha without Camellia — refrigerator jugs and hospitality syllables.",
        "meta": "Mugicha sobacha and Japanese cha without Camellia: barley teas as foodways drinks, not pharmacopeia.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
    "38": {
        "figure_id": "plates.boricha_barley_tea",
        "src": "../assets/images/food/boricha-barley-tea.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Korean boricha barley tea in a glass",
        "caption": "Boricha and omija at the table — restaurant default liquid and tart seasonal glass, not tonic copy.",
        "meta": "Korean boricha barley tea and omija seasonal drinks as restaurant table foodways.",
        "rights": "plates.boricha_barley_tea",
    },
    "39": {
        "figure_id": "plates.butterfly_pea_flower",
        "src": "../assets/images/botanical/butterfly-pea-flower.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Blue Clitoria ternatea butterfly pea flowers",
        "caption": "Butterfly pea and pandan trade on color and aroma — hospitality tricks in the glass, not cleanse branding.",
        "meta": "Butterfly pea and pandan color drinks as Southeast Asian hospitality foodways without detox marketing.",
        "rights": "plates.butterfly_pea_flower",
    },
    "40": {
        "figure_id": "plates.tulsi_ocimum",
        "src": "../assets/images/botanical/tulsi-ocimum.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Holy basil tulsi Ocimum tenuiflorum plant",
        "caption": "Tulsi in the courtyard is a watered pot — hospitality, not a kraft tin virtue list.",
        "meta": "Tulsi holy basil courtyard hospitality water as South Asian foodways, not supplement marketing.",
        "rights": "plates.tulsi_ocimum",
    },
    "41": {
        "figure_id": "plates.mint_spearmint_kohler",
        "src": "../assets/images/botanical/mint-spearmint-kohler.jpg",
        "w": 900,
        "h": 1200,
        "alt": "Spearmint botanical plate for Maghrebi atay context",
        "caption": "Atay is a nineteenth-century pairing of gunpowder tea and sugar — mint taught the leaf how to sit.",
        "meta": "Moroccan atay mint tea pairing as Maghrebi hospitality foodways and trade sugar history.",
        "rights": "plates.mint_spearmint_kohler",
    },
    "42": {
        "figure_id": "plates.herbal_tea_retail_pack",
        "src": "../assets/images/aisle/herbal-tea-retail-pack.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Retail pack of chrysanthemum herbal tea bags",
        "caption": "Lotus and artichoke cafe tins sell scent and story — read the label as commerce, not a cleanse.",
        "meta": "Lotus seed and artichoke cafe drink tins as scented grocery commerce without cleanse claims.",
        "rights": "plates.herbal_tea_retail_pack",
    },
    "43": {
        "figure_id": "svg.grocery-herbal-label-timeline",
        "src": "../assets/svg/grocery-herbal-label-timeline.svg",
        "w": 880,
        "h": 520,
        "alt": "Timeline from stillroom jars to modern HERBAL TEA grocery tins",
        "caption": "Journalists flatten fifty plants into one word — the missing verb is usually pour, serve, or sell.",
        "meta": "How journalists flatten herbal tea into one word: foodways critique of missing verbs and plant diversity.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
    "44": {
        "figure_id": "plates.herbal_tea_retail_pack",
        "src": "../assets/images/aisle/herbal-tea-retail-pack.jpg",
        "w": 1200,
        "h": 900,
        "alt": "Grocery pack of herbal tea showing species and brand labeling",
        "caption": "Label literacy starts with species, part, cut, and story — questions for the tin, not the pancreas.",
        "meta": "Grocery herbal tea label literacy: species, part, cut, and trade story questions for historical readers.",
        "rights": "plates.herbal_tea_retail_pack",
    },
    "45": {
        "figure_id": "svg.hibiscus-atlantic-belt-map",
        "src": "../assets/svg/hibiscus-atlantic-belt-map.svg",
        "w": 880,
        "h": 520,
        "alt": "Schematic map of roselle drink geographies for bibliography context",
        "caption": "The working bibliography lists what we opened — and the belts we still cannot close with one confident date.",
        "meta": "Working bibliography for herbal tea foodways history: sources opened, gaps, and uncertain dates.",
        "rights": "Editorial schematic; pack-owned — see RIGHTS.md.",
    },
}


def load_meta() -> dict[str, dict]:
    if not META_PATH.exists():
        return {}
    return json.loads(META_PATH.read_text(encoding="utf-8")).get("files", {})


def rights_line(spec: dict[str, str | int], meta: dict[str, dict]) -> str:
    key = str(spec.get("rights", ""))
    if key.startswith("Editorial"):
        return key
    # map figure_id plates.foo to path
    rel = str(spec["src"]).replace("../assets/images/", "")
    info = meta.get(rel, {})
    lic = info.get("license", "See Commons (recheck before import)")
    page = info.get("commons_page", "RIGHTS.md")
    return f"{lic}; see <a href=\"{page}\">Commons</a> and RIGHTS.md."


def figure_html(spec: dict[str, str | int], meta: dict[str, dict]) -> str:
    rights = rights_line(spec, meta)
    return (
        f"\n{FIGURE_MARKER}\n"
        f"<figure {FIGURE_CLASS}>\n"
        f'  <img src="{spec["src"]}" alt="{spec["alt"]}" '
        f'width="{spec["w"]}" height="{spec["h"]}" loading="lazy" decoding="async"/>\n'
        f"  <figcaption><strong>Fig. 1.</strong> {spec['caption']} "
        f"<em>Rights:</em> {rights}</figcaption>\n"
        f"</figure>\n"
    )


def upsert_frontmatter(fm: str, spec: dict[str, str | int]) -> str:
    lines = fm.splitlines()
    keep = [ln for ln in lines if not ln.startswith(
        ("figure_id:", "image_rights:", "meta_description:", "image_pass:", "hero_figure:")
    )]
    keep.extend(
        [
            f'figure_id: {spec["figure_id"]}',
            "image_rights: documented",
            f'meta_description: "{spec["meta"]}"',
            f"image_pass: {IMAGE_PASS}",
            f'hero_figure: {spec["figure_id"]}',
        ]
    )
    return "\n".join(keep) + "\n"


def main() -> int:
    meta = load_meta()
    paths = sorted(ROOT.glob("stage-*/[0-9][0-9]-*.md"))
    missing: list[str] = []
    for path in paths:
        m = FM_RE.match(path.read_text(encoding="utf-8"))
        if not m:
            print(f"skip {path}: no frontmatter")
            continue
        essay_id = None
        for line in m.group(1).splitlines():
            if line.startswith("id:"):
                essay_id = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
        if not essay_id or essay_id not in ASSIGN:
            missing.append(path.name)
            continue
        spec = ASSIGN[essay_id]
        body = path.read_text(encoding="utf-8")[m.end() :]
        body = FIGURE_BLOCK_RE.sub("\n", body)
        new_fm = upsert_frontmatter(m.group(1), spec)
        new_text = f"---\n{new_fm}---\n{figure_html(spec, meta)}{body.lstrip()}"
        path.write_text(new_text, encoding="utf-8")
        print(f"embedded {path.name}")

    if missing:
        print("unassigned:", missing)
        return 1
    print(f"ok {len(paths)} drafts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
