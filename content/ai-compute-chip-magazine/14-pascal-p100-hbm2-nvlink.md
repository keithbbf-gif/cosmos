---
title: "Pascal P100: stacked memory and a new wire"
dek: In 2016 the Tesla GPU stopped looking like a thick GeForce. HBM2 and NVLink are why.
slug: 14-pascal-p100-hbm2-nvlink
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Pascal P100: stacked memory and a new wire

The Tesla P100, Pascal generation, 2016, is the first NVIDIA compute GPU a lot of people remember as a different species from a gaming card. Not because it refused a monitor — Tesla had been doing that since 2007 — but because the package changed. High Bandwidth Memory sat on the same interposer as the GPU. NVLink, a proprietary high-speed interconnect, sat next to PCI Express and made “how the cards talk to each other” a first-class spec. The DGX-1 announcement in April 2016 is eight of those cards in one box. The P100 is the reason the box is not just a thicker PC.

HBM2 is the quieter revolution. For a decade the GPU’s appetite had been growing faster than GDDR could politely feed it. Stacking DRAM and putting it closer to the die is how you buy bandwidth without another fifty watts of I/O theater. AMD had already shipped HBM on a consumer Fiji GPU in 2015. NVIDIA’s P100 brought stacked memory into the Tesla line at the moment deep learning was turning from papers into purchase orders. The 16 GB figure in the first DGX-1 spec is a memory figure, not a core figure. That is the tell.

NVLink is the louder revolution because you can draw it. Pascal’s NVLink let GPUs exchange data without pretending PCI Express was going to be enough. In the DGX-1 the topology is a hybrid cube-mesh. You do not need to memorize the mesh to understand the claim: eight GPUs are a small machine, not eight accessories. The wire is the product as much as the SM.

Pascal also shipped GP100 in other shapes, including PCI Express boards that still needed the old bus to talk to the host. The coexistence is the real deployment story. Not every site bought a DGX. A lot of sites bought a P100 in a vanilla 4U and discovered that the host link was still the old problem. NVLink helps GPU-to-GPU. It does not abolish the CPU. People who collapsed those facts wrote bad cluster diagrams.

Half precision shows up in the DGX-1 launch as 170 teraflops of FP16 peak. That number is a deep-learning number. Training had discovered that you could live in sixteen bits if you were careful. Pascal is early in that bargain; Volta will industrialize it with Tensor Cores. P100 is the transition chip: built for HPC and suddenly wearing an FP16 marketing suit because the customer changed in public.

I remember the first time I saw a P100 mezzanine (SXM) next to a PCI Express Tesla of the previous generation. The SXM module looks like a laptop board that got serious. No familiar bracket. Contacts meant for a baseboard. That is the moment the GPU starts to become a node component instead of an add-in card. The rack will finish that thought later. Pascal starts it.

If you want a physical object, an SXM P100 on a removed DGX-1 baseboard is the one — or a PCI Express P100 if you want the last Tesla that still looks like a cousin of GeForce. Read the April 5, 2016 DGX-1 press release next to the module. The press release is selling a supercomputer. The module is selling a package and a wire.

Pascal is not a personality. It is a generation where memory and interconnect stopped being “and also” bullets. After P100 you cannot write a compute-GPU story that is only about SM count. The people who tried, in 2016, were still writing 2010 reviews.

## Sources

- NVIDIA DGX-1 launch, April 5, 2016: eight Tesla P100, 16 GB each, NVLink hybrid cube mesh, up to 170 FP16 teraflops.
- NVIDIA technical blog, “DGX-1: The Fastest Deep Learning System” (topology and system breakdown).
- Public Pascal / Tesla P100 product record; HBM2 on-package memory.
- Public note: AMD Fiji (2015) as earlier consumer HBM shipment.
