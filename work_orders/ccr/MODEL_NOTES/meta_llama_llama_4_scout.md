# meta-llama/llama-4-scout

Status: **PARTIAL** (best: FAIL-404-dead-slug, HTTP; 10 attempts; sets: DEV, RETRY, RETRY2, V3)

## Catalog (OpenRouter author page)
- Context: 1310720 · released: 1743881519
- Price: in $0.1/M / out $0.3/M
- Params: frequency_penalty, logit_bias, max_tokens, min_p, presence_penalty, repetition_penalty, response_format, seed, stop, structured_outputs, temperature, tool_choice

## Harness
- Door: openrouter (default)
- Flags that won/worked: --ping llama-4-scout, --prefill-none, --routing off --ping llama-4-scout, --routing off --ping llama-4-scout --prefill-none, --routing off --ping llama-4-scout --prefill-none --max-tokens 4096, --routing off --ping llama-4-scout --prefill-none --max-tokens 4096 --reasoning-effort low, --routing off --ping llama-4-scout --prefill-none --max-tokens 8192, --routing off --prefill-none, direct

## Scars observed
- 404-dead-slug
- <empty>
- http=404 error='No endpoints found for meta-llama/llama-4-scout:floor. Every can
- {"error":{"message":"No endpoints found for meta-llama/llama-4-scout. Every candidate endpoint was removed during routin

## History
Full rows: BAKEOFF70.jsonl (`"model": "meta-llama/llama-4-scout"`).
Packs: hero_coders/ stubs or tmp/bakeoff70 copies. Never edit hero_coders originals.
