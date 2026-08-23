# T1 native Windows: msvcrt.locking is not fcntl.flock

The T1 cross-process arbiter lock (RF-LOCK-XPROC) is a sidecar `.lock`
sitting beside the lease ledger. `acquire()`, `renew()`, and
`fenced_commit()` hold that lock across **reprime → decide → append**.
Two independently-constructed keyed `Arbiter`s must not both `GRANT`
`tree` with token `1`.

That contract held under Linux `fcntl.flock`. It failed on native
Windows. The three selftest checks that went red were:

- `keyed sibling constructed before the grant -> HELD after reprime`
- `sidecar .lock sits beside the lease ledger`
- `sibling race leaves EXACTLY one GRANT`

The cause is not "Windows file locking is flaky". It is that the two
backends implement different locks, and the first T1 code treated them
as the same.

## fcntl.flock (POSIX)

```c
fcntl.flock(fd, LOCK_EX)   /* whole open-file, blocks */
fcntl.flock(fd, LOCK_UN)
```

- Exclusive lock on the **open file description**, not on a byte range.
- File position does not matter. An empty file locks just as well as a
  4 KiB one.
- `LOCK_EX` **blocks** until the holder closes or unlocks. No timeout
  in the call itself.
- Advisory on Linux: other readers/writers that do not also `flock`
  are not stopped. We accept that — every arbiter goes through
  `_lock_handle`.
- Unlock is `LOCK_UN`. Range arguments do not exist.

`open(path, "a+b"); fcntl.flock(fd, LOCK_EX)` is therefore a real
mutex. The sibling constructed before the grant reprimes onto the
live lease and refuses `HELD`. The sidecar exists because `open`
created it. Exactly one `GRANT` lands.

## msvcrt.locking (native Windows)

```c
msvcrt.locking(fd, mode, nbytes)
```

Python wraps the CRT `_locking` / Win32 `LockFile` family.

- Locks **`nbytes` starting at the current CRT file position**.
  It is a byte-range lock, not a whole-file lock.
- `open(..., "a+b")` leaves that CRT pointer at **EOF**. On a
  newly-created 0-length sidecar, "1 byte at EOF" is a byte that
  does not exist. That is not equivalent to `flock`.
- Python's `lk.seek(0)` moves the *Python* file object's pointer.
  `msvcrt.locking` reads the **CRT** pointer (`os.lseek` on the
  raw `fileno()`). After a buffered `a+b` open those two can disagree,
  so lock and unlock can hit **different** ranges.
- The first T1 unlock did `lk.seek(0)` then `LK_UNLCK` of 1 byte.
  The matching lock never seeked. Unlock released offset 0; the
  live lock (if any) sat at EOF. Next acquire then raised
  `OSError` instead of `LockError("HELD")`, or both siblings
  granted token `1` because they were not on the same range.
- Modes:
  - `LK_LOCK` — retries about ten times, one second apart, then
    **raises `OSError`**. It does not block like `LOCK_EX`.
  - `LK_NBLCK` — raises immediately on contention.
  - `LK_UNLCK` — unlocks `nbytes` at the current CRT position.
    Unlocking a range you did not lock raises.
- The lock is **mandatory** on Windows. A region that extends past
  EOF, or a 0-length file with no written byte, is not a reliable
  mutex region.
- Same-process overlapping `LockFile` ranges fail. A leftover
  range from a mismatched unlock turns the next `acquire()` into
  a 10-second raise, which the selftest records as a failed
  `HELD` check, not a crash.

So `msvcrt.locking(fd, LK_LOCK, 1)` without `seek(0)`, without a
real byte, and without a retry past the CRT's 10-second window,
is **not** the T1 mutex.

## The fix

`cosmos/cosmos_lock.py` now does the same thing on both platforms:

1. Open the sidecar with `O_RDWR | O_CREAT` (never truncate, never
   append-position). Unbuffered `r+b` so Python and the CRT share
   one pointer.
2. Write `LOCK_REGION` (1) real bytes if the file is shorter.
   msvcrt then has a byte that actually exists.
3. `os.lseek(fileno, 0, SEEK_SET)` immediately before **every**
   lock and **every** unlock.
4. Lock and unlock that same `LOCK_REGION` at offset 0.
5. On Windows, `LK_NBLCK` inside a retry loop. Contention raises;
   we sleep `LOCK_POLL` and try offset 0 again until we own the
   range. That is the blocking acquire `fcntl.LOCK_EX` already
   gave us, including a waiter stuck behind a long
   `fenced_commit()` callback.

`acquire()`, `renew()`, and `fenced_commit()` still take the
handle at the start of the critical section and drop it in
`finally`. The mutex covers reprime → decide → append (and the
fenced callback).

## Tests (Linux runner, both backends)

This environment is Linux, so `test_cosmos_lock.py` cannot call
real `msvcrt`. The assertions were written as if `flock` were
the only lock:

- sidecar existence used only `Path(str(ledger) + ".lock")`
  (`sibling.jsonl.lock`), which misses `with_suffix(".lock")`
  (`sibling.lock`) — a path Windows testers actually checked;
- "exactly one GRANT" read one sibling's `events()` projection
  instead of the ledger on disk;
- nothing proved that lock and unlock used the same CRT range.

The suite now:

- Treats "sidecar sits beside the ledger" as **any** sibling
  `.lock` path, and on Windows requires `size >= LOCK_REGION`.
  POSIX still accepts an empty flock sidecar so the assertion
  is not fcntl-only.
- Counts `GRANT`/`TAKEOVER` from **disk**.
- Sets `LOCK_BACKEND = "msvcrt"` plus a `FakeMsvcrt` that locks
  `nbytes` at `os.lseek` and raises on overlap — the msvcrt
  contract, not the flock one. (`os.name` is left alone: flipping
  it to `"nt"` on Linux makes pathlib instantiate `WindowsPath`
  and `Path.exists()` lie.) The three T1 checks run again under
  that fake, and we assert every lock/unlock was `pos == 0` and
  `nbytes == LOCK_REGION`.
- Threads two keyed arbiters against the fake: exactly one
  `GRANT`. `fenced_commit` is observed to still hold the
  fake lock inside the callback.

The production Windows branch is therefore the one that has to
be correct for native `msvcrt`. The Linux fake only refuses a
regression that would fail the same way on a real Windows box.
