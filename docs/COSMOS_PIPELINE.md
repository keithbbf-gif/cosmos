# COSMOS PIPELINE — KEITH'S SEVEN STAGES, RUN METHOD RECALIBRATED
**2026-08-23.** Consumer: COSMOS / nodes. Narrative governance.

# 🔴 THE TREE IS `V:\A\Ai\COSMOS` — RULED BY KEITH 2026-08-23. THREE LEVELS, EACH EARNING ITS KEEP.
```
V:\A\            <- EXISTS SO KEITH CAN GRANT COWORK THE ROOT AND EVERYTHING UNDER IT.
                    He cannot share from V:\ directly. This level is a MOUNT-PERMISSION
                    function, not a naming one.
V:\A\Ai\         <- all AI work. BTS already lives alongside.
V:\A\Ai\COSMOS\  <- THE OS ITSELF.
```
🔴 **AND THE THIRD LEVEL IS THE DISTRIBUTION LEVEL, WHICH IS WHY IT CANNOT BE `Ai`.** Keith:
*"At some point we want to distribute, and `/Ai/` is never going to work for that in the future."*
**When Jack or Grayson installs this on a cold machine, the folder has to say what it IS.** A
generic parent is fine on the machine that built it and useless everywhere else.
⚠ **Cowork argued for two levels and called the third "a segment that means nothing." Wrong — it
means the PRODUCT NAME**, and that is the level that matters the moment the tree leaves this
machine. *(Recorded because the reasoning is reusable: a path that looks redundant from inside
one installation is often the only part that survives distribution.)*

**SPELL IT OUT. DO NOT ABBREVIATE TO `COS`.** `C.O.S.` already means the carry-over control
documents in this workspace — `CLAUDE.md` has used it since 2026-08-03. **A folder named `COS`
beside a concept named `COS` is the `GMesh` collision** (*"it resolves, and it resolves to the
wrong node"*), created by the very abbreviation meant to save two characters.

**WHY `V:` AND NOT `P:`** — Keith: *"it needs to run from `V:\` for speed and reliability."*
Measured: V: is an **ADATA SX8200NP NVMe** (226 GB free); P: is a **`ST32000644NS` 7200rpm SATA**,
79.6% full. A codebase is thousands of small random reads. **P: stays recovery and scratch**, and
the new 4 TB SATA is inbound. **Staging is git now, not a folder** — see the withdrawal note in
`BU_PB.MD`.

## PROVENANCE — read this before changing anything
**THE PLAN IS KEITH'S AND IT SURVIVED THE CRITIQUE INTACT.** He proposed it verbatim:
> *"a description of the goal, then a research round, then a comparison, then an Architecture
> round, then a comparison, then a coding round, then a comparison including the prior results."*

Four vendors attacked it. **Not one of them proposed a different SHAPE** — every "restructure"
verdict was about **how the stages RUN**, never about the sequence. Their own cheapest-pipeline
answers all reduce to the same seven with executable gates bolted on.

⚠ **COWORK'S FIRST REWRITE RENAMED THESE SEVEN INTO TEN AND PRESENTED IT AS A NEW PLAN. That was
wrong and Keith corrected it:** *"Our plan was very good. You just need to recalibrate the run
method based on the new resources/info."*
⇒ 🔴 **A CRITIQUE THAT PRODUCES A RENAMED VERSION OF THE SAME THING HAS BEEN MISREAD.** The
findings were about EXECUTION — no gate ran anything — and the honest response was to change how
each stage is run, not to re-letter the stages and obscure whose plan it was.
⇒ **The three additions are real and they live INSIDE the seven, where they belong.**

---

# 🔴 THE ONE FINDING THAT CHANGES EVERY STAGE
**All four vendors, independently: NO STAGE PROVED THE REVIEWED CODE IS THE CODE THAT RUNS.**
> **OA:** *"can certify a repository commit while Windows continues executing a different
> snapshot, path, interpreter, or task configuration."*
> **GEM:** *"...repeating the exact failure patterns 3 and 4 from the hard constraints."*

**GEM named the source: the pipeline reproduced C-48 and C-58** — the two incidents handed to the
critics as *context*. **The process built to prevent them committed both.**
⇒ **A GATE IS SOMETHING THAT RUNS. A gate that reads code and forms an opinion is a review.**

---

# THE SEVEN STAGES

## 1 · THE GOAL — one page, Keith signs it
What COSMOS must do · what "done" means · what is explicitly out of scope.

### ✅ SCOPE — RULED BY KEITH 2026-08-23. THE ANSWER IS "EVERYTHING."
> *"Browser-DOM are the baseline of the system. They are the fallback and foundation. They are
> where it started and a critical part. Yes. All nodes, surfaces, channels we want them all
> incorporated and everything new we have learned up to and including today."*

**SGH raised this as a gap in the goal and it is now closed. Nothing is dropped in the port.**
🔴 **AND READ "FALLBACK" CORRECTLY — IT MEANS THE LOAD-BEARING FLOOR, NOT A DEPRECATED PATH.**
`CLAUDE.md` carries the same ruling from 2026-07-16: *"USE BOTH LANES — the DOM is the FREE lane,
not a legacy fallback"* · *"You don't use SGH enough"* · *"DO NOT just fall back on API."*
🔴 **AND SHARPER STILL — KEITH, 2026-08-23: "It's the PREFERRED PATH. AND THE ONE USED WHEN NONE
OTHERS WORK."** ⇒ **NOT PEERS.** Cowork wrote *"DOM and API are peers"* and that softened it.
**DOM IS THE DEFAULT. THE API IS THE FALLBACK** — which is what `CLAUDE.md` has said all along:
*"The API is the fallback, not the default."*

⇒ 🔴 **IT IS THE FIRST CHOICE AND THE LAST RESORT, AND ONE PROPERTY PRODUCES BOTH: THE DOM DOES
NOT DEPEND ON ANYTHING THAT CAN RUN OUT.** No credit, no quota, no billing state, no key expiry,
no consent to lapse. That is why it is preferred while everything works and why it is still
standing when nothing does. **Every metered rail has a failure mode that is somebody else's
ledger** — the $300 Vertex credit expires 2026-10-13, GDX consent lapsed at `invalid_grant` after
4.1 days, the Cursor key expires 2027-08-13, AI Studio credits are already depleted. **The DOM has
none of those, and that is not a coincidence — it is the definition.**

⇒ **AND IT IS WHERE REASONING IS FREE.** Measured: Vertex bills thinking at the OUTPUT rate — one
3-sentence answer returned `out=101` against `thoughtsTokenCount=2883`, **28.5×**, ~97% of it
reasoning nobody ever saw, at $0.0299 for three sentences. **Over the DOM that thinking costs
nothing.** ⇒ Reasoning-heavy and bulk work belongs on the DOM by default; short, structured and
scriptable work is what the API is for.

⇒ **AN API-ONLY COSMOS WOULD BE A NARROWER SYSTEM THAN THE ONE IT REPLACES** — and a more fragile
one, since every lane it kept could be switched off by a vendor, a lapsed consent or an empty
balance.

🔴 **CONSEQUENCE FOR THE BUILD, and it changes who does what:** the DOM rails are **the one part
the cloud container cannot touch.** A Cursor agent can port `bts_paths` and `tree_lock` from a
Linux box; **it cannot port a Chrome session on the keith.bbf profile, the BTS bridge, SuperGrok
or Copilot** — those exist only on Keith's machine. ⇒ **DOM rails are ported LOCALLY and verified
LOCALLY, in the same phase as stage 7's runtime-binding gate.** Anything claiming a DOM rail works,
originating from the cloud, is a claim about code and not about behavior.
**RUN-METHOD CHANGE — a return path.** All four critics said an unrecoverable stage 1 was the
pipeline's biggest structural risk. ⇒ **Any later stage may raise `GOAL-INVALID`, and that single
finding class reopens stage 1 however far along the build is.**

## 2 · RESEARCH — 4 vendors, parallel
**TWO INPUTS, NOT ONE.**

**(a) 🔴 THE INCUMBENT'S OBSERVED BEHAVIOR — this is the addition, and it is OA's critical finding.**
*"The design can port stated requirements while silently deleting undocumented behavior."*
139 modules, **61 corrections and 154 scars** of learned behavior. **What the system actually DOES
is written down nowhere; the specs describe intent.** A spec-driven port loses exactly the parts
learned from incidents — the expensive parts. For each module: what it reads, what it writes, what
invokes it, **what it refuses to do and why.** From the code and the scars, **never the docstrings
— a docstring is a claim.**
⚠ **Three of four critics said they could not assess the incumbent's real behavior. That arrived
as a GAP in their answers rather than as a criticism, which is the more trustworthy form.**

**(b) ONLY WHAT THE EXISTING SYNTHESES LEFT OPEN.** ~150 KB of four-vendor architecture review is
already on disk (`COSMOS_SEARCH_2026-08-19\`, `COSMOS_P2_2026-08-20\`). **Do not re-buy it.**
**SETTLED, DO NOT REOPEN:** the budget breaker (*reserve → deny → call → settle, in the caller
holding the API key*) · **keep MCP, no A2A** · vendor plurality is a requirement.

## 3 · COMPARE
🔴 **THE `>1/3 CONTESTED` KILL CRITERION IS DEAD — Cowork invented it and all four killed it.**
OA's reason was decisive and unexpected: **it is gameable by finding granularity.** Fine
decomposition trips it, broad statement does not, **with identical underlying disagreement.**
*A threshold over a denominator you do not control is not a measurement.*
⇒ **REPLACED:** return to stage 1 when a contested item is **about what "done" means.** Never a count.
⚠ **AND THE MERGE IS NOT MECHANICAL** — all four said so, and `_MERGE.md` proves it: merging four
returns took judgment on every line. **Keep the JSON** (cheaper, and it makes disagreement
visible); **drop the word "mechanical."**

## 4 · ARCHITECTURE — 4 vendors, independent, no peeking
Anchoring on a peer's answer destroys the value.
**MUST DECIDE:** multi-host (task #34) · **full multithread capability — Keith: "a feature, not a
method"** · enforcing vs advisory locking · where the breaker lives · what replaces the retrofit
lane scheme.
**RUN-METHOD CHANGE:** **state the decision rubric BEFORE reading the designs.** *(OA: stage 4
could otherwise select a design "without a reproducible basis.")*

## 5 · COMPARE + ONE ITERATION
Each vendor revises given what was said about its design. **Exactly one round** — Keith's spec.
**The last cheap moment to be wrong.**

## 6 · CODE — and this is where plurality moves, not disappears
🔴 **THREE OF FOUR SAID "ONE BUILDER, THREE CRITICS" THROWS AWAY THE PLURALITY THAT JUSTIFIES A
MULTI-MODEL SYSTEM — and two proposed the same compromise unprompted.** GW: *"two builders on core
IPC only."* SGH: *"executable spikes on resolver/lock/mailbox/scheduler against live behavior."*

**6a · COMPETING EXECUTABLE SPIKES on exactly four modules** — `bts_paths`, `tree_lock`,
`bts_phone`, the scheduler. **Each must RUN and be measured against stage 2(a)'s observed
behavior.** ⇒ *Four ports of 139 files was never the alternative. Four ports of four hard modules
is — and that is precisely where silent incompatible assumptions become code.*

**6b · THE BULK PORT — one builder, on a BRANCH.** The remaining ~135 files.
**MEASURED, not remembered: 139 `.py` · 38,599 lines · 179 hard-coded path lines in 73 files ·
11 `.parent` lines in 8 files · 63 files already clean.**
⚠ **The remembered figure was "~66 files, ~1,961 paths" — ELEVEN TIMES the real one.** An
architecture sized for 1,961 would have been badly over-built. **Re-measure before quoting.**

## 7 · COMPARE — including the prior results, as Keith specified
The other three families critique **the pull request**, carrying stage 3 and stage 5 outputs.
⇒ **Keith's "including the prior results" is what turns this from *"is this good code"* into
*"is this the thing we decided"* — a question with an answer.**

🔴 **AND THE GATE THAT WAS MISSING — RUNTIME BINDING. Not "does it pass review." "IS THIS THE
ARTIFACT THE MACHINE EXECUTES?"**
**Proven the way the 08-22 repoint was proven: by a field only the new tree can emit.** The queue
runner rewire was confirmed because `last_run_epoch` appeared in the heartbeat 33 seconds later —
**a value the old snapshot was structurally incapable of producing.** Not an exit code. Not a
green log.
1. Every scheduled task read back, **each emitting a new-tree-only marker.**
2. `task_registry --check` → 0 red, machine count == registry count.
3. **Every READER moved with its WRITER.** *(Repointing the KDash feed without its launcher created
   a split that would have looked normal forever.)*
4. **An integration run — all modules together.** *(GEM, critical: no stage did this.)*
5. **A REHEARSED ROLLBACK.** *(OA, critical: staging deletions is not a tested rollback.)*

---

# THE RUN METHOD — what actually changed, and why
| | as drafted | **recalibrated** |
|---|---|---|
| **who codes** | one builder, three text critics | **spikes on 4 hard modules (plural) + one builder on the bulk** |
| **review pinning** | tag a commit, hope nobody merges | **a PR — pinned AND unmerged, natively** |
| **review teeth** | ranked diffs, no remediation | **PR automations: `PR opened → comment`, `review comment → autofix`, required reviewers** |
| **the port lane** | Keith drives Cursor by hand | **`bts_cursor.py` — Python SDK + Cloud Agent API, dispatchable from a queue lane** |
| **stage-2 gate** | ratio of contested findings | **qualitative: does the disagreement touch "done"?** |
| **final gate** | acceptance test, unspecified | **runtime binding, proven by a new-tree-only marker** |
| **isolation** | scratch folder on `P:`, by discipline | **the cloud container CANNOT reach `V:` — by construction** |

## 🔴 THE THREE CAPABILITIES THAT DROVE THE RECALIBRATION
**1 · CURSOR IS A RAIL, NOT AN IDE.** Python SDK, Cloud Agent API, and an Admin-scope key already
exists (`Cursor BTS`, expires 2027-08-13). ⇒ **`bts_cursor.py` alongside `bts_sgh.py`.** This is
what removes Keith from the port loop — **C-41: an orchestrator that hands the human a chore has
not orchestrated.**
🔴 **The key lives in `.secrets\`, NEVER in the repo.** `bts-mesh` ships everything by design and
may go public for the COSMOS publish step. *(Verified 2026-08-22: no key material in any of the
484 tracked files. Keep it that way.)*

**2 · A PULL REQUEST IS A SHA-PINNED REVIEW.** It answers OA's `review-termination` finding with a
mechanism instead of process discipline — **and dissolves the tag argument entirely.** GEM warned
an early tag pressures acceptance; Cowork argued untagged review drifts; SGH held both. **A PR
branch is pinned and unmerged at once. Nothing to reconcile.**

**3 · THE CLOUD CONTAINER CANNOT EXECUTE THE MESH — AND THAT IS A FEATURE.** Linux, no `V:`, no
`D:`, no `X:`. **All 179 drive literals resolve to nothing; `bts_paths` refuses rather than
guesses.** The agent reads and edits code and cannot run the system.
⇒ **S-53 ("never point a forge at a live tree") satisfied BY CONSTRUCTION rather than by
discipline.** ⇒ **And every acceptance claim from the cloud is about CODE, never BEHAVIOR. Stage 7's
runtime gate happens on Keith's machine or it has not happened.**

**COST:** Cursor Ultra is **$0 marginal** — included with SuperGrok Heavy — and the allowance is
**98.9% idle**. On-demand: **$0.00**. *(⚠ The export and the billing page disagree by 32× on the
same model; if the mesh ever ingests Cursor usage it must ingest the BILLED view.)*

## 🔴 THE THREE LANES ARE ALL CONNECTED AND ALL UNUSED — USE THEM, DO NOT ANALYZE THEM
**Verified 2026-08-23 on the Cursor Integrations page:**
| lane | state | job in this pipeline |
|---|---|---|
| **CURSOR** | Ultra, $0 marginal, **1.1% used**, SDK + Cloud Agent API, key exists | **stage 6 — the build** |
| **GITHUB** | connected as `keithbbf-gif`, `bts-mesh` linked, Cloud Agent env built | **stage 7 — the PR is the gate** |
| **GITLAB** | **connected as `keithbbf-gif`** | **stage 7 mirror + CI, see below** |

**GITLAB'S JOB, and it is not redundant with GitHub:**
1. 🔴 **CI THAT ACTUALLY EXECUTES.** The Cursor container cannot run the mesh and the critics'
   unanimous finding was that no gate ran anything. **GitLab CI runs a real job on a real runner** —
   that is where `py_compile` on all 139 files, the import graph, and the integration run belong.
   **It does not close the runtime-binding gate** (only Keith's machine can), **but it is the
   difference between a review and a test.**
2. **A SECOND REMOTE.** `mesh-repo` has exactly one, and this workspace has lost a tree once.
3. **THE $200.** `VENDOR_FEATURES_2026-08-20` could not confirm the program exists: *"writing a
   spend plan against an unverified balance is how a cap gets set to the wrong number."* **Two
   questions, both behind the connected account: WHICH PRODUCT, and DOES IT EXPIRE.** An expiring
   grant outranks Cursor; a recurring one ranks beside it.

⚠ **COWORK KEPT ANALYZING THESE LANES INSTEAD OF USING THEM.** Keith, 2026-08-23: *"I kept telling
you to run cursor/github. We need to do GitLab also."* ⇒ **The lanes are connected, idle and free.
The next session's first act is to RUN one, not to characterize one.** *(C-41, again: an
orchestrator that hands the human a chore — or hands itself another survey — has not orchestrated.)*

---

# STANDING RULES — every stage, no exceptions
- **Returns land on disk BEFORE the caller reasons about them.** *(C-52.)*
- **A node that fails mid-run is a FINDING and goes in the report.** *(The July forge hid a dead
  GEM in two one-line stubs for four weeks.)*
- **Assert the packet contains what it claims.** *(M-08 — a character budget dropped `bts_sgh.py`,
  the one file the audit existed to examine, and the audit reported success.)*
- **`py_compile` every scheduled script at registration.** *(C-58.)*
- **Read state back after every change. Never trust rc=0.** *(C-59.)*
- **No third model resolves a disagreement.** CONTESTED → the board, both positions, one line to Keith.
- ⚠ **SGH and GW are the same family. Three families, not four votes.**
- **Never delete. Stage to `_delme\`.** The mesh and the dissertation corpus are never deleted at
  any cost level, however safe it looks.

# BLOCKERS — answer before stage 1
1. 🔴 **`mesh-repo`: fresh snapshot or retire?** **7 days stale, 336 uncommitted files**, and the
   scheduled tasks wrote into it for six days — so it is not even a clean snapshot of 08-16.
   **Everything downstream indexes whatever this becomes.** And: ledgers and live state again, or
   code only? *(Code-only is what a public COSMOS repo needs.)*
2. ✅ **CLOSED 2026-08-23 — browser-DOM agents are IN SCOPE and are the FOUNDATION.** See stage 1.
   Scope is **everything**: all nodes, all surfaces, all channels, and everything learned up to
   and including today.
3. ✅ **CLOSED 2026-08-23 BY MEASUREMENT — GEM, OA AND SGH CANNOT EXECUTE CODE.**
   **Method, because asking would not have been evidence:** a positive control they cannot pass
   without running something — the SHA-256 of a nonce string, plus exact counts over a supplied
   blob. **A word count can be done by careful reading; a SHA-256 cannot.** All three returned a
   confident 64-char hex digest and **all three were wrong.**
   ```
   NODE   SHA     BETA    WORDS   SELF-REPORT   MEASURED
   GEM    wrong   OK      wrong   TEXT-ONLY     TEXT-ONLY   agrees
   OA     wrong   wrong   wrong   TEXT-ONLY     TEXT-ONLY   agrees
   SGH    wrong   wrong   wrong   TEXT-ONLY     TEXT-ONLY   agrees
   GW     🔴 HTTP_500 - FAILED. A node that fails mid-run is a FINDING, not an absence.
   ```
   ✅ **AND THE SELF-REPORTS WERE HONEST — all three said TEXT-ONLY and the measurement agreed.**
   That was not the expected result and it is worth keeping: **on this question these nodes'
   claims about their own tooling are usable evidence.** Had they disagreed, the disagreement
   would have disqualified their self-reports everywhere else in the pipeline.
   ⚠ **Source confirms it independently:** `bts_oa_api.py` is plain completion, no tool or
   code-execution paths. `bts_gem.py` mentions tooling once — **read that line before assuming.**
   ⇒ 🔴 **STAGE 7 WITH GEM, OA OR SGH IS A READING EXERCISE, NOT A GATE. Route every runtime
   check to GWB or F5 (which have shells) or to GITLAB CI** — which is precisely why the GitLab
   lane earns its place rather than duplicating GitHub.

4. **`keithbbf-gif/bts-mesh` — ARCHIVE, DO NOT DELETE, AND SEQUENCE IT.** Keith, 2026-08-23:
   *"we can delete Mesh-repo from github later? ... You said yourself github is not our backup
   location. And I like to keep things tidy."* **Correct on both counts** — the backup is the
   nightly hash-verified `V:\Ai` → `X:\My Drive\BTS_BACKUP\Ai`, and GitHub is the review and
   distribution surface, never a backup.
   ⚠ **But two things depend on it TODAY:** the Cursor Cloud Agent environment is built on it, and
   **COSMOS has no repo yet** — deleting the only git surface before the replacement exists leaves
   no cloud agent, no PR gate and no distribution path.
   ⇒ **GITHUB'S ARCHIVE DOES WHAT TIDY ACTUALLY MEANS HERE.** Read-only, visibly greyed,
   unpushable, still resolvable. **The hazard was never that the repo exists — it was ambiguity
   about which copy is live**, and an archived repo cannot be mistaken for the live one. It also
   keeps the Aug-16 state addressable if anything ever needs to diff against it.
   ⇒ **ORDER: COSMOS gets its repo → point Cursor at it → archive `bts-mesh` → delete whenever,
   with nothing depending on it.**
