# video_gen

Hermes keeps video generation behind an opt-in toolset. `video_generate` is one tool for a text prompt, and a configured plugin backend (xAI, FAL, OpenRouter, or DeepInfra) renders it. Passing an image URL is image-to-video; omitting it is text-to-video. Duration, aspect, and resolution are backend capabilities. A backend publishes a minimum and a maximum duration and may clamp. The model id is user configuration, not an agent billing switch. `xai_video_edit` and `xai_video_extend` are separate credential-gated tools. The live product returns a video URL or path. This proposal returns a priced plan and does not render.

The live seam is `cosmos/cosmos_spend.py` (`SpendGate`). Video spend is not a second gate. A model absent from the caller price table is `UNPRICED`. A quoted zero stays zero and `spend_required` stays true. No live module owns a video descriptor. The descriptor is new; the spend decision is not.

`request` builds a frozen `VideoRequest`. `plan` binds a credential id and returns a frozen `VideoPlan`. The allowlist is `grok-video` and `local-noop`. Duration bounds are the typed helpers `duration_lo` and `duration_hi` (1 and 12 seconds). `apply_duration` applies them. An ask below 1 refuses. An ask above 12, up through `ASK_CEILING`, records 12 in `seconds` and `duration_cap` and keeps the ask in `requested_seconds`. The module does not multiply cents by seconds. The prompt cap is 2000 characters. `apply_prompt_cap` records 2000 when the caller asks for more, and a lower positive ask does not shrink it. `spend_required` stays true. `renders` stays false. `run` validates a plan and raises `NOT_RENDER`. It does not open a socket and it does not write a file. Image-to-video, edit, and extend stay outside this descriptor. `local-noop` is still a priced plan. It does not skip the price table. The price table holds at most 32 keys. `rebuild` replays at most 64 plans.

The ledger is the spend authority. A human chooses the model, supplies the price table, and supplies a credential id. This module accepts no key material.

Refusal codes: `UNKNOWN_MODEL`, `SECRET`, `UNPRICED`, `EMPTY`, `BAD_PRICES`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_CAP`, `BAD_SCHEMA`, `MISSING_CREDENTIAL`, `BAD_CREDENTIAL`, `BAD_FLAG`, `BAD_PLAN`, `NOT_RENDER`, `REPLAY`.

CCr would land this in front of `SpendGate`: the attempt calls `plan` with a human-approved price table and a credential id from `cosmos_cred_kit`, reserves `cents`, and only then lets a rail render. This module never renders.

## Ship

- operations: `ASK_CEILING`, `MAX_CENTS`, `MIN_SECONDS`, `MODELS`, `POLICY_SECONDS`, `PROMPT_CAP`, `SCHEMA`, `VideoPlan`, `VideoRequest`, `apply_duration`, `apply_prompt_cap`, `duration_hi`, `duration_lo`, `plan`, `rebuild`, `request`, `run`
- refusal codes: `UNKNOWN_MODEL`, `SECRET`, `UNPRICED`, `EMPTY`, `BAD_PRICES`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_CAP`, `BAD_SCHEMA`, `MISSING_CREDENTIAL`, `BAD_CREDENTIAL`, `BAD_FLAG`, `BAD_PLAN`, `NOT_RENDER`, `REPLAY`
- what this module still refuses to execute: rendering a video, opening a socket, writing a file, reading a key, raising the prompt cap or the duration cap, image-to-video, edit, extend, and any retry
- hot-path shape: one pass over the price table, a set lookup for the model, and `apply_duration` for the seconds. A higher duration ask records the policy cap and does not drop the plan. The prompt is bounded and secret-checked in the seal. `plan` hashes the sealed fields once. `rebuild` is one pass and refuses a repeated plan id.
