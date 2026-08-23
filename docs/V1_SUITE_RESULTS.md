# COSMOS v1.0-f5 - full native suite results - 2026-08-23

## test_browser.py (rc=0)
```
OK    detect_auth_wall: TRUE on a login-form DOM (form + password + login language)
  OK    detect_auth_wall: FALSE on a normal page (a bare search <form> is not a wall)
  OK    detect_auth_wall: FALSE on a 'Sign in' LINK with no <form> (link != wall)
  OK    detect_auth_wall: FALSE on empty DOM
  OK    detect_auth_wall: a <form> with a password input is decisive on its own
  OK    browser present: navigate(data: URL) returns non-empty DOM text containing the rendered marker
  OK    browser present: session_ok() is True (about:blank renders)
  OK    browser present: navigating a login-wall data: URL raises PermissionError (-> AUTH_REQUIRED)
SELFTEST PASS - 8 checks (browser: C:\Program Files\Google\Chrome\Application\chrome.exe)
```

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

## test_concurrency.py (rc=0)
```
OK    B1: 100 interleaved appends from TWO writers, zero errors
  OK    B1: the chain VERIFIES after the hammer (was: BROKEN_CHAIN, measured)
  OK    B1: seqs are 1..100 with no duplicates
  OK    B1: BOTH writers landed records (it was interleaved, not serialized-by-luck)
  OK    B1: read-only Kernel() appends NOTHING
  OK    B1: read-only kernel REFUSES protected writes
  OK    B2: EXACTLY ONE winner under overlap (was: double-claim, measured)
  OK    B2: the loser LOSES CLEANLY (LOST_CLAIM or empty queue, no exception leak)
  OK    B2: the sched chain VERIFIES after the race (was: BROKEN_CHAIN)
  OK    B2: exactly one JOB_CLAIMED in the ledger
  OK    B7: spend on an EXPIRED budget is DENIED and the call NEVER RAN (was: ALLOWED, measured)
  OK    B7: headroom subtracts reservations (the audit stops lying)
  OK    M2: re-install with a different tree_id REFUSES (was: silent restamp)
  OK    M2: install record exists and from_install_record() has a happy path
  OK    M2: from_install_record resolves the root
  OK    kernel COMPOSES registry/spend/validator itself
  OK    kernel session close over open watcher REFUSES (B5 composed)
SELFTEST PASS - 17 checks (every one reproduces a MEASURED critic finding)
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
  OK    wakeup FIRED on submission [os-file-watch, 0.605s latency]
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
  OK    expiry is a RECORDED event (EXPIRE precedes the takeover)
  OK    the grant AFTER an expiry is a TAKEOVER event (contract, not implementation)
  OK    the refusal is a RECORDED event, not console prose
  OK    release frees the resource
  OK    release with stale token is recorded, ignored, and harmless
  OK    token still monotonic after release (3 > 2)
  OK    commit after release of a DIFFERENT older lease -> works for current holder
  OK    commit on released lease -> NO_LEASE
  OK    replayed arbiter sees the live lease
  OK    replayed arbiter's NEXT token is higher (counter survives restart)
  OK    torn ledger -> TORN_LEDGER refusal (never reads as free)
SELFTEST PASS - 18 checks (5 refusals asserted BY KIND, 2 chains BY EVENT)
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

## test_migrate_health.py (rc=0)
```
OK    REAL incumbent registry ingested [MEASURED: 143 tools]
  OK    spike replacements pre-dispositioned REPLACED
  OK    UNDECIDED gap is COUNTED, not defaulted silently
  OK    nothing verified yet (registration is not capability)
  OK    re-ingest is idempotent (duplicates skipped, count stable)
  OK    board runs GREEN on a healthy kernel
  OK    THE PLANTED FAILURE IS RED (the board can see failure)
  OK    board run is ledgered
  OK    every row carries a detail
  OK    a RAISING row is a RED row, not a dead board
  OK    verdict counts the red
  OK    all-red-one-reason -> SHARED-CAUSE diagnosis (C-46)
SELFTEST PASS - 12 checks (the backlog is measured; the board can see failure)
```

## test_port_plan.py (rc=0)
```
OK    cosmos module discovery found the spike successors (paths/lock/mail)
  OK    plan is non-empty
  OK    every decision has a VALID disposition (four + UNDECIDED sentinel)
  OK    every decision has a successor OR a reason (never neither)
  OK    every decision carries a reason (the recorded why)
  OK    every REPLACED entry names a successor
  OK    every REPLACED successor contains at least one cosmos_ module token
  OK    every cosmos_ module named by a REPLACED successor EXISTS on disk
  OK    no successor (any disposition) names a non-existent cosmos_ module
  OK    no UNDECIDED is silent - each names its debt in the reason
  OK    summary().undecided matches the plan's UNDECIDED set
  OK    summary total == len(PORT_DECISIONS)
  OK    by_disposition sums to total (no tool uncounted, none double-counted)
  OK    apply() returned the same summary shape as summary()
  OK    required incumbents are all present in the plan
  OK    every planned tool was declared into the registry
  OK    every FOUR-disposition tool recorded that exact decision in the ledger
  OK    every UNDECIDED tool is declared but carries NO disposition event (the gap)
  OK    re-apply does not raise and returns identical counts
  OK    re-apply leaves the projected rulings unchanged (no drift on replay)
  OK    re-apply adds no new tools to the registry
PORT PLAN: 33 tools mapped | {'REPLACED': 23, 'ADAPTED': 10}
SELFTEST PASS - 21 checks (architecture wins where a contract conflicts; every decision recorded, never drifted)
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

## test_surfaces.py (rc=0)
```
OK    register three surfaces -> all in state
  OK    measure runs the probe and returns reachable + free_bytes
  OK    report shows a measured surface with age_s and free_gb
  OK    a never-measured surface shows reachable=None (UNKNOWN, never True)
  OK    duplicate id -> DUPLICATE
  OK    bad kind -> UNQUALIFIED
  OK    bad role -> UNQUALIFIED
  OK    measure unknown surface -> UNKNOWN_SURFACE
  OK    measure with no probe attached -> UNQUALIFIED
  OK    ...and the refused measure recorded nothing (itc still UNKNOWN)
  OK    LOCAL surface FAILS mesh-addressability (off-machine or it does not count)
  OK    small-capacity CLOUD surface FAILS capacity
  OK    never-measured surface FAILS reachability
  OK    reachable large-enough CLOUD surface QUALIFIES (no reasons)
  OK    stale measurement FAILS reachability (age advanced past the window)
SELFTEST PASS - 15 checks (surfaces measured not assumed; three questions each fail on their own axis; off-machine is structural)
```

## test_tls.py (rc=0)
```
OK    HTTPS: service serves https with a self-signed cert
  OK    HTTPS: a TLS client round-trips /status
  OK    HTTPS: cert + key were generated into config/
SELFTEST PASS - 3 checks (transport encryption or an honest http fallback)
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

## test_wave3.py (rc=0)
```
cker that found something is not broken)
  OK    M5: BROKE from rc=7
  OK    M5: LOG-FIRST - RUNNING + argv precede the output in the log
  OK    M5: attempt-private artifacts (log + result.json per attempt)
  OK    M5: `_`-prefixed script REFUSED as a job, recorded not silent
  OK    B6: signed arbiter grants and verifies its own history
  OK    B6: FORGED well-formed GRANT REFUSED on replay (was: loaded as live lease)
  OK    M4: commit with MATCHING input hashes lands
  OK    M4: commit with CHANGED input REFUSED (decision inputs are part of the fence)
  OK    M4: lease expiring DURING the callback -> COMMIT_UNFENCED incident, raised
  OK    M4: the unfenced commit is a LEDGERED incident
  OK    crucible packet completeness-asserted on disk read-back
  OK    crucible refuses an empty source
  OK    crucible refuses zero critics
  OK    crucible: returns LAND ON DISK before reasoning
  OK    crucible: a dead critic is a RECORDED FINDING (July forge lesson)
  OK    crucible merge: UNANIMOUS vs SINGLETON separated, disagreement visible
  OK    GET /health serves the board with its planted-red control
  OK    GET /spend serves the both-direction audit
  OK    GET /tools serves the contracts report
  OK    GET /events tails the ledger with a cursor
  OK    events cursor: nothing refetched past the head
  OK    POST /command: the voice/frontend seam answers over the wire
  OK    POST /command: destructive verb REFUSED over the wire
  OK    POST /crucible: remote crucible queues a job and ledgers the request
SELFTEST PASS - 31 checks (B3/B6/M4/M5 closed; crucible + remote live)
```

## test_wave4.py (rc=0)
```
OK    M6: DOM-first dispatch runs the DOM rail (was: DOM is just a sort key)
  OK    M6: RAIL_DISPATCH + RAIL_RESULT ledgered
  OK    M6: dead DOM session -> AUDITED fallback to API, never silent
  OK    M6: the fallback is a RECORDED event with its reason
  OK    M6: no MEASURED-live link -> NO_LIVE_LINK (registration is not capability)
  OK    MCP: initialize returns protocol + serverInfo
  OK    MCP: tools/list exposes the kernel verbs
  OK    MCP: tools/call cosmos_status delegates to the kernel
  OK    MCP: cosmos_submit creates a real job (client cannot reach around authority)
  OK    MCP: the submit is in the kernel's own job state
  OK    MCP: cosmos_command drives the voice/frontend seam
  OK    MCP: unknown tool -> JSON-RPC error, not a crash
  OK    MCP: torn request -> parse error (-32700), never a silent drop
  OK    MCP: a notification gets NO response line (protocol-correct)
  OK    SURFACES: a reachable off-machine LAN target with capacity QUALIFIES
  OK    SURFACES: a LOCAL surface FAILS off-machine (one copy on one machine is zero)
SELFTEST PASS - 16 checks (DOM is a rail; COSMOS speaks MCP; surfaces qualified)
```
