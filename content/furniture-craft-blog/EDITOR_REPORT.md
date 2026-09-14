# Editor report — furniture-craft-blog

**Pass date:** 2026-09-14  
**Branch:** `cursor/furniture-craft-editor-6155` (based on `cursor/furniture-craft-graphics-99ed`)  
**Editor:** Cloud agent (EDITOR role)

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed | 45 |
| Drafts updated (`voice_check: edited`) | 45 |
| Hard-ban phrase hits (post-pass) | 0 |
| Figure embeds preserved | 45 |
| `graphic.primary` paths unchanged | 45 |

## What was fixed

1. **Stub boilerplate removed** — All 45 drafts shared the same opening (“working notes for the shop…”), identical “At the bench” copy (including mortise-specific “mark waste sides” on finish and dust-collection pieces), and one generic joinery checklist. Each article now has a topic-specific lede, bench section, and checklist aligned with its `meta_description` and figure caption.
2. **Front matter** — Replaced `voice_check: human` with `voice_check: edited` and `voice_check_date: 2026-09-14` on every draft.
3. **Ban list** — Scanned for delve, landscape, leverage, robust, seamless, underscore, tapestry, ever-evolving, “it’s important to note”, “Whether you’re…”, “In today’s…”. No matches in draft bodies after the pass.
4. **Preserved** — `<figure>` blocks, captions, `graphic.primary`, PHOTO slot wording, `D:\BBF` image paths, and all `../assets/...` SVG links.

## Remaining weak spots

- **Length** — Bodies are still short shop notes (roughly 120–180 words each). Fine for staged drafts with diagrams; a writer pass may want longer narrative where SEO depth matters.
- **Voice uniformity** — Openings follow a similar direct-shop tone. Intentional for the pack, but a few pieces (e.g. `french-polish-overview`, `choosing-hardwood-boards`) could use more first-person bench anecdote when photos land.
- **Checklist rhythm** — Most checklists are three bullets (topic-specific, not generic). Not symmetric fluff, but the three-bullet shape is still recognizable across the pack.
- **Species / numbers** — Movement and fit articles use shop rules of thumb (e.g. tangential ≈ 2× radial). No new joinery claims were added; numeric claims match existing figure captions.

## Articles that still risk “AI” read (lower confidence)

These read clean but are hardest to distinguish from templated craft copy without photos:

| Slug | Note |
|------|------|
| `shop-dust-collection-layout` | Generic shop-layout advice; needs a photo of the actual trunk/gates. |
| `torsion-box-shelf` | Correct but abstract until a grid glue-up shot exists. |
| `finishing-outdoor-furniture` | Policy-style (“refresh yearly”) — accurate, less sensory than finish how-tos. |

No draft was left with the pre-pass clone body. If any file still shows “Mark waste sides before any saw cut” outside joinery topics, treat that as a merge error — it should be zero after this pass.

## Not in scope

- No changes under other content packs.
- No publish / live WP actions.
- Graphics SVGs untouched (graphics branch remains source for diagrams).
