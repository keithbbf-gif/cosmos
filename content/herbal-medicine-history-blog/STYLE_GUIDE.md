# Style guide — history of herbal medicine, drugs, and supplements

- Voice: magazine history, not wellness marketing. Short sentences, dated anchors, named texts (papyri, pharmacopeias, statutes).
- Human voice only. Ban: delve, leverage, robust, seamless, tapestry, underscore, ever-evolving, “it’s important to note,” “Whether you’re…,” corporate triads, fake intimacy.
- Feature length: **≥700 body words** (front matter excluded); target 700–1200.
- Set `voice_check: human` when prose is filled. Keep `status: draft` until Keith clears publish.
- Use `era_focus` in front matter; verify uncertain dates with `[VERIFY]` in prose. Mark weak identifications **soft**.
- Citations array in YAML — writer fills; graphics agent does not invent references.
- Embed figures immediately after the H2 they support (`<!-- graphics-pack:v1 -->` block). Do not reorder those first two H2s, captions, or SVG paths.
- Front matter `figures:` lists relative paths from the article file (synced by `embed_graphics.py`). Keep the graphics-pack order.
