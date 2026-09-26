# Scars from the grade-pile 4Cs — 2026-09-24

No Judge. 186 arms checked. 1 passed. 0 sets have three passing code copies.
Receipts: `SETS_4C.jsonl`. KB ids below.

## Coder scars (cursor-cloud)

| Scar | What went wrong | Fix |
|---|---|---|
| `CURSOR-001` HUNK_DRIFT | 104 hunks: `patch does not apply` on the current file. | Diff from the current file. A stale hunk is not an arm. |
| `CURSOR-002` PATCH_OF_MISSING | Both arms of `gitur-cosmos-b26-page` patch `cosmos/cosmos_rolled.py`. File is not on disk. | Missing path is a new file (`--- /dev/null`), never a patch. |
| `CURSOR-003` SYMLINK_AS_CODE | `new file mode 120000`, body `../../ui` or `../../test_deck_features.py`. | Drop symlink hunks. They are not code. |
| `CURSOR-004` NEWFILE_RUFF | New files (no base on disk) fail ruff: UP009 ×14, UP031 ×4, RUF100 ×4, plus I001 / BLE001 / F401. | New `.py` is ruff-clean: no coding cookie, no `%` formatting, sorted imports, no dead noqa. |

Model note: `CREW/IN/STYLES/cursor-cloud.md`.

## Checker scars (do not blame the coder)

| Scar | What went wrong | Fix |
|---|---|---|
| `SET4C-001` CHECKER_BLAMES_TREE | Result fails ruff/mypy the unpatched file already fails. Measured: `builds/cdeck/test_deck_features.py` is FURB167 and mypy `union-attr` before any patch. 58 of 89 ruff fails sat on an existing file. | Run the tool on the base and on the patch. A coder fail is a **new** finding only. |
| `SET4C-002` PYTEST_ISOLATION | 173 pytest fails. Re-ran one applied file: collection `FileNotFoundError` for `ui/app.js`. The test reads sibling UI at import. The checker ran the file alone in a temp dir. | cDeck pytest must include the UI tree the test opens. That error is the checker. |
| `SET4C-003` NOT_A_SET | 78 pairs, 30 solos, 0 triples. | Do not file a grade set until three code copies exist and each passes 4Cs. |

## Not done

These scars do not finish a set. They say why the current arms are not three passing copies, and what the next coder pass and the next 4Cs pass must not repeat.
