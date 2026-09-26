# Gitur BUILD — Opus AM #2 resume must not reset day cap

Repo keithbbf-gif/cosmos. Branch `ccr/spend-resume-no-reset` from origin/main. P10. Pen f47bad79.

REVIEW_NOTES #2 / CHANGES.md: `/control/resume` currently (on **main**) may call `SpendGuard.clear()` such that `day_credit_usd` resets and each resume grants another `DAY_CAP_USD`.

**Do:** resume clears kill/pause/session throttles only (`reset_day=False`). Response includes `day_lane_reset: false`. More budget = spend-admin `BUDGET_SET`, not resume.

Files: `cosmos_service.py` (resume handler only), `cosmos_spendguard.py` (`clear(..., reset_day=)` keep old default for other callers).

**Expected:** unified diff first. One VERIFY: resume does not set day_credit to today's spend.

Must not: CSRF/loopback in this PR (that's #1, next). No unique HEAD pull.

Title: `WO: Opus #2 resume reset_day=False`
