---
title: "Systolic arrays: an old idea Google shipped"
dek: Kung and Leiserson described a pulse of data through a grid in 1979. The TPU is that pulse with a TensorFlow badge.
slug: 35-systolic-arrays-kung-to-jouppi
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
---

# Systolic arrays: an old idea Google shipped

H. T. Kung and Charles Leiserson’s systolic-array papers from the late 1970s describe a way to push data through a regular grid of simple cells so that a lot of arithmetic happens without a lot of instruction traffic. The metaphor is a heartbeat. Each cell does a little, passes the blood along, and the array as a whole finishes a matrix problem. Architects loved it. Then, for a long time, they loved other things more: caches, out-of-order CPUs, the flexibility of a GPU’s SIMT story. The idea stayed in textbooks and in occasional DSP and crypto chips.

The TPU v1 paper is explicit about the inheritance. The matrix multiply unit is a 256×256 systolic array of 8-bit MACs. Weights can be held. Activations stream. The on-chip memory is software-managed, not a heroic cache hierarchy. Determinism is a feature. The authors cite earlier systolic matrix multipliers, including 1990s machines, because they are doing their related-work job. A careful reader should hear that citation as a bell. Google did not invent the grid. Google shipped the grid at datacenter volume for a workload that looks like the textbook example: dense matrix multiplies, over and over, with forgiving precision.

Why did the idea wait? Because a systolic array is rude to the codes that are not the array’s shape. Branchy codes, sparse codes, “I will decide the address in a minute” codes — those want a GPU or a CPU. In 2015 Google could look at its inference mix and say: the rude machine matches the bill. That is a privilege of knowing your workload. NVIDIA, selling to everyone, could not be that rude on a GeForce. Even NVIDIA’s Tensor Cores are a more localized systolic-ish unit inside a still-programmable SM, not a whole chip that is the array.

There is a beauty to the old papers that the TPU blog posts cannot copy. Kung and Leiserson were working in a world where communication was already the enemy and they drew pictures of data waves. Modern ML compilers rediscovered the pictures and called them tiling and pipelining. XLA’s job, on a TPU, is partly to feed the array without stalling the heartbeat. The compiler is new. The heartbeat is not.

I do not want to over-claim a straight line from 1979 to 2015. Lots of lines exist: vector machines, DSP MACs, GPU Tensor Cores, Cerebras’s wafer-scale grid, Groq’s deterministic streaming story. The TPU is the line that came with an ISCA paper, a production deployment, and a cloud product. That is enough to earn a standalone piece. The piece is not “Google invented systolic arrays.” The piece is “an old, slightly unfashionable idea became the hottest inference chip of 2016 because the workload finally looked like the idea.”

If you want a physical object, print figure-and-caption from Kung/Leiserson and set it next to the TPU v1 block diagram from the ISCA paper. The rhymes are visual. Students who only know Tensor Cores should have to look at both. Specialization is a cycle. We forget, we build general machines, we get tired of their extra energy, we draw a grid again.

The story here stays with the idea, not with later TPU generations. The later generations add more memory, more chips, more networking, more training. They still feed arrays. The array is the constant. The constant is older than the company that shipped it.

## Sources

- H. T. Kung and C. E. Leiserson, systolic-array papers (late 1970s; see also later textbook treatments).
- Jouppi et al., ISCA 2017 TPU paper: 256×256 MXU, software-managed memory, citations to 1990s systolic multipliers.
- Contrast: NVIDIA Tensor Cores as localized matrix units inside a programmable SM (Volta onward, public whitepapers).
