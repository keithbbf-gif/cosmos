# workspace_guard

Hermes keeps a write inside the workspace boundary and refuses secret-shaped text before it leaves. `tools/self_repo_guard.py` is the repo boundary: a path that resolves outside the granted tree is not a write. `tools/spill_safety.py` is the spill check: outbound text that carries key-shaped material is refused rather than scrubbed and sent. There is no off mode and no yolo.

The live seam is new. `cosmos_hermes.PathJail` already contains a path in a grant, and `cosmos_hermes.secret_shape` plus `redact` already detect and scrub key-shaped text. No live module pairs those two checks.

This proposal adds `check_write`, `check_outbound`, and `applied_cap`. `check_write(jail, absolute_path)` returns the path `PathJail.contain` resolved, or raises that jail `Refuse` unchanged. A path that resolves outside the grant raises `OUTSIDE_GRANT`. A `..` segment, a UNC path, and a `file:` URL refuse through `PathJail` before a write exists, including when the same path also carries an `sk-` key. `check_outbound(text)` raises `SPILL` when `secret_shape(text)` is true. It does not return scrubbed text. A clean string is returned unchanged, which matches `redact` on that string. The policy cap is 32000 characters. A requested cap above 32000 is ignored. `applied_cap` records the asked cap, the applied cap, and the policy cap. A lower positive cap is the applied cap. Neither function writes a file.

Authority for the directory list sits with the human grant on the attempt workspace. The guard does not write a ledger, open a socket, or choose a credential. Raw key material is not a credential id. It is a spill, and it is refused.

Refusal codes from this module: `BAD_JAIL`, `SPILL`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_SCHEMA`, `BAD_LIMIT`. `bound_text` raises `NOT_TEXT`, `NULL_BYTE`, and `OVERSIZE`. A path containing an ASCII control character raises `BAD_PATH` before the jail. A path the jail rejects raises that jail `Refuse`, including `OUTSIDE_GRANT`, `RELATIVE_PATH`, `DOTDOT`, `ENCODED_DOTDOT`, `UNC`, `FILE_URL`, `BAD_PATH`, `DRIVE_ROOT`, `DRIVE_RELATIVE`, `ALT_STREAM`, and `TRAILING_DOT`. An empty grant raises `NO_GRANT` from `PathJail`. A relative grant raises `RELATIVE_GRANT`. There is no retry class.

## Ship

- operations: `POLICY_CAP`, `SCHEMA`, `AppliedCap`, `applied_cap`, `check_outbound`, `check_write`
- refusal codes: `BAD_JAIL`, `SPILL`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_SCHEMA`, `BAD_LIMIT`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `BAD_PATH`, `OUTSIDE_GRANT`, `RELATIVE_PATH`, `DOTDOT`, `ENCODED_DOTDOT`, `UNC`, `FILE_URL`, `DRIVE_ROOT`, `DRIVE_RELATIVE`, `ALT_STREAM`, `TRAILING_DOT`, `NO_GRANT`, `RELATIVE_GRANT`
- what this module still refuses to execute: a disk write, a scrubbed send of spilled text, a process, a socket, a cap above 32000, and any path `PathJail` rejects. A contained path is not a shell allow. A path jail is not an OS sandbox. There is no retry and no off switch.
- hot-path shape: one bound, one jail contain, one secret scan; a second secret scan only when resolve changes the path text. Outbound text is scanned once. A match raises `SPILL` and is not copied into a redacted result. The cap clamp is a compare, not a second copy of the body.

CCr lands the two checks in front of attempt-workspace writes and in front of any text that would be logged or returned. `PathJail` stays the only path authority. `secret_shape` stays the only secret detector. A bypass flag is not added.
