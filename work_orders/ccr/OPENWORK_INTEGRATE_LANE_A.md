# RESEARCH — OpenWork × COSMOS integration (Lane A)

**Stage:** 1 RESEARCH. Not ARCH. Not BUILD.  
**Lane:** A — Grok CLI / CCr worktree `ow-integrate-lane-a`.  
**Dated:** 2026-09-05 (host); OpenWork recovery stamp `2026-09-06T01:01:50.410Z`.  
**Question:** How should COSMOS and OpenWork integrate — concretely, on this machine, without cloning each other?  
**Not used as the answer:** `docs/arch/OPENWORK_INTEGRATION.md`, PR #45.  
**Not done:** iframe, legal transcripts, merge of PRs #30 #32 #36 #37 #38, CORE writes, a 27th CLOCKS row.

UNKNOWN where not bound. A claim is not evidence. Every number below is quoted from an artifact this pass emitted or read.

---

## 0. What is already sitting on this PC (occupancy, not a join design)

| Piece | Bound this pass |
|---|---|
| COSMOS Core | `GET http://127.0.0.1:8770/api/v1/status` → `ready: true`, `root: V:\A\Ai\COSMOS\live`, `tree_id: KMesh-COSMOS-live`, `ledger_head.seq: 7743`, `event: HEALTH_BOARD`. `GET /health` on Core is **404**. `GET /api/v1/health` is **200**, ledger `chain VERIFIED, 7743 records` (7742 on first hit; next HEALTH_BOARD incremented). Listen: `127.0.0.1:8770` PID 20396. |
| OpenWork desktop | `OpenWork.exe` **FileVersion 0.18.42** at `C:\Users\Papa\AppData\Local\Programs\@openworkdesktop\OpenWork.exe`. Recovery: `currentVersion: 0.18.42`. Four processes live (PIDs 45808, 11504, 24632, 25072). Window title `OpenWork`. |
| OpenWork `/health` | `http://127.0.0.1:61512/health` **200** `{"ok":true,"version":"0.18.42","opencodeVersion":"1.18.18","uptimeMs":…}`. Bound to workspace port map key `v:/streams/openwork`. BIND’s old port **57383** (`c:/users/papa/openwork chat`) **refused** (`WinError 10061`). |
| GFO sit (active) | `openwork-workspaces.json`: `activeId` / `selectedId` / `watchedId` = **`ws_726c64a2afa5`**, name **COSMOS 2**, path **`V:\OPENWORK\COSMOS_2`**. **No** `workspacePorts` entry for that path. |
| Kept grant | `ws_12669390bcf4`, name **COSMOS**, path **`V:\Streams\openwork`**. This is the only live `/health` port (**61512**). |
| Twin folder | `V:\OPENWORK\COSMOS 2` (space) also exists. GFO `_boot.json` `workspace_root` is `V:\OPENWORK\COSMOS_2`; `cwd` is `V:\OpenWork\COSMOS 2`. Two spellings, one occupant. UNKNOWN whether they are the same NTFS object or two trees. |
| cDeck P5 | Live spec `V:\A\Ai\COSMOS\builds\cdeck\ORCH_HOME_SPEC.md` §5 / P5: main left OpenWork C0 (`open_openwork` / `openwork_status`); LIVE from loopback `/health`; embed **UNMEASURED**. Constant in `lib.rs`: `OPENWORK_EMBED = "UNMEASURED — no HTML origin; Electron /health is API-only, not a webview. Do not iframe."` |
| Recents / Open Sessions | `GET /api/v1/recents` **200** `schema: cdeck-recents/1`, `source: cowork_to_openwork`, `n_catalog: 666`, `n_shown: 200`, `n_omitted_legal: 108`, `truncated: true`, `tree_id: KMesh-COSMOS-live`. Catalog path in `live/state/cdeck/recents.json`: `C:\Users\Papa\OpenWork Chat\cow_sessions\COW_SESSION_CATALOG.json` (leftover grant). Legal rows counted, not opened. |
| Mailbox | Both grants have `cm\` + `README.md` (GFO → CCr WOs). COSMOS_2 also has `_boot.json`. |
| MCP on Core HTTP | **ABSENT.** `GET /api/v1/mcp` **404** `NOT_FOUND`. `GET /mcp` **404**. `cosmos.py` does not import `cosmos_mcp`. `cosmos/cosmos_mcp.py` exists as **stdio** JSON-RPC tools (`cosmos_status`, `cosmos_submit`, `cosmos_jobs`, `cosmos_audit`, `cosmos_health`, `cosmos_command`, `cosmos_events`) — **not** mounted on `:8770`. |
| CLOCKS | `cosmos_own_clocks.CLOCKS` **26 rows**, ids **1–26**. Native Windows schtasks / `pythonw`. Do not mint a 27th that duplicates OpenWork Automations. |
| Gitur | Live `docs/AGENT_BRIEF.md`: **Gitur = GitHub + GitLab + Cursor.** Entire COSMOS BUILD through Gitur → branched trees / PRs. One job, one branch, one PR. This file is Lane A on that rule. Gitur is not a pen and not Bedrock. |
| Loopback auth | `cosmos_service._request_authed`: loopback peer auto-connects without bearer (Keith 2026-09-04). Measured: GET status/health/recents/tools/makers/jobs **200** with no `Authorization`. `POST /api/v1/jobs` with no bearer returned **201** `job_id: 1788663008628-afe18b3af0` (this research’s probe; command `lane-a-probe-do-not-run` — ignore / do not treat as a real WO). Tailscale/LAN still need the token. **Do not persist** `openwork-ui-control.json` bearer (keys seen, values not copied). |

Vendor (fetched 200 this pass):

- https://openworklabs.com/docs/llms.txt
- https://openworklabs.com/docs/start-here/get-started.md
- https://openworklabs.com/docs/start-here/do-work-with-it/skills-plugins-and-mcp.md
- https://openworklabs.com/docs/start-here/do-work-with-it/control-the-browser.md
- https://openworklabs.com/docs/start-here/do-work-with-it/workflows.md
- https://openworklabs.com/docs/start-here/do-work-with-it/create-a-skill-from-chat.md
- https://openworklabs.com/docs/start-here/connect-your-stack/add-an-mcp-server.md
- https://openworklabs.com/docs/start-here/connect-your-stack/connect-services.md
- https://openworklabs.com/docs/start-here/migrate-from-claude-cowork.md
- https://openworklabs.com/docs/cloud/get-started.md
- https://openworklabs.com/docs/cloud/run-in-the-cloud/shared-workspace.md
- https://openworklabs.com/docs/cloud/run-in-the-cloud/cloud-mcp.md
- Automations Den API pages under `/docs/api-reference/automations/`

Install bind (tree, not assumed to be the join): `docs/OPENWORK_BIND.md` (dated 2026-09-04; **stale vs this pass** on selected workspace and `/health` port — see §0 table).

---

## 1. What OpenWork actually offers that COSMOS would have to rebuild if ignored

Bound to vendor docs + this install. If COSMOS ignored OpenWork, Core would have to grow a second orch harness. That is the clone. Do not do it.

### 1.1 On this install (measured)

| Offer | Evidence |
|---|---|
| Desktop orch harness | `OpenWork.exe` 0.18.42 running; `/health` names `opencodeVersion: 1.18.18`. Vendor get-started: *privacy-first, open-source alternative to Claude Cowork*; local desktop free without Cloud sign-in. |
| Folder grant = pen | Active workspace `V:\OPENWORK\COSMOS_2` (`ws_726c64a2afa5`). Kept `V:\Streams\openwork` (`ws_12669390bcf4`). BIND + `AGENTS.md`: **no** COSMOS root grant. Leftover `C:\Users\Papa\OpenWork Chat` still holds the 666 catalog. |
| Skills / plugins / Library | Grant `opencode.jsonc` pins `openwork/z-ai/glm-5.2` + `openwork/deepseek/deepseek-v4-flash`, plugin `./.opencode/plugins/cowork_to_openwork.js`. Vendor: connector / connection / skill / plugin / Library. Local skill = workspace `SKILL.md` (`.opencode/skills/<name>/SKILL.md`); Cloud skill is a private plugin. |
| Session groups / workflows | Vendor workflows: rename, pin, archive, move to group. `docs/research/SESSION_TOOLS.md` (prior research, not re-opened legal): sidebar groups live on `ws_726c64a2afa5`. This pass did **not** open `runtime.sqlite`. Treat group counts as **UNMEASURED this sit** except that rebind onto COSMOS 2 is already claimed there. |
| Cowork pack seed | `tools/cowork_to_openwork/` + plugin on **both** grants. SHARE.md: corpus **not** public; do **not** re-ingest 666; legal listed in catalog only. |
| Mailbox | `cm\` on both grants. COSMOS_2 `_boot.json` already quotes Core status + recents (see §2). |
| Models | BIND (2026-09-04 billing shot): Team seats 1/5 **$0**; OpenWork Models **$10** Active; OpenWork Web **Off** ($50/member if bought). BYOK chips named in BIND (Vertex/Google/xAI/Zen/Duo/OpenWork Models). This pass did **not** re-open Billing. Treat $ figures as BIND-dated, not re-measured. |
| Built-in browser | Vendor: OpenWork Browser extension; click/fill/screenshot **inside that browser**, not full Windows desktop control. **UNMEASURED** whether Library has `OpenWork Browser` enabled on this seat. |
| Automations | Vendor Den API: desktop-created automations run on the **connected desktop runner**; Web-created run in Cloud; due with no runner → **missed**. BIND: max runtime **10s–1h**; not a 15s COSMOS poll; long-running / laptop-closed still **Building** on the vendor roadmap. This pass did **not** list live Automations on the org. **UNMEASURED** whether any Automation exists on Keith’s org today. |
| Connectors / MCP | Vendor Connect: Gmail, Calendar, Drive, Slack, Notion, Linear (Cloud org). Custom MCP: Settings → Library → Advanced → **Add workspace MCP** with **server URL** + OAuth / DCR. MCP Gateway: `https://api.openworklabs.com/mcp/agent` for **external** clients (Cursor, Codex, Claude Code, OpenCode, VS Code). This pass did **not** enumerate connected Connect apps. **UNMEASURED** which Connect chips are live. |
| OpenWork Web | Vendor: hosted browser workspace, **$50 / joined member / month**, not opened from the desktop app. BIND: **Off**. Constraint: do not iframe; do not buy for DT. |

### 1.2 What ignoring it would force Core to grow

If COSMOS rebuilt these inside CORE it would clone the harness:

- Skill/plugin/Library OS (SKILL.md, Collections, create-from-chat)
- MCP Connect + custom MCP + a browser computer-use surface
- Session groups / pin / archive as a second recents product
- Automations scheduler (queued/claimed/running leases) beside 26 Windows clocks
- Folder-grant occupancy (the pen)
- Cowork-class file work + connectors

Constraint from the question: **do not rebuild OpenWork skills/Library/MCP/Automations/browser inside CORE.** Use them where they already run (`OpenWork.exe`).

### 1.3 Stale BIND vs this pass

`docs/OPENWORK_BIND.md` (2026-09-04) still says selected `ws_12669390bcf4` / health port **57383**. This pass: selected **COSMOS 2** / health **61512** on the **kept** Streams workspace; 57383 dead. `docs/ORCH_SEAT.md` and Streams `AGENTS.md` still name the wheelhouse `V:\Streams\openwork`. Question file + live `workspaces.json` name the GFO sit `V:\OPENWORK\COSMOS_2`. Both folders exist. Integration research must not pretend there is one grant.

---

## 2. What COSMOS already exposes that OpenWork could call

Bound to `/api/v1/*` (live Core + `cosmos/cosmos_service.py` docstring / dispatch) and cDeck C0. MCP **absent** on HTTP (measured).

### 2.1 HTTP API on `:8770` (one versioned surface)

From `cosmos_service.py` header + live GETs this pass.

**GET (loopback, no bearer, 200 unless noted)**

| Path | What | This pass |
|---|---|---|
| `/api/v1/status` | kernel READY + root + ledger head | 200, `tree_id=KMesh-COSMOS-live` |
| `/api/v1/health` | HealthBoard | 200, chain VERIFIED 7743 |
| `/api/v1/audit` | audit projection | not hit — UNKNOWN live body |
| `/api/v1/jobs` | scheduler projection | 200, many `CLEAN` ids |
| `/api/v1/spend` | spend gate audit | not hit — UNKNOWN |
| `/api/v1/tools` | tool-**contract** report, not invoke | 200, names include `apply_plans`, `backup_to_onedrive` |
| `/api/v1/events` | ledger page `?since_seq=` / `?tail=` | not hit — UNKNOWN |
| `/api/v1/rails` (`/api/v1/nodes` alias) | rails matrix | not hit — UNKNOWN |
| `/api/v1/makers` | maker map | 200 |
| `/api/v1/surfaces` | storage surfaces | not hit — UNKNOWN |
| `/api/v1/fleet` | cDeck FLEET panel | not hit — UNKNOWN |
| `/api/v1/nodemap` | cDeck NODE MAP | not hit — UNKNOWN |
| `/api/v1/jukebox` | rich job fold | not hit — UNKNOWN |
| `/api/v1/recents` | Open Sessions / cDeck RECENTS | **200**, 666/200/108 legal omitted |
| `/api/v1/cvm/pull` | CVM pull ticket | not hit — UNKNOWN |
| `/api/v1/control` | pause/mic_off | not hit — UNKNOWN |
| `/api/v1/mcp` | — | **404 ABSENT** |
| `/mcp` | — | **404 ABSENT** |
| `/health` (Core) | — | **404** (OpenWork’s `/health` is a **different process**) |

**POST**

| Path | What | This pass |
|---|---|---|
| `/api/v1/jobs` | submit `{command, priority}` → `job_id` | loopback **201** without bearer (probe job id above) |
| `/api/v1/makers` | add maker (unknown kind REFUSES) | not hit |
| `/api/v1/command` | text in, kernel action out | loopback **400** `UNKNOWN_COMMAND: 'ping'` — route is alive; GET of same path is 404 |
| `/api/v1/voice` | spoken turn, spend-gated | not hit |
| `/api/v1/crucible` | critic round; 501 if none composed | not hit |
| `/api/v1/spend` | SET/ADJUST caps (widen needs confirm) | not hit |
| `/api/v1/cvm/snapshot` · `/api/v1/cvm/push` | phone mule | not hit |
| `/api/v1/kill` (also GET `/kill`) | human off-switch, no bearer | not hit |
| `/api/v1/control/resume` | clear flags | not hit |

Static shells (no bearer, no data): `/`, `/dash`, `/cdeck/`, PWA files. cDeck webview talks to COSMOS **only** via `/api/v1/*` (`ORCH_HOME_SPEC` §5).

### 2.2 cDeck C0 (occupancy pipe, not an API clone)

Live `lib.rs`: `open_openwork` focuses a live `OpenWork.exe` or launches the installed exe; second press does not spawn. `openwork_status` reads:

- `openwork-workspaces.json` **activeId** (else selectedId)
- `openwork-server-state.json` `workspacePorts` keyed by workspace **path**
- loopback `GET /health` on that port
- `cosmos_grant` true if the path **looks like the COSMOS tree** (must stay false)

**Implication measured this pass:** active workspace is `V:\OPENWORK\COSMOS_2`, which has **no** port in `workspacePorts`. cDeck LIVE for the GFO sit would see **no server port** even while Streams `:61512` is healthy. Recents-panel note still **prefers** `v:/streams/openwork` (`cosmos_recents_panel._OW_PREFER`). Embed remains UNMEASURED. Do not iframe Electron `/health`.

### 2.3 Open Sessions product

`builds/open_sessions/Open_sessions.py` is a CLI on the same `GET /api/v1/recents` projection. Constraint: do **not** rebuild Open Sessions in place. `cowork_to_openwork` is a **seed**, not ORC recode. 666 stay on COSMOS for federation — do not re-ingest.

### 2.4 Stdio MCP module (not a live call surface)

`cosmos/cosmos_mcp.py` can speak MCP on stdio to a kernel. `cosmos.py serve` does **not** start it. OpenWork’s “Add workspace MCP” docs want a **URL + OAuth**, not a stdio argv. Whether OpenWork can attach stdio MCP to `cosmos_mcp.py` is **UNMEASURED**. Treat Core MCP as **absent** until a live client lists tools.

### 2.5 GFO already quoted Core (grant artifact)

`V:\OPENWORK\COSMOS_2\cm\_boot.json` (not a legal transcript):

```json
"model": "gemini-3.8-flash",
"provider": "google-vertex",
"workspace_root": "V:\\OPENWORK\\COSMOS_2",
"cwd": "V:\\OpenWork\\COSMOS 2",
"health_quote": "{... \"ready\":true, \"root\":\"V:\\\\A\\\\Ai\\\\COSMOS\\\\live\", \"tree_id\":\"KMesh-COSMOS-live\", ... seq: 7742 ...}",
"recents_quote": "n_shown=200 tree_id=KMesh-COSMOS-live",
"time": "2026-09-05T20:56:00-05:00"
```

That is evidence the ORC chair **can** see Core `:8770` without a COSMOS folder grant. UNKNOWN whether that fetch was an in-app OpenWork tool call, a pasted quote, or a CCr write of `_boot.json`. Next measurement (§5) closes that.

### 2.6 What OpenWork must **not** call as if it were CCr

Loopback `POST /api/v1/jobs` **works without a bearer**. That is a Core **queue** write, not a live-tree write, but it is still a second dispatcher. P10: GFO **proposes** into `cm\`; CCr harvests; Gitur branches; CCr writes `cosmos/`. OpenWork must not become an unfenced job mint on `:8770`.

---

## 3. Candidate join shapes (independent; at least two)

These are research candidates, not an architecture. No CORE writes implied.

### Shape A — Two processes, two pens, three pipes (what the room already almost is)

**Pipes**

1. **Filesystem mailbox:** GFO writes `cm\` on the **sit** grant (`V:\OPENWORK\COSMOS_2`). CCr harvests. No COSMOS root grant.
2. **Loopback HTTP read of Core:** `GET /api/v1/status|health|jobs|recents|…` from the same machine (already quoted in `_boot.json`). Writes to Core stay mailbox/Gitur, not `POST /jobs` from ORC.
3. **cDeck C0 occupancy:** OPEN focuses/launches `OpenWork.exe`; LIVE from `/health`; dual-window on two HP 24N until merge. Recents click = focus OpenWork, not `grok -r`.

**What stays in which process**

| OpenWork.exe (wheelhouse) | COSMOS Core (engine room) |
|---|---|
| Skills, plugins, Library, Connect, browser, session groups, Automations UI, GFO talk (GF38 / Joanna) | Ledger, leases, spend gate, 26 Windows clocks, Gitur landings, fenced commit, `/api/v1/*` |
| File work on the grant | Runtime `V:\A\Ai\COSMOS\live` |
| P10 proposals in `cm\` | CCr write of `cosmos/` / `builds/cdeck` |

**Failure modes**

- Sit vs kept grant: LIVE chip looks up **active** path → COSMOS_2 has **no** `/health` port; Streams `:61512` is the live health. Operator sees UNMEASURED/false-dead on the sit.
- Recents catalog still on leftover `C:\Users\Papa\OpenWork Chat\…` — move/delete of that leftover would empty leftmost RECENTS (`NO_SOURCE`), not OpenWork itself.
- `COSMOS_2` vs `COSMOS 2` cwd/root split — plugin/skill relative paths can miss.
- OpenWork down: desktop Automations **miss**; COSMOS clocks **keep running** (that is the point of not cloning clocks).
- Core down: GFO files blind; mailbox still lands on disk for later harvest.
- Loopback `POST /jobs` is an accidental second scheduler (this pass proved it).
- Tailscale/phone: bearer required; OpenWork must not paste `api_token.txt` into ui-control or git.

**UNMEASURED**

- Whether in-chat GFO tools can `fetch` `:8770` (vs a human-curated `_boot.json`).
- Whether any OpenWork Automation is configured.
- HTML origin for a later in-pane webview (`pnpm world up dev-headless` in BIND — not run this pass).
- Whether `V:\OPENWORK\COSMOS_2` and `V:\OPENWORK\COSMOS 2` are one directory.

### Shape B — Grant-local HTTP skill (OpenWork stays the client; Core stays the OS)

**Pipes**

- One OpenWork **local** skill (workspace `SKILL.md` under the **sit** grant, not Cloud, not CORE) that only **GETs** a short allowlist (`/api/v1/status`, `/api/v1/health`, `/api/v1/recents`, `/api/v1/jobs`) and writes a receipt into `cm\`.
- No MCP adapter. No new CLOCKS row. No COSMOS authorized folder.
- CCr still harvests `cm\`. Gitur still takes BUILD.

**What stays where**

- Skill text, Library, browser, connectors, Automations: OpenWork.
- Allowlist + ledger + clocks: Core.
- The skill is **documentation the agent loads**, not a second Core module.

**Failure modes**

- Skill that POSTs `/api/v1/jobs` or `/command` becomes a rogue dispatcher (loopback will accept it).
- Cloud “skill for me” would copy orch procedure into OpenWork Cloud — federation/legal isolation risk. Keep it **local** (`SKILL.md` in the grant).
- OpenWork agent sandbox may deny loopback — then the skill fails closed (good) and mailbox stays the only pipe.
- Duplicating recents inside OpenWork as a second product would rebuild Open Sessions. The skill **reads** Core recents; it does not re-ingest 666.

**UNMEASURED**

- Sandbox allowlist for `127.0.0.1:8770` from an OpenWork chat tool.
- Whether `cowork_to_openwork.js` already performs any Core HTTP (this pass listed the plugin file, did not read its body as a join spec).

### Shape C — OpenWork “Add workspace MCP” → Core (transport ABSENT; not ready)

**Pipes (hypothetical)**

- OpenWork Library custom MCP → some Core MCP URL.
- Vendor docs: **server URL**, OAuth, dynamic client registration. Gateway for the reverse direction is `https://api.openworklabs.com/mcp/agent` (OpenWork **as server** to Cursor/etc.).

**Why this is not a live join**

- Core HTTP MCP **404**.
- `cosmos_mcp.py` is stdio and **not** started by `serve`.
- Vendor custom-MCP UI is URL-shaped; stdio attach is **UNMEASURED**.
- Pointing Core at the **OpenWork MCP Gateway** would pull OpenWork skills **into** Core — that **is** rebuilding the harness inside CORE. That is the anti-join.

**Failure modes if forced**

- OAuth/DCR against a bearer-loopback Core is a new auth story (loopback open, LAN closed). Easy to punch a hole.
- MCP `cosmos_submit` maps to job submit — same rogue-dispatcher class as Shape B POST.
- A BUILD of an HTTP MCP adapter would be Gitur **after** research, not this file.

**UNMEASURED:** OpenWork Add-MCP dialog field list on 0.18.42 (docs show URL; UI not screenshotted this pass).

---

## 4. What is **not** the join

| Not the join | Why (bound) |
|---|---|
| **Iframe `OpenWork.exe`** | P5 / `OPENWORK_EMBED`: no HTML origin; Electron `/health` is API-only. Dual-window is allowed. |
| **Iframe OpenWork Web** | Cloud-hosted; $50/member; BIND Off; URL is a credential class. Vendor: not opened from the desktop app. |
| **Second Core** | One resident service, one ledger writer, `tree_id=KMesh-COSMOS-live`. T7 is update hub / `NO_HOST`, not a second Core (`ORCH_HOME_SPEC`). |
| **Second skill OS inside CORE** | OpenWork already has Library/skills/plugins/MCP. Constraint: do not rebuild them in CORE. |
| **27th CLOCKS row that is OpenWork Automations** | 26 native Windows clocks exist. OW Automations need `OpenWork.exe` up and miss if not. Different vehicle, different failure. |
| **COSMOS root grant to OpenWork** | Two pens. Folder grant = pen. Cowork’s write-pen scar. `cosmos_grant` in cDeck must stay false. |
| **Rebuild Open Sessions / re-ingest 666** | Product already ships on `GET /api/v1/recents`. SHARE.md + question: seed only; federation keeps the pack on COSMOS. |
| **Reverse MCP Gateway into Core** | That is OpenWork consuming Core’s mouth from inside Core. Clone. |
| **Merge cDeck and OpenWork this research** | Keith: until they merge, TUI left HP 24N, GFO fullscreen right HP 24N. Occupancy now; merge later. |
| **PR #45 as the answer** | Independent lane. Not used. |
| **Merging GitHub PRs #30 #32 #36 #37 #38** | Explicitly out. |
| **Opening legal transcripts** | `n_omitted_legal: 108`. Catalog may list; this file did not open them. Legal stays GFO+Keith. |
| **OpenWork as ledger writer** | P10 / CCr / one writer. |

---

## 5. Recommended next measurement (one experiment, Gitur-sized, not a BUILD)

**Name:** `gfo-loopback-status-receipt`  
**Question it answers:** Can the **GFO sit agent** (OpenWork chat on `ws_726c64a2afa5` / `V:\OPENWORK\COSMOS_2`) **itself** `GET http://127.0.0.1:8770/api/v1/status` and write **only** `{tree_id, ledger_head.seq, served_at}` to `V:\OPENWORK\COSMOS_2\cm\CORE_STATUS.json` — without a COSMOS folder grant, without POST `/jobs`, without touching `cosmos/`?

**Why this one**

- Shape A pipe 2 and Shape B both hinge on it.
- `_boot.json` already **quotes** Core, but provenance is UNMEASURED (agent vs paste vs CCr).
- Closes the sit/kept LIVE mismatch only after we know the **agent** can see Core; port-map for COSMOS_2 is a **separate** later measurement (read-only dump of `openwork_status` JSON from cDeck — even smaller, but it does not prove GFO can call Core).
- Gitur-sized: one branch if a local `SKILL.md` is added **in the grant**; **zero** CORE files; one PR only if the skill is versioned. Side jobs included means: do not sneak a `cosmos_mcp` HTTP adapter onto the same branch.

**Pass**

- File exists on the sit `cm\`.
- `tree_id` equals `KMesh-COSMOS-live`.
- `seq` is a live ledger head (must move vs a stale paste).
- No new CLOCKS row, no iframe, no grant expansion, no `/api/v1/jobs` POST.

**Fail-closed**

- Agent cannot reach loopback → Shape B dies; Shape A mailbox remains. Record the refusal body. Do not punch a COSMOS root grant to “fix” it.

**Out of this experiment**

- Add workspace MCP. HTTP MCP adapter. Recode `cowork_to_openwork`. Re-ingest 666. OpenWork Web. Legal files. Merging PRs. Writing `cosmos/`.

A smaller **optional** companion (still not BUILD): one Python one-liner already done this pass — cDeck LIVE for activeId COSMOS_2 is **portless** while Streams `:61512` `/health` is **ok:true**. That mismatch is bound; it does not need a second experiment unless cDeck `openwork_status` JSON should be quoted from a running `cdeck.exe` (UNMEASURED this sit — this pass read `lib.rs`, did not invoke the Tauri command).

---

## 6. UNKNOWN (explicit)

- OpenWork Connect chips actually connected on this org.
- Any live Automation rows / desktop-runner connected bit.
- OpenWork Browser enabled in Library.
- Whether `COSMOS_2` and `COSMOS 2` are one folder.
- Whether GFO in-chat HTTP caused `_boot.json` or a human/CCr wrote it.
- Live bodies of `/api/v1/audit|spend|events|rails|surfaces|fleet|nodemap|jukebox` (routes exist in code; not hit).
- Whether OpenWork 0.18.42 Add-MCP accepts stdio.
- Headless OpenWork HTML origin (embed stays UNMEASURED).
- Tailscale path: OpenWork calling Core **with** bearer (loopback does not prove remote).
- PR #45 contents (not read as the answer).

---

## 7. Lane A bounds kept

- P10 propose-only for CORE. This artifact is research in the Gitur worktree.
- Did not iframe. Did not open legal transcripts. Did not merge PRs #30 #32 #36 #37 #38.
- Did not treat `docs/arch/OPENWORK_INTEGRATION.md` or PR #45 as the answer.
- Accidental Core queue write: `POST /api/v1/jobs` probe `job_id=1788663008628-afe18b3af0` command `lane-a-probe-do-not-run`. Not a work order. CCr may ignore or CLEAN.
