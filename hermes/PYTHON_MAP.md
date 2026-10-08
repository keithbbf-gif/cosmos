# Python map

Public tree of [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) branch `main`.
Fetched from `https://api.github.com/repos/NousResearch/hermes-agent/git/trees/main?recursive=1`.
No clone. No source pasted. Paths only.

- Tree SHA: `ac7927ca489e90810b3c3fbb207d41945b2cf3e8`
- `truncated`: `False`
- Tree entries: 18248
- Python blobs: 8041
- Slugs are the rows in `FEATURES.md`. A file has one primary slug and zero or more `also` slugs. Assignment is by path name. Module bodies were not read.

## Counts

| Kind | Python files |
|---|---:|
| product | 1570 |
| packaging | 265 |
| test | 5639 |
| eval | 146 |
| skill_payload | 155 |
| unmapped | 116 |
| init | 150 |

`skill_payload` is Python shipped inside `skills/` and `optional-skills/`. It belongs to the skills feature, but it is not the loader. `init` is `__init__.py` markers.

## Slug index

Every slug in `FEATURES.md`. Counts are Python files, not imports.

| Slug | Primary | Also | Skill payloads |
|---|---:|---:|---:|
| `agent_loop` | 84 | 27 | 0 |
| `tools_toolsets` | 23 | 8 | 0 |
| `tool_search` | 3 | 1 | 0 |
| `file_terminal` | 43 | 28 | 0 |
| `skills` | 36 | 6 | 155 |
| `memory` | 14 | 17 | 0 |
| `memory_providers` | 11 | 15 | 0 |
| `honcho` | 14 | 0 | 0 |
| `session_search` | 31 | 1 | 0 |
| `context_files` | 4 | 0 | 0 |
| `context_references` | 3 | 0 | 0 |
| `checkpoints` | 8 | 0 | 0 |
| `approval` | 17 | 3 | 0 |
| `cron` | 43 | 2 | 0 |
| `delegation` | 22 | 0 | 0 |
| `code_execution` | 7 | 21 | 0 |
| `hooks` | 10 | 0 | 0 |
| `batch` | 4 | 0 | 0 |
| `voice_mode` | 19 | 17 | 0 |
| `wake_word` | 2 | 0 | 0 |
| `tts` | 15 | 3 | 0 |
| `browser` | 37 | 0 | 0 |
| `vision` | 10 | 3 | 0 |
| `image_gen` | 8 | 10 | 25 |
| `web_search` | 23 | 3 | 0 |
| `document_extract` | 1 | 1 | 39 |
| `mcp` | 38 | 4 | 5 |
| `provider_routing` | 82 | 92 | 0 |
| `fallback` | 5 | 0 | 0 |
| `credential_pools` | 37 | 7 | 0 |
| `credential_vault` | 25 | 4 | 0 |
| `prompt_cache` | 4 | 2 | 0 |
| `api_server` | 8 | 0 | 0 |
| `acp` | 16 | 0 | 0 |
| `personality` | 5 | 1 | 0 |
| `skins` | 4 | 0 | 0 |
| `plugins` | 44 | 106 | 0 |
| `web_dashboard` | 64 | 2 | 0 |
| `kanban` | 25 | 3 | 2 |
| `kanban_lanes` | 3 | 0 | 0 |
| `kanban_fleet` | 4 | 0 | 0 |
| `goals` | 4 | 0 | 0 |
| `heartbeat` | 4 | 0 | 0 |
| `curator` | 4 | 0 | 0 |
| `loops` | 2 | 0 | 0 |
| `mixture` | 6 | 0 | 0 |
| `deliverable` | 0 | 0 | 0 |
| `lsp` | 10 | 0 | 0 |
| `computer_use` | 16 | 11 | 0 |
| `language_packs` | 7 | 0 | 0 |
| `pets` | 13 | 0 | 0 |
| `spotify` | 3 | 0 | 0 |
| `subscription_proxy` | 9 | 0 | 0 |
| `tool_gateway` | 29 | 5 | 0 |
| `codex_runtime` | 7 | 4 | 0 |
| `bot_mode` | 17 | 0 | 0 |
| `gateway` | 135 | 144 | 0 |
| `platforms` | 108 | 9 | 0 |
| `terminal_backends` | 24 | 29 | 0 |
| `cli_tui` | 234 | 75 | 0 |
| `model_switch` | 53 | 11 | 0 |
| `clarify_todo` | 5 | 0 | 0 |
| `x_search` | 1 | 0 | 0 |
| `home_assistant` | 1 | 1 | 0 |
| `setup_portal` | 22 | 0 | 0 |

## Install, update, and packaging

Not a product feature. These build, install, update, back up, or publish Hermes. They are not given a slug. `hermes setup` stays under `setup_portal`. `tools/skills_hub_install.py` stays under `skills`. `tools/browser_tool_install.py` stays under `browser`. `agent/lsp/install.py` stays under `lsp`.

265 files.

### (repo root)

- `hermes_bootstrap.py`
- `setup.py`

### hermes_cli/

- `hermes_cli/_install_repair.py`
- `hermes_cli/_launchers.py`
- `hermes_cli/_old_updater.py`
- `hermes_cli/_scan_venv_blockers.py`
- `hermes_cli/_update_takeover.py`
- `hermes_cli/backup.py`
- `hermes_cli/backup_restore.py`
- `hermes_cli/backup_sqlite.py`
- `hermes_cli/boot_bootstrap.py`
- `hermes_cli/build_info.py`
- `hermes_cli/bundled_app.py`
- `hermes_cli/bundles.py`
- `hermes_cli/container_boot.py`
- `hermes_cli/desktop_build_lock.py`
- `hermes_cli/desktop_console.py`
- `hermes_cli/desktop_update_verify.py`
- `hermes_cli/gui_uninstall.py`
- `hermes_cli/install_identity.py`
- `hermes_cli/linux_desktop_entry.py`
- `hermes_cli/macos_signing.py`
- `hermes_cli/main_dep_hints.py`
- `hermes_cli/main_desktop.py`
- `hermes_cli/main_install_repair.py`
- `hermes_cli/main_web_build.py`
- `hermes_cli/managed_uv.py`
- `hermes_cli/npm_engine.py`
- `hermes_cli/old_updater_deps.py`
- `hermes_cli/old_updater_main.py`
- `hermes_cli/post_update.py`
- `hermes_cli/release_channels.py`
- `hermes_cli/source_build.py`
- `hermes_cli/source_check.py`
- `hermes_cli/source_completion.py`
- `hermes_cli/source_releases.py`
- `hermes_cli/source_stamp.py`
- `hermes_cli/stale_modules.py`
- `hermes_cli/subcommands/backup.py`
- `hermes_cli/subcommands/bundles.py`
- `hermes_cli/subcommands/gui.py`
- `hermes_cli/subcommands/uninstall.py`
- `hermes_cli/subcommands/update.py`
- `hermes_cli/uninstall.py`
- `hermes_cli/update_abort_recovery.py`
- `hermes_cli/update_channel.py`
- `hermes_cli/update_cmd.py`
- `hermes_cli/update_cmd_check.py`
- `hermes_cli/update_cmd_common.py`
- `hermes_cli/update_cmd_config.py`
- `hermes_cli/update_cmd_drain_report.py`
- `hermes_cli/update_cmd_fleet.py`
- `hermes_cli/update_cmd_fleet_checkout.py`
- `hermes_cli/update_cmd_fleet_gatewayless.py`
- `hermes_cli/update_cmd_git.py`
- `hermes_cli/update_cmd_maint.py`
- `hermes_cli/update_cmd_stale_survivors.py`
- `hermes_cli/update_cmd_stash.py`
- `hermes_cli/update_cmd_validation.py`
- `hermes_cli/update_cmd_windows.py`
- `hermes_cli/update_cmd_zip.py`
- `hermes_cli/update_completion.py`
- `hermes_cli/update_contract.py`
- `hermes_cli/update_finish.py`
- `hermes_cli/update_fleet_scope.py`
- `hermes_cli/update_handoff.py`
- `hermes_cli/update_host_obligation.py`
- `hermes_cli/update_inventory.py`
- `hermes_cli/update_lock.py`
- `hermes_cli/update_owning_install.py`
- `hermes_cli/update_receipt.py`
- `hermes_cli/update_restart_recovery.py`
- `hermes_cli/update_serve_obligations.py`
- `hermes_cli/update_serve_resume.py`
- `hermes_cli/update_stage.py`
- `hermes_cli/venv_sync.py`
- `hermes_cli/version_info.py`
- `hermes_cli/web_deps.py`
- `hermes_cli/web_git.py`

### tools/

- `tools/lazy_deps.py`

### pm/

`pm/` is the package manager (install, update, lock, uv, plugin eviction). All 48 files are packaging.

- `pm/__init__.py`
- `pm/_marker_eval.py`
- `pm/_uv.py`
- `pm/artifact_mirror.py`
- `pm/build_env.py`
- `pm/build_operations.py`
- `pm/cli.py`
- `pm/client.py`
- `pm/defaults.py`
- `pm/download_state.py`
- `pm/downloader.py`
- `pm/environment.py`
- `pm/environments.py`
- `pm/environments_adopt.py`
- `pm/extras.py`
- `pm/features.py`
- `pm/filesystem.py`
- `pm/index_config.py`
- `pm/install.py`
- `pm/launch.py`
- `pm/lock.py`
- `pm/native_build.py`
- `pm/network.py`
- `pm/operations.py`
- `pm/package.py`
- `pm/packages.py`
- `pm/paths.py`
- `pm/plugin_declarations.py`
- `pm/plugin_eviction.py`
- `pm/plugin_inputs.py`
- `pm/plugins_state.py`
- `pm/progress.py`
- `pm/publication.py`
- `pm/receipt.py`
- `pm/recovery.py`
- `pm/registry.py`
- `pm/runtime.py`
- `pm/runtime_stage.py`
- `pm/security_packages.py`
- `pm/shell.py`
- `pm/store.py`
- `pm/termux_libs.py`
- `pm/testenv.py`
- `pm/update.py`
- `pm/uv_cache_prune.py`
- `pm/worker.py`
- `pm/worker_operations.py`
- `pm/workspace.py`

### scripts/

`scripts/` is CI, release, bundle, Termux, and desktop build. 118 files, grouped:

- `scripts/(root files)`: 38
- `scripts/build`: 6
- `scripts/bundles`: 13
- `scripts/ci`: 18
- `scripts/desktop-update`: 1
- `scripts/observability`: 2
- `scripts/releases`: 28
- `scripts/termux`: 12

### apps/

- `apps/desktop/e2e/update/seed.py`
- `apps/desktop/electron/fixtures/source-backend.py`
- `apps/desktop/electron/native/hud-modifier-x11.test.py`
- `apps/desktop/electron/pool-retirement-live-fixture/cron_work.py`
- `apps/desktop/electron/pool-retirement-live-fixture/serve.py`
- `apps/desktop/scripts/check-appinstaller-update.py`
- `apps/desktop/scripts/check-store-update.py`
- `apps/desktop/scripts/perf/gateway_attach_bench.py`
- `apps/desktop/scripts/prepare_dmgbuild.py`

### docker/

- `docker/build_agent.py`

### nix/

- `nix/tests/agent-references.py`
- `nix/tests/desktop-backend.py`

### website/

- `website/scripts/check_doc_links.py`
- `website/scripts/extract-automation-blueprints.py`
- `website/scripts/extract-plugins.py`
- `website/scripts/extract-skills.py`
- `website/scripts/fetch-plugin-stars.py`
- `website/scripts/generate-llms-txt.py`
- `website/scripts/generate-skill-docs.py`

## Directory groups

Product Python only. Packaging is above. Tests, evals, and skill payloads follow. `__init__.py` markers are listed once per top-level tree and have no slug.

## (repo root)

Top-level modules. `run_agent.py` is the tool-calling loop. `model_tools.py` with `toolsets.py` and `toolset_distributions.py` is toolset membership. `hermes_state_*.py` is the session DB (SQLite WAL and FTS5), not its own product.

Slugs in this tree: `agent_loop`, `batch`, `checkpoints`, `cli_tui`, `gateway`, `mcp`, `platforms`, `provider_routing`, `session_search`, `tools_toolsets`.

### `session_search`

10 files. Primary slug `session_search`.

- `hermes_state.py` (also `gateway`)
- `hermes_state_dbfile.py`
- `hermes_state_fts.py`
- `hermes_state_messages.py` (also `agent_loop`)
- `hermes_state_schema.py`
- `hermes_state_search.py`
- `hermes_state_sessions.py` (also `agent_loop`)
- `hermes_state_timeline.py`
- `hermes_state_titles.py`
- `hermes_state_wal.py`

### `batch`

3 files. Primary slug `batch`.

- `batch_runner.py`
- `mini_swe_runner.py` (also `code_execution`)
- `trajectory_compressor.py` (also `agent_loop`)

### `tools_toolsets`

3 files. Primary slug `tools_toolsets`.

- `model_tools.py`
- `toolset_distributions.py`
- `toolsets.py`

### `agent_loop`

2 files. Primary slug `agent_loop`.

- `hermes_state_compression.py`
- `run_agent.py`

### `gateway`

2 files. Primary slug `gateway`.

- `hermes_state_gateway.py`
- `registration_lifecycle.py`

### `checkpoints`

1 file. Primary slug `checkpoints`.

- `hermes_state_rewind.py` (also `session_search`)

### `cli_tui`

1 file. Primary slug `cli_tui`.

- `cli.py`

### `mcp`

1 file. Primary slug `mcp`.

- `mcp_serve.py`

### `platforms`

1 file. Primary slug `platforms`.

- `hermes_state_telegram.py` (also `gateway`)

### `provider_routing`

1 file. Primary slug `provider_routing`.

- `hermes_state_usage.py`

### No FEATURES.md slug

In this tree, not packaging, and no slug fits the path name. Shared infrastructure stays here instead of being forced onto a feature.

- `hermes_constants.py`
- `hermes_constants_scratch.py`
- `hermes_logging.py`
- `hermes_startup_watchdog.py`
- `hermes_state_common.py`
- `hermes_state_errors.py`
- `hermes_state_guard.py`
- `hermes_state_health.py`
- `hermes_state_holders.py`
- `hermes_state_identity.py`
- `hermes_state_ids.py`
- `hermes_state_lockguard.py`
- `hermes_state_lockowners.py`
- `hermes_state_maintenance.py`
- `hermes_state_portability.py`
- `hermes_state_profile_repair.py`
- `hermes_state_readpool.py`
- `hermes_state_registry.py`
- `hermes_state_repair.py`
- `hermes_state_user_copy.py`
- `hermes_time.py`
- `hermes_yaml.py`
- `utils.py`

## agent/

Runtime next to the loop: turns, provider adapters, credentials, compression, and feature modules that do not live under `tools/`. Files that are only turn machinery stay on `agent_loop`.

Slugs in this tree: `acp`, `agent_loop`, `approval`, `batch`, `browser`, `clarify_todo`, `cli_tui`, `codex_runtime`, `context_files`, `context_references`, `credential_pools`, `credential_vault`, `cron`, `curator`, `delegation`, `fallback`, `file_terminal`, `gateway`, `hooks`, `image_gen`, `kanban`, `language_packs`, `lsp`, `memory`, `memory_providers`, `mixture`, `model_switch`, `personality`, `pets`, `platforms`, `plugins`, `prompt_cache`, `provider_routing`, `setup_portal`, `skills`, `subscription_proxy`, `terminal_backends`, `tools_toolsets`, `tts`, `vision`, `voice_mode`, `web_search`.

Package markers (no slug), 10 files:

- `agent/__init__.py`
- `agent/lsp/__init__.py`
- `agent/monitoring/__init__.py`
- `agent/pet/__init__.py`
- `agent/pet/generate/__init__.py`
- `agent/proxy_sources/__init__.py`
- `agent/secret_sources/__init__.py`
- `agent/transports/__init__.py`
- `agent/vault_backends/__init__.py`
- `agent/verify/__init__.py`

### `agent_loop`

78 files. Primary slug `agent_loop`.

- `agent/activity_tracking.py`
- `agent/agent_init.py`
- `agent/agent_runtime_helpers.py`
- `agent/async_utils.py`
- `agent/bounded_response.py`
- `agent/compaction_display.py` (also `cli_tui`)
- `agent/compression_facade.py`
- `agent/compression_marker.py`
- `agent/context_breakdown.py`
- `agent/context_compressor.py`
- `agent/context_compressor_summary.py`
- `agent/context_engine.py`
- `agent/context_pin.py`
- `agent/conversation_compression.py`
- `agent/conversation_compression_archive.py`
- `agent/conversation_compression_manual.py`
- `agent/conversation_compression_reply_anchor.py`
- `agent/conversation_loop.py`
- `agent/deadline.py`
- `agent/errors.py`
- `agent/estop.py`
- `agent/history_commentary.py`
- `agent/interrupt_compat.py`
- `agent/interrupt_control.py`
- `agent/interrupt_scope.py`
- `agent/iteration_budget.py`
- `agent/manual_compression_feedback.py`
- `agent/message_content.py`
- `agent/message_metadata.py`
- `agent/message_sanitization.py`
- `agent/micro_compaction.py`
- `agent/native_compaction.py`
- `agent/notification_presentation.py`
- `agent/repetition_guard.py`
- `agent/replay_cleanup.py`
- `agent/runtime_cwd.py`
- `agent/runtime_self_protection.py`
- `agent/session_activity.py`
- `agent/session_persistence.py`
- `agent/stream_delivery.py` (also `gateway`)
- `agent/stream_diag.py`
- `agent/stream_single_writer.py`
- `agent/think_scrubber.py`
- `agent/thinking_timeout_guidance.py`
- `agent/thread_scoped_output.py`
- `agent/tool_dispatch_helpers.py` (also `tools_toolsets`)
- `agent/tool_executor.py` (also `tools_toolsets`)
- `agent/tool_guardrails.py` (also `tools_toolsets`)
- `agent/tool_result_classification.py` (also `tools_toolsets`)
- `agent/transcript_repair.py`
- `agent/turn_author.py`
- `agent/turn_context.py`
- `agent/turn_context_compaction.py`
- `agent/turn_empty_response.py`
- `agent/turn_explainers.py`
- `agent/turn_facade.py`
- `agent/turn_facade_lease.py`
- `agent/turn_failure_copy.py`
- `agent/turn_final_response.py`
- `agent/turn_finalizer.py`
- `agent/turn_iteration_prep.py`
- `agent/turn_liveness.py`
- `agent/turn_loop_errors.py`
- `agent/turn_overflow.py`
- `agent/turn_preflight.py`
- `agent/turn_preflight_gate.py`
- `agent/turn_recovery.py`
- `agent/turn_recovery_autorecover.py`
- `agent/turn_request_assembly.py`
- `agent/turn_response_check.py`
- `agent/turn_response_intake.py`
- `agent/turn_retry_state.py`
- `agent/turn_stop_gates.py`
- `agent/turn_summary.py`
- `agent/turn_tool_round.py`
- `agent/turn_tool_validation.py`
- `agent/turn_truncation.py`
- `agent/turn_usage.py` (also `provider_routing`)

### `provider_routing`

64 files. Primary slug `provider_routing`.

- `agent/account_usage.py`
- `agent/anthropic_adapter.py`
- `agent/anthropic_credentials.py`
- `agent/anthropic_endpoints.py`
- `agent/anthropic_message_convert.py`
- `agent/anthropic_thinking_policy.py`
- `agent/anthropic_thinking_replay.py`
- `agent/api_error_summary.py`
- `agent/aux_accounting.py` (also `agent_loop`)
- `agent/auxiliary_async_rebuild.py`
- `agent/auxiliary_client.py`
- `agent/auxiliary_health.py`
- `agent/auxiliary_reasoning_floor.py`
- `agent/auxiliary_structured_output.py`
- `agent/auxiliary_unavailable.py`
- `agent/auxiliary_wire.py`
- `agent/azure_identity_adapter.py`
- `agent/backend_identity.py`
- `agent/bedrock_adapter.py`
- `agent/billing_links.py`
- `agent/billing_usage.py`
- `agent/billing_view.py`
- `agent/chat_completion_helpers.py`
- `agent/chat_completion_helpers_relay.py`
- `agent/chat_completion_nonstream.py`
- `agent/chat_completion_stream_monitor.py`
- `agent/chat_completion_wait_notice.py`
- `agent/client_lifecycle.py`
- `agent/codex_headers.py` (also `codex_runtime`)
- `agent/codex_responses_adapter.py` (also `codex_runtime`)
- `agent/credits_tracker.py`
- `agent/empty_response_guard.py`
- `agent/error_classifier.py`
- `agent/error_surface.py` (also `agent_loop`)
- `agent/gemini_native_adapter.py`
- `agent/gemini_schema.py`
- `agent/lmstudio_reasoning.py`
- `agent/moonshot_schema.py`
- `agent/nous_rate_guard.py`
- `agent/nous_wire.py`
- `agent/opencode_affinity.py`
- `agent/provider_base.py`
- `agent/provider_projection.py`
- `agent/provider_registry.py`
- `agent/rate_limit_credits.py`
- `agent/rate_limit_tracker.py`
- `agent/retry_utils.py`
- `agent/sdk_transform_bypass.py`
- `agent/ssl_verify.py`
- `agent/subscription_view.py`
- `agent/transports/anthropic.py`
- `agent/transports/base.py`
- `agent/transports/bedrock.py`
- `agent/transports/chat_completions.py`
- `agent/transports/codex.py` (also `codex_runtime`)
- `agent/transports/codex_event_projector.py`
- `agent/transports/hermes_tools_mcp_server.py`
- `agent/transports/types.py`
- `agent/turn_api_call.py`
- `agent/turn_api_error.py`
- `agent/turn_api_request.py`
- `agent/usage_anchor.py`
- `agent/usage_pricing.py`
- `agent/vertex_adapter.py`

### `credential_vault`

14 files. Primary slug `credential_vault`.

- `agent/secret_scope.py` (also `agent_loop`)
- `agent/secret_sources/_cache.py` (also `credential_pools`)
- `agent/secret_sources/base.py` (also `credential_pools`)
- `agent/secret_sources/bitwarden.py` (also `credential_pools`)
- `agent/secret_sources/command.py` (also `credential_pools`)
- `agent/secret_sources/onepassword.py` (also `credential_pools`)
- `agent/secret_sources/registry.py` (also `credential_pools`)
- `agent/vault_backends/base.py`
- `agent/vault_backends/bitwarden.py`
- `agent/vault_backends/local.py`
- `agent/vault_backends/onepassword.py`
- `agent/vault_backends/unlock.py`
- `agent/vault_login_classifier.py`
- `agent/vault_store.py`

### `lsp`

10 files. Primary slug `lsp`.

- `agent/lsp/cli.py`
- `agent/lsp/client.py`
- `agent/lsp/eventlog.py`
- `agent/lsp/install.py`
- `agent/lsp/manager.py`
- `agent/lsp/protocol.py`
- `agent/lsp/range_shift.py`
- `agent/lsp/reporter.py`
- `agent/lsp/servers.py`
- `agent/lsp/workspace.py`

### `model_switch`

9 files. Primary slug `model_switch`.

- `agent/fast_mode.py` (also `provider_routing`)
- `agent/model_metadata.py` (also `provider_routing`)
- `agent/model_metadata_http.py` (also `provider_routing`)
- `agent/models_dev.py` (also `provider_routing`)
- `agent/reasoning_effort.py` (also `provider_routing`)
- `agent/reasoning_params.py` (also `provider_routing`)
- `agent/reasoning_summaries.py` (also `provider_routing`)
- `agent/reasoning_timeouts.py` (also `provider_routing`)
- `agent/served_model.py` (also `provider_routing`)

### `pets`

9 files. Primary slug `pets`.

- `agent/pet/constants.py`
- `agent/pet/generate/atlas.py` (also `image_gen`)
- `agent/pet/generate/imagegen.py` (also `image_gen`)
- `agent/pet/generate/orchestrate.py` (also `image_gen`)
- `agent/pet/generate/prompts.py` (also `image_gen`)
- `agent/pet/manifest.py`
- `agent/pet/render.py`
- `agent/pet/state.py`
- `agent/pet/store.py`

### `cli_tui`

8 files. Primary slug `cli_tui`.

- `agent/display.py`
- `agent/legacy_cli.py`
- `agent/markdown_tables.py`
- `agent/oneshot.py`
- `agent/oneshot_footprint.py`
- `agent/status_output.py`
- `agent/surface_switch.py`
- `agent/title_generator.py`

### `credential_pools`

7 files. Primary slug `credential_pools`.

- `agent/command_token_source.py` (also `credential_vault`)
- `agent/credential_persistence.py` (also `credential_vault`)
- `agent/credential_pool.py`
- `agent/credential_pool_admin.py`
- `agent/credential_pool_model_cooldowns.py`
- `agent/credential_pool_plugin.py`
- `agent/credential_sources.py` (also `credential_vault`)

### `hooks`

6 files. Primary slug `hooks`.

- `agent/api_request_hooks.py`
- `agent/auxiliary_hooks.py` (also `provider_routing`)
- `agent/outbound_webhooks.py`
- `agent/plugin_stream_hooks.py` (also `plugins`)
- `agent/shell_hooks.py`
- `agent/verify_hooks.py`

### `memory`

5 files. Primary slug `memory`.

- `agent/learn_prompt.py` (also `skills`)
- `agent/learning_graph.py` (also `skills`)
- `agent/learning_graph_render.py` (also `skills`)
- `agent/learning_mutations.py` (also `skills`)
- `agent/memory_manager.py` (also `skills`)

### `vision`

5 files. Primary slug `vision`.

- `agent/image_eviction_policy.py` (also `image_gen`)
- `agent/image_routing.py` (also `image_gen`)
- `agent/image_token_cost.py` (also `image_gen`)
- `agent/provider_media.py` (also `image_gen`)
- `agent/vision_message_prep.py` (also `image_gen`)

### `codex_runtime`

4 files. Primary slug `codex_runtime`.

- `agent/codex_runtime.py`
- `agent/codex_runtime_history_seed.py`
- `agent/transports/codex_app_server.py`
- `agent/transports/codex_app_server_session.py`

### `gateway`

4 files. Primary slug `gateway`.

- `agent/relay_cwd.py` (also `provider_routing`)
- `agent/relay_llm.py` (also `provider_routing`)
- `agent/relay_runtime.py` (also `provider_routing`)
- `agent/relay_tools.py` (also `provider_routing`)

### `skills`

4 files. Primary slug `skills`.

- `agent/skill_bundles.py`
- `agent/skill_commands.py`
- `agent/skill_preprocessing.py`
- `agent/skill_utils.py`

### `context_files`

3 files. Primary slug `context_files`.

- `agent/coding_context.py`
- `agent/context_file_sources.py`
- `agent/subdirectory_hints.py`

### `language_packs`

3 files. Primary slug `language_packs`.

- `agent/i18n.py`
- `agent/i18n_languages.py`
- `agent/i18n_layers.py`

### `mixture`

3 files. Primary slug `mixture`.

- `agent/moa_alternation.py` (also `agent_loop`)
- `agent/moa_loop.py` (also `agent_loop`)
- `agent/moa_trace.py` (also `agent_loop`)

### `personality`

3 files. Primary slug `personality`.

- `agent/plan_prompt.py` (also `agent_loop`)
- `agent/prompt_builder.py` (also `agent_loop`)
- `agent/system_prompt.py` (also `agent_loop`)

### `prompt_cache`

3 files. Primary slug `prompt_cache`.

- `agent/prompt_cache_boundary.py`
- `agent/prompt_cache_scope.py`
- `agent/prompt_caching.py`

### `web_search`

3 files. Primary slug `web_search`.

- `agent/search_policy.py` (also `tool_search`)
- `agent/web_search_provider.py`
- `agent/web_search_registry.py`

### `acp`

2 files. Primary slug `acp`.

- `agent/acp_openai_bridge.py` (also `provider_routing`)
- `agent/copilot_acp_client.py` (also `provider_routing`)

### `browser`

2 files. Primary slug `browser`.

- `agent/browser_provider.py`
- `agent/browser_registry.py`

### `curator`

2 files. Primary slug `curator`.

- `agent/curator.py` (also `memory`)
- `agent/curator_backup.py` (also `memory`)

### `delegation`

2 files. Primary slug `delegation`.

- `agent/delegation_context.py` (also `agent_loop`)
- `agent/subagent_lifecycle.py` (also `agent_loop`)

### `fallback`

2 files. Primary slug `fallback`.

- `agent/auxiliary_fallback_recovery.py` (also `provider_routing`)
- `agent/fallback_cooldown.py` (also `provider_routing`)

### `image_gen`

2 files. Primary slug `image_gen`.

- `agent/image_gen_provider.py`
- `agent/image_gen_registry.py`

### `kanban`

2 files. Primary slug `kanban`.

- `agent/kanban_stop.py`
- `agent/kanban_turn_recovery.py`

### `setup_portal`

2 files. Primary slug `setup_portal`.

- `agent/onboarding.py`
- `agent/portal_tags.py`

### `subscription_proxy`

2 files. Primary slug `subscription_proxy`.

- `agent/proxy_bypass.py`
- `agent/proxy_sources/iron_proxy.py`

### `terminal_backends`

2 files. Primary slug `terminal_backends`.

- `agent/terminal_env_provider.py` (also `file_terminal`)
- `agent/terminal_env_registry.py` (also `file_terminal`)

### `tts`

2 files. Primary slug `tts`.

- `agent/tts_provider.py`
- `agent/tts_registry.py`

### `voice_mode`

2 files. Primary slug `voice_mode`.

- `agent/transcription_provider.py`
- `agent/transcription_registry.py`

### `approval`

1 file. Primary slug `approval`.

- `agent/terminal_approval_batch.py` (also `file_terminal`)

### `batch`

1 file. Primary slug `batch`.

- `agent/trajectory.py` (also `agent_loop`)

### `clarify_todo`

1 file. Primary slug `clarify_todo`.

- `agent/side_question.py` (also `agent_loop`)

### `context_references`

1 file. Primary slug `context_references`.

- `agent/context_references.py`

### `cron`

1 file. Primary slug `cron`.

- `agent/periodic_scheduler.py` (also `agent_loop`)

### `file_terminal`

1 file. Primary slug `file_terminal`.

- `agent/file_safety.py` (also `approval`)

### `memory_providers`

1 file. Primary slug `memory_providers`.

- `agent/memory_provider.py` (also `memory`)

### `platforms`

1 file. Primary slug `platforms`.

- `agent/reactions.py` (also `gateway`)

### `plugins`

1 file. Primary slug `plugins`.

- `agent/plugin_llm.py` (also `provider_routing`)

### `tools_toolsets`

1 file. Primary slug `tools_toolsets`.

- `agent/inline_tool_executors.py` (also `agent_loop`)

### No FEATURES.md slug

In this tree, not packaging, and no slug fits the path name. Shared infrastructure stays here instead of being forced onto a feature.

- `agent/background_review.py`
- `agent/battery.py`
- `agent/insights.py`
- `agent/jiter_preload.py`
- `agent/lazy_forward.py`
- `agent/monitoring/cron_health.py`
- `agent/monitoring/emitter.py`
- `agent/monitoring/events.py`
- `agent/monitoring/gateway_health.py`
- `agent/monitoring/gateway_health_export.py`
- `agent/monitoring/otlp_exporter.py`
- `agent/monitoring/policy.py`
- `agent/monitoring/redaction.py`
- `agent/process_bootstrap.py`
- `agent/redact.py`
- `agent/review_engine.py`
- `agent/review_idle_queue.py`
- `agent/trace_upload.py`
- `agent/verification_evidence.py`
- `agent/verification_stop.py`
- `agent/verify/environment.py`
- `agent/verify/recipes.py`
- `agent/verify/runner.py`
- `agent/video_gen_provider.py`
- `agent/video_gen_registry.py`

## tools/

Tool implementations. Terminal, files, delegate, approval, browser, memory, cron, session search, clarify, and todo are here, plus computer use, voice, MCP, and kanban tools.

Slugs in this tree: `agent_loop`, `approval`, `bot_mode`, `browser`, `checkpoints`, `clarify_todo`, `cli_tui`, `code_execution`, `computer_use`, `credential_vault`, `cron`, `delegation`, `document_extract`, `file_terminal`, `home_assistant`, `hooks`, `image_gen`, `kanban`, `mcp`, `memory`, `platforms`, `plugins`, `provider_routing`, `session_search`, `setup_portal`, `skills`, `terminal_backends`, `tool_gateway`, `tool_search`, `tools_toolsets`, `tts`, `vision`, `voice_mode`, `wake_word`, `web_search`, `x_search`.

Package markers (no slug), 7 files:

- `tools/__init__.py`
- `tools/bot_desktop/__init__.py`
- `tools/computer_use/__init__.py`
- `tools/connectors/__init__.py`
- `tools/connectors/gateway/__init__.py`
- `tools/connectors/portal/__init__.py`
- `tools/environments/__init__.py`

### `file_terminal`

34 files. Primary slug `file_terminal`.

- `tools/binary_extensions.py`
- `tools/close_terminal_tool.py` (also `terminal_backends`)
- `tools/env_passthrough.py` (also `terminal_backends`)
- `tools/env_probe.py` (also `terminal_backends`)
- `tools/file_operations.py`
- `tools/file_operations_common.py`
- `tools/file_operations_lint.py`
- `tools/file_operations_search.py`
- `tools/file_state.py`
- `tools/file_tools.py`
- `tools/file_tools_paths.py`
- `tools/file_tools_read_tracking.py`
- `tools/file_tools_write_guards.py`
- `tools/fuzzy_match.py`
- `tools/patch_parser.py`
- `tools/path_security.py`
- `tools/process_registry.py` (also `terminal_backends`)
- `tools/process_registry_notifications.py` (also `terminal_backends`)
- `tools/process_registry_results.py` (also `terminal_backends`)
- `tools/project_tools.py`
- `tools/pty_query_responder.py` (also `terminal_backends`)
- `tools/read_terminal_tool.py` (also `terminal_backends`)
- `tools/shell_heredoc.py` (also `terminal_backends`)
- `tools/terminal_hints.py` (also `terminal_backends`)
- `tools/terminal_scope.py` (also `terminal_backends`)
- `tools/terminal_tool.py` (also `terminal_backends`)
- `tools/terminal_tool_backends.py` (also `terminal_backends`)
- `tools/terminal_tool_background.py` (also `terminal_backends`)
- `tools/terminal_tool_config.py` (also `terminal_backends`)
- `tools/terminal_tool_guards.py` (also `terminal_backends`)
- `tools/terminal_tool_lifecycle.py` (also `terminal_backends`)
- `tools/terminal_tool_result.py` (also `terminal_backends`)
- `tools/terminal_tool_sudo.py` (also `terminal_backends`)
- `tools/working_diff.py`

### `skills`

29 files. Primary slug `skills`.

- `tools/skill_ledger.py`
- `tools/skill_linter.py`
- `tools/skill_manager_batch.py`
- `tools/skill_manager_guards.py`
- `tools/skill_manager_tool.py`
- `tools/skill_provenance.py`
- `tools/skill_usage.py`
- `tools/skillevaluator_scan.py`
- `tools/skills_ast_audit.py`
- `tools/skills_guard.py`
- `tools/skills_hub.py`
- `tools/skills_hub_clawhub.py`
- `tools/skills_hub_github.py`
- `tools/skills_hub_install.py`
- `tools/skills_hub_models.py`
- `tools/skills_hub_official.py`
- `tools/skills_hub_search.py`
- `tools/skills_hub_skillssh.py`
- `tools/skills_hub_sources.py`
- `tools/skills_sync.py`
- `tools/skills_sync_bundled_ops.py`
- `tools/skills_sync_client.py`
- `tools/skills_sync_client_org.py`
- `tools/skills_sync_client_wire.py`
- `tools/skills_sync_optional.py`
- `tools/skills_tool.py`
- `tools/skills_tool_dedup.py`
- `tools/skills_tool_plugin.py`
- `tools/skills_tool_setup.py`

### `mcp`

26 files. Primary slug `mcp`.

- `tools/mcp_dashboard_oauth.py` (also `web_dashboard`)
- `tools/mcp_death_supervisor.py`
- `tools/mcp_liveness.py`
- `tools/mcp_oauth.py`
- `tools/mcp_oauth_device.py`
- `tools/mcp_oauth_manager.py`
- `tools/mcp_oauth_provider.py`
- `tools/mcp_schema_cache.py`
- `tools/mcp_tool.py`
- `tools/mcp_tool_agent.py`
- `tools/mcp_tool_common.py`
- `tools/mcp_tool_config.py`
- `tools/mcp_tool_content.py`
- `tools/mcp_tool_discovery.py`
- `tools/mcp_tool_errors.py`
- `tools/mcp_tool_handlers.py`
- `tools/mcp_tool_health.py`
- `tools/mcp_tool_lifecycle.py`
- `tools/mcp_tool_loop.py`
- `tools/mcp_tool_node_abi.py`
- `tools/mcp_tool_registration.py`
- `tools/mcp_tool_sampling.py`
- `tools/mcp_tool_schema.py`
- `tools/mcp_tool_scope.py`
- `tools/mcp_tool_server_run.py`
- `tools/mcp_tool_transport.py`

### `browser`

24 files. Primary slug `browser`.

- `tools/browser_camofox.py`
- `tools/browser_camofox_state.py`
- `tools/browser_cdp_tool.py`
- `tools/browser_dialog_tool.py`
- `tools/browser_extension_router.py`
- `tools/browser_lightpanda.py`
- `tools/browser_supervisor.py`
- `tools/browser_supervisor_dialogs.py`
- `tools/browser_supervisor_frames.py`
- `tools/browser_tool.py`
- `tools/browser_tool_cdp.py`
- `tools/browser_tool_cloud.py`
- `tools/browser_tool_eval_policy.py`
- `tools/browser_tool_install.py`
- `tools/browser_tool_lifecycle.py`
- `tools/browser_tool_lightpanda_fallback.py`
- `tools/browser_tool_origin.py`
- `tools/browser_tool_real_profile.py`
- `tools/browser_tool_session.py`
- `tools/browser_tool_snapshot.py`
- `tools/browser_tool_vision.py` (also `vision`)
- `tools/browser_use_cli.py`
- `tools/browser_vault_tool.py` (also `credential_vault`)
- `tools/website_policy.py` (also `web_search`)

### `tool_gateway`

24 files. Primary slug `tool_gateway`.

- `tools/connectors/account.py`
- `tools/connectors/catalog.py`
- `tools/connectors/catalog_tool.py`
- `tools/connectors/contract.py`
- `tools/connectors/dispatch.py`
- `tools/connectors/gateway/bridge.py`
- `tools/connectors/gateway/client.py`
- `tools/connectors/gateway/config.py`
- `tools/connectors/gateway/errors.py`
- `tools/connectors/gateway/merge.py`
- `tools/connectors/gateway/names.py`
- `tools/connectors/gateway/wire.py`
- `tools/connectors/live.py`
- `tools/connectors/managed.py`
- `tools/connectors/mcp.py` (also `mcp`)
- `tools/connectors/mcp_oauth.py` (also `mcp`)
- `tools/connectors/operation.py`
- `tools/connectors/run.py`
- `tools/connectors/search.py`
- `tools/connectors/targets.py`
- `tools/connectors/tool.py`
- `tools/connectors/turn.py`
- `tools/managed_gateway_auth.py`
- `tools/managed_tool_gateway.py`

### `terminal_backends`

19 files. Primary slug `terminal_backends`.

- `tools/environments/base.py` (also `file_terminal`, `code_execution`)
- `tools/environments/base_output.py` (also `file_terminal`, `code_execution`)
- `tools/environments/base_session_env.py` (also `file_terminal`, `code_execution`)
- `tools/environments/base_wait.py` (also `file_terminal`, `code_execution`)
- `tools/environments/daytona.py` (also `file_terminal`, `code_execution`)
- `tools/environments/docker.py` (also `file_terminal`, `code_execution`)
- `tools/environments/docker_egress.py` (also `file_terminal`, `code_execution`)
- `tools/environments/file_sync.py` (also `file_terminal`, `code_execution`)
- `tools/environments/local.py` (also `file_terminal`, `code_execution`)
- `tools/environments/local_env_policy.py` (also `file_terminal`, `code_execution`)
- `tools/environments/local_pythonpath.py` (also `file_terminal`, `code_execution`)
- `tools/environments/managed_modal.py` (also `file_terminal`, `code_execution`)
- `tools/environments/modal.py` (also `file_terminal`, `code_execution`)
- `tools/environments/path_utils.py` (also `file_terminal`, `code_execution`)
- `tools/environments/remote_common.py` (also `file_terminal`, `code_execution`)
- `tools/environments/singularity.py` (also `file_terminal`, `code_execution`)
- `tools/environments/ssh.py` (also `file_terminal`, `code_execution`)
- `tools/environments/streams.py` (also `file_terminal`, `code_execution`)
- `tools/environments/vercel_sandbox.py` (also `file_terminal`, `code_execution`)

### `bot_mode`

14 files. Primary slug `bot_mode`.

- `tools/bot_desktop/browser.py`
- `tools/bot_desktop/install.py`
- `tools/bot_desktop/lease.py`
- `tools/bot_desktop/placement.py`
- `tools/bot_desktop/resources.py`
- `tools/bot_desktop/rfb_filter.py`
- `tools/bot_desktop/runtime.py`
- `tools/bot_desktop/sandbox_host.py`
- `tools/bot_desktop/thumbnail.py`
- `tools/bot_failure_reasons.py`
- `tools/bot_live_delivery.py`
- `tools/bot_mode_dm.py`
- `tools/bot_mode_probe.py`
- `tools/bot_relay.py`

### `cli_tui`

14 files. Primary slug `cli_tui`.

- `tools/annotate_preview_tool.py` (also `computer_use`)
- `tools/apply_layout_tool.py` (also `computer_use`)
- `tools/close_preview_tool.py` (also `computer_use`)
- `tools/desktop_ui.py` (also `computer_use`)
- `tools/drive_preview_tool.py` (also `computer_use`)
- `tools/focus_pane_tool.py` (also `computer_use`)
- `tools/interrupt.py`
- `tools/open_preview_tool.py` (also `computer_use`)
- `tools/preview_tool.py` (also `computer_use`)
- `tools/read_preview_tool.py` (also `computer_use`)
- `tools/read_window_tool.py` (also `computer_use`)
- `tools/slash_confirm.py` (also `approval`)
- `tools/tip_tool.py`
- `tools/tour_tool.py`

### `computer_use`

14 files. Primary slug `computer_use`.

- `tools/computer_use/backend.py`
- `tools/computer_use/cua_backend.py`
- `tools/computer_use/cua_backend_capture.py`
- `tools/computer_use/cua_backend_daemon.py`
- `tools/computer_use/cua_backend_driver.py`
- `tools/computer_use/cua_backend_input.py`
- `tools/computer_use/cua_backend_parse.py`
- `tools/computer_use/cua_backend_session.py`
- `tools/computer_use/doctor.py`
- `tools/computer_use/permissions.py`
- `tools/computer_use/schema.py`
- `tools/computer_use/tool.py`
- `tools/computer_use/vision_routing.py` (also `vision`)
- `tools/computer_use_tool.py`

### `delegation`

14 files. Primary slug `delegation`.

- `tools/async_delegation.py`
- `tools/async_delegation_recovery_hints.py`
- `tools/delegate_tool.py`
- `tools/delegate_tool_child_run.py`
- `tools/delegate_tool_config.py`
- `tools/delegate_tool_dispatch.py`
- `tools/delegate_tool_progress.py`
- `tools/delegate_tool_registry.py`
- `tools/delegate_tool_results.py`
- `tools/delegate_tool_tasks.py`
- `tools/delegate_tool_toolsets.py`
- `tools/delegation_live_log.py`
- `tools/delegation_output_schema.py`
- `tools/subagent_worktree.py`

### `tts`

12 files. Primary slug `tts`.

- `tools/neutts_synth.py` (also `voice_mode`)
- `tools/tts_command_provider.py` (also `voice_mode`)
- `tools/tts_streaming.py` (also `voice_mode`)
- `tools/tts_text_normalize.py` (also `voice_mode`)
- `tools/tts_tool.py` (also `voice_mode`)
- `tools/tts_tool_delivery.py` (also `voice_mode`)
- `tools/tts_tool_lifecycle.py` (also `voice_mode`)
- `tools/tts_tool_local.py` (also `voice_mode`)
- `tools/tts_tool_openai.py` (also `voice_mode`)
- `tools/tts_tool_plugins.py` (also `voice_mode`)
- `tools/tts_tool_providers.py` (also `voice_mode`)
- `tools/tts_tool_speaker.py` (also `voice_mode`)

### `voice_mode`

12 files. Primary slug `voice_mode`.

- `tools/audio_container.py`
- `tools/stt_lease.py`
- `tools/transcription_audio.py`
- `tools/transcription_cloud.py`
- `tools/transcription_command.py`
- `tools/transcription_common.py`
- `tools/transcription_local.py`
- `tools/transcription_tools.py`
- `tools/voice_client_config.py`
- `tools/voice_live.py`
- `tools/voice_mode.py`
- `tools/voice_mode_transcript.py`

### `platforms`

11 files. Primary slug `platforms`.

- `tools/discord_tool.py` (also `gateway`)
- `tools/feishu_doc_tool.py` (also `gateway`)
- `tools/feishu_drive_tool.py` (also `gateway`)
- `tools/feishu_lark.py` (also `gateway`)
- `tools/microsoft_graph_auth.py` (also `gateway`)
- `tools/microsoft_graph_client.py` (also `gateway`)
- `tools/react_to_message_tool.py` (also `gateway`)
- `tools/send_message_senders.py` (also `gateway`)
- `tools/send_message_targets.py` (also `gateway`)
- `tools/send_message_tool.py` (also `gateway`)
- `tools/yuanbao_tools.py` (also `gateway`)

### `approval`

9 files. Primary slug `approval`.

- `tools/approval.py`
- `tools/approval_context.py`
- `tools/approval_detection.py`
- `tools/approval_floors.py`
- `tools/approval_gateway_wait.py`
- `tools/approval_human_wait.py`
- `tools/approval_prompt.py`
- `tools/approval_smart.py`
- `tools/write_approval.py`

### `tools_toolsets`

9 files. Primary slug `tools_toolsets`.

- `tools/ansi_strip.py`
- `tools/arg_coercion.py`
- `tools/registry.py` (also `agent_loop`)
- `tools/schema_sanitizer.py`
- `tools/tool_backend_helpers.py` (also `agent_loop`)
- `tools/tool_labels.py` (also `agent_loop`)
- `tools/tool_output_limits.py` (also `agent_loop`)
- `tools/tool_output_truncate.py` (also `agent_loop`)
- `tools/tool_result_storage.py` (also `agent_loop`)

### `code_execution`

7 files. Primary slug `code_execution`.

- `tools/code_execution_env.py`
- `tools/code_execution_rpc.py`
- `tools/code_execution_tool.py`
- `tools/code_kernel.py`
- `tools/code_kernel_remote.py`
- `tools/daemon_pool.py`
- `tools/interpreter_shutdown.py`

### `web_search`

6 files. Primary slug `web_search`.

- `tools/url_safety.py`
- `tools/web_result_cache.py`
- `tools/web_tools.py`
- `tools/web_tools_extract.py` (also `document_extract`)
- `tools/web_tools_rescue.py`
- `tools/web_tools_truncate.py`

### `checkpoints`

5 files. Primary slug `checkpoints`.

- `tools/checkpoint_maintenance.py`
- `tools/checkpoint_manager.py`
- `tools/checkpoint_manager_profile_rename.py`
- `tools/checkpoint_pruning.py`
- `tools/process_registry_checkpoint.py` (also `file_terminal`)

### `setup_portal`

5 files. Primary slug `setup_portal`.

- `tools/connectors/portal/client.py` (also `tool_gateway`)
- `tools/connectors/portal/errors.py` (also `tool_gateway`)
- `tools/connectors/portal/policy.py` (also `tool_gateway`)
- `tools/connectors/portal/tools_cache.py` (also `tool_gateway`)
- `tools/connectors/portal/wire.py` (also `tool_gateway`)

### `cron`

4 files. Primary slug `cron`.

- `tools/blueprints.py`
- `tools/cronjob_job_args.py`
- `tools/cronjob_prompt_scan.py`
- `tools/cronjob_tools.py`

### `image_gen`

4 files. Primary slug `image_gen`.

- `tools/fal_common.py`
- `tools/image_generation_catalog.py`
- `tools/image_generation_managed.py`
- `tools/image_generation_tool.py`

### `vision`

4 files. Primary slug `vision`.

- `tools/image_source.py`
- `tools/vision_tools.py`
- `tools/vision_tools_history_budget.py`
- `tools/vision_tools_image_prep.py`

### `clarify_todo`

3 files. Primary slug `clarify_todo`.

- `tools/clarify_gateway.py` (also `gateway`)
- `tools/clarify_tool.py`
- `tools/todo_tool.py`

### `kanban`

3 files. Primary slug `kanban`.

- `tools/kanban_tools.py`
- `tools/kanban_tools_schemas.py`
- `tools/kanban_toolset_context.py`

### `provider_routing`

3 files. Primary slug `provider_routing`.

- `tools/budget_config.py`
- `tools/openrouter_client.py`
- `tools/xai_http.py`

### `tool_search`

3 files. Primary slug `tool_search`.

- `tools/tool_search.py` (also `tools_toolsets`)
- `tools/tool_search_catalog.py` (also `tools_toolsets`)
- `tools/tool_search_validation.py` (also `tools_toolsets`)

### `memory`

2 files. Primary slug `memory`.

- `tools/memory_tool.py`
- `tools/memory_tool_store.py`

### `plugins`

2 files. Primary slug `plugins`.

- `tools/plugin_guard.py`
- `tools/plugin_guard_context.py`

### `wake_word`

2 files. Primary slug `wake_word`.

- `tools/wake_word.py` (also `voice_mode`)
- `tools/wake_word_engines.py` (also `voice_mode`)

### `agent_loop`

1 file. Primary slug `agent_loop`.

- `tools/thread_context.py`

### `credential_vault`

1 file. Primary slug `credential_vault`.

- `tools/credential_files.py`

### `document_extract`

1 file. Primary slug `document_extract`.

- `tools/read_extract.py` (also `file_terminal`)

### `home_assistant`

1 file. Primary slug `home_assistant`.

- `tools/homeassistant_tool.py`

### `hooks`

1 file. Primary slug `hooks`.

- `tools/hook_output_spill.py`

### `session_search`

1 file. Primary slug `session_search`.

- `tools/session_search_tool.py`

### `x_search`

1 file. Primary slug `x_search`.

- `tools/x_search_tool.py` (also `web_search`)

### No FEATURES.md slug

In this tree, not packaging, and no slug fits the path name. Shared infrastructure stays here instead of being forced onto a feature.

- `tools/debug_helpers.py`
- `tools/osv_check.py`
- `tools/self_repo_guard.py`
- `tools/spill_safety.py`
- `tools/threat_patterns.py`
- `tools/tirith_security.py`
- `tools/video_generation_tool.py`
- `tools/xai_video_tools.py`

## hermes_cli/

The `hermes` command: setup, model switch, gateway, kanban, dashboard, and the slash surface. Update, backup, and uninstall files are packaging, not features. Leftover command modules are `cli_tui`.

Slugs in this tree: `acp`, `agent_loop`, `approval`, `browser`, `checkpoints`, `cli_tui`, `codex_runtime`, `computer_use`, `context_files`, `credential_pools`, `credential_vault`, `cron`, `curator`, `delegation`, `fallback`, `file_terminal`, `gateway`, `goals`, `heartbeat`, `hooks`, `image_gen`, `kanban`, `kanban_fleet`, `kanban_lanes`, `language_packs`, `loops`, `mcp`, `memory`, `mixture`, `model_switch`, `personality`, `pets`, `platforms`, `plugins`, `prompt_cache`, `provider_routing`, `session_search`, `setup_portal`, `skills`, `skins`, `spotify`, `subscription_proxy`, `terminal_backends`, `tools_toolsets`, `voice_mode`, `web_dashboard`.

Package markers (no slug), 8 files:

- `hermes_cli/__init__.py`
- `hermes_cli/dashboard_auth/__init__.py`
- `hermes_cli/local_runtime/__init__.py`
- `hermes_cli/observability/__init__.py`
- `hermes_cli/proxy/__init__.py`
- `hermes_cli/proxy/adapters/__init__.py`
- `hermes_cli/subcommands/__init__.py`
- `hermes_cli/web_routers/__init__.py`

### `cli_tui`

137 files. Primary slug `cli_tui`.

- `hermes_cli/_early_recovery.py`
- `hermes_cli/_parser.py`
- `hermes_cli/_startup_fast.py`
- `hermes_cli/_subprocess_compat.py`
- `hermes_cli/agent_import.py`
- `hermes_cli/agent_import_sync.py`
- `hermes_cli/archive_safe.py`
- `hermes_cli/banner.py`
- `hermes_cli/callbacks.py`
- `hermes_cli/chat_catalog.py`
- `hermes_cli/claw.py`
- `hermes_cli/cli_auto_maintenance.py`
- `hermes_cli/cli_chat_error_copy.py`
- `hermes_cli/cli_chat_turn_mixin.py`
- `hermes_cli/cli_commands_mixin.py`
- `hermes_cli/cli_config_load.py`
- `hermes_cli/cli_footer_split.py`
- `hermes_cli/cli_info_mixin.py`
- `hermes_cli/cli_output.py`
- `hermes_cli/cli_process_dock.py`
- `hermes_cli/cli_process_notifications.py`
- `hermes_cli/cli_render.py`
- `hermes_cli/cli_session_dock.py`
- `hermes_cli/cli_session_mixin.py`
- `hermes_cli/cli_shutdown.py`
- `hermes_cli/cli_single_query.py`
- `hermes_cli/cli_status_bar_mixin.py`
- `hermes_cli/cli_stream_mixin.py`
- `hermes_cli/cli_tui_mixin.py`
- `hermes_cli/cli_tui_runtime_mixin.py`
- `hermes_cli/cli_unknown_command.py`
- `hermes_cli/clipboard.py`
- `hermes_cli/commands.py`
- `hermes_cli/commands_completion.py`
- `hermes_cli/completion.py`
- `hermes_cli/config.py`
- `hermes_cli/config_backups.py`
- `hermes_cli/config_check_diagnostics.py`
- `hermes_cli/config_defaults.py`
- `hermes_cli/config_effective.py`
- `hermes_cli/config_home.py`
- `hermes_cli/config_migrations.py`
- `hermes_cli/config_read_errors.py`
- `hermes_cli/console_engine.py`
- `hermes_cli/curses_ui.py`
- `hermes_cli/data_cleanup.py`
- `hermes_cli/data_cleanup_holders.py`
- `hermes_cli/debug.py`
- `hermes_cli/diagnostics_upload.py`
- `hermes_cli/doctor.py`
- `hermes_cli/doctor_config.py`
- `hermes_cli/doctor_connectivity.py`
- `hermes_cli/doctor_live.py`
- `hermes_cli/doctor_report.py`
- `hermes_cli/doctor_state.py`
- `hermes_cli/dump.py`
- `hermes_cli/env_loader.py`
- `hermes_cli/focus_view.py`
- `hermes_cli/fs_utils.py`
- `hermes_cli/github_api.py`
- `hermes_cli/gitlock.py`
- `hermes_cli/home_data_layout.py`
- `hermes_cli/input_sanitize.py`
- `hermes_cli/inventory.py`
- `hermes_cli/journey.py`
- `hermes_cli/lifecycle.py`
- `hermes_cli/logs.py`
- `hermes_cli/macos_tcc_anchor.py`
- `hermes_cli/main.py`
- `hermes_cli/main_agent_cmds.py`
- `hermes_cli/main_profile_recovery.py`
- `hermes_cli/main_tui_launch.py`
- `hermes_cli/managed_scope.py`
- `hermes_cli/mem_trim.py`
- `hermes_cli/middleware.py`
- `hermes_cli/migrate.py`
- `hermes_cli/oneshot.py`
- `hermes_cli/process_identity.py`
- `hermes_cli/profile_channels.py`
- `hermes_cli/profile_cmd.py`
- `hermes_cli/profile_describer.py`
- `hermes_cli/profile_distribution.py`
- `hermes_cli/profile_identity.py`
- `hermes_cli/profiles.py`
- `hermes_cli/profiles_service_cleanup.py`
- `hermes_cli/projects_cmd.py`
- `hermes_cli/projects_db.py`
- `hermes_cli/psutil_android.py`
- `hermes_cli/pt_input_extras.py`
- `hermes_cli/quiet_single_query.py`
- `hermes_cli/relaunch.py`
- `hermes_cli/resource_limits.py`
- `hermes_cli/route_identity.py`
- `hermes_cli/runtime_paths.py`
- `hermes_cli/runtime_state.py`
- `hermes_cli/security_advisories.py`
- `hermes_cli/security_audit.py`
- `hermes_cli/security_audit_startup.py`
- `hermes_cli/shared_profile_warning.py`
- `hermes_cli/sizefmt.py`
- `hermes_cli/slash_exec.py`
- `hermes_cli/sqlite_runtime.py`
- `hermes_cli/sqlite_safe_read.py`
- `hermes_cli/sqlite_util.py`
- `hermes_cli/status.py`
- `hermes_cli/status_auth.py`
- `hermes_cli/status_bar_git.py`
- `hermes_cli/status_report.py`
- `hermes_cli/stderr_timestamp.py`
- `hermes_cli/stdio.py`
- `hermes_cli/steward.py`
- `hermes_cli/stream_json.py`
- `hermes_cli/subcommands/_shared.py`
- `hermes_cli/subcommands/claw.py`
- `hermes_cli/subcommands/completion.py`
- `hermes_cli/subcommands/config.py`
- `hermes_cli/subcommands/console.py`
- `hermes_cli/subcommands/debug.py`
- `hermes_cli/subcommands/doctor.py`
- `hermes_cli/subcommands/dump.py`
- `hermes_cli/subcommands/import_agent.py`
- `hermes_cli/subcommands/import_cmd.py`
- `hermes_cli/subcommands/journey.py`
- `hermes_cli/subcommands/logs.py`
- `hermes_cli/subcommands/migrate.py`
- `hermes_cli/subcommands/profile.py`
- `hermes_cli/subcommands/security.py`
- `hermes_cli/subcommands/status.py`
- `hermes_cli/subcommands/sync.py`
- `hermes_cli/suggestions_cmd.py`
- `hermes_cli/terminal_breadcrumbs.py`
- `hermes_cli/terminal_notify.py`
- `hermes_cli/timefmt.py`
- `hermes_cli/timeouts.py`
- `hermes_cli/tips.py`
- `hermes_cli/urllib_security.py`
- `hermes_cli/verify_cmd.py`

### `web_dashboard`

63 files. Primary slug `web_dashboard`.

- `hermes_cli/dashboard_auth/audit.py`
- `hermes_cli/dashboard_auth/base.py`
- `hermes_cli/dashboard_auth/cookies.py`
- `hermes_cli/dashboard_auth/login_page.py`
- `hermes_cli/dashboard_auth/middleware.py`
- `hermes_cli/dashboard_auth/native_flow.py`
- `hermes_cli/dashboard_auth/prefix.py`
- `hermes_cli/dashboard_auth/public_paths.py`
- `hermes_cli/dashboard_auth/refresh_singleflight.py`
- `hermes_cli/dashboard_auth/registry.py`
- `hermes_cli/dashboard_auth/request_utils.py`
- `hermes_cli/dashboard_auth/routes.py`
- `hermes_cli/dashboard_auth/token_auth.py`
- `hermes_cli/dashboard_auth/ws_tickets.py`
- `hermes_cli/dashboard_procs.py`
- `hermes_cli/dashboard_register.py`
- `hermes_cli/main_dashboard.py`
- `hermes_cli/subcommands/dashboard.py`
- `hermes_cli/web_models.py` (also `model_switch`)
- `hermes_cli/web_read_coalescing.py`
- `hermes_cli/web_routers/_common.py`
- `hermes_cli/web_routers/actions.py`
- `hermes_cli/web_routers/analytics.py`
- `hermes_cli/web_routers/audio.py`
- `hermes_cli/web_routers/chat_workspaces.py`
- `hermes_cli/web_routers/chat_ws.py`
- `hermes_cli/web_routers/chat_ws_errors.py`
- `hermes_cli/web_routers/config_env.py`
- `hermes_cli/web_routers/cron.py` (also `cron`)
- `hermes_cli/web_routers/dashboard_ui.py`
- `hermes_cli/web_routers/display.py`
- `hermes_cli/web_routers/files.py`
- `hermes_cli/web_routers/git.py`
- `hermes_cli/web_routers/local_models.py` (also `model_switch`)
- `hermes_cli/web_routers/mcp.py` (also `mcp`)
- `hermes_cli/web_routers/memory_providers.py` (also `memory`)
- `hermes_cli/web_routers/messaging.py`
- `hermes_cli/web_routers/models.py` (also `model_switch`)
- `hermes_cli/web_routers/oauth.py`
- `hermes_cli/web_routers/ops.py`
- `hermes_cli/web_routers/profiles.py`
- `hermes_cli/web_routers/sessions.py`
- `hermes_cli/web_routers/shared_metrics.py`
- `hermes_cli/web_routers/skills.py` (also `skills`)
- `hermes_cli/web_routers/status.py`
- `hermes_cli/web_routers/tools.py`
- `hermes_cli/web_server.py`
- `hermes_cli/web_server_chat.py`
- `hermes_cli/web_server_config.py`
- `hermes_cli/web_server_cron.py` (also `cron`)
- `hermes_cli/web_server_dashboard.py`
- `hermes_cli/web_server_files.py`
- `hermes_cli/web_server_gateway.py` (also `gateway`)
- `hermes_cli/web_server_idle_exit.py`
- `hermes_cli/web_server_idle_proof.py`
- `hermes_cli/web_server_lifecycle.py`
- `hermes_cli/web_server_mcp.py` (also `mcp`)
- `hermes_cli/web_server_memory.py` (also `memory`)
- `hermes_cli/web_server_messaging.py`
- `hermes_cli/web_server_oauth.py`
- `hermes_cli/web_server_profiles.py`
- `hermes_cli/web_server_sessions.py`
- `hermes_cli/web_server_skew_exit.py`

### `model_switch`

41 files. Primary slug `model_switch`.

- `hermes_cli/cli_model_switch_mixin.py` (also `provider_routing`)
- `hermes_cli/codex_models.py` (also `codex_runtime`)
- `hermes_cli/local_runtime/binaries.py` (also `provider_routing`)
- `hermes_cli/local_runtime/bootstrap.py` (also `provider_routing`)
- `hermes_cli/local_runtime/capabilities.py` (also `provider_routing`)
- `hermes_cli/local_runtime/catalog.py` (also `provider_routing`)
- `hermes_cli/local_runtime/context_policy.py` (also `provider_routing`)
- `hermes_cli/local_runtime/detect.py` (also `provider_routing`)
- `hermes_cli/local_runtime/endpoint.py` (also `provider_routing`)
- `hermes_cli/local_runtime/estimator.py` (also `provider_routing`)
- `hermes_cli/local_runtime/gguf.py` (also `provider_routing`)
- `hermes_cli/local_runtime/growth.py` (also `provider_routing`)
- `hermes_cli/local_runtime/hardware.py` (also `provider_routing`)
- `hermes_cli/local_runtime/hf_browse.py` (also `provider_routing`)
- `hermes_cli/local_runtime/load_progress.py` (also `provider_routing`)
- `hermes_cli/local_runtime/presets.py` (also `provider_routing`)
- `hermes_cli/local_runtime/processes.py` (also `provider_routing`)
- `hermes_cli/local_runtime/recovery.py` (also `provider_routing`)
- `hermes_cli/local_runtime/supervisor.py` (also `provider_routing`)
- `hermes_cli/model_catalog.py` (also `provider_routing`)
- `hermes_cli/model_cost_guard.py` (also `provider_routing`)
- `hermes_cli/model_data_policy_guard.py` (also `provider_routing`)
- `hermes_cli/model_normalize.py` (also `provider_routing`)
- `hermes_cli/model_search.py` (also `provider_routing`)
- `hermes_cli/model_selection_guards.py` (also `provider_routing`)
- `hermes_cli/model_setup_flows.py` (also `provider_routing`)
- `hermes_cli/model_setup_flows_azure.py` (also `provider_routing`)
- `hermes_cli/model_setup_flows_bedrock.py` (also `provider_routing`)
- `hermes_cli/model_setup_flows_common.py` (also `provider_routing`)
- `hermes_cli/model_setup_flows_custom.py` (also `provider_routing`)
- `hermes_cli/model_switch.py` (also `provider_routing`)
- `hermes_cli/model_switch_providers.py` (also `provider_routing`)
- `hermes_cli/models.py` (also `provider_routing`)
- `hermes_cli/models_catalog_static.py` (also `provider_routing`)
- `hermes_cli/models_detect.py` (also `provider_routing`)
- `hermes_cli/models_local.py` (also `provider_routing`)
- `hermes_cli/models_pricing.py` (also `provider_routing`)
- `hermes_cli/models_profile_cache.py` (also `provider_routing`)
- `hermes_cli/models_reasoning_caps.py` (also `provider_routing`)
- `hermes_cli/models_validate.py` (also `provider_routing`)
- `hermes_cli/subcommands/model.py` (also `provider_routing`)

### `plugins`

37 files. Primary slug `plugins`.

- `hermes_cli/agent_plugins.py`
- `hermes_cli/plugin_capabilities.py`
- `hermes_cli/plugin_catalog.py`
- `hermes_cli/plugin_catalog_presence.py`
- `hermes_cli/plugin_compat.py`
- `hermes_cli/plugin_dev.py`
- `hermes_cli/plugin_events.py`
- `hermes_cli/plugin_packs.py`
- `hermes_cli/plugin_validate.py`
- `hermes_cli/plugin_validate_desktop.py`
- `hermes_cli/plugins.py`
- `hermes_cli/plugins_activation.py`
- `hermes_cli/plugins_activation_live.py`
- `hermes_cli/plugins_admission.py`
- `hermes_cli/plugins_cadence.py`
- `hermes_cli/plugins_cmd.py`
- `hermes_cli/plugins_cmd_capabilities.py`
- `hermes_cli/plugins_cmd_catalog.py`
- `hermes_cli/plugins_cmd_git.py`
- `hermes_cli/plugins_cmd_install.py`
- `hermes_cli/plugins_cmd_listing.py`
- `hermes_cli/plugins_cmd_remove.py`
- `hermes_cli/plugins_cmd_toggle.py`
- `hermes_cli/plugins_cmd_update.py`
- `hermes_cli/plugins_discovery.py`
- `hermes_cli/plugins_dispatch.py`
- `hermes_cli/plugins_ledger.py`
- `hermes_cli/plugins_loader.py`
- `hermes_cli/plugins_manifest.py`
- `hermes_cli/plugins_provenance.py`
- `hermes_cli/plugins_settings.py`
- `hermes_cli/plugins_state.py`
- `hermes_cli/plugins_transaction.py`
- `hermes_cli/plugins_updates.py`
- `hermes_cli/relay_plugin_cutover.py`
- `hermes_cli/relay_plugin_migrate.py`
- `hermes_cli/subcommands/plugins.py`

### `credential_pools`

30 files. Primary slug `credential_pools`.

- `hermes_cli/anon_auth.py` (also `provider_routing`)
- `hermes_cli/anon_sign_in.py` (also `provider_routing`)
- `hermes_cli/anon_sign_in_cli.py` (also `provider_routing`)
- `hermes_cli/auth.py` (also `provider_routing`)
- `hermes_cli/auth_codex.py` (also `provider_routing`)
- `hermes_cli/auth_codex_browser.py` (also `provider_routing`)
- `hermes_cli/auth_commands.py` (also `provider_routing`)
- `hermes_cli/auth_constants.py` (also `provider_routing`)
- `hermes_cli/auth_device_flow.py` (also `provider_routing`)
- `hermes_cli/auth_error_copy.py` (also `provider_routing`)
- `hermes_cli/auth_minimax.py` (also `provider_routing`)
- `hermes_cli/auth_model_picker.py` (also `provider_routing`)
- `hermes_cli/auth_nous.py` (also `provider_routing`)
- `hermes_cli/auth_oauth_grants.py` (also `provider_routing`)
- `hermes_cli/auth_oauth_pkce_plugin.py` (also `provider_routing`)
- `hermes_cli/auth_openrouter.py` (also `provider_routing`)
- `hermes_cli/auth_plugin_providers.py` (also `provider_routing`)
- `hermes_cli/auth_qwen.py` (also `provider_routing`)
- `hermes_cli/auth_xai.py` (also `provider_routing`)
- `hermes_cli/auth_zai_kimi.py` (also `provider_routing`)
- `hermes_cli/copilot_auth.py` (also `provider_routing`)
- `hermes_cli/credential_lifecycle.py` (also `provider_routing`)
- `hermes_cli/nous_account.py` (also `provider_routing`)
- `hermes_cli/nous_auth_keepalive.py` (also `provider_routing`)
- `hermes_cli/nous_billing.py` (also `provider_routing`)
- `hermes_cli/nous_subscription.py` (also `provider_routing`)
- `hermes_cli/subcommands/auth.py` (also `provider_routing`)
- `hermes_cli/subcommands/login.py`
- `hermes_cli/subcommands/logout.py`
- `hermes_cli/vercel_auth.py` (also `terminal_backends`)

### `gateway`

24 files. Primary slug `gateway`.

- `hermes_cli/commands_platforms.py` (also `platforms`)
- `hermes_cli/dingtalk_auth.py` (also `platforms`)
- `hermes_cli/gateway.py`
- `hermes_cli/gateway_command_errors.py`
- `hermes_cli/gateway_enroll.py`
- `hermes_cli/gateway_launchd.py`
- `hermes_cli/gateway_migrate.py`
- `hermes_cli/gateway_migrate_guards.py`
- `hermes_cli/gateway_profile_lifecycle.py`
- `hermes_cli/gateway_setup_wizard.py`
- `hermes_cli/gateway_supervised_restart.py`
- `hermes_cli/gateway_windows.py`
- `hermes_cli/gateway_windows_legacy.py`
- `hermes_cli/main_platform_setup.py` (also `platforms`)
- `hermes_cli/pairing.py` (also `platforms`)
- `hermes_cli/platforms.py` (also `platforms`)
- `hermes_cli/service_manager.py`
- `hermes_cli/setup_platforms.py` (also `platforms`)
- `hermes_cli/setup_whatsapp_cloud.py` (also `platforms`)
- `hermes_cli/slack_cli.py` (also `platforms`)
- `hermes_cli/subcommands/gateway.py`
- `hermes_cli/subcommands/pause.py`
- `hermes_cli/subcommands/peer.py`
- `hermes_cli/telegram_managed_bot.py` (also `platforms`)

### `session_search`

20 files. Primary slug `session_search`.

- `hermes_cli/active_sessions.py` (also `cli_tui`)
- `hermes_cli/foreign_sessions.py` (also `cli_tui`)
- `hermes_cli/foreign_sessions_browser.py` (also `cli_tui`)
- `hermes_cli/session_export.py` (also `cli_tui`)
- `hermes_cli/session_export_html.py` (also `cli_tui`)
- `hermes_cli/session_export_md.py` (also `cli_tui`)
- `hermes_cli/session_filters.py` (also `cli_tui`)
- `hermes_cli/session_listing.py` (also `cli_tui`)
- `hermes_cli/session_lost_and_found.py` (also `cli_tui`)
- `hermes_cli/session_recap.py` (also `cli_tui`)
- `hermes_cli/session_recovery.py` (also `cli_tui`)
- `hermes_cli/session_reset_retirement.py` (also `cli_tui`)
- `hermes_cli/session_schema_history.py` (also `cli_tui`)
- `hermes_cli/sessions_cmd.py` (also `cli_tui`)
- `hermes_cli/sessions_cmd_browse.py` (also `cli_tui`)
- `hermes_cli/sessions_cmd_journal_mode.py` (also `cli_tui`)
- `hermes_cli/sessions_cmd_repair_profiles.py` (also `cli_tui`)
- `hermes_cli/sessions_repair_profiles.py` (also `cli_tui`)
- `hermes_cli/shared_session_attach.py` (also `cli_tui`)
- `hermes_cli/subcommands/sessions.py` (also `cli_tui`)

### `kanban`

16 files. Primary slug `kanban`.

- `hermes_cli/kanban.py`
- `hermes_cli/kanban_boards.py`
- `hermes_cli/kanban_db.py`
- `hermes_cli/kanban_db_connect.py`
- `hermes_cli/kanban_db_graph.py`
- `hermes_cli/kanban_db_notify.py`
- `hermes_cli/kanban_db_workspace.py`
- `hermes_cli/kanban_decompose.py`
- `hermes_cli/kanban_diagnostics.py`
- `hermes_cli/kanban_ops.py`
- `hermes_cli/kanban_output.py`
- `hermes_cli/kanban_parser.py`
- `hermes_cli/kanban_pr_acceptance.py`
- `hermes_cli/kanban_pr_acceptance_store.py`
- `hermes_cli/kanban_specify.py`
- `hermes_cli/kanban_transfer.py`

### `setup_portal`

15 files. Primary slug `setup_portal`.

- `hermes_cli/cli_agent_setup_mixin.py` (also `cli_tui`)
- `hermes_cli/cli_init_mixin.py` (also `cli_tui`)
- `hermes_cli/free_tier_bootstrap.py`
- `hermes_cli/init_command.py`
- `hermes_cli/main_provider_setup.py` (also `provider_routing`)
- `hermes_cli/portal_cli.py`
- `hermes_cli/setup.py`
- `hermes_cli/setup_hidden_env.py`
- `hermes_cli/setup_migration.py`
- `hermes_cli/setup_profile.py`
- `hermes_cli/setup_quick.py`
- `hermes_cli/setup_summary.py`
- `hermes_cli/setup_terminal.py` (also `terminal_backends`)
- `hermes_cli/setup_tts.py` (also `tts`)
- `hermes_cli/subcommands/setup.py`

### `provider_routing`

12 files. Primary slug `provider_routing`.

- `hermes_cli/azure_detect.py`
- `hermes_cli/backend_retirement.py`
- `hermes_cli/cli_billing_mixin.py` (also `cli_tui`)
- `hermes_cli/config_env_routing.py` (also `model_switch`)
- `hermes_cli/config_providers.py` (also `model_switch`)
- `hermes_cli/provider_catalog.py` (also `model_switch`)
- `hermes_cli/providers.py` (also `model_switch`)
- `hermes_cli/runtime_provider.py` (also `model_switch`)
- `hermes_cli/runtime_provider_backends.py` (also `model_switch`)
- `hermes_cli/runtime_provider_custom.py` (also `model_switch`)
- `hermes_cli/subcommands/usage.py`
- `hermes_cli/xai_retirement.py`

### `tools_toolsets`

9 files. Primary slug `tools_toolsets`.

- `hermes_cli/doctor_tools.py` (also `cli_tui`)
- `hermes_cli/subcommands/tools.py`
- `hermes_cli/tool_availability_notices.py`
- `hermes_cli/tools_config.py`
- `hermes_cli/tools_config_cua.py` (also `computer_use`)
- `hermes_cli/tools_config_post_setup.py`
- `hermes_cli/tools_config_providers.py` (also `provider_routing`)
- `hermes_cli/toolset_scope.py`
- `hermes_cli/toolset_validation.py`

### `credential_vault`

8 files. Primary slug `credential_vault`.

- `hermes_cli/_secrets_common.py`
- `hermes_cli/git_credentials.py`
- `hermes_cli/onepassword_secrets_cli.py`
- `hermes_cli/secret_prompt.py`
- `hermes_cli/secrets_cli.py`
- `hermes_cli/subcommands/secrets.py`
- `hermes_cli/subcommands/vault.py`
- `hermes_cli/vault.py`

### `file_terminal`

8 files. Primary slug `file_terminal`.

- `hermes_cli/bang_shell.py` (also `terminal_backends`, `cli_tui`)
- `hermes_cli/cli_terminal_input.py` (also `terminal_backends`, `cli_tui`)
- `hermes_cli/cli_terminal_mixin.py` (also `terminal_backends`, `cli_tui`)
- `hermes_cli/pty_bridge.py` (also `terminal_backends`, `cli_tui`)
- `hermes_cli/pty_session.py` (also `terminal_backends`, `cli_tui`)
- `hermes_cli/ssh_workspace_fs.py` (also `terminal_backends`, `cli_tui`)
- `hermes_cli/win_pty_bridge.py` (also `terminal_backends`, `cli_tui`)
- `hermes_cli/windows_ssh_runtime.py` (also `terminal_backends`, `cli_tui`)

### `mcp`

8 files. Primary slug `mcp`.

- `hermes_cli/mcp_app_detection.py`
- `hermes_cli/mcp_catalog.py`
- `hermes_cli/mcp_config.py`
- `hermes_cli/mcp_picker.py`
- `hermes_cli/mcp_security.py`
- `hermes_cli/mcp_startup.py`
- `hermes_cli/subcommands/mcp.py`
- `hermes_cli/tools_config_mcp.py`

### `platforms`

8 files. Primary slug `platforms`.

- `hermes_cli/doctor_platform.py` (also `cli_tui`)
- `hermes_cli/platform_actions.py` (also `gateway`)
- `hermes_cli/send_cmd.py` (also `gateway`)
- `hermes_cli/subcommands/pairing.py` (also `gateway`)
- `hermes_cli/subcommands/slack.py`
- `hermes_cli/subcommands/webhook.py` (also `gateway`)
- `hermes_cli/subcommands/whatsapp.py`
- `hermes_cli/webhook.py` (also `gateway`)

### `subscription_proxy`

7 files. Primary slug `subscription_proxy`.

- `hermes_cli/proxy/adapters/base.py`
- `hermes_cli/proxy/adapters/nous_portal.py`
- `hermes_cli/proxy/adapters/xai.py`
- `hermes_cli/proxy/cli.py`
- `hermes_cli/proxy/server.py`
- `hermes_cli/proxy/sse_done.py`
- `hermes_cli/proxy_cli.py`

### `approval`

6 files. Primary slug `approval`.

- `hermes_cli/approval_mode.py`
- `hermes_cli/approval_transport.py`
- `hermes_cli/approvals_suggest.py`
- `hermes_cli/approvals_test.py`
- `hermes_cli/subcommands/approvals.py`
- `hermes_cli/write_approval_commands.py`

### `delegation`

5 files. Primary slug `delegation`.

- `hermes_cli/cli_subagent_monitor.py` (also `cli_tui`)
- `hermes_cli/subcommands/worktree.py` (also `file_terminal`)
- `hermes_cli/worktree_cmd.py` (also `file_terminal`)
- `hermes_cli/worktree_gc.py` (also `file_terminal`)
- `hermes_cli/worktree_ops.py` (also `file_terminal`)

### `memory`

5 files. Primary slug `memory`.

- `hermes_cli/memory_oauth.py`
- `hermes_cli/memory_provider_migration.py` (also `memory_providers`)
- `hermes_cli/memory_setup.py`
- `hermes_cli/profile_memory_config.py`
- `hermes_cli/subcommands/memory.py`

### `skins`

4 files. Primary slug `skins`.

- `hermes_cli/colors.py` (also `cli_tui`)
- `hermes_cli/skin_cmd.py` (also `cli_tui`)
- `hermes_cli/skin_engine.py` (also `cli_tui`)
- `hermes_cli/subcommands/skin.py` (also `cli_tui`)

### `agent_loop`

3 files. Primary slug `agent_loop`.

- `hermes_cli/partial_compress.py`
- `hermes_cli/prompt_size.py` (also `prompt_cache`)
- `hermes_cli/subcommands/prompt_size.py` (also `prompt_cache`)

### `browser`

3 files. Primary slug `browser`.

- `hermes_cli/browser_connect.py`
- `hermes_cli/browser_runtime.py`
- `hermes_cli/subcommands/browser.py`

### `codex_runtime`

3 files. Primary slug `codex_runtime`.

- `hermes_cli/codex_runtime_plugin_migration.py`
- `hermes_cli/codex_runtime_switch.py`
- `hermes_cli/subcommands/codex_runtime.py`

### `cron`

3 files. Primary slug `cron`.

- `hermes_cli/blueprint_cmd.py` (also `cli_tui`)
- `hermes_cli/cron.py`
- `hermes_cli/subcommands/cron.py`

### `fallback`

3 files. Primary slug `fallback`.

- `hermes_cli/fallback_cmd.py` (also `provider_routing`)
- `hermes_cli/fallback_config.py` (also `provider_routing`)
- `hermes_cli/subcommands/fallback.py` (also `provider_routing`)

### `kanban_fleet`

3 files. Primary slug `kanban_fleet`.

- `hermes_cli/gateway_multiplex_mode.py` (also `gateway`)
- `hermes_cli/gateway_multiplex_s6.py` (also `gateway`)
- `hermes_cli/gateway_multiplex_served.py` (also `gateway`)

### `mixture`

3 files. Primary slug `mixture`.

- `hermes_cli/moa_cmd.py`
- `hermes_cli/moa_config.py`
- `hermes_cli/subcommands/moa.py`

### `skills`

3 files. Primary slug `skills`.

- `hermes_cli/skills_config.py`
- `hermes_cli/skills_hub.py`
- `hermes_cli/subcommands/skills.py`

### `terminal_backends`

3 files. Primary slug `terminal_backends`.

- `hermes_cli/cli_modal_mixin.py` (also `cli_tui`)
- `hermes_cli/sandbox_image_switch.py` (also `code_execution`)
- `hermes_cli/subcommands/egress.py` (also `cli_tui`)

### `checkpoints`

2 files. Primary slug `checkpoints`.

- `hermes_cli/checkpoints.py`
- `hermes_cli/subcommands/checkpoints.py`

### `computer_use`

2 files. Primary slug `computer_use`.

- `hermes_cli/subcommands/computer_use.py`
- `hermes_cli/subcommands/computer_use_screen.py`

### `curator`

2 files. Primary slug `curator`.

- `hermes_cli/curator.py` (also `memory`)
- `hermes_cli/subcommands/curator.py` (also `memory`)

### `goals`

2 files. Primary slug `goals`.

- `hermes_cli/goal_command.py`
- `hermes_cli/goals.py`

### `hooks`

2 files. Primary slug `hooks`.

- `hermes_cli/hooks.py`
- `hermes_cli/subcommands/hooks.py`

### `kanban_lanes`

2 files. Primary slug `kanban_lanes`.

- `hermes_cli/kanban_db_dispatch.py` (also `kanban`)
- `hermes_cli/kanban_swarm.py` (also `kanban`)

### `language_packs`

2 files. Primary slug `language_packs`.

- `hermes_cli/config_language.py`
- `hermes_cli/plugin_validate_locales.py` (also `plugins`)

### `loops`

2 files. Primary slug `loops`.

- `hermes_cli/cli_loops_mixin.py` (also `agent_loop`)
- `hermes_cli/loops.py` (also `agent_loop`)

### `personality`

2 files. Primary slug `personality`.

- `hermes_cli/default_soul.py`
- `hermes_cli/personality.py`

### `pets`

2 files. Primary slug `pets`.

- `hermes_cli/pets.py`
- `hermes_cli/subcommands/pets.py`

### `voice_mode`

2 files. Primary slug `voice_mode`.

- `hermes_cli/cli_voice_mixin.py` (also `tts`)
- `hermes_cli/voice.py` (also `tts`)

### `acp`

1 file. Primary slug `acp`.

- `hermes_cli/subcommands/acp.py`

### `context_files`

1 file. Primary slug `context_files`.

- `hermes_cli/context_switch_guard.py` (also `cli_tui`)

### `heartbeat`

1 file. Primary slug `heartbeat`.

- `hermes_cli/heartbeat.py`

### `image_gen`

1 file. Primary slug `image_gen`.

- `hermes_cli/image_provenance.py` (also `vision`)

### `prompt_cache`

1 file. Primary slug `prompt_cache`.

- `hermes_cli/prompt_stash.py` (also `agent_loop`)

### `spotify`

1 file. Primary slug `spotify`.

- `hermes_cli/auth_spotify.py` (also `credential_pools`)

### No FEATURES.md slug

In this tree, not packaging, and no slug fits the path name. Shared infrastructure stays here instead of being forced onto a feature.

- `hermes_cli/observability/relay_shared_metrics.py`
- `hermes_cli/observability/shared_metrics.py`
- `hermes_cli/observability/shared_metrics_catalog.py`
- `hermes_cli/observability/shared_metrics_consent.py`
- `hermes_cli/observability/shared_metrics_contract.py`
- `hermes_cli/observability/shared_metrics_desktop.py`
- `hermes_cli/observability/shared_metrics_disabled.py`
- `hermes_cli/observability/shared_metrics_efficiency.py`
- `hermes_cli/observability/shared_metrics_engagement.py`
- `hermes_cli/observability/shared_metrics_events.py`
- `hermes_cli/observability/shared_metrics_fields.py`
- `hermes_cli/observability/shared_metrics_gateway.py`
- `hermes_cli/observability/shared_metrics_harness.py`
- `hermes_cli/observability/shared_metrics_install.py`
- `hermes_cli/observability/shared_metrics_loop.py`
- `hermes_cli/observability/shared_metrics_model.py`
- `hermes_cli/observability/shared_metrics_process.py`
- `hermes_cli/observability/shared_metrics_send_config.py`
- `hermes_cli/observability/shared_metrics_sender.py`
- `hermes_cli/observability/shared_metrics_setup.py`
- `hermes_cli/observability/shared_metrics_signals.py`
- `hermes_cli/observability/shared_metrics_snapshot.py`
- `hermes_cli/observability/shared_metrics_startup.py`
- `hermes_cli/observability/shared_metrics_subscriber.py`
- `hermes_cli/observability/shared_metrics_update.py`
- `hermes_cli/subcommands/insights.py`
- `hermes_cli/subcommands/monitoring.py`
- `hermes_cli/subcommands/verify.py`

## gateway/

One process for ingest, delivery, and status. Built-in adapters are `gateway/platforms/`. Most chat adapters are `plugins/platforms/`. `gateway/wake.py` is ingest wake, not the wake-word detector.

Slugs in this tree: `api_server`, `approval`, `browser`, `clarify_todo`, `cli_tui`, `gateway`, `goals`, `heartbeat`, `hooks`, `kanban`, `kanban_fleet`, `kanban_lanes`, `memory`, `model_switch`, `platforms`, `tts`, `voice_mode`.

Package markers (no slug), 5 files:

- `gateway/__init__.py`
- `gateway/builtin_hooks/__init__.py`
- `gateway/platforms/__init__.py`
- `gateway/platforms/qqbot/__init__.py`
- `gateway/relay/__init__.py`

### `gateway`

105 files. Primary slug `gateway`.

- `gateway/agent_cache_pressure.py`
- `gateway/authz_mixin.py`
- `gateway/bot_loop_guard.py`
- `gateway/cgroup_cleanup.py`
- `gateway/channel_directory.py`
- `gateway/code_skew.py`
- `gateway/config.py`
- `gateway/config_env.py`
- `gateway/config_loader.py`
- `gateway/control_socket.py`
- `gateway/cwd_placeholder.py`
- `gateway/dead_targets.py`
- `gateway/delivery.py`
- `gateway/delivery_ledger.py`
- `gateway/disk_status.py`
- `gateway/display_config.py`
- `gateway/drain_control.py`
- `gateway/host_attach.py`
- `gateway/host_rendezvous.py`
- `gateway/host_topology.py`
- `gateway/hosted_room_discussion.py`
- `gateway/hosted_room_driver.py`
- `gateway/hosted_room_execution_policy.py`
- `gateway/hosted_room_links.py`
- `gateway/hosted_room_peer.py`
- `gateway/hosted_room_policy_checkpoint.py`
- `gateway/hosted_room_replicas.py`
- `gateway/hosted_rooms.py`
- `gateway/hosted_rooms_common.py`
- `gateway/hosted_rooms_legacy_import.py`
- `gateway/lifecycle_ledger.py`
- `gateway/media_fetch.py`
- `gateway/media_policy.py`
- `gateway/media_repair.py`
- `gateway/message_timestamps.py`
- `gateway/mirror.py`
- `gateway/pairing.py`
- `gateway/platform_registry.py`
- `gateway/profile_routing.py`
- `gateway/readiness.py`
- `gateway/relay/adapter.py`
- `gateway/relay/auth.py`
- `gateway/relay/command_manifest.py`
- `gateway/relay/descriptor.py`
- `gateway/relay/egress.py`
- `gateway/relay/media.py`
- `gateway/relay/transport.py`
- `gateway/relay/ws_transport.py`
- `gateway/response_filters.py`
- `gateway/restart.py`
- `gateway/restart_loop_guard.py`
- `gateway/rich_sent_store.py`
- `gateway/run.py`
- `gateway/run_adapters.py`
- `gateway/run_agent_cache.py`
- `gateway/run_busy.py`
- `gateway/run_common.py`
- `gateway/run_config_loaders.py`
- `gateway/run_delivery_queue_watch.py`
- `gateway/run_idle_gates.py`
- `gateway/run_inbound.py`
- `gateway/run_inbound_unauthorized.py`
- `gateway/run_notifications.py`
- `gateway/run_plugin_rewire.py`
- `gateway/run_profile_reconcile.py`
- `gateway/run_shutdown.py`
- `gateway/run_startup.py`
- `gateway/run_topics.py`
- `gateway/run_turn.py`
- `gateway/run_turn_followup_ack.py`
- `gateway/run_turn_runner.py`
- `gateway/run_watchers.py`
- `gateway/runtime_footer.py`
- `gateway/scale_to_zero.py`
- `gateway/session.py`
- `gateway/session_context.py`
- `gateway/session_db_recovery.py`
- `gateway/session_identity.py`
- `gateway/session_lifecycle.py`
- `gateway/session_persistence.py`
- `gateway/session_prompt_pin.py`
- `gateway/session_recovery.py`
- `gateway/session_stall.py`
- `gateway/session_state.py`
- `gateway/session_transcript.py`
- `gateway/shutdown_flush.py`
- `gateway/shutdown_forensics.py`
- `gateway/shutdown_watchdog.py`
- `gateway/status.py`
- `gateway/status_phrases.py`
- `gateway/sticker_cache.py`
- `gateway/stream_consumer.py`
- `gateway/stream_consumer_fallback.py`
- `gateway/stream_consumer_think.py`
- `gateway/stream_consumer_transport.py`
- `gateway/stream_dispatch.py`
- `gateway/stream_events.py`
- `gateway/systemd_notify.py`
- `gateway/systemd_stop_mark.py`
- `gateway/turn_context.py`
- `gateway/turn_executor.py`
- `gateway/turn_lease.py`
- `gateway/wake.py`
- `gateway/warning_notifications.py`
- `gateway/whatsapp_identity.py`

### `platforms`

32 files. Primary slug `platforms`.

- `gateway/platforms/_http_client_limits.py` (also `gateway`)
- `gateway/platforms/_shared.py` (also `gateway`)
- `gateway/platforms/access_policy_mixin.py` (also `gateway`)
- `gateway/platforms/base.py` (also `gateway`)
- `gateway/platforms/base_exec_approval.py` (also `gateway`)
- `gateway/platforms/bluebubbles.py` (also `gateway`)
- `gateway/platforms/event.py` (also `gateway`)
- `gateway/platforms/helpers.py` (also `gateway`)
- `gateway/platforms/media_cache.py` (also `gateway`)
- `gateway/platforms/msgraph_webhook.py` (also `gateway`)
- `gateway/platforms/qqbot/adapter.py` (also `gateway`)
- `gateway/platforms/qqbot/chunked_upload.py` (also `gateway`)
- `gateway/platforms/qqbot/constants.py` (also `gateway`)
- `gateway/platforms/qqbot/crypto.py` (also `gateway`)
- `gateway/platforms/qqbot/keyboards.py` (also `gateway`)
- `gateway/platforms/qqbot/onboard.py` (also `gateway`)
- `gateway/platforms/qqbot/utils.py` (also `gateway`)
- `gateway/platforms/shared_ingress.py` (also `gateway`)
- `gateway/platforms/signal.py` (also `gateway`)
- `gateway/platforms/signal_format.py` (also `gateway`)
- `gateway/platforms/signal_rate_limit.py` (also `gateway`)
- `gateway/platforms/tcp_site.py` (also `gateway`)
- `gateway/platforms/webhook.py` (also `gateway`)
- `gateway/platforms/webhook_coalesce.py` (also `gateway`)
- `gateway/platforms/webhook_filters.py` (also `gateway`)
- `gateway/platforms/weixin.py` (also `gateway`)
- `gateway/platforms/whatsapp_cloud.py` (also `gateway`)
- `gateway/platforms/whatsapp_common.py` (also `gateway`)
- `gateway/platforms/yuanbao.py` (also `gateway`)
- `gateway/platforms/yuanbao_media.py` (also `gateway`)
- `gateway/platforms/yuanbao_proto.py` (also `gateway`)
- `gateway/platforms/yuanbao_sticker.py` (also `gateway`)

### `api_server`

8 files. Primary slug `api_server`.

- `gateway/platforms/api_server.py` (also `gateway`)
- `gateway/platforms/api_server_memory_sessions.py` (also `gateway`)
- `gateway/platforms/api_server_openai_routes.py` (also `gateway`)
- `gateway/platforms/api_server_room_dispatch.py` (also `gateway`)
- `gateway/platforms/api_server_room_grants.py` (also `gateway`)
- `gateway/platforms/api_server_run_idempotency.py` (also `gateway`)
- `gateway/platforms/api_server_runs.py` (also `gateway`)
- `gateway/platforms/api_server_turn_boundary.py` (also `gateway`)

### `cli_tui`

6 files. Primary slug `cli_tui`.

- `gateway/slash_access.py` (also `gateway`)
- `gateway/slash_commands.py` (also `gateway`)
- `gateway/slash_commands_branch_thread.py` (also `gateway`)
- `gateway/slash_commands_login.py` (also `gateway`)
- `gateway/slash_commands_session.py` (also `gateway`)
- `gateway/slash_commands_status.py` (also `gateway`)

### `kanban`

3 files. Primary slug `kanban`.

- `gateway/kanban_watchers.py` (also `gateway`)
- `gateway/kanban_watchers_common.py` (also `gateway`)
- `gateway/kanban_watchers_notifier.py` (also `gateway`)

### `browser`

2 files. Primary slug `browser`.

- `gateway/browser_control_artifacts.py` (also `gateway`)
- `gateway/browser_control_broker.py` (also `gateway`)

### `goals`

2 files. Primary slug `goals`.

- `gateway/run_goals.py` (also `gateway`)
- `gateway/slash_commands_goals.py` (also `gateway`)

### `heartbeat`

2 files. Primary slug `heartbeat`.

- `gateway/run_heartbeat_acceptance.py` (also `gateway`)
- `gateway/run_heartbeat_restore.py` (also `gateway`)

### `memory`

2 files. Primary slug `memory`.

- `gateway/memory_monitor.py` (also `gateway`)
- `gateway/memory_status.py` (also `gateway`)

### `approval`

1 file. Primary slug `approval`.

- `gateway/run_turn_runner_approval_settle.py` (also `gateway`)

### `clarify_todo`

1 file. Primary slug `clarify_todo`.

- `gateway/run_turn_runner_clarify_delivery.py` (also `gateway`)

### `hooks`

1 file. Primary slug `hooks`.

- `gateway/hooks.py` (also `gateway`)

### `kanban_fleet`

1 file. Primary slug `kanban_fleet`.

- `gateway/stream_consumer_fences.py` (also `gateway`)

### `kanban_lanes`

1 file. Primary slug `kanban_lanes`.

- `gateway/kanban_watchers_dispatcher.py` (also `kanban`, `gateway`)

### `model_switch`

1 file. Primary slug `model_switch`.

- `gateway/slash_commands_model.py` (also `gateway`, `cli_tui`)

### `tts`

1 file. Primary slug `tts`.

- `gateway/streaming_tts_consumer.py` (also `gateway`, `voice_mode`)

### `voice_mode`

1 file. Primary slug `voice_mode`.

- `gateway/run_voice.py` (also `gateway`)

## tui_gateway/

Terminal UI backend. Most modules are slash and RPC descriptors (`cli_tui`). Named method modules are the UI edge of another feature.

Slugs in this tree: `bot_mode`, `browser`, `cli_tui`, `context_references`, `credential_vault`, `delegation`, `heartbeat`, `language_packs`, `mcp`, `model_switch`, `pets`, `plugins`, `provider_routing`, `tool_gateway`, `tools_toolsets`, `vision`, `voice_mode`.

Package markers (no slug), 2 files:

- `tui_gateway/__init__.py`
- `tui_gateway/contracts/__init__.py`

### `cli_tui`

68 files. Primary slug `cli_tui`.

- `tui_gateway/_env.py`
- `tui_gateway/_stdin_recovery.py`
- `tui_gateway/agent_callbacks.py`
- `tui_gateway/change_watcher.py`
- `tui_gateway/compute_host.py`
- `tui_gateway/compute_host_bridge.py`
- `tui_gateway/contracts/base.py`
- `tui_gateway/contracts/common.py`
- `tui_gateway/contracts/config_free_tier_control.py`
- `tui_gateway/contracts/display.py`
- `tui_gateway/contracts/events.py`
- `tui_gateway/contracts/registry.py`
- `tui_gateway/contracts/server_requests.py`
- `tui_gateway/contracts/sessions.py`
- `tui_gateway/contracts/tools_commands.py`
- `tui_gateway/entry.py`
- `tui_gateway/event_publisher.py`
- `tui_gateway/event_replay.py`
- `tui_gateway/git_probe.py`
- `tui_gateway/host_supervisor.py`
- `tui_gateway/hosted_room_driver.py`
- `tui_gateway/hosted_room_member_activity.py`
- `tui_gateway/hosted_room_peer_http.py`
- `tui_gateway/hosted_room_peer_transport.py`
- `tui_gateway/hosted_room_server_rpc.py`
- `tui_gateway/hosted_room_service.py`
- `tui_gateway/launch_profile_policy.py`
- `tui_gateway/loop_noise.py`
- `tui_gateway/method_ctx.py`
- `tui_gateway/methods_complete.py`
- `tui_gateway/methods_complete_helpers.py`
- `tui_gateway/methods_config.py`
- `tui_gateway/methods_config_set.py`
- `tui_gateway/methods_display.py`
- `tui_gateway/methods_display_watch.py`
- `tui_gateway/methods_free_tier.py`
- `tui_gateway/methods_onboarding.py`
- `tui_gateway/methods_profiles.py`
- `tui_gateway/methods_projects.py`
- `tui_gateway/methods_session.py`
- `tui_gateway/methods_session_control.py`
- `tui_gateway/methods_session_foreign.py`
- `tui_gateway/methods_shared_metrics.py`
- `tui_gateway/methods_slash.py`
- `tui_gateway/onboarding_personalization.py`
- `tui_gateway/profile_roster_cache.py`
- `tui_gateway/project_tree.py`
- `tui_gateway/prompt_turn.py`
- `tui_gateway/render.py`
- `tui_gateway/rpc_dispatch.py`
- `tui_gateway/server.py`
- `tui_gateway/server_requests.py`
- `tui_gateway/session_auto_continue.py`
- `tui_gateway/session_compression.py`
- `tui_gateway/session_history.py`
- `tui_gateway/session_lifecycle.py`
- `tui_gateway/session_notifications.py`
- `tui_gateway/session_reaper.py`
- `tui_gateway/session_transports.py`
- `tui_gateway/session_workdir.py`
- `tui_gateway/slash_fuzzy.py`
- `tui_gateway/slash_worker.py`
- `tui_gateway/synthetic_turn.py`
- `tui_gateway/tool_progress.py`
- `tui_gateway/transport.py`
- `tui_gateway/turn_marker.py`
- `tui_gateway/user_messages.py`
- `tui_gateway/ws.py`

### `tool_gateway`

5 files. Primary slug `tool_gateway`.

- `tui_gateway/connector_payload.py` (also `cli_tui`)
- `tui_gateway/contracts/connectors.py` (also `cli_tui`)
- `tui_gateway/contracts/connectors_operation.py` (also `cli_tui`)
- `tui_gateway/methods_connectors.py` (also `cli_tui`)
- `tui_gateway/methods_connectors_account.py` (also `cli_tui`)

### `bot_mode`

3 files. Primary slug `bot_mode`.

- `tui_gateway/contracts/groups_bot_relay.py` (also `cli_tui`)
- `tui_gateway/methods_bot_relay.py` (also `cli_tui`)
- `tui_gateway/methods_groups.py` (also `cli_tui`)

### `mcp`

3 files. Primary slug `mcp`.

- `tui_gateway/contracts/tools_mcp_plugins.py` (also `cli_tui`)
- `tui_gateway/mcp_oauth_sessions.py` (also `cli_tui`)
- `tui_gateway/mcp_rpc_helpers.py` (also `cli_tui`)

### `browser`

2 files. Primary slug `browser`.

- `tui_gateway/methods_browser.py` (also `cli_tui`)
- `tui_gateway/methods_browser_control.py` (also `cli_tui`)

### `context_references`

2 files. Primary slug `context_references`.

- `tui_gateway/methods_prompt.py` (also `personality`, `cli_tui`)
- `tui_gateway/prompt_attachments.py` (also `cli_tui`)

### `credential_vault`

2 files. Primary slug `credential_vault`.

- `tui_gateway/contracts/profiles_vault_complete_foreign_subagents.py` (also `cli_tui`)
- `tui_gateway/methods_vault.py` (also `cli_tui`)

### `language_packs`

2 files. Primary slug `language_packs`.

- `tui_gateway/contracts/i18n.py` (also `cli_tui`)
- `tui_gateway/methods_i18n.py` (also `cli_tui`)

### `model_switch`

2 files. Primary slug `model_switch`.

- `tui_gateway/methods_session_model_guard.py` (also `cli_tui`)
- `tui_gateway/model_switch.py` (also `cli_tui`)

### `pets`

2 files. Primary slug `pets`.

- `tui_gateway/contracts/billing_delegation_pets.py` (also `cli_tui`)
- `tui_gateway/contracts/projects_pets.py` (also `cli_tui`)

### `voice_mode`

2 files. Primary slug `voice_mode`.

- `tui_gateway/contracts/prompt_voice.py` (also `cli_tui`)
- `tui_gateway/methods_voice.py` (also `cli_tui`)

### `delegation`

1 file. Primary slug `delegation`.

- `tui_gateway/methods_subagents.py` (also `cli_tui`)

### `heartbeat`

1 file. Primary slug `heartbeat`.

- `tui_gateway/contracts/liveness.py` (also `cli_tui`)

### `plugins`

1 file. Primary slug `plugins`.

- `tui_gateway/plugin_inject.py` (also `cli_tui`)

### `provider_routing`

1 file. Primary slug `provider_routing`.

- `tui_gateway/billing_view.py` (also `cli_tui`)

### `tools_toolsets`

1 file. Primary slug `tools_toolsets`.

- `tui_gateway/methods_tools.py` (also `cli_tui`)

### `vision`

1 file. Primary slug `vision`.

- `tui_gateway/methods_images.py` (also `image_gen`, `cli_tui`)

## plugins/

Plugin packages: model providers, memory providers, Honcho, platform adapters, web, browser, image gen, Spotify, and cron. The loader is `plugins/plugin_*.py`.

Slugs in this tree: `browser`, `cron`, `honcho`, `image_gen`, `kanban`, `memory_providers`, `platforms`, `plugins`, `spotify`, `web_dashboard`, `web_search`.

Package markers (no slug), 111 files:

- `plugins/__init__.py`
- `plugins/browser/browser_use/__init__.py`
- `plugins/browser/browserbase/__init__.py`
- `plugins/browser/firecrawl/__init__.py`
- `plugins/context_engine/__init__.py`
- `plugins/cron_providers/__init__.py`
- `plugins/cron_providers/chronos/__init__.py`
- `plugins/dashboard_auth/basic/__init__.py`
- `plugins/dashboard_auth/drain/__init__.py`
- `plugins/dashboard_auth/nous/__init__.py`
- `plugins/dashboard_auth/self_hosted/__init__.py`
- `plugins/disk-cleanup/__init__.py`
- `plugins/google_meet/__init__.py`
- `plugins/google_meet/node/__init__.py`
- `plugins/google_meet/realtime/__init__.py`
- `plugins/image_gen/deepinfra/__init__.py`
- `plugins/image_gen/fal/__init__.py`
- `plugins/image_gen/krea/__init__.py`
- `plugins/image_gen/meta-ai/__init__.py`
- `plugins/image_gen/openai-codex/__init__.py`
- `plugins/image_gen/openai/__init__.py`
- `plugins/image_gen/openrouter/__init__.py`
- `plugins/image_gen/xai/__init__.py`
- `plugins/memory/__init__.py`
- `plugins/memory/byterover/__init__.py`
- `plugins/memory/holographic/__init__.py`
- `plugins/memory/honcho/__init__.py`
- `plugins/memory/mem0/__init__.py`
- `plugins/memory/openviking/__init__.py`
- `plugins/memory/retaindb/__init__.py`
- `plugins/memory/supermemory/__init__.py`
- `plugins/model-providers/actual/__init__.py`
- `plugins/model-providers/ai-gateway/__init__.py`
- `plugins/model-providers/alibaba-coding-plan/__init__.py`
- `plugins/model-providers/alibaba/__init__.py`
- `plugins/model-providers/anthropic/__init__.py`
- `plugins/model-providers/arcee/__init__.py`
- `plugins/model-providers/azure-foundry/__init__.py`
- `plugins/model-providers/bedrock/__init__.py`
- `plugins/model-providers/commandcode/__init__.py`
- `plugins/model-providers/copilot-acp/__init__.py`
- `plugins/model-providers/copilot/__init__.py`
- `plugins/model-providers/custom/__init__.py`
- `plugins/model-providers/deepinfra/__init__.py`
- `plugins/model-providers/deepseek/__init__.py`
- `plugins/model-providers/fireworks/__init__.py`
- `plugins/model-providers/gemini/__init__.py`
- `plugins/model-providers/gmi/__init__.py`
- `plugins/model-providers/huggingface/__init__.py`
- `plugins/model-providers/kilocode/__init__.py`
- `plugins/model-providers/kimi-coding/__init__.py`
- `plugins/model-providers/meta-ai/__init__.py`
- `plugins/model-providers/minimax/__init__.py`
- `plugins/model-providers/nebius-token-factory/__init__.py`
- `plugins/model-providers/nous/__init__.py`
- `plugins/model-providers/novita/__init__.py`
- `plugins/model-providers/nvidia/__init__.py`
- `plugins/model-providers/ollama-cloud/__init__.py`
- `plugins/model-providers/openai-codex/__init__.py`
- `plugins/model-providers/opencode-zen/__init__.py`
- `plugins/model-providers/openrouter/__init__.py`
- `plugins/model-providers/qwen-oauth/__init__.py`
- `plugins/model-providers/router/__init__.py`
- `plugins/model-providers/stepfun/__init__.py`
- `plugins/model-providers/upstage/__init__.py`
- `plugins/model-providers/vertex/__init__.py`
- `plugins/model-providers/xai/__init__.py`
- `plugins/model-providers/xiaomi/__init__.py`
- `plugins/model-providers/zai/__init__.py`
- `plugins/observability/langfuse/__init__.py`
- `plugins/platforms/a2a/__init__.py`
- `plugins/platforms/buzz/__init__.py`
- `plugins/platforms/dingtalk/__init__.py`
- `plugins/platforms/discord/__init__.py`
- `plugins/platforms/email/__init__.py`
- `plugins/platforms/feishu/__init__.py`
- `plugins/platforms/google_chat/__init__.py`
- `plugins/platforms/homeassistant/__init__.py`
- `plugins/platforms/irc/__init__.py`
- `plugins/platforms/line/__init__.py`
- `plugins/platforms/matrix/__init__.py`
- `plugins/platforms/mattermost/__init__.py`
- `plugins/platforms/ntfy/__init__.py`
- `plugins/platforms/photon/__init__.py`
- `plugins/platforms/raft/__init__.py`
- `plugins/platforms/simplex/__init__.py`
- `plugins/platforms/slack/__init__.py`
- `plugins/platforms/sms/__init__.py`
- `plugins/platforms/teams/__init__.py`
- `plugins/platforms/telegram/__init__.py`
- `plugins/platforms/wecom/__init__.py`
- `plugins/platforms/whatsapp/__init__.py`
- `plugins/security-guidance/__init__.py`
- `plugins/spotify/__init__.py`
- `plugins/teams_pipeline/__init__.py`
- `plugins/video_gen/deepinfra/__init__.py`
- `plugins/video_gen/fal/__init__.py`
- `plugins/video_gen/openrouter/__init__.py`
- `plugins/video_gen/xai/__init__.py`
- `plugins/web/__init__.py`
- `plugins/web/brave_free/__init__.py`
- `plugins/web/ddgs/__init__.py`
- `plugins/web/exa/__init__.py`
- `plugins/web/firecrawl/__init__.py`
- `plugins/web/keenable/__init__.py`
- `plugins/web/openai_native/__init__.py`
- `plugins/web/parallel/__init__.py`
- `plugins/web/perplexity/__init__.py`
- `plugins/web/searxng/__init__.py`
- `plugins/web/tavily/__init__.py`
- `plugins/web/xai/__init__.py`

### `platforms`

55 files. Primary slug `platforms`.

- `plugins/platforms/a2a/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/a2a/protocol.py` (also `plugins`, `gateway`)
- `plugins/platforms/a2a/security.py` (also `plugins`, `gateway`)
- `plugins/platforms/a2a/tools.py` (also `plugins`, `gateway`)
- `plugins/platforms/buzz/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/buzz/nostr_auth.py` (also `plugins`, `gateway`)
- `plugins/platforms/dingtalk/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/dingtalk/inbound.py` (also `plugins`, `gateway`)
- `plugins/platforms/discord/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/discord/adapter_media.py` (also `plugins`, `gateway`)
- `plugins/platforms/discord/ffmpeg_utils.py` (also `plugins`, `gateway`)
- `plugins/platforms/discord/recovery.py` (also `plugins`, `gateway`)
- `plugins/platforms/discord/voice_mixer.py` (also `plugins`, `gateway`, `voice_mode`)
- `plugins/platforms/email/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/feishu/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/feishu/feishu_admission_diagnostics.py` (also `plugins`, `gateway`)
- `plugins/platforms/feishu/feishu_comment.py` (also `plugins`, `gateway`)
- `plugins/platforms/feishu/feishu_comment_rules.py` (also `plugins`, `gateway`)
- `plugins/platforms/feishu/feishu_meeting_invite.py` (also `plugins`, `gateway`)
- `plugins/platforms/google_chat/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/google_chat/cards.py` (also `plugins`, `gateway`)
- `plugins/platforms/google_chat/oauth.py` (also `plugins`, `gateway`)
- `plugins/platforms/google_chat/setup_files.py` (also `plugins`, `gateway`)
- `plugins/platforms/homeassistant/adapter.py` (also `home_assistant`, `plugins`)
- `plugins/platforms/irc/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/line/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/matrix/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/matrix/voice_mention.py` (also `plugins`, `gateway`, `voice_mode`)
- `plugins/platforms/mattermost/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/ntfy/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/photon/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/photon/auth.py` (also `plugins`, `gateway`)
- `plugins/platforms/photon/cli.py` (also `plugins`, `gateway`)
- `plugins/platforms/photon/sidecar_paths.py` (also `plugins`, `gateway`)
- `plugins/platforms/raft/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/simplex/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/slack/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/slack/block_kit.py` (also `plugins`, `gateway`)
- `plugins/platforms/sms/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/teams/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/teams/summary_writer.py` (also `plugins`, `gateway`)
- `plugins/platforms/telegram/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/telegram/inline_picker.py` (also `plugins`, `gateway`)
- `plugins/platforms/telegram/telegram_context.py` (also `plugins`, `gateway`)
- `plugins/platforms/telegram/telegram_entities.py` (also `plugins`, `gateway`)
- `plugins/platforms/telegram/telegram_ids.py` (also `plugins`, `gateway`)
- `plugins/platforms/telegram/telegram_network.py` (also `plugins`, `gateway`)
- `plugins/platforms/telegram/update_admission.py` (also `plugins`, `gateway`)
- `plugins/platforms/wecom/adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/wecom/callback_adapter.py` (also `plugins`, `gateway`)
- `plugins/platforms/wecom/media.py` (also `plugins`, `gateway`)
- `plugins/platforms/wecom/send_queue.py` (also `plugins`, `gateway`)
- `plugins/platforms/wecom/streaming.py` (also `plugins`, `gateway`)
- `plugins/platforms/wecom/wecom_crypto.py` (also `plugins`, `gateway`)
- `plugins/platforms/whatsapp/adapter.py` (also `plugins`, `gateway`)

### `honcho`

14 files. Primary slug `honcho`.

- `plugins/memory/honcho/cli.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/client.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/client_cache.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/config_schema.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/dialectic.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/oauth.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/oauth_flow.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/recall_sync.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/session.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/session_auth.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/session_context.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/session_migration.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/session_peers.py` (also `memory_providers`, `plugins`)
- `plugins/memory/honcho/tool_schemas.py` (also `memory_providers`, `plugins`)

### `web_search`

14 files. Primary slug `web_search`.

- `plugins/web/_common.py` (also `plugins`)
- `plugins/web/brave_free/provider.py` (also `plugins`)
- `plugins/web/ddgs/_search_worker.py` (also `plugins`)
- `plugins/web/ddgs/provider.py` (also `plugins`)
- `plugins/web/exa/provider.py` (also `plugins`)
- `plugins/web/firecrawl/provider.py` (also `plugins`)
- `plugins/web/keenable/provider.py` (also `plugins`)
- `plugins/web/keyless_mcp.py` (also `plugins`)
- `plugins/web/openai_native/provider.py` (also `plugins`)
- `plugins/web/parallel/provider.py` (also `plugins`)
- `plugins/web/perplexity/provider.py` (also `plugins`)
- `plugins/web/searxng/provider.py` (also `plugins`)
- `plugins/web/tavily/provider.py` (also `plugins`)
- `plugins/web/xai/provider.py` (also `plugins`)

### `memory_providers`

10 files. Primary slug `memory_providers`.

- `plugins/memory/config_schema.py` (also `memory`, `plugins`)
- `plugins/memory/holographic/holographic.py` (also `memory`, `plugins`)
- `plugins/memory/holographic/retrieval.py` (also `memory`, `plugins`)
- `plugins/memory/holographic/store.py` (also `memory`, `plugins`)
- `plugins/memory/mem0/_backend.py` (also `memory`, `plugins`)
- `plugins/memory/mem0/_openai_llm.py` (also `memory`, `plugins`)
- `plugins/memory/mem0/_oss_providers.py` (also `memory`, `plugins`)
- `plugins/memory/mem0/_setup.py` (also `memory`, `plugins`)
- `plugins/memory/openviking/_setup.py` (also `memory`, `plugins`)
- `plugins/memory/query_rewrite.py` (also `memory`, `plugins`)

### `browser`

4 files. Primary slug `browser`.

- `plugins/browser/_common.py` (also `plugins`)
- `plugins/browser/browser_use/provider.py` (also `plugins`)
- `plugins/browser/browserbase/provider.py` (also `plugins`)
- `plugins/browser/firecrawl/provider.py` (also `plugins`, `web_search`)

### `plugins`

3 files. Primary slug `plugins`.

- `plugins/plugin_loader.py`
- `plugins/plugin_storage.py`
- `plugins/plugin_utils.py`

### `cron`

2 files. Primary slug `cron`.

- `plugins/cron_providers/chronos/_nas_client.py` (also `plugins`)
- `plugins/cron_providers/chronos/verify.py` (also `plugins`)

### `spotify`

2 files. Primary slug `spotify`.

- `plugins/spotify/client.py` (also `plugins`)
- `plugins/spotify/tools.py` (also `plugins`)

### `image_gen`

1 file. Primary slug `image_gen`.

- `plugins/image_gen/_common.py` (also `plugins`)

### `kanban`

1 file. Primary slug `kanban`.

- `plugins/kanban/dashboard/plugin_api.py` (also `plugins`, `web_dashboard`)

### `web_dashboard`

1 file. Primary slug `web_dashboard`.

- `plugins/dashboard_auth/_shared.py` (also `plugins`)

### No FEATURES.md slug

In this tree, not packaging, and no slug fits the path name. Shared infrastructure stays here instead of being forced onto a feature.

- `plugins/disk-cleanup/disk_cleanup.py`
- `plugins/google_meet/_jsonfile.py`
- `plugins/google_meet/audio_bridge.py`
- `plugins/google_meet/cli.py`
- `plugins/google_meet/meet_bot.py`
- `plugins/google_meet/node/cli.py`
- `plugins/google_meet/node/client.py`
- `plugins/google_meet/node/protocol.py`
- `plugins/google_meet/node/registry.py`
- `plugins/google_meet/node/server.py`
- `plugins/google_meet/process_manager.py`
- `plugins/google_meet/realtime/openai_client.py`
- `plugins/google_meet/tools.py`
- `plugins/hermes-achievements/dashboard/plugin_api.py`
- `plugins/hermes-achievements/tests/test_achievement_engine.py`
- `plugins/security-guidance/patterns.py`
- `plugins/teams_pipeline/cli.py`
- `plugins/teams_pipeline/meetings.py`
- `plugins/teams_pipeline/models.py`
- `plugins/teams_pipeline/pipeline.py`
- `plugins/teams_pipeline/runtime.py`
- `plugins/teams_pipeline/store.py`
- `plugins/teams_pipeline/subscriptions.py`

## acp_adapter/

Editor integration (Agent Client Protocol). The package is `acp`.

Slugs in this tree: `acp`.

Package markers (no slug), 1 files:

- `acp_adapter/__init__.py`

### `acp`

13 files. Primary slug `acp`.

- `acp_adapter/__main__.py`
- `acp_adapter/auth.py`
- `acp_adapter/commands.py`
- `acp_adapter/content.py`
- `acp_adapter/edit_approval.py` (also `approval`)
- `acp_adapter/entry.py`
- `acp_adapter/events.py`
- `acp_adapter/model_catalog.py` (also `model_switch`)
- `acp_adapter/permissions.py`
- `acp_adapter/provenance.py`
- `acp_adapter/server.py`
- `acp_adapter/session.py`
- `acp_adapter/tools.py` (also `tools_toolsets`)

## cron/

In-process scheduler. The package is `cron`. This map names it; it does not adopt the thread.

Slugs in this tree: `cron`.

Package markers (no slug), 2 files:

- `cron/__init__.py`
- `cron/scripts/__init__.py`

### `cron`

33 files. Primary slug `cron`.

- `cron/blueprint_catalog.py`
- `cron/bot_chat_delivery.py`
- `cron/constants.py`
- `cron/delivery_queue.py`
- `cron/env_settings.py`
- `cron/executions.py`
- `cron/incidents.py`
- `cron/job_definition.py`
- `cron/jobs.py`
- `cron/lifecycle_guard.py`
- `cron/monitor.py`
- `cron/notepad.py`
- `cron/occurrences.py`
- `cron/quota_hold.py`
- `cron/scheduler.py`
- `cron/scheduler_delivery.py`
- `cron/scheduler_detached_worker.py`
- `cron/scheduler_diagnostics.py`
- `cron/scheduler_failure_copy.py`
- `cron/scheduler_ownership.py`
- `cron/scheduler_preflight.py`
- `cron/scheduler_prompt.py`
- `cron/scheduler_provider.py`
- `cron/scheduler_script.py`
- `cron/scheduler_thread.py`
- `cron/scheduler_tick.py`
- `cron/scheduler_worker_env.py`
- `cron/scheduler_worker_failure.py`
- `cron/scripts/classify_items.py`
- `cron/suggestion_catalog.py`
- `cron/suggestions.py`
- `cron/unreachable_retry.py`
- `cron/worker_bootstrap.py`

## hermes_platform/

Host and install-layout facts. This is not the messaging `platforms` slug.

Package markers (no slug), 3 files:

- `hermes_platform/__init__.py`
- `hermes_platform/host/__init__.py`
- `hermes_platform/resolver/__init__.py`

### No FEATURES.md slug

In this tree, not packaging, and no slug fits the path name. Shared infrastructure stays here instead of being forced onto a feature.

- `hermes_platform/declaration.py`
- `hermes_platform/host/facts.py`
- `hermes_platform/host/products.py`
- `hermes_platform/host/runtime.py`
- `hermes_platform/resolver/app.py`
- `hermes_platform/resolver/availability.py`
- `hermes_platform/resolver/base.py`
- `hermes_platform/resolver/core.py`
- `hermes_platform/resolver/known_dirs.py`

## providers/

Small provider base. Routing itself is `agent/` plus `plugins/model-providers/`.

Slugs in this tree: `provider_routing`.

Package markers (no slug), 1 files:

- `providers/__init__.py`

### `provider_routing`

1 file. Primary slug `provider_routing`.

- `providers/base.py`

## skills/ and optional-skills/

Skill payloads. The loader is `tools/skills_*.py`, `tools/skill_*.py`, `agent/skill_*.py`, and `hermes_cli` skills commands (`skills`). These scripts are what a loaded skill runs. They are not a second agent.

155 Python files. Each maps to `skills`. Extra slugs from the directory name: `document_extract` for pdf, docx, xlsx, and powerpoint; `image_gen` for comfyui, pixel-art, meme, and presenter; `mcp` for `optional-skills/mcp/`; `kanban` when the path contains kanban.

### `optional-skills/blockchain/evm`

Slugs: `skills`. 1 file.

- `optional-skills/blockchain/evm/scripts/evm_client.py`

### `optional-skills/blockchain/hyperliquid`

Slugs: `skills`. 1 file.

- `optional-skills/blockchain/hyperliquid/scripts/hyperliquid_client.py`

### `optional-skills/blockchain/solana`

Slugs: `skills`. 1 file.

- `optional-skills/blockchain/solana/scripts/solana_client.py`

### `optional-skills/creative/ai-presenter-video`

Slugs: `skills`, `image_gen`. 2 files.

- `optional-skills/creative/ai-presenter-video/scripts/init_job.py`
- `optional-skills/creative/ai-presenter-video/scripts/preflight.py`

### `optional-skills/creative/comfyui`

Slugs: `skills`, `image_gen`. 16 files.

- `optional-skills/creative/comfyui/scripts/_common.py`
- `optional-skills/creative/comfyui/scripts/auto_fix_deps.py`
- `optional-skills/creative/comfyui/scripts/check_deps.py`
- `optional-skills/creative/comfyui/scripts/extract_schema.py`
- `optional-skills/creative/comfyui/scripts/fetch_logs.py`
- `optional-skills/creative/comfyui/scripts/hardware_check.py`
- `optional-skills/creative/comfyui/scripts/health_check.py`
- `optional-skills/creative/comfyui/scripts/run_batch.py`
- `optional-skills/creative/comfyui/scripts/run_workflow.py`
- `optional-skills/creative/comfyui/scripts/ws_monitor.py`
- `optional-skills/creative/comfyui/tests/conftest.py`
- `optional-skills/creative/comfyui/tests/test_check_deps.py`
- `optional-skills/creative/comfyui/tests/test_cloud_integration.py`
- `optional-skills/creative/comfyui/tests/test_common.py`
- `optional-skills/creative/comfyui/tests/test_extract_schema.py`
- `optional-skills/creative/comfyui/tests/test_run_workflow.py`

### `optional-skills/creative/excalidraw`

Slugs: `skills`. 1 file.

- `optional-skills/creative/excalidraw/scripts/upload.py`

### `optional-skills/creative/kanban-video-orchestrator`

Slugs: `skills`, `kanban`. 2 files.

- `optional-skills/creative/kanban-video-orchestrator/scripts/bootstrap_pipeline.py`
- `optional-skills/creative/kanban-video-orchestrator/scripts/monitor.py`

### `optional-skills/creative/meme-generation`

Slugs: `skills`, `image_gen`. 1 file.

- `optional-skills/creative/meme-generation/scripts/generate_meme.py`

### `optional-skills/creative/pixel-art`

Slugs: `skills`, `image_gen`. 4 files.

- `optional-skills/creative/pixel-art/scripts/__init__.py`
- `optional-skills/creative/pixel-art/scripts/palettes.py`
- `optional-skills/creative/pixel-art/scripts/pixel_art.py`
- `optional-skills/creative/pixel-art/scripts/pixel_art_video.py`

### `optional-skills/devops/watchers`

Slugs: `skills`. 4 files.

- `optional-skills/devops/watchers/scripts/_watermark.py`
- `optional-skills/devops/watchers/scripts/watch_github.py`
- `optional-skills/devops/watchers/scripts/watch_http_json.py`
- `optional-skills/devops/watchers/scripts/watch_rss.py`

### `optional-skills/finance/dcf-model`

Slugs: `skills`. 1 file.

- `optional-skills/finance/dcf-model/scripts/validate_dcf.py`

### `optional-skills/finance/excel-author`

Slugs: `skills`. 1 file.

- `optional-skills/finance/excel-author/scripts/recalc.py`

### `optional-skills/finance/polymarket`

Slugs: `skills`. 1 file.

- `optional-skills/finance/polymarket/scripts/polymarket.py`

### `optional-skills/finance/stocks`

Slugs: `skills`. 1 file.

- `optional-skills/finance/stocks/scripts/stocks_client.py`

### `optional-skills/health/fitness-nutrition`

Slugs: `skills`. 2 files.

- `optional-skills/health/fitness-nutrition/scripts/body_calc.py`
- `optional-skills/health/fitness-nutrition/scripts/nutrition_search.py`

### `optional-skills/mcp/fastmcp`

Slugs: `skills`, `mcp`. 4 files.

- `optional-skills/mcp/fastmcp/scripts/scaffold_fastmcp.py`
- `optional-skills/mcp/fastmcp/templates/api_wrapper.py`
- `optional-skills/mcp/fastmcp/templates/database_server.py`
- `optional-skills/mcp/fastmcp/templates/file_processor.py`

### `optional-skills/mcp/mcp-oauth-remote-gateway`

Slugs: `skills`, `mcp`. 1 file.

- `optional-skills/mcp/mcp-oauth-remote-gateway/scripts/diagnose-oauth-mcp.py`

### `optional-skills/migration/openclaw-migration`

Slugs: `skills`. 1 file.

- `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`

### `optional-skills/mlops/training`

Slugs: `skills`. 1 file.

- `optional-skills/mlops/training/trl-fine-tuning/templates/basic_grpo_training.py`

### `optional-skills/productivity/canvas`

Slugs: `skills`. 1 file.

- `optional-skills/productivity/canvas/scripts/canvas_api.py`

### `optional-skills/productivity/memento-flashcards`

Slugs: `skills`, `image_gen`. 2 files.

- `optional-skills/productivity/memento-flashcards/scripts/memento_cards.py`
- `optional-skills/productivity/memento-flashcards/scripts/youtube_quiz.py`

### `optional-skills/productivity/telephony`

Slugs: `skills`. 1 file.

- `optional-skills/productivity/telephony/scripts/telephony.py`

### `optional-skills/research/darwinian-evolver`

Slugs: `skills`. 3 files.

- `optional-skills/research/darwinian-evolver/scripts/parrot_openrouter.py`
- `optional-skills/research/darwinian-evolver/scripts/show_snapshot.py`
- `optional-skills/research/darwinian-evolver/templates/custom_problem_template.py`

### `optional-skills/research/domain-intel`

Slugs: `skills`. 1 file.

- `optional-skills/research/domain-intel/scripts/domain_intel.py`

### `optional-skills/research/drug-discovery`

Slugs: `skills`. 2 files.

- `optional-skills/research/drug-discovery/scripts/chembl_target.py`
- `optional-skills/research/drug-discovery/scripts/ro5_screen.py`

### `optional-skills/research/osint-investigation`

Slugs: `skills`. 16 files.

- `optional-skills/research/osint-investigation/scripts/_http.py`
- `optional-skills/research/osint-investigation/scripts/_normalize.py`
- `optional-skills/research/osint-investigation/scripts/build_findings.py`
- `optional-skills/research/osint-investigation/scripts/entity_resolution.py`
- `optional-skills/research/osint-investigation/scripts/fetch_courtlistener.py`
- `optional-skills/research/osint-investigation/scripts/fetch_gdelt.py`
- `optional-skills/research/osint-investigation/scripts/fetch_icij_offshore.py`
- `optional-skills/research/osint-investigation/scripts/fetch_nyc_acris.py`
- `optional-skills/research/osint-investigation/scripts/fetch_ofac_sdn.py`
- `optional-skills/research/osint-investigation/scripts/fetch_opencorporates.py`
- `optional-skills/research/osint-investigation/scripts/fetch_sec_edgar.py`
- `optional-skills/research/osint-investigation/scripts/fetch_senate_ld.py`
- `optional-skills/research/osint-investigation/scripts/fetch_usaspending.py`
- `optional-skills/research/osint-investigation/scripts/fetch_wayback.py`
- `optional-skills/research/osint-investigation/scripts/fetch_wikipedia.py`
- `optional-skills/research/osint-investigation/scripts/timing_analysis.py`

### `optional-skills/research/pinecone-research`

Slugs: `skills`. 2 files.

- `optional-skills/research/pinecone-research/scripts/memory_manager.py`
- `optional-skills/research/pinecone-research/scripts/rag_pipeline.py`

### `optional-skills/research/rss-feeds`

Slugs: `skills`. 1 file.

- `optional-skills/research/rss-feeds/scripts/feed.py`

### `optional-skills/security/godmode`

Slugs: `skills`. 4 files.

- `optional-skills/security/godmode/scripts/auto_jailbreak.py`
- `optional-skills/security/godmode/scripts/godmode_race.py`
- `optional-skills/security/godmode/scripts/load_godmode.py`
- `optional-skills/security/godmode/scripts/parseltongue.py`

### `optional-skills/security/oss-forensics`

Slugs: `skills`. 1 file.

- `optional-skills/security/oss-forensics/scripts/evidence-store.py`

### `optional-skills/security/unbroker`

Slugs: `skills`. 19 files.

- `optional-skills/security/unbroker/scripts/autopilot.py`
- `optional-skills/security/unbroker/scripts/badbool.py`
- `optional-skills/security/unbroker/scripts/brokers.py`
- `optional-skills/security/unbroker/scripts/cdp.py`
- `optional-skills/security/unbroker/scripts/config.py`
- `optional-skills/security/unbroker/scripts/crypto.py`
- `optional-skills/security/unbroker/scripts/dossier.py`
- `optional-skills/security/unbroker/scripts/email_modes.py`
- `optional-skills/security/unbroker/scripts/emailer.py`
- `optional-skills/security/unbroker/scripts/ledger.py`
- `optional-skills/security/unbroker/scripts/legal.py`
- `optional-skills/security/unbroker/scripts/paths.py`
- `optional-skills/security/unbroker/scripts/pdd.py`
- `optional-skills/security/unbroker/scripts/registry.py`
- `optional-skills/security/unbroker/scripts/report.py`
- `optional-skills/security/unbroker/scripts/scan.py`
- `optional-skills/security/unbroker/scripts/storage.py`
- `optional-skills/security/unbroker/scripts/tiers.py`
- `optional-skills/security/unbroker/scripts/vectors.py`

### `optional-skills/social-media/reddit-reading`

Slugs: `skills`. 1 file.

- `optional-skills/social-media/reddit-reading/scripts/reddit.py`

### `optional-skills/software-development/ast-grep`

Slugs: `skills`. 1 file.

- `optional-skills/software-development/ast-grep/scripts/ast_grep_helper.py`

### `optional-skills/web-development/cloudflare-temporary-deploy`

Slugs: `skills`. 1 file.

- `optional-skills/web-development/cloudflare-temporary-deploy/scripts/parse_deploy_output.py`

### `optional-skills/web-development/har-derived-api-client`

Slugs: `skills`. 3 files.

- `optional-skills/web-development/har-derived-api-client/scripts/har_capture.py`
- `optional-skills/web-development/har-derived-api-client/scripts/har_capture_cdp.py`
- `optional-skills/web-development/har-derived-api-client/scripts/har_to_client.py`

### `skills/media/youtube-content`

Slugs: `skills`. 1 file.

- `skills/media/youtube-content/scripts/fetch_transcript.py`

### `skills/productivity/docx`

Slugs: `skills`, `document_extract`. 9 files.

- `skills/productivity/docx/scripts/docx_comments.py`
- `skills/productivity/docx/scripts/docx_common.py`
- `skills/productivity/docx/scripts/docx_create.py`
- `skills/productivity/docx/scripts/docx_edit.py`
- `skills/productivity/docx/scripts/docx_read.py`
- `skills/productivity/docx/scripts/docx_revisions.py`
- `skills/productivity/docx/scripts/docx_template.py`
- `skills/productivity/docx/scripts/docx_validate.py`
- `skills/productivity/docx/tests/test_docx_skill.py`

### `skills/productivity/google-workspace`

Slugs: `skills`. 4 files.

- `skills/productivity/google-workspace/scripts/_hermes_home.py`
- `skills/productivity/google-workspace/scripts/google_api.py`
- `skills/productivity/google-workspace/scripts/gws_bridge.py`
- `skills/productivity/google-workspace/scripts/setup.py`

### `skills/productivity/maps`

Slugs: `skills`. 1 file.

- `skills/productivity/maps/scripts/maps_client.py`

### `skills/productivity/pdf`

Slugs: `skills`, `document_extract`. 16 files.

- `skills/productivity/pdf/scripts/_raster.py`
- `skills/productivity/pdf/scripts/extract_marker.py`
- `skills/productivity/pdf/scripts/extract_pymupdf.py`
- `skills/productivity/pdf/scripts/pdf_create.py`
- `skills/productivity/pdf/scripts/pdf_fill_form.py`
- `skills/productivity/pdf/scripts/pdf_form_layout.py`
- `skills/productivity/pdf/scripts/pdf_make_form.py`
- `skills/productivity/pdf/scripts/pdf_merge.py`
- `skills/productivity/pdf/scripts/pdf_meta.py`
- `skills/productivity/pdf/scripts/pdf_page_image.py`
- `skills/productivity/pdf/scripts/pdf_read.py`
- `skills/productivity/pdf/scripts/pdf_secure.py`
- `skills/productivity/pdf/scripts/pdf_split.py`
- `skills/productivity/pdf/scripts/pdf_stamp.py`
- `skills/productivity/pdf/scripts/pdf_watermark.py`
- `skills/productivity/pdf/tests/test_pdf_skill.py`

### `skills/productivity/powerpoint`

Slugs: `skills`, `document_extract`. 6 files.

- `skills/productivity/powerpoint/scripts/pptx_create.py`
- `skills/productivity/powerpoint/scripts/pptx_edit.py`
- `skills/productivity/powerpoint/scripts/pptx_from_template.py`
- `skills/productivity/powerpoint/scripts/pptx_read.py`
- `skills/productivity/powerpoint/scripts/pptx_render.py`
- `skills/productivity/powerpoint/tests/test_powerpoint_skill.py`

### `skills/productivity/xlsx`

Slugs: `skills`, `document_extract`. 8 files.

- `skills/productivity/xlsx/scripts/csv_to_xlsx.py`
- `skills/productivity/xlsx/scripts/xlsx_create.py`
- `skills/productivity/xlsx/scripts/xlsx_edit.py`
- `skills/productivity/xlsx/scripts/xlsx_read.py`
- `skills/productivity/xlsx/scripts/xlsx_recalc.py`
- `skills/productivity/xlsx/scripts/xlsx_restructure.py`
- `skills/productivity/xlsx/scripts/xlsx_to_csv.py`
- `skills/productivity/xlsx/tests/test_xlsx_skill.py`

### `skills/research/arxiv`

Slugs: `skills`. 1 file.

- `skills/research/arxiv/scripts/search_arxiv.py`

### `skills/research/grounded-citations`

Slugs: `skills`. 2 files.

- `skills/research/grounded-citations/scripts/_hermes_home.py`
- `skills/research/grounded-citations/scripts/sources.py`

### `skills/software-development/github`

Slugs: `skills`. 1 file.

- `skills/software-development/github/scripts/git-credential-token.py`

### `skills/web/blocked-page-recovery`

Slugs: `skills`. 1 file.

- `skills/web/blocked-page-recovery/scripts/recover_page.py`

## evals/

Evaluation harnesses, not product features. The directory name is the hint. Desktop campaign, postmortem, and update probes have no feature slug.

146 files.

### evals/ (root files)

- `evals/__init__.py` (no slug)
- `evals/acp_empty_session_wire.py` (no slug)
- `evals/anthropic_proxy_thinking_replay.py` (no slug)
- `evals/api_delegation_http_probe.py` (no slug)
- `evals/api_delegation_sync_probe.py` (no slug)
- `evals/approval_deny_dispatch.py` (hint `approval`)
- `evals/auth_pool_controls.py` (no slug)
- `evals/auxiliary_resource_exhausted.py` (no slug)
- `evals/cli_deferred_notice.py` (no slug)
- `evals/cli_fallback_add_picker_error.py` (hint `fallback`)
- `evals/codex_masked_replay_review.py` (hint `codex_runtime`)
- `evals/completion_backlog_probe.py` (no slug)
- `evals/cron_error_diagnostics.py` (hint `cron`)
- `evals/cron_timeout_fork_race.py` (hint `cron`)
- `evals/delivery_flood_wire.py` (hint `gateway`)
- `evals/fanout_resource_bench.py` (no slug)
- `evals/gemini_type_array_probe.py` (no slug)
- `evals/goal_command_parity.py` (hint `goals`)
- `evals/heartbeat_idle_wire.py` (hint `heartbeat`)
- `evals/kanban_graph_identity.py` (hint `kanban`)
- `evals/kanban_pr_acceptance_live.py` (hint `kanban`)
- `evals/kanban_scope_probe.py` (hint `kanban`)
- `evals/key_cmd_picker_live.py` (no slug)
- `evals/mcp_device_flow.py` (hint `mcp`)
- `evals/output_caps_local_capture.py` (no slug)
- `evals/output_caps_surfaces.py` (no slug)
- `evals/process_result_receipt_probe.py` (no slug)
- `evals/session_snapshot_removal.py` (no slug)
- `evals/slack_stream_wire_contract.py` (no slug)
- `evals/update_check_ssh_pty.py` (no slug)
- `evals/update_obligation_identity.py` (no slug)
- `evals/update_unit_client_budget.py` (no slug)
- `evals/vault_fill_live_e2e.py` (hint `credential_vault`)

### `evals/botmode-dm-delivery`

Hint: `bot_mode`. 1 file.

- `evals/botmode-dm-delivery/exception-tick.py`

### `evals/browser_use`

Hint: `browser`. 5 files.

- `evals/browser_use/benchmark_browser_eval.py`
- `evals/browser_use/orchestrate.py`
- `evals/browser_use/orchestrate_cloud.py`
- `evals/browser_use/report.py`
- `evals/browser_use/single_run.py`

### `evals/codebase_navigability`

Hint: `file_terminal`. 5 files.

- `evals/codebase_navigability/__init__.py`
- `evals/codebase_navigability/bench.py`
- `evals/codebase_navigability/lookup_sim.py`
- `evals/codebase_navigability/runtime_bench.py`
- `evals/codebase_navigability/static_metrics.py`

### `evals/codex_echo`

Hint: `codex_runtime`. 2 files.

- `evals/codex_echo/fixture_server.py`
- `evals/codex_echo/probe.py`

### `evals/compaction`

Hint: `agent_loop`. 12 files.

- `evals/compaction/fixtures.py`
- `evals/compaction/jev_arm.py`
- `evals/compaction/policies.py`
- `evals/compaction/report.py`
- `evals/compaction/runner.py`
- `evals/compaction/scripts/build_html_report.py`
- `evals/compaction/scripts/codex_arm.py`
- `evals/compaction/scripts/jev_cycles.py`
- `evals/compaction/scripts/jev_cycles_report.py`
- `evals/compaction/scripts/reconstruct_lineage.py`
- `evals/compaction/scripts/replay_lineage.py`
- `evals/compaction/test_region_scoping.py`

### `evals/core_tool_deferral`

Hint: `tool_search`. 4 files.

- `evals/core_tool_deferral/orchestrator.py`
- `evals/core_tool_deferral/report.py`
- `evals/core_tool_deferral/tasks.py`
- `evals/core_tool_deferral/worker.py`

### `evals/dashboard_auth`

Hint: `web_dashboard`. 1 file.

- `evals/dashboard_auth/refresh_singleflight_live_e2e.py`

### `evals/delegation_group_schema`

Hint: `delegation`. 1 file.

- `evals/delegation_group_schema/probe.py`

### `evals/desktop_bug_campaign`

Hint: no slug. 8 files.

- `evals/desktop_bug_campaign/async-report-producer.py`
- `evals/desktop_bug_campaign/history_live.py`
- `evals/desktop_bug_campaign/hooks_live.py`
- `evals/desktop_bug_campaign/leases_live.py`
- `evals/desktop_bug_campaign/linux_launcher_probe.py`
- `evals/desktop_bug_campaign/markdown-producer.py`
- `evals/desktop_bug_campaign/persistence_live.py`
- `evals/desktop_bug_campaign/rebuild_observer.py`

### `evals/desktop_mcp_oauth`

Hint: `mcp`. 1 file.

- `evals/desktop_mcp_oauth/backend_http_fixture.py`

### `evals/gateway`

Hint: `gateway`. 2 files.

- `evals/gateway/session_time_persistence_ab.py`
- `evals/gateway/session_time_persistence_controls.py`

### `evals/gateway_completion`

Hint: `gateway`. 1 file.

- `evals/gateway_completion/delivery_lifecycle.py`

### `evals/gateway_failure_ownership`

Hint: `gateway`. 2 files.

- `evals/gateway_failure_ownership/foreign_writer.py`
- `evals/gateway_failure_ownership/probe.py`

### `evals/gateway_status_render`

Hint: `gateway`. 1 file.

- `evals/gateway_status_render/iteration_ceiling_ab.py`

### `evals/liveness`

Hint: `heartbeat`. 1 file.

- `evals/liveness/ws_orphan_reconnect.py`

### `evals/memory`

Hint: `memory`. 1 file.

- `evals/memory/honcho_current_query.py`

### `evals/native_compaction`

Hint: `agent_loop`. 1 file.

- `evals/native_compaction/ab_checkpoint_preflight.py`

### `evals/openrouter_pkce_ab`

Hint: `provider_routing`. 1 file.

- `evals/openrouter_pkce_ab/harness.py`

### `evals/postmortem`

Hint: no slug. 33 files.

- `evals/postmortem/__init__.py`
- `evals/postmortem/forensics/__init__.py`
- `evals/postmortem/forensics/common.py`
- `evals/postmortem/forensics/delegation.py`
- `evals/postmortem/forensics/goal_loop.py`
- `evals/postmortem/forensics/logcalls.py`
- `evals/postmortem/forensics/rework.py`
- `evals/postmortem/forensics/tokens.py`
- `evals/postmortem/forensics/tools.py`
- `evals/postmortem/live_ab/__init__.py`
- `evals/postmortem/live_ab/auth_stampede.py`
- `evals/postmortem/live_ab/batch_failure_notice.py`
- `evals/postmortem/live_ab/cache_concurrency_probe.py`
- `evals/postmortem/live_ab/cache_prefix_live.py`
- `evals/postmortem/live_ab/cache_prefix_wire.py`
- `evals/postmortem/live_ab/goal_judge_wait.py`
- `evals/postmortem/live_ab/hardline_scanner_matrix.py`
- `evals/postmortem/live_ab/nested_delegate_deadline.py`
- `evals/postmortem/live_ab/subagent_context_cap.py`
- `evals/postmortem/review_probes/__init__.py`
- `evals/postmortem/review_probes/cache_estimator_probe.py`
- `evals/postmortem/review_probes/context_cap_probe.py`
- `evals/postmortem/review_probes/credential_identity_probe.py`
- `evals/postmortem/review_probes/deadline_probe.py`
- `evals/postmortem/review_probes/finalizer_schedule_probe.py`
- `evals/postmortem/review_probes/goal_repaste_probe.py`
- `evals/postmortem/review_probes/goal_scope_probe.py`
- `evals/postmortem/review_probes/notice_delivery_probe.py`
- `evals/postmortem/review_probes/rewrite_hint_probe.py`
- `evals/postmortem/review_probes/scanner_bypass_probe.py`
- `evals/postmortem/run.py`
- `evals/postmortem/tests/__init__.py`
- `evals/postmortem/tests/test_postmortem_harness.py`

### `evals/prompt_footprint`

Hint: `prompt_cache`. 1 file.

- `evals/prompt_footprint/property_guidance.py`

### `evals/provider_fallback`

Hint: `fallback`. 3 files.

- `evals/provider_fallback/probe_104120.py`
- `evals/provider_fallback/probe_104260.py`
- `evals/provider_fallback/probe_104360.py`

### `evals/provider_wire`

Hint: `provider_routing`. 3 files.

- `evals/provider_wire/issue_103944.py`
- `evals/provider_wire/issue_104282.py`
- `evals/provider_wire/issue_104359.py`

### `evals/providers`

Hint: `provider_routing`. 1 file.

- `evals/providers/reasoning_shapes.py`

### `evals/readtool`

Hint: `file_terminal`. 4 files.

- `evals/readtool/fixtures.py`
- `evals/readtool/report.py`
- `evals/readtool/runner.py`
- `evals/readtool/tasks.py`

### `evals/session_search_schema`

Hint: `session_search`. 4 files.

- `evals/session_search_schema/fixtures.py`
- `evals/session_search_schema/report.py`
- `evals/session_search_schema/runner.py`
- `evals/session_search_schema/tasks.py`

### `evals/subagent_process_handoff`

Hint: `delegation`. 1 file.

- `evals/subagent_process_handoff/stress_handoff_live.py`

### `evals/token_accounting`

Hint: `provider_routing`. 4 files.

- `evals/token_accounting/ab_image_cost_calibration.py`
- `evals/token_accounting/display_provenance.py`
- `evals/token_accounting/replay_gates.py`
- `evals/token_accounting/worktree_prompt_prefix.py`

### `evals/tool_search`

Hint: `tool_search`. 6 files.

- `evals/tool_search/analyze_livetest.py`
- `evals/tool_search/tool_search_livetest.py`
- `evals/tool_search/tool_search_livetest2.py`
- `evals/tool_search/tool_search_livetest_ue.py`
- `evals/tool_search/tool_search_livetest_ue_disc.py`
- `evals/tool_search/tool_search_livetest_ue_hard.py`

### `evals/toolperf_abeval`

Hint: `tools_toolsets`. 1 file.

- `evals/toolperf_abeval/ab_eval.py`

### `evals/update_streaming`

Hint: no slug. 1 file.

- `evals/update_streaming/live_output.py`

### `evals/webhook_auth`

Hint: `platforms`. 1 file.

- `evals/webhook_auth/standard_webhooks_ab.py`

## tests/

Tests are not product features. They follow the package they exercise. Listed by directory and count, not file by file.

5639 files.

| tests/ directory | Files | Maps like |
|---|---:|---|
| `hermes_cli` | 1427 | `hermes_cli/` slugs, mostly `cli_tui` |
| `gateway` | 1005 | `gateway`, `platforms`, `api_server` |
| `agent` | 951 | `agent/` slugs, mostly `agent_loop` and `provider_routing` |
| `tools` | 747 | `tools/` slugs |
| `tui_gateway` | 266 | `cli_tui` and the method slugs |
| `e2e` | 235 | cross-cutting, no single slug |
| `plugins` | 155 | `plugins` plus that plugin's feature slug |
| `cron` | 147 | `cron` |
| `hermes_state` | 145 | `session_search` |
| `scripts` | 132 | packaging |
| `pm` | 114 | packaging |
| `(root files)` | 65 | cross-package suite, no single slug |
| `skills` | 32 | `skills` |
| `acp_adapter` | 29 | `acp` |
| `docker` | 28 | packaging |
| `ci` | 24 | packaging |
| `honcho_plugin` | 23 | `honcho` |
| `fakes` | 20 | test doubles, no slug |
| `providers` | 17 | `provider_routing` |
| `computer_use` | 12 | `computer_use` |
| `conformance` | 9 | cross-cutting, no single slug |
| `hermes_platform` | 7 | no slug (`hermes_platform/`) |
| `website` | 7 | packaging |
| `install` | 6 | packaging |
| `monitoring` | 6 | no slug (observability) |
| `secret_sources` | 5 | `credential_vault` |
| `_fixtures` | 4 | fixtures, no slug |
| `verify` | 4 | no slug (`agent/verify`) |
| `evals` | 3 | `evals/` |
| `compat` | 2 | no single slug |
| `desktop` | 2 | packaging (desktop app) |
| `installation` | 2 | packaging |
| `manual` | 2 | no single slug |
| `dashboard` | 1 | `web_dashboard` |
| `fixtures` | 1 | fixtures, no slug |
| `integration` | 1 | same name as the package |
| `openviking_plugin` | 1 | `memory_providers` |
| `perf_guards` | 1 | no slug |
| `security` | 1 | no slug |

## Slugs with no dedicated Python module

- `deliverable`: no path contains `deliverable`. `agent/verification_evidence.py`, `agent/verify/`, and `tools/working_diff.py` stay under no-slug or `file_terminal`. They are not labeled deliverable mode.
- `kanban_lanes`: no path contains `lane`. Inferred from names only, and also tagged `kanban`: `hermes_cli/kanban_swarm.py`, `hermes_cli/kanban_db_dispatch.py`, `gateway/kanban_watchers_dispatcher.py`.
- `kanban_fleet`: the only `fleet` paths are the updater (`hermes_cli/update_cmd_fleet*.py`, `update_fleet_scope.py`), and those are packaging, not multi-gateway kanban. Inferred product paths, also tagged `gateway`: `hermes_cli/gateway_multiplex_mode.py`, `gateway_multiplex_s6.py`, `gateway_multiplex_served.py`, and `gateway/stream_consumer_fences.py`.
- `language_packs`: no `locales/` Python package. The modules are `agent/i18n.py`, `agent/i18n_languages.py`, `agent/i18n_layers.py`, `hermes_cli/config_language.py`, `hermes_cli/plugin_validate_locales.py`, and the TUI i18n contracts and methods.

## Product paths with no slug

Video generation, Google Meet, the Teams pipeline, observability metrics, security scanners, and host-layout detection have no row in `FEATURES.md`. Messaging Home Assistant (`plugins/platforms/homeassistant/`) is `platforms`, also `home_assistant`. The tool `tools/homeassistant_tool.py` is `home_assistant`. `gateway/wake.py` is `gateway`, not `wake_word`.

- `(repo root)`: 23
- `agent/`: 25
- `tools/`: 8
- `hermes_cli/`: 28
- `plugins/`: 23
- `hermes_platform/`: 9

