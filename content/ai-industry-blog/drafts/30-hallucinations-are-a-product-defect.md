---
title: "Hallucinations are a product defect"
slug: hallucinations-are-a-product-defect
meta_description: "GPT-3 already invented facts. ChatGPT made that a consumer event. Treat fluency-without-belief as a defect class, not a personality."
tags: [hallucination, product, evals, 2022, 2026]
era_start: 2022-11
citations:
  - "BROWN2020 https://arxiv.org/abs/2005.14165"
  - "CHATGPT2022 https://openai.com/index/chatgpt/"
  - "LEWIS2020 https://arxiv.org/abs/2005.11401"
status: draft
voice_check: edited
---

The GPT-3 paper (28 May 2020) already said the model would invent plausible news. Human raters had trouble telling the samples from journalism in a controlled test. That was a research warning. On 30 November 2022 it became a homework-and-legal-brief warning. A New York lawyer filed ChatGPT-invented case citations in *Mata v. Avianca* (sanctions, June 2023). The model was not "lying." It was doing the only job it has: sampling a fluent continuation. The product had presented that continuation as a research assistant.

Call it a hallucination if you want. Call it a fabrication. The engineering name is: **uncalibrated next-token output, displayed as an answer.** That is a defect when the UI implies a fact.

## Why it happens, without mysticism

The pretrain objective is not "say true things." It is "predict the next token on a crawl." The crawl contains errors, fiction, and forum confidence. RLHF (InstructGPT, March 2022) rewards answers that *look* helpful. A hedged "I don't know" often loses that reward. Arena voters (2023–) punish it again. You have now trained a machine to prefer a finished paragraph.

Long context and RAG change the *source*, not the habit. A model can ignore the retrieved passage and answer from weights. A model can stitch two passages into a third fact neither contains. "Grounded" is a claim you measure (did each sentence sit in a span?) not a flag you set in LangChain.

Multimodal makes it nastier. A number "read" from a photo that is actually a guess will be trusted because the user can see the photo. See the multimodal draft.

## A short field guide to the 2023–24 public failures

*Mata v. Avianca* (SDNY, 2023): invented case law in a filing. The defect was the UI plus the professional's skip.

Air Canada’s chatbot (tribunal, 2024): a policy the bot invented, the company tried to disown, the tribunal did not let them. `[CITE NEEDED]` the decision citation if you brief counsel — the lesson is stable: if it speaks on your domain, it is your agent.

Student essays and "AI detectors" (see the school draft): a different defect, false accusation, same root (fluency mistaken for a human).

These are not cute. They are the cost of selling a sampler as a clerk.

## What has reduced it, in public

Retrieval with forced citations (Lewis et al. 2020, and every later production RAG that actually logs spans).

Checkable tools: calculator, code execution, search with click-through. Toolformer and function calling are defect-reducers when the tool is the authority.

Refusal to answer when retrieval is empty. Rarely shipped, because it looks like a worse demo.

Reasoning models (o1, R1) help on tasks with a verifier. They do not help on "who was mayor in 2011" unless you gave them a source. They can hallucinate a *prettier* proof.

What has not worked: telling the model "be accurate" in the system prompt as your only control. That is a wish.

## Calibration is the missing graph

A model that is 70% accurate and *knows* when it is guessing is safer than an 85% model that is always sure. InstructGPT-class training often hurts calibration while it helps preference. Later work (the "verbalized confidence" papers, 2024–25) tried to get a number out of the model. The number is usually overconfident. If you show it to a user, you are showing theater unless you have a reliability diagram on *your* set.

A better UX than a fake 0.92: "I found two passages; they disagree; here they are." That is RAG plus humility. It ships. It looks worse on Arena. Ship it anyway.

## Product patterns that treat it as a defect

**Show work or don't pretend.** Footnotes that map to spans. A "from the web" vs "from the model" badge that is honest.

**Separate draft from send.** Copilot-in-Word got this more right than ChatGPT-the-portal: a human still hits enter. The *Mata* failure was skip-the-human plus a UI that looked like Westlaw.

**Eval the embarrassing tickets.** A frozen set of "we already got this wrong" questions, rerun on every bump. Public MMLU will not save you.

**Severity.** A wrong haiku is not a wrong insulin instruction. Route the second class to a smaller allowed-set or a human. If you cannot classify severity, you cannot ship to the second class.

## What not to promise

"Hallucination-free." No serious lab promises this in a place counsel can read. "Reduced on this eval, here's the number, here's the residual." That you can promise.

## Opinion

The decade's original sin was selling a sampler as a database. GPT-3's authors knew. The 2022 box forgot on purpose, because a box that says "I don't know" grows slower.

A 2026 product that still treats fabrication as a cute quirk is not behind on research. It is behind on defect triage. Put it on the same board as an SSO outage. Then watch it get fixed.
