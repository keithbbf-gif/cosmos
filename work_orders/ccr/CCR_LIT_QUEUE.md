# STOP — SOP

Keith: they stay until they are judged. Agents out of order. **STOP. DO IT BY SOP.**

**SOP:** Gitur PR stays **open** until a **Judge** says KEEP. Then CCr merges. Not before. Not occupancy FIFO. Not this orch “have her do it.”

Orch does **not** write LiT. Orch does **not** tell CCr to apply patches onto main. Propose on a Gitur branch → Judge → CCr merge. Bypass is the mess and the wasted tokens.

Jobs **wait** in the boxes. They do not crash the tree.

| Stage | Where it sits |
|---|---|
| WO / board | `work_orders/drop`, `work_orders/ccr/*.md` |
| Proposal | `work_orders/ccr/proposals/` |
| Attempt / grade | `live/state/attempts/attempts.jsonl` |
| Sandbox / worktree | `live/work/codex/hero/` (not LiT) |
| Gitur | **open PR** until Judge KEEP |
| Filed, not deleted | `_delme/` |

LiT is only CCr merge after Judge KEEP. Everything else is a parking spot.

**Now:**

- **Do not** apply the three SOL coder patches (580 assert / 582 delme / 584 opened). They are **unjudged**.
- **Do not** merge anything else unjudged.
- **Do not** fire SOL/Codex until Keith says.
- **Do not** extra `grok.exe`.
- **#580–#586** already on main is the mess. Do **not** add more on top without a Judge KEEP.

Judge seat when Keith names it. Until then: **hold**.

**Canon:** `docs/CANON_PEN.md` — if Keith names you the pen, **disable the other writers first.** Never write straight to the tree. They stay until judged.
