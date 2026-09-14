---
title: Serving, Lite, and the phone
slug: tensorflow-serving-and-tflite
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 6
word_target: 600-1800
era: "2016–2022"
stack:
  - tensorflow
  - tflite
---

# Serving, Lite, and the phone

The 2015 white paper’s most honest sentence is the one about phones. TensorFlow was supposed to run on a device you carry. That is not a research flex. It is a Google product requirement. TensorFlow Serving and TensorFlow Lite are the public names for the two halves of that requirement: a server process that loads a frozen graph, and a mobile/embedded runtime that does not want Python at all.

If you only ever trained, these libraries were footnotes. If you shipped, they were the point. A lot of the “TensorFlow is heavy” complaint is a person meeting the serving story in the training API. The serving story is why the training API was a graph.

## Serving as a process, not a notebook

TensorFlow Serving, announced in the 2016 window and developed in the open under Apache 2.0, is a C++ server that loads SavedModels, versions them, and answers gRPC or REST. You do not import your training code. You export a signature: inputs, outputs, a tag. The server can hot-swap versions. That is a boring, correct design for a ranker or a vision model behind a product.

The interesting historical fact is not the RPC. It is the wall. Training and serving are different programs. PyTorch shops later built the same wall with TorchServe, ONNX Runtime, Triton, and vLLM. They just did not ask you to live on the serving side of the wall while you were still debugging a loss.

A SavedModel is a directory with a graph and weights. It is closer to a crate than to a checkpoint. You can argue about whether the crate format was pleasant. You cannot argue that the crate was optional for the kind of deployment Google wanted.

## Lite, quantization, and the edge

TensorFlow Lite took the same graph and shrank the runtime. The converter ate a SavedModel or a frozen graph and emitted a `.tflite` flatbuffer. Quantization — first a blunt 8-bit story, later more careful schemes — was how a mobile CPU ran a vision model without a 500-megabyte interpreter.

TFLite Micro went further: microcontrollers, no operating system to speak of, a subset of ops. That line of work is easy to forget in a 2026 conversation about 405B downloads. It is the part of Google’s stack that still looks like 2015’s “phones and tablets” sentence.

Google’s later on-device story (NNAPI, then Gemini Nano / AICore, then Gemma 4 on-device in 2026) sits on this habit even when the brand names change. A company that has already shipped a Lite interpreter thinks about RAM as a hard number. A company that has only shipped an API thinks about RAM as a cloud invoice.

## TensorFlow.js and the other edge

TensorFlow.js (2018) put the same institutional instinct in a browser. Layers models, graph models, WebGL, later WebGPU. It is not the Hub. It is not Transformers.js, which is a later Hugging Face object. It is Google saying: the graph should run where the user already is. Love the API or hate it, the instinct is consistent.

## Why researchers ignored this and why that was rational

A PhD student in 2017 wanted a new layer, not a signature def. Serving docs felt like someone else’s job. Lite converters failed on ops the student had just invented. The rational move was PyTorch + a pickle, and a promise to “productionize later.” Many papers kept that promise in the same way people keep promises to floss.

The cost showed up in 2020–2023, when “later” arrived and the pickle was a security incident and the custom op was not in ONNX. Export (`onnx-export-problem`) became a field. Lite and Serving had been an early, Google-shaped answer to a problem the rest of the field postponed.

## 2026 look

If you find a `.pb` or a SavedModel directory in an old repo, you are looking at a serving object. If you find a `.tflite`, you are looking at a phone object. If you find only a `checkpoint` without a signature, you are looking at a training leftover that nobody froze. That last file is the common one. It is also the one that cannot cross a language boundary without archaeology.

vLLM and `llama.cpp` are not TFLite. They are the language-model generation’s answer to the same split: a runner that is not your training loop. The habit — export, then run — is older than Llama. TensorFlow just made you feel it earlier.

Google’s 2016–2018 serving posts and the TFLite converter guides are the first-party record. This chapter does not need a download count. It needs the directory layout: `saved_model.pb`, `variables/`, a signature you can name without opening the training script.

## Signatures, versions, and the boring server

A Serving model has a signature name. Clients call the name. You can have a `serving_default` and a `predict` and a training leftover you forgot to strip. Version directories let you roll forward and back. This is how a ranking model ships without a Python wheel on the server.

gRPC versus REST is a shop choice. The historical fact is that Serving existed as a C++ process while researchers were still arguing about sessions. The process is the 2015 white paper made operational.

SavedModel as a directory (protobuf + variables) is a crate. A raw checkpoint is not a crate. A lot of “we cannot productionize this” stories are a missing crate, not a missing kernel.

## Quantization as a phone fact

8-bit TFLite models in 2018–2019 were how a camera app ran a detector. Accuracy fights were real. So were APK size fights. The converter’s allowlist of ops was the fence. A research activation that was not in the allowlist died on the phone. That fence trained a generation of mobile ML engineers to think in subsets.

TFLite Micro’s subset is smaller still. A microcontroller net is a few dozen kilobytes and a C array. It is as far from a 405B GGUF as a nail is from a ship. Both are in the 2015 “devices” sentence.

## 2026 leftovers

LiteRT and on-device Gemma 4 (April 2026) are new nouns on an old instinct. A company that shipped TFLite does not have to relearn RAM. A company that only shipped APIs does. When you read a 2026 on-device blog, look for the converter. If there is no converter story, you are reading a demo.

The serving instinct also shows up in vLLM: a process that is not your notebook. The format changed. The wall did not.

## Frozen graphs and the archaeology of `.pb`

A frozen graph is a protobuf with weights baked in. It is older than SavedModel and still turns up in trees. The converter that ate it into TFLite may only exist in an old pip pin. Write the pin down. A 2026 engineer who has never heard of `freeze_graph` will need the note.

Signature defs that export the training softmax instead of the serving softmax are a class of production bug. The serving chapter’s job is to make you look at the signature name. Look at the signature name.

## Mobile as a constraint that taught subsets

Ops not in TFLite died. Activations not in the quant set died. Dynamic ranks died. Research that wants a phone deploy has to live in the subset from week one. Research that does not can ignore this chapter. Products that promised a phone and ignored this chapter shipped a cloud round-trip and called it on-device. The converter knows the difference.

## Sources

Abadi et al., 2015 white paper (heterogeneous devices). TensorFlow Serving documentation and 2016–2017 Google engineering posts. TensorFlow Lite converter guides; TFLite Micro announcements. TensorFlow.js 2018 launch posts on the TensorFlow Blog.

See: `tensorflow-november-2015`, `tensorflow-1-static-graphs`, `onnx-export-problem`, `llama-cpp-gguf`.
