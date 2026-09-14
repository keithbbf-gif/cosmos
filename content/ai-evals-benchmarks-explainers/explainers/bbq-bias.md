---
voice_check: edited
title: "BBQ: bias as a question, not a vibe"
slug: bbq-bias
kind: explainer
era: 2022
tags: [bbq, bias, parrish, qa]
portrait: null
portrait_status: none
---

Alicia Parrish, Angelica Chen, Nikita Nangia, Vishakh Padmakumar, Jason Phang, Jana Thompson, Phu Mon Htut, and Samuel Bowman published “BBQ: A Hand-Built Bias Benchmark for Question Answering” in Findings of ACL 2022. NYU. The name is Bias Benchmark for QA. The hardship is a question whose answer, if you are doing your job, sometimes has to be “not enough information,” and whose answer, if you are echoing a stereotype, will name a group.

The authors wrote the items by hand. That is in the title. Hand-built is slow and is the reason the set can target a stereotype on purpose instead of hoping a crawl produces one.

## Ambiguous and disambiguated

Each scenario comes in at least two weathers.

In the **ambiguous** version, the context does not tell you who did the thing. A fair system abstains or refuses the forced choice. A biased system picks the group that the stereotype wants.

In the **disambiguated** version, the context states the answer. A fair system follows the context even when the context breaks the stereotype. A system that still follows the stereotype has a worse problem than a guess: it is ignoring the sentence in front of it.

The split is the instrument. A single “bias score” that erases it is a vibe. Parrish’s group reports accuracy and a bias metric that depends on whether the context was sufficient. Read both.

## What categories they named

The paper targets U.S.-centric social dimensions: race/ethnicity, gender, age, religion, disability, socioeconomic status, nationality, sexual orientation, physical appearance, and related slices the authors list in the tables. The items are English and culturally located. A stereotype that is loud in another country may not appear. A stereotype that is loud in the U.S. training data will.

This is not a global census of harm. It is a public, inspectable set of traps for a particular society’s models.

## An item in the hand

A short context about two people, named only by group or by a stereotyped occupation. A question: who was the bad driver, who got the job, who caused the noise? In the ambiguous version, the paragraph does not say. The gold is to refuse the frame or to pick “can’t be determined,” depending on the item’s options. In the disambiguated version, the paragraph says the opposite of the stereotype. The gold is to follow the paragraph.

A system that is “fair” only when the context already forbids the stereotype is not fair. It is obedient to sentences and biased in the fog. Parrish’s split exists to catch that pattern. Compressing the split into one “bias ↓” arrow is how a card lies without inventing a number.

The items are blunt. They are supposed to be. Subtle workplace harm will not all fit in a four-choice QA file. Use BBQ for the blunt trap. Use something else for the rest.

## What BBQ will not do

It will not certify that a model is safe to deploy. It will not measure toxicity of free generations (see RealToxicityPrompts). It will not measure whether a model will assist a crime. It will not replace a red-team. It will tell you, on these hand-built QA items, whether the system fills in a stereotype when the paragraph does not.

Multiple-choice QA is also a soft form of the problem. A chatbot in the wild can volunteer a stereotype without being asked to pick (A) or (B). BBQ is a microscope, not a sky survey.

## How it sits next to CrowS-Pairs and StereoSet

Those earlier files (Nangia et al.; Nadeem et al.) compare sentence pairs and ask which one the model finds more likely. BBQ asks a question. Different cheap judge, overlapping worry. If you cite only one, say why.

Bowman’s name on BBQ, GLUE, SuperGLUE, and GPQA is a reminder that the same lab culture can build a capability suite and a bias suite. They are not moral opposites. They are different hardships. A card that reports MMLU and not BBQ is choosing the exam. A card that reports BBQ and calls the model “aligned” is choosing a word the file does not support.

## How to read a BBQ line

Report ambiguous versus disambiguated, the bias metric the paper defines, and the category breakdown. A single headline “we reduced bias by 30%” without the split is an advertisement. The hand-built questions are still there. They still have a right refusal. Use it.
