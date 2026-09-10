# Successor CCr — result + roadmap (2026-09-10)

Read this after `NOW.md`. This backup TUI (grok **16628**, sid `39d083c1`)
stays open. Take `CCR.lease` on BootUP. Pen `V:\A`. Do not write `V:\Ai`.
Do not extra grok.exe while 16628 is live.

Keith: patent → code integration from **mouths already on disk**, not a
cold 407k reread. Sandbox stays `V:\A\Ai\COSMOS\ccr\sandbox_notes`.

---

## 1. Result (what this session actually produced)

Elegant dual-lane + 1M/1.4M full-pack review **returned**. Occupancy
**154/154**. Live-emit **6/6** (`tests/test_live_emit.py`, cosmos **#125**
`759c323`). Porosity GET still `n_obs=0` `kind=UNMEASURED` — honest empty.

**Use these mouths** (`work_orders/ccr/CREW/OUT/ELEGANT/` — gitignored folder):

| Seat | File | mouth | $ | note |
|---|---|---|---|---|
| Kelly GF38 | `gf38.json` | 19498 | 0.052 | Vertex full pack. **Refuse** CCr pen on `V:\Ai`. |
| Kelly Gemini 3.1 Pro | `gemini31pro.json` | 8588 | 0.050 | Tightest WS0–WS11 map. |
| Luna Flex | `luna.json` | 14315 | 0.016 | Occupancy-faithful. Cache write 108428. **No ballot writer.** |
| Sol | `sol.json` | 19452 | 0.324 | Mouth present (unlike earlier empty Sol). Critic. |
| GLM 1.4M | `glm.json` | 4531 | 0.012 | Compact table. **Refuse** ballot-writer stub. |
| DS V4 1.4M | `ds.json` | 8617 | 0.008 | “Mostly occupancy; four gaps.” Same ballot add — refuse that row. |

**Fired then cut (do not adjudicate from):** Luna Pro `luna-pro.json`.
**Never fired:** Ling, Solar (window + low COD).
**Not the review:** `*_slice.json` (sliced pass; Keith: whole context).

No `BLOCKING` string in any **use** mouth.

**Agreement:** one Core `:8770`, JSONL + `obs.jsonl` authority, CCr one
writer, Gitur triad, P12 HOLD, no GET `/forge`, GET `/crucible` 404, no
leftover PR merges, no 15th packet, no `P03_PUBLIC_TENSOR`, `n_obs=0` stays
UNMEASURED.

**Split (CCr takes Luna):** Luna = do **not** invent a P02 ballot writer.
GLM+DS = ballot writer is the first new code. Occupancy already says dual-lane
BUILD has **no ballot writer**. A ballot to un-UNMEASURED is invented
measurement.

---

## 2. Prompts (byte sources — do not rewrite to “improve” the cache)

### Stable preloads (cache-tagged on OR; Vertex used system + user pack)

| File | Role |
|---|---|
| `work_orders/ccr/CREW/IN/CODER_PRELOAD_PATENT_IDEAS_CACHE.md` | Full patent-ideas pack. **407,383 bytes**, SHA256 `9E7C604DAE16BA862DE02B435FC3F58A756F39F6F42B041CC36ABC33A8F3A73F`. `policy:patent-ideas-v1`. Gitignored. Never Gitur. Desktop twin: `C:\Users\Papa\OneDrive\Desktop\CODER_PRELOAD_PATENT_IDEAS_CACHE.md`. |
| `work_orders/ccr/CREW/IN/CACHE_RULE.md` | P11 prefix rule. |
| `work_orders/ccr/CREW/IN/CODING_GUIDELINES.md` | Seat guidelines (not occupancy). |
| `work_orders/ccr/CREW/IN/ELEGANT_OR_SYSTEM.md` | Plan mouth (not pane-diff `PREFIX.md` / `GF38_MOUTH.md`). |
| `work_orders/ccr/CREW/IN/ELEGANT_PLAN.md` | Same-prompt return shape: subtract / keep / add / sequence / elegance. |

### Volatile tail

| File | Role |
|---|---|
| `work_orders/ccr/CREW/IN/ELEGANT_TASK.md` | Patent → code map + live tree table. |
| Seat tag | Last line only (`_elegant_seat.py` Vertex; `_elegant_or_seat.py` OR). |

### How they were sent

- **Kelly Vertex:** full pack in the user turn + CACHE_RULE/guidelines in system. First write `cached_tokens=0`.
- **OR 1.1M/1.4M:** each preload a separate `cache_control: {type: ephemeral}` part; Flex `prompt_cache_breakpoint` on last cached part; `prompt_cache_key` hashes the **fat bytes**. Tail (task + seat tag) untagged. Luna write 108k; Luna Pro had a hit (seat **cut** afterward).
- **Workers:** `work_orders/ccr/_elegant_seat.py` (Vertex), `_elegant_or_seat.py` (OR), launchers `_crew_elegant.py` / `_crew_elegant_or.py`.
- **Index:** `work_orders/ccr/CREW/OUT/ELEGANT/INDEX.md`.

Do not Gitur the 407k pack. Do not send it again unless Keith says. Slice file `ELEGANT_SLICE.md` is leftover; do not re-fire slices.

---

## 3. Test the mouths before you Gitur (P04 / P10)

Do **not** merge plans by vibe. Each add-row must survive this gate. Write
pass/fail into `CREW/OUT/ELEGANT/PLAN.md` (that folder is gitignored — fine).

### 3.1 Live emit (already bound this session)

```
py -3.14 tests\test_live_emit.py
py -3.14 builds\cdeck\test_kdash_working.py
py -3.14 tests\test_cdeck_shell.py
```

Expect: live-emit **6/6**, occupancy **154/154**, shell **15/15** current.
Quote `tree_id=KMesh-COSMOS-live`. Porosity `n_obs=0` `kind=UNMEASURED`.
GET `/cdeck/cdeck.webmanifest` 200; GET `/cdeck/manifest.webmanifest` 404.
GET `/api/v1/forge` and `/api/v1/crucible` 404.

If any of those fail, **stop**. A mouth that wants mkdir-on-GET or a
ballot to fill `n_obs` is refused.

### 3.2 Per-mouth checklist (all six **use** files)

For each JSON: `ok==true`, `text` length > 200, five-part shape present
(subtract / keep / add / sequence / elegance). Record `model`, `usd`,
`cached_tokens` / `cache_write_tokens`. Empty text = failed review (the
old Sol crucible file is that class — ignore it).

Then, for **every Add item**:

1. **Quote a live line** in `cosmos/` or `builds/cdeck/` that the item
   claims to reuse. If you cannot find it → `UNVERIFIED_TREE` or drop.
2. **Contradicts occupancy?** Drop. Examples already judged:
   - Ballot writer (GLM, DS) vs live map “no ballot writer” + Luna subtract → **drop**.
   - CCr writes `V:\Ai` (GF38) → **drop**. Two pens.
   - Invented GET `/forge` or GET `/crucible` → **drop**.
   - Pair/score to un-UNMEASURED → **drop**.
   - P12 FILE / PDJ / 15th packet / `P03_PUBLIC_TENSOR` → **drop**.
3. **Bite exists or is named as pin-old-fail → fix → `_bite_`?** Keep only
   if the bite can run on this tree without a new Core.
4. **Elegance:** net complexity down. A new module that duplicates
   `cosmos_paths` / a second spend Core / a second grok.exe is refuse.

### 3.3 Merge rule

Intersection of **keep** + **subtract** across the six is the plan spine.
**Add** = items that survive 3.2 from ≥2 mouths **or** from Gemini 3.1 Pro
+ Luna when they agree. Sol is critic, not a second disposer.
Write the merge to `CREW/OUT/ELEGANT/PLAN.md`. Do not Gitur that file if
it quotes unfiled packet prose — keep local; Gitur only code/tests.

---

## 4. Roadmap (after PLAN.md exists)

One job, one branch `ccr/<job>`, one PR. Cosmos vs cDeck **not mixed**.
Blob from GitHub `main`. Do **not** `git pull origin/main` onto unique
COSMOS HEAD. Do not force-push. Do not merge leftover PRs (cdeck
6/16/17/68/102/108; cosmos 30/32/36/37/38/40/41/43/44).

| Phase | Packets | First concrete BUILD | Bite / live emit |
|---|---|---|---|
| **A — safety spine (do this first)** | WS0, P11, P07 A/B | Fail-closed SEED: pin old truncate/mid-copy → refuse `VERIFY_MISMATCH` / `OPEN_CONTEXT`. Then Layer A spawn grant ≠ Layer B fencing token. | Existing session/backup refusals; no new IAM. Folder grant = pen. |
| **B — isolation + truth** | P02, P04, P05 | Peeking ban in farm spawn (no shared scratch). Live-emit gate: DONE requires a value only `:8770` emits (`test_live_emit.py` is the pattern — extend, do not replace with CI green). | `PEEKING_VIOLATION` typed; missing emit refuses DONE. **No ballot writer.** |
| **C — measurement** | P03, P06 | Keep JSONL authority. GET never mkdir. COMPARE box$/token$ **only after** real `obs.jsonl` rows exist. Do not invent a pair. | Delete SQLite projection → GET rebuilds from JSONL; `n_obs=0` stays UNMEASURED until observed. |
| **D — spend / DOM / resolver** | P08, P09, P10 | Confirm-to-widen already occupancy. TESS/PPS DOM is Keith+Legal, not a coder USPTO click. Resolver identity mismatch already the rule — add bite if missing. | `409 WIDEN_REQUIRES_CONFIRM`; `IDENTITY_MISMATCH`. |
| **E — ingress / cache / loop** | P13, P14, P01 | Voice Drop is live. Precache SOP is live (`CACHE_RULE` + tagged preloads). MOTIF DEFINE-first gates when to precache. | Measure `cached_tokens`. Prefix byte-stable. |

P12 stays HOLD (CN119168059B). USPTO is Keith + Legal. GrokBot Legal
handoff: `docs/research/docket/GROKBOT_PATENT_SESSION.md`.

---

## 5. First Gitur job (recommended)

**P11 fail-closed SEED / backup verify** on `keithbbf-gif/cosmos`, branch
`ccr/p11-seed-bite`. Pin a predecessor failure (silent truncation or
mid-copy mutate still seals) → fix → `_bite_` `all_bite:true`. Do not
claim “tests exist.” Do not touch cDeck in that PR.

Second job: P07 Layer A vs B (spawn token ≠ fencing token). Same repo.
Still no ballot. Still no extra grok.

---

## 6. Fences (unchanged)

| Fence | Rule |
|---|---|
| One CCr | This backup until you take the lease. |
| Pens | CCr `V:\A`. GrokBot `V:\Ai`. No two streams share a root. |
| Seats | Use GF38, Gemini 3.1 Pro, Luna Flex, Sol, GLM, DS V4. **Cut** Luna Pro, Ling, Solar. |
| GET never mkdir | Forge/crucible GET 404 occupancy-correct. |
| ANTHROPIC_OFF | Composer `composer-2.5` only where already named. |
| Unique HEAD | Blob from origin. Never pull origin/main onto unique COSMOS history. |
| Sandbox | Keep writing `ccr/sandbox_notes/NOW.md` as you go. |

Kelly Vertex `$300` expires **2026-12-04**. Occupancy pin:
`builds/cdeck/test_kdash_working.py`. Live emit:
`tests/test_live_emit.py`.
