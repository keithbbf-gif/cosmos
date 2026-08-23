# COSMOS STAGE 4 — DECISION RUBRIC · fixed 2026-08-23, BEFORE any design is read
*(OA's stage 0 finding: a selection without a pre-stated rubric has no reproducible basis.
This rubric is committed before the architecture round fires and is not edited after
designs arrive. Amendments require Keith and a dated note.)*

## HOW DESIGNS ARE JUDGED
Each design is scored per criterion: **SATISFIES / PARTIAL / FAILS**, with evidence quoted
from the design. No aggregate number — a FAILS on any hard criterion (H) eliminates;
soft criteria (S) rank the survivors. Disagreements between reviewers land as CONTESTED on
the board, both positions, one line to Keith. No third model resolves anything.

## HARD CRITERIA — a FAILS here eliminates the design
| id | criterion |
|---|---|
| H1 | **Carry-over stability is structural**: state carries across sessions by mechanism, not discipline; a forgotten fact is a bug the system can detect. |
| H2 | **Fail-loud everywhere**: no silent fallback, no guess, no plausible-path resolution; torn or unparseable state REFUSES. |
| H3 | **Survives the named failure modes**: a lying/corrupting mount · a session dying without release · two writers in different universes (native + sandbox) · an expiring credit · a dead rail mid-run. Each addressed by design, not by hope. |
| H4 | **The seven OS primitives are native**: integrity-verified I/O · return watchers · return-validation · registry-reality reconciliation · session/context manager · platform adapter · typed absence. Bolted-on = FAILS. |
| H5 | **Enforcing concurrency**: locks enforce (advisory banned at N>1); scheduler owns concurrency + priority; per-worker identity in every artifact; no last-writer-wins shared file. |
| H6 | **Total connectivity is registry-driven**: every rail class (CLI/API/DOM/CHAT/other) a first-class link type; DOM-first routing policy expressible; links probed, never assumed. |
| H7 | **Settable root + served mode**: one install-time root, sentinel-verified; runs as a service (cloud or WRK7) with remote authorized access; API is the product surface. |
| H8 | **Proven incumbent behaviors preserved** (or explicitly adapted with the architecture-wins escape valve, recorded per tool): claim semantics under overlap · three worded outcomes · log-first · report-never-retry · helper convention · append-over-rename on mount-exposed state. |
| H9 | **Real-OS hooks**: one authoritative clock · scheduler integration · interrupt-driven wakeups (file/timer/signal), not poll-only. |
| H10 | **MVP separability**: the architecture is whole, and the code phase can ship the MVP boundary without redesign (frontend/voice as API surface only; W1-W12 as seams). |

## SOFT CRITERIA — rank the survivors
| id | criterion |
|---|---|
| S1 | **Fewest resident moving parts** that still enforce — every new daemon must pay rent. |
| S2 | **Cold-machine install simplicity** — steps to a running peer install, counted. |
| S3 | **Auditability** — how directly the realtime tracking + on-demand/periodic audit falls out of the design. |
| S4 | **Blast-radius containment** — what a bad job, bad node, or bad key can reach. |
| S5 | **Incremental cutover** — how much of BTS can keep running mid-port; rollback cost. |
| S6 | **Wishlist headroom** — W1-W12 land as increments, not surgeries. |

## QUESTIONS EACH DESIGN MUST ANSWER EXPLICITLY (from stage 2/3 contested)
1. Lock enforcement mechanism: OS locks / lease+fencing / arbiter service — chosen and
   justified against H3's failure modes. If a resident arbiter: why it earns its rent (S1).
2. Queue substrate: filesystem manifests / SQLite / other — justified against H5 + H8.
3. Resolver timing: import-time fail-fast vs explicit instantiation — justified against H2.
4. Where DOM lanes live in the scheduler design (H6) — dispatch, watchers, probes.
5. The KDash live backend + frontend API: one service or two, and why.
6. Backup subsystem placement: kernel service or scheduled tool, and how restore rehearsal
   is designed in.
