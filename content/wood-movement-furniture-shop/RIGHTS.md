# Rights — wood movement for the furniture shop

**Pack path:** `content/wood-movement-furniture-shop/`  
**Last updated:** 2026-09-14  
**Status:** draft pack — do not publish figures without reading this file.

## Summary

| Asset class | In repo? | Who may publish | Notes |
| --- | --- | --- | --- |
| Original SVG diagrams (`images/svg/`) | Yes | Keith BBF / authorized site operator | Authored for this pack; see below |
| BBF shop photographs (`D:\BBF\BBF Photos`) | No | Owner only after clearance | Slots stay `needed` until a file + credit land |
| Wood Handbook tables / coefficients | Cited, not copied as scans | N/A | Use `SOURCES.md`; diagrams paraphrase public science |
| Stock / Commons photos | No | Do not add without URL + license | `STYLE_GUIDE.md` |

## Original diagrams (SVG)

These three files are **original vector work** created for the
wood-movement writer pack. They are not traced from third-party
illustrations or stock clip art.

| File | Purpose |
| --- | --- |
| `images/svg/emc-rh-equilibrium-70f.svg` | EMC vs RH at ~70°F |
| `images/svg/breadboard-end-seasonal-movement.svg` | Breadboard cap vs seasonal field width |
| `images/svg/dimensional-change-delta-mc-formula.svg` | Δwidth ≈ width × coefficient × ΔMC |

**Copyright holder:** Keith BBF (Bradley County Hardwood / shop
content program), c/o the COSMOS `content/` tree.

**Creation:** 2026-09-14 — Cursor Cloud Agent illustration lane for
PR #499 follow-up (IMAGE+SEO).

**License for repository copy:** Keith retains copyright. Committing
to this repo grants collaborators permission to **store, review, and
prepare WordPress drafts** only. **Public display** (website, social,
print, courseware) requires an explicit publish decision by Keith or
delegated site operator — not automatic on merge.

**Attribution line (when published):**  
`Diagram: Bradley County Hardwood / wood-movement-furniture-shop series.`

**Modifications:** Prefer editing the SVG in-repo and bumping the
`version` field in `FIGURE_SEO.md`. Do not raster-replace the only
source without keeping the SVG.

## BBF photograph library

Preferred fills are named in draft front matter as
`D:\BBF\BBF Photos …`. Those files are **not** in git.

Before any photograph is embedded or used as `og:image`:

1. Confirm Keith (or rights holder) cleared **that file** for the
   intended use (web, print, client brochure, etc.).
2. Record photographer credit from file metadata when available.
   If metadata is empty, use the STYLE_GUIDE placeholder — do not
   invent a name.
3. Update the draft `figures` entry and `PHOTO_CAPTIONS.md` with
   the resolved path, credit, and license.

Until then, keep photograph slots at `status: needed`.

## WordPress / SEO

- SVG may be blocked or sanitized on some hosts. Export PNG/WebP at
  publish width from the repo SVG when the operator requires raster.
- `FIGURE_SEO.md` lists `alt`, title, and filename slugs for the
  three diagrams. Match those on upload; do not keyword-stuff.

## What this file does not cover

- Client furniture photos, warranty photos, or field service images
  (case-by-case consent).
- Third-party logos or meter manufacturer marks in future photo fills
  (trademark/fair-use review before publish).

## Change log

| Date | Change |
| --- | --- |
| 2026-09-14 | Initial RIGHTS.md; three original SVGs registered |
