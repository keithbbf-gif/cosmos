# Loops

Hermes `/loop`, and the `/proactive` alias, re-runs one prompt on a cadence inside the current session. Each wakeup is one ordinary user-role turn. A fixed interval follows the caller's clock. A self-paced loop starts at 60 seconds and doubles, up to 900 seconds, while a local reply digest stays the same, then snaps back to 60 seconds when the digest changes. The loop ends when the agent marks the work complete, when the iteration budget is spent, when an until-condition is achieved, when that condition is judged unachievable (the loop pauses), or when the user stops it. Pause and interrupt keep the loop. Resume continues it. An active goal defers wakeups. A new loop replaces the one already on the session. Hermes documents a backstop of 100 ticks and treats 0 as unlimited. This proposal does not. The policy cap is 8. A higher `max_iters` is stored on `requested` and `effective` stays 8. A request of 0 is refused.

The live seam is new: cap 8. `cosmos_sched.py` remains the only scheduler. `cosmos_nlcron.py` remains the unattended cadence. The harness turn counter is a different cap. This module does not call those modules.

## Operations

`define(name, max_iters)` returns one frozen loop. `cap` is 8. `effective` is the lesser of `requested` and 8. A caller who asks for more than 8 iterations is ignored: `requested` keeps the ask, and `cap` and `effective` stay 8. `interval_s=None` selects self-paced cadence. A fixed interval of 120 seconds is accepted. A fixed interval below 30 seconds or above 86400 seconds raises `OUT_OF_RANGE` and is not rewritten. `/proactive` is the same `define` call.

`tick(loop)` returns the next record with `ticks` increased by one. It does not run a prompt. The call that would make `ticks` greater than `effective` raises `LOOP_CAP`. That refusal is `Capped`, and `Capped.loop` is the stopped record: `status` is `STOPPED` and `stop_reason` is `LOOP_CAP`. `ticks` stays at `effective`. Eight wakeups are the maximum plan.

`pause`, `interrupt`, `resume`, `stop`, and `complete` are the session commands. `complete` records `LOOP_COMPLETE`. `stop` records `STOP`.

`judge(loop, verdict)` applies a caller-supplied until-verdict. `ACHIEVED` stops with `UNTIL`. `UNACHIEVABLE` pauses with `UNTIL`. `CONTINUE` returns the same record. This module does not score until-text. An unknown verdict raises `BAD_VERDICT` and is not retried.

`note_reply(loop, digest)` updates self-paced backoff from a caller-supplied digest. Comparison uses `const_eq`. No timestamp is read.

`tick(loop, goal_active=True)` records `goal_deferred` and does not spend a tick. A second deferral returns the same record. Deferral is refused once the loop is paused or stopped.

`make_board`, `install`, and `current` keep one loop on a session. `install` replaces.

`snapshot` copies the public fields. `rebuild` from that snapshot, or from a `Loop`, returns an equal loop.

`status` returns the descriptor a `/loop status` view would show: ticks, remaining budget, the base interval, and `next_interval_s` as the duration until the following wakeup. It does not read a clock. A view whose stop reason, ladder step, or deferral flag disagrees with the record refuses.

## Authority

The session record holds the loop. The human owns pause, resume, and stop. Policy owns the cap of 8. A later clock, not this module, decides when a wakeup is due and calls `tick` once. There is no ledger write, no attempt workspace, and no scheduler thread.

## Refusal codes

`BAD_BOARD`, `BAD_CAP`, `BAD_DIGEST`, `BAD_KIND`, `BAD_LOOP`, `BAD_NAME`, `BAD_PROMPT`, `BAD_STATUS`, `BAD_UNTIL`, `BAD_VERDICT`, `EMPTY`, `LOOP_CAP`, `NO_UNTIL`, `NOT_ACTIVE`, `NOT_BOOL`, `NOT_INT`, `NOT_PAUSED`, `NOT_SELF`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `PAUSED`, `SECRET`, `STOPPED`, `UNLIMITED`.

## Ship

Operations: `INTERVAL_CAP`, `MIN_INTERVAL_S`, `POLICY_CAP`, `SCHEMA`, `SELF_CEILING_S`, `SELF_FLOOR_S`, `Board`, `Capped`, `Loop`, `LoopStatus`, `Snapshot`, `complete`, `current`, `define`, `install`, `interrupt`, `judge`, `make_board`, `note_reply`, `pause`, `rebuild`, `resume`, `snapshot`, `status`, `stop`, `tick`.

Refusal codes: `BAD_BOARD`, `BAD_CAP`, `BAD_DIGEST`, `BAD_KIND`, `BAD_LOOP`, `BAD_NAME`, `BAD_PROMPT`, `BAD_STATUS`, `BAD_UNTIL`, `BAD_VERDICT`, `EMPTY`, `LOOP_CAP`, `NO_UNTIL`, `NOT_ACTIVE`, `NOT_BOOL`, `NOT_INT`, `NOT_PAUSED`, `NOT_SELF`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `PAUSED`, `SECRET`, `STOPPED`, `UNLIMITED`.

This module still refuses to execute the prompt, the until-judge, a wakeup turn, a scheduler, a thread, a sleep, or a file write. A 5-second interval is not stored. Unlimited iterations are not accepted. A broken verdict is a denial, not another wakeup.

Hot path: one record. Status, kind, stop, and verdict membership are dict lookups. Self-pace steps are a set. A goal that is already deferred returns the same object. A tick does not hash the prompt. Digest comparison hashes each side once.

## Landing

CCr would store the frozen `Loop` on the session and ask the existing session clock to call `tick` once per idle wakeup. On `Capped`, it would persist `Capped.loop` and not schedule another wakeup. The effective cap stays 8 when a config file asks for more. A fixed interval under 30 seconds is a denial, not a quieter schedule. The landing adds no run loop, no sleep, and no second scheduler.
