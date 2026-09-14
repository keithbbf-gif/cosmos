---
title: Define-by-run, 2016
slug: pytorch-2016-define-by-run
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 9
word_target: 600-1800
era: "2016–2017"
stack:
  - pytorch
---

# Define-by-run, 2016

PyTorch’s `v0.1.6` release notes, frozen on 21 January 2017, contain a line other release notes do not bother with: “PyTorch public release on 18th Jan, 2016.” The alphas (`v0.1.1` on 1 September 2016, tagged by Soumith Chintala) are the ones people who lived on GitHub remember. The January date is the one the project later treated as a birthday. Either way, the object is the same: a Python library that built the graph as you ran the code.

Define-by-run — Chainer’s phrase, and a fair one — means the autograd tape records what this forward pass actually did. A Python `if` is an `if`. A loop is a loop. You can drop into pdb and see a tensor. You do not open a session. You do not name a placeholder unless you want to. That is the entire pitch. It was enough.

## What the alphas shipped

`v0.1.1` said the new `torch.nn` and `torch.autograd` were working and unit-tested, with a draft `torch.optim`, and that the old Torch pieces would live at `torch.legacy`. That sentence is the port in public (`torch-lua-inheritance`). The module API you still write in 2026 — `nn.Linear`, `forward`, `parameters()` — is already there.

By `v0.1.6` there was a model zoo for vision, CuDNN-bound modules, a DataLoader with pinned memory, a functional `nn` interface, sparse embeddings, a Lua `.t7` reader, and the usual pile of shape-check errors made “more informative.” It is a research library becoming a product without calling itself a platform.

Adam Paszke’s autograd work, and the later 2017 Autodiff workshop paper (“Automatic differentiation in PyTorch”), are the math under the tape. The NeurIPS 2019 paper (“PyTorch: An Imperative Style, High-Performance Deep Learning Library”) is the retrospective, written when the library had already won the room this chapter is about to leave.

## Why it felt faster to think in

Speed of kernels mattered. Speed of thought mattered more. A researcher who wanted a dynamic network — variable-length inputs, recursive structure, a decoder that stopped early — wrote Python. The TensorFlow 1 answer was `tf.while_loop` and a headache. The PyTorch answer was `for`.

That difference is easy to moralize. It is harder to historicize. Google had reasons for graphs (`tensorflow-1-static-graphs`). Facebook’s research org had reasons for Torch. PyTorch is what you get when the second group decides Python is non-negotiable.

Chainer (Preferred Networks) had already shown define-by-run in Python. DyNet had its own tape. PyTorch was not the first eager library. It was the one with FAIR’s weight, Torch’s module habits, and a GPU story that did not feel like a science project.

## What 2016 did not decide

It did not decide production. Caffe2 was still Facebook’s serving accent. ONNX (2017) was still in the future. `torch.compile` (2023) was not imaginable as a one-liner. The 2016 library was a researcher’s object that happened to be fast enough to train real nets.

It did not decide the Hub. There was no Hub. You posted a `.pth` on a faculty page or you didn’t. `torchvision` pretrained weights were a zoo, not a social network.

It did not decide language models. The 2016 conversation was still ImageNet, translation, detection. The later fact that Transformers-the-library defaulted to PyTorch is a 2018–2019 fact (`transformers-library-2018`).

## How to look at an old `0.1` script

You will see `Variable`. You will see `volatile`. You will see API shapes that 1.0 cleaned up (`pytorch-1-research-default`). The `forward` method will look like home. That is the tell. TensorFlow 1 scripts do not look like home to a 2026 reader. Early PyTorch scripts do, with wrinkles.

If you want the object: the GitHub tags are still there. Read `v0.1.1` for the port. Read `v0.1.6` for the birthday line and the zoo. Then read a Chainer page if you want the other eager ancestor. This series is not a patent office. It is a shop history. In the shop, PyTorch is the eager library that the rest of the public stack later assumed.

## Autograd as a tape you can print

`tensor.grad`, `requires_grad`, a backward that fails because you forgot `retain_graph` on a toy example — these are 2016 sensations that are still 2026 sensations. The tape is visible. That visibility is the product. TensorFlow 1’s tape was a graph you built in advance. The difference is when you were allowed to be wrong.

Paszke’s 2017 workshop paper is short and worth reading if you want the math without the 2019 marketing. The 2019 NeurIPS paper is the project at the moment it knew it had won research. Read them in order.

## DataLoader without graph queues

Queue runners were a graph. DataLoader is a Python iterator with workers and pinned memory. It is also a source of deadlocks and `num_workers` folklore. It is still better than queue runners for the people who write Python. The 0.1.6 notes already care about this. A research library that cares about data loading is a research library that has been used.

## What “public release 18 January 2016” is worth

The line in the 0.1.6 notes is a project’s own birthday. The alphas are the GitHub birthday. This series keeps both. A history that needs a single day can use 18 January 2016 and footnote the September alphas. A history that needs a file can use `v0.1.1`. The programming model does not change between those dates. The users do.

## `nn.functional` versus `nn.Module` as a 2016 fork in the road

The 0.1.6 notes already mention a functional `nn`. A linear as a function and a linear as a module are two styles. The module won the papers. The functional style won the insides of attention implementations. Both live in one file in 2026. The 2016 library already contained the fork.

Hooks on modules — a 2016-era feature that grew — are how people inspect activations without rewriting `forward`. They are also how a quiet memory leak happens. The tape plus hooks is a power tool. Power tools cut.

## CuDNN as a default, not a badge

“All relevant neural network modules are now CuDNN bound,” said 0.1.6. That sentence is a 2016 performance claim and a vendor coupling. NVIDIA’s library inside a research default is the iron story hiding under the tape story. It is still the iron story.

## Sources

pytorch/pytorch tags `v0.1.1` (2016-09-01), `v0.1.6` (2017-01-21, notes dating public release 18 January 2016). Paszke et al., Autodiff workshop 2017; NeurIPS 2019. Chainer documentation (define-by-run).

See: `torch-lua-inheritance`, `pytorch-1-research-default`, `tensorflow-vs-pytorch-2017-2019`, `transformers-library-2018`.
