---
voice_check: edited
title: "AI2 ARC: grade-school science, two doors"
slug: ai2-arc
kind: explainer
era: 2018
tags: [ai2-arc, allenai, clark, science]
portrait: null
portrait_status: none
---

Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick, and Oyvind Tafjord published “Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge” in 2018 (arXiv:1803.05457). Allen Institute for AI. The questions are grade-school standardized science: multiple choice, the sort of item that asks why a shadow is longer at a certain hour, or what a plant gets from a dark closet.

The paper’s taunt is in the title. SQuAD-style pointing had started to look solved. ARC asked for questions that need you to combine facts, not just highlight a span.

## Easy and Challenge

The authors split the set. **ARC-Easy** is the door most retrieval-and-overlap systems could already open. **ARC-Challenge** is the door they could not: items that a simple information-retrieval baseline missed. The Challenge set is the one later harnesses mean when they say “ARC” in an open-LLM table — except when they do not, and mix Easy in, and look braver than they are.

Say Challenge. Say Easy. Do not say ARC without a modifier if you can help it. And do not say ARC if you mean François Chollet’s Abstraction and Reasoning Corpus. That collision has its own explainer: [ARC-AGI](arc-agi.md).

## What “reasoning” meant in 2018

It meant: the answer is not a span in a provided paragraph. You may need a science fact, a little causal structure, and the elimination of distractors written to trap a child. It did not mean formal logic. It did not mean graduate chemistry (that is closer to GPQA). It did not mean abstract grid puzzles (that is Chollet).

The 2018 systems needed retrieval over a science corpus the authors provided. The 2023 chatbots need a forward pass. Same file, different student. A high ARC-Challenge accuracy today is expected. A low one is a smell, or a broken harness.

## An item in the hand

A Challenge item might ask what happens to the water level when a boat in a pool throws a rock overboard, or why a metal spoon feels colder than a wooden one in the same room. The facts are grade-school. The distractors are written for a child who almost remembers. A 2018 retrieval baseline would fetch a sentence that shares nouns and still pick the wrong letter. A 2024 chatbot will often pick the right one and still be unable to run a lab.

The Easy set includes items a lexical overlap system could already do. Mixing Easy into a “Challenge” number is a way to look taller. Harnesses have done it by accident. Check the config.

Clark’s taunt — try ARC if you think QA is solved — was aimed at span extractors. It landed. It should not be recycled as a 2026 reasoning claim. The file did its job. The job was 2018 science questions, not a theory of mind.

## Why it stayed in the open tables

EleutherAI’s evaluation harness, Hugging Face leaderboards, and a thousand model cards needed a short science noun. ARC was public, multiple-choice, and already split into a hard door. It sat beside HellaSwag, MMLU, and WinoGrande as default furniture.

Furniture still measures something: can you pass a particular flavor of U.S. grade-school science item? That is not nothing. It is also not a reasoning research program by itself. Clark’s title was a taunt at span-QA. It was not a claim that the Challenge set would remain a wall after a decade of pretraining.

## How to read an AI2 ARC line

Ask Easy versus Challenge, the number of shots, and whether the retrieval corpus was allowed (historical) or the model was closed-book (modern default). If the card says only “ARC,” look at the harness source. If the card is sitting next to “ARC-AGI,” you are in a slide that needed an editor.

Grade-school science, two doors, a 2018 taunt at pointing. Keep the institute in the name when you can: AI2 ARC. The other ARC will thank you.

A common mis-citation is a 2026 “reasoning” plot that uses ARC-Challenge as the only science point. Pair it with GPQA or a later exam if you want graduate hardship. Leave the grade-school door labeled as grade-school.
