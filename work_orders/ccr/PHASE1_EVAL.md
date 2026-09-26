# Phase 1 eval → Phase 2 changes (2026-09-24)

16 arms: 4 pairs × (Gitur + North + Nex + Hy3-preview). Receipts: `live/work/phase1/`.

## Score

| Arm | n | Result | Grade |
|---|---|---|---|
| Gitur grok-4.6 | 4/4 launched | HTTP 201 RUNNING, **no PR yet** (`poll: false`) | **HOLD** harvest |
| Hy3-preview | 4/4 HTTP ok | P1: NONE + honest UNMEASURED. P3: NONE + UNMEASURED/none. P2/P4: bare `NONE` | **KEEP** shape; **thin** on P2/P4 |
| North `:free` | 4/4 HTTP ok | Tool-call soup (`<library>`, `<files>`). First line not NONE/diff | **DROP** as coder mouth |
| Nex paid | 4/4 REFUSED | Pin list has `nex-agi/nex-n2.5-mini:free` only. Runner asked paid; rail tried `:floor` | **DROP this slug**; pin `:free` next time |

No 4Cs FILE blocks. Judge SOL stays **HOLD**.

## What Phase 1 proved
- Restated tasks work: Hy3 refused to invent cDeck holes without a running UI.
- Core bounce closed P4’s old “FORGED restart” story; Hy3 P4 NONE is consistent with that.
- OpenRouter chat ≠ a coding harness for North Mini.
- WOMBAT crew Nex is **mis-pinned** (paid vs `:free`).

## Phase 2 — required changes

1. **Do not re-call P1–P4 clones** in the 100: n=501 (selector/TODOs), 502–503/507/509 (resize), 504+511–518/520 (runtime-binding). Same holes Gitur is already running. Wait for those PRs, then one leftover bite max.

2. **Collapse runtime-binding to one WO.** Core is up (pid 27336, chain VERIFIED). n=505 service wrapper = RESTATE leftover only, not a bounce.

3. **Hero pins before summon**
   - Nex = `nex-agi/nex-n2.5-mini:free` (never paid, never `:floor` on `:free`).
   - North = not a Phase 2 coder unless a tool-less / first-line gate is in the rail. Else skip.
   - Hy3-preview KEEP; refuse bare `NONE` (need line 2 reason).

4. **Gitur budget:** 530–552 Opus-5 flood stays HOLD. Phase 2 Gitur = unique KEEP only (519 commit+push, 524 GEM ping GF38). Don’t stack on the four RUNNING agents.

5. **Call list (unique, after Gitur harvest)**  
   KEEP: 519, 524 (gemini-3.8-flash), 553–567 minus DEDUP 556/559/560/561.  
   Skip TABLE/DEDUP/DROP/pile-568–592/wish gold 593–600 second copy.  
   Still ~**15–25** runnable, not 35–45, not 100.

6. **Judge:** still HOLD until a FILE block exists (Gitur PR diff or Hy3-class NONE+reason). Don’t mint SOL on North soup.

7. **Gate file:** `phase1.run` = launched; `phase2.status` = wait-gitur-harvest then unique KEEP.
