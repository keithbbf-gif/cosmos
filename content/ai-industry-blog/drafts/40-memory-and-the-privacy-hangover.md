---
title: "Memory and the privacy hangover"
slug: memory-and-the-privacy-hangover
meta_description: "ChatGPT memory (Feb 2024) and every 'it remembers me' feature: useful, sticky, and a retention nightmare."
tags: [memory, privacy, chatgpt, personalization, 2024]
era_start: 2024-02
citations:
  - "CHATGPT_MEM https://openai.com/index/memory-and-new-controls-for-chatgpt/"
  - "CHATGPT2022 https://openai.com/index/chatgpt/"
  - "NIST_RMF https://doi.org/10.6028/NIST.AI.100-1"
status: draft
voice_check: human
---

On 13 February 2024, OpenAI posted *Memory and new controls for ChatGPT*. The model would remember facts you told it — a child's name, a preferred stack, a diet — and use them later, with a UI to see and delete. Users who had been pasting "remember that I like…" into every thread got a product. Privacy people got a retention graph. Both were correct.

Every lab shipped a cousin: "personalized Gems / GPTs," project folders, Claude's project knowledge, Gemini's saved info, the 2025–26 "it knows my life" features. The 2022 box was stateless on purpose (plus a thread). The 2024 box wanted to be a companion. Companions have GDPR problems.

## Two memories, often mashed

**Thread state.** The messages in the current conversation. Users understand this. Deleting the thread feels like deletion.

**Cross-session profile.** A distilled set of facts, embeddings, or raw notes that survive the thread. This is the 2024 object. Users do not understand what is in it, how it was inferred (not just what they typed), or which model versions can see it. Inferred memory — "we think you are a manager in Berlin" — is the one that should scare you. It is also the one that makes the product feel magic.

RAG-over-your-files is a third object (Google Drive, a repo, a mailbox). That is a corpus with permissions. Treat it like a corpus with permissions. Do not call it "memory" if you cannot list the documents.

## GDPR-shaped questions, in plain words

What is the legal basis for holding an inferred profile? How long? Can the person export it? Can they delete the inference, not just the raw message? If the profile is used to train, is that a new purpose? EU and UK ICO-class guidance on chatbots kept landing through 2024–26; pull the current note. US state privacy (CCPA/CPRA, and the growing list) treats "profiles" as a thing you have to admit. A "memory" toggle that does not hit the profile store is a dark pattern.

Work vs personal is the other axis. A ChatGPT Team workspace that inherits a personal memory is a mishap waiting for a screenshot. Isolation is the feature. Cute recall is the demo.

## Why it feels good and fails loud

A model that knows your stack writes a better function. A model that knows your ex writes a worse evening. A model that remembers a medical fact you typed once will someday complete a sentence in front of a person who was not supposed to hear it. Screen-share is a disclosure path. So is a work laptop that syncs a personal profile. So is a lawsuit's discovery.

The 2023 "do not paste secrets into ChatGPT" memo was about *inputs*. Memory is about *keeping* the inputs, then *reusing* them in a new context. That is a different DPA paragraph. Training-on-your-data is a third paragraph. Vendors who mash the three on a marketing page are doing it on purpose.

## Controls that are real

A list of stored facts the user can read. Delete-all that you can verify in logs. Per-workspace isolation (home vs work vs client). A default-off for inferred facts. A retention clock. No silent "we improved your profile from your emails" without a toggle that is actually off.

NIST AI RMF's "map" function is where you write "what personal data the assistant now holds." If you cannot fill that row, you do not have a memory feature. You have a leak with a cute name.

## What "delete" has to mean

A memory store is usually: raw snippets, embeddings, a distilled profile, caches, logs, backups, and the next model's training opt-in. A button that clears the UI list and leaves the embedding index is not delete. A button that clears the index and leaves 30-day logs is not delete if you told the user it was. GDPR-shaped deletion is a pipeline, not a toggle. Write the pipeline before the launch tweet.

Enterprise tenants need a second switch: "do not infer." Lots of companies want a project knowledge base (files they uploaded) and do *not* want a psychological profile of the intern who asked too many questions. If those are one store, you will ship the second by accident.

## Agents make this worse

A computer-use agent that "remembers how you book travel" will also remember the card flow. Operator (23 January 2025) and Claude's computer-use (22 October 2024) need a *session* memory that dies with the VM, and a *preference* memory that never includes secrets. If your design has one store, you will mix them. See the agents draft.

## Opinion

February 2024 was the month the chat box stopped being a notepad and started being a dossier. The dossier is useful. It is also the hangover.

Ship memory only with a list, a delete, and a wall between work and life. If you cannot afford the wall, do not afford the feature. A slightly dumber stateless model is a better partner than a clever one that will testify.
