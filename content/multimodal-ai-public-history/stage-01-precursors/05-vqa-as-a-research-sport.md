---
id: "05"
slug: vqa-as-a-research-sport
title: Visual question answering as a research sport
stage: 01-precursors
stage_title: Precursors (before the 2021 hinge)
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Antol et al., VQA, ICCV 2015"
  - "Goyal et al., Making the V in VQA Matter, CVPR 2017 (VQA v2)"
  - "Later public sets: GQA, VizWiz, TextVQA, OK-VQA (as named public benchmarks)"
does_not_claim:
  - "a complete catalog of VQA datasets"
  - "unpublished prior-hacking methods"
last_reviewed: 2026-09-14
---

# Visual question answering as a research sport

If captioning was a literary form, VQA was a sport. Someone asks a question about a picture. The model answers in a word or a short phrase. There is a leaderboard. There is a test server. There is a paper every season that wins by a point and a new fusion module.

Antol et al. put the modern version on the table in 2015. The demo was easy to like. *What color is the fire hydrant?* *How many dogs?* *Is it raining?* A child could play. A model that could play looked, to outsiders, like it could see and think. That was the hook. It was also the trap.

The trap had a name by 2016 and a dataset revision by 2017. Models were learning the *question*, not the picture. Bananas are yellow, so “what color is the banana?” does not require a banana. “How many” likes the number two. “Is there a clock?” likes yes in rooms that look expensive. Goyal et al. made the V in VQA matter by balancing complementary images: same question, different answer, so the language prior could not coast. The sport got harder. The sport did not get honest about what an answer is.

Because an answer, in VQA, is usually a classification. The decoder is not writing a paragraph. It is picking from a head of common answers. That design choice made evaluation possible. It also made the task look more like ImageNet than like conversation. The multimodal joint was often late fusion: a picture vector, a question vector, some attention, a softmax. Plenty of cleverness lived in that sandwich. Not much of it was “understanding.”

I do not say that with contempt. Sports produce scars that later work wears as wisdom. The banana-yellow paper is a public lesson that a language model (even a small one) will exploit a prior if you let it. Every vision–language assistant still does this. Ask a looking chatbot a leading question and you can watch the prior sit up. The 2017 correction is the ancestor of every later paper that says, in polite language, we checked that the model needed the image.

The sport also splintered, which is a sign it was real.

- **Compositional** sets (GQA and friends) tried to force relations: the chair *to the left of* the table, not just chair and table.
- **Text in the image** (TextVQA and the OCR line) admitted that a lot of questions are reading, not seeing. Screenshots and signs are language hiding in pixels. This is the leftover channel from draft 01.
- **VizWiz** brought questions from blind and low-vision photographers. The pictures are blurry, the questions are practical, the “unanswerable” label is a moral fact. A sport that only used COCO interiors was a sport for people who had never needed a model.
- **OK-VQA** and later knowledge sets asked for facts that are not in the pixels. What year is this car. Which mountain. The joint now includes a memory, or a retrieval, or a hallucination.

By the time LLaVA and GPT-4V show up, VQA is no longer the product. It is a *benchmark the product has to survive*. That inversion is typical. The sport defines the exam. The assistant treats the exam as one of the things it can do in a chat. Sometimes it still answers like a softmax: short, confident, banana-yellow. Sometimes it writes a paragraph and you cannot tell which sentence used the image.

There is a human texture to VQA that I do not want to sand off. The questions in the original sets were written by people looking at pictures on a screen, paid to be curious. Curiosity, under payment, becomes a style: slightly quizlike, slightly tourist. “What is the man doing?” A real person holding a real photograph asks different things. “Is this the same rash as Tuesday.” “Can I park here.” “Does this look like the part we need.” The product era will meet those questions and discover that the sport only trained the quiz.

So I keep VQA in the precursor stage as a warning and as a debt. Warning: language priors wear the costume of seeing. Debt: without those leaderboards, the later assistants would have had nothing public to fail at. A model that can describe a snowboard and cannot say how many people are on it is not done. A model that can say how many and cannot read the sign behind them is not done either.

The next draft steps back from the sport to a quieter paper that was already trying to throw away the softmax: DeViSE, and the first serious public attempt to put pictures in a word space.
