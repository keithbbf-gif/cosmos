# Dirty PR notes — do not merge without remediation

**Inventory date:** 2026-09-14 (UTC). Policy: **triage only** — dirty stacked PRs must be **closed or rebased**, not force-merged.

---

## [#245](https://github.com/keithbbf-gif/cosmos/pull/245) — supplements R&D editor pass

| Field | Value |
|--------|--------|
| **Branch** | `cursor/supplements-rd-blog-editor-b6b8` |
| **Base** | `cursor/supplements-rd-blog-ee57` (writer [#230](https://github.com/keithbbf-gif/cosmos/pull/230)) |
| **Lane** | Editor |
| **GitHub merge state** | **DIRTY** (conflicts with base) |
| **Verdict** | **Do not merge** in current form |

### Why it is dirty

1. **Stack order violation:** Editor branch was cut from the **writer-only** tip (`supplements-rd-blog-ee57`). Graphics landed separately on [#240](https://github.com/keithbbf-gif/cosmos/pull/240) (`cursor/supplements-rd-blog-graphics-af19` → `main`). The editor diff **deletes** `GRAPHICS_INDEX.md` (~169 lines) and edits `MANIFEST.md` / `STYLE_GUIDE.md` on a base that never contained the graphics merge, so GitHub reports conflicts and the tree would **drop staged SVG inventory** if merged blindly.

2. **Parallel lane drift:** Writer [#230], graphics [#240], and editor [#245] all touch `content/supplements-rd-blog/` without a single integration branch (contrast `cursor/furniture-craft-merge-1ad4`).

3. **Voice pass scope:** One commit on the editor branch line-edits articles 01–40 but does not reconcile embed paths or `graphics:` front matter with [#240](https://github.com/keithbbf-gif/cosmos/pull/240).

### Recommended remediation

| Step | Action |
|------|--------|
| 1 | **Close** [#245](https://github.com/keithbbf-gif/cosmos/pull/245) (keep branch for patch extraction) or mark draft **closed** with link to replacement PR. |
| 2 | Merge or squash **#230** writer pack to `main` when ready (or into a pack integration branch). |
| 3 | Rebase **#240** graphics onto that tip; resolve `INDEX.md` / `MANIFEST.md` once. |
| 4 | Cherry-pick editor commits from `supplements-rd-blog-editor-b6b8` onto `writer+graphics` integration; **restore** `GRAPHICS_INDEX.md`; re-run embed verification. |
| 5 | Open a **new** editor PR with base = integrated branch, merge state **CLEAN**. |

### Commands (maintainer)

```bash
export GH_TOKEN=…   # repo read/write
git fetch origin cursor/supplements-rd-blog-ee57 cursor/supplements-rd-blog-graphics-af19 cursor/supplements-rd-blog-editor-b6b8
git checkout -b cursor/supplements-rd-integrate origin/cursor/supplements-rd-blog-ee57
git merge origin/cursor/supplements-rd-blog-graphics-af19   # resolve INDEX/MANIFEST
git cherry-pick <editor-commits>                            # drop GRAPHICS_INDEX deletion hunk
```

Until step 5 completes, **#245 remains DO NOT MERGE**.
