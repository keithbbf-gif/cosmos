# cDeck P7 — GEM opens Gemini in the Chrome side panel on Profile 2

**Work order:** `work_orders/drop/wo-20260904T125500.json` (absent from this repo — see §0)
**Issue:** [#35](https://github.com/keithbbf-gif/cosmos/issues/35) · **Spec:** `builds/cdeck/ORCH_HOME_SPEC.md` P7 (absent from this repo — see §0)
**Lane:** Cursor Cloud Agent, Claude Opus 5, independent clone of `main`. Not Composer 2.5, not Auto.
**Status:** `PROPOSE_ONLY`. Nothing here is applied.

**P10 held.** No live-tree write. Nothing under `V:\Ai`. `tree_id` not touched. Core `:8770` not started, stopped, or restarted. No `schtasks` created, changed, or deleted. No CVM/Voice MOTIF opened. Voice refine is TABLED and is not touched. PR #30 and PR #32 are not merged, not rebased, not commented on. **Do not merge this PR either** — it is a proposal for CCr to apply.

---

## 0. Evidence ledger — read this before you weigh anything below

Four of the six files the work order names as context **do not exist in this repository** — not on `main`, not on any of the 60+ remote branches, not anywhere in commit history:

| Named context | State here |
|---|---|
| `docs/AGENT_BRIEF.md` | **ABSENT** — 0 commits touch this path, all-branch history |
| `docs/AGENT_BOUNDARIES.md` | **ABSENT** — 0 commits touch this path, all-branch history |
| `builds/cdeck/ORCH_HOME_SPEC.md` (the P7 spec) | **ABSENT** — 0 commits |
| `builds/cdeck/ui/{index.html,app.css,app.js}` | **ABSENT** — 0 commits |
| `work_orders/drop/wo-20260904T125500.json` | **ABSENT** — 0 commits |
| `docs/WORK_ORDER_SOP.md`, `docs/VERDICT_SPEC.md` | **PRESENT** — read, and honoured |

Reproduce:

```bash
for f in docs/AGENT_BRIEF.md docs/AGENT_BOUNDARIES.md builds/cdeck/ORCH_HOME_SPEC.md \
         builds/cdeck/ui/app.js work_orders/drop/wo-20260904T125500.json; do
  printf '%-46s %s\n' "$f" "$(git log --all --oneline -- "$f" | wc -l) commits"
done
```

I complied with "FIRST read `docs/AGENT_BRIEF.md` and `docs/AGENT_BOUNDARIES.md`" to the extent the instruction is satisfiable from a GitHub clone: I attempted both paths, on `HEAD` and after `git fetch origin main`, and they are not there. They are desktop canon (`docs/WORK_ORDER_SOP.md` §Pointers lists them as such) and this clone cannot see the desktop. **I did not guess their contents.** Where a boundary was needed I used the boundaries that *are* in the tree — `docs/AGENTS.md` ("Write the live tree from a proposal" is a *Do not*; "Invent absolute paths" is a *Do not*), `docs/WORK_ORDER_SOP.md` §Do not, and the P10 line in the issue itself.

Likewise **I have not read one line of the cDeck UI.** There is no `builds/` directory in this repository. So I cannot tell you which function `btnGem` calls, whether `cdeck-shell-v11` already has a GEM affordance, or what P7 says verbatim. What follows is a proposal about a *mechanism*, tied to the parts of the tree I could actually read.

Every claim is tagged:

- **[CODE]** — read from source in this repository, path and line given.
- **[CHROME]** — read from Chromium source, Chrome Enterprise policy templates, the DevTools Protocol definition, or Google's own published Chrome documentation. Cited inline.
- **[MEASURED]** — I ran a command in this session and am quoting its output.
- **[WO]** — asserted by the work order / issue #35, taken on trust, not verified here.
- **[ASSUMED]** — my inference. Every one of these carries the command that settles it.

### Finding 0 — the headline, which is not the mechanism

The work order asks for four things that cannot all be true at once. Three of them are fine. The fourth — **"on Profile 2"** — is the one that does not hold, and it does not hold for a structural reason, not a bug:

> **The Alt+G hotkey is a browser-global setting. Gemini entitlement is a per-profile setting. A browser-global control cannot make a per-profile guarantee.**

`glic.launcher_enabled` and `glic.launcher_hotkey` are registered in `RegisterLocalStatePrefs` — they live in `User Data\Local State`, one per Chrome installation. `glic.completed_fre` is registered in `RegisterProfilePrefs` — it lives in `User Data\Profile 2\Preferences`, one per profile. **[CHROME]** ([`chrome/browser/glic/glic_pref_names.cc`](https://chromium.googlesource.com/chromium/src/+/main/chrome/browser/glic/glic_pref_names.cc)) There is exactly one Alt+G for the whole install, and pressing it does not carry a profile argument.

That is not fatal, and §4 gives the fix, which is cheap: **make Profile 2 the only glic-entitled profile on the install, and then verify it.** Uniqueness is a measurement cDeck can take in a few file reads. Once it holds, the browser-global hotkey is unambiguous *by construction* — not by hope. When it does not hold, GEM refuses with `PROFILE_AMBIGUOUS` and says which other profile to fix.

Two smaller findings that change the shape of P7 and are easy to get wrong:

1. **Alt+G is already Chrome's.** It is not a shortcut cDeck should register — it is the one shortcut cDeck must *never* register (§3).
2. **The command is a toggle, not an open** (`Command::kPanelToggle`, `prevent_close = false`). **[CHROME]** Pressing it while the panel is open **closes** it, and cDeck has no channel to read panel state. A GEM button with open-only semantics is a lie (§3.2).

---

## 1. What "Gemini in the Chrome side panel" actually is

Internal codename **glic**. It is a feature *of the Chrome browser*, built into the browser binary — not a web page, not an extension, not an API. **[CHROME]** Google states the distinction explicitly, which is worth quoting because it is exactly the distinction the work order is drawing:

> "Gemini in Chrome is part of the Chrome browser on desktop, and is different from visiting Gemini in any browser at gemini.google.com or starting a chat with the Gemini web app by typing @gemini in the address bar in Chrome."
> — [gemini.google/overview/gemini-in-chrome](https://gemini.google/overview/gemini-in-chrome/) **[CHROME]**

So **"Not `gemini.google.com/app`" is not a preference — it is a different product.** The web app cannot see page content or drive Live mode; glic can. Any implementation that quietly substitutes the web app has not delivered P7, it has delivered a different feature with the same logo. This is `cosmos_dom`'s ratified decision 6 — "never a silent fallback to API" **[CODE]** `cosmos/cosmos_dom.py:4-5` — in a new costume, and it gets the same answer: refuse loudly.

It renders in a side panel as of the Gemini 3 Chrome update **[CHROME]** ([blog.google](https://blog.google/products-and-platforms/products/chrome/gemini-3-auto-browse/): "We're launching a new side panel experience"), which matches P7's wording. Command id `IDC_OPEN_GLIC` = 40294. **[CHROME]** ([`chrome/app/chrome_command_ids.h`](https://chromium.googlesource.com/chromium/src/+/master/chrome/app/chrome_command_ids.h))

### 1.1 Every invocation surface, and its verdict

| # | Surface | Verdict | Why |
|---|---|---|---|
| A | Native accelerator **Alt+G** (Windows) | **RECOMMENDED** | The only surface that both exists and reaches the real signed-in profile. §3 |
| B | Windows UI Automation `Invoke` on the Gemini toolbar button | **ESCALATION** | Strictly more precise than A — per-window, so per-profile. Costs a COM dependency. §4.3 |
| C | CDP `Browser.executeBrowserCommand{commandId:"openGlic"}` | **REFUSED — structurally impossible** | §2. This is the interesting one. |
| D | Chrome extension `chrome.sidePanel` | **REFUSED** | A side panel hosts an *extension* page. It cannot host Google's glic, and no extension API invokes `IDC_OPEN_GLIC`. Embedding `gemini.google.com` inside it is blocked by §7.1. |
| E | `iframe` of `gemini.google.com` | **REFUSED — blocked by Google** | Not policy. Physics. §7.1 |
| F | `window.open('https://gemini.google.com/app')` | **REFUSED by [WO]**, and wrong anyway | Different product (§1). Also the deck's own "do not window.open the web app". |
| G | Vertex AI / `bts_gem` / any API rail | **OUT OF SCOPE by [WO]** | An API answer is not a side panel. Explicitly excluded. |
| H | C1 ConPTY | **DEFERRED by [WO]** ("later") | No ConPTY anywhere in this tree: `git grep -ci ConPTY` → 0 files. **[MEASURED]** |
| I | Command-line switch | **DOES NOT EXIST** | No Chrome switch opens glic. `--glic-always-open-fre` forces the *onboarding* dialog **[CHROME]**, which is the opposite of what you want — it re-prompts consent. |

---

## 2. Why the clean path is closed: CDP `openGlic` and a signed-in profile are mutually exclusive

This deserves its own section because it is the path a competent engineer will find first, it looks perfect, and it is dead — for a reason that is documented on both ends.

**The DevTools Protocol has exactly the command we want.** `Browser.executeBrowserCommand` accepts `commandId`, and the allowed values are `openTabSearch`, `closeTabSearch`, **`openGlic`**. **[CHROME]** ([DevTools Protocol, Browser domain](https://chromedevtools.github.io/devtools-protocol/tot/Browser/)) No keystroke synthesis, no focus races, deterministic, and scoped to the browser you connected to.

**It cannot be used here.** From Chrome 136, `--remote-debugging-port` and `--remote-debugging-pipe` **are ignored** when they target the default Chrome data directory. They must be paired with a `--user-data-dir` pointing somewhere non-standard. **[CHROME]** ([Chrome for Developers: *Changes to remote debugging switches to improve security*](https://developer.chrome.com/blog/remote-debugging-port))

> "These switches will no longer be respected if attempting to debug the default Chrome data directory. These switches must now be accompanied by the `--user-data-dir` switch to point to a non-standard directory."

And a non-standard user-data-dir is a **fresh profile that is not signed in**. Which runs straight into glic's own precondition:

> "This feature isn't available in Incognito mode or for Chrome profiles that are not signed-in."
> — [Use Gemini in Chrome](https://support.google.com/chrome/answer/16283624) **[CHROME]**

So:

```
CDP debugging surface  ⟹  non-default user-data-dir  ⟹  profile not signed in  ⟹  glic unavailable
Keith BBF Profile 2    ⟹  default user-data-dir      ⟹  no CDP surface
```

**You can have the automation surface or the Gemini entitlement. Never both.** This is not a Chrome bug to wait out — it is the *intended* effect of a deliberate anti-cookie-theft change, and Google's stated position is that automation should use Chrome for Testing instead, which is precisely a profile that is not Keith's.

Two corollaries worth writing down:

- **Do not "solve" this by attaching a debugging port to Keith's real profile.** Even where a build still permits it, the port has no authentication — anything that can reach it gets full read of every cookie and live session in that profile. There is no version of that which is acceptable on the profile that holds Keith's Google identity.
- **This also kills the tempting hybrid** — "CDP for everything else, keystroke only for glic." Any CDP attach that reaches Profile 2 has the same problem. Rejecting C also means rejecting a CDP-based preflight against Profile 2; §5's preflight is therefore **all file and registry reads**, no browser attach.

`cosmos_browser.ChromeDriver` already lives on the correct side of this line and should stay there: every invocation passes `--user-data-dir={self._profile_dir}` with an attempt-private ephemeral directory **[CODE]** `cosmos/cosmos_browser.py:155,193`, and its docstring already says interactive automation is "a later CDP upgrade" **[CODE]** `cosmos/cosmos_browser.py:13-15`. **That upgrade must not be routed through Profile 2.** GEM is not a `DomWorker` job and must not be built as one — `DomWorker.run_attempt` creates a fresh profile per attempt by contract **[CODE]** `cosmos/cosmos_dom.py:52-60`, which is the exact thing that makes glic unavailable.

---

## 3. Alt+G is Chrome's shortcut, not cDeck's

**Alt+G is the published Windows accelerator for "open or close Gemini in Chrome."** **[CHROME]** ([Customize your Gemini in Chrome experience](https://support.google.com/chrome/answer/16988996)) Keith's Alt+G in the work order is not an arbitrary binding to invent — it is the binding that already exists. The neighbours matter too:

| Windows | Action **[CHROME]** |
|---|---|
| **Alt+G** | Open **or close** Gemini in Chrome |
| Alt+Shift+G | Switch focus between the tab and Gemini |
| Ctrl+Alt+G | Start selection mode |

### 3.1 cDeck must never call `RegisterHotKey` for Alt+G

This is the trap. "GEM … (Alt+G)" reads like an instruction to bind a hotkey. **Do the opposite.**

With the launcher enabled, the hotkey is registered by Chrome's own `GlicBackgroundModeManager` as a **global** hotkey (`kGlicHotkeyLocalScope` disabled is the default; enabling it scopes the hotkey to Chrome-focused and routes it through `InstanceIndependentHotkeyManager` instead). **[CHROME]** ([Chromium CL: *Add local scope flag for Glic launcher hotkey*](https://chromium.googlesource.com/chromium/src/+/0083718bad37ae19c1ef45965827651c10808187))

Win32 `RegisterHotKey` is exclusive. So if cDeck registers Alt+G, exactly one of two things happens, and both are bad:

- cDeck loses — `RegisterHotKey` fails with `ERROR_HOTKEY_ALREADY_REGISTERED` (1409). Silent no-op if unchecked.
- **cDeck wins** — it registers first and *steals Alt+G from Chrome*. Keith's working native shortcut stops working, replaced by cDeck's handler which then has to synthesize the very keystroke it just intercepted. This is a self-inflicted loop and it will look like "Gemini broke."

**GEM sends the accelerator. It does not own it.**

### 3.2 The accelerator must be read, not hardcoded

The shortcut is user-remappable — Google documents the remap flow, and the current value is stored in `Local State` under `glic.launcher_hotkey` as an accelerator string. **[CHROME]** (`glic_pref_names.cc`, `RegisterLocalStatePrefs`) Hardcoding `Alt+G` is a latent bug that fires the day Keith remaps it, and it fires *silently* — cDeck would send Alt+G into whatever now owns it.

**Read `glic.launcher_hotkey` and send what it says.** If it does not parse, or does not match what GEM is about to synthesize, refuse `HOTKEY_MISMATCH` and print both values. A dispatcher that sends a keystroke it cannot justify is guessing.

### 3.3 GEM is a toggle, and must be labelled one

`Command::kOpenGlic` was **renamed** `Command::kPanelToggle`, with `prevent_close = false`. **[CHROME]** (same CL) Google's own doc says "open **or close**." So:

- Press GEM once → panel opens. Press GEM again → **panel closes.**
- cDeck cannot read panel state. There is no API, no CDP (§2), no file.

There is no honest way to build open-only semantics on a toggle you cannot observe. Do not fake it — do not, for instance, send Alt+G twice to "make sure," which is a reliable way to guarantee it is closed. Two acceptable resolutions:

1. **Label it.** GEM is `GEM ⇄` — a toggle. Deck copy says so. Cheapest, honest, matches the platform.
2. **Escalate to Option B** (§4.3). A UIA `Invoke` on the toolbar button is still a toggle at the Chrome level, so this does not fix toggling either — it fixes *profile targeting*. **State observability is not recoverable by any surface available to us.** Say so rather than engineering around it.

The dispatch result is therefore `TOGGLE_NOT_OBSERVABLE` — see §6, and note it is the *success* path.

---

## 4. The Profile 2 gap, and the cheap way to close it

### 4.1 "Profile 2" is a directory name, and it is not the display name

`Profile 2` is a **directory** under `%LOCALAPPDATA%\Google\Chrome\User Data\`. "Keith BBF" is a **display name**, stored in `Local State` under `profile.info_cache["Profile 2"].name`. The mapping is arbitrary and reorderable — `Profile 2` is not "the second profile," it is whatever directory got that name when it was created, and display names can be edited freely.

**Resolve, never assume.** `docs/AGENTS.md` already forbids the shortcut: *"Do not … invent absolute paths."* **[CODE]** GEM must read `Local State`, find the entry whose `name` is the configured display name, and use *its* key as the profile directory. If the directory `Profile 2` and the display name "Keith BBF" disagree, that is `PROFILE_UNRESOLVED` and a refusal — not a coin flip on Keith's identity. Signed-in is decided by that entry carrying a non-empty `gaia_id` / `user_name`, which is the same read.

### 4.2 The uniqueness gate — the actual recommendation

From Finding 0: the hotkey is browser-global, the entitlement is per-profile, and focusing a Profile 2 window first does **not** repair this while the hotkey is global, because `GlicBackgroundModeManager` handles it ahead of the focused window. Focus-then-send only becomes profile-deterministic if `kGlicHotkeyLocalScope` is enabled — a feature flag whose default is off and which cDeck does not control.

So do not try to steer the hotkey. **Remove the ambiguity instead:**

> Enumerate `glic.completed_fre` across every profile in `User Data`. If **exactly one** profile has it completed, and that profile is the resolved Profile 2, then the browser-global hotkey has only one profile it can open. Profile 2 is guaranteed by construction.

If two or more profiles are entitled → `PROFILE_AMBIGUOUS`. Refuse, and name the other profile so Keith can fix it. Do not dispatch and hope; a 50% chance of opening Gemini on the wrong Google identity is worse than a refusal, because the refusal is visible and the wrong-profile open is not.

This converts an unguaranteeable requirement into a **checkable precondition**, which is the same move `cosmos_surfaces.qualify_backup_target` makes — decide from the last measurement and append a plain-language reason per failing question **[CODE]** `cosmos/cosmos_surfaces.py:140-193`. The `glic.completed_fre` type has already drifted once (a boolean in the January 2025 policy CL, an integer `FreStatus` enum in current `glic_pref_names.h` **[CHROME]**) so the reader must accept both `bool` and `int` and treat an unrecognised shape as *not entitled* — never as entitled.

### 4.3 Option B, and when to escalate to it

`IDC_OPEN_GLIC` is a command on a **browser window**, and a Chrome window belongs to exactly one profile. Invoking the Gemini toolbar button in a known Profile 2 window is therefore profile-deterministic with no uniqueness precondition and no dependence on the hotkey's scope flag.

Cost: Windows UI Automation, which means COM via `ctypes` against `UIAutomationCore`. That is real weight against the house's stdlib-only rule — `cosmos_browser`'s docstring rejects a websocket CDP client on exactly this ground ("the house rule is stdlib-only, and a full CDP client is a heavy dependency") **[CODE]** `cosmos/cosmos_browser.py:17-19`. It is also UI-fragile: it binds to a button's accessible name, which Google renames ("Ask Gemini" today).

**Recommendation: ship A behind the §4.2 uniqueness gate. Escalate to B only if the gate cannot be satisfied** — i.e. Keith genuinely needs two entitled profiles. Do not build B speculatively.

### 4.4 Getting a Profile 2 window to exist

Whichever option, the deck should not dispatch into a Chrome that has no Profile 2 window open. `chrome.exe --profile-directory="Profile 2"` uses Chrome's single-instance handoff: it does not start a second browser, it asks the running one to surface that profile. **[ASSUMED]** — whether it focuses an existing window or opens a new one is version-dependent and I could not test it from Linux. Settles with:

```powershell
# with Chrome already running, one Profile 2 window open:
& "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" --profile-directory="Profile 2"
# observe: new window, or focus of the existing one? count top-level Chrome windows before/after
```

Note the side effect honestly: if it opens a window, GEM has added a tab Keith did not ask for. Prefer an already-open Profile 2 window; treat the launch as the fallback, and if none can be had, refuse `NO_PROFILE_WINDOW`.

---

## 5. The preflight gate — measured, not assumed

Every gate below is a **read**. No browser attach (§2), no writes, no input synthesis until all of them pass. This is `cosmos_surfaces`' registry-reality pattern: a label is a claim, a probe is a measurement, and qualification is re-decided from the last measurement every time it is asked **[CODE]** `cosmos/cosmos_surfaces.py:8-11`.

| # | Gate | Source | Refusal when it fails |
|---|---|---|---|
| 1 | Enterprise policy allows Gemini | `HKLM\Software\Policies\Google\Chrome\GeminiSettings` ≠ 1; `GenAiDefaultSettings` ≠ 2; `GlicEnabled` ≠ 0 **[CHROME]** | `POLICY_BLOCKED` |
| 2 | Chrome binary found | `cosmos_browser.discover_browser()` **[CODE]** `cosmos_browser.py:61` | `UNREACHABLE` |
| 3 | Chrome version supports the side panel experience | `chrome.exe --version` | `VERSION_TOO_OLD` |
| 4 | Display name ↔ profile directory resolve to each other | `Local State` → `profile.info_cache` | `PROFILE_UNRESOLVED` |
| 5 | That profile is signed in | non-empty `gaia_id` / `user_name` in the same entry | `PROFILE_NOT_SIGNED_IN` |
| 6 | Gemini onboarding completed on it | `Profile 2\Preferences` → `glic.completed_fre` == completed **[CHROME]** | `FRE_INCOMPLETE` |
| 7 | **It is the only entitled profile** | `glic.completed_fre` across all profiles (§4.2) | `PROFILE_AMBIGUOUS` |
| 8 | Launcher/hotkey is on | `Local State` → `glic.launcher_enabled` **[CHROME]** — **registered default is `false`** | `LAUNCHER_DISABLED` |
| 9 | The accelerator is the one we will send | `Local State` → `glic.launcher_hotkey` (§3.2) | `HOTKEY_MISMATCH` |
| 10 | A Profile 2 window exists or can be surfaced | window enumeration, else §4.4 | `NO_PROFILE_WINDOW` |

Two notes on gate 6 and gate 8.

**Gate 6 is Keith's click, never automated.** Onboarding is a consent dialog. The tree already has the rule and the words for this — *"AUTH is Keith's click, never automated"* **[CODE]** `cosmos/cosmos_browser.py:174-175`, `cosmos/cosmos_dom.py:74-75`. GEM must not write `glic.completed_fre`, must not pass `--glic-always-open-fre`, and must not click through the dialog. It reports `FRE_INCOMPLETE` and names the menu path.

**Gate 8's default is `false`.** `RegisterLocalStatePrefs` registers `kGlicLauncherEnabled` as `false`, and it is auto-enabled on onboarding acceptance only when Chrome is the default browser or on the stable channel. **[CHROME]** (`glic_fre_controller.cc`) So *"Gemini works when I click the toolbar button"* and *"Alt+G works"* are **different facts**, and the second is the one GEM depends on. This is the single most likely reason a correct implementation appears to do nothing.

Region and language eligibility (US / `en-US`, gradual rollout) are real gates **[CHROME]** but are not locally readable, so they are not in the table. They surface as a dispatch that lands and produces no panel — which is exactly why the result type is `TOGGLE_NOT_OBSERVABLE` and not `OK`.

---

## 6. Typed refusal vocabulary

The work order says "typed refusal." The tree already has two precedents and they disagree slightly, so pick deliberately: `DomError` uses a fixed four-word vocabulary `{UNREACHABLE, SESSION_EXPIRED, AUTH_REQUIRED, BROKE}` **[CODE]** `cosmos/cosmos_dom.py:26-31`, while `SurfaceError` defines its **own** kinds for its own domain **[CODE]** `cosmos/cosmos_surfaces.py:44-54`. GEM is a new domain, so it follows `SurfaceError`: a `GlicError(kind, detail)` with kinds of its own, **reusing `UNREACHABLE` and `BROKE` verbatim** so the ledger vocabulary does not fork for concepts that already have words.

| kind | Meaning | Actionable fix carried in `detail` |
|---|---|---|
| `NOT_ADDRESSABLE` | Caller has no channel to browser UI (browser-served deck) | "Open cDeck in the desktop shell" |
| `POLICY_BLOCKED` | Gate 1 | Which policy, which value, `chrome://policy` to confirm |
| `PROFILE_UNRESOLVED` | Gate 4 | Directory and display name found, and that they disagree |
| `PROFILE_NOT_SIGNED_IN` | Gate 5 | Sign in to Profile 2 — Keith's click |
| `FRE_INCOMPLETE` | Gate 6 | The menu path to onboarding — Keith's click |
| `PROFILE_AMBIGUOUS` | Gate 7 | **Which other profile** is entitled |
| `LAUNCHER_DISABLED` | Gate 8 | Settings → AI innovations → Gemini in Chrome → system tray + shortcut |
| `HOTKEY_MISMATCH` | Gate 9 | Both accelerators, verbatim |
| `NO_PROFILE_WINDOW` | Gate 10 | No Profile 2 window to dispatch into |
| `VERSION_TOO_OLD` | Gate 3 | Version found, version needed |
| `UNREACHABLE` | No Chrome binary | reused from `DomError` |
| `BROKE` | Mid-dispatch failure, outcome unestablished | reused from `DomError`; report-never-retry |

**`TOGGLE_NOT_OBSERVABLE` is the success return, and it is not an error.** GEM dispatched an accelerator; it cannot prove a panel opened. The tree is unusually clear that this distinction matters — *"a screenshot is never proof of a paid action"* **[CODE]** `cosmos/cosmos_dom.py:9`, and evidence is "EVIDENCE, not proof of a remote commitment" **[CODE]** `cosmos/cosmos_dom.py:85-87`. A keystroke is weaker evidence than a screenshot. Returning `OK` here would be the green-log-over-nothing defect that `cosmos_surfaces` was written to stop.

Every refusal must satisfy `docs/VERDICT_SPEC.md` rule 1 — self-contained, naming the exact file/symbol and the fix, because Ara reads it aloud and Keith fixes it from the headphones with no desktop **[CODE]** `docs/VERDICT_SPEC.md:24`. `"doesn't work"` is an invalid refusal. That is why every row above carries a fix and not just a code.

---

## 7. The browser-served deck

### 7.1 "No iframe" is enforced by Google, not by us — and I measured it

I fetched `https://gemini.google.com/app` from this session **[MEASURED]**:

```
HTTP/2 200
x-frame-options: DENY
content-security-policy: report-uri /_/BardChatUi/cspreport;default-src 'none';script-src * ...
```

`X-Frame-Options: DENY` refuses framing from **any** origin, including same-origin. So the "No iframe" instruction is not a house preference that a future work order could relax — an iframe would be blocked by Google's server and render an error inside the deck. Worth recording precisely so nobody spends a cycle trying: **the constraint is upstream and permanent-until-Google-changes-it.**

### 7.2 Typed refusal, and a copy that is not a redirect

A page served from Core `:8770` runs in the renderer sandbox. It cannot synthesize OS keystrokes, read `Local State`, read the registry, enumerate windows, or invoke `IDC_OPEN_GLIC`. **Nothing in the browser-served path can open a Chrome side panel.** That is not a gap to close; it is the sandbox working.

So: `NOT_ADDRESSABLE`, rendered as a typed refusal, plus **copy query** to the clipboard. Explicitly **not** `window.open` — and not the disguised versions of it either: no `<a target="_blank">` to the web app, no `?q=` prefill URL, no meta-refresh. Per [WO], and per §1 it would be the wrong product regardless.

So that both deck modes render the *same* refusal, Core should own it: a read-only `GET /api/v1/gem/preflight` returning the §5 gate results as JSON, and the deck renders whatever it is handed. Desktop shell gets the same object plus a dispatch verb. **Read-only, additive, no Core restart in this PR** — this is a proposal, and Core `:8770` stays up untouched.

**Clipboard, precisely:** `navigator.clipboard.writeText` needs a secure context and transient activation. The tree serves the deck over HTTPS — `phone_url` is `https://{FQDN}:8770/` **[CODE]** `tests/test_up.py:95,137` — so the secure context holds, including with a self-signed cert (secure context is scheme-based). Two real caveats: the write must happen **inside** the click handler, not after an `await` on the preflight fetch, or the activation is gone; and if the deck is ever served over plain `http://` to a LAN IP the API is absent entirely, so keep a `document.execCommand('copy')` fallback on a hidden textarea. Do not report "copied" without checking the promise resolved.

---

## 8. Invariants — how each one is held

| Constraint [WO] | How this proposal holds it |
|---|---|
| `tree_id` stays `KMesh-COSMOS-live` | GEM never calls `cosmos_kernel.install()`. It constructs `Paths(root, expected_tree_id="KMesh-COSMOS-live")`, which **refuses** on mismatch **[CODE]** `cosmos/cosmos_paths.py:119-125`. Re-stamping a live root already refuses **[CODE]** `cosmos/cosmos_kernel.py:225-244`. Nothing here writes a sentinel. |
| Core `:8770` stays up | The only Core change proposed is one additive read-only GET. Not applied in this PR. No restart, no `serve()` change, no port change. |
| Do not write `V:\Ai` | No absolute path is written anywhere. Output is two files under `proposals/`. |
| No iframe | §7.1 — and Google enforces it anyway. **[MEASURED]** |
| Not `gemini.google.com/app` | §1 — different product. No `window.open`, no `target=_blank`, no prefill URL. |
| Not Vertex | No API rail is touched. `cosmos_rails`, `cosmos_spend`, `bts_gem` unmodified. An API answer is not a side panel. |
| Not C1 ConPTY | Deferred. Zero ConPTY references in tree. **[MEASURED]** |
| No CVM/Voice MOTIF | `cosmos_voice.py` not opened, not read, not changed. Voice refine TABLED. |
| PROPOSE only | Two files under `proposals/`. Zero lines changed in `cosmos/`, `tests/`, `docs/`, `work_orders/`. |
| Do not merge #30 / #32 | Not merged, not rebased, not commented. Branched from `main` at `14addfc`. |

---

## 9. File-level change list — proposed, not applied

Nothing below is in this PR. This is the shape for CCr.

**New, in the cDeck build tree (not in this repo):**

1. `builds/cdeck/gem_preflight.py` — the §5 gates. Pure reads: `Local State`, per-profile `Preferences`, registry policy, `chrome.exe --version`. Returns a `GlicError`-shaped object or a pass with every measured value attached. No writes, no input, no browser attach.
2. `builds/cdeck/gem_dispatch.py` — Option A only. Surfaces a Profile 2 window (§4.4), sends the accelerator **read** from `glic.launcher_hotkey` (§3.2) via `SendInput`. Returns `TOGGLE_NOT_OBSERVABLE`. No `RegisterHotKey` — §3.1.
3. `builds/cdeck/ui/` — GEM wired to preflight-then-dispatch; refusal panel rendering `kind` + `detail`; copy-query fallback. **Labelled a toggle** (§3.3).

**Modified:**

4. `cosmos/cosmos_service.py` — additive read-only `GET /api/v1/gem/preflight`. Must keep `POST` semantics and the existing 501-on-unattached pattern that `tests/test_rest_surface.py` pins; that suite passes today **[MEASURED]** and must still pass.
5. `builds/cdeck/ORCH_HOME_SPEC.md` — P7 amended with: Alt+G is Chrome's (§3.1), GEM is a toggle (§3.3), the uniqueness gate (§4.2), and the ten gates (§5).

**Explicitly not created:** no new daemon, no new CLOCKS row, no `schtasks` entry, no clipboard poller. A button is an event, not a clock. GEM runs on click and exits.

**Tests to write:** preflight gates 1/4/5/6/7/8/9 are pure functions over JSON and registry dicts — every one is unit-testable with fixtures and **no Chrome present**, which is the `FakeDriver` discipline the tree already uses to prove failure paths a real browser cannot be asked to produce on demand **[CODE]** `cosmos/cosmos_dom.py:9-11`. Include a fixture for `glic.completed_fre` as a bool *and* as an int (§4.2).

---

## 10. Not done, and why

- **Did not create `work_orders/drop/wo-20260904T125500.json`.** It is absent (§0). Writing it would mean inventing four of the six required fields — `Agent`, `Context source`, `Target & scope`, `Output` **[CODE]** `docs/WORK_ORDER_SOP.md:11-18` — and inventing WO fields is worse than a missing file. Keith or CCr should file it; the six fields it needs are in that SOP table, and per `docs/WORK_ORDER_SOP.md:42` `Agent` stays `xAI | Grok | grok-4.6` with `Route: CURSOR` in `Task`, because Cursor may not be the `Agent` field.
- **Did not write a `Verdict` object.** `docs/VERDICT_SPEC.md` assigns that to the executing lane writing back into the work-order JSON, and there is no work-order JSON here to write into.
- **Did not read the cDeck UI, so I have not named a single existing symbol in it.** No `btnGem`, no handler name, no line number. Anything I said about `app.js` would be fabricated. §9 is a shape, not a patch.

## 11. What would prove me wrong

Each of these is a single command, and each would change a specific section.

| Check | Command | Falsifies |
|---|---|---|
| glic entitlement is not unique to Profile 2 | `Get-ChildItem "$env:LOCALAPPDATA\Google\Chrome\User Data" -Directory \| % { "$($_.Name): " + (Get-Content "$($_.FullName)\Preferences" -Raw \| ConvertFrom-Json).glic.completed_fre }` | §4.2 — forces Option B |
| The launcher/hotkey is off | `(Get-Content "$env:LOCALAPPDATA\Google\Chrome\User Data\Local State" -Raw \| ConvertFrom-Json).glic \| Select launcher_enabled, launcher_hotkey` | Gate 8/9; explains "GEM does nothing" |
| Policy blocks Gemini | `reg query "HKLM\Software\Policies\Google\Chrome" /v GeminiSettings` and `chrome://policy` | Gate 1 — nothing else matters |
| The display name is not on `Profile 2` | `(Get-Content "…\Local State" -Raw \| ConvertFrom-Json).profile.info_cache \| ConvertTo-Json -Depth 3` | §4.1 |
| CDP is somehow reachable on the real profile | attach to `http://127.0.0.1:<port>/json/version` with Profile 2 live | §2 — reopens Option C, and raises a security question that needs its own decision |
| `--profile-directory` focuses rather than opens | §4.4 | Removes the stray-window side effect |

Open questions I could not close from this clone: the verbatim text of P7; whether cDeck's desktop shell has a native host able to call `SendInput` at all (if it is pure WebView2 with no host bridge, **Option A is unavailable in both modes** and §7.2's refusal is the whole feature until a host exists — this is the single biggest unknown in this proposal); Chrome's installed version and channel on the box; and whether `kGlicHotkeyLocalScope` is enabled in that build.
