# SESSION TOOLS — MOTIF stage-2 ARCHITECTURE (independent design)

**Lane:** CURSOR Cloud Agent, pinned `claude-opus-5-thinking-high`. Composer 2.5 / Auto refused.
**Run:** `bc-2f8665b1-161b-4825-9008-015633d86695` · branch `cursor/motif-session-tools-architecture-e416`.
**Clone:** independent clone of `github.com/keithbbf-gif/cosmos` default branch at `223a7dd`. No local
uncommitted COSMOS was read. `docs/arch/SESSION_TOOLS_ARCH.md` is **ABSENT** in this clone — verified
by `git ls-files`, so there was nothing to peek at; this design is independent by construction.
**Stage:** 2 (ARCH) per `docs/MOTIF.md` — *"decision rubric FIRST, then each node designs
independently (no peeking)."* **No BUILD.** No `builds/session-tools/*.py` is authored here.
**Baseline:** `docs/research/SESSION_TOOLS.md` (stage-1 RESEARCH, CCr/Grok 4.6, 2026-09-05).
**P10:** PROPOSE only. Nothing under `V:\A\Ai\COSMOS\` is written by this run. CCr disposes.

---

## 0. The three decisions, up front

The baseline (`SESSION_TOOLS.md` §Next) requires this stage to pick three things independently.

| # | Decision | Verdict |
|---|---|---|
| **D1** | Canonical transcript schema (one) | **`cosmos-transcript/1`** — deterministic JSONL, one head record + N turn records, with a **byte-span partition** of the source that makes the round-trip gate arithmetic. Volatile provenance lives in a `.decl.json` sidecar, so the transcript file is a **pure function of its source**. |
| **D2** | First family after Claude | **ACCEPT `grok-tui`.** Decision uncontested; the baseline's *criterion* is **CONTESTED** — I substitute "retire the widest fidelity gap first" for "obvious next / biggest corpus". They converge here. |
| **D3** | crash-recover shape | **check + restore-from-bak. A third writer is REJECTED.** And enforced structurally: the suite has **no code path that opens a vendor store for write**. The only mutation in the whole suite is `rebind`. |

Each is argued in §3, §4, §5 with the measured evidence it rests on.

---

## 1. Decision rubric (applied before designing)

The baseline's R1–R10 stand. This design adds four criteria that the stage-1 rubric did not
constrain, because they are the ones that actually decide the schema:

| # | Criterion | Why it decides something |
|---|---|---|
| **A1** | **Fidelity must be provable, not asserted** | The baseline sets `convert`'s gate at *"byte-identical round-trip on a fixture"*. A normalized schema cannot round-trip. Either the schema carries the source bytes' structure, or the gate is a lie. This forces the span partition (§3.3). |
| **A2** | **Determinism over timestamping** | If a transcript embeds `produced_at`, converting the same source twice yields two different files and `diff` degrades to a fuzzy compare. Pushing all volatile provenance into the sidecar makes `sha` itself the identity, and `diff` a sha compare. |
| **A3** | **Fences belong in the refusal taxonomy, not only in prose** | `AGENT_BOUNDARIES.md` item 14: *"A new session will not know item 12… protect by folder grant + lease, not a hidden overwrite."* Same lesson here. `WOULD_WRITE_SOURCE` and `CLOSED_VERB` are typed refusal kinds so a future session that never reads this doc still hits a wall. |
| **A4** | **Zero new writers, zero new clocks** | *Improvement is not bloat* (`docs/MOTIF.md`). A suite of nine verbs that adds one writer and one daemon has taxed COSMOS. The design target was **no new authority and no new scheduled task**, and it is met (§7). |

---

## 2. What already exists — the suite composes it, it does not rebuild it

Measured in this clone. Every row is a reuse target; none is re-implemented.

| Need | Existing component | Binding |
|---|---|---|
| Resolve any live path (no hard-coded paths) | `CosmosPaths(root).role(name, *parts)`; roles declared once in `ROLES` | `cosmos/cosmos_paths.py:41-54,153-177` |
| Root identity | `.cosmos-root.json` sentinel, `tree_id`, `IDENTITY_MISMATCH` | `cosmos/cosmos_paths.py:73-128` |
| Typed refusal shape `(kind, detail)` | 55 error classes, 141 distinct kinds, all `(kind, detail)` | `cosmos/cosmos_refusals.py`; `docs/REFUSAL_TAXONOMY.md:10` |
| Declared-length integrity + sidecar | `write_declared(path, content)` / `read_verified(path, expect_len, expect_sha)` | `cosmos/cosmos_validate.py:32-60` |
| Sidecar precedent | `state/SEED.json` + `state/SEED.decl.json` | `cosmos/cosmos_session.py:38-40,288-294` |
| Secrets redaction | `redact(text) -> (clean, n)`, 11 named detectors | `cosmos/cosmos_askmine.py:118-154` |
| Verified copy + manifest (quarantine) | `Backup.run(src, target)` → `{dest, files}` + `_MANIFEST.sha256.json` | `cosmos/cosmos_backup.py:172-211` |
| Content-addressed blobs | `CAS(root)` with `put/get/has`, read-back hash check, standalone (no ledger dependency) | `cosmos/cosmos_segments.py:339-386` |
| Vendor transcript locations | `transcript_path(rail, cwd, session_id, home)` — Claude **and** Grok, already measured | `cosmos/cosmos_resession.py:417-432` |
| Read-only SEED preflight | `precheck_seed(seed_path, decl_path, live_tree_id)` | `cosmos/cosmos_resession.py` |
| Display / product surface | `GET /api/v1/recents` → `cosmos_recents_panel.handle_get`; `Open_sessions.py list\|open` | `cosmos/cosmos_service.py:228,688-705`; `builds/open_sessions/Open_sessions.py:26,32-58` |
| Torn-input discipline to copy | `TORN_LEDGER` — *"a torn ledger must never read as free"* | `cosmos/cosmos_lock.py:295-297` |

**The one thing COSMOS deliberately refuses to do today, and this suite must own.**
`transcript_path()` says it plainly:

> *"The satellite never PARSES these files (the format is version-unstable) — existence + mtime is
> the whole signal."* — `cosmos/cosmos_resession.py:424-425`

That is the gap the suite fills. **session-tools is the single quarantine for version-unstable
vendor formats.** Everything else in COSMOS stays on existence+mtime; only the family adapters
(§6) parse, and only they carry the churn. That is the architectural reason the suite is a separate
build and not a patch to `cosmos_resession`.

### 2.1 Measured blocker that changes this design

`builds/cdeck` is a **submodule gitlink with no `.gitmodules`**, so `cosmos_recents_panel` does not
exist in a clean clone:

```
$ git ls-files -s builds/cdeck
160000 f4270d0953a5e2b8d17b33aac3fe826e8767e86a 0	builds/cdeck
$ cat .gitmodules
cat: .gitmodules: No such file or directory
$ git submodule status
fatal: no submodule mapping found in .gitmodules for path 'builds/cdeck'
$ python3 builds/open_sessions/test_open_sessions.py
ModuleNotFoundError: No module named 'cosmos_recents_panel'
```

On Keith's box the files are present, so **Core `:8770` is fine and Open Sessions is live** — this is
a *repo* gap, not a runtime one. But it has a direct design consequence, which is why it is here and
not in a footnote: **a session-tools test may not `import cosmos_recents_panel` at module scope.**
Off Keith's machine (GitLab CI, a peer's cold install) that import is a hard `ModuleNotFoundError`, so
a `migrate`→recents assertion written that way would be unprovable exactly where the runtime-binding
gate is supposed to run. §8 therefore puts the recents assertion behind an **availability probe**.

Proposal to CCr (P10 — this run does not fix it): either commit `builds/cdeck/` as real files, or add
a `.gitmodules` mapping. Not in scope for this suite; recorded because it bounds the gate.

---

## 3. D1 — the canonical transcript schema: `cosmos-transcript/1`

### 3.1 Shape and naming

One session = one file plus one sidecar, following the SEED precedent exactly:

```
<transcript_id>.ctr.jsonl        the transcript  (deterministic; pure function of its source)
<transcript_id>.ctr.decl.json    the declaration (len, sha, body_sha, + volatile provenance)
```

Record order inside `.ctr.jsonl`: **record 1 = `head`**, then **N × `turn`**, in `seq` order. No tail
record — the coverage proof lives in the sidecar, which is the house pattern
(`cosmos_validate.write_declared`, `cosmos_session.py:288-294`).

### 3.2 Why JSONL, and why not sqlite

- **House idiom.** The authority ledger, the sched ledger, and the lease ledger are all JSONL.
- **Streaming.** The first corpus is 24.4 MB / 17,439 turns (`SESSION_TOOLS.md`). Line-oriented means
  `diff` is a turn-indexed compare and `check` is a single pass, neither needing a whole-doc parse.
- **sqlite is refused as the canonical form** because it would create a second store that could be
  mistaken for authority. Canon: large artifacts go to a CAS, queue/registry/panel views are
  **rebuildable projections, never authority** (`docs/FINAL_ARCHITECTURE.md:14`). An index over
  `.ctr.jsonl` is welcome — as a projection. `GET /api/v1/recents` already *is* that projection, and
  the suite feeds it rather than competing with it.

### 3.3 The round-trip mechanism — the load-bearing part

`convert`'s gate is *byte-identical round-trip*. A normalized schema cannot satisfy that alone, so
`cosmos-transcript/1` **partitions the source byte stream**. Every byte of the source belongs to
exactly one span, and each span is either:

- a **turn** span — carried by a turn record's `src {off, len, sha256}`, or
- a **frame** span — the semantically empty bytes between turns (delimiters, headers, trailing
  newline), listed on the head record as `frames[] {after_seq, off, len}`.

Concatenating all spans in order reproduces the source **byte for byte**, so the gate is arithmetic
rather than a claim:

```
sum(span.len for all spans) == source.len
sha256(concat(spans in order)) == source.sha256
```

A reviewer can check that with a calculator. That is the difference between a provable gate and a
green log.

**Fidelity is declared per source, because not every source is a byte stream.** A directory of md
files or a set of sqlite rows cannot be partitioned as one stream, and claiming otherwise would be
fabricated compliance. So each entry in `sources[]` declares a mode:

| mode | Applies to | Round-trip means |
|---|---|---|
| `span` | one byte stream — Claude Code `.jsonl`, a Grok TUI entry file, one Cowork `.md` | reconstruct from spans; exact, provable by the identity above |
| `blob` | not a byte stream — sqlite rows, a directory of files | the verbatim source is preserved whole in the suite CAS by sha; round-trip is `CAS.get(blob_sha)`, and turn records carry `src {blob_sha, key}` where `key` is the row PK or filename |

`check` asserts the declared mode against the source. A transcript that claims `span` but is `blob`
is `FIDELITY_MISMATCH` — a typed refusal, not a warning.

### 3.4 `head` record

Purely content-derived. No timestamps, no tool version, no environment — that is what makes the file
deterministic (**A2**), which in turn makes `convert` idempotent and `diff` a sha compare.

| field | type | notes |
|---|---|---|
| `schema` | `"cosmos-transcript/1"` | |
| `kind` | `"COSMOS_TRANSCRIPT"` | matches `COSMOS_SEED` style |
| `transcript_id` | str | `<family>-<native_id>`, or `<family>-<sha12(source_sha)>` when the vendor has no id. **Never minted** — Open Sessions' "no fake ids" rule |
| `family` | enum | `claude-code · cowork-pack · grok-tui · opencode · claude-desktop · codex · gemini · unknown` |
| `native_id` | str \| null | the vendor's own id, verbatim. `null`, never a substitute |
| `cwd` | str \| null | the directory the session ran in — the Grok store's key, and the leftover-cwd crash signal |
| `stream` | enum | `cm · plumbing · physics · chapter · legal · unknown` |
| `legal` | bool | when `true` the **body is not materialized** from this profile (R7) |
| `sources[]` | list | `{idx, path, kind: jsonl\|md\|sqlite\|dir, len, sha256, mtime, fidelity: span\|blob, blob_sha?}` — a list because Cowork = md + catalog row, opencode = db rows |
| `frames[]` | list | `{after_seq, off, len}` — `span` mode only |
| `n_turns` | int | |
| `models[]` | list[str] | distinct models that **actually answered**. The runtime-binding value: *"the model that actually answered"* (`CLAUDE.md`, no-fabricated-compliance) |
| `t_first` / `t_last` | float \| null | `null` when the source has no timestamp. Never inferred |

### 3.5 `turn` record

| field | type | notes |
|---|---|---|
| `seq` | int | 1-based, monotonic, **gapless** — a gap is `UNPARSEABLE` |
| `role` | enum | `user · assistant · system · tool_call · tool_result · meta` |
| `t` | float \| null | epoch. `null`, never guessed |
| `utc_off` | int \| null | matches the ledger's `t`/`utc_off` pair |
| `text` | str \| null | normalized plain text; `null` for non-text turns |
| `model` | str \| null | the model that answered this turn |
| `tokens` | `{in,out}` \| null | |
| `parts[]` | list | `{type: image\|file\|tool_json\|audio, sha256, len, mime}` — a **CAS pointer, never an inline blob** (canon: filename = hash, the record holds the pointer) |
| `src` | obj | `span`: `{source_idx, off, len, sha256}` · `blob`: `{source_idx, blob_sha, key}` |
| `redactions` | int | `0` unless this is an `anonymize` output |

The **closed `role` enum is what makes `diff` meaningful across families**: a Claude `tool_use` and a
Grok tool call land on the same role, so a cross-family diff compares conversations rather than
vendor spellings. An unmappable source role is `SCHEMA_UNKNOWN`, never silently folded into `meta`.

### 3.6 `.ctr.decl.json` sidecar

Everything volatile, so the transcript stays pure:

```json
{ "schema": "cosmos-transcript/1", "len": 0, "sha": "", "body_sha": "",
  "source_sha": "", "n_turns": 0, "fidelity": "span", "spans_ok": true,
  "produced_at": 0.0, "produced_by": "session-tools/1", "tree_id": "",
  "anonymized": false, "derived_from": null }
```

- `sha` / `len` — via `write_declared`, verified via `read_verified` (`cosmos_validate.py:32-60`).
- `body_sha` — sha over the turn records only. Survives a head-only change; the axis `diff` uses.
- `tree_id` — provenance stamp, **not** a gate. A transcript is a portable artifact; it must open on a
  peer's cold machine (`docs/FINAL_ARCHITECTURE.md`: installable by a peer). Contrast `SEED.json`,
  which is install-bound and refuses on mismatch.
- **No HMAC, deliberately.** SEED carries one because carry-over must be authenticated against *this*
  install's key (`cosmos_session.py:108-116`). A transcript must travel, and the suite must not touch
  `install_key.bin` — which the backup clock also explicitly declines to copy
  (`cosmos_backup_clock.py:190-193`). sha256 gives integrity; HMAC would buy authenticity at the cost
  of portability and a key handle the suite has no business holding. Stated as a decision so stage 3
  can overturn it on purpose rather than by accident.

---

## 4. D2 — first family after Claude: **ACCEPT `grok-tui`**

### 4.1 Three measured reasons

1. **It is the only non-Claude family with an in-tree, already-measured path resolver.**
   `transcript_path("grok", cwd, sid, home)` → `~/.grok/sessions/<url-quoted cwd>/`, bound to
   `docs/research/AUTO_RESESSION.md` 1.3/2.1 (`cosmos_resession.py:417-432`). Every other candidate is
   either UNMEASURED (Claude Desktop, per the baseline's own table) or not a chat store at all (Cursor
   cloud jobs, SGH `work_orders/drop`). Choosing an unmeasured store first would violate *UNKNOWN, not
   guess*.
2. **`RAILS = ("grok",)`** (`cosmos_resession.py:97`). The resession satellite already spawns and
   tracks exactly this family, so its transcripts are the record of COSMOS's own construction — the
   corpus where a dropped turn is a governance loss, not an inconvenience.
3. **Converter-risk retirement** — see §4.2.

### 4.2 Where I contest the baseline's criterion

The baseline calls Grok TUI *"the obvious next on this machine."* I accept the answer and reject the
reasoning, because "obvious / biggest corpus" would give a wrong answer on the very next call.

Order should be chosen to **retire the widest fidelity gap first**:

- Claude Code is a **single `.jsonl` file per session**. That is the easy case. A schema validated only
  against it will silently bake in *one session = one file* and *source is one byte stream*.
- Grok TUI is a **directory keyed by url-quoted cwd, with id-keyed entries inside**. It forces
  `sources[]` to genuinely be a list, forces the `span`/`blob` split to exist before anything depends
  on it, and forces `cwd` to be a first-class head field — which is *also* the leftover-cwd crash
  signal the baseline names (`SESSION_TOOLS.md:52`, GFO `gentle-falcon`).

So `grok-tui` second is not merely convenient; it is the choice that **proves the schema generalizes
before** 666 Cowork md files and opencode sqlite arrive. Under the baseline's stated criterion,
`claude-desktop` would be a defensible second pick — it is Claude-family and the plugin already claims
it. Under mine it is the worst pick: it proves no new fidelity mode and rests on an UNMEASURED path.

**One line for stage 3:** the *decision* (grok-tui) is uncontested; the *criterion* is CONTESTED —
"retire the widest fidelity gap first", not "obvious next". If a peer design picks `opencode` second,
I hold my position: opencode is the **`migrate` target** and Keith's **live** store; reading it as a
source family before the schema has proven itself on a read-only vendor store puts the one store whose
corruption breaks the live sidebar first in line. Read-only families first, live stores last.

### 4.3 Resulting family order

| # | family | why here | status |
|---|---|---|---|
| 1 | `claude-code` / `cowork-pack` | done — 666 packed | **CLOSED. Do not re-ingest.** |
| 2 | **`grok-tui`** | measured path in-tree; forces dir-of-entries + `span`/`blob` (§4.2) | **this design's pick** |
| 3 | `cowork-pack` md as a *first-class source* | 666 md + catalog already on disk; read-only; exercises multi-source `sources[]` | after 2 |
| 4 | `opencode` | live store — read-only source last, on purpose | after 3 |
| 5 | `claude-desktop` | UNMEASURED; needs a stage-1 walk before it is designed against | deferred, not designed |

---

## 5. D3 — crash-recover: **check + restore-from-bak.** A third writer is REJECTED

### 5.1 The decision, and why it is structural rather than a policy

**crash-recover is not a new mutating verb. It is a composition of verbs that already exist, with
exactly one mutation point — `rebind`.**

1. **`check`** → typed verdict: `VERIFIED`, or `REFUSE(kind)`.
2. **Quarantine.** On damage, **copy** (never move, never unlink) the damaged store to
   `backups/session-tools/<stamp>/` via `Backup.run(src, target)`, which already hash-verifies and
   writes `_MANIFEST.sha256.json` (`cosmos_backup.py:172-211`). Evidence is preserved; *never delete*
   is satisfied by construction, not by remembering to.
3. **Salvage forward, side by side.** `convert` the **readable prefix** of the damaged store into a
   **new** `.ctr.jsonl` at a **new** path. A truncated sqlite is opened
   `file:...?mode=ro&immutable=1`. A torn JSONL stops at the first unparseable line and records
   `truncated_at_line` — the ledger's own discipline: *"a torn ledger must never read as free"*
   (`cosmos_lock.py:295-297`).
4. **`restore-from-bak`.** When a `*.bak_*` or `backups/verified/<stamp>/` copy exists, `diff` the
   backup against the damaged store and report the turn delta. The restore **target is a new path** —
   never the damaged one.
5. **`rebind`** is the single mutation: point the vendor app at the recovered store. It already exists
   as a verb and already has proof-JSON precedent (`cow_migrator_rebind.json`, 2026-09-05T19:11:16).

*Never repair in place* is therefore enforced by **shape**: there is no code path in the suite that
opens a damaged store for write. A reviewer verifies that by grepping the adapters for write modes —
a cheap, real gate — and `WOULD_WRITE_SOURCE` (§6.3) fires if one ever appears.

### 5.2 The third writer — the strongest case for it, and why it still fails

This deserves a fair hearing; it is not a silly idea. COSMOS already owns the machinery.

**For:** `cosmos_lock.Arbiter` is a real lease arbiter with **monotonic fencing tokens** and a
**four-phase fenced commit** that never holds the OS mutex across the callback: Phase A reserves under
the lock, Phase B stages the artifact unlocked with the token in hand, Phase C retakes the lock, CASes
the token against the live projection, and only then `os.replace()`s (`cosmos_lock.py:21-34,330-419`).
Stale tokens are `REJECTED` and the rejection is ledgered. A third writer could `acquire("opencode.db")`,
stage a repaired database, and install it under a re-verified token. Among COSMOS writers that is
genuinely safe, and it would let the suite fix a corrupt store instead of working around it.

**Why it fails anyway — one decisive reason and two supporting ones:**

- **A fencing token only fences participants.** OpenWork/opencode and the Grok TUI never call
  `acquire()`. They are foreign processes holding their own file handles, and the arbiter has no way to
  make them present a token. So the fence is absent against precisely the writer most likely to be
  mid-write during a crash — the vendor app itself. Worse, Phase C's `os.replace()` would swap a file
  out from under a live vendor handle: on Windows that either fails outright or leaves the app writing
  to an orphaned inode, so the app's next flush silently reverts or re-corrupts the repair. **A lease is
  a contract, and you cannot enter one unilaterally on another process's behalf.**
- **It would make the suite an authority**, violating R6 (*suite is tools; does not write
  ledger/kernel/sched*) and the ratified single-authority rule.
- **The BTS two-writer deletion scar** is this exact failure with a cost already paid
  (`AGENT_BOUNDARIES.md` item 9). Rebuilding the mechanism that caused it, with a fence that does not
  reach the other writer, is not a new idea.

### 5.3 Corollary — SEED / BUCm crash classes are read-only plus a proposal

`live/state` is CCr/orchestrator-only (`AGENT_BOUNDARIES.md`, "Touch the tree"). So a bad SEED MAC, a
missing `SEED.decl.json`, or a leftover `running_session_file.toml` produces a **typed REFUSE plus a
P10 proposal object** for CCr. The suite never writes SEED. It reuses
`cosmos_resession.precheck_seed(seed_path, decl_path, live_tree_id)` — already read-only, already
structural — rather than re-implementing the HMAC check and risking a second, drifting verifier.

---

## 6. Module layout, CLI, and the adapter contract

### 6.1 Layout (stage-4 BUILD target — **not** authored in this stage)

```
builds/session-tools/
  session_tools.py            CLI: nine verbs as argparse subcommands. No import-time side effects.
  st_schema.py                cosmos-transcript/1 record builders + validate(). The ONLY schema authority.
  st_spans.py                 span partition + the round-trip proof (sum + sha)
  st_store.py                 transcript paths, decl sidecar (write_declared/read_verified), suite-owned CAS
  st_refusals.py              SessionToolsRefusal(kind, detail)
  st_families/__init__.py     adapter registry
  st_families/claude_code.py
  st_families/grok_tui.py     FIRST after Claude (D2)
  st_families/cowork_pack.py
  st_families/opencode.py     read-only source; migrate/rebind target
tests/test_session_tools.py           schema, spans, refusals — hermetic tmpdir
tests/test_session_tools_families.py  per-family fixture round-trip
```

Fence from the baseline, honoured: code under `builds/session-tools/`, tests as
`tests/test_session_tools*.py`. The suite's own CAS is `CAS(paths.state("session_tools", "cas"))` — the
same class, a **separate store root**, so Core's ledger CAS is untouched (`cosmos_segments.py:344-346`
takes an arbitrary root and has no ledger dependency).

### 6.2 The family adapter contract

Four functions, so a new family is **a file, not a refactor**:

```python
FAMILY: str
def discover(home: Path, hints: dict) -> list[SourceRef]   # read-only. never writes.
def probe(src: SourceRef) -> dict                          # cheap identity: family, native_id, n_turns_est, fidelity
def read(src: SourceRef) -> Iterator[RawTurn]              # ordered. yields a byte span or a blob key.
def fidelity(src: SourceRef) -> str                        # "span" | "blob"
```

`scan` is `discover` mapped across the registry. Neither `discover` nor `read` may write — that is
what `WOULD_WRITE_SOURCE` guards.

### 6.3 Refusal taxonomy — `SessionToolsRefusal(kind, detail)`

House shape (`[kind] detail`, `.kind` attribute), so `cosmos_refusals.survey()` picks it up with no
change to the surveyor.

| kind | Fires when |
|---|---|
| `NO_SOURCE` | no store found. **Not an error** at `scan` — a legal, reportable fact |
| `UNREADABLE` | present but the OS refused it |
| `UNPARSEABLE` | parses as bytes, not as this family (includes a `seq` gap) |
| `TORN` | truncated store. Refuse; never read as free |
| `FIDELITY_MISMATCH` | declared `span`, measured `blob` (or vice versa) |
| `ROUNDTRIP_MISMATCH` | span sum or sha does not reproduce the source |
| `SCHEMA_UNKNOWN` | a source role/field with no canonical mapping. Never silently folded into `meta` |
| `IDENTITY_MISMATCH` | `tree_id` mismatch where identity is actually required |
| `LEGAL_OMITTED` | a legal row requested from this profile. Refuse; do not open (R7) |
| `WOULD_WRITE_SOURCE` | **guard**: an adapter opened a source for write. The D3 fence, in code |
| `CLOSED_VERB` | 666 re-ingest, or 666 rebind. Both **CLOSED** by Keith |
| `NOT_MY_PEN` | asked to write the COSMOS live tree. P10, in code |

The last three exist because of **A3**: a future session that never reads this document still hits a
typed wall. Prose fences drift; refusal kinds do not.

### 6.4 CLI

```
py -3.14 builds/session-tools/session_tools.py <verb> --root <live> [--json]

scan           [--family F] [--home H]
load           <source>            check          <target> [--seed]
convert        <source> [--out D]  anonymize      <transcript> [--out D]
diff           <a> <b>             crash-recover  <store> [--bak B] [--plan]
migrate        <transcript> [--workspace W]
rebind         <ses-id> --workspace W
```

`--root` is **required** and never guessed — same stance as `Open_sessions.py` (*"--root is required
(no guessed live path)"*, `Open_sessions.py:76`). `crash-recover --plan` is dry-run and writes nothing,
which is how it should be run first, every time.

---

## 7. Non-goals — the fences, stated so BUILD cannot drift

- **Not CORE kernel.** Writes no ledger, no registry, no sched, no `live/config`, no `live/state`
  outside its own `state/session_tools/` drop zone. `check` **reads** SEED; nothing writes it.
- **Does not rebuild Open Sessions or `GET /api/v1/recents`.** That product is **LIVE**. The suite
  *feeds* the projection; the panel stays the display authority.
- **Does not re-ingest the 666**, and **does not re-run the 666 rebind — CLOSED.** Both are
  `CLOSED_VERB`.
- **Does not recode `cowork_to_openwork`.** `migrate` delegates to it as a closed boundary.
- **Legal transcripts stay omitted.** `legal: true` heads carry no body from this profile.
- **Adds no clock and removes none.** The suite is on-demand CLI. `cosmos_own_clocks.py` (13 logon
  tasks, `cosmos_own_clocks.py:437-451`) is **untouched**; no `schtasks` create and **no
  `schtasks /delete`**. A future `scan` clock is named here and deliberately **not** proposed.
- **Does not take Core `:8770` down.** No route added, no service restart, no port bound, no
  `cosmos_service.py` edit. The suite runs beside Core, not inside it.
- **Adds no writer.** Nine verbs, one mutation point (`rebind`), zero new authorities (§5).

---

## 8. Runtime-binding gates — one per verb

Per canon a verb is done when it emits **a value only the live store can produce** — never an exit
code, never a green log.

| verb | writes | gate value |
|---|---|---|
| `scan` | nothing | count + absolute paths + per-source `sha256` and `mtime` of stores that exist. `0 found` is a **fact**, reported, not a failure |
| `load` | nothing | `n_turns` + head `sha`. An absent timestamp stays `null` |
| `convert` | new `.ctr.jsonl` + decl | `span`: `sum(span.len)==source.len` **and** `sha256(concat)==source.sha256`. `blob`: `CAS.get(blob_sha)` returns the source bytes. **Plus determinism:** converting twice yields a byte-identical file and an equal `sha` (§3.4/A2) |
| `migrate` | opencode/OpenWork, via the CLOSED `cowork_to_openwork` boundary | the `ses_*` id and `workspace_id` **read back** from the live store. Recents assertion sits behind an availability probe, never a module-scope import (§2.1) |
| `rebind` | vendor pointer only | proof JSON shaped like `cow_migrator_rebind.json`, plus the new `workspace_id` read back |
| `diff` | nothing | per-turn sha delta + `n_turns` delta. Identical sources ⇒ **empty delta and equal `body_sha`** (only determinism makes this checkable) |
| `check` | nothing | typed `VERIFIED` / `REFUSE(kind)`; for SEED, the `precheck_seed` result verbatim |
| `anonymize` | new derived `.ctr.jsonl` | `redactions > 0` on a fixture carrying a planted key; `derived_from == parent sha`; **and the parent's `sha` and `mtime` are unchanged** — the proof the original stayed (R9) |
| `crash-recover` | quarantine copy + new store; mutation only via `rebind` | quarantine `_MANIFEST.sha256.json`, `truncated_at_line`, and a recovered `n_turns` **below** the damaged store's claim. A recovery that reports no loss on a truncated store is a **bug, not a success** |

Two gates deserve emphasis: `anonymize` proves the original is untouched by re-hashing it *after* the
run, and `crash-recover` treats a loss-free recovery of a truncated store as a failure. Both are
anti-placation gates (`docs/SCAR_PLACATION.md`) — designed so a plausible "it worked" cannot pass.

---

## 9. Open questions for stage 3 (CONSENSUS)

Named, not silently decided:

1. **Sidecar HMAC.** I chose sha-only for portability (§3.6). A peer wanting install-bound transcripts
   would add an HMAC and lose the cold-machine open. Contested on purpose.
2. **Cross-family `diff` semantics.** The closed `role` enum makes it *possible*; whether a
   cross-family diff should compare `text` at all, or only structure, is unsettled.
3. **`scan` on a clock.** Deliberately not proposed (§7). If it ever lands it is a new scheduled task
   and needs Keith's word, not an agent's.
4. **`builds/cdeck` gitlink** (§2.1) — a repo blocker owned by CCr, not by this suite, but it bounds
   where the `migrate` gate can run.

---

## 10. Provenance

| item | value |
|---|---|
| Stage | MOTIF 2 (ARCH). No BUILD. |
| Lane / model | Cursor Cloud Agent · `claude-opus-5-thinking-high` (Composer 2.5 / Auto refused) |
| Clone | `github.com/keithbbf-gif/cosmos` default branch @ `223a7dd`; no local uncommitted COSMOS read |
| Peeking | `docs/arch/SESSION_TOOLS_ARCH.md` ABSENT in this clone (`git ls-files`) — independent by construction |
| Baseline | `docs/research/SESSION_TOOLS.md` (stage-1, CCr/Grok 4.6, 2026-09-05) |
| ANTHROPIC_OFF | intact — no `claude -p`, no `api.anthropic.com`; this is a Cursor vendor seat per `AGENT_BOUNDARIES.md` item 10 |
| Live tree writes | **none** |
| PRs merged | **none** (#30 #32 #36 #37 #38 untouched) |
| Clocks / schtasks | untouched — no create, no `/delete` |
| Core `:8770` | untouched — not started, not stopped, no route change |
| Twin | `proposals/session_tools_arch.json` (machine-readable; same decisions) |
