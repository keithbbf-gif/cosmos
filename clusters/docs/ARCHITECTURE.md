# Clusters backend architecture

Keith 2026-10-01. Backend only. The graphical console is another agent. This tree is `V:\streams\clusters`. It does not write `V:\A\Ai\COSMOS` and it does not write `live/`.

## What this is

A Python package, `clusters`, that supervises harness-seated coding sessions the way CodeAgentSwarm describes, under the Clusters rules in `01_CLUSTERS.md`.

The GUI reads and writes JSON over `127.0.0.1`. It does not own the rules. The package owns them.

## How a call is seated

```
Pilot / GUI / harness caller
        |
        v
   clusters.api          HTTP on 127.0.0.1 only
        |
        v
   clusters.console      one facade
        |
        +-- mesh          projects, clusters, subclusters, HERO PACKS
        +-- sessions      the 50 slots, status, title, layout
        +-- coordinators  ORC (global) and manager (project)
        +-- board         kanban and the auto lane
        +-- history       searchable transcript
        +-- changes       diffs, worktree plans, commit proposals
        +-- policy        turbo allowlist and hard refusals
        +-- spend         daily cap and smart pace, projection only
        +-- catalog       doors, account pointers, MCP flags, shortcuts, mobile, notifications
        |
        v
   clusters.harness      g47.seat.seat by default
                         g47.seat.live_call only when execute=True
                         grok.exe never
```

`g47` is imported from the path the caller passes. The stream default is `V:\streams\cosmos_code\harness\G47`, because that is where the current harness sits. A missing harness is `UNMEASURED` / `HARNESS_ABSENT`. It is not a fake seat.

Known heroes today: `luna`, `sol`, `mini`, `glm`, `gf38`, `deepseek`, `ling`, `grok`. Known doors are the catalog in `clusters.models`. A CLI their site names and the harness does not seat stays in the catalog with `seated: false`.

## Projection, not a second ledger

`Store` appends JSONL under a root the caller chooses. Views are folds of that log. Spend numbers are a projection of observations the caller stamps. Publication into the COSMOS ledger stays on Gitur. The log carries no secret fields.

## Trust but verify

| Claim | Required evidence | If it is missing |
|---|---|---|
| status finished or failed | `source`, `observed` | the verified status does not flip |
| dynamic title | `source`, `observed` | the verified title does not flip |
| coordinator plan was the model's | `source`, `observed` | workers open as an operator plan, verdict `UNMEASURED` |
| spend | `source`, `observed` | it does not reduce the remaining cap; new work pauses |
| file change | the service hashes `before` and `after` | no hash, no change record |
| door can resume | catalog flag | history returns a pointer and `resume: false` |
| push happened | never claimed | protected branches refuse; other branches record an intent only |

`seat()` returning is not "the agent is seated." `live_call` returning is an observation. `seated` stays false in both public results.

## Hard refusals

These hold with turbo on or off.

- Path ends with `/live`, contains `/cosmos/live`, uses `..`, a null, a UNC prefix, or a `file:` URL.
- Starting `grok.exe`.
- Flags the harness already forbids: `--dangerously-skip-permissions`, `--danger-full-access`, `--full-auto`, `--ignore-user-config`.
- Destructive commands (`rm -rf`, recursive force delete, `git clean`, `git reset --hard`, drop database, format).
- Push to `main`, `master`, `origin/main`, `origin/master`.
- A second global coordinator, or a second coordinator on the same project.
- Session 51.
- Project shortcut slot outside 1..6, or a seventh shortcut.
- Secret bytes on an account, an MCP row, or a mobile pair.
- Closing a busy worker without `confirm=true`.
- Completing a task that is not in testing, or that has no evidence.
- Mobile post while the desktop is offline.
- Account switch on a session that is not idle.

## Module owners

| Module | Responsibility |
|---|---|
| `models.py` | Constants, door catalog, MCP catalog, dump helpers |
| `store.py` | Append-only log, fold, view, ids |
| `refuse.py` | `Refuse`, path guard, secret guard, destructive and push checks |
| `verify.py` | `judge(claim, evidence) -> VERIFIED, UNMEASURED, or RECORDED` |
| `harness.py` | Plan a seat. Execute only on an explicit flag. Never grok.exe |
| `sessions.py` | Slots, status, titles, layout |
| `mesh.py` | Projects, clusters, members, manager, packs |
| `coordinators.py` | Project and global coordinators, goals, plans, comms |
| `board.py` | Kanban and auto tick |
| `history.py` | Messages and search |
| `changes.py` | Diff records, worktree plan, commit proposal, push intent |
| `policy.py` | Command decisions |
| `spend.py` | Caps, pace, bump, check |
| `catalog.py` | Doors, accounts, MCP, shortcuts, mobile, notifications |
| `console.py` | Facade the HTTP handler calls |
| `api.py` | `127.0.0.1` JSON |

## HTTP

`python -m clusters.api --root <dir> --port <n>`. Default port 8780. Bind `127.0.0.1` only. Routes are the method names in `plugin/API.md`. Errors are `{"error": "<CODE>", "detail": "..."}`.

## What is deliberately absent

No window toolkit, no CSS, no panel renderer. No git subprocess. No provider HTTP. No token store. No write into the live COSMOS tree. No claim that an unseated door ran.
