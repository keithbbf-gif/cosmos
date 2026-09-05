# FEATURE MASTER — every discussed feature, triaged against the CODE

**CCr fence 2026-09-05 (Grok 4.6 Build, pen `V:\A`, lease held):** collapsing three
photographs (origin Aug 31 / dirty working tree / dual-lane PRs) into one tree.
Receipts: `docs/FENCE_IDENTITY_2026-09-05.json`, `docs/FENCE_SPLIT_2026-09-05.json`.
Live at photograph: Core pid **45196** `:8770` `ready` `tree_id=KMesh-COSMOS-live`
ledger seq **7635**; Pulse **49048** P0 `RUNNING` collect `reuse` shadow 26/26.
Coding rail **`orders.ggn@gmail.com`** / Kelly display / `project-10b3a132-ec5b-41e9-a2c`
GATE PASS `VERTEX_OK_20260905T103723`; Crucible spend **`vertex-coding`** (seq 7633–7634).
Joanna key in OpenWork grant (Settings still Keith). SGH Heavy **25% used**, last 2%
reserve. Dual-lane PRs **#30 #32 #36 #37 #38** commented **do not merge**. Untracked
probe junk staged to `_delme/fence-quarantine-20260905/` (not origin). F-70 is this
fence. Not a full re-audit of the 70 rows.

**CCr delta 2026-09-04 (Grok 4.6 Build, pen `V:\A`, lease held):** not a full re-audit
of the 70 rows (still **58 DONE / 9 PARTIAL / 3 BLOCKED** as of 2026-08-31). Live
landings this day: `GET /api/v1/surfaces` **200** `cosmos-live`; Pulse **P0** 26/26
`resident.keep` + collect-reuse (`tick=reuse` wins over collector idle/poll);
`groq-api` on WIRED_NODES; native `gem-api` Vertex adapter composed (Joanna `--gate`
`VERTEX_OK_20260904T202510`); `seed_host_surfaces` skips re-measure when a
measurement already exists (Kernel restart last-event stays `BOOT_VERIFIED`);
cDeck pane DND + OpenWork grant `V:\Streams\openwork`; Core `GET /api/v1/fleet` ·
`/nodemap` · `/jukebox` (existing binders, no new measurement) and browser
`/cdeck/` HTTP-fallback so FLEET is not NO_SHELL without Tauri. F-30 WAVE C Groq
**key SATISFIED** (prove path wired; live `--live` not unattended). F-70 still
**dirty / uncommitted**. Database for state is **research-later**, after the open
feature list is implemented. OpenWork GEM BYOK still down; g43 is the
troubleshooting seat. This TUI keeps orch + CCr.

**Consumer:** COW + the queue. This document is intended as the queue's source of truth for
*what has been asked for and what actually exists*. **Authored** 2026-08-31, Claude Code
(Opus 5) on the `cc` lane, work order `130_wishlist_triage`.
**Fence honored:** everything written by this pass is under `docs/` and `builds/triage/`.

**Re-audited 2026-08-31 19:16Z**, Grok Build Worker on the `cc-infra`
fence `builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/`
was not touched.** **None of F-09 / F-15 / F-36 / F-39 fall in this
fence** (evidence in the status cells + `docs/BLOCKED_ITEMS.md`). F-09
leftover is `builds/cvm-dt/` (forbidden). F-15 leftover is
`BENCH_LATENCY.json` UNMEASURED stages (`builds/cvm-dt/`). F-36 leftover
is `write_tracker_json` `authority=markdown` (`cosmos/`, flip restrained
62/96). F-39 leftover is no-invent on `cosmos_codex_rail.py` (`cosmos/`).
F-60/F-69 already DONE. Job spent pinning unexercised REFUSAL claims:
PAUSE.flag / heartbeat JSON of the wrong shape crashed the clocks
(`AttributeError` on `.get`); `spec_for` of a list config crashed;
`load_scopes excludes="git"` silently became `('g','i','t')`; resession
`watermark`/`decide`/`spawn_argv add_dirs="cwd"` / `arm_gate_flag`
crashed or iterated characters; `compare` live=[] AttributeError;
census `exclude_dirs="git"` silent `set('g','i','t')`. Bite
`builds/backup/_bite_unpinned_round8.json` `all_bite:true`;
`builds/probe/_bite_unpinned_round8.json` `all_bite:true`
`could_not_pin=["CLOSE_REFUSED"]`. Fail-old backup **10/10** probe
**13/13** `all_new_pins_failed:true` on
`_delme/predispose_unpinned_round8_20260831T191100Z/`. Then
`test_offsite_clock.py` **45/45**, `test_backup_mounts.py` **43/43**,
`test_local_clock.py` **44/44**, `test_mount_clock.py` **40/40**,
`test_resession.py` **55/55**, `test_artifact_freshness.py` **41/41**,
`test_longpath_census.py` **13/13**. In-fence of the four: **0**.

**Re-audited 2026-08-31 18:55Z**, Grok Build Worker on the `cc-infra`
fence `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**Taxonomy hand-regen recurrence closed.** `docs/REFUSAL_TAXONOMY.md`
had drifted from the code three more times today (11:20, 12:03, 13:43)
because heal was still a paste of
`py -3.14 cosmos/cosmos_refusals.py --out docs/REFUSAL_TAXONOMY.md`.
`--diff`/`--write` existed; the supervisor still pasted. Closed
in-fence with the remesure_probes shape: `stale_in` /
`refresh_if_stale` / `--check` (rc=1 if stale, no write). Default
(no flags) heals stale and exits 0. The suite calls `refresh_stale`
before the live MATCH gate. Live `--check` `stale: []` `match:true`
`typed_refusal_classes=55` `distinct_kinds=141` `render_chars=19556`.
Scratch proof `_bite_taxonomy_kind.json` `all_bite:true`: planted
`SCRATCH_KIND_PROBE`, `--check` rc=1, `refresh_if_stale` healed,
`--check` rc=0, live doc untouched. Bite
`_fail_taxonomy_remeasure_against_old.json` `all_new_pins_failed:true`
**5/5** on
`builds/probe/_delme/predispose_taxonomy_remeasure_20260831T184950Z/`.
Then `builds/probe/test_refusal_taxonomy.py` **62/62**.
`tests/test_refusals.py` **14/14 + 1/1**, not weakened.
**F-36 re-measured** (cannot flip this fence): live
`builds/probe/_f36_judgement.json` `ok:true`
`tree_id=KMesh-COSMOS-live` `consecutive_agreements=62`
`flip_streak_target=96` `ticks_remaining=34` `flip_ready:false`
`authority=markdown` `restraint_justified:true`
`restraint_is_excuse:false` `clock_alive:true` `hb_age_s=647.4`
`open=["parse_tracker_markdown"]`. `test_f36_judgement.py` **23/23**.
Did not flip `write_tracker_json`. F-09/F-15 leftovers are
`builds/cvm-dt/` (forbidden). F-39 leftover is no-invent on
`cosmos_codex_rail.py`. F-69 closed 18:42Z. F-60 closed 18:35Z.

**Re-audited 2026-08-31 18:42Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-69 leftover (dispatch H6 claude-CLI live-prove) closed.** Dispatch
F5 job through `render_job` / `_claude_job` ran `claude -p` and
emitted PONG. Live `cosmos/_f69_h6_live.json` `ok:true`
`tree_id=KMesh-COSMOS-live` `job_rc=0` `result_rc=0`
`stdout_pong:true` `through_harness:true` `secs=21.0`. Bite
`_fail_f69_h6_against_old.json` **6/6 FAIL** `all_new_pins_failed:true`.
Then `tests/test_dispatch.py` **139/139**, `test_dispatch_jobs.py`
**49/49**. `KIND_LIVE` claude/sonnet/haiku/ssa `proven`; cursor stays
`UNPROVEN` (no Cloud Agents launch, no key chase). F-69
**PARTIAL → DONE.** **DONE 57→58, PARTIAL 10→9.** In-fence buildable
remaining of the six: F-36 (flip restrained). F-09/F-15 leftovers are
`builds/cvm-dt/`. F-39 leftover is no-invent on `cosmos_codex_rail.py`.
F-60 closed 18:35Z.

**Re-audited 2026-08-31 18:35Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-60 leftover (health `--once` native `schtasks` spawn) closed.**
`cosmos_clock.run_schtasks` / `harden_task` honor `COSMOS_SCHTASKS_SANDBOX`
so a descendant Python `--once` inherits the fence and never invokes
`schtasks.exe`. Did **not** write `builds/health/`. Live
`cosmos/_f60_sandbox.json` `ok:true` `tree_id=KMesh-COSMOS-live`
health `unfenced_spawns=[]` `procs=2` `python_spawns=1` `rc=0`.
Bite `_fail_f60_sandbox_against_old.json` **6/6 FAIL**
`all_new_pins_failed:true` `old_query_calls=1` on
`_delme/predispose_f60_sandbox_20260831T183526Z/` (old `/query`
still spawned). Then `tests/test_cosmos_test_guard.py` **18/18**,
`tests/test_live_write_fence.py` **23/23**, callers backup **22/22**,
dhx **38/38**, node-bucket **51/51**. F-60 **PARTIAL → DONE.**
**DONE 56→57, PARTIAL 11→10.** In-fence buildable remaining of the
six: F-36 (flip restrained), F-39 (do not invent a seam in
`cosmos_codex_rail.py`), F-69 (H6 live-prove, do not chase keys).
F-09/F-15 leftovers are `builds/cvm-dt/`.

**Re-audited 2026-08-31 18:35Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**None of the six named remainders fall in this fence.** F-09 leftover is
`builds/cvm-dt/` (forbidden). F-15 leftover is `BENCH_LATENCY.json`
UNMEASURED stages (`builds/cvm-dt/`, forbidden). F-36 leftover is
`write_tracker_json` `authority=markdown` (`cosmos/`, flip restrained
58/96). F-39 leftover is inventing a `# seam` in `cosmos_codex_rail.py`
(`cosmos/`). F-60 leftover is `builds/health/test_cosmos_health_watchdog.py`
native `schtasks`. F-69 leftover is dispatch H6 live cursor/claude
FINISHED (do not chase keys). **Job spent wiring R2 into the nightly
03:00 `COSMOS Mount Offsite Push`.** `cosmos_mount_clock.tick()` now
appends a `target_kind=r2` row per scope: PUSHED (read-back re-hash) or
typed `NO_CREDENTIALS` if `live/config/r2_credentials.json` is absent.
Live `--once --source` `_delme_mount_r2_prove/src --force` →
`builds/backup/_mount_r2_live.json` `ok:true` `tree_id=KMesh-COSMOS-live`
r2 row `state=PUSHED` `files_pushed=2` `readback_verified=2`
`bucket=ai-dchambers` `prefix=src/20260831T183424`; gdx `PUSHED`; odx/es3
`NO_DEST` (operator SKIPPED / queued) so CLI rc=1 `state=PARTIAL` — not
a defect. Receipt `kind=R2_PUSH_OK` `secret_access_key=<redacted>`.
schtasks `COSMOS Mount Offsite Push` **Ready** next `9/1/2026 3:00:00 AM`
(`pythonw … cosmos_mount_clock.py --root live --once`) — the same
registered task now pushes R2. Bite `_fail_mount_r2_against_old.json`
`all_new_pins_failed:true` **5/5 FAIL** on
`_delme/predispose_mount_clock_r2_20260831T183114Z/`. Then
`test_mount_clock.py` **39/39**. PARTIAL-with-a-PUSHED-row now stamps
`last_success_epoch` (ODX/ES.3 would otherwise make the heartbeat look
unprotected forever). **Local dest `D:\COSMOS_BACKUP` is the dest and
it does receive sets** (`COSMOS-20260831T172140` 16206 files;
`COSMOS-20260831T174813` 11366). Last clock refusal
`live/logs/local_clock_heartbeat.json` `kind=COPY_HASH_MISMATCH`
`detail="copy of builds/cvm-dt/F21_VOSK_REUSE.json does not hash-match
source"` `last_run=2026-08-31T12:55:12-05:00` — another session writing
`builds/cvm-dt/` mid-copy, not a dest/adapter defect. **Primary-label
counts do not move.** In-fence of the six: **0**.

**Re-audited 2026-08-31 18:12Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-39 leftover (dispatch `# BTS compatibility lane accounting` seam)
closed.** Helpers moved to `cosmos/cosmos_dispatch_lanes.py`; dispatch
re-exports the SAME objects. Live `cosmos/_f39_lanes_split.json`
`ok:true` `tree_id=KMesh-COSMOS-live` `disp_lines=1715` (was 1846 /
73741 bytes) `lanes_lines=214` `measure_same:true` `pick_same:true`.
Bite `_fail_f39_lanes_against_old.json` **9/9 FAIL**
`all_new_pins_failed:true` on
`_delme/predispose_dispatch_f39_lanes_20260831T1812Z/` (predecessor
still defines `measure_lanes` / `pick_least_loaded`; no lanes module).
New suite **34/61** on the unsplit dispatch, then
`tests/test_dispatch_lanes.py` **61/61**. Callers:
`test_dispatch.py` **137/137** (was 135; +2 re-export pins),
`test_dispatch_jobs.py` **49/49**, `test_dispatch_critique.py` **51/51**,
`test_dispatch_workspace.py` **41/41**, `test_dispatcher.py` **39/39**,
`test_motif_driver.py` **62/62**, `test_watchdog2.py` **43/43**. Did
**not** invent a seam in `cosmos_codex_rail.py`. F-39 **stays PARTIAL**.
**Primary-label counts do not move.** In-fence buildable remaining of
the six: F-36 (flip restrained, 58/96), F-39 (DHx/stamps/index helper
banner; do not invent a seam in `cosmos_codex_rail.py`), F-69 (H6
live-prove, do not chase keys). F-09/F-15 leftovers are
`builds/cvm-dt/`. F-60 leftover is `builds/health/`.

**Re-audited 2026-08-31 18:05Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-39 leftover (dispatch `# stage-5 critic visibility` seam) closed.**
Inliners moved to `cosmos/cosmos_dispatch_critique.py`; dispatch
re-exports the SAME objects. Live `cosmos/_f39_critique_split.json`
`ok:true` `tree_id=KMesh-COSMOS-live` `disp_lines=1846` (was 2026 /
80388 bytes) `crit_lines=259` `compose_same:true`
`is_critique_same:true`. Bite `_fail_f39_critique_against_old.json`
**9/9 FAIL** `all_new_pins_failed:true` on
`_delme/predispose_dispatch_f39_critique_20260831T1802Z/` (predecessor
still defines `compose_critique_prompt` / `_inline_file`; no critique
module). New suite **28/51** on the unsplit dispatch, then
`tests/test_dispatch_critique.py` **51/51**. Callers:
`test_dispatch.py` **135/135** (was 133; +2 re-export pins),
`test_dispatch_jobs.py` **49/49**, `test_dispatch_workspace.py` **41/41**,
`test_dispatcher.py` **39/39**, `test_motif_driver.py` **62/62**. Did
**not** invent a seam in `cosmos_codex_rail.py`. F-39 **stays PARTIAL**.
**Primary-label counts do not move.** In-fence buildable remaining of
the six: F-36 (flip restrained, 58/96), F-39 (remaining dispatch helper
banners: BTS lane accounting, DHx/stamps/index; do not invent a seam
in `cosmos_codex_rail.py`), F-69 (H6 live-prove, do not chase keys).
F-09/F-15 leftovers are `builds/cvm-dt/`. F-60 leftover is
`builds/health/`.

**Re-audited 2026-08-31 17:55Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-39 leftover (dispatch `# job source` seam) closed.** Builders moved to
`cosmos/cosmos_dispatch_jobs.py`; dispatch re-exports the SAME objects.
Live `cosmos/_f39_jobs_split.json` `ok:true`
`tree_id=KMesh-COSMOS-live` `disp_lines=2026` (was 2462 / 96467 bytes)
`jobs_lines=516` `render_same:true` `grok_same:true`. Bite
`_fail_f39_jobs_against_old.json` **8/8 FAIL**
`all_new_pins_failed:true` on
`_delme/predispose_dispatch_f39_jobs_20260831T1750Z/` (predecessor still
defines `_grok_job` / `render_job`; no jobs module). Then
`tests/test_dispatch_jobs.py` **49/49**. Callers:
`test_dispatch.py` **133/133** (was 131; +2 re-export pins),
`test_dispatch_workspace.py` **41/41**, `test_dispatcher.py` **39/39**,
`test_motif_driver.py` **62/62**. Did **not** invent a seam in
`cosmos_codex_rail.py`. F-39 **stays PARTIAL**. **F-36 restraint
re-measured, not flipped:** live `cosmos/_f36_sites_live.json` `ok:true`
`consecutive_agreements=58` `flip_ready:false` `authority=markdown`
`restraint_justified:true` `writes_authority_flip=0`. **Whose judgement:**
Keith or COW on the `cosmos/` fence after `flip_ready`;
`FLIP_STREAK_TARGET=96` (scar 2026-08-26). **Primary-label counts do not
move.** In-fence buildable remaining of the six: F-36 (flip restrained,
58/96), F-39 (remaining dispatch helper banners + do not invent a seam
in `cosmos_codex_rail.py`), F-69 (H6 live-prove, do not chase keys).
F-09/F-15 leftovers are `builds/cvm-dt/`. F-60 leftover is
`builds/health/`.

**Re-audited 2026-08-31 17:51Z**, Grok Build Worker on the `cc-cdeck` fence
`builds/cdeck/` · `kdash/` · changelog. **`builds/cvm-dt/` was not touched.**
**None of the six named buildable rows fall in this fence.** Explicitly from
the CODE: F-09 leftover is device-select / felt latency in `builds/cvm-dt/`
(`SpeechRecognition` has no `deviceId`; cDeck kill/mute/resume + `bindMic`
already ship); F-15 leftover is `BENCH_LATENCY.json` UNMEASURED stages
(`builds/cvm-dt/`); F-36 leftover is `write_tracker_json` authority=markdown
(`cosmos/`, flip restrained); F-39 leftover is inventing a `# seam` in
`cosmos_codex_rail.py` (`cosmos/`); F-60 leftover is
`builds/health/test_cosmos_health_watchdog.py` native `schtasks`; F-69 leftover
is dispatch H6 live cursor/claude FINISHED (do not chase keys). Job spent
pinning claims the panel docstring / KINDS comment asserted and never ran:
LEDGER_REFUSED is a runtime wrap of LedgerError (TORN / BROKEN_CHAIN / FORGED),
not a source grep; handle_post of a torn ledger is 400 not 409; jukebox
JOB_DONE / JOB_STALE of a never-submitted job_id do not invent a row. Bite
`_fail_unexercised_r5_against_old.json` **6/6 FAIL** `all_new_pins_failed:true`
`control_still_green:true` on
`_delme/predispose_unexercised_r5_20260831T1751Z/stripped/` (stripped
`except OSError` so LedgerError leaked `kind=TORN`/`BROKEN_CHAIN`/`FORGED`;
jukebox `setdefault` invented `j-ghost` + `j-stale-ghost`). The old
SpendPanelError("LEDGER_REFUSED" grep AND SUBMITTED-then-DONE fold stayed
green. Live `_unexercised_r5_live.json` `ok:true` `tree_id=KMesh-COSMOS-live`
`measured_at_epoch 1788198899.7811315` jukebox `records=1092`
`hmac_verified:false` `chain_linked:true` nodemap `node_count=16` `hb_total=37`
fleet `clock_count=37`. Then `test_spend_panel.py` **60/60**,
`test_jukebox_panel.py` **54/54**, `test_create_panel.py` **65/65**.
`remeasure_probes.py --check` `stale: []`. **Primary-label counts do not
move.** In-fence PARTIAL remaining: **F-09** (leftover is `builds/cvm-dt/`,
forbidden). Of the six named buildable rows, **0** fall in this fence.

**Re-audited 2026-08-31 17:49Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**None of the six remaining buildable rows fall in this fence.** F-09 / F-15
leftovers are `builds/cvm-dt/` (forbidden). F-36 leftover is the markdown
authority flip (`cosmos/`, Keith/COW after 96). F-39 leftover is inventing a
seam in `cosmos_codex_rail.py` (`cosmos/`). F-60 leftover is
`builds/health/test_cosmos_health_watchdog.py`. F-69 leftover is dispatch H6
live-prove (do not chase keys). Job spent on unexercised refusals.
**Pinned 20** (backup fail-old **12/12 FAIL**, probe **8/8 FAIL**). **Could
not pin 1:** `CLOSE_REFUSED`. **Primary-label counts do not move.**

**Re-audited 2026-08-31 17:40Z**, Grok Build Worker on the `cc-cdeck` fence
`builds/cdeck/` · `kdash/` · changelog. **`builds/cvm-dt/` was not touched.**
**None of the six named buildable rows fall in this fence.** Explicitly:
F-09 leftover is `builds/cvm-dt/` (device-select / felt latency); F-15 leftover
is `BENCH_LATENCY.json` UNMEASURED stages (`builds/cvm-dt/`); F-36 is `cosmos/`
(tracker authority still markdown, 56/96); F-39 leftover is inventing a seam in
`cosmos_codex_rail.py`; F-60 leftover is `builds/health/` native schtasks;
F-69 leftover is live cursor/claude FINISHED (do not chase keys). Job spent
pinning claims the panel docstrings asserted and never ran: a lying stamped
`age_s` is ignored (fleet last_run_epoch / nodemap last_probe / heartbeat
last_run_epoch) and jukebox `JOB_CLAIMED` is QUEUED-only (no CLEAN resurrection,
no stolen RUNNING worker). Bite `_fail_unexercised_r4_against_old.json`
**5/5 FAIL** `all_new_pins_failed:true` `control_still_green:true` on
`_delme/predispose_unexercised_r4_20260831T1740Z/stripped/` (stripped preferred
stamped `age_s=1.0`/`0` and CLAIMED any in-state job). Live
`_unexercised_r4_live.json` `ok:true` `tree_id=KMesh-COSMOS-live`
`measured_at_epoch 1788198074.1749916` jukebox `records=1092`
`hmac_verified:false` `chain_linked:true` nodemap `node_count=16` `hb_total=37`
fleet `clock_count=37`. Then `test_fleet_panel.py` **64/64**,
`test_nodemap_panel.py` **60/60**, `test_jukebox_panel.py` **52/52**,
`test_create_panel.py` **65/65**. `remeasure_probes.py --check` `stale: []`.
**Primary-label counts do not move.** In-fence PARTIAL remaining: **F-09**
(leftover is `builds/cvm-dt/`, forbidden).

**Re-audited 2026-08-31 17:30Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-39 leftover (collector `# scanning` seam) closed.** Walkers moved to
`cosmos/cosmos_collector_scan.py`; collector re-exports the SAME objects.
Live `cosmos/_f39_scan_split.json` `ok:true`
`tree_id=KMesh-COSMOS-live` `coll_lines=1948` (was 2106 / 87360 bytes)
`scan_lines=217` `walk_same:true` `kept_same:true`. Bite
`_fail_f39_scan_against_old.json` **8/8 FAIL**
`all_new_pins_failed:true` on
`_delme/predispose_collector_f39_scan_20260831T173040Z/` (predecessor still
defines `_walk_files` / `iter_queue_files`; no scan module). Then
`tests/test_collector_scan.py` **66/66**. Callers:
`test_collector.py` **72/72** (scan re-export pin),
`test_collector_dhx.py` **38/38**, `test_own_clocks.py` **88/88**,
`test_cosmos_index.py` **44/44**. Did **not** invent a seam in
`cosmos_codex_rail.py`. F-39 **stays PARTIAL**. **Primary-label counts
do not move.** In-fence buildable remaining of the six: F-36 (flip
restrained, live streak **56/96**), F-39 (do not invent a seam in
`cosmos_codex_rail.py`), F-69 (H6 live-prove, do not chase keys).
F-09/F-15 leftovers are `builds/cvm-dt/`. F-60 leftover is
`builds/health/`.

**Re-audited 2026-08-31 17:25Z**, Grok Build Worker on the `cc-cdeck` fence
`builds/cdeck/` · `kdash/` · changelog. **`builds/cvm-dt/` was not touched.**
**F-11 leftover (live `/cdeck/` mount still recorded as 404) closed.** The
resident process had already reloaded (26th-pass `KDASH_AUTH_PROBE.json`
signed `/cdeck/` HTTP 200). This bite re-gated `CORE_CDECK_PROBE.json`
with FULL bodies vs disk. Fresh artifact
`label=AFTER-F11-2026-08-31T1725Z` `ok:true` `tree_id=KMesh-COSMOS-live`
seq **1547** `served_at` 1788197359.008386: `/cdeck` **302**; five-file
shell **200** `match_disk:true` (23340 / 184893 / 31532 / 3436 / 7410);
unsigned `/api/v1/status` **401**; traversal **401**; no ACAO. Bite
`_fail_f11_against_old.json` **15/15 FAIL** `all_new_pins_failed:true`
`control_still_green:true` on seq-1444 404 incumbent. Then
`test_core_cdeck.py` **25/25**; `test_remeasure_probes.py` **43/43**;
`test_kdash_auth.py` **28/28**; `remeasure_probes.py --check` `stale: []`.
F-11 **PARTIAL → DONE**. **DONE 55→56, PARTIAL 12→11.** In-fence
PARTIAL remaining: **F-09** (device-select / felt latency — leftover is
`builds/cvm-dt/`, forbidden). Of the six named buildable rows, none of
F-15 / F-36 / F-39 / F-60 / F-69 fall in this fence.

**Re-audited 2026-08-31 16:41Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-60 leftover (CLOCKS `schtasks` writers outside any Python audit hook)
closed for `tests/`.** `sandbox_heartbeats()` now wraps
`cosmos_clock.run_schtasks` / `harden_task`; a `/create` of
`COSMOS Collector` is typed `PROD_WRITE_REFUSED` and the real writer
is not invoked (`called_real:false`). `test_live_write_fence.py` now
fences `tests/test_backup_clock.py`. Live
`cosmos/_f60_schtasks.json` `ok:true` `tree_id=KMesh-COSMOS-live`.
Bite `_fail_f60_schtasks_against_old.json` **4/4 FAIL**
`all_new_pins_failed:true` on
`_delme/predispose_f60_schtasks_20260831T164154Z/`; suite-before
**7/11**. Then `test_cosmos_test_guard.py` **11/11**;
`test_backup_clock.py` **22/22**; `test_collector_dhx.py` **38/38**;
`test_node_bucket_worker.py` **51/51**; `test_live_write_fence.py`
**22/22**. Health suite still `unfenced_spawns=["schtasks"]` (outside
this fence). F-60 **stays PARTIAL**. **Primary-label counts do not
move.** In-fence buildable remaining of the six: F-36 (flip
restrained 51/96), F-39 (do not invent a seam in
`cosmos_codex_rail.py`), F-69 (H6 live-prove, do not chase keys).
F-09/F-15 leftovers are `builds/cvm-dt/`.

**Re-audited 2026-08-31 16:30Z**, Grok Build Worker on the `cc-infra` fence
`builds/cc_driver/` · `builds/backup/` · `builds/probe/` · `docs/`.
**`builds/cvm-dt/` was not touched.**
**Job 390 re-filed by the classifier, not by hand.**
`py -3.14 builds/cc_driver/cc_refile.py --root V:/A/Ai/COSMOS/live --lane cc-infra --job 390_gbw_buildable_nine --apply`
→ `outcome=MAX_TURNS_WITH_OUTPUT` `route=timed_out` `artifacts=8/24211B`.
`cc-infra` `failed=0` (`timed_out/` holds 370 + 390).
**F-43 leftover (identity unread) closed.** `local_row()` returned
`targets.local.identity` and `bind_local()` never called
`_check_identity`, so a swapped disk at the same letter still got a
verified set. Bite `_bite_f43_identity.json` `all_bite:true`
(`mismatch_tick_verified:true` `mismatch_created_a_set:true`
`bind_local_has_identity_param:false`). `_fail_f43_identity_against_old.json`
**6/6 FAIL** `all_new_pins_failed:true` on
`_delme/predispose_f43_identity_20260831T162758Z/` (old mismatch
`state=VERIFIED` `set_count=1`). Live `_f43_identity_live.json`
`ok:true` `mismatch.kind=IDENTITY_MISMATCH` `sets=[]`
`match.state=VERIFIED` clock 15590 `41991288…`. Then
`test_local_clock.py` **31/31**. Live `--preflight`
`_f43_clock_live_preflight.json` `cli_rc=2` `kind=NO_CONFIG`
`heartbeat_written:false` `live_heartbeat_exists:false`.
`--install-task` was not run. F-43 **PARTIAL → DONE (code) / dest+VSS
BLOCKED / not scheduled**. **DONE 54→55, PARTIAL 13→12.** In-fence
buildable remaining of the eight: **0**. Operator leftovers (F-41 apply,
F-54 dest/cred+register, F-43 dest+VSS Create+register) not chased.

**Re-audited 2026-08-31 16:25Z**, Grok Build Worker on the `cc-cdeck` fence
`builds/cdeck/` · `kdash/` · changelog. **`builds/cvm-dt/` was not touched.**
**F-05 leftover (FEATURE_MASTER cell still PARTIAL) closed.** Code already
had viewport-keyed phone drag (`mapIsDraggable() → true`,
`nmapPosStore()` writes `cdeck.nodePositions.phone`). The cell still
described a static list. This pass re-measured, did not rewrite `ui/`.
Fresh `builds/cdeck/MOBILE_PROBE.json` `label=AFTER-F05-2026-08-31T1625Z`
`tree_id=KMesh-COSMOS-live` `probed_at_epoch 1788193556.8032436` 320
`phoneWrote:true` `desktopUnchanged:true` `firstNodePosition=absolute`
`nodes=31` `nodesOutsideStage=0`. `app.js` 184893 sha256
`7b47ec6d…adf6442` MATCH STAGE6. Bite
`test_mobile_layout.py --against …T1615Z/ui` **30/38**, **8 of 8 new
pins FAIL**. Shipped **115/115** + `test_nodemap_panel.py` **55/55**.
`remeasure_probes.py --check` `stale: []`. F-05 **PARTIAL → DONE**.
**DONE 53→54, PARTIAL 14→13.** In-fence buildable remaining: **F-09**
(device-select / felt latency — leftover is `builds/cvm-dt/`).

**Re-audited 2026-08-31 16:14Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-39 leftover (CVM projection seam) closed.** Helpers moved to
`cosmos/cosmos_cvm_projection.py`; `cosmos_service` re-exports the SAME
objects. Live `cosmos/_f39_cvm_split.json` `ok:true`
`tree_id=KMesh-COSMOS-live` `svc_lines=1581` (was 1732 / 96893 bytes)
`proj_lines=202` `cvmerror_same:true`. HTTP GET `/api/v1/cvm/pull` 200
`pull:false` + POST `/cvm/snapshot` 200 idempotent. Bite
`_fail_f39_cvm_against_old.json` **6/6 FAIL** `all_new_pins_failed:true`.
New suite **20/27 FAIL** on the unsplit service, then
`tests/test_cvm_projection.py` **44/44**. Callers: `test_cvm_p3` **28/28**,
`test_cvm_push` **6/6**, `test_cdeck_shell` **10/10**, `test_makers` **56/56**,
`test_v1` **18/18**, `test_events_page` **10/10**. Did not split voice
hardening or `cosmos_codex_rail.py`. F-39 **stays PARTIAL**.
**Primary-label counts do not move.** In-fence buildable remaining:
**F-39** (voice-hardening banner + `cosmos_codex_rail.py` — no `# seam`
banner). F-53 was closed DONE (code) by a concurrent 16:16Z bite.

**Re-audited 2026-08-31 16:19Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**No in-fence PARTIAL remains buildable.** Remaining **3** are all
operator-blocked: F-41 (COW PORT_DECISIONS / live `--apply` is
`LIVE_LEDGER_FORBIDDEN`), F-43 (Keith dests + elevated
`Win32_ShadowCopy.Create`), F-54 (dest/cred + Keith `--install-task`).
Job spent pinning unexercised refusals. Bite
`builds/backup/_bite_unpinned_round6.json` `all_bite:true`
`untyped_seal=AttributeError` `untyped_scan=KeyError`
`scan_files_str_silent:true` (a string of `install_key.bin` returned
`[]`). `_fail_unpinned_round6b_against_old.json` **8/8 FAIL**
`all_new_pins_failed:true`. Probe
`_fail_unpinned_round6b_against_old.json` **3/3 FAIL**
`all_new_pins_failed:true` (`classify_pause([])` was AttributeError).
Then `test_cosmos_backup.py` **90 OK, 1 skipped**;
`test_cosmos_backup_r2.py` **43/43**; `test_local_clock.py` **25/25**;
`test_resession.py` **48/48**. Could not pin: `CLOSE_REFUSED` (never
raised; needs live kernel `close_session`). Operator leftovers not
chased. F-41 `--apply` not run. **Primary-label counts do not move.**
In-fence PARTIAL remaining: **3** — all operator-blocked, **zero
buildable**.

**Re-audited 2026-08-31 16:16Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-53 leftover (PARALLEL was mailbox-ping + drop 0) closed.** COW-fresh
tick now drops one MOTIF work-order into the resolver bucket when none
is already open (`open_prepaid_orders` flood guard). Queue drop only;
never writes kernel/ledger/sched/service. Spawn still opt-in. Live
`--once --dry-run` `cosmos/_f53_live.json` `ok:true` `winner=grok`
`grok_present:true` `state=ORCHESTRATE` `cow_fresh:false`
`tree_id=KMesh-COSMOS-live` `writes:0` `dropped:0` `spawned:0`
(COW quiet on this host; PARALLEL proven hermetically). Bite
`_fail_f53_parallel_against_old.json` **6/6 FAIL**
`all_new_pins_failed:true` `old_dropped=0` `old_order_count=0`. Then
`tests/test_prepaid_orch.py` **24/24** `parallel_state=PARALLEL`
`dropped=1`; `tests/test_own_clocks.py` **88/88**. `--install-task`
was not run; `--spawn` was not fired. F-53 **PARTIAL → DONE (code) /
not scheduled**. **DONE 52→53, PARTIAL 15→14.**

**Re-audited 2026-08-31 16:12Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**No in-fence PARTIAL remains buildable.** Remaining **3** are all
operator-blocked: F-41 (COW PORT_DECISIONS / live `--apply` is
`LIVE_LEDGER_FORBIDDEN`), F-43 (Keith dests + elevated
`Win32_ShadowCopy.Create`), F-54 (dest/cred + Keith `--install-task`).
Job spent pinning unexercised freeze refusals. Bite
`builds/backup/_bite_unpinned_round6.json` `all_bite:true`
(`noinfo_dobackup_crash=AttributeError` `noinfo_dobackup_kind=null`
`garbage_str_kind=BAD_FREEZE` `occupied_kind=FREEZE_DEST_OCCUPIED`
`tests_name_BAD_FREEZE:false` `tests_name_FREEZE_DEST_OCCUPIED:false`).
`acquire()` now requires `info()`; missing is typed `BAD_FREEZE`
(never a silent live copy that later AttributeErrors).
`_fail_unpinned_round6_against_old.json` **2/2 FAIL**
`all_new_pins_failed:true` (predecessor returned `_NoInfo`;
`do_backup` `AttributeError`). Then `test_cosmos_backup.py` **80 OK,
1 skipped**. Operator leftovers not chased. F-41 `--apply` not run.
**Primary-label counts do not move.** In-fence PARTIAL remaining: **3**
— all operator-blocked, **zero buildable**.

**Re-audited 2026-08-31 16:05Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-36 leftover (four of five OPEN derivation sites) closed.** Work order
2.3 sites `critique_filename_stage`, `inflight_filenames_mtime`,
`wd2_dhx_haystack`, `wd2_uses_inflight_filenames` are now advisory.
Skip/stage authority is leases + ledger + the tracker row; filenames
and DHx prose cannot decide a skip. Live
`cosmos/_f36_derivation_audit.json` `ok:true` `open_count=1`
`open=["parse_tracker_markdown"]`. Live `cosmos/_f36_sites_live.json`
`ok:true` `tree_id=KMesh-COSMOS-live` `consecutive_agreements=51`
`flip_ready:false` `restraint_justified:true`
`restraint_is_excuse_for_flip:false`. **Whose judgement (2.1a):** Keith
or COW on the `cosmos/` fence after `flip_ready`; `FLIP_STREAK_TARGET=96`
(scar 2026-08-26). The flip restraint **still holds**. 2.2 lands in the
same tick as the flip. Bite `_fail_f36_sites_against_old.json` **8/8
FAIL** `all_new_pins_failed:true`. Did not flip `write_tracker_json`.
F-36 **stays PARTIAL**. **Primary-label counts do not move.**

**Re-audited 2026-08-31 16:04Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**F-43 leftover (P0 daemon had no schtasks vehicle) closed.**
`builds/backup/cosmos_backup.py` already refused without dest; nothing
emitted a `schtasks /create` line. `--plan-task` now emits
`COSMOS Bulletproof Backup` daily 04:00 and registers nothing
(`_f43_clock_plan_task.json` `registers:false`). Same-volume dest is
typed `SAME_VOLUME`. Live `--preflight` `_f43_clock_live_preflight.json`
`cli_rc=2` `status=BLOCKED` `kind=NO_CONFIG` `adapter_implemented:true`
`heartbeat_written:false` `live_heartbeat_exists:false`. Bite
`_bite_f43_plan_task.json` `all_bite:true` (`clock_exists:false`
`import_state=ABSENT`). `_fail_f43_plan_task_against_old.json` **5/5 FAIL**
`all_new_pins_failed:true`. Then `test_local_clock.py` **22/22**.
`--install-task` was not run. F-43 **stays PARTIAL** (dests / VSS Create).
F-36 streak re-measured **51/96** `flip_ready:false` `clock_alive:true`.
Operator leftovers not chased. F-41 `--apply` not run. **Primary-label
counts do not move.** In-fence PARTIAL remaining: **3** — F-41 (COW
PORT_DECISIONS / live apply forbidden), F-43 (dests / VSS Create), F-54
(dest/cred + Keith `--install-task`).

**Re-audited 2026-08-31 15:56Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**F-36 leftover (unnamed "deliberate restraint") closed in canon.** The
restraint is **still justified, not an excuse:** live
`builds/probe/_f36_judgement.json` `ok:true` `tree_id=KMesh-COSMOS-live`
`consecutive_agreements=50` `flip_streak_target=96` `ticks_remaining=46`
`flip_ready:false` `authority=markdown` `clock_alive:true` `hb_age_s=703.6`
`restraint_justified:true` `restraint_is_excuse:false`. Whose judgement:
`FLIP_STREAK_TARGET=96` in `cosmos_motif_driver.py` (2026-08-30 CC audit;
scar 2026-08-26); the flip actor is **Keith or COW on the `cosmos/` fence**
after `flip_ready`. Work order **2.1a** now lives in
`docs/CORE_RESTRUCTURE.md`. Bite `_bite_f36_judgement.json` `all_bite:true`
(incumbent had no 2.1a). `_fail_f36_against_old.json` **5/5 FAIL**
`all_new_pins_failed:true`. Then `test_f36_judgement.py` **22/22**;
`test_artifact_freshness.py` **32/32** `live_matched:12`. This fence did
**not** flip `write_tracker_json`. F-36 **stays PARTIAL**. Operator
leftovers not chased. F-41 `--apply` not run. **Primary-label counts do
not move.** In-fence PARTIAL remaining: **3** — F-41 (COW PORT_DECISIONS /
live apply forbidden), F-43 (dests / VSS Create / schtasks), F-54
(dest/cred + Keith `--install-task`).

**Re-audited 2026-08-31 15:43Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**F-54 leftover (no schtasks vehicle) closed.** Packer already refused
`NO_OFFSITE_ROUTE`; nothing emitted a `schtasks /create` line, and the
F-47/F-48 clocks push *scopes*, not the F-54 whitelist. `--plan-task`
now emits `COSMOS State Offsite Push` daily 03:15 and registers nothing
(`_f54_clock_plan_task.json` `registers:false`). Bite
`_bite_f54_plan_task.json` `all_bite:true` (`has_plan_task_argv:false`
CLI `--plan-task` not a verb). `_fail_f54_plan_task_against_old.json`
**5/5 FAIL** `all_new_pins_failed:true`. Then `test_state_offsite.py`
**25/25**. Live `--preflight` still `NO_OFFSITE_ROUTE` payload **4 / 340044**.
`--install-task` was not run. F-54 **stays PARTIAL** (dest/cred).
In-fence PARTIAL remaining: **3** — F-41 (COW PORT_DECISIONS / live
apply forbidden), F-43 (dests / VSS Create / schtasks), F-54 (dest/cred
+ Keith `--install-task`).

**Re-audited 2026-08-31 15:22Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**The leftover whose stated unblock was inside this fence: F-43 VSS
freeze.** Closed in code: `do_backup(..., freeze=)` copies from a
point-in-time read-root; default is still SOURCE_MUTATED detect.
`FrozenTree.capture` live `_f43_freeze_live.json` `frozen_survived:true`
`frozen_kind=copy` (live source mutated, sealed hash equals freeze-time).
`freeze=True` is VSS; live probe `V:\` NTFS `drive_type=3`
`kind=VSS_UNAVAILABLE` `scode=0x80041014` (never a silent live-tree
copy). Bite `_bite_f43_freeze.json` `all_bite:true` (`has_freeze_param:false`
`freeze_kw_crash=TypeError`); `_fail_f43_freeze_against_old.json`
**4/4 FAIL** `all_new_pins_failed:true`. Then `test_cosmos_backup.py`
**77 OK, 1 skipped**. F-41 `--apply` still `LIVE_LEDGER_FORBIDDEN`
ledger **661088** untouched. Operator leftovers were **not** chased.
**Primary-label counts do not move** (F-43 stays PARTIAL on dests).
In-fence PARTIAL remaining: **3** — F-41 (COW PORT_DECISIONS / live
apply forbidden), F-43 (dests / VSS Create / schtasks), F-54 (dest/cred).

**Re-audited 2026-08-31 15:00Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**Every unblocked in-fence infra row is DONE.** The one leftover whose
stated unblock was inside this fence: F-28 (15 unmapped HANDS stems).
Closed: `docs/COMPETENCY.toml` `[nodes.*]` **6 → 21**, census
`_f28_hands_vs_nodes.json` `unmapped_count=0` `node_count=21`
`pin=SUPERSET`. Filed rows are `possessed=false rating=0` HANDS-cited;
`router.nodes_order` still the live six; `pick()` still `code-build=G46`
`web-research=SGH` `DOM-automation=DOM`. Bite staged incumbent
`_bite_f28_unmapped.json` `unmapped_count=15` `node_count=6`;
`_fail_f28_against_old.json` `all_new_pins_failed:true`. Then
`builds/probe/test_f28_competency_map.py` **14/14**;
`tests/test_competency.py` **31/31** `live_six_nodes` lists 21 ids.
Ratings were **not** invented. F-30 WAVE A1/A2 is already in
`cosmos/cosmos_forge_rail.py` (WAVE C is Keith). F-41 `--apply` still
`LIVE_LEDGER_FORBIDDEN` ledger **643712** untouched
(`_f41_live_apply_refused.json`). F-54 live `--preflight`
`NO_OFFSITE_ROUTE` payload **4 / 324562** bytes
(`_f54_live_preflight.json`). Stale claim artifacts restamped:
`test_artifact_freshness.py` **30/30** `live_matched:10`. Operator
leftovers were **not** chased (OpenAI key, schtasks, slack webhook, Core
restart, `backup_targets.json`, R2 credential, Seagate ES.3). F-41 was
**not** applied to the live authority ledger. **DONE 46→47, PARTIAL 16→15.**

**Re-audited 2026-08-31 14:42Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**Every unblocked in-fence infra row is DONE or precisely parked.**
Explicitly: F-26/F-31/F-65 DONE (code) / not scheduled; F-44/F-45/F-47/F-48/F-49/F-50
DONE (code); F-28 parked (`live_six_nodes` pin is `tests/`); F-30 WAVE C operator;
F-41 parked (`LIVE_LEDGER_FORBIDDEN`, not applied); F-43 parked (same-volume dest /
VSS / Keith dests); F-54 parked (`NO_OFFSITE_ROUTE`); F-46 BLOCKED (Keith, R2
credential); F-48 dests unconfigured (`backup_targets.json`) and ES.3 unmounted;
F-47/F-48/F-51/F-63 `--install-task` are Keith's `schtasks` line; F-32 OpenAI key;
F-57 Slack webhook; F-11 Core restart. Operator leftovers were **not** chased.
F-41 `--apply` on the live authority ledger was **not** run. Job spent pinning
unexercised refusals: **8 pinned**, **1 could not**. Bite
`_bite_unpinned_round5.json` backup `all_bite:true` (check_seal array/string
`AttributeError`; local garbage `JSONDecodeError`; local array returned `list`;
R2 garbage `JSONDecodeError`; R2 `true` returned `bool`); probe `all_bite:true`
(scout array `AttributeError`; hands garbage `JSONDecodeError`; hands array
`AttributeError`). Fail-against-old backup **5/5** + probe **3/3**
`all_new_pins_failed:true`. Then `test_cosmos_backup.py` **68 OK, 1 skipped**;
`test_cosmos_backup_r2.py` **41/41**; `test_backup_mounts.py` **41/41**;
`test_newai_scout.py` **29/29**; `test_maker_hands.py` **9/9**. Could not pin:
`CLOSE_REFUSED` (never raised; needs live kernel `close_session`). **Primary-label
counts do not move.**
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 14:22Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**Every unblocked in-fence infra row is DONE or precisely parked.**
Explicitly: F-26/F-31/F-65 DONE (code) / not scheduled; F-44/F-45/F-47/F-48/F-49/F-50
DONE (code); F-28 parked (`live_six_nodes` pin is `tests/`); F-30 parked
(WAVE A wiring is `cosmos/`); F-41 parked (`LIVE_LEDGER_FORBIDDEN`, not
applied); F-43 parked (same-volume dest / VSS / Keith dests); F-54 parked
(`NO_OFFSITE_ROUTE`); F-46 BLOCKED (Keith, R2 credential); F-48 dests
unconfigured (`backup_targets.json`) and ES.3 unmounted; F-47/F-48/F-51/F-63
`--install-task` are Keith's `schtasks` line; F-32 OpenAI key; F-57 Slack
webhook; F-11 Core restart. Operator leftovers were **not** chased. F-41
`--apply` on the live authority ledger was **not** run. Job spent pinning
unexercised refusals: **11 pinned**, **1 could not**. Bite
`_bite_unpinned_round4.json` backup `all_bite:true` (model mismatch bound;
sentinel mismatch bound; identity-not-object `AttributeError`; config array
`AttributeError`; empty credential accepted; JSON `true` `TypeError`); probe
`all_bite:true` (`hands_missing_kind=null` `scout_missing_kind=NO_ROOT`
readback-stripped `healed` over `WRONG-BYTES`). Fail-against-old backup
**7/7** + probe **4/4** `all_new_pins_failed:true`. Then
`test_backup_mounts.py` **41/41**; `test_cosmos_backup_r2.py` **39/39**;
`test_newai_scout.py` **27/27**; `test_maker_hands.py` **6/6**;
`test_refusal_taxonomy.py` **33/33**. Could not pin: `CLOSE_REFUSED`
(never raised; needs live kernel `close_session`). **Primary-label counts
do not move.**
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 14:12Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**In-fence PARTIAL rows (remaining work lives under this fence or its
docs): F-26, F-28, F-30, F-41, F-43, F-54.** Operator leftovers were
**not** chased (OpenAI key, schtasks, slack webhook, Core restart,
`backup_targets.json`, R2 credential, Seagate ES.3). F-41 `--apply` on
the live authority ledger still REFUSES `LIVE_LEDGER_FORBIDDEN`.

From the CODE, not the prose:
- **F-26 PARTIAL → DONE (code) / not scheduled.** CLOCKS id 23
  (`cosmos/cosmos_own_clocks.py`) + live `newai_scout_heartbeat.json`
  `state=SCOUTED` `clock_id=23`. Other-lane live
  `cosmos/_f26_live.json` `proposed_count=15` remote `http=200`
  **`names=0`** (table-bold parser on a GitHub-link README). **This
  fence** built `builds/probe/cosmos_newai_scout.py` which parses
  `[org/repo](https://github.com/…)` ; live `--dry-run`
  `_f26_live_dryrun.json` `kind=MINED` `feed_count=29` `new_count=20`
  `writes=0` `delta=0` head `codex, claude-code, gemini-cli, zed, warp,
  gpt-engineer, continue, tabby`. Bite `_bite_f26_scout_absent.json`
  `all_bite:true`; junk-parse bite `_bite_f26_junk_parse.json` harvested
  "Inclusion criteria"; then `test_newai_scout.py` **24/24**. `--once`
  was **not** fired (would overwrite CLOCKS 23's live heartbeat).
- **F-31 / F-65 PARTIAL → DONE (code) / not scheduled** — CLOCKS ids
  20 / 21 / 22 exist in `cosmos_own_clocks.py` (other lane 14:04Z;
  `docs/BLOCKED_ITEMS.md`). Remaining is Keith's `--install-task`.
- **F-28 stays PARTIAL.** Census `_f28_hands_vs_nodes.json`
  `node_count=6` `unmapped_count=15`. This fence *can* write
  `docs/COMPETENCY.toml`; `tests/test_competency.py` `live_six_nodes`
  is an exact-set pin (outside fence). Adding a `[nodes.X]` row would
  FAIL that suite. Did not invent ratings.
- **F-30 stays PARTIAL.** STAGE3 WAVE A–D *is* the arch
  (`docs/critique/makerhands_STAGE3.md`). Remaining is wiring (cosmos/,
  outside) + WAVE C operator install/key.
- **F-43 stays PARTIAL.** In-fence leftover **COVERAGE gap 4 closed:**
  `do_backup` REFUSES `SECRETS_IN_SCOPE` before a set is created.
  Predecessor sealed a planted `install_key.bin`
  (`_fail_f43_secrets_against_old.json` **2/2 FAIL**
  `all_new_pins_failed:true`). Then `test_cosmos_backup.py` **63 OK,
  1 skipped**. Remaining: same-volume dest / `V:\` scope / VSS / Keith
  dests (named in BLOCKED_ITEMS).
- **F-41 / F-54** unchanged: live ledger APPLY forbidden; offsite
  packer `NO_OFFSITE_ROUTE`.
**DONE 40→43, PARTIAL 17→14.** F-61 clocks **19→23** (does not change
the F-61 primary label).
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 13:54Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**Every unblocked in-fence infra row is DONE.** Explicitly: F-44/F-45/F-47/F-48/F-49/F-50
DONE (code); F-46 BLOCKED (Keith, R2 credential); F-48 dests unconfigured
(`backup_targets.json`) and ES.3 unmounted; F-47/F-48/F-51/F-63 `--install-task`
are Keith's `schtasks` line; F-41 live-ledger APPLY (`LIVE_LEDGER_FORBIDDEN`) +
PORT_DECISIONS (outside fence; not applied); F-54 dest/credential; F-32 OpenAI
key; F-57 Slack webhook; F-11 Core restart. Operator leftovers were **not**
chased. **F-51 prompt leftover was a fence artifact** (prior job's fence was
`cosmos/` + `tests/`; this fence includes `docs/`): P1.3 filed; live
`--dry-run` `prompt_sha=5d10d8ff510503a00b01d6a2b1efca7941ca92a10efc3aa1c6ed59082cfca8db`
`state=IDLE` `tree_id=KMesh-COSMOS-live` `writes:0`
(`builds/probe/_f51_prompt_live.json`). Job then pinned unexercised refusals:
**8 pinned**. Bite `_bite_unpinned_round3.json` backup `pack_dest_file_crash=FileExistsError`
`keep_true_is_int:true`; probe `resumed_tidy_class=HOLD` `stripped would ARM`.
Fail-against-old backup **4/4** + probe **1/1** `all_new_pins_failed:true`. Then
`test_cosmos_backup.py` **59 OK, 1 skipped**; `test_backup_mounts.py` **35/35**;
`test_state_offsite.py` **18/18**; `test_resession.py` **45/45**. Could not pin:
`CLOSE_REFUSED` (never raised; needs live kernel `close_session`); taxonomy
`UNWRITABLE` readback (same leftover as round 2). **Primary-label counts do not
move.**
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 13:53Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
FOLLOW leftover was HEALTH_BOARD (stamped 13:22Z, live Core not reloaded)
plus two writers COSMOS already emits with **zero** FOLLOW_KEYS:
**BACKUP_VERIFIED** (28 live rows; was 1 of the last-100 tail) and
**COMMAND_HANDLED** (56 live rows; PULSE_HOME → CVM, so pulse lit the
box without a harvestable id). This pass stamps both on disk.
**Bite first:** `tests/test_follow_ids.py` current **11/17 FAIL** (6 new
pins); `tests/test_command.py` **2 FAIL** (`COMMAND_HANDLED.node` /
`COMMAND_REFUSED.node`); `_fail_follow_backup_command_against_old.json`
`all_new_pins_failed:true` **5/5** `old_backup_node=null`
`old_command_node=null` `old_clock_backup_nodes=[null]`. Then current
**17/17** + prechange-lacks-keys **11/11**; `test_command.py` **54/54**;
`test_backup_clock.py` **14/14** `whole_scope_node=COSMOS`. Hermetic
`cosmos/_f_backup_command_follow.json` `ok:true` `command.node=CVM`
`backup.node=COSMOS` `files=1`. Clock `Backup(ledger, node=paths.sentinel.system)`;
CLI the same via `k.paths.sentinel.system`. Live census re-measured
`cosmos/_follow_live_measure.json` n=1334 `head_seq=1334` `tail_with_any=16/100`
`tail_missing {HEALTH_BOARD:84}` (BACKUP_VERIFIED left the tail; historical
zero-id rows remain until the clock ticks / Core reloads). Core was **not**
restarted. F-28 still needs `docs/COMPETENCY.toml` (outside this fence; no
invented ratings). F-41 live apply still `LIVE_LEDGER_FORBIDDEN`.
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 08:41 −05:00**, Grok Build Worker on the `cc-cdeck` fence
`builds/cdeck/` · `kdash/` · `docs/`. **`builds/cvm-dt/` was not touched.**
Stale cDeck rows corrected from **emitted probe values**, not source reads.
`remeasure_probes.py --check` on this ui/ (`app.js` 181620 / `sw.js` 7410) was
`stale: []` before the kdash edit. **F-02** 49/49 → **51/51** (`test_spend_panel.py`
run this pass). **F-11** stays PARTIAL — `CORE_CDECK_PROBE.json` signed
`GET /cdeck/` **HTTP 404 `NOT_FOUND`**, unsigned **401 `UNAUTHORIZED`**, signed
`/api/v1/status` **200** `tree_id=KMesh-COSMOS-live` `seq=1315`
`served_at` 1788183185.7421699. **F-13** evidence moved: `PWA_PROBE.json`
cache **`cdeck-shell-v5`**, `test_pwa.py` **67/67**. **F-09** start/stop listen
ships; leftover is CVM-DT. Then **KDASH_REFRESH.toml on `kdash/index.html`
(`/dash`)**: BEFORE rails=audit=tools=**6** in 75s; AFTER **1**, spend stayed **6**,
chips `tier SLOW · 60s / 180s` and `tier FAST · 10s / 30s`
(`KDASH_TIER_PROBE.json` seq 1322). Bite **1/16**; shipped **28/28**.
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 13:42Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**Every in-fence infra row is DONE, parked, or operator-blocked** (F-46 Keith
credential; F-47/F-48/F-51/F-63 `schtasks`; F-48 dests / `backup_targets.json`;
F-41 live ledger + PORT_DECISIONS; F-54 dest/cred; F-32 OpenAI key; F-57 Slack
webhook; F-11 Core restart). Operator leftovers were **not** chased. F-41
`--apply` on the live authority ledger still REFUSES `LIVE_LEDGER_FORBIDDEN`
(deliberate). Job spent pinning unexercised refusals: **9 pinned**, **2 could
not**. Bite `_bite_unpinned_round2.json` (backup `dest_file_old_crash=FileNotFoundError`;
probe `tax_unwritable_old_crash=FileExistsError` `not_windows_raise_present:false`
`bad_spec_raise_present:false` `close_refused_raise_present:false`). Fail-against-old
backup **2/2** + probe **7/7** `all_new_pins_failed:true`. Then
`test_cosmos_backup.py` **56 OK, 1 skipped**; `test_longpath_census.py` **11/11**;
`test_credential_manifest.py` **46/46**; `test_tool_disposition.py` **21/21**;
`test_refusal_taxonomy.py` first tick **29/30** `kind=DRIFT` `healed=true`
`render_chars=18294` (suite contract), second **30/30** `kind=MATCH`. Could not
pin: `CLOSE_REFUSED` (never raised; needs live kernel `close_session`); taxonomy
`UNWRITABLE` readback mismatch (not hermetic without mocking a successful write).
**Primary-label counts do not move.**
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 13:22Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
Stale rows corrected from **code/live artifacts**, not prose:
**F-24 leftover** (two `tests/` literals spelling "the four") is already
closed in `tests/test_rails_prober.py` + `tests/test_boot_attach.py`
(`WIRED_NODES` 8 ids, `count == len(WIRED_IDS)`). **F-66** UNMEASURED →
**DONE (code) / dest unconfigured / workers not started** —
`tests/test_grok_gem_bucket_workers.py` **58/58**; GDX without config is
`NO_DEST`; configured ODX lands under `COSMOS/returns/gem`. **F-69**
collector HIGH (H1–H4) is closed in code (`tests/test_collector.py`
**71/71**; live `dhx.json` `markers=173` `matched=167` `missing=6`);
dispatch H1 drive-literal default is gone; remaining is H6 unproven
cursor/claude through the harness (do not chase keys) — F-69 **stays
PARTIAL**. Then the named FOLLOW leftover: live tail **90/100
`HEALTH_BOARD`** carried none of `FOLLOW_KEYS` (`cosmos/_follow_live_measure.json`
`head_seq=1295` `tail_with_any=9` `newest_event=HEALTH_BOARD`). Disk
writer now stamps `node=sentinel.system` (`COSMOS`). Bite first:
`tests/test_follow_ids.py` current **10/11 FAIL**;
`test_migrate_health.py` + `test_command.py` the new pin FAIL;
`_fail_follow_health_against_old.json` `all_new_pins_failed:true`
`old_node=null`. Then current **11/11** + prechange-lacks-keys **7/7**;
`test_migrate_health.py` **13/13**; `test_command.py` **52/52**.
Hermetic emit `cosmos/_f_health_follow.json` `node=COSMOS` `verdict=GREEN`.
Resident `:8770` has not reloaded — live ledger still writes HEALTH_BOARD
without `node` until Keith restarts `serve` (F-11-shaped).
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 13:26Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
Operator-blocked leftovers were **not** chased (OpenAI key, schtasks, slack
webhook, Core restart, `backup_targets.json`, R2 credential; F-41 live
ledger apply still `LIVE_LEDGER_FORBIDDEN`). Highest remaining in-fence
value: **claim-artifact freshness** — the same class of red that hit
cDeck when `FEATURE_PROBE.json` still named `ui/` byte counts of a
vanished build. Probe/backup evidence JSON had **no** `describes`
fingerprint. Bite `_bite_artifact_freshness.json` `all_bite:true`
(`dated_longpath_kind=UNFINGERPRINTED`, `backup_src_newer_than_dated_longpath:true`
`cosmos_backup.py` 12:49:31Z vs longpath 07:27:06Z). Fail-against-old
**10/10 UNFINGERPRINTED** on staged incumbents. Then writers stamp
`describes` (bytes+sha256); live artifacts re-measured; `test_artifact_freshness.py`
**30/30** `live_matched:10`. Stale FEATURE_MASTER numbers corrected from
the new artifacts (F-40 17918→18235; F-54 payload 254853→293610; F-41
ledger 559724→607100 still untouched by `--apply`; F-44 longpath
re-run `COVERS_LONG_PATHS`). **Primary-label counts do not move.**
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 13:12Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
After F-29, the highest remaining in-fence value-over-effort slice:
**F-60 leftover (two `tests/` suites) closed.** `tests/cosmos_test_guard.py`
`sandbox_heartbeats()` is PROD_WRITE_REFUSED outside the OS temp dir.
**Bite:** staged
`_delme/predispose_f60_20260831T131200Z/` has **no** `sandbox_heartbeats`;
CONTROL unguarded `write_heartbeat` **did write** outside temp
(`scar_unguarded_wrote:true`); guarded same path is
`PROD_WRITE_REFUSED` and creates no file. Then
`tests/test_cosmos_test_guard.py` **6/6**, `test_collector_dhx.py`
**38/38**, `test_node_bucket_worker.py` **51/51** (heartbeat under
`%TEMP%\cosmos_node_bucket_*\live\logs\`). `builds/health/` suite and
CLOCKS `schtasks` writers stay outside this fence — F-60 **stays PARTIAL**.
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 13:10Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tools/` · `tests/`. **`builds/cvm-dt/` was not touched.**
**F-29 PARTIAL → DONE (code)** — the fence-only leftover (promote
`builds/probe/tools/` to repo-root `tools/` + Kernel compose) is closed.
`tools/surface.py` + `tools/mcp_docs.py` are the live surface; Kernel
`compose_rails` row `("tools-surface", "tools.mcp_docs", "attach_to_kernel", True)`
binds `kernel.tools` and does **not** invoke on boot (`tools_compose.invoked=false`).
**Bite first:** `tests/test_tools_surface.py` **FAIL 0/2** `state=ABSENT` while
repo-root `tools/` was missing; `tests/test_tools_compose.py` **FAIL 4/9** on
the incumbent kernel (no compose row); `_fail_f29_against_old.json`
`all_new_pins_failed:true` **4/4 FAIL** against
`_delme/predispose_cosmos_kernel_f29_20260831T130051Z/`. Then hermetic
**15/15**, `--live` **17/17**, compose **9/9**, `tests/test_kernel.py`
**21/21** (was 18). Boot suites: `test_boot_attach.py` **21/21**,
`test_boot_rails.py` **12/12**. **Live composed surface answers:**
`cosmos/_f29_composed_live.json` `ok:true` `composed_tools_surface:true`
`openai-docs value=openai-docs-mcp http=200`
`xai-docs value=xai-docs-mcp http=200` (vendor-emitted `serverInfo.name`).
Further tools beyond these two stay F-30. F-41 live-ledger apply was
**not** run (`LIVE_LEDGER_FORBIDDEN` stands).
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 12:48Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tests/`. **`builds/cvm-dt/` was not touched.** Highest remaining
in-fence cosmos/ engineering after F-27: **F-55** PARTIAL → **DONE (code)** —
hash-chained append (`prev_hash` / `msg_sha256` / `GENESIS_HASH`), writer HMAC
(`writer_sig` when keyed), `cosmos_lock` fenced send (`mail:{to}` GRANT+COMMIT
+RELEASE; HELD is one writer). Kernel composes `arbiter=` + install `key=`.
Bite first: `cosmos/_bite_f55_mail.json` `all_bite:true` (no prev_hash, no
arbiter=, planted lie unread). Then `_fail_f55_against_old.json`
`all_new_pins_failed:true` **8/8 FAIL** against
`_delme/predispose_cosmos_mail_f55_20260831T124826Z/`. `tests/test_cosmos_mail.py`
**23/23** (`cosmos/_f55_mail_suite.json` `chain_head` bound);
`tests/test_kernel.py` **18/18** (`k.mail.arbiter is k.arbiter`, COMMIT
`mail:critic`, signed genesis). GrokBot participant is F-53, not this row.
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 12:46Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
In-fence PARTIAL whose remaining slice was **not** operator-blocked:
**F-43 leftover closed (gap 3 + gap 5).** Torn snapshot no longer seals
`MANIFEST` (`SOURCE_MUTATED`); oldest finished sets stage to `_delme/`
(`do_retire`, `keep<1` is `KEEP_TOO_SMALL`, never deletes). Bite
`_bite_f43_mutate_retire.json` `all_bite:true` (incumbent sealed
`BACKUP_OK` over a mutated `a.txt`; `has_do_retire:false`). New pins
**10/10 FAIL** against
`builds/backup/_delme/predispose_cosmos_backup_f43_20260831T124639Z/`
(`_fail_f43_against_old.json` `all_new_pins_failed:true`). Then
`test_cosmos_backup.py` **51 OK, 1 skipped** (was 39+1; +12). Live
`_f43_mutate_retire_live.json` `ok:true` `mutated_kind=SOURCE_MUTATED`
`manifest_sealed:false` `retire_kind=RETIRE_OK` `never_deleted:true`
`keep_zero_kind=KEEP_TOO_SMALL`. F-43 **stays PARTIAL** (scheduled
same-volume `live/` snapshot; dests/credential; `cosmos/` clock gaps).
Those remaining slices are now named in `docs/BLOCKED_ITEMS.md` — a
PARTIAL with no recorded blocker is the worst kind of row. Operator
items were **not** re-attempted. ⚠
`builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 12:45Z**, Grok Build Worker on the `cc-cdeck` fence
`builds/cdeck/` · `kdash/` · `docs/`. **`builds/cvm-dt/` was not touched.**
Stale rows corrected from **code/live artifacts**, not prose:
**F-16** PARTIAL/`PENDING_CORE` → **DONE (gated)** — `STAGE6_SPLIT.json`
`local.verdict=PASS` counts PASS 11, `core.verdict=PASS` counts PASS 4
`PENDING_CORE:0` `core_reachable:true` `live_tree_id=KMesh-COSMOS-live`.
**F-17** BLOCKED-on-F-33 → **DONE (gated)** — `STAGE6_GATE.json` `ok:true`,
`STAGE6_CORE.json` `verdict=PASS`; F-33 is DONE. Executing `cvm_dt.py`
57611 B `084157e3…` ≠ gated `57146`/`f9a3892d…` (in-flight piper session
outside this fence). **F-59** ABSENT → **DONE** — `cc_outcome.classify`
`TIMED_OUT_WITH_OUTPUT`; `test_cc_outcome_evidence.py` **28/28** run this
pass. Then the highest remaining in-fence kDeck item: **row 29** — COSMOS's
own traffic lights the node map. `REAL_PULSE_PROBE.json` `synthetic=0`
signed `/status` 200 `tree_id=KMesh-COSMOS-live` seq **1270**; paint window
`pulses 96 on 8 node(s)` lit `{COSMOS, cursor-api, firecrawl-web, gem-api,
gw-api, oa-api, playwright-dom, sgh-api}` matching the live tail;
`lit_unexpected: []`. CONNECT-race queue in `ui/app.js` (`nmapPulsePending`
/ `flushPendingPulses`). Bite: `test_real_pulses.py --against` pre-edit
**3/11** (8 FAIL); shipped **23/23**.
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 12:34Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**Every in-fence infra row is DONE, parked, or operator-blocked** (F-46 Keith
credential; F-47/F-48/F-51/F-63 `schtasks`; F-48 dests; F-29 promote; F-41
live ledger; F-54 dest/cred; F-32/F-57 keys; F-11 Core restart). Job spent
on verification hardening: `STAGE_OCCUPIED`, `RESTORE_HASH_MISMATCH`,
`REHEARSAL_HASH_MISMATCH`, `SOURCE_NOT_DIR`, `NOT_A_BACKUP_SET` were in the
kind set and in `do_restore` / `build_manifest` prose, unpinned. Bite
`_bite_stage_restore.json` `all_bite:true` (occupied stage clobbered and
still `RESTORE_OK`; flipped retrieve sealed `RESTORE_OK` /
`REHEARSAL_PASS`; file-as-source `SOURCE_UNREADABLE`; empty set
`FileNotFoundError`). New pins **5/5 FAIL** against the stripped
predecessor, then `test_cosmos_backup.py` **39 OK, 1 skipped** (was 33+1;
+6). Live `_stage_restore_live.json` all five kinds match,
`stage_untouched:true` `dest_untouched:true`. No row primary-label moved.
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 12:28Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
F-40 leftover closed: `docs/REFUSAL_TAXONOMY.md` drifted TWICE because
regen was a hand step (`>` on Windows mangles em-dashes). Now
`builds/probe/regen_refusal_taxonomy.py` + `test_refusal_taxonomy.py`
(clock-collected `builds/*/test_*.py`) diffs, prints the exact
`--out` command, and heals on drift so the next tick MATCHES.
`tests/test_refusals.py` is **not** weakened (still fails the same tick).
Bite `_bite_refusal_taxonomy_absent.json` `state=ABSENT`;
`_bite_refusal_taxonomy.json` `all_bite:true`. Live tick
`_refusal_taxonomy_tick.json` `kind=MATCH` `typed=49` `kinds=128`
`render_chars=17918` `cp437_would_drift:true`. **F-63 re-measured:**
default-scan `--dry-run` is `MINED` `transcripts_seen=2555`
`findings=252` `dry_run:true`; `live/logs/askmine_heartbeat.json`
still absent. Primary-label counts do not move. ⚠
`builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 12:40Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tests/`. **`builds/cvm-dt/` was not touched.** FOLLOW emit
was already landed (re-checked: `cosmos_tools.declare` / `cosmos_makers.add`
stamp `node=`; `tests/test_follow_ids.py` not re-run this pass). Stale
rows corrected from **code/live artifacts**, not prose: **F-33** ABSENT →
**DONE** (signed `GET /api/v1/status` `:8770` HTTP 200 `tree_id=KMesh-COSMOS-live`
`ready=true` `ledger_head.seq=1270`; `live/state/health/board.json`
`verdict=GREEN` `reds=[]` `serve_8770.ok=true` `rtt_s=0.0092`); **F-34**
PARTIAL dormant → **DONE** (`live/logs/health_clock_heartbeat.json`
`serve_supervisor.kind=ALREADY_UP`). Premise 4 clocks **18 → 19**. Then
the highest remaining in-fence cosmos/ row: **F-27** PARTIAL → **DONE
(code)** — `cosmos/cosmos_competency.py` `pick()`; WD2 `pick_agent` now
reads `docs/COMPETENCY.toml`. Live pick `web-research→SGH`
`code-build→G46`. `tests/test_competency.py` current **31/31**,
prechange-lacks-consumer **4/4**. Bite first: module ABSENT + unwired
`pick_agent` TypeError on `matrix=` (`cosmos/_bite_f27_competency.json`
`all_bite:true`; `_bite_f27_pick_agent.json` 25/30 with 5 FAIL).
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 12:18Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tests/`. **`builds/cvm-dt/` was not touched.** FOLLOW emit
(TOOL_DECLARED / MAKER_ADDED / BOOT_VERIFIED `node=`) was already landed
11:21Z — `tests/test_follow_ids.py` current **10/10**, prechange-lacks-keys
**6/6**. This pass took the next in-fence cosmos/ row: **F-63** (PARTIAL →
**DONE (code) / not scheduled** — `cosmos/cosmos_askmine.py` CLOCKS id 19;
`tests/test_askmine.py` **66/66**; WD2 `MD_ROUTE_SOURCES` third source
`askmine` / `live/state/askmine/UNANSWERED.md`). **F-61** 18 clocks → **19**.
`--install-task` not run. ⚠ `builds/triage/FEATURE_MASTER.json` stays a stale
projection.

**Re-audited 2026-08-31 12:05Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
**Every in-fence infra row is DONE, parked, or operator-blocked** (F-46 Keith
credential; F-47/F-48/F-51 `schtasks`; F-48 dests; F-29 promote; F-41 live
ledger; F-54 dest/cred; F-32/F-57 keys). Job spent on verification
hardening: `SEAL_HMAC_MISMATCH` and `COPY_HASH_MISMATCH` were in the kind
set and in prose, unpinned. Bite `_bite_hmac_copyhash.json` `all_bite:true`
(forged HMAC passed sha256-only `check_seal`; null HMAC TypeError on the
incumbent; unhashed corrupt copy sealed a MANIFEST). Then
`test_cosmos_backup.py` **33 OK, 1 skipped** (was 22; +11). Null HMAC is
now typed `SEAL_HMAC_MISMATCH` (`_hmac_copyhash_live.json`). No row
primary-label moved. ⚠ `builds/triage/FEATURE_MASTER.json` stays a stale
projection.

**Re-audited 2026-08-31 07:05–07:35Z**, Claude Code (Opus 5) on the `cc-infra` lane, fence
`builds/backup/` · `builds/probe/` · `docs/`. Rows changed: **F-44** (ABSENT → DONE),
**F-25** (evidence + a built, proven fix), **F-41** (re-measured, unchanged). Every changed
row cites the artifact that justifies it.

**Re-audited 2026-08-31 10:33–10:42Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
Rows changed: **F-29** (ABSENT → PARTIAL — `builds/probe/tools/` surface, live-bound),
**F-47** (ABSENT → DONE (code) / not scheduled — `test_offsite_clock.py` 35/35),
**F-25** leftover closed (mesh_blockers now names `stale`, does not count it live).
**F-41** re-measured, unchanged. ⚠ **`builds/triage/FEATURE_MASTER.json` is now
STALE** — it carries this markdown's old sha256, which is exactly how it is supposed to
announce that. It was not regenerated because `builds/triage/` is another lane's fence:
`py -3.14 builds/triage/feature_master_index.py --repo V:/A/Ai/COSMOS` is COW's to run.

**Re-audited 2026-08-31 11:00–11:05Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
Rows changed: **F-48** (ABSENT → DONE (code) / dest unconfigured), **F-49**
(STALE → DONE — generated doc now names the landed R2 adapter), **F-50**
(PARTIAL → DONE (code) — `--open` / `open_doors`, injected opener). **F-25**
already DONE, not re-opened. **F-29** remaining (repo-root `tools/` + Kernel
compose) is outside this fence — `docs/BLOCKED_ITEMS.md`. **F-41** not picked
(Low/L). ⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Re-audited 2026-08-31 11:30Z**, Grok Build Worker on the `cc` fence
`cosmos/` · `tests/`. **`builds/cvm-dt/` was not touched.** Rows changed:
**F-51** (PARTIAL — clock vehicle, not promoted → **DONE (code) / not scheduled
/ prompt unfiled** — `cosmos/cosmos_resession.py` CLOCKS id 18; `test_resession.py`
**46/46**; live `--dry-run` `state=IDLE` `tree_id=KMesh-COSMOS-live`
`clock_id=18`; heartbeat absent). **F-61** (17 clocks → **18**). Bite first:
`cosmos/_bite_f51_promote.json` `all_bite:true` (`module=ABSENT` FileNotFoundError,
staged CLOCKS `max_id=17` no `cosmos_resession.py`). `--install-task` was not
run. `docs/AUTO_RESESSION_PROMPT.md` is still unfiled (`prompt_sha: null`; a
fire is typed `NO_PROMPT`). ⚠ `builds/triage/FEATURE_MASTER.json` stays a stale
projection.

**Re-audited 2026-08-31 11:08–11:14Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
Rows changed: **F-48** (DONE (code) / dest unconfigured → **DONE (code) / dest
unconfigured / not scheduled** — `cosmos_mount_clock.py`, 34/34, live preflight
`status=BLOCKED` `NO_CONFIG` `adapter_implemented:true`). **F-51** stays PARTIAL
(still not in `cosmos/` / `CLOCKS`) but the in-fence leftover closed:
`--plan-task` emits `COSMOS Resession` minute/1 and registers nothing (36/36;
staged old module `has_plan_task_argv:false`). **F-54** re-measured, unchanged
(no copy off this volume until dests or the R2 credential land). **F-29**
remaining and **F-41** not picked. ⚠ `builds/triage/FEATURE_MASTER.json` stays
a stale projection. *Superseded on F-51 by the 11:30Z promotion — the table
cell is the current truth.*

**Re-audited 2026-08-31 11:56–11:57Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
Rows changed: **F-47** (DONE (code) / not scheduled — leftover closed:
`ADAPTERS["r2"]()` is typed `NO_CREDENTIALS` not a stub; `do_rehearse_target`
is Gate B offline; `DEFAULT_EXCLUDES` includes `__pycache__`; live
`_f47_live_adapter.json` `kind=NO_CREDENTIALS` `writes:0`). **F-41** stays
PARTIAL; the in-fence leftover (116 UNPLANNED cards) closed —
`_f41_unplanned_cards.json` `card_count:116` `with_candidates:47` `disposition:null`
on every card; live `--apply` still `LIVE_LEDGER_FORBIDDEN`, ledger **559724**
bytes mtime unchanged. **F-46** re-measured BLOCKED (no `r2_credentials.json`).
**F-48** re-measured, primary label unchanged. ⚠ `builds/triage/FEATURE_MASTER.json`
stays a stale projection.

**Re-audited 2026-08-31 11:28–11:30Z**, Grok Build Worker on the `cc-infra` fence
`builds/backup/` · `builds/probe/` · `docs/`. **`builds/cvm-dt/` was not touched.**
Rows changed: **F-41** (ABSENT → **PARTIAL** — proposer built, 27 apply-ready,
live authority **not** written: `LIVE_LEDGER_FORBIDDEN`, ledger size 548417
mtime unchanged), **F-54** (PARTIAL, payload packer now exists —
`cosmos_state_offsite.py`, live preflight `BLOCKED` `NO_OFFSITE_ROUTE`
`payload.present=4` `bytes=254853`, `heartbeat_written:false`). F-46/F-47/F-48
clocks re-checked green (35/35 + 34/34), still waiting on Keith's dest/credential.
⚠ `builds/triage/FEATURE_MASTER.json` stays a stale projection.

**Machine-readable projection:** `builds/triage/FEATURE_MASTER.json`, regenerated by
`builds/triage/feature_master_index.py`. **This markdown is authority; the JSON is a
rebuildable projection** that carries the markdown's sha256 so a stale copy is detectable.
The parser's own selftest carries three negative controls (missing source, no rows, short
row) because a parser that cannot refuse is not a parser — **9/9, run**.

---

## How to read this — the evidence rule

Every status in the tables below was determined by **opening the code or an emitted
artifact**, not by reading the prose that named the feature. Six of the rows contradict the
document that requested them, and those contradictions are called out in §3 rather than
silently resolved.

| Status | What it means here |
|---|---|
| **DONE** | An implementing symbol exists **and** an emitted artifact or a test run proves it does the thing. Both halves required. |
| **PARTIAL** | Some named slices land and at least one named slice does not — including *built but not running*, which is the most common shape in this tree. |
| **ABSENT** | No implementing symbol found. A design document, a proposal, or a research note is **not** an implementation and does not lift a row off ABSENT. |
| **BLOCKED** | The code is finished; a credential or an operator action Keith owns is the only thing missing. Distinguished from ABSENT because the engineering is done. |

**`rc=0` is not evidence and neither is a docstring.** Where a claim rests on something I
could not measure, the row says **UNMEASURED** in the evidence cell.

**Measurements in this document were taken 2026-08-31 between 05:55Z and 06:25Z**, on the
live tree at `V:\A\Ai\COSMOS`, root `V:\A\Ai\COSMOS\live` (`tree_id KMesh-COSMOS-live`).

### Tests I actually ran for this pass

| Command | Result |
|---|---|
| `py -3.14 cosmos/cosmos_contracts.py --audit --root V:/A/Ai/COSMOS --out builds/triage/contract_audit_20260831T0600Z.json` | **27/27 contracts verified, 0 contradictions** |
| `py -3.14 builds/cdeck/test_jukebox_panel.py` | **40/40 passed** |
| `py -3.14 builds/cdeck/test_nodemap_panel.py` | **52/52 passed** |
| `py -3.14 builds/cdeck/test_spend_panel.py` | **49/49 passed** |
| `py -3.14 builds/backup/test_cosmos_backup_r2.py` | **29 tests, OK** |
| `py -3.14 builds/probe/test_resession.py` | **32/32**, `live_value {"checks": 32, "refusal_kinds": ["BAD_SEED","IDENTITY_MISMATCH","NO_DECL"]}` |
| `py -3.14 builds/cvm-phone/test_cvm_phone_pull.py` | **5/5** |
| `py -3.14 builds/triage/feature_master_index.py --repo V:/A/Ai/COSMOS --selftest` | **9/9**, incl. 3 negative controls; `live_value {"rows": 70, "counts": {"DONE":24,"PARTIAL":23,"ABSENT":17,"BLOCKED":4,"STALE":1,"UNMEASURED":1}}` |
| read-only `Kernel` + `ToolContracts.report()` on the live root (no writes) | **143 tools · `Counter({'UNDECIDED': 135, 'REPLACED': 8})`** |

### Tests run by the RE-AUDIT pass — 2026-08-31 07:05–07:35Z (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

Kept separate from the authoring pass above rather than merged into it, so neither table
claims a run the other made.

| Command | Result |
|---|---|
| `py -3.14 builds/probe/test_registry_freshness.py --impl-live` | **FAIL — 13 of 20** (intended: this is the F-25 defect proof) |
| `py -3.14 builds/probe/test_registry_freshness.py --impl builds/probe/proposed/cosmos_registry.py` | **PASS — 20/20** |
| `py -3.14 builds/probe/proposed/run_suites_against_proposed.py --live` | **8/8 suites PASS** (control) |
| `py -3.14 builds/probe/proposed/run_suites_against_proposed.py` | **8/8 suites PASS** (proposed module bound) |
| `py -3.14 builds/backup/test_longpath.py` | **10 tests OK**, 1 skipped (POSIX identity) |
| `py -3.14 builds/backup/test_cosmos_backup.py` | **19 tests OK**, 1 skipped (`COSMOS_TEST_DOCS`) |
| `py -3.14 builds/probe/longpath_census.py behave --scratch …` | `cosmos/cosmos_backup.py` → **`COVERS_LONG_PATHS`** (was `SILENTLY_OMITS`) |
| `py -3.14 builds/probe/registry_freshness_effect.py` | replica delta: `count 4→3`, `false_verified_removed ["claude-cli"]` |
| read-only `Kernel` + `ToolContracts.report()` (F-41 re-measure) | **143 rows · `Counter({None: 135, 'REPLACED': 8})`** |

**Total for the re-audit pass: 6 suites run, 6 passed** (20 + 8 + 8 + 10 + 19 + the 8 control
suites are the same 8 re-bound) — plus one deliberate FAIL run and two read-only
measurements. The deliberate FAIL is not counted as a passing suite; it is the evidence that
the new test bites, per *"prove any regression test FAILS against the old code."*

### Tests run by the 10:33–10:42Z pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

| Command | Result |
|---|---|
| `py -3.14 builds/probe/test_mesh_blockers.py` against live (pre-fix) | **FAIL — 27/31** (4 new F-25 leftover checks; intended bite) |
| same 4 checks against `_delme/predispose_mesh_blockers_20260831T103327Z/mesh_blockers.py` | **FAIL 0/4**, `kind=NO_PROOF` (the scar: live_nodes() dropped the row) |
| `py -3.14 builds/probe/test_mesh_blockers.py` against the fix | **PASS — 31/31** |
| `py -3.14 builds/probe/mesh_blockers.py --root …/live --write-md` | `live_count 7`, `stale_count 1`, `claude-cli kind=STALE_PROOF in_stale=true in_registry=false`; MESH_STATUS: *"`stale` list — `claude-cli`"*. Artifact: `builds/probe/_blockers_freshness.json` |
| `py -3.14 builds/probe/test_tools_surface.py` before `tools/` existed | **FAIL 0/2**, `live_value {"state":"ABSENT"}` |
| `py -3.14 builds/probe/test_tools_surface.py` (hermetic) | **PASS — 15/15**, `live_value {"tools":["openai-docs","xai-docs"]}` |
| `py -3.14 builds/probe/test_tools_surface.py --live` | **PASS — 17/17** including LIVE `xai-docs-mcp` and `openai-docs-mcp` |
| NONZERO_RC check against `LegacyAnyBodyPass` | **FAIL** — shim returned `ok:true rc:1` (maker-hands scar) |
| `py -3.14 builds/probe/tools/mcp_docs.py --live` | `openai-docs value=openai-docs-mcp http=200`; `xai-docs value=xai-docs-mcp http=200`. Artifact: `builds/probe/_tools_surface_live.json` |
| `py -3.14 builds/backup/test_offsite_clock.py` | **35 tests OK** (F-47 re-audit) |
| read-only `Kernel` + `ToolContracts.report()` (F-41) | **143 rows · `UNDECIDED 135 · REPLACED 8`**, zero writes. Artifact: `builds/probe/_f41_remeasure.json` |

**Total for this pass: 4 suites run green** (31 + 15 + 17 + 35) **plus three deliberate FAIL runs** (pre-fix mesh_blockers 27/31, staged-old 0/4, tools ABSENT 0/2, and the legacy-shim NONZERO_RC bite). The FAIL runs are the proof the new checks bite.

### Tests run by the 11:00–11:05Z pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

| Command | Result |
|---|---|
| staged-old `ADAPTERS["gdx"]()` / `["odx"]()` (`_delme/predispose_cosmos_backup_f48_20260831T055254Z/`) | **FAIL — `NotImplementedError`, `kind: null`**. Artifact: `builds/backup/_bite_f48_stubs.json` |
| `py -3.14 builds/backup/test_backup_mounts.py` | **PASS — 31/31**, including the staged-old bite and `selfcheck` `MOUNT_PUSH_OK` + `REHEARSAL_PASS` |
| `py -3.14 builds/backup/test_cosmos_backup.py` | **20 tests OK, 1 skipped** (`COSMOS_TEST_DOCS`); new `TestRemoteSeams` expects `NO_CONFIG` not `NotImplementedError` |
| `py -3.14 builds/backup/test_cosmos_backup_r2.py` | **29/29 OK** (no regression on the R2 sibling) |
| live `bind` (creates nothing) + `preflight` + `selfcheck` | Artifact `builds/backup/_f48_live_bind.json`: **gdx READY** `vol:19831116` label `Google Drive` ≠ src `vol:8046DC70`; **odx READY** `vol:3242CB17`; **es3 DRIVE_NOT_MOUNTED** names `ST3000NM0033`; preflight **`status=BLOCKED` `adapter_implemented:true` `NO_CONFIG`**; selfcheck **`files_pushed:1` `bytes_pushed:14` `rehearsal_kind=REHEARSAL_PASS`** |
| staged-old `credential_manifest` R2 row | **BITE** `wired=false` `severity=PLANNED` `open_doors` absent. Artifact: `builds/probe/_bite_f49_f50_old.json` `all_bite: true` |
| `py -3.14 builds/probe/test_credential_manifest.py` | **PASS — 42/42** (was 34; +F-49 wired/BLOCKED + F-50 injected opener) |
| `py -3.14 builds/probe/credential_manifest.py --root …/live --write-md` | **`ok: true`**, tally `BLOCKED 2 · DEGRADED 1 · PLANNED 1 · SATISFIED 3`; `ask_now` includes `r2-credentials`. Generated `docs/CREDENTIALS_NEEDED.md` **Measured 2026-08-31T11:00:59Z** |

**Total for this pass: 4 suites green** (31 + 20 + 29 + 42 = **122** individual checks, plus 1 skip) **plus two deliberate FAIL/bite runs** (old GDX/ODX stubs, old R2 PLANNED row). No key material was read.

### Tests run by the 11:08–11:14Z pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

| Command | Result |
|---|---|
| import `cosmos_mount_clock` before the file existed | **BITE** `state=ABSENT` `kind=ModuleNotFoundError`. Artifact: `builds/backup/_bite_mount_clock_absent.json` |
| staged-old `cosmos_resession.py` (`_delme/predispose_cosmos_resession_f51_20260831T060817/`) | **BITE** `has_plan_task_argv:false` `has_TASK_NAME:true` `all_bite:true`. Artifact: `builds/probe/_bite_f51_plan_task.json` |
| `py -3.14 builds/backup/test_mount_clock.py` | **PASS — 34/34**, including the absent bite, `NO_CONFIG` heartbeat, FakeProbe push `files_pushed:2` under scratch `data/`, `--plan-task` registers nothing, fresh-interpreter CLI |
| `py -3.14 builds/probe/test_resession.py` | **PASS — 36/36**, `live_value {"checks": 36, "refusal_kinds": ["BAD_SEED","IDENTITY_MISMATCH","NO_DECL"]}` (was 32; +4 clock-vehicle checks) |
| `py -3.14 builds/backup/test_backup_mounts.py` | **31/31 OK** (no regression on F-48 adapters) |
| `py -3.14 builds/backup/test_offsite_clock.py` | **35/35 OK** (no regression on the R2 sibling) |
| live `--preflight` (creates nothing; no heartbeat written) | Artifact `builds/backup/_f48_clock_live.json`: **`status=BLOCKED`** `cli_rc=2` `config_present:false` `adapter_implemented:true`; gdx/odx/es3 all `NO_CONFIG`; scopes `NO_SCOPES`. `live/logs/mount_clock_heartbeat.json` **absent** |
| live `--plan-task` (registers nothing) | Artifact `builds/backup/_f48_clock_plan_task.json`: task `COSMOS Mount Offsite Push` `/sc daily` `/st 03:00` `/tn` this file `--once`, no `/rl highest` |
| live resession `--plan-task` | Artifact `builds/probe/_f51_plan_task.json`: task `COSMOS Resession` `/sc minute` `/mo 1` |

**Total for this pass: 4 suites green** (34 + 36 + 31 + 35 = **136** individual checks) **plus two deliberate FAIL/bite runs** (mount-clock ABSENT, old resession no `plan_task_argv`). No key material was read. No byte was pushed to Drive/OneDrive. `builds/cvm-dt/` was not touched.

### Tests run by the 11:30Z pass — 2026-08-31 (`cc` fence `cosmos/`, `tests/`)

| Command | Result |
|---|---|
| import `cosmos/cosmos_resession.py` before the file existed + staged CLOCKS | **BITE** `state=ABSENT` `kind=FileNotFoundError`; staged CLOCKS `count=17` `has_id_18:false` `max_id=17`. Artifact: `cosmos/_bite_f51_promote.json` `all_bite:true` |
| `py -3.14 tests/test_resession.py` | **PASS — 46/46**, `live_value {"checks": 46, "clock_id": 18, "heartbeat": "resession_heartbeat.json", "refusal_kinds": ["BAD_SEED","IDENTITY_MISMATCH","NO_DECL"], "scratch_state": "IDLE"}`. Artifact: `cosmos/_f51_promote.json` |
| `py -3.14 tests/test_own_clocks.py` | **PASS — 70/70** including `clock 18 is COSMOS Resession` and no `bts_` import in `cosmos_resession.py` |
| `py -3.14 cosmos/cosmos_resession.py --selftest` | **12/12** |
| live `--dry-run` (writes nothing) | Artifact `cosmos/_f51_live_dryrun.json`: `state=IDLE` `tree_id=KMesh-COSMOS-live` `clock_id=18` `prompt_sha=null` `why="no COW heartbeat"` |
| live `--plan-task` (registers nothing) | Artifact `cosmos/_f51_plan_task.json`: task `COSMOS Resession` `clock_id=18` `/sc minute` `/mo 1` `--once`, no `/rl` |
| `live/logs/resession_heartbeat.json` and `live/state/control/RESESSION.json` | **absent** after dry-run and plan-task |

**Total for this pass: 3 suites green** (46 + 70 + 12 = **128** individual checks) **plus one deliberate FAIL/bite** (module ABSENT + CLOCKS max 17). No key material was read. `--install-task` / `own_clocks --standup` were not run. `builds/cvm-dt/` was not touched.

### Tests run by the 11:28–11:30Z pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

| Command | Result |
|---|---|
| import `tool_disposition` before the file existed | **BITE** `state=ABSENT` `kind=ModuleNotFoundError`. Artifact: `builds/probe/_bite_tool_disposition_absent.json` |
| import `cosmos_state_offsite` before the file existed | **BITE** `state=ABSENT` `kind=ModuleNotFoundError`. Artifact: `builds/backup/_bite_state_offsite_absent.json` |
| `py -3.14 builds/probe/test_tool_disposition.py` | **PASS — 16/16**, `live_value {"checks": 16, "refusal_kinds": ["LIVE_LEDGER_FORBIDDEN","SUCCESSOR_ABSENT","DRIFT","UNPLANNED"]}` |
| `py -3.14 builds/backup/test_state_offsite.py` | **PASS — 17/17**, including `NO_OFFSITE_ROUTE` heartbeat and FakeProbe+MemoryTransport `readback_verified:4` |
| `py -3.14 builds/backup/test_offsite_clock.py` | **35/35 OK** (no regression on F-47) |
| `py -3.14 builds/backup/test_mount_clock.py` | **34/34 OK** (no regression on F-48) |
| live `tool_disposition.py --root …/live --write-md` (read-only Kernel) | Artifact `builds/probe/_f41_proposals.json`: **143 live · PLAN_READY 19 · DECLARE_READY 8 · PLAN_MATCH 7 · DRIFT 1 (`bts_cursor`) · UNPLANNED 116**. `writes: 0`. Generated `docs/TOOL_DISPOSITION.md` |
| live `--apply --ledger live/ledger/authority.jsonl` | **BITE** `kind=LIVE_LEDGER_FORBIDDEN` `ledger_untouched:true` `cli_rc=2`. Artifact: `builds/probe/_f41_live_apply_refused.json`. Ledger **548417 bytes, mtime_ns 1788175256990144200 — unchanged** |
| live `cosmos_state_offsite.py --preflight` (creates nothing) | Artifact `builds/backup/_f54_live_preflight.json`: **`status=BLOCKED` `kind=NO_OFFSITE_ROUTE` `cli_rc=2`**; payload **present 4 / 254853 bytes**; routes `NO_CONFIG` + `NO_CREDENTIALS`; `adapter_implemented.mount/r2: true`; `heartbeat_written: false`; `live/logs/state_offsite_heartbeat.json` **absent** |

**Total for this pass: 4 suites green** (16 + 17 + 35 + 34 = **102** individual checks) **plus three deliberate FAIL/bite runs** (two ABSENT imports, live-ledger APPLY). No key material was read, printed, or copied. No byte was pushed to Drive/OneDrive/R2. `builds/cvm-dt/` was not touched.

### Tests run by the 11:56–11:57Z pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

| Command | Result |
|---|---|
| staged-old `ADAPTERS["r2"]()` (`_delme/predispose_cosmos_backup_f47_r2adapter_20260831T065325Z/`) | **BITE** `NotImplementedError`, `has_do_rehearse_target:false`, `DEFAULT_EXCLUDES=[".git"]`. Artifact: `builds/backup/_bite_f47_r2_stub.json` `all_bite:true` |
| `py -3.14 builds/backup/test_cosmos_backup.py` | **22 OK, 1 skipped** (`COSMOS_TEST_DOCS`); `ADAPTERS["r2"]()` is `NO_CREDENTIALS`; `__pycache__` excluded |
| `py -3.14 builds/backup/test_cosmos_backup_r2.py` | **35/35 OK** (was 29; +factory, Gate B `do_rehearse_target` `files_restored:2` `kind=REHEARSAL_PASS`, staged-old bite) |
| `py -3.14 builds/backup/test_backup_mounts.py` | **31/31 OK** (r2 seam now `NO_CREDENTIALS`) |
| `py -3.14 builds/probe/test_tool_disposition.py` | **19/19**, `live_value {"checks": 19, "refusal_kinds": ["LIVE_LEDGER_FORBIDDEN","SUCCESSOR_ABSENT","DRIFT","UNPLANNED"]}` (was 16; +UNPLANNED cards HOLD, no invented disposition) |
| `py -3.14 builds/backup/test_offsite_clock.py` | **35/35 OK** (no regression) |
| `py -3.14 builds/backup/test_mount_clock.py` | **34/34 OK** (no regression) |
| `py -3.14 builds/backup/test_state_offsite.py` | **17/17 OK** (no regression) |
| live `ADAPTERS["r2"]()` (no file opened) | Artifact `builds/backup/_f47_live_adapter.json`: **`kind=NO_CREDENTIALS` `writes:0` `has_do_rehearse_target:true` `default_excludes=[".git","__pycache__"]`** |
| live `cosmos_offsite_clock.py --preflight` | Artifact `builds/backup/_f47_live_preflight.json`: **`cli_rc=2` `status=BLOCKED`** adapter `credential.state=NO_CREDENTIALS` `adapter_implemented:true`; scopes `NO_SCOPES`; `task_registered:false`. This pass did **not** write `live/logs/offsite_clock_heartbeat.json` (mtime still `2026-08-31T06:58:23Z`, a prior `--once` that itself REFUSED `NO_CREDENTIALS` `offsite_copy_exists:false`) |
| live `tool_disposition.py --root …/live --write-md --write-cards` | Artifact `builds/probe/_f41_unplanned_cards.json`: **`card_count:116` `with_candidates:47` `without_candidates:69`**; every card `disposition:null` `action:HOLD`. `writes:0`. Generated `docs/TOOL_DISPOSITION.md` |
| live `--apply --ledger live/ledger/authority.jsonl` | **BITE** `kind=LIVE_LEDGER_FORBIDDEN` `cli_rc=2` `ledger_untouched:true`. Artifact: `builds/probe/_f41_live_apply_refused.json`. Ledger **559724 bytes, mtime_ns unchanged** |

**Total for this pass: 7 suites green** (22 + 35 + 31 + 19 + 35 + 34 + 17 = **193** individual checks, plus 1 skip) **plus one deliberate FAIL/bite** (old R2 stub). No key material was read, printed, or copied. No byte was pushed to Drive/OneDrive/R2. `builds/cvm-dt/` was not touched.

### Tests run by the 12:05Z verification-hardening pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

In-fence infra rows were all DONE / parked / operator-blocked. This pass
pinned two prose claims (`SEAL_HMAC_MISMATCH`, `COPY_HASH_MISMATCH`) that
no `test_*.py` named.

| Command | Result |
|---|---|
| reconstructed sha256-only `check_seal` + unhashed `do_backup` + incumbent null HMAC | **BITE** `_bite_hmac_copyhash.json` `all_bite:true` — forged HMAC **passed**; null HMAC **TypeError**; corrupt copy **sealed MANIFEST** |
| `py -3.14 builds/backup/test_cosmos_backup.py` against unfixed `check_seal` | **33 OK, 1 ERROR, 1 skipped** — ERROR `test_null_hmac_is_typed_refusal_not_a_crash` TypeError (required before belief) |
| same, after coerce-to-refusal | **33 OK, 1 skipped** |
| `py -3.14 builds/backup/test_cosmos_backup_r2.py` | **35/35 OK** |
| `py -3.14 builds/backup/test_backup_mounts.py` | **31/31 OK** |
| `py -3.14 builds/backup/test_state_offsite.py` | **17/17 OK** |
| live `check_seal` | `_hmac_copyhash_live.json` `null_hmac_kind=SEAL_HMAC_MISMATCH` `null_hmac_crash=null` `forged_hmac_kind=SEAL_HMAC_MISMATCH` |

**Total for this pass: 4 suites green** (33 + 35 + 31 + 17 = **116** individual checks, plus 1 skip) **plus the bite** (reconstructed old `all_bite:true` and the one TypeError run). No key material was read. `builds/cvm-dt/` was not touched.

### Tests run by the 12:40Z pass — 2026-08-31 (`cc` fence `cosmos/`, `tests/`)

FOLLOW emit already landed; this pass corrected stale F-33/F-34/premise-4
and promoted F-27. `builds/cvm-dt/` was not touched.

| Command | Result |
|---|---|
| import `cosmos/cosmos_competency.py` before the file existed + staged WD2 | **BITE** `state=ABSENT` `kind=FileNotFoundError`; staged `pick_agent` has no `cosmos_competency`; live source same. Artifact: `cosmos/_bite_f27_competency.json` `all_bite:true` |
| `py -3.14 tests/test_competency.py` against unwired `pick_agent` | **FAIL — current 25/30** (5 TypeError `matrix=`). Prechange-lacks-consumer **4/4** (`old_web_research_is_G46`). Artifact: `cosmos/_bite_f27_pick_agent.json` |
| `py -3.14 tests/test_competency.py` after wiring | **PASS — current 31/31**; prechange-lacks-consumer **4/4**. Live `pick(web-research)=SGH` `pick(code-build)=G46` `pick_agent(web research scout)=SGH/grok`. Artifact: `cosmos/_f27_competency.json` `ok:true` |
| `py -3.14 tests/test_watchdog2.py` | **PASS — 43/43** |
| signed `GET /api/v1/status` `:8770` | **HTTP 200** `tree_id=KMesh-COSMOS-live` `ready=true` `seq=1270` (F-33) |
| unsigned `GET /api/v1/status` | **HTTP 401** `UNAUTHORIZED` |
| signed `GET /cdeck/` `/cdeck/cdeck.webmanifest` `/cdeck/sw.js` | all **HTTP 404 `NOT_FOUND`** (F-11 leftover) |
| `live/state/health/board.json` | `verdict=GREEN` `reds=[]` `serve_8770.ok=true` |
| `live/logs/health_clock_heartbeat.json` | `serve_supervisor.kind=ALREADY_UP` (F-34) |

**Total for this pass: 2 suites green** (31 + 43 = **74** individual checks) **plus two deliberate FAIL/bite runs** (module ABSENT; unwired pick_agent 25/30). No key material was read. `builds/cvm-dt/` was not touched.

### Tests run by the 12:18Z pass — 2026-08-31 (`cc` fence `cosmos/`, `tests/`)

FOLLOW emit was already landed; this pass promoted F-63. `builds/cvm-dt/` was not touched.

| Command | Result |
|---|---|
| import `cosmos/cosmos_askmine.py` before the file existed + staged CLOCKS + WD2 sources | **BITE** `state=ABSENT` `kind=FileNotFoundError`; staged CLOCKS `count=18` `has_id_19:false` `max_id=18`; WD2 sources `["wishlist","backlog"]`. Artifact: `cosmos/_bite_f63_promote.json` `all_bite:true` |
| `py -3.14 tests/test_askmine.py` | **PASS — 66/66** (34 detector + 7 clock; UNMEASURED FP still bites pre-fix source). Artifact: `cosmos/_f63_promote.json` |
| `py -3.14 tests/test_own_clocks.py` | **PASS — 74/74** including `clock 19 is COSMOS Askmine` and no `bts_` import in `cosmos_askmine.py` |
| `py -3.14 tests/test_watchdog2.py` | **PASS — 43/43** including `md_sources` wishlist+backlog+askmine and absent UNANSWERED.md contributing 0 items |
| `py -3.14 tests/test_follow_ids.py` | current **10/10**; prechange-lacks-keys **6/6**. FOLLOW emit still holds |
| live `--dry-run --scan-dir cosmos/` (writes nothing) | Artifact `cosmos/_f63_live_dryrun.json`: `state=REFUSED` `kind=NO_TRANSCRIPT` `clock_id=19` `cli_rc=2` |
| live `--plan-task` (registers nothing) | Artifact `cosmos/_f63_plan_task.json`: task `COSMOS Askmine` `clock_id=19` `/sc HOURLY` `--once`, no `/rl` |
| `live/logs/askmine_heartbeat.json` and `live/state/askmine/UNANSWERED.md` | **absent** after dry-run and plan-task |

**Total for this pass: 4 suites green** (66 + 74 + 43 + 10 = **193** individual checks) **plus one deliberate FAIL/bite** (module ABSENT + CLOCKS max 18 + WD2 two sources) **plus prechange-lacks-keys 6/6**. No key material was read. `--install-task` / `own_clocks --standup` were not run. `builds/cvm-dt/` was not touched.

### Tests run by the 12:28Z pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

F-40 leftover (hand regen of `REFUSAL_TAXONOMY.md`) plus F-63 live re-measure.
`builds/cvm-dt/` was not touched.

| Command | Result |
|---|---|
| import `regen_refusal_taxonomy` before the file existed | **BITE** `state=ABSENT` `kind=ModuleNotFoundError`. Artifact: `builds/probe/_bite_refusal_taxonomy_absent.json` |
| hermetic drifted fixture / skip-on-absent / cp437 redirect | **BITE** `_bite_refusal_taxonomy.json` `all_bite:true` — old `test_refusals` SKIP-on-absent would PASS; `--diff` on drift **exits 2** and names `py -3.14 cosmos\cosmos_refusals.py --out docs\REFUSAL_TAXONOMY.md`; cp437 redirect ≠ UTF-8 `--out` |
| `py -3.14 builds/probe/test_refusal_taxonomy.py` | **PASS — 26/26**, `live_value {"checks":26,"kind":"MATCH","typed_refusal_classes":49,"distinct_kinds":128,"render_chars":17918,"healed":false,"cp437_would_drift":true,"command":"py -3.14 cosmos\\cosmos_refusals.py --out docs\\REFUSAL_TAXONOMY.md"}`. Artifact: `builds/probe/_refusal_taxonomy_tick.json` |
| `py -3.14 tests/test_refusals.py` | **PASS — 14/14 + 1/1 projection**, `render_chars=17918` `kinds=128` (not weakened, not skipped) |
| `py -3.14 builds/probe/regen_refusal_taxonomy.py --diff` | **OK** `kind=MATCH` `cli_rc=0` |
| `py -3.14 tests/test_own_clocks.py` | **PASS — 74/74** including `clock 19 is COSMOS Askmine` |
| `py -3.14 tests/test_askmine.py` | **PASS — 66/66** |
| live `cosmos_askmine.py --root …/live --once --dry-run` (default scan dirs; writes nothing) | Artifact `builds/probe/_f63_live_dryrun.json`: **`state=MINED` `ok:true` `dry_run:true` `clock_id=19` `transcripts_seen=2555` `asks=1788` `findings=252` `outstanding=252` `elapsed_s=26.953`**. `live/logs/askmine_heartbeat.json` **absent** |
| live `--plan-task` (registers nothing) | Artifact `builds/probe/_f63_plan_task.json`: task `COSMOS Askmine` `clock_id=19` `/sc HOURLY` `/f` `--once`, no `/rl`, `registers:false` |

**Total for this pass: 4 suites green** (26 + 14+1 + 74 + 66 = **181** individual checks) **plus two deliberate FAIL/bites** (module ABSENT; drifted fixture `--diff` rc=2 + skip-would-pass + cp437). No key material was read. `--install-task` was not run. `builds/cvm-dt/` was not touched.

### Tests run by the 12:34Z verification-hardening pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

In-fence infra rows were all DONE / parked / operator-blocked. This pass
pinned restore fail-closed kinds that sat in the kind set and in prose.
`builds/cvm-dt/` was not touched. `cosmos_backup.py` was **not** edited
(the refusals already existed; they were unpinned).

| Command | Result |
|---|---|
| `py -3.14 builds/backup/_bite_stage_restore.py` | **BITE** `_bite_stage_restore.json` `all_bite:true` — occupied stage clobbered + dest restored + `RESTORE_OK`; flipped retrieve sealed `RESTORE_OK` / `REHEARSAL_PASS`; file-as-source `SOURCE_UNREADABLE`; empty set `FileNotFoundError` |
| `py -3.14 builds/backup/_fail_stage_restore_against_old.py` | **5/5 FAIL** against stripped predecessor (`STAGE_OCCUPIED` not raised; restore/rehearse re-hash not raised; `SOURCE_UNREADABLE` ≠ `SOURCE_NOT_DIR`; `BackupRefusal` not raised for empty set). Artifact: `_fail_stage_restore_against_old.json` `all_new_pins_failed:true` |
| `py -3.14 builds/backup/test_cosmos_backup.py` | **PASS — 39 OK, 1 skipped** (`COSMOS_TEST_DOCS`). Was 33+1; **+6** (`TestRestoreFailClosed`) |
| `py -3.14 builds/backup/_emit_stage_restore_live.py` | `_stage_restore_live.json` `ok:true` kinds `STAGE_OCCUPIED` / `RESTORE_HASH_MISMATCH` / `REHEARSAL_HASH_MISMATCH` / `SOURCE_NOT_DIR` / `NOT_A_BACKUP_SET`; `stage_untouched:true` `dest_untouched:true` |
| `py -3.14 builds/backup/test_backup_mounts.py` | **31/31 OK** (no regression) |
| `py -3.14 builds/backup/test_longpath.py` | **9 OK, 1 skipped** (POSIX identity; no regression) |

**Total for this pass: 3 suites green** (39 + 31 + 9 = **79** individual checks) **plus two deliberate FAIL/bites** (reconstructed pre-fix `all_bite:true`; 5/5 new pins FAIL against predecessor). No key material was read. `--install-task` was not run. `builds/cvm-dt/` was not touched.

### Tests run by the 12:46Z F-43 leftover close — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

F-43 gap 3 (torn snapshot sealed VERIFIED) and gap 5 (no retention).
Operator-blocked dests/credentials/`schtasks` were **not** re-attempted.
`builds/cvm-dt/` was not touched.

| Command | Result |
|---|---|
| `py -3.14 builds/backup/_bite_f43_mutate_retire.py` against incumbent | **BITE** `_bite_f43_mutate_retire.json` `all_bite:true` — mutated `a.txt` after store sealed `BACKUP_OK` / `MANIFEST`; `has_do_retire:false`; no `SOURCE_MUTATED` |
| `py -3.14 builds/backup/_fail_f43_against_old.py` | **10/10 FAIL** against `_delme/predispose_cosmos_backup_f43_20260831T124639Z/` (`all_new_pins_failed:true`) |
| `py -3.14 builds/backup/test_cosmos_backup.py` | **PASS — 51 OK, 1 skipped** (`COSMOS_TEST_DOCS`). Was 39+1; **+12** (`TestQuiescence` + `TestRetire`) |
| `py -3.14 builds/backup/_emit_f43_live.py` | `_f43_mutate_retire_live.json` `ok:true` `mutated_kind=SOURCE_MUTATED` `manifest_sealed:false` `retire_kind=RETIRE_OK` `never_deleted:true` `staged_verifies:true` `keep_zero_kind=KEEP_TOO_SMALL` |
| `py -3.14 builds/backup/test_backup_mounts.py` | **31/31 OK** (no regression) |
| `py -3.14 builds/backup/test_longpath.py` | **9 OK, 1 skipped** (POSIX identity; no regression) |

**Total for this pass: 3 suites green** (51 + 31 + 9 = **91** individual checks) **plus two deliberate FAIL/bites** (incumbent torn-snapshot `all_bite:true`; 10/10 new pins FAIL against predecessor). No key material was read. `--install-task` was not run. `builds/cvm-dt/` was not touched.

### Tests run by the 12:48Z pass — 2026-08-31 (`cc` fence `cosmos/`, `tests/`)

F-55 mailbox channel (hash-chain + writer HMAC + cosmos_lock).
`builds/cvm-dt/` was not touched.

| Command | Result |
|---|---|
| `py -3.14 cosmos/_bite_f55_mail.py` against pre-change `cosmos_mail.py` | **BITE** `_bite_f55_mail.json` `all_bite:true` — no `prev_hash`/`writer_sig`, `Mailbox()` rejects `arbiter=`, planted lie unread, kernel unwired |
| `py -3.14 tests/test_cosmos_mail.py` against pre-change module | **FAIL** `ImportError: cannot import name 'GENESIS_HASH'` |
| `py -3.14 cosmos/_fail_f55_against_old.py` | **8/8 FAIL** against `_delme/predispose_cosmos_mail_f55_20260831T124826Z/` (`all_new_pins_failed:true`) |
| `py -3.14 tests/test_cosmos_mail.py` after the fix | **PASS — 23/23**, `live_value {"checks":23,"passed":23,"fenced_events":["GRANT","COMMIT_RESERVED","COMMIT","RELEASE"],"genesis":"0"*64}`. Artifact `cosmos/_f55_mail_suite.json` |
| `py -3.14 tests/test_kernel.py` | **PASS — 18/18** including `k.mail.arbiter is k.arbiter`, COMMIT `mail:critic`, signed genesis note |
| `py -3.14 tests/test_rest_guards.py` | **PASS — 26/26** (read-only mail unread still 0, writer still registers) |
| `py -3.14 tests/test_refusals.py` after `--out docs/REFUSAL_TAXONOMY.md` | **14/14 + 1/1 projection**, `render_chars=18235` `kinds=134` `MailError` raises `CHAIN_BREAK`×1 `FORGED_MESSAGE`×1 |
| post-fix `cosmos/_bite_f55_mail.py --out cosmos/_f55_mail.json` | `all_bite:false` every claim true, `kernel_wires_arbiter:true` |

**Total for this pass: 4 suites green** (23 + 18 + 26 + 15 = **82** individual checks) **plus two deliberate FAIL/bites** (pre-change `all_bite:true` + ImportError; 8/8 pins FAIL on predecessor). No key material was read. `--install-task` was not run. `builds/cvm-dt/` was not touched.

### Tests run by the 13:22Z pass — 2026-08-31 (`cc` fence `cosmos/`, `tests/`)

FOLLOW leftover (HEALTH_BOARD.node) + stale F-24/F-66/F-69 rows.
`builds/cvm-dt/` was not touched.

| Command | Result |
|---|---|
| live ledger FOLLOW_KEYS census | `cosmos/_follow_live_measure.json` n=1295 `head_seq=1295` `tail_with_any=9/100` `tail_missing {HEALTH_BOARD:90, BACKUP_VERIFIED:1}` `newest_event=HEALTH_BOARD` `newest_follow_keys=[]` |
| `py -3.14 tests/test_follow_ids.py` against old `cosmos_health.py` | **FAIL current 10/11** `health_board_node_equals_system` payload `{control_red,reds,verdict}` no `node`; prechange-lacks-keys **7/7** |
| `py -3.14 tests/test_migrate_health.py` against old writer | **FAIL** `HEALTH_BOARD carries node=system` |
| `py -3.14 tests/test_command.py` against old writer | **FAIL** `HEALTH_BOARD.node is sentinel.system` |
| `py -3.14 cosmos/_fail_follow_health_against_old.py` | **BITE** `all_new_pins_failed:true` `old_node=null` `pin_passed_on_old=false` |
| `py -3.14 tests/test_follow_ids.py` after the stamp | **PASS — current 11/11**; prechange-lacks-keys **7/7**. Emitted `node=COSMOS`. Artifact `cosmos/_follow_ids_prove.json` |
| `py -3.14 tests/test_migrate_health.py` after | **PASS — 13/13** |
| `py -3.14 tests/test_command.py` after | **PASS — 52/52** |
| hermetic HealthBoard.run() | Artifact `cosmos/_f_health_follow.json` `ok:true` `payload.node=COSMOS` `verdict=GREEN` `seq=17` |
| `py -3.14 tests/test_grok_gem_bucket_workers.py` (F-66) | **PASS — 58/58**; GDX without config `NO_DEST`; configured ODX under `COSMOS/returns/gem` |
| `py -3.14 tests/test_collector.py` (F-69) | **PASS — 71/71** including H1/H2/H3/H4 |

**Total for this pass: 5 suites green after the stamp** (11+7 + 13 + 52 + 58 + 71 = **212** individual checks) **plus three deliberate FAIL/bites** (follow 10/11, migrate pin, command pin; fail-old `all_new_pins_failed:true`). No key material was read. Core was not restarted. `builds/cvm-dt/` was not touched.

### Tests run by the 13:53Z pass — 2026-08-31 (`cc` fence `cosmos/`, `tools/`, `tests/`)

FOLLOW leftover (BACKUP_VERIFIED.node + COMMAND_HANDLED.node=CVM).
`builds/cvm-dt/` was not touched. Core was not restarted. F-41 live
ledger apply was not run.

| Command | Result |
|---|---|
| live ledger FOLLOW_KEYS census (before) | `_follow_live_measure.json` (13:22Z) n=1295 `tail_with_any=9/100` `tail_missing {HEALTH_BOARD:90, BACKUP_VERIFIED:1}` |
| `py -3.14 tests/test_follow_ids.py` against old writers | **FAIL current 11/17** — 6 new pins: `command_handled_node_is_cvm` payload `{ok,text}`; `command_refused_node_is_cvm`; `backup_verified_node` TypeError `node=`; clock/cli source kwargs absent. prechange-lacks-keys **11/11** |
| `py -3.14 tests/test_command.py` against old writer | **FAIL 2/54** `COMMAND_HANDLED.node is CVM`; `COMMAND_REFUSED.node is CVM` |
| `py -3.14 cosmos/_fail_follow_backup_command_against_old.py` | **BITE** `all_new_pins_failed:true` **5/5** `old_backup_node=null` `old_command_node=null` `old_clock_backup_nodes=[null]` |
| `py -3.14 tests/test_follow_ids.py` after the stamp | **PASS — current 17/17**; prechange-lacks-keys **11/11**. Emitted `command.node=CVM` `backup.node=COSMOS`. Artifact `cosmos/_follow_ids_prove.json` |
| `py -3.14 tests/test_command.py` after | **PASS — 54/54** |
| `py -3.14 tests/test_backup_clock.py` after | **PASS — 14/14** `whole_scope_state=VERIFIED` `whole_scope_files=7` `whole_scope_node=COSMOS`. Artifact `cosmos/_f_snapshot_incomplete.json` |
| hermetic emit | `cosmos/_f_backup_command_follow.json` `ok:true` `command.node=CVM` `backup.node=COSMOS` `files=1` `clock_source_has_node:true` `cli_source_has_node:true` |
| live ledger FOLLOW_KEYS census (after, Core not reloaded) | `_follow_live_measure.json` n=1334 `head_seq=1334` `tail_with_any=16/100` `tail_missing {HEALTH_BOARD:84}` `newest_event=HEALTH_BOARD` `newest_follow_keys=[]` |

**Total for this pass: 3 suites green after the stamp** (17+11 + 54 + 14 = **96** individual checks) **plus three deliberate FAIL/bites** (follow 11/17, command 2/54, fail-old 5/5). No test was skipped, suppressed, or deleted. No key material was read. Core was not restarted. `builds/cvm-dt/` was not touched.

### Tests run by the 13:54Z pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

F-51 P1.3 prompt leftover closed (fence artifact). Then unexercised-refusal pins.
Operator leftovers were not chased. F-41 `--apply` on the live authority ledger was not run.
`builds/cvm-dt/` was not touched.

| Command | Result |
|---|---|
| `py -3.14 builds/probe/_bite_f51_prompt.py` | **BITE** `all_bite:true` `prompt_exists:false` `dry_run_prompt_sha:null` fire `NO_PROMPT` |
| `py -3.14 builds/probe/test_resession.py` before filing | **FAIL 39/42** — 3 new P1.3 pins FAIL (`_fail_f51_prompt_against_old.json` `all_new_pins_failed:true`) |
| `py -3.14 builds/probe/_emit_f51_prompt_live.py` after P1.3 | `ok:true` `prompt_sha=5d10d8ff510503a00b01d6a2b1efca7941ca92a10efc3aa1c6ed59082cfca8db` `state=IDLE` `tree_id=KMesh-COSMOS-live` `writes:0` (`_f51_prompt_live.json`) |
| `py -3.14 builds/backup/_bite_unpinned_round3.py` | **BITE** `all_bite:true` `pack_dest_file_crash=FileExistsError` `keep_true_is_int:true` `keep_true_kind=KEEP_TOO_SMALL` |
| `py -3.14 builds/probe/_bite_unpinned_round3.py` | **BITE** `all_bite:true` `resumed_tidy_class=HOLD` `tidyup_hold_class=ARM` |
| `py -3.14 builds/backup/_fail_unpinned_round3_against_old.py` | **4/4 FAIL** `all_new_pins_failed:true` (bool keep did_not_raise; pack FileExistsError; volume_serial BAD_CONFIG; FakeProbe `vol:DISCOVERED`) |
| `py -3.14 builds/probe/_fail_unpinned_round3_against_old.py` | **1/1 FAIL** `all_new_pins_failed:true` `stripped_class=ARM` |
| `py -3.14 builds/backup/test_cosmos_backup.py` | **PASS 59/60** (1 skip `COSMOS_TEST_DOCS`, pre-existing) |
| `py -3.14 builds/backup/test_backup_mounts.py` | **PASS 35/35** |
| `py -3.14 builds/backup/test_state_offsite.py` | **PASS 18/18** `DEST_NOT_DIR` |
| `py -3.14 builds/probe/test_resession.py` after | **PASS 45/45** |

**Total for this pass: 4 suites green** (59 + 35 + 18 + 45 = **157** individual checks, + 1 pre-existing skip) **plus six deliberate FAIL/bites** (F-51 absent, F-51 39/42, two round-3 bites, 4/4 + 1/1 fail-old). No test was skipped, suppressed, or deleted to go green. No key material was read, printed, or copied. `--install-task` was not run. `builds/cvm-dt/` was not touched.

### Tests run by the 13:26Z claim-artifact freshness pass — 2026-08-31 (`cc-infra`, fence `builds/backup/`, `builds/probe/`, `docs/`)

Operator-blocked leftovers were not chased. This pass closed the
cDeck-class hole: claim-backing JSON had no fingerprint of the source
it described, so F-43's 12:49Z edit of `cosmos_backup.py` left
FEATURE_MASTER citing a 07:27Z longpath artefact.

| Command | Result |
|---|---|
| `py -3.14 builds/probe/_bite_artifact_freshness.py` | **BITE** `all_bite:true` — dated longpath `UNFINGERPRINTED`; hmac names `cosmos_backup.py` but does not hash it; source **12:49:31Z** newer than artefact **07:27:06Z**; planted wrong sha `STALE`; planted match `MATCH` |
| `py -3.14 builds/probe/test_artifact_freshness.py` against unfingerprinted artefacts | **FAIL 17/28** — 10 live rows `UNFINGERPRINTED` (required before belief) |
| `py -3.14 builds/probe/_fail_freshness_against_old.py` | **10/10 UNFINGERPRINTED** `all_new_pins_failed:true` on `_delme/predispose_claim_artifacts_20260831T133500Z/` |
| longpath `behave` re-measure | `_longpath_behaviour.json` `measured_utc=2026-08-31T13:26:12Z` all three walkers `COVERS_LONG_PATHS`; `describes` `cosmos_backup.py` 38376 `df66be47…` |
| `py -3.14 builds/probe/test_artifact_freshness.py` after stamp | **PASS 30/30** `live_checked:10` `live_matched:10` |
| `py -3.14 builds/backup/test_state_offsite.py` | **17/17** |
| `py -3.14 builds/probe/test_longpath_census.py` | **6/6** |
| `py -3.14 builds/probe/test_mesh_blockers.py` | **31/31** |
| `py -3.14 builds/probe/test_tools_surface.py` | **18/18** hermetic |
| live `--apply --ledger authority.jsonl` | **BITE** `LIVE_LEDGER_FORBIDDEN` ledger **607100** untouched (`_f41_live_apply_refused.json`) |
| live `--preflight` F-54 | `NO_OFFSITE_ROUTE` `payload.present=4` `bytes=293610` (`_f54_live_preflight.json`) |
| live `ADAPTERS["r2"]()` | `NO_CREDENTIALS` `writes:0` (`_f47_live_adapter.json`) |
| live mcp_docs `--live` | `openai-docs-mcp` / `xai-docs-mcp` http=200 (`_tools_surface_live.json`) |

**Total for this pass: 5 suites green** (30 + 17 + 6 + 31 + 18 = **102** individual checks) **plus two deliberate FAIL/bites** (pre-stamp 17/28; 10/10 UNFINGERPRINTED on staged incumbents). No key material was read. `--install-task` was not run. `builds/cvm-dt/` was not touched.

### Tests run by the F-13 re-measure + F-14 refresh — 2026-08-31 06:17 −05:00 (`cc-cdeck`, fence `builds/cdeck/`)

`builds/cvm-dt/` was not touched. Bearer signed probes; never printed.

| Command | Result |
|---|---|
| signed `GET /api/v1/status` `:8770` | **HTTP 200** `tree_id=KMesh-COSMOS-live` `ready=true` `ledger_head.seq=1162` (`CORE_CDECK_PROBE.json`) |
| unsigned `GET /api/v1/status` | **HTTP 401** `UNAUTHORIZED` |
| unsigned `GET /cdeck/` `/cdeck/cdeck.webmanifest` `/cdeck/sw.js` | all **HTTP 401** `UNAUTHORIZED` (un-reloaded process auth gate) |
| signed `GET /cdeck/` `/cdeck/cdeck.webmanifest` `/cdeck/sw.js` | all **HTTP 404** `NOT_FOUND` (`served_at` 1788174995.0375855) |
| `py -3.14 builds/cdeck/pwa_probe.py --label VERIFY-2026-08-31T0617` | Chrome `errors=[]`; cache **`cdeck-shell-v3`** 5 files; **28** `/api` in 12.0s **0 cached**; offline `refused=True` panels **19** cssRules **264** → `SERVER DOWN`. Artifact: `PWA_PROBE.json` |
| `py -3.14 builds/cdeck/stage6_gate.py gate --live-root V:/A/Ai/COSMOS/live` | **`ok: true`** `emitted cdeck:KMesh-COSMOS-live:1166:1788175256.923605:b1f86359…f4706` |
| `py -3.14 builds/cdeck/test_stage6_fresh.py` against the pre-bind gate | **10/29** — 19 of 29 FAIL (PWA files unbound; `app.js` hash 177474 ≠ 178709) |
| `py -3.14 builds/cdeck/test_stage6_fresh.py` | **PASS — 29/29** |
| `py -3.14 builds/cdeck/test_pwa.py --against …/predispose_kdeck_pwa_2026-08-31T0630/ui` | **3/40** — 37 FAIL on the pre-PWA deck |
| `py -3.14 builds/cdeck/test_pwa.py` | **PASS — 65/65** |
| `py -3.14 builds/cdeck/test_probe_upstream.py` | **PASS — 28/28** |

**Total for this pass: 3 suites green** (29 + 65 + 28 = **122** individual checks) **plus two deliberate FAIL/bite runs** (F-14 pre-bind 10/29, F-13 pre-PWA 3/40). No key material was read.

**Total for the authoring pass: 8 suites run, 8 passed** (27 + 40 + 52 + 49 + 29 + 32 + 5 + 9 = **243**
individual checks) plus one read-only measurement. The whole-tree gate was **not** run by me — the scheduled clock runs it every 15
minutes and its own fresh artifact is stronger evidence than a hand-run:
`live/logs/selftest_clock_heartbeat.json` at `2026-08-31T00:57:05-05:00` →
`total 100 · passed 100 · flaky 0 · failed 0 · elapsed_s 203.2`.

---

## 1. The master table

Fence column = the directory that owns the work, per the lane fences recorded in
`docs/CHANGELOG_2026-08-30_CC_AUDIT.md` (§ *Parallel lanes*).

### 1.1 cDeck — `builds/cdeck/` (lane `cc-cdeck`)

| # | Feature | Source | Status | Evidence (symbol / artifact) | Value | Effort |
|---|---|---|---|---|---|---|
| F-01 | cDeck as a KDash superset, every panel backed by a real endpoint | `WISHLIST.md:29`, `:81`, `:99`; `builds/cdeck/FEATURES_KEITH.md:23` | **DONE** | `PARITY_PROBE_LOCAL.json` **19/19** `verdict=RENDERS` `base=http://127.0.0.1:8770`. Fresh layout (ui/ 181620): `MOBILE_PROBE.json` `label=AFTER-REMEASURE-2026-08-31T0822` `tree_id=KMesh-COSMOS-live` `panelsMeasured=19` 320 `chromeVhPct=65.4` `pageOverflowPx=0` `silentClipCount=0`. `test_cdeck_parity.py` is in the gate | High | — |
| F-02 | Spend control — per-rail caps, thresholds, headroom, **view + local overlay** | `FEATURES_KEITH.md:15`; `WISHLIST.md:29` | **DONE** | `builds/cdeck/cosmos_spend_panel.py`; `test_spend_panel.py` **51/51 run this pass**, incl. *"headroom is read from the gate, never recomputed"* and the two WIDEN pins | High | — |
| F-03 | Spend **set/adjust against live Core** (`POST /api/v1/spend`) | `FEATURES_KEITH.md:16,35` (*"the ability to set/adjust them, not just view"*) | **DONE** | `cosmos/cosmos_spend_admin.py` + the dispatch in `cosmos/cosmos_service.py` `do_POST`. Sets a **rail cap** (`{rail, cap_usd, expires_epoch?}` → `BUDGET_SET`) or the **breaker thresholds** (`{thresholds:{session_usd, day_usd, rate_per_min, opus_turns_per_session}}` → live `spendguard_config.json`). **Never a silent widen:** more room to spend is `409 WIDEN_REQUIRES_CONFIRM` without a literal `"allow_widen": true` (a truthy *string* is `400 BAD_FIELD`). **PROVEN ON THE LIVE CORE :8770** (`cosmos/_f03_prove_live.json`): `409 WIDEN_REQUIRES_CONFIRM` → cap absent from `GET /spend` → confirmed `200` → **authority ledger seq 1030 `SPEND_CAP_REFUSED`, 1031 `BUDGET_SET`** `{"actor":"bearer:2c95dc38885441f5","rail":"f03-probe","prev_cap_usd":null,"cap_usd":0.25,"direction":"create","confirmed_widen":true,"source":"POST /api/v1/spend"}`, 1032 narrow-back to `0.0`. `cosmos/test_spend_admin.py` **59/59 run**; the pre-change module answers `404 NOT_FOUND` and writes nothing (`cosmos/_f03_old_code_probe.py`). **GATED 2026-08-31** in the `tests/` suite that should have shipped with the route: `tests/test_spend_post.py` **5/5 PASS** on current (`cosmos/_f03_test_spend_post.json`). Named checks: no bearer → `401 UNAUTHORIZED`; malformed body → `400 BAD_REQUEST`; unknown field → `400 BAD_FIELD`; confirmed create ledgers `BUDGET_SET` `{actor, rail, prev_cap_usd, cap_usd, direction, source}` with no token material; unconfirmed create/raise is `409 WIDEN_REQUIRES_CONFIRM` and the cap does not move (a truthy `"false"` string is `400 BAD_FIELD`). **Bite, before belief:** the discriminating four FAIL as `404 NOT_FOUND` against `_delme/predispose_f03_prechange_20260831T053952/cosmos_service.py` (POST `/spend` block removed) and the historical `_delme/predispose_cosmos_service_20260831_022243/` (1/5 only — the 401 is the global POST gate, recorded, not used as bite) | High | — |
| F-04 | Jukebox (job/queue control surface) | `WISHLIST.md:29`; `FEATURES_KEITH.md:18` | **DONE** | `builds/cdeck/cosmos_jukebox_panel.py`; `test_jukebox_panel.py` **40/40 run by me**. `PARITY_AUDIT.md:166` — measured 351 real jobs on the live queue with Core down (343 CLEAN / 4 BROKE / 3 FINDINGS / 1 RUNNING) | High | — |
| F-05 | Node map with **draggable** nodes | `WISHLIST.md:29`; `FEATURES_KEITH.md:19` | **DONE** | Viewport-keyed drag on every width. `mapIsDraggable()` returns true; `nmapPosStore()` writes `cdeck.nodePositions.phone` on ≤640px and never the desktop key. Fresh `MOBILE_PROBE.json` `label=AFTER-F05-2026-08-31T1625Z` `tree_id=KMesh-COSMOS-live` `probed_at_epoch 1788193556.8032436` 320: `firstNodePosition=absolute` `firstNodeCursor=grab` `phoneWrote:true` `desktopUnchanged:true` `phoneKeys=["COSMOS"]` `desktopKeys=[]` `nodes=31` `nodesOutsideStage=0` `edgesDisplay=block` `resetDisplay=block`. `app.js` 184893 sha256 `7b47ec6d…adf6442` MATCH STAGE6. Bite `test_mobile_layout.py --against …T1615Z/ui` **30/38**, **8 of 8 new pins FAIL**. Shipped `test_mobile_layout.py` **115/115**, `test_nodemap_panel.py` **55/55**. List-mode is gone | Med | — |
| F-06 | Live append-only status feed (never refetch old) | `FEATURES_KEITH.md:20` | **DONE** | Panel 8 `LIVE EVENTS`, `GET /events?since_seq=N`, `PARITY_AUDIT.md:163`. Producer alive: `live/logs/cdeck_feed_heartbeat.json`, 0.75s cadence, fresh at `2026-08-31T00:56` | Med | — |
| F-07 | Batteries — per-node quota/health indicators | `FEATURES_KEITH.md:21` | **DONE** | Panel 13, `PARITY_AUDIT.md:169`. The three **invented** readings (100/40/8 from a status dot) were removed; an unmeasured node now paints UNMEASURED. Real host series from `state/drive/meter.json` (4 volumes) | Med | — |
| F-08 | Caps & speeds, measured per node and channel | `FEATURES_KEITH.md:22` | **DONE** | Panel 14, `PARITY_AUDIT.md:170`; the per-poll row leak (`?since_seq=N` in the speed key) is fixed | Med | — |
| F-09 | Integrated CVM control from inside cDeck | `WISHLIST.md:30`; `FEATURES_KEITH.md:26` | **PARTIAL** | Kill/mute/resume + confirm lane + **start/stop listen** (`ui/app.js` `bindMic` `listening`, `#btnCvmMic`) ship. Remaining named gap is device-select and felt latency — those are CVM-DT (`BENCH_LATENCY.json`, F-15), outside this fence. `PARITY_AUDIT.md:171` still holds for `GET /control` `effective` of exactly 3 keys | Med | — (leftover is `builds/cvm-dt/`) |
| F-10 | The CREATE box (Agent/Tool/Connector/Skill) | `WISHLIST.md:30`; `FEATURES_KEITH.md:12` | **DONE** | Panel 7 files a real queue drop and a real registry write; both target routes exist — `cosmos_service.py:1276` `POST /api/v1/jobs`, `:1286` `POST /api/v1/makers`. `builds/cdeck/test_create_panel.py` in the gate | High | — |
| F-11 | cDeck usable in a **browser** against live Core | `builds/cdeck/README.md:27`; `PARITY_AUDIT.md:233` (K-2) | **DONE** | Live Core `:8770` serves `builds/cdeck/ui/` same-origin. Fresh `CORE_CDECK_PROBE.json` `label=AFTER-F11-2026-08-31T1725Z` `ok:true` `tree_id=KMesh-COSMOS-live` seq **1547** `served_at` 1788197359.008386: unsigned `/cdeck` **302** `/cdeck/`; unsigned AND signed `/cdeck/` `/cdeck/index.html` `/cdeck/app.js` `/cdeck/app.css` `/cdeck/cdeck.webmanifest` `/cdeck/sw.js` **HTTP 200** `match_disk:true` (23340 / 184893 / 31532 / 3436 / 7410; sha256 `7fcc254d…` / `7b47ec6d…` / `6b2a8650…` / `685e4ca3…` / `58da48b7…`). Unsigned `/api/v1/status` still **401 UNAUTHORIZED**. Unknown `/cdeck/nope` and traversal `/cdeck/../cosmos/cosmos_service.py` **401**, not a file. No `Access-Control-Allow-Origin`. Bite `_fail_f11_against_old.json` **15/15 FAIL** `all_new_pins_failed:true` `control_still_green:true` on seq-1444 404 incumbent (`_delme/predispose_f11_core_probe_20260831T172555Z/`). `test_core_cdeck.py` **25/25**. `remeasure_probes.py --check` `stale: []`. The 404 cell described the un-reloaded process, not the executing one | Med | — |
| F-12 | cDeck usable on a phone | `WISHLIST.md:97`; `PARITY_AUDIT.md:236` (K-5) | **DONE** | `MOBILE_PROBE.json` `label=AFTER-REMEASURE-2026-08-31T0822` `tree_id=KMesh-COSMOS-live` `app.js` 181620. 320: `chromeVhPct=65.4` `pageOverflowPx=0` `silentClipCount=0` `smallTouchCount=0` `smallFontCount=0` `effectiveScale=1`. `test_mobile_layout.py` **107/107** (eighth-pass chrome). Status unchanged; evidence is the remeasured artifact | Med | — |
| F-13 | cDeck PWA (service worker + webmanifest) | `PARITY_AUDIT.md:237` (K-6) | **DONE — RE-MEASURED (artifact current 2026-08-31T08:22)** | Status unchanged (still DONE); the *evidence* moved off the v3 VERIFY run. `PWA_PROBE.json` (ui/ 181620 / sw.js 7410): Chrome `errors=[]`, `display=standalone`, cache **`cdeck-shell-v5`** 5 shell entries `cached_api_entries: []`, **28** `/api` in 12.0s to the network. Offline: `refused=True` panels **19** `cssRules` **264** → `SERVER DOWN`, chip `PWA: offline shell ready · 5 files`. `test_pwa.py` **67/67** run this pass. **Install origin bound** (F-11 2026-08-31T17:25Z): `CORE_CDECK_PROBE.json` unsigned AND signed `/cdeck/` **HTTP 200** `match_disk:true` seq **1547** | Low | — |
| F-14 | cDeck stage-6 runtime-binding gate is **current** | `FEATURES_KEITH.md:37` | **DONE — RE-GATED 2026-08-31T12:45Z** | `builds/cdeck/STAGE6_GATE.json` `ok: true`, `gated_at_epoch 1788180225.940071`, `headline LIVE`, **`emitted cdeck:KMesh-COSMOS-live:1272:1788180225.3626423:b1f86359a1910792ac3a3408a07d68beeba4f6b33c233c27b5f49b0c161f4706`**. Live files match: `app.js` 181620 `390aac19…a1cae30b`; `index.html` 23455 `7b7e4c33…bc9273a26`; `sw.js` 7410 `58da48b7…ba840cd4` (`cdeck-shell-v5`); `cdeck.webmanifest` 3436 `685e4ca3…a2ebcd311`; `app.css` 31340 `62dff4b9…922816d4`. Bearer record `{present:true, bytes:32, value_emitted:false}` | High | — |

### 1.2 CVM (voice) — `builds/cvm-dt/`, `builds/cvm-phone/` (lane `cc-cvm`)

| # | Feature | Source | Status | Evidence | Value | Effort |
|---|---|---|---|---|---|---|
| F-15 | **CVM usability — Keith's stated #1 priority** | `WISHLIST.md:15-23` | **PARTIAL** | Real numbers exist for the first time: `builds/cvm-dt/BENCH_LATENCY.json` (`schema cvm-dt-bench/1`, before/after runs, per-stage ms). But two stages are **UNMEASURED by their own artifact**: `respond.voice_post` (Core `:8770` refuses, `connect_ex=10035`) and `transcribe.stt_model_inference`. F-21 now binds vosk in `cosmos/` (`cosmos/_f21_stt_probe.json` `ok:true`); **this fence did not write** `builds/cvm-dt/BENCH_LATENCY.json`, which still records that stage `UNMEASURED` (mtime 2026-08-31 02:34, predates F21_STT_LOCAL.json). The usability claim cannot close while the bench file is UNMEASURED | **Highest** | M |
| F-16 | Desktop (DT) CVM on the same headphones | `WISHLIST.md:21-23` | **DONE (gated) / executing hash lags piper** | `STAGE6_SPLIT.json` `ok:true` `local.verdict=PASS` counts `{PASS:11, PENDING_CORE:0, FAIL:0}` emitted `cvm-dt-local:KMesh-COSMOS-live:Speakers (High Definition Audio Device):48000x2x32f:…`; `core.verdict=PASS` counts `{PASS:4, PENDING_CORE:0}` `core_reachable:true` `live_tree_id=KMesh-COSMOS-live`. Was PARTIAL/`PENDING_CORE` — the Core half is no longer pending. ⚠ live `cvm_dt.py` **57611** sha256 `084157e3…` ≠ gated `57146`/`f9a3892d…`; another session is editing piper under `builds/cvm-dt/` (this fence does not touch it) | **Highest** | — |
| F-17 | CVM DT stage-6 gate overall | `WISHLIST.md:36` | **DONE (gated) / source hash lags piper** | `builds/cvm-dt/STAGE6_GATE.json` `ok: true` `live_tree_id=KMesh-COSMOS-live`; `STAGE6_CORE.json` `verdict=PASS` `live_tree_id=KMesh-COSMOS-live`. F-33 is **DONE** (signed `/api/v1/status` `:8770` HTTP 200). Was **BLOCKED on F-33** / `ok: false` / `PENDING_CORE` — that blocker is gone. Same hash-lag caveat as F-16 (`cvm_dt.py` 57611 ≠ gated 57146); do not re-gate from this fence | High | — |
| F-18 | Thin-phone / heavy-local **pull clock** (data pulled off the phone for local processing) | `WISHLIST.md:18-20` | **DONE (contract half)** | `builds/cvm-phone/cvm_phone_pull.py` + `cvm_phone_clock.py`; `STAGE6_PHONE_PULL.json` → `ok: true` with both source sha256s bound. `test_cvm_phone_pull.py` **5/5 run by me**, incl. *"gate artifact binds emitted values… never_seen → fresh after a real pull cycle"* | High | — |
| F-19 | CVM DT clock actually **scheduled** | `builds/cvm-dt/CLOCK_POSTMORTEM.md` | **BLOCKED — Keith's elevated line** | `live/logs/cvm_dt_clock_heartbeat.json` last wrote **2026-08-27T07:26** (≈3.7 days cold). The postmortem's verdict: *"Neither worker crashed… Neither was ever registered."* `--register` only **emits** the `schtasks /Create` line by design | High | XS |
| F-20 | CVM DT **voice** daemon vehicle | `CLOCK_POSTMORTEM.md` (*"no daemon vehicle at all"*) | **DONE (code) / not running** | The gap is closed in code: `builds/cvm-dt/cvm_dt_voice.py:80-81` now defines `TASK_NAME = "COSMOS CVM DT Voice"` + `TASK_NAME_LOGON`, and `:952-955` builds a real `plan_create(...)` for `--loop` on a 1-minute + onlogon pair. Its comment at `:77` preserves the finding. **Still cold at runtime**: `cvm_dt_voice_heartbeat.json` last wrote 2026-08-27T09:59 | High | XS |
| F-21 | Local STT model inference | `BENCH_LATENCY.json`; `WISHLIST.md:19` | **DONE (code) / CVM-DT bench still UNMEASURED** *(bound 2026-08-31T14:55Z)* | Default `py -3.14 -c "import vosk"` is still `ModuleNotFoundError` — that sentence was true and is no longer the whole fact. `cosmos/cosmos_stt.py` puts repo-relative `builds/cvm-dt/vendor/site` on `sys.path` and binds the provisioned model (`COSMOS_VOSK_MODEL` if set, else `builds/cvm-dt/vendor/models/vosk-model-small-en-us-0.15`). **Live `--probe`** `cosmos/_f21_stt_probe.json` `ok:true` `engine=vosk` `kind=ok` `model=…vosk-model-small-en-us-0.15` `vosk_file=…vendor/site/vosk/__init__.py`. `cosmos_cvm_push.probe_stt` now composes that seam (resident Model + KaldiRecognizer, `Reset()` between turns — the F21_STT_LOCAL per-utterance load is not paid). **Bite:** staged `_delme/predispose_cosmos_cvm_push_f21_20260831T145131Z/` `probe_stt` → `STT_NONE` `"vosk not importable"`; `_fail_f21_f68_against_old.json` `all_new_pins_failed:true`. Then `tests/test_stt.py` **10/10** (`cosmos/_f21_stt.json` `probe_ok:true`). Silence decode is `STT_NONE` empty transcript (never a fabricated word). **Still leftover (cvm-dt, this fence did not write it):** `BENCH_LATENCY.json` mtime 2026-08-31 02:34 still records `transcribe.stt_model_inference` `UNMEASURED`. Named in `docs/BLOCKED_ITEMS.md` | High | — |
| F-22 | Mobile app (CDM) | `WISHLIST.md:97` | **DONE** | `builds/cdm/STAGE6_GATE.json` → `ok: true`, `headline "LIVE"`, bound to a built artifact: `app-debug.apk` sha256 `adecb967b95e…`, 9,574,809 bytes, plus `CosmosApi.kt` sha256 and the `/api/v1` path map | High | — |

### 1.3 Mesh, rails and nodes — `cosmos/`, `builds/probe/` (lanes `cc`, `cc-infra`)

| # | Feature | Source | Status | Evidence | Value | Effort |
|---|---|---|---|---|---|---|
| F-23 | Kernel composes the Dispatcher + registers node rails on **normal boot** | `WISHLIST.md:64-73`; `BACKLOG.md:110` | **DONE** *(compose_rails is in HEAD; leftover is F-70 dirty tree)* | `cosmos/cosmos_kernel.py:138` `self.dispatcher = … else self.compose_rails(live_calls=live_calls)`; `:178` `("node_rails","cosmos_node_rails","register_node_rails", False)` as the first compose row; `cosmos_node_rails.py:138` defines `register_node_rails`. **Re-measured 2026-08-31T14:51Z:** `git grep -c "compose_rails" HEAD -- cosmos/cosmos_kernel.py` → **4**. HEAD is `4b22290`. The prior "UNCOMMITTED / exists only in the working tree" sentence is false. Remaining uncommitted files are F-70 (51 modified / 58 untracked), not a missing compose | High | — |
| F-24 | The four answering-but-unwired rails **prove live** (`gw-api`, `cursor-api`, `firecrawl-web`, `playwright-dom`) | `WISHLIST.md:64`; `BACKLOG.md:34`; `builds/probe/MESH_STATUS.md` | **DONE — PROVEN ON THE LIVE TREE** *(2026-08-31T02:56 −05:00)* | All four are in `cosmos/cosmos_rails_prober.WIRED_NODES` with a prove-shaped `live_call`, and all four have answered through `Registry.prove` on the **authority ledger**. `live/registry/rails.json` `count` **4 → 7**: `gw-api model=grok-build-0.1`, `cursor-api model=Cursor COSMOS 2`, `firecrawl-web model=firecrawl/v2-research-papers`, `playwright-dom model=Playwright/1.63.0-alpha-2026-08-05` — each `verified:true`, `rc:0`, `body_bytes>0`. Hash-chained `PROBE_RESULT` rows at `t=1788162963.796 / 964.190 / 964.599 / 966.916`. `proof_ok`'s "name what answered" is satisfied by the **vendor-emitted responder** (`apiKeyName` · MCP `serverInfo` · endpoint gated on a live `arxiv:` id), with `model_source` naming the field; a missing field yields an empty model and **no** registration. MESH_STATUS was right — **no credential was needed for any of the four**. Tests: `cosmos/test_rails_wired.py` **44/44 PASS**, and **30/44 FAIL** against the reconstructed pre-change modules (`cosmos/_bite_check_f24_f25.py`) — the bite proof. ⚠ Two `tests/` checks spell "the four" as a literal and go red until patched; the patch is written and **proven 9/9 + 21/21** by `cosmos/_propose_tests_f24.py` (fence was `cosmos/`)<br><br>**RE-PROVEN AND CORRECTED 2026-08-31T03:32 −05:00.** Wiring is not proof, so all four were re-asked through the shipped path (`py -3.14 cosmos/cosmos_rails_prober.py --root ./live --once --live`) and read back off the **authority ledger**, not off the prober's stdout: hash-chained `PROBE_RESULT` rows **seq 992 / 995 / 996 / 997** — `gw-api ok rc=0 model=grok-build-0.1 body_bytes=4 hmac=773089ea7076f000…`, `cursor-api model=Cursor COSMOS 2 body_bytes=88 hmac=13e691d41e0aace4…`, `firecrawl-web model=firecrawl/v2-research-papers body_bytes=169 hmac=7ec24bf206541de7…`, `playwright-dom model=Playwright/1.63.0-alpha-2026-08-05 body_bytes=76 hmac=e3d941bc2967e9c8…`. Bodies carry values only a live vendor emits (`primaryId=arxiv:gr-qc/9504041`; `tools/list n=24`). `builds/probe/mesh_blockers.py --root ./live --deep` now emits **`live_count 8 of 9`**, `projection_count 8`, `ledger_error null`. `count` is **4 → 8**, not 4 → 7: F-25 had aged `claude-cli` out, and the same `--live` sweep re-proved it through the prepaid seat. **Nothing unproven is counted live anywhere:** `codex-cli` is the sole non-live rail — it holds a `LINK_REGISTERED` claim with `ok:null, last_probe:null`, and is absent from `live_nodes()`, from **every** `route()` (`core→code` = `claude-cli, cursor-api`), and from `live/registry/nodes.json` (`count 8, stale_count 0`). Its typed refusal names the file to create: `NO_KEY: OpenAI key missing at live/config/openai_api_key.txt` (Keith's domain). **Two defects shipped with the original wiring, same root cause — a thing moved between two tables and not removed/carried from the one it left.** (1) All four stayed in `mesh_blockers.UNWIRED_ROWS`, so `rows()` returned **13 entries for 9 rails**, each of the four reported twice in contradictory states — fixed by the supervisor in `builds/probe`. (2) `rows()` derived `probe_with` as `module or "cosmos_claude_rail"`, and the three satellite rows carry `module=None`, so `cursor-api`, `firecrawl-web` and `playwright-dom` were each probed with the **Anthropic** rail: the 03:27:21 deep run reported all three refusing *"NO_KEY: Anthropic key missing at `live/config/anthropic_api_key.txt`"* — a credential none of them uses, while all three carried passing proofs — and `--deep` was **inert**, never reaching `probe_playwright`. Fixed in-fence by `cosmos_rails_prober.probe_module_for()` + a single `SATELLITES` table (the table's owner names its own probe module); the one-line consumer change in `builds/probe/mesh_blockers.py` is **proposed, not applied** (other agent's fence). Runtime-bound: with the fix the three emit their own evidence (`apiKeyName=Cursor COSMOS 2 http=200` · `arxiv:gr-qc/9504041` · `tools/list n=24`) and `live_count` reads 8/9. Tests: `cosmos/test_rails_wired.py` **48/48 PASS**, and the 4 new checks **FAIL against the staged pre-change prober** (`_delme/predispose_cosmos_rails_prober_20260831T033029/`) — bite proven, not assumed | **Highest** | M |
| F-25 | Registry projection applies a **freshness filter** | `MESH_STATUS.md` (*"1 link sits in the projection on an expired proof"*) | **DONE — APPLIED AND PROVEN ON THE LIVE TREE** *(2026-08-31T02:51 −05:00; leftover closed 10:41Z)* | Applied into `cosmos/cosmos_registry.py` (predecessor staged at `_delme/predispose_cosmos_registry_20260831T025109/`). **Bite proven first, not assumed:** `builds/probe/test_registry_freshness.py --impl-live` **13/20 FAIL against the pre-fix file**, then **20/20 PASS** against the applied one. No regression: `run_suites_against_proposed.py --live` **8/8 suites PASS** on the applied module. **Live-tree effect, read off the file the machine wrote:** `live/registry/rails.json` now carries `proof_ttl_s: 3600.0`, and `claude-cli` — which read `verified:true, age_s 318547.6` (**3.69 days**) — is now under `stale` as `verified:false, proof_state:"STALE"`. It is **relocated and named, not deleted**. **Leftover closed 2026-08-31T10:41Z:** `mesh_blockers.classify` still only saw STALE_PROOF when the row was *in* `live_nodes()`, so after F-25 applied it relabelled `claude-cli` as `NO_PROOF` and MESH_STATUS kept claiming *"`file_runtime` applies no freshness filter"*. Bite: `test_mesh_blockers.py` **27/31 FAIL** against the pre-fix file and **0/4** against `_delme/predispose_mesh_blockers_20260831T103327Z/`; **31/31 PASS** after. Live collect: `live_count 7 · stale_count 1 · claude-cli kind=STALE_PROOF in_stale=true in_registry=false` (`builds/probe/_blockers_freshness.json`). Regenerated `MESH_STATUS.md` now says *"`stale` list — `claude-cli`"*. | High | — |
| F-26 | Active scout for **NEW** AI products (not re-reading known hands) | `WISHLIST.md:53-57`, `:101` | **DONE (code) / not scheduled** *(clock 2026-08-31T14:04Z; outward parse 14:12Z)* | **CLOCKS id 23** `cosmos/cosmos_newai_scout.py` / `cosmos_own_clocks.py`. Live heartbeat `newai_scout_heartbeat.json` `state=SCOUTED` `clock_id=23`. Other-lane `cosmos/_f26_live.json` `ok:true` `tree_id=KMesh-COSMOS-live` `proposed_count=15` `known_count=75`; remote fetch `http=200` but **`names=0`** (table-`**bold**` parser on a GitHub-link README). **This fence:** `builds/probe/cosmos_newai_scout.py` parses `[org/repo](https://github.com/…)`; live `--dry-run` `_f26_live_dryrun.json` `kind=MINED` `feed_count=29` `new_count=20` `writes=0` `delta=0` head `codex, claude-code, gemini-cli, zed, warp, gpt-engineer, continue, tabby`. Bite `_bite_f26_scout_absent.json` `all_bite:true`; junk-parse bite `_bite_f26_junk_parse.json` harvested "Inclusion criteria"; then `builds/probe/test_newai_scout.py` **24/24**. `--plan-task` emits `COSMOS New-AI Scout` HOURLY `--once` and registers nothing (`_f26_plan_task.json`). `--once` was **not** fired (would overwrite CLOCKS 23). Remaining operator: Keith `--install-task`. Remaining engineering (outside this fence): promote the GitHub-link parser into `cosmos/` so CLOCKS 23's remote source is not a no-op | Med | XS (register) |
| F-27 | Competency matrix **drives routing** | `WISHLIST.md:46-48` | **DONE (code)** *(consumer 2026-08-31T12:40Z)* | **`cosmos/cosmos_competency.py` reads the file.** `load()` refuses `UNREADABLE`/`BAD_SCHEMA`; `pick(matrix, task_type, available)` is the declared algorithm (possessed==true AND in `available`, max rating, family==dom ties, then `router.nodes_order`). WD2 `pick_agent` is the consumer (`cosmos_watchdog2.py`); default available is `DISPATCHABLE={G46,SGH}` (grok kind, proven worker) + Cursor when the key exists. GEM/OA/DOM are pickable when the caller passes them — they are not implied live. **Bite first:** `_bite_f27_competency.json` `all_bite:true` (module ABSENT, staged WD2 has no import); unwired `pick_agent(matrix=)` **TypeError** 5/5 (`_bite_f27_pick_agent.json` current 25/30). Then `tests/test_competency.py` **31/31** + prechange-lacks-consumer **4/4**. **Live canon values:** `pick(load(docs/COMPETENCY.toml), "code-build", six nodes)=G46`; `"web-research"=SGH`; `"DOM-automation"=DOM`. `pick_agent({"title":"web research scout",…})` → **`agent=SGH kind=grok`** (`cosmos/_f27_competency.json`). `tests/test_watchdog2.py` **43/43**. Overflow still sheds G46 onto Cursor; a named Cursor still wins; DOM-automation with only grok nodes is `NO_CANDIDATE` then fail-closed G46 so the 15s clock does not halt. GEM/OA bucket workers remain F-65 (not invented available). | High | — |
| F-28 | Read every manual; map **every** product into the matrix | `WISHLIST.md:58-63` | **DONE (unverified rows filed)** *(2026-08-31T15:00Z)* | The 14:09Z census that claimed `live_six_nodes` was an exact-set pin is **STALE** (pin became a SUPERSET `required_six <= live_nodes` at 14:36Z). **This fence filed the 15 HANDS stems** as `[nodes.*]` + skill rows `possessed=false rating=0` HANDS-cited `source` — ratings **not** invented; `router.nodes_order` still the live six so they cannot win a tie. Live census `_f28_hands_vs_nodes.json` `node_count=21` `unmapped_count=0` `toml_bytes=48303`. Staged incumbent `docs/_delme/predispose_competency_f28_20260831T145400Z/COMPETENCY.toml` still has 6 nodes / 15 unmapped. Bite `_bite_f28_unmapped.json` `unmapped_count=15`; `_fail_f28_against_old.json` `all_new_pins_failed:true` 3/3 discriminating pins FAIL on the incumbent. Then `builds/probe/test_f28_competency_map.py` **14/14**; `tests/test_competency.py` **31/31** `live_six_nodes` lists 21 ids; `pick(code-build)=G46` `pick(web-research)=SGH` `pick(DOM-automation)=DOM`. A later SGH pass may rate them; this pass will not. Remaining operator: WAVE C install/key for Ollama/Aider/Groq is F-30, not this mapping leftover | Med | — |
| F-29 | **Write the missing tools** — a `tools/` surface | `WISHLIST.md:78-80` | **DONE (code)** *(promoted + composed 2026-08-31T13:10Z)* | **Repo-root `tools/` is the live surface; Kernel composes it.** `tools/surface.py` + `tools/mcp_docs.py`: named verb, typed refusals, `inventory()` is a declaration, `invoke()` is the measurement. Compose row in `cosmos/cosmos_kernel.py` `compose_rails`: `("tools-surface", "tools.mcp_docs", "attach_to_kernel", True)` — binds `kernel.tools`, does **not** invoke, spend, or LINK_REGISTER (not a rail). **Bite first:** `tests/test_tools_surface.py` **FAIL 0/2** `state=ABSENT` before repo-root `tools/` existed; `tests/test_tools_compose.py` **FAIL 4/9** on the incumbent kernel; `_fail_f29_against_old.json` `all_new_pins_failed:true` **4/4 FAIL** against `_delme/predispose_cosmos_kernel_f29_20260831T130051Z/` (old_bytes 18570, composed list has no `tools-surface`). Then hermetic **15/15**, `--live` **17/17**, compose **9/9**, `tests/test_kernel.py` **21/21**. Boot suites (load-bearing): `test_boot_attach.py` **21/21**, `test_boot_rails.py` **12/12**. **Live composed surface answers:** `cosmos/_f29_composed_live.json` `ok:true` `composed_tools_surface:true` `tools_compose.invoked:false` `openai-docs value=openai-docs-mcp http=200` `xai-docs value=xai-docs-mcp http=200` (vendor-emitted `serverInfo.name`, not a grep). Prototype remains at `builds/probe/tools/` (never-delete). Anything *beyond* these two tools is F-30, not a missing surface. GitLab/GitHub stay on the staged *rail*. | Med | — |
| F-30 | Maker-hands sweep → wired rails/nodes | `WISHLIST.md:35`; `BACKLOG.md:29` | **PARTIAL — WAVE A1/A2 landed; WAVE C operator** | `cosmos/cosmos_makers.py` + `makers.toml` exist. WAVE A1/A2 **are in `cosmos/`**: `cosmos/cosmos_forge_rail.py` (`gitlab-forge` + `github-forge`, dst=forge; `--probe` live `_f30_live.json` `ok:true` github `bound=rest_limit=5000` gitlab `user_id=41407957`; `tests/test_forge_rail.py` **22/22** — other-lane 14:29Z). A3 Playwright MCP is F-24; A5 docs MCP is F-29. Remaining from the code: WAVE C (Ollama / Aider / Groq) is Keith install/key. Prototype remains at `builds/probe/proposed/cosmos_forge_rail.py` (never-delete). Named in `docs/BLOCKED_ITEMS.md` | Med | XS remaining (Keith WAVE C) |
| F-31 | Different-family (GEM/OA) critique actually executes | `WISHLIST.md:74-77`; `BACKLOG.md:16` | **DONE (code) / not scheduled** *(CLOCKS id 20, 2026-08-31T14:04Z)* | Critique bodies exist (F-31 premise was stale). **Consumer is now a clock:** `cosmos_own_clocks.py` id **20** `COSMOS CritConsumer` script `cosmos_crit_consumer.py` heartbeat `crit_consumer_heartbeat.json` vehicle detached + 1-min self-heal + onlogon. Other-lane: `tests/test_crit_consumer.py` **59/59**; `--plan-task` registers nothing (`cosmos/_f31_plan_task.json`). Heartbeat file still **absent** until Keith's `--install-task`. Named in `docs/BLOCKED_ITEMS.md` | High | XS (register) |
| F-32 | Missing credentials (codex-cli / Anthropic keyed rail) | `docs/CREDENTIALS_NEEDED.md:14-15` | **BLOCKED — Keith** | `MESH_STATUS.md` measured `codex-cli → NO_KEY`, `claude-cli → STALE_PROOF` on the keyed path. The manifest generator `builds/probe/credential_manifest.py` (652 lines) is built and never reads key material | High | — |

### 1.4 Live Core and the service — `cosmos/` (lane `cc`)

| # | Feature | Source | Status | Evidence | Value | Effort |
|---|---|---|---|---|---|---|
| F-33 | **Core serving on the real root `:8770`** | `WISHLIST.md:37`; `BACKLOG.md:100`; `builds/probe/CORE_8770_DIAGNOSIS.md` | **DONE** *(re-measured 2026-08-31T12:40Z; was ABSENT/operational)* | Signed `GET http://127.0.0.1:8770/api/v1/status` **HTTP 200** `tree_id=KMesh-COSMOS-live` `ready=true` `ledger_head.seq=1270` `event=PROBE_RESULT`; unsigned same path **HTTP 401 `UNAUTHORIZED`**. `live/state/health/board.json` `measured_at=2026-08-31T07:34:26-05:00` **`verdict=GREEN` `reds=[]`** `rows.serve_8770.ok=true` `detail="listening rtt_s=0.0092"`. Was `"RED x1" / serve_8770` at 00:59. F-11 `/cdeck/` is still 404 on this process (shell routes not reloaded) — that is F-11, not this row | **Highest** | — |
| F-34 | A supervisor for Core | `CORE_8770_DIAGNOSIS.md` §5 | **DONE — supervising** *(re-measured 2026-08-31T12:40Z)* | `cosmos_health_clock._supervise_serve`: `supervise=False` returns `DISABLED`; live is **not** that path. `live/logs/health_clock_heartbeat.json` `last_run=2026-08-31T07:36:11-05:00` `state=RUNNING` `verdict=GREEN` **`serve_supervisor.kind=ALREADY_UP`** `detail="port 8770 listening"` (the `if up` branch, which is only reached after the DISABLED return). Board row `serve_supervisor.kind=ALREADY_UP`. Opt-in code still exists; the live clock has the flag on | **Highest** | — |
| F-35 | One machine-checked contract place (CORE_RESTRUCTURE Phase 1) | `CORE_RESTRUCTURE.md:45-62` | **DONE** | `cosmos/cosmos_contracts.py` + six files under `docs/contracts/` (health 4, ledger 5, motif 4, queue 5, rails 3, service 6 = **27**). **My run**: `27/27 contracts verified, 0 contradictions` → `builds/triage/contract_audit_20260831T0600Z.json`. The auditor is itself gated on being able to FAIL | High | — |
| F-36 | Own the state; derive nothing (Phase 2) | `CORE_RESTRUCTURE.md:65-92` | **PARTIAL — 2.3 four sites closed 2026-08-31T16:05Z; 2.1a flip still restrained (62/96, re-measured 18:55Z)** | Inflight primitive + JSON projection exist. **2.3 leftover closed this fence:** four OPEN filename/prose skip-stage sites are now advisory (`critique_filename_stage`, `inflight_filenames_mtime`, `wd2_dhx_haystack`, `wd2_uses_inflight_filenames`). Live `cosmos/_f36_derivation_audit.json` `ok:true` `unreviewed_count=0` `open_count=1` `open=["parse_tracker_markdown"]`. **Re-measured 2026-08-31T18:55Z** (this fence cannot flip): `builds/probe/_f36_judgement.json` `ok:true` `tree_id=KMesh-COSMOS-live` `consecutive_agreements=62` `flip_streak_target=96` `ticks_remaining=34` `flip_ready:false` `authority=markdown` `restraint_justified:true` `restraint_is_excuse:false` `clock_alive:true` `hb_age_s=647.4` `open=["parse_tracker_markdown"]`. `test_f36_judgement.py` **23/23**. **Whose judgement (2.1a):** `FLIP_STREAK_TARGET=96` in `cosmos_motif_driver.py` (scar 2026-08-26); **the human who lands the flip is Keith or COW on the `cosmos/` fence**, after `flip_ready`. Work order 2.2 lands in the same tick as that flip — that is the one remaining OPEN site. Bite `_fail_f36_sites_against_old.json` **8/8 FAIL** `all_new_pins_failed:true`. Did not flip `write_tracker_json`. Runtime-binding gate cannot pass while authority is markdown | High | S remaining (34 ticks + Keith/COW 2.1a+2.2) |
| F-37 | One rail seam (Phase 3.1) | `CORE_RESTRUCTURE.md:95-101` | **DONE** | `cosmos/cosmos_rail_base.py` holds `ledger_is_authority` + `RailError`; `tests/test_rail_base.py` pins that all five rails resolve `_ledger_is_authority` to the **same object** (25/25 in the gate) | Med | — |
| F-38 | Offline contract tests split from live probes (Phase 3.2) | `CORE_RESTRUCTURE.md:103-108` | **DONE** | `tests/test_boot_rails.py` (offline, 12/12) + `tests/test_boot_rails_live.py` (vendor half, narrow skip). Gate reached 100/100 with no vendor keys, which is the stated runtime-binding gate for this phase | Med | — |
| F-39 | Split the god modules (Phase 4) | `CORE_RESTRUCTURE.md:113-124` | **PARTIAL — ten Phase 4 cuts; dispatch DHx/stamps/index seam closed 2026-08-31T18:20Z** | Nine splits landed: `cosmos_collector_dhx.py` + `cosmos_dispatch_workspace.py` + `cosmos_watchdog2_scan.py` + `cosmos_cvm_projection.py` + `cosmos_voice_hardening.py` + `cosmos_collector_scan.py` + `cosmos_dispatch_jobs.py` + `cosmos_dispatch_critique.py` (259) + `cosmos_dispatch_lanes.py` (214). **Stamps leftover closed 18:20Z:** `cosmos_dispatch_stamps.py` (326); live `cosmos/_f39_stamps_split.json` `ok:true` `tree_id=KMesh-COSMOS-live` `disp_lines=1481` (was 1715 / 69549 bytes) `stamps_lines=326` `dhx_same:true` `inbox_same:true`. Bite `_fail_f39_stamps_against_old.json` **9/9 FAIL** `all_new_pins_failed:true` on `_delme/predispose_dispatch_f39_stamps_20260831T182020Z/`. New suite **47/82** on the unsplit dispatch, then `tests/test_dispatch_stamps.py` **82/82**. Callers: `test_dispatch.py` **139/139**, `test_dispatcher.py` **39/39**, `test_watchdog2.py` **43/43**. Remaining: `cosmos_codex_rail.py` (no existing `# seam` — do **not** invent one). Primary label stays PARTIAL | Low | L remaining (no-invent) |
| F-40 | One refusal taxonomy (Phase 5) | `CORE_RESTRUCTURE.md:127-131` | **DONE — the answer was NO MERGE** *(hand-regen recurrence closed 2026-08-31T18:55Z)* | `cosmos/cosmos_refusals.py` + `tests/test_refusals.py` survey **55** typed refusal classes / **141** kinds / 23 collisions, each with a recorded verdict; a new collision surfaces `UNREVIEWED`. `docs/REFUSAL_TAXONOMY.md` is generated (`render_chars=19556`). **Leftover: the projection drifted THREE more times today** (11:20, 12:03, 13:43) because `--diff`/`--write` still required a human paste of `--out`. **Closed in-fence (remeasure_probes shape):** `stale_in` / `refresh_if_stale` / `--check` (rc=1 if stale, no write). Default (no flags) heals stale and exits 0. `test_refusal_taxonomy.py` calls `refresh_stale` before the live MATCH gate. `COSMOS_SKIP_TAXONOMY_REMEASURE=1` is the bite hatch. Live `--check` `stale: []` `match:true` `typed_refusal_classes=55` `distinct_kinds=141`. Scratch `_bite_taxonomy_kind.json` `all_bite:true`: planted `SCRATCH_KIND_PROBE`, `--check` rc=1, heal, `--check` rc=0, live doc untouched. Fail-old `_fail_taxonomy_remeasure_against_old.json` `all_new_pins_failed:true` **5/5**. Then `test_refusal_taxonomy.py` **62/62**. `tests/test_refusals.py` **14/14 + 1/1**, not weakened. Absent is still `DOC_ABSENT` (not SKIP). `--write` still exits 2 this tick (the red is the notice). `test_rail_base.py` still pins the two `RailError` kind-sets as **DISJOINT** | Med | — |
| F-41 | Tool migration disposition backlog | `BACKLOG.md:128` | **PARTIAL — proposer + UNPLANNED cards built, live ledger not written** *(cards 2026-08-31T11:56Z)* | The 135 UNDECIDED were not 135 missing judgements: `cosmos_port_plan.PORT_DECISIONS` already holds **35** rulings (25 REPLACED · 10 ADAPTED). Live, 19 of those names are still UNDECIDED and 8 are not declared. **Built:** `builds/probe/tool_disposition.py` — proposes APPLY only when the successor `cosmos_` module exists on disk; UNPLANNED is HOLD (no invented ruling); DRIFT (`bts_cursor` live REPLACED vs plan ADAPTED) is HOLD, never overwritten. `apply()` on a scratch ledger records `TOOL_DISPOSITION`. `apply()` against `live/ledger/authority.jsonl` REFUSES **`LIVE_LEDGER_FORBIDDEN`** and does not open the file. **UNPLANNED cards now exist:** `cards_for_unplanned()` writes one HOLD card per name; `successor_candidates` are cosmos_ modules on disk whose stem overlaps a token — evidence, not a ruling; `disposition` stays `null`. **Bite:** `_bite_tool_disposition_absent.json` `state=ABSENT`; staged old module has no `cards_for_unplanned`; then `test_tool_disposition.py` **19/19**. **Live, zero writes:** `_f41_proposals.json` `live_total 143` `apply_ready_count 27` `UNPLANNED 116` `writes: 0`; `_f41_unplanned_cards.json` **`card_count:116` `with_candidates:47` `without_candidates:69`**; `--apply --ledger authority.jsonl` → `_f41_live_apply_refused.json` `kind=LIVE_LEDGER_FORBIDDEN` `ledger_untouched:true`. **Re-measured 2026-08-31T14:58Z** (`_f41_live_apply_refused.json` `kind=LIVE_LEDGER_FORBIDDEN` `cli_rc=2` `ledger_before_bytes=ledger_after_bytes=643712`; `describes` pins `tool_disposition.py` 19583 `b64df60e…`). The 607100 figure was the 13:26Z snapshot; 559724 was 11:57Z. This `--apply` did not open the file. Remaining: COW applies the 27 on a writing Kernel (outside this fence); COW records PORT_DECISIONS rulings for the 116 HOLD cards (`cosmos/` is outside this fence) | Low | S remaining (apply) + L (rulings) |
| F-42 | The gate on the gates | `CORE_RESTRUCTURE.md:32-42` | **DONE** | `builds/selftest_clock/cosmos_selftest_clock.py`, `COSMOS Selftest Clock` every 15 min. Fresh artifact: `selftest_clock_heartbeat.json` `2026-08-31T00:57:05-05:00` → **100/100, 0 flaky, 0 failed** | High | — |

### 1.5 Backup and offsite — `builds/backup/`, `cosmos/` (lane `cc-infra`)

| # | Feature | Source | Status | Evidence | Value | Effort |
|---|---|---|---|---|---|---|
| F-43 | Bulletproof backup daemon — verified, rehearsed, scheduled, fail-closed, heartbeated | `WISHLIST.md:90-94` | **DONE (code) / dest+VSS BLOCKED / not scheduled** *(identity leftover closed 2026-08-31T16:30Z)* | Built and running: `cosmos/cosmos_backup.py` (per-file hash + rehearsed restore) driven by `cosmos_backup_clock.py` on four daily `schtasks`; dest still same-volume `live/backups`. P0 vehicle: `builds/backup/cosmos_local_clock.py` — `--plan-task` emits `schtasks /create /tn "COSMOS Bulletproof Backup"` `/sc daily` `/st 04:00` and **registers nothing**. Without dest `tick()` REFUSES `NO_CONFIG`/`NO_DEST`/`NO_SOURCE`; a dest on the source volume is `SAME_VOLUME` (never invents `live/backups`). **This-fence leftover closed 2026-08-31T16:30Z:** `bind_local` now checks optional `targets.local.identity` via the same `_check_identity` F-48 mounts already run. Drive letter is not identity — a swapped disk is `IDENTITY_MISMATCH` and creates no set. Bite `_bite_f43_identity.json` `all_bite:true` (`mismatch_tick_verified:true` `mismatch_created_a_set:true` `bind_local_has_identity_param:false`). `_fail_f43_identity_against_old.json` **6/6 FAIL** `all_new_pins_failed:true` on `_delme/predispose_f43_identity_20260831T162758Z/` (old mismatch `state=VERIFIED` `set_count=1`). Live `_f43_identity_live.json` `ok:true` `mismatch.kind=IDENTITY_MISMATCH` `sets=[]` `match.state=VERIFIED` clock 15590 `41991288…`. Then `test_local_clock.py` **31/31**. **Live, nothing written and no production heartbeat:** `_f43_clock_live_preflight.json` `cli_rc=2` `status=BLOCKED` `kind=NO_CONFIG` `adapter_implemented:true` `heartbeat_written:false` `live_heartbeat_exists:false`; `_f43_clock_plan_task.json` `registers:false`. `--install-task` was not run. Freeze seam + VSS_UNAVAILABLE `0x80041014` unchanged. **Still operator (same shape as F-48):** Keith names `targets.local.dest` + `targets.local.source` on a different volume (or F-46/F-48 dests), then one elevated `schtasks` line; VSS Create needs an elevated session. Wishlist `V:\` trees are the same dest/cred unblock | **Highest** | XS remaining (dest + register) |
| F-44 | The backup actually covers every file it claims | `docs/LONGPATH_FINDING.md:19-40` | **DONE — the fix has LANDED in `cosmos/`** *(re-audited 2026-08-31T07:27Z; this row was ABSENT and is now measured otherwise)* | The row's own `behave` probe, **re-run 2026-08-31T14:59:17Z against the live modules** (`test_artifact_freshness.py` had gone STALE on the 13:26Z artefact): `builds/probe/_longpath_behaviour.json` `measured_utc=2026-08-31T14:59:17Z` `describes` `cosmos/cosmos_backup.py` 9861 `6a1fdb1f…` / `cosmos_backup_clock.py` 14052 `b6c80de1…` / `builds/backup/cosmos_backup.py` 39968 `97944279…` → all three **`"verdict": "COVERS_LONG_PATHS"`**, `files_reported 3`, `covered {shallow,class_a,class_b all true}`, `missed []`, `long_paths_enabled_registry: 0`. Same verdict for `cosmos/cosmos_backup_clock.py` (`copied 3, truncated false, unreadable []`). Was `SILENTLY_OMITS … missed=['class_a','class_b']`. Suites: `builds/probe/test_longpath_census.py` **6/6** this pass; `builds/backup/test_longpath.py` was **10 tests OK** (1 skipped, POSIX-only) at 07:27Z | **Highest** | — |
| F-45 | R2 offsite adapter | `WISHLIST.md:95-96` | **DONE (code) / BLOCKED (credential)** | `builds/backup/cosmos_backup_r2.py` (469 lines): stdlib SigV4 signer confirmed against AWS's published `get-vanilla` vectors, injected transport, `push()` that **reads every object back and re-hashes**, `FORBIDDEN_PREFIXES` refusing `D:\R2Cloner` before touching the filesystem. `test_cosmos_backup_r2.py` **35 tests, OK — re-run 2026-08-31T11:56Z**. Preflight on the live root: `"state": "NO_CREDENTIALS"` | High | — |
| F-46 | R2 credential in place | `R2_OFFSITE_PLAN.md:59-70`; `CREDENTIALS_NEEDED.md:20` | **BLOCKED — Keith** *(re-measured 2026-08-31T11:57Z)* | `r2_credentials.json` is still absent. Live `--preflight` `_f47_live_preflight.json` `cli_rc=2` `credential.state=NO_CREDENTIALS` `adapter_implemented:true`. `ADAPTERS["r2"]()` is the same kind (`_f47_live_adapter.json` `writes:0`). One file unblocks the whole offsite leg. This pass did not read, invent, or place it | **Highest** | XS |
| F-47 | A **scheduled** offsite push | `R2_OFFSITE_PLAN.md:50` | **DONE (code) / not scheduled** *(leftover closed 2026-08-31T11:57Z)* | `builds/backup/cosmos_offsite_clock.py` exists: `--plan-task` emits `schtasks /create /tn "COSMOS Offsite Push"` and **registers nothing** (pinned by `test_plan_task_registers_nothing`); without the credential `tick()` REFUSES `NO_CREDENTIALS`, heartbeats the refusal, exits 2, and builds no transport. **In-fence leftover closed:** `ADAPTERS["r2"]()` is a factory, not a stub — no-args REFUSES typed `NO_CREDENTIALS` (Bite: staged old raises `NotImplementedError`, `_bite_f47_r2_stub.json` `all_bite:true`); `do_rehearse_target` is R2_OFFSITE_PLAN Gate B (MemoryTransport `files_restored:2` `kind=REHEARSAL_PASS`); `DEFAULT_EXCLUDES` is `(".git", "__pycache__")`. `test_offsite_clock.py` **35/35**; `test_cosmos_backup_r2.py` **35/35**. **Live, no credential read:** `_f47_live_adapter.json` `kind=NO_CREDENTIALS` `writes:0`; `--preflight` `_f47_live_preflight.json` `cli_rc=2` `status=BLOCKED` `credential.state=NO_CREDENTIALS` `adapter_implemented:true` `task_registered:false` scopes `NO_SCOPES`. A prior `--once` (not this pass) left `live/logs/offsite_clock_heartbeat.json` at `2026-08-31T06:58:23Z` itself `state=REFUSED` `kind=NO_CREDENTIALS` `offsite_copy_exists:false` — the refusal is the waiting state. `--install-task` is Keith's elevated line and was not run. Blocked on F-46 for a real push. | High | XS (register) |
| F-48 | Backup to the new Seagate ES.3 / GDX (Google Drive) / ODX (OneDrive) | `WISHLIST.md:91-94` | **DONE (code) / gdx dest PUSHED / R2 on 03:00 PUSHED / ODX SKIPPED / ES.3 queued / task registered** *(R2 nightly 2026-08-31T18:34Z)* | Adapters landed in `builds/backup/cosmos_backup_mounts.py`. Dest is `config/backup_targets.json` (or `--dest`), **never invented**. Clock: `cosmos_mount_clock.py` daily 03:00. **R2 leftover closed this fence:** the same tick now appends `target_kind=r2` (adapter `cosmos_backup_r2`); absent credential is typed `NO_CREDENTIALS`. Live `--once --source` tiny `--force` `_mount_r2_live.json` r2 `state=PUSHED` `files_pushed=2` `readback_verified=2` `bucket=ai-dchambers` `prefix=src/20260831T183424`; gdx `PUSHED` `set_dir=X:\My Drive\COSMOS_BACKUP\src-20260831T183424`; odx/es3 `NO_DEST`. schtasks `COSMOS Mount Offsite Push` **Ready** next `9/1/2026 3:00:00 AM`. Bite `_fail_mount_r2_against_old.json` **5/5 FAIL**; `test_mount_clock.py` **39/39**. **gdx/builds PUSHED 18:07Z:** `_gdx_builds_push.json` `file_count=16781` `total_bytes=7664839452`. ODX dest SKIPPED (operator). ES.3 dest queued (no disk) | Med | — |
| F-49 | `docs/CREDENTIALS_NEEDED.md` R2 row is current | `CREDENTIALS_NEEDED.md:20,218,229` | **DONE** *(regenerated 2026-08-31T11:00:59Z)* | Generator flipped `r2-credentials` from `wired=False` / `PLANNED` to `wired=True` / `BLOCKED`; consumers are `cosmos_backup_r2.py:137` and `cosmos_offsite_clock.py:256`; verify is `--preflight` expecting `"status": "READY"`. **Bite:** staged old module `_bite_f49_f50_old.json` `wired=false` `severity=PLANNED` `all_bite:true`. **Generated artifact:** `docs/CREDENTIALS_NEEDED.md` **Measured 2026-08-31T11:00:59Z** — R2 row is **BLOCKED**, unblocks *"the R2 offsite push (`builds/backup/cosmos_backup_r2.py`)"*, `ask_now` includes `r2-credentials`. `test_credential_manifest.py` **42/42**. The *"once its adapter seam is implemented"* sentence is gone | Med | — |
| F-50 | Credentialing as an **open-window handoff** | `WISHLIST.md:85-87` | **DONE (code)** *(2026-08-31T11:01Z)* | Window-opening half landed: `credential_manifest.open_doors` + CLI `--open NEED_ID` / `--open-asks`. Injected opener so the suite cannot launch a browser. **Bite:** staged old module has no `open_doors` (`_bite_f49_f50_old.json`). **Proven:** `open_doors(["openai-api-key","r2-credentials"], opener=list.append)` launched exactly `https://platform.openai.com/api-keys` and skipped R2 as `NO_WINDOW`; unknown id is `UNKNOWN_NEED`; planted secret absent from the payload. `test_credential_manifest.py` **42/42**. Not invoked against a live browser this pass (would steal focus). `--write-md` still does not open anything | Med | — |

### 1.6 Orchestration, resilience, federation (lanes `cc`, `cc-infra`)

| # | Feature | Source | Status | Evidence | Value | Effort |
|---|---|---|---|---|---|---|
| F-51 | **AUTO-RESESSION** — continue across the context boundary | `WISHLIST.md:25-28`, `:34`; `BACKLOG.md:65` | **DONE (code) / not scheduled / prompt filed** *(promoted 2026-08-31T11:30Z; P1.3 2026-08-31T13:48Z)* | **Shipped into `cosmos/` + CLOCKS id 18.** `cosmos/cosmos_resession.py` (`CLOCK_ID = 18`); `cosmos_own_clocks.CLOCKS` row task `COSMOS Resession` script `cosmos_resession.py` standup `resession` heartbeat `resession_heartbeat.json` vehicle `schtasks /sc minute /mo 1 --once`. **Bite first:** `cosmos/_bite_f51_promote.json` `all_bite:true` — module `ABSENT` `FileNotFoundError`, staged `_delme/predispose_own_clocks_f51_20260831T112530Z/` CLOCKS `count=17` `has_id_18:false`. Then `tests/test_resession.py` **46/46** (`cosmos/_f51_promote.json` `ok:true` `live_value {"checks":46,"clock_id":18,"scratch_state":"IDLE","heartbeat":"resession_heartbeat.json"}`); `tests/test_own_clocks.py` **70/70** including `clock 18 is COSMOS Resession`; `--selftest` **12/12**. Live `--dry-run` (`cosmos/_f51_live_dryrun.json`): `state=IDLE` `tree_id=KMesh-COSMOS-live` `clock_id=18` `prompt_sha=null` `why="no COW heartbeat"` — writes nothing. `--plan-task` (`cosmos/_f51_plan_task.json`) emits `COSMOS Resession` minute/1 `--once` and **registers nothing**. `live/logs/resession_heartbeat.json` and `live/state/control/RESESSION.json` **absent**. Injected `standup()` never calls real schtasks. **Prompt filed 2026-08-31T13:48Z (P1.3, fence artifact):** `docs/AUTO_RESESSION_PROMPT.md` 1133 bytes sha256 `5d10d8ff510503a00b01d6a2b1efca7941ca92a10efc3aa1c6ed59082cfca8db`. Bite `builds/probe/_bite_f51_prompt.json` `all_bite:true` (`prompt_exists:false` `dry_run_prompt_sha:null` fire `NO_PROMPT`). New pins **3/3 FAIL** (`test_resession.py` 39/42) then **45/45**. Live `--dry-run` `_f51_prompt_live.json` `ok:true` `prompt_sha=5d10d8ff…` `state=IDLE` `tree_id=KMesh-COSMOS-live` `writes:0`. A missing file is still `NO_PROMPT`. **Still operator:** `--install-task` (Keith's elevated line). Probe copy remains under `builds/probe/` | **Highest** | XS (register) |
| F-52 | Resume gate (P3) | `CLAUDE.md:54-68`; `BACKLOG.md:72` | **DONE** | `cosmos_watchdog2.py:478-508` (`mode != "resume_gate"` → stay PAUSED; unparseable `auto_resume_at` → stay PAUSED, fail-closed) + `:915-943`. Runtime proof it has actually fired: `live/logs/WATCHDOG2.log` → `AUTO-RESUME (resume_gate) … auto_resume_at=2026-08-25T23:51:58 reached` | High | — |
| F-53 | **Second / parallel orchestrator on a prepaid model** | `WISHLIST.md:105-119` (P1, *"the promotion"*) | **DONE (code) / not scheduled** *(PARALLEL drop 2026-08-31T16:16Z)* | CLOCKS id **24**, winner **grok**, Claude is typed `CLAUDE_SPEND`. **This-fence leftover closed:** COW-fresh PARALLEL is no longer mailbox-ping + drop 0. It mailbox-pings AND drops one MOTIF work-order (Agent `xAI \| grok \| prepaid-orch`) when `open_prepaid_orders` is empty; a second tick with an open order drops 0 (no flood). Queue drop only — never kernel/ledger/sched/service. Spawn still opt-in (`--spawn`). **`--engine gbw` still does not close this row** (it is a builder). **Bite first:** `_fail_f53_parallel_against_old.json` **6/6 FAIL** `all_new_pins_failed:true` on `_delme/predispose_f53_parallel_20260831T161219Z/` (`old_dropped=0` `old_order_count=0` `old_readme` mailbox-only). Then `tests/test_prepaid_orch.py` **24/24** (`_f53_prepaid_orch.json` `parallel_state=PARALLEL` `dropped=1`); `tests/test_own_clocks.py` **88/88**. **Live, nothing written:** `--once --dry-run` `cosmos/_f53_live.json` `ok:true` `winner=grok` `grok_present:true` `state=ORCHESTRATE` `cow_fresh:false` `tree_id=KMesh-COSMOS-live` `writes:0` `dropped:0` `spawned:0`. `--plan-task` registers nothing. **Still operator:** Keith's `--install-task`; `--spawn` only if he wants a live grok -p | **Highest** | XS remaining (register) |
| F-54 | Persistent orchestrator state, redundant and **off-machine** | `WISHLIST.md:110-119` | **PARTIAL — packer + clock built, no off-volume copy / not scheduled** *(clock 2026-08-31T15:43Z)* | On-tree persistence exists: signed `live/state/SEED.json` + `SEED.decl.json`, `live/state/inflight.jsonl`, `live/state/motif_tracker.json`. **Named payload packer exists:** `builds/backup/cosmos_state_offsite.py` copies that whitelist (never `live/state/` wholesale), secret-scans it, and drives the F-47/F-48 adapters. **Without dest AND without credential the tick REFUSES `NO_OFFSITE_ROUTE`**, heartbeats the refusal, exits 2, and writes nothing to a mount. **Clock vehicle 2026-08-31T15:43Z:** `--plan-task` emits `schtasks /create /tn "COSMOS State Offsite Push"` `/sc daily` `/st 03:15` and **registers nothing** (pinned by `test_plan_task_registers_nothing`). F-47/F-48 clocks push *scopes*; this clock pushes the whitelist. **Bite first:** `_bite_f54_plan_task.json` `all_bite:true` (`has_plan_task_argv:false` CLI `--plan-task` not a verb); then `test_state_offsite.py` **25/25** (was 18; +7). Fail-against-old `_fail_f54_plan_task_against_old.json` **5/5 FAIL** `all_new_pins_failed:true`. **Live, nothing written and no production heartbeat:** `_f54_live_preflight.json` `status=BLOCKED` `kind=NO_OFFSITE_ROUTE` `payload.present=4` `bytes=340044` (324562 was 14:58Z; 293610 was 13:26Z; 254853 was 11:30Z) routes `NO_CONFIG` + `NO_CREDENTIALS` `adapter_implemented:true` `heartbeat_written:false`; `_f54_clock_plan_task.json` `registers:false` payload four names; `live/logs/state_offsite_heartbeat.json` **absent**. `--install-task` was not run. The redundancy requirement is still unmet — every copy is under `V:\A\Ai\COSMOS\live` until Keith names dests (F-48) or the R2 credential (F-46), then one elevated `schtasks` line | **Highest** | XS remaining (dest/cred + register) |
| F-55 | Inter-orchestrator comms — write-locked shared mailbox (COW ⇄ GrokBot) | `WISHLIST.md:120-127` (P1) | **DONE (code)** *(channel 2026-08-31T12:48Z)* | The three named gaps closed in `cosmos/cosmos_mail.py`. **Hash-chained append:** each note carries `prev_hash` + `msg_sha256`; genesis is `GENESIS_HASH` (64 zero hex); a planted prev_hash lie is typed `CHAIN_BREAK`. **Writer signature:** keyed send sets `signed=true` and HMAC-SHA256 `writer_sig` over the canonical note + writer id; tampering `from` is `FORGED_MESSAGE`. **cosmos_lock:** `Mailbox(..., arbiter=, key=)` `send()` acquires `mail:{to}`, four-phase fenced COMMIT, releases; a held resource is `LockError HELD` (one writer). Kernel composes both (`arbiter=None if read_only else self.arbiter`, install key). **Bite first:** `_bite_f55_mail.json` `all_bite:true`; `_fail_f55_against_old.json` **8/8 FAIL** on `_delme/predispose_cosmos_mail_f55_20260831T124826Z/`. Then `tests/test_cosmos_mail.py` **23/23** (`_f55_mail_suite.json` `fenced_events=["GRANT","COMMIT_RESERVED","COMMIT","RELEASE"]`); `tests/test_kernel.py` **18/18** `k.mail.arbiter is k.arbiter` COMMIT `mail:critic`. Live boxes still 9 under `live/state/mail/`. **Still F-53:** no GrokBot participant — the channel is the row, the second orchestrator is not | High | — |
| F-56 | **FEDERATION — SRV1 and T7 on the LAN** | `WISHLIST.md:128-130` | **DONE (code) / BLOCKED (hosts)** *(re-measured 2026-08-31T14:55Z)* | The ABSENT cell was stale — `"Zero occurrences of SRV1 or T7920"` is false. `cosmos/cosmos_identity.py` `LAN_NODES` names **SRV1** (storage, 9 TB) and **T7** alias **T7920** (compute, 56-core / 128 GB). `probe_lan_node` is the measurement: host is `None` until Keith names an address; this function does not invent one. **Live** `cosmos/_f56_live.json` `federation_ready:false` `blocker_count:5` SRV1/T7/T7920 all `kind=NO_HOST` `reachable:false` `status=not_installed`; suite artifact `cosmos/_f56_federation.json` `live_value.srv1_kind=NO_HOST`. `tests/test_federation.py` **11/11**; `tests/test_features.py` **33/33** pins `LAN_NODES` + `NO_HOST`. Remaining: Keith installs COSMOS on SRV1 and T7 and names a host. Named in `docs/BLOCKED_ITEMS.md` | Med | — (hosts) |
| F-57 | Health watchdog — hourly fleet check + free Slack heartbeat + COW-escalation-only-on-exception | `WISHLIST.md:132-140` (P0) | **PARTIAL — running; the Slack half is BLOCKED** | Built and beating: `builds/health/cosmos_health_watchdog.py`, `live/logs/health_watchdog_heartbeat.json` at `2026-08-31T00:21:02-05:00` → `state RUNNING · interval_s 3600 · alive 17 / fleet 17 · verdict "RED x1"`. Goals text is implemented (`load_goals()` at `:490`, called `:1065`). **Slack does not deliver**: same heartbeat → `"slack_mode": "PAGE", "slack_ok": false`, because `load_slack_webhook` (`:219-233`) refuses without `live/config/slack_webhook.txt` — fail-closed, `REFUSED_NOT_SLACK` on anything not `hooks.slack.com` | **Highest** | XS |
| F-58 | The watchdog discovers what it is **not** watching | `CHANGELOG…:811-818` | **DONE** | `builds/health/cosmos_health_watchdog.py:349` `def discover_unwatched(logs, now, stale_s=UNWATCHED_STALE_S)`, `:140` `UNWATCHED_STALE_S = 24*3600`, `:372` RED only for *unwatched AND stale*, `:420` state `UNWATCHED_STALE:<fingerprint>`. It deliberately does **not** auto-add to `FLEET` (unknown cadences → false alarms). Confirms the gap it was built for: **29** heartbeat files in `live/logs/` vs `fleet 17` in the heartbeat | High | — |
| F-59 | The queue distinguishes a **timeout** from a work failure | `CHANGELOG…:1080-1099` | **DONE** *(re-audited 2026-08-31T12:45Z; was ABSENT)* | `builds/cc_driver/cc_outcome.py` `classify()` — process outcome ≠ work outcome. `TIMED_OUT_WITH_OUTPUT` routes to `timed_out/` (review, not failed). `cosmos_cc_driver.py` calls `cc_outcome.classify` **before** filing (`timed_out=True` keeps stdout from `TimeoutExpired`). **This pass ran** `py -3.14 builds/cc_driver/test_cc_outcome_evidence.py` → **28/28 OK**. The old `except TimeoutExpired: ok=False; emit_incident; _move(..., failed)` path is the staged predecessor, not the live driver | Med | — |
| F-60 | Test suites must not write **production** heartbeats | `CHANGELOG…:888-899` | **DONE — health --once schtasks sandbox inherited 2026-08-31T18:35Z** | Guard contract lives under `tests/` so this fence can wrap without touching `builds/cvm-dt/` (other session) or `builds/health/`. `tests/cosmos_test_guard.py` `sandbox_heartbeats()`: path-free, OS temp dir only, typed `PROD_WRITE_REFUSED` — **now also wraps `cosmos_clock.run_schtasks` / `harden_task`.** `/create` `/delete` `/change` `/run` `/end` of a COSMOS task is refused before the native binary runs (`called_real:false`). **`test_collector_dhx.py`, `test_node_bucket_worker.py`, `test_backup_clock.py` wrap `main` in it.** `tests/test_live_write_fence.py` FENCED_SUITES now includes `tests/test_backup_clock.py` `own_it=True`. **Bite first:** staged `_delme/predispose_f60_schtasks_20260831T164154Z/` has no `guarded_run_schtasks` and omits backup_clock from FENCED_SUITES; `_fail_f60_schtasks_against_old.json` **4/4 FAIL** `all_new_pins_failed:true`; suite-before **7/11**. Then `tests/test_cosmos_test_guard.py` **11/11**; wrapped `test_backup_clock.py` **22/22**; `test_collector_dhx.py` **38/38**; `test_node_bucket_worker.py` **51/51**; `test_live_write_fence.py` **22/22** (`test_backup_clock.py` `rc=0` `violations=[]` `unfenced_spawns=[]`). Live `cosmos/_f60_schtasks.json` `ok:true` `tree_id=KMesh-COSMOS-live`. **Health leftover closed 18:35Z without writing `builds/health/`:** `cosmos_clock.run_schtasks` / `harden_task` honor `COSMOS_SCHTASKS_SANDBOX` (descendant `--once` inherits it; native `schtasks.exe` is not invoked). `tests/test_live_write_fence.py` sets the env on the child and pins `test_cosmos_health_watchdog.py: no native unfenced spawns (F-60)`. Live `cosmos/_f60_sandbox.json` `ok:true` `tree_id=KMesh-COSMOS-live` health `unfenced_spawns=[]` `procs=2` `python_spawns=1` `rc=0`. Bite `_fail_f60_sandbox_against_old.json` **6/6 FAIL** `all_new_pins_failed:true` `old_query_calls=1` on `_delme/predispose_f60_sandbox_20260831T183526Z/` (old `/query` still spawned). Then `test_cosmos_test_guard.py` **18/18**; `test_live_write_fence.py` **23/23**; wrapped `test_backup_clock.py` **22/22**; `test_collector_dhx.py` **38/38**; `test_node_bucket_worker.py` **51/51**. `cvm_test_guard.py` stays the cvm-dt copy (this fence did not touch it). `builds/cvm-dt/` was not touched | High | — |

### 1.7 The route, dispatch and the clocks — `cosmos/` (lane `cc`)

| # | Feature | Source | Status | Evidence | Value | Effort |
|---|---|---|---|---|---|---|
| F-61 | The dozen COSMOS-own clocks (no BTS) | `WISHLIST.md:32`; `BACKLOG.md:59` | **DONE — 24, not 12** *(re-audited 2026-08-31T14:55Z)* | `cosmos/cosmos_own_clocks.py` `CLOCKS` ids **1–24**. Id **18** Resession (F-51). Id **19** Askmine (F-63). Id **20** CritConsumer (F-31). Ids **21/22** Grok/GEM bucket workers (F-65). Id **23** NEW-AI Scout (F-26). Id **24** Prepaid Orchestrator (F-53). `tests/test_own_clocks.py` pins clock 24. 18–24 are not registered (`--install-task` is Keith) | High | — |
| F-62 | WD2 drives the route from `WISHLIST.md` | `BACKLOG.md:85` | **DONE** | `cosmos_watchdog2.py` `MD_ROUTE_SOURCES` now **wishlist + backlog + askmine** (`loc=state`, `live/state/askmine/UNANSWERED.md`, section Open, enter implement). One shared parser `parse_md_checkboxes`. `tests/test_watchdog2.py` **43/43** pins `md_sources == ["wishlist","backlog","askmine"]` and an absent askmine file contributing 0 items. The **resident** WD2 process has not reloaded, so the production heartbeat still lists the two-source array until Keith's next restart — that is F-11-shaped, not a missing source | High | — |
| F-63 | **Session-transcript mining** — flag unaddressed questions/requests | `BACKLOG.md:49-58` | **DONE (code) / not scheduled** *(promoted 2026-08-31T12:18Z)* | **Shipped into `cosmos/` + CLOCKS id 19 + WD2 route source.** `cosmos/cosmos_askmine.py` (`CLOCK_ID = 19`); `CLOCKS` row task `COSMOS Askmine` script `cosmos_askmine.py` standup `askmine` heartbeat `askmine_heartbeat.json` vehicle `schtasks /sc HOURLY --once`. Detector unchanged (six signals, redaction, paired gate). Clock writes `live/state/askmine/result.json` + `UNANSWERED.md` (Open checkboxes); WD2 `MD_ROUTE_SOURCES` third source `loc=state` section Open enter implement. Empty scan is typed `NO_TRANSCRIPT` and heartbeats the refusal. **Bite first:** `cosmos/_bite_f63_promote.json` `all_bite:true` — module `ABSENT` `FileNotFoundError`, staged CLOCKS `count=18` `has_id_19:false`, WD2 sources wishlist+backlog only. Then `tests/test_askmine.py` **66/66** (`cosmos/_f63_promote.json`); `tests/test_own_clocks.py` **74/74** including `clock 19 is COSMOS Askmine`; `tests/test_watchdog2.py` **43/43**. Live `--dry-run` with `--scan-dir cosmos/` was `NO_TRANSCRIPT` (`cosmos/_f63_live_dryrun.json`). **Re-measured 2026-08-31T12:28Z on default scan dirs:** `builds/probe/_f63_live_dryrun.json` **`state=MINED` `ok:true` `dry_run:true` `clock_id=19` `transcripts_seen=2555` `asks=1788` `findings=252` `outstanding=252` `elapsed_s=26.953`** — writes nothing. `--plan-task` (`builds/probe/_f63_plan_task.json`) emits `COSMOS Askmine` HOURLY `--once` and **registers nothing**. `live/logs/askmine_heartbeat.json` **absent** after both. Injected `standup()` never calls real schtasks. **Still operator:** `--install-task` (Keith's elevated line). Probe copy remains under `builds/probe/`. Measured limit unchanged: Keith's Cowork transcripts are not on this host | High | XS (register) |
| F-64 | Auto-context dispatch (tag + assignment → daemon pulls context, creates the agent, files the record) | `WISHLIST.md:42-45`; `docs/DISPATCH_AUTOCONTEXT.md` | **DONE** | `cosmos/cosmos_dispatcher_daemon.py:9` (*"Pulls the CURRENT session transcript TAIL"*), `:47` `from cosmos_context_pull import …`. Running: `dispatcher_heartbeat.json` `state RUNNING · polls 39740 · interval_s 5.0`; records land in `live/state/assignments/<session>.jsonl` | High | — |
| F-65 | Grok & GEM workers polling **their own buckets** | `WISHLIST.md:38-41` | **DONE (code) / not scheduled** *(CLOCKS ids 21/22, 2026-08-31T14:04Z)* | Modules exist. **Now CLOCKS ids 21/22** (`COSMOS Grok Bucket Worker` / `COSMOS GEM Bucket Worker`) in `cosmos_own_clocks.py`. Other-lane: `tests/test_grok_gem_bucket_workers.py` **62/62**; `--plan-task` registers nothing. Heartbeats still **absent** until Keith's `--install-task`. Older `cosmos_grok_worker` / `cosmos_gem_worker` pair is still the live path. Named in `docs/BLOCKED_ITEMS.md` | Med | XS (register) |
| F-66 | GDX / ODX as alternate result destinations for the bucket workers | `WISHLIST.md:39-41` | **DONE (code) / dest unconfigured / workers not started** *(measured 2026-08-31T13:22Z)* | Dest contract lives in `cosmos/cosmos_bucket_daemon.py` `dest_dir()`: V default is resolver `live/returns/<node>`; GDX/ODX come from `live/config/bucket_worker.json` `dest` and **never** from a drive literal. Missing dest is typed `NO_DEST`. **This pass ran** `tests/test_grok_gem_bucket_workers.py` **58/58** — GDX without config `kind=NO_DEST`; configured ODX lands under `<dest>/COSMOS/returns/gem` and is a directory. Live `bucket_worker.json` is absent (same shape as F-48 `NO_CONFIG`). Starting the workers is F-65 (`schtasks`, not this row) | Low | — |
| F-67 | COSMOS_INDEX — the single self-refreshing living index | `WISHLIST.md:33`; `BACKLOG.md:62` | **DONE** | `cosmos/cosmos_index.py` (1,136 lines) → `docs/COSMOS_INDEX.md` + `live/state/cosmos_index.json` + `cosmos_index.html`. Running as clock id 13: `cosmos_index_heartbeat.json` `schema cosmos-index/2 · tick "done" · panel_ok true`, fresh at `2026-08-31T00:58:12` | Med | — |
| F-68 | Master description re-render (folding the ITERATE fix + the competency table) | `WISHLIST.md:49-50` | **DONE (in-fence render)** *(2026-08-31T14:55Z)* | Agent render, not COW's context. `cosmos/cosmos_master_desc.py` writes OOXML from live `docs/COMPETENCY.toml` + the MOTIF 1→8 pin. **Emitted** `docs/COSMOS_MASTER_DESCRIPTION.docx` `bytes=4563` `rendered_at=2026-08-31T09:55:09-05:00` `iterate_pin:true` `has_code_build:true` `researched_at=2026-08-26`. Pin text: *"ITERATE returns to stage 1 RESEARCH (1→8), not 5→8"*. **Bite against the incumbent:** repo-root `COSMOS_MASTER_DESCRIPTION.docx` mtime **2026-08-25 23:36** (21649 bytes) has `ITERATE` only as P6's name, **no** 1→8 pin, **no** `COMPETENCY.toml`, **no** `code-build`; `_fail_f21_f68_against_old.json` `all_new_pins_failed:true`. Then `tests/test_master_desc.py` **12/12**. Repo-root incumbent is **outside this fence** (write only `docs/`); leftover in `docs/BLOCKED_ITEMS.md` | Low | — |
| F-69 | `cosmos_dispatch` / `cosmos_collector` verified + hardened against their critiques | `BACKLOG.md:42-48` | **DONE — collector HIGH closed; H6 claude-CLI live-proven 2026-08-31T18:42Z** | Collector H1–H4 are in the code, not the 2026-08-25 critique: `parse_dhx_markers` / `correlate_marker`, summary grouped by agent (not lane), `index.jsonl.lock`, resolver queue identity. **This pass ran** `tests/test_collector.py` **71/71** including H1/H2/H3/H4 pins. Live `live/state/collector/dhx.json` `markers=173` `matched=167` `missing=6`; `docs/COLLECTOR.md` has `## DHx assignment ↔ result`. Dispatch H1 (no `V:\Ai\_queue` default; native queue is resolver role) is pinned in `tests/test_dispatch.py`. **H6 leftover closed 18:42Z:** claude-family CLI is live-proven through this harness. Live `cosmos/_f69_h6_live.json` `ok:true` `tree_id=KMesh-COSMOS-live` `dispatch_kind=claude` `job_rc=0` `result_rc=0` `stdout_pong:true` `through_harness:true` `secs=21.0` (PONG). Bite `_fail_f69_h6_against_old.json` **6/6 FAIL** `all_new_pins_failed:true` on `_delme/predispose_f69_h6_20260831T184200Z/`. Then `tests/test_dispatch.py` **139/139**; `tests/test_dispatch_jobs.py` **49/49**; callers workspace **41/41**, dispatcher **39/39**, motif **62/62**. Hermetic `_f69_h6.json` `ok:true` `claude_kind_live=proven` `cursor_kind_live=UNPROVEN` `cursor_missing_key=NO_KEY`. Cursor Cloud Agents was not launched (no key chase). Motif 1–2 is `docs/` research, outside this fence. The critique files themselves are historical | Med | — |
| F-70 | The working tree is **committed** | `CHANGELOG…:688-693` | **PARTIAL — commits flowing; working tree still dirty** *(re-measured 2026-08-31T14:51Z)* | The ABSENT cell was stale. Commits had been **IMPOSSIBLE** since 2026-08-25 because a zero-byte `.git/index.lock` from that day made every commit fail; it was cleared at 04:49. **This pass ran** `git log --oneline` HEAD **`4b22290`** `GBW hour 3: cdeck reds cleared structurally, F-29 closed, tools/ composed` (2026-08-31 09:00:38 −05:00). Since the lock cleared: `8ffeb97` 05:21 cc_driver GBW engine · `c5e8e75` · `10b2034` · `dbaf2ef` · `7745d71` · `4b22290`. `.git/index.lock` is **absent**. `git grep -c "compose_rails" HEAD -- cosmos/cosmos_kernel.py` → **4** (F-23 is in HEAD, not only the working tree). **Still dirty:** `git status --porcelain` → **51 modified, 58 untracked** (109 porcelain lines). A later `checkout` can still drop uncommitted work; it cannot drop `4b22290`. Remaining commit is Keith's call. Named in `docs/BLOCKED_ITEMS.md` | **Highest** | XS |

---

## 2. Roll-up

Counted mechanically from the tables above (`grep -E "^\| F-[0-9]+ \|"` → 70 rows), tallied on
the **primary** label in each status cell.

**Re-audit delta, 2026-08-31T18:35Z (backup+probe fence):** **None of F-09 / F-15 / F-36 / F-39 / F-60 / F-69 fall in this fence.** Job wired R2 into the registered 03:00 `COSMOS Mount Offsite Push`. Live r2 target `state=PUSHED` `readback_verified=2` `bucket=ai-dchambers` `prefix=src/20260831T183424`. Fail-old **5/5 FAIL**; `test_mount_clock.py` **39/39**. Local dest `D:\COSMOS_BACKUP` receives sets; last refusal `COPY_HASH_MISMATCH` on `builds/cvm-dt/F21_VOSK_REUSE.json` is another session writing that dir mid-copy. **Primary-label counts do not move.** In-fence of the six: **0**.

**Re-audit delta, 2026-08-31T18:21Z (backup+probe fence):** **None of F-09 / F-15 / F-36 / F-39 / F-60 / F-69 fall in this fence.** From the code: F-09/F-15 leftover is `builds/cvm-dt/` (forbidden); F-36 leftover is `cosmos_motif_driver.py:453` `"authority": "markdown"` at **58/96** `flip_ready:false` (`builds/probe/_f36_judgement.json`); F-39 leftover is `cosmos_codex_rail.py` has zero `# -----` banners (do not invent); F-60 leftover is `builds/health/test_cosmos_health_watchdog.py` `subprocess.run` of the watchdog `--once` (native schtasks); F-69 leftover is `cosmos_dispatch.py` `KIND_LIVE` cursor/claude `UNPROVEN`. **Backup fixes re-measured:** (a) live daemon lock `live/logs/cdeck_feed.lock` **exists**, `iter_files` **19194** `locks_in_scope=0` `kind=ok` not `SOURCE_UNREADABLE`; dest `D:\COSMOS_BACKUP\COSMOS-20260831T172140` **16205 files / 7698536901 bytes** `lock_files=0` `live_config_files=0`; fail-old **2/2 FAIL** old `SOURCE_UNREADABLE` on the lock; `test_local_clock.py` **42/42**. (b) gdx/builds **PUSHED** `_gdx_builds_push.json` `ok:true` `file_count=16781` `total_bytes=7664839452` `cacert kind=public`; planted `signing.key` `SECRETS_IN_SCOPE`; fail-old **2/2 FAIL**; `test_cosmos_backup.py` **115 OK, 1 skipped**. F-48 evidence cell updated. **Primary-label counts do not move** (F-48 stays DONE (code)). Buildable rows still open in this fence: **0**.

**Re-audit delta, 2026-08-31T18:12Z:** F-39 leftover **closed (dispatch `# BTS compatibility lane accounting` seam)**. Live `_f39_lanes_split.json` `ok:true` `disp_lines=1715` (was 1846 / 73741 bytes) `lanes_lines=214` `measure_same:true` `pick_same:true`; bite **9/9 FAIL**; new suite **34/61** on unsplit then `test_dispatch_lanes.py` **61/61**; callers dispatch **137/137**, jobs **49/49**, critique **51/51**, workspace **41/41**, dispatcher **39/39**, motif **62/62**, watchdog2 **43/43**. F-39 **stays PARTIAL**. **Primary-label counts do not move.** In-fence of the six still open: F-36, F-39, F-69.

**Re-audit delta, 2026-08-31T18:05Z:** F-39 leftover **closed (dispatch `# stage-5 critic visibility` seam)**. Live `_f39_critique_split.json` `ok:true` `disp_lines=1846` (was 2026 / 80388 bytes) `crit_lines=259` `compose_same:true` `is_critique_same:true`; bite **9/9 FAIL**; new suite **28/51** on unsplit then `test_dispatch_critique.py` **51/51**; callers dispatch **135/135**, jobs **49/49**, workspace **41/41**, dispatcher **39/39**, motif **62/62**. F-39 **stays PARTIAL**. **Primary-label counts do not move.** In-fence of the six still open: F-36, F-39, F-69.

**Re-audit delta, 2026-08-31T17:55Z:** F-39 leftover **closed (dispatch `# job source` seam)**. Live `_f39_jobs_split.json` `ok:true` `disp_lines=2026` (was 2462) `jobs_lines=516` `render_same:true`; bite **8/8 FAIL**; `test_dispatch_jobs.py` **49/49**; callers dispatch **133/133**, workspace **41/41**, dispatcher **39/39**, motif **62/62**. F-39 **stays PARTIAL**. F-36 re-measured **58/96** `flip_ready:false` `restraint_justified:true` `writes_authority_flip=0`. **Primary-label counts do not move.** In-fence of the six still open: F-36, F-39, F-69.

**Re-audit delta, 2026-08-31T17:51Z:** **None of F-09 / F-15 / F-36 / F-39 / F-60 / F-69 fall in this fence.** Job pinned unexercised docstring/KINDS claims: LEDGER_REFUSED is a runtime wrap (TORN/BROKEN_CHAIN/FORGED), handle_post torn is 400, jukebox JOB_DONE/STALE of a never-submitted id invents nothing. Bite **6/6 FAIL** `control_still_green:true`; live `_unexercised_r5_live.json` `ok:true` `tree_id=KMesh-COSMOS-live` `records=1092` `hmac_verified:false` `node_count=16` `clock_count=37`; then spend **60/60**, jukebox **54/54**, create **65/65**. `remeasure_probes.py --check` `stale: []`. **Primary-label counts do not move.** In-fence PARTIAL remaining: **F-09** (`builds/cvm-dt/`). Buildable rows still open in this fence: **0**.

**Re-audit delta, 2026-08-31T17:40Z:** **None of F-09 / F-15 / F-36 / F-39 / F-60 / F-69 fall in this fence.** Job pinned unexercised docstring claims: lying stamped `age_s` ignored (fleet/nodemap/heartbeat) and jukebox CLAIMED is QUEUED-only. Bite **5/5 FAIL** `control_still_green:true`; live `_unexercised_r4_live.json` `ok:true` `tree_id=KMesh-COSMOS-live` `records=1092` `hmac_verified:false` `node_count=16` `clock_count=37`; then fleet **64/64**, nodemap **60/60**, jukebox **52/52**, create **65/65**. **Primary-label counts do not move.** In-fence PARTIAL remaining: **F-09** (`builds/cvm-dt/`).

**Re-audit delta, 2026-08-31T17:25Z:** F-11 leftover **closed (live `/cdeck/` byte-equal to disk)**. Resident process had reloaded; stale `CORE_CDECK_PROBE.json` still said signed `/cdeck/` **404** seq 1444. Fresh probe `ok:true` seq **1547** five-file shell **200** `match_disk:true`; bite **15/15 FAIL** on the 404 incumbent; `test_core_cdeck.py` **25/25**. F-11 **PARTIAL → DONE**. **DONE 55→56, PARTIAL 12→11.** In-fence PARTIAL remaining: **F-09** (`builds/cvm-dt/`).

**Re-audit delta, 2026-08-31T16:30Z:** Job 390 re-filed `MAX_TURNS_WITH_OUTPUT` → `timed_out/` (`cc-infra` `failed=0`). F-43 leftover **closed (identity is content, not existence)**. Bite `all_bite:true` old mismatch `VERIFIED` + created a set; fail-old **6/6 FAIL**; live `_f43_identity_live.json` `IDENTITY_MISMATCH` `sets=[]` then match `VERIFIED`; `test_local_clock.py` **31/31**; live `--preflight` `NO_CONFIG`. F-43 **PARTIAL → DONE (code) / dest+VSS BLOCKED / not scheduled**. **DONE 54→55, PARTIAL 13→12.** In-fence buildable remaining of the eight: **0**.

**Re-audit delta, 2026-08-31T16:25Z:** F-05 leftover **closed (FEATURE_MASTER cell)**. Phone drag already shipped (17th); the cell still said static list / drag OFF ≤640px. Fresh `MOBILE_PROBE.json` `label=AFTER-F05-2026-08-31T1625Z` `tree_id=KMesh-COSMOS-live` `probed_at_epoch 1788193556.8032436` 320 `phoneWrote:true` `desktopUnchanged:true` `firstNodePosition=absolute` `nodesOutsideStage=0`. Bite **8/8 FAIL** on list-mode predecessor; shipped **115/115** + **55/55**. F-05 **PARTIAL → DONE**. **DONE 53→54, PARTIAL 14→13.**

**Re-audit delta, 2026-08-31T16:19Z:** **No in-fence PARTIAL remains buildable.** Job pinned unexercised refusals: `seal()` of a non-object was `AttributeError`; `scan_secrets` of a malformed manifest was `KeyError`/`TypeError` or **silent `[]`** (`files` a string). `classify_pause([])` was `AttributeError` (docstring says HOLD). Bite `all_bite:true`; fail-old backup **8/8 FAIL** + probe **3/3 FAIL**; then backup **90 OK, 1 skipped**, r2 **43/43**, local clock **25/25**, resession **48/48**. Could not pin `CLOSE_REFUSED`. **Primary-label counts do not move.** In-fence PARTIAL remaining: **3**, **zero buildable**.

**Re-audit delta, 2026-08-31T16:16Z:** F-53 leftover **closed (PARALLEL drives MOTIF)**. Fail-old **6/6 FAIL** `old_dropped=0`; then `test_prepaid_orch.py` **24/24**; live dry-run `writes:0` `tree_id=KMesh-COSMOS-live`. `--install-task` not run. F-53 **PARTIAL → DONE (code) / not scheduled**. **DONE 52→53, PARTIAL 15→14.**

**Re-audit delta, 2026-08-31T16:12Z:** **No in-fence PARTIAL remains buildable** (F-41 COW ledger, F-43 dests/VSS Create, F-54 dest/cred+register). Job pinned unexercised freeze refusals: handle missing `info()` was `AttributeError`; `BAD_FREEZE` / `FREEZE_DEST_OCCUPIED` were documented and raised but unnamed in tests. Bite `all_bite:true`; fail-old **2/2 FAIL**; `test_cosmos_backup.py` **80 OK, 1 skipped**. **Primary-label counts do not move.** In-fence PARTIAL remaining: **3**, **zero buildable**.

**Re-audit delta, 2026-08-31T16:04Z:** F-43 P0 **clock vehicle closed.** `--plan-task` emits `COSMOS Bulletproof Backup` daily 04:00 `registers:false`; live `--preflight` `NO_CONFIG`; bite `all_bite:true`; fail-old **5/5 FAIL**; `test_local_clock.py` **22/22**. F-43 **stays PARTIAL** (dests / VSS). F-36 streak re-measured **51/96**. **Primary-label counts do not move.** In-fence PARTIAL remaining: **3** (F-41, F-43 dests/VSS, F-54 dest/cred + register).

**Re-audit delta, 2026-08-31T15:56Z:** F-36 unnamed restraint **named, not flipped.** Live `_f36_judgement.json` `consecutive_agreements=50` `flip_ready:false` `restraint_justified:true` `restraint_is_excuse:false` `clock_alive:true`. Work order 2.1a filed in `CORE_RESTRUCTURE.md` (Keith/COW lands the flip after 96). Bite `all_bite:true`; fail-old **5/5 FAIL**; `test_f36_judgement.py` **22/22**; freshness **32/32**. 2.3 "no artifact" cell was STALE. F-36 **stays PARTIAL**. **Primary-label counts do not move.** In-fence PARTIAL remaining: **3** (F-41, F-43 dests/VSS Create, F-54 dest/cred + register).

**Re-audit delta, 2026-08-31T15:43Z:** F-54 leftover **closed (clock vehicle)** — `--plan-task` emits `COSMOS State Offsite Push` daily 03:15 `registers:false`; bite `all_bite:true`; fail-old **5/5 FAIL**; `test_state_offsite.py` **25/25**. Live `--preflight` still `NO_OFFSITE_ROUTE` payload **340044**. `--install-task` not run. F-54 **stays PARTIAL**. Operator leftovers not chased. F-41 `--apply` not run. **Primary-label counts do not move.** In-fence PARTIAL remaining: **3** (F-41, F-43 dests/VSS Create, F-54 dest/cred + register).

**Re-audit delta, 2026-08-31T15:22Z:** F-43 gap 3 freeze seam **CLOSED (code)** — `FrozenTree` live `frozen_survived:true`; VSS `--probe` `V:\` NTFS `VSS_UNAVAILABLE` `scode=0x80041014`; bite TypeError on predecessor; 4/4 FAIL then `test_cosmos_backup.py` **77 OK, 1 skipped**. F-41 `--apply` still `LIVE_LEDGER_FORBIDDEN` ledger **661088** untouched. `test_artifact_freshness.py` **31/31** `live_matched:11`. Operator leftovers not chased. **Primary-label counts do not move.** In-fence PARTIAL remaining: **3** (F-41, F-43 dests/VSS Create, F-54).

**Re-audit delta, 2026-08-31T15:00Z:** F-28 **PARTIAL → DONE (unverified rows filed)** — 15 HANDS stems mapped as `possessed=false rating=0`; census `unmapped_count=0` `node_count=21`; pick still G46/SGH/DOM; `test_f28_competency_map.py` 14/14; `test_competency.py` 31/31. Stale claim artifacts restamped (`test_artifact_freshness.py` 30/30 `live_matched:10`). F-41 live `--apply` still `LIVE_LEDGER_FORBIDDEN` ledger **643712** untouched; F-54 `NO_OFFSITE_ROUTE` payload **324562**. Operator leftovers not chased. **DONE 46→47, PARTIAL 16→15.**

**Re-audit delta, 2026-08-31T14:55Z:** Five ABSENT cells were stale, not open.
F-70 **ABSENT → PARTIAL** (commits flowing since lock cleared 04:49; HEAD
`4b22290`; porcelain 51/58 dirty). F-53 **ABSENT → PARTIAL** (prepaid
satellite CLOCKS 24 exists; `--engine gbw` is a builder, not a second
orchestrator). F-21 **ABSENT → DONE (code)** (`cosmos/_f21_stt_probe.json`
`ok:true` `engine=vosk`; BENCH still UNMEASURED in cvm-dt). F-56
**ABSENT → DONE (code) / BLOCKED (hosts)** (`LAN_NODES` SRV1/T7
`kind=NO_HOST`). F-68 **ABSENT → DONE** (`docs/COSMOS_MASTER_DESCRIPTION.docx`
`iterate_pin:true`). F-23 UNCOMMITTED note cleared (`compose_rails` count
**4** in HEAD). F-61 clocks **23→24**. **DONE 43→46, PARTIAL 14→16,
ABSENT 10→5.**

**Re-audit delta, 2026-08-31T14:22Z:** Every unblocked in-fence infra row is
DONE or parked. Job pinned **11** unexercised refusals (backup 7 + probe 4);
could not pin `CLOSE_REFUSED`. Bite `_bite_unpinned_round4.json` both
`all_bite:true`; fail-old 7/7 + 4/4. Suites 41/41, 39/39, 27/27, 6/6,
33/33. **Primary-label counts do not move.**

**Re-audit delta, 2026-08-31T14:12Z:** F-26 **PARTIAL → DONE (code) / not scheduled**
(CLOCKS id 23; this-fence GitHub-link parser live `MINED` 29/20 `writes=0`;
`test_newai_scout.py` 24/24). F-31 **PARTIAL → DONE (code) / not scheduled**
(CLOCKS id 20). F-65 **PARTIAL → DONE (code) / not scheduled** (CLOCKS ids
21/22). F-43 gap 4 closed (`SECRETS_IN_SCOPE`; 2/2 FAIL on predecessor;
`test_cosmos_backup.py` 63 OK + 1 skip). F-28/F-30/F-41/F-54 stay PARTIAL
with precise blockers in `docs/BLOCKED_ITEMS.md`. F-61 clocks **19→23**.
**DONE 40→43, PARTIAL 17→14.**

**Re-audit delta, 2026-08-31T13:53Z:** FOLLOW leftover closed in `cosmos/`
for the two remaining high-frequency zero-id writers COSMOS already
emits: `BACKUP_VERIFIED.node=sentinel.system` (`COSMOS`) and
`COMMAND_HANDLED`/`COMMAND_REFUSED.node=CVM`. Clock and CLI thread the
resolver identity. Bite 11/17 + 2/54 + 5/5 FAIL on predecessor; then
17/17 + 11/11 + 54/54 + 14/14. Hermetic `_f_backup_command_follow.json`
`ok:true`. Live HEALTH_BOARD still lacks `node` until `serve` reloads
(F-11). **Primary-label counts do not move** (FOLLOW is not an F-row;
it unblocks cDeck FOLLOW harvest + BACKUP map pulse).

**Re-audit delta, 2026-08-31T13:54Z:** F-51 P1.3 prompt leftover closed
(`docs/AUTO_RESESSION_PROMPT.md` 1133 bytes sha256 `5d10d8ff…`; live
`--dry-run` `_f51_prompt_live.json` `prompt_sha=5d10d8ff…` `IDLE`
`KMesh-COSMOS-live` `writes:0`; `test_resession.py` 39/42 then 45/45).
Then 8 unexercised-refusal pins (backup 4/4 + probe 1/1 FAIL against
old; pack dest-is-file was untyped `FileExistsError`). Operator leftovers
not chased. **Primary-label counts do not move.**

**Re-audit delta, 2026-08-31T13:26Z:** claim-artifact freshness gate
(`describes` bytes+sha256 on 10 FEATURE_MASTER-cited artefacts;
`test_artifact_freshness.py` 30/30; bite `all_bite:true`; 10/10
UNFINGERPRINTED on staged incumbents). Stale evidence numbers
re-measured (F-40/F-41/F-44/F-54). Operator leftovers not chased.
**Primary-label counts do not move.**

**Re-audit delta, 2026-08-31T13:22Z:** FOLLOW leftover closed in `cosmos/`
(`HEALTH_BOARD.node=sentinel.system=COSMOS`; `_f_health_follow.json`
`ok:true`; follow suite 11/11 + 7/7; 3 new pins FAIL on predecessor).
F-24 `tests/` leftover already patched (`len(WIRED_IDS)`). F-66
**UNMEASURED → DONE (code)** (`test_grok_gem_bucket_workers.py` 58/58,
`NO_DEST`). F-69 collector HIGH closed (71/71 + live `dhx.json` 173/167/6);
dispatch H6 remains so F-69 **stays PARTIAL**. Live Core HEALTH_BOARD
still lacks `node` until `serve` reloads (F-11). **DONE 39→40,
UNMEASURED 1→0.** (F-29's 38→39 was already in the 13:10Z delta; the
roll-up table had lagged.)

**Re-audit delta, 2026-08-31T13:12Z:** F-60 leftover closed for the two
`tests/` suites (`cosmos_test_guard` + wrap; 6/6 + 38/38 + 51/51).
F-60 **stays PARTIAL** (`builds/health/` + `schtasks`). **Primary-label
counts do not move.**

**Re-audit delta, 2026-08-31T13:10Z:** F-29 **PARTIAL → DONE (code)**
(repo-root `tools/` + Kernel `tools-surface` compose; live
`cosmos/_f29_composed_live.json` `ok:true`
`openai-docs-mcp` / `xai-docs-mcp` http=200; `test_kernel.py` 21/21;
`test_boot_attach.py` 21/21; `test_boot_rails.py` 12/12; 4/4 FAIL on
predecessor). Further tools are F-30. **DONE 38→39, PARTIAL 18→17.**

**Re-audit delta, 2026-08-31T12:48Z:** F-55 **PARTIAL → DONE (code)**
(hash-chain + writer HMAC + `cosmos_lock` fenced send; Kernel composed;
`test_cosmos_mail.py` 23/23; `test_kernel.py` 18/18; 8/8 FAIL on
predecessor). GrokBot participant stays F-53. **DONE 37→38, PARTIAL 19→18.**

**Re-audit delta, 2026-08-31T12:46Z:** F-43 in-fence leftover closed
(`SOURCE_MUTATED` + `do_retire`; `test_cosmos_backup.py` 51 OK + 1 skipped;
bite `all_bite:true`; 10/10 FAIL against predecessor; live
`_f43_mutate_retire_live.json` `ok:true`). F-43 **stays PARTIAL**. Remaining
slices named in `docs/BLOCKED_ITEMS.md`. **Primary-label counts do not move.**

**Re-audit delta, 2026-08-31T12:34Z:** verification hardening only.
`STAGE_OCCUPIED` / `RESTORE_HASH_MISMATCH` / `REHEARSAL_HASH_MISMATCH` /
`SOURCE_NOT_DIR` / `NOT_A_BACKUP_SET` pinned (`test_cosmos_backup.py` 39 OK
+ 1 skipped; bite `all_bite:true`; 5/5 FAIL against predecessor). **Primary-label
counts do not move.**

**Re-audit delta, 2026-08-31T12:28Z:** F-40 leftover closed (taxonomy regen is
clock-collected; `test_refusal_taxonomy.py` 26/26; live tick MATCH 49/128).
F-63 live `--dry-run` re-measured: default scan dirs `MINED` 2555/252,
heartbeat still absent. **Primary-label counts do not move.**

**Re-audit delta, 2026-08-31T12:40Z:** F-33 **ABSENT → DONE** (signed
`GET /api/v1/status` 200 `KMesh-COSMOS-live` seq 1270; board `GREEN`
`serve_8770.ok`). F-34 **PARTIAL → DONE** (`health_clock_heartbeat.json`
`serve_supervisor.kind=ALREADY_UP`). F-27 **PARTIAL → DONE (code)**
(`cosmos_competency.pick`; `pick_agent` → `SGH/grok` on web-research;
`test_competency.py` 31/31). Premise 4 clocks **18 → 19**. **DONE 31→34,
PARTIAL 22→20, ABSENT 12→11.**

**Re-audit delta, 2026-08-31T12:18Z:** F-63 **PARTIAL → DONE (code) / not scheduled**
(`cosmos/cosmos_askmine.py` CLOCKS id 19; `test_askmine.py` 66/66; live
`--dry-run` `NO_TRANSCRIPT`; WD2 third source `askmine`). F-61 **18 → 19**
clocks (does not change the F-61 primary label). FOLLOW emit re-verified
10/10. **DONE 30→31, PARTIAL 23→22.**

**Re-audit delta, 2026-08-31T12:45Z (cdeck):** F-16 **PARTIAL/`PENDING_CORE` → DONE (gated)**
(`STAGE6_SPLIT.json` local PASS 11, core PASS 4, `PENDING_CORE:0`). F-17
**BLOCKED-on-F-33 → DONE (gated)** (`STAGE6_GATE.json` `ok:true`,
`STAGE6_CORE.json` `verdict=PASS`; F-33 is DONE). F-59 **ABSENT → DONE**
(`cc_outcome.classify` `TIMED_OUT_WITH_OUTPUT`; `test_cc_outcome_evidence.py`
**28/28**). F-14 re-gated (`emitted cdeck:KMesh-COSMOS-live:1272:…`).
**DONE 34→37, PARTIAL 20→19, ABSENT 11→10, BLOCKED 4→3.**

**Re-audit delta, 2026-08-31T11:57Z:** F-47 leftover closed (`ADAPTERS["r2"]()` is
typed `NO_CREDENTIALS`, `do_rehearse_target` Gate B, `__pycache__` excluded;
`test_cosmos_backup_r2.py` 35/35; live `_f47_live_adapter.json`). F-41 stays
PARTIAL; UNPLANNED cards closed (`_f41_unplanned_cards.json` 116 HOLD,
`disposition:null`; 19/19). F-46 still BLOCKED. **Primary-label counts do not
move.**

**Re-audit delta, 2026-08-31T11:30Z:** F-41 **ABSENT → PARTIAL** (`test_tool_disposition.py`
16/16; live `_f41_proposals.json` apply_ready 27; `--apply` on authority.jsonl is
`LIVE_LEDGER_FORBIDDEN`, ledger 548417 bytes unchanged). F-54 stays PARTIAL; the
in-fence leftover (named payload packer) closed (`test_state_offsite.py` 17/17;
live `_f54_live_preflight.json` `NO_OFFSITE_ROUTE` `payload.present=4`). Counts
below updated for F-41 only.

**Re-audit delta, 2026-08-31T11:30Z:** F-51 **PARTIAL → DONE (code) / not scheduled
/ prompt unfiled** (`cosmos/cosmos_resession.py` CLOCKS id 18; `test_resession.py`
46/46; live `--dry-run` `IDLE` `KMesh-COSMOS-live`). F-61 **17 → 18** clocks
(does not change the F-61 primary label). **DONE 29→30, PARTIAL 23→22.**

**Re-audit delta, 2026-08-31T11:14Z:** F-48 **DONE (code) / dest unconfigured → DONE (code) /
dest unconfigured / not scheduled** (`test_mount_clock.py` 34/34; live preflight
`BLOCKED` `NO_CONFIG`; `--plan-task` emits, registers nothing). F-51 stays
PARTIAL; the in-fence leftover (`--plan-task`) closed (`test_resession.py` 36/36).
F-54 re-measured, unchanged. **Primary-label counts do not move.** *Superseded
on F-51 by the 11:30Z promotion.*

**Re-audit delta, 2026-08-31T11:05Z:** F-48 **ABSENT → DONE (code) / dest unconfigured**
(`test_backup_mounts.py` 31/31; live bind gdx/odx READY, es3 DRIVE_NOT_MOUNTED).
F-49 **STALE → DONE** (generated `CREDENTIALS_NEEDED.md` 2026-08-31T11:00:59Z, R2
row BLOCKED and wired). F-50 **PARTIAL → DONE (code)** (`open_doors` + `--open`,
42/42). Counts below updated for those three. F-29 remaining and F-41 unchanged.

**Re-audit delta, 2026-08-31T10:42Z:** F-29 **ABSENT → PARTIAL** (`builds/probe/tools/`
exists and live-bound; repo-root `tools/` still absent). F-47 **ABSENT → DONE (code) /
not scheduled** (`test_offsite_clock.py` 35/35; no live heartbeat). F-25 leftover in
`mesh_blockers` closed (does not change the F-25 cell, already DONE). F-41 re-measured,
unchanged. Counts below updated for F-29 and F-47 only.

**Re-audit delta, 2026-08-31T07:35Z:** F-44 **ABSENT → DONE** (the long-path fix has landed
in `cosmos/` and was re-proven by its own `behave` probe). F-25 stays ABSENT *for `cosmos/`* —
the fix is built, proven and diffed, but a proposal is not an implementation and does not lift
a row off ABSENT (the rule stated in §*How to read this*). F-41 re-measured, unchanged. The
counts below are updated for F-44 only. *Superseded on F-25 by the 03:10 slice and the
10:42Z leftover close — the table cell is the current truth.*

**Slice delta, 2026-08-31T03:10 −05:00 (the F-24/F-25 build):** both rows moved **ABSENT → DONE**,
and the proposal above became an implementation — `cosmos/cosmos_registry.py` now carries the
freshness filter and `cosmos/cosmos_rails_prober.WIRED_NODES` now carries all eight rails. Bound
to the live tree, not to a rc=0: `live/registry/rails.json` reads `count 7`, `proof_ttl_s 3600.0`,
`stale_count 1`. Counts below are **not** yet re-tallied for this delta (DONE 25→27, ABSENT 16→14);
the row cells are the current truth.

| Status | Count | Note |
|---|---|---|
| **DONE** | 46 | Previous 43 plus **F-21** cosmos_stt, **F-56** LAN_NODES, **F-68** docs/ render (14:55Z). Includes F-20 *DONE (code) / not running*, F-45 *DONE (code) / BLOCKED (credential)*, F-47 *DONE (code) / not scheduled*, F-48 dest unconfigured, F-50, F-51 CLOCKS 18, F-63 CLOCKS 19, F-33 Core `:8770`, F-34 supervising, F-27, F-16/F-17, F-59, F-55, F-29, F-66 |
| **PARTIAL** | 16 | **+1 F-70 commits flowing/tree dirty; +1 F-53 satellite not a parallel orchestrator** (14:55Z). Remaining in this fence: F-28 (competency pin), F-30 (wire WAVE A), F-41 (live ledger), F-43 (same-volume dest), F-54 (off-volume copy). Outside: F-05, F-09, F-11, F-15, F-36, F-39, F-57, F-60, F-69 |
| **ABSENT** | 5 | **−1 F-21; −1 F-53; −1 F-56; −1 F-68; −1 F-70** 14:55Z. Prior "10 including F-70 operational" was the lag this pass closed. Table ABSENT cells this fence owned are gone; the rollup 5 is the prior 10 minus those five |
| **BLOCKED** | 3 | Code complete; a credential or one elevated line Keith owns is the only gap. **−1: F-17** 12:45Z (was BLOCKED on F-33) |
| **STALE** | 0 | **F-49 closed** — regenerated 2026-08-31T11:00:59Z |
| **UNMEASURED** | 0 | **F-66 closed 2026-08-31T13:22Z** — dest contract measured 58/58 |
| **Total rows** | **70** | |

**The headline of this triage: ten rows are finished code held up by an operator action,
not by engineering** (was twelve; F-33 Core-up and F-34 supervising closed 2026-08-31T12:40Z).
Enumerated so the claim can be checked rather than taken. **F-48 dest-unconfigured is an
eleventh of the same shape** (Keith names `backup_targets.json`; the ES.3 is also
uninstalled) but is counted in DONE (code), same as F-47:

- **Built, not scheduled — one `schtasks` line each (8):** F-19 CVM DT clock · F-20 CVM DT
  voice · F-31 crit consumer · F-65 the two node bucket workers · F-47 the R2 offsite push
  (clock is proven, 35/35; `--plan-task` emits the line and registers nothing) · **F-48 the
  mount offsite push** (clock is proven, 34/34; dests still unconfigured, so the armed
  task would refuse `NO_CONFIG` until Keith names them — same shape as F-47/`NO_CREDENTIALS`) ·
  **F-51 auto-resession** (CLOCKS id 18; `--plan-task` emits `COSMOS Resession`
  minute/1 and registers nothing; **P1.3 prompt filed 2026-08-31T13:48Z** sha256
  `5d10d8ff…`; a missing file is still typed `NO_PROMPT`) · **F-63 askmine** (CLOCKS id 19, 66/66; `--plan-task` emits
  `COSMOS Askmine` HOURLY `--once` and registers nothing; empty scan is typed
  `NO_TRANSCRIPT`).
- **Built, dormant behind a deliberate opt-in (0):** F-34 left this bucket 2026-08-31T12:40Z
  (`serve_supervisor.kind=ALREADY_UP`). *F-51 left at 11:30Z when it landed in CLOCKS.*
- **Built, waiting on one file Keith owns (3):** F-32 OpenAI key · F-46 R2 credential ·
  F-57 the Slack webhook. *(F-49 the doc regeneration **closed** 2026-08-31T11:00Z.)*
- **Built, waiting on one command (1):** F-70 the working tree is still dirty
  (51 modified / 58 untracked) but commits have been flowing since the
  04:49 lock clear — HEAD `4b22290`. *F-33 left this bucket 2026-08-31T12:40Z —
  Core is serving `:8770`.*

The remaining shortfall is genuine engineering, and §4 ranks it.

---

## 3. Premises in the source documents that the code contradicts

Recorded rather than silently corrected, because a document that quietly fixes its own inputs
teaches nobody. Each of these was checked against the file, not inferred.

1. **`WISHLIST.md:64` — "the live registry is EMPTY."** It is not, and the doc already carries
   a dated inline correction. Confirmed again this pass: `live/registry/rails.json` `count: 4`.
   The real gap is F-24 (four answering rails with no prove path), not an empty registry.
2. **`WISHLIST.md:74` — "GEM and OA critique rails land EMPTY."** Partly stale. **Ten**
   different-family critique bodies exist under `docs/critique/` — five from `gem-api`, five
   from `oa-api`, 6,034–17,000 bytes, dated 2026-08-25 to 2026-08-27. What is genuinely not
   running is the *consumer* (F-31).
3. **`WISHLIST.md:81` — cDeck "defaults to `:8791` not the live `:8770`."** Stale.
   `builds/cdeck/ui/app.js:34` reads `var DEFAULT_URL = "http://127.0.0.1:8770";`, with the
   trial kernel named only in a comment at `:32`.
4. **`WISHLIST.md:32` — "the dozen COSMOS-own clocks."** There are **19** (F-61).
5. **`CREDENTIALS_NEEDED.md:229` — "`R2Target`, a declared seam, NOT implemented."** **Closed
   2026-08-31T11:00:59Z (F-49).** The regenerated file names `cosmos_backup_r2.py:137`
   `NO_CREDENTIALS` and the offsite-clock `--preflight`; the R2 row is **BLOCKED**, not
   PLANNED. The stale sentence is gone. Historical copies live under
   `_delme/predispose_CREDENTIALS_NEEDED_f49_20260831T055254Z/`.
6. **The 2,091 MAX_PATH blocker as originally filed** said `build_manifest` *"correctly raises
   `SOURCE_UNREADABLE`"*. Measured, it does not — the files never reach `build_manifest`, and
   the run ends with `BACKUP_VERIFIED` in the ledger (F-44). **The correction makes it worse,
   not better.**
7. **`CLOCK_POSTMORTEM.md` — "`cvm-dt-voice` had no daemon vehicle at all."** True when
   written, closed since: `cvm_dt_voice.py:80-81,952-955` now define the task names and build a
   real `plan_create` (F-20). It is still unregistered, which is a different fact.

---

## 4. WHAT TO BUILD NEXT — ranked

Ranked by **(what it unblocks) × (what it costs) ÷ (risk to the running fleet)**. The first
four are cheap and each one unblocks work that is otherwise stuck.

### Tier 0 — one operator action each, and each unblocks several rows

| Rank | Item | Why it is first | Fence |
|---|---|---|---|
| 1 | **F-70 — commit the remaining dirty tree** | Commits flow (HEAD `4b22290`; `compose_rails` is in HEAD). Still **51 modified / 58 untracked**. One command, and it is Keith's to give | git |
| 2 | ~~**F-33 + F-34 — bring Core up on `:8770`**~~ **BOTH LANDED 2026-08-31T12:40Z** | Signed `GET /api/v1/status` HTTP 200 `tree_id=KMesh-COSMOS-live` seq 1270; board `GREEN` `serve_8770.ok`; supervisor `ALREADY_UP`. Remaining on this process: F-11 `/cdeck/` 404 (reload) | `cosmos/` |
| 3 | **F-57 — drop `live/config/slack_webhook.txt`** | The P0 unattended-safe loop is built, running and hourly; it just cannot deliver (`"slack_ok": false`). Without it, "still running" costs Claude tokens instead of zero. One file | `live/config/` (Keith) |
| 4 | **F-31 + F-19 + F-20 + F-65 — register five built-but-cold daemons** | `crit_consumer`, `COSMOS CVM DT Clock`, `COSMOS CVM DT Voice`, and the two node bucket workers are all finished code with no scheduled task. Each is one elevated `schtasks` line. This is the cheapest capability-per-keystroke on the list | `schtasks` (Keith) |

### Tier 1 — real engineering, highest value

| Rank | Item | Why | Fence | Effort |
|---|---|---|---|---|
| 5 | ~~**F-44 — the MAX_PATH backup hole**~~ **LANDED 2026-08-31** | The scheduled backup omitted files and wrote `BACKUP_VERIFIED` anyway. **Closed:** `cosmos/cosmos_backup.py` and `cosmos_backup_clock.py` now measure `COVERS_LONG_PATHS` on 300/301-character fixtures (`builds/probe/_longpath_behaviour.json`, re-measured 2026-08-31T13:26:12Z with `describes`; the dated 07:27Z file is staged), 29 backup tests green. What is still open is the **scope**: `docs/R2_OFFSITE_PLAN.md` §5 points the backup at the 65 GiB trees where 2,143 long-path files live, and that run has not happened — see rank 6 | `cosmos/`, `builds/backup/` | — |
| 6 | **F-46 + F-47 + F-54 — get one copy off this machine** | The adapter is done and proven (F-45); **F-47 the R2 clock is DONE (code)** — `cosmos_offsite_clock.py`, 35/35. **`ADAPTERS["r2"]()` leftover closed 2026-08-31T11:57Z** — typed `NO_CREDENTIALS` not a stub; Gate B `do_rehearse_target` proven offline (`files_restored:2`). **F-48 path mounts AND their clock are now DONE (code)** — `cosmos_mount_clock.py`, 34/34. **F-54 payload packer + clock 2026-08-31T15:43Z** — `cosmos_state_offsite.py`, **25/25**; `--plan-task` emits `COSMOS State Offsite Push` daily 03:15 and registers nothing (`_f54_clock_plan_task.json`). Live preflight `BLOCKED` `NO_OFFSITE_ROUTE` payload present 4 / **340044** bytes. Remaining: Keith names dests (or the R2 credential, F-46) and one elevated `--install-task` on this clock (whitelist) and/or F-47/F-48 (scopes). The packed SEED/inflight/tracker then pushes with no code change | `live/config/` then `schtasks` (Keith) | XS |
| 7 | ~~**F-24 — wire the four answering rails** *(+ F-25, its pair)*~~ **BOTH LANDED 2026-08-31T02:56 −05:00** | It was never a credential problem: the registry was small because nobody asked. **Closed:** all four are in `WIRED_NODES` with a prove-shaped `live_call`, and the live projection went `count 4 → 7` with each new row naming the responder its vendor emitted (`grok-build-0.1` · `Cursor COSMOS 2` · `firecrawl/v2-research-papers` · `Playwright/1.63.0-alpha-2026-08-05`). F-25 was applied **first**, exactly as this row asked, so the new rails could not inherit the forever-verified bug — and it immediately bit the one row that had it: `claude-cli` moved to `stale`, `verified:false`, `age_s 320779`. **`tests/` leftover closed 2026-08-31T13:22Z:** `test_rails_prober.py` lists the eight wired `link_id`s; `test_boot_attach.py` pins `count == len(WIRED_IDS)` and `spent["n"] == len(WIRED_IDS)`. Remaining on this rank is `claude-cli` itself, which is F-32 (credential, Keith) | `cosmos/` | — |
| 8 | **F-15 — Keith's stated #1: CVM usability** *(F-21 inference bound in `cosmos/` 14:55Z)* | Rank 2 (Core `:8770`) **landed**. F-21 `cosmos/_f21_stt_probe.json` `ok:true` `engine=vosk`. Remaining: `BENCH_LATENCY.json` still records `transcribe.stt_model_inference` **UNMEASURED** (cvm-dt fence) and `respond.voice_post`. *"A usability claim with no number is an opinion."* | `builds/cvm-dt/` | M |

### Tier 2 — structural, high value, larger

| Rank | Item | Why | Fence | Effort |
|---|---|---|---|---|
| 9 | ~~**F-51 — ship auto-resession out of `builds/probe/`**~~ **PROMOTED 2026-08-31T11:30Z** · **P1.3 filed 2026-08-31T13:48Z** | **Closed in `cosmos/`:** CLOCKS id 18. **Prompt leftover closed in `docs/` (fence artifact):** `docs/AUTO_RESESSION_PROMPT.md` 1133 bytes sha256 `5d10d8ff510503a00b01d6a2b1efca7941ca92a10efc3aa1c6ed59082cfca8db`; live `--dry-run` `_f51_prompt_live.json` `prompt_sha=5d10d8ff…` `IDLE` `KMesh-COSMOS-live` `writes:0`; `test_resession.py` **45/45**. Remaining is operator: one elevated `--install-task`. Missing file is still `NO_PROMPT`. The 15s detached-daemon vehicle in the arch is a later thickening — the shipped vehicle is minute/1 `--once`, same as the clock plan | `docs/`, `schtasks` | — |
| 10 | **F-60 — finish the heartbeat fence** *(DONE 2026-08-31T18:35Z)* | Health `--once` child no longer spawns `schtasks.exe`: `cosmos_clock` honors `COSMOS_SCHTASKS_SANDBOX`; fence child env inherits it. Live `_f60_sandbox.json` health `unfenced_spawns=[]` `procs=2`. Bite **6/6 FAIL**. `test_live_write_fence.py` **23/23**. `builds/health/` was not rewritten. `builds/cvm-dt/` was not touched | `cosmos/` · `tests/` | — |
| 11 | ~~**F-55 — mailbox chain / writer sig / cosmos_lock**~~ **LANDED 2026-08-31T12:48Z** · ~~**F-53 PARTIAL**~~ **LANDED 2026-08-31T16:16Z (code) / not scheduled** | **F-55 closed in `cosmos/`.** **F-53 PARALLEL leftover closed:** COW-fresh tick drops one MOTIF work-order (flood-guarded). `test_prepaid_orch.py` **24/24**. `--engine gbw` is still a builder, not this row. Remaining is Keith's `--install-task` | `schtasks` | — |
| 12 | ~~**F-27 — give `COMPETENCY.toml` a consumer**~~ **LANDED 2026-08-31T12:40Z** | **Closed in `cosmos/`:** `cosmos_competency.pick`; WD2 `pick_agent` → live `web-research=SGH` `code-build=G46`; `tests/test_competency.py` **31/31**. GEM/OA/DOM stay out of default `DISPATCHABLE` until their workers/kinds are live (F-65) | `cosmos/` | — |
| 13 | ~~**F-63 — session-transcript mining**~~ **PROMOTED 2026-08-31T12:18Z** | **Closed in `cosmos/`:** CLOCKS id 19, `tests/test_askmine.py` **66/66**, WD2 third source `askmine` → `live/state/askmine/UNANSWERED.md`. **Live default-scan `--dry-run` re-measured 12:28Z:** `MINED` `transcripts_seen=2555` `findings=252` `dry_run:true` (`builds/probe/_f63_live_dryrun.json`); heartbeat still absent. Remaining is operator: one elevated `--install-task`. Probe copy stays under `builds/probe/`. Keith's Cowork transcripts are still not on this host (the detector cannot invent them) | `cosmos/` | — |
| 14 | ~~**F-03 + F-11 — the two one-route Core changes cDeck is waiting on**~~ **F-03 gated 2026-08-31; F-11 on disk, live restart left** | F-03 write route was already live; the missing `tests/` suite is now `tests/test_spend_post.py` **5/5**. F-11 same-origin shell is on disk (`_CDECK_ROUTES`, `tests/test_cdeck_shell.py` **10/10**) — Core **is** serving (F-33) but signed `GET /cdeck/` is still **HTTP 404 `NOT_FOUND`** (`served_at` 1788179666.85, seq 1270). Remaining operator action: restart `serve` so the resident process loads `_CDECK_ROUTES` | `cosmos/` | S — restart |
| 15 | **F-59 — classify a timeout separately from a failure** | Small, and it fixes the queue's own honesty: a job that produced everything and ran long is currently filed identically to one that produced nothing | `builds/cc_driver/` | S |

### Tier 3 — worth doing, not urgent

~~F-14 (re-run the cDeck stage-6 gate)~~ **DONE 2026-08-31T06:17** (`emitted
cdeck:KMesh-COSMOS-live:1166:1788175256.923605:b1f86359…f4706`; PWA files now
hashed) · ~~F-49 regenerate
`CREDENTIALS_NEEDED.md`~~ **DONE 2026-08-31T11:00Z** · ~~F-50 open the credential
window~~ **DONE (code) 2026-08-31T11:01Z** ·
~~F-05 (cDeck drag on mobile)~~ **DONE 2026-08-31T16:25Z** (`MOBILE_PROBE.json` `phoneWrote:true` `desktopUnchanged:true`) · F-09 (real CVM session control leftover is CVM-DT; **F-13 PWA closed DONE
and re-measured 2026-08-31T06:17** — `builds/cdeck/PWA_PROBE.json` cache
`cdeck-shell-v3`, 28 `/api` in 12s, 0 cached) · F-69 (satisfy the
collector/dispatch critiques rather than pointing at heartbeats) · F-26/F-28/F-30
(scout, manuals, maker wiring) · ~~**F-29 `tools/` prototype**~~ **PROMOTED 2026-08-31T13:10Z** — repo-root `tools/` + Kernel `tools-surface` compose; live `_f29_composed_live.json` `openai-docs-mcp` / `xai-docs-mcp` http=200 ·
F-36/F-39 (Phase 2 derivation audit, Phase 4 splits) · ~~F-40 leftover (taxonomy regen was a hand step)~~ **CLOSED 2026-08-31T12:28Z** — `builds/probe/test_refusal_taxonomy.py` 26/26, clock-collected, `--out` not `>` · ~~F-48 (ES.3/GDX/ODX targets)~~
**DONE (code) 2026-08-31T11:04Z** — dest unconfigured, ES.3 not installed ·
~~F-56 (federation)~~ **DONE (code) / BLOCKED (hosts) 14:55Z** — `LAN_NODES` SRV1/T7 `NO_HOST` · ~~F-41 (135 undecided tools)~~ **PARTIAL 2026-08-31T11:29Z** —
proposer built, 27 apply-ready, live ledger not written (`LIVE_LEDGER_FORBIDDEN`);
**UNPLANNED cards 2026-08-31T11:56Z** — `_f41_unplanned_cards.json` 116 HOLD
(`disposition:null`, 47 with name-overlap evidence); rulings still COW/`cosmos/` ·
~~F-68 (master description re-render)~~ **DONE 14:55Z** `docs/COSMOS_MASTER_DESCRIPTION.docx` `iterate_pin:true`.

---

## 5. What this document does **not** claim

- **It does not claim completeness of the *sources*.** It swept `docs/*.md`,
  `docs/contracts/`, `docs/critique/`, `docs/research/` (by filename), and `builds/*/*.md`
  excluding `node_modules/` and `_delme/`. Features discussed only in a session transcript, a
  Slack message, or an agent return that never reached a `.md` are **not** here — which is
  precisely the gap F-63 exists to close. **Partly closed 2026-08-31:** the transcript half
  has now been mined once — `docs/UNANSWERED_ASKS_2026-08-31.md` lists 28 distinct
  requirements that workers said in their own words they did not do, none of which had
  reached a `.md`. Slack and agent returns remain unswept.
- **It does not re-run the whole gate.** The 100/100 figure is the scheduled clock's own fresh
  artifact, not a hand-run by this pass.
- **Every heartbeat-age claim inherits the F-60 caveat**: until the test suites are fenced out
  of `live/logs/`, a fresh heartbeat is a signal producible by something other than the daemon
  it names.
- **Effort column is a sizing judgement** (XS/S/M/L), not a measurement, and is labelled as
  such. Every *status* is measured; every *ranking* is an argument.
