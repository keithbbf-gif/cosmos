# TTS

Hermes turns reply text into one speech request for a named provider. This proposal's allowlist is `edge`, `elevenlabs`, `openai`, `minimax`, `mistral`, `gemini`, `xai`, `neutts`, `kitten`, `piper`, and `command`. `deepinfra`, `nous`, and the Hermes config spelling `kittentts` are outside this allowlist. A request exists after `select`. The Hermes default id `edge` is one allowlisted id, and it becomes the active provider only when `select` names it. Cloud ids (`elevenlabs`, `openai`, `minimax`, `mistral`, `gemini`, `xai`) carry the caller credential id. `edge`, `neutts`, `kitten`, and `piper` are local descriptors. `command` is a descriptor id whose command line is empty. The policy text cap is 4000 characters. A caller `cap` or `max_text_length` above 4000 is discarded, and the request records 4000. A boolean cap is not an integer and does not change that cap. The stored script is `redact(text)`. Secret-shaped text is refused and is not stored. Speed is a multiplier in thousandths (1000 is 1.0). OpenAI accepts 0.25–4.0, MiniMax 0.5–2.0, xAI 0.7–1.5, and Kitten 0.5–2.0. Every other provider uses the 0.5–2.0 policy window. MiniMax region is `global` or `cn`, and the credential id is the one the caller passed for that region. The native format is opus for ElevenLabs, OpenAI, and Mistral; mp3 for Edge, MiniMax, xAI, and command; pcm for Gemini; wav for NeuTTS, Kitten, and Piper. A voice value is an identifier. A slash, a backslash, a colon, or `..` raises `BAD_VOICE`.

## Seam

`cosmos_voice.py` owns the spoken-reply text on the live voice rail. Audio synthesis is a new seam beside that module. This proposal returns a frozen `AudioRequest` and leaves playback, packaging, and model load to a later service.

## Operations

- `Tts.select(name, **fields)` binds one allowlisted provider id.
- `Tts.synthesize(text, **fields)` returns a frozen `AudioRequest`.
- The request carries the provider id, `redact(text)`, the credential id, the policy cap 4000, region, native format, local flag, voice id, `speed_milli`, and an empty `command`.

## Authority

The human chooses the provider and supplies a credential id. This module holds the id, writes no ledger, and keeps no raw key. A later voice service is the authority that would speak the descriptor.

## Refusal codes

- `NO_PROVIDER` — valid speech text before a successful `select`.
- `UNKNOWN_PROVIDER` — the name is outside the allowlist.
- `SECRET` — secret-shaped text, or any input field named `api_key`.
- `MISSING_CREDENTIAL` — a cloud provider without a credential id.
- `EMPTY` — blank speech text.
- `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE` — text bounds. The speech-cap detail is `4000`. These fire before the selection check.
- `BAD_CREDENTIAL` — the credential id is not a token, or a synthesize id differs from the selected id.
- `BAD_REGION` — MiniMax region is outside `global` and `cn`, or another provider is given a region.
- `BAD_VOICE` — the voice is not an identifier.
- `BAD_SPEED` — the speed is outside the provider window.
- `BAD_FORMAT` — a hand-built record names a different audio format.
- `BAD_LIMIT` — a hand-built record names a cap other than 4000.
- `BAD_FIELD` — a field value is outside the scalar, string, list, and mapping set, the local flag disagrees with the provider, or a command, URL, or path field is non-empty.
- `TOO_DEEP` — nesting deeper than 6.
- `TOO_WIDE` — a mapping or sequence longer than 64.

## Ship

- Operations: `SCHEMA`, `TEXT_CAP`, `PROVIDERS`, `AudioRequest`, `Tts`.
- Refusal codes: `NO_PROVIDER`, `UNKNOWN_PROVIDER`, `SECRET`, `MISSING_CREDENTIAL`, `EMPTY`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `BAD_CREDENTIAL`, `BAD_REGION`, `BAD_VOICE`, `BAD_SPEED`, `BAD_FORMAT`, `BAD_LIMIT`, `BAD_FIELD`, `TOO_DEEP`, `TOO_WIDE`.
- This module still refuses to synthesize audio, open a socket, spawn ffmpeg, load a model, read a persona file, or run a command line. `AudioRequest.command` is always empty.
- Hot-path shape: one profile-dict lookup and one redact pass over the script, then the record checks the scrubbed form. Credential ids compare once with `const_eq`. The first malformed field refuses, and later fields are not applied. A higher caller cap is ignored.

## Landing

CCr would hang this rail off the spoken line in `cosmos_voice.py`. After the human selects a provider and, for a cloud engine, a credential id, the voice path calls `synthesize` and hands the `AudioRequest` to a later player. Playback, ffmpeg, and any command runner stay outside this module until a separate approved step exists. The ledger stores the attempt, and the script stays on the request.
