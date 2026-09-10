# NOW — CCr sandbox (living)

**Successor pack (read this next):** `ccr/sandbox_notes/SUCCESSOR_ROADMAP.md`
— result of the six mouths, prompt paths, how to test the output, first Gitur job.

**Drive:** `V:\A\Ai\COSMOS\ccr\sandbox_notes`  
**Lease:** sid `39d083c1-caa1-4fd0-9881-fecfadbfcceb` grok pid **16628** (started 2026-09-05 20:36). Backup CCr. Do not extra grok.exe.  
**Core:** `:8770` `tree_id=KMesh-COSMOS-live` ready. Porosity GET `n_obs=0` `kind=UNMEASURED` schema `cosmos-porosity-tensor/4`.  
**Occupancy pin:** `builds/cdeck/test_kdash_working.py` **154/154** (was 152; this tick added PWA leftover + TAB SMOKE).  
**Dated dump:** `2026-09-10.md`

Keith 2026-09-10: *Keep your sandbox written to that drive as we go. Every
ephemeral idea and work product — you take notes. That's canon for all
future ORC and CCr sessions.* Path he named: `v:\a\ai\cosmos\ccr\sandbox_notes`.

---

## 2026-09-10 fire-all (Keith: prompts checked twice, then all coders)

Keith: *OK. Fire the review on all coders once you the prompts checked and double checked.*

**Checked twice before fire:**

| Check | Result |
|---|---|
| Kelly A/B | Already returned mouths (`gf38.json` / `gemini31pro.json`). **Not re-fired** (same fat prompt, $0.10 spent). |
| Cheap prompt | **Slice**, not 407k. `ELEGANT_SLICE.md` 11,107 bytes = preload §0–5 only (FILE/HOLD + WS0–WS11). Cut before `## 6. Source corpus`. No `SOURCE: SESSION_NOTE`. |
| Preload hash | Desktop = staged `9E7C604D…` still. Pack **not** attached to OpenRouter. Worker refuses if pack body appears in prompt. |
| System | `CACHE_RULE` + `ELEGANT_OR_SYSTEM.md`. **Not** `PREFIX.md` (pane-diff mouth). **Not** `GF38_MOUTH`. |
| Seat tag | Last line only. P02 no peeking. Identical prefix+task bytes. |
| Cut | Ling / Solar **not** fired. Luna is credit pin, not this ITEM. |
| Sol mouth | `max_tokens=8192` + `reasoning.max_tokens=2048` so content is not eaten. Last Sol was 1800 reasoning / 0 text. Empty content = `ok:false` `EMPTY`. |
| grok.exe | 16628 only. pythonw WMI. |

Keith: *I don't want them sliced* / *whole context* / *1M token models only* / *all preloads cache tagged.*

Keith: *GLM and Deep Seek are MORE than 1M they are 1.4* / *don't cut them - use them* / *Ling and Solar are cut on context and low COD scores.*

**P04 live emit this tick:** `tests/test_live_emit.py` **6/6** against Core `:8770` — `tree_id=KMesh-COSMOS-live`, porosity `UNMEASURED` `n_obs=0`, PWA `cdeck.webmanifest` 200 / KDash name 404, FILL_TABS from live `deck_tabs.js`, GET `/forge`+`/crucible` 404. Evidence `cosmos/_live_emit.json`. Occupancy still **154/154** (static). No ballot writer. No extra grok. No more OR.

**Farm DONE.** GLM + DS full-pack mouths on disk. Keith: cut **Luna Pro** as a seat (not a code change). Ling + Solar stay cut.

Use: GF38, Gemini 3.1 Pro, Luna Flex, Sol, GLM, DS V4. Do not use Luna Pro going forward. `*_slice.json` is not the review.

**Re-fired 1M only**, full 407,383-byte pack, each preload a separate `cache_control: {type: ephemeral}` part; Flex also `prompt_cache_breakpoint` on last cached part; `prompt_cache_key` hashes the fat bytes (not PREFIX.md alone). Tail (ELEGANT_TASK + seat tag) untagged.

| Seat | pid | window |
|---|---|---|
| Luna Flex | 59368 | 1.1M |
| Luna Pro Flex | 60012 | 1.1M |
| Sol | 47248 | GPT-5.6 major; same fat pack |

Kelly Vertex already has full-pack mouths. GLM/DS not on this fat call.

| Seat | ok | mouth | $ | note |
|---|---|---|---|---|
| GLM | true | 3248 | 0.000952 | 5-part plan |
| DS V4 | true | 4382 | 0.000932 | 5-part plan |
| Sol | true | 16770 | 0.061099 | **mouth present** (unlike prior Sol) |

No `BLOCKING` string. OR spend this wave ≈ **$0.063**. All five mouths on disk. Successor adjudicates. Ling/Solar not fired.

---

## What this mouth is doing

Resession the CCr **soon**. This TUI stays **open as backup**. Successor
first task = patent → code integration from **Kelly returns already on
disk**, not a cold 407k reread. File: `work_orders/ccr/SUCCESSOR_FIRST_TASK.md`.

Do not spawn. Do not sit ORC. Do not write `V:\Ai`. Do not USPTO. Do not
publish. Do not merge leftover PRs.

---

## Live emit this tick (not a claim)

| Probe | Result |
|---|---|
| GET `/api/v1/status` | 200 |
| GET `/api/v1/porosity` | 200 `n_obs=0` `kind=UNMEASURED` |
| GET `/cdeck/` | 200 264101 bytes |
| GET `/cdeck/cdeck.webmanifest` | 200 `application/manifest+json` |
| GET `/cdeck/sw.js` | 200 |
| GET `/cdeck/manifest.webmanifest` | **404** — occupancy-correct. KDash name is not cDeck. Do not alias. |
| `tests/test_cdeck_shell.py` | SELFTEST PASS 15/15 current; prechange discriminating failed |
| Sol `CREW/OUT/SOL_CRUCIBLE_REVIEW.json` | HTTP 200, **text empty**, reasoning 1800, **$0.028261**. No BLOCKING (no mouth). Do not spend more OR on Sol unless mouth is required. |

Chromium PWA re-probe still **blocked** (prior). Static + Core-serve pins stand. Do not invent a browser harness this tick.

---

## Kelly dual-lane (fired, returned, mouths present)

Fired pythonw WMI, Vertex Kelly only, no OpenRouter, no peeking.

| Lane | File | model | ok | in/out | cached | $ | mouth |
|---|---|---|---|---|---|---|---|
| A | `CREW/OUT/ELEGANT/gf38.json` | `gemini-3.8-flash` | true | 122002 / 5392 | 0 | 0.051833 | 19498 chars |
| B | `CREW/OUT/ELEGANT/gemini31pro.json` | `gemini-3.1-pro-preview` | true | 122007 / 2604 | 0 | 0.050342 | 8588 chars |

`cached_tokens=0` is the **first write**. Prompt ~411k chars = patent preload + ELEGANT_PLAN + ELEGANT_TASK. ELEGANT JSON gitignored (derived from unfiled pack).

**Adjudicate later (successor).** Both used subtract / keep / add / sequence / elegance.

Shared subtract: leftover PRs, GET `/forge`, GET `/crucible`, second Core, second grok.exe, invented scores, `P03_PUBLIC_TENSOR`, green-log as done.

Shared keep: one Core `:8770`, JSONL porosity authority, CCr one writer, Gitur triad, `cosmos_paths` sentinel, P13 Voice Drop, P14 PREFIX+CACHE_RULE.

Add (merge these, do not treat as filed claims):

1. **P07 Layer A vs B** — OS-restricted spawn token ≠ fencing token. GF38 named `cosmos_spawn_token.py` + `cosmos_fence.py`; 3.1 Pro named ledger + spawn profiles. **Do not invent IAM/AD.** Folder grant = pen.
2. **P11 bite-test** — pin old fail → mutate SEED mid-copy → `VERIFY_MISMATCH`. Do not claim "tests exist."
3. **P03 seating** — `obs.jsonl` sole authority; GET never mkdir; no embedding/"space" language.
4. **P02 peeking ban** — dual-lane BUILD still has **no ballot writer**. Do not invent one to green-log.
5. **P04 live-emit** — occupancy pins ≠ live emit. This tick's 404/200 PWA probes are the kind of emit P04 wants.
6. **P09 confirm-to-widen** — already occupancy; do not second-spend-Core.
7. **P14 precache** — ≠ US12596764 engine KV. Measure `cached_tokens`.
8. **P08 DOM** — TESS + Patent Public Search DOM still **owed**. Keith + Legal click USPTO.

**Kelly A error to refuse:** it wrote CCr pen on `V:\A\` **and** `V:\Ai\`. False. CCr = `V:\A`. GrokBot = `V:\Ai`. Two pens. Do not fold that.

Phasing both mouths agree: safety spine (WS0/WS1/WS4) → isolation+emit (WS2/WS8) → porosity+seating (WS3/WS9) → spend/DOM/resolver → ingress/precache/MOTIF.

---

## Patent preload (pointer only)

Desktop + staged copy match:

- `C:\Users\Papa\OneDrive\Desktop\CODER_PRELOAD_PATENT_IDEAS_CACHE.md`
- `work_orders/ccr/CREW/IN/CODER_PRELOAD_PATENT_IDEAS_CACHE.md`
- 407,383 bytes · SHA256 `9E7C604DAE16BA862DE02B435FC3F58A756F39F6F42B041CC36ABC33A8F3A73F`
- `policy:patent-ideas-v1`

FILE P01–P11, P13, P14. **P12 HOLD** CN119168059B. No 15th packet. Do not revive `P03_PUBLIC_TENSOR`. Gitignored. Cosmos **#123 MERGED** `ce79372` gitignored that file (did **not** contain the body). Unique local HEAD: do not `git pull origin/main` onto it.

Do **not** send that pack to OpenRouter (GLM/DS/Sol) until Keith clears data-use.

GrokBot Legal handoff (already published, not the 407k): `docs/research/docket/GROKBOT_PATENT_SESSION.md`.

---

## Ideas that did **not** ship (and why)

| Idea | Why not |
|---|---|
| Alias `/cdeck/manifest.webmanifest` → cDeck manifest | Invented KDash name on cDeck. 404 is correct. Pin the 404. |
| Chromium PWA re-probe | Blocked prior. Static + Core-serve is the emit this tick. |
| Fire GLM/DS/Sol on the 407k pack | Unfiled IP on third-party APIs. Kelly Vertex first. |
| Swap daily Luna for Luna Pro | Keith: no. Flex ½ off. `--seat luna-pro` is not a swap. |
| Merge leftover Cursor PRs | Named parked list. SHOW, never merge. |
| Extra grok.exe for successor | Keith leaves this TUI open as backup. Wait for him to start the new agent. |
| Invent porosity pair to un-UNMEASURED | `n_obs=0` is honest. |
| Ballot writer for dual-lane | Not occupancy. Do not invent. |
| Public digest / chain | TABLED `docs/research/docket/P03_PUBLIC_TENSOR.md`. |

---

## Crew (setup, not a farm right now)

| Seat | Pin | Wallet | State |
|---|---|---|---|
| GF38 | `gemini-3.8-flash` | Kelly Vertex $300 / 2026-12-04 | Elegant plan **returned** |
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | same Kelly | Elegant plan **returned** |
| GLM | `z-ai/glm-5.3-flash` | OpenRouter | Cheap pair; **off** patent pack |
| DS V4 Flash | `deepseek/deepseek-v4-flash-0731` | OpenRouter | Cheap pair; **off** patent pack |
| Sol | `openai/gpt-5.6-sol` | $10 OR major | Ran earlier, **empty mouth**. Do not restorm. |
| Luna / Luna Pro | Flex | credit | Daily credit; not this corpus |
| Ling / Solar | — | — | **Cut** (window/quality) |

FARM_PROCS for elegant seats: **0** (done). Health/Core pythonw still resident. grok **16628** only.

---

## Next (successor, or this backup if Keith says keep coding)

1. Read this file + `SUCCESSOR_FIRST_TASK.md`.
2. Merge Kelly A+B → `CREW/OUT/ELEGANT/PLAN.md` (local, gitignored folder).
3. First Gitur BUILD = Phase 1 safety spine **or** the next defined occupancy leftover. One job one PR. Cosmos vs cDeck not mixed.
4. Keep writing **this folder** as you go. Dated copy when NOW fattens.
5. Do not extra grok. Do not leftover-merge. Do not OR on the patent pack.

Gitur this tick (blob from origin, not unique HEAD):

- cosmos **#124 MERGED** `30c9a42` — `ccr/sandbox_notes` + canon pointers + shell 15 named
- cDeck **#114 MERGED** `be36ffe` — occupancy **154** PWA leftover + TAB SMOKE

Do not `git pull origin/main` onto unique COSMOS HEAD. Product cDeck `main` is `be36ffe` after #114.
