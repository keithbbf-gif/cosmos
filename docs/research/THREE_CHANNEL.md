# Three-channel mesh loop (design, 2026-09-19)

Corpse WOs asked to extend `cosmos_daemon.py` to poll `queries/`. **Do not add a second process.** Do not spawn a sub-agent from the daemon.

## Channels

| # | Channel | Path | Who | Return |
|---|---|---|---|---|
| 1 | **Query** | `live/state/queries/q-*.json` → `queries/replies/q-<stamp>-reply.json` | Orch answers. Daemon **only** notices open files (`--once`). No LLM spawn. | `status`: `open` \| `answered` |
| 2 | **Work order** | `work_orders/drop/` six-field | WOMBAT / runner. P10 propose. | Output file; FAIL → `fail_xfer` JSONL |
| 3 | **Build** | Gitur PR → Judge → CCr LiT | Coder HERO + Luna KEEP | PR + attempt row |

One append-only log for returns: student `live/state/attempts/attempts.jsonl` (`cosmos-score-attempt/1`) plus existing ledger. Do not a fourth JSONL.

## Query poller

`cosmos/cosmos_query_channel.py --once --root <live>`  
GET never mkdir. Missing `queries/` → `kind=UNMEASURED`, n=0. Open `q-*.json` listed; replies written **only** when an orch file already exists to copy — never invent an answer.

Not: second daemon, GUI flash, new window, grok.exe.
