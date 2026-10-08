# Clusters

## What it is

Backend for the COSMOS Clusters console. A cluster is agents, clusters, or both. A Manager Agent is optional. ORC can manage several clusters. Pilot can manage agents, clusters, managers, and ORC. Management uses HERO packs: rules, skills, wrappers, and environments. The store is an append-only JSONL projection (`events.jsonl`). Views are folds. Seating goes through the COSMOS harness and does not start a process. The listener is local JSON on `127.0.0.1`. Routes are `clusters/API.md`, prefix `/v1`.

Management rules stay in `clusters/docs/01_CLUSTERS.md`. That file is the in-tree copy of the section of record. It is not a work order, and it is not this package's code.

## Where it lives

Repo path: `V:\A\Ai\COSMOS\clusters`. Applied 2026-10-07 from `V:\streams\clusters`. The streams original stays in place. Package name: `cosmos-clusters` (`clusters.__version__` is `0.1.0`). The graphical console is a separate agent. This package does not draw it.

## Entry points

```
py -3.14 -m clusters --root <projection-dir> --port 8780
py -3.14 -m pytest -q
py -3.14 -m clusters.grade <module>
```

`clusters.__main__` calls `clusters.api.main`. `serve(console, host="127.0.0.1", port=8780)` builds the listener. `Console(root)` is the facade. `Store(root)` is the projection. `plan_seat(hero, task, where, via="cosmos-code", *, execute=False, harness_root=None)` calls `g47.seat.seat` when `V:\streams\cosmos_code\harness\G47` is present. `grade_module(name)` writes a 4C receipt under `V:\streams\clusters\receipts`. Policy: `check_command`, `set_limits`. Spend projection: `set_budget`, `observe`, `bump_today`, `check`. Path and body guards: `guard_path`, `scrub`.

## What it refuses

The live tree (`guard_path` raises `LIVE_TREE`; `check_command` returns `LIVE_TREE`). `grok.exe` (`GROK_EXE`, and `forbidden_flag`). Pushes to `main`, `master`, `origin/main`, or `origin/master` (`PROTECTED`). Destructive commands (`DESTRUCTIVE`). Hard flags such as skip-permissions (`FLAG`). Secret-shaped body keys (`SECRET`). A bind host other than `127.0.0.1` (`BIND`). A projection root that is the COSMOS `live` tree. `plan_seat` keeps `seated` false. `execute` is off unless the caller sets it, and even then `grok.exe` does not start. A missing harness is `UNMEASURED`, not a seat. Empty evidence is `RECORDED`, not proof a command ran. Turbo does not widen the routine allowlist (`APPROVAL`). The spend module refuses to treat itself as a second ledger. Only verified observations reduce a cap. Unmeasured spend pauses.

## What it is not

Not the graphical console. Not Core, and not the Core ledger. `events.jsonl` is a rebuildable projection. `clusters.spend` is not `cosmos_spend`. Not a process spawner. Not Sessions (`builds/session-plugin`, `builds/sessions-app`). Not a publisher into the live tree. Publication stays on Gitur.

## Grade

On main `501fdee2` (2026-10-08), Clusters passed `py_compile`, `ruff`, `mypy`, and `pytest` under `grade.py` flags. Those mypy flags are `--follow-imports=silent` and `--ignore-missing-imports`. Bare mypy fails 2. `mypy --strict` is 866 errors in 88 files and is not the 4C bar. That is the recorded grade. It was not re-run for this note.
