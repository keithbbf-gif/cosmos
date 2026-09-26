# WOMB pile — 157 failed + `_delme` wo-json, cap 400

Keith 2026-09-19: work those 157 plus the pile in `_delme` up to 400.

**Do not retry corpses.** Unique work after collapse is **80**, not 400. Cap 400 is the ingest ceiling; we classified the whole 949-file pile.

Ledger: `work_orders/ccr/WOMB_PILE_400.json`

## Measured

| Stack | Files | What |
|---|---|---|
| Live `failed/` | **157** | GET `/work_orders` failed=157 |
| `_delme` `wo-*.json` | **792** | dirty-clean 699 + cosmos-sync-lit 62 + drop_wo_before_github 31 |
| **Seen** | **949** | 157 + 792 |
| Empty Task | 447 | `_delme` copies with no Task |
| MOTIF clones | 224 | `Drive the MOTIF route…` + grok `--single` — **WD2 already does this** |
| Unique other | **80** | real DEFINE leftovers |

Live board still n_total=217 (failed 157 + assigned 35 + completed 25). Token economy = **bucket+picked**, not n_total. Bucket=0 picked=0.

## Disposition of 80 unique

| n | class | Action |
|---|---|---|
| 23 | restate | Collapsed to **14** six-field drops in `work_orders/drop/wo-20260919T01*-restate-*.json` |
| 10 | restate_gitur | Already `GITUR_*.md` — FIFO those packs, do not clone |
| 15 | superseded_lit | On LiT (plugin-waist, chamber, skill, recall, HITL, packets, Stagehand) |
| 6 | superseded_gitur | Runtime-bind / resume — no third rewrite |
| 6 | superseded_policy | Anthropic off; Composer CHECK; WOMBAT unseated; Judge=Luna |
| 11 | hold | Daytona keys, chatbot phone, OpenWork iframe, auto-push, CLOCKS observe, Crucible pin, Medicine Man |
| 3 | close | leftover list, GEM ping probe |
| 2 | cancel | repo-split; SUPERSEDES cancel |
| 4 | review | orch DEFINE leftovers (10-minute CCr status; duplicate orch-profile) |

## Gitur (open, unjudged — do not merge)

1. **PR #591** `ccr/fail-xfer` — fail_xfer JSONL + wo_partner + n_board. https://github.com/keithbbf-gif/cosmos/pull/591

## FIFO restated drops (attempt 2, list CTX, no grok.exe)

1. fail-xfer  
2. wo-partner  
3. judge-run (one fat prefix)  
4. judge-idle  
5. head-gate  
6. warn-x3  
7. orch-profiles  
8. session-tools  
9. auto-resession  
10. cDeck backlog  
11. query-channel RESEARCH  
12. DOM SGH/DeerFlow RESEARCH  
13. federation blockers RESEARCH  
14. Work agents RESEARCH  

Then existing `GITUR_WOMB_SEAT` / makers / learn-clock / CREATE ROLE / canon-spawn / harness-seat / Opus ledger.

## Not done this pass

- CCr stage of `live/state/work_orders/failed/` → `_delme/work_orders_failed/` (pen). After JSONL autopsy, projection n_total drops.
- Seating WOMBAT GF38 (after JUDGE + Coders 1–6).
- Firing Pi / dsh / OpenCode / Luna on these drops until Keith names them.
