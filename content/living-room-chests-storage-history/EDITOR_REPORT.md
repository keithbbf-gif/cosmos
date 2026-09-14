---
title: Editor report — living-room chests and storage history
series: living-room-chests-storage-history
status: staged
voice_check: edited
channel: BBF
writer_pr: 485
alternate_pr: 496
editor_branch: cursor/living-room-chests-editor-d903
---

# Editor report

**Writer source:** GitHub PR **#485** (`feat: stage BBF living-room chests and storage history pack`, head `f51cb8a`).  
**Alternate pack:** PR **#496** (flat scratch folder, essays v1–v6, `41-final-candidate.md`, fact-check and claims index). **Not merged here.** Reconcile later if Keith wants a single long feature cut from #496’s `41` or borrowings from `40-fact-check.md` / `45-claims-index.md`.  
**This pass:** Stacked editor branch on #485’s tree. `voice_check` set to **`edited`**. Do not merge without Keith’s publish pen.

## Scope

| Area | Files | Result |
| --- | ---: | --- |
| Staged essays | 44 in `drafts/` | Line edit + voice pass |
| Apparatus | README, INDEX, MANIFEST, STYLE_GUIDE, BIBLIOGRAPHY, SHOP_GUARDRAILS, WP_IMPORT | Front matter / validator alignment |
| Machine check | `validate_staging.py` | Now requires `voice_check: edited` |

## Method

1. Read `STYLE_GUIDE.md` and `SHOP_GUARDRAILS.md` as the contract.
2. Ran `validate_staging.py` (word counts, YAML, banned patterns) before and after.
3. Scanned all draft bodies for banned list items (delve, leverage, game-changer, throat-clear closers, COSMOS, etc.) — **no hits in essay bodies**.
4. Ran `codespell` on `drafts/` — only false positives (finial, presse, NAM, Asai, planed).
5. Full read of frame essays (`01`–`04`), shop close (`44`), and spot reads across stages; full skim of remaining slugs for AI cadence and catalog voice.

## Prose changes (this commit)

| File | Change |
| --- | --- |
| `drafts/13-rosemaling-and-alpine.md` | “When **Pedersen** emigrated” → “When **he** emigrated” (owner named as Peder Tollisen Ryggsaas two sentences earlier; Pedersen was a slip). |

No other body edits. The #485 pack was already in shop-floor voice: artifact-led openings, qualified dates, `[VERIFY]` where the writer refused to fake certainty, closes that leave tension instead of recaps.

## Voice and AI-speak

**Kept as-is (intentional):**

- First-person bench talk, refusals, and qualified museum language.
- Repeated “I will not …” guardrails (series contract, not padding).
- `carcase` / `carcass` mix (British inventory habit vs American shop floor) — harmonize only if Keith wants one spelling everywhere.
- Essay cross-refs (“Essay 40 owns …”) in Notes — editor scaffolding for Keith, not reader-facing WP copy.

**Banned habits (STYLE_GUIDE):** not found in draft bodies.

## `[VERIFY]` flags left for Keith / camera

Still open in draft bodies (writer placed them; editor did not clear):

| Draft | Topic |
| --- | --- |
| `13-rosemaling-and-alpine.md` | Inscription dates; Lysne “father of rosemaling in America” as Vesterheim formula |
| `16-when-the-lid-lost.md` | Public accession for geometric oak chest figure |
| `21-chest-on-chest.md` | PMA chest-on-stand date; Townsend brass/bonnet at sale |
| `24-lowboy-left-the-bedroom.md` | (one verify line in YAML/body — see file) |
| `32-tansu.md` | Multiple museum/accession hedges |
| `39-midcentury-credenza.md` | Museum figure without named accession |

## PR #496 — reconcile later (do not delete)

#496 is a **different tree shape** (numbered flat files, multiple essay versions, `42-editor-letter.md`). Useful collateral for a future pass:

- `40-fact-check.md`, `45-claims-index.md` — cross-check against #485 claims (Bok, mule-chest 1911, La Muette, relocation thesis).
- `41-final-candidate.md` / `36-essay-v6-bbf.md` — single long feature if Keith wants one magazine piece instead of 44 stand-alones.
- `39-rejects.md`, `37-openings.md` — cut list and opening alternates.

**Canonical staged pack for this channel remains #485’s `drafts/` + apparatus** unless Keith says otherwise.

## Validator

After this pass:

```bash
python3 content/living-room-chests-storage-history/validate_staging.py
```

Expect: `OK  44 staged drafts, all 1100–1700 body words` and `voice_check: edited` on every draft.

## Recommendation to Keith

- **Publish path:** 44 essays as staged, or cherry-pick a subset by `INDEX.md` stage.
- **Before camera:** Clear `[VERIFY]` items called out in Notes (especially Bok issue date, commode dates essay `23`, Pickvance dendro ranges essay `08`).
- **Art:** Follow figure plans; no bowl-of-lemons staging (#496 editor letter still applies).

---

*Editor pass complete. Quality over speed; no merge.*
