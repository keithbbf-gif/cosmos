# Linux CI suite — pass / skip counts

Measured **2026-08-23** in-container on Linux (`python3` 3.12, `PYTHONPATH=cosmos`,
`os.name != 'nt'`). Same gate as `.gitlab-ci.yml` (`python` on the GitLab
`python:3.12` image).

## Result

| | count |
|---|---|
| Suite files (`tests/test_*.py`) | 21 |
| File failures | **0** |
| Checks recorded | **336** |
| Checks executed | **327** |
| Checks self-skipped (`SKIPPED-NON-NATIVE`) | **9** |

Every file printed `SELFTEST PASS`. Skips are recorded as passed with a
`SKIPPED-NON-NATIVE` note — the same pattern the MAX_PATH native demo already used.

## Per-file

| file | status | checks | ran | skipped |
|---|---|---:|---:|---:|
| test_browser.py | PASS | 8 | 7 | 1 |
| test_command.py | PASS | 14 | 14 | 0 |
| test_concurrency.py | PASS | 17 | 17 | 0 |
| test_core.py | PASS | 19 | 19 | 0 |
| test_cosmos_lock.py | PASS | 18 | 18 | 0 |
| test_cosmos_mail.py | PASS | 12 | 12 | 0 |
| test_cosmos_paths.py | PASS | 16 | 15 | 1 |
| test_features.py | PASS | 28 | 26 | 2 |
| test_kernel.py | PASS | 13 | 13 | 0 |
| test_migrate_health.py | PASS | 8 | 8 | 0 |
| test_node_rails.py | PASS | 12 | 12 | 0 |
| test_port_plan.py | PASS | 21 | 21 | 0 |
| test_segments.py | PASS | 21 | 21 | 0 |
| test_spend_context.py | PASS | 15 | 15 | 0 |
| test_stage7_fixes.py | PASS | 13 | 13 | 0 |
| test_surfaces.py | PASS | 15 | 15 | 0 |
| test_tls.py | PASS | 3 | 3 | 0 |
| test_tools.py | PASS | 18 | 18 | 0 |
| test_v1.py | PASS | 18 | 18 | 0 |
| test_wave3.py | PASS | 31 | 26 | 5 |
| test_wave4.py | PASS | 16 | 16 | 0 |
| **total** | **21 PASS** | **336** | **327** | **9** |

## What was skipped (Windows-native only)

These checks use `msvcrt` / `taskkill` / the `py` launcher / WinError / a live
Windows browser. On Linux they record `SKIPPED-NON-NATIVE` and do not fail the
gate. Pure-Python checks in the same files still run.

| file | skipped check | why |
|---|---|---|
| test_browser.py | live Chrome/Edge `--dump-dom` navigate | Windows Chrome/Edge native demo |
| test_cosmos_paths.py | MAX_PATH native demo (WinError 206/3 at creation) | WinError / `\\?\` path |
| test_features.py | subprocess UTF-8 via `py -3.14` | Windows `py` launcher |
| test_features.py | `run_tree_killed` timeout + kill report | `py` launcher + `taskkill /T` |
| test_wave3.py | five M5 runner execute/outcome checks | runner argv is `py -3.14` |

Not skipped (they are logic, not OS calls):

- Drive-letter **strings** used as surface/path identifiers (`V:\`, `P:\`,
  `C:\Windows\...`) — refused or stored, never opened as a Windows volume.
- Ledger locking — `fcntl.flock` on Linux, `msvcrt.locking` only on Windows.
- MAX_PATH CAS / `makedirs` past 260 chars — Linux has no 260-char create limit;
  those checks ran and passed.
- `py:` **prefix** helper/traversal refusals (K4, M5 helper) — path logic,
  no launcher.

## How to reproduce

```bash
export PYTHONPATH="$PWD/cosmos"
fail=0
for t in tests/test_*.py; do
  echo "== $t =="
  python "$t" || fail=1
done
exit $fail
```

On this Linux agent the interpreter is `python3` (no `python` on PATH). The
GitLab job uses the `python:3.12` image, which provides `python`.
