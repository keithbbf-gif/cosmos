# DEFINE — vendor harness / wrapper / skills (2026-09-18)

Keith: look at GLM, DeepSeek, and Ling sites for skills, wrappers, harnesses. DeepSeek released a harness — search DeepSeek’s website.

WRAP: What is the intent, and the best execution of this intent?

**Intent:** Sit each Coder in **that family’s native harness** when one exists. Steal their skill/wrapper shape into COSMOS layers (Role WRAP + Skills + Enviro). Do not install a second OS.

## DeepSeek — first-party harness (bound)

Site: [deepseek.com/harness](https://www.deepseek.com/harness/en/) · GitHub [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) · Docs [deepseek-harness.github.io](https://deepseek-harness.github.io/deepseek-harness/en/guide/quickstart)

**Agent = Model + Harness.** Cordis kernel. Everything is a plugin: models, tools, **skills**, sessions, sandboxes, storage, loops, scheduling, UI. Compose in config, no source fork.

| COSMOS layer | dsh analog |
|---|---|
| Harness | `dsh` profiles: `headless` (CODER spawn), `web` (not COSMOS default), `sdk` / `acp` |
| Wrapper | system-prompt plugin + session prefix |
| Skills | `ctx.skills` + `skill` tool. Catalog from `$DSH_HOME`, `~/.agents`, project roots. Lazy load by name. |
| Tools | plugins (fs, bash, skill, subagent, web). Kind-gate still COSMOS. |
| Enviro | `$DSH_HOME` (default `~/.dsh`). COSMOS: `live/work/dsh-home`. Append-only session log. |
| Size | SDK example `max_tokens=49152` is a cap they picked — we still compute **MAX** after preload − 20% window. |

Installed this chair: `@deepseek-ai/dsh@0.1.5-rc.2` → `dsh` on PATH (`dsh -V` = `0.1.5-rc.2`). Spawn: `dsh --profile headless "<ITEM>"` with `DSH_HOME=live/work/dsh-home`. **Not** `dsh web`. Needs `DEEPSEEK_API_KEY` (Keith). Do not dual-write `DSH_HOME`.

Safety: developer preview, not an audit. Disposable worktree. No LiT cwd.

## GLM / Z.AI — official harness is ZCode (desktop ADE, not a dsh CLI)

They **do** have a first-party harness. Homepage title: [“Official Harness for GLM-5.3”](https://zcode.z.ai/en). Filing: ZCode’s harness does context, tools, scheduling, cache, verification.

| COSMOS layer | ZCode analog |
|---|---|
| Harness | **ZCode Agent** inside the Electron ADE. Windows installer exists (`ZCode-3.12.3-win-x64.exe`). Also wraps Claude Code / Gemini CLI / Codex / OpenCode in the same app. |
| Wrapper | `~/.zcode/AGENTS.md` + `/` commands (`/goal`, `/compact`). Long-lived rules in project files ([best practice §4](https://docs.z.ai/devpack/resources/best-practice)). |
| Skills | `SKILL.md` at `~/.zcode/skills/<name>/` or workspace `.zcode/skills/`. Invoke `$`. Frontmatter `name` + `description` (≤1024). [docs](https://zcode.z.ai/en/docs/skill). Also [zai-org/GLM-skills](https://github.com/zai-org/GLM-skills) via Clawhub. |
| Tools | Plugin pack: skills + commands + subagents + MCP + hooks. `.zcode-plugin` or Claude-compatible `.claude-plugin`. |
| Enviro | Desktop workspace / SSH / Docker remote. Not `dsh --profile headless`. |

**ZCode desktop not installed** (ADE, extra occupancy). COSMOS Coder-1 bound to **Pi** (`pi 0.85.1`, `cli:pi`, `PI_CODING_AGENT_DIR=live/work/pi-home`). Spawn `pi -p --provider zai --model glm-5.3-flash`; OpenRouter fallback if `ZAI_API_KEY` unset. AutoClaw is office/browser, not the coding harness.

## Ling / InclusionAI — no first-party harness product

Official docs never ship a `dsh`/`ZCode` of their own. They sit **inside other harnesses**:

- [Claude Code](https://developer.ant-ling.com/en/docs/integrations/claude-code/) — `ANTHROPIC_BASE_URL=https://api.ant-ling.com/anthropic`, `claude -p "…" --model Ling-3.0-flash`
- [Hermes](https://developer.ant-ling.com/en/docs/integrations/hermes-agent/) — custom endpoint `https://api.ant-ling.com/v1` (Hermes still COSMOS **WISHLIST**)
- Named compatible: OpenCode, OpenClaw
- SWE-Bench they published: **OpenHands**
- Skills: cookbook `resources/recommended-skills/ling-gui-agent-skill` only — no skill platform
- Model page: “improved compatibility with **common Harness environments**” (they mean Claude Code et al., not a Ling CLI)

Coder-5 bound to **OpenCode** (`opencode 1.18.31`, `cli:opencode`, `OPENCODE_CONFIG=live/work/opencode-home/opencode.json`). Spawn `opencode run -m openrouter/inclusionai/ling-3.0-flash`. Hermes still WISHLIST. Claude Code not installed (Anthropic-off-the-route).

## Steal (into COSMOS, not a new product)

1. DeepSeek’s sentence **Agent = Model + Harness** is our DUD (legend + mission) + occupant.
2. Skills = lazy catalog + load-by-name (dsh `skill` tool; GLM `SKILL.md`; Ling cookbook skill). COSMOS Skills layer, not PREFIX bloat.
3. Long-lived rules in PREFIX; this job in Mission tail (Z.AI best-practice §4).
4. Separate session per task (Z.AI §10) = new sid per spawn.
5. Do not bind COSMOS WD2 to dsh Schedule / Hermes cron.

## Not

Install Hermes. `dsh web` as the COSMOS dashboard. Clone the 18k-commit harness into LiT. Extra `grok.exe`. GLM-skills multimodal OCR into Coder-1. Ling OpenHands as the OS.
