# Namecheap → Cloudflare — checklist + runbook

**Status:** STAGED OPS DOC. Not executed. No live cutover. No credentials in this file.
**Audience:** Keith (operator). Money, logins, EPP, and approvals stay with Keith.
**Scope:** registrar transfer of Keith’s ~dozen Namecheap domains onto Cloudflare Registrar,
plus the DNS full-setup Cloudflare requires *before* it will accept an auth code.
**Not in scope:** hosting moves, mailbox-provider moves, COSMOS Core, the live tree,
R2 keys, Tailscale, KDash, or any site rebuild.
**Inventory source (historical):** [Namecheap Domain List](https://ap.www.namecheap.com/domains/domainlist)
**Written:** 2026-09-14. Vendor pages cited below were read the same day.

---

## Read this first

Two different operations share the word “transfer.” Do not conflate them.

| Operation | What actually moves | Reversible? | When |
|---|---|---|---|
| **DNS cutover** | Authoritative nameservers → Cloudflare | Yes, until the registrar transfer finishes — *if* you still have a Namecheap zone snapshot | **Required first.** Cloudflare will not take an EPP/auth code while the zone is `Pending`. |
| **Registrar transfer** | Who you pay for the name (Namecheap → Cloudflare Registrar) | No cheap undo. After success, ICANN locks the name for **60 days**. | **Only after** the zone is `Active` on Cloudflare **and** HTTP + mail are proven. |

Cloudflare Registrar will not keep another company’s nameservers. Every name that
moves to Cloudflare Registrar must already be on a Cloudflare **full setup**
(Cloudflare-assigned NS). That is a vendor hard rule, not a preference.

The danger is the DNS step, not the EPP step. A wrong zone file takes mail and
sites down in minutes. A delayed registrar transfer only delays who sends the
renewal invoice.

**Order of operations (do not invert):**

1. Census + freeze (Wave 0) — no unlock, no NS change.
2. Snapshot every zone. Confirm eligibility.
3. Add the zone on Cloudflare. Rebuild the zone by hand. Grey-cloud first.
4. Disable DNSSEC at Namecheap. Wait out the DS TTL.
5. Point Namecheap Custom DNS at the two Cloudflare nameservers.
6. Prove `Active` + HTTP + MX **before** unlocking.
7. Unlock + request EPP **for that one name**, paste it only into Cloudflare, approve the FOA.
8. After the registry shows Cloudflare as registrar: verify email, optionally re-enable DNSSEC, leave Namecheap products that still serve mail/hosting alone.

**One name at a time on anything that serves a live site or real mail.** Parked names may ride together. Live sites do not.

---

## 0. What this is / is not

### This document is

- A staged checklist Keith can walk with the Namecheap Domain List open in one tab
  and Cloudflare in another.
- A fail-closed runbook: skip a gate → stop. A claim is not evidence.
- Operator procedure only. It does not change COSMOS Core, `live/`, or DNS.

### This document is not

- Permission to log in as anyone else, store passwords, or paste EPP codes into
  chat, git, the ledger, or this repo.
- A hosting migration. Namecheap Shared / cPanel / WordPress stays where it is
  unless Keith later opens a **separate** work order.
- An email-provider migration. Private Email, Google Workspace, Microsoft 365,
  and cPanel mail stay at their current vendors. Only the **DNS records that
  point at them** move.
- A reason to create a second Cloudflare account. R2 offsite already assumes
  Keith’s existing Cloudflare account (`docs/OFFSITE_READY.md`,
  `docs/CREDENTIALS_NEEDED.md`). Use that account. Do not open a parallel one.
- A batch “transfer all twelve now” button. Cloudflare will charge each name
  individually; the registry still processes each transfer on its own clock.

### COSMOS fence (do not cross from this job)

- Do not write the COSMOS live tree or `live/config/`.
- Do not touch Core `:8770`, KDash, or `cosmos up` / Tailscale MagicDNS.
- Do not put API tokens, R2 keys, or the Core bearer into Workers, Pages, or
  Transform Rules “while we are in the dashboard anyway.”
- Do not publish COSMOS. Registrar move ≠ public site.

Keith does money and credentials. This file never asks for a password.

---

## 1. Vendor facts that drive the procedure

Pinned to vendor pages, not folklore. If a dashboard disagrees with this file,
the dashboard + the cited page win; amend this file.

### Cloudflare (Registrar + DNS)

- You **cannot** enter an authorization code until the domain is **Active** on
  Cloudflare. Pending zone → no EPP field.
  Source: [Transfer your domain to Cloudflare](https://developers.cloudflare.com/registrar/get-started/transfer-domain-to-cloudflare/)
  (updated 2026-04-24) and
  [Troubleshoot failed domain transfers](https://developers.cloudflare.com/registrar/troubleshooting/).
- Cloudflare Registrar requires **full-setup** authoritative DNS. You cannot
  keep Namecheap BasicDNS / PremiumDNS / hosting NS after the registrar lands.
- DNSSEC at the *losing* registrar must be **off** before NS change. A leftover
  DS record makes the name unresolvable and can block `Active`.
- Most gTLD transfers (`.com` / `.net` / `.org`, …) add **one year** from the
  current expiration and charge at-cost. Some ccTLDs (example: `.uk`) add no
  year and charge no transfer fee.
- Do not transfer a name that already has ~9+ years remaining on a 10-year
  registry cap (`.co` cap is 5 years). The extra year can reject the transfer.
- If the name expired and was then renewed, wait **45 days after the original
  expiration** before transferring, or the registry may refuse the extra year.
- Renew first if the name is within **15 days** of expiration.
- Do **not** edit registrant name / org / email in the 60 days before transfer.
  ICANN treats that as Change of Registrant and can lock the name for 60 days.
- IDN / non-Latin labels (and `xn--` punycode) are not supported.
- TLD support is the live list at [cloudflare.com/tld-policies](https://www.cloudflare.com/tld-policies/)
  and [Supported TLDs](https://developers.cloudflare.com/registrar/top-level-domains/).
  If the TLD is missing, **stop**. Do not invent a workaround.
- `.uk` / `.co.uk` / `.org.uk` use an **IPS tag**, not an EPP code.
- After a successful transfer, ICANN may require registrant-email verification.
  Ignore it for 15 days and Cloudflare/the registry can **replace nameservers
  with parking NS**. That takes sites and mail down. Treat the verification
  mail as a P0.
- Cloudflare’s zone scan is **not** a complete zone transfer. MX, DKIM, SRV,
  CAA, and odd CNAMEs are the usual misses.
- Proxy (orange cloud) is **on by default** for A/AAAA/CNAME created in the
  dashboard. That is the #1 email/SaaS foot-gun. Grey-cloud first.

### Namecheap (losing registrar)

- Domain List (the census): <https://ap.www.namecheap.com/domains/domainlist>
- Unlock + Auth Code: **Manage → Sharing & Transfer → Transfer Out**.
  Source: [Transfer a domain from Namecheap](https://www.namecheap.com/support/knowledgebase/article.aspx/258/84/what-should-i-do-to-transfer-a-domain-from-namecheap/)
  (updated 2023-08-15) and
  [Release registrar lock](https://www.namecheap.com/support/knowledgebase/article.aspx/380/46/how-do-i-setrelease-registrar-lock-for-a-domain/).
- The Auth/EPP code is emailed to the **registrant** address, which is **not**
  always the Namecheap account email.
- Namecheap has five days to release after a valid gaining-registrar request
  (ICANN). Approving the FOA/email shortens that.
- Changing nameservers: **Manage → Nameservers** dropdown → **Custom DNS**.
  Source: [Change DNS for a domain](https://www.namecheap.com/support/knowledgebase/article.aspx/767/10/how-can-i-change-the-nameservers-for-my-domain/)
  (updated 2025-04-03).
- Switching **away** from BasicDNS / PremiumDNS / Web Hosting DNS does **not**
  copy host records onto the new nameservers. Save the zone *before* the
  dropdown changes.
- Switching **to** Namecheap Web Hosting DNS **overwrites** custom records with
  hosting defaults. Do not pick that dropdown during this job.
- Namecheap-native **URL Redirect** and **Email Forwarding** are BasicDNS
  features. They die when NS leave Namecheap unless you rebuild them on
  Cloudflare (Redirect Rules / Email Routing) **before** the cutover.
- Private Email mailboxes **do not move**. They keep working if and only if MX
  + SPF + DKIM (+ DMARC) are copied and left **DNS-only**.
- WHOIS privacy is a separate toggle from registrar lock. Leave privacy on
  unless a specific transfer is refused because of it. Do not disable privacy
  “just in case” across the whole list.
- ccTLD oddities (`.uk`, `.de`, `.fr`, `.es`, …) have their own clocks. If a
  name is not a generic TLD, read the TLD row on Cloudflare’s TLD policies
  page before Wave 1.

---

## 2. Wave 0 — census (do this before any unlock)

Open [Domain List](https://ap.www.namecheap.com/domains/domainlist). Export or
transcribe into an **operator-private** notes file (not this repo, not
`live/`, not chat). The table below is the schema. Fill it from the dashboard.
Do not invent names.

### Census columns

| Field | Where to read it | Why it gates the wave |
|---|---|---|
| Domain | Domain List | Identity |
| TLD | name | Cloudflare support check |
| Status | Domain List (Active / expired / redemption) | Expired → renew at Namecheap first. Redemption → cannot transfer out. |
| Expires | Domain List | <15 days → renew first. Post-expiry renewal <45 days → wait or accept no extra year. |
| Created / last transfer | WHOIS/RDAP or Domain List | <60 days since register or last registrar transfer → **BLOCKED** |
| Registrant email | Manage → Domain / WHOIS | Must be an inbox Keith can open today. EPP and FOA land here. |
| Privacy | Domain tab | Leave on unless a refusal names it. |
| Registrar lock | Sharing & Transfer | Must stay **locked** until Wave 3/4 for that name. |
| Nameservers | Domain tab | BasicDNS / PremiumDNS / Web Hosting DNS / Custom — drives snapshot path |
| DNSSEC | Advanced DNS | On → schedule a 24h+ disable before NS change |
| Mail | Advanced DNS → Mail Settings + MX | Classifies EMAIL vs none |
| Web | A/AAAA/CNAME/URL Redirect for `@` and `www` | Classifies LIVE / PARKED / REDIRECT |
| Hosting | Namecheap Hosting list / cPanel | Hosting stays. Copy A records; do not cancel. |
| Years remaining | Expires − today | ≥9 years on a 10-year TLD → wait |
| Wave | this file | PARK / MAIL / LIVE / BLOCKED |
| Snapshot path | operator notes | Proof the zone was copied before NS change |
| Done? | — | Empty until verification artifacts exist |

### Classify each name (exactly one class)

| Class | Meaning | Wave |
|---|---|---|
| **BLOCKED** | <60 days old or last transferred; TLD unsupported; IDN; redemption; `clientHold`/`serverHold`; registrant email dead; 9+ years remaining | Do not start. Write the reason in the census. |
| **PARK** | No mailbox, no production site. Parking page or unused. | Wave 1 (may batch) |
| **REDIRECT** | Namecheap URL Redirect / forwarding only | Wave 1 **after** Cloudflare Redirect Rules exist |
| **MAIL** | Real MX (Private Email, Google, M365, cPanel, forwarder) but no production site | Wave 2 — one-at-a-time if the mailbox is load-bearing |
| **LIVE** | Public site, shop, app, or anything Keith would notice if it 404’d | Wave 3 — **strictly one name at a time** |
| **HOST-BOUND** | Namecheap Web Hosting DNS (`dns1.namecheaphosting.com`) or cPanel mail on the same box | Treat as LIVE. Copy the **cPanel Zone Editor** export, not only Advanced DNS. |

If unsure, it is **LIVE**.

### Eligibility gate (every name, before Wave 1)

Tick all, or the name stays BLOCKED.

- [ ] TLD is on [Cloudflare TLD policies](https://www.cloudflare.com/tld-policies/).
- [ ] Not an IDN / `xn--` label.
- [ ] Status is Active (not expired, not redemption, not pending delete).
- [ ] Registered > 60 days ago **and** not transferred in the last 60 days.
- [ ] Registrant name / org / email **not** changed in the last 60 days. Do not “fix” WHOIS now.
- [ ] Expiration > 15 days away, or already renewed at Namecheap.
- [ ] Years remaining + 1 ≤ registry max (usually 10; `.co` = 5).
- [ ] Registrant inbox reachable today (send yourself a test).
- [ ] Cloudflare account email is verified; a payment method is on file (Keith).
- [ ] If transferring several paid names in one week: Keith has warned the card issuer. Cloudflare bills **each** transfer.

### Zone snapshot (every name, before any NS dropdown)

Namecheap does not follow the records to Custom DNS. Cloudflare’s scan misses
records. The snapshot is the only rollback.

From **Manage → Advanced DNS → Host Records** (and Mail Settings):

1. Screenshot the full Host Records table.
2. Transcribe every row: type, host, value, priority, TTL.
3. If nameservers are Web Hosting DNS: also export **cPanel → Zone Editor**.
4. Pull a live answer from the public DNS, not just the panel:

```text
# Windows (Keith's box)
nslookup -type=NS  example.com  1.1.1.1
nslookup -type=A   example.com  1.1.1.1
nslookup -type=AAAA example.com 1.1.1.1
nslookup -type=MX  example.com  1.1.1.1
nslookup -type=TXT example.com  1.1.1.1
nslookup -type=SOA example.com  1.1.1.1

# Also pull (replace example.com)
nslookup -type=CNAME www.example.com 1.1.1.1
nslookup -type=TXT   _dmarc.example.com 1.1.1.1
nslookup -type=TXT   default._domainkey.example.com 1.1.1.1
nslookup -type=TXT   privateemail._domainkey.example.com 1.1.1.1
nslookup -type=SRV   _autodiscover._tcp.example.com 1.1.1.1
```

5. Store the snapshot in operator-private notes. **Never commit zone dumps that
   include street-address WHOIS, EPP codes, or mailbox passwords.**

Record types people forget: `MX`, `TXT` (SPF / DKIM / DMARC / domain-verify),
`SRV`, `CAA`, `AAAA`, `CNAME` for `www` / `mail` / `autodiscover`, Namecheap
`URL Redirect` (recreate on Cloudflare — the record type does not exist there),
and any `NS` delegations for subdomains.

---

## 3. What NOT to touch

This is the keep-her-afloat list. A transfer that “succeeds” while any of these
move is a failed job.

### Live sites and origins

- Do **not** change origin A/AAAA IPs “to clean them up.” Copy them.
- Do **not** orange-cloud a LIVE name on the first cutover. Grey-cloud, prove
  HTTP/HTTPS against the real origin, then optionally proxy.
- Do **not** switch Cloudflare SSL mode to Flexible if the origin already
  speaks HTTPS (redirect loops, mixed content).
- Do **not** enable Bot Fight, aggressive WAF, or “I’m Under Attack” on day one.
- Do **not** delete Namecheap URL Redirect rows until the Cloudflare Redirect
  Rule is live **and** proven. Then the Namecheap row is leftover, not a delete
  target during the cutover window.
- Do **not** point `@` at Cloudflare Pages / Workers as a side quest. That is a
  new site, not a transfer.

### Mail

- Do **not** orange-cloud `mail`, `webmail`, `autodiscover`, `autoconfig`, or
  any A/AAAA that an MX target uses.
- Do **not** put a CNAME on the zone apex if MX exists. CNAME-at-apex wins and
  mail dies. Namecheap documents this; it is still true on Cloudflare.
- Do **not** “simplify” two MX records into one.
- Do **not** rewrite SPF. Copy the exact TXT. Merging SPF by hand is how
  deliverability dies a week later.
- Do **not** cancel Namecheap Private Email, Email Forwarding, or cPanel mail
  because the registrar moved. Registrar ≠ mailbox.
- Do **not** assume Namecheap **Email Forwarding** survives NS change. Rebuild
  with Cloudflare Email Routing (or a real mailbox) **before** leaving BasicDNS
  if that name still needs forwarding.

### Namecheap account / products

- Do **not** unlock the whole Domain List in one sitting.
- Do **not** request EPP codes for names you will not submit the same day.
  Codes expire; leftover unlocks are an attack surface.
- Do **not** change registrant contact “to match Cloudflare” before transfer.
- Do **not** flip to Web Hosting DNS.
- Do **not** close the Namecheap account, cancel PremiumDNS, or cancel hosting
  until every name is transferred **and** mail/hosting still work on their own
  subscriptions.
- Do **not** disable WHOIS privacy across the list.

### COSMOS / Cloudflare account hygiene

- Do **not** create a second Cloudflare account.
- Do **not** rotate or re-upload R2 keys as part of this job.
- Do **not** bind Core, KDash, or Tailscale hostnames to these zones.
- Do **not** paste EPP, card numbers, or passwords into this repo, a work
  order, Slack, or a chat.

### Process

- Do **not** start Wave 3 because Wave 1 “looked fine in the dashboard.”
  Wave 1 proof is `dig`/`nslookup` + a fetch. Wave 3 is that plus a real
  browser hit on the live URL.
- Do **not** call a name done because Cloudflare showed a green badge.
  Done = the verification table in §8 has artifacts.

---

## 4. Email / MX caution

Mail breaks silently. Users notice hours later. Treat every MX-bearing name as
hostile until a send **and** a receive have been proven.

### Decision before NS change

| Current Mail Settings (Namecheap) | After Cloudflare NS | Action |
|---|---|---|
| No Email Service / no MX | No mail | Wave 1. Still copy any leftover TXT. |
| Email Forwarding (BasicDNS) | Forwarding **stops** unless rebuilt | Recreate as Cloudflare Email Routing *or* stand up a real mailbox **first**. |
| Private Email | Mailboxes stay at Namecheap | Copy the Private Email record set. Grey-cloud every mail CNAME. |
| Custom MX (Google / M365 / other) | Provider stays | Copy MX + SPF + DKIM + DMARC + any `autodiscover` exactly. |
| cPanel / Web Hosting mail | Mail stays on the hosting box | Copy MX + `mail`/`webmail` A records from Zone Editor. Grey-cloud `mail`. |
| Gmail preset (Namecheap) | Namecheap notes this preset is unreliable | Use Custom MX. Post-2023 Google Workspace is usually one MX: `SMTP.GOOGLE.COM` priority 1. Confirm in the Google Admin console, do not guess. |

### Private Email on Cloudflare (copy these; then verify against the live zone)

Namecheap’s own Cloudflare article
([KB 9967](https://www.namecheap.com/support/knowledgebase/article.aspx/9967/2176/how-to-set-up-dns-records-for-namecheap-email-service-with-cloudflare-cpanel-and-private-email/),
updated 2026-09-11) and the third-party-DNS article
([KB 1340](https://www.namecheap.com/support/knowledgebase/article.aspx/1340/2176/namecheap-private-email-records-for-domains-with-thirdparty-dns/),
updated 2026-08-27):

| Type | Name | Priority | Content | Proxy |
|---|---|---|---|---|
| MX | `@` | 10 | `mx1.privateemail.com` | n/a (always DNS-only) |
| MX | `@` | 10 | `mx2.privateemail.com` | n/a |
| TXT | `@` | — | `v=spf1 include:spf.privateemail.com ~all` | n/a |
| TXT | `default._domainkey` **or** `privateemail._domainkey` | — | Exact DKIM string from the Private Email panel | n/a |
| TXT | `_dmarc` | — | Existing DMARC if present; do not invent a `p=reject` if the old record was `p=none` | n/a |
| CNAME | `mail` | — | `privateemail.com` | **DNS only** |
| CNAME | `autodiscover` | — | `privateemail.com` | **DNS only** |
| CNAME | `autoconfig` | — | `privateemail.com` | **DNS only** |
| SRV | `_autodiscover._tcp` | 0 (weight 0, port 443) | `privateemail.com` | n/a |

DKIM hostname split (Namecheap, 2026-06-02):

- Subscription **on/after 2026-06-02:** host is `privateemail._domainkey`. Available as soon as the subscription exists.
- **Legacy** (before that date): host is `default._domainkey`. Older docs say “create a mailbox first.”

Copy the string from **Private Email → DKIM**. Do not type a `p=` by hand.

Webmail clients keep using `mail.privateemail.com` (IMAP 993 / SMTP 465). That
hostname is Namecheap’s, not yours. Do not “fix” it to `mail.yourdomain`.

### Other providers (do not invent values)

- **Google Workspace:** Admin console → Apps → Google Workspace → Gmail →
  MX records. Copy those, plus the Google SPF include and any `google._domainkey`.
- **Microsoft 365:** `*.mail.protection.outlook.com` MX, plus
  `autodiscover` CNAME, plus the MS SPF include and DKIM CNAMEs. All DNS-only.
- **cPanel:** MX as in Zone Editor; A `mail` → the cPanel IP, **DNS only**.

### Mail proof (required for MAIL and LIVE classes)

After NS is `Active`, before EPP:

1. `nslookup -type=MX example.com 1.1.1.1` matches the snapshot.
2. `nslookup -type=TXT example.com 1.1.1.1` still has the SPF.
3. DKIM host answers.
4. Send a message **from** the domain mailbox to an outside inbox (Gmail/etc.).
5. Send a message **to** the domain mailbox from outside.
6. If forwarding: trigger a real forward, do not stop at “record looks right.”

A green Cloudflare zone is not a mail test.

---

## 5. Unlock / EPP notes

Unlock is the last thing you do on a name, not the first.

### When

- Zone is `Active` on Cloudflare.
- Grey-cloud DNS matches the snapshot.
- HTTP (if LIVE) and mail (if MAIL) are proven.
- You are sitting in front of the Cloudflare **Transfer domains** page for
  **that one name**.

### Namecheap clicks

1. [Domain List](https://ap.www.namecheap.com/domains/domainlist) → **Manage**.
2. **Sharing & Transfer**.
3. **Transfer Out → Unlock** (registrar lock / `clientTransferProhibited`).
4. **AUTH CODE** / Get EPP. Namecheap asks for a transfer-out reason. Pick a
   true short reason (consolidating registrars). Do not write passwords there.
5. The code is emailed to the **registrant** address. Check spam.
6. Paste the code **only** into Cloudflare’s transfer field. Do not store it
   in this repo, a screenshot folder that syncs to git, or a chat.

### Rules

- One unlocked name at a time for LIVE/MAIL. PARK may unlock a small batch
  only if you will submit every EPP the same sitting.
- If you abort: **re-lock** immediately. Confirm WHOIS/RDAP no longer shows
  `clientTransferProhibited` cleared — wait up to a few hours if the panel and
  WHOIS disagree.
- Codes expire. If Cloudflare rejects the code, request a **fresh** one. Watch
  trailing spaces and line breaks on paste.
- Do not unlock because you “might transfer this weekend.”
- WHOIS privacy: leave on. If Cloudflare or Namecheap refuses a specific name
  and the refusal text names privacy, disable privacy **for that name only**,
  retry, then re-enable after the gaining registrar has the name.
- `.uk` family: no EPP. Ask Namecheap to set the IPS tag to Cloudflare’s tag
  (Cloudflare’s transfer UI / support page states the tag). If the field is
  missing, that is expected — see Cloudflare troubleshooting “`.uk` transfer
  uses an IPS tag.”

### After Cloudflare has the code

1. Confirm payment method (Keith). A declined charge can leave a half-started
   transfer.
2. Enter registrant contact **accurately**. Cloudflare redacts public WHOIS by
   default; ICANN still requires real data. Junk data can suspend the name.
3. Confirm the registration terms.
4. Watch mail for:
   - Cloudflare FOA (Form of Authorization), especially `.us`.
   - Namecheap “approve this transfer” mail.
5. Approve at Namecheap. Do not click **reject**. Leaving it can sit for ~5
   business days; some TLDs (`.mx`) up to ~10.
6. Cloudflare statuses: `Transfer in progress` → `Pending approval` → done.
   `Transfer rejected` → fix the cause, then **Retry** (re-enter a fresh code).

### Do not

- Change the registrant email after submitting (verification + 60-day lock).
- Re-lock the name while `pendingTransfer` is in flight (it will stall).
- Start a second transfer for the same name.

---

## 6. Staged waves

| Wave | Names | Allowed actions | Stop / go |
|---|---|---|---|
| **0 — Census** | All | Read Domain List, classify, snapshot, eligibility | No unlock. No NS change. |
| **1 — Park / redirect** | PARK + REDIRECT | CF zone + records + (redirects) + DNSSEC off + NS + prove | If a park name has surprise MX, reclassify to MAIL and stop that name. |
| **2 — Mail** | MAIL | Same, plus send/receive proof | One load-bearing mailbox at a time. |
| **3 — Live sites** | LIVE / HOST-BOUND | Same, plus real browser hit on apex **and** `www` | **One name.** Next name only after §8 is green. |
| **4 — Registrar** | Only names that passed their wave | Unlock → EPP → pay → approve FOA | Do not batch LIVE names. |
| **5 — Close-out** | Transferred names | Registrant verify, optional DNSSEC, leave Namecheap products | Do not close Namecheap. |

Wave 4 can follow each name immediately after that name’s DNS proof (preferred
for LIVE: DNS Monday, transfer Monday night). Or Wave 4 can wait until a whole
wave of PARK names is stable. Never Wave-4 a name that is still `Pending`.

Suggested calendar (quality over speed):

1. One evening: Wave 0 for the whole list.
2. Next sitting: Wave 1 DNS for all PARK names (NS change).
3. 24–48h later: Wave 1 registrar for those PARK names that stayed quiet.
4. Then Wave 2, one MAIL name through DNS **and** registrar before the next.
5. Then Wave 3, one LIVE name through DNS, sleep on it, then registrar.

---

## 7. Per-domain runbook

Copy this block into the operator notes for each name. Replace
`example.com`. Check boxes only when the artifact exists.

### A. Freeze

- [ ] Census row filled. Class = ______. Wave = ______.
- [ ] Eligibility gate all green, or name is BLOCKED with a written reason.
- [ ] Registrant inbox tested.
- [ ] Zone snapshot (panel + `nslookup`) saved. Snapshot date: ______.
- [ ] No registrant WHOIS edits scheduled.

### B. Cloudflare zone (still on Namecheap NS)

- [ ] Same Cloudflare account as R2. No new account.
- [ ] **Onboard a domain** → apex only (`example.com`, not `www.`).
- [ ] Plan: Free is enough for DNS + Registrar. Do not upsell yourself.
- [ ] Review every scanned record against the snapshot. Delete junk. Add misses.
- [ ] Recreate Namecheap URL Redirects as Cloudflare **Redirect Rules** (or
      Bulk Redirects). Prove with a `curl -I` against the Cloudflare zone
      **after** NS change — you cannot prove a redirect while NS still point at
      Namecheap.
- [ ] Every A/AAAA/CNAME that is not a public website: **DNS only**.
- [ ] LIVE websites: **DNS only** for the first 24h.
- [ ] Mail records match §4. No orange cloud on mail names.
- [ ] Assigned Cloudflare nameservers written in the notes (two hostnames,
      copied exactly). They are account-assigned; do not invent `ns1.cloudflare.com`.

### C. DNSSEC off (Namecheap, before NS)

- [ ] Advanced DNS → DNSSEC. If on: note the DS TTL, then disable / remove DS.
- [ ] Wait **at least 24 hours** (or the recorded DS TTL, whichever is longer).
- [ ] Confirm DS is gone at the parent:

```text
nslookup -type=DS example.com 1.1.1.1
```

Empty/NX is the go signal. A leftover DS + new NS = an outage.

Namecheap path: Domain List → Manage → **Advanced DNS** → DNSSEC toggle
([Custom-DNS DS management](https://www.namecheap.com/support/knowledgebase/article.aspx/9722/2232/managing-dnssec-for-domains-pointed-to-custom-dns);
BasicDNS/PremiumDNS uses the same tab’s DNSSEC control). Cloudflare’s
transfer page also links a Namecheap-specific DNSSEC article from their
provider list.

### D. Nameserver cutover (the reversible-ish step)

- [ ] Cloudflare zone still matches the snapshot.
- [ ] Namecheap → Manage → **Nameservers** → **Custom DNS**.
- [ ] Paste the two Cloudflare NS **exactly**. Green check.
- [ ] Do not pick BasicDNS, PremiumDNS, or Web Hosting DNS.
- [ ] Wait until Cloudflare zone status is **Active** (minutes to 24h).
- [ ] Run the verification commands in §8.1–8.3.

**Rollback (only while Namecheap is still the registrar):** switch the
Nameservers dropdown back to the **previous** setting (BasicDNS / hosting /
old custom) **if and only if** the snapshot shows those records still live
there. If you already emptied Advanced DNS, rollback is “re-type the snapshot
onto BasicDNS,” not a toggle. This is why the snapshot exists.

### E. Registrar transfer (the one-way step)

- [ ] §8 is green for this name.
- [ ] Cloudflare → [Transfer domains](https://dash.cloudflare.com/?to=/:account/domains/transfer).
- [ ] Name appears (Active). If missing: zone is Pending, TLD unsupported, or
      60-day lock — stop and read
      [troubleshooting](https://developers.cloudflare.com/registrar/troubleshooting/).
- [ ] Namecheap unlock + fresh EPP (or IPS tag for `.uk`).
- [ ] Paste code. Confirm contact. Confirm payment (Keith).
- [ ] Approve Namecheap / FOA email.
- [ ] Status leaves `Pending approval`.
- [ ] RDAP/WHOIS registrar field shows Cloudflare. Date: ______.
- [ ] Registrant verification email completed (15-day fuse).

### F. After

- [ ] Optional: enable DNSSEC in Cloudflare (one click after Registrar owns it).
      Wait 1–2 days for DS to appear at the registry.
      [Enable DNSSEC](https://developers.cloudflare.com/registrar/get-started/enable-dnssec/).
- [ ] Namecheap lock is irrelevant now; Cloudflare locks transfers by default.
- [ ] Private Email / hosting / Workspace subscriptions **still billed at the
      old vendors**. Do not cancel.
- [ ] Orange-cloud the LIVE website records only after a quiet day, then
      re-prove HTTPS (certificate should be Cloudflare Universal SSL).

---

## 8. Verification (runtime binding)

A name is not transferred because a UI said so. Quote the artifact.

### 8.1 Nameservers (after cutover, before EPP)

```text
nslookup -type=NS example.com 1.1.1.1
nslookup -type=NS example.com 8.8.8.8
```

Expect the **two** Cloudflare-assigned nameservers from the zone Overview.
`whatsmydns.net` is optional and cache-heavy; the two public resolvers are the
gate.

Cloudflare dashboard: zone **Active**, not Pending.

### 8.2 Apex and www (LIVE / REDIRECT)

```text
nslookup -type=A    example.com     1.1.1.1
nslookup -type=AAAA example.com     1.1.1.1
nslookup -type=A    www.example.com 1.1.1.1
```

Grey-cloud: answers must match the snapshot IPs.
Orange-cloud (later): answers will be Cloudflare anycast, **not** the origin.
That is expected; then prove HTTP, not the IP.

```text
curl -sI https://example.com
curl -sI https://www.example.com
```

Expect the same status class as before the cutover (200/301/302 — not NXDOMAIN,
not 530, not a Namecheap parking page you did not ask for).

Browser: Keith hits the real URL. A `curl` from this cloud agent is not Keith’s
users, but it is the unattended gate.

### 8.3 Mail (MAIL / LIVE-with-mail)

```text
nslookup -type=MX  example.com 1.1.1.1
nslookup -type=TXT example.com 1.1.1.1
```

Plus DKIM host(s) from the snapshot. Then the two real messages in §4.

### 8.4 Registrar (after Wave 4)

```text
# RDAP is cleaner than whois when privacy is on
curl -s "https://rdap.org/domain/example.com"
```

Read `status` and the registrar object. Expect Cloudflare (or the IANA
registrar name Cloudflare uses) and **no** `pendingTransfer` once complete.
`clientTransferProhibited` after success is normal (new lock).

Dashboard: Transfer Domains no longer lists the name as in progress; it sits
under Manage Domains.

### 8.5 Negative proofs (failures that look like success)

| Looks like | Actually | What to run |
|---|---|---|
| Cloudflare “Active” | Resolver still on Namecheap NS | `nslookup -type=NS` at 8.8.8.8 |
| Site loads for you | Your DNS cache; others NXDOMAIN | Second resolver + phone off Wi-Fi |
| MX records present | DKIM missing; outbound junked | send-from test |
| Transfer “in progress” 10 minutes | Normal; not done | Wait / approve FOA |
| Transfer “done” in CF | Registrant verify ignored | Check the 15-day mail; RDAP NS still Cloudflare |

### 8.6 Done line (paste into operator notes)

```text
domain: example.com
wave: 3
cf_zone: Active
ns_1.1.1.1: <ns1>.ns.cloudflare.com / <ns2>.ns.cloudflare.com
http_apex: <status>
http_www: <status>
mx: <copied / none>
mail_send: ok|n/a
mail_recv: ok|n/a
rdap_registrar: Cloudflare
rdap_status: ...
registrant_verified: yes|pending
epp_stored_in_repo: no
when: 2026-__-__
```

If any field is a wish, the name is not done.

---

## 9. Troubleshooting (do not improvise)

Use [Cloudflare transfer troubleshooting](https://developers.cloudflare.com/registrar/troubleshooting/)
first. Short map:

| Symptom | Likely cause | Action |
|---|---|---|
| No EPP field / name missing on Transfer page | Zone Pending, unsupported TLD, 60-day lock | Fix NS/DNSSEC; wait; or leave BLOCKED |
| Zone stuck Pending >24h | NS not updated, typo in NS, DNSSEC still on | `nslookup -type=NS` and `-type=DS` |
| Site dead after NS | Incomplete zone, orange-cloud on a non-HTTP service, leftover DS | Grey-cloud; restore missing records from snapshot; rollback NS if needed |
| Mail dead | MX/SPF/DKIM missed; mail A/CNAME proxied; apex CNAME | §4; grey-cloud; no apex CNAME |
| `clientTransferProhibited` | Still locked, or re-locked | Unlock again; wait up to 5–24h |
| Auth code invalid | Expired, whitespace, wrong name | Fresh code, paste clean |
| Transfer rejected | FOA declined; privacy/protection; registry year cap; Namecheap reject-all | Read the rejection; Retry; do not spam retries |
| Payment failed after code | Card declined | Update billing; check for a half-started transfer |
| Stuck >5 business days | Losing registrar holding | Approve in Namecheap; then Namecheap support |
| Parking NS after transfer | Registrant email not verified (15 days) | Verify immediately |
| `.uk` no auth field | IPS tag flow | Ask Namecheap to set Cloudflare’s IPS tag |

Restart (not `.uk`): Cloudflare Manage Domain → **Cancel Transfer and Retry** →
new code + WHOIS confirm.

---

## 10. Close-out (Wave 5)

- [ ] Every transferred name: RDAP registrar = Cloudflare; registrant verified.
- [ ] Every leftover Namecheap name: still locked; census says why it stayed.
- [ ] Private Email / hosting / Workspace still work; subscriptions still paid
      where the mail/site actually lives.
- [ ] No EPP codes left in mail archives you are about to forward; no codes in
      git.
- [ ] Do **not** delete the Namecheap account. Keep it until the next renewal
      cycle on Cloudflare has succeeded for every moved name.
- [ ] Optional DNSSEC on at Cloudflare after a quiet week.
- [ ] This file stays a runbook. Execution evidence lives in operator notes,
      not in a green sentence in chat.

---

## 11. Master checklist (print this)

Wave 0

- [ ] Domain List opened from the URL above; census filled from the panel.
- [ ] Every name classified. LIVE default if unsure.
- [ ] Snapshots exist. Eligibility gates ticked or BLOCKED with a reason.
- [ ] Cloudflare account is the existing one; payment method on file (Keith).
- [ ] No unlocks yet.

Per name (Waves 1–4)

- [ ] Zone rebuilt on Cloudflare from the snapshot (scan is not trusted).
- [ ] Mail/redirect special cases handled *before* NS.
- [ ] DNSSEC off + DS TTL waited.
- [ ] Custom DNS → assigned Cloudflare NS only.
- [ ] `Active` + §8 proofs.
- [ ] Unlock + EPP the same sitting; code not saved in-repo.
- [ ] FOA approved; RDAP shows Cloudflare; email verified.

Stop conditions (any one)

- Registrant inbox unreachable.
- TLD not on the Cloudflare list.
- LIVE site or mail fails §8.
- 60-day lock, hold, redemption, or year-cap reject.
- Temptation to “just orange-cloud it and see.”

---

## 12. Sources

Read these if the dashboard moved. Dates are last-updated on the page when this
file was written (2026-09-14).

- Cloudflare — [Transfer domain](https://developers.cloudflare.com/registrar/get-started/transfer-domain-to-cloudflare/) (2026-04-24)
- Cloudflare — [Transfer troubleshooting](https://developers.cloudflare.com/registrar/troubleshooting/) (2026-04-24)
- Cloudflare — [Full-setup nameservers](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/) (2026-07-29)
- Cloudflare — [Proxy status](https://developers.cloudflare.com/dns/proxy-status/) (2026-04-21)
- Cloudflare — [Enable DNSSEC](https://developers.cloudflare.com/registrar/get-started/enable-dnssec/) (2026-04-24)
- Cloudflare — [Supported TLDs](https://developers.cloudflare.com/registrar/top-level-domains/) (2026-05-15)
- Cloudflare — [TLD policies](https://www.cloudflare.com/tld-policies/)
- Cloudflare — [Registrar FAQ](https://developers.cloudflare.com/registrar/faq/)
- Namecheap — [Domain List](https://ap.www.namecheap.com/domains/domainlist)
- Namecheap — [Transfer out](https://www.namecheap.com/support/knowledgebase/article.aspx/258/84/what-should-i-do-to-transfer-a-domain-from-namecheap/) (2023-08-15)
- Namecheap — [Registrar lock](https://www.namecheap.com/support/knowledgebase/article.aspx/380/46/how-do-i-setrelease-registrar-lock-for-a-domain/)
- Namecheap — [Change nameservers](https://www.namecheap.com/support/knowledgebase/article.aspx/767/10/how-can-i-change-the-nameservers-for-my-domain/) (2025-04-03)
- Namecheap — [Mail settings / MX](https://www.namecheap.com/support/knowledgebase/article.aspx/322/2237/required-spf-and-dkim-settings-for-private-email/) (2025-01-20)
- Namecheap — [Private Email on Cloudflare](https://www.namecheap.com/support/knowledgebase/article.aspx/9967/2176/how-to-set-up-dns-records-for-namecheap-email-service-with-cloudflare-cpanel-and-private-email/) (2026-09-11)
- Namecheap — [Private Email on third-party DNS](https://www.namecheap.com/support/knowledgebase/article.aspx/1340/2176/namecheap-private-email-records-for-domains-with-thirdparty-dns/) (2026-08-27)
- Namecheap — [DNSSEC (Custom DNS)](https://www.namecheap.com/support/knowledgebase/article.aspx/9722/2232/managing-dnssec-for-domains-pointed-to-custom-dns/)

Related COSMOS notes (do not mix jobs): `docs/OFFSITE_READY.md` (R2),
`docs/CREDENTIALS_NEEDED.md` (Keith owns keys), `docs/AGENT_BOUNDARIES.md` item 5
(no money, no credentials in-agent).

---

## 13. Census worksheet (blank)

Fill from the Domain List. Do not commit completed rows that include EPP,
passwords, or full WHOIS.

| Domain | TLD | Class | Expires | Lock | NS | DNSSEC | Mail | Web | Wave | Block reason |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |
| | | | | | | | | | | |

---

*End of staged ops doc. No cutover has been performed. No secrets belong in a
revision of this file.*
