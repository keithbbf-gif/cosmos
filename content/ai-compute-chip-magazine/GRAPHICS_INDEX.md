# Graphics index — ai-compute-chip-magazine

Two original SVGs per article under `assets/<slug>/`:

| File | Role |
| --- | --- |
| `historical-timeline.svg` | Dated public anchors (press, papers, SKUs) |
| `architecture-diagram.svg` | Illustrative system shape for the article theme |

Selected articles also ship a **Wikimedia Commons** product photo (hardware only).
See `RIGHTS.md` for licenses.

Regenerate:

```bash
cd content/ai-compute-chip-magazine/scripts
python3 build_pack_data.py   # after front-matter / anchor edits
python3 generate_graphics.py
python3 fetch_photos.py      # optional; CC/PD files only
python3 inject_figures.py
```

Articles embed HTML `<figure>` with descriptive `alt` and `<figcaption>` for SEO.
Class: `chip-figure` (SVG) and `chip-figure-photo` (licensed photos).

No vendor logo sheets, no leaderboard screenshots, no AI-generated faces.
