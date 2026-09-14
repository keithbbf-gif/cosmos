---
title: "The warp: thirty-two threads that live or die together"
dek: NVIDIA's SIMT bet is a number you can count on your fingers if you have enough hands. The number is thirty-two.
slug: 21-the-warp-thirty-two-threads
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# The warp: thirty-two threads that live or die together

CUDA’s public hierarchy is grids, blocks, and threads. The hardware’s favorite unit is hiding one layer down: the warp. On NVIDIA GPUs, for a long public stretch of generations, a warp is thirty-two threads that share an instruction stream. They march together. If they disagree about where to go — a branch, a divergence — the machine has to take both roads and mask off the loiterers. That fact has been in the programming guides and the architecture whitepapers for as long as people have been writing serious CUDA. It is not a secret. It is a tax that beginners meet as “why is my kernel slow.”

SIMT is the name NVIDIA put on this: single instruction, multiple threads. It is SIMD with a friendlier story and a per-thread register file. The friendliness is real. You write scalar code. The unfriendliness is also real. Thirty-two is not a metaphor. A block of thirty-three threads wastes a slot. A warp that splits on `if (threadIdx.x > 16)` pays for both sides. A warp that gathers from random addresses turns a beautiful memory pipe into a drizzle.

Why thirty-two? Architecture papers and talks give engineering reasons: register file design, instruction issue, the shape of a memory transaction. A magazine article should not pretend to have the die photo. It should say the number became culture. People pad arrays to multiples of thirty-two. People write “warp-synchronous” comments. People learned, then unlearned, then relearned what the compiler and the hardware guarantee about warp-level primitives. `__shfl` and later `cooperative_groups` are public APIs that exist because thirty-two is a social unit as well as a hardware unit.

Other widths exist in the world. AMD’s wavefront was sixty-four on GCN for years, then could be thirty-two on later RDNA parts. That mismatch is why “just port the kernel” is a punchline. The warp is not a law of physics. It is NVIDIA’s law, and they kept it long enough that software crystallized around it.

Divergence is the drama. Neural-net kernels, luckily, are often uniform: every thread does the same math on a different index. That is why the machine and the workload got married. The codes that hurt — parsers, graphs, sparse leftovers — are the codes that make a warp look like a bad idea. CUDA survived because the paying workloads, first HPC dense math and then dense-ish neural nets, were warp-friendly enough.

If you want a physical object, you will not find a warp in a box. You will find it in an Nsight screenshot with 32-wide execution masks, or in a blog post from 2011 that is still correct about the number and wrong about a later primitive. The durability of the number is the story. Chips changed. Thirty-two stayed in the muscle memory.

This piece is not a how-to on avoiding divergence. The public guides already do that. It is a history of a constant. Few constants in computing last twenty years in volume hardware. This one did. Respect it, then ask, when a new vendor arrives, what their constant is — and whether your software can forgive a different one.

## Sources

- NVIDIA CUDA C Programming Guide: warps, SIMT, divergence.
- NVIDIA architecture whitepapers (Fermi onward) describing warp width.
- Public AMD GCN/RDNA wavefront-width documentation (64, later 32) as contrast.
- NVIDIA warp-level primitive docs (`__shfl`, cooperative groups).
