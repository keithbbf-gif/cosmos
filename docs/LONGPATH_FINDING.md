# MAX_PATH — the backup gap that reports success over a hole

**Consumer:** COW + the backup / R2 work orders. **Origin:** the blocker filed by the
previous job on this lane (`live/queue/_lanes/cc-infra/returns/080_r2_offsite_result.json`)
— *"V:\Ai push refuses SOURCE_UNREADABLE on 2091 MAX_PATH files until the walker uses
the `\\?\` prefix."* **Measured 2026-08-31T05:36–05:47Z**, this machine, `py -3.14`.

Every number here came from a run. The probe is
`builds/probe/longpath_census.py` (three verbs: `census`, `realscope`, `behave`);
its raw output is `builds/probe/_longpath_census.json`,
`_longpath_realscope.json` / `_longpath_realscope_after.json`, and
`_longpath_behaviour.json`. Anything not measured is labelled **UNMEASURED** and is
not rounded into a fact.

---

## 1. The headline, in one line

**The scheduled backup does not refuse on long paths. It omits them and appends
`BACKUP_VERIFIED`.** That is worse than the blocker as filed, and it is the failure
class the canon names by name.

Measured against a real 300-character file, `behave` verb:

```
LongPathsEnabled = 0 | files on disk = 3
  fixture shallow  len= 60 plain_stat_ok=True
  fixture class_a  len=300 plain_stat_ok=False
  fixture class_b  len=303 plain_stat_ok=False

SILENTLY_OMITS     cosmos/cosmos_backup.py
                   state=RETURNED returned=1 missed=['class_a', 'class_b']
                   ledger=['BACKUP_VERIFIED']
SILENTLY_OMITS     cosmos/cosmos_backup_clock.py
                   state=RETURNED returned={'copied': 1} missed=['class_a', 'class_b']
```

`cosmos/cosmos_backup.py` is the module `cosmos_backup_clock` drives on four daily
`schtasks` (07/11/19/23). It is the only backup COSMOS runs. Three files on disk,
one in the backup, `BACKUP_VERIFIED` in the ledger, no error anywhere.

## 2. Correction to the filed blocker — the number, and the severity

**The count.** 2,091 was right for the class it measured, and is exactly reproduced
here (`class_a_dir_listable` for `V:\Ai` = 2,091). It is not the whole count. The true
figure for `V:\Ai` is **2,125**, and across the three WISHLIST trees **2,143**.

**The severity.** The blocker records that `build_manifest` "correctly raises
`SOURCE_UNREADABLE` rather than skipping them". **Measured, it does not** — the files
never reach `build_manifest`. `iter_files` filtered them out first, on
`Path.is_file()`, which swallows the error and answers `False`. On real bytes:

```
$ py -3.14 builds/probe/longpath_census.py realscope --root V:\Ai\_session_logs\_mcp_logs
 "files_ground_truth": 2129,
 "long_in_scope": 2124,
 "builds_backup_iter_files": {
  "selected": 5, "raised": null, "omitted": 2124, "verdict": "SILENTLY_OMITS" }
```

**Five files selected out of 2,129, and nothing raised.** The `SOURCE_UNREADABLE`
guard in `build_manifest` is real and correct — it was simply unreachable for this
class. A guard behind a filter that removes the thing it guards against is not a guard.

## 3. Two failure classes — a fix for one is not a fix for the other

| | what is too long | what the OS does | what a plain walker does |
|---|---|---|---|
| **class A** — 2,103 files | the FILE path (dir still lists) | `scandir` returns the name; `stat`/`open` fail `winerror=3` | `Path.is_file()` swallows it, returns `False` → **filtered out, no error** |
| **class B** — 40 files | the DIRECTORY path itself | `scandir` cannot descend | `os.walk(onerror=None)` swallows it → **subtree never seen** |

Measured: **2,103 of 2,103** class-A files return `is_file() == False`, and **40**
files are invisible to a plain `os.walk` (147 swallowed `scandir` errors across the
three trees). Both classes end the same way — coverage claimed over a hole — so both
need fixing, and the two halves of the fix are different code.

## 4. The census — measured 2026-08-31T05:44Z

`os.walk` through `\\?\`, `__pycache__` excluded. MAX_PATH is 260 *including* the
terminating NUL, so **259** is the last length a plain Win32 call accepts; both
thresholds were counted and here they are identical.

| tree | files | >259 chars | class A | class B | invisible to plain walk | longest path |
|---|---|---|---|---|---|---|
| `V:\Ai` | 17,232 | **2,125** | 2,091 | 34 | 34 | **412** |
| `V:\A` | 55,924 | 14 | 8 | 6 | 6 | 275 |
| `V:\Research4` | 79,538 | 4 | 4 | 0 | 0 | 267 |
| **total** | **152,694** | **2,143** | **2,103** | **40** | **40** | **412** |

All 2,143 fail `os.stat()` unprefixed; every failure is `winerror=3`, i.e. path
length, not permissions and not missing files.

`HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled` = **0** on this
machine, so the prefix is required. (Setting it to 1 is *not* the fix: it is a
machine-wide change that a peer install on a cold machine would not inherit, and
COSMOS is built to be installed by a peer.)

The deepest file, 412 characters — the shape is Claude session transcripts whose
directory name already encodes an absolute path:

```
V:\Ai\Legal\_transcripts\sessions\598a803e-7ed8-4011-8c6f-36b1139ced47\
  ccd03d6b-a1bb-44c5-a4d3-100b4b78f91f\local_a1f6b07b-30ca-4482-a22d-a0a8e93da6d5\
  .claude\projects\C--Users-Papa-AppData-Roaming-Claude-local-agent-mode-sessions-
  598a803e-...-outputs\STRIPPED_bc05144b-b005-49c3-8aff-e4b57b6bc01f.md.partial
```

These are not junk. `V:\Ai\Legal\_transcripts` is legal-stream material.

## 5. Is the RUNNING backup at risk *today*? — the honest answer

**The defect is present and proven (§1). It is not firing today, and it is unbounded
tomorrow.** Both halves matter; neither cancels the other.

The scheduled snapshot is bounded (`ledger`, `config/*`, `state/SEED*`,
`state/control`, `queue/sched_ledger.jsonl`, `queue/manifests`). Measured headroom to
the destination path, `live\backups\verified\<stamp>\`:

| staged subtree | files | longest resulting dest path | headroom |
|---|---|---|---|
| `ledger` | 2 | 80 | 179 |
| `state/control` | 1 | 77 | 182 |
| `queue/manifests` | **351** | 98 | 161 |

So **no file is being dropped by the current scheduled run**, and the last heartbeat
is consistent with that (`live/logs/backup_clock_heartbeat.json`: `"state":
"VERIFIED", "files": 360, "staged": 360`, 2026-08-30T23:00:07-05:00).

What makes it serious anyway:

1. **The scope is the only thing holding it back, and the scope is scheduled to grow.**
   `docs/R2_OFFSITE_PLAN.md` §5 step 5 points the backup at `V:\Research4`, `V:\Ai`,
   `V:\A` — 65 GiB where the defect fires on 2,143 files immediately.
2. **`queue/manifests` is at 351 files against a hard 400 cap** — 87% of the way to a
   silent truncation, in the *same function*, with the *same* symptom (`VERIFIED` over
   a short scope). `COVERAGE.md` gap 2 records the cap; this is the measurement of how
   close it is.
3. **A latent silent-omission bug in the one module whose job is trustworthiness is
   not a low-severity bug.** It is the exact thing the ledger exists to make impossible.

## 6. Separate defect found while measuring — `cosmos_backup_clock` crashes on every run

`cosmos/cosmos_backup_clock.py` calls `json.dumps` at lines 195, 201 and 204 and
**never imports `json`**. Measured, read-only verb:

```
$ py -3.14 cosmos/cosmos_backup_clock.py --root V:/A/Ai/COSMOS/live --status
  File "V:\A\Ai\COSMOS\cosmos\cosmos_backup_clock.py", line 195, in main
    print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
NameError: name 'json' is not defined. Did you forget to import 'json'?
```

All three exits from `main()` hit it. `poll_once` writes the heartbeat **before** the
crash, which is why the backup genuinely runs and the heartbeat genuinely says
`VERIFIED` — and then the process dies non-zero. **The health watchdog and Task
Scheduler therefore disagree about every single backup run, and have since the module
was written.** One-line fix, included in the proposal. The scheduled task's recorded
last-result is **UNMEASURED** — `schtasks /query` was denied to this agent.

## 7. The fix, and the Windows caveats it has to honor

Two parts. Both are required; either alone still loses files.

**Part 1 — prefix the ROOT, once.** `os.walk` on a `\\?\`-prefixed root produces
prefixed `dirpath`s, so every descendant inherits the prefix for free. That is why
this is a small change and not a conversion sprinkled over every call site.

**Part 2 — stop swallowing.** Replace `os.walk`'s default `onerror=None` with one that
REFUSES, and replace error-swallowing predicates (`Path.is_file()`, `except OSError:
continue`) with a single `lstat` that refuses. With part 1 alone, a permissions error
still silently deletes a subtree from the backup.

**Caveats of `\\?\`, each honored in the code:**

| caveat | consequence | handling |
|---|---|---|
| It disables **all** path normalization | `/`, `.`, `..`, trailing dots/spaces are taken literally and the call fails | `os.path.abspath()` before prefixing |
| Requires an **absolute** path | a relative path cannot be prefixed at all | same `abspath` |
| UNC takes a different shape | `\\server\share` → `\\?\UNC\server\share` | explicit branch |
| Windows-only | prefixing on POSIX would corrupt the path | `os.name != "nt"` → identity, so the module stays portable and its POSIX behaviour is unchanged |
| Must never double-prefix | `\\?\\\?\V:\…` is invalid | startswith guard |
| The **destination** needs it too | a backup set dir + a 240-char relative key is longer than the source | `_copy` / `_xmkdirs` / `os.replace` all go through it |
| It lifts the limit to ~32,767 | COSMOS can now read files Explorer and most tools still cannot | stated, not worked around |
| It bypasses DOS device-name reservation | `CON`, `NUL`, `AUX` become legal filenames | no new exposure here — this walker only reads names the filesystem already holds |

A module-local `_x()` is used rather than importing `cosmos_paths.extended` on purpose:
`builds/backup/cosmos_backup.py` is stdlib-only and root-agnostic by design (every root
arrives as a parameter), and importing the resolver would require a COSMOS root to exist.
`cosmos_paths.extended` remains the canonical implementation and the two agree by
construction — same four branches, same order.

## 8. DONE (in fence) — `builds/backup/`

`iter_files` rewritten per §7, and every filesystem touchpoint in the module routed
through `_x()`: `sha256_file`, `_write_json_atomic`, `_copy`, `_check`,
`LocalDirTarget` (`exists`/`mkdir`/`is_dir`/`get_artifact`), `emit_incident`,
`heartbeat`, `do_backup`, `do_rehearse`, `do_restore`.

Net: **+142 / −30 lines**, of which **59 are comment or blank** — the `\\?\` caveat
table above lives in the module, next to the code that honors it, because the next
person to touch `iter_files` needs it there and not here. Executable delta is **+83**.
Against that, the walk now costs **one** `lstat` per entry where it previously issued
`is_symlink()` + `is_file()` — two syscalls, both of them error-swallowing, which is
how the hole opened in the first place.

Proven three ways:

- **Fixture** — `builds/backup/test_longpath.py`, **10 tests**, creating real 300- and
  303-character files through the prefix. Covers both classes, the full
  backup → verify → rehearse → restore round trip past MAX_PATH (destination side
  included), the two refusal paths, and the `_x()` shapes.
- **Real bytes** — the same `realscope` probe as §2, re-run against the fixed module:
  `"selected": 2129, "omitted": 0, "verdict": "COVERS_LONG_PATHS"`. **5 → 2,129.**
- **No regression** — the pre-existing suites stay green: `test_cosmos_backup.py`
  19 tests (1 skipped, needs `COSMOS_TEST_DOCS`), `test_cosmos_backup_r2.py` 29 tests.

## 9. PROPOSALS — outside this fence, for COW to dispose

`cosmos/` is not this agent's fence, so nothing there was touched. The proposals are
**complete proposed files**, not prose:

- `builds/probe/proposed/cosmos_backup.py` → target `cosmos/cosmos_backup.py`
- `builds/probe/proposed/cosmos_backup_clock.py` → target `cosmos/cosmos_backup_clock.py`
- `builds/probe/proposed/_PROPOSED.diff` — the unified diff, **+171 / −42**, regenerable
  with `py -3.14 builds/probe/proposed/_make_diffs.py`

**They were RUN, not merely written.** Loaded by path and put through the identical
fixture as the live modules (`behave` verb, same output block as §1):

```
COVERS_LONG_PATHS  PROPOSED cosmos/cosmos_backup.py
                   state=RETURNED returned=3 missed=[]  ledger=['BACKUP_VERIFIED']
COVERS_LONG_PATHS  PROPOSED cosmos/cosmos_backup_clock.py
                   state=RETURNED returned={'copied': 3, 'truncated': False,
                                            'unreadable': [], 'skipped_large': 0} missed=[]
```

What each contains:

1. **`cosmos_backup.py`** — `_x()` helper; `_walk_files()` replaces
   `rglob('*') + is_file()`; `_sha`, `copy2`, `makedirs`, the manifest write and the
   rehearsal restore all go through the prefix. New refusal kind `SOURCE_UNREADABLE`.
2. **`cosmos_backup_clock.py`** — the same `_x()`; `_copy_tree_files` walks prefixed and
   **returns a record** (`copied` / `truncated` / `unreadable` / `skipped_large`)
   instead of a bare int, because a bare int cannot express a hole;
   `assemble_snapshot` raises `SNAPSHOT_INCOMPLETE` on either, which closes
   `COVERAGE.md` gap 2 (the 400-file cap) with the same change. **Plus the missing
   `import json`** (§6).

Two judgement calls COW should know about before applying:

- **`SNAPSHOT_INCOMPLETE` will make a truncating run FAIL where it now says VERIFIED.**
  That is the point — but with `queue/manifests` at 351/400 it is a refusal Keith
  should expect to see soon, and the remedy is to raise or remove the cap, not to
  restore the silence. Applying part 1 (the prefix) without part 2 (the refusal) is a
  coherent smaller step if COW wants the cap decision separated.
- **`_copy_tree_files` changes its return type**, so any other caller must be checked.
  Measured: `assemble_snapshot` is the only caller in the repo, and it is updated in
  the same file.

Still open from `docs/R2_OFFSITE_PLAN.md` §8 and unaffected by this shift: wiring
`ADAPTERS["r2"]`, adding `__pycache__` to `DEFAULT_EXCLUDES`, the `credential_manifest`
R2 row, and the WISHLIST annotation.

## 10. What is UNMEASURED

- **The scheduled task's recorded last-result.** `schtasks /query` was denied. That the
  process crashes is measured (§6); what Task Scheduler *recorded* is not.
- **A real long-path backup of `V:\Ai` end to end.** The fixed walker is proven to
  *select* all 2,129 files of a real subtree; a full 11.37 GiB backup+verify of `V:\Ai`
  has not been run, and no R2 byte has moved (that blocker is unchanged — the
  credential is still absent).
- **Whether other COSMOS walkers share the defect.** This shift measured the three
  backup walkers only. The collector, the ITC indexer and the dispatcher also walk
  trees; they were not probed. `builds/probe/longpath_census.py realscope` will answer
  it for any of them cheaply.
- **POSIX behaviour** of the changed modules. `_x()` is the identity function there by
  construction and `test_longpath.py` is written to run unskipped on POSIX, but it has
  only ever been executed on Windows.
