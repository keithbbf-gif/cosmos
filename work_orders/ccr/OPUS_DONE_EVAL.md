# Evaluate Opus `done\` (2026-09-24)

Packet: `O:\opus2\cosmos2\opus-review\done\` — proposal, **not LiT**.
Checked against live `V:\A\Ai\COSMOS\cosmos\`. CCr disposes. Do not copy `O:\` onto live.

## Verdict

**KEEP the findings. HOLD the land.** Diff file-by-file through Gitur/CCr. Do not drop the whole `done\cosmos` tree on unique HEAD.

Opus did the job the 1092 WO pile did not: **read the code, reproduced bugs, did not invent scores.**

## Confirmed on live LiT (spot-check)

| Claim | Live | Hold? |
|---|---|---|
| `hook_trial` scores matching ballots `who_erred="none"` | `cosmos_porosity.py:879` `unknown if disc else none` | **KEEP** — same wrong answer never raises `cofail` |
| `recommend(axes="coding")` iterates characters | `want = [… for a in (axes or …)]` — a str is iterable by char | **KEEP** |
| WOMB reads `orth_sketch`, porosity emits `orthogonality` | `cosmos_womb.py:167` vs porosity fold | **KEEP** — `/womb/seat` and `/porosity` can rank different pairs |
| TLS `wrap_socket` on the **listening** socket | `cosmos_service.py:2661` no `do_handshake_on_connect=False` | **KEEP** — handshake in `accept()` can freeze `/kill` |
| Unpriced ≠ $0 in the docstring | `SpendGate._state`: `measured_usd is None` → `unpriced += 1`, **settled += 0** | **KEEP** — F5 breaker headroom ignores unpriced. `SpendGuard.record(usd=None)` already uses `CALL_EST_USD`. Two spend systems; only the voice/service guard holds |
| `bool("false")` is True | `record_pair`: `disc = bool(disagree)` | **KEEP** — string `"false"` records disagree=True |
| Default `error_mag=5` | `record_pair` default None; **`record_hit_vectors(..., error_mag=5)`** | **KEEP on hit-vectors only** — invents mag when caller omits it |

Did not re-run their 10k-obs bench. Timing numbers are **their machine/snapshot**, not a live Core gate.

## KEEP (land as P10, one PR per seam)

1. **Tensor correctness** — **LANDED 2026-09-24 (partial):** hook_trial matching ballots → `who_erred=unknown`; `disagree="false"` is False; `recommend(axes="coding")` comma-splits. Selftest **26/26**. Did **not** land NaN/rotator/hit-vector mag=5 / log lock / full rewrite. Existing 619 obs unchanged.
2. **Log** — mutex + fsync, torn line, `\n`-only split, corrupt visible (`n_corrupt`). Authority log is occupancy.
3. **WOMB** — **LANDED 2026-09-24** (CCr this sid token 8): read `orthogonality`; NaN budget `BAD_INPUT`. Selftest 12/12. Core GET still stale until bounce.
4. **Rater** — refuse BROKE overwrite; atomic save; UNMEASURED price not $0.
5. **Service** — TLS handshake off the accept thread; POST always JSON; `/kill` overflow.
6. **Ledger / lock / 0-byte key** — truncation must not verify clean; install key ≥16 bytes.
7. **Spend** — unpriced holds worst case; Vertex inherit meter; budget seed once; crucible OA gated.
8. **Approval HARDLINE** deletes outside `_delme`.
9. **Secret strip** one `write_spec_record`.
10. **Windows** — `encoding=` on `text=True`; `paths=` on bucket `NodeRail`.

## HOLD (owner / CCr before merge)

- **Behaviour change:** hook rows stop producing complement/cofail. Existing `obs.jsonl` may have invented `none`s. Fold must ignore or re-tag those, not silently rewrite history.
- **vertex-coding metered** → needs a budget or `UNKNOWN_RAIL`. Watch Kelly/Joanna.
- **`--root` required** — clocks/gitur no longer guess `V:\`. Install record must exist.
- **`loopback_trust=legacy` CSRF** left on purpose (`test_p0_opus_exposure.py`). DNS-rebinding closed. Don’t “fix” legacy in the same PR.
- **Rewrite of `cosmos_porosity.py`** — SCHEMA claimed unchanged; still a high-risk file. Prefer surgical diffs over a full replace if CCr can split it.
- **`done\cosmos` still has ~186 `_bite_*` junk files.** Don’t land those. Opus named this and didn’t clean it.

## DROP / don’t

- Don’t treat snapshot selftests as runtime-binding of Core `:8770` (restart still `FORGED_EVENT`).
- Don’t land missing-module imports as “fixed” (`session_tools` etc. absent from packet).
- Don’t copy `done\` over `V:\A\Ai\COSMOS\cosmos`. Unique HEAD + Gitur PR.

## Tie to the WO pile

This pack is **Core truth**. The 1092 board was **process corpses**. Related: WOMB seating used the wrong orth field, so pair picks could be UNMEASURED/wrong — that’s why “auto-seat” must not drive Phase 2 until this lands or WOMB is patched to read `orthogonality`.

Full WO/wishlist crosswalk: `work_orders/ccr/OPUS_VS_PIPELINE.md`.

## Dispose path

Gitur: one job one PR, start with porosity hook_trial + WOMB orth field (smallest, highest leverage). Then log lock. Then TLS. Then spend. CCr `--accept` only after `cosmos_porosity --selftest` on **this** tree with `--root` live.
