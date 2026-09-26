# Layer 4 — Wrapper

**Canon:** `WRAP/{Role}` + `STYLES/{Model}` (append). Missing STYLE → `_TEMPLATE`. PREFIX not rewritten; WRAP/STYLE are tails on a stable prefix.

**Hole on LiT:** `cosmos/WRAP/JUDGE` does not exist (only CODER, CCR). `STYLES/gpt-5.6-luna` does not exist. This file **is** the JUDGE wrapper fill until Gitur lands `cosmos/WRAP/JUDGE`. Do not occupancy-write those onto `main`.

```
role = JUDGE
pen = none
propose_only = true
merge = false
first_line = KEEP | DROP | NONE | HOLD | UNMEASURED
wrap = What is the intent, and the best execution of this intent?
review = findings first, severity, file:line; summary after; NONE if empty
no_plan_as_product = true
style = STYLES/_TEMPLATE (family=default)
```

Codex injects `AGENTS.md` in the worktree as user-role messages (legend). That file must not contain dates, PR numbers, or commit hashes (those belong in the Mission pack).

## Wrapper forms (translate Keith’s code samples)

Do **not** copy the stock-order/`gpt-4o` loops. Codex CLI **is** the runner (sample 2). Kind-gate still forbids write tools on JUDGE.

| Sample | Form | DUD **What** | This JUDGE |
|---|---|---|---|
| `while True` + `tool_calls` until `msg.content` | execution loop | `text` | **Codex `exec`** does the loop. We do not reimplement `chat.completions.create`. Final mouth = last-message **text**. |
| `Agent` + `runner.run` | SDK binds instructions, model, tools | `text` | **Legend** binds those. Via = `codex-cli`, not `openai_agents`. |
| Pydantic `result_type=…` | schema on the output layer | `python` or `no_prose` | JUDGE uses **`text`** with a **required first line** (`KEEP\|DROP\|HOLD`) — a thin schema, not a Python object. CODER missions may set `what=python` (diff only) or `no_prose` (JSONL only). |

`python` = code/diff/JSON object, **no wrapping essay**. `no_prose` = machine record only (e.g. one `attempts.jsonl` line). `text` = graded prose **with** that first line.
