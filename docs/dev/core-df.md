# Core D–F

This slice is not a finished product. COSMOS is not finished. These pages
are a reading map of `cosmos/cosmos_*.py` whose names start with `cosmos_d`,
`cosmos_e`, or `cosmos_f`. They name the public surface. They do not paste
function bodies, and a name here is not a claim that the lane is proven,
attached, or safe to treat as done.

There is no `cosmos_e*.py` in `cosmos/`. The prefix is empty.

Public names below are module-level classes and functions that do not start
with `_`. Methods listed under a class are the same rule. A function that
exists only inside a generated job script is not a module function.
`cosmos_dispatch` re-exports the split helpers; those names are documented
on the module that defines them.

## `cosmos_delegate.py`

Delegation limits as scheduler jobs: depth, concurrency, stripped child
capabilities, and a report of stale children that does not re-run them.

Public: `DelegateError`. `Delegation` (`depth_of`, `spawn`, `snapshot`,
`children`, `sweep_stale`).

Errors: `Delegation.__init__` merges a caller `policy` over
`max_depth`, `max_children`, and `max_iterations`, so the constructor can
raise the caps the module says a caller cannot raise. `requested_iterations`
above the stored cap is ignored; the policy dict is not. `sweep_stale`
appends `JOB_STALE` when `stale_reported` is absent and never sets that
flag, so the same running child is reported again on every sweep. The fold
reads `scheduler._state` and `scheduler._clock`.

## `cosmos_derivation_audit.py`

Substring audit of a fixed site list: a derivation is classified primitive,
advisory, or still open. It does not flip tracker authority.

Public: `audit`, `main`.

Errors: a site is present when its `symbol` string occurs anywhere in the
file, not when an AST node matches. `parse_tracker_markdown` is still
`verdict=open` (markdown parse of `MOTIF_TRACKER.md`) and `main` still
exits 0 while that site classifies. `main` writes
`cosmos/_f36_derivation_audit.json` beside the module.

## `cosmos_discover.py`

Hourly rebuildable inventory of `docs/research/**/*_HANDS.md` plus a closed
PATH and local-HTTP probe table. No model call.

Public: `repo_tree`, `default_research_dir`, `plan_once_argv`,
`plan_task_argv`, `inventory_hands`, `probe_cmds`, `probe_http`, `bind`,
`read_heartbeat`, `heartbeat_age_s`, `write_heartbeat`, `poll_once`,
`install_task`, `standup`, `main`.

Errors: `pythonw_exe` is imported and unused. The heartbeat replace is
atomic; `hands.json` is a direct `write_text`, so a crash mid-write can
leave a torn projection. `install_task` treats any schtasks output
containing `denied` as an elevation failure.

## `cosmos_dispatch.py`

TYPE plus task in, a job file and collector row out. Native queue is the
resolver `queue` role. An explicit `--queue` is the BTS compatibility lane.
This file is the offload harness, not a finished dispatcher.

Public: `bind_paths`, `default_target_dir`, `default_dhx`,
`locked_returns_path`, `index_path_for`, `index_lock_for`, `inbox_dir`,
`worker_bucket_dir`, `worker_compat_dir`, `dispatch_map_path`,
`is_native_queue`, `infer_kind`, `infer_task_class`, `infer_default_agent`,
`resolve_lane_model`, `parse_agent_tag`, `resolve_kind`, `job_status`,
`wait_for`, `reconcile_return`, `dispatch`, `run_gate`, `main`.
`DispatchError` is re-exported from `cosmos_dispatch_workspace`.

Errors: the module text disagrees with itself. The header still describes
`claude -p` / F5 / Haiku jobs and says research defaults to groq. `dispatch`
raises `ANTHROPIC_OFF` for `claude`, `sonnet`, and `haiku`.
`RESEARCH_DEFAULT_AGENT` is `G46`, while `infer_default_agent`'s docstring
still says research goes to SSA. A comment says the Claude-family CLI was
proven, and `KIND_LIVE` marks those kinds `ANTHROPIC_OFF`. Cursor and Codex
stay `UNPROVEN`. `KIND_MODEL["cursor"]` is `composer-2.5`, and
`resolve_lane_model` rewrites an empty model, `grok-4.6`, Auto, and an
explicit Opus alias to that Composer id. The comment above that branch says
it pins Opus 5 and that Composer 2.5 already leaked. `cosmos_cursor_rail`
pins default coding to `grok-4.6`. `_timeout_for` has a dead
`WORKER_KINDS` branch after `gem` and `oa` are already handled.
`reconcile_return` marks the index row `returned` when `rc` is 0, or the
outcome is `CLEAN`/`FINDINGS`, or any `live_tree_id` is present, so a
non-zero result that still carries a tree id joins as returned. A stage-5
gem/oa task is rewritten only when `compose_critique_prompt` sets
`inlined`; missing files leave the path-only assignment in place.

## `cosmos_dispatcher_daemon.py`

Tag-routed drop daemon. Reads a small JSON drop, pulls a session tail,
attaches `docs/AGENT_BOUNDARIES.md`, and calls `dispatch`.

Public: `repo_tree`, `default_config`, `load_config`, `pause_flag`,
`bucket_root`, `per_agent_bucket`, `list_drop_files`, `parse_drop`,
`stage_processed`, `out_dir_for`, `assignments_path`, `process_drop`,
`poll_once`, `loop`, `standup`, `status_probe`, `main`.

Errors: `process_drop` sets top-level `ok` true when the drop was filed.
That is not a finished agent result. `stage_processed` copies the drop
into `processed/` when the move fails, then tries to rename the original
to `*.claimed`. If that rename also fails, the original drop stays in the
bucket and the next tick can dispatch it again. A missing boundaries file
refuses the drop (`NO_DIR`). `--loop` idles on `PAUSE.flag`. `--once`
still drains.

## `cosmos_dispatch_critique.py`

Stage-5 critic prompt builder. Inlines file bytes and a full-file sha256
so a remote rail is not handed paths it cannot open.

Public: `compose_critique_prompt`.

Errors: if no located file has a sha256, the return is `inlined` false and
the original assignment is unchanged. `dispatch` then sends that path-only
text. An assignment that already contains the begin-file mark and the
text `sha256=` is treated as already inlined and is not rebuilt.

## `cosmos_dispatch_jobs.py`

Renders one Python job script for a kind. Keys are paths in the script,
not literals baked into the string.

Public: `render_job`.

Errors: the module docstring says the Claude-family CLI is proven.
`render_job` raises `ANTHROPIC_OFF` for `claude`, `sonnet`, and `haiku`
and never calls `_claude_job`. Cursor and Codex scripts still label
themselves `UNPROVEN`. The Cursor script is generated with
`autoCreatePR: true`. Closed-over copies of `CLAUDE_KINDS`,
`WORKER_KINDS`, and the model ids must be kept in step with
`cosmos_dispatch` by hand. The Cursor model string is then passed through
`pin_cursor_model`, which does not use `KIND_MODEL["cursor"]`.

## `cosmos_dispatch_lanes.py`

BTS-compatible lane counts, least-loaded pick, job filename, and locate.
Native queue identity is not decided here.

Public: `lane_load`, `measure_lanes`, `pick_least_loaded`, `job_filename`,
`locate_job`, `returns_dir`.

Errors: `locate_job` loops over `jobs` and `jobs/running` and does not
test those paths. After the loop it only checks `queue/jobs/<name>`. A
file that exists only at `queue/jobs/running/<name>` comes back
`state=missing`. `LANE_ORDER` and the skip set are a second copy of the
tables in `cosmos_dispatch`.

## `cosmos_dispatch_stamps.py`

DHx assignment-log marker, collector index append, boundaries addendum,
and the inbox sidecar. Appends are locked.

Public: `append_dhx_marker`, `append_index_row`, `append_assignment_row`,
`append_session_assignment`, `repo_docs_dir`, `load_boundaries_text`,
`compose_agent_prompt`, `write_inbox_sidecar`.

Errors: lock timeout raises `DispatchError` kind `IO` and does not append.
`MARKER_SEP`, `DHX_ASSIGN_HEADER`, and `ONELINE_CAP` are a second copy of
the dispatch constants. A marker tail match is string equality on the
`lane/file` tail, so a changed assignment with the same tail is treated
as already stamped.

## `cosmos_dispatch_workspace.py`

Attempt-private clone fence. Refuses the live repo and the runtime root
outside `work/` as the coder cwd. The return is a proposal, not a commit.

Public: `DispatchError`. `assert_not_live_workspace`,
`clone_attempt_workspace`, `prepare_grok_workspace`,
`prepare_dual_lane_workspaces`, `collect_workspace_proposal`.

Errors: `prepare_dual_lane_workspaces` records the sibling path and does
not itself stop one lane from reading the other. The docstring says that
read is refused; the function says peeking is a later check. A failed
`git clone --local` is not deleted. The copytree fallback may land on a
`*-copyN` sibling, and that path is the workspace the caller gets. Clone
failure stays `BROKE` and does not fall back to the live tree.

## `cosmos_dom.py`

DOM attempt protocol: ephemeral profile, typed failure record, evidence
file, report rather than retry. The driver is injected.

Public: `DomError`. `Driver` (`start`, `navigate`, `session_ok`, `stop`).
`DomWorker` (`run_attempt`).

Errors: `DomError` is never raised. `run_attempt` returns a dict.
`start` / `navigate` failures are mapped. The evidence write and the
success ledger append sit outside that mapping, so they propagate as raw
exceptions. `stop` failures are swallowed. This file has no browser
implementation.

## `cosmos_drive_meter.py`

One-minute `shutil.disk_usage` satellite for a closed drive table plus
the runtime-root volume. A missing drive is `ABSENT`.

Public: `poll_once`, `standup`, `main`.

Errors: the tick's `ok` is hard-coded true. An `UNREADABLE` volume is
recorded on that drive and does not fail the tick. `seen` is filled and
never read. The meter does not honor `PAUSE`. `standup` can report
`in-process-tick` when scheduled-task creation did not succeed; `main`
still exits 0 because `started` is a non-empty string.

## `cosmos_duds.py`

Eight-layer outfit check, CPU checks on a saved reply, WOMBAT session
notes, and the Judge card. Summon functions do not exec a model.

Public: `DudsError`. `womb_root`, `layers_of`, `require_duds`,
`cpu_first_pass`, `cpu_pass`, `xform`, `score_problems`, `judge_audit`,
`gradable_sets`, `write_succession`, `sweep_idle`, `note_ccrew_summon`,
`note_final_summon`, `watch_spawn`, `summon_hero`, `on_saved_reply`,
`summon_judge`, `grade_pile`.

Errors: `summon_hero` builds a fallback session id from the model plus
`isoformat()`, then uses that string as a file name under `spawn/`. On
Windows, `:` is illegal, and a model id containing `/` or `:` splits or
rejects the path. `require_duds` refuses an ORC harness when the harness
string contains `cod`, which also matches words that are not a coding
seat. `on_saved_reply` sets `summon_judge` / `judge_waiting_duds` at the
judge floor and does not call `summon_judge`. `note_ccrew_summon` is not
called from this module and does not refuse a count under the order
floor. `grade_pile` says an empty pile retires the Judge, leaves
`retired` false, and does not clear `judge_seat.json`. `sweep_idle`
stores `queue_dry_30m` on the session and always writes the scar reason
`idle_30m`. A server-marker hit (`429`, `500`, `deprecated`, and the
other tokens in `SERVER_MARK`) closes the session even when the CPU rows
passed. `cpu_pass` does not require the three named checks, only that
the rows it was given say `PASS`.

## `cosmos_firecrawl_rail.py`

Satellite Firecrawl REST adapter, link `firecrawl-web`, route
`core` to `papers`. Keyless papers, scrape, and search. Not the default
web-search path.

Public: `FirecrawlRailError`. `default_spec`, `merge_spec`, `load_spec`,
`write_spec`, `redact_key`, `read_key`, `first_primary_id`,
`first_title`, `id_is_live`. `FirecrawlRail` (`last_identity`, `probe`,
`dispatch`). `spec_path_for`, `key_path_for`, `probe_path_for`,
`register_firecrawl_rail`, `attach_to_kernel`,
`refuse_live_authority_attach`, `inspect_live_kernel`, `gate`, `main`.

Errors: the module says an optional key unlocks crawl and map. `dispatch`
still returns `BROKE` for those verbs (`not in slice 1`) after the key
check. HTTP 402 and 429 are `BROKE`, not `UNREACHABLE`. `attach_to_kernel`
refuses the authority ledger unless `boot_compose` is true. The kernel
does not attach this rail at boot. Papers success requires an `arxiv:`,
`doi:`, or `pmid:` id. `key_path_for` ignores the spec argument.

## `cosmos_forge_bg.py`

Detached OpenRouter CLI workers for Forge research, arch, and the two
consensus stages. Does not start implement and does not write the live
tree.

Public: `ForgeBgError`. `bg_dir`, `pick_free_coders`, `pick_cheap_coders`,
`status`, `facilitate`, `start`, `worker_main`.

Errors: `start` returns `ok` true even when a detached spawn record is
not ok. `pick_free_coders` accepts `http` and does not use it. `status`
returns `ok` true when a run file does not parse (`kind` `BROKE` on that
row only). `facilitate` reads `status`, and `status` keeps only the last
twelve run files, so the bar is not the full stage directory. If the
worker raises before it writes the out file, that run never appears.
`worker_main` stores `n_chars` and may leave `tokens` null; `status`
then copies `n_chars` into `tokens`.

## `cosmos_forge_rail.py`

Two CLI forge hands in one module: `gitlab-forge` (`glab`) and
`github-forge` (`gh`). Probe binds an authenticated identity value, not
a version string. No COSMOS-held forge secret.

Public: `ForgeRailError`. `default_spec`, `merge_spec`, `load_spec`,
`write_spec`, `spec_path_for`, `probe_path_for`. `ForgeRail`
(`last_identity`, `probe`, `dispatch`). `register_forge_rails`,
`attach_to_kernel`, `main`.

Errors: any non-zero `gh` / `glab` exit, including a logged-out CLI, is
`UNREACHABLE`. There is no separate auth kind. Pipeline refusal is a
substring match on the argv tail (`workflow run`, `release create`, and
the other needles), so a non-pipeline argument that contains one of
those phrases is refused. A dispatch that is not the identity verb
returns raw stdout and does not lift a forge-only field. Registration
still records a link whose binary is absent. `attach_to_kernel` refuses
an authority-ledger register unless `boot_compose` is true.
