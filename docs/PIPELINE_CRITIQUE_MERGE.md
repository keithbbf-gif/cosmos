# PIPELINE CRITIQUE — THE MERGE
**4 of 4 vendors returned. 4 of 4 produced valid JSON. Total spend $0.0476.**
SGH 7.3 KB · GEM 7.8 KB · GW 5.3 KB · OA 11.4 KB (OA billed under its own plan, not itemized).

## VERDICTS
| node | verdict |
|---|---|
| **GW (xAI)** | **restructure** |
| **OA (OpenAI)** | **restructure** |
| **SGH (xAI/grok)** | **restructure** |
| GEM (Google) | adopt-with-changes |

⇒ **Three of four say restructure, not tweak.** The one dissent is the least severe, not a
different diagnosis — GEM raises the same critical finding as the other three.
⚠ **SGH and GW are the same family.** Counting them as two independent votes would overstate
the consensus. **The honest tally is: three families, and all three flagged the same critical
defect first.**

---

# 🔴 THE UNANIMOUS FINDING, AND IT IS THE ONE THIS SESSION SPENT ALL DAY ON

## **NO STAGE PROVES THE CODE THAT WAS REVIEWED IS THE CODE THAT RUNS.**

All four, independently, in four vocabularies:

> **OA** — *"The pipeline can certify a repository commit while Windows continues executing a
> different snapshot, path, interpreter, or task configuration."*
> **SGH** — *"False green: JSON consensus and a tagged commit while scheduled tasks still execute
> an old tree and checkers never actually run."*
> **GW** — *"No stage before the stage 5 commit requires any proposed change to execute against
> the live system."*
> **GEM** — *"Can ship a non-functional system that passes all gates because no stage actually
> executes the full, integrated application in a realistic environment — repeating the exact
> failure patterns 3 and 4 from the hard constraints."*

🔴 **GEM NAMED IT PRECISELY: THE PIPELINE REPRODUCES C-48 AND C-58.** I gave the critics those two
incidents as *context* — three scheduled tasks running a frozen snapshot for six days, and a
watchdog that had never executed — **and they turned around and found that the pipeline I designed
to prevent them commits both.** A tagged commit, four green reviews, and Task Scheduler still
pointing somewhere else.

⇒ **THE FIX IS A GATE THEY ALL DESCRIBE AND I DID NOT HAVE: RUNTIME BINDING.** Not "does the code
pass review" but ***"is this artifact the one the machine executes?"*** — proven the way tonight's
repoint was proven, by a field only the new tree can emit, not by an exit code.

---

# UNANIMOUS 4/4 — ADOPT WITHOUT FURTHER DEBATE

### 1. THE `>1/3 CONTESTED` KILL CRITERION IS DEAD
> **OA** — *"can be passed or failed by **changing finding granularity** without changing the
> underlying disagreement."*
> **GEM** — *"worse than no threshold because it provides a **false sense of mathematical rigor**
> for what is a qualitative judgment."*
> **SGH** — *"uncalibrated invention that **both false-kills good goals and false-passes bad
> ones**."*
> **GW** — *"arbitrary, no grounding in the listed incidents or constraints."*

⇒ **OA's is the killer argument and it is not the one I expected:** the ratio is **gameable by
splitting or merging findings**, so a vendor that decomposes finely trips the gate and one that
states broadly does not — *with identical underlying disagreement.* **A threshold over a
denominator you do not control is not a measurement.**
⇒ **REPLACED BY: a qualitative gate.** Contested items are *named and classified*; the pipeline
returns to stage 0 when a contested item is about **what "done" means**, not when a count is hit.

### 2. THE "MECHANICAL MERGE" IS NOT MECHANICAL
All four. *"Judgment re-enters at id assignment and granularity"* (SGH). *"Vendors decompose the
same defect differently"* (GW). *"Equivalent findings will often have different IDs and scopes"*
(OA). *"Requires human judgment to deduplicate semantically identical findings"* (GEM).
⇒ **MY STAGE-2 CLAIM WAS WRONG, and this very document is the proof — merging these four returns
took judgment on every line.** Semantic dedupe is the work, and it does not disappear because the
transport is JSON.
⇒ **KEEP THE JSON ANYWAY** — it made *this* merge far cheaper than four prose essays, and it made
disagreement visible. **Structured transport is a real saving; "mechanical" was the overclaim.**

### 3. STAGE 0 HAS NO PATH BACK
All four. With the kill criterion now gone, **there is no return path at all.**
⇒ **Every later stage may raise a `GOAL-INVALID` finding, and that one class reopens stage 0
regardless of how far along the build is.**

---

# MAJORITY 3/4 — ONE BUILDER, THREE CRITICS
**GW critical · OA major · SGH major · GEM minor.** Unanimous in direction, split on severity.
> **GW** — *"discards the vendor plurality that is the stated justification for the multi-model
> system."*
> **OA** — *"One builder is tractable, but **three post-hoc textual critics do not restore
> implementation diversity** or independently validate its assumptions."*
> **GEM** — *"single point of failure and a significant knowledge silo."*

⇒ **AND THEY CONVERGED ON THE SAME COMPROMISE WITHOUT BEING OFFERED IT:** GW proposes *"two
builders on core IPC only,"* SGH proposes *"executable spikes on resolver/lock/mailbox/scheduler
against live behavior."*
⇒ **ADOPTED: plurality where the assumptions live, one builder for the bulk.** The resolver, the
lock, the mailbox and the scheduler get **competing executable spikes**; the other ~130 files get
one builder. **Four ports of 139 files was never the alternative — four ports of four hard
modules is, and that is where silent incompatible assumptions actually become code.**

---

# SINGLETONS WORTH ADOPTING — nobody else said these, and they are right

**OA · `no-incumbent-characterization` (critical)** — *"The design can port stated requirements
while **silently deleting undocumented behavior** of the live BTS_MESH system."*
⇒ 🔴 **The sharpest finding in the set.** 139 modules, 61 corrections and 154 scars of accumulated
behavior, and the goal document describes *intent*. **What the system actually does is not written
down anywhere, and a port against the spec loses exactly the parts nobody documented — which are
disproportionately the parts learned from incidents.**
⇒ **NEW STAGE: characterize the incumbent BEFORE designing.** Capture observed behavior, not
stated behavior.

**OA · `rollback-and-recovery` (critical)** — *"Staging deletions protects against one class of
loss but does not provide a **tested rollback** for a bad migration, registry change, task update,
or mailbox change."* ⇒ Correct, and it is a gap in the whole mesh, not just the pipeline.

**OA · `candidate-tag` (major)** — a tag must be **explicitly a mutable candidate** and
unmistakable for a release artifact. ⇒ Cheap, adopt.

**GEM · `missing-integration-test` (critical)** — no stage integrates all 139 modules and runs
them together. ⇒ Adopt; it is the executable half of the runtime-binding gate.

**GEM · `one-builder-ossification` (major)** — *"Committing before critique creates immense social
and technical pressure to accept the builder's work, flaws and all."*
⇒ ⚠ **This DIRECTLY OPPOSES my SHA-pinning argument, and SGH holds both sides:** *"critiques must
pin a SHA — untagged review ossifies nothing and allows silent drift, **but early tag without a
runtime gate ossifies wrong code**."*
⇒ **CONTESTED → RESOLVED BY SGH's OWN FORMULATION: tag, but tag as `candidate/*`, never `v*`, and
the tag confers no status until the runtime-binding gate passes.** Both concerns are real and the
resolution satisfies both.

---

# WHAT THEY COULD NOT ASSESS — recorded, per the rule
- **GEM & OA:** whether the critic models can **execute code and run probes**, or only read text.
  ⇒ 🔴 **This determines whether stage 6 is a real gate or a reading exercise. ANSWER IT BEFORE
  RELYING ON IT** — GWB and F5 have shells; GEM and OA over the API do not.
- **SGH:** the real hard-coded path count, the actual task→module map, whether **browser-DOM
  agents are in scope for the port.** ✅ *The count is now measured — see below. The DOM scoping
  question is open and is a genuine gap in the goal.*
- **GW:** whether the live tree can be observed or copied by external vendor sessions **without
  tripping the watchdog or the scheduled tasks.**
- **OA:** the scheduled-task definitions, the deployment mechanism, current acceptance tests, and
  the incumbent's behavioral contracts.

⇒ **THREE OF FOUR SAID THEY LACKED THE INCUMBENT'S ACTUAL BEHAVIOR.** That is the same finding as
OA's `no-incumbent-characterization`, arriving as a *gap* rather than as a *criticism* — which is
the more trustworthy form of it.

---

# ✅ AND ONE NUMBER IS NOW MEASURED, KILLING A REMEMBERED ONE
OA flagged `path-inventory` as major: *"the unverified estimate can drive an architecture and work
plan without a completed, reproducible inventory."* **Measured 2026-08-22, same hour:**

| | remembered | **MEASURED** |
|---|---|---|
| files to port | ~66 | **139 `.py`** (38,599 lines, 1.87 MB) |
| hard-coded path lines | ~1,961 | **179**, in **73 of 139 files** |
| `.parent` arithmetic | — | **11 lines in 8 files** |
| already clean | — | **63 of 139 — port is a move, not a rewrite** |

🔴 **THE REMEMBERED FIGURE WAS ELEVEN TIMES THE REAL ONE.** 179 lines is a day of careful work, not
a quarter. **An architecture chosen for a 1,961-line problem would have been over-built for a
179-line one** — and the plan was about to be sized against it.
⚠ Comments and docstrings were **excluded**: a docstring *warning about* a hard-coded path is not
one, and counting it sends a builder to "fix" the warning. `tmp\COSMOS_PORT\PORT_SURVEY.json`.
