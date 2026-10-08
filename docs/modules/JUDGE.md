# HERO judge — finish wave

NOT DONE

Poll of the wave-2 result files at 2026-10-08 13:45:36. A missing file was not run. PASS is only an exit this judge saw as 0. FAIL is only a non-zero exit this judge saw. No product code was edited. No commit. `grok.exe` was not started. The live `install_key.bin` was not opened. Ruff and mypy were not pointed at the repo root or at `live\`. Pytest basetemp for these runs is under `C:\Users\Papa\AppData\Local\Temp\c4-judge`. One suite at a time. None hit the two-minute cap.

The verdict is not DONE. These stay open even where a checker passed:

- Hermes pool install is tabled. `docs/modules/hermes.md` says credential-pool install onto the live tree is TABLED. The hermes result says no key file was read and no pool was installed.
- Voice refine is tabled. `docs/modules/voice.md` says voice refine is TABLED and this tree does not ship a phone APK. The voice result says refine was not built.
- The chatbot phone is not to be published. `cosmos/cosmos_publish_stage.py` writes `"publish": False` and `"chatbot": False` on the staged manifest. This judge published nothing.
- Per-source meter recipes are not written. No recipe text is in the `cosmos` meter modules. `meter_window` is a fixture fold, not a per-source recipe.
- Resession must not spawn. `plan_resession` stays dry (`execute` false) and the script below did not call `subprocess.run`. `spawn_auto_resession` still launches grok when `execute=True`. That path was not removed. This judge did not start it.
- Dispatch stays locked. `Provider.prepare_call` in `cosmos_code/cosmos_code/propose.py` raises `DISPATCH_LOCKED` (`no provider is bound`).
- cDeck day/week stays UNMEASURED. `builds/cdeck/ui/header.js` `renderTokStrip` still writes the literals `day UNMEASURED` and `week UNMEASURED`. It does not call `meter_window`. No ledger events were folded into the deck here.
- Token Center is not on SpendGate. `Store.reserve` in `tokenctr/cosmos_pay_gateway.py` subtracts `credits_face_usd` in its own database. It does not import `cosmos_spend`. The comment that says to bind SpendGate is not that wire.

## Result files

| file | grade |
| --- | --- |
| `c4-rails2-result.md` | NOT_MEASURED (absent) |
| `c4-cdeck2-result.md` | NOT_MEASURED (absent) |
| `c4-core2-result.md` | pytest, ruff, mypy, py_compile, rail script PASS; hermes-features script FAIL |
| `c4-resession-result.md` | PASS |
| `c4-orc2-result.md` | PASS |
| `c4-pkt-result.md` | PASS |
| `c4-hermes-result.md` | PASS |
| `c4-voice-result.md` | PASS |
| `c4-fedclu-result.md` | NOT_MEASURED (absent) |
| `c4-code-result.md` | NOT_MEASURED (absent) |

### orc2 — PASS

Re-run after `cosmos_service.py` and `tests/test_orc_compose.py` both showed mtime 13:37:44. An earlier `1 passed in 1.28s` was before that edit and is not the grade.

```
1 passed in 1.44s
EXIT=0
```

`py -3.14 -m py_compile cosmos\cosmos_service.py tests\test_orc_compose.py` printed nothing.

```
EXIT=0
```

`tests/test_pilot_womb_http.py` was not run. NOT_MEASURED.

### hermes — PASS

From `V:\A\Ai\COSMOS\hermes`. Not a pool install.

```
compiled 144
EXIT=0
```

```
All checks passed!
EXIT=0
```

```
Success: no issues found in 146 source files
EXIT=0
```

That mypy command had 142 targets. Pytest, single `-q` so the count line is present:

```
1157 passed in 3.53s
EXIT=0
```

### pkt — PASS

`tests/test_packet_singular.py` and `tests/test_action_chain.py`.

```
11 passed in 0.37s
EXIT=0
```

### core2 — PASS on the 4C list, FAIL on the features script

Explicit modules, not the repo root: `cosmos_resession.py`, `cosmos_session_procedures.py`, `cosmos_recall.py`, `cosmos_nlcron.py`, `cosmos_skills.py`, `cosmos_approval.py`, `cosmos_delegate.py`, `cosmos_porosity.py`, `cosmos_packet.py`, `cosmos_stagehand_rail.py`, `cosmos_sandbox.py`, `cosmos_action_chain.py`, `cosmos_spawn.py`, `cosmos_xtalk.py`. Config `cosmos/ruff.toml`.

```
All checks passed!
EXIT=0
```

```
Success: no issues found in 14 source files
EXIT=0
```

mypy also printed `annotation-unchecked` at `cosmos_stagehand_rail.py:360`. The process exit was still 0.

py_compile of those 14 printed nothing.

```
EXIT=0
```

Pytest of the eleven files named in the result (`test_canon_spawn`, `test_cosmos_sandbox`, `test_hermes_features`, `test_nlcron`, `test_orc_compose`, `test_porosity`, `test_resession`, `test_session_procedures`, `test_stagehand_rail`, `test_womb`, `test_xtalk`):

```
50 passed in 6.36s
EXIT=0
```

`py -3.14 tests\test_rail_base.py`:

```
result: ok  33/33 on the shared rail seam
EXIT=0
```

`py -3.14 tests\test_hermes_features.py` is FAIL. The miss is the service text slice, not the approval, delegation, recall, or skills behavior checks. The key it read was created by `install()` under a temp root.

```
[FAIL] SK6 GET /skills never mkdir (handler is a ledger fold)
50/51 passed
EXIT=1
```

`tests/test_packets.py` was not run. NOT_MEASURED. The singular packet file and the action-chain file are the pkt grade above.

### resession — PASS

Source mtime 13:42:26, after the core2 pytest. This block is the later measurement. No `grok.exe`.

py_compile of `cosmos\cosmos_resession.py` and `tests\test_resession.py` printed nothing.

```
EXIT=0
```

Ruff on those two files with `cosmos\ruff.toml`:

```
All checks passed!
EXIT=0
```

```
Success: no issues found in 1 source file
EXIT=0
```

```
1 passed in 0.50s
EXIT=0
```

`py -3.14 tests\test_resession.py` printed a `schtasks` argv for `--plan-task` and then:

```
result: ok  85/85
EXIT=0
```

`py -3.14 cosmos\cosmos_resession.py --selftest`:

```
result: ok  28/28
EXIT=0
```

The plans that passed are dry. Spawn-on-execute remains in the module. See the open list.

### voice — PASS

Voice refine was not built. From each package directory.

`voice` pytest:

```
118 passed in 0.32s
EXIT=0
```

`voice` ruff `cosmos_voice tests check4.py`:

```
All checks passed!
EXIT=0
```

`voice` `py -3.14 -m mypy`:

```
Success: no issues found in 17 source files
EXIT=0
```

`voice` `py -3.14 -m mypy --strict cosmos_voice tests check4.py`:

```
Success: no issues found in 32 source files
EXIT=0
```

`voice` py_compile of `cosmos_voice\*.py`, `tests\*.py`, and `check4.py` (32 files) printed nothing.

```
EXIT=0
```

`voice_duplex` pytest:

```
66 passed in 0.26s
EXIT=0
```

`voice_duplex` ruff `cosmos_voice_duplex tests scripts`:

```
All checks passed!
EXIT=0
```

`voice_duplex` `py -3.14 -m mypy`:

```
Success: no issues found in 46 source files
EXIT=0
```

`voice_duplex` py_compile of package `*.py` except `android` and `__pycache__` (29 files) printed nothing.

```
EXIT=0
```

## Re-runs with no wave-2 file

Suites were not mid-write (python mtimes were 12:50 or earlier; the judge clock was 13:36).

### tokenctr pytest — PASS

Cwd `V:\A\Ai\COSMOS\tokenctr`.

```
12 passed in 4.85s
EXIT=0
```

This does not put Token Center on SpendGate.

### meter window — PASS

Cwd `V:\A\Ai\COSMOS\tests`. `test_meter_window.py`.

```
7 passed in 0.14s
EXIT=0
```

Day and week on the deck stay UNMEASURED. The header does not call this fold.

### session-tools pytest — PASS on the rerun

Cwd `V:\A\Ai\COSMOS\builds\session-tools`.

The first command exited 1 because the basetemp parent `c4-judge` was not there. Pytest tried to create `c4-judge\session-tools` and got WinError 3. The suite did not run.

```
3 passed, 26 errors in 0.93s
EXIT=1
```

After that parent directory existed, the same pytest command:

```
29 passed in 0.49s
EXIT=0
```

The product grade is the second line. The first line is a judge setup miss.

### orc compose

Graded under orc2, not the pre-edit run.
