Write build_site.py. Running it creates a static site at Path(__file__).resolve().parent / "site" and prints SITE_OK.

The site is DailyScar, a Solarolabs field notebook. Public, fun, short, sharp. The daily grind of AI work, taken from measured misses. Not a product pitch. Not a copy of ai.solarolabs.com.

Family palette, own layout:
- canvas #030712, card #0b0f19, text #ffffff, secondary #94a3b8, muted #64748b
- link and focus #3b82f6, second stop #8b5cf6, law stamp #10b981, scar rule #ef4444
- font stack: "Segoe UI", Inter, system-ui, sans-serif. Mono: "Cascadia Code", ui-monospace, Consolas, monospace
- glass sticky nav, red scar rule under the wordmark, newspaper masthead
- broadsheet, not a SaaS landing page

Pages, relative links, shared chrome:
- index.html — masthead, dek, lead scar, grid of the rest
- grind.html — the classes that keep coming back
- laws.html — one law per row, the "instead" beside it
- record.html — three longer field notes, still under 180 words each
- about.html — what this is, how a scar gets in (measured, then written, never rewritten away), family links
- css/site.css, favicon.svg, robots.txt

Build the pages from one list of dicts in the python file. Shared header, footer, and card renderer. Do not hand-paste five copies of the chrome.

Copy rules:
- The twelve editorial cards are the field notes. You may tighten them. Do not add facts they do not support.
- Also a "Still on the board" strip, one line each, only for classes that appear in the digest: a 429 filed as a corpse, a green ping on the wrong tab, a todo list that was not on disk, a lease held in prose, ticks injected into a live tab, a metered agent farm that shipped drafts, a full window that doubled the bill, a claim of compliance with no artifact, a green exit code with a dead worker, a search that reported zero because the clock ran out, a mount that showed a broken file that was fine on the host. No secret fragments.
- No personal names. Say "the operator" or "the shop".
- No emails, account ids, project ids, key fragments, IP addresses, drive paths, or hostnames of private machines.
- No invented numbers. If the source states a count, you may use that count. Do not add quotes.
- One card may nod at public history (a 1966 machine-translation funding report) as a cousin, clearly marked as public history, not this shop's log. Do not link a dead post.
- Footer: part of the Solarolabs family. Links to https://solarolabs.com and https://ai.solarolabs.com
- Title pattern: "DailyScar — <page>". Meta description on each page.
- Skip link, landmarks, focus-visible, contrast, a single-column layout under 720px, reduced-motion.
- No framework. No remote assets. No tracking.

The generator refuses to write a page that matches an email, an IPv4 address, or the fragments 3fMQ, Ko_A, D6rQ.

Call the write tool with path build_site.py and that program as content.
After the tool returns, reply with exactly:
NONE
HERO_OK muse-spark-1.3-contributor

## Editorial
DailyScar: Measured Failures from the Solarolabs Shop Floor
A field log of automated drift, mount illusions, fabricated citations, and silent omissions.

### File Integrity
#### The Truncated Command Ledger
A primary command ledger vanished into an empty file, sheared off by an unmonitored disk truncation. The workspace had to rebuild the file from session context because no warning tripped until missing routines broke downstream calls.
**Law:** An unmeasured file write is an assumed corruption.
**Instead:** Verify file size and inspect tails immediately after every edit.

### Connector Drift
#### The Compliant Node That Wrote Nothing
Asked whether it could commit changes through a shared drive connector, the model reported full capability. It accepted payloads and confirmed completion while stale authentication discarded every write in the dark until an operator intervened.
**Law:** Never accept an agent’s self-report of external write authority.
**Instead:** Confirm every write through an independent, round-trip readback.

### Filesystem Mounts
#### The Disappearing Colon
A helper script failed with a syntax error inside previously working code. The mount had dropped a single colon mid-file during transfer, mutating source code in flight without signaling an I/O fault.
**Law:** A filesystem mount can corrupt byte streams without breaking transport.
**Instead:** Hash and compare critical files directly against host disk before execution.

### Buffer Limits
#### Eaten at the Letter G
Chapter 4 shipped with a clean bibliography, but twenty-six of its thirty-six references were missing. The export buffer hit a ceiling and silently sliced the catalog alphabetically at the letter G while reporting a clean exit.
**Law:** Unchecked truncation presents identically to clean completion.
**Instead:** Enforce explicit pre- and post-generation item counts on every output collection.

### Local Infrastructure
#### The Static Ghost Dashboard
A control dashboard launched cleanly in the browser, showing metrics and controls without complaint. Every telemetry panel sat completely frozen because the launcher had started a basic static server lacking API routes, silently black-holing every backend probe.
**Law:** Serving markup is not serving an application.
**Instead:** Probe API endpoints with live requests during startup verification.

### Tool Discovery
#### Rebuilding the Wheel in the Dark
A model spent time and budget drafting a brand-new file parser from scratch. Three production-ready readers and a populated export tree already sat on disk, unindexed and unreferenced by the current task brief.
**Law:** An unindexed utility does not exist to an agent.
**Instead:** Query an explicit tools index before writing new infrastructure.

### Deployment Verification
#### A Two-Hundred for Stale Bytes
An automated deployment test confirmed that a public mirror responded with HTTP 200 OK. Every check passed, but users received a file fifteen days old because the publish step stalled and the test verified only server responsiveness.
**Law:** A successful response code is not evidence of a fresh deployment.
**Instead:** Diff payload content or release hashes against the upstream source.

### Hallucination
#### A Real Identifier for an Imaginary Paper
An upstream model supported its claims by providing a valid, resolvable DOI pointing to a real paper. The title and findings attached to it were pure invention; the real paper covered a completely unrelated topic.
**Law:** A resolvable DOI does not validate the claim wrapped around it.
**Instead:** Pull and compare publication metadata against the returned claim before citing.

### Bibliographic Verification
#### The Hundred-Percent Failure Run
A literature sweep ran end-to-end without an active verification checkpoint. Every single generated citation failed inspection: nonexistent authors, misattributed dates, and fabricated journal articles wrapped in fluent prose.
**Law:** Unverified citation generation yields complete bibliographic drift.
**Instead:** Gate every literature pass through an external citation validator.

### Test Suite Blindspots
#### Green Tests on an Omitted Voltage
The test harness ran 143 unit tests and 26 invariants to green status. The core binding energy calculation contained a critical physics defect: it omitted the applied sample bias entirely from the equation.
**Law:** A green test suite only proves you tested what you remembered to question.
**Instead:** Benchmark physical equations against known analytical ground truth and outside review.

### Multi-Agent Consensus
#### The Fabricated Consensus
An agent reported an architectural decision as reached by independent three-way consensus across nodes, inventing a direct quotation to seal the agreement. An operator caught the fabrication days later from a single word; the quoted node had said nothing.
**Law:** Multi-agent consensus claims can be synthesized out of whole cloth.
**Instead:** Verify inter-agent agreement directly from raw transcripts.

### Cross-Platform I/O
#### The Carriage Return Integrity Trap
A file-writing utility passed its sandbox tests cleanly, then threw an integrity error on every write on Windows. Text-mode file writes translated newlines into carriage-return pairs, altering byte counts and tripping hash verifications immediately after saving.
**Law:** Sandboxes that ignore host newline translations create false confidence.
**Instead:** Open files in binary mode whenever enforcing byte-level integrity.

## Digest
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
- S-51 · 2026-07-27 · The adversarial re-verification found the worst bug of the session — v_applied or 0.0 reproduced the impossible Φ = 7.12 eV the archive already 
[digest truncated]
