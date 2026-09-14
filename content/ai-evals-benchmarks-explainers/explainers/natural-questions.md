---
voice_check: edited
title: "Natural Questions: the query came from a person"
slug: natural-questions
kind: explainer
era: 2019
tags: [natural-questions, google, kwiatkowski, qa]
portrait: null
portrait_status: none
---

Tom Kwiatkowski, Jennimaria Palomaki, Olivia Redfield, Michael Collins, Ankur Parikh, Chris Alberti, Danielle Epstein, Illia Polosukhin, Jacob Devlin, Kenton Lee, Kristina Toutanova, Llion Jones, Matthew Kelcey, Ming-Wei Chang, Andrew Dai, Jakob Uszkoreit, Quoc Le, and Slav Petrov published “Natural Questions: a Benchmark for Question Answering Research” in *Transactions of the ACL*, 2019. Google. The questions are real Google queries. The documents are Wikipedia pages. The annotators mark a long answer (a paragraph) and, when possible, a short answer (a span), or they mark that the page does not answer the query.

SQuAD’s workers read a paragraph and invented a question. NQ’s pipeline starts from a person who wanted to know something. That reversal is the whole instrument.

## Why “natural” is doing work

A crowdworker staring at a paragraph asks questions the paragraph can answer. A user staring at a search box asks questions that are underspecified, wrongly spelled, temporally loaded, or simply not about the page you retrieved. NQ keeps the ones that were paired with a Wikipedia result and then asks: is the answer here, and where?

The unanswerable slice is first-class. A system that always highlights will be punished. SQuAD 2.0 learned that lesson in a synthetic way. NQ brought it in from the query log.

## Long and short

The **long answer** task is closer to retrieval-inside-a-page: which passage, if any? The **short answer** task is closer to SQuAD, when a short span exists. Some queries want a yes/no. The paper’s metrics treat these as related but not identical sports. A card that reports “NQ” without long versus short is smearing them.

Open-domain NQ — retrieve from all of Wikipedia, then read — is the setting that later retriever papers used. Closed-book NQ — no page, just the model — is a different exam that people sometimes run anyway. Name the setting.

## An item in the hand

A query like “when did the berlin wall fall” paired with the Wikipedia page, a long-answer paragraph, and a short date. Or a query that is a mess — a typo, a missing year, a pronoun with no antecedent — paired with a page that does not actually answer it. The second class is the one SQuAD’s workers would not have invented. They already had the paragraph. They asked what it could answer.

NQ’s unanswerable label is a judgment about *this page*, not about the universe. The answer may exist elsewhere. A closed-book model that recites the fact is not succeeding at the 2019 task; it is succeeding at a memory task that borrowed the questions. Keep the page in the sentence if you are citing NQ proper.

The long-answer problem is closer to “which section do I read?” than to “what is the date?” Plenty of systems were good at one and bad at the other. The smear is the lie.

## What a query log is not

It is not a census of human curiosity. It is a log from one company’s search box, in the languages and years they released, filtered for a Wikipedia pairing. It is gold. It is also a particular internet.

Privacy and release took care. The paper is a lesson in publishing user questions without publishing users. The questions that made it out are the ones that could.

## How it aged

Retriever-reader systems climbed the original metrics. Closed-book LLMs turned NQ into a memory test: did the weights store the Wikipedia fact? That is not the 2019 task. It is a cousin that inherited the questions. SimpleQA later tried to make short factuality hard again for models that had eaten trivia. TriviaQA (Joshi et al., ACL 2017) sits in the same family with a different collection story.

## How to read an NQ line

Long or short, open or closed book, which Wikipedia dump, exact match or the paper’s official metrics, and whether unanswerable items were kept. If the model is a chatbot that writes a paragraph, you need a judge or a span-alignment story. Do not quietly convert NQ into a vibe.

A person typed a query. A page may or may not answer it. Kwiatkowski’s group kept both halves. That is why the file is still the citation when you want questions that were not invented after the answer was known.
