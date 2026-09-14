---
title: "Fermi: caches, error correction, and a grown-up GPU"
dek: In 2010 NVIDIA added the things a lab asks for after the demo: L1, L2, ECC, and a straighter C++ story.
slug: 10-fermi-caches-and-ecc
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
---

# Fermi: caches, error correction, and a grown-up GPU

G80 proved a compiler could live on a graphics chip. Fermi, the GF100 generation announced for 2010, tried to prove a lab could live with the result. The public whitepaper and the Tesla C2050/C2070 datasheets read like a list of complaints from the first three CUDA years: irregular memory access, silent bit flips, double precision that was a second-class citizen, a C++ story that felt bolted on.

Start with the caches. Each streaming multiprocessor on GF100 got 64 KB of on-chip memory you could split: 48 KB shared plus 16 KB L1, or the other way around. A 768 KB unified L2 sat in the middle and served loads, stores, and textures. NVIDIA’s own words in the GF100 paper are about algorithms whose addresses you do not know ahead of time — physics, ray tracing, sparse structure. Shared memory had already taught people to stage data on purpose. L1 and L2 said: we will also catch the accidents.

Then ECC. The Tesla 20-series datasheets say error correction covers register files, L1, L2, shared memory, and DRAM. They also say the quiet part: with ECC on, user memory drops by 12.5 percent. A 3 GB C2050 becomes 2.625 GB you can actually use. That trade is the grown-up move. Scientific buyers will give you capacity for a story about not trusting the answer. Gaming buyers will not. Fermi is the generation where NVIDIA is willing to print both sentences in a datasheet.

Double precision is the other lab demand. Tesla marketing for the 20-series talks about a large jump in FP64 versus the 10-series. Whether any one application saw “7X” is a benchmark argument. The architectural intent is not: Fermi wanted to be mentionable in the same breath as a CPU node for codes that cannot live in FP32. Supercomputing sites were already wiring GPUs into TOP500 machines. A GPU that lies on a residual is a liability.

C++ support, listed next to ECC on the same slides, is easy to sneer at. Language support is never only a compiler flag. It is a signal to the people who write the codes that they will not have to rewrite their types into C89 to use the card. Fermi’s C++ was not modern C++. It was a door.

GF100 as a gaming part had a messy launch: delayed, hot, a GeForce GTX 480 that became a joke about space heaters. That consumer story is real and well documented. It is not the center of the Fermi compute story. The compute story is that the same generation produced boards a procurement office could defend. C2050, C2070, then the C2075 with 6 GB and a slightly calmer power story. Those boards are why “CUDA in the cluster” stopped sounding like a graduate student with a GeForce under a desk.

Fermi also changed how people wrote kernels. Caches forgive some alignment sins. They also hide some of them, which made performance work harder in a new way. Occupancy lore, already a cottage industry, met a memory hierarchy that looked more like a CPU and still was not one. The programming guides from that era are full of people rediscovering that a GPU cache is small and shared by an army.

If you want a physical object, a Tesla C2070 is the one: 6 GB, ECC in the datasheet, no romance, a fan that sounds like a server. Hold the GF100 whitepaper next to it. The paper is trying to be a CPU without giving up the throughput. That ambition is Fermi. The later chips will add tensor units and faster wires. They will still ship ECC on the expensive SKU, because Fermi taught NVIDIA which checkbox the lab will not waive.

## Sources

- NVIDIA GF100 whitepaper (Fermi architecture): SM on-chip 64 KB configurable L1/shared; 768 KB L2; cache rationale.
- NVIDIA Tesla C2050/C2070 datasheet (July 2010): ECC coverage; 12.5% memory tax; FP64 marketing; C++.
- Public GeForce GTX 480 launch record (consumer Fermi, 2010).
