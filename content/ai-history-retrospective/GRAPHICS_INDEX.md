# Graphics index — Long Term History of AI (Retrospective)

All paths relative to `content/ai-history-retrospective/`. **Staged** for COPY embed; not published.

## Shared figures

| ID | File | Use |
|----|------|-----|
| G-ERA-001 | `assets/shared/era-timeline-pre1956-2026.svg` | Series opener, `00-series-overview` |
| G-WIN-001 | `assets/shared/ai-winter-summer-schematic.svg` | Winter articles, funding context |
| G-PAR-001 | `assets/shared/paradigm-comparison.svg` | Paradigm framing across series |

## By article slug

| Slug | Figures |
|------|---------|
| `00-series-overview` | G-ERA-001, G-PAR-001, G-WIN-001 |
| `pre-1956-origins` | `assets/pre-1956-origins/timeline.svg`, `assets/pre-1956-origins/labs-schools.svg` |
| `dartmouth-1956` | `assets/dartmouth-1956/timeline.svg`, `assets/dartmouth-1956/attendees-schematic.svg` |
| `symbolic-ai-era` | `assets/symbolic-ai-era/labs-schools.svg` |
| `expert-systems-1980s` | `assets/expert-systems-1980s/labs-schools.svg` |
| `first-ai-winter` | `assets/first-ai-winter/funding-band.svg`, G-WIN-001 |
| `connectionist-revival` | `assets/connectionist-revival/timeline.svg` |
| `deep-learning-renaissance` | `assets/deep-learning-renaissance/labs-schools.svg` |

## Portraits

| Slug | Plate | Raster |
|------|-------|--------|
| `figure-alan-turing` | `assets/figure-alan-turing/portrait-plate.svg` | — (rights not cleared) |
| `figure-john-mccarthy` | `assets/figure-john-mccarthy/portrait-plate.svg` | — |
| `figure-marvin-minsky` | `assets/figure-marvin-minsky/portrait-plate.svg` | — |

Template: `assets/_templates/portrait-plate.svg`

## Staged embed packs

Markdown snippets: `staged/embeds/<slug>.md` — copy into article drafts when COPY lands.

## Maintenance

- Update this file when adding any SVG under `assets/<slug>/`.
- Run `python3 content/ai-history-retrospective/tools/validate_graphics.py` before PR.
- Portrait clearance: `PORTRAIT_SOURCES.md` only.
