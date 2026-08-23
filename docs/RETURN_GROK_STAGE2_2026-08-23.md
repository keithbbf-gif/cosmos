# COSMOS STAGE 2 — GROK RETURN
**2026-08-23 · vendor: Grok · consumer: COSMOS builders and the four-family compare**

Method: scars/corrections as quoted in the packet first, attached source second, docstrings never as evidence. Files named in the characterization but not attached (scar record, corrections.toml, bts_health.py, bts_board.py, scheduled-task XML, FUSE driver identity) are **NOT IN PACKET** — I do not assume their contents. The 154/61 counts are therefore unverified.

---

## A. FINDINGS (JSON)

```json
[
  {
    "id": "grok-01",
    "topic": "bts_paths CLI advertised flags are no-ops",
    "verdict": "MISSED BY CHARACTERIZATION. --check and --selftest are in the allowlist and then ignored. The process always prints the same report and exits 0. A spec-port that copies the CLI will ship a resolver whose 'selftest' certifies nothing.",
    "evidence": "bts_paths.py __main__: _bad filters argv to allow --check/--selftest; no branch reads those flags; sys.exit(0) is unconditional. Packet INPUT A §1 claims only 'CLI refuses unknown flags (exit 2)'.",
    "confidence": "high"
  },
  {
    "id": "grok-02",
    "topic": "bts_paths CLI report omits the shared surface it exists to protect",
    "verdict": "MISSED. The report prints ai/mesh/archive/working/secrets and one key file. It does not print AIROOT, AIHOW, airoot(), queue(), board(), or rold(). The 2026-08-16 coordination break was exactly a missing shared surface. The diagnostic that every other tool depends on cannot see that surface.",
    "evidence": "bts_paths.py __main__ loop over (ai, mesh, archive, working, secrets) only. AIROOT/AIHOW are computed at import and never printed. Packet INPUT A §1 lists those roles as the API but not as CLI coverage.",
    "confidence": "high"
  },
  {
    "id": "grok-03",
    "topic": "sandbox glob is lex-first, not current-session, and does not refuse multi-hit",
    "verdict": "MISSED, and it is a silent fallback. sorted(glob.glob(pat))[0] picks the lexicographically smallest session mount. Two live mounts (current + leftover) resolve to whichever name sorts first. That is a stale-tree fallback wearing a glob.",
    "evidence": "bts_paths.py _resolve/_resolve_ai nix branch: hits = sorted(glob.glob(pat)); return hits[0]. Packet INPUT A §1 says 'GLOBS because the session name changes' and 'NO FALLBACK IS THE LOAD-BEARING FEATURE'. The code has a fallback the moment hits > 1. Whether two mounts coexist on this host is NOT IN PACKET.",
    "confidence": "high"
  },
  {
    "id": "grok-04",
    "topic": "existence is still the only identity check",
    "verdict": "CODE DOES NOT IMPLEMENT the sentinel the characterization now requires. Every resolve and the CLI 'OK' column are os.path.isdir/isfile. mesh() was pointed at the live tree; the class of bug (wrong dir that exists) is unclosed. A spec-driven port of the attached source silently loses the spike acceptance.",
    "evidence": "bts_paths.py _resolve/_resolve_ai/__main__; mesh() is only os.path.join(AIROOT,'BTS_MESH',*parts). Packet INPUT A §1 scar of 2026-08-21 and SPIKE ACCEPTANCE 'sentinel-content check' are prescriptions, not observed behavior.",
    "confidence": "high"
  },
  {
    "id": "grok-05",
    "topic": "characterization of env-last is supported; env-first would be a regression",
    "verdict": "SUPPORTED. BTS_RESEARCH_ROOT / BTS_AI_ROOT are consulted only after the compiled ladder misses. An override cannot shadow a healthy V: tree. COSMOS portability to a peer box is this same clause (env when the letter is absent), not a new first-priority override. Families that put COSMOS_ROOT first will re-enable shadowing.",
    "evidence": "bts_paths.py _resolve and _resolve_ai: env block sits after the platform loop, gated on isdir. Packet INPUT A §1. INPUT B.3 names the peer-cold-machine case.",
    "confidence": "high"
  },
  {
    "id": "grok-06",
    "topic": "tree_lock still parent-walks ROLD; characterization claims it does not",
    "verdict": "WRONG in the characterization. LOCK uses bts_paths.queue(). WATCHED still uses ROLD = MESH.parent / 'ROLD' and MESH = Path(__file__).resolve().parent. The defect class the packet says is 'in residence' is also still the live code. 'ROLD now resolves via bts_paths.rold()' is unsupported by the attached source.",
    "evidence": "tree_lock.py lines MESH/ROLD/WATCHED vs LOCK = Path(bts_paths.queue(...)). Packet INPUT A §2: 'this file computes ROLD = MESH.parent / \"ROLD\"' AND 'ROLD now resolves via bts_paths.rold()'. Those two sentences cannot both describe this file. Only the first matches the source. bts_paths.rold() exists and is unused here.",
    "confidence": "high"
  },
  {
    "id": "grok-07",
    "topic": "tree_lock _sha collapses absent with unreadable; verify then labels a deletion as mount-lie",
    "verdict": "CROSS-CUTTING CLAIM IS FALSE FOR THIS MODULE. Packet §CROSS-CUTTING.4 says absent ≠ unreadable ≠ changed ≠ empty. _sha() excepts everything to None. verify() treats (was-hash, now-None) as 'UNREADABLE now (was readable at claim)' / 'mount's signature'. A deleted watched file and a FUSE read failure are the same state. A file that was None at claim and later readable is not reported at all.",
    "evidence": "tree_lock.py _sha try/except return None; verify() loop over then.items() only. Packet INPUT A §2 claims '_sha() returns None for unreadable-vs-absent and DOES NOT treat either as changed' — true, and that is the collapse, not a solution.",
    "confidence": "high"
  },
  {
    "id": "grok-08",
    "topic": "manifest keys are absolute path strings from the claimer's universe",
    "verdict": "MISSED. manifest() keys are str(p) for Path objects built from __file__ and MESH.parent. A claim on native Windows and a --verify from the Linux sandbox cannot share keys. Cross-universe verify reports every file unreadable (now.get(win_path) is None). The mechanism built to separate 'changed under me' from 'the mount lied' is blind across the two universes that made the lock necessary.",
    "evidence": "tree_lock.py manifest() / verify() then.items() / now.get(p). Packet INPUT A §2 'HASH MANIFEST' and the 2026-08-16 two-universes scar. No normalization, no role-relative keys.",
    "confidence": "high"
  },
  {
    "id": "grok-09",
    "topic": "tree_lock and bts_phone still emit naive local timestamps",
    "verdict": "MISSED, and it is the same scar the runner already paid for. _now() is datetime.now() with no tz. claim['claimed'] is naive isoformat. age_minutes compares naive-to-naive in-process (OK) but any out-of-process reader on UTC repeats the five-hour-dead false report. phone check() prints fromtimestamp without tz. COSMOS 'timezone-aware timestamps' is not a port of these two files; it is a rewrite the characterization only stated for the runner.",
    "evidence": "tree_lock.py _now/claim/age_minutes; bts_phone.py check() datetime.fromtimestamp(st.st_mtime).isoformat. Packet INPUT A §4 heartbeat scar of 2026-08-22. Packet CROSS-CUTTING.6 'timestamp with offset' is not what lock or phone write.",
    "confidence": "high"
  },
  {
    "id": "grok-10",
    "topic": "same-writer re-claim launders the manifest and resets the clock",
    "verdict": "MISSED AS A HAZARD. claim() refuses only when writer differs AND the claim is fresh. The same writer may re-claim; _write replaces the whole record including manifest. Edits to watched files followed by a re-claim become the new baseline. Selftest treats this as a required property ('the same writer may re-claim'). A spec-port that keeps the selftest keeps the laundering.",
    "evidence": "tree_lock.py claim(): if d and d.get('writer') != writer and age <= STALE. selftest() asserts same-writer re-claim == 0. Packet INPUT A §2 lists that selftest line as a negative control; it is a positive grant.",
    "confidence": "high"
  },
  {
    "id": "grok-11",
    "topic": "lock write can create the torn state that then wedges every operation",
    "verdict": "MISSED. Torn-file refusal is real and correct. _write() is open(LOCK,'w') + json.dump with no temp/rename and no fsync. A crash mid-write produces the unparseable file. After that, status/claim/verify/release all raise. There is no recovery path in the tool. Refuse-as-not-free plus a non-atomic writer is a self-deadlock the first time a session dies during _write.",
    "evidence": "tree_lock.py _write / _read. Packet INPUT A §2 'A TORN LOCK FILE REFUSES' and the 08-22 session-died-without-release scar. Packet CROSS-CUTTING.7 'Appends over atomic renames on anything a sandbox might touch' — this write is neither.",
    "confidence": "high"
  },
  {
    "id": "grok-12",
    "topic": "claim() is last-writer-wins on the one file Keith banned",
    "verdict": "THE INCUMBENT SHAPE CANNOT BE ENFORCED BY PORTING IT. _read then _write is TOCTOU. Two claimers who both see free/stale both write. open(...,'w') is not O_EXCL. Selftest is single-threaded and cannot see this. Concurrent lanes make this the production path.",
    "evidence": "tree_lock.py claim()/_write. Packet INPUT A §2 'COOPERATIVE → LOAD-BEARING' and INPUT B.1. Packet CROSS-CUTTING no-last-writer-wins is a COSMOS requirement, not incumbent behavior.",
    "confidence": "high"
  },
  {
    "id": "grok-13",
    "topic": "unparseable claimed timestamp fail-opens as stale",
    "verdict": "PARTIAL TORN-STATE. A parseable JSON object with a bad 'claimed' field yields age 1e9, so claim() takes over. Torn file refuses; torn field grants. Inconsistent with CROSS-CUTTING.5.",
    "evidence": "tree_lock.py age_minutes except return 1e9; claim() stale branch. Packet INPUT A §2 and CROSS-CUTTING.5.",
    "confidence": "high"
  },
  {
    "id": "grok-14",
    "topic": "bts_phone is probe-and-read only; there is no send",
    "verdict": "MISSED. The contract in comments says CoW writes OUTBOX. The module never writes a letter. Agents write the file by hand. A spec-port of the module produces a dead send path unless that convention is written down elsewhere (NOT IN PACKET).",
    "evidence": "bts_phone.py functions: check, read, selftest. No write/send. Packet INPUT A §3 'CoW writes airoot(...)'.",
    "confidence": "high"
  },
  {
    "id": "grok-15",
    "topic": "phone: empty file is live; undecodable letter is success",
    "verdict": "missing≠empty is only implemented as isfile vs not. rc=0 for a 0-byte inbound. read() uses errors='replace' and returns 0. A torn/undecodable letter is printed as a successful read. Four-state collapse on the read path.",
    "evidence": "bts_phone.py check() ok = os.path.isfile(INBOX); read() open(..., errors='replace'). Packet INPUT A §3 'missing ≠ empty' and CROSS-CUTTING.4/.5.",
    "confidence": "high"
  },
  {
    "id": "grok-16",
    "topic": "dead-phone text instructs a human fallback to the Research4 mirror",
    "verdict": "A SOCIAL FALLBACK. The code does not read the mirror (correct). The printed recovery path names the old surface. A spec-port that 'helpfully' automates that sentence reopens the 2026-08-16 wrong-surface bug. COSMOS with one root must not carry this instruction.",
    "evidence": "bts_phone.py check() else-branch: 'Check the Research4 mirror before concluding silence' + join(MIRROR_DIR, 'QA_ENGINEER_TO_COW.md'). Packet INPUT A §3 and CROSS-CUTTING.1.",
    "confidence": "high"
  },
  {
    "id": "grok-17",
    "topic": "one --once drains every pending job; heartbeat is written once at the start",
    "verdict": "CHARACTERIZATION UNDERSTATES THE SHAPE. 'One job at a time per lane' is sequential execution, not one job per tick. tick() snapshots all pending runnables and runs them all. beat() is called once, before the loop. A 60-minute job makes runner_heartbeat.json older than the 180s liveness window while the runner is alive. --lanes will declare that worker DEAD. --once itself is almost a no-op: it only suppresses the idle 'nothing queued' line. Bare invocation and --once share the drain-all path.",
    "evidence": "bts_runner.py tick() for-job-in-jobs; beat() before the loop; main() always calls tick() unless --status/--selftest/--lanes; --once only gates the n==0 print. Packet INPUT A §4 'one job at a time' / 'Heartbeat on EVERY tick'. Packet INPUT B.2.",
    "confidence": "high"
  },
  {
    "id": "grok-18",
    "topic": "selftest is not isolated and will execute production jobs",
    "verdict": "MISSED AND DANGEROUS. selftest() plants files in the live PENDING of the current QUEUE_ROOT, then calls tick(), which claims every runnable non-helper already sitting there. --selftest --lane lg does this to a real lane. The runner that exists to make failures visible can fire live work as a side effect of a test.",
    "evidence": "bts_runner.py selftest() writes into PENDING then tick(quiet=True); main() set_lane() before selftest. Packet INPUT A §4 selftest description lists plants, not isolation. CROSS-CUTTING.3 wants negative controls; this one is live-fire.",
    "confidence": "high"
  },
  {
    "id": "grok-19",
    "topic": "--status cannot see FINDINGS jobs",
    "verdict": "MISSED. status() lists files in done\\, not done\\findings\\. A PLM-44 job that did its job vanishes from the status board. The third outcome the runner was rebuilt to preserve is invisible to its own status.",
    "evidence": "bts_runner.py status() for label,d in queued/running/done/failed; items = d.glob('*') files only. FINDINGS = done/findings. Packet INPUT A §4 PLM-44 three outcomes.",
    "confidence": "high"
  },
  {
    "id": "grok-20",
    "topic": "QUEUE_BASE literal is not judged-benign; Linux launch writes the wrong universe before any job",
    "verdict": "WRONG in the characterization / audit note. On POSIX, Path(r'V:\\Ai\\_queue') is a relative name containing backslashes. _dirs() and beat() run before _cmd_for. A Linux launch mkdir's junk, writes a heartbeat, and if the queue is empty returns 0. 'py does not exist so a wrong-platform launch dies at the first job' is false for the idle path — the same successful-write-to-the-wrong-place that made tree_lock theater.",
    "evidence": "bts_runner.py QUEUE_BASE, _dirs, beat, tick early return when no jobs, main() return 0. Packet INPUT A §4 'JUDGED-BENIGN literal' and the 2026-08-16 two-universes incident in §1–§3.",
    "confidence": "high"
  },
  {
    "id": "grok-21",
    "topic": "losing the claim-rename raises and kills the tick",
    "verdict": "MISSED. job.rename(dst) is uncaught. Two overlapping --once on the same job: winner claims, loser FileNotFoundError, tick() dies mid-loop after any earlier jobs in that drain already ran. 'Two overlapping ticks cannot both take a job' is true. The losing tick does not skip; it crashes. Ledger/heartbeat completeness is then luck.",
    "evidence": "bts_runner.py _claim / tick() for-loop. Packet INPUT A §4 claim-by-rename. Overlap policy of the Windows scheduled task is NOT IN PACKET.",
    "confidence": "high"
  },
  {
    "id": "grok-22",
    "topic": "a legal long job is reported STALE while it is running",
    "verdict": "MISSED. STALE_RUNNING_SECS is 7200. __tNNNN caps at 21600. report_stale() uses mtime in running\\, which is the claim time. A job with __t10800 is announced STALE at the next tick's start (or, if drain-all, not until the next process — see grok-17). Re-run is correctly withheld. The word STALE still lands on work that is within its declared ceiling.",
    "evidence": "bts_runner.py _timeout_for cap 21600; STALE_RUNNING_SECS = 7200; report_stale. Packet INPUT A §4 'Stale jobs (>2 h in running\\) are REPORTED, never retried'.",
    "confidence": "high"
  },
  {
    "id": "grok-23",
    "topic": "CROSS-CUTTING.6 'every artifact carries who wrote it' is not incumbent behavior",
    "verdict": "UNSUPPORTED as a description of these four files. tree_lock: writer + naive time, no lane, no host. phone letters: identity is the filename pair, no header. runner ledger: epoch + job name, no worker/pid/host. runner heartbeat: lane + tz-aware times, no worker identity (one process per lane today). A port that assumes this property is already in the artifacts will not add it.",
    "evidence": "tree_lock.py _write payload; bts_phone.py file names; bts_runner.py _append rec and beat() rec. Packet CROSS-CUTTING.6 vs attached source.",
    "confidence": "high"
  },
  {
    "id": "grok-24",
    "topic": "runner never calls tree_lock; the 'must claim' rule lives in a comment",
    "verdict": "A SPEC-PORT OF THE CODE DROPS THE COUPLING THE CHARACTERIZATION TREATS AS LOAD-BEARING. Packet §4 says any lane that writes the live tree must claim the lock. No import, no subprocess, no claim. The two spikes are 'one design decision in two files' only in prose.",
    "evidence": "bts_runner.py has no tree_lock symbol. Packet INPUT A §4 standing conditions and INPUT B.1–B.2.",
    "confidence": "high"
  },
  {
    "id": "grok-25",
    "topic": "implicit priority is lexicographic filename order",
    "verdict": "MISSED. jobs = sorted(...). There is already a priority field: the name. aaa.py runs before zzz.py. COSMOS adding __pNN__ without deleting this tie-break will surprise anyone who thought the queue was FIFO-by-mtime (it is not FIFO either).",
    "evidence": "bts_runner.py tick() jobs = sorted([...]). Packet INPUT B.2 'no priority field'.",
    "confidence": "high"
  },
  {
    "id": "grok-26",
    "topic": "rc=2 means three different things across the four modules",
    "verdict": "PORT HAZARD NOT COVERED BY B.1–B.4. paths/lock/phone: unknown flag → 2. lock status: stale → 2; unknown writer → 2. runner jobs: FINDINGS → 2. runner --lanes: problems → 2. runner --lane bad name → 3. A wrapper that treats 2 as 'FINDINGS, not broken' (PLM-44) will treat a typo as findings. A wrapper that treats 2 as refuse will file a correct checker as a flag error.",
    "evidence": "bts_paths.py exit 2; tree_lock.py claim unknown=2, status stale=2; bts_phone.py unknown=2; bts_runner.py RC_FINDINGS=2, lanes_status returns that, main lane-name return 3. Packet INPUT A §4 PLM-44 and CROSS-CUTTING.2.",
    "confidence": "high"
  },
  {
    "id": "grok-27",
    "topic": "ENFORCING LOCK design",
    "verdict": "Do not use OS-level file locks as the cross-universe mechanism. Do not use a lease file that both universes write. Use a native-only arbiter (cosmos_lockd) plus request-by-rename plus a single lease with a monotonic fence, role-relative manifest keys, blank-not-unlink, expiry-by-epoch. See prose B.1.",
    "evidence": "2026-08-16 two-universes incident (packet §1–§2): LockFileEx/flock are per-universe (exact FUSE driver NOT IN PACKET; the incident already proved OS identity is not shared). Packet INPUT B.1 constraints: dead session, FUSE unlink refusal, native+sandbox writers.",
    "confidence": "high"
  },
  {
    "id": "grok-28",
    "topic": "SCHEDULER design",
    "verdict": "Minimal COSMOS scheduler: one job per worker cycle (not drain-all), claim-by-rename with FileNotFoundError=lost-race, priority in the filename, per-worker ledger and heartbeat (glob-discoverable), beat during the job, three worded outcomes, log-first, report-never-retry, helper prefix enforced in-runner, isolated selftest, resolve QUEUE via the one-root resolver. Concurrency is process count, not a shared mutable file. See prose B.2.",
    "evidence": "Packet INPUT B.2 required properties + grok-17/18/19/20/21/24/25. Incumbent proven properties are in bts_runner.py tick/_claim/_append/_is_helper and the three dest dirs.",
    "confidence": "high"
  },
  {
    "id": "grok-29",
    "topic": "RESOLVER design",
    "verdict": "Keep import-time resolve-or-raise and env-LAST. One compiled default per platform. Multi-glob-hit must raise. Sentinel file with exact role bytes on every resolved dir. Return Windows paths as \\\\?\\-prefixed for walks. Never walk from __file__. secrets remains a sibling of the published subtree, not of 'mesh'. --check must assert sentinels; --selftest must be a real negative control. See prose B.3.",
    "evidence": "Packet INPUT B.3; bts_paths.py observed behavior grok-01..05; 2026-08-21 mesh-empty-dir scar; C-60 MAX_PATH as quoted in packet §1 (the C-60 record itself is NOT IN PACKET).",
    "confidence": "high"
  },
  {
    "id": "grok-30",
    "topic": "MAILBOX design",
    "verdict": "Directory existence is the channel; files are messages; one writer per file via unique names; never two writers to one outbox. Probe: missing dir = dead, empty dir = no news, oldest/newest mtime+size printed, stale open question → rc FINDINGS not DEAD. No send-by-overwrite. No mirror fallback. See prose B.4.",
    "evidence": "Packet INPUT B.4; bts_phone.py grok-14/15/16; 2026-08-16 wrong-surface scar; 2026-08-23 inbound-present-but-stale observation in packet §3.",
    "confidence": "high"
  },
  {
    "id": "grok-31",
    "topic": "no \\\\?\\ prefix in any of the four modules",
    "verdict": "C-60 is quoted as a standing scar. None of the attached sources prefix walks. COSMOS paths are stated to be longer than BTS paths. A faithful port inherits WinError 3 on first deep walk and will call it 'not found'.",
    "evidence": "grep-equivalent read of all four attached files: no \\\\?\\ string. Packet INPUT A §1 MAX_PATH / C-60. The C-60 write-up is NOT IN PACKET.",
    "confidence": "high"
  },
  {
    "id": "grok-32",
    "topic": "INPUT C behavioral cards",
    "verdict": "SKIP. No SOURCE APPENDIX files beyond the four deep modules are in this packet. I will not invent cards for the 'other 135'.",
    "evidence": "Packet INPUT C: 'If none included: skip, do not invent.' Packet characterization closing: cards deferred to fan-out.",
    "confidence": "high"
  }
]
```

---

## B. PROSE REASONING

### B.0 Stance

I am not merging toward the characterization. It is a strong narrative document that is more accurate than the docstrings it refuses to trust, and it still has four failure modes I will not paper over:

1. It sometimes describes the spike *acceptance* as if it were *observed behavior* (sentinels, enforcement, per-worker identity, timezone-aware lock/phone stamps).
2. It contains at least one sentence that the attached source falsifies (`ROLD now resolves via bts_paths.rold()` inside `tree_lock.py`).
3. It repeats CROSS-CUTTING rules (four-state, who-wrote-it, append-over-rename) that these four files do not all keep.
4. It under-reports live-fire shapes in the runner (drain-all, unisolated selftest, Linux idle-path write, status-blind FINDINGS).

Docstrings in the attached files were used only as claims to doubt. Every verdict above is pinned to a code path or to an explicit gap.

---

### B.1 INPUT A — critique and extend

#### What the code does that the characterization missed

**`bts_paths.py`**
- `--check` / `--selftest` are accepted and do nothing (grok-01).
- The human report cannot see AIROOT/queue/board/rold (grok-02).
- Unknown *positionals* are swallowed (`python bts_paths.py typo` exits 0). Only tokens starting with `-` are refused.
- Nix resolution is lex-first multi-hit (grok-03). That is a fallback.
- `ai()` is `ROOT/Ai`. `airoot()` is `AIROOT`. The names collide. The 08-16/08-21 bugs are this collision in costume. Characterization lists the role split as history; it does not name the API trap.

**`tree_lock.py`**
- Parent-walk still feeds WATCHED (grok-06). If COSMOS moves the package to `V:\A\Ai\COSMOS`, `MESH.parent/"ROLD"` becomes `V:\A\Ai\ROLD`, not `V:\A\Ai\COSMOS\ROLD`. Today's layout makes the walk accidentally equal `bts_paths.rold()`. The port is where the landmine detonates.
- Manifest keys are not portable across universes (grok-08).
- `_sha` / `verify` collapse four states into two (grok-07).
- Same-writer re-claim launders fingerprints (grok-10).
- `_write` can *create* the torn file that then refuses forever (grok-11).
- `age_minutes` fail-opens on a bad timestamp field (grok-13).
- `--claim` / `--release` with a missing operand raise IndexError. Not a refuse.
- Default CLI is `--status`. Exit codes: free=0, held=1, stale=2. Unknown writer on `--claim` is also 2. Stale-held and unknown-writer are indistinguishable to a wrapper.

**`bts_phone.py`**
- No send (grok-14). This is a probe tool. The mailbox is a pair of filenames plus social convention.
- Identity is CoW-hardcoded. GbQA running the same file would read their own outbox's counterpart only if they ignore OUTBOX and treat INBOX as theirs — there is no `--as`. N=2 is baked into constants, not a parameter.
- `--check` (also the default) probes inbound existence only. It does not prove the outbound is on the surface the other party reads. The scar was "I sent it" ≠ "they received it". The probe still only checks one of those claims.
- Staleness is printed (mtime, size) and not alarmed — characterization got this. It did not note the naive timestamp (grok-09) or that a 0-byte file is "PRESENT" / rc=0 (grok-15).
- Selftest does not plant an empty letter. missing≠empty is untested in the direction that would prove empty is live.

**`bts_runner.py`**
- Drain-all + heartbeat-at-start (grok-17). This is the largest behavioral miss in the packet. Combined with a scheduled task that (UNKNOWN — NOT IN PACKET) likely uses "do not start a new instance", a long job freezes the heartbeat for the whole drain. `--lanes` then lies: DEAD over a living worker. That is the "checker that cannot go red" class inverted — a checker that cannot stay green.
- `--once` does not mean one job and barely means one tick. It means "do not print 'nothing queued'".
- Bare `python bts_runner.py` is live fire.
- Selftest is live fire against the real queue (grok-18).
- `--status` hides `done\findings\` (grok-19).
- Losing rename crashes the tick (grok-21).
- `__t` above 7200 s is STALE-by-policy while still legal (grok-22).
- Filename sort is a hidden priority (grok-25).
- `main()` after `tick()` returns 0 even when every job BROKE. The runner process is fail-open. Outcomes live in logs/ledger only. Characterization never says this.
- Heartbeat is `write_text` replace, no fsync. A torn heartbeat still has an mtime, so `--lanes` (mtime-based) reports ok while a JSON reader raises. Liveness and content can disagree.
- `cwd=QUEUE_ROOT` for every job. A job with a relative write can trash the inbox. Helper-prefix exists because this cwd was how `_tidyup2_checks.py` got claimed; the same cwd remains.
- `_cmd_for` hard-codes `py -3.14`. A port that changes the interpreter without changing this one function silently fails every `.py` job. One predicate is good; one hardcoded launcher version is a new landmine.
- `set_lane` rebinds module globals. The moment concurrency is in-process threads, this is a race. Characterization wants concurrency as a property; this implementation of lanes cannot host it inside one interpreter.

#### What in the characterization is wrong or unsupported

| Claim | Verdict |
|---|---|
| `ROLD now resolves via bts_paths.rold()` in tree_lock | **False** for the attached file (grok-06). |
| QUEUE_BASE literal is judged-benign because `py` dies off Windows | **False** on the idle path (grok-20). |
| CROSS-CUTTING.4 four-state never collapsed | **False** in `_sha`/`verify` and phone `read`/`isfile` (grok-07, grok-15). |
| CROSS-CUTTING.6 every artifact carries who / offset | **False** as a description of these four (grok-23). |
| CROSS-CUTTING.7 appends over renames on sandbox-touched state | **False** for `tree_lock._write` and heartbeat replace (grok-11). |
| "one job at a time per lane" without drain-all | **Incomplete** to the point of misleading (grok-17). |
| Sentinel / enforcement / per-worker identity as incumbent | Those are spike *requirements*. The source does not do them. |
| 154 scars / 61 corrections / C-60 body / scheduled-task settings | **NOT IN PACKET.** I treat the quoted incidents that appear in the attached comments as claims supported by those comments, not as independently counted records. |

What the characterization got right, and I will not pretend otherwise: import-time dual-root fail-loud; env-last; D:\Research3 exclusion; secrets-by-location; unknown-flag refuse on the three argparse-less CLIs; torn-JSON refuse on the lock; stale takeover with announcement; closed `KNOWN_WRITERS`; release-verifies-then-blanks; claim-by-rename; command-from-claimed-path; three worded outcomes; log-first; report-never-retry; helper prefix enforced in-runner; UTF-8 both ends of the pipe; append+fsync ledger; lane heartbeats globbed at the base; `--lanes` discovers a directory with no heartbeat. Those are in the source.

#### Undocumented behavior a spec-driven port would silently lose — per module

**bts_paths.** Lose (because they are not in a spec drawn from "what the docstring says" or even from the characterization's acceptance list as *code*): env-last shadowing rule; lex-first glob (better to lose this — refuse instead); CLI no-op flags (better to lose); CLI blindness to AIROOT; `ai` vs `airoot` naming; import as machine assertion; `p()` as the generic join under ROOT; secrets as sibling of `ROOT/Ai`, not as a blocklist. A spec that only says "role-based resolver, one root" will drop the sibling-not-child publish property unless that sentence is copied.

**tree_lock.** Lose: blank-on-unlink-refusal (FUSE); verify-before-release and rc=1 from `--release` even when the file is gone (08-22 workflow scar — wrappers that require rc=0 will skip release and then blame expiry); same-writer re-claim; `KNOWN_WRITERS` closed set (must die for vendor-plural, but a blind port keeps it and refuses COSMOS workers); naive timestamps; parent-walk WATCHED (must die); torn-file refuse; unreadable-vs-changed split as implemented (lossy, but it is the behavior); `_readme` field inside the lock JSON (callers that json-load and expect a closed schema may strip it — harmless). The hash manifest itself is easy to drop if a designer thinks "we have an enforcing lock now." Dropping it loses the only tool that can tell a concurrent write from a lying mount. Enforcement and fingerprinting are not substitutes.

**bts_phone.** Lose: missing-inbound is DEAD not "no news"; non-zero on dead; belt `assert isdir(AIROOT)`; outbox≠inbox and mirror≠source selftest; the *instruction* to look at the Research4 mirror (should lose); CoW/QA filename pair (must lose for N>2); probe prints mtime+size without alarming; no send path (a spec that says "mailbox" will invent a write-in-place and recreate last-writer-wins).

**bts_runner.** Lose: drain-all (should lose); `--once` idle-message quirk; live-queue selftest (should lose); status-blind findings (should not lose — must fix); uncaught rename (should lose); `py -3.14`; cwd=queue; always-rc-0 process; heartbeat field set (aware local + epoch + UTC + lane); ledger fsync; `__tNNNN` cap 21600; helper skip printed by `--status`; collision rename with timestamp suffix on dest; `move_failed` ledger event when the post-job rename dies (FUSE) — job stays in `running\`, not retried; root-queue default when `--lane` omitted (load-bearing: the historical inbox stays live); lane-name charset refuse (return 3); `RUNNABLE` dict *absence* (do not reintroduce). A spec that says "scheduled worker, claim-by-rename, three outcomes" can still drop UTF-8-on-both-ends, log-first, and report-never-retry if the writer has not read the scars.

---

### B.2 INPUT B — open design questions

#### 1. ENFORCING LOCK

**Reject OS-level file locking as the cross-universe mechanism.** `LockFileEx` lives in the Windows handle table. The sandbox talks to a FUSE (or similar) view of the same bytes. The 2026-08-16 incident already proved the two sides do not share file identity: one side can hold "the lock" the other cannot see. I will not design as if `flock`/`LockFileEx` started working because we renamed the tool COSMOS. Exact mount driver: **UNKNOWN / NOT IN PACKET**. That unknown is a reason to *avoid* depending on OS lock semantics, not a reason to hope.

**Reject a lease file that both universes write.** Exclusive-create (`O_EXCL`, `ReplaceFile`, POSIX `O_CREAT|O_EXCL`) still requires both writers to resolve the *same* inode. Two universes plus a resolver bug is two exclusive leases, both green. That is the cooperative file with better flags.

**Reject a fencing token with no single issuer.** Two issuers are two fence spaces. A fence is only a fence if one clock assigns it.

**Adopt: native-only arbiter + request-by-rename + one lease + monotonic fence + role-relative fingerprints.**

Concrete shape:

1. **`cosmos_lockd`** runs only on native Windows (service or scheduled task). It takes a machine-wide named mutex `Global\COSMOS_LOCKD`. A second instance exits 2 and prints the holder. Session death of lockd releases the mutex; that is the OS doing what a cooperative JSON file cannot.
2. **Sandbox never writes `lease.json`.** Workers (any universe) drop a *request* file into `queue("lock_requests")` via the resolver. The drop is write-temp + rename. Request names: `req__<worker_id>__<nonce>.json` with `{op: claim|renew|release, worker_id, why, fence_held or null}`.
3. **lockd** rename-claims one request into `lock_running\`, processes it, writes the lease with native `ReplaceFile` (or write-temp + `os.replace`) under `\\?\`, fsyncs. It can unlink because it is not on FUSE. It still *does not need to unlink*: the stable file is `lease.json`, always present, never deleted. Free state is `{holder: null, fence: N, ...}`. This survives "FUSE refuses unlink" because FUSE is not the writer, and because we stopped treating absence as free.
4. **Lease body:** `{fence: uint64, holder: worker_id|null, expires_epoch: int, why, manifest: {relpath: sha16|null|{"state":"absent"|"unreadable"|"empty"|"hashed","sha":...}}, lockd_pid, lockd_started_epoch}`. `fence` increments on every grant and every forced expiry. Never reset to 0 on lockd restart. Restart reads the lease; if torn, **refuse and stop** (do not treat as free); if parseable and unexpired, honor the holder; if stale, increment fence, set holder null, announce.
5. **Session death without release:** expiry is epoch seconds, compared with `time.time()`. No timezone. Holder must renew (request `renew` with the current fence) before expiry. lockd is what expires. The 90-minute incumbent constant can stay as a default; it is not optional (packet 08-22).
6. **Two universes:** both must resolve `queue("lock_requests")` to the same directory *and* pass the sentinel check on that directory (see B.3). If the sandbox resolver fails, the sandbox cannot request — it cannot start a writer. If it writes a literal backslash name in cwd, that is not in `lock_requests` and lockd never sees it; the sandbox's own probe (`--check` on the request dir) says DEAD. Probe-not-assume applies to the lock channel too.
7. **Manifest keys are role-relative** (`rold/rails.toml`, `mesh/bts_health.py`), never `str(absolute Path)`. Closes grok-08. Four states stored explicitly. Closes grok-07.
8. **Same-writer re-claim** refreshes expiry and *does not* replace the manifest unless `--rebaseline` is explicit and announced. Closes grok-10.
9. **Closed writer set** becomes a registry file behind a sentinel, not a Python set literal. Unknown worker → refuse 2. Vendor-plural updates the registry, not the lockd source.
10. **What this still cannot do:** stop a process that writes the tree without asking. True mandatory locking on arbitrary files across this mount is a filter driver. **UNKNOWN** whether Keith wants a minifilter. I will not invent one. Enforcement here means: no two *protocol* writers, auto-expiry, one fence space, fingerprints that work across universes, no fail-open torn lease. Violation by a non-participant remains a *detected* event via `--verify`, not a prevented write.

#### 2. SCHEDULER CONCURRENCY + PRIORITY

Keep the incumbent's proven properties. Do not keep drain-all, global rebind, live selftest, or the process-rc-always-0 lie as the *only* signal (ledger stays authoritative; process rc should still be 0 on a clean tick so a scheduled task does not flap — that part I would keep, and I would document it).

Minimal design:

1. **The file is still the dispatch.** Job = runnable dropped in the lane inbox. Helpers `_` skipped in-runner and printed by `--status`.
2. **Priority on the job:** `__pNN__` in the filename, `NN` in `00–99`, default `50` if absent. Invalid `__p__` → refuse to claim, print, leave in inbox (do not run, do not hide). Tie-break: remaining name ascending (today's `sorted()`). Do not add a sidecar priority file (it can tear; last-writer-wins).
3. **Concurrency is a property of the lane, not a shared counter file.** `lane.toml` (read-only at worker start; change requires restart) or env `COSMOS_LANE_CONCURRENCY`. A supervisor starts N *processes*, each with `COSMOS_WORKER_ID` required. Missing worker id → exit 2 before any mkdir. No in-process thread pool; that fights `set_lane` and `subprocess.run`.
4. **One job per cycle per worker.** Claim at most one file, run it, loop. Closes grok-17.
5. **Claim-by-rename**, dest `running/<jobstem>__w_<worker_id>__<nonce><ext>`. On `FileNotFoundError`, continue (lost the race). Never crash the tick. Command is built from the *claimed* path. Closes grok-21 and keeps the 0.1s-all-fail scar closed.
6. **Three worded outcomes, same dirs:** 0 → `done\`, 2 → `done\findings\`, else → `failed\`. `--status` lists findings as its own row. Closes grok-19.
7. **Log-first.** Same RUNNING header, UTF-8 env + parent `encoding="utf-8"`. Timeout writes `RED - TIMED OUT`. Nothing deleted.
8. **Report-never-retry.** Stale = in `running\` longer than `max(declared __t, STALE_RUNNING_SECS)` *and* no live heartbeat from the worker whose id is in the claimed name. A job within its `__t` is not STALE. Closes grok-22.
9. **Per-worker artifacts, no last-writer-wins file:**
   - `runner_heartbeat__<lane>__<worker_id>.json` — glob-discoverable at the base. Fields: aware-local, epoch, UTC, lane, worker_id, pid, host, fence_held_or_null, current_job_or_null.
   - `runner_ledger__<worker_id>.jsonl` — append + fsync. Two workers never share a jsonl (incumbent comment already said interleaved lines are worse than two clean logs).
   - Heartbeat is rewritten on a timer *during* the job (every 60s), not only at cycle start.
10. **Queue path from the resolver**, `\\?\` on walks. No `V:\Ai\_queue` literal. Linux/sandbox must refuse to be a runner (`os.name != "nt"` → exit 2, no mkdir). Closes grok-20.
11. **Selftest** uses `tempfile` for QUEUE_ROOT, never the live tree. Plants success/fail/findings/helper/unknown-flag/overlap-rename. Closes grok-18.
12. **tree_lock / lockd:** a job that declares write (filename `__write__` or a shebang-level sidecar — I prefer the filename, one representation) must hold a fence. The runner sends `claim`/`renew`/`release` requests. Read-only jobs do not. This is the one design decision in two files, now in code.
13. **Do not reintroduce `RUNNABLE`.** `_is_runnable` iff `_cmd_for` is non-empty.

That is the minimum that keeps the scars paid-for and satisfies Keith's concurrency/priority/identity rules. A work-queue database would also work and would drop "the file is the dispatch"; I do not recommend it. The sandbox's only proven ability is "write a file."

#### 3. RESOLVER FOR ONE ROOT

Successor of `bts_paths`, call it `cosmos_paths`, one tree: the compiled default on Windows is `V:\A\Ai\COSMOS`. I am taking that string from INPUT B.3, not from any other file.

Rules, in order:

1. **Import-time resolve-or-raise.** The incumbent chose fail-fast; the packet says it has never been the defect. Call-time start-anyway is how a tool writes into cwd and looks successful. Keep import-time. Hermetic tests: hide the compiled default (do not create `V:\A\Ai\COSMOS` on the test box) and set `COSMOS_ROOT` at process start. Do not add a "test mode" fallback inside the module.
2. **One entry per platform.** Windows: `[r"V:\A\Ai\COSMOS"]`. Nix: `["/sessions/*/mnt/A/Ai/COSMOS"]` — **UNKNOWN** whether the peer/sandbox mount point will actually be that string; if the real mount is different, the compiled default must change, not grow a ladder. I will not invent `/mnt/cosmos` as a second rung.
3. **Multi-hit glob raises.** Print every hit. Do not `sorted()[0]`. Closes grok-03.
4. **`COSMOS_ROOT` last**, only if the compiled default is absent. `isdir` is not enough; see sentinels. Env cannot shadow a healthy default. Peer cold machine with a different letter: default misses, env wins. Peer cold machine with a leftover empty `V:\A\Ai\COSMOS`: env cannot save them — they must remove the stub or they are on the wrong tree. That is the point.
5. **No second root.** `AIROOT`/`ROOT` collapse. `mesh/queue/board/rold/working/archive/mail` are roles under the one root. `ai()` as `ROOT/Ai` dies so it cannot be confused with `airoot()`.
6. **`secrets()` is safe by location.** It is a sibling of the *published* subtree, not of `mesh`, and not "under COSMOS if COSMOS is what gets published." **UNKNOWN / NOT IN PACKET** what COSMOS will publish. The resolver must take a `publish` role (the subtree that may be pushed) and place `.secrets` next to it, never inside it. An exclude list is a blocklist and blocklists rot — keep that sentence in the acceptance test, not only in a comment.
7. **Sentinel-content assertion.** Every role directory contains `.cosmos-role` whose exact bytes are `role=<name>\n`. Resolve functions `isdir` then read and compare. Mismatch or absence raises, naming the path and the expected bytes. Existence is not identity (08-21 mesh).
8. **`\\?\` on Windows walks.** Prefix internally for any filesystem operation. Provide `display(path)` that strips for humans. Apply in this module so callers inherit it; do not wait for each walker to remember C-60.
9. **Never `Path(__file__).parent` for roles.** Consumers that need ROLD call `rold()`, not `mesh().parent`.
10. **CLI:** unknown flags *and* unknown positionals → 2. `--check` asserts every role sentinel and prints AI-equivalent (the one root + every role). `--selftest` plants: missing default, multi-hit (if nix), dir without sentinel, env-shadow attempt (create a dummy default, set env to another tree, require the dummy). If `--selftest` is listed, it must run. Closes grok-01/02/04.

I do **not** move env first for portability. That is the popular wrong answer.

#### 4. IPC AT N>2

Generalize the phone from two letter files to a directory that *is* the channel.

1. **`mail/` must exist** (resolver role + sentinel). Missing `mail/` = `THE PHONE IS DEAD` (rc=1). This is the missing-vs-empty distinction at channel level. An empty inbox is news: "no letter." A missing inbox is a misaddress.
2. **Per-worker inbox:** `mail/to/<worker_id>/`. If `mail/` exists and `mail/to/<worker_id>/` does not, that is MISADDRESSED (rc=1), not EMPTY. Probe must print which of {channel missing, worker inbox missing, inbox empty, inbox live}.
3. **One writer per file.** A message is `mail/to/<dest>/from-<src>-<utc>-<nonce>.md`. Write-temp in a private staging dir, rename into the dest inbox. No `COW_TO_QA_ENGINEER.md`. Two concurrent senders cannot clobber.
4. **Identity in the file header** (first lines, not only the name): `from`, `to`, `nonce`, `utc` with offset, `epoch`, optional `in-reply-to: <nonce>`.
5. **Probe-not-assume:** `--check --as <worker_id>` prints resolved paths, the four-state on the inbox, count, newest mtime+size+age (tz-aware). Non-zero on dead/misaddressed. Zero on empty or live.
6. **Staleness:** if the newest inbound is older than N days *and* this worker has an outbound with no file in any inbox whose `in-reply-to` matches that nonce, rc=2 (FINDINGS / STALE CONVERSATION), not rc=1 DEAD. Presence + age without this rule is the 2026-08-23 observation (letter since 08-18, no alarm). N is a constant, announced, not inferred.
7. **Read:** refuse undecodable UTF-8 (no `errors="replace"`). Empty file is a letter with zero bytes — print size, rc=0, do not call it missing.
8. **No send-by-overwrite. No Research4/mirror fallback text.** One root.
9. **Selftest:** dead channel (impossible dir) → non-zero; empty inbox dir → zero; two planted messages from two senders both present (no last-writer-wins); in-reply-to clears stale; unknown `--as` that has no inbox dir → misaddressed.

The incumbent's load-bearing lesson is not "two files." It is "a channel nobody probes is indistinguishable from a channel that works." Keep the probe. Kill the pair.

#### 5. WHAT ELSE BREAKS AT THE PORT (not covered above)

These are the singletons I would not expect the other families to copy from the characterization, because the characterization does not see them.

1. **`rc=2` collision (grok-26).** PLM-44 and "unknown flag → 2" cannot share a number once wrappers exist. COSMOS should reserve process rc 2 for refuse/unknown, and put FINDINGS on a *word* in the ledger plus a dedicated dest dir — which the runner already has. Job rc 2 can stay as the job's own exit (the child, not the runner). Do not let the runner's process rc equal the child's FINDINGS code.
2. **Prose-eating migrators.** The 2026-07-17 sweep rewrote paths inside the resolver's own history and collapsed the ladder to the same path twice. COSMOS will be the next tree rename (`V:\Ai` → `V:\A\Ai\COSMOS`). Any path-rewriting tool that is not told to skip prose and skip tests-as-history will falsify this return, the scars, and the ladders again. This is not a lock/scheduler/resolver/mailbox question; it is a tooling constraint on the port itself.
3. **Import-time `bts_paths` makes every importer a machine assertion.** That is a feature in production and a silent skip of an entire test file on a peer box. Port hazard: CI goes green because `import cosmos_paths` raised and the runner treated collection error as "no tests." Fail-loud only works if the thing that saw the raise is allowed to go red.
4. **Heartbeat mtime vs heartbeat JSON.** `--lanes` trusts mtime. A torn or last-writer-wins heartbeat still looks alive. COSMOS checkers must parse JSON, require `worker_id`, and compare `last_run_epoch`. Mtime is a hint, not a verdict.
5. **Scheduled-task overlap policy is NOT IN PACKET** and decides whether grok-17/21 are theoretical. If the task is "run a new instance anyway," overlapping drain-alls are production. If it is "queue a new instance," jobs pile behind a drain. If it is "do not start," heartbeats freeze. The port must write this policy down next to the scheduler; the Python file cannot be the whole spec.
6. **`KNOWN_WRITERS` as source-closed set** will refuse the first COSMOS vendor not in the literal. The closed set is correct *as a behavior* (unknown writer refused). The *membership source* must move.
7. **Publish/secrets under one root (see B.3.6).** If someone publishes `V:\A\Ai\COSMOS` wholesale, sibling-of-mesh is no longer sibling-of-published. This is the one property the characterization says to preserve and the one most likely to be "simplified."
8. **`argparse` vs hand-rolled `KNOWN_FLAGS`.** Runner already uses argparse (unknown flags die, `--help` exists). The other three hand-roll. A unification pass will change exit-code timing and can introduce default-0 after a partial parse. Port them one way, with an explicit unknown-flag selftest on each.
9. **Jobs inherit `cwd=queue`.** A COSMOS job that writes `./tree_lock.json` or `./lease.json` relative is a writer that never asked lockd. The runner should set cwd to a per-job scratch under `logs/scratch/<claimed>` or refuse relative writes — otherwise enforcement is theater again.
10. **Watcher list built from `__file__`.** Even after ROLD is fixed, `MESH / "bts_health.py"` still hashes the copy next to the lock source. A vendor running from a checkout that is not the live mesh will fingerprint the wrong tree and `--verify` will cry wolf or go silent. Watched paths must be resolver roles, not `__file__`.
11. **Negative-control selftests that plant into production paths.** tree_lock selftest retargets LOCK to temp (good). phone retargets INBOX (good). paths has no selftest. runner plants into live PENDING (bad). The port will copy the runner pattern if that is the "scheduler selftest" example.
12. **Worded outcomes vs emoji.** Runner logs words (`FINDINGS rc=2`, `RED - TIMED OUT`) *and* the source is full of 🔴. UTF-8-on-both-ends made that survivable. A "no emoji" cleanup that also rewrites log grammar will break checkers that grep `FINDINGS rc=2`. Preserve the words; they are the API.

---

### B.3 INPUT C — behavioral cards

No SOURCE APPENDIX files beyond the four deep modules were included in this packet.

**SKIP.** I will not invent cards for the other 135.

The four deep modules, if a card is wanted for completeness of *this* packet's sources (not INPUT C, which said "beyond"):

- `bts_paths.py` — reads: compiled ladders, env, filesystem isdir/isfile, argv. writes: stdout. invoked-by: import of lock/phone (runner does not import it). refuses: unknown `--` flags (exit 2); missing ROOT/AIROOT (raise at import).
- `tree_lock.py` — reads: lease JSON, watched files' bytes, argv. writes: `queue("tree_lock.json")` (or blanks it). invoked-by: CLI; runner does not call it. refuses: unknown flags (2); unknown writer (2); second writer (1); torn JSON (raise); release by non-holder (1).
- `bts_phone.py` — reads: inbound letter, argv, AIROOT. writes: stdout only. invoked-by: CLI. refuses: unknown flags (2); missing AIROOT (assert); missing inbound on `--read`/`--check` (1).
- `bts_runner.py` — reads: queue dir, heartbeats, argv. writes: running/done/failed/findings, logs, ledger, heartbeat, mkdir tree. invoked-by: Windows scheduled task (XML NOT IN PACKET), CLI. refuses: bad `--lane` name (3); argparse unknown flags; helpers (`_` prefix) skipped not refused.

---

### B.4 Closing

The characterization is a better map than the docstrings and a worse map than the source. The expensive lessons (no fallback, torn-refuse, claim-by-rename, three worded outcomes, log-first, report-never-retry, helper-in-runner, UTF-8 both ends, glob-discoverable heartbeats, secrets-by-location) are real and must survive. The port hazards are mostly shapes the characterization already named and then failed to notice still living in the attached files: parent-walk, two-universes writes, last-writer-wins JSON, collapsed file states, naive timestamps, and a runner that does more per tick than it admits.

I would rather be compared as the family that called `ROLD now resolves via bts_paths.rold()` false than as the family that repeated it.
