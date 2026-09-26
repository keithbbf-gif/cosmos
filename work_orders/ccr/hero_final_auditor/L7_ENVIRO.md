# L7 — Final Auditor Environment

- cwd: `V:\A\Ai\COSMOS\live\work\audit\` (isolated worktree).
- Trigger: `len(glob("live/queue/gitur_keeps/*.json")) >= 30`.
- Handoff: ACCEPTs bundled to `live/queue/scribe_inbox/batch-<id>.json`.
