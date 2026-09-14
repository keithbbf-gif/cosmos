# Editor report — East Asian herbal pharmacopeias

**Branch:** `cursor/east-asia-herbal-editor-65d3` (editor pass on writer branch `cursor/east-asia-herbal-pharmacopeias-9821`, PR #307)  
**Editor pass date:** 2026-09-14  
**Scope:** `content/east-asia-herbal-pharmacopeias/` — 45 staged essays (`eahp-00` … `eahp-44`)

## Scope

| Item | Result |
| --- | --- |
| Draft essays | **45/45** under `drafts/` |
| YAML `voice_check: edited` | **45/45** (`status: draft` unchanged) |
| `MANIFEST.toml` | `voice_check = "edited"`, `editor_pass` set |
| Claims guard | No new efficacy, dose, or processing instructions added |
| House slop / unguarded clinical verbs (`check_drafts.py`) | **0 hits** in bodies |

## Automated QA (editor run)

```text
$ python3 content/east-asia-herbal-pharmacopeias/_editorial/check_drafts.py
essays: 45
words:  31642
median: 696
structure ok (still drafts; not a truth gate)
```

## Edit themes (collection-wide)

1. **Voice:** Preserved HOUSE essay voice (named books, offices, copies; limits marked with “I”). Trimmed TED-style uplift in `44-what-this-collection-cannot-do.md`; removed meta “cloud agent” phrasing in `02-the-claims-guard.md`.
2. **Claims / medical line:** Tightened administration and *paozhi* pointers so they cannot be read as instructions (`32`, `34`, `43`, `41`). Softened unguarded “indications change” (`21`). Clarified Tang promulgation as palace identity standard (`01`).
3. **Grammar / usage:** Article and agreement fixes (`35`, `28`, `30`, `14`, `29`).
4. **Romanization / terms:** *Sejong sillok* (`31`); *haneui* 韓醫 (`38`); incompatibility tables *shibafan* / *shijiuwei* (`41`); Nishi / Nakarai museum naming (`25`).

## Per-essay notes (high signal)

| id | File | Notable editor action |
| --- | --- | --- |
| eahp-01 | `01-what-a-pharmacopeia-is.md` | Palace-standard wording for Tang promulgation |
| eahp-02 | `02-the-claims-guard.md` | Reader-facing limit on library-only access |
| eahp-14 | `14-chen-cangqi.md` | “quotation tanks” phrasing |
| eahp-21 | `21-jinling-jiangxi.md` | Attributed uses in print, not clinical “indications” |
| eahp-25 | `25-ishinpo.md` | Nishi family / Nakarai catalog label |
| eahp-28 | `28-yamato-honzo.md` | Subject–verb agreement on picture *juan* |
| eahp-30 | `30-yakkyokuho-1886.md` | Count sentence grammar |
| eahp-31 | `31-hyangyak-as-politics.md` | *sillok* spelling |
| eahp-32 | `32-hyangyak-gugeupbang.md` | Approximate date; administration not reproduced |
| eahp-34 | `34-hyangyak-jipseongbang.md` | Gathering calendar framed as text’s ordinance |
| eahp-35 | `35-uibang-yuchwi.md` | An honest; witness-study wording |
| eahp-38 | `38-modern-cut.md` | *haneui* RR |
| eahp-41 | `41-poison-dose-upper-drugs.md` | Grade vs safety; incompatibility term graphs |
| eahp-43 | `43-three-modern-books.md` | *paozhi* as legal chapter, not instructions |
| eahp-44 | `44-what-this-collection-cannot-do.md` | Cross-ref to 32; problem-ending close |

Pieces **eahp-00, 03–13, 15–20, 22–24, 26–27, 29, 33, 36–37, 39–40, 42** received `voice_check: edited` and line-level polish where the pass touched adjacent files; no structural changes.

## Remaining for human QA / specialist pass

- Primary-book or diplomatic-edition check before any `status` promotion (per README and HOUSE).
- Resolve open questions and `SOURCES.md` gaps (Li dates, Kampo listing year, Goryeo colophons, JP crude-drug counts, etc.).
- Optional: extend `check_drafts.py` to require `voice_check: edited` on editor-complete passes.

## Sign-off

Editor agent: **pass** for voice, grammar, claims guard, and dose/efficacy boundary on this branch. Draft PR only; **do not merge** until specialist witness pass.
