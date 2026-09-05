
## 2026-08-31 02:20–02:40 — F-15 CVM latency MEASURED; F-17 stage-6 gate CLOSED (`builds/cvm-dt/`, `builds/cvm/`)

Core answering on `:8770` (real root) unblocked both. Fence: `builds/cvm-dt/`, `builds/cvm/`.
Pre-edit copies staged at `builds/cvm-dt/_delme/predispose_cvm_latency_gate_20260831T022204/`.

### F-15 — the loop has a complete number for the first time
`respond.voice_post` was the last UNMEASURED stage and the dominant one. Measured against the
live Core, `felt_latency.total_ms` (mouth-shut -> first audio) now resolves with `missing: []`
across three runs: **988.0 / 1187.7 / 860.7 ms** (`BENCH_LATENCY.json`, tags `core_up`,
`core_up_budgeted`, `core_up_final`). The **loopback POST is the largest term at 270-593 ms** —
~30-50% of felt latency for a verb the kernel serves from its own state, with no network, no
model and no audio hardware in the path. That is the optimization target. STT inference is
215-245 ms; the fixed VAD hangover 200 ms; client CPU is negligible (resample and WAV parse are
microseconds, mix converter already 2.4-2.7x faster than its predecessor, byte-identical).
Every sample carries `rc=200 kind="command" brain="local"` per verb. Written up in
`builds/cvm-dt/LATENCY_F15.md`.

### Two defects the measurement found — both real, both fixed
1. **The bench would have spent Keith's money.** `stage_respond` POSTed `--phrase` verbatim and
   the default phrase is prose; prose is not a verb, so Core classifies it dictation ->
   `kind="chat"` -> model rail -> `CALL_EST_USD` on the spend guard. Harmless while Core was
   down, a standing charge the moment it came up. New `spend_class()` imports **Core's own verb
   sets** from `cosmos_voice` (never a private copy) and refuses to buy a latency sample.
2. **The bench denied service to the gate.** The first run posted 5 x 4 verbs = **20 in one
   minute**, exactly `RATE_PER_MIN` (shared, cross-session). The gate ran next and was refused
   `[SPEND_BLOCKED] RATE_LIMIT: 20 requests in the last 60s (cap 20/min)` — the measurement
   broke what it measured. Now capped at half the budget (read from `cosmos_spendguard`), and
   **a refused reply is never timed as a round-trip**: SPEND_BLOCKED returns HTTP 200 and fast,
   so timing it would report the loop getting quicker as it stopped working.
3. Latent bug caught by the suite (not standalone): the aggregate filter used truthiness, so a
   row measuring **0.0 ms was dropped as absent**. Now `is not None`.

### F-17 — stage-6 gate closed
`STAGE6_GATE.json` was `ok: false` since 22:57 and stayed false on the first re-run even with
Core up, for a reason that was **not** Core: `run_gate` demanded `audio_owner == "desktop"`
while the split gate scored the same unclaimed-sink reading PASS. Two gates, one box, opposite
verdicts off one string. Collapsed into one predicate `cvm_dt.sink_granted()` +
`SINK_OWNERS_OK`, which `cvm_gate` now imports instead of restating. It is not a loosening: it
also requires no `lease_kind` and an earcon-confirmed device match.
- `STAGE6_GATE.json` -> **`ok: true`**, ledger_seq **840**, sid `de067a75...` minted and resumed
  to the same sid, earcon on the Windows default device.
- `STAGE6_SPLIT.json` -> **PASS**; LOCAL 11/11, CORE 4/4 at ledger_seq **849**.

### LAN reach — recorded, not worked around
New `builds/cvm/lan_reach.py` -> `LAN_REACH.json` (`cvm-lan-reach/1`), verdict **`LOOPBACK_ONLY`**
on two independent readings: the only LISTEN socket is `127.0.0.1:8770` (pid 28484), and that
same pid's recorded spawn argv has **no `--remote`**. A firewall rule alone would change
nothing. Four blocking requirements recorded in `builds/cvm/LAN_REACH.md`: `--remote` bind;
`--tls` (cleartext remote binds are refused at `cosmos_service.py:1503`; `cryptography` verified
importable); keep bearer auth ON (no `--no-auth`); a Windows Firewall inbound rule (operator,
needs elevation). **The phone half of CVM stays UNMEASURED** and is not extrapolated from
loopback numbers. The probe issues no HTTP request at all, so it cannot carry a credential.

### Tests actually run
- `cvm_suites.py` -> `SUITES.json`: **15 suites, 189 checks passed, 0 failed** (was 14/170).
- New `test_cvm_dt_bench.py` **19/19**; new `builds/cvm/test_lan_reach.py` **7/7**.
- Regressions proven to FAIL against the pre-edit code via `prove_old_fails.py`
  (`all_fail_against_old: true`): old `cvm_dt` has no `sink_granted`; old `device_ok` returns
  **False** on the live reading where the new predicate returns **True**; old bench lacks the
  fence; and old `stage_respond` really did post the paid prose phrase.
