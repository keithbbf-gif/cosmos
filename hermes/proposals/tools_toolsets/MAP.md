# tools_toolsets

Hermes groups each tool into one toolset and resolves the model-visible set from a platform allow list and a deny list (`disabled_toolsets`). A platform with no config enables nothing. An empty allow list enables nothing. Composite names such as `debugging`, `coding`, and `safe`, and platform preset names such as `hermes-telegram`, expand to a fixed tuple of toolset names before any tool is chosen. Stock messaging presets are the same tuple as `hermes-cli`, and that tuple includes `terminal`. `effective` reads the expanded tuple. On any platform other than `cli`, a resolved allow list that still contains `terminal` raises `MESSAGING_TERMINAL`, including when deny names that toolset too. A selected tool whose risk is `terminal` raises the same code. `hermes-webhook` and `safe` do not list `terminal`. The names `all` and `*` do not expand. Deny drops a toolset that the allow list also names. A named disabled tool is removed and later allowed tools stay.

The live seam is hand allowlists. COSMOS hand allowlists do not yet resolve per-platform toolsets. The neighbor is `cosmos/cosmos_approval.py`, which gates an action after a tool is chosen and does not choose the toolset list.

## Operations

`new_catalog` returns an empty frozen registry. `register` appends one tool (`name`, `toolset`, `risk`) and returns a new catalog. Risk is `read`, `write`, `terminal`, `net`, or `admin`. `rebuild` replays those tool records into an equal catalog. `effective(platform, allow, deny, catalog=..., disabled_tools=...)` returns an `Effective` record. `toolsets` is the resolved allow list after preset expansion and deny, limited to toolsets that still have a tool. `tools` holds the matching registered tools, in registration order, minus `disabled_tools`.

`allow` `None` is a missing platform config. `None` and an empty allow raise `EMPTY_ALLOW` and do not return the registry. A toolset name that is not registered raises `UNKNOWN_TOOLSET`. A disabled tool name that is not registered raises `UNKNOWN_TOOL`. A platform id outside `PLATFORMS` raises `UNKNOWN_PLATFORM`. `PRESETS` is the table `effective` expands. It is not a comment beside the call.

Name, list, and registry caps are policy (`NAME_CAP` 64, `LIST_CAP` 32, `REGISTRY_CAP` 64). A higher or lower requested cap does not move the recorded cap. A cap that is not a positive int raises `BAD_CAP`. An expanded allow list longer than `LIST_CAP` raises `OVER_CAP`.

## Authority

The human allow list and deny list are the authority. The registry does not grant a toolset. `PRESETS` only expands names the human already listed. This module does not execute a tool, open a socket, or write a file.

## Refusal codes

`EMPTY_ALLOW`, `MESSAGING_TERMINAL`, `UNKNOWN_TOOLSET`, `UNKNOWN_TOOL`, `UNKNOWN_PLATFORM`, `BAD_NAME`, `BAD_RISK`, `BAD_RECORD`, `BAD_CAP`, `DUPLICATE`, `NOT_LIST`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `OVER_CAP`, `SECRET_SHAPE`.

`NOT_TEXT`, `NULL_BYTE`, and `OVERSIZE` come from `bound_text`.

## Landing

CCr would call `effective` at the hand-allowlist edge before a turn builds model-visible tool schemas, and would pass only `Effective.tools` forward. `cosmos_approval.py` still gates execution. Messaging adapters pass their platform name and their saved allow and deny lists. A stock messaging preset is refused while its resolved tuple still contains `terminal`. A refusal is the result the turn shows. It is not replaced with the full registry.

## Ship

- operations: `LIST_CAP`, `NAME_CAP`, `PLATFORMS`, `PRESETS`, `REGISTRY_CAP`, `RISKS`, `SCHEMA`, `Catalog`, `Effective`, `Tool`, `effective`, `new_catalog`, `rebuild`, `register`
- refusal codes: `EMPTY_ALLOW`, `MESSAGING_TERMINAL`, `UNKNOWN_TOOLSET`, `UNKNOWN_TOOL`, `UNKNOWN_PLATFORM`, `BAD_NAME`, `BAD_RISK`, `BAD_RECORD`, `BAD_CAP`, `DUPLICATE`, `NOT_LIST`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `OVER_CAP`, `SECRET_SHAPE`
- still refuses to execute: a tool call, a terminal, a socket, a file write, expansion of `all` or `*`, and any non-cli grant whose resolved allow list or remaining tools still include a terminal tool. An empty or missing allow list is a refusal.
- hot-path shape: expand preset names once, then one pass over the catalog with set membership. A denied toolset or a named disabled tool is dropped and later tools that remain allowed are kept. A terminal tool on a non-cli platform refuses the grant.
