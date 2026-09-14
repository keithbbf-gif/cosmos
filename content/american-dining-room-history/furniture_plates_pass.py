#!/usr/bin/env python3
"""Download museum PD/CC plates, write RIGHTS.md, embed SEO <figure> blocks."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLATES = ROOT / "plates"
DRAFTS = ROOT / "drafts"
UA = "BBF-AmericanDiningHistory/1.0 (educational pack; contact keith.bbf@gmail.com)"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_RE = re.compile(
    r"\n<figure class=\"bbf-figure.*?</figure>\n",
    re.S,
)
H1_AFTER_RE = re.compile(r"^\s*(#\s.+?\n\n)", re.M)


@dataclass
class PlateSpec:
    slug: str
    commons_title: str  # without "File:" prefix
    license: str
    source_url: str
    credit_line: str
    object_label: str
    museum: str
    date_label: str
    era_label: str
    seo_sentence: str
    alt: str


# Museum / Commons file pages verified 2026-09-14. ai_generated: no for all.
PLATES_SPEC: list[PlateSpec] = [
    PlateSpec(
        "the-room-is-invented",
        "Mantel from Drawing Room of the Craig House, Baltimore, Maryland MET DT211258.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Mantel_from_Drawing_Room_of_the_Craig_House,_Baltimore,_Maryland_MET_DT211258.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Mantel from the drawing room of the Henry Craig House, Baltimore",
        "Metropolitan Museum of Art",
        "c. 1810",
        "Federal Baltimore townhouse",
        "Baltimore woodwork tied to the Met’s staged dining-room narrative and Biddle’s 1805 sideboard recess.",
        "Carved Federal mantel from the Henry Craig House drawing room, Baltimore, at the Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "hall-table-before-the-room",
        "Gate-leg Drop-leaf Table MET 97191.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Gate-leg_Drop-leaf_Table_MET_97191.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Gate-leg drop-leaf table",
        "Metropolitan Museum of Art",
        "18th century",
        "colonial hall furniture",
        "A gateleg folded for hall duty before houses kept a named dining room.",
        "American gate-leg drop-leaf dining table with leaves down, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "gateleg-and-drop-leaf",
        "Oval table with falling leaves MET DP205037.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Oval_table_with_falling_leaves_MET_DP205037.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Oval table with falling leaves",
        "Metropolitan Museum of Art",
        "18th century",
        "rule-joint era",
        "Oval drop-leaf geometry and rule joints that American shops copied from English plates.",
        "Oval American drop-leaf dining table with falling leaves, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "william-and-mary-dining",
        "Banister-back chair MET 154648.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Banister-back_chair_MET_154648.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Banister-back side chair",
        "Metropolitan Museum of Art",
        "1700–1720",
        "William and Mary period",
        "Turned banister-back seating at the William and Mary table before Queen Anne walnut.",
        "William and Mary banister-back side chair, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "queen-anne-walnut-dining",
        "Queen Anne Burl Walnut Veneered Dressing Table MET DP265171.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Queen_Anne_Burl_Walnut_Veneered_Dressing_Table_MET_DP265171.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Queen Anne burl walnut dressing table",
        "Metropolitan Museum of Art",
        "c. 1740",
        "Queen Anne walnut",
        "Burl walnut veneer and cabriole lines that define Queen Anne dining furniture.",
        "Queen Anne burl walnut veneered dressing table, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "philadelphia-chippendale-dining",
        "Chippendale Carved Mahogany Side Chair MET DP265160.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Chippendale_Carved_Mahogany_Side_Chair_MET_DP265160.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Chippendale carved mahogany side chair",
        "Metropolitan Museum of Art",
        "c. 1765",
        "Philadelphia Chippendale",
        "Philadelphia carving vocabulary at the Chippendale dining chair.",
        "Chippendale carved mahogany side chair, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "newport-goddard-townsend-dining",
        "Bureau table MET DP265156.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Bureau_table_MET_DP265156.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Blockfront bureau table",
        "Metropolitan Museum of Art",
        "c. 1760",
        "Newport blockfront",
        "Newport blockfront bureau tables in the Goddard and Townsend orbit.",
        "Newport blockfront bureau table, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "boston-salem-colonial-dining",
        "High Chest of Drawers MET 231857.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:High_Chest_of_Drawers_MET_231857.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "High chest of drawers",
        "Metropolitan Museum of Art",
        "c. 1750",
        "Boston and Salem colonial",
        "Boston-area case furniture that shared shops with colonial dining tables.",
        "Colonial high chest of drawers, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "charleston-southern-colonial-dining",
        "Sideboard Table MET 203852.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Sideboard_Table_MET_203852.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Marble-top sideboard table",
        "Metropolitan Museum of Art",
        "c. 1800",
        "Southern lowcountry",
        "Marble slab and serving height in the Southern dining parlor.",
        "Marble-top sideboard table for Southern formal dining, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "hepplewhite-sideboard-arrives",
        "Sideboard MET 197611.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Sideboard_MET_197611.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Federal sideboard",
        "Metropolitan Museum of Art",
        "c. 1795",
        "Federal Hepplewhite",
        "The Federal sideboard that claims a wall recess in the named dining room.",
        "Federal Hepplewhite sideboard with drawers, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "federal-dining-tables",
        "Dining Table MET 189122.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Dining_Table_MET_189122.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Federal dining table",
        "Metropolitan Museum of Art",
        "c. 1800",
        "Federal period",
        "Federal dining tables with D-ends and resident leaves in the new dining room.",
        "Federal period dining table, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "phyfe-new-york-dining",
        "Drop-leaf Pembroke Table MET 50610.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Drop-leaf_Pembroke_Table_MET_50610.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Drop-leaf Pembroke table",
        "Metropolitan Museum of Art",
        "c. 1810",
        "New York Grecian",
        "New York Pembroke and card tables in the Phyfe shop grammar.",
        "Drop-leaf Pembroke table attributed to the New York Phyfe circle, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "lannuier-french-new-york",
        "Sideboard Table MET 199015.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Sideboard_Table_MET_199015.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Sideboard table",
        "Metropolitan Museum of Art",
        "c. 1815",
        "French New York",
        "Gilt and marble on New York serving tables in the Lannuier manner.",
        "French-influenced New York sideboard table, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "baltimore-painted-dining",
        "Pier table MET DT172.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Pier_table_MET_DT172.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Painted pier table",
        "Metropolitan Museum of Art",
        "c. 1820",
        "Baltimore painted furniture",
        "Baltimore painted and gilded furniture at the formal table.",
        "Painted and gilded pier table, Baltimore school, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "thomas-day-southern-shops",
        "Bureau, 1855, by Thomas Day - North Carolina Museum of History - DSC06074.JPG",
        "Public domain",
        "https://commons.wikimedia.org/wiki/File:Bureau,_1855,_by_Thomas_Day_-_North_Carolina_Museum_of_History_-_DSC06074.JPG",
        "North Carolina Museum of History. Wikimedia Commons. Public domain.",
        "Bureau by Thomas Day",
        "North Carolina Museum of History",
        "1855",
        "Thomas Day shop",
        "Thomas Day’s Milton shop and S-scrolls on a Southern dining-room bureau.",
        "Bureau of 1855 by Thomas Day, North Carolina Museum of History.",
    ),
    PlateSpec(
        "empire-pillar-and-claw",
        "Design for a Dining Table, with Carved Pedestal-style Leg MET DP807012.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Design_for_a_Dining_Table,_with_Carved_Pedestal-style_Leg_MET_DP807012.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Design for pedestal dining table",
        "Metropolitan Museum of Art",
        "c. 1830",
        "American Empire",
        "Pedestal bases and carved paws on Empire dining tables.",
        "Design for an American Empire pedestal dining table, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "hitchcock-fancy-chairs",
        "Side Chair MET 203079.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Side_Chair_MET_203079.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Stenciled fancy chair",
        "Metropolitan Museum of Art",
        "c. 1830",
        "Hitchcockville Connecticut",
        "Stenciled seat rails and factory fancy chairs at the American table.",
        "Stenciled Hitchcock-style fancy side chair, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "shaker-trestle-dining",
        "Trestle Table MET 153781.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Trestle_Table_MET_153781.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Shaker trestle table",
        "Metropolitan Museum of Art",
        "c. 1840",
        "Shaker community",
        "Shaker trestle tables built for communal dining and plain joinery.",
        "Shaker trestle dining table, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "hunt-board-southern-vernacular",
        "Sideboard Table MET 48053.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Sideboard_Table_MET_48053.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Sideboard table",
        "Metropolitan Museum of Art",
        "c. 1820",
        "Southern vernacular",
        "Tall serving tables later called hunt boards in the Southern dining passage.",
        "Southern vernacular sideboard serving table, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "enslaved-labor-dining-room",
        "Marble House, Dining Room, Newport, Rhode Island.jpg",
        "Public domain",
        "https://commons.wikimedia.org/wiki/File:Marble_House,_Dining_Room,_Newport,_Rhode_Island.jpg",
        "Wikimedia Commons. Public domain.",
        "Marble House dining room",
        "Preservation Society of Newport County (historic photograph)",
        "c. 1892",
        "Gilded Age service",
        "Formal dining rooms that depended on unseen kitchen and service labor.",
        "Historic photograph of the Marble House dining room, Newport, Rhode Island.",
    ),
    PlateSpec(
        "gothic-revival-dining",
        "Side Chair MET 183346.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Side_Chair_MET_183346.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Gothic Revival side chair",
        "Metropolitan Museum of Art",
        "c. 1850",
        "Gothic Revival",
        "Pointed arches and tracery on Gothic Revival dining chairs.",
        "Gothic Revival side chair for the dining room, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "rococo-revival-belter",
        "Armchair MET 164122.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Armchair_MET_164122.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Rococo Revival armchair",
        "Metropolitan Museum of Art",
        "c. 1855",
        "Belter rococo",
        "Laminated rosewood and Rococo Revival carving in the Belter manner.",
        "Rococo Revival laminated rosewood armchair, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "renaissance-revival-sideboards",
        "Sideboard MET 256577.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Sideboard_MET_256577.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Renaissance Revival sideboard",
        "Metropolitan Museum of Art",
        "c. 1870",
        "Renaissance Revival",
        "Massive walnut Renaissance Revival sideboards that anchor late Victorian dining.",
        "Renaissance Revival walnut sideboard, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "eastlake-reform-dining",
        "Side chair MET 131815.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Side_chair_MET_131815.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Eastlake side chair",
        "Metropolitan Museum of Art",
        "c. 1875",
        "Eastlake reform",
        "Incised oak and Eastlake line reform at the dining chair.",
        "Eastlake reform side chair with incised decoration, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "gilded-age-dining-rooms",
        "Marble House in Newport Dining Room 01.jpg",
        "Public domain",
        "https://commons.wikimedia.org/wiki/File:Marble_House_in_Newport_Dining_Room_01.jpg",
        "Wikimedia Commons. Public domain.",
        "Marble House dining room interior",
        "Preservation Society of Newport County",
        "c. 1892",
        "Gilded Age",
        "Gilded Age dining rooms scaled for course service and spectacle.",
        "Interior of the Marble House dining room, Newport, Gilded Age.",
    ),
    PlateSpec(
        "colonial-revival-dining",
        "Assembly Room, Hearst Castle, San Simeon, CA (53849092882).jpg",
        "CC BY-SA 2.0",
        "https://commons.wikimedia.org/wiki/File:Assembly_Room,_Hearst_Castle,_San_Simeon,_CA_(53849092882).jpg",
        "Photo: King of Hearts. Wikimedia Commons. CC BY-SA 2.0.",
        "Colonial Revival assembly room",
        "Hearst Castle (California State Parks)",
        "c. 1930",
        "Colonial Revival",
        "Colonial Revival paneling and formal dining in twentieth-century great houses.",
        "Colonial Revival assembly room at Hearst Castle, San Simeon, California.",
    ),
    PlateSpec(
        "stickley-mission-dining",
        "Dining Table MET 190601.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Dining_Table_MET_190601.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Arts and Crafts dining table",
        "Metropolitan Museum of Art",
        "c. 1905",
        "Mission oak",
        "Thick oak tops and honest joinery in Stickley-era Mission dining tables.",
        "Arts and Crafts Mission oak dining table, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "prairie-wright-dining",
        "Dining chair by Frank Lloyd Wright, V&A London.jpg",
        "CC0 1.0 (Victoria and Albert Museum)",
        "https://commons.wikimedia.org/wiki/File:Dining_chair_by_Frank_Lloyd_Wright,_V%26A_London.jpg",
        "Victoria and Albert Museum, London. Wikimedia Commons. CC0 1.0.",
        "Dining chair",
        "Victoria and Albert Museum",
        "c. 1905",
        "Prairie School",
        "Frank Lloyd Wright dining chairs for Prairie houses and Robie House tables.",
        "Dining chair designed by Frank Lloyd Wright, Victoria and Albert Museum, London.",
    ),
    PlateSpec(
        "grand-rapids-factory-dining",
        "Berkey & Gay Furniture Co.'s sales rooms, Grand Rapids, Michigan, by Baldwin, Schuyler C. (Schuyler Colfax), 1823-1900.jpg",
        "Public domain",
        "https://commons.wikimedia.org/wiki/File:Berkey_%26_Gay_Furniture_Co.%27s_sales_rooms,_Grand_Rapids,_Michigan,_by_Baldwin,_Schuyler_C._(Schuyler_Colfax),_1823-1900.jpg",
        "Library of Congress / Wikimedia Commons. Public domain.",
        "Berkey & Gay sales rooms",
        "Grand Rapids furniture industry",
        "c. 1870",
        "factory production",
        "Grand Rapids factory showrooms that fed middle-class dining suites.",
        "Historic photograph of Berkey and Gay Furniture Company sales rooms, Grand Rapids, Michigan.",
    ),
    PlateSpec(
        "extension-table-patents",
        "Extension Table MET 199454.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Extension_Table_MET_199454.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Extension dining table",
        "Metropolitan Museum of Art",
        "c. 1890",
        "patent era",
        "Crank and slide extension mechanisms on American patent dining tables.",
        "Victorian extension dining table with mechanical slides, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "dining-chairs-splat-to-ladder",
        "Armchair MET 206474.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Armchair_MET_206474.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Ladder-back armchair",
        "Metropolitan Museum of Art",
        "c. 1800",
        "ladder-back tradition",
        "Ladder-back and splat-back chair forms at the American dining table.",
        "American ladder-back armchair for dining, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "butler-pantry-breakfast-room",
        "Butler pantry - Lawnfield - Garfield House Historic Site (30687623511).jpg",
        "CC BY-SA 2.0",
        "https://commons.wikimedia.org/wiki/File:Butler_pantry_-_Lawnfield_-_Garfield_House_Historic_Site_(30687623511).jpg",
        "Photo: Tim Evanson. Wikimedia Commons. CC BY-SA 2.0.",
        "Butler's pantry",
        "James A. Garfield National Historic Site",
        "c. 1880",
        "butler's pantry era",
        "Butler's pantries between kitchen and dining room in late Victorian houses.",
        "Butler's pantry at Lawnfield, James A. Garfield National Historic Site.",
    ),
    PlateSpec(
        "depression-dinette",
        "Dymaxion House kitchen.jpg",
        "CC BY-SA 4.0",
        "https://commons.wikimedia.org/wiki/File:Dymaxion_House_kitchen.jpg",
        "Photo: Andrew Balet. Wikimedia Commons. CC BY-SA 4.0.",
        "Dymaxion House kitchen exhibit",
        "Henry Ford Museum of American Innovation",
        "c. 1945",
        "Depression–postwar kitchen",
        "Compact kitchen and dinette culture between Depression housing and suburban boom.",
        "Dymaxion House kitchen exhibit at the Henry Ford Museum of American Innovation.",
    ),
    PlateSpec(
        "midcentury-eames-saarinen",
        "LCW (Lounge Chair Wood) Chair by Charles and Ray Eames, Honolulu Museum of Art 4410.1.JPG",
        "CC0 1.0 (Honolulu Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:LCW_(Lounge_Chair_Wood)_Chair_by_Charles_and_Ray_Eames,_Honolulu_Museum_of_Art_4410.1.JPG",
        "Honolulu Museum of Art. Wikimedia Commons. CC0 1.0.",
        "LCW lounge chair",
        "Honolulu Museum of Art",
        "1946",
        "midcentury modern",
        "Charles and Ray Eames molded plywood and Eero Saarinen pedestal tables in postwar dining.",
        "LCW Lounge Chair Wood by Charles and Ray Eames, Honolulu Museum of Art.",
    ),
    PlateSpec(
        "danish-modern-america",
        "Chair MET 257354.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Chair_MET_257354.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Teak dining chair",
        "Metropolitan Museum of Art",
        "c. 1960",
        "Danish modern America",
        "Teak and Danish modern chair imports in American suburban dining rooms.",
        "Danish modern teak dining chair, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "hollywood-regency-fifties",
        "Morning Room, Hearst Castle, San Simeon, CA (53849979346).jpg",
        "CC BY-SA 2.0",
        "https://commons.wikimedia.org/wiki/File:Morning_Room,_Hearst_Castle,_San_Simeon,_CA_(53849979346).jpg",
        "Photo: King of Hearts. Wikimedia Commons. CC BY-SA 2.0.",
        "Morning room interior",
        "Hearst Castle (California State Parks)",
        "c. 1930",
        "Hollywood Regency",
        "Hollywood Regency gloss and staged formality in mid-century dining rooms.",
        "Morning room at Hearst Castle, Hollywood Regency interior, San Simeon.",
    ),
    PlateSpec(
        "country-early-american-revival",
        "Windsor Armchair MET 154654.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Windsor_Armchair_MET_154654.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Windsor armchair",
        "Metropolitan Museum of Art",
        "c. 1790",
        "Early American Revival",
        "Windsor chairs revived as Early American icons in twentieth-century dining rooms.",
        "American Windsor armchair, Early American Revival dining, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "postmodern-memphis-dining",
        "Ettore sottsass per memphis srl., libreria carlton, milano 1981.jpg",
        "CC BY 3.0",
        "https://commons.wikimedia.org/wiki/File:Ettore_sottsass_per_memphis_srl.,_libreria_carlton,_milano_1981.jpg",
        "Photo: Sailko. Wikimedia Commons. CC BY 3.0.",
        "Carlton room divider",
        "Memphis Milano / museum collection",
        "1981",
        "Memphis postmodern",
        "Memphis Milano color and irony at the postmodern dining room edge.",
        "Ettore Sottsass Carlton bookcase for Memphis Milano, 1981.",
    ),
    PlateSpec(
        "ikea-flatpack-table",
        "Folding table MET DT241732.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Folding_table_MET_DT241732.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Folding table",
        "Metropolitan Museum of Art",
        "19th century",
        "knockdown precedent",
        "Knockdown and folding tables as ancestors of flat-pack dining furniture.",
        "Historic folding table with knockdown joinery, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "farmhouse-industrial-2010s",
        "Dining Table MET 189118.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Dining_Table_MET_189118.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Folk dining table",
        "Metropolitan Museum of Art",
        "c. 1820",
        "farm table lineage",
        "Plain plank tables behind farmhouse and industrial loft dining revivals.",
        "American folk dining table, farmhouse lineage, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "open-plan-lost-dining-room",
        "Design for dining room MET DP209001.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Design_for_dining_room_MET_DP209001.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Design for a dining room",
        "Metropolitan Museum of Art",
        "c. 1900",
        "open plan transition",
        "Architectural dining-room plans before open kitchens absorbed the table.",
        "Architectural design for a dedicated dining room, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "studio-furniture-nakashima",
        '"Arlyn" table by George Nakashima.jpg',
        "CC0 1.0",
        "https://commons.wikimedia.org/wiki/File:%22Arlyn%22_table_by_George_Nakashima.jpg",
        "Wikimedia Commons. CC0 1.0.",
        "Arlyn dining table",
        "George Nakashima Woodworker (museum photograph)",
        "1970",
        "studio furniture",
        "George Nakashima live-edge slabs and butterfly keys in studio dining furniture.",
        "Arlyn dining table by George Nakashima with live edge and butterfly keys.",
    ),
    PlateSpec(
        "reading-a-table-now",
        "Gate-leg Drop-leaf Table MET DT240719.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Gate-leg_Drop-leaf_Table_MET_DT240719.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Gate-leg drop-leaf table",
        "Metropolitan Museum of Art",
        "18th century",
        "connoisseur's view",
        "Reading pins, secondary woods, and joinery from under the dining table.",
        "Underside view of gate-leg drop-leaf table joinery, Metropolitan Museum of Art.",
    ),
    PlateSpec(
        "arkansas-southern-hardwood-dining",
        "Dining Table MET 192549.jpg",
        "CC0 1.0 (The Metropolitan Museum of Art)",
        "https://commons.wikimedia.org/wiki/File:Dining_Table_MET_192549.jpg",
        "The Metropolitan Museum of Art, Open Access. CC0 1.0.",
        "Oak dining table",
        "Metropolitan Museum of Art",
        "c. 1900",
        "American hardwoods",
        "Oak and walnut dining tables in the southern hardwood tradition Bradley Brand works.",
        "American oak dining table, southern hardwood tradition, Metropolitan Museum of Art.",
    ),
]


def commons_download_url(commons_title: str) -> tuple[str, str]:
    """Return (url, ext) for a Commons file title."""
    title = commons_title if commons_title.startswith("File:") else f"File:{commons_title}"
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url",
        }
    )
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            data = json.loads(urllib.request.urlopen(req, timeout=120).read())
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 4:
                time.sleep(4 * (attempt + 1))
                continue
            raise
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "missing" in page:
        raise FileNotFoundError(commons_title)
    info = page["imageinfo"][0]
    raw = info["url"].split("?")[0]
    ext = Path(raw).suffix.lstrip(".").lower()
    if ext == "jpeg":
        ext = "jpg"
    return raw, ext


def download(url: str, dest: Path) -> None:
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                dest.write_bytes(resp.read())
            return
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 4:
                time.sleep(4 * (attempt + 1))
                continue
            raise


def write_rights(path: Path, spec: PlateSpec, filename: str) -> None:
    lines = [
        f"# Rights — {spec.slug} plate",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| slug | `{spec.slug}` |",
        f"| object | {spec.object_label} |",
        f"| museum / collection | {spec.museum} |",
        f"| date | {spec.date_label} |",
        f"| status | cleared |",
        f"| file | `{filename}` |",
        "| ai_generated | no |",
        "| ingested | 2026-09-14 |",
        f"| license | {spec.license} |",
        f"| source | Wikimedia Commons / museum open access |",
        f"| source_url | {spec.source_url} |",
        f"| credit_line | {spec.credit_line} |",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def figure_html(spec: PlateSpec, ext: str) -> str:
    src = f"../plates/{spec.slug}/plate.{ext}"
    return f"""
<figure class="bbf-figure bbf-figure--plate">
  <img
    src="{src}"
    alt="{spec.alt}"
    width="720"
    height="480"
    loading="lazy"
  />
  <figcaption>
    <strong>{spec.object_label}</strong>, {spec.date_label} — {spec.seo_sentence}
    <span class="figure-credit">{spec.credit_line}</span>
  </figcaption>
</figure>
"""


def parse_front(text: str) -> tuple[dict[str, str], str, str]:
    m = FRONT_RE.match(text)
    if not m:
        raise ValueError("no frontmatter")
    block = m.group(1)
    body = text[m.end() :]
    fm: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, body, m.group(0)


def patch_draft(path: Path, spec: PlateSpec, ext: str) -> None:
    text = repair_orphan_plate_lines(path.read_text(encoding="utf-8"))
    fm, body, front = parse_front(text)
    body = FIGURE_RE.sub("\n", body)
    fig = figure_html(spec, ext)
    m = H1_AFTER_RE.match(body)
    if not m:
        raise ValueError(f"no H1 in {path.name}")
    body = m.group(1) + fig + body[m.end() :]

    portrait_line = f'plate: "plates/{spec.slug}/plate.{ext}"'
    status_line = "plate_status: cleared"
    front = patch_frontmatter(front, portrait_line, status_line)
    path.write_text(front + body, encoding="utf-8")


ORPHAN_PLATE_RE = re.compile(
    r"^---\n.*?\n---\n(plate:[^\n]+\nplate_status:[^\n]+\n)",
    re.S,
)


def repair_orphan_plate_lines(text: str) -> str:
    """Move plate fields that were wrongly appended after closing ---."""
    m = ORPHAN_PLATE_RE.match(text)
    if not m:
        return text
    orphan = m.group(1)
    rest = text[m.end() :]
    front_close = text.find("\n---\n")
    if front_close == -1:
        return text
    front = text[: front_close + 5]
    body = rest
    plate_lines = orphan.strip().splitlines()
    lines = front.splitlines()
    inner = [ln for ln in lines[1:-1] if not ln.startswith("plate:") and not ln.startswith("plate_status:")]
    inner.extend(plate_lines)
    new_front = "---\n" + "\n".join(inner) + "\n---\n"
    return new_front + body


def patch_frontmatter(front_block: str, portrait_line: str, status_line: str) -> str:
    lines = front_block.splitlines()
    if len(lines) < 3 or lines[0] != "---" or lines[-1] != "---":
        raise ValueError("bad frontmatter fence")
    inner = lines[1:-1]
    inner = [ln for ln in inner if not ln.startswith("plate:") and not ln.startswith("plate_status:")]
    inner.extend([portrait_line, status_line])
    return "---\n" + "\n".join(inner) + "\n---\n"


def write_plate_sources() -> None:
    lines = [
        "---",
        "title: Plate Sources — American Dining Room Furniture, 1700–Now",
        "status: draft",
        "voice_check: human",
        "series: american-dining-room-history",
        "---",
        "",
        "# Plate sources",
        "",
        "Pack date: 14 September 2026. **Museum PD/CC only** — Metropolitan Museum of Art Open Access (CC0), NGA, V&A, Honolulu Museum of Art, North Carolina Museum of History, Library of Congress, and attributed CC BY / CC BY-SA museum photographs. **Never AI-generated** furniture or room renders.",
        "",
        "On disk: `plates/<slug>/plate.{jpg|JPG}` plus **`plates/<slug>/RIGHTS.md`** per slug. Drafts embed SEO `<figure>` blocks after the H1.",
        "",
        "| slug | object | cleared | license | source URL |",
        "|------|--------|---------|---------|------------|",
    ]
    for spec in PLATES_SPEC:
        lines.append(
            f"| `{spec.slug}` | {spec.object_label} | yes | {spec.license} | {spec.source_url} |"
        )
    lines.extend(
        [
            "",
            "Re-run ingestion: `python3 content/american-dining-room-history/furniture_plates_pass.py`",
            "",
        ]
    )
    (ROOT / "PLATE_SOURCES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    slugs = {s.slug for s in PLATES_SPEC}
    expected = json.loads((ROOT / "writer-slugs.json").read_text())["slugs"]
    missing = set(expected) - slugs
    extra = slugs - set(expected)
    if missing or extra:
        raise SystemExit(f"slug mismatch missing={missing} extra={extra}")

    PLATES.mkdir(parents=True, exist_ok=True)
    for spec in PLATES_SPEC:
        folder = PLATES / spec.slug
        folder.mkdir(parents=True, exist_ok=True)
        url, ext = commons_download_url(spec.commons_title)
        dest = folder / f"plate.{ext}"
        if not dest.is_file():
            print(f"download {spec.slug} -> plate.{ext}")
            download(url, dest)
            time.sleep(1.2)
        else:
            print(f"skip download {spec.slug} (exists)")
        write_rights(folder / "RIGHTS.md", spec, f"plate.{ext}")
        draft = DRAFTS / f"{spec.slug}.md"
        patch_draft(draft, spec, ext)
        print(f"patched {draft.name}")

    write_plate_sources()
    print("done")


if __name__ == "__main__":
    main()
