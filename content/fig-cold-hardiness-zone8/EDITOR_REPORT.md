# Editor report — Fig cold hardiness (Zone 8a focus)

**Editor pass:** 2026-09-14  
**Writer branch:** `cursor/fig-cold-hardiness-zone8-2144` (PR #309)  
**Editor branch:** `cursor/fig-cold-hardiness-zone8-editor-c4ac`  
**Scope:** `content/fig-cold-hardiness-zone8/drafts/*.md` (50 essays)

## Summary

| Check | Result |
| --- | --- |
| Drafts edited | 50 / 50 |
| `voice_check` | `edited` on every draft (replaced writer `voice: human`) |
| `validate.py` SLOP list | 0 hits |
| `status: staged` | Preserved on all drafts |
| `_manifest.toml` | **Not modified** (structure unchanged) |
| Net prose change | Light grammar/line-break fixes; anti–cure-theater trims on wrap/garage pieces |

## Editorial method

1. **Voice** — Kept first-person 8a yard tone: temperatures, selective borrowing from Zone 7/9, no catalog warranties. No new variety claims or extension facts beyond what the writer already cited.
2. **No cure theater** — Softened lines that read like guaranteed outcomes (wrap physics, garage, tip-and-bury, “this is the wrap”) without removing honest anecdotes where the draft already names failure modes.
3. **Grammar / layout** — Fixed a misleading line break in `d17` (“nursery can”), paragraph split in `d41`, wrapped a run-on closer in `d29`.
4. **Front matter** — `voice_check: edited` on all 50; `STAGE.md` documents the field; `validate.py` now requires `voice_check: edited`.

## Files with body edits (beyond YAML)

| Draft | Change |
| --- | --- |
| `d17-in-ground-vs-pot.md` | Decision-tree intro: “nursery / can” line break → one clear sentence |
| `d24-the-leaf-filled-cage.md` | “Why it works” → “When it helps” + explicit non-promise; “this is the wrap” qualified |
| `d25-tip-and-bury.md` | “It works” → conditional “can hold wood when…” |
| `d29-a-winter-kit.md` | Closing paragraph line breaks |
| `d36-garage-protocol.md` | Garage “works” → “can work for pots” (room does not save wood) |
| `d41-polar-vortex-year.md` | Final paragraph break |

All other drafts: `voice_check` only (prose already met bar).

## Intentionally not changed

- `README.md`, `_manifest.toml`, draft IDs, stage/cluster tags
- Word-count floor (480+ words) — still passes; total ~26.7k words
- No new drafts, no cuts to the 50-piece set

## Validation

```bash
python3 content/fig-cold-hardiness-zone8/validate.py
```

## Sign-off

Editor pass complete: Zone 8a practical voice retained, cure-theater edges trimmed, `voice_check: edited` set, structural validator green.
