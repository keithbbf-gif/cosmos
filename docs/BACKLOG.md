# BACKLOG — open items (Watchdog2 scans this; COW logs here as items surface)

**Rule:** COSMOS never idles > **15s** (Keith 2026-08-25). The 15s **Activity Clock** / Watchdog2
(`cosmos_watchdog2.py`) does NOT invent a rubric — it DRIVES the canonized MOTIF route + step-8
ITERATE. It scans this + `docs/WISHLIST.md` (open wishes, MOTIF stage-1) + MOTIF_TRACKER + DHx open assignments + the runner ledger every 15s and
DROPS an agent for any open item with no in-flight worker. COW appends new requests here the
instant they surface. **PAUSE** (`docs/PAUSE_PROTOCOL.md`, flag `live\state\control\PAUSE.flag`)
is the formal stop: while the flag exists the clock drops NO agent (in-flight still finishes).
COSMOS uses its **OWN** clocks — **no BTS**.

## Stopping point (2026-09-05T19:55 CCr)
Keith: square git, then stop COSMOS this pass. Open Sessions LIVE on `:8770`. GFO sit is BUrestart only. Route still has open rows below — they wait for the next motion. HOLD is not on disk.

## Open (as of 2026-08-25 evening)
- [ ] **ChatBot phone DEFINE (Keith 2026-09-07)** — frozen `work_orders/ccr/DEFINE_CHATBOT_PHONE.md` (**Freemium** iterate). RESEARCH next (DOM rails): Freemium chat apps vs trial/crippleware, named OpenRouter `:free` roster (low latency), desktop funnel + where Premium sits. Do not invent a price. Do not start Android BUILD until returns on disk. Do not ship `cosmos-voice.apk`. Do not publish. Do not use rotator. · WATCHDOG2 ASSIGNED 2026-09-07T15:26:29.195286-05:00 cm/g46_grok_backlog_chatbot_phone_define_keith_2_408c87d8__t1800.py
- [x] **Origin-47 harvest / GitHub hitch (Keith 2026-09-05)** — CCr read the 47 origin-only commits, applied drops/docs, tabled stale daemon (`work_orders/ccr/ORIGIN47_DISPOSITION.md`; harvest `bae0372`; ours-merge `087a3b5`). APK stored as **draft** (`kdash/ANDROID_VOICE_DRAFT.md`); untracked + `*.apk` gitignored; files stay on disk. **GitHub `main` published** `59e2711` (`commit-tree` of `56cf49a` onto `14addfc`; no 164 MB apk). Do not merge PRs #30/#32/#36/#37/#38. Do not force-push local `main` (apk blob still in local unique commits). Do not `filter-branch` on Windows.
- [x] **Cowork→OpenWork migrator plugin** — **CLOSED 2026-09-05T18:38:01 CCr G46; REBOUND 2026-09-05T19:11:16 onto COSMOS 2.** Pack left ingested (666 `ses_cow_*`). Live GFO workspace_id **`ws_726c64a2afa5`** path **`V:\OPENWORK\COSMOS 2`**. `opencode.db` 2026-09-05T19:13 host peek: `n_cow=666` `cow_by_dir=V:/OPENWORK/COSMOS 2` `cow_by_ws=ws_726c64a2afa5`; leftover Chat sessions **5** untouched (`ses_f8d498f9effezSDQoNrtAhum6Q` gentle-falcon among them). Sidebar `session_group_states` rows on **both** `ws_12669390bcf4` (old Streams, kept) and `ws_726c64a2afa5` (7 groups / 666 assignments copied). OpenWork JSON `selectedId=ws_726c64a2afa5`; `workspaces[]` still only lists old COSMOS at `V:\Streams\openwork` (OpenWork array lag — do not invent a row). Proof: `V:\OPENWORK\COSMOS 2\cm\cow_migrator_rebind.json`. Backups: `opencode.db.bak_before_gfo_rebind_20260905T191116`, `runtime.sqlite.bak_before_gfo_rebind_20260905T191116`. Ctrl+R in the COSMOS 2 window. Do not re-ingest. Not CORE. First close 18:38:01 was Streams `ws_12669390bcf4`. · WATCHDOG2 ASSIGNED 2026-09-05T18:28:39.266565-05:00 cm/g46_grok_backlog_cowork_openwork_migrator_plu_841a38e4__t1800.py
- [ ] **Session tools suite (Keith 2026-09-05)** — the Cowork→OpenWork migrator is the **seed**, not the product. Full suite: crashed systems, all AIs and installs, load / convert / migrate / diff / check / anonymize. Pack TOML already on disk. Plugin rebind (if proven) does not close this. **Open Sessions product route is LIVE** on Core `:8770` GET `/api/v1/recents` 200 n=200 (bounce 2026-09-05T19:17, proof `live/logs/recents_bounce_prove.json`). Suite verbs beyond list/open still open. CCr builds; ORC does not recode. Research: `docs/research/SESSION_TOOLS.md`. Stage-2 ARCH next. Not CORE kernel. Not Legal mining from this TUI.
- [x] **Clock cadence rubric** — encoded in `docs/ORCHESTRATION.md` (FAST 0.5s–few-s daemon /
      NO-IDLE 15s / SLOW 1 min schtasks / MOTIF 15m / hourly / 4× daily backup / 5m verify).
- [x] **Watchdog2** — `cosmos_watchdog2.py` 15s Activity Clock; honors PAUSE `mode` (hold /
      resume_gate + auto_resume_at); queue=`live\queue`; schtasks `COSMOS Watchdog2`.
- [x] **Stage-5 critiques consumer** — `COSMOS CritConsumer` 1-min + Logon registered
      2026-09-02; heartbeat `RUNNING` (drain). A live GEM/OA body written back is still
      the remaining runtime-binding proof for *critiques*, not the consumer clock.
- [x] **Windows clocks** — 26 CLOCKS; 1-min + Logon registered 2026-09-02 (`c2 43/43`
      runtime-bind GATE_CLOSED). CVM DT Clock task now exists (heartbeat may still REFUSE).
- [ ] **CLOCKS collapse — one pulse, one runner, calendar** — 26 resident · WATCHDOG2 ASSIGNED 2026-09-04T11:30:02.013157-05:00 cm/g46_grok_backlog_clocks_collapse_one_pulse_on_b71e6a29__t1800.py
      pythonw for small different jobs is the wrong shape. Target: one 15s
      HOLD-aware Pulse + `cosmos_pool` as the only `claim_next` + `--once`
      schtasks for backup/verify/meters/hourly. Optional third process:
      Health `--supervise` until Pulse owns Core restart. Coupling + order:
      `docs/ORCHESTRATION.md` **CLOCKS collapse**. Do not shrink `CLOCKS` or
      `/delete` Logon until that order; leftover Logon respawns old `--loop`
      after reboot. HOLD stays. Core `:8770` stays up.
- [ ] **Maker + gcloud sweeps** — stage-3 rank landed (`docs/critique/makerhands_STAGE3.md`). Next: arch which to wire (WAVE A satellite workers first; Dispatcher rails blocked on Kernel attach). · WATCHDOG2 ASSIGNED 2026-08-31T19:45:28.509328-05:00 cm/g46_grok_backlog_maker_gcloud_sweeps_you_are_79cfc2ba__t1800.py
      **STILL OPEN, but the stated BLOCKER IS CLEARED (2026-08-30):** "Dispatcher rails blocked on
      Kernel attach" no longer holds — `Kernel.__init__` composes the Dispatcher (see the closed
      Owed entry below for the code sites + runtime artifact). Dispatcher rails are unblocked for
      arch; sequencing WAVE A first is now a choice, not a constraint.
- [ ] **Mesh additions** — verify each candidate has real hands (Ollama/Groq/Playwright/…).
      **STILL OPEN — re-measured 2026-08-30.** 9 adapters compose, only 4 have runtime-proven
      hands: composed `['claude-cli','codex-cli','cursor-api','firecrawl-web','gem-api','gw-api',
      'oa-api','playwright-dom','sgh-api']` vs `live/registry/nodes.json` → `count: 4`,
      `['claude-cli','gem-api','oa-api','sgh-api']`. The 5 unproven (codex-cli, cursor-api,
      firecrawl-web, gw-api, playwright-dom) are exactly this entry's worklist — fail-closed is
      working as designed (a node that does not answer is not registered), so the gap is real work,
      not a defect.
- [ ] **cosmos_dispatch / cosmos_collector** — live; verify + harden (COW review).
      **STILL OPEN — confirmed open 2026-08-30, do not close on "it's running".** Both daemons are
      live (`live/logs/dispatcher_heartbeat.json`, `collector_heartbeat.json`, both fresh at
      22:49), but the critiques are unsatisfied: `docs/critique/collector_CRITIQUE_g46.md:17`
      verdict **"No — not the decided collector"** (the DHx correlate-marker-to-result function is
      absent; unsynchronized second JSONL writer) and `docs/critique/dispatch_STAGE3.md:12-23`
      ranks one candidate with stages 1–2 never run. A heartbeat is not the gate.
- [~] **Constant session-backlog agent** — flag unaddressed questions/requests/features (Watchdog2 role).
      **PARTIAL 2026-08-30 — half built, half absent; NOT closed.** BUILT: WD2 is that constant
      agent for the *tracked* sources — `cosmos_watchdog2.py:3-7` ("A CONSTANT agent finds, flags,
      and ASSIGNS route items as they surface"), and it names itself the owner of this very row
      (`SELF_SLUGS`, `:116-122`, so it never drops a second agent for it). Live artifact:
      `watchdog2_heartbeat.json` `polls: 12528`, tick footer `flagged=9`. ABSENT: nothing flags
      unaddressed **questions/requests from session transcripts**. `cosmos_context_pull.py` can
      tail a session transcript, but only `cosmos_dispatcher_daemon.py` references it — WD2 does
      not (measured: `context_pull` appears in exactly 2 files under `cosmos/`, neither is WD2).
      Remaining work is the session-mining half only.
- [x] **COSMOS-own clocks (a dozen+)** — NO BTS. Built+registered 2026-08-25T23:19-05.
      Matrix + `schtasks` proof: `docs/ORCHESTRATION.md`. Standup:
      `cosmos/cosmos_own_clocks.py --standup`. Runtime-binding of live Core `:8770` remains BACKLOG.
- [x] **COSMOS_INDEX** — the single living index (tools building / features / implemented),
      self-refreshing from trackers+heartbeats. Generator `cosmos/cosmos_index.py`; dest `docs/COSMOS_INDEX.md`;
      heartbeat `live/logs/cosmos_index_heartbeat.json`; schtasks `COSMOS Index` every 1 min; collector hook each poll.
- [ ] **AUTO-RESESSION** — COSMOS continues its own route across the context boundary with zero / · WATCHDOG2 ASSIGNED 2026-08-31T19:45:28.509328-05:00 cm/g46_grok_backlog_auto_resession_you_are_g46_g_85e577c1__t1800.py
      minimal user disturbance. Stage-1 research in flight → `docs/research/AUTO_RESESSION.md`.
      **STILL OPEN, one word stale (2026-08-30): stage-1 has LANDED, not "in flight".**
      `docs/research/AUTO_RESESSION.md` exists (34,386 bytes, G46, dated 2026-08-26) with the
      layer-A/layer-B split and the R1–R8 rubric. Implementation is the open part — the tick footer
      below still reads `auto_resession:inflight:dhx:resession`, and no resession daemon
      heartbeats in `live/logs/`.
- [x] **Resume gate** (PERMANENT, all streams) — at BootUP, present the option to restart on the
      carried-over task list; no affirmative selection → auto-resume on the 15s WD2 clock. Canon in
      `CLAUDE.md` + `docs/PAUSE_PROTOCOL.md`; WD2 honors flag `mode` (hold / resume_gate + `auto_resume_at`).
      **CLOSED (BUILT) 2026-08-30 — all three cited pieces verified present.** Canon:
      `CLAUDE.md:54-68`; protocol: `docs/PAUSE_PROTOCOL.md:46,49,58`; mechanism:
      `cosmos_watchdog2.py:478-508` (`mode != "resume_gate"` → stay PAUSED; unparseable
      `auto_resume_at` → stay PAUSED, fail-closed) + `:915-943`. Runtime artifact — the self-clear
      has actually fired on this machine: `live/logs/WATCHDOG2.log` →
      `[2026-08-25T23:56:58-05:00] AUTO-RESUME (resume_gate) … auto_resume_at=
      2026-08-25T23:51:58.955511-05:00 reached`. Closing the *build*; the gate itself is a standing
      per-session behavior (canon), not a task that stops applying. It was being re-dropped as
      `resume_gate` on every WD2 pass — that motion stops here.
- [x] **PAUSE protocol** — DONE. `docs/PAUSE_PROTOCOL.md`; formal stop for the 15s retask clock.
- [x] **Wire WD2 → WISHLIST** — WD2/motif-driver scans `docs/WISHLIST.md` as a route source (each
      open wish → a MOTIF thread), so COSMOS self-builds from Keith's wishlist alone. Canon:
      CLAUDE.md "COSMOS builds itself — a process, not an endpoint."
      **CLOSED 2026-08-30 — already wired; verified in code AND at runtime.** Code:
      `cosmos_watchdog2.py:100-113` `MD_ROUTE_SOURCES` = `{wishlist, WISHLIST.md, section "Open
      wishes", enter motif_s1}` then `{backlog, …, enter implement}`; one shared parser
      (`parse_md_checkboxes`, `:580`). Runtime artifact from the *running* daemon —
      `live/logs/watchdog2_heartbeat.json` (`polls: 12528`, `last_run 2026-08-30T22:48:04-05:00`)
      carries `"md_sources": ["wishlist", "backlog"]`. Binding proof that wishlist rows really
      route: the tick footer below flags/skips slugs that exist **only** in `WISHLIST.md` and in no
      BACKLOG row — `grok_gem_node_workers_own_buckets` (WISHLIST.md:38),
      `master_description_re_render` (:49), `auto_context_dispatch` (:42),
      `competency_hierarchy` (:46).

## Owed — LIVE CORE (Keith's call; not fire-and-forget)
- [x] `cosmos.py serve` on real root `:8770` — **CLOSED 2026-09-02.** Health board
      `verdict=GREEN` `serve_8770` listening (runtime-bind GATE_CLOSED quoted
      `rtt_s=0.0252`). The 08-30 RED/`NO_LAUNCHER` diagnosis is stale. Supervisor
      `ALREADY_UP`.
- [x] `Kernel.__init__` never calls `register_node_rails` — Dispatcher not composed on normal boot.
      **CLOSED 2026-08-30 — STALE; already fixed in the working tree.** Re-verified in the code by
      this pass, not accepted on another agent's say-so: `cosmos_kernel.py:137-138`
      (`self.rails_compose = (None if read_only else self.compose_rails(...))` — every writing boot),
      `:178` (`("node_rails", "cosmos_node_rails", "register_node_rails", False)`, first row of the
      compose table), `:235` (`_try("dispatcher", _disp)`; `_disp` sets `self.dispatcher =
      Dispatcher(...)`). `cosmos_node_rails.py:138` defines `register_node_rails`. Own runtime
      artifact — a **writing** Kernel on a throwaway temp root (live tree untouched, zero live
      ledger writes): `READY=True · DISPATCHER=Dispatcher · COMPOSED=['node_rails','cursor-api',
      'codex-cli','playwright-dom','firecrawl-web','claude-cli','dispatcher','prove_nodes'] ·
      WARNINGS=[]`. Corroborates `builds/probe/CORE_8770_DIAGNOSIS.md` §2.4a/b + §4.
      ⚠ **THE FIX IS UNCOMMITTED — a `git checkout`/`stash`/`reset` of these files silently
      un-composes the Dispatcher and re-opens this entry.** Measured:
      `git grep -c "compose_rails" HEAD -- cosmos/cosmos_kernel.py` → no match, same for
      `register_node_rails` and `self.dispatcher` (control: `"class Kernel"` → `HEAD:…:1`, so the
      pathspec is good and the misses are real); `git status` → `M cosmos/cosmos_kernel.py`,
      `M cosmos/cosmos_node_rails.py`. Runtime binding on the LIVE root still waits on the entry
      above — `:8770` has never come up. That blocks the *verification*, not the fix.
- [ ] Tool migration: 135 UNDECIDED / 8 REPLACED — disposition backlog.
      **PARTIAL 2026-08-31T11:56Z.** Live projection unchanged (`total=143 · UNDECIDED 135 ·
      REPLACED 8`, `writes:0`) but the judgements already exist: PORT_DECISIONS holds 35
      rulings, of which 27 are apply-ready (`builds/probe/_f41_proposals.json`). Proposer
      `builds/probe/tool_disposition.py` REFUSES `LIVE_LEDGER_FORBIDDEN` on authority.jsonl
      (ledger 559724 bytes unchanged). **UNPLANNED cards now exist:**
      `builds/probe/_f41_unplanned_cards.json` `card_count:116` `with_candidates:47`
      `disposition:null` (HOLD, no invented ruling). Remaining: COW applies the 27;
      COW records PORT_DECISIONS rulings for the 116 HOLD cards.
