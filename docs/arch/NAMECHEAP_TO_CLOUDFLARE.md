# NAMECHEAP → CLOUDFLARE — operator runbook (DNS cutover + optional registrar transfer)

**Consumer:** Keith (the operator). **Agents:** read-only reference; **do not execute** any step
that changes registrar state, nameservers, or EPP transfers.

**Written:** 2026-09-14. **Scope:** move DNS authority (and optionally registration) for a domain
from Namecheap to Cloudflare. **COSMOS touchpoint:** public ITC reads use
`https://ai.dchambers.com/…` (`cosmos/cosmos_itc.py` `DEFAULT_INDEX_URL`); R2 backup and custom
domains use the same Cloudflare account — keep DNS, R2, and Workers in one intentional layout.

---

## 0. Hard boundary — no live transfers from automation

| Rule | Why |
|------|-----|
| **No agent, script, or CI job runs registrar transfer, unlock, auth-code reveal, or nameserver change.** | Irreversible or hard-to-rollback; credential and fraud surfaces. |
| **This document is the procedure.** Keith performs UI steps in Namecheap and Cloudflare dashboards (or approved CLI with Keith's session). | Matches `docs/AGENT_BOUNDARIES.md` — Keith does money, credentials, and external control planes. |
| **Dry-run only in repo work:** inventory DNS, export zone file, screenshot TTLs, write a cutover checklist — **stop before** any Save that mutates production. | "No live transfers" for agent sessions means **zero production mutations** unless Keith is at the keyboard for that step. |

If a work order says "execute cutover," the deliverable is an **updated checklist with timestamps and probe output Keith pasted**, not an agent-performed cutover.

---

## 1. Choose the path (do not mix them blindly)

| Path | Registration stays | DNS authority moves | Auth code (EPP) | Typical reason |
|------|-------------------|---------------------|-----------------|----------------|
| **A — DNS only** | Namecheap | Cloudflare (after NS cutover) | **Not used** | Fastest; keep Namecheap billing; use CF proxy, R2 custom hostnames, Workers. |
| **B — Registrar transfer** | Cloudflare Registrar | Cloudflare (automatic after transfer completes) | **Required** | Single bill, CF registrar features; longer calendar time (ICANN). |

**Default for COSMOS edge work:** Path **A** unless Keith explicitly wants Path **B**.

Path A steps: §4 (inventory) → §5 (unlock only if needed for other reasons) → §6 (add zone) → §7 (NS cutover) → §8 (post-check).  
Path B steps: §4 → §5 → §6 (add zone, **do not** cut NS until transfer policy clear) → §5.3 (auth code) → Cloudflare **Transfer** wizard → wait for completion → §8.

---

## 2. Preconditions (operator checklist)

Copy into a local note (not committed); fill before changing anything.

```
domain:                 _________________________
path:                   A (DNS only)  /  B (registrar transfer)
cloudflare_account:     _________________________  (same account as R2 if applicable)
namecheap_login:        2FA device available: Y / N
registrar_lock_before:  ON / OFF
whois_privacy:          ON / OFF  (may block transfer emails — know which inbox receives ICANN mail)
current_nameservers:    _________________________
apex_A_AAAA:            _________________________
critical_hostnames:     apex, www, ai, mail, _dmarc, ACME/_acme-challenge, R2 CNAME targets
lowest_TTL_seen:        _____ s  (plan propagation from this)
maintenance_window:     from _______ UTC  to _______ UTC
rollback_NS_pair:       _________________________  (write down BEFORE cutover)
```

**COSMOS-critical hostnames (verify in inventory even if migrating another zone):**

- `ai.dchambers.com` — ITC / GrokDex public index (`GrokDex.csv`, `00_INDEX/…`).
- Any R2 **custom domain** or public bucket hostname tied to `builds/backup` / ITC publish — must exist in Cloudflare DNS **before** or **immediately after** cutover with correct target.

---

## 3. Inventory and export (no production change)

### 3.1 Namecheap — Advanced DNS snapshot

1. Log in: [Namecheap → Domain List](https://www.namecheap.com/myaccount/login-signup/) → **Manage** on the domain.
2. **Advanced DNS** tab: export or screenshot every host record (type, host, value, TTL).
3. **Domain** tab: note **NAMESERVERS** (Namecheap Basic/Premium/custom) and **DOMAIN LOCK**.

### 3.2 Authoritative check from a resolver (baseline)

From any machine (replace `<DOMAIN>`):

```bash
dig +short NS <DOMAIN>
dig +short A <DOMAIN>
dig +short A ai.<DOMAIN>
dig +short CNAME <critical-host>
```

Save output in the local cutover note. Post-cutover, §8 compares against these baselines.

### 3.3 Cloudflare — account ready

1. Log in: [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Confirm the account that holds **R2** (if used) is the same account where the zone will live.
3. Do **not** add the zone twice; search existing zones first.

---

## 4. Namecheap — unlock domain (Path A and B)

Unlock is required for **registrar transfer (Path B)**. For **DNS-only (Path A)**, unlock is usually **not** required for nameserver change — but transfer lock must be **understood** so an accidental transfer request is not started.

1. **Domain List** → **Manage** → **Domain** tab.
2. **DOMAIN LOCK** (or **Registrar Lock**):  
   - Path **B:** set to **OFF** / Unlocked. Wait for UI confirmation (some TLDs take a few minutes).  
   - Path **A:** leave **ON** unless Namecheap support docs for your TLD say otherwise for custom nameservers only.
3. Record timestamp: `unlock_at: ___________`

**Fail-closed:** If lock will not disable, **stop** — do not request auth code or start Cloudflare transfer until lock is OFF (Path B).

---

## 5. Auth code (EPP) — Path B only

**Skip entirely for Path A (DNS-only).**

### 5.1 Request the code (Namecheap)

1. Same **Manage** → **Domain** tab (or **Sharing & Transfer** depending on UI revision).
2. **AUTH CODE** / **Get Auth Code** / **EPP Code** — reveal once; copy to a **password manager**, not chat, not git, not ledger.
3. Properties:
   - Often **single-use** or invalidated after successful transfer.
   - May **rotate** if you click "refresh" — use the latest only.
   - Valid only while domain is **unlocked** and not in **pending transfer**.

### 5.2 Give the code to Cloudflare (not to an agent)

1. Cloudflare Dashboard → **Domain Registration** → **Transfer Domains** (or **Add site** → transfer flow).
2. Enter domain; paste auth code when prompted.
3. Approve confirmation emails (registrant contact must be reachable — privacy services may forward to a hidden inbox; know which one).

### 5.3 While transfer is pending

- Do **not** change nameservers at Namecheap unless Cloudflare's transfer UI explicitly instructs (follow the active wizard — UI text wins over this doc).
- Do **not** renew at Namecheap for the same term unless you intend to cancel transfer.
- Typical duration: **5–7 days** for gTLDs; some complete faster if auto-approve.

Record: `transfer_initiated_at`, `transfer_order_id` (Cloudflare UI), `expected_completion` from wizard.

---

## 6. Cloudflare — add site (zone) and DNS records

### 6.1 Add the domain

1. Dashboard → **Add a site** → enter apex `<DOMAIN>` → select plan (Free is fine for DNS + proxy).
2. Cloudflare scans existing DNS. **Compare** every scanned row to §3.1 export; fix omissions before cutover.
3. Manually add missing records (common gaps):
   - `MX`, `TXT` (SPF, DKIM, DMARC), `SRV`
   - `CNAME` for `ai`, `www`, R2 custom hostnames
   - `AAAA` if apex uses IPv6 at Namecheap

### 6.2 Proxy status (orange cloud)

| Record | Guidance |
|--------|----------|
| `A`/`CNAME` for web / ITC (`ai`, `www`) | Usually **Proxied** (orange) for CDN/WAF/TLS — unless you need direct origin IP exposure. |
| `MX` | **DNS only** (grey). |
| `TXT` for mail auth | **DNS only**. |
| R2 public bucket / custom domain | Follow [R2 custom domain](https://developers.cloudflare.com/r2/buckets/public-buckets/#custom-domains) docs — often **CNAME** to `*.r2.cloudflarestorage.com` or Workers route; match what ITC publish already uses. |

**COSMOS:** After records exist in Cloudflare, confirm `https://ai.dchambers.com/GrokDex.csv` (or your target host) resolves to the **same content path** as pre-cutover (§8.3).

### 6.3 SSL/TLS mode (before traffic hits proxy)

1. **SSL/TLS** → set mode appropriate to origin (often **Full (strict)** if origin has valid cert; **Full** if origin uses Cloudflare-origin cert only on R2).
2. Enable **Always Use HTTPS** only when apex/www redirects are intentional.

### 6.4 Nameservers Cloudflare will assign

On the **Overview** page after adding the site, Cloudflare shows **two** nameservers, e.g.:

```
<name>.ns.cloudflare.com
<name>.ns.cloudflare.com
```

Copy both exactly into §7 — typo breaks delegation.

**Stop here for Path B** until registrar transfer completes, unless the transfer wizard tells you to update NS earlier.

---

## 7. Nameserver cutover (Path A — and Path B when instructed)

**Operator-only step. Double-check §2 rollback pair before Save.**

### 7.1 Lower TTL (optional but recommended)

24–48 hours before cutover, if Namecheap allows editing TTL on critical records, lower to **300s** (5 min). Re-export §3.1 after change.

### 7.2 Namecheap — custom nameservers

1. **Domain List** → **Manage** → **Domain** tab → **NAMESERVERS**.
2. Select **Custom DNS** (not "Namecheap BasicDNS").
3. Enter **both** Cloudflare nameservers from §6.4 (no trailing dots required in UI; if required, use FQDN with dot).
4. **Save**. Namecheap may email confirmation — approve if prompted.

### 7.3 Do not

- Delete the zone in Cloudflare while debugging — fix records in-zone.
- Re-enable **DOMAIN LOCK** in a way that blocks transfer completion (Path B) — follow Cloudflare transfer status page.

Record: `ns_changed_at: ___________`

---

## 8. Post-check (required evidence)

Run after NS change (Path A) or transfer **Active** (Path B). Propagation is TTL-bound; re-run checks for at least **2× lowest TTL** from §2.

### 8.1 Delegation

```bash
dig +short NS <DOMAIN>
# Expect: only the two *.ns.cloudflare.com names from §6.4
```

From a **non-local** resolver if possible (public DNS or `dig @1.1.1.1`):

```bash
dig @1.1.1.1 +short NS <DOMAIN>
dig @8.8.8.8 +short NS <DOMAIN>
```

### 8.2 Critical records

```bash
dig +short A <DOMAIN>
dig +short A ai.<DOMAIN>
dig +short CNAME <each-critical-host>
```

Compare to §3.2 baseline — values should match **intent** (IP/CNAME targets), not necessarily old Namecheap proxy paths.

### 8.3 HTTPS and COSMOS ITC smoke

```bash
curl -sS -o /dev/null -w "%{http_code} %{url_effective}\n" "https://ai.dchambers.com/GrokDex.csv"
# Expect: 200 (or documented redirect chain ending in 200)
```

Optional: fetch first line of CSV and confirm header row unchanged from pre-cutover snapshot.

### 8.4 Cloudflare dashboard

1. **Overview** → status **Active** (not "Pending nameserver update").
2. **DNS** → no unexpected orange/grey mismatches on mail records.
3. **SSL/TLS** → edge certificate **Active** for `ai` / apex as needed.

### 8.5 Mail (if domain sends/receives mail)

Send/receive test message after MX/SPF/DKIM verify. DNS-only cutover breaks mail if MX/TXT were not copied.

### 8.6 Operator log template (paste into local note, not git)

```
ns_changed_at:
dig_NS_cloudflare:
curl_GrokDex_http_code:
cloudflare_zone_status:
anomalies:
signed_off_by: Keith
signed_off_at:
```

---

## 9. Rollback (Path A)

If post-check fails and you must restore service quickly:

1. Namecheap → **NAMESERVERS** → restore **Namecheap BasicDNS** (or §2 `rollback_NS_pair`).
2. Wait TTL; re-run §8.2 against §3.2 baseline.
3. Root-cause in Cloudflare zone (missing record) before attempting cutover again.

**Path B rollback** during pending transfer: contact Cloudflare support / cancel transfer per their UI; may require Namecheap support if transfer already approved — **avoid** by completing §4–§6 before initiating transfer.

---

## 10. After cutover — COSMOS hygiene

| Item | Action |
|------|--------|
| R2 credentials | Unchanged path: `live/config/r2_credentials.json` — DNS move does not rotate keys (`docs/OFFSITE_READY.md`). |
| ITC publish | Confirm publish pipeline still targets the same R2/custom domain; no code change if hostname unchanged. |
| Tailscale vs public edge | Phone/remote may use `cosmos up` (Tailscale); public DNS is separate — both should be documented in operator notes. |
| Agents | Update work orders with **probe output** (§8), not "done" without artifacts. |

---

## 11. Quick reference links

| Surface | URL |
|---------|-----|
| Namecheap login | https://www.namecheap.com/myaccount/login-signup/ |
| Cloudflare dashboard | https://dash.cloudflare.com/ |
| Cloudflare DNS docs | https://developers.cloudflare.com/dns/ |
| Cloudflare registrar transfer | https://developers.cloudflare.com/registrar/ |
| R2 custom domains | https://developers.cloudflare.com/r2/buckets/public-buckets/#custom-domains |

---

## 12. Document history

| Date | Change |
|------|--------|
| 2026-09-14 | Initial operator runbook: unlock, auth code (Path B), Cloudflare add, NS cutover, post-check; agent no-live-transfer boundary. |
