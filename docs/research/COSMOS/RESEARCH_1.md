# COSMOS Core OS — RESEARCH_1

**Researcher:** G46 (Grok 4.6)
**Date:** 2026-08-25
**Scope:** Top improvements and gaps in the COSMOS *core OS* (kernel, ledger, lock/arbiter, scheduler, service, session, spend, registry, DOM/runner, backup). Not a surface-by-surface UI review.
**Method:** Ratified architecture vs the code that actually composes, plus host-side reads of the live root. Docstrings treated as claims. A prior per-module review exists (`docs/G46_TOOL_REVIEW_2026-08-25.md`); this pass is the *system* picture that review could not form while HEART/lock was empty.
**Not done:** no test run this pass, no `serve` process inspected, no code edits.

**Ground truth this pass (host-side):**

| Fact | Value |
|---|---|
| git HEAD | `56fa423` (`cosmos: deploy voice safety guards + grounded Opus brain...`) |
| Live authority ledger | `live/ledger/authority.jsonl` — **268 records** (BUCm.toml `[live].ledger` still says 192) |
| Event mix | 143 `TOOL_DECLARED`, 28 `LINK_REGISTERED`, 28 `BUDGET_SET`, 16 `SPEND_RESERVED`, 16 `SPEND_SETTLED`, 9 `BOOT_VERIFIED`, 8 `TOOL_DISPOSITION`, 8 `PROBE_RESULT`, 6 `MAKER_ADDED`, 1 each of `SESSION_OPENED`/`CLOSED`/`SEED_WRITTEN`, `RAIL_DISPATCH`/`RAIL_RESULT`, `NODE_REVIEW` |
| Queue ledger on live | **absent** (`live/queue/sched_ledger.jsonl` not present; orphan staged at `live/_delme/queue_orphan_2026-08-25/`) |
| Lease ledger on live | **absent** (`live/ledger/leases.jsonl` not present) |
| GitLab CI | **no** `.gitlab-ci.yml` |
| Runtime pointer | `BUCm.toml` stream `Cm`, tree_id `KMesh-COSMOS-live` |

---

## 1. What the running core actually is

COSMOS Core is a **Python 3.14 modular monolith** with a composition root (`cosmos/cosmos_kernel.py`) and a stdlib HTTP API (`cosmos/cosmos_service.py`). Keith runs it himself:

```
py -3.14 cosmos\cosmos.py serve --root V:\A\Ai\COSMOS\live --port 8770
```

That is a **foreground `ThreadingHTTPServer`**, not a Windows service. Persistence, if any, is `schtasks /sc onlogon` via `cosmos/cosmos_up.py`.

**What is composed at `Kernel.__init__` (writing boot):** resolver, install key, authority `Ledger`, `BOOT_VERIFIED`, `Arbiter`, `Mailbox`, `Scheduler`, `Registry`, `SpendGate`, `ReturnValidator`, `SessionManager`, `MakerMap`, `ConvoStore`, `ITC`. Then `ready = True`.

**What exists as a sibling module but is *not* composed on the kernel:** `Dispatcher`, `Runner`, `IngressGate`, `SegmentedLedger` + `CAS`, `HealthBoard`, `Backup`, `DomWorker` / `cosmos_browser.Driver`, `register_node_rails`. Tests and the voice handler construct them ad hoc. That is the critic line already on the kernel: *"composition in a test is not composition in Core"* (`cosmos_kernel.py` lines 75–77) — and it still applies to the execution path.

**Stale self-description (claim vs tree):** the kernel module docstring still says *"no HTTPS API yet, no DOM worker, no spend gate wiring, no Windows-service wrapper"*. Spend *is* wired on the kernel. HTTPS *does* exist on `Service`. DOM *protocol* exists. The Windows-service wrapper still does not. The docstring is a mixed lie: half overtaken, half still true. `README.md` Status is worse — it still says **"Pre-implementation."**

---

## 2. Ratified decisions vs the live Core

From `docs/FINAL_ARCHITECTURE.md` (ratified `docs/RATIFIED.md`, 2026-08-23). Verdict is **IN / PARTIAL / ABSENT**, with the file that proves it.

| # | Decision | Verdict | Evidence |
|---|---|---|---|
| 1 | One resident Windows service; fail-closed; **Windows service recovery**; ledger replay; never a second unsynchronized writer | **PARTIAL** | Replay and fail-closed: yes (`cosmos_ledger.py` `verify()` on open). Resident **Windows service + recovery: no** (no `win32service` / NSSM anywhere; `cosmos.py serve` is `serve_forever()`). Second writer: **structurally present** — three ledgers (authority, scheduler, leases), see Gap 1. |
| 2 | Leases + monotonic fencing tokens + fenced commit gateway | **IN (protocol) / UNUSED (live)** | `cosmos_lock.py` four-phase `fenced_commit` with `expected_inputs` hashes. Live root has **no** `leases.jsonl` — production has not exercised a protected write. `Kernel.protected_write` never passes `expected_inputs`. |
| 3 | Framed, hash-chained, **signed JSONL segments** + CAS; corrupt segment REFUSE + incident | **PARTIAL** | Single-file `Ledger` is the authority (`Kernel` opens `ledger/authority.jsonl`). `cosmos_segments.py` `SegmentedLedger` + `CAS` exist and are tested (`tests/test_segments.py`) — **never imported by the kernel**. |
| 4 | Queue = immutable manifests + ledger lifecycle; SQLite projection-only | **IN (shape) / FRAGILE (keying)** | `cosmos_sched.py` writes manifests then `JOB_SUBMITTED`. **No SQLite** (optional, not a defect). Scheduler is a **second keyed Ledger** (`queue/sched_ledger.jsonl`), which is what fail-closed the 2026-08-25 reinstall. |
| 5 | Resolver instantiated at boot; READY only after sentinel + install record | **IN** | `CosmosPaths(root)` first in `Kernel.__init__`. Empty-dir → `IDENTITY_MISMATCH`. Roles table in `cosmos_paths.py`. |
| 6 | DOM = first-class scheduler rail; Job Objects; typed failures; DOM-first policy data; explicit audited fallback | **PARTIAL** | Protocol + typed kinds: `cosmos_dom.py`. Read-only `--dump-dom` driver: `cosmos_browser.py` (honest: cannot click / MFA / OAuth). `Dispatcher` DOM-first: `cosmos_rails.py`. **Not composed on Kernel.** Production voice path **hardcodes** `bts_sgh.ask` (`cosmos_service.py` ~706–747). Node rails all `policy_rank=0` API (`cosmos_node_rails.py`). Job Objects: **absent** (`cosmos_platform.py` uses `taskkill /T`). `ChatRail` / `OtherRail`: **absent**. |
| 7 | One versioned API; KDash is a projection client | **IN (shape)** | `/api/v1/*` on `cosmos_service.py`. Static PWA allowlist. Bearer (or `--no-auth` trial). Not a version-negotiated schema; it is one URL prefix. |
| 8 | Backup policy in Core; execution as **scheduled jobs**; `rehearse-restore` first-class; Task Scheduler **registered and read back** | **PARTIAL** | Hash-verified copy + rehearsal: `cosmos_backup.py`, CLI verbs in `cosmos.py`. **Not a scheduler job type.** Task Scheduler is used to *keep serve alive* (`cosmos_up.install_persistent`), not to run backups, and is **not read back**. |
| 9 | Compatibility lane: legacy mutable-file tools SERIALIZED until behavior-cards earn parallelism; Legacy Job Adapter | **ABSENT** | No adapter, no serialized lane. `cosmos_port_plan.py` is a disposition table, not a runtime lane. |
| 10 | Context manifests at session close; no valid manifest ⇒ `OPEN_CONTEXT` | **IN (with holes)** | `cosmos_session.close_session` writes HMAC'd `state/SEED.json` + sidecar. Live seed exists and verifies by length/HMAC (BUCm). **Seed body has no `stream` field** (see Gap 7). Reconstructed close skips `Session.close()`. |
| 11 | Seven scar primitives are **kernel interfaces with capability enforcement** — workers cannot import around them | **ABSENT as enforcement** | Modules exist (VerifiedIO in `cosmos_validate.py`, ReturnValidator, PlatformAdapter, Context, typed errors). **ReturnWatcher class: none.** No capability tokens, no import firewall. Any holder of `install_key.bin` who can `import cosmos_ledger` is a writer. |

Honest risks from the ratification, still open:

- Core is a single availability point — **unmitigated** (no service recovery).
- Operator override must be explicit and audited — **only** `close_session(force=True)` + `--no-auth` / `--insecure-http` trial flags.
- FS-notification overflow → loud degraded + bounded scans — `wait_for_submission` poll fallback says `DEGRADED`; overflow handling **not built**.
- ~135 tool contracts UNKNOWN — **measured:** 143 `TOOL_DECLARED` on the live ledger, 8 `TOOL_DISPOSITION` (the spike/v1 replacements).
- DOM secret-store / browser hardening — still UNKNOWN; dump-dom is not a secret store.

---

## 3. Top gaps (ranked)

### G1 — Three ledgers, one key, no rotation protocol (HIGH)

Architecture: *one* service-signed authority ledger; everything else a projection.

Code: three independently keyed JSONL files:

1. `ledger/authority.jsonl` — `Kernel` (`cosmos_kernel.py` ~65)
2. `queue/sched_ledger.jsonl` — `Scheduler` (`cosmos_sched.py` ~56)
3. `ledger/leases.jsonl` — `Arbiter` (`cosmos_kernel.py` ~82)

All three HMAC with the same `config/install_key.bin`. Re-install regenerates the key and a fresh authority chain. The scheduler file is **not** rotated. Measured 2026-08-25 (BUCm.toml `[live].root_cause_fixed`): *every full-kernel boot fail-closed at the Scheduler (`[FORGED] line 1`)* until the orphan was staged to `live/_delme/queue_orphan_2026-08-25/`.

This is not a one-off ops miss. It is the architecture decision ("never a second unsynchronized writer") leaking at the composition boundary. A peer on a cold machine who runs `install` twice, or who restores authority without queue, hits the same FORGED wall.

**Improvement:** one of: (a) scheduler and leases become *event types on the authority ledger* (projections only), or (b) a keyed-bundle install record that lists every ledger path + key generation, with `Kernel` refusing READY if any sibling chain is present under the wrong key (typed `FORGED` *naming the file*), plus an explicit `cosmos migrate-key` that re-signs or quarantines. Do not "repair in place."

### G2 — The execution path is not the kernel (HIGH)

The ratified Core is scheduler + arbiter + spend + return-watcher + registry/prober + fenced commit + API, **one process**.

What `serve` actually runs: HTTP handlers that reach into `kernel.sched` / `kernel.ledger` / `kernel.spend`, plus a **voice path that late-imports `V:\Ai\BTS_MESH` and calls `bts_sgh.ask`** (`cosmos_service.py` 706–747). `Dispatcher.dispatch` is constructed in tests (`tests/test_node_rails.py`, `tests/test_wave4.py`), not in `Kernel`. `Runner.drain` is not started by `serve`. There is no worker-supervisor loop. Jobs can be submitted (`POST /api/v1/jobs`, CLI `submit`) with **nobody claiming them** unless an operator runs a runner by hand.

Live evidence: 268 authority events, **one** `RAIL_DISPATCH` + one `RAIL_RESULT`. Dispatch was proven once. It is not the steady-state path.

**Improvement:** Kernel composes `Dispatcher`, `Runner`, `IngressGate`, and a drain/watch loop behind `ready`. `Service` may only call kernel verbs. The BTS wrap stays behind `register_node_rails`, never inlined in the HTTP handler.

### G3 — DOM-first is a policy that production does not take (HIGH)

Canon (`docs/COSMOS_PIPELINE.md`, `CLAUDE.md`): DOM is the preferred path *and* the last resort because it depends on nothing that can run out.

Code:

- `cosmos_node_rails.py` registers four **API** links, all `policy_rank=0`. Docstring mentions Cursor; `specs` does not.
- `ApiRail.probe` always returns True (*"liveness is per-call"*) — registration-as-capability in a trench coat (`cosmos_rails.py` 81–82).
- `Dispatcher.dispatch` **silently `continue`s** when `adapters.get(lid)` is None — no ledger event, then `NO_LIVE_LINK` (`cosmos_rails.py` 109–111). The G46 tool review already marked this HIGH.
- Production voice: hardcoded Grok API + Opus CLI + hardcoded roots `V:\Ai\Legal`, `V:\A\Ai\COSMOS`, `V:\Ai\ROLD`, `V:\Ai\BTS_MESH`, `V:\Ai` (`cosmos_service.py` 121–127, 720–721; `cosmos_brain.py` 88–102). Drive literals. Resolver canon violated on the hottest path.

`cosmos_browser.py` is honest about being dump-dom, not CDP. That honesty is correct. Shipping API-only voice as if DOM-first were live is not.

**Improvement:** register a real DOM link with `policy_rank > 0` on Kernel boot (even if the driver is dump-dom and many jobs then type `AUTH_REQUIRED`). Ledger every skipped-missing-adapter. Move stream roots into the install record / resolver roles, not module constants.

### G4 — Worker containment and the runner `-c` hole (HIGH)

Architecture: Windows Job Objects contain native *and* browser subprocess trees; timeout/kill includes descendants; workers publish only through the fenced gateway.

Code:

- `cosmos_platform.run_tree_killed` uses `taskkill /PID /T /F` on timeout. `run()` on `TimeoutExpired` records *"descendants not guaranteed"*.
- No `CreateJobObject` / `AssignProcessToJobObject`.
- `Runner.run_one` (`cosmos_runner.py` 173–174): a command that is neither `py:` nor `argv:` becomes `["py", "-3.14", "-c", cmd]`. Confined tools-root does not apply. Anyone who can `submit` can run arbitrary Python as the service user.
- `_confine_argv` treats whitelisted interpreter + `-c` anywhere in argv as "nothing to confine" (`cosmos_runner.py` 124–125).
- Default `tools_root` is `work.parent / "cosmos"` (`_tools_root`), while comments say `"tools"`. `CosmosPaths` role `"tools"` *is* `"cosmos"` — the runner does not use the resolver; it concatenates.

**Improvement:** refuse bare/`-c` unless the job lane is an explicit "eval" type that is operator-gated and ledgered. Bind `tools_root` through `kernel.paths.role("tools")`. Put the Popen tree in a Job Object; record containment success/failure on the attempt log (the platform adapter already has a `kill_result` field — fill it with a real fact).

### G5 — Segmented ledger + CAS built, then left beside the authority (MED–HIGH)

`cosmos_segments.py` is the M9 close: rotation, anchor chain, `LEDGER_INCIDENT` on a *named* corrupt segment, CAS with read-back hash. Kernel still full-walks one JSONL on **every** `append` (`cosmos_ledger.py` 157–158, `append_guarded` 199). Live file is 125,573 bytes / 268 records today; 143 of those are `TOOL_DECLARED`. This cost is already the reason segments exist.

Also: `prev_sha` of the next record is SHA256 of the **on-disk line**, while `append` sets `_prev_sha` from `json.dumps(rec)` (G46 tool review HIGH). Stable today; any dump change or `\r` tears the chain. Segments do not fix that coupling.

**Improvement:** Kernel opens a `SegmentedLedger` on `paths.ledger()`, CAS under a role (e.g. `publish/` or a new `cas/` role — add it to `ROLES`, do not assemble a path). Keep `Ledger` as the segment primitive.

### G6 — Return-watcher is named in the architecture and does not exist (MED)

Decision 11 / OA H4: Dispatch creates an immutable **return watcher** *before* a rail call; validators run before a return can touch a projection.

Present: `ReturnValidator` (`cosmos_validate.py`) — empty claims = `UNVALIDATED` refuse. Wired as `Kernel.accept_return`.

Absent: no `ReturnWatcher` type, no pre-dispatch subscriber, no deadline, no `WORKER_DIED` on process death. Session "watchers" (`cosmos_context.py` / seed `watchers`) are a different object (open-context at close), not rail-return watches.

`Kernel.accept_return` (`cosmos_kernel.py` 151–154) calls `validator.accept` then `sched.done`. Because `accept` **raises** on failure, the scheduler is unchanged on refuse — that part of the G46 UNKNOWN is resolved by reading `ReturnValidator.accept`. The remaining hole is that **nothing registers a watcher at dispatch**, so a hung rail is not a timeout event; it is silence.

**Improvement:** `dispatch` appends `WATCHER_OPENED` with deadline + validator names *before* the call; a supervisor expires it to `BROKE`/`UNREACHABLE`. Session-close watchers stay a separate vocabulary (or are renamed so the two cannot be conflated).

### G7 — Carry-over seed does not carry the stream (MED)

Architecture decision 10: inherited facts, active leases, open watchers, **handoff recipient**.

Live `state/SEED.json`:

```
schema, kind, facts, handoff="Cm", incidents, sid="cm-populate", tree_id, watchers, closed_epoch
```

No `stream`. BUCm `[live].verified` already noted *"SEED 'stream' field came back null (handoff_to=Cm)"*. That is not a read bug. `close_session` never writes `stream` (`cosmos_session.py` 254–264). `start_session(stream)` takes the stream from the **caller**, not from the seed. A BootUP that does not pass the same stream the previous session lived on silently opens the wrong lane.

Related defects already in the G46 session review, still in tree:

- Reconstructed `SESSION_CLOSED` does not call `Session.close()` (HIGH in that review).
- `start_session` does not consult `project_live_session` after `self.session is None`, so a second start can inject while the ledger still says open.
- Extra `config/*.json` are parse-only (verify_conf scar the comments warn about).

**Improvement:** seed.schema bump that *requires* `stream`, `active_leases`, `open_watchers`. `start_session` refuses `IDENTITY`/`BAD_SEED` if stream is missing. Reconstructed close must run the same `Session.close` semantics (or refuse: "cannot reconstruct a live Session object — force").

### G8 — Health and audit cannot tell the truth about leases (MED)

`HealthBoard.lease_board` (`cosmos_health.py` 55–58) **always returns `True`**. A free tree and a held tree are both GREEN. The planted-RED row exists; this row cannot go RED. That is the C-46/C-58 class the module's own docstring forbids.

`Kernel.audit` counts `leases_live` only for resource `"tree"` (`cosmos_kernel.py` 213–214). Live root has no lease ledger at all; audit would report `0` and look calm.

`queue_alive` treats empty as GREEN (stated) and uses `sched._state()` (private). `ledger_chain` is "verify() yielded N records" — if verify raised, the row handler catches it; if verify were a silent generator, it would stay GREEN. Today verify is real.

**Improvement:** lease row RED on torn/forged lease ledger, on a held-past-expiry projection, or on "lease file missing after a writing boot that should have created it." Audit enumerates `arbiter` resources from the projection, not a hardcoded tuple.

### G9 — Spend has two books (MED)

`SpendGate` (`cosmos_spend.py`): reserve → deny → call → settle on the **authority ledger**. This is the ratified breaker.

`SpendGuard` (`cosmos_spendguard.py`): session/day USD + rate limit in a **JSON counter file** (`config/spendguard_state.json`), fail-closed, used by `/api/v1/voice`. Day totals *can* fold the ledger; session/rate cannot.

G46 spend review still applies: `_decide` can pop expired reservations in memory without `SPEND_RELEASED`; `DOUBLE_SETTLE` / `RESERVATION_EXPIRED` documented and never raised; `set_budget` failures swallowed in `register_node_rails` (`except: pass`).

Voice can be paused by the guard while the gate still has headroom, or the reverse after `control/resume` clears local counters (`cosmos_service.py` control/resume). Two projections of "how much did we spend" is the forgotten-fact class.

**Improvement:** SpendGuard becomes a *projection + policy* over SpendGate events (plus a rate ledger event), not a second wallet. `register_node_rails` must not swallow `set_budget` failure — refuse READY or mark the rail UNBUDGETED and unmetered-dispatch-forbidden.

### G10 — "Installable by a peer on a cold machine" is not true of the hands (MED)

Resolver, install, serve-on-loopback: yes.

Hands: `_BTS = r"V:\Ai\BTS_MESH"` (`cosmos_node_rails.py` 22). Voice and brain hardcode `V:\Ai\BU.MD`, `V:\Ai\Legal`, `V:\Research4` (`cosmos_service.py`, `cosmos_brain.py`). `BU_MD_PATH` is a module global "so a test can repoint it" — that is a test seam, not a resolver.

A peer who clones this repo and `cosmos.py install --root D:\Ai\Cosmos` gets a kernel that boots and an API that cannot reach a model or a handoff file without Keith's drive map.

`cosmos_up.plan_serve_cmd` docstring still says *"`cosmos.py serve` has no `--cert`/`--key` flag today (measured 2026-08-24)"* and **drops cert/key on the floor** (`cosmos_up.py` 19–26, 190–196). `cosmos.py` **has** `--cert`/`--key` now (lines 48–51). The road-reach layer will keep serving a self-signed cert next to a Tailscale cert it already fetched.

Stray `serve.bat` at repo root and `tmp/commit-boot.bat` (BUCm `[housekeeping]`) — no-bats canon, still in the tree.

**Improvement:** incumbent mesh path is an install-record field (or a role). Stream roots live in config under the COSMOS root. `plan_serve_cmd` passes `--cert`/`--key` when present. Stage the bats to `_delme\`.

### G11 — Capability enforcement, compatibility lane, CI, override (MED / carried)

- **Decision 11:** no import firewall, no worker capability tokens. Internal interfaces are Python classes, not RPC. "Split-ready" is a comment.
- **Decision 9:** no serialized compatibility lane; 135+ UNDECIDED tools (`cosmos_migrate.py`, live 143 `TOOL_DECLARED` vs 8 `TOOL_DISPOSITION`).
- **Stage 6 ratification item 3:** GitLab CI after `glab auth login` — **no CI file**.
- **Operator override:** `--no-auth`, `--insecure-http`, ungated `/api/v1/kill` when `kill_token.txt` is absent. Kill-without-bearer is deliberate (reduce-only); it is still an unaudited mutation if the token file was never minted.
- **Placation scar** (`docs/SCAR_PLACATION.md`, earned this calendar day): runtime-binding of *claims* is governance, not a kernel gate. Core already ledgers `RAIL_DISPATCH`/`RAIL_RESULT` and voice `VOICE_BRAIN`. It does not refuse a handler that reports `ok` without quoting those events. That is the next place the fabricated-compliance class will land — inside Core's own mouth.

---

## 4. Top improvements (what to do first)

Ordered by "closes a measured failure class" then "closes a ratified decision the code already half-built."

1. **Unify or bind the three ledgers (G1).** Highest leverage. The FORGED-on-reinstall event already happened on this machine. Until this is closed, `install` is a loaded gun aimed at `serve`.
2. **Compose the execution path on Kernel (G2).** Dispatcher + Runner drain + IngressGate + node-rail registration at writing boot. Service stops importing BTS. This is also how DOM-first (G3) becomes a fact instead of a sort key in a test.
3. **Close the runner `-c` / Job Object gap (G4).** This is RCE-shaped on the submit surface the phone can already reach.
4. **Cut SegmentedLedger + CAS into Kernel (G5).** The module is written; the live authority file is already mostly `TOOL_DECLARED` replay tax.
5. **Seed.stream + reconstructed close (G7).** Carry-over is the product. A seed that cannot name its lane is an OPEN_CONTEXT that currently looks green.
6. **One spend book (G9) and a health row that can go RED on leases (G8).** Cheap, and they are the exact predecessor checker failures.
7. **Resolver for hands (G10).** Drive literals on the voice path are a distribution blocker and a two-universes bug waiting on the next letter.
8. **ReturnWatcher as a kernel type (G6).** Completes the seven primitives; makes hung rails visible.
9. **Windows service wrapper + recovery (Decision 1 remainder).** `schtasks onlogon` is not recovery; a crash between logons is a silent Core death. Pair with backup-as-`rehearse-restore` *job type* and Task Scheduler *read-back*.
10. **Disposition the UNDECIDED backlog from `cosmos_port_plan.py` in slices, with behavior cards.** Do not bulk-port 135 files. The migrate report is already the worklist.

Do **not** reopen: reserve-deny-call-settle, MCP-not-A2A, vendor plurality, fail-closed, never-delete-stage-to-`_delme`, no-bats, one-tree-one-truth.

---

## 5. What is already standing (so the gaps are not the whole picture)

These are real, tested, and should not be redesigned:

- **Resolver** (`cosmos_paths.py`): one root, sentinel *content*, no import-time IO, typed kinds, `extended()` MAX_PATH. This spike held.
- **Ledger primitive** (`cosmos_ledger.py`): hash-chain, HMAC (full hexdigest now; 32-hex legacy still verifies), OS sidecar lock (msvcrt offset-0, measured B1 fix), `STALE_HEAD`, `append_guarded`. Torn ≠ broken ≠ forged.
- **Arbiter protocol** (`cosmos_lock.py`): monotonic tokens across restart, four-phase fenced commit, dying-holder recovery, `COMMIT_UNFENCED` for legacy 0-arg callbacks. Cross-process mutex matches the ledger's.
- **Scheduler claim** (`cosmos_sched.py`): optimistic concurrency, clean `LOST_CLAIM`, three worded outcomes, report-never-retry. Stale-RUNNING stuckness (G46 HIGH) remains.
- **Session HMAC seed** (`cosmos_session.py` + `cosmos_validate.read_verified`): length + hash + install-key MAC + tree_id. The mechanism is the product.
- **Voice safety layer** (this HEAD): SpendGuard fail-closed, control/kill channel, Opus turn cap, dedupe window, body cap, constant-time bearer compare, remote-bind will not mint a token.
- **Ingress envelope** (`cosmos_ingress.py`): declaration vs bytes, `INGRESS_ACCEPTED`/`REFUSED`, never-delete rename. Not composed (G2), but the gate is written.
- **Fail-closed as culture:** the 2026-08-25 queue orphan was staged, not repaired. That is correct behavior. The gap is that `install` can still create the orphan.

---

## 6. Unknowns (not guessed)

- Whether `serve` is running *right now* on port 8770, and whether a Runner is attached in that process. Ledger says 9 `BOOT_VERIFIED` and one rail dispatch; that is not a process table.
- Whether `trylive/` is a trial root still in use (it has certs, `opus_turns.json`, `spendguard_state.json` that `live/` does not). Two populated roots in one tree is a split-brain hazard if someone points `--root` at the wrong one. Not investigated beyond listing.
- Incumbent `bts_*.ask` contracts (G46 UNKNOWN, still). Wrap-don't-reimplement is correct; the `ok` default-True (`r.get("ok", True)` in `NodeRail.dispatch`) is still a silent success on a missing field.
- Whether `ledger.project` deep-copies nested dicts (spend HIGH if shared).
- DOM secret store / CDP interact — explicitly UNKNOWN in the ratification; dump-dom does not close it.
- HA / multi-writer — UNKNOWN, out of MVP; restated so it is not "forgotten closed."

---

## 7. What this pass did not verify

- No pytest / selftest run. Prior native suite notes (`docs/F5_CORE_BUILD_NOTES.md`, `docs/V1_SUITE_RESULTS.md`) are dated 2026-08-23 and do not cover the 2026-08-25 voice/spendguard/brain work at HEAD.
- No HTTP round-trip to a live `serve`.
- No read of `install_key.bin` / `api_token.txt` contents (presence only).
- `docs/G46_TOOL_REVIEW_2026-08-25.md` HEART/lock section is empty; this file does not replace a line-level lock review. The arbiter protocol was read for composition and live-use, not re-audited instruction-by-instruction.

---

## Sources (read)

- `BUCm.toml`, `CLAUDE.md`, `README.md`
- `docs/FINAL_ARCHITECTURE.md`, `docs/RATIFIED.md`, `docs/COSMOS_PIPELINE.md`, `docs/SCAR_PLACATION.md`, `docs/SPIKE_BRIEFS.md`, `docs/STAGE2A_INCUMBENT_BEHAVIOR.md`, `docs/G46_TOOL_REVIEW_2026-08-25.md`, `docs/V1_SUITE_RESULTS.md`
- `cosmos/cosmos.py`, `cosmos_kernel.py`, `cosmos_ledger.py`, `cosmos_lock.py`, `cosmos_sched.py`, `cosmos_paths.py`, `cosmos_service.py`, `cosmos_session.py`, `cosmos_spend.py`, `cosmos_spendguard.py`, `cosmos_rails.py`, `cosmos_node_rails.py`, `cosmos_registry.py`, `cosmos_runner.py`, `cosmos_platform.py`, `cosmos_dom.py`, `cosmos_browser.py`, `cosmos_health.py`, `cosmos_validate.py`, `cosmos_backup.py`, `cosmos_migrate.py`, `cosmos_port_plan.py`, `cosmos_segments.py`, `cosmos_ingress.py`, `cosmos_mcp.py`, `cosmos_up.py`, `cosmos_orchestrator.py`
- Live: `live/ledger/authority.jsonl` (event-type histogram only), `live/state/SEED.json`, `live/state/SEED.decl.json`, `live/config/install_record.json`
