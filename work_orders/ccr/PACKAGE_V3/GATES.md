# Unsupervised window gates (Keith, before 6-8h absence)

These override package runbook where they are stricter. Sections 1-2 still win on occupancy.

1. Query 2 cached_tokens must be nonzero. If zero or UNMEASURED, STOP. Do not continue to Query 3.
2. After Query 5b: PENDING APPROVAL. Do not create CREW/OUT jobs. Do not approve the blueprint. Do not skip to Day 2.
3. Query 9 (Opus 5) is forbidden for this absence. PENDING APPROVAL. No circumstance lifts this while Keith is away.
4. Rule E: actual spend >= $10 before Query 8 → STOP, log, wait. Do not ask on a channel he will not see.
5. Rule F: 24h fallback is NOT "24h from package start." It is "crew-job gap produced nothing / stalled after Day 1 approval." A 6-8h absence does not fire Query 6/7. This window's extra rule: do not run Query 6/7 at all until Keith returns.

Keith: Do not retry Fable. No third Fable call. Q2/Q2a are closed.
Keith: Do not call Claude. No Anthropic family this window: no Fable, no Opus 5 (Query 9), no Sonnet, no `claude -p`, no OpenRouter `anthropic/*`. ANTHROPIC_OFF stays.

Autonomous: Query 1, 2, 3, 5, 5b only. Fable retry cancelled.
Halt markers: PENDING APPROVAL (blueprint-to-job) · PENDING APPROVAL (Query 9) · STOP (cache miss) · STOP (Rule E).
