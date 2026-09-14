---
voice_check: human
title: "Chatbot Arena: two unnamed replies, one thumb"
slug: lmsys-chatbot-arena
kind: explainer
era: 2023–2024
tags: [lmsys, arena, lmarena, preference]
portrait: null
portrait_status: none
---

In May 2023 a site invited anyone with a browser to talk to two unnamed chatbots and pick a winner. The people who built it were around LMSYS and UC Berkeley Sky Lab. Wei-Lin Chiang, Lianmin Zheng, Ying Sheng, Anastasios Angelopoulos, Tianle Li, Dacheng Li, Banghua Zhu, Hao Zhang, Michael Jordan, Joseph Gonzalez, and Ion Stoica wrote the method up as “Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference” (ICML 2024; preprint arXiv:2403.04132). The paper’s URL is chat.lmsys.org. The later home is lmarena.ai. The scientific object is the pairwise vote.

## How a fight works

You type a prompt. Two models, hidden behind aliases, answer. You vote for A, or B, or a tie, or you skip. The prompt is yours. It is not an item from a committee. That is the whole idea, and the whole sampling problem.

The ranking is not a raw win rate. The paper describes a Bradley-Terry style model: a latent strength for each system, estimated from pairwise outcomes, with the usual statistical care about uncertainty. People still say “Elo” in the hallway. The hallway is close enough for gossip and not close enough for a methods section. The important sentence is: a coefficient is not a percentage of questions correct.

## What the 2024 paper claimed

At writing, the authors reported more than 240,000 votes, enough prompt diversity to discriminate models, and meaningful agreement between crowd votes and expert raters. Those claims are dated. The vote count is a historical snapshot, not a live widget. Do not update it from memory in this draft.

They also claimed the thing the industry wanted: an open preference leaderboard that was not a company’s private side-by-side. Labs began to quote it. Journalists treated a rank as a review. The site became, for a while, the closest thing the field had to a public weather service for chat.

## The rename, without mythology

LMSYS is a research collective (Vicuna, SGLang, Arena, and other projects). In a 20 September 2024 post they announced that Chatbot Arena would live at lmarena.ai, “graduate and stand on its own,” and remain a partner. Later public branding also says LMArena. If you are citing the ICML paper, use the paper’s name. If you are describing the site a reader will find tomorrow, name the URL change. Do not invent a corporate novel around it.

## What a thumb measures

Preference. Not truth. Not legal safety. Not pass@1. A model that writes a warmer wrong answer can beat a colder right one. A model that refuses a request the user wanted will lose that fight. A model that is funny will collect votes from people who came to be entertained. None of that is invisible in the paper’s framing. It becomes invisible in a screenshot of a table.

The crowd is a filter. English-heavy, internet-heavy, hobby-heavy, sometimes adversarial. A workplace assistant that is excellent on internal policy and dull in a browser will look worse than it is. A model tuned to win this room will look better than your procurement committee may want.

Identity leakage is a known sport. Models have tells — cadence, refusal boilerplate, a favorite list format. Some voters try to unblind the fight. Some models seem, to a suspicious reader, to have been tuned for the room. The paper cannot legislate that away. A public room is a public incentive.

## Related instruments

**MT-Bench** (Zheng et al., NeurIPS 2023) is a fixed set of multi-turn questions with a model judge. It is a file that dreams of being a room.

**AlpacaEval** is another preference-shaped automatic ranking. Cheap, judge-dependent.

**Arena-Hard** (later LMSYS work) tries to keep the preference flavor while using a harder, more controlled prompt set. Different instrument, same family.

A static exam (MMLU) and this room should not be averaged. They disagree on purpose.

## How to read an Arena rank

Read it as: among the people who showed up, with the prompts they brought, under this week’s model list and this week’s statistical pipeline, system A was preferred to system B with such-and-such uncertainty. That sentence is too long for a tweet. It is the length of the truth.

If a vendor says “#1 on Arena,” ask: which category, which date, which style control, was the model anonymous, and did they also report a file-based suite? A thumb is data. A thumb is not a degree.
