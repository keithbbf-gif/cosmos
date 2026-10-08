Applied 2026-10-07 from V:\streams\clusters onto this tree. The streams original stays in place. Nothing here writes live/, takes CCR.lease, or opens a second ledger. Live COSMOS seams stay the authority. The plugin still refuses live-tree paths, grok.exe, and pushes to main.

# Clusters plugin

Backend for the COSMOS Clusters console. The graphical interface is a separate agent. This package does not draw it.

```
py -3.14 -m pytest -q
py -3.14 -m clusters --root <projection-dir> --port 8780
```

The listener is `127.0.0.1` only. Routes are `API.md`. The projection directory must not be the COSMOS `live` tree.

Seating goes through `clusters.harness.plan_seat`, which calls `g47.seat.seat` when `V:\streams\cosmos_code\harness\G47` is present. `seated` stays false. `execute` is off unless the caller sets it, and `grok.exe` still does not start.

Feature list: `docs/FEATURES.md`. Plan: `docs/ARCHITECTURE.md`. Rules: `docs/01_CLUSTERS.md`.
