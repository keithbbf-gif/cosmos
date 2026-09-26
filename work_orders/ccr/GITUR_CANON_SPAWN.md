# Gitur BUILD — CANON spawn layers (Core)

Repo keithbbf-gif/cosmos. Branch `ccr/canon-spawn-layers` from origin/main. P10. Tag CCr `f47bad79` to preload as default Agent Roles.

FIRST read docs/AGENT_BRIEF.md, docs/AGENT_BOUNDARIES.md, and the rules in this prompt (also `docs/CANON_SPAWN.md` if present on the blob; if missing, this prompt IS the spec).

**Do (smallest functions):**
1. `cosmos/cosmos_spawn.py`:
   - `SpawnSpec` fields: role, model, wrapper_paths[], skill_names[], tools[], params{}
   - `defaults(role, model)` loads WRAP/{role}, STYLES/{model} or _TEMPLATE, default skills for that role
   - `apply(spec)` fills missing layers with defaults; never silent skip
   - `preflight_session(paths)` : if SEED/BU says resume, return `{need_resume: true}` — caller runs session start; GET never mkdir
   - `refuse` extra grok.exe (argv containing grok.exe / `grok --single` as WO worker)
   - Context source must be list; string with ` · ` → `NO_CONTEXT` typed
2. Call `apply` from work-order runner **before** any model argv (replace grok spawn with refuse + fail_xfer)
3. `--selftest`: missing role fills default CODER; concat CTX refuses; grok argv refuses

**Expected:** unified diff first, 3 VERIFY.

Must not: pull unique HEAD; USPTO; occupancy pin drop; second scheduler.

Title: `WO: CANON spawn layers Role Wrapper Skills Tools Params`
