# Layer 7 — Enviro

**cwd:** repo root (no Codex worktree required; ITEM is in the prompt).  
**pack:** house.  
**ctx list:** PREFIX = JUDGE WRAP fill (no dates); tail = PR #587 diff / `docs/CANON_PEN.md` body.  
**wallet:** OpenRouter key `live/config/openrouter_api_key.txt`.  
**budget_out:** $0.25/M.  
**context_window:** ~1.3M.  
**output:** What=`text`. MAX = `1.3M − cache − prompts − 0.20×1.3M` (hard). OPTIMUM floats if unknown. Where = Mission pack.  
**cache:** first call writes prefix; measure `cached_tokens`. DeepInfra 429 ≠ cache miss.

**Output target defaults:** What=`text`. MAX computed at spawn; OPTIMUM floats. Not 4096-as-MAX.
