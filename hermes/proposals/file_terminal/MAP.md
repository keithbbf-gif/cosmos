# file_terminal

Hermes reads a text file, replaces one targeted span, and runs a command through `terminal`, with `process` for background commands. A command string is shell syntax. A background action is still a process. This proposal reads UTF-8 inside a grant, replaces a span only when the old text has one match, and records an argv list. It does not start a process.

`read_text(jail, path, cap=None)` reads one absolute path through `PathJail`. The policy cap is 64000 UTF-8 bytes. A requested cap above that is ignored, and the result records the applied cap and the policy cap. A lower positive cap is honored. An oversize file refuses. It is not truncated. `patch(text, old, new)` returns the edited text when `old` has one match (a second start index, including an overlap, is a second match). Zero matches are `EDIT_MISS`. More than one match is `EDIT_NOT_UNIQUE`. `terminal(argv)` raises `SHELL_STRING` for a `str`. A list becomes a frozen descriptor whose `code` is `NEED_APPROVAL`.

`execute` stays refused until the caller supplies a frozen `WipeProof` as data: `wipe_proof` is `True` and `backend` is one of `job_object`, `posix_subprocess`, `daytona`, or `e2b`. Any other proof raises `UNSANDBOXED` or `UNKNOWN_BACKEND` and does not build a hold. A valid proof still does not spawn. The return is an `ExecuteHold` whose `code` is `HELD`. The policy timeout is 180 seconds. A higher request is recorded and applied as 180. A lower positive timeout stands.

## Live seam

The live seam is `cosmos/cosmos_platform.py`. That module is the process adapter: argv lists, UTF-8 on both ends, and tree kill on timeout. A string command refuses there as `SHELL_REFUSED`. This proposal does not import it and does not call it.

## Authority

Authority for the bytes is the attempt-workspace grant. Paths go through `PathJail`. Authority to execute is a wipe proof the caller supplies as data, plus the human approval gate. `WipeProof` attests that a later sandbox will wipe the child. This package does not grant that attestation. `NEED_APPROVAL` is not permission to run. `HELD` is not a running process. Remote wipe backends (`daytona`, `e2b`) require a credential id, compared with `const_eq`, never a raw key. `job_object` and `posix_subprocess` refuse a credential. Patch returns text and leaves the file unchanged. There is no retry class.

## Ship

- operations: `ARG_CAP`, `ARGV_CAP`, `POLICY_TIMEOUT_S`, `READ_CAP`, `SCHEMA`, `WIPE_BACKENDS`, `ExecuteHold`, `PatchResult`, `ReadText`, `TerminalRequest`, `WipeProof`, `execute`, `patch`, `read_text`, `terminal`
- refusal codes: `BAD_JAIL`, `BAD_LIMIT`, `BAD_ARGV`, `EMPTY_ARGV`, `EMPTY_ARG`, `ARGV_COUNT`, `SHELL_STRING`, `MISSING`, `NOT_FILE`, `NOT_UTF8`, `UNREADABLE`, `OVERSIZE`, `SECRET`, `EMPTY_OLD`, `EDIT_MISS`, `EDIT_NOT_UNIQUE`, `BAD_CODE`, `BAD_SCHEMA`, `BAD_RESULT`, `UNSANDBOXED`, `UNKNOWN_BACKEND`, `NOT_INT`, `OUT_OF_RANGE`, `MISSING_CREDENTIAL`, `CREDENTIAL_MISMATCH`, `BAD_CREDENTIAL`, `CREDENTIAL_REFUSED`, plus `NOT_TEXT` and `NULL_BYTE` from `bound_text`. A path the jail rejects raises that jail code (`DOTDOT`, `OUTSIDE_GRANT`, `RELATIVE_PATH`, and the jail's other path codes).
- what this module still refuses to execute: a shell string, an argv whose proof is missing or not a frozen `WipeProof`, a proof whose `wipe_proof` is not `True`, a known non-wipe backend (`local`, `platform`, `policy_only`, `docker`, `ssh`, `singularity`, `modal`, `vercel`, `vercel_sandbox`), and every argv even after a valid proof. `execute` returns `ExecuteHold` and does not spawn, poll, or kill. `terminal` returns `NEED_APPROVAL` and does not spawn. No descriptor carries a pid. `patch` does not write the file.
- hot-path shape: one read of at most cap+1 bytes, then a refuse when the file does not fit; patch finds the needle and one later start index, including an overlap, and stops; wipe-backend checks are set membership. A higher read cap or timeout is ignored and the policy cap is recorded. Secret text on a stored record is classified once.

## Landing

CCr lands `read_text` and `patch` beside `cosmos_platform.py`, keeps the 64000-byte cap, and passes only a `HELD` argv into a sandbox whose backend matches the proof. A string refusal stays in both layers. `cosmos_platform.run` stays the only process launcher, and this proposal does not call it.
