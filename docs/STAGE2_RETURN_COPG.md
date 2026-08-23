Reading _copg_prompt.txt to retrieve the prompt text so it can be answered exactly.

● Read _copg_prompt.txt
  └ 1 line read

✗ Read _copg_prompt.txt
  └ view_range out of bounds

● Read _copg_prompt.txt
  └ L1201:1600 (265 lines read)

● Read _copg_prompt.txt
  └ L801:1200 (400 lines read)

● Read _copg_prompt.txt
  └ L1:400 (306 lines read)

● Read _copg_prompt.txt
  └ L401:800 (398 lines read)

[{"id":"copilot-01","topic":"Lock enforcement requirement","verdict":"ENFORCE (design required)","evidence":"tree_lock.py + INCUMBENT_BEHAVIOR_4_SPIKE_MODULES.md: cooperative claim file, manifest, STALE_MINUTES; packet notes cooperative→load-bearing transition when lanes added.","confidence":"high"},{"id":"copilot-02","topic":"Scheduler concurrency & priority","verdict":"DESIGN CHANGE REQUIRED","evidence":"bts_runner.py + INCUMBENT_BEHAVIOR_4_SPIKE_MODULES.md: single-threaded per lane, lanes retrofit (2026-08-22), no priority field; ledger & claim-by-rename operational invariants must be preserved.","confidence":"high"},{"id":"copilot-03","topic":"Path resolver semantics","verdict":"PRESERVE FAIL-LOUD, ADD SENTINEL CHECKS","evidence":"bts_paths.py + packet notes: resolves TWO roots at import time; no fallback; incidents from hard-coded/fallback paths and migration-corrupted prose.","confidence":"high"},{"id":"copilot-04","topic":"IPC/mailbox scaling","verdict":"GENERALIZE MAILBOX (per-worker identities & staleness)","evidence":"bts_phone.py + INCUMBENT doc: fixed pair of files, checks existence vs missing, lacks per-writer identity and explicit staleness alarm.","confidence":"high"},{"id":"copilot-05","topic":"Runner conventions to preserve","verdict":"MANDATORY PRESERVATION","evidence":"bts_runner.py: claim-by-rename, claimed-path used to build command, three worded outcomes (0/2/other) → distinct destinations, log-first, helper '_' skip, append-only ledger with fsync, UTF-8 enforcement.","confidence":"high"},{"id":"copilot-06","topic":"Port hazards (singleton findings)","verdict":"HIGH RISK — SPECIFIC MITIGATIONS REQUIRED","evidence":"INCUMBENT packet and files: cross-universe literal backslash filenames (sandbox vs native), mount-refused unlink semantics, MAX_PATH truncation, migration tools rewriting prose, last-writer-wins shared artifacts, torn/unparseable files must refuse.","confidence":"high"}]

Reasoning and concrete answers to Input B (cite packet sections as used above):

A. ENFORCING LOCK (design)
- Requirement: an enforcement mechanism that survives a dying session, a FUSE mount that refuses unlink, and cross-universe writers (native Windows + Linux sandbox). (evidence: tree_lock.py behavior + INCUMBENT notes)
- Proposal (minimal, concrete):
  1. Lease-file with fencing token + epoch written atomically to a per-worker artifact directory (BASE/leases/<lane>.lease). Claim = write new JSON line with {"writer","epoch","token","claimed_at","manifest"} appended to an append-only file (fsync). The appender uses O_EXCL-like atomic create for a short-lived lock token file (native) and always append the lease record to the ledger so the record survives mounts that break rename. Read path picks the latest epoch+token and requires token possession (keeper kept in the process memory) to perform release. If unlink fails, release appends a "released" record; a reclaim requires proof-of-staleness by epoch time. Use manifest fingerprints (existing WATCHED) to detect "changed under me". 
  2. Fencing: include a monotonic epoch counter served by a single small arbiter process (Windows service) or by using a replace-with-expected-token atomic rename on the host filesystem when available; if arbiter cannot be hosted, emulate via an append-only epoch ledger plus signed token (HMAC with per-host key) so reclaimers can detect token ownership. Always append, never rely on last-writer-wins single-file state. (Design references: tree_lock.py manifest + ledger append rationale.)

B. SCHEDULER CONCURRENCY + PRIORITY (minimal design preserving invariants)
- Keep claim-by-rename semantics or replace by per-job lease record plus atomic move to running directory performed by the worker process using atomic filesystem rename where available.
- Add explicit job metadata sidecar: <job>.meta.json written by creator (or injected by ingress) with {"priority":int,"concurrency_group":string,"requested_timeout":int,"owner":string}. Scheduler: allow configurable parallelism per lane (worker count >1) but enforce per-concurrency_group single active job if needed. Always record per-worker identity in every artifact (logs, ledger entries, heartbeat).
- Preserve: log-first (create RUNNING log before exec), three worded outcomes (map rc→word), per-job timeout from filename permitted but prefer meta.timeout; ledger stays append-only+fsync; helpers '_' remain skipped at ingestion. (evidence: bts_runner.py)

C. RESOLVER FOR ONE ROOT (bts_paths successor)
- API: role-based functions (ai(), mesh(), secrets(), queue()) that resolve at call-time, not import-time, unless caller explicitly requests fail-fast import-time resolution.
- Fail-loud: resolver raises on missing roots. Add sentinel-content assertion: resolved dir must contain a named sentinel file (e.g.,/.bts_root or TOOLS_REGISTRY.json) and fail if absent.
- No fallback: remove implicit ladders; support explicit environment overrides only if caller sets an authoritative flag. Use MAX_PATH-safe walks (prefix \\?\ when on Windows APIs that need it) and canonicalize drive-letter differences by resolving via a small host-side mapping service or via per-machine config. (evidence: bts_paths.py incidents)

D. IPC AT N>2 (mailbox generalization)
- Mailbox becomes per-worker inbox/outbox directories under shared surface: airoot/mail/<worker-id>/inbox/ and /outbox/.
- Messages are append-only records (jsonl) with metadata: {id, from, to, created_at(epoch+tz), expires_at, delivered_flag, origin_path, manifest_hash}. Writers append; readers perform read+ack by appending an ack record. Presence vs missing preserved: existence of message record = present; separate delivered/ack flags and mtime used for staleness. Provide probe APIs: list-unseen, probe-staleness (age threshold), per-worker identity mandatory in every message. Mirror copies remain mirrors; readers must check host-side mirror only for diagnostics (NOT authoritative). (evidence: bts_phone.py + INCUMBENT notes)

E. WHAT ELSE BREAKS AT THE PORT? (singleton hazards)
- Migration tools that rewrite paths must skip prose; otherwise docstrings become false claims (observed). (bts_paths docstring scars)
- Mount semantics: atomic rename may not exist across FUSE/NFS; rely on append-only ledger + fsync to prove actions and avoid single-file last-writer-wins authority. (ledger reasoning in runner)
- MAX_PATH and path normalization on Windows will mask files (use \\?\ prefix where appropriate).
- Backslash-literal filenames created on Linux become distinct artifacts; avoid hard-coded platform paths and ensure resolver-mapping per-environment. (tree_lock & phone incidents)
- Unparseable/torn state files MUST refuse (torn lock in tree_lock selftest). Preserve negative controls in selftests.

F. INPUT C cards (one-line) — files named beyond the four deep modules included in packet: none provided in the stage2 questions section itself, so skipped.

Concluding rationale (prose, citations): the packet repeatedly demonstrates a design philosophy: fail-loud, append-over-rename where sandbox mounts break renames, manifest-fingerprints to distinguish "changed under me" from mount failures, and negative-control selftests to prevent regressions (see INCUMBENT_BEHAVIOR_4_SPIKE_MODULES.md sections for each module and the source files bts_paths.py, tree_lock.py, bts_phone.py, bts_runner.py). The above designs keep those invariants while providing concrete enforcement (lease+fencing or small arbiter), scheduler concurrency with sidecar metadata and per-worker identity, sentinel-checked resolver semantics, and a mailbox that scales to N>2 by using append-only per-worker message records and explicit staleness/probe semantics.

