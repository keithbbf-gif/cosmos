# agent_loop

## Hermes behavior

Hermes `run_agent.py` is the public facade. The conversation loop lives behind it: each iteration samples the model, and a tool call is executed and appended before the next sample. A text reply with no tool call is the final answer. An empty assistant reply is a failed turn, not a silent success. The caller can interrupt before the next tool runs; that tool does not run, and a partial call is not stored as a tool result. Hermes budgets iterations with a caller-supplied maximum (documented default 500). A tool failure is handed back as a result so the model can correct itself. The same failure again is a stuck loop. One confirming retry is the most a named failure class receives.

## Live seam

`cosmos_harness` loop (`V:\streams\cosmos_code\cosmos_harness\cosmos_harness\loop.py`) already owns the attempt FSM and the turn cap of 8. This proposal does not import that module.

## Operations

- `clamp_turns` records the caller budget and applies 8 when the caller asks for more.
- `AgentLoop.step(model_text, tool_result)` advances one edge.
- `AgentLoop.interrupt` stops before the pending tool. No tool callable runs after it.
- `AgentLoop.snapshot` freezes the public state. `rebuild` replays that chain.
- `run` drives `step` from a model callable for at most the applied turn count.
- States are `idle`, `tool`, `observe`, and `stop`.
- A model sample is a final answer, or one first line `tool:<name>` plus opaque args. One tool per sample. The host adapts provider tool calls into that line. This module does not evaluate args.
- Named failure classes are `DENIED`, `MISSING`, `TIMEOUT`, and `TOOL_FAULT`. The first one is returned to the model. The same class again stops as `TOOL_LOOP`. Any other class stops at once as `UNCLASSIFIED`.

## Authority

The turn budget is policy on the attempt, not a model choice. Interrupt is the human. Tool results are records the caller supplies. An empty tool table enables no tool. This module does not write the ledger, does not open a socket, and does not spawn a thread.

## Refusal codes

Stop records: `DONE`, `EMPTY`, `INTERRUPTED`, `TOOL_LOOP`, `MAX_TURNS`, `SECRET`, `NO_ALLOW`, `UNKNOWN_TOOL`, `BAD_TOOL`, `UNCLASSIFIED`.

A tool exception is the observe record `TOOL_FAULT`. The first time a named failure class appears, that record is returned to the model on the next sample. The second time the same class appears, the machine stops as `TOOL_LOOP`. `run` writes `MAX_TURNS` when the applied budget is spent. It does not take another sample.

Caller refusals: `SECRET`, `EMPTY_TASK`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_TOOLS`, `BAD_TOOL`, `BAD_STATE`, `NEED_TOOL_RESULT`, `BAD_TOOL_RESULT`, `ALREADY_STOPPED`, `NOT_STOPPED`, `BAD_POLICY`, `BAD_NOTE`, `BAD_RECORD`, `BAD_SNAPSHOT`, `BROKEN_CHAIN`, `STALE`, `POLICY_CAP`.

`POLICY_CAP` is the ninth model step after eight turns are already on the chain. That step raises and writes nothing. A lower caller budget still stops as `MAX_TURNS`.

## Landing

CCr keeps `cosmos_harness` as the only loop. The host constructs this machine with the harness hand table, passes samples in, and lets the existing hook order fire around `tool` and `observe`. The cap stays 8. Interrupt stays a latch, not a thread. The second identical named tool error stops the attempt instead of sampling again.

## Ship

- operations: `SCHEMA`, `POLICY_MAX_TURNS`, `STATES`, `FAILURE_CLASSES`, `AgentLoop`, `Halt`, `Model`, `Note`, `Policy`, `Record`, `Role`, `Snapshot`, `State`, `ToolAsk`, `ToolResult`, `clamp_turns`, `rebuild`, `run`. Methods: `step`, `interrupt`, `run`, `halt`, `snapshot`, `transcript`.
- refusal codes: `SECRET`, `EMPTY_TASK`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_TOOLS`, `BAD_TOOL`, `BAD_STATE`, `NEED_TOOL_RESULT`, `BAD_TOOL_RESULT`, `ALREADY_STOPPED`, `NOT_STOPPED`, `BAD_POLICY`, `BAD_NOTE`, `BAD_RECORD`, `BAD_SNAPSHOT`, `BROKEN_CHAIN`, `STALE`, `POLICY_CAP`, plus stop records `DONE`, `EMPTY`, `INTERRUPTED`, `TOOL_LOOP`, `MAX_TURNS`, `NO_ALLOW`, `UNKNOWN_TOOL`, `UNCLASSIFIED`.
- what this module still refuses to execute: provider calls, sockets, threads, subprocesses, file and ledger writes, tool-argument evaluation, a yolo or off mode, a cap above 8, a second retry of a named failure, and any retry of an unnamed failure.
- hot-path shape: one pass over `range(applied)`, set lookup for the allowlist and for failure classes; a model step after eight turns raises `POLICY_CAP` and does not start another pass. Each record hashes once onto the previous digest.
