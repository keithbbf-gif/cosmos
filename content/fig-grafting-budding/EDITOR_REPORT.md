# Editor report — Fig grafting and budding (Zone 8a)

**Editor pass:** 2026-09-14  
**Writer branch:** `cursor/fig-grafting-drafts-ef91` (PR #483)  
**Editor branch:** `cursor/fig-grafting-budding-editor-59d3`  
**Scope:** `content/fig-grafting-budding/stage-*/*.md` (50 essays) + pack README

## Summary

| Check | Result |
| --- | --- |
| Drafts touched | 50 / 50 |
| `voice_check` | `edited` on every draft |
| `last_edited` | `2026-09-14` on every draft |
| `validate.py` SLOP list | 0 hits |
| `status: staged` | Preserved on all drafts |
| `MANIFEST.toml` | **Not modified** (structure unchanged) |
| Net prose change | Targeted grammar, deduped research beats, light variety-stage weaving |

## Editorial method

1. **Voice** — Kept working-gardener 8a tone: phenology over borrowed calendars, chip-bud as weekday method, honest failure. No new cultivar claims or frost dates beyond what the writer already used.
2. **Deduping** — Shortened the late-August ISHS T-bud cite in the calendar draft so the budding stage keeps the full trial detail; varied mosaic “knife copies” closers between kit hygiene and failure chapters; trimmed repeated *palmata*/nematode and omega-bench jokes.
3. **Grammar** — Fixed `A 8a` → `An 8a` (and `a 8a` / awkward zone phrases) across aftercare, kit, scion, and budding pieces; `leaves is` → `leaves are` in union-timing draft.
4. **Stage 13** — Bridged scion-list headers with yard-test lines; tied ripening-ladder rungs to local weeks, not catalog weeks; softened doubled “religion” phrasing on closed-eye.
5. **Pack gate** — `validate.py` requires `voice_check: edited`, word floor, slop scan, and `A 8a` guard.

## Files with body edits (beyond YAML)

| Draft | Change |
| --- | --- |
| `01-01-zone-8a-year-on-the-knife.md` | ISHS August T-bud → cross-ref; keep detail in `08-02` |
| `02-02-latex-gloves-and-eyes.md` | `An 8a April session` |
| `02-03-sanitation-and-fig-mosaic.md` | Closing knife line de-duped from `12-02` |
| `03-02-converting-a-freeze-killed-top.md` | `April sun in 8a` |
| `04-03-green-wood-scions-in-summer.md` | `an 8a porch` |
| `05-02-stock-awake-scion-asleep.md` | `leaves are late` |
| `06-03-saddle-and-omega.md` | `An 8a note` |
| `08-01-chip-bud-the-reliable-one.md` | Living-of-habit scar; Jsacadura framing; `An 8a` morning/afternoon |
| `08-03-patch-bud-and-when-to-skip-it.md` | `LSU Purple`; shed-wall closing varied |
| `09-01-bench-graft-in-a-bucket.md` | Omega joke cross-ref; `late February in 8a` |
| `10-01-bags-shade-and-the-first-three-weeks.md` | Forum-villain phrasing; `an 8a soaker` |
| `10-02-when-to-unwrap-and-when-to-wait.md` | `An 8a habit` |
| `10-04-staking-brittle-fig-shoots.md` | `An 8a thunderstorm` |
| `12-02-mosaic-nematodes-what-you-imported.md` | *palmata*/nematode beat shortened vs `03-03` |
| `13-01-8a-scion-list-that-earns-a-slot.md` | Transitions between list blocks |
| `13-02-closed-eye-for-humid-8a.md` | `guarantee` / `habit` vs doubled `religion` |
| `13-03-multi-variety-ripening-ladder.md` | Local-week framing on early/mid/late rungs |

All other drafts: `voice_check: edited` + `last_edited` only (prose already met bar).

## Intentionally not changed

- `README.md` structure, stage table, contested-points canon (Eisen, chip vs T, *palmata*)
- `MANIFEST.toml`, draft IDs, slugs, titles, `related:` graphs
- Intentional short line breaks (house style for staged copy)
- No new drafts, no cuts to the 50-piece set

## Validation

```bash
python3 content/fig-grafting-budding/_check.py
python3 content/fig-grafting-budding/validate.py
```

## Sign-off

Editor pass complete: Zone 8a grafting voice retained, `voice_check: edited` set, structural validators green. Ready for human staging review; **not for merge** without Keith.
