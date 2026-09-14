---
title: Ollama and the local box
slug: ollama-local-box
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 28
word_target: 600-1800
era: "2023–2026"
stack:
  - ollama
  - llamacpp
---

# Ollama and the local box

Ollama’s first tagged release, `v0.0.1`, is 8 July 2023. The GitHub author on that tag is Jeffrey Morgan (`jmorganca`). The notes call it an early preview. The Darwin arm64 binary is the artifact: a wrapper around the `llama.cpp` habit that had existed since 10 March (`llama-cpp-gguf`), shipped ten days before Llama 2 made a commercial-friendly base a thing you could fetch with a click (`llama-2-july-2023`). This chapter is about the box on the desk, not the cluster.

A week later the README had already found its sentence: create, run, and share self-contained packages; a `Modelfile` that looks enough like a Dockerfile that people wrote essays about it; `ollama run llama2` as the demo once Llama 2 existed. The engine underneath stayed Gerganov’s. The product was a name that resolved to a file, plus a local HTTP dialect that looked enough like OpenAI’s that a lot of tools could point at `localhost`.

## A name that resolves to a file

`ollama run llama3.1` is `from_pretrained` for people who do not want a venv. Under the hood: a GGUF, a runner, a prompt template. The value is the registry of names and the opinionated defaults — context, quant, chat template — so a designer and an engineer can share a sentence.

The cost is opacity. When a model “is bad,” you may be on a harsh quant, a short context, or a template that forgot the system prompt. Power users drop to `llama.cpp` or to raw GGUF on the Hub. Ollama’s job is to make that drop unnecessary for the first hour.

A Modelfile names the `FROM`, the template, the parameters. It is a recipe. Pin the from. If you do not, `llama3` becomes a moving noun. System prompts hidden in the recipe are how two users of “the same model” disagree. Print the recipe. Then argue.

By mid-August 2023 (`v0.0.15`) the project had a public library on ollama.ai, experimental `ADAPTER` lines in the Modelfile, and a note that some bundled models were research-only. The library of names is a second Hub (`hub-as-distribution`). A second registry is a second landlord. Do not assume `llama3` means Meta’s latest card.

## The OpenAI-shaped local API

A lot of 2024–2026 desktop tools speak one HTTP dialect. Ollama spoke it. That compatibility, more than any kernel, is why the wrapper stuck. Continue, Open WebUI, a pile of editor plugins — they needed a local endpoint. vLLM can be that endpoint (`vllm-paged-attention`). Ollama was the one that installed like an app.

When the schema drifts, tools break. That compatibility is a promise the project has to keep. The desk and the rack now speak a dialect that started as a closed API. The local box learned it.

The project’s license and the model licenses are different files. Mixing them is the usual card error. Ollama MIT-or-whatever on the daemon does not wash Llama’s community PDF inside the GGUF.

## What Ollama is not

It is not a trainer. It is not a license. It is not faster than a tuned vLLM on a full GPU for concurrent users — Red Hat’s public notes and a hundred blog benches agree on the direction of that comparison, if not on the exact ratio. It is not “the open-source AI.” It is a runner.

If you need a specific quant, a specific rope scale, or a server queue, put the wrapper down. `llama.cpp` and vLLM are the floor. Ollama is the first hour and the designer’s hour. Both hours are real. They are not the same hour.

`ollama pull` is `from_pretrained` with a different landlord. The name `llama3.2` may lag Meta’s card. The quant may not be the one you would pick. If the work matters, pull the GGUF yourself and write a Modelfile that `FROM`s a local path. The library of names is for the first hour. The local path is for the pin.

## 2026 look

Monthly-download folklore will age. The box will not: a developer machine with a local endpoint and a GGUF cache is now an ordinary workstation, the way a Docker daemon became ordinary. Ollama is one daemon. LM Studio is another. `llama-cli` is the bare one. MLX is the Apple-shaped Python path (`mlx-apple-silicon`).

If you want objects: the 8 July 2023 tag, a Modelfile, the current README, and the `llama.cpp` chapter next door. Product landing pages will say “easy.” The Modelfile will say which quant you actually ran.

## Sources

ollama/ollama `v0.0.1`, 8 July 2023 (Jeffrey Morgan). ollama/ollama `v0.0.15` library notes, August 2023. Ollama Modelfile documentation. ggerganov/llama.cpp (underlying engine). Red Hat Developer comparisons, 2025–2026.

See: `llama-cpp-gguf`, `vllm-paged-attention`, `llama-3-april-2024`, `hub-as-distribution`.
