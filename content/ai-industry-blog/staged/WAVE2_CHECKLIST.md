# Wave 2 graphics checklist (42 drafts)

Use this when adding draft **43+** or remapping figures.

## Quality bar (required)

Every figure must **earn its place** in the article it ships with:

1. **Relevance** — the diagram teaches something the adjacent section argues; no “logo stack” padding.
2. **Clarity** — one main idea per SVG; short labels; no empty decorative chrome (tight artboards).
3. **Accuracy** — schematics only; no fabricated benchmarks, scores, or vendor UIs.
4. **Novelty-safe** — public industry concepts; no COSMOS/KMesh/ModelRater internals.
5. **Density cap** — default **≤2 figures** per draft; a third only for eval/safety deep dives (e.g. draft 09).

Before adding a slug to `wave2_draft_figure_plan.json`, ask: *If this figure were deleted, would the draft lose explanatory power?* If not, do not embed.

Shared assets (e.g. era comparison) belong on **at most ~5 drafts** where era framing is the thesis — not every chronology piece.

## Pipeline

1. Add SVG under `assets/<slug>/` with a **new** filename (extend `render_graphics.py` → `render_wave2()` or add wave-3 section).
2. Register metadata in `staged/asset_catalog_wave2.json` (`file`, `alt`, `caption`).
3. Map draft → slugs in `staged/wave2_draft_figure_plan.json` (respect quality bar above).
4. Run `python3 content/ai-industry-blog/scripts/render_graphics.py` then `embed_wave2_figures.py`.
5. Append row to `GRAPHICS_INDEX.md` wave-2 table.
6. Optional: add copy-paste block to `staged/FIGURE_EMBEDS.md`.

## Wave 2 library (14 new slugs)

| Slug | File | Type |
|------|------|------|
| `infographic-context-window-literacy` | `infographic-context-window.svg` | Token budget bar |
| `infographic-training-inference-cost` | `infographic-training-inference.svg` | Capex/opex schematic |
| `infographic-data-flywheel` | `infographic-data-flywheel.svg` | Data loop |
| `comparison-era-capability-2020-2023-2026` | `fig-02-era-comparison.svg` | Era columns (sparse use) |
| `flowchart-safety-evals-release` | `fig-02-safety-evals-flow.svg` | Safety gate flow |
| `diagram-red-team-vs-eval-harness` | `fig-02-red-team-eval.svg` | Red team vs harness |
| `topology-open-vs-closed-deployment` | `infographic-topology.svg` | Deployment topology |
| `diagram-multimodal-pipeline` | `fig-02-multimodal-pipeline.svg` | Multimodal fuse |
| `swimlane-agent-orchestration` | `fig-02-agent-swimlanes.svg` | Agent swimlanes |
| `decision-tree-ai-compliance` | `decision-tree-compliance.svg` | Compliance tree |
| `callout-inference-cost-drivers` | `callout-cost-drivers.svg` | Callout (**illustrative**, draft 31 only) |
| `diagram-rag-vs-long-context` | `fig-02-rag-vs-context.svg` | RAG vs window |
| `infographic-moe-routing` | `infographic-moe.svg` | MoE router |
| `flowchart-prompt-injection-defenses` | `fig-02-prompt-injection.svg` | Injection layers |

## Draft coverage

All files in `drafts/01-…` through `drafts/42-…` have `figures:` front matter and embedded `<figure>` blocks after the lede. Counts are curated (mostly 1–2 figures; draft 09 has 3).

## Guardrails

- No COSMOS/KMesh/ModelRater art; no fake benchmarks or product UIs.
- Callouts without primary citations must say **Illustrative** in caption or footnote.
- Law diagrams: “not legal advice” in caption where applicable.
