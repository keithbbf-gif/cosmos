---
title: "Anthropic, the other lab"
slug: anthropic-the-other-lab
meta_description: "Claude 1 (March 2023) through computer-use (Oct 2024): Constitutional AI as a product line, not a sermon."
tags: [anthropic, claude, constitutional-ai, 2023, 2024]
era_start: 2023-03
citations:
  - "BAI2022 https://arxiv.org/abs/2212.08073"
  - "CLAUDE3 https://www.anthropic.com/news/claude-3-family"
  - "COMPUSE https://www.anthropic.com/news/3-5-models-and-computer-use"
status: draft
voice_check: human
---

On 14 March 2023 — the same week as GPT-4 — Anthropic put Claude in a waitlist chat. The company was the 2021 OpenAI diaspora (Amodei et al.) plus a research program that had already published *Constitutional AI* (Bai et al., 15 December 2022). Claude 2 arrived 11 July 2023 with a 100K context that was, for a few months, the thing you used when GPT-4's 8K felt like a closet. Claude 3 (4 March 2024) shipped Haiku, Sonnet, and Opus as a priced ladder. Sonnet 3.5 (June 2024, then October) became the default coding model for a lot of people who would not have said "I am an Anthropic customer" a year earlier.

This pack already has a safety piece and a computer-use piece. This one is the lab as a product company.

## What they sold that OpenAI did not, at first

Long context as a default, not a limited SKU. Developers noticed. Legal teams noticed. "Paste the contract" is a boring feature and a real one.

A tone. Claude's refusals and its prose style are the constitution plus a lot of SFT that we do not have. Users describe it as more cautious, more willing to write the essay, sometimes more sycophantic in a different key. Taste is not a bench. It is why two labs can share a capability curve and not share an account.

The Messages API and the later tool-use / computer-use primitives were documented like something you would put in a production repo: XML-ish artifacts early, then cleaner tool JSON, then a Docker desktop you were told not to run on your daily machine (22 October 2024). OpenAI often shipped the consumer object first and the API second. Anthropic often reversed that. Neither is virtue. It is a go-to-market.

## Money and the other landlord

Google and Amazon (Bedrock, TPUs, multi-cloud announcements through 2023–25) are Anthropic's capital-and-iron story the way Azure is OpenAI's. The details of each round get restated. The shape does not: a "safety-first" lab still needs a cloud landlord and a training budget that looks like a nation-state science program. Public benefit corporation plus long-term benefit trust is the governance brand. November 2023's OpenAI weekend is the context in which that brand is pitched. See the board-week draft. Do not treat a PBC filing as a safety eval.

## Claude as an API dialect

Early Claude APIs used more XML-shaped tool tags than OpenAI's function JSON. Teams that abstracted "the vendor" in 2023 still leaked dialect into prompts (`Human:` / `Assistant:` vs chat roles). A portable prompt is a lie you discover at 2 a.m. Keep a thin adapter. Keep golden traces per vendor. When Sonnet 3.5 shipped, those traces were how you knew whether *your* coding tasks moved, not LMSYS.

The 200K window (late 2023) plus tool use is why Claude showed up in "paste the repo" products before computer-use existed. It was already an agent with a bigger clipboard.

## The model line, without a scoreboard

Haiku = cheap and fast. Sonnet = the workhorse. Opus = the expensive brain, sometimes not worth it on your private set. 3.5 Sonnet's coding jump is the 2024 event a lot of IDE vendors felt. 2025–26 successor numbers (4, 4.5, 4.6 in secondary blogs) should be taken from Anthropic's own post the week you publish. `[CITE NEEDED]` for any OSWorld percentage you want on a slide.

Computer-use is the 2024–26 differentiator that is not a chat tone. It is also the risk differentiator. A lab that gives you `bash` and a mouse is a lab whose safety story has to cover *actions*, not just completions. Their public write-up is better than most. It is still a beta with a warning label.

## What they did not solve

They did not solve "the model is wrong." They did not solve copyright. They did not make constitutional principles a democratic object; they made them a lab object. A bank can write a stricter constitution in the prompt. That is not the same as the training constitution. Users who think Claude "won't lie because of the constitution" have not watched it invent a citation.

They also did not stay small. Consumer Claude, Team, Enterprise, the API — the 2024–26 Anthropic is a full-funnel SaaS company that happens to have a research blog. That is allowed. It is just not the 2022 myth.

## Opinion

Anthropic is the existence proof that a second frontier lab can exist as a product, not a paper. Constitutional AI is the research brand. Sonnet-in-the-IDE is the revenue brand. Computer-use is the 2026 question.

If you only have one vendor, the board week already explained why that is sloppy. Claude is the spare tire a lot of teams actually mounted. Treat it as a tire: check the pressure (evals), do not give it the keys to the car (prod credentials), and read the constitution as a style guide, not a law.
