---
title: "Shared memory: the scratchpad that taught a generation"
dek: CUDA's block-local RAM is a small idea that became a rite of passage. Tiling is the rite.
slug: 23-shared-memory-scratchpad
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
description: "CUDA's block-local RAM is a small idea that became a rite of passage. Tiling is the rite."
image: "assets/svg/spine-gpu-public-history.svg"
image_alt: "Timeline schematic of selected public GPU, CUDA, and TPU milestones from 1999 through 2024."
---

# Shared memory: the scratchpad that taught a generation

Every CUDA course eventually draws a square. The square is a tile of a matrix. Threads cooperate to pull the tile from slow memory into a fast scratchpad, `__shared__`, then reuse it. The scratchpad is scoped to the block. A barrier keeps the neighbors honest. That exercise, usually a matrix multiply, has trained more GPU programmers than any whitepaper. It is also a picture of what G80-era hardware wanted you to do: if you care about bandwidth, do not ask the DRAM twice.

Shared memory is not a cache you do not understand. It is a cache you address. That distinction is why the first CUDA generations could beat a CPU on problems that look like textbooks. You, the programmer, became the prefetcher. Fermi later added a real L1 you could steal space from, configurable against the scratchpad. The scratchpad did not go away. It remained the thing you used when you knew the reuse pattern and did not want to hope.

Bank conflicts are the accompanying folklore. Shared memory is organized in banks. If thirty-two threads touch thirty-two different banks, life is good. If they all hit the same bank, the hardware serializes and your tile turns into a queue. The guides have diagrams. The workshops have jokes. The jokes are accurate enough.

Why a whole article? Because shared memory is the last widely taught CUDA idea that still feels like programming a machine instead of calling a library. After cuDNN, after Tensor Cores, after a framework fused your op, most people never write a tile. The people who do — kernel engineers, library writers, the person who owns the one op that is always on the trace — still live here. A culture that forgets the scratchpad cannot read a profiler. A culture that only worships the scratchpad cannot ship a framework.

Other architectures have the same idea under other names. OpenCL’s local memory. HIP’s shared memory, on purpose. Some research machines called it a software-managed cache and wrote dissertations. NVIDIA’s contribution was to put the scratchpad in the beginner model, not only in the expert model. `__shared__` is a keyword a student meets in week one.

There is a nostalgia trap. Tiling a GEMM by hand is no longer how you beat cuBLAS. The hardware grew tensor units that want their own fragment APIs. The scratchpad is still there, sometimes feeding those units, sometimes holding a softmax tile, sometimes sitting idle while a library you did not write does the clever thing. History should honor the teaching object without pretending it is still the hot path for everything.

If you want a physical object, print a 16×16 tile of numbers and a picture of 256 threads. Tape it above a desk. That poster is 2008–2014 GPU computing. A lot of good work happened under that poster. A lot of time was also wasted making a slower GEMM than the one NVIDIA already shipped. Both facts can be true.

The scratchpad taught a generation that memory, not arithmetic, was the boss. That lesson outlived the keyword. You can see it in every later argument about HBM, about cache line sizes, about why a transformer is an I/O problem. Shared memory was the first place CUDA people met the boss on purpose.

## Sources

- NVIDIA CUDA C Programming Guide: shared memory, `__syncthreads`, bank conflicts.
- NVIDIA Fermi / GF100 whitepaper: 64 KB configurable shared / L1.
- Classic teaching examples: tiled matrix multiplication in NVIDIA workshops and the CUDA samples.
