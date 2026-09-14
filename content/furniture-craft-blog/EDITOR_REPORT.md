# Editor report — Furniture Craft Blog Pack

**Date:** 2026-09-14  
**Scope:** `content/furniture-craft-blog/drafts/` — 44 essays  
**Stacked on:** `cursor/furniture-craft-blog-623a` (parent pack PR [#251](https://github.com/keithbbf-gif/cosmos/pull/251))  
**Voice:** `voice_check: edited` on every draft  

## Method

- Read against `STYLE_GUIDE.md` banned list and magazine voice (shop-first openings, paid opinions, no throat-clear).
- Grammar, spelling, article usage (`a`/`an`), typos only where wrong; **no** stripping of `[VERIFY]` claims or figure front matter.
- Removed **verbatim duplicate** sections left from drafting (same anecdote or closer printed twice), merged near-duplicates into one passage where both sentences carried unique detail.
- Recounted body `word_count` after edits (text below closing `---` of YAML only).
- Graphics: preserved all `figures:` blocks; see `GRAPHICS_MERGE_NOTE.md` for merge-agent handoff (#235/#241).

## Banned-language scan

Post-pass grep on all drafts: **no hits** for delve, robust, leverage, unlock, Moreover/Furthermore stacks, “In conclusion,” “At the end of the day,” “key takeaway,” “Let’s dive,” etc.

## Substance and length

| concern | action |
|---|---|
| Duplicate closers / “notebook” sections | Cut duplicates only; kept first, stronger occurrence |
| Style guide target 1,200–2,000 words | Most essays remain in band; several sit **just under** 1,200 after dedupe (acceptable as complete essays) |
| `rubbing-out` | **1,000** words — complete argument; recommend **optional author expansion** (~150–250 words) if pack must strictly hit 1,200 — not padded by editor |

**Under 1,200 words (post-edit):** `24-rubbing-out` (1000), `25-old-paint-new-work` (1057), `30-cherry-changes-its-mind` (1072), `19-a-burnished-surface` (1132), `17-following-the-curve` (1162), `29-the-dark-board-in-the-stack` (1173), `26-ray-fleck-on-the-face` (1178), `23-color-without-a-lie` (1183), `06`/`09`/`13` (1182–1185).

Pack total after edit: **54,122** body words (was 55,844 pre-dedupe per prior manifest; recount aligned front matter to body copy).

## Per-essay change log

| # | file | body edits |
|---|---|---|
| 01 | `01-the-shoulder-is-the-joint.md` | batten; “century of mill work” |
| 02 | `02-waste-between-the-pins.md` | — |
| 03 | `03-a-chair-that-tries-to-walk.md` | — |
| 04 | `04-the-pot-on-the-hot-plate.md` | — |
| 05 | `05-the-pin-that-still-slides.md` | still moves |
| 06 | `06-the-drawer-that-does-not-bind.md` | dedupe June/feeler section |
| 07 | `07-a-wedge-you-can-see.md` | — |
| 08 | `08-the-open-mortise.md` | — |
| 09 | `09-room-to-move.md` | dedupe January oak door block |
| 10 | `10-a-thin-bit-of-hardwood.md` | — |
| 11 | `11-drawbore-then-drive.md` | caption: greedy (not proud) |
| 12 | `12-the-dovetail-that-travels.md` | — |
| 13 | `13-slurry-on-the-stone.md` | dedupe dished stone section |
| 14 | `14-the-shaving-that-tells.md` | trim redundant cap-iron line |
| 15 | `15-the-first-line.md` | — |
| 16 | `16-walls-you-can-trust.md` | — |
| 17 | `17-following-the-curve.md` | dedupe closing “nick” paragraph |
| 18 | `18-teeth-and-set.md` | — |
| 19 | `19-a-burnished-surface.md` | merge duplicate hook / end-grain closers |
| 20 | `20-what-the-cloth-leaves-behind.md` | an oily contaminant |
| 21 | `21-eighty-is-not-a-suggestion.md` | an arris |
| 22 | `22-the-cut-of-alcohol.md` | — |
| 23 | `23-color-without-a-lie.md` | raised panel; dedupe toner closer |
| 24 | `24-rubbing-out.md` | dedupe cure/nibs/hospitality repeats |
| 25 | `25-old-paint-new-work.md` | dedupe cupboard/chips closers |
| 26 | `26-ray-fleck-on-the-face.md` | an honest; century of mill work; drop redundant specifying section |
| 27 | `27-from-the-yard-to-the-room.md` | dedupe 1901 / truck paragraphs |
| 28 | `28-the-slats-come-off-warm.md` | dedupe short-grain under “Why a shop…” |
| 29 | `29-the-dark-board-in-the-stack.md` | batten plan; dedupe steamed walnut |
| 30 | `30-cherry-changes-its-mind.md` | dedupe UV/sap recap closer |
| 31 | `31-what-the-meter-says.md` | merge redundant meter anecdotes |
| 32 | `32-climbing-cut-tearout.md` | consolidate cathedral/glue/figured/teaching duplicates |
| 33 | `33-a-skin-of-better-wood.md` | dedupe apology / match closers |
| 34 | `34-the-knife-in-the-head.md` | merge historic-room anecdotes |
| 35 | `35-casing-that-meets-the-floor.md` | tighten floor-high; restore stain-grade handoff |
| 36 | `36-raising-the-field.md` | trim overlapping end-grain / catalog tail |
| 37 | `37-before-the-blade-turns.md` | cut redundant stick-away block |
| 38 | `38-the-elevation-on-the-shop-door.md` | merge stair/CNC; trim duplicate tail |
| 39 | `39-clamps-then-quiet.md` | one clamp-hunt anecdote |
| 40 | `40-the-bench-not-the-feed.md` | trim duplicate CNC/feed/stone |
| 41 | `41-a-jig-you-keep.md` | drop repeated cup/MDF section |
| 42 | `42-taking-a-piece-apart.md` | dedupe opening / refuse sections; brief refusal close |
| 43 | `43-the-iron-and-the-knot.md` | merge butterfly duplicates |
| 44 | `44-the-story-in-the-end-grain.md` | tighten pith/price/teaching tails |

**Essays with no body copy changes (voice_check + word_count only):** 02, 03, 04, 07, 08, 10, 12, 15, 16, 18, 22.

## Pack metadata updated

- `MANIFEST.md` — counts and `voice_check: edited`
- `INDEX.md` — status line and per-link word counts
- `GRAPHICS_MERGE_NOTE.md` — new (figures still `needed`)
- `STYLE_GUIDE.md` — editor note for `voice_check: edited` (if present in this commit)

## Recommended follow-ups (not editor scope)

1. Author pass on short essays if strict 1,200-word floor is required for publication.
2. Graphics merge per `GRAPHICS_MERGE_NOTE.md`.
3. Resolve open `verify:` bullets on the Wilmar/Warren floor before `ready` status.
