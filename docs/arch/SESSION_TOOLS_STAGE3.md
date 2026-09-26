# SESSION TOOLS — MOTIF stage-3 CONSENSUS

**Stage:** 3 CONSENSUS (`docs/MOTIF.md`). **CCr:** G46 `39d083c1`. **Date:** 2026-09-05.
**Lanes:** A = this TUI (`docs/arch/SESSION_TOOLS_ARCH.md`). B = Cursor `bc-2f8665b1` / `run-754fda1f` **FINISHED**, draft PR **#40** `https://github.com/keithbbf-gif/cosmos/pull/40` (P10; **do not merge**). Harvest: `work_orders/ccr/lane_b_session_tools_arch.md` + `.json`.
**No peeking during stage 2.** This file is the compare, then **CCr dispose**. Keith 2026-09-05: *You are the CCr.* CCr picks. No BUILD this tick. No Core kernel write. No PR merge of #30/#32/#36/#37/#38/#40.

## CCr DISPOSE (2026-09-05T21:12) — TAKEN

| # | Pick | Why |
|---|---|---|
| **D1 shape** | **JSONL + `.ctr.decl.json` sidecar + source byte-span partition** (Lane B). Canonical files: `{id}.ctr.jsonl` (record 1 = `head`, then N `turn`) and `{id}.ctr.decl.json` (`len`/`sha` via `write_declared`; **no HMAC**). Convert gate: `sum(span.len)==source.len` **and** `sha256(concat(spans))==source.sha256`. Fidelity `span` (one byte stream) or `blob` (sqlite/dir). | Runtime-binding is arithmetic, not a fixture claim (SCAR_PLACATION). House JSONL. 24.4 MB / 17439 turns streams. Lane A object remains a **load stdout view**, not the canonical file. |
| **D2 criterion** | **Widest fidelity gap first; read-only families first, live stores last** (Lane B). Pick stays **Grok TUI**. Order after that: cowork-pack md as first-class source, then opencode (live, last), Claude Desktop HOLD/UNMEASURED. | Stops Claude Desktop from jumping the queue on “obvious Claude-family.” |
| **HMAC** | **sha-only** on the transcript sidecar. HMAC stays on **SEED**. | Transcripts must open on a cold peer. Suite does not hold `install_key.bin`. |

Live canon after dispose: `docs/arch/SESSION_TOOLS_ARCH.md` (this TUI). Lane B PR **#40** stays draft P10 harvest — **do not merge**.

## Agreed (both lanes; CCr takes)

| # | Decision | Both said | CCr |
|---|---|---|---|
| **D2 pick** | First family after Claude | **Grok TUI** (`grok_tui` / `grok-tui`) | **TAKE.** Bound on this machine; Open Sessions docstring already names it. |
| **D3** | Crash-recover | **check + restore-from-bak.** Third writer **REJECTED.** Never repair sqlite/SEED in place. | **TAKE.** AD-3. Lane B adds: only mutation in the suite is `rebind` (shape, not policy) — keep. |
| **Name** | Canonical schema name | **`cosmos-transcript/1`** | **TAKE** the name. |
| **Fences** | Not a second Core; no 666 re-ingest; Legal omitted; Open Sessions stays LIVE; no CLOCKS shrink; `ANTHROPIC_OFF` | same | **TAKE.** |
| **Home** | Stage-4 code | `builds/session-tools/` + `tests/test_session_tools*` | **TAKE.** |

## CONTESTED — resolved by CCr (no third model)

1. **D1 shape.** **TAKEN: JSONL+spans.** Lane A object is load-view only.
2. **D2 criterion.** **TAKEN: widest fidelity gap first; read-only first.**
3. **Sidecar HMAC.** **TAKEN: sha-only.** HMAC stays on SEED.

## Lane B extras CCr records

- **BLK-1:** `builds/cdeck` is a gitlink `160000 f4270d0` with **no `.gitmodules`**, so a clean GitHub clone lacks `cosmos_recents_panel`. Runtime on this box is LIVE; GitLab CI / peer install is the gap. Owner = CCr. Not this suite. Do not bounce Core to “fix” it this tick.
- Cross-family `diff`: compare **structure** (`seq`/`role`/`src.sha`) first; `text` is a second axis. HOLD to Slice-2.
- `scan` on a clock: **not proposed.** New scheduled task needs Keith’s word.

## What CCr does not do this tick

Does not merge PR **#40** (draft, P10). Does not merge #30/#32/#36/#37/#38. Does not author `builds/session-tools/*.py` this tick (Slice-1 is next BUILD, not this dispose). Does not recode `cowork_to_openwork`. Does not re-ingest 666.

## Next

Slice-1 BUILD: `builds/session-tools/` `scan`+`load` cowork wrap + grok_tui, hermetic tests, Core `:8770` stays up. Docs in this tree are the disposed ARCH. Gitur PR-A later if Keith wants GitHub `main` to carry the ARCH; local `docs/arch/` is already authority.
