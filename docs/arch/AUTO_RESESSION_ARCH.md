# AUTO-RESESSION ARCH — MOTIF stage-2 ARCHITECTURE

**Stage:** 2 ARCHITECTURE (MOTIF.md). **Author:** G46 (Grok Build). **Date:** 2026-08-26.
**Wish:** `docs/WISHLIST.md` HEADLINE AUTOMATED RESESSION + open line AUTO-RESESSION; `docs/BACKLOG.md` same.
**Target path:** `docs/arch/AUTO_RESESSION_ARCH.md`. **P10:** proposed, not filed. **No tree write. No COSMOS core edited.**
**Baseline (do not rebuild):** `docs/research/AUTO_RESESSION.md` (G46, 2026-08-26, stage-1 RESEARCH). This file consumes that rubric and binds it to **already-built** Resume Gate / SEED / WD2 / fencing artifacts.
**Inputs (asserted, then used):**
- `docs/research/AUTO_RESESSION.md` (Layer A vs Layer B; `--continue` is not the engine)
- `docs/PAUSE_PROTOCOL.md` (two pause kinds; Resume Gate arming)
- `docs/FINAL_ARCHITECTURE.md` AD-2 (leases + fencing) + AD-10 (context manifests)
- `docs/ORCHESTRATION.md` (15s Activity Clock; cadence rubric; logged-on only)
- `docs/MOTIF.md` + `docs/MOTIF_TRACKER.md` (route + stage cursor)
- `docs/SCAR_PLACATION.md` (a claim is not evidence)
- `cosmos/cosmos_principles.toml` P1, P2, P3, P5, P7, P8, P9, P10
- `cosmos/cosmos_session.py` + `cosmos_context.py` (SEED write/read, HMAC, OPEN_CONTEXT)
- `cosmos/cosmos_watchdog2.py` `maybe_auto_resume`
- `cosmos/cosmos_lock.py` (monotonic fencing token + `fenced_commit`)
- `cosmos/cosmos_sched.py` (`claim_next` `expect_head_seq` / `LOST_CLAIM`)
- `cosmos/cosmos_motif_driver.py` (`inflight_filenames`, `ledger_inflight`, `is_advancing`, `motif_token`)
- `cosmos/cosmos_dispatch.py` (PROVEN grok/claude spawn flags)
- `cosmos/cosmos_own_clocks.py` `CLOCKS` (ids 1–16 taken)
- Live: `live/state/SEED.json` + `SEED.decl.json`; `live/state/control/PAUSE.flag`; `BUCm.toml`
**`rc=0` is not complete. Stage-6 (MOTIF_TRACKER numbering) is named here, not claimed.**

Keith (`docs/WISHLIST.md`):

> COSMOS resessions itself across the context boundary with zero / minimal user disturbance — the resume-gate (P3) is already built and canon.

The hole, already named in stage-1 (`docs/research/AUTO_RESESSION.md` §3.2): **WD2 can resume the route. Nothing currently spawns the next COW process when the last one dies.** This arch closes that loop **and** the pre-truncation gap the research left open: the SEED must be written **while there is still room**, never after the window is gone.

---

## 0. What already exists (reuse; do not reinvent)

| Mechanism | Artifact | Already does | Does **not** do |
|---|---|---|---|
| Signed SEED | `cosmos_session.close_session` → `live/state/SEED.json` + `SEED.decl.json` (`len`/`sha`/`mac`) | AD-10 close; HMAC-SHA256 over `cosmos-session-seed/1` + `tree_id` + exact bytes with the install key; dated archive under `state/seeds/` (never unlink) | Does not spawn an LLM. Live body is **thin**: `facts={}`, `watchers={}`, `sid=inherit`, **no leases, no MOTIF cursor, no `auto_resume_at`** |
| BootUP inject | `cosmos_session.start_session(stream)` | `read_verified` (INTEGRITY) → install-key MAC (AUTHENTICITY) → `tree_id` vs sentinel (IDENTITY) → inject facts/watchers; ledger `SESSION_SEED_INJECTED`. Typed refusals: `NO_SEED` / `BAD_SEED` / `IDENTITY_MISMATCH` | Does not pack or require MOTIF cursor. Extra JSON keys are ignored today |
| OPEN_CONTEXT | `cosmos_context.Session.close` + reconstruct path in `close_session` | Forced close over unresolved watchers **records** `OPEN_CONTEXT` then `SESSION_CLOSED`. `boot_inherit` folds every incident for the next boot | Missing-SEED at **start** raises `NO_SEED` and does **not** append `OPEN_CONTEXT` (gap this arch closes on the satellite path) |
| Resume Gate (P3) | `PAUSE.flag` `mode` + `cosmos_watchdog2.maybe_auto_resume` | `hold` never self-clears; `resume_gate` unlinks the flag at `auto_resume_at` (parse fail → stay PAUSED). Heartbeat stays `state=PAUSED` while the file exists (paused ≠ dead) | **No production writer of `mode=resume_gate`.** Only tests write it. Live flag this pass is `mode=hold`, no `auto_resume_at`, reason `TidyUP + resession (Keith, 2026-08-25)` |
| Activity Clock | `cosmos_watchdog2.py` 15s daemon, CLOCKS id 1 | Drives MOTIF route; max 3 drops/pass; skips inflight via `motif_token` / `is_advancing` / `ledger_inflight` | Drops **workers**. Assumes a COW exists. Does not spawn Layer B |
| Job exactly-once | `cosmos_sched.claim_next(..., expect_head_seq=head)` | Racing loser → `LOST_CLAIM`. `done` only by claimant. `report_stale` **reports, never auto-reruns** | Not a session fence. Stale RUNNING can look inflight forever (anti-dup **and** a stranded-job gap; P5 reconcile owns the re-drop) |
| Resource fence | `cosmos_lock.Arbiter` `Lease(resource, holder, token, granted_at, expires_at)` + four-phase `fenced_commit` | Monotonic token; stale commit → `STALE_TOKEN` / `COMMIT_REFUSED`. HMAC-signed `leases.jsonl` | Kernel audit counts resource `"tree"` only. **No `resource="cow"`.** SEED does not snapshot leases (AD-10 miss) |
| MOTIF cursor | `docs/MOTIF_TRACKER.md` table + `parse_tracker` / `effective_stage` | Honest stage per deliverable. Token `motif_{slug}_s{N}` | Markdown, **not signed**. Not in SEED. Dual droppers (WD2 15s + Motif Driver 15m) |
| Dispatch recipes | `cosmos_dispatch.py` | Proven: `grok --single … --always-approve --max-turns 60 --cwd <dir>`; F5 twin `claude -p … --permission-mode dontAsk --add-dir` | Worker jobs, not BootUP |
| BUCm pointer | `V:\A\Ai\COSMOS\BUCm.toml` (git-ignored, `bucm/1`) | Canon: *lightweight agent-session pointer beside the SEED. One truth, never a competing second handoff* | In practice a **second narrative store** (`[tidyup]`, `[next].in_flight`, resume text). `[read_order]` lists BUCm → CLAUDE.md → FINAL_ARCHITECTURE → COSMOS_PIPELINE — **SEED is not in that list** |
| Competing BTS handoff | `cosmos_brain.py` `BRAIN_BU_MD = r"V:\Ai\BU.MD"` comment *STATE OF RECORD* | Voice brain still injects BU.MD | Violates one-SEED-truth. Named for collapse (Slice-3) |

Layer A (clocks, runner, collector, Core `:8770`) **already survives** a Cowork/CLI death. Auto-resession is Layer B: a **fresh** orchestrator, seeded from COSMOS carry-over, with no human turn. Vendor `--continue` / `--resume` **replays the same transcript** (research R1 fail) and is reserved only for crash-recovery of a still-roomy PID.

---

## 1. Decision rubric (stated first, per Motif stage 2)

Scored before any wiring. A FAIL on any hard row eliminates. No aggregate number.

### Hard (FAILS = do not wire)

| id | criterion |
|---|---|
| **H1 Fresh window** | Context-full is the failure. Same-transcript `--continue`/`--resume`/`--fork-session` FAILS. Spawn is a **new** vendor session id. (`docs/research/AUTO_RESESSION.md` R1) |
| **H2 COSMOS seed, not vendor memory** | Carry-over authority is HMAC `live/state/SEED.json` (+ `SEED.decl.json`). BUCm is a pointer. BACKLOG / MOTIF_TRACKER / DHx / collector index are **projections the new COW reads after inject**. A design that BootUPs from Claude/Grok transcripts or `V:\Ai\BU.MD` FAILS |
| **H3 Default is MOTION (P3)** | `hold` never self-clears. `resume_gate` carries `auto_resume_at` and self-clears on the 15s WD2 clock. Unattended path does **not** wait for a click. Keith-present BootUP still presents the one option (canon); headless satellite **is** the ratified default |
| **H4 Unattended permissions** | Spawn uses **existing** dispatch flags (`--always-approve` / `--permission-mode dontAsk`). A Scheduled Task cannot click Allow. `--bare` FAILS (BootUP needs `CLAUDE.md`). `--restore-code` FAILS (live tree) |
| **H5 Additive, keep-her-afloat (P7)** | Live Core `:8770` and the running clocks stay up through the mechanism. Satellite does **not** edit `kernel` / `ledger` / `sched` / `service`. SEED-field thickening is an additive `cosmos_session` patch invoked by the **CLI Kernel** (`cosmos.py session`), not a serve restart. One writer of the route. A change that takes COSMOS down to install auto-resession is the wrong change |
| **H6 Windows clock, logged-on only** | Detector + spawn ride a COSMOS-own clock (`docs/ORCHESTRATION.md`). `schtasks` floor = 1 min; faster = detached daemon + 1-min self-heal. No `ONSTART` (`V:` is a user-session volume). No bats. No Cowork `/loop` |
| **H7 One orchestrator** | At most one live COW. Mutex is arbiter lease `resource="cow"` (reuse AD-2; do not invent a second lock file as authority). Two BootUPs double-dropping FAILS |
| **H8 Fail-closed on a bad SEED** | Missing / unparseable / MAC-fail / wrong-`tree_id` / schema-not-COSMOS → **refuse + surface**, never resume, never `--continue` around it, never invent an empty seed. Typed kinds already exist (`NO_SEED` / `BAD_SEED` / `IDENTITY_MISMATCH`); the satellite must **ledger** them, not only raise |
| **H9 SEED written before truncation** | The watermark fires **while the current window still has room**. A detector that only notices “process gone” / “prompt too long” is a **backstop**, not the engine. Writing the SEED after compact-cliff or after the process is dead FAILS this row (it may still self-heal via the quiet path, visibly) |
| **H10 HOLD is sacred; TidyUP-handoff is not** | Operator `mode=hold` (Keith says stop / mesh-destroy / dissertation boundary) **never** self-clears and **never** gets rewritten by the satellite. The live TidyUP-handoff hold (`set_by=COW`, reason contains `TidyUP`) **is** the P3 arming case: satellite (not an LLM) is the missing production writer of `resume_gate` |
| **H11 Exactly-once across the boundary** | A resume must not re-dispatch an in-flight `motif_{slug}_sN` or re-claim a live `JOB_CLAIMED`. Reuse sched head-fence + motif inflight tokens + SEED snapshot. Silent re-claim of stale RUNNING FAILS (P5: report, then explicit re-drop) |
| **H12 Improvement is not bloat (P8)** | One SEED truth. No second handoff format. No vendor memory product. No second pause primitive. Collapse BUCm narrative + `BRAIN_BU_MD` rather than adding a third store |

### Soft (rank the survivors)

| id | criterion |
|---|---|
| **S1 Proven on this PC** | Grok CLI 1.0.5 on PATH with dispatch recipe; Claude 2.1.220 as F5 twin; Cursor `agent` **not** on PATH (research) |
| **S2 Fewest new processes** | One satellite (`cosmos_resession.py`), CLOCKS **id 17**. Not a branch that can hang WD2’s retask loop |
| **S3 File-shaped signals** | Detect from files + PID, not UI scrape. Vendor “window full” flag is UNKNOWN (research §3.4) — do not pretend it exists |
| **S4 Grace is one WD2 tick** | Canon says `auto_resume_at = now + grace` but **never names grace**. This arch names it: `AUTO_RESUME_GRACE_S = 15` (one Activity Clock cycle). Tunable; default MOTION |

### Classification

| class | meaning | next |
|---|---|---|
| **WIRE** | H1–H12 hold. Slice-ready | stage 3 critique, then stage 4 code |
| **HOLD** | Real, but needs a named Core-adjacent patch or Keith-gated auth | design now; build after the dependency |
| **OVERFLOW** | Works, overlaps a live path | do not build first |
| **REJECT** | Fails a hard row | do not promote |

**WIRE:** COSMOS-native resession satellite + thickened SEED + P3 arming writer + `resource="cow"` lease. Spawn rail #1 Grok fresh `-p`/`--single`; rail #2 Claude F5 twin.

**HOLD:** Cursor local `agent -p --force --trust` until the Cursor binary is the one on PATH. Cowork tab has **no documented unattended path** (research) — Keith still opens that UI when he wants it; the **route** does not wait.

**REJECT:** `--continue` as the context-full engine; `--fork-session`; Claude Desktop local scheduled tasks as the COSMOS clock; Cowork auto-restart; `/loop`; a second SEED format; Memanto-class vendor memory; rewriting an operator HOLD.

---

## 2. The two layers, and the one loop

```
 Layer A  (already alive)                         Layer B  (dies with the window)
 ┌─────────────────────────────────────┐          ┌──────────────────────────────┐
 │ Core :8770  WD2  runner  collector  │          │ COW process (Cowork / grok   │
 │ motif-driver  dispatch  queue       │          │  -p / claude -p)             │
 │ leases.jsonl  runner_ledger.jsonl   │          │  ← this is what auto-        │
 └─────────────────────────────────────┘          │     resession must replace   │
                                                  └──────────────────────────────┘
```

Auto-resession is **not** restarting Layer A. It is: **detect the Layer-B boundary while there is still room → write a thick HMAC SEED → arm `resume_gate` → spawn a fresh COW → `start_session` verifies the SEED → WD2 self-clears at `auto_resume_at` and drives the same MOTIF cursor.** Zero human turns on the unattended path.

Sequence (happy path):

1. **Arm** — every live COW writes `live/state/control/COW_HEARTBEAT.json` (projection) each synthesis cycle: `pid, rail, vendor_session_id, spawned_at, last_act_epoch, turn_n, tokens_in?, context_pct?`. Also `FACT_RECORDED` for `motif_cursor` as the route moves (incremental carry-over; TidyUP must not be the first time facts exist).
2. **Watermark** — satellite (CLOCKS 17) sees W1/W2 while the PID is still alive (H9).
3. **TidyUP** — satellite runs `py -3.14 cosmos\cosmos.py session close --handoff Cm --root <live>` (reconstruct path already in `close_session` when `self.session is None`). Packer (Slice-2) snapshots leases + MOTIF cursor + inflight + pause into the SEED. Ledger `SESSION_SEED_WRITTEN`.
4. **Arm gate** — satellite writes `PAUSE.flag` `mode=resume_gate`, `auto_resume_at=now+15s`, `origin=watermark`, `reason` required. WD2 heartbeats `PAUSED` (visible). Runner + collector **keep moving** (P2).
5. **Fence** — `arbiter.acquire("cow", holder="resession-<pid>", ttl=600)` ; heartbeat renews.
6. **Spawn fresh** — Grok (or F5) with **dispatch-copied** flags, `--prompt-file docs/AUTO_RESESSION_PROMPT.md`, **not** `--continue`. Capture `sessionId` / `session_id`.
7. **BootUP inject** — new COW (or satellite just before spawn) runs `cosmos.py session start Cm`. MAC/len/sha/`tree_id` must verify. Inherit includes `motif` cursor.
8. **MOTION** — WD2 `maybe_auto_resume` unlinks the flag at `auto_resume_at`. Route continues from `max(SEED.motif.stage, MOTIF_TRACKER effective_stage)` and **never rewinds**. Inflight tokens in SEED ∪ live ledger are skipped (H11).
9. **Quiet backstop** — if the PID dies *before* the watermark (crash), satellite takes the quiet path: if SEED MAC verifies, spawn anyway (visible `spawn_reason=quiet`); if close never ran, append `OPEN_CONTEXT` and **refuse to invent a seed**. Resume from last valid SEED + MOTIF_TRACKER + BACKLOG, with the incident in the inherit. Not silent.

---

## 3. TRIGGER — detect the boundary before it bites

No vendor CLI flag means “window full; start a new one” (research §1.5, §3.4). Claude/Grok **auto-compact** instead of exiting; compaction is **not** COSMOS carry-over. UI scrape is not a COSMOS clock. The trigger is therefore **file-shaped and conservative**, owned by the satellite, with three stacked detectors. **W1/W2 are the engine. W3 is the self-heal.**

### 3.1 Projection: `COW_HEARTBEAT.json`

Path: `live/state/control/COW_HEARTBEAT.json` (under existing resolver role `state/`, same directory as `PAUSE.flag`; **no new `ROLES` entry**).

```json
{
  "schema": "cosmos-cow-heartbeat/1",
  "tree_id": "KMesh-COSMOS-live",
  "pid": 0,
  "rail": "grok",
  "vendor_session_id": "",
  "spawned_at": "",
  "last_act_epoch": 0,
  "turn_n": 0,
  "tokens_in": null,
  "tokens_out": null,
  "context_pct": null,
  "motif_cursor": {"slug": "", "stage": 0}
}
```

Writer: the live COW (prompt-contract) **and** the satellite (on spawn: pid + vendor id + `spawned_at`). Authority for *resume position* remains the SEED, not this file. A missing heartbeat is a signal (treat as quiet), not a resume source.

### 3.2 W1 — session-age / turn watermark (always available)

| knob | default | why |
|---|---|---|
| `SESSION_AGE_WATERMARK_S` | `2700` (45 min) | Context fills on a busy COW far before a 5-hour seat; 45 min leaves room for TidyUP. Tunable |
| `TURN_WATERMARK` | `40` | Dispatch `GROK_MAX_TURNS = 60`. Reserve **20 turns** as the TidyUP budget so `close_session` still fits |
| `HEARTBEAT_STALE_S` | `180` | Feeds W3, not W1 |

Fire W1 when **either** `now - spawned_at >= SESSION_AGE_WATERMARK_S` **or** `turn_n >= TURN_WATERMARK`, **and** the orchestrator PID is still alive. Then TidyUP immediately (step 3). Do not wait for compact.

### 3.3 W2 — context-budget watermark (best-effort, vendor-plural)

If the rail reports usage (`tokens_in` / `context_pct` from `--output-format json` when that field is **measured** at build time — UNKNOWN until the filled-session probe, research §3.4). Honest fallback: Grok `~\.grok\sessions\<cwd>\<id>\signals.json` token counters — **not** TUI scrape, **not** unstable JSONL as the watermark.

**Keith 2026-09-01 (discussion, not wired):** two lines, not one.

| line | when | what |
|---|---|---|
| **W2-pack** | `context_pct >= 0.70` (or `tokens_in >= 0.70 * window` once quoted) | **Start packing.** Autorun TU then **COSMOS TU2** (adversarial recount of lists vs disk), write BU / thicken SEED **while the dying COW still has room.** Do not spawn yet. |
| **W2-close** | `context_pct >= 0.90` | **Hard close.** Finish SEED HMAC, print `SESSION CLOSED` ×3, `TEXT SAVED TO <pack>`, spawn a **fresh interactive Grok Build TUI** `--cwd V:\A\Ai\COSMOS` with prompt-file / BootUP. Not `-c`/`-r`. Pack lands in `live/state/session_saves/`. |

70% pack / 90% close ratified 2026-09-01. If `context_pct` is absent, W2 is a no-op and W1 carries the wish.

**TU2 (Keith 2026-09-01 — add it).** BTS TidyUP2 is the adversarial pass after TidyUP (*"what did doing the steps break, and what did I claim without checking"* — `V:\Ai\BTS_MESH\tidyup2_*.py`). That is good; COSMOS did not have the twin. **Do add a COSMOS-own TU2:** recount MOTIF/BACKLOG/in-flight/leases/produced-files against the filesystem; refuse a green TU that the disk contradicts. Optionally **read** a BTS tidyup2 board into the save pack as census. **Do not execute** `V:\Ai` tidyup2 scripts from this COW (two-pen; those tools write `V:\Ai`). GrokBot still runs BTS TU2 on its own close.

**Spawn / pack home (Keith 2026-09-01):** interactive TUI, not headless `-p`. Archive under `live/state/session_saves/`. SEED remains authority.

**Do not scrape the Cowork UI. Do not parse unstable JSONL transcripts as a watermark** (`cosmos_context_pull.py` is a dispatch tail, not a full-window detector). Not implemented this session.

### 3.3a Improper close — resume where it ended (Keith 2026-09-01)

A session that dies **before** W2-close (kill TUI, crash, power) must not BootUP from a stale SEED as if TidyUP ran.

Grok already keeps the vendor log: `~\.grok\sessions\<encoded-cwd>\<id>\` (`updates.jsonl`, `chat_history.jsonl`, `signals.json`, `plan.json`). Pull that when it exists.

Also write a live pointer **continuously** (not only at TU), to the TUI screen and to:

`live/state/running_session_file.toml`

Cursor, last user line, grok `sessionId`, pid, files touched, motif position. Projection, not a second SEED (H12). Proper TU **seals** it into HMAC SEED and the session_saves pack.

Next session:

| how the last one died | what the next one does |
|---|---|
| Proper W2-close | Fresh TUI + BootUP from HMAC SEED. Not `-c`. |
| Improper close, window still roomy | Resume vendor log (`grok -c` / `-r <id>` for that cwd) **and** read `running_session_file.toml`. Crash-recovery of a still-roomy session — the one case `-c` is allowed. |
| Improper close, window full or log missing | Fresh TUI. Promote `running_session_file.toml` into inject, typed `OPEN_CONTEXT` / `IMPROPER_CLOSE`. Never `--continue` a full window. |

W3 still prefers a valid SEED if one was written. The running file is the backstop when it was not.

### 3.4 W3 — quiet / death backstop (not the engine)

Any one:

- recorded pid in `RESESSION.json` is not alive, **and** BACKLOG / MOTIF_TRACKER still has open items;
- `COW_HEARTBEAT.last_act_epoch` older than `HEARTBEAT_STALE_S` while items remain open;
- last `SESSION_SEED_WRITTEN` older than the age watermark **and** no live pid.

W3 **must still prefer a valid existing SEED** over a panic close. If the session is still ledger-open, attempt `session close` (reconstruct) **before** spawn so the next inject is current. If close refuses (`CONTROL_INVALID`, unresolved watchers without `--force`), **do not spawn**; surface the refusal. `--force` is only for unresolved watchers and **already** records `OPEN_CONTEXT` — the satellite may pass `--force` only when W3 is the path and watchers would otherwise block carry-over; the incident is required reading at next BootUP (`cosmos_context.py` detail: *the next boot MUST read this*).

### 3.5 What the trigger must never do

- Wait for “Prompt is too long.” That is after the bite (H9 fail).
- `--continue` the full window (H1 fail).
- Compact-and-hope (vendor summary ≠ SEED).
- Kill in-flight workers (P2: PAUSE is a gate, not a kill).
- Call `close_session` **after** the process is truncated **as the only plan**. Reconstruction from the ledger only sees facts that were `FACT_RECORDED`. That is why packing from **disk sources** (MOTIF_TRACKER, leases.jsonl projection, runner ledger, assigned.json) is mandatory in Slice-2 — COW memory is not the authority.

---

## 4. SEED contract — additions for a clean auto-resume

### 4.1 Live body today (host, this pass)

`live/state/SEED.json` (`schema=cosmos-session-seed/1`):

```
closed_epoch, facts={}, handoff="Cm", incidents=[], kind="COSMOS_SEED",
schema, sid="inherit", tree_id="KMesh-COSMOS-live", watchers={}
```

`SEED.decl.json`: `len=218`, `sha=51373295e6b5f2366a8c8aad124dec38dcd501bc76db3941f6942749cbd48a88`, `mac=3a1348580d2dd72df2c64940b91b7097eaab33293ab182e4cadbd4cf723a450c`.

AD-10 (`docs/FINAL_ARCHITECTURE.md` decision 10): *inherited facts, **active leases**, open watchers, handoff recipient*. **Leases are named in canon and absent in the writer** (`close_session` seed dict at `cosmos_session.py` ~254–264). `cosmos_context.Session` docstring says “facts/watchers/leases”; the object only has `_facts` and `_watchers`. Thin `facts={}` is why a resession today cannot resume an **exact** MOTIF position from the HMAC manifest — it would have to re-parse markdown and hope.

### 4.2 Schema policy (additive, keep-her-afloat)

`start_session` currently **hard-equals** `schema == "cosmos-session-seed/1"`. A bump that does not accept `/1` would refuse the live seed and brick BootUP (H5/H8).

| rule | contract |
|---|---|
| Writer (Slice-2) | Emit `cosmos-session-seed/2` when the thick packer ran |
| Reader | Accept `/1` **or** `/2`. `/1` injects facts+watchers as today. `/2` also returns `leases`, `motif`, `inflight`, `auto_resume_at`, `stream` |
| Auto-resession satellite | Prefers `/2`. A valid `/1` is **not corrupt**: ledger `SESSION_SEED_THIN`, resume from MOTIF_TRACKER + BACKLOG + DHx (fail **visible**). A `/2` missing required keys is `BAD_SEED` (corrupt shape) |
| HMAC | Unchanged algorithm: `HMAC-SHA256(install_key, schema + \x00 + tree_id + \x00 + exact_seed_bytes)` over the **declared schema string inside the body**. Sidecar `schema` field follows the body |

Do **not** mint a second file (`SEED2.json`, `HANDOFF.json`). Same fixed name, same sidecar, same dated archive.

### 4.3 `/2` body (additive keys; `/1` keys kept)

```json
{
  "schema": "cosmos-session-seed/2",
  "kind": "COSMOS_SEED",
  "tree_id": "KMesh-COSMOS-live",
  "sid": "Cm-<n>",
  "stream": "Cm",
  "handoff": "Cm",
  "closed_epoch": 0.0,
  "facts": {
    "motif_cursor": "<slug>@<stage>",
    "last_disposition_at": "<ISO>",
    "wishlist_head": "<first open wish slug>"
  },
  "watchers": {},
  "leases": [
    {"resource": "tree", "holder": "", "token": 0, "granted_at": 0.0, "expires_at": 0.0}
  ],
  "motif": {
    "cursor": {"slug": "auto-resession", "stage": 2},
    "route": [
      {"slug": "auto-resession", "stage": 2, "next_stage": 3, "artifact": "docs/arch/AUTO_RESESSION_ARCH.md", "inflight_token": null}
    ]
  },
  "inflight": [
    {"job": "motif_cvm_s4", "state": "JOB_CLAIMED", "claim_seq": 0, "token": null}
  ],
  "auto_resume_at": "<ISO or null>",
  "pause_mode": "resume_gate",
  "incidents": []
}
```

**Why `facts.motif_cursor` as well as `motif.cursor`:** today’s `start_session` already injects every fact via `record_fact`. A `/2` writer that also copies the cursor into `facts` keeps the `/1` inject path honest even before the reader is taught the new keys (P8: one mechanism, two views, not two stores).

**Packer sources (disk, not COW RAM)** — `close_session` after `boot_inherit`:

| field | source (already on disk) |
|---|---|
| `facts` | `boot_inherit` ∪ `motif_cursor` from `parse_tracker` ∪ last `<!-- cow-disposition` stamp if present |
| `watchers` | existing Session / reconstruct / OPEN_CONTEXT incidents (already) |
| `leases` | `Arbiter` live projection (`status` / replay of `ledger/leases.jsonl`) for resources that are currently held. Empty list is valid |
| `motif.route` | `cosmos_motif_driver.parse_tracker` + `effective_stage` on `docs/MOTIF_TRACKER.md` |
| `motif.cursor` | the in-flight COW item if `COW_HEARTBEAT.motif_cursor` is fresh; else the first tracker row not at stage 6 and not inflight |
| `inflight` | `ledger_inflight(ledger_paths(queue))` ∪ `inflight_filenames` ∪ `live/state/watchdog2/assigned.json` |
| `auto_resume_at` / `pause_mode` | the flag the satellite just armed, or the existing `PAUSE.flag` |
| `stream` | argument / `handoff` (closes the BUCm note that SEED `stream` came back null — it was **never a field**) |

`FACT_RECORDED` still truncates `value[:500]` (`cosmos_context.py`). Cursor strings must stay under that cap (`slug@stage` does). Structured `motif.route` lives **on the seed object**, not as one giant fact string.

### 4.4 Merge rule at resume (clocks may have moved)

Layer A is **not** paused except for **new retask** during the 15s gate. In-flight jobs finish; collector files. Motif Driver honors PAUSE presence (new submits stop; comment: *resume_gate self-clears elsewhere (WD2)*).

Therefore SEED.motif is **COW’s last known synthesis position**, not a freeze of the universe.

On inject:

1. Never rewind: `resume_stage = max(SEED.motif.cursor.stage, tracker.effective_stage(slug))`.
2. Never re-drop: skip if `motif_token(slug, stage)` is in `SEED.inflight` **or** live `ledger_inflight` **or** `is_advancing`.
3. P5 first act of the new COW: DIFF DHx assigned vs `live/state/collector/index.jsonl`; re-drop **only** rows whose job is `JOB_STALE` / never returned — not `JOB_CLAIMED` still live.
4. If SEED.cursor slug is gone from the tracker (completed/superseded), do not resurrect it; take the next open wish (WISHLIST → MOTIF s1), and record `FACT_RECORDED` `cursor_skipped=<slug>`.

Exact-position resume means: **the same slug@stage COW was synthesizing, unless Layer A already advanced it.** That is keep-her-afloat, not a time machine.

---

## 5. HANDOFF — start the next session, read the SEED, one truth

### 5.1 Satellite (WIRE, Slice-1, no kernel edit)

New file `cosmos/cosmos_resession.py`, same class as `cosmos_watchdog2.py` / `cosmos_motif_driver.py`. CLOCKS **id 17**:

| field | value |
|---|---|
| clock | COSMOS Resession |
| cadence | 15s detached daemon (W1/W2 must beat truncation; 1 min schtasks floor is too coarse for H9) + 1-min self-heal + onlogon |
| task | `COSMOS Resession` / `COSMOS Resession Logon` |
| heartbeat | `live/logs/resession_heartbeat.json` |
| control projection | `live/state/control/RESESSION.json` |
| CLI | `--root <live> --once \| --loop \| --standup \| --status` |
| logged-on only | yes (H6) |

It does **not** instantiate a writer-Kernel on every tick. `session close` / `session start` / `arbiter.acquire("cow")` run **only** on a fire (watermark/quiet/spawn), as short CLI/Kernel uses — same pattern as backup/verify clocks talking to Core without becoming a second Core.

Prefer a **separate** satellite (research §3.3): a hung spawn must not stall WD2 retask.

### 5.2 `RESESSION.json` is a projection, not a second SEED

```json
{
  "schema": "cosmos-resession/1",
  "tree_id": "KMesh-COSMOS-live",
  "state": "IDLE|ARMED|SPAWNED|REFUSED|HOLD",
  "spawn_reason": "watermark|quiet|crash-continue|null",
  "rail": "grok|claude",
  "pid": null,
  "vendor_session_id": null,
  "prev_vendor_session_id": null,
  "spawned_at": null,
  "prompt_sha": null,
  "seed_sha": null,
  "seed_sid": null,
  "seed_schema": null,
  "resumed_from": {"slug": null, "stage": null},
  "cow_token": null,
  "refused_kind": null,
  "refused_detail": null
}
```

Authority remains: HMAC SEED + ledger events `SESSION_SEED_WRITTEN` / `SESSION_SEED_INJECTED` / `OPEN_CONTEXT` / `SESSION_SEED_THIN`. If `RESESSION.json` disagrees with the SEED, the SEED wins and the projection is rewritten (fail visible).

### 5.3 Verify-then-spawn (H8)

Order is mandatory:

1. Read `PAUSE.flag`. If **operator HOLD** (H10) → `state=HOLD`, do not spawn, do not rewrite.
2. If TidyUP-handoff hold (`set_by=COW` and reason contains `TidyUP`) or no flag → this is P3 arming, continue.
3. If a fire requires a close: `cosmos.py session close --handoff Cm`. On `SessionError`/`ContextError` → `state=REFUSED`, `refused_kind=<kind>`, heartbeat, **no spawn**.
4. `start_session` checks **or** an equivalent read of `SEED.json` + `SEED.decl.json`:
   - missing seed → append ledger `OPEN_CONTEXT` `{detail: "auto-resession found no seed"}`, `refused_kind=NO_SEED`, **do not invent a seed**, **do not spawn** (Keith/manual BootUP is the recovery; H8).
   - sidecar missing / len/sha fail / mac missing or `hmac.compare_digest` fail → `BAD_SEED`, refuse.
   - `tree_id` ≠ sentinel → `IDENTITY_MISMATCH`, refuse.
   - `/2` missing required keys → `BAD_SEED`, refuse.
   - `/1` thin but MAC-valid → spawn allowed, `SESSION_SEED_THIN`, `resumed_from` taken from MOTIF_TRACKER not from empty facts.
5. Arm `PAUSE.flag` `mode=resume_gate`, `auto_resume_at=now+AUTO_RESUME_GRACE_S`, `origin=watermark|bootup`, reason+timestamp required (`docs/PAUSE_PROTOCOL.md`).
6. `acquire("cow")`. `HELD` → another orchestrator is live; **do not spawn** (H7).
7. Spawn **fresh** (H1). Record pid + vendor id + `seed_sha` (the sidecar `sha` just verified) + `resumed_from` (from the seed just read).
8. Next ticks: pid alive → noop. Pid dead + items open + lease expired → W3, **fresh** spawn again, never `--continue` of the dead full session.

`--continue` is **OVERFLOW**, crash-recovery only: pid died, `turn_n < TURN_WATERMARK`, age < watermark, last heartbeat fresh enough that the vendor window is still roomy. Even then, SEED must already be valid (close first if ledger-open). Documented in research §1.2: a schtask `claude --continue` **without** `-p` misses headless sessions — if this overflow is ever built, it is `claude -p --continue` / `grok -c -p`.

### 5.4 Spawn recipes (copy, do not invent)

From `cosmos_dispatch.py` (comments: *PROVEN flags; do not change*):

**Rail #1 (default, on PATH, prepaid Grok Build):**

```
grok --single "<prompt>" -m <model> --output-format json --always-approve --max-turns 60 --cwd V:\A\Ai\COSMOS --prompt-file docs/AUTO_RESESSION_PROMPT.md --no-auto-update
```

Capture JSON `sessionId` (camelCase — mixing Claude’s `session_id` is a bug, research §2.1).

**Rail #2 (F5 prepaid seat):**

```
claude -p --permission-mode dontAsk --output-format json --add-dir V:\A --add-dir V:\Ai --cwd V:\A\Ai\COSMOS
```

`--add-dir` is **not restored** on Claude resume and **does not exist** on Grok. Re-pass every spawn. Never `--bare`. Never leave `ANTHROPIC_API_KEY` stealing the prepaid seat (`docs/research/ANTHROPIC_HANDS.md`).

Prompt file (tracked): BootUP order from `BUCm.toml [read_order]` **plus** `live/state/SEED.json` under HMAC (run `cosmos.py session start Cm` and quote the returned inherit) **plus** `docs/BACKLOG.md` + `MOTIF_TRACKER.md` + DHx + `docs/COLLECTOR.md` + `live/state/collector/index.jsonl` **plus** “you are COW (P9): drop work, do not search in your own context; auto-resume the route at `resumed_from`; HOLD only if the flag is operator-sacred.”

### 5.5 BUCm vs SEED (one truth)

Canon (`CLAUDE.md`, `BUCm.toml [carryover]`): BUCm is the **pointer beside** the SEED.

**Collapse (H12 / P8):**

| stays in BUCm | moves into SEED `/2` (or dies) |
|---|---|
| `[meta]` schema/stream/repo_tree/runtime_root/tree_id/written_at | `in_flight`, `resume`, task narrative — these are facts + motif.route |
| `[read_order]`, `[mounts]`, `[run]`, `[hazards]` (session bootstrap / Keith mounts) | `[next].resume_gate` text — **code** in the satellite is the writer; the paragraph in BUCm becomes a pointer to PAUSE_PROTOCOL |
| `written_at` refresh each session (pointer freshness) | Duplicate resume instructions |

BootUP `[read_order]` **gains** `live/state/SEED.json` as an explicit step (it is already in the Resume Gate paragraph, missing from the list). BUCm does not grow a parallel cursor.

`cosmos_brain.BRAIN_BU_MD` (*STATE OF RECORD*) is a **real competing handoff**. Slice-3 demotes it: voice brain reads HMAC SEED facts head, not `V:\Ai\BU.MD`. Until that lands, auto-resession of **Cm** still uses SEED; voice remains a known split-universe (named, not papered).

### 5.6 OPEN_CONTEXT (close the start-path gap)

AD-10: *closure without a valid manifest ⇒ OPEN_CONTEXT incident.*

Today OPEN_CONTEXT is only the **forced-close-with-watchers** path. The satellite adds:

- spawn-time `NO_SEED` / unreadable seed → ledger `OPEN_CONTEXT` `{sid, detail, refused_kind}` **and** `RESESSION.state=REFUSED`;
- W3 close that needs `--force` → existing OPEN_CONTEXT (already implemented);
- never a silent “BootUP from empty”.

`start_session` itself stays a typed raise (CLI remains fail-closed). The satellite is the place that **records** the incident so the next successful boot’s `boot_inherit` sees it.

---

## 6. Idempotency / fencing — a resume never double-executes

Three fences already exist. Auto-resession **reuses** them and adds one mutex. It does not invent a fourth ledger.

### 6.1 Job fence (runner ledger) — already the exactly-once path

`cosmos_sched.claim_next` appends with `expect_head_seq=head`; a racing resume that tries to claim the same work gets `LOST_CLAIM` / `STALE_HEAD`. `done` by non-claimant → `BAD_STATE`. Pool comment: *exactly-once is that head-fence*.

**Resume rule:** the new session does not `submit` a job whose id/token is in `SEED.inflight` or live `ledger_inflight`. WD2 already skips `is_advancing(slug, next_stage, names)` matching `motif_{slug}_sN` and later stages. Keep that helper; do not fork a second matcher.

**Stale RUNNING:** `report_stale` **reports, never auto-reruns**. After resession, a dead worker’s claim must become `JOB_STALE` (existing) and only then may P5 re-drop. Silent reclaim would double-execute if the old worker was slow, not dead (H11).

### 6.2 Resource fence (arbiter token) — already AD-2

`Lease.token` is monotonic. `fenced_commit` Phase C CAS: once token N+1 is accepted, token N is `COMMIT_REFUSED`. Dying holder: expiry → TAKEOVER with a **higher** token; late commit refused.

**Add** `resource="cow"` (orchestrator mutex), TTL 600s, renewed from `COW_HEARTBEAT`. Holder `resession-<pid>` or `cow-<vendor_session_id>`. Satellite spawn is `acquire`; COW death + TTL expiry is TAKEOVER for the next spawn. A second satellite tick while the lease is live is `HELD` → noop.

Do **not** use `PAUSE.flag` as the orchestrator mutex (it is the retask gate). Do **not** use `RESESSION.json` as the mutex (projection). Do **not** snapshot the `cow` lease *as the thing that survives resume* — it is released/expired across the boundary on purpose so the **new** COW can acquire. Snapshot **tree** (and any other live resource) in `SEED.leases` so the new session **knows** what is held; it does not forge a token. Forging a stored token would be `STALE_TOKEN` anyway if expiry/takeover already moved the counter.

### 6.3 Retask fence (PAUSE + inflight names)

During handoff, `resume_gate` PAUSE stops **new** WD2 / motif-driver / dispatcher drops. In-flight **finish**. Filenames in `queue/running` + manifests stay in `inflight_filenames`. After auto-resume, WD2’s existing skip path is the daily driver; SEED.inflight is the **handoff-time** snapshot so a tick that races the collector cannot re-drop a job that ended between close and inject.

Dispatch idempotent job-file names (`created=False` if name exists) stay as the last line of defense.

### 6.4 What a new COW may do on day one

Allowed: `session start` inject, collector reconcile, dispose **returned** results (P10), drop the **next** unworked stage for a slug that is not inflight.

Forbidden: re-dispatch `motif_{slug}_sN` present in SEED.inflight; `claim_next` of a live claim; rewrite operator HOLD; `--continue` a full window; start a second COW.

---

## 7. FAIL-CLOSED — corrupt SEED never resumes

| condition | kind | satellite | Core/CLI |
|---|---|---|---|
| No `SEED.json` | `NO_SEED` | `OPEN_CONTEXT` + `RESESSION.REFUSED`; no spawn; no invented seed | `start_session` already raises |
| No sidecar / bad `len`/`sha` | `BAD_SEED` | refuse spawn | already raises (`read_verified`) |
| Missing/mismatched `mac` | `BAD_SEED` | refuse spawn | already `hmac.compare_digest` |
| `tree_id` ≠ sentinel | `IDENTITY_MISMATCH` | refuse spawn | already raises |
| Body not `COSMOS_SEED` / facts not object / watchers not object | `BAD_SEED` | refuse | already raises |
| `/2` missing `motif`/`leases`/`inflight` keys | `BAD_SEED` | refuse (corrupt shape, not thin) | reader Slice-2 |
| `/1` MAC-valid, empty facts | `SESSION_SEED_THIN` | spawn allowed, **visible**; cursor from MOTIF_TRACKER | inject as today |
| Ledger chain broken at close | `CONTROL_INVALID` | refuse close+spawn | `close_session` already refuses |
| Operator HOLD | `HOLD` | no rewrite, no spawn | WD2 never self-clears |
| `cow` lease HELD | `HELD` | no second spawn | arbiter already typed |
| Unparseable `auto_resume_at` | stay PAUSED | — | WD2 already fail-closed toward pause |

Corrupt ≠ thin. Thin is a packing bug to surface and fix on the next close. Corrupt is a lie. **Never `--continue` around a bad manifest. Never “resume from BACKLOG only” when the MAC failed** — that would treat a forged or silently-corrupted seed as absence. Absence is `NO_SEED` (loud). MAC failure is `BAD_SEED` (loud). Both refuse.

KDash / `cosmos status` / resession heartbeat must show `REFUSED` + kind the same way a paused clock shows `PAUSED` (PAUSE_PROTOCOL: a check that never ran is indistinguishable from one that passed — a refused resession that only stops is forbidden; it must heartbeat the refusal).

---

## 8. Keep-her-afloat topology (H5) and slices

Live Core `:8770` is **not** restarted. Clocks 1–16 keep their pids. New work is a satellite + an additive session-lifecycle packer.

| slice | lands | touches core? | keep-her-afloat |
|---|---|---|---|
| **Slice-1** WIRE | `cosmos_resession.py` + CLOCKS id 17 + `docs/AUTO_RESESSION_PROMPT.md` + P3 arming writer + `RESESSION.json` / `COW_HEARTBEAT.json` + `resource="cow"` acquire on fire | **No** kernel/ledger/sched/service source | Yes. Serve stays up. WD2 stays up |
| **Slice-2** WIRE | thicken `close_session` packer + `start_session` accept `/1`+`/2` + `SESSION_SEED_THIN` / spawn-path `OPEN_CONTEXT` | `cosmos_session.py` + `cosmos_context.py` (session lifecycle). **CLI Kernel**, not `serve` restart | Additive fields. Old `/1` still injects. Tests in `tests/test_session.py` gain `/2` round-trip + negative MAC |
| **Slice-3** SUBTRACT | BUCm narrative → pointer-only; `[read_order]` includes SEED; demote `BRAIN_BU_MD` from “state of record” | `cosmos_brain.py` (voice). Not required to ship Slice-1 | Collapses a competing handoff (H12) |
| **Slice-4** gate | runtime-binding harness that **quotes** the live tuple in §10 | no | proves the wish |

`AUTO_RESUME_GRACE_S = 15` lives as a named constant (satellite + tests), not a magic number in BUCm prose.

Keith still does: credentials (`grok login` / Claude `/login`), money, **operator HOLD**, mesh/dissertation boundary. No bats. No stored password. Sleep/logout still unmounts `V:` (already ORCHESTRATION).

---

## 9. SUBTRACT — collapse competing carry-over

| duplicate | collapse to |
|---|---|
| BUCm `[tidyup]` / `[next].in_flight` / resume essays | SEED `facts` + `motif.route`. BUCm stays mounts/read_order/run pointer |
| `V:\Ai\BU.MD` as brain “STATE OF RECORD” | HMAC SEED facts head (Slice-3). BU.MD becomes archive, not authority |
| Proposed extra `HANDOFF.json` / second seed schema file | **Do not build.** `SEED.json` + sidecar is the one manifest |
| Vendor transcripts as resume source | Overflow crash-continue only; never the engine |
| `RESESSION.json` as authority | Projection of pid/session/seed_sha. SEED + ledger win |
| Dual MOTIF droppers (WD2 15s + motif-driver 15m) | **Out of scope to merge this wish**, but both must honor PAUSE and `is_advancing` so auto-resession does not amplify double-drops. Do not add a third dropper |
| Satellite writing its own pause primitive | Reuse `PAUSE.flag` |
| Compaction-as-resession | Rejected (research §1.5) |

Net: **one SEED, one pause flag, one cow lease, one satellite, one prompt file.** Capability up, stores down (P8).

---

## 10. Stage-6 RUNTIME-BINDING proof

MOTIF_TRACKER numbering: stage 6 = the gate. (`docs/MOTIF.md` puts the same gate after stage-8 ITERATE; `docs/COSMOS_PIPELINE.md` calls it stage-7 COMPARE. This wish binds the **tracker** stage-6, as the assignment asked.)

**`rc=0`, a green log, a heartbeat `ok`, or `py_compile` is not the gate.** (`docs/COSMOS_PIPELINE.md`: *a field only the new tree can emit*; `docs/SCAR_PLACATION.md`: *quote the artifact, never the intention*.)

### 10.1 The value only a genuine auto-resume can emit

After an unattended watermark (or quiet) fire, **all** of the following must be **quoted** from disk, and they must **agree**:

1. **`live/state/SEED.decl.json` `sha`** of the bytes `start_session` just verified (MAC matched this install’s key; `tree_id=KMesh-COSMOS-live`).
2. **`live/state/SEED.json` `motif.cursor`** (or `/1` fallback `facts.motif_cursor`) — the signed position.
3. **`live/state/control/RESESSION.json`:**
   - `spawn_reason` ∈ {`watermark`,`quiet`} (not `null`, not a human KDash click);
   - `seed_sha` **equals** (1);
   - `seed_sid` **equals** `SEED.json sid`;
   - `resumed_from.slug` + `resumed_from.stage` **equal** (2);
   - `vendor_session_id` is **non-null** and **≠** `prev_vendor_session_id` (H1 fresh window — `--continue` cannot produce this);
   - `state=SPAWNED`.
4. **Authority ledger** `SESSION_SEED_INJECTED` payload: `sid`, `path` ending in `SEED.json`, `facts` containing `motif_cursor` matching (2). Event after the spawn’s `SESSION_SEED_WRITTEN`.
5. **WD2** `live/logs/WATCHDOG2.log` line `AUTO-RESUME (resume_gate)` whose `auto_resume_at` **equals** the ISO the satellite wrote on `PAUSE.flag` (or the heartbeat extra `auto_resume_at` from the PAUSED ticks immediately before). After that line, a heartbeat with `tick=scan` / not `state=PAUSED`.
6. **A route artifact after `spawned_at`:** a new `<!-- watchdog2-tick -->` or DHx line (`docs/AGENT_BRIEF.md`) whose token is the **next** stage of `resumed_from` (or a P5 re-drop of a `JOB_STALE` row), **without** a human prompt in `RESESSION.json`.

The **tuple** `(seed_sha, resumed_from, vendor_session_id ≠ prev, SESSION_SEED_INJECTED.sid)` is structurally impossible for:

- the pre-satellite tree (no `RESESSION.json` `resumed_from`, no satellite spawn);
- a `--continue` of the old vendor session (`vendor_session_id` would match `prev`);
- a placating green log (`seed_sha` would not equal the HMAC sidecar of the SEED that `start_session` injected);
- a resume that ignored the SEED and guessed the tracker (signed `motif.cursor` would not match `resumed_from` unless they actually read it).

**Procedure (unattended):** with Core `:8770` **left up**, operator HOLD **absent**, BACKLOG/MOTIF still open: either wait out W1 or run the satellite `--once` after a synthetic heartbeat that crosses the watermark. Do **not** click BootUP. Quote the six artifacts. If any field is missing or disagrees, the gate is **not** passed — report the contradiction first (SCAR_PLACATION).

### 10.2 Negative controls (a gate tested only in the passing direction is a gate nobody has seen closed)

`tests/test_session.py` already has negative MAC/identity cases. Add:

- forged SEED + matching sidecar `len`/`sha` but wrong `mac` → satellite `REFUSED`/`BAD_SEED`, **no** new `vendor_session_id`;
- operator HOLD → `state=HOLD`, flag still present after `auto_resume_at` would have passed;
- live `motif_token` in runner ledger → new session does not submit a second file of that name;
- `--continue` path (if overflow is even present) must **not** be able to satisfy `vendor_session_id ≠ prev` in the gate tuple — the gate **requires** inequality.

---

## 11. Honest limits (Keith surface)

- Cowork tab **will not** reopen itself. The route continues on CLI. Keith opens Cowork when he wants that UI (research §1.7, §4).
- Folder grants in Cowork still do not persist; CLI `--add-dir` / `--cwd` is the unattended mount.
- 5-hour / weekly seat windows and prepaid wallets can still run out (R7). That is a named refusal, not a silent stall.
- Sleep / logout unmounts `V:`. Logged-on only.
- Numeric vendor context windows are **UNKNOWN** until Slice-4 probe; W1 carries the wish until a quoted field exists (do not fabricate a token ceiling).
- Live tree this pass is **not** auto-resuming: `PAUSE.flag` is operator-shaped TidyUP **hold** with no `auto_resume_at`, and SEED is thin. Slice-1’s H10 promotion of *TidyUP-handoff* hold → `resume_gate` is what unsticks that **without** treating a Keith stop as fuel.

---

## 12. Stage-3 / stage-4 brief (for the next MOTIF stop)

Critics (different family) judge this file against the rubric and against `docs/research/AUTO_RESESSION.md` — *is this the thing we decided*, not *is this good prose*. Contested items worth naming now rather than hiding:

- **Grace = 15s** is an invention where canon said only `grace`. Soft S4; changeable without re-litigating H1–H12.
- **Satellite as the P3 arming writer** (vs waiting for the spawned LLM to rewrite `PAUSE.flag`) is the keep-her-afloat choice: flipping JSON is not a sparse model decision.
- **`resource="cow"`** vs a file lock on `RESESSION.json`: AD-2 already killed advisory file locks as authority; use the arbiter.

Build order after consensus: Slice-1 (satellite + arming + spawn) → Slice-2 (thick SEED) → Slice-4 gate on the live tree with Core still up → Slice-3 subtract (BUCm / BU.MD) so the one-truth collapse is **measured**, not a preface.

No fabricated compliance: nothing in this document claims the satellite exists, that `resume_gate` is armed on the live flag, or that the live SEED can resume a MOTIF cursor. Those are the holes Slice-1/2 close. The proof is the tuple in §10.1, quoted from the live tree after an unattended fire.
