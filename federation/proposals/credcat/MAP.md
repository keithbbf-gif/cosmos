# credcat — credential phases for a two-minute peer

## What I read

- `CONTRACT.md` slot `credcat`, plus the product laws that day-one doors are OpenRouter and xAI and that Anthropic is off the route.
- `README.md` for the 120-second install: the peer mints the bearer and the install key, pastes one model key, and does not receive this machine's `live/` tree.
- `V:\A\Ai\COSMOS\docs\CREDENTIALS_NEEDED.md` for filenames and Keith's measured states only. No file under `live\config` was opened, and no secret value was copied.
- Live rail filenames: `openrouter_api_key.txt` in `cosmos/cosmos_openrouter_rail.py`, `xai_api_key.txt` in `cosmos/cosmos_cred_kit.py`, `openai_api_key.txt` in `cosmos/cosmos_codex_rail.py`, `anthropic_api_key.txt` in `cosmos/cosmos_claude_rail.py`, `cursor_cosmos_key.txt` in `cosmos/cosmos_cursor_rail.py`, `firecrawl_api_key.txt` in `cosmos/cosmos_firecrawl_rail.py`, and `groq_api_key.txt` in `cosmos/cosmos_groq_rail.py`.
- Install writes `config/install_key.bin` and does not mint `api_token.txt`. Serve mints `config/api_token.txt` only for a loopback bind when the file is absent.

## What is already true

- The credentials manifest is a presence list for Keith's machine. SATISFIED means his file is there. It is not a reason to put that file on a peer.
- `api_token.txt` and `install_key.bin` are SATISFIED on his machine because install and serve already ran there. A new peer mints new files. The catalog does not point at his copies.
- `cursor_cosmos_key.txt` is SATISFIED on his machine and is a later agent lane for a stranger.
- `groq_api_key.txt` is SATISFIED on his machine. Groq is not a day-one door and it is not one of the later asks, so the catalog does not name that file and does not ship it.
- OpenWork Google and Vertex are occupant settings, not `config/` filenames, so they are not catalog rows.
- `openai_api_key.txt` is the Codex CLI key and is blocked on his machine. A stranger does not need Codex to open chat.
- `r2_credentials.json` is the offsite backup target. Backup is outside the two-minute clock.
- `firecrawl_api_key.txt` is optional. The rail already answers with no key.
- `kill_token.txt` is optional. While it is absent, the bearer alone gates the off-switch.
- Tailscale is an interactive login. The manifest gives it no filename.
- Anthropic is off the route. The manifest lists `anthropic_api_key.txt` as degraded, and the installer does not create it.
- The manifest generator does not read, list, or touch the plaintext store under `D:\R2Cloner`.

## What this proposal adds

`catalog()` returns a frozen tuple of `Cred` rows. Each row has `name`, `phase` (`DAY_ONE`, `LATER`, or `REFUSED`), `filename` or `None`, and one sentence in `why`. The tuple holds no key bytes.

DAY_ONE filenames are `api_token.txt`, `install_key.bin`, `openrouter_api_key.txt`, and `xai_api_key.txt`. The installer mints the first two on the peer. The peer pastes one model key. OpenRouter is the chosen model-key filename. xAI is the second day-one door, so its filename is listed too. The wizard still accepts only one of those two doors.

LATER filenames are `r2_credentials.json`, Tailscale with no file, `cursor_cosmos_key.txt`, `openai_api_key.txt`, `firecrawl_api_key.txt`, and `kill_token.txt`.

REFUSED rows are `anthropic_api_key.txt` and `r2cloner` with no filename, which covers any path under `D:\R2Cloner`.

`SCHEMA` is `cosmos-federation-credcat/1`.

## Refusal codes

- `BOUND` — a name, phase, filename, or why is empty, too long, or not text.
- `PHASE` — the phase is not `DAY_ONE`, `LATER`, or `REFUSED`.
- `FILE` — a `DAY_ONE` row omitted its filename.
- `PATH` — a filename is a path, a drive, or a dotfile instead of a config basename.
- `SECRET` — a why or a filename is key-shaped, including the vendor `sk-` prefix.
- `WHY` — why is not a single sentence.
- `DUP` — two rows share a name or a filename.

## How CCr lands it

CCr keeps this tuple as the ask list next to the wizard. The secrets writer mints `api_token.txt` and `install_key.bin` on the peer and shows the bearer once. The wizard asks for the chosen day-one door and stores a credential id, not the pasted bytes. LATER rows stay outside the 120-second clock. REFUSED rows are never created and never copied. When Core grows a credential screen, it reads these phases instead of the SATISFIED column. His live config directory and his ledger stay the authority for files that already exist on his machine.
