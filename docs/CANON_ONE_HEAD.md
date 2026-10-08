# CANON — one head (Gitur → LiT)

Keith: if CCr only writes LiT from Gitur, there is one head. The 37 occupancy commits + 189 GitHub commits were two heads. Reversed: LiT **is** `origin/main`.

## Rules (smallest)

1. **One git head.** `main` on disk = `origin/main`. Count `origin/main..HEAD` is 0.
2. **One CCr.** Only that sid writes LiT. **Keith 2026-09-18:** if he names you the pen, **disable the other writers first**. **Keith 2026-10-02:** a writer is a session that holds the pen, or that is writing or has written to the tree without it. A running session is not a writer. Stop means stop the write, or let it finish. Ask Keith before any session is closed, and tell him what is going on. Do not kill the process. Then take `CCR.lease`. Then write. Canon: `docs/CANON_PEN.md`.
3. **One write pipe.** Gitur proposes (PR from `starting_ref: main`). **Judge KEEP.** CCr squash-merges to `main`, then fast-forward pull. That is the LiT write. They stay until judged. No straight-to-tree.
4. **No occupancy-only commits** (“join GitHub / keep local”).
5. **No side-door** `search_replace` on `cosmos/` from a non-CCr TUI.
6. **No `git pull` that merges two histories** onto occupancy to “catch up.” After reset, only fast-forward.
7. **No second `starting_ref`.** Cursor `live/config/cursor_rail.json` `starting_ref` is `main`. Not a unique SHA that GitHub does not have.
8. Unique work still wanted goes **Gitur first** (new PR), never a local 38th commit on a private line.
9. Backup branches (`backup/unique-head-37`) are archive, not LiT.
10. Spawn layers (Role→Enviro) still fail-closed (`docs/CANON_SPAWN.md`).
11. **The checkout of `main` stays equal to LiT.** Edit in a worktree on a Gitur branch. Check the change against that branch, because that is the codebase it joins. After the merge, fast-forward the shared checkout and leave it clean. Do not stack the next land on an uncommitted checkout.

## Gate

`git rev-list --count origin/main..HEAD` must be **0** before claiming LiT synced. Non-zero = two heads = stop and FIFO Gitur, do not invent a join commit.
