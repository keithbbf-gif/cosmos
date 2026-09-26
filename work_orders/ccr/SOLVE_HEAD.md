# Solve unique HEAD vs Gitur `main`

**Do not pull `origin/main` onto this tree.**

LiT commit is **`8b5ad84e`**. GitHub default branch is **`main`** (`4f8bb074` class). Gitur `starting_ref` in `live/config/cursor_rail.json` is **`main`** — that is the head bug. This sandbox **cannot `git push`** (policy deny). Run on a host with git write:

```
cd /d V:\A\Ai\COSMOS
git push origin 8b5ad84e:lit
```

Then CCr sets Gitur base to `lit` (not `main`):

- `live/config/cursor_rail.json` → `"starting_ref": "lit"`
- `cosmos/cosmos_cursor_rail.py` `REF = "lit"` (after pen)
- Future `run_coding_dispatch(..., extra={"starting_ref": "lit"})`

Uncommitted KEEP is **still not on `8b5ad84e`**. `lit` is the last **commit**, not the dirty working tree. Committing KEEP onto `lit` is a **separate** CCr dispose.

Open PRs #563–#576 were cut from **`main`**. After `lit` exists, new Gitur only. Do not merge those PRs onto LiT via pull.
