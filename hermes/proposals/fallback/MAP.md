# Fallback

Hermes can switch a live session from the primary provider to a different provider and model when the primary fails, then try the primary again on the next user message. Inside one turn the backup is spent once. If that backup also fails, Hermes stops walking the chain and surfaces the error. Credential pools rotate keys on the same provider and are not this feature. Vision and context compression keep their own failure counters. Hermes will also switch on authentication failures and missing models, and it will walk several backups. This proposal keeps one backup. The confirming classes are `RATE`, `HTTP_429`, `TIMEOUT`, `SERVER`, `HTTP_500`, `HTTP_502`, and `HTTP_503`. Auth, payment, not-found, and the other terminal codes do not switch.

The live seam is one backup. Provider selection sits beside the provider rails. `cosmos_spend.py` remains the spend authority. `cosmos_cred_kit.py` remains the credential store. This module returns a descriptor and does not call those modules.

`configure` takes a primary endpoint, zero or more fallback endpoints, a provider allowlist, and a requested cap. The policy keeps the first fallback and counts the rest as dropped. A requested cap above 1 is stored on `requested` and is not applied. The recorded `cap` is 1. `fail` appends one refusal to a caller-supplied log for a turn id and a channel (`chat`, `vision`, or `compress`). The first refusal on that turn must name the primary and a confirming class. `switch` then returns that backup once. The next refusal must name the backup. `switch` on a turn that already holds both refusals raises `EXHAUSTED` and does not name another route. A new turn id starts on the primary again, including when it is appended to the same log. `rebuild` replays the log into the same public snapshot: one confirming spend, and an ended turn with no active route.

The human names the primary, the fallback list, and the allowlist. The attempt owns the log and the timestamps. A later ledger write sits outside this module.

## Ship

- operations: `CHANNELS`, `ELIGIBLE`, `POLICY_CAP`, `SCHEMA`, `TERMINAL`, `Choice`, `Endpoint`, `Policy`, `Record`, `Snapshot`, `Turn`, `configure`, `fail`, `rebuild`, `switch`
- refusal codes: `BAD_ALLOW`, `BAD_CAP`, `BAD_CHAIN`, `BAD_CHANNEL`, `BAD_CODE`, `BAD_ROUTE`, `BAD_TURN`, `BROKEN_CHAIN`, `DUPLICATE`, `EMPTY_ALLOW`, `EXHAUSTED`, `MISSING_CRED`, `NO_FALLBACK`, `NOT_ALLOWED`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SAME_PROVIDER`, `SECRET`, `STALE`, `UNCLASSIFIED`
- what this module still refuses to execute: a second backup, a retry loop, sleep, a cooldown thread, credential-pool rotation, resolving key material, opening a socket, rebuilding an HTTP client, editing the prompt cache, and any auxiliary, delegation, or cron route that was not named in this policy
- hot-path shape: one pass over the fallback list (an invalid row refuses; the first valid row fills the only slot; later valid rows increment `dropped`); `switch` verifies the log once, then reads that turn's channel once
