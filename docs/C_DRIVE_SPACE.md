# What is taking up room on C:  — measured 2026-08-31 ~04:30

Answering an ask that `cosmos_askmine` (F-63) found had been made **twice and never
answered**: *"Add this to the tasks list: Find out what is taking up so much room on
C: that can/needs to be moved off there."*
(`V:\Ai\_session_logs\plumbing\2026-07-14_3180225d\audit.jsonl:5113` and `:5229`.)

## The headline

    C:   used 891.2 GB   free 39.7 GB   total 930.9 GB     -> 96% FULL

## Where it went

| Location | Size | Files | Note |
|---|---:|---:|---|
| `C:\Users\Papa\OneDrive` | **274.6 GB** | 52,798 | biggest single consumer |
| `C:\Program Files (x86)` | 107.7 GB | 109,303 | unusually large for x86 |
| `C:\Users\Papa\Desktop` | 67.6 GB | 33,071 | very large for a Desktop |
| `C:\Users\Papa\AppData\Local` | 65.7 GB | 631,678 | see breakdown below |
| `C:\Users\Papa\Downloads` | 51.0 GB | 1,695 | few files, large ones |
| `C:\Users\Papa\Videos` | 29.2 GB | 19 | 19 files |
| `C:\Windows` | 28.8 GB | 405,044 | |
| `C:\Program Files` | 18.6 GB | 60,831 | |
| `C:\ProgramData` | 6.4 GB | 14,674 | |
| `C:\Users\Papa\Games` | 6.4 GB | 2,775 | |
| `C:\Users\Papa\AppData\Roaming` | **UNMEASURED** | — | the walker refused early on a reparse point; NOT reported as small |

`AppData\Local` breakdown: `Packages` 31.7 · `Google` 14.7 · `Microsoft` 4.9 ·
`Temp` 4.8 · `Programs` 3.0 GB.

## The single biggest reclaimable win

    OneDrive total                          274.6 GB
    OneDrive LOCALLY RESIDENT (real bytes)  179.8 GB   (30,291 files)

About **95 GB is already cloud-only placeholder**; the other **179.8 GB is occupying
the disk**. Right-click OneDrive -> "Free up space" converts locally-resident files
back to placeholders without deleting anything, and it is reversible per-folder. That
one action is worth more than everything else on this list combined, and it is the
only item here that frees space without moving or removing anything.

After that, in order of size and ease: `Downloads` (51 GB in 1,695 files — a handful
of large items), `Videos` (29.2 GB in **19 files**), and `Desktop` (67.6 GB, which is
where `UNSYNCED_REPORT.txt` was also supposed to land and never did — see
`docs/UNANSWERED_ASKS.md` row 1).

## Caveats, stated rather than glossed

* `AppData\Roaming` is UNMEASURED, not zero. A first pass reported it as exactly
  65.7 GB / 631,678 files — **identical to `AppData\Local`**, because the PowerShell
  error left the previous measurement in the variable. That number was wrong and is
  not in the table above. It is the same defect class this whole audit is about: a
  value that reported something other than what it measured. Caught by noticing two
  different directories could not plausibly agree to the file.
* Sizes exclude what the walker could not read; MAX_PATH and permission failures are
  silent in `Get-ChildItem`. Treat every figure as a FLOOR.
* `pagefile.sys` / `hiberfil.sys` could not be read by this pass and are not counted.
  They are typically 10-40 GB combined on a machine this size.
