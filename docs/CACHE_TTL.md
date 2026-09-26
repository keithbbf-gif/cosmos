# Cache TTL by model family (all seats read this)

Recorded 2026-09-23. Governs prefix-cache survival for every seat's legend.
Rule everywhere: stable PREFIX bytes, varying ITEM tail; measure
`cached_tokens` per response; ~0 cached = prefix drifted, flag it.

| Family (models) | Default TTL | Max / configurable | Reset behavior |
|---|---|---|---|
| DeepSeek (V3, V4, Flash) | few hours | up to days (auto) | Disk-backed (NVMe): unused context evicted over hours/days by capacity |
| GLM / Zhipu (GLM-4, GLM-5+) | 5 min | up to ~1h (partner rules) | Sliding: exact-prefix hit resets the 5-min timer |
| Qwen / Alibaba (2.5, 3+) | 5 min | fixed per endpoint (~5m public cloud) | Sliding: longest-prefix match flushes/resets 5-min window on hit |
| Anthropic Claude (3.5, 3.7) | 5 min | up to 1h (2x cache-write cost) | Sliding: hit resets 5-min timer |
| OpenAI GPT-5.6+ (frontier) | 30 min | via `prompt_cache_options.ttl` (min 30m) | Sliding: alive 30m after latest write/reuse |
| OpenAI GPT-4o / legacy | 5–10 min | 1h max (dropped at 60m regardless) | Hard limit: cleared fast at peak, gone at 60m |
| Google Gemini (1.5, 2.0, 2.5) | 60 min | fully customizable (`ttl` / `expire_time`) | Fixed: expires on creation/update time, NOT on reuse |

## What this means for our seats

- **Judge Luna 6.0 (openai): 30-min sliding.** Fire grade batches back-to-back;
  gaps > 30m re-bill the ~3k prefix. 111 grades fit in a few windows.
- **Auditor Grok 4.7 (grok CLI):** single 30-batch call per summon — one
  prefix, one window; no TTL risk inside a call.
- **Scribe Muse 1.3 (meta):** long durable runs — re-assert prefix (lease check
  + manifest hash) routinely; treat any uncached turn as drift until proven.
- **CCrew GLM / Qwen pairs: 5-min sliding — tightest constraint.** Fire a/b
  arms of a pair within the same 5 minutes or the second arm re-bills prefix.
  Schedule pairs, not singles.
- **CCrew DeepSeek: hours/days, disk-backed.** Most forgiving; batch DS arms
  last in a window, they survive.
- **WOMBAT Luna 6.0 (openai): 30-min sliding.** ITEM authoring in sustained
  bursts; idle > 30m = re-prime with one cheap call before the batch.

## Optimum prefix per role (measured 2026-09-23)

| Role | Prefix (stable) | Size | Floor | Fits |
|---|---|---|---|---|
| WOMBAT Luna 6.0 | AGENTS.md (1.5kB) + TASK + canon § | ~2–3k tok | 1024* | 1 wish/call, stream 42 inside 30m |
| Judge SOL 6 | legend + verdict schema (CANON §4) | ~3k tok | 1024* | pair ~70kB avg (~18k tok) + prefix per call |
| Auditor grok-4.7 | legend ~2k + packets | **≤450kB/call** | n/a | **30-bin NEVER fits 128k window** (30 biggest pairs = 3.4MB): sub-batch 5–9 pairs/call |
| Scribe Muse 1.3 | lease check + manifest | ~2k tok | n/a | ceiling 786k; re-assert prefix per turn |
| CCrew | house ~100k / fat varies | 100–500k | 4096 GF38 / 5-min GLM+Qwen | fire a/b arms of a pair inside one 5-min window |

*6.0/Luna-6/SOL floors assumed 1024 from measured 5.6-luna family value —
confirm from first responses' `cached_tokens`, adjust file on evidence.
Grade-queue measured: 78 pairs 10–251kB (avg 68.5), 33 solos 5–311kB
(avg 41.3), all-111 ≈ 6.7MB. Judge calls stream; Auditor sub-batches.
