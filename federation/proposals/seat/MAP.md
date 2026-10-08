# seat

This proposal binds one day-one door to a named model pin and builds the chat JSON a later sender would POST. It does not call a model, open a socket, or read a key file.

## What I read

I read `CONTRACT.md` (slot seat), `README.md`, and `cosmos_federation` (`bounds.py`, `errors.py`, `product.py`, `redact.py`). I read `cosmos/cosmos_openrouter_rail.py` for `DEFAULT_MODEL`, `DEFAULT_MAX_TOKENS`, `tag_preload`, `OpenRouterRail._headers`, and `OpenRouterRail._dispatch_body`. I read `cosmos/cosmos_cursor_rail.py` for `CURSOR_GROK`, `CURSOR_MODEL`, `pin_cursor_model`, and `CursorRail._create_body`. I confirmed there is no `cosmos_*xai*rail.py` and no `cosmos_*grok*rail.py`. `cosmos/cosmos_groq_rail.py` is GroqCloud, not the xAI door, so its default is not this pin. `cosmos/cosmos_grok_worker.py` is a bucket worker, not a chat body. I did not read `live/config`.

## What is already true

`OpenRouterRail._dispatch_body` posts `model`, `messages`, `max_tokens`, `stream`, and `provider`. A text-only payload becomes `messages: [{role, content}]`. `tag_preload` rewrites system and developer blocks only, so a user-only message stays that pair. `provider` is `{allow_fallbacks: false}` unless a named provider tag is added. `max_tokens` defaults to 1024. The bearer is `Authorization` inside `_headers`, not a JSON field. The module's single default pin is `google/gemma-4-26b-a4b-it:free`, and the module header prices that pin at $0. `pin_cursor_model` returns `grok-4.6` for a coding launch. `CursorRail._create_body` is a cloud-agent create (`prompt.text`, `repos`, `model.id`), not a chat completion, so this seat does not copy that object. Day-one doors stay `openrouter` and `xai`. Anthropic is off. `check_cap` allows 1 through 1_000_000 micro-dollars.

## What this proposal adds

`suggested_pin` returns `google/gemma-4-26b-a4b-it:free` for `openrouter` and `grok-4.6` for `xai`. The OpenRouter pin is that rail's single default, and it is the cheapest documented chat model there ($0). The xAI pin is the single Grok default in `cosmos_cursor_rail.py`. OpenRouter's catalog slug `x-ai/grok-4.6` is a pin on the other door, not the native xAI id. `bind` stores the folded door, a credential id, the pin, and the cap on a frozen slotted `Seat`. `user_turn` copies the pin and the cap and refuses text over 4000 characters. `request_body` returns the `_dispatch_body` object. `fake_reply` is the test double. Files in this directory: `MAP.md`, `seat.py`, `test_seat.py`.

## Refusal codes

`BOUND` is an empty pin, an empty credential id, a non-string, text or reply text outside 1..4000 characters, or a cost that is not a non-negative int. `ANTHROPIC_OFF` is an Anthropic door or a pin that contains `anthropic/` or `claude`. `DOOR` is any other unknown door. `SECRET` is a credential id, pin, user text, or reply text that matches `secret_shape`, because those strings would show up in `repr`. `CAP` is a seat cap outside day-one policy (`check_cap`). `OVER_CAP` is a reply cost strictly above that seat's cap. A cost equal to the cap is allowed, including a $0 reply. `SEAT` and `TURN` mean the caller passed the wrong object.

## How CCr lands it

The wizard calls `bind` with the account credential id, `suggested_pin` or a person-chosen pin, and the cap. The chat route calls `user_turn` and `request_body`. For the OpenRouter door, the existing rail posts that object and adds the bearer in `_headers`. For the xAI door, CCr adds a sender later. That sender keeps `model` and `messages`. It drops `provider` if the xAI endpoint rejects OpenRouter's fallback guard. `fake_reply` does not ship as the live call. A live cost uses the same above-cap refusal before the spend fold records it. Core's ledger stays the authority. If the fold and the chain disagree, the chain wins.
