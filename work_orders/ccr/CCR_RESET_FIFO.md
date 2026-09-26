# CCr `f47bad79` — reset LiT to Gitur, then FIFO #563

Keith: reverse the two-head scar. One head. Gitur only.

## 1. Reset (this sandbox cannot `--hard`)

```
cd /d V:\A\Ai\COSMOS
git branch backup/unique-head-37
git stash list
REM stash@{0} = KEEP-wip — already on Gitur #577. Do NOT stash pop.
git reset --hard origin/main
git status -sb
REM expect: ## main...origin/main  (not ahead 37)
```

`backup/unique-head-37` already exists locally. Do not delete it.

## 2. FIFO first PR

https://github.com/keithbbf-gif/cosmos/pull/563  
Draft → **Ready** → squash-merge to **`main`**.  
Then `git pull` (fast-forward). That is the only LiT write.

Then 564 (do **not** merge as-is if HOST_PEN=V:\ — close or fix via Gitur). Then 565 close dup, 566 close dup, 567…577 per `FIFO_OLD_PILE.md`.

## 3. So this cannot happen again

Canon: `docs/CANON_ONE_HEAD.md`

- LiT **is** `origin/main`. `git rev-list --count origin/main..HEAD` = **0**.
- CCr writes LiT **only** by merging a Gitur PR (fast-forward pull). No occupancy-only commits. No TUI `search_replace` on `cosmos/`.
- Gitur `starting_ref` = **`main`** (same head). `live/config/cursor_rail.json`
- Empty `origin/main..HEAD` is a **gate** (`cosmos_head_gate` / principles check). Ahead of origin = refuse “synced”.
- Second CCr stream (this TUI writing LiT while Gitur writes `main`) is **P10 violate**.

After reset, continue: WOMB → Gitur (`main`) → CCr merge → LiT.
