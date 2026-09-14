---
title: "NVLink and NVSwitch: the midplane"
dek: PCI Express was a driveway. NVIDIA built a highway, then a cloverleaf, then a backplane.
slug: 28-nvlink-nvswitch-midplane
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
description: "PCI Express was a driveway. NVIDIA built a highway, then a cloverleaf, then a backplane."
image: "assets/svg/spine-gpu-public-history.svg"
image_alt: "Timeline schematic of selected public GPU, CUDA, and TPU milestones from 1999 through 2024."
---

# NVLink and NVSwitch: the midplane

PCI Express is a miracle of compatibility and a bottleneck if you pretend eight GPUs are one machine. NVIDIA’s NVLink, first shipped with Pascal in 2016, is a proprietary high-speed link between GPUs (and later, in some systems, between CPU and GPU). NVSwitch, arriving with the V100 generation’s DGX-2 era and then becoming a regular in HGX designs, is the chip that turns those links into a fabric. Together they are why a “GPU node” in a modern rack has a midplane, not just a PCIe riser.

The first public topology a lot of people learned was the DGX-1 hybrid cube-mesh: not fully connected, but much friendlier than eight cards shouting through a CPU root complex. Then DGX-2 used NVSwitch to make a flatter world: more pairs at full-ish bandwidth. Later HGX boards made the switch a default photograph. You can see the NVSwitch chips on the baseboard like little cities. The GPUs are the suburbs.

Generations of the link are public even when the protocol guts are not. Pascal’s first NVLink, Volta’s faster second generation, Ampere and Hopper’s later rates — the whitepapers print GB/s per link and links per GPU. Software people should treat those numbers like memory bandwidth, not like lore. If NCCL is slow, the first question is still “what does `nvidia-smi topo` say,” and the second is “are we actually on the link we paid for.” A surprising number of clusters have answered the second question with “no, that job fell back to PCIe.” The midplane only works if the job stays on it.

Why proprietary? Because NVIDIA wanted a speed and a protocol it did not have to wait on the PCI-SIG for, and because a proprietary link is also a reason to buy the rest of the system. That second sentence is not a conspiracy. It is how platform businesses work. AMD has Infinity Fabric. Intel has various EMIB and Xe Link stories. Google’s TPU pods have their own torus-ish stories. Everyone who wants a domain larger than a socket invents a wire and a religion.

For software people, NVLink shows up as a number in `nvidia-smi topo` and as a hope in an NCCL log. For mechanical people it shows up as a baseboard you should not flex and a cable you should not invent. For historians it shows up as the moment the add-in card stopped being the whole product. An SXM module without the board that knows its NVLink assignment is a brick with expensive memory.

I have heard NVLink described as “the thing that makes eight GPUs feel like one.” That is a half-truth. Eight GPUs never feel like one. They feel like eight GPUs with a better bus. The better bus is a lot. It is not fusion. People who write “the GPU” when they mean “the node” are doing NVLink’s marketing for free.

If you want a physical object, an HGX baseboard with NVSwitch chips and empty SXM sockets is the honest one. It looks like a motherboard that ate a supercomputer. That is the midplane. Pascal invented the highway. The switch invented the interchange. Blackwell-class racks extend the interchange until the rack is the chip. The interchange is a complete story on its own: the driveway was not enough, and NVIDIA built something you could only buy from NVIDIA.

PCIe did not die. Host traffic, NICs, and a million ordinary servers still live there. NVLink is for the family inside the node. Keeping those two buses in your head is the difference between a cluster diagram and a wish.

## Sources

- NVIDIA Pascal NVLink public architecture notes; DGX-1 hybrid cube-mesh (2016).
- NVIDIA DGX-2 / NVSwitch public materials (V100 era).
- NVIDIA HGX baseboard photographs and topology docs (A100 / H100 generations).
- `nvidia-smi topo` documentation as the operator-facing view.
