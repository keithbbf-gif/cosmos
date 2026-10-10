# Checks

The four checkers are `py_compile`, `ruff`, `mypy`, and `pytest`, in that
order. This page is how to run them. COSMOS is not finished. A row of passes
is not a finished product, not a live serve, and not the runtime-binding
gate. Quote the output you saw. Do not treat a missing tool as a pass.

`py_compile` is in the Python 3.14 standard library. The other three are not.
Several packages list them as optional dev dependencies: `pytest>=8`,
`ruff>=0.6`, `mypy>=1.11`. The interpreter in the commands below is
`py -3.14`.

## What each one answers

| Checker | Question | A zero is not |
| --- | --- | --- |
| `py_compile` | Does this file compile? | Behavior, types, or tests. |
| `ruff check` | Does this file meet the lint select? | A format pass. Do not run `ruff format` for this bar. |
| `mypy` | Do the names this config checks type-check? | A proof that imports outside that config are sound. |
| `pytest` | Did the named tests pass? | Live composition. Exit 5 is `NO_TESTS`, not a pass. |

Status words used by the checkers in this tree:

| Status | Meaning |
| --- | --- |
| `PASS` | Return code 0. |
| `FAIL` | Any other failure, including a timeout. |
| `MISSING` | The tool is not installed. Never a silent skip. Package runners use exit 127. |
| `NO_TESTS` | `pytest` returned 5 (nothing collected). It blocks. |
| `NO_CODE` | A saved reply was `NONE`. Not a command you type. |

## Do not scan the repo root

Run package checkers from that package's directory. Never point `ruff`,
`mypy`, or `pytest` at the repository root, at `.` from that root, or at
`live\`. A root scan walks `live\`. That directory is the running instance
(ledger, state, config). It is git-ignored. It is not a package.

There is no root `pyproject.toml`, no root `pytest.ini`, and no
`tests\conftest.py`. A bare `ruff check`, `mypy`, or `pytest` in the clone
is a root scan. Name files, or name the package's own source directories.
Do not pass the parent of `live\`.

GitLab CI (`.gitlab-ci.yml`) is narrower than this page. It compiles
`cosmos\*.py` and runs `tests\test_*.py` as scripts with `PYTHONPATH=cosmos`.
It does not run `ruff`, `mypy`, or `pytest`. A green CI job is not these
four checkers.

cDeck's JavaScript is not graded here.

## House ruff for loose core modules

Loose modules under `cosmos\` have no package table. Their ruff bar is
`cosmos\ruff.toml`, passed with `--config`. The file says:

- `line-length = 120`
- `target-version = "py314"`
- select `E`, `F`, `I`
- ignore `E501`

`E501` stays ignored. Do not select the ruff default set (`UP`, `SIM`, `PL`,
`RUF`). Do not format for style. Do not point this file at a package that
has its own `pyproject.toml` unless you mean to replace that package's
select list.

There is no house `mypy` config for these modules. The hand check follows
imports only as far as `--follow-imports=skip`.

Name the module. Do not pass the repo root. From the clone, with one file
as the example:

```text
py -3.14 -m py_compile cosmos\cosmos_health.py
py -3.14 -m ruff check --config cosmos\ruff.toml cosmos\cosmos_health.py
py -3.14 -m mypy --follow-imports=skip cosmos\cosmos_health.py
py -3.14 -m pytest -q -p no:cacheprovider --tb=line --basetemp $env:LOCALAPPDATA\Temp\cosmos-pytest tests\test_health_clock_optin.py
```

`ruff check cosmos --config cosmos\ruff.toml` stays inside `cosmos\`. That
is not a root scan. It is also wider than the file you changed. Prefer the
file.

Core tests live in `tests\`. Many of them insert `cosmos\` on `sys.path` and
can also be run as `py -3.14 tests\<file>.py`. That script run is not
`pytest`. Suites that write a heartbeat or a lock must write under the OS
temp directory (`tests\cosmos_test_guard.py`). Do not point a suite at
`live\`.

The saved-reply runner (`cosmos\cosmos_code_checks.py`, schema
`cosmos-code-checks/1`) is a different entry. It runs the same four tools on
one file and records rows in the runtime root's `state\code_checks.db`. That
database is not source. Do not commit it. That runner calls `ruff check` on
the file without `--config cosmos\ruff.toml`, and its `pytest` argv does not
set a basetemp. A hand check of a loose core module still uses the config
and the basetemp rule on this page. The formatting contract for replies is
`docs\CANON_4C_JUDGE.md`.

## Package checkers

Change into the package directory first. The tool then reads that
directory's `pyproject.toml`, and the walk does not enter `live\`.

| Directory | What is different |
| --- | --- |
| `hermes\` | Ruff matches the house select. Mypy is `--strict` on `cosmos_hermes`. Runner: `py -3.14 check4.py`. Chapter: [pkg-hermes](pkg-hermes.md). |
| `federation\` | Same ruff shape. Mypy is `--strict`. Runner: `py -3.14 check4.py` or `py -3.14 check4.py <slug>`. Chapter: [pkg-federation](pkg-federation.md). |
| `voice\` | Ruff line length 100, select `E`, `F`, `I`, and `E501` is not ignored. Mypy is strict. Runner: `py -3.14 check4.py`. |
| `voice_duplex\` | Ruff line length 100, target `py311`, select `E`, `F`, `I`, `UP`. Mypy is Python 3.11. Runner: `py -3.14 scripts\check4c.py`. The Android tree is not part of that compile. |
| `tokenctr\` | Ruff matches the house select. Mypy `files` are the pay modules named in that `pyproject.toml`, with `follow_imports = skip`. No `check4.py`. |
| `cosmos_code\` | Ruff matches the house select, with `E402` ignored on `cosmos_code\__init__.py`. Mypy and pytest also see `..\harness\G47`. |
| `cosmos_harness\` | Ruff matches the house select. Mypy package is `cosmos_harness`. Pytest `pythonpath` includes `..\harness\G47`. |
| `harness\G47\` | Ruff matches the house select. Mypy package is `g47` and excludes `seats\`. |
| `clusters\` | Pytest only in `pyproject.toml` (`pythonpath` `.`, `testpaths` `tests`). No ruff or mypy table. Chapter: [pkg-clusters](pkg-clusters.md). |

From the package directory, one checker at a time, with that package's own
paths (the `src` and `files` lists in its `pyproject.toml`):

```text
py -3.14 -m py_compile <files>
py -3.14 -m ruff check <package dirs>
py -3.14 -m mypy <packages or files>
py -3.14 -m pytest -q -p no:cacheprovider --tb=line --basetemp $env:LOCALAPPDATA\Temp\cosmos-<package>-pytest
```

In `cmd.exe` the temp folder is `%LOCALAPPDATA%\Temp\...`. PowerShell does
not expand that form. Use `$env:LOCALAPPDATA\Temp\...`.

A package `check4.py` already sets its working directory to the package.
Read that package's chapter before widening the targets. `voice` and
`voice_duplex` are deliberately not the house ruff file.

## Pytest basetemp

Pytest's basetemp belongs under the user temp directory. On this machine
that is the OS temp dir (`tempfile.gettempdir()`), which is
`%LOCALAPPDATA%\Temp`. Give each run its own folder there.

Do not put basetemp in the clone, under `live\`, or on a stream path.
`-p no:cacheprovider` keeps `.pytest_cache` out of the working tree.
`hermes`, `federation`, and `voice` already pass that flag from their runner
or from `addopts`.

`clusters\pyproject.toml` currently pins
`--basetemp=V:/streams/clusters/_pytest_tmp`. That path is not the user temp
directory. A `--basetemp` on the command line overrides `addopts`. When you
run that suite, pass a directory under the user temp directory.

The shared pytest basetemp on this machine is not a place to rely on.
`hermes` path tests avoid `tmp_path` and create a private directory with
`tempfile.mkdtemp` for that reason. If you do let pytest create temporary
directories, the basetemp you pass is still the user temp directory.

`pytest` exit 5 means nothing was collected. Record `NO_TESTS`. Do not
record `PASS`.

## What a pass does not close

COSMOS is not finished. These checkers do not start the service, do not
open the ledger, and do not decide dispatch, SpendGate, seats, voice, or
Token Center. Those limits are in the package chapters and in
`docs\modules\core.md`. An isolated pytest is not live composition.
Return code 0 is not the runtime-binding gate.
