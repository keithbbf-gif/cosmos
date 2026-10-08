Applied 2026-10-08 from V:\streams\cosmos_code\product onto this tree. The streams original stays in place. Nothing here writes live/, takes CCR.lease, or opens a second ledger. Live COSMOS seams stay the authority.

# COSMOS CODE

Propose-only coding rail. G47 (`../harness/G47`) plans the harness call. This package jails the worktree, requires a red oracle before an edit, and grades with the 4Cs: pytest, ruff, and the free legacy checkers (`py_compile`, `mypy` on this Python package). Keith 2026-09-30: `../harness/KEITH_20260930_STANDALONE.md`.

It does not start a provider. `dispatch` stays locked. It does not write `live/`. The enclosure is `policy_only` and is not wipe-proof.

```
py -3.14 -m pytest -q
py -3.14 -m cosmos_code doctor
py -3.14 -m cosmos_code check .
```

`check` exits 1 when any 4C row is FAIL or MISSING.
