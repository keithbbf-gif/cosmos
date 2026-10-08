# Clusters feature index

Organized 2026-10-01 from https://www.codeagentswarm.com/en, the guides index, and the coordinator, auto-kanban, and turbo pages. Similar-program notes are collected under `research/` as those pages are read. Nothing here is published to the live COSMOS tree.

Status: **built** means the plugin already stores and enforces it. **wave 2** means this pass adds the module. **gui** means the other agent draws it. **refused** means the site describes it and this backend will not do it.

## Built

| Id | Feature | Module |
|---|---|---|
| W1 | Parallel sessions, cap 50, own project and task | `sessions.py` |
| W2 | Grid, tabs, list, panel bounds | `sessions.py` |
| W3 | Dynamic title, verified only with evidence | `sessions.py` |
| W4 | Projects, six shortcuts | `mesh.py` |
| W5 | Clusters, subclusters, manager, HERO PACKS | `mesh.py` |
| W6 | Project and global coordinator, one each | `coordinators.py` |
| W7 | Greeting does not start a goal | `coordinators.py` |
| W8 | Plan opens workers or reuses one | `coordinators.py` |
| W9 | Unmeasured plan stays an operator plan | `coordinators.py` |
| W10 | Report on ask, polled false | `coordinators.py` |
| W11 | Close only own workers, confirm if busy | `coordinators.py` |
| W12 | Session comms for sessions opened after the switch | `coordinators.py` |
| W13 | Kanban columns including Auto and In Testing | `board.py` |
| W14 | Complete only from testing, with evidence | `board.py` |
| W15 | Auto tick plans a seat and does not execute | `board.py` |
| W16 | Searchable history, resume flag, claimed false | `history.py` |
| W17 | Diff hashes, worktree plan, commit proposal, no push | `changes.py` |
| W18 | Protected branches | `changes.py` `policy.py` |
| W19 | Turbo does not allow non-routine commands | `policy.py` |
| W20 | Hard refuse: destructive, live tree, grok.exe, skip-permission flags | `policy.py` `refuse.py` |
| W21 | Daily cap, smart pace, +5% once, unmeasured pauses | `spend.py` |
| W22 | Door catalog, seated false where the harness is not | `models.py` |
| W23 | Claude and Codex account pointers, idle switch, no secrets | `catalog.py` |
| W24 | MCP enable per project, no token, no download | `catalog.py` |
| W25 | Agent and key shortcuts | `catalog.py` |
| W26 | Mobile pair hash, desktop online, message | `catalog.py` |
| W27 | Notifications record | `catalog.py` |
| W28 | Harness plan, seated false, grok.exe never starts | `harness.py` |
| W29 | Local JSON on 127.0.0.1 | `api.py` |

## Wave 2 — coded in this pass

| Id | Feature | Module | Site basis |
|---|---|---|---|
| P1 | Allow, ask, or deny per file, shell, git, network, and MCP | `perms.py` | Turbo guide: categories, not one YOLO switch |
| P2 | Git guards: push, force-push, merge, branch delete stay deny | `perms.py` `gitx.py` | Same guide |
| P3 | Auto defaults and three queue paths: drag, lightning overrides, new card | `lane.py` | Auto-kanban guide |
| P4 | Per-task reasoning, permission mode, workspace folder or worktree or branch | `lane.py` | Auto-kanban guide |
| P5 | Finished session moves its card to In Testing and emits a note | `link.py` | Auto-kanban and notifications |
| P6 | needs_input is a claim and needs evidence | `sessions.py` | Notifications: the agent really is waiting |
| P7 | Follow-up and correction messages | `relay.py` | Coordinator guide |
| P8 | Small work stays on the coordinator | `relay.py` | Coordinator guide |
| P9 | Global coordinator can hand a goal to a project coordinator | `relay.py` | Coordinator guide |
| P10 | Commit text assembled from recorded diffs, not from a model, unless evidence says so | `gitx.py` | Git integration, AI commits |
| P11 | Review bundle. Not a created pull request | `gitx.py` | T3 comparison: they end in a PR. We record the review. |
| P12 | Skill paths enabled per project. Bodies refused | `skills.py` | Skills marketplace mention. Harness: skills are paths |
| P13 | Quota window and prorata. Missing stamps pause | `quota.py` | Spend sidebar and their quota indicator |
| P14 | Door mode: agent, plan, ask, chat, cli, default | `room.py` | Cursor and Pi guides |
| P15 | Cancel intent. No process is killed here | `room.py` | Cursor permissions and cancellation |
| P16 | Mobile follow: list sessions for a paired token while desktop is online | `room.py` | About: Mobile Connect |
| P17 | Default keyboard map, seeded once | `room.py` | Pro list: keyboard shortcuts |
| P18 | New Claude or Codex session takes the default account | `sessions.py` | Multiple accounts guide |
| P19 | Verified title changes append title history | `sessions.py` | Dynamic titles |
| P20 | One-level kanban subtasks | `subtasks.py` | Kanban subtasks |
| P21 | Bookmarks point at a session or a message. Hide is a flag | `marks.py` | Devin bookmarks |
| P22 | Admit pauses when spend or quota pauses. No third ledger | `allowance.py` | Budget and quota |
| P23 | Git confirmation. Verified only with source and observed. Git is not run | `confirm.py` | Operator git read |
| P24 | Isolation intent. `executed` and `git` stay false | `isolate.py` | Own directory or shared |
| P25 | Seat binding stores door and model. `started` stays false | `bind.py` | Harness binding, not a launch |
| P26 | Attention reason. Nothing is sent | `notice.py` | Waiting seat |
| P27 | Thread active, snoozed, or settled. Settled does not close the session | `thread.py` | Transcript state |
| P28 | Shortcut colour, icon, door, resume, and turbo. Nothing launches | `presets.py` | Project switcher |
| P29 | Work style and image paths on a task. Files are not read | `attach.py` | Auto-kanban first message |
| P30 | Review paths stay unseen until marked. `accepted` stays false | `seen.py` | Review column |
| P31 | Instruction and MCP paths. Import `written` stays false | `instruct.py` | AGENTS.md and mcp.json pointers |
| P32 | Provider conversation id. `resume_claimed` stays false | `doorid.py` | Antigravity and Kimi session ids |
| P33 | Credential route is a path pointer. `copied` stays false | `credroute.py` | Login location, not the secret |
| P34 | Named quota shape. Unmeasured pauses. Spend is not reduced | `qshape.py` | 5-hour, weekly, opus, monthly, credits |
| P35 | Door mode and provider are stored. `applied` and `started` stay false | `doorcap.py` | Pi, Kimi, OpenCode, Grok flags |
| P36 | Host fact and env name. No value is stored and nothing is probed | `hostnote.py` | Host abilities and base URL name |
| P37 | Same-file conflict outcome. Git is not run | `conflict.py` | Two sessions, one file |
| P38 | Per-tool Allow, Ask, or Deny. A missing tool stays ask | `toolperm.py` | MCP marketplace |
| P39 | Headless intent. `started` and `executed` stay false | `headless.py` | grok -p format, turns, sandbox |
| P40 | Plain shell door. `executable` stays false | `models.py` | Bash terminal beside the agents |
| P41 | Seat flags. `written` and `fetched` stay false | `seatflag.py` | Channel, Kimi role, hooks, updater lock |
| P42 | Usage meter. Empty is not unlimited. Logged-out is not stopped | `meter.py` | BYOK, Zen, Cursor pools |

## GUI only

Grid painting, tab chrome, resizable drag, notification toast, project color, discord, installer, auto-update. The backend stores the facts those views read.

## Refused

| Item | Why |
|---|---|
| `--dangerously-skip-permissions` and Codex `--full-auto` | Harness forbids them. Turbo is an allowlist. |
| Starting `grok.exe` | The coding seat is cosmos-code. |
| Writing `live/` or pushing `main` | One live tree. Publication stays on Gitur. |
| Storing provider tokens | Account rows are path pointers. |
| Claiming a seat, a push, a commit, or a resume | The harness and the git module return observations. |
| One-click pull request | A review bundle is stored. The push is not performed. |
| Fetching MCP servers or skill bodies | Enable flags and paths only. |

## How a wave-2 call sits

`console.py` is the only facade `api.py` calls. Wave-2 modules are reached through console methods and `/v1` routes listed in `plugin/API.md`. They append to the same JSONL projection. The English guides that loaded are in `research/cas_pages.md` and `research/cas_unread.md`. The early "still absent" list in that second file is older than P32 through P39.
