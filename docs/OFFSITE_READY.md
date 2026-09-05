# OFFSITE READY — everything is built; here is the one file only Keith can supply

**Consumer:** Keith (the operator) + COW. **Wish:** `docs/WISHLIST.md` — *"R2 running
properly — trees: `V:\Research4`, `V:\Ai`, `V:\A`. Keys live in `D:\R2Cloner`"*, and
the clause that ranks it: **survives total tree DELETION**. **Written 2026-08-31**
from runs taken the same session. Every number and every quoted artifact below came
out of a command; anything that did not is labelled **UNMEASURED**.

> **Credential boundary, binding on this whole document.** `D:\R2Cloner` holds key
> material in PLAINTEXT. Nothing in `builds/backup/` reads, opens, lists or resolves
> into it — `cosmos_backup_r2.guard_credential_path` refuses that prefix *before*
> touching the filesystem, and `test_offsite_clock.py` pins the refusal. This document
> records **which** credential is needed and **what it unblocks**, and no value from
> it appears here, in any test, log, receipt or heartbeat. Keith moves key material;
> COSMOS opens the door.

---

## 1. The state, in one line

**The scheduled offsite push is built, tested and armed-able today. It refuses,
typed and visibly, until one file exists.** The adapter seam matches: `ADAPTERS["r2"]()`
with no credential is `NO_CREDENTIALS` (`builds/backup/_f47_live_adapter.json`,
2026-08-31T11:56Z), not a `NotImplementedError` stub. Restore rehearsal from an R2
prefix (`do_rehearse_target`) is proven offline against MemoryTransport. Measured
against the live root:

```
$ py -3.14 builds\backup\cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --once ^
        --source V:\A\Ai\COSMOS\cosmos
  rc=2
  "state": "REFUSED",
  "kind": "NO_CREDENTIALS",
  "detail": "no credential file at V:\\A\\Ai\\COSMOS\\live\\config\\r2_credentials.json
             (Keith places it; COSMOS opens the door)",
  "offsite_copy_exists": false,
  "heartbeat_path": "V:\\A\\Ai\\COSMOS\\live\\logs\\offsite_clock_heartbeat.json"
```

That refusal *is* the deliverable while F-46 is open. The task can be registered
tonight; it will refuse every night, on the board, and the night the credential lands
it starts pushing **with no code change and no second decision**.

## 2. What the operator must supply — exactly two files, one of them secret

### 2.1 The credential — **only Keith can produce this**

**Path:** `V:\A\Ai\COSMOS\live\config\r2_credentials.json`
(the `config` role under the runtime root; no path is hard-coded — the resolver finds it)

**Shape** — four required fields, one optional:

```json
{
  "account_id":        "<Cloudflare account id>",
  "access_key_id":     "<R2 API token access key id>",
  "secret_access_key": "<R2 API token secret>",
  "bucket":            "<the backup bucket name>",
  "endpoint":          "optional; defaults to https://<account_id>.r2.cloudflarestorage.com"
}
```

**Make it a COSMOS-only R2 API token scoped to one backup bucket — not a reused
account-wide key**, and give it Object Read + Write only. COSMOS never issues a
DELETE, so delete permission is capability it does not need and should not hold.

**It unblocks:** the entire offsite leg — `push`, the read-back verification, the
sealed `REMOTE_PUSH.json` receipt, the scheduled task, the protection heartbeat, and
with them F-46, F-47 and the off-machine half of F-54.

**A missing field is a different refusal from a missing file**, deliberately, because
the next move differs:

| what is wrong | `kind` | measured |
|---|---|---|
| file absent | `NO_CREDENTIALS` | live run above, rc=2 |
| file present, field missing | `BAD_CREDENTIALS` — names the FIELD, never a value | `test_offsite_clock.py::test_malformed_credential_is_a_different_kind` |
| path inside `D:\R2Cloner` | `FORBIDDEN_CREDENTIAL_PATH` — refused before any filesystem call | `test_plaintext_key_store_is_refused_by_path_alone` |

### 2.2 The scope declaration — Keith's call, not a secret

**Path:** `V:\A\Ai\COSMOS\live\config\offsite_scopes.json`
**Template:** `builds/backup/offsite_scopes.example.json` (copy it; it parses as-is —
verified: `load_scopes` returned the `cosmos` and `docs` scopes).

Nothing guesses a source tree: an absent declaration is `NO_SCOPES`. A backup that
quietly covers a plausible-but-wrong tree is the exact defect this module refuses.

Alternatively pass `--source <tree>` (repeatable) and skip the file — same code path.

## 3. The exact commands to arm it

Run in order. Each one's failure is cheap and each one's success is provable.

```bat
:: 0. BEFORE the credential — prove the whole path offline, against a memory bucket.
::    Fake credential, no network, real push/read-back/re-hash/receipt/heartbeat.
py -3.14 builds\backup\cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live ^
        --selfcheck --source V:\A\Ai\COSMOS\cosmos

:: 1. Keith places live\config\r2_credentials.json   (§2.1)
:: 2. Keith places live\config\offsite_scopes.json   (§2.2 — or use --source)

:: 3. Preflight: configured vs missing. No network, no credential value read.
::    Must print  "status": "READY"  before going further.
py -3.14 builds\backup\cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --preflight

:: 4. First real push, by hand, smallest scope first. Watch readback_verified.
py -3.14 builds\backup\cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live ^
        --once --source V:\A\Ai\COSMOS\cosmos

:: 5. See the schtasks command WITHOUT registering anything.
py -3.14 builds\backup\cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --plan-task

:: 6. ARM IT — register the nightly task for the current user.
py -3.14 builds\backup\cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live ^
        --install-task --at 02:30
```

Step 6 is the one line that arms the clock. It is **not run in this shift** —
registering a recurring job on Keith's machine is Keith's decision, and
`--plan-task` exists so he can read it first. The argv it will run, printed by
`--plan-task` against the live root just now:

```
schtasks /create /tn "COSMOS Offsite Push"
         /tr "<pythonw> V:\A\Ai\COSMOS\builds\backup\cosmos_offsite_clock.py
              --root V:\A\Ai\COSMOS\live --once"
         /sc daily /st 02:30 /f
```

`pythonw`, so no console flashes nightly. Current-user, **no `/rl highest`** — pushing
a backup needs no elevation and asking for it would be capability the task does not need.

## 4. How to tell it is working — two clocks, one heartbeat

`V:\A\Ai\COSMOS\live\logs\offsite_clock_heartbeat.json`, rewritten on **every** tick
(push, refusal or pause), carries two different timestamps because they answer two
different questions:

| field | question | why it is separate |
|---|---|---|
| `last_run_epoch` | is the **clock** alive? | what the health watchdog compares on |
| `last_success_epoch` / `success_age_s` | is the **data** protected? | carried forward across refusals |
| `offsite_copy_exists` | has a push **ever** succeeded? | `false` today, and never faked |

**A clock that ticks nightly and refuses nightly is alive and protecting nothing.**
One timestamp cannot say both, so a refusal preserves the last real success and never
invents one — pinned by `test_a_later_refusal_remembers_the_last_real_success` and
`test_a_refusal_never_fabricates_an_offsite_copy`.

The watchdog picks the file up automatically: `discover_unwatched` globs
`*heartbeat*.json` in the logs role, so it is visible on the board from the first
tick. **PROPOSAL (outside this fence):** add to `builds/health/cosmos_health_watchdog.py`'s
`FLEET` tuple — `DaemonSpec("offsite_clock", "offsite_clock_heartbeat.json", "COSMOS
Offsite Push", 93600.0, required=False)`; 26h = daily + slack, and `required=False`
until the task is actually registered, so an unarmed clock does not page.

Per-push receipts also land on **this** machine at
`live\logs\offsite\<scope>-<stamp>.json`. The receipt in the bucket proves the push to
whoever holds the bucket; the copy here proves it to the operator who has just lost
the bucket and needs to know what should have been in it. Both are sealed —
`cosmos_backup.check_seal` refuses an altered one.

## 5. What proves a push, and what must never count

The push does **not** trust the PUT. After storing, it GETs **every object back** into
a scratch directory and re-hashes it against the sealed manifest; any drift is
`R2_HASH_MISMATCH` and the push refuses. `readback_verified` must equal `files_pushed`.

**What must never count as verification:** a green exit code, a 200 from a PUT, a byte
count that matches, or a listing showing the objects exist. Only a re-hash of bytes
that came back. And the gate that actually settles it — **restore onto a machine that
is not this one** (`cosmos.py install` + restore-from-R2 on a cold peer, then
`cosmos.py audit` → `"ok": true`) — is **UNMEASURED** and stays that way until it runs.
No byte has ever been sent to R2 from this tree.

## 6. Things the operator should know before arming it

- **Nothing is ever deleted.** Each push lands under `<scope>/<YYYYmmddTHHMMSS>/`, so
  runs never overwrite each other, and COSMOS issues no DELETE. **Bucket retention is a
  Cloudflare lifecycle policy Keith sets** — otherwise the bucket grows forever.
- **The read-back scratch is staged, not cleaned.** It is born in
  `live\work\_delme_offsite_readback\<scope>-<stamp>\` — a full local copy of what was
  verified, kept for inspection, deleted by Keith at his leisure. Left alone it grows
  by the size of each push; on the 65 GiB scope that matters, so **this is a real chore
  the schedule creates**, and it is named rather than hidden.
- **A scope holding key material refuses the push**, by manifest path alone (the scan
  never opens a file), because off-machine storage inherits every exposure in scope.
  There is deliberately **no override flag** — exclude the file, or build encryption at
  rest and lift the refusal properly.
- **One scope refusing does not cancel the others** (state `PARTIAL`, `ok: false`), and
  the failing scope's `kind` reaches the heartbeat by name.
- **PAUSE is honored** — an unreadable `state/control/PAUSE.flag` is treated as paused
  (fail-closed).
- **Cost — UNMEASURED against Keith's account.** Cloudflare's published rates (10 GB-month
  free, $0.015/GB-month after, $4.50/M writes, $0 egress) put 65.42 GiB / 150,504 files
  at roughly **$0.85/month** and **under $1 for the first full push including read-back**.
  Order of magnitude, not a quote; nothing has been billed.
- **First push, plan for hours not minutes.** 65 GiB over a home uplink, and the
  read-back doubles the object count. Roll out smallest scope first (§2.2 template) —
  a monolith that refuses at 90% restarts from zero.

## 7. Long paths — covered on BOTH sides, and that was not free

`docs/LONGPATH_FINDING.md` measured 2,143 files under the three WISHLIST trees past
MAX_PATH (deepest 412 chars) and fixed the walker. **A source-side fix alone would still
have lost them on a push**, because a push has two more filesystem touchpoints and
neither is the walker:

| touchpoint | side | state before this shift |
|---|---|---|
| `R2Target.store` | reads the source | `Path(src).read_bytes()` → **untyped `FileNotFoundError`** |
| `R2Target.retrieve` | writes the read-back scratch | `Path(dst).write_bytes()` → same |
| `push()` scratch-empty guard | destination | plain `iterdir()` — a scratch holding only long-path leftovers looked **empty** |

All three now go through the `\\?\` prefix. Measured: `test_longpath_r2.py` **4 errors
before the fix, 7 tests OK after**. The live core module's destination side
(`cosmos/cosmos_backup.py` — dest dir, manifest write, rehearsal scratch) was checked
too and is honored: `test_longpath_core_dest.py` is **5 tests OK against the fixed
module and 3 failures against `git show HEAD:` (`1 != 3` — the silent omission)**.

## 8. Fence and honesty record

Written this shift, all inside the fence: `builds/backup/cosmos_offsite_clock.py`,
`builds/backup/test_offsite_clock.py`, `builds/backup/test_longpath_r2.py`,
`builds/backup/test_longpath_core_dest.py`,
`builds/backup/prove_shadow_regression.py`,
`builds/backup/offsite_scopes.example.json`, three edits to
`builds/backup/cosmos_backup_r2.py` (§7), this file, and an appended section in
`docs/CHANGELOG_2026-08-30_CC_AUDIT.md`. The replaced adapter is staged at
`_delme\predispose_cosmos_backup_r2_20260831T015148\`.

**Run against the live tree:** `--preflight` and one `--once`, which wrote
`live\logs\offsite_clock_heartbeat.json` (the refusal quoted in §1). Nothing else in
the live tree was touched; no task was registered.

**UNMEASURED, and stated as such:** no byte has ever been sent to R2. The wire leg,
the real bucket, real auth, real latency, throughput on 65 GiB, any cost figure, and
restore-on-a-cold-peer are all unmeasured and stay so until the credential lands.
`schtasks /query` reports the task is not registered; whether `--install-task` succeeds
on this account is likewise unmeasured, because it was not run.

## 9. F-54 — the orchestrator-state payload (added 2026-08-31T11:30Z)

The clocks above push a *scope* Keith names. The carry-over that lets COSMOS
resession after total tree DELETION is four files, not 65 GiB:

`SEED.json` · `SEED.decl.json` · `inflight.jsonl` · `motif_tracker.json`

`builds/backup/cosmos_state_offsite.py` packs that whitelist (never `live/state/`
wholesale) and drives the same two adapters. **Live, credential-free, dest-free:**

```
$ py -3.14 builds\backup\cosmos_state_offsite.py --root V:\A\Ai\COSMOS\live --preflight
  rc=2
  "status": "BLOCKED",
  "kind": "NO_OFFSITE_ROUTE",
  "payload": {"present": 4, "bytes": 254853},
  "routes": [{"route":"mount","kind":"NO_CONFIG"}, {"route":"r2","kind":"NO_CREDENTIALS"}],
  "heartbeat_written": false
```

Artifact: `builds/backup/_f54_live_preflight.json`. `test_state_offsite.py` **17/17**.
The night either dests or the R2 credential land, this same tick pushes the packed
payload with no code change. No byte was written to Drive, OneDrive, or R2 this pass.
