# COSMOS surface cluster — adversarial attack

**Critic:** Cursor background agent (not the builder).
**Subject:** `f5/cosmos-core-v1` @ `e9e23ef`.
**Cluster:** `cosmos_service` · `cosmos_mcp` · `cosmos_command` · `cosmos_crucible` · `cosmos.py` · `cosmos_migrate` · `cosmos_tools`.
**Contracts:** `docs/FINAL_ARCHITECTURE.md` (ratified), harvest = Grok critic review (`origin/review/f5-core-grok:docs/REVIEW_F5_CORE_GROK.md`) B1–B7 + M1–M10 (~17 named gaps; ~19 if M8/M10 surface remainders are counted separately). No `docs/*harvest*` file is present on this branch.
**Method:** `PYTHONPATH=/workspace/cosmos`; run every existing `tests/test_*.py` that imports this cluster; then new probes in `attack/test_surface_adversarial.py`. Docstrings are claims. Behavior is evidence. `cosmos/` and existing `tests/` were not modified.

A finding without a repro that runs is an opinion. Every BLOCKER/MAJOR/MINOR below names a test that **PASSED HERE**, meaning the broken observation was measured.

```
PYTHONPATH=/workspace/cosmos python3 -m pytest -v attack/test_surface_adversarial.py
# 37 passed in ~7s (this container, 2026-08-23)
```

---

## 1. Existing suites HERE vs NATIVE-DEMO-REQUIRED

`PYTHONPATH=/workspace/cosmos python3 -m pytest -v` on the eight suites that touch this cluster:

| suite | HERE | NATIVE-DEMO-REQUIRED / native-only | builder's `docs/V1_SUITE_RESULTS.md` |
|---|---|---|---|
| `tests/test_command.py` | **PASS** (14 checks) | none | PASS |
| `tests/test_tools.py` | **PASS** (18 checks) | none | PASS |
| `tests/test_migrate_health.py` | **PASS** (8 checks, **synthetic**) | incumbent `V:\Ai\BTS_MESH\TOOLS_REGISTRY.json` absent. Suite labels this `[SANDBOX - native is the measurement]`. **Not** marked `NATIVE-DEMO-REQUIRED`. The 143-tool measurement did not run. | PASS, claimed `MEASURED: 143 tools` |
| `tests/test_v1.py` | **PASS** (18 checks) | none | PASS |
| `tests/test_wave3.py` | **FAIL** `FileNotFoundError: [Errno 2] No such file or directory: 'py'` at `cosmos_runner.run_tree_killed` | Windows `py` launcher. **Not** marked `NATIVE-DEMO-REQUIRED`. The suite dies **before** the crucible + `/health` `/spend` `/tools` `/events` `/command` `/crucible` checks. Those surface checks were **not executed HERE**. | PASS (31 checks) native Windows |
| `tests/test_wave4.py` | **PASS** (16 checks) | none | PASS |
| `tests/test_tls.py` | **PASS** (3 checks, **real HTTPS**) | `cryptography` is installed here, so the `NATIVE-DEMO note - install 'cryptography'` skip branch was **not** taken. TLS is proven on this runner. | PASS |
| `tests/test_port_plan.py` | **FAIL** (3 of 21 checks) | none. `existing_cosmos_modules()` globs `tests/cosmos_*.py` and `SPIKE_F5_*`. Modules live in `cosmos/`. Successor-exists-on-disk is **test-layout theater**. | PASS |

Bare `pytest tests/` without `PYTHONPATH` still fails collection (`No module named 'cosmos_*'`). That is unchanged from the harvest. A peer who types `pytest` does not get the native-PASS claim.

Transcript: `/opt/cursor/artifacts/surface_pytest_here.txt`.

---

## 2. Harvest gaps that touch this cluster

The harvest is the Grok review of an earlier cut (`2651e20`). The builder tagged later commits as having closed B1/B2/B3/B6/B7/M2/M3/M4/M5/M6. Verified **only** where the gap is a surface-cluster fact:

| id | harvest claim | touches | HERE |
|---|---|---|---|
| **B1** | `Kernel()` appends on `cosmos status` | `cosmos.py` | **CLOSED** for `status`/`audit` (`read_only=True`; no extra ledger events). `serve` still boots a writer and still lets `Service` invent the bearer token. Repro: `test_closed_B1_cli_status_is_read_only` (PASS). |
| **B2** | `claim_next` double-claim | no claim on the API | **N/A internally**. The product surface still cannot claim or done. See M8. |
| **B3** | no ingress; mount write is already real | `POST /api/v1/crucible` | **OPEN**. Remote crucible does not go through `IngressGate`, does not hash sources, and `paths.role("docs", s)` lets an absolute path replace the docs root. Repro: `test_repro_remote_crucible_is_print_stub_and_path_escapes`. |
| **B4** | workers import around kernel primitives | MCP / service call `k.sched.submit` directly | **OPEN at the seam**. Submit on HTTP/MCP/command never presents a fencing token, expected input hashes, or a spend reservation. |
| **B5** | no `OPEN_CONTEXT` | not this cluster | N/A |
| **B6** | unsigned leases | audit surfaces | leftover is **M10** (below) |
| **B7** | expired credit ALLOWED | every submit seam | **OPEN on this cluster.** `SpendGate` may deny in isolation; `POST /jobs`, `cosmos_submit`, and `Commander.handle("submit …")` never call it. Repro: `test_repro_surface_submit_ignores_expired_spend_budget`. |
| **M1** | `TAKEOVER` dead | lock | N/A |
| **M2** | silent restamp | kernel/install | N/A (CLI `install` delegates) |
| **M3** | `GET /rails` 200 + empty matrix | `cosmos_service` | **CLOSED.** `k.registry = None` → HTTP 503 `REGISTRY_NOT_COMPOSED`. Repro: `test_closed_M3_rails_uncomposed_is_503_not_empty_matrix`. |
| **M4** | unfenced commit | lock | N/A |
| **M5** | no runner / `py` | wave3 only | wave3 **FAIL HERE** on `py`. Remote crucible does not invoke the runner or `Crucible`. |
| **M6** | DOM is a sort key | rails | N/A |
| **M7** | backup not a job type | CLI `backup` | N/A as a surface-cluster close |
| **M8** | HTTP surface is not the product | service + CLI | **OPEN** (TLS and `--remote` landed; token invention, missing verbs, stub crucible remain). |
| **M9** | ledger not framed/CAS | ledger | N/A |
| **M10** | audit hard-codes resource `"tree"` | command + HTTP + MCP | **OPEN.** A live lease on `mailbox` reports `leases_live == 0` on every surface. Repro: `test_repro_M10_audit_hardcodes_tree_on_every_surface`. |

Architecture Decision 7 (“one versioned API; KDash / voice / mobile are clients”) is a file with routes, not a product: clients cannot claim, done, lease, mail, ingress, or spend-reserve over that API (`test_repro_no_lease_or_mail_or_claim_http_endpoints`).

---

## 3. Ranked findings

### BLOCKER

**S-B1 — Remote crucible is a print stub that path-escapes.**
Decision 7 + Keith “remote access should include ability to run Crucible” + B3 ingress + Decision 2 (mount write is not authority).

`POST /api/v1/crucible` resolves `sources` with `kernel.paths.role("docs", s)`. On POSIX, `joinpath("docs", "/etc/passwd")` is `/etc/passwd`. It then submits `argv:["py","-3.14","-c","print('crucible round queued')"]`, ledgers `CRUCIBLE_REQUESTED`, and never calls `Crucible.build_packet` / `run_round`. Completeness is not asserted. A lying or absolute path is reflected in the 201 body.

```
PYTHONPATH=cosmos python3 -m pytest -v attack/test_surface_adversarial.py::test_repro_remote_crucible_is_print_stub_and_path_escapes
# PASSED HERE. 201, sources contain /etc/passwd, command contains "crucible round queued",
# CRUCIBLE_PACKET_BUILT absent.
```

**S-B2 — The never-delete canon is the first word only. The runner-facing payload is free.**
`cosmos_command` docstring: “There are NO destructive verbs in the grammar, and none can be added by accident: FORBIDDEN is checked FIRST.” `submit high rm -rf /` and `submit critical delete everything` return `ok: True`, ledger `COMMAND_HANDLED` with `ok=true`, and create real scheduler jobs.

```
PYTHONPATH=cosmos python3 -m pytest -v attack/test_surface_adversarial.py::test_repro_command_forbidden_is_verb_only_payload_is_free
# PASSED HERE. Manifests contain "rm -rf / --no-preserve-root" and "delete everything".
# Control: first-word "delete everything" is still REFUSED.
```

Voice/frontend is this seam (Decision 7). The fence does not fence the thing the runner will execute.

**S-B3 — Spend expiry is not enforced at any product call site.**
Harvest B7 was closed on `SpendGate.guarded_call`. Architecture: “the breaker lives in the caller.” The callers on this cluster are HTTP `POST /jobs`, MCP `cosmos_submit`, and `Commander._submit`. None of them call the breaker. An expired budget (`expires_epoch=1.0`) still admits a 201.

```
PYTHONPATH=cosmos python3 -m pytest -v attack/test_surface_adversarial.py::test_repro_surface_submit_ignores_expired_spend_budget
# PASSED HERE. 201 + job in scheduler state + no SPEND_DENIED event.
```

Same hole on MCP: `test_repro_mcp_submit_bypasses_spend_and_has_no_claim`.

**S-B4 — Handler exceptions drop the TCP connection. Typed ledger refusals die at the socket.**
H2: torn/unparseable REFUSES by kind. `GET /api/v1/events?since_seq=abc` raises `ValueError` in `do_GET`. `GET /api/v1/events` on a torn authority file raises `LedgerError [TORN]`. `ThreadingHTTPServer` prints a traceback and **closes without a status line**. The client sees `RemoteDisconnected`, not `{"error":"TORN"}`.

```
PYTHONPATH=cosmos python3 -m pytest -v \
  attack/test_surface_adversarial.py::test_repro_events_bad_since_seq_drops_the_connection \
  attack/test_surface_adversarial.py::test_repro_events_torn_ledger_drops_the_connection
# BOTH PASSED HERE (RemoteDisconnected / URLError, no JSON envelope).
```

A mount that tears one line takes the live-backend primitive (`/events` is documented as “THE LIVE-BACKEND PRIMITIVE”) off the air for that request and hides the kind.

---

### MAJOR

**S-M1 — Empty / whitespace `api_token.txt` is an open door. Missing file is invented.**
Harvest M8. Kernel refuses to invent `install_key.bin`. `Service.__init__` writes `api_token.txt` with `secrets.token_urlsafe(24)` if absent (mode group/other-readable HERE). If the file exists and is whitespace, `token == ""` and `Authorization: Bearer ` authenticates as 200.

```
PYTHONPATH=cosmos python3 -m pytest -v \
  attack/test_surface_adversarial.py::test_repro_M8_service_invents_api_token_if_missing \
  attack/test_surface_adversarial.py::test_repro_empty_token_file_is_an_open_door
# BOTH PASSED HERE.
```

**S-M2 — MCP is not a safe stdio adapter.**
- Non-object JSON-RPC (`[1,2]`, `null`, `42`) raises `AttributeError` in `handle()` — `serve_stdio` dies. Not `-32600`.
- A request (`id` present) with method `initialized` returns `None` (client hang).
- `cosmos_command` `REFUSED` becomes JSON-RPC `-32603` wrapping `CommandError`, not a tool-level kind. Delete and a kernel crash are the same code.
- Tools list has submit/jobs/status/audit/health/command/events. No claim, no done.

```
PYTHONPATH=cosmos python3 -m pytest -v \
  attack/test_surface_adversarial.py::test_repro_mcp_non_object_request_crashes_the_handler \
  attack/test_surface_adversarial.py::test_repro_mcp_initialized_with_id_is_dropped \
  attack/test_surface_adversarial.py::test_repro_mcp_command_refusal_is_internal_error \
  attack/test_surface_adversarial.py::test_repro_mcp_submit_bypasses_spend_and_has_no_claim
# ALL PASSED HERE.
```

**S-M3 — Crucible collapses four-state absence and hides disagreement.**
Ratified H2 / mail contract: missing ≠ empty ≠ unreadable. `build_packet` raises `EMPTY_SOURCE` for a missing path **and** a zero-byte file. A directory (`exists` and `st_size > 0`) raises untyped `IsADirectoryError`. Merge groups by topic string only: opposite verdicts on `lease expiry` land under `UNANIMOUS`. The advertised `CONTESTED` bucket does not exist. The advertised `ID: FAMILY-n` line format is never parsed. An empty critic return is a successful family (`families==2`, no warning). Concurrent rounds share `_PACKET.md` / `RETURN_{name}.md` and measure `PACKET_INCOMPLETE` or last-writer-wins. `extended()` is not used (C-60; Windows MAX_PATH is NATIVE-DEMO-REQUIRED).

```
PYTHONPATH=cosmos python3 -m pytest -v \
  attack/test_surface_adversarial.py::test_repro_crucible_missing_and_empty_are_the_same_kind \
  attack/test_surface_adversarial.py::test_repro_crucible_directory_source_is_untyped \
  attack/test_surface_adversarial.py::test_repro_crucible_merge_treats_topic_mention_as_agreement \
  attack/test_surface_adversarial.py::test_repro_crucible_id_line_format_is_dead_code \
  attack/test_surface_adversarial.py::test_repro_crucible_concurrent_rounds_clobber_packet \
  attack/test_surface_adversarial.py::test_repro_crucible_empty_critic_return_is_not_a_finding \
  attack/test_surface_adversarial.py::test_repro_crucible_max_path_does_not_use_extended
# ALL PASSED HERE.
```

The July-forge lesson the module quotes (“returns land on disk before anyone reasons; a dead critic is a FINDING; nothing hides disagreement”) is not the behavior.

**S-M4 — `ToolContracts.declare` is check-then-append. Overlap double-declares.**
No `expect_head_seq`. Eight threads on one name land multiple `TOOL_DECLARED` events; `DUPLICATE` does not fire. Empty name `""` and empty disposition reason are legal. Kernel composes registry/spend/validator and **not** tools; `GET /tools` constructs a fresh `ToolContracts(kernel.ledger)` per request, so in-memory checks never survive the wire.

```
PYTHONPATH=cosmos python3 -m pytest -v \
  attack/test_surface_adversarial.py::test_repro_tools_declare_race_double_declaration \
  attack/test_surface_adversarial.py::test_repro_tools_empty_name_and_empty_reason_are_legal \
  attack/test_surface_adversarial.py::test_repro_tools_not_composed_on_kernel
# ALL PASSED HERE.
```

**S-M5 — Migrate is not a measured backlog with one decision record.**
- Missing registry → untyped `FileNotFoundError`. Empty file → untyped `JSONDecodeError`. `[]` → success, `total=0`. Missing ≠ empty ≠ empty-list is not typed.
- Re-ingest appends another `TOOL_DISPOSITION` every time (`n2 > n1`). Counts stay stable; the ledger is not exactly-once.
- `_try_disposition` swallows every `ToolsError`. `SHRUGGED` is indistinguishable from “tool absent.”
- Two authorities: `REPLACED_BY_*` (8 names) vs `cosmos_port_plan.PORT_DECISIONS` (33 rulings). `bts_cursor` is `REPLACED` in migrate and `ADAPTED` in the port plan. Architecture: one recorded decision, never drifted.

```
PYTHONPATH=cosmos python3 -m pytest -v \
  attack/test_surface_adversarial.py::test_repro_migrate_missing_vs_empty_vs_empty_list \
  attack/test_surface_adversarial.py::test_repro_migrate_reingest_reappends_dispositions \
  attack/test_surface_adversarial.py::test_repro_migrate_swallows_all_disposition_errors \
  attack/test_surface_adversarial.py::test_repro_migrate_and_port_plan_are_two_authorities
# ALL PASSED HERE.
```

HERE, migrate never saw the 143-tool incumbent file. The builder’s “MEASURED: 143” is a native-machine claim, unmarked as `NATIVE-DEMO-REQUIRED`.

**S-M6 — Harvest M8/M10 remain on every surface.**
- No HTTP `/leases` `/mail` `/claim` `/backup` `/ingress` (all 404).
- Audit `leases_live` counts only `("tree",)` on command, `GET /audit`, and MCP `cosmos_audit`.
- CLI `serve` still writes; CLI has no `crucible`/`migrate`/`command`/`tools`/`mcp` verbs. Unknown flags **do** refuse (argparse; `test_closed_cli_unknown_flag_refuses`).

```
PYTHONPATH=cosmos python3 -m pytest -v \
  attack/test_surface_adversarial.py::test_repro_M10_audit_hardcodes_tree_on_every_surface \
  attack/test_surface_adversarial.py::test_repro_no_lease_or_mail_or_claim_http_endpoints \
  attack/test_surface_adversarial.py::test_repro_cli_has_no_crucible_migrate_or_command_verbs
# ALL PASSED HERE.
```

**S-M7 — Concurrent `POST /jobs` has no idempotency key.**
20 overlapping identical posts: chain still verifies (B1 ledger lock holds), 20 distinct job ids. Exactly-once under overlap is not a property of the product surface.

```
PYTHONPATH=cosmos python3 -m pytest -v attack/test_surface_adversarial.py::test_repro_concurrent_job_posts_have_no_idempotency_key
# PASSED HERE. 20/20 unique ids, ledger verifies.
```

This is not a chain tear. It is the absence of the exactly-once contract the harvest asked the suites to prove.

---

### MINOR

**S-m1 — `/api/v1/events` is `startswith`, not an exact route.**
`GET /api/v1/events_FORGED` and `/api/v1/eventss` return 200 + the tail. Extra surface, no 404.

```
PYTHONPATH=cosmos python3 -m pytest -v attack/test_surface_adversarial.py::test_repro_events_prefix_is_not_an_exact_route
# PASSED HERE.
```

**S-m2 — Unicode / ZWSP `delete` is `UNKNOWN_COMMAND`, not `REFUSED`.**
Fullwidth `ｄｅｌｅｔｅ` and `de\u200blete` miss the ascii `FORBIDDEN` set. No current handler would fire either, so this is a fence that only fences the spelling it knows.

```
PYTHONPATH=cosmos python3 -m pytest -v attack/test_surface_adversarial.py::test_repro_command_unicode_homoglyph_and_zwsp
# PASSED HERE.
```

**S-m3 — Empty command text is `UNKNOWN_COMMAND` with verb `''`.**
`""`, whitespace, `None` are the same kind. No `EMPTY_COMMAND`. `test_repro_command_empty_and_missing_vs_blank`.

**S-m4 — Crucible MAX_PATH / `extended()`.**
Module never imports `extended`. Linux will read a long path that exists. The C-60 WinError-3 clothing is **NATIVE-DEMO-REQUIRED**. `test_repro_crucible_max_path_does_not_use_extended` only proves the call-site gap.

**S-m5 — `test_port_plan` successor-exists check looks in the wrong directory.**
Not a `cosmos_tools` bug. The suite that claims “every REPLACED successor EXISTS on disk” cannot see `cosmos/cosmos_*.py`. HERE: FAIL. Native PASS was an environment claim.

---

## 4. What is actually closed on this cluster

| check | evidence |
|---|---|
| M3 `/rails` composition fault is 503 | `test_closed_M3_rails_uncomposed_is_503_not_empty_matrix` |
| B1 CLI `status`/`audit` do not append | `test_closed_B1_cli_status_is_read_only` |
| CLI unknown flags refuse (exit 2) | `test_closed_cli_unknown_flag_refuses` |
| ASCII `FORBIDDEN` verbs still refuse | `test_closed_command_every_ascii_forbidden_verb` |
| TLS self-signed round-trip | `tests/test_tls.py` PASS HERE (`cryptography` present) |
| Ledger lock holds under 20 concurrent HTTP submits | `test_repro_concurrent_job_posts_have_no_idempotency_key` (chain verifies) |

Closed is not Core. The product seams (HTTP, MCP, voice, remote crucible, migrate) still admit work the architecture said Core must refuse: expired spend, unfenced submit, mount-escaped sources, a delete payload, a torn ledger with no typed HTTP kind.

---

## 5. Architecture contract, module by module

| module | ratified job | what shipped |
|---|---|---|
| `cosmos_service` | one versioned API; every client; served + authorized; panel age on every response | stdlib `ThreadingHTTPServer`; bearer invented on boot; `served_at` present; no claim/done/lease/mail/ingress/spend; `/events` and `/crucible` are the load-bearing holes above |
| `cosmos_mcp` | “one protocol adapter, many clients, every op delegating to the real thing” | stdio JSON-RPC; no auth (acceptable for stdio); crashes on non-objects; command refusals are `-32603`; no claim/done |
| `cosmos_command` | text in, kernel actions out; no destructive verbs; unknown never guessed | grammar holds for first-word unknown/forbidden; payload of `submit` is unsanitized kernel work |
| `cosmos_crucible` | completeness-asserted packet; disk-first returns; dead critic is a finding; disagreement visible | packet read-back is real; missing=empty; merge averages by topic mention; remote path does not call this module |
| `cosmos.py` | peer on a cold machine: install/boot/status/submit/audit/backup/rehearse/serve | those verbs exist; unknown flags refuse; status is read-only; serve invents auth; no crucible/migrate/command/MCP |
| `cosmos_migrate` | “139 tools” becomes a queryable worklist; UNDECIDED is counted | UNDECIDED is counted on a synthetic 2-tool list HERE; two decision authorities; re-ingest is not exactly-once |
| `cosmos_tools` | architecture-wins disposition, dated check, registration ≠ capability | sequential suite holds; overlap double-declares; not composed on `Kernel` |

Honest risks the architecture already carried (“~135 tool contracts still UNKNOWN”) are still true. `PORT_DECISIONS` covers 33 names. Native 143-tool ingest did not run in this container.

---

## 6. How to re-run

```bash
# existing cluster suites (expect wave3 FAIL on Linux, port_plan FAIL on this layout)
PYTHONPATH=cosmos python3 -m pytest -v \
  tests/test_command.py tests/test_tools.py tests/test_migrate_health.py \
  tests/test_v1.py tests/test_wave3.py tests/test_wave4.py \
  tests/test_tls.py tests/test_port_plan.py

# adversarial probes (37 passed HERE; a PASS is a landed attack)
PYTHONPATH=cosmos python3 -m pytest -v attack/test_surface_adversarial.py
```

`NATIVE-DEMO-REQUIRED` on this cluster, honestly labeled:

1. Incumbent `TOOLS_REGISTRY.json` at `V:\Ai\BTS_MESH\` — 143-tool measurement (suite says SANDBOX, not the required tag).
2. Windows `py` launcher — `test_wave3` runner drain (unmarked; aborts surface checks).
3. Crucible / backup walks past MAX_PATH 260 — Linux cannot close C-60; `extended()` is unused in crucible regardless.
4. TLS skip branch — not taken HERE because `cryptography` is present.

Marking a skip as `OK` (tls crypto-absent path, paths MAX_PATH off-Windows in other clusters) is the same defect class the harvest named. On this cluster the tls skip was not exercised.
