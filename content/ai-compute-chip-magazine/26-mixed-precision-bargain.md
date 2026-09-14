---
title: "Mixed precision: the accuracy bargain"
dek: FP16, BF16, TF32, FP8 — the chip got faster every time we agreed the extra bits were a lifestyle.
slug: 26-mixed-precision-bargain
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Mixed precision: the accuracy bargain

For a long time, scientific computing treated IEEE FP64 as adulthood and FP32 as a compromise you explained in a footnote. Neural nets, as a public industrial practice, went the other way. They discovered that a lot of training can live in sixteen bits if you keep a thirty-two-bit copy of the weights and scale the loss when the exponents get shy. NVIDIA’s mixed-precision training documentation, Baidu’s and then NVIDIA’s work on FP16 training, Google’s bfloat16 on TPUs, Ampere’s TF32, Hopper’s FP8 — the acronyms changed. The bargain did not. Fewer bits, more math per second, more math per byte, and a ritual to keep the model from exploding.

FP16 is the first widely taught bargain on NVIDIA hardware. Tensor Cores on Volta loved it. Loss scaling became a paragraph in every training README. The paragraph hid a lot of pain: overflow, underflow, the one layer that needed to stay wide, the batch-norm that misbehaved. People learned. Libraries absorbed the ritual. Automatic mixed precision in PyTorch and TensorFlow is a historical artifact: the bargain became a context manager.

BF16, born as a TPU-friendly format with an FP32 exponent and a short mantissa, is the bargain for people who hated loss scaling. Google published it. NVIDIA later added it. The exponent range is the feature. The mantissa is the cost. Whether a given model “prefers” BF16 or FP16 is an empirical fight that should not be settled in a magazine. The existence of the fight is the history.

TF32 is NVIDIA’s peace offering to people who did not want to change their dtypes. Ampere Tensor Cores could take FP32 inputs, internally use a 10-bit mantissa / 8-bit exponent style format, and accumulate wide. NVIDIA said your code could stay FP32. Sometimes the answers stayed close enough that nobody opened a ticket. Sometimes they did not. Default math that is not the IEEE math you learned in school is a cultural event. TF32 is that event with a product name.

FP8, on Hopper and then everyone else’s slides, is the bargain again with less suitcase. Training recipes and inference recipes split. Inference can often live even smaller. Training is pickier. The public Transformer Engine materials are a recipe book for that pickiness. Treat them as a recipe book, not as physics.

Why this is a chip-history article and not a numerics lecture: every one of these formats exists because a vendor spent area on a path that is fast only for that format. The formats are the software face of Tensor Cores and systolic arrays. If you refuse the bargain, you buy more chips or you wait. If you accept it, you join a church with release notes.

If you want a physical object, there isn’t one. The object is a table of formats that has been copied from an NVIDIA blog into a thousand Slack channels, with someone’s handwritten “use BF16” in the margin. That table is the last decade of training.

A careful closing: mixed precision is not a trick NVIDIA invented alone, and it is not a trick that always works. It is a public, documented, sometimes painful agreement between people who want bigger models and machines that are tired of moving extra bits. The bits we discarded are the real monument.

## Sources

- NVIDIA mixed-precision training documentation and Automatic Mixed Precision guides.
- NVIDIA Volta / Ampere / Hopper architecture materials: FP16 Tensor Cores, TF32, FP8.
- Google bfloat16 public documentation (TPU).
- Micikevicius et al., “Mixed Precision Training,” ICLR 2018 (public paper).
