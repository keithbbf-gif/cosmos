# WO-20260920-001 — Runtime-binding gate: COMBINED proposal (DS + GLM)

**Grading pile entry.** Scored by JUDGE (not yet seated) with all other outputs.
**Prompt xfer (honest chain):** initial prompt = original `wo-20260902T114500`
mission (verbatim below). This coder's prompt included the outputs of the two
prior attempts: DS (`live/work/hero-ds/out/runtime-binding-gate.json`) and GLM
(`live/work/hero-glm/out/runtime-binding-gate.json`). Output = the combined
proposal that follows.

---

## This job (initial prompt — verbatim from wo-20260902T114500)

> FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only.
> Never write the live tree. Close the runtime-binding gate: the seven-stage
> pipeline has code and passing tests, but nothing has proven the machine
> executes the new tree instead of an old snapshot. Design and propose the
> acceptance test that forces a real runtime execution of the new tree (not a
> cached snapshot), including how to detect and fail if the old snapshot is
> used. Output a concrete test plan and any required harness changes as a
> proposal.

## Context included in this prompt (prior outputs)

1. **DS** (`hero-ds/out/runtime-binding-gate.json`, 22 KB): nonce-echo child
   (`tests/runtime_bind_echo.py`, already filed), gate harness
   (`tests/test_runtime_binding.py`), five pipeline checks C1–C5, L1/L2/L3
   layers, refusal kinds, proof schema. Stdlib-only, no Core changes,
   GitLab-safe default (`L1_ONLY`, `live_gate_closed=false`).
2. **GLM** (`hero-glm/out/runtime-binding-gate.json`, 7.8 KB): `BUILD_NONCE.txt`
   planted in `live/state`, Core restart, `status` verb emits `runtime_binding`
   {nonce, executed_sha256, executed_path}, service-signed
   `RUNTIME_BINDING_PROOF` ledger event, negative controls NC1 (stale snapshot
   must FAIL) and NC2 (rotate nonce without restart → `STALE_BINDING`).

## Combined proposal

**Principle:** two independent proofs, one gate. The **child echo** (DS) proves
the checked-out tree is what a fresh interpreter executes. The **ledger proof**
(GLM) proves the RUNNING Core is bound to that tree. Both must pass for
GATE_CLOSED. Each has its own negative controls; a gate that cannot fail is not
a gate.

### Files

| File | Action | Source |
|---|---|---|
| `tests/runtime_bind_echo.py` | **KEEP** (already filed by prior WO) | DS |
| `tests/test_runtime_binding.py` | **CREATE** — DS harness + GLM NC2 freshness + ledger verify | DS + GLM |
| `cosmos/cosmos.py` | **ADDITIVE patch** — `status` verb gains `runtime_binding` field + `RUNTIME_BINDING_PROOF` ledger event; active only when `live/state/BUILD_NONCE.txt` exists | GLM |

### Mechanism (merged)

1. **Plant** — gate writes fresh 256-bit nonce N to `live/state/BUILD_NONCE.txt`
   (git-ignored, never committed). N did not exist in any prior snapshot.
2. **Child echo (DS)** — fresh `py -3.14 -B tests/runtime_bind_echo.py
   --nonce-file <challenge>` emits `bind_digest = sha256(nonce + loaded source
   bytes)`, captured at import time (not re-read at emit). Old snapshot, copy at
   another path, pyc-cached stub, or in-process import cannot emit a correct
   digest for an unknown nonce. Stdlib-only; does not import Kernel/Ledger/
   Sched/Service.
3. **Ledger proof (GLM)** — after restart, `cosmos.py status --root <live>`
   emits `runtime_binding` = {nonce (read by the serving process),
   executed_sha256 (of the loaded core module), executed_path (its `__file__`)}
   and appends one service-signed, hash-chained `RUNTIME_BINDING_PROOF` ledger
   event. Test reads the LEDGER (authority), not a log line, and verifies the
   chain over N.
4. **Freshness (GLM NC2)** — rotate N without restart → status still returns the
   OLD nonce → gate reports `STALE_BINDING`; restart → NEW nonce appears. Proves
   freshness is measured, not assumed.
5. **Stale-snapshot negative (both)** — run against a deliberate copy of an
   older tree (no N) → gate must FAIL. If it passes, the gate is broken.
6. **Five pipeline checks (DS C1–C5)** — task read-back + nonce marker (C1),
   machine_count == registry_count (C2), reader-with-writer pairs (C3),
   integration children of THIS tree (C4), rehearsed rollback (C5).

### Contracts (first and last)

- **First line:** NONE or `diff --git`. Propose only. No merge. No live-tree
  write. No grok.exe.
- **Never:** `schtasks /create /delete /change` (default), kill pids, write
  under `live/` (except the gate's own BUILD_NONCE.txt plant), import
  Kernel/Ledger/service state in the harness.
- **rc=0 is not the gate.** The proof object is. Negatives must fire or the
  detector is UNMEASURED.
- **GATE_CLOSED only when:** child echo passes (nonce + bind_digest + child_pid
  != parent_pid + epoch > planted) AND ledger `RUNTIME_BINDING_PROOF` verifies
  over N AND C1–C5 all pass on Keith's machine with `--live --root --stage7`.
- Default pytest/GitLab invocation is `L1_ONLY` and must keep
  `live_gate_closed=false`. A GitLab green or SELFTEST PASS on a non-HEAD SHA is
  not the gate.

### Invocations

```
py -3.14 -B tests/test_runtime_binding.py
    → L1_ONLY, live_gate_closed=false (GitLab-safe)

py -3.14 -B tests/test_runtime_binding.py --live --root V:\A\Ai\COSMOS\live
    → L1 + C1–C3 live machine query (no /create, no kill)

py -3.14 -B tests/test_runtime_binding.py --stage7 --live --root V:\A\Ai\COSMOS\live --proof %TEMP%\runtime-bind-proof.json
    → all five checks; GATE_CLOSED if all pass
```

### Proof object (minimum)

```json
{
  "schema": "cosmos-runtime-bind-gate/1",
  "headline": "GATE_CLOSED | PARTIAL | L1_ONLY | GATE_OPEN",
  "live_gate_closed": true,
  "c1": {"nonce": "...", "bind_digest": "...", "child_pid": 0, "file": "...", "epoch": 0.0, "tasks": []},
  "c2": {"machine_count": 0, "registry_count": 0, "reds": 0, "red_rows": []},
  "c3": {"pairs": []},
  "c4": {"children": []},
  "c5": {"c5a_ok": false, "c5b_ok": null, "c5c_fired": null},
  "ledger": {"event": "RUNTIME_BINDING_PROOF", "verified": true},
  "did_not_write_live_tree": true,
  "did_not_touch_core": true
}
```

### Refusal kinds (unchanged from DS)

`SNAPSHOT_OLD, SNAPSHOT_BYTES, SNAPSHOT_PATH, SNAPSHOT_PYC, SNAPSHOT_INPROC,
SNAPSHOT_STALE, SNAPSHOT_INTERPRETER, SNAPSHOT_TASK, SNAPSHOT_COUNT,
SNAPSHOT_SPLIT, SNAPSHOT_MEMORY, STALE_BINDING, GREEN_LOG, UNMEASURED,
REHEARSAL_FAILED`

### What was merged and why

| Piece | From | Why kept |
|---|---|---|
| Child-echo mechanism | DS | Stdlib-only, no Core patch, GitLab-safe — the safe primary |
| Ledger-signed proof | GLM | Authority layer — the running Core proves itself, not just a child |
| NC2 restart-freshness | GLM | Closes the "cached boot" hole DS's design only flagged |
| C1–C5 + refusal kinds + proof schema | DS | The complete pipeline mapping and fail-closed grammar |
| BUILD_NONCE.txt gating | GLM | Ledger proof only active when planted — no behavior change otherwise |

### Not proposed

- Killing/restarting the live serve or Watchdog2 (SNAPSHOT_MEMORY flags a needed
  restart without performing it)
- `cosmos_clock.write_heartbeat` schema change (follow-on: optional challenge
  extra, per DS follow_on)
- Claiming GATE_CLOSED on any subset of tasks
- `.gitlab-ci.yml` edit (existing `python tests/test_*.py` picks up the new file)

---

**Derivation chain:** `wo-20260902T114500` → DS output → GLM output → this
combined proposal. Judge scores this entry against the same bar as the singles.