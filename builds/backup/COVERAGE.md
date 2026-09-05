# Backup coverage — what is protected, what is NOT

Measured 2026-08-30 (local) / 2026-08-31Z on the live tree, **re-measured
2026-08-31T05:36–05:47Z** for long paths (§ "Long paths", below). Every number came
from a run, not from reading code. Re-measure before trusting it; this file goes stale.

## There are TWO backup implementations, and only one of them runs

| | `cosmos/cosmos_backup.py` (+ `cosmos_backup_clock`) | `builds/backup/cosmos_backup.py` (this dir) |
|---|---|---|
| Scheduled | YES — 4x daily (07/11/19/23) | **clock vehicle 2026-08-31T16:04Z** — `cosmos_local_clock.py` `--plan-task` emits `COSMOS Bulletproof Backup` daily 04:00 and **registers nothing**. Live `--preflight` `NO_CONFIG`. `--install-task` is Keith's line |
| Ledger-integrated | YES (`BACKUP_VERIFIED`, `RESTORE_REHEARSAL_PASSED`) | NO — standalone artifacts only |
| Scope | bounded `live/` snapshot | any root passed as a parameter |
| Restore-over-a-tree | NO — rehearsal into scratch only | YES — `restore` verb, staged displacement |
| Sealed artifacts | manifest JSON, unsealed | sha256 + optional HMAC seal on every artifact |

Same module name, two trees. `cosmos_backup_clock` imports the `cosmos/` one; nothing
imports this one. Converging them is a separate work order — this file only records it.

## What the RUNNING backup actually covers

Ground truth, `live/logs/backup_clock_heartbeat.json`:

    "last_run": "2026-08-30T19:00:03-05:00", "state": "VERIFIED",
    "files": 360, "dest": "V:\\A\\Ai\\COSMOS\\live\\backups\\verified\\20260830T190002"

24 verified sets on disk; the last three hold 350–361 files / **~0.94–0.98 MB** each,
top-level `config/ ledger/ queue/ state/` only.

**NOT covered by anything scheduled** (measured file counts / bytes, `__pycache__` excluded):

| tree | files | bytes |
|---|---|---|
| `cosmos/` | 90 | 1,676,023 |
| `docs/` | 113 | 2,602,417 |
| `tests/` | 62 | 602,814 |
| `kdash/` | 5 | 172,587,270 |
| `builds/` | 11,350 | 6,791,120,767 |

Also not covered: `V:\Research4`, `V:\Ai`, `V:\A` (the WISHLIST P0 scope), and any target
that is not this machine.

## The five gaps that matter

1. **Same-volume.** The backup destination of the *running* clock is still
   `V:\A\Ai\COSMOS\live\backups` — the same physical volume as the original. A drive
   failure takes both. **Path-mount adapters now exist (F-48, 2026-08-31):**
   `builds/backup/cosmos_backup_mounts.py` — GDX / ODX / ES.3. Dest is
   `config/backup_targets.json`, never invented. Live bind (creates nothing)
   `builds/backup/_f48_live_bind.json`: GDX `X:\` READY `vol:19831116` ≠ src
   `vol:8046DC70`; ODX `C:\Users\Papa\OneDrive` READY `vol:3242CB17`; ES.3
   `DRIVE_NOT_MOUNTED` (ST3000NM0033 not installed). Preflight without config is
   `NO_CONFIG` with `adapter_implemented: true`. **Clock vehicle landed
   2026-08-31T11:14Z:** `cosmos_mount_clock.py` — without dests the tick REFUSES
   `NO_CONFIG` and heartbeats it; `--plan-task` emits `COSMOS Mount Offsite Push`
   daily 03:00 and registers nothing (`test_mount_clock.py` 34/34; live
   `_f48_clock_live.json` `status=BLOCKED`). R2 is a separate adapter
   (`cosmos_backup_r2.py`), blocked on the credential.
2. **Silent truncation upstream.** `cosmos_backup_clock._copy_tree_files` caps at 400
   files per subtree and skips anything over 32 MB, then reports `VERIFIED`. A backup
   that drops files and still says VERIFIED is the green-log defect the canon names.
3. **No quiescence (detect landed 2026-08-31T12:46Z; freeze seam 2026-08-31T15:22Z).**
   The live tree mutates *while* it is read. Measured: `docs/COLLECTOR.md`
   was rewritten at 21:30:48 and again at 21:31:24 (constant 212,832 bytes, different
   sha256 each time) during this session. A whole-tree manifest is therefore stale the
   moment it is sealed. **`builds/backup/cosmos_backup.py` now REFUSES `SOURCE_MUTATED`
   and does not seal `MANIFEST` if any named source file changes after the walk**
   (torn snapshot would otherwise VERIFY — copies match the walk-time hashes).
   Bite `_bite_f43_mutate_retire.json` `all_bite:true` (incumbent sealed
   `BACKUP_OK`). Live `_f43_mutate_retire_live.json` `mutated_kind=SOURCE_MUTATED`
   `manifest_sealed:false` `incomplete_left:true`. **Freeze seam landed:**
   `do_backup(..., freeze=)` copies from a point-in-time read-root
   (`builds/backup/cosmos_backup_freeze.py`). Default is still detect-and-refuse.
   `freeze=True` asks Win32_ShadowCopy; no shadow is typed `VSS_UNAVAILABLE`
   (never a silent live-tree copy under a freeze flag). Tests inject
   `FrozenTree.capture`. Live `_f43_freeze_live.json` `frozen_survived:true`
   `frozen_kind=copy`; `V:\` NTFS `drive_type=3` `kind=VSS_UNAVAILABLE`
   `scode=0x80041014`. Bite `_bite_f43_freeze.json` `all_bite:true`;
   predecessor 4/4 FAIL. The *scheduled* `cosmos/` clock does not have this
   check (outside this fence).
4. **Backups contain secrets (detect landed 2026-08-31T14:10Z for this
   implementation; PEM classification 2026-08-31T16:46Z).** The *scheduled*
   `cosmos/` sets still include `config/install_key.bin` (outside this fence).
   **`builds/backup/cosmos_backup.py` `do_backup` REFUSES `SECRETS_IN_SCOPE`**
   before a set is created. Credential path-shapes (`install_key.bin`,
   `api_token.txt`, `.pfx`, `.p12`, …) still refuse by name and are never
   opened. PEM-like suffixes (`.pem`, `.key`, `.crt`, `.cer`, `.cert`) are
   classified by BEGIN label: `BEGIN CERTIFICATE` is public (a vendored
   certifi `cacert.pem` is not key material); `BEGIN RSA/EC/OPENSSH/PGP
   PRIVATE KEY` and `BEGIN ENCRYPTED PRIVATE KEY` still refuse; unknown,
   empty, or unreadable is fail-closed. Predecessor treated every `.pem` as
   a secret and ignored `.key` content — that permanently blocked offsite
   backup of `builds/` (`gdx/builds` `SECRETS_IN_SCOPE` on
   `cvm-dt/vendor/whisper_site/certifi/cacert.pem`, measured 16:39Z). Bite:
   `_fail_pem_classify_against_old.json`. The scheduled `cosmos/` clock does
   not call this check (outside this fence).
5. **No retention (policy landed 2026-08-31T12:46Z; never-delete).** Every run
   still writes a full copy. **`do_retire(dest, keep>=1)` now stages oldest
   finished sets to `dest/_delme/predispose_<set>_<utc>/`** — never deletes;
   `keep<1` is `KEEP_TOO_SMALL` (retiring the last copy is forbidden); CLI
   `retire --dest-root --keep N` and optional `run --keep N`. Live
   `_f43_mutate_retire_live.json` `retire_kind=RETIRE_OK` `never_deleted:true`
   `staged_verifies:true`. Opt-in: omit `--keep` and nothing is staged (no
   invented default). The scheduled `cosmos/` clock does not call this
   (outside this fence). R2 lifecycle remains a bucket policy (offsite_clock
   never DELETEs).

## What this directory now proves (bound to emitted values)

- `test_cosmos_backup.py` — **90 OK, 1 skipped** (`COSMOS_TEST_DOCS`). HMAC
  (`SEAL_HMAC_MISMATCH`) and verify-on-write (`COPY_HASH_MISMATCH`) pinned
  2026-08-31T12:05Z; bite `_bite_hmac_copyhash.json`. Restore fail-closed
  kinds pinned 2026-08-31T12:34Z (`STAGE_OCCUPIED`, `RESTORE_HASH_MISMATCH`,
  `REHEARSAL_HASH_MISMATCH`, `SOURCE_NOT_DIR`, `NOT_A_BACKUP_SET`); bite
  `_bite_stage_restore.json` `all_bite:true`; live
  `_stage_restore_live.json` all five kinds match, stage and dest
  untouched on `STAGE_OCCUPIED`. **F-43 leftover 2026-08-31T12:46Z:**
  `SOURCE_MUTATED` (torn snapshot) and `do_retire` (`KEEP_TOO_SMALL` /
  `RETIRE_OK` / `DEST_NOT_DIR` / `RETIRE_DEST_OCCUPIED`); bite
  `_bite_f43_mutate_retire.json` `all_bite:true`; new pins **10/10 FAIL**
  against predecessor; live `_f43_mutate_retire_live.json` `ok:true`.
  **Round-2 unpinned 2026-08-31T13:42Z:** `do_backup` dest-is-a-file is
  `DEST_NOT_DIR` (was untyped `FileNotFoundError`); `_copy` onto an
  existing directory is `COPY_IO_ERROR` and does not clobber. Bite
  `_bite_unpinned_round2.json` `all_bite:true`; new pins **2/2 FAIL**
  against staged predecessor.
  **Round-3 unpinned 2026-08-31T13:54Z:** `do_retire(keep=True)` is `KEEP_TOO_SMALL`
  (`True` is an `int`); dest-is-a-file on `do_retire` is `DEST_NOT_DIR`;
  `pack()` dest-is-a-file is now `DEST_NOT_DIR` (was untyped `FileExistsError`);
  `identity.kind=volume_serial` mismatch is `IDENTITY_MISMATCH`; FakeProbe
  unknown volume is `DRIVE_NOT_MOUNTED`. Bite `_bite_unpinned_round3.json`
  `all_bite:true`; fail-against-old **4/4 FAIL**
  `all_new_pins_failed:true`.
  **Round-4 unpinned 2026-08-31T14:22Z:** measured-but-wrong `identity.kind=model`
  is `IDENTITY_MISMATCH` (was bind); sentinel field mismatch is
  `IDENTITY_MISMATCH` (was bind); identity-not-object / config JSON array /
  `targets` list are `BAD_CONFIG` (were `AttributeError` or silent return);
  empty/whitespace R2 credential field and JSON `true` are `BAD_CREDENTIALS`
  (were accept / `TypeError`). Bite `_bite_unpinned_round4.json`
  `all_bite:true`; fail-against-old **7/7 FAIL**
  `all_new_pins_failed:true`. Then `test_backup_mounts.py` **41/41**,
  `test_cosmos_backup_r2.py` **39/39**.
  **Round-5 unpinned 2026-08-31T14:42Z:** `check_seal` of a JSON array or a
  string `seal` is `NO_SEAL` (was `AttributeError`);
  `LocalDirTarget.get_artifact` of `{not json` / `[]` is `NOT_A_BACKUP_SET`
  (was `JSONDecodeError` / returned a list); `R2Target.get_artifact` of
  `{not json` / `true` is `NOT_A_BACKUP_SET` (was `JSONDecodeError` /
  returned a bool). Bite `_bite_unpinned_round5.json` `all_bite:true`;
  fail-against-old **5/5 FAIL** `all_new_pins_failed:true`. Then
  `test_cosmos_backup.py` **68 OK, 1 skipped**,
  `test_cosmos_backup_r2.py` **41/41**, `test_backup_mounts.py` **41/41**.
  **Round-6 unpinned 2026-08-31T16:12Z:** a freeze handle with
  `read_root`+`release` but no `info()` was accepted by `acquire()` and
  then `AttributeError` in `do_backup` (predecessor
  `_bite_unpinned_round6.json` `noinfo_dobackup_crash=AttributeError`).
  `acquire()` now requires `info()`; missing is typed `BAD_FREEZE`.
  `BAD_FREEZE` (garbage freeze=) and `FREEZE_DEST_OCCUPIED` (capture dest
  exists, including dest-is-a-file) were documented and raised but
  unnamed in this suite; they are now pinned. Bite `all_bite:true`;
  fail-against-old **2/2 FAIL** `all_new_pins_failed:true`. Then
  `test_cosmos_backup.py` **80 OK, 1 skipped**.
  **Round-6b unpinned 2026-08-31T16:19Z:** `seal([])` / `seal(None)` /
  `seal("x")` were `AttributeError` (check_seal was typed in round 5;
  seal() was not). `scan_secrets({})` was `KeyError`; `[]` / `files=None`
  / `files=1` were `TypeError`; `files="install_key.bin"` **silently
  returned `[]`** — a string iterates as characters, so a secret name
  as a string was "no secrets". Now `NO_SEAL` / `NOT_A_BACKUP_SET`.
  Bite `_bite_unpinned_round6.json` `untyped_seal=AttributeError`
  `scan_files_str_silent:true`; fail-against-old **8/8 FAIL**
  `all_new_pins_failed:true`. Then `test_cosmos_backup.py` **90 OK, 1
  skipped**, `test_cosmos_backup_r2.py` **43/43**,
  `test_local_clock.py` **25/25** (relative dest `BAD_CONFIG`, dest-is-a-file
  `DRIVE_NOT_MOUNTED`, `targets.local` list `NO_DEST` — already typed,
  now named).
  **F-43 identity leftover 2026-08-31T16:30Z:** `local_row()` returned
  `targets.local.identity` and `bind_local()` never called
  `_check_identity` — a swapped disk at the same letter still
  `VERIFIED`. Bite `_bite_f43_identity.json` `all_bite:true`
  (`mismatch_tick_verified:true` `mismatch_created_a_set:true`
  `bind_local_has_identity_param:false`). Fail-against-old **6/6 FAIL**
  `all_new_pins_failed:true`. Live `_f43_identity_live.json` `ok:true`
  `mismatch.kind=IDENTITY_MISMATCH` `sets=[]` `match.state=VERIFIED`.
  Then `test_local_clock.py` **31/31**. Live `--preflight` still
  `NO_CONFIG` `heartbeat_written:false`.
  **Local whole-tree scope 2026-08-31T17:21Z:** measured 16:50Z
  `cosmos_local_clock --once` `SOURCE_UNREADABLE`
  `live/logs/cdeck_feed.lock` PermissionError — runtime locks were in
  scope because tick() passed `DEFAULT_EXCLUDES` (`.git`, `__pycache__`)
  only. Walker now matches path prefixes + `*.lock` *before* open;
  `targets.local.excludes` is per-target (unioned with
  `LOCAL_DEFAULT_EXCLUDES`). Call, in the clock: `*.lock` / `live/logs`
  / `live/work` / `live/backups` / `live/returns` / `_delme` are not
  data; `live/ledger` stays in; `live/config` and `trylive/config` and
  credential basenames never copy to the unencrypted dest. Unreadable
  *in-scope* data still REFUSES. Bite `_fail_local_excludes_against_old.json`
  **2/2 FAIL** `all_new_pins_failed:true` (old named
  `live/logs/cdeck_feed.lock` PermissionError). Then
  `test_local_clock.py` **38/38**, `test_cosmos_backup.py` **104 OK, 1
  skipped**, `tests/test_backup_local_excludes.py` **2/2**. Live
  `--once` 17:21Z hashed the whole tree (locks out of scope) and copied
  **16205 files / 7,698,536,901 bytes** onto
  `D:\COSMOS_BACKUP\COSMOS-20260831T172140` (`live/config` absent,
  `*.lock` absent) then `COPY_HASH_MISMATCH` on
  `cosmos/_f03_test_spend_post.json` — fail-closed verify-on-write
  against a tree other sessions were mutating; not the lock defect.
  Retry 17:33Z same kind on `builds/backup/_f43_clock_live_preflight.json`.
  Bound in `_local_excludes_live.json`.
- `prove_roundtrip.py` — the drill: copy real files OUT of a tree, back them up, flip one
  byte in the scratch copy, restore, re-hash. Prints every sha256 and seals a
  `ROUNDTRIP_PROOF.json`. Never writes the tree it samples.
- `cosmos_backup_r2.py` + `test_cosmos_backup_r2.py` — the R2 offsite leg (29 tests).
  Gap 1 (same-volume) now has a destination that is not this machine, blocked on ONE
  thing: the credential. See `docs/R2_OFFSITE_PLAN.md`.
- `cosmos_mount_clock.py` + `test_mount_clock.py` — the GDX/ODX/ES.3 scheduled
  push (34 tests). Without dests: typed `NO_CONFIG`, heartbeated, rc=2. With
  FakeProbe: verify-on-write onto a scratch dest. `--plan-task` registers nothing.
- `cosmos_state_offsite.py` + `test_state_offsite.py` — F-54 payload packer (18
  tests; dest-is-a-file is `DEST_NOT_DIR`). Packs SEED / SEED.decl / inflight / motif_tracker (never live/state
  wholesale). Without dest AND without credential: typed `NO_OFFSITE_ROUTE`,
  rc=2, no heartbeat on `--preflight`. Live: `_f54_live_preflight.json`
  `payload.present=4` `bytes=293610` (re-measured 2026-08-31T13:26Z;
  `describes` pins `cosmos_state_offsite.py` so a later edit cannot hide
  behind this number). 254853 was the 11:30Z snapshot.

## Gap 1 update — the offsite leg exists (2026-08-31)

`R2Target` is no longer a `NotImplementedError` seam. SigV4 signing is stdlib
(`hmac`/`hashlib`), CONFIRMED against AWS's published vectors; the transport is
injected, so `selfcheck` proves sign → PUT → GET → re-hash → seal against an in-memory
bucket with **zero credentials and zero network**. Measured on real tree files
2026-08-31T05:10:56Z: 12 files, 221,309 bytes, `readback_verified == files_pushed`.

Still **UNMEASURED**: the wire. No byte has gone to R2. Blocked on
`live/config/r2_credentials.json`, which is absent (measured — 11 files in `config/`,
not that one). `rclone`, `aws`, `boto3`, `botocore` are all absent too and are all
deliberately unnecessary.

Gap 4 (backups contain secrets) is now **fail-closed for the remote path**: a push
whose scope holds key material refuses `SECRETS_IN_SCOPE` by manifest path alone,
before the first request, with no override flag. It does not open the file.

**New measured gap — long paths.** *(Superseded by the re-measurement below. Recorded
here as written: `V:\Ai` holds 2,091 files >260 chars and `build_manifest` refuses
`SOURCE_UNREADABLE`. The count was the class-A subtotal, and the refusal did not
happen — see below.)*

Wishlist scope, measured 2026-08-31 (`os.walk`, `__pycache__` excluded):
`V:\Research4` 79,533 files / 24.21 GiB · `V:\Ai` 15,107 / 11.37 GiB ·
`V:\A` 55,864 / 29.84 GiB — **150,504 files, 65.42 GiB** total.
*(That walk was unprefixed, so it could not see past MAX_PATH. Prefixed re-walk below:
152,694 files.)*

## Long paths — RE-MEASURED 2026-08-31T05:36–05:47Z

Full finding, both proposals and every caveat: **`docs/LONGPATH_FINDING.md`**.
Probe: `builds/probe/longpath_census.py` (`census` · `realscope` · `behave`).
`LongPathsEnabled` = **0** on this machine, so the `\\?\` prefix is required.

### The true numbers

| tree | files (prefixed walk) | >259 chars | class A | class B | longest |
|---|---|---|---|---|---|
| `V:\Ai` | 17,232 | **2,125** | 2,091 | 34 | **412** |
| `V:\A` | 55,924 | 14 | 8 | 6 | 275 |
| `V:\Research4` | 79,538 | 4 | 4 | 0 | 267 |
| **total** | **152,694** | **2,143** | **2,103** | **40** | **412** |

**class A** (2,103) — directory lists, file path too long: `Path.is_file()` swallows
`winerror=3` and returns `False`, so the file is **filtered out with no error**.
**class B** (40) — directory path itself too long: `os.walk(onerror=None)` swallows
the `scandir` failure, so the **subtree is never seen**. 147 swallowed enumeration
errors across the three trees. The earlier 2,091 is exactly the class-A subtotal for
`V:\Ai`; it was a real count of a real class, not the whole one.

### What each walker actually did (fixture: real 300- and 303-char files)

| module | scheduled | before | after |
|---|---|---|---|
| `cosmos/cosmos_backup.py` | **YES, 4x daily** | `SILENTLY_OMITS` — 1 of 3 files, ledger `BACKUP_VERIFIED` | proposal only, not applied (outside fence) |
| `cosmos/cosmos_backup_clock.py` | **YES, 4x daily** | `SILENTLY_OMITS` — copied 1 of 3 | proposal only, not applied |
| `builds/backup/cosmos_backup.py` | no | `SILENTLY_OMITS` — 1 of 3 | **`COVERS_LONG_PATHS` — 3 of 3** |

On real bytes, `V:\Ai\_session_logs\_mcp_logs` (2,129 files, 2,124 of them long):
`iter_files` selected **5, raised nothing** → after the fix, **2,129, omitted 0**.

### Gap 6 (new) — the scheduled backup omits silently

**Gap 1–5 above stand.** This is the sixth, and it is the green-log defect the canon
names, sitting in the one module whose job is to be trustworthy: `Backup.run` appends
`BACKUP_VERIFIED` over a scope it silently shortened. **Not firing today** — the
bounded snapshot's longest destination path is 98 chars, 161 to spare — and unbounded
tomorrow, because `docs/R2_OFFSITE_PLAN.md` §5 step 5 points this same engine at the
65 GiB wishlist trees where it drops 2,143 files.

Related, measured the same run: **`queue/manifests` holds 351 files against gap 2's
hard 400-file cap** — 87% of the way to a silent truncation that would still report
`VERIFIED`. The proposal closes gap 2 and gap 6 with one change (`_copy_tree_files`
returns a hole record; `assemble_snapshot` raises `SNAPSHOT_INCOMPLETE`).

### Gap 7 (new) — `cosmos_backup_clock` crashes on every invocation

`json.dumps` at lines 195/201/204, no `import json`. Measured:
`NameError: name 'json' is not defined`. The heartbeat is written *before* the crash,
so the backup really runs and really says `VERIFIED` while the process exits non-zero
— **the health watchdog and Task Scheduler have disagreed about every run since the
module was written.** One line, in the same proposal.

### This directory's coverage now

- `test_cosmos_backup.py` — **51 OK, 1 skipped** (`COSMOS_TEST_DOCS`).
  **Pinned 2026-08-31T12:05Z:** `SEAL_HMAC_MISMATCH` (forged / missing /
  null / wrong-key HMAC) and `COPY_HASH_MISMATCH` (verify-on-write). Both
  kinds were in the module's refusal set and in prose; neither was named
  by a test. Bite `_bite_hmac_copyhash.json` `all_bite:true` — a
  sha256-only `check_seal` accepted a forged HMAC, the incumbent crashed
  TypeError on `hmac_sha256: null`, and a `do_backup` without the
  post-copy re-hash sealed a MANIFEST over a flipped byte. Live after
  the coerce: `_hmac_copyhash_live.json` both kinds `SEAL_HMAC_MISMATCH`.
  **Pinned 2026-08-31T12:34Z:** `STAGE_OCCUPIED` (occupied stage slot is
  never overwritten in place), `RESTORE_HASH_MISMATCH` / `REHEARSAL_HASH_MISMATCH`
  (re-hash after retrieve), `SOURCE_NOT_DIR`, `NOT_A_BACKUP_SET`. All five
  sit in the kind set and in `do_restore` / `build_manifest` prose. Bite
  `_bite_stage_restore.json` `all_bite:true` — without the guards, restore
  clobbered `PRECIOUS` and still sealed `RESTORE_OK`, a flipped retrieve
  sealed `REHEARSAL_PASS`, a file-as-source was `SOURCE_UNREADABLE`, and an
  empty folder `FileNotFoundError`d untyped. The new pins **5/5 FAIL**
  against the stripped predecessor (`_fail_stage_restore_against_old.json`).
  Live `_stage_restore_live.json` all five kinds match; `stage_untouched`
  and `dest_untouched` true on `STAGE_OCCUPIED`.
  **Pinned 2026-08-31T12:46Z:** `SOURCE_MUTATED` (re-hash sources after
  copy; a torn snapshot does not seal `MANIFEST`) and `do_retire`
  (`KEEP_TOO_SMALL` / `RETIRE_OK` / never-delete staging). Bite
  `_bite_f43_mutate_retire.json` `all_bite:true` — incumbent sealed
  `BACKUP_OK` over a mutated `a.txt` and had no `do_retire`. New pins
  **10/10 FAIL** against
  `_delme/predispose_cosmos_backup_f43_20260831T124639Z/`
  (`_fail_f43_against_old.json`). Live `_f43_mutate_retire_live.json`
  `ok:true` `mutated_kind=SOURCE_MUTATED` `manifest_sealed:false`
  `retire_kind=RETIRE_OK` `never_deleted:true` `staged_verifies:true`
  `keep_zero_kind=KEEP_TOO_SMALL`.
  **Pinned 2026-08-31T13:09Z (verification hardening):** `SCRATCH_NOT_EMPTY`
  (local `do_rehearse` — occupied scratch must not seal `REHEARSAL.json`;
  the kind was in the set and the test raised `BackupRefusal` without
  naming it) and `COPY_IO_ERROR` (`_copy` missing src). Bite
  `_bite_unpinned_refusals.json` `all_bite:true` — without the scratch
  guard, occupied scratch sealed `REHEARSAL_PASS`; missing src was
  untyped `FileNotFoundError`. New pins **8/8 FAIL** against stripped
  modules (`_fail_unpinned_against_old.json` `all_new_pins_failed:true`).
  Live `test_cosmos_backup.py` **53 OK, 1 skipped**.
- `test_cosmos_backup_r2.py` — **36 tests.** **Pinned 2026-08-31T13:09Z:**
  `R2_UNREACHABLE` (UrllibTransport OSError; injected urlopen, no socket).
- `test_offsite_clock.py` — **Pinned 2026-08-31T13:09Z:** `BAD_SCOPES`
  (malformed JSON / empty list / missing name / missing source). Prose
  said load_scopes REFUSES rather than inventing a default tree; only
  `NO_SCOPES` (absent file) was named.
- `test_backup_mounts.py` — **Pinned 2026-08-31T13:09Z:** unknown
  `identity.kind` is `BAD_CONFIG` (existence of the dest dir is not
  identity). Without the else-raise, bind succeeded.
- `test_longpath.py` — **10 tests, new.** Real 300/303-char files created through the
  prefix; both classes; the full backup → verify → rehearse → restore round trip past
  MAX_PATH including the destination side; both refusal paths; the `_x()` shapes.
  Runs unskipped on POSIX by design (long paths are legal there) — but has only ever
  been executed on Windows.

**Still not covered by anything scheduled:** everything in the table at the top of this
file, plus every long-path file in any tree the *scheduled* backup is ever pointed at,
until the `cosmos/` proposals in `docs/LONGPATH_FINDING.md` §9 are disposed.
