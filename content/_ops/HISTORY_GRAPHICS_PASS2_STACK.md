# History packs — graphics pass 2 stack (2026-09-14)

**Do not merge to `main` without editor integration.** This PR stacks prose lanes with a second graphics pass.

## Branch

`cursor/history-graphics-pass2-d01e`

## Stack order

| Layer | Source branch | Contents |
|-------|---------------|----------|
| 1 — Prose | `cursor/wowtherapies-therapy-history-b51d` | 42 WOW Therapies essays |
| 2 — Pass-1 graphics lane | `cursor/wowtherapies-therapy-history-graphics-9a7f` | Staged SVG + pipeline (merged, README reconciled) |
| 3 — Pass-2 graphics | this PR | `assets/` SVG depth, `drafts/articles/` embeds |
| 4 — Fig pack | `cursor/fig-history-graphics-762d` | Fig history tree + pass-2 shared SVG + `drafts/staging/` |

## Rights

- Editorial SVG: **CC0** (original ink schematics).
- Photographs: **PD/CC only** per pack `IMAGE_SOURCES.md` / `PORTRAIT_SOURCES.md`.
- **No AI-generated faces** — monogram plates until cleared rasters.

## Verification

```bash
python3 content/wowtherapies-therapy-history/check_pack.py
python3 content/wowtherapies-therapy-history/pipeline/wow_graphics_pass2.py
python3 content/fig-history-ancient-to-today/pipeline/fig_graphics_pass2_drafts.py
```

## Remediation before publish

1. Editor merges `drafts/articles/*` into `articles/*` when satisfied.
2. Reconcile `staged/` vs `assets/` paths in CMS import (`WP_IMPORT.md`).
3. Run portrait clearance for any monogram → photograph upgrade.
