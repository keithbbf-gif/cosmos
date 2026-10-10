# Clone planner

This page is one chapter of the developer book. It does not mean COSMOS is
finished, or that parallel seats exist as running processes. The planner
is `cosmos\cosmos_clone_plan.py`, function `plan_clones`. It does not
launch seats.

## What a plan is

One call returns one inert plan. The plan's `pen` is false. Its
`executable` is the empty string. `rows` has one row per seat, in the
order the caller passed. A row stores the seat id, the same mission
string, `pen` false, `spawn` false, and the index pointer
`work_orders/ccr/HERO_SEAT_INDEX.md`.

The pointer is a string on the row. The planner does not open that file,
does not read a hero index, and does not check that the path exists. It
does not write `CCR.lease`, does not take a pen, and does not start a
terminal. The module imports nothing that launches a process. The pin
`tests\test_clone_plan.py` requires the source to contain neither
`subprocess` nor `Popen`. This page does not report a pass count.

The plan object has three keys, in this order: `pen`, `executable`,
`rows`. Each row has five keys, in this order: `seat`, `mission`, `pen`,
`spawn`, `index_pointer`. Twelve seats is the maximum (`MAX_SEATS`). A
full plan of twelve still has `pen` false, `executable` empty, and
`spawn` false on every row.

## Refusals

A bad call raises `ClonePlanError` and returns no rows. `reason` is one
stable code. The first failure wins. Check order is the pen, then the
mission, then the roster size, then each id. There is no partial plan.

| Reason | When |
| --- | --- |
| `SECOND_PEN` | The caller passed `pen=True`. Checked first, so an empty mission or an empty roster with `pen=True` is still this code. |
| `EMPTY_MISSION` | The mission is missing, not a string, or blank after strip. |
| `NO_SEATS` | `seats` is not a list, or the list is empty. |
| `TOO_MANY` | More than 12 entries. Checked before each id, so thirteen blanks are `TOO_MANY`, not `BLANK_SEAT`. |
| `BLANK_SEAT` | An entry is not a non-blank string. |
| `DUPLICATE_SEAT` | The same id appears twice. Blank is noticed before duplicate on that entry. |

`pen` defaults to false. Only the value `True` is a second pen. Any other
value is not `SECOND_PEN`, and the returned plan still sets `pen` false.
The planner does not grant a pen because the caller omitted the flag.

An unknown reason cannot be constructed as a `ClonePlanError`. That
constructor raises `ValueError` instead of inventing a code.

## Not the other clones

These names are other modules. They are not `plan_clones`, and this
planner does not call them.

| Name | What it actually is |
| --- | --- |
| `cosmos_workspace.clone_tree` | Copies a workspace tree into an attempt directory. |
| `cosmos_dispatch_workspace.clone_attempt_workspace` | Seeds an attempt workspace. |
| `builds\session-tools\clone.py` | Refuses two texts with the same final stretch (`CLONE`). It detects a duplicate mouth. It does not plan seats. |
| `git clone` | Not this function. The planner does not run git. |
| Door bind / cluster presets | Other packages that store a seat and do not launch. They are not this plan. |

`installs\DOORS.toml` is the resession door catalog. It is not an input
to `plan_clones`. A seat id here is whatever non-blank string the caller
passed, up to twelve unique ids. The planner does not look up a binary
and does not start one.

A plan on disk or in a return value is a list of seats that must not run.
`spawn` false is the contract, not a default the caller flips. There is
no execute flag. COSMOS is not finished because a planner can name twelve
rows.
