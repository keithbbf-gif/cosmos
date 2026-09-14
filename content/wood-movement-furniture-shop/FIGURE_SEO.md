---
title: Figure SEO — wood movement for the furniture shop
status: draft
series: wood-movement-furniture-shop
---

# Figure SEO

Machine- and human-readable metadata for **in-repo diagrams**.
Photograph slots stay in draft front matter until BBF files clear
`RIGHTS.md`.

Import rule: use **`alt`** for accessibility and image search;
use **`wp_media_title`** as the WordPress media library title (not
the post title); use **`wp_filename`** on upload so URLs stay
stable and readable.

## Diagram registry

### `diagram-emc-70f`

| Field | Value |
| --- | --- |
| **file** | `images/svg/emc-rh-equilibrium-70f.svg` |
| **version** | 1 |
| **drafts** | `09-emc-is-the-boards-weather.md` |
| **figure id** | `fig-diagram-emc` |
| **alt** | Chart of equilibrium moisture content EMC versus relative humidity at 70 degrees F for furniture wood drying in the shop |
| **title** | EMC vs relative humidity at 70°F — furniture wood equilibrium moisture |
| **wp_media_title** | EMC vs RH at 70F — wood equilibrium moisture content chart |
| **wp_filename** | wood-movement-emc-relative-humidity-70f.svg |
| **caption** | At shop temperature, relative humidity sets the moisture content the board is headed for — verify Handbook cells before you bet a rack on one number. |
| **description** (schema / long) | Equilibrium moisture content (EMC) is the moisture percentage solid wood approaches in a given relative humidity and temperature. This diagram plots example Handbook-style points at 30%, 50%, and 70% RH near 70°F, with a board on sticks approaching that EMC over time. Used in the wood-movement-furniture-shop series for furniture makers sizing acclimation and ΔMC. |
| **keywords** (natural, not stacked) | equilibrium moisture content, EMC, relative humidity, wood moisture, furniture shop drying, Wood Handbook |
| **license** | See `RIGHTS.md` § Original diagrams |
| **status** | ready |

### `diagram-breadboard-seasonal`

| Field | Value |
| --- | --- |
| **file** | `images/svg/breadboard-end-seasonal-movement.svg` |
| **version** | 1 |
| **drafts** | `27-breadboard-that-doesnt-blow.md`, `02-winter-proud-summer-shy.md` |
| **figure id** | `fig-diagram-breadboard` |
| **alt** | Plan view of table breadboard end cap with center glue and slotted pins while the field panel grows wider in humid summer and narrower in dry winter |
| **title** | Breadboard end cap and seasonal table top width — slots and center glue |
| **wp_media_title** | Breadboard joint seasonal wood movement — field width vs end cap |
| **wp_filename** | wood-movement-breadboard-seasonal-width-slots.svg |
| **caption** | The cap stays on length; the field still changes width. Glue the center, slot the outer pins, size travel from ΔMC on the scrap. |
| **description** (schema / long) | Technical diagram for breadboard-end joinery on solid wood table tops: the breadboard end grain cap does not change length while the main field changes width with seasonal moisture. Shows humid versus dry field width, center-only glue, elongated pin slots, and the proud shoulder line when a joint was built as a clamp. Furniture design wood movement. |
| **keywords** | breadboard end, table top expansion, wood movement joint, slotted pins, seasonal shrinkage |
| **license** | See `RIGHTS.md` § Original diagrams |
| **status** | ready |

### `diagram-delta-mc-formula`

| Field | Value |
| --- | --- |
| **file** | `images/svg/dimensional-change-delta-mc-formula.svg` |
| **version** | 1 |
| **drafts** | `11-the-scrap-paper-formula.md`, `26-the-gap-in-the-groove.md`, `50-the-cut-list-checklist.md` |
| **figure id** | `fig-diagram-delta-mc` |
| **alt** | Formula for wood dimensional change: delta width equals width times handbook coefficient times change in moisture content, with red oak panel example about five thirty-seconds inch |
| **title** | Wood movement formula — width × coefficient × ΔMC with groove allowance |
| **wp_media_title** | Dimensional change formula width coefficient delta MC — wood movement |
| **wp_filename** | wood-movement-formula-width-coefficient-delta-mc.svg |
| **caption** | The groove is not a feeling. It is width × coefficient × ΔMC, split across both sides, plus a little mercy. |
| **description** (schema / long) | Shop reference for USDA Wood Handbook dimensional change: approximate change in width equals panel width in inches times tangential or radial coefficient times change in moisture content in percentage points. Includes worked flatsawn red oak example (11.25 in, 0.00369, 4 points) and a frame-and-panel groove sketch showing travel plus mercy. |
| **keywords** | wood movement formula, dimensional change coefficient, delta MC, groove allowance, flatsawn oak |
| **license** | See `RIGHTS.md` § Original diagrams |
| **status** | ready |

## Markdown embed pattern

In draft body (relative to pack root):

```markdown
![{alt}](images/svg/{file})
*{caption}*
```

WordPress block equivalent: Image block with **alt text** from this
file, **caption** from this file, **title attribute** optional from
**title** column.

## Open Graph / social

Do not set `og:image` to a diagram until the post is approved for
publish. When set, prefer exported **1200×630** PNG derived from the
SVG for `diagram-delta-mc-formula` on formula posts and
`diagram-breadboard-seasonal` on design posts — crop with caption
legible. Record export hash in commit message when raster is added
(later lane).

## Checks before publish

1. `alt` matches visible teaching content (not a keyword list).
2. `RIGHTS.md` read; attribution line on site if required.
3. Handbook numbers in diagram copy match `[VERIFY]` resolution in
   the draft.
4. Photograph slots still `needed` unless BBF clearance is written.
