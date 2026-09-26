# Gitur BUILD — cDeck page for spawn FORM

Repo keithbbf-gif/cdeck. Branch `ccr/spawn-form-page` from origin/main. P10. CCr `f47bad79`.

Occupancy: extra pane in `deck_*.js` not `app.js`. Fold pins; do not drop. GitHub main occupancy is 163-class — do not invent 165.

**Do:**
1. New extra pane `deck_spawn.js` (or CREATE extension) titled SPAWN / ROLES.
2. Form fields **in apply order**: Role, Model, Harness (kind+via), Wrapper path, Skills, Tools, Enviro (env/ctx/pack/budget/cache/resume). Defaults button fills Role[Model] defaults. Kind-gate tools after harness.
3. GET `/api/v1/spawn/defaults?role=&model=` if Core PR landed; else static defaults from WRAP names. Missing GET = UNMEASURED, still show blanks+defaults, never invent makers.
4. Checkbox: session preload / BU resume required.
5. Occupancy: grep new pane from existing CREATE or extra-pane checks — **extend one existing check**, no new pin if possible.

**Expected:** unified diff first. No iframe. No drawCore.

Title: `WO: cDeck SPAWN form Role×Model layers`
