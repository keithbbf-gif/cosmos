# CVM Desktop Clock — MOTIF stage-5 critique

- model: `bts_oa_api`  rc: `0`  secs: `77.6`
- source: `oai_oa_cvmdt_clock_motif_stage_5_critique_o_bc130121_result.json`
- recorded: 2026-08-27T05:19:55-0500 (COW disposition, P10)

---

# cvmdt - Motif stage-5 critique (oa-api)

## Evidence boundary

This review is limited to the supplied artifacts:

- `builds/cvm-dt/cvm_dt_clock.py`
- `builds/cvm-dt/test_cvm_dt_clock.py`
- supplied `README.md` excerpt (explicitly the voice-client README, not clock documentation)
- supplied `docs/CVM_ARCH.md` H-constraint excerpt
- dispatch-time live observations

The supplied test is loopback/fake-Core evidence only. It is not native Task Scheduler, `pythonw --loop`, live `:8770`, or runtime-binding evidence.

## Findings

### 1. Native DT clock is not runtime-bound

**FAIL — HIGH — missing live runtime surface / dispatch observation**

The required runtime-binding gate is explicitly named in `builds/cvm-dt/cvm_dt_clock.py:26-29`: two native heartbeat advances plus advancement of `state/cvm/pull.json` under this clock, without a human turn or Claude process. The module correctly says `rc=0 is not the gate`.

That gate is not met at dispatch:

> `live/logs/` has `cvm_clock_heartbeat.json` (clock id 15/16 family) but **NO** `cvm_dt_clock_heartbeat.json` — the DT own-clock is not ticking natively.

Without the DT heartbeat, there is no evidence that `--register` was emitted, manually installed, accepted by Task Scheduler, launched under `pythonw`, survived a minute self-heal interval, or drove `CvmDtClient.cycle_once()` against live Core. There is also no supplied before/after live `pull.json` evidence attributable to clock id 17.

`builds/cvm-dt/test_cvm_dt_clock.py:3-9` expressly limits itself to loopback evidence and restates that stage-6 requires the missing live proof. Its green result therefore cannot compensate for the missing native heartbeat.

**Required change before stage 6:** install/run the emitted task in the logged-on user session, collect two separate native DT heartbeat records with increasing `last_run_epoch`, and collect a corresponding live `state/cvm/pull.json` cursor transition while documenting no human turn and no Claude process.

---

### 2. `CLOCK_ID = 17` is unratified drift against H10’s stated next ID of 15

**FAIL — HIGH — `builds/cvm-dt/cvm_dt_clock.py:66`**

The module declares:

```python
CLOCK_ID = 17
```

But the supplied H10 contract says:

> “Next clock id is **15**.”

Dispatch observations make the drift more concrete:

> `live/logs/` has the `cvm_clock_heartbeat.json` clock-id 15/16 family  
> `live/state/cvm/pull.json` has `clock_id=16` (not 17).

The clock’s own comments and test assert that 17 is correct, but no supplied registry/allocation artifact ratifies 17 or explains the transition from H10’s 15 through observed 16 to 17. A unique ID is important for the lock/heartbeat namespace and `skip_alive`; an invented or stale ID can make a clock appear separate while violating the canonical own-clock allocation.

**Required change before stage 6:** reconcile the canonical own-clock registry and H10 documentation, then use the ratified ID everywhere: source constant, emitted task identity, heartbeat proof, tests, and live projection. Do not proceed by merely editing the H10 excerpt after the fact without showing the allocation authority.

---

### 3. H10 design is present, but deployment proof is absent

**FAIL — HIGH — `builds/cvm-dt/cvm_dt_clock.py:208-269`, `272-289`; missing Task Scheduler artifact**

The intended H10 topology is structurally sound:

- `loop()` is a detached long-running body with a 15-second inner interval (`DEFAULT_INTERVAL_S = PULL_INTERVAL_S`) at `builds/cvm-dt/cvm_dt_clock.py:72`.
- `register()` emits a one-minute task and a logon task at `builds/cvm-dt/cvm_dt_clock.py:272-289`.
- It uses `plan_create(..., "minute", mo=1)` and `plan_create(..., "onlogon")`, not `ONSTART`.
- `register()` returns emitted command text rather than calling `schtasks`; this is consistent with the propose/Keith-runs-COSMOS constraint.

However, H10 is not satisfied merely by having a command emitter. There is no supplied evidence of:

1. the actual emitted `schtasks /Create` command,
2. a registered task on the host,
3. its “logged-on only” settings as realized by Task Scheduler,
4. a `pythonw --loop` process,
5. a minute self-heal event, or
6. the required DT heartbeat.

The absent `cvm_dt_clock_heartbeat.json` is direct negative evidence for the final item.

**Required change before stage 6:** retain the source design, but produce runtime evidence from the logged-on host: registered task query, task action/trigger configuration, process identity, and the two-tick heartbeat/cursor gate.

---

### 4. Paused-loop behavior and `--once` drain behavior are correctly separated

**PASS — MED — `builds/cvm-dt/cvm_dt_clock.py:140-206`, `294-306`**

The pause contract is materially implemented:

- `pause_flag()` reads `state/control/PAUSE.flag` (`:75-97`).
- `is_paused()` treats any state other than `RUNNING` as paused and explicitly does not self-clear `RESUME-GATE` (`:99-107`).
- Normal loop ticks default `drain = not paused_now` (`:150-152`).
- A paused non-draining tick writes a `PAUSED` heartbeat and returns without constructing/calling the client (`:163-172`).
- `--once` explicitly calls `poll_once(..., drain=True)` (`:300-302`), so it drains even while paused.
- `test_pause_hold_heartbeats_without_pull()` and `test_resume_gate_idles_until_cleared()` exercise HOLD and RESUME-GATE loopback behavior.

The dispatch observation is consistent with this interpretation:

> `PAUSE.flag state=RUNNING (COW auto-resume 2026-08-27T01:50).`

A present flag in `RUNNING` state will not pause the clock, which follows this implementation’s stated contract.

---

### 5. Unreadable pause control is not emitted as a typed refusal

**FAIL — MED — `builds/cvm-dt/cvm_dt_clock.py:81-85`, `163-172`**

H3 requires unread control state to yield a named refusal rather than a silent ambiguity. On an `OSError` reading `PAUSE.flag`, `pause_flag()` returns a record containing only:

```python
{"path": ..., "state": "PAUSED", "read_error": ...}
```

The subsequent paused path at `:163-172` emits a heartbeat with:

- `tick = "paused"`
- `state = "PAUSED"`
- `ok = True`

It does not emit a refusal `kind`, `detail`, or an H3-recognizable typed result for the unreadable control state. The operator can infer something from `read_error` inside the heartbeat payload, but the cycle is reported successful and paused rather than refused for a named reason.

This is not a dead-clock issue: heartbeat advancement remains correct. It is a typed-refusal classification issue.

**Required change:** preserve heartbeat advancement, but add a stable typed refusal state/kind for unreadable pause control (for example a defined control/read refusal consistent with the existing CVM refusal vocabulary), set `ok=False`, and cover it with a test that makes the flag unreadable or injects a read failure.

---

### 6. Core unreachability is typed and still heartbeats on the normal error path

**PASS — MED — `builds/cvm-dt/cvm_dt_clock.py:176-206`; `test_cvm_dt_clock.py:test_dead_core_refuses_and_heartbeats`**

For `CvmDtError`, `poll_once()`:

- catches the error (`builds/cvm-dt/cvm_dt_clock.py:194-199`);
- emits `ok=False`, `state="REFUSED"`, `kind=str(e.kind)`, and bounded `detail`;
- writes the heartbeat afterward (`:201-205`).

The loopback test exercises a dead loopback endpoint and expects `RefusalKind.UNREACHABLE` while checking that the heartbeat advances.

This is appropriate H3 behavior for the provided `CvmDtError` path. It does not establish that live Core is reachable.

---

### 7. Generic loop exceptions lose H3 typed-refusal semantics

**FAIL — MED — `builds/cvm-dt/cvm_dt_clock.py:252-265`**

The outer loop catches broad `Exception`, writes a traceback to `cvm_dt_clock.err`, and attempts a heartbeat with only:

```python
{"tick": "error", "clock_id": CLOCK_ID, "error": tb[-500:]}
```

That generic heartbeat omits:

- `state = "REFUSED"`,
- a stable typed `kind`,
- `detail` differentiated from arbitrary traceback text,
- the normal schema/pause/tree fields constructed by `poll_once()`.

Therefore errors outside the inner `CvmDtError` catch—including path, serialization, unexpected client, or projection failures—can become untyped `tick="error"` heartbeats. They are not silent, which is better than disappearance, but they do not meet H3’s named-refusal requirement.

**Required change:** funnel all loop-level failures through one refusal/heartbeat construction path, with a defined typed `kind` for unexpected/internal failures or conversion to an existing appropriate refusal. Retain bounded diagnostics separately from the typed status.

---

### 8. `skip_alive` is unique-ID aware for loops, but `--once` bypasses it

**FAIL — MED — `builds/cvm-dt/cvm_dt_clock.py:109-120`, `220-234`, `300-302`**

The positive part is correct: `skip_alive()` verifies both heartbeat `clock_id` and live PID, so it does not mistake clock id 16 for this clock. The loop calls it when lock acquisition fails (`:220-234`), and the test checks the foreign-ID case.

But the CLI `--once` path goes straight to:

```python
poll_once(..., drain=True)
```

at `builds/cvm-dt/cvm_dt_clock.py:300-302`; it neither acquires `LOCK_NAME` nor calls `skip_alive()`.

Consequently a second `--once` launch can run concurrently with an active `--loop` process and invoke `CvmDtClient.cycle_once()` rather than no-op. That is contrary to the stated module contract:

> “skip_alive by unique clock_id so a second launch no-ops.”

The scheduler normally uses `--loop`, but the contract is written broadly and the `--once` diagnostic/drain route is executable concurrency surface.

**Required change:** define whether `--once` is intentionally exempt. If not exempt, give it the same lock/unique-ID discipline. If it must drain despite pause but may coexist with the loop, document the exception explicitly and prove that concurrent cycles cannot duplicate client-side effects.

---

### 9. The clock module itself does not establish an HTTP server, scheduler, SEED, or ledger authority

**PASS — MED — `builds/cvm-dt/cvm_dt_clock.py:140-206`, `208-269`, `272-289`**

Within the supplied clock file, there is no listening socket, HTTP route implementation, Core mutation API, scheduler/SEED implementation, or ledger write. The module:

- instantiates `CoreClient`,
- drives `CvmDtClient.cycle_once()`,
- writes its own heartbeat,
- reads a pause flag, and
- emits Task Scheduler command lines.

That is structurally consistent with H2’s satellite role.

This pass is intentionally narrow: `CvmDtClient`, `CoreClient`, and the projection implementation are not supplied. Their compliance cannot be inferred from this wrapper.

---

### 10. H6 audio-owner non-authority cannot be verified from the supplied clock packet

**FAIL — HIGH — missing surface: `builds/cvm-dt/cvm_dt_client.py` and audio-owner writer/lease authority**

The clock does not directly open or write an owner file in the supplied source. However, its core operational action is:

```python
rec = client.cycle_once()
```

at `builds/cvm-dt/cvm_dt_clock.py:181`.

The test expects that a successful clock cycle produces `audio_owner == "desktop"` and that `state/cvm/pull.json` records `"audio_owner": "desktop"` in `test_tick_heartbeat_and_cursor()`. That proves the clock delegates into an audio-owner-affecting path, but not whether the DT client is merely projecting a Core-authoritative lease or locally writing an authority file.

The supplied live state is fail-closed but not proof of correct ownership semantics:

> `live/state/cvm/pull.json audio_owner='none', core_kind='UNREACHABLE', clock_id=16 (not 17).`

There is no live DT heartbeat and no supplied DT client implementation to establish exactly one owner, a visible lease, non-stealing behavior, or that this clock never writes the owner state as authority.

**Required change before stage 6:** provide the `CvmDtClient`/audio-lease source and a live ownership proof showing Core-authoritative leasing/projection, exactly one active owner, and no DT clock-owned authority write. Do not use the current `audio_owner='none'`/UNREACHABLE record as a substitute.

---

### 11. H5 “keep Core up” is not met as an operational readiness condition

**FAIL — HIGH — dispatch observation; causal source attribution UNKNOWN**

H5 requires that Core `:8770` stay up through the change. Dispatch observes:

> `live/state/cvm/pull.json core_kind='UNREACHABLE'`.

This critique cannot attribute the Core outage to this clock: the supplied module is a client and does not edit Core in the packet. The source-side additive posture is therefore acceptable in principle. But stage-6 runtime binding cannot be declared ready while the only supplied live Core state is `UNREACHABLE`, because the clock cannot demonstrate real pulling/projection against unavailable Core.

**Required change before stage 6:** restore/verify live Core `:8770` in the logged-on runtime session, then perform the DT-clock runtime-binding proof. Preserve the fail-closed `UNREACHABLE` behavior; do not mask it with cached or synthetic success.

---

### 12. `register()` correctly emits and does not execute `schtasks`

**PASS — LOW — `builds/cvm-dt/cvm_dt_clock.py:272-289`; `test_cvm_dt_clock.py:test_register_emits_does_not_run`**

`register()` constructs minute and on-logon command arrays, converts them to displayable command lines, and returns `ran=False`. There is no `subprocess.run`, `Popen`, `os.system`, or equivalent execution call in the function. The test monkeypatches `subprocess.run` and verifies that it is not invoked.

This meets the narrow contract: emit `/Create`; do not run it.

It does not prove that the emitted commands are valid on the target host or that the tasks have been manually installed; finding 3 remains blocking.

---

### 13. “One HTTP stack” is not demonstrated by the `REUSED` tuple; it is decorative dead code

**FAIL — LOW — `builds/cvm-dt/cvm_dt_clock.py:54-62`**

The module imports `core_get` and `pull_url`, then declares:

```python
REUSED = (core_get, pull_url, write_heartbeat)
```

`REUSED` is not consumed by the clock. `pull_url(client_id)` is used only as a quoted provenance field in `poll_once()` (`:160`), while the actual cycle is delegated through `CoreClient` and `CvmDtClient`.

The tuple does not enforce stack reuse, reduce round trips, or provide an integration boundary. It is dead/decorative code and creates a misleading H9 compliance signal. The loopback test’s identity checks (`clk.core_get is core_get`, `clk.pull_url is pull_url`) likewise prove import identity, not that the client cycle uses the same transport implementation.

**Required change:** remove `REUSED`, or replace the claim with a real injected/shared transport boundary demonstrated by `CvmDtClient` source and a focused test. Avoid adding another stack merely to satisfy the test; the preferred resolution is to make the existing client transport relationship explicit.

---

## Gate-readiness verdict

**NOT READY for stage-6 runtime-binding.**

The primary blocker is not loopback correctness; it is the absence of the DT native clock in live runtime. There is no `live/logs/cvm_dt_clock_heartbeat.json`, no proof of two native ticks, and no attributable live `pull.json` cursor advance. Live Core is also currently represented as `UNREACHABLE`, which prevents the required real pull/projection proof.

Before stage 6, COSMOS must first:

1. reconcile and ratify the clock-ID allocation (`17` versus H10’s stated `15` and observed `16`);
2. install and run the emitted logged-on Task Scheduler topology, then collect native `pythonw --loop`/heartbeat evidence;
3. restore or verify live Core `:8770`;
4. demonstrate the named heartbeat-plus-cursor gate with no human turn and no Claude process;
5. provide the missing `CvmDtClient`/audio-lease authority surface to prove H2/H6 rather than merely asserting it;
6. make unread-control and generic-loop failures typed refusals; and
7. resolve `--once` concurrency against the stated `skip_alive` contract.

The current loopback green log is useful regression evidence, but it is not a stage-6 gate pass.