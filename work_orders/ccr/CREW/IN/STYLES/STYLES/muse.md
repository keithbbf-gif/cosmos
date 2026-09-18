# Prompt_style — Muse Spark (OpenRouter `meta/muse-spark-1.2`)

Cache-stable. No dates. No UUIDs. **Append** after PREFIX; do not rewrite PREFIX.

Slug: `meta/muse-spark-1.2` (plain). Not `*-contributor` (measured HTTP 404 on 1.2-contributor). 1.1 and 1.3 exist; occupancy pin is 1.2 unless Keith names another.

Quirks (measured farm mouths, then style):

1. **Does not look at the live slice before inventing a handler.** Chamber mouth added `handle_chamber_post` when `cosmos_service.py` already routed POST `/api/v1/chamber` → `chamber_join`. Style: if the provided bytes already contain the path+verb, first line is `NONE`.
2. **Truncates multi-file diffs** mid-function (`loadChamberPres`). Style: one file per mouth or close every hunk. Unclosed `@@` = invalid.
3. **Invented occupancy** (`163` → `166 pass`). Style: never emit a pin count. Fold strings into an existing check. Extra panes in `deck_*.js` not `app.js`.
4. **Invented line numbers** (`@@ -242`) not in the pack. Style: quote a live line from the ITEM/pack; if you cannot find it, `NONE`.
5. **Fast + reasoning** (~13s chamber, ~1.4k reasoning tokens) still duplicate. Speed is not a KEEP. Style: GF38 mouth rules 1–5 apply: first line `NONE` or `diff --git`; then 3 VERIFY lines.

House pack (no patent) unless the shared three-seat rotation pack is the job pack — then this file is **tail-only** so the cache family stays.

Do not vendor OpenHands. Do not spawn grok.exe. P10 propose.
