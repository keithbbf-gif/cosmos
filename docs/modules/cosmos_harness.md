# COSMOS Harness

Snapshot of main `501fdee25a581648ee0ddb096bdafa70a2325a71`.

## What it is

The control loop. The model is sampled once per turn, and only there. Eight hooks decide the prompt, the hands, the stop, the seating SOP, the checkers, and the bundle. Turn cap is 8. A refused hand sets a latch. The latch is not cleared on the next turn, on a token-budget continuation, or after a stop. There is no `while true`. The range is `range(1, TURN_CAP + 1)`.

Eight layers, and the language `LAYER_LANGUAGE` records:

| Layer | Language | What it is |
|---|---|---|
| l1 role | Markdown | Role and the first line already named |
| l2 model | TOML | The pin. No fallback. No `:floor` on `:free` |
| l3 harness | Python | This package. Hook order and the turn cap |
| l4 wrapper | Markdown | System text. Style does not go here |
| l5 skills | Markdown | Dormant until named. Default body is `none extra` |
| l6 tools | JSON | Hand schemas the host executes |
| l7 enviro | C | `native/job_object.c`, plus the Python path jail |
| l8 mission | Markdown | The task. The oracle argv sits beside it |

Hands: `read`, `glob`, `grep`, `edit`, `write`, `archive`, `oracle`, `worktree`. Plan mode may use only `read`, `glob`, `grep`, and `oracle`.

`learn.step` classifies one observation with the G47 scar table and returns the one SOP. The outcome is appended to a journal, including a stop. The journal line's `seated` field stays false. `seat_proof` is a separate check: the served id must be this pin, and a child running `constants()` must pass. A file from another model stays `MOUTH_FOREIGN`. The table is not edited at runtime.

Enclosure reason stays `policy_only`. `wipe_proof` stays false, including when `probe` can see a job object. A job without a restricted token, a denied network, and a measured child assignment is not wipe-proof.

## Where it lives

`cosmos_harness/`. Package `cosmos_harness`. Pack text is `cosmos_harness/pack/`. The Win32 job source is `cosmos_harness/native/job_object.c`. Tests are `cosmos_harness/tests/`. It imports G47 from `harness/G47`.

## Entry points

- `py -3.14 -m cosmos_harness` — prints layer languages, hook order, hands, enclosure, one local seat example, and the law score. No key is read. No provider is called.
- `cosmos_harness.run` — one attempt. The driver is injected. `Driver.sample` raises `NO_DRIVER` until a test or a caller supplies it.
- `cosmos_harness.bind` — refuses an unbound stack before any sample.
- `cosmos_harness.step` / `seat_proof` — one SOP, then the host proof. Neither starts a provider from the journal.

Hook order: `prompt_in`, `prompt_bound`, `pre_tool`, `post_tool`, `stop`, `seat_scar`, `verify`, `done`.

## What it refuses

`bind` refuses `UNKNOWN_ROLE`, `FIRST_LINE`, `WHAT`, `EMPTY_PIN`, `NOT_A_PIN`, `FLOOR_ON_FREE`, `FALLBACK_MODEL`, `LIVE_TREE`, `WHERE`, `PACK_INCOMPLETE`, `MODE`, `SHELL_ORACLE`, `POINTER_IN_TASK`, and `GROK_NOT_A_WORKER` (a `grok.exe` oracle). A shell string is not an oracle argv.

`pre_tool` refuses a name outside the hand set (`NOT_A_HAND`), a plan-mode mutation (`PLAN_MODE`), and `edit` / `write` / `archive` before a red oracle (`ORACLE_NOT_RED`). That set includes `delete`, `bash`, `shell`, and `agent`. The latch is not cleared.

`verify` requires a green post-oracle and exactly four checker statuses, each `PASS`. Any other status blocks. The reason is that status. `done` requires five non-empty hashes: `diff_hash`, `oracle_id`, `oracle_log_hash`, `pack_hash`, `cmd_hash`.

`archive` moves a file under `_delme` and appends `_delme/ledger.jsonl`. A missing file and the jail root are refused. A failed move leaves the original in place. `run_child` raises `UNENCLOSED_CHILD` if the child cannot be assigned to the job, and kills that child. `refuse_unsandboxed_retry` always raises. Credential-shaped environment variables are dropped before a child starts.

Doors this loop may sample are `cosmos-harness`, `codex`, `pi`, `opencode`, `dsh`, `claude`, and `copilot`. `grok` is absent.

## What it is not

Not Core. The archive JSONL is not the Core ledger. Not a delete hand and not a bash hand. Not wipe-proof. Not a start of `grok.exe`. Not a runtime edit of the scar table. A journal line does not stamp `seated`. Checkers are the verify hook, not a shell the model typed. The law score is not a task bakeoff.

## Grade

4C is `py_compile`, `ruff`, `mypy`, `pytest`. No fifth C. A tool this interpreter cannot import is `UNAVAILABLE` and blocks done. It is not a pass and it is not a skip. `pytest` exit 5 is `NO_TESTS`, which also blocks a coding seat. A checker timeout (exit 124) is `FAIL`. No Python files is `PROSE`.

The verify hook blocks any status that is not four `PASS` rows. Product `cosmos_code` spells a missing tool `MISSING`, and `python -m cosmos_code check` exits 0 when the only bad row is `NO_TESTS`. Same checkers. Different block rule. That mismatch is real.

Package 4C for this tree passed at this tip. Run the four tools inside `cosmos_harness/`, not as a repo-root scan.
