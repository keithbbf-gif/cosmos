# Layer 3 — Harness

**Kind:** `review`.

**Via (when `hermes` is on PATH / `~/.hermes/.env`):** **`cli:hermes`**. Hermes is the persistent harness (MCP + pools). GLM is the **model**. OpenRouter is the **credential pool**, not a naked CLI chat. Hermes does **not** mean we drive Codex/Claude/Cursor consumer UIs — MCP/stdio only if kind-gated.

**Via (until Hermes bound):** degenerate `mouth:openrouter` (`CALL_GLM_587.py`) — one key, 429 = FAIL attempt.

**We need (Keith):** Hermes **credential pools** + **provider routing** — `DEFINE_HERMES_POOLS.md`.

- `ignore: ["deepinfra"]` (GLM 429 scar)
- `fill_first` not `round_robin` (rotation **busts prompt cache**)
- `OPENROUTER_API_KEY`, `_2`, `_3` — Keith pastes; orch does not `hermes auth add`
- JUDGE MCP: read-only tools only; no write servers

Not Codex. Not grok.exe. Not Cursor BUILD. Not Ori `curl|bash`.
