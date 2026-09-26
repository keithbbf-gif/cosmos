# L2 — Final Auditor Model & Lane

- **Model:** `grok-4.7` via **local `grok.exe` CLI (verified on PATH,
  listed by `grok models`). NOT the API lane.** Effort **High**
  (`--reasoning-effort high`).
- **Family law:** MUST differ from the Judge family. Judge is `openai`
  (gpt-6-luna) => Auditor is `xai`. If Judge ever rotates to Grok, Auditor
  auto-swaps lanes (never grade your own family's work).
- **Prompt caching (grok):** keep the legend PREFIX bytes identical on every
  call of a batch; ITEM/audit-packets go in the tail. Stable prefix = cache
  hits; churning the legend = full re-bill. (Ref: OpenRouter grok
  prompt-caching guide.)
- **Mode:** strict verification, temperature 0.1. Missing test proof or
  forbidden-path touch = REJECT.
