# WOMB — A/B hero board (reused prompts, same agents, hero packs)

n=134 PENDING. Built from good replies + live wishes/workorders. No new prompts written; all tasks verbatim reuse. Agents seated only on Part A (same-agent requeue per your order); everything else UNASSIGNED for WOMBAT/pilot.

## Counts
- heroab: 52
- pile-hold: 11
- pile-restate_gitur: 10
- pile-review: 4
- wish: 42
- workorder: 15
- hero packs: {'hero_coders/6_grok_gitur': 46, 'hero_coders/2_gf38': 1, 'hero_luna': 5}
- superseded set aside (not on board): superseded_lit 15, superseded_gitur 6, superseded_policy 6, cancel 2, close 3 = 32

## How the A/B works
- Part A (52 `heroab`): same prompt + same `agent_field` as the good baseline (`baseline_n`/`baseline_oid`/`baseline_write_path`), this time with `hero_pack` + `hero_pack_ref`. Judge grades both arms; `judge_score_hero` vs `judge_score_base`, `judge_winner` starts PENDING.
- Score tracking keys on every row: `ab_pair_id`, `arm`, `baseline_*`, `judge_score_hero`, `judge_score_base`, `judge_winner`.

## Part A — hero requeues (52)
### 501. wo-20260902T005038-e27005ae-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T005038-e27005ae` ← baseline n=3 `wo-20260902T005038-e27005ae` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T005038-e27005ae\out\out\cdeck_selector_todos_proposal.json`
- scores: hero=None base=None winner=PENDING
- task: You are G46 (Grok Build) on a COSMOS work order. FIRST read DHx and AGENT_BOUNDARIES.  Keith 2026-09-02: cDeck needs (1) a far-left pane to SELECT 1) Projects/streams 2) Previous s
### 502. wo-20260902T113100-05-00-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T113100-05-00` ← baseline n=4 `wo-20260902T113100-05-00` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T113100-05-00\out\proposals\ddeck-resize.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Reformat the D-deck panels so each panel can be resized by the user at ru
### 503. wo-20260902T113100-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T113100` ← baseline n=5 `wo-20260902T113100` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T113100\out\proposals\ddeck-resize.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Reformat the D-deck (cDeck) panels so each panel can be resized by the us
### 504. wo-20260902T114500-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T114500` ← baseline n=6 `wo-20260902T114500` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T114500\out\proposals\runtime-binding-gate.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Close the runtime-binding gate: the seven-stage pipeline has code and pas
### 505. wo-20260902T114510-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T114510` ← baseline n=8 `wo-20260902T114510` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T114510\out\proposals\cosmos-core-service.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Install COSMOS Core as a real resident Windows service: one always-on pro
### 506. wo-20260902T114520-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T114520` ← baseline n=10 `wo-20260902T114520` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T114520\out\proposals\work-order-loop.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Close the work-order loop: the drop folder, verdict spec, and poll doc ex
### 507. wo-20260902T115500-05-00-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T115500-05-00` ← baseline n=15 `wo-20260902T115500-05-00` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T115500-05-00\out\proposals\ddeck-move-snap.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Add drag-to-move for every D-deck panel window: a title bar or drag regio
### 508. wo-20260902T170800-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T170800` ← baseline n=18 `wo-20260902T170800` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T170800\out\proposals\github-agents-local.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Keith 2026-09-02: we can run GitHub agents locally and save quota (SGH). 
### 509. wo-20260902T171500-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T171500` ← baseline n=22 `wo-20260902T171500` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T171500\out\proposals\cdeck-resize-handles.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Keith 2026-09-02: he sees no cDeck improvements and says resize is gone. 
### 510. wo-20260902T174000-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T174000` ← baseline n=26 `wo-20260902T174000` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T174000\out\proposals\work-agents-hands.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Keith 2026-09-02: new OpenAI and other Work products are out and coming. 
### 511. wo-20260902T175700-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T175700` ← baseline n=30 `wo-20260902T175700` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T175700\out\proposals\runtime-binding-gate.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Keith 2026-09-02: close the runtime-binding gate from stage 7 of docs/COS
### 512. wo-20260902T175900-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T175900` ← baseline n=34 `wo-20260902T175900` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T175900\out\proposals\runtime-binding-gate.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Close the runtime-binding gate from stage 7 of docs/COSMOS_PIPELINE.md. T
### 513. wo-20260902T180200-retry2-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T180200-retry2` ← baseline n=40 `wo-20260902T180200-retry2` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T180200-retry2\out\proposals\runtime-binding-service.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Part 1 of 3 for closing the runtime-binding gate: the Windows service wra
### 514. wo-20260902T180210-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T180210-retry` ← baseline n=47 `wo-20260902T180210-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T180210-retry\out\proposals\runtime-binding-watchdog.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Part 2 of 3 for closing the runtime-binding gate: the watchdog and schedu
### 515. wo-20260902T180220-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T180220-retry` ← baseline n=53 `wo-20260902T180220-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T180220-retry\out\proposals\runtime-binding-integration.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Part 3 of 3 for closing the runtime-binding gate: the integration harness
### 516. wo-20260902T184600-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T184600-retry` ← baseline n=59 `wo-20260902T184600-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T184600-retry\out\proposals\runtime-binding-service.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Part 1 of 3 for closing the runtime-binding gate: the Windows service wra
### 517. wo-20260902T184610-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T184610-retry` ← baseline n=65 `wo-20260902T184610-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T184610-retry\out\proposals\runtime-binding-watchdog.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Part 2 of 3 for closing the runtime-binding gate: the watchdog and schedu
### 518. wo-20260902T184620-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T184620-retry` ← baseline n=71 `wo-20260902T184620-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T184620-retry\out\proposals\runtime-binding-integration.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Part 3 of 3 for closing the runtime-binding gate: the integration harness
### 519. wo-20260902T190500-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T190500-retry` ← baseline n=77 `wo-20260902T190500-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T190500-retry\out\proposals\runtime-binding-git-commit.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Add the git-commit-and-push step to the daemon pipeline so every write th
### 520. wo-20260902T191500-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T191500` ← baseline n=82 `wo-20260902T191500` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T191500\out\proposals\test-runtime-binding.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Keith 2026-09-02: close the stage-7 runtime-binding gate. COW filed tests
### 521. wo-20260902T193000-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T193000-retry` ← baseline n=116 `wo-20260902T193000-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T193000-retry\out\proposals\daemon-query-extension.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Extend the existing cosmos_daemon.py (single daemon, no second process) t
### 522. wo-20260902T194500-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T194500-retry` ← baseline n=152 `wo-20260902T194500-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T194500-retry\out\proposals\query-daemon-design.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Design the query-handling addition to the existing single cosmos_daemon.p
### 523. wo-20260902T195000-retry-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260902T195000-retry` ← baseline n=168 `wo-20260902T195000-retry` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T195000-retry\out\proposals\three-channel-loop.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Design the canonical three-channel communication loop for the mesh: (1) q
### 524. wo-20260902T175000-gemping-heroab — Google | Flash | gemini-2.5-flash + hero_coders/2_gf38
- pair `ab-wo-20260902T175000-gemping` ← baseline n=326 `wo-20260902T175000-gemping` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260902T175000-gemping\out\prove\gem_ping.json`
- scores: hero=None base=None winner=PENDING
- task: PROVE call/return only. You are GEM on the COSMOS Vertex rail. Write ONLY the Output file as JSON with keys: ok, rail, model, nonce (unique), invoked_how (must be vertex if Vertex 
### 525. wo-20260903T003252-cdeck-p5-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260903T003252-cdeck-p5` ← baseline n=327 `wo-20260903T003252-cdeck-p5` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260903T003252-cdeck-p5\out\proposals\cdeck-p5-three-pane.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. COSMOS only (V:\A\Ai\COSMOS). Not BTS-MESH. Not V:\Ai. Not Legal. Not cos
### 526. wo-20260903T003810-cdeck-sess-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260903T003810-cdeck-sess` ← baseline n=330 `wo-20260903T003810-cdeck-sess` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260903T003810-cdeck-sess\out\proposals\cdeck-left-session-resume.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. COSMOS only. Not BTS-MESH. Not V:\Ai. Keith 2026-09-03: cDeck leftmost pa
### 527. wo-20260903T004834-dispcol-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260903T004834-dispcol` ← baseline n=331 `wo-20260903T004834-dispcol` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260903T004834-dispcol\out\proposals\backlog-dispatch-collector.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. COSMOS only. Resume last-session Core backlog drain after GATE_CLOSED. BA
### 528. wo-20260903T004834-mesh-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260903T004834-mesh` ← baseline n=332 `wo-20260903T004834-mesh` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260903T004834-mesh\out\proposals\backlog-mesh-unproven.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. COSMOS only. Resume last-session Core backlog drain after GATE_CLOSED (li
### 529. wo-20260905T220000-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T220000` ← baseline n=368 `wo-20260905T220000` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T220000\out\proposals\OPENWORK_INTEGRATE_LANE_A.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. RESEARCH only. How should COSMOS and OpenWork integrate without cloning e
### 530. wo-20260905T221100-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T221100` ← baseline n=375 `wo-20260905T221100` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221100\out\proposals\clocks-observe.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. MOTIF on 
### 531. wo-20260905T221200-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T221200` ← baseline n=382 `wo-20260905T221200` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221200\out\proposals\cdeck-backlog.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. One job: remaining cDeck BACKLOG rows that are BACKLOG not 
### 532. wo-20260905T221300-heroab — xAI | Grok | grok-4.6 + hero_luna
- pair `ab-wo-20260905T221300` ← baseline n=389 `wo-20260905T221300` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221300\out\proposals\auto-resession-next.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: DOM. SGH; free Gemini/Google search; ChatGPT chatbot; Perplexity; 
### 533. wo-20260905T221400-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T221400` ← baseline n=396 `wo-20260905T221400` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221400\out\proposals\orch-profiles.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. MOTIF: ORCHESTRATOR PROFILES — one occupant per profile (GF
### 534. wo-20260905T221500-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T221500` ← baseline n=403 `wo-20260905T221500` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221500\out\proposals\session-tools-next.json`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. MOTIF continue SESSION TOOLS: CCr PR #43 is Slices 1-4; CLI
### 535. wo-20260905T221600-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T221600` ← baseline n=410 `wo-20260905T221600` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221600\out\proposals\health-watchdog.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 536. wo-20260905T221700-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T221700` ← baseline n=416 `wo-20260905T221700` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221700\out\proposals\bulletproof-backup.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 537. wo-20260905T221800-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T221800` ← baseline n=421 `wo-20260905T221800` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221800\out\proposals\diff-family-critique.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 538. wo-20260905T221900-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T221900` ← baseline n=426 `wo-20260905T221900` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T221900\out\proposals\orch-mailbox.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 539. wo-20260905T222000-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T222000` ← baseline n=431 `wo-20260905T222000` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222000\out\proposals\parallel-orch.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 540. wo-20260905T222100-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T222100` ← baseline n=436 `wo-20260905T222100` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222100\out\proposals\wire-mesh.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 541. wo-20260905T222200-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T222200` ← baseline n=441 `wo-20260905T222200` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222200\out\proposals\dispatch-collector.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 542. wo-20260905T222300-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T222300` ← baseline n=446 `wo-20260905T222300` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222300\out\proposals\maker-hands-arch.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 543. wo-20260905T222400-heroab — xAI | Grok | grok-4.6 + hero_luna
- pair `ab-wo-20260905T222400` ← baseline n=451 `wo-20260905T222400` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222400\out\proposals\new-ai-discovery.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: DOM. SGH; free Gemini/Google search; ChatGPT chatbot; Perplexity; 
### 544. wo-20260905T222500-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T222500` ← baseline n=456 `wo-20260905T222500` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222500\out\proposals\competency.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 545. wo-20260905T222600-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T222600` ← baseline n=461 `wo-20260905T222600` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222600\out\proposals\crucible-extra-judges.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 546. wo-20260905T222700-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T222700` ← baseline n=466 `wo-20260905T222700` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222700\out\proposals\github-agents-local.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 547. wo-20260905T222800-heroab — xAI | Grok | grok-4.6 + hero_luna
- pair `ab-wo-20260905T222800` ← baseline n=471 `wo-20260905T222800` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222800\out\proposals\federation-spec.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: DOM. SGH; free Gemini/Google search; ChatGPT chatbot; Perplexity; 
### 548. wo-20260905T222900-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T222900` ← baseline n=476 `wo-20260905T222900` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T222900\out\proposals\r2-trees.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 549. wo-20260905T223000-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T223000` ← baseline n=481 `wo-20260905T223000` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T223000\out\proposals\node-workers.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 550. wo-20260905T223100-heroab — xAI | Grok | grok-4.6 + hero_coders/6_grok_gitur
- pair `ab-wo-20260905T223100` ← baseline n=486 `wo-20260905T223100` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T223100\out\proposals\auto-context-dispatch.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: GITUR. Pin Claude Opus 5 on Cursor. Refuse Composer 2.5. Do not me
### 551. wo-20260905T223200-heroab — xAI | Grok | grok-4.6 + hero_luna
- pair `ab-wo-20260905T223200` ← baseline n=491 `wo-20260905T223200` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T223200\out\proposals\sgh-drive-hands.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: DOM. SGH; free Gemini/Google search; ChatGPT chatbot; Perplexity; 
### 552. wo-20260905T223300-heroab — xAI | Grok | grok-4.6 + hero_luna
- pair `ab-wo-20260905T223300` ← baseline n=496 `wo-20260905T223300` → `V:\A\Ai\COSMOS\live\work\orders\wo-20260905T223300\out\proposals\chrome-extension.md`
- scores: hero=None base=None winner=PENDING
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: DOM. SGH; free Gemini/Google search; ChatGPT chatbot; Perplexity; 

## Part B1 — live workorders (15, UNASSIGNED)
### 553. wo-20260919T010000-restate-fail-xfer-womb
- src `live-drop/wo-20260919T010000-restate-fail-xfer.json` | drop route: Gitur Cursor grok-4.6 BUILD + GLM Flash mouth check
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: FAIL is not terminal. Add cosmos-score-attempt/1 JSONL + wo_partner autopsy + GAC re-seat 
### 554. wo-20260919T010100-restate-wo-partner-womb
- src `live-drop/wo-20260919T010100-restate-wo-partner.json` | drop route: Gitur Cursor grok-4.6 BUILD + DS Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: wo_partner(order) returns partner_id+state or UNMEASURED. Same pair_id / stamp-minute / Ta
### 555. wo-20260919T010200-restate-judge-run-womb
- src `live-drop/wo-20260919T010200-restate-judge-run.json` | drop route: Gitur Cursor grok-4.6 BUILD + Luna Flex review later
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: judge_run — ONE Judge model and ONE fat prefix for the whole run. Regrades are attempt 2/3
### 556. wo-20260919T010300-restate-judge-idle-womb
- src `live-drop/wo-20260919T010300-restate-judge-idle.json` | drop route: Gitur Cursor grok-4.6 BUILD + GLM Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: judge_idle_gate(n_board, cache_alive): if bucket+picked < 20 AND cache expired, LEAVE the 
### 557. wo-20260919T010400-restate-head-gate-womb
- src `live-drop/wo-20260919T010400-restate-head-gate.json` | drop route: Gitur Cursor grok-4.6 BUILD + GLM Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: cosmos_head_gate — git rev-list --count origin/main..HEAD must be 0 or refuse synced. Uniq
### 558. wo-20260919T010500-restate-warn-x3-womb
- src `live-drop/wo-20260919T010500-restate-warn-x3.json` | drop route: Gitur Cursor grok-4.6 BUILD + DS Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: WARN BEFORE ERROR x3. See danger, print WARN BEFORE ERROR: {kind} three times, then refuse
### 559. wo-20260919T010600-restate-orch-profiles-womb
- src `live-drop/wo-20260919T010600-restate-orch-profiles.json` | drop route: Gitur Cursor grok-4.6 BUILD + GLM Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: ORCHESTRATOR PROFILES — one occupant per profile (tree grant + CCR.lease), not a second li
### 560. wo-20260919T010700-restate-session-tools-womb
- src `live-drop/wo-20260919T010700-restate-session-tools.json` | drop route: Gitur Cursor grok-4.6 BUILD + DS Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: SESSION TOOLS next slice only (CCr PR 43 slices 1-4 already). One file. NONE if done. VERI
### 561. wo-20260919T010800-restate-auto-resession-womb
- src `live-drop/wo-20260919T010800-restate-auto-resession.json` | drop route: Gitur Cursor grok-4.6 BUILD + GLM Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: AUTOMATED RESESSION — next measurement only, not a spawn, not a second Core. SOP already e
### 562. wo-20260919T010900-restate-cdeck-backlog-womb
- src `live-drop/wo-20260919T010900-restate-cdeck-backlog.json` | drop route: Gitur Cursor grok-4.6 BUILD (cdeck repo) + GLM Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. ONE bite: remaining cDeck BACKLOG rows that are BACKLOG not BLOCKED/DO-NOT. Not C1 ConPTY. Not OpenW
### 563. wo-20260919T011000-restate-query-channel-womb
- src `live-drop/wo-20260919T011000-restate-query-channel.json` | drop route: Luna Flex JUDGE-research + GLM Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. RESEARCH only (not code): query channel / three-channel mesh — (1) query (2) drop (3) return. DOM fi
### 564. wo-20260919T011100-restate-dom-sgh-deerflow-womb
- src `live-drop/wo-20260919T011100-restate-dom-sgh-deerflow.json` | drop route: Luna Flex + GLM Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. RESEARCH DOM only: SGH local GitHub agents + DeerFlow on existing Chrome path. Not Gitur. Not this T
### 565. wo-20260919T011200-restate-federation-womb
- src `live-drop/wo-20260919T011200-restate-federation.json` | drop route: Luna Flex + DS Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. RESEARCH: five federation blockers so peer meshes can go live. Each blocker: concrete fix OR explici
### 566. wo-20260919T011300-restate-work-agents-womb
- src `live-drop/wo-20260919T011300-restate-work-agents.json` | drop route: Luna Flex + GLM Flash
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. RESEARCH: new OpenAI and other Work products. Propose docs/research/WORK_AGENTS_HANDS.md. ITEM or NO
### 567. wo-20260919T140000-tools-claude-code-parity-womb
- src `live-drop/wo-20260919T140000-tools-claude-code-parity.json` | drop route: xAI | Grok | grok-4.6
- task: FIRST read AGENT_BRIEF and AGENT_BOUNDARIES. P10 propose only.  ONE bite: COSMOS coding tools modeled on Claude Code: Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch, Skil

## Part B2 — pile hold/review/restate_gitur (25, UNASSIGNED)
### 568. wo-20260905T220000-womb [pile-hold]
- src `pile/hold/wo-20260905T220000` docs exist; no iframe
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. RESEARCH only. How should COSMOS and OpenWork integrate without cloning e
### 569. wo-20260902T190500-womb [pile-hold]
- src `pile/hold/wo-20260902T190500` do not WO every write pushes
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Add the git-commit-and-push step to the daemon pipeline so every write th
### 570. wo-20260904T031200-womb [pile-hold]
- src `pile/hold/wo-20260904T031200` Medicine Man PARKED
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only on the Grok lane. Route: CURSOR. Keith 2026-09-04: build the live Crucible critic set on Cursor Cloud
### 571. wo-20260904T120000-womb [pile-hold]
- src `pile/hold/wo-20260904T120000` CLOCKS observe-only / critics see clocks — FIFO after Gitur pile
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Route: CURSOR. Keith 2026-09-04: GitHub critics must see all 26 CLOCKS (cosmos/cosmos_own_clocks.py 
### 572. wo-20260904T124800-womb [pile-hold]
- src `pile/hold/wo-20260904T124800` CLOCKS observe-only / critics see clocks — FIFO after Gitur pile
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: CURSOR. Keith 2026-09-04: this TUI does not code — it writes work 
### 573. wo-20260905T120000-womb [pile-hold]
- src `pile/hold/wo-20260905T120000` Medicine Man PARKED
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: CURSOR. Keith 2026-09-05: keep coding COSMOS. Incoming company GCl
### 574. wo-20260907T152629-womb [pile-hold]
- src `pile/hold/wo-20260907T152629` frozen DEFINE MOTIF RESEARCH
- task: FIRST read work_orders/ccr/DEFINE_CHATBOT_PHONE.md. That file is the frozen DEFINE. Do not paraphrase. MOTIF stage 2 RESEARCH only (DOM rails). P10: PROPOSE only. Never write the l
### 575. wo-20260904T125500-womb [pile-review]
- src `pile/review/wo-20260904T125500` unique leftover — human/orch DEFINE
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: CURSOR. Keith 2026-09-04: this TUI does not code. Cooking is COSMO
### 576. wo-20260917T163833-womb [pile-hold]
- src `pile/hold/wo-20260917T163833` sandbox HOLD keys; facade on LiT; do not merge HOST_PEN=V:\
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. You are WOMBAT GF38. Write a fat-cache coding ITEM tail from wo-20260917T181010 (Daytona/E2B sandbox
### 577. wo-20260917T163839-womb [pile-hold]
- src `pile/hold/wo-20260917T163839` sandbox HOLD keys; facade on LiT; do not merge HOST_PEN=V:\
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. You are SOL (openai/gpt-5.6-sol) coding against G46/GLM. Daytona/E2B backends behind cosmos_sandbox.
### 578. wo-20260909T181800.json-womb [pile-review]
- src `pile/review/wo-20260909T181800.json` unique leftover — human/orch DEFINE
- task: FIRST read docs/AGENT_BRIEF.md (DHx) and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Deliver the last 10-minute CCr update: a timestamped status of what
### 579. wo-20260908T180000.json-womb [pile-hold]
- src `pile/hold/wo-20260908T180000.json` frozen DEFINE MOTIF RESEARCH
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Running leftover list from this CCr session and prior Keith asks — follow
### 580. wo-20260917T181010.json-womb [pile-hold]
- src `pile/hold/wo-20260917T181010.json` sandbox HOLD keys; facade on LiT; do not merge HOST_PEN=V:\
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Route: CURSOR. Compose Daytona and E2B as named backends behind cosmos_sa
### 581. wo-20260917T210153-womb-seat.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T210153-womb-seat.json` work_orders/ccr/GITUR_WOMB_SEAT.md
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10 PROPOSE. WOMB pick_pair. See work_orders/ccr/GITUR_WOMB_SEAT.md. Do not pull unique HEAD. Pen f47bad
### 582. wo-20260917T210154-makers-role.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T210154-makers-role.json` work_orders/ccr/GITUR_MAKERS_ROLE_WRAPPER.md
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10 PROPOSE. makers ROLE WRAPPER. See work_orders/ccr/GITUR_MAKERS_ROLE_WRAPPER.md. Do not pull unique H
### 583. wo-20260917T210155-learn-clock.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T210155-learn-clock.json` work_orders/ccr/GITUR_LEARN_CLOCK.md
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10 PROPOSE. learn-style clock. See work_orders/ccr/GITUR_LEARN_CLOCK.md. Do not pull unique HEAD. Pen f
### 584. wo-20260917T210156-cdeck-create.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T210156-cdeck-create.json` work_orders/ccr/GITUR_CDECK_CREATE_ROLE.md
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10 PROPOSE. CREATE ROLE WRAPPER. See work_orders/ccr/GITUR_CDECK_CREATE_ROLE.md. Do not pull unique HEA
### 585. wo-20260917T212414-opus-ledger.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T212414-opus-ledger.json` work_orders/ccr/GITUR_OPUS_LEDGER.md
- task: Route: CURSOR. P10. Opus AM pack first. See work_orders/ccr/GITUR_OPUS_LEDGER.md. CCr f47bad79 disposes LiT.
### 586. wo-20260917T212414-opus-resume.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T212414-opus-resume.json` work_orders/ccr/GITUR_OPUS_SPEND_RESUME.md
- task: Route: CURSOR. P10. Opus AM pack first. See work_orders/ccr/GITUR_OPUS_SPEND_RESUME.md. CCr f47bad79 disposes LiT.
### 587. wo-20260917T220523-canon-spawn.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T220523-canon-spawn.json` docs/CANON_SPAWN.md + GITUR_CANON_SPAWN.md + GITUR_HARNESS_SEAT.md
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10. Tag CCr f47bad79 preload default Role/Wrapper/Skills. ENCODE spawn FORM: Role, Role[Model] Wrapper,
### 588. wo-20260917T220523-scar-1-problem.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T220523-scar-1-problem.json` docs/CANON_SPAWN.md + GITUR_CANON_SPAWN.md + GITUR_HARNESS_SEAT.md
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10. Tag CCr f47bad79 preload default Role/Wrapper/Skills. Never 112x MOTIF-driver WOs. One wish one six
### 589. wo-20260917T220523-scar-2-agent.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T220523-scar-2-agent.json` docs/CANON_SPAWN.md + GITUR_CANON_SPAWN.md + GITUR_HARNESS_SEAT.md
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10. Tag CCr f47bad79 preload default Role/Wrapper/Skills. Never grok.exe / grok --single as WO worker. 
### 590. wo-20260917T220523-scar-3-prompt.json-womb [pile-restate_gitur]
- src `pile/restate_gitur/wo-20260917T220523-scar-3-prompt.json` docs/CANON_SPAWN.md + GITUR_CANON_SPAWN.md + GITUR_HARNESS_SEAT.md
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10. Tag CCr f47bad79 preload default Role/Wrapper/Skills. Context source MUST be a list of existing [re
### 591. wo-20260917T215011-restate-profiles.json-womb [pile-review]
- src `pile/review/wo-20260917T215011-restate-profiles.json` unique leftover — human/orch DEFINE
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. WOMBAT ITEM then pair GLM Flash + Luna Flex. Restate: one occupant per orch profile (tree grant + CCR.lease), not a sec
### 592. wo-20260917T220523-scar-5-judge-idle.json-womb [pile-review]
- src `pile/review/wo-20260917T220523-scar-5-judge-idle.json` unique leftover — human/orch DEFINE
- task: FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. Route: CURSOR. P10. Tag CCr f47bad79 preload default Role/Wrapper/Skills. One Judge per run. If cache dead and n_board 

## Part B3 — open wishes (42, UNASSIGNED)
### 593. wish-01-womb
- task: WISH: HERMES CREDENTIAL POOLS + PROVIDER ROUTING (Keith 2026-09-18). Same-provider key rotate (`OPENROUTER_API_KEY`, `_2`, `_3`) and `ignore: ["deepinfra"]` for GLM. `fill_first` n
### 594. wish-02-womb
- task: WISH: CHATBOT PHONE — FREEMIUM (Keith 2026-09-07). *Follow the Freemium model.* *You can include adversarial AI over remote (terminal OR phone).* Phone ChatBot = **free forever** f
### 595. wish-03-womb
- task: WISH: OSS CODE BORROW (Keith 2026-09-07). Besides layout, read LangGraph / LangFlow / Temporal / n8n / Dify **source**. IN COSMOS / BORROW / ADAPT / LEARN / REFUSE. Execute MOTIF. 
### 596. wish-04-womb
- task: WISH: CDECK PARALLEL INSTANCES (Keith 2026-09-07). cDeck runs parallel profile windows the way Grok.com + OpenWork already sit in parallel: one instance **Forge**, one instance **C
### 597. wish-05-womb
- task: WISH: OPENWORK IS LOAD-BEARING (Keith 2026-09-05). *OpenWork has too much of what we need to ignore.* COSMOS **consumes** OpenWork (skills, plugins, MCP, session groups/workflows, 
### 598. wish-06-womb
- task: WISH: SESSION TOOLS SUITE (Keith 2026-09-05). Full suite of session tools — not only the leftover Cowork→OpenWork migrator. Covers **crashed systems**, **all AIs and installs**, an
### 599. wish-07-womb
- task: WISH: GROK COWORK SURFACE — Keith 2026-08-31: build the tools/interface Claude Cowork has, so Grok can compete and win. **cDeck = Orchestration. Grok TUI = hardcore coding, as a pa
### 600. wish-08-womb
- task: WISH: ORCHESTRATOR PROFILES (Keith 2026-09-02). Different profiles for different · WATCHDOG2 ASSIGNED 2026-09-02T19:17:28.847086-05:00 cm/g46_grok_motif_orchestrator_profiles_keith
### 601. wish-09-womb
- task: WISH: CHROME EXTENSION / PLUGIN FOR GROK (future — Keith 2026-09-02). A Chrome · WATCHDOG2 ASSIGNED 2026-09-02T19:17:28.847086-05:00 cm/g46_grok_motif_chrome_extension_plugin_for_g
### 602. wish-10-womb
- task: WISH: SGH DRIVE HANDS (future — Keith 2026-09-02). SuperGrok Heavy Chatboxes (DT Chat · WATCHDOG2 ASSIGNED 2026-09-02T19:17:28.847086-05:00 cm/g46_grok_motif_sgh_drive_hands_future
### 603. wish-11-womb
- task: WISH: WORK AGENTS CLASS (Keith 2026-09-02 — out now and coming). The Cowork fight is · WATCHDOG2 ASSIGNED 2026-09-02T19:17:44.635751-05:00 cm/g46_grok_motif_work_agents_class_keith
### 604. wish-12-womb
- task: WISH: cDeck — **Orchestration** (Keith 8/31 evening). Current 19-panel KDash clone is not that UX. Front stage: talk, jobs, orchestration tools, Automations, pool, voice, **Grok TU
### 605. wish-13-womb
- task: WISH: AUTO-RESESSION — continue across the context boundary, zero / minimal user disturbance.
### 606. wish-14-womb
- task: WISH: Maker-hands — sweep every AI-maker's tools; wire the useful ones as COSMOS rails/nodes. - [x] **CVM (voice)** — SUPERSEDED 2026-09-03 by Grok Voice → SGH phone app. Code reta
### 607. wish-15-womb
- task: WISH: GROK VOICE → SGH PHONE — **TABLED 2026-09-04** (Keith: mostly solved; refine later). Endpoint on this roll: SGH Android Voice + **Grok Voice Think Fast 2.0** (`grok-voice-thi
### 608. wish-16-womb
- task: WISH: CDM · gbridge — carry each to the runtime-binding gate. - [x] **Live Core** — `cosmos serve` on `:8770` GREEN 2026-09-02; Kernel composes Dispatcher.
### 609. wish-17-womb
- task: WISH: Grok & GEM node workers (own buckets) — native Windows Python daemons: each polls its own · WATCHDOG2 ASSIGNED 2026-08-31T19:45:12.264797-05:00 cm/g46_grok_motif_grok_gem_nod
### 610. wish-18-womb
- task: WISH: Auto-context dispatch — COW drops only a tag + assignment; a native daemon pulls the       session context from C:\ (transcript tail), creates the tagged agent, feeds it cont
### 611. wish-19-womb
- task: WISH: Competency hierarchy — SGH web-researches + builds a rated skills matrix (task type × · WATCHDOG2 ASSIGNED 2026-08-31T19:45:12.264797-05:00 cm/g46_grok_motif_competency_hiera
### 612. wish-20-womb
- task: WISH: Master description re-render — regenerate `COSMOS_MASTER_DESCRIPTION.docx` via an AGENT · WATCHDOG2 ASSIGNED 2026-08-31T19:45:12.264797-05:00 cm/g46_grok_motif_master_descrip
### 613. wish-21-womb
- task: WISH: NEW-AI DISCOVERY (active scout). A researcher/daemon that goes OUT and finds NEW AI       products/models/agents to add to COSMOS — not just re-reading known HANDS. It propos
### 614. wish-22-womb
- task: WISH: READ EVERY MANUAL + MAP EVERY PRODUCT. SGH reads the full manual/doc/dissertation for       every AI product we have and MAPS it into `docs/COMPETENCY.toml` as a real node ro
### 615. wish-23-womb
- task: WISH: WIRE THE MESH (nodes mapped at RUNTIME). The live registry (`live/registry/`) is EMPTY and       <!-- CORRECTION 2026-08-30 21:30 (Claude Code, measured not asserted): the pr
### 616. wish-24-womb
- task: WISH: FIX DIFFERENT-FAMILY CRITIQUE. GEM and OA critique rails land EMPTY (rc=0, 0.0s, no stdout)       — only Grok/G46 (same family) executes, so the vendor-plural stage-5 gate th
### 617. wish-25-womb
- task: WISH: WRITE THE MISSING TOOLS. For every capability we need and don't have, have an agent BUILD       the tool (not just research it). No `tools/` dir exists today; maker-hands is 
### 618. wish-26-womb
- task: WISH: cDeck REAL parity (not asserted). Code claims KDash-superset (18 panels) but several render       UNMEASURED/derived and it defaults to `:8791` not the live `:8770` — so it L
### 619. wish-27-womb
- task: WISH: CREDENTIALING = open-window handoff. When a build needs an account/key (account creation,       API key, OAuth), COW OPENS the signup/login window and leaves it open for Keit
### 620. wish-28-womb
- task: WISH: BULLETPROOF BACKUP (P0 — first). Native Python backup daemon backing up the COSMOS tree       AND all of `V:\` — verified (per-file hash), rehearsed restore, scheduled, fail-
### 621. wish-29-womb
- task: WISH: R2 running properly — trees: `V:\Research4`, `V:\Ai`, `V:\A` (→ ITC). Keys live in       `D:\R2Cloner`; COW opens the door for any credential, never a bat.
### 622. wish-30-womb
- task: WISH: Voice app + Mobile app — carry CVM to the gate (thin-phone / heavy-local pull clock +       desktop CVM on the same headphones) and the phone/mobile client alongside it.
### 623. wish-31-womb
- task: WISH: cDeck — major improvement: Keith 8/31 evening: the 19-panel telemetry wall is the       wrong product. Operator home first (talk / jobs / Automations / pool / voice). Keep   
### 624. wish-32-womb
- task: WISH: ADD HANDS + PUBLIC AIs (active scout). Go out and find + WIRE additional public AI       tools/MCPs as new hands; build the missing tools, don't just research them.
### 625. wish-33-womb
- task: WISH: HANDS FOR THE OTHER AIs — build tools/hands for OpenAI, Grok/GrokBot, and others so each       is a first-class working node.
### 626. wish-34-womb
- task: WISH: META + AMAZON AS EXTRA JUDGES (Keith 2026-09-01). Stage-5 critics add **Meta Llama**       (family `meta`) and/or **Amazon Nova** (family `amazon`) — real extra votes against
### 627. wish-35-womb
- task: WISH: Claude Desktop on Amazon Bedrock — Keith paste 2026-09-02 (AWS 21 APR 2026, updated       June 2026). Official AWS rail: Chat + Cowork + Claude Code through Bedrock in-accoun
### 628. wish-36-womb
- task: WISH: COWORK BACK AS ORCHESTRATOR (contingency — Keith 2026-09-02). Remember and keep       the door open: Claude Cowork may sit as COSMOS orchestrator again. Two allowed       pat
### 629. wish-37-womb
- task: WISH: GROK-BASED MESH (Keith 2026-09-01 — standing). Home is Grok: this TUI + GrokBot       orchestrate; Grok Build codes. Anthropic/Claude is not dispatched. Other families stay  
### 630. wish-38-womb
- task: WISH: GITHUB AGENTS LOCAL (Keith 2026-09-02 — SGH). Run GitHub Copilot agents on the       desktop clones under `V:\GitHub\` (cosmos, cdeck, cdm, cosmos-android, bts-mesh), not    
### 631. wish-39-womb
- task: WISH: SECOND / PARALLEL ORCHESTRATOR (P1 — top of the build wave; "the promotion"). Stand up a       backup/parallel orchestrator on a PREPAID model (from the SGH+GEM orchestrator 
### 632. wish-40-womb
- task: WISH: INTER-ORCHESTRATOR COMMS (COW ⇄ GrokBot) — write-locked shared mailbox (P1). Give the two       orchestrators a way to TALK: a shared drop-note / mailbox on disk (file-based 
### 633. wish-41-womb
- task: WISH: FEDERATION — bring other COSMOS installs into the mesh. LAN first: **SRV1**       (9 TB Linux/Win10) and **T7** (T7920, 56-core Xeon, 128 GB). **People/systems next       (Ke
### 634. wish-42-womb
- task: WISH: HEALTH WATCHDOG + FREE HEARTBEAT + COW-ESCALATION-ON-EXCEPTION (P0 — unattended-safe). A       native Python watchdog (free, no Claude) that every ~hour checks the fleet — da
