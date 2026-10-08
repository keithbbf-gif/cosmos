# codex_runtime

Hermes can hand an OpenAI turn, an `openai-codex` turn, or a named custom provider to the Codex app-server. The switch is opt-in. Codex then owns the shell, structured patches, and the sandbox, and Hermes keeps sessions, slash commands, and approval prompts. A judge stays read-only. A coder may write inside the workspace sandbox and nowhere else. Four flags are never accepted: `--danger-full-access`, `--full-auto`, `--ignore-user-config`, and `--approve-for-me`. The model is an argv element. A shell metacharacter in an argument refuses. This proposal does not start Codex.

The live seam is argv only. `cosmos/cosmos_codex_rail.py` already chooses coder and vetter sandboxes and can start the Codex CLI. No COSMOS module owns a Hermes app-server argv that refuses those four flags. This proposal does not import the rail and does not spawn.

`plan(role, model, extra=(), *, workspace=None, extra_cap=None)` returns a frozen `Plan` for one named workspace and one model. `argv_for` returns a fresh list of that plan's argv. `rebuild` re-seals the same public fields. `run` raises `NOT_RUN` and does not start a process. The roles are `judge` and `coder`. `judge` argv is `codex app-server -m <model> --sandbox read-only`. `coder` argv uses `--sandbox workspace-write`. The sandbox comes from the role. A record whose sandbox disagrees with its role is `UNSANDBOXED`. The workspace is a name on the plan, not a path and not an argv element, so a leaked argv list cannot change directory. A missing, empty, `off`, `yolo`, `auto`, slash-bearing, or `..` name is `BAD_WORKSPACE`. `extra` may only add the pair `--color never`, repeated up to the applied cap. Any other extra is `UNCLASSIFIED`. A forbidden flag, a `danger-full-access` sandbox value, or a yolo alias raises `FORBIDDEN` before the cap is applied. The extra-token policy cap is 8. A higher requested cap is stored on the plan and ignored. A lower cap is kept. There is no retry class.

Authority for a later process is the attempt workspace. A judge record is not a write grant. The workspace name is not that grant. This module holds no process, no socket, and no credential. Key-shaped text is refused and is not stored.

Refusal codes: `FORBIDDEN`, `UNKNOWN_ROLE`, `EMPTY_MODEL`, `BAD_MODEL`, `BAD_WORKSPACE`, `SECRET_SHAPE`, `SHELL_META`, `NOT_LIST`, `EMPTY_ARG`, `BAD_ARG`, `UNCLASSIFIED`, `OVER_CAP`, `OVERSIZE`, `NULL_BYTE`, `NOT_TEXT`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_LIMIT`, `BAD_SCHEMA`, `BAD_PLAN`, `UNSANDBOXED`, `BAD_ARGV`, `NOT_RUN`.

CCr would later pass the list from `argv_for` to the runner that already lives in `cosmos_codex_rail.py`, and would resolve the workspace name to a jailed directory outside this package. The runner stays outside this package. `run` stays a refusal. A judge launch still requires `read-only`, and the four forbidden flags still refuse. Landing adds no scheduler and no socket.

## Ship

### Operations

- `SCHEMA`
- `EXTRA_CAP`
- `ARG_CAP`
- `MODEL_CAP`
- `FORBIDDEN_FLAGS`
- `JUDGE_SANDBOX`
- `CODER_SANDBOX`
- `Plan`
- `plan`
- `argv_for`
- `rebuild`
- `run`

### Refusal codes

`FORBIDDEN`, `UNKNOWN_ROLE`, `EMPTY_MODEL`, `BAD_MODEL`, `BAD_WORKSPACE`, `SECRET_SHAPE`, `SHELL_META`, `NOT_LIST`, `EMPTY_ARG`, `BAD_ARG`, `UNCLASSIFIED`, `OVER_CAP`, `OVERSIZE`, `NULL_BYTE`, `NOT_TEXT`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_LIMIT`, `BAD_SCHEMA`, `BAD_PLAN`, `UNSANDBOXED`, `BAD_ARGV`, `NOT_RUN`.

### What this module still refuses to execute

The Codex process. `run` raises `NOT_RUN` for a sealed plan and for any non-plan. A tampered plan is re-sealed and refused before any start. There is no shell, no JSON-RPC session, no config write, no plugin migration, no login, and no network. The workspace name is not a directory open. An argv list is not permission to spawn.

### Hot-path shape

One pass over the extra tokens. Forbidden canon is a dict. Shell metacharacters, model characters, and workspace characters are sets. Each token is bounded and classified once on the way in. A list longer than the hard window refuses after that window. A list inside the window that exceeds the applied cap refuses only after those tokens are classified, so a forbidden flag or a shell metacharacter is not reported as a cap miss. Pairing the accepted `--color never` suffix is a second walk of at most eight tokens. `rebuild` copies the sealed fields and checks them again.
