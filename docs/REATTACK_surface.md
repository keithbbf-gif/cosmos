# REATTACK — surface cluster

**Critic, not builder.** Target: `main` after the stage-7 merge (`483e0fe`, K1–K6+H2 closed, 341 checks).  
**Branch:** `reattack/surface`  
**Date:** 2026-08-23  
**Rule:** a finding without a repro that runs is an opinion.

```
PYTHONPATH=cosmos python3 tests/reattack_surface_repros.py
```

12/12 findings in that script REPRODUCED on this tree. Raw transcript: this file, section “Measured run”.

---

## Cluster and method

Surface cluster as attacked:

| module | why it is surface |
|---|---|
| `cosmos_surfaces.py` | storage surfaces; qualification is the backup-target product question |
| `cosmos_ingress.py` | mount-visible write is ingress until the native gate accepts it |
| `cosmos_service.py` / `cosmos_command.py` / `cosmos_mcp.py` | the versioned product API / voice / MCP seams |
| `cosmos_runner.py` | execution of jobs that enter through those seams |
| `cosmos_mail.py` | shared IPC surface; worker-id is a directory name |

Prior attack residuals **in scope if they touch this cluster:**

| residual | touches surface? | this reattack |
|---|---|---|
| ingress `envelope_id` traversal | yes — `_verify_one` | **S-R1, S-R1b, S-R1c** |
| `argv:` runner confinement bypass | yes — job surfaces + runner | **S-R2, S-R2b, S-R2c** |
| worker-id spoofing | yes — ingress sender, mail path, claimed identity | **S-R3, S-R3b, S-R3c** |
| cross-process arbiter serialization | no (lock) | not claimed |
| spend over-cap under overlap | no (spend) | not claimed |
| segment anchor authentication | no (ledger/segments) | not claimed |

Stage-7 closures that **still hold** as negative controls (same process, `test_stage7_fixes.py` PASS):

- K2: `role()` / `protected_write` refuse absolute and `..` parts
- K3: backup manifest `..` → `REHEARSAL_FAILED`
- K4: `py:<path>` outside `tools_root` → `traversal_refused` (the `argv:` form is the hole)
- K5: worker `"B"` cannot `done()` a job claimed by `"A"` (same-name construction is the hole)

---

## Cluster tests (PYTHONPATH=cosmos)

| suite | result | note |
|---|---|---|
| `tests/test_surfaces.py` | PASS 15 | does not ask the role question or the sticker question |
| `tests/test_wave4.py` | PASS 16 | LAN-claim QUALIFIES; that is the S-N2 hole wearing a green check |
| `tests/test_v1.py` | PASS 18 | HTTP API surface |
| `tests/test_tls.py` | PASS 3 | |
| `tests/test_stage7_fixes.py` | PASS 13 | K2/K4/K5 closed *as written* |
| `tests/test_wave3.py` | **CRASH** | `FileNotFoundError: 'py'` — same unhandled launch-fail as **S-R2c** |
| `tests/test_browser.py` | **CRASH** | headless Chrome 60s timeout in this environment (not claimed as a logic defect) |

The existing surface suites are green because they never submit `argv:`, never put `..` in `envelope_id`, never register `CLOUD`+`PUBLISH`, and never age `report()` without re-qualifying.

---

## Findings

### S-R1 — CRITICAL — ingress `envelope_id` path traversal (KNOWN residual)

**Locus:** `cosmos/cosmos_ingress.py` `_verify_one` — `payload_path = self.dir / (env["envelope_id"] + ".payload")`.

Stage-7 confined `role()` and backup-manifest keys. The ingress gate still trusts `envelope_id` as a path fragment. `../` is resolved by the OS; an envelope sitting *inside* the ingress dir can name a payload *outside* it. Hash/length are checked against whatever file that path opens, so a well-formed lie about location ACCEPTs.

**Impact:** the native gate treats a file the sandbox never placed in the ingress directory as an accepted envelope. Confinement of the untrusted surface is broken. Combined with S-R1c, any readable `*.payload` (or, via symlink, any readable file) the service account can open becomes ingress.

**Repro:** `tests/reattack_surface_repros.py` finding `S-R1`.

**Measured:**

```
REPRODUCED  S-R1
accepted_payload=b'TRAVERSAL-SECRET-BYTES'
resolved=.../outside_r1/leaked.payload
under_ingress=False accepted=1 refused=[]
```

---

### S-R1b — CRITICAL — absolute `envelope_id` replaces the ingress root (KNOWN residual sibling)

**Locus:** same join. `pathlib.Path(ingress) / "/abs/secret.payload"` is `/abs/secret.payload`.

**Repro:** `S-R1b`.

**Measured:**

```
REPRODUCED  S-R1b
payload_path=.../abs_secret.payload
accepted=b'ABS-PATH-SECRET'
```

---

### S-R1c — CRITICAL — payload symlink followed (NEW, same gate)

`Path.read_bytes` follows a symlink. An honest `envelope_id` plus a `.payload` symlink to any readable file, with `payload_len`/`payload_sha` matching that file, is ACCEPTED. That is arbitrary file read through the ingress gate.

**Repro:** `S-R1c`.

**Measured:**

```
REPRODUCED  S-R1c
accepted bytes from symlink -> .../symlink_secret.txt: b'SYMLINK-READ-SECRET'
```

Architecture required: native service verifies bytes/hash/schema/**identity** and only then accepts. Location confinement and identity are both missing. Hash agreement is not confinement.

---

### S-R2 — CRITICAL — `argv:` bypasses K4 tools-root confinement (KNOWN residual)

**Locus:** `cosmos/cosmos_runner.py`

```
argv = ["py", "-3.14", "-c", cmd] if not cmd.startswith("argv:") \
    else json.loads(cmd[5:])
```

K4 confines `py:<path>` to `tools_root`. The `argv:` form `json.loads`s the rest and passes that list to `run_tree_killed` with **no** root check, **no** helper-prefix check, **no** allowlist. K4 is a side door with the front door left open.

**Negative control in the same run:** `py:<outside script>` still returns `traversal_refused` and does not execute. Then `argv:[sys.executable, "-c", "open(marker).write(...)"]` runs CLEAN and writes the marker.

**Repro:** `S-R2`.

**Measured:**

```
REPRODUCED  S-R2
K4_held=True argv_ran=True outcome=CLEAN rc=0 marker=True
```

---

### S-R2b — CRITICAL — every product surface accepts `argv:` (KNOWN residual delivery)

`Commander.handle("submit … argv:…")`, `MCPServer` `cosmos_submit`, and `POST /api/v1/jobs` all call `sched.submit` with the raw command string. No confinement policy at the product surface. Three `argv:` jobs landed in one kernel.

**Repro:** `S-R2b`.

**Measured:**

```
REPRODUCED  S-R2b
command_job=… mcp_job=… http_job=… argv_jobs=3
```

---

### S-R2c — HIGH — launch failure leaks; job stays RUNNING (NEW)

`run_tree_killed` → `subprocess.Popen` raises `FileNotFoundError` before `done()`. The runner does not catch it. The job remains `RUNNING`. `test_wave3.py` dies the same way on this host (`'py'` is not on PATH — the runner hard-codes the Windows launcher).

**Repro:** `S-R2c` (`argv:["/no/such/cosmos-bin-r2c"]`). Also: `python3 tests/test_wave3.py`.

**Measured:**

```
REPRODUCED  S-R2c
leaked_FileNotFoundError=True job_state=RUNNING
err="[Errno 2] No such file or directory: '/no/such/cosmos-bin-r2c'"
```

A claimed job that throws is not BROKE. It is a zombie RUNNING, which `report_stale` will only *report*, never complete.

---

### S-R3 — HIGH — ingress sender is an unauthenticated claim (KNOWN residual: worker-id)

**Locus:** `accept_all` ledgers `body["sender"]` after schema/hash checks only. Architecture (OA): the native service “validates its sender identity.” There is no allowlist, key, or mailbox proof. `sender="core"` from a sandbox write is `INGRESS_ACCEPTED`.

**Repro:** `S-R3`.

**Measured:**

```
REPRODUCED  S-R3
claimed_sender=core ledgered_sender=core (no identity check)
```

---

### S-R3b — HIGH — mailbox worker-id is a path component (KNOWN residual)

**Locus:** `cosmos_mail.py` `_inbox` / `_receipts` — `self.root / worker / "inbox"`.

`Mailbox(root, "../escaped_worker").register()` creates `root/../escaped_worker/inbox`. `send("../escaped_worker", …)` writes a message there. Worker-id is unsanitized path.

**Repro:** `S-R3b`.

**Measured:**

```
REPRODUCED  S-R3b
register_inbox=.../escaped_worker/inbox
under_mail=False
send_landed=[.../escaped_worker/inbox/<mid>.json]
```

---

### S-R3c — HIGH — K5 is a name comparison, not a credential (KNOWN residual)

K5 refuses `Scheduler(worker="B").done(job_claimed_by_A)`. Construct `Scheduler(same_queue, same_key, worker="A")` and `done()` succeeds. Worker-id is a constructor string at every seam that composes a scheduler, mailbox, or kernel. The claimant guard assumes the string is authentic.

**Repro:** `S-R3c`.

**Measured:**

```
REPRODUCED  S-R3c
state=CLEAN by=A
(spoof Scheduler(worker='A') completed A's job)
```

---

### S-N1 — HIGH — `qualify_backup_target` ignores role (NEW)

**Locus:** `cosmos_surfaces.py` `qualify_backup_target`. Three questions: reachability, capacity, kind ∈ {LAN, CLOUD}. **Role is never read.**

The module docstring says kind and role “are checked against each other at qualification time” and names “a PUBLISH kind in a BACKUP role” as the publishing-is-not-backup trap. The inverse — **CLOUD kind, PUBLISH role** — QUALIFIES with `reasons=[]`. That is the R2-nightly scar: a publish bucket answering a backup question.

**Repro:** `S-N1`.

**Measured:**

```
REPRODUCED  S-N1
CLOUD+PUBLISH qualified=True reasons=[]
```

`test_surfaces.py` never registers `role=PUBLISH` on a CLOUD/LAN kind, so the suite cannot see this.

---

### S-N2 — HIGH — off-machine is a sticker, not a measurement (NEW)

Question (3) is `claim["kind"] in {"LAN", "CLOUD"}`. The probe returns `(reachable, free_bytes, detail)` — nothing about leaving this machine. Register a directory on *this box* as `kind=LAN`, attach a probe that reports terabytes free, and it QUALIFIES.

That is the G: / SABRENT USB enclosure labelled NAS1. The code still answers “off-machine?” from the label the registrant typed.

**Repro:** `S-N2`.

**Measured:**

```
REPRODUCED  S-N2
kind=LAN path='.../this-machine-usb' (on this box)
qualified=True reasons=[]
```

`test_wave4.py` “a reachable off-machine LAN target QUALIFIES” is this claim path, not a measured off-machine fact.

---

### S-N3 — MEDIUM — `report()` freezes a green qualification (NEW)

`report()["qualified"]` is the last `SURFACE_QUALIFIED` event. `age_s` is computed now. After the measurement ages past `STALE_AFTER_S`, `report()` still shows `qualified=True` with `age_s=90000`. A live `qualify_backup_target` on the same facts returns `qualified=False`.

The class docstring: “Nothing holds a qualified status that a re-run of `qualify_backup_target` would not reproduce from the recorded facts.” `report()` does.

`test_surfaces.py` advances the clock and re-asks `qualify_backup_target`. It never reads `report()` after aging.

**Repro:** `S-N3`.

**Measured:**

```
REPRODUCED  S-N3
first_qualify=True
report_after_stale qualified=True age_s=90000.0
re_ask_qualify=False
```

---

## Out of cluster (not claimed)

These known residuals were **not** attacked here. Absence of a finding is not a close.

- **Cross-process arbiter serialization** — `cosmos_lock.Arbiter._append` has no OS lock; ledger append does. Lock cluster.
- **Spend over-cap under overlap** — `expect_head_seq` is bound to `head_seq()` *after* the cap decision. Spend cluster.
- **Segment anchor authentication** — anchors are unsigned JSON; `_load()` trusts `record_count`. Ledger/segments cluster.

---

## Measured run

```
PYTHONPATH=cosmos python3 tests/reattack_surface_repros.py

REATTACK surface: 12/12 findings REPRODUCED on main@stage-7

  REPRODUCED  S-R1   envelope_id ../ traversal ACCEPT
  REPRODUCED  S-R1b  absolute envelope_id replaces ingress root
  REPRODUCED  S-R1c  payload symlink foreign-file ACCEPT
  REPRODUCED  S-R2   argv: executes outside tools_root (K4 held for py:)
  REPRODUCED  S-R2b  command + MCP + HTTP accept argv: (3 jobs)
  REPRODUCED  S-R2c  FileNotFoundError; job left RUNNING
  REPRODUCED  S-R3   sender='core' ACCEPTED unauthenticated
  REPRODUCED  S-R3b  mail worker ../ escapes mail root
  REPRODUCED  S-R3c  Scheduler(worker='A') spoof beats K5
  REPRODUCED  S-N1   CLOUD+PUBLISH QUALIFIES as backup
  REPRODUCED  S-N2   local path registered LAN QUALIFIES
  REPRODUCED  S-N3   report() stays qualified=True at age 90000s
```

---

## What this is not

This is not a patch. The stage-7 tests remain green because they do not cover these cases. The next builder who “closes” any of these without a repro that fails first is writing prose.
