# Opus `done\` vs pipeline (WOs + wishlists) — 2026-09-24

Opus pack is **measured Core bugs**. The 1092 board is **process + product**. Crosswalk only. Do not land `done\`. Do not call the overlapping WOs as-is.

Sources: `OPUS_DONE_EVAL.md`, `WOMB_MASTER.jsonl`, `PHASE1/2/3`, `RESURRECT_WO.jsonl`, `VET_PHASE3_100.md`, `WO_REVIEW_ALL.md`, `DEFINE_WOMB.md`, `GITUR_WOMB_SEAT.md`, `DEFINE_*POROSITY*`, `docs/WISHLIST.md` / `BACKLOG.md`, Gitur FIFO `#563–576`, drop `opus-ledger` / `womb-seat`.

## One-line

**Do not farm porosity math. Opus already named the live defects. The board’s porosity WOs are either RESTATE/DEDUP or they teach the wrong field (`orth_sketch`). Auto-seat and Phase 1 pairs stay HOLD until hook_trial + WOMB orth land.**

## Opus KEEP → pipeline

| Opus finding | In the pipeline? | Call? |
|---|---|---|
| `hook_trial` matching ballots → `who_erred=none` (cofail never rises) | **Not named.** Closest: WO-031 “finish tensor math”, WO-037 “fold who_erred into C”, WO-035/778 Luna math, WO-887 “interaction metric”. DEFINE_COMPLEMENT already says unknown → C UNMEASURED — **code violates DEFINE**. | **DROP those WOs as farm jobs.** Gitur PR 1 = this bug. VET already **RESTATE** WO-031, **DEDUP** 035–038. |
| WOMB reads `orth_sketch`, porosity emits `orthogonality` | **Encoded as canon.** `DEFINE_WOMB.md` + `GITUR_WOMB_SEAT.md` + n=581 `womb-seat` + Gitur pick_pair PR: “maximize `orth_sketch`”. `WOMB_ROW_FIELDS.md` / template still have `orth_sketch`. | **HOLD Gitur pick_pair until field alias.** Else auto-seat is UNMEASURED forever. Do not let farm “rewrite T”. |
| `recommend(axes="coding")` iterates characters | **No WO.** | **Gap.** Surgical with hook_trial. |
| `bool("false")` is True in `record_pair` | **No WO.** | **Gap.** Same PR. |
| `error_mag=5` invented on `record_hit_vectors` only | DEFINE “do not invent”. No WO names hit-vectors. | **Gap.** Same PR. |
| TLS `wrap_socket` handshake on accept (can freeze `/kill`) | **No WO.** Core serve / FORGED_EVENT is a different block. | **Gap.** After tensor. |
| SpendGate UNPRICED settle → `settled += 0` | Canon `unpriced ≠ $0` (`ARCH_SPEC`). Voice `SpendGuard` already uses `CALL_EST_USD`. Pipeline KEEP = WO-056/057 spend **tab/UI**, “token/dollar meters”. Not the F5 fold. | **KEEP as new Gitur**, not those UI WOs. Vertex-coding metered = **HOLD** (Kelly/Joanna). |
| Ledger verify on truncated tail | Drop `opus-ledger` T212414, Gitur **#575**. Core restart **FORGED_EVENT**. | **HOLD.** Don’t rewrite live ledger while FORGED. |
| 0-byte install key signs `b""` | F-43 backup secrets **CLOSED**. `CREDENTIALS_NEEDED` SATISFIED. No WO for empty key. | **Gap.** Small Gitur after ledger HOLD lifts. |
| `/kill` junk client_id evicts a real kill | No WO. | **Gap.** With TLS. |
| HARDLINE deletes outside `_delme` | Approval is CONFIRM today. No unique WO. | **HOLD** (behavior). |
| Secret strip one `write_spec_record` | No WO. | **KEEP** later. |
| cDeck porosity CHECK/TEST (WO-326/327/400/401/736/737/746/747) | Phase 4 resurrect **UI occupancy**. | **Not the tensor.** Don’t call to “fix porosity”. Green paint on broken C. |
| Phase 1 P1–P4 (n=501–504) | **0 porosity hits.** Restated measure pairs. | **HOLD until hook_trial.** Else they write invented `none` into `obs.jsonl`. |
| wish-01..05 (mouth) | Chatbot / session-tools / OpenWork bind — **product**, not Core tensor. | Unrelated. Do not auto-seat them off broken T. |
| wish-06 / gold 09–42 | Session-tools suite, Chrome, Voice, CVM… VET TABLE/DEDUP. | Unrelated. |
| wish-34 extra judges | Would **feed** the tensor. | **HOLD** until hook_trial. Extra judges + bad `none` = poison C. |
| `porosity_v6` | `CCR_ORC_NOW` **HOLD**. Opus rewrote in place, SCHEMA claimed `/` unchanged. | Stay HOLD. No v6. |
| MRT-4 `builds/tensor` | `CDECK_PAGES_ARCH` **DO NOT START** until `builds/tensor` exists. | Still don’t. Live tensor is `cosmos_porosity.py`. |

## What the board would waste

Calling WO-031/035/037/043/887/778 as “finish porosity” spends CCrew to **re-derive math Opus already measured**, against `UNVERIFIED_TREE`, with Luna-grades-both farm shape VET already killed.

Calling n=581 / Gitur pick_pair **as written** lands a seater that looks for a field porosity never writes.

Calling Phase 1 pairs **now** is occupancy theater: Judge `who_erred` contract is fine; the **writer** (`hook_trial`) is the liar.

## Wishlist / BACKLOG

Open wishes are product (ChatBot phone, session-tools verbs, CLOCKS collapse, AUTO-RESESSION, makers). **None name hook_trial / orth field / SpendGate fold / TLS handshake.**

Wishlists **depend** on T for WOMBAT auto-seat (`DEFINE_WOMB` missing #2). Until Opus KEEP 1+3 land, auto-seat must stay **hand seating** (current farm).

## Dispose (same as eval, now gated on the board)

1. **WOMB landed 2026-09-24** (this CCr sid, token 8): `cosmos_womb.py` reads `orthogonality` first; NaN/inf/neg budget `BAD_INPUT`; DEFINE/GITUR/ROW_FIELDS patched. Selftest **12/12**. Live `seat(axis=coding)` **MEASURED** `seed-2.0-mini` + `qwen3-8b` orth=0 mag=9.5 on 619 obs. Core GET `/womb/seat` still the **old** module until bounce (`FORGED_EVENT`). **hook_trial not landed.**
2. **Do not call** WO-031/035/037/043/887/778, cDeck porosity CHECK/TEST, Phase 1 pairs, wish-34, n=581 as-is.
3. **Then** log lock → TLS+/kill → SpendGate UNPRICED=CALL_EST (not the Review-tab WOs).
4. Ledger/0-byte key **after** FORGED_EVENT.
5. Rest of Phase 2/3 unique KEEP (session-tools verbs, factory propose, meters UI) can run **in parallel** — they don’t write T.

CCr `--accept` only. No `O:\` copy onto `V:\A\Ai\COSMOS`.
