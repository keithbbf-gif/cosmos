# Fig grafting and budding — Zone 8a, staged drafts

These are **staged drafts**, not a published site. They sit in the Website GC
staging box: readable, usable, still open to a knife. Nothing here is live
copy until someone with the publish click says so.

The job is practical. USDA Zone **8a** (average annual extreme minimum about
10–15°F). Common fig, *Ficus carica*. Human voice. One grower talking to
another person who is about to cut a tree they actually like.

## Why this folder exists

Figs root from cuttings so easily that grafting looks like a hobby for people
who enjoy extra work. It is extra work. It is also the only clean way to:

- convert a hardy but boring bush after a hard 8a winter
- keep a tender variety on roots that come back
- put more than one ripening window on one trunk
- salvage a single bud when the rest of a rare cutting is going in water

If a cutting will do, take the cutting. These drafts assume you already
decided the knife is the right tool.

## How the stages work

Read in order the first year you graft. After that, jump. Each draft is
meant to stand alone; the stage number is the recommended first pass.

| Stage | Folder | What it is |
|---|---|---|
| 00 | `stage-00-orientation/` | When grafting is worth it, and when it is theater |
| 01 | `stage-01-calendar/` | Zone 8a year, phenology, late frost |
| 02 | `stage-02-kit-and-safety/` | Knife, tape, latex, mosaic hygiene |
| 03 | `stage-03-understock/` | What you graft *onto* |
| 04 | `stage-04-scion/` | Wood you cut, store, and throw out |
| 05 | `stage-05-union-anatomy/` | Cambium, pith, awake/asleep |
| 06 | `stage-06-dormant-grafts/` | Cleft, whip, saddle, side veneer |
| 07 | `stage-07-bark-and-large-stock/` | Thick stubs, sap drawers, two-year topwork |
| 08 | `stage-08-budding/` | Chip, T, patch, wrapping the bud |
| 09 | `stage-09-bench-and-special/` | Bucket grafts, nurse roots, inarch |
| 10 | `stage-10-aftercare/` | Bags, unwrap, suckers, stakes |
| 11 | `stage-11-first-year-and-winter/` | First summer, first winter, form |
| 12 | `stage-12-failures-and-disease/` | The usual death, virus, fruit faults |
| 13 | `stage-13-varieties-8a/` | Scions that earn a slot in 8a |
| 14 | `stage-14-field-cards/` | Pocket lists for collect / cut / 90 days |

Frontmatter on every draft:

- `status: staged` — not published
- `zone: 8a`
- `voice: human`
- `stage` matches the folder

## Voice and quality bar

No "comprehensive guide." No "unlock." No cultivar worship that ignores
humidity, souring, or a January that actually hits 11°F. Prefer phenology
over a calendar date stolen from San Diego. Name the failure when the
literature and the backyard disagree.

Contested points are marked in the drafts, not smoothed:

- Eisen (1901) liked autumn/winter grafting and two-year wood. Most living
  grafters in 8a collect one-year dormant wood in winter and cut when the
  **stock** starts to move in spring.
- Chip-bud is the reliable backyard method on figs. T-bud wants slipping
  bark and still loses to chip-bud for most people.
- *Ficus palmata* is graft-compatible and often called mosaic-immune. It is
  **not** a guaranteed nematode-proof understock. Clone matters.

## Check

```text
python3 content/fig-grafting-budding/_check.py
```

Inventory: `MANIFEST.toml`.
