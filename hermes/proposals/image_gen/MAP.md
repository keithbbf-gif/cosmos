# image_gen

Hermes turns a text prompt into an image through one configured backend. The agent names an allowlisted model. It may ask for landscape, square, or portrait, and the request records that model's native size token. Upscale stays off unless the call opts in. A source count is an edit, and only some models accept one. GPT Image quality stays medium so the bill does not jump a tier. The live product returns a hosted image. This proposal returns a priced plan and does not open a socket or return image bytes.

The live seam is `cosmos/cosmos_spend.py` (`SpendGate`). Image spend is not a second gate. A model absent from the caller price table is `UNPRICED`. A quoted zero stays zero and `priced` is true. An opted-in upscale needs an `upscale` cent quote in that same table.

`request` builds a frozen `ImageRequest`. `native_size` maps the aspect onto the model preset. `dispatch` binds a credential id and returns a `GenerationJob` plan. The plan stores a prompt digest and a `plan_id`. `rebuild` replays those jobs and reproduces the same public state. A repeated plan id is `REPLAY`. A digest that does not match the prompt is `BAD_JOB`. It does not generate an image. `MODELS` is the allowlist: `flux-2-klein`, `flux-2-pro`, `gpt-image-1.5`, `gpt-image-2`, `nano-banana-pro`, `ideogram-v3`, `recraft-v4`, `qwen-image`, `z-image-turbo`, `krea-v2`. The prompt cap is 2000 characters and is stored on the request. A caller cap is ignored. The price table holds at most 32 keys.

The ledger is the spend authority. A human chooses the model and supplies the price table. This module accepts a credential id and refuses key-shaped text. It writes no file.

Refusal codes: `UNKNOWN_MODEL`, `SECRET`, `UNPRICED`, `EMPTY`, `BAD_PRICES`, `BAD_ASPECT`, `BAD_FLAG`, `NO_EDIT`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `MISSING_CREDENTIAL`, `BAD_CREDENTIAL`, `BAD_ORDER`, `BAD_CAP`, `BAD_QUALITY`, `BAD_CATALOG`, `BAD_JOB`, `REPLAY`.

CCr would land this in front of `SpendGate`: the attempt calls `request` with a human-approved price table, reserves `cents`, and only then lets a rail perform the generation with the credential id from `cosmos_cred_kit`. The proposal stays free of network, files, and a second spender.

## Ship

Operations: `ASPECTS`, `CATALOG`, `DEFAULT_MODEL`, `MAX_CENTS`, `MODELS`, `PROMPT_CAP`, `SCHEMA`, `SOURCE_CAP`, `GenerationJob`, `ImageRequest`, `ModelSpec`, `dispatch`, `native_size`, `rebuild`, `request`.

Refusal codes: `UNKNOWN_MODEL`, `SECRET`, `UNPRICED`, `EMPTY`, `BAD_PRICES`, `BAD_ASPECT`, `BAD_FLAG`, `NO_EDIT`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `MISSING_CREDENTIAL`, `BAD_CREDENTIAL`, `BAD_ORDER`, `BAD_CAP`, `BAD_QUALITY`, `BAD_CATALOG`, `BAD_JOB`, `REPLAY`.

This module still refuses to generate image bytes, open a socket, write a file, read a key, raise the prompt cap, retry a delivery, or run an upscaler.

Hot path: one pass over the price table, a dict lookup for the model, and a set check for the aspect. Each call is one plan, so a later cheaper shot is not dropped by a selection loop. A caller's cap is not applied. `dispatch` hashes the prompt once; the job hashes it again only to check the digest with `const_eq`. `rebuild` is one pass and refuses a repeated plan id.
