---
title: Why TPUs and GPUs kept not replacing each other
dek: For a decade the obituaries were written in both directions. Both machines are still here.
slug: 38-why-tpus-and-gpus-coexist
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
---

# Why TPUs and GPUs kept not replacing each other

Every year or so someone writes that the GPU is done because the TPU exists, or that the TPU is a Google curiosity because the GPU exists. The public record of 2016–2026 is ruder than those obituaries. Google trained and served on TPUs and also bought GPUs. Everyone else trained mostly on GPUs and sometimes rented TPUs. NVIDIA’s data-center business grew into a monster. Google’s TPU generations kept shipping. Coexistence is the fact. The explanations are a pile, not a slogan.

Start with the buyer. NVIDIA sells to anyone with money and a PCIe slot or a rack contract. Google sells TPU hours to cloud customers and, first, to itself. Those are different markets even when the workload looks the same. A startup can buy eight used A100s and own them. A startup cannot own a TPU pod in the same way. Ownership versus rental is not a footnote. It is why CUDA kept a hobbyist-to-HPC pipeline that the TPU never fully copied.

Then the software wetland. PyTorch-plus-CUDA is a default. JAX-plus-XLA-plus-TPU is a powerful dialect with a smaller church. People port. People do not all port. The existence of `jax` on GPU and `torch` on TPU (with various levels of pain) is the industry trying to pretend the machines are the same. They are not. One is a programmable SM with libraries. The other is an array-plus-compiler with a pod network. You can make them share a front end. You cannot make them share a soul.

Then the workload. Inference at Google scale with a stable model loved TPU v1. Training a new idea on Friday night loved a GPU you already had. Fine-tuning a 7B model in a lab loved a 3090. Serving a latency-sensitive endpoint might love either, depending on the batch and the compiler. The word “AI chip” hides this split. Once you unhide it, coexistence is the boring prediction.

Then politics and supply. Export rules, cloud quotas, NVIDIA lead times, Google internal priority — these are public enough, in filings and outages and blog posts, to mention without pretending we have a classified brief. When H100s were scarce, TPU capacity became a story. When TPU quotas were scarce, people went back to GPUs. Scarcity is a teacher. It teaches you that the other machine is not theoretical.

I do not want a kumbaya ending. The machines compete. They take jobs from each other. Google has every incentive to move work onto its own silicon. NVIDIA has every incentive to make the next framework feature NVIDIA-shaped. Coexistence is not peace. It is a stalemate with enormous revenue on both sides and a long tail of other accelerators hoping the stalemate breaks.

If you want a physical object, put a TPU board photo next to an H100 SXM photo. Same era of problem, different religions of programmability. The industry kept both religions because both have believers who ship.

Do not pick a winner for 2030. Scold the obituaries instead. The GPU did not die in 2016 when Jouppi went on stage. The TPU did not die in 2023 when every startup deck said “NVIDIA.” What died, over and over, was the fantasy that one architecture gets to be the last architecture.

## Sources

- TPU v1 ISCA 2017 paper (Google still using CPUs and GPUs for other ML as of that writing).
- NVIDIA data-center GPU public product line (P100 through Blackwell) as the other volume path.
- Public framework paths: PyTorch CUDA default; JAX/XLA on TPU and GPU; Torch/XLA efforts.
- Public cloud TPU product pages and NVIDIA cloud-instance catalogs (both for sale, same years).
