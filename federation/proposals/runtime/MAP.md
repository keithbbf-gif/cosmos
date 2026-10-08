# runtime

## What this proposal read

CONTRACT.md requires `plan(facts) -> tuple[Step, ...]` with integer seconds. When `embed_present` is true, the sum is at most `SOFTWARE_BUDGET_S` and no step downloads. When `py_major` is missing and the embed zip is missing, the plan raises `Refuse("RUNTIME_MISSING", ...)`. A plan never pip-installs a compiler and never runs npm or cargo.

README.md states the clock starts when the installer file is already on disk, and that today's serve line expects the person to already have Python 3.14. That expectation is not a two-minute clean install.

`cosmos_federation/product.py` sets `INSTALL_BUDGET_S` to 120, `SOFTWARE_BUDGET_S` to 90, and `KEY_PASTE_BUDGET_S` to 30. The download of the installer sits outside the clock. A Rust or npm build is inside no plan.

The live tree is read-only. `serve.bat` launches `py -3.14` against `cosmos\cosmos.py` and a `live` root a stranger does not receive. `cosmos/cosmos_clock.py` sets `PY_LAUNCHER` to `("py", "-3.14")`. Neither file unpacks an embeddable interpreter. The zip named below was not downloaded.

On 2026-10-01 the python.org Windows downloads page lists Python 3.14.8 (Sept. 30, 2026) as the latest Python 3.14 release. Its Windows embeddable package (64-bit) filename is `python-3.14.8-embed-amd64.zip`. The same page also lists `python-3.14.8-embed-win32.zip` and `python-3.14.8-embed-arm64.zip`. This proposal packs only the 64-bit file.

## What is already true

A machine that already has the Windows Python launcher and CPython 3.14 can start Core with `py -3.14`. A clean machine has no such interpreter. The live serve banner still points at `kdash/index.html` and still assumes Python is installed. There is no root `pyproject.toml` in the product notes, and day-one kernel imports are treated as the standard library. cDeck under `builds/cdeck` is a Tauri skin and is not the day-one window.

## What this proposal adds

`Facts` records `os_name`, `py_major`, `py_minor`, `launcher`, and `embed_present`. `Step` records `name`, `seconds`, and `detail`. `plan` returns ordered local steps or refuses. `SCHEMA` is `cosmos-federation-runtime/1`.

The embeddable zip is packed into the installer before the user's clock starts. `plan` only names that member. It does not fetch it.

When `embed_present` is true, the plan expands `python-3.14.8-embed-amd64.zip` into `runtime/python`, points `python314._pth` at the unpacked standard library and the app tree, leaves site disabled, and probes `runtime/python/python.exe`. The packed build wins even if a system 3.14 is also present, so day one does not depend on an older patch the machine happened to have. The second total is 11. No step downloads.

When the embed is absent and the reported interpreter is CPython 3.14 or a newer 3.x (`py_minor >= 14`), the plan selects that interpreter. `launcher` true uses `py -3.14`, which is the same selector `serve.bat` already uses, and is not `py install`. `launcher` false uses the installed `python.exe`. The second total is 3.

The integers are a planned allowance for local file work and a process start. This module does not call `time.time`, so the numbers are not a stopwatch reading.

Accepted `os_name` values are `windows`, `win32`, and `nt`, compared case-insensitively. The packed file is a Windows amd64 embed, so any other OS refuses.

## Refusal codes

- `RUNTIME_MISSING` — `py_major` is None and `embed_present` is false. The plan does not download CPython to fill the gap.
- `RUNTIME_TOO_OLD` — an interpreter is present, its version is 3.x below 3.14, and the embed zip is not packed.
- `RUNTIME_UNSUPPORTED` — the reported interpreter is outside the 3.x line at 3.14 or newer, and the embed zip is not packed.
- `OS_REFUSED` — `os_name` is not Windows. This slot does not fetch a different archive.
- `BOUND` — a fact or a step field has the wrong type or shape, including a major without a minor.
- `RUNTIME_PLAN` — a step text named a download, pip, npm, cargo, a compiler, or `py install`. The plan refuses instead of emitting that step.
- `RUNTIME_BUDGET` — the second total would pass `SOFTWARE_BUDGET_S` (90).

## Seconds

- Embed present: `unpack_embed` 8 + `pin_pth` 1 + `probe` 2 = 11. Cap 90.
- Python 3.14 already present, embed absent: `use_installed` 1 + `probe` 2 = 3. Cap 90.
- Either total plus `KEY_PASTE_BUDGET_S` (30) stays within `INSTALL_BUDGET_S` (120). The remaining software budget belongs to later slots.

## How CCr lands it

CCr ships `python-3.14.8-embed-amd64.zip` as an installer member under a path the package slot creates, not as a git file in the public repo. On apply, CCr creates `runtime/python` by expanding that zip and writes `python314._pth` for the app tree. It does not call pip, npm, cargo, or the Python install manager, and it does not uncomment `import site`.

When the payload has no embed and the peer already has CPython 3.14, CCr uses the installed interpreter `serve.bat` already selects and does not install another one.

When neither is present, CCr surfaces `RUNTIME_MISSING` and stops. It does not open python.org during the clock.

Core's serve command stays the behavior source. This slot only chooses the interpreter that launches it. The `live` root on this machine is not copied.

## Files

- `proposals/runtime/MAP.md`
- `proposals/runtime/runtime.py`
- `proposals/runtime/test_runtime.py`

No extra files.
