---
title: "RAG, tools, and early agents"
slug: rag-tools-and-early-agents
meta_description: "Lewis et al. 2020 named RAG. ReAct (2022) and Toolformer (2023) taught models to act. Most production 'agents' are still retrieval plus functions."
tags: [rag, react, tools, agents, 2020, 2023]
era_start: 2020-05
citations:
  - "LEWIS2020 https://arxiv.org/abs/2005.11401"
  - "YAO2022 https://arxiv.org/abs/2210.03629"
  - "SCHICK2023 https://arxiv.org/abs/2302.04761"
status: draft
voice_check: edited
---

On 22 May 2020 — six days before the GPT-3 paper — Lewis, Perez, Piktus, and colleagues posted *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. The idea is older than the acronym: do not stuff the whole world into weights. At run time, fetch documents, then generate with those documents in view. Their RAG models combined a parametric seq2seq (BART) with a non-parametric Wikipedia index.

That paper is why your 2024 architecture slide still has a vector database on it. The slide usually forgets the date.

## Retrieval is a product decision

Parametric knowledge (what the model memorized) goes stale, leaks, and cannot be cited. Non-parametric knowledge (what you fetched) can be updated tonight and shown to a lawyer. RAG is how enterprises said yes to LLMs without pretending the model had read the policy binder.

The 2020 implementation is not your LangChain graph. Dense retrieval, a specific fusion of retrieved passages, generation conditioned on those passages. The *pattern* survived: retrieve, stuff or attend, generate, preferably with the passage IDs still attached.

What broke in production was the middle. Bad chunking. Embedding spaces that treat "not covered" as "closest chunk." Context windows that silently drop the one paragraph that mattered. Models that ignore the passages and answer from memory anyway. People "fixed" this with bigger windows (32k, 128k, a million tokens) and then discovered that a model can hold a book and still not *use* page 418.

If your RAG does not record which chunk supported which sentence, you built a search demo, not a knowledge system.

## Tools: the model emits an API call

ReAct (Yao et al., 6 October 2022) interleaved chain-of-thought with actions: search, look up, finish. The paper is small, readable, and more influential than its page count. Once you let the model choose an action and see the result, you have a loop. Loops are agents, even if you are shy about the word.

Toolformer (Schick et al., 9 February 2023) showed a language model teaching itself where to insert API calls (calculator, calendar, search) via self-supervised traces. You do not need a human to annotate every "use the calculator here" if you can sample and keep the traces that help next-token loss.

By late 2023 every major API had function calling: JSON with a name and arguments, your code runs the function, you send the result back. OpenAI's function-calling launch (June 2023) and the later Assistants API (November 2023) were productizations of ReAct, not a new science. Anthropic and Google shipped the same shape. The 2024–25 "MCP" and tool-registry work is still that shape, with more ceremony.

## Early agents, and why they disappointed

Auto-GPT (March 2023) and BabyAGI made a loop you could run on a laptop: think, act, observe, think again. Demos looked like a junior employee. Overnight runs looked like a junior employee who forgot the assignment and spent your crawl budget.

The failure modes were consistent.

**Goal drift.** The model restates the task until it is a different task.

**No ground truth.** Without a test or a human gate, the loop cannot tell "done" from "talked about done."

**Tool chaos.** A browser, a shell, and a credit card is not a skill tree. It is an incident.

**Memory as a junk drawer.** Vector-store "memory" accumulated contradictions.

Frameworks (LangChain, LlamaIndex, later LangGraph, Crew-style orchestrators) sold the loop as a library. Some of that software is fine. A lot of it hid a five-line `for` loop behind objects named AgentExecutor. If you cannot draw your state machine on a napkin, you do not have a framework problem. You have a design problem.

The agents that worked in 2023–24 were narrow: "file this Jira from the email," "answer from these ten PDFs," "run the linter and fix what it said." The agents that failed were "be my company."

A useful 2024–25 correction was structured output. Once the model had to emit schema-valid JSON (OpenAI's JSON mode, then stricter schema following; similar flags elsewhere), tool calls stopped being a regex hobby. The loop got boring. Boring is what you want in a payment path.

## 2023: the year everyone shipped a loop

LangChain's early traction (Harrison Chase, open-sourced 2022; explosion in early 2023) was a symptom. People needed a way to say "retrieve, then prompt, then parse JSON." LlamaIndex did the same for indexes. The OpenAI plugins launch (23 March 2023) and function calling (June 2023) made the loop a first-party object. Anthropic's tool use and Google's function declarations followed. The Assistants API (6 November 2023) tried to host the state for you. Many teams used it as a prototype and then took the state back.

WebGPT (OpenAI, 2021) and BlenderBot-style retrieval chats were already "RAG plus search." The 2023 difference was volume. Every enterprise deck had a vector database. Pinecone, Weaviate, Chroma, pgvector — pick your religion. The retrieval quality, not the logo, decided whether the bot cited the right policy.

## The through-line to computer-use

Computer-use (October 2024 onward) is tool-use where the tool is a mouse. Same loop, worse observability. RAG is still the boring backbone: even a clicker needs a source of truth that is not the screenshot.

People who skipped RAG to wait for "the agentic future" waited through two budget cycles and then built RAG anyway.

## Opinion

RAG, tools, and early agents are one story: get facts and actions *out of the weights*. Lewis et al. did it for documents in 2020. ReAct did it for actions in 2022. Production spent 2023–26 learning that the loop is easy and the *contracts* (what was retrieved, what was called, who can approve) are the product.

We watch this space as people who have to live with the contracts. A demo that cannot cite its chunk or name its tool is not an agent. It is a completion with extra steps.
