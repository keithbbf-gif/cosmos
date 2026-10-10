# Install

This page is one chapter of the developer book. It does not mean COSMOS is
finished, fully tested, or ready to treat as a completed product. A clean
install only means a peer has a verified runtime root and can start the
loopback API. Spend budgets, vendor credentials, seats, critics, dispatch,
voice, and Token Center are not turned on by this command.

COSMOS — Carry-Over State Mesh Operating System — is a modular monolith. One
Core process is the authority: the path resolver, the append-only ledger, the
lease arbiter, the scheduler, and the versioned HTTP API. Everything else is
a projection or a later package. This chapter is how a peer on a cold machine
stands that Core up. It is not a tour of the unfinished house.

## Two directories

Keep the source clone and the runtime root apart.

| Directory | What it is |
| --- | --- |
| Repository | The clone that contains `cosmos\cosmos.py`. Code and governance. |
| Runtime root | A directory you choose at install. Ledger, queue, config, state. |

The resolver does not hard-code a drive letter, walk parents, or fall back to
another path. You pass one root. Construction checks the sentinel **content**
in that directory. A folder that merely exists is not a COSMOS root. Two
installs at two paths do not share resolver state.

Do not point this command at another machine's runtime tree, and do not copy
one install's `config` or `ledger` onto another. This page does not tell you
to start the live server on the machine where the development tree already
runs. The commands below are what the peer runs against the root they just
configured.

## What you need

- This repository, obtained the way that peer is allowed to obtain it. This
  page does not include a token, a password, or a clone credential.
- Windows with the Python launcher. Core is invoked as `py -3.14`. The HTTP
  service in `cosmos\cosmos.py serve` is written against the Python 3.14
  standard library. Install does not pip-install a stack.
- An empty or new directory for the runtime root. Any path you can write. The
  path is configuration, not a built-in drive.

Put that root somewhere Git will not commit. The repository ignore is
deny-by-default: a top-level `live\` directory, ledgers, queue output, and
secrets are not source. If the root sits inside the clone anyway, do not
commit `config\install_key.bin`, `config\api_token.txt`, or the ledger. This
book does not contain those files' contents. Do not paste them into docs,
chat, or tickets.

Run the commands from the repository root, so `cosmos\cosmos.py` is the path
that exists. The script puts its own directory on `sys.path`. You do not
install the `cosmos` package into site-packages for this path.

## Install the root

`--root` and `--tree-id` are both required. `--tree-id` is the name of **this**
install. Pick one and keep it. The example in the CLI help uses a placeholder
root such as `D:\Ai\Cosmos` and a tree id such as `JMesh-1`. Use your own
values. There is no default root.

```text
py -3.14 cosmos\cosmos.py install --root <the configured root> --tree-id <your-tree-id>
```

On success the process prints the root path and the tree id and exits 0.

What that command writes, and nothing more:

- `.cosmos-root.json` at the root. The identity stamp is JSON with `system`
  set to `COSMOS`, `tree_id` set to the id you passed, and `schema_version`
  `1`. Identity is those fields, not the folder name.
- Role directories, created if missing. The relative names are `state`,
  `ledger`, `queue`, `work`, `logs`, `registry`, `backups`, `publish`,
  `config`, `docs`, and `cosmos`. The runtime `cosmos` directory is an empty
  role. Install does not copy the source tree into the root.
- `config\install_key.bin`, only if that file is not already there. It is 32
  random bytes. The kernel loads it and will not invent a replacement. Lose
  the file and this ledger's authentication material is gone. Do not print
  it, do not commit it, and do not transcribe it here.
- `config\install_record.json`, rewritten each run. It records `root` (the
  path you passed), `tree_id`, and `installed_epoch`. It is a pointer, not a
  secret. The CLI does not read it back. `serve` and `status` take `--root`
  every time. Library code may call `CosmosPaths.from_install_record`, which
  reads this file or the path in the `COSMOS_INSTALL_RECORD` environment
  variable. If neither is set, that call refuses. It does not guess a root.

The same tree id may be installed again. Role directories are left in place.
An existing install key is not rotated. A root whose sentinel already has a
**different** tree id is refused (`IDENTITY_MISMATCH`). Re-stamping a live
install is treated as a hijack, not as an install. A sentinel that is not
valid JSON is refused (`UNPARSEABLE`). The command does not repair it.

`install` does not ask questions. It does not create a virtual disk, mount a
volume, register a Windows service, or schedule a task. Those ideas live in
other notes. This verb only stamps the root. `serve` is a foreground process
until you stop it.

## How the root is verified

`Kernel` constructs `CosmosPaths` on the `--root` you pass. That constructor
is the check. It fails closed, with a typed `CosmosPathError`, before any
ledger write:

| Kind | When |
| --- | --- |
| `NOT_FOUND` | The root path does not exist. Also: no install record and `COSMOS_INSTALL_RECORD` unset, when using the library helper. |
| `NOT_A_DIRECTORY` | The path exists and is not a directory. |
| `IDENTITY_MISMATCH` | No `.cosmos-root.json`, or `system` is not `COSMOS`, or `tree_id` does not match the id you expected. An empty directory is this case. Existence is not identity. |
| `UNREADABLE` | The sentinel or the install record cannot be read. |
| `UNPARSEABLE` | The file is not JSON, or an install record has no `root` key. |

Callers do not assemble paths by hand. Roles are a fixed table (`state`,
`ledger`, and the rest above). A role part that is absolute or contains `..`
is refused. On Windows, long paths use the `\\?\` form inside the walker so
a deep path is not reported as a missing file.

There is still no drive literal in that check. `<the configured root>` means
the directory whose sentinel you wrote, wherever it sits.

## Serve

After `install` succeeds on the cold machine, from the repository root:

```text
py -3.14 cosmos\cosmos.py serve --root <the configured root> --port 8770
```

`<the configured root>` is the same path you passed to `install`. It is not a
path on the development machine, and it is not implied by a drive letter.
This book does not start that process here.

What `serve` does:

1. Builds a writing kernel. The sentinel is checked, then
   `config\install_key.bin` is loaded. A missing key is `NOT_FOUND`. The
   kernel does not mint one. Run `install` first.
2. Opens `ledger\authority.jsonl`. A missing ledger file is an empty history,
   which is allowed. A file that exists and fails the hash chain is refused.
   A torn, forged, or truncated ledger is not repaired in place. Fix the
   cause or restore a verified backup. Do not hand-edit the chain.
3. Appends one `BOOT_VERIFIED` record, then composes the arbiter, mail,
   scheduler, registry, spend gate, and session manager on that ledger.
4. Attaches vendor rails fail-open. A dead rail is skipped and logged. It
   does not abort `READY`. `READY` means this boot passed the checks above.
   It does not mean the product is finished.
5. Listens. With no `--remote`, the bind is `127.0.0.1` only. The port on
   this command is `8770` (also the flag's default). Stop the process with
   Ctrl+C. It shuts the server down.

The banner prints the URL, says the bearer file is `config\api_token.txt`
under the runtime root, and points at `kdash\index.html` in the **repository**
(a static page, not something `install` generates). On loopback, if that
bearer file is missing, the service writes one. On a non-loopback bind it
will not invent a token: a missing file is `TOKEN_MISSING`, and an empty or
whitespace file is `BLANK_TOKEN`. Read the file only on the machine that
wrote it. This book does not contain a bearer, a key, or either file's
bytes.

`--remote` binds all interfaces and is a separate decision. `--no-auth`
together with `--remote` is refused (`REMOTE_OPEN_ACCESS`) before the socket
is used. Do not disable the bearer to get a first page up. `--tls`,
`--cert`, and `--key` are optional and are not part of the cold-machine line
above. A remote bind without TLS is refused unless you explicitly pass the
trial flag `--insecure-http`, which still requires the bearer. This page does
not walk that trial.

The banner also names any Crucible critics that attached. If none attach, it
says so, and `POST /api/v1/crucible` stays HTTP 501. That refusal is the
honest state. Do not stub a critic to make the line look green.

## Look, without serving

These two commands boot a read-only kernel. They check the sentinel and the
ledger and do not append `BOOT_VERIFIED`.

```text
py -3.14 cosmos\cosmos.py status --root <the configured root>
py -3.14 cosmos\cosmos.py audit  --root <the configured root>
```

`status` prints JSON with `ready`, `root`, `tree_id`, and the ledger head
(`seq` and `event`). `audit` re-walks the chain and reports measured counts.
An unmeasured value is omitted. It is not reported as zero.

Use these against the root you installed. They are not a request to start
the development machine's server.

## What a fresh root does not include

- No spend budgets. `SpendGate` has nothing to spend until a budget is set
  on a rail. An unbudgeted rail cannot spend. Install does not set a cap and
  does not load vendor credentials.
- No seats module. `GET` and `POST /api/v1/seats` stay HTTP 501
  (`SEATS_NOT_COMPOSED`).
- No promise that critics run. With none attached, the crucible route stays
  501, as the serve banner says.
- No Windows service, no Tailscale join, and no second copy of the source
  tree inside the root.
- No statement that dispatch, voice, Token Center, resession, or the clone
  planner are done. Token Center is a separate package. Install does not bind
  it to Core `SpendGate`. Those subjects belong to their own chapters. A
  successful install line is not a ship gate.

The same CLI also implements `backup`, `rehearse`, `submit`, `session`,
`deck`, and `xtalk`. They are outside this chapter. `backup` and `rehearse`
are how a peer proves a copy can be restored. They are not run by `install`.

## Refusal is a result

A typed refusal is the gate working. Do not delete the sentinel to "unwedge"
a mismatch, do not replace `install_key.bin` with bytes from another tree,
and do not point `--root` at a directory that only happens to be writable.
Create a new directory and install it with its own tree id, or keep using the
tree id the sentinel already names.
