# Rights — ACT / mindfulness therapy history pack

Pack path: `content/act-mindfulness-therapy-history/`. Staged for WOW Therapies (`wowtherapies.com`). **Draft only** — not live-site canon.

## Policy (binding)

| Rule | Detail |
| --- | --- |
| Faces | **No AI-generated likenesses.** No synthetic “historical photographs.” |
| Living people | **No portraits** unless counsel clears a specific file with a written license chain. Default: **type plate** (`assets/_shared/series-featured.svg`). |
| Deceased people | **Public domain or Creative Commons only**, with a per-plate `plates/<id>/RIGHTS.md` row before `portrait_status: cleared`. |
| Workshop / publisher art | No hexaflex, body-scan maps, values sorts, DBT modules, or Guilford jacket scans without permission. |
| Diagrams | Original SVG timelines and maps in `graphics/` are **site-authored** (WOW Therapies educational series). |
| Stock | No “meditation group” stock. No retreat candids. No patient art. |

## File classes

| Location | License posture |
| --- | --- |
| `graphics/*.svg` | Original work; credit “WOW Therapies educational series.” |
| `assets/_shared/*.svg` | Original templates; no embedded likeness. |
| `plates/<id>/plate.jpg` | Must match that folder’s `RIGHTS.md` (`cleared` only). |
| `plates/<id>/plate.svg` | Placeholder or type plate; not a photograph. |

## Portrait census

Authoritative table: `PORTRAIT_SOURCES.md`. Graphics pass must not contradict it.

| Status in `PORTRAIT_SOURCES` | Featured image | In-article `<figure>` |
| --- | --- | --- |
| `no-portrait` | Series type template | Type plate or none |
| `confirm` | Series type template until cleared | Placeholder + link to `RIGHTS.md` |
| `cleared` (future) | `plates/<id>/plate.jpg` | Portrait `<figure>` with credit line |

## Re-verify on upload day

Commons and publisher terms change. Before WordPress import, re-open every `source_url` in plate `RIGHTS.md` files dated before the import.

## Contact

Rights questions block publish. Escalate to human editor + counsel before marking any living-person row `cleared`.
