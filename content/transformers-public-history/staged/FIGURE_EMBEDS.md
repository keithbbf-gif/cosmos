# Staged HTML embeds — transformers public history

Paths are relative to site root `content/transformers-public-history/`. Copy into CMS HTML or keep inline in numbered drafts. Captions are **architecture history only** — no product pitches, no unreleased-block reconstruction.

---

## Series hub (`00-reading-rules.md`)

```html
<figure class="tph-figure tph-figure--spread">
  <img src="content/transformers-public-history/staged/graphics/fig-01-first-public-timeline.svg"
       alt="Timeline of selected first-public transformer architecture milestones from 2017 to 2026"
       width="1200" height="520" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> Selected first-public milestones for blocks covered in this pack (editorial schematic). Dates follow arXiv v1 or official release classes — not conference program years.</figcaption>
</figure>
```

---

## Draft slug: `attention-is-all-you-need-2017` (tph-01)

```html
<figure class="tph-figure tph-figure--architecture">
  <img src="content/transformers-public-history/staged/graphics/fig-02-transformer-stack-2017.svg"
       alt="Schematic diagram of the 2017 Transformer encoder and decoder stacks with attention and feed-forward sublayers"
       width="960" height="640" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> Encoder–decoder stack as publicly specified in <em>Attention Is All You Need</em> (12 June 2017). Editorial schematic — not a scan of the paper figure panel.</figcaption>
</figure>
```

---

## Draft slug: `scaled-dot-product-attention` (tph-02)

```html
<figure class="tph-figure tph-figure--architecture">
  <img src="content/transformers-public-history/staged/graphics/fig-03-attention-compute-flow.svg"
       alt="Flowchart of scaled dot-product attention from Q K and V through softmax to output"
       width="900" height="420" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> Dataflow for scaled dot-product attention (§3.2.1, arXiv:1706.03762). Shows the public equation form used throughout the series.</figcaption>
</figure>
```

---

## Draft slug: `three-topologies` (tph-09)

```html
<figure class="tph-figure tph-figure--architecture">
  <img src="content/transformers-public-history/staged/graphics/fig-04-three-topologies-2018.svg"
       alt="Comparison of encoder-decoder decoder-only and encoder-only transformer topologies with first-public dates"
       width="1100" height="480" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> Three incompatible ways to stack the 2017 layer after the October 2018 fork (taxonomy card tph-09). Masks and training objectives differ; the word “transformer” does not.</figcaption>
</figure>
```

---

## Draft slug: `flashattention-2022` (tph-37)

```html
<figure class="tph-figure tph-figure--spread">
  <img src="content/transformers-public-history/staged/graphics/fig-05-context-mechanisms-timeline.svg"
       alt="Timeline of public sparse attention KV-cache and IO-aware attention mechanisms from 2019 to 2023"
       width="1200" height="500" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> Public mechanisms on the length and memory axis preceding and surrounding FlashAttention (27 May 2022). Not a vendor context-window chart.</figcaption>
</figure>
```

---

## Draft slug: `hybrid-sparse-2024-2026` (tph-48)

```html
<figure class="tph-figure tph-figure--architecture">
  <img src="content/transformers-public-history/staged/graphics/fig-06-sparse-hybrid-landscape.svg"
       alt="Concept map of public sparse hybrid state-space and MoE routes from the 2017 attention block"
       width="1000" height="520" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> Editorial map of public sparse, hybrid, and routing cards in the 2024–2026 band (draft tph-48). Names label cited artifacts only.</figcaption>
</figure>
```
