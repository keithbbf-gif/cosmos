# CCr disposition — GitHub `origin/main` 47 commits (2026-09-05)

Live tree is authority. Origin-only tip files were **applied**, **tabled for review**, or **tabled stale**. Nothing deleted.

Merge-base: `419bfb5` (2026-08-24). Origin tip: `14addfc`. Local tip at harvest: `ebd5e24`.

## APPLY (on the live tree)

| Origin path | Live path | Note |
|---|---|---|
| `docs/AGENTS.md` | same | Copilot/Bugbot. CCr: Composer 2.5 → **Opus 5**. |
| `docs/AGENT_LANDSCAPE.md` | same | GitHub/GitLab review landscape. |
| `work_orders/drop/wo-20260902T*.json` (legal names, 17 files) | same | Inbox harvest. Ingest daemon owns next state. |
| `inbox/wo-20260902T201500.json` etc (3) | `work_orders/drop/` | Misfiled `inbox/` — stored on the real drop path. |
| `queries/q-20260902T*.json` (2) | `queries/` | Query channel; not CORE. |

Already present locally (no overwrite): `docs/WORK_ORDER_SOP.md`, `docs/VERDICT_SPEC.md`, `docs/ARA_STATUS_PROTOCOL.md`, `docs/ARA_POLL.md`, `docs/CURSOR_EXEC.md`, `docs/ADVERSARIAL_LOOP.md`.

## TABLE STALE (stored, not on CORE hot path)

`work_orders/ccr/origin-47-stale/`

| File | Why stale |
|---|---|
| `cosmos_daemon.py` | Root poller. Live ingest is `cosmos/cosmos_sgh_drop_ingest.py` + work-order runner. |
| `SOP.md` | Root SOP. Canon is `docs/WORK_ORDER_SOP.md`. Do not drop SOP at repo root. |
| `CRON.md` | Invents a second clock. Live is CLOCKS / Pulse. No bats. |
| `cosmos-test.txt` | Orchestrator write probe, not CORE. |
| daemon test fixtures | Travel with the stale daemon. |

Colon-named drops (`wo-…-05:00.json`) were **removed on origin** after ingest. Not recreated (Windows-illegal). History remains on `origin/main`.

## TABLE REVIEW (open WOs, not executed this tick)

Runtime-binding gate WOs (`wo-20260902T1757*`–`191500`), daemon git-push WO, query-handling WOs, CLOCKS topology critic (`wo-20260904T120000` — **do not merge PR #32/#38**), lawsuit-notes WO (`wo-20260902T203000` — Legal stream, parked), Composer 2.5 race text in origin `docs/AGENTS.md` (CCr already patched).

## GitHub copy (Keith 2026-09-05 — this hitch is closed)

Join landed locally: `087a3b5` (`-s ours`; second parent `origin/main`). **Push refused** GH001 `kdash/cosmos-voice.apk` 164.52 MB in `4f88953` (one of the 16 unique local commits). Windows `filter-branch` over the join died on colon-named origin paths (`wo-…-05:00.json`).

Keith: store the APK as a **draft** — that **clears this hitch**. GitHub `main` stays `14addfc` until a later sync that does not send that blob. Live tree remains the engine room.

APK stays on disk (`kdash/cosmos-voice.apk` + `kdash/_draft_cosmos-voice.apk`). Untracked. `*.apk` gitignored. Note: `kdash/ANDROID_VOICE_DRAFT.md`.

## Do not

- Merge PRs #30 #32 #36 #37 #38.
- Reset live tree to origin (would delete CORE).
- Force-push (would drop the 47 from GitHub history).
- Recreate colon filenames.
- Delete the APK (draft seed).
- `filter-branch` `419bfb5..HEAD` on Windows (colon paths in origin history).
