---
id: "35"
slug: flamingo-few-shot-not-chat
title: Flamingo — few-shot, not chat
stage: 07-vision-language-assistants
stage_title: Vision–language assistants
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Alayrac et al., Flamingo: a Visual Language Model for Few-Shot Learning, arXiv:2204.14198"
  - "DeepMind blog, 28 April 2022"
does_not_claim:
  - "unpublished Flamingo weights"
  - "that Flamingo is a product chatbot"
last_reviewed: 2026-09-14
---

# Flamingo — few-shot, not chat

April 28, 2022. DeepMind’s blog and a preprint: a visual language model that you adapt by **showing it a few examples in the prompt**, the way you had learned to adapt a large language model. Interleaved images (and video) and text in. Text out. An 80B-class object in the public telling, built on a frozen Chinchilla-like language model and a frozen vision encoder, with new pieces in the middle. No consumer chat. No “try it.” A paper public.

I care about Flamingo more than the 2022 picture models, if I am allowed a prejudice, because it states the **other job** cleanly. Not “make me a picture.” *Talk about pictures you have just been shown, with almost no training for the task.* That is closer to what a person does with a new album than FID is.

The public architecture is a small essay in joints.

The vision side is pretrained and **frozen**. The language side is pretrained and **frozen**. What you train is the glue: a **Perceiver resampler** that turns a variable pile of visual features into a fixed set of tokens, and **gated cross-attention** layers inserted into the LLM so those tokens can be glanced at without, in their telling, wrecking the language model’s brain. Freeze-both-plus-glue is a template. BLIP-2 will make a cheaper glue. LLaVA will make a cheaper glue still, sometimes just a linear map. The template is Flamingo’s even when the later papers are ruder.

Few-shot is the evaluation religion. Not because DeepMind was allergic to fine-tuning, but because the claim is *generality*: one model, many multimodal tasks, a handful of in-context examples. Captioning, VQA, yes/no, the old sport in a new harness. The banana-yellow problem does not vanish. A frozen LLM has priors. The image is a guest in a house that already talks. Sometimes the guest is heard. Sometimes the house finishes the sentence it was always going to finish.

I want the “not chat” in the title to do work. Chat is a product genre: a user, a turn-taking UI, safety stacked on the outside, a personality. Flamingo is a **prompted sequence model**. You can make a chat out of a prompted sequence model. They did not ship that. If you write the history as “then we got multimodal ChatGPT,” you will treat Flamingo as a prototype of a product. It was a prototype of a *capability*, and the capability is in-context visual learning. Those are different descendants. GPT-4V is a product descendant. A lot of academic VLMs are capability descendants. LLaVA is both, which is why it spread.

Interleaving is the other public gift. Not one image and a question, but a strip of images and words, like a comic or a thread. That interface is the true multimodal object of the assistant era. Screenshots, memes, “this then this.” Flamingo’s paper understands the strip. 2015 VQA mostly did not.

No weights. Again. DeepMind’s 2022 is Imagen-adjacent in distribution even when the method is not. The influence is citations and diagrams. The first time a lot of practitioners *touched* a Flamingo-like object, it was an open clone or a smaller cousin, a year later. Influence without a file is real. It is just slower in City B.

A sentence I keep: **the interesting 2022 was not only pictures coming out. It was pictures going in, and a language model not dying.** The gated xattn is the “not dying.” Later people will drop the gate and sometimes the language model will get a little dumber about punctuation, a little smarter about posters. The trade is the literature.

Next: the cheap-glue school in the open — BLIP, BLIP-2, a Q-Former, bootstrapped captions — the academic path that did not need an 80B frozen bird.
