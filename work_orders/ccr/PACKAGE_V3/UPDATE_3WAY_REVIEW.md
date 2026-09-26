# COSMOS2 + cDeck — Package v3 UPDATE: Three-Way Review + Fable Retry Fix
FOR: Grok 4.6 / CCr — SUPERSEDES Query 2 in v3. Read alongside the original
package (Sections 1+2 preload/rules unchanged and still binding). This file
only changes the Review 2 step and adds a Review 2b step.

Source: https://drive.google.com/file/d/1P6R2xzD2SXZzp9bhBLvRV0Md67accYTT/view
Copied onto the live tree as directed.

---

## WHAT HAPPENED (context for the log)

Query 2 (original Review 2, Claude Fable 5.1) ran with cached_tokens=0 /
cache_write_tokens=11343 — expected on a first call to a new prefix, NOT
itself a failure. The real problem: actual cost was $4.7852 against a
modeled $1.92, and the response truncated at 16k output tokens before
finishing the tab survey or reaching a merge decision.

CCr correctly halted per the cache-hit discipline and did not proceed to
Query 3/5/5b. Total spend at halt: $4.9138 of $20.00 budget.

DECISION: Retry Fable 5.1 with corrected settings (Review 2a), AND add a
third independent model, Gemini 3 Pro (Review 2b).

---

## RULE B — UPDATED (three-way)

Review 1 (Sol), Review 2a (Fable 5.1, retried), and Review 2b (Gemini 3
Pro, new) must all run on genuinely distinct model families: OpenAI,
Anthropic, Google. Terra remains fourth-opinion tie-breaker only.

---

## CONFIGURATION FIX FOR REVIEW 2a (Fable 5.1 retry) — MANDATORY

1. Reasoning/thinking effort STANDARD or MEDIUM, not maximum/high.
2. Output ceiling at least 24,000 tokens (or split tabs 1-11 / 12-22).
3. Second call to identical cached prefix. cached_tokens must be nonzero.
   If zero again, STOP and report prefix bytes of both calls.
4. Do not change Sections 1+2 or CSM_prompt.md. Only ITEM params change.

---

## NEW QUERY 2b — Gemini 3 Pro (Google family)

Identical ITEM contract as Query 1 / Query 2. Confirm live OpenRouter slug
before firing.

Everything else from package v3 unchanged: Rule D, Query 9 Opus once-only,
Rule E spend ceiling, hold Query 6/7/8/9 until Keith returns.

END OF UPDATE FILE.
