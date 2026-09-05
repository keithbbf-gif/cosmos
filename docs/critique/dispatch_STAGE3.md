# cosmos_dispatch — Motif STAGE-3 critique / rank (G46)

**Reviewer:** G46 (Grok Build), dispatched `motif_dispatch_s3` 2026-08-25T22:42:11.604955-05:00
(`lg/g46_grok_motif_dispatch_s3_you_are_g46_grok_b_9063db38__t1800.py`, this job).
**Question:** rank the *candidate* against the decided contract — not "is this good code,"
not "did a selftest print 60/60." Stage 3 is critique/rank of architecture. Stage 4 is
not earned by an in-session spike.
**Spec (decided):** DHx dispatch bullet (`docs/AGENT_BRIEF.md` Active assignments);
architecture decisions 1 / 4 / 5 / 9 (`docs/FINAL_ARCHITECTURE.md`); resolver contract
(`cosmos_paths`); Keith 2026-08-25 "Don't use any BTS" + BUCm bootstrap note; Windows-clock
canon (`docs/ORCHESTRATION.md`); routing policy is caller-side (`docs/ROUTING.md`).
**Candidate (not a locked arch):** `cosmos/cosmos_dispatch.py` (855 lines, **untracked**),
`tests/test_dispatch.py` (300 lines, **untracked**). Tracker artifact column is still
`(owed)`. HEAD `56fa423`.
**Core:** `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service` are not
imported by the module. This review does not modify them.

**Process (not a code defect):** Motif stages 1–2 did not run for this deliverable. There
is no vendor-plural research packet and no independent architecture return (no
`STAGE2_RETURN_*` for dispatch). COW coded in-session and the tracker says so (`2/4 — COW
codes in-session`). This document ranks **one candidate** against the contract. Missing
families are UNKNOWN, not votes. Same-family process note: G46 is also the builder of the
candidate. COW still owes a non-Grok-Build pass before any consensus claim.

`rc=0` on `cosmos_build_dispatch` / `cosmos_build_dispatch2` is not complete. Isolated
selftest `60/60` (re-run this critique, `py -3.14 tests\test_dispatch.py`) is not complete.
Stage 6 is a value only the live tree can emit *for the decided behavior*.

---

## Verdict

**The candidate is a working BTS-bridge file-drop. It is not the decided offload layer.**

It *does* create a runner-job `.py` from an agent TYPE, auto-pick a BTS lane, auto-stamp
DHx from `datetime.now().astimezone().isoformat()`, and append a
`source=dispatch_assignment` row. Grok through this harness has returned live (`PONG\n` in
3.7s; collector STAGE-5 critique in 414.5s). Kind inference G46→grok / Cursor→cursor /
F5→claude is implemented and isolated-tested.

It is **not** the DHx function: caller still owes a `--dir`; default identity is the drive
literal `V:\Ai\_queue`; the COSMOS runner on `live\queue` is idle while this harness
feeds BTS; assignment rows never become returns; `wait_for` is unused by the clocks that
call `dispatch()`; cursor and claude kinds have **zero** live `dispatch_assignment` rows.

Until the ranked locks below are decided and the HIGH defects close, this row stays
**DRAFT at stage 3**. Do not promote the untracked spike to stage 4 "the thing we
decided," and do not treat a heartbeat or `60/60` as stage 6.

---

## What was decided (the contract this rank uses)

From DHx (`docs/AGENT_BRIEF.md`, Dispatch harness bullet):

1. Caller gives only an **agent TYPE** (e.g. `G46`) **+ a task**.
2. The system **CREATES and assigns** — auto-picks lane + the right invocation for the type.
3. The system **MONITORS progress**.
4. The system **FILES the result under the correct stream/folder/returns** automatically.
5. Auto-stamps the DHx marker from `datetime.now()` (never a hand-typed time).
6. **Registers the return** with the collector.
7. Minimal input in, full lifecycle handled by the OS — COW just decides.

From DHx assignment-log protocol:

- Marker shape: `ISO-timestamp · agent · assignment · lane/file`.
- Collector reads this log and correlates each marker to its result.

From ratified architecture:

- Decision 1 — never a second unsynchronized writer.
- Decision 4 — queue = immutable manifests + ledger lifecycle events.
- Decision 5 — resolver is identity; no drive literal, no parent-walking, no fallback ladder.
- Decision 9 — legacy mutable-file tools run on the **compatibility lane** until they earn
  the native queue.

From Keith / BUCm (quoted, not paraphrased as if they were the destination):

- `"Don't use any BTS."`
- BUCm `[live].daemons`: *bootstrap: dispatch still drops into `V:\Ai\_queue` (BTS runner)
  as a bridge; migrate dispatch onto `live\queue` via the own runner.*
- Windows clock carries monitor/reap; Claude does not babysit (`docs/ORCHESTRATION.md`).

`docs/ROUTING.md` picks **which TYPE** (F5 vs G46 vs Cursor). That is not this module's
job. This module's job is: given a TYPE + task, do the rest.

---

## Live-tree read (this critique, not a stage-6 pass)

Quoted from host-side reads 2026-08-25 ~23:05-05.

**Candidate on disk**

| path | git | bytes | lines |
|---|---|---|---|
| `cosmos/cosmos_dispatch.py` | untracked (`??`) | 31916 | 855 |
| `tests/test_dispatch.py` | untracked (`??`) | 13262 | 300 |
| `docs/critique/dispatch_STAGE3.md` | this file | — | — |

HEAD `56fa423`. Isolated selftest this critique: **60/60 passed** (tempfile queue, does
not write `V:\Ai\_queue`). Prior claim in `V:\Ai\_queue\cosmos_build_dispatch2_result.json`
was also `60/60` / `rc=0` / 422.6s.

**Collector index** (`live/state/collector/index.jsonl`): 1825 parsed rows, 0 bad lines.
`dispatch_assignment=8`. All 8 `status=assigned`. All 8 `agent=G46`, `kind=grok`.
`cursor=0`, `claude=0`.

**Those 8 jobs, located on the BTS tree** (not on `live\queue`):

| stamp | lane | located | result json | returns json |
|---|---|---|---|---|
| 22:05:53 PONG-1 | root | `root/done` | YES (`rc=0`, `stdout_tail='PONG\n'`, 3.7s) | NO (row has no `returns_path` field) |
| 22:31:31 PONG-2 | root | `root/.` still **queued** | NO | NO |
| 22:42:11 collector_s5 | lg | `lg/done` | YES (`rc=0`, 414.5s) | YES (`_lanes\lg\returns\…`) |
| 22:42:11 **this job** dispatch_s3 | lg | `lg/running` | not yet | not yet |
| 22:42:11 makerhands_s3 | pb | `pb/.` queued | NO | NO |
| 22:42:11 meshadditions_s2 | lg | `lg/.` queued | NO | NO |
| 22:42:11 cursor_s4 | pb | `pb/running` | NO | NO |
| 22:42:11 runner_s5 | root | `root/.` queued | NO | NO |

`V:\Ai\_queue\returns` (root stream) is **empty**. `live\queue` holds `manifests/` only
(0 files). `live\queue\returns` does not exist.

**DHx assignment log:** 18 markers. **8** ISO-with-offset (no `~`). **9** still hand-typed
`T~20:5x-05`. The 8 ISO lines are this harness. Separator is ` - `, not the protocol ` · `.

**Who is draining what**

- `cosmos_runner_heartbeat.json`: pid **32400**, `queue_root=V:\A\Ai\COSMOS\live\queue`,
  `tick=idle`, `jobs_this_tick=0`, polls 404. Native runner is alive and idle on an empty
  role.
- `watchdog2_heartbeat.json`: pid 32388, `queue=V:\Ai\_queue`, `state=PAUSED`.
- `motif_driver_heartbeat.json`: last_run 22:57:02, `queue=V:\Ai\_queue`, `dispatched=0`
  (later tick; the 22:42 six-pack was an earlier drop).
- BTS **root** runner: `running/cosmos_build_index__t1200.py` since 22:54:14. That is why
  PONG-2 and `motif_runner_s5` are still sitting in the root lane 30+ minutes after drop.
- BTS **lg** runner: started this job at 23:01:59 after collector_s5 `end` rc=0 elapsed 414.8s.
- BTS **pb** runner: started `motif_cursor_s4` at 22:57:08.

**Cursor key:** `live/config/cursor_cosmos_key.txt` exists, 69 bytes, prefix `crsr_`,
last4 `31ab`. Never consumed by a live `dispatch_assignment` of `kind=cursor`.

---

## Rank of design choices (lock these before calling it stage 4)

Stage 3's job is to rank, not to recode. Independent architectures were never written;
the rank is contract vs this one candidate.

| # | choice | candidate | rank | lock |
|---|---|---|---|---|
| R1 | **Queue identity** | `DEFAULT_QUEUE = Path(… "V:\\Ai\\_queue")`; env override is a ladder | **REJECT as identity.** Named bootstrap ingress is allowed until the own runner drains real jobs. | Default identity = resolver role `queue` under a sentinel-verified root. BTS path is `--queue` / config, never the default, never a drive literal in the module. Missing configured ingress → typed `NO_LANE`/`NO_QUEUE`, not a drop into the wrong universe. |
| R2 | **Job shape** | Mutable `.py` file-drop, exclusive-create, hash filename | **ACCEPT as decision-9 compatibility** for the BTS bridge only. **REJECT as the native queue.** | Native path: immutable manifest under `live/queue/manifests` + ledger lifecycle (decision 4). Do not invent a second mutable queue inside COSMOS. |
| R3 | **Kind map** | `G46/grok/GrokBuild → grok`; `Cursor → cursor`; `F5/claude/fable → claude` | **ACCEPT.** | Keep inference. `--kind` override stays. Unknown TYPE without kind = `BAD_INPUT` (already). ROUTING.md picks the TYPE; dispatch does not second-guess F5 vs G46. |
| R4 | **Invocation flags** | grok `--single -m --output-format plain --always-approve --max-turns 60 --cwd`; cursor Cloud Agents v1 POST+poll; claude `-p --model claude-fable-5 --permission-mode dontAsk --add-dir` | **ACCEPT grok flags** (live-proven this session). **PROVISIONAL cursor/claude** (string-matched in tests; **UNKNOWN live** through this harness). | Do not change grok flags. Cursor body matches `docs/research/CURSOR_CLOUD_AGENTS_API_v1.md` (repos+autoCreatePR, Basic `key:`, poll `/runs/{id}` to FINISHED). Live-prove cursor and claude once each, or mark those kinds `UNPROVEN` in the return dict — do not imply they are as proven as grok. |
| R5 | **DHx stamp** | `_iso_now()` = `datetime.now().astimezone().isoformat()` | **ACCEPT.** | Never a hand-typed time. Already true for the 8 ISO markers. |
| R6 | **Marker grammar** | `{stamp} - {agent} - {_oneline(task)} - {lane}/{file}` | **CONTESTED.** | DHx protocol line uses ` · `. Build uses ` - `. Collector STAGE-5 H1 cannot parse either yet. **Lock one grammar** (recommend protocol ` · ` so the DHx prose and the file agree) and put a parser test on both the writer and the collector. Truncation at 140 chars is fine; the `lane/file` tail is the identity (already used for idempotent re-stamp). |
| R7 | **Collector registration** | Append `status=assigned` to `index.jsonl`; never update; no lock shared with collector | **REJECT as "register the return."** Assignment-only is a useful *event*; it is not the return. | One writer on that JSONL (collector critique H3). Dispatch drops a sidecar the collector ingests **or** both take the same lock and the collector owns the append. Return path updates `status` to `returned`/`MISSING` and joins `result_path`. 8/8 rows still `assigned` while 2 results exist is the proof this lock is required. |
| R8 | **Monitor** | `job_status` / `wait_for` pull; motif_driver and watchdog2 fire-and-forget | **ACCEPT pull API. REJECT blocking wait as the default lifecycle.** | DHx "MONITORS" + Windows-clock canon resolve as: OS runner moves buckets; dispatch exposes `job_status`; collector correlates. `wait_for` stays CLI-optional (`--wait`). A Claude/COW loop calling `wait_for(1800)` is the thing Keith forbade. |
| R9 | **Returns path** | ` <lane_dir>/returns/<stem>_result.json `; `job_status` *also* looks at `<runtime>/state/returns/<stream>/` and never writes it | **CONTESTED / incomplete.** | Lock **one** returns contract. DHx says `stream/folder/returns`. Candidate treats the BTS **lane** as the stream (`root→cm` in `STREAM_FOR_LANE` but markers say `root/`). Recommend: publish under the resolver role (`paths.state("returns", stream, name)` or `paths.queue("returns", …)` — pick one role, declare it). Lane-local `returns/` may stay as a compatibility copy during the BTS bridge, not as identity. |
| R10 | **Caller input** | `dispatch(agent, task, target_dir, …)` — dir required (`NO_DIR` if missing) | **CONTESTED vs DHx "TYPE + task only."** | Default `target_dir` to the **repo tree resolved from the install record**, not from `__file__`. Caller *may* override. After that default, the DHx one-liner is true. Kind stays inferred. |
| R11 | **Resolver** | `repo_tree() = Path(__file__).resolve().parent.parent`; `default_runtime_root = repo_tree()/"live"`; no `CosmosPaths` import (grep of the module is empty) | **REJECT.** | Instantiate `CosmosPaths` from `--root` / install record. Role API for `state/collector/index.jsonl`, `config/cursor_cosmos_key.txt`, queue, returns. Existence of `live/` next to the `.py` is not identity. |
| R12 | **Idempotency** | sha256(agent, kind, task, target_dir)[:8] in filename; O_EXCL create; skip second DHx stamp and second index row | **ACCEPT.** | Keep. Do not key only on time. |
| R13 | **Lane pick** | least loaded of root/lg/pb; tie → LANE_ORDER; `_`-prefix helpers skipped | **ACCEPT for BTS bridge** (matches `bts_runner --lanes`, isolated-tested). **N/A for native queue.** | While the bridge lives, keep this rule. Native queue does not have BTS lanes. |
| R14 | **Secrets** | Cursor key read at job runtime from `config/cursor_cosmos_key.txt`; never baked; last4 only in result | **ACCEPT.** Isolated test asserts `crsr_` not in job source. |

**Do not lock:** motif_driver always dropping `G46/grok` (ignores ROUTING.md F5 default). That is a **caller** defect, not a dispatch-harness defect. Rank it on the motif-driver row, not here.

---

## HIGH (contract misses that block stage 4 / 6)

### H1 — Default identity is a foreign drive literal; native queue is unused

- **File/symbol:** `cosmos_dispatch.py` `DEFAULT_QUEUE`; `dispatch()` `q = Path(queue) if queue is not None else Path(DEFAULT_QUEUE)`; `default_runtime_root()` parent-walk. No `from cosmos_paths import CosmosPaths`.
- **Decided:** resolver is identity (decision 5). Keith: no BTS. BUCm: migrate onto `live\queue`. COSMOS runner already heartbeats on that role.
- **Candidate:** baked `V:\Ai\_queue`. Env `COSMOS_DISPATCH_QUEUE` / `COSMOS_COLLECTOR_QUEUE` is a fallback ladder. `live\queue` is never written.
- **Live proof:** all 8 assignment artifacts are under `V:\Ai\_queue\…`. `cosmos_runner_heartbeat.json` `queue_root=V:\A\Ai\COSMOS\live\queue`, `tick=idle`, `jobs_this_tick=0`. Native runner cannot see work this harness creates. A peer on a cold machine with no `V:\Ai` gets either a drop into nothing or a silent wrong-universe (scar S-101/S-148).
- **Impact:** the "own runner" standup is a green idle loop while the offload layer still depends on BTS. That is the opposite of the migration BUCm named.
- **Fix:** R1 + R11. Bridge remains an explicit `--queue` for this install until the own runner drains a real job; it is not the default.

### H2 — "Register the return" is not implemented; assignment rows never leave `assigned`

- **File/symbol:** `append_assignment_row`; `dispatch()` builds `status: "assigned"` once; no updater. Collector does not close the join (collector STAGE-5 H1/H3/M5).
- **Decided:** DHx: register **the return** with the collector. Anti-loss DIFF assigned vs collected.
- **Live proof:** 8 `dispatch_assignment` rows, 8 `assigned`. PONG-1 result exists (`rc=0`, `PONG\n`) and collector_s5 result+returns exist; those rows still say assigned. `docs/COLLECTOR.md` "By source" omitted `dispatch_assignment` at the collector critique's read (catalog 1812 vs file 1820).
- **Impact:** `job_status` can see `done` if you pass the filename. The collector index — the thing DHx named — cannot answer open vs returned. The anti-loss job cannot be done from the projection this harness writes.
- **Fix:** R7. Dispatch must not be a second unlocked appender. The joined row is the product.

### H3 — Unsynchronized second writer on `index.jsonl` (safety)

- **File/symbol:** `append_assignment_row` opens `'a'` + `fsync`; collector `_append_rows` holds `collector.lock` only around its own loop. No shared lock.
- **Decided:** decision 1 — never a second unsynchronized writer. Same torn-line physics as the ledger, even though this file is a projection.
- **Live proof:** collector critique measured file 1820 vs catalog 1812, with the 8 sibling rows invisible to `COLLECTOR.md`. This critique: file 1825, still 8 dispatch rows. Motif-driver dropped six jobs in one process (serial, ~30 ms apart) so DHx/index were lucky-serial; watchdog2 + motif_driver + a CLI dispatch overlapping a collector tick is the torn-line case.
- **Impact:** torn JSONL under concurrent append is possible. Assignment rows the harness "registered" can be invisible to the live summary.
- **Fix:** R7. One writer.

### H4 — Result filing is partial and the path contract is two (or three) places

- **File/symbol:** `_emit_result_block` writes `RESULT` (lane dir) + `RETURNS` (`lane/returns`); `job_status` also searches `runtime_root/state/returns/stream` (never populated — grep of `state/returns` in this module is empty); `STREAM_FOR_LANE` maps `root→cm` while markers say `root/`.
- **Decided:** FILES the result under the correct **stream/folder/returns**.
- **Live proof:**
  - PONG-1: result at `V:\Ai\_queue\<stem>_result.json` (`rc=0`, `'PONG\n'`). **No** `returns/` copy. Row0 has **no** `returns_path` key (schema grew between 22:05 and 22:31).
  - collector_s5: both lane-root result **and** `_lanes\lg\returns\…` (the one later job template).
  - `V:\Ai\_queue\returns` (root) n=0. PONG-2's promised returns path does not exist because the job has not run.
  - `live\queue\returns` missing.
- **Impact:** "filed under stream/folder/returns" is true for one lg job, false for the first live demo, undefined for root, and a third path `state/returns/cm` is searched and never written. Collectors and humans cannot have one lookup.
- **Fix:** R9. One path. Compatibility copy optional and labeled.

### H5 — Caller still owes `--dir`; DHx one-liner is false

- **File/symbol:** `dispatch(agent, task, target_dir, …)`; CLI `ap.error("--agent, --task, and --dir are required")`.
- **Decided:** caller gives **only** TYPE + task.
- **Candidate:** kind *is* inferred (this part of the one-liner is true — live CLI `kind_inferred: true` in `cosmos_build_dispatch2_result.json`). Dir is not.
- **Impact:** every clock (`cosmos_motif_driver.py` ~562, `cosmos_watchdog2.py` ~910) must pass `str(repo)`. That is not "the system does the rest."
- **Fix:** R10.

### H6 — Cursor and claude kinds are unproven through this harness

- **File/symbol:** `_cursor_job`, `_claude_job`. Live index: `kind=grok` on 8/8 assignment rows.
- **Decided:** auto-picks the right invocation for the type, including Cursor (DHx Cursor lane is LIVE, recipe in `docs/research/CURSOR_CLOUD_AGENTS_API_v1.md`) and F5 (`claude -p`).
- **Live proof:** key file exists (`crsr_…31ab`). Isolated tests assert the job **source text** contains `/v1/agents` and `claude-fable-5`. Zero live `dispatch_assignment` of those kinds. `cursor_verify` / `cursor_prove` were **other** jobs, not this harness.
- **Impact:** reporting "cursor kind is wired" from a string match is the placation class (`docs/SCAR_PLACATION.md`). UNKNOWN live, not a pass.
- **Fix:** R4. One live cursor drop (or a typed refusal if Cloud Agents is down) and one live F5 drop, quoted from the result json `kind`/`rc`/`run.status`. Until then the return dict must not imply parity.

---

## MEDIUM

### M1 — "OS carries" is BTS FIFO; drop ≠ progress

- **Live:** PONG-2 queued in root since 22:31:31 while `cosmos_build_index__t1200.py` occupies `running/` (started 22:54:14). `motif_runner_s5` queued behind the same FIFO. Least-loaded pick at drop time does not account for a 20-minute occupant.
- **Impact:** DHx "MONITORS progress" is not satisfied by `created: true`. `job_status` would say `queued`; nothing in the candidate re-lanes, nacks, or surfaces stall. Watchdog2 is PAUSED so it will not notice either.
- **Fix:** R8 plus a stall signal (queued age > timeout/2 → collector `MISSING`/`STALLED`). Do not add a Claude poll loop.

### M2 — DHx append is unlocked read-modify-write

- **File/symbol:** `append_dhx_marker` reads whole file, splices before next `## `, `write_text`.
- **Impact:** two concurrent `dispatch()` calls can lose a marker. The 22:42 six-pack was one process so it survived. Watchdog2 + motif-driver overlap would not.
- **Fix:** same lock story as R7, or length-prefixed append-only markers below a sentinel.

### M3 — Lane-load accounting is duplicated three more times

- **File/symbol:** `LANE_ORDER`, `_lane_dir`, `SKIP_COUNT_NAMES` (dispatch) vs copies in `cosmos_collector.py`, `cosmos_motif_driver.py`, `cosmos_watchdog2.py`.
- **Canon:** improvement is not bloat; net complexity down.
- **Fix:** one satellite helper. Not Core. Do not grow a fourth copy in stage 4.

### M4 — Isolated selftest does not cover the decided behaviors

- **File/symbol:** `tests/test_dispatch.py` — 60 checks, all against a tempfile BTS-shaped queue and a fake DHx.
- **Missing vs spec:** resolver bind (no drive literal default); missing-queue typed failure; native `live/queue` role; return-row update; shared-lock with collector; live cursor POST (tests write a dummy key and never send); live claude; marker grammar vs DHx ` · `; `state/returns/<stream>` not written.
- **Impact:** `60/60` is exactly the class Motif forbids treating as complete. Re-run this critique: still 60/60, still the same 60 checks.

### M5 — `job_status.terminal` is true if any leftover result json exists

- **File/symbol:** `"terminal": state in ("done", "failed") or result is not None`.
- **Impact:** a leftover `*_result.json` next to a re-queued same-hash file would report terminal while the job is queued. Idempotent names make this rare; not impossible after a done→re-drop of the same inputs (idempotent skip usually prevents re-drop — unless the file was moved out of all buckets).
- **Fix:** terminal iff bucket is done/failed **and** result hashes/mtime are newer than job create, or result `stamp` matches the assignment row.

### M6 — First live schema has no `returns_path`

- **Live:** row0 keys listed in this critique — no `returns_path`, no `stream`. Row1 grew those fields.
- **Impact:** projection consumers cannot assume the current row shape. Schema `cosmos-collector/1` did not bump.
- **Fix:** if the row shape changes, bump the schema token the collector already keys on.

---

## LOW

### L1 — Exception path in grok/claude jobs may omit `rc` before `_emit_result_block`

- **File/symbol:** `_grok_job` `except` sets `error`/`secs` only; exit is `0 if out.get("rc")==0 else 2` → 2. Harmless, but the result json then has no `rc` key (cursor job does set `rc=2` on error).
- **Fix:** set `rc=2` in every except. One shape.

### L2 — `_lane_of_path` is a substring test on Windows/Unix path text

- **File/symbol:** `"\\_lanes\\lg\\" in jp.lower()`. Fine on this volume; a target_dir that happens to contain `_lanes\lg` is a false lane. Unlikely, still not identity.

### L3 — `ONELINE_CAP=140` eats the Motif instruction after "Deliv…"

- **Live DHx:** this job's marker ends `… Delive… - lg/g46_grok_motif_dispatch_s3_…`. The `lane/file` tail is intact (good). Humans grepping DHx for "STAGE-3" will miss it. Acceptable if collector keys on the tail.

### L4 — Tests import `cosmos_kernel.install` to build a scratch root

- Satellite test using Core `install()` as a fixture is acceptable. Do not let that become dispatch importing Core at runtime. It does not today.

---

## What is positively evidenced (bound to artifacts)

- Satellite module: no runtime import of kernel/ledger/sched/service; this review does not touch those four.
- Grok invocation through this harness is live: PONG-1 result json `rc=0`, `secs=3.7`, `stdout_tail='PONG\n'`; collector_s5 result json `rc=0`, `secs=414.5`, wrote `docs/critique/collector_CRITIQUE_g46.md`.
- DHx auto-stamp is live: 8 markers with `T` + numeric offset + microseconds, no `~`. Quoted this job: `2026-08-25T22:42:11.604955-05:00 - G46 - motif_dispatch_s3 … - lg/g46_grok_motif_dispatch_s3_you_are_g46_grok_b_9063db38__t1800.py`.
- Kind inference is implemented and isolated-tested (`infer_kind("G46")=="grok"`, Cursor, F5). Live CLI demo (`cosmos_build_dispatch2_result.json`) reports `kind_inferred: true`.
- Least-loaded lane pick is isolated-tested and was used live (six-pack spread root/lg/pb).
- Idempotent filename + no double DHx stamp + no double index row: isolated-tested.
- Cursor key is not baked into job source (isolated test + this job file contains no `crsr_`).
- Typed refusals exist: `BAD_INPUT` / `NO_DIR` / `NO_LANE` / `NO_KEY`.
- Isolated selftest this critique: **60/60**.
- Callers exist: `cosmos_motif_driver.dispatch(...)`, `cosmos_watchdog2.dispatch(...)` — the offload *shape* is already how the clocks drop work.
- `wait_for` is not used by those clocks (correct under R8).

Those are foundations for a **bridge spike**. They are not evidence that R1–R11 were decided, and they are not a stage-6 gate.

---

## UNKNOWN (not guessed)

- Whether a `kind=cursor` job from **this** harness reaches `GET /v1/me` 200 and `run.status=FINISHED`. Key exists; no assignment row.
- Whether a `kind=claude` / F5 job from **this** harness returns a real `claude -p` result. No assignment row.
- Whether BTS root runner will ever pick PONG-2 / `motif_runner_s5` before their `__t1800` timeout (occupancy of `cosmos_build_index` is measured; remaining runtime of that job is UNKNOWN).
- Whether concurrent dispatch+collector append has already torn a line (1825 rows parsed clean **now**; absence of a torn line in this read is not a proof the race cannot fire).
- Whether `docs/COLLECTOR.md` has been regenerated to include `dispatch_assignment` since the collector critique's 22:59 read (not re-audited here; not this deliverable).
- Independent-family architecture for this harness (Gemini / OA / F5). None on disk.

---

## Safety

| question | finding |
|---|---|
| Does it write the authority ledger? | No. |
| Does it modify kernel/sched/service? | No. Untracked satellite + test. |
| Can it tear the collector index? | **Yes (H3).** |
| Can it look successful while the native runner is idle? | **Yes (H1).** `created: true` on BTS, `cosmos_runner` `tick=idle`. |
| Drive-literal default? | **Yes (H1).** `V:\Ai\_queue`. |
| Parent-walk identity? | **Yes (R11).** `__file__` → repo → `live/`. |
| Secrets in job files? | Not observed; cursor key path-only. |
| Blocking Claude-loop wait as default? | No. `wait_for` is CLI `--wait` only. |
| PAUSE? | Dispatch itself does not honor `PAUSE.flag` (correct: it is a primitive the clocks call). Watchdog2 is PAUSED and so does not drop *new* work; this job was dropped before pause and is allowed to finish. |

---

## Acceptance conclusion

**Do not advance to stage 4 as "the decided harness." Do not advance to stage 6.**

The in-session spike delivered a BTS-bridge that clocks already call, with a live grok proof (`PONG\n`) and live DHx ISO stamps. The tracker is right that the artifact is still **(owed)**: native queue identity, return registration, single-writer index, one returns path, TYPE+task-only entry, and live cursor/F5 proof are not the thing DHx decided.

**Ranked work for the next Motif step (COW locks, then stage-4 code):**

1. Lock R1/R11/R7/R9 (queue identity, resolver, one index writer, one returns path). These four are blocking.
2. Lock R6/R10 (marker grammar, default dir). Cheap.
3. Keep R3/R4-grok/R5/R8/R12/R13-bridge/R14 as accepted.
4. Prove cursor + claude once each through **this** harness, or label them UNPROVEN in the return dict (H6).
5. Then a different-family stage-5 vs this ranked contract.

**Stage-6 gate** (when the locks are built) is not `rc=0` and not `60/60`. It is a live-tree tuple only this install can emit, for example:

1. `dispatch("G46", <task>)` with **no** `--dir` and **no** `--queue` writes the job under the **resolver `queue` role** (`live\queue\…`), and `cosmos_runner_heartbeat.json` shows that job id on a later tick (not `tick=idle` while BTS ran it).
2. DHx contains an ISO stamp (no `~`) for that job in the locked grammar; the collector index has a row for it whose `status` is **not** stuck at `assigned` once the result exists (joined to the returns artifact or explicit `MISSING`).
3. The result json at the **locked** returns path quotes a value only the live run can emit (e.g. grok `stdout_tail` / cursor `run.status=FINISHED` + `key_last4`, **not** an exit code).

Until that tuple is quoted from the live tree, the MOTIF_TRACKER row remains stage 3 DRAFT — candidate ranked, artifact owed.
)
