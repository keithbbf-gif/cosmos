# REATTACK — kernel-rails (post stage-7)

**Critic, not builder.** Target: `main` at `483e0fe` (stage-7 K1–K6+H2 merged).
Cluster: kernel / rails / lock / runner / spend / ingress / segments / sched.
Date: 2026-08-23. Host: Linux, Python 3.12.3.

A finding without a repro that runs is an opinion. Every residual below is
produced by `tests/reattack_kernel_rails.py`. That suite **exits 0 only when
every hole is still open**. Two consecutive runs: 9/9 HIT each.

```
PYTHONPATH=cosmos python3 tests/reattack_kernel_rails.py
```

## Cluster tests first

`PYTHONPATH=/workspace/cosmos`. Selftests that belong to this cluster:

| suite | result |
|---|---|
| test_kernel.py | PASS 13 |
| test_node_rails.py | PASS 12 |
| test_stage7_fixes.py | PASS 13 (K1–K6+H2 still closed under their own cases) |
| test_cosmos_lock.py | PASS 18 |
| test_segments.py | PASS 21 |
| test_spend_context.py | PASS 15 |
| test_concurrency.py | PASS 17 |
| test_wave4.py | PASS 16 |
| test_wave3.py | **host crash** — `FileNotFoundError: 'py'` in `run_tree_killed` (runner hardcodes the Windows `py` launcher). Not scored as a residual of the six named holes; it is an environment fact that the default `-c`/`py:` argv cannot even start here, while `argv:` can. |

Stage-7 closed what it tested. The six named residuals were not in those tests.
They remain.

## What stage-7 actually closed (so this is not a re-report)

| id | claimed close | still true under the original case |
|---|---|---|
| K1 | kernel Arbiter is keyed; forged unsigned GRANT refused on replay | yes — `test_stage7_fixes` K1 |
| K4 | `py:<path>` outside `tools_root` → BROKE/`traversal_refused` | yes — R2 control case |
| K5 | a *different worker string* cannot `done()` a claimed job | yes — R6 control case (`B` is refused `BAD_STATE`) |
| K6 | two reservations at the same clock ms get distinct `rid`s | yes — collision of *ids* is gone |

The residuals are the cases those fixes did not cover.

---

## R1 — Cross-process arbiter serialization  (CRITICAL)

**Module:** `cosmos/cosmos_lock.py` (`Arbiter.acquire`, `Arbiter._append`)
**Repros:** `repro_r1_inprocess_double_grant`, `repro_r1_cross_process_double_grant`

K1 signed the GRANT. It did not make the protocol a single writer.

- `_leases` and `_max_token` are process-private memory. `acquire()` expires and
  checks that map; it never re-reads the file.
- `_append` opens the JSONL in `'a'`, writes, fsyncs. No OS lock. Contrast
  `Ledger.append`, which takes an exclusive lock and re-primes from disk (B1).
- Two `Arbiter` objects on the same path — in one process or two — both see
  "free", both mint **token 1**, both write a *valid* HMAC GRANT.

**Measured (in-process):** A holds token 1, B holds token 1, two GRANT lines.

**Measured (two `fork` children, barrier after `__init__` / before `acquire`):**

```
{"event":"GRANT","holder":"B","token":1,"sig":"..."}
{"event":"GRANT","holder":"A","token":1,"sig":"..."}
```

Both signatures verify (same install key, honest `_sig`). Replay of that file
is last-GRANT-wins: one holder in memory, two GRANTs in history, fencing token
not monotonic. `fenced_commit` on the losing in-memory lease still believes it
is live until that process happens to replay.

This is the original "the arbiter serializes" contract, still only true inside
one object.

---

## R2 — `argv:` runner confinement bypass  (CRITICAL)

**Module:** `cosmos/cosmos_runner.py` lines 77–79
**Repro:** `repro_r2_argv_confinement_bypass`

K4 confined `py:<path>` to `tools_root`. The other command form is unconfined:

```python
argv = ["py", "-3.14", "-c", cmd] if not cmd.startswith("argv:") \
    else json.loads(cmd[5:])
```

`argv:[...]` is `json.loads`'d and handed to `run_tree_killed` with no root
check, no helper-prefix check, no allow-list.

**Measured:**

- `py:/tmp/.../evil.py` → `BROKE` + `traversal_refused` (K4 holds). Marker absent.
- `argv:["/usr/bin/python3","-c","open(marker,'w').write('pwned')"]` → `CLEAN`,
  marker contains `pwned`.

Delivery: `POST /api/v1/jobs` takes `command` as a raw string
(`cosmos_service.py`); so does `cosmos.py submit --command`. Anyone who can
submit a job can run any argv the service account can exec. K4 is a
side-entrance lock on a building whose front door is open.

The default `-c` path (`["py","-3.14","-c", cmd]`) is the same class of
unconfined execution; it is how `test_wave3.py` M5 is written, and it is why
that suite dies on this host. The named residual is `argv:`.

---

## R3 — Spend over-cap under overlap  (CRITICAL)

**Module:** `cosmos/cosmos_spend.py` lines 100–113
**Repro:** `repro_r3_spend_overcap_overlap`

K6's comment says the race is closed by binding the reservation to *the head
the caller projected from*. The code binds it to a **fresh** `head_seq()`
evaluated as the `append(...)` keyword argument — after the cap check, and
re-read from disk:

```python
self.ledger.append("SPEND_RESERVED", {...},
                   expect_head_seq=self.ledger.head_seq())
```

`Scheduler.claim_next` does this correctly (`head = self.ledger.head_seq()`
*before* `queued()`). Spend does not.

Interleaving that the production values themselves permit:

1. A and B both `_state()` a cap-10 rail with nothing reserved.
2. Both pass `settled + outstanding + 6 <= 10`.
3. A reserves (head 1 → 2).
4. B's `head_seq()` now returns 2, so `expect_head_seq=2` matches. No `STALE_HEAD`.
5. Both settle. **settled = 12 on cap 10.**

**Measured:** `ran == ["fast","slow"]`, no errors, `settled == 12.0`, `cap == 10.0`.
The barrier / 80 ms delay only *orders* steps 1–4. They do not invent the 12.

A sequential over-cap is still denied (`test_spend_context.py`). Overlap is not.

---

## R4 — Ingress `envelope_id` traversal  (HIGH)

**Module:** `cosmos/cosmos_ingress.py` line 86
**Repro:** `repro_r4_envelope_id_traversal`

```python
payload_path = self.dir / (env["envelope_id"] + ".payload")
```

`envelope_id` is attacker-controlled JSON. No confinement.

- Relative `../secret` → `ingress/../secret.payload`.
- Absolute `/tmp/.../secret` → pathlib drops the ingress dir
  (`Path("/ingress") / "/tmp/secret.payload"` is `/tmp/secret.payload`).

`accept_all` then hash-checks the *out-of-dir* bytes and ledgers
`INGRESS_ACCEPTED` with those bytes as `payload`.

**Measured:** both forms accepted `b"INSTALL_KEY_BYTES"` from a file that was
never inside the ingress directory.

**Length oracle (same join):** declare `payload_len=1`. Refusal detail is
`consumed 17 != declared 1` — the real size of the traversed file, ledgered
on `INGRESS_REFUSED`. Existence is also oracled (`BAD_ENVELOPE` vs
`SHORT_PAYLOAD` vs `HASH_MISMATCH`).

K2 confined `role()` / `protected_write`. Ingress was not given the same join.

---

## R5 — Segment anchors are unauthenticated  (HIGH)

**Module:** `cosmos/cosmos_segments.py` (`_rotate`, `_load`, `verify_all`)
**Repros:** `repro_r5_splice_history_unsigned_anchors`,
`repro_r5_load_trusts_unsigned_record_count`,
`repro_r5_missing_anchor_untyped_crash`

Segment *files* are `Ledger`s: HMAC, hash chain, typed refusals. Anchors are
bare JSON `{segment, first_seq, last_seq, record_count, segment_sha256,
prev_anchor_sha256, last_record_sha}`. No `hmac`, no `sig`. The ratified
revision called for signed anchors; this layer hashes them to each other and
stops.

Three measured consequences:

1. **History splice.** Delete sealed segment 2 (events `n=5..9`), rename
   survivors so numbers are consecutive, rewrite the unsigned anchors so they
   chain and the seq arithmetic matches the *remaining* walk. Each surviving
   `.jsonl` still passes `Ledger.verify()`. `verify_all()` **accepts**.
   **Measured payload `n`:** `[0,1,2,3,4,10,11,12,13,14,15,16]`. Five events
   gone, chain "VERIFIED".
2. **`_load` trusts `record_count`.** One-field edit, no signature to break.
   Next append's `global_seq` is **101** instead of 5.
3. **Missing anchor is not typed.** Delete `seg-00001.anchor.json` and
   construct `SegmentedLedger` → `FileNotFoundError`, not `LedgerError("TORN")`
   / `BROKEN_CHAIN`. Fail-loud is not typed-loud (H2).

`test_segments.py` plants *byte* corruption in an anchor and checks
`verify_all` names it. It does not test an attacker who rewrites a *consistent*
unsigned anchor, and it does not test `_load`.

Kernel still composes a single `Ledger`, not `SegmentedLedger`. The module is
in-tree, tested, and the residual is in the module.

---

## R6 — Worker-id spoofing  (HIGH)

**Module:** `cosmos/cosmos_sched.py` (`Scheduler.__init__`, `done`)
**Repro:** `repro_r6_worker_id_spoof`

K5 compares `st[job_id]["by"]` to `self.worker`. `self.worker` is the
constructor string. There is no credential, no binding to a key or process.

**Measured:**

- Real `A` claims job J.
- `Scheduler(..., worker="B").done(J, "CLEAN")` → `BAD_STATE` (K5 holds).
- `Scheduler(..., worker="A").done(J, "CLEAN")` → **succeeds**. Projection
  `st="CLEAN"`, `by="A"`.

The install key lives at `config/install_key.bin` and is what every
`Scheduler` / `Kernel` / `Ledger` needs. Possession of the key is possession
of every worker name. K5 is a string compare on a field the caller types.

Same shape everywhere identity is a name: `Kernel(..., worker=)`,
`Mailbox(..., worker_id=)`, `Ledger(..., writer=)`. The K5 residual is the
one that was supposed to be closed.

---

## Not claimed (no repro, so not a finding)

- HTTPS / bearer issues — not in the residual list; `test_tls` / `test_v1` not re-opened.
- `CliRail.dispatch` argv from payload — not exercised.
- Federation "no trust model" prose in `cosmos_identity.py` — already admitted;
  R6 is the *scheduler* manifestation after a fix that claimed to close it.
- Fixing any of this. Critic, not builder.

## How to re-run

```
export PYTHONPATH=cosmos
python3 tests/test_kernel.py
python3 tests/test_node_rails.py
python3 tests/test_stage7_fixes.py
python3 tests/test_cosmos_lock.py
python3 tests/test_segments.py
python3 tests/test_spend_context.py
python3 tests/test_concurrency.py
python3 tests/test_wave4.py
python3 tests/reattack_kernel_rails.py
```

`reattack_kernel_rails.py` returning 0 means the residuals are still open.
After a real close, that file must go red (MISS), then the closer writes a
positive selftest — the same shape as `test_stage7_fixes.py`.
