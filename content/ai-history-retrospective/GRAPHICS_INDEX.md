# Graphics index — Long Term History of AI (Retrospective)

All paths relative to `content/ai-history-retrospective/`. Embeds are written for articles in `essays/` and `profiles/` (paths start `../assets/`).

This COPY tree (`cursor/ai-history-retrospective-7b08`) is the writer of record. Graphics PR #247 (`cursor/ai-history-graphics-aae1`) shipped the SVG pipeline ahead of copy; slugs below are that pack’s IDs. Do not invent a second set of faces or a second timeline.

## Shared figures

| ID | File | Use |
|----|------|-----|
| G-ERA-001 | `assets/shared/era-timeline-pre1956-2026.svg` | Series anchor timeline |
| G-WIN-001 | `assets/shared/ai-winter-summer-schematic.svg` | Winters, funding context |
| G-PAR-001 | `assets/shared/paradigm-comparison.svg` | Paradigm framing |

## COPY slug → graphics slug

| COPY file | COPY `slug` | `graphics_slug` (#247) | Figures in the article |
|-----------|-------------|------------------------|------------------------|
| `essays/00-series-overview.md` | `00-series-overview` | `00-series-overview` | G-ERA-001, G-PAR-001, G-WIN-001 |
| `essays/before-the-machines-thought.md` | `before-the-machines-thought` | `pre-1956-origins` | `assets/pre-1956-origins/timeline.svg`, `labs-schools.svg` |
| `essays/cybernetics-and-the-macy-years.md` | `cybernetics-and-the-macy-years` | `pre-1956-origins` | `labs-schools.svg` (Macy / early schools) |
| `essays/dartmouth-1956.md` | `dartmouth-1956` | `dartmouth-1956` | `assets/dartmouth-1956/timeline.svg` |
| `essays/the-symbolic-bet.md` | `the-symbolic-bet` | `symbolic-ai-era` | `assets/symbolic-ai-era/labs-schools.svg` |
| `essays/perceptrons-and-the-first-winter.md` | `perceptrons-and-the-first-winter` | `first-ai-winter` | G-WIN-001 |
| `essays/winters-and-summers.md` | `winters-and-summers` | `first-ai-winter` | G-WIN-001 |
| `essays/expert-systems-summer.md` | `expert-systems-summer` | `expert-systems-1980s` | G-ERA-001 (no dedicated map yet) |
| `essays/connectionist-revival.md` | `connectionist-revival` | `connectionist-revival` | G-PAR-001 |
| `essays/statistical-turn.md` | `statistical-turn` | `statistical-ml-1990s` | none yet; era tick lives on G-ERA-001 in the overview |
| `essays/imagenet-moment.md` | `imagenet-moment` | `deep-learning-renaissance` | none yet; 2012 tick is on G-ERA-001 |
| `essays/attention-and-transformers.md` | `attention-and-transformers` | `transformers-and-foundation-models` | none yet; 2017 tick is on G-ERA-001 |
| `essays/llms-2018-2026.md` | `llms-2018-2026` | `transformers-and-foundation-models` | same slug; no second copy of the era map |
| `profiles/alan-turing.md` | `alan-turing` | `figure-alan-turing` | raster in body; plate cleared |
| `profiles/john-mccarthy.md` | `john-mccarthy` | `figure-john-mccarthy` | raster in body; plate cleared |
| `profiles/marvin-minsky.md` | `marvin-minsky` | `figure-marvin-minsky` | raster in body; plate cleared |

Unmapped essays (games, speech, vision, RL, Soviet cybernetics, ELIZA, KR, robotics, publication, fifth generation, knowledge representation) have no #247 folder yet. Do not mint graphics slugs for them until a figure is drawn.

## Dedicated article figures

| Graphics slug | Files |
|---------------|-------|
| `pre-1956-origins` | `assets/pre-1956-origins/timeline.svg`, `assets/pre-1956-origins/labs-schools.svg` |
| `dartmouth-1956` | `assets/dartmouth-1956/timeline.svg` |
| `symbolic-ai-era` | `assets/symbolic-ai-era/labs-schools.svg` |

## Portrait plates

| Graphics slug | Plate | Raster (`PORTRAIT_SOURCES.md`) | Status |
|---------------|-------|--------------------------------|--------|
| `figure-alan-turing` | `assets/figure-alan-turing/portrait-plate.svg` | `assets/portraits/alan-turing.jpg` | **cleared** — Princeton 1936 card, PD |
| `figure-john-mccarthy` | `assets/figure-john-mccarthy/portrait-plate.svg` | `assets/portraits/john-mccarthy.jpg` | **cleared** — Stanford 2006, CC BY-SA 2.0 |
| `figure-marvin-minsky` | `assets/figure-marvin-minsky/portrait-plate.svg` | `assets/portraits/marvin-minsky.jpg` | **cleared** — OLPC event, CC BY 3.0 |

Template (hatched, uncleared default): `assets/_templates/portrait-plate.svg`. Defs: `assets/_templates/archival-defs.svg`.

Other profiles in this tree have sourced rasters or labeled placeholders. Do not add `figure-*` plates until GRAPHICS draws them against `PORTRAIT_SOURCES.md`. Never generate a face.

## Staged embed packs

`staged/embeds/<graphics_slug>.md` — copy-ready Markdown, paths relative to `essays/` or `profiles/`.

## Maintenance

- Run `python3 content/ai-history-retrospective/tools/validate_graphics.py` before PR.
- Portrait clearance: `PORTRAIT_SOURCES.md` only.
- Series titles: COPY says *History of AI — Retrospective*; the graphics pack says *Long Term History of AI*. One folder.
