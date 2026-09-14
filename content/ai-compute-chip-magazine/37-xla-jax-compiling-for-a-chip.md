---
title: "XLA and JAX: compiling for a chip you cannot buy"
dek: Google's TPU stack is a compiler culture. The chip is what the compiler feeds.
slug: 37-xla-jax-compiling-for-a-chip
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
portrait: null
figures:
  - ../assets/37-xla-jax-compiling-for-a-chip/historical-timeline.svg
  - ../assets/37-xla-jax-compiling-for-a-chip/architecture-diagram.svg
---
# XLA and JAX: compiling for a chip you cannot buy

CUDA’s beginner story is a kernel you typed. The TPU’s beginner story is a compiler you angered. XLA, Accelerated Linear Algebra, started as TensorFlow’s compiler stack for targeting CPUs, GPUs, and TPUs from the same graph. JAX, born at Google as a research-friendly combination of Autograd and XLA, made “write NumPy, get a compiled program” a personality. The personality won a generation of researchers who wanted to transform functions, jit them, and not think about a warp.



<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/37-xla-jax-compiling-for-a-chip/historical-timeline.svg" alt="Timeline of public milestones for XLA and JAX: compiling for a chip you cannot buy: dated anchors from press releases, papers, and product records — not live benchmark scores." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Calendar anchors for this piece. Years follow the essay; verify against Sources before publication.</figcaption>
</figure>


This is a chip-history article because the TPU almost requires that personality. A systolic array with a software-managed memory and a pod interconnect is not a friendly place to write a handwritten kernel in the CUDA sense. Some people do write low-level TPU code. Most people write a JAX function and let XLA tile, fuse, and layout. The chip’s public face is the compiler error about a shape you cannot shard.

JAX’s public documentation and the papers around Autograd, XLA, and later Pathways-class systems are the trail. The trail is open enough to use and Google enough to remind you that the best target is a machine in their building. JAX runs on GPUs too. That is important. It is how a lot of people learned the style without a TPU quota. The style — functional, jit, pmap then pjit then shard_map, explicit sharding annotations — leaked into how people think about multi-chip training even when the backend is NCCL.

I like JAX and I have also watched a student lose a week to a recompilation. The compiler culture has costs. First-run latency. Hermetic-but-not-quite caches. Error messages that point at HLO you did not know you had written. The costs are the price of not launching a thousand tiny kernels by hand. CUDA Graphs is NVIDIA admitting a version of the same problem from the other side. XLA admitted it from birth.

Why “a chip you cannot buy”? Because the TPU, for most of its life, has not been a Newegg SKU. The compiler is the access path. That changes the politics of learning. A poor student can still learn CUDA on a used GeForce. Learning TPU well has usually meant a Cloud credit, a university program, or a job. The software is public. The machine is a gate. That gate is part of the chip’s history.

If you want a physical object, a printout of an HLO dump next to a JAX function of ten lines is the right joke. The ten lines are what the human wrote. The dump is the program. TPU history without that joke is just a list of MXU sizes.

This article will not teach `jax.jit`. It will say that Google’s accelerator story is incomplete if you only describe the array. The array is hungry. XLA is the kitchen. JAX is the restaurant that made the kitchen fashionable. The fashionable restaurant also serves GPUs. That is how compiler cultures spread: they stop being about one chip and start being about a way to talk to chips.







<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/37-xla-jax-compiling-for-a-chip/architecture-diagram.svg" alt="Architecture diagram for XLA and JAX: compiling for a chip you cannot buy: illustrative GPU or datacenter shape from the public record, not an official vendor block diagram." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Illustrative system shape for the argument — protocol and architecture, not scraped silicon photography unless noted.</figcaption>
</figure>
## Sources

- TensorFlow XLA public documentation.
- JAX documentation and the Autograd / Compiling ML programs literature from Google (public).
- Google Cloud TPU docs on XLA as the programming path.
- Contrast: CUDA Graphs (2018) as NVIDIA’s later attack on launch glue.
