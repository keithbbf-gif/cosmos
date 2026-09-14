---
title: AMD's long compute detour
dek: Close-to-Metal, Stream, OpenCL, ROCm, HIP — the other house kept building on-ramps to a highway NVIDIA already owned.
slug: 32-amd-firestream-rocm-hip
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
portrait: null
figures:
  - ../assets/32-amd-firestream-rocm-hip/historical-timeline.svg
  - ../assets/32-amd-firestream-rocm-hip/architecture-diagram.svg
---
# AMD's long compute detour

AMD’s GPU-compute story is a sequence of doors. Close-to-Metal was an early, low-level ATI door that developers treated like a live wire. The Stream SDK tried to be a product. OpenCL, which AMD publicly championed in 2008, tried to be a standard. ROCm, announced in 2016, tried to be an open Linux compute stack you could put on a cluster without asking NVIDIA’s permission. HIP, the Heterogeneous-compute Interface for Portability, tried to be CUDA with the serial numbers filed off — a C++ dialect close enough that a tool, HIPIFY, could rewrite a lot of the source and leave you to fight the rest.



<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/32-amd-firestream-rocm-hip/historical-timeline.svg" alt="Timeline of public milestones for AMD's long compute detour: dated anchors from press releases, papers, and product records — not live benchmark scores." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Calendar anchors for this piece. Years follow the essay; verify against Sources before publication.</figcaption>
</figure>


None of these doors is a joke. People shipped codes through all of them. The reason the story feels like a detour is the destination. The destination, for most of the 2010s, was “run the thing the NVIDIA people already run.” That is a brutal product requirement. It means your success metric is compatibility with someone else’s wetland, plus performance on your own memory system and wavefront width. HIPIFY’s own documentation is honest about the leftovers: libraries with no twin, kernels tuned for the wrong machine, the last mile that is always manual.

ROCm’s public life has been a Linux-admin story as much as a compiler story. Install it, hit a kernel version, hit a GPU that is not on the support matrix, hit a distribution that is not the blessed one. The GitHub issues are the archive. The archive got better over time. The early years cost AMD labs that would have been allies. Platform work is timing. NVIDIA had already burned those years on CUDA 2, 3, 4, 5.

Then the machines that do not care about your feelings showed up. Frontier at Oak Ridge and El Capitan at Lawrence Livermore took AMD Instinct GPUs to the top of the public TOP500. Those are not asterisks. They are national machines running production-class codes on AMD’s compute architecture (CDNA, in AMD’s naming). HPC was always the other house’s better shot: the buyers write their own software, the contracts are huge, the CUDA habit is strong but not always mandatory. Training-the-latest-LLM-in-PyTorch is a different buyer. AMD is still in that fight in public, with ROCm builds of the popular frameworks and a lot of partner slides.

GCN, then CDNA versus RDNA, is AMD splitting the product the way NVIDIA split Tesla and GeForce. Gaming wants one kind of cache and one kind of raster story. Compute wants matrix cores and HBM and a firmware that will not reset because a desktop compositor coughed. The split is late compared with NVIDIA’s 2007 Tesla, but it is the correct split. You cannot optimize one die for a 4K game and a 200-GPU all-reduce and tell the truth to both customers.

If you want a physical object, an Instinct MI250X or MI300 board is the late-period object; a FireStream card is the early one. Hold the two in your head even if you cannot hold them in your hands. The distance between them is the detour: twenty years of trying to get the software to forgive the hardware.

This article is not a prediction about who wins 2027. It is a record of a company that never left the aisle, never owned the default language, and still put accelerators into the fastest public supercomputers on earth. That combination is allowed. History is not a single-elimination bracket.







<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/32-amd-firestream-rocm-hip/architecture-diagram.svg" alt="Architecture diagram for AMD's long compute detour: illustrative GPU or datacenter shape from the public record, not an official vendor block diagram." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Illustrative system shape for the argument — protocol and architecture, not scraped silicon photography unless noted.</figcaption>
</figure>
## Sources

- Khronos OpenCL 1.0 release (2008) and AMD’s public Stream-SDK commitment.
- AMD ROCm public launch (2016) and current ROCm documentation.
- HIP and HIPIFY documentation (CUDA-to-HIP translation limits).
- TOP500 records: Frontier and El Capitan (AMD Instinct).
- AMD CDNA / RDNA public architecture naming.
