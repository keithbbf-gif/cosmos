---
title: "DGX-1: eight GPUs and a category"
dek: April 2016: NVIDIA sold a 3U box as a supercomputer. The first one went to OpenAI in a photo.
slug: 29-dgx-1-eight-gpus
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
---

# DGX-1: eight GPUs and a category

On April 5, 2016, at GTC, NVIDIA unveiled the DGX-1. The press release used the phrase “world’s first deep learning supercomputer” and the phrase “supercomputer in a box,” which is the kind of language that makes HPC people wince and buyers reach for a purchase order. The spec that mattered was concrete: eight Tesla P100 GPUs, 16 GB each, NVLink in a hybrid cube-mesh, dual 10GbE plus four 100Gb InfiniBand ports, 7 TB of SSD cache, a 3U chassis, 3200 watts, up to 170 FP16 teraflops. General availability in the U.S. was listed as June.

The category invention is more important than any one number. Before DGX, you could build an eight-GPU server. People did. After DGX, you could buy a SKU that meant “the NVIDIA-shaped way to do that,” with a software image, a support story, and a price that was public enough for journalists to repeat: on the order of $129,000 in contemporary coverage. OEMs would spend the next decade cloning the idea with more or less NVLink fidelity. The clone-and-original market is the success metric.

Huang hand-delivering a DGX-1 to OpenAI in San Francisco is a photo that got more circulation than the datasheet. TOP500’s write-up treated it as news. The symbolism is almost too on the nose — a graphics-company CEO carrying a beige-and-black box into a nonprofit that would later become a different kind of company — but the symbolism is public and therefore fair game. The box was real. The photo was a launch.

What was inside, besides GPUs: two Xeons to boot and babysit, a network story that assumed you might scale out, a software stack NVIDIA promised was tuned. The blog post a year later is a guided tour of a node that wants to be a product, not a parts list. That is the DGX idea. You are not buying eight accelerators. You are buying a weekend you will not spend in the BIOS.

A skeptical reading: 3200 watts in 3U is a facility problem wearing a bow. Sites that could not cool it did not buy it. Sites that could, and that wanted the NVLink mesh, did. The DGX-1 is also a reference platform for P100 at a moment when the GPUs were not yet everywhere. Sometimes you buy the box because it is the only honest way to get the silicon.

The software image is the less photographed invention. NVIDIA shipped a stack of drivers, libraries, and later NGC containers so that “it works on DGX” became a sentence a framework author could say. That sentence is a platform. It is also a gentle lock-in: the blessed image is easier than assembling the same stack on a random 4U. OEMs copied the hardware faster than they copied the blessing. The blessing is why DGX remained a brand after the parts list stopped being unique.

If you want a physical object, a DGX-1 bezel — the face with the name that became a brand — is enough. Later DGX boxes got denser and louder in the marketing sense. The first one is the category. Eight GPUs, one SKU, a photo, a price, a software image. That combination is a product-management event as much as a silicon event.

The DGX line after A100 and H100 is a different story. 2016 is the year NVIDIA decided the node was something they would brand. Everything in the rack-scale story after that is a louder version of the same decision.

## Sources

- NVIDIA, “NVIDIA Launches World's First Deep Learning Supercomputer,” April 5, 2016.
- NVIDIA Technical Blog, “DGX-1: The Fastest Deep Learning System.”
- TOP500.org, “NVIDIA Delivers DGX-1 Supercomputer in a Box to OpenAI.”
- Contemporary press on list price (~$129,000) and June 2016 U.S. availability.
