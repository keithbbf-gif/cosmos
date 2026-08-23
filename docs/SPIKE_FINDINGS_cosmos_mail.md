# SPIKE FINDINGS — cosmos_mail

**Worker:** `cursor.cosmos_mail` · instance `bc-c18bfff9-6c25-43a4-b6fa-8e11af6caa32`
**Observed at:** `2026-08-23T10:08:50+00:00` (offset-aware)
**Epoch:** `1787479730.680447`
**Branch:** `spike/cosmos_mail` · container Linux / Python 3.12.3
**Contract:** `docs/SPIKE_BRIEFS.md` SPIKE 3 · `docs/FINAL_ARCHITECTURE.md` · `docs/STAGE2A_INCUMBENT_BEHAVIOR.md` §3

A spike whose claims are prose has not run. This note is the measured run.

## What held

The incumbent phone (`bts_phone.py`) is a fixed pair of letter files. At N>2 that shape is last-writer-wins. The spike replaced it with per-worker inbox directories and immutable uniquely-named messages. The name carries sender identity, a Windows-safe offset timestamp, and the payload hash (`alice__20260823T100851.263234+0000__53acd54179e9__21aa157e`). Two senders to one recipient produced two files and zero collisions.

Missing, empty, unreadable, and stale are four distinct `AbsenceKind` values. They are not collapsed, and they are not `None`. `probe` reports all of them as facets (sentinel, identity, heartbeat, inbox, unread count, oldest unanswered required-ack, last read receipt) plus a dominant `mailbox_state`. Exit codes are machine-readable: empty mailbox is `0` (a live phone with no news); missing mailbox is `3` (dead phone). That is the incumbent `--check` lesson, made usable at N>2.

Staleness is policy, not a printed mtime for a human to judge. A heartbeat older than the age threshold is `STALE` (exit `2`, FINDINGS). An unanswered `requires_ack` past `ack_deadline_epoch` is `STALE` even when the heartbeat is fresh. Send and receive are separate recorded facts: after send, `sent` and `delivered` receipts are `FOUND` and `read` is `NOT_IN_RECORD`; after receive, `read` is `FOUND`.

Refuse-not-guess held. Import creates no files. A missing root refuses send and writes nothing into cwd. An existing empty directory without the sentinel is `IDENTITY_MISMATCH` (the `mesh()` lesson: existence is not identity). A Windows drive or backslash path on POSIX is `REFUSED` (two-universes, 2026-08-16). Unknown CLI flags exit `2`.

## What surprised

The reliable `UNREADABLE` control on this container is “inbox path is a file,” not `chmod`. uid 1000 cannot hide a directory from itself as thoroughly as a type mismatch can. The incumbent already collapsed “inbox is a directory” with “inbox is missing”; the spike treats wrong type as `UNREADABLE` and missing as `NOT_FOUND`.

inotify is a real wakeup here. A 50 ms watch with no event returned in 52.3 ms with zero events — not a 60 s poll. Creating a file in a watched inbox woke the waiter and named `wake.json`. The Windows twin (`ReadDirectoryChangesW`) is present in the adapter and returns `NATIVE_DEMO_REQUIRED` on this box.

`O_EXCL` plus read-back is enough to detect a half-written message without leaning on rename. A planted JSON object with a lying `payload_hash` is `HASH_MISMATCH` (exit `8`), not empty and not missing. Torn `{` is `UNPARSEABLE`. A future `created_epoch` is `OUT_OF_CLOCK`. An unknown id is `NOT_IN_RECORD`. Those four absences from the ground rules all fired as themselves.

Windows string logic is testable off Windows. `WindowsPlatformAdapter.native_fs_path` applies `\\?\` (C-60). `interpret_drive(r"V:\A\Ai\COSMOS")` returns drive `V` as configuration, not a guess. The live V: volume, Job Objects, msvcrt locking, and `ReadDirectoryChangesW` latency are not claimed here.

## What the bulk port must change

- Inbox writes from a sandbox are ingress, not authority. The spike writes the inbox directly so the probe can run. Core must ingest an envelope, verify bytes/hash/schema/identity, ledger `INGRESS_ACCEPTED`, and only then treat delivery as a fact (`docs/FINAL_ARCHITECTURE.md`).
- Worker clocks are evidence. The spike’s injected clock is fine for tests; production staleness and ack deadlines must be judged on the arbiter/service clock.
- Receipt files are the spike’s split-fact store. The port should emit the same facts as hash-chained ledger events; files may remain a rebuildable projection.
- Case-collision refusal belongs in the worker registry, not only in mail. The spike rejects `Bob` and a planted `Bob/` vs `bob`.
- Broadcast / multi-recipient / instance-fan-out (OA B.4 `workers/<id>/<instance>/`) is not in this spike. One instance per worker (`i1`) was enough to prove N>2.
- Compatibility lane: incumbent `COW_TO_QA_ENGINEER.md` letters must not be reintroduced as a mutable outbox.

## MEASURED (container demo)

```
MEASURED send_readback_ms=4.517
MEASURED two_sender_files=2
MEASURED two_sender_collisions=0
MEASURED two_sender_ms=1.899
MEASURED empty_state=EMPTY empty_exit=0
MEASURED missing_state=NOT_FOUND missing_exit=3 dead_phone_nonzero=1
MEASURED half_written_state=HASH_MISMATCH half_written_exit=8
MEASURED stale_state=STALE stale_exit=2
MEASURED unreadable_state=UNREADABLE unreadable_exit=4
MEASURED out_of_clock_state=OUT_OF_CLOCK
MEASURED not_in_record_state=NOT_IN_RECORD
MEASURED sent_receipt=FOUND delivered_receipt=FOUND
MEASURED read_receipt_after_send=NOT_IN_RECORD
MEASURED read_receipt_after_receive=FOUND
MEASURED posix_inotify_timeout_ms=52.339 events=0
MEASURED windows_job_object=NATIVE_DEMO_REQUIRED
MEASURED windows_readdirectorychanges=NATIVE_DEMO_REQUIRED
MEASURED windows_msvcrt=NATIVE_DEMO_REQUIRED
MEASURED windows_extended_prefix=1
MEASURED posix_refuses_drive=REFUSED
MEASURED demo_ok=1
```

## NATIVE-DEMO-REQUIRED (queue-lane demo on live Windows)

These branches exist behind `WindowsPlatformAdapter` and returned `NATIVE_DEMO_REQUIRED` here. The native demo must print MEASURED numbers for each:

1. **ReadDirectoryChangesW** on a live inbox — wakeup latency vs the incumbent 60 s poll. No polling loop.
2. **Job Objects** — `CreateJobObjectW` + `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` + `AssignProcessToJobObject` around any mail-watcher/helper process.
3. **msvcrt.locking** — `LK_NBLCK` on the publish handle. Container analog `fcntl.LOCK_EX|LOCK_NB` is tested; it is not a claim that msvcrt ran.
4. **Drive semantics** — instantiate the exchange on the verified `V:` root (configuration, not a ladder). Confirm a `P:` or stale letter is refused, not guessed.
5. **MAX_PATH** — publish and probe a 275+ character inbox path with the `\\?\` prefix (C-60). WinError 3 without the prefix is the scar.

## Selftest

Positive and negative controls live under `cosmos/spikes/cosmos_mail/tests/` and run with `pytest` in this container (also `python -m cosmos.spikes.cosmos_mail selftest`).

```
$ python3 -m pytest cosmos/spikes/cosmos_mail/tests -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
configfile: pytest.ini
collected 48 items

cosmos/spikes/cosmos_mail/tests/test_cli.py ......                       [ 12%]
cosmos/spikes/cosmos_mail/tests/test_negative_controls.py .............. [ 41%]
.....                                                                    [ 52%]
cosmos/spikes/cosmos_mail/tests/test_platform_adapter.py ..........      [ 72%]
cosmos/spikes/cosmos_mail/tests/test_positive_controls.py .............  [100%]

============================== 48 passed in 0.36s ==============================
```

Negative controls that closed: missing mailbox non-zero · half-written hash · torn JSON · inbox-as-file unreadable · stale heartbeat · unanswered required-ack · missing root does not write cwd · empty-dir sentinel trap · wrong sentinel identity · `OUT_OF_CLOCK` · `NOT_IN_RECORD` · uppercase / casefold worker id · identity mismatch · `O_EXCL` collision · unknown flag exit 2.

## Typed absence catalog (this spike)

`FOUND` · `EMPTY` · `NOT_FOUND` · `UNREADABLE` · `UNPARSEABLE` · `STALE` · `OUT_OF_CLOCK` · `NOT_IN_RECORD` · `IDENTITY_MISMATCH` · `HASH_MISMATCH` · `REFUSED` · `COLLISION_REFUSED` · `NATIVE_DEMO_REQUIRED`

`NOT_FOUND ≠ EMPTY ≠ UNREADABLE ≠ STALE ≠ OUT_OF_CLOCK ≠ NOT_IN_RECORD`.
