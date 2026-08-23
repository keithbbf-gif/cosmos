# COSMOS STAGE 2 — MERGE OF FAMILY RETURNS · 2026-08-23 ~04:15
**Returns merged: GEM (gemini-2.5-pro, $0.075) · OA (gpt-5.6 API) · CoPG (Copilot).**
**PENDING: Grok 4.6 via Cursor — dispatches when the Cursor key lands. This merge reopens
for exactly that one addendum; nothing here is final against a 3-of-4 set.**
⚠ Identity note: GEM's return self-labeled "CCF5" — it lifted the name from `KNOWN_WRITERS`
in the packet's tree_lock source. Identity here is from the DISPATCH RECORD, never the
return's self-label. GEM's ids CCF5-NN are cited as GEM-NN.
⚠ Family count: three families returned (Google, OpenAI ×2 lanes counted once — OA is the
only OpenAI return; CoPG is Microsoft-served but the underlying model family overlaps OpenAI.
Treat CoPG agreement with OA as WEAK plurality, same-priors risk.)

---

## 1 · ERRATA AGAINST THE F5 CHARACTERIZATION — verified host-side, doc corrected
| id | finding | verdict |
|---|---|---|
| OA API-04 | tree_lock still computes `ROLD = MESH.parent / "ROLD"`; the doc claimed it resolves via `bts_paths.rold()` | **CONFIRMED against source. Doc corrected.** Parent-walk is LIVE in tree_lock. |
| OA API-01 | bts_paths has NO sentinel-content check and NO `\\?\` handling — those are REQUIREMENTS, not incumbent behavior | **CONFIRMED. Doc phrasing kept them under "spike acceptance" — correct — but §1 read as if partially present.** |
| OA API-02 | bts_paths CLI *accepts* `--check`/`--selftest` but implements no distinct branch — report prints for any accepted arg | **CONFIRMED against source.** A permitted flag with no implementation is a silent no-op — same class as the scars.py --selftest scar. |
| GEM-02 | RUNNABLE-dict deletion was not mere drift cleanup; it was the sole job filter in tick()/status(), deleting blind would have killed the runner | **CONFIRMED — the doc understated the dependency.** |

## 2 · UNANIMOUS (3 of 3) — ADOPT AS STAGE 3/4 INPUT
1. **Enforcing lock requires a mechanism, not discipline** — all three independently
   converge on *lease + fencing token + append-only event record*, and all three reject
   the current read-check-write claim. OA goes furthest: **the claim is not even a safe
   cooperative protocol** (API-05: two claimants can both read free and both write).
2. **Scheduler: priority + identity in every artifact + no last-writer-wins.** GEM proposes
   SQLite transactional queue; OA proposes immutable job manifests + arbiter-issued claims;
   CoPG proposes meta-sidecars + per-group limits. **The SHAPE is agreed; the mechanism is
   the stage 4 decision.**
3. **Resolver: role-based, fail-loud, sentinel-content assertion, no fallback, MAX_PATH via
   adapter, drive letter is config.** GEM and OA both propose a class/object over a module
   with import-time side effects; CoPG proposes call-time resolution. **Contested detail
   below (import-time vs call-time).**
4. **Mailbox at N>2: per-worker directories, immutable/unique message files, sender
   identity + timestamp in payload, missing≠empty preserved, staleness policy added.**
   Convergent to the point of near-identical layouts.

## 3 · MAJORITY / STRONG SINGLETONS — CARRY FORWARD
- **OA API-05 (with GEM-07 adjacent): the one-volume assumption.** Claim-by-rename and all
  queue moves are atomic ONLY on one volume; any COSMOS layout splitting queue/logs/archive
  across volumes silently loses the guarantee. GEM ranks this its top port hazard (GEM-11).
- **OA API-11: the losing rename in an overlapping tick is UNHANDLED** — aborts the tick.
  Double-execution is prevented; clean concurrency is not.
- **OA API-12: only the LEDGER is append-only.** Heartbeat, logs, claim moves are
  overwrite/truncate artifacts. Do not generalize "the runner is append-only."
- **OA API-03: sandbox glob takes sorted()[0] of possibly-multiple mounts** — arbitrary
  lexicographic winner. A port preserving globbing must assert uniqueness or identity.
- **OA API-07: stale takeover + FUSE-fallback release leave NO durable audit record** —
  console output is not evidence. Fold into the lock's append-only event requirement.
- **OA API-08: bts_phone has no SEND path at all** — OUTBOX is declared, never written.
  The characterization described the convention; the code implements only probe/read.
- **OA (prose): tree_lock timestamps are NAIVE LOCAL** — the exact defect class the runner
  heartbeat already paid for (misread as five hours stale, twice). Malformed `claimed`
  inside valid JSON reads as infinitely stale → enables takeover, not refusal.
- **GEM-06: lane-name regex is an undocumented path-injection guard** — preserve it.
- **OA hazards 4/5/7 (singletons):** clock skew (arbiter clock is authority, worker clocks
  are evidence) · Windows case-insensitive identity collisions (canonicalize, reject) ·
  subprocess containment (a timeout that kills the wrapper may orphan descendants; use job
  objects on Windows, record the kill outcome).

## 4 · CONTESTED — for stage 4 architecture round, rubric first
| topic | positions |
|---|---|
| **Lock arbiter** | OA: single Windows arbiter SERVICE + fenced write gateway (strongest guarantees, new moving part). GEM: OS file locks + fencing hybrid (fewer parts; GEM itself flags FUSE lock-semantics risk). CoPG: append-only lease ledger + HMAC tokens, arbiter optional. **The real question: is a resident arbiter service acceptable in a mesh that today has zero resident daemons beyond Task Scheduler?** |
| **Queue substrate** | GEM: SQLite (transactional, one file — but a shared mutable file by construction). OA: immutable manifests + claims dirs (no DB, more files, needs arbiter for assignment). CoPG: keep filesystem + sidecars (minimal delta). |
| **Resolver timing** | GEM/OA: object instantiated with explicit root (no import-time effects). CoPG: call-time functions. Incumbent: import-time constants — proven fail-fast property. **Decide: where does the failure surface?** |
| **DOM lanes in scheduler scope** | Not addressed by any return (packet did not ask). Keith's ruling: DOM is the foundation. Stage 4 must place DOM dispatch inside the scheduler design, not beside it. |

## 5 · WHAT THIS MERGE DOES NOT COVER
- Grok 4.6 return — PENDING (Cursor key).
- Behavioral cards for the other 135 modules — every family correctly skipped (sources not
  in packet). **Dispatch as a follow-up packet in slices, or per-slice via Cursor agents.**
- No family could RUN anything (all text-only, per Blocker-3 measurement). Every design
  claim above is unexecuted reasoning — the spikes are where these designs meet reality.

## 6 · DECISION QUEUE FOR KEITH (one line each)
1. Arbiter service: acceptable yes/no? (Shapes lock + scheduler both.)
2. SQLite vs filesystem-manifest queue substrate?
3. Resolver: fail-fast import (incumbent's proven shape) vs explicit-instantiation object?
*(Stage 4 packet carries whichever rubric you set; contested items return as designs, not
re-votes.)*
