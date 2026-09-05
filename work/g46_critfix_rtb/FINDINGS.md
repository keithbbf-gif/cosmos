# P10 findings — gem/oa fake-DONE runtime proof (CVM desktop clock)

**Agent:** G46. **Propose-only.** Wrote this directory; did not edit `cosmos/` or `live/` source.

## Verdict

The applied execute_handoff path is **runtime-bound**. A fresh GEM dispatch and a fresh OA dispatch each spawned the node rail, dropped onto `live/buckets/<node>`, and returned **non-empty model text**. This is not the old packet-and-exit (`rc=0`, `secs=0.0`, empty body).

| rail | link_id | recorded model | secs | done_why | stdout bytes |
|---|---|---|---:|---|---:|
| GEM | gem-api | bts_gem | 29.9 | nonempty_stdout | 11638 |
| OAi | oa-api | bts_oa_api | 77.6 | nonempty_stdout | 16484 |

Recorded `model` is the rail module id the worker wrote (`bts_gem` / `bts_oa_api`). That is what the result JSON contains; this report does not invent a vendor model name behind it.

## Named critique artifacts

execute_handoff identity is `*.stdout.txt` beside the dispatch result. G46 filed **byte-identical** copies of that rail text to the named gate paths and to this work dir:

| path | bytes | sha256_16 | who answered |
|---|---:|---|---|
| `V:\A\Ai\COSMOS\docs\critique\cvmdt_CRITIQUE_gem-api.md` | 11638 | f94061e1b3ec7f28 | gem-api / bts_gem |
| `V:\A\Ai\COSMOS\docs\critique\cvmdt_CRITIQUE_oa-api.md` | 16484 | 3f8962ca56c0ed1a | oa-api / bts_oa_api |
| `V:\A\Ai\COSMOS\work\g46_critfix_rtb\cvmdt_CRITIQUE_gem-api.md` | 11638 | f94061e1b3ec7f28 | same GEM body |
| `V:\A\Ai\COSMOS\work\g46_critfix_rtb\cvmdt_CRITIQUE_oa-api.md` | 16484 | 3f8962ca56c0ed1a | same OA body |

Heads: GEM `# cvm_dt - Motif stage-5 critique (gem-api)`; OA `# cvmdt - Motif stage-5 critique (oa-api)`. Real HIGH/MED/LOW markdown, not a 0-byte packet.

## Harness identity (what execute_handoff actually wrote)

- GEM job: `live/cosmos/dispatch_jobs/gem_gem_cvmdt_clock_motif_stage_5_critique_g_c4443209__t1800.py`
  - timeout_s **1800** (not the 120s stub)
  - SOURCE calls `from cosmos_node_worker import execute_handoff`
  - worker_bucket `live/buckets/gem`
  - processed drop `live/buckets/gem/processed/20260827T043515-0500_handoff-20260827T043515-0500.json`
  - stdout `live/queue/returns/cm/gem_gem_cvmdt_clock_motif_stage_5_critique_g_c4443209_result.json.stdout.txt`
  - V return `live/returns/gem/gem_handoff-20260827T043515-0500_20260827T043515-0500_result.json`
- OA job: `live/cosmos/dispatch_jobs/oai_oa_cvmdt_clock_motif_stage_5_critique_o_bc130121__t1800.py`
  - same execute_handoff contract; worker_bucket `live/buckets/oa` (created this run)
  - processed drop `live/buckets/oa/processed/20260827T043515-0500_handoff-20260827T043515-0500.json`
  - stdout `live/queue/returns/cm/oai_oa_cvmdt_clock_motif_stage_5_critique_o_bc130121_result.json.stdout.txt`
  - V return `live/returns/oa/oa_handoff-20260827T043515-0500_20260827T043515-0500_result.json`
  - spend recorded `usd=0.099528`

Contrast with the scar (`fa6c68cc`): `rc=0`, `secs=0.0`, packet only under `state/dispatch/workers/oa`, no rail.

## Dispatch notes (not a fail)

- CLI `--task` with the source packet hits Win32 `CreateProcess` **WinError 206** (filename/args too long). Runtime dispatch used `cosmos_dispatch.dispatch()` in-process with a short `label` and the full task body. Same function the CLI wraps.
- `live/logs/oa_worker_heartbeat.json` still absent (OA `--loop` not stood up). execute_handoff does not need the poller: it writes the bucket packet and `process_drop`s itself.
- Core SHA of the applied files matched the prior bundle: dispatch `fc433ba939c50b6b`, node_worker `0da48282e86b4556`, oa_worker `d23644bce4d2c5c1`.

## CVM desktop clock — different-family consensus (quote, do not rubber-stamp)

Both GEM and OA: **NOT ready for stage-6 runtime-binding.** Shared HIGHs:

1. Native DT clock is not ticking (`cvm_dt_clock_heartbeat.json` missing). Loopback tests are a green log.
2. `CLOCK_ID = 17` vs H10 “next is 15” vs live `pull.json clock_id=16`.
3. Live Core `core_kind='UNREACHABLE'` — the named heartbeat+cursor gate cannot fire.
4. H6 audio-owner authority is not proven from the clock file alone (clock drives `CvmDtClient.cycle_once()`).

OA-only (worth keeping): `--once` bypasses `skip_alive`/lock; unread `PAUSE.flag` reports `ok=True` paused instead of a typed refusal; `REUSED = (core_get, pull_url, write_heartbeat)` is unused decorative code.

Full bodies: the two `.md` files above.
