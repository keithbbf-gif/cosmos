# pathscan

The scanner reports machine-local paths in the day-one surface. It does not rewrite the live tree and it does not open `live/`.

## What I read

I read `CONTRACT.md`, the federation `README.md`, and `cosmos_federation/product.py`. I ran `scan_root` once on `V:\A\Ai\COSMOS` and counted hits by kind. The run opened `cosmos/*.py`, `README.md`, `serve.bat`, `kdash/*.html`, and `docs/federation/*.md`. It did not open `live/`, `.git`, `node_modules`, `__pycache__`, `src-tauri`, or `_delme`. It did not open the one `cosmos/*.py` whose name contains `secret`.

## What is already true

The live README forbids hard-coded paths and says a peer can install on a cold machine. It still says Pre-implementation. `serve.bat` resolves `%~dp0` and carries no drive letter, UNC, Keith tree, R2 store, or taken tree id. The kdash pages are telemetry. They do not contain those literals. `repo_disposition` already denies a drive letter and a UNC path. `check_tree_id` already refuses `KMesh-COSMOS-live`. The kernel still contains the other literals. That is the gap this slot measures.

## What this proposal adds

`scan_text` and `scan_root` return frozen `Hit` values (`rel`, `line`, `kind`, `excerpt`). The excerpt is `redact` of the matched span, then at most 120 characters. `SCHEMA` is `cosmos-federation-pathscan/1`.

A drive letter is this machine's layout. A peer disk is not that letter. Two forward slashes after a letter are a URL, not a drive. One backslash and `n`, `t`, `r`, `a`, `b`, `f`, or `v` inside a non-raw string is an escape, not a folder. A UNC or `\\?\` device path names a host root the installer cannot assume. `V:\A\Ai\COSMOS` is Keith's checkout. Identity is a sentinel, not that tree. `V:\Ai` is the parent mesh on Keith's workstation. `D:\R2Cloner` is Keith's object store. Day one does not open it. `KMesh-COSMOS-live` is an installed tree id. A new peer cannot take it.

## Counts

One scan of the live tree on 2026-10-01 opened 261 allowlisted files and skipped 1 secret-named module. 81 files produced 195 hits. `README.md`, `serve.bat`, and `kdash/*.html` contributed none. `cosmos/*.py` contributed 191. `docs/federation/*.md` contributed 4.

| Kind | Hits | Why it blocks a clean machine |
| --- | ---: | --- |
| DRIVE | 91 | The path names a letter on this workstation. |
| UNC | 1 | The path names a host or device root. |
| KEITH_TREE | 55 | The path is Keith's checkout, not a sentinel. |
| KEITH_AI | 42 | The path is Keith's parent mesh. |
| R2_STORE | 0 | The object store is absent here and still refused if it appears. |
| TAKEN_ID | 6 | The tree id is already taken. |

No hit excerpt still matched a secret shape.

## Refusal codes

`BOUND` refuses a label or a text that is the wrong type, empty, too long, or contains a null. `PATH` refuses a label that is a drive, a UNC, an absolute path, a `..` segment, a skipped directory, or a secret-shaped filename. `ROOT` refuses a root that is not a directory, and a root whose path contains `live`, `.git`, `node_modules`, `__pycache__`, `src-tauri`, or `_delme`. `READ` refuses an allowlisted file that cannot be read. The detail does not echo file bytes.

## How CCr lands it

CCr runs `scan_root` on the ship set before cutting an installer. A hit refuses the package. The fix replaces shipped literals with sentinel-relative roles and leaves this checkout in place. Core stays the behavior source. The gate only reads. A non-empty result means the installer must not claim a clean-machine root. The day-one surface did not name `D:\R2Cloner`. The kind stays so a later edit cannot add that store to a shipped file.
