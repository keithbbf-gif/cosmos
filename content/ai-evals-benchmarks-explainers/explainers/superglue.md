---
voice_check: edited
title: "SuperGLUE: the sequel that admitted the first test got easy"
slug: superglue
kind: explainer
era: 2019
tags: [superglue, glue, nlu]
portrait: null
portrait_status: none
---

Sequels in evaluation are usually a confession. SuperGLUE is a polite one. Alex Wang, Yada Pruksachatkun, Nikita Nangia, Amanpreet Singh, Julian Michael, Felix Hill, Omer Levy, and Samuel Bowman published “SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems” at NeurIPS 2019. The title’s adjective is doing work. GLUE had become un-sticky. Models were climbing. The average was losing its ability to hurt.

The authors did not throw GLUE away. They built a smaller, meaner English suite with the same social contract: hidden test labels, a public leaderboard, a single headline number, and a hope that linguistic hardship would return.

## Fewer tasks, more stubborn ones

SuperGLUE’s core tasks, as the paper specifies them, include:

- **BoolQ** — Clark et al.’s yes/no questions, the kind a person actually types, paired with a Wikipedia passage.
- **CB** — CommitmentBank, a small, nasty inference set about what a speaker has committed to.
- **COPA** — Roemmele, Bejan, and Gordon’s Choice of Plausible Alternatives: a premise and two causal tails. Common sense as a fork in the road.
- **MultiRC** — Khashabi et al.’s multi-sentence questions with multiple correct answers. F1 that cannot be faked by picking one span.
- **ReCoRD** — Zhang et al.’s cloze over news, entities as the missing piece.
- **RTE** — kept from GLUE, because entailment was still earning its keep.
- **WiC** — Pilehvar and Camacho-Collados, word-in-context: is this word the same sense in two sentences?
- **WSC** — a Winograd Schema format closer to Levesque’s original pronoun problem than GLUE’s WNLI recast.

The mix is still English, still mostly classification and span-ish work, still an average of unlike scores. It is “stickier” because the items were chosen to remain hard after BERT-style fine-tuning had embarrassed GLUE.

## What “stickier” meant in 2019

It meant: human performance still sat above the machines by a gap you could discuss without squinting. It meant: you could not win by being merely good at MNLI-style entailment and sentiment. COPA and WSC punish a model that has no idea what “it” points at. MultiRC punishes a model that thinks a question has one highlightable phrase. BoolQ punishes a model that cannot say no.

It also meant the suite was smaller. Small is sticky and small is brittle. CB and WSC do not give you the law of large numbers. A prompt quirk, a label error, or a leak can move the headline more than a genuine modeling idea. SuperGLUE inherited GLUE’s leaderboard culture and a more fragile denominator.

## The human ceiling as a character

SuperGLUE’s tables made “human performance” a character in the story. When models later reached or passed that character on the headline average, the sequel had the same problem as the original. The field did not stop. It changed genres: multiple-choice exams (MMLU), preference rooms (Arena), executable tests (HumanEval, SWE-bench). SuperGLUE is the last major moment when “general-purpose language understanding” still meant a pile of English classification tasks with a hidden test server.

If you see a 2024 card reporting SuperGLUE, ask whether anyone still uses the official submission path. Many numbers in the wild are development-set vibes or partial task lists. The paper’s contract was the server.

## What it kept from GLUE

The average. The English-only horizon. The fine-tuning assumption. The diagnostics impulse (SuperGLUE also shipped analysis tools). The NYU-and-friends editorial taste: inference, pronouns, a little common sense, not dialogue, not code, not toxicity.

That taste is not a defect. It is a date. 2019’s “general-purpose” was a sentence about whether one pretrained encoder could be fine-tuned across formats. 2024’s “general-purpose” is a sentence about whether a chatbot can be a colleague. SuperGLUE measures the first sentence. It can only spectate the second.

## How to read it now

Read it as the official admission that GLUE worked. Suites that work get climbed. Climbed suites need sequels or they become folklore. SuperGLUE is the sequel. MMLU is a different sport. HELM is a refusal to keep printing one sport’s average as a worldview.

The stickiness was real for a while. Then the models grew another order of magnitude and the glue — even the super kind — dried in a new way. The paper remains the right citation for the moment the field said, in public, that the first yardstick had become a ruler for a shorter man.
