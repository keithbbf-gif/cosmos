---
title: CUDA Graphs and the tax of launching a kernel
dek: The GPU got faster. The act of telling it to start did not. Graphs are a receipt for that problem.
slug: 25-cuda-graphs-launch-tax
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
portrait: null
figures:
  - ../assets/25-cuda-graphs-launch-tax/historical-timeline.svg
  - ../assets/25-cuda-graphs-launch-tax/architecture-diagram.svg
---
# CUDA Graphs and the tax of launching a kernel

A CUDA kernel launch is a small miracle that started to cost too much. You build a parameter buffer, you talk to the driver, you wake a work distributor, you do this thousands of times per second if your model is a soup of small ops. As the GPU got wider, a short kernel became a rounding error of compute and a real error of control. NVIDIA’s public answer, in the CUDA 10 era (2018), was CUDA Graphs: record a graph of launches and memory ops, then replay the graph with less per-kernel bureaucracy.



<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/25-cuda-graphs-launch-tax/historical-timeline.svg" alt="Timeline of public milestones for CUDA Graphs and the tax of launching a kernel: dated anchors from press releases, papers, and product records — not live benchmark scores." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Calendar anchors for this piece. Years follow the essay; verify against Sources before publication.</figcaption>
</figure>


The documentation is frank about the problem. Launch overhead is a thing. If your workload is one fat GEMM, you do not care. If your workload is a deep-learning step that used to be a Python loop of little kernels, you care. Frameworks cared first. They had already been fusing ops and writing custom engines. Graphs gave them a driver-level way to say “this whole step is one object.”

Capture is the uncanny part. You run the work once in capture mode, the runtime records what you launched, and then you have a graph. The restrictions — what you may not do while capturing — are the interesting historical document. They tell you what the driver can see. They also tell you why a feature like this ships years after people start complaining: the driver has to become a compiler of a launch tape.

I have watched people treat graphs as magic and then trip over a memcpy they did not mean to capture. I have also watched an inference server drop its CPU usage because the launch loop moved. Both are the feature. Graphs do not make math faster. They make telling the GPU to do the math less embarrassing.

There is a longer arc here that includes CUDA streams, events, and the entire “keep the GPU busy from a single CPU thread” genre. Graphs are a late chapter of that genre, not a new Bible. Streams said: overlap. Events said: depend. Graphs said: stop re-explaining the dependence every millisecond. The three ideas stack. A history that starts at graphs will confuse a reader who has never met a stream. This article assumes you have met a stream, or can survive without a tutorial.

If you want a physical object, you want a profiler timeline from 2017 with a sawtooth of tiny kernels and a lot of white space, then a timeline from 2020 with a fatter, calmer block. The white space was the tax. The calmer block is the receipt.

Hopper and Blackwell generations make the tax more important, not less, because the device is hungrier and the models are a mix of huge matmuls and annoying little glue. The glue is where launch overhead lives. Graphs, fusion, and compiler traces are all attempts to starve the glue. CUDA Graphs is the one with NVIDIA’s name on the API.

This is not a how-to. The programming guide will outlive any recipe I could type. It is a marker: by 2018, NVIDIA admitted in an API that the CPU telling the GPU what to do had become a first-class performance problem. Admitting that is a historical event. The GPU was no longer only a throughput machine. It was a machine whose doorbell needed redesigning.







<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/25-cuda-graphs-launch-tax/architecture-diagram.svg" alt="Architecture diagram for CUDA Graphs and the tax of launching a kernel: illustrative GPU or datacenter shape from the public record, not an official vendor block diagram." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Illustrative system shape for the argument — protocol and architecture, not scraped silicon photography unless noted.</figcaption>
</figure>
## Sources

- NVIDIA CUDA 10 release materials and Programming Guide: CUDA Graphs, capture, replay.
- NVIDIA developer blogs on graph launch overhead and inference use.
- Prior public APIs in the same arc: CUDA streams and events.
