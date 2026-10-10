# Core G–I

This slice is not a finished product. COSMOS is not finished. This page is a reading map of the seventeen `cosmos/cosmos_*.py` modules whose names start with `cosmos_g`, `cosmos_h`, or `cosmos_i`. It names each file’s role, its public classes and functions, and errors visible in that file. It does not paste function bodies. It is not a second service, and it is not a claim that these modules are done or fully tested.

Paths below are under `cosmos/`. Private helpers (names starting with `_`) are omitted. A class constructor is not listed again. Typed `kind` strings are the errors the module itself names.

## `cosmos_gem_bucket_worker.py`

GEM bucket daemon entry: polls only the `gem` bucket and hands the claim to `cosmos_bucket_daemon` (vertex-coding path). It does not modify kernel, ledger, sched, or service.

Public: `main`.

Errors: no class of its own. `CosmosPathError` and `WorkerError` print and exit 2. The same `gem` bucket is also claimed by `cosmos_gem_worker.py` through a different executor and a different heartbeat file. Two live entry points can both believe they own that bucket.

## `cosmos_gem_free_rail.py`

Satellite API rail `gem-free`: Google AI Studio Developer API (`generativelanguage.googleapis.com`). Not Vertex `gem-api` and not `gemini.cmd`. Billing-linked or exhausted quota is HTTP 429 and must not be reported green.

Public: `GemFreeRailError`. `default_spec`, `merge_spec`, `load_spec`, `write_spec`, `redact_key`, `read_key`. `GemFreeRail` methods `last_identity`, `probe`, `dispatch`. `spec_path_for`, `key_path_for`, `probe_path_for`, `register_gem_free_rail`, `attach_to_kernel`, `refuse_live_authority_attach`, `gate`, `main`.

Errors: `GemFreeRailError` is raised only as `BAD_SPEC` (bad overlay, schema, base, or key file name) and `REFUSED` (`attach_to_kernel` on the authority ledger unless `boot_compose=True`). The class comment also names `NO_KEY`, `BAD_ROOT`, `UNREACHABLE`, `AUTH_REQUIRED`, `QUOTA_DEAD`, and `BROKE`. Those are record kinds, not raises. A missing key is turned into a synthetic HTTP 401 and then `AUTH_REQUIRED`. `probe` returns `(ok, detail)`; `dispatch` returns a dict. `register_gem_free_rail` accepts `spend_gate` and discards it. `gate` can mark PASS from HTTP 200 plus a model string. The prompt asks for the token `GEM_FREE_READY`, and that token is not checked. When the body has no vendor model field, the model string falls back to the requested id, so a PASS can be the request echoed, not a vendor-emitted model.

## `cosmos_gem_worker.py`

Thin GEM worker: `cosmos_node_worker.run_cli(node="gem")`. Spend-gated rail path, not the vertex bucket daemon above.

Public: `main`.

Errors: `CosmosPathError` and `WorkerError` exit 2. Same dual-owner overlap as `cosmos_gem_bucket_worker.py`. The usage comment embeds a drive-letter root; the module does not resolve that path itself.

## `cosmos_gitlab_duo_rail.py`

GitLab Duo COM rail (`gitlab-duo-com`): `glab` identity plus a trigger roster. Probe lists triggers. It does not start a pipeline. Dispatch of CI or Duo execute verbs needs `execute=True`. The trigger token file is an existence check; this page does not describe its contents.

Public: `GitlabDuoComRailError`. `default_spec`, `merge_spec`, `load_spec`, `write_spec`, `spec_path_for`, `probe_path_for`, `trigger_token_path_for`, `hands_configured`, `cdeck_map`. `GitlabDuoComRail` methods `last_identity`, `probe`, `dispatch`. `register_gitlab_duo_com_rail`, `attach_to_kernel`, `live_call_shape`, `main`.

Errors: `GitlabDuoComRailError` kinds that are raised: `BAD_SPEC` (overlay type, token file name, argv given as a string), `UNREACHABLE` (trigger row with no id), `REFUSED` (execute phrase without `execute=True`, and authority attach outside kernel boot). The class comment also names `BAD_ROOT` and `NO_HANDS`; this file does not raise those. Missing hands makes `probe` return false with an `UNMEASURED` detail string. `dispatch` does not use that hands check, so it can still call `glab`. The execute refusal is a phrase match on the joined argv, not a closed command allowlist. `load_spec` maps `JSONDecodeError` to `BAD_SPEC` and lets `OSError` escape. `merge_spec` overwrites a foreign schema instead of refusing it. A non-zero `glab` exit, a timeout, and a missing binary are all folded into `UNREACHABLE`.

## `cosmos_gitur.py`

Rebuildable Gitur projection for `GET /api/v1/gitur`: GitHub, GitLab, and Cursor as one build triad, plus jukebox, work-order, crew, and credential folds. CLI failure is supposed to stay `UNMEASURED`, not an invented PR list. Not a live-tree writer.

Public: `GiturError`. `request_default_review`, `github_live`, `vendor_lives`, `gitlab_live`, `cursor_live`, `snapshot`.

Errors: `GiturError` is constructed and never raised. Callers get dicts. Kinds in those dicts include `REFUSED` (bad PR number or empty repo), `UNMEASURED` (CLI missing, or a review `via` that is not Cursor), `UNREACHABLE`, `BROKE`, `BUSY` (fold already in flight and no cached payload), and `OK`. `snapshot`’s own line says it does not vendor-poll; the uncached fold calls `vendor_lives`, which runs `gh`, `glab`, and a Cursor `GET /v1/me`. A per-repo `gh` exception is swallowed into an empty list while the parent result stays `kind=OK`, so a failed walk looks like a measured zero. A failed GitLab MR list is the same: identity can be `OK` with `mrs` left empty. `request_default_review`, when no launch hook is injected and the reviewer is Cursor, falls back to a drive-letter live root instead of the caller’s resolver root. The 10-second snapshot cache is process memory; a `BROKE` fold clears the busy flag and does not keep a partial board.

## `cosmos_grok_bucket_worker.py`

GROK bucket daemon entry: polls only the `grok` bucket and executes through the sgh-api then gw-api rail via `cosmos_bucket_daemon`.

Public: `main`.

Errors: `CosmosPathError` and `WorkerError` exit 2. The same `grok` bucket is also claimed by `cosmos_grok_worker.py` with a different heartbeat. Two entry points, one bucket.

## `cosmos_grok_worker.py`

Thin GROK worker: `cosmos_node_worker.run_cli(node="grok")` on the sgh-then-gw rails.

Public: `main`.

Errors: same exit-2 pair as the bucket daemon, and the same dual-owner overlap. The usage comment embeds a drive-letter root.

## `cosmos_groq_rail.py`

Satellite API rail `groq-api`: GroqCloud chat completions. Not xAI Grok. Default cheap model is `openai/gpt-oss-20b`. Runtime binding is the `model` field on the response. Budget on the spec is $0. Batch and Flex stay dark. Kernel attach is marked backlog: `attach_to_kernel` refuses the authority ledger unless `boot_compose=True`.

Public: `GroqRailError`. `default_spec`, `model_refused`, `merge_spec`, `load_spec`, `write_spec`, `redact_key`, `read_key`. `GroqRail` methods `last_identity`, `probe`, `dispatch`. `spec_path_for`, `key_path_for`, `probe_path_for`, `register_groq_rail`, `attach_to_kernel`, `refuse_live_authority_attach`, `inspect_live_kernel`, `gate`, `main`.

Errors: raised `GroqRailError` kinds are `BAD_SPEC` (overlay, schema, rail type, base, key file name, refused default model) and `REFUSED` (authority attach). The class comment also lists `NO_KEY`, `BAD_ROOT`, `UNREACHABLE`, `AUTH_REQUIRED`, and `BROKE`. A missing key becomes a synthetic 401 and then `AUTH_REQUIRED`. `BAD_ROOT` and `BAD_ARGS` are CLI JSON, not raises. `model_refused` blocks an empty id, Mixtral, Llama 3.x, and Whisper; `dispatch` returns `REFUSED` for those and for `service_tier` `flex` or `performance`. HTTP 429 is `BROKE`, not its own quota kind; rate-limit headers are copied onto the record when present. `probe` is green only when HTTP 200 and the default model id is in `GET /models`. `dispatch` is green on HTTP 200 plus a response model, even if the text is empty. `register_groq_rail` discards `spend_gate`. `gate` PASS also requires the isolated attach refusal and `kernel_attached` false. The chat prompt asks for `GROQ_READY`; the predicate does not read that text. `inspect_live_kernel` folds every exception into `error` and `opened: false`.

## `cosmos_head.py`

Chooses one host as head (`cosmos`, `openwork`, `cowork`, `hermes`, `cursor`). Overlapping features get one owner; the others stay shadow. Default when the file is missing is `openwork`. It does not load a plugin and does not start a host. The record is `state` role, `cdeck/head.json`.

Public: `HeadError`. `harmonize`, `load_head`, `set_head`.

Errors: `HeadError` kinds `BAD_HEAD` (unknown id), `UNREADABLE` (OS or JSON error), `UNPARSEABLE` (JSON that is not an object). `load_head` recomputes features from the in-code table and drops a stored model and timestamp. `set_head` always stamps Muse unless the head is Hermes, which stamps Solar. The directory create on the state path is not wrapped in `HeadError`. The CLI only runs the self-test; any other argv exits 2.

## `cosmos_head_gate.py`

Refuses a “synced” claim unless `git rev-list --count origin/main..HEAD` is a measured 0. It does not join-commit and it does not edit the kernel. Unmeasured is not synced.

Public: `measure_ahead`, `head_gate`, `main`.

Errors: `head_gate` raises `WarnRefuse` from `cosmos_warn`, kinds `HEAD_UNMEASURED` (count failed; `measure_ahead` returns -1, never a guessed 0) and `NOT_SYNCED` (count is not 0). The ref is ahead-only. A branch that is behind `origin/main` and not ahead still measures 0 and is treated as synced. If the given path has no `.git` and its parent does, the count runs in the parent (one step, not a search). `main` only runs the self-test. It does not apply the gate to a repo.

## `cosmos_health.py`

One board: each built-in row is a callable that must be able to go red or green. Results are ledgered as `HEALTH_BOARD`. `snapshot` is what `GET /api/v1/health` imports.

Public: `HealthBoard` methods `add_row`, `run`. `snapshot`.

Errors: a row that raises becomes red with `row RAISED …`. It does not escape `run`. The planted row `negative control (must be RED)` is red by design. If that row is green, the verdict is `BOARD-BROKEN`. Other rows all green is `GREEN`. Otherwise `RED xN`. If every real row is red and the detail strings share one leading token before `:`, the diagnosis is `SHARED-CAUSE`. The resolver row’s detail always says the sentinel is present, including when the boolean is false. The ledger-chain row is green for an empty verify. The lease row is green whether the tree lease is held or free. The queue row calls the scheduler’s private `_state`. `run` appends `HEALTH_BOARD` even when the verdict is red or the board is broken.

## `cosmos_health_clock.py`

About a 2-second liveness clock. It does not construct `Kernel` or `HealthBoard`, so it does not append `HEALTH_BOARD`. It checks the sentinel, the authority file’s presence, the install key file’s presence, the queue directory, pause, TCP `127.0.0.1:8770`, and peer heartbeat ages. With supervise on (the default), it can start `cosmos.py serve` on port 8770. `--no-supervise` only observes.

Public: `repo_tree`, `poll_once`, `loop`, `standup`, `main`.

Errors: this module has no error class. Supervise result kinds are `DISABLED`, `ALREADY_UP`, `PAUSED_HOLD`, `BACKOFF`, `CHILD_ALIVE`, `SUPERVISOR_BUSY`, `SPAWNED`, `SPAWN_FAILED`. A missing authority file is row-ok (“empty history is legal”). A present file is ok from size and mtime only. This clock does not verify the chain. Peer heartbeats are always row-ok, including when every peer is absent or dead. `serve_8770` down is a red. `poll_once` still sets its own `ok` true after a red board, and `--once` exits 0 anyway. `netstat` failure is treated as no listener; together with a failed connect, that is the path that can start a second serve. A HOLD pause blocks the spawn. A resume-gate pause does not. An unreadable pause flag is treated as hold. `loop` catches every tick exception, writes `health_clock.err`, and keeps sleeping. `CosmosPathError` at the CLI exits 2.

## `cosmos_identity.py`

Install identity (`MESH_ID` `KMesh`, owner Keith) and the federation seam. Peers `JMesh` and `HMesh` are named as building and planned. LAN nodes `SRV1` and `T7` are declared with `host` unset and `status` `not_installed`. An ambiguous G mesh id is left unassigned on purpose. Federation is not ready while any blocker stands.

Public: `FederationError`. `lan_node`, `probe_lan_node`, `federation_blockers`, `federation_ready`.

Errors: `FederationError` is raised only as `UNKNOWN_NODE` from `lan_node`. The class comment also lists `NO_HOST` and `UNREACHABLE`. `probe_lan_node` returns those in a dict and does not raise. With no host it returns `ok` false and `kind` `NO_HOST`. It does not invent an address. The default transport, used only after a host is set, returns `UNREACHABLE` (“no transport”). `federation_blockers` is five static sentences. It does not call `probe_lan_node`. `federation_ready` is true only when that list is empty, which this list never is.

## `cosmos_index.py`

Rebuildable projection of modules, wishlist, backlog, MOTIF tracker, recent `state/*_result.json` landings, and heartbeat files. Clock 13. Output is `state/cosmos_index.json` plus an HTML panel. The JSON is marked `authority: false`. Sources are the files it reads. It does not open the ledger writer.

Public: `repo_tree`, `plan_once_argv`, `plan_task_argv`, `canonical_slug`, `parse_tracker`, `parse_dispositions`, `parse_dhx_assignments`, `parse_checkboxes`, `parse_backlog`, `parse_wishlist`, `scan_modules`, `scan_landings`, `load_heartbeats`, `gather`, `projection`, `render_panel`, `rebuild`, `standup`, `loop`, `main`.

Errors: no error class. `CosmosPathError` at the CLI exits 2. Tracker, wishlist, and backlog status come from markdown regexes, not from a runtime proof. A required daemon with no heartbeat file is recorded `exists: false` and then left out of the live section, so a missing required daemon does not show up as a red live row. `rebuild` returns `ok: true` even when the HTML panel write fails (`panel_ok` false). It writes a heartbeat before `gather`, so a crash during the scan can leave a fresh tick. `loop` swallows exceptions into `cosmos_index.err` and continues. Unreadable landing JSON becomes `unreadable: true` on that row. An unreadable heartbeat file becomes an empty record that still counts as existing.

## `cosmos_inflight.py`

Owned in-flight leases. A claim is an append-only JSONL event. A release is another event, not an edit. Default TTL is 1800 seconds. State is a fold. Nothing is inferred from queue filenames or result files.

Public: `InflightError`. `Inflight` methods `claim`, `release`, `state`, `active`, `expired`, `tokens`. `selftest`.

Errors: `InflightError` kinds `NO_TOKEN` (empty claim or release), `WRITE_FAILED`, `READ_FAILED`. Releasing an unknown token is not an error. A corrupt line is skipped. The reader comment says a corrupt file raises. A file whose every line is bad JSON returns an empty event list, which is the same shape as “nothing is running.” `os.write`’s byte count is not checked, so a short write can be reported as a stored claim and later skipped as a torn line. `ttl_s` of 0 is treated as missing and replaced with the default TTL, because 0 is falsy. Two tokens may claim the same slug. There is no slug lock. The store does not fsync.

## `cosmos_ingress.py`

Envelope gate. An untrusted writer drops a payload file and a JSON envelope (sender, kind, length, sha256). `accept_all` checks the bytes, appends `INGRESS_ACCEPTED` or `INGRESS_REFUSED`, and renames the envelope. Refused envelopes stay on disk with a `.refused` suffix. Known kinds are `job`, `message`, and `return`.

Public: `IngressError`. `write_envelope`. `IngressGate` method `accept_all`.

Errors: `IngressError` kinds `BAD_ENVELOPE` (unreadable JSON, missing field, missing payload), `UNKNOWN_KIND`, `SHORT_PAYLOAD` (any length mismatch, including a longer payload), `HASH_MISMATCH`. Field types are not checked. A non-numeric `payload_len` can raise `TypeError` out of `accept_all`, which stops the rest of the directory and does not rename that envelope. The ledger append happens before the rename. If the rename fails, the next pass can append the same acceptance again. Payload files are never renamed. There is no directory lock. `write_envelope` does not check `kind` against the known set; the gate refuses it later.

## `cosmos_itc.py`

ITC resource broker. Fetches a public object index (default URL is the GrokDex CSV) through an injected fetcher, and keeps a local path corpus. This module does not open the network itself. Every search or get hit carries `index_hash`. The ledger stores the refresh hash and row count, not the CSV body. File bytes of the corpus are not read.

Public: `ItcError`. `ITC` methods `refresh`, `search`, `get`, `register_corpus`, `search_corpus`, `state`, `report`.

Errors: `ItcError` kinds `UNREACHABLE` (no fetcher, fetcher raised, or fetcher returned a non-string), `BAD_INDEX` (CSV parse failure, missing required column, duplicate `object_key`), `STALE` (no refresh in this process, or older than `max_age`), `NOT_FOUND` (key absent after a fresh index). Construction calls `state()`, which projects the ledger. A torn or forged chain raises whatever the ledger raises, not `ItcError`. Rows are not rebuilt from the ledger. `state` and `report` can describe a prior refresh while `search` and `get` still raise `STALE` until `refresh` succeeds in this process. Nothing is appended for a fetch that did not finish. Sanitizing a field caps it at 500 characters and strips controls, which can make two keys identical and then refuse the whole index as `BAD_INDEX`. `get` looks up the caller’s key as given. It does not run that key through the same sanitizer. An empty search query matches every row up to `limit`. `report` assumes `fetch_epoch` is a real timestamp.

## What this slice does not prove

These seventeen files are not the whole G–I surface of COSMOS. Rails, workers, and clocks here call modules outside this slice (`cosmos_bucket_daemon`, `cosmos_node_worker`, `cosmos_kernel`, `cosmos_ledger`, `cosmos_paths`, `cosmos_warn`, and others). A green self-test inside one file is not a live-tree proof. This slice is not a finished product.
