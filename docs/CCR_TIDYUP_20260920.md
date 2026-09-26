# CCr TidyUP / TidyUP2 — 2026-09-20

Durable record. Not a dump. Pack: `live/state/session_saves/20260920T084628/`.

## TidyUP

`cosmos.py session close` **failed**. Kernel would not load:

`LedgerError FORGED` — `live/ledger/authority.jsonl.head.json` HMAC does not verify.

Fail-closed. Did **not** repair in place. Existing `SEED.json` (len **10878**, mac `5e7805c6…`) copied into the pack. Never unlinked.

## TidyUP2 (re-measured)

| check | result |
|---|---|
| Live-emit | **6/7** PASS. Porosity **MEASURED n_obs=619** (test still wants UNMEASURED 0). |
| Occupancy | **CRASH** — `cosmos/cosmos_session_tools_kit.py` missing. |
| HEAD | **dbd29ca3**. Do not pull origin/main from this sit without Keith. |
| Ledger | **FORGED** head. Close blocked. |

## What is worth keeping

**Pipeline (decided)**  
Coders send a pair. Luna keep/drop, then Gitur files keep. **CCr is after Gitur** — last check, then write the live tree. Not the serial grader.

**Luna 700k**  
Cached codebase for the grader. Rebuild **every 30 minutes** while she is grading. Not every 30 seconds. Empty pile = do not call her.

**Spawners**  
Two mouths. **One-minute clock**, jobs spread across that minute. 10/min each = 20/min assign. Grade will lag. Dest files wait in order. That is fine.

**Board (last honest count)**  
906 jobs. ~1965 dests with code. 250 singles numbered `MATCH.md` (`WO-NNN` + keeper path + `WO-NNN-<seat>-R`). Skip singles until the second seat is in. ~2000 dests still ungraded. Score book: 3 keep (old), 251 drop. Gitur got none of this farm (drops).

**Luna “not grading”**  
She was. Scorekeeper wanted a `JUDGE` JSON table. She wrote `DROP qvl8-001 — 1/10`. Parser fixed. Those drops are in `scores.jsonl`. She is **not done** the pile. Grader **stopped** so we do not empty-hit.

**Money (last complete 2026-09-15T20:45Z)**  
Running **$224.82**. OpenRouter extra **$85.49 / $90 (95%) ALERT**. Gemini extra **$128.45 / $185**, $1.05 under 70%. Empty Luna hits were the 189M cached-token day.

**Never overwrite**  
Old copy → `_delme/<name>-001`. Live name stays the pointer.

**Resession scar**  
5a inject exits. 5b must open the **same** id. Session names: `yyyyMMddTHHmm-CCr-resession`. Ticks on the Grok TUI line, not OpenWork.

**Understudy if Luna is out**  
DS V4 Flash 0731 is under Luna Flex price, slower. GLM 5.3 Flash is faster and just over the Flex line. Speed on the grader seat is **untested**.

## Not this pass

No successor window spawned (Keith asked TidyUP + TidyUP2 + durable save, not 5a+5b). No ledger repair. No 30s Luna. No cap rewrite.
