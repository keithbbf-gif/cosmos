# Gitur BUILD — WOMB pair seat (DEFINE_WOMB)

Repo: keithbbf-gif/cosmos. Branch `ccr/womb-seat` from **origin/main**. Blob = GitHub main. Do not pull unique HEAD `8b5ad84`. P10 PR. CCr `f47bad79` disposes onto LiT.

FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md.

**Problem:** WOMB must DEFINE then pick a **pair** from the model-rater row + porosity tensor: high orthogonality, low porosity on the **target axis**, under GAC (output ≲ $1/M). Opus T stays `/5`. Read T; do not rewrite math.

**Do**
1. Add `cosmos/cosmos_womb.py`:
   - `pick_pair(porosity_fold, rater_rows, *, axis: str, budget_out: float = 1.0) -> dict`
   - Filter slugs with completion USD/1M ≤ budget_out (UNMEASURED rate = skip, not $0).
   - Exclude `openai/gpt-5.6-sol` and non-flex Luna. Luna Flex IN if rate ≤ budget.
   - **Mix:** when both a paid-low (≤ $0.60 out: Luna Flex, GLM Flash, DS 0731 paid, Muse 1.2 plain) and a `:free` slug are eligible, prefer one of each over two :free.
    - Among remaining, maximize **`orthogonality`** (porosity fold; aliases `orth_sketch` / `signed`; else `(xor_err − cofail) × mean_err`) on `axis`, minimize pair porosity mag on that axis. Missing cell = UNMEASURED, skip that pair. NaN/inf/negative `budget_out` = BAD_INPUT.
   - Return `{kind: MEASURED|UNMEASURED, a, b, axis, orth, mag, reason}`. GET never mkdir.
2. Optional GET `/api/v1/womb/seat?axis=coding` — fold live porosity + rater; 404 UNMEASURED if no pair. Never invent.
3. `--selftest` hermetic: fake fold + rows; UNMEASURED when empty; refuses SOL.

**Expected output:** unified diff first, then 3 VERIFY lines. Empty if a womb seat already exists on main.

Must not: change `cosmos_porosity.py` T formula; second scheduler; USPTO; extra grok.exe; occupancy pin drop.

Title: `WO: WOMB pick_pair high-orth low-porosity GAC`
