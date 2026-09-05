# AUTO-RESESSION — DESIGN (buildable, bound to file:line, with the patch)

**Stage:** MOTIF design pass, consuming stage-1 RESEARCH (`docs/research/AUTO_RESESSION.md`,
G46, 2026-08-26) and stage-2 ARCH (`docs/arch/AUTO_RESESSION_ARCH.md`, G46, filed).
**Author:** Claude Code coder agent, native on the live tree, 2026-08-30.
**Fence:** this agent wrote only `builds/probe/` and `docs/research/`. Everything under
`cosmos/` and `docs/arch/` in section 6 is a **PROPOSAL for COW** (P10) — not applied.
**Measured, not asserted:** every claim below that says MEASURED carries the command and the
value it emitted this shift. Where a thing could not be measured it says **UNMEASURED** and
says why. Nothing here claims the satellite is running.

---

## 0. What this document adds

The research named the hole. The arch named the shape. **Neither is buildable as written**, for
three measured reasons, and all three are fixed here:

| # | Arch as filed | Measured reality | This design |
|---|---|---|---|
| A1 | `CLOCKS` **id 17** for the satellite (`docs/arch/AUTO_RESESSION_ARCH.md:79,294,470`) | id 17 is **taken** by *COSMOS Work-Order Runner* (`cosmos/cosmos_own_clocks.py:164`) | **id 18** |
| A2 | Spawn recipe passes `--single "<prompt>"` **and** `--prompt-file …` (`AUTO_RESESSION_ARCH.md:363`) | Passing the prompt twice is undefined on both rails; `--no-auto-update` is **not in this binary's `--help`** (research §2.1) | Satellite **reads** the prompt file and passes its bytes once via the proven `--single` / `-p`; `prompt_sha` binds which bytes |
| A3 | "Capture `sessionId` / `session_id`" from the spawn's JSON | Capturing stdout means **holding the orchestrator's pipe for its whole life** — the one thing a detached satellite must not do | **Mint** the id (`--session-id`, new-conversation only on both rails) and prove freshness from the **vendor-written transcript**, which a minted uuid alone cannot fake |

Plus one layering fix: the arch puts the thick-SEED packer **inside** `close_session`, which
would drag `cosmos_motif_driver` into the session lifecycle. This design keeps the packer in the
satellite and gives `close_session` one optional `extra` dict — smaller, and core stays ignorant
of MOTIF.

---

## 1. What already exists — do not redesign it

All MEASURED by host-side read this shift.

| Built | Where | What it already does |
|---|---|---|
| Signed carry-over write | `cosmos/cosmos_session.py:205` `close_session` → `:273` `_write_seed` | Validates control files, closes the open session (or reconstructs it from the ledger, `:225`), writes `state/SEED.json` + `SEED.decl.json` (len/sha/**HMAC**), archives the previous seed under `state/seeds/` without unlinking (`:281-287`), appends `SESSION_SEED_WRITTEN` (`:266`) |
| Signed carry-over read | `cosmos/cosmos_session.py:298` `start_session` | INTEGRITY (`read_verified`, `:330`) → AUTHENTICITY (install-key HMAC, `:357-368`) → IDENTITY (`tree_id` vs sentinel, `:373-379`) → inject facts/watchers → `SESSION_SEED_INJECTED` (`:399`). Typed refusals `NO_SEED` / `BAD_SEED` / `IDENTITY_MISMATCH` (`:49`) |
| Resume gate (P3) | `cosmos/cosmos_watchdog2.py:475` `maybe_auto_resume`, driven at `:917` | `mode=hold` never self-clears (`:486`); `mode=resume_gate` unlinks `PAUSE.flag` at `auto_resume_at` (`:502`) and logs `AUTO-RESUME (resume_gate)` (`:508`); unparseable timestamp **stays paused** (`:494`) |
| Paused ≠ dead | `cosmos/cosmos_watchdog2.py:919-951` | Heartbeat keeps writing with `state=PAUSED`, mode, reason, `auto_resume_at` |
| One-orchestrator primitive | `cosmos/cosmos_lock.py:330` `Arbiter.acquire`, wired at `cosmos/cosmos_kernel.py:86` | Monotonic fencing tokens, `HELD` refusal, expiry→TAKEOVER, HMAC-signed lease ledger |
| Proven spawn flag sets | `cosmos/cosmos_dispatch.py:1031` (grok), `:1239` (claude); shared builder `cosmos/cosmos_work_order.py:345` | `grok --single … --always-approve --max-turns 60 --cwd`; `claude -p … --permission-mode dontAsk --add-dir` |
| Satellite scaffolding | `cosmos/cosmos_clock.py:99` `acquire_lock`, `:125` `tr_cmdline`, `:180` `create_task`, `:191` `harden_task`, `:292` `spawn_detached`, `:301` `wait_fresh`, `:39` `write_heartbeat` | Everything a new clock needs. **No new clock plumbing is being written.** |
| CLI kernel entry | `cosmos/cosmos.py:131-141` | `cosmos.py session close --handoff … ` / `session start <stream>` — the satellite's TidyUP and BootUP hands |
| The gate harness | `builds/selftest_clock/cosmos_selftest_clock.py:89-96` | Globs `tests/test_*.py` **and** `builds/*/test_*.py`; one retry distinguishes FAIL from FLAKY (`:104-110`) |

**Layer A already survives an orchestrator death.** Core `:8770`, WD2, runner, collector, and
the motif driver are Windows tasks and detached daemons; they are not inside a context window.
Auto-resession is **only** about Layer B.

---

## 2. The mechanism, exactly

```
  W1/W2 watermark (PID STILL ALIVE)            W3 quiet backstop (PID gone)
              │                                            │
              ▼                                            ▼
     ┌──────────────────────────────────────────────────────────┐
     │ 1  classify PAUSE.flag      HOLD ─────────────► REFUSED   │  operator hold is sacred
     │ 2  pre-check SEED bytes     bad ──────────────► REFUSED   │  never spawn around a lie
     │ 3  prompt file present      missing ──────────► REFUSED   │  no prompt invented at fire time
     │ 4  arbiter.acquire("cow")   HELD ─────────────► REFUSED   │  exactly one orchestrator
     │ 5  cosmos.py session close --handoff Cm  (+extra packer)  │  TidyUP: the SIGNED manifest
     │ 6  arm PAUSE.flag mode=resume_gate auto_resume_at=+15s    │  P3 — the missing production writer
     │ 7  mint uuid; spawn_detached FRESH vendor session         │  never --continue
     │ 8  write RESESSION.json projection + heartbeat            │  a refusal that only stops is forbidden
     └──────────────────────────────────────────────────────────┘
              │
              ▼
     new COW runs `cosmos.py session start Cm`  →  SESSION_SEED_INJECTED
     WD2 unlinks the flag at auto_resume_at     →  AUTO-RESUME (resume_gate)
     the route moves with no human turn
```

**Order is the design.** Steps 1–4 are all refusals and they run *before* anything is written,
so a satellite tick that fails is a tick that changed nothing. This ordering is gated:
`builds/probe/test_resession.py` proves an operator HOLD wins over a fired watermark *and* a
good seed, and that a fired watermark over a `BAD_SEED` is `REFUSED`, not resumed.

### 2.1 Why the watermark, not the crash

`--continue` / `--resume` / `--fork-session` all reopen **the same transcript** (research §1.2,
§1.5): continuing a full window reloads the full window. "Prompt is too long" and "process gone"
are both *after* the bite. So the trigger fires while the current window still has room:

| detector | fires on | role |
|---|---|---|
| **W1** age ≥ `SESSION_AGE_WATERMARK_S` (2700s) or turns ≥ `TURN_WATERMARK` (40) | live PID | **the engine.** 40 of the dispatch cap of 60 (`cosmos_dispatch.py:1032`) leaves 20 turns of TidyUP budget |
| **W2** `context_pct ≥ 0.70` | live PID, **only if the rail actually reports it** | best-effort. **UNMEASURED** — no vendor field is bound yet; W2 is a no-op until one is, and W1 carries the wish |
| **W3** PID dead, or `last_act_epoch` older than 180s | dead/silent PID | **backstop only**, labelled `spawn_reason=quiet` so a self-heal is never mistaken for the engine |

The satellite never scrapes a UI and never parses vendor transcripts. Format instability is
explicit in the research (§1.3); this design touches transcript files **only** as
existence + mtime.

### 2.2 Why the vendor session id is minted

Both rails accept a caller-supplied id for a **new** conversation (`claude --session-id <uuid>`;
`grok --session-id <UUID>`, new-only — research §1.1, §2.1). Minting removes the need to hold
the spawned orchestrator's stdout for its entire life, which is incompatible with a detached
satellite. A minted uuid proves nothing on its own, so **the gate does not accept it alone**:
it additionally requires the transcript **the vendor binary writes** for that id to exist and
to be newer than `spawned_at` (`transcript_path()`; paths measured on this machine in research
§1.3 / §2.1). That pair — an id COSMOS chose, in a file only the vendor can create — is the
fresh-window proof, and `--continue` structurally cannot produce it.

---

## 3. The state it must carry

Three stores, each with one job. **No fourth store, no second seed format** (P8).

### 3.1 `state/SEED.json` — the authority (signed)

Today `/1`: `facts, watchers, handoff, incidents, sid, closed_epoch, tree_id, kind, schema`.
MEASURED live this shift — `facts={}`, `sid="inherit"`, `sha=51373295…`, so **it cannot name a
route position**. `/2` adds, additively:

| key | source (all on disk, never COW's memory) |
|---|---|
| `motif: {cursor:{slug,stage}, route:[…]}` | `cosmos_motif_driver.parse_tracker` (`:193`) + `effective_stage` (`:238`) over `docs/MOTIF_TRACKER.md` |
| `inflight: [tokens]` | `ledger_inflight` (`:319`) ∪ `inflight_filenames` (`:277`) ∪ `state/watchdog2/assigned.json` |
| `leases: [{resource,holder,token,granted_at,expires_at}]` | `Arbiter.status` (`cosmos_lock.py:562`) — AD-10 names active leases and the writer has never carried them |
| `stream`, `auto_resume_at`, `pause_mode` | the satellite's own arming act |
| `facts.motif_cursor = "<slug>@<stage>"` | duplicated into `facts` so the **existing** `/1` inject path (`cosmos_session.py:385`) carries the cursor even before any reader is taught `/2`. One mechanism, two views — not two stores |

The `/2` cursor lives on the seed object, not as one giant fact: `FACT_RECORDED` truncates
values, and `slug@stage` stays well under any cap.

### 3.2 `state/control/RESESSION.json` — a projection, never authority

`{schema, tree_id, state, spawn_reason, rail, pid, vendor_session_id, prev_vendor_session_id,
spawned_at, prompt_sha, seed_sha, seed_sid, seed_schema, seed_thin, resumed_from, cow_token,
refused_kind, refused_detail, detectors, why}`.

If it ever disagrees with the SEED, **the SEED wins** and the projection is rewritten. Its only
irreplaceable job is holding `prev_vendor_session_id` across the boundary so the gate can assert
inequality.

### 3.3 `state/control/COW_HEARTBEAT.json` — liveness, not position

`{schema, tree_id, pid, rail, vendor_session_id, spawned_at_epoch, last_act_epoch, turn_n,
context_pct?, motif_cursor}`. Written by the live COW each synthesis cycle and by the satellite
at spawn. **A missing heartbeat is a signal, never a resume source** — this is exactly what the
live tree reports today (§5, M5).

---

## 4. Failure modes — each one typed, each one visible

`ResessionRefusal.kind` is machine-readable and every kind heartbeats. PAUSE_PROTOCOL's rule
governs: *a check that never ran is indistinguishable from one that passed*, so a refused
resession that merely stops is forbidden.

| condition | kind | satellite does | gated by |
|---|---|---|---|
| Operator `mode=hold` (Keith stops, mesh/dissertation boundary) | `HOLD` | never rewrites the flag, never spawns | `test_resession.py` — HOLD beats a fired watermark + good seed |
| Unrecognised `mode` value | `HOLD` | fail-closed to hold | ✓ |
| `mode=resume_gate` already armed | — | leaves it; WD2 owns clearing it | ✓ |
| No `SEED.json` | `NO_SEED` | ledger `OPEN_CONTEXT`, **no invented seed**, no spawn | ✓ |
| No `SEED.decl.json` | `NO_DECL` | refuse | ✓ |
| len or sha mismatch, or sidecar with no MAC | `BAD_SEED` | refuse — never `--continue` around a bad manifest | ✓ (3 cases) |
| `tree_id` ≠ sentinel | `IDENTITY_MISMATCH` | refuse — another tree's carry-over is not a resume | ✓ |
| `/2` body missing `motif`/`leases`/`inflight` | `BAD_SEED` | refuse (corrupt shape ≠ thin) | ✓ |
| `/1` MAC-valid, `facts={}` | `SEED_THIN` (**not** a refusal) | spawn allowed, ledger `SESSION_SEED_THIN`, cursor from the tracker | ✓ |
| Missing `docs/AUTO_RESESSION_PROMPT.md` | `NO_PROMPT` | refuse rather than invent a BootUP prompt at fire time | ✓ |
| `cow` lease held | `HELD` | no second orchestrator | ✓ |
| `close_session` refuses (`CONTROL_INVALID`, unresolved watchers) | `CLOSE_REFUSED` | no spawn; surface the kind | UNMEASURED (needs a live kernel; deferred to Slice-4) |
| Unknown rail | `NO_RAIL` | typed refusal, not a silent default | ✓ |

**Corrupt is not thin.** Thin is a packing bug to surface and fix at the next close. Corrupt is
a lie. Absence is `NO_SEED` (loud). MAC failure is `BAD_SEED` (loud). Both refuse; neither
degrades into "resume from BACKLOG and hope".

Two more, named because they are real and not designed away:

- **Wallet / seat exhaustion.** A prepaid Grok wallet or a Claude seat window can run out
  mid-spawn. That is a named refusal in `RESESSION.json`, not a silent stall. Keith owns money
  and credentials; the satellite never touches either.
- **Sleep / logout unmounts `V:`.** Logged-on only, no `ONSTART`, no stored password. The clock
  stops with the session and self-heals on logon.

---

## 5. What is MISSING today — bound to file:line, MEASURED

| # | Missing | Binding | How measured |
|---|---|---|---|
| **M1** | The satellite itself. No `cosmos/cosmos_resession.py` | — | `ls cosmos/` — absent |
| **M2** | **No production writer of `mode=resume_gate`.** `cosmos_watchdog2.py:486` *reads* it; every other hit is a reader or a test | `cosmos_watchdog2.py:486`, `cosmos_bucket_daemon.py:219`, `cosmos_node_bucket_worker.py:208`, `cosmos_principles.py:110` | `grep -rn resume_gate --include=*.py cosmos/` — 20 hits, **zero writers** |
| **M3** | The SEED cannot carry a route position: the seed dict has no `motif`/`inflight`/`leases` | `cosmos/cosmos_session.py:254-264` | probe dry-run: `seed_thin=true`, `seed_sid="inherit"`, `resumed_from=null` |
| **M4** | AD-10 names *active leases*; `Session` has only `_facts` and `_watchers` | `cosmos/cosmos_context.py:32-33` | host read |
| **M5** | No `COW_HEARTBEAT.json` — so **W1/W2, the engine, cannot fire at all today**; only the W3 backstop could | `live/state/control/` holds `PAUSE.flag` only | probe dry-run: `"why": "no COW heartbeat"` |
| **M6** | No `docs/AUTO_RESESSION_PROMPT.md` | referenced by `AUTO_RESESSION_ARCH.md:363,470` | probe dry-run: `prompt_sha: null` |
| **M7** | No `CLOCKS` row for resession; the arch's id 17 is **taken** | `cosmos/cosmos_own_clocks.py:164-172` | host read |
| **M8** | `start_session` **hard-equals** `/1`, so a `/2` writer landing first would brick BootUP | `cosmos/cosmos_session.py:341` | host read — **this fixes the patch order: reader before writer** |
| **M9** | No `resource="cow"` lease anywhere | `cosmos_lock.Arbiter` exists; nothing acquires `"cow"` | `grep -rn '"cow"' --include=*.py cosmos/` — no hits |
| **M10** | Live `PAUSE.flag` carries `mode="resumed"` — a **third** mode value the protocol does not define (`hold` / `resume_gate`) | `docs/PAUSE_PROTOCOL.md:43-47` vs the live flag | host read. `state=RUNNING` so nothing is currently gated on it, but `classify_pause` fails it closed to HOLD on purpose |

---

## 6. The patch — PROPOSAL for COW (`cosmos/` is outside this agent's fence)

**Nothing below was applied.** Slices are ordered so the tree stays green at every step.

### Slice-1 — the satellite (no core edit)

**P1.1 — new file `cosmos/cosmos_resession.py`.** Take `builds/probe/cosmos_resession.py`
**verbatim**; the only edit is deleting the final `PROBE NOTE:` paragraph of the module
docstring. The `--repo` default (`Path(__file__).resolve().parent.parent`) resolves correctly
from `cosmos/`; no code change is needed. Measured in the probe location:
`--selftest` → `ok 12/12`; `--once --dry-run` against the live tree → the JSON in §7.

**P1.2 — new file `builds/probe/test_resession.py`** already written by this agent inside its
fence, and already counted by the gate (`cosmos_selftest_clock.py:93`). If COW moves the module
to `cosmos/`, move this suite to `tests/test_resession.py` and change its import.

**P1.3 — new file `docs/AUTO_RESESSION_PROMPT.md`** (tracked, hashed into `prompt_sha`):

```markdown
# AUTO-RESESSION BootUP prompt (read by cosmos_resession; do not edit at fire time)

You are COW for the COSMOS `Cm` stream, spawned by the auto-resession satellite. There is
no human in this turn. Read, in the order given by `BUCm.toml [read_order]`:
BUCm.toml -> CLAUDE.md -> docs/FINAL_ARCHITECTURE.md -> docs/COSMOS_PIPELINE.md.
Then run `py -3.14 cosmos\cosmos.py session start Cm --root <live>` and quote the inherit
it returns; that verified SEED, not this file and not any vendor memory, is your carry-over.
Then read docs/BACKLOG.md, docs/MOTIF_TRACKER.md, docs/AGENT_BRIEF.md and the collector index.

Resume at `RESESSION.json.resumed_from`, never earlier: take
`max(SEED cursor stage, tracker effective_stage)`. Do not re-dispatch any token in
`SEED.inflight` or live in the runner ledger. Your first act is to reconcile DHx against the
collector index and re-drop only rows that are JOB_STALE or never returned.

You are the ORCHESTRATOR (P9): drop work in the box, do not run searches in your own context.
Agents propose; you dispose (P10). Never rewrite an operator HOLD. Report with artifacts, never
with intentions.
```

**P1.4 — register the clock.** `cosmos/cosmos_own_clocks.py`, id **18** (17 is taken):

```diff
--- a/cosmos/cosmos_own_clocks.py
+++ b/cosmos/cosmos_own_clocks.py
@@
         "heartbeat": "work_order_runner_heartbeat.json",
         "standup": "work_order",
     },
+    {
+        "id": 18, "clock": "COSMOS Resession",
+        "cadence": "15s loop / 1-min self-heal",
+        "script": "cosmos_resession.py",
+        "task": "COSMOS Resession",
+        "logon": "COSMOS Resession Logon",
+        "vehicle": "detached daemon + 1-min self-heal + onlogon",
+        "heartbeat": "resession_heartbeat.json",
+        "standup": "resession",
+    },
 )
```

A separate satellite, not a WD2 branch: a hung spawn must never stall the 15s retask clock.

### Slice-2 — thicken the SEED (core-adjacent, additive, **reader first**)

`start_session` hard-equals `/1` at `cosmos_session.py:341` (M8), so the **reader must land
before any `/2` is ever written** or BootUP bricks. Both hunks are in one patch, reader first.

```diff
--- a/cosmos/cosmos_session.py
+++ b/cosmos/cosmos_session.py
@@
 SEED_SCHEMA = "cosmos-session-seed/1"
+SEED_SCHEMA_V2 = "cosmos-session-seed/2"
+# The reader accepts both. A bump that refused /1 would refuse the live seed and
+# brick BootUP - keep-her-afloat is a property of the patch, not just the design.
+SEED_SCHEMAS = (SEED_SCHEMA, SEED_SCHEMA_V2)
+# Keys a /2 seed carries beyond /1. The satellite packs them from DISK sources
+# (tracker, lease projection, runner ledger); cosmos_session stays ignorant of
+# MOTIF so the session lifecycle does not grow a dependency on a satellite.
+SEED_V2_KEYS = ("motif", "leases", "inflight")
@@
-    def _seed_mac(self, tree_id: str, payload: bytes) -> str:
+    def _seed_mac(self, schema: str, tree_id: str, payload: bytes) -> str:
@@
-        material = (SEED_SCHEMA.encode("utf-8") + b"\x00"
+        material = (str(schema).encode("utf-8") + b"\x00"
                     + str(tree_id).encode("utf-8") + b"\x00" + payload)
         return hmac.new(self._install_key(), material, hashlib.sha256).hexdigest()
@@
-    def close_session(self, handoff_to: str = "next", force: bool = False) -> Path:
+    def close_session(self, handoff_to: str = "next", force: bool = False,
+                      extra: dict | None = None) -> Path:
@@
         seed = {
-            "schema": SEED_SCHEMA,
+            "schema": SEED_SCHEMA_V2 if extra else SEED_SCHEMA,
             "kind": "COSMOS_SEED",
@@
             "tree_id": self.k.paths.sentinel.tree_id,
         }
+        if extra:
+            # Additive only: a packer may add route state, never overwrite the
+            # facts/watchers/incidents this method just proved.
+            missing = [k for k in SEED_V2_KEYS if k not in extra]
+            if missing:
+                raise SessionError(
+                    "BAD_SEED",
+                    f"/2 packer omitted {missing} - a /2 seed that cannot name its "
+                    f"route is corrupt, not thin")
+            for key, value in extra.items():
+                if key not in seed:
+                    seed[key] = value
+            if isinstance(extra.get("facts"), dict):
+                seed["facts"].update(extra["facts"])
         path = self._write_seed(seed, sid)
@@
         decl = write_declared(path, payload)
         write_declared(
             decl_path,
             json.dumps({"len": decl["len"], "sha": decl["sha"],
-                        "schema": SEED_SCHEMA,
-                        "mac": self._seed_mac(seed.get("tree_id", ""), payload)},
+                        "schema": seed.get("schema", SEED_SCHEMA),
+                        "mac": self._seed_mac(seed.get("schema", SEED_SCHEMA),
+                                              seed.get("tree_id", ""), payload)},
                        indent=1, sort_keys=True).encode("utf-8"))
@@
         if (not isinstance(seed, dict)
-                or seed.get("schema") != SEED_SCHEMA
+                or seed.get("schema") not in SEED_SCHEMAS
                 or seed.get("kind") != "COSMOS_SEED"
                 or not isinstance(seed.get("facts"), dict)):
@@
+        if seed.get("schema") == SEED_SCHEMA_V2:
+            absent = [k for k in SEED_V2_KEYS if k not in seed]
+            if absent:
+                raise SessionError(
+                    "BAD_SEED",
+                    f"{seed_path} declares /2 but omits {absent} - corrupt shape, "
+                    f"which is not the same failure as a thin /1 seed")
@@
-        want = self._seed_mac(seed.get("tree_id", ""), raw)
+        want = self._seed_mac(seed.get("schema", SEED_SCHEMA),
+                              seed.get("tree_id", ""), raw)
@@
-def close_session(kernel, handoff_to: str = "next", force: bool = False) -> Path:
+def close_session(kernel, handoff_to: str = "next", force: bool = False,
+                  extra: dict | None = None) -> Path:
     """Module-level TidyUP: validate controls, write seed, return its path."""
-    return kernel.sessions.close_session(handoff_to=handoff_to, force=force)
+    return kernel.sessions.close_session(handoff_to=handoff_to, force=force,
+                                         extra=extra)
```

**Backward-compatibility, checked against the existing gate, not assumed:** `tests/test_session.py`
imports `SEED_SCHEMA` (`:21`) and asserts the written body equals it (`:96`) — with no `extra`
passed, `close_session` still writes `/1`, so that holds. `:196` builds an alien MAC from
`SEED_SCHEMA`; for a `/1` body the new `_seed_mac` material is byte-identical, so that holds too.
`cosmos.py:136` calls `close_session(handoff_to=…, force=…)` by keyword and is unaffected.
**UNMEASURED:** this patch was not applied, so the suite was not run against it — that is
Slice-2's own gate, not a claim made here.

### Slice-3 — SUBTRACT (do not skip; improvement is not bloat)

- `BUCm.toml`'s `[tidyup]` / `[next].in_flight` narrative → SEED `facts` + `motif.route`. BUCm
  keeps `[meta]`, `[read_order]`, `[mounts]`, `[run]`, `[hazards]` and becomes a pointer again.
- `BUCm.toml [read_order]` **gains `live/state/SEED.json`** — canon calls the SEED the carry-over
  and the read list does not name it.
- `cosmos_brain.BRAIN_BU_MD` (`V:\Ai\BU.MD`, commented *STATE OF RECORD*) is a competing handoff.
  Demote to archive; the voice brain reads the HMAC SEED facts head.
- Reconcile `docs/PAUSE_PROTOCOL.md:43-47` with the live flag's `mode="resumed"` (M10): either
  define a third mode or stop writing one.

Net after all three slices: **one seed, one pause flag, one cow lease, one satellite, one prompt
file** — capability up, stores down.

---

## 7. The runtime-binding gate — what would prove it works

`rc=0` is not the gate. A green log is not the gate. A heartbeat that says `ok` is not the gate.
The gate is **a value only a genuine unattended auto-resume can emit.**

**Procedure.** Core `:8770` left **up**; operator HOLD **absent**; BACKLOG/MOTIF still open. Let
W1 fire naturally, or write a `COW_HEARTBEAT.json` whose `spawned_at_epoch` crosses the
watermark and run the satellite `--once`. **Do not click BootUP. Do not type a prompt.** Then
quote all seven, from disk, and they must agree:

1. `live/state/SEED.decl.json` `sha` — the bytes `start_session` verified.
2. `live/state/SEED.json` `motif.cursor` (or `/1` fallback `facts.motif_cursor`) — the **signed** position.
3. `live/state/control/RESESSION.json`: `state=SPAWNED`; `spawn_reason ∈ {watermark, quiet}`;
   `seed_sha` **=** (1); `seed_sid` **=** SEED `sid`; `resumed_from` **=** (2);
   `vendor_session_id` non-null and **≠** `prev_vendor_session_id`.
4. **The vendor-written transcript** at `transcript_path(rail, cwd, vendor_session_id, home)`
   exists with mtime **>** `spawned_at`. *This is the row the arch did not have* — it is the only
   artifact in the tuple that the satellite cannot write, and it is what stops a minted uuid from
   standing in for a real spawn.
5. Authority ledger `SESSION_SEED_INJECTED`: `sid` matching, `path` ending `SEED.json`, `facts`
   containing `motif_cursor` equal to (2), appended **after** the spawn's `SESSION_SEED_WRITTEN`.
6. `live/logs/WATCHDOG2.log` line `AUTO-RESUME (resume_gate)` whose `auto_resume_at` equals the
   ISO the satellite wrote, followed by a heartbeat that is no longer `state=PAUSED`.
7. A route artifact **after** `spawned_at` — a new `docs/AGENT_BRIEF.md` DHx line or watchdog2
   tick whose token is the **next** stage of `resumed_from`.

**Why the tuple cannot be faked.** The pre-satellite tree has no `RESESSION.json` at all. A
`--continue` produces `vendor_session_id == prev`, failing (3). A placating green log cannot make
`seed_sha` equal the HMAC sidecar of the seed `start_session` actually injected, failing (1)+(5).
A resume that ignored the SEED and guessed from the tracker cannot make the **signed**
`motif.cursor` equal `resumed_from`, failing (2). And a satellite that wrote a projection without
spawning anything fails (4), because only the vendor binary writes that transcript.

**Negative controls (a gate tested only in the passing direction is a gate nobody has seen
closed).** Already gated in `builds/probe/test_resession.py`: forged-sha / forged-len / no-MAC /
wrong-tree seeds all refuse with no spawn; an operator HOLD stays HOLD with a fired watermark; a
held `cow` lease refuses the second orchestrator; no spawn argv may contain `--continue`,
`--resume`, `--fork-session`, `--bare`, or `--restore-code`.

### Gate status this shift — honest

| row | status |
|---|---|
| Refusal ordering, seed pre-check, argv rules, arming semantics | **MEASURED PASS** — `builds/probe/test_resession.py` 32/32, and it is now inside the tree-wide selftest clock |
| Satellite decision core against the **live** tree | **MEASURED** — §8 output; correctly reports `IDLE`, thin seed, no COW heartbeat, no prompt |
| Rows 1–7 of the runtime-binding gate | **UNMEASURED, and deliberately not run.** Executing it means spawning an autonomous orchestrator with `--always-approve` / `dontAsk` on the live tree while three other agents are working it. That is the expensive-and-irreversible case: it is Keith's call and Slice-4's job, not this design pass's |
| `grok --help` re-verification of `--session-id` / `--prompt-file` | **UNMEASURED** — running the binary was denied in this session. The flags are bound to research §2.1's measured `--help` (2026-08-26), not re-measured today. §6 P1.1 should re-check before Slice-4 |
| W2 (`context_pct`) | **UNMEASURED** — no vendor field is bound. W2 is a documented no-op until a filled-session probe names one. W1 carries the wish |

---

## 8. Measured output, verbatim

`py -3.14 builds/probe/cosmos_resession.py --root V:/A/Ai/COSMOS/live --repo V:/A/Ai/COSMOS --once --dry-run`

```json
{
 "detectors": {"w1_age": false, "w1_turns": false, "w2_context": false,
               "w3_dead": false, "w3_quiet": false},
 "dry_run": true,
 "pause_class": "RUNNING",
 "projection_path": "V:\\A\\Ai\\COSMOS\\live\\state\\control\\RESESSION.json",
 "prompt_path": "V:\\A\\Ai\\COSMOS\\docs\\AUTO_RESESSION_PROMPT.md",
 "prompt_sha": null,
 "rail": "grok",
 "refused_detail": null,
 "refused_kind": null,
 "resumed_from": null,
 "schema": "cosmos-resession/1",
 "seed_schema": "cosmos-session-seed/1",
 "seed_sha": "51373295e6b5f2366a8c8aad124dec38dcd501bc76db3941f6942749cbd48a88",
 "seed_sid": "inherit",
 "seed_thin": true,
 "spawn_reason": null,
 "state": "IDLE",
 "tree_id": "KMesh-COSMOS-live",
 "ts": "2026-08-30T22:14:32-05:00",
 "why": "no COW heartbeat"
}
```

`seed_sha` is the live `SEED.decl.json` `sha` exactly — the pre-check is reading the real bytes,
not reporting a hope. `seed_thin: true` / `resumed_from: null` / `prompt_sha: null` /
`"why": "no COW heartbeat"` are M3, M5 and M6 stating themselves out of the live tree.

**Nothing was spawned, armed, or written to `live/`.** `--dry-run` is how this was measured.
