---
title: "OpenCL: the standard that arrived on time and still lost"
dek: Khronos ratified a portable GPU compute API in December 2008. CUDA kept the jobs.
slug: 31-opencl-the-standard-that-lost
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# OpenCL: the standard that arrived on time and still lost

On December 9, 2008, at SIGGRAPH Asia in Singapore, the Khronos Group announced that OpenCL 1.0 was ratified and public. The press release is a roll call: Apple had proposed a draft six months earlier; AMD, NVIDIA, Intel, IBM, ARM, and a long list of others had sat on the working group. Neil Trevett bragged, in contemporary coverage, that they had done in six months what some standards bodies take five years to do. Apple wanted it for Snow Leopard. AMD said it would evolve the ATI Stream SDK to comply. The industry, on paper, had a portable, royalty-free way to write data-parallel C for CPUs, GPUs, and other odd processors.

CUDA was two years old as a named product and already a habit in the labs that had adopted it. OpenCL was cleaner as a committee artifact and clumsier as a thing you taught on a Tuesday. The host API was verbose. The kernel language was C with restrictions. The portability was real at the level of “it compiles” and fictional at the level of “it is fast.” Performance portability is the polite phrase. The impolite phrase is that every vendor’s OpenCL was a different machine with a common spelling.

NVIDIA shipped OpenCL because they were in the room. They did not put their best library energy there. That is not a leaked memo. It is visible in the relative thickness of the two developer stories. AMD put more of its public compute identity on OpenCL for years, then had to build ROCm and HIP anyway because the codes people wanted to run were CUDA codes. Intel used OpenCL in various accelerator stories. Apple, having started the thing, later deprecated OpenCL on its platforms and pointed people at Metal. A standard can lose its own parent.

Why did the portable API lose the job market? Timing is not the answer; it arrived early. Completeness is closer. CUDA was a compiler plus a driver plus libraries plus a story about C++ plus, eventually, cuDNN. OpenCL was a specification plus vendor implementations plus, later, a heterogeneous zoo that included FPGAs. The zoo is admirable. The training job in 2016 wanted a conv primitive and an all-reduce. Those lived on the NVIDIA side of the aisle.

I am not writing an obituary. OpenCL still exists. It still makes sense in some embedded and cross-vendor cases. SYCL and other Khronos-adjacent efforts are later chapters of the same hope: write once, run on whatever accelerator the buyer has. The hope is decent. The historical record of 2008–2016 is that hope did not beat a vertically integrated stack with better libraries and a consumer card in the student’s PC.

If you want a physical object, the Khronos OpenCL 1.0 specification PDF is enough. Print the participant list on page whatever and read it as a picture of an industry that thought it could standardize its way out of a platform war. The war continued. The specification is still there, public, royalty-free, and not what your PyTorch install talks to by default.

A standalone article should not turn this into a morality play about open versus closed. OpenCL was open and late in the only way that mattered: late to the wetland. CUDA was closed and early to the wetland. The wetland won. That sentence is enough.

## Sources

- Khronos Group, “The Khronos Group Releases OpenCL 1.0 Specification,” December 9, 2008.
- Contemporary AMD statement in the Khronos release (ATI Stream SDK to comply).
- Apple WWDC / Snow Leopard public OpenCL positioning (2008–2009).
- Later public note: Apple deprecation of OpenCL in favor of Metal; AMD’s move toward ROCm/HIP.
