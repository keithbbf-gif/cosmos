# Core A–C

This slice is not a finished product. COSMOS is not finished. This page is a
reading map of the 40 `cosmos/cosmos_*.py` modules whose names start with
`cosmos_a`, `cosmos_b`, or `cosmos_c`. It is not a second service, not an
install guide, and not a claim that any module below is done or fully tested.

Names come from a host `ast` parse (`py -3.14`) on 2026-10-08. That parse
reported no `SyntaxError` in this slice. Public means a module-level class or
function whose name does not start with `_`, plus methods defined on those
classes that likewise do not start with `_`. Private helpers are omitted.
Function bodies are not pasted. A `SystemExit` that only wraps a CLI `main`
is not listed unless a library path raises it.

## cosmos_action_chain.py

Chains actions on the ledger with separation of duties (creator, reviewer,
and approver must differ). It is not a second audit product.

Public: `ActionError`. `last_action_sha`, `append_action`, `snapshot`,
`verify_actions`.

Errors: `ActionError` kinds `SOD` (a party missing, or the three parties not
distinct), `FORGED`, and `BROKEN_CHAIN`. Import inserts this file's directory
on `sys.path`.

## cosmos_approval.py

Action approval gate: classify a normalized action, then request, grant,
deny, consume, or allowlist it. Silence is not consent.

Public: `ApprovalError`. `normalize_action`, `content_scan`. `ApprovalGate`
methods `classify`, `request`, `pending`, `grant`, `deny`, `consume`,
`guard`, `allowlist`.

Errors: `ApprovalError` kinds raised here are `BAD_ACTION`, `HARDLINE`,
`NO_REQUEST`, `NOT_APPROVER`, `SELF_APPROVAL`, `ALREADY_DECIDED`, `EXPIRED`,
`NEEDS_APPROVAL`, and, from `consume`, `DENIED`, `BAD_NONCE`, and
`ACTION_MISMATCH`. A hardline is refused rather than queued. A principal
cannot approve its own request. An expired request is not a grant.

## cosmos_askmine.py

Session-transcript mining satellite (clock id 19). It reads JSONL, scores
asks, and can write a route projection. It is a projection, not the ledger.

Public: `redact`, `parse_transcript`, `classify_segment`, `terms_of`,
`analyse_turns`, `mark_repeats`. `TreeIndex` methods `find_basename`, `find`.
`absolute_paths`, `named_artifacts`, `build_name_index`, `disk_check`,
`tree_status`, `mark_answered_later`, `closure_candidates`, `score_closure`,
`resolve_status`, `mine`, `to_markdown`. `AskmineRefusal`. `finding_slug`,
`to_route_markdown`, `default_scan_dirs`, `collect_jsonl`, `poll_once`,
`standup`, `plan_task_argv`, `install_task`, `main`.

Errors: `AskmineRefusal` is raised for `IDENTITY_MISMATCH` and
`NO_TRANSCRIPT`. The class text also names `NO_ROOT` and `NO_CONFIG`.
`NO_CONFIG` does not appear anywhere else in the file. `NO_ROOT` is a JSON
kind on the CLI path, not an `AskmineRefusal`. `_since_epoch` raises
`SystemExit` on a bad `--since` value. Import inserts this file's directory
on `sys.path`.

## cosmos_backup.py

Verified backup and rehearsed restore. A copy without a hash check is not a
verification. The file records an older green-log hole: long Win32 paths
were omitted and `BACKUP_VERIFIED` was still appended. The text says the
current rule is to prefix the root via `cosmos_paths.extended` and refuse
with `SOURCE_UNREADABLE` instead of shortening the scope.

Public: `BackupError`. `scan_secrets`, `refuse_secrets`. `Backup` methods
`run`, `rehearse_restore`.

Errors: `BackupError` kinds this file raises are `SECRETS_IN_SCOPE`,
`SOURCE_UNREADABLE`, `EMPTY_SCOPE`, `TARGET_MISSING`, `VERIFY_MISMATCH`, and
`REHEARSAL_FAILED`. The class text also names `SNAPSHOT_INCOMPLETE`; this
file does not raise that kind. `cosmos_backup_clock.py` does.

## cosmos_backup_clock.py

Four-times-daily backup satellite at hours 07, 11, 19, and 23. It stages a
bounded snapshot and calls `Backup`. The file's own note says a short
snapshot used to be labeled verified; `assemble_snapshot` now fails closed
on a hole. It does not edit `Backup` or the ledger writer.

Public: `assemble_snapshot`, `poll_once`, `standup`, `main`.

Errors: `BackupError` `SOURCE_UNREADABLE`, `SNAPSHOT_INCOMPLETE`, and
`EMPTY_SCOPE` (zero files staged). `poll_once` raises `FileNotFoundError`
when `install_key.bin` is missing. Import inserts this file's directory on
`sys.path`.

## cosmos_backup_fold.py

GET-only fold of the backup clock for cDeck. It does not run a backup and
does not mkdir.

Public: `snapshot`.

Errors: no exception type of its own. A missing heartbeat starts as kind
`NO_SOURCE`. Unreadable heartbeat JSON becomes `BROKE`. If
`backups/verified` exists, a `NO_SOURCE` result is rewritten to `OK`, so a
missing heartbeat is not left as `NO_SOURCE` whenever that directory is
present. `paths.backups` failures are swallowed (`except Exception`) and
the verified side becomes absent. The self-test, not import, inserts
`sys.path`.

## cosmos_brain.py

Headless Claude CLI ("Opus") brain for free-form voice turns, with a Grok
fallback when the CLI is missing, slow, or over cap. Callers inject the
process so tests need no `claude` binary.

Public: `voice_client_timeout_s`, `brain_context`, `claude_session_uuid`,
`opus_ask`. `TurnGuard` methods `check`, `record`, `clear`, `audit`.

Errors: `TurnGuard` raises `ValueError` when the guard config is not a JSON
object or the state has the wrong shape. `opus_ask` catches timeout and
other exceptions and falls back; a dead brain is not raised to the voice
caller. Several `except Exception` handlers swallow probe and audit
failures.

## cosmos_browser.py

Best-effort DOM read driver: headless Chrome or Edge with `--dump-dom`.
The file says this is a read, not CDP. It does not fill forms, click, or
complete OAuth.

Public: `discover_browser`, `detect_auth_wall`. `ChromeDriver` methods
`start`, `navigate`, `session_ok`, `stop`.

Errors: `ConnectionError` when no Chrome or Edge binary is found, when
`navigate` runs before `start`, or when the browser process fails.
`PermissionError` when navigation hits an auth wall the detector names.
Discovery `OSError` is swallowed while probing candidates.

## cosmos_bucket_daemon.py

Shared poll, claim, and handoff loop for the Grok and GEM bucket workers.
One node bucket per daemon. Results go to the configured dest. It does not
wrap `cosmos_runner`.

Public: `WorkerError`. `canon_node`, `node_spec`, `make_worker_id`,
`clamp_interval`, `script_for`, `load_config`, `pause_flag`,
`pause_decision`, `bucket_dir`, `v_returns`, `canon_out`, `dest_dir`,
`list_drop_files`, `parse_task`, `fence_path`, `write_fence`, `claim_drop`,
`stage_drop`, `execute_handoff`, `write_result_files`, `process_drop`,
`poll_once`, `loop`, `plan_loop_argv`, `plan_task_argv`, `standup`,
`status_probe`, `build_parser`, `run_cli`, `main`.

Errors: `WorkerError` kinds `BAD_NODE`, `BAD_OUT`, `NO_DEST`, `BAD_TASK`,
`REPLAY`, `NO_KEY`, and `NO_ROOT`. This `WorkerError` is not the class
`cosmos_crit_consumer.py` subclasses. Import inserts this file's directory
on `sys.path`.

## cosmos_ccr.py

Chief Coder lease. Presence of `state/control/CCR.lease` is the write
token. One writer at a time.

Public: `CcrError`. `lease_path`, `arbiter_ledger_path`, `read_lease`,
`is_legacy`, `held`, `assert_pen`, `acquire`, `renew`, `release`, `status`.

Errors: `CcrError` kinds `UNPARSEABLE`, `CCR_NO_LEASE`, `CCR_SID_MISMATCH`,
`CCR_HELD`, `ROUND_TRIP_UNVERIFIED`, and `CCR_STALE_TOKEN` (mapped from a
lock `STALE_TOKEN` during renew). A lease that does not read back is
refused. `assert_pen` fails closed with no lease or a sid mismatch.

## cosmos_ccr_duty.py

Measures what Gitur publishes and what CCr does next. It does not merge,
pull, push, grade the pile, or run the Composer check.

Public: `measure_sync`, `gitur_warnings`, `next_action`, `head_claim`,
`report`.

Errors: no error class. `ValueError` from a bad count, `OSError` from the
adapted head read, and `SystemExit` from the CLI. `measure_sync` swallows
`OSError` and `subprocess.TimeoutExpired` into the measurement record.
`gitur_warnings` swallows `Exception`.

## cosmos_cdeck_feed.py

Fast display feed (about 0.75s) that aggregates heartbeats and meter
projections already on disk. The tick does not call the ledger, Kernel, or
SpendGate.

Public: `poll_once`, `loop`, `standup`, `main`.

Errors: no error class. Unreadable inputs are skipped (`OSError`,
`ValueError`). The loop's broad `except Exception` keeps the daemon up.
Import inserts this file's directory on `sys.path`.

## cosmos_cdeck_launch.py

Starts native `cdeck.exe` with `os.startfile` so the window is a desktop
process, not a browser tab and not a child of the agent session.

Public: `repo_tree`, `cdeck_exe`, `launch_cdeck`.

Errors: does not raise for a missing tool. The record stays `ok: false`
with `error` `EXE_MISSING`, `NO_STARTFILE` (`AttributeError`, non-Windows),
or `OSError` text. `repo_tree` is the parent of the `cosmos` package
directory, derived from `__file__`.

## cosmos_chamber.py

Room and board presence as a ledger projection. Not a second scheduler.
GET does not mkdir.

Public: `ChamberError`. `snapshot`, `join`.

Errors: `ChamberError` kinds `STREAM_REFUSED` and `BAD_PRINCIPAL` (empty
principal). Rooms named in the file are `Cm`, `plumbing`, `physics`, and
`chapter`. Import inserts this file's directory on `sys.path`.

## cosmos_claude_rail.py

Claude Code CLI coding rail (`claude -p`), not the metered Messages API.
The file refuses a `core->models` route. Prompt is on stdin because a
trailing `--add-dir` swallows a positional prompt.

Public: `ClaudeRailError`. `default_spec`, `merge_spec`, `load_spec`,
`write_spec`, `redact_key`, `read_key`, `done_from_artifacts`,
`parse_agent_spec`. `ClaudeRail` methods `key_last4`, `last_probe`,
`probe`, `dispatch`. `spec_path_for`, `key_path_for`, `probe_path_for`,
`launch_path_for`, `register_claude_rail`, `attach_to_kernel`,
`refuse_live_authority_attach`, `inspect_live_kernel`, `gate`,
`launch_run`, `main`.

Errors: `ClaudeRailError` kinds `BAD_SPEC`, `NO_KEY`, and `BROKE`, plus
`REFUSED` from `attach_to_kernel` (it will not append authority
`LINK_REGISTERED` until kernel boot reattaches probes; isolated `--gate`
ledger only, unless `boot_compose=True`). Import inserts this file's
directory on `sys.path`.

## cosmos_clock.py

Shared Windows-clock helpers for satellites: heartbeat, lock, schtasks, and
detached spawn. The file says it is not kernel, ledger, sched, or service.
schtasks cannot go below one minute; faster work is a detached loop plus a
one-minute heal task.

Public: `schtasks_sandbox_on`, `pythonw_exe`, `iso_now`, `write_heartbeat`,
`read_heartbeat`, `heartbeat_age_s`, `pid_alive`, `acquire_lock`,
`hush_vbs`, `tr_cmdline`, `plan_create`, `run_schtasks`, `query_task`,
`run_task`, `create_task`, `harden_task`, `spawn_wmi`,
`spawn_popen_detached`, `spawn_detached`, `wait_fresh`, `atomic_json`.

Errors: no error class and no `raise`. `read_heartbeat` returns `None` on
missing or unreadable JSON. `acquire_lock` returns `None` when the lock is
already held. `pid_alive` returns false for a dead or unopenable pid (it
checks exit code 259, not merely `OpenProcess`). `run_schtasks` returns
`ok: false` with kind `SCHTASKS_SANDBOX` or `PROD_WRITE_REFUSED` when the
sandbox env is on, and `rc: -1` when `schtasks` cannot start. Spawn and
wait helpers return `ok: false` records instead of raising.

## cosmos_clone_plan.py

Plans parallel clone seats. It does not start them. Every row has `pen`
false, `spawn` false, and an empty plan executable. A clone never takes a
second live pen.

Public: `CloneRow`, `ClonePlan`, `ClonePlanError`. `plan_clones`.

Errors: `ClonePlanError` reasons `SECOND_PEN` (caller passed `pen=True`),
`EMPTY_MISSION`, `NO_SEATS`, `TOO_MANY` (more than 12), `BLANK_SEAT`, and
`DUPLICATE_SEAT`. The first failure raises; no partial row list is
returned. `ClonePlanError.__init__` raises `ValueError` if `reason` is not
one of those six codes.

## cosmos_code_checks.py

Non-AI checks on a saved CCrew reply, before WOMBAT, in order: `py_compile`,
`ruff`, `mypy`, `pytest`. Rows go to `state/code_checks.db`. A missing tool
is a `MISSING` row, not a skip. This module does not call WOMBAT.

Public: `db_path`, `point_local_tree`, `extract_file_blocks`, `materialize`,
`run_code_checks`, `fails_of`, `rows_for`.

Errors: no error class. `point_local_tree` raises `OSError` when the local
tree cannot be pointed. Checker argv construction raises `ValueError`.
Tool failures are recorded rows, not raised as a checker exception.

## cosmos_code_tools.py

Read, Write, Edit, Glob, Grep, and Bash under an injected path allowlist.
Bash is `shell=False` argv, not a shell. The file says these tools do not
open the ledger, the kernel, or a shell.

Public: `CodeToolError`. `declare_on`, `contract_rows`. `CodeTools` methods
`Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`. `main`.

Errors: `CodeToolError` kinds `BAD_INPUT` (empty allowlist, bad root, empty
edit string, bad glob, bad argv, bad cwd, timeout out of range), `REFUSED`
(path outside the allowlist, sensitive names, ledger or git internals,
`grok.exe`), `NOT_FOUND`, `TOO_BIG`, and `AMBIGUOUS` (edit string matches
more than once).

## cosmos_codex_rail.py

OpenAI Codex CLI coder and vetter. Not the metered `oa-api` rail and not a
BTS wrap. It refuses a `core->models` route. The vetter requires an output
schema.

Public: `CodexRailError` (subclass of `RailSeamError`). `default_spec`,
`merge_spec`, `load_spec`, `write_spec`, `redact_key`, `read_key`,
`done_from_artifacts`. `CodexRail` methods `key_last4`, `last_probe`,
`probe`, `coder`, `vet`, `dispatch`. `spec_path_for`, `key_path_for`,
`probe_path_for`, `launch_path_for`, `vet_path_for`, `register_codex_rail`,
`attach_to_kernel`, `refuse_live_authority_attach`, `inspect_live_kernel`,
`gate`, `launch_run`, `vet_run`, `run_coding_dispatch`, `run_vetter`,
`main`.

Errors: `CodexRailError` kinds `BAD_SPEC`, `NO_KEY`, `BROKE` (vetter missing
`--output-schema`, or a broken register), and `REFUSED` from
`attach_to_kernel` (same authority-attach refusal as the Claude rail).
Import inserts this file's directory on `sys.path`.

## cosmos_collector.py

About-30s results collector. The index is a cache. Source files stay the
truth. It is not a second ledger writer. DHx marker join and the file
walks live in the two modules below; this file's text says it re-exports
them.

Public: `load_collector_config`, `resolve_repo_tree`, `repo_tree`,
`default_research_dir`, `default_summary_md`, `default_dhx_path`,
`pythonw_exe`, `plan_loop_argv`, `plan_task_argv`, `plan_logon_argv`,
`display_agent`, `display_maker`, `summarize_file`, `dedup_key`.
`Collector` methods `write_heartbeat`, `poll_once`, `render_summary`,
`drain_loop`. `read_heartbeat`, `heartbeat_age_s`, `acquire_lock`,
`spawn_wmi`, `spawn_popen_detached`, `spawn_detached`, `install_task`,
`wait_fresh`, `bind`, `status_probe`, `loop`, `standup`, `compact_index`,
`main`.

Errors: no error class. This file's parse shows no typed `raise` except a
bare re-raise in `loop` and CLI `SystemExit`. Import inserts this file's
directory on `sys.path`. This page did not re-check the re-export claim
against importers.

## cosmos_collector_dhx.py

Pure DHx marker grammar and marker-to-result join. Text in, dicts out. No
runtime root and no writes.

Public: `task_of`, `path_hit_score`, `pick_lane_job`, `parse_dhx_markers`,
`marker_stems`, `resolve_marker_artifact`, `correlate_marker`.

Errors: no `raise`. `OSError` and bad marker values are skipped
(`OSError`, `TypeError`, `ValueError`). A join miss is an ordinary result,
not an exception.

## cosmos_collector_scan.py

Pure queue, research, and ledger iterators split out of the collector.
No runtime root and no writes.

Public: `iter_queue_files`, `iter_research_files`, `iter_ledger_events`,
`ledger_event_kept`, `iter_runner_ledger`, `iter_jsonl_objs`.

Errors: no `raise`. Walk and JSONL read errors are skipped (`OSError`,
`ValueError`). An unreadable directory disappears from the iterator
instead of failing the scan.

## cosmos_command.py

Text-in command seam over kernel actions that already exist. The grammar
is a first-word verb (`status`, `audit`, `health`, `spend`, `rails`,
`makers`, `jobs`, `events`, `session`, `submit`, `help`). Handlers do not
add a second implementation of those actions.

Public: `CommandError`. `Commander` method `handle`.

Errors: `CommandError` kinds `REFUSED` (destructive verbs are not on this
seam), `UNKNOWN_COMMAND`, `BAD_ARGS`, and `KERNEL_REFUSED`.

## cosmos_competency.py

`COMPETENCY.toml` as routing input. Ratings pick a node. The file is not a
prose scorecard.

Public: `CompetencyError`. `default_path`, `load`, `pick`,
`classify_task_type`, `agent_kind`.

Errors: `CompetencyError` kinds `UNREADABLE`, `BAD_SCHEMA`, `UNKNOWN_TASK`,
`NO_CANDIDATE`, and `NO_DISPATCH`.

## cosmos_context.py

Session context manifest on the ledger. A clean close requires no open
watcher, or an explicit force that records the miss.

Public: `ContextError`. `Session` methods `record_fact`, `open_watcher`,
`resolve_watcher`, `close`. `boot_inherit`.

Errors: `ContextError` kinds `ALREADY_CLOSED`, `NOT_OPEN`, and
`UNRESOLVED`. `close(force=True)` with watchers still open does not raise;
it appends ledger event `OPEN_CONTEXT` and then `SESSION_CLOSED`.
`boot_inherit` folds those incidents for the next boot. There is no
`ContextError` kind named `OPEN_CONTEXT`.

## cosmos_context_pull.py

Native Windows tail of session transcripts. The file says the sandbox
cannot read `C:\` reliably, so this tool is the host-side reader.

Public: `ContextPullError`. `default_sessions_roots`,
`find_current_transcript`, `read_tail_bytes`, `record_turn`, `parse_turns`,
`format_blob`, `pull_context`, `main`.

Errors: `ContextPullError` is defined with kinds `NO_ROOT`,
`NO_TRANSCRIPT`, and `IO`, and this file never raises it. `pull_context`
writes `rec["error"]` instead (`no transcript`, `transcript missing`, or
`IO ...`). `find_current_transcript` returns a dict on a miss. Decode uses
`errors="replace"`. Bad JSONL lines are skipped.

## cosmos_contracts.py

Machine-checked subsystem contracts: a statement plus evidence markers in
code, tests, or prose. The file's reason for existing is a measured
docstring-versus-test drift (`register_node_rails`). An exit code is not
the proof; the emitted result is.

Public: `ContractError`. `load_contracts`, `check_evidence`, `audit`,
`selftest`, `main`.

Errors: `ContractError` kinds `NO_CONTRACTS` and `BAD_CONTRACT`. `audit`
reports `broken` rows and `broken_count` inside the result object; a broken
contract is data, not only an exception.

## cosmos_control.py

Polled human off-switch for the voice seam: pause, mic off, and clear-queue,
per client and global. Flags do nothing by themselves; the voice handler is
what refuses spend while they are up.

Public: `ControlError`. `ControlChannel` methods `get`, `blocked`, `kill`,
`set_flags`, `resume`.

Errors: `ControlError` kind `STATE_UNREADABLE`. `ValueError` when the
control state is not the expected shape. Load and mutate paths also bare-
reraise after recording the failure.

## cosmos_convo.py

Durable conversation sessions projected from the authority ledger. The
store keeps no private session database. A phone client holds a session id,
not the transcript.

Public: `ConvoError`. `ConvoStore` methods `create_session`, `assert_owner`,
`append_turn`, `get_session`, `list_sessions`, `close_session`,
`reopen_session`.

Errors: `ConvoError` kinds `BAD_SCOPE`, `BAD_TURN` (empty title, empty text,
bad mode, bad follow dict, bad close or reopen), `NO_SESSION`, and
`BAD_ROLE`.

## cosmos_copilot_rail.py

GitHub Copilot cloud-agent satellite. Identity probe is a GET and does not
spend. Creating a task spends credits and is opt-in. Installation tokens
(`ghs_`) are refused. The file also refuses `core->models` and
`core->forge`.

Public: `CopilotRailError` (subclass of `RailSeamError`). `default_spec`,
`merge_spec`, `load_spec`, `write_spec`, `spec_path_for`, `key_path_for`,
`probe_path_for`, `read_key`. `CopilotRail` methods `last_identity`,
`probe`, `dispatch`. `register_copilot_rail`, `attach_to_kernel`,
`refuse_live_authority_attach`, `main`.

Errors: `CopilotRailError` kinds `BAD_SPEC`, `REFUSED` (the `ghs_` token,
and `attach_to_kernel` refusing authority `LINK_REGISTERED` unless
`boot_compose=True` from boot). Import inserts this file's directory on
`sys.path`.

## cosmos_cred_kit.py

Fold of API keys, SDKs, and local agents for display and paste-in. GET does
not return secret material, does not mkdir, and does not poll vendors. A
live view is a rails probe already on file.

Public: `CredError`. `gcloud_accounts`, `load_custom`, `save_custom`,
`snapshot`, `agents_snapshot`, `set_secret`, `delete_secret`, `grab_secret`,
`add_custom`.

Errors: `CredError` kinds `REFUSED` (secret path, or the custom catalog is
full), `BAD_INPUT` (empty, oversized, or NUL secret; bad id; duplicate
custom id), and `NO_SOURCE`. Import inserts this file's directory on
`sys.path`.

## cosmos_crew_pipe.py

Saved CCrew reply, then CPU checks, then WOMBAT, then a judge filing at 30
sets, then Gitur. Legacy github, cursor, and gitlab rails stamp CI and do
not read the saved file. This module does not spawn a model and does not
write LiT. An `UNMEASURED` rail stays visible and is not treated as a pass.

Public: `pipe_root`, `local_code_checks`, `legacy_rail_view`,
`wombat_action`, `attach_pipe`, `note_failed`, `file_judge_correction`,
`file_judge_keep`, `file_gitur_result`.

Errors: no error class in this file. `file_judge_correction` raises
`DudsError` kind `JUDGE_UNSEATED` and `FileNotFoundError` when the reply
file is missing. `file_gitur_result` raises `FileNotFoundError` the same
way.

## cosmos_crit_consumer.py

Vendor-plural critique packet consumer. It claims inbox packets under a
fence, invokes a rail, and writes the return. Replay of a finished packet
is refused.

Public: `ConsumerError`. `canon_crit_kind`, `route_for`, `workers_dir`,
`fence_path`, `list_inbox_files`, `list_packets`, `returns_already_done`,
`is_replay`, `write_fence`, `claim_packet`, `parse_critique_packet`,
`run_claude_sonnet`, `invoke_rail`, `process_packet`, `poll_once`, `loop`,
`plan_task_argv`, `standup`, `status_probe`, `main`.

Errors: `ConsumerError` subclasses `WorkerError` imported from
`cosmos_node_worker`, not the `WorkerError` class in
`cosmos_bucket_daemon.py`. Kinds raised here are `BAD_KIND`, `REPLAY`, and
`NO_ROOT`. The file inserts its directory on `sys.path`, imports
`cosmos_dispatch` (the comment says that import inserts another directory
and would bind the wrong `cosmos_node_worker`), then inserts its directory
again.

## cosmos_crucible.py

Adversarial packet: named sources, injected critics, returns on disk, then
a merge skeleton that keeps unanimous, majority, singleton, and contested
findings apart. A dead critic is a finding. Dispatchers are injected so
tests do not spend.

Public: `CrucibleError`. `Crucible` methods `build_packet`, `run_round`,
`merge_skeleton`.

Errors: `CrucibleError` kinds `EMPTY_SOURCE` (no sources, or an empty
source), `PACKET_INCOMPLETE`, and `NO_CRITICS` (one family reviewing its
own work is refused).

## cosmos_crucible_critics.py

Builds live critic callables and attaches them at `serve` time. The file
states that `POST /api/v1/crucible` stays HTTP 501 until that attach.
Tests inject fakes. `Kernel()` itself is not changed, so an unattached
process keeps the 501.

Public: `CriticError`. `grok_sgh_env`, `grok_sgh_argv`,
`make_grok_sgh_critic`, `make_vertex_critic`, `make_oa_critic`,
`make_rail_critic`, `compose_crucible_critics`, `attach_crucible_critics`,
`spend_round`.

Errors: `CriticError` kinds `NO_RAIL` (binary or account missing, or
`do_not_activate` is off — the file refuses rather than Upgrade or
Activate), `EMPTY_OUTPUT`, and `UNPRICED` (gem-api returned no USD, so the
stated cap cannot fire). An empty `compose_crucible_critics` result leaves
the 501 in place. The file tells the reader not to mix grok-sgh with
sgh-api, and not to mix the Vertex coding account with Joanna's gem-api.
Import inserts this file's directory on `sys.path`.

## cosmos_cursor_rail.py

Cursor Cloud Agents rail against `api.cursor.com`, with the key under the
runtime root. Not a wrap of the legacy Cursor module. It refuses a
`core->models` route. The file notes a measured case where cloud agents
never started and Gitur credits did not move.

Public: `pin_cursor_model`. `CursorRailError`. `default_spec`, `merge_spec`,
`load_spec`, `write_spec`, `redact_key`, `read_key`, `identity_matches`.
`CursorRail` methods `key_last4`, `last_identity`, `probe`, `dispatch`.
`spec_path_for`, `key_path_for`, `probe_path_for`, `launch_path_for`,
`register_cursor_rail`, `attach_to_kernel`, `refuse_live_authority_attach`,
`inspect_live_kernel`, `gate`, `launch_run`, `run_coding_dispatch`, `main`.

Errors: `CursorRailError` kinds `BAD_SPEC`, `NO_KEY`, `BROKE` (dispatch
without a prompt, or a broken register), and `REFUSED` from
`attach_to_kernel` (same authority-attach refusal as the other coding
rails). Import inserts this file's directory on `sys.path`.

## cosmos_cvm_clock.py

About-2s CVM satellite for audio owner and UX (clock id 16). It does not
construct Kernel, append the authority ledger, bind a port, run STT or the
brain, or GET the phone. It is not the owner of `state/cvm/pull.json`.
That file's authoritative clock is id 18. This satellite merges cadence and
does not clobber drain keys.

Public: `poll_once`, `loop`, `standup`, `main`.

Errors: no error class. Failures stay in the daemon loop. CLI uses
`SystemExit`. Import inserts this file's directory on `sys.path`.

## cosmos_cvm_projection.py

CVM projection helpers. Not the ledger. Clock writes `state/cvm/pull.json`.
The phone snapshot is `state/cvm/phone.json`. The file says
`cosmos_service` re-exports these private helpers. This page did not
re-check that import.

Public: `CvmError` only. Every helper in this file starts with `_`.

Errors: `CvmError` kinds `UNPARSEABLE`, `BAD_SNAPSHOT` (kinds not an object,
inline PCM bytes instead of a sha256 pointer, `cvm` not 1, missing
`request_id`), `IDENTITY_MISMATCH` (pull `tree_id` is not the sentinel),
`CLIENT_ID_REQUIRED`, and `UNREADABLE`. `path.owner()` failure is swallowed
and replaced with a uid string.

## cosmos_cvm_push.py

Phone turn landing for `POST /api/v1/cvm/push`. It composes the projection
helpers. It does not copy their filters. `stamp_desktop_pull` is the one
pull-ticket writer helper described here. Desktop clock id 18 stays the
pull authority. Command-start STT is not that drain cycle.

Public: `phone_state`, `phone_cursor`, `pcm_pointer`, `speech_live`,
`cadence_mode`, `cadence_next_s`, `cadence_wait`, `load_cas_pcm`,
`voice_state`, `reset_voice_ack`, `set_voice_state`, `ack_listening`,
`ack_stt_none`, `probe_stt`, `transcribe_pcm`, `bind_phone_stt`.
`PlaybackGate` methods `arm`, `is_set`, `cancel`, `finish`. `stt_interrupt`,
`ticket_due`, `stamp_desktop_pull`, `merge_satellite_pull`,
`cvm_store_push`, `cvm_post`.

Errors: `ValueError` for a bad voice state, a ticket that is not an object
(`UNPARSEABLE`), and `IDENTITY_MISMATCH` when pull `tree_id` is not the
sentinel (`stamp_desktop_pull` and `merge_satellite_pull`). `CvmError`
kinds `BAD_SNAPSHOT`, `OWNER_CONTESTED`, `UNREACHABLE` (push stored nothing
the following GET could publish), and `NOT_FOUND`.

## What this page does not say

Forty files, letters A through C, none skipped. No module past
`cosmos_cvm_push.py` belongs in this slice. Parsing clean is not a runtime
proof. A name on this page is not a guarantee the live service calls it.
This slice is not a finished product.
