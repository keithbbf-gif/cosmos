---
title: Intel's third chair
dek: Larrabee, Xe, Ponte Vecchio, Gaudi — the CPU company kept pulling up a seat at a table it used to own.
slug: 33-intel-third-chair
series: AI Compute Chip Magazine
status: staged
voice_check: edited
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Intel's third chair

Intel’s relationship to the GPU is a long story about a company that owned the default computer and then watched the default computer’s hot work move to someone else’s die. The public chapters have different names. Larrabee was a many-core x86 graphics bet that became a cautionary talk. Intel Xe is a branding of GPU efforts that includes integrated graphics and datacenter parts. Ponte Vecchio, the Xe HPC GPU in the Aurora supercomputer at Argonne, is a mosaic of tiles and EMIB and a statement that Intel still belongs in TOP500 photographs. Habana’s Gaudi line, which Intel bought, is an AI training NIC-and-accelerator story that does not look like a GeForce and does not want to.

The third chair is a structural fact, not an insult. NVIDIA has the wetland. AMD has the other house and, at times, the fastest public machine. Intel has the CPU, the server account, the compiler people, and a need not to watch the acceleration budget walk out of the socket. Every few years they put a product in the chair and the internet decides whether to laugh. Sometimes the laugh is fair (the launch is late, the software is thin). Sometimes the laugh is just the wetland talking.

Aurora is the fairest public object for the HPC side. A U.S. exascale machine with Intel CPUs and Intel GPUs is a national vote. The vote does not make oneAPI a default in a startup. It does make “Intel cannot do GPUs” a lazy sentence. Ponte Vecchio’s tile count and HBM are documented in Intel’s architecture days. The software story around SYCL and oneAPI is documented too: a bet that you can write a modern C++ parallel dialect and not fall into CUDA. Some codes did. The training default, again, lived elsewhere.

Gaudi is a different chair at the same table. Habana, before and after the acquisition, sold a training accelerator with a strong Ethernet scale-out story. Intel’s public Gaudi materials talk about avoiding a proprietary fabric tax. That pitch only makes sense in a world where the proprietary fabric tax is real and named NVLink. The existence of the pitch is the history. Whether a given cloud’s Gaudi cluster is a bargain is a procurement fight, not a magazine verdict.

Integrated graphics is the quiet Intel GPU that actually shipped by the hundreds of millions. It is not a TPU. It is not an H100. It is why a lot of the world has a GPU that is not a GPU in the sense this magazine usually means. An honest industry history mentions that, then returns to the datacenter, because that is where the money and the heat moved.

If you want a physical object, a Ponte Vecchio OAM or a Gaudi board is the datacenter object; a random laptop with “Intel Iris” is the volume object. The gap between those objects is Intel’s problem in one photograph.

This piece stays public and stays kind enough to be accurate. Intel did not “fail at AI chips” in a single cinematic year. Intel has been sitting down, standing up, and sitting down again while the table was being rebuilt around a different default processor. The third chair is still there. People still sit in it. The check, most nights, still goes to the first chair.

## Sources

- Public Larrabee history (Intel many-core graphics bet; cancellation / retargeting as documented in contemporary press).
- Intel Xe / Ponte Vecchio architecture days; Aurora (Argonne) public system descriptions.
- Intel acquisition of Habana Labs (2019) and Gaudi product materials.
- oneAPI / SYCL public documentation.
