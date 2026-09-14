"""Figure definitions per article slug."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FigureSpec:
    file_id: str
    generator: str
    alt: str
    caption: str
    embed_after_heading: str
    title: str = ""
    note: str = ""
    cells: tuple[str, ...] = ()


ARTICLE_FIGURES: dict[str, list[FigureSpec]] = {
    "fig-growing-degree-days": [
        FigureSpec(
            "gdd-daily-bars",
            "gdd-daily-bars",
            "Schematic bar chart showing how daily GDD50 units accumulate from high and low temperatures",
            "Illustrative GDD50 bars for one week — replace with your station math, not this drawing.",
            "## What a growing degree day actually is",
        ),
        FigureSpec(
            "gdd-filter-flow",
            "gdd-filter-flow",
            "Flowchart for filtering late fig varieties by local heat budget before frost",
            "Grower workflow: use your own GDD total and frost date — schematic only.",
            "## A simple way to run the number this year",
        ),
    ],
    "tight-eye-vs-open-eye-humid-climates": [
        FigureSpec(
            "eye-comparison",
            "eye-comparison",
            "Side-by-side schematic of tight-eye and open-eye fig fruit cross-sections",
            "Ostiole size schematic — pair with a real fruit photo from D:\\FIGS\\Fig Fruit.",
            "## What “tight” looks like in the hand",
        ),
        FigureSpec(
            "humidity-decision-tree",
            "humidity-decision-tree",
            "Decision tree for humid-week harvest choices on fig trees",
            "After rain + heat — illustrative choices, not a spray schedule.",
            "## What you do in a wet week",
        ),
    ],
    "breba-vs-main-crop-planning": [
        FigureSpec(
            "breba-timeline",
            "breba-timeline",
            "Timeline diagram showing breba fruit on old wood and main crop on new growth",
            "Season schematic — timing shifts with prune and variety.",
            "## The two crops, in plain wood",
        ),
    ],
    "pot-vs-in-ground-figs-south": [
        FigureSpec(
            "pot-vs-ground-chart",
            "pot-vs-ground-chart",
            "Comparison table of container vs in-ground fig growing in the South",
            "Arkansas-weighted tradeoffs — your site may differ.",
            "## A blunt chooser",
        ),
    ],
    "fig-flavor-families": [
        FigureSpec(
            "flavor-wheel",
            "flavor-wheel",
            "Diagram of five fig flavor family descriptors arranged around ripe fruit",
            "Tasting vocabulary only — not lab chemistry or Brix.",
            "## The five words we actually use",
        ),
    ],
    "storing-dormant-fig-cuttings": [
        FigureSpec(
            "fridge-storage-flow",
            "fridge-storage-flow",
            "Process diagram for washing, bagging, and refrigerating dormant fig cuttings",
            "Jack’s fridge workflow — see the cuttings post for the spoken version.",
            "## Wash, wrap, double-bag, crisper",
        ),
    ],
    "fig-cutting-rooting-failures": [
        FigureSpec(
            "rooting-failure-tree",
            "rooting-failure-tree",
            "Decision tree for diagnosing rot, callus-only, or dry fig cuttings",
            "Name the failure mode before you restick — schematic autopsy.",
            "## Failure 1: rot",
        ),
    ],
    "birds-pests-green-vs-dark-figs": [
        FigureSpec(
            "birds-color-chart",
            "birds-color-chart",
            "Illustration comparing green and dark ripe fig visibility to birds",
            "Illustrative contrast — local bird pressure still wins.",
            "## Birds first, because they cost the most fruit",
        ),
    ],
    "fig-soil-drainage-clay-beds": [
        FigureSpec(
            "drainage-cross-section",
            "drainage-cross-section",
            "Cross-section schematic of a fig on a raised berm over clay soil with mulch",
            "Bed profile schematic — not a engineered drainage spec.",
            "## Dig the hole. Fill it. Come back in the morning.",
        ),
    ],
    "summer-shade-water-hot-south": [
        FigureSpec(
            "shade-day-chart",
            "shade-day-chart",
            "Schematic July day showing morning sun and afternoon shade bands",
            "Tune shade to your row — hours shown are illustrative.",
            "## Morning sun, afternoon shade",
        ),
    ],
    "verifying-fig-variety-true-to-type": [
        FigureSpec(
            "variety-verify-flow",
            "variety-verify-flow",
            "Flowchart for verifying fig variety identity over multiple fruiting seasons",
            "True-to-type takes seasons — document while you wait.",
            "## How long I actually wait",
        ),
    ],
    "seasonal-fig-cuttings-calendar": [
        FigureSpec(
            "cuttings-calendar",
            "cuttings-calendar",
            "Schematic year band chart for dormant cut, storage, sticking, and greenwood",
            "US-wide bands — verify frost dates for your zip.",
            "## South Arkansas (our 8a) as the example",
        ),
    ],
    "how-to-read-a-fig-cutting": [
        FigureSpec(
            "cutting-read-checklist",
            "steps_flow",
            "Checklist for reading a fig cutting: polarity, nodes, wood, damage",
            "Read the stick before you stick it — schematic only.",
            "## Which end is up",
            title="Read the stick",
            note="6–8 inches, three nodes. Firewood is not a bargain.",
            cells=("Polarity", "3 nodes", "Lignified?", "Damage?"),
        ),
    ],
    "when-to-pot-up-fig-cuttings": [
        FigureSpec(
            "pot-up-root-check",
            "decision_fork",
            "Decision fork: pot a fig pop when roots exist, not when leaves exist",
            "Leaves lie. Roots on the wall are the check.",
            "## Ready is roots, not leaves",
            title="Pot-up check",
            note="Callus is not a root. June deadline is a different page.",
            cells=("Roots on the wall?", "Leave it", "Pot to #3", "Callus only → wait"),
        ),
    ],
    "water-rooting-fig-cuttings": [
        FigureSpec(
            "water-root-when",
            "compare_table",
            "When Jack would water-root a fig cutting versus stick it in mix",
            "Emergency lane — not a second method we ran a trial on.",
            "## When I would put a stick in a jar",
            title="Jar vs mix",
            note="No success rate. Water roots are brittle.",
            cells=("Job", "Jar", "Mix / coir", "Good lignified tray|No|Yes", "Dehydrated now-wood|Maybe|Prefer mix", "Mail a name|No|Yes"),
        ),
    ],
    "fig-fertigation-after-pot-up": [
        FigureSpec(
            "fertigate-after-plant",
            "steps_flow",
            "Sequence: root first, then pot, then fertigate a living fig",
            "Feed the plant, not the stick. Mixer settings [VERIFY].",
            "## Fertigate the plant, not the stick",
            title="Feed after it exists",
            note="TAMU: no fertilizer at planting. Late N makes tender wood.",
            cells=("Stick", "Roots", "#3", "Then feed"),
        ),
    ],
    "arkansas-winter-protection-figs": [
        FigureSpec(
            "winter-pot-vs-ground",
            "compare_table",
            "Winter protection comparison for potted versus in-ground figs in Arkansas",
            "8a conversation — not a heated-den catalog.",
            "## Pots: the shuffle is the protection",
            title="Winter jobs",
            note="Pots above ~40°F, barely moist. In-ground: save a trunk.",
            cells=("Job", "Pots", "In-ground", "Hard night|Roll inside|Sheet / wall", "Moisture|Barely moist|Water before dry freeze", "January saw|No|Wait for budbreak"),
        ),
    ],
    "the-fig-shuffle-pots": [
        FigureSpec(
            "shuffle-two-moves",
            "steps_flow",
            "Two required pot moves: night before a hard freeze and first 100-degree week",
            "Night low and afternoon high — not the daytime slogan.",
            "## Winter is a move, not a spa",
            title="The two moves",
            note="Wagon beats a hero back. West pad first in July.",
            cells=("Forecast", "Wagon", "Winter cover", "July shade"),
        ),
    ],
    "why-figs-drop-fruit": [
        FigureSpec(
            "drop-causes",
            "decision_fork",
            "Fork for naming fig fruit drop: drought, buttons, or wasp-type",
            "UAEX already named the fathers. Not a curse.",
            "## UAEX already named the fathers",
            title="Name the drop",
            note="TAMU adds water stress and nematodes.",
            cells=("Fruit on the ground?", "Drought / storm / weak", "Wasp-type / Smyrna", "Buttons → wait"),
        ),
    ],
    "fig-split-vs-sour-after-rain": [
        FigureSpec(
            "split-vs-sour",
            "compare_table",
            "Comparison of split fig fruit versus sour fig fruit after rain",
            "Split is physics. Sour is biology. Two buckets, once.",
            "## Split is physics",
            title="After rain",
            note="Kong 2013 is California postharvest — not an 8a hose recipe.",
            cells=("Kind", "Split", "Sour", "Cause|Water vs skin|Eye + microbes", "Smell|Still a fig|Vinegar", "Bucket|Eat / cook now|Trash"),
        ),
    ],
    "daily-picking-fig-harvest-window": [
        FigureSpec(
            "morning-pick-flow",
            "steps_flow",
            "Morning harvest walk: feel, two buckets, fridge pause",
            "Soft means now. A wet week is a day, not a weekend visit.",
            "## Soften, hang, then pick",
            title="Morning job",
            note="NC State: pick at soften. ~40°F is a pause.",
            cells=("Walk", "Feel", "Two buckets", "Eat / 40°F"),
        ),
    ],
    "common-figs-only-arkansas": [
        FigureSpec(
            "fig-types-arkansas",
            "compare_table",
            "Horticultural fig types and which one Arkansas actually grows",
            "Common figs only. Wasp types stay in the book.",
            "## Four types, one that works here",
            title="Types",
            note="UAEX: we do not grow wasp types here.",
            cells=("Type", "Needs wasp?", "AR yard?", "Common|No|Yes", "Smyrna|Yes|No", "Caprifig|Is the pollen|No"),
        ),
    ],
    "celeste-vs-brown-turkey-arkansas": [
        FigureSpec(
            "celeste-turkey-tools",
            "compare_table",
            "Celeste versus Brown Turkey as climate tools in Arkansas",
            "County-agent tools. Not a personality. Fruit still has to be eaten.",
            "## What UAEX actually wrote",
            title="Two tools",
            note="NC State: this Brown Turkey is not California’s.",
            cells=("Trait", "Celeste", "Turkey type", "Eye|Tight|More open", "Hard prune|Punishes crop|Rebounds", "Season|Earlier|Longer pick"),
        ),
    ],
    "lsu-figs-for-humid-south": [
        FigureSpec(
            "lsu-release-years",
            "steps_flow",
            "Timeline of LSU fig releases from Purple through O’Rourke",
            "Release years from AgCenter news — not our tasting scores.",
            "## The real releases",
            title="LSU names",
            note="Gulf timing is not Ozark timing. Tag unverified until fruit.",
            cells=("Purple ’91", "Gold ’95", "Tiger ’07", "Champagne / O’Rourke"),
        ),
    ],
    "root-knot-nematodes-fig-pots": [
        FigureSpec(
            "nematode-pot-rule",
            "decision_fork",
            "Decision: rare fig cutting goes in trusted mix if roots show galls or sand is infested",
            "See galls: pot. Sand + rare stick: pot. No fumigant recipe.",
            "## Galls, sand, and a tired top",
            title="Collector’s rule",
            note="NC State: no chemical on established plants. [VERIFY] agent.",
            cells=("Galls or sand?", "Trusted mix / pot", "Clean clay hole", "Wood only — trash the roots"),
        ),
    ],
    "fig-rust-in-humidity": [
        FigureSpec(
            "rust-litter-cycle",
            "steps_flow",
            "Fig rust cycle: litter spores, wet leaves, drop, repeat",
            "Fruit is not the rust host. Rake is the program.",
            "## Spores on litter, a wet-summer cycle",
            title="Rust cycle",
            note="LSU: spores on diseased leaves. No invented spray schedule.",
            cells=("Litter", "Wind", "Spots", "Rake"),
        ),
    ],
    "pruning-figs-for-cuttings-vs-fruit": [
        FigureSpec(
            "prune-card",
            "decision_fork",
            "Shed card: prune this fig for wood or for fruit this year",
            "Every stick is a fig you will not eat on that branch.",
            "## The card on the shed: wood or fruit",
            title="Wood or fruit",
            note="Celeste hates a hard late-winter chop. Turkey rebounds.",
            cells=("This tree’s July job?", "Take 6–8\" / 3 nodes", "Leave the wood", "Donor trees first"),
        ),
    ],
    "fig-freeze-recovery-multi-trunk": [
        FigureSpec(
            "five-trunk-rebuild",
            "steps_flow",
            "Freeze recovery: wait, let shoots reach two feet, keep five or six trunks",
            "TAMU’s number. Thin over two or three weeks.",
            "## Five or six trunks, not twenty",
            title="Rebuild",
            note="Wait at budbreak. Do not fertilize spears.",
            cells=("Wait", "Shoots ~2 ft", "Keep 5–6", "Year-two thin"),
        ),
    ],
    "pot-up-fig-before-june": [
        FigureSpec(
            "june-pot-deadline",
            "steps_flow",
            "Calendar: pot a rooted fig into a 3-gallon before June",
            "This page is the date. The other page is the roots.",
            "## This page is the date. The other page is the roots.",
            title="Before June",
            note="Introduction already said #3 before the knot.",
            cells=("Roots ready", "#3", "Shade", "Before June"),
        ),
    ],
    "fig-potting-mix-that-drains": [
        FigureSpec(
            "mix-drain-test",
            "decision_fork",
            "Hand test: if water stands on fig potting mix, add air",
            "If water stands on top, the pot is lying.",
            "## Promix, field capacity, the feel",
            title="Does it leave?",
            note="Promix HP + perlite you can see. No decorative vase.",
            cells=("Water stands?", "Add air / perlite", "Field capacity ~70%", "Saucer is a pond"),
        ),
    ],
    "heat-mat-thermostat-fig-cuttings": [
        FigureSpec(
            "mat-thermostat",
            "steps_flow",
            "Heat mat setup: thermostat, probe in the mix, 75 to 78 F",
            "A mat without a controller cooks the tray.",
            "## The number is 75–78°F, and it needs a controller",
            title="Mat + controller",
            note="Probe in the mix, not the air. Off when it is a plant.",
            cells=("Controller", "Probe in mix", "75–78°F", "Unplug later"),
        ),
    ],
    "labeling-fig-cuttings-and-pots": [
        FigureSpec(
            "label-three-times",
            "steps_flow",
            "Write a fig name on the bag, the cup, and the 3-gallon pot",
            "A missing label takes one afternoon. True-to-type takes years.",
            "## Write the name three times",
            title="Three writes",
            note="Paint pen, both sides. One scribe on pot-up day.",
            cells=("Bag", "Cup", "#3", "Notebook"),
        ),
    ],
    "inspecting-mail-order-fig-cuttings": [
        FigureSpec(
            "mailbox-inspect",
            "decision_fork",
            "Mail-order fig cutting inspection: keep, restick, or trash",
            "Open the box the day it lands. Photo the same day.",
            "## Open it the day it lands",
            title="The fork",
            note="6–8 inches, three nodes. Mold, crush, dry.",
            cells=("Alive lignified wood?", "Wash / stick / fridge", "Trash / photo", "Note the seller"),
        ),
    ],
    "grafting-over-a-dud-fig": [
        FigureSpec(
            "graft-keep-hole",
            "steps_flow",
            "Graft-over sequence: trial, scion, wrap, sucker fight, relabel",
            "Keep the hole. The rootstock will try to take the tree back.",
            "## Keep the hole",
            title="Graft over",
            note="Not a surgery manual. Relabel the day it takes. [VERIFY] week.",
            cells=("Long trial", "Cambium", "Wrap", "Suckers / relabel"),
        ),
    ],
    "air-layer-vs-fig-cutting": [
        FigureSpec(
            "layer-vs-cutting",
            "compare_table",
            "When to air-layer a fig versus cut 6–8 inch sticks",
            "A cutting is a tray. A layer is a plant you can already picture.",
            "## A cutting is a tray. A layer is a plant you can already picture.",
            title="Pick the job",
            note="Do not layer the only trunk. Fall clock is on the live site.",
            cells=("Want", "Cutting", "Layer", "Twenty plants|Yes|No", "One #5 this year|Slow|Yes", "Only trunk|Side stick|Do not"),
        ),
    ],
    "east-wall-fig-microclimate": [
        FigureSpec(
            "east-wall-day",
            "steps_flow",
            "East-wall day: morning sun dries fruit, afternoon shade, still 6–8 hours",
            "TAMU/UAEX: east or south of a building. West fries.",
            "## East or south of a building",
            title="The wall is a climate",
            note="Still 6–8 hours. Not a decoration.",
            cells=("East/south", "Morning dry", "Afternoon ease", "6–8 hr"),
        ),
    ],
    "collecting-figs-vs-eating-figs": [
        FigureSpec(
            "pantry-vs-library",
            "compare_table",
            "Collection library versus pantry trees that actually feed you",
            "Count bowls, not names. Pantry trees first on the fridge list.",
            "## The jobs fight",
            title="Two jobs",
            note="Three eaters before twenty names.",
            cells=("Job", "Pantry", "Library", "Plant|Few in-ground|Many #3s", "July|Pick daily|Shuffle / labels", "Buy|Net + hose|Mix + shop"),
        ),
    ],
    "unknown-figs-honest-names": [
        FigureSpec(
            "unknown-until-plate",
            "steps_flow",
            "Keep Unk in the name until fruit on the plate says otherwise",
            "Jack kept Unk on Navid’s Unk Dark Greek. That is the method.",
            "## Unknown is a working name",
            title="Until the plate",
            note="Do not ship a guess. Paint pen + source + year.",
            cells=("As received", "Unk stays", "Eat fruit", "Then maybe rename"),
        ),
    ],
    "late-freeze-after-fig-budbreak": [
        FigureSpec(
            "late-freeze-kit",
            "steps_flow",
            "Late freeze night kit: forecast, wagon, covers, wait days to saw",
            "The cruel freeze is the one after the buds move.",
            "## A night-of kit that is not cute",
            title="After budbreak",
            note="GDD resets. Breba is usually gone. No heater under dry leaves.",
            cells=("Night low", "Roll pots", "Sheet", "Wait to saw"),
        ),
    ],
    "first-two-summers-in-ground-fig": [
        FigureSpec(
            "two-summer-hole",
            "steps_flow",
            "First two summers in the ground: plant, water, mulch, still a hose job",
            "The hole is a pot you cannot lift until year three.",
            "## What I put in the hole",
            title="Two summers",
            note="Graduation = live trunk in March of year three + hose in August of year two.",
            cells=("Drain hole", "Water in", "Two Augusts", "Year three"),
        ),
    ],
    "marketplace-fig-cutting-red-flags": [
        FigureSpec(
            "listing-red-flags",
            "decision_fork",
            "Walk away from a fig cutting listing that sells a name instead of wood",
            "Close the tab. The mailbox draft is for boxes you already accepted.",
            "## The wood they are selling is not the wood they photographed",
            title="Buy wood, not a caption",
            note="6–8 inches, three nodes. Green in a heat wave is produce.",
            cells=("Photo of the sticks?", "Read length / nodes", "Close the tab", "Unverified until fruit"),
        ),
    ],
    "fig-fall-harden-off-arkansas": [
        FigureSpec(
            "september-stop",
            "steps_flow",
            "Fall harden-off: stop late nitrogen, ease the hose, keep moisture even, wait for wood",
            "NC State: late N makes succulent growth that takes winter injury.",
            "## What I turn off",
            title="Quit the September push",
            note="Not California deficit irrigation. Not a bone-dry trick.",
            cells=("Stop mixer", "Even water", "Lignify", "March scratch"),
        ),
    ],
    "outdoor-bulk-fig-starts": [
        FigureSpec(
            "bulk-vs-cup",
            "compare_table",
            "Outdoor bulk starts versus cups for named fig cuttings",
            "Outdoor page numbers stay on that page. Dirt is for wood you can replace.",
            "## The job is volume",
            title="Bed vs cup",
            note="Do not invent an outdoor coir/DE sequel.",
            cells=("Job", "Outdoor bed", "Cup / pop", "Wood|Replaceable donor|Mailbox name", "Clock|60–90 days / dormancy|Roots, then #3", "Mix|Trusted bed dirt|Clean media"),
        ),
    ],
    "winter-shop-scale-figs": [
        FigureSpec(
            "den-vs-shop",
            "compare_table",
            "Winter shop that stays barely moist versus a 70-degree den that grows scale",
            "Winter page: above ~40°F, not a heated den. [VERIFY] before you spray.",
            "## Why the den does it",
            title="Den or shop",
            note="LSU mentions hort oil for mealybugs — Louisiana, not an AR recipe.",
            cells=("Room", "Shop", "Den", "Temp|Not frozen|Steady 70°F", "Mix|Barely moist|Saucers / flush", "Pests|Look / isolate|Cotton + honeydew"),
        ),
    ],
    "variety-trial-row-figs": [
        FigureSpec(
            "five-tree-trial",
            "steps_flow",
            "Five-tree fig trial: tool, honey or gold, tight berry, two pot wildcards",
            "A trial has a question. A parking lot has a receipt.",
            "## A five-tree row I would actually run",
            title="Five trees you pick",
            note="Intro: 1–3 years to prove type. Fig Jam: long trial before you cut a tree.",
            cells=("Tool", "Honey/gold", "Tight berry", "Two pots"),
        ),
    ],
}
