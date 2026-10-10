# Meter window

This page is one chapter of the developer book. It does not mean COSMOS is
finished, or that a live spend total has been measured. The fold is
`cosmos\cosmos_meter_window.py`, function `meter_window`. It is pure. The
caller passes the rows and the clock. The module does not open the ledger,
the meter file, or the wall clock.

The window is UTC today and seven UTC dates. A missing count is the string
`UNMEASURED`. A carried 0 stays 0.

## Today and seven dates

`clock` is an epoch (int or float) or an offset-aware ISO timestamp. A
date with no clock is that UTC midnight, which is the start of the new
day. A clock with no offset is refused. Local time is not treated as UTC.
A `Z` suffix is UTC. A non-finite epoch is `BAD_CLOCK`.

`today` is the half-open UTC day that contains the clock: from that
midnight inclusive to the next midnight exclusive. A timestamp exactly on
midnight belongs to the day that starts then, not the day that ended.

`week` is seven UTC dates ending today: today plus the six dates before
it (`TRAILING_DAYS` is 7). The same exclusive end applies. A row on the
midnight before that oldest date is outside the week. A row on the next
UTC midnight is outside both windows.

The return value is `today` and `week`. Each side has `tokens_in`,
`tokens_out`, and `usd`. Nothing else is added.

## UNMEASURED is not zero

`UNMEASURED` is the string `"UNMEASURED"`. It is not `None`, not `0`, and
not a missing key.

Counts: if the window has no rows, or any row in the window did not carry
that side, the side is `UNMEASURED`. The fold does not sum the rows that
happened to have a number and store zero for the rest. One missing
`tokens_out` makes the whole window's `tokens_out` `UNMEASURED`, including
the week when yesterday is missing it and today is complete.

A carried 0 stays 0. Zero is a count the row carried. The result is an
int, not the string. The same rule applies to dollars: a row that carried
`0` is a price, and a window of those zeros sums to `0`.

Dollars sum only the rows that carried a price. The window is `UNMEASURED`
only when none of them did. A priced row beside an unpriced row still
contributes the priced amount. The sum is rounded to six decimal places.
An unpriced label (`unpriced` or `unmeasured`) must not also carry a
number. That row is `BAD_ROW`, not a silent zero.

Empty input matches the same shape. `meter_window([], clock)` and
`meter_window(None, clock)` both return today and week with all three
fields `UNMEASURED`. `None` means no rows. It does not mean zero spend.

## Which rows count

A named event in the skip set is ignored. It is not an error and it is not
a zero. The names are `BUDGET_SET`, `SPEND_RESERVED`, `SPEND_RELEASED`,
`SPEND_DENIED`, `RUN_FAILED`, `CREDIT_PURCHASED`, `CREDIT_GRANTED`,
`TOLL_ACCRUED`, and `QUOTA_HIT`.

A named event is counted only for `SPEND_SETTLED`, `RUN_SETTLED`, and
`RUN_UNPRICED`. Any other name is `BAD_ROW`. The whole call raises.
Later good rows are not folded, and earlier good rows are not returned as
a partial window.

A row with no `event` must already carry meter fields. Otherwise it is
`BAD_ROW`.

Token aliases on one row must agree. The in-side looks at `tokens_in`,
`tokens.in`, and `prompt_tokens`. The out-side looks at `tokens_out`,
`tokens.out`, and `completion_tokens`. Two different numbers, or a number
beside an explicit empty alias, is `BAD_ROW`. A bool is not a count. A
negative is not a count. A float is not a count.

Price aliases must agree within a small tolerance. The fold reads
`measured_usd` with `provenance`, a scalar `usd` with `cost_kind`, and
`cost` when that value is a measured object or a scalar. `usd` that is
itself an object is not read as the price. Provenance must be one of
`unpriced`, `unmeasured`, `measured`, `estimate`, or `billed`.
`measured` and `billed` require a price. An unknown label is `BAD_ROW`.

Time comes from `t` or `at` on the row, and the same keys inside `payload`
when that value is an object. Two timestamps that are not the same instant
are `BAD_ROW`. No timestamp is `BAD_ROW`. Payload fields overlay the row
for the meter values. The ledger-shaped row is `event`, `t`, and
`payload`. A flat row with `at` and the counts is also accepted.

`MeterWindowError` kinds are `BAD_INPUT`, `BAD_CLOCK`, and `BAD_ROW`.
`events` must be a list of objects, or `None`. A string is `BAD_INPUT`.

## Not the spend-meter satellite

`cosmos\cosmos_spend_meter.py` is a different program. It walks the
authority ledger through `SpendGate.audit` and writes a projection under
the state role (`spend\meter.json`) plus a heartbeat. That projection's
token object is kind `UNMEASURED` with empty in and out. Its day and week
dollar fields are left empty, kind `UNMEASURED` when there is nothing to
call measured. The satellite's own comment says not to invent 0 there. It
does not call `meter_window`. Do not read `meter.json` as this seven-date
fold.

`builds\cdeck\ui\header.js` keeps a parallel fold and comments that it is
the same rule as `meter_window`. The strip is painted from events already
on the page. Cap and `settled_usd` are not inputs to that fold. A missing
count there is also the string `UNMEASURED`, and a numeric 0 stays a
number. That script is not an import of the Python module. Core `serve`
does not call `meter_window`. The Python pins are `tests\test_meter_window.py`.
This page does not report a pass count.

A string `UNMEASURED` on the strip means this window was not counted. It
does not mean the spend was zero, and it does not mean COSMOS has a
finished meter.
