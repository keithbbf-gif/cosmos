# SCAR — the silent runner respawn (2026-08-27)

**Symptom.** Every `respawn_slot2` / `spawn_slot4` helper this check-in dropped returned
`rc=0` yet the slot never came back to life (`heartbeat_fresh_after: false`, poll loop
never advanced). For ~56 minutes slot2 sat dead while the respawn jobs all reported
success. A green rc that changed nothing — the fabricated-compliance failure class, this
time emitted by the tooling rather than an agent.

**Cause (reproduced by G46, job `acf186b2`, 2026-08-27 12:42).** `cosmos/cosmos_runner.py`
is a **library, not a daemon** — it has no `__main__` and no argparse. The respawn recipe
`py -3.14 cosmos\cosmos_runner.py --root <LIVE> --worker-id cosmos-runner-slotN --interval 5`
loads `class Runner`, ignores the leftover argv, and falls off the end of the module:
**rc=0, empty stdout/stderr, 0.13s, no worker.** It is not a missing `--loop`/`serve` flag
and not a runtime guard — the entrypoint simply does not exist.

**Corrected respawn recipe — expose the existing pool worker CLI (no new daemon, LOC delta 0):**

```
py -3.14 cosmos\cosmos_pool.py --root V:\A\Ai\COSMOS\live --worker --slot 4 --n 5 --interval 5
```

- Generic extra slot N: `--worker --slot N --n <N+1> --interval 5`. `--n` must be `>= slot+1`
  because `slot_spec()` only sees `plan_slots(n)`. `--n` here does **not** retune the running
  supervisor (which stays at `n=3`).
- Watch the **pool-naming** heartbeat `live\logs\cosmos_runner.slot4_heartbeat.json`, NOT the
  homemade `cosmos_runner_heartbeat.slot4.json` (that name belongs to the live extra slot3).
- Spawn from an agent job with `cosmos_clock.spawn_detached` (WMI `Win32_Process.Create`). A
  child `Popen` of the job gets **reaped with the Job Object** (a slot4 `Popen` died after 3
  polls even with DETACHED|BREAKAWAY); WMI detaches cleanly.
- **Do NOT** bump the supervisor `--n` while the homemade extra slot3 (`worker=cosmos-runner-slot3`)
  is alive — a pool slot3 with the same worker-id collides on the `Scheduler.done()` guard.

**Bind proof.** slot4 came up under the corrected recipe: `worker=cosmos-runner-slot4`,
pid 37216, instance `aec21229af18`, heartbeat advancing (polls 186+, age ~5s), main
(`cosmos-runner`) and slot3 (`cosmos-runner-slot3`) undisturbed. `py_compile` rc=0 on both
`cosmos_runner.py` and `cosmos_pool.py`; live files unchanged. See
[docs/arch/RUNNER_POOL_ARCH.md](arch/RUNNER_POOL_ARCH.md) for the pool design.

**Rule for future check-ins.** Never respawn a runner via `cosmos_runner.py <args>`. Use the
`cosmos_pool.py --worker` CLI above and confirm the slot by a **fresh, advancing** pool
heartbeat — an rc is not a runner.
