# 09-anthropic-hooks

Role: ANTHROPIC-HOOKS

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 335, 'out': 353, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**
Hooks are user-defined commands, HTTP endpoints, MCP calls, prompts, or subagents triggered at lifecycle points. Cadences include `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `Stop`, `PreToolUse`, and `PostToolUse`. While a rule in `CLAUDE.md` is considered a request, a `PreToolUse` hook provides programmatic enforcement. Hooks run deterministically and do not depend on the model remembering instructions.

**What the source does not say**
The source does not specify the precise payload schemas, exit code conventions, timeout parameters, or execution latency overhead for any of the hook cadences. It does not provide the concrete implementation details for invoking HTTP endpoints, MCP calls, or subagents, nor does it specify how hooks integrate directly with COSMOS ledger writes or Spidercaster’s schema definitions.

**One consequence for a provisional COSMOS Crystals note**
Because a rule in a guide file is merely a request while a hook is deterministic enforcement, any durable crystal constraint (such as preventing unauthorized writes outside Spidercaster or intercepting tool calls) must be pinned to lifecycle enforcement points like `PreToolUse` rather than relying on context memory in `CLAUDE.md`.

**Open questions**
- What specific JSON payload or environment variables are passed to `PreToolUse` and `PostToolUse` hooks to evaluate tool parameters and outputs?
- Can `SessionStart` hooks reliably inject crystal checkpoints or bound notes into the session context prior to model evaluation?
- UNMEASURED: How hook failures (non-zero exits or timed-out HTTP/MCP calls) are surfaced to the runtime or recovered from during active execution.
