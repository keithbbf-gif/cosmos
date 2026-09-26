# CODER 5 DUDs — Ling 3.0 Flash (sharp outfit)

**1 Role** CODER.

**2 Model** `inclusionai/ling-3.0-flash` (OpenRouter / OpenCode). Native Ant Ling id `Ling-3.0-flash` if `ANT_LING_API_KEY` is later bound. Measure `model`.

**3 Harness** `cli:opencode` — Ling has no first-party harness. COSMOS uses **OpenCode headless** `opencode run --dir WORKTREE -m openrouter/inclusionai/ling-3.0-flash`. Isolated `OPENCODE_CONFIG=V:\A\Ai\COSMOS\live\work\opencode-home\opencode.json`. Not Hermes. Not Gemini. Not extra grok.exe. Stay inside cwd.

**4 Wrapper** `_CODER_WRAP.md`. OpenCode `AGENTS.md` in worktree = PREFIX.

**5 Skills** OpenCode skills dir under `OPENCODE_CONFIG_DIR`. None extra until CCr accepts.

**6 Tools** OpenCode built-in, kind-gated in worktree. Forbid push/merge/grok.exe.

**7 Enviro** `OPENROUTER_API_KEY`. Window 262144. MAX = window − (cache+prompts) − 20% window (hard, never 0). OPTIMUM = 15k if expecting ~10k py, else `"float"`. Where=`proposals/`.

**8 Mission** Per Gitur WO. Luna KEEP. CCr merge. Spawn: `work_orders/ccr/CALL_OPENCODE_LING.cmd` (not fired until named).
