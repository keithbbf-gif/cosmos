---
voice_check: edited
title: "What a benchmark is, and what it pretends"
slug: what-a-benchmark-is
kind: essay
era: 2002–2024
tags: [overview, evaluation, methodology]
portrait: null
portrait_status: none
---

A benchmark, in the sense this series uses the word, is a public agreement to be compared on a shared hardship. Someone publishes items. Someone publishes a scoring rule. Other people run models and report a number. The hardship is the point. If the items are easy, the agreement dies of saturation. If the rule is vague, the agreement dies of argument. If the items never leave one lab, the agreement was never public.

That is already more than a dataset. A dataset can sit on a disk. A benchmark is a dataset plus a social life: a paper, a leaderboard or a table in a paper, a habit of citing the number in a model card, and a later literature that explains why the number lied.

## The parts

**Items.** Sentences, questions, images, GitHub issues, tool traces. They have to be fixed enough that two groups can claim to have run “the same test.” They have to be numerous enough that a lucky prompt does not look like a theory.

**A split.** Training, development, test — or, in the 2020s, “the whole thing is test because nobody should fine-tune on it.” The split is where leakage is born. See [When the exam was in the library](contamination-and-leakage.md).

**A scorer.** Exact match, F1, accuracy, BLEU, `pass@k`, a fail-to-pass test suite, a human vote, a model asked to play judge. The scorer is not a detail. Change the scorer and you have a different instrument that happens to share a folder name.

**A prompt contract.** Older suites assumed fine-tuning. Newer suites assume a template: few-shot, chain-of-thought, system message, tool access. HELM’s authors spent pages on this because, before them, two “MMLU numbers” could be two different homework assignments.

**A report.** A table, a site, a tweet-length claim. The report is where the instrument becomes a rumor.

## What it pretends

The polite pretense is that the hardship stands for a capacity: “language understanding,” “reasoning,” “coding,” “alignment with human preference.” The papers are usually more careful than the slides. GLUE’s authors called their suite a benchmark for English NLU and then filled it with entailment, sentiment, and grammaticality — real tasks, and not the whole of understanding. MMLU’s authors called theirs massive multitask language understanding and then filled it with multiple-choice exams. Arena’s authors called theirs preference. Preference is the rare case where the pretense and the measurement match.

The dangerous pretense is that a single average is a mind. Nine tasks averaged (GLUE). Fifty-seven subjects averaged (MMLU). A Bradley-Terry coefficient (Arena). A fail-to-pass rate on 2,294 GitHub issues (SWE-bench). Each of those numbers is a compression. Compression is useful. It is also how a specialist model that is merely good at multiple-choice exams becomes, in a keynote, “generally capable.”

## Who gets to publish one

In the 2010s the typical authors were academic NLP or vision groups with a shared task tradition: SemEval, CoNLL, ILSVRC, the GLUE site at NYU. In the 2020s the authors diversified. University labs still publish (Princeton’s SWE-bench; Stanford’s HELM; Waterloo’s MMLU-Pro). Industry labs publish (OpenAI’s HumanEval, GSM8K, SimpleQA; Google’s MBPP). Collectives publish (BIG-bench’s hundreds of contributors; LMSYS’s Arena). Safety institutes publish (Center for AI Safety’s work on Humanity’s Last Exam, with Scale AI). Epoch AI publishes FrontierMath.

The institutional mix matters because incentives mix. A company that sells a model also publishes an eval that its model can sit on. That is not automatically fraud. It is a conflict that the paper should make easy to see. OpenAI’s SimpleQA paper is a factuality test collected against GPT-4; that fact belongs in the explainer, not in a footnote of suspicion. Scale AI’s name on Humanity’s Last Exam belongs in the byline, because it is in the byline.

## Static files and live rooms

A frozen file is easy to cite and easy to spoil. A live room — Arena, LiveBench’s monthly refresh, a hidden test split that never ships — is harder to spoil and harder to reproduce. The field now runs both, and then argues about which one is “real.” The argument is misplaced. They answer different questions. A file asks: did this system, on this date, match this key? A room asks: what do people (or this month’s fresh items) do with the system now? See [A file on disk, a vote in public](arena-versus-static.md).

## How to tell a yardstick from a costume

A yardstick publishes items or a reproducible generator, a scoring rule a second lab can implement, and enough protocol that a disagreement can be localized. A costume publishes a name, a vibe, and a number that cannot be re-run.

Some public evals sit between those poles. Chatbot Arena publishes votes and a statistical story; it does not publish tomorrow’s user prompts in advance. FrontierMath publishes a paper and a difficulty argument; many items stay private so they are not immediately trained on. Both can still be public science. Privacy of items is a method, not a sin — if the protocol is public and the holdout is not a marketing department.

## The sentence that should survive

If you remember one sentence from this piece, remember this: a benchmark is a hardship people agreed to share, plus a rule for saying who suffered less. It is not a mind, a product, or a moral grade. The explainers that follow are tours of particular hardships. They are not endorsements of the rumors that grew on them.
