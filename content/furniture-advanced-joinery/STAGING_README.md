# Staging README — IMAGE + SEO workflow

1. **Schematics** — edit `scripts/faj_graphics_specs.json`, run `python3 scripts/generate_joinery_svgs.py`.
2. **Museum** — edit `assets/museum/museum_sources.yaml`, run `python3 scripts/fetch_museum_photos.py` (rate-limited; retries built in).
3. **Draft embeds** — after changing specs or assignments, run `python3 scripts/inject_faj_figures.py` (only while `<!-- PHOTO: -->` comments exist; otherwise edit `<figure>` blocks by hand).
4. **Validate** — `python3 scripts/validate_faj_graphics.py` (also wired in `tests/test_faj_graphics.py`).
5. **Shop pulls** — follow `PHOTO_NOTES.md`; update `RIGHTS.md` and replace `faj-shop-pending` images.

Paths in drafts are relative from `drafts/` → `../assets/...`.
