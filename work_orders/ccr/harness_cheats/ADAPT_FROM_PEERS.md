# Adapt from peers — what the source actually does

Keith 2026-09-25. Read, not cloned. Depth is named. Nothing here is a license to copy a tree into COSMOS.

## What was read

| Peer | Source this pass |
|---|---|
| OpenCode | Golden excerpt of `session/prompt.ts` `while (true)` (2026-09-19, MIT). |
| Codex | Golden `apply_patch.lark` and `assess_patch_safety` (Apache-2.0). |
| OpenHands | Golden `Agent.step` (MIT, SDK). Product repo is `OpenHands/OpenHands`. |
| Pi | Golden `packages/coding-agent/src/core/tools/index.ts` (`earendil-works/pi`). |
| Hermes | Golden `run_conversation` entry (MIT). |
| Deep Agents | Golden `create_deep_agent` signature (MIT). |
| Aider | `aider/repomap.py` fetched this pass (Apache-2.0). Full file. |
| DeepSeek | `docs/architecture.md` fetched this pass (MIT). The loop description, not every package. |
| Cline, Kilo, Qwen, TrueForge, Oh-my-pi | README or prior architecture notes. Not a line read of their loops this pass. |

## Best piece, and the COSMOS shape

### Pi — small tool index, but it is no longer four

The index exports read, write, edit, bash, and also grep, find, ls, powershell, plus truncation helpers. The "four tools" story is the old default. The useful part is still the factory: each tool is a function of `cwd`, and extra tools are not required to boot.

**Adapt:** core offer is read, edit, write. Grep and find are a reveal. Bash stays dark (`policy_only`) until a sandbox is attached. Do not copy their missing jail.

### OpenCode — do not exit while a tool is owed

The loop is `while (true)`. The one rule worth taking: some providers return `stop` even when the assistant message still has tool calls. They keep going so the tool result can go back. They also log a warning and can exit on an orphaned interrupted tool.

**Adapt:** same rule, plus a hard cap. Their infinite loop is the scar (`query.ts` class). A step that still owes a tool result is not done. A step past the cap is `guard_held`, and the guard is not cleared.

### Codex — patch text is a grammar, safety is a separate function

`apply_patch.lark`: `*** Begin Patch` / Add / Delete / Update / Move / `*** End Patch`. `assess_patch_safety` returns AutoApprove, AskUser, or Reject. Empty patch rejects. Write outside the project rejects. Read-only sandbox rejects. Approval and sandbox are separate arguments.

**Adapt:** this is the edit wire, not a free-form `old`/`new` string, once we write edit. Delete hunks rewrite to archive. Never AutoApprove outside the attempt grant. Their "retry unsandboxed?" stays a hole we close (`refuse_unsandboxed_retry` already raises).

### OpenHands — one step does one thing

`step` executes pending confirmed actions and returns, before it samples a new model call. Unmatched actions are not mixed with a new sample. The conversation is an append-only event log. Docker workspace is how they keep the agent off the host tree.

**Adapt:** a turn is either "run the tool that was already allowed" or "ask the model." Not both. The attempt log is the source of what the model saw. PathJail is the isolation we have. A container is a later reveal, not the core.

### Hermes — every exit stamps the turn

`run_conversation` sends success, error, interrupt, retry-exhausted, and tool-limit through one export of `{turn_id, current_turn_user_idx}` after history rewrites. The prompt is meant to stay byte-stable. Compression is an explicit cache break.

**Adapt:** one exit function. Cap, pin-change, stop-refuse, and done all stamp the same record. Do not import the 70-tool registry. A skill enters only when named.

### Deep Agents — shell errors if there is no sandbox

Default tools include ls, read, write, edit, glob, grep, execute, and task. `execute` returns an error unless the backend implements a sandbox protocol. Subagents and skills are arguments, not a silent always-on.

**Adapt:** that error is our shell policy. Subagents stay dark. Do not take LangGraph. Their default stack is the token-tax warning.

### Aider — rank symbols, then fit a token budget

`RepoMap` parses defs and refs with tree-sitter, builds a graph, PageRank with personalization for chat files and mentioned names, then binary-searches how many tags fit `max_map_tokens` (default 1024). Important filenames are forced in. Long lines are cut at 100 characters. The tag cache is mtime. If the graph is too large it disables the map.

**Adapt:** the rank, not the walk. Seed is the work-order touch-set plus one hop of callers, not the repo. The map bytes go into `map_hash` with git HEAD. mtime-only cache is forbidden here. No auto-commit. `/undo` means revert in the attempt, not a live commit.

### DeepSeek — a profile is a list of plugins, and the log is the prompt

Cordis: every part is a plugin, including the loop, and a plugin unload unwinds its effects. Profiles (`web`, `headless`, `sdk`, `sdk-minimal`, `acp`) stack bundles. `sdk-minimal` does not apply the fat base. `tools/pre-execute` is a waterfall: a listener must call `next()` or the tool does not run. The session log is the source of model-visible context. A rejected first claim closes the turn with no step. Developer preview. Breaking changes expected.

**Adapt:** Ultralight / Cruiser / Flightdeck are profiles in this sense: a named list of what is mounted. Unmounting a layer removes it from the tool schema. Hooks run before exec and can deny. Do not adopt Cordis, `dsh web`, or their desktop host. Our core is not "no privileged core." Jail, stop, and the pen stay privileged.

### The ones read from docs, not loops

| Peer | Best idea | COSMOS use |
|---|---|---|
| Cline | Plan mode cannot edit. Act mode asks before write and shell. Skills load when needed. | Plan vs edit is a revealed mode. Opening the mode is not a summon. |
| Kilo | Same split, plus headless `--auto` for CI. | Bakeoff runner only. Not the default. |
| Qwen Code | Many protocols, one agent. Their own SWE-bench note uses `max_iterations=500`. | Adapter normalizes the vendor. 500 is the scar. Do not boot their Claude Code parity pack. |
| TrueForge | Sandbox is a tool, requested, not always wrapped. Session inspect shows tokens. | Shell reveal attaches a sandbox. Inspect is a log read, not a second UI in the prompt. |
| Oh-my-pi | A rule stays dark until a pattern fires, then it injects and retries from that point. A stale edit anchor refuses. | That is core-reveal for rules. Hash-anchored edit matches Codex. Do not take their 31 tools or in-process shell. Call `rg` if search is hot. |

## Write order, when Keith says write

1. Capped step loop. Owes a tool result → continue. Cap or failed guard → stop and do not clear the guard.
2. Edit through the Codex patch grammar, inside PathJail. Delete hunk → archive.
3. Repo map only inside the work-order closure, hashed. Dark until the WO names it.
4. Profiles mount layers. Ultralight mounts jail, stop, read, edit, write. Nothing else is in the tool schema.

Not in that write: Cordis, LangGraph, Docker, `dsh`, a TUI, cDeck mode code, a C helper.
