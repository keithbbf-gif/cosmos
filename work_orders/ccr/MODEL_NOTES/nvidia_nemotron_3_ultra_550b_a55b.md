# nvidia/nemotron-3-ultra-550b-a55b

Status: **SEATED** (best: ACTIVE, FAIL-mouth; 4 attempts; sets: FIZZ70, V4)

## Catalog (OpenRouter author page)
- Context: 262144 · released: 1780551208
- Price: in $0.6/M / out $2.4/M
- Params: frequency_penalty, include_reasoning, logit_bias, max_tokens, min_p, presence_penalty, reasoning, reasoning_effort, repetition_penalty, response_format, seed, stop

## Harness
- Door: openrouter (default)
- Flags that won/worked: --routing off --ping nemo-ultra, --routing off --prefill-none, --routing off --prefill-none +short-task, --routing off --routing off

## Scars observed
- fizz-16lines-ok lines=16
- lines=1 first='Done. The `fizzbuzz.py` file outputs the'
- lines=15 first='1'
- sku=nvidia/nemotron-3-ultra-550b-a55b

## History
Full rows: BAKEOFF70.jsonl (`"model": "nvidia/nemotron-3-ultra-550b-a55b"`).
Packs: hero_coders/ stubs or tmp/bakeoff70 copies. Never edit hero_coders originals.
