# Core P–R

This slice is not a finished product. COSMOS is not finished. This page is a reading map of the 34 modules under `cosmos/` whose names start with `cosmos_p`, `cosmos_q`, or `cosmos_r`. It names the public surface and the errors a read of that source shows. It does not paste function bodies, does not run the modules, and does not claim a green self-test.

Private helpers (names that start with `_`) are omitted. `main` is listed when it is a public function. A CLI with no `--selftest` often exits `2`. That exit is a usage refusal, not a domain error.

Two names collide inside this slice. `cosmos_rails.RailError` and `cosmos_rail_base.RailError` are different classes with different `kind` sets. Importing both into one namespace keeps only one of them. `cosmos_refusals` is the reader that derives kinds from raise sites. The notes below are a reading of these files, not a regenerated taxonomy. Several class docstrings list kinds the module returns in a record, or never raises, and some omit a kind the code does raise. Branch on the class and the `kind` together.

## `cosmos_p06_compare.py`

Compare box$ seating against token$ seating only after real porosity observations exist.

Public: `seating_family`, `assert_distinct_seating_families`, `compare_box_token`.

Errors: `PorosityError` `REFUSED` for a rotator id or a same-family double-seat (Sol and Luna share one family). Zero observation rows stay `UNMEASURED` and do not run a pair fold, coverage, or a bake-off. No local exception class. Does not write fake observation rows.

## `cosmos_packet.py`

Hash a tool-output body and keep a short preview. The bytes go in the existing content-addressed store under the `state` role (`state/cas`). Not a second store and not a Headroom product.

Public: `cas_dir`, `packetize`, `retrieve`.

Errors: no local exception class. `packetize` with no destination is `UNMEASURED` and does not create a directory. An `OSError` on write is also `UNMEASURED`, and the exception text is dropped. `retrieve` returns `None` for a missing destination, a hash that is not 64 hex characters, a missing file, or an unreadable file. Those four misses look the same.

## `cosmos_paths.py`

The path resolver. One configured root, checked by sentinel content, not by the fact that a directory exists.

Public: `CosmosPathError`, `Sentinel`, `extended`, `CosmosPaths` (`from_install_record`, `role`, `root`, `walk`), `write_sentinel`. Role names also work as methods (`paths.ledger(...)`) through attribute lookup. Unknown attributes raise `AttributeError`.

Errors: `CosmosPathError` kinds that are raised: `NOT_FOUND` (root missing, install record missing, unknown role), `NOT_A_DIRECTORY`, `UNREADABLE`, `UNPARSEABLE`, `IDENTITY_MISMATCH` (no sentinel, wrong `system`, wrong `tree_id`, a role part that is absolute or contains `..`, or a resolved path that leaves the root). The class text says "four facts, four values" and then names five kinds. Traversal is filed as `IDENTITY_MISMATCH`, which is a different fact from a wrong tree. Construction refuses to guess a root.

## `cosmos_pause.py`

One reader for `state/control/PAUSE.flag`. HOLD does not clear itself. A resume gate may unlink at `auto_resume_at`.

Public: `pause_path`, `read_pause_flag`, `classify_pause`, `is_paused`, `maybe_auto_resume`.

Errors: no exception type. An unreadable flag is still `PAUSED`, with `read_error` set. An unrecognised `mode` classifies as `HOLD`. A missing or unparseable `auto_resume_at` stays paused. An `OSError` on unlink stays paused. `HOLD`, `GATE`, and `ARM` all count as paused for new work.

## `cosmos_peeking.py`

Dual-lane build rule: a lane must not read its sibling workspace, and there is no ballot writer.

Public: `PeekingError`, `assert_no_peek`, `assert_prompt_no_peek`, `refuse_ballot`.

Errors: `PeekingError` `BAD_LANE` (same workspace, or a path that cannot be resolved), `PEEKING_VIOLATION` (sibling path in a read or named in a prompt), `NO_BALLOT_WRITER` (`refuse_ballot` always raises that).

## `cosmos_pilot.py`

Propose-only transcript for the Pilot seat. GET and POST for `/api/v1/pilot`. It does not spawn a model and does not write the COSMOS tree.

Public: `PilotError`, `snapshot`, `post_turn`.

Errors: `PilotError` `BAD_STREAM`, `BAD_TAIL`, `BAD_REQUEST`, `EMPTY`, `TOO_LONG`, `ORC_REPLY_REFUSED`, `PEN_REFUSED`. A missing transcript file is `UNMEASURED`, not a measured empty thread. ORC replies are not a request field.

## `cosmos_platform.py`

The only process and text-encoding adapter. Argv lists, no shell. UTF-8 on both ends. A timeout is recorded. It is not treated as a clean kill.

Public: `PlatformError`, `run`, `run_tree_killed`, `write_text_lf`, `write_text_crlf`, `makedirs`.

Errors: the class text names `TIMEOUT`, `SHELL_REFUSED`, and `KILL_INCOMPLETE`. The only kind raised is `SHELL_REFUSED` (a string command). Timeout is a return record: `timed_out` true, `rc` null, `kill_result` set. `KILL_INCOMPLETE` is a suffix on that string when the child does not reap within 10 seconds. It is not a raised kind.

## `cosmos_playwright_rail.py`

Satellite DOM rail `playwright-dom`. Interact (navigate and snapshot), pinned package, not the cheap dump-dom read. Attaching to the authority ledger is refused unless boot compose is on.

Public: `PlaywrightRailError`, `default_spec`, `merge_spec`, `load_spec`, `write_spec`, `find_pinned_cli`, `write_mcp_config`, `spawn_argv`, `PlaywrightRail` (`last_identity`, `close`, `probe`, `dispatch`), `spec_path_for`, `probe_path_for`, `register_playwright_rail`, `attach_to_kernel`, `refuse_live_authority_attach`, `inspect_live_kernel`, `gate`, `main`.

Errors: raised `PlaywrightRailError` kinds are `BAD_SPEC` (package pin, browser, schema, rail type, unreadable or unparseable spec) and `REFUSED` (authority attach while boot compose is false). The class text also names `BAD_ROOT`, `UNREACHABLE`, `BROKE`, and `DENIED`. Those are not raised as `PlaywrightRailError` in this file. `BAD_ROOT` is a CLI record when `--root` is missing. `BROKE` and `UNREACHABLE` are dispatch and probe records (`file://` is `BROKE`). `DENIED` is an `McpClientError` from the MCP client when an unsafe tool is called, not this class.

## `cosmos_pool.py`

Pull supervisor plus N drain workers and one fast slot. Do not run it beside `cosmos_run` on the same queue. Both claim jobs.

Public: `worker_id_for`, `slot_lock_name`, `slot_heartbeat_name`, `slot_log_name`, `plan_slots`, `slot_spec`, `bind_worker`, `run_worker`, `spawn_worker`, `supervise`, `status_view`, `install_task`, `standup`, `main`.

Errors: `ValueError` for `n < 1` or an unknown slot. `CosmosPathError` `NOT_FOUND` when `config/install_key.bin` is missing. The pool does not invent a key. Spawn and scheduled-task failures come back as records with `ok` false. A slot lock that is already held refuses a second worker rather than double-claiming.

## `cosmos_porosity.py`

Hole size, hole distribution, and pair orthogonality for seated models. Observations append. The SQLite file is a rebuildable index. Scores are not invented.

Public: `PorosityError`, `normalize_quality`, `store_dir`, `obs_path`, `db_path`, `axes_for`, `empty_snapshot`, `load_obs`, `compare_snapshot`, `recommend_call`, `compare_pack`, `record_hit_vectors`, `record_pair`, `hook_trial`, `hook_returns`, `recommend`, `pair_matrix`, `coverage`, `snapshot`.

Errors: `PorosityError` `BAD_INPUT` (missing model, bad boolean, unknown source, unknown `who_erred`, unequal hit strings, a pair that is not two models) and `REFUSED` (rotator id, or two names that are not distinct). Empty or unseen folds are `UNMEASURED`. A missing error magnitude stays unmeasured even when disagreement frequency is measured. GET paths do not create the store.

## `cosmos_port_plan.py`

Recorded port ruling for each incumbent BTS tool: preserved, adapted, replaced, or abandoned. `UNDECIDED` is the absence of a ruling, not a fifth ruling.

Public: `apply`, `summary`.

Errors: no local exception class. `apply` catches `ToolsError` and skips only `DUPLICATE`. Any other `ToolsError` is re-raised. An `UNDECIDED` tool is declared and gets no disposition event. `summary` counts from `PORT_DECISIONS`, not from a remembered total.

## `cosmos_portfolio_attribution.py`

Canonical product and stage tags for new evidence. Spend folded by those tags. Untagged spend is not filled in as zero.

Public: `AttributionError`, `catalog_product_ids`, `normalize_product`, `normalize_stage`, `optional_tags`, `read_tags`, `porosity_optional_tags`, `empty_product_spend_totals`, `fold_spend_by_product`, `parse_work_order_tags`.

Errors: `AttributionError` `BAD_INPUT` (product or stage outside the catalog) and `PARTIAL` (one of product or stage present and the other omitted). Catalog products with no tagged settles stay `UNMEASURED` with a null dollar figure. Tags are not inferred from command text.

## `cosmos_prepaid_orch.py`

Second orchestrator tick on a prepaid rail. The winner rail is Grok. Claude is not invoked.

Public: `PrepaidOrchError`, `repo_tree`, `spawn_argv`, `refuse_rail`, `bind`, `cow_fresh`, `open_prepaid_orders`, `poll_once`, `plan_task_argv`, `install_task`, `standup`, `main`.

Errors: raised kinds are `CLAUDE_SPEND` and `NO_RAIL`. The class text also names `NO_ROOT` and `HOLD`. Those are records: `NO_ROOT` is printed by `main` when the root will not resolve, and `HOLD` is a poll state when pause classifies as hold. A scheduled-task spawn failure is `ok` false. This module does not start Claude.

## `cosmos_principles.py`

The Cm-stream principles as checks that return a status and evidence. The TOML beside this file is the canon text the checks read. This page does not restate that file.

Public: `load`, `activity_clock_15s`, `pause_formal`, `resume_gate`, `no_bts_imports`, `anti_loss_daemons`, `self_build_process`, `keep_afloat`, `improvement_not_bloat`, `orchestrator_only`, `agents_propose_only`, `prompt_cache_prefix`, `pen_disables_other_writers`, `gitur_then_judge`, `audit`, `main`.

Errors: no exception class. Status strings declared at the top are `PASS`, `FAIL`, `UNPROVEN`, and `NA`. `anti_loss_daemons` is `UNPROVEN` unless both the collector and runner heartbeats are fresh and the handoff mentions reconcile. `improvement_not_bloat` can return `WATCH` when line count grew. `WATCH` is not one of the four declared statuses. A broken baseline file is treated as no baseline. The check creates `state/principles` and writes the baseline. That is a write inside an audit.

## `cosmos_profiles.py`

Occupancy skins and the per-profile MOTIF engine document.

Public: `ProfileError`, `motif_skin_tabs`, `skin_tabs_for`, `dir_for`, `engine_path`, `dest_via_gitur`, `catalog`, `default_dest`, `default_step_setup`, `default_engine`, `load_engine`, `save_engine`, `snapshot`.

Errors: `ProfileError` `BAD_INPUT` (unknown profile, unknown destination, body not an object, define not text, unknown stage) and `REFUSED` (define text over the length cap). The class text also names `BROKE`. A saved engine that cannot be read, or that is not an object, is returned with `kind` `BROKE`. It is not raised. Save can re-raise `ProfileError` with the kind it already caught.

## `cosmos_publish_stage.py`

Copy the MOTIF public pack from `docs/publish` into an existing `live/publish`. It does not post, and it does not flip GitHub visibility.

Public: `stage`, `main`.

Errors: `RuntimeError` with a fixed message for a missing `docs/publish`, for a missing `live/publish` (it will not create that directory), and for a missing pack file. Nested preview files may create directories under the destination that already exists. No typed `kind`.

## `cosmos_pulse.py`

Fifteen-second pulse. It collects results even under HOLD, writes a shadow heartbeat of the clock due-set, and does not claim the queue or dispatch MOTIF.

Public: `PulseError`, `poll_once`, `loop`, `main`.

Errors: `PulseError` `CLOCKS_SHRUNK` when the due-set is not 26 clocks or the clock names are not unique. Collector and cDeck-feed failures inside a poll are records with `ok` false and `error` set to the exception type and text. They do not abort the tick by themselves. HOLD is not cleared here. The watchdog shim is off unless asked, so this pulse does not race a live watchdog heartbeat.

## `cosmos_query_channel.py`

One-shot list of open query files. Channel 1 of three. No model spawn and no second daemon.

Public: `queries_dir`, `replies_dir`, `once`, `main`.

Errors: no exception class. A missing queries directory is `UNMEASURED` with `ok` true, and the directory is not created. A query file that is unreadable, not JSON, or not an object is skipped. It is not an error row, so a corrupt file disappears from both the open count and the answered count. CLI without `--once` or `--root` exits `2`.

## `cosmos_rail_base.py`

Shared rail seam: authority-ledger check, secret-stripped probe records, and the seam-wide refusal type. Vendor rails are expected to subclass this `RailError`, not the one in `cosmos_rails`.

Public: `RailError`, `ledger_is_authority`, `write_probe_record`, `selftest`.

Errors: documented kinds are `NO_KEY`, `BAD_SPEC`, `BAD_ROOT`, `UNREACHABLE`, `BROKE`, `REFUSED`. The raise a read of the public helpers shows is `BROKE` from the private process runner when the command is a string. Other kinds are the contract for subclasses. `ledger_is_authority` returns false when it cannot prove the ledger is `authority.jsonl`. It does not raise. `write_probe_record` drops known secret field names and creates the parent directory. A secret under another name is not stripped.

## `cosmos_rail_guard.py`

Approval gate in front of dangerous coding-rail actions. Other kinds run straight through.

Public: `maybe_guard`.

Errors: no local exception class. Kinds sent to the gate are `shell`, `git`, `file_write`, `file_delete`, and `install`. Refusals are `ApprovalError` from `cosmos_approval`: `HARDLINE` (the action does not run) and `NEEDS_APPROVAL` (confirm needs a captain nonce). Anything else is not guarded.

## `cosmos_rails.py`

CLI, DOM, and API adapters plus a dispatcher. DOM-first is registry policy. A dead DOM link is a typed failure, not a silent jump to API.

Public: `RailError`, `CliRail` (`probe`, `dispatch`), `DomRail` (`probe`, `dispatch`), `ApiRail` (`probe`, `dispatch`), `Dispatcher` (`dispatch`).

Errors: this `RailError` (not the seam class) raises `NO_LIVE_LINK`, `UNPRICED_METERED`, `UNGATED_METERED`, `NOT_PERMITTED` (the spend gate refused; the call did not run), and `RAIL_FAILED` (the rail raised after the gate allowed it, or the result was not ok and not an audited fallback). Fallback continues only for result kinds `UNREACHABLE`, `SESSION_EXPIRED`, and `AUTH_REQUIRED`, and that skip is ledgered. A missing adapter is skipped. `wallet=api` with no positive price, or with no spend gate, refuses before the call. Zero is not a price.

## `cosmos_rails_prober.py`

One-minute freshness satellite and, only when asked, a live proof of wired rails. `--once` does not dispatch a rail.

Public: `probe_module_for`, `default_live_call`, `open_registry`, `map_wired_nodes`, `poll_once`, `standup`, `main`.

Errors: no local exception class. `open_registry` returns `None` when the install key is missing. It does not invent a key. A live call that fails returns `ok` false and `rc` 2. A node that does not answer is not registered. Proof still needs a non-empty body and a name for what answered. An empty registry directory is not identity.

## `cosmos_recall.py`

Cross-session search over a SQLite projection of conversation records on the authority ledger. The index is not the record. Delete it and rebuild.

Public: `RecallError`, `Recall` (`refresh`, `rebuild`, `state_sha`, `search`).

Errors: `RecallError` `BAD_QUERY` (no searchable terms), `NO_FTS5` (this SQLite has no FTS5), `TRUNCATED` (the ledger is shorter than the index checkpoint). `search` on a missing index, or on a checkpoint that cannot be read, returns `kind` `UNMEASURED` and `results` null. It does not create the file. An unknown owner and a foreign owner look the same. `captain:*` is the principal that searches every session.

## `cosmos_recall_clock.py`

Native scheduled task that refreshes the recall index. Not an in-process loop.

Public: `once`, `standup`, `main`.

Errors: `once` can raise `RecallError` from the index. `main` prints that as `ok` false with the `kind` and exits `2`. `standup` does not claim `registered` true when elevation is denied. The task name is `COSMOS Recall Refresh`. Already registered returns `started` `already`.

## `cosmos_refusals.py`

Read-only survey of `*Error(kind, detail)` raise sites. The markdown it prints is a projection. The source is the taxonomy.

Public: `survey`, `render_table`, `selftest`, `main`.

Errors: no domain exception class. It parses source and does not import the modules it surveys. It reports kind collisions, kinds a docstring names but the module never raises, and kinds a module raises but does not document. It does not decide which collision is safe. A path you do not pass is not written.

## `cosmos_registry.py`

Nodes, rails, and links as ledger events. A registration is a claim. A probe is a dated measurement. The JSON under the registry role is a projection.

Public: `proof_ok`, `RegError`, `Registry` (`register`, `attach_probe`, `probe`, `prove`, `live_nodes`, `stale_nodes`, `file_runtime`, `probe_all`, `state`, `matrix`, `route`).

Errors: `RegError` `BAD_TYPE` (rail type not in CLI, API, DOM, CHAT, OTHER), `UNKNOWN_LINK`, `NO_PROBE`. `prove` does not raise when the live call fails or is not a dict. It records the measurement and registers only when `proof_ok` passes: `ok`, return code 0, non-empty body, non-empty model or responder name. Stale proofs drop out of `live_nodes` and are named by `stale_nodes`. Freshness and the prober TTL are separate constants pinned equal by a test, not by an import.

## `cosmos_resession.py`

Satellite that notices the orchestrator window filling, closes through the session CLI, arms the resume gate, and can spawn a fresh Grok session. It does not restart Core and it does not spawn Claude.

Public: `ResessionRefusal`, `precheck_seed`, `watermark`, `warn_flag_path`, `read_warn_latched`, `latch_warn`, `mint_session_id`, `spawn_argv`, `resolve_grok`, `spawn_inject_argv`, `spawn_tui_argv`, `doors_catalog_path`, `installed_doors`, `plan_resession`, `wmi_create`, `spawn_auto_resession`, `close_banner`, `resume_plan`, `cosmos_tu2`, `render_running_session`, `write_running_session`, `unique_stamp`, `write_session_save`, `transcript_path`, `arm_gate_flag`, `decide`, `read_json`, `pid_is_alive`, `sha256_file`, `tick`, `poll_once`, `standup`, `plan_task_argv`, `install_task`, `main`, `selftest`.

Errors: the class text lists `HOLD`, `NO_SEED`, `NO_DECL`, `BAD_SEED`, `IDENTITY_MISMATCH`, `NO_PROMPT`, `HELD`, `CLOSE_REFUSED`, and `NO_RAIL`. Raised kinds in this file are `NO_RAIL` and `ANTHROPIC_OFF`. `ANTHROPIC_OFF` is not in that docstring list. `CLOSE_REFUSED` is named and never used. `NO_SEED`, `NO_DECL`, `BAD_SEED`, and `IDENTITY_MISMATCH` are fields on the pre-check record. `HOLD`, `NO_PROMPT`, and `HELD` are fields on the decision record. Seed authenticity stays in `cosmos_session`. This module does not reimplement the HMAC. A thin seed is reported as thin, not as corrupt. `main` prints `NO_ROOT` when the root is missing. That string is not a `ResessionRefusal` kind. Spawn failures return `ok` false. A non-zero scheduled-task registration is reported, not swallowed.

## `cosmos_review.py`

GET fold for the Review pane: approvals, blocking decisions, logins, and a catalog of recent work. It does not mutate and it does not copy files into the COSMOS tree.

Public: `snapshot`.

Errors: no exception class. Missing sources are `NO_SOURCE`. A broken read is `BROKE` with the exception type in the row. A missing human-in-the-loop artifact is `MISSING_HITL_ARTIFACT`. Login gaps are `AUTH_REQUIRED`. The OpenWork database path and the sample product paths are absolute paths on one workstation. A missing file stays missing. It is not imported. A window name that is not day, week, month, or 90 does not widen the catalog.

## `cosmos_rold_index.py`

Pointer index for seats, credentials, and demonstrated skills. A row is a path, a name, and a time. The body stays in the file the path names.

Public: `RoldIndexError`, `refuse_if_secret`, `ensure_entry`, `note`, `lookup`, `index_seat`, `index_credential`, `index_skill`.

Errors: `RoldIndexError` `SECRET` (a credential value, or a string that looks like a secret), `ESCAPE` (the name leaves the ROLD root), `BROKE` (the row file is not a list, or cannot be parsed), `NO_ROLD`, `BAD_KIND`, `BAD_ROW`, `NO_TARGET` (the path does not exist). The index does not read a credential file and does not store the secret.

## `cosmos_route_variant.py`

OpenRouter routing suffixes (`:nitro`, `:floor`, `:exacto`) change provider order only. They are not catalog rows. The saved default priority is `:floor`.

Public: `RouteVariantError`, `routing_path`, `catalog_id`, `request_model`, `load_routing`, `set_routing`.

Errors: `RouteVariantError` subclasses `Exception`, not `RuntimeError`, so a handler that only catches `RuntimeError` will miss it. Kinds: `BAD_MODEL`, `DEPRECATED` (`:online`), `BAD_SUFFIX`, `BAD_PRIORITY`, `UNPARSEABLE`, `UNREADABLE`. `routing_path` creates `state/openrouter` if it is missing. That is a mkdir on a path helper, unlike the GET-never-mkdir modules in this slice.

## `cosmos_run.py`

This install's queue drain daemon. Jobs run through `cosmos_runner.Runner`. A heartbeat file is the liveness signal. Do not run it beside the pool.

Public: `pythonw_exe`, `plan_loop_argv`, `plan_task_argv`, `query_task`, `bind`, `read_heartbeat`, `heartbeat_age_s`, `status_view`, `acquire_lock`, `spawn_wmi`, `spawn_popen_detached`, `spawn_detached`, `install_task`, `wait_fresh`, `loop`, `standup`, `main`.

Errors: `CosmosPathError` `NOT_FOUND` when the install key is missing. Task query and spawn failures are records with `ok` false. A lock that is already held and a heartbeat that is not fresh exit `2` instead of starting a second loop. The loop writes a traceback and then re-raises. A child of this process is not used as the daemon. It would die with the job.

## `cosmos_run_spend.py`

One spend line for the WOMB board. Dollars come from the stored Model Rater price table. No per-reply call to OpenRouter.

Public: `db_path`, `approx_tokens`, `store_price_table`, `quote_run`.

Errors: no exception class. Token counts are a local characters-over-4 estimate until a vendor usage object is present (`token_kind` `MEASURED` versus the estimate). A missing price or a vendor cost that is not a number is `cost_kind` `UNMEASURED` and `usd` null. It is not zero. A priced estimate is `ESTIMATE`.

## `cosmos_runner.py`

The executor. One attempt directory per job. The log opens with `RUNNING` and the argv before the process starts.

Public: `Runner` (`run_one`, `drain`, `write_heartbeat`, `poll_once`, `drain_loop`).

Errors: no local exception class. Worded outcomes are `CLEAN` (return code 0), `FINDINGS` (return code 2), and `BROKE` (anything else, a timeout, a helper-prefixed script, or a path outside the tools root and this runner's work root). `SchedError` `LOST_CLAIM` sleeps and continues. Any other `SchedError`, and any other exception in the drain, is written onto the heartbeat and then re-raised. Timeout uses `run_tree_killed`. The kill result is stored. It is not turned into `CLEAN`.

## `cosmos_runs_ops.py`

GET fold for the Runs column: watchdog, clocks, work orders, the CCR stream, recents, Gitur jobs, and spend. It does not mutate, create directories, or invent token counts.

Public: `snapshot`.

Errors: no exception class. A missing heartbeat is `NO_SOURCE` with a null age. Counts that were not measured stay absent. They are not filled with zero.

## What this read did not do

These 34 files were not imported and their self-tests were not run. A kind that appears only inside a string, or only in a docstring, is marked that way above. `cosmos_refusals.survey` is the check that will disagree with this page the moment a raise site changes. This slice is not a finished product.
