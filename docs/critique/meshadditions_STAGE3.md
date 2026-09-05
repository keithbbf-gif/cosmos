# Mesh additions — Motif STAGE-3 critique / rank (G46)

**Reviewer:** G46 (Grok Build), dispatched `motif_meshadditions_s3`
2026-08-25T23:27:01.371025-05:00
(`lg/g46_grok_motif_meshadditions_s3_you_are_g46_g_f554d9a5__t1800.py`, this job).
**Question:** is `docs/arch/meshadditions_ARCH.md` the thing we should wire for
slice-1 (`MCP-client` + `playwright-dom` + `firecrawl-web`) — scored against
**that document's own rubric** (§1 H1–H8 / S1–S5) and the live table in §3 —
not "is this good prose."
**Architect (stage 2):** G46, `motif_meshadditions_s2`
(DHx 2026-08-25T22:42:11.675905-05:00). Same family as this rank.
**Inputs asserted, then used:** `docs/arch/meshadditions_ARCH.md`,
`docs/MESH_ADDITIONS.md`, maker-hands
`docs/research/{PLAYWRIGHT_MCP,FIRECRAWL,MCP_REFERENCE_SERVERS,OLLAMA,GROQ}_HANDS.md`,
`docs/critique/makerhands_STAGE3.md` (prior rank; satellite-first),
rail contract `cosmos/cosmos_cursor_rail.py` + `cosmos/cosmos_rails.py` +
`cosmos/cosmos_registry.py`, DOM floor `cosmos/cosmos_browser.py`,
MCP **server** `cosmos/cosmos_mcp.py`, platform `cosmos/cosmos_platform.py`,
`docs/ROUTING.md`, `docs/FINAL_ARCHITECTURE.md` decision 6, `docs/BACKLOG.md`
Kernel-attach item.
**Core:** `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service`
were not edited. This file is docs-only. Slice-1 code is **not** this stage.

**Family note (process, not a packet defect):** Motif stage 3 is different-family
critique. The ARCH, the HANDS packet, makerhands STAGE3, and this rank are all
G46 / Grok-Build. Two adversarial lenses in this job (safety+fail-closed; DOM-first
+ Chapter-4) are the same family. **This is not three vendor votes.** COW still
owes `gem-api` and/or `oa-api` against the same rubric before treating the rank
as Motif vendor-plural consensus. Same-family rank is still bound to files +
host-side packets below. Contested items go to Keith as one line each; no third
model resolves.

`rc=0` on the s2 arch job is not complete. `--help` is not complete. HTTP 200 on
a vendor is not COSMOS stage 6. Stage 6 is a value only the live tree emits
*after* a rail is attached **or** a cursor-shaped `--gate` writes
`live/config/<name>_rail_probe.json` quoting a live field (cursor pattern,
bound this morning). This row has **not** passed stage 6.

---

## Verdict

**CONVERGE with locks. Do not REJECT slice-1. Do not stamp the ARCH as
Dispatcher-wired.**

The ARCH's *capability* pick is right: Playwright fills the named INTERACT hole
in `cosmos_browser.py`; Firecrawl keyless papers is a live Chapter-4 hand;
COSMOS still has no outbound MCP client (`cosmos_mcp.py` is server-only).
Ollama/Groq HOLD, n8n/Zapier/OpenRouter-`free` REJECT — those rows stand.

The ARCH's *packaging* is not the thing the machine executes on boot.
`Kernel.__init__` does not attach rails (`cosmos_kernel.py` 37–130).
`attach_to_kernel` on the authority ledger **refuses** unless `boot_compose=True`,
and that call site does not exist (`cosmos_cursor_rail.py` 552–566). Copying the
cursor-rail *shape* is correct; copying the ARCH diagram's "Dispatcher (existing)
→ adapters[link_id]" as if `serve` routed through it is a registered-but-dead
adapter (H3). Cursor already proved the honest satellite path this morning:
`live/config/cursor_rail_probe.json` `gated_at=2026-08-26T10:03:11-05:00`
`gate=PASS` `kernel_attached=false` `attach_refusal.refused=true`
`tree_id=KMesh-COSMOS-live` `live_value.apiKeyName=Cursor COSMOS 2`.

**Slice-1 after this critique:** three additive modules in that **satellite
`--gate` shape**, not Kernel compose, not a ROUTING.md default swap.

| lock | decision |
|---|---|
| **A** `cosmos/cosmos_mcp_client.py` | YES. Owns long-lived stdin Popen + tree-kill. `cosmos_platform.run` / `run_tree_killed` cannot keep a pipe (no `stdin=PIPE`; wait-for-exit). |
| **B** `cosmos/cosmos_playwright_rail.py` `link_id=playwright-dom` `kind=DOM` | YES. Probe = `tools/list` containing `browser_navigate` **and** `browser_snapshot` (bound this job, not `--help`). |
| **C** `cosmos/cosmos_firecrawl_rail.py` `link_id=firecrawl-web` `kind=API` | YES. Keyless `scrape` / `search` / `papers`. Papers is the first `--gate`. Crawl/map stay `AUTH_REQUIRED` without `fc-`. |
| **D** Kernel / ledger / sched / service | NO EDIT. `attach_to_kernel` copies cursor: refuse authority ledger; isolated `--gate` ledger only. |
| **E** ARCH §6 first-links | **REJECT** for search and known-URL READ. `docs/ROUTING.md` search default stays SGH DOM. Known-URL READ stays dump-dom first (H4). Firecrawl papers is additive (no ROUTING row). |
| **F** `policy_rank` above dump-dom | **REJECT** as a `Registry.route` implementation. No job class (`cosmos_registry.py` 108–127). Distinct `dst` / caller-picked job class, or do not register both on the same route. |
| **G** 429 / 402 | **Not** `UNREACHABLE`. Dispatcher `RAIL_FALLBACK` on `UNREACHABLE` (`cosmos_rails.py` 132–138) would hide quota as "down." Map to `BROKE` with `http=` in detail until a quota kind exists. |
| **H** Spawn | Pin `@playwright/mcp@0.0.79`. `--browser chrome` (CLI help values; this job's `tools/list` used it). `--headless --isolated`. No `--caps` on the default worker. `browser_run_code_unsafe` **client-denied** (it is in the default 24). No `--extension`. No Keith daily profile. No `file://` gate URL (server blocks it unless `--allow-unrestricted-file-access`). |
| **I** Stage 6 (named, not claimed) | Playwright: `tools/list` JSON from the spawned 0.0.79 server **and** a `browser_snapshot` containing `tree_id=KMesh-COSMOS-live` or the live ledger head, via `http://127.0.0.1` KDash/serve — not `--help`. Firecrawl: HTTP 200 body with `success:true` and a `primaryId` (`arxiv:` / `doi:` / `pmid:`). Cursor-shaped `live/config/*_rail_probe.json`. Isolated `--selftest` is a green log. |

Makerhands STAGE3 WAVE A (satellite / MCP-host, Dispatcher `ApiRail` blocked) and this
ARCH (three Core rails in slice 1) **converge here**: ship the modules as
**cursor-shaped satellites**. Do not wait for Kernel attach to *write* them; do
not claim they are on the boot Dispatcher until Keith closes BACKLOG.

---

## Packet assertion (what this rank used)

| packet | on disk | used as |
|---|---|---|
| `docs/arch/meshadditions_ARCH.md` | stage-2 design under review | rubric + slice plan + §3 live table |
| `docs/MESH_ADDITIONS.md` | 20-row backlog; stage-2 verified column | row classes |
| `PLAYWRIGHT_MCP_HANDS.md` | tools, caps, RCE note, host `tools/list` claim | H1 names; allowlist |
| `FIRECRAWL_HANDS.md` | keyless vs Free, papers path, AGPL, unpublished IP cap | H4, papers REST vs MCP |
| `MCP_REFERENCE_SERVERS_HANDS.md` | Fetch HOLD (`uvx` missing); Memory/Sequential Thinking vs SEED | REJECT competing SEED |
| `OLLAMA_HANDS.md` / `GROQ_HANDS.md` | REST/CLI; Groq ≠ Grok; Mixtral dead; Llama-3 Free/Dev shutdown 2026-08-16 | HOLD slice 2 |
| `makerhands_STAGE3.md` | WAVE A satellite-first; Firecrawl D3; Kernel-attach block | prior rank to reconcile |
| `cosmos_cursor_rail.py` | additive `--gate` / `attach_to_kernel` REFUSED | the shape to copy |
| `live/config/cursor_rail_probe.json` | `gate=PASS` 2026-08-26T10:03:11-05, `kernel_attached=false` | satellite pattern is live |

No mid-run packet failure. Same-family `MESH_ADDITIONS_grok.md` is prior art, not
a second vote. Groq Llama-3 shutdown vs MESH row 2's older blurb remains a
**correction**, not a contest.

---

## Live-tree probes (this critique, 2026-08-26T10:06–10:07-05)

Host-side, this process. Secrets not printed. **Not a stage-6 pass.**

| probe | result | implication |
|---|---|---|
| `git rev-parse --short HEAD` | `56fa423` · `main` ahead 2 | Rank bound to this commit. |
| clock | `2026-08-26T10:06:12.588-05:00` | Next calendar day after the ARCH's 2026-08-25T23:09-05 probes. |
| Node / npm via `cmd /c` | `v24.18.0` / `11.16.0` | Meets engines `>=18`. |
| `live/config/` names | `api_token.txt`, `cursor_cosmos_key.txt`, `cursor_rail.json`, `cursor_rail_probe.json`, `install_key.bin`, `install_record.json` | **No** `groq_api_key.txt`, `firecrawl_api_key.txt`, `ollama_api_key.txt`. |
| env `GROQ_API_KEY` `FIRECRAWL_API_KEY` `OLLAMA_API_KEY` `ANTHROPIC_API_KEY` `BROWSER_USE_API_KEY` `MISTRAL_API_KEY` `DEEPSEEK_API_KEY` | all **ABSENT** | Matches ARCH §3.2. |
| py 3.14 imports | `browser_use` `ollama` `groq` `firecrawl` `aider` `playwright` `mcp` all **NO** | Slice 1 must stay stdlib + sidecar. |
| `ollama` / `aider` / `uvx` | `NOT_ON_PATH` | HOLD rows stay HOLD. |
| Chrome | `CHROME_EXISTS C:\Program Files\Google\Chrome\Application\chrome.exe` | Hands for `--browser chrome` / `discover_browser()`. Do not bake the path in Core. |
| `nvidia-smi` | `NVIDIA GeForce RTX 3070, 8192 MiB, 610.62` | 8 GiB; 30B-coder still will not fit. |
| Ollama `GET http://127.0.0.1:11434/api/version` | **UNREACHABLE** `WinError 10061` (Python `URLError`); PowerShell `WebException Unable to connect` | Default install paths still **MISSING**. HOLD. |
| Groq `GET https://api.groq.com/openai/v1/models` no key | **HTTP 401** `{"error":{"message":"Invalid API Key","type":"invalid_request_error","code":"invalid_api_key"}}` | Endpoint live; no `gsk_`. HOLD. |
| Firecrawl `POST /v2/scrape` keyless `url=https://docs.firecrawl.dev/introduction` `formats=["markdown"]` | **HTTP 200** `{"success":true,"data":{"markdown":"> ## Documentation Index\n>\n> Fetch the complete documentation index at: [/llms.txt]…` | Keyless scrape still answers **today**. WIRE verb. |
| Firecrawl `POST /v2/search` keyless `query=playwright mcp microsoft` `limit=2` | **HTTP 200** `success:true`; first hit `https://github.com/microsoft/playwright-mcp` title `Playwright MCP server` | Keyless search still answers. **Overflow** of SGH DOM, not ROUTING default. |
| Firecrawl `GET /v2/search/research/papers?query=Lindau+theorem+superluminal` | **HTTP 200** `primaryId":"arxiv:physics/0103087"` title `Thoughtful comments on 'Bessel beams and signal propagation'` | Same `arxiv:` id as ARCH §3.1. WIRE papers `--gate` value. |
| Playwright `cmd /c npx -y @playwright/mcp@0.0.79 --help` | rc 0 · `Usage: Playwright MCP [options]` · `--browser` values **`chrome, firefox, webkit, msedge`** (not `chromium`) · `--caps` `vision, pdf, devtools` · `--isolated` · `--headless` · `--image-responses allow\|omit` · file:// **blocked** unless `--allow-unrestricted-file-access` | Hands still here. ARCH spawn `--browser chromium` is **not** a listed value. |
| Playwright MCP stdio **this job** (not `--help`) | `cmd.exe /c npx -y @playwright/mcp@0.0.79 --headless --isolated --browser chrome --image-responses omit --console-level error` · JSON-RPC `initialize` + `notifications/initialized` + `tools/list` · **elapsed 1.69s rc 0** | **New bind.** `serverInfo.name=Playwright` `version=1.63.0-alpha-2026-08-05` `protocolVersion=2024-11-05` **tools count = 24**: `browser_close,browser_resize,browser_console_messages,browser_handle_dialog,browser_evaluate,browser_file_upload,browser_drop,browser_find,browser_fill_form,browser_press_key,browser_type,browser_navigate,browser_navigate_back,browser_network_requests,browser_network_request,browser_run_code_unsafe,browser_take_screenshot,browser_snapshot,browser_click,browser_drag,browser_hover,browser_select_option,browser_tabs,browser_wait_for`. Probe names ARCH named (`browser_navigate`, `browser_snapshot`) **are in the live list.** `browser_run_code_unsafe` is **core-default**, not behind `--caps`. |
| `Kernel.__init__` | composes paths, key, ledger, arbiter, mail, sched, registry, spend, validator, sessions, makers, convo, ITC; `self.ready = True`. **No** `register_node_rails`, **no** `attach_to_kernel`, **no** `Dispatcher`, **no** `self.adapters` | BACKLOG still true. |
| `cosmos_platform` | `run` = `subprocess.run` capture; `run_tree_killed` = `Popen(stdout, stderr)` + `communicate`; **no stdin pipe**; kill = `taskkill /T /F`; **zero** `CreateJobObject` in `cosmos/*.py` | ARCH H7 "Job-Object via platform" is **not** in the tree. MCP client must own Popen. |
| Registry `RAIL_TYPES` | `{CLI, API, DOM, CHAT, OTHER}` — **no MCP** | ARCH §4.1 `kind in {CLI, API, DOM, MCP}` is a contract error. Playwright = `DOM`. |
| `live/config/cursor_rail_probe.json` | `gate=PASS` `kernel_attached=false` `stage6.kind=satellite` `tree_id=KMesh-COSMOS-live` | The legal additive pattern while Kernel attach is BACKLOG. |

`browser_navigate` was **not** called. Chromium/Chrome first-download size and
time on first navigate: **UNKNOWN**. `tools/list` did not need a browser
(1.69s, no download stall). Probe ≠ dispatch capability (H3).

---

## Rubric scores (ARCH §1 applied to ARCH slice-1)

| id | score | bound reason |
|---|---|---|
| **H1 Hands** | **PASS** (this job) | Playwright action is MCP `tools/list` / `tools/call`, not `--help`. This critique bound 24 names including `browser_navigate` + `browser_snapshot`. Firecrawl scrape/search/papers HTTP 200 **today**. ARCH's WIRE *stamp* on `--help` was a classification miss (MED); the hand is real. |
| **H2 One authority** | **PASS** | Adapters / workers. n8n as scheduler REJECT. Sequential Thinking / Memory as competing SEED REJECT. Publish stays the fenced commit gateway. AGPL Firecrawl self-host stays a process. |
| **H3 Fail-closed + typed absence** | **CONTESTED → lock** | Typed UNREACHABLE for Ollama 10061 / Groq 401 is correct. Defects: (a) ARCH diagrams a Dispatcher that Kernel does not compose; (b) 429→`UNREACHABLE` then `RAIL_FALLBACK` hides quota; (c) `policy_rank` above dump-dom has no INTERACT/READ split; (d) `--help` WIRE vs named `--gate`. Locks E–G close these for stage 4. Registration of a satellite `--gate` module is **not** boot capability — probe JSON must say `kernel_attached=false` (cursor). |
| **H4 Nothing-that-can-run-out** | **PASS Playwright / FAIL Firecrawl-as-first-READ** | Playwright is local Apache-2.0, no vendor meter. Firecrawl keyless has an **unpublished** per-IP daily request **and** credit cap (`FIRECRAWL_HANDS.md`); 429 when either trips. Live 200s prove H1, not "cannot run out." Lock E: dump-dom first for READ; Firecrawl papers is $0 index, allowed as first *papers* link (different class). |
| **H5 Additive, no core edit** | **PASS** with packaging lock | No kernel/ledger/sched/service edit. `cosmos/` additive modules are allowed (cursor-rail lives there). `attach_to_kernel` must refuse authority compose. Three files whose only production hook is a function Kernel does not call are still **legal** if `--gate` is the honest stage-6 path (`stage6.kind=satellite`). |
| **H6 Vendor-plural, not a twin** | **PASS** | Playwright INTERACT ≠ dump-dom READ. Firecrawl is web-context / papers, not a Grok twin. Groq HOLD + "not Grok" is correct. SGH and GW remain one family. |
| **H7 Blast radius** | **PASS intent / UNKNOWN containment** | `--isolated`, loopback, secrets under `paths.config`, no Keith profile, no AGPL fold-in: PASS. Job-Object **absent**. `cmd.exe /c npx` is argv-to-cmd (not `shell=True`) but still cmd's parser. First Chromium download UNKNOWN. Stage 4 must tree-kill the Node+browser grandchildren (`taskkill /T` on the cmd pid), attempt-private `--output-dir`, deny `browser_run_code_unsafe`. |
| **H8 Improvement is not bloat** | **PASS with locks** | MCP client pays rent if Playwright `--gate` and later MCP servers reuse it. It is bloat if it is only a dead `adapters[link_id]`. Dump-dom stays (do not delete). No new pip in Core. Do not duplicate `cosmos_mcp.py` (server); client is a separate module, no edit to the server. ARCH §6 first-link swap would tax ROUTING.md — rejected (lock E). |
| **S1 Cost now** | **PASS** | Playwright $0. Firecrawl keyless $0 until the unpublished cap. No Keith mint required for slice 1. |
| **S2 Buildable on this machine today** | **PASS** | Node, Chrome, `cmd /c npx`, stdlib urllib. `uvx` / Ollama / Groq key / Python vendor pkgs ABSENT. |
| **S3 Runtime-binding path** | **PASS** (named) | ARCH §7 names the right values. `--help` is not the gate (ARCH already said so). This job's `tools/list` is still not the gate. |
| **S4 Fewest new resident processes** | **PASS** | Per-job stdio / HTTP. Ollama tray is slice 2, Keith-started. |
| **S5 Windows spawn truth** | **PASS measured / lock the argv** | `npm.ps1` execution-policy block is real. This job spawned `cmd.exe /c npx …` successfully. Prefer `node.exe` + packaged `cli.js` if stage 4 can resolve the path without cmd parsing; until then `cmd.exe` as argv[0] `/c` + argv list, never `shell=True`, never a `.bat`. |

---

## Three lenses (same family; recorded so consensus is not a blend)

### Lens 1 — safety / one-authority / fail-closed (adversarial)

Would **REJECT** slice-1 as three Dispatcher rails: `attach_to_kernel` without
`Kernel.__init__` is registered-but-dead; Firecrawl-as-first-READ fails H4;
`policy_rank` captures READ; Core MCP client is a second JSON-RPC stack the
boot Dispatcher never drives. Would **wire** Playwright as MCP-host config /
queue worker and Firecrawl papers as a urllib job.

**Kept:** H3/H4/H8 attacks on packaging and on ARCH §6. **Not kept as REJECT
of the three files:** cursor-api already shipped the satellite `--gate` shape
on this tree today; that is the legal additive path while Kernel attach is
BACKLOG, not a placation if the probe JSON states `kernel_attached=false`.

### Lens 2 — DOM-first / vendor-plural / Chapter-4

**Split the bundle.** Playwright INTERACT + Firecrawl **papers REST** are the
right capabilities now. Hosted Firecrawl MCP keyless **cannot** do papers
(tools are search/scrape/parse only) — Chapter-4 **is REST**. Scrape of a JS
app is not INTERACT. ARCH §6 search default vs `docs/ROUTING.md` SGH DOM is a
real conflict. dump-dom-only this cycle leaves "use a site" unclosed.
Ollama-first while 10061 is the probe is H3.

**Kept:** papers REST first `--gate`; ROUTING.md search stays; scrape ≠ click;
INTERACT hole is real; hosted MCP is not the papers path.

### Lens 3 — this-host packets (this job)

ARCH §3 table **still true** one day later: Playwright `--help` rc 0; Firecrawl
three keyless 200s with the same `arxiv:physics/0103087`; Groq 401; Ollama
10061; no maker keys in `live/config/`. **Upgraded:** Playwright `tools/list`
24 names in 1.69s with `--browser chrome`. **Corrected:** CLI `--browser`
values do not list `chromium`; `file://` is blocked by default;
`browser_run_code_unsafe` is in the default 24; platform has no stdin and no
Job-Object; Registry has no `MCP` kind.

---

## Consensus vs makerhands STAGE3

| item | makerhands s3 | meshadditions ARCH | this consensus |
|---|---|---|---|
| Playwright | WAVE A3 — MCP-host **or** COSMOS client | WIRE slice 1 Core rail | **Both, ordered:** Core satellite `--gate` module is this Motif row; MCP-host config on Claude/Grok/Cursor is complementary and is **not** a COSMOS stage-6 artifact. Pin **0.0.79**, not `--latest`. |
| Firecrawl | WAVE D3 (cap unpublished; ARCH designs, does not enable) | WIRE slice 1 | **Split:** papers REST **WIRE** (live `primaryId`, $0 index, no ROUTING conflict). scrape/search **OVERFLOW** of dump-dom / SGH DOM. Not a Core default READ/search rail. |
| MCP client | only if host cannot; WAVE B3 prefers host so Core does not grow clients | required slice 1 | **Required for COSMOS `--gate`.** Host config cannot write `live/config/playwright_rail_probe.json`. Client is a stdio helper, not a second scheduler. |
| Dispatcher `ApiRail` as first commit | REJECT this cycle (Kernel attach) | `attach_to_kernel` slice 1 | **CONVERGE on cursor satellite:** write the modules; refuse authority compose; do not edit Kernel; `--gate` records `kernel_attached=false`. |
| Ollama / Groq | WAVE C install/key | HOLD slice 2 | **HOLD.** 10061 / 401 still the honest probes 2026-08-26. |
| n8n / Zapier / OpenRouter `free` / Mixtral | REJECT | REJECT | **REJECT.** |

---

## Rank of ARCH design choices (lock these before stage 4)

| # | choice | ARCH | rank | lock |
|---|---|---|---|---|
| R1 | Slice-1 = MCP-client + playwright-dom + firecrawl-web | three `cosmos/*.py` + tests + `--gate` | **ACCEPT as files. REJECT as boot Dispatcher rails.** | Cursor satellite shape. `--gate` writes `live/config/<name>_rail_probe.json`. `kernel_attached=false` is a PASS predicate, not a miss. |
| R2 | Shared adapter contract copies CursorRail | probe / dispatch / register_* / attach_to_kernel / `--gate` / `--selftest` | **ACCEPT CursorRail, not CliRail/ApiRail.** | `ApiRail.probe` is always True — do not copy that. Cursor `probe` is cheap live GET. Playwright probe = `tools/list` names. Firecrawl probe = papers `primaryId` **or** scrape `success:true` (cheap vs crawl). `--selftest` fake transport; not the gate. |
| R3 | `kind in {CLI, API, DOM, MCP}` | §4.1 | **REJECT MCP as a Registry type.** | Registry `RAIL_TYPES` has no MCP (`BAD_TYPE`). Playwright `kind=DOM`. Firecrawl `kind=API`. MCP is the *transport* of the client helper. |
| R4 | `attach_to_kernel` additive, no kernel.py edit | H5 | **ACCEPT the refuse.** | Copy cursor: authority ledger → `REFUSED` unless `boot_compose=True` from Kernel.__init__ (BACKLOG). Isolated `--gate` ledger is the only legal compose this slice. |
| R5 | Playwright spawn `--browser chromium` | §4.2 B | **REJECT listed value.** | Help: `chrome, firefox, webkit, msedge`. This job: `--browser chrome` → 24 tools. Optional `--executable-path` from `cosmos_browser.discover_browser()` — **no drive literal** in the module. Pin package `0.0.79`. |
| R6 | Playwright `policy_rank` above dump-dom for INTERACT | §4.2 B | **REJECT as Registry.route.** | No job class. Distinct `dst` (e.g. `core->interact` vs dump-dom READ) **or** caller selects `link_id`. dump-dom stays the cheap READ. Do not delete `cosmos_browser`. |
| R7 | Dispatch `{url, steps?}` → navigate then snapshot | §4.2 B | **ACCEPT.** | Click/type only when `steps` present. Allowlist tool names. **Deny** `browser_run_code_unsafe` unless the job spec opts in (it is in the default 24 — server will list it; client must refuse `tools/call`). |
| R8 | Gate URL `file://` or localhost KDash | §4.2 B / §7 | **REJECT file:// as default.** | Server: navigation to `file://` blocked unless `--allow-unrestricted-file-access` (H7: do not open that). Gate = `http://127.0.0.1` KDash / `serve` page containing `tree_id`. |
| R9 | Firecrawl verbs scrape / search / papers; no `limit` on papers | §4.2 C | **ACCEPT.** | Papers path is GET `/v2/search/research/papers?query=` — not search category `research`. Hosted MCP keyless cannot do papers. Slice 1 is REST urllib, not Firecrawl MCP. |
| R10 | Firecrawl `metered_usd=0.0`; missing key → keyless not UNREACHABLE | §4.2 C / §5 | **ACCEPT keyless default. REJECT 429→UNREACHABLE.** | 402/429 → `BROKE` + `http=` (no `RAIL_FALLBACK`). Crawl/map without key → `AUTH_REQUIRED`. Spend-gate still ledgers `RAIL_DISPATCH`/`RAIL_RESULT` at $0 on the **isolated** `--gate` ledger, not authority, until Kernel compose. Smart Upgrade off. |
| R11 | ARCH §6 routing table as Dispatcher pick | §6 | **REJECT search + known-URL first-links.** | ROUTING.md: search / broad sweep = SGH DOM. Known-URL READ = dump-dom first, Firecrawl scrape overflow. **Use a site** = `playwright-dom` when the satellite is live. **Chapter-4 papers** = `firecrawl-web` papers (additive). Coding unchanged. Dead Playwright = UNREACHABLE, never a silent Groq/Firecrawl "looked at the page." |
| R12 | MCP client: `cmd.exe /c npx`, own Popen if platform cannot pipe | §4.2 A | **ACCEPT own Popen. Lock argv.** | `cosmos_platform` has no stdin and is not a Job Object. Client: argv list, `stdin=PIPE`, newline JSON-RPC `initialize` → `notifications/initialized` → `tools/list` / `tools/call`, timeout + `taskkill /T` on the cmd pid (grandchildren). `CREATE_NO_WINDOW`. No prompt interpolation through cmd. Prefer `node.exe` + `cli.js` if resolvable. |
| R13 | Ollama / Groq slice 2 HOLD | §4.3 | **ACCEPT.** | Do not open `cosmos_ollama_rail.py` / `cosmos_groq_rail.py` in slice 1. Contracts in ARCH §4.3 stand (native `/api/chat` when `num_ctx` matters; Groq default `openai/gpt-oss-20b`; Mixtral/Llama-3 Free/Dev IDs dead). |
| R14 | browser-use / Aider / MCP Fetch slice 3 | §4.4 | **ACCEPT HOLD.** | `uvx` ABSENT; `aider` ABSENT; browser-use pkg NO; telemetry `ANONYMIZED_TELEMETRY=false` if ever wired; Cloud `bu_` **do not wire**. |
| R15 | Out: n8n, Zapier, OpenRouter rotating `free`, LiteLLM, AGPL fold-in, `--extension`, bats | §4.5 | **ACCEPT REJECT.** | OpenRouter named-model pin only if Keith asks. |
| R16 | Tests: fake stdio / fake HTTP, no network in pytest | §8 | **ACCEPT.** | Live `--gate` is CLI, like cursor. pytest must not mint keys or download browsers as a green log. |

---

## HIGH (block a false-green stage 4 / 6)

### H1 — Dispatcher-on-boot is not the live path; satellite `--gate` is

- **File:** `cosmos_kernel.py` 37–130; `cosmos_cursor_rail.py` 552–566;
  `docs/BACKLOG.md` "Kernel.__init__ never calls register_node_rails";
  `live/config/cursor_rail_probe.json` `kernel_attached: false`.
- **ARCH:** diagram "Dispatcher (existing) → adapters[link_id]" + H5
  `attach_to_kernel`.
- **Fact:** production Kernel has no `adapters` and never calls attach.
  `attach_to_kernel` **raises REFUSED** on the authority ledger. The live
  `cosmos_dispatcher_daemon` is a tag-routed agent daemon, not
  `cosmos_rails.Dispatcher`.
- **Impact:** a green `register_*` without Kernel compose is the false-green
  makerhands H2 already named. Cursor closed it by making `--gate` PASS
  *require* attach-refusal + `kernel_attached=false`.
- **Fix:** R1 + R4. Slice-1 `--gate` copies that predicate. Do not edit Kernel.

### H2 — ARCH §6 would demote DOM-first and hide a cap as "first live link"

- **File:** `docs/ROUTING.md` search default = SGH DOM; FINAL_ARCHITECTURE
  decision 6; `FIRECRAWL_HANDS.md` unpublished per-IP cap; ARCH §6 table.
- **Fact:** Firecrawl keyless scrape/search 200s today. They can 429 tomorrow
  at an unpublished threshold. dump-dom and SGH DOM cannot run out of that cap.
- **Impact:** putting `firecrawl-web` first for "read a known URL" and "web
  search" is a ROUTING.md change smuggled into an adapter ARCH. H4 fail if
  treated as unmetered default.
- **Fix:** R11. Papers first-link is allowed (no ROUTING row; live `primaryId`).

### H3 — `policy_rank` above dump-dom has nowhere to mean "INTERACT only"

- **File:** `cosmos_registry.py` `route()` sorts `(-policy_rank, DOM-before-API)`
  with **no job class**. `Dispatcher.dispatch(src, dst, payload)` has no
  INTERACT vs READ.
- **Impact:** when both rails ever attach, cheap READ becomes a long-lived
  Chromium MCP session. Inverse of "DOM dead must not quietly become API."
- **Fix:** R6.

### H4 — 429→`UNREACHABLE` is a silent fallback once a Dispatcher exists

- **File:** ARCH §4.1; `cosmos_rails.py` 132–138 `RAIL_FALLBACK` on
  `UNREACHABLE` / `SESSION_EXPIRED` / `AUTH_REQUIRED`.
- **Impact:** quota looks like vendor-down; next link runs; spend-gate never
  saw a dollar. H3 "no silent fallback."
- **Fix:** R10. `BROKE` + `http=429` (Dispatcher does not fallback on `BROKE`).

### H5 — Playwright WIRE on `--help` was the wrong stamp; `tools/list` now exists

- **ARCH §3.1 / row 3:** WIRE because `--help` rc 0. ARCH §7 already says
  `--help` is not the gate. HANDS.md had a host `tools/list`; the ARCH did not
  quote it for the stamp.
- **This job:** 24-tool `tools/list` in 1.69s, names bound.
- **Impact:** stage 4 must probe `tools/list`, not `--help`. First
  `browser_navigate` may still download a browser — **UNKNOWN** size/time —
  so probe-OK is not dispatch-OK (H3). `--gate` that snapshots must timeout
  that download as typed `UNREACHABLE`, not hang.

---

## MED

1. **`--browser chromium` vs help `chrome`.** This job used `chrome`. Stage 4
   must not copy the ARCH argv blindly.
2. **`file://` gate.** Help text: file:// navigation blocked by default.
   Localhost HTTP only.
3. **`browser_run_code_unsafe` is in the default 24.** Client allowlist is the
   only control (no `--caps` hide). Deny by default.
4. **`--caps` conflict.** ARCH default none; PLAYWRIGHT_HANDS / makerhands A3
   suggested `network,storage`. Lock: **none** on the default worker (smaller
   schema, matches ARCH). Opt-in per job.
5. **Platform "NO SHELL, EVER" vs `cmd.exe /c npx`.** Measured necessary on
   this host (`npx.ps1`). Argv `[cmd.exe, /c, npx, …]` is not `shell=True`.
   Still a quoting surface — keep args as separate tokens; never fold the
   prompt into the cmd line (the prompt is JSON-RPC stdin).
6. **Job-Object named in H7 / FINAL_ARCHITECTURE decision 6 is not in
   `cosmos_platform`.** `taskkill /T` is the live kill. Do not claim
   Job-Object in slice-1 docs. Containment UNKNOWN beyond tree-kill.
7. **Two "Dispatchers."** `cosmos_rails.Dispatcher` (tests + cursor isolated
   `--gate`) ≠ `cosmos_dispatcher_daemon` (agent jobs). ARCH prose must not
   conflate them. Stage 4 comments: "isolated `--gate` Dispatcher," not
   "the live daemon."
8. **Hosted Firecrawl MCP is not papers.** MESH_ADDITIONS_grok "keyless hosted
   MCP first" would drop `arxiv:` / `doi:` / `pmid:`. Slice 1 REST is correct.
9. **Playwright is a second DOM surface, not a drop-in `ChromeDriver`.**
   `cosmos_browser.py` promised INTERACT "behind the SAME Driver protocol."
   Slice 1 does **not** have to implement that protocol; it must not pretend
   it did. dump-dom stays.
10. **Cursor `AUTH_REQUIRED` is not a CursorRailError kind** (401→UNREACHABLE).
    Firecrawl crawl-without-key **does** want `AUTH_REQUIRED`. Do not blindly
    copy Cursor's HTTP map.

---

## LOW

- Firecrawl papers `limit` → 400 `unrecognized_keys` is a useful correction;
  keep it.
- Mixtral / Llama-3 Free/Dev / OpenRouter rotating `free` REJECT stands.
- `gh` on PATH is a host tool, not a new rail (makerhands WAVE A2, not this row).
- dump-dom is also not Kernel-attached; "keep as cheap READ" is the floor
  module, not a live `Registry` row today.
- GPU CIM 32-bit wrap vs nvidia-smi 8 GiB: ARCH was right; do not re-litigate.

---

## UNKNOWN (typed; stage 4 must not guess)

- Chromium/Chrome-for-Playwright **first `browser_navigate` download** bytes,
  minutes, and whether the npm cache already has the browser. `tools/list`
  did not need it.
- Firecrawl keyless per-IP daily request/credit **numbers** (unpublished
  until 429). Remaining quota on this IP: UNKNOWN.
- Whether `~/.grok/`, Claude Code, or Cursor already have Playwright MCP
  configured (makerhands U11).
- Papers `inspect` / `read` / `similar` on this host (only search was probed,
  twice: ARCH and this job, same `arxiv:physics/0103087`).
- Whether `--browser chromium` is accepted as an alias (help does not list
  it; not re-probed).
- Whether `node.exe` + `@playwright/mcp` `cli.js` can drop `cmd /c` entirely.
- Kernel attach schedule (BACKLOG, Keith).
- Groq org live model list / RPM (no `gsk_`).
- Ollama `/api/tags` after install (daemon down).
- `uv` / `uvx` (Fetch HOLD).
- Whether dump-dom HTML and Firecrawl scrape markdown of the same JS SPA are
  equivalent READ quality.

---

## CONTESTED — one line each to Keith (no third model)

Motif: converge, or mark CONTESTED. These are the items this rank **cannot**
lock from canon / live packets:

1. **Close Kernel attach this cycle?** BACKLOG: `Kernel.__init__` never calls
   `register_node_rails`. Slice-1 will not put rails on `serve` until you say
   so. Cursor `--gate` already PASSed as `stage6.kind=satellite` with attach
   refused.
2. **Give coding hosts Playwright MCP now** (Claude Code / Grok / Cursor
   `.mcp.json`, pin `0.0.79`) **in parallel** with the Core satellite module?
   Complementary; not a COSMOS stage-6 artifact; F5 quota is scarce (ROUTING
   snapshot). Your call whether COW drops those host configs.

Everything else in the lock table is decided from rubric + packets + existing
cursor pattern. Same-family process still owes gem-api/oa-api a pass; that is
a **family hole**, not a design contest.

---

## What this stage did **not** do

- Did not edit `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` /
  `cosmos_service`.
- Did not write slice-1 code (`cosmos_mcp_client.py`,
  `cosmos_playwright_rail.py`, `cosmos_firecrawl_rail.py`). That is stage 4
  under the locks above. Not stage 6.
- Did not `browser_navigate` / snapshot KDash (no Chromium-download claim).
- Did not treat Firecrawl HTTP 200 or Playwright `tools/list` as COSMOS
  stage 6 (no rail, no `*_rail_probe.json` for these link_ids).
- Did not install Ollama, mint Groq/Firecrawl keys, or `pip install` into Core.
- Did not resolve Kernel attach (BACKLOG).
- Did not obtain a different-family (gem-api / oa-api) critique — **owed**.
- Did not change `docs/ROUTING.md` or `docs/MOTIF_TRACKER.md` (proposals
  below; COW files tracker).

---

## Proposed tracker line (COW files)

| deliverable | current stage (HONEST) | artifact | next stage |
|---|---|---|---|
| **Mesh additions** (Ollama/Groq/Playwright/…) | 3 critique/rank (G46 `meshadditions_STAGE3.md` 2026-08-26) — UNVETTED (same family as ARCH); **CONVERGE with locks** | `docs/MESH_ADDITIONS.md`, `docs/arch/meshadditions_ARCH.md`, `docs/critique/meshadditions_STAGE3.md` | 4 code slice-1 under STAGE3 locks: satellite `--gate` modules `cosmos_mcp_client` + `playwright-dom` + `firecrawl-web` (papers `--gate` first). Not Kernel attach. Not ROUTING.md search swap. Not stage 6. Different-family (gem/oa) still owed on the ARCH. |

---

## Next Motif stage

**Stage 4 BUILD** (G46 / Cursor / F5 per competency — not this critique):
code slice-1 on a branch / as additive untracked modules, **under R1–R16**.
Each of the three files must **run**: `--selftest` fake transport (pytest)
and a live `--gate` that writes a probe JSON quoting a live field.

**Stage 5** different-family review of the *build* vs this document + the ARCH
as amended by the locks (is this the thing we decided).

**Stage 6** is the `--gate` JSON in `live/config/` with a value only the live
tree / vendor can emit — `arxiv:` `primaryId` and/or a snapshot containing
`tree_id=KMesh-COSMOS-live` — plus `kernel_attached=false` until BACKLOG
closes. An exit code is not that value.
