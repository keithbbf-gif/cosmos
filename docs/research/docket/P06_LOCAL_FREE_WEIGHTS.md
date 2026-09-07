# P06 — Local free-weight plurality vs S-tier (low fixed cost)

**Kind:** method / system of deployment. **Status:** FILE. **Fee:** US provisional micro $65.

## What it is (in-tree)

2–3 **free-weight** models of **different families**, **isolated**, **locally deployed** on the **same machine**, **low fixed cost** (hardware + power, not per-token), versus one **S-tier API**, on **price and task performance**. Keith: *locally deployable for a low fixed cost with free weight models.* Easy to show because some weights are free and several fit one box. **Not yet a controlled bake-off.** OpenRouter “free” APIs are a **different** rail (rotator refused). **Phone ChatBot** named `:free` picker (DEFINE `DEFINE_CHATBOT_PHONE.md`) is that cloud rail — funnel, not this packet. P06 is on-box weights (later actual unlimited on the user's hardware). Combine with P03 (Porosity / different mistakes).

## Problem / scar

S-tier is a variable invoice (quota, key, billing). One brain, same porosity. Metered “free APIs” still run out. Local free weights + isolation + family-axis is how cost becomes a **cap you can name**.

## Written description

1. Select N=2 or 3 models whose **weights** are free/open and whose **families differ** (P03).
2. Deploy them **on-box** (llama.cpp / Ollama / vLLM class). Cost = machine + power.
3. Run them **isolated** (P02): no shared context mid-pass.
4. Dispose through one writer (P05). Gate on a live emit (P04).
5. Compare dollars and task outcome to a single S-tier API pass on the same task. Measurement is for conversion, not a number in this provisional.

## Already public

Swiss-cheese price/performance *hypothesis* in MOTIF.md and the unposted publish pack. Local multiplex as Keith’s 2026-09-07 measurement plan — **not** a public bake-off.

## Prior art to name (R2)

**Must cite — blocks slogans, not necessarily the combination:** Mixture-of-Agents arXiv:2406.04692 (open mix > GPT-4o AlpacaEval; **shares** layer context; cloud-scale open models); Blending Is All You Need arXiv:2401.02994 (2–3 small vs ChatGPT on **engagement**); FrugalGPT arXiv:2305.05176 (API **cascade**, up to 98% cost cut); RouteLLM arXiv:2406.18665; Hybrid LLM arXiv:2404.14618 (edge vs cloud, **one** model per query); More Agents arXiv:2402.05120 (same-model copies); Self-MoA arXiv:2502.00674 (**mixing can hurt**); LLM-Blender; PrivateGPT / GPT4All / LocalAI / OnPrem.LLM; llama.cpp `--models-preset`; Ollama multi-model; vLLM; Intelligence per Watt arXiv:2511.07885.

**Patents Legal must read (R2 close):** **US12524210B2** / WO2024238128A1 Microsoft (granted 2026-01-13) — hybrid **local GPT vs remote LLM** for coding COGS; **one** local + **one** remote, router predicts accept. **US20240311405A1** Google — pick **one** of N heterogeneous generative models (on-device small vs remote large). Citibank US12536406B2 gateway; Martian US12314825B2 prompt routing. On-device multi-LM **speculative decoding** (US12505335B2) **shares** the decode stream (anti-isolation).

**Products:** Ollama / llama.cpp multi-model = **tooling** (“run Ollama twice”). XDA 2026-08: Gemma + Qwen-Coder on one GPU, **user** switches tabs. AirgapAI: local multi-model, fixed license, **shared chat** (not E4).

**Gap:** this search found **no** paper/patent that measures **2–3 isolated local free-weights vs one S-tier API** on a coding task with **box dollars vs token dollars**. Combination E3+E4+E5+E6+E7: UNKNOWN as blocking (research, not a legal conclusion).

## What this is not

Not “run Ollama twice.” Not FrugalGPT (paid API cascade). Not Together MoA (shared layers, hosted). Not a fake bake-off number.

## Suggested independent idea

Family-diverse **free-weight** models, isolated, on one local machine at **fixed** cost, selected and gated as occupancy — versus one metered S-tier pass.
