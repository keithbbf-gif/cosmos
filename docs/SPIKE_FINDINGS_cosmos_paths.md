# SPIKE FINDINGS — cosmos_paths

**Worker:** `cursor-cloud:cosmos_paths:cursor:3535:findings`  
**Written at:** `2026-08-23T10:05:31.784+00:00` (offset-aware local)  
**UTC:** `2026-08-23T10:05:31.784Z`  
**Epoch:** `1787479531.784199`  
**Time source:** host-local-aware  
**Host:** Cursor cloud container (Linux), branch `spike/cosmos_paths`  
**Run:** https://cursor.com/agents/bc-ac4720f4-becc-4c54-abf8-63c558f67db6  
**Command:** `python3 -m pytest cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py -v -s --tb=short`

This spike is an executable probe of the resolver contract in `docs/FINAL_ARCHITECTURE.md` against the incumbent behavior in `docs/STAGE2A_INCUMBENT_BEHAVIOR.md`. It is disposable. The bulk port should reuse the lessons, not necessarily this code.

## What held

- Explicit instantiation from a machine-local installation record is enough to keep fail-fast and kill import-time side effects. Import opened zero `.cosmos-*` / installation-record files (`MEASURED import_cosmos_sentinel_opens=0`).
- One configured root, no ladder, no `COSMOS_ROOT` fallback, no neighbor-tree search. A healthy planted tree next to a record that points at a missing root is ignored. The missing root is `NOT_FOUND`, not a guess.
- Sentinel **content** is the identity check: SHA-256 digest plus installation UUID plus `system: "COSMOS"`. An existing empty directory is not a root. The mesh() lesson is a named kind: `EMPTY_DIR_TRAP` (not `NOT_FOUND`).
- Role API resolves 16 declared roles plus `root` under that one tree. `secrets` is `COSMOS_ROOT/.secrets`, a sibling of `publish` by location, not a blocklist.
- Second-install settability: two scratch roots instantiate independently. Drive-letter settability (`V:\A\Ai\COSMOS` vs `D:\Ai\COSMOS`) is proven in the adapter algebra (`V: != D:`). Live letter-to-volume binding is **NATIVE-DEMO-REQUIRED**.
- MAX_PATH-safe walk via the adapter: a 289-character path wrote, walked, and read back in 3.739 ms on this host. Extended-length algebra produces `\\?\V:\A\Ai\COSMOS` and `\\?\UNC\server\share\cosmos` and will not double-prefix.
- Typed absence does not collapse: `NOT_FOUND`, `OUT_OF_CLOCK`, `UNREADABLE`, and `NOT_IN_RECORD` are four values and four measured refusals.
- CLI unknown flag exit code is 2. Missing `--record` also exits 2 and says `COSMOS_ROOT` is not consulted.
- The two-universes scar holds as a refusal: a `V:\...` configured root on POSIX is `REFUSED` before any open. A backslash string is not a filename here.
- Windows-only APIs (Job Objects, ReadDirectoryChangesW, msvcrt.locking, GetDriveTypeW/GetVolumeInformationW, unprefixed WinError 3) are implemented behind the adapter and return `NATIVE_DEMO_REQUIRED` in this container.

## What surprised

- `fcntl.flock` will not conflict with itself inside one process. The negative control only closes if a child process loses. Same-process "second lock failed" is a false gate.
- This Linux host has no 260-character MAX_PATH clamp. A 289-character walk succeeds without `\\?\`. WinError 3 cannot be measured here; claiming it from a container run would be prose.
- Python on Linux will treat `V:\A\Ai\COSMOS` as a legal single-path name. The refuse-before-open check has to live in the adapter, not in `pathlib`.
- Replacing the sentinel file with a directory is a reliable `UNREADABLE` control under root. `chmod 000` is not (the agent is root).

## What the bulk port must change

- Boot composition instantiates `RootResolver` from an explicit installation-record path. Do not revive an import-time ladder. Do not treat `COSMOS_ROOT` as a search hint.
- `PlatformAdapter` is the only module allowed to apply `\\?\` / `\\?\UNC\`, talk to Job Objects, call ReadDirectoryChangesW, use msvcrt, or query volume identity. Business code sees logical paths.
- Role layout is a table. `secrets` stays a sibling of `publish`. No role is computed with `parent`, `__file__`, or cwd.
- `mesh()` (and any role that had an existence-only guard in BTS) requires a content sentinel. Existence is not identity.
- Typed absence is the return algebra. `None` is not an absence. Torn JSON is `UNPARSEABLE`. A future timestamp is `OUT_OF_CLOCK`. A missing declared role is `NOT_IN_RECORD`.
- CLI and every operator tool refuse unknown flags with exit 2.
- The queue-lane native demo on WRK7 must run the five items below. This container certified the refusals and the portable parts only.
- Path-rewriting / migration tools must skip prose. This note names kinds and measured numbers, not a live WRK7 path, on purpose.

## NATIVE-DEMO-REQUIRED (queue-lane demo on live Windows)

| Item | API | Why it cannot be closed here |
|---|---|---|
| Job Objects | `CreateJobObjectW` / `AssignProcessToJobObject` / `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` | No Win32 job API in this container |
| ReadDirectoryChangesW | `ReadDirectoryChangesW` + `CreateFileW FILE_FLAG_BACKUP_SEMANTICS` | Interrupt-driven wakeup vs the 60 s poll |
| msvcrt.locking | `msvcrt.locking(LK_NBLCK)` | CRT lock; POSIX counterpart (`fcntl`) is what ran here |
| Live drive / volume | `GetDriveTypeW` / `GetVolumeInformationW` | Second install on a real `D:` vs `V:` volume |
| MAX_PATH WinError 3 | `stat` of a 275+ char path **without** `\\?\` | Incumbent C-60; prefix algebra is tested, the error is not |

Adapter entry points already exist for each row. The native demo should print MEASURED latencies (especially ReadDirectoryChangesW vs 60 s) and the WinError 3 reproduction.

## MEASURED (container)

| Claim | Value |
|---|---|
| instantiate_ok_ms | 1.911 |
| instantiate_ok_kind | FOUND |
| roles_resolved | 17 |
| second_install_roots | 2 |
| long_path_chars | 289 |
| long_path_walk_ms | 3.739 |
| missing_root_refusal | NOT_FOUND (0.126 ms) |
| wrong_identity_refusal | IDENTITY_MISMATCH |
| empty_dir_trap | EMPTY_DIR_TRAP |
| torn_sentinel_refusal | UNPARSEABLE |
| unreadable_sentinel_refusal | UNREADABLE |
| out_of_clock_refusal | OUT_OF_CLOCK |
| not_in_record_refusal | NOT_IN_RECORD |
| unknown_role_refusal | REFUSED |
| unknown_flag_rc | 2 |
| import_cosmos_sentinel_opens | 0 |
| two_universes_backslash | REFUSED |
| job_object / RDC / msvcrt / WinError 3 | NATIVE_DEMO_REQUIRED |
| pytest | 36 passed in 0.34 s |

## Pytest output (this machine, before final commit)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /workspace
configfile: pytest.ini
collecting ... collected 36 items

cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_instantiate_against_valid_root MEASURED instantiate_ok_ms=1.911
MEASURED instantiate_ok_kind=FOUND
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_role_api_resolves_under_one_root MEASURED roles_resolved=17
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_secrets_is_sibling_of_publish_by_location PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_second_install_at_different_path MEASURED second_install_roots=2
MEASURED second_install_ids_distinct=True
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_second_install_drive_letters_are_distinct_identities MEASURED drive_letter_settability_algebra=V: != D:
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_max_path_safe_walk_275_plus MEASURED long_path_chars=289
MEASURED long_path_walk_ms=3.739
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_extended_length_algebra_does_not_double_prefix MEASURED extended_length_local=\\?\V:\A\Ai\COSMOS
MEASURED extended_length_unc=\\?\UNC\server\share\cosmos
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_mesh_content_assertion_passes_when_identity_matches PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_typed_absence_kinds_are_four_distinct_values MEASURED typed_absence_core_count=4
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_every_artifact_carries_worker_offset_epoch PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_posix_advisory_lock_fcntl MEASURED fcntl_lock_held_then_conflict=True
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestPositiveControls::test_cli_report_on_valid_record MEASURED cli_report_rc=0
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_missing_root_refuses MEASURED missing_root_refusal=NOT_FOUND
MEASURED missing_root_ms=0.126
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_sentinel_wrong_identity_refuses MEASURED wrong_identity_refusal=IDENTITY_MISMATCH
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_empty_dir_sentinel_trap_detected_on_instantiate MEASURED empty_dir_trap_instantiate=EMPTY_DIR_TRAP
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_empty_dir_sentinel_trap_detected_on_mesh_call MEASURED empty_dir_trap_mesh=EMPTY_DIR_TRAP
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_import_causes_no_filesystem_side_effect MEASURED import_cosmos_sentinel_opens=0
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_unknown_cli_flag_exits_2 MEASURED unknown_flag_rc=2
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_missing_record_flag_exits_2_does_not_guess_env PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_env_is_not_a_fallback_for_instantiate PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_does_not_search_a_plausible_neighbor_root PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_unknown_role_refuses_do_not_guess MEASURED unknown_role_refusal=REFUSED
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_torn_sentinel_refuses_unparseable MEASURED torn_sentinel_refusal=UNPARSEABLE
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_unreadable_sentinel_is_not_not_found MEASURED unreadable_sentinel_refusal=UNREADABLE
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_digest_mismatch_is_identity_mismatch PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_windows_drive_path_refused_as_posix_filename MEASURED two_universes_backslash_refused=REFUSED
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_future_timestamp_is_out_of_clock MEASURED out_of_clock_refusal=OUT_OF_CLOCK
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_omitted_role_is_not_in_record MEASURED not_in_record_refusal=NOT_IN_RECORD
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_path_escaping_root_is_refused PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_job_object_is_native_demo_required_on_posix MEASURED job_object=NATIVE_DEMO_REQUIRED
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_read_directory_changes_is_native_demo_required_on_posix MEASURED read_directory_changes=NATIVE_DEMO_REQUIRED
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_msvcrt_locking_is_native_demo_required_on_posix MEASURED msvcrt_locking=NATIVE_DEMO_REQUIRED
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_live_volume_info_is_native_demo_required_on_posix PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::TestNegativeControls::test_max_path_winerror3_is_native_demo_required_on_posix MEASURED max_path_winerror3=NATIVE_DEMO_REQUIRED
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::test_native_demo_checklist_names_queue_lane_items MEASURED native_demo_required_count=5
PASSED
cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py::test_measured_summary_printed MEASURED selftest_controls_note=positive+negative
MEASURED_SUMMARY {"cli_report_rc": 0, "drive_letter_settability_algebra": "V: != D:", "empty_dir_trap_instantiate": "EMPTY_DIR_TRAP", "empty_dir_trap_mesh": "EMPTY_DIR_TRAP", "extended_length_local": "\\\\?\\V:\\A\\Ai\\COSMOS", "extended_length_unc": "\\\\?\\UNC\\server\\share\\cosmos", "fcntl_lock_held_then_conflict": true, "import_cosmos_sentinel_opens": 0, "instantiate_ok_kind": "FOUND", "instantiate_ok_ms": 1.911, "job_object": "NATIVE_DEMO_REQUIRED", "long_path_chars": 289, "long_path_walk_ms": 3.739, "max_path_winerror3": "NATIVE_DEMO_REQUIRED", "missing_root_ms": 0.126, "missing_root_refusal": "NOT_FOUND", "msvcrt_locking": "NATIVE_DEMO_REQUIRED", "native_demo_required_count": 5, "not_in_record_refusal": "NOT_IN_RECORD", "out_of_clock_refusal": "OUT_OF_CLOCK", "read_directory_changes": "NATIVE_DEMO_REQUIRED", "roles_resolved": 17, "second_install_ids_distinct": true, "second_install_roots": 2, "selftest_controls_note": "positive+negative", "torn_sentinel_refusal": "UNPARSEABLE", "two_universes_backslash_refused": "REFUSED", "typed_absence_core_count": 4, "unknown_flag_rc": 2, "unknown_role_refusal": "REFUSED", "unreadable_sentinel_refusal": "UNREADABLE", "wrong_identity_refusal": "IDENTITY_MISMATCH"}
PASSED

============================== 36 passed in 0.34s ==============================
```
