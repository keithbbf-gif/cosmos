# JUDGE_DOCS

Second pass over the module notes. Product code was not edited. Scope is the thirteen notes linked from `README.md`, plus `README.md`. `improvements/` was not judged. `tokenctr-client.md`, `tokenctr-rails.md`, and `tokenctr-server.md` are not in that index of thirteen. They were read because they sit in this folder. Only `tokenctr-server.md` has a completeness sentence.

Grade marks that block a completeness claim:

| file | Grade section |
|---|---|
| `core.md` | 4C is `NOT_RUN`. The page says it does not claim a pass. |
| `cdeck.md` | Tests left `NOT_RUN`. The note does not record a result. |
| `sessions.md` | sessions-page 4C was `NOT_RUN`. session-tools and Open Sessions were not graded here. |
| `xtalk.md` | 4C was `NOT_RUN`. `--selftest` was not run and is not treated as a grade. |
| `tokenctr.md` | `ruff` FAIL 379, `mypy` FAIL 34 errors in 21 files, `pytest` exit 3. The note does not call the package green. |
| `voice.md` | The four 4C tools are recorded as passed, and the same section says voice refine stays `TABLED`. |
| `cosmos_code.md` | Grade says package 4C passed. Locked dispatch is in the body and in `README.md`, not in the Grade section. |
| `README.md` | No Grade section. Dispatch stays locked is a limit, not a completeness claim. |

No sentence in those fourteen files says a module is complete, finished, or fully integrated. Sentences that say the opposite were not rewritten. That includes Core routes that return 501, cDeck totals that stay `UNMEASURED`, session-tools tests the note does not claim passed, xtalk stating `NOT_RUN` in the same breath as “Core already serves,” Token Center refusing to treat 190/190 as 4C, and voice refine staying `TABLED`. “The rebind of the 666 Cowork sessions is already done” names that rebind, not a finished sessions module.

## Corrections

| file | quote | what is actually true |
|---|---|---|
| `tokenctr-server.md` | `README.md` says the package is complete at 190/190 checks, and that `tests/` holds 12 suites, all green. This run supports that count. | Token Center is not complete. `tokenctr.md` Grade on main `501fdee2` is `py_compile` PASS, `ruff` FAIL 379, `mypy` FAIL 34 errors in 21 files, `pytest` exit 3 because those test modules call `sys.exit` at import. That note says this is not a green package and that the README 190/190 line is not the 4C grade. The server note’s own HANDOFF section 3 boxes are empty, and the next sentence says this run does not close section 3. A direct-run tally of 190, if that addition is right, is twelve scripts exiting 0. It is not 4C, not one book with Core `SpendGate`, and not the manufactured-rail or nightly-dashboard boxes.

## Pytest

One process at a time. `py -3.14 -m pytest -q -p no:cacheprovider --basetemp C:\Users\Papa\AppData\Local\Temp\c4-judge2`. No run exceeded two minutes.

| target | exit line |
|---|---|
| `tests\test_meter_window.py` | exit 0. `7 passed in 0.11s` |
| `tests\test_orc_compose.py` | exit 0. `1 passed in 1.48s` |
| `tests\test_tokenctr_rails.py` | exit 0. `1 passed in 0.14s` |
| `tests\test_tokenctr_wizard_offline.py` | exit 0. `2 passed in 0.11s` |
| `builds\session-tools\tests` | exit 0. `29 passed in 0.42s` |

## Later than this judge

The table above is the second-pass snapshot. These notes moved after it. This section does not rewrite that snapshot.

- `xtalk.md` now records the local grade in `c4-h10-result.md`: py_compile 0, ruff 0, mypy 0, pytest 4 passed.
- `sessions.md` records sessions-page `68/68` and Open Sessions `5/5`. Those are script grades, not a four-tool 4C pass.
- `cdeck.md` records pytest 5 failed, 33 passed, and the header fold check `assertions 102 passed`. Day and week stay `UNMEASURED` without a priced on-page row.
- `tokenctr.md` records the later package grade ruff 0, mypy 0, pytest 12 passed, plus dispatch tests 10 passed. The `1 passed` rails line above is the pre-rail test. The desk is still not a live sale, and SpendGate is still not bound.
- `core.md` still refuses a blanket Core 4C PASS. A later combined recheck of 13 wave files printed `74 passed in 13.73s`, and the feature script printed `56/56`. That is not a claim that every Core module passed 4C.
- Session-tools later printed 30 passed, including the seed refusal. The 29-passed line above is the earlier run.
