# T1 sync Gbot<->COW - RESEARCH - openai

_58.8s, 14991 chars_

## Bottom line

**No documented xAI API currently exposes a persistent `grok.com` Grok Bot / Bot Team / “Grok Bot QA” as an addressable agent resource.** The public xAI API is a model-inference API. It can synchronously invoke a Grok model, but the published API surface does **not** document an endpoint such as:

```http
POST /v1/agents/{agent_id}/runs
POST /v1/teams/{team_id}/messages
POST /v1/assistants/{assistant_id}/threads
```

for a Grok.com-created persistent Bot or team.

Therefore:

* A supported synchronous replacement is feasible: **COW → local MCP tool → xAI Chat Completions/Responses API → structured result**.
* A supported synchronous call to the **existing** Grok.com persistent team is **UNKNOWN / not documented**.
* Do not treat “call Grok model with a prompt” as equivalent to “message the existing GrokBot team”: the latter may have private configuration, memory, files, tools, or UI-only state that the xAI API does not expose.

Primary xAI API documentation:  
- https://docs.x.ai/  
- https://docs.x.ai/docs/api-reference  
- https://docs.x.ai/docs/guides/chat-completions  
- https://docs.x.ai/docs/guides/responses  

---

# 1. xAI Agents / Teams / Assistants API for a specific persistent Grok Bot/team

## Finding: no documented public API for Grok.com Bot/team addressing

I do **not** find a published xAI API contract for addressing a Grok.com persistent Bot/team by ID, name, or handle.

The documented xAI API is centered on invoking models through endpoints such as:

```http
POST https://api.x.ai/v1/chat/completions
```

and, where enabled/account-supported:

```http
POST https://api.x.ai/v1/responses
```

Those calls accept model, messages/input, tool configuration, and generation controls. They do **not** document a `grok.com` Bot/team identifier field.

Relevant official documentation:

- Chat Completions: https://docs.x.ai/docs/guides/chat-completions
- Responses: https://docs.x.ai/docs/guides/responses
- API reference: https://docs.x.ai/docs/api-reference
- Authentication / getting started: https://docs.x.ai/docs/overview

## What is available: synchronous model invocation

Illustrative Chat Completions request:

```http
POST /v1/chat/completions HTTP/1.1
Host: api.x.ai
Authorization: Bearer $XAI_API_KEY
Content-Type: application/json
```

```json
{
  "model": "<xAI-model-enabled-for-this-account>",
  "temperature": 0,
  "messages": [
    {
      "role": "system",
      "content": "You are the QA Engineer. Return only valid JSON matching the requested schema."
    },
    {
      "role": "user",
      "content": "Review this task: ..."
    }
  ]
}
```

Typical Chat Completions response shape:

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 0,
  "model": "...",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"status\":\"ok\",\"summary\":\"...\",\"findings\":[]}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

COW can block on this HTTP request until the response arrives, subject to its own client timeout and xAI service limits.

## Authentication

Use an xAI API key:

```http
Authorization: Bearer $XAI_API_KEY
```

Create/manage API credentials in the xAI console; do not place the key in a prompt, checked-in config file, MCP tool arguments, or a Grok.com Bot definition.

- xAI API overview / setup: https://docs.x.ai/docs/overview
- xAI console: https://console.x.ai/

For a Windows local MCP bridge, store `XAI_API_KEY` in the service/user environment or a proper secret store, not in the MCP JSON configuration.

## Limits

Exact rate/token/concurrency limits are account- and model-dependent and can change. I will not invent numeric limits.

Verify the currently applicable limits in:

1. the xAI Console for the API project/key;
2. the model documentation for the selected model;
3. xAI rate-limit documentation, if present for the account/product.

The important architectural consequence is that the MCP bridge must handle:

* HTTP timeout;
* `429` / rate limiting;
* transient `5xx`;
* response-size/token limits;
* invalid JSON/model-schema failures;
* retries only where safe and idempotent.

## What this does **not** establish

A Chat Completions call does **not** demonstrate access to:

* the Bot named “Grok Bot QA” on grok.com;
* that Bot’s persistent state;
* its hidden system prompt;
* its attachments/knowledge;
* its internal team routing;
* its prior mailbox conversation;
* any Grok.com UI-specific tools.

Those would require a published API identity such as `bot_id`, `team_id`, or an OAuth/session-backed Bot API. **That API is UNKNOWN / not documented in the public xAI API reference.**

### How to verify definitively

Ask xAI support or check the API reference for all of the following, specifically:

```text
Grok.com Bot API
Grok Bot team API
persistent agent API
agent runs API
assistant/thread API
bot_id
team_id
custom bot API
Grok Build API
```

A real supported integration should provide all of:

1. an endpoint;
2. a durable bot/team identifier;
3. an auth model;
4. a request schema;
5. a response/run-status schema;
6. rate limits;
7. ownership/sharing semantics.

Without those, do not build against browser/session automation as though it were a supported API.

---

# 2. Can a GrokBot be wrapped as an MCP server/tool?

## Existing Grok.com Bot: not directly, on the documented API surface

An MCP server is a service **you implement**. It can expose a tool called `grok_qa_review`, but it still needs a supported way to reach the upstream service.

For the existing Grok.com persistent Bot/team, that upstream callable interface is **UNKNOWN**.

So this is not sufficient:

```text
COW ──MCP──> “GrokBot”
```

unless there is a real callable bot endpoint behind “GrokBot.”

## Supported practical version: an MCP wrapper around the xAI model API

Build:

```text
COW / Claude Code
      │
      │ MCP over local stdio
      ▼
local grok-qa-mcp server
      │
      │ HTTPS + xAI API key
      ▼
xAI Chat Completions or Responses API
      │
      ▼
Grok model configured as the QA delegate
```

This gives COW a native synchronous tool while using the supported xAI API.

Claude Code MCP documentation:  
https://docs.anthropic.com/en/docs/claude-code/mcp

MCP tool specification:  
https://modelcontextprotocol.io/specification/

## Suggested MCP surface

Expose one narrow tool first:

```text
grok_qa.review
```

### Tool input schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Stable caller-generated task identifier."
    },
    "task": {
      "type": "string",
      "description": "The QA question or review assignment."
    },
    "context": {
      "type": "string",
      "description": "Relevant code, requirements, logs, or prior decisions."
    },
    "acceptance_criteria": {
      "type": "array",
      "items": { "type": "string" }
    },
    "max_findings": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50,
      "default": 10
    }
  },
  "required": ["task_id", "task"]
}
```

### Tool result contract

Return stable application JSON, not prose:

```json
{
  "task_id": "QA-1042",
  "status": "ok",
  "summary": "Two material issues found.",
  "findings": [
    {
      "severity": "high",
      "title": "Race condition in retry state",
      "evidence": "src/retry.ts:41-63",
      "recommendation": "Protect state update with ..."
    }
  ],
  "questions": [],
  "assumptions": [],
  "raw_model_response_id": "chatcmpl-..."
}
```

Recommended status enum:

```text
ok
needs_input
blocked
error
```

At the MCP protocol layer, return either:

* successful tool output containing the JSON result; or
* an MCP tool error/result with `isError: true` for infrastructure failures.

## What the “bot side” needs

### If using the supported xAI model API

There is no Grok.com Bot-side component. The MCP server becomes the integration component and provides:

* a fixed QA system prompt;
* the expected response JSON schema;
* context packaging/truncation;
* API key handling;
* JSON validation;
* retry/error policy;
* audit logging and correlation IDs.

### If the requirement is truly “use that exact persistent Grok.com Bot/team”

The Bot side would need a documented externally callable bridge, for example:

```text
POST /bot-runs
{
  "bot_id": "grok-bot-qa",
  "input": {...}
}
```

or a webhook/action mechanism that can synchronously return a result.

No such public Grok.com Bot/team bridge is established by the published xAI API documentation cited above. Until xAI documents one, the alternatives are:

1. keep the mailbox design;
2. recreate the QA behavior in the xAI API-backed MCP service;
3. obtain a supported Bot/team API from xAI.

Browser automation against a grok.com account is not recommended as an integration surface: it is brittle, difficult to secure, may break on UI changes/challenges, and is not evidence of supported API access.

---

# 3. CLI paths

## Official xAI API path: curl or SDK, synchronous

The documented API can be called synchronously from any CLI environment using `curl`, PowerShell, Python, Node, etc.

Windows PowerShell example:

```powershell
$headers = @{
  Authorization = "Bearer $env:XAI_API_KEY"
  "Content-Type" = "application/json"
}

$body = @{
  model = "<enabled-xAI-model>"
  temperature = 0
  messages = @(
    @{
      role = "system"
      content = "You are a QA engineer. Return JSON only."
    },
    @{
      role = "user"
      content = "Review task QA-1042: ..."
    }
  )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
  -Method Post `
  -Uri "https://api.x.ai/v1/chat/completions" `
  -Headers $headers `
  -Body $body
```

That is synchronous in the normal HTTP sense: PowerShell blocks until completion/failure.

Official starting point:  
https://docs.x.ai/docs/overview

## “Official Grok CLI” / “Grok Build CLI”

**UNKNOWN as a supported path to invoke a specific persistent Grok.com Bot/team.**

Even if an official Grok-related CLI exists for coding or interactive use, it would need explicit documented support for all of the following to satisfy this target:

```text
--bot-id / --team-id
non-interactive invocation
machine-readable JSON output
API-key or OAuth authentication
documented service limits
stable automation contract
```

I cannot cite a publisher-authored CLI contract that establishes those capabilities for a Grok.com persistent Bot/team.

### Verification steps

Before adopting any CLI, verify from an xAI-published source:

```powershell
<cli> --help
<cli> auth --help
<cli> bots --help
<cli> teams --help
<cli> run --help
```

Look specifically for:

* a noninteractive command;
* a Bot/team selection mechanism;
* JSON output;
* API-key/OAuth documentation;
* a stated relationship to Grok.com custom Bots/teams.

If the CLI only prompts interactively or only invokes a model, it is not a reliable COW native-tool integration and does not solve persistent-Team targeting.

---

# 4. Recommendation

## Recommended integration surface

**Build a local stdio MCP server that exposes one synchronous QA tool and calls the supported xAI Chat Completions or Responses API.**

This is the smallest supported, automatable path:

```text
COW
  → MCP tool: grok_qa.review
  → local Windows MCP bridge
  → POST https://api.x.ai/v1/chat/completions
  → validated structured QA result
```

Use the Chat Completions endpoint first unless the selected xAI model/workflow specifically requires Responses API features.

## Why this is the best first slice

| Criterion | Local MCP → xAI model API | Existing Grok.com Bot/team |
|---|---:|---:|
| Synchronous request/response | Yes | UNKNOWN |
| Documented programmatic auth | Yes | UNKNOWN |
| Native COW/Claude-Code tool shape | Yes, via MCP | Only with an undocumented bridge |
| Structured machine-readable result | Yes, enforce in bridge | UNKNOWN |
| Uses exact persistent Grok.com team state | No | Desired, but no documented API |
| Safe production integration surface | Yes | No published basis |

## Smallest buildable slice

### 1. Implement one local MCP server

Example command registration concept:

```json
{
  "mcpServers": {
    "grok-qa": {
      "command": "node",
      "args": ["C:\\tools\\grok-qa-mcp\\dist\\server.js"],
      "env": {
        "XAI_API_KEY": "${XAI_API_KEY}"
      }
    }
  }
}
```

Use the exact COW/Claude Code MCP configuration mechanism supported by that installation; do not assume the above path or variable interpolation syntax is universal.

### 2. Add one tool only

```text
grok_qa.review(task_id, task, context?, acceptance_criteria?)
```

Do not start with multiple agent roles, async jobs, background queues, or tool-to-tool delegation.

### 3. Put the prior Bot’s QA role into a versioned prompt

For example:

```text
Role: QA Engineer.
Inputs: task, context, acceptance criteria.
Rules:
- Distinguish observed evidence from assumptions.
- Say UNKNOWN rather than inventing evidence.
- Return only JSON matching the schema.
- Produce actionable findings with severity and evidence.
```

Version that prompt in source control:

```text
prompts/qa-engineer.v1.md
```

This makes the behavior reproducible and reviewable, unlike a UI-only Bot configuration.

### 4. Enforce structured output in the bridge

Use xAI’s documented structured-output capability if supported by the chosen model. Otherwise:

1. instruct the model to emit JSON only;
2. parse JSON;
3. validate against a JSON Schema;
4. retry once with the validation error;
5. return `status: "error"` if still invalid.

Relevant xAI documentation should be checked for current structured-output model support:  
https://docs.x.ai/docs/api-reference

### 5. Set a bounded timeout and return a deterministic error

Example policy:

```text
COW tool timeout: 90 seconds
xAI request timeout: 75 seconds
one retry only for transport/429/5xx as appropriate
no automatic retry after an ambiguous completed request
```

Return:

```json
{
  "task_id": "QA-1042",
  "status": "error",
  "summary": "xAI request timed out before a validated result was received.",
  "findings": [],
  "questions": [],
  "assumptions": []
}
```

---

## Decision statement

If “GrokBot agent team” means the exact persistent Grok.com team named **Grok Bot QA**, the supported synchronous API path is currently:

```text
UNKNOWN — no documented xAI endpoint for targeting that persistent Bot/team.
```

If the operational goal is “get Grok QA reasoning synchronously into COW,” the best supported path is:

```text
COW native MCP tool → local bridge → xAI model API → validated JSON response.
```

That is the recommended first build. It replaces the file mailbox with a synchronous, auditable, structured call, while avoiding an unsupported claim that the existing Grok.com Bot/team can be remotely addressed.