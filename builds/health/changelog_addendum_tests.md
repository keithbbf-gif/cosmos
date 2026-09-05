
**Addendum — the two suites that pinned the old opt-in contract.** The default flip
breaks 20 assertions across `tests/test_core_supervisor.py` (18/31) and
`tests/test_health_clock_optin.py` (11/18). **None is a functional regression**, and that
is measured, not asserted: `builds/health/test_cascade_isolation.py` (**11/11**) replays
the same calls on a clean root and every "functional-looking" failure — `SPAWNED`, the
three `argv` checks, `DISABLED`, `ALREADY_UP` — passes. They failed because
`poll_once(str(root))` in section 1 now legitimately spawns and writes
`logs/core_serve.json` with a future `next_attempt_epoch`, so the next call correctly
returns `BACKOFF` and `CALLS` is empty (`IndexError`). The harness demonstrates that
cascade directly. `tests/test_own_clocks.py` is unaffected: **66/66**.

`tests/` is outside this fence, so the repairs are **proposals**, not edits —
`builds/health/PROPOSAL_tests_default_on.md`. Both are proven by patched copies that were
actually run: `test_core_supervisor.py` needs **one line** (line 91,
`poll_once(str(root), supervise=False)` — section 1 means "OFF is inert" and must now
*ask* for OFF) → **31/31**; `test_health_clock_optin.py` needs 4 (two `--no-supervise`
CLI args, the `"Default OFF"` help string, and the three default assertions) → **18/18**.
Regenerate with `builds/health/make_patched_tests.py`, which fails loudly
(`ANCHOR MISSING`) if `tests/` moves under it. `--supervise` is still documented; `--help`
renders `--supervise, --no-supervise`.

**Final live state:** Core pid 28484 on :8770 serving `KMesh-COSMOS-live`
(`ledger_head seq 688 BOOT_VERIFIED`); health clock pid 21028 at 175 polls,
`verdict GREEN`, `serve_supervisor ALREADY_UP`; and the `COSMOS Health` task action is
still `... --root V:\A\Ai\COSMOS\live --loop` — **unchanged**, which is the point: the
fix needed no re-registration.
