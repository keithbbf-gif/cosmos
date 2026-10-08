# domdefer

## What this slice read

This slice read the `domdefer` slot in `V:\streams\federation\CONTRACT.md`, the day-one paragraphs in `V:\streams\federation\README.md`, and the DOM-first paragraphs in `V:\A\Ai\COSMOS\README.md` (Scope, and the design requirement "DOM first, API second"). It also read the DOM `AUTH_REQUIRED` note in `V:\A\Ai\COSMOS\docs\AGENT_BRIEF.md`. A search of the live `cosmos` Python tree found no `NEED_KEY`, `ask_scrape`, or `NO_PROFILE` chooser.

## What is already true

Browser-DOM agents are the preferred path in the live README. They are the default because the DOM depends on nothing that can run out: no credit, no quota, no billing state, and no key expiry. Reasoning-heavy and bulk work is specified to go over the DOM. Short, structured, scriptable work is what the API is for. A DOM auth wall is a person's own click on a Chrome profile they already have. It is not an installer action. A clean machine has no vendor session, so federation day one is the key the person pastes. The installer does not collect a password, scrape a browser profile, or automate a vendor login. `cosmos.py install` does not mint `api_token.txt` and does not open a chat window.

## What this proposal adds

`choose` is the two-minute function. A scrape request raises `Refuse("SCRAPE")` before any other choice, including when a key id is also present. A key id returns `via="api"` and `phase="DAY_ONE"` and ignores the browser-profile flag. No key id returns `via="none"` and `phase="NEED_KEY"`, even when the profile flag is true. `choose` never returns `via="dom"`. `later` is a separate function and is not on the two-minute path. `later(True)` returns `via="dom"` and `phase="LATER"`. `later(False)` raises `Refuse("NO_PROFILE")`. Neither function launches a browser, reads a profile directory, or logs in. The profile flag is an assertion the caller already has, not a path this module opens.

## Refusal codes

- `SCRAPE` — the caller asked the installer to capture a vendor session. That session is a credential the installer does not own.
- `NO_PROFILE` — `later` was asked to name DOM when no profile is asserted.

## How CCr would land it

CCr would call `choose` from the day-one installer before any browser step and before any network step. `DAY_ONE` continues with the credential id the secrets slot already stored. `NEED_KEY` is the typed stop when the person has not pasted a key. `later` stays off the two-minute clock. CCr would attach it only to a later control that runs after the person already has a vendor session of their own. Existing DOM workers stay in the live tree. This slice does not replace them and does not start them.

No extra files.
