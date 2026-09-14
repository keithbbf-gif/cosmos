---
title: "Brook for GPUs: a language for a machine that was still a toy"
dek: Stanford wrote C-like streams, compiled them onto OpenGL and DirectX, and published it at SIGGRAPH. The toy grew up elsewhere.
slug: 05-brook-for-gpus
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
description: "Stanford wrote C-like streams, compiled them onto OpenGL and DirectX, and published it at SIGGRAPH. The toy grew up elsewhere."
image: "assets/svg/spine-gpu-public-history.svg"
image_alt: "Timeline schematic of selected public GPU, CUDA, and TPU milestones from 1999 through 2024."
---

# Brook for GPUs: a language for a machine that was still a toy

SIGGRAPH 2004, Los Angeles. The paper is “Brook for GPUs: Stream Computing on Graphics Hardware.” The authors are Ian Buck, Tim Foley, Daniel Horn, Jeremy Sugerman, Kayvon Fatahalian, Mike Houston, and Pat Hanrahan. If you have heard of CUDA and not Brook, that is not because Brook was secret. It is because academic languages often die of success: the idea gets a job in industry and stops using its campus name.

Brook was a C-like stream language. You wrote kernels over streams of data. The compiler and runtime, BrookGPU, mapped that onto the GPUs you could actually buy — NVIDIA and ATI — by speaking OpenGL and DirectX. The hardware still thought it was drawing. The programmer could almost forget that. “Almost” is doing a lot of work. Anyone who compiled Brook in anger still met the graphics driver’s opinions.

The intellectual parent is stream computing, the same family as Imagine and Merrimac at Stanford. Hanrahan’s group had already been arguing that the right way to talk to a data-parallel machine was streams and kernels, not a graphics API with extra steps. Brook was the version that ran on a card in a workstation instead of a research supercomputer. That is why the paper matters as public history. It is a demonstration, in a venue anyone can cite, that the GPU could be treated as a stream processor with a language, not only as a triangle factory with a shader.

Read the author list as a map of a lab, not a startup. Fatahalian and Houston would keep showing up in GPU architecture conversations. Hanrahan already had RenderMan and a reputation that made SIGGRAPH listen. Buck is the one who later took the idea to NVIDIA. The paper does not predict CUDA by name. It does not need to. It states the problem CUDA later sold: people want C, they want the throughput, they do not want to become graphics programmers to get it.

There is a genre of tech history that treats every university project as a stolen invention. Skip that genre. Brook was published. The code was discussed. NVIDIA hired the student. The company then spent years — Buck has said, in public talks, more than two years of internal software — turning a research compiler story into a product compiler, a driver, and a set of libraries. That is not a heist. That is how industrial languages get born when the lab and the vendor share a hallway.

What Brook could not be, in 2004, was a platform. It ran on top of graphics APIs that changed, on drivers that were not written to keep a scientific job resident, on hardware that still lacked the communication and sharing CUDA’s 2006 press release would brag about. A language cannot abolish a memory model. It can only costume it. Brook’s costume was better than hand-written fragment shaders. It was still a costume.

Why write a whole article about a compiler most working engineers have never installed? Because “CUDA appeared in 2006” is true and incomplete. The incomplete part is the public research that made “C on the GPU” a sentence you could say at SIGGRAPH without getting laughed out of the room. Brook is that sentence with an implementation and a citation.

If you go looking for the project today you will find the old Stanford graphics pages, the paper, and a trail of people who went into vendors and schools. That is a successful research outcome even if the binary does not run on a modern card. Languages do not have to ship in 2026 to have changed 2006.

A physical object for this one is not a card. It is a SIGGRAPH proceedings CD, or a printed stack of the 2004 papers, with Brook in the GPU track. The machine it targeted was a toy if you were used to a Cray. The paper treated the toy as if it might grow up. It did. The name on the grown-up was different.

## Sources

- Ian Buck et al., “Brook for GPUs: Stream Computing on Graphics Hardware,” SIGGRAPH 2004.
- Stanford BrookGPU project pages (public academic record).
- Ian Buck, public history-of-CUDA remarks (NVIDIA GTC / recorded talks): thesis ~2004, then NVIDIA, CUDA 1.0 with GeForce 8800.
- Related: Merrimac / stream computing papers, Supercomputing 2003, Stanford.
