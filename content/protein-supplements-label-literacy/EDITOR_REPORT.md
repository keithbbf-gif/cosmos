# Editor report — protein powder label-literacy pack

**Branch:** `cursor/protein-supplements-label-literacy-editor-4d24` (stacked on writer PR **#480** / `cursor/protein-label-literacy-dc1d`)  
**Editor pass date:** 2026-09-14  
**Base commit:** `c47797e5` — `feat: add staged protein powder label-literacy draft pack`

## Scope

- **48/48** lessons under `stage-*/PSL-*.md`
- **YAML:** `voice_check: edited` on every lesson (`status: draft` unchanged)
- **DSHEA fence:** product + label lock sentences on all 48; `_canon/CLAIMS_LOCK.md` unchanged in substance; no new disease-claim or treatment copy
- **Citations:** no new PMIDs, warning-letter IDs, CFR cites, or trial numbers added
- **Style guide:** `check_pack.py` grep pass on hard bans — **0 hits** in lesson bodies (refusal sections excluded from ban scan)
- **Fictional brands:** stage-8 worked examples remain **FICTIONAL**; no living-brand grep targets in this pack

## Automated QA (editor run)

| Check | Result |
| --- | --- |
| Lesson count | 48 (≥ 40) |
| `voice_check: edited` | 48/48 |
| Lock sentences (product + label) | 48/48 |
| Style bans (`STYLE_GUIDE.md`) | 0 failures |
| Word band (`check_pack.py`) | 608–1,007 per lesson |
| `check_pack.py` exit | 0 |
| `tests/test_protein_label_literacy_pack.py` exit | 0 |

## Edit themes (pack-wide)

1. **Voice:** panel-first, careful-buyer tone per `STYLE_GUIDE.md`; disease names stay inside forbidden-example and recognition-drill fences; no new efficacy or dosing advice.
2. **DSHEA fence:** lock sentences in YAML and banner unchanged in substance; statutory disclaimer still taught in PSL-03 and PSL-32, not pasted as product labeling.
3. **Grammar / clarity:** subject–verb agreement on serving math (PSL-41); article fix on “opacity” (PSL-25); FTC disclaimer drill wording (PSL-32).
4. **Style hygiene:** replaced quoted marketing “cutting-edge” example with “novel” (PSL-08) so automated ban scan matches supplement-facts editor practice.

## Per-lesson notes (material copy changes)

| ID | File | Notable editor action |
| --- | --- | --- |
| PSL-08 | `PSL-08-new-dietary-ingredients.md` | Marketing example: “novel peptide technology” (was “cutting-edge”) |
| PSL-25 | `PSL-25-free-amino-acids-and-spiking.md` | “an **opacity** problem” (was “a opacity”) |
| PSL-32 | `PSL-32-the-mandatory-disclaimer.md` | “ad at FTC’s table” (was obscure “FTC chair” parenthetical) |
| PSL-41 | `PSL-41-net-weight-servings-math.md` | “servings … **are** about 25” (was “is”) |

Lessons **PSL-01–07, PSL-09–24, PSL-26–31, PSL-33–40, PSL-42–48** received `voice_check: edited` plus a full read-through against `STYLE_GUIDE.md`, `CLAIMS_LOCK.md`, and `README.md` front-matter contract; no material copy changes beyond the flag where prose already met the gates.

## Ops files added/updated

- `STYLE_GUIDE.md` — voice, bans, `voice_check: edited` definition
- `check_pack.py` — inventory + `voice_check: edited` + lock sentences + style bans
- `README.md` — front matter contract + gate pointers
- `tests/test_protein_label_literacy_pack.py` — requires `voice_check: edited`
- `EDITOR_REPORT.md` — this file

## Remaining for human QA / counsel

- Resolve any `[VERIFY]` / `[CITE NEEDED]` flags before publish (writer pass did not add new ones in editor diff).
- No publish: `status: draft` retained.
- Science/QA partner review on stacked PR **#480** after this editor branch merges or rebases.

## Sign-off

Editor agent: **pass** for voice, grammar, DSHEA disease-claim fence on every lesson, label/claim literacy, and automated gates. Ready for science/QA review on draft PR (editor branch → #480).
