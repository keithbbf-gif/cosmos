# home_assistant

Hermes exposes a `homeassistant` toolset with four tools: `ha_list_entities`, `ha_get_state`, `ha_list_services`, and `ha_call_service`. A configured token arms the toolset in the product. Service calls change devices. State and list tools read them. Entity ids are `domain.object`. The product blocks service domains `shell_command`, `command_line`, `python_script`, `pyscript`, `hassio`, and `rest_command`. The messaging gateway that subscribes to `state_changed` is a separate platform, not this toolset.

The live seam is confirm, never run. Seam: an approval descriptor. No HTTP call to a Home Assistant host. No COSMOS module opens that socket. This package does not import the approval module.

`Home` starts disabled. `enable(cred_id)` arms it with a credential id. A missing id, a raw token, or a second different id refuses, and there is no off switch. `service`, `state`, `list_entities`, and `list_services` return a frozen `Call`. `classify` returns `CONFIRM` for a valid call, including a state read. `run` raises `NOT_RUN` after that check and does not touch a network or a device. Shell metacharacters in any field raise `BAD_ENTITY`. A caller who asks for a higher field cap, list cap, state cap, or plan budget is ignored, and the policy cap is recorded. `plan` keeps a call that fits the remaining character budget and skips a call that does not, then still considers later calls. `retry` rebuilds the same call once when the failure is `STALE`. `rebuild` replays a plan snapshot. `catalog` is the effective service allowlist and does not enable the toolset.

`volume_level`, cover `position`, and fan `percentage` are integer percents from 0 to 100. Brightness is an integer from 0 to 255. Climate `temperature` is an integer Celsius from 0 to 40. `hvac_mode` value `off` is climate data, not an off switch for this module. A repeated call digest inside one plan refuses.

Authority is a human grant on the approval ledger. This module holds a credential id only. It holds no token, no socket, and no device handle.

CCr would land this later by submitting each `Call` to `cosmos_approval` as `CONFIRM` and binding one consumed grant to that call's digest. REST, websocket subscribe, persistent notifications, and device dispatch stay outside this package. `run` remains a refusal until that grant exists. Blocked domains stay blocked. The caps stay at their policy values.

## Ship

- operations: `AREA_CAP`, `BLOCKED_DOMAINS`, `CALL_DOMAINS`, `CONFIRM`, `CRED_CAP`, `Call`, `ENTITY_CAP`, `FAILURE`, `Field`, `Home`, `MAX_STAMP`, `NAME_CAP`, `POLICY_BUDGET`, `POLICY_FIELDS`, `POLICY_ITEMS`, `POLICY_LIST`, `POLICY_STATE`, `Plan`, `READ_DOMAINS`, `SCHEMA`, `SERVICES`, `Skip`, `Step`, `TOOLS`, `catalog`, `classify`, `rebuild`, `retry`, `run`, `weight`. Methods: `enable`, `service`, `state`, `list_entities`, `list_services`, `plan`, `enabled`, `credential_id`.
- refusal codes: `BAD_AREA`, `BAD_CAP`, `BAD_CRED`, `BAD_DATA`, `BAD_DOMAIN`, `BAD_ENTITY`, `BAD_KIND`, `BAD_RECORD`, `BAD_SCHEMA`, `BAD_SERVICE`, `BLOCKED_DOMAIN`, `BROKEN_CHAIN`, `DISABLED`, `DUPLICATE`, `EMPTY`, `MISMATCH`, `NOT_INT`, `NOT_LIST`, `NOT_MAP`, `NOT_RUN`, `NOT_TEXT`, `NO_CRED`, `NO_RETRY`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `RETRY_CAP`, `SECRET`, `STALE`, `UNCLASSIFIED`.
- what this module still refuses to execute: Home Assistant REST, websocket subscribe, `state_changed` forwarding, persistent notifications, device service calls, state reads, shell and script domains, a cap above policy, a second confirming retry, and any retry whose failure is not `STALE`.
- hot-path shape: one pass over at most 32 calls; set membership for domains, blocked domains, services, colors, hvac modes, and digests already seen; a call whose weight exceeds the remaining budget is skipped and later calls are still considered. Each kept step is hashed once in that pass. `rebuild` hashes again as the check.
