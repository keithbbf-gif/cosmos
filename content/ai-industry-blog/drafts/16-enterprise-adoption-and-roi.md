---
title: "Enterprise adoption and ROI skepticism"
slug: enterprise-adoption-and-roi
meta_description: "Microsoft 365 Copilot hit GA in November 2023 at $30/user/month. Usage climbed. Proven return did not automatically follow."
tags: [enterprise, roi, copilot, adoption, 2023, 2026]
era_start: 2023-11
citations:
  - "MS365COP https://www.microsoft.com/en-us/microsoft-365/blog/"
  - "MCK_AI https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai"
status: draft
voice_check: edited
figures:
  - callout-inference-cost-drivers
  - topology-open-vs-closed-deployment
---

On 1 November 2023, Microsoft 365 Copilot went generally available. The list price that stuck in every CFO chat was $30 per user per month on top of the existing Office seat. Ten thousand seats, $3.6 million a year, before anyone measured a minute saved. Jared Spataro's product story was conservative in one respect: the model drafts, the employee keeps the send button. That is the right shape. It is also why "we bought Copilot" is not the same sentence as "we changed the work."

Eighteen months later the pattern was boring enough to be true. Lots of experiments. Some daily habits (summarize the thread, first draft the deck). Few process redesigns. A smaller set of firms with a measured line on a P&L. McKinsey's annual *State of AI* surveys have documented the gap between "we use generative AI somewhere" and "we can show EBIT." Quote the latest PDF when you publish; do not quote a blog that quotes McKinsey. **[CITE NEEDED]** for any 2025 percentage you want to put in a customer memo.

A 2025 MIT-associated figure about most pilots showing no return made the trade-press rounds. Same rule: no primary PDF, no number in this draft.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/callout-inference-cost-drivers/callout-cost-drivers.svg" alt="Illustrative callout on inference cost drivers" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Inference bills track tokens, width, utilization, and region more than parameter counts alone. <em>Illustrative.</em></figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/topology-open-vs-closed-deployment/infographic-topology.svg" alt="Open-weight file deployment versus closed API topology" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> Open weights shift spend to your hardware; closed APIs shift it to vendor meters — controls can be shared.</figcaption>
</figure>

<!-- ai-blog-figures:end -->

## What enterprises actually bought

**Seats.** Copilot, ChatGPT Enterprise, Gemini for Workspace, Claude for Work. Easy to procure. Easy to forget. License dashboards full of people who opened it twice.

**Embedded assistants.** The useful ones sit in the system of record: the IDE, the ticket tool, the EHR sidecar, the CRM compose box. Distribution beats a portal.

**Platforms.** Azure OpenAI, Bedrock, Vertex, plus a vector store and a "gateway" that is usually an API key manager with a moral vocabulary. Necessary. Not ROI.

**Projects.** A 90-day RAG on the policy wiki. Half of these die when the champion changes jobs. The half that live have an owner, an eval set, and a clause about what happens when the model invents a policy.

## A concrete before/after, without fake numbers

Take a tier-1 support queue. Before: a human reads the ticket, searches Confluence, writes a reply. After: a model drafts from the five retrieved articles; the human edits and sends. The measurable objects are: handle time, escalation rate, customer come-back rate, and policy-invention rate (how often the draft cites a rule that is not in the five articles). If you only measure handle time, the model will learn to write shorter wrong letters.

Take a coding team. Before: PR cycle time, revert rate. After: Copilot-class gray text plus an agent that opens a draft PR. If revert rate rises, you did not save time. You borrowed it from next week.

Those two paragraphs are the whole method. Everything else is a dashboard color.

## Why the math is hard

If you cannot name the task, you cannot time it. "Productivity" is not a task. "Close this ticket type" is. The teams with numbers instrumented a before: median minutes, error rate, rework. Then they ran an after. Then they watched people spend the saved minutes on more tickets *or* on Slack. Both are outcomes. Only one shows up as headcount.

The $30 seat is the wrong unit if one analyst's Copilot-assisted model saves a day a week and 9,000 other seats generate emails that need more email. Average ROI across a tenant is how you talk yourself into a cancellation *or* a renewal without learning.

Shadow AI eats both. Employees already had ChatGPT on their phones in December 2022. The enterprise buy is often a legalization event, not a capability event. That still has value (data protection, logs). It is not a 10% headcount story.

## Failure modes that keep repeating

**No ground truth.** A sales assistant that does not have to win a deal can hallucinate a discount.

**Wrong workflow.** Forcing a chat sidebar onto a job that is a form. The form was correct.

**Eval theater.** A vendor POC scored by the vendor's prompts.

**Change management as an afterthought.** The model is the easy install. The permission to change the SOP is the hard one.

**Risk unpriced.** A single bad outbound mail or a leaked source file can erase a year of "minutes saved." If risk is not in the ROI model, the model is a brochure.

## What the 2026 buyers do differently

They pick three tasks, not thirty. They keep a holdout set of real artifacts. They pay for the boring integration (SSO, DLP, retention, human review on external sends). They refuse year-two seat expansions without usage *and* outcome. They treat agents (the computer-use kind) as a separate, smaller bet with a VM budget, not as the justification for the original Copilot invoice.

They also stop asking "what's our AI strategy" as if the answer were a model name. The answer is a list of jobs and a rule for when a human is still on the hook.

Procurement theater is its own cost. Six vendors, three POCs, a steering committee, no owner. A cheaper test: pick one task this month, instrument it, keep or kill. If you cannot do that, a platform RFP will not help you.

## Opinion

The 2023–26 enterprise wave did not fail. It got confused with a miracle. Copilot-class tools are real, and they are incremental unless you redesign the work they touch.

Pay for seats where the job is writing-shaped and the review is cheap. Pay for projects where you own the eval. Do not pay for a platform so you can tell the board you have a platform. The board can smell that now.
