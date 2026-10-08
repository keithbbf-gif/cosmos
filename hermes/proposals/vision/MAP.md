# Vision

Hermes attaches a clipboard image, a local file, or an image URL and sends pixels to a vision-capable model. A text-only model receives a description from an auxiliary vision pass instead. SVG and other non-raster inline types are not sent as pixels. Clipboard readers, rasterizers, and URL fetches run on the host. This proposal does not paste, rasterize, fetch, or call a model.

The live seam is `cosmos/cosmos_spend.py`. That module is the only spend authority: reserve a worst case, deny when the reserve fails, call, then settle. An unpriced call stays `UNPRICED` and is never treated as free. No live module owns image ingest. The descriptor is new; the spend decision is not.

`from_bytes` and `from_path` admit one PNG, JPEG, GIF, or WebP image and return a `LocalImage`. `image_id` is the sha256 of the bounded bytes. The pixels stay with the caller. The ingest ceiling is 2000000 bytes. `from_path` takes a `PathJail` and an absolute path, bounds that text, and reads at most the ceiling. A read that raises `OSError` or returns the wrong length gets one confirming retry, then `UNREADABLE`. `from_url` refuses. A secret-shaped URL is `SECRET` and is not echoed. A missing credential id is `NO_CRED`. There is no `off` and no `yolo`.

`choose_route` maps `auto`, `native`, and `text`. `auto` is native only when the caller says the model is vision-capable and no auxiliary vision backend is set. Otherwise `auto` is `describe`. `text` is always `describe`. `native` is always `native`. `request` binds one local image id, a credential id, a prompt, and a price table into a frozen `VisionRequest`. `assemble` walks at most 8 images once. An image that is already at the call cap, or that does not fit the remaining byte budget, is skipped. A later image that fits is kept. Duplicate ids refuse. `rebuild` replays that batch.

A caller who asks for a byte cap, an embed cap, or a call cap above policy is ignored. The descriptor records the policy ceiling: 2000000 bytes, 262144 embed bytes, and 3 calls. It does not raise that ceiling. A tighter ask from 1 through the ceiling is recorded as asked. An image inside the byte ceiling but above the embed ceiling stays on the descriptor with `fits_embed` false. This module does not downscale it. `spend_required` stays true. A quoted zero stays zero and `priced` stays true. A route missing from the price table is `UNPRICED`.

Authority lives on the ledger. A human supplies the price table and the credential id. `cosmos_cred_kit` would resolve the id later. This module accepts only the id and refuses key-shaped text.

Refusal codes: `NOT_BYTES`, `EMPTY`, `OVERSIZE`, `UNSUPPORTED_FORMAT`, `BAD_JAIL`, `BAD_PATH`, `NOT_FILE`, `UNREADABLE`, `NO_FETCH`, `NOT_TEXT`, `NULL_BYTE`, `SECRET`, `NO_CRED`, `BAD_CRED`, `UNPRICED`, `BAD_PRICES`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_IMAGE`, `BAD_MODE`, `BAD_FLAG`, `CALLS`, `DUPLICATE`, `BAD_RECORDS`, `BAD_SCHEMA`, `BAD_ROUTE`, `BAD_MEDIA`, `BAD_SOURCE`, `BAD_DIGEST`, `BAD_CAP`, `BAD_CALLS`. Path checks the jail already owns (`RELATIVE_PATH`, `DOTDOT`, `OUTSIDE_GRANT`, `FILE_URL`, `ENCODED_DOTDOT`, `UNC`, `DRIVE_ROOT`, `DRIVE_RELATIVE`, `ALT_STREAM`, `TRAILING_DOT`) pass through unchanged.

CCr would land the descriptor beside the spend gate. A vision rail accepts only a `VisionRequest`, reserves `cents` on `cosmos_spend` before any provider call, and re-hashes the caller-held bytes against `image_id`. URL fetch, clipboard capture, SVG rasterizing, and downscale stay outside this package. One confirming retry for one named provider timeout stays on that rail.

## Ship

- operations: `BYTE_CAP`, `CALL_CAP`, `COUNT_CAP`, `CRED_CAP`, `EMBED_CAP`, `LocalImage`, `MAX_CENTS`, `PATH_CAP`, `PROMPT_CAP`, `SCHEMA`, `VisionBatch`, `VisionRequest`, `assemble`, `choose_route`, `from_bytes`, `from_path`, `from_url`, `rebuild`, `request`
- refusal codes: `NOT_BYTES`, `EMPTY`, `OVERSIZE`, `UNSUPPORTED_FORMAT`, `BAD_JAIL`, `BAD_PATH`, `NOT_FILE`, `UNREADABLE`, `NO_FETCH`, `NOT_TEXT`, `NULL_BYTE`, `SECRET`, `NO_CRED`, `BAD_CRED`, `UNPRICED`, `BAD_PRICES`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_IMAGE`, `BAD_MODE`, `BAD_FLAG`, `CALLS`, `DUPLICATE`, `BAD_RECORDS`, `BAD_SCHEMA`, `BAD_ROUTE`, `BAD_MEDIA`, `BAD_SOURCE`, `BAD_DIGEST`, `BAD_CAP`, `BAD_CALLS`, plus jail codes that pass through
- what this module still refuses to execute: a model call, a socket, a URL fetch, a clipboard read, SVG rasterizing, image downscale, a spend reservation, and any file write
- hot-path shape: one pass, skip images that do not fit the remaining byte budget or the call cap
