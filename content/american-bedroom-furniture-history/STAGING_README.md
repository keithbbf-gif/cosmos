---
title: Staging readme — American bedroom furniture history
status: draft
voice_check: edited
series: american-bedroom-furniture-history
---

# Staging readme

Image + SEO pass on the **PR #516 fill / PR #450 editor** stack (`cursor/american-bedroom-editor-unify-75a9`). Full pack **01–45**.

## What shipped in this pass

1. `assets/figures/REGISTRY.toml` — hot-link registry (Met Open Access, NGA CC0, LACMA PD, cleared Commons)
2. `assets/diagrams/<slug>/lead-timeline.svg` — original chapter timelines (furniture silhouettes only; no portraits)
3. `assets/diagrams/series-overview.svg` — pack-level axis diagram for `INDEX.md`
4. `_editorial/figure_assignments.toml` — one museum-open plate per slug (object photos only; no gallery crowd shots)
5. `_editorial/generate_diagrams.py` / `embed_figures.py` / `check_figures.py` — Fig. 1 museum + Fig. 2 SVG embed + QA
6. `RIGHTS.md` — human-readable license table (no AI-generated images)
7. Lead figures + `meta_description`, `figure_id`, `diagram_id` frontmatter in all **45** drafts

## QA commands

From repo root:

```bash
python3 content/american-bedroom-furniture-history/_editorial/generate_diagrams.py
python3 content/american-bedroom-furniture-history/_editorial/embed_figures.py
python3 content/american-bedroom-furniture-history/_editorial/check_figures.py
```

## WordPress import notes

- Figures use absolute Commons URLs; no binaries in git.
- Figcaption includes `<em>Rights:</em>` line for layout CSS.
- Re-run `RIGHTS.md` spot checks before publish; Met Open Access status can change.
