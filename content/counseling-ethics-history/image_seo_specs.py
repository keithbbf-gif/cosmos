"""Timeline and portrait specs for counseling-ethics-history graphics_pass.

Each slug maps to (title, events, caption, highlight_index).
highlight_index marks the focal tick on the code-lineage SVG (0-based).
"""
from __future__ import annotations

# slug -> (title, [(year, label), ...], seo_caption, highlight_index)
TIMELINE_SPECS: dict[str, tuple[str, list[tuple[str, str]], str, int]] = {
    "what-this-folder-refuses": (
        "What this pack will not publish",
        [
            ("1953", "APA first code"),
            ("1960", "NASW one page"),
            ("1961", "APGA five pages"),
            ("2026", "Draft ≠ code"),
        ],
        "Three professions' ethics documents on a calendar — heritage education, not a complaint desk.",
        3,
    ),
    "how-to-read-a-code-as-history": (
        "Reading a code as history",
        [
            ("draft", "Committee text"),
            ("vote", "Council / assembly"),
            ("adopt", "Association act"),
            ("effective", "Membership clock"),
        ],
        "Adoption, effective date, and amendment as separate historical events — not one blur.",
        2,
    ),
    "three-professions-three-codes": (
        "Three codes, three printers",
        [
            ("1953", "APA Ethics Code"),
            ("1960", "NASW page"),
            ("1961", "APGA pamphlet"),
            ("2002+", "Parallel revisions"),
        ],
        "Psychology, social work, and counseling associations printed separate public ethics books.",
        0,
    ),
    "public-text-is-not-a-trial": (
        "Three rooms for ethics language",
        [
            ("guild", "Association code"),
            ("board", "Licensure statute"),
            ("court", "Case law"),
        ],
        "Association ethics, licensing boards, and courts are related but not interchangeable rooms.",
        0,
    ),
    "sister-packs-different-job": (
        "Sister packs on wowtherapies.com",
        [
            ("ethics", "This folder"),
            ("heritage", "Therapy history"),
            ("speech", "SLPWOW lane"),
        ],
        "Ethics documents here; schools and figures elsewhere — do not merge the calendars.",
        0,
    ),
    "oaths-older-than-associations": (
        "Oaths before association codes",
        [
            ("antiquity", "Hippocratic reception"),
            ("1915", "Flexner report"),
            ("1953", "APA printed code"),
        ],
        "Professional oaths and guild codes long predate APA's 1953 book.",
        0,
    ),
    "nuremberg-helsinki-belmont": (
        "Research ethics leaking into practice",
        [
            ("1947", "Nuremberg Code"),
            ("1964", "Helsinki"),
            ("1979", "Belmont Report"),
            ("1980s+", "Practice codes cite research"),
        ],
        "Research-ethics documents that later shaped counseling and psychology practice language.",
        2,
    ),
    "flexner-richmond-casework": (
        "Social work before NASW's page",
        [
            ("1915", "Flexner"),
            ("1917", "Richmond"),
            ("1929", "AASW code"),
            ("1960", "NASW adopts"),
        ],
        "Casework arguments and early social-work codes before NASW's 1960 one-pager.",
        1,
    ),
    "vocational-guidance-before-a-page": (
        "Guidance before APGA's pamphlet",
        [
            ("1908", "Parsons Boston"),
            ("1913", "NVGA forms"),
            ("1952", "APGA merger"),
            ("1961", "Five pages"),
        ],
        "Vocational guidance as a craft before counseling's first short ethics pamphlet.",
        0,
    ),
    "1938-apa-committee-without-a-book": (
        "APA's unwritten 1938 committee",
        [
            ("1938", "Informal committee"),
            ("1947", "Tolman formal"),
            ("1953", "Printed code"),
        ],
        "An ethics committee without a book — informal complaints before Hobbs's incidents.",
        0,
    ),
    "a-code-is-not-a-conscience": (
        "Codes list fights; they do not sit in the grocery store",
        [
            ("committee", "Drafts & votes"),
            ("member", "Reads & argues"),
            ("clinic", "Daily judgment"),
        ],
        "Association text versus the judgment a clinician carries between sessions.",
        2,
    ),
    "1947-tolman-committee": (
        "APA ethics lineage — Tolman chair",
        [
            ("1938", "Informal committee"),
            ("1947", "Tolman committee"),
            ("1953", "Ethical Standards"),
            ("2002", "Current spine"),
        ],
        "Edward C. Tolman's 1947 chairmanship as the opening move in APA's printed ethics lineage.",
        1,
    ),
    "hobbs-critical-incidents-1953": (
        "APA ethics lineage — critical incidents",
        [
            ("1947", "Tolman opens"),
            ("1951", "Draft segments"),
            ("1953", "Ethical Standards"),
            ("1959", "Short code"),
        ],
        "Nicholas Hobbs, critical incidents, and the 1953 book members would call too long.",
        2,
    ),
    "short-codes-1959-1979": (
        "APA short-code decades",
        [
            ("1959", "First abridgment"),
            ("1968", "Revision"),
            ("1977", "Revision"),
            ("1979", "Last short book"),
        ],
        "Editing as history: APA's shorter ethics codes between 1959 and 1979.",
        0,
    ),
    "1981-and-the-law-sentence": (
        "APA 1981 — ethics versus law",
        [
            ("1979", "Short code"),
            ("1981", "Law conflicts named"),
            ("1992", "Principles split"),
            ("2002", "1.02 grandfather"),
        ],
        "The 1981 sentence that put conflicts between ethics and law on the page.",
        1,
    ),
    "1992-principles-you-cannot-be-expelled-for": (
        "APA 1992 — principles vs standards",
        [
            ("1981", "Enforceable book"),
            ("1992", "Principles added"),
            ("2002", "Fisher rewrite"),
            ("2010", "Amendments"),
        ],
        "Aspirational principles separated from enforceable standards in 1992.",
        1,
    ),
    "2002-fisher-june-2003": (
        "APA 2002 adoption / 2003 effective",
        [
            ("1992", "Prior book"),
            ("2002", "Council adopts"),
            ("2003", "Effective 1 June"),
            ("2010", "Post-PENS suture"),
        ],
        "Celia Fisher's task force book — adopted August 2002, effective June 2003.",
        2,
    ),
    "pens-2005-and-2010-amendments": (
        "PENS and the 2010 suture",
        [
            ("2002", "Ethics Code"),
            ("2005", "PENS report"),
            ("2010", "Standards 1.02–1.03"),
            ("2015", "Hoffman report"),
        ],
        "A 2005 policy report and later amendments to Standards 1.02 and 1.03.",
        2,
    ),
    "hoffman-2015-and-standard-304": (
        "Hoffman report and Standard 3.04",
        [
            ("2005", "PENS era"),
            ("2015", "Hoffman report"),
            ("2016", "Council vote"),
            ("2017", "3.04 effective"),
        ],
        "July 2015 Sidley Austin report, Council action, and 2017 Standard 3.04 suture.",
        1,
    ),
    "ectf-after-2018": (
        "APA revision after 2018",
        [
            ("2002", "Living code"),
            ("2018", "ECTF charged"),
            ("2020s", "Member comment"),
            ("2026", "No successor book"),
        ],
        "Ethics Code Task Force work — a charge document, not yet a printed successor code.",
        1,
    ),
    "four-associations-1952": (
        "ACA lineage — 1952 merger",
        [
            ("1952", "APGA forms"),
            ("1961", "Ethical Standards"),
            ("1992", "ACA name"),
            ("2014", "Current code"),
        ],
        "Four guidance associations building the body that would print counseling's ethics codes.",
        0,
    ),
    "1961-five-pages": (
        "ACA lineage — 1961 pamphlet",
        [
            ("1952", "APGA"),
            ("1961", "Five pages"),
            ("1974", "Revision"),
            ("2005", "Major rewrite"),
        ],
        "APGA's 1961 *Ethical Standards* as a short public bet before longer books.",
        1,
    ),
    "1974-1988-middle-revisions": (
        "ACA middle revisions",
        [
            ("1961", "First pamphlet"),
            ("1974", "Revision"),
            ("1981", "Revision"),
            ("1988", "Revision"),
        ],
        "Archive years between Tarasoff weather and the 1992 ACA rename.",
        1,
    ),
    "apga-aacd-aca-names": (
        "APGA → AACD → ACA names",
        [
            ("1952", "APGA"),
            ("1983", "AACD"),
            ("1992", "ACA (1 Jul)"),
            ("2014", "Code"),
        ],
        "Letterhead renames as ethics history — not cosmetic rebranding only.",
        2,
    ),
    "1995-code": (
        "ACA 1995 code",
        [
            ("1988", "Prior book"),
            ("1995", "Full code"),
            ("2005", "Rewrite"),
            ("2014", "Values fight"),
        ],
        "The last full ACA ethics book before the 2005 rewrite.",
        1,
    ),
    "2005-the-danger-sentence": (
        "ACA 2005 — danger language",
        [
            ("1995", "Prior code"),
            ("2005", "New code"),
            ("2014", "Section H"),
            ("2026", "Revision committee"),
        ],
        "Ten-part interview map and retiring 'clear and imminent danger' phrasing.",
        1,
    ),
    "2014-values-screens-five-years": (
        "ACA 2014 — values and screens",
        [
            ("2005", "Prior code"),
            ("2014", "Adopted code"),
            ("2014", "Section H tech"),
            ("2020s", "Revision"),
        ],
        "Task force, values-imposition arguments, and technology standards in 2014.",
        1,
    ),
    "2026-revision-still-in-committee": (
        "ACA revision calendar",
        [
            ("2014", "Living code"),
            ("2024", "Draft withdrawn"),
            ("2026", "Committee work"),
            ("fall", "Promised window"),
        ],
        "A withdrawn draft is not a code — committee tempo as of September 2026.",
        2,
    ),
    "1955-merger-1960-one-page": (
        "NASW lineage — 1960 one page",
        [
            ("1955", "NASW merger"),
            ("1960", "One-page code"),
            ("1967", "Revision"),
            ("1979", "82 principles"),
        ],
        "Thirteen October 1960: fourteen first-person proclamations on one page.",
        1,
    ),
    "1979-eighty-two-principles": (
        "NASW 1979 — eighty-two principles",
        [
            ("1960", "One page"),
            ("1979", "Task force book"),
            ("1980", "Effective 1 Jul"),
            ("1996", "Values rewrite"),
        ],
        "Levy's task force and six sections — effective 1 July 1980.",
        1,
    ),
    "1996-mission-and-six-values": (
        "NASW 1996 — six values",
        [
            ("1979", "82 principles"),
            ("1996", "Mission + values"),
            ("2008", "Nondiscrimination"),
            ("2021", "Limited suture"),
        ],
        "Service, social justice, dignity, relationships, integrity, competence — a 1996 distillation.",
        1,
    ),
    "2008-who-nondiscrimination-named": (
        "NASW 2008 nondiscrimination",
        [
            ("1996", "Values code"),
            ("2008", "Identity named"),
            ("2017", "Technology"),
            ("2021", "Self-care"),
        ],
        "Gender identity, sexual orientation, and immigration status named in 2008.",
        1,
    ),
    "2017-technology-as-an-ethics-object": (
        "NASW 2017 — technology",
        [
            ("2008", "Prior code"),
            ("2017", "Tech standards"),
            ("2020s", "Telehealth surge"),
            ("2021", "Amendments"),
        ],
        "Machines as an ethics object in NASW's revision cycle.",
        1,
    ),
    "2021-self-care-and-cultural-competence": (
        "NASW 2021 suture",
        [
            ("2017", "Tech code"),
            ("2021", "Adopted changes"),
            ("2021", "Effective 1 Jun"),
            ("2020s", "Delegate tempo"),
        ],
        "Limited 2021 amendments — self-care and cultural competence on the public record.",
        1,
    ),
    "delegate-assembly-as-a-machine": (
        "NASW Delegate Assembly tempo",
        [
            ("bylaws", "Assembly rules"),
            ("vote", "Floor action"),
            ("code", "Published text"),
            ("clinic", "Inherited stack"),
        ],
        "How NASW's assembly machinery turns proposals into a membership-facing code.",
        1,
    ),
    "confidentiality-privilege-tarasoff-jaffee": (
        "Confidentiality objects across rooms",
        [
            ("1969", "Tarasoff (CA)"),
            ("1996", "Jaffee (fed.)"),
            ("1996+", "HIPAA"),
            ("codes", "Three guilds"),
        ],
        "Privilege, duty-to-warn debates, and HIPAA as separate historical objects.",
        0,
    ),
    "multiple-relationships-and-year-counts": (
        "Multiple relationships in three codes",
        [
            ("APA", "Standard language"),
            ("ACA", "Counseling rules"),
            ("NASW", "Social work"),
            ("grocery", "The hard case"),
        ],
        "Two-year rules, five-year rules, and the colleague in the checkout line.",
        3,
    ),
    "competence-and-the-edge-of-the-license": (
        "Competence at the license edge",
        [
            ("degree", "Training gate"),
            ("license", "State board"),
            ("code", "Guild standard"),
            ("workshop", "Weekend CE"),
        ],
        "License, degree, association code, and the weekend workshop as competing claims.",
        1,
    ),
    "informed-consent-as-a-late-object": (
        "Informed consent arrives late",
        [
            ("research", "Nuremberg → Belmont"),
            ("1970s", "Practice forms"),
            ("codes", "Guild adoption"),
            ("courts", "Bitter cases"),
        ],
        "Research passport becomes practice form — a late object in ethics codes.",
        1,
    ),
    "distance-records-and-the-screen": (
        "Distance and records in codes",
        [
            ("1990s", "Fax era"),
            ("2014", "ACA Section H"),
            ("2017", "NASW tech"),
            ("2020s", "Telehealth"),
        ],
        "Dated inventories of machines — not a user manual for your EHR.",
        3,
    ),
    "conversion-practices-public-refusals": (
        "Public refusals in guild codes",
        [
            ("1970s", "Debate"),
            ("1990s", "Language hardens"),
            ("2010s", "State bans"),
            ("codes", "Name refusals"),
        ],
        "Name the refusals in public codes — do not teach the method.",
        3,
    ),
    "who-adjudicates-association-board-court": (
        "Who adjudicates what",
        [
            ("association", "Membership ethics"),
            ("board", "License"),
            ("court", "Civil/criminal"),
            ("blog", "None of the above"),
        ],
        "Association, board, and court — a blog post is not a fourth room.",
        0,
    ),
    "how-to-read-a-new-ethics-code-headline": (
        "Headline versus adoption calendar",
        [
            ("headline", "News cycle"),
            ("vote", "Official act"),
            ("effective", "Membership date"),
            ("book", "Printed text"),
        ],
        "Vote, adoption, effective date, and book versus suture — read the calendar.",
        2,
    ),
    "living-people-public-documents": (
        "Living people — public documents only",
        [
            ("book", "Published work"),
            ("lecture", "Named talk"),
            ("report", "Association PDF"),
            ("gossip", "Refused here"),
        ],
        "No health speculation — public books, lectures, and association pages only.",
        3,
    ),
    "what-a-small-city-clinic-inherited": (
        "Inherited stack, not a Washington tablet",
        [
            ("state", "License law"),
            ("guild", "Association code"),
            ("HIPAA", "Federal privacy"),
            ("local", "Clinic policy"),
        ],
        "What a Southeast Arkansas clinic inherits — a stack of texts, not one voice.",
        3,
    ),
    "what-we-opened": (
        "Bibliography as honesty list",
        [
            ("primary", "Association PDFs"),
            ("secondary", "Histories"),
            ("news", "Dated headlines"),
            ("[VERIFY]", "Open rows"),
        ],
        "Sources named in public — gaps marked instead of smoothed.",
        0,
    ),
    "portraits-we-will-not-fake": (
        "Portraits policy",
        [
            ("commons", "PD/CC only"),
            ("type", "Default plate"),
            ("AI", "Banned"),
            ("RIGHTS", "Per file"),
        ],
        "Wikimedia Commons only with RIGHTS.md — never AI-generated historical faces.",
        2,
    ),
    "map-to-the-sister-packs": (
        "Where to send the reader next",
        [
            ("ethics", "You are here"),
            ("heritage", "Therapy history"),
            ("ACT", "Mindfulness lane"),
            ("SLP", "Speech pack"),
        ],
        "Ethics documents here; schools, mindfulness, and speech history in sister folders.",
        0,
    ),
}

# slug -> portrait plate (Commons cleared only)
PORTRAIT_SPECS: dict[str, tuple[str, str, str]] = {
    "1947-tolman-committee": (
        "Edward C. Tolman",
        "1886–1959",
        "psychologist who chaired APA's 1947 Committee on Ethical Standards.",
    ),
}
