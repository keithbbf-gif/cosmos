#!/usr/bin/env python3
"""Generate shop SVG diagrams for content/furniture-finishing-chemistry/."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "furniture-finishing-chemistry"
ASSETS = PACK / "assets"

CREAM = "#F7F3E8"
INK = "#1A1A1A"
INK_LIGHT = "#4A4A4A"
ACCENT = "#6B4423"
GRID = "#D4C9B0"


@dataclass(frozen=True)
class DraftGraphic:
    slug: str
    title: str
    alt: str
    caption: str
    diagram_title: str
    rows: tuple[tuple[str, str, str], ...]  # col1, col2, col3


GRAPHICS: list[DraftGraphic] = [
    DraftGraphic(
        "what-a-finish-actually-is",
        "Three jobs of a furniture finish",
        "Diagram: evaporation, binder solidification, and adhesion on sanded wood",
        "Evaporation is fast; crosslinking or coalescence builds the film; adhesion decides whether the board keeps it.",
        "Three jobs, one surface",
        (
            ("Step", "Mechanism", "Shop tell"),
            ("Carrier leaves", "Water, alcohol, or mineral spirits evaporates", "Can feels empty; film may still be soft"),
            ("Binder solidifies", "Oxygen cure, coalescence, or resin reunion", "Napkin test fails when it should"),
            ("Stays attached", "Mechanical bite + chemical stick", "Peel at edge = prep or compatibility"),
        ),
    ),
    DraftGraphic(
        "film-versus-penetrating",
        "Penetrating oil versus surface film",
        "Cross-section: oil in pores versus varnish skin on wood surface",
        "Penetrating systems wet fibers; film systems form a measurable skin — most cans do both and hide the ratio.",
        "Film versus penetrating (section)",
        (
            ("Family", "Where protection lives", "Repair tell"),
            ("Penetrating oil", "In surface pores, little crust", "Scuff-in refresh hides wear"),
            ("Thin film", "On top, mils not hope", "Scratch is a line in a skin"),
            ("Mutt (wipe-on varnish)", "Film applied like oil", "Same binder, different schedule"),
        ),
    ),
    DraftGraphic(
        "binder-solvent-additive",
        "Anatomy of a finish can",
        "Labeled diagram: binder, carrier solvent, and additives in a commercial finish",
        "The label sells feeling; the SDS lists nouns — the shop must know which noun does the work on this board.",
        "Can anatomy",
        (
            ("Layer", "Role", "Read on the label"),
            ("Binder", "Becomes the solid", "Oil, alkyd, acrylic, shellac, casein"),
            ("Carrier", "Gets it onto wood", "Water, MS, alcohol, blend"),
            ("Helpers", "Modify behavior", "Driers, coalescent, flatteners, UV absorbers"),
        ),
    ),
    DraftGraphic(
        "why-some-woods-drink-and-some-spit",
        "Porous oak versus resinous teak",
        "Diagram: open pores versus oily extractives blocking finish penetration",
        "Ring-porous woods drink; oily exotics spit — extractives are a sealer you did not apply.",
        "Drink versus spit",
        (
            ("Wood type", "Surface behavior", "Prep habit"),
            ("Ring-porous oak", "Finishes sink unevenly", "Seal or accept honest pore"),
            ("Diffuse maple", "Predictable film", "Grain raise on waterborne"),
            ("Oily teak / rosewood", "Finish beads or fisheyes", "Degrease, test, do not assume oil"),
        ),
    ),
    DraftGraphic(
        "the-shop-safe-fence",
        "Shop-safe content fence",
        "Flowchart: allowed commercial finishing practice versus out-of-scope formulation",
        "This series explains labeled products and ventilation — not distillation, synthesis, or hazmat evasion.",
        "Shop-safe fence",
        (
            ("In scope", "Out of scope", "Why"),
            ("Read labels & films", "Cook resins or solvents", "Safety and law"),
            ("Ventilation & rags", "Dump waste", "Ordinary shop duty"),
            ("Test unknown old coats", "Strip lead without PPE", "Health, not bravado"),
        ),
    ),
    DraftGraphic(
        "linseed-oil-polymerizes",
        "Linseed oil oxygen cure",
        "Diagram: linoleic acid crosslinks with atmospheric oxygen into a solid network",
        "Raw linseed polymerizes slowly; heat-bodied and alkyd systems trade open time for hardness.",
        "Linseed polymerization",
        (
            ("Stage", "Chemistry (plain)", "Shop clock"),
            ("Wipe-on", "Thin layer meets air", "Touch-dry hours; cure weeks"),
            ("Pooled oil", "Skin over wet center", "Wrinkle, bloom, fire risk in rags"),
            ("Over raw wood", "Penetration + surface cure", "Feeding schedule, not one flood"),
        ),
    ),
    DraftGraphic(
        "tung-oil-and-the-can-that-lied",
        "Tung oil label versus polymerizing oil",
        "Comparison: true tung polymerization versus wiping varnish labeled tung oil",
        "A can that says tung may be varnish thinned for wiping — read the binder, not the front panel romance.",
        "Tung oil: label versus binder",
        (
            ("Product", "Binder truth", "Cure behavior"),
            ("Pure tung", "Eleostearic acid, slow", "Harder; long cure; rags dangerous"),
            ("Tung oil finish (trade)", "Often alkyd or urethane", "Faster build; film possible"),
            ("Danish / antique oil", "Wiping varnish family", "Mutt — see Danish oil draft"),
        ),
    ),
    DraftGraphic(
        "danish-oil-is-a-wiping-varnish",
        "Danish oil as wiping varnish",
        "Diagram: thin alkyd or urethane in mineral spirits wiped like oil",
        "Danish oil is usually a film binder in a wiping carrier — the rag is the same; the chemistry is not linseed alone.",
        "Danish oil composition",
        (
            ("Fraction", "Typical role", "If misused"),
            ("Resin / varnish", "Builds skin when stacked", "Cloudy thick film"),
            ("Mineral spirits", "Open time, penetration aid", "Flash-off drives recoat"),
            ("Linseed or tung fraction", "Marketing and flexibility", "Still a mutt"),
        ),
    ),
    DraftGraphic(
        "hardwax-oil-the-wax-is-the-last-coat",
        "Hardwax oil layers",
        "Diagram: oil penetration with wax occupying surface pores",
        "Oil wets fiber; wax occupies the last microns — pile it on and you get a soft cloudy film.",
        "Hardwax oil stack",
        (
            ("Layer", "Function", "Maintenance"),
            ("Oil phase", "Penetrates, crosslinks lightly", "Refresh wipe when dull"),
            ("Wax phase", "Surface slip and mark resistance", "Buff; do not stack endlessly"),
            ("Over-build", "Soft haze", "Strip back or live with fingerprints"),
        ),
    ),
    DraftGraphic(
        "a-curing-schedule-that-respects-oxygen",
        "Oil cure schedule versus oxygen",
        "Timeline: wipe coats with air gaps versus stacked wet coats",
        "Oxygen reaches only the exposed surface — schedule thin coats and dry rags, not heroic puddles.",
        "Oxygen-respecting schedule",
        (
            ("Day", "Action", "Avoid"),
            ("0", "First thin wipe, off overnight", "Pooled corners"),
            ("1–3", "Second wipe if dry", "Stacking before center cured"),
            ("Week+", "Light use; full cure later", "Closed cabinets on wet oil"),
        ),
    ),
    DraftGraphic(
        "bloom-wrinkle-and-the-rag-that-never-dries",
        "Oil bloom and wrinkle defects",
        "Diagram: wrinkled skin over uncured oil versus bloom haze",
        "Wrinkle is too much oil too little air; bloom is moisture or incompatible stack — both are chemistry, not bad luck.",
        "Bloom and wrinkle",
        (
            ("Defect", "Likely cause", "Response"),
            ("Wrinkle", "Thick wet coat", "Strip back; thin schedule"),
            ("Bloom", "Moisture or bad recoat", "Identify layer; strip isolate"),
            ("Warm rag", "Exothermic cure in pile", "Water bucket or lay flat dry"),
        ),
    ),
    DraftGraphic(
        "oil-on-teak-rosewood-and-other-greasy-citizens",
        "Finishing oily exotic hardwoods",
        "Diagram: surface extractives repelling film finish",
        "Natural oils in teak and rosewood fight adhesion — degrease, seal, test, never assume the first coat stuck.",
        "Oily wood prep",
        (
            ("Step", "Purpose", "Skip at your peril"),
            ("Fresh plane / sand", "Opens clean surface briefly", "Old wax still there"),
            ("Solvent wipe", "Removes exudate", "Re-oils before next coat"),
            ("Test panel", "Proves adhesion", "Full table as experiment"),
        ),
    ),
    DraftGraphic(
        "alkyd-varnish-the-shop-standard",
        "Alkyd varnish oil length",
        "Diagram: short oil alkyd versus long oil flexibility",
        "Oil length trades hardness for flexibility — table tops and chairs want different alkyd conversations.",
        "Alkyd oil length",
        (
            ("Oil length", "Film character", "Typical use"),
            ("Short", "Harder, less flex", "Cabinets, trim"),
            ("Medium", "Shop default", "Mixed furniture"),
            ("Long", "More flex, slower", "Exterior-ish, heavy movement"),
        ),
    ),
    DraftGraphic(
        "oil-modified-polyurethane-without-the-marketing",
        "Oil-modified polyurethane structure",
        "Diagram: urethane links with oil-modified segments in one film",
        "Oil-mod poly is still a thermoset film — the oil softens marketing, not the scratch test.",
        "Oil-modified polyurethane",
        (
            ("Claim", "Reality", "Shop test"),
            ("Plastic armor", "Crosslinked urethane film", "White scratch line"),
            ("Oil warmth", "Modified segments, amber", "Still a skin repair"),
            ("One coat miracle", "Build + cure schedule", "Use board, not can copy"),
        ),
    ),
    DraftGraphic(
        "spar-varnish-and-porch-chalk",
        "Spar varnish UV and flex additives",
        "Diagram: UV absorbers and longer oil in spar versus interior alkyd",
        "Spar trades indoor hardness for UV help and movement — on a dining table it often chalks instead of protecting.",
        "Spar versus interior varnish",
        (
            ("Property", "Spar tendency", "Interior alkyd"),
            ("UV packages", "More absorbers", "Less exterior focus"),
            ("Flex", "Longer oil", "Harder for tabletops"),
            ("Wrong use", "Chalky porch film indoors", "Better interior system"),
        ),
    ),
    DraftGraphic(
        "wipe-on-varnish-is-just-thin-varnish",
        "Wipe-on versus brushed varnish thickness",
        "Diagram: many thin wiped coats building mils slowly",
        "Wipe-on is the same binder thinned — patience builds mils without runs; impatience builds dust nibs anyway.",
        "Wipe-on build",
        (
            ("Coat", "Typical thickness", "Note"),
            ("Wiped", "Thin, even", "More coats, less run"),
            ("Brushed", "Heavier per pass", "Leveling matters"),
            ("Either", "Same recoat window rules", "Label is not a new chemistry"),
        ),
    ),
    DraftGraphic(
        "recoat-windows-and-intercoat-adhesion",
        "Varnish recoat window",
        "Timeline: sand lightly after cure versus strip when amorphous",
        "Inside the window, chemical bite; outside it, mechanical tooth — miss both and the coat floats.",
        "Recoat window",
        (
            ("Timing", "Surface", "Next coat"),
            ("Fresh window", "Slightly soft", "Chemical bond"),
            ("Cured gloss", "Hard", "Scuff or abrade"),
            ("Contaminated", "Silicone, wax", "Strip isolate — fisheye country"),
        ),
    ),
    DraftGraphic(
        "amber-plastic-and-the-look-people-return",
        "Amber alkyd versus water-white acrylic",
        "Side-by-side appearance: warm amber varnish versus clear waterborne on maple",
        "Amber is oxidizing alkyd honesty; water-white is acrylic on pale woods — neither is virtue, both are choices.",
        "Amber versus clear film",
        (
            ("Finish", "Color cast", "When it wins"),
            ("Traditional alkyd", "Warm amber over time", "Walnut, cherry, antique mood"),
            ("Waterborne acrylic", "Minimal cast", "Maple, ash, modern pale"),
            ("Client ask", "Match existing room", "Sample on species, not on pine strip"),
        ),
    ),
    DraftGraphic(
        "shellac-is-a-bug-resin",
        "Shellac flake dissolved in alcohol",
        "Diagram: lac flakes in denatured alcohol forming shellac solution",
        "Shellac is a natural resin in alcohol — fast dry, reversible repair, honest limits on water and heat.",
        "Shellac solution",
        (
            ("Form", "Carrier", "Film trait"),
            ("Blonde / orange flake", "Denatured alcohol", "Dries fast; repair with alcohol"),
            ("Waxed flake", "Same", "Intercoat stick; dewax for stack"),
            ("Fresh mix", "Weeks pot life", "Old jar gels — remix"),
        ),
    ),
    DraftGraphic(
        "cuts-flakes-and-why-dewaxed-exists",
        "Shellac pound cut chart",
        "Table: one-pound through four-pound cut uses and dewaxed stacking",
        "Pound cut is pounds per gallon — sealer low, French polish high; dewaxed for anything stacked over shellac.",
        "Shellac pound cuts",
        (
            ("Cut", "Typical use", "Wax note"),
            ("1 lb", "Wash sealer", "Waxed OK under same"),
            ("2 lb", "General sealing", "Dewax before dissimilar topcoat"),
            ("3–4 lb", "Pad build, polish", "Burnish, not flood"),
        ),
    ),
    DraftGraphic(
        "french-polish-without-the-monastery",
        "French polish pad layers",
        "Diagram: shellac and oil in a pad building thin shellac film",
        "French polish is many thin shellac passes with a lubricated pad — a film so thin people argue if it is a film.",
        "French polish stack",
        (
            ("Pass", "Material", "Risk"),
            ("Shellac in pad", "Ultra-thin build", "Stick if too much oil"),
            ("Olive / mineral oil", "Lubricate pad", "Cloud if trapped"),
            ("Body coat", "Burnished gloss", "Heat and water sensitive"),
        ),
    ),
    DraftGraphic(
        "shellac-as-the-diplomat",
        "Shellac between dissimilar coats",
        "Stack diagram: shellac sealer between stain and waterborne or wax and varnish",
        "Shellac isolates incompatible layers when dewaxed and cured — it is a diplomat, not a universal miracle.",
        "Shellac barrier coat",
        (
            ("Below", "Shellac role", "Above"),
            ("Oily or waxy wood", "Blocks bleed", "Waterborne or lacquer class"),
            ("Pigment stain", "Locks color", "Clear film"),
            ("Unknown old finish", "Test first", "Anything — test still required"),
        ),
    ),
    DraftGraphic(
        "blush-alcohol-and-a-humid-tuesday",
        "Shellac blush in humid air",
        "Diagram: moisture trapped in drying shellac forming white haze",
        "Blush is water in a drying alcohol film — move air, reduce humidity, or add retarder; do not keep padding blindly.",
        "Shellac blush",
        (
            ("Condition", "Film state", "Fix"),
            ("High RH", "Moisture trapped", "Dehumidify; warm dry air"),
            ("Cold shellac", "Slow evaporation", "Warm room; fresh mix"),
            ("Heavy coat", "More trapped water", "Thin passes"),
        ),
    ),
    DraftGraphic(
        "what-shellac-cannot-survive",
        "Shellac limits: water, heat, alcohol",
        "Table of shellac failure modes on tabletops and rings",
        "Shellac is repairable because it redissolves — that same trait loses to hot mugs and wet glasses.",
        "Shellac honest limits",
        (
            ("Attack", "Symptom", "Shop speech"),
            ("Hot wet cup", "White ring", "Not a bar-top finish"),
            ("Alcohol drink", "Sticky or dull spot", "Choose harder topcoat"),
            ("Exterior UV", "Quick breakdown", "Use exterior system instead"),
        ),
    ),
    DraftGraphic(
        "waterborne-means-emulsion",
        "Waterborne emulsion particles",
        "Diagram: acrylic or PU particles in water coalescing after evaporation",
        "Water leaves first; particles must coalesce — touch-dry is not hard, and cold shops fail the knit silently.",
        "Waterborne coalescence",
        (
            ("Phase", "What happens", "Misread"),
            ("Wet", "Water + surfactant + particles", "Looks like paint"),
            ("Touch-dry", "Water mostly gone", "Not yet hard"),
            ("Coalesced", "Continuous film", "Tape test on schedule"),
        ),
    ),
    DraftGraphic(
        "grain-raise-is-swelling",
        "Grain raise from waterborne wetting",
        "Diagram: fibers swell then sand back before topcoats",
        "Water swells cellulose — first coat raises grain; cutting back once beats fighting raised fibers under clear.",
        "Grain raise sequence",
        (
            ("Step", "Surface", "Tool"),
            ("First water coat", "Fibers stand", "Dry fully"),
            ("Cut back", "Knock tops", "320–400 on raised only"),
            ("Seal coats", "Smooth under film", "Do not skip raise pass"),
        ),
    ),
    DraftGraphic(
        "acrylic-versus-waterborne-polyurethane",
        "Acrylic versus waterborne polyurethane",
        "Comparison table: clarity, hardness, and repair of acrylic vs PUD",
        "Acrylic stays clearer on pale woods; waterborne PU trades a little cast for toughness — read the binder on the label.",
        "Acrylic vs waterborne PU",
        (
            ("Type", "Clarity", "Wear"),
            ("Acrylic emulsion", "High on maple", "Good; thermoplastic when soft"),
            ("Waterborne PU (PUD)", "Slight warm cast", "Tougher film"),
            ("Hybrid label", "Read SDS binder", "Do not trust front panel alone"),
        ),
    ),
    DraftGraphic(
        "coalescent-cold-shops-and-the-film-that-never-knits",
        "MFFT and cold shop coalescence failure",
        "Diagram: film formation temperature versus cold garage finish powdering",
        "Below minimum film formation temperature, particles never knit — the dust you can scrape off was never a finish.",
        "MFFT in a cold shop",
        (
            ("Shop temp", "Particle behavior", "Result"),
            ("Above MFFT", "Coalesce", "Continuous film"),
            ("Marginal", "Partial knit", "Soft, poor solvent hold"),
            ("Cold garage", "Powdery", "Scrape test fails — re-coat warm"),
        ),
    ),
    DraftGraphic(
        "waterborne-over-oil-the-honest-sequence",
        "Stacking waterborne over cured oil",
        "Layer diagram: fully cured thin oil then dewaxed shellac or approved sealer then waterborne",
        "Waterborne over sticky oil is adhesion fiction — cure the oil, isolate if needed, test the stack on a board.",
        "Waterborne over oil stack",
        (
            ("Layer", "Requirement", "Skip = peel"),
            ("Oil", "Fully cured, wiped", "Tacky oil under WB"),
            ("Barrier (if needed)", "Dewaxed shellac or label sealer", "Direct WB on oil"),
            ("Waterborne", "Within recoat rules", "Heavy first coat on raise"),
        ),
    ),
    DraftGraphic(
        "foam-leveling-and-the-cheap-applicator",
        "Foam applicator versus brush leveling",
        "Diagram: foam leaving bubbles versus bristle laying a level wet film",
        "Foam puts air in the film; cheap foam puts more — a level brush or pad beats a heroic single flood.",
        "Applicator and leveling",
        (
            ("Tool", "Risk", "Mitigation"),
            ("Cheap foam", "Bubbles, telegraph", "Quality foam; light coats"),
            ("Synthetic brush", "Brush marks if thick", "Thin passes, tip off"),
            ("Spray (pro booth)", "Different class", "Not a garage default"),
        ),
    ),
    DraftGraphic(
        "milk-paint-is-casein-and-lime",
        "Milk paint casein and lime set",
        "Diagram: casein protein and lime forming insoluble calcium caseinate film",
        "Real milk paint sets by protein chemistry — chalky matte unless the can quietly became acrylic latex.",
        "Casein-lime set",
        (
            ("Ingredient", "Role", "Finish look"),
            ("Casein", "Protein binder", "Matte, opaque"),
            ("Lime", "Insolubilize protein", "Chalk hand"),
            ("Acrylic milk paint", "Latex film", "Less true chalk — read label"),
        ),
    ),
    DraftGraphic(
        "bonding-coats-and-the-myth-of-universal-stick",
        "Bonding coat on slick substrates",
        "Diagram: bonding primer between old finish and milk paint",
        "Universal stick is marketing — slick or glossy needs a bonding coat matched to the topcoat system.",
        "Bonding coat",
        (
            ("Substrate", "Problem", "Bonding coat job"),
            ("Raw wood", "Often none", "First milk coat bites"),
            ("Old poly", "Slick skin", "Sand + compatible bond coat"),
            ("Wax / silicone", "Reject everything", "Strip or isolate — no magic can"),
        ),
    ),
    DraftGraphic(
        "milk-paint-over-an-old-film",
        "Milk paint over existing finish",
        "Cross-section: chalky paint on sanded or bonded old varnish",
        "Milk paint is a film on a film — prep and bond coat decide whether it chips in a week or reads as history.",
        "Milk paint over old film",
        (
            ("Prep", "Goal", "Failure mode"),
            ("Degloss sand", "Mechanical tooth", "Peel sheets"),
            ("Bond coat", "Chemical stick", "Chip at edges"),
            ("Milk coats", "Matte build", "Too thick = crackle theater"),
        ),
    ),
    DraftGraphic(
        "topcoating-milk-paint-without-killing-the-chalk",
        "Clear topcoat over milk paint",
        "Diagram: wax or thin waterborne over chalky milk paint sheen change",
        "Any clear wets pigment and changes hand — wax keeps more chalk than thick poly, which flattens to plastic.",
        "Topcoat over milk paint",
        (
            ("Topcoat", "Chalk kept?", "Tradeoff"),
            ("Paste wax", "Most chalk", "Less spill protection"),
            ("Thin waterborne", "Some chalk", "Test sheen shift"),
            ("Heavy poly", "Kills chalk", "Armor, not milk look"),
        ),
    ),
    DraftGraphic(
        "chip-and-crackle-defect-history-or-theater",
        "Intentional crackle versus adhesion chip",
        "Diagram: controlled crackle medium versus edge chip from poor bond",
        "Crackle can be a product layer; chip at an edge is usually prep — know which you are selling.",
        "Chip versus crackle",
        (
            ("Look", "Cause", "Fix"),
            ("Crackle glaze", "Intentional breakup", "Part of design"),
            ("Edge chip", "Bad bond / flex", "Strip zone, prep right"),
            ("Random flaking", "Incompatible stack", "Compatibility draft — test"),
        ),
    ),
    DraftGraphic(
        "sanding-decides-the-film",
        "Grit sequence before film finish",
        "Process: progressive grits ending before first sealer coat",
        "The finish only hides sanding you already chose to keep — skip grits and the film telegraphs them.",
        "Sanding before film",
        (
            ("Grit", "Removes", "Stop before"),
            ("80–120", "Mill marks", "Leaving deep tracks"),
            ("150–180", "Previous scratch", "First sealer on raw"),
            ("220+", "Intercoat only", "Polishing closed pore too soon"),
        ),
    ),
    DraftGraphic(
        "dye-stain-and-the-finish-on-top",
        "Dye under film finish stack",
        "Layer diagram: dye in fiber, gel stain in pore, clear coats on top",
        "Dye moves in fiber; pigment sits in pore — the finish on top locks whichever story you told.",
        "Color under clear",
        (
            ("Color", "Sits where", "Finish note"),
            ("Dye", "In cell walls", "Seal before uneven blot"),
            ("Pigment stain", "In pores mainly", "Wipe back before clear"),
            ("Glaze", "On sealed surface", "Topcoat locks it"),
        ),
    ),
    DraftGraphic(
        "compatibility-in-prose",
        "Finish compatibility matrix (simplified)",
        "Table: oil, shellac, varnish, waterborne, milk paint stacking rules",
        "When in doubt, isolate with dewaxed shellac or strip to a known layer — prose beats a universal chart, but tests beat prose.",
        "Compatibility sketch",
        (
            ("Stack", "Rule of thumb", "Verify"),
            ("Water over oil", "Cured oil + test; often barrier", "Use board, not table"),
            ("Milk over poly", "Sand + bond coat", "Chip at edge = prep"),
            ("Shellac diplomat", "Dewaxed between fights", "Still test unknown old"),
        ),
    ),
    DraftGraphic(
        "repair-without-stripping-the-whole-piece",
        "Spot repair versus full strip",
        "Diagram: feather sand local zone blend into cured film",
        "Local repair needs the same binder and feathered edge — strip a zone when chemistry does not redissolve.",
        "Spot repair",
        (
            ("Damage", "Strategy", "When to strip zone"),
            ("Surface scratch", "Abrade + same finish", "Through color"),
            ("Peel patch", "Feather edge", "Unknown undercoat"),
            ("Shellac ring", "Pad alcohol locally", "Large water damage"),
        ),
    ),
    DraftGraphic(
        "maintenance-years-later",
        "Maintenance refresh cycles by finish family",
        "Timeline: oil feed, wax buff, varnish recoat, waterborne scuff-recoat",
        "Every finish family has a maintenance sentence — say it at sale or the client will invent a wrong one.",
        "Maintenance by family",
        (
            ("Family", "Years later", "Refresh"),
            ("Penetrating oil", "Dull, marks", "Wipe same oil"),
            ("Wax on shellac", "Dry handle", "Clean, thin wax"),
            ("Film varnish / WB", "Wear through", "Scuff + coat or pro"),
        ),
    ),
    DraftGraphic(
        "rags-air-and-the-fire-you-do-not-see-coming",
        "Oil-soaked rag spontaneous combustion",
        "Triangle diagram: oily rag, oxygen, insulated pile heat",
        "Linseed and alkyd rags oxidize exothermically — flat dry or submerged, never a warm crumpled pile in the trash.",
        "Rag fire triangle",
        (
            ("Factor", "Shop rule", "Never"),
            ("Oily rag", "Lay flat or water bucket", "Ball in trash can"),
            ("Pile heat", "Insulation holds exotherm", "Closed lid on wet rags"),
            ("Ventilation", "Reduces vapor load", "Spray in unvented closet"),
        ),
    ),
    DraftGraphic(
        "food-safe-is-a-sentence-not-a-halo",
        "Food contact and cured film",
        "Diagram: fully cured film versus uncured surface on cutting board (conceptual)",
        "Food-safe is a regulatory sentence about cured film — not a license for uncured polyurethane on a cutting board.",
        "Food contact clarity",
        (
            ("Claim", "Means", "Does not mean"),
            ("FDA cleared additive", "In specific cured system", "Eat off any wet coat"),
            ("Beeswax board butter", "Surface maintain", "Substitute for cure schedule"),
            ("Client ask", "State limits plainly", "Magic halo label"),
        ),
    ),
    DraftGraphic(
        "fisheye-crater-orange-peel",
        "Fisheye, crater, and orange peel defects",
        "Diagram: silicone contamination fisheye versus thick spray orange peel",
        "Fisheye is contamination; orange peel is flow — different sins, different fixes, same ruined first impression.",
        "Finish surface defects",
        (
            ("Defect", "Likely cause", "Direction"),
            ("Fisheye", "Silicone / oil contam", "Clean, isolate, barrier"),
            ("Crater", "Dirty air / water in oil", "Filter, strain, prep"),
            ("Orange peel", "Too thick, cold, fast", "Thin coat, heat, level"),
        ),
    ),
    DraftGraphic(
        "a-staged-dining-table-schedule",
        "Dining table finish schedule",
        "Gantt-style shop schedule: sand, seal, color, build coats, cure before delivery",
        "A table schedule names dry times and use limits — delivery before cure is a refund waiting to happen.",
        "Table finish schedule",
        (
            ("Day", "Step", "Client use"),
            ("0–1", "Sand, seal, raise cut", "Hands off"),
            ("2–4", "Color + build coats", "No dishes"),
            ("7–14+", "Cure per label", "Glasses with care → normal"),
        ),
    ),
    DraftGraphic(
        "what-to-tell-a-client-who-wants-just-oil",
        "Client conversation: oil look versus film need",
        "Flow: client wants oil → use questions → maintenance plan or film compromise",
        "Give them the honest fork: oil look with maintenance, or film with a different repair story — write the plan before the deposit.",
        "Client oil conversation",
        (
            ("Client says", "You answer with", "Document"),
            ("Just oil", "Use and refresh schedule", "Maintenance sheet"),
            ("No plastic", "Oil still polymerizes", "Sample board abuse test"),
            ("No maintenance", "Film or hardwax speech", "Signed scope, not argument"),
        ),
    ),
]


def svg_table(g: DraftGraphic) -> str:
    rows_html = []
    y = 136
    for i, (c1, c2, c3) in enumerate(g.rows):
        if i == 0:
            continue
        rows_html.append(
            f'  <text x="48" y="{y}" fill="{INK_LIGHT}" font-family="sans-serif" font-size="13">{_esc(c1)}</text>\n'
            f'  <text x="220" y="{y}" fill="{INK_LIGHT}" font-family="sans-serif" font-size="13">{_esc(c2)}</text>\n'
            f'  <text x="400" y="{y}" fill="{INK_LIGHT}" font-family="sans-serif" font-size="13">{_esc(c3)}</text>\n'
            f'  <line x1="40" y1="{y + 12}" x2="600" y2="{y + 12}" stroke="{GRID}" stroke-width="0.8"/>'
        )
        y += 52
    header = g.rows[0]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 420" width="640" height="420" role="img" aria-labelledby="title desc">
  <title id="title">{_esc(g.diagram_title)}</title>
  <desc id="desc">{_esc(g.alt)}</desc>
  <rect width="100%" height="100%" fill="{CREAM}"/>
  <text x="32" y="44" fill="{INK}" font-family="Georgia, serif" font-size="20" font-weight="600">{_esc(g.diagram_title)}</text>
  <text x="48" y="100" fill="{INK}" font-family="sans-serif" font-size="14" font-weight="600">{_esc(header[0])}</text>
  <text x="220" y="100" fill="{INK}" font-family="sans-serif" font-size="14" font-weight="600">{_esc(header[1])}</text>
  <text x="400" y="100" fill="{INK}" font-family="sans-serif" font-size="14" font-weight="600">{_esc(header[2])}</text>
  <line x1="40" y1="108" x2="600" y2="108" stroke="{GRID}" stroke-width="1"/>
{chr(10).join(rows_html)}
</svg>
"""


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_index() -> None:
    lines = [
        "---",
        "title: Graphics index — furniture finishing chemistry",
        "status: draft",
        "series: furniture-finishing-chemistry",
        "---",
        "",
        "# Graphics index",
        "",
        "Shop diagrams (cream/ink SVG). Regenerate: `python3 tools/generate_furniture_finishing_chemistry_graphics.py`.",
        "",
        "| Slug | SVG | Alt (SEO) |",
        "| --- | --- | --- |",
    ]
    for g in GRAPHICS:
        rel = f"assets/{g.slug}/shop-diagram.svg"
        lines.append(f"| `{g.slug}` | `{rel}` | {g.alt} |")
    (PACK / "GRAPHICS_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for g in GRAPHICS:
        dest = ASSETS / g.slug
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "shop-diagram.svg").write_text(svg_table(g), encoding="utf-8")
    write_index()
    print(f"Wrote {len(GRAPHICS)} SVGs under {ASSETS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
