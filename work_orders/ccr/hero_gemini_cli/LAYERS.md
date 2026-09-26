# Gemini CLI HERO — LAYERS (Google Agents template, draft)

**Seat:** CODER on the Google lane. **Binary:** `gemini.cmd` v0.52.0 (npm global).
**Docs:** https://geminicli.com/docs/ · headless: https://geminicli.com/docs/cli/headless/

## L1 Role
CODER — propose-only. First line NONE or `diff --git`. No merge. No live-tree pen.

## L2 Model
`gemini-3.8-flash` (pin). `-m gemini-3.8-flash`. Never HIGH thinking on this seat
(thinking bills as output at $3.75/M — GF38-001 scar).

## L3 Harness (the execution vector)
```
C:\Users\Papa\AppData\Roaming\npm\gemini.cmd -p "<mission>" -m gemini-3.8-flash --output-format json
```
- **Headless** is triggered by `-p`/`--prompt` (or non-TTY). No interactive UI.
- **`--output-format json`** → single JSON: `{response, stats, error}`. `stats`
  carries token usage + latency — feeds the usage tracker (WO-20260920-003).
- **Exit codes:** `0` success · `1` general/API error · `42` input error ·
  `53` turn limit exceeded. The runner maps these; 53 = restate, not retry.
- **No `--harness` flag** on this install. **No `--system-instruction`** — the
  wrapper is copied into cwd as `AGENTS.md` + `GEMINI.md` (project context).
- `--allowed-tools` is **deprecated** — tool policy lives in the wrapper.

## L4 Wrapper
Copied to cwd as `AGENTS.md` (house rules) + `GEMINI.md` (project context —
Gemini CLI reads it automatically). Same content as `_CODER_WRAP.md` +
`STYLES/_TEMPLATE`, adapted: first line NONE|diff, propose-only, worktree-only.

## L5 Skills
`gemini-headless-diff` (below) — prefill, contract-first, JSON output parse.

## L6 Tools
allow: read, bash, powershell, edit, write, grep, find, ls (worktree).
forbid: git_push, git_merge, grok.exe. Sandbox: worktree (Gemini CLI has its
own sandboxing feature — keep the prose fence too; LING-001 scar class).

## L7 Environment
```
cwd: V:\A\Ai\COSMOS\live\work
wallet: DECISION NEEDED (see below)
GOOGLE_CLOUD_PROJECT: <wallet project>   # if Vertex-backed
GEMINI_API_KEY / GOOGLE_API_KEY: <wallet key>  # if API-key-backed
```

## L8 Mission
`-p "<mission text>"` — the WO tail. Keep PREFIX+ITEM under the window
(1M); MAX = window − (cache + prompts) − 0.20×window.

---

## Wallet decision (RESOLVED 2026-09-20)

**Verified:** the CLI works pinned to **medicineman** — `GOOGLE_CLOUD_PROJECT=
project-cc5302c9-190c-4cdf-87d` + `GOOGLE_API_KEY=vertex_medicineman_key.txt`
→ **PONG** (Agent Platform API is enabled on that project).

The default env key (openwork-csm, project 252939746739) **fails** — Agent
Platform API is disabled there (403 SERVICE_DISABLED). Do not enable it on
that project without Keith (AGENTS.md: no GCP Activate).

| Option | Key | Project | Result |
|---|---|---|---|
| A. env key (openwork-csm) | GOOGLE_API_KEY | 252939746739 | ❌ 403 SERVICE_DISABLED |
| **B. medicineman** | vertex_medicineman_key.txt | project-cc5302c9 | ✅ **PONG** |
| C. any other $300 account | its key | its project | untested but same class (Agent Platform must be enabled) |

## Skill: gemini-headless-diff

```markdown
---
name: gemini-headless-diff
description: Use when coding on gemini-3.8-flash via Gemini CLI headless. Trigger on Gitur WO, refactor, propose-diff. Google lane. Never HIGH thinking.
---
1. Headless: -p "<mission>" -m gemini-3.8-flash --output-format json.
2. Parse the JSON: response = the diff/proposal; stats = token usage (record it).
3. First line NONE or diff --git. Propose only. Worktree only.
4. Exit 53 = turn limit — restate shorter, never retry the same prompt.
5. Wrapper lives in cwd as AGENTS.md + GEMINI.md (no --system-instruction).
6. No grok.exe. No LiT. No USPTO.
```

## Verification (when seated)

```
gemini.cmd -p "Reply with exactly: PONG" -m gemini-3.8-flash --output-format json
  → {"response": "PONG", "stats": {...}}  (exit 0)
```