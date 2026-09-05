# Cursor lane — Motif STAGE-5 critique (G46)

**Reviewer:** G46 (Grok Build), dispatched `motif_cursor_s5` 2026-08-25T23:12:02.276012-05:00
(`lg/g46_grok_motif_cursor_s5_you_are_g46_grok_bui_ba559c0d__t1800.py`, this job).
**Question:** is the build the thing that was decided — not "is this good code."
**Spec (decided):** `docs/CURSOR_LANE.md` (stage-4 recap, G46) bound to
`docs/research/CURSOR_LANE.md` + `docs/research/CURSOR_CLOUD_AGENTS_API_v1.md`;
DHx Cursor-lane bullet (`docs/AGENT_BRIEF.md`); Dispatcher adapter surface
(`cosmos/cosmos_rails.py`); resolver (`cosmos_paths`); BACKLOG Kernel-attach
carve-out (`docs/BACKLOG.md` owed LIVE CORE).
**Build:** `cosmos/cosmos_cursor_rail.py`, `tests/test_cursor_rail.py`,
`live/config/cursor_rail.json`, `live/config/cursor_rail_probe.json`,
`live/state/cursor_rail/gate.jsonl`.
**Core:** `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service`
were not modified (`git diff --name-only` on those four is empty; HEAD `56fa423`).
`cosmos_cursor_rail.py` / `docs/CURSOR_LANE.md` / `tests/test_cursor_rail.py` are
untracked. Satellite only. Kernel attach remains BACKLOG — this review does not
close it and does not edit kernel.

**Family note (process, not a rail defect):** Motif stage 5 is a *different-family*
review. This job was dispatched to G46, who also wrote the module and
`docs/CURSOR_LANE.md`. The findings below are still spec-vs-build, bound to files
and to a live-tree read. They are not a second family's vote. COW still owes a
non-Grok-Build pass before any stage-6 claim.

`rc=0` on `--selftest` / `--gate` is not complete. Stage 6 is a value only the
live *production* tree can emit *for the decided behavior* (Kernel-composed
`cursor-api` on the authority path, or an explicit refusal that the slice cannot
get there). A satellite `--gate PASS` while `kernel_attached: false` is a probe
of the key, not Motif stage 6. Tracker: nothing has passed stage 6.

---

## Verdict

**Partly — the adapter is the decided Cloud Agents rail. It is not yet the
decided identity-bound, production-composed lane, and the route it registers is
the wrong job.**

The build *is* a COSMOS-native `CursorRail` (`link_id=cursor-api`) that:

- reads the runtime-root key via `cosmos_paths` (`config/cursor_cosmos_key.txt`),
  never hard-codes it, never imports `bts_cursor`;
- `probe()` = cheap `GET /v1/me` (Bearer);
- `dispatch()` = opt-in `POST /v1/agents` + poll `GET /v1/agents/{id}/runs/{runId}`;
- `register_cursor_rail` claims + attaches the probe (missing key → still
  registered, probe `UNREACHABLE`);
- `--gate` composes an *isolated* Registry+Dispatcher under
  `live/state/cursor_rail/` and writes a live `/v1/me` identity to
  `live/config/cursor_rail_probe.json`;
- does not write `live/ledger/authority.jsonl`;
- does not edit kernel / ledger / sched / service.

That matches the *shape* of `docs/CURSOR_LANE.md` §§1–2.

It is **not** fully the decided *function*:

1. The spec's own identity (`apiKeyName=Cursor COSMOS 2`, never BTS) is quoted
   in the proof file but **not** the `--gate` PASS predicate. A BTS key in the
   same path would also PASS.
2. `--launch` exit status is the probe gate, not whether a Cloud Agent launched.
3. The rail is registered `core→models` at `policy_rank=0` with
   `autoCreatePR=true` on every `dispatch()`. Research/DHx decided a *coding*
   Cloud Agent launch (quota, GitHub branch, PR). `sgh-api`/`gem-api`/`gw-api`/
   `oa-api` are *model asks*. Collapsing those onto one Dispatcher route is the
   wrong thing relative to the research table the spec claims not to re-open.
4. `attach_to_kernel` on a writing Kernel appends `LINK_REGISTERED` to the
   *authority* ledger with an in-memory probe — the dangling-claim pattern the
   spec itself forbids — and Kernel boot still does not reattach.

Until HIGH defects close, this row stays DRAFT at stage 5. Do not treat
`live/config/cursor_rail_probe.json` `gate=PASS` as Motif stage 6. Kernel attach
stays BACKLOG.

---

## What was decided (the contract this review uses)

From `docs/CURSOR_LANE.md` §1 (bound to research, "not re-opened"):

1. COSMOS's own key, never BTS (`Cursor BTS` / `Cursor BTS 2`). Key file
   `live/config/cursor_cosmos_key.txt`.
2. Auth: Bearer (proven) or Basic `key:`.
3. Probe = `GET /v1/me` (cheap). Launch = `POST /v1/agents` (quota). Honor the split.
4. Repo `https://github.com/keithbbf-gif/cosmos`, `startingRef=main`.
5. Do not wrap `bts_cursor`. Port-plan ADAPTED successor is a COSMOS rail, not a
   second BTS client.
6. `$0` marginal ≠ skip the ledger. Dispatcher still appends `RAIL_DISPATCH` /
   `RAIL_RESULT`.
7. `GET /v1/repositories` is 1/min, 30/hr — do not poll.

From `docs/CURSOR_LANE.md` §2 (rail contract this slice shipped):

- `kind=API`, `link_id=cursor-api`, `src→dst=core→models`, `metered_usd=0.0`.
- `register_cursor_rail` records the claim and attaches the probe.
- `attach_to_kernel` is additive; does not edit `kernel.py`.
- `--gate` isolated ledger; not authority; no `POST /v1/agents`.
- Re-run rule (§7): new `Date` expected; **`apiKeyName` must stay `Cursor COSMOS 2`**.

From research (`docs/research/CURSOR_LANE.md` §§5–6, 8) and DHx:

- Cloud Agents v1: create `{agent, run}`, poll run until terminal, read `result`
  + `git.branches[].prUrl`.
- Coding overflow, not a chat-model peer. `POST /v1/agents` is billed/quota.
- One authority, one ledger. Key via resolver, never the git tree.
- Three DHx dispatch paths exist (headless CLI / Cloud Agent API / SDKs). This
  slice is the Cloud Agent API rail only — in scope.

From Dispatcher (`cosmos_rails.Dispatcher.dispatch`):

- Adapter: `kind`, `probe() -> (ok, detail)`, `dispatch(payload) -> {ok, kind, ...}`.
- `metered_usd` falsy → skip spend gate; still ledger.
- `BROKE` aborts the route (`RAIL_FAILED`). Only `UNREACHABLE` /
  `SESSION_EXPIRED` / `AUTH_REQUIRED` fall through.

From BACKLOG / this dispatch: **do not modify kernel**. `Kernel.__init__` still
does not call `register_node_rails`. That hole is not this slice's defect and
not this slice's to close.

---

## Live-tree read (this critique, not a stage-6 pass)

Quoted from `live/config/cursor_rail_probe.json` (host read this session):

```
gate                        = PASS
gated_at                    = 2026-08-25T23:04:14-05:00
tree_id                     = KMesh-COSMOS-live
link_id                     = cursor-api
live_value.apiKeyName       = Cursor COSMOS 2
live_value.http             = 200
live_value.date             = Wed, 26 Aug 2026 04:04:13 GMT
me.userId                   = 405041965
key_last4                   = crsr_…31ab
probe_ok                    = true
matrix[0].verified          = true (route core->models)
isolated_ledger_events      = LINK_REGISTERED, PROBE_RESULT
authority_ledger_written    = false
kernel_attached             = false
launch                      = false
```

`probe_detail` Date is `04:04:12 GMT`; `live_value.date` is `04:04:13 GMT`
(two `/v1/me` hops in one `--gate`; spec already notes the split).

Isolated ledger `live/state/cursor_rail/gate.jsonl` line 2 payload (seq=2,
writer `cosmos-cursor-rail`): `PROBE_RESULT` `ok=true` detail contains
`apiKeyName=Cursor COSMOS 2 http=200 date=Wed, 26 Aug 2026 04:04:12 GMT`.

Host-side key file (redacted): length **69**, prefix `crsr_`, last4 `31ab`.
Matches research. Secret not printed.

`live/config/cursor_rail.json`: `link_id=cursor-api`, `rail_type=API`,
`src=core`, `dst=models`, `policy_rank=0`, `metered_usd=0.0`,
`repo_url=https://github.com/keithbbf-gif/cosmos`, `starting_ref=main`,
`auto_create_pr=true`, `work_on_current_branch=false`, `base=https://api.cursor.com`.
No `crsr_` secret in the spec file.

`Kernel.__init__` (`cosmos/cosmos_kernel.py`) composes an empty `Registry` +
`SpendGate`. No `register_node_rails`, no `register_cursor_rail`, no
`Dispatcher`, no `adapters`. `docs/BACKLOG.md` owed LIVE CORE still open.

These numbers prove the COSMOS key answers `/v1/me` as `Cursor COSMOS 2`.
They do not prove the decided gate predicate, a launch, or production attach.

---

## HIGH

### H1 — `--gate` PASS does not bind `apiKeyName` to `Cursor COSMOS 2` (BTS key would pass)

- **File/symbol:** `cosmos/cosmos_cursor_rail.py` — `gate` PASS block
  (`live_name = (rec.get("live_value") or {}).get("apiKeyName")` then
  `if rec["probe_ok"] and live_http == 200 and live_name and ...`);
  `CursorRail.probe` (`if status == 200 and name:` any truthy name);
  `read_key` (prefix `crsr_` + `len >= 12` only).
- **Decided:** DHx + spec §1: COSMOS's own key, **never** `Cursor BTS` /
  `Cursor BTS 2`. Spec §4 proof table and §7 re-run: `apiKeyName` **must stay**
  `Cursor COSMOS 2`.
- **Build:** PASS requires a truthy `apiKeyName` and HTTP 200. It does not
  compare to `"Cursor COSMOS 2"`. It does not reject names containing `BTS`.
  `read_key` will accept any `crsr_` blob ≥ 12 chars (official format is 69).
  Selftest injects `me_body["apiKeyName"]="Cursor COSMOS 2"` and never asserts
  the BTS-reject path.
- **Live proof:** the proof *file* currently quotes `Cursor COSMOS 2` because
  that is what this tree's key returned on 2026-08-25T23:04:14-05:00. The
  *predicate* would have written `gate=PASS` for `Cursor BTS 2` the same way.
- **Impact:** The identity the spec named as the live-tree value is
  documentation, not a gate. Swapping the key file for a BTS secret (or a
  truncated `crsr_` toy) is still a green `--gate`. That is the fabricated-
  compliance class on the slice's own proof.
- **Fix:** PASS iff `live_value.apiKeyName == "Cursor COSMOS 2"` and
  `live_value.http == 200`. `probe()` fail-closed on any other name (detail
  must say `BTS` / mismatch, not `live`). Test: injected `apiKeyName="Cursor
  BTS 2"` → `gate=FAIL` / probe `UNREACHABLE`. `read_key` length = 69.

### H2 — `--launch` exit status is the probe gate, not whether a Cloud Agent launched

- **File/symbol:** `cosmos/cosmos_cursor_rail.py` — `main` (`rec = gate(...,
  launch=a.launch is not None, prompt=a.launch)` then
  `return 0 if rec.get("gate") == "PASS" else 2`); `gate` launch block (runs
  `dispatch` after the identity GET, does **not** fold `dispatch["ok"]` into
  `rec["gate"]`).
- **Decided:** Probe and launch are a split. Launch is opt-in quota
  (`POST /v1/agents`). `rc=0` is not the proof — but a CLI that reports
  success must still track the verb it was asked to perform.
- **Build:** `--launch "PROMPT"` always goes through `gate()`. Launch failure
  (HTTP 4xx, missing `agent.id`, `TIMEOUT_POLLING`, empty prompt →
  `launch_error`) leaves `gate=PASS` if `/v1/me` was 200. Conversely, a
  successful POST after a failed probe returns rc=2. `gate["launch"]` is then
  the bool `True` ("we attempted"), not the Cloud Agent outcome.
- **Impact:** An operator (or a clock) can spend quota, get a failed run, and
  see rc=0 / `gate=PASS`. The inverse hides a successful launch behind a probe
  miss. This is the same green-log class the Motif forbids.
- **Fix:** `--launch` is not `--gate`. Separate the verbs. Launch rc follows
  `dispatch["ok"]` (and never writes `gate=PASS` on a failed POST). A combined
  invocation must record both, and the process exit must not claim PASS when
  launch failed. Test: injected POST 500 → nonzero rc, `gate != PASS` if the
  command was `--launch`.

### H3 — `core→models` + `autoCreatePR=true` is a Cloud Agent coding launch registered as a model peer

- **File/symbol:** `default_spec` (`src="core"`, `dst="models"`,
  `policy_rank=0`, `auto_create_pr=True`); `CursorRail._create_body`
  (every dispatch includes `repos[]` + `autoCreatePR` + `workOnCurrentBranch`);
  `register_cursor_rail` (`registry.register(..., spec["src"], spec["dst"], ...)`).
- **Decided (research / DHx, which spec §1 says is not re-opened):** Cursor
  Cloud Agents are a **coding** overflow. Create is quota. Output is a branch /
  PR / `result` text. Model asks are `sgh-api` / `gem-api` / `gw-api` /
  `oa-api` (`cosmos_node_rails` specs, same `core→models`, same rank 0).
  Dispatcher `route("core","models")` then `adapter.dispatch(payload)` is "ask
  a model."
- **Build / stage-4 spec:** the rail claims the same route as those four APIs.
  `dispatch({"prompt": "..."})` always `POST /v1/agents` against
  `keithbbf-gif/cosmos` with `autoCreatePR=true` (OpenAPI default is *false*;
  research chose true for the *coding* recipe). Dispatcher fallback: a Cloud
  Agent `ERROR`/`TIMEOUT_POLLING` is `kind=BROKE` → `RAIL_FAILED`, so it will
  **not** fall through to `sgh-api`. `metered_usd=0` skips the spend breaker,
  so the quota POST is unbudgeted.
- **Live proof:** `cursor_rail.json` and the probe `matrix[0].route` are
  `core->models`. `--gate` never `dispatch`es, so the landmine is not armed on
  the live Kernel (H4 / BACKLOG). Selftest *does* `disp.dispatch("core",
  "models", {"prompt": "route me", ...})` and treats a Cloud Agent FINISHED
  text as the model-rail success path.
- **Impact:** The moment Kernel attach (BACKLOG) calls this register without
  changing src/dst/rank, a live `core→models` ask can mint a GitHub Cloud
  Agent, push a `cursor/…` branch, and open a PR — and on BROKE, block the
  real model rails. That is not the research recipe sitting behind a coding
  kind. Spec-and-build agree on a wrong route. Closing the Kernel hole as-is
  is unsafe.
- **Fix:** Do not register `cursor-api` as a peer of `sgh-api`. A coding rail
  needs its own route (e.g. `core→code` / `kind` distinct / explicit
  `dispatch` kind), or a payload schema that cannot be satisfied by a model
  ask (require `repos`/`launch` flag; refuse a bare `prompt`).
  `autoCreatePR` stays opt-in for the coding recipe, never the default for
  `Dispatcher.dispatch("core","models")`. Test: `Dispatcher.dispatch("core",
  "models", {"prompt": "hi"})` with sgh+cursor both live must not POST
  `/v1/agents`.

### H4 — `attach_to_kernel` writes authority `LINK_REGISTERED` with an in-memory probe (dangling claim)

- **File/symbol:** `attach_to_kernel` → `register_cursor_rail(kernel.registry,
  ...)`; `Registry.register` appends `LINK_REGISTERED` to whatever ledger the
  Kernel owns (`authority.jsonl` for a writing Kernel);
  `Registry.attach_probe` stores the callable in `self._probes` (not the
  ledger).
- **Decided:** Spec §5: "Do not append `LINK_REGISTERED` to the authority
  ledger without attaching the probe on every boot — probes are in-memory. A
  dangling claim is how 'registration is not capability' becomes a lie."
  Kernel `__init__` does not call this (BACKLOG). This slice must not edit
  kernel — correct. The helper must not be a one-shot authority writer either.
- **Build:** `attach_to_kernel` on a writing Kernel is a live authority append.
  Next `Kernel()` boot reconstructs Registry from the ledger **without** the
  probe map. Claim remains; measurement is gone (`NO_PROBE` / not live).
  Docstring only notes that a *read-only* Kernel refuses append. Selftest
  attaches on a spike Kernel, not a guard against the live root.
- **Impact:** The "additive compose" advertised in spec §5 is the dangling-
  claim generator if anyone uses it before `Kernel.__init__` reattaches every
  boot. Isolated `--gate` does not do this (`authority_ledger_written: false`
  on the live proof — good). The helper still will, on the real Kernel.
- **Fix:** `attach_to_kernel` must refuse unless it is being called from boot
  composition (or unless `kernel.ledger` is not the authority file). Until
  Kernel attach is allowed, the only legal compose is the isolated `--gate`
  ledger. Do not document `attach_to_kernel(kernel)` as equivalent to boot
  attach while boot attach does not exist.

---

## MEDIUM

### M1 — Two Cloud Agent launchers; auth and path already drifted

- **File/symbol:** `CursorRail._real_http` / `CursorRail.dispatch` (Bearer,
  `paths.config(key_name)`); `cosmos_dispatch._cursor_job` (Basic `key:`,
  `Path(runtime_root) / "config" / CURSOR_KEY_NAME` — hand-assembled, no
  `CosmosPaths`).
- **Decided:** Spec §6 defers unifying dispatch-kind onto the rail. Research
  recipe is one loop. Resolver: no caller assembles paths by hand. Auth: either
  Bearer or Basic, not two independent stacks.
- **Build:** `cosmos_dispatch` kind `cursor` never imports `CursorRail`. Bearer
  vs Basic already diverge. Dispatch still concatenates `config/` onto a root
  path. `cosmos_rails_prober._cursor_probe` is a third `/v1/me` caller that
  *does* use `CursorRail`.
- **Impact:** A Cursor recipe bug will be fixed in one place and not the other.
  The live coding path Keith's clocks actually drop is still the dispatch job,
  not this rail. "The rail is the registry adapter" is true and also means the
  decided launch path is not the one the OS runs.
- **Fix:** `_cursor_job` (or the job it writes) calls `CursorRail.dispatch`.
  Delete the duplicate urllib/poll loop. Key path only via `paths.config`.

### M2 — `--gate` `dispatcher_composed=True` is object construction, not Dispatcher behavior

- **File/symbol:** `gate` (`disp = Dispatcher(...)`;
  `rec["dispatcher_composed"] = True`; PASS requires that flag). Isolated
  ledger events on the live proof are only `LINK_REGISTERED`, `PROBE_RESULT` —
  no `RAIL_DISPATCH` / `RAIL_RESULT`.
- **Decided:** `$0` marginal ≠ skip the ledger. Dispatcher still appends
  `RAIL_DISPATCH` / `RAIL_RESULT`. `--gate` must not POST; that part is
  honest. Calling the isolated compose a "Dispatcher-shaped" *proof* is not.
- **Build:** Selftest (fake HTTP) is the only place those events are asserted.
  Live `--gate` never calls `disp.dispatch`. PASS treats a constructor as
  capability.
- **Impact:** The live-tree file can say `dispatcher_composed: true` forever
  without the Dispatcher having run a rail. That is a green log inside the
  proof artifact.
- **Fix:** Drop `dispatcher_composed` from the PASS predicate. Name it
  `dispatcher_constructed`. Prove `RAIL_DISPATCH`/`RAIL_RESULT` only on an
  isolated *fake-HTTP* dispatch (selftest), or on an explicit `--launch` that
  is not the probe gate.

### M3 — Create without `run.id` is reported `ok=True`

- **File/symbol:** `CursorRail.dispatch` (`if status not in (200, 201) or not
  aid` fails; `if not do_poll or not rid: rec["text"] = f"launched {aid}
  run={rid} ..."; return rec` with `ok=True`).
- **Decided:** Research create returns `{agent, run}`; poll is
  `GET /v1/agents/{id}/runs/{runId}`. A launch you cannot poll is not a
  launch.
- **Build:** Missing `rid` after 201 skips poll and returns success. `aid`
  fallback also accepts `created["id"]` (v0-shaped).
- **Impact:** Dispatcher will treat an un-pollable create as a live API
  success and not try another link.
- **Fix:** No `rid` → `ok=False`, `kind=BROKE`. Test it.

### M4 — Poll result does not lift `git.branches[].prUrl` (the DHx recipe's return)

- **File/symbol:** `CursorRail.dispatch` (`rec["text"] = str(last.get("result")
  or "")[:4000]`; `rec["run"]["git"] = last.get("git")` nested only).
- **Decided:** DHx / research poll target: `FINISHED` / `result` /
  `git.branches[].prUrl`. Cloud output is code (branch / PR).
- **Build:** Callers reading `result["text"]` get assistant text. `prUrl` is
  buried. No field `pr_url` / `branch`.
- **Impact:** A COSMOS return-watcher looking at Dispatcher `text` will not
  see the PR the Cloud Agent opened. The coding lane's actual artifact is
  optional JSON one level down.
- **Fix:** Promote `prUrl` / `branch` / `repoUrl` to the dispatch dict.
  Truncation flag if `result` exceeds the cap.

### M5 — Spec overlay can retarget `base` and `key_name` off the decided endpoints

- **File/symbol:** `merge_spec` (copies every overlay key; `base` defaults to
  `https://api.cursor.com` but any string is accepted; `key_name` any string).
- **Decided:** Base is `https://api.cursor.com`. Key is
  `config/cursor_cosmos_key.txt` under the verified root. Fail-closed.
- **Build:** `live/config/cursor_rail.json` can point the rail at another host
  or another filename (including a BTS key file name) and `merge_spec` will
  honor it. Combined with H1, `--gate` still PASSes on whatever `/v1/me`
  returns.
- **Impact:** The runtime spec is an unsigned, unconstrained overlay on the
  decided identity.
- **Fix:** Fail-closed unless `base` is the vendor origin (allow an explicit
  documented pin). `key_name` stays `cursor_cosmos_key.txt` unless a typed
  override is a later decision. Test a `base` of `https://example.invalid` →
  `BAD_SPEC`.

### M6 — Duplicate poll/HTTP stack vs Motif "improvement is not bloat"

- **File/symbol:** `CursorRail._real_http` + poll loop (~80 lines) vs
  `cosmos_dispatch._cursor_job` embedded urllib/poll (~80 lines). `_selftest`
  inlined; `tests/test_cursor_rail.py` is a 27-line wrapper that only calls it.
- **Decided:** Motif standing rule: net complexity trends down. One recipe.
- **Build:** Two launchers (M1) plus a third probe in `cosmos_rails_prober`.
  Tests do not add cases the module selftest lacks (H1 BTS name, M3 missing
  rid, repositories-not-called).
- **Impact:** Weight without a second contract. Stage-5 critics judge elegance
  as a gate criterion.
- **Fix:** One HTTP helper. Tests own the cases the selftest currently skips.
  Do not grow a fourth client.

---

## LOW

### L1 — `--gate` issues two live `GET /v1/me` (proof Date ≠ ledger Date)

- **File/symbol:** `gate` (`reg.probe` → `CursorRail.probe` then
  `adapters[...]._call("GET", "/v1/me")` again).
- **Live:** `probe_detail` Date `04:04:12 GMT` vs `live_value.date`
  `04:04:13 GMT`. Spec documents the split instead of collapsing it.
- **Fix:** One GET. Parse identity from the probe body/headers (pass them
  through `probe()` or cache on the rail).

### L2 — `read_key` length ≥ 12; official key is 69 bytes

- **File/symbol:** `read_key`. Live file is 69 (bound this session).
- **Fix:** Require `startswith("crsr_")` and `len==69` (or vendor's hex-64
  rule). Test a 12-char toy → `NO_KEY`.

### L3 — Secret-absent check is tautological

- **File/symbol:** `_selftest` (`"crsr_" not in spec_txt or "crsr_…" in
  spec_txt`).
- **Fix:** Assert the full dummy secret is absent, and `crsr_…last4` is the
  only form present.

### L4 — Proof file stores `userEmail`

- **File/symbol:** `gate` `rec["me"]["userEmail"]`;
  `live/config/cursor_rail_probe.json`.
- **Decided:** Spec quotes `userId` / `apiKeyName`. Email is not required for
  the live-tree value.
- **Fix:** Drop email from the proof (keep userId). Live is gitignored; still
  no reason to copy PII into the quoted identity.

### L5 — Isolated `gate.jsonl` is unbounded; PASS uses event-*name* existence

- **File/symbol:** `gate` (`events = [e.get("event") for e in led.verify()]`;
  `"LINK_REGISTERED" in events and "PROBE_RESULT" in events`). HMAC key is
  the literal `b"cursor-rail-gate"`.
- **Impact:** After the first run, those names are always present. This-run
  identity is `probe_ok` / `live_value`, not the JSONL. Fine while isolated;
  do not treat the isolated chain as a second proof.
- **Fix:** Assert *this run's* last two events, or do not use the isolated
  ledger in the PASS predicate.

### L6 — First poll sleeps `poll_s` before the first GET

- **File/symbol:** `CursorRail.dispatch` (`while time.time() < deadline:
  time.sleep(...); GET ...`).
- **Impact:** A run that is already `FINISHED` still waits 15s. Quota is not
  the issue; the return is delayed for no reason.
- **Fix:** GET, then sleep.

### L7 — No assertion that `GET /v1/repositories` is never called

- **File/symbol:** missing in `_selftest` `calls` checks (probe asserts no
  POST; nothing asserts path `!= /v1/repositories`).
- **Fix:** One check on the fake HTTP log.

### L8 — `spend_gate.set_budget` failures swallowed

- **File/symbol:** `register_cursor_rail` `except Exception: pass` (same
  pattern as `register_node_rails`). Harmless at `metered_usd=0`; a later
  overlay that meters the rail can run unbudgeted and then
  `UNKNOWN_RAIL` / mis-kinded `NOT_PERMITTED`.
- **Fix:** Do not swallow. If metered and `set_budget` fails, refuse
  registration.

### L9 — Bearer only; Basic not implemented in this rail

- **File/symbol:** `_real_http` `Authorization: Bearer`.
- **Decided:** either is valid; Bearer was proven live. Not a functional miss.
  Note only because `cosmos_dispatch` already chose Basic (M1).
- **Fix:** None required if M1 collapses onto this client.

---

## What matches (do not re-open)

- No `bts_cursor` import. Successor module is COSMOS HTTP, not a wrap.
- Probe never POSTs `/v1/agents`. `--gate` live proof `launch: false`.
- Key via `paths.config`; isolated state via `paths.role("state", "cursor_rail")`.
  No drive literal as identity in this module.
- `metered_usd=0` skips spend; selftest still sees `RAIL_DISPATCH` +
  `RAIL_RESULT` on fake dispatch.
- Missing key → probe/dispatch `UNREACHABLE`, still registered.
- Default repo / `startingRef=main` / `workOnCurrentBranch=false`.
- Does not poll `/v1/repositories` (no code path).
- Does not write authority.jsonl from `--gate`.
- Does not modify kernel/ledger/sched/service. `kernel_attached: false` is
  recorded, not papered over.
- Live `/v1/me` 200 `apiKeyName=Cursor COSMOS 2` `key=crsr_…31ab`
  `tree_id=KMesh-COSMOS-live` — that *value* is real. The *predicate* is H1.

## UNKNOWN / not this slice (honest, same as spec §6)

- Kernel production attach. BACKLOG. Forbidden here.
- `POST /v1/agents` against this key right now. Not sent by `--gate`; this
  critique did not send it either.
- Model catalog (`GET /v1/models`).
- Key expiry / dashboard Admin label (`/v1/me` has neither).
- GitLab URLs as `repos[].url`.
- Headless Cursor Agent CLI / SDKs (DHx lists them; this slice is Cloud
  Agents API).
- A second-family stage-5 vote.

---

## Runtime-binding (stage 6) — what would count

Not this document. Not `SELFTEST PASS - 22 checks`. Not
`live/config/cursor_rail_probe.json` `gate=PASS` while
`kernel_attached: false`.

A later stage-6 value, after HIGHs close, is one of:

1. Production Kernel actually routes a *coding* dispatch through `cursor-api`
   and the authority ledger shows `RAIL_DISPATCH` / `RAIL_RESULT` with a live
   `apiKeyName=Cursor COSMOS 2` (and a `prUrl` or typed refusal) — which
   requires the BACKLOG Kernel attach, Keith's call; or
2. An explicit, durable refusal: `cursor-api` is a satellite rail, Kernel
   attach is BACKLOG, and the OS coding path is `cosmos_dispatch` kind
   `cursor` *calling this rail* — proven by a live job result whose
   `apiKeyName` / `agent_id` / `run.status` only this tree's key can emit.

Until then the row is DRAFT. `--gate` remains a valid *key* probe for the
satellite module, not Motif complete.

---

## Suggested next (stage 6 consensus / improve — not done here)

1. Bind `--gate` PASS to `apiKeyName=="Cursor COSMOS 2"` (H1).
2. Split `--launch` rc from `--gate` (H2).
3. Change the registered route so a model ask cannot mint a Cloud Agent (H3).
   Do **not** attach to Kernel until that lands.
4. Make `attach_to_kernel` refuse authority writes without boot reattach (H4).
5. Point `cosmos_dispatch` cursor kind at `CursorRail` (M1).
6. Different-family (non-Grok-Build) pass on this critique + the patched
   build.

Kernel attach stays on `docs/BACKLOG.md`. This critique does not edit
`cosmos_kernel.py`.
