# CCrew pack smoke — 2026-09-24 after fixes

Fixes: pin `xiaomi/mimo-v2.5`; pin `openai/gpt-6-luna`; `:free` `--routing off`; class-6 `--prefill-none`; STYLE first-line MUST NONE.

## ACTIVE (first line NONE, or Hy3 prefill+HERO_OK)

1. Nex Mini `:free`
2. Nex Pro `:free`
3. North Mini `:free`
4. Nemo 3.5 Lightning `:free` (prefill)
5. Nemo Super `:free`
6. Ling Flash (`opencode`)
7. Ling VL **paid** (prefill)
8. DS 0731
9. DS 0423 (prefill)
10. Qwen 3.8 Flash
11. Solar Pro4
12. GLM Flash (OR)
13. GF38 (OR)
14. Seed 2.0 Mini
15. GPT-OSS 20B
16. Codestral 2508
17. MiMo v2.5 (prefill)
18. Ministral 8B (prefill)
19. Hy3 preview (prefill ate NONE; mouth `HERO_OK`)

## Still not

| Seat | Why |
|---|---|
| Gemma 26B/31B `:free`, Qwen 27B `:free` | 429 upstream pool |
| Ling VL `:free` | 404 |
| Inkling / Inkling-small `:free` | 403 harness |
| Nano Omni / Nemo Ultra `:free`, Luna 6 OR | 200 `response_model=None` |
| Llama 4 Scout | 404 |
| Muse 1.3 | 200 empty mouth |
| GLM `pi -p` | Pi no key (auth.json present; env not seen) |
| DS `dsh` | no key file |
| Grok CCrew | grok.exe refused this pass |

18–19 ACTIVE vs 8 before. Log: `CCREW_PACK_SMOKE.jsonl`.
