# COSMOS INDEX — living projection

> Rebuildable. Sources are truth; this file is a cache. Never hand-edit.
> Generated `2026-08-28T14:21:29-05:00` by `cosmos-index` pid=24328 schema=`cosmos-index/1`.
> Root: `V:\A\Ai\COSMOS\live` · Repo: `V:\A\Ai\COSMOS`
> Sources: `docs/MOTIF_TRACKER.md` · `docs/BACKLOG.md` · `docs/AGENT_BRIEF.md` (DHx) · `builds/*/FEATURES_KEITH.md` · `live/state/collector/index.jsonl` · `live/logs/*heartbeat*.json` · ledger `LINK_REGISTERED`/`PROBE_RESULT`/`RAIL_RESULT`.
> Section C lists an item ONLY when bound to an emitted artifact (heartbeat last_run/mtime, ledger seq, or HTTP 200). Motif stage 6 is the only 'complete' for a build (0 passed).
> Refresh: collector each poll, or `py -3.14 cosmos\cosmos_index.py --root <live> --once` (light clock `COSMOS Index` every 1 min).

## A. TOOLS/APPS BEING BUILT

Every MOTIF_TRACKER deliverable that has **not** passed the runtime-binding gate.

| name | motif stage | builder agent | artifact path | last update |
|---|---|---|---|---|
| cDeck | 4 code (first-pass, build3, 8 files) — UNVETTED | G46 | builds/cdeck | 2026-08-27T02:04:13-05:00 |
| CVM (cosmos-android) | 4 code (fanout scaffold) — UNVETTED | G46 | Ai\tmp\cosmos-android | 2026-08-27T17:30:07-05:00 |
| CDM | 4 code (fanout scaffold) — UNVETTED | G46 | builds/cdm | 2026-08-27T02:04:12-05:00 |
| gbridge (T1 sync tool) | 4 code (wrong-model draft) — UNVETTED; research done | GEM | builds/gbridge, docs/T1_ARCH.md | 2026-08-28T09:37:06-05:00 |
| cosmos_collector | 4 code (G46 building) — UNVETTED | G46 | (building) | 2026-08-28T09:36:52-05:00 |
| cosmos_dispatch | 2/4 — COW codes in-session | G46 | (owed) | 2026-08-28T09:36:28-05:00 |
| Maker-hands sweep (GitHub/GitLab + 12 makers) | 3 critique/rank (G46 `makerhands_STAGE3.md` 2026-08-25) — UNVETTED (same family as HANDS scouts); research packet on disk | G46 | docs/research/*_HANDS.md, docs/critique/makerhands_STAGE3.md | 2026-08-27T02:04:22-05:00 |
| Mesh additions (Ollama/Groq/Playwright/…) | 2 arch (G46; hands verified this host — Playwright `--help` + Firecrawl keyless 200s + Groq 401 + Ollama 10061) — UNVETTED | G46 | docs/MESH_ADDITIONS.md, docs/arch/meshadditions_ARCH.md | 2026-08-27T02:04:12-05:00 |
| Cursor lane | 4 code (CursorRail `cursor-api` + live spec; `--gate` live `/v1/me` 200 `apiKeyName=Cursor COSMOS 2` bound 2026-08-25T23:04:14-05:00) — UNVETTED; Kernel.__init… | G46 | live/config, docs/CURSOR_LANE.md, cosmos/cosmos_cursor_rail.py | 2026-08-27T05:22:35-05:00 |
| COSMOS runner (own queue) | 4 (G46 standup) — verify heartbeat | G46 | (standup ran) | 2026-08-27T12:43:04-05:00 |
| runtime binding — ALL | 0 | G46 | — | 2026-08-27T02:04:13-05:00 |

## B. NEW FEATURES REQUESTED

From `builds/*/FEATURES_KEITH.md` and open/checked BACKLOG items. `shipped` here still requires a C-row proof.

| feature | target tool | status | source |
|---|---|---|---|
| CREATE box | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Spend control | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Jukebox | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Node map | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Live status feed | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Batteries | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Caps & speeds | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Every KDash feature | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| New functional controls | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Integrated CVM control | cDeck | in-build | builds\cdeck\FEATURES_KEITH.md |
| Clock cadence rubric | Watchdog2 | shipped | docs/BACKLOG.md |
| Watchdog2 | Watchdog2 | shipped | docs/BACKLOG.md |
| Windows clocks | Watchdog2 | shipped | docs/BACKLOG.md |
| Maker + gcloud sweeps | COSMOS | in-build | docs/BACKLOG.md |
| Mesh additions | Mesh additions | in-build | docs/BACKLOG.md |
| cosmos_dispatch / cosmos_collector | collector | in-build | docs/BACKLOG.md |
| Constant session-backlog agent | COSMOS | in-build | docs/BACKLOG.md |
| COSMOS-own clocks (a dozen+) | Watchdog2 | shipped | docs/BACKLOG.md |
| COSMOS_INDEX | COSMOS_INDEX | shipped | docs/BACKLOG.md |
| AUTO-RESESSION | session | requested | docs/BACKLOG.md |
| Resume gate | session | requested | docs/BACKLOG.md |
| PAUSE protocol | PAUSE | shipped | docs/BACKLOG.md |
| Wire WD2 → WISHLIST | COSMOS | in-build | docs/BACKLOG.md |
| `cosmos.py serve` not up on real root `:8770` (only trylive:8791). | COSMOS Core | requested | docs/BACKLOG.md |
| `Kernel.__init__` never calls `register_node_rails` | COSMOS Core | requested | docs/BACKLOG.md |
| Tool migration: 135 UNDECIDED / 8 REPLACED | migrate | requested | docs/BACKLOG.md |

## C. IMPLEMENTED / LIVE

Bound artifacts only. Daemons quote heartbeat `last_run` and file mtime. Rails quote ledger seq. No Motif build is listed unless stage 6 passed.

| item | kind | proof | last update |
|---|---|---|---|
| backup_clock | daemon | STALE age_s=12087.0 · heartbeat last_run=2026-08-28T11:00:03-05:00 file_mtime=2026-08-28T11:00:03-05:00 pid=10456 polls=0 tick=once | 2026-08-28T11:00:03-05:00 |
| cdeck_feed | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:29-05:00 file_mtime=2026-08-28T14:21:29-05:00 pid=37392 polls=173922 tick=once | 2026-08-28T14:21:29-05:00 |
| collector | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:25-05:00 file_mtime=2026-08-28T14:21:25-05:00 pid=24328 polls=3845 tick=poll | 2026-08-28T14:21:25-05:00 |
| cosmos_index | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:29-05:00 file_mtime=2026-08-28T14:21:29-05:00 pid=24328 polls=None tick=rebuild | 2026-08-28T14:21:29-05:00 |
| cosmos_pool_heartbeat | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:21-05:00 file_mtime=2026-08-28T14:21:21-05:00 pid=39336 polls=9076 tick=supervise | 2026-08-28T14:21:21-05:00 |
| cosmos_runner | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:15-05:00 file_mtime=2026-08-28T14:21:15-05:00 pid=37752 polls=3310 tick=idle | 2026-08-28T14:21:15-05:00 |
| cosmos_runner.slot0_heartbeat | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:15-05:00 file_mtime=2026-08-28T14:21:15-05:00 pid=33732 polls=4692 tick=idle | 2026-08-28T14:21:15-05:00 |
| cosmos_runner.slot1_heartbeat | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:22-05:00 file_mtime=2026-08-28T14:21:22-05:00 pid=38140 polls=1209 tick=idle | 2026-08-28T14:21:22-05:00 |
| cosmos_runner.slot2_heartbeat | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:15-05:00 file_mtime=2026-08-28T14:21:15-05:00 pid=40384 polls=6805 tick=idle | 2026-08-28T14:21:15-05:00 |
| cosmos_runner.slot4_heartbeat | daemon | STALE age_s=83941.0 · heartbeat last_run=2026-08-27T15:02:29-05:00 file_mtime=2026-08-27T15:02:29-05:00 pid=37216 polls=1675 tick=idle | 2026-08-27T15:02:29-05:00 |
| cosmos_runner.slotfast_heartbeat | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:16-05:00 file_mtime=2026-08-28T14:21:16-05:00 pid=5724 polls=631 tick=idle | 2026-08-28T14:21:16-05:00 |
| cosmos_runner_heartbeat.slot2 | daemon | STALE age_s=94883.0 · heartbeat last_run=2026-08-27T12:00:07-05:00 file_mtime=2026-08-27T12:00:07-05:00 pid=38656 polls=1352 tick=error | 2026-08-27T12:00:07-05:00 |
| cosmos_runner_heartbeat.slot3 | daemon | STALE age_s=69274.0 · heartbeat last_run=2026-08-27T19:06:56-05:00 file_mtime=2026-08-27T19:06:56-05:00 pid=38184 polls=7483 tick=idle | 2026-08-27T19:06:56-05:00 |
| cvm_clock_heartbeat | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:28-05:00 file_mtime=2026-08-28T14:21:28-05:00 pid=23444 polls=67773 tick=loop | 2026-08-28T14:21:28-05:00 |
| cvm_dt_clock_heartbeat | daemon | STALE age_s=111312.0 · heartbeat last_run=2026-08-27T07:26:18-05:00 file_mtime=2026-08-27T07:26:18-05:00 pid=5404 polls=0 tick=refused | 2026-08-27T07:26:18-05:00 |
| cvm_dt_voice_heartbeat | daemon | STALE age_s=102147.0 · heartbeat last_run=2026-08-27T09:59:03-05:00 file_mtime=2026-08-27T09:59:03-05:00 pid=14444 polls=1 tick=refused | 2026-08-27T09:59:03-05:00 |
| dispatcher | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:28-05:00 file_mtime=2026-08-28T14:21:28-05:00 pid=12020 polls=27240 tick=idle | 2026-08-28T14:21:28-05:00 |
| drive_meter | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:00-05:00 file_mtime=2026-08-28T14:21:00-05:00 pid=19124 polls=0 tick=once | 2026-08-28T14:21:00-05:00 |
| gem_worker_heartbeat | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:26-05:00 file_mtime=2026-08-28T14:21:26-05:00 pid=30644 polls=9090 tick=idle | 2026-08-28T14:21:26-05:00 |
| grok_worker_heartbeat | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:26-05:00 file_mtime=2026-08-28T14:21:26-05:00 pid=4928 polls=9090 tick=idle | 2026-08-28T14:21:26-05:00 |
| health_clock | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:28-05:00 file_mtime=2026-08-28T14:21:28-05:00 pid=10372 polls=60049 tick=once | 2026-08-28T14:21:28-05:00 |
| ledger_verify | daemon | LIVE · heartbeat last_run=2026-08-28T14:20:00-05:00 file_mtime=2026-08-28T14:20:00-05:00 pid=10456 polls=0 tick=once | 2026-08-28T14:20:00-05:00 |
| mesh_discovery | daemon | LIVE · heartbeat last_run=2026-08-28T14:06:02-05:00 file_mtime=2026-08-28T14:06:02-05:00 pid=21988 polls=None tick=done | 2026-08-28T14:06:02-05:00 |
| motif_driver | daemon | LIVE · heartbeat last_run=2026-08-28T14:15:00-05:00 file_mtime=2026-08-28T14:15:00-05:00 pid=33604 polls=None tick=once | 2026-08-28T14:15:00-05:00 |
| rails_prober | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:03-05:00 file_mtime=2026-08-28T14:21:03-05:00 pid=22308 polls=0 tick=once | 2026-08-28T14:21:03-05:00 |
| spend_meter | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:01-05:00 file_mtime=2026-08-28T14:21:01-05:00 pid=40456 polls=0 tick=once | 2026-08-28T14:21:01-05:00 |
| watchdog2 | daemon | LIVE · heartbeat last_run=2026-08-28T14:21:18-05:00 file_mtime=2026-08-28T14:21:18-05:00 pid=26560 polls=9022 tick=assigned | 2026-08-28T14:21:18-05:00 |
| claude-cli | rail | ledger LINK_REGISTERED seq=356 · PROBE_RESULT ok=True seq=357 | 2026-08-27T09:49:54-05:00 |
| cursor-api | rail | ledger LINK_REGISTERED seq=321 | 2026-08-26T11:06:53-05:00 |
| gem-api | rail | ledger LINK_REGISTERED seq=287 · PROBE_RESULT ok=True seq=493 · RAIL_RESULT ok=True seq=478 | 2026-08-28T09:36:51-05:00 |
| gw-api | rail | ledger LINK_REGISTERED seq=289 · PROBE_RESULT ok=True seq=187 | 2026-08-25T17:38:02-05:00 |
| oa-api | rail | ledger LINK_REGISTERED seq=291 · PROBE_RESULT ok=True seq=494 · RAIL_RESULT ok=True seq=420 | 2026-08-27T16:42:42-05:00 |
| sgh-api | rail | ledger LINK_REGISTERED seq=285 · PROBE_RESULT ok=True seq=492 · RAIL_RESULT ok=True seq=307 | 2026-08-25T23:55:27-05:00 |
| PAUSE protocol | protocol | flag V:\A\Ai\COSMOS\live\state\control\PAUSE.flag state=RUNNING mode=resumed file_mtime=2026-08-28T09:59:42-05:00 | 2026-08-27T01:00-05 |
| cursor_verify | http | HTTP 200 · `GET https://api.cursor.com/v1/me` / / Auth / `Authorization: Bearer <key>` / / **HTTP** / **200** / / Date header / `W… · V:\Ai\_queue\cursor_verif… | 2026-08-25T21:38:52-05:00 |
| apk_http | http | HTTP 200 · 127.0.0.1 - - [24/Aug/2026 09:15:10] "HEAD /cosmos-voice.apk HTTP/1.1" 200 - · V:\Ai\_queue\_lanes\pb\logs\apk_http.out | 2026-08-24T09:15:10-05:00 |

Collector index rows scanned: 5302. DHx assignment markers: 166.

