# Layout

COSMOS is not finished, and this page is not a completion claim. It is the map
of two trees that share a parent folder on this machine and are not the same
thing. Code and governance are the repo. The running instance is one
configured runtime root. Paths into that root go through `cosmos_paths`. A
directory that merely exists is not that root.

Install steps are [INSTALL](INSTALL.md). The authority file under the ledger
role is [LEDGER](LEDGER.md). Who may write the live tree is [PEN](PEN.md).
The ratified shape is `docs/FINAL_ARCHITECTURE.md`. This page does not paste
those contracts and does not paste source.

## Two trees

| | Repo tree | Runtime root |
|---|---|---|
| On this machine | `V:\A\Ai\COSMOS` | `V:\A\Ai\COSMOS\live` |
| What it is | The software and the governance. This repository is that tree, not a copy of it. | The running instance: state, ledger, queue, registry, config, and the other declared roles. |
| Identity | Git history and the files that are tracked. | Sentinel **content** in `.cosmos-root.json` (`system` = `COSMOS`, `tree_id` = `KMesh-COSMOS-live`, `schema_version` = 1). |
| Git | Tracked, deny-by-default. | Git-ignored (`/live/` in `.gitignore`). Shipping it would hand a peer somebody else's history. |

Nesting is a local choice. The runtime root sits inside the repo directory on
this workstation. That does not make `live\` a package, and it does not make
the repo directory the root Core opens. A peer install passes its own `--root`
and `--tree-id`. The examples in `cosmos/cosmos.py` use a different path on
purpose. The resolver will not infer a root from the repo, a drive letter, or
a parent walk.

Windows treats `V:\A\Ai\COSMOS` and `V:\a\ai\cosmos` as one directory. Casing
is not identity either. The sentinel is.

`/trylive/` is git-ignored scratch. It is not this runtime root. A backup set
under the backups role is not a second live root. A dated copy of config beside
the config role is not the config role.

The repo `README.md` still says "Pre-implementation". That line is older than
the Core already in `cosmos/`. Neither sentence means the system is done.

## What is tracked

Reading map, not an inventory. Sibling chapters cover packages and builds.
None of these directories is the runtime root.

- `cosmos/` — Core package. The CLI is `cosmos/cosmos.py`. The resolver is
  `cosmos/cosmos_paths.py`. This is source. It is not the tools role below.
- `docs/` — governance, including the ratified architecture. This book is
  `docs/dev/`. It is not the runtime `docs` role.
- `tests/` — tests.
- `kdash/` — a projection client. It does not hold authority.
- `builds/` — product trees (cDeck and others). Not a second Core.
- `tools/`, `work_orders/` — tools and the proposal queue. See [PEN](PEN.md).
- Package trees named from the book index: `clusters/`, `cosmos_code/`,
  `cosmos_harness/`, `federation/`, `hermes/`, `harness/`, `tokenctr/`,
  `voice/`, `voice_duplex/`. Presence in the tree is not a finished product.

`work/` at the repo root is not the runtime `work` role. Session pointers
`BUCm.toml`, `BUcr.toml`, `BUhar.toml`, and `BUorc.toml` sit beside the code
and are git-ignored. They are not a sentinel and not a second root.

`.gitignore` is deny-by-default: code and governance in, live state and
secrets out. `/live/` ignores the runtime root as a whole. Secret-shaped names
are ignored even outside that directory. Do not copy `live/config` into a doc,
a commit, or a chat. This page does not name credential files or quote them.

## One configured root

`cosmos/cosmos_paths.py` is the Core resolver. Construction is the check.
There is no half-built resolver.

- One root, chosen at install. No ladder, no fallback, no drive literal, no
  parent walk.
- Importing the module does not touch the filesystem.
- `CosmosPaths(root)` reads the sentinel and raises if the root is wrong.
  `Kernel` does this before it opens the ledger. A bad root never becomes
  `ready`.
- `CosmosPaths.from_install_record(path)` reads a JSON record with a `root`
  key and, when present, checks `tree_id`. The path is the argument you pass,
  or the path in the environment variable `COSMOS_INSTALL_RECORD`. If neither
  is set the kind is `NOT_FOUND`. The resolver refuses to guess.
- The same class can open two roots. They share no state. A second tree id is
  a different install, not a fallback.

The installer (`install` in `cosmos/cosmos_kernel.py`, CLI
`cosmos.py install --root … --tree-id …`) stamps the sentinel, creates every
declared role directory, writes `config/install_record.json` (`root`,
`tree_id`, `installed_epoch`), and writes per-install authentication material
under the config role. This page does not name that material or show its
bytes. Re-install with the same `tree_id` is idempotent. Re-install with a
different `tree_id` raises `IDENTITY_MISMATCH`. Restamping a live install is
treated as a hijack, not as setup.

On this machine the install record points at `V:\A\Ai\COSMOS\live` with
`tree_id` `KMesh-COSMOS-live`. Serve still takes `--root`. It does not
discover that path:

```text
py -3.14 cosmos\cosmos.py install --root <runtime-root> --tree-id <tree-id>
py -3.14 cosmos\cosmos.py serve   --root <runtime-root> --port 8770
```

Callers ask for a role. They do not join strings onto a drive.

```python
paths = CosmosPaths(root)          # verifies sentinel content
paths.ledger("authority.jsonl")
paths.queue("manifests", name)
paths.registry()
paths.config("install_record.json")
paths.state("SEED.json")
```

`paths.<role>(...)` is the role table. An unknown role raises `NOT_FOUND`
and lists the known names. It does not invent a plausible path.

A role part that is absolute, or that contains `..`, raises
`IDENTITY_MISMATCH`. After the join, the normalized path must still sit under
the root. Traversal is not a path.

On Windows, `extended()` and `walk()` use the `\\?\` form so a path past
MAX_PATH is not reported as a missing file. That prefix is a length fix, not a
second root.

`builds/cdeck/cosmos/cosmos_paths.py` is a smaller copy for cDeck panel
binders (tools and work only). It is not the installer and not a second
runtime root. Core code uses `cosmos/cosmos_paths.py`.

## Existence is not identity

The scar this check closes: a resolver pointed at a directory that existed and
held nothing, and every "is this a directory?" test passed. Content is the
identity. Existence is nothing.

The sentinel file is `.cosmos-root.json` in the runtime root. On this install
it is:

```json
{
  "system": "COSMOS",
  "tree_id": "KMesh-COSMOS-live",
  "schema_version": 1
}
```

`CosmosPaths` accepts that root only when the file parses and `system` is
`COSMOS`. When the caller also passes an expected `tree_id` (the install
record does), the sentinel id must match. A COSMOS root with the wrong id is
still a refusal: it is a COSMOS root, but not this install's root.

An empty registry directory is not a registry. A seed whose `tree_id` does
not match the sentinel is not this install's handoff. A projection that says
`verified` without a fresh measurement is not a proof. Those are the same
rule in three places.

Typed refusals from the resolver (`CosmosPathError.kind`):

| Kind | When |
|---|---|
| `NOT_FOUND` | The root path does not exist, or the role name is not in the table, or no install record was given. |
| `NOT_A_DIRECTORY` | The root path exists and is not a directory. |
| `UNREADABLE` | The sentinel or the install record cannot be read. |
| `UNPARSEABLE` | The file is not JSON, or the install record has no `root` key. |
| `IDENTITY_MISMATCH` | The directory exists but has no sentinel, `system` is not `COSMOS`, `tree_id` does not match, or a role part would escape the root. |

Wrong kind is a wrong claim. A missing root is not an identity mismatch. An
empty directory is not "not found".

## Declared roles

One table in `cosmos/cosmos_paths.py` (`ROLES`). The value is the relative
directory under the runtime root. `install` creates each of them. Callers use
the role name, not a hand-built path.

| Role | Directory | What it is for |
|---|---|---|
| `root` | `.` | The verified root itself. |
| `state` | `state` | Session handoff, mail, protected writes, projections, blobs. Not the authority chain. |
| `ledger` | `ledger` | Core authority chain and the lease chain. See [LEDGER](LEDGER.md). |
| `queue` | `queue` | Immutable job manifests and the scheduler's own chain. |
| `registry` | `registry` | Rebuildable node and rail projection. |
| `config` | `config` | Install record and other instance material, including credentials. |
| `work` | `work` | Attempt-private work. Not authority until it is filed through the fence. |
| `logs` | `logs` | Process logs and heartbeats. |
| `backups` | `backups` | Backup sets and rehearsals. Not a live root. |
| `publish` | `publish` | Staged publish output. |
| `tools` | `cosmos` | Runtime tools directory (job scripts and the like). **Not** the repo package `cosmos/`. |
| `docs` | `docs` | Runtime docs role. **Not** the tracked `docs/` tree. |

This machine's `live\` also holds directories that are not roles, including
`buckets/`, `returns/`, and a dated config backup. They are local runtime
material. Do not add them to the table by documenting a hand-built path.
Unknown role names refuse.

### State

The state role is carry-over and projections. It is not the ledger.

- Session close writes `state/SEED.json` plus a declaration sidecar. Start
  reads that seed only if the bytes check and the `tree_id` equals the live
  sentinel. Another tree's seed must not inject here. A dated archive is kept
  under `state/seeds`. Nothing is unlinked.
- The kernel composes mail at `state/mail`.
- A fenced protected write targets `paths.role("state", relpath)`. The path
  is checked before a lease is taken.
- The pen projection is `state/control/CCR.lease`. Do not print the token.
  See [PEN](PEN.md).
- Large blobs are content-addressed under this role, not under a `cas` role.
  The role table has no `cas` entry. Packet bytes go to `state/cas` with the
  filename equal to the hash (`cosmos/cosmos_packet.py`). CVM blobs go to
  `state/cvm/cas`. `cosmos_segments.CAS` writes `<sha>.blob` under a directory
  the caller passes. The ledger holds the pointer, not the blob. These stores
  are not one finished product. See [LEDGER](LEDGER.md).

On this machine `state\` is large: audits, heartbeats, and other projections
accumulate there. Count of files is not authority. A file in `state\` can be
dropped and rebuilt. The chain cannot.

### Ledger

Role path: `paths.ledger("authority.jsonl")`. That file is the Core chain:
append-only, hash-chained, authenticated with the per-install key. A corrupt
segment is refused. It is not repaired in place.

`paths.ledger("leases.jsonl")` is the lease arbiter's chain. It is not
`authority.jsonl`. Details, field names, and what a projection is allowed to
be are [LEDGER](LEDGER.md). Do not commit either file.

### Queue

Ratified decision 4: the queue is immutable manifests plus ledger lifecycle
events. A service-private SQLite file, if one is used, is a projection. It is
not authority.

The scheduler (`cosmos/cosmos_sched.py`) is opened on `paths.role("queue")`.
Submit writes `queue/manifests/<job_id>.json`, then appends `JOB_SUBMITTED` to
`queue/sched_ledger.jsonl`. After that write the manifest is not the
lifecycle. The scheduler chain is not Core's `authority.jsonl`. A row in one
does not prove an event in the other.

This install also has `done/`, `failed/`, `running/`, `returns/`, `_lanes/`,
and `logs/` under `queue/`. Those are runtime output. They do not outrank the
manifest plus the scheduler chain.

### Registry

`live/registry/nodes.json` and `live/registry/rails.json` are a rebuildable
projection (`cosmos/cosmos_registry.py`, `file_runtime`, schema
`cosmos-registry/1`). The ledger is authority. The directory being present is
not a registry. The files carry a measurement time.

A node is registered at runtime only after a live rail call returns success, a
non-empty body, and the model that answered. A claim is not a proof. An import
or a version string is not a proof.

Freshness is a gate, not a decoration. The projection and the router share one
TTL (`PROOF_TTL_S`, 3600 seconds, pinned to the prober). Rows older than that
are listed under `stale` with `verified` false. They are not left looking live,
and they are not dropped without a name. Do not read `verified: true` and
ignore the measurement time.

### Config

`config/install_record.json` is the machine record: `root`, `tree_id`,
`installed_epoch`. `from_install_record` uses it only when you point at it or
set `COSMOS_INSTALL_RECORD`. It is instance state. It lives under the
git-ignored root. It is not a secret, and it is still not something to commit.

The same role holds the install's authentication material and local rail
configuration. This page does not name those files, list them, or quote them.
The kernel does not invent authentication material if it is missing. Boot
refuses and tells the operator to run the installer.

A backup copy of config that sits **beside** `config/` is not this role. Do
not serve from it and do not commit it.

## What not to do

- Do not hard-code `V:\A\Ai\COSMOS` or `V:\A\Ai\COSMOS\live` inside Core. Pass
  the root. Resolve a role at the moment of use.
- Do not treat the repo `cosmos\`, `docs\`, or `work\` directory as the
  matching runtime role. The tools role is `live\cosmos`. The docs role is
  `live\docs`. The work role is `live\work`.
- Do not point a tool at an empty folder, a backup, or `trylive\` and call it
  this install because the directory exists.
- Do not copy `live\` into git, into a proposal, or into this book. That
  includes the ledger, the registry projection, session seeds, and everything
  under config.
