# 17-elsewhere-supermemory

Role: ELSEWHERE-SUPERMEMORY

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 325, 'out': 355, 'cached': 0}

Provisional. Pending research, review, and improvement.

### What the source says
The source describes a Claude Code plugin from `supermemoryai/claude-supermemory`. It uses hooks to search substantive prompts before Claude sees them and injects the retrieved matches. Its hosted MCP tools include `search_memory`. The lifecycle hooks run in the following order: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, and `Stop`. The tool requires an API key or browser login, operating as a hosted memory product rather than a local crystal file.

### What it does not say
The source does not specify the underlying storage schema, data retention policies, or transport protocols used by the hosted service. It does not state how "substantive prompts" are defined or filtered. It does not provide the performance latency of hook execution or MCP tool calls. Furthermore, it does not mention integration mechanisms with COSMOS, offline fallbacks, or local cache handling.

### One consequence for a provisional COSMOS Crystals note
Because Supermemory relies on a hosted external service requiring API keys or browser logins rather than local file persistence, it represents an external ephemeral projection or remote memory store rather than an inspectable, offline-first local crystal file. Any provisional crystal schema note must treat hosted memory products as third-party I/O integrations distinct from durable, rebuildable local artifacts.

### Open questions
- UNMEASURED (The packet does not specify how prompt injection formatting behaves during `UserPromptSubmit` or `PreToolUse`).
- UNMEASURED (The packet does not state what payload is emitted or captured at the `SessionStart` and `Stop` hooks).
- UNMEASURED (The packet does not detail how authentication tokens or API keys are provisioned within an automated pipeline).
