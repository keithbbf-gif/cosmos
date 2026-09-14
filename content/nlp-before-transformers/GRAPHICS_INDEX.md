# Graphics index — nlp-before-transformers

Three figures per essay (51 essays):

| # | Asset | Role |
| --- | --- | --- |
| 1 | `assets/<slug>/historical-timeline.svg` | Four dated anchors (from `scripts/pack_data.py`) |
| 2 | `assets/<slug>/concept-chart.svg` | Stage-scoped method schematic (`chart` key) |
| 3 | `REGISTRY.toml` plate | One archival Commons diagram (no portraits) |

Regenerate:

```bash
cd content/nlp-before-transformers/scripts
python3 build_pack_data.py
python3 generate_graphics.py
python3 inject_figures.py
python3 check_figures.py
```

Articles embed HTML `<figure>` with descriptive `alt` and `<figcaption>` for SEO. Policy:
`PHOTO_NOTES.md`. Rights: `RIGHTS.md`.

## Stage → concept chart template

| Stage folder | `chart` key |
| --- | --- |
| `stage-01-origins` | `channel` |
| `stage-02-symbols` | `parse_tree` |
| `stage-03-counts-hmms` | `hmm_chain` |
| `stage-04-structured` | `crf_features` |
| `stage-05-vectors` | `vector_space` |
| `stage-06-neural-warmup` | `nn_stack` |
| `stage-07-seq2seq` | `seq2seq_attn` |
| `stage-08-tasks-rulers` | `shared_task` |

## Portrait policy

`portrait: null` and `portrait_status: essay-only` on every draft. No generated likenesses of
living or historical researchers. Archival plates are diagrams, spectra, trees, and hardware.
