# SOP — coder calls (measured 2026-09-25)

No Judge. No extra grok.exe. Ping only. Mouths are not a finished set.

## How the coders are doing

1092 board rows, all PENDING. Finished sets: 0.

wish-18 harness crew (qwen3.7-flash, North, Hy3) returned python that stores tag, assignment, and a timestamp. Not 4Cs'd. Nex rotated out after 3 fails.

## Call each model

| Model | Command | This pass | Scar |
|---|---|---|---|
| GLM `z-ai/glm-5.3-flash` | `pi.cmd -p --provider openrouter --model z-ai/glm-5.3-flash --no-tools` | Returned. First line was a fence, not `def ping():`. | `PI-PS1` execution policy blocks `pi.ps1`. Use `pi.cmd`. `ZAI_API_KEY` absent; OpenRouter fallback worked. `FENCE` |
| GF38 `gemini-3.8-flash` | `VertexRail(key_file, spec).dispatch({prompt, model})` | `ok True`. First line `def ping():`. | `VERTEX-CTOR` there is no `from_config`. Pass `key_file` plus the json spec. Set `role=coding`. |
| DeepSeek | `dsh.cmd --profile headless` | Not called. | `DS-NO-KEY` `live/config/deepseek_api_key.txt` absent. `dsh.ps1` also blocked. Use `dsh.cmd` after the key exists. |
| Ling | `opencode.cmd run --dir WORKTREE -m openrouter/inclusionai/ling-3.0-flash` | Returned. First line was a fence. | `FENCE`. Binary is 1.18.30, docs say 1.18.31. |
| OpenRouter seats | `py -3.14 work_orders/ccr/_summon_or_hero.py --pack --duds --model` | qwen37, North, Hy3 already summoned. Pack must pass `require_duds` or the script refuses. | Do not raw-dispatch. |
| Codex `gpt-5.4-mini` | `codex exec --sandbox workspace-write` | Not fired. | Opt-in. Do not point it at the live tree. |
| Grok | Cursor Gitur only | Not fired. | No extra `grok.exe`. |
| Hermes | wishlist | Not installed. | Do not `hermes auth add`. |

## Tabled

Free OpenRouter seats are tabled. 429 is the free-provider cap (20/minute; 50 or 1000/day). Not a pack defect. Do not call `:free` until that cap is clear.

## Sample abc (no preload)

Prompt: write `abc.py`, few lines, `def abc(): return "abc"`.

| Seat | File | Format | Answer |
|---|---|---|---|
| GLM `pi.cmd --tools write` | `live/work/pi-home/abc/abc.py` written | python, 2 lines | wrong: `return abc` (the function, not `"abc"`) |
| Ling `opencode run` | `live/work/opencode-home/abc/abc.py` written | python, 2 lines | wrong: same |
| GF38 `VertexRail.dispatch` | no file. Rail cannot write. Mouth saved by the caller. | python, 2 lines | right: `return "abc"` |
| DeepSeek | not called | | no key |

Scar: `ABC-BARE` was the caller. PowerShell ate the quotes. `call_pi_glm.py` had `--no-tools` and a `NONE|diff` system prompt. MCP is not required. Pi and OpenCode have built-in write. Vertex `generateContent` has no tools; the caller files the reply.

Retest with a Python argv (quotes kept) and `--tools read,write,edit`: Pi `abc2` and Ling `abc3` both `abc() == "abc"`.

## Rules

1. Isolated worktree under `live/work/hero-ping/`. Do not cwd the live tree.
2. Coder reply is python only. A fence is a fail, not a pass.
3. Results stay out of `builds/cdeck`.
4. Port 8770 is not part of these calls.
