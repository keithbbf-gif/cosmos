# Per-article graphics checklist

Copy into PR description or article folder as `GRAPHICS_QA.md` when requesting editor move to `articles/ready/`.

## Article: ____________________  Slug: ____________________

### Coverage

- [ ] **≥2 figures** embedded (target **3–5+** when narrative supports it)
- [ ] Mix includes at least one **non-fruit** visual (map, timeline, plate, process, or chart)
- [ ] No decorative images without informational caption

### Registration

- [ ] Every `<!-- figure-id: ... -->` appears in `GRAPHICS_INDEX.md`
- [ ] Every raster path appears in `IMAGE_SOURCES.md` with license
- [ ] No broken relative paths from `articles/_staging/<slug>/index.md`

### Labels & honesty

- [ ] Schematics labeled *schematic* / *not to scale* in caption or SVG footer
- [ ] No fake historical photographs
- [ ] Cultivar / date claims match writer sources or marked *c.* / *approx.*

### Technical

- [ ] `python3 tools/fig_graphics_validate.py content/fig-history-ancient-to-today` exits 0
- [ ] SVGs render in preview (no missing entities / broken XML)
- [ ] Raster width ≥1600 px for hero figures (or editor exception noted)

### Sign-off

| Role | Name | Date |
|------|------|------|
| Graphics | | |
| Writer | | |
| Editor | | |
