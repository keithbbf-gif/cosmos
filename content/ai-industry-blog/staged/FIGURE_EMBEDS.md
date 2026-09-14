# Staged figure embeds (copy into drafts)

Paths assume the draft file sits in `content/ai-industry-blog/drafts/`. Each block includes a captioned `<figure>`.

---

## Timelines

### Industry milestones

```html
<figure class="blog-figure">
  <img src="../assets/industry-milestones-2020-2026/timeline.svg" alt="Public AI industry milestones from 2020 to 2026" width="1200" loading="lazy" />
  <figcaption><strong>Figure.</strong> A selective timeline of research, product, and policy anchors that shaped the generative-AI era. <em>Not a complete catalog.</em></figcaption>
</figure>
```

### Compute and scaling

```html
<figure class="blog-figure">
  <img src="../assets/compute-and-scaling-2020-2026/timeline.svg" alt="Compute and scaling narrative from 2020 to 2026" width="1200" loading="lazy" />
  <figcaption><strong>Figure.</strong> How training scale, hardware cycles, and serving economics entered mainstream industry discourse.</figcaption>
</figure>
```

### Open-weights epochs

```html
<figure class="blog-figure">
  <img src="../assets/open-weights-epochs-2020-2026/timeline.svg" alt="Open model weights epochs from 2020 to 2026" width="1200" loading="lazy" />
  <figcaption><strong>Figure.</strong> Public releases that expanded who could fine-tune and deploy models outside hosted APIs.</figcaption>
</figure>
```

---

## Architecture

### Transformer block

```html
<figure class="blog-figure">
  <img src="../assets/architecture-transformer-block/diagram.svg" alt="Generic transformer block diagram" width="1100" loading="lazy" />
  <figcaption><strong>Figure.</strong> A textbook-style transformer block: attention, residuals, and feed-forward layers stacked depth-wise.</figcaption>
</figure>
```

### RAG pipeline

```html
<figure class="blog-figure">
  <img src="../assets/architecture-rag-pipeline/diagram.svg" alt="Generic retrieval-augmented generation pipeline" width="1100" loading="lazy" />
  <figcaption><strong>Figure.</strong> Retrieval-augmented generation: embed the query, fetch ranked passages, then condition the language model on cited context.</figcaption>
</figure>
```

### Fine-tuning stages

```html
<figure class="blog-figure">
  <img src="../assets/architecture-fine-tuning-stages/diagram.svg" alt="Generic fine-tuning stages from base model to deployment" width="1100" loading="lazy" />
  <figcaption><strong>Figure.</strong> Common post-training path: supervised fine-tuning, preference alignment, and parameter-efficient adapters before release.</figcaption>
</figure>
```

### Inference stack

```html
<figure class="blog-figure">
  <img src="../assets/architecture-inference-stack/diagram.svg" alt="Generic LLM inference serving stack" width="1100" loading="lazy" />
  <figcaption><strong>Figure.</strong> Simplified inference path from client request through gateway, scheduler, and model workers to streamed tokens.</figcaption>
</figure>
```

### Agent tool loop

```html
<figure class="blog-figure">
  <img src="../assets/architecture-agent-tool-loop/diagram.svg" alt="Conceptual agent plan-act-observe loop with tools" width="1100" loading="lazy" />
  <figcaption><strong>Figure.</strong> Conceptual agent loop: plan, call tools, observe results, update memory, repeat until a final answer is produced.</figcaption>
</figure>
```

---

## Evaluation

### Benchmark families

```html
<figure class="blog-figure">
  <img src="../assets/eval-benchmark-families/explainer.svg" alt="Families of public AI benchmarks" width="900" loading="lazy" />
  <figcaption><strong>Figure.</strong> Leaderboard suites cluster into knowledge, reasoning, coding, instruction-following, safety, and multimodal tasks — scores are not interchangeable.</figcaption>
</figure>
```

### Eval harness

```html
<figure class="blog-figure">
  <img src="../assets/eval-harness-pipeline/explainer.svg" alt="Generic evaluation harness pipeline" width="1100" loading="lazy" />
  <figcaption><strong>Figure.</strong> A reproducible eval harness versions prompts, fixes decoding settings, scores outputs, and publishes metrics with provenance.</figcaption>
</figure>
```

### Leaderboard caveats

```html
<figure class="blog-figure">
  <img src="../assets/eval-leaderboard-caveats/explainer.svg" alt="Caveats when reading AI leaderboards" width="1000" loading="lazy" />
  <figcaption><strong>Figure.</strong> Before trusting a headline score, ask about contamination, prompt sensitivity, judge bias, and checkpoint versioning.</figcaption>
</figure>
```

---

## Regulation

### EU AI Act

```html
<figure class="blog-figure">
  <img src="../assets/regulation-eu-ai-act/timeline.svg" alt="EU AI Act public implementation timeline" width="1200" loading="lazy" />
  <figcaption><strong>Figure.</strong> Staggered EU AI Act obligations as commonly summarized in compliance guides — confirm dates against EUR-Lex.</figcaption>
</figure>
```

### U.S. federal (selected)

```html
<figure class="blog-figure">
  <img src="../assets/regulation-us-federal-2023-2026/timeline.svg" alt="Selected U.S. federal AI policy milestones 2023 to 2026" width="1200" loading="lazy" />
  <figcaption><strong>Figure.</strong> Selected U.S. federal milestones (executive orders, frameworks, procurement). <em>Not legal advice.</em></figcaption>
</figure>
```

### Global snapshot

```html
<figure class="blog-figure">
  <img src="../assets/regulation-global-snapshot-2026/timeline.svg" alt="Illustrative global AI governance timeline 2020 to 2026" width="1200" loading="lazy" />
  <figcaption><strong>Figure.</strong> Parallel policy tracks across regions illustrate why cross-border AI products face fragmented obligations.</figcaption>
</figure>
```

---

## Wave 2 (infographics — see `GRAPHICS_INDEX.md`)

Copy-paste blocks for all wave-2 slugs match `staged/asset_catalog_wave2.json`. Example — context window literacy:

```html
<figure class="blog-figure">
  <img src="../assets/infographic-context-window-literacy/infographic-context-window.svg" alt="Schematic breakdown of context window budget: system, user, retrieval, and output" width="1200" loading="lazy" />
  <figcaption><strong>Figure.</strong> Advertised context is a budget across roles — not a single block of usable reasoning space.</figcaption>
</figure>
```

Automated embed for pack drafts: `python3 content/ai-industry-blog/scripts/embed_wave2_figures.py`.
