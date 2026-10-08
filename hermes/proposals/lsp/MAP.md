# lsp

Hermes runs language servers as child processes and, after a clean in-process syntax check, asks them for semantic diagnostics on a write or a patch. The check runs only inside a git workspace. An untrusted checkout starts only a small allowlist of servers. A missing or slow server leaves the syntax result in place. Definition and hover use the same JSON-RPC session. Install, restart, and idle shutdown are process operations.

The live seam is JSON-RPC builders. `cosmos/cosmos_mcp_client.py` speaks MCP JSON-RPC and does not own language-server document requests. This proposal builds LSP bodies on that seam. It does not start a language server.

`initialize` returns one `initialize` request for a jailed root URI. The process id on the wire is null. Capabilities are the fixed set this module can describe: definition, hover, and diagnostic. `did_open` returns a `textDocument/didOpen` notification for a jailed file URI. The language id comes from the suffix. A `.py` file is `python`, a `.blade.php` file is `blade`, and a file named `Dockerfile` is `dockerfile`. Any other unknown suffix refuses. `definition` and `hover` return positioned requests. `diagnostic` returns a pull request with no position. `parse` accepts one JSON object and refuses a malformed envelope, a framed stream, or a server result. `rebuild` replays an emitted record through the same jail, including a lower cap stored on that record. `parse` applies the policy caps because the wire does not carry them. A caller who asks for a position cap above 1000000, or a text cap above 16000, is ignored, and the record stores the policy cap. A lower positive cap is honored. These records are descriptors.

Authority for the path is the attempt-workspace grant. The body is not a ledger entry and not an approval. A later service would decide whether a language server may run. This module has no spawn authority.

Refusal codes from this module: `BAD_BODY`, `BAD_HOST`, `BAD_JAIL`, `BAD_LANGUAGE`, `BAD_LIMIT`, `BAD_METHOD`, `BAD_POSITION`, `BAD_RECORD`, `BAD_RPC`, `BAD_SCHEMA`, `BAD_URI`, `SECRET`. `bound_text` and `bound_int` still raise `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, and `OUT_OF_RANGE`. A path `PathJail` rejects raises that jail code, including `OUTSIDE_GRANT`, `DOTDOT`, `ENCODED_DOTDOT`, `RELATIVE_PATH`, `DRIVE_ROOT`, `DRIVE_RELATIVE`, `ALT_STREAM`, `TRAILING_DOT`, `FILE_URL`, and `UNC`. There is no retry class.

## Ship

- operations: `CLIENT_NAME`, `CLIENT_VERSION`, `ID_MAX`, `LANGUAGES`, `METHOD_CAP`, `METHODS`, `POSITION_CAP`, `SCHEMA`, `TEXT_CAP`, `URI_CAP`, `VERSION_MAX`, `RpcRequest`, `definition`, `diagnostic`, `did_open`, `hover`, `initialize`, `parse`, `rebuild`
- refusal codes: `ALT_STREAM`, `BAD_BODY`, `BAD_HOST`, `BAD_JAIL`, `BAD_LANGUAGE`, `BAD_LIMIT`, `BAD_METHOD`, `BAD_POSITION`, `BAD_RECORD`, `BAD_RPC`, `BAD_SCHEMA`, `BAD_URI`, `DOTDOT`, `DRIVE_RELATIVE`, `DRIVE_ROOT`, `ENCODED_DOTDOT`, `FILE_URL`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OUTSIDE_GRANT`, `OVERSIZE`, `RELATIVE_PATH`, `SECRET`, `TRAILING_DOT`, `UNC`
- what this module still refuses to execute: spawning a language server, opening a socket, installing or restarting a server, idle shutdown, a git-trust decision, a Content-Length frame, a server result, `workspace/executeCommand`, and any method outside the five descriptors
- hot-path shape: one pass over the URI, percent-decode once, contain once, render one JSON object; suffix lookup is a dict; method and hex checks are sets; a position or a document that does not fit the applied cap refuses before render

CCr lands `cosmos_lsp.py` beside the MCP client. Call sites pass a grant jail and receive a descriptor. The position cap stays 1000000 and the text cap stays 16000. Server install, trust, and process lifetime stay out of this module until a supervised runner exists. That runner consumes the body. It does not grow a second path check.
