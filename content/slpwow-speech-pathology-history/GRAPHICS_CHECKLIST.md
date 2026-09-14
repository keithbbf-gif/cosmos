# Graphics checklist — drafts & remaining slugs

Writer drafts (40 articles) landed 14 September 2026. Seed SVGs are embedded in the essays named below.

## Seed set (figures shipped)

| Slug | Figure(s) | Embed | Used in article | Portrait | Status |
|------|-----------|-------|-----------------|----------|--------|
| `elocution-to-modern-slp` | Timeline SVG | `embeds/elocution-to-modern-slp.md` | `articles/01-before-the-clinic.md` | — | **Ready** |
| `asha-institutional-era` | Institutional schematic | `embeds/asha-institutional-era.md` | `articles/12-asha-grows-up.md` | — | **Ready** |
| `method-schools-compared` | Comparison chart | `embeds/method-schools-compared.md` | `articles/15-from-correction-to-csd.md` | — | **Ready** |
| `clinic-geography-schematic` | U.S. schematic map | `embeds/clinic-geography-schematic.md` | `articles/07-iowa-school.md` | — | **Ready** |
| `charles-van-riper` | Pending portrait plate | `embeds/charles-van-riper.md` | `articles/30-charles-van-riper.md` | Rights **not** cleared | **Plate only** |
| `lee-edward-travis` | Pending portrait plate | `embeds/lee-edward-travis.md` | `articles/28-lee-edward-travis.md` | Rights **not** cleared | **Plate only** |
| `wendell-johnson` | Pending portrait plate | `embeds/wendell-johnson.md` | `articles/29-wendell-johnson.md` | Rights **not** cleared | **Plate only** |

Cleared photographic portraits (see `PORTRAIT_SOURCES.md`) are embedded in the Bell, Broca, Wernicke, Gutzmann, Scripture, Fogerty, and Luria profiles, plus essay illustrations for de l’Épée and Visible Speech.

## Article drafts

- [x] Forty `articles/*.md` files exist (`INDEX.md`)
- [x] Seed figure paths pasted into the matching essays
- [ ] Caption numbers still “Figure 1” per article — fine until a later designer sequences a multi-figure piece
- [x] Hunt profiles keep pending plates or the labeled placeholder block
- [x] No synthetic faces

## Planned slugs (graphics not started)

| Slug (proposed) | Likely graphic | Notes |
|-----------------|----------------|-------|
| `vienna-1924-logopedics` | IALP / Europe schematic | Pair with essay 05 |
| `wwii-rehab-wards` | Ward-flow diagram | Pair with essay 09 |
| `boston-va` | Team diagram (Goodglass–Kaplan–Geschwind) | Pair with essay 13 |
| `mayo-motor-speech` | Dysarthria cluster schematic | Pair with essay 14; no patient audio |
| `global-profession` | Non-U.S. name map | Pair with essay 16 |

## Portrait research queue

Open hunts remain in `PORTRAIT_SOURCES.md`. Highest-value next letters: ASHA (Stinchfield Hawk 1939; West; Travis), WMU (Van Riper), Iowa (Johnson), Mayo (Darley), Minnesota (Schuell, Templin, Brookshire).

## Graphics agent acceptance (per new slug)

- [ ] SVG in `assets/<slug>/` with `<title>` + `<desc>`
- [ ] `embeds/<slug>.md` with alt text + caption
- [ ] `python scripts/regenerate_graphics_index.py`
- [ ] Row updated in this checklist
