# Graphics checklist — drafts & remaining slugs

Staged graphics ship with the **seed set** below. Update this file when writer drafts land or new slugs are added to the series bible.

## Seed set (figures shipped in this PR)

| Slug | Figure(s) | Embed | Portrait | Status |
|------|-----------|-------|----------|--------|
| `elocution-to-modern-slp` | Timeline SVG | `embeds/elocution-to-modern-slp.md` | — | **Ready** |
| `asha-institutional-era` | Institutional schematic | `embeds/asha-institutional-era.md` | — | **Ready** |
| `method-schools-compared` | Comparison chart | `embeds/method-schools-compared.md` | — | **Ready** |
| `clinic-geography-schematic` | U.S. schematic map | `embeds/clinic-geography-schematic.md` | — | **Ready** |
| `charles-van-riper` | Pending portrait plate | `embeds/charles-van-riper.md` | Rights **not** cleared | **Plate only** |
| `lee-edward-travis` | Pending portrait plate | `embeds/lee-edward-travis.md` | Rights **not** cleared | **Plate only** |
| `wendell-johnson` | Pending portrait plate | `embeds/wendell-johnson.md` | Rights **not** cleared | **Plate only** |

## Article drafts (waiting on writer)

When `articles/<slug>.md` (or CMS equivalents) appear, verify:

- [ ] Figure paths in draft match `embeds/<slug>.md`
- [ ] Caption numbers follow article sequence
- [ ] Portrait articles reference `PORTRAIT_SOURCES.md` when swapping pending → photo

## Planned slugs (graphics not started)

Add rows as the series outline firms up. Suggested next figures:

| Slug (proposed) | Likely graphic | Notes |
|-----------------|----------------|-------|
| `alexander-melville-bell` | Portrait + Visible Speech diagram | Portrait pending until licensed |
| `world-war-speech-rehab` | Timeline inset or clinic map variant | Could extend clinic-geography |
| `idea-and-school-based-history` | Flow schematic (law → service delivery) | New SVG |
| `aphasia-and-neurology-teams` | Interdisciplinary team diagram | New SVG |
| `diversity-and-scope-evolution` | Scope-of-practice band chart | New SVG |
| `international-comparisons` | Non-U.S. schematic map | Mirror clinic-geography style |

## Portrait research queue

| portrait_id (proposed) | Figure | Researcher action |
|------------------------|--------|-------------------|
| `van-riper-charles` | Charles Van Riper | Locate archive/Commons image; fill `PORTRAIT_SOURCES.md` |
| `travis-lee-edward` | Lee Edward Travis | Same |
| `johnson-wendell` | Wendell Johnson | Same |

## Graphics agent acceptance (per slug)

- [ ] SVG in `assets/<slug>/` with `<title>` + `<desc>`
- [ ] `embeds/<slug>.md` with alt text + caption
- [ ] `python scripts/regenerate_graphics_index.py`
- [ ] Row updated in this checklist
