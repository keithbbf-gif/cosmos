# TOOL CARDS — SLICE 1
**2026-08-23 · Consumer: COSMOS builders (stage 6b) and critics. Not a spike; not a port.**
**Method:** one line per incumbent. Fields from `docs/STAGE2A_INCUMBENT_BEHAVIOR.md` (reads / writes / invoked-by / refuses-and-why) plus a disposition guess (`PRESERVE` / `ADAPT` / `REPLACE`).
**Evidence rule:** mesh documentation under `docs/` only. Where a field is not stated, the field is `UNKNOWN`. Names are labels, not evidence. Disposition is a guess from stated architecture (carry-forward lists, escape valve, spike rulings) and is marked as such — it is not observed behavior.

Sources used: `STAGE2A_INCUMBENT_BEHAVIOR.md`, `STAGE2_MERGE.md`, `STAGE2_RETURN_OA.md`, `STAGE2_RETURN_GEM.md`, `STAGE2_RETURN_COPG.md`, `ARCH_SPEC_2026-08-17.md`, `COSMOS_PIPELINE.md`, `STAGE1_GOAL_SIGNED.md`, `FINAL_ARCHITECTURE.md`, `SPIKE_BRIEFS.md`, `STAGE4_MERGE.md`, `STAGE4_DESIGN_OA.md`, `PORT_SURVEY.json` (existence / size / literal counts only).

`PORT_SURVEY.json` (measured 2026-08-22, source `V:\Ai\BTS_MESH`) does **not** list `backup_watchdog`, `corrections`, `scars`, `verify_pointers`, `verify_conf`, or `bts_cursor`. Those six are carded from other `docs/` mentions and the assigned names only.

---

## Cards

bts_health | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN (docs attest a selftest that caught `bts_paths` swallowing a typo; `tree_lock` hashed this file as a watched control on 2026-08-22) | refuses UNKNOWN | ADAPT (guess: STAGE1 carries a "health board with positive and negative controls" but does not identify this file as that board; health becomes a service/API projection)

bts_kdash_feed | reads UNKNOWN | writes UNKNOWN (COSMOS_PIPELINE: a WRITER that must move with its launcher — repointing the feed without the launcher created a split) | invoked-by scheduled task "KDash Feed" (ARCH_SPEC live floor: already mesh-repo, Last Result 0; paired in that row with Queue Runner) | refuses UNKNOWN | REPLACE (guess: FINAL_ARCHITECTURE / STAGE4 — KDash is an API projection client, not a file-reading dashboard)

rail_check | reads UNKNOWN | writes UNKNOWN | invoked-by scheduled `RAIL_CHECK.bat` (ARCH_SPEC: `MESH=V:\Ai\mesh-repo\BTS_MESH`; next schedule 2026-08-18 02:05 CT; bat not fired that night) | refuses UNKNOWN | ADAPT (guess: STAGE1 rails matrix must be measured; architecture makes rails registry probes; STAGE1 also bans new `.bat`)

task_registry | reads machine scheduled-task set and a registry (`task_registry --check` → 0 red and machine count == registry count — COSMOS_PIPELINE / STAGE1) | writes UNKNOWN | invoked-by UNKNOWN (`--check` is the stage-7 runtime-binding gate command; no other invoker stated) | refuses UNKNOWN | ADAPT (guess: STAGE1 scheduled-task registry carries forward; done means zero red, counts match, no relative paths or drive literals)

bts_elevated_ops | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN | refuses UNKNOWN | ADAPT (guess: STAGE1 "elevated ops worker" carries forward; done #5 is "elevated ops repointed first (one UAC click)"; STAGE4/5 place backup execution on an elevated worker)

backup_watchdog | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN | refuses UNKNOWN | REPLACE (guess: name-only ID — file not in PORT_SURVEY; STAGE1 says backup is a requirement, not a script; FINAL_ARCHITECTURE puts policy/verification/evidence in Core and execution on scheduled jobs; PIPELINE_CRITIQUE's "watchdog that had never executed" is C-58 context and does not name this file)

bts_drive_health | reads UNKNOWN | writes UNKNOWN | invoked-by scheduled task "Drive Health" (ARCH_SPEC: action still `V:\Research4\Ai\BTS_MESH\bts_drive_health.py`, script missing at that path, Last Result 2, needs elevation; unelevated change blocked) | refuses UNKNOWN | ADAPT (guess: keep the scheduled check; retarget/elevate; PORT_SURVEY lists a 389-line copy with 0 drive literals under the surveyed mesh)

tools_sync | reads tools index / named live path for `--check` drift (ARCH_SPEC OA gate: canonical `00_TOOLS_INDEX.md` + read-only `--check`) | writes tools index on `--write` | invoked-by UNKNOWN (GbPL holds the pen; OWNER must name the live index path first) | refuses `--write` until OWNER names the live index path (ARCH_SPEC writers table + forbidden list) | ADAPT (guess: STAGE1 "tools registry with index sync" carries forward; check-then-write stays)

corrections | reads `corrections.toml` (ARCH_SPEC pairs `corrections.toml` + `corrections.py`) | writes UNKNOWN (process rule: COS Observer audits only and must not write; that is not stated as this file's own refusal) | invoked-by boot (STAGE1: count-weighted, printed at boot) | refuses UNKNOWN | PRESERVE (guess: STAGE1 carry-over stability; 61 corrections are load-bearing memory, not a spike rewrite)

scars | reads UNKNOWN (STAGE1: "scars as a query") | writes UNKNOWN | invoked-by UNKNOWN | refuses UNKNOWN (`--selftest` is a silent no-op — STAGE2_MERGE / scars.py scar — a defect, not a stated refusal) | PRESERVE (guess: STAGE1 scars-as-query; 154 scars are the evidence primitive)

verify_pointers | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN | refuses UNKNOWN | ADAPT (guess: name-only; STAGE1 lists "pointer integrity" as a build gate but does not name this file; file not in PORT_SURVEY)

verify_conf | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN | refuses UNKNOWN | ADAPT (guess: name-only; no `docs/` mention; file not in PORT_SURVEY; STAGE1 done #10 wants every control file to parse AND validate)

mesh_fanout | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN | refuses UNKNOWN | ADAPT (guess: PORT_SURVEY lists `mesh_fanout.py` at 351 lines / 1 drive literal; no stated behavior; vendor plurality remains a requirement)

bts_sgh | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN | refuses UNKNOWN | ADAPT (guess: ARCH_SPEC "adapt rails"; COSMOS_PIPELINE sits `bts_cursor.py` alongside this file; M-08 — dropping this file from a packet is a finding; DOM-first makes SuperGrok a metered rail, not the floor)

bts_gem | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN | refuses Activate (ARCH_SPEC: `bts_vertex.py` / `bts_gem.py` are GEM rail vs Studio wrapper — keep separate, Never Activate) | ADAPT (guess: keep-separate / Never Activate is a PRESERVE boundary; the rail itself adapts into the spend-gated registry; COSMOS_PIPELINE: this file mentions tooling once — read that line before assuming)

bts_gw | reads UNKNOWN | writes UNKNOWN | invoked-by UNKNOWN | refuses treating unpriced as $0 (ARCH_SPEC: unpriced ≠ $0; shares SGH $10 ceiling; not a second SGH grok) | ADAPT (guess: named build rail; adapt into the same spend-gate / ceiling as SGH)

bts_oa_api | reads UNKNOWN | writes a spend ledger (ARCH_SPEC: `bts_oa.py` + `bts_oa_api.py` — two ledgers, two ceilings, 272k vs 1.05M) | invoked-by UNKNOWN | refuses UNKNOWN (COSMOS_PIPELINE: plain completion, no tool or code-execution paths — stated capability, not a stated refusal) | ADAPT (guess: keep the two-ledger / two-ceiling split; rail adapts into the breaker-in-the-caller)

bts_cursor | reads UNKNOWN | writes UNKNOWN | invoked-by a queue lane (COSMOS_PIPELINE: Python SDK + Cloud Agent API, dispatchable from a queue lane) | refuses UNKNOWN | ADAPT (guess: intended Cursor rail alongside `bts_sgh.py`; key lives in `.secrets\`, never the repo; file not in PORT_SURVEY 139)

tree_lock | reads `bts_paths.queue("tree_lock.json")` plus sha256[:16] of 8 watched control files at claim time; torn/unparseable JSON raises (fail-open banned); `_sha()` returns None for unreadable-vs-absent and does not treat either as "changed" | writes claim overwrite (read-check-write, no OS lock); release runs verify first and blanks the file if FUSE refuses unlink; stale takeover overwrites WITH ANNOUNCEMENT (console only — no append-only audit); still computes `ROLD = MESH.parent / "ROLD"` (parent-walk LIVE; only LOCK uses `bts_paths`) | invoked-by UNKNOWN (CLI claim / `--verify` / release; SPIKE_BRIEFS: claim before any live-tree read/write) | refuses unknown writers (exit 2, `KNOWN_WRITERS` closed set); torn lock (never reads as free); silent stale clear; second-writer in selftest | REPLACE (guess: STAGE2A — cooperative shape cannot be ported; FINAL_ARCHITECTURE — advisory locking dead; leases + fencing tokens + fenced commit)

bts_phone | reads inbound `QA_ENGINEER_TO_COW.md` via `airoot()`; `--check` prints both paths and whether inbound EXISTS, plus mtime + size when present (no staleness alarm); `read()` probes then opens (TOCTOU possible) | writes none in attached source (OUTBOX `COW_TO_QA_ENGINEER.md` declared, never written — STAGE2_MERGE OA API-08; Research4 copies are mirrors only) | invoked-by UNKNOWN (CLI `--check` / `--read` / `--selftest` only) | refuses missing `AIROOT` at import (assert `isdir` — no letter into cwd); missing inbound = "THE PHONE IS DEAD", non-zero (missing ≠ empty); unknown option-like flags (positional garbage tolerated) | ADAPT (guess: keep probe-not-assume / dead ≠ no-news; add send, N>2 per-worker identity, staleness policy)

bts_runner | reads queue dir for runnable files (`.py`/`.bat`/`.cmd`/`.ps1`; a file is runnable iff a command exists — `RUNNABLE` dict deleted); `--lanes` discovers a lane only if heartbeat or `_lanes\<name>\` exists; `--lane lg|pb` rebinds to `_queue\_lanes\<name>\` | writes claim-by-rename into `running\` BEFORE exec (command built from the CLAIMED path); dest by rc: 0=CLEAN→`done\` · 2=FINDINGS→`done\findings\` · else=BROKE→`failed\`; log opens FIRST ("RUNNING" + cmd); timeout writes "RED - TIMED OUT"; append-only fsync jsonl ledger; heartbeat overwrite (`runner_heartbeat__<lane>.json`, glob-discovered); never deletes; one tick runs ALL jobs in the initial sorted list serially | invoked-by a native Windows scheduled task, one-minute tick per lane | refuses claiming `_`-prefix helpers (enforced in-runner); retrying stale >2h jobs (report, never retry); treating rc=2 as BROKE; lane names outside `[a-z0-9_-]{1,16}` (GEM-06 path-injection guard); loser of an overlapping rename is unhandled (`OSError` aborts the tick) | ADAPT (guess: STAGE2A / FINAL_ARCHITECTURE — concurrency + priority become scheduler properties; preserve claim-by-rename-or-better, claimed-path command, three worded outcomes, log-first, report-never-retry, helper convention, UTF-8 both ends, append-only ledger)

bts_paths | reads platform ladders (`_WIN=["V:\Research4"]`, `_NIX=["/sessions/*/mnt/Research4"]` — sandbox glob, `sorted(glob)[0]` if multiple) then env `BTS_RESEARCH_ROOT` / `BTS_AI_ROOT` LAST (override cannot shadow a healthy tree); import-time `ROOT` + `AIROOT` (import is a machine assertion) | writes none (CLI prints a report and exits 0 for any accepted arg) | invoked-by import from other modules (fail-fast); CLI | refuses missing either root at import; unknown flags beginning with `-` (exit 2 — added after `bts_health` selftest caught a swallowed typo); fallback to `D:\Research3`; env override shadowing a live tree; `--check` / `--selftest` are accepted but implement no distinct branch (silent no-op) | ADAPT (guess: keep resolve-or-raise / no fallback / role API; FINAL_ARCHITECTURE — one configured root, explicit instantiation at boot, sentinel-content; import-time side effects dropped)

---

## Disposition tally (guesses only)

| guess | names |
|---|---|
| PRESERVE | corrections, scars |
| ADAPT | bts_health, rail_check, task_registry, bts_elevated_ops, bts_drive_health, tools_sync, verify_pointers, verify_conf, mesh_fanout, bts_sgh, bts_gem, bts_gw, bts_oa_api, bts_cursor, bts_phone, bts_runner, bts_paths |
| REPLACE | bts_kdash_feed, backup_watchdog, tree_lock |
