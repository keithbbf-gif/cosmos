# Prompt_style — TEMPLATE (copy to STYLES/<vendor-model-slug>.md)

Cache-stable. No dates. No UUIDs. Append after WRAP. Do not rewrite PREFIX or WRAP.

Slug: replace this file's name with the OpenRouter id, `/` → `-` if needed (`deepseek-deepseek-v4-flash-0731-free.md`).

1. First line of the answer is `NONE` or `diff --git` (CODER) / `ITEM` (WOMBAT) / `KEEP|DROP|...` (JUDGE).
2. If this model essays before the form, the xfer is this file — not a new PREFIX.
3. If ctx < 400k (Model Rater PRELOAD_POLICY), house pack only.
4. If HTTP 429, xfer `rate_limit`: backoff, next GAC slug. If 404, dead slug. If 403, skip/key scope.
5. Measured quirks go here as numbered lines. Do not duplicate WRAP.
