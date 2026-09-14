# Graphics index — ai-evals-benchmarks-explainers

Two original SVGs per slug under `assets/<slug>/`:

| File | Role |
| --- | --- |
| `historical-timeline.svg` | Four dated anchors from `scripts/pack_data.py` |
| `instrument-chart.svg` | Scoring-shape diagram (`chart` key in pack data) |

Regenerate:

```bash
cd content/ai-evals-benchmarks-explainers/scripts
python3 build_pack_data.py   # after front-matter edits
python3 generate_graphics.py
python3 inject_figures.py
```

Articles embed HTML `<figure>` with `alt` and `<figcaption>` for SEO. Rights: `RIGHTS.md`.

No leaderboard screenshots, no vendor logos, no generated researcher portraits.
