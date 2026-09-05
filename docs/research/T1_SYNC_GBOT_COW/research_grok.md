# T1 sync Gbot<->COW - RESEARCH - grok

_32.9s, 4916 chars_

**UNKNOWN vs documented:** There is **no public, documented xAI API that addresses a specific persistent grok.com GrokBot / team** (GBt). The product “agent team” and the **API** are different surfaces. Treat “call *that* mailbox bot synchronously” as **unverified / likely unavailable** until xAI docs or grok.com network traffic prove otherwise.

Verify: [https://docs.x.ai](https://docs.x.ai) · [https://docs.x.ai/docs](https://docs.x.ai/docs) · OpenAPI/SDK repos under [https://github.com/xai-org](https://github.com/xai-org) · grok.com DevTools (whether the UI hits an authenticated “team run” HTTP API). If those have no team-id RPC, it does not exist for third parties.

---

### 1) Agents / Teams / Assistants API (persistent GBt)

**Finding: UNKNOWN as a public product; almost certainly no.**

What *is* documented (chat, not teams):

- Base: `https://api.x.ai/v1`
- Auth: `Authorization: Bearer <XAI_API_KEY>`
- Primary: `POST /v1/chat/completions` (OpenAI-compatible: `model`, `messages`, `stream`, tools/function-calling depending on model)
- Also commonly: models list, image gen (check current docs)
- **Not documented:** Assistants-style threads, “team_id”, “agent_id”, “GrokBot QA” handle, grok.com session continuity

**Request/response shape (API, not GBt):** standard chat completion JSON in → JSON (or SSE) out. **Limits:** rate/token limits on the key (see dashboard/docs; do not guess numbers).

**Precedent:** OpenAI Assistants / Responses with stored threads is the *pattern*; xAI’s public surface is **stateless (or client-managed) chat**, not grok.com persistence.

If you need the *same* GBt identity, the path that exists today is still the **file mailbox** (or another out-of-band channel you own).

---

### 2) Wrap GrokBot as MCP so COW calls it as a native tool

**MCP can wrap any sync function you can implement.** It **cannot** magically talk to grok.com unless you have a backend.

**MCP surface (smallest):**

- Server: stdio or HTTP MCP (what Claude Code/Cowork already speaks)
- Tool e.g. `grokbot_ask`:
  - input: `{ "task": string, "context_uris"?: string[], "timeout_ms"?: number, "schema"?: object }`
  - output: structured JSON matching that schema (or `{ "status", "answer", "artifacts" }`)
- Optional: `grokbot_health`

**Bot side needs one of:**

| Bridge | Sync? | Talks to *GBt*? |
|--------|--------|------------------|
| xAI chat completions inside MCP | Yes | No — new model session |
| MCP → HTTP you host → grok.com (undocumented) | UNKNOWN / fragile | Only if private UI API exists |
| MCP → wait on `QA_ENGINEER_TO_COW.md` | Blocking *for COW*, still async bot | Yes |
| Reverse: GBt long-polls your webhook | Near-sync | Yes if bot can HTTP |

**Precedent:** MCP servers that wrap Slack/Linear/HTTP; “agent as tool” = thin RPC, not a special xAI MCP.

**Bot side for true GBt:** the team must **poll or receive** the task (HTTP, websocket, or files) and **write a structured reply**. grok.com GBt cannot be assumed to host MCP.

---

### 3) CLI (official grok / x.ai / “Grok Build”)

**UNKNOWN / do not treat as GBt RPC.**

- **xAI:** API + SDKs; a first-party `grok` CLI that **targets a named grok.com team** is **not** something to rely on without checking:
  - [https://docs.x.ai](https://docs.x.ai)
  - npm/pypi/`xai` GitHub
- **Grok Build Fast / Cursor-style CLIs:** if present, they are typically **model/API** or **repo coding agents**, not “invoke GrokBot QA on grok.com and block.”
- **Claude Code/Cowork:** already the COW side; it does not give you xAI team addressing.

**Verify:** `npm search`, `pip index`, xAI changelog, and whether any CLI takes `team_id` / grok.com cookies (cookie-based = unofficial, brittle, ToS risk).

---

### 4) Recommendation — best surface + smallest slice

**Best integration if the goal is “COW blocks for structured reply”:**  
**MCP tool on Windows that calls `POST https://api.x.ai/v1/chat/completions`** (same Grok *model family*, **not** the grok.com team). Auth: env `XAI_API_KEY`. Request: chat messages + JSON schema / tool forcing. Response: parse `choices[0].message`. That is the only **documented synchronous** path.

**If the goal is literally GBt identity:** there is **no documented native tool**. Smallest buildable slice:

1. Keep mailbox files **or** replace with a **local HTTP** `POST /task` + `GET /task/{id}` (or one blocking `POST /task` that waits on a file/event).
2. Expose that HTTP as **one MCP tool** `grokbot_ask` so COW “looks native.”
3. GBt keeps writing the reply file (or POSTs to localhost/ngrok). COW blocks in the MCP server until timeout.

That is **sync at the orchestrator**, still **async at grok.com**, which is the honest architecture until an Agents API appears.

**Do not guess** a teams endpoint. Re-check [https://docs.x.ai](https://docs.x.ai) and xai-org GitHub; if a Teams API ships, it will show `team`/`agent` resources and Bearer auth like the rest of the API.