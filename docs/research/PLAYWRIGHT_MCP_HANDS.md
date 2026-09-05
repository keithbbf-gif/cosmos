# PLAYWRIGHT MCP HANDS — G46 scout return (Microsoft official)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim. **No COSMOS core code was edited.**
**Assignment:** maker-docs sweep (DHx) — every official Playwright MCP hand COSMOS could fire.

**Already on the mesh (do not re-add as "new"):** MESH_ADDITIONS row 3 named Playwright MCP as an UNVERIFIED MCP server (`npx @playwright/mcp@latest`, a11y-tree, free OSS). MESH_ADDITIONS_grok row 1 ranked it **highest** as the canonical DOM upgrade over `--dump-dom`. This file inventories **every official tool and install/config surface** so COW can decide caps, isolation, and which MCP-client lane owns it. Browser-Use remains the *open-ended* "figure out this site" sibling; Chrome DevTools MCP remains the *live-Chrome inspect* sibling. Playwright MCP is the *deterministic a11y-tree* lane.

**Filter:** a surface is a HAND only if COSMOS can **do** something with it (drive a browser, snapshot, click, fill, screenshot, evaluate, tabs, capture network/console, mock, persist auth, PDF, trace, video). Chat-only dashboard chrome is out. Community forks (`@executeautomation/playwright-mcp-server`, `mcp-playwright-tools`) are **not** this product — listed at the bottom so they are not confused with Microsoft's package.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks (DOM worker, MCP-client, fenced commit of artifacts, vendor-plural). Equal power, cheaper wins. There is **no vendor meter**. Token cost lives in the *LLM that calls the tools*, not in Playwright.

**What Playwright MCP is (one sentence):** Microsoft's Apache-2.0 MCP server (`@playwright/mcp`) that exposes a real Playwright browser as MCP tools so an LLM drives pages through the **accessibility tree** (stable `ref=eN` handles) instead of screenshots or CSS-selector guessing. Official human docs: [playwright.dev/mcp/introduction](https://playwright.dev/mcp/introduction). Package: [npm `@playwright/mcp`](https://www.npmjs.com/package/@playwright/mcp). Source: [github.com/microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp).

**Repo in play:** `keithbbf-gif/cosmos`. Playwright MCP is a **DOM worker / MCP-client tool**, never a second ledger writer. It runs in an attempt-private workspace (or as a sidecar MCP the agent brains call); fenced commit still owns the live tree. Screenshots, PDFs, traces, videos, snapshots go into the content-addressed store; the ledger holds the pointer.

**Live package probed 2026-08-25 (npm registry, not a green log):** `@playwright/mcp@0.0.79`, `license: Apache-2.0`, `engines.node: ">=18"`, `mcpName: io.github.microsoft/playwright-mcp`, depends on `playwright` / `playwright-core` `1.63.0-alpha-2026-08-05`. Bin: `playwright-mcp` → `cli.js`.

---

## Official documentation URLs (the real ones)

Fetched 2026-08-25. **There is no official PDF.** Third-party "Playwright MCP User Guide" PDFs are scrapes. Canon is the GitHub README (tool list generated from the package) plus `playwright.dev/mcp/*`.

### Source of truth (package + license)

| what | URL |
|------|-----|
| **GitHub repo** | https://github.com/microsoft/playwright-mcp |
| **README (live tool list + install + CLI flags)** | https://github.com/microsoft/playwright-mcp/blob/main/README.md |
| **README raw** | https://raw.githubusercontent.com/microsoft/playwright-mcp/main/README.md |
| **LICENSE (Apache-2.0, Copyright Microsoft Corporation)** | https://github.com/microsoft/playwright-mcp/blob/main/LICENSE |
| **npm package** | https://www.npmjs.com/package/@playwright/mcp |
| **npm registry JSON (version/license/engines)** | https://registry.npmjs.org/@playwright/mcp/latest |
| **MCP registry name** | `io.github.microsoft/playwright-mcp` |
| **Config TypeScript schema (repo)** | https://github.com/microsoft/playwright-mcp/blob/main/config.d.ts |
| **Chrome/Edge extension (connect to existing tabs)** | https://github.com/microsoft/playwright/tree/main/packages/extension |
| **Sibling: Playwright CLI + SKILLS (coding agents)** | https://github.com/microsoft/playwright-cli |
| **Docker (Microsoft Container Registry)** | `mcr.microsoft.com/playwright/mcp` |
| **Docker Hub MCP catalog (community packaging of same repo)** | https://hub.docker.com/mcp/server/playwright |

### Official docs site (`playwright.dev/mcp`)

Source tree: [github.com/microsoft/playwright.dev/tree/main/mcp](https://github.com/microsoft/playwright.dev/tree/main/mcp).

| what | URL |
|------|-----|
| **Introduction (tool overview, 40+ tools)** | https://playwright.dev/mcp/introduction |
| **Installation / getting started** | https://playwright.dev/mcp/installation |
| **Legacy/mirror getting-started (same product)** | https://playwright.dev/docs/getting-started-mcp |
| **Capabilities (core / network / storage / testing / vision / pdf / devtools / config)** | https://playwright.dev/mcp/capabilities |
| **Snapshots (a11y tree, refs, vs screenshots)** | https://playwright.dev/mcp/snapshots |
| **Vision mode (coordinate mouse; opt-in)** | https://playwright.dev/mcp/vision-mode |
| **Configuration (headed/headless, browsers, config file, CLI flags)** | https://playwright.dev/mcp/configuration/options |
| Navigation | https://playwright.dev/mcp/tools/navigation |
| Interaction (click/hover/drag/select/resize) | https://playwright.dev/mcp/tools/interaction |
| Forms (type / fill_form / check / uncheck) | https://playwright.dev/mcp/tools/forms |
| Keyboard & mouse | https://playwright.dev/mcp/tools/keyboard-mouse |
| Screenshots | https://playwright.dev/mcp/tools/screenshots |
| Tabs | https://playwright.dev/mcp/tools/tabs |
| Dialogs | https://playwright.dev/mcp/tools/dialogs |
| File upload | https://playwright.dev/mcp/tools/file-upload |
| Waiting | https://playwright.dev/mcp/tools/waiting |
| Code execution (`run_code` + `evaluate`) | https://playwright.dev/mcp/tools/code-execution |
| Console | https://playwright.dev/mcp/tools/console |
| Network & mocking | https://playwright.dev/mcp/tools/network-mocking |
| Storage & auth | https://playwright.dev/mcp/tools/storage |
| Testing & assertions | https://playwright.dev/mcp/tools/assertions |
| PDF export | https://playwright.dev/mcp/tools/pdf |
| Tracing | https://playwright.dev/mcp/tools/tracing |
| Video | https://playwright.dev/mcp/tools/video |
| Client: VS Code | https://playwright.dev/mcp/clients/vscode |
| Client: Cursor | https://playwright.dev/mcp/clients/cursor |
| Client: Claude Code | https://playwright.dev/mcp/clients/claude-code |
| Client: other (Cline, Codex, Copilot CLI, Goose, Kiro, Gemini CLI, opencode) | https://playwright.dev/mcp/clients/other-clients |
| Grok MCP host docs (client-side, not Playwright) | https://docs.x.ai/build/features/mcp-servers |
| MCP security (Playwright MCP is **not** a security boundary) | https://modelcontextprotocol.io/docs/tutorials/security/security-best-practices |

---

## Licensing / cost floor

| fact | official source | COSMOS implication |
|------|-----------------|--------------------|
| Package is **Apache-2.0**. Copyright (c) Microsoft Corporation. | [LICENSE](https://github.com/microsoft/playwright-mcp/blob/main/LICENSE), npm `"license":"Apache-2.0"` | Tool cost = **$0**. Install, wrap, redistribute with NOTICE. |
| No Microsoft account, no API key, no cloud meter. The server is local Node + a local browser. | README, npm | Spend-gate the **LLM that calls the tools**, not Playwright. |
| npm `@playwright/mcp@0.0.79` (2026-08-25). `engines.node: ">=18"`. | [registry JSON](https://registry.npmjs.org/@playwright/mcp/latest) | Node is already on the box. Browser binaries download on first use. |
| Docs install page says **Node.js 20+**; GitHub README + npm engines say **18+**. | [installation](https://playwright.dev/mcp/installation) vs README / npm | Prefer **Node 20+** for the docs-stated floor; 18 is the published engine. |
| Docker image `mcr.microsoft.com/playwright/mcp` is free; **headless Chromium only**. | README Docker section | Isolation lane. Not a paid product. |
| Playwright CLI (`@playwright/cli`) is a **sibling**, also free OSS — recommended by Microsoft for *coding* agents because MCP dumps tool schemas + a11y trees into context. | [README MCP vs CLI](https://github.com/microsoft/playwright-mcp), [playwright-cli](https://github.com/microsoft/playwright-cli) | COSMOS **agentic DOM loops** → MCP. COSMOS **coding agents writing tests** → CLI+SKILLS. Both $0. |
| Snapshots ~200–400 tokens vs screenshots ~3000–5000 vision tokens. | [snapshots](https://playwright.dev/mcp/snapshots) | Default a11y mode is the cheap + reliable path. Vision is the overflow. |

There is **no paid Playwright MCP SKU**. Microsoft does not bill for this server.

---

## Install / config (the knobs COSMOS actually sets)

### One-line install (stdio, any MCP client)

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

Browser downloads automatically on first use. **Headed by default** (a window you can watch). Pass `--headless` for unattended workers.

### Headed vs headless

| mode | flag | when |
|------|------|------|
| **Headed (default)** | none | Keith watching; DOM-canon "see the site"; first login. |
| **Headless** | `--headless` or `PLAYWRIGHT_MCP_HEADLESS=true` | Queue workers, Job-Object jobs, CI, no display. |

### Accessibility-tree mode vs vision mode

| mode | how | what the LLM sees | what it clicks with |
|------|-----|-------------------|---------------------|
| **A11y / snapshot (default)** | no extra cap | structured tree, `ref=e5` | `browser_click { ref }` — deterministic, no vision model |
| **Vision (opt-in)** | `--caps=vision` | screenshots + x,y | `browser_mouse_click_xy { x, y }` — canvas / WebGL / no-ARIA widgets |

Official: *for most web apps, snapshots are more reliable and token-efficient; use vision only when the accessibility tree does not expose the element.* See [vision-mode](https://playwright.dev/mcp/vision-mode).

### Capability groups (`--caps=`)

Default = **core only**. Add groups to unlock tools (and to grow the tool schema the LLM pays tokens for).

| cap | tools it unlocks | COSMOS default? |
|-----|------------------|-----------------|
| `core` | always on; cannot disable | yes |
| `network` | `browser_route` / `route_list` / `unroute` / `network_state_set` | yes for data-extraction / API-inspect jobs |
| `storage` | cookies, localStorage, sessionStorage, save/restore `storage_state` | yes when a login must persist across attempts |
| `testing` | verify_* assertions + `generate_locator` | only for test-authoring jobs |
| `vision` | coordinate mouse | only when a11y tree is empty |
| `pdf` | `browser_pdf_save` | when the artifact is a PDF |
| `devtools` | tracing, video, annotate, highlight, resume | debugging / bug-repro recordings |
| `config` | `browser_get_config` | introspection |

Full automation: `--caps=network,storage,testing,vision,pdf,devtools`.

Set via CLI `--caps=…`, env `PLAYWRIGHT_MCP_CAPS`, or config file `"capabilities": ["core", "vision", …]`.

### Config file

```
npx @playwright/mcp@latest --config path/to/config.json
```

Schema (docs + README): `browser` (name, isolated, userDataDir, launchOptions, contextOptions, cdpEndpoint, remoteEndpoint, initPage, initScript), `extension`, `server` (port/host/allowedHosts), `capabilities`, `secrets`, `saveSession`, `sharedBrowserContext`, `snapshot.mode` (`full`\|`none`), `imageResponses` (`allow`\|`omit`), `outputDir`, `console.level`, `network.allowedOrigins` / `blockedOrigins`, timeouts, `allowUnrestrictedFileAccess`, `codegen`. **Official warning:** allowed/blocked origins *do not* serve as a security boundary and *do not* affect redirects. Playwright MCP is **not** a security boundary.

### Profiles (auth)

| profile | flag | behavior |
|---------|------|----------|
| **Persistent (default)** | none; override `--user-data-dir` | logins survive. Windows: `%USERPROFILE%\AppData\Local\ms-playwright\mcp-{channel}-{workspace-hash}`. One browser instance per profile. |
| **Isolated** | `--isolated` | in-memory; lost on `browser_close`. Seed with `--storage-state=auth.json`. |
| **Extension** | `--extension` | attach to **already-running** Edge/Chrome tabs (Playwright Extension required). |
| **CDP** | `--cdp-endpoint` | attach to an existing Chromium-family browser. |

**COSMOS default for unattended jobs:** `--isolated` + Job-Object + attempt-private `--output-dir` + `--user-data-dir` under the attempt workspace. **Never** Keith's daily Chrome profile.

### Transports

| transport | how | when |
|-----------|-----|------|
| **stdio** (default) | MCP client spawns `npx @playwright/mcp@latest` | Cursor, Claude Code, Grok CLI, COSMOS MCP-client worker |
| **HTTP / Streamable** | `npx @playwright/mcp@latest --port 8931` then client `"url": "http://localhost:8931/mcp"` | headed browser from a worker with no display; multi-client; Docker sidecar. HTTP sessions have a 5s heartbeat; `PLAYWRIGHT_MCP_PING_TIMEOUT_MS` (0 disables). |
| **Docker stdio** | `docker run -i --rm --init --pull=always mcr.microsoft.com/playwright/mcp` | isolation; **headless Chromium only** |
| **Docker HTTP** | map 8931, `--host 0.0.0.0 --port 8931 --headless --browser chromium --no-sandbox` | long-lived sidecar |
| **Programmatic** | `import { createConnection } from '@playwright/mcp'` + MCP SDK transport | embed in a COSMOS Node worker (not the Python Core) |

### Dangerous knobs (do not leave on)

| knob | why |
|------|-----|
| `browser_run_code_unsafe` (core tool) | README: executes arbitrary JS **in the Playwright server process**; **RCE-equivalent**. Docs page still names this `browser_run_code`. Same hand. Fence the process. |
| `--allow-unrestricted-file-access` | lets the LLM read/upload outside workspace + `file://`. Official: convenience, not a secure boundary. |
| `--extension` / `--cdp-endpoint` on Keith's daily profile | session cookies, saved passwords, bank tabs. Contained profile only. |
| `--shared-browser-context` | all HTTP clients share one context. Fine for a single COSMOS sidecar; not for mixed tenants. |
| `secrets` redaction | convenience; **not** a security feature. Don't put live tokens in snapshots. |

---

## How it plugs into Claude / Cursor / other MCP clients

Official recipes (README + `playwright.dev/mcp/clients/*`). Same binary, different config files.

| client | how |
|--------|-----|
| **Cursor** (COSMOS's coding lane) | One-click: [cursor.com/en/install-mcp?name=Playwright&…](https://cursor.com/en/install-mcp?name=Playwright&config=eyJjb21tYW5kIjoibnB4IEBwbGF5d3JpZ2h0L21jcEBsYXRlc3QifQ%3D%3D). Manual: Settings → MCP → Add → command `npx @playwright/mcp@latest`. Also `.cursor/mcp.json`. |
| **Claude Code** | `claude mcp add playwright npx @playwright/mcp@latest` |
| **Claude Desktop** | Standard `mcpServers` JSON in the Desktop config ([MCP user guide](https://modelcontextprotocol.io/quickstart/user)) |
| **VS Code / Copilot agent** | `code --add-mcp '{"name":"playwright","command":"npx","args":["@playwright/mcp@latest"]}'` |
| **Grok CLI** (this scout's host) | `grok mcp add playwright -- npx @playwright/mcp@latest` **or** `~/.grok/config.toml` `[mcp_servers.playwright]` |
| **Codex** | `codex mcp add playwright npx "@playwright/mcp@latest"` or `~/.codex/config.toml` |
| **Copilot CLI** | `/mcp add` or `~/.copilot/mcp-config.json` (`type: local`, `tools: ["*"]`) |
| **Cline** | `cline_mcp_settings.json` with `"type":"stdio"`, `args: ["-y", "@playwright/mcp@latest"]` |
| **Goose** | Extensions → Add custom → STDIO → `npx @playwright/mcp` |
| **Gemini CLI** | standard config in `settings.json` |
| **opencode** | `~/.config/opencode/opencode.json` `"mcp": { "playwright": { "type":"local", "command":["npx","@playwright/mcp@latest"] } }` |
| **Junie** | `/mcp` → Playwright, or `.junie/mcp/mcp.json` |
| **Kiro / Warp / Windsurf / LM Studio / Amp / Factory / Qodo Gen / Antigravity** | standard JSON; see README |

**Auth to the MCP server itself: none.** The client spawns a local process. Site auth is cookies / `storage_state` / the headed profile. Keith holds credentials; COSMOS does not mint them.

---

## How COSMOS reaches Playwright MCP (one pattern)

Core stays sole ledger writer. Playwright MCP is a **DOM worker** (or an MCP server the agent-brain calls). Attempt-private workspace. Fenced commit.

| Lane | Mechanism | When |
|------|-----------|------|
| **A. COSMOS MCP-client stdio (preferred unattended)** | Core/worker spawns `npx -y @playwright/mcp@latest --headless --isolated --output-dir <attempt>` and calls tools over stdio. Ledger each tool call. | Scripted DOM: login-wall, MFA click, KDash verify, "is this the artifact the machine executes?" |
| **B. HTTP sidecar** | `npx @playwright/mcp@latest --port 8931 --host 127.0.0.1` then `"url": "http://127.0.0.1:8931/mcp"`. | Headed watch from a worker; share one browser across a job's tool calls. |
| **C. Cursor / Claude Code / Grok as the brain** | Those clients already speak MCP; add the standard config. COSMOS dispatches the *task*; the coding agent drives the browser. | Exploratory automation, self-healing tests, "open this URL and tell me what broke." Cursor Ultra is $0 marginal this cycle (DHx). |
| **D. Docker Job-Object** | `mcr.microsoft.com/playwright/mcp` headless Chromium. | Isolation when host Node/browser deps are hostile. |
| **E. CDP / extension attach** | `--cdp-endpoint` or `--extension` to a **contained** Chrome. | Need Keith's already-logged-in session (AUTH_REQUIRED). Never the daily profile. |
| **F. Playwright CLI sibling** | `npm i -g @playwright/cli`; skills. | Coding agents writing tests — Microsoft says CLI is more token-efficient than MCP here. |
| **G. DOM fallback** | Keith's own browser, same sites. | First OAuth, CAPTCHA, "I have to see it." Canon: DOM first when the API can lapse; this MCP *is* that DOM hand for the agent. |

Typed failures already named on the DOM rail: `UNREACHABLE` / `AUTH_REQUIRED` / `BROKE`. Map Playwright timeouts / net errors onto those; do not invent a second vocabulary.

---

## Naming discrepancies (docs vs live README)

The GitHub README **Tools** section is generated from the installed package (`update-readme.js`). Prefer it when the two disagree.

| docs site (`playwright.dev/mcp`) | live README / npm 0.0.79 |
|----------------------------------|---------------------------|
| `browser_run_code` | `browser_run_code_unsafe` (RCE-equivalent, documented as such) |
| `browser_navigate_forward`, `browser_reload`, `browser_check`, `browser_uncheck` | not listed as separate core tools (forward/reload/check may be done via `run_code` / click / `wait_for`) |
| `browser_console_clear` | not listed |
| interaction params `ref` | README params often `target` (ref **or** unique selector) |
| — | extra core: `browser_find`, `browser_drop`, `browser_network_request` (singular, full headers/body) |
| — | extra devtools: `browser_annotate`, `browser_highlight` / `hide_highlight`, `browser_video_show_actions` / `hide_actions`, `browser_resume` |

Both sources agree on the workflow: navigate → snapshot (refs) → click/type/fill → re-snapshot. Both agree core includes **screenshot, evaluate, tabs, console, network_requests**.

---

## Ranking table

Every official hand. Ranked FREE + high-power first. Auth is **none** for the server unless a row says otherwise. Cost is **free** (Apache-2.0, local browser) unless a row says token/vision cost.

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it | source |
|---|------|------|----------------------|------|------|-------|------------------------|--------|
| 1 | **`npx @playwright/mcp@latest` (stdio MCP server)** | MCP stdio | The product: spawn a Playwright browser and expose the tool surface to any MCP client. | none | **free** | **highest** | COSMOS MCP-client worker **or** Cursor/Claude/Grok config. Pin `@latest` only after a probe; production should pin a version. | [README](https://github.com/microsoft/playwright-mcp), [installation](https://playwright.dev/mcp/installation) |
| 2 | **`browser_snapshot` (a11y tree)** | core tool | Capture the accessibility tree with stable `ref=eN` handles. Official: *better than screenshot* for interaction. ~200–400 tokens. Most action tools also return a snapshot. Params: `target`, `filename`, `depth`, `boxes`. | none | **free** | **highest** | Call after navigate / when refs went stale. This **is** the DOM-first perception stack. | [snapshots](https://playwright.dev/mcp/snapshots), README |
| 3 | **`browser_navigate`** | core tool | Open a URL in the current tab. Returns a snapshot. | none | **free** | **highest** | First call of almost every DOM job. | [navigation](https://playwright.dev/mcp/tools/navigation) |
| 4 | **`browser_click`** | core tool | Click (or double-click, right/middle, with modifiers) by snapshot `ref`/`target`. | none | **free** | **highest** | Buttons, links, checkboxes. Prefer this over vision coordinates. | [interaction](https://playwright.dev/mcp/tools/interaction) |
| 5 | **`browser_type` / `browser_fill_form`** | core tools | Type into one field (`submit`, `slowly` for autocomplete) **or** fill many fields in one call (textbox, checkbox, radio, combobox, slider). | none | **free** | **highest** | Login, search, registration. `fill_form` is the token-cheap multi-field path. | [forms](https://playwright.dev/mcp/tools/forms) |
| 6 | **`browser_evaluate`** | core tool | Run JS on the page or on a ref'd element. Read title, computed style, `data-testid`, shadow DOM. | none | **free** | **highest** | Runtime binding: *is this the artifact the machine executes?* Evaluate a value only the live page can emit. Allowlist; drop on untrusted sites if the job does not need it. | [code-execution](https://playwright.dev/mcp/tools/code-execution) |
| 7 | **`browser_tabs`** | core tool | `list` / `new` / `select` / `close` tabs. New tab can take a `url`. | none | **free** | **highest** | Compare staging vs prod; OAuth popup; keep KDash open while hitting another origin. | [tabs](https://playwright.dev/mcp/tools/tabs) |
| 8 | **`browser_console_messages`** | core tool | Dump console (`error`/`warning`/`info`/`debug`). Optional `all` (session-wide) and `filename`. | none | **free** | **highest** | Debug a broken page; ledger JS errors as `BROKE` evidence. | [console](https://playwright.dev/mcp/tools/console) |
| 9 | **`browser_network_requests` + `browser_network_request`** | core tools | Numbered list of requests since load (filter regexp; optional static assets). Singular tool returns headers/body of one index. | none | **free** | **highest** | API-inspect without a vendor search API. Evidence for "the request actually fired." | [network-mocking](https://playwright.dev/mcp/tools/network-mocking), README |
| 10 | **`--headless` / headed default** | config | Headed = watch. Headless = no window. | none | **free** | **highest** | Workers: `--headless`. Keith-watch / first login: headed. | [configuration](https://playwright.dev/mcp/configuration/options) |
| 11 | **`--isolated` + `--storage-state`** | config | Ephemeral in-memory profile; seed cookies/localStorage from a JSON file. | none (file is the session) | **free** | **highest** | Default COSMOS unattended profile. Persist auth by writing `storage_state` into the attempt workspace, not Keith's user dir. | README User profile |
| 12 | **`--caps=storage` cookie / localStorage / sessionStorage / `storage_state`** | storage tools | Full CRUD on cookies (`list/get/set/delete/clear`), localStorage, sessionStorage; `browser_storage_state` save; `browser_set_storage_state` restore. | site cookies | **free** | **highest** | Skip re-login. Save `auth.json` after a headed login; restore on the next isolated job. | [storage](https://playwright.dev/mcp/tools/storage) |
| 13 | **`browser_take_screenshot`** | core tool | PNG/JPEG/webp of viewport, element (`ref`/`target`), or `fullPage`. Official: *you can't perform actions based on the screenshot — use snapshot for actions.* | none | **free** tool; image tokens if the LLM views it | **highest** | Visual verify, canvas, bug attach. Pair with snapshot. `--image-responses=omit` if the brain must not pay vision tokens. | [screenshots](https://playwright.dev/mcp/tools/screenshots) |
| 14 | **`--caps=network` mock + offline** | network tools | `browser_route` (pattern → status/body/headers), `route_list`, `unroute`, `network_state_set` online/offline. | none | **free** | **high** | Test 503 / empty search / strip `authorization`. Deterministic fixtures without a staging server. | [network-mocking](https://playwright.dev/mcp/tools/network-mocking), [capabilities](https://playwright.dev/mcp/capabilities) |
| 15 | **`browser_select_option` / `browser_hover` / `browser_drag` / `browser_press_key` / `browser_resize`** | core tools | Dropdowns; hover menus; drag-drop by refs; keys (`Enter`, `Tab`, `ArrowLeft`); window size. | none | **free** | **high** | Remaining interaction surface. Resize 375×812 for mobile KDash check. | [interaction](https://playwright.dev/mcp/tools/interaction), [keyboard-mouse](https://playwright.dev/mcp/tools/keyboard-mouse) |
| 16 | **`browser_handle_dialog`** | core tool | Accept/dismiss alert/confirm/prompt; optional `promptText`. Other tools report an open dialog and refuse until handled. | none | **free** | **high** | Delete-confirm, `onbeforeunload`, JS prompt. | [dialogs](https://playwright.dev/mcp/tools/dialogs) |
| 17 | **`browser_file_upload` + `browser_drop`** | core tools | Satisfy a file chooser with absolute paths (or cancel). `drop` dumps files or MIME data onto an element as if dragged from outside. Workspace-root restricted unless `--allow-unrestricted-file-access`. | none | **free** | **high** | Upload a GEM artifact into a vendor UI. Paths from the attempt workspace only. | [file-upload](https://playwright.dev/mcp/tools/file-upload), README |
| 18 | **`browser_wait_for`** | core tool | Wait seconds, or for text to appear / disappear. | none | **free** | **high** | SPA loaders. Complex waits → `run_code` `page.waitForSelector`. | [waiting](https://playwright.dev/mcp/tools/waiting) |
| 19 | **`browser_find`** | core tool | Search the current a11y snapshot (text or regex) and return matching nodes + path + refs — cheaper than a full snapshot when you only need one control. | none | **free** | **high** | Large pages (KDash, GitHub). Live README; docs intro does not highlight it. | README Tools |
| 20 | **`browser_navigate_back` (+ docs `navigate_forward` / `reload`)** | core / docs | History back. Docs also document forward + reload. | none | **free** | **high** | "Did the item persist after leaving?" Reload after a mock. | [navigation](https://playwright.dev/mcp/tools/navigation) |
| 21 | **`browser_close`** | core tool | Close page/browser. Isolated profiles die here. | none | **free** | **high** | End of job. Persistent profile keeps cookies. | README |
| 22 | **HTTP transport `--port 8931`** | install | Standalone MCP over `http://localhost:8931/mcp`. | none (bind localhost) | **free** | **high** | Sidecar for workers without a display; Docker. Bind `127.0.0.1`, not `0.0.0.0`, unless the box is already fenced. | README Standalone, [configuration](https://playwright.dev/mcp/configuration/options) |
| 23 | **Docker `mcr.microsoft.com/playwright/mcp`** | install | Same server in a container. Headless Chromium only. | none | **free** | **high** | Isolation lane (MESH_ADDITIONS_grok Docker MCP Toolkit). `--no-sandbox` is in Microsoft's own long-lived example — still Job-Object the engine. | README Docker |
| 24 | **`--caps=pdf` `browser_pdf_save`** | pdf tool | Save the current page as PDF into `outputDir`. | none | **free** | **high** | Receipts, dashboards, "print this chapter-shaped HTML." Artifact → content-addressed store. | [pdf](https://playwright.dev/mcp/tools/pdf) |
| 25 | **`--caps=testing` verify_* + `generate_locator`** | testing tools | Assert role+name visible, text visible, list items, form value; emit `page.getByRole(...)` locators. Exploratory session → Playwright test file. | none | **free** | **high** | Coding-agent jobs that must leave a real test, not a story. Pair with Playwright CLI for the file write. | [assertions](https://playwright.dev/mcp/tools/assertions) |
| 26 | **`--caps=devtools` tracing** | devtools tools | `browser_start_tracing` / `stop_tracing` → zip + network log. Open with `npx playwright show-trace`. Captures DOM snapshots, screenshots, network, console, timing. `--save-session` auto-records. | none | **free** | **high** | Bug-repro artifact the ledger can point at. | [tracing](https://playwright.dev/mcp/tools/tracing) |
| 27 | **`--caps=devtools` video** | devtools tools | `start_video` / `stop_video` (WebM), `video_chapter`, `video_show_actions` / `hide_actions`. Auto via `PLAYWRIGHT_MCP_SAVE_VIDEO=800x600` or config `saveVideo`. | none | **free** | **high** | Record the agent. Attach to an incident. Disk, not a vendor bill. | [video](https://playwright.dev/mcp/tools/video) |
| 28 | **`--caps=vision` coordinate mouse** | vision tools | `mouse_move_xy`, `mouse_click_xy` (button/clickCount/delay), `mouse_drag_xy`, `mouse_down`/`up`, `mouse_wheel`. Requires a vision-capable LLM + a screenshot. | none | **free** tool; **vision tokens** | **high** (only when a11y fails) | Canvas, maps, image editors, icon-without-name. Default **off**. | [vision-mode](https://playwright.dev/mcp/vision-mode) |
| 29 | **`--browser` chrome/firefox/webkit/msedge** | config | Cross-browser. Default Chrome. | none | **free** | **high** | Vendor-plural at the engine: same job on Firefox/WebKit when Chrome lies. | [configuration](https://playwright.dev/mcp/configuration/options) |
| 30 | **`--device` / `--mobile` / `--viewport-size`** | config | Emulate `iPhone 15` etc., or generic mobile (Pixel 10 / iPhone 17). Mobile pages are lighter → fewer snapshot tokens. Cannot combine `--mobile` with `--device`. | none | **free** | **high** | Phone KDash / dissertation figure checks. | README CLI options |
| 31 | **Cursor MCP host** | client | COSMOS's own Cursor key (`Cursor COSMOS 2`). One-click Playwright install. Cloud Agents + local Agent CLI can call the tools. | Cursor key (already on mesh) | **$0** marginal (Ultra included) | **high** | DHx coding lane drives the browser instead of inventing selectors. | [clients/cursor](https://playwright.dev/mcp/clients/cursor), DHx |
| 32 | **Claude Code MCP host** | client | `claude mcp add playwright npx @playwright/mcp@latest` | Claude subscription / API | tokens | **high** | F5 / Claude Code jobs that must *use* a site. | [clients/claude-code](https://playwright.dev/mcp/clients/claude-code) |
| 33 | **Grok MCP host** | client | `grok mcp add playwright -- npx @playwright/mcp@latest` or `~/.grok/config.toml` | SuperGrok | tokens | **high** | This scout's host can grow hands without a COSMOS-core edit. | README Grok section, [xAI MCP](https://docs.x.ai/build/features/mcp-servers) |
| 34 | **`--caps=devtools` annotate / highlight / resume** | devtools tools | `browser_annotate` (human draws on the Playwright Dashboard; returns annotated screenshot + ARIA + list). `highlight` / `hide_highlight`. `browser_resume` (step / pause at `file:line`). | none (annotate needs a human) | **free** | **med-high** | HITL on a headed session. Pause a generated test. | README DevTools |
| 35 | **`--extension` / `--cdp-endpoint` / `remoteEndpoint`** | attach | Drive an already-running Chrome/Edge (extension) or any CDP/Playwright server. | the attached browser's cookies | **free** local | **med-high** | AUTH_REQUIRED: use a **contained** profile Keith already logged into. Not the daily profile. | README, extension package |
| 36 | **`--init-page` / `--init-script`** | config | TS on the Playwright `page` at start (geolocation, viewport, permissions). JS injected before every page's own scripts. | none | **free** | **med-high** | Stamp `window.isPlaywrightMCP`, grant clipboard, fake GPS — without a tool call. | README Initial state |
| 37 | **`--secrets` dotenv redaction** | config | Replace matching plaintext in tool **responses** so the LLM does not echo passwords. Official: *convenience, not a security feature.* | path to dotenv | **free** | **med-high** | Always on for login jobs. Still don't type secrets into the prompt. | README config schema |
| 38 | **`--proxy-server` / `--proxy-bypass`** | config | HTTP/SOCKS proxy. | proxy if any | **free** (proxy itself may be paid) | **med-high** | Only if Keith already has a proxy. Not a stealth product. | [configuration](https://playwright.dev/mcp/configuration/options) |
| 39 | **`--allowed-origins` / `--blocked-origins` / `--allowed-hosts`** | config | Origin allow/block (not a security boundary; no redirect coverage). `--allowed-hosts` is DNS-rebinding protection for the HTTP server. | none | **free** | **med-high** | Fail-closed allowlist of vendor hosts per job. Still wrap in Job-Object. | README, config schema |
| 40 | **`browser_run_code_unsafe` / docs `browser_run_code`** | core tool | `async (page) => { … }` with the full Playwright API: iframes, geolocation, clipboard, custom waits, conditional `page.route`. **RCE in the server process.** | none | **free** | **med** (power is high; trust is not) | Last resort when a first-class tool does not exist. COSMOS: Job-Object, no live-tree write, never on an untrusted prompt. | [code-execution](https://playwright.dev/mcp/tools/code-execution), README (unsafe name) |
| 41 | **`--caps=config` `browser_get_config`** | config tool | Dump the resolved config (CLI + env + file). | none | **free** | **med** | Probe/audit: prove which caps/headed/isolated the live process actually has. Runtime binding for config. | [capabilities](https://playwright.dev/mcp/capabilities) |
| 42 | **`--output-dir` / `--output-max-size` / `--image-responses` / `--snapshot-mode`** | config | Where screenshots/PDFs/traces land; eviction threshold; send or omit images; snapshot `full` vs `none`. | none | **free** | **med** | Point `output-dir` at the attempt workspace / GEM. `snapshot-mode=none` only when a coding agent is using the CLI sibling. | README CLI options |
| 43 | **`--grant-permissions` / `--ignore-https-errors` / `--block-service-workers` / `--user-agent` / `--executable-path` / `--no-sandbox`** | config | Clipboard/geolocation grants; TLS ignore; SW block; UA override; custom binary; sandbox off. | none | **free** | **med** | Use narrowly. `--no-sandbox` is for containers, not the host. `--ignore-https-errors` is a last resort. | README |
| 44 | **`--codegen` typescript/python/java/csharp/none** | config | Language for generated locators/tests. Default TypeScript. | none | **free** | **med** | COSMOS test authoring in the language of the tree (`python` if we emit pytest). | README |
| 45 | **Programmatic `createConnection` from `@playwright/mcp`** | Node API | Embed the MCP server in a Node HTTP process (example uses SSE transport). | none | **free** | **med** | Only if a COSMOS Node worker must host MCP itself. Prefer spawning the CLI. | README Programmatic usage |
| 46 | **Playwright CLI + SKILLS (`@playwright/cli`)** | sibling CLI | Microsoft's recommended interface for *coding* agents: shell commands, no huge tool schemas in context, default **headless**. | none | **free** | **med** (different job) | Use for "write me a Playwright test." Keep MCP for long-running agentic DOM with persistent state. | [playwright-cli](https://github.com/microsoft/playwright-cli), README MCP vs CLI |
| 47 | **Persistent Windows profile** | config | Default cache dir under `%USERPROFILE%\AppData\Local\ms-playwright\mcp-{channel}-{workspace-hash}`. One instance at a time. | leftover cookies | **free** | **med** | Fine for a headed Keith session. Unattended COSMOS jobs should **not** share this; use `--isolated` or a per-attempt `--user-data-dir`. | README User profile |
| 48 | **`browser_check` / `browser_uncheck` (docs)** | docs tools | Check/uncheck checkbox or radio by ref. Live README may fold this into click/fill_form. | none | **free** | **med** | Use if the connected server lists them (`tools/list`). Else click the checkbox ref. | [forms](https://playwright.dev/mcp/tools/forms) |
| 49 | **`browser_console_clear` (docs)** | docs tool | Clear the console buffer. | none | **free** | **low-med** | Nice-to-have between navigations. | [console](https://playwright.dev/mcp/tools/console) |
| 50 | **MCP Registry listing** | discovery | `mcpName: io.github.microsoft/playwright-mcp` on the package. | none | **free** | **low** | Lets a registry-aware client find the official server. COSMOS can skip the marketplace and pin npm. | npm `mcpName` |

---

## Default COSMOS flags (unattended DOM worker)

```
npx -y @playwright/mcp@latest
  --headless
  --isolated
  --browser chromium
  --caps=network,storage
  --output-dir <attempt-workspace>/pw
  --image-responses omit
  --console-level error
```

Add `--caps=pdf` when the artifact is a PDF. Add `--caps=devtools` only when a trace/video is the evidence. Add `--caps=vision` only after an a11y snapshot shows no usable refs. Add `--storage-state=<attempt>/auth.json` after a headed login has been saved.

Ledger: tool name, URL, snapshot hash or screenshot hash, console errors, network 4xx/5xx. The report quotes those artifacts — not the intention.

---

## Not these (do not mix)

| package | what it is | vs official |
|---------|------------|-------------|
| `@executeautomation/playwright-mcp-server` | community MCP, different tool names, Smithery install | **Not** Microsoft. Do not install as "Playwright MCP." |
| `mcp-playwright-tools` (PyPI) | Python MCP wrapping Playwright with `navigate`/`click`/`fill` | Different surface. |
| Archived MCP **Puppeteer** reference server | unmaintained Chromium MCP | Prefer this official Playwright MCP. |
| Browser-Use Cloud MCP | metered; trains on inputs | MESH_ADDITIONS_grok: do not use cloud for COSMOS. |

---

## Recommendation (for COW, not a live-mesh claim)

Ship **lane A first**: COSMOS MCP-client stdio, `--headless --isolated`, core + `network,storage`, output into the attempt workspace. That is the DOM-canon upgrade over `--dump-dom`: deterministic refs, console + network evidence, $0 tool cost.

Keep Cursor/Claude/Grok configs as **lane C** so coding agents can drive the same server without Core growing a browser.

Treat `browser_run_code_unsafe` as RCE: Job-Object, no live-tree write, never on an untrusted prompt.

Vision, PDF, tracing, video, testing caps stay **opt-in per job** so the tool schema stays small (official reason capabilities exist: fewer tokens, fewer hallucinated calls).

Vendor-plural: Playwright MCP (deterministic a11y) disagrees with Browser-Use (open-ended) and Chrome DevTools MCP (live Chrome). That disagreement is the point.

---

## ARCH pick (additive, 2026-08-25) — M5 / A3

**Default DOM worker = Playwright MCP.** `cosmos_browser --dump-dom` stays as vendor-plural overflow / AUTH_REQUIRED fallback — not a second unsynchronized DOM authority.

**WAVE A3 (ARCH):** spawn from Claude Code / Grok Build / Cursor MCP host **or** a COSMOS MCP-client worker. No kernel. No Dispatcher `ApiRail`. Spawn via **`cmd /c`** (PowerShell `npm.ps1` is execution-policy blocked). Default flags as above (`--headless --isolated --browser chromium --caps=network,storage`).

**Host bind this process (not a stage-6 pass):**

- Node `v24.18.0` at `C:\Program Files\nodejs\node.exe` (engines `>=18`).
- `npx` present.
- `cmd /c npx -y @playwright/mcp@0.0.79 --help` → **`Usage: Playwright MCP [options]`**.
- `cmd /c npx -y @playwright/mcp@0.0.79 -V` → **`Version 0.0.79`**.
- MCP stdio `initialize` + `tools/list` against `npx -y @playwright/mcp@0.0.79 --headless --isolated --browser chromium` → JSON-RPC `serverInfo.name=Playwright`, **`serverInfo.version=1.63.0-alpha-2026-08-05`**, **`protocolVersion=2024-11-05`**, **`tools` count = 24**: `browser_close,browser_resize,browser_console_messages,browser_handle_dialog,browser_evaluate,browser_file_upload,browser_drop,browser_find,browser_fill_form,browser_press_key,browser_type,browser_navigate,browser_navigate_back,browser_network_requests,browser_network_request,browser_run_code_unsafe,browser_take_screenshot,browser_snapshot,browser_click,browser_drag,browser_hover,browser_select_option,browser_tabs,browser_wait_for`.
- That `tools/list` is a **host spawn**, not a COSMOS worker and **not** a stage-6 pass. Browser binary download on first `browser_navigate` remains **UNKNOWN**. `browser_run_code_unsafe` stays off.

---

## Host bind (additive, 2026-08-27 s6) — A3 satellite `--probe` / U10 closed

RAN (no kernel/ledger/sched/service edit; `--probe` does **not** overwrite `live/config/playwright_rail_probe.json`):

`py -3.14 cosmos\cosmos_playwright_rail.py --root V:\A\Ai\COSMOS\live --probe`

Live emit this process:

- `ok=true`
- `link_id=playwright-dom`
- `tool_count=24`
- `serverInfo.name=Playwright`
- `serverInfo.version=1.63.0-alpha-2026-08-05`
- `tools/list` includes `browser_navigate` + `browser_snapshot` (`browser_run_code_unsafe` listed, client-denied)

Prior meshadditions `--gate` (2026-08-26T10:53:58-05, `live/config/playwright_rail_probe.json`, not rewritten here): `gate=PASS`, `tree_id=KMesh-COSMOS-live`, `snapshot_has_tree_id=true`, `gate_url=http://127.0.0.1:59571/`, `kernel_attached=false`. That snapshot **closed U10** (browser binary on first `browser_navigate`). Default DOM remains Playwright MCP; `cosmos_browser --dump-dom` overflow. Core `:8770` **DOWN** this pass — live Kernel registry attach unproven.
)
