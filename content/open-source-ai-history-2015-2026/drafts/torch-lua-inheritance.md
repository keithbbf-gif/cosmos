---
title: What Lua Torch left in the room
slug: torch-lua-inheritance
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 10
word_target: 600-1800
era: "2011–2017"
stack:
  - torch
  - pytorch
---

# What Lua Torch left in the room

PyTorch’s first alphas kept a `torch.legacy` package so that Lua-era modules had somewhere to sit while the new `nn` grew. That is not nostalgia. It is a port. The people who built PyTorch had already built habits in Torch7: a `Module` with a `forward`, a container, a parameter list you could walk, a tensor library that knew CUDA. Python was the language change. The object model was a translation.

Ronan Collobert, Koray Kavukcuoglu, and Clément Farabet’s Torch7 workshop paper (2011) described a scientific computing framework with a Lua frontend and a C core. NYU, then Facebook AI Research, then a wider research circle, used it because it was fast to try an idea. Soumith Chintala’s name is on the PyTorch tags because he was already in that circle, already answering issues, already the public maintainer a certain kind of user trusted.

## Modules, not graphs

A Torch module is an object that holds parameters and knows how to map input to output. You compose modules. You print the tree. You save the parameters. This is so normal in 2026 that it is hard to see as a choice. The other choice was a global graph with names and collections. TensorFlow 1 chose the graph. Keras chose layers that hid the graph. Torch chose the object.

`nn.Sequential` is a sentence you can say in Lua Torch and in PyTorch. The inheritance is not metaphorical. The 2016 alphas said so.

Autograd in PyTorch is more complete than the older Torch `nn`’s reverse-mode story, which mixed explicit `updateGradInput` paths with newer tape ideas. The tape is the new math. The module is the old furniture.

## Why Lua lost

NumPy won the rest of science. A student who already wrote Python for data and scikit-learn did not want a second language to train a net. Interns arrived without Lua. Papers arrived with Python listings. The scientific community’s language monopoly is the unromantic reason PyTorch exists.

LuaJIT was fast. That was not enough. Ecosystem is a gravity well. The well was `pip`.

Facebook could have doubled down on Lua. It did not. It spent the cost of a rewrite to stay in the conversation. That is an institutional decision, not a weekend hack. Caffe2, in parallel, was the C++ production bet. The 2018 unification story — Caffe2 and PyTorch moving toward one family, ONNX as a hinge — is the later cleanup (`onnx-export-problem`).

## What survived the port

NCHW as a default. CuDNN bindings as a default. A DataLoader that is a Python iterator, not a graph of queues. Optimizers as objects that take `parameters()`. Checkpoints as pickle-shaped blobs (later a security problem, later `safetensors` as a reaction). A culture that treats the interactive interpreter as a first-class workplace.

What did not survive: Lua’s lightness, for better and worse. Python is heavier. It is also the language the Hub, the notebooks, and the hiring pipeline already spoke.

The `.t7` reader in `v0.1.6` is a small, perfect artifact. The new library could still eat the old files. Ports that cannot eat their own past are advertisements. Ports that can are shops.

## 2026 look

When a new engine — MLX, a Rust trainer, a JAX module — copies `nn.Linear` and `forward`, it is copying Torch’s noun, usually via PyTorch. The Lua years are why that noun exists. Students who never heard of Lua still live in its room.

If you want a primary object: the 2011 workshop paper, the PyTorch alpha notes on `torch.legacy`, and a Torch7 `nn` doc page. The rest is oral history and should be marked as such. This chapter stays with the files.

Chintala’s later public writing about the PyTorch Foundation (2022) still sounds like a maintainer, not like a brand manager. That continuity is also inheritance. The Lua shop taught a certain tone: fix the bug, ship the tag, do not give a keynote about destiny.

## `forward` as a cultural object

A method named `forward` is how a generation writes a net. JAX does not require it. Keras subclassing copied it. New engines copy it because the papers copy it. Lua Torch named the method. That is enough of a monument.

`parameters()` as a walkable iterator is the other monument. Optimizers that take a list of tensors are a Torch idea. TensorFlow 1 optimizers that took a loss op are a graph idea. The 2026 default is the list.

## The intern problem, again

A 2015 FAIR intern who knew Lua was already a special intern. A 2017 intern who knew Python was the default hire. The rewrite is a hiring document as much as a technical document. Companies rewrite libraries when the hiring pipeline speaks another language. That sentence is unromantic and true.

Caffe2 as the production twin is the reminder that Facebook did not think PyTorch was enough in 2016–2017. The later merge is a 2018 peace. This chapter is the 2011–2016 house the peace was signed in.

## A `.t7` on disk in 2026

If you find one, you have a museum piece that the 2016 reader might still eat. Convert it and write down the conversion. Do not assume a 2026 `torch.load` will care. Ports that eat their past do so in a named module (`torch.legacy`, a reader, a script). When the named module dies, the past dies with it.

## `nn` containers as a sentence you can still say

`Sequential`, `Parallel`, `Concat` — Lua names that mapped. PyTorch dropped some and kept the idea: a module is a tree. Printing the tree is a debugging act older than TensorBoard. `print(model)` is a Torch habit. Keep it.

Weight initialization folklore (`xavier`, `kaiming`) traveled in the same tree. The 2016 library inherited the folklore and then the papers renamed it. A port is a folklore vehicle.

## What Lua’s lightness bought

A small process, a fast start, a REPL that did not import half of PyData. Python’s heaviness is the tax for NumPy and the hiring pipeline. The tax is worth it for most shops. A 2015 FAIR engineer who still misses Lua is not confused. They miss a small process. `llama.cpp` later gave a small process back, for inference only. Different job, same longing.

## Sources

Collobert, Kavukcuoglu, Farabet, “Torch7,” BigLearn / NIPS workshop 2011. pytorch/pytorch `v0.1.1` (`torch.legacy`), `v0.1.6` (Lua `.t7` reader). Paszke et al., NeurIPS 2019 (project lineage).

See: `before-tensorflow-theano-torch-caffe`, `pytorch-2016-define-by-run`, `pytorch-1-research-default`, `onnx-export-problem`.
