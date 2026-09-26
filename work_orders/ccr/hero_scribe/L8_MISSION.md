# L8 — Scribe Mission & Output Contract

## Mission
Read incoming ACCEPT batch from `live/queue/scribe_inbox/batch-<id>.json`.
For each approved patch:
1. Verify SHA matches staging diff.
2. Apply patch to working tree.
3. Verify 4Cs still green on target files.
4. Stage changes: `git add <files>`.
5. Commit: `git commit -m "<message>"`.
6. Push both remotes: `git push origin main` and `git push gitlab main`.
7. Reconcile local `V:\` mirror.
8. Append `SCRIBE_COMMIT` to `live/ledger/authority.jsonl`.
9. If context exceeds 75%, emit `SEED.json` and resession.
