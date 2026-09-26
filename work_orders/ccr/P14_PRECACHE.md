# Gitur BUILD — P14 precache gate (PLAN.md E2)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/p14-precache` from GitHub `main`.
Measure cached_tokens. NAKED_FIRST_QUERY / FABRICATED_CACHE_HIT. Not a new Core module.
Reuse cosmos_openrouter_rail cache_family. Not engine KV cache.

## Bite
Untagged first query is NAKED_FIRST_QUERY. Claiming a hit without cached_tokens is FABRICATED_CACHE_HIT.
