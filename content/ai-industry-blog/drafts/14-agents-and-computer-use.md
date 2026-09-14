---
title: "Agents and computer-use"
slug: agents-and-computer-use
meta_description: "22 October 2024: Claude looks at a screen and moves a mouse. January 2025: Operator. The loop is old. The permission is new."
tags: [agents, computer-use, operator, 2024, 2025]
era_start: 2024-10
citations:
  - "COMPUSE https://www.anthropic.com/news/3-5-models-and-computer-use"
  - "Anthropic research https://www.anthropic.com/research/developing-computer-use"
  - "OPERATOR https://openai.com/index/introducing-operator/"
  - "MARINER_IO https://blog.google/innovation-and-ai/technology/ai/io-2025-keynote/"
status: draft
voice_check: edited
voice_edited: 2026-09-14
figures:
  - swimlane-agent-orchestration
  - architecture-agent-tool-loop
  - flowchart-prompt-injection-defenses
---

On 22 October 2024, Anthropic announced that Claude 3.5 Sonnet could use a computer: look at a screenshot, move a cursor, click, type. The research note is plain. They trained on a small set of apps (a calculator, a text editor), kept the model off the open internet during that training for safety reasons, and watched it generalize to software it had not been taught as a tool API. The interface is the human interface.

That is the shift. For three years we made tools fit the model — JSON schemas, custom functions, tidy MCP-style catalogs. Computer-use makes the model fit the tools that already exist, including the ugly ones with no API.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/swimlane-agent-orchestration/fig-02-agent-swimlanes.svg" alt="Swimlane diagram of user, orchestrator, tools, and policy in agent workflows" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Agent products split planning, tool execution, and policy across coordinated lanes.</figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/architecture-agent-tool-loop/diagram.svg" alt="Conceptual agent plan-act-observe loop with tools" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> Agents plan, call tools, observe results, and iterate until a final answer.</figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/flowchart-prompt-injection-defenses/fig-02-prompt-injection.svg" alt="Layered prompt injection defenses from sanitization to human gates" width="1200" loading="lazy" />
  <figcaption><strong>Figure 3.</strong> Untrusted text in context requires isolation, tool limits, policy, and human gates — not one filter.</figcaption>
</figure>

<!-- ai-blog-figures:end -->

## Two product shapes, immediately

Anthropic shipped a **developer primitive**. You bring a machine (they published a Docker/VNC reference path). The model emits `computer`, `bash`, `text_editor` style actions. You execute them. You send the next screenshot. It is beta-flavored and documented like something that can wreck a desktop. Keep it off your daily driver. That warning is the most honest sentence in the 2024 agent literature.

OpenAI shipped **Operator** on 23 January 2025 as a ChatGPT-side, hosted-browser agent: a Computer-Using Agent (CUA) that clicks through the live web for a user, first to Pro subscribers. The action space is a remote browser OpenAI runs. The user can take over. There is less "bring your own VM," more "watch our VM shop for you."

Google's Project Mariner sat in the same browser-agent bucket. DeepMind showed the research prototype in the December 2024 Gemini wrap-up. At I/O on 20 May 2025, Pichai said Ultra subscribers could use it, that computer-use would come to the Gemini API, and that broader availability was "this summer." The standalone Mariner page later said the experiment shut down on 4 May 2026 and that the technology moved into other Google products (Gemini Agent, AI Mode — Google's wording). A research name that dies and a capability that gets absorbed is the normal Google pattern. Do not brief Mariner as a 2026 SKU. Brief the product that inherited the clicks, on the week you publish.

Same science-fiction screenshot. Different buyers. If you need to operate an internal thick client, you want the primitive and a VM you own. If you need to book a dentist, you want the hosted browser and a takeover button.

## The scores, handled with tongs

OSWorld and WebVoyager became the named benches. Launch numbers were low (Anthropic's early screenshot-only OSWorld figures were in the teens to low twenties; OpenAI's CUA paper claimed much higher WebVoyager). Later 2025–26 vendor posts advertised large jumps. Secondary blogs will quote Sonnet 4.5 at 61.4% OSWorld-Verified, Opus 4.7 at 78%, and so on. **[CITE NEEDED]** — those later figures should be pulled from the lab's own post or the bench site, dated, before they go on a customer slide. This draft will not launder a blog's table into a fact.

Even if the latest number is real, 80% on a public desktop suite is not "replace the employee." It is "sometimes finishes the scripted task." The unscripted task is your SAP skin from 2011.

## Why the loop still dies

Computer-use is ReAct with pixels. Drift, loops, and "I think I'm done" still happen. They happen with a mouse, so they happen to your CRM.

**Auth.** The agent will trip every bot wall, every SSO popup, every "confirm it's you." Operator's takeover flow is an admission of this. If you hide credentials in the VM, you now have a credentials-in-the-VM problem.

**Observability.** A function call is a log line. A click at (812, 343) is a shrug unless you store the screenshot and the reason. Store both and you have a privacy pile. Store neither and you cannot debug.

**Permissions.** A bash tool on a laptop is a junior with sudo. The only grown-up designs we have seen in public are: disposable VM, network egress allowlist, no prod credentials, human approval on payments and deletes.

**Cost.** A step is a screenshot plus a frontier-model forward pass. A 40-step booking is a small invoice. A 400-step confused loop is a large one. Timeouts are a feature.

## Frameworks, after the hangover

LangGraph, Microsoft's AutoGen, OpenAI's Swarm experiments, Anthropic's public computer-use reference, and a dozen "agent OS" pitches all tried to own the state machine. The useful ones make transitions explicit and testable. The rest hide a queue behind a metaphor.

SWE-agent and related 2024 academic loops (agent + repo + tests) are the coding-side cousin. They belong next to the Copilot piece. Computer-use is the same idea pointed at a GUI instead of `git`. If your coding agent already has a terminal, you do not need a mouse until the thing you must operate has no CLI. That is more often than vendors admit (legacy ERP) and less often than keynotes claim (everything).

## 2025–26: agents as a product word

Every vendor renamed chat "agents." Most of those products are RAG plus three tools. Fine. Call them that to customers if you must. Internally, keep the words straight:

- **Tool-using chat:** model picks a function, you run it.
- **Workflow agent:** a state machine you wrote, model fills slots.
- **Computer-use agent:** model drives a GUI.

GPT-5 (7 August 2025) was sold, on the developer side, for coding and agentic tasks. That is the first category plus the second. It is not automatically the third. Do not let a model card collapse them.

A procurement tell: if the vendor cannot show a recording of a *failed* computer-use run and how the system stopped, they have not operated it. Ask for the stop. Ask who holds the credentials during the run. If the answer is "the model," leave the meeting.

## Opinion

October 2024 mattered because it attacked the integration tax. You should not need a vendor API to file an expense. You may still want one, because GUIs are hostile and agents are clumsy.

Ship computer-use only where the alternative is a human already doing a miserable click path, and only inside a machine you can burn. The rest of your "agent platform" can stay JSON. JSON is underrated.
