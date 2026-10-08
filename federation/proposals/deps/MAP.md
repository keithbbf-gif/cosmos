# deps

## What I read

I read `CONTRACT.md`, `README.md`, and `cosmos_federation/product.py`. I read every `import` and `from` line in the 256 files at `V:\A\Ai\COSMOS\cosmos\*.py`. I did not read `live/`. I did not read `builds/`. The live tree has no root `pyproject.toml`, `requirements.txt`, `setup.py`, `setup.cfg`, or `Pipfile`. `cosmos/` has no nested Python packages.

## What is already true

The kernel declares no Python dependency file. Static import lines are the standard library plus `cosmos_*` modules, except eight THIRD modules. Those modules are `cryptography`, `cryptography.hazmat.primitives`, `cryptography.hazmat.primitives.asymmetric`, and `cryptography.x509.oid` in `cosmos_service.py` (optional TLS certificate mint); `vosk` in `cosmos_stt.py` (vendor site, absent unless that site is present); `watchdog.events` and `watchdog.observers` in `cosmos_sched.py` (poll fallback when the import fails); and `tools.surface` in `_f29_composed_live.py`. `tools.surface` is the in-repo module `tools/surface.py`, not a distribution. `cosmos_openrouter_rail.py` imports `urllib` and `cosmos_packet`. Top-level imports in `cosmos_service.py` are the standard library and `cosmos_*`. `cosmos_cred_kit.py` probes `openai`, `anthropic`, `google.genai`, and `groq` with `__import__`. Those probes are not import lines, so they are not dependencies. No `cosmos/*.py` file uses a relative import. No file imports a bare module named `cosmos`. `fcntl` is imported and is on the Python 3.14 standard-library name list.

## What this proposal adds

`classify_module` returns `STDLIB`, `THIRD`, or `LOCAL`. `LOCAL` is a `cosmos_*` module or a relative import. `STDLIB` is the running 3.14 standard-library name list, including builtins. `census` parses `cosmos/*.py` with `ast` and returns frozen `ImportRow` values (`module`, `kind`, `used_by` filenames). `dayone_pyproject` requires Python `>=3.14`. Its dependency list is the sorted THIRD import roots of that live census: `cryptography`, `tools`, `vosk`, `watchdog`. Submodule paths stay out of the list, because a dotted requirement normalizes into a different project. No build backend is declared. The same text is `pyproject.proposed.toml`. The day-one installer must not grow a hidden pip install of anything outside that measured list.

## Refusal codes

`BOUND` refuses an empty module name, a null byte, or a name past the length cap. `CENSUS` refuses a non-directory root, a missing `cosmos/` package, a path that escapes the root or the package, an unreadable file, an unparsed file, an empty import, or an `ImportRow` whose kind disagrees with `classify_module`.

## How CCr would land it

CCr copies `pyproject.proposed.toml` as the peer installer's metadata and keeps the dependency list equal to a fresh census. CCr treats `tools` as the in-repo `tools/` tree (`repo_disposition` calls that path `DEV`) and records it in-tree instead of fetching a project named `tools`. `cryptography`, `vosk`, and `watchdog` stay optional on the paths that already catch a missing import. Loopback day-one chat does not import them. The declaration is the closed list a later full install may use. It is not a clock-blocking download, and it is not a license to add `setuptools`, `requests`, `playwright`, `openai`, or `anthropic`.
