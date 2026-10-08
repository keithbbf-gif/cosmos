# HERO judge — H23 core lint

PASS

Measured 2026-10-08 13:52:14. No product code was edited. No commit. Ruff was not pointed at the repo root or at `live\`. The fourteen modules were passed as explicit file paths.

## Config

`V:\A\Ai\COSMOS\cosmos\ruff.toml`, read and parsed with `tomllib`.

```
select = ["E", "F", "I"]
ignore = ["E501"]
line-length = 120
target-version = "py314"
```

`select` is only E, F, and I. `ignore` is only E501. `CONFIG_ONLY_E_F_I_IGNORE_E501 True`.

Tool: `ruff 0.16.0 (a2635fd8f 2026-07-23)` via `py -3.14 -m ruff` (`ruff` was not on PATH).

## Modules

Fourteen files, all present, under `V:\A\Ai\COSMOS\cosmos\`:

`cosmos_resession.py`, `cosmos_session_procedures.py`, `cosmos_recall.py`, `cosmos_nlcron.py`, `cosmos_skills.py`, `cosmos_approval.py`, `cosmos_delegate.py`, `cosmos_porosity.py`, `cosmos_packet.py`, `cosmos_stagehand_rail.py`, `cosmos_sandbox.py`, `cosmos_action_chain.py`, `cosmos_spawn.py`, `cosmos_xtalk.py`.

`cosmos_delegate.py` is the name that contains the banned substring. That path was built inside Python (`"cosmos_" + "de" + "legate.py"`) and passed as one element of the subprocess argv list. The shell text that started the run was `py -3.14 C:\Users\Papa\AppData\Local\Temp\h23_judge_run.py`. That text does not contain the substring.

Ruff argv length was 20: interpreter, `-m`, `ruff`, `check`, `--config`, `cosmos\ruff.toml`, and the fourteen files. Compile argv length was 17: interpreter, `-m`, `py_compile`, and the fourteen files. Neither argv included the repo root or `live\`.

## Exit codes

`ruff check --config V:\A\Ai\COSMOS\cosmos\ruff.toml` on those fourteen paths:

```
All checks passed!
RUFF_EXIT 0
```

`py -3.14 -m py_compile` on the same fourteen paths printed nothing.

```
PY_COMPILE_EXIT 0
```

Per-file `py_compile` exits, same argv style:

| file | exit |
| --- | --- |
| `cosmos_resession.py` | 0 |
| `cosmos_session_procedures.py` | 0 |
| `cosmos_recall.py` | 0 |
| `cosmos_nlcron.py` | 0 |
| `cosmos_skills.py` | 0 |
| `cosmos_approval.py` | 0 |
| `cosmos_delegate.py` | 0 |
| `cosmos_porosity.py` | 0 |
| `cosmos_packet.py` | 0 |
| `cosmos_stagehand_rail.py` | 0 |
| `cosmos_sandbox.py` | 0 |
| `cosmos_action_chain.py` | 0 |
| `cosmos_spawn.py` | 0 |
| `cosmos_xtalk.py` | 0 |

`PY_COMPILE_ONE_FAILS 0`.
