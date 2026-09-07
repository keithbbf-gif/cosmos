# DEFINE — ChatBot phone (OpenRouter named free picker) (MOTIF stage 1)

**Keith 2026-09-07.** Frozen prompt. Verbatim to every model. Do not paraphrase.
**Iterate:** Keith 2026-09-07 — *Follow the Freemium model.*

Keith, verbatim: *The ChatBot phone app version of this (runs on openrouter models -
low latency, free models) can be FREE FOREVER - NO USAGE LIMIT! And lead people
to install the Desktop version (chatbot). That can be a pentration point.
Replace Claude with FREE FOREVER - YOU PICK THE MODEL.*

Keith, verbatim: *Follow the Freemium model.*

Keith, verbatim: *You can include advesarial Ai over remote (terminal OR phone).*

## WHAT

A **phone ChatBot** is the consumer mouth of the same drop-box loop (P13):
typed chat on the phone → optional JSON work order on GitHub
`work_orders/drop/` → host OS daemon → named agent → Output + timestamps.

The mouth runs on **OpenRouter named `:free` models** (low latency). The
human **picks a named model**. Not `openrouter/free`. Not `openrouter/auto`.
Not a silent rotator (H3).

**Business model is Freemium** (not a trial, not crippleware, not a timed
teaser):

| Tier | What the human gets | Money |
|---|---|---|
| **Free forever** | Phone ChatBot. Named `:free` picker. Real chat. Pitch **FREE FOREVER — YOU PICK THE MODEL**. | $0 from us. Not a 7-day trial. Not a message cap we invent. |
| **Install (free)** | Desktop ChatBot download. Same free picker still works. This is the penetration / acquisition surface. | $0 to install. |
| **Premium** | Paid upgrade, mainly on Desktop (phone may show the same upgrade). Named **paid** models, desktop hands (files / grants / drop-box as a real operator path), later P06 local free weights on their box. | **Keith names the price.** This TUI does not mint a SKU, does not click billing, does not invent a dollar amount. |

The free tier must stay **usable forever**. Conversion is because they want
**more** (desktop hands, paid models, on-box weights) — not because we
gutted chat. Vendor `:free` RPM/RPD is a vendor fact, not our paywall.

**Pitch (on the phone, on the store card, on the funnel):**
**FREE FOREVER — YOU PICK THE MODEL.**

That pitch **replaces Claude** as the consumer chat seat: no Claude
subscription required to talk. Premium is optional, like every Freemium
product. It is not “pay us or the app dies.”

The phone is the **free** front door. Desktop is the **install** and the
natural Premium sit. Phone does not pretend it is the desktop.

**Adversarial AI over remote (terminal OR phone)** is included. The P05
occupancy engine (isolated proposers, different-family critics, one
disposer) may be seated from a **remote terminal** (TUI / SSH / drop) **or**
from the **phone** (ChatBot / Voice drop). Same inbox. Same peeking ban.
Same one pen. Not a second Core. Not a shared-transcript crew on the
phone. Free-tier single-model chat stays usable; adversarial N-seat is
the occupancy path through those mouths, not a replacement for FREE
FOREVER — YOU PICK THE MODEL.

Operator Voice (SGH + Grok Voice Think Fast 2.0) stays Keith's operator
mouth and stays TABLED. This DEFINE is the **consumer ChatBot**, not Voice
refine, not CVM.

## WHY

Claude is a paid / metered seat. Freemium puts a **real free forever**
phone ChatBot in front of the same COSMOS drop loop, then earns on
Desktop / Premium. People who like the chat install Desktop. People who
need hands or paid models upgrade. That is the wedge.

"this" in Keith's line is the ThinkFast / Chatbox drop-box loop already
DEFINE'd in `DEFINE_THINKFAST_DROP.md`. This file is the **phone ChatBot
embodiment + Freemium funnel**, not a second drop desk.

## HONEST SPLIT (do not green-wash)

**Product meaning of FREE FOREVER / NO USAGE LIMIT:**

- Free tier is Freemium-free: **no subscription, no trial clock, no
  invented message quota from us.**
- The picker is named `:free` OpenRouter ids ($0 / token).
- Premium is optional.

**Vendor fact (must stay visible in-app and in docs):**

- OpenRouter `:free` is **not** infinite. Official caps (encode, do not
  invent): **20 RPM**; **50 RPD** until **$10** lifetime credits, then
  **1000 RPD**. Provider 429s still happen. Failed calls can count.
- Do **not** claim "OpenRouter has no usage limit."
- Do **not** print NO USAGE LIMIT as a legal warranty of vendor capacity.
- Do **not** sell “unlimited `:free`” as Premium. Premium sells **our**
  extras (desktop hands, named paid models, later on-box weights).
- Surface the vendor cap in the picker (short, true). Pitch vs Claude
  stays **FREE FOREVER — YOU PICK THE MODEL**.

P06 (local free weights on-box) is a **Premium / later** path to *actual*
unlimited on the user's hardware. Phone `:free` is the cloud free tier,
not P06.

## ACCEPTANCE (live emit)

- This DEFINE file is the work-order Task text. Same bytes to every lane.
- In-app chrome shows **FREE FOREVER — YOU PICK THE MODEL**.
- Freemium is visible: Free / Install Desktop / Premium. Free is not
  labeled “trial.” Premium is not required to send a chat on a named
  `:free` model.
- Picker lists **named** OpenRouter `:free` ids on the free tier. User
  tap = that id on the request. `allow_fallbacks=false`. Runtime bind =
  `response.model` (must equal the pick, or the turn is REFUSED / shown
  as swapped).
- Rotator ids `openrouter/free`, `openrouter/auto`, `openrouter/free:free`
  are REFUSED.
- Initial named pins already wired on `openrouter-api`:
  `google/gemma-4-26b-a4b-it:free` (default, low-latency) and
  `google/gemma-4-31b-it:free`. BUILD may **add** more **named** `:free`
  ids (prefer low latency, family-diverse). BUILD may not add a rotator.
- Vendor cap is printed, not hidden (20 RPM / 50–1000 RPD). Do not wrap
  that cap as “upgrade to Premium for unlimited free models.”
- Funnel: one persistent control to **install Desktop ChatBot**. A
  second control may say **Premium** once Keith names the SKU. Until
  then Premium is **UNMEASURED** (no fake price, no fake checkout).
- COSMOS work from the phone still uses GitHub `work_orders/drop/`
  (six fields). Phone never mounts `live/`. CCr still disposes live-tree
  writes. Drop-box as a *consumer operator path* is Premium / Desktop,
  not a silent second writer on `live/`.
- Desktop binary is **named at BUILD**, not invented here. Candidates:
  OpenWork desktop (already a product) or a COSMOS desktop ChatBot.
  Keith names which. Do not iframe OpenWork Web. Do not charge OpenWork
  Web $50 as this funnel. Do not invent a ChatBot dollar price.
- `kdash/cosmos-voice.apk` stays a **draft seed**. Do not ship it as this
  product. Do not delete it.
- Adversarial over remote: a drop (phone **or** terminal) may name the
  occupancy engine (N isolated seats), not only one Agent. Runner creates
  isolated sessions (P02 peeking ban). CCr still disposes. Phone still
  never mounts `live/`. Terminal over remote is a mouth, not a second
  writer on the runtime root.

## OFF-LIMITS

Do not rebuild CVM. Do not open a new Voice MOTIF (Think Fast stays TABLED).
Do not make GitHub Actions the executor. Do not invent a second drop desk.
Do not use the OpenRouter rotator. Do not claim vendor infinite quota.
Do not turn Freemium into a trial or crippleware. Do not invent a price.
Do not click billing. Do not write `V:\Ai`. Do not file USPTO from this
TUI. Do not publish (whitepaper / X / LinkedIn / arXiv / store listing)
until Keith says. Do not auto-MOTIF Forge/Studio. Do not merge parked PRs
(cosmos #30 #32 #36 #37 #38; cDeck #6 #16). Do not pull `origin/main`
onto unique local history. Do not force-push. Not a 13th $65 provisional
— this is a P13 embodiment + Freemium funnel.

## THIS TEXT

Copy this file into every lane's prompt. GEM, GLM, Cursor, Grok — same bytes.
