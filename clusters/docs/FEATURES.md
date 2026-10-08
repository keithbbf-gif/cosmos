# CodeAgentSwarm features taken for the Clusters backend

Source read 2026-10-01 from https://www.codeagentswarm.com/en and the About and coordinator guides linked from that page. Product version named on the page: 2.4.0. Creator named there: Arturo García. This list is what their site claims. It is not a claim that COSMOS already does it.

The graphical console is another agent's work. This stream implements the backend these features need.

## Workspace

1. One workspace for many coding agents, supervised together.
2. Parallel sessions. Each agent has its own project, context, and task.
3. Mix vendors in one swarm. Named CLIs: Claude Code, Codex CLI, Antigravity CLI (`agy`), OpenCode, Kimi Code, Grok Build (`grok`), Cursor Agent (`cursor-agent` over ACP), Muse Code, Pi, Devin CLI.
4. Bring your own subscription. The app is not a model provider. Provider quotas stay with the provider.
5. Code stays on the machine. The backend does not upload a worktree.
6. Session cap named on the Pro list: 50 agents.
7. Independent processes. One session finishing or blocking does not close the others.
8. Grid, Tabs, and List as views. Resizable panel bounds. The GUI draws them. The backend stores view and bounds.
9. Dynamic titles for what each agent is doing.
10. Pinned coordinators ahead of other sessions.
11. Project organization: each project's agents, task board, and history stay together.
12. Unlimited projects.
13. Six project shortcuts.
14. Unlimited agent shortcuts.
15. Keyboard shortcut bindings (the map, not the key listener).
16. Per-project setup that survives switching projects.
17. Desktop platforms named by them: macOS 12+, Windows 10/11, Linux. This backend is the Windows COSMOS service. It does not ship their installers.

## Coordinators (2.4.0)

18. A coordinator is a chat whose job is to plan and delegate.
19. Project coordinator: one per project, including that project's worktrees. Sees that project's open chats. Delegates to worker sessions.
20. Global coordinator: one. Sees every configured project, including new ones. Delegates to project coordinators or to workers.
21. Both may run at the same time. A second coordinator for the same scope is refused. The existing one is reopened.
22. The first real goal starts the plan. A greeting does not.
23. Small work stays on the coordinator. Substantial work becomes worker sessions. An already-open suitable session is reused before a new one is opened.
24. Workers may use a different door and model from the coordinator.
25. Workers open without stealing focus. Focus is GUI state. The backend marks them background.
26. Workers are real sessions the operator can open.
27. Messages from the coordinator are marked Assignment, Follow-up, or Correction.
28. Session communication is a privacy setting. It applies to sessions opened after it is turned on. Sessions may ask each other a focused question. The answer is a request card.
29. The coordinator does not poll. It reports when asked, from evidence the workers stored.
30. Closing a worker that is working, has queued messages, or is waiting for approval requires confirmation. A coordinator closes only workers it opened.
31. Coordinator permissions are the session's own permissions. The role adds none.
32. Closing the coordinator ends the role and does not stop workers. The chat remains in history.
33. Coordinators run on this desktop. A paired remote does not become the coordinator host.

## Task board

34. Columns observed on the page: Pending, Auto, In Progress, In Testing, Completed.
35. Create, label, and assign a task to a door, a model, and a workspace.
36. Agents read and update the board through a tool surface (their MCP). Here that surface is the board API. A move that claims done without evidence stays unmeasured.
37. Auto lane: queue with the lightning action, pick the agent or accept defaults, start up to a concurrency limit, watch, then review in testing.
38. Each auto task may use a different door and model.
39. Finished work waits in testing. Completing it is a review, not an automatic merge.
40. Search and project filter are query parameters on the board API.

## History

41. Full conversation history across supported sessions.
42. Search over what the operator wrote, what the agent replied, and snippets.
43. Organize by project, by date, and by continuation chain.
44. Resume pointer. The backend does not claim a door can resume unless that door's record says so. Cursor resume stays off until a probe reports `loadSession`. This build does not probe.

## Changes, git, notifications

45. Live file-change records and a diff per change. Hashes are the evidence.
46. Review the diff before any commit intent.
47. Git worktree plan per session so two agents do not share one checkout. The backend plans the path. It does not run git.
48. Commit proposal from recorded changes. It is a proposal, not a commit, and not a push.
49. Protected branches cannot be pushed: `main`, `master`, and their `origin/` forms.
50. Notifications when an agent finishes, needs input, or fails. The backend emits the record. The GUI delivers it.

## Permissions and turbo

51. Per-agent permission check for commands and paths.
52. Turbo skips confirmation only for the routine allowlist.
53. Hard refusals stay on under turbo: protected-branch push, destructive delete, live-tree writes, `grok.exe`, and the harness-forbidden flags `--dangerously-skip-permissions`, `--danger-full-access`, `--full-auto`, `--ignore-user-config`.
54. Their site also describes a wider YOLO mode in a comparison article. This backend does not implement an unbounded skip.

## Spend

55. Daily cap per provider, in dollars and tokens.
56. Smart pace: spread what remains of the window across the days left.
57. At the limit: notify, pause new work, or stop.
58. One +5% bump for today, once.
59. Figures count only when the caller supplies a source and an observed value. A number without that stamp does not lower the remaining cap. Unmeasured spend fails closed.

## Accounts, MCP, mobile

60. Managed credential profiles for Claude Code and Codex: label, default, and a profile directory pointer. Secret bytes are refused. Other doors use the current CLI profile.
61. Switch account only for an idle session.
62. MCP catalog, enabled per project, not fetched by this service: Notion, Supabase, GitHub, Slack, Atlassian, Playwright, Puppeteer, Google Drive, Postgres, Brave. Groups: database and storage, browser, team. Install-all enables the catalog. Tokens are not stored.
63. Mobile Connect: pair a device, follow sessions, post a message. The desktop must be online. The pair token is returned once and stored as a hash. No cloud host.

## Roadmap item they still mark planned

64. Autonomous mode: goal in, swarm decomposes, prioritizes, executes, and collaborates. The coordinator plus the auto lane cover the supervised form. Nothing in this backend ships a goal by itself or starts a provider call unless the caller passes `execute=True` to the harness port, and even then `grok.exe` and an unseated door do not start.

## COSMOS rules that bind every feature

65. A cluster is agents, agents plus clusters, or only subclusters. A manager agent is optional. The global coordinator is the ORC seat. The operator API is the Pilot. HERO PACKS are rules, skills, wrappers, and environments on an agent, a cluster, or both.
66. One Core, one ledger, one publish path. This store is a rebuildable projection. It does not write `live/` and it does not start `grok.exe`.
67. Seating goes through the COSMOS harness (`g47.seat`). `seat` does not start a process. `live_call` is an observation, and its return does not say the agent is seated.
68. A claim without `source` and `observed` is `UNMEASURED`. A refusal is a result, not a fake success.
