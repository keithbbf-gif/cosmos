---
title: "The OpenAI board week"
slug: the-openai-board-week
meta_description: "17–21 November 2023: Altman fired, staff revolt, Microsoft, a new board. Governance as a product risk."
tags: [openai, governance, 2023, board, microsoft]
era_start: 2023-11
citations:
  - "OAI_BOARD https://openai.com/index/openai-announces-leadership-transition/"
  - "OAI_RETURN https://openai.com/index/sam-altman-returns-as-ceo-openai-has-a-new-initial-board/"
  - "GPT4 https://openai.com/index/gpt-4-research/"
status: draft
voice_check: human
figures:
  - industry-milestones-2020-2026
---

On 17 November 2023, OpenAI's nonprofit board posted that Sam Altman would "depart as CEO" and leave the board. Mira Murati was interim CEO. The sentence that mattered: the board had concluded he was "not consistently candid," and it no longer had confidence in his leadership. Ilya Sutskever, Adam D'Angelo, Tasha McCauley, and Helen Toner were the directors named on that post. Greg Brockman was stripped of the chair and then, within hours, left too.

By 21 November, Altman was CEO again, the board was being rebuilt, and Microsoft — already the capital and Azure partner — had spent a weekend looking like the lifeboat (Satya Nadella's public "we are on their side" and the offer to hire the team). The primary posts are the 17 November announcement and the 29 November "Sam Altman returns… new initial board" note. Almost everything else is reporting. Use it as reporting.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/industry-milestones-2020-2026/timeline.svg" alt="Public AI industry milestones from 2020 to 2026" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Selected milestones in research, products, and policy. <em>Not exhaustive.</em></figcaption>
</figure>

<!-- ai-blog-figures:end -->
## What the structure was

OpenAI, Inc., a 501(c)(3), controlled the capped-profit below it. The board's job, on paper, was the mission: AGI that "benefits all humanity," not shareholder value. That structure was the 2019 answer to "we took Microsoft's money and still want a nonprofit soul." November 2023 was the exam. The structure failed the exam in public.

The board had the legal right to fire the CEO. It did not have the staff, the investors, or the customers. A weekend of letters (the "we quit if he doesn't return" staff note, widely reported) made the power map obvious. Mission control without operational control is a blog post.

Sutskever's role — chief scientist, director, then a public apology for the board action — is documented in reporting more than in a primary paper. `[CITE NEEDED]` if you quote him. This draft will not invent dialogue.

## Why builders should care

Your vendor is a governance object. If a board can zero the CEO on a Friday, your API key is a political instrument. Microsoft's weekend offer was a reminder of who held the cluster. Enterprises that had just put Copilot in the tenant (GA 1 November 2023) spent Monday asking "what is our backup model." Some of them actually added one. Most of them waited and then forgot.

The "safety vs shipping" morality play that ate Twitter that week is a bad map. The board's stated reason was candor, not a specific model launch. Outsiders filled in Q* rumors and doomer scripts. We do not have the board minutes. Do not write as if we do. The *structural* fact is enough: a nonprofit board, a for-profit race, a cloud landlord, and a consumer product with a hundred million users cannot share a brain forever.

Later 2024–25 corporate reshuffles (more for-profit, more equity, secondary sales) are the sequel. `[CITE NEEDED]` the current Delaware filing before you print a capitalization table. The direction of travel is not in dispute: the 2019 structure is not the 2026 structure.

## The week, as a timeline you can defend

17 Nov: board post, Altman out, Murati interim. Brockman out as chair, then gone.

18–19 Nov: Emmett Shear (Twitch) briefly as interim, in reporting; Microsoft's "we will hire them" public posture; staff letter.

20–21 Nov: return path negotiated; Altman back; Toner and McCauley off the incoming board; a new initial board named in the 29 Nov post (Bret Taylor chair, Larry Summers, Adam D'Angelo staying, in that announcement).

Use those two OpenAI URLs. If you need the staff letter, treat it as a leaked document and say so. Do not invent a Q* capability. The rumor was a rumor.

## What did not change that week

GPT-4 still served. ChatGPT still answered. The model cards did not grow a spine because of a blog fight. Safety process and board composition are related and not identical. A new board can be worse or better at oversight. The weekend did not measure that. It measured who the staff would follow.

Anthropic's public story — a public benefit corporation, a long-term benefit trust — exists in this light. So does xAI's. So does every "we are not OpenAI" paragraph in a 2024 seed deck. Imitation is the sincere form of panic.

## Contracts that week actually changed

Enterprises asked for: a second-provider clause, data-handling on bankruptcy, a named status page, and whether a nonprofit board could still zero the CEO. Some vendors wrote "business continuity" paragraphs that were already in the DPA. A few customers actually dual-homed (OpenAI + Azure-hosted + Anthropic). Dual-home is the only clause that does not care about the charter.

If you are still single-homed in 2026 because "the board thing was a one-off," you are betting that a cap table fight will never again land on a Friday. That is a bold bet for a feature that files invoices.

## Opinion

November 2023 was the industry's first real vendor-risk drill that was not an outage. The lesson is dull and correct: have a second model, a contract that names data handling if the vendor implodes, and a written owner who can switch the router on a Monday.

Mission statements are not failover. Failover is failover.
