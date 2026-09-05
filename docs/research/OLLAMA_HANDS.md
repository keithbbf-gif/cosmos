# OLLAMA HANDS — G46 scout return (local + cloud open-model runtime)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim except where a COSMOS artifact is named.
**No COSMOS core code was edited.** Maker-docs sweep (DHx assignment log): each maker's hands → `docs/research/<MAKER>_HANDS.md`.

**Already on the mesh (do not re-add as "new"):** `docs/MESH_ADDITIONS.md` row 1 named Ollama as the **#1 candidate** (CLI + local HTTP, OpenAI-chat-compatible, `link_id="ollama-local"`, **UNVERIFIED** against a live install on this machine). `docs/MESH_ADDITIONS_grok.md` row 16 named Ollama + `mcp-ollama-python` as a fifth spend-gate rail with cost=0. Aider HANDS and browser-use HANDS already point at this rail. This file inventories **every official hand**, including Cloud (quota) and publish (signin), so COW can decide.

**Filter:** a surface is a HAND only if COSMOS can **do** something with it (generate, chat, embed, pull, create, serve, tool-call, launch a coding agent, list/ps, copy/delete, push). Chat-only desktop chrome is out unless it is the DOM fallback (signin / settings / library).

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks (local `ApiRail`, coding-agent launch, RAG embeddings, vendor-plural without a bill). Equal power, cheaper wins. Cloud quota sits **below** local even when the hosted model is larger — local cannot run out of credit (canon: nothing that can run out).

**What Ollama is (one sentence):** a local (and optional-cloud) open-model runtime that serves llama.cpp-backed models over a native REST API on `http://localhost:11434`, plus OpenAI- and Anthropic-compatible shims, a CLI (`run`/`pull`/`create`/`serve`/`launch`), and a Modelfile for customizing weights, templates, adapters, and parameters. MIT license. Official home: [ollama.com](https://ollama.com). Docs: [docs.ollama.com](https://docs.ollama.com). Repo: [github.com/ollama/ollama](https://github.com/ollama/ollama).

**Repo in play:** `keithbbf-gif/cosmos`. Ollama is a **native sidecar worker** (or Docker), never a second ledger writer. Inference stays in an attempt-private workspace or on the local daemon; fenced commit still owns the live tree. Artifacts (embeddings, structured JSON, generated text) go into the content-addressed store; the ledger holds the pointer.

---

## Official documentation URLs (fetched 2026-08-25)

These are the real vendor pages this scout used. Prefer the machine indexes over blog roundups.

| what | URL |
|------|-----|
| **Docs machine index** | https://docs.ollama.com/llms.txt |
| **Full machine dump** | https://docs.ollama.com/llms-full.txt |
| Human docs home | https://docs.ollama.com |
| Quickstart | https://docs.ollama.com/quickstart |
| **API introduction** | https://docs.ollama.com/api/introduction |
| **OpenAPI (JSON)** | https://docs.ollama.com/api-reference/openapi.json |
| **OpenAPI (YAML)** | https://docs.ollama.com/openapi.yaml |
| **GitHub API.md (legacy, still complete)** | https://github.com/ollama/ollama/blob/main/docs/api.md · raw: https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md |
| Authentication | https://docs.ollama.com/api/authentication |
| Streaming | https://docs.ollama.com/api/streaming |
| Usage metrics | https://docs.ollama.com/api/usage |
| Errors | https://docs.ollama.com/api/errors |
| **OpenAI compatibility** | https://docs.ollama.com/api/openai-compatibility |
| **Anthropic compatibility** | https://docs.ollama.com/api/anthropic-compatibility |
| `POST /api/generate` | https://docs.ollama.com/api/generate |
| `POST /api/chat` | https://docs.ollama.com/api/chat |
| `POST /api/embed` | https://docs.ollama.com/api/embed |
| `GET /api/tags` | https://docs.ollama.com/api/tags |
| `GET /api/ps` | https://docs.ollama.com/api/ps |
| `POST /api/create` | https://docs.ollama.com/api/create |
| `POST /api/copy` | https://docs.ollama.com/api/copy |
| `POST /api/pull` | https://docs.ollama.com/api/pull |
| `POST /api/push` | https://docs.ollama.com/api/push |
| `DELETE /api/delete` | https://docs.ollama.com/api/delete |
| `POST /api/show` | https://docs.ollama.com/api-reference/show-model-details |
| `GET /api/version` | https://docs.ollama.com/api-reference/get-version |
| **CLI reference** | https://docs.ollama.com/cli |
| **Modelfile** | https://docs.ollama.com/modelfile |
| Import (GGUF / Safetensors / adapters) | https://docs.ollama.com/import |
| Context length | https://docs.ollama.com/context-length |
| **Tool calling** | https://docs.ollama.com/capabilities/tool-calling |
| Embeddings capability | https://docs.ollama.com/capabilities/embeddings |
| Structured outputs | https://docs.ollama.com/capabilities/structured-outputs |
| Thinking | https://docs.ollama.com/capabilities/thinking |
| Vision | https://docs.ollama.com/capabilities/vision |
| Streaming (capability) | https://docs.ollama.com/capabilities/streaming |
| Web search / fetch | https://docs.ollama.com/capabilities/web-search |
| **Hardware / GPU** | https://docs.ollama.com/gpu |
| Windows | https://docs.ollama.com/windows |
| Linux | https://docs.ollama.com/linux |
| macOS | https://docs.ollama.com/macos |
| Docker | https://docs.ollama.com/docker |
| FAQ | https://docs.ollama.com/faq |
| Cloud models | https://docs.ollama.com/cloud |
| Claude Code integration | https://docs.ollama.com/integrations/claude-code |
| **GitHub README** | https://github.com/ollama/ollama/blob/main/README.md |
| **Model library** | https://ollama.com/library |
| Model search | https://ollama.com/search |
| Tools-capable models | https://ollama.com/search?c=tool |
| Thinking models | https://ollama.com/search?c=thinking |
| Cloud models | https://ollama.com/search?c=cloud |
| **Pricing** | https://ollama.com/pricing |
| Download | https://ollama.com/download |
| API keys | https://ollama.com/settings/keys |
| Python SDK | https://github.com/ollama/ollama-python |
| JavaScript SDK | https://github.com/ollama/ollama-js |
| Tool-support blog (2024-07-25) | https://ollama.com/blog/tool-support |
| OpenAI-compat blog (2024-02-08) | https://ollama.com/blog/openai-compatibility |
| `ollama launch` blog | https://ollama.com/blog/launch |

GitHub `docs/api.md` still documents **`POST /api/embeddings`** (singular `prompt`/`embedding`) as **superseded** by `POST /api/embed`. Current Mintlify docs only list `/api/embed`. COSMOS should call `/api/embed` (or OpenAI `/v1/embeddings`). Keep `/api/embeddings` only for old clients.

---

## How COSMOS reaches Ollama (reach column, one pattern)

Core stays sole ledger writer. Ollama is reached as:

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Local REST (preferred)** | `POST http://127.0.0.1:11434/api/chat` (native) or `/v1/chat/completions` (OpenAI shim). No key. | Default. Zero per-token cost. Matches "nothing that can run out." |
| **B. OpenAI-compat drop-in** | Existing COSMOS `ApiRail` / OpenAI SDK with `base_url=http://127.0.0.1:11434/v1` and dummy `api_key=ollama`. | Fastest path onto the Dispatcher: same shape as `oa-api` / `sgh-api`. |
| **C. Anthropic-compat** | `ANTHROPIC_BASE_URL=http://localhost:11434` + `ANTHROPIC_AUTH_TOKEN=ollama` → Claude Code / Messages SDK against a local model. Or `ollama launch claude`. | Coding-agent lane without burning F5 / Claude Code weekly quota. |
| **D. Native CLI** | `ollama run` / `pull` / `create` / `serve` / `ps` / `stop` / `launch` inside an attempt-private workspace. | Pull/create/serve/inventory. Headless jobs: `ollama run <model> "<prompt>"`. |
| **E. Official Python/JS SDK** | `pip install ollama` / `npm i ollama`. `chat()`, `embed()`, `pull()`, tools as Python functions. | In-process workers that want typed tool-calling loops. |
| **F. Docker sidecar** | `docker run -d -p 11434:11434 -v ollama:/root/.ollama [--gpus=all] ollama/ollama` | Isolated daemon; GPU via NVIDIA Container Toolkit / ROCm tag. |
| **G. Cloud (quota)** | Local daemon with `*:cloud` models after `ollama signin`, **or** `https://ollama.com/api` with `Authorization: Bearer $OLLAMA_API_KEY`. | Only when local VRAM cannot hold the model. Can run out. Spend-gate it. |
| **H. DOM** | ollama.com/download, /settings/keys, /library, signin in the Windows tray app. | First install, key mint, library browse. |

Keith owns credentials. Store `OLLAMA_API_KEY` under `live/config/` (git-ignored) if Cloud is used. Never hard-code. Never print a key in full. Fenced commit still gates any tree write.

**Windows install (this machine):** `irm https://ollama.com/install.ps1 | iex` or [OllamaSetup.exe](https://ollama.com/download/OllamaSetup.exe). Native app; API on `http://localhost:11434`. Standalone zip `ollama-windows-amd64.zip` + optional `…-rocm.zip` / `…-mlx.zip` for service/NSSM embed. Default model store: `C:\Users\<user>\.ollama\models` (override `OLLAMA_MODELS`). Logs: `%LOCALAPPDATA%\Ollama`. Binaries: `%LOCALAPPDATA%\Programs\Ollama`.

---

## Auth primer (all rows inherit this unless overridden)

| surface | auth | COSMOS note |
|---------|------|-------------|
| Local API `http://localhost:11434` | **None.** OpenAPI `security: []`. | Default. Bind stays `127.0.0.1`. Do **not** set `OLLAMA_HOST=0.0.0.0` without a proxy + origin allowlist. |
| OpenAI shim `/v1/*` | Dummy `api_key='ollama'` (required by client libs, **ignored** by server). | Same as local. |
| Anthropic shim `/v1/messages` | Dummy `x-api-key: ollama` / `ANTHROPIC_AUTH_TOKEN=ollama`. `anthropic-version` accepted, unused. | Same as local. |
| Cloud via local daemon (`model:cloud`) | `ollama signin` — daemon attaches identity automatically. Public key at `C:\Users\<user>\.ollama\id_ed25519.pub`. | No Bearer on localhost calls. |
| Cloud direct `https://ollama.com/api` | `Authorization: Bearer $OLLAMA_API_KEY` (mint at [settings/keys](https://ollama.com/settings/keys)). Keys do not expire; revocable. | Required. Also for `/api/web_search` and `/api/web_fetch`. |
| Push / private pull | Sign-in **or** API key. Model name `user/model`. | Publishing is optional; COSMOS does not need it for inference. |
| CORS | Default origins `127.0.0.1` and `0.0.0.0`. Extra via `OLLAMA_ORIGINS`. | KDash-from-file or browser extensions need this if they call the daemon. |

Local-only lock: `OLLAMA_NO_CLOUD=1` or `~/.ollama/server.json` `{"disable_ollama_cloud": true}`. Logs then show `Ollama cloud disabled: true`. Prefer this for the COSMOS rail until Keith opts into Cloud.

---

## Cost floor (local vs Cloud — do not conflate)

Two wallets. Mixing them is how a "free local rail" quietly starts burning a Pro seat.

| Wallet | What official docs say | COSMOS note |
|--------|------------------------|-------------|
| **Local inference** | "Running models on your own hardware is always unlimited." [Pricing](https://ollama.com/pricing). MIT. No key, no cap, no per-token bill. | **$0.** Electricity + disk + VRAM. This is the ranked-first rail. |
| **Public library pulls** | Unlimited public models on Free. | Disk only. Models are tens–hundreds of GB. |
| **Ollama Cloud Free** | $0. Light cloud usage. 1 concurrent cloud model. Session limits every **5 hours** + weekly limits every **7 days**. Access cloud models. | Overflow when VRAM cannot hold the model. **Can run out.** |
| **Cloud Pro** | **$20/mo** (or $200/yr). 50× Free usage. 3 concurrent cloud models. Private-model upload/share. Extra usage balance optional. | Real money. Spend-gate. |
| **Cloud Max** | **$100/mo**. 5× Pro. 10 concurrent. **New sign-ups paused** (capacity). Existing Max kept. | Do not plan on this. |
| **Team** | **$25/seat/mo**, 5-seat min ($125). Waitlist. Extra usage at model token rate. | Out of scope until Keith asks. |
| **Enterprise** | Custom. | Out of scope. |
| **Web search / fetch** | Requires a free ollama.com account + API key. Usage against the Cloud plan, not local. | Prefer Playwright / Firecrawl / local fetch unless Keith wants Ollama's agent loop. |
| **Structured outputs on Cloud** | Official note: "Ollama's Cloud currently does not support structured outputs." | Keep `format`/JSON-schema on **local** models. |

Cloud usage is **not** a fixed token cap: models have a **usage level** 1–4 (e.g. `gpt-oss:20b` = 1, `deepseek-v4-pro` = 4) displayed on the model page. Limits reset on a 5-hour window and a 7-day window.

---

## Hardware (what actually runs here)

Official [GPU](https://docs.ollama.com/gpu) + [Windows](https://docs.ollama.com/windows) + [context-length](https://docs.ollama.com/context-length).

**OS:** Windows 10 22H2+ (Home or Pro). Native app, NVIDIA + AMD Radeon.

**NVIDIA:** compute capability **5.0+**, driver **550+** (CC 5.0–6.2 need **570+**). Windows docs also say NVIDIA **551.61+**. Covers GTX 900 / 10 / 16, RTX 20/30/40/50, Tesla/Quadro/professional (T4, A100, H100, L40, Blackwell PRO). Select GPUs with `CUDA_VISIBLE_DEVICES`. Invalid ID (`-1`) forces CPU.

**AMD Windows:** ROCm v7 / HIP7 **or** Vulkan (Vulkan is default fallback). Official ROCm Windows cards: RX 7900 XTX/XT/GRE, 7800 XT, 7700 XT, 7600 XT/7600, Radeon PRO W7900–W7500. RDNA2 / RX 6000 (incl. 6800-class) often **lack ROCm v7** on current Windows drivers — **use Vulkan**. Mixed iGPU/dGPU: `GGML_VK_VISIBLE_DEVICES=<discrete index>`. Disable Vulkan: `OLLAMA_VULKAN=0` or `GGML_VK_VISIBLE_DEVICES=-1`.

**Apple:** Metal. **Linux AMD:** ROCm v7 table includes RX 6000/7000/9000, Instinct MI100–MI350X, Ryzen AI. `HSA_OVERRIDE_GFX_VERSION` for close-but-unsupported GFX.

**CPU:** always works; slow. `ollama ps` `PROCESSOR` column: `100% GPU` / `100% CPU` / split.

**Context-length defaults (VRAM):**

| VRAM | default `num_ctx` |
|------|-------------------|
| < 24 GiB | 4k |
| 24–48 GiB | 32k |
| ≥ 48 GiB | 256k |

Coding / agents / web-search: official recommendation **≥ 64k**. Cloud models run at **max** context. Override: `OLLAMA_CONTEXT_LENGTH=64000`, API `options.num_ctx`, CLI `/set parameter num_ctx`, or a Modelfile `PARAMETER num_ctx`. OpenAI shim **cannot** set context — bake it into a custom model via Modelfile.

**FAQ vs context-length.md:** FAQ still says "default 4096 tokens." Context-length.md is the VRAM-scaled table above. Treat the VRAM table as current; always set `num_ctx` explicitly for agent jobs.

**Keep-alive:** default **5 minutes**. `keep_alive`: duration (`10m`/`24h`), seconds, `-1` (forever), `0` (unload now). Env `OLLAMA_KEEP_ALIVE`. Preload: `POST /api/generate {"model":"…"}` or `ollama run llama3.2 ""`.

**Concurrency:** `OLLAMA_MAX_LOADED_MODELS` (default 3× GPU count), `OLLAMA_NUM_PARALLEL` (default 1; RAM scales by parallel × context), `OLLAMA_MAX_QUEUE` (default 512; overflow → **503**). Parallel requests multiply context (2k ctx × 4 parallel = 8k). Multi-GPU: fit-on-one preferred; else spread.

**Flash Attention / KV cache:** auto when backend supports. Force `OLLAMA_FLASH_ATTENTION=1`. KV quant `OLLAMA_KV_CACHE_TYPE=f16|q8_0|q4_0` (global). `q8_0` ≈ half f16 memory, small quality loss.

**Disk:** installer ≥ 4 GB. Models: tens to hundreds of GB. Change store with `OLLAMA_MODELS`.

**Rule of thumb (Q4_K_M, official callouts + library sizes):**

| class | example | typical weight | VRAM to run well |
|-------|---------|----------------|------------------|
| Tiny embed | `all-minilm`, `embeddinggemma` (300M) | < 1 GB | CPU fine |
| 1–3B | `llama3.2:3b`, `gemma4 e2b/e4b` | 2–4 GB | 8 GB GPU or CPU |
| 7–8B | `qwen3:8b`, `mistral`, `gemma4` 8B-class | ~5 GB | 8–12 GB |
| 14B | `phi4`, `qwen2.5:14b` | ~9 GB | 12–16 GB |
| ~20–32B | `gpt-oss:20b`, `qwen3-coder` **30B** | ~12–20 GB | **≥ 24 GB** (official: qwen3-coder 30B "at least 24GB of VRAM"; more for long context) |
| Coding 30B flash | `glm-4.7-flash` | — | **~23 GB VRAM at 64k ctx** ([launch blog](https://ollama.com/blog/launch)) |
| 70B | `llama3.3:70b`, `llama3.1:70b` | ~40 GB | 48 GB+ or CPU offload (slow) |
| 120B+ / MoE huge | `gpt-oss:120b`, `qwen3-coder:480b`, DeepSeek 671B | does not fit a desktop | **Cloud** (`:cloud` tag) |

`ollama ps` is ground truth for whether a model is on GPU.

---

## Model library (free local, $0/token)

Library: [ollama.com/library](https://ollama.com/library). Pull: `ollama pull <name>[:tag]`. Names are `model:tag` (`latest` if omitted). Namespaces: `user/model`.

**COSMOS-relevant picks (local first).** Pull counts from library 2026-08-25 — popularity, not quality.

| model | sizes / tags | caps | why COSMOS |
|-------|--------------|------|------------|
| **gemma4** | e2b, e4b, 12b, 26b, 31b + cloud | vision, tools, thinking, audio | Current default in official examples. Multimodal + tools. |
| **qwen3** / **qwen3.5** / **qwen3.6** | 0.6b–235b / 0.8b–122b / 27b–35b | tools, thinking, vision (3.5+) | Tool-calling examples in official docs (`qwen3`). Strong local agent. |
| **qwen3-coder** | 30b, 480b | tools | Official Claude-Code local rec. 30B needs **≥24 GB VRAM**. |
| **gpt-oss** | 20b, 120b + cloud | tools, thinking | OpenAI open-weight. 20B is the practical local coding/general model. Think levels `low/medium/high` only (bool ignored). |
| **glm-4.7-flash** | (30B-class) | tools, thinking | Official `ollama launch` coding rec; ~23 GB VRAM @ 64k. |
| **llama3.2** | 1b, 3b | tools | Tiny, tool-capable. Good smoke-test rail. |
| **llama3.1** | 8b, 70b, 405b | tools | 8B fits 8–12 GB; 70B needs big VRAM. |
| **deepseek-r1** | 1.5b–671b | tools, thinking | Reasoning distill. Small tags are local; 671b is Cloud/VRAM-monster. |
| **mistral** / **mistral-small** / **devstral** | 7b / 22–24b / 24b | tools (small/devstral + vision on some) | Coding agents (`devstral`). |
| **embeddinggemma** | 300m | embedding | Official embeddings rec. L2-normalized. |
| **qwen3-embedding** | 0.6b, 4b, 8b | embedding | Official rec. |
| **nomic-embed-text** | — | embedding | 83.5M pulls. Large token window. |
| **all-minilm** | 22m, 33m | embedding | Smallest RAG embed. |
| **mxbai-embed-large** | 335m | embedding | High-quality local embed. |
| **llava** / **qwen3-vl** / **llama3.2-vision** / **gemma3** | 7–34b / 2–235b / 11b, 90b / 270m–27b | vision | Image-in. Prefer gemma4 / qwen3-vl on current docs. |
| **functiongemma** | 270m | tools | Tiny function-calling specialist. |
| Cloud-only giants | `glm-5.2:cloud`, `minimax-m3:cloud`, `kimi-k2.6:cloud`, `gpt-oss:120b-cloud`, `qwen3.5:397b` | tools / thinking / vision | Do not pull weights; offload. Quota. Cloud structured-outputs **unsupported**. |

Quantization: library tags are typically **Q4_K_M**. Create custom quants with `ollama create --quantize q4_K_M|q4_K_S|q8_0`.

---

## Ranking table

Columns: **#** rank · **hand** · **kind** · **DOES** · **auth** · **cost** · **power** · **how COSMOS reaches it** · **source**.

### A. Local inference (FREE, cannot run out) — rank first

| # | hand | kind | DOES | auth | cost | power | how COSMOS reaches it | source |
|---|------|------|------|------|------|-------|----------------------|--------|
| 1 | **`POST /api/chat`** | native REST | Multi-turn chat. Roles `system`/`user`/`assistant`/`tool`. Tools, vision (`images` base64), thinking, JSON/schema `format`, `options` (`num_ctx`, temp, seed…), `keep_alive`, streaming NDJSON (default) or `stream:false`. Empty `messages` **preloads**; `keep_alive:0` **unloads**. Returns `message.tool_calls`, usage ns metrics. | none (localhost) | **free** | **highest** — the COSMOS local `ApiRail`. Vendor-plural without a bill. | Dispatcher HTTP from Core; attempt workspace. `curl http://127.0.0.1:11434/api/chat -d '{model,messages,stream:false,tools?}`. | [chat](https://docs.ollama.com/api/chat) |
| 2 | **`POST /v1/chat/completions`** | OpenAI-compat REST | Drop-in Chat Completions: streaming, JSON mode, vision (base64; **URL images unsupported**), tools, reasoning_effort `high/medium/low/max/none`. **Not:** `tool_choice`, `logit_bias`, `user`, `n`, logprobs (compat page; native generate *does* have logprobs). | dummy `api_key=ollama` | **free** | **highest** — existing `oa-api` shape. Alias a local model `ollama cp qwen3-coder gpt-4o` if a client hard-codes the name. Context size **cannot** be set here → Modelfile `PARAMETER num_ctx`. | `OpenAI(base_url='http://127.0.0.1:11434/v1/', api_key='ollama')` or COSMOS `ApiRail` base rewrite. | [openai-compatibility](https://docs.ollama.com/api/openai-compatibility) |
| 3 | **Tool / function calling** (`tools` on `/api/chat` or `/v1/chat/completions`) | capability | Model emits `tool_calls`; COSMOS executes; reply with `role=tool` + `tool_name`. Single-shot, **parallel** multi-call, and **agent loop** (while `tool_calls`). Python SDK accepts callables. Streaming: accumulate partial `tool_calls`. Models: [search?c=tool](https://ollama.com/search?c=tool) (qwen3, llama3.1/3.2, gpt-oss, gemma4, glm-*, devstral, functiongemma, …). **`tool_choice` unsupported** on both shims. | none | **free** (local) | **highest** — local agents (scheduler, registry probe, citation fetch) without metered tokens. | Same as #1/#2. Loop in the worker: chat → execute → append tool result → chat. | [tool-calling](https://docs.ollama.com/capabilities/tool-calling) · [blog](https://ollama.com/blog/tool-support) |
| 4 | **`POST /v1/messages`** (Anthropic compat) | Anthropic-compat REST | Messages API: streaming, system, vision (base64 only), tools + tool_results, thinking. Lets **Claude Code** run against a local model. **Not:** count_tokens, tool_choice, metadata, prompt cache, batches, citations, PDF, URL images. Token counts are approximations. | dummy `ANTHROPIC_AUTH_TOKEN=ollama` | **free** | **highest** — F5 overflow: coding agent on local weights when Claude weekly quota is dry. Recs: `qwen3-coder`, `gpt-oss:20b`, `glm-4.7-flash`. | `ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_AUTH_TOKEN=ollama claude --model qwen3-coder` **or** `ollama launch claude`. Copy name if the tool insists on `claude-3-5-sonnet`: `ollama cp qwen3-coder claude-3-5-sonnet`. | [anthropic-compatibility](https://docs.ollama.com/api/anthropic-compatibility) |
| 5 | **`ollama serve`** | CLI / daemon | Starts the HTTP API (default `127.0.0.1:11434`). Windows tray app already does this. `ollama serve --help` lists env vars. | none | **free** | **high** — without this, no rail. | Native Windows service / NSSM / existing tray. COSMOS probes `GET /api/version` + `/api/tags` at boot. `OLLAMA_HOST`, `OLLAMA_MODELS`, `OLLAMA_CONTEXT_LENGTH`, `OLLAMA_KEEP_ALIVE`, `OLLAMA_ORIGINS`, `OLLAMA_NO_CLOUD=1`. | [cli](https://docs.ollama.com/cli) · [faq](https://docs.ollama.com/faq) · [windows](https://docs.ollama.com/windows) |
| 6 | **`ollama run <model> [prompt]`** | CLI | Pull-if-needed + interactive chat **or** one-shot prompt (headless). Multimodal: `ollama run gemma4 "What's in this? /path/img.png"`. Embed: `ollama run embeddinggemma "Hello"` → JSON array. `--think` / `--think=false` / `--hidethinking`. `/set think`, `/set parameter num_ctx`, `/bye`. Preload: `ollama run llama3.2 ""`. | none (local) | **free** | **high** — queue-job one-shot without HTTP client code. | Attempt-private: `ollama run qwen3-coder --think "…task…"`. | [cli](https://docs.ollama.com/cli) |
| 7 | **`POST /api/generate`** | native REST | Completion from a `prompt` (not chat history). Fill-in-middle `suffix`, images, `format` json/schema, `system`, `raw` (no template), `think`, logprobs, `options`, load/unload. Streaming default. | none | **free** | **high** — FIM / raw / structured one-shots; preload/unload. Prefer `/api/chat` for agents. | HTTP. Empty body-prompt loads; `keep_alive:0` unloads. | [generate](https://docs.ollama.com/api/generate) |
| 8 | **`POST /api/embed`** (+ OpenAI `POST /v1/embeddings`) | native / OpenAI REST | L2-normalized vectors. `input` string **or** string[]. `truncate` (default true), `dimensions` (Matryoshka). Batch. Typical 384–1024 dims. Recs: `embeddinggemma`, `qwen3-embedding`, `all-minilm`. Same model for index **and** query. Cosine similarity. | none | **free** | **high** — local RAG for Chapter 4 / citation / queue search. No OpenAI embed bill. | HTTP. OpenAI: `input` string or string[] (not token arrays). **Do not use superseded `POST /api/embeddings`** (`prompt` → singular `embedding`) except old clients. | [embed](https://docs.ollama.com/api/embed) · [embeddings](https://docs.ollama.com/capabilities/embeddings) · [github api.md](https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md) |
| 9 | **Structured outputs** (`format`) | capability | `"json"` or a JSON Schema object. Pydantic `model_json_schema()` / Zod. Works on generate **and** chat; vision+schema too. Also OpenAI `response_format`. **Cloud does not support this.** Lower temperature. Ground the schema in the prompt. | none | **free** (local only) | **high** — typed worker returns (validators, registry cards, spend events) without a parser lottery. | Set `format` on `/api/chat` or `/api/generate`; `stream:false`. | [structured-outputs](https://docs.ollama.com/capabilities/structured-outputs) |
| 10 | **`ollama pull` / `POST /api/pull`** | CLI + REST | Download a library (or `user/model`) blob. Resumable; concurrent pulls share progress. `insecure` for private registries. Streams status/digest/total/completed. | none for public; sign-in for private | **free** (public) + disk | **high** — the install step of the rail. | `ollama pull qwen3-coder` once; then every chat is local. API equivalent for unattended jobs. | [cli](https://docs.ollama.com/cli) · [pull](https://docs.ollama.com/api/pull) |
| 11 | **Modelfile + `ollama create` / `POST /api/create`** | CLI + REST | Blueprint: `FROM` (library / Safetensors dir / GGUF), `PARAMETER` (num_ctx, temp, stop, num_predict, draft_num_predict, top_k/p, min_p, seed, repeat_*), `TEMPLATE` (Go templates: `.System` `.Prompt` `.Response`), `SYSTEM`, `ADAPTER` (QLoRA safetensors or GGUF), `LICENSE`, `MESSAGE` few-shot, `REQUIRES` min Ollama version. `ollama create -f Modelfile [name]`. API: `from`, `system`, `parameters`, `quantize` (`q4_K_M` rec). Case-insensitive. | none | **free** | **high** — pin 64k ctx, COSMOS system prompt, stop tokens, LoRA, quantize FP16→Q4 so a 30B fits. **Required** to set context for the OpenAI shim. | Write Modelfile in attempt workspace; `ollama create cosmos-coder -f Modelfile`; call that name on the rail. | [modelfile](https://docs.ollama.com/modelfile) · [create](https://docs.ollama.com/api/create) · [import](https://docs.ollama.com/import) |
| 12 | **`ollama launch`** | CLI | One-command wire-up of Claude Code, Codex, OpenCode, VS Code, Droid (and OpenClaw / Copilot CLI per README). `ollama launch claude --model qwen3.5`. `--config` writes config without starting. Needs Ollama **v0.15+**. Coding tools want **≥64k** ctx. | none (local model) / sign-in if `:cloud` | **free** local | **high** — coding-agent lane on local weights; no F5 burn. | Native: `ollama launch claude --model qwen3-coder` after `ollama pull`. Lease so it does not double-write with Cursor Cloud Agents. | [cli](https://docs.ollama.com/cli) · [launch blog](https://ollama.com/blog/launch) · [claude-code](https://docs.ollama.com/integrations/claude-code) |
| 13 | **Thinking / reasoning** (`think`) | capability | Separates `message.thinking` from `content`. Bool or `low/medium/high/max`. GPT-OSS: levels only (true/false ignored); cannot fully disable. CLI `--think`, `/set think`. Stream thinking then answer. | none | **free** | **high** — audit traces for agent jobs; hide with `--hidethinking` in user-facing paths. | `think: true` on `/api/chat` or `/api/generate`. Models: [search?c=thinking](https://ollama.com/search?c=thinking). | [thinking](https://docs.ollama.com/capabilities/thinking) |
| 14 | **Vision** | capability | Images in `images[]` (REST = base64; SDKs also path/bytes/URL). CLI path in the prompt string. Works with structured outputs. OpenAI shim: base64 `image_url` only. | none | **free** | **high** — local OCR/screenshot/exhibit photos without Gemini/OpenAI vision spend. | `/api/chat` or `/api/generate` with a vision model (`gemma4`, `qwen3-vl`, `llava`, …). | [vision](https://docs.ollama.com/capabilities/vision) |
| 15 | **`POST /v1/responses`** | OpenAI Responses API | Non-stateful Responses (since Ollama **v0.13.3**). Streaming, tools, reasoning summaries. **No** `previous_response_id` / `conversation` / truncation. | dummy key | **free** | **med-high** — newer OpenAI clients (Codex-style) without rewriting to chat. | `client.responses.create(model=…, input=…)` against `/v1`. | [openai-compatibility](https://docs.ollama.com/api/openai-compatibility) |
| 16 | **`POST /v1/completions`** | OpenAI Completions | Legacy completions. Streaming, JSON, seed. `prompt` **string only**. No logprobs / n / echo. | dummy key | **free** | **med** — old FIM/completion clients. Prefer native `/api/generate`. | OpenAI `completions.create`. | same |
| 17 | **Official Python SDK `ollama`** | SDK | `chat`, `generate`, `embed`, `pull`, `list`, `ps`, `create`. Tools as Python functions. `think=True`. `Client(host=…, headers=…)`. Cloud host `https://ollama.com` + Bearer. | none local | **free** | **high** — typed tool loop in a native worker. | `pip install ollama -U` in the attempt venv. | [ollama-python](https://github.com/ollama/ollama-python) |
| 18 | **Official JS SDK `ollama`** | SDK | Same surface for Node workers / KDash-adjacent tools. | none local | **free** | **med-high** | `npm i ollama`. | [ollama-js](https://github.com/ollama/ollama-js) |
| 19 | **`GET /api/tags` + `GET /v1/models`** | REST | List local models (name, size, digest, family, quant, parameter_size). OpenAI list: `owned_by` = ollama user or `"library"`; `created` = last modified. | none | **free** | **med-high** — boot probe / registry. Fail-closed if empty. | `GET http://127.0.0.1:11434/api/tags`. Also `GET /v1/models/{model}`. | [tags](https://docs.ollama.com/api/tags) |
| 20 | **`GET /api/ps` / `ollama ps` / `ollama stop`** | REST + CLI | What is loaded, VRAM bytes, context_length, GPU/CPU split, expiry. Stop unloads. | none | **free** | **med-high** — runtime binding: *is this the GPU the machine is using?* | Probe before dispatch; `ollama stop <model>` to free VRAM for a bigger job. | [ps](https://docs.ollama.com/api/ps) · [faq](https://docs.ollama.com/faq) |
| 21 | **`POST /api/show` / `ollama show --modelfile`** | REST + CLI | Modelfile, template, parameters, license, `model_info`, **capabilities** (`completion`, `vision`, …). `verbose=true` dumps tokenizer. | none | **free** | **med** — capability probe before claiming tools/vision. | `POST /api/show {"model":"qwen3"}`. | [show](https://docs.ollama.com/api-reference/show-model-details) · [github api.md](https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md) |
| 22 | **`POST /api/copy` / `ollama cp`** | REST + CLI | Alias a model (`qwen3-coder` → `gpt-4o` / `claude-3-5-sonnet`) so stubborn clients work. | none | **free** | **med** — glue for OpenAI/Anthropic shims. | `ollama cp llama3.2 gpt-3.5-turbo`. | [copy](https://docs.ollama.com/api/copy) |
| 23 | **`DELETE /api/delete` / `ollama rm`** | REST + CLI | Delete a local model. | none | **free** | **low-med** — disk reclaim. Never delete; COSMOS stages to `_delme\` if it wraps this. | Only against attempt-private model names, not Keith's library. | [delete](https://docs.ollama.com/api/delete) |
| 24 | **Import GGUF / Safetensors / LoRA** | CLI | `FROM ./model.gguf` or safetensors dir; `ADAPTER` for QLoRA. Architectures: Llama 2/3/3.1/3.2, Mistral/Mixtral, Gemma 1/2, Phi3 (base). Then `ollama create`. Quantize `--quantize q4_K_M`. | none | **free** | **med** — bring HF / custom fine-tunes onto the rail. | Attempt workspace files → Modelfile → create. | [import](https://docs.ollama.com/import) |
| 25 | **Blob API** `HEAD/POST /api/blobs/:digest` | REST | Existence check + upload GGUF/safetensors by SHA256 before `POST /api/create` with `files` map. | none | **free** | **med** — unattended create from blobs (no Modelfile on disk). | Worker hashes file, POST blob, then create. | [github api.md](https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md) |
| 26 | **`GET /api/version`** | REST | `{"version":"…"}`. | none | **free** | **med** — boot identity. Bind "Ollama is up" to this JSON, not a green log. | Core health probe. | [version](https://docs.ollama.com/api-reference/get-version) |
| 27 | **`POST /v1/completions` suffix / FIM** | (covered in #7/#16) | Fill-in-the-middle via `suffix` on generate/completions. | none | **free** | **med** — code-complete rail. | `/api/generate` `prompt`+`suffix`. | [generate](https://docs.ollama.com/api/generate) |
| 28 | **Docker `ollama/ollama`** | container | CPU / `--gpus=all` / `ollama/ollama:rocm` / Vulkan devices. Volume `ollama:/root/.ollama`. Port 11434. Jetson: `JETSON_JETPACK=5|6`. macOS Docker Desktop: **no GPU passthrough**. | none | **free** | **med** — isolated sidecar if Keith does not want the tray app. | `docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 ollama/ollama` then same HTTP. | [docker](https://docs.ollama.com/docker) |
| 29 | **Keep-alive / preload / flash-attn / KV-quant env** | server config | `OLLAMA_KEEP_ALIVE`, `OLLAMA_FLASH_ATTENTION`, `OLLAMA_KV_CACHE_TYPE`, `OLLAMA_NUM_PARALLEL`, `OLLAMA_MAX_LOADED_MODELS`, `OLLAMA_MAX_QUEUE`, `OLLAMA_CONTEXT_LENGTH`, `HTTPS_PROXY` (not HTTP_PROXY). Windows: user env vars + restart tray. | none | **free** | **med** — make the rail actually fast/fit. | Set once on the Windows user; document in `live/config`. | [faq](https://docs.ollama.com/faq) |
| 30 | **Streaming NDJSON** | protocol | Default on generate/chat. `application/x-ndjson`. Mid-stream errors keep HTTP 200 and emit `{"error":…}`. Disable with `stream:false`. SDKs default **off**; set `stream=True`. | none | **free** | **med** — KDash token paint; accumulate for tool loops. | Native HTTP. | [api/streaming](https://docs.ollama.com/api/streaming) · [capabilities/streaming](https://docs.ollama.com/capabilities/streaming) |
| 31 | **Usage metrics on every generate/chat** | protocol | `total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_duration`, `eval_count`, `eval_duration` (all ns). tok/s = `eval_count / eval_duration * 1e9`. Streaming: last chunk with `done:true`. | none | **free** | **med** — spend-gate analogue for local (time/VRAM, not dollars). Ledger `RAIL_RESULT` can carry eval_count. | Parse the JSON; do not invent tok/s. | [usage](https://docs.ollama.com/api/usage) |
| 32 | **Errors** | protocol | 200 / 400 / 404 / 429 / 500 / **503 queue full** / 502 cloud unreachable. Body `{"error":"…"}`. | none | **free** | **low-med** — typed failures for the rail. | Map 503 → retry/backoff; 404 → pull; 502 → cloud down. | [errors](https://docs.ollama.com/api/errors) |

### B. Cloud / account (can run out) — rank below local

| # | hand | kind | DOES | auth | cost | power | how COSMOS reaches it | source |
|---|------|------|------|------|------|-------|----------------------|--------|
| 33 | **Cloud models `:cloud` via localhost** | REST + CLI | Same `/api/chat` etc., weights offloaded. Full context. `ollama run gpt-oss:120b-cloud`. Sign-in once. | `ollama signin` | **Free plan light quota**; Pro $20; Max $100 (paused) | **med-high** — 120B/480B/671B when VRAM cannot. **Can run out. No structured outputs.** | Same local URL; model name ends `:cloud`. Spend-gate + `OLLAMA_NO_CLOUD` default-off until Keith opts in. | [cloud](https://docs.ollama.com/cloud) · [pricing](https://ollama.com/pricing) |
| 34 | **`https://ollama.com/api` remote host** | REST | ollama.com as a remote Ollama. `POST /api/chat`, `/api/generate`, `GET /api/tags`. | `Authorization: Bearer $OLLAMA_API_KEY` | Cloud plan | **med** — phone/Tailscale client without a local GPU. | Python `Client(host="https://ollama.com", headers={Authorization: Bearer…})`. Store key in `live/config/`. | [authentication](https://docs.ollama.com/api/authentication) |
| 35 | **`POST https://ollama.com/api/web_search`** | REST + SDK | Query → `{title,url,content}[]`. `max_results` default 5, max 10. | Bearer API key (free account required) | Cloud plan (not local) | **med** — search tool for local agents. Prefer Firecrawl/Playwright if those rails are live. Raise ctx to ≥32k (rec 64k). | `ollama.web_search("…")` or HTTP. MCP example: [web-search-mcp.py](https://github.com/ollama/ollama-python/blob/main/examples/web-search-mcp.py). | [web-search](https://docs.ollama.com/capabilities/web-search) |
| 36 | **`POST https://ollama.com/api/web_fetch`** | REST + SDK | URL → `{title,content,links[]}`. | Bearer | Cloud plan | **med** — page fetch for the search agent. | `ollama.web_fetch(url)`. | same |
| 37 | **`POST /api/push` / `ollama push`** | REST + CLI | Publish `user/model` to ollama.com. Needs public key on [settings/keys](https://ollama.com/settings/keys). | sign-in | Free: public; Pro: private | **low** — COSMOS is not a model host. | Only if Keith wants to share a Modelfile. | [import](https://docs.ollama.com/import) · [push](https://docs.ollama.com/api/push) |
| 38 | **`ollama signin` / `signout`** | CLI | Bind local daemon to ollama.com account (cloud models, push, private pull). | browser/app | $0 to sign in | **low-med** — prerequisite of 33–37. | Keith does credentials. | [cli](https://docs.ollama.com/cli) · [authentication](https://docs.ollama.com/api/authentication) |

### C. DOM fallback

| # | hand | kind | DOES | auth | cost | power | how COSMOS reaches it | source |
|---|------|------|------|------|------|-------|----------------------|--------|
| 39 | **ollama.com library / download / settings** | DOM | Installer, model cards (size, usage level 1–4), API key mint, billing, usage. | account for keys/cloud | $0 browse | **low** — first install and key mint only. | DOM worker if AUTH_REQUIRED; Keith otherwise. | [library](https://ollama.com/library) · [download](https://ollama.com/download) · [pricing](https://ollama.com/pricing) |

---

## Recommended COSMOS wiring (not implemented this pass)

1. **Probe:** `GET /api/version` + `GET /api/tags` + `GET /api/ps`. Bind "Ollama up" to those JSON bodies. Missing daemon → typed `UNREACHABLE`, not a fake DONE.
2. **Rail:** `ApiRail` `link_id="ollama-local"`, `base=http://127.0.0.1:11434/v1`, dummy key, **spend_gate budget = 0**. Prefer native `/api/chat` when tools + `num_ctx` + `think` matter; OpenAI shim when reusing `oa-api` client code.
3. **Default local models (if VRAM unknown):** `qwen3:8b` or `gpt-oss:20b` for chat/tools; `embeddinggemma` for RAG; `gemma4` for vision. If ≥24 GB VRAM: `qwen3-coder` or `glm-4.7-flash` at `num_ctx=64000`.
4. **Context:** never trust the 4k default for agents. Modelfile or `options.num_ctx` (native) — OpenAI shim cannot set it.
5. **Cloud off** until Keith opts in: `OLLAMA_NO_CLOUD=1`.
6. **Do not** expose `0.0.0.0:11434` to the LAN without `OLLAMA_ORIGINS` + a proxy. Tailscale `cosmos up` can reach localhost on the box; that is enough.

---

## What this scout did **not** do

- Did not install or probe Ollama on this machine (MESH_ADDITIONS still **UNVERIFIED**).
- Did not mint an API key, sign in, or pull a model.
- Did not edit COSMOS core or register a rail.
- Did not benchmark tok/s or VRAM on Keith's GPU — `ollama ps` after a real pull is the only honest number.

---

## Host bind (additive, 2026-08-25 ARCH) — H4

Live this machine, this process:

- `where.exe ollama` → **NOT_ON_PATH**.
- `GET http://127.0.0.1:11434/api/version` (2s) → **`OLLAMA_DOWN:System.Net.WebException`**.

Ollama is MESH #1 new *capability* and is **install-blocked** here. Treating C1 as "ready to code" is a guess. **WAVE C1 (ARCH):** designed-but-dark until Keith installs the Windows app and a small tool model (`OLLAMA_NO_CLOUD=1` until he opts in). After that, bind to `/api/version` JSON + `/api/tags` + `/api/ps` — never an exit code. Do **not** register Dispatcher `ApiRail` `ollama-local` until Kernel attach exists (BACKLOG). VRAM: **UNKNOWN** — do not pull 30B until `ollama ps` exists. This is **not** a stage-6 pass.

---

## Host bind (additive, 2026-08-27 s6 re-probe) — H4 / U1 VRAM

This process (2026-08-27T01:53-05):

- `Get-Command ollama` → **NOT_ON_PATH**
- `GET http://127.0.0.1:11434/api/version` (2s) → **timeout** (`URLError`)
- `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader` → **`NVIDIA GeForce RTX 3070, 8192 MiB`**

U1 VRAM **closed as 8 GiB**. Install still blocked. After Keith installs: 8B-class (`llama3.2` / `qwen3:8b` / `embeddinggemma`), not 30B-coder. WAVE C1 remains designed-but-dark.

---

## Sources (primary)

All URLs in the documentation table above were fetched 2026-08-25. Canonical cluster:

- https://docs.ollama.com/llms.txt
- https://docs.ollama.com/api/introduction
- https://docs.ollama.com/api/openai-compatibility
- https://docs.ollama.com/api/anthropic-compatibility
- https://docs.ollama.com/cli
- https://docs.ollama.com/modelfile
- https://docs.ollama.com/gpu
- https://docs.ollama.com/cloud
- https://ollama.com/pricing
- https://ollama.com/library
- https://github.com/ollama/ollama
- https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md
