# G47 — harness call architecture

G47 is the spawn planner for COSMOS and COSMOS CODE. A caller hands it a legend (role, pin, mission, window) and a door name. It returns a pack, an argv or a rail payload, and a size. It refuses with a named reason when the call would repeat a failure we already measured. It does not loop, swap models, or treat HTTP 200 as a seat.

The first draft of this package used the door cheats, the size formula, and `hero_unify.py` BIND. It had not re-read the OpenRouter seating campaign. This revision does. The sources are `SOP_SUMMON_HERO.md`, `SUMMON_BY_HARNESS.md`, `SOP_CCREW_PACK_SMOKE.md`, `SOP_CCREW_CATALOG.md`, `SCAR_HERO_SUMMON_20260923.md`, `SCAR_MODEL_CALL_20260925.md`, `SCAR_CCREW_PACK_SMOKE.md`, `SCAR_CCREW_CATALOG.md`, `PACK_BY_HARNESS.md`, and `CORE_REVEAL.md`, plus the measured argv in `call_pi_glm.py`, `run_work_order.py`, and `_summon_or_hero.py`.

## What the seating campaign actually taught

About a hundred pins were smoked, cheapest first. The failures were not one 429.

| Class | What came back | What G47 does |
|---|---|---|
| Upstream shared pool | HTTP 429, `limit_source=upstream_provider_shared_pool`. Gemma `:free` is Google AI Studio. Qwen `:free` is ModelRun. The weekly cap was still ~150. | `classify()` returns `UPSTREAM_POOL`. `retry_same` is false. Wait, another pin, or BYOK. |
| Pin hole | Roster slug missing from the rail's `PINNED` table. Refused before HTTP. | G47 does **not** freeze that Monday's missing list. Laguna was refused, then seated the next day once the rail pinned it. The live pin table stays in the rail. |
| Dead slug | Ling VL `:free` was HTTP 404. | `SLUG_DEAD` before any call. Paid id is `inclusionai/ling-3.0-flash-vl`. |
| Harness gate | Inkling `:free` is HTTP 403 on chat: agentic harnesses only. | `HARNESS_GATE` on the OpenRouter door. OpenCode may still carry that pin. |
| `:floor` on `:free` | Nano Omni and the route-variant default returned HTTP 200 with `response_model=None`. | `FLOOR_ON_FREE` if both suffixes are on the slug. Rail payload sets `routing=off` and `allow_fallbacks=false`. |
| Mouth form | Hy3 preview and Nemotron Lightning: HTTP 200, SKU bound, first line was preamble or CoT. North Mini later echoed PREFIX the same way. | Grade fails `FIRST_LINE`. `classify()` returns `MOUTH_FORM`. Do not seat on the status code. |
| Empty mouth | Muse 1.2 / 1.3: 200 and a SKU, no text. | `EMPTY`. Not active. |
| Empty house | Luna's grade cwd had no `AGENTS.md`. She hunted git and returned one sentence of HOLD. | Codex refuses `EMPTY_HOUSE` unless the legend carries a wrapper. |
| Stale flag | `--ignore-user-config` made Codex skip `config.toml`, auth as ChatGPT, and 401. | The flag is in the forbid list. It is not emitted. |
| Open stdin | PowerShell left stdin open. Codex printed "Reading additional input from stdin" and the log had no model id. | `execute` passes `stdin=DEVNULL`. |
| Hung re-seat | A long prompt on a second launcher hung with no last-message file. OpenCode drops a long positional tail. | Positional text over 1200 characters becomes "Read TASK.md…". The mission stays in the file. |
| Wrong via | Luna on OpenRouter chat: 200, `response_model=None`. Flex is `codex -m …:floor`. GLM smoked on the chat rail produced CoT; the seated via is `pi -p`. | `WRONG_VIA` for Luna on chat. `MIXED_VIA` for GLM on chat. A named `deepseek/…` rail pin is allowed. That is a different seat from `dsh.cmd`. |
| Windows sandbox | Codex stamps read-only even when workspace-write was asked. | Judge and WOMBAT get `--sandbox read-only` and no `--approve-for-me`. A write job gets `--approve-for-me` and no `--sandbox`. The grade still will not say the sandbox wrote the file. Host harvest does. |
| Grok worker | `grok.exe` as a CCrew worker or a subagent is a refuse. BUILD is Gitur. | `execute` raises `GROK_NOT_A_WORKER` before the process exists. The pack can still be planned. Input over 200k raises `KEEP_UNDER` even when the vendor window is 2M. |
| Public traces | Broadcast wrote prompts into a world-readable bucket. | G47 writes `g47-plan.json` into the attempt worktree only. It does not upload a trace. |

`classify()` never sets `retry_same` true. Branch on the class. Do not fire the same pin again and call it a new attempt.

## Take-rate

Take-rate here means the share of calls that come back in the legal shape, on the pin you named, inside the window you measured. The levers that moved that number in the seating runs are the ones in the code:

1. **One door, the door that was measured.** GLM is `pi.cmd -p --provider zai --model glm-5.3-flash --tools read,write,edit --no-session`. DeepSeek's binary is `dsh.cmd --profile headless`. Ling paid is `opencode run --dir … -m openrouter/<slug>`. Luna's flex suffix belongs on Codex. Mixing those is how a pack that was active on Monday failed on Tuesday.
2. **Pack weight follows the door.** A strong door already owns the loop, the tools, and the worktree. It receives the mission and one contract line. The wrapper goes in the file that door loads (`AGENTS.md`, or `WRAP.md` for Pi's `--system-prompt`). A weak door (OpenRouter chat, Vertex without a tools array) gets WRAP as the system turn and STYLE on the user tail. STYLE on the system turn canceled the tool call. A none-door (bare mouth, unseated Hermes) gets an outfit card that says no harness is running.
3. **Skills are paths or the line `none extra`.** Pasting a skill body is a context tax. Claiming "none extra" when a skill was accepted is a failed spawn. The caller passes paths, or the file says `none extra`.
4. **The contract is one line and it does not list answers.** Fizz prompts that listed the answers taught the label instead of the rule. Ping shape is `NONE` then `HERO_OK <slug>`. A ping can be mouth-correct and still have `task_pass` false.
5. **Do not bake 2048, 4096, or 8192.** The live summoner still defaults `--max-tokens 2048`, and 256 starves a reasoning model. G47 computes MAX from the measured window. OPTIMUM is a positive aim clamped to MAX, or the string `float`. `MAX ≤ 0` refuses `MAX_LE_ZERO`. Grok also refuses `KEEP_UNDER` above 200k input.
6. **Short argv, full mission on disk.** The positional string stays under 1200 characters. `TASK.md` holds the mission plus the contract line. That is the OpenCode drop and the hung-spawn scar, handled once.
7. **No fallback model, no router swap.** Claude's `--fallback-model` is forbidden. The OpenRouter payload sets `allow_fallbacks` false and `routing` off. A named pin that changes mid-turn is not the pin you graded.
8. **Grade the thing the door actually did.** Worktree doors are not applied on mouth text. Filed-text doors are not applied on HTTP 200. A served model that is empty is `SKU_UNBOUND`. A served model that is a different slug is `SKU_MISMATCH`. A leading fence is `FENCE`, including when the mission asked for Python. The old grader treated a fence as a Python opening and also demanded `NONE` for every coder line, so a legal text reply and a legal Python reply could not both pass. G47 splits them: `what=text` wants the role's first line, `what=python` wants a code opening, `what=no_prose` wants exactly that one line.

## Token shape

Order is fixed. Write the prefix and the prompt, count them, then compute size, then spawn.

```
margin     = 0.20 × window
MAX        = window − cached_tokens − prompt_tokens − margin
OPTIMUM    = a positive aim, clamped to MAX, or the string "float"
```

The 20% margin is the thinking-and-error cushion. It is not an invitation to stuff the rest of the window into the prompt. Context is a list of paths. A joined ` · ` string refuses `NO_CONTEXT`. A `<pointer>` or `see docs/…` inside the mission refuses `POINTER_IN_TASK`: the board cell has to contain the bytes, because a pointer breaks and nobody can grade it. Dates and `PR #` inside a wrapper that will be loaded as `AGENTS.md` refuse `PREFIX_VOLATILE`. Codex injects that file as user messages, and a moving prefix misses the cache.

`approx_tokens` is `len // 4` and is marked `estimate=true` until the caller passes a real tokenizer count. It is there so a plan can refuse an obvious overflow. It is not a vendor count.

Prefill (`prefill_none`) exists for the class-6 mouths, Qwen 3.7 Flash in particular. It is legal only on the OpenRouter door. The live summoner drops the system turn when it prefills `NONE`, so G47 sets `wrapper_bound` false. The grader, told that the prefill was injected, does not treat our `NONE` as the model's first line. A transcript that is only the prefill is `PREFILL_ONLY`.

What stays out of the prompt, from `CORE_REVEAL.md`: the skill catalog, the repo tree, shell advice, vendor demo packs, swarm, and a second system prompt. Dark until this attempt names the layer. cDeck painting a pane is not a spawn.

## Doors

| Door | Strength | Seat | What the plan emits |
|---|---|---|---|
| cosmos-code | strong | seated as a rail, not a process | Thin pack. `execute` raises `EXECUTE_IS_RAIL`. Jail and DoneBundle stay in the scaffold. |
| opencode | strong | seated | `opencode.cmd run --dir <work> -m openrouter/<slug> -- <short>` |
| pi | strong | seated | Measured `pi.cmd -p --provider zai --model … --tools read,write,edit --system-prompt … --no-session` |
| dsh | strong | seated | `dsh.cmd --profile headless <short>`. Missing key file is `NO_KEY` at execute. The file is not read. |
| codex | strong | seated | `codex exec --skip-git-repo-check --json --color never --ephemeral -m <sku>`. Judge/WOMBAT add `--sandbox read-only`. Write adds `--approve-for-me` only. |
| copilot | strong | seated | `copilot.cmd` with `--allow-all-tools` and `-s`. Model names were unverified on 2026-09-29. |
| grok | strong | binary exists; worker spawn refused | Pack plus the 200k keep-under. `execute` raises `GROK_NOT_A_WORKER`. |
| openrouter | weak | seated as a payload, not a CLI | Empty argv. `rail` dict for the caller. No invented tools array. |
| vertex | weak | seated | `gemini.cmd -m -p`. `--harness` is forbidden. No tools array was applied on generateContent. |
| claude | strong | **unseated** | Steal-list argv from Claude Code 2.1.88: `--bare`, `-p`, `--max-turns`. `--fallback-model` and `--dangerously-skip-permissions` are forbidden. `execute` raises `UNSEATED`. |
| hermes | none | unseated | Outfit card. Pools, if seated later, are `fill_first` and ignore DeepInfra. Not a fallback onto Anthropic. |
| antigravity | strong | unseated | No argv. SDK configs exist; the IDE launcher is not an agent run. |
| none | none | unseated | Outfit card. Do not claim a harness ran. |

Aliases: `deepseek` → dsh, `openai` → codex, `gemini` → vertex, `ling` → opencode, `glm` → pi.

ORC on a strong coding door refuses `ORC_NO_CODING`. A folder grant is the pen. CCr is `CCR_NOT_A_DOOR`. A daemon is `DAEMON_NOT_LLM`.

## What is deliberately not ported

From Claude Code 2.1.88, recorded in `hero_unify.py`: the `query.ts` `while(true)`, `fallbackModel` swapping the pin mid-turn, bash-ask-at-50, and the yolo classifier's fast allow. From our own runners: baking `max_tokens=2048`, appending `:floor` onto `:free`, treating `mouth.txt` as the worktree grade, and starting `grok.exe` from the planner.

G47 does not publish `live/`, does not take the CCr lease, and does not delete. Materialize refuses a worktree whose path is `live`. An existing `AGENTS.md` is left alone; the native file wins over a generated copy.

## Applied

Applied means the door bound each layer it claims and the reply obeyed. A written `PACK.toml` is not a pass. `require_duds` checks the outfit. G47's grade is the reply half:

- mouth shape matches `what` and the role's first line
- a ping does not count as a finished task
- the served SKU matches the pin, when the caller supplies it
- a worktree door also has `worktree_obeyed=true` from a later harvest

One process, no retry that clears a failed grade, no second launcher.
