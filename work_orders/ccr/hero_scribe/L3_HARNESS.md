# L3 — Scribe Harness Specification

- **Invocation:** Persistent runner or interactive session holding `CCR.lease`:
  ```powershell
  py -3.14 cosmos\cosmos_crew_pipe.py --station scribe --inbox live\queue\scribe_inbox\
  ```
- **Fenced Commit Gateway:**
  All writes to `V:\A\Ai\COSMOS` execute through `cosmos_lock.Arbiter.fenced_commit(lease, ...)`
  with active fencing token from `CCR.lease`.
- **Sync Pipeline:**
  After local commit:
  1. `git push origin main` (GitHub)
  2. `git push gitlab main` (GitLab mirror)
  3. Mirror working tree to local `V:\` canonical root
  4. Append commit record to `live/ledger/authority.jsonl`
