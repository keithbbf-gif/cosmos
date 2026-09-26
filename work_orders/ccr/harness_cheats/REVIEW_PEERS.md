# Peer review — 2026-09-25

Not a clone. Not a bakeoff. Method is named per row.

## Official sources (Keith 2026-09-25)

| Name | Repo | Site |
|---|---|---|
| OpenCode | https://github.com/anomalyco/opencode | https://opencode.ai |
| Codex CLI | https://github.com/openai/codex | https://developers.openai.com/codex/cli |
| Kilo | https://github.com/Kilo-Org/kilocode | https://kilo.ai |
| Hermes | https://github.com/NousResearch/hermes-agent | https://hermes-agent.nousresearch.com |
| DeepSeek | https://github.com/deepseek-ai/deepseek-harness | https://deepseek.com/harness |
| Qwen | https://github.com/QwenLM/qwen-code | https://qwenlm.github.io/qwen-code-docs |
| TrueForge | https://github.com/truefoundry/trueforge | https://trueforge.dev |
| Oh-my-pi | https://github.com/can1357/oh-my-pi | https://omp.sh |
| Deep Agents | https://github.com/langchain-ai/deepagents | https://docs.langchain.com/deepagents |
| Aider | https://github.com/Aider-AI/aider | https://aider.chat |
| Cline | https://github.com/cline/cline | https://docs.cline.bot |
| Pi | https://github.com/earendil-works/pi | https://pi.dev |
| OpenHands | https://github.com/OpenHands/OpenHands | https://www.openhands.dev |

Pi moved from `badlogic/pi-mono` in May 2026. Use `earendil-works/pi`. Older golden excerpts may still cite the old path.

OpenHands product repo is `OpenHands/OpenHands` (was OpenDevin). The 2026-09-19 notes also read `OpenHands/software-agent-sdk` for the loop. SDK is not a second product.

Not these: Microsoft's old Codex-CLI experiment. `rkchoudary/hermes`. Community Deep Code CLIs. TrueCharts/TrueForge Helm charts.

Shape: OpenCode, Codex CLI, Qwen Code, Aider, Cline, and OpenHands are coding agents. Kilo is editor + CLI. Pi is the minimal coding harness. Oh-my-pi is a coding fork of Pi. DeepSeek Harness, TrueForge, Hermes, and Deep Agents are general runtimes. Deep Agents Code (`dcode`) is the terminal coder in that same repo family.

| Peer | Read this pass | What it is | Steal | Do not adopt |
|---|---|---|---|---|
| OpenCode | 2026-09-19 NOTES + golden loop excerpt. No new clone. | TS TUI. Plan/Build. `while (true)` prompt loop. Permissions in JSON. | Plan asks before edit/bash. Provider map. | The loop. OpenCode as Core. |
| Codex CLI | Same pack. Golden `apply_patch` grammar on disk. | Rust. Sandbox ⊥ approval. AGENTS.md does not grant rights. | Patch grammar + safety assess. Third knob stays ours: archive-only. Close their "retry unsandboxed?" hole. | `danger-full-access`. Codex as the name. |
| Kilo | Same pack. | OpenCode-shaped CLI. Code/Plan/Ask/Debug/Review. | Headless `--auto` for a later bakeoff. Mode split as UX. | VS Code product. Org cloud. |
| Hermes | Same pack. Golden registry excerpts. | Python. Chat→tools until budget. 70+ tools. Skills by frontmatter. | Thin registry. Byte-stable prompt. Skill loaded by name. | Gateway, cron, learning-loop OS. |
| OpenHands | Same pack. | Typed Action/Observation. Docker workspace. | Attempt that cannot see `live/`. Event log shape. | Canvas + agent server as Core. |
| Pi | Local architecture + 4-tool golden. README fetched. | Four tools: read, write, edit, bash. No in-process sandbox. Extensions add the rest. | This is the core shape. Reveal is an extension, not a default tool. | Their missing jail. Do not ship four tools and call it safe. |
| TrueForge | Local architecture. | HTTP + SSE. Sandbox is a tool, on demand. SQLite local. | Sandbox on demand. Session inspect (turns, tokens). | Hosted Postgres/Redis mesh as Core. |
| Deep Agents | Local architecture + golden `create_deep_agent`. | LangGraph middleware. VFS. Subagents. Skills disclosed late. | Offload big tool output to a file. Skills dark until named. | LangGraph as the loop. Their default scaffold is a token tax. |
| Aider | README fetched. Catalog already had the map. | Git-native. Repo map (tree-sitter, no vector DB). Architect/Editor. Auto-commit. Lint/test after edit. | Map of the touch-set, not the tree. `/undo` = revert. Plan model ≠ edit model. | Auto-commit on the live tree. |
| Cline | README fetched. | Plan vs Act. Human approval on edit and shell. Checkpoints. Skills when needed. | Plan/Act as a mode. Approval before mutation. | Teams, cron, Slack/Telegram inside CODE. |
| Qwen Code | README fetched. | Gemini CLI fork, now independent. Claims Claude Code parity. Agent Arena. `max_iterations=500` in their SWE-bench note. | Multi-protocol adapter, not a hardcoded prompt pack. | Their parity table as our spec. A 500-step loop. |
| Oh-my-pi | README fetched. | Pi fork. ~31 tools. Rust in-process search/shell. Rules sit dormant until a regex fires, then inject and retry. | Dormant-until-triggered is the public twin of core-reveal. Hash-anchored edit (stale anchor refuses). | 31 tools at boot. Vendored shell. Their product. |
| DeepSeek harness | README fetched (`deepseek-ai/deepseek-harness`, MIT, `dsh`). | Everything is a plugin (Cordis). Developer preview. Breaking changes expected. Web UI default. | A plugin is a reveal unit. Core does not import the catalog. | `dsh web` as the product. A preview kernel. |

## What none of them are

Archive-not-delete as a third knob beside sandbox and approval. Hash-bound DONE. A failing oracle before the first edit. Those stay ours.

## What this does to the write

Core matches Pi's four names, plus our jail, hooks, and stop. Plan/Act is Cline's mode, revealed. Repo map is Aider's, touch-set only, revealed. Patch grammar is Codex's, when we write edit. Dormant rules are Oh-my-pi's idea, without their tool pile. Deep Agents and Qwen Code are the warning: a fat default prompt loses on tokens even when the model is fine.
