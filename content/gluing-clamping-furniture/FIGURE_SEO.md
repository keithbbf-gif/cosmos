---
title: Figure SEO — gluing & clamping for the furniture shop
status: draft
series: gluing-clamping-furniture
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

### `diagram-four-glue-clocks`

| Field | Value |
| --- | --- |
| **file** | `images/svg/four-glue-clocks-timeline.svg` |
| **version** | 1 |
| **drafts** | `d10-four-clocks.md` |
| **figure id** | `fig-diagram-four-clocks` |
| **alt** | Timeline of four glue clocks — open time, closed time, clamp time, and full cure — on one furniture glue-up |
| **title** | Four glue clocks — open, closed, clamp, and cure are not one hour |
| **wp_media_title** | Furniture glue open time closed time clamp time cure timeline |
| **wp_filename** | gluing-clamping-four-glue-clocks-timeline.svg |
| **caption** | Open is assembly. Closed is the walk to the iron. Clamp is permission to remove iron. Cure is when the machine may touch the seam. |
| **description** (schema / long) | Process diagram for furniture shop glue-ups: separates open time (spread and assembly), closed time (faces met before full pressure), clamp time (hours under iron), and cure (full strength before machining or load). Used in the gluing-clamping-furniture series to stop mixing bottle labels into one timer. |
| **keywords** (natural, not stacked) | open time, clamp time, glue cure, furniture glue-up, PVA hide epoxy clocks |
| **license** | See `RIGHTS.md` § Original diagrams |
| **status** | ready |

### `diagram-glue-film-witness`

| Field | Value |
| --- | --- |
| **file** | `images/svg/glue-film-starved-drowned-witness.svg` |
| **version** | 1 |
| **drafts** | `d23-starved-and-drowned.md`, `d24-both-cheeks-not-a-puddle.md` |
| **figure id** | `fig-diagram-glue-film` |
| **alt** | Three panel edge joints showing starved dry glue line, correct thin film with even squeeze-out bead, and drowned flooded glue smear |
| **title** | Starved drowned and witness bead — furniture glue film on a closed seam |
| **wp_media_title** | Starved joint vs drowned glue vs witness bead — panel glue line |
| **wp_filename** | gluing-clamping-starved-drowned-witness-bead.svg |
| **caption** | A thin even bead is the witness. Dry counties starve. A river drowns and stains. |
| **description** (schema / long) | Cross-section teaching diagram for spreading glue on furniture panel or frame joints: starved joint with dry patches, correct thin continuous film with witness bead at the seam, and drowned joint with hydraulic squeeze and smear. Supports starved-and-drowned and both-cheeks application essays. |
| **keywords** | starved glue joint, squeeze-out, glue film, panel glue-up, drowned joint |
| **license** | See `RIGHTS.md` § Original diagrams |
| **status** | ready |

### `diagram-breadboard-glue-center`

| Field | Value |
| --- | --- |
| **file** | `images/svg/breadboard-center-glue-slots.svg` |
| **version** | 1 |
| **drafts** | `d21-glue-the-middle-of-the-breadboard.md` |
| **figure id** | `fig-diagram-breadboard-glue` |
| **alt** | Plan view of table breadboard tongue with glue only at center mortise and elongated pin slots at wings while field width may change |
| **title** | Breadboard glue center only — slotted pins at wings |
| **wp_media_title** | Breadboard joint center glue slotted pins furniture glue-up |
| **wp_filename** | gluing-clamping-breadboard-center-glue-slots.svg |
| **caption** | The middle may stick. The wings must walk. Glue the center; slot the pins. |
| **description** (schema / long) | Glue-up diagram for breadboard-end table tops: tongue and breadboard cap with center-only adhesive zone, dry wings, and elongated pin holes so seasonal field width can move without splitting a fully glued cap. Complements wood-movement seasonal diagrams; this pack owns the **glue** decision. |
| **keywords** | breadboard end, center glue, slotted pins, table top glue-up, wood movement joint |
| **license** | See `RIGHTS.md` § Original diagrams |
| **status** | ready |

### `diagram-banana-panel-bars`

| Field | Value |
| --- | --- |
| **file** | `images/svg/banana-panel-alternate-bars.svg` |
| **version** | 1 |
| **drafts** | `d36-the-banana-panel.md`, `d14-cauls-are-the-clamp-you-forgot.md` |
| **figure id** | `fig-diagram-banana-panel` |
| **alt** | Side view comparing wrong panel glue-up with all clamp bars on one face causing a banana bow versus correct alternating bars above and below with crowned cauls |
| **title** | Banana panel clamp mistake vs alternate bars and cauls |
| **wp_media_title** | Panel glue-up banana bow — alternate clamp bars and cauls |
| **wp_filename** | gluing-clamping-banana-panel-alternate-bars-cauls.svg |
| **caption** | Bars on one face smile the panel. Above, below, cauls in the field — or saw the seams and try again. |
| **description** (schema / long) | Clamp-pattern process diagram for wide solid-wood panel glue-ups: shows bars-only-on-show-face producing edge-down banana bow versus sandwich of alternating pipe or bar clamps and crowned cauls distributing pressure through the field. Used when teaching clamp smiles versus moisture cup. |
| **keywords** | panel glue-up, banana panel, clamp cauls, alternate clamp bars, pipe clamp panel |
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
SVG for clock and clamp-pattern posts — crop with labels legible.
Record export hash in commit message when raster is added (later lane).

## Checks before publish

1. `alt` matches visible teaching content (not a keyword list).
2. `RIGHTS.md` read; attribution line on site if required.
3. Sheet numbers in diagram copy match `[VERIFY]` resolution in
   the draft.
4. Photograph slots still `needed` unless BBF clearance is written.
