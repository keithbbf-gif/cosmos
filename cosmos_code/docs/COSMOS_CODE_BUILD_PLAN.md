# COSMOS CODE v3 — BUILD PLAN (implementation proposal)

**Author:** Hermes (reviewer seat) · **Date:** 2026-09-29 CT
**Status:** PROPOSE-ONLY. This is the coding plan for `COSMOS_CODE_ARCH.md` (same date, Scratch). It proposes; CCr disposes. All work lands Gitur-first (branch off `origin/main` → PR → Judge KEEP → CCr merge). No straight-to-tree, no second live tree, no second ledger.
**Target repos:** `keithbbf-gif/cosmos` (engine + doors + gates). Board assets (`V:/A/COSMOS_Harness/…`) are read/cited, not relocated.
**Companion:** architecture = `V:/Hermes/Sessions/Scratch/COSMOS_CODE_ARCH.md` — read that first; this file assumes it.

---

## 0. Rules this build obeys (all tested, not promised)

| # | Rule | Enforced by |
|---|---|---|
| 1 | One engine. No per-door runners, no per-language forks. | Phase 1 deletes 3 `_summon_*.py`; parity harness proves identical grades |
| 2 | Fail-closed everywhere: missing key/binary/toolchain/layer = named refuse, never a fake call or silent-green | `Refuse` exception family + doctor |
| 3 | Model-visible ⟺ logged | `session.py` invariant test |
| 4 | Draft consumes Shot-1 IR or no model call happens | `test_draft_consumes_ir` |
| 5 | Workers propose; publish = Gitur pipe only | engine has no publish-to-live verb at all |
| 6 | One BAKEOFF70 ledger; grade = CPU evidence, HTTP ≠ applied | rescore script + contract-first grader |
| 7 | Python 3.12+ (box runs 3.14), stdlib-first; TOML via stdlib `tomllib`; subprocess for doors; **no Node, no Cordis, no LangGraph** | dependency gate test |
| 8 | Windows-first (the box is the host): `creationflags=0x08000000` on spawns, forward-slash-native paths, no POSIX-only calls | tests run on the box |

---

## 1. Target tree (end state)

```
cosmos/                                # keithbbf-gif/cosmos
  cosmos_code/                         # NEW — the one engine
    __init__.py
    contracts.py                       # every frozen dataclass (§2)
    refuse.py                          # Refuse + reasons
    doors/
      __init__.py
      spec.py                          # DoorSpec schema + loader + validator
      registry.py                      # load all TOMLs, family×door join, pick()
      summon.py                        # THE one dispatch path
      negotiate.py                     # native|carried|none per layer
      doctor.py                        # door probe: bound/unbound/dead + toolchain probe
      specs/                           # the doors as data
        opencode.toml  pi.toml  dsh.toml  codex.toml  openrouter.toml
        vertex.toml  copilot.toml  cosmos-code.toml  antigravity.toml
        zcode.toml  grok-gitur.toml
    session.py                         # session log v1 (append-only)
    quality/
      define.py        # OracleSpec gate (imports scaffold spine)
      context_pack.py  # map_hash + repo map + ACI + oracle stub
      plan.py          # symbol∩hunk gate
      draft.py         # apply_patch writer, attempt workspace
      ladder.py        # D0–D6 + GateFailure/GateUnavailable
      checkers/        # CheckerPacks (§7)
        python.toml  cpp.toml  csharp.toml  jsts.toml
        detect.py    # worktree language detection
      repair.py  escalate.py  evidence.py   # DoneBundle close
    mcp/
      server.py                        # exposes jailed tools via MCP (Phase 4.5)
    cli.py                             # argparse: run / probe / doctor / rescore / tui
    tui/
      app.py                           # Textual shell (last phase)
  work_orders/ccr/
    rescore_bakeoff.py                 # Phase 0 script (transitional, then moves into engine)
    (deleted in Phase 1:) _summon_opencode.py, _summon_copilot.py
  tests/cosmos_code/                   # binding tests live WITH the engine
```

The scaffold spine (`V:/A/COSMOS_Harness/code/cosmos_code_scaffold/cosmos_code/`) is **imported, not copied**: a path shim resolves it (same pattern as `hero_unify.CODE_ROOT`); Phase 3 proposes absorbing it into `cosmos_code/` via one Gitur PR (files move verbatim, 19 tests travel, git history notes the source). Q1–Q5 stay green throughout.

---

## 2. Contracts (`contracts.py`) — write these first, everything hangs off them

```python
@dataclass(frozen=True)
class OutputContract:                 # grader input — kills GRADER-CONTRADICTION
    first_line: str                   # "NONE|diff --git" | "python" | "KEEP|DROP|NONE|HOLD|UNMEASURED" | "ITEM|NONE"
    what: str                         # text | python | no_prose
    ping: bool = False                # ping grading: line1 NONE + line2 HERO_OK <slug>

@dataclass(frozen=True)
class LayerBind:                      # per HERO layer
    state: str                        # native | carried | none
    transfer: dict | None = None      # e.g. {"file":"AGENTS.md","from":"WRAP.md","only_if_absent":True}

@dataclass(frozen=True)
class DoorSpec:
    id: str; family: str; kind: str; strength: str          # strong|weak|none
    binds: dict[str, LayerBind]                             # l1..l8
    argv: tuple[str, ...]; env: dict[str, str]
    first_line: str; grade: str                             # "worktree" | "filed_text"
    session_mode: str; home: str
    model_flag: str | None; prefill_none: bool = False      # quirk fields (§4.3)
    reasoning_flags: bool = False; max_tokens_floor: int = 0
    keep_under_tokens: int | None = None                    # xAI 200k family flag

# Reused verbatim from the scaffold (do not redefine):
#   OracleSpec{cmd,cwd,expect_fail_pre,expect_pass_post,property_id}   verify/oracle.py
#   DoneBundle{diff_hash,oracle_id,oracle_log_hash,pack_hash,cmd_hash} verify/stop_gate.py
#   GateFailure{axis,locus,log_hash,cmd_hash}                          (add to ladder.py)
@dataclass(frozen=True)
class GateUnavailable:                # NEW — a gate that cannot run is not a pass
    axis: str; reason: str
```

`Refuse(reason, detail)` exception; every refuse prints a named reason string (the scar vocabulary already in BAKEOFF70: `NO_KEY`, `NO_BINARY`, `NOT_PINNED`, `PACK_INCOMPLETE`, `MAX_LE_ZERO`, `NO_CONTEXT`, `GATE_UNAVAILABLE`).

---

## 3. Phase 0 — grader honesty (≈half day, 1 PR)

**Files:** modify `work_orders/ccr/_summon_or_hero.py`; add `work_orders/ccr/rescore_bakeoff.py`.

1. Add `OutputContract` to `_summon_or_hero.py` (temporary home; moves to `cosmos_code/contracts.py` in Phase 1).
2. `grade_pack(pack, mouth, model_returned, contract)`:
   - `l1_role`/`l8_mission`: `contract.ping` → ping shape; `what=="text"` → NONE-first legal; `what=="python"` → `_py_first(first)`.
   - Everything else (l2–l7 wire checks) unchanged.
3. Mission DUDs gain `output.what` plumbed through (already in the DUD schema §3 of HARNESS.md — read it, don't invent).
4. `rescore_bakeoff.py`: walks `BAKEOFF70.jsonl`, re-grades each row from its pack dir under the row's true contract, prints per-set seat counts. Writes `BAKEOFF70_RESCORE.jsonl` (append-only, never edits the original).

**Binding tests:** `test_none_first_passes_text_contract` · `test_python_first_fails_text_contract` · `test_ping_contract` · `test_applied_reachable_all_contracts`.
**Exit:** `applied=true` reachable for every set; one seat count printed; SEATED-BY-EVIDENCE rows resolved to a real grade or an explicit `contract_violation` scar.

---

## 4. Phase 1 — DoorSpec kernel (1–2 days, 2 PRs)

### 4.1 `doors/spec.py` — schema + loader
`tomllib` load → validate: every layer `l1..l8` present with state ∈ {native,carried,none}; `strength` ∈ {strong,weak,none}; argv is a tuple; env values may reference `{home}`, `{worktree}`, `{model}`, `{task}`, `{slug}` placeholders. **Bad row = load-time refuse with the file and field named** (fail-loud, the dsh rule).

### 4.2 `doors/negotiate.py` — PACK_BY_HARNESS compiled
```python
def negotiate(spec: DoorSpec, duds: dict) -> Wire:
    """Every layer must be native (door binds it) or carried (host carries it).
    carried("l4_wrapper") -> wrapper bytes go in the prompt
    carried("l6_tools")   -> host emulates the write tool, host-side PathJail
    carried("l7_enviro")  -> host files the reply through PathJail
    strong door           -> forbid restuffing a native layer (pack does not re-send it)
    unbound layer         -> Refuse("LAYER_UNBOUND", layer)"""
```

### 4.3 `doors/summon.py` — the one code path (behavior = union of the nine runners, nothing more)
```python
def summon(spec, duds, task, *, rail, session=None, ping=None, max_loops=6,
           routing=None, reasoning=None, max_tokens=None) -> SummonResult
```
Steps, in order: `require_duds` → pin check (`model_refused()` from the rail) → key/env preflight (`Refuse("NO_KEY")` absent — never a degenerate chat call) → `negotiate` → Size law at wire time (`MAX = window − (cached+prompts) − 0.20×window`; `≤0` refuse) → session header → spawn (subprocess argv for CLI doors / `rail.dispatch` for OR) → tool loop ≤ `max_loops` with `jail_write` (existing `hero_unify.jail_write`) → collect → return `(mouth, wrote, session, rec)`.
Quirks as spec fields (all currently hardcoded in `_summon_or_hero.py`): `prefill_none`, `reasoning_flags`, `max_tokens_floor=256` (reasoning models), 404-tool_choice retry, `routing="off"` default for `:free`, `model_flag="-m openrouter/{slug}"`.

### 4.4 First three specs (convert in this order — clearest BIND rows)

```toml
# specs/opencode.toml
id="opencode" family="any-or" kind="coding" strength="strong"
[binds]
l1_role="native" l2_model="native" l3_harness="native"
l4_wrapper="file" l5_skills="file" l6_tools="native" l7_enviro="native" l8_mission="argv"
[spawn]
argv=["opencode","run","--dir","{worktree}","-m","openrouter/{slug}","--","{task}"]
env={ OPENCODE_CONFIG="{home}/opencode.json", OPENCODE_CONFIG_DIR="{home}", OPENCODE_DATA_DIR="{home}/data" }
wrapper_transfer={ file="AGENTS.md", from="WRAP.md", only_if_absent=true }
[probe] first_line="NONE|diff --git" grade="worktree"
[session] mode="one-shot" home="{live}/work/opencode-home"
```
`copilot.toml` (authenticated ping+fizz on `auto`; model enumeration owed — Phase 4) · `vertex.toml` (weak door: `l4_wrapper="prompt"`, `l6_tools="none"`, `l7_enviro="carried"`, `grade="filed_text"`).

Then port the remaining BIND rows from `hero_unify.py` (pi, dsh, codex, openrouter, cosmos-code) + new (antigravity, zcode, grok-gitur) — each is a TOML file + one parity run, no new code.

### 4.5 Parity harness (the delete license)
`tests/cosmos_code/test_parity.py`: re-run **10 known seated models** through `summon()` with their existing packs; grades must match their stored BAKEOFF70 rows (model, first_line, applied-equivalent layers). Only after parity: delete `_summon_opencode.py` + `_summon_copilot.py` (one PR per door, per one-job-one-PR).

**Exit:** 3 runners gone, parity green, adding a door = a TOML file + parity run.

---

## 5. Phase 2 — session log v1 (1–2 days, 1 PR)

**Files:** `cosmos_code/session.py`.

Schema (JSONL, append-only, one file per attempt; human-readable on purpose):
```jsonc
{"v":1,"ev":"session/start","door":"opencode","model":"...","duds_sha":"...","prefix_head":"<sha256>"}
{"ev":"system/message","bytes":"<WRAP.md>","sha":"..."}     // frozen head
{"ev":"user/message","bytes":"<TASK.md>","sha":"..."}
{"ev":"assistant/attempt","http":429,"note":"..."}          // failures NEVER enter model history
{"ev":"assistant/message","bytes":"..."}
{"ev":"tool/call","tool":"write","args_sha":"..."}  {"ev":"tool/result","detail":"wrote fib.py"}
{"ev":"gate/result","axis":"D2","locus":"src/x.py:41","ok":false}
{"ev":"turn/end","cached_tokens":4102,"out_tokens":830,"usage_usd":0.0031}
```
API: `SessionLog.open(path)` · `.append(ev)` (append-only, no rewrite ever) · `.derive_messages() -> list[msg]` (the wire, projected) · `.frozen_head_sha()` · `.compact(summary_text)` = append a `summary` event **after** the frozen head, never splice · `.usage()` (per-turn cached/out/$ for meters + close-rule).

**Binding tests:** `test_derive_equals_wire` (byte-identical to what was sent) · `test_model_visible_logged` (inject a fake provider that records bytes; every request byte reconstructs from the log) · `test_compact_appends_never_splices` · `test_attempt_never_enters_history` · `test_prefix_head_stable_across_turns`.
**Integration:** `summon()` writes the log; `wire.json` becomes a projection of it (one source — kills the LOG_IS_NOT_MODEL / wire-drift scar family). Close-rule inputs (WOMB clear / cache stale / too long) read `.usage()`.
**Exit:** OR door writes v1 logs; cached-tokens per turn visible; cDeck spend meter can read `turn/end` rows.

---

## 6. Phase 3 — quality spine + the three HOLD-closing tests (2–3 days, 2 PRs)

### 6.1 Wire the scaffold as the verify half
Path shim imports `OracleSpec`/`DoneBundle`/`PathJail`/`hooks`/`context_pack` from the scaffold (canonical root, Streams mirror fallback). Absorb into `cosmos/` in one verbatim-move PR (tests travel; Q1–Q5 must stay green in CI on the branch).

### 6.2 New modules (`cosmos_code/quality/`)
`define.py` (oracle gate: nontrivial WO without failing oracle → `Refuse("NO_FAILING_TEST")`) · `context_pack.py` (map_hash = HEAD+WO paths; oracle stub = failing cmd + compressed red stderr; Aider-style map ≤1–2k tokens via tree-sitter) · `plan.py` (plan names symbols+invariants; hunks must intersect symbol set — path-only = refuse) · `draft.py` (apply_patch grammar into the attempt workspace; malformed hunk = reject, no file change) · `ladder.py` (D0–D6 ordered, stop at first hard fail, `GateFailure{axis,locus}` only; D4.5 after spine) · `repair.py` (input = GateFailure only) · `escalate.py` (UncertaintyScore all-fields-logged; critic/dual-lane once) · `evidence.py` (DONE = full DoneBundle or refuse).

### 6.3 The three REVIEW_HOLD-closing tests (each fails if violated)
- `test_draft_consumes_ir` — a draft whose session log lacks `oracle/red` + `plan/bound` events → engine refuses to call the model.
- `test_shot1_trace_exists` — `doctor` replays a session log and verifies plan→draft→gate ordering; missing row = reported gap.
- `test_provider_seam_typed` — a Provider implementing only a name dict fails typecheck (ProviderSpec: `prepare_call`, `normalize_tools`, `fold_usage`).

### 6.4 `cli.py doctor`
One command, two panels: **doors** (binary on PATH? key present? → bound/unbound/dead) and **toolchains** (cmake/dotnet/node/pytest present? → which gates go dark). Prints a table; never guesses; exits nonzero if a *bound* door lacks its key (that's a config error, fail-loud).

**Exit:** all four REVIEW_HOLD fails closed by named tests; `doctor` runs clean on the box.

---

## 7. CheckerPacks — language coverage (1 day, 1 PR; arch §2.6)

`quality/checkers/python.toml` first (backfills the current Python behavior), then `cpp.toml`, `csharp.toml`, `jsts.toml`:

```toml
# checkers/python.toml
[lang] id="python" detect=["*.py","pyproject.toml","requirements*.txt"]
[gates]
D1_lint=["ruff","check","{files}"]        D1_format=["ruff","format","--check","{files}"]
D2_type=["mypy","{files}"]                D3_test=["pytest","-q","{test_files}"]
D4_mutate=["mutmut","run","--paths-to-mutate","{files}"]   # degrade: oracle-only mutate
[symbols] extractor="tree_sitter_python"
```

`detect.py` maps the worktree → packs (a repo can load several; gates run per touched language). **Law:** missing toolchain ⇒ `GateUnavailable(axis, reason)` into the session log + DoneBundle — never silent-green; bakeoff can punish closes on degraded ladders. Probe packs per language for seating (compiled-and-executed FizzBuzz equivalents; the Python `compile_fizz`/fib/math checks stay the Python probe pack).

---

## 8. Phase 4 — native doors + enumeration (≈1 day each, separate PRs)

1. **dsh** — spec: `argv=["dsh.cmd","--profile","headless","{task}"]` (never `.ps1`), `env={DSH_HOME="{live}/work/dsh-home"}`, key `live/config/deepseek_api_key.txt` absent ⇒ `Refuse("NO_KEY")` (open-window handoff per WISHLIST credentialing rule — no bat, no paste in chat). Verified fact from the clone: dsh ships **only** DeepSeek-family LLM adapters (`llm-deepseek*`, `llm-pi-ai`); driving dsh on OR slugs means mounting a custom `ctx.llm` provider plugin — probe it, do not assume it. Smoke ping → FizzBuzz → `DSH` set.
2. **ZCode** — hypothesis until probed: headless/CLI mode + custom OpenAI-protocol provider → OR. Probe first (`zcode --help`, config scan at `V:/A/Z/ZCode`); desktop ADE stays pilot-observation if no headless exists. Honest `UNMEASURED` until then.
3. **AntiGravity** — PING-OK exists (`grav_or_ping.py`); write the spec (`LocalOpenAIAgentConfig` → OR endpoint), BIND row, `AGY` set.
4. **Copilot** — enumerate `--model` names (`copilot.cmd --help` + probe); fill `copilot.toml`.
5. **N1/N2 (independent, cheapest roster win)** — one CCr pin PR (21 slugs + nex twins) → rail admits them → smoke ladder. Zero engine work; blocked only on the pin.

## Phase 4.5 — MCP shelf (optional, 1 day)
`mcp/server.py`: stdio MCP server exposing `jailed_read`, `jailed_write`, `run_oracle`, `wo_status` — once, so every MCP-speaking door (dsh `mcp/`, OpenCode, ZCode, the majors) can use them. Lazy disclosure only (schemas appear when the WO names the tool — the dsh in-scope rule and our CORE_REVEAL law agree).

---

## 9. Phase 5 — the proof (run, not code)

`cosmos_code bakeoff arm B vs A`: Sonnet 5 + COSMOS CODE vs Sonnet 5 + Claude Code, fixed ≥20-task pack (BAKEOFF_RUBRIC.md shape), metrics: pass_rate, false_done, incidents, tokens/$, PASS-only quality (0–10), **ungated_retry_rate**. Plus `union_count.py`: seats-per-door union vs each single-door competitor, from BAKEOFF70. Report the inequalities honestly — they hold or the docs say they don't.

---

## 10. Work-order decomposition (drop-ready, one job one PR each)

| WO | Branch | Job | Gate |
|---|---|---|---|
| 1 | `ccr/grader-contract` | Phase 0 grader + rescore | rescore prints one count |
| 2 | `ccr/doors-kernel` | contracts + spec/registry/negotiate/summon + opencode.toml | parity: opencode seats identical |
| 3 | `ccr/doors-convert` | copilot + vertex specs; delete 2 runners | parity green |
| 4 | `ccr/session-v1` | session.py + invariant tests + summon integration | derive≡wire test |
| 5 | `ccr/quality-spine` | quality/* + 3 HOLD tests + doctor | 3 tests fail-if-violated proven |
| 6 | `ccr/checkerpaks` | 4 language packs + detect + GateUnavailable | degraded-ladder visible |
| 7 | `ccr/door-dsh` (+ key) | dsh spec + DSH set | smoke→fizz rows |
| 8 | `ccr/door-agy` / `ccr/copilot-enum` / `ccr/zcode-probe` | per-door | BIND + rows |
| 9 | `ccr/pin-n1n2` (CCr) | rail pins | smoke ladder |
| 10 | `ccr/mcp-shelf` | MCP server | lazy disclosure test |
| 11 | `ccr/bakeoff-proof` | arm runner + union count | rubric report |

---

## 11. Honest gaps / risks

1. Nothing here is built yet — this is a proposal; the only green code is the pre-existing scaffold (19 tests).
2. `grade_pack` change touches the live seating SOP — CCr's call to land WO-1; rescore must run before any new seat rows are trusted.
3. dsh-on-OR is unproven (only DeepSeek-family adapters ship); until probed, the dsh door = DS key or nothing.
4. ZCode headless is a hypothesis; AntiGravity runner is unwritten; Copilot models unknown.
5. Mutate tooling quality varies sharply by language (mull/Stryker vs mutmut) — D4.5 may degrade to oracle-mutate outside Python; that degradation is recorded, never hidden.
6. Textual TUI is deliberately last — the engine is fully usable headless before any UI exists (Keith-testable via `doctor` + `run` + `rescore`).
7. Solo-dev pacing: WOs are sized ≈ one sitting each; the dependency order is 1→2→4→5 (freeze spine first), 3/6/7+ parallelizable after 2.

## 12. Authority files

`COSMOS_CODE_ARCH.md` (Scratch — the architecture) · `docs/HARNESS.md` + CANON trio (governance) · `HERO_SEAT_INDEX.md` + `BAKEOFF70.jsonl` (seat law + ledger) · `hero_unify.py` + `_summon_or_hero.py` (the behavior being unified — read before WO-2/3) · `cosmos_openrouter_rail.py` (Model layer) · scaffold `README/STATUS` (Q1–Q5) · `vendor-docs/HARNESS_QUALITY_ENGINE.md` + `BAKEOFF_RUBRIC.md` + `BUILD_STANDARD.md` · `REVIEW_HOLD.md` (the verdict WO-5 closes) · `V:/tmp/dsh-src/docs/architecture.md` (dsh engine, full clone) · `harness_cheats/PACK_BY_HARNESS.md` + `CORE_REVEAL.md` + `ADAPT_FROM_PEERS.md`.

*Build the tower once. Doors are data. The log proves what the model saw. The ladder verifies for free. One pen publishes.*
