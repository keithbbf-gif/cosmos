---
voice_check: human
title: "LegalBench: tasks a lawyer would recognize, not a bar exam cosplay"
slug: legalbench
kind: explainer
era: 2023
tags: [legalbench, law, guha]
portrait: null
portrait_status: none
---

Neel Guha, Julian Nyarko, Daniel Ho, Christopher Ré, and a long list of legal and computer-science collaborators published “LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models” (arXiv:2308.11462, 2023; later a NeurIPS datasets paper). Stanford. The hardship is not “take the bar.” It is dozens of small legal tasks that lawyers and legal scholars actually named: classification of a clause, spotting a kind of issue, applying a given rule to a short fact pattern, extraction from a passage.

The collaborative build is the method. Legal experts proposed tasks. The suite keeps those task boundaries instead of blending them into one GPA.

## Why not one exam

A bar-style multiple-choice average will tell you something about exam technique and the crawl of prep books. It will not tell you whether a model can, given a statute excerpt, apply the rule and stop. LegalBench’s authors wanted the second, in pieces small enough to score and to disagree about.

Some tasks are easy classification. Some want you to stay inside a provided rule (a “rule-application” mood that is closer to IRAC as a constrained game than to open-ended advice). The interesting scientific object is the spread. A model that is high on extraction and low on rule application is a highlighter, not a clerk.

## What it will not do

It will not certify a lawyer. It will not replace a professional responsibility course. It will not tell you the law of a jurisdiction the tasks do not cover. U.S. law is over-represented because that is who showed up to write tasks. A card that says “legal reasoning” on the basis of this suite should say “LegalBench’s tasks, mostly U.S.”

It will not measure whether the model refuses to give reckless advice. Pair it with a safety or professional-norm eval if that is your claim.

## An item in the hand

A task might give you a short contract clause and ask whether it is a non-compete, an assignment, or neither. Another gives you a one-paragraph fact pattern and a rule, and asks whether the rule’s element is met. A third asks you to extract a date or a party. None of those is “write a brief.” All of them are chores a junior person actually does, badly or well, on a Tuesday.

The rule-application items are the ones to watch. If you hide the rule, you are testing memory of doctrine. If you show the rule, you are testing whether the model can stay inside a text. Legal work is often the second, because the doctrine lives in a jurisdiction’s documents, not in the weights. Guha’s collaborators built tasks that can tell those apart — if you report them apart.

Hallucinated citations are mostly out of scope here. Pair a generation-heavy legal product with a citation audit. LegalBench will not do that audit for you.

## How it sits next to MMLU’s law slice

MMLU has a professional-law subset that behaves like a four-choice exam. LegalBench is a task zoo with expert fingerprints. If you report only MMLU-law, you are reporting exam recognition. If you report LegalBench, report which tasks. The zoo average is a last resort.

Guha also appears on the HELM author list. The through-line is measurement as a grid, not as a mascot. LegalBench is a grid for a profession.

## How to read a LegalBench line

Per-task tables, the prompt (the suite is sensitive to whether you give the rule), and whether a lawyer reviewed the errors. A single percentage is a press object. The collaboratively built tasks are the science.

A clause, a rule, a fact pattern, a label a lawyer would recognize. That is enough for a public yardstick. It is not enough for a license. Keep the license in the human world.

A common mis-citation is a single LegalBench percentage in a procurement slide. Ask for the task names. If the slide cannot name three tasks, it is not using the suite. It is using the brand. If the prompt hid the statute or the rule, say that too; memory and application are different tasks.
