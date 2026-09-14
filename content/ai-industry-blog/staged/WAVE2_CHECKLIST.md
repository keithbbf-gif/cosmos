# Wave 2 graphics checklist (42 drafts)

Use this when adding draft **43+** or remapping figures.

## Pipeline

1. Add SVG under `assets/<slug>/` with a **new** filename (extend `render_graphics.py` → `render_wave2()` or add wave-3 section).
2. Register metadata in `staged/asset_catalog_wave2.json` (`file`, `alt`, `caption`).
3. Map draft → slugs in `staged/wave2_draft_figure_plan.json`.
4. Run `python3 content/ai-industry-blog/scripts/embed_wave2_figures.py` (idempotent via `<!-- ai-blog-figures:begin/end -->`).
5. Append row to `GRAPHICS_INDEX.md` wave-2 table.
6. Optional: add copy-paste block to `staged/FIGURE_EMBEDS.md`.

## Wave 2 library (14 new slugs)

| Slug | File | Type |
|------|------|------|
| `infographic-context-window-literacy` | `infographic-context-window.svg` | Budget explainer |
| `infographic-training-inference-cost` | `infographic-training-inference.svg` | Capex/opex schematic |
| `infographic-data-flywheel` | `infographic-data-flywheel.svg` | Data loop |
| `comparison-era-capability-2020-2023-2026` | `fig-02-era-comparison.svg` | Era columns |
| `flowchart-safety-evals-release` | `fig-02-safety-evals-flow.svg` | Safety gate flow |
| `diagram-red-team-vs-eval-harness` | `fig-02-red-team-eval.svg` | Red team vs harness |
| `topology-open-vs-closed-deployment` | `infographic-topology.svg` | Deployment topology |
| `diagram-multimodal-pipeline` | `fig-02-multimodal-pipeline.svg` | Multimodal fuse |
| `swimlane-agent-orchestration` | `fig-02-agent-swimlanes.svg` | Agent swimlanes |
| `decision-tree-ai-compliance` | `decision-tree-compliance.svg` | Compliance tree |
| `callout-inference-cost-drivers` | `callout-cost-drivers.svg` | Callout (illustrative) |
| `diagram-rag-vs-long-context` | `fig-02-rag-vs-context.svg` | RAG vs window |
| `infographic-moe-routing` | `infographic-moe.svg` | MoE router |
| `flowchart-prompt-injection-defenses` | `fig-02-prompt-injection.svg` | Injection layers |

## Draft coverage

All files in `drafts/01-…` through `drafts/42-…` have `figures:` front matter and embedded `<figure>` blocks after the lede (wave 1 + wave 2 assets per plan).

## Guardrails

- No COSMOS/KMesh/ModelRater art; no fake benchmarks or product UIs.
- Callouts without primary citations must say **Illustrative** in caption or footnote.
- Law diagrams: “not legal advice” in caption where applicable.
