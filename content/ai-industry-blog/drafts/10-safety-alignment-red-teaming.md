---
title: "Safety, alignment, red-teaming"
slug: safety-alignment-red-teaming
meta_description: "InstructGPT (March 2022), Constitutional AI (December 2022), and the high-level practice of trying to make a next-token model behave."
tags: [rlhf, constitutional-ai, red-team, safety, 2022]
era_start: 2022-03
citations:
  - "OUYANG2022 https://arxiv.org/abs/2203.02155"
  - "BAI2022 https://arxiv.org/abs/2212.08073"
  - "CHATGPT2022 https://openai.com/index/chatgpt/"
  - "NIST_RMF https://doi.org/10.6028/NIST.AI.100-1"
status: draft
voice_check: human
---

On 4 March 2022, Ouyang et al. posted the InstructGPT paper. The opening is the whole field in one line: making the model bigger does not make it follow a user's intent. A 1.3B model trained with human feedback beat 175B GPT-3 on labeler preference. Helpfulness went up. Toxicity, on their measurements, went down a bit. The model still made "simple mistakes."

That paper is the industrial safety stack, year one: demonstrate the behavior you want, rank the alternatives, reinforce. Everything after — constitutions, RLAIF, refusal taxonomies, bug bounties — is a variation on who writes the preference and how expensive they are.

This piece stays at that altitude. No exploit recipes. No "how to jailbreak." Those do not belong in a public education pack.

## RLHF, said without incense

Supervised fine-tuning teaches style. The reward model teaches taste. PPO (or whatever optimizer the lab uses now) teaches the policy to chase that taste. The humans in InstructGPT were contractors ranking outputs on API-like prompts. Their taste is not "humanity." It is a labor pool with instructions.

Christiano et al. 2017 and Stiennon et al. 2020 (summarization) sat underneath. InstructGPT made the loop a default API behavior. ChatGPT (30 November 2022) was the same loop with dialogue data. When a vendor says "aligned," ask: aligned to which raters, on which prompt mix, with what refusal policy? If they cannot answer, they mean "we ran RLHF."

Known side effects, all documented in public research and user lore: sycophancy (agree with the user's error), over-refusal (decline a harmless ask because it rhymes with a banned one), reward hacking (the output looks preferred and is empty). Preference models are models. They fail.

## Constitutions and cheaper feedback

Bai et al., *Constitutional AI* (15 December 2022), tried to take a slice of harmlessness labeling off humans. Write principles in English. Have the model critique and revise its own answers. Train a preference model from AI feedback (RLAIF). Anthropic's Claude line is the product that grew up next to that paper.

Principles are not magic. They are a prompt with institutional backing. Who writes the constitution is a governance decision: a lab, a regulator, a customer. A bank's constitution is not a teenager's. A single global model with one constitution will offend someone on purpose or by accident. That is not a reason to skip the work. It is a reason to stop talking as if the work had a unique moral owner.

## Red-teaming, the adult version

Before GPT-4's March 2023 launch, OpenAI ran an adversarial testing program and said so in the announcement: six months of iteration after ChatGPT. External red-teamers, domain experts, a list of harms (bio, cyber, scams, self-harm, election junk). The public write-ups are high-level, which is correct.

A serious red team does not publish a cookbook. It publishes *categories* and *rates*: how often the model assists on a disallowed class, how often it refuses a allowed class, how the rate moves after a mitigation. NIST's AI RMF 1.0 (26 January 2023) is a voluntary language for that work — map, measure, manage, govern — not a test harness.

Internal red teams get captured. They start to like the model. External programs (the UK AISI-style evals, US AISI while it existed in that form, academic centers, paid bug bounties) exist because capture is normal. After EO 14110 (30 October 2023) a lot of US "safety" process was tied to an order that EO 14179 (23 January 2025) revoked. The *practice* of pre-release testing did not vanish with the letterhead. The federal mandate did. See the regulation piece.

What belongs in public: that you test, what classes you test, how you handle reports. What does not: the prompts that still work.

## System cards, the public cousin

OpenAI's GPT-4 System Card (14 March 2023) is the artifact to steal from, not the model. It lists categories, qualitative findings, and the fact of an external red team. Anthropic's model cards and Google's Gemini safety reports sit in the same genre. They are incomplete. They are still better than a blog post that says "we red-teamed it."

A card that only lists *intentions* is PR. A card that lists rates (even ranges) and residual risks is a start. NIST AI 100-1's "measure" function is that start in federal English.

What we will not do here is walk through jailbreak technique. The public internet is already a tutorial. A product pack that adds another is not education.

## Dual use without theater

Language models are dual-use because language is. They can draft a phishing mail or a threat model. They can explain a paper or hallucinate a citation that sends a student to the wrong protocol. Capability without process is not "safety research." It is shipping.

The grown-up posture, visible at labs that have been embarrassed in public: default-deny on a short list of high-severity classes, logging, a human path for edge cases, and the humility to pull a feature (remember OpenAI's first voice-cloning experiments, and the on-again-off-again custom GPT store fights). The immature posture is a launch keynote that says "we take safety seriously" and a policy page last edited six months ago.

Incident response belongs next to the model card. When a model starts giving a new class of bad help — after a silent bump, or after a viral prompt style — the product question is how fast you can roll back a checkpoint and how you tell users. A lab that cannot revert is not "aligned." It is stuck.

## Opinion

Alignment, in the sense that shipped, is product quality under a moral vocabulary. InstructGPT made the vocabulary operational. Constitutional AI made it cheaper to iterate. Red-teaming is how you check whether either one survived contact with people who are trying to break it.

Treat anyone who claims a solved alignment as a salesperson. Treat anyone who treats all safety work as a plot against open weights as a salesperson of a different kind. The work is narrower and more necessary than both speeches: measure refusals, measure assists, keep the cookbooks off the blog.
