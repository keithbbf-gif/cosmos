# Layer 3 — Harness

**Kind:** `review` (from Role JUDGE).
**Via:** `codex exec` (OpenAI family bound) **keyed to OpenRouter — never
direct-OpenAI key.** Not Vertex. Not grok.exe. Not Google Agent Platform.

Provider profile (`%CODEX_HOME%\cosmos-openrouter.config.toml`, written by the
CALL file at runtime from the template below — never hand-edit CODEX_HOME):

```toml
model = "openai/gpt-6-luna:floor"
model_provider = "openrouter"
model_reasoning_effort = "max"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
wire_api = "chat"
```

Call shape (`work_orders/ccr/CALL_LUNA_G6_OR.cmd`):

```cmd
codex.cmd exec -p cosmos-openrouter --ignore-user-config --skip-git-repo-check ^
  --sandbox read-only --json --color never ^
  -m openai/gpt-6-luna:floor ^
  --output-last-message V:\A\Ai\COSMOS\work_orders\ccr\JUDGE_LUNA_last.txt ^
  "Read AGENTS.md and TASK.md. Grade the candidate files. First line KEEP, DROP, or HOLD."
```

- `:floor` on the model id routes OpenRouter to Flex endpoints (no
  `service_tier` flag needed on this lane; that flag is OpenAI-direct only).
- `MAX` = `model_reasoning_effort = "max"`. If the CLI rejects the value it
  fails closed before any spend — report the accepted set, do not guess spend.
- `OPENROUTER_API_KEY` loaded at runtime from
  `live\config\openrouter_api_key.txt`, never printed, never committed.
- Flex can be stripped if the catalog omits it. Measure `model` on the
  response. Read-only sandbox — not `--approve-for-me` (CODER write).

The public Codex prompting guide is for `gpt-5.3-codex`. Do not dump that starter prompt onto Luna. Let codex-cli inject tools. Do not ask for an upfront plan (she can stop early). Review = findings first, file:line, severity.

Call file: `work_orders/ccr/CALL_LUNA_587.cmd` (not run until Keith seats).
