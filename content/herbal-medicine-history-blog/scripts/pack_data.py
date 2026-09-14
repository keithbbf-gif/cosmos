"""Article registry for herbal-medicine-history-blog (staged content)."""

from __future__ import annotations

# (file_suffix, slug, title, era_focus, category, tags)
ARTICLE_ROWS: list[tuple[str, str, str, str, str, list[str]]] = [
    ("edwin-smith-papyrus", "edwin-smith-papyrus", "The Edwin Smith Papyrus and wound botany", "circa 1600 BCE", "ancient", ["egypt", "papyrus", "surgery"]),
    ("mesopotamian-plant-tablets", "mesopotamian-plant-tablets", "Mesopotamian plant lists on clay", "circa 2000 BCE", "ancient", ["mesopotamia", "cuneiform"]),
    ("hippocratic-corpus-herbs", "hippocratic-corpus-herbs", "Hippocratic texts and Mediterranean simples", "circa 400 BCE", "ancient", ["greece", "hippocrates"]),
    ("dioscorides-de-materia-medica", "dioscorides-de-materia-medica", "Dioscorides and the De Materia Medica", "circa 77 CE", "ancient", ["rome", "pharmacognosy"]),
    ("galen-compound-medicines", "galen-compound-medicines", "Galen, compounds, and the formulary habit", "circa 180 CE", "ancient", ["galen", "formulary"]),
    ("ibn-sina-canon", "ibn-sina-canon", "Ibn Sina and the Canon of Medicine", "1025 CE", "medieval", ["islamic", "canon"]),
    ("rhazes-clinical-pharmacy", "rhazes-clinical-pharmacy", "Al-Razi and hospital pharmacy in practice", "circa 900 CE", "medieval", ["rhazes", "hospital"]),
    ("shennong-materia-medica", "shennong-materia-medica", "Shennong bencao and early Chinese materia medica", "tradition 1st c.", "ancient", ["china", "bencao"]),
    ("tang-formularies", "tang-formularies", "Tang dynasty formularies and imperial dispensaries", "659 CE", "medieval", ["china", "formulary"]),
    ("ayurveda-charaka-sushruta", "ayurveda-charaka-sushruta", "Charaka, Sushruta, and Ayurvedic plant categories", "tradition 1st c.", "ancient", ["india", "ayurveda"]),
    ("unani-tibb-synthesis", "unani-tibb-synthesis", "Unani tibb and the Greco-Arabic bridge", "circa 1000 CE", "medieval", ["unani", "humoral"]),
    ("monastic-herbaria", "monastic-herbaria", "Monastic gardens and medieval herbaria", "12th c.", "medieval", ["europe", "monastery"]),
    ("hildegard-physica", "hildegard-physica", "Hildegard of Bingen and Physica", "1158 CE", "medieval", ["hildegard", "germany"]),
    ("silk-road-medicinals", "silk-road-medicinals", "Silk Road exchanges of resins and roots", "1st–15th c.", "trade", ["silk-road", "trade"]),
    ("indian-ocean-spice-routes", "indian-ocean-spice-routes", "Indian Ocean spice routes and pharmacy", "8th–16th c.", "trade", ["spice", "maritime"]),
    ("arabian-gulf-pharmacy", "arabian-gulf-pharmacy", "Persian Gulf ports and materia medica sorting", "9th–13th c.", "trade", ["gulf", "ports"]),
    ("age-of-exploration-botany", "age-of-exploration-botany", "Age of Exploration and botanical transfer", "16th c.", "trade", ["exploration", "botany"]),
    ("columbian-exchange-medicinals", "columbian-exchange-medicinals", "Columbian Exchange medicinal plants", "16th–18th c.", "trade", ["americas", "exchange"]),
    ("paracelsus-chemical-medicine", "paracelsus-chemical-medicine", "Paracelsus and the chemical turn in medicine", "1520s", "early_modern", ["paracelsus", "iatrochemistry"]),
    ("willow-salicylate-path", "willow-salicylate-path", "From willow bark to salicylate chemistry", "1763–1899", "alkaloid", ["willow", "salicylate"]),
    ("opium-alkaloid-discovery", "opium-alkaloid-discovery", "Opium, morphine, and the alkaloid concept", "1804–1832", "alkaloid", ["opium", "morphine"]),
    ("cinchona-quinine-isolation", "cinchona-quinine-isolation", "Cinchona bark and quinine isolation", "1820–1940s", "alkaloid", ["cinchona", "quinine"]),
    ("colchicum-gout-alkaloids", "colchicum-gout-alkaloids", "Colchicum, gout, and colchicine history", "1820–1950s", "alkaloid", ["colchicum", "gout"]),
    ("belladonna-atropine", "belladonna-atropine", "Belladonna and atropine in pharmacopeias", "1833–1900s", "alkaloid", ["belladonna", "atropine"]),
    ("digitalis-cardiac-glycosides", "digitalis-cardiac-glycosides", "Digitalis and cardiac glycoside recognition", "1785–1957", "alkaloid", ["digitalis", "foxglove"]),
    ("ergot-alkaloid-history", "ergot-alkaloid-history", "Ergot, midwifery, and ergot alkaloids", "1582–1938", "alkaloid", ["ergot", "lysergic"]),
    ("caffeine-tea-coffee-trade", "caffeine-tea-coffee-trade", "Tea, coffee, and caffeine as global commodities", "17th–20th c.", "trade", ["caffeine", "tea"]),
    ("tobacco-nicotine-regulation", "tobacco-nicotine-regulation", "Tobacco, nicotine, and shifting regulation", "16th c.–now", "regulation", ["tobacco", "nicotine"]),
    ("victorian-patent-medicines", "victorian-patent-medicines", "Victorian patent medicines and newspaper ads", "1850–1906", "regulation", ["patent", "advertising"]),
    ("us-pharmacopeia-evolution", "us-pharmacopeia-evolution", "United States Pharmacopeia editions in context", "1820–2024", "pharmacopeia", ["usp", "standards"]),
    ("british-european-pharmacopoeias", "british-european-pharmacopoeias", "British and European pharmacopoeia lineages", "1864–2024", "pharmacopeia", ["bp", "ph-eur"]),
    ("pure-food-drug-act-1906", "pure-food-drug-act-1906", "The Pure Food and Drug Act of 1906", "1906", "regulation", ["fda", "1906"]),
    ("fdca-1938-sulfanilamide", "fdca-1938-sulfanilamide", "The 1938 FD&C Act after sulfanilamide", "1938", "regulation", ["fdca", "elixir"]),
    ("who-monographs-herbal", "who-monographs-herbal", "WHO monographs on selected medicinal plants", "1999–2024", "pharmacopeia", ["who", "monographs"]),
    ("eu-traditional-herbal-registration", "eu-traditional-herbal-registration", "EU traditional herbal medicinal products", "2004–2024", "regulation", ["eu", "thmpd"]),
    ("dshea-1994-supplements", "dshea-1994-supplements", "DSHEA and the US dietary-supplement category", "1994", "regulation", ["dshea", "usa"]),
    ("fda-dietary-supplement-cgmp", "fda-dietary-supplement-cgmp", "21 CFR Part 111 and supplement cGMP", "2007–2024", "regulation", ["cGMP", "111"]),
    ("biodiversity-medicinal-plants", "biodiversity-medicinal-plants", "CITES, Nagoya, and medicinal plant trade", "1973–2024", "regulation", ["cites", "biodiversity"]),
    ("ginseng-east-west-trade", "ginseng-east-west-trade", "Ginseng as an East–West trade case study", "18th–21st c.", "trade", ["ginseng", "trade"]),
    ("modern-phytochemistry-lab", "modern-phytochemistry-lab", "Twentieth-century phytochemistry without hype", "1920–2000", "early_modern", ["phytochemistry", "alkaloids"]),
]

DISCLAIMER = (
    "**Disclaimer.** Educational history only. Not medical advice. "
    "Past uses of plants do not prove safety or efficacy today. "
    "Do not use this series to self-treat or to market disease claims."
)

STUB = (
    "Draft shell for the Grok writer pass. Replace this paragraph with sourced narrative, "
    "primary citations, and `[VERIFY]` tags where print-ready dates are required."
)


def _section_titles(category: str) -> tuple[str, str]:
    if category == "trade":
        return ("## Routes and ports in the record", "## What changed when the cargo landed")
    if category == "alkaloid":
        return ("## From materia medica to named principle", "## Laboratory milestones readers should know")
    if category == "pharmacopeia":
        return ("## How the monograph is organized", "## Edition-to-edition shifts worth tracking")
    if category == "regulation":
        return ("## Statute and agency context", "## Operator timeline (US-focused where noted)")
    return ("## Textual and archaeological context", "## Plants named in the surviving record")


def _timeline_events(slug: str, title: str, era: str) -> list[tuple[str, str, str]]:
    return [
        (era.split()[0], "Corpus named", f"Opening anchor for “{title}” — verify exact dating in draft."),
        ("…", "Commentary layer", "Medieval or early modern copyists often reorder entries; note recension."),
        ("1800s", "Print pharmacopeia", "National compilations begin citing the same Latin binomials."),
        ("1900s", "Alkaloid / marker era", "Isolation chemistry renames many entries; cross-check old synonyms."),
        ("Today", "Historiography", "Museum, philology, and pharmacognosy methods — not clinical proof."),
    ]


def _alkaloid_events(slug: str) -> list[tuple[str, str, str]]:
    maps = {
        "willow-salicylate-path": [
            ("1763", "Stone letter", "Edmund Stone on willow and agues — often cited; verify primary."),
            ("1828", "Salicin", "Brugnatelli / Leroux isolation work — check spelling in sources."),
            ("1853", "Acetylation path", "Gerhardt experiments toward acetylsalicylic acid."),
            ("1899", "Aspirin marketed", "Bayer trademark era; not a supplement history lesson."),
        ],
        "opium-alkaloid-discovery": [
            ("1804", "Morphine", "Sertürner names morphium / morphine from opium."),
            ("1817", "Codeine", "Robiquet identifies codeine."),
            ("1832", "Alkaloid term", "Meissner's alkaloid concept spreads in pharmacy texts."),
            ("20th c.", "Scheduling", "International control treaties — legal, not efficacy."),
        ],
        "cinchona-quinine-isolation": [
            ("1630s", "Jesuit bark", "European adoption of cinchona bark narratives."),
            ("1820", "Quinine isolated", "Pelletier and Caventou — classic citation."),
            ("1940s", "Synthetic antimalarials", "Wartime chemistry shifts supply stories."),
        ],
    }
    return maps.get(
        slug,
        [
            ("19th c.", "Isolation", "Named principle isolated from plant material — dates vary by source."),
            ("Pharmacopeia", "Monograph entry", "Official texts standardize identity tests over time."),
            ("20th c.", "Semisynthesis", "Plant origin remains part of the supply story."),
            ("Today", "Historiography", "Illustrative lab milestones only — not prescribing guidance."),
        ],
    )


def _pharmacopeia_entries(slug: str) -> list[tuple[str, str]]:
    return [
        ("Atropa belladonna", "Leaf and root in 19th-c. plates"),
        ("Digitalis purpurea", "Foxglove leaf — digitalis glycosides"),
        ("Cinchona spp.", "Bark — quinine alkaloids"),
        ("Papaver somniferum", "Opium — morphine family"),
    ]


def _trade_nodes(slug: str) -> tuple[list[tuple[str, str]], list[tuple[int, int, str]]]:
    if "silk" in slug:
        nodes = [("Chang'an", "caravan hub"), ("Samarkand", "sorting"), ("Baghdad", "bazaar"), ("Alexandria", "Mediterranean")]
        routes = [(0, 1, "overland"), (1, 2, "caravan"), (2, 3, "sea leg")]
    elif "indian-ocean" in slug:
        nodes = [("Calicut", "spice"), ("Aden", "relay"), ("Cairo", "Red Sea"), ("Venice", "European gate")]
        routes = [(0, 1, "monsoon"), (1, 2, "portage"), (2, 3, "mediterranean")]
    elif "ginseng" in slug:
        nodes = [("Jilin", "wild root"), ("Beijing", "imperial tax"), ("Guangzhou", "export"), ("London", "apothecary")]
        routes = [(0, 1, "tribute"), (1, 2, "coastal"), (2, 3, "maritime")]
    else:
        nodes = [("Port A", "source"), ("Hub B", "sorting"), ("Port C", "re-export"), ("Market D", "dispensary")]
        routes = [(0, 1, "coastal"), (1, 2, "relay"), (2, 3, "retail")]
    return nodes, routes


def _plant_isolate(slug: str) -> tuple[str, list[str]]:
    plants = {
        "willow-salicylate-path": ("Salix spp. bark", ["Decoction / extract", "Salicin fraction", "Salicylic acid", "Acetylsalicylic acid (historical)"]),
        "opium-alkaloid-discovery": ("Papaver somniferum latex", ["Opium crude", "Alkaloid fractionation", "Morphine salt", "Pharmacopeia monograph"]),
        "cinchona-quinine-isolation": ("Cinchona bark", ["Tincture / decoction", "Alkaloid separation", "Quinine sulfate", "Antimalarial supply chain"]),
        "colchicum-gout-alkaloids": ("Colchicum autumnale", ["Seed / bulb prep", "Colchicine recognition", "Modern monograph", "Toxicity warnings in texts"]),
        "belladonna-atropine": ("Atropa belladonna", ["Leaf extract", "Tropane alkaloids", "Atropine sulfate", "Ophthalmic / anticholinergic history"]),
        "digitalis-cardiac-glycosides": ("Digitalis purpurea", ["Leaf infusion", "Glycoside fraction", "Digitoxin / digoxin era", "Clinical pharmacology texts"]),
        "ergot-alkaloid-history": ("Claviceps purpurea", ["Ergot on rye", "Ergot alkaloids", "Ergometrine / ergotamine", "Obstetric history"]),
    }
    return plants.get(
        slug,
        ("Representative medicinal plant", ["Maceration / decoction", "Crude extract", "Named principle", "Official monograph"]),
    )


def figure_specs_for(slug: str, category: str, title: str, era: str) -> list[dict]:
    h1, h2 = _section_titles(category)
    specs: list[dict] = []

    if category == "trade":
        nodes, routes = _trade_nodes(slug)
        specs.append(
            {
                "heading": h1,
                "file": "trade-route-schematic.svg",
                "alt": f"Illustrative schematic of ports and overland legs for {title}.",
                "caption": (
                    f"Figure 1. Illustrative trade schematic for “{title}” — simplified geography, not navigation or modern routing."
                ),
                "kind": "trade",
                "args": {"title": f"{title} — illustrative route", "nodes": nodes, "routes": routes, "footnote": "Speculative topology for literacy; verify ports and dates in prose."},
            }
        )
        specs.append(
            {
                "heading": h2,
                "file": "milestones-timeline.svg",
                "alt": f"Timeline of selected milestones for {title}.",
                "caption": f"Figure 2. Dated beats to verify in draft — not a clinical efficacy chart.",
                "kind": "timeline",
                "args": {"title": f"{title} — selected milestones", "events": _timeline_events(slug, title, era), "footnote": "Illustrative sequencing until writer locks citations."},
            }
        )
    elif category == "alkaloid":
        plant, steps = _plant_isolate(slug)
        specs.append(
            {
                "heading": h1,
                "file": "plant-to-principle.svg",
                "alt": f"Schematic from plant material to named principle for {plant}.",
                "caption": f"Figure 1. Historical processing schematic — not synthesis instructions or dosing guidance.",
                "kind": "plant_isolate",
                "args": {"title": f"{plant} → named principle (historical)", "plant": plant, "steps": steps, "footnote": "Process labels are historiographic, not manufacturing SOPs."},
            }
        )
        specs.append(
            {
                "heading": h2,
                "file": "discovery-timeline.svg",
                "alt": f"Discovery and pharmacopeia timeline for {title}.",
                "caption": f"Figure 2. Laboratory and regulatory dates to cite — no fabricated effect sizes.",
                "kind": "timeline",
                "args": {"title": f"{title} — discovery timeline", "events": _alkaloid_events(slug), "footnote": "Verify each date against primary sources before print."},
            }
        )
    elif category == "pharmacopeia":
        specs.append(
            {
                "heading": h1,
                "file": "comparative-plate.svg",
                "alt": "Line plate comparing four pharmacopeia entries as stylized botanical diagrams.",
                "caption": "Figure 1. Comparative plate for reading monographs — line art only, not herbarium IDs.",
                "kind": "pharmacopeia",
                "args": {"title": "Comparative pharmacopeia plate (line)", "entries": _pharmacopeia_entries(slug), "footnote": "Latin names follow historical spellings; modern taxonomy may differ."},
            }
        )
        specs.append(
            {
                "heading": h2,
                "file": "edition-timeline.svg",
                "alt": f"Timeline of pharmacopeia edition milestones for {title}.",
                "caption": "Figure 2. Edition and harmonization beats — verify against official publishers.",
                "kind": "timeline",
                "args": {"title": f"{title} — edition timeline", "events": _timeline_events(slug, title, era), "footnote": "USP/BP/Ph. Eur. dates must be confirmed in draft."},
            }
        )
    elif category == "regulation":
        reg_events = {
            "pure-food-drug-act-1906": [
                ("1906", "Pure Food and Drug Act", "Wiley-era federal food and drug law."),
                ("1912", "Sherley Amendment", "False therapeutic claims language — verify scope."),
                ("1938", "FD&C Act", "Safety standard after sulfanilamide disaster."),
            ],
            "fdca-1938-sulfanilamide": [
                ("1937", "Elixir sulfanilamide", "Massengill disaster — diethylene glycol solvent."),
                ("1938", "FD&C Act", "New drug safety requirement."),
                ("1962", "Kefauver-Harris", "Efficacy standard for drugs — context for botanical drugs."),
            ],
            "dshea-1994-supplements": [
                ("1994", "DSHEA enacted", "Pub. L. 103-417 — dietary supplement category."),
                ("2006", "Adverse event reporting", "AER rule for supplements — verify date in draft."),
                ("2007", "Part 111 cGMP", "21 CFR 111 final rule era."),
            ],
            "eu-traditional-herbal-registration": [
                ("2004", "THMPD", "EU traditional herbal medicinal products directive."),
                ("2011", "Herbal monographs", "EMA committee monograph program expands."),
                ("2024", "National registers", "Member-state implementation still varies."),
            ],
            "fda-dietary-supplement-cgmp": [
                ("2007", "Part 111", "cGMP for dietary supplements."),
                ("2010", "Inspection cadence", "FDA inspection themes evolve — cite current guidance."),
                ("2024", "Quality agreements", "Contract manufacturer liability stays with brand owner."),
            ],
            "tobacco-nicotine-regulation": [
                ("1600s", "Colonial trade", "Tobacco as commodity, not medicine."),
                ("1964", "Surgeon General", "Smoking and health report."),
                ("2009", "FSPTCA", "FDA tobacco center — separate from supplements."),
            ],
            "biodiversity-medicinal-plants": [
                ("1973", "CITES", "Appendix listings for some medicinal species."),
                ("1992", "CBD", "Convention on Biological Diversity."),
                ("2010", "Nagoya Protocol", "Access and benefit-sharing for genetic resources."),
            ],
            "victorian-patent-medicines": [
                ("1850s", "Patent medicine ads", "Newspaper and almanac marketing boom."),
                ("1906", "Pure Food and Drug Act", "Labeling and adulteration federal hook."),
            ],
        }
        events = reg_events.get(slug, _timeline_events(slug, title, era))
        specs.append(
            {
                "heading": h1,
                "file": "regulation-timeline.svg",
                "alt": f"Regulatory timeline for {title}.",
                "caption": "Figure 1. Statutory milestones — legal history, not treatment recommendations.",
                "kind": "timeline",
                "args": {"title": f"{title} — regulation timeline", "events": events, "footnote": "Counsel verifies current law; this figure is educational."},
            }
        )
        specs.append(
            {
                "heading": h2,
                "file": "agency-flow.svg",
                "alt": "Flow from product category to agency review concepts.",
                "caption": "Figure 2. Illustrative agency questions — not a filing checklist.",
                "kind": "flow",
                "args": {
                    "title": "Illustrative review questions (US-centric)",
                    "steps": [
                        "Is the article a food, drug, device, or cosmetic category?",
                        "Does intended use include disease diagnosis or treatment?",
                        "Are structure/function claims notified and substantiated?",
                        "Do advertising claims match competent scientific evidence (FTC)?",
                    ],
                    "footnote": "Simplified for history readers; modern SKUs need counsel.",
                },
            }
        )
    else:
        specs.append(
            {
                "heading": h1,
                "file": "historical-timeline.svg",
                "alt": f"Historical timeline for {title}.",
                "caption": f"Figure 1. Anchors for antiquity-to-modern framing — verify dates in draft.",
                "kind": "timeline",
                "args": {"title": f"{title} — historical anchors", "events": _timeline_events(slug, title, era), "footnote": "Illustrative until philological citations are attached."},
            }
        )
        specs.append(
            {
                "heading": h2,
                "file": "materia-medica-plate.svg",
                "alt": "Stylized line plate of plants named in related pharmacopeia traditions.",
                "caption": "Figure 2. Comparative materia medica plate — illustrative line art, not botanical ID.",
                "kind": "pharmacopeia",
                "args": {"title": "Materia medica plate (line)", "entries": _pharmacopeia_entries(slug), "footnote": "Speculative pairing for layout; writer aligns taxa to text."},
            }
        )
    return specs


def build_articles() -> list[dict]:
    out: list[dict] = []
    for i, (suffix, slug, title, era, category, tags) in enumerate(ARTICLE_ROWS, start=1):
        h1, h2 = _section_titles(category)
        figures = figure_specs_for(slug, category, title, era)
        out.append(
            {
                "num": i,
                "file": f"{i:02d}-{suffix}.md",
                "slug": slug,
                "title": title,
                "meta_description": f"Historical essay shell: {title}. Educational only.",
                "era_focus": era,
                "tags": tags,
                "category": category,
                "sections": [
                    {"heading": h1, "body": STUB},
                    {"heading": h2, "body": STUB},
                ],
                "figures": figures,
            }
        )
    return out


ARTICLES: list[dict] = build_articles()


def embed_plan() -> dict[str, list[tuple[str, list[tuple[str, str, str]]]]]:
    plan: dict[str, list[tuple[str, list[tuple[str, str, str]]]]] = {}
    for art in ARTICLES:
        by_heading: dict[str, list[tuple[str, str, str]]] = {}
        for fig in art["figures"]:
            rel = f"../assets/{art['slug']}/{fig['file']}"
            by_heading.setdefault(fig["heading"], []).append((rel, fig["alt"], fig["caption"]))
        plan[art["file"]] = [(h, figs) for h, figs in by_heading.items()]
    return plan


EMBED_PLAN = embed_plan()
