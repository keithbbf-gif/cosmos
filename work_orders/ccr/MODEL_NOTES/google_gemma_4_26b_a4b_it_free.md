# google/gemma-4-26b-a4b-it:free

Status: **OPEN** (best: HTTP, SKIP; 28 attempts; sets: DEV2, DEV3, F1, F1R, FREE-CLOSE, GO9, RETRY, RETRY2)

## Catalog (OpenRouter author page)
- Context: 262144 · released: 1775227989
- Price: in $0/M / out $0/M
- Params: include_reasoning, max_tokens, reasoning, response_format, seed, temperature, tool_choice, tools, top_p

## Harness
- Door: openrouter (default)
- Flags that won/worked: , --ping gemma-4-26b-a4b-it:free, --ping gemma-4-26b-a4b-it:free --max-tokens 2048, --ping gemma-4-26b-a4b-it:free --prefill-none, --ping gemma-4-26b-a4b-it:free --reasoning-effort low, --ping gemma-4-26b-a4b-it:free --reasoning-effort low --reasoning-max-tokens 512, direct, direct - chat

## Scars observed
- <empty>
- VOID-invalid-pack-path-harness-bug | http-detail:<empty>
- http-detail:http=400 error='Only one of "reasoning.effort" and "reasoning.max_tokens" can be
- http-detail:http=429 error='Provider returned error'
- http=400 error='Only one of "reasoning.effort" and "reasoning.max_tokens" can be
- http=429 error='Provider returned error'
- pool-still-hot-or-dead
- pool-still-hot-revisit-within-hour

## History
Full rows: BAKEOFF70.jsonl (`"model": "google/gemma-4-26b-a4b-it:free"`).
Packs: hero_coders/ stubs or tmp/bakeoff70 copies. Never edit hero_coders originals.
