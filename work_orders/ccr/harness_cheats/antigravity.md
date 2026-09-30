# CHEAT — AntiGravity (UNMEASURED — IDE installing 2026-09-29)

Google agentic door. SDK = Python library (`google-antigravity` wheel incl. compiled
runtime — cloning the repo alone does NOT run it; install from PyPI). Status: IDE
installing on KC-PC; nothing on PATH verified yet. Do not claim a seat until a ping passes.

- **SDK:** `pip install google-antigravity` (platform wheel). Repo: `google-antigravity/antigravity-sdk-python` (Apache-2.0).
- **Entry:** `Agent` — high-level, batteries-included; session via `async with Agent(...)`.
- **Resume:** `AgentConfig.conversation_id` reopens a saved session (`conversation.conversation_id`).
- **Sandbox:** `sandbox_status` reports whether `run_command` executed sandboxed; `enable_sandbox` requested-but-unavailable = unsandboxed fallback. Surface it, don't assume it.
- **Wrapper (planned):** AGENTS.md in the worktree if the door native-loads it (verify); else prompt-carried WRAP then TASK. Do not claim which until measured.
- **Skills:** TBD — not a second system sentence until the door proves otherwise.
- **Writes:** TBD worktree shape. Grade reads files after exit. PathJail on any host harvest.
- **COSMOS CODE:** jail + hooks-as-law stay in the rail, not copied into the prompt.

## Measured 2026-09-29 (SDK 0.1.20, IDE 1.107.0)

- CLI `bin/antigravity-ide.cmd` = VS Code-style window launcher only (no agent run).
- SDK: `AgentConfig` abstract → use `LocalAgentConfig` (Gemini/Vertex) or `LocalOpenAIAgentConfig` (`model` + `base_url` + `env`) — the latter drives ANY OpenAI-compatible endpoint incl. OpenRouter. `Agent(cfg)` + `async with` + `await agent.chat()`; read via `await reply.resolve()` (chunks) — `text()` hangs; resolve-then-read is the pattern.
- BLOCKED: runtime 401 `No cookie auth credentials found` — needs Google sign-in inside the IDE (app_data_dir pointing at the IDE profile did NOT satisfy it). Keith: sign into Google in AntiGravity, then ping re-runs.
- Test scripts (tmp, not live): `tmp/bakeoff70/grav_ping.py`, `grav_or_ping.py` (mimo-v2.5 via OR).

1. `where antigravity` / IDE binary on PATH. `pip show google-antigravity`.
2. Auth shape (OAuth / API key / IDE login?) — record, never print secrets.
3. Ping seat: hero pack + first line `NONE`. Then FizzBuzz exact.
4. Then: runner (`_summon_antigravity.py` sketch), BIND entry, BAKEOFF70 rows.

## Scars (pre-seat)

- REPO-CLONE-DOES-NOT-RUN — needs the wheel runtime.
- No ping yet. No runner yet. No BIND entry yet.

## Not

Claude Code. A second live pen. Claiming this door seats anything before step 3 passes.
