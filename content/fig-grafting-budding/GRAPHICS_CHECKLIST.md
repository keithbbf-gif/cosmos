# Graphics checklist — fig grafting & budding pack

**Target for this PR:** core teaching plates embedded with SEO `<figure>` blocks
in anatomy, dormant graft, chip-bud, and aftercare drafts; all SVGs registered
in `GRAPHICS_INDEX.md` and `RIGHTS.md`.

## Pipeline

1. Author or update SVG under `assets/diagrams/svg/` (palette: fig history pack — ink `#2c2416`, leaf `#4a6741`, paper `#f5f0e8`).
2. Register ID + alt in `GRAPHICS_INDEX.md`.
3. Add licence row in `RIGHTS.md`.
4. Embed per `templates/figure-block.md` (`<!-- figure-id: ... -->` + `<figure>`).
5. `python3 content/fig-grafting-budding/_check.py`
6. `python3 content/fig-grafting-budding/validate_graphics.py`
7. Human: swap schematic heroes for `D:\FIGS` union close-ups before publish (`PHOTO_NOTES.md`).

## Sign-off (IMAGE+SEO pass)

- [x] `shared.cambium-cross-section` — file on disk, RIGHTS row, embed in 05-01
- [x] `shared.graft-cuts-plate` — file on disk, RIGHTS row, embeds in 06-01–06-04
- [x] `shared.chip-bud-sequence` — file on disk, RIGHTS row, embed in 08-01
- [x] `shared.aftercare-first-three-weeks` — file on disk, RIGHTS row, embed in 10-01
- [ ] Optional: orchard_slot + `<figure>` on remaining 39 drafts (future raster pass)
- [ ] Pre-publish: verify SVG footer IDs match this index
