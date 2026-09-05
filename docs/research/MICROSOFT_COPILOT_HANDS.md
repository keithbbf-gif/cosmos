# MICROSOFT COPILOT HANDS — G46 scout return (M365 Copilot APIs, Graph, Copilot Studio, Azure AI Foundry / Azure OpenAI, Power Platform, DOM chat)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live from learn.microsoft.com).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim except where a COSMOS artifact is named.
**No COSMOS core code was edited.** Maker-docs sweep (DHx assignment log): each maker's hands → `docs/research/<MAKER>_HANDS.md`.

**Already on the mesh (do not re-add as "new"):** Dispatcher rails **`sgh-api` / `gw-api` / `gem-api` / `oa-api`**. There is **no Microsoft Copilot rail** today. This file inventories every Microsoft Copilot **hand** COSMOS could fire.

**Filter:** a surface with no hands is rejected. Every row is an **action** COSMOS could fire: REST endpoint, SDK call, MCP tool, Direct Line activity, Power Automate connector action, or DOM fallback. Marketing chrome without a dispatchable call is out.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks. Equal power, cheaper wins. Metered Azure OpenAI / Copilot Credits sit **below** the included Graph Search + Copilot Chat (web) cluster even when the model is stronger. The $30/user Microsoft 365 Copilot add-on is a **wallet**, not a hand.

**Name collision (do not mix wallets):**

| Name in the wild | What it actually is | Wallet |
|------------------|---------------------|--------|
| **Microsoft Copilot Chat** (web) | Web-grounded chat at `m365.cloud.microsoft/chat` / `m365copilot.com`. Included with eligible M365. | **$0 extra** (M365 seat) |
| **Microsoft 365 Copilot** (add-on) | Work-grounded Copilot in Graph + Word/Excel/Teams. Required for Chat API, Copilot Search API, OneDrive Retrieval, interaction export. | **$30/user/mo yearly** ($31.50 monthly) |
| **Copilot Studio** | Custom agents / tools / Direct Line. Credits, not the M365 Copilot seat. | Copilot Credits ($0.01 PAYG or $200/25k pack) |
| **Work IQ** | Workplace intelligence A2A + MCP + REST. **Independent of M365 Copilot licensing.** | Copilot Credits (usage-based) |
| **Azure OpenAI in Microsoft Foundry** | Raw model endpoints (`*.openai.azure.com`, `*.services.ai.azure.com`). Not Copilot. | Azure Cloud Billing (token meters) |
| **GitHub Copilot** | Separate product (see `GITHUB_HANDS.md`). Not this file. | GitHub Copilot credits |

---

## How COSMOS reaches Microsoft Copilot (reach column, one pattern)

Core stays sole ledger writer. Microsoft is reached as:

| Lane | Mechanism | When |
|------|-----------|------|
| **A. HTTP Microsoft Graph** | `https://graph.microsoft.com/v1.0/copilot/…` and `/beta/copilot/…` (Retrieval, Chat, Search, reports, interaction export). Same MSAL token as other Graph. | Preferred for RAG + work chat. Spend-gate as a new rail only after Keith mints an Entra app. |
| **B. HTTP Work IQ** | A2A JSON-RPC `https://workiq.svc.cloud.microsoft/a2a/` **or** Work IQ remote MCP. Scope `WorkIQAgent.Ask`. | Highest-power M365-grounded agent without a Copilot add-on. Usage-billed. |
| **C. HTTP Azure OpenAI / Foundry** | `https://{resource}.openai.azure.com/openai/v1/` (preferred v1, no `api-version`) **or** `{resource}.services.ai.azure.com/openai/v1/`. Chat completions, Responses, embeddings, batch, files. | Raw models (GPT-5.x, DeepSeek, Grok on Foundry). Sibling of `oa-api` but Azure-billed, Azure-resident. |
| **D. Direct Line (Copilot Studio)** | Bot Framework `https://directline.botframework.com/v3/directline/…` **or** Power Platform token endpoint. | Talk to a published Studio agent as a bot. |
| **E. Power Platform connector** | Copilot Studio connector `Execute Agent` / `Execute Agent and wait`; HTTP / HTTP-with-Entra; custom OpenAPI connectors. Trigger via Power Automate REST or a Keith-owned flow. | When Keith already has a flow; COSMOS should not become a Power Automate tenant. |
| **F. MCP-client** | Work IQ MCP (10 generic M365 tools); Copilot Studio MCP tool; federated Copilot connectors (MCP, no index). | Agent brains. Core prefers native Graph over giving itself a shell via MCP. |
| **G. DOM** | [m365.cloud.microsoft/chat](https://m365.cloud.microsoft/chat) (pinned Copilot Chat), [m365copilot.com](https://m365copilot.com), Copilot Studio maker portal, Azure portal / [ai.azure.com](https://ai.azure.com), Entra app registration, first OAuth. | **Canon: DOM first** when the API depends on something that can run out (Copilot Credits, Azure balance, seat, consent). Web-grounded chat is also the **free high-power** surface when Graph Copilot APIs are license-blocked. |

Keith owns credentials. Store under `live/config/` (git-ignored). Never hard-code. Never print a secret in full. Fenced commit still gates any tree write.

---

## Auth primer (all API rows inherit this unless overridden)

Base Graph: `https://graph.microsoft.com`. Header `Authorization: Bearer {token}`. Copilot APIs live under `/v1.0/copilot` and `/beta/copilot`.

| method | credential | header / env | COSMOS use |
|--------|------------|--------------|------------|
| **Entra delegated (user)** | MSAL / device code / `az login` for Keith's work account | `Authorization: Bearer` | **Required** for Retrieval, Copilot Chat API, Copilot Search API. Application permissions **not supported** on those three. Work/school only — personal MSA rejected. |
| **Entra application (daemon)** | App registration + client secret or cert; admin consent | `Authorization: Bearer` (client credentials) | Copilot **connectors indexing** (`external/connections`, `externalItem`). Interaction export (`AiEnterpriseInteraction.Read.All`). Not for Retrieval/Chat/Search. |
| **Work IQ** | Entra delegated, audience `api://workiq.svc.cloud.microsoft`, scope `WorkIQAgent.Ask` | `Authorization: Bearer` + `A2A-Version: 1.0` | A2A gateway and MCP. OBO when Foundry agents call Work IQ. |
| **Azure OpenAI API key** | Key on the Foundry / Azure OpenAI resource | `api-key:` **or** `Authorization: Bearer {key}` on `/openai/v1/` | Fast to stand up. Full resource access. Rotate. Prefer Entra in production. |
| **Azure OpenAI Entra (keyless)** | User / SP / managed identity with **Cognitive Services OpenAI User** | `Authorization: Bearer`; token scope **`https://ai.azure.com/.default`** on v1 | Production Foundry. Custom subdomain required (regional `*.api.cognitive.microsoft.com` does **not** do Entra). |
| **Copilot Studio Direct Line secret** | Web channel secret from Studio → token | `Authorization: Bearer {secret}` then conversation token | `POST https://directline.botframework.com/v3/directline/tokens/generate`. Never put the secret in a browser. |
| **Power Platform OAuth** | Entra login to Power Platform API | connector connection (not shareable) | Copilot Studio connector, HTTP-with-Entra. |
| **Graph delegated scopes (least privilege)** | Retrieval/Search: `Files.Read.All` + `Sites.Read.All`; connectors retrieval: `ExternalItem.Read.All` | — | Chat API needs the **full documented permission set** (all of them, not one). |

**Copilot APIs vs Graph CRUD (official):** Graph CRUD is data access under the M365 seat. Copilot APIs are AI over that data and generally need the **Microsoft 365 Copilot add-on** (Retrieval has a PAYG exception). Do not call Copilot endpoints expecting Graph-search prices.

---

## Cost floor (four wallets — do not conflate)

Mixing the M365 Copilot seat with Copilot Credits and Azure tokens is how a spend-gate gets burned by accident.

| Wallet | What official docs say | COSMOS note |
|--------|------------------------|-------------|
| **Eligible Microsoft 365 seat** | Copilot Chat (web-grounded) is **included, $0 extra**. Graph Search API, Graph CRUD, Copilot **connectors indexing** (up to **50 million items/tenant**, default **5 million/connection**) are included. | Highest-ranked Microsoft surface. Confirm Keith's plan is in the eligibility list (Business Basic/Standard/Premium, E3/E5, etc.). |
| **Microsoft 365 Copilot add-on** | **$30.00 user/month yearly** or **$31.50 monthly** ([microsoft.com/microsoft-365-copilot](https://www.microsoft.com/en-us/microsoft-365/copilot)). Work Graph grounding, in-app Copilot, Chat API, Copilot Search API, OneDrive Retrieval, interaction export, Researcher/Analyst agents. | One seat for Keith is enough to unlock most Copilot APIs **as that user**. Retrieval PAYG still requires **at least one** Copilot license in the tenant. |
| **Copilot Credits** | Common currency. **PAYG $0.01 / credit** (Azure). **Capacity pack $200 / tenant / month = 25,000 credits**. Studio rates (unlicensed users): classic answer 1, generative answer 2, agent action 5, tenant Graph grounding 10, agent-flow 13 / 100 actions. **M365 Copilot–licensed users: those Studio rates are $0** in M365 Chat/Teams/SharePoint. Retrieval PAYG meter: **$0.10 / API call**. Work IQ: usage-based, **no Copilot license required**. | Spend-gate this as `copilot-credits`. Credits **do not roll over**. Exceeding prepaid capacity can **deny service**. |
| **Azure Cloud Billing (Foundry / Azure OpenAI)** | Token meters. New Azure accounts: **~$200 credit, 30 days**. No perpetual free inference. Batch = **50% off** Global Standard. GPT-5.6 Luna Global Standard (official Azure blog 2026-07-09): **$0.20 in / $0.02 cached / $1.20 out per 1M**. GPT-5.6 Terra $2/$12; Sol $5/$30 (promo $4/$20 from 2026-09-01 through at least 2026-11-30). Data Zone ~+10%. | Distinct from `oa-api` (OpenAI.com). Confirm remaining Azure credit before looping. Inference beta SDK **retires 2026-08-26** — use OpenAI v1. |

**Copilot Studio trial:** maker can build and test in the test panel; **cannot publish**. Test-panel prompts in topics/actions are free; agent-flow prompts still consume credits.

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it |
|---|------|------|----------------------|------|------|-------|------------------------|
| 1 | **Microsoft Graph Search API** (`POST /search/query`) | Graph REST | Hybrid search over mail, calendar, files, sites, lists, Teams messages, people, bookmarks, **and Copilot-connector `externalItem`**. KQL, aggregations, collapse, spelling correction. Results permission-trimmed to the signed-in user. This is the **free** search hand; Copilot Retrieval is the AI-chunk cousin. | Entra **delegated**. Scopes per entity (`Mail.Read`, `Files.Read.All`, `Sites.Read.All`, `Calendars.Read`, `Chat.Read`, …). Application **not** for this query path. | **free** (M365 seat + Graph rate limits) | **highest** | HTTP spend-gate `POST https://graph.microsoft.com/v1.0/search/query` `{requests:[{entityTypes:["driveItem"], query:{queryString:"…"}}]}`. One request at a time. Default page 25, max 1000 (mail/event max 25). |
| 2 | **Copilot Chat DOM** (`m365.cloud.microsoft/chat`) | DOM | Web-grounded Copilot Chat with latest models, file upload, Pages, image gen (standard/capacity-gated), agents. Pinned users land here from `m365copilot.com`. Work Graph grounding **only** with the $30 add-on **or** a PAYG agent. Side pane in Edge / Teams / Outlook. Model picker: Auto / Quick / Think deeper. | Keith's Entra work session in a contained DOM profile. | **free** (eligible M365). Agents + work-grounded agents = Copilot Credits. Priority GPT-5 / upload = add-on. | **highest** (free LLM + files) | Existing `cosmos_browser` / Playwright MCP against `https://m365.cloud.microsoft/chat`. Canon: **this is the DOM-first Copilot hand** when Chat API is license-blocked. Typed failures: `AUTH_REQUIRED`, `SESSION_EXPIRED`. Do not scrape; drive the composer and capture the reply as the artifact. |
| 3 | **Graph CRUD (mail, calendar, files, Teams)** | Graph REST | Create/read/update mail (`/me/messages`, sendMail), calendar, OneDrive/SharePoint files, Teams chats. Copilot APIs **reason**; these **act**. Chat API explicitly **cannot** send mail or create files. | Entra delegated (`Mail.Send`, `Calendars.ReadWrite`, `Files.ReadWrite`, …) or application with admin consent. | **free** (Graph) | **highest** (action rail) | HTTP. Pair with Search (row 1) or Retrieval (row 8): search/ground → act here. Fenced commit still owns the COSMOS tree; Graph writes are tenant writes, ledger them as EGRESS. |
| 4 | **Copilot connectors API — ingest** (`/external/connections`) | Graph REST | Index **external** LOB data into Microsoft Graph so Search, Copilot, and Retrieval can see it. Four steps: Entra app → `POST /external/connections` → register **schema** (long-running) → `PUT …/items/{id}` with ACL. Synced model. 128 schema properties. Item body **30 MB**. 25 concurrent ops/connection. | **Application** permissions only (no signed-in user). Admin consent. | **free** index quota: **50M items/tenant** included on eligible M365; default **5M/connection**. Microsoft-built connectors free. Over-quota = account team. | **highest** (makes other Copilot hands see COSMOS/BTS content) | Daemon worker. `PUT https://graph.microsoft.com/v1.0/external/connections/{id}/items/{itemId}`. Probe remaining quota via `connectionQuota`. Do **not** dump the COSMOS ledger into Graph — only published, ACL'd artifacts. Samples: GitHub issues connector (Python/.NET/TS). |
| 5 | **Copilot connectors — federated MCP** | MCP | Query-time fetch **without** indexing. Citations point at the MCP server. For regulated / live data that must not leave the source. | MCP OAuth 2.0 or server-specific. | **free** protocol; backend cost is yours | **high** | COSMOS can **be** the MCP server (expose Core tools) **or** consume a federated connector. Register via M365 admin / agentConnectors in the app manifest. |
| 6 | **Work IQ A2A** | A2A JSON-RPC | Send a natural-language task to Microsoft Copilot / tenant agents; get a synthesized, permission-trimmed answer over mail, meetings, files, chats. Multi-turn via `contextId`. Agent cards at `/.well-known/agent-card.json`. **Does not require an M365 Copilot add-on.** | Entra delegated. Audience `api://workiq.svc.cloud.microsoft`. Scope `WorkIQAgent.Ask`. Header `A2A-Version: 1.0`. | **usage-based Copilot Credits** (independent of Copilot seat). Licensed Copilot users still billed for **custom/third-party** agents. | **highest** (Copilot-quality answers, no $30 seat) | `POST https://workiq.svc.cloud.microsoft/a2a/` JSON-RPC `SendMessage`. Location metadata required for time queries. Also wireable from Foundry agents as remote A2A. Word/Excel/PPT in-app agents are **useless headless** — skip those agent-ids. |
| 7 | **Work IQ MCP** | MCP | **10 generic tools** (fetch / create / update verbs + resource paths) over mail, calendar, files, people, chat, sites. Runtime schema discovery. Rego policy on every call. Collapses hundreds of Graph operations. | Same Work IQ Entra; Copilot Studio can attach the MCP server as a tool. | Copilot Credits (usage) | **highest** | MCP-client to the Work IQ remote server (Studio catalog: search "mail" / Work IQ). Prefer this over giving an agent raw Graph. Every invocation is logged — good ledger cousin. |
| 8 | **Copilot Retrieval API** | Graph Copilot REST | RAG without a second index: natural-language query → relevant **text extracts** from SharePoint, OneDrive, or Copilot connectors (`dataSource`: `sharePoint` / `oneDriveBusiness` / `externalItem`). KQL `filterExpression`. Max 25 hits. 1,500-char query. **200 req/user/hour**. Hybrid/semantic only for `.doc/.docx/.pptx/.pdf/.aspx/.one`; other types lexical. Files >512 MB (Office/PDF) or >150 MB (other) skipped. Sensitivity labels returned. Batch up to 20 via `$batch`. | Entra **delegated** only. `Files.Read.All` + `Sites.Read.All`; connectors also `ExternalItem.Read.All`. | **included** with M365 Copilot add-on. **PAYG preview** for unlicensed: SharePoint + connectors only (**not OneDrive**), **$0.10 / API call**, and the tenant must already have **≥1 Copilot license**. | **highest** (ground COSMOS brains on Keith's M365) | `POST https://graph.microsoft.com/v1.0/copilot/retrieval` (also `/beta`). Feed extracts to Grok/Claude — do not re-index. Interactive demo: `https://aka.ms/copilot.dev`. |
| 9 | **Copilot Chat API** (preview) | Graph Copilot REST | Multi-turn **Microsoft 365 Copilot** in COSMOS: create conversation → sync `…/chat` or SSE `…/chatOverStream`. Enterprise + web grounding (web off is **per-turn**). Attach SharePoint/OneDrive files as context. **Text only — no actions, no code interpreter, no image gen, no long-running tasks.** | Entra delegated; **all** documented Graph permissions required (not a subset). | **included with M365 Copilot add-on only.** No PAYG. Unlicensed = unavailable. | **high** (full Copilot stack, license-gated) | `POST /beta/copilot/conversations` `{}` → id; then `POST /beta/copilot/conversations/{id}/chat` `{message:{text:"…"}, locationHint:{timeZone:"America/Chicago"}}`. Streamed SSE not in Graph Explorer. |
| 10 | **Copilot Search API** (preview) | Graph Copilot REST | Hybrid semantic+lexical search over **OneDrive for work/school only**. Natural language. Page size 1–100. Path `filterExpression` only (for now). | Delegated `Files.Read.All` + `Sites.Read.All`. | **included with Copilot add-on.** No unlicensed path. | **med-high** | `POST /beta/copilot/search` `{query:"…"}`. Prefer Graph Search (row 1) unless you need Copilot-grade OneDrive ranking. |
| 11 | **Azure OpenAI v1 — Responses + Chat Completions** | Azure REST / SDK | Raw frontier models on **Keith's Azure**: GPT-5.x family, DeepSeek, Llama, Grok (Foundry catalog). `POST …/openai/v1/responses` or `/chat/completions`. Deployment name in `model`. No `api-version` on v1. Same OpenAI SDK as `oa-api` with a different `base_url`. | API key **or** Entra `https://ai.azure.com/.default`. Role: Cognitive Services OpenAI User. | **metered Azure**. New-account **~$200 / 30 days**. Luna $0.20/$1.20 per 1M (cheapest current frontier on Azure). Batch 50% off. | **high** (model rail, Azure-resident) | `POST https://{resource}.openai.azure.com/openai/v1/chat/completions` (also `*.services.ai.azure.com/openai/v1/`). Spend-gate as `az-oa` distinct from `oa-api`. SDK: `openai` + `azure-identity`. **Do not** use the retiring Azure AI Inference `/models` SDK after **2026-08-26**. |
| 12 | **Azure OpenAI embeddings + files + vector stores + batch** | Azure REST | `POST /openai/v1/embeddings`, `/files`, `/vector_stores`, `/batches`. Assistants/threads still on the Azure OpenAI surface. Batch JSONL, 24h, 50% off. | same as row 11 | metered; embeddings cheap vs chat | **high** (RAG store on Azure if Retrieval is license-blocked) | Same v1 base URL. Prefer Copilot Retrieval when the Copilot seat exists — it already indexed SharePoint. |
| 13 | **Foundry project endpoint + model catalog** | Azure REST | Project API `https://{resource}.services.ai.azure.com/api/projects/{project}`. One resource, many deployments (GPT, Grok, DeepSeek, Llama). Switch models without code. Portal: [ai.azure.com](https://ai.azure.com). | Entra or key | Foundry portal **free**; inference metered | **high** | Use for deployment CRUD + listing models. Inference still goes through row 11. |
| 14 | **Foundry ↔ Work IQ tool** | Foundry + A2A | Foundry agent emits `work_iq_preview`; Foundry OBO-forwards to Work IQ A2A. Ground an Azure-hosted agent in M365 without copying data. | Entra OBO; scopes `WorkIQAgent.Ask` + `offline_access` | Azure tokens + Work IQ credits | **high** | Only if Keith stands up a Foundry agent. Connection target `https://workiq.svc.cloud.microsoft/a2a/`. |
| 15 | **Copilot Studio custom agent + tools** | Studio | Standalone agent: generative orchestration, topics, knowledge (SharePoint, Dataverse, Graph connectors, uploaded files, public sites). Tools: prebuilt/custom **Power Platform connectors**, **REST API** (OpenAPI v2; v3 auto-downgraded), **MCP**, **agent flows**, **prompts**, **computer use** (GUI drive), HTTP Request node, Azure Bot skills, client tools. Max **128 tools**; docs recommend **25–30**. | Maker: Copilot Studio user license (free **after** tenant credit pack) **or** M365 Copilot **or** trial **or** Copilot Studio authors role. Runtime: end-user or maker credentials per tool. | Maker license free; **runtime = Copilot Credits** unless the user has M365 Copilot (zero-rated on M365 surfaces). Trial cannot publish. | **high** (custom M365 agent COSMOS can call) | Keith authors in Studio (DOM). COSMOS **calls** the published agent via Direct Line (row 16) or the Power Automate connector (row 17). Point a REST/MCP tool **at Core's versioned API** (fenced) so the agent can submit jobs. |
| 16 | **Direct Line v3 (published Studio agent)** | Bot REST + WS | Start a conversation, POST activities, receive replies over HTTP or WebSocket. Token from Studio **token endpoint** (GET) or `POST https://directline.botframework.com/v3/directline/tokens/generate` with the web-channel secret. Token TTL ~1800–3600s; refresh while unexpired. | Direct Line secret → conversation token. Never embed the secret in a DOM page. | Studio credits per turn (row 15) | **high** | Native worker: generate token → `POST …/conversations` → `POST …/conversations/{id}/activities` `{type:"message", text:"…"}`. Poll `/activities` or open the streamUrl. This is the **HTTP hand** for a Studio agent. |
| 17 | **Power Automate — Copilot Studio connector** | Connector | Actions: **Execute Agent** (fire-and-forget, returns `ConversationId`), **Execute Agent and wait** (`ExecuteCopilotAsyncV2` — lastResponse + responses[] + conversationId), plus eval/test-set actions. Standard harness agents only — **GitHub Copilot harness agents cannot be called this way**. Throttle: **300 calls / 60 s / connection**. | Entra OAuth to Power Platform (connection not shareable). | Connector class **Standard**. Runtime still burns Studio credits. | **high** | Prefer Direct Line (row 16) from Core. Use this if Keith already has cloud flows. Code-apps path: `/proactivecopilot/executeAsyncV2`. Conversations URL shape: `https://{id}.environment.api.powerplatform.com/copilotstudio/dataverse-backed/authenticated/bots/{agentName}/conversations`. |
| 18 | **Power Platform connectors (prebuilt + custom)** | Connector | Thousands of actions/triggers (SharePoint, Outlook, Dataverse, Teams, HTTP, SQL, Salesforce, …). Standard vs **Premium**. Custom connector from OpenAPI / Postman. Same connectors are Studio **tools** and Automate **actions**. HTTP-with-Entra: `InvokeHttp` GET/POST/PATCH/PUT/DELETE; **100 calls / 60 s**. | Per-connector OAuth / key / Entra. | Standard included; **Premium** needs Power Automate Premium / Studio plan. HTTP-with-Entra is **Premium**. | **high** (action bus) | Do not make COSMOS a flow designer. If a Premium connector is the only way to a system, wrap it as a Studio tool and call the agent, **or** call the underlying API directly (cheaper, ledgerable). |
| 19 | **Power Automate HTTP + Dataverse Web API** | REST | Generic HTTP action; Dataverse Web API for Dataverse rows. Trigger a Keith-owned flow via HTTP trigger URL (secret). | SAS/trigger URL **or** Entra. | Premium for HTTP; Dataverse per Power Platform plan | **med-high** | Last-resort glue. Treat trigger URLs as secrets (`live/config/`). Prefer Graph/Direct Line. |
| 20 | **Studio REST API tool + HTTP Request node** | Studio | OpenAPI v2 upload → select methods as tools (auth none / OAuth2). HTTP Request node: GET/POST/PATCH/PUT/DELETE with headers/body (Power Fx). | As configured on the tool | credits (agent action 5) | **high** (COSMOS as the API behind a Studio agent) | Expose Core's versioned API with a tight allowlist. Maker-provided vs end-user auth — end-user so the agent cannot outrun Keith's identity. |
| 21 | **Studio MCP tool + A2A child agent** | Studio / A2A | Attach any MCP server as tools/resources. Connect to an external A2A agent (`Add an agent` → Agent2Agent, endpoint URL, auto-pull agent card). | MCP OAuth; A2A per peer | credits | **high** | COSMOS MCP server as a Studio tool = the agent can lease/submit. Inverse of Work IQ MCP. |
| 22 | **Studio computer use** | Studio tool | Drive a **GUI** (web + desktop): clicks, menus, typing. Copilot's DOM-shaped tool. | Maker/runtime as configured | credits (heavy) | **med-high** | Overlaps COSMOS DOM workers. Use only if the target has no API. Do not point it at the COSMOS live tree. |
| 23 | **Declarative agents + plugins (M365 Copilot)** | M365 app | Sideload/publish a declarative agent into Copilot Chat. Plugins: MCP **or** OpenAPI REST (create/update/delete, not just read). Dynamic MCP tool discovery. Agents Toolkit in VS/VS Code. `wiqd agent provision` writes Entra IDs. | Entra app in the package; user Copilot seat to **run** | agent runtime: included for Copilot-licensed; **metered** for Chat-only users | **high** | Package as an M365 app; Keith sideloads. COSMOS can be the plugin API. Not a Core-to-Copilot HTTP call — it is Copilot-to-COSMOS. |
| 24 | **Interaction Export API** | Graph Copilot REST | `GET /copilot/users/{id}/interactionHistory/getAllEnterpriseInteractions` — user prompt + Copilot response + resources across Word/Excel/Teams/BizChat/WebChat. `$filter=appClass eq '…'`. `$top` recommend 100. **Does not** include Copilot Studio agent chats. | **Application** `AiEnterpriseInteraction.Read.All` + admin consent. Copilot license required. | included with Copilot add-on | **med** (audit / collector) | Daemon + admin consent. Feed the collector, not a brain. Delta not supported. |
| 25 | **AI interaction change notifications** | Graph subscriptions | Webhook on `/copilot/users/{id}/interactionHistory/getAllEnterpriseInteractions` or tenant-wide. `created,deleted,updated`. Resource-data encryption cert required. | App permissions; HTTPS notificationUrl on Core (Tailscale/`cosmos up`) | included | **med-high** (push vs poll) | `POST /v1.0/subscriptions`. Verify `clientState`; ledger `X-` delivery. Prefer this over polling row 24. |
| 26 | **Meeting Insights API** | Graph Copilot REST | AI notes, action items, topics for a Teams meeting: `GET /copilot/users/{id}/onlineMeetings/{meetingId}/aiInsights`. Companion: AI Insights change notifications. | delegated/app per docs; Copilot license | included with add-on | **med-high** | After a meeting id is known (Graph onlineMeetings). Pipe action items into COSMOS jobs. |
| 27 | **Copilot usage reports API** | Graph Copilot REST | `GET /copilot/reports/getMicrosoft365CopilotUsageUserDetail(period={period}, version={version})`. Licensed users only — unlicensed Chat usage is **not** here (Admin Center / Purview / Unified Audit / Management Activity API instead). | Reports permissions | included | **med** (spend/adoption projection) | Periodic collector job. Do not treat this as evidence of unlicensed Chat. |
| 28 | **Package management API** | Graph Copilot REST | Inventory / manage agents in the tenant. | admin Graph | included | **med** | Agent inventory for KDash — rebuildable projection. |
| 29 | **Copilot API client libraries** | SDK | Typed clients in the Microsoft 365 Agents SDK: `Microsoft.Agents.M365Copilot` (.NET NuGet), TypeScript, Python. v1.0 + Core packages. Preview-state possible after big drops. | same as Graph | **free** libraries; API cost as above | **med-high** (less foot-gun than raw REST) | Worker dependency. Prefer these over ad-hoc JSON for Retrieval/Chat. |
| 30 | **Azure CLI token helper** | CLI | `az login`; `az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv` (Foundry v1); `--resource https://graph.microsoft.com` for Graph. `az cognitiveservices account list` for resource names. | Keith's Azure/Entra | **free** tool | **infra** | Native worker mints short-lived tokens. Never log the token. |
| 31 | **Graph `$batch` for Retrieval/Search** | Graph REST | Up to **20** Retrieval (or Search) calls in one `POST /v1.0/$batch`. | same as child calls | 20× the child meter if PAYG | **med** | Use when fanning SharePoint + connectors (they cannot interleave in one Retrieval call). |
| 32 | **SharePoint tool in Microsoft Foundry** (Retrieval PAYG) | Foundry tool | Unlicensed users with Retrieval PAYG can ground Foundry agents on SharePoint via the same meter. | Foundry + Graph delegated | $0.10/call PAYG | **med** | Only if Foundry is already up and Copilot seats are scarce. |
| 33 | **Copilot in Edge / Teams / Outlook side pane** | DOM | Content-aware chat over the **open** document/mail/meeting without Graph. | same Entra session | **free** Chat; work features need add-on | **med** | DOM worker when the artifact is already on screen. Worse for headless Core than row 2. |
| 34 | **Microsoft 365 Copilot app (desktop/mobile)** | DOM / app | Deployed web + Win/Mac + iOS/Android. Same Chat surface. Auto-install with M365 Apps v2511+ (Current/MEC). | Entra | **free** Chat | **low** (redundant with row 2) | Do not automate the desktop app; drive the web URL. |
| 35 | **Purview / Unified Audit / Office 365 Management Activity API** | REST / PS | Unlicensed Copilot Chat usage is **not** in Graph reports. Official alternatives: Admin Center report, Purview Audit, `Search-UnifiedAuditLog`, Management Activity API. | admin | **free** (M365 compliance) | **med** (collector completeness) | Only if Keith wants Chat-usage telemetry without Copilot seats. |
| 36 | **Marketplace Product Ingestion API** (Copilot apps) | Graph partner | Publish M365 + Copilot offers (`type: microsoft365CopilotApp`). Seller-associated Entra tenant only. MCP helper for VS Code / GitHub Copilot. | Partner Center + seller Entra | partner | **low** (publish, not a COSMOS rail) | Skip unless Keith is listing an agent in Marketplace. |
| 37 | **DOM: Entra admin / Azure portal / Studio / ai.azure.com** | DOM | First app registration, admin consent, billing policy, credit-pack buy, Studio publish, Foundry deploy, PAYG enable (Copilot > Billing & usage > Pay-as-you-go > Retrieval API). | Keith | **free** UI | **high as fallback** | AUTH_REQUIRED / consent / credit-card. Keith does money. COSMOS does not click Buy. |

---

## What is **not** a COSMOS hand (rejected)

- GitHub Copilot CLI / cloud agent — see `GITHUB_HANDS.md`.
- Windows Copilot / Recall / consumer copilot.microsoft.com (personal MSA) — different identity, no Graph work data.
- Copilot Studio **GitHub Copilot harness** agents — cannot be called from the Power Automate Copilot Studio connector or Direct Line the same way.
- Chat API "do this in Word/Excel" — **text only**; use Graph CRUD or DOM in the app.
- Azure AI Inference beta SDK `/models` after **2026-08-26**.
- Fabricating a Copilot rail from `oa-api` — Azure OpenAI is a different wallet and ToS.

---

## Suggested COSMOS adoption order (cheap → expensive)

1. **Graph Search + Graph CRUD** (rows 1, 3) — $0, real M365 hands, no Copilot SKU.
2. **DOM Copilot Chat** (row 2) — $0 LLM for web-grounded work; matches DOM-first canon.
3. **Connectors ingest** (row 4) — $0 index (within 50M) if COSMOS/BTS knowledge should appear in Search/Copilot.
4. **Work IQ A2A/MCP** (rows 6–7) — no Copilot add-on; **credits**. Spend-gate before looping.
5. **Retrieval API** (row 8) — if Keith has (or buys one) Copilot seat: included. Else PAYG $0.10/call (SharePoint/connectors only) after enabling in admin center.
6. **Chat API** (row 9) — only with the $30 add-on.
7. **Azure OpenAI v1** (rows 11–13) — if Azure credit remains; never as a silent substitute for Graph-grounded Copilot.
8. **Studio agent + Direct Line** (rows 15–16) — when COSMOS needs a **custom** M365-facing agent with tools, not when Graph already does the job.

---

## Official sources (fetched 2026-08-25)

**Microsoft 365 Copilot APIs**

- [Copilot APIs overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/copilot-apis-overview)
- [Retrieval API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview)
- [Retrieve grounding data (`POST /copilot/retrieval`)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/copilotroot-retrieval)
- [Retrieval API pay-as-you-go (preview)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/paygo-retrieval)
- [Chat API overview (preview)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/overview)
- [Create conversation](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/copilotroot-post-conversations)
- [copilotConversation: chat](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/copilotconversation-chat)
- [Copilot Search API (`POST /copilot/search`)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/search/copilotroot-search)
- [Interaction export `getAllEnterpriseInteractions`](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/interaction-export/aiinteractionhistory-getallenterpriseinteractions)
- [AI interaction change notifications](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/change-notifications/aiinteraction-changenotifications)
- [Copilot usage user detail](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/admin-settings/reports/copilotreportroot-getmicrosoft365copilotusageuserdetail)
- [Teams export + Copilot interactions](https://learn.microsoft.com/en-us/microsoftteams/export-teams-content-copilot)

**Graph connectors + Search**

- [Copilot connectors overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-copilot-connector)
- [Connectors API (v1.0)](https://learn.microsoft.com/en-us/graph/api/resources/connectors-api-overview?view=graph-rest-1.0)
- [Connectors API limits](https://learn.microsoft.com/en-us/graph/connecting-external-content-api-limits)
- [Index quota / licensing](https://learn.microsoft.com/en-us/microsoftsearch/licensing)
- [Microsoft Search API](https://learn.microsoft.com/en-us/graph/api/resources/search-api-overview?view=graph-rest-1.0)
- [Plugins for M365 Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-plugins)

**Work IQ**

- [Work IQ overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/)
- [Work IQ API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/api-overview)
- [Work IQ A2A overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/a2a/overview)
- [Work IQ A2A quickstart](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/a2a/quickstart)
- [Work IQ MCP in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/use-work-iq)
- [Foundry agents + Work IQ](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/work-iq)

**Copilot Studio + Power Platform**

- [Add tools to custom agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent)
- [REST API tools](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api)
- [Power Platform connectors in Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors)
- [HTTP Request node](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-http-node)
- [A2A in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-agent-to-agent)
- [Standard harness licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing)
- [Copilot Credits billing rates](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management)
- [Call Studio agents from Power Automate](https://learn.microsoft.com/en-us/power-automate/call-copilot-studio-agent)
- [Microsoft Copilot Studio connector](https://learn.microsoft.com/en-us/connectors/microsoftcopilotstudio/)
- [Connectors catalog](https://learn.microsoft.com/en-us/connectors/)
- [HTTP with Microsoft Entra ID connector](https://learn.microsoft.com/en-us/connectors/webcontentsv2/)
- [Direct Line web security / tokens](https://learn.microsoft.com/en-us/microsoft-copilot-studio/configure-web-security)
- [Publish to mobile/custom apps (token endpoint)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-connect-bot-to-custom-application)
- [Direct Line performance testing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/conversational-agents-performance-testing-direct-line)
- [Copilot connectors vs Power Platform connectors](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-graph-vs-power-platform-connectors)

**Azure AI Foundry / Azure OpenAI**

- [Foundry model endpoints](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/endpoints)
- [Azure OpenAI v1 API lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle)
- [Azure OpenAI REST preview reference](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/reference-preview)
- [Quotas and limits](https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits)
- [GPT-5.6 in Foundry + published token prices](https://azure.microsoft.com/en-us/blog/gpt-5-6-now-available-in-microsoft-foundry/)
- [Azure OpenAI pricing page](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)

**Copilot Chat (DOM) + licensing**

- [Copilot Chat overview](https://learn.microsoft.com/en-us/copilot/overview)
- [Manage Copilot Chat / eligibility](https://learn.microsoft.com/en-us/copilot/manage)
- [Copilot Chat minimum requirements](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-chat-requirements)
- [License options](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-licensing)
- [Copilot Credits (M365 admin / Work IQ / Cowork)](https://learn.microsoft.com/en-us/microsoft-365/copilot/usage-based-billing-overview-copilot-credits)
- [Capacity packs vs PAYG](https://learn.microsoft.com/en-us/microsoft-365/copilot/pay-as-you-go/copilot-capacity-packs)
- [Public list price $30/user/mo](https://www.microsoft.com/en-us/microsoft-365/copilot)

**Interactive / ToS**

- Interactive Copilot API demo: `https://aka.ms/copilot.dev`
- [Copilot APIs Terms of Use (preview)](https://learn.microsoft.com/en-us/legal/m365-copilot-apis/terms-of-use)

---

## Host bind (additive, 2026-08-27 s6) — D6 / U7

This process: `claude mcp list` → `claude.ai Microsoft 365: https://microsoft365.mcp.claude.com/mcp` — **Needs authentication**. Seat eligibility + Copilot add-on: still **UNKNOWN** (U7, Keith). Graph Search remains the free hand **if** Entra exists; Copilot Chat API / Studio stay lease-or-skip ($30 or Credits). Not a stage-6 pass.
