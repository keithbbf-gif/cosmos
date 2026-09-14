# AI industry & research — draft calendar

Coverage window: **1 January 2020 → 14 September 2026**.
Eighteen pieces. Public record only. Drafts live in `drafts/`. None of this is scheduled to publish until a human editor and counsel pass it.

Soft voice: we watch this space. No product internals. See `NOVELTY_GUARDRAILS.md` and `STYLE_GUIDE.md`.

| # | Slug | Working title | Era start | Anchor fact | Status |
| --- | --- | --- | --- | --- | --- |
| 01 | `gpt-3-and-the-api-economy` | GPT-3 and the API economy | 2020-05 | Brown et al. arXiv 28 May 2020; API 11 June 2020 | draft |
| 02 | `scaling-laws-and-the-compute-race` | Scaling laws and the compute race | 2020-01 | Kaplan et al. 23 Jan 2020; Chinchilla Mar 2022 | draft |
| 03 | `from-copilot-to-coding-agents` | From Copilot to coding agents | 2021-06 | GitHub Copilot preview 29 June 2021; Codex paper July 2021 | draft |
| 04 | `diffusion-and-the-image-models` | Diffusion and the image models | 2021-01 | DALL·E Jan 2021; Stable Diffusion 22 Aug 2022 | draft |
| 05 | `the-chatgpt-moment` | The ChatGPT moment | 2022-11 | OpenAI "Introducing ChatGPT" 30 Nov 2022 | draft |
| 06 | `multimodal-models-arrive` | Multimodal models arrive | 2023-03 | GPT-4 14 Mar 2023; GPT-4o 13 May 2024 | draft |
| 07 | `open-weights-versus-closed` | Open weights versus closed | 2023-02 | Llama 24 Feb 2023; Llama 2 18 July 2023; Mistral 7B 27 Sept 2023 | draft |
| 08 | `rag-tools-and-early-agents` | RAG, tools, and early agents | 2020-05 | Lewis et al. RAG May 2020; ReAct Oct 2022 | draft |
| 09 | `the-evaluation-crisis` | The evaluation crisis | 2022-11 | HELM 2022; Chatbot Arena late Apr / 3 May 2023 write-up | draft |
| 10 | `safety-alignment-red-teaming` | Safety, alignment, red-teaming | 2022-03 | InstructGPT Mar 2022; Constitutional AI Dec 2022 | draft |
| 11 | `regulation-eu-ai-act-us-nist` | Regulation: EU AI Act, US orders, NIST RMF | 2023-01 | NIST AI RMF 26 Jan 2023; AI Act in force 1 Aug 2024; EO 14110 / 14179 | draft |
| 12 | `small-models-on-device` | Small models and on-device | 2023-12 | Phi-2 / Phi-3; Gemma; Llama 3.2 (25 Sept 2024) | draft |
| 13 | `voice-and-realtime-multimodal` | Voice and realtime multimodal | 2024-05 | GPT-4o 13 May 2024 demo and later voice mode | draft |
| 14 | `agents-and-computer-use` | Agents and computer-use | 2024-10 | Anthropic computer use 22 Oct 2024; OpenAI Operator Jan 2025 | draft |
| 15 | `synthetic-data-and-copyright` | Synthetic data and copyright fights | 2023-12 | *NYT v. OpenAI* filed 27 Dec 2023 | draft |
| 16 | `enterprise-adoption-and-roi` | Enterprise adoption and ROI skepticism | 2023-11 | Microsoft 365 Copilot GA Nov 2023 | draft |
| 17 | `deepfakes-and-media-authenticity` | Deepfakes and media authenticity | 2022 | C2PA specs; SynthID; 2024 election year | draft |
| 18 | `good-ai-product-design-2026` | What good AI product design looks like in 2026 | 2026-08 | AI Act majority application 2 Aug 2026 | draft |

## How to read the arc

2020–21 is the lab-to-API handoff: few-shot GPT-3, Kaplan's power laws, then code and pixels. Late 2022 is the consumer break (ChatGPT) built on work that was already public (InstructGPT, diffusion). 2023–24 is distribution: multimodal, open weights, RAG-as-default, arenas, and the first serious statutes. 2024–26 is action: voice, computer-use, reasoning models (o1, DeepSeek-R1, GPT-5 on 7 Aug 2025), and a hangover about evals, copyright, and ROI.

Each draft file has YAML (`title`, `slug`, `meta_description`, `tags`, `era_start`, `citations`, `status: draft`, `voice_check: human`).

## Suggested publish order

Ship 01–05 as a "how we got here" week. Then 06–10 (capabilities and measurement). Then 11–15 (law, efficiency, agents, data). Close with 16–18 (money, media, product). Do not dump all eighteen in one week.

## Out of scope

COSMOS, KMesh, MOTIF internals, patents, dockets, ModelRater / DailyScar / LMNator / BrokenTokn mechanisms. See `NOVELTY_GUARDRAILS.md`.
