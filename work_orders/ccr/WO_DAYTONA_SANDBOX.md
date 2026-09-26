# Gitur BUILD — Daytona/E2B attempt sandbox backends (cannot reach V:\)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/daytona-sandbox` from GitHub `main`. Not unique HEAD `8b5ad84`.
**Lane B:** Cursor Cloud Agent, Opus 5 / Sonnet class. Composer 2.5 / Auto refused. Do not change Opus T.
**P10:** PROPOSE only. CCr writes CORE. Never write the live tree from this run.
**Do not:** spawn grok.exe, pull unique HEAD 8b5ad84, merge leftover PRs, USPTO, install OpenHands as a scheduler, a second Core, LangGraph/Temporal/n8n.

FIRST read `docs/AGENT_BRIEF.md` and `docs/AGENT_BOUNDARIES.md`. Then `docs/STEAL_MAP.md` order item 3.

## Already on this tree (do not re-build)

- `cosmos/cosmos_sandbox.py` — OpenHands **split** (session = ledger / harness = this module / sandbox = Job-Object child). Selftest **5/5**. Host-pen refuse for `V:\Ai`, `V:\OPENWORK`, OneDrive. Attempt dirs under `live/work/attempts/<id>`.
- `cosmos_workspace.assert_not_live` / `refuse_tree_cwd`. Worker cwd is still on `V:\` (`live/work`). That is the wipe lesson not yet true.
- Job-Object spawn (`CreateJobObjectW`, kill-on-close, 8 procs). Keep it as the **local** backend.

Daytona / E2B / Modal are **named** in the module docstring and **not composed**.

## Job

Compose **Daytona** and **E2B** as named backends behind `cosmos_sandbox.py` so an attempt sandbox **cannot reach `V:\`** (host pens `V:\Ai`, the COSMOS repo tree, `V:\OPENWORK`). Docker/Daytona is the isolation that Job-Object-on-host cannot give.

Contract:

1. One facade: `cosmos_sandbox` picks backend `job-object` | `daytona` | `e2b`. Default stays Job-Object when remote backends are unconfigured (fail-closed, not fail-open to host).
2. A remote backend worker **must not** map extra drives. Proof: listing `V:\` / reading a host pen is a typed refuse (`HOST_PEN` / `BACKEND_ISOLATION`), never a green log.
3. OpenHands **split**, not OpenHands as scheduler. Do not add a clock, do not claim jobs, do not write the ledger from the sandbox process.
4. Keith owns credentials. Propose a config **role** under the live root (e.g. `config/sandbox_backend.json` schema + empty-unconfigured refuse). Never paste keys. Never handle money.
5. Kernel compose, if any, is fail-open like other satellites (`attach_to_kernel`) and must not abort READY when Daytona/E2B are absent.
6. Selftest: keep the existing 5 Job-Object pins. Add backend pins that prove isolation **without** a live Daytona/E2B account (stub / recorded refuse). Live vendor calls are UNMEASURED until Keith pastes creds.

## Bite

- Unconfigured Daytona/E2B → typed refuse, worker still on Job-Object or refused — never silent host cwd.
- `assert_sandbox_cwd` still refuses `live/state` and host pens.
- `py -3.14 cosmos\cosmos_sandbox.py --selftest` stays green; new pins named.
- No new scheduler. No `schtasks`. No in-process cron.

## Output

Unified diffs + rationale under the work-order Output (`proposals | DAYTONA_SANDBOX.json`). One job, one branch, one PR `WO: Daytona/E2B sandbox backends`. Gitur BUILD. autoCreatePR.

A claim is not evidence. Quote the selftest line and the refuse kind.
