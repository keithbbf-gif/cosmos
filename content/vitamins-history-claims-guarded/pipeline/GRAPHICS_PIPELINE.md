# Graphics pipeline — vitamins-history-claims-guarded

## Stages

1. **Staged** — rasters in `staged/images/`, SVG in `staged/graphics/`, embed snippets in `staged/FIGURE_EMBEDS.md`.
2. **Human revise** — editor picks which draft receives which figure; captions stay claims-safe.
3. **Publish** — reproduce CC BY credit lines on the live page; do not strip `<figure>` semantics.

## Verify

```bash
python3 content/vitamins-history-claims-guarded/pipeline/verify_staged_graphics.py
python -m pytest tests/test_vitamins_history_graphics.py -q
```

The verify script:

- Parses every registered SVG as XML.
- Confirms every raster in `pipeline/image_sources.json` exists and is non-trivial size.
- Writes `staged/image_manifest.json` with SHA-256 checksums.

## Adding a raster

1. Confirm license on Wikimedia Commons, Wellcome, LOC, or another archive — **no AI faces**.
2. Download into `staged/images/` with a descriptive filename.
3. Add a row to `pipeline/image_sources.json` and `RIGHTS.md`.
4. Add a `<figure>` block to `staged/FIGURE_EMBEDS.md` mapped to a `draft_slug`.
5. Re-run verify and pytest.

## SVG conventions

- ViewBox width **1200** for spread timelines.
- Include `<title>` and `<desc>` for accessibility (mirrors SEO intent).
- Palette tokens: paper `#F4F0E6`, ink `#1A1814`, accent brown `#8B4513`, accent blue `#2F5F6F`.
- Figure label upper-left: `Fig. NN` in small caps.
