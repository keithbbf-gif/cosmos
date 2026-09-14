---
title: Training silicon and inference silicon are different animals
dek: The industry kept saying "AI chip" as if the forward pass and the backward pass wanted the same die.
slug: 42-training-vs-inference-silicon
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Training silicon and inference silicon are different animals

TPU v1 was an inference chip. The ISCA paper is not shy. The job is the forward pass, the SLO is a tail latency, the precision is 8-bit, the comparison is a K80 that was trying to be a general computer. TPU v2 and v3, and NVIDIA’s V100/A100/H100 line as people actually bought them, are training animals: they want capacity, they want all-reduce, they want a backward pass that materializes gradients, they want to run for a week without a jitter story. Those are different animals. The industry kept putting them in the same zoo sign: AI chip.

The differences are public and mechanical. Training wants high-bandwidth links between chips because the batch is split and the gradients must meet. Inference can often live on one chip, or on a small pipeline, and cares about the 99th percentile and the tokens per watt. Training wants enough memory to hold activations (or a rematerialization strategy). Inference wants enough memory to hold weights and a KV cache. Training can hide a compiler’s first-run cost. Inference cannot hide a 200-millisecond surprise.

NVIDIA’s product line grew names that try to admit this: training-oriented SXM parts, inference-oriented T4 then L4 then various “edge” and “NVIDIA L-series” stories, Triton Inference Server as a software admission that serving is a job. Google grew v5e versus v5p style splits in the cloud catalog: efficiency versus peak. Amazon’s Inferentia and Trainium, as publicly described, are the split as two product nouns. The nouns are the tell. When a vendor uses two nouns, believe them.

The confusion is profitable. A slide that says “AI performance” can pick the benchmark that fits the animal. TOP500-ish dense math, MLPerf Training, MLPerf Inference — pick one and you get a different winner. A magazine draft should refuse the combined slide. Ask: is this a week of training or a millisecond of serving? If the speaker cannot say, the speaker is selling.

Edge inference is a third animal people keep stuffing into the same sentence. A phone NPU, a camera DSP, an automotive part — those care about idle watts and a thermal envelope you can hold. They are not a V100 and they are not a TPU pod. They belong in a different issue. Mentioning them here is only to stop the zoo sign from growing a third silent lie.

I have run both jobs on the same GPU because a GPU is a general-enough animal. That generality is NVIDIA’s blessing and curse. It means you can buy one SKU and do both badly-to-well. It also means you will overbuy for inference and under-connect for training if you believe the zoo sign. The TPU line, being ruder, sometimes makes the split clearer. v1 is the clearest.

If you want a physical object, put a T4 next to a V100. Same era, same vendor, different animals. The T4 is a small inference/video part. The V100 is a training brick. People used each for the wrong job, because people are people. The hardware still knew.

This article does not pick a winner in the inference-ASIC gold rush. It says the gold rush exists because the animals diverged in public, and because the combined slide became embarrassing. After 2017 you can still say “GPU.” You should not say “AI chip” without a clause.

## Sources

- Jouppi et al., ISCA 2017: TPU v1 as inference, tail-latency argument.
- Google Cloud TPU generation docs (training pods vs. efficiency SKUs).
- NVIDIA product splits: Tesla/V100/A100/H100 vs. T4/L4 and inference-server software.
- MLPerf Training vs. MLPerf Inference as public, separate scoreboards.
- AWS Inferentia / Trainium public product pages (two nouns).
