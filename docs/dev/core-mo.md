# Core M–O

This slice is not a finished product. It is a reading map of the 23
`cosmos/cosmos_*.py` modules whose names start with `cosmos_m`,
`cosmos_n`, or `cosmos_o`. Each entry is a one-line role, the public
classes and functions by name, and errors visible in that file. Private
helpers are omitted. Function bodies are not pasted. Nothing here is a
second service, and nothing here is a claim that COSMOS is finished.

## cosmos_mail.py

Per-worker immutable mailbox: hash-chained notes, optional HMAC and
`cosmos_lock` fence, and a probe that keeps missing, empty, unreadable,
and stale apart.

Public: `assert_split_tree`, `resource_for`, `msg_sha256`, `writer_sig`.
Classes: `MailError`, `ProbeResult`, `Mailbox` (`register`, `send`,
`unread`, `ack`, `receipt_for`, `probe`).

`MailError` kinds: `SHARED_TREE`, `MAILBOX_MISSING`, `SELF_SEND`,
`TORN_MESSAGE`, `CHAIN_BREAK`, `FORGED_MESSAGE`. Probe states are
`MISSING`, `EMPTY`, `UNREADABLE`, `STALE`, `LIVE` and are not raises.
A keyed mailbox still accepts a note whose `signed` flag is false, so
the signature check does not run. `send` builds the chain tip by
skipping unreadable JSON and notes with no `msg_sha256`; `unread` then
raises on those same files. A non-numeric `epoch` is skipped on send
and can escape `unread` as a bare `ValueError`. A missing `body` is a
bare `KeyError`, not `MailError`. `probe` uses file mtime and does not
verify the hash or the chain. `ack` writes a receipt without checking
that the id exists.

## cosmos_makers.py

Ledger-backed map of places where agents, tools, connectors, skills,
roles, and wrappers can be made. Registration is not a liveness probe.
There is no delete.

Public class: `MakerError`. Class `MakerMap` (`add`, `load`, `state`,
`list`, `find`). No module-level functions.

`MakerError` kinds: `UNKNOWN_KIND`, `BAD_ENTRY`, `DUPLICATE`,
`UNREADABLE`. A second `MAKER_ADDED` for the same id makes `state`
raise `DUPLICATE`, so the map cannot be read until that drift is
dealt with outside this module. The file notes that cDeck
`CREATE_KINDS` must match `MAKER_KINDS` and does not enforce that here.

## cosmos_master_desc.py

Stdlib OOXML renderer for `docs/COSMOS_MASTER_DESCRIPTION.docx` from
`docs/COMPETENCY.toml`. The repo-root incumbent docx is outside this
fence.

Public: `repo_tree`, `competency_path`, `default_out`,
`load_competency`, `extract_text`, `render`, `main`. No class.

A bad competency file raises an untyped `RuntimeError` (`BAD_SCHEMA`).
`extract_text` decodes only a short entity list. `render` sets `ok`
from substrings of the file it just wrote (`ITERATE` pin, `code-build`,
`G46`, `not 5→8`). That is not a live-tree proof.

## cosmos_mcp.py

Stdio newline JSON-RPC MCP server. Tools: `cosmos_status`,
`cosmos_submit`, `cosmos_jobs`, `cosmos_audit`, `cosmos_health`,
`cosmos_command`, `cosmos_events`. Each call is supposed to go through
the kernel.

Public class: `MCPServer` (`handle`, `serve_stdio`). No error class.

JSON-RPC: `-32700` parse, `-32601` unknown method, `-32602` unknown
tool or missing argument (`KeyError`, including a missing tool name),
`-32603` any other exception, with the exception text in the message.
`cosmos_jobs` reads `sched._state()`. There is no Content-Length
framing.

## cosmos_mcp_client.py

Outbound stdio MCP client: long-lived child, tree-kill, OpenAI-shaped
tool conversion, and a deny list. Does not edit `cosmos_mcp.py`.

Public: `convert_tool_format`, `openai_tools_from_mcp`, `named_servers`,
`npx_argv`, `tree_kill`, `main`. Classes: `McpClientError`,
`StdioTransport` (`pid`, `start`, `send`, `recv`, `stderr_tail`,
`close`), `FakeTransport` (`start`, `send`, `recv`, `stderr_tail`,
`close`), `McpClient` (`start`, `tools_list`, `tool_names`,
`tools_call`, `close`; also a context manager).

`McpClientError` kinds actually raised: `BAD_SPEC`, `UNREACHABLE`,
`BROKE`, `DENIED`, `REFUSED`. The class comment also names `TIMEOUT`,
but waits raise `UNREACHABLE` with the word TIMEOUT in the detail.
`named_servers` swallows any import failure and still returns
`ok: true` with an empty tool list. `tree_kill` is `taskkill /T` on
Windows and a single-pid `SIGKILL` elsewhere. The cookbook filesystem
MCP package is refused by `npx_argv`.

## cosmos_meter_window.py

Pure UTC today-and-trailing-week fold for the cDeck meter strip. The
caller supplies events and the clock. This module does not open the
ledger or the wall clock.

Public: `meter_window`. Class: `MeterWindowError`.

Kinds: `BAD_INPUT`, `BAD_CLOCK`, `BAD_ROW`. Counts the row does not
carry stay `UNMEASURED`. One missing token count blanks that count for
the whole window; a carried 0 stays 0. Dollars sum only priced rows.
Skipped ledger events (`BUDGET_SET`, reservations, releases, denials,
`RUN_FAILED`, credits, tolls, quota) are dropped. Any other named
event is `BAD_ROW`. A naive clock-time string is refused; a bare date
is treated as UTC midnight. Payload fields overwrite the event shell
before token and price checks, so a disagreeing shell value is not
reported. Timestamps on `t` and `at` are required to match.

## cosmos_migrate.py

Reads an incumbent tools registry and declares contracts on
`cosmos_tools`. Ingestion does not verify a port. The report is the
whole contracts projection, not only this ingest.

Public class: `Migrator` (`ingest`, `report`). No error class of its
own. `ToolsError` other than `DUPLICATE` escapes `ingest`.
`_try_disposition` swallows every `ToolsError`, so a bad decision or a
ledger failure looks like "tool was not in the registry." A registry
that is neither a list nor an object raises `AttributeError`.
`bts_health` is recorded as `REPLACED` with the reason "planned on
kernel selftests."

## cosmos_model_rater.py

Local catalog, seats, job estimate, and observed porosity for cDeck.
Refresh reads OpenRouter `GET /api/v1/models`. It does not call the
rotating `openrouter/free` router. Seat assignment is explicit.
Unmeasured axes stay `UNMEASURED`.

Public class: `ModelRaterError`. Functions: `dir_for`, `catalog_path`,
`porosity_path`, `seats_path`, `job_est_path`, `family_of`,
`default_policy`, `normalize_policy`, `is_banned`, `is_favored`,
`normalize_row`, `quality_score`, `blended_per_m`,
`apply_aa_benchmarks`, `inherit_variant_quality`, `load_catalog`,
`default_seats`, `load_seats`, `save_seats`, `save_catalog`, `refresh`,
`query_models`, `normalize_via`, `set_model_cap`, `default_porosity`,
`load_porosity`, `save_porosity`, `apply_porosity`, `complement_pack`,
`record_porosity`, `normalize_effort`, `assign_seat`, `set_policy`,
`scan_roles`, `add_adversary`, `remove_adversary`,
`default_job_estimate`, `load_job_estimate`, `save_job_estimate`,
`reset_job_estimate`, `job_costs`, `estimate`, `snapshot`,
`hermes_probe`, `main`.

Kinds raised: `NO_KEY`, `AUTH_REQUIRED`, `UNREACHABLE`, `BROKE`,
`BAD_INPUT`, `REFUSED`. The class comment also lists `BAD_ROOT`; the
CLI prints that kind when `--root` is missing and does not raise
`ModelRaterError`. Rotator ids, banned models, and an empty
`forge.ccr` seat are `REFUSED`. Porosity stays `UNMEASURED` until an
observation is recorded. `scan_roles` is a named catalog, not a live
grep of the tree.

## cosmos_motif_define.py

DEFINE-first gate. Frozen problem statement before BUILD or CRITICS.
Does not start Gitur and does not invent traces.

Public: `stage_graph`, `frozen_statement`, `require_frozen_statement`,
`assert_run_stage`. Class: `MotifDefineError` (`REFUSED`, `BAD_STAGE`).

`frozen_statement` swallows every exception from the studio pack and
falls through to the profile engine, so a broken studio file looks
like an empty studio statement. `require_frozen_statement` returns
without error for stages other than `build` and `critics`.
`assert_run_stage` refuses those other names. Import inserts `cosmos/`
on `sys.path`. Running the file with no arguments runs the self-test,
which installs a temporary tree.

## cosmos_motif_driver.py

Mechanical MOTIF clock. Reads the tracker and collector notes, drops
the next Grok Build job, and writes the tracker plus a JSON
projection. It does not flip markdown authority. `flip_ready` is
advice. The agreement streak target is 96 ticks.

Public: `repo_tree`, `default_runtime_root`, `default_tracker`,
`default_collector_md`, `default_dhx`, `canonical_slug`,
`plan_task_argv`, `query_task`, `install_task`, `parse_tracker`,
`critique_exists`, `effective_stage`, `motif_token`, `is_receipt`,
`inflight_filenames`, `ledger_inflight`, `ledger_paths`,
`write_tracker_json`, `stage_map_for`, `compare_projection`,
`record_agreement`, `release_completed`, `is_advancing`,
`next_job_task`, `write_heartbeat`, `update_tracker`, `drive_once`,
`standup`, `main`. No error class.

`stage_map_for` turns any per-slug exception into `(None, None)`.
`release_completed` drops a failed `release` with `pass`, so the
caller cannot see it. An unreadable lease store skips the tick
(`lease_unreadable`) instead of dispatching. `drive_once` still
returns `ok: true` when individual dispatches failed. Queue filenames
and `COLLECTOR.md` are advisory only. `standup` takes no root; the
clock matrix calls it that way.

## cosmos_motif_run.py

BUILD/CRITICS run record after the define gate. Passing the gate does
not launch Gitur, invent a PR trace, or write the live tree.

Public: `start`. No class. Failures are `MotifDefineError`. Import
inserts `cosmos/` on `sys.path`. A bare run executes the self-test.

## cosmos_newai_scout.py

Propose-only discovery of names that are not already in the known
folds. It does not write `COMPETENCY.toml`, makers, or rails.

Public class: `ScoutError`. Functions: `repo_tree`, `fold_name`,
`known_folds`, `parse_catalog`, `default_http`, `path_present`,
`propose`, `bind`, `poll_once`, `plan_task_argv`, `install_task`,
`standup`, `main`.

The class comment lists `NO_ROOT`, `BAD_CATALOG`, and `UNREACHABLE`.
The only `raise` in this file is `BAD_CATALOG`. A failed remote fetch
is a source row `kind: UNREACHABLE` while the tick itself stays
`ok: true`. `bind` creates log and discovery directories even on
`dry_run`. `standup` sets `proof.ok` true even when the task was only
planned and no tick ran.

## cosmos_nlcron.py

Natural-language cadence parser onto the Windows clock vehicles
`schtasks`, `detached_daemon`, and `onlogon`. Parser only. It does not
create a task, spawn `schtasks`, or start a timer.

Public: `parse_cadence`. Class: `NlcronError` (`UNRECOGNIZED`).

Unparseable or ambiguous phrases raise. Sub-minute phrases are
`detached_daemon`, not `schtasks` with a modifier under one minute.
This read did not show a second error class.

## cosmos_node_bucket_worker.py

Grok and GEM bucket daemon with an `O_EXCL` fence. One script, `--node
grok|gem`. Result files go to V, GDX, or ODX. This is a later cut of
the node worker, not a replacement that removed it.

Public class: `WorkerError` (`BAD_NODE`, `BAD_OUT`, `BAD_TASK`,
`NO_DEST`, `NO_KEY`, `NO_ROOT`, `REPLAY`). Functions: `canon_node`,
`node_spec`, `make_worker_id`, `load_config`, `pause_flag`,
`pause_decision`, `bucket_dir`, `v_returns`, `canon_out`, `dest_dir`,
`list_drop_files`, `parse_task`, `fence_path`, `write_fence`,
`claim_drop`, `stage_drop`, `execute_via_rail`, `write_result_files`,
`process_drop`, `poll_once`, `loop`, `status_probe`, `build_parser`,
`run_cli`, `main`.

`oa` is not a node here. `cosmos_own_clocks` does not stand this
module up; grok and gem clocks point at other bucket scripts.

## cosmos_node_rails.py

Adapters that import incumbent node clients (`bts_sgh`, `bts_gem`,
`bts_gw`, `bts_oa_api`) and register them for the dispatcher. A failed
import is unreachable, not a fake success. The header also names a
cursor client. The spec list does not register one.

Public: `resolve_incumbent_root`, `fail_closed_empty`,
`register_node_rails`. Class: `NodeRail` (`probe`, `dispatch`). No
error class.

`probe` true means the module imported, not that the model answered.
`dispatch` treats a dict that omits `ok` as success when the text is
non-empty, and treats a non-dict return as success. Empty text is
forced to `ok: false` (`EMPTY_OUTPUT`, rc 2). `register_node_rails`
swallows every `set_budget` exception and still returns the adapters.
The incumbent root is appended to `sys.path` for the process. Boot is
not supposed to receive the real registry here; a comment says passing
it registers rails that have not answered.

## cosmos_node_worker.py

Grok, GEM, and OA bucket workers. Each node polls its own bucket and
writes the result folder directly. No `bts_*` import in this file.
Claude CLI names are refused (`ANTHROPIC_OFF`).

Public class: `WorkerError` (`BAD_NODE`, `BAD_OUT`, `BAD_TASK`,
`NO_DEST`, `NO_KEY`, `NO_ROOT` — no `REPLAY`, unlike the bucket
worker). Functions: `canon_node`, `node_spec`, `script_for`,
`load_config`, `pause_flag`, `is_paused`, `bucket_dir`, `v_returns`,
`canon_out`, `dest_dir`, `list_drop_files`, `parse_task`,
`stage_drop`, `execute_via_rail`, `write_result_files`,
`register_return`, `land_critique_return`, `process_drop`,
`execute_handoff`, `poll_once`, `loop`, `standup`, `status_probe`,
`build_parser`, `run_cli`, `main`.

Empty rail text is `FAILED`, not a fake done. This module and
`cosmos_node_bucket_worker.py` both still claim grok and gem buckets.
The clock matrix does not name this file.

## cosmos_oa_worker.py

Thin CLI wrapper. `main` calls `cosmos_node_worker.run_cli` with node
`oa`.

Public: `main`. No class. `CosmosPathError` and `WorkerError` exit 2.
The wrapper is not in the `cosmos_own_clocks` matrix.

## cosmos_openrouter_rail.py

Named-model OpenRouter satellite rail. The rotating `openrouter/free`
id, unpinned `:free` ids, `~latest`, unknown endpoint uuids, and
`allow_fallbacks=true` are refused (silent model swap). Not a second
Core.

Public class: `OpenRouterRailError` (`NO_KEY`, `BAD_SPEC`, `BAD_ROOT`,
`UNREACHABLE`, `AUTH_REQUIRED`, `BROKE`, `REFUSED`). Class
`OpenRouterRail` (`last_identity`, `submit_batch`, `get_batch`,
`probe`, `dispatch`, `fetch_generation`). Functions: `default_spec`,
`model_refused`, `cache_family`, `tag_preload`, `merge_spec`,
`load_spec`, `write_spec`, `redact_key`, `read_key_file`, `read_key`,
`fold_usage`, `usage_dir`, `usage_path`, `record_usage`,
`snapshot_usage`, `spec_path_for`, `key_path_for`, `probe_path_for`,
`register_openrouter_rail`, `attach_to_kernel`,
`refuse_live_authority_attach`, `gate`, `main`.

`attach_to_kernel` raises `REFUSED` on an authority ledger unless
`boot_compose=True`. Many refusals on `dispatch` are returned as
`ok: false` rather than raised. Key bytes are redacted on the way out
of the helpers that say so; this file still reads the key file.

## cosmos_or_fill_first.py

OpenRouter key-file cursor. Stick on the current file until HTTP 402,
or until a second 429. The first 429 retries that same file.
Round-robin is refused. `pick` returns a file name, never key bytes,
and does not create directories.

Public class: `FillFirstError` (`BAD_STATUS`, `NO_KEYS`). Functions:
`view`, `pick`, `note_status`.

A broken state file is `kind: BROKE`, and `pick` still returns the
first present key under that kind. The lock is a process-local
`threading.Lock`, so two processes can move the cursor. `note_status`
creates the state directory; `pick` does not. No key files is
`UNMEASURED` from `pick`, and `NO_KEYS` from `note_status`.

## cosmos_orc_boot.py

cDeck ORC BootUP: inspect close state, optional TidyUP plus TU2, then
`start_session` for one of `Cm`, `plumbing`, `physics`, `chapter`,
`legal`. Does not spawn OpenWork and does not write `V:\Ai`.

Public class: `OrcBootError` (`BAD_STREAM`, plus whatever
`SessionError.kind` was). Functions: `inspect_boot`, `boot`.

`inspect_boot` does not read or verify an HMAC. It checks that
`SEED.json` and `SEED.decl.json` exist and compares mtimes. The
`elif seed_ok` branch is unreachable. `ok` is true for `NO_SEED` and
`PARTIAL`. If the kind is not `GOOD_CLOSE`, `boot` calls
`close_session(..., force=True)` before the already-open check, so a
still-open Core session whose running file is newer than the seed is
force-closed. `ALREADY_LIVE` runs only when the inspect kind was
already `GOOD_CLOSE`.

## cosmos_orch_hands.py

Fail-closed hands for the orchestrator. Consequential hands do nothing
unless `confirm` is true. `dispatch_grokbot` does not spawn
`grok.exe`. Coding verbs exist only when a `code_root` is injected.

Public: `make_hands`, `hand_schema`. No class. The callables are
`get_session`, `select_project`, `invoke_bootup`, `dispatch_job`,
`dispatch_grokbot`, and, when a code root is set, `Read`, `Write`,
`Edit`, `Glob`, `Grep`, `Bash`.

Returned kinds include `REFUSED`, `UNMEASURED`, `BAD_INPUT`,
`NO_BOOT`, `NO_DESK`, `NAMED`, `MEASURED`, plus `CodeToolError.kind`.
`confirm` accepts `True` or the string `"true"` only.
`select_project` with confirm and no setter returns `ok: true`,
`kind: NAMED`. `get_session` maps every exception to `UNMEASURED`.
`dispatch_grokbot` refuses only when the task text contains
`grok.exe`.

## cosmos_orchestrator.py

Bounded tool loop over an injected `model_call`. This module does not
open the network. Spend is the caller's problem. The loop cap is 8
model calls.

Public class: `OrchestratorError` (`BAD_INPUT`, `MODEL_FAILED`,
`BAD_MODEL_RESPONSE`). Class `Orchestrator` (`run`). Functions:
`make_search_files`, `make_search_itc`, `build_tools`.

In-band results, not raises: `UNKNOWN_TOOL`, `BAD_ARGUMENTS`,
`TOOL_FAILED`, `TOO_MANY_TOOL_CALLS`, `EMPTY_MODEL_REPLY`,
`MAX_STEPS`. The header still says this module writes nothing and that
`get_session`, `select_project`, `invoke_bootup`, `dispatch_job`, and
`dispatch_grokbot` are not built. `build_tools` wires those hands, and
`TOOLS_SCHEMA` advertises them. With a `drop_fn`, a confirmed
`dispatch_job` drops work. `max_steps=True` passes the `int` check
because `bool` is an `int`.

## cosmos_own_clocks.py

One standup and one status matrix for the COSMOS Windows clocks named
in this file. It does not itself modify kernel, ledger, sched, or
service. Task names are `COSMOS <x>`.

Public: `matrix`, `standup_all`, `main`. No class. A bad root surfaces
as `CosmosPathError` from the path resolver. An unknown standup name
or a raising satellite returns `ok: false` with the error text.
`cvm_dt` returns `ok: true` and `ran: false`; it only emits commands
and does not run `schtasks`.

The header says "the dozen" clocks. The `CLOCKS` table is larger
(ids through 28, 27 standup names). The default root is the drive
literal `V:\A\Ai\COSMOS\live`. Top-level `ok` is "every primary task
in the matrix is registered." A missing logon task does not fail that
flag. Grok and gem logon commands name `cosmos_grok_bucket_worker.py`
and `cosmos_gem_bucket_worker.py`, not `cosmos_node_worker.py` or
`cosmos_node_bucket_worker.py`. `cosmos_oa_worker.py` is not in the
matrix. `newai_scout` standup can look successful in this fold when
its own proof says ok without a registered task (see that module).

## Not finished

This M–O slice is not a finished product. The modules above disagree
with each other in places (two bucket workers, a clock matrix that
does not seat them, an orchestrator header that denies the hands it
loads, probes and ticks that report ok without the check the comment
names). Treat the names and the errors as a map of the tree that is
there, not as a ship statement.
