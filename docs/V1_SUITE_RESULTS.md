# COSMOS v1.0-f5 - full native suite results - 2026-08-23

## test_command.py (rc=0)
```
OK    status: ok + READY + root identity
  OK    status: ledger head is present
  OK    audit (any case): chain VERIFIED
  OK    jobs: empty projection before any submit
  OK    help: teaches the submit grammar
  OK    submit high -> claimable job with the same id
  OK    claimed job carries the spoken command
  OK    bad priority -> BAD_ARGS that teaches the grammar
  OK    missing command -> BAD_ARGS
  OK    unknown verb -> UNKNOWN_COMMAND, never a guess
  OK    'delete everything' -> REFUSED (never-delete canon)
  OK    every FORBIDDEN verb refuses
  OK    refusal is ledgered as COMMAND_REFUSED
  OK    handled commands are ledgered with ok flags
SELFTEST PASS - 14 checks
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
  OK    wakeup FIRED on submission [os-file-watch, 0.606s latency]
SELFTEST PASS - 19 checks (7 refusals BY KIND, 4 planted corruptions, 1 measured interrupt)
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

## test_features.py (rc=0)
```
gainst its declaration
  OK    wrong declared length -> SHORT_READ (the mount's signature)
  OK    wrong declared sha -> HASH_MISMATCH
  OK    path_exists PASSES for a file that is on disk
  OK    path_exists on a missing file REFUSES the whole return
  OK    ...and the refusal is LEDGERED (RETURN_REFUSED event present)
  OK    doi_shape passes a real-shaped DOI, detail says UNPROVEN (shape is not existence - Crossref is the authority)
  OK    doi_shape FAILS 'not-a-doi' (shape failure is a certain fabrication signal)
  OK    quote_in_source: an exact quotation is found verbatim
  OK    quote_in_source: a FABRICATED quotation is refused (S-55 control)
  OK    unknown validator name -> NO_VALIDATOR (never silently skipped)
  OK    OK path: evidence file written and holds the page text
  OK    OK path ledgers DOM_ATTEMPT_OK
  OK    driver raising on start -> UNREACHABLE, and it is ledgered
  OK    stale session with require_session -> SESSION_EXPIRED, ledgered
  OK    navigate raising PermissionError -> AUTH_REQUIRED, ledgered
  OK    navigate raising mid-action -> BROKE (report-never-retry), ledgered
  OK    every attempt used a DIFFERENT profile dir (ephemeral per attempt)
  OK    federation_ready() is False - never reported working while blockers stand
  OK    federation blockers == 5, counted FROM THE FUNCTION, not from prose
  OK    MESH_ID is KMesh
  OK    no peer ID starts with G (GMesh UNASSIGNED - Keith assigns, nobody guesses)
SELFTEST PASS - 28 checks (platform owns the shell; validation is a gate; DOM failures are typed and ledgered; identity is asked, not quoted)
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

## test_spend_context.py (rc=0)
```
OK    reserve -> call -> settle at MEASURED (not worst case)
  OK    over-cap call DENIED
  OK    ...and the call NEVER RAN (denial precedes spend - the whole point)
  OK    unbudgeted rail -> UNKNOWN_RAIL
  OK    unpriced call counted as UNPRICED, settled unchanged
  OK    a raising call releases its reservation
  OK    expiring unspent credit -> EXPIRY RISK flagged (S-102: we governed the wrong direction)
  OK    every audit number carries measured_at
  OK    close with an open watcher REFUSES (S-121 made structural)
  OK    forced close records OPEN_CONTEXT incident
  OK    next boot INHERITS the facts
  OK    next boot SEES the unresolved watcher as an incident
  OK    clean close after resolution needs no force
  OK    resolved incident clears from inheritance
  OK    double close REFUSES
SELFTEST PASS - 15 checks (breaker denies BEFORE the call; carry-over is a mechanism)
```

## test_tools.py (rc=0)
```
OK    declare -> attach -> verify passes and returns detail
  OK    passing check ledgered as TOOL_CONTRACT_OK
  OK    report shows AGE on the verified tool (dated, not just true)
  OK    never-verified tool reports verified=None - UNKNOWN, never True
  OK    duplicate declare REFUSES - a second declaration is a drift
  OK    disposition on unknown tool -> UNKNOWN_TOOL
  OK    bad decision -> BAD_DISPOSITION
  OK    no check attached -> CONTRACT_FAIL (an unverifiable contract is a claim)
  OK    ...and the refusal ledgered NOTHING - nothing was measured
  OK    failing check -> CONTRACT_FAIL raised
  OK    ...and the failure LANDED IN THE LEDGER, not just the exception
  OK    failed tool reports verified=False, dated
  OK    disposition ADAPTED with reason lands in state, dated
  OK    disposition surfaces in report
  OK    verify_all never raises and covers every declared tool
  OK    verify_all: the passing tool still passes
  OK    verify_all: the failing and the unverifiable both recorded ok=False
  OK    verify_all ledgered the no-check refusal per-tool (UNVERIFIABLE)
SELFTEST PASS - 18 checks (registration is not capability; only a dated passing check is)
```

## test_v1.py (rc=0)
```
OK    never-probed link is UNKNOWN (None), not verified
  OK    probed matrix shows verified WITH age
  OK    DOM-first routing picks the DOM link
  OK    dead DOM link drops from routing; API remains (explicit fallback)
  OK    unknown link probe -> UNKNOWN_LINK
  OK    probeless link -> NO_PROBE (recorded, not skipped)
  OK    bad rail type REFUSES
  OK    backup hash-verified per file
  OK    RESTORE REHEARSAL runs and passes
  OK    rehearsal is a LEDGERED event
  OK    tampered backup -> REHEARSAL_FAILED (verification is real)
  OK    empty scope -> EMPTY_SCOPE (no green log over nothing)
  OK    no token -> 401 (auth exists day one, invisible in use)
  OK    GET /status: ready over the wire
  OK    GET /rails: matrix served with ages
  OK    POST /jobs -> claim -> done, end to end over HTTP
  OK    GET /audit answers with measured_at + verified chain
  OK    every response carries served_at (panel age exists)
SELFTEST PASS - 18 checks (v1 integration: registry, backup+rehearse, live API)
```
