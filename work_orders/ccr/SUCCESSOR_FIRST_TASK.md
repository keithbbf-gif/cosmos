# Successor CCr — first task (Keith 2026-09-10)

This session (sid `39d083c1`, grok pid **16628**) stays **open as backup**.
Do **not** spawn a second `grok.exe` while 16628 is live. One CCr lease.
Acquire `live/state/control/CCR.lease` on BootUP. Pen `V:\A`. Do not write `V:\Ai`.

Keith: resession the CCR; leave the old TUI as backup; first job for the
new agent is **patent → code integration**, pointed at Kelly review results
(not a cold 407k reread).

---

## First act (in order)

1. Read this file, `docs/CCR.md`, `docs/CODER_BRIEF.md`, `work_orders/ccr/CREW/IN/ELEGANT_PLAN.md`.
2. **Do not Gitur-publish** `CREW/IN/CODER_PRELOAD_PATENT_IDEAS_CACHE.md` (407,383 bytes, SHA256 `9E7C604D…`, `policy:patent-ideas-v1`). Gitignored. Unfiled IP.
3. Read the Kelly returns (this backup CCr fires them before you sit):
   - `work_orders/ccr/CREW/OUT/ELEGANT/gf38.json` — Kelly A `gemini-3.8-flash`
   - `work_orders/ccr/CREW/OUT/ELEGANT/gemini31pro.json` — Kelly B `gemini-3.1-pro-preview`
   - `_watch.json` — pids / spawn
4. If either JSON is missing or `ok` is false or `text` is empty: **do not invent a plan**. Wait or re-fire **Kelly Vertex only**. Do **not** send the patent preload to OpenRouter (GLM/DS/Sol) until Keith clears data-use.
5. Adjudicate (P10 / P02): merge subtract / keep / add. Write `CREW/OUT/ELEGANT/PLAN.md`. Dual-lane: they must not have peeked.
6. First Gitur BUILD = the top occupancy gap in that merged plan. One job, one branch `ccr/<job>`, one PR. Cosmos vs cDeck not mixed. Do not `git pull origin/main` onto unique COSMOS HEAD. Do not force-push.
7. Code the **embodiments**. Do not click USPTO. Do not post whitepaper/X/LI/arXiv. P12 HOLD. No 15th packet. Do not revive `P03_PUBLIC_TENSOR`. Do not invent porosity scores (`n_obs` stays honest).

---

## Hard fences (still in force)

| Fence | Rule |
|---|---|
| One CCr | This backup TUI until you take the lease. Then you are the writer. |
| Kelly first | Vertex `orders.ggn` `$300` expires 2026-12-04. Not Joanna. |
| No OR on this corpus | Patent pack stays off OpenRouter until Keith says. |
| No leftover PR merge | cdeck 6/16/17/68/102/108; cosmos 30/32/36/37/38/40/41/43/44. |
| No extra grok.exe | If 16628 is alive, it is backup. |
| GET never mkdir | GET `/forge` and GET `/crucible` 404 occupancy-correct. |
| Composer | pin `composer-2.5` only where already named. ANTHROPIC_OFF. |

---

## Preload (local only)

Desktop source and staged copy match:

- `C:\Users\Papa\OneDrive\Desktop\CODER_PRELOAD_PATENT_IDEAS_CACHE.md`
- `work_orders/ccr/CREW/IN/CODER_PRELOAD_PATENT_IDEAS_CACHE.md`
- 407,383 bytes · SHA256 `9E7C604DAE16BA862DE02B435FC3F58A756F39F6F42B041CC36ABC33A8F3A73F`

FILE P01–P11, P13, P14. P12 HOLD CN119168059B. Roadmap skeleton WS0–WS11 in that file §4.

GrokBot Legal handoff (already published, not the 407k pack): `docs/research/docket/GROKBOT_PATENT_SESSION.md`.
