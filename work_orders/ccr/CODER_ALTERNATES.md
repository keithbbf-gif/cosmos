# CODER ALTERNATES & 3-STRIKE ROTATION LADDER

Governs automatic seat rotation when a CCrew coder encounters 3 consecutive failures
(HTTP 404, rate limits/429, empty output, or invalid syntax).

## 3 tries, then close (Keith 2026-09-24)
Same HERO session. Fail 1 and 2: scar + xFORM tail. The stage-1 prompt is not rewritten.
The third fail closes that session (`cosmos_duds.ATTEMPT_CAP = 3`) and files a new HERO only when its outfit is complete. Otherwise `hold_no_duds`. No Judge. No as-is retry.
A server or deprecated error closes on the first hit.

The alternate table below is the next HERO's outfit, not a silent rotate that skips the close.
3. The alternate is matched by:
   - **Context Window:** must meet or exceed 1,000,000 tokens (all non-Cloudflare hosts).
   - **TPS Band:** matched to comparable throughput.
   - **Orthogonality:** maintains family diversity across the active pair/triple.

## Alternates Matrix

| Primary Coder | Family | Ctx | TPS | 1st Alternate | 2nd Alternate | Matching Rationale |
|---|---|---|---|---|---|---|
| `glm` (z-ai/glm-5.3-flash) | zai | 1M | 33 | `qwen` (qwen3.8-flash) | `qwen-omni` (qwen3.8-omni) | Same 1M ctx; fast speed (33–48 t/s); high reasoning. |
| `gf38` (gemini-3.8-flash) | google | 1M | — | Joanna Vertex (same model) | `gemini-2.5-flash` | Automatic failover to Joanna vault project; then 2.5 Flash. |
| `ds0731` (deepseek-v4-flash-0731) | deepseek | 1M | 25 | `ds0423` (deepseek-v4-flash) | `ds41` (deepseek-v4.1-flash) | Same deepseek family; disk-backed cache; 1M ctx floor. |
| `grok` (grok-4.6 CLI) | xai | 131k | — | `grok-4.7` (local CLI) | `grok-4.7-build-fast` | Uses SuperGrokHeavy quota only. Never Cursor credits. |
| `qwen` (qwen3.8-flash) | qwen | 1M | 48 | `qwen37` (qwen3.7-flash) | `qwen-omni` (qwen3.8-omni) | 1M ctx; top speed; high agentic score. |
| `muse13` (muse-spark-1.3) | meta | 1.05M | 80 | `llama` (llama-4-maverick) | `mistral` (codestral-2508) | High context; fast throughput. |
| `mimo-flash` (mimo-v2.6-flash) | xiaomi | 1.05M | 12 | `ling` (ling-3.0-flash) | `mistral` (codestral-2508) | Faster substitutes replace 6 t/s models. |
| `nemo-ultra` (nemotron-3-ultra:free) | nvidia | 1M | 17 | `nemo35` (nemotron-3.5:free) | `qwen27` (qwen3.8-27b:free) | Free tier replacement; 1M ctx floor. |

## Data Trail & Porosity Pipeline

### Where Every Field Is Saved:
Every trial is persisted to `live/state/porosity/trials/<trial_id>.json` and the SQLite database:
1. `model`: exact served model ID from response header/payload.
2. `hero_pack`: path to applied HERO pack (`hero_coders/<dir>/PACK.toml`).
3. `prompt_tokens` & `cached_tokens`: measured per API return.
4. `output`: raw generated diff/code + sha256 digest.
5. `grades`: Judge verdict (`KEEP` | `DROP` | `HOLD`), `score_base`, `score_hero`, `who_erred`, `error_mag`.
6. `xfer_function`: extracted error analysis from `fails_of()` when re-prompting.

### Who Calculates Porosity & Orthogonality?
- **NOT WOMBAT.** WOMBAT authors work orders, seeds prompts, and manages the board. WOMBAT never grades or computes math.
- **No Judge is seated.** Harvester (`_porosity_pair_save.py`) stores pair rows. Do not paint KEEP.
  - **When:** Step 6b of every factory cycle (`_ccr_cycle.py`).
  - **Judge Input:** Blind pair A vs B.
  - **Judge Output:** `who_erred` (`a` | `b` | `both` | `none`).
  - **Math Computed:**
    - `Porosity` (co-failure rate) = $P(\text{both wrong})$
    - `Orthogonality` (diversity) = $P(\text{exactly one wrong})$
    - `Rescue` = $P(B \text{ correct} \mid A \text{ failed})$
  - **Destination:** Updated into `live/state/model_rater/porosity.json` matrix across all active pairs.
