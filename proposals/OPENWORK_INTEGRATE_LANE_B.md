# OPENWORK × COSMOS — INTEGRATION RESEARCH, **LANE B**

**Stage:** 1 RESEARCH. Not ARCH. Not BUILD. No join is designed here; no code is proposed for
application. **P10 — PROPOSE only.** Nothing in the COSMOS live tree was written by this lane.

**Question:** `docs/research/OPENWORK_INTEGRATE_Q.md` (read at `10027c9`).
**Lane:** B — Cursor Cloud Agent, independent clone, model **Claude Opus 5** (Composer 2.5 refused;
`docs/AGENTS.md` "Adversarial loop" and the assignment both pin this).
**Lane isolation honored:** `docs/arch/OPENWORK_INTEGRATION.md` was **not opened** (it is also absent
from this clone — §0.3). **PR #45 was not fetched or read.** No PR was merged. No legal transcript
was opened. Lane A output was not read.

---

## 0. PROVENANCE — what this lane actually stood on

A claim is not evidence. This section states the measurement surface so every later claim can be
graded, because Lane B ran on a **Linux cloud clone, not Keith's Windows machine**. That materially
limits what "measured" can mean here, and pretending otherwise would be the fabricated-compliance
failure class.

| | |
|---|---|
| Surface | Cursor Cloud Agent VM, `Linux 6.12.94+`, `Python 3.12.3` |
| Repo | `/workspace` @ `10027c9eaffb1026b7b660ffe729044e99192a14`, branch `cursor/openwork-cosmos-integration-0f09` (cut from `ccr/openwork-integrate-q`) |
| Run at | `2026-09-06T02:51:50Z` |
| Core `:8770` | **NOT REACHABLE.** No live Core on this VM. |
| `live/` runtime root | **ABSENT** (gitignored by design; `.cosmos-root.json`, `live/config/api_token.txt` all absent). |
| `OpenWork.exe` | **NOT PRESENT.** No Windows install to probe. |

### 0.1 Three evidence grades used below

- **MEASURED (Lane B)** — this lane ran it and quotes the bytes it emitted.
- **BOUND (source)** — read directly from tracked repo source, cited `file:line`.
- **BOUND (vendor)** — read directly from `openworklabs.com` vendor docs, cited by URL.
- **BOUND (secondhand)** — asserted by a tracked COSMOS doc from a prior host-side measurement
  (chiefly `docs/OPENWORK_BIND.md`). Lane B could **not** re-verify these. They are Keith's/CCr's
  measurements, carried forward, and marked as such — not re-measured by me.
- **UNMEASURED / UNKNOWN** — nobody has bound it, or Lane B could not.

### 0.2 What Lane B could genuinely measure

Exactly one thing of consequence, and it turned out to matter: **COSMOS's MCP server module runs and
emits real protocol bytes** (§2.3). Everything else is source-bound or doc-bound.

### 0.3 Two bound starting points were NOT readable from Lane B — reported, not papered over

The question lists `builds/cdeck/ORCH_HOME_SPEC.md` P5 (C0 OPEN/LIVE; embed UNMEASURED) as a bound
starting point. **Lane B could not read it.**

```
$ git ls-files -s builds/cdeck
160000 f4270d0953a5e2b8d17b33aac3fe826e8767e86a 0    builds/cdeck
$ cat .gitmodules
cat: .gitmodules: No such file or directory
```

`builds/cdeck` is tracked as a **gitlink (mode 160000)** pointing at commit `f4270d0`, with **no
`.gitmodules` entry**. It is an unregistered/uninitialized submodule: the directory clones empty and
`git submodule update` has no URL to work from. `ORCH_HOME_SPEC.md` is absent from the working tree
**and** from all reachable history (`git log --all -- '*ORCH_HOME_SPEC*'` → empty).

Consequences, all of which are findings rather than excuses:

1. **C0 OPEN/LIVE claims in this artifact are BOUND (secondhand)** via the `Pane` row of
   `docs/OPENWORK_BIND.md`, not read from P5. Where Lane A read P5 directly, **prefer Lane A** on C0.
2. **`cosmos_recents_panel` is absent**, so `GET /api/v1/recents` response *semantics* are UNKNOWN to
   Lane B (only its dispatch is bound — §2.2).
3. **The first COSMOS product does not run from a fresh clone.** Measured:
   ```
   $ python3 builds/open_sessions/test_open_sessions.py
   ModuleNotFoundError: No module named 'cosmos_recents_panel'
   ```
   `builds/open_sessions/Open_sessions.py:23,27` puts `builds/cdeck` on `sys.path` and imports
   `handle_get` from it. **This is a Gitur finding, not a cDeck finding** — see §5.4. "One job, one
   branch, one PR" silently assumes a branch is self-contained. This one is not, and any lane, CI
   job, or Cursor/Copilot agent that checks it out inherits a product that cannot import.

### 0.4 Term not bound in-tree

**"Gitur" appears nowhere in the tracked repo** (`git ls-files | grep -i gitur` → empty; no hit
across `docs/*.md`). Lane B uses only the definition given in the question itself — *BUILD lands on
branched trees; one job, one branch, one PR; side jobs included* — and marks the term
**UNKNOWN-in-tree**. If Gitur is meant to be canon, it has no doc yet.

---

## 1. WHAT OPENWORK OFFERS THAT COSMOS WOULD HAVE TO REBUILD IF IGNORED

### 1.1 This install

| Fact | Value | Grade |
|---|---|---|
| Vendor / repo | OpenWork Labs / `different-ai`, `github.com/different-ai/openwork` (public; MIT except `ee/` Den) | BOUND (secondhand) `docs/OPENWORK_BIND.md` |
| Version | **0.18.42** (2026-09-03) | BOUND (secondhand) |
| Install path | `C:\Users\Papa\AppData\Local\Programs\@openworkdesktop\OpenWork.exe` | BOUND (secondhand) |
| State | `%AppData%\com.differentai.openwork\` | BOUND (secondhand) |
| **Grant (the pen)** | **`V:\Streams\openwork`**, workspace id `ws_12669390bcf4`, display name `COSMOS` | BOUND (secondhand) |
| Authorized folders | **none extra** (`cm\`, `legal\` are inside the root) | BOUND (secondhand) |
| Loopback `/health` | port **57383**, from `openwork-server-state.json` | BOUND (secondhand) |
| Cloud org | `COSMOS`, Creator plan, 1 member, `keith.bbf@gmail.com` | BOUND (secondhand) |
| Team seats | Included 1/5, **$0** | BOUND (secondhand) |
| OpenWork Web | **Off**, $50/joined member if bought | BOUND (secondhand) |
| AI model access | **Active $10/mo** | BOUND (secondhand) |

> ⚠ **`/health` is a name collision and a wiring hazard.** The `/health` at **57383** is
> **OpenWork's** loopback health, not COSMOS's. **COSMOS Core has no root `/health`** — measured
> absent from the router; the COSMOS health route is **`/api/v1/health`**
> (`cosmos/cosmos_service.py:615-617`). Anything that probes `:8770/health` expecting a COSMOS
> answer will 404. Two different products, two different ports, one identical path name.

### 1.2 The capability inventory — what rebuilding would actually cost

Bound to the vendor doc index (`https://openworklabs.com/docs/llms.txt`, fetched 2026-09-06) and to
the pages named. This is the concrete content of Keith's *"OpenWork has too much of what we need to
ignore."*

| Capability | What it is (vendor) | COSMOS today | Rebuild cost if ignored |
|---|---|---|---|
| **Workspace MCP client** | `Settings > Library > Advanced settings > Add workspace MCP`. Custom/local MCP servers, **free, no Cloud account, local to the workspace**. OAuth or `OAuth on this device` for pre-registered clients. [add-an-mcp-server](https://openworklabs.com/docs/start-here/connect-your-stack/add-an-mcp-server.md) | `cosmos_mcp_client.py` exists (stdio, outbound) but is wired only to `@playwright/mcp` (`cosmos_playwright_rail.py:45-46`) | **This is the socket the whole join can plug into.** See §3.1. Rebuilding OpenWork's side is pointless; COSMOS only has to be a server. |
| **Skills / plugins / Library / marketplaces / Collections** | Full config-object system: versioned immutable skill objects, plugins, access grants, org marketplaces, publish/copy | none | Very high, and explicitly out of bounds |
| **Connectors** | Gmail, Calendar, Drive, Outlook, OneDrive, Teams, GitHub, Notion, Linear, Stripe, Slack presets; per-member vs shared credential modes; OAuth + SCIM/SSO | none | Very high; this is a credential-management product |
| **Automations** | Den-scheduled, durable run history, leases (`queued/claimed/running`), heartbeat, cancel; desktop-created run on **this PC's connected runner**; **no runner connected ⇒ occurrence recorded MISSED**; runtime **10s–1h** | native Windows `pythonw` + `schtasks` (Pulse, collector, WD2, health, feed, runner) | Duplicating is **forbidden** by the question, and correctly so — see §4.5 |
| **Built-in browser** | Runs + screenshots tasks in Chrome | `cosmos_playwright_rail.py` (own Playwright rail) | Partial overlap already |
| **Cross-chat memory / session groups / workflows** | Answers about past sessions; chat + session-group organization; Workflow versions with immutable receipts | Open Sessions product + `cowork_to_openwork` seed | Overlaps the 666-pack work |
| **OpenWork MCP Gateway** | One **hosted** endpoint exposing org skills/plugins/connections **into any MCP client** (Cursor, Claude Code, Codex, VS Code, Gemini CLI…) [cloud-mcp](https://openworklabs.com/docs/cloud/run-in-the-cloud/cloud-mcp.md) | `cosmos_mcp_client.py` could consume it | The **direction-inverted** shape — §3.4 |
| **Self-host (Den)** | Full control plane: Docker Compose eval, or K8s/Helm + **managed MySQL** on AWS/Azure/GCP | — | A second control plane. **Not the join** — §4.3 |

**Concurrency, bound (secondhand, vendor 2026-09-04, `docs/OPENWORK_BIND.md`):** interactive left
pane is **one conversation**; Automations are separate leased threads; **long-running /
laptop-closed background is still "Building" on the roadmap and scheduled tasks are "Partial."**
Usage is **shared org buckets**, not a hard one-agent lock.

**The load-bearing consequence:** OpenWork Automations **cannot** be COSMOS's clock. Its floor is
10s, its runner must be up or the occurrence is *missed*, and its own vendor roadmap calls the
background case unfinished. `docs/OPENWORK_BIND.md` already states the verdict — *"No as the clock"*
— and `docs/ORCH_SEAT.md` names the failure class (the Claude-scheduler scar). Lane B concurs and
adds: a missed-occurrence semantic is a **silent** failure, which is precisely what a fail-closed
system must not adopt for its heartbeat.

---

## 2. WHAT COSMOS ALREADY EXPOSES THAT OPENWORK COULD CALL

### 2.1 Core HTTP — the full `:8770` surface

All BOUND (source), `cosmos/cosmos_service.py`. Default port **8770** (`cosmos/cosmos.py:43`),
default bind **`127.0.0.1`** (`cosmos/cosmos.py:138`; `0.0.0.0` only with `--remote`).

**GET `/api/v1/*`**

| Path | Line | Notes |
|---|---|---|
| `/api/v1/status` | 602-608 | ready, root, `tree_id`, ledger head |
| `/api/v1/audit` | 609-610 | audit projection |
| `/api/v1/jobs` | 611-614 | job states |
| `/api/v1/health` | 615-617 | HealthBoard — **the real health route** |
| `/api/v1/spend` | 618-619 | spend gate audit |
| `/api/v1/tools` | 620-632 | ToolContracts report |
| `/api/v1/events` | 633-667 | ledger page/tail; `since_seq`, `tail` (1..100) |
| `/api/v1/rails`, `/api/v1/nodes` | 668-678 | registry matrix (aliases) |
| `/api/v1/surfaces` | 679-687 | surfaces catalog |
| `/api/v1/fleet`, `/api/v1/nodemap`, `/api/v1/jukebox`, `/api/v1/recents` | 688-705 | cDeck C0 panels |
| `/api/v1/makers` | 706-728 | `kind`, `tag`, `text` |
| `/api/v1/control` | 592-601 | `client_id` |
| `/api/v1/cvm/pull` | 729-745 | `client_id` required |

**POST `/api/v1/*`:** `/kill` (749-767), `/control/resume` (771-789), `/spend` (790-821), `/voice`
(822-1238), `/command` (1239-1252), `/crucible` (1253-1337), `/jobs` (1338-1347), `/makers`
(1348-1366), `/cvm/snapshot` + `/cvm/push` (1369-1395).

**Static / unauthenticated:** `/`, `/m`, `/mobile`, `/dash`, `/cdeck/*`, manifests, service workers,
the APK, and `/kill`. **No root `/health`.**

### 2.2 cDeck C0 and `GET /api/v1/recents`

Dispatch is BOUND (source): `_CDECK_PANEL_MOD` maps `/api/v1/recents → cosmos_recents_panel`
(`cosmos_service.py:224-229`), and `recents` is the one panel that gets its query string parsed
(`688-697`). Parameters `open=1` and `id=<sid>` are bound from the caller
(`builds/open_sessions/Open_sessions.py:50-53`). A `limit` parameter is **ABSENT** from tracked
source. Response semantics are **UNKNOWN to Lane B** — the handler module is behind the empty
gitlink (§0.3). The open path's response reportedly carries an `openwork` field
(`Open_sessions.py:101`), which is the existing C0 "OpenWork focus" seam, but Lane B **cannot** say
what it contains.

### 2.3 MCP — the finding that reframes the question

The question asks Lane B to *"note MCP **absent** if you measure that."* Measured, the honest answer
is more useful than absent-or-present, because it splits three ways:

| Face | Status | Evidence |
|---|---|---|
| MCP over Core HTTP `:8770` | **ABSENT** | No MCP route in `do_GET`/`do_POST`; no `text/event-stream`, `/sse`, `FastMCP`, `@modelcontextprotocol`, `streamableHttp` anywhere in `cosmos/*.py`. Core is JSON REST only. |
| MCP **client** (outbound) | **PRESENT** | `cosmos/cosmos_mcp_client.py` — stdio JSON-RPC client, `initialize → tools/list → tools/call` (`255-373`); used against `@playwright/mcp`. |
| MCP **server** (stdio) | **PRESENT but UNWIRED** | `cosmos/cosmos_mcp.py` — stdio JSON-RPC 2.0 server exposing 7 kernel verbs. **Not** imported by `cosmos_service.py`, **not** reachable from `cosmos.py serve`, and has **no `if __name__ == "__main__"`** — there is no command that starts it. |

**So: COSMOS already speaks the exact protocol OpenWork's free local socket accepts — and nothing
can currently launch it.**

**MEASURED (Lane B).** Because `initialize` and `tools/list` never touch the kernel, Lane B drove
the real handler in this clone and captured what COSMOS actually emits:

```
# note the client deliberately asks for the CURRENT revision, 2026-07-28:
REQ  {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28",...}}
RESP {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05",
      "capabilities": {"tools": {}}, "serverInfo": {"name": "cosmos", "version": "1.0-f5"}}}

REQ  {"jsonrpc":"2.0","method":"notifications/initialized"}
RESP <none: notification>            # correct — notifications get no reply

REQ  {"jsonrpc":"2.0","id":2,"method":"tools/list"}
RESP {"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "cosmos_status", ...}, ...]}}
      # 7 tools: cosmos_status, cosmos_submit, cosmos_jobs, cosmos_audit,
      #          cosmos_health, cosmos_command, cosmos_events

REQ  {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"cosmos_status",...}}
RESP {"jsonrpc": "2.0", "id": 3, "error": {"code": -32603,
      "message": "AttributeError: 'NoneType' object has no attribute 'ledger'"}}
```

Three things this proves rather than asserts:

1. The handshake and tool catalogue are **real and emitted**, not aspirational.
2. With no kernel bound, a `tools/call` **fails closed with a typed JSON-RPC error** instead of
   inventing a result. Correct behavior.
3. **The protocol version is stale and is not negotiated — measured, not inferred.** The probe above
   deliberately asked for `2026-07-28` and COSMOS answered `2024-11-05` anyway. `PROTOCOL` is a module
   constant (`cosmos_mcp.py:22`) echoed at line 88; `initialize` **ignores the client's requested
   version entirely**. Against the vendor spec, the **current MCP revision is `2026-07-28`**, which
   **removed the `initialize`/`initialized` handshake altogether** (SEP-2575) in favor of per-request
   `_meta`, with a **12-month backward-compatibility window** for handshake-based revisions
   (`2025-11-25` and earlier) — [MCP versioning](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning),
   [2026-07-28 release candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/).
   The spec also says a server that cannot serve a requested version should answer
   `UnsupportedProtocolVersionError` listing what it does support. **COSMOS cannot do that** — it has
   one hardcoded answer. So COSMOS is inside the compatibility window but two revisions behind, and
   its handshake is take-it-or-leave-it.

**Whether OpenWork 0.18.42's MCP client accepts `2024-11-05` is the single highest-value UNKNOWN in
this entire research.** It is exactly what §5 proposes to measure.

### 2.4 The join is already open, and it is unfenced

This is Lane B's most consequential finding, and it inverts the framing of the question.

**BOUND (source)**, `cosmos/cosmos_service.py:331-344`:

```python
def _request_authed(peer, authorization, token, open_access=False):
    """...Wrong bearer on loopback still passes — the peer is this machine."""
    if open_access:
        return True
    if _is_loopback_peer(peer):
        return True
    ...
```

`_is_loopback_peer` (317-328) accepts `127.0.0.1` and `::ffff:127.0.0.1`. Combined with the default
bind of `127.0.0.1` (`cosmos.py:138`), this means:

> **Any process on Keith's machine already has full, unauthenticated access to COSMOS Core's entire
> `/api/v1/*` surface — including the write verbs `POST /api/v1/jobs`, `POST /api/v1/command`,
> `POST /api/v1/spend`, and `POST /api/v1/voice`.**

`OpenWork.exe` runs on that machine. So does every skill, MCP subprocess, shell command, and browser
task it spawns. **OpenWork can already drive COSMOS Core today, with no token, no grant, and no code
on either side.** Nothing needs to be opened.

This is a deliberate design decision (Keith 2026-09-04, quoted in the docstring: loopback
auto-connects, Tailscale/LAN still need the bearer), and for cDeck-in-a-local-browser it is
reasonable. But it changes what "integrate" means:

**The integration problem is not connectivity. It is narrowing, typing, and attributing a channel
that is currently wide, untyped, and anonymous.**

Two corollaries that should survive into ARCH:

- **Attribution gap.** Core's ledger records its own writer, not the loopback caller. A job submitted
  by GFO and a job submitted by cDeck are, as far as Lane B can tell from source, indistinguishable
  in the ledger. If ORC starts operating Core, "who did that" becomes unanswerable. That is a
  fail-closed problem: the ledger is the authority, and it cannot currently attribute the new actor.
  (Whether any peer identity is recorded is **UNMEASURED** — Lane B did not exhaustively audit the
  ledger event schema.)
- **No CORS, by explicit design.** No `Access-Control-Allow-Origin` header is ever emitted, and there
  is no `do_OPTIONS`. The module docstring (86-87) states the intent: *"a header that would let any
  other origin read Core is not added."* So OpenWork's **built-in browser** (a web origin) is blocked,
  while an OpenWork **subprocess** is not. This asymmetry cleanly separates the candidate shapes in §3
  — and it means the tempting "just add CORS" move is a non-join (§4.6).

---

## 3. CANDIDATE JOIN SHAPES

Four, deliberately independent: different **transport**, different **trust model**, different
**failure class**. None is recommended here — Stage 1 does not choose. They are laid out so ARCH can.

---

### 3.1 Shape A — **MCP tool-face**: COSMOS registered as a workspace MCP server in OpenWork

**Pipe.** OpenWork Desktop spawns COSMOS's stdio MCP server as a child process and speaks JSON-RPC
over stdin/stdout. Registered by hand once via `Settings > Library > Advanced settings > Add
workspace MCP` — free, local, no Cloud account (BOUND vendor).

**Process split.**
- *Stays in COSMOS:* the kernel, ledger, leases, scheduler, spend gate. Every tool call delegates to
  the kernel and is ledgered — `cosmos_mcp.py:6-10` states the invariant plainly: *"an MCP client
  cannot reach around the authority."*
- *Stays in OpenWork:* skills, Library, model routing, connectors, browser, Automations, session
  groups. Nothing is rebuilt inside CORE.

**Why it fits the constraints.** The **tool list *is* the grant.** OpenWork receives seven named
verbs, not a filesystem. No COSMOS folder grant, root or authorized, is needed or implied — which is
the literal reading of "folder grant = pen" (`docs/CCR.md`, `docs/AGENT_BOUNDARIES.md` item 9)
extended to a capability grant. It is also the only shape that gives ORC **typed** hands: GFO calls
`cosmos_status`, not a URL it composed, which directly mitigates the CoT-ghosting risk
`docs/ORCH_SEAT.md` names.

**Failure modes.**
1. **Protocol staleness (highest risk).** `2024-11-05`, no negotiation, against a client of unknown
   vintage in a world where current is `2026-07-28` (§2.3).
2. **No launcher.** No `__main__`; a command line must construct a `Kernel` first.
3. **Second-writer hazard.** `cosmos_mcp.py` needs a live `Kernel`. Constructed read-write, that is a
   **second ledger writer** beside the serving Core — a direct hit on the one-writer invariant and
   the two-writer deletion scar. `cosmos.py:95` shows the read-only construction path
   (`Kernel(root, worker="cli", read_only=...)`), so a read-only kernel is available; whether every
   tool degrades correctly under it is **UNMEASURED**.
4. **Write verbs in the tool list.** `cosmos_submit` and `cosmos_command` are **actions**, not
   proposals. Handing them to ORC sits in tension with P10 (agents propose, CCr disposes). A
   read-only subset (`status`, `jobs`, `audit`, `health`, `events`) is the P10-safe cut; anything
   beyond it is a governance decision for Keith, not an engineering default.
5. **Stdio is single-client and per-spawn.** Startup cost per kernel construction, and no obvious
   story for two OpenWork workspaces at once.

**UNMEASURED.** Whether OpenWork 0.18.42 accepts `2024-11-05`; how it passes `cwd`/env/args to a
local server; whether it tolerates a server that ignores requested version; whether tool errors
surface legibly to GFO; concurrency; whether the child survives OpenWork restarts.

---

### 3.2 Shape B — **HTTP client-face**: OpenWork calls Core `/api/v1/*` over loopback

**Pipe.** Plain HTTP from an OpenWork skill or shell command to `http://127.0.0.1:8770/api/v1/*`.

**Process split.** Everything stays where it is. Core remains sole authority and sole ledger writer;
no new process, no new protocol, no new code on either side.

**Status: this shape already works today, uncoded and unfenced** (§2.4). That is its defining
property and the reason it must be evaluated rather than ignored — *it is the default that obtains if
nobody decides anything.*

**Failure modes.**
1. **No fence.** Ambient authority for every local process. The write verbs are exposed to anything
   OpenWork spawns, including model-authored shell commands.
2. **No attribution.** See §2.4.
3. **Untyped.** The model composes URLs and JSON by hand — the exact surface where CoT-ghosting
   produces structurally valid, semantically wrong calls.
4. **Brittle paths.** Most handlers compare `self.path` **exactly** (e.g. 602, 609), so any query
   string on those routes 404s. Only `recents`, `events`, `makers`, `control`, `cvm/pull` parse a
   query. A caller that appends `?` to `/api/v1/status` gets a 404 that looks like "Core is down."
5. **Browser-blocked.** No CORS ⇒ OpenWork's built-in browser cannot do this; only subprocesses can.

**UNMEASURED.** Whether OpenWork skills can issue arbitrary local HTTP/shell under the grant, and
whether desktop policies can constrain that.

---

### 3.3 Shape C — **Mailbox / two-drive file join** (the shape already half-built)

**Pipe.** The filesystem. `V:\Streams\openwork\cm\` is *already declared* the COSMOS orch mailbox
that CCr harvests (`docs/OPENWORK_BIND.md` Permissions table). Plus `work_orders/drop/` and
`work_orders/ccr/` (`docs/CCR.md` "Queue for next Cm"; both directories exist in-tree). Plus the
declared read posture: **ORC and CCr each read-write their own tree and both fully read the other's**
(`docs/ORCH_SEAT.md`, Keith 2026-09-05).

**Process split.** Total. Neither process calls the other; they exchange typed files.

**Why it fits.** It is the **only shape already consistent with two pens and P10 with no new
protocol**: GFO proposes into `cm\`/`work_orders/`, CCr disposes through the fenced commit gateway.
It cannot create a second ledger writer because it does not touch the ledger.

**Failure modes.**
1. **Latency, and the clock is contested.** A file drop is inert until something harvests it. The
   question forbids a 27th CLOCKS row, so harvesting must ride an existing native clock (collector /
   WD2 / dispatcher). Which one is a real, unresolved decision.
2. **A drop is not a lease.** No fencing token, no claim, no exactly-once. Two harvests could double-
   apply unless the existing head-fence covers it.
3. **No schema enforcement at the boundary** unless the typed work-order spec is enforced on read
   (`docs/WORK_ORDER_SPEC.md`, `docs/VERDICT_SPEC.md` are referenced by `docs/AGENTS.md`).
4. **Grant drift is already measured.** GFO's 666-session pack landed on the **leftover**
   `C:\Users\Papa\OpenWork Chat\cow_sessions\`, **not** the granted `V:\Streams\openwork`
   (`docs/ORCH_SEAT.md`, "Grant mismatch"). The mailbox only works if both parties agree where it is,
   and on the one measured occasion they did not.
5. **Stream-count disagreement already measured.** GFO's table and the catalog JSON disagree on
   per-stream counts for the same 666 (`docs/ORCH_SEAT.md`). A file join inherits whatever the writer
   believed; there is no reconciliation step.

**UNMEASURED.** Whether GFO reliably writes `cm\`; which clock harvests; whether `work_orders/ccr/`
is being consumed today.

---

### 3.4 Shape D — **Direction-inverted**: COSMOS consumes OpenWork as an MCP server

Included because it is the only shape where **COSMOS gains OpenWork's capabilities** rather than the
reverse — the most literal answer to *"OpenWork has too much of what we need to ignore."*

**Pipe.** `cosmos_mcp_client.py` (already a working stdio MCP client) points at OpenWork's exposed
MCP surface. Vendor offers the **OpenWork MCP Gateway**: one hosted endpoint bringing org skills,
plugins, and connections into *any* MCP client, with Cursor/Claude Code/Codex/VS Code/Gemini CLI all
documented ([cloud-mcp](https://openworklabs.com/docs/cloud/run-in-the-cloud/cloud-mcp.md),
[agent-plugins](https://openworklabs.com/docs/model-context-protocol/agent-plugins.md)). COSMOS would
gain Gmail/Drive/Calendar/GitHub connectors without building a credential product.

**Process split.** OpenWork keeps connectors and credentials. COSMOS keeps authority and gains hands.

**Failure modes.**
1. **It is a Cloud dependency.** The Gateway is hosted, so the endpoint URL plus token behaves like a
   credential — the same objection that rules out Cloud Web. It is **not** the same SKU as OpenWork
   Web ($50, currently Off), but Lane B has **not** established that the Gateway is free on the
   current Creator plan. **UNMEASURED, and it is a money question — Keith's alone.**
2. **Violates DOM-first / no-runnable-out-of-credit** in spirit: a hosted gateway can lapse.
3. Inverts the ORC story — this serves CCr and Core, not GFO's seat.

**UNMEASURED.** Gateway availability and cost on Creator plan; whether the desktop (not Cloud) can
expose a purely local MCP server face at all. **Lane B found no vendor doc for a local/desktop MCP
*server* face — only the desktop as MCP *client* (§1.2) and the Gateway as a *Cloud* server.** If
that holds, Shape D is Cloud-only, and the local-only join must be A, B, or C.

---

### 3.5 Independence check

| | A (MCP) | B (HTTP) | C (files) | D (inverted) |
|---|---|---|---|---|
| Transport | stdio JSON-RPC | loopback HTTP | filesystem | stdio/HTTP to vendor |
| Trust model | typed capability grant | ambient loopback | two-pen proposal | vendor credential |
| Direction | OW → COSMOS | OW → COSMOS | bidirectional, async | COSMOS → OW |
| Dominant failure | protocol staleness | unfenced authority | latency + drift | Cloud dependency |
| New code needed | launcher only | **none** | harvest wiring | client config |
| Second-writer risk | **yes**, if kernel is RW | no | no | no |

A and B are not variants of each other: A adds a fence and a type system that B lacks, and B needs no
code while A needs a launcher. C is orthogonal to both. D reverses the arrow.

---

## 4. WHAT IS **NOT** THE JOIN

1. **Iframing `OpenWork.exe`.** An Electron desktop app has no HTML origin to embed. `docs/OPENWORK_BIND.md`
   records embed as **UNMEASURED** and the standing instruction as *"Never iframe."* Lane B adds
   nothing that changes this.
2. **Iframing OpenWork Web (Cloud).** The URL is a credential, the SKU is **Off**, and it costs $50
   per joined member. The desktop app does not need it. Keith does money; this lane does not click
   Purchase.
3. **A second Core, or a second Den.** Self-hosting Den means a full control plane — Docker Compose
   for evaluation, or K8s/Helm plus managed MySQL on AWS/Azure/GCP (BOUND vendor). That is a second
   authority next to Core, contradicting one-authority/one-ledger-writer and `docs/CCR.md`
   ("Do not fork Core"; decision 7: UI may deploy separately, authority may not).
4. **A second skill OS inside CORE.** Rebuilding skills/Library/MCP/Automations/browser inside
   `cosmos/` is forbidden by the question and would violate improvement-not-bloat: net complexity up,
   capability merely duplicated.
5. **A 27th CLOCKS row mirroring OpenWork Automations.** Native COSMOS clocks stay Windows
   `pythonw` + `schtasks`. Automations' floor is 10s, its ceiling 1h, and a due run with no connected
   runner is recorded **missed** — a silent failure the heartbeat cannot adopt.
6. **Adding CORS to Core so OpenWork's browser can call it.** This will look like the easy fix. It is
   not the join: the no-CORS posture is deliberate and documented in-source
   (`cosmos_service.py:86-87`), and relaxing it would widen an origin boundary at the same moment
   §2.4 shows the local boundary is already too wide. Named here so ARCH rules it out on purpose
   rather than rediscovering it.
7. **Granting OpenWork `V:\A\Ai\COSMOS`** (root or authorized). Standing and repeated:
   `AGENT_BOUNDARIES` item 9, `CCR.md`, `OPENWORK_BIND.md`, `ORCH_SEAT.md`. The display name "COSMOS"
   on the Cloud org and the workspace is **branding, not a tree grant.**
8. **Re-ingesting the 666.** They stay on COSMOS for federation. `cowork_to_openwork` is a seed, not
   an ORC recode. Do not rebuild Open Sessions in place.
9. **Legal.** Stays GFO + Keith. Not opened here.

---

## 5. RECOMMENDED NEXT MEASUREMENT — **one** experiment, Gitur-sized

### 5.1 The measurement

> **M1 — Does OpenWork Desktop 0.18.42 complete an MCP handshake with COSMOS's *existing* stdio MCP
> server, and can it call one read-only tool that returns a value only the live tree can emit?**

### 5.2 Why this one and not another

Every other question in this artifact is either already answered or is downstream of this one.

- Shape A is the only candidate that satisfies *all* the stated constraints at once — typed hands for
  ORC, no folder grant, nothing rebuilt in CORE, no new clock. Everything about it is already measured
  **except** whether the two ends actually speak. The server exists, its seven tools are enumerated,
  and Lane B has its emitted bytes (§2.3). The client socket is vendor-documented and free (§1.2).
  **One unknown sits between them: `2024-11-05` versus whatever OpenWork 0.18.42 speaks** — and the
  current spec revision removed that handshake entirely (§2.3).
- The result is decisive either way. **Pass** ⇒ Shape A becomes the leading ARCH input and the
  remaining questions are governance ones (which tools, read-only kernel). **Fail** ⇒ Shape A costs a
  protocol bump to CORE before it is even designable, which re-weights ARCH toward C (or B, fenced).
- It is cheap, reversible, and touches nothing.

### 5.3 Why it is a MEASUREMENT, not a BUILD

**No CORE file is created or edited.** `cosmos_mcp.py` has no `__main__` (§2.3), but it does not need
one for this: the existing module can be launched from a command line, so registration in OpenWork is
pure configuration.

Sketch only — exact quoting/interpreter is the runner's problem, and `--root` must be the real
configured root, never a guessed path:

```
py -3.14 -c "import sys; sys.path.insert(0, r'V:\A\Ai\COSMOS\cosmos');
from cosmos_kernel import Kernel; from cosmos_mcp import MCPServer;
MCPServer(Kernel(r'V:\A\Ai\COSMOS\live', worker='mcp-probe', read_only=True)).serve_stdio()"
```

`read_only=True` is **mandatory** for the probe: it is the read-construction path already used by the
CLI (`cosmos.py:95`) and it is what keeps the probe from becoming a second ledger writer beside the
serving Core (§3.1 failure 3). If a read-only kernel refuses to construct, **that is a result** —
record it and stop.

### 5.4 Runtime-binding gate — what counts as proof

*Every gate executes; the final gate is runtime binding.* A screenshot of COSMOS appearing in
OpenWork's Library is **not** a pass — a tool list is fabricable from source, and Lane B just
fabricated one legitimately in §2.3.

**The pass condition is a value only the true, live run can emit.** Call `cosmos_status` from an
OpenWork chat and require the reply to carry **both**:

- `tree_id` = **`KMesh-COSMOS-live`**, and
- the **current `ledger_head.seq`**,

then **cross-check that same `seq` against `GET /api/v1/status` on `:8770` within the same minute.**
The tool list is static text; the ledger head is a live monotone counter that no static file and no
model can guess. If the two `seq` values agree, an OpenWork-spawned process really did reach the live
kernel. If OpenWork renders a plausible answer whose `seq` does not match Core, that is a
**fabricated-compliance catch** and the most valuable possible outcome — record it loudly.

### 5.5 Shape (Gitur)

One job, one branch, one PR — including the side job.

| | |
|---|---|
| Branch | `ccr/m1-openwork-mcp-probe` |
| Contents | **one** measurement record, `docs/research/M1_OPENWORK_MCP_PROBE.md` |
| Record must carry | OpenWork version; the exact launch command; the **verbatim** JSON-RPC lines exchanged (or the verbatim failure); the `tree_id` + both `seq` values with timestamps; a PASS/FAIL/REFUSED verdict |
| Side job (same PR) | **Register `builds/cdeck` properly** — either add the `.gitmodules` entry for gitlink `f4270d0` or land the panel sources. Rationale: §0.3 measured that a fresh clone yields an unimportable Open Sessions and an unreadable `ORCH_HOME_SPEC.md`. Every future lane, CI run, and vendor agent pays this tax until it is fixed, and it silently degraded *this* research. |
| Explicit non-goals | Do **not** patch `PROTOCOL`. Do **not** add `__main__`. Do **not** wire MCP into `cosmos.py serve`. Do **not** expose write tools. Those are CORE writes — CCr, after ARCH. |
| Fail-closed | On handshake failure, capture the exact error and **stop**. A refusal is a correct result, not a fault to route around. |

### 5.6 The finding that should reach ARCH even if M1 never runs

§2.4 stands on its own and does not depend on M1: **OpenWork can already drive COSMOS Core today —
unauthenticated, untyped, unattributed, over loopback.** The integration question is therefore not
*"how do we connect them"* but *"how do we narrow, type, and attribute a channel that is already
open."* Lane B recommends ARCH open from that premise rather than from a blank page.

---

## 6. UNKNOWN / UNMEASURED — consolidated

Fail-closed: listed rather than guessed.

| # | Unknown | Who could bind it |
|---|---|---|
| 1 | Does OpenWork 0.18.42 accept MCP `2024-11-05`? | **M1** |
| 2 | `builds/cdeck` panel sources + `ORCH_HOME_SPEC.md` P5 — C0 OPEN/LIVE detail | CCr / Lane A |
| 3 | `GET /api/v1/recents` response schema; the `openwork` field's contents | requires `cosmos_recents_panel` |
| 4 | Does the ledger attribute a loopback caller at all? | host-side audit of the event schema |
| 5 | Do all 7 MCP tools degrade correctly under a `read_only=True` kernel? | host-side |
| 6 | Can OpenWork skills issue arbitrary local HTTP/shell under the grant? Can desktop policies restrict it? | host-side |
| 7 | Is the OpenWork MCP Gateway available/free on the current Creator plan? | Keith (money) |
| 8 | Does OpenWork Desktop expose any **local** MCP *server* face? No vendor doc found. | vendor / host-side |
| 9 | Which existing native clock would harvest `cm\` under Shape C? | CCr |
| 10 | Is `work_orders/ccr/` being consumed today? | CCr |
| 11 | "Gitur" has no in-tree definition (§0.4) | Keith / CCr |
| 12 | Everything marked **BOUND (secondhand)** in §1.1 — Lane B could not re-verify a single host-side fact | host-side |

---

## 7. LANE B COMPLIANCE

| Constraint | Status |
|---|---|
| P10 — propose only, never write the live COSMOS tree | **HELD.** Only `proposals/OPENWORK_INTEGRATE_LANE_B.md` created, on a feature branch. No `cosmos/`, `docs/`, `tests/`, `kdash/`, `builds/`, or governance file touched. |
| Read `docs/AGENT_BRIEF.md` + `docs/AGENT_BOUNDARIES.md` first | **HELD** — both read before any other action. |
| Route CURSOR, pin Claude Opus 5, refuse Composer 2.5 / Auto | **HELD** — Opus 5. |
| Lane B = RESEARCH only, not ARCH, not BUILD | **HELD** — no design chosen, no code proposed for application. |
| Do not read `docs/arch/OPENWORK_INTEGRATION.md` | **HELD** — not opened (also absent from this clone). |
| Do not treat PR #45 as the answer | **HELD** — never fetched or read. |
| Independent of Lane A | **HELD** — Lane A output not read. |
| Do not merge PRs #30 #32 #36 #37 #38 | **HELD** — no merge, no PR interaction of any kind. |
| No `main` | **HELD** — branch `cursor/openwork-cosmos-integration-0f09`. |
| Do not open legal transcripts | **HELD.** |
| UNKNOWN where not bound | **HELD** — §0.1 grading, §6 register. |
| A claim is not evidence | **HELD** — §2.3 quotes emitted bytes; secondhand facts are labeled as such throughout. |

---

*Lane B ends here. This artifact does not choose a join. CCr compares lanes and disposes.*
