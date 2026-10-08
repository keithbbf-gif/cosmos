# Batch

Hermes batch processing runs each prompt from a JSONL dataset through its own agent session and stores a trajectory. A line carries a prompt and may name a container image or a working directory. The stock runner samples a toolset distribution at random, checkpoints completed prompt text, merges batch files, and drops samples that lack reasoning or that name an unknown tool. Parallel workers are the stock default, and the output is aimed at training-data export.

The live seam is attempt batch. `cosmos_sandbox.py` owns one attempt workspace and does not sequence a capped list of named jobs into descriptors.

`attempt` accepts named jobs in memory. It does not read a dataset file, start a session, or sample tools at random. `default` pins `file` and `terminal`. `eval` pins `file`. A caller who asks for a count cap above 100 is ignored. The descriptor records policy cap 100. A requested cap from 1 to 100 is the applied limit, and a longer submission refuses `BATCH_CAP` instead of truncating. Prompt text is not retained. Each job descriptor stores the sha256 of the utf-8 prompt. One bad job refuses the whole batch. There is no partial status. A prompt that does not fit the remaining byte budget is skipped and named, and a later prompt that fits is still accepted. `resume` keeps jobs whose prompt hash is already present, refuses a stale clock, a reused fence, or a name whose prompt changed, and still refuses the submission when any new job is bad. `confirm` allows one retry, and only for `TRANSIENT`. `rebuild` replays the descriptor chain. `upload` raises `NO_UPLOAD`.

Authority sits in the attempt workspace. The caller supplies the jobs, the credential id, the fence, and the clock. This module holds no key, spends nothing, approves no tool, and writes no checkpoint.

## Ship

Operations: `BatchDescriptor`, `JobDescriptor`, `POLICY_BYTES`, `POLICY_CAP`, `PROMPT_CAP`, `RETRY_FAILURE`, `SCHEMA`, `Skip`, `attempt`, `confirm`, `rebuild`, `resume`, `upload`.

Refusal codes: `ALT_STREAM`, `BAD_FENCE`, `BAD_IMAGE`, `BAD_ITEMS`, `BAD_NAME`, `BAD_PATH`, `BAD_RECORD`, `BATCH_CAP`, `CHAIN`, `DOTDOT`, `DRIVE_RELATIVE`, `DRIVE_ROOT`, `DUPLICATE`, `EMPTY`, `EMPTY_NAME`, `EMPTY_PROMPT`, `ENCODED_DOTDOT`, `FILE_URL`, `MISMATCH`, `MISSING`, `MISSING_CRED`, `NOT_BOOL`, `NOT_INT`, `NOT_LIST`, `NOT_MAP`, `NOT_TEXT`, `NO_GRANT`, `NO_RETRY`, `NO_UPLOAD`, `NULL_BYTE`, `OUT_OF_RANGE`, `OUTSIDE_GRANT`, `OVERSIZE`, `RELATIVE_GRANT`, `RELATIVE_PATH`, `REPLAY`, `RETRY_CAP`, `SECRET`, `STALE`, `TRAILING_DOT`, `UNC`, `UNKNOWN`, `UNKNOWN_FIELD`, `UNVERIFIABLE`.

This module still refuses to execute agent sessions, tool calls, container pulls, checkpoint writes, trajectory merges, training upload, and worker threads. A claimed completed trajectory is unverifiable. Random toolset sampling is not offered.

Hot path: one validation pass over the named jobs, then one pack pass that skips a prompt larger than the remaining byte budget and still takes a later prompt that fits. The prompt is hashed once. Name membership is a set. Distribution membership is a dict.

CCr would land this later as a pure sequencer beside the attempt workspace. The harness would own model spend and tool approval. Checkpoint files and any training export would wait for a ledger-backed path. The policy cap stays 100 until policy itself changes.
