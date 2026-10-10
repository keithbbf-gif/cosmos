# Core J–L

This slice is not a finished product. COSMOS is not finished. This page is a reading map of the nine `cosmos/cosmos_*.py` modules whose names start with `cosmos_j`, `cosmos_k`, or `cosmos_l`. It names public classes and functions. It does not paste function bodies. Names that start with `_` are private and are not listed. Nothing here was executed; the errors are what the source shows.

No other file in `cosmos/` matches that prefix.

## cosmos_job_adapter.py

**Role.** Claims a queue-role `*.py` file-drop by rename, copies it under the tools role, and submits that copy to the scheduler.

**Public.** Class `LegacyJobAdapter`: `claims_path`, `scan`, `adapt`, `project_outcomes`.

**Errors.** No error class. A claim or copy `OSError` is not raised: claim failure returns `None`; copy failure returns a record with `copy_error` and `job_id` null, and the file is already in `running/`, so `project_outcomes` will not move it. A project `OSError` comes back as a dict with `error`. A torn line in `adapter_claims.jsonl` is skipped. `scan` can still raise `OSError` if a listed file disappears before `stat`. The claims file is appended with no lock.

## cosmos_judge_run.py

**Role.** One Judge model and prefix per run, plus partner autopsy and an attempt JSONL. It is not a second scheduler.

**Public.** `stamp_minute`, `task_prefix`, `wo_partner`, `judge_idle_gate`, `judge_run_path`, `load_judge_run`, `judge_run`, `attempts_path`, `read_attempts`, `append_attempt`, `list_sibling_orders`, `xfer_for`, `autopsy_fail`, `board_counts`, `cache_alive`, `poll_once`, `reseat_follow_up`, `archive_corpse`, `backfill_failed`, `main`.

**Errors.** No error class. A miss is a dict kind `UNMEASURED` (or `None` from `load_judge_run`), not a guessed id. A torn JSON line is skipped. `autopsy_fail` and `reseat_follow_up` catch `Exception` and turn it into `UNMEASURED` or `dropped: false`. Readers do not create directories; `judge_run`, `append_attempt`, and `archive_corpse` do. The CLI accepts `--once` and never reads it: any `--root` that is not `--backfill` runs `poll_once`.

## cosmos_kdash.py

**Role.** Client and page gate for the KDash CREATE panel: makers cards from `GET /api/v1/makers`, and a disk check that the page has no remote script or stylesheet.

**Public.** Class `KdashError`. Functions `makers_path`, `card_from_maker`, `cards_from_payload`, `invoke_instructions`, `parse_makers_response`, `fetch_makers`, `inspect_page`, `inspect_kdash_file`.

**Errors.** `KdashError` kinds actually raised: `UNKNOWN_KIND`, `BAD_ENTRY`, `UNREACHABLE`, `UNAUTHORIZED`, `NOT_FOUND`, `BAD_PAGE`, `CDN_FORBIDDEN`, `MISSING_PANEL`. An unknown kind is refused before the request. A non-200 body whose `error` is not one of those kinds is rewritten (`401` to `UNAUTHORIZED`, `404` to `NOT_FOUND`, a 400 that mentions `KIND` to `UNKNOWN_KIND`, otherwise `UNREACHABLE`). `fetch_makers` decodes an HTTP error body as strict UTF-8, so a bad encoding can escape as `UnicodeDecodeError` instead of `KdashError`.

## cosmos_kernel.py

**Role.** Composition root: resolver, authority ledger, arbiter, mail, scheduler, and the other Core pieces, with `ready` set after that boot.

**Public.** Class `Kernel`: `compose_rails`, `open_session`, `accept_return`, `protected_write`, `audit`. Function `install`.

**Errors.** This file defines no error class. Boot raises `CosmosPathError` `NOT_FOUND` when the install key is missing, and `UNPARSEABLE` or `IDENTITY_MISMATCH` from `install` on a torn or different sentinel. Read-only refusal of lease writes, return acceptance, and protected writes is also `CosmosPathError` `NOT_FOUND`, which is the wrong kind for "a reader is not a writer". `LedgerError`, `LockError`, `MailError`, `SchedError`, and `ValidateError` are imported and not raised here. The module text names `status()`; `Kernel` has no `status` method. `ready` is set true after fail-open rail compose, so a skipped rail does not clear it. `audit` counts a live lease only for the resource name `tree`. `protected_write` appends `PROTECTED_WRITE` after `fenced_commit` returns; a failed append does not undo the install.

## cosmos_learn_clock.py

**Role.** Native `--once` clock that proposes STYLE lines from xfer JSONL and does not rewrite `PREFIX.md`.

**Public.** Class `LearnRefusal`. Functions `session_ideas_dir`, `default_jsonl_path`, `propose_dir`, `style_propose_path`, `applied_path`, `field_gaps`, `row_action_kind`, `xfer_already_applied`, `row_fingerprint`, `path_under_declared_role`, `resolve_jsonl`, `style_line`, `review_sets`, `snapshot`, `poll_once`, `standup`, `plan_task_argv`, `emit_plan`, `main`.

**Errors.** `LearnRefusal` is raised only as `ESCAPE` or `PREFIX_REWRITE`. The class text also names `NO_ROOT`, `NO_ONCE`, and `IDENTITY_MISMATCH`. Those first two are CLI JSON and exit 2, not raised. A clock-id mismatch is a `poll_once` dict kind `IDENTITY_MISMATCH`; `standup` still queries or creates the task and only stores `clock_id_error`. A `CosmosPathError` at the process edge is printed as `NO_ROOT`. A torn JSONL row is skipped as `UNMEASURED`. The tools role's directory is `cosmos` while its role name is `tools`: a relative JSONL starting with `tools` is resolved under `state`, and one starting with `cosmos` is passed to `paths.role` and raises `CosmosPathError` `NOT_FOUND`. An absent JSONL tick still calls `write_heartbeat`, which creates the logs directory, unless `--dry-run`.

## cosmos_ledger.py

**Role.** Append-only hash-chained service-authenticated JSONL authority. A bad line is refused. It is not repaired in place.

**Public.** Class `LedgerError`. Class `Ledger`: `append`, `head_seq`, `head`, `append_guarded`, `verify`, `project`, `fold_cached`, `last`.

**Errors.** `LedgerError` kinds: `TORN`, `BROKEN_CHAIN`, `FORGED`, `UNREADABLE`, `STALE_HEAD`, `TRUNCATED`. A missing file is an empty ledger, not `UNREADABLE`. `append` raises `STALE_HEAD` when `expect_head_seq` is not the head after catch-up. A failed head-anchor write is swallowed after the record is already on disk, so the append stands and the anchor can lag. That is written as intentional in the anchor writer. This page is not a second copy of the ledger chapter.

## cosmos_ledger_verify.py

**Role.** Five-minute satellite that walks `Ledger.verify` on `authority.jsonl` and writes a verify projection plus a heartbeat. It does not append.

**Public.** `poll_once`, `standup`, `main`.

**Errors.** No error class. `LedgerError` is stored as `state: REFUSED` with that `kind`. The module text names `TORN`, `BROKEN_CHAIN`, `FORGED`, and `UNREADABLE`; the code forwards every `LedgerError` kind, including `TRUNCATED` and `STALE_HEAD`. A missing `install_key.bin` is a bare `FileNotFoundError` folded into `state: ERROR`, not a named ledger kind. `main` calls `json.dumps` and the file never imports `json`, so `--status`, `--standup`, and the default print path raise `NameError` after or instead of a clean report. `CosmosPathError` at the process edge exits 2.

## cosmos_live_emit.py

**Role.** Requires a live Core `GET /api/v1/status` that is ready and carries tree id `KMesh-COSMOS-live`. An exit code is not that proof.

**Public.** Class `LiveEmitError`. Functions `quote_tree_id`, `require_live_emit`.

**Errors.** The class text names `MISSING_EMIT`, `CORE_UNREACHABLE`, and `BAD_EMIT`. Only the first two are raised. `BAD_EMIT` never appears. A non-200 response, `ready` other than true, and a wrong `tree_id` are all `MISSING_EMIT`, including when Core did answer. Transport failure other than `HTTPError` is `CORE_UNREACHABLE`. An `HTTPError` is turned into a status code and then `MISSING_EMIT`. A token that cannot be read becomes `None`, and the request goes out without a bearer.

## cosmos_lock.py

**Role.** Lease arbiter: expiring leases, monotonic fencing tokens, and a four-phase fenced commit on an append-only lease ledger.

**Public.** `sidecar_lock_path`. Classes `LockError`, `Lease`, `StagedArtifact`. Class `Arbiter`: `acquire`, `renew`, `release`, `fenced_commit`, `status`, `events`.

**Errors.** `LockError` kinds actually raised: `HELD`, `STALE_TOKEN`, `NO_LEASE`, `TORN_LEDGER`, `FORGED_EVENT`, `REENTRANT`, `BAD_STAGE`. `UNKNOWN_RESOURCE` is named on the class and never raised. An unreadable `expected_inputs` path is raised as `NO_LEASE`. A hash mismatch on that input is raised as `STALE_TOKEN`. Neither condition is a missing lease or a stale fencing token. `release` of a token that is not current appends `REFUSE` and returns; it does not raise. A legacy zero-argument stage can write during the unlocked phase and then raise `STALE_TOKEN` after `COMMIT_UNFENCED` is recorded. A torn or forged lease line refuses load. It is not treated as free.

This slice is not a finished product.
