# Layer 7 — Enviro (house half of digs; city is Harness)

**cwd:** `V:\A\Ai\COSMOS\live\work\codex\hero-luna-587`  
**git:** detached `origin/ccr/canon-pen` — not `origin/main`. Isolated worktree. Not LiT.  
**pack:** house (the PR is 46 lines).  
**ctx (list, not ` · ` concat):** `docs/CANON_PEN.md` [read*], `TASK.md` [read*], `AGENTS.md` [read*], `work_orders/ccr/hero_luna/L1_ROLE.md` … `L7_ENVIRO.md` [read*].  
**wallet:** oa-api `live/config/openai_api_key.txt`. Not ADC. Not Kelly. Not Medicine Man. `--ignore-user-config`.  
**budget_out:** Flex $0.60/M (under $1). If Flex omitted: $1.20/M — report.  
**cache:** PREFIX = AGENTS.md + L1–L7 (no dates, no PR id, no UUID). Mission pack is tail. Floor 1024. First call writes. Measure `cached_tokens` / `cache_write_tokens`. TTL: 5.6 Flex aim 30m; in-memory 5–10 min idle if CLI sits an old SKU. Hit resets.  
**resume:** no BU/SEED inject on this Judge spawn.

## Output target (canon, in the DUD)

Role defaults for JUDGE fill **What**. **Size is computed at spawn**, after PREFIX (cache) and prompts are written:

| Knob | Meaning | This HERO default |
|---|---|---|
| **Where** | boxes only, never LiT | Mission pack fills paths |
| **What** | `text` \| `python` \| `no_prose` | `text` (KEEP/DROP/HOLD + findings). Not python-only. Not no_prose. |
| **Size** | MAX hard, OPTIMUM may float | `MAX = 1.1M − (cache + prompts) − 0.20×1.1M`. API `max_tokens` = MAX always. OPTIMUM floats unless expected return is known (then shoot it, ≤ MAX). |

`python` = unified diff / code block only, no wrapping essay. `no_prose` = machine record only (JSONL line). `text` = graded prose with required first line.
