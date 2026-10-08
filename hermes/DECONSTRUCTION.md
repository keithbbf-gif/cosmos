# Hermes deconstructed for COSMOS

Repo: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent).
Docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/overview.
This is the learning-loop agent. It is not `rkchoudary/hermes` (action chain and
separation of duties), which already landed as `cosmos/cosmos_action_chain.py`.

Nothing here is applied to `V:\A\Ai\COSMOS`. Proposals live under `proposals/<slug>/`.

## Python surface

The running agent is a Python program. The pieces that matter:

| Hermes element | Role |
|---|---|
| `run_agent.py` | Tool-calling conversation loop (`AIAgent`) |
| `model_tools.py` | Tool definitions and toolset membership |
| `tools/` | One module per tool: terminal, files, delegate, approval, browser, memory, cron, session search, clarify, todo |
| `hermes_cli/` | CLI, setup, `hermes model`, gateway command, kanban dispatch, update |
| `gateway/` | One process for messaging platforms, delivery, status |
| `tui_gateway/` | Terminal UI backend |
| `plugins/` | Tools, hooks, memory providers (Honcho and others), context engines |
| Session DB | SQLite WAL + FTS5 recall across sessions |
| Skill loader | `SKILL.md`, agentskills.io, progressive disclosure |
| Terminal backends | local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox |
| MCP client | stdio or HTTP, tool filters, sampling |

`PYTHON_MAP.md` is the file-level index once the public tree listing is in.

## Already on the live tree

Do not install a second copy of these. The proposal is a review module that
names the live file as the seam.

| Live module | Hermes behavior it already owns |
|---|---|
| `cosmos/cosmos_approval.py` | Fail-closed action gate. No `off`. No `yolo`. Hardline never moves. |
| `cosmos/cosmos_delegate.py` | Child depth, concurrency, iteration budget the caller cannot raise. |
| `cosmos/cosmos_recall.py` | Cross-session recall as a projection of the ledger. |
| `cosmos/cosmos_skills.py` | Skills are proposed. Only CCr activates them. Hash check on load. |
| `cosmos/cosmos_nlcron.py` | Natural-language cadence parsed onto schtasks / WD2. No in-process cron. |
| `cosmos/cosmos_sandbox.py` | Attempt workspace and job object. Unconfigured cloud backends refuse. |
| `cosmos/cosmos_mcp_client.py` | Outbound MCP. Argv lists. No `shell=True`. |
| `cosmos/cosmos_cred_kit.py` | Key reads never return secret material. |
| `cosmos/cosmos_dom.py`, `cosmos/cosmos_browser.py` | DOM is the browser path. |
| `cosmos/cosmos_platform.py` | Argv, encoding, tree-kill. |
| `cosmos/cosmos_sched.py` | The scheduler. Hermes cron must not become a second one. |
| `cosmos/cosmos_spend.py` | The only spend authority. |

## Shape rules for every feature

1. Stable. Unknown input refuses with a stable code. Caps are policy. A caller who asks for a higher cap is ignored. One confirming retry only, and only for a named error class.
2. Fast. Pure functions, bounded scans, deterministic ordering. No unbounded tool loop. The agent loop cap is 8 turns, matching the COSMOS harness.
3. Secure. Empty allowlists enable nothing. Messaging platforms cannot enable a terminal. Secrets are ids. Raw key shapes are refused. Paths stay inside a grant. `run()` on code, computer-use, and home-assistant does not perform the action. Plugins are registered callables, not `importlib` from disk. Wake word is on-device or refused. API and dashboard bind loopback unless a public grant is passed in.

## Where each feature lands

| Slug | Hermes feature | Best COSMOS landing |
|---|---|---|
| `agent_loop` | `run_agent.py` loop | Harness FSM. Interrupt latches. Second identical tool error stops. |
| `tools_toolsets` | toolsets, per-platform enable | Allowlist minus denylist. Empty allow enables nothing. |
| `tool_search` | tool search | Deterministic rank over the in-memory registry. |
| `file_terminal` | read, patch, terminal, process | Jail plus argv list. Terminal returns `NEED_APPROVAL` and does not run. |
| `skills` | skills + learning loop | Propose and hash. `propose_from_task` never activates. Seam: `cosmos_skills.py`. |
| `memory` | `MEMORY.md` / `USER.md` | Bounded entries. A nudge returns text and does not write. |
| `memory_providers` | Honcho, Mem0, and the other backends | Satellites. Unconfigured is `UNCONFIGURED`. |
| `honcho` | dialectic user model | Evidence log. Contradictions are both kept. Not a SEED. |
| `session_search` | FTS5 session search | Pure-Python projection, owner scoped. Seam: `cosmos_recall.py`. |
| `context_files` | AGENTS.md, CLAUDE.md, SOUL.md, and kin | Fixed name list, size caps, caller-supplied text. |
| `context_references` | `@file` `@folder` `@diff` `@url` | Files from a supplied map. A URL is `NEED_FETCH`, not a socket. |
| `checkpoints` | snapshot and `/rollback` | Hash snapshot of an attempt. No git, no live tree. |
| `approval` | dangerous-command approval | Seam: `cosmos_approval.py`. Hardline stays hardline. |
| `cron` | natural language and cron expressions | Parse to a vehicle name. Seam: `cosmos_nlcron.py`. No thread. |
| `delegation` | `delegate_task` | Seam: `cosmos_delegate.py`. Parent sees the summary only. |
| `code_execution` | `execute_code` RPC | `ast` scan only. `run` refuses until a wipe-proof sandbox is injected. |
| `hooks` | lifecycle hooks | A refusing hook latches. A hook cannot widen the tool set. |
| `batch` | many prompts, trajectory capture | Sequential, cap 100, partial failure stays partial. No upload. |
| `voice_mode` | talk and barge-in | State machine. No device open. |
| `wake_word` | "Hey Hermes" | On-device flag required. Cooldown. |
| `tts` | ten providers | No provider selected means no audio request. |
| `browser` | Browserbase, CDP, Browser Use | A DOM job. `http(s)` only. Seam: `cosmos_dom.py`. |
| `vision` | image paste and analyze | Bytes or a granted path. No remote fetch. |
| `image_gen` | FAL and the model list | Allowlisted model ids. Missing price is `UNPRICED`. |
| `web_search` | search and extract | A DOM-rail request plus a capped ingest. |
| `document_extract` | documents | txt and md in-process. pdf, docx, and zip refuse to a named code. |
| `mcp` | MCP client | JSON-RPC builders and filters. Seam: `cosmos_mcp_client.py`. Sampling needs approval. |
| `provider_routing` | cost / speed / quality | Allowlist required. Denylist wins. |
| `fallback` | backup providers | One fallback. Only timeout, 429, and 5xx. |
| `credential_pools` | key rotation | Rotate ids. Never store a raw key. Do not change provider. |
| `credential_vault` | sealed secrets | Sealed bytes plus a purpose tag. Plaintext setter refuses. |
| `prompt_cache` | prefix cache | Frozen prefix. Dates and UUIDs in the prefix refuse. Never assume a hit. |
| `api_server` | OpenAI-compatible HTTP | Parser and bearer check. Loopback. No socket. |
| `acp` | editor integration | Display messages. A terminal message is `NEED_APPROVAL`. |
| `personality` | `SOUL.md` | Soul is first. Text that disables the gate is `GUARD_ESCAPE`. |
| `skins` | CLI theme | Strip ESC and bidi overrides. |
| `plugins` | plugin kinds | Manifest plus an injected callable. `importlib` from disk refuses. |
| `web_dashboard` | dashboard and widgets | Read panels are open. A mutation needs an approval nonce. |
| `kanban` | board | Hash-chained event projection. Not a second queue. |
| `kanban_lanes` | worker lanes | Lane cap. One crash report, then `REQUEUE_CAP`. No spawn. |
| `kanban_fleet` | several gateways | A fencing token. Two gateways cannot both mark a card running. |
| `goals` | goals | Named predicate id. The id is not code. |
| `heartbeat` | heartbeat | Interval floor 15s. A beat is liveness, separate from task success. |
| `curator` | memory curator | Deterministic select inside a byte budget. Drops secret-shaped lines. |
| `loops` | loops | Policy cap 8. |
| `mixture` | mixture of agents | 2 to 5 outputs. A tie is `TIE`. |
| `deliverable` | deliverable mode | Name, media type, sha256 against a supplied snapshot. |
| `lsp` | language server requests | JSON-RPC builders. URIs go through the jail. No spawn. |
| `computer_use` | mouse and keyboard | Every action is `CONFIRM`. `run` refuses. |
| `language_packs` | locales | Missing key returns the key and `MISSING`. |
| `pets` | cosmetic pet | Sprite and mood. A command or URL field refuses. |
| `spotify` | Spotify intents | Off until enabled. No token field. No HTTP. |
| `subscription_proxy` | subscription proxy | Strips Authorization from the log line. No second auth header. No socket. |
| `tool_gateway` | web, image, tts, browser | Each tool enables only with a credential id. |
| `codex_runtime` | Codex app-server | Argv builder. Judge requires read-only sandbox. Forbidden flags refuse. No spawn. |
| `bot_mode` | specialist bots | Mention routing. A bot cannot approve. |
| `gateway` | one gateway process | Idempotency key. Draining refuses new ingest. No watcher thread. |
| `platforms` | twenty messaging adapters | Disabled until a secret id is set. Parse and format only. |
| `terminal_backends` | seven backends | `execute` is `UNSANDBOXED`. SSH host is a hostname, not a shell. |
| `cli_tui` | slash commands, history, interrupt | Descriptors only. |
| `model_switch` | `hermes model` | Allowlist. Router and auto ids refuse unless explicitly enabled. |
| `clarify_todo` | clarify and todo | Questions are returned. A todo cannot execute. |
| `x_search` | X search | Off until a credential id is set. |
| `home_assistant` | Home Assistant | Service calls are `CONFIRM`. `run` refuses. |
| `setup_portal` | `hermes setup --portal` | A plan and a hash. Persisting a secret-shaped value refuses. |

## Python tree

`PYTHON_MAP.md` lists the public `main` tree: 18,248 entries, 8,041 Python files, tree `ac7927ca`.
Optional skill payloads (finance packs, research packs, and the security "godmode" skill) stay unloaded.
The skills proposal is the gate that would refuse a hardline skill. Those packs are not reimplemented.

Four path groups had no feature row and now have proposals: video generation, the threat-pattern classifier, observability counters, and the workspace guard (repo boundary plus secret spill).

## Checks

`py -3.14 check4.py` from this folder runs `py_compile`, `ruff`, `mypy`, and `pytest`.
A missing checker exits 127. Pytest exit 5 is `NO_TESTS` and blocks.
