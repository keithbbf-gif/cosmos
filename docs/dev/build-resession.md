# Resession

This page is one chapter of the developer book. It does not mean COSMOS is
finished, or that an unattended fresh session already runs. The satellite
is `cosmos\cosmos_resession.py`. Its plans return `execute` false and do
not spawn. Claude stays off.

## What the satellite is

Core, the watchdog, the runner, and the collector can keep going after the
orchestrator process dies. The orchestrator process does not. This module
is the CLOCKS id 18 satellite for that boundary (`WORKER` `cosmos-resession`,
schema `cosmos-resession/1`, task name `COSMOS Resession`). It does not
modify the kernel, the ledger writer, the scheduler, or the HTTP service,
and it does not restart Core.

The seed authority is `cosmos.py session start`. This module's seed read is
a structural pre-check so a bad file fails early. It is not a second HMAC
verifier. A thin seed (shape present, facts empty) is not the same as a
seed whose bytes do not match its declaration.

The CLI rail list is `grok` only. `--plan-task` prints a scheduled-task
argument list and registers nothing. `--standup` is not for tests. `--dry-run`
decides and prints; it does not write the projection and it does not spawn.

## Plans do not spawn

`plan_resession` is the dry plan for one door from `installs\DOORS.toml`.
Reading that catalog starts nothing. The function's own body does not call
`Popen` or `subprocess`. Every plan it returns has `execute` set to false.
There is no flag on this function that turns execute on.

Claude is refused before any argument list is built. The kind is
`ANTHROPIC_OFF` (`ResessionRefusal`), with the rule that resession will not
spawn claude. A historical comment in the module mentions a claude session
id flag. That comment is not a rail. `spawn_argv` raises the same
`ANTHROPIC_OFF` if something asks it for claude. Do not add Claude back as
a door this planner will run.

Grok is the one door with a measured two-step plan. The record's `steps`
is `5a+5b`: an inject argument list, then a TUI argument list for the same
caller-supplied session id. `execute` is false. The window on that record
is tokens `200000`, warn `130000` (65 percent), close `190000`. The close
line is that token count, not 90 percent and not 92 percent. A `model`
argument is stored on the record when the caller passed one. It is not
turned into an extra flag. The catalog binary string `grok.exe` is not
copied into that argument list. The plan still does not start a process.
The door note in `DOORS.toml` says not to start `grok.exe`. The plan
agrees.

Every other installed door returns a dry record: `execute` false, `argv` a
one-element list of that row's `binary`, and `window` the string
`UNMEASURED`. None of those rows carry a `window` field, and the planner
does not invent a token cap. As of this tree the other ids are `codex`,
`dsh`, `opencode`, `pi`, `cursor`, `gemini`, and `hermes`. Their binaries
in the catalog are `codex`, `dsh.cmd`, `opencode.cmd`, `pi.cmd`,
`cursor.cmd`, `gemini`, and `hermes`. A passed model is recorded and is
not appended. An id that is not in the catalog is `NO_RAIL`. A catalog
that cannot be read is `NO_RAIL`. An unknown name inside `spawn_argv` is
`NO_RAIL` as well.

`spawn_auto_resession` defaults `execute` to false. That call returns
`ok` true and `dry` true, with the argument lists recorded, and it does
not run them. Clocks use that default. Tests that call it pass
`execute=False` and assert that it does not execute. `--spawn` on the
process is a separate opt-in inside `poll_once`, and only then when the
decision state is `ARMED`, the rail is `grok`, and the reason is not the
quiet backstop. This page does not give that opt-in as a launch recipe.
The plan object never sets `execute` true.

## Decide, then stop

`decide` is a pure state machine. The projection schema is
`cosmos-resession/1`. Order is fixed: a hold wins; a bad seed refuses
before a gate is armed; a live cow lease refuses last so a second
orchestrator is not armed beside a live one.

| State | When |
| --- | --- |
| `HOLD` | Pause class is hold. No spawn. |
| `PACKING` | Pack watermark while the process is still alive. The reason text says not to spawn yet. |
| `WARN` | Warn watermark, or a latched warn. Not a spawn. |
| `IDLE` | No fire. Includes a missing heartbeat. |
| `REFUSED` | Bad seed, missing BootUP prompt, or lease held (`HELD`). |
| `ARMED` | The decision says the next act would be TidyUP and a fresh session. The plan is still not a spawn. |

Watermarks the pure function uses, so a reader can see why it did not
fire:

| Mark | Value | Effect while the pid is alive |
| --- | --- | --- |
| Session age | 2700 seconds | Can fire. |
| Turns | 40 | Can fire. Dispatch's cap is not this number. |
| Warn | 65 percent, or 130000 tokens in | Warn only. Do not spawn. |
| Pack | 70 percent of the context field | Pack. Do not spawn yet. |
| Close | 190000 tokens in, or the same ratio of `context_pct` | Can fire. |
| Heartbeat quiet | 180 seconds, or pid not alive | Recorded as quiet. Does not fire, pack, or close. |

A quiet or dead pid is not treated as a fresh window. `tick` with
`dry_run` computes the projection and does not write it. `poll_once`
without the spawn opt-in can write a heartbeat, a running-session pointer,
and a snapshot when the state is packing or armed. Writing that projection
is not launching a seat.

Pins live in `tests\test_resession.py`: Claude plans raise `ANTHROPIC_OFF`,
the grok plan stays `execute` false with the window above, other doors stay
dry with `UNMEASURED`, and `spawn_auto_resession(..., execute=False)` does
not execute. This page does not report a pass count. A green pin file is
not a claim that the live clock has spawned, or that COSMOS is finished.
