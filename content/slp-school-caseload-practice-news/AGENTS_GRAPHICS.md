# GRAPHICS agent — school SLP caseload / practice news

## Deliverables

1. Original **SVG infographics** under `assets/<slug>/` for each explainer (caseload, workload, IDEA, ASHA survey — educational schematics only).
2. `embeds/<slug>.md` with schema.org `<figure>` blocks for CMS paste.
3. Inline figures after the first `##` in each `articles/*.md`.
4. `RIGHTS.md` and `GRAPHICS_INDEX.md` kept in sync with assets.

## Regenerate

```bash
cd content/slp-school-caseload-practice-news
python3 scripts/generate_graphics.py
python3 scripts/regenerate_graphics_index.py
python3 check_pack.py
```

## Hard rules

- No PHI, no fictional student names, **no therapy worksheets**.
- No AI faces or classroom photography.
- Infographics summarize public policy and survey facts — not billing instructions or union advice.
