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
            "## What I actually do",
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
            "## The test I want you to run before you shop a tree",
        ),
    ],
    "summer-shade-water-hot-south": [
        FigureSpec(
            "shade-day-chart",
            "shade-day-chart",
            "Schematic July day showing morning sun and afternoon shade bands",
            "Tune shade to your row — hours shown are illustrative.",
            "## Sun is not one thing",
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
}
