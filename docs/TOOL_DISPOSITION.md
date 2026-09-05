# TOOL DISPOSITION — F-41 proposals (not applied to the live ledger)

**Generated** 2026-08-31T11:56:45+00:00 by `tool-disposition`. This document is a rebuildable projection of `cosmos_port_plan.PORT_DECISIONS` against the live ToolContracts report. **It is not a disposition.** Applying these rulings to `live/ledger/authority.jsonl` is the Orchestrator's door.

## Counts

- plan total: **35**
- live total: **143**
- apply-ready: **27** (`backup_watchdog`, `bootup`, `bts_bus`, `bts_cop`, `bts_drive_health`, `bts_dymon`, `bts_elevated_ops`, `bts_gem`, `bts_gw`, `bts_identity`, `bts_node`, `bts_oa_api`, `bts_policy`, `bts_poller`, `bts_serve`, `bts_sgh`, `bts_spend`, `bts_watchdog`, `corrections`, `mesh_fanout`, `rail_check`, `scars`, `task_registry`, `tidyup`, `tools_sync`, `verify_conf`, `verify_pointers`)
- by kind: `{"DECLARE_READY": 8, "DRIFT": 1, "PLAN_MATCH": 7, "PLAN_READY": 19, "UNPLANNED": 116}`
- by action: `{"APPLY": 19, "DECLARE_AND_APPLY": 8, "HOLD": 117, "SKIP": 7}`
- live projection: `{"REPLACED": 8, "UNDECIDED": 135}` verified_true=0

## Ready to apply (scratch ledger only)

| name | plan | successor | kind |
|---|---|---|---|
| `backup_watchdog` | REPLACED | `cosmos_backup + cosmos_surfaces` | DECLARE_READY |
| `bootup` | REPLACED | `cosmos_session` | DECLARE_READY |
| `bts_bus` | REPLACED | `cosmos_mail + cosmos_sched + cosmos_health` | PLAN_READY |
| `bts_cop` | REPLACED | `cosmos_spend` | PLAN_READY |
| `bts_drive_health` | ADAPTED | `cosmos_surfaces` | PLAN_READY |
| `bts_dymon` | REPLACED | `cosmos_mail + cosmos_sched + cosmos_health` | PLAN_READY |
| `bts_elevated_ops` | ADAPTED | `—` | PLAN_READY |
| `bts_gem` | ADAPTED | `cosmos_rails` | DECLARE_READY |
| `bts_gw` | ADAPTED | `cosmos_rails` | PLAN_READY |
| `bts_identity` | REPLACED | `cosmos_identity` | DECLARE_READY |
| `bts_node` | REPLACED | `cosmos_mail + cosmos_sched + cosmos_health` | PLAN_READY |
| `bts_oa_api` | ADAPTED | `cosmos_rails` | PLAN_READY |
| `bts_policy` | REPLACED | `cosmos_spend` | PLAN_READY |
| `bts_poller` | REPLACED | `cosmos_mail + cosmos_sched + cosmos_health` | PLAN_READY |
| `bts_serve` | REPLACED | `cosmos_service` | DECLARE_READY |
| `bts_sgh` | ADAPTED | `cosmos_rails` | DECLARE_READY |
| `bts_spend` | REPLACED | `cosmos_spend` | DECLARE_READY |
| `bts_watchdog` | REPLACED | `cosmos_mail + cosmos_sched + cosmos_health` | PLAN_READY |
| `corrections` | ADAPTED | `cosmos_context` | PLAN_READY |
| `mesh_fanout` | REPLACED | `cosmos_crucible` | PLAN_READY |
| `rail_check` | REPLACED | `cosmos_registry + cosmos_rails` | PLAN_READY |
| `scars` | ADAPTED | `cosmos_context` | PLAN_READY |
| `task_registry` | REPLACED | `cosmos_sched` | PLAN_READY |
| `tidyup` | REPLACED | `cosmos_session` | DECLARE_READY |
| `tools_sync` | ADAPTED | `cosmos_context` | PLAN_READY |
| `verify_conf` | REPLACED | `cosmos_validate` | PLAN_READY |
| `verify_pointers` | REPLACED | `cosmos_validate` | PLAN_READY |

## Held

| name | kind | live | plan | why |
|---|---|---|---|---|
| `bts_cursor` | DRIFT | REPLACED | ADAPTED | cosmos_rails ApiRail adapter (Cursor link driver), dispatchable from a queue lan |

UNPLANNED HOLD rows (card review owed, no invented ruling): **116**.

## UNPLANNED cards (HOLD — not a ruling)

- card count: **116**
- with successor_candidates (evidence only): **47**
- with no name-overlap on disk: **69**

| name | live | successor_candidates |
|---|---|---|
| `apply_plans` | UNDECIDED | — |
| `bench_drive` | UNDECIDED | `cosmos_drive_meter`, `cosmos_motif_driver` |
| `bfast` | UNDECIDED | — |
| `bts` | UNDECIDED | — |
| `bts_bench` | UNDECIDED | — |
| `bts_billing` | UNDECIDED | — |
| `bts_board` | UNDECIDED | — |
| `bts_calibrate` | UNDECIDED | — |
| `bts_capacity` | UNDECIDED | — |
| `bts_chanbench` | UNDECIDED | — |
| `bts_claude` | UNDECIDED | `cosmos_claude_rail` |
| `bts_conductor` | UNDECIDED | — |
| `bts_creditprobe` | UNDECIDED | — |
| `bts_daemon` | UNDECIDED | `cosmos_bucket_daemon`, `cosmos_dispatcher_daemon` |
| `bts_deadline` | UNDECIDED | — |
| `bts_discovery` | UNDECIDED | `cosmos_discover` |
| `bts_docindex` | UNDECIDED | `cosmos_index` |
| `bts_doctor` | UNDECIDED | — |
| `bts_drivebench` | UNDECIDED | — |
| `bts_gate` | UNDECIDED | — |
| `bts_gdxbench` | UNDECIDED | — |
| `bts_gemini_cli` | UNDECIDED | `cosmos_mcp_client` |
| `bts_launch` | UNDECIDED | — |
| `bts_licwatch` | UNDECIDED | — |
| `bts_meters` | UNDECIDED | — |
| `bts_mtl` | UNDECIDED | — |
| `bts_mux` | UNDECIDED | — |
| `bts_oa` | UNDECIDED | — |
| `bts_oagrab` | UNDECIDED | — |
| `bts_odx` | UNDECIDED | — |
| `bts_office` | UNDECIDED | — |
| `bts_orchestrator` | UNDECIDED | `cosmos_orchestrator` |
| `bts_quota` | UNDECIDED | — |
| `bts_registry` | UNDECIDED | `cosmos_registry` |
| `bts_review` | UNDECIDED | — |
| `bts_route` | UNDECIDED | — |
| `bts_schemas` | UNDECIDED | — |
| `bts_selfaudit` | UNDECIDED | — |
| `bts_snapshot` | UNDECIDED | — |
| `bts_spend_gate` | UNDECIDED | `cosmos_spend`, `cosmos_spend_admin`, `cosmos_spend_meter`, `cosmos_spendguard` |
| `bts_state` | UNDECIDED | — |
| `bts_surfaces` | UNDECIDED | `cosmos_surfaces` |
| `bts_sync` | UNDECIDED | — |
| `bts_watcher` | UNDECIDED | — |
| `codex_config_fix` | UNDECIDED | `cosmos_codex_rail` |
| `collect_sessions` | UNDECIDED | `cosmos_collector`, `cosmos_collector_dhx`, `cosmos_session` |
| `crossref` | UNDECIDED | — |
| `crucible_method` | UNDECIDED | `cosmos_crucible` |
| `crucible_verify_record` | UNDECIDED | `cosmos_crucible`, `cosmos_ledger_verify` |
| `dash` | UNDECIDED | `cosmos_kdash` |
| `dedupe_corpus` | UNDECIDED | `cosmos_up` |
| `dedupe_transcripts` | UNDECIDED | `cosmos_up` |
| `demo_roundtrip` | UNDECIDED | — |
| `disk_guard` | UNDECIDED | `cosmos_spendguard` |
| `domain_assay` | UNDECIDED | `cosmos_dom` |
| `drive_inventory` | UNDECIDED | `cosmos_drive_meter`, `cosmos_motif_driver` |
| `drop_old_mcp_key` | UNDECIDED | `cosmos_mcp`, `cosmos_mcp_client` |
| `fanout_review` | UNDECIDED | — |
| `figdig` | UNDECIDED | — |
| `find_in_mail` | UNDECIDED | `cosmos_mail` |
| `fire_one_rail` | UNDECIDED | `cosmos_claude_rail`, `cosmos_codex_rail`, `cosmos_cursor_rail`, `cosmos_firecrawl_rail`, `cosmos_node_rails`, `cosmos_playwright_rail`, `cosmos_rail_base`, `cosmos_rails`, `cosmos_rails_prober` |
| `fix_rails` | UNDECIDED | `cosmos_node_rails`, `cosmos_rails`, `cosmos_rails_prober` |
| `fix_stale_dates` | UNDECIDED | — |
| `gdx` | UNDECIDED | — |
| `gdx_fresh_auth` | UNDECIDED | — |
| `gem` | UNDECIDED | `cosmos_gem_bucket_worker`, `cosmos_gem_worker` |
| `glossary` | UNDECIDED | — |
| `handoff_guard` | UNDECIDED | `cosmos_spendguard` |
| `identity` | UNDECIDED | `cosmos_identity` |
| `index_sessions` | UNDECIDED | `cosmos_index`, `cosmos_session` |
| `legal_tree` | UNDECIDED | — |
| `maint_sweep` | UNDECIDED | — |
| `mcp` | UNDECIDED | `cosmos_mcp`, `cosmos_mcp_client` |
| `mesh_test` | UNDECIDED | — |
| `ocr_backlog` | UNDECIDED | — |
| `odx_probe` | UNDECIDED | `cosmos_rails_prober` |
| `opjreader` | UNDECIDED | — |
| `originexport` | UNDECIDED | — |
| `pandoc` | UNDECIDED | — |
| `parallel_jobs` | UNDECIDED | — |
| `pdais_stage5` | UNDECIDED | — |
| `publish_nightly` | UNDECIDED | — |
| `qa_handoff` | UNDECIDED | — |
| `r2publish` | UNDECIDED | — |
| `rail_check_task` | UNDECIDED | `cosmos_claude_rail`, `cosmos_codex_rail`, `cosmos_cursor_rail`, `cosmos_firecrawl_rail`, `cosmos_node_rails`, `cosmos_playwright_rail`, `cosmos_rail_base`, `cosmos_rails`, `cosmos_rails_prober` |
| `record_add_exhibits` | UNDECIDED | — |
| `record_reindex` | UNDECIDED | `cosmos_index` |
| `record_trim` | UNDECIDED | — |
| `rfa_review` | UNDECIDED | `cosmos_surfaces` |
| `route_gate` | UNDECIDED | — |
| `runner_doctor` | UNDECIDED | `cosmos_run`, `cosmos_runner` |
| `runner_repair` | UNDECIDED | `cosmos_run`, `cosmos_runner` |
| `sgh` | UNDECIDED | — |
| `sng_ask` | UNDECIDED | — |
| `sort_sessions` | UNDECIDED | `cosmos_session` |
| `spectra_index` | UNDECIDED | `cosmos_index` |
| `spendgate_wrapper_controls` | UNDECIDED | `cosmos_control`, `cosmos_spend` |
| `strip_transcript` | UNDECIDED | — |
| `sweep_corpus` | UNDECIDED | — |
| `test_bts_bus` | UNDECIDED | — |
| `test_integration` | UNDECIDED | — |
| `test_mesh_v2` | UNDECIDED | — |
| `test_watcher` | UNDECIDED | — |
| `tidy_transcripts` | UNDECIDED | — |
| `tidyup2_checks` | UNDECIDED | `cosmos_up` |
| `tidyup2_full` | UNDECIDED | `cosmos_up` |
| `tidyup2_hand` | UNDECIDED | `cosmos_up` |
| `toml_guard` | UNDECIDED | `cosmos_spendguard` |
| `tools` | UNDECIDED | `cosmos_tools` |
| `usb_link` | UNDECIDED | — |
| `verify_citations` | UNDECIDED | `cosmos_ledger_verify` |
| `verify_gemini_cli` | UNDECIDED | `cosmos_ledger_verify`, `cosmos_mcp_client` |
| `verify_quotes` | UNDECIDED | `cosmos_ledger_verify` |
| `wargame` | UNDECIDED | — |
| `wargame_bundle` | UNDECIDED | — |
| `wargame_feed` | UNDECIDED | `cosmos_cdeck_feed` |

Cards are HOLD. A candidate is evidence a cosmos_ module exists whose name overlaps; it is NOT a ruling. PORT_DECISIONS is the only place a ruling is recorded, and that module is outside this fence.

Apply: `py -3.14 builds/probe/tool_disposition.py --root <live> --apply --ledger <scratch.jsonl>` — LIVE_LEDGER_FORBIDDEN on authority.jsonl.
