# MESH ADDITIONS ARCH — Motif STAGE-2 + STAGE-3 locks + STAGE-6 satellite gate

**Stage:** 2 ARCHITECTURE, amended by stage-3 locks, slice-1 coded and `--gate` bound
2026-08-26. **Author:** G46 (Grok Build). **Date:** 2026-08-25T23:09-05 (ARCH);
locks 2026-08-26 (`docs/critique/meshadditions_STAGE3.md`); gate 2026-08-26T10:53-05.
**Assignment:** `motif_meshadditions_s2` then `s3` then `s6`.
**Inputs (asserted, then used):** `docs/MESH_ADDITIONS.md` (20-row research, UNVERIFIED),
`docs/MESH_ADDITIONS_grok.md` (G46 candidate backlog), maker-hands
`docs/research/{OLLAMA,GROQ,PLAYWRIGHT_MCP,BROWSER_USE,AIDER,FIRECRAWL,MCP_REFERENCE_SERVERS}_HANDS.md`,
rail contract `cosmos/cosmos_rails.py` + `cosmos/cosmos_cursor_rail.py`, DOM floor
`cosmos/cosmos_browser.py` (`--dump-dom` READ only), MCP *server* `cosmos/cosmos_mcp.py`
(Core spoken as MCP; **no client**).
**Host ground truth this pass:** git `56fa423` (`main` ahead 2), Node `v24.18.0`,
npm `11.16.0` via `cmd /c` (PowerShell `npm.ps1` is execution-policy blocked),
Chrome at `C:\Program Files\Google\Chrome\Application\chrome.exe`,
`nvidia-smi` `NVIDIA GeForce RTX 3070, 8192 MiB, driver 610.62`,
`glab 1.114.0`, `gh` on PATH. **No COSMOS core (kernel/ledger/sched/service) was edited.**

`rc=0` is not complete. Stage 6 for slice-1 is a **satellite `--gate`**
(`stage6.kind=satellite`, `kernel_attached=false`) quoting a value only the live
tree / vendor can emit. Kernel attach remains BACKLOG. See §11.

---

## 1. Decision rubric (stated first, per Motif stage 2)

A candidate is scored against these **before** any wiring design. Hard FAILS eliminates.
Soft criteria rank the survivors. No aggregate number.

### Hard (FAILS = do not wire)

| id | criterion |
|---|---|
| **H1 Hands** | The vendor exposes an **action** COSMOS can fire: CLI argv, HTTP endpoint, MCP `tools/call`, or a contained DOM driver. Chat-only chrome is out. A HANDS.md inventory of named tools/endpoints is the packet; a marketing page is not. |
| **H2 One authority** | Core stays the sole ledger writer. The candidate is a **worker / adapter**, never a second scheduler, never a second SEED, never a second spend ledger. Publish is the fenced commit gateway. |
| **H3 Fail-closed + typed absence** | Missing daemon, missing key, 401, 429, 402, connection refused → `UNREACHABLE` / `AUTH_REQUIRED` / `BROKE`. Registration is not capability. No silent fallback (DOM dead must not quietly become API). |
| **H4 Nothing-that-can-run-out preferred** | At equal power, local / keyless / prepaid outranks a meter. A rail that *can* run out is allowed only as an explicit overflow with a spend-gate ceiling. Rotating "free model" routers (silent vendor swap) FAIL. |
| **H5 Additive, no core edit** | Slice ships as a new module in the cursor-rail shape: `probe` / `dispatch`, `register_*`, `attach_to_kernel(kernel)` that does **not** edit `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service`. Kernel boot still does not attach rails (BACKLOG). This slice cannot close that hole. |
| **H6 Vendor-plural, not a twin** | The addition must be a **different family** or a **different capability class** than a live rail. Same-family chat on a new bill is overflow, not a first rail. SGH and GW are one family. Groq (LPU inference) is **not** Grok. |
| **H7 Blast radius** | Job-Object, attempt-private workspace, secrets only under resolver role `config/` (git-ignored), bind loopback, no Keith daily browser profile, no AGPL source folded into `cosmos/`. |
| **H8 Improvement is not bloat** | Net complexity and runtime cost trend down. A second orchestrator (n8n-as-scheduler), a second memory product, or a Python dep in Core when stdlib + a sidecar will do, FAILS. |

### Soft (rank the survivors)

| id | criterion |
|---|---|
| **S1 Cost now** | Free / already-on-the-box first. Keith does money and credentials; COSMOS does not mint keys or run installers. |
| **S2 Buildable on *this* machine today** | Node, Chrome, `cmd /c npx`, stdlib `urllib` are here. `uvx`, `ollama`, `aider`, `browser_use`, Groq/Firecrawl/Anthropic keys are **not**. Keith-gated install is a later slice, not a blocker for the design. |
| **S3 Runtime-binding path** | The design names the live-tree value the later `--gate` must quote (version JSON, `arxiv:` id, `tools/list` names, response `model`). Never an exit code. |
| **S4 Fewest new resident processes** | Prefer per-job stdio / HTTP. A sidecar (Ollama daemon) pays rent only if it is the unmetered overflow the canon requires. |
| **S5 Windows spawn truth** | PowerShell `*.ps1` may be execution-policy blocked (measured this pass on `npm.ps1`). Production spawn is `cmd /c` or `node.exe` + argv list, never a `.bat`, never `shell=True`. |

### How a row is classified

| class | meaning | next |
|---|---|---|
| **WIRE** | H1–H8 hold. Hands verified (docs + at least one live packet or a typed UNREACHABLE). Slice-ready. | stage 3 critique, then stage 4 code |
| **HOLD** | Hands real, but Keith-gated (install / key / card) or depends on a WIRE sibling. | design now; build after the gate |
| **OVERFLOW** | Hands real, capability overlaps a live rail; keep as quota overflow, not a default. | do not build first |
| **REJECT** | Fails a hard criterion, or the named product is dead. | do not promote |

---

## 2. Research packets (asserted before reasoning)

Maker-hands files exist on disk and name tools, URLs, auth, and cost. MESH_ADDITIONS.md
called every row UNVERIFIED. This pass **does not re-research vendors**. It checks
whether each named hand (a) exists in those packets and (b) answers from *this* host.

| packet | what it claims | used for |
|---|---|---|
| `OLLAMA_HANDS.md` | Local REST `127.0.0.1:11434`, OpenAI shim `/v1/chat/completions`, no key, MIT, Cloud is a different wallet | H1, H4, HOLD-until-install |
| `GROQ_HANDS.md` | `api.groq.com/openai/v1`, keys `gsk_`, **not** xAI Grok; Llama 3.x Free/Dev shutdown 2026-08-16; Mixtral dead; default `openai/gpt-oss-20b` | H1, H6 name-collision |
| `PLAYWRIGHT_MCP_HANDS.md` | `@playwright/mcp` Apache-2.0, a11y snapshot refs, npm `0.0.79` | H1 DOM upgrade |
| `BROWSER_USE_HANDS.md` | MIT OSS Agent; Cloud trains; telemetry default-on | H4 local-only, H8 |
| `AIDER_HANDS.md` | Apache-2.0 CLI `--message --yes-always`, BYO model, auto-commit | H2 fence vs aider commits |
| `FIRECRAWL_HANDS.md` | Keyless scrape/search/papers; AGPL self-host is a **separate process** | H1 Chapter-4, H7 AGPL |
| `MCP_REFERENCE_SERVERS_HANDS.md` | 7 live refs; educational not production; archived GitHub/Puppeteer dead | H1 Fetch; REJECT archives |
| `cosmos_cursor_rail.py` | Additive API rail pattern that does not edit kernel | H5 shape |
| `cosmos_browser.py` | `--dump-dom` is READ; "Interactive automation is a later CDP upgrade" | hole Playwright fills |
| `cosmos_mcp.py` | COSMOS-as-**server**; tools are Core verbs | hole: no MCP **client** |

No mid-run packet failure. Grok-family MESH_ADDITIONS_grok.md is the same family as this
architect — it is prior art, **not** a second vote. Stage 3 still owes a different-family
critique. Nothing here is CONTESTED between packets; Groq Llama-3 shutdown vs MESH_ADDITIONS
row 2's older "Llama-3-70B" blurb is a **correction**, not a contest.

---

## 3. Hands verification — this machine, 2026-08-25T23:09-05

Host-side probes. Quotes are the artifact. Absence is typed.

### 3.1 Live packets (something answered)

| candidate | probe | live value |
|---|---|---|
| **Playwright MCP** | `cmd /c npx -y @playwright/mcp@0.0.79 --help` → rc 0 | Usage banner `Playwright MCP [options]`; flags include `--headless`, `--isolated`, `--browser`, `--caps`, `--output-dir`, `--port`. npm registry: `name=@playwright/mcp version=0.0.79 license=Apache-2.0 mcpName=io.github.microsoft/playwright-mcp bin=playwright-mcp→cli.js`, `engines.node >=18` (host Node **v24.18.0**). |
| **Firecrawl keyless scrape** | `POST https://api.firecrawl.dev/v2/scrape` `{"url":"https://docs.firecrawl.dev/introduction","formats":["markdown"]}` no Bearer | **HTTP 200** `{"success":true,"data":{"markdown":"> ## Documentation Index\n>\n> Fetch the complete documentation index at: [/llms.txt]…` |
| **Firecrawl keyless search** | `POST https://api.firecrawl.dev/v2/search` `{"query":"playwright mcp microsoft","limit":2}` | **HTTP 200** `success:true`; first hit `https://github.com/microsoft/playwright-mcp` title `Playwright MCP server`. |
| **Firecrawl Research Index** | `GET https://api.firecrawl.dev/v2/search/research/papers?query=Lindau+theorem+superluminal` (no `limit` — `limit` is **400** `unrecognized_keys`) | **HTTP 200**, 38578 bytes. First record `primaryId":"arxiv:physics/0103087"`, title `Thoughtful comments on 'Bessel beams and signal propagation'`, abstract discusses superluminal wave fronts vs finite-energy pulses. |
| **Groq endpoint** | `GET https://api.groq.com/openai/v1/models` no key | **HTTP 401** `{"error":{"message":"Invalid API Key","type":"invalid_request_error","code":"invalid_api_key"}}` — the hand exists; this host has no `gsk_`. |
| **Ollama daemon** | `GET http://127.0.0.1:11434/api/version` | **UNREACHABLE** `WinError 10061` connection refused. `ollama` not on PATH. Default install paths missing (`%LOCALAPPDATA%\Programs\Ollama\ollama.exe`, `C:\Program Files\Ollama\ollama.exe`, `%USERPROFILE%\.ollama`). |
| **GPU (Ollama capacity)** | `nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv` | `NVIDIA GeForce RTX 3070, 8192 MiB, 610.62`. CIM `AdapterRAM` 4293918720 is the 32-bit wrap; **8 GiB is ground truth**. Local 30B-coder models (HANDS: ≥24 GB) will **not** fit. |

### 3.2 Typed absence (not a fail — H3)

| surface | fact |
|---|---|
| `live/config/` keys | Present: `api_token.txt`, `cursor_cosmos_key.txt`, `cursor_rail.json`, `cursor_rail_probe.json`, `install_key.bin`, `install_record.json`. **Absent:** `groq_api_key.txt`, `firecrawl_api_key.txt`, `ollama_api_key.txt`, `anthropic` / `browser_use` / `mistral` / `deepseek` keys. |
| env | `GROQ_API_KEY`, `FIRECRAWL_API_KEY`, `OLLAMA_API_KEY`, `ANTHROPIC_API_KEY`, `BROWSER_USE_API_KEY`, `MISTRAL_API_KEY`, `DEEPSEEK_API_KEY` all **ABSENT**. |
| Python 3.14 imports | `browser_use` NO · `ollama` NO · `groq` NO · `firecrawl` NO · `aider` NO · `playwright` NO · `mcp` NO. Slice 1 must not need them (stdlib + sidecar). |
| `uvx` | not on PATH. Python MCP reference servers that document `uvx mcp-server-fetch` are HOLD until `uv` exists **or** a pip-isolated worker is used. |
| `aider` | not on PATH. |
| PowerShell `npm` | `npm.ps1` SecurityError UnauthorizedAccess. `cmd /c npm --version` → `11.16.0`. **S5 is measured, not theoretical.** |

### 3.3 Verdict per MESH_ADDITIONS.md row

| # | name | H1 hands? | this-host | class |
|---|---|---|---|---|
| 1 | Ollama | YES (REST+CLI+shim, HANDS) | daemon UNREACHABLE; GPU 8 GiB ready | **HOLD** (Keith install). Design now; `--gate` after `ollama serve` answers `/api/version`. |
| 2 | Groq API | YES (OpenAI-compat; **not Grok**) | 401 invalid_api_key | **HOLD** (Keith mints `gsk_`). Default model **`openai/gpt-oss-20b`**, not Llama-3-70B (shutdown). Mixtral **REJECT** (dead 2026-03-20). |
| 3 | Playwright MCP | YES | **WIRE** — package + `--help` ran here | **WIRE** slice 1. Pin `0.0.79`. |
| 4 | browser-use OSS | YES (Agent/Actor/local MCP) | pkg NO; Cloud **do not wire** | **HOLD** behind Ollama or an existing LLM rail. Telemetry `ANONYMIZED_TELEMETRY=false` required. |
| 5 | MCP reference servers | YES (7 live); archives unmaintained | `uvx` ABSENT; Fetch is the $0 URL-read | **OVERFLOW** of Firecrawl for known URLs. Fetch **HOLD** until spawn path exists. Filesystem/Git writers: attempt workspace only. Sequential Thinking / Memory: **REJECT** as competing SEED (H2). Puppeteer archive: **REJECT** (Playwright is the live DOM). |
| 6 | Aider | YES (CLI `--message`) | binary ABSENT; needs isolated Py 3.12 | **HOLD** coding-overflow worker. `--no-auto-commits` so Core fences. |
| 7 | Copilot CLI | YES (GitHub) | `gh` present; Copilot CLI not probed as a new daily driver | **OVERFLOW**. Cursor + Claude Code + Grok-Build already occupy coding. |
| 8 | Codex CLI | YES | overlaps `oa-api` | **OVERFLOW**. |
| 9 | Firecrawl | YES | **WIRE** keyless scrape + search + papers (live JSON) | **WIRE** slice 1. Papers `limit` param is invalid. Crawl/map need `fc-` key (HOLD). AGPL self-host = separate process, not `cosmos/`. |
| 10 | Exa | YES, metered | not probed (paid overlap) | **OVERFLOW** of Firecrawl. |
| 11 | LlamaParse | YES, PDF | overlaps Firecrawl `/parse` | **OVERFLOW**. |
| 12 | Mistral API | YES | no key | **OVERFLOW** after Ollama (local Mistral tags) / Groq. |
| 13 | DeepSeek API | YES, then metered | no key; distill via Ollama | **OVERFLOW**. |
| 14 | Perplexity Sonar | YES, grounded search | no key | **OVERFLOW** of Firecrawl papers+search. |
| 15 | Hugging Face Inference | YES, weak free tier | — | **OVERFLOW** / low. |
| 16 | OpenRouter `free` rotator | YES but silent model swap | — | **REJECT** H3/H4 (silent fallback). Pin a named model only if Keith ever wants the router. |
| 17 | Anthropic Messages API | YES | no `sk-ant`; F5/`claude -p` already prepaid | **OVERFLOW** when Claude Code weekly is dry. Real money. Keith-gated. |
| 18 | GitHub CLI `gh` | YES | **on PATH** | Already a host tool. Not a new rail; queue jobs may call it. Native `gh`, not archived GitHub MCP. |
| 19 | Zapier MCP | metered task quota | — | **REJECT** H4/H8. |
| 20 | n8n CE | YES as orchestrator | — | **REJECT** as scheduler (Core already is). Revisit only as a narrow SaaS-bridge if a named integration appears. |

**Already on the mesh (do not re-add):** `sgh-api` / `gem-api` / `gw-api` / `oa-api` (node_rails specs; Kernel still does not attach — BACKLOG), `cursor-api` (additive rail, `--gate` bound), Claude Code `claude -p`, Grok-Build, `cosmos_browser` dump-dom, `cosmos_mcp` **server**, `glab`, `gh`.

---

## 4. Decision — what to build, in what shape

**Build three additive adapters in the cursor-rail pattern, plus one MCP-client that they share. Do not edit Core.**

```
                    ┌─────────────────────────────────────────┐
  isolated --gate   │  adapters[link_id]  (probe / dispatch)  │
  Dispatcher        └───────────────┬─────────────────────────┘
  (NOT the live     (cosmos_rails.Dispatcher on state/<rail>/gate.jsonl)
   daemon; NOT      authority attach REFUSED until Kernel boot_compose)
   Kernel boot)
          ┌─────────────────────────┼──────────────────────────┐
          ▼                         ▼                          ▼
   playwright-dom              firecrawl-web              ollama-local / groq-api
   kind=DOM                    kind=API                   kind=API
   core->interact              core->papers               HOLD until daemon/key
   stdio MCP                   HTTP urllib
          │                    keyless first
          ▼
   cosmos_mcp_client  (NEW)     cosmos_mcp SERVER stays inbound
   stdio JSON-RPC               (KDash/Claude talk TO Core)
   Windows: node.exe+cli.js or cmd /c npx
```

The **missing piece** named by MESH_ADDITIONS_grok.md is real: `cosmos_mcp` exposes Core;
nothing in Core speaks *out* as an MCP client. Playwright is the first consumer of that
client. Firecrawl slice 1 does **not** need MCP (keyless REST is proven). Ollama/Groq
are OpenAI-shaped HTTP, same as `oa-api` / `cursor-api`.

### 4.1 Shared adapter contract (lock this)

Copy the proven shape from `CursorRail` / `CliRail` / `DomRail` / `ApiRail`:

```
kind            in {CLI, API, DOM, CHAT, OTHER}   # Registry RAIL_TYPES. MCP is *transport*, not a type.
link_id         stable string (spec overlay in live/config/<name>_rail.json)
probe()      -> (ok: bool, detail: str)     # cheapest liveness; NEVER the paid/heavy call
dispatch(p)  -> {ok, kind, text|data, node, ... typed failure}
metered_usd  0.0 unless a real bill exists
register_*(registry, adapters, spend_gate=None, paths=None)
attach_to_kernel(kernel)   # additive; authority ledger REFUSED unless boot_compose=True
--gate                     # writes live/config/<name>_rail_probe.json with a live value
--selftest                 # fake transport; green log; NOT the gate
```

Playwright `kind=DOM`. Firecrawl `kind=API`. The MCP client is a stdio helper,
not a Registry type (`BAD_TYPE` if `MCP` is passed).

Secrets: `paths.config(key_name)` only. Never in the spec JSON. Redact to prefix+last4
in probe records (cursor pattern).

Typed failures stay the DOM/API vocabulary already in Core: `UNREACHABLE`,
`AUTH_REQUIRED`, `BROKE`. HTTP **402/429 map to `BROKE` + `http=`** — not
`UNREACHABLE`. Dispatcher `RAIL_FALLBACK` on `UNREACHABLE` would hide a cap as
"down" (STAGE3 H4). Visible refusal, not a retry loop inside the adapter.

### 4.2 Slice 1 — WIRE now (stage 4, after stage 3)

Three new files. Stdlib Python. No new pip in Core. No bats.

#### A. `cosmos/cosmos_mcp_client.py` — COSMOS-as-MCP-client

- Spawn `command + args + env` from a spec. JSON-RPC 2.0 newline-delimited stdio
  (`initialize` → `tools/list` → `tools/call`).
- Windows: if command is `npx`, spawn `cmd.exe /c npx ...` (S5). Argv list, no shell
  interpolation of the prompt.
- Probe = `tools/list` names (cheap). Dispatch = one `tools/call`.
- `cosmos_platform.run` / `run_tree_killed` cannot keep a pipe (no stdin=PIPE; no
  Job-Object in the tree). This module owns the Popen (`stdin=PIPE`) and
  tree-kills on timeout with `taskkill /T` on the cmd/node pid (grandchildren).
  Do not claim Job-Object in slice-1. That is the only new moving part, and it
  pays rent: every later MCP server reuses it.
- Allowlist the tool names a job may call. `browser_run_code_unsafe` is **off** unless
  the job spec opts in (RCE-equivalent per PLAYWRIGHT_MCP_HANDS).
- Does **not** modify `cosmos_mcp.py` (server). Two faces, one protocol.

#### B. `cosmos/cosmos_playwright_rail.py` — `link_id="playwright-dom"`

- `kind="DOM"`, route `core->interact` (distinct dst). `policy_rank=0` — **do not**
  outrank dump-dom on a shared route (STAGE3 R6: Registry.route has no job class).
  dump-dom remains the cheap READ (H8: do not delete `cosmos_browser`).
- Spawn (pin version, measured; STAGE3 R5: `--browser chrome`, not `chromium`):

```
Prefer node.exe + pinned @playwright/mcp@0.0.79 cli.js (no cmd parser).
Fallback: cmd.exe /c npx -y @playwright/mcp@0.0.79 --headless --isolated --browser chrome --output-dir <attempt>/pw --image-responses omit --console-level error
```

  Optional `--executable-path` from `cosmos_browser.discover_browser()` at runtime —
  no drive literal in the module. Help text lists `--caps` extra values
  `vision, pdf, devtools`. Do not pass `--caps` on the default worker. Opt-in per job.
- Probe: `tools/list` contains `browser_navigate` and `browser_snapshot` (bound
  live: 24 names). `--help` is not the probe and is not the gate.
- Dispatch payload: `{url, steps?}` → `browser_navigate` then `browser_snapshot`.
  Click/type only when `steps` is present. Screenshots are artifacts hashed into
  GEM; ledger holds the pointer. `file://` dispatch is BROKE.
- `browser_run_code_unsafe` is **client-denied** (it is in the default 24).
- Profile: `--isolated` always for unattended jobs. Never `--extension` / Keith's
  daily Chrome. Chrome binary exists (probe path above).
- Gate value: snapshot of a **loopback HTTP** page containing
  `tree_id=KMesh-COSMOS-live`. Never `file://`. Bound 2026-08-26T10:53:58-05: see §11.

#### C. `cosmos/cosmos_firecrawl_rail.py` — `link_id="firecrawl-web"`

- `kind="API"`, `metered_usd=0.0`, budget $0. Keyless default.
- Base `https://api.firecrawl.dev`. Stdlib urllib. UA identifies COSMOS (papers
  polite-pool).
- Verbs: `scrape` (POST `/v2/scrape`), `search` (POST `/v2/search`), `papers`
  (GET `/v2/search/research/papers?query=`). **Do not send `limit` on papers**
  (live 400 `unrecognized_keys:["limit"]`).
- Probe: papers returning a `primaryId` (`arxiv:` / `doi:` / `pmid:`). Scrape
  `success: true` is a dispatch verb, not the first `--gate`. `--gate` files
  `live/config/firecrawl_rail_probe.json`. Bound 2026-08-26T10:53:54-05:
  `primaryId=arxiv:physics/0103087`. See §11.
- Optional overlay: `live/config/firecrawl_api_key.txt` (`fc-…`) raises RPM and
  unlocks crawl/map. Missing key → keyless path, not UNREACHABLE. Crawl without
  a key → typed `AUTH_REQUIRED`.
- Spend-gate: still ledger `RAIL_DISPATCH` / `RAIL_RESULT` at $0 on the
  **isolated** `--gate` ledger so the collector sees the call. HTTP 402/429 →
  `BROKE` + `http=` (not `UNREACHABLE`). Smart Upgrade must stay off if a key is
  ever added (fail-closed 402).
- AGPL self-host (`localhost:3002`) is a **later sidecar**, not slice 1. Do not
  vendor Firecrawl source into `cosmos/`.
- Gate value: a `primaryId` such as `arxiv:physics/0103087` (bound
  2026-08-26T10:53:54-05 in `live/config/firecrawl_rail_probe.json`) **or** a
  later Chapter-4 query Keith names. Quote the JSON; do not retell the abstract
  as proof. Route is `core->papers` so this does not capture READ/search.

### 4.3 Slice 2 — HOLD (Keith does credentials / install)

#### D. `cosmos/cosmos_ollama_rail.py` — `link_id="ollama-local"`

- `kind="API"`, `metered_usd=0.0`. Base `http://127.0.0.1:11434`. Dummy OpenAI
  key `ollama` on the `/v1` shim. Prefer native `/api/chat` when `num_ctx` /
  tools / `think` matter (OpenAI shim cannot set context — HANDS).
- Probe: `GET /api/version` + `GET /api/tags`. Today: UNREACHABLE 10061. That is
  the correct probe result until Keith installs the native Windows app
  ([OllamaSetup.exe](https://ollama.com/download/OllamaSetup.exe)). COSMOS does
  not install software for him (no bats; Keith runs COSMOS).
- After install, `--gate` binds the version JSON **and** a non-empty `models`
  list. Empty tags = registered-but-unusable (H3), not a fake chat.
- Models for **8 GiB**: smoke `llama3.2:3b` or `qwen3:8b`; embed
  `embeddinggemma` / `all-minilm`. Do **not** default `qwen3-coder` 30B
  (HANDS: ≥24 GB). `OLLAMA_NO_CLOUD=1` until Keith opts in. Bind 127.0.0.1;
  do not set `OLLAMA_HOST=0.0.0.0`.
- Sidecar: the tray app *is* the resident process. Core does not start it.
  Dead daemon = UNREACHABLE, never a silent skip to Groq/OpenAI.

#### E. `cosmos/cosmos_groq_rail.py` — `link_id="groq-api"`

- **Not Grok.** Different vendor, different silicon, different key (`gsk_`).
- Base `https://api.groq.com/openai/v1`. Cursor-rail HTTP shape.
- Probe: `GET /models` with Bearer. Today 401 `invalid_api_key` is the honest
  state. After Keith stores `live/config/groq_api_key.txt`, probe must see
  `openai/gpt-oss-20b` in the list (live IDs, not this markdown).
- Dispatch: chat completions, default model `openai/gpt-oss-20b`. Persist
  `usage` + `x-ratelimit-*` + `retry-after` into the result. Runtime
  binding = the `model` string **in the response**, not the one in the
  prompt. Header units (vendor 2026-09-04): `*-requests` = RPD, `*-tokens`
  = TPM. 429 is BROKE. Live cap is Console settings/limits, not the docs
  table. https://console.groq.com/docs/rate-limits
- Budget $0 (Free tier). Spend-gate refuses if a Developer invoice appears
  without a new budget (Keith does money). Batch/Flex stay dark.
- Do not dispatch `mixtral-8x7b-32768` or Llama 3.x Free/Dev IDs.
- Cookbook https://github.com/groq/groq-api-cookbook is a **research
  pointer** (guides + tutorials 01–10, fetched 2026-09-04). Not a COSMOS
  rewrite. Tutorial 01 batch-processing does **not** lift Batch/Flex.
  Llama-3 stock tutorials are stale vs catalog ContactSales. Firecrawl
  MCP in the cookbook is a recipe; COSMOS already has `firecrawl-web`.
  Do not vendor-lock into LangChain / CrewAI / LiteLLM.

### 4.4 Slice 3 — HOLD (depends on slice 1–2)

| module | why later |
|---|---|
| browser-use OSS worker | Needs an LLM. Point at `ollama-local` or `gem-api`. `ANONYMIZED_TELEMETRY=false`. `allowed_domains` required. Cloud MCP / `bu_` key: **do not wire** (H4). Complements Playwright (open-ended vs a11y-tree) — vendor-plural DOM, H6. |
| Aider CLI worker | Attempt workspace only. `--yes-always --analytics-disable --no-stream --no-suggest-shell-commands`. `--no-auto-commits` so the fence, not Aider, publishes. `--model` from whichever rail has headroom (`ollama_chat/…` or Groq or existing). Isolated `aider-install` Python 3.12 — do not drag Aider into 3.14 Core. |
| MCP Fetch | $0 known-URL read in front of Firecrawl. Blocked today by missing `uvx`. After `uv` or a pinned pip worker: stdio via the MCP client. SSRF allowlist. |

### 4.5 Explicitly out of this architecture

| item | why |
|---|---|
| n8n as orchestrator | H2/H8 — Core already schedules. |
| Zapier | H4 meter for almost no COSMOS consumer. |
| OpenRouter rotating `free` | H3 silent fallback. |
| LiteLLM proxy sidecar | Second spend surface. Ollama + Groq already speak OpenAI-shape. Revisit if many CLI agents need one base URL. |
| Kernel.`__init__` calling `register_node_rails` | LIVE CORE BACKLOG. This slice uses `attach_to_kernel` like Cursor. |
| Folding Firecrawl / Playwright source into `cosmos/` | Sidecars. AGPL especially stays a process boundary. |
| `browser_run_code_unsafe` default-on | RCE. Opt-in + Job-Object only. |
| Keith daily Chrome via `--extension` | Session cookies / bank tabs. |
| Bats, drive literals, import-time path assembly | Canon. |

---

## 5. Auth and secrets

| rail | credential | where | missing behavior |
|---|---|---|---|
| playwright-dom | none (local Node + Chrome) | — | UNREACHABLE if `npx`/`node`/`chrome` absent |
| firecrawl-web | none (keyless); optional `fc-…` | `paths.config("firecrawl_api_key.txt")` | keyless verbs still run; crawl/map → AUTH_REQUIRED |
| ollama-local | none on localhost | Cloud key only if Keith opts in | UNREACHABLE until daemon listens |
| groq-api | `gsk_…` | `paths.config("groq_api_key.txt")` | UNREACHABLE 401 (already measured) |
| browser-use Cloud | `bu_…` | not wired | — |
| Anthropic API | `sk-ant-…` | overflow only | F5 subscription stays the Claude path |

Keith owns minting. COSMOS never prints a key in full. Spec JSON never contains secrets.

---

## 6. Routing (how Dispatcher should pick them)

Existing `docs/ROUTING.md` is per-task, not a blanket. Additions slot in as:

| job class | first live link | overflow |
|---|---|---|
| **Use a site** (click, fill, snapshot) | `playwright-dom` (satellite `--gate` live; Kernel attach BACKLOG) | browser-use OSS (slice 3); dump-dom stays READ-only |
| **Read a known URL → markdown** | dump-dom first (H4; STAGE3 R11) | Firecrawl keyless scrape **or** MCP Fetch (when spawned) |
| **Web search** | SGH DOM (prepaid, `docs/ROUTING.md` default) | Firecrawl keyless search (overflow; unpublished per-IP cap) |
| **Chapter-4 papers / DOI / related** | Firecrawl Research Index (keyless, **$0**, `core->papers`) | SGH prompt-hunt (the thing this replaces) |
| **Cheap / offline / quota-dry chat** | `ollama-local` (after install) | Groq free-tier → existing `sgh-api`/`gw-api`/`oa-api` |
| **Bulk / low-latency agent loops** | `groq-api` gpt-oss-20b (~1000 t/s) | Ollama local (slower, cannot run out) |
| **Coding** | unchanged: Claude Code default, Grok-Build overflow, Cursor `cursor-api` | Aider (slice 3) pointed at Ollama/Groq |

DOM-first remains policy. A dead `playwright-dom` is UNREACHABLE, not a silent
Groq call that claims it "looked at the page."

---

## 7. Runtime-binding gates (stage 6 — named now, not claimed)

| rail | value only the live tree / vendor can emit |
|---|---|
| playwright-dom | **BOUND 2026-08-26T10:53:58-05** `live/config/playwright_rail_probe.json` `gate=PASS`: `tools/list` 24 names from spawned 0.0.79 **and** `browser_snapshot` containing `tree_id=KMesh-COSMOS-live` via `http://127.0.0.1:59571/` (not `file://`, not `--help`). `kernel_attached=false`. |
| firecrawl-web | **BOUND 2026-08-26T10:53:54-05** `live/config/firecrawl_rail_probe.json` `gate=PASS`: HTTP 200 `success: true` `primaryId=arxiv:physics/0103087`. Quote those fields. `kernel_attached=false`. |
| ollama-local | `GET /api/version` `{"version":"…"}` plus a `/api/chat` `message.content` whose `model` is in `/api/tags`. 10061 is the current honest probe. |
| groq-api | `GET /models` list containing `openai/gpt-oss-20b` **and** a chat response `id` / `model` with `x-groq` request metadata. 401 is the current honest probe. |

`--selftest` with fake HTTP is a green log. It does not move the tracker to
"complete."

---

## 8. Stage-4 file plan (after stage-3 consensus)

| path | role |
|---|---|
| `cosmos/cosmos_mcp_client.py` | stdio MCP client + Windows `cmd /c` npx spawn |
| `cosmos/cosmos_playwright_rail.py` | DOM adapter + `--gate` |
| `cosmos/cosmos_firecrawl_rail.py` | API adapter + `--gate` |
| `tests/test_mcp_client.py` | fake stdio, no network |
| `tests/test_playwright_rail.py` | fake MCP, no browser |
| `tests/test_firecrawl_rail.py` | fake HTTP |
| `live/config/playwright_rail.json` | spec, no secrets (git-ignored runtime) |
| `live/config/firecrawl_rail.json` | spec |
| `docs/MESH_ADDITIONS.md` | verified column (updated this stage) |

HOLD files **not** opened in slice 1: `cosmos_ollama_rail.py`, `cosmos_groq_rail.py`.
Their contracts are in §4.3 so stage 4 does not invent them under a deadline.

Estimated new Core Python: MCP client + two thin adapters. Playwright and Firecrawl
stay out-of-process. That is H8: capability up, Core weight small, dump-dom kept.

---

## 9. What this stage did **not** do

- Did not edit `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service`.
- Did not install Ollama, mint Groq/Firecrawl keys, or `pip install` anything into Core.
- Did not spawn a headed/headless **browser session** (Playwright `--help` only — no
  Chromium download claimed as "DOM works").
- Did not treat Firecrawl papers HTTP 200 as COSMOS stage 6 (the rail is not attached).
- Did not resolve Kernel attach (BACKLOG).
- Did not run a different-family architecture (stage 2 is this node; stage 3 is
  consensus). Same-family prior art: `docs/MESH_ADDITIONS_grok.md`.

---

## 10. Next Motif stage

**Stage 3 CONSENSUS:** different-family critique of *this* design vs the rubric in §1
and the live table in §3. Question: "is this the thing we should wire," not "is this
good prose." CONTESTED items go to Keith as one line each.

Likely non-contested: Playwright + Firecrawl keyless + MCP-client as slice 1;
Ollama/Groq as Keith-gated slice 2; n8n/Zapier/OpenRouter-free rejected.

If stage 3 agrees, stage 4 codes slice 1 on a branch. Stage 5 different-family
review vs this document. Stage 6 is the `--gate` JSON in `live/config/`.

---

## 11. STAGE-3 locks applied + STAGE-6 satellite proof (2026-08-26)

No `docs/critique/meshadditions_*STAGE5*` file existed. HIGH/MED from
`docs/critique/meshadditions_STAGE3.md` were applied additively in slice-1
code. Same-family process still owes gem-api/oa-api a pass on the ARCH (family
hole, not a design contest). Kernel/ledger/sched/service were **not** edited.

### Locks (do not regress)

| lock | applied |
|---|---|
| Satellite `--gate`, not Dispatcher-on-boot | `attach_to_kernel` REFUSED on authority. Probe JSON `kernel_attached=false` is a PASS predicate. Isolated `cosmos_rails.Dispatcher`, not `cosmos_dispatcher_daemon`. |
| `kind` | Playwright `DOM`. Firecrawl `API`. MCP is transport. Registry has no `MCP` type. |
| Routes | `playwright-dom` `core->interact`. `firecrawl-web` `core->papers`. dump-dom stays READ. ROUTING.md search stays SGH DOM. |
| `policy_rank` | 0. Not above dump-dom. |
| 402/429 | `BROKE` + `http=`. Not `UNREACHABLE` (no `RAIL_FALLBACK`). |
| Spawn | Pin `0.0.79`. `--browser chrome`. No `--caps`. Prefer `node.exe`+cli.js. `taskkill /T`, not Job-Object. |
| Unsafe | `browser_run_code_unsafe` client-denied (listed in default 24). |
| Gate URL | `http://127.0.0.1` only. `file://` BROKE. |
| Papers | GET `/v2/search/research/papers?query=` — no `limit`. REST, not hosted MCP. |
| HOLD | Ollama / Groq / browser-use / Aider / MCP Fetch. REJECT n8n / Zapier / OpenRouter rotating `free` / Mixtral. |

### Live `--gate` (not `--selftest`)

`--selftest` (fake transport): MCP client 8/8, firecrawl-web 20/20, playwright-dom 18/18. That is a green log.

**Firecrawl live:** `py -3.14 cosmos\cosmos_firecrawl_rail.py --root V:\A\Ai\COSMOS\live --gate`

Proof artifact: `live/config/firecrawl_rail_probe.json`

Emitted value (quoted from that file):

`firecrawl-web probe_ok=True primaryId='arxiv:physics/0103087' http=200 tree_id=KMesh-COSMOS-live route=core->papers attach_refused=True kernel_attached=False`

`gated_at=2026-08-26T10:53:54-05:00` `success=true` `title=Thoughtful comments on 'Bessel beams and signal propagation'` `Date=Wed, 26 Aug 2026 15:53:53 GMT`.

**Playwright live:** `py -3.14 cosmos\cosmos_playwright_rail.py --root V:\A\Ai\COSMOS\live --gate`

Proof artifact: `live/config/playwright_rail_probe.json`

Emitted value (quoted from that file):

`playwright-dom probe_ok=True tools=24 snapshot_has_tree_id=True tree_id=KMesh-COSMOS-live url=http://127.0.0.1:59571/ route=core->interact attach_refused=True kernel_attached=False`

Snapshot head (a11y tree the spawned 0.0.79 server actually returned):

```
- heading "COSMOS mesh additions stage-6 gate" [level=1] [ref=e2]
- paragraph [ref=e3]: tree_id=KMesh-COSMOS-live
```

`serverInfo.name=Playwright` `version=1.63.0-alpha-2026-08-05`. `browser_run_code_unsafe` listed (`unsafe_listed=true`); client denies `tools/call`.

### Honest limit

- Production Kernel still does not attach these rails (`live_kernel.playwright_in_registry=false`, `firecrawl_in_registry=false`).
- Ollama still UNREACHABLE 10061; Groq still 401 without `gsk_`. Slice 2 HOLD.
- Different-family (gem/oa) critique of this ARCH is still owed.
- `rc=0` is not the proof. The probe JSON is.
)
