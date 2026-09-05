# CURSOR_LANE — COSMOS rail (`cursor-api`)

**Stage:** Motif 6 runtime-binding (satellite). **Author:** G46. **Date:** 2026-08-26.
**Kernel attach remains BACKLOG** — this slice cannot modify `cosmos_kernel` /
`cosmos_ledger` / `cosmos_sched` / `cosmos_service`. Stage-5 HIGH/MED from
`docs/critique/cursor_CRITIQUE_g46.md` applied additively in
`cosmos/cosmos_cursor_rail.py`.

`rc=0` is not the proof. The live-tree value is
`live/config/cursor_rail_probe.json` (`live_value.apiKeyName`, `http`, `date`)
plus `attach_refusal` against this tree's authority path.

---

## 1. What was decided (from research, not re-opened)

Bound to `docs/research/CURSOR_LANE.md` (GET `/v1/me` HTTP 200, 2026-08-26
02:36:56 GMT) and `docs/research/CURSOR_CLOUD_AGENTS_API_v1.md`:

| Decision | Bound to |
|---|---|
| COSMOS's own key, never BTS (`Cursor BTS` / `Cursor BTS 2`) | DHx; key file `live/config/cursor_cosmos_key.txt` |
| Auth: Bearer (proven) or Basic `key:` | live `/v1/me` 200 + vendor docs |
| Probe = `GET /v1/me` (cheap). Launch = `POST /v1/agents` (quota) | research recipe; `--gate` vs `--launch` are split (H2) |
| Repo `https://github.com/keithbbf-gif/cosmos`, `startingRef=main` | `git remote` / research |
| Do not wrap `bts_cursor` | Keith 2026-08-25: no BTS; port-plan ADAPTED successor is `cosmos_rails` |
| $0 marginal (Ultra included) ≠ skip the ledger | research §8; Dispatcher still appends `RAIL_DISPATCH` / `RAIL_RESULT` |
| `GET /v1/repositories` is 1/min, 30/hr — do not poll | vendor docs |
| Coding overflow, not a chat-model peer | research / DHx; route is `core→code` (H3) |

`bts_cursor` stays ADAPTED in `cosmos_port_plan.py`. This module is the COSMOS
successor, not a second BTS client.

---

## 2. What landed (files)

| Path | Role |
|---|---|
| `cosmos/cosmos_cursor_rail.py` | `CursorRail` adapter (`probe` / `dispatch`) + `register_cursor_rail` + `attach_to_kernel` (H4 refuse) + `--gate` / `--launch` |
| `tests/test_cursor_rail.py` | isolated fake-HTTP selftest wrapper (calls `_selftest`; not edited this slice) |
| `live/config/cursor_rail.json` | runtime spec (no secret; `src/dst=core/code`) |
| `live/config/cursor_cosmos_key.txt` | secret (pre-existing; git-ignored; never printed in full) |
| `live/config/cursor_rail_probe.json` | **live-tree proof** of `--gate` |
| `live/state/cursor_rail/gate.jsonl` | isolated ledger (`LINK_REGISTERED`, `PROBE_RESULT`) — not authority |
| `live/state/cursor_rail/gate.json` | copy of the proof record |

### Rail contract (Dispatcher-shaped)

```
kind = "API"
link_id = "cursor-api"          # live/config/cursor_rail.json
src -> dst = core -> code       # NOT core -> models (H3)
probe()  -> (ok, detail)        # GET /v1/me only; fail-closed unless apiKeyName=="Cursor COSMOS 2"
dispatch(payload) -> {ok, kind, text, pr_url, branch, ...}   # POST /v1/agents + poll
metered_usd = 0.0               # included lane; spend-gate skipped
```

`register_cursor_rail(registry, adapters, spend_gate=..., paths=...)` records the
claim and attaches the probe. Missing key → still registered; probe returns
`UNREACHABLE` (registration is not capability). Explicit `src/dst=core/models`
raises `BAD_SPEC`. Overlay `dst=models` is coerced to `code`.

`attach_to_kernel(kernel)` is the additive compose. It does **not** edit
`kernel.py`. It **refuses** to append `LINK_REGISTERED` to the authority ledger
unless `boot_compose=True` (H4). A later Kernel boot that calls it with
`boot_compose=True` is the BACKLOG item this slice is forbidden to close.

`--launch` is a separate verb from `--gate` (H2). Launch rc follows
`dispatch["ok"]` and never writes `gate=PASS` on a failed POST.

---

## 3. Stage-5 HIGH/MED applied this slice

Bound to `docs/critique/cursor_CRITIQUE_g46.md`. Kernel attach stays BACKLOG.

| ID | Fix |
|---|---|
| H1 | `--gate` PASS iff `live_value.apiKeyName == "Cursor COSMOS 2"` and `http == 200`. `probe()` fail-closed on BTS / mismatch. `read_key` length = 69. |
| H2 | `--launch` is not `--gate`. Separate verbs. Combined invocation fails the process if launch failed. |
| H3 | Registered route is `core→code`. `Dispatcher.dispatch("core","models")` cannot mint a Cloud Agent via this rail. |
| H4 | `attach_to_kernel` refuses authority writes without `boot_compose=True`. |
| M1 | `run_coding_dispatch` is the one launcher. `cosmos_dispatch._cursor_job` still embeds urllib (this slice cannot edit `cosmos_dispatch.py`). Collapse point exists; dispatch rewire is owed COW. |
| M2 | PASS does not use `dispatcher_composed`. Field renamed `dispatcher_constructed`. Isolated `--gate` does not claim Dispatcher behavior. |
| M3 | Create without `run.id` → `ok=False`, `kind=BROKE`. |
| M4 | `pr_url` / `branch` / `repo_url` promoted on the dispatch dict. Truncation flagged. |
| M5 | `base` pinned to `https://api.cursor.com`. `key_name` pinned to `cursor_cosmos_key.txt`. Else `BAD_SPEC`. |
| M6 | One HTTP helper (`_real_http`). Selftest owns H1/H3/M3/M5/L7 cases. No fourth client. |

LOW applied where they were the same change: L1 (one GET, identity from probe cache),
L2 (len=69), L4 (no `userEmail` in proof), L6 (GET then sleep), L7 (repositories
never called, asserted), L8 (`set_budget` failure refuses registration when metered).

---

## 4. Isolated selftest (not the gate)

Command:

```
py -3.14 cosmos\cosmos_cursor_rail.py --selftest
```

Fake HTTP; dummy key `crsr_…31ab` (69 chars); no live `POST /v1/agents`; no
authority ledger writes. This is a green log — **not** runtime binding.

---

## 5. Runtime-binding proof (the live-tree value)

Command:

```
py -3.14 cosmos\cosmos_cursor_rail.py --root V:\A\Ai\COSMOS\live --gate
```

`--gate` composes `Registry` + `Dispatcher` on an **isolated** ledger under
`live/state/cursor_rail/` (throwaway HMAC key `cursor-rail-gate`, writer
`cosmos-cursor-rail`). It does **not** append to `live/ledger/authority.jsonl`.
It does **not** `POST /v1/agents`.

PASS predicate (H1, not a truthy name):

- `probe_ok`
- `live_value.apiKeyName == "Cursor COSMOS 2"`
- `live_value.http == 200`
- `route == "core->code"`
- `attach_refusal.refused == true` (H4 against this tree's authority path)
- `authority_ledger_written == false`
- `kernel_attached == false`
- `cursor-api` is not in a production Kernel registry (when a read-only Kernel opens)

**Proof file:** `live/config/cursor_rail_probe.json`

Quoted fields from that file (host read after `--gate` 2026-08-26T10:03:11-05:00):

| Field | Value |
|---|---|
| `gate` | `PASS` |
| `gated_at` | `2026-08-26T10:03:11-05:00` |
| `tree_id` | `KMesh-COSMOS-live` |
| `link_id` | `cursor-api` |
| `live_value.apiKeyName` | `Cursor COSMOS 2` |
| `live_value.http` | `200` |
| `live_value.date` | `Wed, 26 Aug 2026 15:03:10 GMT` |
| `me.userId` | `405041965` |
| `key_last4` | `crsr_…31ab` |
| `route` | `core->code` |
| `probe_ok` | `true` |
| `identity_ok` | `true` |
| `matrix[0].verified` | `true` (route `core->code`) |
| `authority_ledger_written` | `false` |
| `kernel_attached` | `false` |
| `launch` | `false` |
| `attach_refusal.refused` | `true` (`kind=REFUSED`) |
| `live_kernel.opened` | `true` (read-only) |
| `live_kernel.cursor_in_registry` | `false` |
| `stage6.kernel_attach` | `BACKLOG` |

`proof` string in that file:

`cursor-api probe_ok=True apiKeyName='Cursor COSMOS 2' http=200 date='Wed, 26 Aug 2026 15:03:10 GMT' key=crsr_…31ab tree_id=KMesh-COSMOS-live route=core->code attach_refused=True kernel_attached=False`

That `apiKeyName` + HTTP 200 + `Date` header is a value only this tree's
COSMOS key can emit (a new `Date` vs the stage-4 proof `Wed, 26 Aug 2026
04:04:13 GMT`). The attach refusal + `tree_id` is a value only this tree's
resolver-verified authority path can emit. Neither is an exit code.

### Honest limit (stage-6 satellite)

Production Kernel **will not** show `cursor-api` until `Kernel.__init__`
attaches rails (`docs/BACKLOG.md` owed LIVE CORE). This file does not pretend
otherwise. `kernel_attached: false` and `stage6.kernel_attach: BACKLOG` are
the recorded gap.

Critique option 1 (authority `RAIL_DISPATCH` / `RAIL_RESULT` through a
Kernel-composed `cursor-api`) requires Kernel attach — Keith's call, not this
slice.

Critique option 2 residual: `cosmos_dispatch` kind `cursor` still has its own
urllib loop. `run_coding_dispatch` is the collapse point; rewiring
`cosmos_dispatch.py` is outside this deliverable tree.

---

## 6. How to compose later (when Kernel is allowed to)

```python
from cosmos_cursor_rail import register_cursor_rail, attach_to_kernel

# preferred, once Kernel.__init__ calls register_node_rails:
register_cursor_rail(kernel.registry, adapters, kernel.spend, paths=kernel.paths)

# equivalent additive, ONLY from Kernel boot (probes reattached every boot):
attach_to_kernel(kernel, boot_compose=True)
```

Do not call `attach_to_kernel(kernel)` without `boot_compose=True` — it
refuses. A dangling `LINK_REGISTERED` on authority without an in-memory probe
is how "registration is not capability" becomes a lie.

Opt-in Cloud Agent launch (quota; not the gate):

```
py -3.14 cosmos\cosmos_cursor_rail.py --root V:\A\Ai\COSMOS\live --launch "PROMPT"
```

`--launch` rc follows `dispatch["ok"]`. A failed POST does not report
`gate=PASS`. This session's stage-6 gate did **not** run `--launch` (no quota
POST).

The one launcher for other modules:

```python
from cosmos_cursor_rail import run_coding_dispatch
run_coding_dispatch(root, prompt, poll=True)
```

---

## 7. UNKNOWN / not claimed

- Kernel production attach. Forbidden this slice (`kernel.py`). BACKLOG.
- `POST /v1/agents` against this key **right now**. Not sent by `--gate`.
- Model catalog (`GET /v1/models` not called this slice).
- Key expiry / dashboard "Admin" label (still absent from `/v1/me`).
- GitLab URLs as Cloud Agents `repos[].url` (docs: GitHub).
- Headless Cursor Agent CLI / SDKs (DHx lists them; this slice is Cloud Agents API).
- Rewiring `cosmos_dispatch._cursor_job` onto `run_coding_dispatch` (M1 residual;
  cannot edit `cosmos_dispatch.py` this slice).
- A second-family stage-5 vote (the critique on disk is G46, same family as the
  build). Findings were spec-vs-build and bound to files; they are applied.

---

## 8. Re-run

```
py -3.14 cosmos\cosmos_cursor_rail.py --root V:\A\Ai\COSMOS\live --gate
```

Compare `live/config/cursor_rail_probe.json` `live_value` (http, apiKeyName, date)
to this page. A new `Date` is expected; `apiKeyName` must stay `Cursor COSMOS 2`;
`route` must stay `core->code`; `attach_refusal.refused` must stay true;
`kernel_attached` must stay false.
