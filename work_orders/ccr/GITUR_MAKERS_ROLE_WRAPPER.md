# Gitur BUILD — CREATE kinds ROLE + WRAPPER

Repo: keithbbf-gif/cosmos. Branch `ccr/makers-role-wrapper` from origin/main. P10 PR. CCr disposes LiT.

FIRST read docs/AGENT_BRIEF.md, docs/AGENT_BOUNDARIES.md, cosmos/cosmos_makers.py.

**Problem:** cDeck CREATE is AGENT/TOOL/CONNECTOR/SKILL. WOMB also needs **ROLE** (WOMBAT/CODER/JUDGE) and **WRAPPER** (WRAP md / STYLE append). Occupancy: `CREATE_KINDS == MAKER_KINDS` (test_create_panel.py).

**Do**
1. `MAKER_KINDS` += `ROLE`, `WRAPPER`. Keep tuple order stable: existing four first, then ROLE, WRAPPER.
2. Selftest / tests that UNKNOWN_KIND still refuses `FOO`.
3. GET `/makers?kind=ROLE` never mkdir; empty list UNMEASURED-as-empty is OK.
4. Do **not** edit cDeck in this PR (separate cdeck job). Comment in makers.py that cDeck CREATE_KINDS must match.

**Expected:** unified diff first. Fold occupancy on the **cdeck** PR, not here.

Must not: app.js JACK'S MESH; iframe; extra grok.exe; pull 8b5ad84.

Title: `WO: makers ROLE+WRAPPER kinds`
