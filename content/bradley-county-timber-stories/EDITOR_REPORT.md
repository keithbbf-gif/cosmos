# Editor report — Bradley County Timber Stories

**Pass date:** 2026-09-14  
**Base:** PR #318 (`0bd8ac0` — 44 staged essays)  
**Branch:** `cursor/bradley-county-timber-editor-7703`  
**Editor:** Cloud agent (EDITOR role)

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed | 44 |
| Drafts updated (`voice_check: edited`) | 44 |
| Pack meta files updated | 6 (`INDEX`, `MANIFEST`, `STYLE_GUIDE`, `BIBLIOGRAPHY`, `STAGING_README`, this file) |
| Meta “Ken Burns hour” in draft bodies (post-pass) | 0 |
| Hard-ban phrase hits in bodies (post-pass) | 0 |
| `commerce: false` on all drafts | 44 |

## What was fixed

1. **Ken Burns tone without documentary scaffolding** — Removed in-body references to “Ken Burns hour/grammar” and most “if this were a film / camera / voice-over” closers. Endings now use direct still language (hold the gate, the depot step, the blank card) per `STYLE_GUIDE.md`.
2. **Process talk** — Replaced “this series / the public pack / published pack” with county-record phrasing where it broke the fourth wall. Epistemic rules (“do not invent a roster”) stay imperative, not pack-meta.
3. **Front matter** — `voice_check: human` → `voice_check: edited` and `voice_check_date: 2026-09-14` on every draft and pack markdown file.
4. **Commerce** — Re-scanned for CTAs, catalog voice, and “our craftsmen.” No new commerce language added. Historical dollar figures (suits, depots, ADFA loans) unchanged as sourced facts.
5. **BBF** — No expansion of Bradley Brand Furniture asides; prior PR thinning preserved.

## Spot-check essays (heaviest edit)

| Slug | Note |
|------|------|
| `photographs-and-letters` | Film/meta grammar rewritten; honesty-about-gaps kept |
| `mill-town-america` | Closing capstone de-meta’d; sibling links preserved |
| `the-long-afterlife` | BBF paragraph kept non-commerce; “fabricated proof” wording |
| `names-on-the-time-clock` | Ken Burns line removed; list ending tightened |
| `when-the-hardwood-mill-closed` | 2008 gate close without film voice-over |

## Remaining weak spots

- **`[CITE NEEDED]`** — Council of 22 names, WWII dead roster, union record, filing-room roster, and others stay visible by design.
- **“We / do not invent”** — A few essays still speak as the historian’s contract (e.g. `joe-reaves-buys-timber`, `wartime-lumber`). Intentional fail-closed voice, not catalog copy.
- **Word band** — `MANIFEST.md` counts unchanged; no length expansion in this pass.
- **Duplicate facts** — Capstone `mill-town-america` still recaps reading order 1–43 by design.

## Not in scope

- No WordPress publish / WXR import.
- No changes outside `content/bradley-county-timber-stories/`.
- No merge (draft PR only).
