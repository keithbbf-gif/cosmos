# STYLES/cursor-cloud — model note from the 2026-09-24 4Cs pile

family = cursor
note = these arms are cursor-a / cursor-b / cursor-solo. Not a Judge. Not a third copy.

## What the pile showed

- 104 Python hunks do not `git apply` on the current file (HUNK_DRIFT). A stale hunk is not code.
- Do not patch a path that is not on disk. Missing path = new file (`--- /dev/null`). `cosmos/cosmos_rolled.py` was patched twice and is absent.
- Do not emit `new file mode 120000`. A symlink body (`../../ui`) is not a code copy.
- A new `.py` must be ruff-clean: no coding cookie (UP009), no `%` formatting (UP031), imports sorted (I001), no dead noqa (RUF100).

## What is not this model's fault

- Ruff/mypy that already fail on the unpatched file are tree debt. The checker must compare base vs patched.
- pytest FileNotFoundError for `ui/app.js` in a temp dir with no UI tree is the checker, not the coder.
