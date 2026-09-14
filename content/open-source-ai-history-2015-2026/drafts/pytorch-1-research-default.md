---
title: PyTorch 1.0 and the research default
slug: pytorch-1-research-default
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 11
word_target: 600-1800
era: "2018–2021"
stack:
  - pytorch
---

# PyTorch 1.0 and the research default

PyTorch 1.0 was announced at the 2018 PyTorch Developer Conference and treated as the grown-up line: production-ready, Caffe2-adjacent, a stable `1.` for people who had been living on `0.4`. The exact day of the tag matters less than the social fact that followed. By 2019, a new methods paper that needed a reference implementation was, more often than not, a PyTorch repo. Papers With Code–style counts and conference hallway counts agreed. TensorFlow still trained production systems. PyTorch trained ideas.

The NeurIPS 2019 systems paper (Paszke et al.) is the project describing itself after the win: imperative style, tape autograd, a GPU story, a community. It is not modest. It is also not wrong about the programming model.

## What “research default” means as a shop fact

It means the official code for a new attention variant is an `nn.Module`. It means a reviewer can clone and run. It means a graduate student’s sunk cost is Python and `forward`, not `tf.cond`. It means Hugging Face’s library, when it grew from a BERT port to a zoo, grew in PyTorch first (`transformers-library-2018`).

It does not mean PyTorch was faster in every kernel. It does not mean TensorFlow vanished. It means the place you sketched became the place you published.

Fastai (Jeremy Howard, Rachel Thomas, and the fast.ai course) and Lightning (William Falcon) later sat on that default (`lightning-fastai-wrappers`). They could not have sat on a framework the papers had abandoned.

## 1.0 as a production promise

The 2018 conference talk promised that the research library and the production library would stop being two Facebook stories. Caffe2’s runtime, Torch Script, a path from a module to a graph you could ship — this is Google’s 2015 idea arriving late and optional. Optional is why researchers accepted it. You could ignore Torch Script for years. Many did. Then ONNX and, later, `torch.compile`, made the graph a performance tool instead of a lifestyle (`pytorch-2-compile`, `onnx-export-problem`).

JIT as an optional compiler is the compromise TensorFlow 2 also tried, from the other direction. PyTorch added a graph. TensorFlow added eager. They met in the middle with different defaults. Defaults decide cultures.

## The Hub that was not the Hub

PyTorch Hub (`torch.hub.load`) existed. It loaded a model from a GitHub repo with a `hubconf.py`. It was a reasonable design for researchers. It was not Hugging Face. It did not grow cards, likes, gated licenses, or a social graph of fine-tunes. When people say “the Hub” in 2026 they do not mean `pytorch.org/hub`. That lexical theft is a historical fact (`hub-as-distribution`).

## How the default froze

Once Transformers, Detectron, fairseq, and a thousand course homeworks sat on PyTorch, the switching cost reversed. A new framework now had to offer a reason. JAX offered transformations and TPUs. It took a slice. It did not take the default.

The Foundation (`pytorch-foundation-2022`) later made the default look like infrastructure instead of a Facebook product. That ceremony matters for procurement. It did not create the default. The papers created the default. The Foundation notarized it.

## 2026 look

Open a new LLM trainer — Axolotl, Unsloth, a TRL script, a university lab’s repo — and you will see `import torch` before you see a license. That order is this chapter’s residue. The license may be Llama’s. The tensor library is PyTorch’s, or a runner that already ate a PyTorch-trained file.

`Variable` is gone. `torch.tensor` is ordinary. AMP, DDP, FSDP, `torch.compile` — the 1.x and 2.x years piled systems on an API that still looks like 2016. That stability is the inheritance Lua Torch wanted and TensorFlow 1.x, for research, failed to keep.

If you need a dated object: the 2018 Dev Conference stream, the 1.0 release notes, and the 2019 NeurIPS paper. Hallway counts are hallway counts. Mark them as such if you use them. The repos are the evidence.

## AMP, DDP, and the years the library grew up

Automatic mixed precision and DistributedDataParallel are 1.x systems work that made multi-GPU the default, not a specialist path. FairScale and then FSDP (later in-core) made large models a PyTorch story instead of a DeepSpeed-only story. DeepSpeed still exists. The point is that the research default grew a systems department.

`torch.cuda.amp` folklore — `GradScaler`, unscale, inf checks — is 2020 shop talk. A 2026 `torch.amp` API is the same talk with cleaner names. The 1.x years are when that talk became ordinary.

## Reproducibility as a social default

A paper without a PyTorch repo in 2020 looked incomplete in a way a paper without a TensorFlow repo in 2016 did not yet. That social fact is the default. It is not a quality metric. Bad papers shipped PyTorch. Good papers shipped JAX. The default is a habit of the venue, not a halo.

## 1.0 conference as a primary source

Watch the 2018 Developer Conference keynote if you want the production promise in the original voice. Read the NeurIPS 2019 paper if you want the same promise in venue voice. They agree: eager first, graph optional, community already large. The Foundation (2022) is a later notarization of a fact that was already true in 2018–2019.

## TorchScript as the optional cathedral

`torch.jit.trace` and `script` were the 2018–2020 production path. They failed on dynamic models in ways that felt like TensorFlow 1. Researchers ignored them. Production teams fought them. `compile` later became the friendlier compiler. TorchScript still exists in trees. If you meet it, you are in a 2019 production promise.

ONNX export from a 1.x module is the other promise (`onnx-export-problem`). Same joint, different IR.

## fairseq, Detectron, and the official gravity

When Facebook’s own research code sat on PyTorch, the default hardened. A lab that wanted to compare to the official detection or translation stack imported `nn`. That is how defaults freeze: official code plus course homework plus a Hub library. 1.0 is the year those three lined up.

## Sources

PyTorch 1.0 announcement / Developer Conference 2018. Paszke et al., NeurIPS 2019. pytorch.org Hub documentation. Papers With Code framework tallies as secondary, 2019–2022.

See: `pytorch-2016-define-by-run`, `tensorflow-vs-pytorch-2017-2019`, `pytorch-foundation-2022`, `transformers-library-2018`.
