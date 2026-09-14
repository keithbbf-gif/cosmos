---
voice_check: human
title: "A file on disk, a vote in public"
slug: arena-versus-static
kind: essay
era: 2023–2025
tags: [arena, static-benchmarks, preference, lmsys]
portrait: null
portrait_status: none
---

There are two kinds of public hardship, and they do not settle the same bet.

One kind is a file. GLUE, MMLU, HumanEval, GSM8K: a list of items and a key. You can download it, hash it, argue about item 412, and run it next year on a machine that does not exist yet. The file does not care who you are.

The other kind is a room. Chatbot Arena, as Chiang, Zheng, Sheng, Angelopoulos, and colleagues described it at ICML 2024, is a pairwise vote. A person types a prompt. Two unnamed models answer. The person picks a winner, or a tie, or walks away. The prompts are whatever the public brought today. The leaderboard is a statistical summary of those fights.

Calling one of these “real evaluation” and the other “fake” is a category error. A file measures agreement with a key. A room measures preference under a sampling process you do not control. Both are public. Both can be gamed. They fail in different weather.

## What a file is good for

A file is good for localization. If two labs disagree about a HumanEval number, they can compare completions on problem 47. If MMLU’s anatomy subset moves and the law subset does not, that is a clue. HELM’s authors pushed this further: same scenarios, several metrics, raw completions released, so a third party can re-score.

A file is also good for history. You can say, without theater, that SuperGLUE was published at NeurIPS 2019 because GLUE’s average had been climbed. You can say HumanEval appeared in the 2021 Codex paper as 164 handwritten Python problems. Those sentences stay true when the leaderboard of the week does not.

The file’s vice is death by popularity. See [When the exam was in the library](contamination-and-leakage.md). Its other vice is the key. Exact match cannot see a correct proof written in a different algebra. BLEU cannot see a good translation that chose other words. A multiple-choice key cannot see that all four options are a little wrong.

## What a room is good for

A room is good for the thing a key cannot see: whether a person, today, likes the reply. That is not a small thing. Instruction-following, tone, refusal style, and the ability to stay useful across a messy prompt are poorly captured by MNLI. Zheng, Chiang, and colleagues had already published MT-Bench and an “LLM-as-a-judge” study (NeurIPS 2023). Arena is the human-vote sibling: no rubric except the user’s thumb.

The ICML paper reported, at the time of writing, more than 240,000 votes, a claim that crowdsourced votes agreed reasonably with expert raters, and a statistical apparatus (Bradley-Terry style ranking, not a raw win rate). Those are public methodological claims. They are not a promise that the crowd is a philosopher.

The room’s vice is the crowd. The people who show up to vote are not a census. They bring jailbreaks, homework, erotica, code, and jokes in proportions that no standards body chose. A model that is pleasant in that mixture can look “better” than a model that is more careful, or more boring, or better at a job the voters did not ask. Style wins votes. So does sycophancy. So does answering when a refusal was due.

The room’s other vice is identity. LMSYS incubated the site. In September 2024 the collective announced a dedicated home at lmarena.ai. Later public materials say LMArena. The ICML paper still says Chatbot Arena and chat.lmsys.org. An explainer that pretends there was only one noun is doing marketing. An explainer that treats the rename as a different scientific object is doing confusion. It is the same social instrument growing a new URL.

## Judges that are not people

Between the file and the room sits a third object: a model scoring another model. AlpacaEval (from the Alpaca/AlpacaFarm line at Stanford and collaborators) and MT-Bench both lean on this. It is cheap. It correlates, sometimes, with human preference. It also inherits the judge’s taste and the judge’s blindness. If the judge likes lists, lists rise. If the judge is the cousin of the candidate, the family resemblance is not a secret.

LiveBench tried to refuse both the stale file and the chatty judge: new items, automatic keys. That is a fourth object — a file that pretends to be a room by moving. It is a good pretense. It still needs a key.

## How to use both without lying

Use a file when you need a reproducible claim: this checkpoint, this template, this split, this scorer. Use a room when you need to know what people pick when the prompt is not your homework. Use a model judge when you can afford the bias and cannot afford the humans. Do not average them into a super-score and call the average “intelligence.”

The field’s better papers already know this. HELM refused the single number. Arena’s authors called their object preference. MMLU’s authors called theirs multitask understanding and then used multiple choice. The lie begins when a slide erases those nouns.

A file on disk will still be there when the voters go home. A vote in public will still tell you something a file cannot. Keep both. Name which one you are holding.
