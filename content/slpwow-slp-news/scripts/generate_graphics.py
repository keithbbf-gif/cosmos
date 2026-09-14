#!/usr/bin/env python3
"""Generate SVG assets, embed snippets, RIGHTS rows, and patch articles."""

from __future__ import annotations

import html
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
EMBEDS = ROOT / "embeds"
ART = ROOT / "articles"
RIGHTS = ROOT / "RIGHTS.md"

PALETTE = {
    "paper": "#FAF9F7",
    "ink": "#1E293B",
    "muted": "#64748B",
    "card": "#FFFFFF",
    "rule": "#CBD5E1",
    "teal": ("#CCFBF1", "#0F766E"),
    "indigo": ("#E0E7FF", "#4338CA"),
    "amber": ("#FEF3C7", "#B45309"),
    "rose": ("#FFE4E6", "#BE123C"),
    "slate": ("#F1F5F9", "#475569"),
}

BEAT_THEME = {
    "ASLP-IC": "teal",
    "Medicare / CMS / ASHA": "indigo",
    "Licensure / school workforce": "amber",
    "Research": "rose",
    "Practice trends": "slate",
}

# slug, beat, file stem, svg title, desc, alt, caption lead, bullets, kind
GRAPHICS: list[dict] = [
    {
        "slug": "four-states-now-issuing-aslp-ic-privileges",
        "beat": "ASLP-IC",
        "file": "four-state-issuance-map",
        "title": "ASLP-IC issuance status schematic (Sept. 2026)",
        "desc": "Editorial map-style card showing four issuing member states versus 33 enacted-but-not-issuing jurisdictions on the Commission map.",
        "alt": "Schematic compact map legend: four states issuing privileges, thirty-three enacted members still onboarding, four with active legislation, fourteen with none",
        "caption": "Four jurisdictions issue compact privileges; enactment alone does not equal issuance.",
        "bullets": [
            "Issuing (4): LA · WV · OH · TN",
            "Enacted, not issuing: 33 members",
            "CompactConnect: app.compactconnect.org",
            "Practice site = client location",
        ],
        "kind": "map",
    },
    {
        "slug": "enacted-is-not-operational-aslp-ic",
        "beat": "ASLP-IC",
        "file": "enacted-vs-operational-buckets",
        "title": "Enacted versus operational compact privileges",
        "desc": "Four-bucket schematic contrasting statute enactment, board onboarding, CompactConnect issuance, and ordinary single-state licensure.",
        "alt": "Four labeled buckets: enacted law, operational issuance, onboarding queue, and single-state license still required where compact is not issuing",
        "caption": "Enactment fills a map bucket; issuance needs onboarding and a live privilege.",
        "bullets": [
            "Enacted ≠ issuing",
            "Home board must onboard data",
            "No account until home state is live",
            "ASHA Oct. 2025 first ops day",
        ],
        "kind": "buckets",
    },
    {
        "slug": "tennessee-goes-live-aslp-ic-may-2026",
        "beat": "ASLP-IC",
        "file": "tennessee-go-live-timeline",
        "title": "Tennessee ASLP-IC issuance timeline (schematic)",
        "desc": "Timeline card from October 2025 first issuers through Tennessee Commission update 28 May 2026.",
        "alt": "Timeline schematic from October 2025 Louisiana and West Virginia issuance through Ohio February 2026 and Tennessee May 2026",
        "caption": "Tennessee joined the issuing column on the Commission’s 28 May 2026 notice.",
        "bullets": ["Oct 2025: LA, WV open", "Feb 2026: OH processing", "May 2026: TN issuing", "Verify on Commission PDFs"],
        "kind": "timeline",
    },
    {
        "slug": "ohio-opens-aslp-ic-privileges-february-2026",
        "beat": "ASLP-IC",
        "file": "ohio-shp-compact-start",
        "title": "Ohio SHP board compact processing start",
        "desc": "News card noting Ohio Speech and Hearing Professionals Board processing from 9 February 2026.",
        "alt": "News card schematic: Ohio board begins processing ASLP-IC privilege applications 9 February 2026",
        "caption": "Ohio’s board date is public; home-state rules still gate first-time FBI checks.",
        "bullets": ["SHP board notice: 9 Feb 2026", "CompactConnect dashboard", "Client-location practice rule", "School credentials separate"],
        "kind": "card",
    },
    {
        "slug": "compactconnect-fifty-dollar-commission-fee",
        "beat": "ASLP-IC",
        "file": "compactconnect-fee-stack",
        "title": "CompactConnect fee stack schematic",
        "desc": "Layered fee card showing $50 Commission privilege fee plus variable state board charges.",
        "alt": "Stacked fee schematic: fifty dollar ASLP-IC Commission fee per privilege with additional state board fees listed separately",
        "caption": "The published $50 is a Commission line item, not the full cost of mobility.",
        "bullets": ["$50 Commission fee / privilege", "State fees extra", "Renewal rules on Commission site", "Not a substitute for MAC billing"],
        "kind": "stack",
    },
    {
        "slug": "pending-aslp-ic-bills-michigan-pennsylvania-new-jersey-new-mexico",
        "beat": "ASLP-IC",
        "file": "pending-compact-bills-card",
        "title": "Pending compact legislation card (Feb. 2026 newsletter)",
        "desc": "Schematic list of jurisdictions named in a Commission newsletter as having active bills; map may change after publication.",
        "alt": "News card listing Michigan, Pennsylvania, New Jersey, and New Mexico as jurisdictions with pending compact bills in a February 2026 newsletter",
        "caption": "Newsletter names are a snapshot; only enacted law and issuing status count for practice.",
        "bullets": ["MI · PA · NJ · NM named", "Newsletter ≠ enacted", "Check state legislature", "Map updates asynchronously"],
        "kind": "card",
    },
    {
        "slug": "home-state-fbi-background-checks-aslp-ic",
        "beat": "ASLP-IC",
        "file": "fbi-check-home-state-gate",
        "title": "Home-state FBI background check gate",
        "desc": "Flow schematic showing first privilege FBI check routed through home licensing board, not the CompactConnect portal alone.",
        "alt": "Flow schematic: first compact privilege FBI background check handled by home state board before CompactConnect completes privilege",
        "caption": "The portal registers clinicians; home boards still own background-check policy.",
        "bullets": ["First privilege: home board", "Portal cannot bypass statute", "Renewals differ by state", "Document board letters"],
        "kind": "flow",
    },
    {
        "slug": "school-slps-and-compact-privileges",
        "beat": "ASLP-IC",
        "file": "school-credential-dual-gate",
        "title": "School SLP credential versus compact privilege",
        "desc": "Two-gate schematic: compact privilege to practice versus educator certificate and district assignment rules.",
        "alt": "Two-column schematic comparing ASLP-IC compact privilege with school educator certificate and district hiring requirements",
        "caption": "A privilege to practice is not a teaching certificate or an IEP assignment.",
        "bullets": ["Compact: practice authority", "School: educator credential", "District: contract & caseload", "Both may be required"],
        "kind": "compare",
    },
    {
        "slug": "practice-happens-where-the-client-is",
        "beat": "ASLP-IC",
        "file": "client-location-practice-pin",
        "title": "Client-location practice pin (compact)",
        "desc": "Map pin schematic: telepractice encounter jurisdiction follows the client’s location, not the clinician’s home office.",
        "alt": "Schematic map pin on client location with telepractice path showing practice jurisdiction follows patient site not clinician home",
        "caption": "The Commission’s geography sentence governs both in-person and tele encounters.",
        "bullets": ["Client site = practice state", "Tele does not move the pin", "Non-issuing members: ordinary license", "Document location in chart"],
        "kind": "map",
    },
    {
        "slug": "military-spouse-portability-promise-aslp-ic",
        "beat": "ASLP-IC",
        "file": "military-spouse-portability-card",
        "title": "Military spouse portability on the benefits list",
        "desc": "Benefits card juxtaposing Commission portability messaging with four-state issuance reality as of September 2026.",
        "alt": "News card contrasting military spouse portability promise on Commission materials with only four states issuing privileges in September 2026",
        "caption": "Portability is the design goal; issuance footprint is still narrow.",
        "bullets": ["Benefit named on Commission site", "4 states issuing", "33 still onboarding", "Verify privilege before move"],
        "kind": "card",
    },
    {
        "slug": "aslp-ic-commission-newsletters-are-the-record",
        "beat": "ASLP-IC",
        "file": "commission-newsletter-record",
        "title": "Commission newsletter as dated public record",
        "desc": "Document stack schematic treating Commission PDF newsletters as primary dated artifacts for rule changes.",
        "alt": "Schematic stack of dated ASLP-IC Commission PDF newsletters labeled as the public record for operational updates",
        "caption": "Open the PDFs; social posts are not the record.",
        "bullets": ["PDF newsletters dated", "Map lags newsletter", "Save copies locally", "Cross-check state boards"],
        "kind": "card",
    },
    {
        "slug": "2026-medicare-conversion-factor-two-tracks-slps",
        "beat": "Medicare / CMS / ASHA",
        "file": "conversion-factor-two-tracks",
        "title": "2026 Medicare conversion factor two-track schematic",
        "desc": "Dual-track card for MIPS-participating versus non-participating clinician conversion factors affecting therapy payments.",
        "alt": "Two-track schematic comparing Medicare 2026 conversion factor paths for MIPS participants versus clinicians exempt from mandatory MIPS",
        "caption": "Most SLPs are on the exempt track but still feel both numbers in policy fights.",
        "bullets": ["Two CF values in 2026", "MIPS optional for most SLPs", "ASHA publishes illustrative PDF", "MAC letter is billing authority"],
        "kind": "compare",
    },
    {
        "slug": "two-clocks-medicare-telehealth-codes-vs-slp-authority-2026",
        "beat": "Medicare / CMS / ASHA",
        "file": "telehealth-two-clocks",
        "title": "Medicare telehealth two clocks schematic",
        "desc": "Parallel timelines for HCPCS telehealth codes availability and statutory SLP telehealth authority sunsets.",
        "alt": "Parallel timeline schematic: Medicare telehealth billing codes versus congressional SLP telehealth authority clocks for 2026",
        "caption": "A billable code does not extend statutory authority by itself.",
        "bullets": ["Code list clock", "Authority clock (CAA 2026)", "2027 extension on books", "2028 FAQ horizon"],
        "kind": "timeline",
    },
    {
        "slug": "congress-extends-medicare-telehealth-slps-through-2027-caa-2026",
        "beat": "Medicare / CMS / ASHA",
        "file": "telehealth-extension-2027",
        "title": "Congressional telehealth extension through 2027",
        "desc": "Legislative timeline card for Consolidated Appropriations Act 2026 SLP telehealth authority through 31 December 2027.",
        "alt": "Timeline schematic showing congressional extension of Medicare SLP telehealth authority through December 31 2027",
        "caption": "The extension is dated law, not a permanent telehealth mandate.",
        "bullets": ["CAA 2026 language", "Ends 31 Dec 2027", "Pair with CMS FAQ", "State licensure still applies"],
        "kind": "timeline",
    },
    {
        "slug": "medicare-2026-kx-threshold-pt-slp-2480",
        "beat": "Medicare / CMS / ASHA",
        "file": "kx-threshold-2480-card",
        "title": "2026 KX threshold for PT plus SLP",
        "desc": "Threshold card showing $2,480 combined therapy cap indicator for documentation modifiers.",
        "alt": "News card schematic stating Medicare 2026 KX modifier threshold of 2480 dollars for combined physical therapy and speech therapy services",
        "caption": "The threshold is a documentation trigger, not a hard benefit stop.",
        "bullets": ["$2,480 combined PT+SLP", "KX modifier rules", "Verify MAC guidance", "Not a caseload limit"],
        "kind": "card",
    },
    {
        "slug": "cms-telehealth-faq-2028-slps-pts-ots-audiologists",
        "beat": "Medicare / CMS / ASHA",
        "file": "cms-2028-telehealth-faq-bridge",
        "title": "CMS 2028 telehealth FAQ horizon",
        "desc": "Bridge schematic from 2027 authority end to CMS-published 2028 telehealth FAQ expectations for therapy disciplines.",
        "alt": "Bridge timeline from 2027 telehealth authority sunset to CMS 2028 telehealth FAQ guidance for speech pathology and related therapy",
        "caption": "CMS has described a 2028 posture; Congress can move the authority date.",
        "bullets": ["Authority may end 2028", "CMS FAQ is planning doc", "Watch congressional fixes", "Do not assume permanence"],
        "kind": "timeline",
    },
    {
        "slug": "medicare-mppr-therapy-50-percent-2026",
        "beat": "Medicare / CMS / ASHA",
        "file": "mppr-50-percent-card",
        "title": "Medicare therapy MPPR still at 50 percent",
        "desc": "Payment reduction card noting multiple procedure payment reduction remains on outpatient therapy for 2026.",
        "alt": "Schematic card noting Medicare fifty percent multiple procedure payment reduction still applies to therapy services in 2026",
        "caption": "MPPR is a payment mechanics issue, not a scope-of-practice change.",
        "bullets": ["50% MPPR continues", "Affects second+ procedures", "Facility vs non-facility", "MAC implements"],
        "kind": "card",
    },
    {
        "slug": "cms-2026-practice-expense-rebalancing-slps",
        "beat": "Medicare / CMS / ASHA",
        "file": "practice-expense-rebalance",
        "title": "2026 practice expense rebalancing schematic",
        "desc": "Split bar showing CMS raising non-facility practice expense while cutting facility PE—effect on SLP codes varies.",
        "alt": "Split bar schematic of CMS 2026 practice expense increases for non-facility settings and decreases for facility settings affecting therapy codes unevenly",
        "caption": "Rebalancing moves relative value; it is not an automatic raise for every SLP.",
        "bullets": ["Non-facility PE up", "Facility PE down", "Code-level impact differs", "Read ASHA summary tables"],
        "kind": "bars",
    },
    {
        "slug": "92507-exempt-cms-2026-efficiency-adjustment",
        "beat": "Medicare / CMS / ASHA",
        "file": "cpt-92507-exempt-badge",
        "title": "CPT 92507 efficiency adjustment exemption",
        "desc": "Code badge schematic marking 92507 exempt from 2026 Medicare efficiency adjustment with caveat that exemption is not a raise.",
        "alt": "Code badge schematic showing CPT 92507 exempt from CMS 2026 efficiency adjustment with note that exemption is not a payment increase",
        "caption": "Exempt from the cut ≠ automatic upward revision.",
        "bullets": ["92507 named exempt", "Other codes may adjust", "Check fee schedule PDF", "MAC adjudicates claims"],
        "kind": "card",
    },
    {
        "slug": "cms-2026-remote-therapeutic-monitoring-sometimes-therapy-codes",
        "beat": "Medicare / CMS / ASHA",
        "file": "rtm-sometimes-therapy-codes",
        "title": "2026 remote therapeutic monitoring code family",
        "desc": "Code family card for three RTM codes CMS classified as sometimes therapy for 2026 policy.",
        "alt": "Schematic listing three CMS 2026 remote therapeutic monitoring codes classified as sometimes therapy for billing policy",
        "caption": "RTM is a monitoring lane; clinical judgment and MAC rules still govern.",
        "bullets": ["Three RTM codes added", "Sometimes therapy label", "Not a speech-only default", "Pair with documentation"],
        "kind": "card",
    },
    {
        "slug": "medicare-2026-originating-site-facility-fee-q3014",
        "beat": "Medicare / CMS / ASHA",
        "file": "originating-site-fee-3185",
        "title": "2026 originating-site facility fee Q3014",
        "desc": "Fee line card for $31.85 originating site facility fee before coinsurance in 2026.",
        "alt": "Fee line schematic for Medicare 2026 originating site facility fee thirty-one dollars eighty-five cents before coinsurance for code Q3014",
        "caption": "Facility fee is one line on the telehealth stack, not the therapy payment.",
        "bullets": ["Q3014 facility fee", "$31.85 before coinsurance", "Distinct from therapy CF", "Verify site eligibility"],
        "kind": "card",
    },
    {
        "slug": "most-slps-exempt-mips-2026-two-conversion-factors",
        "beat": "Medicare / CMS / ASHA",
        "file": "mips-exempt-majority-card",
        "title": "Most SLPs outside mandatory MIPS",
        "desc": "Venn-style schematic showing majority of SLPs exempt from MIPS while still affected by dual conversion-factor politics.",
        "alt": "Schematic showing most speech-language pathologists exempt from mandatory MIPS in 2026 while affected by two Medicare conversion factors",
        "caption": "Exempt from MIPS is not exempt from Medicare fee-schedule fights.",
        "bullets": ["Majority not in MIPS", "Two CF tracks remain", "Voluntary reporting possible", "ASHA tracks policy"],
        "kind": "compare",
    },
    {
        "slug": "how-to-read-asha-public-2026-slp-medicare-fee-schedule",
        "beat": "Medicare / CMS / ASHA",
        "file": "asha-fee-schedule-anatomy",
        "title": "How to read ASHA’s public fee-schedule PDF",
        "desc": "Annotated document card labeling illustrative columns versus MAC-specific billing instructions.",
        "alt": "Annotated schematic of ASHA public Medicare fee schedule PDF zones: illustrative rates, code list, and reminders that MAC letters govern billing",
        "caption": "ASHA’s PDF is a reader’s guide, not a contractor determination letter.",
        "bullets": ["Illustrative vs binding", "Code & RVU columns", "Cross-check CMS file", "MAC owns claims"],
        "kind": "card",
    },
    {
        "slug": "michigan-screens-fill-school-speech-gaps",
        "beat": "Licensure / school workforce",
        "file": "michigan-screen-hire-card",
        "title": "Michigan districts hiring on screens",
        "desc": "Workforce card on districts filling vacancies with screen-based hires while state counts remain uncertain.",
        "alt": "Workforce schematic: Michigan school districts filling speech-language pathology vacancies using screen-based hires with uncertain state vacancy counts",
        "caption": "Local hiring stories can outrun published vacancy statistics.",
        "bullets": ["District-level screens", "State count unclear", "Credential rules apply", "Verify MDE guidance"],
        "kind": "card",
    },
    {
        "slug": "baltimore-county-unsustainable-slp-caseloads",
        "beat": "Licensure / school workforce",
        "file": "baltimore-caseload-signal",
        "title": "Baltimore County caseload sustainability signal",
        "desc": "Bar schematic comparing reported caseload stress against staffing FTE reality in public radio coverage.",
        "alt": "Bar schematic of Baltimore County school speech-language pathologists reporting unsustainable caseloads in WYPR coverage May 2025",
        "caption": "Reporter testimony is a signal; official ratios may lag.",
        "bullets": ["WYPR May 2025 story", "Caseload vs workload", "Union / board context", "Not a national statistic"],
        "kind": "bars",
    },
    {
        "slug": "florida-hb-471-slp-recruitment-plan",
        "beat": "Licensure / school workforce",
        "file": "florida-hb471-bill-track",
        "title": "Florida HB 471 recruitment plan track",
        "desc": "Bill-track card: filed legislation would direct DOE to write statewide SLP staffing plan—not yet law.",
        "alt": "Bill track schematic for Florida HB 471 requiring Department of Education statewide speech-language pathology staffing plan still not enacted law",
        "caption": "Filed is not enrolled; check Florida legislature status before citing.",
        "bullets": ["HB 471 filed", "DOE staffing plan", "Not law in this draft", "Pair with district data"],
        "kind": "timeline",
    },
    {
        "slug": "asha-2024-schools-survey-paperwork-workforce",
        "beat": "Licensure / school workforce",
        "file": "asha-schools-survey-paperwork-first",
        "title": "ASHA 2024 schools survey: paperwork first",
        "desc": "Ranked bar schematic placing paperwork at top complaint across school facility types in ASHA survey.",
        "alt": "Ranked bar schematic from ASHA 2024 schools survey showing paperwork as top complaint across school facility types",
        "caption": "Survey ranks complaints; it does not prescribe a caseload cap.",
        "bullets": ["Paperwork #1 everywhere", "2024 schools wave", "Self-reported sample", "Workload ≠ caseload count"],
        "kind": "bars",
    },
    {
        "slug": "utah-hb-374-dopl-takes-the-slp-license",
        "beat": "Licensure / school workforce",
        "file": "utah-dopl-transfer-timeline",
        "title": "Utah HB 374 DOPL license transfer",
        "desc": "Timeline for school SLP license moving to DOPL effective 6 May 2026.",
        "alt": "Timeline schematic Utah enrolled HB 374 moving school speech-language pathology license to DOPL effective May 6 2026",
        "caption": "A board move changes who answers renewal questions.",
        "bullets": ["HB 374 enrolled", "DOPL takes license", "Effective 6 May 2026", "School cert may differ"],
        "kind": "timeline",
    },
    {
        "slug": "two-licenses-health-board-and-school-credential",
        "beat": "Licensure / school workforce",
        "file": "health-board-school-cert-dual",
        "title": "Health board license plus school credential",
        "desc": "Dual-license schematic for clinicians holding both LLR health license and educator certificate.",
        "alt": "Dual credential schematic showing separate health board speech-language pathology license and school educator certificate requirements",
        "caption": "States can require two parallel credentials for the same person.",
        "bullets": ["Health board license", "Educator certificate", "Renewal cycles differ", "Compact ≠ school cert"],
        "kind": "compare",
    },
    {
        "slug": "bls-projects-15-percent-slp-job-growth",
        "beat": "Licensure / school workforce",
        "file": "bls-growth-projection-card",
        "title": "BLS 15 percent SLP growth projection",
        "desc": "Projection card distinguishing BLS demand forecast from funded school FTE lines.",
        "alt": "Projection card schematic BLS fifteen percent speech-language pathology job growth 2024 to 2034 as demand not funded FTE",
        "caption": "Growth projections describe labor market pressure, not a district budget line.",
        "bullets": ["15% 2024–34 projection", "National estimate", "School FTE separate", "Vacancy data local"],
        "kind": "card",
    },
    {
        "slug": "south-carolina-slp-educator-certificate-renewal",
        "beat": "Licensure / school workforce",
        "file": "sc-educator-cert-renewal",
        "title": "South Carolina educator certificate renewal gate",
        "desc": "Renewal card tying educator certificate to current LLR speech license.",
        "alt": "Renewal schematic South Carolina speech-language pathology educator certificate requires current LLR license",
        "caption": "Renewal chains credentials; lapse in one can block the other.",
        "bullets": ["Educator cert renewal", "Current LLR license", "June 2026 rule cited", "Verify SC DOE"],
        "kind": "card",
    },
    {
        "slug": "new-york-slp-title-protection-school-exemption",
        "beat": "Licensure / school workforce",
        "file": "ny-title-protection-exemption",
        "title": "New York SLP title protection with school exemption",
        "desc": "Title-protection schematic noting licensed title rules and listed school-setting exemptions.",
        "alt": "Schematic of New York speech-language pathology title protection with noted exemptions for certain school settings",
        "caption": "Title law and school employment exemptions can coexist.",
        "bullets": ["Title protected", "School exemptions exist", "Read Education Law", "Not clinical advice"],
        "kind": "compare",
    },
    {
        "slug": "rhode-island-even-year-slp-license-renewal",
        "beat": "Licensure / school workforce",
        "file": "ri-even-year-renewal",
        "title": "Rhode Island even-year license cycle",
        "desc": "Calendar card for July 1 expirations in even years plus separate school certificate.",
        "alt": "Calendar schematic Rhode Island speech-language pathology licenses expiring July first in even years with separate school certificate",
        "caption": "Even-year rhythm is administrative, not clinical.",
        "bullets": ["Expires July 1", "Even-numbered years", "School cert separate", "DOH verifies dates"],
        "kind": "timeline",
    },
    {
        "slug": "light-aac-societal-barriers-research-agenda",
        "beat": "Research",
        "file": "aac-societal-barriers-agenda",
        "title": "AAC research agenda: societal barriers first",
        "desc": "Research flow placing societal barriers ahead of device feature lists in a new AAC agenda paper.",
        "alt": "Research flow schematic placing societal barriers before device features in AAC research agenda",
        "caption": "Access barriers sit outside the handset.",
        "bullets": ["Society before device", "Participation framing", "Not a product review", "Read primary paper"],
        "kind": "flow",
    },
    {
        "slug": "jmir-free-aac-elearning-inventory",
        "beat": "Research",
        "file": "aac-elearning-inventory-131",
        "title": "Free AAC e-learning inventory (131 tools)",
        "desc": "Inventory card citing 131 free AAC e-learning tools counted without quality ranking.",
        "alt": "Inventory card schematic listing one hundred thirty-one free AAC e-learning tools counted in JMIR inventory without quality ranking",
        "caption": "An inventory counts tools; it does not certify them.",
        "bullets": ["131 free tools listed", "No ranking in paper", "Verify accessibility", "Institutional login may apply"],
        "kind": "card",
    },
    {
        "slug": "babb-caron-all-app-literacy-ajslp",
        "beat": "Research",
        "file": "babb-caron-case-series-flow",
        "title": "Babb and Caron parent-delivered literacy app study",
        "desc": "Small-n case-series flow for four children and parent-delivered app literacy training limits.",
        "alt": "Case series flow schematic four children parent-delivered literacy app study with limits on generalization noted",
        "caption": "Small n studies illustrate mechanism; they do not set universal protocol.",
        "bullets": ["n=4 case series", "Parent-delivered app", "Trained items moved", "Generalization limited"],
        "kind": "flow",
    },
    {
        "slug": "light-aac-literacy-barriers-companion",
        "beat": "Research",
        "file": "aac-literacy-barriers-outside-learner",
        "title": "AAC literacy barriers outside the learner",
        "desc": "Barrier wheel schematic placing literacy obstacles in environment, policy, and instruction—not cognition alone.",
        "alt": "Barrier wheel schematic placing AAC literacy obstacles in environment policy and instruction outside the learner",
        "caption": "Barrier location guides intervention design, not blame.",
        "bullets": ["Environment & policy", "Instructional access", "Not device-only fix", "Companion to agenda paper"],
        "kind": "flow",
    },
    {
        "slug": "lvppa-teletherapy-phonological-memory",
        "beat": "Research",
        "file": "lvppa-teletherapy-transfer",
        "title": "lvPPA teletherapy phonological training transfer",
        "desc": "Outcomes schematic: trained phonological items improved with thin broader transfer in lvPPA teletherapy trial.",
        "alt": "Outcomes schematic lvPPA teletherapy phonological training improved trained items with limited transfer to untrained tasks",
        "caption": "Item-specific gains are not automatic discourse recovery.",
        "bullets": ["Trained items improved", "Transfer thin", "Teletherapy delivery", "Primary dementia syndrome"],
        "kind": "flow",
    },
    {
        "slug": "cerebellar-tdcs-cantonese-aphasia",
        "beat": "Research",
        "file": "tdcs-sham-naming-outcomes",
        "title": "Cerebellar tDCS versus sham naming outcomes",
        "desc": "Trial schematic: tDCS did not beat sham for Cantonese naming while computerized therapy moved verbs.",
        "alt": "Trial schematic cerebellar tDCS did not outperform sham for Cantonese naming though computerized therapy improved verbs",
        "caption": "Null stimulation result still leaves therapy signal to interpret cautiously.",
        "bullets": ["tDCS ≈ sham naming", "Verb training moved", "Cantonese cohort", "Adjunct research only"],
        "kind": "flow",
    },
    {
        "slug": "fnirs-guided-rtms-naming-subacute-aphasia",
        "beat": "Research",
        "file": "fnirs-rtms-adjunct-trial",
        "title": "fNIRS-guided rTMS naming adjunct trial",
        "desc": "Adjunct trial schematic for Chinese naming gains with explicit not-standard-of-care labeling.",
        "alt": "Adjunct trial schematic fNIRS guided rTMS improved Chinese naming in subacute aphasia labeled not standard of care",
        "caption": "Adjunct neuromodulation trials stay outside routine practice until replicated.",
        "bullets": ["fNIRS-guided rTMS", "Naming gains reported", "Subacute aphasia", "Not standard of care"],
        "kind": "flow",
    },
    {
        "slug": "caseload-is-the-wrong-metric",
        "beat": "Practice trends",
        "file": "caseload-vs-workload-split",
        "title": "Caseload count versus workload",
        "desc": "Split card contrasting countable caseload numbers with documentation, meetings, and travel workload.",
        "alt": "Split schematic contrasting countable school caseload numbers with documentation meetings and travel workload components",
        "caption": "Districts count heads; clinicians live the hours.",
        "bullets": ["Caseload = countable", "Workload = hours", "Paperwork in workload", "Advocacy needs both terms"],
        "kind": "compare",
    },
    {
        "slug": "paperwork-is-the-first-complaint",
        "beat": "Practice trends",
        "file": "paperwork-first-complaint",
        "title": "Paperwork as first complaint",
        "desc": "Rank card echoing ASHA schools survey: paperwork leads complaints in every setting asked.",
        "alt": "Rank card schematic paperwork listed first complaint in every school facility type in ASHA schools survey",
        "caption": "Complaint rank is not a mandate; it is a staffing conversation starter.",
        "bullets": ["#1 in every setting", "Survey self-report", "Pairs with workload", "Not legal advice"],
        "kind": "bars",
    },
    {
        "slug": "aac-access-when-the-slp-is-remote",
        "beat": "Practice trends",
        "file": "remote-slp-aac-access-gap",
        "title": "AAC access when the SLP is remote",
        "desc": "Gap schematic: AAC hardware and support does not automatically follow telepractice sessions.",
        "alt": "Gap schematic showing AAC device access and support does not automatically follow remote speech-language pathology services",
        "caption": "Telepractice opens the session; access still needs local logistics.",
        "bullets": ["Device stays on site", "Caregiver training", "Funding separate", "Document access plan"],
        "kind": "flow",
    },
    {
        "slug": "document-the-client-location",
        "beat": "Practice trends",
        "file": "client-location-documentation",
        "title": "Document the client location",
        "desc": "Charting card linking compact geography and Medicare telehealth to a single documentation field.",
        "alt": "Charting card schematic urging documented client location for ASLP-IC compact practice rules and Medicare telehealth",
        "caption": "One documentation habit serves two unrelated regulatory masters.",
        "bullets": ["Client address on chart", "Compact geography", "Medicare telehealth site", "No shared government form"],
        "kind": "card",
    },
    {
        "slug": "slpa-supervision-in-a-shortage",
        "beat": "Practice trends",
        "file": "slpa-supervision-twelve-percent",
        "title": "SLPA supervision in a shortage",
        "desc": "Statistic card: twelve percent of school SLPs supervised an SLPA—smaller than shortage magnitude.",
        "alt": "Statistic card schematic twelve percent of school speech-language pathologists supervised a speech-language pathology assistant amid larger shortage",
        "caption": "Supervision rates describe capacity, not permission to skip rules.",
        "bullets": ["12% supervised SLPA", "Shortage larger", "State rules govern", "Scope unchanged"],
        "kind": "card",
    },
    {
        "slug": "continuity-when-a-family-moves",
        "beat": "Practice trends",
        "file": "continuity-four-state-reality",
        "title": "Continuity benefit versus four-state issuance",
        "desc": "Bridge schematic juxtaposing compact continuity messaging with four issuing states as of September 2026.",
        "alt": "Bridge schematic compact continuity of care benefit juxtaposed with only four states issuing privileges September 2026",
        "caption": "Continuity is a design promise; privileges still require issuance.",
        "bullets": ["Continuity on benefits list", "4 states issuing", "Plan before move", "School + health gates"],
        "kind": "bridge",
    },
]


def _esc(s: str) -> str:
    return html.escape(s, quote=False)


def _theme(beat: str) -> str:
    return BEAT_THEME.get(beat, "slate")


def _svg_styles(theme: str) -> str:
    band, accent = PALETTE[theme]
    return f"""
.bg {{ fill: {PALETTE['paper']}; }}
.title {{ font-family: Georgia, serif; font-size: 16px; font-weight: 600; fill: #1E293B; }}
.dek {{ font-family: system-ui, sans-serif; font-size: 11px; fill: #64748B; }}
.label {{ font-family: system-ui, sans-serif; font-size: 11px; fill: #64748B; }}
.strong {{ font-family: system-ui, sans-serif; font-size: 12px; font-weight: 600; fill: #1E293B; }}
.card {{ fill: {PALETTE['card']}; stroke: {PALETTE['rule']}; stroke-width: 1; }}
.band {{ fill: {band}; }}
.accent {{ fill: {accent}; }}
.bullet {{ font-family: system-ui, sans-serif; font-size: 11px; fill: #1E293B; }}
.note {{ font-family: system-ui, sans-serif; font-size: 10px; fill: #64748B; }}
.spine {{ stroke: {accent}; stroke-width: 2; fill: none; }}
.node {{ fill: {accent}; }}
"""


def _body_default(bullets: list[str]) -> list[str]:
    lines: list[str] = []
    y0 = 148
    for i, b in enumerate(bullets[:4]):
        y = y0 + i * 28
        lines.append(f'  <circle cx="68" cy="{y - 4}" r="3" class="accent"/>')
        lines.append(f'  <text x="82" y="{y}" class="bullet">{_esc(b)}</text>')
    return lines


def _body_timeline(bullets: list[str]) -> list[str]:
    lines = [
        '  <line class="spine" x1="80" y1="200" x2="800" y2="200"/>',
    ]
    xs = [120, 280, 440, 600]
    for i, (x, b) in enumerate(zip(xs, bullets[:4])):
        lines.append(f'  <circle class="node" cx="{x}" cy="200" r="7"/>')
        lines.append(f'  <text x="{x}" y="178" text-anchor="middle" class="strong">{i + 1}</text>')
        wrapped = textwrap.wrap(b, width=22)[:2]
        for j, row in enumerate(wrapped):
            lines.append(
                f'  <text x="{x}" y="{228 + j * 14}" text-anchor="middle" class="label">{_esc(row)}</text>'
            )
    return lines


def _body_compare(bullets: list[str]) -> list[str]:
    left, right = bullets[:2], bullets[2:4]
    lines = [
        '  <rect class="band" x="56" y="140" width="370" height="200" rx="6"/>',
        '  <rect class="band" x="454" y="140" width="370" height="200" rx="6"/>',
        '  <text x="72" y="164" class="strong">Column A</text>',
        '  <text x="470" y="164" class="strong">Column B</text>',
    ]
    for i, b in enumerate(left):
        lines.append(f'  <text x="72" y="{188 + i * 22}" class="bullet">• {_esc(b)}</text>')
    for i, b in enumerate(right):
        lines.append(f'  <text x="470" y="{188 + i * 22}" class="bullet">• {_esc(b)}</text>')
    return lines


def _body_buckets(bullets: list[str]) -> list[str]:
    lines = []
    xs = [56, 232, 408, 584]
    for x, b in zip(xs, bullets[:4]):
        lines.append(f'  <rect class="band" x="{x}" y="150" width="168" height="170" rx="6"/>')
        wrapped = textwrap.wrap(b, width=18)[:3]
        for j, row in enumerate(wrapped):
            lines.append(f'  <text x="{x + 10}" y="{178 + j * 16}" class="label">{_esc(row)}</text>')
    return lines


def _body_bars(bullets: list[str]) -> list[str]:
    lines = []
    widths = [520, 420, 360, 300]
    for i, (b, w) in enumerate(zip(bullets[:4], widths)):
        y = 150 + i * 42
        lines.append(f'  <rect class="band" x="56" y="{y}" width="{w}" height="28" rx="4"/>')
        lines.append(f'  <text x="68" y="{y + 18}" class="bullet">{_esc(b)}</text>')
    return lines


def _body_flow(bullets: list[str]) -> list[str]:
    lines = []
    xs = [100, 300, 500, 700]
    for i, (x, b) in enumerate(zip(xs, bullets[:4])):
        if i:
            lines.append(f'  <line class="spine" x1="{xs[i-1]+40}" y1="210" x2="{x-40}" y2="210"/>')
        lines.append(f'  <rect class="band" x="{x - 70}" y="170" width="140" height="80" rx="6"/>')
        wrapped = textwrap.wrap(b, width=16)[:2]
        for j, row in enumerate(wrapped):
            lines.append(
                f'  <text x="{x}" y="{200 + j * 14}" text-anchor="middle" class="label">{_esc(row)}</text>'
            )
    return lines


BODY_BY_KIND = {
    "timeline": _body_timeline,
    "compare": _body_compare,
    "buckets": _body_buckets,
    "bars": _body_bars,
    "flow": _body_flow,
    "bridge": _body_compare,
    "map": _body_buckets,
    "stack": _body_compare,
    "card": _body_default,
}


def _svg_wrap(
    title: str,
    desc: str,
    headline: str,
    subline: str,
    bullets: list[str],
    beat: str,
    kind: str = "card",
    foot: str = "SLPWOW SLP News — original editorial SVG. No photographs or AI faces.",
) -> str:
    theme = _theme(beat)
    body_fn = BODY_BY_KIND.get(kind, _body_default)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 420" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{_esc(title)}</title>',
        f'  <desc id="desc">{_esc(desc)}</desc>',
        "  <defs><style>",
        _svg_styles(theme),
        "  </style></defs>",
        '  <rect class="bg" width="880" height="420"/>',
        f'  <text x="40" y="36" class="title">{_esc(headline)}</text>',
        f'  <text x="40" y="56" class="dek">{_esc(subline)}</text>',
        '  <rect class="card" x="40" y="76" width="800" height="300" rx="8"/>',
        '  <rect class="band" x="56" y="92" width="768" height="36" rx="4"/>',
        '  <rect class="accent" x="56" y="92" width="6" height="36" rx="2"/>',
        f'  <text x="72" y="116" class="strong">{_esc(beat)}</text>',
    ]
    lines.extend(body_fn(bullets))
    lines.append(f'  <text x="40" y="396" class="note">{_esc(foot)}</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def write_svg(spec: dict) -> Path:
    slug = spec["slug"]
    out_dir = ASSETS / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{spec['file']}.svg"
    subline = spec["desc"][:120] + ("…" if len(spec["desc"]) > 120 else "")
    path.write_text(
        _svg_wrap(
            spec["title"],
            spec["desc"],
            spec["title"],
            subline,
            spec["bullets"],
            spec["beat"],
            spec.get("kind", "card"),
        ),
        encoding="utf-8",
    )
    return path


def write_embed(spec: dict) -> Path:
    EMBEDS.mkdir(parents=True, exist_ok=True)
    slug = spec["slug"]
    path = EMBEDS / f"{slug}.md"
    alt = spec["alt"]
    cap = spec["caption"]
    body = textwrap.dedent(
        f"""# Embed — {slug}

```html
<figure class="slpwow-figure slpwow-figure--infographic" itemscope itemtype="https://schema.org/ImageObject">
  <img
    src="../assets/{slug}/{spec['file']}.svg"
    alt="{alt}"
    width="880"
    height="420"
    loading="lazy"
    itemprop="contentUrl"
  />
  <figcaption itemprop="caption">
    <strong>Figure 1.</strong> {cap}
    <span class="figure-credit">SLPWOW SLP News — original editorial SVG. Not legal, billing, or clinical advice.</span>
  </figcaption>
</figure>
```
"""
    )
    path.write_text(body, encoding="utf-8")
    return path


def figure_html(spec: dict) -> str:
    slug = spec["slug"]
    alt = spec["alt"]
    cap = spec["caption"]
    return textwrap.dedent(
        f"""
<figure class="slpwow-figure slpwow-figure--infographic" itemscope itemtype="https://schema.org/ImageObject">
  <img
    src="../assets/{slug}/{spec['file']}.svg"
    alt="{alt}"
    width="880"
    height="420"
    loading="lazy"
    itemprop="contentUrl"
  />
  <figcaption itemprop="caption">
    <strong>Figure 1.</strong> {cap}
    <span class="figure-credit">SLPWOW SLP News — original editorial SVG. Not legal, billing, or clinical advice.</span>
  </figcaption>
</figure>
"""
    ).strip()


def patch_articles() -> list[str]:
    missing: list[str] = []
    slug_to_spec = {g["slug"]: g for g in GRAPHICS}
    for path in sorted(ART.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r'^slug:\s*"?([^"\n]+)"?\s*$', text, re.M)
        if not m:
            missing.append(f"{path.name}: no slug")
            continue
        slug = m.group(1).strip()
        spec = slug_to_spec.get(slug)
        if not spec:
            missing.append(f"{path.name}: no graphic spec for {slug}")
            continue
        if "<figure" in text:
            continue
        fig = figure_html(spec)
        # Insert after first ## section heading line
        sec = re.search(r"(^## .+\n)", text, re.M)
        if not sec:
            missing.append(f"{path.name}: no ## section")
            continue
        insert_at = sec.end()
        text = text[:insert_at] + "\n" + fig + "\n\n" + text[insert_at:]
        path.write_text(text, encoding="utf-8")
    return missing


def write_rights() -> None:
    lines = [
        "# Rights — SLPWOW SLP News (stage 46 pack)",
        "",
        "Original editorial SVG schematics for draft articles in `articles/`. **No photographs, no AI-generated faces, no child likenesses.**",
        "",
        "| Asset path | Creator / rightsholder | License (this repo) | Credit (publish) | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for spec in GRAPHICS:
        rel = f"assets/{spec['slug']}/{spec['file']}.svg"
        lines.append(
            f"| `{rel}` | SLPWOW editorial | Practice may publish on slpwow.com | "
            f"“SLPWOW SLP News — original schematic” | {spec['caption'][:80]}… |"
        )
    lines.extend(
        [
            "",
            "## Optional public-domain or Creative Commons rasters",
            "",
            "This wave ships **SVG only**. If editors later embed government maps or Wikimedia charts:",
            "",
            "| Source type | Example | Typical license | Rule |",
            "| --- | --- | --- | --- |",
            "| U.S. federal works | CMS, ASHA public PDF figures (cropped) | Often PD-USGov | Log URL + access date in `BIBLIOGRAPHY.md`; prefer linking out over raster embed. |",
            "| Wikimedia Commons | Historical SLP portraits | Varies (often PD-old) | Add a row here **before** embed; no AI colorization. |",
            "| Wellcome / LOC | Period engravings (equipment only) | Often CC BY 4.0 | Crop to objects; **no identifiable patients or children**. |",
            "",
            "## Excluded",
            "",
            "- AI-generated faces or “stock clinician” renders.",
            "- Patient photography, classroom photos, or any image with identifiable minors.",
            "- CompactConnect, CMS, or state board **logos** embedded as if endorsed — use text labels in schematics instead.",
            "",
        ]
    )
    RIGHTS.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    for spec in GRAPHICS:
        write_svg(spec)
        write_embed(spec)
    write_rights()
    gaps = patch_articles()
    if gaps:
        print("PATCH GAPS:", *gaps, sep="\n")
        return 1
    print(f"OK: {len(GRAPHICS)} graphics, articles patched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
