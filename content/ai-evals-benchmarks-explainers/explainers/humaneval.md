---
voice_check: edited
title: "HumanEval: 164 docstrings and a hidden test"
slug: humaneval
kind: explainer
era: 2021
tags: [humaneval, codex, openai, code]
portrait: null
portrait_status: none
---

HumanEval is small enough to memorize as a folklore number: 164. Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, and a long OpenAI list published “Evaluating Large Language Models Trained on Code” in 2021 (arXiv:2107.03374). The paper is the Codex paper. The eval is a set of handwritten Python problems: a function signature, a docstring, a few visible examples, and hidden unit tests you do not get to see until the harness runs your function body.

The scientific object is not “can the model program.” It is: given this docstring, can it write a function that satisfies these tests, under this sampling budget? See [pass@k](../essays/pass-at-k-and-the-coder-receipt.md).

## Why they wrote the items

Existing code corpora were training data. Existing programming contests were often in the crawl. The authors wanted problems that were, as far as they could manage, not copied from the web — handwritten, original, in the style of a simple interview or a textbook exercise. 164 is a modest N. Modest is a feature when you are claiming originality. Modest is a bug when you want statistical calm.

Each item is short. The room is a single function. No repository, no issue tracker, no API design, no tests authored by the model. If you can pass HumanEval and cannot open a pull request, you have not found a contradiction. You have found the edge of the instrument.

## How a run works

The model sees the prompt (signature + docstring + examples). It emits completions. Each completion is executed against hidden tests. Pass or fail is binary per problem. `pass@k` estimates how often at least one of k samples would have passed. Temperature 0.8 and k = 100 in the original tables is a different sport from greedy `pass@1`. Cards that omit k are omitting the sport.

Later variants add more tests (HumanEval+ from EvalPlus, Liu et al., 2023) because the original hidden tests were thin. A thin test suite is a generous teacher. A function can be wrong in ways the authors did not probe. Plus-style expansions are a criticism of the key, not a new problem set.

## An item in the hand

A signature: `def has_close_elements(numbers, threshold):`. A docstring that states the contract in English, with a couple of examples. Hidden tests you will not see if you are the model. You write a body. The harness runs it.

That is an interview whiteboard with a grading script. It is a good interview whiteboard. It is not a week on a team. The original 164 were written to be original. After they became famous, originality became a hope. EvalPlus later added tests because the hidden suite was thin enough that a wrong function could still go green.

If you report HumanEval and your completions were never executed, you have reported a poetry contest. Chen’s paper is about execution. Keep the interpreter in the pipeline.

## What the number became

It became the default coding integer, the way MMLU became the default exam integer. Models climbed. Tutorials reprinted the problems. The handwritten shield weakened: 164 famous docstrings do not stay off the internet. A 2024 `pass@1` in the 90s on the original file is a mixture of real code skill, prompt craft, and possible familiarity.

LiveCodeBench, contest clones, and SWE-bench exist because this file stopped being a frontier. That is a successful life cycle. It is also why reprinting HumanEval as “coding ability” in a keynote is now a genre mistake.

## Related files

**MBPP** (Austin et al., 2021) is larger, a bit more pedestrian, still function-level Python. See [MBPP](mbpp.md).

**DS-1000** (Lai et al., ICML 2023) asks for data-science snippets against real Stack Overflow-shaped problems.

**SWE-bench** asks for a patch in a repo. Different animal.

HumanEval is the interview whiteboard. SWE-bench is the ticket. Do not hire from the whiteboard alone.

## How to read a HumanEval line

Name the file (original vs. plus), the language (the original is Python), k, temperature, and whether execution was actually run. A model judge staring at code is not HumanEval. A few-shot prompt that pastes similar problems is not the zero-shot interview the paper made famous.

164 docstrings. Hidden tests. A receipt called `pass@k`. The paper that introduced a code model also introduced the yardstick that would, for a few years, stand in for the profession. The profession is larger. The yardstick still works as a historical interview — if you remember it is an interview.
