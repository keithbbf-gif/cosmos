# MCP REFERENCE SERVERS HANDS — G46 scout return

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim. **No COSMOS core code was edited.**
**Assignment:** maker-docs sweep (DHx) — every official MCP **reference-server** hand COSMOS could fire.

**What this is (one sentence):** the MCP steering group's small set of **reference implementations** — not a marketplace. Community / vendor servers live on the [MCP Registry](https://registry.modelcontextprotocol.io/); this file covers only what `github.com/modelcontextprotocol/servers` currently lists (7 live) plus the archived set it still names (SQLite, PostgreSQL, Puppeteer, GitHub, …).

**Filter:** a surface is a HAND only if COSMOS can **do** something with it (read/write files, git, fetch a URL, query a DB, persist a graph, think in steps, drive a browser). Protocol chrome (sampling/elicitation demos) is kept only on the Everything row, because that is the point of that server.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks (native worker, MCP-client, DOM, spend-gate, vendor-plural). Equal power, cheaper wins. The **server binary is always $0** (MIT / Apache-2.0). Metered **backend APIs** (Brave, Maps, AWS, EverArt, Slack, GitHub/GitLab tokens) sit below the local-only cluster.

**Official warning (do not ignore):** the live README states these are **educational reference implementations, not production-ready**. Evaluate the threat model; do not treat `npx -y @modelcontextprotocol/server-*` as a hardened COSMOS module.

---

## Official documentation URLs (the real ones)

Fetched 2026-08-25. These are the canonical pages — not third-party PDF scrapes.

### Protocol + docs site

| what | URL |
|------|-----|
| Docs home / "what is MCP" | https://modelcontextprotocol.io/ |
| Intro (versioned, current `2026-07-28`) | https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro |
| Full docs index (llms.txt) | https://modelcontextprotocol.io/llms.txt |
| Architecture | https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture |
| Server concepts | https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts |
| Client concepts (roots, sampling, elicitation) | https://modelcontextprotocol.io/docs/2026-07-28/learn/client-concepts |
| **Connect to local MCP servers** (stdio + Claude Desktop config) | https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers |
| Connect to remote MCP servers | https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-remote-servers |
| Build a server | https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server |
| Build a client | https://modelcontextprotocol.io/docs/2026-07-28/develop/build-client |
| Example servers page (mirrors the 7 live refs) | https://modelcontextprotocol.io/examples |
| SDKs | https://modelcontextprotocol.io/docs/2026-07-28/sdk |
| Authorization | https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization |
| Security best practices | https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices |
| MCP Inspector | https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector |
| Debugging | https://modelcontextprotocol.io/docs/2026-07-28/tools/debugging |
| Spec (current `2026-07-28`) | https://modelcontextprotocol.io/specification/2026-07-28/ |
| **stdio transport** (current) | https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio |
| **Streamable HTTP** transport (current; replaced SSE) | https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http |
| Transports overview `2025-03-26` (stdio + Streamable HTTP; SSE deprecated) | https://modelcontextprotocol.io/specification/2025-03-26/basic/transports |
| Legacy HTTP+SSE transport `2024-11-05` | https://modelcontextprotocol.io/specification/2024-11-05/basic/transports |
| Tools | https://modelcontextprotocol.io/specification/2026-07-28/server/tools |
| Resources | https://modelcontextprotocol.io/specification/2026-07-28/server/resources |
| Prompts | https://modelcontextprotocol.io/specification/2026-07-28/server/prompts |
| Roots | https://modelcontextprotocol.io/specification/2026-07-28/client/roots |
| MCP Registry | https://registry.modelcontextprotocol.io/ |
| Registry about | https://modelcontextprotocol.io/registry/about |
| Python SDK docs | https://py.sdk.modelcontextprotocol.io/ |
| Python SDK (run / transports) | https://py.sdk.modelcontextprotocol.io/run/ |
| Spec + docs source repo | https://github.com/modelcontextprotocol/modelcontextprotocol |

### Reference-server repos (the inventory)

| what | URL |
|------|-----|
| **Live reference servers (THIS is the list)** | https://github.com/modelcontextprotocol/servers |
| Live README (raw) | https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md |
| LICENSE (Apache-2.0 new + MIT existing) | https://github.com/modelcontextprotocol/servers/blob/main/LICENSE |
| Archived reference servers | https://github.com/modelcontextprotocol/servers-archived |
| Everything | https://github.com/modelcontextprotocol/servers/tree/main/src/everything |
| Everything features (full tool/prompt/resource list) | https://github.com/modelcontextprotocol/servers/blob/main/src/everything/docs/features.md |
| Fetch | https://github.com/modelcontextprotocol/servers/tree/main/src/fetch |
| Filesystem | https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem |
| Git | https://github.com/modelcontextprotocol/servers/tree/main/src/git |
| Memory | https://github.com/modelcontextprotocol/servers/tree/main/src/memory |
| Sequential Thinking | https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking |
| Time | https://github.com/modelcontextprotocol/servers/tree/main/src/time |

There is **no official PDF**. Third-party "MCP Reference Servers User/Admin Guide" PDFs on doccompiler.ai are scrapes, not canon.

---

## Inventory as of 2026-08-25

**Live (7)** — `modelcontextprotocol/servers`, maintained by the MCP steering group:

| server | lang | package | docker |
|--------|------|---------|--------|
| Everything | TypeScript | `@modelcontextprotocol/server-everything` | `mcp/everything` |
| Fetch | Python | `mcp-server-fetch` | `mcp/fetch` |
| Filesystem | TypeScript | `@modelcontextprotocol/server-filesystem` | `mcp/filesystem` |
| Git | Python | `mcp-server-git` | `mcp/git` |
| Memory | TypeScript | `@modelcontextprotocol/server-memory` | `mcp/memory` |
| Sequential Thinking | TypeScript | `@modelcontextprotocol/server-sequential-thinking` | `mcp/sequentialthinking` |
| Time | Python | `mcp-server-time` | `mcp/time` |

**Archived (13 still named on the live README)** — `modelcontextprotocol/servers-archived`. **No security updates.** Git is listed in the archive snapshot *and* remains live in the current repo (use the live Git). Archived GitHub is superseded by [`github/github-mcp-server`](https://github.com/github/github-mcp-server). Archived Slack is now maintained by [Zencoder](https://github.com/zencoderai/slack-mcp-server). Archived Brave Search is replaced by [brave/brave-search-mcp-server](https://github.com/brave/brave-search-mcp-server).

Python live servers (Fetch, Git, Time) currently require **MCP Python SDK 1.x** (`mcp>=1.29.0,<2`). SDK 2.0 renamed APIs; the port is in progress per each README.

---

## Licensing / cost floor

| fact | official source | COSMOS implication |
|------|-----------------|--------------------|
| Live repo: **Apache-2.0 for new contributions, existing code MIT** | [LICENSE](https://github.com/modelcontextprotocol/servers/blob/main/LICENSE) | Tool cost = **$0**. Copy, run, wrap. |
| Each live server README also says **MIT** for that server | filesystem / git / fetch / memory / sequential-thinking / time / everything READMEs | Same: free to use. |
| Archived servers: **MIT**, unmaintained | [servers-archived README](https://github.com/modelcontextprotocol/servers-archived) | Still $0 binary. **No security guarantee.** Prefer live replacements. |
| MCP protocol + official SDKs: OSS | [python-sdk](https://github.com/modelcontextprotocol/python-sdk), [typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk) | Client cost = $0. Inference still bills whichever rail *calls* the tools. |
| **No MCP seat, no MCP SaaS bill** | — | Spend-gate the **backend** (GitHub PAT rate limits, Brave queries, AWS Bedrock, Maps, Slack, Sentry, EverArt), never the MCP wrapper. |
| Local-only servers (filesystem, git, memory, time, sequential-thinking, sqlite, everything, puppeteer) | those READMEs | **$0** including at runtime. Highest-ranked cluster. |

---

## Transports (how the bytes move)

Official current spec (`2025-03-26` onward, still current in `2026-07-28`): **two** standard transports. Clients **SHOULD** support **stdio**.

| transport | what it is | who uses it here | COSMOS default |
|-----------|------------|------------------|----------------|
| **stdio** | Client **spawns** the server as a subprocess. JSON-RPC newline-delimited on stdin/stdout. Logs on stderr. | **All 7 live servers.** Default for npx/uvx/pip/docker `-i`. | **Preferred.** Local, no open port, matches attempt-private workers. |
| **Streamable HTTP** | Independent HTTP process. POST+GET on one MCP endpoint; optional SSE *inside* the HTTP stream. Replaced HTTP+SSE. | **Everything** only, among the reference set: `npx @modelcontextprotocol/server-everything streamableHttp` | Use only if COSMOS is hosting a multi-client test endpoint. Bind 127.0.0.1. Origin-header check required. |
| **HTTP+SSE** (deprecated `2024-11-05`) | GET `/sse` + POST `/message`. | **Everything** still: `npx @modelcontextprotocol/server-everything sse` / `npm run start:sse`. Python SDK: `mcp.run(transport="sse")` "exists for clients that haven't moved." | **Do not build new COSMOS code on this.** |

Python SDK transport table ([py.sdk.modelcontextprotocol.io/run](https://py.sdk.modelcontextprotocol.io/run/)): `stdio` = default local; `streamable-http` = deploy; `sse` = don't.

---

## Auth (the servers themselves)

Local reference servers **have no MCP-level login**. Auth is:

1. **OS identity of the spawned process** (your user / the Job-Object worker).
2. **Allowlists** (filesystem roots, git `repo_path`, sqlite `--db-path`).
3. **Env tokens for archived cloud wrappers** (PAT, API keys) — Keith owns; store under `live/config/`; never in the tree.

Remote MCP (not these reference servers) uses OAuth 2.1 per [authorization docs](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization). That is a different class.

---

## How COSMOS reaches these (one pattern)

Core stays sole ledger writer. An MCP reference server is **never** a second authority. It is a **hand** a worker or an agent-host can call.

| Lane | Mechanism | When |
|------|-----------|------|
| **A. MCP-client stdio (preferred)** | Official Python SDK client (`mcp`) or TS SDK: spawn `npx` / `uvx` / `python -m …` as a subprocess, JSON-RPC over stdio, list/call tools. | COSMOS-as-host: brains get tools without giving them a raw shell. |
| **B. Native CLI worker** | Same argv, but Core treats the process as a Job-Object worker and maps tool results into ledger events. | Queue jobs that *are* "read this dir / fetch this URL / git status this attempt repo." |
| **C. Existing MCP hosts** | Claude Code, Cursor, VS Code Copilot, Codex — they already speak MCP. Drop the config JSON; the host spawns the server. | Coding lanes (DHx Cursor / CC). Do not double-write the live tree; fenced commit still owns publish. |
| **D. Docker stdio** | `docker run -i --rm … mcp/<name>`. Bind-mount only the attempt workspace. | Isolation when Node/Python on the host is the wrong version. |
| **E. Streamable HTTP / SSE** | Everything server only. | Protocol tests of COSMOS-as-client. Not a production rail. |
| **F. Inspector** | `npx @modelcontextprotocol/inspector <spawn cmd>` | Debug a server before wiring it. |
| **G. DOM** | n/a for these servers. Puppeteer *is* the DOM-shaped archived hand. | Canon: DOM first when an *API* can run out; these local servers cannot run out of credit. |

**Windows npx wrap** (official live README): Claude-shaped config must use `cmd /c` around `npx`. `uvx` entries stay unwrapped.

```json
{
  "mcpServers": {
    "memory": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Fenced-commit mapping:** Filesystem `write_file` / `edit_file` / `move_file` and Git `git_commit` / `git_add` write the **workspace they were allowed**. Point them at an **attempt-private** tree. Core reviews, then the fenced commit gateway publishes. Never allow these servers onto `V:\A\Ai\COSMOS` live or `live\` as a second writer.

**Default COSMOS allowlist for filesystem:** the attempt workspace only — not `V:\A`, not `live\ledger`, not `live\config`.

---

## Ranking table

| # | name | status | kind | HANDS (what it DOES) | tools (official names) | run / transport | config shape | auth | cost | power | how COSMOS reaches it |
|---|------|--------|------|----------------------|------------------------|-----------------|--------------|------|------|-------|------------------------|
| 1 | **Filesystem** | **live** | local FS | Sandboxed read/write/search of **allowed directories only**. 13 tools. Roots protocol can replace the CLI allowlist at runtime. Destructive tools annotated (`write_file` overwrite, `edit_file` non-idempotent, `move_file` deletes source). `openWorldHint: false`. | `read_text_file`, `read_media_file`, `read_multiple_files`, `write_file`, `edit_file`, `create_directory`, `list_directory`, `list_directory_with_sizes`, `move_file`, `search_files`, `directory_tree`, `get_file_info`, `list_allowed_directories` | **npx stdio.** `npx -y @modelcontextprotocol/server-filesystem <dir> [<dir>…]`. Docker: `mcp/filesystem` + bind-mounts to `/projects`. | Claude: `mcpServers.filesystem.command=npx` + allowed dirs in `args`. VS Code: `servers.filesystem`. **Windows:** `cmd /c npx …`. Must have ≥1 allowed dir (CLI **or** client roots). | none (OS user + allowlist) | **free** (MIT/Apache) | **highest** | MCP-client stdio **or** native worker. Allow **only** the attempt workspace. Do not point at ledger / config / live tree. Complements native resolver — this is the *agent-brain* FS, not Core's. |
| 2 | **Git** | **live** | local git | Read + mutate a git repo: status, staged/unstaged/target diffs, add, reset, commit (returns hash), log (date filters), show, branch list/create, checkout. **12 tools.** Early development; surface can change. | `git_status`, `git_diff_unstaged`, `git_diff_staged`, `git_diff`, `git_commit`, `git_add`, `git_reset`, `git_log`, `git_create_branch`, `git_checkout`, `git_show`, `git_branch` | **uvx stdio** (recommended): `uvx mcp-server-git [--repository path]`. pip: `pip install mcp-server-git` → `python -m mcp_server_git`. Docker: `mcp/git` + bind-mount. | `"command":"uvx","args":["mcp-server-git","--repository","path/to/git/repo"]`. Every tool also takes `repo_path`. | none (needs a git repo the process can write) | **free** | **highest** | uvx worker against the **attempt** clone. `git_commit` here is **not** fenced publish — it is a commit inside the attempt repo. Core then fences. Prefer native `git` for Core jobs; MCP Git is for brains that should not get a shell. Requires Python MCP SDK 1.x. |
| 3 | **Fetch** | **live** | web GET | Fetch a URL, convert HTML → markdown (or raw). Chunk via `start_index`. Obeys **robots.txt** for model-initiated tool calls, not user-initiated prompts. Optional `--ignore-robots-txt`, `--user-agent=`, `--proxy-url`. **Caution: can hit local/internal IPs.** | `fetch` (`url`, `max_length` default 5000, `start_index`, `raw`). Prompt: `fetch`. | **uvx stdio:** `uvx mcp-server-fetch`. pip: `python -m mcp_server_fetch`. Docker: `mcp/fetch`. | `"command":"uvx","args":["mcp-server-fetch"]`. Windows: set `env.PYTHONIOENCODING=utf-8` (timeout footgun). | none (open web; optional proxy) | **free** (binary + HTTP GET; no API key) | **highest** | uvx MCP-client. DOM-second for *known URLs*. Does not replace Playwright/browser-use for JS apps. Pin `--user-agent`; do **not** `--ignore-robots-txt` unless Keith says so. Spend-gate is unnecessary (no vendor meter) but still log the URL in the ledger. SDK 1.x. |
| 4 | **Memory** | **live** | local KG | Persistent **knowledge graph** on disk (JSONL). Entities + directed relations + atomic observations. CRUD + search. Resource `memory://knowledge-graph` (JSON); mutations emit `notifications/resources/updated`. | `create_entities`, `create_relations`, `add_observations`, `delete_entities`, `delete_observations`, `delete_relations`, `read_graph`, `search_nodes`, `open_nodes` | **npx stdio:** `npx -y @modelcontextprotocol/server-memory`. Docker: `mcp/memory` + volume `claude-memory:/app/dist`. | `"command":"npx","args":["-y","@modelcontextprotocol/server-memory"]` + `env.MEMORY_FILE_PATH` (default `memory.jsonl` in the **server directory** — isolate per project). Windows: `cmd /c`. | none | **free** | **high** | MCP-client with `MEMORY_FILE_PATH` under `live/state/` or the attempt workspace — **never** a second SEED. Architecture decision 10: carry-over is `state/SEED.json`. Memory MCP is optional long-term *facts* for a brain, not session handoff. Without `MEMORY_FILE_PATH`, all hosts share one file. |
| 5 | **SQLite** | **archived** | local SQL | Query + mutate a SQLite file. SELECT / INSERT-UPDATE-DELETE / CREATE TABLE / list / describe. Demo "business insights" memo resource. | `read_query`, `write_query`, `create_table`, `list_tables`, `describe-table`, `append_insight`. Resource: `memo://insights`. Prompt: `mcp-demo`. | **uvx stdio (historical):** `uvx mcp-server-sqlite --db-path <file>`. Docker: `mcp/sqlite --db-path /mcp/test.db`. | `"command":"uvx","args":["mcp-server-sqlite","--db-path","~/test.db"]` | none (file path is the auth) | **free** (unmaintained) | **high** (local DB) **with a hard no** | **Do not** point this at Core's service-private projection SQLite or the ledger. Ledger is JSONL authority; SQLite is cache. If used at all: a **copy** of a worker DB in the attempt workspace. Prefer a COSMOS-owned module over this archive. |
| 6 | **Sequential Thinking** | **live** | reasoning scaffold | One tool the model calls **repeatedly** to keep a revisable thought sequence (branch, revise, extend total). Does not solve anything by itself — it is structured scratchpad. | `sequential_thinking` (`thought`, `nextThoughtNeeded`, `thoughtNumber`, `totalThoughts`, optional `isRevision`/`revisesThought`/`branchFromThought`/`branchId`/`needsMoreThoughts`) | **npx stdio:** `npx -y @modelcontextprotocol/server-sequential-thinking`. Docker: `mcp/sequentialthinking`. `DISABLE_THOUGHT_LOGGING=true` to quiet. | `"command":"npx","args":["-y","@modelcontextprotocol/server-sequential-thinking"]` | none | **free** | **high** (planning) | Attach to coding/brain hosts (Cursor, Claude Code, COSMOS-as-client) for migration plans / architecture forks. Cheap. No filesystem side effects. |
| 7 | **Time** | **live** | clock | Current time in an IANA zone; convert `HH:MM` between zones. Auto-detects system TZ; override `--local-timezone=`. | `get_current_time` (`timezone`), `convert_time` (`source_timezone`, `time`, `target_timezone`) | **uvx stdio:** `uvx mcp-server-time`. pip: `python -m mcp_server_time`. Docker: `mcp/time` + `LOCAL_TIMEZONE`. | `"command":"uvx","args":["mcp-server-time"]` or `python -m mcp_server_time --local-timezone=America/Chicago` | none | **free** | **med-high** | uvx MCP-client. Grounds "what time is it" without an LLM clock hallucination. Pair with COSMOS scheduler / return-watcher. SDK 1.x. |
| 8 | **Puppeteer** | **archived** | DOM / browser | Real Chromium: navigate, screenshot, click, hover, fill, select, `evaluate` JS. Resources: `console://logs`, `screenshot://<name>`. NPX opens a window; Docker is headless. **Can reach local files and internal IPs.** | `puppeteer_navigate`, `puppeteer_screenshot`, `puppeteer_click`, `puppeteer_hover`, `puppeteer_fill`, `puppeteer_select`, `puppeteer_evaluate` | **npx stdio:** `npx -y @modelcontextprotocol/server-puppeteer`. Docker: `mcp/puppeteer` + `DOCKER_CONTAINER=true`. Env `PUPPETEER_LAUNCH_OPTIONS` JSON; `ALLOW_DANGEROUS`. | `"command":"npx","args":["-y","@modelcontextprotocol/server-puppeteer"]` | none (browser = the user) | **free** binary; **unmaintained** | **high** (DOM rail) | Archived — prefer live Playwright MCP / COSMOS `cosmos_browser`. If used: Job-Object, ephemeral profile, `allowDangerous=false`. Canon DOM-first when an API can lapse; this *is* that DOM hand. |
| 9 | **PostgreSQL** | **archived** | SQL (read-only) | One tool: run SQL in a **READ ONLY** transaction. Resources: `postgres://<host>/<table>/schema` (JSON columns/types). | `query` (`sql`) | **npx stdio:** `npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb`. Docker: `mcp/postgres` + URL (`host.docker.internal` on Mac). | args = connection URL (`postgresql://user:pass@host:port/db`) | **DB URL** (user/pass in the URL) | **free** binary; DB is yours | **high** (read) | Archived. If COSMOS ever inspects an external Postgres, spawn this (or a maintained fork) with a **read-only** role. Never the ledger. Prefer a maintained Postgres MCP from the registry for production. |
| 10 | **Redis** | **archived** | KV | set/get/delete/list keys. Optional TTL on set. Pattern list default `*`. | `set`, `get`, `delete`, `list` | **npx stdio:** `npx -y @modelcontextprotocol/server-redis redis://localhost:6379`. Docker: `mcp/redis`. | URL in args or `REDIS_URL`. Windows: WSL Redis or Memurai. | Redis AUTH in URL if required | **free** binary | **med-high** | Only if a worker already runs Redis. Not a COSMOS primitive (ledger is JSONL). |
| 11 | **Everything** | **live** | protocol test harness | **Not a useful production server.** Exercises the whole protocol: tools, prompts, resources, subscriptions, logging, sampling, elicitation (form + URL mode), progress, **Tasks (SEP-1686)**. Unique among refs: **stdio + SSE + Streamable HTTP**. | 19 tools: `echo`, `get-annotated-message`, `get-env`, `get-resource-links`, `get-resource-reference`, `get-roots-list`, `gzip-file-as-resource`, `get-structured-content`, `get-sum`, `get-tiny-image`, `trigger-long-running-operation`, `toggle-simulated-logging`, `toggle-subscriber-updates`, `trigger-elicitation-request`, `trigger-url-elicitation`, `trigger-sampling-request`, `simulate-research-query`, `trigger-sampling-request-async`, `trigger-elicitation-request-async`. Prompts: `simple-prompt`, `args-prompt`, `completable-prompt`, `resource-prompt`. Resources: `demo://resource/dynamic/{text,blob}/{index}`, `demo://resource/static/document/<file>`, `demo://resource/session/<name>`. | Default **stdio:** `npx -y @modelcontextprotocol/server-everything` or `… stdio`. **SSE (deprecated):** `… sse`. **Streamable HTTP:** `… streamableHttp`. From source: `npm run start:sse` / `start:streamableHttp`. | stdio: same npx shape as Memory. HTTP: client URL to the process's MCP endpoint. | none (`get-env` **dumps process env** — do not run with secrets in the environment) | **free** | **high as a client-conformance test**, **low as a product hand** | Use to prove COSMOS-as-MCP-client (roots, tasks, elicitation, sampling) against a known-good server. **Never** in a worker that holds `live/config` secrets — `get-env` is a leak. |
| 12 | **GitHub (archived ref)** | **archived; superseded** | GitHub API wrapper | 26 tools: files, repos, issues, PRs, reviews, merge, search code/issues/users, forks, branches, commits. | `create_or_update_file`, `push_files`, `search_repositories`, `create_repository`, `get_file_contents`, `create_issue`, `create_pull_request`, `fork_repository`, `create_branch`, `list_issues`, `update_issue`, `add_issue_comment`, `search_code`, `search_issues`, `search_users`, `list_commits`, `get_issue`, `get_pull_request`, `list_pull_requests`, `create_pull_request_review`, `merge_pull_request`, `get_pull_request_files`, `get_pull_request_status`, `update_pull_request_branch`, `get_pull_request_comments`, `get_pull_request_reviews` | **npx stdio:** `npx -y @modelcontextprotocol/server-github`. Docker: `mcp/github`. | `env.GITHUB_PERSONAL_ACCESS_TOKEN` | **PAT** (`repo` or `public_repo`) | **free** binary; GitHub API rate limits | **high but do not adopt this package** | **Do not install the archived server.** Use [`github/github-mcp-server`](https://github.com/github/github-mcp-server) (see `docs/research/GITHUB_HANDS.md` row 8) or native `gh`. Same hands, maintained. |
| 13 | **GitLab (archived ref)** | **archived** | GitLab API wrapper | Files, projects, issues, MRs, fork, branch. 9 tools. | `create_or_update_file`, `push_files`, `search_repositories`, `create_repository`, `get_file_contents`, `create_issue`, `create_merge_request`, `fork_repository`, `create_branch` | **npx stdio:** `npx -y @modelcontextprotocol/server-gitlab` | `GITLAB_PERSONAL_ACCESS_TOKEN` + optional `GITLAB_API_URL` (default `https://gitlab.com/api/v4`) | **PAT** (`api` / `write_repository`) | **free** binary; GitLab API limits | **high but unmaintained** | Prefer `glab` (already the COSMOS forge CLI) + `docs/research/GITLAB_HANDS.md`. Archived MCP is a fallback for agent brains only. |
| 14 | **Slack (archived ref)** | **archived; moved to Zencoder** | Slack bot | List channels, post, thread reply, react, history, thread replies, users, profile. | `slack_list_channels`, `slack_post_message`, `slack_reply_to_thread`, `slack_add_reaction`, `slack_get_channel_history`, `slack_get_thread_replies`, `slack_get_users`, `slack_get_user_profile` | **npx stdio:** `npx -y @modelcontextprotocol/server-slack` | `SLACK_BOT_TOKEN` (`xoxb-`), `SLACK_TEAM_ID` (`T…`), optional `SLACK_CHANNEL_IDS` | Slack app bot token + scopes (`channels:history/read`, `chat:write`, `reactions:write`, `users:read`, `users.profile:read`) | **free** binary; Slack plan is Keith's | **med-high** | Prefer the Zencoder fork if Slack becomes a COSMOS rail. Token in `live/config/`. Do not let an agent `chat:write` without a lease. |
| 15 | **Google Drive (archived)** | **archived** | GDrive read | Search files; resources `gdrive:///<file_id>` (Docs→md, Sheets→CSV, Slides→text, Drawings→PNG). | `search` (`query`) | **npx stdio** after OAuth dance: `npx -y @modelcontextprotocol/server-gdrive`. Auth: `node ./dist auth` / docker `mcp/gdrive auth`. | `GDRIVE_CREDENTIALS_PATH`; OAuth desktop client `gcp-oauth.keys.json`; scope `drive.readonly` | **Google OAuth** (Keith) | **free** binary; Google API quotas | **med-high** | GDX is already on the mount block (`X:\My Drive\BTS_SGH_Handoff`) via file tools. This MCP is API-shaped Drive. OAuth is a Keith action; DOM fallback if AUTH_REQUIRED. Unmaintained. |
| 16 | **Brave Search (archived)** | **archived; official successor exists** | web search API | Web search + local-business search (falls back to web). | `brave_web_search` (`query`,`count`≤20,`offset`≤9), `brave_local_search` | **npx stdio:** `npx -y @modelcontextprotocol/server-brave-search` | `BRAVE_API_KEY` | Brave Search API key | binary **free**; API **free tier 2,000 queries/mo** then paid | **high search, not free-unbounded** | Prefer [brave/brave-search-mcp-server](https://github.com/brave/brave-search-mcp-server). Spend-gate the query meter. Fetch (row 3) is the $0 known-URL path; Brave is discovery. |
| 17 | **Sentry (archived)** | **archived** | error intel | One tool: fetch a Sentry issue by ID or URL (title, status, level, counts, full stacktrace). Prompt `sentry-issue`. | `get_sentry_issue` | **uvx stdio:** `uvx mcp-server-sentry --auth-token TOKEN` | `--auth-token` or `SENTRY_AUTH_TOKEN` | Sentry auth token | **free** binary; Sentry product tiers | **med** | Only if COSMOS incidents should pull stacktraces. Token in `live/config/`. |
| 18 | **Google Maps (archived)** | **archived** | Maps API | Geocode, reverse, place search/details, distance matrix, elevation, directions. | `maps_geocode`, `maps_reverse_geocode`, `maps_search_places`, `maps_place_details`, `maps_distance_matrix`, `maps_elevation`, `maps_directions` | **npx stdio:** `npx -y @modelcontextprotocol/server-google-maps` | `GOOGLE_MAPS_API_KEY` | Google Maps API key | binary **free**; **Maps API is billed** | **med** (paid backend) | Keith mints the key; spend-gate every call. Not a COSMOS kernel need. |
| 19 | **AWS KB Retrieval (archived)** | **archived** | Bedrock RAG | Retrieve chunks from an AWS Knowledge Base. | `retrieve_from_aws_kb` (`query`, `knowledgeBaseId`, `n` default 3) | **npx stdio:** `npx -y @modelcontextprotocol/server-aws-kb-retrieval` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` | AWS IAM (Bedrock Agent Runtime) | binary **free**; **AWS billed** | **med** (paid) | Only if a Bedrock KB exists. Prefer IAM role over long-lived keys. |
| 20 | **EverArt (archived)** | **archived** | image gen API | Generate images (FLUX / SD3.5 / Recraft); opens URL in browser. | `generate_image` (`prompt`, optional `model`, `image_count`) | **npx stdio:** `npx -y @modelcontextprotocol/server-everart` | `EVERART_API_KEY` | EverArt API key | binary **free**; **generation is paid** | **low-med** | COSMOS image path is Imagine / other rails. Do not add a dead vendor. |
| 21 | **MCP Inspector** | **official tool** (not a reference server) | debug client | GUI / CLI / TUI that **is** an MCP client: spawn any server, list tools, call them, inspect resources/prompts. | (client, not a tool server) | `npx @modelcontextprotocol/inspector uvx mcp-server-fetch` (pattern from each README) | — | none | **free** | **infra / highest for bring-up** | First step before wiring a server into Core. Docs: https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector |
| 22 | **Official Python / TS SDKs** | **live** | client+server libraries | Build COSMOS-as-MCP-**client** (call any of the above) or COSMOS-as-MCP-**server** (expose Core tools to Claude/Cursor). Transports: stdio, Streamable HTTP, SSE-legacy. | N/A (you register tools) | Python: https://py.sdk.modelcontextprotocol.io/ · TS: https://github.com/modelcontextprotocol/typescript-sdk | client config is whatever you spawn | OAuth only if you serve remote HTTP | **free** (OSS) | **highest as the wire** | This is how lanes A/B exist. Python SDK 2.x is current stable for **new** COSMOS code; the three live **Python reference servers** are still on 1.x — do not mix those servers into a 2.x import graph until they port. |

---

## Live servers — tools, run, config (detail)

### 1. Filesystem — `@modelcontextprotocol/server-filesystem`

**Does:** secure file operations inside an allowlist. CLI dirs **or** MCP Roots (client `roots/list`; `roots/list_changed` replaces the allowlist). Empty allowlist + no roots ⇒ init error.

**Run**

```text
npx -y @modelcontextprotocol/server-filesystem V:\path\allowed1 V:\path\allowed2
```

Docker (all mounts under `/projects`; `,ro` = read-only):

```text
docker run -i --rm --mount type=bind,src=<host>,dst=/projects/<name> mcp/filesystem /projects
```

**Client config (Claude Desktop / generic stdio host)**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "cmd",
      "args": [
        "/c", "npx", "-y", "@modelcontextprotocol/server-filesystem",
        "V:\\A\\Ai\\COSMOS\\live\\work"
      ]
    }
  }
}
```

VS Code workspace file uses `"servers"` (not `"mcpServers"`). Official local-connect tutorial: https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers

**COSMOS note:** 9 read-only tools vs 4 writers. Always `edit_file` with `dryRun=true` first. `read_media_file` returns image/audio content blocks — useful for KDash asset checks, not for ledger bytes.

---

### 2. Git — `mcp-server-git`

**Does:** GitPython-shaped tools on a `repo_path` (or `--repository` default).

**Run**

```text
uvx mcp-server-git --repository V:\path\to\repo
python -m mcp_server_git --repository V:\path\to\repo
```

**Client config**

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "V:\\path\\to\\attempt"]
    }
  }
}
```

Debug: `npx @modelcontextprotocol/inspector uvx mcp-server-git`

**Missing vs a real git CLI (so COSMOS still wants native `git`):** no `init`, no remotes (`fetch`/`pull`/`push`), no stash, no merge/rebase, no tag, no blame. This is workspace-local mutation, not forge publish.

---

### 3. Fetch — `mcp-server-fetch`

**Does:** HTTP GET + readability-style markdown. Optional Node HTML simplifier if Node is installed.

**Run:** `uvx mcp-server-fetch`

**Flags:** `--ignore-robots-txt` · `--user-agent=…` · `--proxy-url=…`

User-agents (official):

- tool call: `ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)`
- prompt: `ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)`

**Windows:** `PYTHONIOENCODING=utf-8` in `env` or the server times out on encoding.

**COSMOS note:** Fetch is the $0 "read this URL" hand. Firecrawl / paid search sit below it. SSRF: the README's internal-IP caution is real — wrap with a URL allow/deny if Core ever calls this unattended.

---

### 4. Memory — `@modelcontextprotocol/server-memory`

**Does:** local entity-relation-observation graph. Default file `memory.jsonl` **inside the npm package dir** unless `MEMORY_FILE_PATH` is set.

**Run:** `npx -y @modelcontextprotocol/server-memory`

**Isolate**

```json
"env": { "MEMORY_FILE_PATH": "V:\\A\\Ai\\COSMOS\\live\\state\\mcp_memory.jsonl" }
```

Docker volume warning (official): an old `mcp/memory` volume can contain an `index.js` that the new image overwrites — delete that file or use a dedicated data path.

**COSMOS note:** this is **not** `cosmos_session` SEED. Do not store leases, fencing tokens, or handoff recipient here.

---

### 5. Sequential Thinking — `@modelcontextprotocol/server-sequential-thinking`

**Does:** one recursive scratchpad tool. Host should call it many times (`nextThoughtNeeded: true`) rather than once.

**Run:** `npx -y @modelcontextprotocol/server-sequential-thinking`

Codex: `codex mcp add sequential-thinking npx -y @modelcontextprotocol/server-sequential-thinking`

---

### 6. Time — `mcp-server-time`

**Does:** IANA timezone now + HH:MM conversion. Returns ISO-8601 + `is_dst` + hour delta.

**Run:** `uvx mcp-server-time` · override `--local-timezone=America/Chicago`

---

### 7. Everything — `@modelcontextprotocol/server-everything`

**Does:** MCP protocol gym. Full primitive list: https://github.com/modelcontextprotocol/servers/blob/main/src/everything/docs/features.md

**Run**

```text
npx @modelcontextprotocol/server-everything           # stdio (default)
npx @modelcontextprotocol/server-everything stdio
npx @modelcontextprotocol/server-everything sse         # deprecated HTTP+SSE
npx @modelcontextprotocol/server-everything streamableHttp
```

SSE endpoints (from `src/everything/docs/startup.md`): GET `/sse`, POST `/message`. Streamable HTTP: `/mcp` POST/GET/DELETE, sessionId, event store.

**COSMOS note:** the only reference server that proves Streamable HTTP + Tasks + elicitation. Use it to test a COSMOS MCP client. `get-env` is hostile in a secret-bearing process.

---

## Client config shapes (copy these)

### Generic / Claude Desktop (`mcpServers`)

Path: Windows `%APPDATA%\Claude\claude_desktop_config.json`. Logs: `%APPDATA%\Claude\logs\mcp-server-SERVERNAME.log`.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "V:\\path\\allowed"]
    },
    "memory": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-memory"],
      "env": { "MEMORY_FILE_PATH": "V:\\path\\memory.jsonl" }
    },
    "sequential-thinking": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "everything": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-everything"]
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "V:\\path\\repo"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "env": { "PYTHONIOENCODING": "utf-8" }
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/Chicago"]
    }
  }
}
```

### VS Code (`servers` / `.vscode/mcp.json`)

User: Command Palette → "MCP: Open User Configuration". Workspace: `.vscode/mcp.json` (sometimes wrapped in `"mcp": { … }`).

### COSMOS-as-client (conceptual — no code in this scout)

Spawn the same `command` + `args` + `env` via the official Python SDK stdio client. Record `tools/list` in the job artifact. Each `tools/call` is a worker action; writes go to the attempt workspace; Core ledgers the result. That is the entire integration.

---

## Archived servers — still listed, not maintained

Source: live README "Archived" section + https://github.com/modelcontextprotocol/servers-archived

**Security notice (archive README):** no updates, no CVE fixes, use at own risk.

| server | package / run | tools | auth | cost | successor / COSMOS note |
|--------|---------------|-------|------|------|-------------------------|
| SQLite | `uvx mcp-server-sqlite --db-path FILE` · `mcp/sqlite` | `read_query`, `write_query`, `create_table`, `list_tables`, `describe-table`, `append_insight` | file path | free | **Named in the assignment.** Do not attach to Core's projection DB. |
| PostgreSQL | `npx -y @modelcontextprotocol/server-postgres <url>` · `mcp/postgres` | `query` (READ ONLY txn) | DB URL | free binary | **Named in the assignment.** Read-only role only. |
| Puppeteer | `npx -y @modelcontextprotocol/server-puppeteer` · `mcp/puppeteer` | 7 browser tools | none | free | Prefer Playwright MCP / COSMOS DOM worker. |
| GitHub | `npx -y @modelcontextprotocol/server-github` | 26 GitHub API tools | `GITHUB_PERSONAL_ACCESS_TOKEN` | free + API limits | **Moved to** https://github.com/github/github-mcp-server |
| GitLab | `npx -y @modelcontextprotocol/server-gitlab` | 9 GitLab API tools | `GITLAB_PERSONAL_ACCESS_TOKEN`, optional `GITLAB_API_URL` | free + API limits | Prefer `glab` |
| Slack | `npx -y @modelcontextprotocol/server-slack` | 8 Slack tools | `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` | free binary | **Now** https://github.com/zencoderai/slack-mcp-server |
| Google Drive | `npx -y @modelcontextprotocol/server-gdrive` | `search` + `gdrive:///` resources | Google OAuth desktop | free + quotas | File-mount GDX already exists; API is extra |
| Google Maps | `npx -y @modelcontextprotocol/server-google-maps` | 7 maps tools | `GOOGLE_MAPS_API_KEY` | **paid API** | Spend-gate or skip |
| Brave Search | `npx -y @modelcontextprotocol/server-brave-search` | `brave_web_search`, `brave_local_search` | `BRAVE_API_KEY` | 2k free queries/mo | **Replaced by** https://github.com/brave/brave-search-mcp-server |
| Redis | `npx -y @modelcontextprotocol/server-redis <url>` | `set`,`get`,`delete`,`list` | Redis URL | free | Optional worker cache, not authority |
| Sentry | `uvx mcp-server-sentry --auth-token` | `get_sentry_issue` | token | Sentry plan | Incident enrichment |
| EverArt | `npx -y @modelcontextprotocol/server-everart` | `generate_image` | `EVERART_API_KEY` | **paid gen** | Skip |
| AWS KB Retrieval | `npx -y @modelcontextprotocol/server-aws-kb-retrieval` | `retrieve_from_aws_kb` | AWS keys + region | **AWS billed** | Only with a real KB |
| Git (archive copy) | historical | (see live Git) | none | free | **Use live Git**, not the archive snapshot |

The archive README also lists Git as archived; the **live** repo still ships Git. That is a snapshot vs current-list split — COSMOS should run `uvx mcp-server-git` from the live package.

---

## What COSMOS should actually pick (short)

**Wire first (free, local, high power):** Filesystem (attempt workspace only) + Git (attempt repo) + Fetch + Time. Sequential Thinking on planning hosts. Memory only with an explicit `MEMORY_FILE_PATH` that is **not** the SEED.

---

## ARCH pick (additive, 2026-08-25) — A4

**WAVE A4 = Fetch only** (`uvx mcp-server-fetch` or pip `mcp-server-fetch`; pin `mcp>=1.29.0,<2`; SSRF host allowlist). Filesystem + Git reference servers do **not** replace Core pathlib / native `git` (official warning: educational, not production). BTS `fs_*` already exists. Memory must **not** write `SEED.json`. Time is an optional agent tool, not a clock (Windows clocks already exist). Spawn **not run** this pass. Dispatcher rail waits on Kernel attach. This is **not** a stage-6 pass.

---

## Host bind (additive, 2026-08-27 s6 re-probe) — A4 still blocked / U11

This process:

- `uvx` → **NOT_ON_PATH**
- `py -3.14 -m pip show mcp-server-fetch` → **not installed**
- `py -3.14 -m pip show mcp` → **not installed**
- MCP hosts inspected (server **names** only): Grok=`BFast`; Cursor=`bts`; Gemini=`BFast`; Claude Code=Gmail/Slack/Box/Cloudflare/GDrive (M365 needs auth). **No** Fetch server.

A4 spawn is install-blocked (`uvx` + pip package missing). Not a stage-6 pass.

**Test the client:** Everything on stdio, then Streamable HTTP, in a process with **no secrets**.

**Do not resurrect archived GitHub/Slack/Brave packages** — use the named successors. SQLite/Postgres MCP: only against disposable copies, never Core state.

**Do not** expose Core as a promiscuous MCP server that wraps a shell. If COSMOS becomes an MCP **server**, the tools should be the versioned external API (submit/status/audit) — one authority, still.

---

## Proof this scout read the live tree, not a memory

| artifact | quoted |
|----------|--------|
| Live README reference list | Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time — then Archived: AWS KB, Brave, EverArt, GitHub, GitLab, GDrive, Google Maps, PostgreSQL, Puppeteer, Redis, Sentry, Slack, SQLite |
| Live README run | `npx -y @modelcontextprotocol/server-memory` · `uvx mcp-server-git` · Windows `cmd /c` wrap |
| License | Apache-2.0 new + MIT existing (servers/LICENSE); per-server READMEs say MIT |
| Transports spec | stdio + Streamable HTTP; SSE deprecated as of 2025-03-26 |
| Filesystem tool count | 13 named tools in src/filesystem/README.md |
| Git tool count | 12 named tools in src/git/README.md |
| Fetch tools | 1 tool `fetch` + 1 prompt `fetch` |
| Memory tools | 9 named tools + resource `memory://knowledge-graph` |
| Everything | 19 tools in src/everything/docs/features.md; transports stdio\|sse\|streamableHttp |
| Python ref servers | Fetch/Git/Time require `mcp>=1.29.0,<2` |

**Not verified here:** actually spawning these binaries on this Windows box (this assignment is docs-only). Runtime binding of a live `tools/list` against `npx`/`uvx` is a follow-up job.
