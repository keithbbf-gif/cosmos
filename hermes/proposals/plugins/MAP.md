# Plugins

Hermes discovers plugins from bundled, user, project, and pip sources, then runs a plugin only after its name is on `plugins.enabled` and every declared capability is granted. A name on `plugins.disabled` stays off even when it is also enabled. Memory providers and context engines are separate kinds, and only one of each is active. General tool plugins combine. Hermes loads a plugin directory from disk. This review copy never does that.

The live seam is injected callables. No COSMOS module owns a plugin loader. The host passes the callable in. Only that object is callable, and only when its name is on the allowlist and `seal(signer, name)` matches. An unsigned plugin refuses. An unknown plugin refuses. `load_from_path` raises `IMPORT` for every argument and does not open a path, so a plugin cannot be loaded with importlib from disk.

`Registry` starts empty. An empty allowlist raises `EMPTY_ALLOW`. `register` admits one plugin when the kind is `tool`, `memory`, or `context`, every requested permission is in the grant, the name is allowlisted, the name is not denied, the handler is a callable the host passed in, and the signature matches the seal. The public row is `name`, `callable_id`, and `kind`. The callable, the grant, and the seal are not on the row. `call` runs that callable with one bounded string. `clock` on the allowlist runs. `shell` off the allowlist raises `NOT_ALLOWED` and is not stored. A second memory provider or a second context engine raises `EXCLUSIVE`.

The policy cap is 32 admissions. A higher request is ignored and recorded on `requested`. A lower positive cap is the effective cap. The next new name past that cap raises `FULL`. `catalog` walks admissions once, skips a description that does not fit the remaining budget, and continues with later names that fit. The catalog budget policy is 512. There is no retry class. A handler exception becomes `PLUGIN_FAIL` after one attempt.

Each admission is a `Link` in a hash chain that starts at `GENESIS`. `rebuild` replays those links with the host's callables and seals and returns the same public entries, fence, and catalog. A bad link raises `BROKEN_CHAIN`. A fence that is not the chain head raises `STALE`. The seal is a consent digest over the schema, the signer id, and the name. It is not a certificate and it does not authorize disk code.

Authority for the allowlist, the deny list, the signer id, and the grant sits with the human. The registry is an in-memory projection. It does not write a ledger, open a socket, or read a plugin directory. A credential is the signer id. Raw key material raises `SECRET`. `repr` stays free of key material. Seals, callable ids, and chain digests are compared with `const_eq`.

Refusal codes: `ABSENT`, `BAD_CRED`, `BAD_FENCE`, `BAD_ID`, `BAD_KIND`, `BAD_NAME`, `BAD_RESULT`, `BAD_TEXT`, `BROKEN_CHAIN`, `DENIED`, `DUPLICATE`, `EMPTY_ALLOW`, `EXCLUSIVE`, `FULL`, `IMPORT`, `MISSING_CRED`, `NOT_ALLOWED`, `NOT_CALLABLE`, `NOT_INT`, `NOT_LIST`, `NOT_MAP`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `PERMISSION`, `PLUGIN_FAIL`, `SECRET`, `STALE`, `UNCLASSIFIED`, `UNKNOWN`, `UNSIGNED`.

CCr would land this later as the admission step in front of a host callable table. The host injects the callable. The allowlist and the seal stay the gate. Disk discovery, importlib, and pip entry points stay refused.

## Ship

- operations: `CATALOG_BUDGET`, `GENESIS`, `KINDS`, `PERMISSIONS`, `POLICY_CAP`, `SCHEMA`, `TEXT_CAP`, `Catalog`, `Link`, `Plugin`, `Registry`, `Result`, `load_from_path`, `seal`
- refusal codes: `ABSENT`, `BAD_CRED`, `BAD_FENCE`, `BAD_ID`, `BAD_KIND`, `BAD_NAME`, `BAD_RESULT`, `BAD_TEXT`, `BROKEN_CHAIN`, `DENIED`, `DUPLICATE`, `EMPTY_ALLOW`, `EXCLUSIVE`, `FULL`, `IMPORT`, `MISSING_CRED`, `NOT_ALLOWED`, `NOT_CALLABLE`, `NOT_INT`, `NOT_LIST`, `NOT_MAP`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `PERMISSION`, `PLUGIN_FAIL`, `SECRET`, `STALE`, `UNCLASSIFIED`, `UNKNOWN`, `UNSIGNED`
- still refuses to execute: importlib or any other load from a path, pip entry points, network install, subprocess and shell commands, hook dispatch, platform actions, a callable the host did not pass in, a name off the allowlist, an unsigned plugin, an unknown plugin, a second memory provider, a second context engine, and any handler retry
- hot-path shape: one pass — set membership for the allowlist, the deny list, and canonical grants; `call` looks up one dict entry and runs the injected callable; `catalog` skips a description that does not fit the remaining budget and continues
