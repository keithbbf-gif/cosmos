# Feature assignments

One folder per slug: `proposals/<slug>/`. The import name is the slug.
Contract: `CONTRACT.md`. Map: `DECONSTRUCTION.md`. Live tree is read-only.

| Slug | Doc | Live seam |
|---|---|---|
| agent_loop | overview, `run_agent.py` behavior | `cosmos_harness` loop |
| tools_toolsets | /features/tools | hand allowlists |
| tool_search | /features/tool-search | tool registry |
| file_terminal | /features/tools | `cosmos_platform.py` |
| skills | /features/skills | `cosmos_skills.py` |
| memory | /features/memory | artifact files |
| memory_providers | /features/memory-providers | projection |
| honcho | /features/honcho | projection, not SEED |
| session_search | recall / FTS5 behavior | `cosmos_recall.py` |
| context_files | /features/context-files | spawn context |
| context_references | /features/context-references | DOM fetch later |
| checkpoints | /checkpoints-and-rollback | attempt workspace |
| approval | approval gate | `cosmos_approval.py` |
| cron | /features/cron | `cosmos_nlcron.py` |
| delegation | /features/delegation | `cosmos_delegate.py` |
| code_execution | /features/code-execution | `cosmos_sandbox.py` |
| hooks | /features/hooks | harness hooks |
| batch | /features/batch-processing | attempt batch |
| voice_mode | /features/voice-mode | `cosmos_voice.py` |
| wake_word | /features/wake-word | on-device only |
| tts | /features/tts | voice rail |
| browser | /features/browser | `cosmos_dom.py` |
| vision | /features/vision | spend-gated request |
| image_gen | /features/image-generation | spend-gated request |
| web_search | /features/web-search | DOM / firecrawl rail |
| document_extract | /features/document-extraction | in-process txt/md |
| mcp | /features/mcp | `cosmos_mcp_client.py` |
| provider_routing | /features/provider-routing | rails |
| fallback | /features/fallback-providers | one backup |
| credential_pools | /features/credential-pools | `cosmos_cred_kit.py` |
| credential_vault | /features/credential-vault | sealed blobs |
| prompt_cache | prompt-caching | P11 prefix |
| api_server | /features/api-server | loopback handler |
| acp | /features/acp | editor messages |
| personality | /features/personality | SOUL first |
| skins | /features/skins | terminal-safe text |
| plugins | /features/plugins | injected callables |
| web_dashboard | /features/web-dashboard | projection panels |
| kanban | /features/kanban | chained projection |
| kanban_lanes | /features/kanban-worker-lanes | no spawn |
| kanban_fleet | /features/kanban-multi-gateway | fencing token |
| goals | /features/goals | named predicates |
| heartbeat | /features/heartbeat | liveness record |
| curator | /features/curator | deterministic select |
| loops | /features/loops | cap 8 |
| mixture | /features/mixture-of-agents | tie refuses |
| deliverable | /features/deliverable-mode | hash check |
| lsp | /features/lsp | JSON-RPC builders |
| computer_use | /features/computer-use | confirm, never run |
| language_packs | /features/language-packs | missing key is MISSING |
| pets | /features/pets | cosmetic only |
| spotify | /features/spotify | off until enabled |
| subscription_proxy | /features/subscription-proxy | no socket |
| tool_gateway | /features/tool-gateway | four tools, each needs a cred id |
| codex_runtime | /features/codex-app-server-runtime | argv only |
| bot_mode | bot screen | mention route, no approve |
| gateway | gateway runner | idempotent ingest |
| platforms | messaging platforms | disabled until a secret id |
| terminal_backends | seven backends | execute unsandboxed refuses |
| cli_tui | CLI / TUI | slash descriptors |
| model_switch | `hermes model` | allowlist, no silent router |
| clarify_todo | clarify and todo tools | inert todos |
| x_search | X search tool | off until a cred id |
| home_assistant | homeassistant toolset | confirm, never run |
| setup_portal | `hermes setup --portal` | plan hash, no secrets on disk |
| video_gen | `tools/video_generation_tool.py`, `tools/xai_video_tools.py` | spend-gated descriptor, no socket |
| threat_scan | `tools/threat_patterns.py`, `tools/tirith_security.py` | classifier only, pairs with approval |
| observability | `hermes_cli/observability/` | projection counters, no second ledger |
| workspace_guard | `tools/self_repo_guard.py`, `tools/spill_safety.py` | jail plus secret-spill refusal |

Base URL for a `/features/...` path: `https://hermes-agent.nousresearch.com/docs/user-guide`.
