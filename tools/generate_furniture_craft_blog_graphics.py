#!/usr/bin/env python3
"""Generate furniture-craft-blog drafts, SVG assets, and GRAPHICS_INDEX.md."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "content" / "furniture-craft-blog"
ASSETS = BLOG / "assets"
DRAFTS = BLOG / "drafts"

CREAM = "#F7F3E8"
INK = "#1A1A1A"
INK_LIGHT = "#4A4A4A"
ACCENT = "#8B4513"
GRID = "#D4C9B0"

GraphicKind = Literal["joinery", "tools", "finish", "process"]


@dataclass(frozen=True)
class Article:
    num: int
    slug: str
    title: str
    kind: GraphicKind
    meta: str
    tags: list[str]
    graphic_title: str
    caption: str
    photo_caption: str


ARTICLES: list[Article] = [
    Article(1, "mortise-and-tenon-basics", "Mortise and tenon: cheeks, shoulders, and glue line", "joinery",
            "How to lay out a through mortise and tenon so shoulders register before glue.", ["joinery", "mortise", "tenon"],
            "Through mortise and tenon (section)", "Cheek faces stay parallel; shoulders define depth stop.",
            "Shop shot: test fit on the bench before glue."),
    Article(2, "dovetail-layout", "Dovetail layout without guessing the angle", "joinery",
            "Pin and tail spacing from a single baseline and half-pins at the ends.", ["dovetails", "layout", "hand-tools"],
            "Half-blind dovetail layout", "Baseline and slope lines before any saw cut.",
            "Shop shot: tails marked on end grain."),
    Article(3, "half-blind-dovetails", "Half-blind dovetails for drawer fronts", "joinery",
            "Socket depth, tail length, and hiding the joint from the front.", ["dovetails", "drawers"],
            "Half-blind socket depth", "Tail length equals socket depth plus reveal allowance.",
            "Shop shot: drawer front clamped for chopping."),
    Article(4, "breadboard-ends", "Breadboard ends that still let the top move", "joinery",
            "Center fixed pin, elongated slots at the ends, and glue only in the middle.", ["tablet", "movement", "joinery"],
            "Breadboard end movement", "Fixed center; slots at ends for seasonal width change.",
            "Shop shot: breadboard dry-fit on tabletop."),
    Article(5, "dowel-vs-biscuit", "Dowels vs biscuits for case glue-ups", "finish",
            "When alignment matters more than open time.", ["glue", "joinery", "case"],
            "Alignment aid comparison", "Dowels: strong registration. Biscuits: face alignment, weaker shear.",
            "Shop shot: case dry-clamped on bench."),
    Article(6, "hand-plane-setup", "Hand plane setup: frog, mouth, and cap iron", "tools",
            "Chip breaker close to the edge for figured wood; open mouth for thick shavings.", ["planes", "sharpening"],
            "Bench plane iron assembly", "Cap iron ~0.5–1 mm behind cutting edge for general work.",
            "Shop shot: plane on shooting board."),
    Article(7, "chisel-sharpening-jig", "Chisel sharpening on a honing guide", "tools",
            "Primary bevel, micro-bevel, and back flattening order.", ["chisels", "sharpening"],
            "Honing guide setup", "Roll to micro-bevel; do not grind away the registration face.",
            "Shop shot: chisel backs on glass plate."),
    Article(8, "table-saw-fence-check", "Table saw fence parallel to the blade", "tools",
            "Measure front and rear tooth to fence; adjust until both match.", ["table-saw", "setup"],
            "Fence alignment check", "Same gap at front and rear of blade plate.",
            "Shop shot: dial indicator on fence rail."),
    Article(9, "block-plane-use", "Block plane: bevel-up shavings for end grain", "tools",
            "Low angle for end grain; higher pitch for tricky face grain.", ["planes", "block-plane"],
            "Block plane cut direction", "Plane into the uphill grain on end grain.",
            "Shop shot: end-grain shooting on bench hook."),
    Article(10, "marking-gauge-technique", "Marking gauge lines that saws can follow", "tools",
            "Light scoring pass, then firm pass; knife wall for crosscuts.", ["layout", "gauges"],
            "Knife wall at layout line", "Saw kerf rides in the knife wall; waste side is obvious.",
            "Shop shot: gauge line on drawer side."),
    Article(11, "shellac-vs-polyurethane", "Shellac vs polyurethane for tabletops", "finish",
            "Repairability, heat, and build coats compared without hype.", ["finish", "shellac", "poly"],
            "Finish property comparison", "Shellac: fast repair; poly: harder film, slower spot fix.",
            "Shop shot: finish samples on offcuts."),
    Article(12, "oil-finish-maintenance", "Oil finish maintenance on hard-use tables", "finish",
            "When to refresh vs strip; curing vs drying.", ["oil", "maintenance"],
            "Oil finish refresh cycle", "Light wipe coat when water no longer beads.",
            "Shop shot: oiled tabletop in use."),
    Article(13, "water-pop-before-finish", "Water pop before the first finish coat", "process",
            "Raise grain once, dry, then cut back before sealing.", ["sanding", "finish"],
            "Water pop sequence", "Wet → dry → 220 → seal; avoids raised grain after finish.",
            "Shop shot: wiped surface before pop."),
    Article(14, "sanding-grit-sequence", "Sanding grit sequence that does not skip steps", "process",
            "Each grit removes the scratches of the previous one.", ["sanding", "prep"],
            "Grit progression", "80 → 120 → 150 → 180 → 220 for film finishes.",
            "Shop shot: random orbit on case side."),
    Article(15, "glue-up-clamping-strategy", "Glue-up clamping: cauls, sequence, and open time", "process",
            "Dry run clamp map; longest open-time joint first.", ["glue", "clamps"],
            "Clamp order flow", "Dry fit → glue longest joint → cauls → check square → wipe squeeze-out.",
            "Shop shot: case in clamps with cauls."),
    Article(16, "case-dry-fit", "Case dry-fit checklist before glue", "process",
            "Square, flush, and hardware clearances without adhesive panic.", ["case", "assembly"],
            "Dry-fit gate", "No glue until square repeats twice and hardware clears.",
            "Shop shot: dry-fit with strap clamps."),
    Article(17, "steam-bending-form", "Steam bending: form radius and springback", "process",
            "Over-bend slightly; strap and cool on the form.", ["bending", "chairs"],
            "Steam bend cooling", "Strap compresses outside; stay on form until cool.",
            "Shop shot: bent crest on form."),
    Article(18, "resawing-veneer", "Resawing veneer on the bandsaw", "process",
            "Blade drift, fence lead-in, and sticker stack drying.", ["veneer", "bandsaw"],
            "Resaw path", "Tall fence + featherboard; flip book-match at center cut.",
            "Shop shot: veneer stack in stickers."),
    Article(19, "crosscut-sled", "Crosscut sled: zero-clearance and stop block", "tools",
            "Runner fit, fence square to blade, replaceable insert.", ["table-saw", "jigs"],
            "Crosscut sled layout", "Fence 90° to blade; stop block for repeat length.",
            "Shop shot: sled on saw."),
    Article(20, "router-table-setup", "Router table: bit height and fence bearing", "tools",
            "Push against rotation; offset fence for edge profiles.", ["router", "setup"],
            "Router table feed direction", "Feed against bit rotation; bearing follows template.",
            "Shop shot: profile test on scrap."),
    Article(21, "drawer-fit-shimming", "Drawer fit: shims and parallel runners", "joinery",
            "Even reveals; side clearance for seasonal width.", ["drawers", "fit"],
            "Drawer side clearance", "1–2 mm total side play; front reveal even left-right.",
            "Shop shot: drawer half-out showing reveal."),
    Article(22, "hinge-mortise-by-hand", "Hinge mortises by hand chisel", "joinery",
            "Depth stop with knife wall; pare to line.", ["hardware", "chisels"],
            "Butt hinge mortise depth", "Mortise depth = hinge leaf thickness; barrel flush.",
            "Shop shot: hinge test fit in door stile."),
    Article(23, "tabletop-flattening", "Flattening a glued tabletop", "process",
            "Cross-hatch with No. 5, diagonals, then with the grain.", ["flattening", "hand-planes"],
            "Top flattening pattern", "High spots only; diagonal passes until winding sticks agree.",
            "Shop shot: winding sticks on glue-up."),
    Article(24, "edge-banding-solid-wood", "Solid-wood edge banding on plywood", "joinery",
            "Groove or tongue; glue and tape clamp; flush trim after cure.", ["plywood", "edge-band"],
            "Solid edge on ply", "Slightly proud band; flush after glue cures.",
            "Shop shot: iron-on vs solid strip comparison."),
    Article(25, "shop-dust-collection-layout", "Shop dust collection: hose runs and blast gates", "tools",
            "Shortest run to the collector; gate only what you need.", ["dust", "shop"],
            "Dust trunk layout", "Main trunk + branches; blast gate at each machine.",
            "Shop shot: collector and hose drops."),
    Article(26, "lumber-milling-order", "Milling lumber: face, edge, thickness", "process",
            "Joint one face, edge square, then thickness to final.", ["milling", "jointer"],
            "Mill four-square sequence", "Face → edge 90° → rip width → thickness to gauge.",
            "Shop shot: boards at jointer."),
    Article(27, "wood-movement-across-grain", "Wood movement across the grain", "joinery",
            "Why tabletops are anchored in the middle only.", ["movement", "design"],
            "Width change vs grain", "Tangential movement roughly 2× radial on many species.",
            "Shop shot: gap at breadboard end in winter."),
    Article(28, "seasonal-gaps-in-drawers", "Seasonal gaps in solid-wood drawers", "joinery",
            "Allow side clearance; do not size drawers at peak humidity.", ["drawers", "movement"],
            "Drawer in summer vs winter", "Size for mid-RH; runners take up slack.",
            "Shop shot: tight drawer in humid week."),
    Article(29, "choosing-hardwood-boards", "Choosing hardwood boards at the yard", "process",
            "Defect map, grain direction for the part, and yield.", ["lumber", "buying"],
            "Board defect map", "Mark knots and sap; nest longest parts on clearest grain.",
            "Shop shot: stickered pile at yard."),
    Article(30, "reading-grain-for-planing", "Reading grain for tear-out-free planing", "process",
            "Plane into the uphill; reverse on patches.", ["grain", "planes"],
            "Grain direction arrows", "Cathedral opens toward you = often downhill on face.",
            "Shop shot: tear-out patch and corrected pass."),
    Article(31, "bandsaw-blade-tension", "Bandsaw blade tension and drift", "tools",
            "Tension by deflection; drift tracked before fence lock.", ["bandsaw", "setup"],
            "Blade drift adjustment", "Mark freehand cut; set fence parallel to drift line.",
            "Shop shot: drift line on test board."),
    Article(32, "shooting-board-build", "Shooting board for square end grain", "tools",
            "Hook stops plane; fence 90° to sole path.", ["jigs", "shooting-board"],
            "Shooting board section", "Plane rides fence; work stops on hook.",
            "Shop shot: shooting end of drawer part."),
    Article(33, "workbench-dog-holes", "Workbench dog holes and holdfast layout", "tools",
            "Row spacing for planing and assembly tasks.", ["workbench", "holdfast"],
            "Dog hole grid", "Front row for planing; second row for wider panels.",
            "Shop shot: holdfast in dog hole."),
    Article(34, "holdfast-workholding", "Holdfast workholding for case sides", "tools",
            "Angle and bench thickness matter more than brand.", ["holdfast", "workholding"],
            "Holdfast shaft angle", "Shaft wedges in hole; pad presses work to bench.",
            "Shop shot: case side held for planing."),
    Article(35, "card-scraper-vs-sanding", "Card scraper vs sanding before finish", "finish",
            "Burrs cut torn grain; sanding follows for even sheen.", ["scraper", "prep"],
            "Scraper then sand", "Scraper for tear-out; 180–220 to unify scratch pattern.",
            "Shop shot: scraper curl on cherry."),
    Article(36, "french-polish-overview", "French polish: shellac pad and oil slip", "finish",
            "Thin coats, lubricated pad, no heavy build in one session.", ["shellac", "french-polish"],
            "Rubber pad paths", "Figure-eight with thin shellac; oil slip prevents drag.",
            "Shop shot: pad materials on bench."),
    Article(37, "milk-paint-on-primer", "Milk paint over a sizing primer", "finish",
            "Bond coat for raw wood; two thin milk paint coats.", ["paint", "milk-paint"],
            "Milk paint layers", "Sizing → milk paint → light sand → second coat.",
            "Shop shot: brushed sample boards."),
    Article(38, "wax-over-shellac", "Wax over shellac for low-luster furniture", "finish",
            "Shellac seals; wax buffs; repair stays local.", ["wax", "shellac"],
            "Shellac then wax", "2–3 lb cut shellac; paste wax after cure, buff out.",
            "Shop shot: buffed chair arm."),
    Article(39, "finishing-outdoor-furniture", "Outdoor furniture finishes that can be renewed", "finish",
            "Film builds fail outdoors; oil or thinned exterior formulas refresh.", ["outdoor", "finish"],
            "Outdoor finish refresh", "Annual light coat beats thick build that peels.",
            "Shop shot: outdoor table after season."),
    Article(40, "repair-loose-chair-wedged-tenon", "Repairing a loose chair with a wedged tenon", "joinery",
            "Disassemble, clean old glue, reglue, wedge if mortise is worn.", ["repair", "chairs"],
            "Wedged through-tenon", "Wedge spreads tenon in mortise; orient wedge across grain.",
            "Shop shot: chair reglue clamped."),
    Article(41, "carving-gouge-grind", "Carving gouge grind and inside bevel", "tools",
            "Outside bevel for depth; inside bevel for reach.", ["carving", "sharpening"],
            "Gouge bevel profile", "Outside bevel sets depth; inside bevel aids tight curves.",
            "Shop shot: gouges on strop."),
    Article(42, "curved-apron-template", "Curved apron from a plywood template", "process",
            "Template guides router; fair curve before fairing by hand.", ["curves", "template"],
            "Template routing path", "Pattern bit follows template; climb cuts on exit only with care.",
            "Shop shot: apron on template."),
    Article(43, "torsion-box-shelf", "Torsion box shelf for long spans", "joinery",
            "Skins in shear; grid resists sag without solid thickness.", ["shelves", "case"],
            "Torsion box section", "Top and bottom skins glued to grid; edges capture square.",
            "Shop shot: dry assembly of grid."),
    Article(44, "sliding-dovetail-shelf", "Sliding dovetail shelf support", "joinery",
            "Tapered tail slides in; capture dado at back.", ["dovetails", "shelves"],
            "Sliding dovetail shelf", "Tail narrower at front; slide from back rail.",
            "Shop shot: shelf tail in gable dado."),
    Article(45, "pocket-hole-when-to-use", "When pocket holes are the right joint", "joinery",
            "Face frames and carcass backs; not for show joinery.", ["pocket-hole", "assembly"],
            "Pocket hole use map", "OK: face frame, carcass back. Avoid: visible show faces.",
            "Shop shot: face frame clamped."),
]


def svg_header(w: int, h: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{{title}}</title>\n'
        f'  <desc id="desc">{{desc}}</desc>\n'
        f'  <rect width="100%" height="100%" fill="{CREAM}"/>\n'
    )


def svg_footer() -> str:
    return "</svg>\n"


def wrap_title(title: str, x: int, y: int, size: int = 20) -> str:
    return (
        f'  <text x="{x}" y="{y}" fill="{INK}" font-family="Georgia, serif" '
        f'font-size="{size}" font-weight="600">{title}</text>\n'
    )


def joinery_svg(title: str, desc: str, variant: str) -> str:
    w, h = 640, 420
    parts = [svg_header(w, h).format(title=title, desc=desc)]
    parts.append(wrap_title(title, 32, 44))
    parts.append(f'  <rect x="24" y="64" width="{w-48}" height="{h-88}" fill="none" stroke="{GRID}" stroke-width="1"/>\n')
    if variant == "mortise":
        parts.append(f'  <rect x="120" y="140" width="80" height="200" fill="none" stroke="{INK}" stroke-width="2.5"/>\n')
        parts.append(f'  <rect x="200" y="160" width="280" height="40" fill="{CREAM}" stroke="{INK}" stroke-width="2.5"/>\n')
        parts.append(f'  <line x1="200" y1="200" x2="200" y2="340" stroke="{INK}" stroke-width="2.5"/>\n')
        parts.append(f'  <text x="130" y="360" fill="{INK_LIGHT}" font-family="Helvetica, Arial, sans-serif" font-size="13">mortise</text>\n')
        parts.append(f'  <text x="300" y="155" fill="{INK_LIGHT}" font-family="Helvetica, Arial, sans-serif" font-size="13">tenon cheek</text>\n')
        parts.append(f'  <text x="210" y="320" fill="{INK_LIGHT}" font-family="Helvetica, Arial, sans-serif" font-size="13">shoulder</text>\n')
    elif variant == "dovetail":
        parts.append(f'  <polygon points="140,320 180,260 220,320" fill="none" stroke="{INK}" stroke-width="2.5"/>\n')
        parts.append(f'  <polygon points="220,320 260,260 300,320" fill="none" stroke="{INK}" stroke-width="2.5"/>\n')
        parts.append(f'  <line x1="120" y1="340" x2="520" y2="340" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="6 4"/>\n')
        parts.append(f'  <text x="124" y="332" fill="{ACCENT}" font-family="Helvetica, Arial, sans-serif" font-size="12">baseline</text>\n')
    elif variant == "breadboard":
        parts.append(f'  <rect x="100" y="200" width="400" height="60" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        parts.append(f'  <rect x="500" y="190" width="40" height="80" fill="none" stroke="{INK}" stroke-width="2.5"/>\n')
        parts.append(f'  <circle cx="520" cy="230" r="6" fill="{INK}"/>\n')
        parts.append(f'  <rect x="512" y="250" width="16" height="30" fill="none" stroke="{ACCENT}" stroke-width="2"/>\n')
        parts.append(f'  <text x="360" y="190" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">top (width moves)</text>\n')
        parts.append(f'  <text x="505" y="360" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">slot</text>\n')
    elif variant == "drawer":
        parts.append(f'  <rect x="160" y="160" width="320" height="180" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        parts.append(f'  <rect x="180" y="180" width="280" height="140" fill="none" stroke="{INK_LIGHT}" stroke-width="1.5" stroke-dasharray="4 3"/>\n')
        parts.append(f'  <text x="170" y="150" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">1–2 mm side clearance</text>\n')
    elif variant == "hinge":
        parts.append(f'  <rect x="200" y="180" width="120" height="160" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        parts.append(f'  <rect x="200" y="200" width="40" height="80" fill="{INK_LIGHT}" opacity="0.25" stroke="{INK}" stroke-width="1.5"/>\n')
        parts.append(f'  <text x="250" y="220" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">mortise depth = leaf</text>\n')
    elif variant == "movement":
        parts.append(f'  <line x1="100" y1="250" x2="540" y2="250" stroke="{INK}" stroke-width="3"/>\n')
        parts.append(f'  <path d="M 300 250 l -30 -20 M 300 250 l 30 -20" stroke="{ACCENT}" stroke-width="2" fill="none"/>\n')
        parts.append(f'  <text x="280" y="290" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">across grain width</text>\n')
    elif variant == "wedge":
        parts.append(f'  <rect x="280" y="160" width="200" height="50" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        parts.append(f'  <polygon points="280,210 280,310 330,310" fill="none" stroke="{INK}" stroke-width="2.5"/>\n')
        parts.append(f'  <polygon points="300,220 320,240 300,260" fill="{ACCENT}" stroke="{INK}" stroke-width="1"/>\n')
        parts.append(f'  <text x="340" y="280" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">wedge across grain</text>\n')
    elif variant == "sliding_dt":
        parts.append(f'  <rect x="140" y="200" width="360" height="24" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        parts.append(f'  <polygon points="160,224 200,280 240,224" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        parts.append(f'  <text x="280" y="300" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">slide from back</text>\n')
    elif variant == "torsion":
        parts.append(f'  <rect x="120" y="170" width="400" height="120" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        for i in range(5):
            parts.append(f'  <line x1="{160+i*70}" y1="190" x2="{160+i*70}" y2="270" stroke="{INK_LIGHT}" stroke-width="1"/>\n')
        parts.append(f'  <text x="200" y="320" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">grid + face skins</text>\n')
    elif variant == "pocket":
        parts.append(f'  <rect x="160" y="160" width="140" height="200" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        parts.append(f'  <rect x="300" y="160" width="140" height="200" fill="none" stroke="{INK}" stroke-width="2"/>\n')
        parts.append(f'  <line x1="230" y1="220" x2="310" y2="240" stroke="{ACCENT}" stroke-width="2" marker-end="url(#arr)"/>\n')
        parts.append(f'  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="{ACCENT}"/></marker></defs>\n')
        parts.append(f'  <text x="180" y="380" fill="{INK_LIGHT}" font-size="12" font-family="sans-serif">face frame OK · show face avoid</text>\n')
    else:
        parts.append(f'  <rect x="180" y="160" width="280" height="160" fill="none" stroke="{INK}" stroke-width="2.5"/>\n')
        parts.append(f'  <line x1="180" y1="240" x2="460" y2="240" stroke="{ACCENT}" stroke-width="1.5" stroke-dasharray="5 4"/>\n')
    parts.append(svg_footer())
    return "".join(parts)


def tools_svg(title: str, desc: str, labels: list[str]) -> str:
    w, h = 640, 420
    parts = [svg_header(w, h).format(title=title, desc=desc)]
    parts.append(wrap_title(title, 32, 44))
    cols = min(3, len(labels))
    box_w, box_h, gap = 160, 72, 24
    start_x = (w - (cols * box_w + (cols - 1) * gap)) // 2
    for i, lab in enumerate(labels[:9]):
        row, col = divmod(i, cols)
        x = start_x + col * (box_w + gap)
        y = 100 + row * (box_h + gap)
        parts.append(f'  <rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="4" fill="#FFFDF8" stroke="{INK}" stroke-width="1.8"/>\n')
        parts.append(
            f'  <text x="{x + box_w//2}" y="{y + box_h//2 + 5}" text-anchor="middle" '
            f'fill="{INK}" font-family="Helvetica, Arial, sans-serif" font-size="13">{lab}</text>\n'
        )
    parts.append(svg_footer())
    return "".join(parts)


def finish_svg(title: str, desc: str, rows: list[tuple[str, str, str]]) -> str:
    w, h = 640, 420
    parts = [svg_header(w, h).format(title=title, desc=desc)]
    parts.append(wrap_title(title, 32, 44))
    headers = ["Finish", "Repair", "Notes"]
    xs = [48, 220, 400]
    y0 = 100
    for i, hdr in enumerate(headers):
        parts.append(
            f'  <text x="{xs[i]}" y="{y0}" fill="{INK}" font-family="sans-serif" '
            f'font-size="14" font-weight="600">{hdr}</text>\n'
        )
    parts.append(f'  <line x1="40" y1="{y0+8}" x2="{w-40}" y2="{y0+8}" stroke="{GRID}" stroke-width="1"/>\n')
    for ri, (a, b, c) in enumerate(rows[:5]):
        y = y0 + 36 + ri * 52
        for i, cell in enumerate((a, b, c)):
            parts.append(
                f'  <text x="{xs[i]}" y="{y}" fill="{INK_LIGHT}" font-family="sans-serif" font-size="13">{cell}</text>\n'
            )
        parts.append(f'  <line x1="40" y1="{y+12}" x2="{w-40}" y2="{y+12}" stroke="{GRID}" stroke-width="0.8"/>\n')
    parts.append(svg_footer())
    return "".join(parts)


def process_svg(title: str, desc: str, steps: list[str]) -> str:
    w, h = 640, 420
    parts = [svg_header(w, h).format(title=title, desc=desc)]
    parts.append(wrap_title(title, 32, 44))
    n = len(steps)
    box_w = min(120, (w - 80) // n - 16)
    gap = 20
    total = n * box_w + (n - 1) * gap
    x = (w - total) // 2
    y = 200
    for i, step in enumerate(steps):
        bx = x + i * (box_w + gap)
        parts.append(f'  <rect x="{bx}" y="{y}" width="{box_w}" height="56" rx="6" fill="#FFFDF8" stroke="{INK}" stroke-width="1.8"/>\n')
        wrapped = textwrap.wrap(step, width=14)[:3]
        for j, line in enumerate(wrapped):
            parts.append(
                f'  <text x="{bx + box_w//2}" y="{y + 22 + j*14}" text-anchor="middle" '
                f'fill="{INK}" font-family="sans-serif" font-size="11">{line}</text>\n'
            )
        if i < n - 1:
            ax = bx + box_w + 4
            parts.append(f'  <line x1="{ax}" y1="{y+28}" x2="{ax+gap-8}" y2="{y+28}" stroke="{ACCENT}" stroke-width="2"/>\n')
            parts.append(f'  <polygon points="{ax+gap-8},{y+28} {ax+gap-14},{y+24} {ax+gap-14},{y+32}" fill="{ACCENT}"/>\n')
    parts.append(svg_footer())
    return "".join(parts)


JOINERY_VARIANT: dict[str, str] = {
    "mortise-and-tenon-basics": "mortise",
    "dovetail-layout": "dovetail",
    "half-blind-dovetails": "dovetail",
    "breadboard-ends": "breadboard",
    "drawer-fit-shimming": "drawer",
    "hinge-mortise-by-hand": "hinge",
    "wood-movement-across-grain": "movement",
    "seasonal-gaps-in-drawers": "drawer",
    "repair-loose-chair-wedged-tenon": "wedge",
    "sliding-dovetail-shelf": "sliding_dt",
    "torsion-box-shelf": "torsion",
    "pocket-hole-when-to-use": "pocket",
    "edge-banding-solid-wood": "default",
    "dowel-vs-biscuit": "default",
}


TOOL_LABELS: dict[str, list[str]] = {
    "hand-plane-setup": ["frog seat", "mouth", "cap iron", "chip breaker", "cutting iron", "lever cap"],
    "chisel-sharpening-jig": ["primary bevel", "micro-bevel", "flat back", "honing guide", "1000 stone", "strop"],
    "table-saw-fence-check": ["front gap", "rear gap", "blade plate", "adjust fence", "lock handles", "retest"],
    "block-plane-use": ["bevel up", "end grain", "low angle", "light pass", "bench hook", "stop block"],
    "marking-gauge-technique": ["stock face", "pin / knife", "score line", "knife wall", "waste side", "saw kerf"],
    "crosscut-sled": ["runners", "zero insert", "fence 90°", "stop block", "hold-down", "blade guard"],
    "router-table-setup": ["bit height", "fence face", "bearing", "push pad", "dust port", "test scrap"],
    "shop-dust-collection-layout": ["collector", "main trunk", "blast gates", "machine drops", "hose ID", "ground strap"],
    "bandsaw-blade-tension": ["tension knob", "drift line", "fence parallel", "blade guide", "thrust bearing", "resaw fence"],
    "shooting-board-build": ["hook stop", "fence 90°", "plane sole", "workpiece", "miter fence", "clamp rail"],
    "workbench-dog-holes": ["front row", "vise dog", "planing stop", "holdfast hole", "bench dogs", "tail vise"],
    "holdfast-workholding": ["shaft wedge", "bench top", "pad contact", "strike down", "twist release", "dog backup"],
    "carving-gouge-grind": ["outside bevel", "inside bevel", "heel", "sweep #", "strop", "tool roll"],
}


FINISH_ROWS: dict[str, list[tuple[str, str, str]]] = {
    "shellac-vs-polyurethane": [
        ("Shellac", "Easy", "Alcohol repair; heat sensitive"),
        ("Polyurethane", "Hard", "Spot repair needs abrade"),
        ("Oil + varnish", "Moderate", "In-the-wood look"),
    ],
    "oil-finish-maintenance": [
        ("Boiled linseed", "Wipe yearly", "Cure slow; rags fire risk"),
        ("Tung oil", "Light refresh", "Water resistance builds"),
        ("Hardwax oil", "Factory recoat", "Follow vendor interval"),
    ],
    "dowel-vs-biscuit": [
        ("Dowel", "Strong", "Drill alignment critical"),
        ("Biscuit", "Moderate", "Face registration only"),
        ("Domino", "Strong+", "Machine dependent"),
    ],
    "card-scraper-vs-sanding": [
        ("Card scraper", "Local", "Fixes tear-out"),
        ("180 sand", "Blend", "Unifies surface"),
        ("220 sand", "Pre-finish", "Before first coat"),
    ],
    "french-polish-overview": [
        ("Pad rubber", "N/A", "Shellac + oil slip"),
        ("1 lb cut", "Easy", "Build slow"),
        ("3 lb cut", "Moderate", "Padding only"),
    ],
    "milk-paint-on-primer": [
        ("Sizing", "N/A", "Bond to raw wood"),
        ("Milk paint", "Repaint", "Two thin coats"),
        ("Topcoat", "Optional", "Wax or water poly"),
    ],
    "wax-over-shellac": [
        ("Shellac seal", "Alcohol", "2–3 lb cut typical"),
        ("Paste wax", "Buff", "Low sheen handle"),
        ("Renew wax", "Easy", "No full strip"),
    ],
    "finishing-outdoor-furniture": [
        ("Teak oil", "Annual", "Thin builds"),
        ("Exterior poly", "Moderate", "Peels if too thick"),
        ("Paint + primer", "Repaint", "Film protection"),
    ],
}


PROCESS_STEPS: dict[str, list[str]] = {
    "water-pop-before-finish": ["Wipe water", "Dry", "220 sand", "Seal coat"],
    "sanding-grit-sequence": ["80", "120", "150", "180", "220"],
    "glue-up-clamping-strategy": ["Dry fit", "Glue long joint", "Cauls on", "Square check"],
    "case-dry-fit": ["Strap clamps", "Square", "Flush rails", "Hardware clear"],
    "steam-bending-form": ["Steam", "Bend over", "Strap", "Cool on form"],
    "resawing-veneer": ["Joint face", "Bandsaw resaw", "Book match", "Sticker dry"],
    "tabletop-flattening": ["Winding sticks", "Diagonal plane", "With grain", "Edge joint"],
    "lumber-milling-order": ["Face joint", "Edge joint", "Rip width", "Thickness"],
    "choosing-hardwood-boards": ["Defect map", "Grain for part", "Yield nest", "Stick stack"],
    "reading-grain-for-planing": ["Read cathedral", "Test pass", "Reverse patch", "Light finish pass"],
    "curved-apron-template": ["Fair curve", "Template", "Pattern bit", "Hand fair"],
}


def graphic_filename(kind: GraphicKind) -> str:
    return {
        "joinery": "joinery-diagram.svg",
        "tools": "tool-layout.svg",
        "finish": "finish-comparison.svg",
        "process": "process-flow.svg",
    }[kind]


def build_svg(article: Article) -> str:
    slug = article.slug
    if article.kind == "joinery":
        return joinery_svg(article.graphic_title, article.caption, JOINERY_VARIANT.get(slug, "default"))
    if article.kind == "tools":
        return tools_svg(article.graphic_title, article.caption, TOOL_LABELS.get(slug, ["tool", "setup", "check", "adjust", "test", "repeat"]))
    if article.kind == "finish":
        rows = FINISH_ROWS.get(slug, [("Option A", "Moderate", "Notes"), ("Option B", "Easy", "Notes")])
        return finish_svg(article.graphic_title, article.caption, rows)
    steps = PROCESS_STEPS.get(slug, ["Prep", "Work", "Check", "Finish"])
    return process_svg(article.graphic_title, article.caption, steps)


def draft_markdown(article: Article, svg_name: str) -> str:
    num = f"{article.num:02d}"
    rel = f"../assets/{article.slug}/{svg_name}"
    tags_yaml = "\n".join(f"  - {t}" for t in article.tags)
    body = textwrap.dedent(
        f"""
---
title: "{article.title}"
slug: {article.slug}
meta_description: "{article.meta}"
author: BBF Shop
tags:
{tags_yaml}
images:
  - path: "D:\\\\BBF"
    caption: "{article.photo_caption}"
    source: ours
    status: staged
graphic:
  primary: "assets/{article.slug}/{svg_name}"
  alt: "{article.graphic_title}"
status: draft
voice_check: human
pillar: furniture-craft
priority: {article.num}
---

{article.title} — working notes for the shop. Measure on your stock; humidity and species move the numbers.

## At the bench

Use the diagram as the layout reference. Mark waste sides before any saw cut. Dry-fit twice when shoulders must close at the same time.

<figure class="craft-figure">
  <img src="{rel}" alt="{article.graphic_title}" width="640" height="420" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> {article.caption}</figcaption>
</figure>

## Photo slot (staged)

**Staged only** — drop a `{article.slug}` frame from `D:\\BBF` when the shot is captioned and color-corrected. Do not publish catalog pulls.

## Checklist

- Layout lines are knife-deep where saws must register.
- Test fit without glue; note where light shows through.
- Finish samples on offcuts from the same milling session.

"""
    ).strip() + "\n"
    return body


def graphics_index_lines() -> str:
    lines = [
        "# GRAPHICS_INDEX — furniture-craft-blog",
        "",
        "Magazine craft line art (cream `#F7F3E8`, ink `#1A1A1A`). SVG under `assets/<slug>/`.",
        "Photo placeholders point at **`D:\\BBF`** (staged shop shots only).",
        "",
        "| # | Slug | Graphic type | Asset |",
        "|---:|---|---|---|",
    ]
    for a in ARTICLES:
        fn = graphic_filename(a.kind)
        lines.append(f"| {a.num} | `{a.slug}` | {a.kind} | `assets/{a.slug}/{fn}` |")
    lines.extend(
        [
            "",
            "## Regenerate",
            "",
            "```bash",
            "python3 tools/generate_furniture_craft_blog_graphics.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_supporting_docs() -> None:
    style = BLOG / "STYLE_GUIDE.md"
    style.write_text(
        textwrap.dedent(
            """# Furniture craft blog — STYLE_GUIDE

Evergreen shop copy for BBF / furniture craft articles. Not COSMOS core.

## Voice

Bench-first: measurements you can act on, species named when it matters, no influencer filler.

## Figures

- Primary diagrams are SVG in `assets/<slug>/`.
- HTML `<figure>` with numbered caption in each draft.
- Shop photos: **`D:\\BBF`** only, staged and captioned before publish.

## Ban list

Same class as other content packs: no "delve", "robust", "journey", "game-changer", or symmetric three-tip filler.

"""
        ),
        encoding="utf-8",
    )
    (BLOG / "INDEX.md").write_text(
        "# Furniture craft blog — INDEX\n\n"
        f"{len(ARTICLES)} drafts in `drafts/`. See `GRAPHICS_INDEX.md` for diagram inventory.\n",
        encoding="utf-8",
    )
    (BLOG / "PHOTO_MANIFEST.md").write_text(
        "# PHOTO_MANIFEST — D:\\BBF (staged)\n\n"
        "Use real shop frames only. Staged folder on KC-PC: `D:\\BBF`.\n\n"
        "Pair each draft slug with a matching shot after color correction.\n",
        encoding="utf-8",
    )


def main() -> None:
    DRAFTS.mkdir(parents=True, exist_ok=True)
    write_supporting_docs()
    for article in ARTICLES:
        adir = ASSETS / article.slug
        adir.mkdir(parents=True, exist_ok=True)
        fn = graphic_filename(article.kind)
        svg_path = adir / fn
        svg_path.write_text(build_svg(article), encoding="utf-8")
        draft_path = DRAFTS / f"{article.num:02d}-{article.slug}.md"
        draft_path.write_text(draft_markdown(article, fn), encoding="utf-8")
    (BLOG / "GRAPHICS_INDEX.md").write_text(graphics_index_lines(), encoding="utf-8")
    print(f"Wrote {len(ARTICLES)} drafts and SVG sets under {BLOG}")


if __name__ == "__main__":
    main()
