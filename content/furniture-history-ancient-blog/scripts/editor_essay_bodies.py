"""Topic-specific prose bodies for the editor pass (slug -> list of paragraphs)."""

# Each value is markdown paragraphs (joined with blank lines in apply script).
BODIES: dict[str, list[str]] = {}

def _p(slug: str, *paragraphs: str) -> None:
    BODIES[slug] = list(paragraphs)

# 01–11
_p(
    "mesopotamian-chair-evidence",
    "Mesopotamian chairs arrive in the archaeological record mostly as ghosts: legs and tenons in palace destruction levels, and far more often as carved stone substitutes for wood on palace reliefs. Between **3000 and 539 BCE**, the question is not whether elites sat elevated—they did—but how sculptors translated workshop reality into an iconography of command.",
    "Cylinder seals and Early Dynastic plaques already show figures on high-backed seats, while Neo-Assyrian palace programs freeze the king on a throne whose legs terminate in lion paws or bull hooves. Those animal feet are rhetorical, not zoological; they signal domination over the ordered world. Typology therefore tracks **posture protocols** as much as joinery: who may sit, on what height, with arms exposed or shielded by a wrap-around back.",
    "Cuneiform inventories occasionally list wooden furniture alongside metal fittings, but rarely describe silhouette. When a text mentions a chair of ebony or cedar, the modern reader still lacks seat depth and back rake. The typology plate (Fig. 3) separates morphotypes—open stool, wrap-around throne, portable folding frame—so readers do not collapse distinct social uses into one generic “Mesopotamian chair.”",
    "Chronology matters because chair height rises with centralized spectacle. Third-millennium seats in temples differ from eighth-century Assyrian audience furniture in scale and in the relief convention that enlarges the king’s knees toward the viewer. The timeline (Fig. 1) stays coarse; debates over Uruk IV versus Early Dynastic III seating belong in footnotes, not in millimeter-precise graphics.",
    "Maps here are schematic guides to circulation: Mari, Nimrud, Babylon, Susa. Cedar moved downriver; ideas about enthronement moved with ambassadors and captured craftsmen. Compare the map with site plans in excavation reports rather than treating coastlines as GIS truth.",
    "Gallery labels that show a single reconstructed throne risk implying a unified typology across two millennia. These redrawn figures state their didactic intent: morphology and rank, not a forged photograph of one accessioned object.",
)

_p(
    "egyptian-folding-stool",
    "The Egyptian folding stool is a portable argument about rank. In the New Kingdom especially, painted tomb scenes show officials carrying lattice-legged stools that open with crossed struts—furniture light enough for processions yet stiff enough for court. **2686–30 BCE** spans formats from compact camp stools to gilded examples buried with nobles.",
    "Surviving wooden frames, often from Theban tombs, reveal careful pegging and animal-skin seats rather than upholstered panels. Lion paws on front legs echo palace thrones but on a collapsible scale; the typology diagram contrasts ceremonial fixed chairs with foldable field furniture. Joinery had to survive repeated opening without metal hinges as we know them—leather sleeves and shaped pivots carried the load.",
    "Texts and scenes pair the stool with scribal kits and overseer roles: to sit on a folding stool was to hold delegated authority, not domestic ease. Misreading these objects as camping gear flattens Egyptian social grammar.",
    "Fig. 1 anchors well-dated tomb groups (Eighteenth Dynasty Thebes, Ramesside burials) against long-lived types that persist into Ptolemaic painting. Where chronology wobbles between iconographic persistence and new joinery tricks, prose should say so plainly.",
    "The Nile Valley map marks workshop centers and import routes for ebony and ivory inlays sometimes applied to stool rails. It does not survey every nome; it orients the reader toward corpus volumes on furniture from Egyptian museums (described textually, not photographed here).",
    "Reconstruction drawings in older publications occasionally over-tighten lattice angles. Prefer measured drawings from excavation archives when building a physical replica; use these schematics for classroom comparison only.",
)

_p(
    "egyptian-bed-frames",
    "Pharaonic bed frames are not our mattresses on legs. They are low platforms with lion- or bull-footed supports, headboards that can carry protective deities, and string or mat surfaces that imply a different sleep posture than the raised European bed. The New Kingdom window **1550–1069 BCE** concentrates well-published examples from Theban tombs.",
    "Surviving wood—when humidity allows—shows mortised rails and turned legs copied from metal prototypes in shape if not in material. Tomb scenes add color: gilded headboards, linen hangings, and beds carried as funeral equipment. The bed’s role in awakening rituals and protective magic ties furniture to text corpora that rarely mention dimensions.",
    "Typology must separate **sleeping platforms**, **day couches**, and **funerary biers** that share zoomorphic feet but serve different rites. A single morphotype plate cannot stand in for that separation; readers should cross-walk Fig. 3 with scenes in the Theban necropolis publications.",
    "Inventories list beds with determinatives that lexicographers still parse; this essay does not invent catalog numbers. Thin spot: exact household bed counts for middle-rank artisans remain under-published compared with royal burials.",
    "Regional focus on the Nile Valley highlights Thebes, Amarna, and Delta sites with preserved wood. Export of style—not always of objects—shows in Aegean borrowings of headboard form.",
    "Museum reconstructions sometimes raise beds higher than tomb scenes suggest. Treat elevation plates as comparative, not prescriptive for gallery mounting height.",
)

_p(
    "minoan-throne-hierarchy",
    "Knossos Room 4—the so-called throne room—centers Minoan debates about seated authority. The gypsum seat against the north wall is fixed, flanked by benches and griffin frescoes. Whether a priest-king or a goddess’s epiphany occupied that seat remains contested; the furniture, however, is material and in situ on Crete between **1900 and 1450 BCE**.",
    "Minoan palaces distribute seating across stepped benches, low stools, and one-off stone thrones rather than uniform chair typologies. Frescoes from Akrotiri show elegant camp stools and woven seats; administrative seating may have favored benches that kept bodies aligned for long sessions.",
    "Hierarchy reads through **placement**: throne against wall, benches lateral, floor cushions for attendants. The typology figure encodes those roles, not IKEA categories.",
    "Chronology links Neopalatial peak to LM IA–IB destruction horizons. Thera’s eruption threads into dating fresco parallels; the timeline stays schematic so LM/LH debates remain in prose.",
    "Aegean trade routes on the map explain ivory inlays and Egyptianizing motifs without claiming direct import of finished thrones.",
    "Replicas in heritage sites sometimes romanticize the gypsum seat. These diagrams refuse photographic mimicry; cite Evans and later stratigraphic critiques when arguing function.",
)

_p(
    "mycenaean-throne-stools",
    "On the Greek mainland **1600–1100 BCE**, thrones appear in palatial contexts at Pylos, Mycenae, and Tiryns as fragmentary stone or bronze fittings attached to wooden frames long decayed. High-backed stools in fresco and glyptic echo Minoan prototypes but stiffen toward martial display.",
    "Linear B tablets mention furniture sparingly; when they do, lexical overlap with seating and footstools demands caution. Archaeology supplies carved chair stumps and ivory inlays from chamber tombs that imply conspicuous consumption at feasts.",
    "Typology contrasts **fixed thrones** for wanax ceremony with **portable high stools** for banqueters. Leg shape—turned, saber, animal paw—tracks chronology from LH II to LH IIIC.",
    "The timeline aligns palatial destructions with changes in seat height in pictorial art. Sub-Mycenaean simplification may reduce back height; confirm against regional cemetery evidence.",
    "Mainland Greece on the map is a schematic anchor for workshop exchange with Crete and Cyprus.",
    "Do not merge Mycenaean seats with later Greek klismos lines without an intermediate argument; morphology diverges at the joinery.",
)

_p(
    "greek-klinai-symposium",
    "The Greek **kline** is a dining couch before it is a bed. From sympotic pottery through Macedonian tomb furniture, the Aegean world **700–300 BCE** normalized reclining on left elbow for banquets—a posture that drives room architecture and cushion logistics.",
    "Vase painters show klinai as patterned mattresses on low frames; stone versions from tombs at Pella and Vergina preserve painted decoration on actual wood. Leg turnings and headrests become typological markers across Classical and Hellenistic phases.",
    "Symposium etiquette maps guests to positions (honored middle, flanking couches). Furniture is choreography: without triclinium logic, the kline collapses into a generic couch.",
    "Fig. 1 spans Archaic sympotic scenes through Hellenistic palace dining. Dating painterly fashion against excavated frames produces known mismatches; note them in text.",
    "Regional circulation includes Magna Graecia and coastal Anatolia workshops copying Attic turnings.",
    "Modern banquet reconstructions often set klinai too upright. Comparative plates show rake angles as hypotheses, not ergonomic finals.",
)

_p(
    "greek-chair-types",
    "Greek vocabulary sorts seating finer than English does: **thronos** (enthroned authority), **klismos** (curved stile chair), **diphros** (backless stool), **thronos** versus priestly **bathron**. Literary and votive evidence from **600–146 BCE** must align with scant wooden remains and abundant pottery scenes.",
    "The klismos silhouette—saber legs, horizontal back rails—becomes an export image of Hellenic taste. Stone reliefs and bronze mirrors preserve the line when wood fails. Typology plates separate thronos mass from klismos elegance and diphros portability.",
    "Chairs appear in drama as props of office: the tyrant’s seat, the judge’s bench. Reading typology without tragedy and oratory loses the performative frame.",
    "Chronology tracks Persian War-era simplicity against fourth-century luxury inlays documented in inventories.",
    "Hellenic world map marks Athens, Sparta, Delphi votives, and colonial finds—not a political border map.",
    "Lexicon essays need philological caution; this piece flags thin spots where Latin **sella** later overlays Greek terms in bilingual inscriptions.",
)

_p(
    "roman-cubiculum-furniture",
    "The Roman **cubiculum** bundles sleep, sex, and display. Beds (**lecti**), chests, and occasional chairs share a small room off the atrium or upper story. Italy **100 BCE–300 CE** provides Pompeian wall painting, carbonized wood from rare contexts, and legal texts on dowry furniture.",
    "Bed frames range from simple rope-strung platforms to elaborate bronze-mounted headboards in elite houses. Night lamps, slippers, and mirrors in frescoes show furniture as part of a nocturnal kit rather than isolated sculpture.",
    "Typology must separate **garden-room sleeping couches** from **formal reception beds** that never held sleep. Mislabeling confuses social use.",
    "Timeline crosses Republic austerity with Imperial luxury and late antique simplification.",
    "Campania dominates preservation; the map reminds readers that Rome’s urban furniture often survives only in representation.",
    "Reconstruction ethics: carbonized fragments justify partial mounts; painted beds on walls justify color, not dimension alone.",
)

_p(
    "roman-triclinium-dining",
    "Roman dining rooms arrange three **lecti** around a central table so guests recline on the left arm. The **triclinium** layout—walls marked for couch placement, mosaics implying orientation—outlasts the wooden couches themselves across the Empire **200 BCE–400 CE**.",
    "Pompeian houses preserve floor cues; literary satire preserves social embarrassment when a guest receives the wrong couch. Cushions and bolsters (see the series essay on upholstery) convert hard frames into hour-long meals.",
    "Typology contrasts U-shaped formal arrangements with simpler single-couch dining in apartments.",
    "Western Empire sites versus eastern palaces show divergent leg carving fashions; the timeline notes third-century shifts without over-precision.",
    "Schematic map traces couch exports through port cities, not consumer surveys.",
    "Museum dioramas that cram three full couches into small rooms ignore architectural measurements from house plans.",
)

_p(
    "etruscan-funeral-couches",
    "Etruscan chamber tombs place banqueting couches in stone as permanent furniture for the dead **700–200 BCE**. Tufa couches at Tarquinia and painted terracotta equivalents rehearse a symposium that continues beyond life.",
    "Banqueting scenes on sarcophagi pair male and female recliners in ways Greek norms rarely allowed. Typology encodes gendered postures and double couches versus single lecti.",
    "Metal fittings and ivory inlays on fragmentary wood hint at workshop skill; most evidence is sculptural substitute for perishable frames.",
    "Chronology links Orientalizing luxury to Hellenizing simplification.",
    "Etruria on the map situates coastal trade that brought Aegean turnings inland.",
    "Funerary couches are not domestic imports copied verbatim; exaggeration serves tomb display.",
)

_p(
    "persian-throne-protocol",
    "Achaemenid audience scenes at Persepolis encode throne protocol in stone: the king elevated, attendants with flywhisks, tribute bearers on lower ground **550–330 BCE**. Wooden thrones did not survive the burnings; the relief is the furniture.",
    "Classical authors describe golden thrones and portable camps; archaeology supplies platform heights and stair alignments that imply furniture scale.",
    "Typology separates **enthronement on platform** from **camp stool** mobility for royal tours.",
    "Timeline crosses Cyrus through Darius III; Macedonian conquest ends the court but not the image repertoire.",
    "Persia schematic map includes satrap capitals where local workshops adapted court forms.",
    "Avoid conflating Apadana relief thrones with later Sasanian silver furniture; series cross-links handle succession.",
)

_p(
    "achaemenid-furniture-trade",
    "Luxury wood moved across the Achaemenid sphere along roads and sea lanes **550–330 BCE**. Cedar from Lebanon, Indian ivory, Egyptian ebony—texts and archaeology trace **materials** more often than finished dining sets.",
    "Administrative tablets and Greek mercenary memoirs mention portable tables and elaborate beds in royal baggage trains. Furniture here is logistics: pack animals, disassembly, regilding after transit.",
    "Typology for trade focuses on **flat-pack tables**, folding stands, and throne components shipped as prestige gifts.",
    "Timeline aligns foundation of royal road systems with increased gift exchange in fifth-century diplomacy.",
    "Near East map marks Sardis, Susa, Persepolis, and Mediterranean ports—schematic trade arcs only.",
    "Thin citation zone: quantified export volumes for furniture specifically are rare; infer from timber duties and gift lists.",
)

# 12–22
_p(
    "levantine-ivory-inlays",
    "Levantine workshops **1200–600 BCE** produced ivory plaques meant to nail onto wooden furniture fronts—sphinxes, lotus bundles, “woman at the window” motifs. Samaria, Nimrud, and Damascus area hoards preserve panels ripped from chairs and beds during sackings.",
    "Inlay furniture is fragmentary by nature: plaques survive, substrates rot. Typology reconstructs chair backs and bed headboards from repeatable panel sizes and nail holes.",
    "Phoenician and Aramean styles interleave; attribution debates belong in prose, not in map borders.",
    "Iron Age chronology ties panel style to Megiddo levels and Neo-Assyrian booty lists.",
    "Levant map shows inland capitals and coastal ports without survey-grade coastlines.",
    "Do not invent joinery behind plaques; cite excavation drawings when silhouettes inform Fig. 4.",
)

_p(
    "phoenician-export-furniture",
    "Phoenician merchants exported **cedar logs** and, with them, forms: headboards with Egyptianizing volutes, low tables, and shrine furniture **1000–500 BCE**. Finished pieces rarely survive; shipwreck and colony archaeology supply hints.",
    "Classical writers credit Phoenicians with introducing couches to the west; material proof is indirect—colony tombs with Levantine turnings.",
    "Typology tracks **export silhouettes** versus local hybrid copies in Sardinia and Iberia.",
    "Timeline spans Iron Age peak to Hellenistic absorption of workshops.",
    "Eastern Mediterranean map arcs Tyre, Carthage, and colonial cemeteries.",
    "Cedar supply essay in this series complements but does not duplicate timber law texts.",
)

_p(
    "assyrian-relief-seating",
    "Assyrian palace reliefs **900–612 BCE** are deliberate furniture catalogs for royal ideology. Kings sit on high-backed thrones with attendants shading them; conquered enemies kneel or stand. Scale is rhetorical: knees enlarged, throne legs as lion paws.",
    "Relief evidence biases toward ceremony, not kitchens. Still, it preserves footstool types, high stools for scribes, and camp furniture in campaign scenes.",
    "Typology codes **enthroned king**, **standing court**, **kneeling tribute** as furniture-relative postures.",
    "Timeline links Ashurnasirpal II through Ashurbanipal libraries.",
    "Assyria map centers Nimrud, Khorsabad, Nineveh destruction horizons.",
    "Photographic forgery is unnecessary when line drawings extract silhouette; these SVGs are didactic reductions.",
)

_p(
    "neo-babylonian-household",
    "Neo-Babylonian legal and economic texts **626–539 BCE** name household goods: beds, chairs, tables, lamps. Furniture appears in dowry lists, debt pledges, and temple leases—language without illustration.",
    "Translating Akkadian terms onto modern typology risks false precision. Some words may mean chests used as seats; context clauses matter.",
    "Typology here is **text-forward**: group by determinative and by room of mention (roof terrace, inner chamber).",
    "Timeline crosses Nabopolassar through Cyrus’s entry; archival density peaks in late archives.",
    "Babylonia map orients Ur, Uruk, Babylon urban households.",
    "Flag: few published joins between text lines and excavated Neo-Babylonian house plans.",
)

_p(
    "cypriot-wood-traditions",
    "Cyprus sat between Aegean, Levantine, and Near Eastern furniture idioms **1200–300 BCE**. Tomb beds with animal legs, ivory plaques, and bronze fittings show hybrid workshops serving both palace and export.",
    "Wood species and metal technology shifted with Phoenician settlement and Archaic Greek trade.",
    "Typology labels **hybrid morphotypes**—Minoan curve on Levantine plaque layout—without pretending single authorship.",
    "Chronology runs Geometric through Hellenistic royal tombs at Soloi.",
    "Island schematic on the map; compare with site plans in Cyprus Survey volumes.",
    "Thin spot: fewer intact wooden frames than plaque hoards.",
)

_p(
    "urartian-metal-furniture",
    "Urartian fortresses in the Armenian highlands **860–590 BCE** yield bronze shield rings, furniture nails, and ceremonial standards more often than wooden seats. Metal fittings imply thrones and banquet equipment in fire-destroyed halls.",
    "Inscriptions boast of booty including enemy furniture; archaeology supplies local production of bronze couch fittings.",
    "Typology emphasizes **metal appliqué** and riveted strapping on timber frames.",
    "Timeline aligns Menua and Argishti building phases with Assyrian conflict horizons.",
    "Highland map is intentionally coarse given alpine site dispersion.",
    "Reconstruction must not invent wooden sections without mineralized wood evidence.",
)

_p(
    "hittite-seating-ritual",
    "Hittite ritual texts from Anatolia **1600–1180 BCE** prescribe seating arrangements for festivals: gods, king, and priests occupy differentiated furniture in temple courtyards.",
    "Archaeology at Boğazköy offers stone bases and fragmentary furnishings; cuneiform instructions supply choreography.",
    "Typology links **cult stool**, **king’s seat**, and **ritual couch** where festivals mirror Mesopotamian loans.",
    "New Hittite versus Empire phases appear on the timeline schematic.",
    "Anatolia map marks capital and provincial temples without exhaustive survey.",
    "Philological gaps: some Hittite furniture terms lack agreed morphological match.",
)

_p(
    "indus-valley-household-forms",
    "Indus Valley sites **2600–1900 BCE** preserve stone seating platforms, probable stool legs in terracotta, and house plans with raised sleeping platforms—nothing like a European chair typology.",
    "Evidence is architectural and small-find based; seals rarely depict seated furniture clearly.",
    "Typology stresses **platform**, **low stool**, and **courtyard bench** inferred from plans at Mohenjo-daro and Harappa.",
    "Timeline marks Mature Harappan peak and deurbanization—dating debates stay in prose.",
    "South Asia map schematic for major mounds only.",
    "**Weak article flag:** thin pictorial corpus; arguments lean on comparative Near Eastern platform habits cautiously.",
)

_p(
    "vedic-india-low-seating",
    "Vedic texts from North India **1500–500 BCE** describe ritual seated on grass, hides, and low wooden seats (**asana**). Archaeology for the period offers little wooden furniture; the essay is philological and ethnographic comparator aware.",
    "Later sculptural and pillar edicts retroject court seating; do not read them straight back into Rigvedic camps.",
    "Typology lists floor, low stool, and teacher’s seat as social gradations.",
    "Timeline crosses Vedic composition layers cautiously.",
    "Regional map orients Ganges plain ritual geography schematically.",
    "**Weak article flag:** minimal excavation joins; cite secondary philology, not invented objects.",
)

_p(
    "mauryan-palace-furniture",
    "Mauryan palace descriptions in **Arthashastra**-era sources and Ashokan legends mention gilded couches, elephant-leg beds, and audience halls **322–185 BCE**. Archaeology supplies polished stone columns, not wooden thrones.",
    "Pataliputra’s wooden palaces burned; literary hyperbole may inflate furniture lists.",
    "Typology treats **palace bed**, **audience seat**, and **camp furniture** as textual categories.",
    "Timeline spans Chandragupta through Shunga transition.",
    "India map marks capitals and rock-edict geography only.",
    "**Weak article flag:** literature-heavy; no secure Mauryan wooden throne.",
)

_p(
    "han-dynasty-low-platforms",
    "Han tombs in China **206 BCE–220 CE** preserve lacquered low platforms, couch frames, and screen furniture in waterlogged contexts. Platform sleeping and seated reception on mats intersect with emerging raised furniture for elite display.",
    "Lacquer layers preserve color and metal fittings when wood structure collapses.",
    "Typology separates **platform bed (chuang)**, **couch**, and **armchair precursors** in late Han art.",
    "Timeline crosses Western Han opulence and Eastern Han simplification.",
    "China map marks Chang’an, Luoyang, and key tomb districts schematically.",
    "Climate bias: northern dry tombs versus southern waterlogged preservation.",
)

# 23–33
_p(
    "chinese-kang-platform-beds",
    "Heated sleeping platforms—the **kang** tradition in North China—have long archaeological antecedents in raised heated surfaces and stove-linked benches **1000 BCE–200 CE**. This essay traces platform logic before brick kang maturity.",
    "Warring States and Han architecture shows kang-like sleeping surfaces tied to flue systems in northern winters.",
    "Typology links **stove bench**, **raised sleeping platform**, and **mat-on-floor** summer habits.",
    "Timeline is deliberately long and coarse given regional climate variation.",
    "North China schematic map; not a climatic GIS model.",
    "**Weak article flag:** pre-Han heated platform evidence is architectural inference more than furniture finds.",
)

_p(
    "korean-on-demand-platforms",
    "Korean floor culture and **ondol** heating **300 BCE–600 CE** encourage low portable platforms and heated floors rather than high chairs. Archaeology for early platforms is sparse; later Joseon evidence is often projected backward cautiously.",
    "Comparative Japan and China essays in this series provide context without merging traditions.",
    "Typology: **heated floor**, **low tray table**, **portable lectern** for elites on mats.",
    "Timeline schematic across Three Kingdoms toward Unified Silla.",
    "Peninsula map illustrative only.",
    "**Weak article flag:** sparse early furniture finds; argument relies on architectural parallels.",
)

_p(
    "japanese-floor-sitting",
    "Japanese **floor sitting** from Yayoi through early Heian **300–800 CE** ties domestic life to tatami logic precursors—woven mats, low tables, and zabuton cushions emerge late in the window.",
    "Archaeology supplies pit dwellings and raised-floor storehouses; seating is inferred from hearth placement.",
    "Typology contrasts **floor mat**, **low camp stool** in ritual, and imported Chinese chairs for court by Nara period.",
    "Timeline ends before full chair adoption; later essays carry that story.",
    "Japan map schematic for key capitals and ritual sites.",
    "Do not equate modern zabuton with ancient straw mats without period caveats.",
)

_p(
    "nubian-egyptian-exchange",
    "Nubian and Egyptian interaction **1550–600 BCE** moved beds, stools, and storage along the Nile. Kerma and Napatan elites adopted and resisted Egyptianizing furniture forms.",
    "Tomb furniture at el-Kurru and Nuri shows hybrid animal-leg beds and Egyptian chest types.",
    "Typology tracks **Egyptian import**, **Nubian local**, and **Kushite revival** morphotypes.",
    "Timeline crosses New Kingdom occupation through Twenty-fifth Dynasty.",
    "Nile corridor map schematic.",
    "Colonial bias in excavation reports may overstate Egyptianization.",
)

_p(
    "ptolemaic-fusion-forms",
    "Ptolemaic Egypt **305–30 BCE** blends Macedonian klinai, pharaonic beds, and Alexandrian luxury in houses and tombs. Fusion is visible in painted tomb furniture and surviving wooden fragments.",
    "Greek names on Egyptian forms complicate typology labels.",
    "Typology encodes **hybrid headboard**, **Greek couch on Egyptian platform**.",
    "Timeline from Ptolemy I through Roman annexation.",
    "Egypt map: Alexandria, Fayum, Theban tombs.",
    "Alexandrian wood is underrepresented versus textual opulence.",
)

_p(
    "hellenistic-luxury-goods",
    "Hellenistic patrons **323–31 BCE** commissioned inlaid thrones, silver couches, and parade furniture attested in inventories, shipwrecks, and victory booty lists.",
    "Delos houses and Vergina tombs anchor domestic reality against royal exaggeration.",
    "Typology: **court throne**, **sympotic silver**, **portable shrine furniture**.",
    "Timeline from Alexander’s successors through Actium.",
    "Eastern Mediterranean trade schematic.",
    "Shipwreck furniture is rare; most examples are metal vessels interpreted as banquet sets.",
)

_p(
    "pompeian-house-furniture",
    "Pompeian houses **200 BCE–79 CE** freeze movable furniture in wall paint, bronze fittings, and occasional carbonized wood. Chests, tables, lamps, and couches appear as sets tied to room function.",
    "The eruption records placement, not always ownership across generations.",
    "Typology by room: **atrium bench**, **cubiculum bed**, **triclinium couch**.",
    "Timeline ends 79 CE; pre-Roman Oscan layers omitted here.",
    "Campania map with Vesuvian cities labeled schematically.",
    "Household inventories from legal texts complement archaeology in the economics essay.",
)

_p(
    "herculaneum-carbonized-wood",
    "Herculaneum’s **79 CE** pyroclastic surge carbonized wooden furniture in the Villa of the Papyri and waterfront shops—among the rare cases where Roman joinery survives as charred fiber.",
    "Conservation stabilizes fragments; reconstruction debates focus on hinge types and couch rake.",
    "Typology derives from **measurable charred lengths**, not fresco alone.",
    "Single-year anchor on timeline; comparative Pompeii contexts noted.",
    "Bay of Naples inset map.",
    "Flag: public access to fragments rotates; cite conservation bulletins, not static photos.",
)

_p(
    "catacombs-funeral-furniture",
    "Late antique Roman catacombs **200–500 CE** rarely contain furniture; stone sarcophagi and arcosolia substitute for perishable couches. Christian burial shifts emphasis from banquet couch to loculus niche.",
    "Silver and ivory fittings in elite catacomb zones hint at displaced household goods.",
    "Typology contrasts **pagan funeral couch tradition** with **Christian niche burial**.",
    "Timeline crosses legal recognition of Christianity through Gothic sieges.",
    "Rome schematic map for major catacomb belts.",
    "Thin physical furniture; argument is mostly typological succession.",
)

_p(
    "byzantine-throne-symbolism",
    "Byzantine thrones **330–1204 CE** marry Roman imperial furniture protocol to Christian liturgy: emperors crowned on elevated thrones, bishops on ** synthronon** benches.",
    "Ivory plaques and manuscript miniatures supply silhouettes when Constantinople wood burns.",
    "Typology: **imperial throne**, **patriarchal seat**, **choir stall**.",
    "Timeline coarse across iconoclasm and Macedonian revival.",
    "Constantinople-centered schematic map.",
    "Do not invent Hagia Sophia furnishing details without primary liturgical texts.",
)

# 34–44
_p(
    "sasanian-silver-furniture",
    "Sasanian silver plates and vessels **224–651 CE** show banqueting and enthronement scenes; some scholars read them as furniture surrogates in metal.",
    "Rock reliefs add investiture thrones; wooden originals are lost.",
    "Typology links **ceremonial stool**, **banquet couch in relief**, **royal throne on platform**.",
    "Timeline from Ardashir through Arab conquest.",
    "Iran plateau schematic map.",
    "Metal survives; wooden frames are hypothetical beyond rivet clusters.",
)

_p(
    "islamic-early-seating",
    "Early Islamic courts **632–900 CE** favored portable cushions, folding chairs for authority, and low couches in Umayyad and Abbasid palaces. Damascus and Samarra frescoes show seated caliphs on rich textiles more than on fixed thrones.",
    "Byzantine and Sasanian inheritances merge in stool and throne protocol.",
    "Typology: **portable lectern**, **divan**, **folding enrobed seat**.",
    "Timeline crosses Rashidun through Abbasid foundation.",
    "Near East schematic map.",
    "Archaeological furniture rarer than literary court ceremony.",
)

_p(
    "oak-and-cedar-supply-chains",
    "Mediterranean furniture depended on **oak**, **cedar**, **cypress**, and imported **ebony** **2000 BCE–500 CE**. Supply chains appear in shipwreck cargoes, Assyrian tribute lists, and Roman tariff inscriptions.",
    "This essay is materials-forward: grain, season, and shipboard stowage shape what workshops could build.",
    "Typology by timber species and typical object class (bed vs. shrine door).",
    "Long timeline intentionally coarse.",
    "Basin-wide schematic map of forest zones—not modern deforestation data.",
    "Ecological claims need forestry archaeology; avoid retroactive sustainability moralizing.",
)

_p(
    "woodworking-tools-ancient",
    "Axes, adzes, bow drills, saws, and chisels from **3000 BCE–500 CE** appear in tool caches, tomb kits, and shipwright deposits. Tool marks on furniture fragments allow typological matching when wood survives.",
    "Cross-regional comparison shows Egyptian copper saws versus Roman iron tooth patterns.",
    "Typology plate groups tools by **cut**, **bore**, and **finish** functions.",
    "Timeline tracks metallurgical shifts affecting edge hardness.",
    "World schematic map for find spots cited in corpora.",
    "Tool alone does not prove furniture type; match marks cautiously.",
)

_p(
    "joinery-before-nails",
    "Before reliable iron nails dominated, furniture relied on **mortise-and-tenon**, pegs, dovetails, and hide glue **2500 BCE–500 CE**. Egyptian and Chinese examples preserve sophisticated joints without metal fasteners.",
    "Surviving frames from tombs and wells teach tolerances and seasonal wood movement.",
    "Typology diagrams joint families, not branded modern hardware.",
    "Timeline notes copper vs. iron nail adoption varies by region.",
    "Cross-regional map of exemplar sites.",
    "Replica builders should test peg shear; schematics omit load ratings.",
)

_p(
    "upholstery-bolsters-ancient",
    "Ancient **bolsters, cushions, and woven covers** **2000 BCE–500 CE** converted rigid frames into usable seats. Textiles rarely survive; tomb linens and impression marks on bronze couch fittings hint at stuffing.",
    "Symposium and triclinium culture depends on textile layer as much as wood.",
    "Typology: **bolster**, **mattress sack**, **draped cover**.",
    "Timeline tracks wool vs. linen prestige by region.",
    "Cross-regional schematic.",
    "Weak preservation biases argument toward Egypt and Pompeii.",
)

_p(
    "pigment-and-gilding-furniture",
    "Gilded furniture and painted surfaces **2000 BCE–500 CE** appear in tomb equipment, palace reliefs colored in antiquity, and lacquer traditions in China.",
    "Pigment analysis on fragments justifies reconstructions more than grayscale excavation photos.",
    "Typology by surface treatment: **leaf gilding**, **red ochre ground**, **polychrome lacquer**.",
    "Timeline notes technology transfers along trade routes.",
    "Cross-regional map.",
    "Do not assign specific pigment recipes without lab citations.",
)

_p(
    "furniture-in-tomb-inventory",
    "Tomb inventories in Egypt and the Near East **2000 BCE–500 CE** list beds, chairs, and chests with terms that lexicographers still map to morphotypes.",
    "Epigraphy supplies quantity and order of deposit; rarely dimensions.",
    "Typology ties **determinative shapes** to proposed furniture classes.",
    "Timeline spans Old Kingdom lists through Late Antique bilingual texts.",
    "Egypt / Near East schematic.",
    "Translation disagreements flagged rather than resolved by fiat.",
)

_p(
    "roman-furniture-prices-didactic",
    "Roman price lists, legal maxima, and school declamations **100 BCE–300 CE** mention furniture values in sesterces—didactic texts as much as market reality.",
    "Diocletian’s Price Edict entries for beds and couches anchor high-end benchmarks; satire supplies low-end ridicule.",
    "Typology by price band, not morphology alone.",
    "Timeline crosses Republic auction culture through late antique edicts.",
    "Empire schematic map for regional price variation caveats.",
    "Economics essay does not invent exact shop receipts.",
)

_p(
    "greek-vocabulary-furniture",
    "Greek literary vocabulary **800 BCE–200 CE** for beds, chairs, and couches feeds modern typology: **kline**, **klismos**, **thronos**, **skimpous**.",
    "Contexts span Homer, Aristophanes, inscriptions, and medical writers describing bed rest.",
    "Typology crosswalks terms to schematic morphotypes without claiming one-to-one archaeology.",
    "Timeline tracks Attic drama through Hellenistic koine spread.",
    "Hellenic world map.",
    "Philology disputes noted inline; no fake lexical citations.",
)

_p(
    "reconstruction-methods-museums",
    "Modern museums **1800–2026 CE** reconstruct ancient furniture using fragment mounts, extrapolation from reliefs, and controlled replication workshops.",
    "Methods diverge: minimalist armatures versus full experiential replicas for film.",
    "Typology of **display strategies**: ghost mount, partial restore, full replica labeled as such.",
    "Timeline of conservation ethics from plaster fills to reversible adhesives.",
    "Global museums schematic—not a directory of accession numbers.",
    "This meta-essay cites methodology literature; figures remain redrawn didactic plates, not gallery photos.",
)

WEAK_SLUGS = {
    "indus-valley-household-forms",
    "vedic-india-low-seating",
    "mauryan-palace-furniture",
    "chinese-kang-platform-beds",
    "korean-on-demand-platforms",
    "catacombs-funeral-furniture",
    "islamic-early-seating",
}
