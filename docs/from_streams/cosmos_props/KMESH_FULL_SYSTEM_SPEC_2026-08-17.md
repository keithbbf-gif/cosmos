# KMESH FULL SYSTEM SPEC — 2026-08-17

**AUTHORITATIVE PLAN SPEC. NOT A BUILD OR GO.** Keith BBF / GbQA. On-disk corpus only; UNKNOWN means owner decision or new measurement required. No Legal content, TidyUP, publish, spend, or `claude.exe`.

## 1. Ontology and invariants

BTS_MESH is software; KMesh is the instance. ROLD is constitution. A model node is an actor/family/role, not a transport. **GEM is one node; Vertex is GEM's live Google API/credit execution rail, not another node. Preserve `vertex` routing and `vertex_usage.json`; roughly $295/$300 credit expires October 2026.** AI Studio is a GEM path and currently billing-dead. One writer per host/key; append-only SCARS/ledger; explicit roots only (`BTS_AI_ROOT`, `BTS_RESEARCH_ROOT`, optional roots file), configured-missing fails loud; no drive ladder.

## 2. Model/node inventory

- **SGH** — xAI/Grok 4.5; independent xAI family. `bts_sgh.py`, xAI `/v1/responses`; DOM grok.com prepaid, API metered and search requires `spend_ok`. Health must be live-call/selftest plus measured ledger, never a remembered HTTP 200.
- **GW** — Grok Build (`grok-build-0.1`), `bts_gw.py`, `cli-grok`; same engine/family as SGH, not an independent check. CLI prepaid; API shares SGH ceiling. UNKNOWN current callable state requires selftest.
- **GEM** — Google/Gemini; independent Google family. `bts_gem.py`, `bts_vertex.py`; `vertex` API/credit rail, `cli-gemini`, `gemini-dom`, AI-Studio HTTP path. Vertex live in corpus; AI Studio billing-dead/broken; CLI registered but live health UNKNOWN. Required: no-spend credential/config probe, explicit approved live selftest later, credit meter reconciliation.
- **OA** — OpenAI/gpt-5.6; independent family. `bts_oa.py`/`openai-codex` prepaid CLI+MCP (272k ceiling); `bts_oa_api.py`/`openai-api` metered (1.05M in/128k out), separate ledgers and ceilings. Known proven 2026-08-15/16 but current health is stale until selftest.
- **CoW** — Anthropic/Claude Code-Cowork; independent family and keeper/verifier role, not bus. `cli-claude`, MCP/BFast, letters/files. Prepaid Max windows; no Claude API node. Do not start `claude.exe`; health UNKNOWN this pass.
- **GbQA** — Grok Bot QA role/agent-team; same vendor platform family as SGH but distinct governance role, not a generation rail or independent family check. Writes QA return surfaces; acceptance is identity/route/write-read proof.
- **CoPG** — GitHub Copilot CLI; `cli-copilot`, MCP config. Family UNKNOWN (self-report gpt-5-mini is unverified); credits include unpriced calls. Must measure executable/version/model/credit.
- **CoP365** — Microsoft 365 Copilot observation-only DOM node in stale registry; family/model and callable automation UNKNOWN. Never count as answering family without proof.
- **No other model-node IDs** occur in the stale on-box `rails.toml`: CoW, GW, SGH, GEM, CoPG, CoP365, OA. Live brief additionally records GbQA. Crossref, ITC, BFast, channels, lock, board, phone, queue, ROLD, BTS_MESH, Crucible and Judge-UPS are not model nodes.

## 3. Rails/transports

Actual registry rail names: `crossref`, `itc`, `xai`, `vertex`, `bfast`, `bfast-handoff`, `cli-copilot`, `cli-grok`, `cli-gemini`, `cli-claude`, `gemini-dom`, `openai-codex`, `openai-api`. Transport classes: CLI, MCP, DOM, API, LOCAL/files/letters, GDX/Drive, ITC/R2. Each rail record must carry node, executable/module, endpoint/tool, destination surface, cost pool, meter source, last-tested CT timestamp, status and selftest. Unmeasured is UNKNOWN, never 0 or GREEN.

## 4. Surfaces and roots

| surface | role/path | writer/discovery | measurement and fail mode |
|---|---|---|---|
| live floor | explicit `BTS_AI_ROOT`; Keith now `V:\Ai`, later possibly `V:\A\Ai` | lock holder; board/phone/queue/tmp/BU | resolve proof + read/write/hash under selected root; configured-missing is fatal |
| research | explicit `BTS_RESEARCH_ROOT`; Keith currently `V:\Research4` | designated pen only; not floor | path proof; no existence ladder or stale fallback |
| GDX | Google Drive handoff, `BTS_SGH_Handoff`, `X:\My Drive\BTS_SGH_Handoff`; `bts_gdx.py` | authorized agent; Drive index | upload/list/read-back hash; filename-only search fails |
| ITC/R2 | `r2:ai-dchambers` -> `https://ai.dchambers.com` | keyed publisher; GrokDex index | keyed listing/count/hash/sample; public HTTP cannot enumerate, so 200 alone fails |
| ODX | archive surface in registry | archival writer; archive index UNKNOWN | listing/hash/age required; absent measurement UNKNOWN |
| GHX | `keithbbf-gif/bts-mesh`, floor commit `fb6c53d` | git pen/PR; Git tree | SHA/tree/status; snapshot is not live pen |
| P archive | `P:\Ai`, sibling of `P:\BOOKS` | copy/archive process | listing/count/hash; never call live floor |
| planned share | `V:\A` ACL parent; planned floor `V:\A\Ai` | none while HOLD | must not be called live until cutover evidence |

Grayson uses the same root roles with his own explicit values. Drive letters are values, never identity.

## 5. ITC backup contract

Corpus records keyed R2 publish and non-enumerable public HTTP; GrokDex is the discovery layer. Live keyed listing measured **9,251 objects** while the older GrokDex held **6,092**, a 3,159-object discovery gap. Nightly behavior through 2026-08-16 was copy-only. Correct design: keyed publish -> keyed `rclone lsf` source-of-truth listing -> regenerate GrokDex -> verify source/destination counts, hashes where available, and deterministic samples -> stamp CT time -> fail loudly on mismatch or index-generation failure. Never infer completeness from public HTTP. Do not publish in this spec pass.

## 6. KDash contract

KDash is a read-only projection via `bts_kdash_feed.py`, `bts_snapshot.py`, `bts_serve.py`, `jack_command.html`, and launcher/runtime artifacts (including KDash launcher/VBS where present). Show real nodes only; show GEM once and Vertex beneath it as rail/capacity/credit. Show channels and surfaces, family-independence flags, lock, board, both phone letters, queue/job states, ROLD/BTS_MESH version, ITC backup/index state, credits/cost pools, federation readiness, and last measurement CT time. Every number cites a meter; stale age is visible; unmeasured != 0.

Known corpus omissions/breakages: stale registry versus live `rails.toml`; Vertex previously misdrawn as node/removed as rail; hard-coded roots in runner/meters; missing `tree_lock.json`; `federation_ready` false; public HTTP cannot enumerate ITC; GrokDex gap; AI Studio billing-dead; GEM CLI health unknown; CoPG family unverified; CoP365 observation-only; false-green selftests/existence checks; stale/last-known-good rendered as current. KDash paints and never routes, spends, fixes, or writes truth.

## 7. Infra/products/bridge

- **lock** `tree_lock.py`/`_queue/tree_lock.json`: cooperative one-pen + control manifest; absent currently means FREE by contract, but unreadable/torn must fail closed.
- **board** `bts_board.py`/`_board/board.json`: route/escalate, not adjudicate.
- **phone** `bts_phone.py` plus `COW_TO_QA_ENGINEER.md` and `QA_ENGINEER_TO_COW.md`: missing inbound means PHONE DEAD.
- **queue** `bts_runner.py`/`_queue`: claim by rename; pending/running/done/failed, heartbeats; hard-coded root must be removed only after sign.
- **ROLD** RULES/RAILS/ROUTINES/SCARS, `rails.toml`, `corrections.toml`: constitution; SCARS append-only.
- **BTS_MESH** software modules, identity, policy, meters, gate, watchdog, snapshot/feed.
- **BFast** bridge/file verbs and handoff rail, not model/node.
- **Crucible** later multi-seat adjudication product; requires fully live mesh and owner-named seat; no sit now.
- **Judge-UPS** separate desktop instrument/product, not runtime/model; own later intent.

## 8. System matrix

| ID | class | family/model | rail | module/tool | root/surface | cost pool | measurement source | current status | acceptance test |
|---|---|---|---|---|---|---|---|---|---|
| SGH | model | xAI/Grok 4.5 | DOM,xai API | `bts_sgh.py` | file return | prepaid+metered | spend ledger/selftest | stale-known | approved call+ledger+file |
| GW | model-role | same as SGH/Grok Build | cli-grok/API | `bts_gw.py` | local/file | prepaid/shared API | executable+ledger | UNKNOWN | version+model+return |
| GEM | model | Google/Gemini | vertex,cli-gemini,gemini-dom,AI Studio | `bts_gem.py`,`bts_vertex.py` | file/DOM | expiring credit+prepaid; Studio dead | `vertex_usage.json`, console proof | Vertex known; others mixed | route+meter+return; no duplicate node |
| OA | model | OpenAI/gpt-5.6 | openai-codex,openai-api | `bts_oa.py`,`bts_oa_api.py` | file | prepaid+metered | OA ledger | stale-known | both rail selftests |
| CoW | model-role | Anthropic/Claude | cli-claude,MCP,letters | Claude/BFast | live floor | prepaid | session/letters | UNKNOWN; do not start | owner-run selftest+roundtrip |
| GbQA | role | xAI-platform/QA | agent,GDX/GHX/files | agent route | review surfaces | subscription | identity+return | live role | stable identity+readback |
| CoPG | model? | UNKNOWN | cli-copilot,MCP | Copilot CLI | local/file | credits/unpriced risk | credit ledger/version | family UNKNOWN | vendor/model+price proof |
| CoP365 | observer | UNKNOWN | DOM | M365 Copilot | DOM/file | subscription | registry/manual proof | observation-only | owner-defined test |
| ITC | surface | n/a | itc/R2 | keyed rclone+GrokDex | R2/public HTTP | current tier | keyed listing/index | 9251 vs 6092 gap | publish+regen+count/hash/sample |
| floor infra | infra | n/a | LOCAL/files | lock/board/phone/runner | configured AI root | free | readback+heartbeats | mixed; lock missing | all selftests same root |
| ROLD/BTS | constitution/software | n/a | LOCAL/GHX | validators/modules | floor+GHX | free | hashes/selftests | snapshot/live drift | exact version+validators |
| GDX/ODX/P/GHX | surfaces | n/a | DRIVE/archive/git | GDX/archive/git tools | named surfaces | mixed/free | listing/hash/SHA | mixed/UNKNOWN | per-surface measurement |
| BFast | bridge | n/a | bfast,bfast-handoff,MCP | `bfast.py` | configured roots | free | verb selftests/hash | corpus-known | 13 verbs+readback |
| Crucible/Judge | products | n/a | mesh/desktop | later products | outside model graph | n/a | dependency checklist | not up | mesh fully up first |

## 9. Dependency-driven restore/build order (after Keith signs only)

1. Freeze authoritative corpus, hashes and explicit host root maps; resolve UNKNOWN owner choices.
2. Restore/validate ROLD and registry semantics, preserving Vertex as GEM rail/accounting.
3. Make path resolver fail-loud; remove hidden ladders/hard-coded runner/meter roots.
4. Restore BTS_MESH identity, atomic bus, lock, board, phone, queue and gates on one selected floor.
5. Restore ledgers/expected-version append, meter schemas, checkpoints and fail-closed readers.
6. Selftest each rail without spend where possible; owner-authorize any live metered proof; record timestamps.
7. Measure each surface; restore GDX/ITC/ODX/GHX/P discovery and hashes.
8. Perform later authorized ITC publish, regenerate GrokDex from keyed listing, and verify.
9. Rebuild KDash projection from the same measurements; compare state one-for-one.
10. Implement federation cursors/checkpoints, trust/meeting point/fencing; keep `federation_ready=False` until every blocker is measured.
11. Score by independent reviewers; author does not close.
12. Only then consider Crucible; Judge-UPS remains its own later dependency tree.

## 10. FULLY UP acceptance

- [ ] Explicit roots resolve on Keith and Grayson; configured-missing fails; no drive ladder.
- [ ] ROLD validators, corrections and append-only SCARS pass against authoritative bytes.
- [ ] Lock/board/phone/queue/bus/gate/health/watchdog each pass real selftests on the same floor.
- [ ] Every registered rail has executable/module, endpoint/tool, cost pool, meter, timestamp and acceptance result; UNKNOWN is visible.
- [ ] Vertex routes and meters under GEM; no Vertex node/family; credit and expiry measured.
- [ ] Every surface has listing/index/count/hash/sample evidence and writer identity.
- [ ] ITC authorized publish, keyed listing, GrokDex regeneration and verification agree; public HTTP is not enumeration proof.
- [ ] KDash displays exactly the measured state, stale ages and UNKNOWNs; no false green/zero.
- [ ] Jobs survive retry without duplicate accepted facts; checkpoints and named cursors restore.
- [ ] `federation_ready` stays False until live peer, meeting point, wire protocol, trust model and notarization/TOCTOU are proven.
- [ ] Family independence is honest: GW≠new family; GbQA role; CoPG/CoP365 UNKNOWN until proven.
- [ ] Crucible remains after a fully live mesh; no minimal sit.

## 11. Explicit UNKNOWNs

Grayson: one named seat vs local Conductor (OWNER). Current rail live health and executable versions (MEASURE). CoPG vendor/model independence and pricing (VENDOR/MEASURE). CoP365 model/callability (OWNER/MEASURE). GEM CLI and DOM health; AI Studio future relevance (MEASURE/OWNER). Exact Vertex remaining credit/expiry reconciliation (CONSOLE MEASURE; no spend). ODX writer/index/health (OWNER/MEASURE). GDX current listing/readback (MEASURE). Current authoritative live `rails.toml` bytes versus stale box copy (RECOVER/MEASURE). ITC object/hash state after any future publish (MEASURE). Federation meeting point/trust/wire/fencing (OWNER/DESIGN).

## Sources read

On-disk only: rebuild plan/groks; `ROLD/rails.toml`, RAILS/ROLD briefs; module inventory and BTS_MESH brief; KDash feed/snapshot/serve/launcher artifacts; R2/GrokDex listing and delta reports; recovery/version reports; architecture mines. No Legal content.

*End. Authoritative plan spec only. No build, publish, spend, Legal, TidyUP, or Crucible sit.*
