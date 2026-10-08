# COSMOS Harness

The control loop is fixed. The model is sampled once per turn, and only there.
Eight hooks decide the prompt, the hands, the stop, the seating SOP, the
checkers, and the bundle. Turn cap is 8. A refused hand sets a latch, and
the latch is not cleared.

## Languages

| Layer | Language | File |
|---|---|---|
| l1 role | Markdown | `pack/L1_ROLE.md` |
| l2 model | TOML | `pack/pin.toml` |
| l3 harness | Python | `cosmos_harness/loop.py`, `hooks.py` |
| l4 wrapper | Markdown | written per attempt as `WRAP.md` |
| l5 skills | Markdown | `pack/L5_SKILLS.md` |
| l6 tools | JSON | `pack/L6_TOOLS.json` |
| l7 enviro | C and Python | `native/job_object.c`, `jail.py` |
| l8 mission | Markdown | `pack/L8_MISSION.md` |

The Win32 job API is C. The path jail and the hook machine are Python. The
hands the model can call are a JSON schema the host executes. Style stays
off the system turn.

## Hands

`read`, `glob`, `grep`, `edit`, `write`, `archive`, `oracle`, `worktree`.

There is no delete hand and no bash hand. Removal moves the file to
`_delme`. Checkers run in the verify hook: py_compile, ruff, mypy, pytest.
A missing checker is `UNAVAILABLE` and blocks done. An edit waits until the
oracle has failed. Plan mode can look and cannot write.

## Seating

`learn.step` classifies one observation with the G47 scar table and returns
the one SOP. The outcome is appended to a journal, including a stop. The
table is not edited at runtime. A sentence the table does not name stays in
the journal until a person adds one row, which is how pcm16, the batch
adapter, and effort-low were added.

`seat_proof` seats only when the served id is this pin and a child running
`constants()` passes. A file from another model stays `MOUTH_FOREIGN`.

## What this does not claim

The law score is ahead of the recorded Claude Code zeros (pin lock, no
ungated retry, bundle, oracle before edit, delete is not a tool, four
checkers, live refused, turn cap, eight layers, one scar one SOP). That is
not a task bakeoff. Opus seated in Claude Code is a different measurement.
`wipe_proof` stays false. The enclosure reason stays `policy_only`.

```
py -3.14 -m pytest -q
py -3.14 -m cosmos_harness
```
