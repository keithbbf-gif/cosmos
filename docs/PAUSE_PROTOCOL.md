# PAUSE — COSMOS control primitive (a formal stop for the retask clock)

**Consumer:** COSMOS / nodes. Narrative governance. **Encoded 2026-08-25 at Keith's order:**
*"Come up with a pause protocol and make PAUSE a formal stop to the Watchdog2 15-second retask
clock."*

## What PAUSE is
One flag file — **`live\state\control\PAUSE.flag`**. Its PRESENCE is the whole signal: the
Watchdog2 15-second no-idle retask clock — and every auto-retask clock — stops dropping NEW
agents. One file, one truth, checked at the TOP of every clock cycle.

## What PAUSE does — and does NOT do
- **STOPS:** new retasking. Watchdog2 drops no agents; the ≤15s no-idle rule is suspended.
- **DOES NOT stop:** in-flight agents (they finish and return), the results collector, or the
  runner executing already-queued jobs. A pause halts NEW work, never work already moving — so
  nothing in flight is lost.
- **DOES NOT kill anything.** PAUSE is a gate, not a kill.

## Visible, never silent (the scar it respects)
A paused clock MUST be distinguishable from a dead one. While paused, Watchdog2 keeps writing its
heartbeat with `state = "PAUSED"` and the reason; `cosmos status` reports PAUSED. *"A check that
never ran is indistinguishable from one that passed"* — so a pause that merely stops the heartbeat
is forbidden.

## The flag contract
`live\state\control\PAUSE.flag` — JSON: `state, scope, reason, set_by, set_at, effect, resume`.
**Reason and timestamp are REQUIRED** — a bound control, never a silent one.

## Set / clear
- **PAUSE:** COW or Keith writes the flag (reason + timestamp).
- **RESUME:** delete the flag (or set `state = "RUNNING"`). On resume, Watchdog2 logs `RESUMED`
  and picks the route back up from `WISHLIST.md` / `BACKLOG.md` / `MOTIF_TRACKER.md`.

## Every auto-retask clock honors it
Watchdog2 (`cosmos_watchdog2.py`) and any future auto-retask clock read this flag first each
cycle. The runner, collector, and discovery clocks do NOT gate on it — they must keep moving so
in-flight work returns during a pause.

## When to PAUSE
TidyUP + resession (so the retask clock does not fire new agents mid-handoff), and any deliberate
stop Keith calls.

**OA-burn (Keith 2026-09-04):** HOLD was on until this review because a **poll daemon
ran up ~$150 on the OpenAI Platform API for nothing.** **RESUME fully** 2026-09-04
(Keith: continue building COSMOS, testing cDeck) — `PAUSE.flag` staged to
`_delme/resume_2026-09-04T1116/`. The OA API lane stays paused on the **OpenAI
account** and as `live/state/control/OA_PAUSE.flag`; `dispatch()` raises `OA_PAUSED`.
Lifting HOLD does **not** re-enable `oa-api`. No unattended poll/prove loop on a
metered API.

## Two pause modes — `mode` field
- **`hold`** — waits until explicitly resumed; NEVER self-clears. TidyUP and "Keith says stop" are
  holds.
- **`resume_gate`** — dropped at BootUP; carries **`auto_resume_at`** (ISO time). WD2 self-clears
  it at that time and resumes the route. This is the auto-resession default.

## The Resume Gate — PERMANENT, ALL STREAMS (Keith, 2026-08-25)
The instant BootUP finishes loading the carry-over (BUCm + `state/SEED.json` + task list), the
session **presents ONE option: restart on the carried-over task list / all prior-session items?**
— *Resume all · pick a subset · hold.*
- **Affirmative selection → act on it** (resume all / the chosen subset / stay held).
- **No affirmative selection → AUTO-RESUME.** The BootUP resume-gate flag carries
  `auto_resume_at`; the native 15s WD2 clock clears it at that time and drives the MOTIF route with
  **no human turn**. The default is MOTION — when Keith returns, work is already moving.
- **How BootUP arms it:** on load, if a `hold` flag from TidyUP is present, BootUP presents the
  option and (unless Keith holds) rewrites the flag to `mode="resume_gate"` with
  `auto_resume_at = now + grace`; WD2 does the rest. Same for every stream.
- This makes auto-resume a property of the **OS clock**, not the Cowork session — the offload-onto-
  Windows principle, and the mechanism behind unattended auto-resession.
