
---

## 2026-08-31 — F-33 + F-34 CLOSED: Core is serving the REAL root on :8770

**The ~83,000 REDs had two causes, and neither was the one the backlog assumed.**
Measured, not inferred.

**Cause 1 — a green scheduled task watching the wrong tree (the rc=0 scar).** The only
task that starts Core, `\COSMOS_Serve_Watchdog` (every 2 min, `Last Result: 0`), runs an
OUT-OF-TREE script `V:\Ai\BTS_MESH\cosmos_watchdog.py` that hard-codes
`ROOT = ...\trylive`, `PORT = 8791`. It has been keeping the TRIAL Core alive and
reporting success. Measured side by side: :8791 serves `tree_id KMesh-COSMOS-try`
(ledger seq 2290); :8770 serves `KMesh-COSMOS-live` and was dead. A task returning rc=0
forever is not evidence that the right thing is running. It also violates *no hard-coded
paths* and lives outside the repo tree.

**Cause 2 — the supervisor was written, complete, and never switched on.**
`cosmos_health_clock._supervise_serve` was gated behind an opt-in `--supervise` that the
registered action never passed (`... --root ...\live --loop`, no flag). Heartbeat
artifact at kill time: **89,217 polls, `verdict: RED x1`, `serve_supervisor: null`, zero
spawns.**

**Fix — `cosmos/cosmos_health_clock.py`.** `--supervise` now DEFAULTS ON
(`argparse.BooleanOptionalAction`; `--no-supervise` opts out); `poll_once` / `loop` /
`standup` defaults flipped to `True`; `standup()` now writes the flag into the task action
EXPLICITLY instead of relying on a default — relying on a default is exactly how this
stayed dormant. Default-ON was chosen over a config toggle so the fix needs **no SCHTASKS
re-registration**: the existing action supervises the moment the process reloads the file.
Spawn lock, 15→300 s backoff ladder, `CHILD_ALIVE` no-second-writer refusal and
`PAUSED_HOLD` are unchanged.

**Runtime binding — the proof, not the intention.**
- Killed stale clock pid 18636 (89,217 polls). The UNCHANGED 1-min task relaunched pid
  21028 → heartbeat flipped to `verdict: "GREEN"`, `serve_8770: true`,
  `serve_supervisor: {"kind": "ALREADY_UP"}` — the row that was `null` for 89k polls.
- **Kill test (run, not assumed):** killed Core pid 11916, port confirmed dead, supervisor
  spawned pid 28484 — **recovered in 2.4 s**.
- `live/logs/core_serve.json`: `pid 28484`, `fails 0`, argv
  `cosmos.py serve --root V:\A\Ai\COSMOS\live --port 8770`; 28484 is the pid `netstat`
  shows listening on 8770.
- `GET /api/v1/status` :8770 → HTTP 200, `root: V:\A\Ai\COSMOS\live`,
  `tree_id: KMesh-COSMOS-live`, `ledger_head: {seq: 688, event: BOOT_VERIFIED}`.
  `GET /api/v1/health` → 200, `ledger chain VERIFIED, 686 records`.

**Tests actually run** — `builds/health/test_serve_supervisor.py`: **6 of 9 assertions
FAIL against the staged pre-fix copy** in
`_delme/predispose_cosmos_health_clock_20260831_015230/`, **9/9 pass** against the fixed
module. The regression is real, proven against the old code first.

**Operator-only, documented not done** (`docs/CORE_SERVE_SUPERVISOR.md`): the exact
`schtasks /Change` line to pin `--supervise` explicitly in `COSMOS Health`, and the
decision on the now-redundant `\COSMOS_Serve_Watchdog` (leave it serving `trylive`, or
`/DISABLE`). It must NOT be repointed at :8770 — that would be a second uncoordinated
supervisor for one root. **No credential was missing; this was never a secrets problem.**

**Unblocks** F-17 (CVM stage-6 gate), F-15 (CVM latency, operator #1), cDeck panel
measurement.
