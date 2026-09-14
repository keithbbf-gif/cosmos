---
title: A board in a Google datacenter
dek: In May 2016 Google told I/O it had already been running a custom ASIC for a year. The board fit a disk slot.
slug: 34-tpu-v1-board-in-a-datacenter
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
description: "In May 2016 Google told I/O it had already been running a custom ASIC for a year. The board fit a disk slot."
image: "assets/svg/tpu-v1-datacenter-2016.svg"
image_alt: "Google TPU v1 inference accelerator in the datacenter (2016 public story)."
---

# A board in a Google datacenter

<figure id="fig-tpu-v1-board" itemscope itemtype="https://schema.org/ImageObject">
  <img src="assets/svg/tpu-v1-datacenter-2016.svg"
       alt="Schematic of the 2016 TPU v1 inference accelerator board in a Google datacenter slot."
       width="880" height="360" loading="lazy" decoding="async"
       itemprop="contentUrl" />
  <figcaption itemprop="caption"><strong>Figure 1.</strong> Google's first public TPU story is inference in production — not the training-at-scale chapter yet.</figcaption>
</figure>

Norm Jouppi walked on stage at Google I/O on May 18, 2016, and described a chip Google had already been using. The Tensor Processing Unit, TPU, was a custom ASIC for machine learning, tailored for TensorFlow, running in Google’s datacenters for more than a year. The blog post that day says the board fits in a hard-disk slot. It says first silicon to production applications took twenty-two days. It says an order of magnitude better performance per watt for ML, “roughly equivalent to fast-forwarding technology about seven years.” Those are Google’s sentences. They are marketing and they are also the first public description of a machine that had already been answering queries.

The later paper is the one you should trust for the numbers. “In-Datacenter Performance Analysis of a Tensor Processing Unit,” Jouppi and dozens of co-authors, ISCA 2017, arXiv 1704.04760. The TPU had been deployed since 2015 for inference. The heart of the chip is a 256×256 array of 8-bit multiply-accumulates: 65,536 MACs, 92 tera-ops per second peak, 28 MiB of software-managed on-chip memory. The comparison machines, in the same datacenters, were a Haswell CPU server and an NVIDIA K80. The production workload mix — MLPs, CNNs, LSTMs — was, they said, 95 percent of their datacenter NN inference demand. Average speedup about 15–30×, TOPS per watt about 30–80×. A sentence in the abstract still stings if you love GPUs: the TPU’s deterministic execution matched 99th-percentile latency better than the time-varying tricks CPUs and GPUs use to help average throughput.

Read that last claim slowly. v1 is not a training hero. It is an inference appliance for a company that already knew its models and its tail-latency SLOs. The reduced precision is not a research experiment. It is a transistor budget. The missing features — the ones that make a GPU a good general computer — are, the authors argue, part of why the TPU could be small and relatively low power. Specialization is what you delete.

The disk-slot detail is the magazine image. A datacenter is a geography of bays. If your accelerator takes a disk bay, you can add it without inventing a new chassis. That is an operations sentence. Google’s first TPU story is an operations story that happens to include a systolic array.

There is a temptation to say “this is when Google left NVIDIA.” The paper does not say that. It says that in 2017 Google still used CPUs and GPUs for other ML, and that the TPU was for the inference demand they measured. The later Cloud TPU story, training pods, JAX — those are other articles. v1 is a board, a year of silent production, a May reveal, a June 2017 paper.

If you want a physical object, you want the photograph Google published of the TPU board: a PCB that looks like a thick disk sled, not like a GeForce. That photograph is the anti-8800. No RGB. No dual-slot cooler facing a living room. A sled for a building that already existed.

This piece stays with v1 on purpose. The v1 paper is one of the cleanest public documents we have about why a company would build its own chip: they knew the workload, they knew the SLO, they knew the power bill, and they were willing to delete generality. Everything after is scale. The deletion is the origin.

## Sources

- Norm Jouppi, Google Cloud Blog, “Google supercharges machine learning tasks with TPU custom chip,” May 18, 2016 (I/O announcement; disk-slot board; 22 days; >1 year in production).
- Jouppi et al., “In-Datacenter Performance Analysis of a Tensor Processing Unit,” ISCA 2017 / arXiv:1704.04760 (65,536 8-bit MACs, 92 TOPS, 28 MiB, Haswell and K80 comparisons).
