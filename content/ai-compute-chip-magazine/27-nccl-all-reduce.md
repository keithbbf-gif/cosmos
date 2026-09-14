---
title: "NCCL: all-reduce as industrial plumbing"
dek: Data-parallel training is a reduction in a trench coat. NVIDIA's library made the trench coat a dependency.
slug: 27-nccl-all-reduce
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
portrait: null
figures:
  - ../assets/27-nccl-all-reduce/historical-timeline.svg
  - ../assets/27-nccl-all-reduce/architecture-diagram.svg
---
# NCCL: all-reduce as industrial plumbing

If you train a model on more than one GPU and you are doing the ordinary thing — each GPU sees a different batch, then they average the gradients — you are performing an all-reduce. The math is old. MPI had it. Supercomputers lived on it. What NVIDIA’s NCCL, the NVIDIA Collective Communications Library, did was make that collective fast on a tangle of NVLink, NVSwitch, PCIe, and Ethernet or InfiniBand, and then become the thing every framework calls.



<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/27-nccl-all-reduce/historical-timeline.svg" alt="Timeline of public milestones for NCCL: all-reduce as industrial plumbing: dated anchors from press releases, papers, and product records — not live benchmark scores." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Calendar anchors for this piece. Years follow the essay; verify against Sources before publication.</figcaption>
</figure>


NCCL’s public documentation is a catalog of collectives: all-reduce, all-gather, reduce-scatter, broadcast, send/recv. The interesting pages are the ones about topology. The library wants to know how your GPUs are wired. It will sniff NVLink meshes, it will notice a switch, it will pick a ring or a tree. People who have watched `NCCL_DEBUG=INFO` scroll past at two in the morning have seen a personality: a library that believes the machine room is its business.

The library’s public life starts in the mid-2010s, when multi-GPU training stopped being a research demo and became a default. Horovod, open-sourced by Uber in 2017, made a thin MPI-ish wrapper over NCCL famous in the TensorFlow world. PyTorch Distributed later made `backend="nccl"` the path people copied out of the tutorial. Those front ends matter because they hid the collective. The hiding is why a lot of competent engineers can train on eight GPUs and still not be able to draw a ring. NCCL did the drawing.

Why a standalone article? Because after a certain date, “multi-GPU training” is not a CUDA kernel story. It is an NCCL story with kernels on either side. Horovod, PyTorch Distributed, TensorFlow’s various strategies — the front ends changed, the collective library often did not. NCCL is infrastructure in the same sense as cuDNN. You do not demo it. You wait on it.

The failure modes are public and social. A hanging all-reduce is how a lot of people first learn they have a bad cable, a bad NIC, a rank that died, or a mismatch in the process group. The hang is not NCCL being mysterious. It is a collective being a collective: nobody goes home until everybody arrives. In a bedroom with two GTX 580s you could see both cards. In a 256-GPU job you see a timeout.

There is a politics of collectives that this piece will only point at. Other stacks exist: MPI, Gloo, RCCL (AMD’s cousin), various research all-reduces that win a paper and lose a release cycle. NCCL won the NVIDIA-shaped world because the vendor wrote it to the vendor’s wires. That is an advantage and a tell. Portability people dislike tells. Cluster people like microseconds.

If you want a physical object, a printout of a ring all-reduce diagram from an NCCL talk is enough: GPUs in a loop, chunks chasing each other, bandwidth math in the corner. That diagram is how the 2016–2024 training boom actually moved bytes. The models got the magazine covers. The ring got the bytes.

A second object is a stack of Ethernet or InfiniBand cables behind a GPU node. NCCL is not only an NVLink library. It is also the thing that has to stay fast when the job leaves the node. The later work on GPU-direct, NIC offload, and in-network reductions is public vendor material because the ring outgrew the midplane. When the collective leaves the box, the chip story becomes a network story. That is still this article. The heartbeat did not stay home.

NCCL will keep growing new protocols for new NVLink generations and new NIC offloads. This article does not freeze a version. It freezes the role. Once gradient averaging became the heartbeat of the industry, the library that implements the heartbeat became part of the chip story — even though it is software — because the chip’s wires only matter if something knows how to use them.







<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/27-nccl-all-reduce/architecture-diagram.svg" alt="Architecture diagram for NCCL: all-reduce as industrial plumbing: illustrative GPU or datacenter shape from the public record, not an official vendor block diagram." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Illustrative system shape for the argument — protocol and architecture, not scraped silicon photography unless noted.</figcaption>
</figure>
## Sources

- NVIDIA NCCL documentation and GitHub public repository (collectives, topology).
- PyTorch Distributed / Horovod public docs showing NCCL as a backend.
- AMD RCCL as a public counterpart on ROCm.
- Classic HPC: MPI all-reduce as the older collective this work inherits.
