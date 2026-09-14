# FigRoots blog scripts

## Graphics pipeline

```bash
python content/figroots-blog/scripts/graphics_pipeline.py --all
```

- Writes SVGs to `content/figroots-blog/assets/<slug>/`
- Embeds `![alt](../assets/...)` plus italic captions in drafts
- Sets `figures:` in YAML front matter
- Refreshes `GRAPHICS_INDEX.md` and `GRAPHICS_CHECKLIST.md`

Add new figures in `figroots_graphics/specs.py` and optional generators in `figroots_graphics/generators.py`, then run with `--slug <slug>` or `--all`.

`--force` regenerates SVG files. `--dry-run` skips markdown writes.
