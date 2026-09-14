# Graphics pipeline — transformers-public-history

1. Edit SVG under `staged/graphics/` (keep `<title>` and `<desc>` for accessibility).
2. Register paths in `pipeline/image_sources.json`.
3. Mirror embeds in `staged/FIGURE_EMBEDS.md` and in the linked draft markdown (HTML `<figure>`).
4. Run `python3 pipeline/verify_staged_graphics.py` from this folder’s parent (`content/transformers-public-history/`).
5. Run `pytest tests/test_transformers_public_history_graphics.py`.

The verify script regenerates `staged/image_manifest.json` with SHA-256 checksums. It does not fetch network assets — this pack is SVG-only.
