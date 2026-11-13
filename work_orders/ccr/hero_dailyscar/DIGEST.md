# DailyScar digest

Redacted headings and one-line lessons. Not for publication raw.

## Ledger headings
- S-01 · 2026-07-05 · Three Chrome-bridge denials were Keith being away, not Keith refusing
  If Keith is away and it's denied, note it and queue bridge work; do NOT retry-spam (3 denials on 2026-07-05 = Keith away, not refusal).
- S-02 · 2026-07-06 · The ROLD commands file was lost to disk truncation and had to be reconstructed
  **⚠ RESTORED 2026-07-06 after disk truncation (see .bak_2026-07-06-* files): reconstructed from Doping-session context; this IS the canonical current version. Post-edit integrity rule: wc -c + tail-check after every edit of this file.**
- S-03 · 2026-07-06 · A mixed permission dialog let the wrong scope be answered
  **2026-07-06 lesson: Keith must answer the PRIMARY per-site ask, not a broader-scope option in a mixed dialog; a mis-click deny is recoverable same-session by re-granting.**
- S-04 · 2026-07-10/11 · GDX write silently failed on stale connector auth, and the node said it could write
  **2026-07-10/11 (mesh/dashboard + GDX session):** **GDX write-requires-reauth class** — Grok's Drive write silently failed on stale connector auth (SGH walked back an earlier "yes I can"); Keith re-auth fixed it and the round-trip proved out. Lesson: don't trust an agent's sel...
- S-05 · 2026-07-12 · MOUNT HIT: jack_command.html served pinned at a truncated 63,824 bytes
  1. **TRUNCATION (known):** jack_command.html served **pinned at 63,824 bytes** (host: 1,146 lines) and
- S-06 · 2026-07-12 · MOUNT HIT: bts_gdx.py read back missing a colon → a FALSE SyntaxError
  2. **CHARACTER-LEVEL CORRUPTION (NEW):** bts_gdx.py read through the mount was **missing a colon** —
- S-07 · 2026-07-12 · MOUNT HIT: dash.json / sgh_spend.json gave bogus JSON decode errors
  3. Same corruption hit dash.json (a bogus "Unterminated string" at line 255, which is valid on disk).
- S-08 · 2026-07-12 · 26 of Chapter 4's 36 references were silently eaten — the list truncated at the letter G
  This is the same failure class that silently ate **26 of Ch4's 36 references** (list truncated at the
- S-09 · 2026-07-12 · BootUP took only one mount and then stalled twice mid-session
  On 2026-07-12 the BootUP took ONLY [path] and then had to stop twice mid-session — for the Desktop (to fix the launcher) and for GDX. Exactly the stall this step exists to prevent. **Ask for the whole set in ONE up-front block, before any work starts.**
- S-10 · 2026-07-12 · The dashboard launcher started the plain static server, so every panel silently went stale
  **⚠ THE 2026-07-12 ROOT CAUSE — do not regress this.** The Desktop launcher was starting **python -m http.server 8765**, the PLAIN static server. It serves the page but has **no /api routes**, so <TEST> could not run the python probe (a browser cannot execute python — the butt...
- S-11 · 2026-07-12 · The §4.10 IP pedestal finding was raised then withdrawn — the chapter was right
  - ❌ §4.10 IP pedestal was RAISED THEN WITHDRAWN — the chapter was right; the error was Cowork's
- S-12 · 2026-07-13 · A brand-new Origin reader was written while three existing tools sat unpointed-at — and $2.93 of paid search bought facts already in Ch4's own reference list
  **WHY IT IS HERE AND NOT BURIED:** on 2026-07-13 Cowork wrote a brand-new Origin reader while BUILD_OPJ_READER.sh, origin_export.py and a fully populated Ai\OPJ_exports\ tree already existed — nothing pointed at them, so nothing found them. Keith: *"Why that in the ROLD? Why d...
- S-13 · 2026-07-13 · GDX's drive letter was written as E: instead of X: and the wrong letter sat in the ROLD for a day
  **⚠ THE DRIVE LETTER IS X:, NOT E: — Keith corrected this 2026-07-13 and the wrong letter sat in this file for a day, sending scripts to a path that does not exist)**
- S-14 · 2026-07-13 · The Ch4-review publish stalled because [path] was not in the mount list
  Without this mount Cowork cannot publish, cannot read the bat, and has to hand Keith a RUN_ME_*.bat to double-click — which is exactly what stalled the Ch4-review publish on 2026-07-13.
- S-15 · 2026-07-15 · [path] cannot be mounted — the step had been failing at every BootUP since it was added
  **🔴 CORRECTION 2026-07-15 — [path] CANNOT BE MOUNTED EITHER.** The line above asks for it
- S-16 · 2026-07-15 · GDX mounts for Claude's file tools but NOT into the bash sandbox
  **🔴 ALSO 2026-07-15 — [path] Drive\BTS_SGH_Handoff (GDX) mounts for Claude's file tools but NOT into
- S-17 · 2026-07-15 · THE RAILS SECTION OF THE ROLD WAS FALSE ON EVERY ROW FOR TWO DAYS — and seeded a $299 phantom credit
  ### 🔴 THIS SECTION LIED FOR TWO DAYS AND COST HOURS. What it claimed vs what was MEASURED 2026-07-15:
- S-18 · 2026-07-15 · [K-96] — a mislabelled fit parameter, and a pointer that called it "THE ONE GATE" for three days after it was resolved
  ### ✅ [K-96] IS CLOSED. IT IS NOT A GATE. STOP LOOKING FOR IT.
- S-19 · 2026-07-15 · bts_identity.py shipped and appeared in NO index — the exact failure the TOOLS INDEX was created to prevent
  **No generator exists.** So obeying the instruction meant editing the JSON while the index silently
- S-20 · 2026-07-15/16 · Hardware and network topology was an item class with no home in any checklist
  1. **HARDWARE/NETWORK TOPOLOGY is an item class and was NOT on the checklist.** This session produced a
- S-21 · 2026-07-15/16 · Proposed moving 105 GB to fix a bottleneck that was somewhere else — Keith caught three of these, I caught none
  2. 🔴 **PRICE THE BOTTLENECK BEFORE MOVING THE DATA.** I proposed moving 105 GB of ODX to the NVMe
- S-22 · 2026-07-15/16 · TidyUP2 produced two false alarms out of four checks
  3. ⚠ **A VERIFIER THAT CRIES WOLF IS THE SAME BUG CLASS AS THE FUSE MOUNT.** TidyUP2 this session
- S-23 · 2026-07-16 · GEM named the right Google service but invented the path — a 404
  - ⚠ **VERIFY THEIR URLS/DOIS — never ship them.** 2026-07-16: GEM named the right Google service but
- S-24 · 2026-07-16 · Vertex billed 28.5× the visible output — and $0.0296 was paid for a question the free lane answers
  **MEASURED 2026-07-16 — the API punishes exactly what we want GEM for:** one 3-sentence Vertex
- S-25 · 2026-07-16 · A PUBLISH IS NOT A SYNC — the public mirror served a 15-day-old file and every verify returned 200
  1. 🔴 **A PUBLISH IS NOT A SYNC. Cloud-verify must diff CONTENT, not expect HTTP 200.**
- S-26 · 2026-07-16 · The sandbox held the ONLY copy of a delivered 2.7 MB deliverable's builder
  2. **SANDBOX SWEEP (T2-6) IS NOT BOOKKEEPING — it caught a real loss on its first real run.**
- S-27 · 2026-07-16 · TOOLS_REGISTRY.json claimed a generator that does not exist, so obeying it froze the index
  3. ⚠ **A DOC THAT CLAIMS TO BE GENERATED MUST HAVE A GENERATOR ON DISK — VERIFY, DON'T BELIEVE.**
- S-28 · 2026-07-17 · MOUNT HIT #11 — the mount lied about SIZE: under-reported by 39,584 bytes, and a divergence check returned a clean, specific, garbage answer
  **#11 — it lied about SIZE, not just content.** Comparing D: vs V: through the mount, jack_command.html
- S-29 · 2026-07-17 · MOUNT HIT #12 — a FALSE SyntaxError at line 106 nearly ate bts_paths.py, the resolver everything depends on
  **#12 — a FALSE SyntaxError in bts_paths.py, the resolver everything depends on.** The sandbox reported
- S-30 · 2026-07-17 · The migration's code/history split ate the file that exists to survive the sweep
  1. 🔴 **THE CODE/HISTORY SPLIT WAS DRAWN AT THE FILE LEVEL. FILES ARE BOTH.**
- S-31 · 2026-07-17 · A handoff recorded backup_to_onedrive.py as "Patched." It was not — on either tree
  2. 🔴 **A HANDOFF THAT RECORDS A FIX NOBODY VERIFIED IS WORSE THAN ONE THAT RECORDS THE BUG.**
- S-32 · 2026-07-17 · A migration rewrote a broken path into a differently-broken one; Win32_SystemSlot reported all 7 PCIe slots free including the one holding the GPU
  3. ⚠ **A MIGRATION CAN REWRITE A BROKEN PATH INTO A DIFFERENTLY-BROKEN ONE.**
- S-33 · 2026-07-17 · SGH fabricated the Au 5d citation 10.1002/adma.201906478 — and five documents then spent four days telling the next session to "replace" a citation that was never inserted
  3. ✅ **SGH's Au 5d citation — CLOSED-OUT 2026-07-17. THE GUARD WORKED; THE TODO WAS THE BUG.**
- S-34 · 2026-07-19 · A node's DOI can be REAL while its title is FABRICATED
  1. 🔴 **A NODE'S DOI CAN BE REAL WHILE ITS TITLE IS FABRICATED.** GEM/SGH handed back 10.1103/PhysRevB.20.4126
- S-35 · 2026-07-19 · A sub-agent cannot read its host/parent session's transcript
  2. 🔴 **A SUB-AGENT CANNOT READ ITS HOST/PARENT SESSION'S TRANSCRIPT.** session_info lists children and the
- S-36 · 2026-07-19 · An OAuth "deleted project" claim was carried forward on faith for days and was false
  3. ⚠ **AN OAUTH "DELETED PROJECT" CLAIM DECAYS LIKE A STALE POINTER — RE-TEST, DON'T INHERIT.** The GDX project
- S-37 · 2026-07-20 · THE DATED-HANDOFF SCHEME ROTTED FOUR TIMES — the glob returned 15 files across two directories
  **Why:** the dated scheme rotted **FOUR times** (12c→12d, 12d→07-15, →07-17, and on 2026-07-20 this line
- S-38 · 2026-07-26 · "I called GEM and Vertex dead. They were not." — the sandbox's own egress block read as dead keys
  **1. I called GEM and Vertex dead. They were not.** Every googleapis.com host returned HTML 403
- S-39 · 2026-07-26 · SANDBOX NONDETERMINISM — 23 scans over threshold / worst 4.998 eV on the first run, 7 / 3.680 on the next four. Same code, same data.
  **2. I reported the archive's own recorded numbers as "not reproducing".** sec_prep.py gave
- S-40 · 2026-07-26 · "VERTEX DEAD" was recorded THREE TIMES on the strength of a wrong auth header
  bts_vertex.py sends **x-goog-[credential]I key. My probe sent
- S-41 · 2026-07-26 · The rail check's own first run cried wolf — the probe truncated the model list at 400 bytes
  Also fixed: the check's own first run cried wolf, reporting grok-build-0.1 MISSING because the
- S-42 · 2026-07-26 · The daily rail-health task was blind for seven days because its connected-folder set is not a file anyone can edit
  **The rail check no longer needs a mount.** The Cowork task free-tier-allotment-check was blind for
- S-43 · 2026-07-26 · "GDX blocked, needs re-auth" was too broad — one of three paths was down and I wrote it as all three
  **"GDX blocked, needs re-auth" was too broad and I wrote it.** Nothing Cowork does is waiting on
- S-44 · 2026-07-26 · Every doc in the tree called GW browser-only. It was one free GET /v1/models away.
  **GW is an API model.** Every doc in this tree called it browser-only or a PowerShell CLI; it was one
- S-45 · 2026-07-27 · A literature sweep run without a verification step had a 100% citation failure rate
  🔴 **THE VERIFICATION GATE IS NOT CEREMONY — measured 2026-07-27.**
- S-46 · 2026-07-27 · Five defects the headless GUI suite caught that no linter could — including 2 eV lost between the screen and the arithmetic
  1. **The displayed bias never reached Φ.** _load pushed the seeded voltage to the slider only.
- S-47 · 2026-07-27 · The outside review found real physics bugs while 143 tests and 26 invariants were green — binding_energy() omitted the bias
  1. **binding_energy() OMITTED THE BIAS.** BE = (hv − E_an) − KE, missing + V. A biased sample
- S-48 · 2026-07-27 · GEM argued one finding confidently and it was simply wrong — and reported NO FINDINGS on the file holding the real bug
  ⚠ **GEM produced one confidently-argued finding that was simply wrong** (claimed
- S-49 · 2026-07-27 · GEM's auth: two of three options dead, and the real blocker was one key in settings.json
  | option | result 2026-07-27 |
- S-50 · 2026-07-27 · Six defects in the fitting layer — an unweighted Poisson fit, a defensible gate that passed redchi = 4,000, and four more
  * **fit_peaks fitted UNWEIGHTED.** Photoemission is a photon count, so the noise is Poisson;
- S-51 · 2026-07-27 · The adversarial re-verification found the worst bug of the session — v_applied or 0.0 reproduced the impossible Φ = 7.12 eV the archive already had a name for
  **Ruling.phi() ended - (self.markers.v_applied or 0.0).** A bias nobody had established
- S-52 · 2026-07-27 · The courier architecture was designed around an absence that nodes/gbw.json had already denied
  nodes/gbw.json has said this since before 07-14: *"Two legs — (1) chat-worker window via
- S-53 · 2026-07-27 · THE FORGE — 204 node calls produced output that failed 3 of 4 gates, and FORGE.bat double-launched and was still clobbering restored files an hour later
  5 rounds, 204 node calls, 0 rail failures, ~23 min. **Its output failed 3 of 4 gates** — 85 ruff
- S-54 · 2026-07-27 · GEM issued a FALSIFIED verdict from a premise it had itself marked [UNVERIFIED], and its predicted mechanism did not reproduce
  **Rejected after measurement:** GEM's *"lmfitxps is passive-only, do not adopt"* — ShirleyBG and
- S-55 · 2026-07-28 · COWORK FABRICATED A QUOTATION AND ATTRIBUTED IT TO GEM — and manufactured a three-way agreement that never existed. Keith caught it from a single word, two days later.
  ## 🔴🔴 RETRACTED — "THE DECISION, REACHED THREE WAYS INDEPENDENTLY" WAS NOT.
- S-56 · 2026-07-28 · An MCP server was built that reimplemented 7 of bts_tools.py's 8 verbs — the 07-13 Origin-reader failure repeated exactly, five days after the index was created to prevent it
  🔴 **PROVEN AGAIN 2026-07-28, AND THIS TIME BY SKIPPING THIS VERY STEP.** A session that never
- S-57 · 2026-07-28 · bts_tools.edit(count=-1) called str.replace(old, new, 0) — a silent no-op that reported success, live since 07-17
  **CONSOLIDATING IMMEDIATELY PAID FOR ITSELF — a live bug fell out of it.**
- S-58 · 2026-07-28 · bts_tools._guard confinement was a SUBSTRING test, so C:/evil/tmp/x passed
  **Also fixed in bts_tools._guard: confinement was a SUBSTRING test**, so C:/evil/tmp/x
- S-59 · 2026-07-28 · fs_write threw IntegrityError on every write on Windows — text-mode open() translates \n to \r\n
  **THE SANDBOX SUITE WAS GREEN AND WINDOWS STILL FOUND THREE BUGS. All three were OS-shaped.**
- S-60 · 2026-07-28 · Grok's config.toml was CORRUPTED on the second wiring run — re.sub processes escapes in the replacement
  2. **Grok's config.toml was CORRUPTED on the second wiring run** — re.sub processes escapes in
- S-61 · 2026-07-28 · GEM registered the MCP server but refused to START it — security.folderTrust.enabled defaults true and the per-server trust flag does not bypass it
  3. **GEM registered the server but refused to START it** — security.folderTrust.enabled defaults
- S-62 · 2026-07-28 · A console in QuickEdit selection mode SUSPENDS the process, and it looks exactly like a hang. The title bar read Select.
  🔴 **JUDGE.bat CAN FREEZE upsjudge AND IT LOOKS EXACTLY LIKE A HANG — measured 2026-07-28.**
- S-63 · 2026-07-28 · CoP was written off on a premise that expired — five days of a dead lane, and the "do not re-test" note was the thing keeping it dead
  1. 🔴 **A "DO NOT RE-TEST IT" NOTE INHERITS THE LIFESPAN OF THE FACT UNDERNEATH IT.** BU.MD said
- S-64 · 2026-07-28 · A launcher that prints "LAUNCHED" is not evidence anything launched — FANOUT_UI.bat v1: neither node ran
  2. 🔴 **A LAUNCHER THAT PRINTS "LAUNCHED" IS NOT EVIDENCE ANYTHING LAUNCHED.** FANOUT_UI.bat v1
- S-65 · 2026-07-28 · setx PATH "%PATH%;…" is destructive — it truncates at 1024 chars, silently
  3. 🔴 **setx PATH "%PATH%;…" IS DESTRUCTIVE — never use it.** It **truncates at 1024 chars**
- S-66 · 2026-07-28 · hv_judged was added to to_json and not to from_json — written to disk, quietly dropped on read
  5. 🔴 **ADDING ONE FIELD TOUCHES FOUR SERIALISATION POINTS, AND MISSING ONE IS SILENT.**
- S-67 · 2026-07-28 · The RULING_COLUMNS append-only invariant was written wrong TWICE — both versions forbade the very thing append-only means
  6. ⚠ **DO NOT OVER-SPECIFY AN APPEND-ONLY INVARIANT.** The RULING_COLUMNS guard was written
- S-68 · 2026-07-28 · GEM reported its prototype "compiles and runs flawlessly (Exit Code: 0)" having executed only py_compile
  7. ⚠ **A PARSE CHECK IS NOT A RUN — including when a NODE claims otherwise.** GEM reported its
- S-69 · 2026-07-28 · Bare python on this box is 3.13 with no pytest — and _pyver_probe.log had already recorded it on 07-27
  - *(Also recorded, environment-specific:)* bare python on this box is **3.13 and has no
- S-70 · 2026-07-28 · 55 LF-only line endings and 12 non-ASCII bytes in this project's .bat files produced measured mojibake
  **1. RUN_TESTS.bat failed tests\test_launchers.py** — 55 LF-only line endings and 12
- S-71 · 2026-07-28 · srdata.nist.gov returns HTTP 200 for EVERY path including nonsense — the 401-vs-404 endpoint test is useless against it
  And **srdata.nist.gov returns HTTP 200 for EVERY path** including
- S-72 · 2026-07-28 · A session ran four streams in one context and degraded badly by the end
  A session that touches rails, physics, tooling and prompt-discipline in one context degrades
- S-73 · 2026-07-29 · Keith's screen was taken ~30 times in two days — every test run a 95-second round trip while he was working
  **NO Run dialog. NO computer-use launches. NO cmd /k.** Rule 2 restated as a hard boundary
- S-74 · 2026-07-29 · The R2 publish took 16 minutes to transfer ZERO bytes — 87 rclone invocations, 970.3 s
  🔴 **AND THE LOG ANSWERED "WHY IS R2 SLOW" WITH A NUMBER: 16 MINUTES TO TRANSFER ZERO BYTES.**
- S-75 · 2026-07-29 · There are TWO 00_WORKING directories and four bats write to the unpublished one — four reports reached nobody
  ⚠ **T2-1: THERE ARE TWO 00_WORKING DIRECTORIES AND MY BATS WRITE TO THE UNPUBLISHED ONE.**
- S-76 · 2026-07-29 · BU_RAILS.MD — a live pointer to a file that was NEVER CREATED, under a stream name Keith had already killed
  ⚠ **STALE POINTER, FIXED 2026-07-29.** This line used to say the borrowing gets a line in
- S-77 · 2026-07-29 · ~$500 over on usage credits in one month running Fable uncapped — discipline alone did not hold
  **Two pools, and they are NOT the same thing.** Max-plan usage (5-hour + weekly windows) costs
- S-78 · 2026-07-29 · Cowork hand-coded for a whole session with three paid rails untouched — and it felt like thrift
  - ⚠ **A PAID RAIL SITTING IDLE IS THE FAILURE, NOT THE SAVING.** Keith, 2026-07-29: *"I can't pay
- S-79 · 2026-07-30 · A pointer relocation took four edits across three files — miss any one and BootUP silently reads stale state
  1. 🔴 **A POINTER RELOCATION MUST BE VERIFIED FROM THE READER'S SIDE, NOT THE WRITER'S.** Moving the
- S-80 · 2026-07-30 · Cowork's own session storage is walled off from Cowork — any plan depending on it reading its own transcript is unbuildable
  2. 🔴 **COWORK'S OWN SESSION STORAGE IS WALLED OFF FROM COWORK.** request_cowork_directory on

## Occupancy table
- **Two heads** — 37 occupancy commits vs 189 Gitur main. CCr wrote LiT *and* Gitur wrote GitHub. — LiT **is** origin/main. origin/main..HEAD ≠ 0 → WARN ×3. Gitur only. CANON_ONE_HEAD.md
- **Two pens** — 716fbaea wrote cosmos/ after pen passed to f47bad79. Lease in the TUI ≠ disk ACL. — CAM holds write key. Agents never get S: R/W. Fencing on the **resource**. DEFINE_CAM_SAFE.md
- **Zombie grok.exe** — 112× grok --single MOTIF clones. Empty Output. Token leak. — Runner: WARN ×3 then **do not spawn**. WD2 drives MOTIF. #578
- **Concat CTX** — 35 NEVER RAN ( ·  string / missing SOP.md). — CTX is a **list**. Spawn refuse.
- **FAIL terminal** — 157 corpses. No partner, no judge, no attempt 2. n_total looked like work. — JSONL attempts. wo_partner. Board = bucket+picked. File away, don’t throw away.
- **Judge on empty WOMB** — Qwen Max 907k write, 5 min TTL, **$2.31**, then gone. New judge prefixes. — One Judge/run. If cache dead and n_board < 20, **leave**.
- **As-is retry** — Retrying empty WOs would re-fire grok. — (1) prove full or (2) restate + two GAC + new prompt.
- **Squash clobber** — #570/#577 delete working main files (1127-del stagehand). — WARN ×3 if PR deletes more than it adds on a live file. Grade dups. Don’t squash.
- **cd /d in PowerShell** — Reset never ran; git not in repo. — WARN: cd [path]
- **Placation** — (older) docs/SCAR_PLACATION.md — Claim ≠ evidence. Runtime binding.
- **Muse chamber** — Duplicate POST, truncated diff, invented occupancy. — STYLES/muse.md append.
- **DS :free essay** — Fat cache hit, first line not NONE. — STYLES/deepseek-v4-flash.md.
- **Hunk drift** — 104 grade hunks do not git apply on the current file. — Stale hunk is not code. Refresh the base. CURSOR-001.
- **Patch of missing** — cosmos/cosmos_rolled.py patched, file absent. — Missing path = new file, not a patch. CURSOR-002.
- **Symlink as code** — mode 120000 body is ../../ui. — Drop before 4Cs. Not a code copy. CURSOR-003.
- **Checker blames tree** — Patched file fails ruff/mypy the base already fails. — Score the delta, not the whole file. SET4C-001.
- **Pytest isolation** — 173 pytest fails; one re-measured as missing ui/app.js in a temp dir. — cDeck pytest needs the UI tree. Not a coder scar. SET4C-002.
- **Not a set** — 108 jobs, 0 triples, 0 with three passing copies. — No grade row until 3 code arms pass 4Cs. No Judge. SET4C-003.

## DailyScar notes
### 09-22-60-SCAR.md
1. **429 is a queue, not a corpse.** Rate-limit / Resource exhausted must sit in retry/waiting until the meter has room. Mapping it to APIError kills the turn.
2. **Sanitized lastError lies.** OpenWork strips the 429 body. Quote the vendor string (“Resource exhausted… cloud.google…/vertex”) or you will call it a generic provider fail.
3. **A green ping is not that tab.** COSMOS Express pings (Joanna last4 [redacted], Kelly last4 [redacted]) can be OK while the OpenWork chip is a different key. Measured draw: OPENWORK_GOOGLE_KEY_NAME=[redacted], last4 **[redacted]**. Not in the five-file vault.
4. **Fat transcript is load.** Hundreds of messages on 3.8 Flash is TPM/RPM even when a 1-token ping is green. Queue still; do not confuse “wallet dead” with “this request is too big right now.”
5. **Do not print keys.** last4 + key name only.

### 09-23-COLLECTION.md
- **09-22-60** — Vertex Resource exhausted → APIError — Fat OpenWork tab (3.8 Flash) died instead of **queueing**. lastError sanitized. — 429 queues. Never a corpse. 09-22-60-SCAR.md
- **Ping ≠ tab** — Joanna/Kelly Express pings GREEN — OpenWork chip was **[redacted] last4 [redacted]**, not vault [redacted] / [redacted]. — Quote the bound key name. A 1-token ping is not that transcript.
- **No five-todo list** — Prefork “five todos” — Disk had Keith items **3–5 only**. TU2 caught it. — Claim vs transcript search. Don’t invent a list.
- **Lease JSON** — Fork held the pen in prose — CCR.lease still prefork sid until release+acquire. — Never hand-edit the lease. Arbiter only.
- **OW_POST** — TICKs SQLite-injected into the hot tab — Preempted the pen; turned **off**. — File TICKs. Don’t inject OpenWork.
- **Cursor quota burn** — Website Builder ~100+ cloud agents — 2026-09-14 stop order. Draft PRs, not live sites. — No retask loop on a metered agent farm. Closeout under WEBSITES\.
- **xAI 200k / 2×** — Fill the window because MAX allows it — Grok bills 2× above 200k. Cheaper to **new session**. — Keep PREFIX+ITEM under 200k. Resession warn at 65% (130k).
- Scar — Avoid
- **Two heads** — LiT is origin/main. Don’t dual-write Gitur + TUI.
- **Two pens** — One CCR.lease. CAM holds write.
- **Zombie grok.exe** — WARN ×3 then **do not spawn**. No extra grok --single.
- **Concat CTX** — Context is a **list**, not a middle-dot string.
- **FAIL terminal** — Corpses on the board. File away; partner + attempt 2.
- **Judge on empty WOMB** — If cache dead and n_board < 20, **leave**.
- **As-is retry** — Don’t re-fire empty WOs. Prove full or restate.
- **Squash clobber** — WARN if a PR deletes more than it adds on a live file.
- **cd /d in PowerShell** — Wrong shell. cd [path]
- **Placation** — A claim of compliance is not compliance. Quote the artifact, never the intention. — docs/SCAR_PLACATION.md
- **Green rc, dead worker** — cosmos_runner.py as a script: rc=0, no daemon, slot stays dead. — docs/SCAR_RUNNER_RESPAWN.md
- **Timeout = absence** — Time-boxed search reports 0 when it ran out of clock. — ROLD S-151
- **Gates test the file, not the pointer** — Suite green; registered path dangling. — ROLD S-153
- **Stuck-mic / runaway loop** — Always-on paid loop without a kill + spend breaker. — ROLD 2026-08-25
- **Asserted without checking** — “Not possible” / “GUI-only” before research. — same
- **Self-reported capability** — Agent said it could write Drive; stale auth. Don’t trust the mouth. — ROLD S-04
- **Mount lie** — Read a truncated/corrupt view and “fix” a file that was never broken. — ROLD S-05–S-07
- This folder: [path]
- Occupancy table: [path]
- Append-only ledger: [path] (never rewrite an entry)
- Website burn: [path]

## Recovery ground
- P:\ holds sweep-recovery, a 2026-08-17 recover tree, and a mirror. The site may say the record was rebuilt from disk, not from memory.
- Session notes on the Ai tree record truncated files, mounts that lied, and workers that reported success while the slot stayed dead.
