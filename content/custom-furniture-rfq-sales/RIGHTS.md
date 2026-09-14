# Image rights — custom furniture RFQ / quote-only sales

Hero figures for this staging set combine **original CC0 schematics** and **PD/CC documentary photographs**. No synthetic faces. No stock “happy couple on a white sofa” presented as our floor. Files live in `assets/`; drafts embed them with `<figure>`, descriptive `alt` text, and SEO `figcaption` captions.

Use this file as the credit ledger before any public import. When a license requires attribution, reproduce the credit line on the same page as the image (the embed script appends it to `figcaption`).

## Policy

- **Schematics** (`process-measure-quote-ack.svg`, `schematic-*.svg`) are original line art for this pack, dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
- **Raster photos** are educational: historical factories, documentary kitchens, measure prep, and warehouse logistics — **not** labeled as Bradley Brand Furniture’s current Warren floor unless a future swap uses Keith’s shop library (`PHOTO_NOTES.md`).
- **No AI-generated images.**
- **Redistribution:** JPEG/PNG files follow their Commons licenses; SVG schematics may be reused without restriction.

Full provenance table: `IMAGE_SOURCES.md`. Process overview: `GRAPHICS_INDEX.md`.

## Staged shop-adjacent photos (not Commons download in CI)

These files were copied from the verified `kitchen-island-design-guide` asset set (same Commons provenance as that pack) to avoid hammering Wikimedia during batch fetch:

| Local file | Original Commons file | License |
| --- | --- | --- |
| `cf-rfq-07-kitchen-measure-prep.jpg` | [Measuring … bright kitchen setting](https://commons.wikimedia.org/wiki/File:Measuring_a_green_apple_beside_fresh_juice_in_a_bright_kitchen_setting_during_a_healthy_lifestyle_moment.jpg) | CC BY 2.0 |
| `cf-rfq-09-tape-measure-wall.jpg` | *(duplicate of 07 for layout/tape articles)* | CC BY 2.0 |
| `cf-rfq-17-two-tapes-measure.jpg` | *(duplicate of 07 — two-tape article)* | CC BY 2.0 |
| `cf-rfq-31-wood-finish-samples.jpg` | [Mineral oil treating butcher block](https://commons.wikimedia.org/wiki/File:Mineral_oil_treating_butcher_block.png) | CC BY-SA 3.0 |

Replace with Keith’s redacted shop library frames when available; update this table and `IMAGE_SOURCES.md` in the same commit.

## License notes

- **Public domain** and **CC0** files may be used without permission; credit remains good practice for library and museum scans.
- **CC BY** and **CC BY-SA** require **attribution**; share-alike applies to adaptations — read the linked Commons file page before crop or remix.
- U.S. government record scans (warehouse logistics) are public domain; captions stay editorial.

## Verification

```bash
python3 content/custom-furniture-rfq-sales/scripts/generate_svgs.py
python3 content/custom-furniture-rfq-sales/scripts/build_manifest.py
python3 content/custom-furniture-rfq-sales/scripts/patch_manifest_urls.py
python3 content/custom-furniture-rfq-sales/scripts/stage_local_photos.py
python3 content/custom-furniture-rfq-sales/scripts/fetch_images.py
python3 content/custom-furniture-rfq-sales/scripts/embed_figures.py
python3 content/custom-furniture-rfq-sales/validate_images.py
python3 content/custom-furniture-rfq-sales/check_pack.py
```

Re-fetch rasters only when swapping a Commons file in `image_assets.json`.
