# Gitur BUILD — cDeck CREATE ROLE + WRAPPER kinds

Repo: keithbbf-gif/cdeck. Branch `ccr/create-role-wrapper` from origin/main. P10 PR.

FIRST read docs/AGENT_BRIEF.md if present. Occupancy is `test_kdash_working.py` + `test_create_panel.py`.

**Problem:** `CREATE_KINDS` in `ui/app.js` (and deck_create.js if it duplicates) must stay **equal** to Core `MAKER_KINDS`. Core PR adds ROLE, WRAPPER. This PR adds the same two strings.

**Do**
1. `CREATE_KINDS = ["AGENT", "TOOL", "CONNECTOR", "SKILL", "ROLE", "WRAPPER"]`
2. Fold into **existing** CREATE occupancy checks — do not drop a pin. If a check lists the four names, extend the same check.
3. CREATE ORDER still POST `/jobs` queued WO, not a finished skill.
4. Painters for ROLE/WRAPPER: empty GET is empty chips, not invented makers.

**Expected:** unified diff first, 3 VERIFY. Occupancy must stay green (163 on github main; do not invent 165).

Must not: iframe, drawCore, extra grok.exe, merge leftover PRs 6/16/17/68/102/108/320.

Title: `WO: CREATE kinds ROLE WRAPPER`
