---
title: What a FLOP stopped meaning
dek: Peak floating-point was a useful lie, then a marketing unit, then a number you had to annotate with a format.
slug: 45-what-a-flop-stopped-meaning
series: AI Compute Chip Magazine
status: staged
voice_check: edited
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# What a FLOP stopped meaning

The GeForce 256 launch talked about gigaflops and a Cray. The DGX-1 launch talked about 170 teraflops of FP16. The Hopper slides talk about petaflops-ish numbers that only exist in FP8 on a good day with the wind from the right library. The word FLOP stayed. The unit drifted until a responsible sentence looks like a legal disclaimer: sparse or dense, which format, which accumulation, which sparsity pattern, which clock, which neighbor chips you are allowed to count.

This is not only NVIDIA. Google’s TPU v1 paper uses TOPS, tera-operations per second, because 8-bit integer MACs are not floating-point. The industry then spent years mixing TOPS and FLOPS as if the letters were decoration. A TOP is not a FLOP. A sparse FLOP is not a dense FLOP. A TF32 FLOP is not an FP64 FLOP. If you add them, you are writing advertising.

Why did the lie stay useful for so long? Because in the CPU era, a flop was a reasonably stable object: FP64 in a LINPACK, maybe FP32 in a media codec, and you knew which talk you were in. The GPU era made the flop a family. Tensor Cores made the family a zoo. Sparsity features made the zoo a hypothetical zoo. A peak number that requires a structured-sparsity pattern your model does not have is a number about a chip that exists on the slide.

I still use peak FLOPS. I use them the way I use highway speed limits: as a scale, not as a trip time. Roofline is how you keep yourself honest. MLPerf is how you keep a vendor slightly honest, when the category is specified well enough. `nvidia-smi` utilization is how you keep yourself humble. None of these is a flop. They are the coping mechanisms we grew because the flop broke.

The breaking is the history. Somewhere between Pascal’s FP16 marketing and Ampere’s TF32 default, it became impossible to compare two accelerators by a single number without specifying a religion. The religions have names: HPC, training, inference, graphics. The same die can serve all four and still not have “a” flop.

If you want a physical object, take a keynote slide with a single huge number and write the format in the margin until the number looks smaller. That annotated slide is the artifact of this decade.

A closing that is not a sermon: the flop did not become meaningless because we got sloppy. It became meaningless because the machines got specialized, and specialization makes units multiply. We should have retired the bare word. We did not. We added superscripts and hope. This magazine can at least refuse to print a bare FLOP as if it were 1999. The Cray comparison was already a stretch then. It is a costume now.

Read the rest of the issue if you want the machines. This piece is only about the yardstick. The yardstick bent. We kept using it because the alternative was to say, every time, what we actually measured. We should say what we actually measured.

## Sources

- NVIDIA GeForce 256 launch flop language (1999).
- NVIDIA DGX-1 launch: 170 FP16 teraflops (2016).
- NVIDIA Ampere TF32 / Hopper FP8 / sparsity public marketing vs. architecture docs.
- Jouppi et al., ISCA 2017: TOPS, not FLOPS, for 8-bit MACs.
- Williams et al., Roofline (2009), as the adult way to talk about peaks.
