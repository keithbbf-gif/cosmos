# Graphics index — butcher-block countertops guide

Twelve illustrated drafts: one PD historical plate, eleven original SVG care/spec diagrams. See `RIGHTS.md` before import.

| Draft | Slug | Asset | Embed |
| --- | --- | --- | --- |
| 01 | why-this-guide | `assets/workflow/island-wood-top-schematic.svg` | `embeds/why-this-guide.md` |
| 03 | the-block-was-a-tool | `assets/historical-butcher-block/ochs-reading-terminal-market-1910s.jpg` | `embeds/the-block-was-a-tool.md` |
| 09 | edge-grain-is-the-residential-default | `assets/grain-orientations/edge-end-face-grain.svg` | `embeds/edge-grain-is-the-residential-default.md` |
| 12 | thickness-is-structure | `assets/thickness-profile/thickness-profile.svg` | `embeds/thickness-is-structure.md` |
| 18 | how-the-top-gets-fastened | `assets/top-fasteners/top-fasteners.svg` | `embeds/how-the-top-gets-fastened.md` |
| 19 | oil-is-a-habit | `assets/oil-schedule/oil-maintenance-schedule.svg` | `embeds/oil-is-a-habit.md` |
| 24 | never-soak-never-dishwasher | `assets/care-habits/care-never-soak.svg` | `embeds/never-soak-never-dishwasher.md` |
| 25 | knives-heat-and-the-trivet | `assets/care-habits/heat-knife-trivet.svg` | `embeds/knives-heat-and-the-trivet.md` |
| 30 | overhang-on-wood | `assets/overhang-wood/wood-overhang-support.svg` | `embeds/overhang-on-wood.md` |
| 46 | spec-sheet-for-a-wood-top | `assets/spec-sheet/six-line-spec-sheet.svg` | `embeds/spec-sheet-for-a-wood-top.md` |
| 47 | sequence-job-to-care-card | `assets/workflow/job-to-care-sequence.svg` | `embeds/sequence-job-to-care-card.md` |
| 48 | aftercare-card | `assets/aftercare-card/aftercare-card-layout.svg` | `embeds/aftercare-card.md` |

## SEO frontmatter (all drafts)

Every draft carries `meta_description` and `featured_image` (relative from `drafts/`). Illustrated drafts list `figures:` with the same asset path.

## QA

```bash
python3 tools/check_butcher_block_drafts.py
python3 tools/check_butcher_block_graphics.py
```
