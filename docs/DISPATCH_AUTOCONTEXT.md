# DISPATCH — auto-context, tag-routed agent creation (spec)

**Consumer:** COSMOS / nodes (builder = G46). **Encoded by COW 2026-08-25** from Keith's direction.
Enhances `cosmos/cosmos_dispatch.py`. NO BTS. PAUSE-aware. No fabricated compliance.

## Goal
Drive the Orchestrator's dispatch cost to near zero. COW **transcribes Keith's text, adds an AGENT
TAG, and drops it in the box.** The OS does the rest — pulls the context, creates the agent, feeds
it the assignment, sets the output folder + timestamp, and files the assignment record. COW is free
in under a second (the offload principle; the role contract P9).

## The drop — what COW writes (minimal)
A tiny file in the bucket carrying: `agent` (tag), `assignment` (COW's transcription of Keith),
optional `context_hint`, optional `out` (results-folder tag). That is the whole of COW's hands-on
dispatch surface.

## The dispatcher daemon — native Windows, per drop
1. **Parse the TAG** → agent type: `G46`/`GW` (Grok Build), `SGH` (Grok), `GEM`, `OAi`, `CURSOR`, `SSA`…
2. **PULL CONTEXT (native, C:\\).** Find the current session transcript (`.jsonl` under
   `C:\\Users\\Papa\\AppData\\Roaming\\Claude\\local-agent-mode-sessions\\...`), read the **TAIL**
   (last N turns / M KB — config), strip tool noise, keep Keith's text + COW's framing → a context
   blob. **The sandbox cannot read C:\\ reliably; the native tool pulls it directly.** Bind
   provenance (session id + byte range).
3. **CREATE the agent** of that type; feed it `{context + assignment}`; set the **OUTPUT tag** = a
   results folder; stamp a **timestamp** from `datetime.now()` (never hand-typed).
4. **EXECUTE** via the node's rail/lane, or hand the drop to that node's worker bucket
   (`cosmos_grok_worker`/`cosmos_gem_worker`).
5. **FILE the record** — creation time, agent, assignment, target (output folder), timestamp, tag —
   into the **per-session agent-assignment file** (the DHx assignment log + a session-scoped
   `assignments.jsonl`). The collector correlates the result back.

## Bucket topology (config; DEFAULT = shared, tag-routed)
- **DEFAULT:** ONE shared bucket ("the box"); every drop carries its agent tag; the dispatcher
  routes/creates by tag. One box, one truth.
- **OPTION:** one bucket per agent (each agent watches its own).
Record + output-folder + timestamp behavior is identical either way.

## Every assignment carries the boundaries addendum (auto-attached)
The dispatcher **auto-attaches `docs/AGENT_BOUNDARIES.md` to every assignment** — no task goes out
without it. The addendum says: **only the Orchestrator touches the tree; agents PROPOSE tree changes
in their results (target path + full content or diff) for COW to execute, or not.** Agents never
write the live tree or the C:\ Claude tree, and never delete (propose staging to `_delme\`). This is
what closes the concurrency / one-writer gap.

## Canon honored
No BTS · PAUSE-aware · no fabricated compliance (every record bound to a real file) · COW drops only
the tag + assignment, the OS does creation/context/filing · never delete (stage to `_delme\`).
