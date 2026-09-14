---
title: "Hopper: the transformer as a product requirement"
dek: H100 did not invent attention. It is the first NVIDIA GPU that behaves as if attention is the job.
slug: 18-hopper-transformer-factory
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
portrait: null
figures:
  - ../assets/18-hopper-transformer-factory/historical-timeline.svg
  - ../assets/18-hopper-transformer-factory/architecture-diagram.svg
---
# Hopper: the transformer as a product requirement

By the time NVIDIA announced Hopper and the H100 in 2022, the transformer was no longer a paper from 2017. It was the training workload that ate clusters. NVIDIA’s public Hopper materials talk about a Transformer Engine: hardware and software that mix precisions, including FP8, along a transformer-shaped path. That is a different sentence from “we made Tensor Cores faster.” It is a sentence that names the model family on the tin.



<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/18-hopper-transformer-factory/historical-timeline.svg" alt="Timeline of public milestones for Hopper: the transformer as a product requirement: dated anchors from press releases, papers, and product records — not live benchmark scores." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Calendar anchors for this piece. Years follow the essay; verify against Sources before publication.</figcaption>
</figure>


FP8 is the headline format. Smaller numbers, more of them per second, more of them per byte of HBM. The bargain is familiar: if the training recipe can stand the rounding, the chip will look twice as clever in a slide. Hopper’s software story — cuDNN, Transformer Engine libraries, later FlashAttention-class kernels that may or may not sit in NVIDIA’s tree — is about making that bargain default for the models people were actually running. GPT-class training is matrix math plus a memory-system problem. Hopper is aimed at both.

NVLink 4 and the NVSwitch generation that accompanies Hopper are how eight or sixteen H100s become a node, and how nodes become a rack. The chip is not only an SM design. It is a claim about a scale-up domain. People started quoting H100-count the way they had quoted A100-count, then discovered that the count without the switch topology is a lie. Hopper is where that lie got expensive enough to notice.

A second public fact: H100 shipped into a shortage. Cloud prices, secondary-market listings, and company filings through 2023–2024 made the board a character in business journalism. This article will not recite stock prices. It will say that a GPU generation’s meaning is partly its scarcity. When a chip is scarce, software people write to the chip they can get, and researchers time papers to cluster grants. Hopper’s cultural footprint is that scarcity as much as FP8.

The software that made Hopper look like a transformer factory is also public: Transformer Engine libraries, cuDNN paths, later fused attention kernels in the frameworks. Some of those kernels came from NVIDIA. Some came from papers and university groups that NVIDIA then had to keep up with. The factory is not only a die. It is a race between a vendor library and a GitHub repo that implemented the memory-efficient attention before the vendor slide caught up. That race is the 2022–2024 plot under the product name.

HPC is still on the slide. H100 has an FP64 story. Some sites bought it for simulation. The gravity is elsewhere. You can feel it in the keynote demos, in the partner announcements, in the way “for LLMs” became a default clause. Volta had to convince the world that deep learning was a GPU job. Hopper assumes the argument is over and optimizes the winner.

If you want a physical object, an H100 SXM in a tray next to its NVSwitch backplane is the honest one. The module alone looks like a thicker A100. The backplane is the tell. Hopper wants friends.

This is not a review of whether FP8 training “works.” It works when the recipe is written for it, and it does not when it isn’t. The historical event is the naming. A GPU vendor put the dominant model architecture into the product name of a feature. That is how you know the workload is no longer a guest.







<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/18-hopper-transformer-factory/architecture-diagram.svg" alt="Architecture diagram for Hopper: the transformer as a product requirement: illustrative GPU or datacenter shape from the public record, not an official vendor block diagram." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Illustrative system shape for the argument — protocol and architecture, not scraped silicon photography unless noted.</figcaption>
</figure>
## Sources

- NVIDIA Hopper architecture / H100 public whitepapers and GTC 2022 launch materials (Transformer Engine, FP8).
- NVIDIA NVLink 4 / NVSwitch public scale-up descriptions for HGX H100.
- Public cloud and press record of H100 scarcity in 2023–2024 (treat as context, not a price table).
- Vaswani et al., “Attention Is All You Need,” 2017 (the model family Hopper names, already public).
