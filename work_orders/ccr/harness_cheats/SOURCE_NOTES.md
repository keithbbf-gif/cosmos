# Source notes — peers + Claude Code 2.1.88

Kept 2026-09-25. Background for COSMOS CODE. Not a license to copy.

Depth: line-read where named. README or September notes where named. No full clones.

## Claude Code 2.1.88 (local extract)

Path: `V:\Streams\cosmos_code\harness_examples\c_code_repo\c-code-source\2.1.88\source\src`

`query.ts` is 1729 lines. The loop is `while (true)` at line 307, closed at 1728.

Scars, read in the file:

- **Pin swap.** Lines 894–922. `FallbackTriggeredError` sets `currentModel = fallbackModel` and retries the same turn. A named pin must not change under the caller.
- **Guard cleared.** Line 1157 sets `hasAttemptedReactiveCompact: true` after a compact. Line 1333 sets it back to `false` on token-budget continuation. Line 1721 sets it `false` again on `next_turn`. That is the spiral: compact fails, the guard is wiped, compact runs again. Do not clear a failed guard.
- **Cap exists, late.** Lines 1704–1711 return `max_turns` only if `maxTurns` was passed. Default is uncapped `while (true)`.
- **Grep** is ripgrep (`GrepTool.ts` imports `ripGrep`). Not C++. Do not vendor their binary.
- **`hooks/`** is mostly React UI. Law is not that folder. `utils/bash/bashParser.ts` is a second parser. Do not parse bash to decide safety.
- **Tools** are a large set (Agent, Bash, PowerShell, FileEdit, EnterPlanMode, TeamCreate, ScheduleCron, …). That set is the fat pack. Do not boot it.

Steal as shape only: PreToolUse can deny or rewrite before exec. Stop can refuse a false done. Plan mode exists as a tool pair (`EnterPlanMode` / `ExitPlanMode`), which means plan is optional, not the law.

Do not port `query.ts`, `cli.js`, or `cli.js.map`.

## Pi — `packages/agent/src/agent-loop.ts` (fetched this pass)

`earendil-works/pi`. MIT. The loop is real source, not the README.

- Outer `while (true)` plus an inner tool loop. Follow-up messages can resume after the agent would stop.
- `beforeToolCall` can block. Unknown tool returns an error result, it does not throw the process down.
- A `length` stop fails every tool call in that message. Truncated arguments are not executed.
- Tool loadout changes are declared as a delta (`toolsAdded` / `toolsRemoved`), not by restuffing the whole catalog into the system prompt.
- `prepareNextTurn` may replace `config.model`. That is a pin-change hole. We refuse it.
- Still no in-process sandbox. Isolation is the operator's container.

The coding-agent tool index also exports grep, find, ls, and powershell. The "four tools" line is the product bet, not the current export list. Core offer stays read, edit, write.

## OpenCode — golden `session/prompt.ts`

`while (true)`. If the provider says stop but a tool call is still owed, the loop continues. Orphaned interrupted tools are logged and can exit. Steal the owed-tool rule. Do not steal the infinite loop.

## Codex — golden grammar + `assess_patch_safety`

Patch text is a grammar: Begin / Add / Delete / Update / Move / End. Safety returns AutoApprove, AskUser, or Reject. Empty patch rejects. Outside project rejects. Read-only rejects. Sandbox and approval are separate arguments. Delete becomes archive. Never AutoApprove outside the grant. Do not copy "retry unsandboxed."

## OpenHands — golden `Agent.step`

Pending confirmed actions run and the step returns before a new sample. One step, one job. Event log is append-only. Docker workspace is the isolation peer. We have PathJail now. Container is a later reveal.

## Hermes — golden `run_conversation`

Every exit path stamps `{turn_id, current_turn_user_idx}` after history rewrites. Prompt is meant to stay byte-stable. Compression is an explicit cache break. Do not import the 70-tool registry.

## Deep Agents — golden `create_deep_agent`

Default tools include execute and task. `execute` errors if the backend is not a sandbox. That error is our shell policy. Do not take LangGraph.

## Aider — `aider/repomap.py` (full file, this pass)

Tree-sitter defs and refs, PageRank, personalization for chat files and mentioned names, binary search to fit `max_map_tokens` (default 1024), lines cut at 100 characters. Tag cache is mtime. Too-large graph disables the map. Steal the rank inside the work-order closure. Hash it. No mtime pin. No auto-commit.

## DeepSeek — `docs/architecture.md` (this pass)

Everything is a plugin, including the loop. Profiles stack bundles. `sdk-minimal` does not load the fat base. `tools/pre-execute` must call `next()` or the tool does not run. The session log is what the model sees. A rejected first claim closes the turn with no step. Developer preview. Steal the profile-as-mount-list and the pre-execute gate. Do not adopt Cordis. Jail, stop, and the pen do not unload.

## TrueForge — README (this pass)

The product is the runtime: chat UI, HTTP API, embeddable UI. Sandbox is a tool, provisioned when needed. Skills load on demand. Local SQLite is not a production deploy. Their benchmark claim is same accuracy, lower cost, against Claude managed agents and deepagents. Steal sandbox-on-demand and session inspect as a log read. Do not stand up a second server beside cDeck.

## Cline, Kilo, Qwen, Oh-my-pi

Not a loop read this pass. Prior READMEs and September notes still hold:

- Cline: Plan cannot edit. Act asks before write. Checkpoints. Token cost climbs if left loose.
- Kilo: OpenCode-shaped CLI plus Cline-shaped IDE. Headless `--auto` is a bakeoff tool, not the default.
- Qwen Code: Gemini CLI descendant, retuned for Qwen. Claims Claude Code parity. Their SWE-bench note uses `max_iterations=500`. Adapter yes. That cap no.
- Oh-my-pi: Pi fork. Hash-anchored edit rejects a stale file. Rules stay dark until a pattern fires. 31 tools and an in-process shell are the fat pack. Call `rg` if search is hot. Do not vendor their natives.

## What none of them are

Archive-not-delete as a third knob. Hash-bound DONE. A failing oracle before the first edit. A pin that cannot move. A failed guard that cannot be cleared.
