# GOOGLE / GEMINI HANDS — G46 scout return (Gemini API, Gemini CLI, Vertex / Agent Platform)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim except where a COSMOS artifact is named.
**No COSMOS core code was edited.** Maker-docs sweep (DHx assignment log): each maker's hands → `docs/research/<MAKER>_HANDS.md`.

**Already on the mesh (do not re-add as "new"):** Dispatcher rail **`gem-api`** (`bts_gem`) — Gemini via **Vertex**, drawing the **$300 Vertex / Google Cloud credit expiring 2026-10-13**, budget $300 (`docs/MESH_ADDITIONS.md`, `docs/MOTIF.md`). This file inventories every Google/Gemini **hand** COSMOS could fire, including the ones already wired.

**Filter:** a surface with no hands is rejected. Every row is an **action** COSMOS could fire: REST endpoint, CLI flag, SDK call, MCP tool, GitHub Action, or DOM fallback. Chat-only (gemini.google.com chat UI chrome) is out unless it is a dispatchable CLI/API.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks. Equal power, cheaper wins. Metered Vertex / prepaid AI Studio sit **below** the free Gemini Developer API + OSS Gemini CLI cluster even when the model is the same family.

**Name collision (do not mix wallets):** Google renamed **Vertex AI** to **Gemini Enterprise Agent Platform**. Official docs still answer at both `cloud.google.com/vertex-ai/…` and `docs.cloud.google.com/gemini-enterprise-agent-platform/…`. COSMOS's `gem-api` is the **Vertex / Agent Platform** wallet, **not** the AI Studio Developer API wallet. They are different billing, different ToS, different data-use.

---

## How COSMOS reaches Google/Gemini (reach column, one pattern)

Core stays sole ledger writer. Google is reached as:

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Native Gemini CLI** | `gemini -p "…"` / `--prompt` inside an attempt-private workspace. JSON via `--output-format json`. Built-in tools: files, shell, web fetch, Google Search grounding, MCP. | Preferred coding/agent lane. Apache-2.0 OSS. Auth = Google login **or** `GEMINI_API_KEY` **or** Vertex ADC. Matches "no bats — in-app / COSMOS action." |
| **B. HTTP Gemini Developer API (AI Studio)** | `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` **or** `POST …/v1beta/interactions`. Header `x-goog-api-key`. | Free-tier Flash tokens first. Spend-gate as `gem-api` sibling only if Keith mints a **Studio** key distinct from Vertex. |
| **C. HTTP Vertex / Agent Platform** | `POST https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent`. Bearer ADC / SA. Same `google-genai` SDK with `vertexai=True`. | **Already `gem-api`.** Burns the $300 Vertex credit. Enterprise grounding, Model Garden, batch, Agent Builder. |
| **D. Vertex Express Mode** | `POST https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent?key={API_KEY}` (no project/location in path). SDK: `genai.Client(vertexai=True, api_key=…)`. | New-GCP 90-day free try. Key-shaped Vertex, not Studio. |
| **E. MCP-client** | Gemini CLI is an MCP **host**. Interactions API talks to remote Streamable-HTTP MCP (`type: mcp_server`). COSMOS can also be a host. | Agent brains get forge/browser/search tools. Core should prefer native `gemini`/`gh`/`glab` over giving itself a shell via MCP. |
| **F. Forge CI** | `google-github-actions/run-gemini-cli` — PR review, issue triage, `@gemini-cli`. | Overflow coding on `keithbbf-gif/cosmos`. Lease so it does not double-write with Cursor Cloud Agents. |
| **G. DOM** | [AI Studio](https://aistudio.google.com), Cloud Console billing, first OAuth, key mint, Agent Garden click-deploy — everything the API cannot do when AUTH_REQUIRED. | Fallback only. Canon: DOM first when the API depends on something that can run out (free RPD, prepaid balance, Vertex credit expiry 2026-10-13). |

Keith owns credentials. Store under `live/config/` (git-ignored). Never hard-code. Never print a key in full. Fenced commit still gates any tree write.

---

## Auth primer (all API/CLI rows inherit this unless overridden)

Two backends, one SDK (`pip install google-genai` → `from google import genai`).

| method | credential | header / env | COSMOS use |
|--------|------------|--------------|------------|
| **AI Studio API key** (standard or **auth key**) | key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | `x-goog-api-key` **or** `GEMINI_API_KEY` / `GOOGLE_API_KEY` (`GOOGLE_API_KEY` wins if both set) | Developer API + Gemini CLI Option 2. New keys are **auth keys** (bound to a service account). **Unrestricted standard keys rejected.** Standard keys die **September 2026** — migrate to auth keys. |
| **Gemini CLI Google login** | OAuth cached locally after `gemini` → "Sign in with Google" | CLI manages it | Individual accounts: historically 60 RPM / 1,000 RPD via Code Assist for individuals. **Banner (official, 2026-08-25):** unpaid + Google One users were moved to **Antigravity CLI on 2026-06-18**. Treat Google-login quota as **unreliable for unpaid**; prefer API key / Vertex for headless COSMOS. |
| **Vertex ADC** | `gcloud auth application-default login` **or** SA JSON | `Authorization: Bearer $(gcloud auth print-access-token)` | Production `gem-api`. Unset `GEMINI_API_KEY`/`GOOGLE_API_KEY` or ADC is skipped. Env: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` (or `global`), `GOOGLE_GENAI_USE_VERTEXAI=true`. |
| **Vertex service account** | JSON key, role **Vertex AI User** | `GOOGLE_APPLICATION_CREDENTIALS` | Headless / CI. Keith holds the file. |
| **Vertex / Express API key** | Cloud API key **or** Express-mode key | `GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_VERTEXAI=true`; Express: `?key=` on global `aiplatform.googleapis.com` | Express = 90-day no-billing try. Org policy may reject API keys ("API keys are not supported by this API…") — then ADC/SA. |
| **Remote MCP headers** | per-server token in `tools[].headers` | Interactions `mcp_server` tool | Streamable HTTP only (SSE **not** supported). Server names: snake_case, no `-`. |

**SDK switch:** `genai.Client()` → Developer API. `genai.Client(vertexai=True, project=…, location=…)` → Vertex / Agent Platform. Same `generate_content` / `interactions.create` / `files` / `batches` surface.

---

## ARCH env isolation (additive, 2026-08-25) — H5 / B1

Two-wallet theft / skip: leftover `GEMINI_API_KEY` / `GOOGLE_API_KEY` makes the SDK **skip ADC** and bill Studio instead of Vertex `gem-api` (or the reverse). `live/config/` this pass has **no** `GEMINI_API_KEY`. GCLOUD_HANDS: ADC exists for Vertex (do not expand this MOTIF row into a GCP rewrite — M6).

**ARCH rule:** `gem-api` (Vertex) jobs **unset** `GEMINI_API_KEY` / `GOOGLE_API_KEY` so ADC is used. A future Studio Flash sibling (WAVE D2) **sets** an **auth** key (standard keys die Sep 2026) in a **different** job env. Unpaid Google-login path migrated to Antigravity CLI **2026-06-18** — do not build on it. Gemini CLI binary is on PATH; auth method in use: **UNKNOWN** (B1). Vertex credit MESH-expires **2026-10-13**. Dispatcher new rails wait on Kernel attach. This is **not** a stage-6 pass.

---

## Host bind (additive, 2026-08-27 s6 re-probe) — U4 closed / B1 not a new wallet

This process (`gemini` 0.52.0 via `cmd /c`; `~/.gemini/settings.json` keys only):

- `selectedAuthType` → **`vertex-ai`**. U4 **closed**.
- `mcpServers` names → **`BFast`** only.
- No `GEMINI_API_KEY` in `live/config/`.

**Rubric 8:** Gemini CLI on Vertex ADC is the **same wallet as `gem-api`**, not a distinct coding-agent lane. Demote B1 from "wire next" to **delta of already-on-mesh `gem-api`**. Studio Flash sibling (D2) remains the distinct-wallet path and is still dark. Vertex credit MESH-expires **2026-10-13**.

---

## Cost floor (three wallets — do not conflate)

Mixing Studio prepaid credits with Vertex Cloud Billing is how `gem-api` gets burned by accident. Official: **Prepay credits are locked to Gemini Developer API** and **cannot** pay for Vertex / Agent Platform / Compute / Storage.

| Wallet | What official docs say | COSMOS note |
|--------|------------------------|-------------|
| **Gemini Developer API Free Tier** | Free input & output tokens on **certain models** (Flash family; Pro often **not available** free). Rate-limited (RPM/TPM/RPD per model; RPD resets **midnight Pacific**). Limits per **project**, not per key. **Content used to improve Google products.** AI Studio **chat UI is free** in all available regions unless a **paid** key is linked. | Highest-ranked Gemini inference. Probe live limits at [aistudio.google.com/rate-limit](https://aistudio.google.com/rate-limit). |
| **Gemini Developer API Paid** | Link Cloud Billing + **Prepay min $10** (new users; Prepay/Postpay live since **2026-03-23**). Tiers: Free → T1 ($250/mo cap, $10/10-min spend) → T2 ($2,000; paid $100 + 3 days) → T3 ($20k–$100k; paid $1,000 + 30 days). **Content not used to improve products.** Batch = **50% off**. Context caching. Highest models (3.1 Pro, image gen). Credits expire **12 months**, non-refundable except Prepay→Postpay switch. $0 balance = **all keys on that billing account stop**. | Real money. **Google Cloud $300 Welcome credit cannot pay Gemini API** (accounts opened after 2026-03-02; Gemini API excluded from Free Trial starting March 2026). |
| **Vertex / Agent Platform** | Pay-as-you-go Cloud Billing. **New customers: up to $300 free credits** for Agent Platform **and** other GCP products. Token prices often match Developer API list but **region** (global vs non-global) and **partner models** differ. Grounding, Model Garden deploys, Agent Engine, batch JSONL on GCS/BQ. | This is `gem-api`. MESH: **$300 Vertex credit expires 2026-10-13**. Spend-gate it. After expiry = metered. |
| **Vertex Express Mode** | New `@gmail.com` GCP users: **90 days free**, no billing info, subset of models, Express key, global endpoint. Upgrade by enabling billing. | Separate from Studio free tier. Useful only if Keith still has Express headroom. |
| **Gemini CLI (tool)** | Apache-2.0, `$0` to install. Inference billed by **auth method** (table below). | Tool is free; tokens are not. |
| **Files API ops** | Upload / list / get / delete = **$0**. 20 GB/project, 2 GB/file, **48 h TTL**, not downloadable. Always use Files API when request > **100 MB** (PDF **50 MB**). | Storage free; tokens when the file is used as input. |
| **Code execution tool** | **No extra charge.** Tokens only (prompt + generated code + execution result + summary). 30 s runtime, 5 retries, Python-only sandbox, no pip install. | Prefer this over a local Python worker for math/CSV/plot. |
| **Function calling** | **$0 extra** — tokens only. Model does **not** execute; COSMOS must. | Wire COSMOS tools as declarations. |
| **Grounding with Google Search (Developer API)** | **Gemini 2.x Flash:** 500 RPD free (shared Flash+Flash-Lite); Pro often N/A on free. Paid 2.5: 1,500 RPD then **$35 / 1,000 grounded prompts**. **Gemini 3.x:** **not available on Free API**; paid **5,000 free searches/month** (shared all 3.x) then **$14 / 1,000 search queries**. One user request may fire **multiple** billable queries. Testable in AI Studio (`**` on pricing page). | Do not enable on a COSMOS loop without a spend cap. Prefer URL-context on known URLs. |
| **countTokens / GetTokens** | **Not billed**, does not consume inference quota. | Pre-flight spend-gate. |
| **Failed 400/500** | Tokens **not** billed; **still counts against quota**. | |
| **Embeddings** | Free of charge on Free; paid **$0.15 / 1M** (`gemini-embedding-001` text). Batch embeddings **50%**. | RAG / collector search. |

**List rates fetched 2026-08-25** from [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing) (USD / million tokens, **Standard** paid). Flash 3.7/3.6 intro prices hold **through 2026-12-31**, then 2×.

| Model | Free? | Input | Output | Cache read / storage | Batch in/out |
|-------|-------|-------|--------|----------------------|--------------|
| Gemini 3.7 Flash / 3.6 Flash | **yes** | $0.75 (→ $1.50 on 2027-01-01) | $3.75 (→ $7.50) | $0.075 + $0.50/M/hr | 50% |
| Gemini 3.5 Flash | **yes** | $1.50 | $9.00 | $0.15 + $1.00/M/hr | 50% |
| Gemini 3.5 Flash-Lite | **yes** | $0.30 | $2.50 | $0.03 + $1.00/M/hr | 50% |
| Gemini 3.1 Flash-Lite | **yes** | $0.25 ($0.50 audio) | $1.50 | $0.025 + $1.00/M/hr | 50% |
| Gemini 3 Flash Preview | **yes** | $0.50 ($1 audio) | $3.00 | $0.05 + $1.00/M/hr | 50% |
| Gemini 2.5 Flash | **yes** | ~$0.30 | ~$2.50 | yes | 50% |
| Gemini 2.5 Pro | **yes** (exp id on some SKUs) | $1.25 (≤200k) / $2.50 (>200k) | $10 / $15 | $0.125 / $0.25 + $4.50/M/hr | 50% |
| Gemini 3.1 Pro Preview | **no** (Studio-testable) | $2 / $4 | $12 / $18 | $0.20 / $0.40 + $4.50/M/hr | 50% |
| Gemini Embedding | **yes** | $0.15 | n/a | n/a | $0.075 |
| Nano Banana image (3.1 Flash Image) | **no** | $0.50 | $3 text / **$60 images** (~$0.067/1K img) | — | 50% |

Vertex / Agent Platform list (same order of magnitude; **global** cheaper than regional for 3.7 Flash: $0.75 vs $0.825 in): [Agent Platform pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing) and legacy [Vertex generative pricing](https://docs.cloud.google.com/vertex-ai/generative-ai/pricing).

**Gemini CLI quotas by auth** ([official](https://geminicli.com/docs/resources/quota-and-pricing), last updated 2026-06-18):

| Auth | Daily requests | Notes |
|------|----------------|-------|
| Google account · Code Assist Individual | 1,000 (60/min advertised on README) | **Unpaid path migrated to Antigravity CLI 2026-06-18** per site banner. |
| Google AI Pro / Ultra | 1,500 / 2,000 | Subscription, login with that Google account. |
| `GEMINI_API_KEY` unpaid | **250**/day, **Flash only** | Draws Developer API free tier. |
| `GEMINI_API_KEY` paid | varies (tier RPM/TPM/RPD) | Per-token. |
| Vertex Express | varies, 90 days | |
| Vertex billed | dynamic shared quota / provisioned throughput | |
| Code Assist Standard / Enterprise / Workspace Ultra | 1,500 / 2,000 / 2,000 | Org license + GCP project. |

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it |
|---|------|------|----------------------|------|------|-------|------------------------|
| 1 | **Gemini CLI headless (`gemini -p`)** | CLI + agent | Open-source **agentic terminal**: reads/edits the attempt workspace, runs shell, web-fetches, grounds with Google Search, talks MCP, checkpoint/resume (`-r latest`). `gemini -p "…"` non-interactive; `--output-format json` (`response`, `stats`, `error`); `stream-json` for JSONL events (`init`/`tool_use`/`tool_result`/`result`). Exit 0/1/42/53. `@file` / `!cmd`. `GEMINI.md` project context. | Google login **or** `GEMINI_API_KEY` **or** Vertex ADC/SA. Headless **requires** env if no cached creds. | **Tool free** (Apache-2.0). Inference: API-key free 250 RPD Flash, or paid/Vertex. Google-login 1k RPD **may be dead for unpaid** (Antigravity cutover 2026-06-18). | **highest** | Native worker: `npm i -g @google/gemini-cli` then `gemini -p "…" --output-format json` in attempt workspace. Prefer API key / Vertex for unattended. Never a `.bat`. Bind result to JSON `response` + ledger. |
| 2 | **`generateContent` (Developer API)** | REST + SDK | The core hand: multimodal generate (text/image/audio/video/PDF). `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` (+ `:streamGenerateContent`). Tools, system instruction, cached_content, thinking, structured JSON schema. Same call in Python: `client.models.generate_content(model=…, contents=…)`. | `x-goog-api-key` / `GEMINI_API_KEY` | **Free** on Flash family within RPM/TPM/RPD. Paid list rates above. | **highest** | HTTP spend-gate **or** `google-genai`. Default COSMOS Studio rail (distinct from Vertex `gem-api`). Fail-closed on 429. |
| 3 | **Interactions API** | REST + SDK | GA agent-shaped loop: `POST /v1beta/interactions`. Stateful `previous_interaction_id`, built-in tools (`google_search`, `code_execution`, `url_context`, `file_search`, `google_maps`, computer use), custom functions, remote MCP, streaming steps. Google now **recommends this** over raw generateContent for new work. **Implicit cache only** (no explicit cache objects). | same Studio key | same tokens as generateContent | **highest** | `client.interactions.create(...)`. Prefer for multi-turn tool loops. REST: `https://generativelanguage.googleapis.com/v1beta/interactions`. |
| 4 | **Function calling (custom tools)** | API tool | Model emits `functionCall` / `function_call` with name+args; **COSMOS executes**; send `functionResponse` / `function_result` back. Parallel + compositional. Modes: AUTO / ANY / NONE / validated. Gemini 3: multimodal function **responses** (image/PDF), stream args, combine with built-in tools (`include_server_side_tool_invocations` on generateContent). Max ~512 declarations; keep 10–20 live. | same | **$0 extra** (tokens) | **highest** | Declare COSMOS verbs (ledger-read, queue-submit, gh/glab, collector) as tools. Do **not** give Core a shell; give the worker scoped functions. Vertex twin: `tools[].functionDeclarations` on generateContent. |
| 5 | **Code execution (server sandbox)** | API built-in tool | Model writes **Python**, Google runs it (numpy/pandas/matplotlib/scipy/sklearn/…; **no pip**). Returns `executableCode` + `codeExecutionResult`. 30 s, 5 retries, CSV/text I/O, graph images inline. Gemini 3 Flash: **code-on-images** (crop/zoom/count). Combinable with Search. | same | **$0 extra**; intermediate tokens billed as input, code+result+summary as output | **highest** | `tools=[{"type":"code_execution"}]` (Interactions) or `tools=[types.Tool(code_execution=…)]` (generateContent). Use for math, CSV, plots — not for executing COSMOS tree Python. |
| 6 | **Files API** | REST + SDK | `POST /upload/v1beta/files` (resumable), `GET /v1beta/files`, `GET /v1beta/{name}`, `DELETE`. Then pass `file.uri` into generate/interactions. Required when total request >100 MB (PDF 50 MB). Video: poll until `ACTIVE`. | same | **$0** storage; 20 GB/project, 2 GB/file, **48 h**, not downloadable | **highest** | Upload attempt artifacts / PDFs / audio into Files, hash locally in GEM, pointer in ledger. Delete after use. Vertex uses **GCS `gs://`** instead of this Files store. |
| 7 | **`countTokens`** | REST + SDK | Pre-count input tokens before a call. `GenerativeModel.count_tokens` / `:countTokens`. | same | **$0**, no inference quota | **high** (spend-gate) | Spend-gate calls this (or estimates) **before** generate. Failed 400/500 still eat quota — count first. |
| 8 | **Embeddings (`embedContent`)** | REST + SDK | `POST …/models/gemini-embedding-2:embedContent` (multimodal: text/image/audio/video/PDF, 8k tok, 128–3072-d, MRL). Text-only `gemini-embedding-001` + `task_type`. Spaces **incompatible** across versions — re-embed on upgrade. | same | **Free** on free tier; paid $0.15/1M; batch 50% | **high** | Collector / chapter RAG / duplicate detection. Prefer **File Search** (row 16) if managed RAG is enough. |
| 9 | **Implicit context caching** | API | Automatic prefix-cache on Gemini 2.5+. Min tokens: 4,096 (Gemini 3.x), 2,048 (2.5). Hit → cheaper cached rate. Put stable corpus **first**. `usage.total_cached_tokens`. Interactions = implicit only. | same | **Free of charge** on several Flash SKUs; paid ~0.1× input + hourly storage on explicit | **high** | Always-on. For COSMOS repeated-doc critique, also use **explicit** cache (row 21) on generateContent. |
| 10 | **Gemini CLI built-in tools** (files/shell/web) | CLI tools | `read_many_files`, `run_shell_command`, web fetch, Google Search grounding — the model **acts on the machine** under CLI security/trusted-folders. `/tools` lists. | CLI auth | included in CLI request quota | **highest** (with row 1) | Same `gemini -p` worker. Restrict trusted folders to the attempt workspace. Sandbox docs: [geminicli.com/docs/cli/sandbox](https://geminicli.com/docs/cli/sandbox). |
| 11 | **Gemini CLI MCP host** | MCP | `~/.gemini/settings.json` MCP servers; `gemini mcp`; `/mcp reload`. `@server tool`. | per-server | **free** protocol; tokens when used | **high** | Point at GitHub MCP / Playwright / COSMOS MCP **from the CLI worker**, not from Core. |
| 12 | **Grounding with Google Search (Developer API)** | API built-in tool | Model searches, synthesizes, returns `url_citation` annotations + `google_search_call` queries. Combinable with URL context, Maps, code exec, custom functions (Gemini 3). | same | Free: 500 RPD on **2.x Flash** (not Pro). **3.x: not on Free API** (Studio-testable); paid 5k/mo then $14/1k **queries**. | **high** (cited web) | `tools=[{"type":"google_search"}]`. Vendor-plural with Firecrawl/Exa. Spend-cap 3.x. Prefer row 13 for known URLs. |
| 13 | **URL context** | API built-in tool | Fetch **specific URLs** into context (not a web search). | same | tokens; **$0 extra** (unlike Search) | **high** | `{"type":"url_context"}`. Known docs/DOIs. |
| 14 | **Gemini CLI GitHub Action** (`google-github-actions/run-gemini-cli`) | Actions | PR reviews, issue triage, `@gemini-cli` on-demand, scheduled workflows. | `GEMINI_API_KEY` or Vertex WIF in repo secrets | API tokens + Actions minutes (public = $0 minutes) | **high** | Workflow on `keithbbf-gif/cosmos`; Core `workflow_dispatch`. Lease vs Cursor Cloud Agents. |
| 15 | **OpenAI-compat endpoint** | REST | Drop-in OpenAI client → Gemini (`chat/completions`, Batch). | Studio key | same model prices | **high** (adapter) | If a worker already speaks OpenAI (Aider, etc.), point `OPENAI_API_BASE` at Gemini. Do **not** invent a second spend ledger. |
| 16 | **File Search (managed RAG)** | API built-in tool | Upload corpus to File Search Stores; model retrieves. Cheaper than stuffing full docs. | same | storage + retrieval SKUs (see pricing page tools section); free-tier availability model-specific | **high** | `tools=[{"type":"file_search","file_search_store_names":[…]}]`. Alternative to local embeddings+SQLite. |
| 17 | **Remote MCP in Interactions** | API tool | `tools: [{type:"mcp_server", name, url, headers, allowed_tools}]`. Streamable HTTP only. | Studio key + MCP token | tokens + MCP server cost | **high** | Let Gemini call GitHub/Playwright MCP **server-side** without COSMOS hosting the loop. snake_case names. |
| 18 | **Vertex / Agent Platform `generateContent`** | REST + SDK | Same multimodal generate on GCP: `POST https://{loc}-aiplatform.googleapis.com/v1/projects/{p}/locations/{loc}/publishers/google/models/{m}:generateContent`. Data stays under **paid Cloud ToS** (not "used to improve products" the way Studio free is). Global endpoint supported. | ADC / SA / Express key | **Vertex $300 credit** (MESH: expires **2026-10-13**) then PAYG. Welcome credit **does** apply here (unlike Studio API). | **highest** (already `gem-api`) | **Existing rail.** Keep using it until credit dies; then either Studio free Flash or real Vertex money. SDK: `genai.Client(vertexai=True, project=…, location="global")`. |
| 19 | **Vertex Express Mode** | REST + SDK | Vertex features with **only an API key**, no project in URL: `https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent?key=`. 90-day free for new `@gmail.com` GCP. | Express API key | **free 90 days** then billing | **high** (if eligible) | Probe whether Keith's GCP user still has Express. Else skip. |
| 20 | **Vertex function calling + Search grounding** | API tools | Identical tool loop on Vertex. Grounding can use **Google Search** or **Agent Platform Search** (enterprise corpus). Web Grounding for Enterprise is a **separate $45/1k** SKU. | ADC | tokens + grounding SKU ($35/1k grounded prompts on older Gemini; confirm live SKU) | **high** | `gem-api` tools config. Enterprise search is the Vertex-only hand Studio cannot do. |
| 21 | **Explicit context caching** | REST + SDK | `client.caches.create(model=…, config=CreateCachedContentConfig(contents, system_instruction, ttl))` then `cached_content=cache.name` on generateContent. **Not** on Interactions. Min token floors apply. | Studio paid (some Flash free) or Vertex | cache write + **hourly storage** + cheap reads | **high** (repeat docs) | Cache COSMOS canon / dissertation corpus for critique loops. TTL explicit. |
| 22 | **Batch API (Developer API)** | REST + SDK | Async bulk generate at **50%**. Inline (<20 MB) or JSONL via Files (2 GB). Target 24 h, often faster; expire 48 h. Results ~6 weeks. Embeddings batch too. Image batch (Nano Banana) for volume. Concurrent batches: 100. Enqueued-token caps per tier. Webhooks `batch.succeeded` / `batch.failed`. | Studio **paid** (Batch listed under Paid features; some Lite SKUs show free batch) | **50% of list** | **high** (bulk eval) | `client.batches.create(model=…, src=…)`. Poll or webhook → return-watcher. Critique/port-backlog. |
| 23 | **Vertex / Agent Platform batch prediction** | REST + SDK | `POST …/batchPredictionJobs`. JSONL on **GCS** or **BigQuery** in/out. Gemini + self-deployed Model Garden (Llama, …). Same 50% idea. | ADC | Vertex token 50% + GCS/BQ storage | **high** | When corpus already lives in GCS/BQ. Else Developer Batch is simpler. |
| 24 | **Model Garden** | console + SDK + REST | Discover/test/tune/deploy **200+** Google + partner (Claude, Llama, Mistral, Gemma, …) models. `vertexai.model_garden.list_deployable_models()`. Deploy → dedicated endpoint (GPU $) **or** use managed partner APIs (token $). | ADC + billing | **$0 to browse**; inference = partner/Google token or **VM/GPU** for self-deploy | **high** (vendor-plural) | Console/SDK from a worker. Do not self-deploy GPUs without a spend cap. Partner Claude on Vertex is a **second** Anthropic wallet — don't double-bill F5. |
| 25 | **Agent Development Kit (ADK) + `adk deploy`** | OSS framework + CLI | Open-source multi-agent kit (Python/Java). `adk deploy` → **Agent Engine**. MCP + A2A. Model-agnostic (Gemini or Garden). | ADC for deploy; local ADK is free | **ADK free** (OSS). Agent Engine = Vertex runtime $. | **high** | Optional COSMOS-external agent runtime. Overlaps Core scheduler — use only if Keith wants GCP-hosted agents. |
| 26 | **Agent Builder / Agent Garden / Agent Studio / Agent Engine** | GCP product | Lifecycle: Garden samples → Designer (low-code) → ADK → **Agent Engine** (managed runtime, sessions, Memory Bank, eval, identity). Console click-deploy. | Cloud login + billing | Vertex $ + Engine hours | **med-high** | DOM + `adk` CLI. Not a substitute for COSMOS Core. |
| 27 | **Gemini Agents API (Developer)** | REST | `POST https://generativelanguage.googleapis.com/v1beta/agents` — typed agents with code_execution / function / google_search tools. Overlaps Interactions. | Studio key | tokens | **med-high** | Prefer Interactions (GA, recommended). Agents API is the resource CRUD around that idea. |
| 28 | **Live API / audio** | WS + REST | Real-time audio-to-audio (`gemini-3.1-flash-live-preview`, `gemini-3.5-live-translate-preview`). Billed per audio token (~25 tok/s). | Studio key | free-tier listed on some Live SKUs; paid ~$0.005/min in + $0.018/min out (3.1 Flash Live) | **med** (voice) | Phone/voice clients. Not coding. |
| 29 | **Computer Use** | API built-in tool | Client-side computer-use loop (`functionCall`/`functionResponse` parts). Combinable on Gemini 3. | same | tokens; preview | **med-high** | Only inside a **contained** worker VM. Overlaps Playwright/browser-use. Vendor-plural, not default. |
| 30 | **Google Maps grounding** | API built-in tool | Places/routing-grounded answers. Gemini 3.5+ Flash. | same | 3.x: 5k prompts/mo free shared, then $14/1k | **med** | Niche (location). |
| 31 | **Image gen (Nano Banana / Gemini image)** | API | `gemini-3.1-flash-image`, Pro image preview, Omni Flash video. `response_modalities: IMAGE`. Batch for volume. | mostly **paid** | ~$0.045–$0.15/image depending on res; video ~$0.10/s 720p | **med** | KDash/docs figures. Not a coding rail. |
| 32 | **TTS (Flash TTS)** | API | `gemini-3.1-flash-tts-preview` text→audio. | Studio; free listed | $1/M in, $20/M audio out | **med** | Voice surface. |
| 33 | **Structured output / JSON schema** | API config | `response_mime_type` + `response_json_schema` / Pydantic. Combinable with tools on Gemini 3. | same | tokens | **high** (reliability) | Always on for COSMOS machine-readable returns. |
| 34 | **Webhooks (Developer API)** | REST | `client.webhooks.create(subscribed_events=["batch.succeeded","batch.failed"], uri=…)`. Push instead of poll. | Studio key | **$0** | **high** (infra) | Point at Core return-watcher (Tailscale/`cosmos up`). HMAC/verify per docs. |
| 35 | **Flex / Priority inference** | API service tier | Flex = cheaper/slower (batch-like $). Priority = 1.8× list, own RPM (0.3× standard). | paid | Flex 50%; Priority ~1.8× | **med** | Spend-gate `serviceTier`. Default Standard. |
| 36 | **AI Studio DOM (prompts, keys, billing)** | DOM | Mint/restrict keys, view rate limits, Playground, Build-mode deploy (Cloud **Starter Tier**: 2 apps without a GCP project), billing/prepay, spend caps. | Keith Google login | Studio UI **free**; paid key usage bills | **high as fallback** | `cosmos_browser` when AUTH_REQUIRED / key restrict / billing. Canon: DOM first when quota/billing can run out. |
| 37 | **Cloud Console (Vertex)** | DOM | Enable APIs, IAM, Model Garden deploy, Agent Garden, billing reports, GCS buckets for batch. | GCP login | console free | **high as fallback** | Same. Credit-expiry watch before 2026-10-13. |
| 38 | **Antigravity CLI (`agy`)** | CLI (successor) | Official banner: unpaid Gemini CLI users moved here **2026-06-18**. Closed-source Go binary; Google-login path. | Google login | unpaid individual plan (per Code Assist FAQ) | **med** (watch) | **Do not build COSMOS on this** until Keith chooses it. Prefer remaining OSS `gemini` + API key. Cite: [transition post](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli). |
| 39 | **gcloud / ADC bootstrap** | CLI | `gcloud auth application-default login`, `gcloud auth print-access-token`, enable `aiplatform.googleapis.com`. | user Google | **free** | **infra** | Keith runs once. COSMOS workers inherit ADC. No bats wrapping gcloud. |

---

## Two APIs, one mental model

| | **Gemini Developer API (AI Studio)** | **Vertex / Gemini Enterprise Agent Platform** |
|--|--------------------------------------|-----------------------------------------------|
| Base | `https://generativelanguage.googleapis.com/v1beta` | `https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{P}/locations/{L}` |
| Auth | API key (`x-goog-api-key`) | ADC / SA / Express key |
| Free | Generous Flash RPD; data **may train** | $300 GCP credit (Vertex **does** take it); Express 90-day |
| Paid | Prepay credits in AI Studio (Gemini-only) | Cloud Billing PAYG (all GCP) |
| Files | Files API, 48 h | GCS / BQ |
| Batch | `batches.create` + Files JSONL | `batchPredictionJobs` + GCS/BQ |
| Extra | Interactions, Agents, Studio UI | Model Garden, Agent Builder, enterprise Search, provisioned throughput |
| COSMOS today | **not** the registered rail | **`gem-api` / `bts_gem`** |

Unified SDK: [pypi.org/project/google-genai](https://pypi.org/project/google-genai/). REST generateContent: [ai.google.dev/api/generate-content](https://ai.google.dev/api/generate-content).

---

## What COSMOS should actually fire first

1. **Keep `gem-api` (Vertex) spend-gated** until the $300 credit's **2026-10-13** expiry — that credit **cannot** be spent on Studio API.
2. **Stand a Studio-key Flash lane** (`GEMINI_API_KEY` in `live/config/`) for $0 Flash generate/function-call/code-exec/Files — vendor-plural **and** a wallet that still works after Vertex credit dies.
3. **Gemini CLI `gemini -p --output-format json`** as a fourth coding-agent lane (alongside Claude Code, Cursor, Grok-Build), authenticated with that Studio key (not unpaid Google-login).
4. Enable **code execution + URL context** by default; **Google Search** only behind a cap (3.x is paid).
5. Use **Batch 50%** for bulk critique once on Paid; until then, live generate on Free Flash.

---

## Sources (official, fetched 2026-08-25)

**Gemini Developer API / AI Studio**

- [Gemini API docs home](https://ai.google.dev/gemini-api/docs)
- [Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Billing / tiers / Prepay](https://ai.google.dev/gemini-api/docs/billing)
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [generateContent REST](https://ai.google.dev/api/generate-content)
- [Interactions API](https://ai.google.dev/gemini-api/docs/interactions)
- [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Code execution](https://ai.google.dev/gemini-api/docs/code-execution)
- [Files API](https://ai.google.dev/gemini-api/docs/files)
- [Context caching](https://ai.google.dev/gemini-api/docs/caching) · [generateContent caching](https://ai.google.dev/gemini-api/docs/generate-content/caching)
- [Batch API](https://ai.google.dev/gemini-api/docs/batch-api)
- [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search)
- [Tool combination](https://ai.google.dev/gemini-api/docs/generate-content/tool-combination)
- [Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- [Gemini 3 guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [Agents API](https://ai.google.dev/api/agents)
- [File input methods](https://ai.google.dev/gemini-api/docs/generate-content/file-input-methods)
- [AI Studio](https://aistudio.google.com) · [Get API key](https://aistudio.google.com/apikey) · [Rate limit dashboard](https://aistudio.google.com/rate-limit)

**Gemini CLI**

- [Docs](https://geminicli.com/docs/) · [Auth](https://geminicli.com/docs/get-started/authentication.md) · [Quotas](https://geminicli.com/docs/resources/quota-and-pricing) · [Headless](https://geminicli.com/docs/cli/headless) · [Cheatsheet](https://geminicli.com/docs/cli/cli-reference/)
- [GitHub google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) · [npm @google/gemini-cli](https://www.npmjs.com/package/@google/gemini-cli)
- [GitHub Pages docs](https://google-gemini.github.io/gemini-cli/docs/)
- [Launch post](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-cli-open-source-ai-agent/)
- [Antigravity CLI transition](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli)
- [Code Assist quotas](https://developers.google.com/gemini-code-assist/resources/quotas)

**Vertex AI / Gemini Enterprise Agent Platform**

- [Agent Platform product](https://cloud.google.com/products/gemini-enterprise-agent-platform)
- [Agent Platform generative pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
- [Vertex generative pricing (legacy URL)](https://docs.cloud.google.com/vertex-ai/generative-ai/pricing)
- [Function calling](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tools/function-calling)
- [Batch from GCS](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-prediction-from-cloud-storage)
- [Batch prediction API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/batch-prediction-api)
- [Model Garden use](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-garden/use-models)
- [Cookbook](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/cookbook)
- [Express mode overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview) · [Express generateContent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/express-mode/rest/v1/publishers.models/generateContent)
- [Agent Builder overview](https://docs.cloud.google.com/agent-builder/overview) · [ADK on Agent Engine](https://docs.cloud.google.com/agent-builder/agent-engine/develop/adk)
- [Vertex quickstart](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/quickstart)
