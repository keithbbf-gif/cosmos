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

## Second-wave slugs (figures shipped 14 September 2026)

| Slug | Figure(s) | Embed | Used in article | Portrait | Status |
|------|-----------|-------|-----------------|----------|--------|
| `vienna-1924-logopedics` | IALP / two-rooms schematic | `embeds/vienna-1924-logopedics.md` | `articles/05-vienna-1924-logopedics.md` | — | **Ready** |
| `wwii-rehab-wards` | War-room to shelf-object flow | `embeds/wwii-rehab-wards.md` | `articles/09-wwii-rehab-wards.md` | — | **Ready** |
| `boston-va` | Jamaica Plain hallway | `embeds/boston-va.md` | `articles/13-boston-va.md` | — | **Ready** |
| `mayo-motor-speech` | 1969 cluster names | `embeds/mayo-motor-speech.md` | `articles/14-mayo-motor-speech.md` | — | **Ready** (not a diagnostic tool; no audio) |
| `global-profession` | Door-sign name sketch | `embeds/global-profession.md` | `articles/16-global-profession.md` | — | **Ready** |

## Portrait research queue

Open hunts remain in `PORTRAIT_SOURCES.md`. Highest-value next letters: ASHA (Stinchfield Hawk 1939; West; Travis), WMU (Van Riper), Iowa (Johnson), Mayo (Darley), Minnesota (Schuell, Templin, Brookshire).

## Graphics agent acceptance (per new slug)

Second-wave slugs (Vienna, war wards, Boston VA, Mayo, global names):

- [x] SVG in `assets/<slug>/` with `<title>` + `<desc>`
- [x] `embeds/<slug>.md` with alt text + caption
- [x] `python scripts/regenerate_graphics_index.py`
- [x] Row updated in this checklist

Future slugs still use the same list.
