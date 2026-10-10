# Core S–Z

Reading map for `cosmos/cosmos_s*.py` through `cosmos/cosmos_z*.py`, plus `cosmos/cosmos.py`. Forty-five files. Names only. No function bodies.

This slice is not a finished product. A name here is not a claim that the route is bound, measured, or shipped. Typed refusals, `501`, and `UNMEASURED` are the code saying the thing is not there.

These files parsed. This read did not see a `SyntaxError`.

## `cosmos/cosmos_sandbox.py`

Attempt sandbox. Workers run under the attempt workspace, not on a host pen. The composed child is a Windows Job Object. Daytona and E2B are named transports.

Public: `SandboxError`. `load_backend_config`, `credentials_present`, `pick_backend`, `snapshot`, `assert_no_host_map`, `spawn_remote`, `spawn_backend`, `attempt_dir`, `assert_sandbox_cwd`, `spawn_in_job`, `attach_to_kernel`.

Errors: `SandboxError` kinds seen: `UNMEASURED`, `UNKNOWN_BACKEND`, `UNCONFIGURED`, `BACKEND_ISOLATION`, `NOT_COMPOSED`, `JOB_CREATE`, `JOB_LIMIT`, `HOST_PEN`, `JOB_ASSIGN`. `spawn_remote` does not open a vendor socket. No key is `UNCONFIGURED`. A key file still raises `UNMEASURED` ("live vendor call not bound"). Modal is named, not composed. `assert_no_host_map` is a recorded refuse, not a live mount audit. `snapshot` does not spawn.

## `cosmos/cosmos_sched.py`

Scheduler on the ledger: concurrency and priority as a property of queued work. The module docstring still calls this SPIKE 4.

Public: `SchedError`. `Scheduler` — `submit`, `queued`, `claim_next`, `done`, `report_stale`, `wait_for_submission`.

Errors: `SchedError` kinds `BAD_PRIORITY`, `BAD_STATE`, `UNKNOWN_JOB`, `LOST_CLAIM`.

## `cosmos/cosmos_scout.py`

Diffs the standing `NEW_AI_SCOUT` note against `MESH_ADDITIONS` files. It does not fetch the web.

Public: `poll_once`, `main`.

Errors: no error class in this file. "Went out" is kind `UNMEASURED`, not a live ranking.

## `cosmos/cosmos_segments.py`

Segmented ledger plus a content-addressed store, layered on `cosmos_ledger.Ledger`. Not a second ledger. A corrupt segment refuses and records an incident. Record hashes stay inside one segment. Cross-segment continuity is the anchor chain.

Public: `SegmentedLedger` — `segments`, `append`, `head_global_seq`, `incidents`, `verify_all`. `CAS` — `put`, `get`, `has`.

Errors: this file raises `LedgerError`, not its own type. Kinds seen: `BROKEN_CHAIN`, `NOT_FOUND`, `HASH_MISMATCH`, `UNREADABLE`, `FORGED`, `TORN`.

## `cosmos/cosmos_service.py`

The versioned HTTP API (stdlib). KDash, voice, and other clients are meant to use this one surface. Route names live in the module docstring. Handlers are nested inside `make_handler`. They are not module-level functions. `Handler` is not a public class.

Public: `record_work_order_picked`, `page_events`, `ServiceError`, `parse_loopback_trust`, `make_handler`. `Service` — `serve_background`, `shutdown`. The constructor takes the kernel plus host, port, tls, `cert_file`, `key_file`, `open_access`, and `insecure_http`.

Errors: `ServiceError` kinds `BLANK_TOKEN`, `TOKEN_MISSING`, `REMOTE_OPEN_ACCESS`, `REMOTE_CLEARTEXT`, `CERT_NOT_FOUND`. A remote bind with auth off is refused. A remote bind with no TLS is refused unless the insecure-HTTP trial flag is set, and that trial still cannot pair with open access. One bare `RuntimeError` string is `[NO_RAIL]` when no Grok rail is composed and the Opus brain did not answer.

Honest `501`s in this file, not hidden successes:

- `GET` and `POST /api/v1/seats` — `UNMEASURED`. No seats module.
- `POST /api/v1/chamber` and `POST /api/v1/temporal` — stay on that `501` table. GET reads. Join, `assert_fact`, and `invalidate` are not called.
- `POST /api/v1/xtalk` Transport A — `NOT_COMPOSED`. Transport B can append. Do not treat a missing inject as success.
- `POST /api/v1/crucible` — `CRUCIBLE_NOT_RUNNABLE` when no critic dispatchers are composed.

`POST /api/v1/spend` is the admin writer in `cosmos_spend_admin`, not a silent widen. The model-rater cap route says it is not the Core spend gate. Voice is hardened through `SpendGuard` before a model call. Control resume does not reset the day cap. The nested `log_message` is empty on purpose (quiet server), not a missing route.

This file re-exports `cosmos_voice_hardening` names, including the private BootUP helpers.

## `cosmos/cosmos_session.py`

Session lifecycle. Close is TidyUP: control files must parse and validate. Start is BootUP from the seed.

Public: `SessionError`, `project_live_session`, `bootup_path`, `read_bootup`, `require_bootup`. `SessionManager` — `open`, `validate_control_files`, `close_session`, `start_session`. Also module `close_session`, `start_session`, `require_bootup_kernel`.

Errors: `SessionError` kinds `NO_BOOTUP`, `ALREADY_OPEN`, `NOT_FOUND`, `BAD_STREAM`, `NO_SEED`, `BAD_SEED`, `IDENTITY_MISMATCH`, `CONTROL_INVALID`, `UNPARSEABLE`, `VERIFY_MISMATCH`. A `ContextError` kind `UNRESOLVED` is also raised from this file.

## `cosmos/cosmos_session_kit.py`

COS panes, autosave minutes, and auto-resession config. GET does not mutate or mkdir. POST writes the pack. Saving the kit does not fire TidyUP, a BU file, or a resession.

Public: `SessionKitError`, `pack_path`, `default_kit`, `load_kit`, `save_kit`, `snapshot`.

Errors: `SessionKitError` kind `BAD_INPUT`. Autosave minutes are only 5, 10, 20, or 30.

## `cosmos/cosmos_session_procedures.py`

Resession close, the ask ladder, autosave, and a learned-skill proposal. Order is TidyUP, then TidyUP2, then one BU file. Asks sit at 75, 80, and 85 percent. A live Grok session figure in this file is 190000 input tokens, not 92 percent. Compaction asks. It does not close. The clock does not close unless the caller passes `engage=True`.

Public: `SessionProcedureError`, `canon_pct`, `redact`, `ladder`, `pct_from_heartbeat`, `decide_rung`, `next_action`, `ask_path`, `read_ask`, `declined_set`, `write_ask`, `decline_rung`, `session_identity`, `bu_name`, `render_bu`, `tidyup_close`, `close_resession`, `autosave_tick`, `record_session_beat`, `maybe_autosave`, `render_skill`, `parse_skill_md`, `save_skill`, `promote_inbox`, `preview_rung`, `apply_rung`.

Errors: `SessionProcedureError` kinds `BAD_STREAM`, `BAD_LADDER`, `BAD_BEAT`, `BAD_SLUG`, `THIN_SKILL`, `NO_CLOSER`. Autosave does not close and does not spawn. CCr accept of a skill stays on the pen. This module is not a process launcher.

## `cosmos/cosmos_session_tools_kit.py`

Thin adapter for the sessions page. The engine is `builds/sessions-page/`. This module does not change the service, the ledger, or the cDeck scripts.

Public: `SessionToolsKitError`, `snapshot`, `run`.

Errors: `SessionToolsKitError` kinds `ENGINE_MISSING`, `BAD_REQUEST`. A missing engine is a refusal, not an in-file reimplementation.

## `cosmos/cosmos_sgh_drop_ingest.py`

GitHub SGH drop into the work-order bucket. Lists `keithbbf-gif/cosmos` `work_orders/drop/*.json` on `main`, then `parse_order` and `drop_order`. The existing work-order runner creates the session. This clock is not a second runner. It does not delete the GitHub file. Anthropic is off. Cursor is not an Agent family.

Public: `IngestError`, `pause_flag`, `sanitize_order_id`, `split_context_source`, `normalize_drop`, `skip_entry`, `seen_path`, `load_seen`, `seen_shas`, `append_seen`, `github_list`, `github_fetch`, `file_drop`, `poll_once`, `loop`, `standup`, `status_probe`, `main`.

Errors: `IngestError` kinds `BROKE`, `BAD_INPUT`, `UNREACHABLE` (docstring also names `REFUSED`). `--loop` honors `PAUSE.flag`. `--once` still drains while paused. Seen-sha is not a second authority.

## `cosmos/cosmos_skills.py`

Learned skills as proposals (`SKILL.md` shape) without a second writer. Accept and reject need the pen.

Public: `SkillError`, `parse_skill`. `SkillRegistry` — `propose`, `accept`, `reject`, `list`, `load`. `open_registry`, `main`.

Errors: `SkillError` kinds `BAD_SKILL`, `NO_PROPOSAL`, `ALREADY_DECIDED`, `TAMPERED`, `NOT_FOUND`, `NO_PEN`, `HARDLINE`. The service GET skills route is list-only. Accept and reject stay off that route.

## `cosmos/cosmos_spawn.py`

Spawn layers: role, wrapper, skills, tools, params. One spec. A missing layer is visible. Never a silent skip. The work-order runner calls `apply` before model argv.

Public: `SpawnError`. `SpawnSpec` — `to_dict`. `defaults`, `apply`, `require_context_list`, `spec_from_order`, `apply_order`, `preflight_session`, `refuse`, `fail_xfer`, `main`.

Errors: `SpawnError` kinds `BAD_INPUT`, `MISSING_LAYER`, `NO_CONTEXT`, `REFUSED`. `refuse` rejects `grok.exe` and `grok --single` as a work-order worker. `fail_xfer` moves the order to failed and does not spawn. `GAC_RESEAT` drops one follow-up JSON. It does not start a scheduler. The constructor tries `warn3` and swallows a failure of that import, then still raises.

## `cosmos/cosmos_spawn_grant.py`

Layer A spawn grant: a folder pen, not a fencing token. Commit fencing stays on `cosmos_lock.Lease.token`.

Public: `SpawnGrantError`. `SpawnGrant` — `allows`. `assert_granted`, `refuse_as_fencing_token`.

Errors: `SpawnGrantError` kinds `NOT_A_GRANT`, `GRANT_DENIED`, `LAYER_COLLAPSE`, `BAD_GRANT`. Passing the grant object where a fencing token belongs is `LAYER_COLLAPSE` via `refuse_as_fencing_token`.

## `cosmos/cosmos_spend.py`

In-caller spend breaker. Reserve the worst case, deny if the reserve fails, call, then settle on actual use. A ledger line after the call is a receipt, not the control. An unpriced call is `UNPRICED`, never zero.

Public: `SpendError`. `SpendGate` — `set_budget`, `guarded_call`, `audit`.

Errors: kinds actually raised in this file are `DENIED` and `UNKNOWN_RAIL`. The class docstring also lists `RESERVATION_EXPIRED` and `DOUBLE_SETTLE`. This file does not raise those two. An expired reservation is swept with `SPEND_RELEASED`. An expired budget is `DENIED`, not a second kind. An unbudgeted rail cannot spend. `POST /api/v1/spend` can still answer `SPEND_NOT_COMPOSED` when the kernel has no `SpendGate`. This page does not describe a finished multi-provider money desk. The model-rater cap is a different knob.

## `cosmos/cosmos_spend_admin.py`

Write side of the spend surface. Validates every field. A widen is not silent.

Public: `SpendAdminError` — `status`, `as_dict`. `validate`, `apply_rail_cap`, `current_thresholds`, `apply_thresholds`, `handle_post`.

Errors: kinds in `KINDS`: `BAD_REQUEST`, `BAD_TARGET`, `BAD_FIELD`, `BAD_RAIL`, `BAD_CAP`, `BAD_EXPIRY`, `BAD_THRESHOLD`, `WIDEN_REQUIRES_CONFIRM` (409), `BELOW_OUTSTANDING` (409), `CURRENT_UNREADABLE` (500), `ROUND_TRIP_UNVERIFIED` (500), `LEDGER_REFUSED` (500), `SPEND_NOT_COMPOSED` (503), `GUARD_NOT_COMPOSED` (503). Other kinds default to 400. Detail names the number, not the secret. `WIDEN_REQUIRES_CONFIRM` needs a literal allow flag. A cap above `MAX_CAP_USD` (100000) is treated as a typo.

## `cosmos/cosmos_spend_meter.py`

One-minute projection of `SpendGate.audit`. Writes `live/state/spend/meter.json` and a heartbeat. It does not append the ledger.

Public: `poll_once`, `standup`, `main`.

Errors: `FileNotFoundError` with `no install_key.bin` when that key file is missing. No spend error class of its own.

## `cosmos/cosmos_spendguard.py`

Voice circuit breaker above the gate: per session, per day, and a rate limit. `check` does not raise. A corrupt state is a denial.

Public: `SpendGuard` — `check`, `record`, `clear`, `audit`.

Errors: no `SpendGuardError`. Bad on-disk state or config raises `ValueError` inside loaders (`spendguard state is not a JSON object`, `spendguard state has wrong shapes`, `spendguard config is not a JSON object`). `check` catches that and returns `(False, GUARD_ERROR ...)`. Refusal strings also use `RATE_LIMIT`, `DAY_CAP`, and `SESSION_CAP`. `record` returns `False` instead of raising. `clear(..., reset_day=False)` does not refill the day cap. The code default `DAY_CAP_USD` is 3.00 until config or the admin thresholds replace it. This is not the Core `SpendGate`, and it is not a resale desk.

## `cosmos/cosmos_spidercaster.py`

SpiderCaster as a motif plugin. Reads `plugin/cosmos.json` from `SPIDERCASTER_HOME` or the working tree. cDeck may edit labels, models, and workflow order. Hands stay in the package. Nothing here publishes.

Public: `manifest_path`, `base_manifest`, `SpiderError`, `public_plugin`.

Errors: `SpiderError` kind `BAD_INPUT` (missing label, bad model id, or a workflow that is not the seven seats once each).

## `cosmos/cosmos_stagehand_rail.py`

Preferred-rail DOM adapter under Playwright. Act, extract, and observe. The DOM is untrusted. Playwright stays the underlay. This module does not import the job scheduler. `cosmos_kernel` compose does not attach it (no second Core).

Public: `StagehandRailError`, `default_spec`, `merge_spec`, `load_spec`, `write_spec`, `spec_path_for`, `probe_path_for`, `cache_dir`, `cache_path`, `validate_projection`, `snapshot_cache`, `record_action`. `ActionCache` — `get`, `put`. `StagehandRail` — `last_identity`, `close`, `probe`, `dispatch`. `register_stagehand_rail`, `attach_to_kernel`, `refuse_live_authority_attach`, `inspect_live_kernel`, `gate`, `main`.

Errors: `StagehandRailError` kinds in the class line: `BAD_SPEC`, `BAD_ROOT`, `UNREACHABLE`, `BROKE`, `DENIED`, `REFUSED`. Occupying `playwright-dom` is `BAD_SPEC`. `attach_to_kernel` without `boot_compose` is `REFUSED` and does not write the registry. `gate` does not write the authority ledger. GET does not mkdir the action cache.

## `cosmos/cosmos_stations.py`

Wish queue and station seats. ORC appends wishes. It does not rewrite the log. A hollow board row does not spawn anyone.

Public: `StationError`, `family_of`, `load_state`, `set_rotation`, `pick_audit`, `save_state`, `choose_station`, `choose_ccrew`, `append_wish`, `wish_depth`, `set_wish_floor`, `board_missing`, `order_count`, `set_floors`, `file_board`, `release_ccrew`, `judge_family_ok`, `family_caution`, `note_judge_seated`, `judge_due`, `pile_audit`, `snapshot`.

Errors: `StationError` kinds seen: `UNREADABLE`, `UNPARSEABLE`, `BAD_ROTATION`, `NO_FAMILY`, `BAD_CANDIDATE`, `BAD_STATION`, `NO_JUDGE`, `SAME_FAMILY`, `SET_SHORT`, `ORC_WRITES`, `EMPTY_WISH`, `BAD_FLOOR`, `BOARD_INCOMPLETE`. Coding, porosity, ortho, context, and latency on a hollow row are the string `UNMEASURED`. There is still no seats module. `GET/POST /api/v1/seats` stays `501` on the service.

## `cosmos/cosmos_stt.py`

Local speech-to-text through Vosk, on box. The default interpreter import of `vosk` is `ModuleNotFoundError`. The wheel and model are expected under `builds/cvm-dt/vendor/`.

Public: `SttError`, `repo_tree`, `vendor_site`, `provisioned_model`, `ensure_import`, `probe`, `transcribe`, `wav_to_pcm`, `main`.

Errors: `SttError` kinds `STT_NONE`, `NO_MODEL`, `BAD_WAV`. `probe` and `transcribe` return those kinds in a dict when the import or the model is missing. They do not invent a transcript.

## `cosmos/cosmos_studio.py`

MOTIF Studio pack for cDeck. GET does not mutate or mkdir. POST writes `state/studio/pack.json`. It does not start MOTIF. It does not hold API keys.

Public: `dest_via_gitur`, `default_graph`, `StudioError`, `pack_path`, `default_targets`, `default_consensus`, `default_arch`, `default_build_agents`, `default_critic_agents`, `default_build`, `default_critics`, `default_dest`, `default_implement`, `default_iterate`, `bar_met`, `default_research_models`, `empty_pack`, `load_pack`, `save_pack`, `hitl_waits`, `snapshot`.

Errors: `StudioError` kinds `BAD_INPUT`, `REFUSED`, `BROKE`, `HITL_BIND_FAILED`. Unknown write target is `BAD_INPUT`. A missing pack snapshot is kind `NO_SOURCE`, not an invented pack. A plurality tie does not meet the bar.

## `cosmos/cosmos_surfaces.py`

Storage surfaces as registered resources. A label is not a measurement. A publish mirror is not a backup. Local does not qualify as off-machine backup while that requirement holds.

Public: `SurfaceError`. `Surfaces` — `register`, `attach_probe`, `measure`, `qualify_backup_target`, `state`, `report`. `local_disk_probe`, `seed_host_surfaces`.

Errors: `SurfaceError` kinds `UNQUALIFIED`, `DUPLICATE`, `UNKNOWN_SURFACE`. The class note also names `UNREACHABLE`: `measure` records that word. It does not raise it. The seed does not invent drive rows for tests.

## `cosmos/cosmos_surfaces_kit.py`

GET fold of storage plus channels plus named local tools. Does not mutate, mkdir, or call `disk_usage`. Does not poll a vendor. UPS-JUDGE is named, not invented.

Public: `snapshot`.

Errors: no error class. A missing path is a note in the fold, not a fabricated reachability.

## `cosmos/cosmos_temporal_fold.py`

Temporal facts on the ledger. Invalidate. Do not delete. Rebuildable projection. Not a graph server.

Public: `TemporalError`, `snapshot`, `assert_fact`, `invalidate`.

Errors: `TemporalError` kinds `BAD_FACT`, `NOT_FOUND`. The service does not call `assert_fact` or `invalidate` on GET. POST of this fold stays `501` on the service.

## `cosmos/cosmos_tools.py`

Tool-contract registry. Disposition is a dated ledger decision. Registration is not capability. A never-verified tool is `verified=None` (`UNKNOWN`), never `True`.

Public: `ToolsError`. `ToolContracts` — `declare`, `disposition`, `attach_check`, `verify`, `verify_all`, `state`, `report`.

Errors: `ToolsError` kinds `DUPLICATE`, `BAD_DISPOSITION`, `UNKNOWN_TOOL`, `CONTRACT_FAIL`. `verify_all` records a broken contract per tool instead of aborting the sweep.

## `cosmos/cosmos_tools_kit.py`

GET catalog for the Tools pane: named Core modules, local callables (DOI, PDF-to-text, OCR, UPS-JUDGE, ROLD, scars), and tools already named elsewhere. Does not mutate or mkdir. Does not invent a binary.

Public: `snapshot`.

Errors: no error class. A contract row that is not verified stays `FAIL` or `UNKNOWN`, not a fake pass.

## `cosmos/cosmos_up.py`

Road reachability over Tailscale: detect, cert, serve plan, optional logon task. Effects go through an injected runner. Missing Tailscale, logged-out, no cert, and bad state stay distinct. `phone_url` is `None` when no address was measured.

Public: `UpError`. `RoadUp` — `detect_tailscale`, `ensure_cert`, `plan_serve_cmd`, `install_persistent`, `up`.

Errors: `UpError` kinds `NO_TAILSCALE`, `NOT_LOGGED_IN`, `NO_CERT`, `BAD_STATE`. Only `NO_CERT` is raised in this file. The other kinds are returned on the `up` dict. `up` itself does not raise for a reach state.

Visible mismatch: the module docstring and `plan_serve_cmd` still say `cosmos.py serve` has no `--cert` / `--key` (measured 2026-08-24). `cosmos.py` and `Service` now take that pair. `plan_serve_cmd` still accepts `cert` and `key` and then drops them. The argv is `--remote --tls` (self-signed). `up` still notes that the fetched Tailscale cert is unused until a flag lands. The flag landed. This road-up path does not pass it. Logon install needs one elevated `schtasks` (`/rl highest`). A remote serve still will not mint `config/api_token.txt`.

## `cosmos/cosmos_validate.py`

Verified reads and return checks. Declared length and hash on a critical read. DOI, quote, and path claims are gates, not optional tools.

Public: `ValidateError`, `read_verified`, `write_declared`, `v_path_exists`, `v_doi_shape`, `v_quote_in_source`. `ReturnValidator` — `register`, `accept`.

Errors: `ValidateError` kinds `SHORT_READ`, `VERIFY_MISMATCH`, `HASH_MISMATCH`, `UNVALIDATED`, `FAILED_VALIDATION`, `NO_VALIDATOR`.

## `cosmos/cosmos_verdict.py`

Voice-facing verdict stamp, GitHub write-back, and notify. The writer is the work-order runner, not the agent. This module does not touch kernel, ledger, sched, or service, and it does not add a Core route.

Public: `VerdictError`, `objection_is_concrete`, `format_objection`, `make_verdict`, `parse_github_source`, `spoken_line`, `proposal_of`, `verdict_for`, `stamp_verdict`, `voice_drop_payload`, `gh_get_file`, `gh_put_file`, `load_notify_url`, `default_http_post`, `emit_verdict`.

Errors: `VerdictError` kinds `BAD_INPUT`, `GITHUB_GET`, `GITHUB_PUT`. `objection_is_concrete` is fail-closed: a vague "no" or "broken" is not a concrete objection.

## `cosmos/cosmos_vertex_rail.py`

Vertex Agent Platform Express rail. Two wallets (`gem-api` and `vertex-coding`). Not AI Studio. Not `gemini.cmd`. Keys come from the environment or key files. Do not print the token. Does not modify kernel, ledger, sched, or service.

Public: `price_usd`, `VertexRailError`, `default_spec`, `load_spec`, `key_path_for`, `load_coding_spec`, `cache_display_name`, `key_path_for_coding`. `VertexRail` — `ensure_cache`, `ask`, `dispatch`. `rail_for`, `rail_for_coding`, `attach_to_kernel`, `write_output`, `main`.

Errors: `VertexRailError` kinds `NO_KEY`, `BAD_SPEC`, `BAD_ROOT`, `UNREACHABLE`, `BROKE`. Raises seen in this file: `NO_KEY`, `BAD_SPEC`, `BROKE`.

## `cosmos/cosmos_voice.py`

Server side of a spoken turn. The client sends a transcript. This module classifies it, confirms destructive commands with a nonce bound to that utterance, and ledgers the turn. State lives in the convo projection, not in the object.

Public: `VoiceError`. `VoiceMode` — `handle`.

Errors: `VoiceError` kinds `NO_SESSION`, `BAD_INPUT`. An unknown session is `NO_SESSION`. A confirm id that is missing, consumed, expired, or bound to a different utterance does not run the command. Unknown model words stay question text. They are not guessed into a model alias.

## `cosmos/cosmos_voice_hardening.py`

Voice constants and read-only BootUP string helpers, cut out of the service. No kernel, ledger, or HTTP of its own. `cosmos_service` re-exports these names.

Public classes and functions: none. The public constants are `DEDUPE_WINDOW_S`, `BU_MD_PATH`, and `STREAM_ROOTS`. The helpers `_flat_trim`, `_stream_section`, and `_bootup_summary` are private.

Errors: no error class. An unreadable handoff returns `ok: False`, `error: BU_MD_UNREADABLE`, and `refused: True`. It does not raise. A missing stream section is an honest note plus the head of the file, not a fabricated section.

Visible limit: `BU_MD_PATH` and `STREAM_ROOTS` are drive literals (`V:\Ai\BU.MD`, Legal, this repo, ROLD, Research4). The module says that is on purpose so a test can repoint them. They are not `cosmos_paths`. Identical `(client_id, utterance)` inside `DEDUPE_WINDOW_S` (15 seconds) is a duplicate drop on the service voice route.

## `cosmos/cosmos_voice_loop.py`

Two products that share the work-order bucket. Voice Drop is the GitHub file the SGH ingest clock reads. The Android mouth talks HTTP and does not mount `live/`. This module does not run that clock, does not delete GitHub, does not start an agent, does not POST `/voice`, and does not poll grok.com.

Public: `VoiceLoopError`, `load_sops`, `order_from_mouth`, `file_mouth_drop`, `save_sop`, `snapshot`.

Errors: `VoiceLoopError` kinds in the class line: `BAD_INPUT`, `REFUSED`, `BROKE`. The raise seen in this file is `BAD_INPUT`. An unreachable ingest heartbeat is the string `UNREACHABLE` or `UNKNOWN` on the snapshot, not a fake ready.

## `cosmos/cosmos_warn.py`

Print `WARN BEFORE ERROR` three times, then the caller refuses. Humans are distracted. Then fail-closed.

Public: `warn3`, `warn_if_two_heads`, `WarnRefuse`.

Errors: `WarnRefuse` carries `kind` and the warned line. The self-test raises `NO_CONTEXT`. `warn_if_two_heads` warns when `origin/main..HEAD` is non-empty and returns the count. It does not refuse serve. Git failure returns `-1` (unmeasured), not a fabricated zero. `SpawnError` calls `warn3` for `REFUSED`, `NO_CONTEXT`, and `MISSING_LAYER`.

## `cosmos/cosmos_watchdog2.py`

Fifteen-second route scanner and assigner so the idle ceiling stays under thirty seconds. The 15s loop is a detached process. Task Scheduler's floor is one minute, so the scheduled task only restarts the daemon (self-heal and logon). Does not modify kernel, ledger, sched, or service. A hold pause does not self-clear. A resume-gate pause can.

Public: `repo_tree`, `default_runtime_root`, `pythonw_exe`, `plan_loop_argv`, `plan_task_argv`, `plan_logon_argv`, `query_task`, `read_heartbeat`, `heartbeat_age_s`, `acquire_lock`, `spawn_wmi`, `spawn_popen_detached`, `spawn_detached`, `wait_fresh`. `Watchdog2` — `pause_flag`, `maybe_auto_resume`, `log`, `write_heartbeat`, `load_assigned`, `save_assigned`. `scan_once`, `loop`, `install_minute_task`, `install_logon_task`, `standup`, `bind`, `main`.

This module re-exports the public functions of `cosmos_watchdog2_scan` as the same objects, not copies.

Errors: no error class. A failed watchdog is logged as "Watchdog2 failed (never-idle-15s is broken)." `PAUSE.flag` drops nothing. The heartbeat still writes `PAUSED`. Wishlist lines already in backlog, tracker, DHx, or the queue are not re-dropped. Max drops per pass is 3.

## `cosmos/cosmos_watchdog2_scan.py`

Markdown and route scanners split out of the watchdog. Text in, dicts out. No daemon, no 15s loop, no schtasks. The filesystem touches are the cursor-key check and the annotate / tick writers.

Public: `parse_md_checkboxes`, `parse_backlog`, `dhx_haystack`, `cursor_key_exists`, `pick_agent`, `name_hit`, `checkbox_skip_reason`, `backlog_skip_reason`, `backlog_task`, `wishlist_task`, `route_drop_spec`, `annotate_checkbox`, `annotate_backlog`, `update_source_tick`, `update_backlog_tick`.

Errors: no raises in this file. Prose does not decide a skip. A missing Cursor key drops Cursor (and G46 in that same availability set) from the pick. That is an absence, not a measured failure of the model.

## `cosmos/cosmos_womb.py`

DEFINE, then pick a pair: high orthogonality, low porosity, under a completion-price cap. Reads the porosity tensor and the model-rater row. Does not rewrite the tensor formula. GET does not mkdir and does not invent. A missing cell is `UNMEASURED` and that pair is skipped. An unmeasured completion rate is a skip, not $0.

Public: `WombError`, `is_sol`, `is_luna`, `is_luna_flex`, `completion_usd_per_m`, `eligible_rows`, `pick_pair`, `seat`.

Errors: `WombError` kind `BAD_INPUT`. The service maps a bad budget to `400 BAD_INPUT` and no pair to `404 UNMEASURED`. SOL and non-flex Luna are excluded. This does not spawn the pair.

## `cosmos/cosmos_womb_board.py`

Read-only tail of the factory-floor board. GET does not mkdir. A missing file is `UNMEASURED`, not an empty measured board. Does not call the pipe root (that mkdir's inboxes).

Public: `WombBoardError`, `snapshot`.

Errors: `WombBoardError` kind `BAD_TAIL`.

## `cosmos/cosmos_work_order.py`

Typed work-order record and the DONE versus COMPLETED split. Agents stay write-private. Output is one file in the attempt workspace.

Public: `OrderError`, `new_order_id`, `parse_agent`, `parse_context_source`, `parse_output`, `parse_order`, `claude_model`, `vertex_cli_env`, `gemini_binary`, `route_agent`, `compose_prompt`, `build_argv`, `infer_repo_tree`, `work_order_dirs_ro`, `work_order_dirs`, `public_order_row`, `fold_work_orders`, `order_file`, `find_order`, `pickup_order`, `notify_core_picked`, `file_done`, `accept_order`, `reject_order`, `drop_order`.

Errors: `OrderError` kinds `BROKE`, `BAD_INPUT`, `NO_CONTEXT`, `REFUSED`, `FAILED` (docstring also names those). Unknown agent family is `BAD_INPUT`. `build_argv` for the Claude rail raises `ValueError` `[ANTHROPIC_OFF]`, not `OrderError`. Grok argv is still built here. The runner refuses to spawn it (see `cosmos_work_order_run`). `infer_repo_tree` assumes the repo sits beside the runtime root. That is a parent-directory guess, not the path resolver. `vertex_cli_env` drops Studio API keys from the child env when a project is set. It does not print secrets.

## `cosmos/cosmos_work_order_checks.py`

GitHub, GitLab, and Cursor checks, one each, when a DONE order lands in assigned. Same runner. Not a second cron. Cursor here is a check, not an Agent family.

Public: `stamp`, `unmeasured`, `rail_stamped`, `proposal_branch`, `cow_checks_view`, `check_github`, `check_cursor`, `check_gitlab`, `apply_done_checks`, `stamp_assigned_done`.

Errors: no error class. A check that cannot be measured returns `unmeasured` rather than a fake pass. `check_rails` must be a dict, `None`, or `False`. Anything else is `TypeError`.

## `cosmos/cosmos_work_order_run.py`

Native poller for typed work orders. One inflight agent, a heartbeat each tick, DONE in assigned for accept. Grok is not spawned live from this clock. Vertex GEM stays in-tick. The same daemon runs the CHECKED rails. Does not open `live/ledger/` itself. Pickup is notified to Core.

Public: `pause_flag`, `list_drops`, `list_picked`, `reap_picked`, `bind_github_source`, `bind_verdict`, `process_one`, `poll_once`, `loop`, `standup`, `status_probe`, `main`.

Errors: a live `grok` / `--single` argv with no injected `run_fn` warns `GROK_EXE_SCAR` and files DONE with `rc` 2 and `err` `GROK_EXE_SCAR`. That is a refuse, not a successful worker. `SpawnError` from `apply_order` or `refuse` goes through `fail_xfer`. Pause holds the loop. `--once` behavior follows `pause_flag` in this file's poll path. This clock does not make Anthropic a worker.

## `cosmos/cosmos_workspace.py`

One attempt-private workspace path for every rail. The live runtime root and the repo tree are refused as cwd.

Public: `WorkspaceError`, `under_work`, `assert_not_live`, `refuse_tree_cwd`, `list_working_files`, `seed_working_tree`, `clone_tree`, `prepare_workspace`, `order_workspace`, `stage_context`, `output_path`, `output_exists`.

Errors: `WorkspaceError` kinds `REFUSED`, `BROKE`, `NO_CONTEXT`. A missing context source is `NO_CONTEXT`. Seed overlay is fail-closed onto the clone dest only.

## `cosmos/cosmos_xtalk.py`

Core face of the XTalk stream. Canonical JSON plus a sha256 chain. GET does not mkdir and does not advance a cursor. POST Transport B appends the Core-local stream. Transport A (harness inject) is `501` `NOT_COMPOSED` on the service. Do not fake an inject. `?bind=openwork` is read-only. This module does not write OpenWork.

Public: `XTalkError`, `resolve_bind`, `fence_check`, `verify_chain`, `snapshot`, `send`. `cosmos.py xtalk` calls the private `_cli`.

Errors: `XTalkError` kinds `NO_PATHS`, `BAD_TAIL`, `CHAIN`, `BAD_REQUEST`, `BIND_READONLY`, `BAD_MSG`, `BAD_ROLE`, `NOT_COMPOSED`, `BAD_BIND`, `LOCK`. An unknown role is `BAD_ROLE`, not a fake inject. `fence_check` returns `"unknown"` when the role row is missing. That is not Transport A.

Visible limit: `OPENWORK_STREAM` and `OPENWORK_ROLES` are drive literals under `V:\OpenWork\XTalk\live\state\`. If the stream file is absent, bind kind is `UNMEASURED`. The local stream still resolves through `paths.role("state")`.

## `cosmos/cosmos.py`

CLI entry a peer runs after clone. Verbs in the parser: `install`, `status`, `audit`, `submit`, `backup`, `rehearse`, `serve`, `session` (`close` / `start`), `deck`, `xtalk`. Unknown flags fail argparse.

Public: `main`.

Errors: `serve` prints `REFUSED` and returns 2 on `ServiceError` (blank token, missing token, remote cleartext, remote open access, cert not found). `session` prints `SessionError` or `ContextError` and returns 2. If critic attach throws, the exception is printed and critics become an empty list. The next line says `POST /api/v1/crucible` stays `501`. That swallow is visible. It is not a composed critic round.

The module docstring lists install through session and does not mention `deck` or `xtalk`. Both parsers exist. `serve` does accept `--cert` and `--key` and passes them to `Service`. `cosmos_up.plan_serve_cmd` still does not (see that file). `status` and `audit` boot a read-only kernel. `deck` only launches native cDeck. It is not a second service.

This slice is not a finished product.
