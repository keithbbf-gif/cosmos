# COSMOS STAGE 6a — THE FOUR SPIKE BRIEFS · 2026-08-23
**Builder: GWB (native shell, local disk). Reviewer: F5/CC + GbQb (diffs, not prose).**
**Every spike RUNS on live Windows and is measured against `docs/STAGE2A_INCUMBENT_BEHAVIOR.md`
observed behavior. Architecture contract: `docs/FINAL_ARCHITECTURE.md`. A spike is an
EXECUTABLE PROBE of the hard assumptions — small, runnable, disposable; the bulk port reuses
its lessons, not necessarily its code.**

## GROUND RULES (all four)
- Work on a branch (`spike/<name>`), never the live BTS tree. Claim `tree_lock` for any
  live-tree read/write. NEVER delete anything; stage to `_delme` if needed. No `.bat`.
- Each spike ships: the code · a selftest with POSITIVE AND NEGATIVE controls · a measured
  demo run on this machine · a one-page findings note (what held, what surprised, what the
  bulk port must change). American English.
- Typed absence everywhere: NOT_FOUND ≠ OUT_OF_CLOCK ≠ UNREADABLE ≠ NOT_IN_RECORD.
- Every artifact carries worker identity + offset-aware timestamp + epoch.

## SPIKE 1 — `cosmos_paths` (resolver)
Prove: explicit-instantiation resolver with ONE configured root (installation record +
sentinel content verification, not existence), role API, refuse-don't-guess, second-install
settability (instantiate against a scratch root at a different letter/path), MAX_PATH-safe
walk via platform adapter (275+ char path demo), and the mesh() lesson — a sentinel
CONTENT assertion that catches an existing-but-empty directory.
Negative controls: missing root REFUSES · sentinel wrong-identity REFUSES · empty-dir
sentinel trap DETECTED · import causes no filesystem side effect.

## SPIKE 2 — `cosmos_lock` (lease + fencing + fenced commit)
Prove: arbiter-issued lease with expiry on arbiter clock, monotonic fencing token, fenced
commit that REJECTS a stale token, recorded takeover chain (LEASE_EXPIRED→LEASE_GRANTED),
torn-state refusal, and the two-universes test: a native claimant and a sandbox-side write
attempt cannot both "hold" anything — the sandbox path goes through an ingress envelope and
cannot commit. Demonstrate a dying-holder recovery WITHOUT any cleanup discipline.
Negative controls: stale-token commit REFUSED and ledgered · torn lease file REFUSES ·
expired holder cannot publish · takeover is a recorded event, not a silent clear.

## SPIKE 3 — `cosmos_mail` (IPC at N>2)
Prove: per-worker inbox directories, immutable uniquely-named messages (sender identity +
offset timestamp + payload hash), missing-vs-empty-vs-unreadable-vs-stale as four distinct
typed states, probe command reporting all of them, staleness policy (age threshold +
unanswered required-ack), and send-vs-received as separate recorded facts (receipt files).
Negative controls: missing mailbox NON-ZERO (dead phone, never "no news") · a half-written
message detected by hash · two senders to one recipient produce two files, zero collisions.

## SPIKE 4 — `cosmos_sched` (scheduler: concurrency + priority + interrupts)
Prove: N concurrent workers on one queue with priority admission (manifest field, not
filename), claim that survives overlap (atomic per-job assignment; the loser LOSES CLEANLY
and moves on — the incumbent's unhandled-loser gap), three worded outcomes to three
destinations, log-first, report-never-retry on stale, per-worker glob-discoverable
heartbeats, and ONE INTERRUPT-DRIVEN WAKEUP: a file-change or timer event fires a job with
no polling loop (ReadDirectoryChangesW / watchdog), measured latency vs the 60 s poll.
Negative controls: rc=2 lands in findings not failed · a lane with jobs and no worker is
FLAGGED · helper `_` file untouched · two overlapping ticks execute the job exactly once
(run 100 iterations, count executions).

## MEASUREMENT BAR
Each spike's demo prints MEASURED numbers (latencies, counts, refusal codes) — a spike
whose claims are prose has not run. Findings notes land in `docs/SPIKE_FINDINGS_<name>.md`
on the spike branch; the stage 7 reviewers read the DIFF plus the findings.
