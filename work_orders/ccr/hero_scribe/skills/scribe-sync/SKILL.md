---
name: scribe-sync
description: Protocol for atomic commit and synchronization across all 4 COSMOS estates.
---

# Scribe Multi-Estate Sync Protocol

1. **Verify Exclusive Pen:**
   Check `CCR.lease`:
   - `held == True`
   - `expired == False`
   - `sid == self.sid`
   If not holding, STOP. Never write without active lease token.

2. **Apply & Verify:**
   - Apply patch: `git apply --check <patch>` then `git apply <patch>`.
   - Re-verify target with `py_compile`, `ruff`, `mypy`, `pytest`.

3. **Atomic Multi-Estate Push:**
   - Commit locally: `git commit -m "[SCRIBE] <order_id>: <title>"`.
   - Push GitHub: `git push origin main`.
   - Push GitLab: `git push gitlab main`.
   - Verify `V:\` mirror is in sync.
   - Record commit hash and order_id in `live/ledger/authority.jsonl`.

4. **Context Management (75% Gate):**
   - Measure turn tokens against model context ceiling.
   - When usage reaches 75%:
     a. Finalize in-flight commit.
     b. Write signed carry manifest `SEED.json` with open cursors and lease status.
     c. Emit TidyUP and close turn cleanly.
