# thinkingmachines/inkling-small:free

Status: **SEATED** (best: ACTIVE, HARNESS, HTTP, MOUTH, SKIP; 19 attempts; sets: DEV2, DOOR, DOOR2, F1, FREE-CLOSE)

## Catalog (OpenRouter author page)
- Context: 1048576 · released: 1785443117
- Price: in $0/M / out $0/M
- Params: frequency_penalty, include_reasoning, max_tokens, presence_penalty, reasoning, reasoning_effort, seed, stop, temperature, tools, top_p

## Harness
- Door: openrouter / codex / opencode-agentic
- Flags that won/worked: , --ping inkling-small:free, --ping inkling-small:free --max-tokens 2048, --ping inkling-small:free --prefill-none, --ping inkling-small:free --reasoning-effort low --reasoning-max-tokens 512, codex exec --ephemeral -m <slug> (isolated CODEX_HOME), codex exec --ephemeral -m <slug> service_tier=flex (default HOME), direct - chat, opencode openrouter-provider, opencode openrouter/thinkingmachines/inkling-small:free

## Scars observed
- HARNESS_GATE SPAWN-FAIL FileNotFoundError: [WinError 2] The system cannot find the file specified ||| SPAWN-FAIL FileNotFoundError: [WinError 2] The system cann
- HARNESS_GATE no agentic door binds for inkling: OR-chat 403 + codex 400-not-supported; paid thinkingmachines/inkling is PINNED (VALUE lane)
- Line 1
- VOID-bad-binary-path-superseded-by-codex-iso/def | SPAWN-FAIL FileNotFoundError: [WinError 2] The system cannot find the file specified
- codex default HOME Flex/ephemeral: 400 The 'thinkingmachines/inkling-small:free' model is not supported when using Codex with a ChatGPT account.
- codex isolated CODEX_HOME: 401 Unauthorized Missing bearer (no login there)
- http=400 error='Only one of "reasoning.effort" and "reasoning.max_tokens" can be
- http=403 error='thinkingmachines/inkling-small:free is only available on agentic

## History
Full rows: BAKEOFF70.jsonl (`"model": "thinkingmachines/inkling-small:free"`).
Packs: hero_coders/ stubs or tmp/bakeoff70 copies. Never edit hero_coders originals.
