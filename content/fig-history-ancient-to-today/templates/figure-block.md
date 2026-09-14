# Figure block template

Use in `articles/_staging/<slug>/index.md`.

## Shared SVG (reused across articles)

```markdown
<!-- figure-id: shared.timeline-master -->
![Major milestones in fig cultivation and trade, schematic timeline.](../../assets/shared/svg/timeline-fig-cultivation-master.svg)

*Figure 1. Selected milestones in fig domestication and long-distance dried-fig trade. Schematic timeline; dates approximate.*
```

## Slug-specific raster (with credit)

```markdown
<!-- figure-id: ancient-egypt-fig-harvest.tomb-detail -->
![Painted harvest scene with syconia, framed museum scan.](../../assets/images/ancient-egypt-fig-culture/tomb-harvest-detail.png)

*Figure 3. Painted harvest scene (detail). Photo: Example Museum. License: CC BY-SA 4.0 — see IMAGE_SOURCES.md.*
```

## Rules

1. `figure-id` = `{slug}.{short-name}` or `shared.{name}` — must exist in `GRAPHICS_INDEX.md`.
2. Alt text = first sentence of caption (no “image of”).
3. Never embed unlisted files; run the validator before PR.
