---
title: Llama 3, 18 April 2024
slug: llama-3-april-2024
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 30
word_target: 600-1800
era: "2024"
stack:
  - llama
---

# Llama 3, 18 April 2024

Meta’s Llama 3 post that Thursday released 8B and 70B models, base and instruction-tuned, trained on 8,192-token sequences, under a Llama 3 Community License in the same family as Llama 2’s. The model card is dated 18 April 2024. Meta called the pair the most capable openly available LLM they had shipped and, in the same post, “the best open source models of their class.” The Hub cards were ready. The 400B-class sibling was promised and not in the April dump.

The card’s table is the object you should pin: 15T+ pretraining tokens from “publicly available online data,” grouped-query attention on both sizes, knowledge cutoffs of March 2023 (8B) and December 2023 (70B), more than 10 million human-annotated fine-tune examples, no Meta user data in the mix they describe. The post adds that the pretraining set is seven times Llama 2’s and includes four times more code, with over 5 percent high-quality non-English text covering 30+ languages — and then says they do not expect those languages to match English. That last clause is the honest one.

This is the generation that made “self-host a serious assistant” an 8B sentence as well as a 70B sentence. Mistral 7B had already made 7B respectable (`mistral-7b-apache`). Llama 3 8B made the Meta line respectable again at the small end. 70B remained the serious self-host. The promised 400B is a July story (`llama-3-1-405b`).

## Tokenizer, GQA, and the silent migration

Llama 3 uses a tokenizer with a 128K-class vocabulary. The later herd paper (arXiv:2407.21783) describes it as about 100K tokens from OpenAI’s tiktoken plus 28K added for non-English, and gives a compression improvement on a sample of English from 3.17 to 3.94 characters per token versus Llama 2. Old Llama-2 adapters do not drop in. Old `[INST]` wraps misbehave. The adapter era (`peft-lora-adapters`) had to start over. That is a real cost for shops. It is also how you know a generation happened. “Llama” is not a tokenizer name. Write the generation on the card.

GQA on the 8B, not only the 70B, is why the small card was cheap enough to become the default local assistant once GGUF quantizers caught up. Llama 2 had reserved GQA for the 70B. The 8B of April is a different small model than the 7B of July 2023.

## What April did not include

405B. 128K context. Vision. Those arrived as 3.1 (23 July) and 3.2 (25 September). A history that flattens “Llama 3” into one day is a keynote. The family is a year: 3, 3.1, 3.2, 3.3 (6 December 2024, a 70B instruct Meta described as near-405B quality at lower serve cost).

Llama 3.2 added 11B and 90B vision models and 1B / 3B text models for edge, still at 128K after 3.1’s context jump. The 1B and 3B cards are the first time this series can say “Meta shipped a phone-sized Llama” without meaning TFLite. They sit next to Gemma and Phi (`gemma-phi-small-weights`) in the small-weights drawer. Llama 3.3 70B was an instruct-only text model, a cost play. Edge and vision are how a family tries to be a platform without waiting for Llama 4’s MoE.

People who say “Llama 3 has 128K” mean 3.1. The family name hid a 16× jump. RAG systems that assumed 8K and then silently took 3.1 changed their economics. Write the minor version in the RAG config. This is the same lesson as the tokenizer change, applied to length.

## License continuity

Community license, acceptable use, a large-user threshold. Meta still said “open source” in prose. The instrument was still not Apache. Mistral’s 7B, sitting on Apache 2.0 since September 2023, remained the cleaner crate for lawyers who only know OSI. Llama 3 remained the crate a lot of engineers preferred on English benches. Lawyers who had blessed Llama 2 could bless 3 with a redline. Lawyers who had refused 2 still refused 3. Quality and license stayed a trade.

## 2026 look

Llama 3.x is still in production stacks that have not taken 4’s MoE serving cost. GGUF names still say `Llama-3.1-8B-Instruct-Q4_K_M`. The April 18 post is the family door. The useful look is the card date, not the major number. A shop that says “we use Llama 3” has said almost nothing. Say the minor, the size, and the date of the card.

Read the 18 April post, the model card table, then the 3.1 post, then the 3.2 post. Four objects. One brand.

## Sources

Meta AI, “Introducing Meta Llama 3,” 18 April 2024. Llama 3 Community License. meta-llama/llama3 `MODEL_CARD.md` (15T+, GQA, cutoffs). Grattafiori et al., “The Llama 3 Herd of Models,” arXiv:2407.21783 (tokenizer note). Meta, Llama 3.2, 25 September 2024. Llama-3.3-70B-Instruct model card, 6 December 2024.

See: `llama-2-july-2023`, `llama-3-1-405b`, `mistral-7b-apache`, `gemma-phi-small-weights`.
