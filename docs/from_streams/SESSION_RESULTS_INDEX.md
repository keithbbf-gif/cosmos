# Session results — 2026-10-07

Saved from the dirty checkout. Nothing here was committed. The two Grok processes were left running. `CCR.lease` was not taken.

## Already on disk before this pack

| Result | Where |
|---|---|
| Eight topic outcomes and the 2026-10-07 retests | `V:\streams\TOPIC_WORK_RECORD.md` |
| Sessions exe, 10,501,653 bytes, 2026-10-01 | `V:\streams\cmsessions\builds\sessions-page\dist\sessions_page.exe` |
| Harness and COSMOS CODE pack | `V:\streams\opus_finish_2026-10-02\` (`00_INDEX.md`, `01_PACKAGE_HARNESS.md`, `02_PACKAGE_COSMOS_CODE.md`) |
| Cache tap, not landed | `V:\streams\opus_finish_2026-10-02\03_PROPOSAL_CACHE_TAP.md` |
| Seat notes, 118-file count, DS0731 table | `P:\cosmos_code\harness\seat_notes\` |
| Language split and the 4C runner change | `P:\cosmos_code\for_opus\LANGUAGES.md`, `LANGUAGE.md`, `CHECK_PIPELINE.md` |
| 190k close rule | `resession\RESESSION_190K_NOTES.md` in this pack, copied from `V:\A\Ai\COSMOS\docs\RESESSION_190K_NOTES.md` |

`V:\A\COSMOS_Harness` is not on disk. The harness package is the Streams copy named in `00_INDEX.md`.

## What this pack freezes

The working tree only:

- `canon\CANON_PEN.md` and `canon\CANON_ONE_HEAD.md`, plus the diffs against `ccr/seed-archive-stamp`
- `resession\RESESSION_190K_NOTES.md` (untracked on the branch)
- `sessions-page\` source of the dirty submodule at gitlink `3ea9c9bf`. No exe, no `build\`, no `.git`
- `cdeck\` the uncommitted UI and `tests\test_cluster_floor.py` on top of `c984ad33`. `tracked.diff` is the tracked-file diff. `__pycache__` was not copied

The cDeck commit `c984ad33` ("Name the website profile Spidercaster.") and `origin/main`'s pin `ed7805a` (#333, same message) have the same tree. The extra files in `cdeck\` are the part that is on neither pin.

## Small Sessions packet

`G:\cmsessions\` has the same Sessions source, `README.md`, and `design\example-western-digital.jpg`. No exe. Current overview and sessions screenshots were not on disk. The Blackline style files were not at `V:\cosmos_props\2026-09-19_UI_Xpert_COSMOS_Blackline`.

## Combine check

`origin/main` merged onto this branch in a detached probe. The live checkout was not merged and was not committed.

One conflict: `.gitignore`. This branch ignores `work_orders/ccr/hero_coders/*/mouth.py`. `origin/main` does not. Both tips already track `work_orders/ccr/hero_coders/27_qwen37/mouth.py`. The probe keeps the ignore line, so new untracked `mouth.py` files stay local and the tracked file stays.

`cosmos/cosmos_profiles.py` was edited on both sides. The branch copy already contains main's Spidercaster label rename and adds the website plugin block. Git kept that file. Nothing from main was dropped.

`builds/cdeck` takes main's gitlink `ed7805a`. That tree matches the local commit. The uncommitted cDeck UI still applies on top of it.

`cosmos/cosmos_query_channel.py` and `tests/test_query_channel.py` come from `origin/main`. The resession, ROLD, session kit, session procedures, and Spidercaster module stay from this branch.

`py_compile` of those modules passed. `pytest` of `tests/test_resession.py`, `tests/test_session_procedures.py`, and `tests/test_query_channel.py` passed 4/4 once the gitignored `_delme` fixtures were visible. A fresh worktree does not contain `_delme`, and without it `test_resession_gate` reports 69/71. That failure is the missing fixture, not a merge break.

The probe was removed. `V:\A\Ai\COSMOS\_delme` is still in place.
