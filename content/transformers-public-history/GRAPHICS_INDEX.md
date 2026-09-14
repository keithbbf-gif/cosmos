# Graphics index — transformers-public-history

Six original SVG figures support the staged reading pack. Each has a matching HTML embed in `staged/FIGURE_EMBEDS.md` and is wired into at least one draft card for on-page SEO.

| ID | File | Role | Primary draft |
| --- | --- | --- | --- |
| tph-fig-01 | `staged/graphics/fig-01-first-public-timeline.svg` | First-public milestone axis (2017–2026) | `00-reading-rules.md` |
| tph-fig-02 | `staged/graphics/fig-02-transformer-stack-2017.svg` | 2017 encoder–decoder stack | `01-attention-is-all-you-need-2017.md` |
| tph-fig-03 | `staged/graphics/fig-03-attention-compute-flow.svg` | Scaled dot-product flow | `02-scaled-dot-product-attention.md` |
| tph-fig-04 | `staged/graphics/fig-04-three-topologies-2018.svg` | 2018 topology fork | `09-three-topologies.md` |
| tph-fig-05 | `staged/graphics/fig-05-context-mechanisms-timeline.svg` | Context / memory mechanisms | `37-flashattention-2022.md` |
| tph-fig-06 | `staged/graphics/fig-06-sparse-hybrid-landscape.svg` | Sparse & hybrid public cards | `48-hybrid-sparse-2024-2026.md` |

## Verify

```bash
python3 content/transformers-public-history/pipeline/verify_staged_graphics.py
pytest tests/test_transformers_public_history_graphics.py -q
```

Policy: `RIGHTS.md`. Prose fence: `README.md` and per-card `private_systems: excluded`.

## Portrait policy

No portraits in this pass. Timelines and architecture schematics only.
