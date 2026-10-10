# Clusters package

`cosmos-clusters` 0.1.0 is the Clusters backend on this tree. The import package is `clusters`, under `clusters/`. It requires Python 3.11 or newer. The project text says it supervises harness-seated agent clusters.

This page names the package, the command-check entry, and the refusal rules visible in that code. It is not a claim that COSMOS is finished, and it is not a claim that every feature index row is a shipped product. `clusters/docs/INDEX.md` uses **built** for “the plugin already stores and enforces this row.” That word is not a completion stamp for COSMOS.

The package does not write `live/`, does not take `CCR.lease`, and does not open a second ledger. Its store is an append-only JSONL projection (`events.jsonl` under the caller’s root). Views are folds of that file. The COSMOS ledger stays the authority.

Management rules stay in `clusters/docs/01_CLUSTERS.md` (Keith, 2026-09-30). Routes are listed in `clusters/API.md`. Feature notes are `clusters/docs/FEATURES.md` and `clusters/docs/INDEX.md`. Those files are the longer record. This page does not paste their source, or the plugin source.

## What it is, and what it is not

A cluster can hold agents, other clusters, or both. A cluster may have a manager. The product text says ORC can manage clusters and Pilot can manage agents, clusters, managers, and ORC. HERO PACKs are rules, skills, wrappers, and environments, scoped to an agent, a cluster, or both. The backend stores those records. It does not draw the console. The README says the graphical interface is a separate agent.

The cDeck Cluster tab is a different UI. In `builds/cdeck/ui/deck_tabs.js` the tab id is `cluster` and the hint is “ORC · stacked agents · seven cards.” `builds/cdeck/ui/deck_cluster.js` is a deck roster: it watches agents and treats a manager seat as a label update. It does not start a process, and it is not this package, not the JSON API, and not a second Core.

## Run

From `clusters/` (not the repo root):

```
py -3.14 -m clusters --root <projection-dir> --port 8780
py -3.14 -m pytest -q
```

`python -m clusters` calls `clusters.api.main`. There is no `project.scripts` entry in `clusters/pyproject.toml`. The listener accepts only `127.0.0.1`. Any other host raises `Refuse("BIND")` before a socket is opened. The default port is 8780. The projection directory must not be the COSMOS `live` tree; the store constructor runs the path guard below.

Pytest is configured in that `pyproject.toml` with `pythonpath = ["."]` and a basetemp of `V:/streams/clusters/_pytest_tmp`. Run it from the package directory. This page does not report a pass count.

`py -3.14 -m clusters.grade <module> [module...]` is a separate 4C receipt for one module file plus `tests/test_<module>.py` when that test exists. The four checkers are `py_compile`, `ruff`, `mypy`, and `pytest`. A missing checker is `MISSING` (code 127), not a pass. Pytest exit 5 is `NO_TESTS`. `FAIL` or `MISSING` blocks the receipt. Receipts are written under `V:\streams\clusters\receipts`, not under `live/`. That grade command is not the command-policy check.

## Check entry

The command check is `clusters.policy.check_command(store, *, command, turbo=False, branch="")`.

HTTP entry: `POST /v1/policy/check`. The route table in `clusters/api.py` maps that path to `Console.check_command`, which calls `check_command`. Body fields are `command` (required string), `turbo` (bool, default false), and `branch` (string, default empty).

The function returns `{decision, code, detail}`. It does not append a store row and it does not raise `Refuse` for a hard command hit. A refused command is still HTTP 200 with `decision` set to `refuse`. Raised `Refuse` errors elsewhere on the API are HTTP 409 with `{error, detail}`.

`turbo` is accepted and then discarded. A true turbo flag does not add commands to the allowlist.

`clusters.perms.decide` calls `check_command` first. If that decision is `refuse`, `decide` returns it unchanged. A category set to allow cannot override a hard refusal.

A different function, `clusters.spend.check`, is `POST /v1/spend/check` (`provider`, `usd`, `tokens`). That is a spend-projection gate (daily cap or smart pace). It is not `check_command`, and it is not Core SpendGate. Only a verdict of `VERIFIED` reduces the cap. An unmeasured observation pauses.

## Refusal rules

`clusters.refuse.Refuse` carries `code` and `detail`. `to_public()` is `{error, detail}`.

`clusters.policy` states that `FLAG`, `DESTRUCTIVE`, `PROTECTED`, `LIVE_TREE`, `DENY`, and `LIMIT` always refuse. An empty claim stays `RECORDED`. It is not evidence that a command ran. `clusters.verify.judge` marks a claim `VERIFIED` only when both `source` and `observed` are non-empty. Otherwise the claim is `UNMEASURED`.

### `check_command` order

The command is whitespace-collapsed, then tested in this order:

1. **FLAG** (`decision` `refuse`). A case-insensitive hit on `--dangerously-skip-permissions`, `--danger-full-access`, `--full-auto`, or `--ignore-user-config`. The same code is used when the text contains `grok.exe`. The detail is the flag, or `grok.exe`.
2. **DESTRUCTIVE**. A hit on `rm -rf`, `rm -fr`, `remove-item -recurse`, `remove-item -force -recurse`, `git clean`, `git reset --hard`, `drop database`, `drop table`, `format c:`, `format d:`, `del /s`, or `rmdir /s`.
3. **PROTECTED**. A push onto `main`, `master`, `origin/main`, or `origin/master`. The branch argument counts when it is one of those names and the command contains `push`. A `git push` destination counts after an optional leading `+` and after a refspec colon, including a `refs/heads/main` or `refs/heads/master` form.
4. **LIVE_TREE**. The substrings `cosmos/live` and `cosmos\live`, or any path-like token whose segments include `live`.
5. **DENY**. A stored deny phrase, after collapsing whitespace, is contained in the command.
6. **APPROVAL** (`decision` `needs_approval`, detail `shell chain`). The command contains `&&`, `||`, `;`, `|`, `&`, a backtick, or `$(`. This is not an allow. It is also not one of the always-refuse codes.
7. **OK** (`decision` `allow`). The command equals a routine phrase, or starts with that phrase plus a space. The built-in phrases are `git status`, `git diff`, `git log`, `git rev-parse`, `pytest`, `py -3.14 -m pytest`, `python -m pytest`, `ruff`, `py_compile`, `python -m py_compile`, `npm test`, `dir`, and `ls`, plus any stored allow phrases.
8. Otherwise **APPROVAL** with detail `not on the routine allowlist`.

`POST /v1/policy/limits` calls `set_limits`. A non-list, or an item that is not a single-line string, raises `Refuse("LIMIT")`. Accepted phrases are stored. Storing them does not mean a command ran.

### Path guard

`guard_path` runs on the store root and on seat paths:

- Empty or non-string: `PATH` / `empty`.
- A NUL, a UNC prefix `\\`, or a `file:` prefix: `PATH` / `rejected`.
- A `..` part: `PATH` / `rejected`.
- A path segment `live`, or a path that ends in `:live`: `LIVE_TREE`.

### Secrets

`scrub` walks the body. A key named `token`, `secret`, `password`, `api_key`, `authorization`, `credential`, `access_token`, or `refresh_token` raises `SECRET` when the value is not `""`, `None`, or `False`. Nested dicts are scrubbed. A profile path may be stored. A token value may not.

### Matrix and git guards

`perms.decide` categories are `file`, `shell`, `git`, `network`, and `mcp`. Levels are `allow`, `ask`, and `deny`. An unknown category or level raises `MATRIX`. If no matrix row is stored, the level used is `ask`.

After `check_command` returns something other than `refuse`, these still refuse, and a git allow plus turbo cannot clear them:

- `git push` with a `--force` or `-f` token: `FORCE_PUSH`.
- `git branch -d` or `git branch -D`: `BRANCH_DELETE`.
- a command that starts with `git merge`, or contains ` git merge `: `MERGE`.
- `git push`: `PUSH_GUARD`.

Category `deny` returns `DENY`. Category `ask` returns `needs_approval` / `ASK`. Category `allow` returns `OK` only after those guards.

`clusters.gitx.classify` names `force_push`, `branch_delete`, `merge`, and `push` as refused operations. It does not run them. Read names are `status`, `diff`, `log`, and `rev-parse`.

`clusters.changes.plan_worktree` and `request_push` record intent only. They do not run git. A protected branch raises `PROTECTED`. An unconfirmed push raises `CONFIRM`. A recorded push intent keeps `executed` false and `pushed` false. `gitx` commit text is not a git commit. A review bundle is not a pull request.

### Seat, bind, and session cap

`clusters.harness.plan_seat` refuses `UNKNOWN_VIA` unless `via` is `native` or `cosmos-code`. Hero `grok` with `via=native` raises `GROK_EXE` (`grok.exe` is not a worker). A blank task raises `PACK_INCOMPLETE`. The public plan keeps `seated` false. `execute` defaults off. If the caller sets `execute` and the door is `grok` or not executable, the call raises `NOT_EXECUTABLE`. `grok.exe` is not started. A missing harness is `UNMEASURED` with `seated` false, not a seat. When `execute` is on and the door is executable, the code may call the harness `live_call` and still reports `seated` false and verdict `RECORDED` (“live_call is an observation”).

Opening a session when the open count is already `SESSION_CAP` (50) raises `SESSION_CAP`. Shortcut storage uses a separate cap of 6.

Other modules raise `Refuse` with their own codes (session, board, catalog, quota, and the rest). Those codes are local to each call. They do not replace the command-check order above.
