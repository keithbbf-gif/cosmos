# Staging — drawer construction history (IMAGE + SEO)

PR **#527** adds pack-authored joinery SVGs and WordPress-ready `<figure>` blocks. Shop photographs remain **`status: needed`** until files are pulled from `D:\BBF\BBF Photos`.

## Regenerate

From repo root:

```bash
python3 content/drawer-construction-history/scripts/generate_drawer_svgs.py
python3 content/drawer-construction-history/scripts/inject_dch_figures.py
python3 content/drawer-construction-history/scripts/validate_dch_graphics.py
pytest tests/test_dch_graphics.py -q
```

## Editor checks

- `RIGHTS.md` — licenses and BBF ledger
- `SEO_MAP.md` — alt text and featured-image rules
- `GRAPHICS_INDEX.md` — slug → schematic kind
- `PHOTO_MANIFEST.md` — unchanged pull list for Keith’s library

Do not publish or set featured images to placeholders.
