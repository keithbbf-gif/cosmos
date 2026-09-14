---
voice_check: human
title: "DROP: the paragraph that wants you to count"
slug: drop
kind: explainer
era: 2019
tags: [drop, dua, allenai, qa]
portrait: null
portrait_status: none
---

Dheeru Dua, Yizhong Wang, Pradeep Dasigi, Gabriel Stanovsky, Sameer Singh, and Matt Gardner published “DROP: A Reading Comprehension Benchmark Requiring Discrete Reasoning Over Paragraphs” at NAACL 2019. Allen Institute and Irvine. SQuAD had made pointing fashionable. DROP asked for addition, subtraction, counting, sorting, and comparison on facts that are in the paragraph but are not sitting there as a pre-packaged span.

The name is Discrete Reasoning Over Paragraphs. The hardship is a football drive, a census table in prose, a list of people who entered a room. The answer is often a number or a short list you must assemble.

## Why pointing was not enough

If the paragraph says the team scored 3, then 7, then 10, and the question asks for the total, the gold span may not exist. You have to add. If the question asks who arrived first, you have to compare dates. Extractive F1 will either fail or reward a lucky nearby numeral. DROP’s evaluation still uses numbers and F1-like matching, but the *task* is not “find the span.” It is “operate.”

That operation is still small. It is not a spreadsheet model. It is not a proof. It is discrete reasoning at the scale of a paragraph, which was enough, in 2019, to drop the scores of systems that had just climbed SQuAD.

## What the items feel like

Many are sports narratives and Wikipedia-style event write-ups, because those contain comparable numbers and entities. The distribution is a scope. A model that can total a football drive may still fail a legal hypothetical. The authors did not claim otherwise.

Annotation is hard. Discrete answers have to be consistent. Later work found noise, as later work always does. If you use DROP as a 2026 frontier claim, you are late. If you use it as a diagnostic for “does my reader actually add,” you are on time.

## An item in the hand

A paragraph lists scoring plays and clock times. The question asks how many points were scored after the two-minute warning, or which player had the longest reception that is actually named in the text. The numerals are all present. The span you want may not be. You add, you filter, you compare.

A 2019 pointer model would highlight “14–7” because it looks like a score. A DROP-aware system has to notice that 14–7 is a standing and not the answer to “how many field goals.” That distinction is small and it is the whole reason the file exists.

Sports prose is over-represented because it is full of comparable numbers. Wikipedia event articles are the other habitat. If your product is medical notes, DROP is a cousin, not a certificate. If your product is a reader that must add, it is a cheap, dated, still-useful floor.

Annotation noise shows up as two gold numbers that a careful human could both defend. When a model “fails,” sample the item before you rewrite the architecture.

## How generation changed the student

A 2019 reader predicted spans or a small program. A 2024 chatbot writes a paragraph and then a number. The scorer may only see the number. Chain-of-thought helps when the steps are arithmetic and hurts when the babble invents an extra field goal. The file did not change. The student did.

## How to read a DROP line

Ask F1 versus exact match, whether arithmetic was done with a tool, and whether they also report SQuAD (the pointing floor) and a later quantitative QA set. If the card only has DROP, you are looking at a 2019 discrete-reasoning paragraph exam. That is a real exam. It is not “the model can reason.”

When the highlight is easy, change the homework. Dua’s group changed it to counting. The next groups changed it again. Keep the paragraph. Keep the operation. Keep the date.

A common mis-citation is to file DROP under “reasoning” next to GPQA or MATH. It is discrete operations on a paragraph. That is a smaller, older, still-real skill. Give it the smaller noun. If the model used a calculator or a short program, say that tool by name; a tool-using reader is a different student.
