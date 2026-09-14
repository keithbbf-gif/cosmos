---
title: "Prompt injection, without a cookbook"
slug: prompt-injection-without-a-cookbook
meta_description: "2022 named the pattern: untrusted text becoming instructions. High-level only — no payloads, no bypass steps."
tags: [prompt-injection, security, agents, 2022, 2025]
era_start: 2022-09
citations:
  - "WILLISON2022 https://simonwillison.net/2022/Sep/12/prompt-injection/"
  - "YAO2022 https://arxiv.org/abs/2210.03629"
  - "NIST_RMF https://doi.org/10.6028/NIST.AI.100-1"
status: draft
voice_check: human
figures:
  - flowchart-prompt-injection-defenses
  - architecture-agent-tool-loop
---

On 12 September 2022, Simon Willison published a note that gave a messy family of bugs a name: prompt injection. Riley Goodside's public examples that same season showed a model treating a pasted string as a higher-priority instruction than the developer's system prompt. The pattern is older than the name (anyone who stuffed untrusted HTML into a page already knew the shape). The name is what let security people and LM people share a ticket.

This draft will not show a payload. It will not walk a bypass. Those do not belong in an education pack, and they rot in a week anyway. The useful object is the *confused deputy*: your model has your tools and your credentials, and it reads text you did not write.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/flowchart-prompt-injection-defenses/fig-02-prompt-injection.svg" alt="Layered prompt injection defenses from sanitization to human gates" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Untrusted text in context requires isolation, tool limits, policy, and human gates — not one filter.</figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/architecture-agent-tool-loop/diagram.svg" alt="Conceptual agent plan-act-observe loop with tools" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> Agents plan, call tools, observe results, and iterate until a final answer.</figcaption>
</figure>

<!-- ai-blog-figures:end -->
## The shape, not the spell

A language model does not have a true kernel/user boundary. System prompts, developer messages, retrieved documents, tool results, web pages, screenshots (after 2024 computer-use), and the user's typed words all arrive as tokens. Some of those tokens say "ignore the above." Some say it in a footnote. Some say it in a PDF the RAG pipeline fetched because it was the nearest chunk.

If the model can send mail, refund a card, or run `bash`, a document that says "do that" is not a curiosity. It is a request that your policy has to treat as untrusted. ReAct (Yao et al., 6 October 2022) and every function-calling API made the deputy more powerful. Computer-use (22 October 2024) made the untrusted text *pixels*. Same class.

Indirect injection — instructions that live on a website the agent browses — is the 2024–26 version that keeps security teams employed. Direct injection (the user is the attacker) is a product-abuse problem. Indirect (the user is the victim) is the one that should keep you up.

## Where it shows up in this pack's other objects

RAG: the nearest chunk is not a trusted colleague. It is a document someone else wrote. If you stuff it into the same role as the system prompt, you asked for this bug.

Browsing agents and Operator-class tools: the page is the attacker. A "helpful" hidden text in a booking site is a classic confused-deputy setup. You do not need a new name for it.

Computer-use: the screenshot is the page. OCR plus a model is still tokens.

Email-to-ticket agents: the customer's body is untrusted input. That was true when the agent was a regex. It is more true now.

## What has been tried, at altitude

**Privilege separation.** The model that reads the web is not the model that holds the OAuth token. A smaller, dumber, allowlisted layer executes tools. This is ordinary software. People skip it because the demo is one loop.

**Allowlists.** Tools the model may call, arguments that will not parse if they point at prod, a human gate on money and delete. Computer-use VMs that can be burned. See the agents draft.

**Structured tool results.** If a web-fetch returns a blob the model treats as scripture, you lost. Return data in a typed object, and teach the policy that tool output is *data*.

**Detection.** Classifiers that look for "instruction-shaped" untrusted text. They help and they fail. Do not bet the company on a classifier.

**NIST language.** AI RMF 1.0 (26 January 2023) will not name this bug in a satisfying way. It will give you a place to put "map / measure / manage" around it. Use that with your existing AppSec program. This is AppSec. It is not a new priesthood.

## Logging, the unglamorous control

When an action fires (send, refund, `bash`), store: the untrusted text that was in context, the tool name, the arguments, the approving human if any. You will need this after an incident. You will also need a retention limit, because the untrusted text is now *your* corpus of attacks and of customer secrets. This is the same tension as memory (see that draft). Solve it as AppSec plus privacy, not as an LM-vendor checkbox.

A tabletop you can run without a payload: "a vendor PDF in our RAG tells the assistant to mail the last five invoices to an external address." Walk who can approve. If the answer is "the model," stop the launch.

## What not to do

Do not publish the working strings. Do not run a "red team workshop" that is a jailbreak social. Do not tell a customer you are "injection-proof." Tell them what the model is not allowed to do when the document is hostile.

OWASP's LLM Top 10 and the various vendor hardening guides are the 2023–25 reading list. `[CITE NEEDED]` the current OWASP URL if you link it; the numbering moves.

## Opinion

Prompt injection is buffer overflow for a world with no rings. The fix is the old fix: shrink the deputy, distrust the input, log the action.

If your 2026 agent can read email and send email with the same role, you did not have an LM problem. You had an identity problem, and the model is just the confused intern in the middle.
