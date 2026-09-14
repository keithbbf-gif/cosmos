---
id: "08"
slug: transformers-eat-both-modalities
title: Transformers eat both modalities
stage: 01-precursors
stage_title: Precursors (before the 2021 hinge)
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Devlin et al., BERT, NAACL 2019 (arXiv 2018)"
  - "Radford et al., GPT / GPT-2 public reports"
  - "Dosovitskiy et al., An Image is Worth 16x16 Words, ICLR 2021"
  - "Touvron et al., DeiT, 2021 (data-efficient ViT neighbor)"
does_not_claim:
  - "that transformers are the only multimodal path"
  - "undisclosed tokenizer internals"
last_reviewed: 2026-09-14
---

# Transformers eat both modalities

There is a story that says multimodal AI happened because transformers ate everything. It is not false. It is incomplete, and it is a little vain — as if a block diagram could want lunch.

What actually happened in public is smaller. A language stack became default. Then a vision paper showed that the same stack, given patch tokens and enough data, could classify pictures without a convolutional backbone. Then a handful of labs put both stacks in one diagram and trained a joint. The eating was opportunistic. The hunger was engineering rhyme: shared code, shared optimizers, shared people who already knew how to scale a transformer.

BERT is the language-side monument I want on the table, not because CLIP is a BERT (it isn’t, not exactly), but because BERT made *pretrain then adapt* the water people swam in. Bidirectional, masked, a [CLS] token that became a handle. A generation of NLP papers were adapters on a frozen or lightly tuned BERT. When vision–language papers in 2019–2020 say “we concatenate region features and wordpieces and run a transformer,” they are speaking that water. VisualBERT, ViLBERT, LXMERT, UNITER — I will not pretend this draft is a census — are public evidence that the joint, for a while, looked like *early fusion inside a BERT*.

That line is easy to lose because CLIP abandoned it for something ruder and cheaper: two towers, contrastive loss, no region detector required in the version people actually used. The BERT-fusion line wanted object features, often from a Faster R-CNN, which meant your multimodal model inherited a detector’s idea of an object. CLIP wanted a crop and a string. History, in public, rewarded the rude version. That does not make the BERT-fusion papers a dead end. They are the other way to build a joint: one sequence, two vocabularies, a lot of attention among neighbors. Flamingo will look more like that family than like CLIP, even when it uses a CLIP-like vision encoder.

GPT’s public lesson was different. Autoregressive, left-to-right, a model that can be prompted. Zero-shot as a *behavior*, not just a metric. CLIP’s authors, several of whom had lived in that lineage, say out loud that they wanted a vision analog of that behavior. You do not fine-tune a classifier head. You write a sentence. The transformer-eats-everything story is, on that telling, a story about **interfaces**. The interface of a GPT is text. The interface of a CLIP is also text. The interface of a 2015 softmax is an integer.

ViT’s public dare is the one civilians still underestimate. An image is 16×16 words. Linear-embed the patches. Add position embeddings. Train big. The paper is careful: this works when the data is big enough; convolution’s bias is a gift when it is not. DeiT and the follow-on literature spent a year making the dare cheaper. By the time Stable Diffusion needs an image encoder/decoder, and by the time a LLaVA needs a visual tower, ViT-shaped things are just *the* way a picture enters a transformer world.

I want to separate three unifications that get talked about as one:

1. **Unification of block.** Same layer code for pixels and words. True-ish, with asterisks for UNets, resamplers, and convolutional VAEs.
2. **Unification of objective.** Not true. Masked language modeling, next-token prediction, contrastive pairing, denoising score matching — these are different jobs that happened to like the same block.
3. **Unification of meaning.** Not even a research claim I would sign. A patch token is not a wordpiece. Sharing a block does not share a semantics. It shares a gradient highway.

A lot of later “natively multimodal” language is (3) wearing (1)’s clothes. I will get to Gemini’s public claim in stage 07. Here I only want the habit flagged. When a lab says the model was multimodal from the start, ask whether they mean the *data* was mixed, the *block* was shared, or the *loss* was one. Those are three histories.

The precursor stage ends here on purpose. By 2020 the field has: a joint-space instinct (DeViSE), a speaking-about-images instinct (captions, VQA), a routing algebra (attention), and a block that will take any token you feed it. What it does not yet have, in public, is a cheap web-scale pair dataset plus a contrastive recipe that makes the joint space a *default tool*. That is the next stage. It starts with a smaller fact: contrastive learning was already working on pictures alone, with two crops instead of a sentence.
