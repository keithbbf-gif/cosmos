# Code and harness

COSMOS is not finished. This page is a reading map for three packages on this tree. It is not a completion claim, a task bakeoff, or a second copy of the source.

The three packages are a propose-only coding rail, the planner that builds one harness call, and the control loop around a single model sample. None of them is Core. None of them writes `live/`, takes `CCR.lease`, or opens a second ledger. `grok.exe` is not a worker.

Dispatch stays locked. `cosmos_code.propose.propose` returns `done: false`. The stub provider raises `DISPATCH_LOCKED` and does not start HTTP.

The code grade is four checkers, in this order: `py_compile`, `ruff`, `mypy`, `pytest`. Not five. Not six.

## Three packages

| Package | Path | Import | Version | What it owns |
|---|---|---|---|---|
| COSMOS CODE | `cosmos_code/` | `cosmos_code` | 1.0.0 | Propose path, path jail, red oracle, 4C rows, done bundle. Does not start a provider. |
| G47 | `harness/G47/` | `g47` | 0.2.0 | One plan: pack, argv or rail payload, token cap. `plan` does not spawn. |
| COSMOS Harness | `cosmos_harness/` | `cosmos_harness` | 1.0.0 | Eight layers, eight hooks, host-owned hands, turn cap 8. The model sample is the unbound step. |

Python requirement is 3.11 or newer. None of the three declares a third-party runtime dependency. Dev extras are `pytest`, `ruff`, and `mypy`. Editable install from the repo root is in `cosmos_code/docs/INSTALL.md`. Optional door binaries are not downloaded by that install.

`cosmos_code` and `cosmos_harness` put `harness/G47` on `sys.path` when that directory is present. Their pytest and mypy configs do the same. Import G47 as `g47`, not as a path you assemble beside `live/`.

Seat dumps, attempt trees, vendor source, and `installs/LOCAL.toml` are not part of the product. Do not copy them in to "complete" the packages. `installs/DOORS.toml` is the committed catalog of optional doors. `LOCAL.toml` is generated for one machine.

`harness/G47/CODE.md` still names a streams folder and an older test count. Read the modules on this tree. `harness/G47/README.md` still says not to copy that folder onto `V:\A`. The source this page describes is already the copy under `V:\A\Ai\COSMOS`.

## What a green package is not

A package checker pass is not a finished COSMOS, not a seated model, and not permission to publish `live/`. The enclosure reason stays `policy_only`. `wipe_proof` stays false. Generated code stays blocked from a wipe-proof claim until a real sandbox proof exists. That proof is not in these packages.

CCr still publishes. A worker stop, even with a full done bundle, is propose-only. See [PEN](PEN.md).

## Dispatch stays locked

`propose` in `cosmos_code/cosmos_code/propose.py` is the one propose path.

It refuses a worktree whose resolved path is `live` or sits under `live/` (`LIVE_TREE`). It loads door specs, opens an append-only `session.jsonl`, and, for a nontrivial work order, requires a red oracle before any file write (`NO_ORACLE_SPEC`, `ORACLE_ALREADY_GREEN`). An edit also requires the plan to name a symbol that occurs in the written bodies (`PLAN_UNBOUND`, `NO_SHOT1_IR`). It then asks G47 for a plan and returns a dict whose `done` field is `false`, plus checker rows, ladder blocks, and the session path. It does not call a provider.

`dispatch` is the model-call seam. It refuses unless the session already has `oracle/red` and `plan/bound` (`NO_SHOT1_IR`). When those events exist it still does not send HTTP. `Provider.prepare_call` raises `Refuse("DISPATCH_LOCKED", "no provider is bound")`. The package ships no caller.

`cosmos_code.own.seat_here` asks G47 to seat an approved agent and writes the pack into the attempt. It does not start the native door and it does not start `grok.exe`.

G47 `execute` can start a seated binary. The `g47` CLI does not call it. `plan` prints JSON and returns. Calling `execute` on `cosmos-code` raises `EXECUTE_IS_RAIL`. Calling it on `grok` raises `GROK_NOT_A_WORKER`.

## Four checkers

The four tools are `py_compile`, `ruff`, `mypy`, and `pytest`. A missing tool is never a silent skip. A hung checker is exit 124, and that row is `FAIL`. Checker children drop environment names that contain `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, or `CREDENTIAL`.

Two spellings of "missing" are both in the tree. They are the same fact and not the same token. That mismatch is open.

| | COSMOS CODE `checks4.py` | Harness `checks.py` and `hooks.verify` |
|---|---|---|
| Missing tool | `MISSING` (exit 127) | `UNAVAILABLE` |
| pytest exit 5 | `NO_TESTS` | `NO_TESTS` |
| No Python files | `PROSE` on each of the four tools | `PROSE` on each of the four tools |
| Reply row blocks | `fails_of`: `FAIL` and `MISSING` only | not a reply grader |
| Package / verify gate | `package_blocked`: exactly four rows, every status `PASS` | `verify`: exactly four statuses, every one `PASS` |
| What else blocks that gate | `NO_TESTS`, `NO_CODE`, `PROSE`, `UNAVAILABLE`, any other non-`PASS` | the same idea: any status other than `PASS`, or a count other than four (`CHECKS` when every present token is already `PASS` but the count is wrong) |

`cosmos_code check` uses `package_blocked` and exits 1 on any block. The README sentence that names only `FAIL` and `MISSING` is narrower than the function. `NO_TESTS` blocks that command too. The quality ladder (`quality/ladder.py`) is different again: `MISSING` is `GateUnavailable` and `FAIL` is `GateFailure` on axes D0–D3. `NO_TESTS` and `NO_CODE` are recorded by the checker and are not ladder failures. Do not treat those three views as one verdict.

House ruff, from each package `pyproject.toml`, is line length 120, target `py314`, select `E`, `F`, `I`, ignore `E501`. `cosmos_code/__init__.py` ignores `E402` because it inserts the G47 path before the imports. Package mypy is Python 3.14, `check_untyped_defs`, `ignore_missing_imports`, `warn_unused_ignores`. G47 mypy excludes `seats/`. Strict mypy of the whole repo is not this bar. Do not run ruff or mypy from the repo root. That walk can enter `live/`.

Run each tool from the package directory so that package's `pyproject.toml` is the config. From the repo root, pytest can collect unrelated trees, including paths under `_delme`.

On this reading (2026-10-08, Python 3.14), from each package directory: `ruff check` and `mypy` exited 0, and `pytest -q` reported 34 passed (`cosmos_code`), 25 passed (`harness/G47`), and 49 passed (`cosmos_harness`). `compileall` of those three package and test trees exited 0. That is a package measurement. It does not finish COSMOS.

## COSMOS CODE

Default mode, from the package docstring, is WOMBAT: propose, workspace-write, approval on request, delete policy archive-only. CCr alone publishes. The harness call is G47. This package verifies the proposal.

### Modules

| Module | Role |
|---|---|
| `propose.py` | The propose path. Returns `done: false`. Dispatch stays locked. |
| `doorspec.py` | TOML door rows. Argv stays in G47. A bad row refuses at load. |
| `specs/*.toml` | Nine doors: cosmos-code, opencode, pi, dsh, codex, copilot, grok, openrouter, vertex. `via` must be `g47`. |
| `own.py` | `seat_here`. Materialize a G47 seat. Do not spawn. |
| `checks4.py` | The 4C rows above. |
| `quality/ladder.py` | Stop-worthy rows only. |
| `verify/oracle.py` | Fail before edit, pass after, for a nontrivial work order. |
| `verify/stop_gate.py` | Done needs five hashes. A green session line is not done. |
| `safety/pathjail.py` | Scar-class path jail. Grant list. |
| `safety/archive.py` | The only legal disappearance: move into `_delme`. |
| `safety/hooks.py` | Rewrite `rm` and a delete tool into archive. |
| `safety/scars.py` | Named September 2026 path shapes. |
| `safety/enclosure.py` | Always `policy_only`. `wipe_proof` false. |
| `pack/context_pack.py` | `map_hash` over git HEAD and work-order paths. |
| `session_log.py` | Append-only JSONL. A failed attempt is not model history. |
| `tools/fs.py` | Jailed read, edit, and write. Refuses `live/`. |
| `__main__.py` | `doctor`, `enclosure`, `scars`, `refuse-retry`, `check`. |

### Door negotiation

Every spec binds eight layers: `l1_role` through `l8_mission`. Legal states are `native`, `carried`, `none`, and `file`. Strength is `strong`, `weak`, or `none`. `negotiate` refuses an unbound role or mission (`LAYER_UNBOUND`), a strong door whose wrapper is `carried` (`RESTUFF`), and a weak door whose tools are `native` (`FAKE_TOOLS`). An id that is not in the G47 door table is `SPEC_UNKNOWN_DOOR`.

### Oracle, jail, archive, stop

A nontrivial edit needs an `OracleSpec`: command, cwd, `expect_fail_pre`, `expect_pass_post`, and `property_id`. The pre-edit run must fail. A zero exit is `ORACLE_ALREADY_GREEN` and the edit is refused. The post-edit run of the same spec must pass. The cwd must not be `live`. A shell name as the command's first token (`cmd`, `powershell`, `pwsh`, `bash`, `sh`, and the `.exe` forms) is `SHELL_ORACLE`. The product gate still launches that command with `shell=True` after the name check. The harness oracle does not: it runs an argument vector with `shell=False`. Treat the product form as unfinished enclosure, not as a shell feature.

`PathJail` refuses the shapes named in `safety/scars.py` before it touches the filesystem: `..`, encoded `..`, a null byte, a drive-relative path, UNC and the `\\?\` / `\\.\` device namespace, a current-drive `\Windows` root, a bare drive root, and a `file:` URL. POSIX absolute paths are grant-checked rather than banned by shape. A path outside every grant is `outside_grant`.

`ArchiveStore` moves a file into `_delme` and appends a ledger row. `delete_policy` is `archive_only`. A raw unlink is `CrashClass`, not a pass. The default hook bus rewrites a shell delete and a delete tool into `stage_to_delme`. There is no delete hand.

`StopGate` accepts done only with a `DoneBundle`: `diff_hash`, `oracle_id`, `oracle_log_hash`, `pack_hash`, `cmd_hash`. An empty field is `INCOMPLETE_BUNDLE`. A hash that does not match the artifact is a mismatch refusal (`DIFF_HASH_MISMATCH`, `ORACLE_LOG_HASH_MISMATCH`, `PACK_HASH_MISMATCH`, `CMD_HASH_MISMATCH`). `session_success_is_not_done` is true when a session event says success, ok, or green and has no valid bundle. Green prose is not publishable.

`map_hash` is the SHA-256 of canonical JSON: git HEAD, sorted work-order paths, and `property_id`. An empty HEAD or a pack marked mtime-only raises `MTIME_ONLY_FORBIDDEN`. Extra paths outside the work-order closure raise `FULL_TREE_SNEAK`.

`SessionLog` appends one JSON object per line and refuses an event with no `ev`. `compact` may only append a summary. If the file no longer starts with the previous bytes, that is `SPLICE`. `derive_messages` drops `assistant/attempt`. The model is not shown the refused dispatch.

`detect_enclosure` looks for `bwrap` and does not attach it. Both branches return kind `none`, available false, reason `policy_only`, `wipe_proof` false. `refuse_unsandboxed_retry` always raises `UnsandboxedRetryRefused`. `enclosure_is_wipe_proof` is false for that status. Do not describe this package as wipe-proof.

### CLI

```
py -3.14 -m pytest -q
py -3.14 -m cosmos_code doctor
py -3.14 -m cosmos_code enclosure
py -3.14 -m cosmos_code check .
```

`doctor` prints the version, the delete and format hook decisions, and the enclosure line. It does not spawn a model. `check` prints the four receipt rows and exits 1 when `package_blocked` returns a reason.

Tests, under `cosmos_code/tests/`, cover the five freeze spines (oracle before edit, archive instead of delete, done bundle, map hash, policy-only enclosure), the engine (specs, propose does not spawn, dispatch stays locked, checker rows), and `seat_here` landing a Sol pack on the rail.

## G47

G47 plans one call. It builds the pack, the argv or the rail payload, and the token size. It does not loop, swap the pin, or treat HTTP 200 as a seat. Design notes are `harness/G47/ARCHITECTURE.md`. This page is the map of the modules that are on the tree now.

`Refuse` is the only failure type. Branch on `reason`. The detail is evidence, not a second code path.

### Public surface

`g47` exports `plan`, `grade`, `seat`, `prepare`, `run`, `action_for`, and `classify`.

| Module | Role |
|---|---|
| `contracts.py` | `Legend`, `OutputContract`, `FIRST_LINE`, `KIND`. |
| `doors.py` | Door table and aliases. |
| `pack.py` | Project a legend onto a door. Strong, weak, and none packs differ. |
| `size.py` | MAX from the measured window. No baked 2048. |
| `summon.py` | `plan`, `materialize`, `execute`, `served_model`. |
| `grade.py` | Mouth against the contract. Worktree doors are not applied on text alone. |
| `scars.py` | Name one failure class. `retry_same` is always false. |
| `loop.py` | At most the attempt plus one confirming SOP. |
| `seat.py` | A seat object exists only when all eight layers have a proof. |
| `roster.py` | Approved HERO cards. |
| `locate.py` | Read `installs/DOORS.toml`. Write this machine's `LOCAL.toml`. |
| `doctor.py` | Which seated doors have a binary on `PATH`. Does not run them. |
| `superior.py` | Eleven law axes against a recorded all-zero Claude Code card. Not a benchmark. |

### Contracts

`KIND` maps `ORC`, `WOMBAT`, `JUDGE`, `CODER`, `CCR`, and `DAEMON` to orch, board, review, coding, dispose, and daemon. A daemon legend is `DAEMON_NOT_LLM`. A CCR legend is `CCR_NOT_A_DOOR`. An ORC legend on a coding door is `ORC_NO_CODING`.

`FIRST_LINE` is the table the grader and the harness bind actually use:

| Role | Allowed first line |
|---|---|
| CODER | `NONE`, or a line that starts with `diff --git` |
| WOMBAT | `ITEM`, `NONE` |
| JUDGE | `KEEP`, `DROP`, `NONE`, `HOLD`, `UNMEASURED` |

`docs/HARNESS.md` and `docs/CANON_SPAWN.md` still disagree on role, `output.what`, and the first line. G47 and the harness do not invent a third table. A role with no row in `FIRST_LINE` fails the harness bind (`FIRST_LINE`). Ping shape, when requested, is `NONE` and then a line that starts with `HERO_OK`. A ping can be mouth-correct with `task_pass` false.

`what` is `text`, `python`, or `no_prose`. Text wants the role's first line. Python wants a code opening (`import`, `from`, `def`, `class`, and the fence check). A leading fence is `FENCE` even for Python. `no_prose` wants exactly one allowed line. Worktree grade mode returns `NEED_WORKTREE` unless the caller passes `worktree_obeyed=True`. An empty served model is `SKU_UNBOUND`. A different served model is `SKU_MISMATCH`. HTTP 200 is not applied.

### Doors

Aliases: `deepseek` to dsh, `openai` to codex, `gemini` to vertex, `ling` to opencode, `glm` to pi.

Seated in the table does not mean the binary is on this machine, and it does not mean `execute` will start it.

| Door | Strength | Grade | Execute |
|---|---|---|---|
| cosmos-code | strong | worktree | `EXECUTE_IS_RAIL`. Pack only. |
| opencode, pi, dsh, codex, copilot | strong | worktree | One process if the binary is on `PATH`. dsh also needs its key file or `NO_KEY`. The file is not read here. |
| grok | strong | worktree | `GROK_NOT_A_WORKER` before a process exists. Pack still plans. Input over the door keep-under (200k) is `KEEP_UNDER`. |
| openrouter | weak | filed text | Empty argv. A `rail` dict: pin as model, `allow_fallbacks` false, routing off, computed `max_tokens`. No invented tools array. |
| vertex | weak | filed text | `gemini.cmd` plan. `--harness` is forbidden. |
| claude, hermes, antigravity, none | mixed | mixed | Unseated. `execute` raises `UNSEATED` or `NO_BINARY`. Claude's steal-list forbids `--fallback-model` and `--dangerously-skip-permissions`. |

`plan` refuses slug shapes before HTTP: `openrouter/free` and a trailing `/free` (`NOT_A_PIN`), `:floor` on `:free` (`FLOOR_ON_FREE`), the dead Ling VL free slug (`SLUG_DEAD`), Luna flex on the OpenRouter door (`WRONG_VIA`), GLM on that door (`MIXED_VIA`), and Inkling `:free` on chat (`HARNESS_GATE`). A joined context string is `NO_CONTEXT`. A `<pointer>` or `see docs/` in the mission is `POINTER_IN_TASK`. Dates or a PR id in a wrapper that lands in `AGENTS.md` is `PREFIX_VOLATILE`. Codex with an empty wrapper is `EMPTY_HOUSE`. `prefill_none` is legal only on the OpenRouter door.

Strong doors get a thin user message. The wrapper goes in the file that door loads, and `materialize` does not overwrite an existing `AGENTS.md`. Weak doors put WRAP on the system turn and STYLE on the user tail. STYLE on the system turn is the measured way to cancel a tool call. A none-door gets an outfit card that says no harness is running. Skills are paths, or the line `none extra`. A pasted skill body is `SKILL_BODY`.

Positional prompt text longer than 1200 characters becomes a short "read TASK.md" line. The mission stays in the file. Argv longer than 7000 characters is `ARGV_TOO_LONG`. Forbidden flags on the argv are `FORBID_FLAG`. `materialize` refuses `live` (`LIVE_TREE`) and a pack filename that escapes the attempt (`PATH_ESCAPE`). It writes `g47-plan.json` into that worktree only.

`served_model` accepts one JSON document or JSONL and the keys `model`, `served_model`, and `response_model`. Two different ids, a null, prose, or a missing key return empty. The argv pin is not a substitute. `process_observation` always returns `seated: false`.

Size: margin is 20 percent of the measured window. MAX is window minus cached tokens minus prompt tokens minus that margin. No positive window is `WINDOW_UNMEASURED`. MAX at or below zero is `MAX_LE_ZERO`. OPTIMUM is a positive aim clamped to MAX, or the string `float`. `approx_tokens` is `len // 4` and the plan marks `estimate` true until the caller passes a real count. It is not a vendor tokenizer.

### Seat loop and roster

`g47.loop.run` places at most two calls: the attempt, and one confirming call after a single SOP. It does not clear a latch and it does not run `while (true)`. `prepare` refuses a free pool pin, `:floor` on `:free`, a tilde alias, a `-latest` suffix, and the door `grok` (`GROK_NOT_A_WORKER`). It does not move a seat onto Codex, OpenCode, or Pi. The caller's door stays the route.

`classify` names the class and sets `retry_same` false. Classes include `PIN_GATE`, `BATCH_UNSUPPORTED`, `BATCH_OPEN`, `BATCH_DOOR`, `MOUTH_FOREIGN`, `TASK_ASK`, `UPSTREAM_POOL`, `SLUG_DEAD`, `HARNESS_GATE`, `NO_SHAPE`, `REJECTED`, `UPSTREAM`, `SKU_UNBOUND`, `EMPTY`, `FENCE`, `NOT_CODE`, `MOUTH_FORM`, and `LOOKS_SHAPED`. `action_for` maps one class to one SOP. A second post-call SOP does not fire. Stop SOPs include an open batch, a refused batch, a foreign mouth, a nameless 400, a safety label, a door that asks for the task again, a free-pool 429, and an HTTP 5xx. Confirming shapes that the provider text already names (pcm16, a batch adapter, effort low, reasoning left on, an image endpoint, Relace apply XML) are one call, then stop. The harness does not invent a new SOP row at runtime.

`seat` builds a `Seat` for a roster id via `native` or `cosmos-code`. A missing layer is `PACK_INCOMPLETE`. `executable` is false for `grok` and for `cosmos-code` even when the door table says seated. `seat_agent` runs the call the caller supplies and journals `seat.jsonl` with `seated` false. The return is seated only when that call's flag is boolean true and `same_pin` matches the served id. `live_call` is the one function that starts a process. Its return is an observation, not a seat.

Roster ids on this tree: `luna` (JUDGE, Codex, not OpenRouter chat), `sol` and `mini` (CODER, Codex), `glm` (CODER, pi), `gf38` (CODER, vertex), `deepseek` (CODER, dsh), `ling` (CODER, opencode), `grok` (CODER card; do not start `grok.exe`).

`g47.superior.law` scores a cosmos-code seat from phrases in `LOOP.md` and `TOOLS.md`. A native door can carry eight layers and still score zero on the rail axes. `ahead_of` compares sums. It is not a claim that a task was won.

### Locate and CLI

`locate.catalog` reads `installs/DOORS.toml` via `Path(__file__).parents[3] / "installs" / "DOORS.toml"`, which is this repo root when the file lives at `harness/G47/g47/locate.py`. An absent catalog raises `CATALOG_ABSENT`. An empty list is not what a missing file returns, and it would not be a pass. `probe` marks each row `found` or `missing`. `write_local` writes `installs/LOCAL.toml` for this machine. The catalog stays the source of names.

```
py -3.14 -m pytest -q
py -3.14 -m g47 doctor
py -3.14 -m g47 locate
py -3.14 -m g47 plan --door opencode --role CODER --model inclusionai/ling-3.0-flash --window 262144 --where V:\tmp\attempt --task "Say the contract."
py -3.14 -m g47 grade --role CODER --what text --mouth -
```

`plan` does not spawn. `grade` exits 2 when the mouth fails its contract. `seat` prints the public seat JSON and does not start a process. Tests are `tests/test_g47.py` and `tests/test_seat.py`. They do not start a vendor process.

## COSMOS Harness

The control loop is fixed. Eight hooks decide the prompt, the hands, the stop, the seating SOP, the checkers, and the bundle. The model is sampled in between those hooks. It does not choose the next hook and it does not clear a refusal. Turn cap is 8 (`layers.TURN_CAP`). A refused hand sets a latch. The latch is not cleared on the next turn or on a token-budget continuation.

`cosmos_harness` exports `LAYER_LANGUAGE`, `TURN_CAP`, `bind`, `run`, `seat_proof`, and `step`.

### Eight layers

Each layer has one language. `layers.bind` refuses an unbound stack before any sample.

| Layer | Language | Shipped file | Bind rule |
|---|---|---|---|
| l1 role | Markdown | `pack/L1_ROLE.md` | Role must be in G47 `KIND`. First line must be in `FIRST_LINE` for that role. |
| l2 model | TOML | `pack/pin.toml` | A real pin. No `openrouter/free`, no `:floor` on `:free`, no fallback in the pin. |
| l3 harness | Python | `loop.py`, `hooks.py` | This package. Door must be one the loop may sample. |
| l4 wrapper | Markdown | written per attempt as `WRAP.md` | Non-empty. Style does not go here. |
| l5 skills | Markdown | `pack/L5_SKILLS.md` | Default body is `none extra`. |
| l6 tools | JSON | `pack/L6_TOOLS.json` | Eight hand names, in order. Delete is absent. |
| l7 enviro | C and Python | `native/job_object.c`, `jail.py` | Attempt directory, not `live`. Oracle argv is not a shell and not `grok.exe`. |
| l8 mission | Markdown | `pack/L8_MISSION.md` | Non-empty task. A pointer or `see docs/` is `POINTER_IN_TASK`. |

Doors the loop may sample (`SEAT_DOORS`): `cosmos-harness`, `codex`, `pi`, `opencode`, `dsh`, `claude`, `copilot`. `grok` is absent. `bind` also refuses `GROK_NOT_A_WORKER` if `grok.exe` appears on the oracle argv.

`pack.materialize` fills those templates into the attempt. If the L6 name list drifts, it raises. If style text appears inside `WRAP.md`, it raises.

### Eight hooks

Order in `hooks.HOOK_ORDER`: `prompt_in`, `prompt_bound`, `pre_tool`, `post_tool`, `stop`, `seat_scar`, `verify`, `done`.

`loop.run` is the driver. It binds, checks the hands are bound to the same root and mode, runs `prompt_in` and `prompt_bound`, then requires a red oracle before the first sample. A sample whose reported model is not the pin is `PIN_SWAP` and halts. A provider error with tool calls still attached is `ORPHANED_DEBT` and does not edit. A provider error with no calls goes through `learn.step` and `seat_scar`: one journal line, and at most one confirming sample. A second scar does not sample again. Plan mode may look and may not write. An act-mode edit, write, or archive before red is `ORACLE_NOT_RED`. A failed hand latches. After a landed edit, a later latch still reaches the grade. Turn 8 with the loop still open is `HALT_MAX_TURNS`.

Plan mode does not produce a done bundle. It closes on the role's first line (`VERDICT`) or refuses `FIRST_LINE`. Act mode then requires a green oracle (`ORACLE_STILL_RED` becomes `GATE_FAILED`), four `PASS` checker rows, and a five-field bundle. The terminal name `DONE` means those hashes were present. It does not publish `live/` and it does not clear the locked propose path in COSMOS CODE.

`bundle.make` hashes the recorded patches, the oracle argv, the post-oracle log, and the pack files in name order. `seat.jsonl` is not part of the pack hash. An empty field fails `done` with `INCOMPLETE_BUNDLE`.

### Hands

Host hands: `read`, `glob`, `grep`, `edit`, `write`, `archive`, `oracle`, `worktree`. Plan hands: `read`, `glob`, `grep`, `oracle`. There is no delete hand and no bash hand. An unknown name is `NOT_A_HAND`.

Caps in `tools.py`: read 100_000 bytes, grep 200 hits, file and write 256_000 bytes. The first path segment `_pack` or `_delme` is `RESERVED_PATH`. `archive` still moves an ordinary file into `_delme`. A hand does not write those reserved directories as a target prefix. Removal is that move. It is not unlink.

The oracle hand reads the host result. It does not let the model invent the exit code. Pre-edit must be non-zero (`ORACLE_ALREADY_GREEN` if it is already green). Post-edit must be zero (`ORACLE_STILL_RED` otherwise). The child is `job.run_child`: argument vector, scrubbed environment, `PYTHONDONTWRITEBYTECODE=1`, timeout default 15 seconds. Timeout is exit 124 and is still an oracle result. `UNENCLOSED_CHILD` propagates. It is not a red test and it is not a retry without the job.

### Jail and job

`jail.Jail` is one attempt root. It refuses an empty path, a null, a `file:` URL, UNC, `..`, an absolute path, a drive, and a colon (alternate data stream) before joining onto the root. A resolved path outside the root, including a symlink that escapes, is `PATH_ESCAPE`. The jail is policy. It is not a wipe-proof kernel boundary.

`job.py` is the process-tree half of L7. On Windows, `run_child` creates the child suspended, assigns it to an unnamed job with kill-on-job-close and class-9 extended limits, then resumes it. If assignment fails, the child is killed and `UNENCLOSED_CHILD` is raised. The default active-process limit is 4. A limit below 1 does not start the process. `None` keeps kill-on-close and does not cap the count. The OpenCode door passes `None` because that process tree does not fit in four. The function does not assign the current process. Assigning this process to a kill-on-close job would take the harness down with the handle.

`probe` can report kind `job_object` and available true when the flags read back. `wipe_proof` is still false and the reason is still `policy_only`. A job without a restricted token, a denied network, and a measured child assignment is not a filesystem jail. `refuse_unsandboxed_retry` always raises `UNSANDBOXED_RETRY`. `native/job_object.c` probes the same flags and prints `policy_only` either way. The tests run the Python loader. The C file is optional to build and is not a wipe-proof claim.

COSMOS CODE's enclosure detector does not report this job object. It stays on the `bwrap` / `policy_only` branch. Both packages agree on the reason and on `wipe_proof` false. They do not share one detector.

### Wire and OpenCode

`wire.body` builds an OpenRouter-shaped chat object and does not send it. The model field is the pin. The system turn is the wrapper only. Style, when present, sits on the user side with the task and the contract line. Tools are the L6 schemas. `provider.allow_fallbacks` is false. There is no fallback model and no `:floor` suffix in that body. The API key is not an argument. A caller that posts the body attaches the key outside this package. This page does not name a key file's contents.

`opencode_door.py` is the measured OpenCode spawn for three pins: `thinkingmachines/inkling:free`, `thinkingmachines/inkling-small:free`, and `inclusionai/ling-3.0-flash`. A slug that contains `inkling` also matches. The argv is `opencode.cmd run` with `--dir`, `-m openrouter/<slug>`, and a short prompt. It does not pass `--auto`. A long mission stays on disk. An existing `AGENTS.md` is left in place. A missing binary is a refusal. Session seating still requires `same_pin` and a host pass. An empty served id does not seat.

`tests/test_chat_retry.py` imports `ChatSample` from `V:\streams\cosmos_code\attempts\cheap-seat`. That helper is outside this package. The suite passed on this machine because that path was present. It is not the locked `propose` path, and it is not a provider inside `cosmos_code`. Do not treat a shape retry in that helper as permission to clear a harness latch.

### Seating proof

`learn.step` classifies one observation with `g47.scars.classify`, asks `g47.loop.action_for` for the one SOP, and can append the outcome to a journal. The line's `seated` field stays false. The SOP table is not edited here. A sentence the table does not name stays a stop in the journal until a person adds one row.

`seat_proof` seats only when `same_pin` matches and `host_constants` passes. The host runs `constants()` in a child and expects `(pi, sqrt(2), e, log(1))` within tolerances `1e-6`, `1e-6`, `1e-6`, and `1e-9`. Credential-shaped environment variables are dropped. A classifier label or a story fails the host (`HOST_FAIL`). A file from another model is `MOUTH_FOREIGN`. HTTP 200 is not a seat.

### Law score

`law.score` reads `pack/LOOP.md`, `pack/L6_TOOLS.json`, `loop.py`, and `hooks.py` and reports 1 or 0 on the same eleven axes as `g47.superior`: pin lock, no ungated retry, done bundle, oracle before edit, delete is not a tool, four checks, live refused, turn cap, eight layers, one scar one SOP, one corrective. `ahead_of_claude_record` is true only when every local axis is 1 and the recorded Claude Code card is still all zeros. That card is a steal-list of loop behavior (pin swap, ungated retry, a delete-shaped tool). It is not a task bakeoff and it does not claim an Opus win. `cosmos_harness` with no arguments prints the layer languages, the hook order, the hands, the enclosure line, one local pcm16 classification, and that score. It reads no key and calls no provider.

### Tests

`tests/test_harness.py` covers the hook order, a repeated script, the done bundle, the turn cap, plan versus act, pin swap, the scar latch, the jail, the job, and the four-pass verify rule. `tests/test_opencode_door.py` covers the measured argv and the host seat. `tests/test_chat_retry.py` is the streams helper noted above.

## Still open

These are gaps in the code this page read. Closing them is later work. This list is not a finish line.

- Dispatch stays locked. `propose` returns `done: false`. No provider is bound. A real door is not started by the product package.
- `wipe_proof` is false in both enclosure reports. The reason string is `policy_only`. COSMOS CODE does not attach `bwrap`. The harness job object is not a restricted-token sandbox.
- The product oracle still uses `shell=True` after refusing a shell executable name. The harness oracle uses an argument vector.
- The 4C vocabulary differs: `MISSING` in COSMOS CODE, `UNAVAILABLE` in the harness. Reply rows, the quality ladder, and `package_blocked` do not block the same set.
- `FIRST_LINE` is the table these packages grade. `docs/HARNESS.md` and `docs/CANON_SPAWN.md` still disagree. Do not add a third table in a proposal that has not been accepted.
- Claude, Hermes, Antigravity, and the bare `none` door are unseated. Grok plans and does not execute.
- `CODE.md` and the G47 README still describe the streams copy. The modules to read are the ones named above.
- One harness test reaches outside the repo into a streams attempt tree.
- Seating a pin, a Windows sandbox proof, and a spend cap are not done because these packages import. Native doors on `PATH` are optional and are not a 4C result.
- Publishing `live/` remains the Chief Coder's pen. These packages do not hold it.

## Where to read next

- `cosmos_code/README.md` and `cosmos_code/docs/INSTALL.md`
- `harness/G47/ARCHITECTURE.md` for the seating scars the planner encodes
- `cosmos_harness/README.md` and `cosmos_harness/pack/LOOP.md`
- `harness/KEITH_20260930_STANDALONE.md` for the 2026-09-30 4C and standalone note
- [PEN](PEN.md) for who may write the live tree
- [CHECKS](CHECKS.md) for how a change is checked, when that chapter is present

Do not paste these modules into a work order as a blob. Point at the path. Do not claim the three package measurements above mean COSMOS is finished.
