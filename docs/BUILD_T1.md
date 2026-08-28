# BUILD T1 — RF-LOCK-XPROC (Arbiter cross-process serialization)

**Branch:** `build/T1-arbiter-xproc` · **Date:** 2026-08-23 · **Machine:** Linux (Python 3.12.3)
**Module touched:** `cosmos/cosmos_lock.py` only. Ledger, mail, sched, kernel: not touched.
**Never-delete:** existing protocol, event kinds, and selftest checks remain.

## The finding (measured, not inferred)

Two independently-constructed keyed `Arbiter` instances sharing one lease ledger were
not serialized. Each replayed (or started empty) in its own memory, decided `tree` was
free, issued fencing token `1`, and appended a `GRANT`. The in-process `HELD` check
cannot see a sibling process's `_leases`. Advisory locking is dead; this was the same
read-check-write race the spike claimed to have closed, one process boundary later.

## The fix

An exclusive OS lock on a sidecar file beside the lease ledger, copied from
`cosmos_ledger._lock_handle`:

- path: `str(ledger_path) + ".lock"`
- Windows: `msvcrt.locking(..., LK_LOCK, 1)`
- elsewhere: `fcntl.flock(..., LOCK_EX)`
- held across **replay -> decide -> append** in `acquire()`, `renew()`, and
  `fenced_commit()`
- under the lock the arbiter **re-primes** `_leases` and `_max_token` from disk
  (a remembered projection is how the duplicate token was born)
- the OS drops the lock on process death — no cleanup discipline

## BEFORE (unlocked arbiter, this container)

Protocol: two `subprocess` children, each `Arbiter(ledger, key=b"t1-xproc-key")`,
barrier, then simultaneous `acquire("tree", holder)`. 20 trials.

```
BEFORE trials=20
  exact_one_winner: 0 / 20
  two_winners:      20 / 20
  zero_winners:     0 / 20
  duplicate_token_1:20 / 20
  all_tokens: [[1, 1], [1, 1], ... x20]
  all_grants: two GRANT events per trial, both token=1 (A and B)
  sample: a={'won': True, 'holder': 'A', 'token': 1}
          b={'won': True, 'holder': 'B', 'token': 1}
```

The ledger lied: two live grants, one resource, one token number.

## AFTER (sidecar lock + reprime)

Same harness, same 20-trial count, same barrier.

```
AFTER trials=20
  exact_one_winner: 20 / 20
  two_winners:      0 / 20
  zero_winners:     0 / 20
  loser_HELD:       20 / 20
  all_tokens: [[1], [1], ... x20]
  all_loss_kinds: [['HELD'], ... x20]
  all_grants: exactly one GRANT per trial, token=1
  winners: A in some trials, B in others (not serialized-by-luck)
  sample: a={'won': True, 'holder': 'A', 'token': 1}
          b={'won': False, 'holder': 'B', 'kind': 'HELD'}
```

The second child blocks on the OS lock, re-primes onto the live lease, and refuses
`HELD` by kind. One fencing token. One holder.

## Selftest (positive and negative controls)

`tests/test_cosmos_lock.py` keeps the original spike checks and adds:

- **Positive:** a keyed sibling constructed *before* the grant, then `acquire` — after
  reprime it sees the live lease (does not mint a second token 1).
- **Negative:** that sibling raises `LockError` kind `HELD`; the ledger has exactly
  one `GRANT`.
- **Positive (xproc):** two processes race `acquire("tree")` — exactly one wins,
  winner token is 1 and matches the lone GRANT.
- **Negative (xproc):** the loser is `HELD` by kind (not a crash, not a second grant);
  two `GRANT`s with token 1 is a failed check.

Run in this container (claim without a passing run is not done):

```
PYTHONPATH=cosmos python3 -m pytest tests/test_cosmos_lock.py -v
```

```
tests/test_cosmos_lock.py::test_cosmos_lock PASSED
1 passed in 0.17s
```

Script form of the same selftest:

```
SELFTEST PASS - 25 checks (7 refusals asserted BY KIND, 2 chains BY EVENT, 1 measured xproc race)
```

Related suites still green on this change: `test_stage7_fixes`, `test_kernel`,
`test_concurrency`. Wave3 B6 (signed leases) and M4 (hash-fenced commit / COMMIT_UNFENCED)
re-ran against the locked `fenced_commit` and passed. The full `test_wave3` file dies
earlier in this Linux container on the incumbent `py` launcher (`FileNotFoundError: 'py'`),
which is not this change.

## What this does not claim

`release()` and `status()` are still in-memory on the calling instance. T1's RF is
`acquire` / `renew` / `fenced_commit` across independently-constructed keyed arbiters.
Those three now take the lock.
