# GRAPHICS agent — herbal tea foodways history

## Deliverables per illustrated draft

1. Original SVG map or timeline under `assets/svg/`, **or** a cleared Commons foodways plate under `assets/images/`.
2. Lead `<figure class="htf-figure">` in each `stage-*/*.md` after frontmatter (WXR-safe HTML).
3. SEO frontmatter: `figure_id`, `image_rights: documented`, `meta_description`, `image_pass`.
4. Rows in `GRAPHICS_INDEX.md` and `IMAGE_SOURCES.md`; license row in `RIGHTS.md`.

## Hard rules

- **Never** AI faces, AI lifestyle pours, or unidentified stock “wellness tea” renders.
- **Never** materia-medica indication graphics (anatomy charts, “benefits” icons, dose tables).
- Prefer botanical plates, market still lifes, vessels, dried calyces, and editorial schematics.
- Alt text: plain language; name the plant or object, not a health outcome.
- Captions: one teaching sentence + `<em>Rights:</em>` line pointing to `RIGHTS.md` or Commons.
- Diagrams: follow `assets/_shared/editorial-palette.md`.

## Tooling

```text
python3 content/herbal-tea-foodways-history/tools/download_commons.py
python3 content/herbal-tea-foodways-history/tools/embed_figures.py
python3 content/herbal-tea-foodways-history/tools/check_figures.py
python3 content/herbal-tea-foodways-history/tools/lint_claims.py
```

## Acceptance

- [ ] Every draft has exactly one lead figure and documented rights.
- [ ] `check_figures.py` and `lint_claims.py` pass.
- [ ] No medical-payoff language in captions (checker enforces sniff test).
