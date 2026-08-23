# F5 CORE BUILD - v1 first cut - 2026-08-23

Modules: cosmos_paths (resolver) - cosmos_ledger (hash-chained signed authority) -
cosmos_lock (lease/fencing arbiter) - cosmos_mail (N>2 IPC) - cosmos_sched
(priority scheduler on the ledger, measured interrupt wakeup) - cosmos_kernel
(composition root: install -> boot-verify -> fenced writes -> audit).

All five suites ran NATIVE on Windows before this commit; outputs below.

## test_cosmos_paths.py (rc=0)
```
OK    install A resolves
  OK    install B resolves at a NON-default root (settability)
  OK    two installs share no state
  OK    role API joins under the root
  OK    every declared role resolves
  OK    missing root -> NOT_FOUND
  OK    existing-but-empty dir -> IDENTITY_MISMATCH (the mesh() scar)
  OK    torn sentinel -> UNPARSEABLE (never read as free)
  OK    wrong system -> IDENTITY_MISMATCH
  OK    wrong tree_id -> IDENTITY_MISMATCH (a COSMOS root, not YOUR root)
  OK    root-is-a-file -> NOT_A_DIRECTORY
  OK    unknown role REFUSES (no plausible-path assembly)
  OK    install record absent -> NOT_FOUND refusal, no guessing
  OK    extended() never double-prefixes
  OK    MAX_PATH: >260-char path readable via extended() [NATIVE MEASURED, 682 chars]
  OK    walk() traverses past MAX_PATH
  OK    no import-time side effects (module has no resolved global root)
SELFTEST PASS - 17 checks (8 negative controls asserted BY KIND)
```

## test_cosmos_lock.py (rc=0)
```
OK    grant issues token 1
  OK    fenced commit under live token runs
  OK    renew extends expiry
  OK    second writer -> HELD
  OK    dying holder recovered by expiry, no cleanup discipline
  OK    fencing token is MONOTONIC across takeover
  OK    dead holder's late commit -> STALE_TOKEN, refused and ledgered
  OK    expiry is a RECORDED event (EXPIRE precedes the new GRANT)
  OK    the refusal is a RECORDED event, not console prose
  OK    release frees the resource
  OK    release with stale token is recorded, ignored, and harmless
  OK    token still monotonic after release (3 > 2)
  OK    commit after release of a DIFFERENT older lease -> works for current holder
  OK    commit on released lease -> NO_LEASE
  OK    replayed arbiter sees the live lease
  OK    replayed arbiter's NEXT token is higher (counter survives restart)
  OK    torn ledger -> TORN_LEDGER refusal (never reads as free)
SELFTEST PASS - 17 checks (5 refusals asserted BY KIND, 2 chains BY EVENT)
```

## test_cosmos_mail.py (rc=0)
```
OK    two senders -> two files, zero collisions (N>2 works)
  OK    messages carry sender identity + epoch + offset
  OK    sender sees NO receipt before ack
  OK    after ack, sender sees the receipt (received is a recorded fact)
  OK    acked message leaves unread; the other remains
  OK    probe LIVE (unread within window)
  OK    probe EMPTY (endpoint live, nothing unread)
  OK    probe MISSING for an unregistered worker (THE PHONE IS DEAD)
  OK    probe STALE (old unread = dead conversation, not a quiet one)
  OK    send to missing mailbox -> MAILBOX_MISSING, no silent create
  OK    self-send -> SELF_SEND (nobody talks to themselves)
  OK    half-written/tampered message -> TORN_MESSAGE by hash
SELFTEST PASS - 12 checks (4 probe states distinct, 3 refusals BY KIND)
```

## test_core.py (rc=0)
```
OK    5 appends verify as a chain
  OK    projection rebuilds state by replay
  OK    reload continues the chain (writer state survives restart)
  OK    torn line -> TORN
  OK    tampered payload -> BROKEN_CHAIN (bytes/hash disagree)
  OK    record signed with the WRONG KEY -> FORGED
  OK    silently dropped middle record -> BROKEN_CHAIN
  OK    priority admission: critical first, low last
  OK    bad priority REFUSES
  OK    claim takes the critical job
  OK    claimed job leaves the queue
  OK    FINDINGS is an outcome, not a failure
  OK    bare-rc outcome REFUSES (three words only)
  OK    done on a non-RUNNING job REFUSES
  OK    every job claimed EXACTLY once (ledger count = jobs)
  OK    claim on empty queue returns None (empty != error)
  OK    stale RUNNING is REPORTED (event), job NOT retried
  OK    stale is reported ONCE, not every tick
  OK    wakeup FIRED on submission [POLL-FALLBACK (watchdog absent - DEGRADED, recorded), 0.754s latency]
SELFTEST PASS - 19 checks (7 refusals BY KIND, 4 planted corruptions, 1 measured interrupt)
```

## test_kernel.py (rc=0)
```
OK    installer stands up a bootable root
  OK    kernel boots READY on a verified root
  OK    boot left a ledgered record
  OK    fenced write lands
  OK    write is ledgered with worker identity
  OK    submit->claim->done through the kernel
  OK    kernel mail send + peer unread
  OK    audit: ledger chain VERIFIED
  OK    audit: jobs projected by state
  OK    audit carries its measurement time
  OK    kernel on an uninstalled root REFUSES (typed)
  OK    second lease on held resource -> HELD
  OK    restarted kernel verifies the same chain and continues it
SELFTEST PASS - 13 checks
```
