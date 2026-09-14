---
title: A chatbot company that kept the library
slug: huggingface-from-chatbot
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 16
word_target: 600-1800
era: "2016–2020"
stack:
  - huggingface
---

# A chatbot company that kept the library

Hugging Face, founded in 2016 by Clément Delangue, Julien Chaumont, and — as the technical public face — Thomas Wolf, began as a consumer product: a chatbot aimed at teenagers, a brand that looked like a startup, not like a model zoo. The product did not become the stack. The library they wrote to support language models did. That accident is the company’s historical luck and its business model.

This chapter stays with the public record: the company existed before Transformers; Transformers existed before the Hub was a social network; the Hub then became the reason people said the company name when they meant a URL.

## From app to infrastructure

A chatbot in 2016–2017 lived in the shadow of whatever sequence model you could actually run. The team’s later writing (including the Transformers paper, arXiv:1910.03771) says the library started as internal tools. That is an ordinary sentence. Lots of companies have internal tools. Few of them become `pip install transformers`.

The decision to open-source the BERT port in November 2018 (`transformers-library-2018`) is the hinge. Google had released BERT weights. A clean PyTorch implementation with `from_pretrained` was the missing object. Hugging Face shipped it. The field copied it. The company followed the users.

Delangue’s later public role is CEO of a model platform. Wolf’s is the engineer whose name is on the early tags. Chaumont is less quoted in English-language press and still belongs on the founding line. A history that turns the company into one founder is doing magazine work.

## Why a startup could become the zoo

Google and Facebook already had hubs. TensorFlow Hub and PyTorch Hub were real. They were also institutional: a blessed list, a research accent, a weak social layer. Hugging Face built the thing GitHub would have built if GitHub had cared about tensors — cards, likes, organizations, a CDN, a culture of forking a model the way you fork a repo.

The company remained a company. It raised money. It sold compute and enterprise Hub. Those facts are public and ordinary. They do not cancel the Apache 2.0 library. They do mean the Hub is not a commons with no landlord. A later chapter treats the Hub as a distribution system (`hub-as-distribution`). This one only needs the landlord’s origin: a chatbot shop that noticed the library was the product.

## The name as a verb

By 2021 people said “it’s on Hugging Face” the way they said “it’s on GitHub.” That lexical win is rarer than a good README. It is also a single point of failure. When the Hub is down, a lot of “open” workflows are down. When a card is gated, a lot of “open” workflows have a click. The company’s success is the field’s dependency.

BigScience (`bloom-and-bigscience`) later used the Hub as a collaboration surface. That only works if the surface already exists. 2016’s chatbot company, by 2022, was infrastructure for a multilingual research collaboration it did not invent.

## 2026 look

The consumer app is a trivia question. The org `huggingface` on GitHub is a shelf: Transformers, Datasets, Tokenizers, Accelerate, Diffusers, PEFT, TRL, Hub, `safetensors`, TGI. Some of those are later chapters. The through-line is a company that kept shipping libraries under Apache 2.0 while making the website the place the files lived.

If you want objects: the 2018 `v0.1.2` tag, the 2019/2020 Transformers paper, and the company’s own about pages as primary-source claims (treat marketing as marketing). Wikipedia’s page on the Transformers library is a secondary pointer, not a citation of record.

No private mesh. No unpublished stack. The chatbot became a URL. The URL became the crate store. The crate store is why the rest of this series has a place to point when it says “the card.”

## Money, compute, and the landlord problem

The company sold inference, enterprise Hub, and later training compute. Those products are public. They do not make the Apache libraries less Apache. They do make the website a business. A business can change pricing, rate limits, and terms. A shop that treats huggingface.co as a public utility will meet a bill or a cap.

Spaces as a product trained users to expect a running demo. Demos are not archives. A Space that goes to sleep is not a paper appendix.

## The GitHub org as a shelf list

Transformers, Datasets, Tokenizers, Accelerate, Diffusers, PEFT, TRL, Hub, safetensors, text-generation-inference, candle, smolagents — the list will grow after this pack is staged. The 2016 chatbot company became a holding company for the verbs the field needed: load, tokenize, train a little, serve a little, demo. That is a coherent business even if you dislike businesses.

Thomas Wolf’s early tags and the 2019 paper are the engineering origin. Delangue’s interviews are the company origin. Use both. Do not use only one.

## What “kept the library” means

They could have closed the source when the Hub made money. They did not, on the core libraries, as of this pack’s date. That fact can change. The series records the files as they are: Apache 2.0 repos and a proprietary website next to them. The next chapter is the 35-kilobyte wheel that made the website necessary.

## The website as a verb the field cannot easily replace

`huggingface.co/org/name` is a citation format. Replacing it means replacing a generation of papers’ footnotes. That is landlord power. It is also why mirrors and `git clone` of a model repo matter. A field that can only cite one website is a field that should keep local copies.

The 2016 chatbot is trivia. The citation format is not. This chapter exists so the trivia does not hide the landlord.

## Sources

Wolf et al., arXiv:1910.03771 (library origin as internal tools; name changes). huggingface/transformers `v0.1.2`. Hugging Face company about / blog posts on the Hub’s growth (public). GitHub org file list as of the series date.

See: `transformers-library-2018`, `hub-as-distribution`, `bloom-and-bigscience`, `datasets-tokenizers-accelerate`.
