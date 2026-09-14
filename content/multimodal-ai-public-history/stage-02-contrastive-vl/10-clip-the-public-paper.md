---
id: "10"
slug: clip-the-public-paper
title: CLIP, the public paper
stage: 02-contrastive-vl
stage_title: Contrastive vision–language
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "OpenAI CLIP blog, 5 January 2021"
  - "Radford et al., Learning Transferable Visual Models From Natural Language Supervision, arXiv:2103.00020, ICML 2021"
  - "openai/CLIP GitHub repository and model card"
does_not_claim:
  - "unpublished WIT scrape details"
  - "internal ablations not in the paper"
last_reviewed: 2026-09-14
---

# CLIP, the public paper

On January 5, 2021, OpenAI published a blog post about connecting text and images. The same day they published a blog post about DALL·E. That pairing is already a historical fact: the lab presented a retriever and a generator as twins. This draft is only about the retriever. The generator gets its own room later, and it is not a diffusion model.

The paper that followed — *Learning Transferable Visual Models From Natural Language Supervision* — is the object I want to treat as a primary source. Blog posts sell. Papers constrain. A public history should prefer the constraints.

Here is what the paper, in public, actually commits to.

**Two encoders.** An image encoder (ResNet family or ViT family, in the released line). A text encoder (a Transformer). Each side emits a vector. The vectors are compared with a cosine, scaled by a learned temperature.

**A contrastive objective.** In a batch of N pairs, you want the N correct pairings to score high and the N² − N incorrect pairings to score low. That is a symmetric retrieval problem. Image-to-text and text-to-image. No decoder writes a caption. No softmax names an ImageNet class during pretraining.

**Natural language as the supervision.** The pairing is an image and a text that *occurred with it*. The paper describes a dataset of 400 million pairs collected from the internet, which they call WIT in the paper’s dialect — WebImageText — and which is **not** released. I will not pretend we have the scrape. We have the number, the description, and the downstream behavior.

**Zero-shot transfer as the headline evaluation.** Instead of attaching a new linear head for each dataset, they turn class names into sentences (“a photo of a {label}”) and ask which sentence the image matches. They report, among other things, that this can match a fully supervised ResNet-50 on ImageNet. That sentence is the one that traveled.

**Prompting and ensembling as part of the method.** This is easy to skip and I will not skip it. The paper does not only embed the raw class name. It embeds templates. It ensembles. The interface *is* the classifier. That is a cultural fact as much as a technical one. A lot of the “CLIP is robust” conversation is secretly a conversation about prompts.

**A released artifact.** Unlike DALL·E 1, CLIP came with code and weights you could actually run. The GitHub repository, the model card, the Colab — those are part of the public object. A paper without a weight is a claim. A paper with a weight is a tool. CLIP was a tool.

What the paper does not give you, if you are honest:

It does not give you the URL list. It does not give you a full accounting of whose photos those were. It does not give you a guarantee that “natural language supervision” means captions in the COCO sense; it means text that co-occurred, which includes junk. The model card is more careful than the first wave of tweets. A historian should be too.

It does not give you a generator. People immediately *used* CLIP as if it were one — optimizing images to score high against a prompt, ranking samples from other generators, steering GANs. That is reception history. It is not in the methods section. I will write that reception in draft 15.

It does not give you a chatbot. There is no instruction tuning. There is no “in this image, explain.” If you want words out, you have to bring your own decoder or your own nearest-neighbor sentences. The public repeatedly forgot this and then rediscovered it every time a CLIP demo looked like it was talking.

I read the paper, years later, as a study in **refusing work**. Refuse the closed softmax. Refuse the detector-first BERT fusion. Refuse the caption decoder. Keep the pair, the batch, the prompt. The refusal is why it transferred. Models that do less during pretraining sometimes do more afterward, if the less is the right less.

A note on authors and priority, because novelty-safe means I do not play inventor. The author list is public on the arXiv page. The debts are public in the related-work section. ConVIRT, VirTex, the GPT zero-shot instinct, the contrastive vision papers — they are named. CLIP is a synthesis at a scale that made synthesis look like a break. Synthesis at that scale is still a historical event. It is not a virgin birth.

If you only have time to read one primary document in this whole series, read this paper’s evaluation section and the blog’s examples, then the model card’s limitations. The examples made people want it. The limitations are the part that aged well.
