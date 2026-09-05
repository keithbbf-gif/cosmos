# AUTO-RESESSION — MOTIF stage-1 RESEARCH

**Researcher:** G46 (Grok Build). **Date:** 2026-08-26 (docs fetched live this session).
**Wish:** *Acquire the ability to RE-SESSION automatically without user intervention — or with minimal user disturbance.* (`docs/WISHLIST.md`, `docs/BACKLOG.md`).
**Consumer:** COSMOS / COW. Stage-1 research only. **No COSMOS core was edited.**
**Rule:** every flag/command is bound to official docs and/or this machine's `--help`. **UNKNOWN** where not bound. A guess is a research failure.

---

## The problem, named precisely

Two layers that must not be conflated:

| Layer | What it is | Survives Cowork death today? |
|---|---|---|
| **A. COSMOS clocks** | Watchdog2, runner, collector, Motif Driver, the rest of `docs/ORCHESTRATION.md` | **YES.** They are Windows `schtasks` + detached Python daemons. They do not live inside a model context window. |
| **B. Orchestrator session** | The Cowork / Claude Code / Grok TUI process that *is* COW: reads collector returns, synthesizes, drops the next MOTIF stage | **NO.** When that window fills or the app is closed, Layer B stops until Keith starts a new session and runs BootUP! Cm. |

Keith's measured failure: a Cowork/Claude context window fills → work *looks* stopped → he must manually open a new session + BootUP. Layer A actually keeps humming (queued jobs still run; collector still files). What dies is the **orchestrator**. Auto-resession is: spawn a **fresh** orchestrator, seeded from COSMOS carry-over, with no (or one) human turn.

`--continue` / `--resume` is **not** that mechanism. Official Claude Code: a resumed session *reopens the same session ID and appends to the existing conversation*. A **new** session starts with a **fresh** context window and **without** prior history. Continuing a full window reloads the full window. COSMOS already has the file-shaped carry-over (`state/SEED.json` + `BUCm.toml` + `BACKLOG.md`). The missing piece is a satellite that **spawns** a new headless orchestrator when Layer B goes quiet.

---

## Decision rubric (apply before ranking)

Score each rail against the wish. A rail that cannot spawn a **fresh** context window fails the wish even if `--continue` is beautifully documented.

| # | Criterion | Why it is on the rubric |
|---|---|---|
| R1 | **Fresh window, not a replay** | Context-full is the failure. Same-transcript resume fails it. |
| R2 | **Seeded from COSMOS carry-over** | `live/state/SEED.json` (HMAC) + `BUCm.toml` + `docs/BACKLOG.md` + DHx. Not vendor memory. |
| R3 | **No human turn (or one click)** | Default is MOTION (`docs/PAUSE_PROTOCOL.md` resume_gate). HOLD never self-clears. |
| R4 | **Unattended permissions** | A Scheduled Task cannot click "Allow". The run must not stall on a prompt. |
| R5 | **Windows-native clock** | `schtasks` / detached daemon. Not Cowork `/loop`. Keith 2026-08-22: **logged-on only** (`V:` is a user-session volume; `ONSTART` is the wrong trigger). `schtasks` floor = **1 minute**. |
| R6 | **Does not take COSMOS down** | Satellite. Fail-closed. One orchestrator at a time (lease). No core/kernel edit. |
| R7 | **Honest Keith surface** | Credentials, money, HOLD, mesh-destroy. Named, not hidden. |
| R8 | **Proven on this machine** | Binary on PATH, `--help` matches docs, session dir exists. |

---

## Verified sources (fetched 2026-08-26)

| Rail | Official pages used | Local binary this session |
|---|---|---|
| Claude Code | [headless](https://code.claude.com/docs/en/headless), [sessions](https://code.claude.com/docs/en/sessions), [CLI reference](https://code.claude.com/docs/en/cli-reference), [permission modes](https://code.claude.com/docs/en/permission-modes), [context window](https://code.claude.com/docs/en/context-window), [Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks), [scheduled-tasks /loop](https://code.claude.com/docs/en/scheduled-tasks) | `C:\Users\Papa\.local\bin\claude.exe` **2.1.220** |
| Grok Build CLI | [headless](https://docs.x.ai/build/cli/headless-scripting), [sessions](https://docs.x.ai/build/features/sessions), [CLI reference](https://docs.x.ai/build/cli/reference), [permissions](https://docs.x.ai/build/features/permissions) | `C:\Users\Papa\.grok\bin\grok.exe` **1.0.5 (5115b46bc9) [stable]** |
| Cursor CLI | [overview](https://cursor.com/docs/cli/overview), [parameters](https://cursor.com/docs/cli/reference/parameters), [headless](https://cursor.com/docs/cli/headless) | **Cursor `agent` / `cursor-agent` NOT on PATH.** `agent.exe` at `C:\Users\Papa\.grok\bin\agent.exe` is **Grok**, not Cursor. |
| Cowork | [Cowork overview](https://claude.com/docs/cowork/overview) | No Cowork CLI exists in those docs. |
| COSMOS | `cosmos/cosmos_session.py`, `cosmos/cosmos_watchdog2.py`, `cosmos/cosmos_dispatch.py`, `docs/PAUSE_PROTOCOL.md`, `docs/ORCHESTRATION.md`, live `SEED.json` + `PAUSE.flag` | Host-side reads this session. |

---

## 1. Claude Code headless as a resession engine

### 1.1 Flags — verified

Local `claude --help` (2.1.220) + official CLI reference. Official note: *"`claude --help` does not list every flag, so a flag's absence from `--help` does not mean it is unavailable."* Flags below are tagged **HELP** (this binary lists them) and/or **DOCS** (official reference).

| Flag | What it does | Bound how |
|---|---|---|
| `-p` / `--print` | Non-interactive. Print result, exit. | HELP + DOCS |
| `-c` / `--continue` | Load the **most recent conversation in the current directory**. | HELP + DOCS |
| `-r` / `--resume [value]` | Resume by session ID, or open the picker. | HELP + DOCS |
| `--output-format <fmt>` | **Only with `-p`.** Choices this binary lists: `text` (default), `json`, `stream-json`. | HELP + DOCS |
| `--permission-mode <mode>` | This binary's choices: `acceptEdits`, `auto`, `bypassPermissions`, `manual`, `dontAsk`, `plan`. Official config value for Manual is `default`; CLI accepts `manual` as alias (docs, v2.1.200+). | HELP + DOCS |
| `--add-dir <directories...>` | Extra working directories Claude may read/edit. **Not restored on resume** — must be passed again. | HELP + DOCS |
| `--session-id <uuid>` | Use a specific UUID for the conversation (must be a valid UUID). | HELP + DOCS |
| `--no-session-persistence` | Don't write the transcript. **`-p` only.** Session cannot be resumed. | HELP + DOCS |
| `--fork-session` | On resume, new session ID (history is **copied** — still full). | HELP + DOCS |
| `--bare` | Skip hooks/skills/plugins/MCP/auto-memory/**CLAUDE.md**. Wrong for BootUP. | HELP + DOCS |
| `--dangerously-skip-permissions` | ≡ `--permission-mode bypassPermissions`. Docs: isolated containers/VMs. | HELP + DOCS |
| `--allowedTools` / `--allowed-tools` | Auto-approve named tools. | HELP + DOCS |
| `--append-system-prompt` | Append to default system prompt. | HELP + DOCS |
| `--max-turns <N>` | Limit agentic turns in non-interactive mode. | **DOCS only** — this binary's `--help` does not list it. UNKNOWN whether 2.1.220 accepts it. |
| `--permission-prompt-tool` | MCP tool to answer permission prompts in `-p`. | **DOCS only** |
| `--verbose` | Verbose logging. Required with `stream-json` for token streaming. | HELP + DOCS |

Documented multi-turn headless pattern ([headless § Continue conversations](https://code.claude.com/docs/en/headless)):

```
claude -p "Review this codebase for performance issues"
claude -p "Now focus on the database queries" --continue
session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"
```

JSON field for the id: **`session_id`** (snake_case). Official `jq -r '.session_id'`.

### 1.2 `--continue` vs `-p --continue` (easy to get wrong)

Official [sessions](https://code.claude.com/docs/en/sessions):

- Interactive `claude --continue` **skips** sessions created with `claude -p` / Agent SDK, background sessions, and sessions whose first prompt was `/loop`.
- `claude -p --continue` **includes** `-p`, SDK, and `/loop` sessions; still skips background sessions.
- `-p` sessions are **left out of the session picker**. Resume them by ID: `claude --resume <session-id>`.

A Scheduled Task that runs `claude --continue` (no `-p`) will **miss** the headless orchestrator it just spawned. The loop must be `claude -p --continue "…"`.

### 1.3 Where session ids live (this machine)

Official: `~/.claude/projects/<project>/<session-id>.jsonl`, where `<project>` is the working-directory path with non-alphanumeric characters replaced by `-`. Retention default 30 days (`cleanupPeriodDays`). Override root with `CLAUDE_CONFIG_DIR`.

Verified this session:

```
C:\Users\Papa\.claude\projects\V--A-Ai-COSMOS\
```

Also present: `C--Users-Papa-ClaudeLocalSession`, `V--Ai`, `V--Ai-BTS-MESH`, … Entry format is **internal and version-unstable**; scripts should use `--output-format json` / `/export`, not parse JSONL.

`--add-dir` / `--mcp-config` / `--settings` / `--plugin-dir` / `--fallback-model` are **not restored** on resume. Re-pass them.

Permission-mode restore exceptions (official): `plan` and `bypassPermissions` are **never restored**. `auto` restores only if the account still qualifies.

### 1.4 Can a Windows Scheduled Task loop `claude -p --continue` on SEED/BUCm with no human turn?

**Technically yes, as crash-recovery of a still-roomy session. No, as the engine for context-full.**

| Claim | Verdict | Evidence |
|---|---|---|
| `claude -p` runs without a TTY | YES | Official headless. Workspace-trust dialog is skipped in `-p`. |
| `claude -p --continue "prompt"` continues the last `-p` session in that cwd | YES | Official headless + sessions. |
| That loop gives a **new** context window when the old one is full | **NO** | Resume = same transcript, same window. Auto-compact can keep the process alive (see 1.5) but that is vendor summary, not COSMOS SEED. |
| The task can *read* SEED / BUCm | YES, if the prompt says so | The CLI does not auto-inject `state/SEED.json`. The prompt (or `--append-system-prompt`) must name the files. |
| Unattended (no prompt stall) | ONLY with an explicit mode | Official: **`claude -p` built-in starting permission mode is Manual (`default`) on every plan.** Without `--permission-mode auto|dontAsk|acceptEdits` and/or `--allowedTools`, a tool call that needs approval **cannot prompt** and the run stalls or the action is denied. `--permission-mode auto` in `-p` has no prompt to fall back to; repeated classifier blocks skip the action and Claude keeps working. |
| `schtasks` can fire it | YES, with Keith's constraints | COSMOS rubric: logged-on only; 1-minute floor. Example pattern (official docs themselves show cron wrapping `claude -p`). **No bats** — register via `schtasks` / Python, not a `.bat`. |
| Auth in a Scheduled Task | CONDITIONAL | Without `--bare`, `-p` uses the subscription login already on the machine (`%USERPROFILE%\.claude\.credentials.json`). `--bare` **does not** read OAuth/keychain/`CLAUDE_CODE_OAUTH_TOKEN`; needs `ANTHROPIC_API_KEY` (metered). `claude setup-token` is the documented CI token. Leftover `ANTHROPIC_API_KEY` **steals** the session off the prepaid seat (precedence in `docs/research/ANTHROPIC_HANDS.md`). |
| `--add-dir V:\A V:\Ai` on every spawn | REQUIRED if those mounts are needed | Not restored. Cowork folder grants **do not persist** and are a different product (below). |

Honest answer to Keith's question: a Task Scheduler loop of `claude -p --continue` **can** keep a headless Claude Code session talking with no click, **until the window is full**. It does **not** replace BootUP. It is the wrong primitive for the wish.

### 1.5 What Claude does when context fills (not resession)

Official [context window](https://code.claude.com/docs/en/context-window): *"Claude Code compacts automatically as you approach the limit, so a full context window doesn't end your session."* `/compact`, `/autocompact`, `/clear`, subagents. Compaction **summarizes history**; it does not re-read `SEED.json`. Cowork (Pro/Max/Team/Enterprise) also auto-summarizes (Anthropic Help Center, fetched this session). That is **vendor compaction**, not COSMOS carry-over. It can mask the failure for a while, then quality falls off a cliff (the "Prompt is too long" lockout class — GitHub issue #31313, Cowork resume loop). Do not treat auto-compact as auto-resession.

### 1.6 Claude Desktop local scheduled tasks (not CLI)

Official [Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks): while the **Desktop app is open and the machine is awake**, Desktop polls every minute and **starts a fresh session** when a task is due — independent of any manual session. Permissions are per-task; Manual mode **stalls until Keith approves**. Connector/`requiresUserInteraction` tools stall every time. Sleep skips the run (one catch-up in the last 7 days). This is a **fresh window** (R1) but it is **not** a COSMOS clock (R5), it requires Desktop open, and it is the **Code** tab, not Cowork. Storage on disk: `~/.claude/scheduled-tasks/<task-name>/SKILL.md`.

`/loop` is **session-scoped**: dies when the session ends; restored on `--resume` only if unexpired. Minimum interval 1 minute. **Not** an OS scheduler.

### 1.7 Cowork — the actual dying surface — has no CLI

Official [Cowork overview](https://claude.com/docs/cowork/overview): Cowork is Claude Desktop's agentic workspace, **not** the terminal. It does **not** read `~/.claude` CLI skills. Permission-modes docs: *"The Cowork tab doesn't use these modes."* BUCm: Cowork folder grants **do not persist between sessions**.

| Cowork auto-resession via `claude -p` / schtasks | UNKNOWN / **no documented path** |
|---|---|
| Cowork CLI flags | **None documented** |
| Cowork `--continue` | **None documented** |
| Cowork session-id location | **UNKNOWN** (CLI transcripts are not Cowork) |

Auto-resession **cannot** reopen the Cowork tab. It can spawn **Claude Code CLI** (or Grok CLI) beside it. If Keith wants the Cowork UI, he still opens Desktop. The **route** can move without that UI.

---

## 2. Grok CLI / Cursor CLI equivalents

### 2.1 Grok Build CLI — verified this machine

Binary: `C:\Users\Papa\.grok\bin\grok.exe` **1.0.5**. `grok sessions list` works. Session dir exists.

#### Flags

| Flag | What it does | Bound how |
|---|---|---|
| `-p` / `--single <PROMPT>` | Headless one prompt, print, exit. | HELP + DOCS |
| `-c` / `--continue` | Continue the most recent session **for the current working directory**. | HELP + DOCS |
| `-r` / `--resume [<ID or title>]` | Resume by UUID or title; omit = most recent. | HELP + DOCS |
| `-s` / `--session-id <UUID>` | UUID for a **NEW** conversation. Must not already exist. **Does not resume.** Only valid with `--resume`/`--continue` when paired with `--fork-session`. | **HELP (this binary) + sessions page.** Headless page text ("Create **or resume** a named headless session") **conflicts**. Trust the binary + sessions page. |
| `--output-format` | This binary: `plain` (default), `json`, `streaming-json`, `streaming-messages-json`. Docs list the first three. | HELP + DOCS |
| `--always-approve` | Auto-approve tool executions. Docs alias `--yolo`. | HELP + DOCS |
| `--yolo` | Official alias of `--always-approve`. **Not listed** in this binary's `--help`. `grok --yolo --help` still prints help (exit 0) — treated as accepted. | DOCS + smoke |
| `--permission-mode` | This binary: `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`. **Not in the official CLI-reference table** fetched this session; **is** in local `--help`. | HELP; docs page incomplete |
| `--cwd <PATH>` | Working directory. **No `--add-dir`.** | HELP + DOCS |
| `--add-dir` | — | **Does not exist** on this binary or in official Grok CLI reference. UNKNOWN as a hidden Claude-compat alias; not listed among the documented Claude aliases (`--allowedTools`, `--disallowedTools`, `--append-system-prompt`, `--system-prompt`, `--dangerously-skip-permissions`). |
| `--max-turns <N>` | Cap agent turns. COSMOS dispatch already uses `60`. | HELP + `cosmos_dispatch.py` |
| `--fork-session` | New id; copies history (still full). | HELP + DOCS |
| `--restore-code` | Restore the original session's **repo snapshot**. Remote sessions require `--worktree`. **Do not use on the live COSMOS tree.** | HELP |
| `--no-auto-update` | Official headless page: pass in scripts/CI. **Not listed** in this binary's `--help`. `grok --no-auto-update --help` still prints help (exit 0). | DOCS + smoke |
| `--prompt-file <PATH>` | Headless prompt from a file. | HELP |

JSON session id field: **`sessionId`** (camelCase). Official: `grok -p "…" --output-format json | jq -r '.sessionId'`. **Not** `session_id`. Mixing this with Claude's `session_id` is a bug.

#### Where Grok sessions live (this machine)

Official: `~/.grok/sessions/`, keyed by working directory. Headless sessions (`--session-id` / `--resume` / `--continue`) stored there.

Verified:

```
C:\Users\Papa\.grok\sessions\V%3A%5CA%5CAi%5CCOSMOS\
```

(URL-encoded `V:\A\Ai\COSMOS`.) `grok sessions list|search|delete`. `grok export <id>`.

Official: headless starts a **fresh** session by default. Must pass `-r`/`-c` to keep context. Auto-compacts as the window fills (`/compact`, `/context`). Same caveat as Claude: compaction ≠ COSMOS SEED.

#### Unattended Grok loop (documented)

```
grok --no-auto-update -p "BootUP prompt here" --cwd V:\A\Ai\COSMOS --always-approve --output-format json
# then, only if the SAME window still has room:
grok --no-auto-update -c -p "Next MOTIF step" --cwd V:\A\Ai\COSMOS --always-approve --output-format json
```

COSMOS already ships this recipe in `cosmos_dispatch.py` (comment: *PROVEN flags; do not change*):

```
grok --single <task> -m <model> --output-format plain --always-approve --max-turns 60 --cwd <dir>
```

Permissions (official): default is **Ask**. `--always-approve` auto-approves; **deny rules and PreToolUse hooks still apply**. `dontAsk` exists on this binary (headless lock-down). Always-approve still prompts for remembered-dangerous patterns (`rm`, `git push`) unless an explicit allow rule is set — **except** under always-approve they run unless denied. For a Scheduled Task, `--always-approve` (or `--permission-mode dontAsk` + `--allow` rules) is the unattended floor.

Auth: cached `grok login`, or `XAI_API_KEY` (different wallet — do not mix; see `docs/research/XAI_GROK_HANDS.md`). `grok login --device-auth` for headless/remote.

### 2.2 Cursor CLI — official flags, **not installed here**

Official command is **`agent`**, not `cursor-agent`. Windows install: `irm 'https://cursor.com/install?win32=true' | iex`.

| Flag / command | Official meaning |
|---|---|
| `agent -p` / `--print` | Non-interactive. Has write + shell. |
| `--continue` | Continue previous session. Alias for `--resume=-1`. |
| `--resume [chatId]` | Resume a chat. |
| `agent resume` | Resume **latest**. |
| `agent ls` | List / pick a chat. |
| `agent create-chat` | Create empty chat, return its ID. |
| `--output-format` | With `--print`: `text`, `json`, `stream-json`. |
| `-f` / `--force` / `--yolo` | Allow commands unless denied. **Without `--force`, `-p` proposes edits and does not apply them.** |
| `--trust` | Trust workspace without prompting. **Headless only. Required for headless runs** (parameters page). |
| `--workspace <path>` | Working directory. **No `--add-dir` in official parameters.** |
| `--approve-mcps` | Auto-approve configured MCP servers. |
| Auth | `CURSOR_API_KEY` or `--api-key`. |

Documented unattended edit:

```
agent -p --force "Refactor this code to use modern ES6+ syntax"
```

**On this machine:** `Get-Command cursor-agent` → not on PATH. `agent.exe` resolves to **Grok**. Cursor CLI session-transcript path is **UNKNOWN in official docs** fetched this session (config lives at `%USERPROFILE%\.cursor\cli-config.json`; that is not the transcript store). Third-party scanners claim `~/.cursor/projects/*/agent-transcripts/` — **not used as evidence**.

Cursor **Cloud Agents API** (`POST https://api.cursor.com/v1/agents`) is a **different rail**: cloud VM, GitHub repo `keithbbf-gif/cosmos`, proven in `docs/research/CURSOR_LANE.md`. It continues *coding* while Keith is away. It does **not** BootUP the local COSMOS tree, does not read `SEED.json` on `V:`, and is not a Cowork replacement. Keep it as overflow coding, not as the resession engine.

---

## 3. COSMOS-native path — the auto-BootUP driver

### 3.1 What already exists (do not rebuild)

| Mechanism | Where | What it does | What it does **not** do |
|---|---|---|---|
| Signed SEED | `cosmos_session.close_session` → `live/state/SEED.json` + `SEED.decl.json` (len/sha/HMAC) | Architecture decision 10. `start_session` refuses a missing/forged/wrong-tree seed. | Does not spawn an LLM. |
| BUCm pointer | `V:\A\Ai\COSMOS\BUCm.toml` (git-ignored) | Agent-session bootstrap beside the SEED. One truth. | Not a competing handoff. |
| Resume gate | `cosmos_watchdog2.maybe_auto_resume` + `PAUSE.flag` `mode` | `hold` never self-clears. `resume_gate` self-clears at `auto_resume_at`. | Clears the **retask** pause. Does **not** start Cowork/Claude/Grok. |
| Activity Clock | `COSMOS Watchdog2` 15s daemon | Drops agents onto `live\queue` from BACKLOG / MOTIF_TRACKER / DHx. Max 3/pass. | Drops **workers**. The orchestrator (COW) is assumed to exist. |
| Dispatch recipes | `cosmos_dispatch.py` | Proven `grok --single … --always-approve` and `claude -p … --permission-mode dontAsk --add-dir`. | One-shot **worker** jobs, not a BootUP orchestrator. |
| Motif Driver | 15 min schtask | Mechanical next-stage drop. Judgment stays with COW. | No synthesis. |

Live this session (host-side):

- `live/state/SEED.json` present, schema `cosmos-session-seed/1`, `handoff=Cm`, `tree_id=KMesh-COSMOS-live`, `facts={}`, `watchers={}` (thin seed — a real TidyUP should pack inherited facts before relying on it).
- `live/state/control/PAUSE.flag` present, **`mode=hold`**, reason `TidyUP + resession`. WD2 stays PAUSED until Keith deletes it **or** BootUP rewrites it to `resume_gate`.

### 3.2 The hole, in one sentence

**WD2 can resume the route. Nothing currently spawns the next COW process when the last one dies.**

### 3.3 The driver (design only — not built this pass)

A **satellite** (same class as Watchdog2 / Motif Driver; **not** kernel/ledger/service):

1. **Detect Layer B quiet** (any one is enough):
   - no live `claude.exe` / `grok.exe` orchestrator PID recorded in `live/state/control/RESESSION.json`;
   - heartbeat older than N minutes;
   - optional: vendor "prompt is too long" / compaction-storm in the transcript tail (**UNKNOWN** as a stable Claude/Grok machine-readable signal — do not scrape UI. Prefer "process gone" + "SEED age" + "collector rows with no COW act").
2. **TidyUP if a COSMOS session is still marked open** — `close_session` writes SEED. If the dying process was Cowork and never called `close_session`, the last SEED is stale: the driver must treat that as `OPEN_CONTEXT` and still BootUP from whatever SEED+BUCm+BACKLOG exist (fail visible, not silent).
3. **Arm resume_gate** — if `PAUSE.flag` is `hold` from TidyUP, rewrite to `mode=resume_gate` + `auto_resume_at=now+grace` unless a HOLD reason says Keith stopped the mesh. That is already canon.
4. **Spawn a FRESH headless orchestrator** (not `--continue`):

```
grok --single "<BootUP prompt>" -m <model> --output-format json --always-approve --max-turns 60 --cwd V:\A\Ai\COSMOS --prompt-file <docs or live prompt>
```

   or the F5 prepaid twin:

```
claude -p --permission-mode dontAsk --output-format json --add-dir V:\A --add-dir V:\Ai --cwd V:\A\Ai\COSMOS
```

   Prompt (file on disk, not invented at fire time): read `BUCm.toml` → `CLAUDE.md` → `docs/FINAL_ARCHITECTURE.md` → `live/state/SEED.json` under HMAC → `docs/BACKLOG.md` + `MOTIF_TRACKER.md` + DHx → collector index → **auto-resume the route** (the resume-gate default). Do **not** use `--bare` (BootUP needs `CLAUDE.md`). Do **not** use `--restore-code`.
5. **Record** `sessionId` / `session_id`, pid, spawned_at, rail, into `live/state/control/RESESSION.json`. Next tick: if pid alive, do nothing. If dead and BACKLOG still open, spawn **another fresh** session (not `--continue` of the dead full one).
6. **Lease** so two orchestrators cannot double-drop. One writer of the route. Fail-closed if the lease is held.

Clock: 1-minute `schtasks` (`COSMOS Resession`) as self-heal + onlogon, **or** a branch of WD2's 15s loop. Prefer a **separate satellite** so a hung spawn cannot pause retask. Logged-on only.

### 3.4 Context-full signal — honest UNKNOWN

No official Claude/Grok/Cursor headless flag means "this session is full; start a new one." Claude auto-compacts instead of exiting. Grok auto-compacts. Cowork auto-summarizes. Detecting "full" by scraping the Cowork UI is DOM-fragile and not a COSMOS clock.

**Practical detector (file-shaped, not UI):**

- orchestrator process missing, or
- last COW artifact (BUCm `written_at`, SEED `closed_epoch`, DHx marker) older than the grace, while BACKLOG still has open items, or
- `claude -p --output-format json` result carries a documented error string — **UNKNOWN** which field is stable; bind it at build time by running one filled-session probe, not by guessing now.

When in doubt: spawn fresh. A wasted BootUP is cheaper than a silent stall.

---

## 4. Minimal-disturbance UX — what still needs Keith

| Surface | Fully unattended? | What Keith still does | Honest limit |
|---|---|---|---|
| **COSMOS clocks (Layer A)** | YES, once ONLOGON wrappers exist | One elevated onlogon line (already owed, `docs/ORCHESTRATION.md`). Machine logged on, `V:` mounted, awake. | Sleep / logout stops `V:`. No stored password (Keith 2026-08-22). |
| **Grok `-p --always-approve` orchestrator** | YES after first `grok login` | Credentials once. Money if it falls onto `XAI_API_KEY`. HOLD if he wants it stopped. | Always-approve is real autonomy on the live tree. Deny-rules are the guard. Quota/wallet can still run out. |
| **Claude `-p --permission-mode dontAsk`** (already the dispatch recipe) | YES for tools on the allowlist | First `/login` or `setup-token`. **Do not** leave `ANTHROPIC_API_KEY` set if the prepaid seat is the wallet. | `dontAsk` **denies** anything not pre-allowed — safer than `bypassPermissions`, stricter than `auto`. `AskUserQuestion` / `requiresUserInteraction` MCP are denied. 5-hour + weekly seat windows still bind. |
| **Claude `-p --permission-mode auto`** | MOSTLY | Classifier can still skip actions in `-p` (no prompt fallback). | Not a stall; silent skips. Wrong for "never drop a MOTIF stage on the floor." |
| **`claude -p --continue` loop** | YES until the window is full | Same auth. Then it degrades. | Does not implement the wish. |
| **Claude Desktop local routine** | NO | Desktop app must stay open. First-run "always allow" per task. Sleep skips. | Fresh window, but Keith-shaped. Code tab, not Cowork. |
| **Cowork tab** | **NO documented unattended path** | Start Cowork. Re-grant folders every session (BUCm). | This is the failure. Do not build against it. |
| **Cursor `agent -p --force --trust`** | YES in docs | Install CLI (not on PATH today). `CURSOR_API_KEY`. `--trust` once per workspace. | Cannot be the first rail until the binary is the Cursor one. |
| **Cursor Cloud Agents** | YES (cloud) | Key already live (`Cursor COSMOS 2`). | Codes on GitHub; does not BootUP `V:\A\Ai\COSMOS\live`. |
| **HOLD vs resume_gate** | HOLD = Keith only | Saying stop. TidyUP hold. Mesh/dissertation boundary. | Auto-resume is the default. HOLD is the only stop. |
| **KDash one-click RESUME** | Minimal disturbance | Delete `PAUSE.flag` (or a KDash button that does). | Needed only when `mode=hold`. Not needed for `resume_gate`. |

**What a "single click" is worth:** clearing a HOLD. Everything else should move on the OS clock. Asking Keith to open Cowork + paste BootUP is the bug this wish exists to kill.

---

## Ranked options

| Rank | Option | R1 fresh window | R3 no human | R4 unattended perms | R5 Windows clock | R8 on this PC | Fit to the wish |
|---|---|---|---|---|---|---|---|
| **1** | **COSMOS-native resession satellite** spawning a **fresh** `grok -p` (dispatch recipe) seeded from SEED+BUCm+BACKLOG | YES | YES (resume_gate) | YES (`--always-approve`) | YES (new `COSMOS Resession` / WD2 branch) | YES | **The wish.** |
| **2** | Same satellite, **F5 twin**: fresh `claude -p --permission-mode dontAsk --add-dir …` | YES | YES | YES (`dontAsk` + allowlist) | YES | YES (`claude.exe` 2.1.220) | Same architecture, prepaid Claude seat. Use when the orchestrator must be Opus/Fable. |
| **3** | Fresh spawn + **one KDash/HOLD click** when `mode=hold` | YES | almost | YES | YES | YES | Minimal-disturbance fallback. |
| **4** | `grok -c -p` / `claude -p --continue` **schtasks loop** | **NO** (same transcript) | YES | YES if always-approve/dontAsk | YES | YES | Crash-recovery of a *roomy* session only. Supporting tactic, not the engine. |
| **5** | Claude Desktop **local scheduled task** (fresh session while app open) | YES | NO (app + first allows) | stalls in Manual | Desktop poll, not COSMOS | Desktop assumed | Vendor-owned; Code tab; sleep-fragile. |
| **6** | Cursor Cloud Agents API | n/a (cloud clone) | YES | n/a | n/a | Key live; no local CLI | Overflow **coding**, not local BootUP. |
| **7** | Cursor local `agent -p --force --trust --continue` | `--continue` = NO; fresh `-p` = YES | YES in docs | `--force --trust` | YES | **CLI not installed** | Install first, then it becomes a 3rd spawn rail. |
| **8** | Auto-restart **Cowork** | UNKNOWN / none | NO | folder grants die | NO | n/a | **No documented mechanism. Reject.** |
| **9** | `/loop` inside a live CLI session | NO | NO (needs open session) | inherits session | NO | n/a | In-session poll only. |
| **10** | `--fork-session` / `/branch` | NO (copies full history) | n/a | n/a | n/a | YES | Wrong primitive for a full window. |

---

## Recommendation

**Drive resession from COSMOS, not from vendor `--continue`.**

- **Clock + detector + lease:** a satellite (`cosmos_resession.py` class, **not** kernel) on the logged-on Windows clock.
- **Spawn rail #1:** Grok Build CLI, **fresh** `-p`/`--single`, `--always-approve`, `--cwd V:\A\Ai\COSMOS`, `--output-format json`, capture `sessionId`. Already proven by `cosmos_dispatch.py`. Already on PATH. Session store already at `C:\Users\Papa\.grok\sessions\V%3A%5CA%5CAi%5CCOSMOS\`.
- **Spawn rail #2 (F5):** `claude -p --permission-mode dontAsk --output-format json --add-dir V:\A --add-dir V:\Ai`. Capture `session_id`. Use when the orchestrator must be the prepaid Claude seat. Never `--bare` for BootUP. Never leave `ANTHROPIC_API_KEY` stealing the seat.
- **Seed:** `live/state/SEED.json` (verify HMAC/decl) + `BUCm.toml` + `docs/BACKLOG.md` + DHx + collector index. The prompt is a file on disk (BootUP script), not a one-liner in Task Scheduler.
- **`--continue` is reserved** for "the orchestrator PID died mid-turn and the window is still roomy" (Claude: SIGTERM leaves the turn unfinished; resume continues it). It is **not** the context-full path.
- **Cowork is not the engine.** The route continues on CLI. Keith opens Cowork when he wants that UI.
- **HOLD stays sacred.** `mode=hold` never self-clears. Everything else auto-resumes.

This matches canon: the Windows clock carries the overhead; Claude/Grok make the sparse decisions; carry-over is structural; fail-closed; do not take the live tree down to modify it.

---

## Concrete next build step (MOTIF stage 2+)

**Do not touch COSMOS core.** Stage-2 arch should specify, then stage-4 should land, a satellite:

1. **`cosmos/cosmos_resession.py`** (satellite, like `cosmos_watchdog2.py` / `cosmos_motif_driver.py`):
   - `--once` / `--loop`
   - `--root V:\A\Ai\COSMOS\live`
   - reads `PAUSE.flag` first (HOLD wins)
   - reads/writes `live/state/control/RESESSION.json` `{rail, pid, session_id, spawned_at, prompt_sha}`
   - spawn recipe **copied from** `cosmos_dispatch.py` (do not invent flags)
   - `--prompt-file` → a tracked prompt at `docs/AUTO_RESESSION_PROMPT.md` (BootUP order from `BUCm.toml [read_order]` + "auto-resume the BACKLOG; you are COW; drop work, do not search in your own context")
2. **`schtasks` name `COSMOS Resession`** — 1-minute self-heal + onlogon, logged-on only, no `.bat`.
3. **Lease** so WD2 and the orchestrator cannot double-assign the same BACKLOG row (one orchestrator PID in RESESSION.json is the mutex).
4. **Runtime-binding gate (stage 8):** kill or wait out the current Grok/Cowork window; the satellite must emit a **new** `sessionId` in `RESESSION.json` **and** a new DHx marker / queue drop **without** a human prompt. Quote those artifacts. A green log is not evidence.

Stage-2 arch still needed (vendor-plural: how to detect quiet; grok vs claude vs both; what goes in the prompt file; how thin SEEDs are packed at TidyUP). This document is the rubric that arch must use.

---

## Flag cheat-sheet (copy-paste, verified)

### Claude Code 2.1.220 — this machine

```
claude -p "PROMPT" --output-format json --permission-mode dontAsk --add-dir V:\A --add-dir V:\Ai
# capture .session_id
claude -p "follow-up" --resume "<session_id>" --output-format json --permission-mode dontAsk --add-dir V:\A --add-dir V:\Ai
claude -p "follow-up" --continue --output-format json --permission-mode dontAsk
```

Transcripts: `%USERPROFILE%\.claude\projects\V--A-Ai-COSMOS\<uuid>.jsonl`

### Grok Build CLI 1.0.5 — this machine

```
grok --single "PROMPT" --cwd V:\A\Ai\COSMOS --always-approve --output-format json --max-turns 60
# capture .sessionId
grok -c -p "follow-up" --cwd V:\A\Ai\COSMOS --always-approve --output-format json
grok --resume "<uuid>" -p "follow-up" --cwd V:\A\Ai\COSMOS --always-approve --output-format json
```

Transcripts: `%USERPROFILE%\.grok\sessions\V%3A%5CA%5CAi%5CCOSMOS\`

`--session-id` = **new** UUID only. `--add-dir` = **does not exist**.

### Cursor CLI — official, **not on PATH here**

```
agent -p --force --trust --output-format json "PROMPT"
agent -p --force --trust --continue "follow-up"
agent --resume="<chat-id>" -p --force --trust "follow-up"
```

Session store path: **UNKNOWN** (official docs fetched this session do not name it).
