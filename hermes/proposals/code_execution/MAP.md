# code_execution

Hermes `execute_code` lets an agent submit one Python script that calls a fixed tool list (`web_search`, `web_extract`, `read_file`, `write_file`, `search_files`, `patch`, foreground `terminal`). The script is a child of the agent process. Only stdout returns to the model. Modes are `project` (session working directory and the active interpreter) and `strict` (a staging directory and the Hermes interpreter). A session kernel may keep names across calls until reset, timeout, or idle eviction. Policy caps are 300 seconds, 50 KiB stdout, 10 KiB stderr, and 50 tool calls. The child environment drops secret-shaped variables. The script cannot call `execute_code`, `delegate_task`, or MCP. This proposal does not start that child, open a socket, or load a kernel.

## Live seam

`cosmos/cosmos_sandbox.py` already owns the attempt workspace and the backend facade. The composed host backend is a Windows job object (kill-on-close). Daytona and E2B are remote transports that refuse with `UNCONFIGURED` until a credential file exists. Modal is named and not composed. An unconfigured remote backend never falls through to a silent host cwd. Nothing in that module is a script planner, and this proposal does not import it.

## Operations

`plan` bounds the script, parses it with `ast.parse`, and records allowlisted calls in source order. Attribute calls count. A Hermes tool that is not on the allowlist is `NOT_ALLOWED`. An empty allowlist enables nothing. Duplicate allowlist ids are `DUPLICATE`. A call whose source span exceeds `POLICY_CALL_CHARS`, or that does not fit the remaining tool-call budget, is skipped. Later calls that fit are kept. `rebuild` re-seals those records into the same public plan.

`apply_caps` records the policy ceiling when a caller asks for more time, more tool calls, or a larger buffer. A lower request is kept. A request below 1 or above 1000000000 is `OUT_OF_RANGE`. The ceiling is not raised. A forged cap record is `BAD_CAP`.

`issue_proof` builds a `WipeProof` from caller-supplied sandbox data: proof schema `cosmos-sandbox/1`, the composed host backend, remote readiness, a credential id, a proof id, and a stamp. The digest is sealed on the record. `run` raises `UNSANDBOXED` until that record is present. A bool, a missing proof, or a lookalike dataclass is not proof. With a valid proof it still does not execute the script. It hands a frozen `RunJob` to the injected runner after the work path is jailed. `terminal` background, pty, and unverifiable keywords are `BACKGROUND`.

## Authority

The attempt workspace is the only place a script may later run. `WipeProof` is data from the ledger or from a measured `cosmos_sandbox` snapshot, not a boolean this package can flip. This package does not grant that authority. A path jail is not an OS sandbox: a jailed directory without wipe-proof data stays `UNSANDBOXED`. Remote backends (`daytona`, `e2b`) require a ready bit on the proof and a credential id, compared with `const_eq`, never a raw key. `policy_only` is a label, not a sandbox. `modal` is named and not composed.

## Refusal codes

`SYNTAX`, `EMPTY`, `EMPTY_ALLOWLIST`, `BAD_ALLOWLIST`, `DUPLICATE`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `SECRET_SHAPE`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_CAP`, `UNKNOWN_MODE`, `MISSING_CONFIG`, `UNCLASSIFIED`, `UNSANDBOXED`, `NOT_COMPOSED`, `UNKNOWN_BACKEND`, `UNCONFIGURED`, `MISSING_CREDENTIAL`, `CREDENTIAL_MISMATCH`, `BAD_PROOF`, `BAD_STAMP`, `STALE`, `NO_GRANT`, `FORBIDDEN_CALL`, `BACKGROUND`, `NOT_ALLOWED`, `UNVERIFIED`, `NO_RUNNER`, `BROKEN_CHAIN`, `RETRY_EXHAUSTED`, `RUNNER_FAILED`. A path that is present also refuses through `PathJail` (`RELATIVE_PATH`, `OUTSIDE_GRANT`, `DOTDOT`, and the other jail codes). `ConfirmFault` is the only failure class that is confirmed, and only once.

## Landing

CCr would call `plan` in the tool gate, then `issue_proof` only from a `cosmos_sandbox` snapshot that is actually composed or configured (`job_object`, `posix_subprocess`, `daytona`, `e2b` with a ready credential file). `policy_only` and `modal` stay refusals. The injected runner would be the existing spawn facade, still outside this package, with the attempt directory as the jailed work dir. No scheduler and no RPC listener are added here.

## Ship

### Operations

- `SCHEMA`
- `PROOF_SCHEMA`
- `POLICY_TIMEOUT_S`
- `POLICY_TOOL_CALLS`
- `POLICY_STDOUT`
- `POLICY_STDERR`
- `POLICY_SOURCE`
- `POLICY_CALL_CHARS`
- `TOOLS`
- `ConfirmFault`
- `AppliedCaps`
- `WipeProof`
- `CallRec`
- `ScriptPlan`
- `RunJob`
- `RunResult`
- `apply_caps`
- `proof_digest`
- `issue_proof`
- `plan`
- `rebuild`
- `run`

### Refusal codes

`SYNTAX`, `EMPTY`, `EMPTY_ALLOWLIST`, `BAD_ALLOWLIST`, `DUPLICATE`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `SECRET_SHAPE`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_CAP`, `UNKNOWN_MODE`, `MISSING_CONFIG`, `UNCLASSIFIED`, `UNSANDBOXED`, `NOT_COMPOSED`, `UNKNOWN_BACKEND`, `UNCONFIGURED`, `MISSING_CREDENTIAL`, `CREDENTIAL_MISMATCH`, `BAD_PROOF`, `BAD_STAMP`, `STALE`, `NO_GRANT`, `FORBIDDEN_CALL`, `BACKGROUND`, `NOT_ALLOWED`, `UNVERIFIED`, `NO_RUNNER`, `BROKEN_CHAIN`, `RETRY_EXHAUSTED`, `RUNNER_FAILED`, plus the `PathJail` codes for a supplied path.

### What this module still refuses to execute

The snippet itself. `exec`, `eval`, `compile`, and `__import__`, including as the injected runner. `subprocess` and any child process. A session kernel, a socket, and an RPC listener. `terminal` with `background`, `pty`, or a keyword that is not the constant `False`. `execute_code`, `delegate_task`, `breakpoint`, and `mcp`. A run with no `WipeProof` data, a boolean wipe flag, `policy_only`, or `modal`. A path jail does not unlock any of those.

### Hot-path shape

One iterative AST pass. Allow, forbid, and tool membership are sets. A call that exceeds the per-call span ceiling or the remaining tool-call budget is skipped. Later calls that fit are kept. The source is bounded, secret-checked, and hashed once on the plan seal.
