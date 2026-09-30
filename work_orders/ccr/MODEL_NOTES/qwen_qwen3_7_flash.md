# qwen/qwen3.7-flash

Status: **SEATED** (best: ACTIVE, FAIL-fizz, PASS; 5 attempts; sets: FIZZ70, V4)

## Catalog (OpenRouter author page)
- Context: 1000000 · released: 1785190561
- Price: in $0.03/M / out $0.13/M
- Params: include_reasoning, logprobs, max_tokens, presence_penalty, reasoning, response_format, seed, temperature, tool_choice, tools, top_logprobs, top_p

## Harness
- Door: openrouter (default)
- Flags that won/worked: --routing off, --routing off --ping qwen3.7-flash, --routing off --routing off, --routing off --routing off --prefill-none, --routing off --routing off --prefill-none --max-tokens 4096

## Scars observed
- fizz-16lines-ok lines=16
- fizz-lines=1 first='NONE'
- fizz-lines=15 first='NONE'
- fizz-lines=89 first='The user wants a specific output format:'
- sku=qwen/qwen3.7-flash

## History
Full rows: BAKEOFF70.jsonl (`"model": "qwen/qwen3.7-flash"`).
Packs: hero_coders/ stubs or tmp/bakeoff70 copies. Never edit hero_coders originals.
