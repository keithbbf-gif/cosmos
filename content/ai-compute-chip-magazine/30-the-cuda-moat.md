---
title: "The CUDA moat: lock-in, libraries, and habit"
dek: The moat is not a kernel language. It is a twenty-year pile of things people do not want to rewrite.
slug: 30-the-cuda-moat
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# The CUDA moat: lock-in, libraries, and habit

People say “CUDA moat” as if it were a single alligator. It is a wetland. The C++ dialect is one patch. The compiler is another. cuDNN, cuBLAS, cuFFT, NCCL, TensorRT, the profilers, the containers, the cloud images, the Stack Overflow answers, the course notes, the hiring filters that say “CUDA experience” — those are the water. You can port a kernel. You cannot port a wetland in a quarter.

This is not a secret NVIDIA leaked. It is the ordinary economics of a successful platform, visible from outside. Intel had it with x86. Microsoft had it with Windows. The interesting CUDA-specific fact is that the wetland grew during years when the hardware was also a gaming card, so the developer base could recruit from a consumer market. Students had GeForce. Labs had Tesla. The same nouns worked. That double market is the part competitors keep having to reconstruct.

HIP exists because the wetland is real. OpenCL existed earlier because the wetland was already forming. Triton, JAX, and various graph compilers exist because people want to write less of the dialect and still hit the libraries. Every one of those projects is a public admission that the hot path is NVIDIA-shaped even when the front end is not. Sometimes the admission is a compatibility layer. Sometimes it is a compiler that emits NVIDIA binaries first and everyone else later.

A fair piece should resist two lazinesses. The first is that CUDA is lock-in and therefore illegitimate. Platforms that work produce lock-in. The second is that CUDA is lock-in and therefore eternal. Wetlands dry when the money moves. If a buyer with enough GPUs demands another stack, the hiring filters change. We have watched AMD take pieces of HPC. We have watched Google keep a TPU world that never spoke CUDA. We have watched people write PyTorch and not think about any of this until the bill arrived. The moat is wide. It is not the ocean.

Habit is the deepest water. A senior engineer who has twenty years of intuition about warps and occupancies and NCCL hangs is a capital asset. You do not throw that asset at a new wavefront width for fun. Managers who have been burned by one port do not volunteer for a second. The moat is in their calendars.

Containers made the water deeper. NVIDIA’s NGC images, the cloud “CUDA 12.x + driver Y” pairings, the unspoken rule that you do not upgrade a working training box on a Friday — those are operational lock-in. They are also how a lot of good science got done. A moat can be a harbor. The harbor still has a landlord.

If you want a physical object, a shelf of CUDA programming guides from 2.0 to 12.x is a nice one: same cartoon of grids and blocks, thicker library chapters every year. The thickness is the moat. The early slim book is a language. The late fat book is an economy.

This article names no unfiled inventions and no private stacks. It names a public business fact: NVIDIA’s compute advantage, as of the mid-2020s, is still easier to describe as software gravity than as a single transistor trick. The transistors matter. The gravity is why a faster transistor from someone else does not immediately get a training job.

## Sources

- Public NVIDIA library catalog: CUDA Toolkit, cuDNN, cuBLAS, NCCL, TensorRT.
- AMD HIP / HIPIFY documentation (explicit CUDA-to-HIP path).
- Khronos OpenCL 1.0 as an earlier alternative bet (December 2008).
- Framework compiler stacks (Triton, XLA) as public attempts to sit above the dialect.
