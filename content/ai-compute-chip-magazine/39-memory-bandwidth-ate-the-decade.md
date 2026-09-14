---
title: Memory bandwidth ate the decade
dek: The FLOPS slides kept going up. The useful ones were about bytes per second and whether you reused them.
slug: 39-memory-bandwidth-ate-the-decade
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
portrait: null
figures:
  - ../assets/39-memory-bandwidth-ate-the-decade/historical-timeline.svg
  - ../assets/39-memory-bandwidth-ate-the-decade/architecture-diagram.svg
---
# Memory bandwidth ate the decade

There is a slide, and then there is a profiler. The slide says teraflops. The profiler says the pipes were hungry and the arithmetic units were polite. For most of the 2010s and the early 2020s, the honest GPU and TPU conversation was about memory: how fast you could feed the array, how often you reused a weight, how much HBM you could afford, how badly a stray materialization punished you. Roofline models — Williams, Waterman, Patterson, 2009 — were already public when CUDA was a toddler. The industry spent a decade rediscovering them every time a new model family arrived.



<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/39-memory-bandwidth-ate-the-decade/historical-timeline.svg" alt="Timeline of public milestones for Memory bandwidth ate the decade: dated anchors from press releases, papers, and product records — not live benchmark scores." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Calendar anchors for this piece. Years follow the essay; verify against Sources before publication.</figcaption>
</figure>


Transformers made the rediscovery fashionable. Attention, in the naive form, is a memory-traffic event with a softmax in the middle. FlashAttention-class papers, public and widely implemented, are bandwidth essays. Mixture-of-experts is a routing-and-capacity essay. KV caches at decode time are a memory-capacity essay. None of that is a secret architecture. It is the roofline wearing a 2023 hoodie.

GPUs got more FLOPS per watt and per dollar than they got bytes per second per dollar. Vendors answered with HBM, with bigger on-chip memories, with Tensor Cores that do more math per load, with formats that make each load carry more math. Those answers are real. They do not repeal the rule. If your kernel is a streaming walk over a tensor you will not see again, you are buying a memory controller that happens to have ALUs attached.

I first learned this as a shared-memory tiling exercise. Then I learned it again as “your batch size is a memory size.” Then I learned it again as “you are waiting on NCCL because the gradient is a large tensor.” Same boss, different hallway. A magazine that only prints FLOPS is a vendor’s magazine. A magazine that prints bandwidth is closer to the machine.

You can date the rediscoveries. 2008–2010: CUDA people tiling GEMMs because GDDR could not hide a naive multiply. 2012: AlexNet’s authors saying GPU memory, not a better idea, capped the net. 2016: P100’s public story leading with HBM2 because Pascal’s arithmetic would have been a joke without the sandwich. 2020: A100’s 40 GB then 80 GB as a capacity fight, not a core fight. 2022–2024: every serious transformer paper growing a “memory” section that is longer than the “math” section. The decade did not have one bandwidth crisis. It had a repeating class.

The TPU v1 paper is almost rude about this. The authors note that if the TPU had had the CPU’s GDDR5, the achieved TOPS would have jumped. Even their specialized array was, on some workloads, a memory story. That sentence should be taped to every keynote.

If you want a physical object, an HBM stack next to a GDDR chip is the pair. The stack is what you buy when you are tired of lying to yourself about the bus. The GDDR chip is what you buy when the product is still a game at 144 hertz. Both are memory. One of them ate the datacenter decade.

A practical test for any new accelerator announcement: hide the FLOPS line with your thumb. What is left — bytes per second, bytes on package, bytes between chips — is the announcement. If nothing is left, the announcement is a costume.

This article is standalone on purpose. You do not need a later-architecture piece to understand a roofline. You need a peak operation number, a peak bandwidth number, and an honest arithmetic intensity. The rest of the decade was commentary.







<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/39-memory-bandwidth-ate-the-decade/architecture-diagram.svg" alt="Architecture diagram for Memory bandwidth ate the decade: illustrative GPU or datacenter shape from the public record, not an official vendor block diagram." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Illustrative system shape for the argument — protocol and architecture, not scraped silicon photography unless noted.</figcaption>
</figure>
## Sources

- Williams, Waterman, Patterson, “Roofline: An Insightful Visual Performance Model,” CACM 2009.
- Jouppi et al., ISCA 2017 TPU paper (memory as limiter; GDDR5 counterfactual in the abstract).
- Public GPU memory-bandwidth specs across Pascal–Hopper generations (HBM2/HBM2e/HBM3).
- Public FlashAttention papers as transformer-era bandwidth literature.
