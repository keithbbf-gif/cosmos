# PROPOSAL — `builds/probe/mesh_blockers.py`: stop guessing each rail's probe module

**From:** COSMOS coder, F-24 re-prove job, 2026-08-31.
**Fence:** this job writes only under `cosmos/`. `builds/probe/` is the supervisor's.
**Action:** `edit` — two lines. Proposed, **not applied**.

## The defect (measured, not asserted)

`rows()` derives each wired rail's probe target itself:

```python
out.append(dict(w, probe_with=w.get("module") or "cosmos_claude_rail", ...))
```

That reads correctly for the incumbent rows (`module="bts_*"`) and for `claude-cli`.
It reads **wrongly for every satellite**: those `WIRED_NODES` rows carry
`module=None` and name their rail in `satellite`, so all three fall through to the
Anthropic default.

Emitted proof, `py -3.14 builds/probe/mesh_blockers.py --root ./live --deep`
at **2026-08-31T03:27:21 −05:00** (`cosmos/_f24_deep_blockers.json`):

| link_id | `probed_via` | what MESH_STATUS reported it emitting |
|---|---|---|
| `cursor-api` | `cosmos_claude_rail` | `UNREACHABLE: NO_KEY: [NO_KEY] Anthropic key missing at …\anthropic_api_key.txt` |
| `firecrawl-web` | `cosmos_claude_rail` | *(identical Anthropic refusal)* |
| `playwright-dom` | `cosmos_claude_rail` | *(identical Anthropic refusal)* |

All three carried **passing proofs on the authority ledger at that same moment**
(`PROBE_RESULT` seq 995 / 996 / 997). The document therefore named a credential
none of the three rails uses, for three rails that were live — and pointed anyone
reading it at `anthropic_api_key.txt`, which would fix nothing.

Second consequence: `measure()` dispatches on `probe_with`, so `playwright-dom`
routed to `probe_binary_rail`. **`--deep` was inert** — `probe_playwright()`, the
only reason the flag exists, was unreachable.

## Root cause — the same lesson twice in one slice

The four rails moved from `UNWIRED_ROWS` (where each row named its own
`probe_with`) into `WIRED_NODES` (where no row does). The double-count you already
fixed was *not removing them from the table they left*; this is *not carrying what
they had in it*. One move, two halves, both missed.

## The fix, in two parts

**Part 1 — applied, in fence.** `cosmos/cosmos_rails_prober.py` now exports
`probe_module_for(spec)`, and the satellite name → live_call map became a single
`SATELLITES` table carrying **both** the rail module and the call, so "which module
is this rail?" and "what do I call to prove it?" are read off one row and cannot
drift. `SATELLITE_CALLS` is gone; its only consumers were in `cosmos/`.

**Part 2 — proposed, yours.** Two lines, so the tool asks the table's owner
instead of guessing:

```diff
--- a/builds/probe/mesh_blockers.py
+++ b/builds/probe/mesh_blockers.py
@@ -44,7 +44,7 @@
-from cosmos_rails_prober import NODE_PROOF_TTL_S, WIRED_NODES    # noqa: E402
+from cosmos_rails_prober import (                                # noqa: E402
+    NODE_PROOF_TTL_S, WIRED_NODES, probe_module_for)
@@ -86,7 +86,7 @@ def rows() -> list[dict]:
     out = []
     for w in WIRED_NODES:
-        out.append(dict(w, probe_with=w.get("module") or "cosmos_claude_rail",
+        out.append(dict(w, probe_with=probe_module_for(w),
                         route=f"{w['src']}->{w['dst']}", note=NOTES.get(w["link_id"])))
```

## Runtime binding for the proposal

Applied in-memory over the live tree (`cosmos/_f24_deep_blockers_fixed.json`),
each rail now emits its **own** evidence instead of an Anthropic refusal:

```
cursor-api      kind=NONE probe=OK  via=cosmos_cursor_rail      apiKeyName=Cursor COSMOS 2 http=200
firecrawl-web   kind=NONE probe=OK  via=cosmos_firecrawl_rail   primaryId=arxiv:gr-qc/9504041 http=200
playwright-dom  kind=NONE probe=OK  via=cosmos_playwright_rail  tools/list n=24 server=Playwright 1.63.0-alpha-2026-08-05
codex-cli       kind=NO_KEY         via=cosmos_codex_rail       NO_KEY: OpenAI key missing at live\config\openai_api_key.txt
```

`live_count 8 of 9`. `--deep` reaches the MCP server again (`tools/list n=24` can
only come from `probe_playwright`).

Bite proof for Part 1: `cosmos/test_rails_wired.py` is **48/48 PASS** on the fixed
prober and **4 checks FAIL** against the staged predecessor at
`_delme/predispose_cosmos_rails_prober_20260831T033029/`. `builds/probe/test_mesh_blockers.py`
stays **24/24** (its `probe_with` checks are satisfied by the fix, not broken by it).

## One more thing, flagged not fixed — a redaction gap in the same column

With Part 2 applied, `cursor-api`'s `probe_detail` is the **CursorRail's own**
detail string, and that string ends with a redacted key fragment. `render_md()`
writes `probe_detail` straight into `MESH_STATUS.md`, which is a tracked document.
`cosmos_rails_prober._cursor_live_call` already refuses to use that string for
exactly this reason — *"the rail's own detail string carries a redacted key
fragment, and nothing key-shaped belongs in the authority ledger."* The same
argument applies to a committed markdown file. Suggest `render_md()` and the
per-node `probe_detail` block strip a `key=…` tail before writing. Not touched
here — your fence, and it is a separate change from the mis-routing above.
