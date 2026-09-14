---
title: "AGI talk and product roadmaps"
slug: agi-talk-and-product-roadmaps
meta_description: "From OpenAI's charter to 2025–26 'unified' models: how a destination word bent roadmaps, hiring, and evals."
tags: [agi, roadmaps, evals, 2023, 2026]
era_start: 2023-03
citations:
  - "OAI_CHARTER https://openai.com/charter/"
  - "GPT4 https://openai.com/index/gpt-4-research/"
  - "O1 https://openai.com/index/introducing-openai-o1-preview/"
status: draft
voice_check: human
---

OpenAI's charter (the public one, updated over the years; the page still live) names "highly autonomous systems that outperform humans at most economically valuable work" as the AGI destination and says the company will stop competing on that object if a later-stage project needs to. That sentence is why a chat company has a nonprofit parent and why November 2023's board week (see that draft) sounded like theology. GPT-4's 14 March 2023 post was more careful in the body — "less capable than humans in many real-world scenarios" — and less careful in the culture it fed. Bar-exam clips do that.

This piece is not a bet on a date. It is about what the *word* did to people who ship software.

## What the word bought

Hiring. A certain kind of researcher will not join a "better autocomplete" company and will join an "AGI" company. That is a real labor-market fact. It staffed labs. It also staffed a rhetoric that treated a product delay as a moral event.

Money. Investors who would not fund a wrapper funded a destination. The 2023–25 capex makes more sense as a destination purchase than as a seat-license purchase. See NVIDIA and ROI drafts.

Evals. If the destination is "most economically valuable work," then a moving suite of hard benches (GPQA, SWE-bench, ARC-AGI-class puzzles, the 2024–26 reasoning sets) becomes a proxy religion. Some of those benches are good. The religion is not. A model can climb ARC-AGI and still invent a citation. The evaluation-crisis draft is the longer version.

## Preparedness frameworks, the bureaucratic cousin

OpenAI's Preparedness Framework (2023–24 public iterations), Anthropic's RSP (Responsible Scaling Policy), and Google's various safety-level notes are how labs turned destination talk into gates: if a model crosses a capability line (bio, cyber, autonomy), do extra evals, maybe pause. The documents are public-ish and change. They are better than a vibe. They are also self-graded. November 2023 showed what happens when the grader is a board without the staff. 2024–26 RSPs are an attempt to write the grader down. Read them as process claims. Do not read them as a CASP.

If you are a customer, ask which threshold would stop a *your-tenant* deploy, not which threshold would stop humanity. You want the first. The second is a charter problem.

## What the word cost

It made ordinary defect work feel small. Hallucination triage, prompt injection, a county power fight, a Colorado high-risk inventory — these are the 2026 job. They lose meetings to a slide about "the next capability jump." o1 (12 September 2024) and GPT-5 (7 August 2025) were sold as jumps. Some of that was real (test-time compute). Some of it was the destination word looking for a quarter.

It licensed postponement. "We will fix citations after the next model" is how you still have a citation bug. The next model is always next.

It confused customers. A procurement team asked for AGI-readiness and got a chatbot with a memory feature. Write the job. Do not write the destination.

## A working definition you can use without joining a church

For product work, throw the word out. Replace it with four questions:

1. What tasks does this checkpoint finish without a human?
2. What is the residual error on a frozen private set?
3. What actions may it take?
4. What happens when we pull it tonight?

If a vendor answers with a destination, they have not answered.

Scientific AI (AlphaFold) did not need the word. It needed CASP. Chat AI borrowed the word and skipped the CASP.

## 2026, five weeks after the Act's majority date

The EU calendar (2 August 2026) does not mention AGI. It mentions systems, risks, GPAI, transparency. US state law mentions decisions and disclosures. NIST mentions functions. The destination word is almost absent from the documents that can fine you. That is information.

We watch this space as people who have to live with the systems, not the destination. The systems are impressive. They are also unfinished in the ways this pack has been listing since the 2020 API.

## Opinion

AGI talk was a hiring and fundraising technology that leaked into product language. Capability still moved — few-shot, chat, vision, tools, reasoners, mice. Those moves are enough to fill a roadmap. They are not a finish line.

Write the four questions on the launch review. Leave the destination for the charter page. If the launch review cannot pass without the word, you are not launching. You are preaching.
