# Ledger

COSMOS is not finished, and this page is not a completion claim. It describes the
authority primitive in `cosmos/cosmos_ledger.py` and how Core uses it. Panels,
SQLite files, and JSON snapshots are caches. They are not the record.

Ratified rule (`docs/FINAL_ARCHITECTURE.md`, decision 3): Core is the single
writer of an append-only, hash-chained, service-signed JSONL ledger on the
verified native volume. A corrupt segment is refused. It is not repaired in
place.

## What is authority

One resident service writes the chain. Queue views, registries, KDash panels,
and spend totals are rebuildable projections. A projection may be dropped and
folded again from the chain. The chain is not rewritten to match a projection.

Core opens the authority file through the path resolver, role `ledger`, name
`authority.jsonl`, under the install root identified by sentinel content. Do
not assemble that path by hand and do not treat a copy on another volume as
the live chain. The runtime root is git-ignored. Do not commit the ledger.

Large artifacts, in the ratified design, live in a content-addressed store
(filename = hash). The ledger holds the live pointer. The ledger file is not
the blob store.

Other JSONL files exist and are not this authority. The lease arbiter keeps
`ledger/leases.jsonl`. The scheduler keeps its own chain under the queue role.
Those are subsystem logs with their own verify rules. A row in one of them
does not prove a Core event. Core events are the records in `authority.jsonl`.

## One record, one line

Each line is one JSON object. New records use canonical JSON (sorted keys, no
extra whitespace) and end with a newline. Blank lines are skipped. A CRLF copy
still chains on the record bytes; the hash is of the line without the carriage
return.

Fields a current writer puts on the line:

| Field | Role |
|---|---|
| `seq` | Monotonic sequence in this file, starting at 1. |
| `event` | Caller event name. The ledger does not interpret it. |
| `t`, `utc_off` | Clock reading and UTC offset seconds. |
| `payload` | Event body. |
| `payload_len`, `payload_sha` | Length and SHA-256 of the canonical payload bytes. |
| `prev_sha` | SHA-256 of the previous record's full line. Empty on the first record. |
| `writer` | Writer identity on the record. |
| `mac_v` | `2` on records this version writes. Absent on legacy lines. |
| `hmac` | Service authentication. Not a public signature scheme description and not a key. |

`prev_sha` ties the line to the bytes of the line before it. `payload_sha`
ties the declared body to the canonical encoding of `payload`. Either mismatch
is a broken chain, including a line that parses but is not a ledger record.

## Service authentication

The HMAC is computed with the per-install key Core loads at boot. This page
does not name the key file, quote key bytes, or show a signing example. The
key is not invented if it is missing: boot refuses and tells the operator to
run the installer.

Two MAC generations verify:

- **mac_v 2** (current). HMAC-SHA256 over the canonical record with `hmac`
  removed. Every field is covered, including `event`, `writer`, and `t`.
- **Legacy.** HMAC over `seq|prev_sha|payload_sha` only. Old lines still load,
  including a shorter stored digest from an earlier writer. A v2 line cannot
  be downgraded into that rule: the stored MAC will not match.

A line that parses and chains but fails the MAC is `FORGED`. It is not
accepted as history.

## Append

Append is the only mutation. The writer takes an exclusive OS lock on a
sidecar lock file, re-reads bytes added since the last verified offset, then
writes one line and `fsync`s. The lock is what stops two processes from both
emitting the same `seq` and tearing the chain. The lock is released by the OS
if the process dies. There is no in-place edit and no truncate-and-rewrite.

`expect_head_seq` is optimistic concurrency. If the head moved after the caller
decided, the append raises `STALE_HEAD` and writes nothing. The caller
re-projects and retries. `append_guarded` holds the same lock across the whole
read-decide-append so two callers cannot both pass a check against a stale
head.

Open verifies the whole chain. Later appends and `head()` verify only the
delta. A full walk remains the gate for `verify()`, `project()`, and open. A
file shorter than the verified offset is `TRUNCATED`. A shorter file is not a
clean shorter history.

Kernel opens this ledger with the signed head anchor on. After each successful
append, a sidecar records sequence, previous-line hash, and offset under the
same install key. At open:

- anchor ahead of the file: `TRUNCATED` (records were removed);
- anchor whose line hash does not match that sequence: `BROKEN_CHAIN`;
- anchor behind the file: a crash after the append already hit disk; accepted.

Failure to advance the anchor does not fail an append that already reached
disk. An anchor behind the file is the crash-after-append shape.

A writing kernel appends `BOOT_VERIFIED` once the chain loads. A read-only
kernel (status, audit) verifies and does not append. A reader is not a second
writer.

## Fail closed

`verify()` walks from the start and stops at the first bad line. It yields
only records that passed. It does not skip the bad line, does not drop a tail,
and does not rewrite the file. `LedgerError.kind` is one of:

| Kind | Meaning |
|---|---|
| `TORN` | The line does not parse. Unreadable history is not empty history. |
| `BROKEN_CHAIN` | The line parses, but sequence, `prev_sha`, or payload bytes disagree. A well-formed lie is this kind. |
| `FORGED` | The line parses and chains, but the HMAC is not this service's. Same kind if the head anchor's HMAC fails. |
| `TRUNCATED` | The file is shorter than a verified offset, a fold checkpoint, or a head anchor. Absent after a non-zero verified length is the same refusal. |
| `UNREADABLE` | The file or the head anchor exists and cannot be read or parsed as an anchor. |
| `STALE_HEAD` | Append refused because the head moved while the caller was deciding. Nothing was written. |

Absent is not unreadable. A missing ledger file is an empty history (zero
events). A file that exists and cannot be read is `UNREADABLE`.

The ratified incident rule is refuse plus an incident, never repair-in-place.
The ledger module's job is the typed refusal. It does not heal, compact, or
re-sign a bad segment. Restoring service means returning to a copy that still
verifies, not editing the live segment. Visible refusal is the success case
for a corrupt chain.

There is no segment rotator in `cosmos_ledger.py`. One `Ledger` instance is
one JSONL file, and `seq` is the sequence inside that file. "Corrupt segment"
means that file (or its anchor) failed the walk. Multi-file segment rotation
is not what this module does.

## Projections

Anything a person or a panel reads as "current state" is a fold of verified
records. The fold is disposable.

- `project(fold, init)` replays every verified record. Spend totals are built
  this way: caps, reservations, and settlements are a fold, not a stored
  balance.
- `fold_cached(name, fold, init)` folds only the suffix since the last call
  for that name, still under chain and MAC checks, and returns a deep copy.
  Callers must not mutate the cache. A file shorter than the folded offset is
  `TRUNCATED`. Registry state, maker maps, sessions, and similar hot readers
  use this pattern.
- Registry files such as `registry/nodes.json` and `registry/rails.json` are
  written from the fold. They name their TTL and the rows that TTL dropped.
  Deleting them loses nothing the chain still holds.
- Recall (`cosmos/cosmos_recall.py`) is the service-private SQLite projection
  of conversation events. The database indexes `CONVO_OPENED` / `CONVO_TURN`
  from the signed chain. `rebuild()` deletes the index and folds from the
  start. A checkpoint past the end of the ledger is `TRUNCATED` on refresh
  and on search. The index never outlives the history it was built from.
  Search on a missing index is unmeasured; a read does not create the file.

SQLite elsewhere in the tree is not automatically a projection of
`authority.jsonl`. Read that module's own contract. Where a database is a
projection, the rule is the same: service-private, rebuildable, never
authority, never the thing another machine mounts as truth.

KDash and the other panels are clients of the versioned API. They show
projections. They do not hold the pen. A panel total that disagrees with a
fresh fold is discarded with the panel cache. It is not patched into the
chain.

Mount-visible copies are ingress, not authority. A sandbox write becomes real
only when the service checks bytes, hash, schema, and identity and then
appends. That check belongs to the caller (the kernel and the fenced commit
path), not to a silent assumption inside the ledger module.

## What not to do

- Do not open the JSONL in an editor and save it. A rewritten line breaks
  `prev_sha` or the HMAC. The next open refuses.
- Do not delete a tail to "undo" an event. With the head anchor on, that is
  `TRUNCATED`. Without it, a verified reader that already saw the longer file
  still refuses.
- Do not treat a SQLite row, a registry JSON file, or a panel as proof. Proof
  is a verified record.
- Do not log, document, or paste the install key. Do not put key material in
  an event payload.
- Do not add a second writer that appends without the ledger lock and the
  service MAC. Chain-safe serialization is the lock plus re-prime, not a
  convention.

## Still open

Single-writer fail-closed is the ratified shape. High availability and a
second unsynchronized writer are explicitly out of that decision and are not
solved here. Fail-closed means a bad segment stops the readers that verify it.
That refusal is correct. It is not a healer waiting to be written.

This page does not claim every screen, every SQLite file, or every JSON dump
in the tree is already a correct fold of `authority.jsonl`. Recall and the
registry projection are built that way. Other caches have to be checked
against their own module before anyone treats them as disposable. COSMOS is
still being built. The ledger is the authority those builds have to fold from,
not a certificate that the rest of the system is done.
