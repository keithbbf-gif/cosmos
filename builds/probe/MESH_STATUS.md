# MESH_STATUS -- why each node rail does or does not prove live

**Generated** by `builds/probe/mesh_blockers.py` (do not hand-edit; re-run it).
**Measured** 2026-08-31T08:26:03.465685-05:00  ·  root `V:\A\Ai\COSMOS\live`  ·  deep=False  ·  0.07s
**Projection** `V:\A\Ai\COSMOS\live\registry\nodes.json` count=7  ·  proof TTL 3600s

The gate is `cosmos_registry.proof_ok`: **ok AND rc==0 AND a non-empty body AND the model that answered.** Nothing here weakens it, and nothing here asserts reachability -- a rail this tool did not measure is UNMEASURED, never green.

Two columns, two different facts. **blocker kind** is why the node does or does not carry a passing proof on the authority ledger. **the rail's own probe** is the line that rail emitted during this run, verbatim -- a rail can be perfectly healthy and still never prove live, because nothing asks it (`NOT_WIRED`).

| node | type | route | wired for prove | proven live | blocker kind | the rail's own probe, right now |
|---|---|---|---|---|---|---|
| `sgh-api` | API | core->models | yes | yes | **NONE** | OK: bts_sgh importable (liveness is per-call) |
| `gem-api` | API | core->models | yes | yes | **NONE** | OK: bts_gem importable (liveness is per-call) |
| `gw-api` | API | core->models | yes | yes | **NONE** | OK: bts_gw importable (liveness is per-call) |
| `oa-api` | API | core->models | yes | yes | **NONE** | OK: bts_oa_api importable (liveness is per-call) |
| `claude-cli` | CLI | core->code | yes | no | **STALE_PROOF** | NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to |
| `cursor-api` | API | core->code | yes | yes | **NONE** | NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to |
| `firecrawl-web` | API | core->papers | yes | yes | **NONE** | NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to |
| `playwright-dom` | DOM | core->interact | yes | yes | **NONE** | NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to |
| `codex-cli` | CLI | core->code | **NO** | no | **NO_KEY** | NO_KEY: [NO_KEY] OpenAI key missing at V:\A\Ai\COSMOS\live\config\openai_api_key.txt (never hard-code; redact to sk-…l |

**7 of 9 node rails carry a passing proof** (the projection counts 7).

## What the ledger says, structurally

* **1 links hold a `LINK_REGISTERED` claim and ZERO `PROBE_RESULT` rows** -- `codex-cli`. The claim is in the authority ledger; no measurement ever followed it, so `live_nodes()` drops every one. Registration is not capability, exactly as designed.
* **1 link sits in the projection's `stale` list** -- `claude-cli`. `Registry.file_runtime` applies the proof TTL (`proof_ttl_s`); a stale row is `verified: false` and is not in `count`/`nodes`. Re-prove to move it back.

## Per node

### `sgh-api` -- NONE

**Blocker:**

```
none -- this node proves live
```

**What `bts_sgh` emitted on this run** (OK):

```
bts_sgh importable (liveness is per-call)
```

Evidence:

```json
{
 "incumbent_root": "V:\\Ai\\BTS_MESH",
 "module": "bts_sgh",
 "module_file": "V:\\Ai\\BTS_MESH\\bts_sgh.py",
 "has_ask": true
}
```

Ledger's last measurement for this link:

```json
{
 "ok": true,
 "rc": 0,
 "model": "grok-4.6",
 "body_bytes": 4,
 "age_s": 3298.9,
 "probe_results_recorded": true
}
```

**Unblocked by:** Nothing -- proven live.

### `gem-api` -- NONE

**Blocker:**

```
none -- this node proves live
```

**What `bts_gem` emitted on this run** (OK):

```
bts_gem importable (liveness is per-call)
```

Evidence:

```json
{
 "incumbent_root": "V:\\Ai\\BTS_MESH",
 "module": "bts_gem",
 "module_file": "V:\\Ai\\BTS_MESH\\bts_gem.py",
 "has_ask": true
}
```

Ledger's last measurement for this link:

```json
{
 "ok": true,
 "rc": 0,
 "model": "gemini-2.5-flash",
 "body_bytes": 4,
 "age_s": 3297.3,
 "probe_results_recorded": true
}
```

**Unblocked by:** Nothing -- proven live.

### `gw-api` -- NONE

**Blocker:**

```
none -- this node proves live
```

**What `bts_gw` emitted on this run** (OK):

```
bts_gw importable (liveness is per-call)
```

Evidence:

```json
{
 "incumbent_root": "V:\\Ai\\BTS_MESH",
 "module": "bts_gw",
 "module_file": "V:\\Ai\\BTS_MESH\\bts_gw.py",
 "has_ask": true
}
```

Ledger's last measurement for this link:

```json
{
 "ok": true,
 "rc": 0,
 "model": "grok-build-0.1",
 "body_bytes": 4,
 "age_s": 3295.1,
 "probe_results_recorded": true
}
```

**Unblocked by:** Nothing -- proven live.

### `oa-api` -- NONE

**Blocker:**

```
none -- this node proves live
```

**What `bts_oa_api` emitted on this run** (OK):

```
bts_oa_api importable (liveness is per-call)
```

Evidence:

```json
{
 "incumbent_root": "V:\\Ai\\BTS_MESH",
 "module": "bts_oa_api",
 "module_file": "V:\\Ai\\BTS_MESH\\bts_oa_api.py",
 "has_ask": true
}
```

Ledger's last measurement for this link:

```json
{
 "ok": true,
 "rc": 0,
 "model": "gpt-5.6-terra",
 "body_bytes": 4,
 "age_s": 3291.5,
 "probe_results_recorded": true
}
```

**Unblocked by:** Nothing -- proven live.

### `claude-cli` -- STALE_PROOF

*Two paths, one link_id: ClaudeRail.dispatch needs config/anthropic_api_key.txt, but cosmos_rails_prober._claude_live_call falls back to the prepaid SEAT (`claude -p` with ANTHROPIC_API_KEY unset). The recorded proof came from the seat path, so ClaudeRail.probe() refusing NO_KEY does not contradict the registry row.*

**Blocker:**

```
proof age 17866.3s exceeds the 3600s proof TTL; Registry.file_runtime lists this row under 'stale' (verified:false, proof_state:STALE), not under 'nodes'. The F-25 freshness filter dropped it from count; it is named, not deleted
```

**What `cosmos_claude_rail` emitted on this run** (NO_KEY):

```
UNREACHABLE: NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to sk-ant-…last4)
```

Evidence:

```json
{
 "key_path": "V:\\A\\Ai\\COSMOS\\live\\config\\anthropic_api_key.txt",
 "key_present": false,
 "binary": "claude",
 "binary_on_path": "C:\\Users\\Papa\\.local\\bin\\claude.EXE"
}
```

Ledger's last measurement for this link:

```json
{
 "ok": true,
 "rc": 0,
 "model": "haiku",
 "body_bytes": 4,
 "age_s": 17866.3,
 "probe_results_recorded": true
}
```

**Unblocked by:** Re-prove: `file_runtime` already dropped this row from `count`/`nodes` (F-25 freshness filter) and lists it under `stale`. Run the rails prober with `--live` to record a fresh proof.

### `cursor-api` -- NONE

**Blocker:**

```
none -- this node proves live
```

**What `cosmos_claude_rail` emitted on this run** (NO_KEY):

```
UNREACHABLE: NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to sk-ant-…last4)
```

Evidence:

```json
{
 "key_path": "V:\\A\\Ai\\COSMOS\\live\\config\\anthropic_api_key.txt",
 "key_present": false,
 "binary": "claude",
 "binary_on_path": "C:\\Users\\Papa\\.local\\bin\\claude.EXE"
}
```

Ledger's last measurement for this link:

```json
{
 "ok": true,
 "rc": 0,
 "model": "Cursor COSMOS 2",
 "body_bytes": 88,
 "age_s": 3291.0,
 "probe_results_recorded": true
}
```

**Unblocked by:** Nothing -- proven live.

### `firecrawl-web` -- NONE

**Blocker:**

```
none -- this node proves live
```

**What `cosmos_claude_rail` emitted on this run** (NO_KEY):

```
UNREACHABLE: NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to sk-ant-…last4)
```

Evidence:

```json
{
 "key_path": "V:\\A\\Ai\\COSMOS\\live\\config\\anthropic_api_key.txt",
 "key_present": false,
 "binary": "claude",
 "binary_on_path": "C:\\Users\\Papa\\.local\\bin\\claude.EXE"
}
```

Ledger's last measurement for this link:

```json
{
 "ok": true,
 "rc": 0,
 "model": "firecrawl/v2-research-papers",
 "body_bytes": 169,
 "age_s": 3280.5,
 "probe_results_recorded": true
}
```

**Unblocked by:** Nothing -- proven live.

### `playwright-dom` -- NONE

**Blocker:**

```
none -- this node proves live
```

**What `cosmos_claude_rail` emitted on this run** (NO_KEY):

```
UNREACHABLE: NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to sk-ant-…last4)
```

Evidence:

```json
{
 "key_path": "V:\\A\\Ai\\COSMOS\\live\\config\\anthropic_api_key.txt",
 "key_present": false,
 "binary": "claude",
 "binary_on_path": "C:\\Users\\Papa\\.local\\bin\\claude.EXE"
}
```

Ledger's last measurement for this link:

```json
{
 "ok": true,
 "rc": 0,
 "model": "Playwright/1.63.0-alpha-2026-08-05",
 "body_bytes": 76,
 "age_s": 3279.9,
 "probe_results_recorded": true
}
```

**Unblocked by:** Nothing -- proven live.

### `codex-cli` -- NO_KEY

**Blocker:**

```
UNREACHABLE: NO_KEY: [NO_KEY] OpenAI key missing at V:\A\Ai\COSMOS\live\config\openai_api_key.txt (never hard-code; redact to sk-…last4)  [AND: codex-cli is absent from cosmos_rails_prober.WIRED_NODES, so clearing the refusal above still leaves nothing asking it for a proof]
```

**What `cosmos_codex_rail` emitted on this run** (NO_KEY):

```
UNREACHABLE: NO_KEY: [NO_KEY] OpenAI key missing at V:\A\Ai\COSMOS\live\config\openai_api_key.txt (never hard-code; redact to sk-…last4)
```

Evidence:

```json
{
 "key_path": "V:\\A\\Ai\\COSMOS\\live\\config\\openai_api_key.txt",
 "key_present": false,
 "binary": "codex",
 "binary_on_path": "C:\\Users\\Papa\\AppData\\Roaming\\npm\\codex.CMD"
}
```

Ledger's last measurement for this link:

```json
{
 "ok": null,
 "rc": null,
 "model": null,
 "body_bytes": null,
 "age_s": null,
 "probe_results_recorded": false
}
```

**Unblocked by:** Keith places the credential at the `key_path` in the evidence above (credentials are his domain -- COSMOS opens the door, never a bat).

---

Regenerate: `py -3.14 builds\probe\mesh_blockers.py --root <runtime-root> --deep --write-md`
