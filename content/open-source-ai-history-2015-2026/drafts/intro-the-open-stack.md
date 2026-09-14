---
title: The open stack, eleven years on
slug: intro-the-open-stack
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 1
word_target: 600-1800
era: "2015–2026"
stack:
  - tensorflow
  - pytorch
  - huggingface
  - llama
---

# The open stack, eleven years on

On 17 November 2018, Thomas Wolf tagged `v0.1.2` on what was then called `pytorch_pretrained_bert`. The wheel was 35.6 kilobytes. It loaded Google’s BERT checkpoints from an S3 bucket under `models.huggingface.co` and cached the tar.gz on disk. That is a small object. It is also a fair place to start a history that people keep telling as if it began with ChatGPT, or with a 405-billion-parameter dump, or with a slogan about “open source AI.” The stack that a laptop in 2026 actually runs — a PyTorch graph or a GGUF file, a tokenizer JSON, a Hub card, a license you did or did not read — was assembled in public, in pieces, over eleven years, by labs that did not share a plan.

![Milestone years in the public open stack, 2015 through 2026.](../assets/timeline/2015-2026.svg)

*Figure 1. Milestone years in the public open stack, from TensorFlow’s 2015 release through DeepSeek-R1, gpt-oss, and Llama 4. Dates are first-party announcements named in the bibliography.*

![Four public layers: framework, hub, weights, and the engine you run.](../assets/four-stacks/layers.svg)

*Figure 2. Four layers, not one product. A shop in 2026 mixes them. The license on one layer does not cover the others.*

## Four layers, four clocks

Call the first layer the **framework**. Google open-sourced TensorFlow on 9 November 2015 under Apache 2.0, as a successor to the internal DistBelief system the 2015 white paper still describes. Facebook’s PyTorch alphas landed in 2016; a release note on `v0.1.6` later dated the public release to 18 January 2016. Those two libraries, plus Theano before them and JAX beside them, are what “training code” meant for a decade. They are also what a lot of people still mean, wrongly, when they say a language model is open source. A model is not a framework. A framework’s Apache license does not travel into a weight file.

The second layer is the **hub**. Hugging Face began as a consumer chatbot company in 2016. The library that mattered was the 2018 wheel, then `pytorch-transformers`, then Transformers (Wolf et al., arXiv:1910.03771). The Hub became a distribution system: cards, gated clicks, `safetensors`, later GGUF mirrors. TensorFlow Hub and PyTorch Hub existed. They did not become the place people looked first.

The third layer is **weights**. Meta’s LLaMA paper (arXiv:2302.13971) and blog post of 24 February 2023 offered 7B, 13B, 33B, and 65B checkpoints to approved researchers under a non-commercial license. A torrent of those weights was posted on 4chan on 3 March 2023; The Verge reported the leak on the 8th. That accident, more than Meta’s form, is why a generation of fine-tunes and C++ runners exist. Llama 2 (18 July 2023) put a community license on commercial use with conditions. Llama 3 (18 April 2024) and Llama 3.1 405B (23 July 2024) made “open weights at frontier size” a sentence you could say without smirking. Llama 4 Scout and Maverick (5 April 2025) arrived as natively multimodal mixture-of-experts models; Behemoth was previewed and, as of September 2026, has no public weights. Around that clock, Mistral, Qwen, DeepSeek, Gemma, Phi, and — on 5 August 2025 — OpenAI’s `gpt-oss` line shipped their own files.

The fourth layer is **how you run it**. Georgi Gerganov’s `llama.cpp` (March 2023) and the GGUF format (August 2023) made a quantized file a thing you could copy to a USB drive. Ollama wrapped that for people who did not want a compiler. vLLM (Kwon et al., SOSP 2023) treated the KV cache like a pager and made a GPU serve many requests. Apple’s MLX (December 2023) did the same job on a different silicon story. None of these are Meta. None of them are Google. They are why “I downloaded Llama” and “I run Llama” stopped being the same sentence.

## What this series is not

It is not a history of artificial intelligence. It does not start in 1956, and it does not spend a chapter on ImageNet except where a framework paper names it. It is not a history of closed APIs, except where those APIs are the thing an open release is answering (GPT-3.5 for Alpaca; o1 for DeepSeek-R1; Gemini for Gemma). It is not a leaderboard. Vendor phrases such as “most capable” are quoted and dated when they appeared; they are not this narrator’s ranking.

It is not a history of any private operating system, any mesh, or any unpublished stack. Public artifacts only. If a fact is traditional shop knowledge and not pinned, it is marked `[CITE NEEDED]`.

It is also not a compliment. “Open source” is a license test. The Open Source Initiative’s definition is older than TensorFlow. A file you can download is **open weight**. A file under Apache 2.0 or MIT, without field-of-use bans, is closer to what that definition meant. A Llama Community License with an acceptable-use policy and a user-count threshold is a different instrument. Meta called Llama 2 and Llama 3 “open source” in blog posts; by Llama 4 the company preferred “open-weight.” That shift is one of the few honest edits in the marketing.

## How a shop actually uses the clock

If you train, you still live in PyTorch for most new papers, with JAX in a smaller, sharper set of Google-adjacent and scientific shops, and with `tf.keras` / Keras 3 still present where a production graph or a teaching notebook never moved. Keras 3 (late 2023) made the high-level API a frontend over TensorFlow, JAX, or PyTorch. That sentence would have sounded like science fiction in 2016, when the argument was whether a static graph was a grown-up choice.

If you fine-tune a language model, you live on the Hub: a base card, a PEFT adapter, a `tokenizer.json`, sometimes a gated click that records that you accepted a community license. LoRA (Hu et al., 2021) and QLoRA (Dettmers et al., 2023) are why a weekend box can write a derivative without storing a second full copy of the base.

If you serve, you pick an engine the way a mill picks a saw. `llama.cpp` is the portable file. vLLM is the concurrent GPU. A cloud listing of the same weights is a third choice and a different trust story.

If you only call an API, you are not in this series except as context. That is not an insult. It is a boundary. The thing this history can see is the artifact a stranger can fetch.

## A note on people and orgs

Jeff Dean’s name is on the 2015 TensorFlow story because DistBelief and the white paper put it there. Soumith Chintala’s name is on the PyTorch story because the release tags and the Foundation notes put it there. Clément Delangue, Julien Chaumont, and Thomas Wolf are the Hugging Face names the public record keeps repeating; the library commits are a longer list. Hugo Touvron’s name is first on the LLaMA paper. Gerganov’s name is on the C++ runner that made the leak useful on a machine you already owned. None of these people “invented open source AI.” They shipped objects other people could fork.

Google, Meta (Facebook), Hugging Face, Mistral, Alibaba Cloud, DeepSeek, Microsoft Research, and OpenAI are companies. The Linux Foundation is a trade association that took PyTorch’s governance in 2022. BigScience was a collaboration that trained BLOOM. Stanford CRFM published Alpaca and withheld weights pending Meta’s permission. Those are different kinds of author. The drafts that follow keep the kind visible.

## How to walk the house

Start with the framework you already import, or walk the English-language clock: TensorFlow’s 2015 release, PyTorch’s eager bet, the 2018 wheel, the 2023 leak, the 2024–2026 weight dump that made “open” a market position. Figure 1 is the corridor. Figure 2 is the rooms.

Then read a license the way you would read a crate label. Apache 2.0 on `tensorflow/tensorflow` does not license `meta-llama/Llama-3.1-405B-Instruct`. MIT on DeepSeek-R1 does not license the data it was trained on. A Gemma 1–3 Terms of Use file is not the Apache 2.0 file Gemma 4 shipped on 2 April 2026. The last two chapters of this series exist so the earlier ones have a standard.

Open a terminal wherever you are. `import torch` and `from transformers import AutoModel` and `llama-cli -m something.gguf` are three different centuries stacked in one prompt. The useful question is still the shop question: what did this file let you do, who had to approve it, and what happens when the card changes.

Macquoid, if he had been a systems person, would have given you four timber ages. This house has more rooms than a framework war.

## A note on what “public” excludes

If a fact lives only in a private Slack, a vendor NDA, or an unpublished cluster log, it is not in this pack. Download counts that appear only on a keynote slide are vendor claims; quote them as such or omit them. Star counts that are not dated to a first-party page get the same treatment. The series would rather be thin than inventive.

The four layers leak into each other — a Hub card names a library, a GGUF names a base, a trainer names a license it did not ship — but the leak is not a reason to use one adjective for the pile. Keep the layer. Keep the date. Keep the file.

## Sources

Google Research TensorFlow announcement, 9 November 2015; TensorFlow white paper, 2015. PyTorch `v0.1.6` release notes (public release dated 18 January 2016); Paszke et al., NeurIPS 2019. Hugging Face `transformers` `v0.1.2`, 17 November 2018; Wolf et al., arXiv:1910.03771. Meta, “Introducing LLaMA,” 24 February 2023; Touvron et al., arXiv:2302.13971; The Verge, 8 March 2023. Meta Llama 2 (18 July 2023), Llama 3 (18 April 2024), Llama 3.1 (23 July 2024), Llama 4 (5 April 2025). Linux Foundation PyTorch Foundation, 12 September 2022. Kwon et al., SOSP 2023. OpenAI, “Introducing gpt-oss,” 5 August 2025. Google, Gemma 4, 2 April 2026.

See: `before-tensorflow-theano-torch-caffe`, `transformers-library-2018`, `llama-february-2023`, `open-weight-vs-open-source`, `twenty-twenty-six-the-stack`.
