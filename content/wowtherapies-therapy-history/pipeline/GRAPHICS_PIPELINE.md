# Graphics pipeline — wowtherapies-therapy-history

## Agent routing (Keith, 2026-09-14)

**WOWTherapies graphics stay on Cursor Composer 2.5** for this content tree
(`content/wowtherapies-therapy-history/`). Do not switch this lane to Opus or
other models unless Keith directs otherwise. (COSMOS adversarial work orders
elsewhere may still refuse Composer; this strand is an explicit exception.)

## Stages

1. **Draft** — optional markdown in `drafts/` (outline only).
2. **Staged** — SVG + index updates under `staged/` and `GRAPHICS_INDEX.md`.
3. **Publish** — human gate: attach verified portrait files, flip status in index, PR merge.

## Seed core figures

When `drafts/` is empty or thin, regenerate validation and refresh the manifest:

```bash
python3 content/wowtherapies-therapy-history/pipeline/seed_core_figures.py
```

The script:

- Verifies every **core** SVG listed in `core_figures.json` exists and parses as XML.
- Writes `staged/MANIFEST.json` (checksums + dimensions).
- Refuses portrait plates that embed raster `<image>` tags without a matching
  `portrait_sources.yaml` entry (prevents accidental synthetic uploads).

## Adding a portrait (publish pass)

1. Confirm license on `pipeline/portrait_sources.yaml` (`status: cleared`).
2. Place the file under `staged/portraits/<figure-id>.<ext>` (not committed until cleared).
3. Replace the monogram block in the SVG with `<image href="...">` and update `credit` in
   `GRAPHICS_INDEX.md`.
4. Re-run `seed_core_figures.py`; open PR when all staged figures are `ready`.

## Magazine SVG conventions

- ViewBox width **960** (single column) or **1200** (spread).
- Palette tokens: `--ink`, `--paper`, `--rule`, `--accent`, `--caption` (defined in `<style>`).
- Every figure includes `<title>` + `<desc>` for accessibility.
- Figure label upper-left: `Fig. NN` in small caps.
