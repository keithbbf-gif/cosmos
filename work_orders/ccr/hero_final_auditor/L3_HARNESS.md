# L3 — Final Auditor Harness (local grok CLI)

Bucket-full-only. Summoned ONLY when `live/queue/audit_bins/final/` (or the
GitHub PR list) holds >= 30 judged keeps. Never otherwise.

```powershell
# prompt file = legend PREFIX (stable bytes) + 30 audit packets in tail
grok --single --prompt-file live\work\audit\batch-<id>.md -m grok-4.7 `
  --reasoning-effort high --output-format json --always-approve `
  > live\queue\audit_verdicts\batch-<id>.json
```

- `--prompt-file` (measured 5a pattern), `--output-format json` for machine
  verdicts (dispatch uses plain; audit uses json).
- No TUI flags (`-r`, `--cwd --fullscreen` are resession shapes, not audit).
- Exactly ONE grok.exe (the Auditor). No second grok writer on the tree.
- Verdicts land in `live/queue/audit_verdicts/batch-<id>.json`, then Scribe.
