# Hermes package

`hermes/` is the COSMOS copy of a NousResearch/hermes-agent review. Package name: `cosmos-hermes-proposals` (`0.1.0`, Python `>=3.11`). It was applied onto this tree on 2026-10-07 from `V:\streams\hermes`. The stream folder stays where it is. This page describes the package as it sits. COSMOS is not finished. A green checker is not a finished product, and these proposals are not landed Core.

This is not `rkchoudary/hermes`. That idea is already `cosmos/cosmos_action_chain.py`. This package does not clone NousResearch/hermes-agent and it does not paste that repo. Behavior comes from the public docs (https://github.com/NousResearch/hermes-agent and https://hermes-agent.nousresearch.com/docs/user-guide/features/overview). Each feature is original Python.

## Role

The folder holds review modules. It does not replace the live seams, and a proposal still refuses the action it was written to refuse. Those seams stay the authority:

- `cosmos_approval`
- `cosmos_delegate`
- `cosmos_recall`
- `cosmos_skills`
- `cosmos_nlcron`
- `cosmos_sandbox`
- `cosmos_mcp_client`
- `cosmos_cred_kit`
- `cosmos_dom`
- `cosmos_spend`
- `cosmos_sched`

Shared law is the `cosmos_hermes` package. Feature code imports that package and the standard library. It does not import a sibling proposal. One feature is one folder, `proposals/<slug>/`: the module, `test_<slug>.py`, and `MAP.md`. The slug list is `hermes/FEATURES.md` (69 features). The writer rules are `hermes/CONTRACT.md`. The landing notes are `hermes/DECONSTRUCTION.md`.

What the proposals are allowed to be: pure checks, descriptors, and in-memory records. What they are not: a second ledger, a second spend gate, a second scheduler, an in-process cron, a self-activating skill, a `yolo` mode, or an `off` switch. Empty allowlists enable nothing. Caps are policy. A caller who asks for a higher cap does not get it. Unknown input fails closed with a stable `Refuse` code. `run` on code execution, computer use, and home assistant does not perform the action.

There is no installer CLI and no console script in `pyproject.toml`.

## Layout

| Path | What it is |
|---|---|
| `hermes/cosmos_hermes/` | Shared kernel: `Refuse`, `PathJail`, `bound_text`, `bound_bytes`, `bound_int`, `secret_shape`, `redact`, `const_eq`. |
| `hermes/proposals/<slug>/` | One feature. Public names are that module's `__all__`. |
| `hermes/tests/test_kernel.py` | Kernel refusals, including the secret shape and the device-name jail. |
| `hermes/conftest.py` | Puts `hermes/` and each proposal folder on `sys.path` for pytest. |
| `hermes/check4.py` | The four-checker runner. |
| `hermes/pyproject.toml` | Ruff, mypy, and pytest settings for this folder only. |

`bound_text` accepts a string up to 256,000 characters and refuses a NUL (`NULL_BYTE`) or a longer string (`OVERSIZE`). `bound_bytes` accepts up to 1,048,576 bytes. `bound_int` refuses a bool (`NOT_INT`) and a value outside the given range (`OUT_OF_RANGE`).

## Run the four checkers

Run them from `hermes/`, not from the repo root. The ruff and mypy settings live in `hermes/pyproject.toml`. `check4.py` sets its own working directory to that folder. From the repo root, ruff or mypy is the wrong tree.

```
cd V:\A\Ai\COSMOS\hermes
py -3.14 check4.py
```

That one command runs all four, in order. Each line is `name STATUS exit=code`. Each checker is cut off at 180 seconds. A timeout is `FAIL`.

| Checker | What `check4.py` runs | Block rule |
|---|---|---|
| `py_compile` | `py -3.14 -m py_compile` on every `*.py` under `cosmos_hermes/`, `tests/`, and `proposals/` (`__pycache__` skipped). No files is `NONE` and exit 1. | Compile failure is `FAIL` and blocks. |
| `ruff` | `py -3.14 -m ruff check cosmos_hermes tests proposals conftest.py check4.py`. Selects E, F, and I. Ignores E501. Line length 120. | A finding is `FAIL`. `No module named ruff` is `MISSING`. |
| `mypy` | `py -3.14 -m mypy --strict` on `cosmos_hermes`, `tests/test_kernel.py`, `conftest.py`, `check4.py`, and each `proposals/<slug>/<slug>.py` plus `test_<slug>.py` when those files exist. | A type error is `FAIL`. `No module named mypy` is `MISSING`. |
| `pytest` | `py -3.14 -m pytest -q -p no:cacheprovider --tb=line`. `pyproject.toml` also sets `testpaths` to `tests` and `proposals`. | A failed test is `FAIL`. Exit 5 is `NO_TESTS` and blocks. `No module named pytest` is `MISSING`. |

Exit codes from `check4.py`: `0` only when every checker is `PASS`. `127` when any checker is `MISSING` (that wins over a plain failure). `1` when something blocked and nothing was missing. Do not treat a missing tool as a pass.

To run one checker yourself, use the same `py -3.14 -m ...` command from `hermes/`. A single feature, still from this folder, is the same four tools pointed at `proposals/<slug>/` only: `py_compile` on the module and its test, `ruff check` on that folder, `mypy --strict` on those two files, and `pytest` on `proposals/<slug>/test_<slug>.py` with `-q -p no:cacheprovider --tb=short`.

The kernel test does not use pytest's `tmp_path`. On this machine the shared pytest basetemp is not writable, so path tests create a private directory with `tempfile.mkdtemp`.

This page did not re-run the four checkers.

## Safety rules

These are the public rules in `cosmos_hermes`. Proposals call them. They are not a paste of the source.

### Long `xai-` tokens are secrets

`secret_shape` is true for a long xAI token: `xai-` (any case), not stuck to a letter or digit before it, then eight or more letters, digits, underscores, or hyphens. `xai-main` is not that shape. The suffix is shorter than eight characters, so it can stay an id.

The same check treats these as secrets too:

- an `sk-` key with eight or more token characters after the prefix
- a `Bearer` token with eight or more token characters
- an assignment of `api_key`, `apikey`, `token`, `secret`, `password`, or `authorization`

`redact` replaces those shapes and leaves the rest of the string. Assignments become `[redacted-assignment]`, bearer tokens become `[redacted-bearer]`, and `sk-` or long `xai-` keys become `[redacted-key]`. After a successful redact, `secret_shape` on that result is false. Compare two tokens with `const_eq`. It does not report which byte differed. Do not print a raw key. Proposals take credential ids.

`Refuse` carries a short stable code (`UPPER_SNAKE`, 2 to 40 characters) and an optional detail of at most 200 characters. A refusal is the result. The input is not repaired.

### Windows device names are refused

`PathJail` refuses a Windows device name before it resolves the path, so the name is never opened. The code is `DEVICE_PATH`. The stem of any path part is compared case-insensitively. The stem is the text before the first dot. These stems refuse:

- `CON`, `PRN`, `AUX`, `NUL`
- `COM1` through `COM9`
- `LPT1` through `LPT9`

`NUL` and `nul.txt` both refuse. `COM10` is not in that set.

The jail also refuses, and does not open, these shapes:

| Code | Shape |
|---|---|
| `BAD_PATH` | Empty, or not a string. |
| `NULL_BYTE` | A NUL in the path. |
| `FILE_URL` | A `file:` URL. |
| `DOTDOT` | A `..` segment. |
| `ENCODED_DOTDOT` | Percent-encoded `..`. |
| `UNC` | A path that starts with `\\` or `//`. |
| `DRIVE_ROOT` | A bare drive root such as `C:\`. |
| `DRIVE_RELATIVE` | A drive-relative path such as `C:foo`. |
| `ALT_STREAM` | An alternate data stream (a colon after an optional drive prefix). |
| `TRAILING_DOT` | A path part that ends with a dot or a space. |
| `NO_GRANT` | No grant, or a grant that is not a non-empty string. |
| `RELATIVE_GRANT` | A grant that is not absolute. |
| `RELATIVE_PATH` | A candidate that is not absolute. |
| `OUTSIDE_GRANT` | A resolved path that is not the grant and not under it. |

A grant is a list or tuple of absolute paths. `contain` returns the resolved path only when it is the grant or a child of it. Existence is not required (`strict=False`).

Other product rules the proposals share: no network, socket, subprocess, thread, or sleep in the proposal itself. No `exec`, `eval`, `pickle`, or HTTP client. A scheduler or an HTTP server is a descriptor for a later COSMOS clock or service, not a process this package starts. SQLite, when a proposal uses it, is a projection rebuilt from caller-supplied records. A missing index is `UNMEASURED`, not an empty success. Plugins are injected callables, not `importlib` from disk. Wake word is on-device or refused. API and dashboard code bind loopback unless a public grant is passed in.

## Credential-pool install

Credential-pool install stays uninstalled.

`proposals/credential_pools/` is a review module, schema `cosmos-hermes-credential_pools/1`. `CredentialPool` is an in-memory ledger of credential ids for one provider. `add` stores an id. `next_id(now)` picks the next id that is not cooling. `report` can cool an id. `rebuild` replays the hash-chained records. `status` peeks and does not rotate. The caller passes `now`. The module does not read a clock.

It does not install anything. It does not read `auth.json`, an env secret, or `cosmos_cred_kit`. It does not write a key. `reveal` always refuses with `PLAINTEXT`. `change_provider` refuses with `PROVIDER_FIXED`, including when every id is cooling. `random` selection refuses (`NONDETERMINISTIC`). There is no OAuth refresh, no socket, and no fallback onto another provider. A requested cap above 8 is recorded and not applied. Secret bytes stay in the live kit. The human names the ids.

The live seam remains `cosmos/cosmos_cred_kit.py`. Wiring this pool into that kit, or installing Hermes pool machinery (on-disk metadata, env borrow, OAuth refresh, a fallback model), is not done. Upstream Hermes install, update, and uninstall files were not given a feature slug. Do not add that install from this package.

## What this package is not

Not Core. Not a running gateway, cron, key vault, or spend gate. Not a second copy of the live seams. Not a claim that the 69 features have been accepted into the service. CCr would land a proposal later, one seam at a time, and only after review. Until that happens the proposal keeps refusing the action it was written to refuse.
