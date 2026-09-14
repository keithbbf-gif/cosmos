---
title: torch.compile and the 2.0 line
slug: pytorch-2-compile
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 14
word_target: 600-1800
era: "2022–2024"
stack:
  - pytorch
---

# torch.compile and the 2.0 line

PyTorch 2.0’s get-started page, posted while the 2.0 nightlies were already public, called `torch.compile` the reason for the new major number. One function wraps a module and returns a compiled module. TorchDynamo, AOTAutograd, PrimTorch, and TorchInductor sit underneath. On NVIDIA and AMD GPUs, Inductor leans on OpenAI’s Triton. The feature is optional. 2.0 is backward compatible “by definition,” the docs said, because you do not have to call the function.

The stable tag `v2.0.0` landed on 15 March 2023 — the same spring as LLaMA’s leak and `llama.cpp`. The compiler and the local-LLM story are neighbors in the calendar and strangers in the stack. One makes eager code faster. The other makes a weight file run without eager code.

## Why a compiler without abandoning eager

The 2016 bet was the tape. The 2023 bet is that you can keep the tape for development and still get graph-level speed when the shape stabilizes. Dynamo intercepts Python bytecode, finds the graph, and lets Inductor emit kernels. If it fails, you fall back to eager. That fallback is the product. Researchers will not accept a compiler that turns a Tuesday experiment into a graph-mode archaeology dig. They will accept a decorator that sometimes works.

Soumith Chintala told VentureBeat the name 2.0 existed because users would treat `compile` as a new experience, not because the API had broken. That is a careful sentence. It is also a marketing sentence. The technical claim is testable: wrap the model, measure.

Dynamic shapes, the hard part, were called out in the 2.0 notes as in progress. Language models, which change sequence length every batch, are exactly the workload that punishes a naive compiler. The 2.x series is the story of that punishment being slowly reduced.

## Triton as a public hinge

Inductor generating Triton is a piece of open-stack luck. OpenAI published Triton as a language for writing GPU kernels that is not CUDA-the-career. PyTorch using it meant a lot of people met Triton as a backend they never wrote. The kernel language and the trainer sharing a generation is the kind of accident this series likes: public tools composing without a joint press release at the start.

## What 2.0 did not change

`nn.Module` stayed. The Hub stayed secondary. The license stayed. The Foundation (`pytorch-foundation-2022`) was already six months old. Users who never called `compile` got a new number on `pip show` and a pile of release notes about SDPA, Better Transformers, and MPS.

Scaled dot product attention as a stable functional op is, for the LLM years, as important as the compiler. Flash-attention-shaped kernels becoming a framework primitive is how a research paper becomes a default.

## 2026 look

A training script that does not call `torch.compile` is still normal. A serving stack that does not use PyTorch at all is also normal. The 2.0 line succeeded as a performance option and as a statement that eager had won the culture so thoroughly that the graph could return as an optimization.

If compilation errors greet you, you are in the old TensorFlow feeling with new nouns. The right look is the same: is this graph failure telling you something true about your control flow, or is the compiler young? In 2023 the answer was often the latter. In 2026 it is more often the former, which is a kind of maturity.

Read the official 2.0 get-started page and the `v2.0.0` notes together. The first is a tutorial. The second is a parts list. Neither needs a benchmark screenshot from a vendor keynote.

## Dynamo’s failure modes as a teaching tool

Graph breaks — a data-dependent `if`, a Python set, a print — are how you learn what the compiler can see. The 2.0 docs tell you to start with `fullgraph=False` and to read the break graph. Shops that skip that page treat `compile` as a magic decorator and then file a bug. The bug is often their control flow.

`mode="reduce-overhead"` versus `mode="max-autotune"` is a shop knob. Nightly versus stable is another. The 2.x series is fast-moving enough that a paper’s compile flags are a date.

## SDPA and the other 2.0 gift

Scaled dot product attention as a framework op, with backends that include FlashAttention-shaped kernels, is why a lot of people felt 2.0 without calling `compile`. A transformer that uses `F.scaled_dot_product_attention` is a 2.x transformer. A transformer that ships its own attention is either old or doing research.

MPS (Apple) as a beta in the 2.0 notes is the other local-GPU story, next to MLX (`mlx-apple-silicon`). PyTorch-on-Mac existed. It was not always pleasant. The 2.x years improved it. MLX exists because “improved” was not “native.”

## Compile and the LLM serving split

vLLM does not need you to `compile` your serving path in the 2.0 sense. Training might. The 2023 coincidence — 2.0 stable and LLaMA leaking in the same season — is a calendar joke. The stacks met later, when people trained with compile and served with vLLM. Two graphs. Two jobs.

## Triton as a language people met by accident

A researcher who never wrote a Triton kernel still runs Triton kernels if Inductor emitted them. That is a successful backend. It is also a debugging problem: the stack trace is not your Python. Learn enough Triton to read what you were given. You do not have to like it.

`fullgraph=True` is a research discipline: no breaks allowed. Most shops should not start there. Start with default, read the breaks, then tighten. The 2.0 docs say this. People skip the docs and file issues. The issues are often the docs.

## Sources

pytorch.org, “Get Started with PyTorch 2.0.” pytorch/pytorch `v2.0.0`, 15 March 2023. VentureBeat interview with Chintala on the 2.0 experimental announcement. Triton documentation (OpenAI).

See: `pytorch-1-research-default`, `pytorch-foundation-2022`, `tensorflow-2-eager-2019`, `jax-and-the-google-split`.
