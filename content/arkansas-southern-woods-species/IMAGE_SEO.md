# Image + figure SEO — Arkansas / Southern woods pack

Staged drafts in this folder get **one lead `<figure>`** when a cleared plate or diagram exists. Figures are for readers and for import-time SEO (alt text, figcaption keywords, lazy loading).

## Policy

| Rule | Detail |
|------|--------|
| Species photos | **Real PD / CC / USDA / Commons botanical** images only — no AI-generated “wood texture” or invented tree photos. |
| Rights | Every on-disk plate has `plates/<id>/RIGHTS.md`. Diagrams: `assets/diagrams/RIGHTS.md`. |
| Lead placement | Immediately after YAML frontmatter (before the first prose paragraph). |
| CSS hooks | `asw-figure`, `asw-figure--species`, `asw-figure--diagram` |
| Frontmatter | `meta_description` (≤160 chars), `lead_figure` (`species` \| `diagram` \| `none`), `photo_status` (`cleared` \| `none`) |

## Alt text

- Name the species in plain English and Latin once: `White oak (Quercus alba) on an Ozark upland — …`
- Diagrams: state what the drawing **shows**, not “infographic”.

## Figcaption

1. **Bold** common name (and Latin in italics for species plates).
2. One sentence tying the image to Arkansas furniture / shop context (species, mill town, humidity, sawing).
3. `<span class="figure-credit">` with license and source (mirror `RIGHTS.md`).

## Embed templates

- [`embeds/species-figure-block.md`](embeds/species-figure-block.md)

## QA

Run from this directory:

```bash
python3 check_pack.py
```

Checks: plate `RIGHTS.md` pairs, required frontmatter on figure-bearing drafts, banned AI-face phrases, `<figure class="asw-figure` present when `lead_figure` is set.
