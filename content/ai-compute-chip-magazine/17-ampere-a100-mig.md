---
title: Ampere A100 and the sliced GPU
dek: In 2020 NVIDIA shipped a training monster that could also be carved into smaller GPUs. The carving is the product idea.
slug: 17-ampere-a100-mig
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
description: "In 2020 NVIDIA shipped a training monster that could also be carved into smaller GPUs. The carving is the product idea."
image: "assets/svg/spine-gpu-public-history.svg"
image_alt: "Timeline schematic of selected public GPU, CUDA, and TPU milestones from 1999 through 2024."
---

# Ampere A100 and the sliced GPU

The A100, Ampere generation, 2020, is easy to file under “more.” More HBM2e. More Tensor Core throughput. A 40 GB then 80 GB memory story. TF32 as a format that let people keep writing FP32 in the framework and still hit a tensor path. All of that is on the public slides. The idea that is easier to miss is MIG: Multi-Instance GPU. One physical A100 can be partitioned into smaller, isolated GPU instances, each with its own memory slice and SM slice, suitable for inference or for the kind of shared cluster where seven teams want a piece of the expensive board.

MIG is a cloud idea that arrived in silicon. Hyperscalers had already been time-slicing and MIG-less sharing with various levels of pain. NVIDIA’s bet was that a hard partition, done in the device, would be something a scheduler could treat like a smaller SKU. The docs read like an operations manual because they are one: instance profiles, memory sizes, how many you can have at once, what you cannot do while partitioned. That prose is the opposite of a keynote. It is also how you know the customer is a platform team, not a single researcher with a box.

Ampere’s other public move, TF32, is a format story. Nineteen-bit-ish tensor math with an FP32-looking exponent, sold as “your code does not change.” Sometimes the code did not change. Sometimes the model did, a little, and the internet grew another reliability thread. Mixed precision always has this aftertaste. Ampere made the aftertaste default for people who never opted into FP16.

The A100 became the unit of the 2020–2022 training boom the way the V100 had been the unit of 2018. Eight-GPU HGX boards, DGX A100, then dense clouds that quoted A100-hours like electricity. The pandemic years are in the background of every procurement story from that time: lead times, scalping, “we have budget and no boards.” A chip article should mention the queue without turning into a supply-chain documentary. The queue is how you know the part was not theoretical.

Consumer Ampere (the 30-series) is a cousin with a different memory system and a different audience. Do not collapse them. The A100 is an SXM or PCI Express datacenter part with HBM and a MIG story. The 3090 is a GDDR6X monster that enthusiasts used as a poor man’s training card. Both are Ampere. They are not the same product.

If you want a physical object, an A100 80 GB SXM is the one that still shows up in used-cluster listings like a used industrial engine. Heavy, serial-numbered, no RGB. The interesting photograph is not the module. It is the `nvidia-smi` output with MIG instances listed like apartment numbers. That screenshot is Ampere’s contribution to how a GPU is allowed to look: not only a whole chip, but a chip that can be zoned.

This piece does not follow Hopper. Hopper will add a transformer-specific story and a different scale. A100 is the last NVIDIA training GPU a lot of institutions bought before the prices went lunar. It is also the first one that wanted to be several GPUs when you asked.

## Sources

- NVIDIA A100 Tensor Core GPU architecture whitepaper (2020): TF32, HBM2e, MIG overview.
- NVIDIA MIG user guide (instance profiles, isolation language).
- NVIDIA DGX A100 / HGX A100 public system specs.
- Public distinction: GeForce RTX 30-series as consumer Ampere, not A100.
