# Therapy / SLP practice sites — structure, trust, intake

**Pass:** 2026-09-14. Public marketing pages only.

**Not done (on purpose):** no client portals, no FormDr/SimplePractice logins, no Google Form fills, no Calendly bookings, no `/register` submissions, no review of uploaded packets. PHI is not on these pages and we did not go looking for it. Testimonials quoted below are what the practices already published.

**Why these:** they are *practice* sites a family actually uses to decide “do I call.” Expressable is the scale contrast, not the peer. Hummingbird is the “consultation as a Shopify product” warning.

**GP shell job:** get a parent or adult from “I think we need help” to a **consult** without collecting a history on WordPress. Intake lives on a BAA’d tool. The marketing host never sees the packet.

---

## What a 9.5 practice site does in the first screen

1. **Who** — named SLP, credentials a stranger can check (CCC-SLP, state license, ASHA).
2. **For whom** — kids, adults, or both, in one sentence. Do not make a parent hunt.
3. **Where** — city / in-home / telehealth. If the book is closed, say so.
4. **Next step** — Schedule a consult. Phone in the header. Not “Learn more.”
5. **Not yet** — no 40-field history. No insurance card upload. No “create an account to continue.”

Everything else (modalities, FEES, bilingual, insurance panels) is the second scroll or a service page.

---

## Care to Speak — credentials before the ask

- Home: [https://caretospeakspeech.com/](https://caretospeakspeech.com/)
- Agency write-up of the same site: [https://tmncreative.com/care-to-speak-website-design](https://tmncreative.com/care-to-speak-website-design)

**Stack (public):** WordPress + Elementor + Calendly.

**Structure.** Nav is short: About / Meet Siobhain / Working with us / Services / FAQ / Contact. Home H1 is the whole practice: *“Adult and Pediatric Speech-Language Therapy.”* Then Support Starts Here → Meet your therapist (Siobhain McHale, M.S., CCC-SLP) → four **modes** (Telehealth / In-Home / School-Based / Group) → “Take the next step, schedule a consultation today.” One lifespan practice, two audiences, not two sites.

**Trust.** The agency case study is accurate to the live DOM: CCC-SLP, California licensure, and years of work are on the first screen *before* Calendly. The founder is named. A “Director of Company Culture” dog (Kiki) is a warmth beat after the credential — it does not replace it. FAQ and “Working with us” exist so the consult is not the first time someone hears how sessions work.

**Intake.** `#calendly` on the home CTA. Contact is a page. There is no public pediatric/adult packet on the marketing host. That is the right split: **book first, packet later, off-site.**

**Steal for GP.** H1 names both ages. Credential line above the button. Four delivery modes as cards, not a paragraph. Calendly (or Acuity / Jane / SimplePractice scheduler) embedded; WP form plugin is not the scheduler.

**Leave.** Elementor’s default system-font stack (the kit lists Albert Sans, Alegreya, Bodoni Moda, Bricolage… — a font cafeteria). Pick two. The dog is optional.

---

## Idaho Voice & Swallow Center — specialty, named procedures, schedule in the chrome

- Home: [https://idahovoiceswallowcenter.com/](https://idahovoiceswallowcenter.com/)
- Services: [https://idahovoiceswallowcenter.com/services/](https://idahovoiceswallowcenter.com/services/)
- Conditions: [https://idahovoiceswallowcenter.com/conditions-treated/](https://idahovoiceswallowcenter.com/conditions-treated/)
- Public schedule route (not opened as a session): `/register` from the header
- Privacy / NPP exist as first-class pages (`/privacy`, `/notice-of-privacy`) — linked from the live app map

**Stack (public):** custom (Gatsby). Type: **Inter** body, **Lexend** display. Phone `(208) 298-9949` is a nav item, not a footer leftover. Clinic: 875 S. Vanguard Way, Suite 200C, Meridian, ID.

**Structure.** Five public jobs: Home / Services / Conditions / Insurance / Schedule. Home H1 is *“There is HOPE !”* — loud, specialty-clinic energy. Immediately: “Now accepting referrals and non-referrals.” Then the **procedure cards** (Acoustic/Aerodynamic Voice Evaluations, Videostroboscopy, Skilled Intervention, FEES). Conditions are the words patients search (chronic cough, throat clearing, hoarseness, VCD/EILO, vocal fatigue). Services pages use a repeating **What is it? / Benefits:** pair so a referring ENT and a scared patient can both scan.

**Trust.** Named clinicians with training (UVA, ASHA CCC, Idaho license, FEES, stroboscopy, Speak Out, PhoRTE). “Meet your care providers” is a real block, not an About blob. Testimonials on the public home are first-name / initials only as *they* published them; we did not retrieve charts. Insurance is its own page — not a PDF buried under Contact.

**Intake.** Header CTA is **Schedule an appointment → `/register`** (repeated in the footer). That is a **scheduler**, not a history form, on a separate route. Notice of Privacy is a page. The marketing site does not host a 12-page case-history PDF.

**Steal for GP.** Phone + Schedule in the sticky header. Procedure names in the patient’s vocabulary. Conditions as a taxonomy. Insurance as a URL. NPP as a URL. “Accepting / not accepting” as a one-liner, not a blog post.

**Leave.** Exclamation-point H1 if the practice is pediatric generalist — hope-shouting fits voice/swallow more than “late talker.” Gatsby is irrelevant; GP Elements can do this header in an afternoon.

---

## Dynamic Speech & Language Therapy — consult first, then HIPAA packets

- Home: [https://dynamicsltherapy.com/](https://dynamicsltherapy.com/)
- Forms (public instructions only): [https://dynamicsltherapy.com/client-information/forms/](https://dynamicsltherapy.com/client-information/forms/)
- Free consult: [https://dynamicsltherapy.com/request-a-free-consultation/](https://dynamicsltherapy.com/request-a-free-consultation/)

**Stack (public):** WordPress, custom theme (`dynamic-speech-and-therapy-theme` 3.4.1), Stackable blocks, Google fonts **Source Sans Pro + Bodoni Moda + Dosis + Lato**. Reviews badge via Business Reviews Bundle (Google 5.0 / 11 reviews on the forms page). **FormDr** for packets.

**Structure.** This is a **multi-clinician, multi-city** practice (Woodland, Longview, Kelso, Vancouver, WA). Nav exposes the team with **training tags** (DTTC/ReST, PROMPT, Talk Tools, SPEAK OUT!, stuttering, aphasia) *in the menu*. That is unusual and useful — a parent looking for PROMPT does not open four bios. Home: H1 “Speech & Language Therapy,” age band “2 Years – Adult,” clinician photo/name, then **Get a Free Consultation Now!**, then service tiles (Cognition / Language / Social Communication / Speech). Geography is in the `<title>` and the meta, which is how local search actually works.

**Trust.** Credentials are in the menu and on the home (Christy Bisconer, M.S. CCC-SLP). Special trainings are named, not “evidence-based care.” The Google badge is on the forms page — social proof at the moment of commitment, which is when it helps.

**Intake (the one to copy).** Forms page, live 2026-09-14:

1. Owner welcome, signed **Mrs. Christy Bisconer MS CCC-SLP**.
2. Bold rule: *“Do not complete these forms until you have scheduled, and completed, a free consultation!”*
3. Two packets only: **Pediatric Intake Packet** / **Adult Intake Packet**.
4. After consult + forms: billing email in 3–4 business days with deductible / coinsurance / auth / copay / visit count.
5. Platform sentence: *“Dynamic Speech & Language uses FormDr which is a HIPAA compliant platform ensuring all patient data is encrypted in transit and at rest.”*
6. Save-and-continue-later is explained in human words.

**Steal for GP.** Consult → packet → money talk. Two packets, not one “new client form.” Name the HIPAA vendor on the public page. Do not host the fields on WP. Put “do not fill this yet” at the top — it prevents abandoned PHI sitting in a wrong inbox.

**Leave.** Training-stuffed mega-menu if there is one clinician (it will look like résumé stuffing). Four Google fonts. Duplicate H2s (the home currently repeats Cognition / Language / Social — a builder accident; do not ship that).

---

## Ms. Paula SLP — Client Center as a numbered path

- Home: [https://mspaulaslp.com/](https://mspaulaslp.com/)
- Client Center: [https://mspaulaslp.com/client-center/](https://mspaulaslp.com/client-center/)
- Contact: [https://mspaulaslp.com/contact-us/](https://mspaulaslp.com/contact-us/)
- Calendly (public scheduling URL, not booked): [https://calendly.com/mspaulaslp/consultation](https://calendly.com/mspaulaslp/consultation)

**Stack (public):** WordPress + Elementor. Sticky via Elementor (`#e-sticky-js`). Type: **Nunito + Open Sans**. Calendly. Bilingual (EN/ES) in the first fold.

**Structure.** Home H1: *“Unlocking Unlimited Potential, One Word at a Time.”* Softer than Care to Speak; the useful line is the next one — compassionate, individualized, diverse needs — plus a Spanish duplicate. **WE ACCEPT INSURANCE** is a heading, not a footnote. Offerings mega-menu is long (teletherapy, bilingual, pediatric, Spanish, language, social-pragmatic, feeding, cognitive, schools). A persistent banner: *only accepting new clients for teletherapy*. Client Portal is a separate heading from Client Center — portal = existing families; center = new.

**Trust.** Insurance called out. Bilingual is not a flag icon; it is a second headline. “For Schools” is its own offering. FAQ on the Client Center answers cost / medically necessary vs elective / session length — the three questions that otherwise become phone tag.

**Intake.** Client Center is a **numbered recipe**:

1. Schedule a free consultation (Calendly).
2. Complete appropriate forms (Pediatric / Adult / Insurance).
3. Schedule an evaluation.
4. Begin in-home or teletherapy.

That sequence is the GP page template. **Caveat:** the Adult Intake link on this pass resolved to a **Google Form** (`formrestricted`). Google Forms is not a BAA’d intake. Pediatric link on this pass pointed back at the home — a broken door. Copy the *numbering*, not the hosts.

**Steal for GP.** Four-step Client Center. Capacity banner in the header. Insurance as a heading. EN/ES if the practice is bilingual. FAQ that names money.

**Leave.** Google Forms for anything with a history, insurance ID, or school record. Elementor sticky plus a second “message-header” plus Trustindex widgets — the header is already busy. Nunito at every weight (the Google request pulls 100–900 italic).

---

## Hummingbird Speech Therapy — consultation as a product (warning)

- Home: [https://hummingbird-speechtherapy.com/](https://hummingbird-speechtherapy.com/)
- Founder: [https://hummingbird-speechtherapy.com/pages/meet-the-founder](https://hummingbird-speechtherapy.com/pages/meet-the-founder)
- Consultation SKU: [https://hummingbird-speechtherapy.com/products/consultation-services](https://hummingbird-speechtherapy.com/products/consultation-services)

**Stack (public):** Shopify. Type: Fahkwang + Klee One. Dawn sticky header. Request Consultation is `/products/consultation-services`. Login in the nav.

**Why it is in this pack:** it is a small bilingual (NY & CT) practice with a clean “in-home / school / virtual” sentence. The **failure** is architectural. A consult is not a variant. Shopify checkout + wallet chrome (the `<title>` even concatenates card brands) trains the family to type payment data on the same host they will later be asked for developmental history. Login on a marketing nav implies a portal the shop is not.

**Steal.** One sentence for place-of-service. Founder page with CCC-SLP + state list.

**Leave.** Shopify as the clinical front door. Consultation SKU. Login in the public nav unless there is a real portal.

---

## Expressable — scale contrast, not a peer

- Home: [https://www.expressable.com/](https://www.expressable.com/)
- Insurance estimate (public marketing CTA): [https://app.expressable.com/estimate](https://app.expressable.com/estimate)

National teletherapy. Next.js. Sticky promo: *“Check your insurance coverage — Get my estimate.”* FAQ schema, Joint Commission seal, “What we treat,” major-plan logos. Useful **pattern**: insurance estimate is a *tool*, not a paragraph. Useless as a visual target for a one- or two-SLP GP shell — it is a product company. Do not clone the mascot CTA. Do steal the habit of answering “does insurance cover this?” with a button.

Chicago Speech Therapy ([https://chicagospeechtherapy.com/](https://chicagospeechtherapy.com/)) returned **403** to this pass’s fetcher; not scored.

---

## Intake rules for the GP shell (non-negotiable)

| Step | Lives on | Never |
|---|---|---|
| Discover / trust | WP + GP | PHI fields |
| Free consult | Calendly / SimplePractice / Jane / Acuity | WP Contact Form 7 “tell us about the concern” textareas that invite diagnosis |
| Packets | FormDr / Jotform HIPAA / SimplePractice intake | Google Forms, Typeform free, Gravity Forms on the same WP install without a BAA |
| Billing talk | Staff email / portal after packets | Surprise “we’ll check benefits later” |
| Portal | Vendor host | A “Login” chip that 404s |

Public copy may say “HIPAA-compliant intake via {vendor}.” It may not ask for DOB, school, diagnosis, or subscriber ID on a GP page.

---

## Structure template (GP Elements)

1. **Sticky header:** logo · Services · How it works · Team · Insurance · Client Center · tel: · **Schedule**
2. **Hero:** `{age band} speech-language therapy in {place}` + credential line + one button
3. **Modes:** in-clinic / in-home / telehealth (only the ones that are true)
4. **How it works:** Consult → Packet → Eval → Therapy (Ms. Paula’s four, Dynamic’s “consult first” rule)
5. **Team:** name, CCC-SLP, license state, 3 trainings max, ASHA lookup link
6. **Client Center:** numbered, packets linked off-site, “do not fill until after consult”
7. **Footer:** NPP, privacy, accessibility, phone, no fake chat widget

---

## Do not

- Scrape, store, or restyle anyone’s patient packet.
- Put a chatbot on a therapy home that invites “describe your child’s delay.”
- Badge-wash (ten logos, no named human).
- Ship a “portal” that is a Google Drive folder.
