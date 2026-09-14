---
title: ONNX and the export problem
slug: onnx-export-problem
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 43
word_target: 600-1800
era: "2017–2026"
stack:
  - onnx
  - pytorch
  - tensorflow
---

# ONNX and the export problem

On 7 September 2017 Facebook and Microsoft announced ONNX — Open Neural Network Exchange — in matching research and Azure posts: a graph format so a model trained in one framework could run in another, or in a dedicated runtime. The first named citizens were Caffe2, PyTorch, and Microsoft’s Cognitive Toolkit. The problem statement in Facebook’s post is the one that survived: researchers lived in one stack, production lived in another, and rewriting a net by hand was the tax. Joaquin Candela’s public comments that week described a translator for Caffe2 and a tracer for PyTorch — record the eager run, emit a graph. That tracer instinct is still how a lot of export actually works.

LF AI & Data later housed the project. ONNX Runtime became Microsoft’s product-shaped runtime. The dream was a crate that was not a pickle and not a SavedModel. The dream half-worked. Export is still a problem. That is the chapter.

## Why export exists

Training APIs optimize for experimentation. Serving APIs optimize for a fixed signature (`tensorflow-serving-and-tflite`). A converter is the joint. ONNX Runtime, TensorRT, Core ML, TFLite, TorchScript, `torch.export`, ExecuTorch — the names change. The joint stays.

2017’s specific joint was Facebook’s two-stack problem (PyTorch research, Caffe2 production) and Microsoft’s stack problem (CNTK, then ONNX Runtime). The 2018 Caffe2-into-PyTorch unification (`pytorch-1-research-default`) removed one reason for ONNX inside Facebook and did not remove the industry reason. A shared IR is how you stop rewriting models by hand. A shared IR is also how you discover that your research net was never a graph.

## Where it breaks

Custom ops. Dynamic control flow. Sparse MoE routers. New attention kernels. A research model that is a pile of Python will fail `torch.onnx.export` in a way that is informative if you know the IR and insulting if you do not. Every major LLM serving engine eventually stopped waiting for a perfect ONNX graph and wrote a loader for `safetensors` plus a model definition. vLLM does not need you to succeed at ONNX (`vllm-paged-attention`). A medical-imaging shop from 2019 still does.

So ONNX is the interchange for a lot of vision and classical nets, and a maybe for transformers. Name the op. Name the dynamic shape. Name the converter version. “ONNX doesn’t work” is not a bug report. “This MoE router fails `torch.onnx.export` 2.x on dynamic batch” is a bug report. The 2017 announcement cannot file the report for you.

If your research is a new kernel, plan the export on week one or plan to serve in-Python. The second plan is how vLLM won transformers. The first plan is how a 2019 vision model reached a phone. Pick on purpose.

## Adjacent crates

TorchScript was PyTorch’s in-house IR. `torch.compile` (`pytorch-2-compile`) is a compiler, not an interchange, but it is the same instinct: leave eager, gain a graph. `torch.export` is the later in-house export story, Microsoft not required in the room. ExecuTorch is the edge child. TFLite flatbuffers are Google’s phone IR. GGUF is the local-LLM IR (`llama-cpp-gguf`). `safetensors` is not an IR; it is a safe tensor dump. People conflate all five. A dump is not a graph. A graph is not a quant format.

Caffe2 + PyTorch + ONNX was a Facebook peace for 2018 nets. Attention kernels, KV caches, and MoE routers were not the 2018 net. The IR grew. The runners that won LLM serving did not wait. They loaded tensors and a Python model class. That is a defeat for interchange and a win for shipping.

## 2026 look

If you ship vision to a phone, you still live in converters. If you ship a 70B chat model, you live in a runner that ate the Hub files. ONNX did not lose. It kept the job it was good at and did not become the LLM crate. CNTK is gone. The 7 September 2017 press release is still worth reading as a statement of the problem. The problem outlived CNTK.

Read the Facebook research post and the Azure post from that day, then a recent ONNX Runtime transformer note. The gap between them is the history.

## Sources

Facebook Research, “Facebook and Microsoft introduce new open ecosystem…,” 7 September 2017. Microsoft Azure Blog, same day. ONNX and ONNX Runtime docs. PyTorch ONNX export docs; `torch.export` docs. Caffe2 / PyTorch unification notes, 2018.

See: `pytorch-2016-define-by-run`, `tensorflow-serving-and-tflite`, `pytorch-2-compile`, `llama-cpp-gguf`.
