# cosmos_collector — Motif STAGE-5 critique (G46)

**Reviewer:** G46 (Grok Build), dispatched `motif_collector_s5` 2026-08-25T22:42:11-05:00.
**Question:** is the build the thing that was decided — not "is this good code."
**Spec (decided):** `docs/AGENT_BRIEF.md` (DHx) assignment log protocol + Permanent results-collector bullet; architecture decisions 1/3/5 (`docs/FINAL_ARCHITECTURE.md`); clock shape in `docs/ORCHESTRATION.md`; anti-loss DIFF in `BUCm.toml` `[next].reconcile`.
**Build:** `cosmos/cosmos_collector.py`, `tests/test_collector.py`, live projection under `live/state/collector/` + `live/logs/collector_heartbeat.json`.
**Core:** `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service` were not imported and `git diff` on those four is empty (HEAD `56fa423`). Satellite only.

**Family note (process, not a collector defect):** Motif stage 5 is a *different-family* review. This job was dispatched to G46, who also wrote the module. The findings below are still spec-vs-build, bound to files and to a live-tree read. They are not a second family's vote. COW still owes a non-Grok-Build pass before any stage-6 claim.

`rc=0` on `cosmos_build_collector` is not complete. Stage 6 is a value only the live tree can emit *for the decided behavior*. A live pid polling the wrong aggregate is not that value.

---

## Verdict

**No — not the decided collector.**

The build *is* a ~30s rebuildable projection daemon that reads BTS queue buckets + research markdown + filtered ledger events, appends `live/state/collector/index.jsonl`, rewrites `docs/COLLECTOR.md`, and heartbeats `live/logs/collector_heartbeat.json`. That matches the *shape* of the assignment.

It is **not** the decided *function*. DHx's first collector sentence is: the collector reads the assignment log and correlates each marker to its result. That function is absent. The human summary is not "the aggregated state of all agents": on the live tree it is dominated by lane names (`## pb` 813, `## unknown` 589). The index is an unsynchronized second JSONL writer next to `cosmos_dispatch.append_assignment_row`, and the in-memory catalog diverges from the file.

Until HIGH defects are closed, this row stays DRAFT. Do not treat the heartbeat as a stage-6 gate.

---

## What was decided (the contract this review uses)

From DHx (`docs/AGENT_BRIEF.md`):

1. Collector **reads the DHx assignment log** and **correlates each marker to its result**. Precise start/end times also live in `V:\Ai\_queue\runner_ledger.jsonl`.
2. Daemon polls **~30s**, collecting every agent result from queue `*_result.json`, `done/`/`failed/`/`logs/`, `docs/research/*.md`, and the ledger.
3. Store: `live/state/collector/index.jsonl` + `docs/COLLECTOR.md` summary.
4. Runs from the **system clock** (scheduled task / detached); heartbeat `live/logs/collector_heartbeat.json`.
5. When live, `docs/COLLECTOR.md` is **the aggregated state of all agents**.

From ratified architecture:

- Projection / cache, never a second authority writer (decision 1, 3).
- Resolver: one sentinel-verified root; no drive literal as identity; no parent-walking (decision 5; `cosmos_paths` contract).
- Fail-closed: missing identity is a typed refusal, not an empty success.

From `BUCm.toml` anti-loss: DIFF assigned (DHx log) vs collected (index rows), re-drop anything that never returned. That DIFF is the reason the collector exists.

---

## Live-tree read (this critique, not a stage-6 pass)

Quoted from `live/logs/collector_heartbeat.json` after a host-side read:

```
last_run        = 2026-08-25T22:59:01-05:00
last_run_epoch  = 1787716741
worker          = cosmos-collector
pid             = 32940
instance_id     = 65f9cf23f39f
polls           = 123
interval_s      = 30.0
index_rows      = 1812          # len(Collector.catalog), not file line count
queue_root      = V:\Ai\_queue
tick            = idle
scanned         = 1717
```

Same process as the original standup (`pid=32940` in `cosmos_build_collector_result.json` SNAP1). Interval is the decided ~30s. Heartbeat path and summary path match the assignment.

Host-side count of `live/state/collector/index.jsonl` at the same window: **1820 parsed rows, 0 bad lines.** Sources on disk: `queue_log=975, queue_done=634, queue_failed=60, queue_result=43, ledger=73, research=27, dispatch_assignment=8`. `docs/COLLECTOR.md` "By source" line (generated `2026-08-25T22:59:01-05:00`, `index_rows=1812`) lists every source **except** `dispatch_assignment`. Catalog 1812 + 8 sibling rows = 1820 file rows.

Zero index rows whose artifact is `AGENT_BRIEF.md`, `runner_ledger.jsonl`, `live\queue`, or a `returns/` path. `COLLECTOR.md` contains neither `DHx` nor `AGENT_BRIEF` nor any correlate/DIFF section.

These numbers prove a daemon is polling. They do not prove the decided collector.

---

## HIGH

### H1 — DHx assignment log is never read; no marker↔result correlation

- **File/symbol:** `cosmos/cosmos_collector.py` — `Collector.poll_once`, `iter_queue_files`, `iter_research_files`, `iter_ledger_events`. No symbol reads `docs/AGENT_BRIEF.md`. Grep of the module for `AGENT_BRIEF` / `DHx` / `correlate` / `assignment` is empty.
- **Decided:** DHx protocol: "The collector reads this log and correlates each marker to its result." Anti-loss (`BUCm.toml`): DIFF assigned vs collected, re-drop silent assignments.
- **Build:** `poll_once` walks BTS queue + research + filtered ledger only. It never parses the append-only marker list, never joins `lane/file` to a `*_result.json` / `done/` / `failed/` artifact, never emits a "assigned but no return" row.
- **Live proof:** `has_dhx=0` across 1820 index rows. `docs/COLLECTOR.md` has no assignment-vs-result section. Historical DHx markers (cDeck, runner standup, Cursor prove, maker-docs sweep, …) are invisible to the collector unless a filename prefix happens to match.
- **Impact:** The anti-loss job cannot be performed from the collector's own artifacts. COW would have to grep DHx by hand against the queue — the thing the collector was assigned to do.
- **Fix:** Parse DHx markers (the `ISO · agent · assignment · lane/file` lines). For each marker, record `{marker, agent, task, lane, jobfile, result_artifact | MISSING}`. Surface unmatched assignments at the top of `COLLECTOR.md`. Tests must include a marker with no result and a marker whose result later appears.

### H2 — Human summary is not "the aggregated state of all agents"

- **File/symbol:** `cosmos/cosmos_collector.py` — `_infer_agent` (lane fallback `return lane, lane`); `Collector.render_summary` (groups on `maker`).
- **Decided:** `docs/COLLECTOR.md` is the aggregated state of **all agents**.
- **Build:** If the filename does not match `_AGENT_PREFIXES`, a non-root lane becomes both agent and maker. Root files with no prefix become `"unknown"`.
- **Live proof:** maker histogram of the index: `pb=813, unknown=589, COSMOS=146, Grok=121, … lg=26`. `COLLECTOR.md` headings include `## pb` and `## unknown` as two of the three largest groups. `pb` samples are ordinary `queue_done` scripts (`add_kdash`, `android_push2`, …) sitting under `_lanes/pb/done/` — the lane is not a maker. Agent `G46` exists on 42 rows, but there is no `## G46` heading; G46 is folded under `## Grok` only when the filename starts with `g46`.
- **Impact:** A reader of `COLLECTOR.md` cannot answer "what did each agent return." Lane names and `unknown` bury agents. That is a spec miss on the primary human artifact, not a cosmetic taxonomy nit.
- **Fix:** Agent identity comes from DHx / dispatch assignment / result JSON `agent`/`worker`, never from `_lanes/<lane>`. Group the summary by agent (with maker as a field). Tests must fail if a `_lanes/pb/done/foo.py` is stored as `maker=pb`.

### H3 — Unsynchronized second writer on the projection JSONL; catalog diverges from the file (safety)

- **File/symbol:** `Collector._append_rows` / `Collector._load_index` / `Collector.render_summary` (catalog is loaded once in `__init__`, never re-read); sibling `cosmos_dispatch.append_assignment_row` writes the same `live/state/collector/index.jsonl` without taking `collector.lock`.
- **Decided:** Projection is a cache; still must not be two unsynchronized appenders on one JSONL (architecture decision 1 is about the ledger, but the same torn-line physics applies). Dispatch is specified to "register the return with the collector" — that is a *protocol*, not a license to race the file.
- **Build:** Collector holds an exclusive lock only around its own `--loop`. Dispatch appends independently. `render_summary` rewrites `COLLECTOR.md` from the in-memory `catalog`, so sibling rows that landed after process start are in the file and absent from the summary until the daemon restarts. Pid `32940` / `instance_id=65f9cf23f39f` has been up since standup (~21:57); dispatch assignment rows were written ~22:42.
- **Live proof:** file has `dispatch_assignment=8`; `COLLECTOR.md` "By source" omits that source; heartbeat `index_rows=1812` vs file 1820.
- **Impact:** Torn JSONL under concurrent append is possible (no shared lock, no length-prefix). Assignment rows the dispatch harness registered are invisible to the live summary. Restart-safety of *this process's* rows is not the same as index integrity.
- **Fix:** One writer. Either the collector is the only process that appends (dispatch drops an assignment sidecar the collector ingests), or both take the same lock and the collector reloads the tail (or the whole file) each tick before rendering. Test: dispatch-append during `poll_once` must not tear a line and must appear in the next summary.

### H4 — Queue identity is a drive literal; COSMOS queue role is unused; missing queue is silent

- **File/symbol:** `DEFAULT_QUEUE = Path(os.environ.get("COSMOS_COLLECTOR_QUEUE", r"V:\Ai\_queue"))`; `Collector.__init__` (`self.queue = Path(queue) if queue is not None else Path(DEFAULT_QUEUE)`); `poll_once` `lane_roots` only under that path. No `self.paths.queue()`.
- **Decided:** Resolver canon — no drive literal as identity, no fallback ladder. COSMOS own queue is `live/queue` (BUCm: migrate dispatch onto `live\queue` via the own runner). Fail-closed: absence is typed, existence is not identity.
- **Build:** The BTS path is baked as the default. If it is missing, `iter_queue_files` yields nothing and the heartbeat still reports `error_count=0` / a successful poll. `live/queue` is never scanned (`has_liveq=0`).
- **Impact:** A peer on a cold machine (or any install whose runner is the COSMOS queue role) gets a green heartbeat and an empty queue projection. The collector looks live while dropping the native result stream the runner was stood up to write. Env override exists but is not identity.
- **Fix:** Default queue ingress = resolver role `queue` under the verified root. BTS `V:\Ai\_queue` is an *optional named bootstrap ingress* (config / `--queue`), never the default identity. Missing configured ingress → heartbeat `tick=error` with a typed reason, not a quiet 0.

---

## MEDIUM

### M1 — `runner_ledger.jsonl` not collected

- **File/symbol:** missing; DHx names `V:\Ai\_queue\runner_ledger.jsonl` as the precise start/end-time source.
- **Live:** `has_runner_led=0`.
- **Impact:** Correlation cannot use actual start/end even after H1; duration/staleness of in-flight work is not in the projection.

### M2 — `returns/` not collected

- **File/symbol:** `iter_queue_files` walks `*_result.json` anywhere under the queue tree plus `done/`/`failed/`/`logs/` only. Dispatch contract (`cosmos_dispatch.returns_dir`, DHx dispatch bullet) files results under `<lane>/returns/`.
- **Live:** `has_returns=0`.
- **Impact:** If the runner result JSON and the dispatch returns copy diverge, or if returns is the only published copy, the collector never sees it. Spec of the sibling deliverable is "FILES the result under the correct stream/folder/returns."

### M3 — COSMOS own queue (`live/queue`) not scanned

- **File/symbol:** `Collector.poll_once` `lane_roots`; `cosmos_paths.ROLES["queue"]` unused.
- **Live:** `live/queue` currently holds `manifests/` only, so this is not dropping results *today*. It becomes a silent miss the moment the own runner is the drain path.
- **Tied to H4.** Separate because even with `--queue` pointed at BTS, the native role should still be a source.

### M4 — `COLLECTOR.md` is a 40-row-per-group window, not an aggregate

- **File/symbol:** `SUMMARY_CAP_PER_GROUP = 40`; `Collector.render_summary` `shown = rows[:SUMMARY_CAP_PER_GROUP]`.
- **Decided:** the summary is the aggregated state of all agents.
- **Live:** `## pb` is 813 results, 40 shown; 773 older are a one-line ellipsis. Anti-loss cannot be done from the markdown; only from the index — and the index has H1/H3.
- **Fix:** Agent-level unmatched-assignment section is uncapped. Per-agent caps, if any, must not hide MISSING returns.

### M5 — Assignment rows never leave `status=assigned`

- **File/symbol:** collector does not update rows; `cosmos_dispatch` writes `status: "assigned"` once. Dedup key is `artifact|mtime` of the *job script*, so a later `*_result.json` is a different artifact with no back-pointer consumed by the collector.
- **Live:** 8 `dispatch_assignment` rows still `assigned` even where a matching `queue_log` / result exists (e.g. this critique's own job `g46_grok_motif_collector_s5_…`).
- **Impact:** The index cannot answer "open vs returned" without an external join. That *is* the correlation DHx required.

### M6 — Repo-tree paths parent-walk from `__file__`

- **File/symbol:** `repo_tree()` → `Path(__file__).resolve().parent.parent`; `default_research_dir()`, `default_summary_md()`.
- **Decided:** no parent-walking; resolver is the identity. Spec *does* locate the summary at repo `docs/COLLECTOR.md` (two-roots: repo vs `live/`), so a repo-tree pointer is required — but it should be a configured path (install record / `--summary`), not `__file__` climbing.
- **Mitigation already present:** runtime index/heartbeat/ledger go through `CosmosPaths`. Do not regress that.

### M7 — `--standup` registers ONLOGON only; live clock is a 1-minute self-heal of `--loop`

- **File/symbol:** `plan_task_argv` (`/sc onlogon`); `install_task`.
- **Decided / live:** `docs/ORCHESTRATION.md` — collector is a 30s `--loop` daemon plus a 1-minute schtask self-heal (`Schedule Type: One Time Only, Minute`, `Repeat: 1 Minute(s)`, last measured `/tr` pointing at `cosmos_collector.py --root … --loop`). ONSTART is the wrong trigger for a user-session `V:` volume; ONLOGON alone is not the self-heal.
- **Impact:** A cold `--standup` does not recreate the live clock. Survival across a dead `--loop` depends on a task another job registered.

### M8 — Isolated selftest does not exercise the decided behaviors

- **File/symbol:** `tests/test_collector.py` (42 checks: bind paths, first-poll ingest, ledger keep/drop, dedup, rewrite-as-new-row, schtasks argv).
- **Missing vs spec:** DHx parse + unmatched marker; lane-name must not become maker; sibling append during poll; `live/queue` role; `returns/`; `runner_ledger.jsonl`; missing-queue typed failure; no drive literal in `plan_task_argv` `/tr` (already asserted for the *queue* flag, not for default identity).
- **Impact:** `42/42` and `rc=0` are exactly the class Motif forbids treating as complete.

### M9 — Growing logs are re-indexed as new results

- **File/symbol:** `dedup_key(artifact, mtime)`; `_collect_file` uses `st.st_mtime`.
- **Live:** 22 artifacts appear twice (max 2), all `queue_log` files whose mtime moved after first ingest (`cosmos_build_collector__t1800__….log`, maker-docs logs, …).
- **Decided:** "never lose a result" (build's own rule) is correct for *rewritten result JSON*. Applying it to append-only logs inflates the index and duplicates lines in `COLLECTOR.md`.
- **Fix:** For `queue_log`, dedup on artifact path (update summary in place is a projection rebuild — allowed) or on inode+size with a single live pointer.

### M10 — Ledger ingest is a substring keep-list, not "agent results"

- **File/symbol:** `LEDGER_KEEP`, `LEDGER_KEEP_SUBSTR`, `ledger_event_kept`, `Collector._collect_ledger`.
- **Live status mix includes** `SPEND_RESERVED=23`, `SPEND_SETTLED=23`, `TOOL_DISPOSITION=8`, `MAKER_ADDED=6`, `SESSION_OPENED/CLOSED`. Those are infrastructure, not agent returns. Filtering out `BOOT_VERIFIED` / `TOOL_DECLARED` is documented and tested; keeping spend/session as first-class "results" dilutes the agent aggregate (H2).
- **Also:** `iter_ledger_events` skips torn/unparseable lines and does not verify the hash chain / service signature. Acceptable for a labeled cache; not acceptable if `COLLECTOR.md` presents them as authority. They are currently mixed into the same maker groups as queue returns.

---

## LOW

### L1 — `_AGENT_PREFIXES` third clause is a superset of the first two

- **File/symbol:** `_infer_agent` — `stem == pref or stem.startswith(pref + "_") or stem.startswith(pref)`.
- **Defect:** `startswith(pref)` already covers the other two. Short prefixes (`oa`, `gem`, `lg`, `pb`) will classify any stem that merely begins with those letters. Harmless today only because lane fallback (H2) fires first for unprefixed pb/lg jobs.

### L2 — Maker taxonomy splits the same family

- **File/symbol:** `render_summary` groups on raw `maker` string; research `_HANDS.md` uses filename (`GOOGLE_GEMINI`) while queue prefixes use `Gemini` / `OpenAI`.
- **Live headings:** `## OpenAI` and `## OPENAI`; `## Gemini` vs `## GOOGLE_GEMINI`; `## GCLOUD` vs neither.

### L3 — `--status` constructs a `Collector` (mkdir state/logs)

- **File/symbol:** `main` `--status` → `bind()` → `Collector.__init__` `state_dir.mkdir` / `logs_dir.mkdir`.
- **Defect:** a read of liveness is not a write of the tree. Cheap, but it is a side effect on a status probe.

### L4 — Result text is inlined into `docs/COLLECTOR.md`

- **File/symbol:** `_summarize_json_obj`, `_collect_ledger` (`json.dumps(payload)[:SUMMARY_LINE]`).
- **Defect:** first string-ish field (`summary` / `result` / `out_tail` / …) or ledger payload is copied into a repo-adjacent markdown file (gitignored, but world-readable on the volume). Not observed leaking the Cursor key; still no allow-list / redaction. Keep as a safety note for COW.

### L5 — `Collector.__init__` / `drain_loop` fail-open on source errors

- **File/symbol:** `drain_loop` bare `except Exception`; `iter_ledger_events` continues on `ValueError`; missing queue is not an error (H4).
- **Canon:** fail-closed. For a projection daemon, continuing *after recording a typed error in the heartbeat* is the right survival behavior; swallowing without a typed `tick=error` is not.

---

## What is positively evidenced (bound to artifacts)

- Satellite module, not Core: no import of `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service`; git diff on those four is empty.
- Runtime store paths go through `CosmosPaths`: heartbeat `logs/collector_heartbeat.json`, index `state/collector/index.jsonl`, ledger read `ledger/authority.jsonl`.
- Source classes named in the assignment *other than DHx / runner_ledger* are actually ingested on the live tree: `queue_result=43, queue_done=634, queue_failed=60, queue_log=975, research=27, ledger=73`.
- Poll interval is 30s; pid 32940 has advanced from `polls=1` (standup SNAP1) to `polls=123` with `last_run_epoch` moving.
- Heartbeat is written on idle ticks (`tick=idle`, `new_this_tick=0`) — liveness is a file, as designed.
- `docs/COLLECTOR.md` is gitignored (`.gitignore` line `docs/COLLECTOR.md`) and rewritten atomically via `.tmp` + replace; a live copy also sits at `live/state/collector/COLLECTOR.md`.
- Isolated selftest exists and covers resolver bind, first ingest, ledger keep/drop (`BOOT_VERIFIED` / `TOOL_DECLARED` excluded), artifact+mtime dedup, rewrite-as-new-row, and schtasks argv not baking the queue path into `/tr`.
- `plan_task_argv` uses `py -3.14 … cosmos_collector.py --root <root> --loop` with no `/rl highest` — matches the unelevated-registration constraint in the module docstring.
- PAUSE protocol is honored by absence: collector does not gate on `PAUSE.flag` (decided: collector keeps moving).

Those are foundations. They are not evidence that DHx correlation, agent aggregation, or single-writer index integrity were delivered.

---

## Safety (the review MOTIF_TRACKER named)

| question | finding |
|---|---|
| Does it write the authority ledger? | No. Read-only `iter_ledger_events` / `_collect_ledger`. |
| Does it modify kernel/sched/service? | No. Untracked satellite + test only. |
| Can it tear its own index? | **Yes (H3).** Dispatch and collector both append `index.jsonl` without a shared lock. |
| Can it look alive while dropping work? | **Yes (H1, H4).** Fresh heartbeat + empty/wrong aggregate. |
| Does it stop on PAUSE? | Correctly no. |
| Secrets in the summary? | Possible (L4); not observed for the Cursor key in this read. |
| Drive-literal default? | **Yes (H4).** `V:\Ai\_queue`. |
| Second authority? | Index is labeled a cache. Unsynchronized writers still make it a second *file* with torn-line risk. |

COW in-session safety review should treat H3 and H4 as the blocking pair: do not add more writers; do not default identity to a foreign volume.

---

## Acceptance conclusion

**Reject as demonstrated-complete. Do not advance to stage 6.**

The build delivered a live 30s projection daemon at the named paths. It did not deliver the decided collector: DHx marker↔result correlation, an agent-level aggregate, a single-writer index, or resolver-named queue identity.

Stage-6 gate, when H1–H4 are closed, is not `rc=0` and not "heartbeat age < 90s." It is a live-tree triple only this install can emit, for example:

1. A DHx marker for a known job appears in `index.jsonl` joined to its result artifact (or an explicit `MISSING`).
2. `docs/COLLECTOR.md` groups that job under the **agent** (G46), not under `pb` / `unknown`.
3. `collector_heartbeat.json` `last_run_epoch` advances on the 30s clock from the same pid **and** `index_rows` equals the file's line count (no sibling-row divergence).

Until that triple is quoted from the live tree, the MOTIF_TRACKER row remains stage 5 DRAFT.
)
