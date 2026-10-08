# Cron

Hermes accepts a natural-language cadence or a 5-field cron expression and can pause or resume a job. The gateway ticker is the only runner. A cron session does not create further cron jobs unless a later config says so. This proposal does not start a ticker.

The live seam is `cosmos/cosmos_nlcron.py`. It already maps a cadence onto `schtasks`, `detached_daemon`, or `onlogon`. `cosmos/cosmos_sched.py` remains the only scheduler. `plan_create` in `cosmos/cosmos_clock.py` already accepts `sc`, `mo`, and `st`. This proposal does not add a second clock and does not call `plan_create`.

`parse(text)` returns a frozen `Cadence`. It accepts one 5-field expression when that expression names a single vehicle, plus the phrases `every day at HH:MM`, `daily at HH:MM`, `every weekday at HH:MM`, `weekdays at HH:MM`, `every N minutes` (and second or hour units written the same way), `hourly`, `weekly`, and `on logon`. A starred day-of-month with a day-of-week list or range is one `WEEKLY` vehicle. `every weekday at 09:00`, `0 9 * * 1-5`, and `0 9 * * MON-FRI` are the same descriptor: `day` is `MON,TUE,WED,THU,FRI` and `st` is `09:00`. Day lists are Monday-first, duplicates and wrapped ranges refuse, and twelve-hour suffixes stay unrecognized. An interval below 60 seconds is mode `detached_daemon` with the requested `interval_s` and no `schtasks` payload. That mode names the WD2 vehicle. `on logon` is mode `onlogon`. Every other fit is mode `schtasks`. `pause(record)` sets `paused`. `resume(record)` clears it. Both return a new record. `snapshot(record)` emits a frozen record. `rebuild` restores the same cadence. `run(record)` does not fire.

A whole minute count maps to `minute`, a whole hour count through 23 maps to `HOURLY`, and a whole day count through 365 maps to `DAILY`. `minute /mo` stops at 1439 and `HOURLY /mo` stops at 23, so those longer exact periods use the next vehicle instead of a rounded one. Clock times keep `interval_s` empty. Bare `weekly` is `WEEKLY` with no day and no start time. Cron `0` and `7` are both Sunday, one label. `day` is recorded for a later `/d` and is not a `plan_create` argument today.

Authority to fire stays with the human who accepts the descriptor and with the ledger row that would store `paused`. This module is not a projection and not an attempt workspace. It writes nothing. It has no retry class. It accepts no path and no credential.

Refusal codes are `UNRECOGNIZED`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `SECRET`, `BAD_RECORD`, `BAD_LIMIT`, `NOT_INT`, `OUT_OF_RANGE`, `IN_PROCESS`, and `STALE`. Empty text, a day-of-month combined with a day-of-week, a duplicate or wrapped weekday, and any phrase with two vehicles are `UNRECOGNIZED`. A request to run in this process, and `run` on a cadence, are `IN_PROCESS`. A snapshot whose schema is not this module's schema is `STALE`. The text cap is 256. A higher requested cap is ignored and 256 is recorded. An interval longer than 365 days is `OUT_OF_RANGE`. Secret-shaped text is `SECRET` and is not copied into the error. A duration that is not a whole minute and not under 60 seconds stays unrecognized, so nothing is rounded onto schtasks or WD2.

CCr would later call `parse` from the `cosmos_nlcron.py` fold and pass `sc`, `mo`, and `st` into `plan_create`. Sub-minute stays a detached-daemon name owned by the clock standup. `day` waits for an explicit `/d` argument. Pause and resume stay flags on the ledger job. This module still would not sleep, tick, or spawn.

## Ship

- operations: `FLOOR_S`, `MAX_INTERVAL_S`, `MODES`, `POLICY_CAP`, `SCHEMA`, `Cadence`, `Emitted`, `Schedule`, `parse`, `pause`, `rebuild`, `resume`, `run`, `snapshot`
- refusal codes: `UNRECOGNIZED`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `SECRET`, `BAD_RECORD`, `BAD_LIMIT`, `NOT_INT`, `OUT_OF_RANGE`, `IN_PROCESS`, `STALE`
- still refuses to execute: no in-process fire, no registration, no schtasks write, and no WD2 spawn. `run` is `IN_PROCESS`. A phrase that asks to run in this process is `IN_PROCESS`. The record is a descriptor only.
- hot-path shape: one bound, one secret scan on the lowered text, one whitespace normalization, then one matcher pass or one pass over five cron fields. Weekday membership is a set of Monday-first lists. A repeated day refuses. The cap only bounds the phrase. There is no item-selection loop and no second scan.
