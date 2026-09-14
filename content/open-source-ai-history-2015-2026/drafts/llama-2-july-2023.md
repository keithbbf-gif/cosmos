---
title: Llama 2, 18 July 2023
slug: llama-2-july-2023
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 26
word_target: 600-1800
era: "2023"
stack:
  - llama
---

# Llama 2, 18 July 2023

Meta and Microsoft announced Llama 2 on 18 July 2023: 7B, 13B, 70B, base and Chat, with a Llama 2 Community License that Meta described as free for research and commercial use. Azure was a launch partner. The Hub cards were official. The acceptable-use policy was a PDF. The 700-million-user threshold — if you had more monthly actives than that, you needed a separate license from Meta — was the clause people either never read or never forgot.

This is the first Llama generation you could, in Meta’s telling, put in a product without being a researcher. It is also not Apache 2.0. OSI-shaped it is not. Useful it was. Ollama’s first tag was ten days earlier (`ollama-local-box`); the daemon spent the rest of the summer learning to say `ollama run llama2`.

## What changed from February

The name lost an L and gained a product manager. Chat variants were first-class. The license moved from non-commercial research to community commercial with conditions. The distribution moved from a form-plus-leak to a Hub gate you could click. Training details in the Llama 2 paper (Touvron et al., 2023) included more RLHF story than LLaMA-1. Chat versus base is a product decision that LLaMA-1 left to Alpaca (`alpaca-vicuna-weekend-finetunes`). Llama 2 shipped both.

Code Llama (24 August 2023) sat on this license: 7B, 13B, 34B, base / Python / Instruct. A code-specialized sibling is how a family becomes a platform. Qwen-Coder and Codestral are later cousins. July–August 2023 is when Meta’s open-weight line became a shelf instead of a paper.

Llama 2 Chat wanted a specific `[INST]` wrapping. Tools that forgot it made the model look worse than it was. The 2024 tokenizer chat-template file is the grown-up form of this leftover. If you evaluate a 2023 Chat model with a raw string, you are evaluating your wrapper. Write the wrapper down.

## The community license as a crate label

You may use and redistribute under conditions. You must include the license. You must not use the model for certain named harms. You must not use Llama outputs to train other models except under the terms they wrote — a clause later relaxed in spirit for Llama 3.1 (`llama-3-1-405b`). You must watch the user-count cap if you are a giant.

A startup with ten thousand users could ship. A consumer internet company the size of Meta’s peers had to pick up the phone. That is industrial policy in a PDF. Whether the cap is enforceable is a lawyer question. That it exists is a historian’s fact.

People still said “open source.” Debian and OSI voices said, publicly, that acceptable-use and user caps fail the definition. Both sentences happened. This series keeps both. Acceptable-use lists are cousins of RAIL (`licenses-that-are-not-open`). They fail OSI. They may still be why a company was willing to post 70B Chat weights.

## Why July, not February

The leak had already made 7B and 13B a hobbyist default. Alpaca and Vicuna had already taught the Hub to expect Chat. Microsoft wanted a model for Azure that was not OpenAI-only. Meta wanted credit for openness without giving away an Apache dump. July is those forces meeting.

Azure wanted a model that was not only OpenAI. Meta wanted distribution. The 18 July post is a partnership post. The paper is a Meta paper. Keep the author lists straight. Cloud availability is not a training credit.

Quality relative to the leaked originals was Meta’s claim and, on a lot of English benches, the public’s experience. This chapter does not reprint a table. It notes that a licensed Chat 70B became the serious self-host default for the rest of 2023, until Mixtral (`mixtral-open-moe`) and then Llama 3. Mistral 7B, two months later, was the Apache door (`mistral-7b-apache`). Lawyers who had blessed Llama 2 could stay. Lawyers who wanted OSI could leave.

## 2026 look

Llama 2 cards are still on the Hub. They are historical objects. New work moved to 3.x and 4. The license text is still the template later Llama licenses vary. If you inherit a 2023 startup’s model clause, you may still be in this PDF.

Read the 18 July announcement and the Community License in the same hour. The announcement says open. The license says when.

## Sources

Meta / Microsoft Llama 2 announcement, 18 July 2023. Llama 2 paper (Touvron et al.). Llama 2 Community License and Acceptable Use Policy. Code Llama announcement, 24 August 2023.

See: `llama-february-2023`, `licenses-that-are-not-open`, `mistral-7b-apache`, `llama-3-april-2024`.
