# REFUSAL TAXONOMY — every `*Error(kind, detail)` in `cosmos/`

**GENERATED — do not hand-edit.** Source is the code; this file is a
projection. Regenerate:

```
py -3.14 cosmos\cosmos_refusals.py --render > docs\REFUSAL_TAXONOMY.md
```

Modules parsed: **160** · error classes: **55** · carrying the `(kind, detail)` shape: **55** · distinct kinds: **141**

## Typed refusals — branch on `kind`

| Class | Module | Kinds raised (sites) | Declared in docstring | `except` sites |
|---|---|---|---|---|
| `AskmineRefusal` | `cosmos_askmine` | `IDENTITY_MISMATCH`×1, `NO_TRANSCRIPT`×1 | `IDENTITY_MISMATCH`, `NO_CONFIG`, `NO_ROOT`, `NO_TRANSCRIPT` | 1 |
| `BackupError` | `cosmos_backup` | `EMPTY_SCOPE`×2, `REHEARSAL_FAILED`×4, `SECRETS_IN_SCOPE`×2, `SNAPSHOT_INCOMPLETE`×1, `SOURCE_UNREADABLE`×3, `TARGET_MISSING`×1, `VERIFY_MISMATCH`×1 | `EMPTY_SCOPE`, `REHEARSAL_FAILED`, `SECRETS_IN_SCOPE`, `SNAPSHOT_INCOMPLETE`, `SOURCE_UNREADABLE`, `TARGET_MISSING`, `VERIFY_MISMATCH` | 2 |
| `WorkerError` | `cosmos_bucket_daemon` | `BAD_NODE`×1, `BAD_OUT`×1, `BAD_TASK`×4, `NO_DEST`×3, `NO_KEY`×1, `NO_ROOT`×1, `REPLAY`×1 | `BAD_NODE`, `BAD_OUT`, `BAD_TASK`, `NO_DEST`, `NO_KEY`, `NO_ROOT`, `REPLAY` | 7 |
| `ClaudeRailError` | `cosmos_claude_rail` | `BAD_INPUT`×1, `BAD_SPEC`×12, `BROKE`×1, `NO_KEY`×4, `REFUSED`×1 +3 dynamic | `BAD_INPUT`, `BAD_ROOT`, `BAD_SPEC`, `BROKE`, `NO_KEY`, `REFUSED`, `UNREACHABLE` | 10 |
| `CodexRailError` | `cosmos_codex_rail` | `BAD_SPEC`×12, `BROKE`×2, `NO_KEY`×4, `REFUSED`×1 +2 dynamic | `BAD_ROOT`, `BAD_SPEC`, `BROKE`, `NO_KEY`, `REFUSED`, `UNREACHABLE` | 10 |
| `CommandError` | `cosmos_command` | `BAD_ARGS`×9, `KERNEL_REFUSED`×1, `REFUSED`×1, `UNKNOWN_COMMAND`×1 | `BAD_ARGS`, `KERNEL_REFUSED`, `REFUSED`, `UNKNOWN_COMMAND` | 2 |
| `CompetencyError` | `cosmos_competency` | `BAD_SCHEMA`×8, `NO_CANDIDATE`×1, `NO_DISPATCH`×1, `UNKNOWN_TASK`×1, `UNREADABLE`×2 | `BAD_SCHEMA`, `NO_CANDIDATE`, `NO_DISPATCH`, `UNKNOWN_TASK`, `UNREADABLE` | 2 |
| `ContextError` | `cosmos_context` | `ALREADY_CLOSED`×2, `NOT_OPEN`×1, `UNRESOLVED`×2 | `ALREADY_CLOSED`, `NOT_OPEN`, `UNRESOLVED` | 2 |
| `ContextPullError` | `cosmos_context_pull` | — | `NO_ROOT`, `NO_TRANSCRIPT` | 0 |
| `ContractError` | `cosmos_contracts` | `BAD_CONTRACT`×1, `NO_CONTRACTS`×1 | `BAD_CONTRACT`, `NO_CONTRACTS`, `NO_ROOT` | 2 |
| `ControlError` | `cosmos_control` | `STATE_UNREADABLE`×1 | `STATE_UNREADABLE` | 3 |
| `ConvoError` | `cosmos_convo` | `BAD_ROLE`×1, `BAD_SCOPE`×1, `BAD_TURN`×8, `NO_SESSION`×5 +1 dynamic | `BAD_ROLE`, `BAD_SCOPE`, `BAD_TURN`, `NO_SESSION` | 2 |
| `ConsumerError` | `cosmos_crit_consumer` | `BAD_KIND`×1, `NO_ROOT`×1, `REPLAY`×1 | `BAD_KIND`, `BAD_PACKET`, `EMPTY_OUTPUT`, `FENCE_LOST`, `REPLAY` | 2 |
| `CrucibleError` | `cosmos_crucible` | `EMPTY_SOURCE`×2, `NO_CRITICS`×1, `PACKET_INCOMPLETE`×1 | `EMPTY_SOURCE`, `NO_CRITICS`, `PACKET_INCOMPLETE` | 1 |
| `CursorRailError` | `cosmos_cursor_rail` | `BAD_SPEC`×10, `BROKE`×2, `NO_KEY`×4, `REFUSED`×1 | `BAD_ROOT`, `BAD_SPEC`, `BROKE`, `NO_KEY`, `REFUSED`, `UNREACHABLE` | 8 |
| `CvmError` | `cosmos_cvm_projection` | `BAD_SNAPSHOT`×6, `CLIENT_ID_REQUIRED`×1, `IDENTITY_MISMATCH`×1, `NOT_FOUND`×1, `OWNER_CONTESTED`×1, `UNPARSEABLE`×2, `UNREACHABLE`×1, `UNREADABLE`×1 +1 dynamic | — | 4 |
| `DispatchError` | `cosmos_dispatch_workspace` | `BAD_INPUT`×10, `BROKE`×4, `IO`×1, `NO_DIR`×4, `NO_KEY`×5, `NO_LANE`×1, `NO_QUEUE`×1, `NO_ROOT`×3, `REFUSED`×6 | — | 5 |
| `DomError` | `cosmos_dom` | — | `AUTH_REQUIRED`, `BROKE`, `SESSION_EXPIRED`, `UNREACHABLE` | 0 |
| `FirecrawlRailError` | `cosmos_firecrawl_rail` | `BAD_SPEC`×7, `REFUSED`×1 | `AUTH_REQUIRED`, `BAD_ROOT`, `BAD_SPEC`, `BROKE`, `REFUSED`, `UNREACHABLE` | 2 |
| `ForgeRailError` | `cosmos_forge_rail` | `BAD_ROOT`×1, `BAD_SPEC`×7, `REFUSED`×2, `UNREACHABLE`×2 | `BAD_ROOT`, `BAD_SPEC`, `REFUSED`, `UNREACHABLE` | 8 |
| `FederationError` | `cosmos_identity` | `UNKNOWN_NODE`×1 | `NO_HOST`, `UNKNOWN_NODE`, `UNREACHABLE` | 0 |
| `InflightError` | `cosmos_inflight` | `NO_TOKEN`×2, `READ_FAILED`×1, `WRITE_FAILED`×1 | — | 1 |
| `IngressError` | `cosmos_ingress` | `BAD_ENVELOPE`×3, `HASH_MISMATCH`×1, `SHORT_PAYLOAD`×1, `UNKNOWN_KIND`×1 | `BAD_ENVELOPE`, `HASH_MISMATCH`, `SHORT_PAYLOAD`, `UNKNOWN_KIND` | 1 |
| `ItcError` | `cosmos_itc` | `BAD_INDEX`×5, `NOT_FOUND`×1, `STALE`×2, `UNREACHABLE`×3 | `BAD_INDEX`, `NOT_FOUND`, `STALE`, `UNREACHABLE` | 3 |
| `KdashError` | `cosmos_kdash` | `BAD_ENTRY`×8, `BAD_PAGE`×3, `CDN_FORBIDDEN`×1, `MISSING_PANEL`×7, `UNKNOWN_KIND`×3, `UNREACHABLE`×2 +1 dynamic | `BAD_ENTRY`, `BAD_PAGE`, `CDN_FORBIDDEN`, `MISSING_PANEL`, `NOT_FOUND`, `UNAUTHORIZED`, `UNKNOWN_KIND`, `UNREACHABLE` | 0 |
| `LedgerError` | `cosmos_ledger` | `BROKEN_CHAIN`×10, `FORGED`×2, `HASH_MISMATCH`×1, `NOT_FOUND`×1, `STALE_HEAD`×1, `TORN`×2, `UNREADABLE`×2 +1 dynamic | `BROKEN_CHAIN`, `FORGED`, `STALE_HEAD`, `TORN`, `UNREADABLE` | 7 |
| `LockError` | `cosmos_lock` | `BAD_STAGE`×1, `FORGED_EVENT`×1, `HELD`×1, `NO_LEASE`×3, `REENTRANT`×1, `STALE_TOKEN`×5, `TORN_LEDGER`×3 | `BAD_STAGE`, `FORGED_EVENT`, `HELD`, `NO_LEASE`, `REENTRANT`, `STALE_TOKEN`, `TORN_LEDGER`, `UNKNOWN_RESOURCE` | 0 |
| `MailError` | `cosmos_mail` | `CHAIN_BREAK`×1, `FORGED_MESSAGE`×1, `MAILBOX_MISSING`×2, `SELF_SEND`×1, `TORN_MESSAGE`×5 | `CHAIN_BREAK`, `FORGED_MESSAGE`, `MAILBOX_MISSING`, `SELF_SEND`, `TORN_MESSAGE`, `UNREADABLE` | 0 |
| `MakerError` | `cosmos_makers` | `BAD_ENTRY`×6, `DUPLICATE`×2, `UNKNOWN_KIND`×2, `UNREADABLE`×3 +1 dynamic | `BAD_ENTRY`, `DUPLICATE`, `UNKNOWN_KIND`, `UNREADABLE` | 4 |
| `McpClientError` | `cosmos_mcp_client` | `BAD_SPEC`×3, `BROKE`×3, `DENIED`×2, `UNREACHABLE`×10 | `BAD_SPEC`, `BROKE`, `DENIED`, `TIMEOUT`, `UNREACHABLE` | 6 |
| `ScoutError` | `cosmos_newai_scout` | `BAD_CATALOG`×1 | `BAD_CATALOG`, `NO_ROOT`, `UNREACHABLE` | 1 |
| `WorkerError` | `cosmos_node_bucket_worker` | `BAD_NODE`×1, `BAD_OUT`×1, `BAD_TASK`×4, `NO_DEST`×3, `NO_KEY`×1, `NO_ROOT`×1, `REPLAY`×1 | `BAD_NODE`, `BAD_OUT`, `BAD_TASK`, `NO_DEST`, `NO_KEY`, `NO_ROOT`, `REPLAY` | 5 |
| `WorkerError` | `cosmos_node_worker` | `BAD_NODE`×2, `BAD_OUT`×1, `BAD_TASK`×4, `NO_DEST`×2, `NO_KEY`×1, `NO_ROOT`×2 | `BAD_NODE`, `BAD_OUT`, `BAD_TASK`, `NO_DEST`, `NO_KEY`, `NO_ROOT` | 11 |
| `OrchestratorError` | `cosmos_orchestrator` | `BAD_INPUT`×3, `BAD_MODEL_RESPONSE`×2, `MODEL_FAILED`×1 | `BAD_INPUT`, `BAD_MODEL_RESPONSE`, `MODEL_FAILED` | 0 |
| `CosmosPathError` | `cosmos_paths` | `IDENTITY_MISMATCH`×6, `NOT_A_DIRECTORY`×1, `NOT_FOUND`×9, `UNPARSEABLE`×4, `UNREADABLE`×2 | `IDENTITY_MISMATCH`, `NOT_A_DIRECTORY`, `NOT_FOUND`, `UNPARSEABLE`, `UNREADABLE` | 42 |
| `PlatformError` | `cosmos_platform` | `SHELL_REFUSED`×2 | `KILL_INCOMPLETE`, `SHELL_REFUSED`, `TIMEOUT` | 0 |
| `PlaywrightRailError` | `cosmos_playwright_rail` | `BAD_SPEC`×7, `REFUSED`×1 | `BAD_ROOT`, `BAD_SPEC`, `BROKE`, `DENIED`, `REFUSED`, `UNREACHABLE` | 2 |
| `PrepaidOrchError` | `cosmos_prepaid_orch` | `CLAUDE_SPEND`×1, `NO_RAIL`×1 | `CLAUDE_SPEND`, `HOLD`, `NO_RAIL`, `NO_ROOT` | 2 |
| `RailError` | `cosmos_rail_base` | `BROKE`×1 | `BAD_ROOT`, `BAD_SPEC`, `BROKE`, `NO_KEY`, `REFUSED`, `UNREACHABLE` | 2 |
| `RailError` | `cosmos_rails` | `NOT_PERMITTED`×1, `NO_LIVE_LINK`×2, `RAIL_FAILED`×2 | `NOT_PERMITTED`, `NO_LIVE_LINK`, `RAIL_FAILED` | 7 |
| `RegError` | `cosmos_registry` | `BAD_TYPE`×2, `NO_PROBE`×1, `UNKNOWN_LINK`×1 | `BAD_TYPE`, `NO_PROBE`, `UNKNOWN_LINK` | 1 |
| `ResessionRefusal` | `cosmos_resession` | `NO_RAIL`×2 | `BAD_SEED`, `CLOSE_REFUSED`, `HELD`, `HOLD`, `IDENTITY_MISMATCH`, `NO_DECL`, `NO_PROMPT`, `NO_RAIL`, `NO_SEED` | 1 |
| `SchedError` | `cosmos_sched` | `BAD_PRIORITY`×1, `BAD_STATE`×4, `LOST_CLAIM`×1, `UNKNOWN_JOB`×1 | `BAD_PRIORITY`, `BAD_STATE`, `LOST_CLAIM`, `UNKNOWN_JOB` | 1 |
| `ServiceError` | `cosmos_service` | `BLANK_TOKEN`×1, `CERT_NOT_FOUND`×1, `REMOTE_CLEARTEXT`×1, `REMOTE_OPEN_ACCESS`×1, `TOKEN_MISSING`×1 | `BLANK_TOKEN`, `CERT_NOT_FOUND`, `REMOTE_CLEARTEXT`, `REMOTE_OPEN_ACCESS`, `TOKEN_MISSING` | 2 |
| `SessionError` | `cosmos_session` | `ALREADY_OPEN`×1, `BAD_SEED`×9, `BAD_STREAM`×1, `CONTROL_INVALID`×1, `IDENTITY_MISMATCH`×4, `NOT_FOUND`×2, `NO_SEED`×1, `UNPARSEABLE`×2 | `ALREADY_OPEN`, `BAD_SEED`, `BAD_STREAM`, `CONTROL_INVALID`, `IDENTITY_MISMATCH`, `NOT_FOUND`, `NO_SEED`, `UNPARSEABLE` | 2 |
| `SpendError` | `cosmos_spend` | `DENIED`×3, `UNKNOWN_RAIL`×1 | `DENIED`, `DOUBLE_SETTLE`, `RESERVATION_EXPIRED`, `UNKNOWN_RAIL` | 4 |
| `SpendAdminError` | `cosmos_spend_admin` | `BAD_CAP`×3, `BAD_EXPIRY`×1, `BAD_FIELD`×4, `BAD_RAIL`×1, `BAD_REQUEST`×1, `BAD_TARGET`×2, `BAD_THRESHOLD`×4, `BELOW_OUTSTANDING`×1, `CURRENT_UNREADABLE`×4, `GUARD_NOT_COMPOSED`×1, `LEDGER_REFUSED`×2, `ROUND_TRIP_UNVERIFIED`×3, `SPEND_NOT_COMPOSED`×1, `WIDEN_REQUIRES_CONFIRM`×2 +2 dynamic | — | 3 |
| `SttError` | `cosmos_stt` | `BAD_WAV`×3, `STT_NONE`×1 | `BAD_WAV`, `NO_MODEL`, `STT_NONE` | 1 |
| `SurfaceError` | `cosmos_surfaces` | `DUPLICATE`×1, `UNKNOWN_SURFACE`×2, `UNQUALIFIED`×3 | `DUPLICATE`, `UNKNOWN_SURFACE`, `UNQUALIFIED`, `UNREACHABLE` | 0 |
| `ToolsError` | `cosmos_tools` | `BAD_DISPOSITION`×1, `CONTRACT_FAIL`×2, `DUPLICATE`×1, `UNKNOWN_TOOL`×3 | `BAD_DISPOSITION`, `CONTRACT_FAIL`, `DUPLICATE`, `UNKNOWN_TOOL` | 4 |
| `UpError` | `cosmos_up` | `NO_CERT`×2 | `BAD_STATE`, `NOT_LOGGED_IN`, `NO_CERT`, `NO_TAILSCALE` | 1 |
| `ValidateError` | `cosmos_validate` | `FAILED_VALIDATION`×1, `HASH_MISMATCH`×1, `NO_VALIDATOR`×1, `SHORT_READ`×1, `UNVALIDATED`×1 | `FAILED_VALIDATION`, `HASH_MISMATCH`, `NO_VALIDATOR`, `SHORT_READ`, `UNVALIDATED` | 1 |
| `VoiceError` | `cosmos_voice` | `BAD_INPUT`×2, `NO_SESSION`×1 | `BAD_INPUT`, `NO_SESSION` | 1 |
| `OrderError` | `cosmos_work_order` | `BAD_INPUT`×18, `BROKE`×3, `FAILED`×3, `REFUSED`×7 | `BAD_INPUT`, `BROKE`, `FAILED`, `NO_CONTEXT`, `REFUSED` | 5 |
| `WorkspaceError` | `cosmos_workspace` | `BROKE`×5, `NO_CONTEXT`×3, `REFUSED`×5 | `BROKE`, `NO_CONTEXT`, `REFUSED` | 7 |

## Untyped error classes — a message, not a kind

Listed so the boundary is explicit: a caller CANNOT branch on `kind` for these.

**None.** Every error class in `cosmos/` already carries the `(kind, detail)` shape — the taxonomy is uniform at the class level, and what remains to unify is the VOCABULARY below.

## Collisions — one kind string, more than one class

| Kind | Classes | Verdict | Note |
|---|---|---|---|
| `BAD_ENTRY` | `cosmos_kdash.KdashError`, `cosmos_makers.MakerError` | **BENIGN** | one meaning: a record in a declarative list is malformed |
| `BAD_INPUT` | `cosmos_claude_rail.ClaudeRailError`, `cosmos_dispatch_workspace.DispatchError`, `cosmos_orchestrator.OrchestratorError`, `cosmos_voice.VoiceError`, `cosmos_work_order.OrderError` | **BENIGN** | one meaning: a caller-supplied argument is invalid |
| `BAD_NODE` | `cosmos_bucket_daemon.WorkerError`, `cosmos_node_bucket_worker.WorkerError`, `cosmos_node_worker.WorkerError` | **BENIGN** | one meaning: the node spec is malformed |
| `BAD_OUT` | `cosmos_bucket_daemon.WorkerError`, `cosmos_node_bucket_worker.WorkerError`, `cosmos_node_worker.WorkerError` | **BENIGN** | one meaning: the output target is unusable |
| `BAD_SPEC` | `cosmos_claude_rail.ClaudeRailError`, `cosmos_codex_rail.CodexRailError`, `cosmos_cursor_rail.CursorRailError`, `cosmos_firecrawl_rail.FirecrawlRailError`, `cosmos_forge_rail.ForgeRailError`, `cosmos_mcp_client.McpClientError`, `cosmos_playwright_rail.PlaywrightRailError` | **BENIGN** | one meaning: the rail spec is malformed |
| `BAD_TASK` | `cosmos_bucket_daemon.WorkerError`, `cosmos_node_bucket_worker.WorkerError`, `cosmos_node_worker.WorkerError` | **BENIGN** | one meaning: the task record is malformed |
| `BROKE` | `cosmos_claude_rail.ClaudeRailError`, `cosmos_codex_rail.CodexRailError`, `cosmos_cursor_rail.CursorRailError`, `cosmos_dispatch_workspace.DispatchError`, `cosmos_mcp_client.McpClientError`, `cosmos_rail_base.RailError`, `cosmos_work_order.OrderError`, `cosmos_workspace.WorkspaceError` | **BENIGN** | one meaning: a programmer error on this seam |
| `DENIED` | `cosmos_mcp_client.McpClientError`, `cosmos_spend.SpendError` | **SYNONYM** | policy declined -- see the policy_declined cluster |
| `DUPLICATE` | `cosmos_makers.MakerError`, `cosmos_surfaces.SurfaceError`, `cosmos_tools.ToolsError` | **BENIGN** | one meaning: an id appears twice in a registry |
| `HASH_MISMATCH` | `cosmos_ingress.IngressError`, `cosmos_ledger.LedgerError`, `cosmos_validate.ValidateError` | **BENIGN** | one meaning: content did not hash to what was declared |
| `IDENTITY_MISMATCH` | `cosmos_askmine.AskmineRefusal`, `cosmos_cvm_projection.CvmError`, `cosmos_paths.CosmosPathError`, `cosmos_session.SessionError` | **BENIGN** | one meaning: what was found is not what was declared |
| `NOT_FOUND` | `cosmos_cvm_projection.CvmError`, `cosmos_itc.ItcError`, `cosmos_ledger.LedgerError`, `cosmos_paths.CosmosPathError`, `cosmos_session.SessionError` | **BENIGN** | one meaning: the named thing is absent; the referent is in detail |
| `NO_DEST` | `cosmos_bucket_daemon.WorkerError`, `cosmos_node_bucket_worker.WorkerError`, `cosmos_node_worker.WorkerError` | **BENIGN** | one meaning: no destination was resolvable |
| `NO_KEY` | `cosmos_bucket_daemon.WorkerError`, `cosmos_claude_rail.ClaudeRailError`, `cosmos_codex_rail.CodexRailError`, `cosmos_cursor_rail.CursorRailError`, `cosmos_dispatch_workspace.DispatchError`, `cosmos_node_bucket_worker.WorkerError`, `cosmos_node_worker.WorkerError` | **BENIGN** | one meaning: a required credential is absent |
| `NO_RAIL` | `cosmos_prepaid_orch.PrepaidOrchError`, `cosmos_resession.ResessionRefusal` | **BENIGN** | one meaning: the named rail is absent or unknown |
| `NO_ROOT` | `cosmos_bucket_daemon.WorkerError`, `cosmos_crit_consumer.ConsumerError`, `cosmos_dispatch_workspace.DispatchError`, `cosmos_node_bucket_worker.WorkerError`, `cosmos_node_worker.WorkerError` | **BENIGN** | one meaning: the COSMOS root did not verify |
| `NO_SESSION` | `cosmos_convo.ConvoError`, `cosmos_voice.VoiceError` | **BENIGN** | one meaning: the named session does not exist |
| `REFUSED` | `cosmos_claude_rail.ClaudeRailError`, `cosmos_codex_rail.CodexRailError`, `cosmos_command.CommandError`, `cosmos_cursor_rail.CursorRailError`, `cosmos_dispatch_workspace.DispatchError`, `cosmos_firecrawl_rail.FirecrawlRailError`, `cosmos_forge_rail.ForgeRailError`, `cosmos_playwright_rail.PlaywrightRailError`, `cosmos_work_order.OrderError`, `cosmos_workspace.WorkspaceError` | **SYNONYM** | policy declined -- see the policy_declined cluster |
| `REPLAY` | `cosmos_bucket_daemon.WorkerError`, `cosmos_crit_consumer.ConsumerError`, `cosmos_node_bucket_worker.WorkerError` | **BENIGN** | one meaning: the fence for this work is already held |
| `UNKNOWN_KIND` | `cosmos_ingress.IngressError`, `cosmos_kdash.KdashError`, `cosmos_makers.MakerError` | **BENIGN** | one meaning: a kind string outside the known set |
| `UNPARSEABLE` | `cosmos_cvm_projection.CvmError`, `cosmos_paths.CosmosPathError`, `cosmos_session.SessionError` | **BENIGN** | one meaning: bytes were read but did not parse |
| `UNREACHABLE` | `cosmos_cvm_projection.CvmError`, `cosmos_forge_rail.ForgeRailError`, `cosmos_itc.ItcError`, `cosmos_kdash.KdashError`, `cosmos_mcp_client.McpClientError` | **BENIGN** | one meaning: the far endpoint did not answer |
| `UNREADABLE` | `cosmos_competency.CompetencyError`, `cosmos_cvm_projection.CvmError`, `cosmos_ledger.LedgerError`, `cosmos_makers.MakerError`, `cosmos_paths.CosmosPathError` | **BENIGN** | one meaning: the bytes could not be read at all |

## Synonym clusters — one concept, several kind strings

The inverse of a collision, and the harder defect: a caller asking one question must know every spelling of the answer.

**`policy_declined`** — `DENIED`, `NOT_PERMITTED`, `REFUSED`

> cosmos_rails.Dispatcher.dispatch catches SpendError('DENIED') and re-raises RailError('NOT_PERMITTED'); cosmos_node_worker, cosmos_bucket_daemon and cosmos_node_bucket_worker each catch the same SpendError('DENIED') and emit a result dict with kind='NOT_PERMITTED'. One spend refusal, two names, and a third ('REFUSED') used for the same concept across the rails, cosmos_command and cosmos_workspace.


## Gaps — docstring vs raise sites

The drift check. `documented_never_raised` is a kind a caller may branch on that can never arrive; `raised_never_documented` is a kind that arrives with nothing telling the caller it exists.

| Class | Documented, never raised | Raised, never documented |
|---|---|---|
| `cosmos_askmine.AskmineRefusal` | `NO_CONFIG`, `NO_ROOT` | — |
| `cosmos_claude_rail.ClaudeRailError` | `BAD_ROOT`, `UNREACHABLE` | — |
| `cosmos_codex_rail.CodexRailError` | `BAD_ROOT`, `UNREACHABLE` | — |
| `cosmos_context_pull.ContextPullError` | `NO_ROOT`, `NO_TRANSCRIPT` | — |
| `cosmos_contracts.ContractError` | `NO_ROOT` | — |
| `cosmos_crit_consumer.ConsumerError` | `BAD_PACKET`, `EMPTY_OUTPUT`, `FENCE_LOST` | — |
| `cosmos_cursor_rail.CursorRailError` | `BAD_ROOT`, `UNREACHABLE` | — |
| `cosmos_dom.DomError` | `AUTH_REQUIRED`, `BROKE`, `SESSION_EXPIRED`, `UNREACHABLE` | — |
| `cosmos_firecrawl_rail.FirecrawlRailError` | `AUTH_REQUIRED`, `BAD_ROOT`, `BROKE`, `UNREACHABLE` | — |
| `cosmos_identity.FederationError` | `NO_HOST`, `UNREACHABLE` | — |
| `cosmos_kdash.KdashError` | `NOT_FOUND`, `UNAUTHORIZED` | — |
| `cosmos_ledger.LedgerError` | — | `HASH_MISMATCH`, `NOT_FOUND` |
| `cosmos_lock.LockError` | `UNKNOWN_RESOURCE` | — |
| `cosmos_mail.MailError` | `UNREADABLE` | — |
| `cosmos_mcp_client.McpClientError` | `TIMEOUT` | — |
| `cosmos_newai_scout.ScoutError` | `NO_ROOT`, `UNREACHABLE` | — |
| `cosmos_platform.PlatformError` | `KILL_INCOMPLETE`, `TIMEOUT` | — |
| `cosmos_playwright_rail.PlaywrightRailError` | `BAD_ROOT`, `BROKE`, `DENIED`, `UNREACHABLE` | — |
| `cosmos_prepaid_orch.PrepaidOrchError` | `HOLD`, `NO_ROOT` | — |
| `cosmos_resession.ResessionRefusal` | `BAD_SEED`, `CLOSE_REFUSED`, `HELD`, `HOLD`, `IDENTITY_MISMATCH`, `NO_DECL`, `NO_PROMPT`, `NO_SEED` | — |
| `cosmos_spend.SpendError` | `DOUBLE_SETTLE`, `RESERVATION_EXPIRED` | — |
| `cosmos_stt.SttError` | `NO_MODEL` | — |
| `cosmos_surfaces.SurfaceError` | `UNREACHABLE` | — |
| `cosmos_up.UpError` | `BAD_STATE`, `NOT_LOGGED_IN`, `NO_TAILSCALE` | — |
| `cosmos_work_order.OrderError` | `NO_CONTEXT` | — |

## Typed classes declaring no kinds at all

These carry `(kind, detail)` but no `kind in {…}` docstring line, so the declared set is unknown to a reader and to this tool.

- `cosmos_cvm_projection.CvmError`
- `cosmos_dispatch_workspace.DispatchError`
- `cosmos_inflight.InflightError`
- `cosmos_spend_admin.SpendAdminError`

## Outside the taxonomy — bare builtin raises

A caller cannot branch on `kind` here, because there is none. Listed by module so the seams that still refuse untyped are visible.

| Module | Bare raises | Classes |
|---|---|---|
| `cosmos_browser` | 6 | `ConnectionError`, `PermissionError` |
| `cosmos_cvm_push` | 6 | `ValueError` |
| `cosmos_service` | 6 | `RuntimeError` |
| `cosmos_spendguard` | 3 | `ValueError` |
| `cosmos_brain` | 2 | `ValueError` |
| `cosmos_pool` | 2 | `ValueError` |
| `_fail_f60_sandbox_against_old` | 1 | `OSError` |
| `_fail_follow_backup_command_against_old` | 1 | `RuntimeError` |
| `_fail_follow_health_against_old` | 1 | `RuntimeError` |
| `cosmos_backup_clock` | 1 | `FileNotFoundError` |
| `cosmos_control` | 1 | `ValueError` |
| `cosmos_ledger_verify` | 1 | `FileNotFoundError` |
| `cosmos_master_desc` | 1 | `RuntimeError` |
| `cosmos_mcp` | 1 | `KeyError` |
| `cosmos_paths` | 1 | `AttributeError` |
| `cosmos_spend_meter` | 1 | `FileNotFoundError` |
