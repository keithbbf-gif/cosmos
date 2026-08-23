# SPIKE FINDINGS — `cosmos_lock`

**Worker:** `cursor-cloud-agent` / instance `bc-63fd576e-6e16-4c50-9067-af61cef66bd0` / lane `spike/cosmos_lock`
**Stamp:** `2026-08-23T10:06:40.764+00:00` · offset `+00:00` · epoch `1787479600.765`
**Host:** Linux container (Python 3.12.3). Windows-run adapter paths are **NATIVE-DEMO-REQUIRED**.
**Brief:** `docs/SPIKE_BRIEFS.md` spike 2 · contract `docs/FINAL_ARCHITECTURE.md` · incumbent `docs/STAGE2A_INCUMBENT_BEHAVIOR.md` §2 `tree_lock.py`.

## What held

Arbiter-issued leases expire on the **arbiter clock**, not the client clock. Fencing tokens are monotonic per resource. A fenced commit presenting a superseded token is **REFUSED** and **ledgered** (`COMMIT_REFUSED` / `STALE_TOKEN`). Takeover is the recorded chain `LEASE_GRANTED → LEASE_EXPIRED → LEASE_GRANTED` (`cleanup_calls=0`); there is no silent clear and no unlink. A dying holder is recovered by advancing the arbiter clock — `release()` is never called. Torn lease JSON is `UNPARSEABLE`/`TORN_STATE`, not free. A torn or HMAC-tampered ledger refuses new composition. The two-universes test has one holder: the sandbox may write an ingress envelope (and even plant `V:\Ai\_queue\tree_lock.json` as a POSIX filename); `INGRESS_ACCEPTED` does not publish; `commit_from_ingress` is `INGRESS_CANNOT_COMMIT`. Typed absence is closed: `NOT_FOUND ≠ OUT_OF_CLOCK ≠ UNREADABLE ≠ NOT_IN_RECORD`. Import has no filesystem side effect. Unknown CLI flags exit 2.

POSIX container-run adapter parts held: `fcntl` exclusive lock (second locker `ADVISORY_LOCK_HELD`), `st_dev` same-volume, path-shape classification that refuses a Windows drive path as a native root (`IDENTITY_MISMATCH`/`WRONG_UNIVERSE`).

## What surprised

`FOUND(None)` (“looked; no active holder”) is not `NOT_FOUND` (“could not look”). Treating `value is None` as failure collapses that distinction — the bulk port must not.

A client-supplied `expires_at` is ignored in this spike. That is a guess. Refuse-don’t-guess says the bulk port should **REFUSE** a client expiry rather than silently replace it with arbiter TTL.

`fcntl` works so cleanly here it is tempting to call it enforcement. It is not. The two-universes defect was a backslash string succeeding as a Linux filename; an advisory lock on the wrong universe still “holds.” Leases stay arbiter-authoritative; OS locks stay a single-volume optimization.

Fingerprint `UNREADABLE` / `NOT_FOUND` / `CHANGED` stayed distinct only because verify does not go through `exists()`-then-read. The incumbent `_sha()` returning None for both unreadable and absent is the scar; do not reintroduce it.

## What the bulk port must change

- This Arbiter is in-process. Production is the resident COSMOS Core module behind the versioned API. Workers must not import the arbiter or write the ledger.
- Root comes from explicit `cosmos_paths` instantiation (one sentinel-verified root). This spike takes a Path; it does not walk up from `__file__`.
- Service HMAC key is a test constant here. Production key material is installation-scoped and never in-tree.
- Worker registration is an explicit set (incumbent `KNOWN_WRITERS`). OA: no hard-coded list — credentialed registration belongs in Core.
- Ledger here is hash-chained JSONL with `payload_len` inside the object. Bulk port should use the OA framed record (declared byte length outside JSON) so a torn line is rejected before parse.
- Incumbent `tree_lock.json` is not a lease. Compatibility lane may read it as a diagnostic mirror; it must never grant.
- Release never unlinks (FUSE unlink refusal). Keep append-only `LEASE_RELEASED`.
- Default TTL is the incumbent 90 minutes. Confirm COSMOS policy before copying it.

## NATIVE-DEMO-REQUIRED (queue-lane demo on live Windows)

Implemented behind `PlatformAdapter`; this container returns `NATIVE_DEMO_REQUIRED`:

| Feature | Adapter method | What the Windows demo must measure |
|---|---|---|
| Job Objects | `create_job_object` / assign / terminate | Dying-holder process tree killed; lease still expires on arbiter clock; zero cleanup |
| ReadDirectoryChangesW | `watch_directory_rdcw` | Ingress/lease-mirror wakeup latency vs the 60 s poll |
| msvcrt.locking | `msvcrt_try_lock` | Advisory lock on NTFS; still not a lease |
| Drive semantics | `windows_volume_name` / `open_extended` / `\\?\` | `V:` vs `P:` vs `\\?\` same-volume; refuse the other universe |

## MEASURED (container demo, FrozenClock TTL=8 s)

```
MEASURED grant_latency_ms=2.414
MEASURED fencing_token=1
MEASURED commit_latency_ms=1.139
MEASURED commit_ok=True
MEASURED two_universes_holders=1
MEASURED windows_path_on_posix=IDENTITY_MISMATCH:WRONG_UNIVERSE
MEASURED ingress_accepted=True
MEASURED sandbox_commit=INGRESS_CANNOT_COMMIT
MEASURED expired_holder_publish=EXPIRED_HOLDER
MEASURED takeover_chain=LEASE_GRANTED,LEASE_EXPIRED,LEASE_GRANTED
MEASURED dying_holder_cleanup_calls=0
MEASURED new_fencing_token=2
MEASURED stale_token_refusal=STALE_TOKEN
MEASURED commit_refused_ledgered=2
MEASURED torn_state=UNPARSEABLE:TORN_STATE
MEASURED job_objects=NATIVE_DEMO_REQUIRED
MEASURED readdirectorychangesw=NATIVE_DEMO_REQUIRED
MEASURED msvcrt=NATIVE_DEMO_REQUIRED
MEASURED win_volume=NATIVE_DEMO_REQUIRED
MEASURED posix_advisory_lock=True
MEASURED posix_second_lock=ADVISORY_LOCK_HELD
MEASURED not_in_record=NOT_IN_RECORD
MEASURED out_of_clock=OUT_OF_CLOCK
MEASURED demo_wall_ms=9.275
```

## pytest (this container, before final commit)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
configfile: pytest.ini
collected 40 items

cosmos/spikes/cosmos_lock/selftest.py .................................. [ 85%]
......                                                                   [100%]

============================== 40 passed in 0.16s ==============================
```

15 positive controls · 25 negative controls. Command: `python3 -m pytest cosmos/spikes/cosmos_lock/selftest.py -v`.
