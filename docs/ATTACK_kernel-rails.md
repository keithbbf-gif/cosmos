# ATTACK · kernel-rails

**Critic:** Cursor background agent (adversarial, not the builder).
**Subject:** `f5/cosmos-core-v1` @ `e9e23ef` — cluster **kernel-rails**
(`cosmos_kernel`, `cosmos_registry`, `cosmos_rails`, `cosmos_node_rails`,
`cosmos_dom`, `cosmos_ingress` — composition + dispatch).
**Date:** 2026-08-23. **Ran in:** this Linux container.
**Contracts:** `docs/FINAL_ARCHITECTURE.md` (ratified), harvest recovered from
`origin/review/f5-core-grok:docs/REVIEW_F5_CORE_GROK.md` (B1–B7 + M1–M10; not
present under `docs/` on `f5/cosmos-core-v1`).
**Method:** `PYTHONPATH=cosmos` pytest of every `tests/test_*.py` that touches
the cluster; then 38 new probes in `tests/attack_kernel_rails.py`. Docstrings
are claims. Behavior is evidence. A finding without a repro that ran is an
opinion — every ranked item below has a command that was executed HERE.

**Scope kept:** `cosmos/` and existing `tests/test_*.py` were not modified.

---

## Verdict

The builder closed several harvest items **as modules and as sequential
selftests**. They did not close them **at the composition root, under overlap,
or against forged/escaped input**. Kernel now constructs `Registry` / `SpendGate`
/ `ReturnValidator` and the unsigned-lease / hash-fence / ingress *APIs* exist
— then Kernel composes an **unkeyed** `Arbiter`, `protected_write` never
presents input hashes, `IngressGate.accept_all` never submits a job, and
Dispatcher / DOM / ingress are still sibling files a test wires by assignment.

`v1.0-f5` / "all suites PASS native Windows" is an environment claim. HERE,
three cluster-touching suites fail for native-only reasons the builder did not
mark as failing the v1 claim.

---

## 1. Existing suites HERE vs NATIVE-DEMO-REQUIRED

Command:

```
PYTHONPATH=/workspace/cosmos python3 -m pytest -v \
  tests/test_kernel.py tests/test_concurrency.py tests/test_node_rails.py \
  tests/test_features.py tests/test_v1.py tests/test_wave3.py \
  tests/test_wave4.py tests/test_command.py tests/test_migrate_health.py \
  tests/test_tls.py tests/test_browser.py
```

| suite | touches | HERE | NATIVE-DEMO-REQUIRED? | notes |
|---|---|---|---|---|
| `test_kernel.py` | kernel | **PASS** (13 checks) | no | sequential install/boot/write/audit |
| `test_concurrency.py` | kernel compose | **PASS** (17 checks) | no | B1 ledger lock + B2 claim + B7 expiry + M2 restamp + compose |
| `test_node_rails.py` | node_rails, rails, registry | **PASS** (12 checks) | **yes** — live model dispatch is opt-in; suite uses `sys.modules` fakes | honest UNREACHABLE for missing incumbents |
| `test_wave4.py` | rails, dom, registry, kernel | **PASS** (16 checks) | no | M6 DOM-first + audited fallback (FakeDriver) |
| `test_v1.py` | kernel, registry | **PASS** (18 checks) | no | registry + HTTP; test still assigns probes in-process |
| `test_command.py` | kernel | **PASS** | no | |
| `test_migrate_health.py` | kernel | **PASS** | no | |
| `test_tls.py` | kernel + service | **PASS** (3 checks, HTTPS) | marked only if `cryptography` absent | HERE crypto is present; HTTPS served |
| `test_wave3.py` | **ingress** + kernel | **FAIL** (uncaught) | **not marked** | B3 ingress checks **ran**; then `cosmos_runner` execs `py` (Windows launcher). Isolated B3 HERE: `accepted=1 refused=[UNKNOWN_KIND, SHORT_PAYLOAD]` |
| `test_features.py` | **dom** + platform | **FAIL** (uncaught) | **not marked** | dies on `run(["py", "-3.14", ...])` **before** any DOM check. DOM protocol is covered by `test_wave4` + attacks |
| `test_browser.py` | DOM driver | **FAIL** | marked only when **no** binary | `discover_browser()` returned `/usr/local/bin/chrome` — a **675-byte shell stub**, not Chrome. Live-navigate timed out 60s (`SIGKILL`). The NATIVE-DEMO-REQUIRED skip is unreachable whenever a stub is on PATH |

Bare `pytest tests/` without `PYTHONPATH=cosmos` still cannot collect (imports
are top-level `cosmos_*`, not `cosmos.cosmos_*`). Same harvest note as Grok.

Adversarial file (measurement, not a gate):

```
PYTHONPATH=/workspace/cosmos python3 tests/attack_kernel_rails.py
```

**38 probes: 31 LANDS, 7 HOLDS.** Full transcript:
`/opt/cursor/artifacts/attack_kernel_rails_run.txt`.

---

## 2. Harvest verification (only gaps that touch this cluster)

Harvest source: Grok critic review B1–B7 + M1–M10 (~17 numbered; minors m1–m7
bring the list to ~19+). Builder claims in `docs/V1_SUITE_RESULTS.md` that
B1/B2/B3/B6/B7/M2/M4/M6 are closed. Measured HERE:

| id | harvest claim | builder's close | HERE vs cluster | status |
|---|---|---|---|---|
| **B1** | two writers tear the chain; `Kernel()` is a write | OS-lock + `read_only` | Overlapping `protected_write` from two Kernels: **chain verifies, 0 errors** (42 recs). **Still open:** `read_only=True` calls `mail.register()` and creates an inbox | **HALF** |
| **B2** | overlapping `claim_next` double-claims | `expect_head_seq` / `STALE_HEAD` | `test_concurrency` PASS HERE. Scheduler is composed, not the dispatch cluster | **CLOSED** (not re-broken) |
| **B3** | no ingress; mount write is already real | `cosmos_ingress` + `test_wave3` | Sequential happy path works (isolated HERE). **Not closed:** no identity, `../` escape, accept ≠ job, concurrent double-`INGRESS_ACCEPTED` + crash | **OPEN** (module is theater at the kernel) |
| **B4** | seven primitives not kernel interfaces; import-around | "composed registry/spend/validator" | `import cosmos_ledger; Ledger(...).append("I_AM_THE_KERNEL")` verifies on the authority chain | **OPEN** |
| **B5** | no context / `OPEN_CONTEXT` | `Kernel.open_session` | `test_concurrency` close-over-watcher refuses. Not a rails finding | **CLOSED** (kernel verb) |
| **B6** | unsigned GRANT loads as live lease | keyed `Arbiter` + `FORGED_EVENT` | `Arbiter(..., key=)` refuses a forge (`test_wave3` path). **`Kernel` constructs `Arbiter(path, clock=)` with no key.** Forged GRANT loads | **OPEN at composition** |
| **B7** | expired budget ALLOWED | `SpendGate` reads `expires_epoch` | Dispatcher + expired budget: adapter **did not run**, `NOT_PERMITTED`. **Still open:** reservation-id collision under overlap (m2) | **HALF** (expiry closed; exactly-once spend not) |
| **M2** | `install()` restamps `tree_id` | refuse `IDENTITY_MISMATCH` + write record | Restamp still refused. **Still open:** Kernel goes READY after `install_record.json` is deleted (Decision 5) | **HALF** |
| **M3** | `GET /rails` 200+empty when uncomposed | 503 `REGISTRY_NOT_COMPOSED`; Kernel composes registry | HERE: 200 + `matrix=[]` on a fresh composed kernel (honest empty). M3's silent-uncomposed path is gone | **CLOSED** |
| **M4** | fenced commit has no input hashes / no post-check | `Arbiter.fenced_commit(..., expected_inputs)` | API exists. `Kernel.protected_write` calls `fenced_commit(lease, commit)` — **`expected_inputs is None`** | **OPEN at composition** |
| **M6** | DOM is a sort key | `DomRail` + `Dispatcher` + typed failures | `test_wave4` PASS. **Still open:** no Job Object, empty DOM is OK, `ApiRail.probe` always True, missing adapter silent-skip, `job_id` path escape | **HALF** |
| **M10** | `audit.leases_live` hard-codes `"tree"` | unclaimed | Still `sum(1 for r in ("tree",) if ...)` | **OPEN** |
| M1, M5, M7, M8, M9 | lock TAKEOVER / runner / backup / HTTP / ledger segments | various | **out of cluster** — not scored here | n/a |

---

## 3. Ranked findings

Repro convention: every BLOCKER/MAJOR has a **named function** in
`tests/attack_kernel_rails.py`. The one-liner under each item was executed
HERE (either as that function, or as the equivalent `python3 -c`). Run the
whole attack file to reproduce the set.

```
PYTHONPATH=cosmos python3 tests/attack_kernel_rails.py
```

---

### BLOCKER

#### B-KR-1 — Kernel composes an **unkeyed** Arbiter. Forged GRANT is a live lease.

**Harvest B6, Decision 2, H5.** `cosmos_lock.Arbiter` can HMAC-sign events.
`Kernel.__init__` does `Arbiter(self.paths.ledger("leases.jsonl"), clock=clock)`
— no install key. Replay with `_key is None` skips signature checks. A
well-formed unsigned GRANT becomes `Lease(holder='ATTACKER', token=99)`.

`p_b6_kernel_arbiter_unsigned` **LANDS**:
`forged lease=Lease(resource='crown', holder='ATTACKER', token=99, expires_at=1e+18)`.

```bash
PYTHONPATH=cosmos python3 -c '
from pathlib import Path, tempfile; import json, tempfile
from cosmos_kernel import Kernel, install
td=Path(tempfile.mkdtemp()); root=td/"C"; install(root,"t"); k=Kernel(root)
p=k.paths.ledger("leases.jsonl")
p.open("a").write(json.dumps({"t":1,"event":"GRANT","resource":"crown",
  "holder":"ATTACKER","token":99,"expires_at":1e18})+"\n")
k2=Kernel(root, worker="b")
print(k2.arbiter.status("crown"))
'
```

The suite that "closed B6" constructs `Arbiter(..., key=KEY)` in the test
process. Composition in a test is not composition in Core.

#### B-KR-2 — `protected_write` is not a fenced gateway (no expected input hashes).

**Harvest M4, Decision 2.** Architecture: present fencing token **+ expected
input hashes**. Spy on `k.arbiter.fenced_commit`:
`expected_inputs captured=[None]`. `p_m4_protected_write_omits_hashes` **LANDS**.

The write is `tmp.write_text` + `os.replace` under a lease acquired and
released in the same call. Workers never hold a token across a job. Atomic
rename is used as authority — the thing Decision 2 demoted to "single-volume
optimization."

#### B-KR-3 — Workers import around the kernel and write the authority ledger.

**Harvest B4, Decision 11.** "The seven scar-derived primitives are kernel
interfaces with capability enforcement — workers cannot import around them."

`p_b4_import_around_kernel` **LANDS**: read `install_key.bin`,
`Ledger(authority.jsonl, key, "ATTACKER").append("I_AM_THE_KERNEL", {"lie": True})`,
`verify()` accepts it. Events: `['BOOT_VERIFIED', 'I_AM_THE_KERNEL']`.

There is no import hook, no capability token, no worker-supervisor. The key
file on disk **is** the kernel.

#### B-KR-4 — Kernel does not compose Dispatcher, IngressGate, or DomWorker.

**H6, Decision 6, critic "composition in a test is not composition in Core."**
Kernel now attaches `registry` / `spend` / `validator`. It does **not** attach
`dispatcher`, `ingress`, `dom`, or `rails`. `p_kernel_does_not_compose_rails_ingress_dom`
**LANDS**: `absent attributes: ['dispatcher', 'ingress', 'dom', 'rails']`.

`test_v1` / `test_wave4` still construct `Registry` / `Dispatcher` / `DomRail`
beside a kernel. The HTTP `/rails` matrix is a probe table, not a dispatch
path. There is no resident accept-loop for ingress.

#### B-KR-5 — `protected_write(relpath="../escaped.txt")` writes outside `state/`.

**H3 two-universes / mount.** `paths.role("state", relpath)` is
`joinpath` with no jail. `p_protected_write_escapes_state_role` **LANDS**:
wrote `/.../Cosmos/state/../escaped.txt` (resolves to `/.../Cosmos/escaped.txt`).

A sandbox that can call the kernel verb (or that shares the volume) leaves the
role tree.

#### B-KR-6 — Ingress `envelope_id="../stolen"` reads a payload **outside** the ingress dir.

**H3 lying mount, Decision 2.** `_verify_one` does
`self.dir / (env["envelope_id"] + ".payload")` with no sanitise.
`p_ingress_envelope_id_path_escape` **LANDS**: planted `../stolen.payload`
outside the gate directory; `accept_all` returned `accepted=1` with those bytes.

The envelope filename is not the path; the attacker-controlled `envelope_id`
is.

#### B-KR-7 — Ingress accepts any `sender` string. Identity is a field, not a check.

**Decision 2: verify bytes/hash/schema/identity.** `p_ingress_no_identity`
**LANDS**: `write_envelope(..., sender="keith-ceo", kind="job", ...)` →
`INGRESS_ACCEPTED` with `sender='keith-ceo'`. No HMAC, no install-key bind, no
worker registry lookup.

#### B-KR-8 — `INGRESS_ACCEPTED` does not make a job (or anything else) real.

B3's docstring: "only ACCEPTED envelopes become real (e.g., a job
submission)." `accept_all` appends a ledger line and renames
`.envelope.json` → `.json.accepted`. It does not call `sched.submit`.
`p_ingress_accepted_is_not_real` **LANDS**: `accepted=1 sched_state={}`.

So: the mount write is still not operationally real, **and** a forged sender
can get a green `INGRESS_ACCEPTED` on the authority ledger. The gate is a
rename with a receipt.

#### B-KR-9 — Concurrent `accept_all` is not exactly-once and crashes.

**H5 / exactly-once under real overlap.** Two `IngressGate` threads, one
envelope, `threading.Barrier`. `p_ingress_concurrent_double_accept` **LANDS**:

- `INGRESS_ACCEPTED=2` on the authority ledger
- `FileNotFoundError` on the loser rename
- `accepted_n=1` in memory (one thread crashed after ledgering)

Sequential re-entry HOLDS (`r2` empty, one event). The suite never overlaps.

#### B-KR-10 — Spend reservation ids collide; two overlapping `$0.02` calls on a `$0.03` cap both RAN.

**Harvest m2, H3 expiring/over-cap credit, Dispatcher spend path.**
`rid = "r%d" % int(self._clock() * 1000)`. Frozen clock `1000.500`, cap
`$0.03`, two threads `guarded_call(..., 0.02, ...)`.
`p_spend_rid_collision_under_overlap` **LANDS**: `outcomes=['ran', 'ran']`.

B7 expiry through Dispatcher HOLDS (adapter did not run). The breaker still
does not serialize the reserve-check, so overlap bypasses the cap.

---

### MAJOR

#### M-KR-1 — Decision 5: Kernel goes READY with `install_record.json` deleted.

Architecture: "service cannot go READY without sentinel-verified root
**+ installation record**." Kernel only requires `install_key.bin`.
`p_decision5_ready_without_install_record` **LANDS**: `ready=True` after unlink.
M2 wrote the record; boot never reads it. `Kernel(root)` still takes a path,
not `from_install_record()`.

#### M-KR-2 — `audit()["leases_live"]` only counts resource `"tree"`.

**Harvest M10.** `p_m10_audit_hardcodes_tree` **LANDS**: acquire `"crown"`,
`leases_live=0`. An operator audit can read "no leases" while a live fence
exists.

#### M-KR-3 — `read_only=True` still writes (mailbox register).

**Harvest B1 leftover.** `p_b1_readonly_still_writes_mail` **LANDS**:
`Kernel(..., worker="reader", read_only=True)` creates
`state/mail/reader/inbox`. A read is still a write on the mail surface.
Authority ledger append is suppressed; the "reader is not a writer" claim is
not total.

#### M-KR-4 — Registry routing never expires a probe.

**H6 dated probes; "registration is not capability."** Age is displayed.
`route()` uses `v["ok"]` truthiness with no freshness window.
`p_registry_stale_probe_never_expires` **LANDS**: `age_s=31536000.0`
(one year), `route=['dom1']`, `verified=True`. A dead rail whose last
measurement was ok stays a dispatch candidate until someone probes again.

#### M-KR-5 — Re-register silently restamps the claim and wipes the measurement.

`p_registry_reregister_wipes_measurement` **LANDS**: `ok before=True after=None
type=CLI`. Same `link_id`, new `rail_type`, no `DUPLICATE` / `DRIFT` refusal
(tools contracts refuse a second declare; links do not). Projection fold on
`LINK_REGISTERED` resets `last_probe` and `ok`.

#### M-KR-6 — `ApiRail.probe` is always True. Registration is capability.

Probe returns `(True, "api adapter present (liveness is per-call)")` without
calling `fn`. `p_apirail_probe_is_always_live` **LANDS**: a function that
raises `RuntimeError("endpoint dead")` is **route-live** after `probe_all`.
`NodeRail.probe` at least tries an import. `ApiRail` does not.

#### M-KR-7 — Dispatcher silently skips a live link with no adapter.

H2: no silent fallback. `p_missing_adapter_silent_skip` **LANDS**: DOM link
probed live, absent from `adapters={}`; dispatch returns the API result;
**no** `RAIL_FALLBACK` / `RAIL_DISPATCH` names the ghost. Events:
`RAIL_DISPATCH` only for `api`.

#### M-KR-8 — A raising metered adapter is labeled `NOT_PERMITTED` after the call RAN.

```python
except Exception as e:
    ...
    raise RailError("NOT_PERMITTED", str(e))
```

`p_dispatch_raise_mislabeled_not_permitted` **LANDS**: `kind=NOT_PERMITTED
ran=[1]`. Spend denial and model/BROKE collapse. The spend gate's
"deny precedes the call" invariant is true only for `SpendError`; Dispatcher
then lies about every other exception.

#### M-KR-9 — `NodeRail` fabricates `ok=True` (`r.get("ok", True)`; `None`/`""` → success).

`p_noderail_missing_ok_defaults_true` **LANDS**: `{"text": "I forgot the ok
field"}` → `ok=True`.
`p_noderail_none_and_empty_are_ok` **LANDS**: `ask()→None` becomes
`text='None', ok=True`; `ask()→""` is `ok=True`. Missing vs empty vs failure
are one costume.

#### M-KR-10 — `DomWorker` treats empty page text as `DOM_ATTEMPT_OK`.

`ChromeDriver.navigate` raises `ConnectionError` on empty DOM (UNREACHABLE).
The protocol module does not. `p_dom_empty_text_is_ok` **LANDS**:
`kind=OK`, `text=''`, event `DOM_ATTEMPT_OK`. Missing page and empty page are
the same success.

#### M-KR-11 — `job_id` is a path segment. `../escaped_job` writes outside `work_root`.

`p_dom_job_id_path_escape` **LANDS**: evidence and profile created at
`{tmp}/escaped_job/...`, not under `work/`. Combined with B-KR-5 / B-KR-6,
path jail is not a kernel property.

#### M-KR-12 — Decision 6 Job Objects / ACL'd OS identity are not implemented.

`p_dom_no_job_object` **LANDS**: `cosmos_dom.py` has no Job Object / ACL /
`AssignProcessToJobObject` tokens. `run_attempt` is `makedirs` + injected
driver + ledger lines. Containment is a comment. HERE cannot prove a Windows
Job Object; the source absence is the measurement.

#### M-KR-13 — Accepted ingress payload file stays mount-visible.

`p_ingress_payload_left_after_accept` **LANDS**: after `INGRESS_ACCEPTED`,
`*.payload` is still on disk with the original bytes. The envelope is renamed;
the body is not. A second universe can mutate the leftover after the receipt.

---

### MINOR

Each ran HERE via the attack file.

| id | what | repro fn | measured |
|---|---|---|---|
| m-KR-1 | `route()` collapses unknown pair and unprobed-empty to `[]` | `p_registry_empty_vs_missing_route` | both `[]` |
| m-KR-2 | `DomRail.dispatch({})` is untyped `KeyError('job_id')` | `p_domrail_missing_keys_untyped` | no `RailError`/`DomError` |
| m-KR-3 | `NodeRail._mod` cache survives `del sys.modules[name]` | `p_noderail_cached_mod_after_delete` | probe still `True` |
| m-KR-4 | `payload_len: "4"` (string) → `SHORT_PAYLOAD` | `p_ingress_payload_len_type_confusion` | honest 4 bytes refused |
| m-KR-5 | longer-than-declared payload is named `SHORT_PAYLOAD` | `p_ingress_long_payload_named_short` | kind lies |
| m-KR-6 | 0-byte declared payload is `ACCEPTED` (empty == present) | `p_ingress_empty_payload_accepted` | `payload=b""` |
| m-KR-7 | `CHAT` is a `RAIL_TYPES` member; no `ChatRail` | `p_no_chat_rail_adapter` | only Cli/Api/Dom |
| m-KR-8 | `discover_browser()` treats a PATH stub as a live browser | `test_browser` HERE | 675-byte `/usr/local/bin/chrome`; 60s timeout instead of NATIVE-DEMO-REQUIRED |

---

## 4. What HOLDS (so the builder cannot say we ignored closes)

These probes **HOLDS** — the contract held under attack, HERE:

| probe | evidence |
|---|---|
| B1 overlapping `Kernel.protected_write` | `errors=0 chain_ok=True recs=42` |
| B7 expired budget via Dispatcher | `ran=[] kind=NOT_PERMITTED` |
| M2 restamp | `IDENTITY_MISMATCH` |
| M3 `/rails` uncomposed lie | 200 + empty matrix on a **composed** registry (honest) |
| sequential `accept_all` twice | second pass empty; one `INGRESS_ACCEPTED` |
| unicode envelope_id / unicode `protected_write` | accepted / round-tripped `café ✓` |

`test_concurrency` B1/B2 and `test_wave4` M6 happy-path also PASS HERE. Those
closes are real **for the cases they test**. They are not the cases above.

---

## 5. Architecture contract vs this cluster (one screen)

| ratified decision | cluster reality HERE |
|---|---|
| 1 · one resident service, never a second unsynchronized writer | Authority ledger is lock-serialized (B1 HOLDS). Lease file is a **second, unkeyed** writer (B-KR-1). Ingress double-appends under overlap (B-KR-9). |
| 2 · leases + fencing tokens + **expected input hashes**; mounts are ingress until verify+identity | Hashes omitted (B-KR-2). Ingress has no identity (B-KR-7), escapes the dir (B-KR-6), does not publish (B-KR-8). |
| 5 · READY only after sentinel **and** install record; no import-time side effects | Sentinel yes. Install record written then **ignored**. Import-time is clean. |
| 6 · DOM is a scheduler rail: OS identity, ACL'd profiles, Job Objects, typed failures | Adapter + typed FakeDriver paths exist. No Job Object, no ACL, empty DOM is OK, `job_id` escapes, Kernel does not own a DOM worker. |
| 11 · primitives are kernel interfaces; workers cannot import around them | Anyone with the key file appends authority events (B-KR-3). Dispatcher/ingress/DOM are importable siblings. |

Honest risks the architecture already carried (single availability point, DOM
hardening UNKNOWN) are still accurate. They do not excuse unsigned leases at
the composition root or a path jail that `../` walks through.

---

## 6. What would close this cluster (not a design; a refuse-list)

1. `Kernel` passes the install key into `Arbiter`. Replay of an unsigned GRANT
   on a kernel-booted root raises `FORGED_EVENT`. Repro B-KR-1 goes HOLD.
2. `protected_write` (and any other publish path) presents `expected_inputs`
   and refuses a role-escaping `relpath`.
3. `IngressGate` binds `envelope_id` to a single path segment, verifies
   sender against the worker/install identity, **one** `accept_all` under the
   ledger lock, and a Kernel accept-loop that turns `kind=job` into
   `sched.submit` (or a typed refuse). Concurrent overlap = one
   `INGRESS_ACCEPTED`, no `FileNotFoundError`.
4. Spend `rid` is unique under overlap; reserve-check is serialized. Two
   `$0.02` calls on `$0.03` → one `ran`, one `DENIED`.
5. `ApiRail.probe` measures something or returns unknown. `route()` drops
   stale probes. Dispatcher ledgers a missing adapter. NodeRail does not
   default `ok=True`. DomWorker does not OK an empty DOM. `job_id` cannot
   leave `work_root`.
6. Suites that need `py` / a real Chrome **fail the v1 claim** when the
   environment cannot prove the property — skip-as-PASS and stub-as-browser
   are the same costume.

Until B-KR-1, B-KR-6, B-KR-9, and B-KR-10 HOLD, calling this cluster
"composition + dispatch, harvest closed" is the defect class the harvest named.
