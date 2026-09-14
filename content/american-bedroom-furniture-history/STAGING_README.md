---
title: Staging readme — American bedroom furniture history
status: draft
voice_check: edited
series: american-bedroom-furniture-history
---

# Staging readme

Image + SEO pass for PR **#462** editor branch (`cursor/american-bedroom-furniture-editor-2bbe`). Builds on staged drafts **07–45** only.

## What shipped in this pass

1. `assets/figures/REGISTRY.toml` — hot-link registry (Met CC0, NGA CC0, LACMA PD, Commons CC)
2. `_editorial/figure_assignments.toml` — one museum plate per slug
3. `_editorial/embed_figures.py` / `check_figures.py` — `<figure class="abfh-figure">` embed + QA
4. `RIGHTS.md` — human-readable license table (no AI-generated images)
5. Lead figures + `meta_description` / `figure_id` frontmatter in all 39 drafts

## QA commands

From repo root:

```bash
python3 content/american-bedroom-furniture-history/_editorial/embed_figures.py
python3 content/american-bedroom-furniture-history/_editorial/check_figures.py
```

## WordPress import notes

- Figures use absolute Commons URLs; no binaries in git.
- Figcaption includes `<em>Rights:</em>` line for layout CSS.
- Re-run `RIGHTS.md` spot checks before publish; Met Open Access status can change.
