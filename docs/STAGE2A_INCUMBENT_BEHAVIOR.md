# STAGE 2(a) — OBSERVED BEHAVIOR OF THE FOUR SPIKE MODULES
**2026-08-23 · F5/Cowork · Consumer: COSMOS builders and critics (nodes). Narrative governance.**
**Method, per Keith's ruling: scars/corrections FIRST, code SECOND, docstrings NEVER as evidence.**
Source of truth: the live tree at `V:\Ai\BTS_MESH\` read host-side 2026-08-23, plus the scar
record (154 scars) and corrections (61). A docstring is a claim; everything below is behavior
the code exhibits or an incident that was paid for.

---

## 1 · `bts_paths.py` — filesystem abstraction (200 lines)

**WHAT IT ACTUALLY DOES:**
- Resolves TWO roots at IMPORT TIME, not call time: `ROOT` (research tree) and `AIROOT` (shared
  AI surface). Import fails loudly if either is missing — **importing this module is itself an
  assertion about the machine.** Any module that imports it cannot start on a box where the
  trees are absent. COSMOS must decide: keep import-time resolution (fail fast) or move to
  call-time (start anyway, fail on use). The incumbent chose fail-fast and it has never been
  the defect.
- Resolution ladders are ONE entry per platform, DELIBERATELY: `_WIN=["V:\Research4"]`,
  `_NIX=["/sessions/*/mnt/Research4"]`. The sandbox side GLOBS because the session name
  changes every session. Env overrides (`BTS_RESEARCH_ROOT`, `BTS_AI_ROOT`) are checked LAST,
  only if the ladder fails — an override cannot shadow a healthy tree.
- **NO FALLBACK IS THE LOAD-BEARING FEATURE.** `D:\Research3` is deliberately excluded; a
  resolver that silently falls back to a stale tree ships a chapter built on the wrong archive.
  A crash names the problem in one line.
- Role functions: `p/ai/mesh/rold/archive/working/secrets/airoot/queue/board`. NOTE THE SPLIT:
  `mesh()` and `rold()` resolve under AIROOT; `ai()/archive()/working()/secrets()` under ROOT.
  Two roots, and which role belongs to which is HISTORY, not logic — COSMOS gets one root.
- `secrets()` is **safe by LOCATION, not by blocklist**: `.secrets` is a SIBLING of the
  published subtree, so the R2 publish can never ship it. Preserve this property — an exclude
  list is a blocklist and blocklists rot.
- CLI refuses unknown flags (exit 2) rather than printing its report and exiting 0 — added
  after bts_health's selftest caught it swallowing a typo.

**SCARS IT CARRIES (the expensive parts a spec-port would lose):**
- Its own migration sweep CORRUPTED ITS DOCSTRING (rewrote paths inside prose, turned true
  history false, and collapsed the ladder to the same path twice). Rule: path-rewriting tools
  must skip prose.
- `mesh()` returned `ROOT/Ai/BTS_MESH` — a directory that EXISTS and holds ZERO tools — so
  every `isdir()` guard passed while pointing at nothing (fixed 2026-08-21). **An existence
  check is not an identity check.** COSMOS spike must include a content assertion (e.g., the
  resolved mesh dir must contain a named sentinel file).
- The hard-coded-path class it exists to close: on Linux a backslash string SUCCEEDS as a
  filename. Two agents each held "the lock" in different universes (2026-08-16). One
  `os.path.isdir()` would have said so; nothing asked.
- MAX_PATH: a 275-char path returns WinError 3 ("not found") without the `\\?\` prefix.
  COSMOS paths are longer than BTS paths. Every filesystem walk needs the prefix (C-60).

**SPIKE ACCEPTANCE (behavioral, from incidents):**
resolve-or-raise with zero fallback · glob on sandbox side · role-based API · import-time or
justified alternative · refuses unknown flags · sentinel-content check on resolved dirs ·
`\\?\` on walks · prose-safe under migration tooling.

---

## 2 · `tree_lock.py` — mutex + change detection (281 lines)

**WHAT IT ACTUALLY DOES:**
- TWO mechanisms in one file, and the second matters more: (1) a cooperative claim file at
  `bts_paths.queue("tree_lock.json")`; (2) a HASH MANIFEST — sha256[:16] of 8 watched control
  files recorded AT CLAIM TIME. `--verify` distinguishes "changed under me" from "the mount
  lied to me" — a lock says who held the pen, never what the page said.
- Claims expire at 90 min (STALE_MINUTES). A stale claim is reported and may be claimed over
  WITH ANNOUNCEMENT — never silently cleared. `KNOWN_WRITERS` is a closed set; unknown writers
  are refused (exit 2).
- **A TORN LOCK FILE REFUSES rather than reading as free** — `_read()` raises on unparseable
  JSON. Fail-open is the defect class this mesh closed in five separate spend brakes.
- `_sha()` returns None for unreadable-vs-absent and DOES NOT treat either as "changed" —
  collapsing them is how a checker starts crying wolf.
- `release()` runs verify() first, and tolerates the FUSE mount's unlink refusal by BLANKING
  the file instead of pretending failure.
- Selftest is all negative controls: second-writer refusal, unknown-writer refusal, planted
  hash change detected, torn file refuses.

**SCARS / STANDING CONDITIONS:**
- Was hard-coded `V:\Ai\_queue\...` — the two-universes incident above. Now resolves via
  bts_paths. **The fix depends on bts_paths being right — the spike modules are coupled.**
- **COOPERATIVE → LOAD-BEARING TRANSITION ALREADY HAPPENED:** with two queue lanes live
  (2026-08-22), the docstring's "buys visibility, not enforcement" is no longer an acceptable
  trade. Keith's COSMOS requirement: **enforcing locks, concurrency as a scheduler property,
  no last-writer-wins shared file.** The spike must design enforcement (OS-level lock,
  lease-based, or single-arbiter) — the incumbent's shape cannot simply be ported.
- `MESH.parent`-derived paths built a second archive tree elsewhere; this file computes
  `ROLD = MESH.parent / "ROLD"` — **that line is the defect class in residence, and it is
  STILL LIVE in the source** (corrected 2026-08-23 after OA's API-04 caught this doc claiming
  it had been fixed; only LOCK resolves via bts_paths). The spike must not walk up from
  `__file__`.
- 08-22: lock correctly reported `bts_health.py` changed under a claim (Cowork's own edit),
  `--release` returned rc=1, lock went stale at 581 min. Behavior was CORRECT; the lesson is
  the workflow — sessions end without releasing, so expiry is not optional.

**SPIKE ACCEPTANCE:** claim/verify/release with fingerprints · torn-file refusal · stale
takeover with announcement · closed writer set · ENFCORCEMENT design (new) · per-worker
identity in every artifact · no parent-walking.

---

## 3 · `bts_phone.py` — IPC / mailbox (136 lines)

**WHAT IT ACTUALLY DOES:**
- Fixed pair of letter files on the SHARED surface via `airoot()`: CoW writes
  `COW_TO_QA_ENGINEER.md`, reads `QA_ENGINEER_TO_COW.md`. Research4 copies are MIRRORS ONLY.
- **`--check` PROBES THE CHANNEL:** prints both paths and whether the inbound EXISTS. A
  missing inbound letter is "THE PHONE IS DEAD," never "no news" — an empty mailbox and a
  misaddressed one are identical from the sending end. Returns non-zero on missing.
- Belt-and-braces assertion at import: `assert isdir(AIROOT)` — refuses rather than writing a
  letter into cwd (which would look like a successful send).
- Selftest includes a dead-phone NEGATIVE control (points inbox at an impossible dir, requires
  non-zero) and asserts outbox != inbox, mirror != source, no literal backslash survives.

**SCARS:**
- Died TWICE in one day from one defect in two costumes: hard-coded paths (wrong universe) and
  correct syntax on the WRONG SURFACE (letters on Research4 while lock/board moved to V:\Ai).
  "I sent it" and "they received it" are different claims; only one was checked.
- Observed today (2026-08-23): inbound present but stale since 08-18 — the probe reports
  presence + mtime + size so the reader can judge staleness. It does NOT alarm on staleness;
  COSMOS should (a letter older than N days with an open question is a dead conversation).

**SPIKE ACCEPTANCE:** resolver-addressed both ends · probe-not-assume · missing ≠ empty ·
non-zero on dead · refuse-not-guess when the surface is missing · (new) staleness signal ·
(new, from multithread requirement) per-worker identity — two writers to one outbox is the
last-writer-wins shape Keith banned.

---

## 4 · `bts_runner.py` — scheduler / sandbox↔Windows bridge (582 lines)

**WHAT IT ACTUALLY DOES:**
- A native Windows scheduled task ticks every minute per lane; a job is ANY runnable file
  (.py/.bat/.cmd/.ps1) dropped in the queue dir. **The file IS the dispatch.** This is what
  lets the 45-s-capped, V:-blind sandbox run anything: a sandbox that can write a file can
  dispatch anything.
- **Claim-by-rename** into `running\` BEFORE execution — atomic on one volume, two overlapping
  ticks cannot both take a job. **Command is built from the CLAIMED path** — the first version
  resolved before the rename and every job failed rc=1 in 0.1 s including the success control;
  the selftest refused to certify it, which is the only reason a broken runner was not
  scheduled into service. Verifying a path is not verifying the path you are about to use.
- **THREE outcomes, in words:** 0=CLEAN→`done\` · 2=FINDINGS→`done\findings\` ·
  else=BROKE→`failed\`. A checker that correctly finds a discrepancy exits 2 and must not be
  filed as broken (PLM-44 — tidyup2_seal did its job and was recorded as a failure).
- Log opens FIRST ("RUNNING" + cmd), so a crash mid-job is distinguishable from never-started.
  A timeout writes "RED - TIMED OUT," never a silent empty file. Nothing is deleted — ever.
- Stale jobs (>2 h in running\) are REPORTED, never retried — re-running a job whose side
  effects already happened is worse than leaving it visible.
- `_`-prefix = helper, never claimed — enforced IN THE RUNNER after the runner executed a
  helper out from under the .bat calling it. Skips are PRINTED by --status, never silent.
- Per-job timeout from filename (`__tNNNN`, cap 21600). Ledger is APPEND-ONLY jsonl with
  fsync — appends survive the FUSE mount where atomic renames die.
- **LANES (2026-08-22 retrofit):** `--lane lg|pb` rebinds module globals to
  `_queue\_lanes\<name>\`. Each lane single-threaded internally; concurrency BETWEEN streams
  only. Heartbeats moved to the BASE dir as `runner_heartbeat__<lane>.json`, DISCOVERED BY
  GLOB — a checker told the lane names goes green over a lane added later. `--lanes` flags the
  nastiest case: jobs queued into a lane with no runner sit forever, and an unrun queue looks
  exactly like an empty one.
- UTF-8 forced on BOTH ends of the pipe (child env + parent decode) — four tools died on
  emoji under cp1252 the moment stdout was redirected: **the monitor worked whenever anyone
  was watching it.**
- Heartbeat on EVERY tick carries aware-local + epoch + UTC + lane identity — a naked local
  timestamp was twice misread as five hours stale by a UTC reader, and a healthy runner was
  reported dead.

**STANDING CONDITIONS:**
- `QUEUE_BASE = Path(r"V:\Ai\_queue")` is a JUDGED-BENIGN literal (native-only file; `py`
  doesn't exist off Windows so a wrong-platform launch dies at the first job). The COSMOS
  spike resolves it anyway — the audit note says so itself.
- Single-threaded per lane BY DESIGN; a 60-min job parks its own stream. COSMOS requirement:
  concurrency as a scheduler PROPERTY with priority, which makes the lock enforcing (see
  tree_lock). These two spikes are ONE design decision in two files.
- `RUNNABLE` dict deleted 2026-08-22 after drifting from `_cmd_for()` — one predicate now:
  a file is runnable exactly when a command exists for it. Do not reintroduce two
  representations of one fact.

**SPIKE ACCEPTANCE:** claim-by-rename (or better) proven under overlap · claimed-path command ·
three worded outcomes · log-first · report-never-retry · helper convention enforced in-runner ·
per-worker heartbeat, glob-discoverable · UTF-8 both ends · append-only ledger · priority +
concurrency by design · timezone-aware timestamps.

---

## THE CROSS-CUTTING BEHAVIORS — every module, or the port loses the learning
1. **Fail loudly; never guess; never fall back to a stale or plausible path.**
2. **Refuse unknown flags** — a tool that swallows an argument reports success for work it
   never did.
3. **Negative controls in every selftest** — a gate tested only in the passing direction is a
   gate nobody has seen closed. Three of these four selftests REFUSED a broken first version;
   that is the mechanism working.
4. **Absent ≠ unreadable ≠ changed ≠ empty — four states, never collapsed.**
5. **Torn/unparseable state files REFUSE, never read as free/zero/green.**
6. **Every artifact carries who wrote it** (lane, writer, timestamp with offset).
7. **Appends over atomic renames on anything a sandbox might touch.**
8. **A probe beats an assumption; a read-back beats an exit code; behavior beats configuration.**

## ONE-LINE BEHAVIORAL CARDS — the other 135 files
Deferred to the fan-out: the stage 2 packet instructs each vendor to produce cards
(reads/writes/invokers/refusals) for its assigned slice of the remaining modules, with the
scar record as required context. F5 has done the four in depth; buying 135 cards from prepaid
lanes is the delegation rule applied.
