---
id: "30"
slug: two-publics-api-and-weights
title: Two publics — API and weights
stage: 05-public-t2i
stage_title: Public text-to-image
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "OpenAI DALL·E 2 preview / API announcements (2022)"
  - "Stability AI SD public release (22 August 2022)"
  - "Midjourney as a subscription Discord product (public terms)"
  - "GLIDE filtered-release notes (precedent)"
does_not_claim:
  - "private traffic numbers"
  - "that one public is morally complete"
last_reviewed: 2026-09-14
---

# Two publics — API and weights

2022 had two publics that used the same words and did not live in the same city.

**City A** is the waitlist, the preview, the API, the Discord bot you pay for. You send a sentence. You receive pixels. You do not receive a tensor. Your ability to fork the model is zero. Your ability to screenshot is total. Safety can be a server-side yes/no. The lab can change the model under you and call it an improvement. DALL·E 2 lived here. Midjourney lived here. Imagen lived in a suburb of here that you could not even enter — a paper public, which is a third, thinner city.

**City B** is the checkpoint. You download a file. You are now the server. Safety is a license plus your conscience plus whatever filters you bother to install. You can fine-tune. You can strip. You can merge. You can be a teenager or a company. Stable Diffusion lived here. OpenCLIP lived here. A thousand unnamed merges lived here.

I am not going to pick a hometown. I am going to say that **a lot of arguments in this field are people in City A and City B pretending they share a civic government**.

When City A says “we released a model,” they often mean “we released an endpoint.” When City B says “open,” they often mean “I can `ls` the bytes.” When City A talks about safety, they mean a policy they can update on a Tuesday. When City B talks about safety, they mean a cat-and-mouse that they will lose. When City A talks about quality, they mean the best sample. When City B talks about quality, they mean the best sample *and* the existence of LoRA #4000.

CLIP itself was a weird dual citizen. Weights in B, data in a vault, a lab in A. That dual citizenship is why CLIP could become infrastructure for both cities. DALL·E 1 was almost purely a paper-and-blog citizen. GLIDE tried a gated B. The pattern is not a moral arc. It is a set of distribution choices that then produced different *kinds of history*.

City A’s history is screenshots, terms of service updates, and “we have improved prompt following.” It is easy to write and hard to footnote. City B’s history is commit hashes, model cards, and Civitai-style markets (a public, messy fact). It is easy to footnote and hard to make polite.

There is a third public I do not want to lose: **the rater public**. People paid to click which picture is better. Imagen’s tables. DALL·E’s tables. Academic user studies. They do not get the API and they do not get the weights. They get a pair of images and a question. A lot of “SOTA” is their Tuesday. I have no romance about this. I have a duty to remember that human preference is a labor market.

Why this split belongs between promptcraft and LAION: because folk practice diverged by city. City A folk practice is prompt plus subscription plus not making the content policy angry. City B folk practice is prompt plus checkpoint merge plus a face restoration plugin. If you study only one, you will think you understand 2022. You will understand a borough.

The later vision–language assistants repeat the split. GPT-4V is City A. LLaVA is City B. Gemini is A with a paper that talks like a researcher. The split is older than they are. It is August and April and January, repeating.

I will not write “and then open won” or “and then the APIs won.” As of the date on this draft, both cities are still populated. The interesting historical claim is smaller: **once you have two publics, you have two records, and a series like this has to read both without laundering one into the other.**

Next: the dataset that made City B possible at scale, and the fights that made “commons” a word you have to earn — LAION, CLIP-as-filter, safety, the circular gate.
