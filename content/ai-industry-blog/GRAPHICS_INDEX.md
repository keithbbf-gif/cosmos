# Graphics index — AI industry blog

Publish-ready **SVG** figures for drafts under `content/ai-industry-blog/`. All art uses a shared magazine palette (warm paper `#FAF8F5`, ink `#141414`, accent `#1E4D6B`, highlight `#B85C38`). Figures depict **generic public concepts only** — no COSMOS/KMesh/ModelRater internals, no patent art, no mock product UIs.

**Regenerate:** `python3 content/ai-industry-blog/scripts/render_graphics.py`

**Staged embeds:** copy blocks from [`staged/FIGURE_EMBEDS.md`](staged/FIGURE_EMBEDS.md) into draft markdown.

---

## Timelines (2020→2026)

| Slug | File | Use when |
|------|------|----------|
| `industry-milestones-2020-2026` | `assets/industry-milestones-2020-2026/timeline.svg` | Era overview, “what changed since 2020” |
| `compute-and-scaling-2020-2026` | `assets/compute-and-scaling-2020-2026/timeline.svg` | Training scale, hardware, inference economics |
| `open-weights-epochs-2020-2026` | `assets/open-weights-epochs-2020-2026/timeline.svg` | Open models, licenses, local deployment |

## Architecture (generic)

| Slug | File | Use when |
|------|------|----------|
| `architecture-transformer-block` | `assets/architecture-transformer-block/diagram.svg` | Explain attention / blocks |
| `architecture-rag-pipeline` | `assets/architecture-rag-pipeline/diagram.svg` | Grounding, retrieval, citations |
| `architecture-fine-tuning-stages` | `assets/architecture-fine-tuning-stages/diagram.svg` | SFT, preferences, adapters |
| `architecture-inference-stack` | `assets/architecture-inference-stack/diagram.svg` | Serving, gateways, batching |
| `architecture-agent-tool-loop` | `assets/architecture-agent-tool-loop/diagram.svg` | Tool use, agent loops (conceptual) |

## Evaluation & benchmarks

| Slug | File | Use when |
|------|------|----------|
| `eval-benchmark-families` | `assets/eval-benchmark-families/explainer.svg` | Map MMLU-style suites to categories |
| `eval-harness-pipeline` | `assets/eval-harness-pipeline/explainer.svg` | Describe reproducible eval runs |
| `eval-leaderboard-caveats` | `assets/eval-leaderboard-caveats/explainer.svg` | Contamination, judges, prompt sensitivity |

## Regulation & governance

| Slug | File | Use when |
|------|------|----------|
| `regulation-eu-ai-act` | `assets/regulation-eu-ai-act/timeline.svg` | EU AI Act phases (verify EUR-Lex) |
| `regulation-us-federal-2023-2026` | `assets/regulation-us-federal-2023-2026/timeline.svg` | U.S. executive / agency milestones |
| `regulation-global-snapshot-2026` | `assets/regulation-global-snapshot-2026/timeline.svg` | Cross-jurisdiction context |

---

## Embed pattern (markdown / HTML)

From a draft in `content/ai-industry-blog/drafts/<name>.md`:

```html
<figure class="blog-figure">
  <img
    src="../assets/industry-milestones-2020-2026/timeline.svg"
    alt="Timeline of public AI industry milestones from 2020 through 2026"
    width="1200"
    loading="lazy"
  />
  <figcaption>
    <strong>Figure 1.</strong> Selected public milestones in generative AI and policy.
    <em>Illustrative; not exhaustive.</em>
  </figcaption>
</figure>
```

Adjust the relative `src` if the draft lives in a subfolder. Prefer `width="1200"` (native artboard) and let CSS cap `max-width: 100%` on publish.

---

## Draft tag hints

Optional front-matter tags for discoverability:

- `graphics:timeline`
- `graphics:architecture`
- `graphics:eval`
- `graphics:regulation`

---

## Novelty & accuracy

- Timelines cite **widely reported** public events; footnotes remind readers to verify primary sources (especially law).
- Diagrams are **schematics**, not implementations.
- Update copy in `render_graphics.py` and re-run the renderer when dates or labels need revision.
