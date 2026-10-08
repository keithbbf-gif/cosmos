# G47 code walk

Package root: `V:\streams\cosmos_code\harness\G47`. Import path is the `g47` directory. Tests are `tests/test_g47.py` and `tests/test_seat.py`. They do not start a vendor process. Twenty passed on Python 3.14 after the 2026-10-01 scar revision.

Nothing here runs a provider. `execute` can, and the CLI does not call it.

## `refuse.py`

`Refuse(reason, detail)` is the only failure type. The reason string is the scar vocabulary (`FLOOR_ON_FREE`, `EMPTY_HOUSE`, `KEEP_UNDER`, …). Callers branch on `exc.reason`.

## `contracts.py`

`FIRST_LINE` is the HARNESS.md table: CODER `NONE` or `diff --git`, WOMBAT `ITEM` or `NONE`, JUDGE `KEEP`, `DROP`, `NONE`, `HOLD`, `UNMEASURED`.

`KIND` maps a role to orch / board / review / coding / dispose / daemon.

`OutputContract(role, what, ping)` is what a legal reply looks like. `what` is `text`, `python`, or `no_prose`.

`Legend` is the seven layers the caller actually has: role, model pin, what, ping, wrap, style, task, context paths, where, optimum, window, cached token count, skill paths, and `prefill_none`. Context is a tuple. A joined string is rejected later. Skills default to empty, which the pack records as `none extra` rather than pasting a body.

## `size.py`

`compute(window, cached_tokens, prompt_tokens, optimum, keep_under)`:

- no positive window → `WINDOW_UNMEASURED`
- negative counts → `BAD_TOKEN_COUNT`
- cached + prompt over `keep_under` → `KEEP_UNDER` (Grok's 200k, applied by the door)
- `margin = int(0.20 * window)`
- `max_tokens = window - cached - prompt - margin`
- `max_tokens <= 0` → `MAX_LE_ZERO`
- optimum `"float"` stays the string `float`
- a positive optimum larger than MAX is clamped down
- zero or a bad type → `OPTIMUM_ZERO`

`approx_tokens` is `max(1, len // 4)` and the plan marks `estimate=true` when the caller did not pass a real count. The returned `max_tokens` is what a rail should send. G47 never substitutes 2048.

## `scars.py`

`check_slug(door_id, model)` runs before the pack is built.

- `openrouter/free` or a slug that is only `free` → `NOT_A_PIN`
- both `:free` and `:floor` → `FLOOR_ON_FREE`
- `ling-3.0-flash-vl:free` → `SLUG_DEAD`
- `gpt-6-luna` or a `luna:floor` pin on the openrouter door → `WRONG_VIA`
- `glm` or `z-ai/…` on the openrouter door → `MIXED_VIA`
- `inkling…:free` on the openrouter door → `HARNESS_GATE`

A `deepseek/…` pin on the openrouter door is not refused. The catalog seated `deepseek-v4.1-flash` there. Choosing the door `dsh` is the native binary; choosing the door `openrouter` is the chat pin. Those are different calls.

`classify(http, detail, mouth, served_model)` returns `{class, retry_same, next}`. `retry_same` is always false. This function does not re-fire.

Order: pin-gate phrase, then the 2026-10-01 classes, then 429, 404, 403, 400, empty served model, empty mouth, a leading fence, a safety label, a first line that is not a legal shape, otherwise `LOOKS_SHAPED` (still grade it).

October classes, each with one SOP in `loop.py`:

- `BATCH_UNSUPPORTED` — the Batch API refused the model, or the job detail is `failed` plus a batch id. SOP `batch_unsupported`: keep the id, do not stamp, do not return to chat.
- `BATCH_OPEN` — detail is `in_progress` plus a batch id. SOP `batch_open`: keep the id. A later poll seats only when status is completed, the served id is this pin, and the host passes.
- `BATCH_DOOR` — the 404 names a batch adapter. SOP `batch_endpoint`: one `POST /api/v1/batches`.
- `MOUTH_FOREIGN` — the file was served as another id. SOP `foreign_mouth`: do not bind this pin. `same_pin` is the check the catalog seater uses before `json_code` can seat.
- `TASK_ASK` — the door asked what the task is. SOP `task_ask`: the mission was already sent.
- `NO_SHAPE` — HTTP 400 and the body says bad request, with no pcm16 or audio format named. SOP `no_shape`: do not invent a body.
- `NOT_CODE` — the mouth is a safety label (`User Safety` or `unsafe`). SOP `not_code`: do not wrap it into the math file.
- `UPSTREAM_POOL` — SOP `pool_hold`. A 45-second wait is the same pool.
- `HOST_FAIL` is the caller's scar when the host did not pass. SOP `unemitted`: do not write a line the model did not emit.
- Empty Claude keys (`empty keys=` in the detail) take SOP `effort_low` once: reasoning effort low, a larger cap, never effort none. A bare empty Claude mouth still takes `reasoning_on`. The latch does not add `effort_low` as a second post-call SOP.

## `doors.py`

`DOORS` is data. Each `Door` carries strength, seated, binary, grade mode, the flags that were read off a cheat or off Claude Code `main.tsx`, a forbid list, an optional key path, and a note. `get_door` applies aliases and raises `UNKNOWN_DOOR`.

Seated means "this plan is allowed to describe a real call." It does not mean `execute` will start a process. Grok is seated as a pack and refused as a worker. Claude is unseated: the argv is recorded so the steal-list can be inspected, and `execute` raises `UNSEATED`.

`dsh.key_file` points at `live\config\deepseek_api_key.txt`. Execute checks `is_file()` and does not read the bytes.

## `pack.py`

`project(legend, door)` checks the legend, then writes the file map and the two strings (system, user).

Checks, in order: role and model present, daemon and CCr refused, ORC on a coding door refused, context items that contain ` · ` or a newline refused, a `<pointer>` or `see docs/` inside task, style, or wrap refused, Codex without a wrapper refused (`EMPTY_HOUSE`), an ISO date or `PR #` inside a wrapper that will become `AGENTS.md` refused, `prefill_none` on any door but openrouter refused, a skill path that contains a newline or is over 240 characters refused (`SKILL_BODY`).

Files always include `TASK.md` (mission plus the one contract line) and `SKILL.md` (`none extra`, or the path list). Strong doors put the wrapper in `agents_file` when the door has one, otherwise in `WRAP.md`. The user string is style (only if the caller passed one) plus task plus the contract line. WRAP is not copied into that user string. Weak doors set system to the wrapper alone and put style on the user tail. None-doors build an outfit card that says no harness is running.

The contract line looks like:

```
CONTRACT role=CODER first_line=NONE|diff --git what=text where=worktree
```

A ping appends `ping=NONE then HERO_OK`. It does not list acceptable answers.

## `grade.py`

`grade(mouth, contract, door_grade, worktree_obeyed, served_model, expected_model, prefill_injected)`:

1. Empty → `EMPTY`.
2. If `prefill_injected` and the first line is `NONE`, drop that line. Nothing left → `PREFILL_ONLY`.
3. A first line that starts with a fence → `FENCE`. This happens before the Python test, so a fence cannot pass as code.
4. Ping: line 0 is exactly `NONE` and line 1 starts with `HERO_OK`. `task_pass` stays false.
5. `what=python`: first line starts with `#`, `import `, `from `, `def `, or `class `.
6. `what=no_prose`: first line is in the role table and the reply is one line.
7. `what=text`: first line is in the role table. A trailing space is stripped, so `NONE ` still matches. That showed up on Laguna.

Then the SKU, if the caller passed one. Empty served model → applied false, `SKU_UNBOUND`. Different slug → `SKU_MISMATCH`. The `openrouter/` prefix is ignored in the comparison.

A filed-text door with a good mouth is applied. A worktree door is applied only when `worktree_obeyed` is true. Otherwise the mouth can be fine and the reason is `NEED_WORKTREE`. HTTP 200 never enters this function.

## `summon.py`

`plan(legend, door_name, prompt_tokens=None, write=False)` is the entry. Slug check, project, argv, size, and for OpenRouter a `rail` dict:

- `routing: off`
- `allow_fallbacks: false`
- `max_tokens` from `Size`, not 2048
- `prefill` set only when the legend asked
- `wrapper_bound` false when prefill is on, because that path drops the system turn
- `tools: "not invented"` — a fake tools array is how a weak door pretends to be a coder

`Plan.to_json()` is the CLI output.

Argv is per measured command, not one generic flag soup.

- **Pi** follows `call_pi_glm.py`: `pi.cmd -p --provider zai --model <sku> --tools read,write,edit`, then `--system-prompt` when `WRAP.md` exists. Under 1500 characters the bytes go on the argv. Over that, the flag carries "Read WRAP.md" and the file holds the wrapper. `--no-session` is always there so a prior session cannot resume.
- **Codex** follows the working Luna call: `codex exec --skip-git-repo-check --json --color never --ephemeral -m <sku>`. Judge and WOMBAT add `--sandbox read-only`. `write=True` on a coder adds `--approve-for-me` and does not add `--sandbox` (those two cannot combine). `--` then the short prompt. `service_tier` is not passed; effort already lives in that home's `config.toml`.
- **OpenCode** is `opencode.cmd run --dir <where> -m openrouter/<slug> -- <short>`. The model is prefixed once.
- **dsh** is `dsh.cmd --profile headless <short>`.
- **Grok** argv is `grok.exe` with no prompt flag. Execute will not run it.
- **Claude, Copilot, Vertex** use the door's binary, extra, model flag, work flag, and prompt flag. Claude's extra includes `--bare` and `--max-turns 8`. `--print` is not emitted; the short flag is `-p`.
- **OpenRouter, none, antigravity** have an empty argv.

`_prompt_text` returns the user string when it is at most 1200 characters. Above that it returns a one-line instruction to read the files already in the pack. The full mission remains on `Plan.user` and in `TASK.md`. Joined argv over 7000 characters refuses `ARGV_TOO_LONG`. A forbid-list flag that appears in the argv refuses `FORBID_FLAG`.

`materialize(plan, worktree)` refuses a path whose name is `live` or that contains `\live\` or `/live/`. It refuses a file name with a drive colon, a leading slash, or a `..` part. It skips an existing `AGENTS.md`. It writes the other pack files and `g47-plan.json`.

`execute(plan, worktree)` is one `subprocess.run`, `shell=False`, `CREATE_NO_WINDOW` when the interpreter has it, stdin closed. Before that it refuses, in order: grok (`GROK_NOT_A_WORKER`), cosmos-code (`EXECUTE_IS_RAIL`), an unseated door, an empty binary, a missing key file (`NO_KEY`), a binary `shutil.which` cannot see. It then grades stdout with `worktree_obeyed=None`, so a worktree door comes back `NEED_WORKTREE` until a harvest says the tree obeyed. There is no second attempt.

## `doctor.py`

Walks `DOORS`. Reports `on-path`, `missing`, or `no-binary`, then `/unseated` and, for dsh, `/key` or `/NO_KEY`. It does not run the binaries and it does not print a key.

## `__main__.py`

`python -m g47 plan|grade|doctor`. Plan requires `--door`, `--role`, `--model`. `--window` is required by the size rule; omitting it raises `WINDOW_UNMEASURED` from `compute`. `--optimum` becomes an int when it is all digits, otherwise the string is kept (`float`). Grade reads `--mouth` or stdin when the mouth is `-`, and exits 2 when the mouth is not ok.

## What a caller does

1. Build a `Legend` with a measured window and the pin's real via.
2. `plan(legend, door)`.
3. On `Refuse`, branch on the reason. Do not retry that pin on that door.
4. `materialize` into an attempt worktree that is not `live/`.
5. For OpenRouter, send `plan.rail` through the existing rail. Do not add a tools array in this module.
6. For a seated CLI, `execute` once. Harvest the worktree. Call `grade` again with `worktree_obeyed` and the served model.
7. `classify` the HTTP row if the rail returned one. The class picks the next pin. G47 does not pick it for you.
