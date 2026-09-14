#!/usr/bin/env python3
"""Insert lead <figure> blocks and SEO frontmatter from REGISTRY.toml + ASSIGNMENTS."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets" / "figures" / "REGISTRY.toml"
DRAFTS = ROOT / "drafts"

# essay_id -> (plate_key, alt, caption prose before Rights line, meta_description)
ASSIGNMENTS: dict[str, tuple[str, str, str, str]] = {
    "eahp-00": (
        "ming-contents-wellcome",
        "Ming-era Chinese materia medica contents page in vertical script",
        "Contents page from a Ming materia medica manuscript in the Wellcome Collection — a map of how a pharmacopeia-shaped book announces its rooms before the reader reaches any single drug.",
        "How to read the East Asian herbal pharmacopeia drafts: method, limits, and claims-guarded history of bencao, honzō, and hyangyak books.",
    ),
    "eahp-01": (
        "gangmu-1603-spread-1",
        "1603 woodblock spread from the Compendium of Materia Medica (Bencao gangmu)",
        "Printed opening from a 1603 Jiangxi-line recut of Li Shizhen’s Bencao gangmu — a late-Ming state of the art in classified materia medica, not a modern legal pharmacopeia.",
        "What counts as a pharmacopeia in East Asia: court bencao, private encyclopedias, and later ministry codes compared without clinical advice.",
    ),
    "eahp-02": (
        "acupuncture-prohibitions-wellcome",
        "Ming woodcut listing acupuncture prohibitions in Chinese script",
        "Ming woodcut on acupuncture prohibitions — an example of how historical medical books encode caution in print. The image documents a text’s warnings, not safe practice for a modern reader.",
        "The claims guard for this collection: dates, attributions, UNESCO prose, and why historical use is not efficacy.",
    ),
    "eahp-03": (
        "gangmu-1603-spread-2",
        "Second spread of 1603 Bencao gangmu woodblock pages with Chinese characters",
        "Facing pages from the 1603 Compendium of Materia Medica print show mixed scripts and repeated book titles — a reminder that romanization choices in these drafts are editorial, not stamped on the block.",
        "Names, scripts, and romanization for Chinese bencao, Japanese honzō, and Korean hyangyak titles in historical context.",
    ),
    "eahp-04": (
        "ming-trifoliate-wellcome",
        "Ming materia medica color illustration of trifoliate orange and related plants",
        "Ming plate in the Bencao gangmu illustration tradition (trifoliate orange and related items). Transmission between China, Japan, and Korea is argued in text, not assumed from a shared picture style.",
        "Why East Asian materia medica traditions are related in script and citation but not one pipeline from Shennong to modern pharmacopeias.",
    ),
    "eahp-05": (
        "shennong-woodcut-wellcome",
        "Ming woodcut of the culture hero Shen Nong from a pharmacopeia portrait series",
        "Legendary culture hero Shen Nong in a Ming-period woodcut from the Bencao mengquan portrait series — legendary attribution on a title page, not evidence of a Han author with a camera.",
        "Shennong as culture hero and legendary byline on the Shennong bencao jing, without treating myth as authorship.",
    ),
    "eahp-06": (
        "ming-cinnabar-wellcome",
        "Ming illustration of cinnabar mineral drug in Chinese materia medica style",
        "Ming illustration for cinnabar (vermilion ore) in a materia medica set. Historical texts classified and depicted substances; they did not perform modern toxicology.",
        "Reconstructing the Shennong bencao jing from later quotations: what scholars can and cannot prove about a Han original.",
    ),
    "eahp-07": (
        "gangmu-mineral-panel",
        "Mineral drug illustrations from the Bencao gangmu tradition",
        "Mineral-drug panel from the Bencao gangmu illustration tradition — upper, middle, and lower grades in the literature were moral and administrative categories, not modern safety tiers.",
        "Upper, middle, and lower drug grades in early bencao as a classification machine, without dosing or treatment claims.",
    ),
    "eahp-08": (
        "ming-huangqin-wellcome",
        "Ming materia medica painting of huangqin (Scutellaria root)",
        "Ming painted plate for huangqin (Scutellaria) — the kind of image Tao Hongjing’s commentary tradition inherited and rearranged in red and black text layers.",
        "Tao Hongjing, the Bencao jing jizhu, and how Six Dynasties commentary shaped later imperial bencao.",
    ),
    "eahp-09": (
        "ming-mallow-wellcome",
        "Ming illustration of cluster mallow plant in Chinese materia medica style",
        "Cluster mallow plate from a Ming materia medica set — an extra-drug world like the Mingyi bielu line lives in names and omissions as much as in a single picture.",
        "Mingyi bielu and supplementary drug literature outside the core Shennong list in early Chinese pharmaceutics.",
    ),
    "eahp-10": (
        "ming-honey-wellcome",
        "Ming illustration labeled Sichuan honey in a materia medica series",
        "Sichuan honey in a Ming materia medica illustration — food and drug share a shelf in many East Asian books; the image shows classification, not a nutrition recommendation.",
        "Food as drug in early Chinese materia medica and the road toward Tang court pharmacopeia projects.",
    ),
    "eahp-11": (
        "wen-shu-copy-plate",
        "Qing painting copying metals, minerals, insects, and plants after materia medica models",
        "Wen Shu’s Jin shi kun chong cao mu zhuang (Library of Congress WDL) copies earlier materia medica models — evidence of how pictures travel as arguments across centuries.",
        "Food, tribute, and materia medica on the road to the Tang court’s pharmaceutical projects.",
    ),
    "eahp-12": (
        "gangmu-plate-insects",
        "Circa 1800 printed plate of insects and plants after Bencao gangmu",
        "Insect and plant plate from a circa-1800 copy after the Bencao gangmu — the Tang Xinxiu bencao’s lost color paintings survive only through later image traditions like this one.",
        "Xinxiu bencao (659): the Tang state’s Newly Revised Materia Medica as government product and bibliographic event.",
    ),
    "eahp-13": (
        "ishinpo-title",
        "Title page of Ishinpō Heart of Medicine Japanese medical encyclopedia",
        "Title page from the Ishinpō (Heart of Medicine) tradition — Japan’s surviving witness to Tang materia medica that China often meets only through fragments and quotations.",
        "What survives of early Chinese imperial bencao: Japanese copies, Dunhuang fragments, and reconstruction limits.",
    ),
    "eahp-14": (
        "ming-cardamom-wellcome",
        "Ming illustration of Yizhou cardamom in Chinese materia medica",
        "Cardamom of Yizhou in a Ming materia medica plate — Chen Cangqi’s lost Bencao shiyi survives in quoted names and traces, not in a single intact Song print like this Ming set.",
        "Chen Cangqi and Bencao shiyi: recovered fragments and Kaiyuan-era supplement literature.",
    ),
    "eahp-15": (
        "gangmu-1603-spread-2",
        "1603 Bencao gangmu woodblock pages",
        "1603 printed pages from the Bencao gangmu line — the Kaibao bencao (973/974) began the Song official print story this spread continues as bibliography, not as the Kaibao itself.",
        "Kaibao bencao and Song official printing of materia medica in the tenth century.",
    ),
    "eahp-16": (
        "gangmu-plate-insects",
        "Printed herbal plate with insects and plants in Chinese materia medica style",
        "Prefectural illustration ambitions of Su Song’s Bencao tujing (1061) echo in later plates like this copy-chain insect spread — image-tradition, not a surviving 1061 painting.",
        "Su Song’s Bencao tujing: prefectural pictures and the illustrated classic presented in 1061.",
    ),
    "eahp-17": (
        "ming-trifoliate-wellcome",
        "Ming color plate of trifoliate orange from Bencao gangmu illustration line",
        "Trifoliate orange plate from the Ming Bencao gangmu illustration line — Tang Shenwei’s Zhenglei bencao is the private encyclopedia that carried such pictures into everyday Ming use.",
        "Tang Shenwei and the Zhenglei bencao recensions that Ming readers actually opened.",
    ),
    "eahp-18": (
        "ming-plant-drugs-c17-wellcome",
        "17th-century Chinese plant-drug illustration sheet from Wellcome Collection",
        "Seventeenth-century plant-drug sheet — Liu Wentai’s Bencao pinhui jingyao (1505) was an official color herbal that court politics kept from wide print; later copies carry its visual ambition.",
        "Bencao pinhui jingyao (1505): Ming official color herbal completed but not promulgated like a modern code.",
    ),
    "eahp-19": (
        "gangmu-1603-spread-1",
        "1603 Compendium of Materia Medica woodblock opening",
        "1603 opening spread of the Bencao gangmu — read Li Shizhen through the workshop colophon and print, not through a modern bronze statue.",
        "Li Shizhen without monument mythology: dates, family labor, and the Bencao gangmu as workshop encyclopedia.",
    ),
    "eahp-20": (
        "gangmu-mineral-panel",
        "Mineral drugs illustrated in Bencao gangmu style panel",
        "Mineral panel from the Bencao gangmu reading-machine — sixteen departments and fixed inner slots on the page, pictured here as materia, not as instructions.",
        "Bencao gangmu as a machine for reading: gang, mu, sixteen bu, and slots for doubt.",
    ),
    "eahp-21": (
        "gangmu-1603-spread-1",
        "Jinling and Jiangxi line Bencao gangmu 1603 woodblock spread",
        "1603 Jiangxi-line spread — Jinling (Wanli-era) and Jiangxi recuts are the edition fight this draft tracks; the page is evidence of print, not of clinical authority today.",
        "Jinling, Jiangxi, and the late-Ming print geography of Li Shizhen’s Bencao gangmu.",
    ),
    "eahp-22": (
        "gangmu-plate-insects",
        "Later copy plate after Bencao gangmu with plants and insects",
        "Later copy plate — Zhao Xuemin’s Bencao gangmu shiyi (1765) picks up omissions from a book already circulating with pictures like this chain.",
        "Zhao Xuemin and Bencao gangmu shiyi: Qing supplement literature after Li Shizhen’s encyclopedia.",
    ),
    "eahp-23": (
        "ishinpo-ninnaji",
        "Manuscript page from Ishinpō Ninna-ji line Japanese medical text",
        "Ishinpō manuscript page (Ninna-ji line) — Japan receives Tang materia medica as a foreign library problem before Edo naturalists rename plants locally.",
        "Tang materia medica as a Japanese problem: citation, shortage, and kundoku reading.",
    ),
    "eahp-24": (
        "ishinpo-title",
        "Ishinpō title page oldest extant Japanese medical encyclopedia tradition",
        "Ishinpō title page — Fukane no Sukehito’s Honzō wamyō (early tenth century) names drugs in Japanese before this 984 encyclopedia quotes Chinese bencao at length.",
        "Honzō wamyō: Japan’s early pharmaceutical name-book in the Engi era.",
    ),
    "eahp-25": (
        "ishinpo-ninnaji",
        "Heian-period Ishinpō manuscript page Tokyo National Museum tradition",
        "Ninna-ji line Ishinpō page — Tanba Yasuyori’s 984 encyclopedia preserves Chinese materia medica quotations; vol. 30 is the honzō room this draft discusses.",
        "Ishinpō (984): Japan’s oldest surviving medical encyclopedia and its materia medica volume.",
    ),
    "eahp-26": (
        "yamato-honzo-page",
        "Printed page from Yamato honzō Japanese materia medica",
        "Page from the Yamato honzō line associated with Kaibara Ekiken — Edo readers compare Chinese faces on the page to plants on Japanese mountains.",
        "Medieval and early Edo honzō literature between Chinese citation and local naming.",
    ),
    "eahp-27": (
        "gangmu-1603-spread-2",
        "1603 Bencao gangmu pages imported into Japanese reading",
        "1603 gangmu pages — Hayashi Razan’s introduction of the Bencao gangmu to Japanese scholarly reading in 1607 sits in a print culture this spread represents.",
        "Hayashi Razan and the Bencao gangmu’s entry into Tokugawa scholarly reading.",
    ),
    "eahp-28": (
        "yamato-honzo-page",
        "Yamato honzō printed page with Japanese plant names",
        "Yamato honzō page — Kaibara Ekiken’s text (1708/1709) and later picture volumes argue which items are Yamato honzō versus Chinese imports.",
        "Kaibara Ekiken’s Yamato honzō: local plants, Chinese titles, and Edo pictures.",
    ),
    "eahp-29": (
        "ming-plant-drugs-c17-wellcome",
        "17th-century East Asian plant-drug illustration sheet",
        "Plant-drug sheet — Ono Ranzan’s Honzō kōmoku keimō (1803–1806) belongs to the same picture-heavy Edo moment as surviving illustrated materia medica pages.",
        "Ono Ranzan and late Edo honzō scholarship after Kaibara Ekiken.",
    ),
    "eahp-30": (
        "gangmu-1603-spread-1",
        "East Asian materia medica woodblock pages before Meiji pharmacopeia",
        "Pre-Meiji woodblock spread — the Nihon yakkyokuhō (1886) replaces this bookish world with a ministry monograph list; the image is the old object, not the 1886 statute.",
        "Nihon yakkyokuhō (1886): Meiji Japan’s first legal pharmacopeia and the break from honzō books.",
    ),
    "eahp-31": (
        "donguibogam-cover",
        "Donguibogam Korean medical encyclopedia cover or opening",
        "Donguibogam cover — hyangyak policy begins as Joseon insistence on local names before this royal encyclopedia absorbs Chinese shelves.",
        "Hyangyak as politics: local herbs, court budgets, and Joseon identity claims.",
    ),
    "eahp-32": (
        "donguibogam-ko-page",
        "Korean woodblock page from Donguibogam scan",
        "Donguibogam woodblock page — the Hyangyak gugeupbang (1236/1417 lines) is earlier vernacular emergency materia medica this later print culture echoes.",
        "Hyangyak gugeupbang: Goryeo and Joseon emergency formulary and surviving Tokyo copy.",
    ),
    "eahp-33": (
        "donguibogam-page-en",
        "Printed page from Donguibogam Tongui bogam",
        "Printed Donguibogam page — Goryeo-to-Joseon shifts in materia medica are argued from office and reprint, not from a single illustration.",
        "From Goryeo to Joseon: reprints, offices, and hyangyak continuities.",
    ),
    "eahp-34": (
        "donguibogam-ko-page",
        "Korean materia medica woodblock page from Joseon encyclopedia tradition",
        "Joseon woodblock page — Hyangyak jipseongbang (1433) belongs to the same local-herb compilation century as surviving printed pages.",
        "Hyangyak jipseongbang (1433): early Joseon local-herb formulary in standard narratives.",
    ),
    "eahp-35": (
        "donguibogam-page-en",
        "Donguibogam encyclopedia page with Korean and Chinese medical text",
        "Donguibogam page — Uibang yuchwi (finished 1445) is the larger royal collation whose materia medica rooms this print culture later summarizes.",
        "Uibang yuchwi (1445/1477): Joseon royal medical encyclopedia and collation politics.",
    ),
    "eahp-36": (
        "donguibogam-cover",
        "Donguibogam UNESCO Memory of the World Korean medical encyclopedia",
        "Donguibogam opening — Heo Jun’s royal commission (printed 1613) is a Joseon encyclopedia; UNESCO files document holdings, not clinical efficacy.",
        "Donguibogam: Heo Jun, Seonjo’s court, and the 1613 Naeuiwon print.",
    ),
    "eahp-37": (
        "donguibogam-ko-page",
        "Korean medical woodblock page after Heo Jun era",
        "Post–Heo Jun woodblock page — later Joseon readers inherit Donguibogam as a shelf, not as a single author’s notebook.",
        "Korean materia medica after Heo Jun: reprints, commentaries, and colonial pressure.",
    ),
    "eahp-38": (
        "donguibogam-page-en",
        "Donguibogam printed page as historical Korean medical book",
        "Donguibogam page — modern Korean Pharmacopeia (KP, from 1958) and colonial cuts are twentieth-century statutes, not extensions of this woodblock.",
        "Modern Korean pharmacopeias, KP/KHP, and the colonial rupture in hanui.",
    ),
    "eahp-39": (
        "ming-honey-wellcome",
        "Ming materia medica illustration of honey — tribute trade good",
        "Sichuan honey plate — tribute and trade moved materia medica names across East Asia; the picture is a commodity face, not proof of therapeutic effect.",
        "Tribute, trade, and the object-life of drugs between Chinese, Japanese, and Korean books.",
    ),
    "eahp-40": (
        "gangmu-plate-insects",
        "Herbal picture plate where image argues for plant identity",
        "Picture plate from a bencao copy-chain — illustrations argue that a name has a visible form; they are claims that need citations, not substitutes for them.",
        "Pictures that argue in bencao, tujing, and later pharmacopeia illustration traditions.",
    ),
    "eahp-41": (
        "ming-cinnabar-wellcome",
        "Ming illustration of cinnabar — toxic drug in historical literature",
        "Cinnabar plate — aconite and cinnabar appear in lower-grade and mineral chapters; historical presence documents textual classification, not safe use.",
        "Poison, dose language, and upper/lower drugs in official East Asian materia medica.",
    ),
    "eahp-42": (
        "acupuncture-prohibitions-wellcome",
        "Ming medical woodcut on prohibited practices",
        "Prohibitions woodcut — official books omit midwives, markets, and household practice; what survives in print is a filtered slice of pharmacopeia-shaped knowledge.",
        "What official pharmacopeias and materia medica books leave out of the record.",
    ),
    "eahp-43": (
        "gangmu-1603-spread-2",
        "East Asian woodblock materia medica pages beside modern ministry codes",
        "1603 gangmu spread — Zhonghua yaodian (1930/1931), Nihon yakkyokuhō, and Korean Pharmacopeia are ministry objects unlike this Ming book.",
        "Three modern East Asian pharmacopeia codes: Republican China, Meiji Japan, and Korean KP.",
    ),
    "eahp-44": (
        "ming-contents-wellcome",
        "Ming materia medica contents page — limits of the collection",
        "Ming contents page — this draft collection stops at staged essays; the page marks a bookshelf door, not a finished history or clinical guide.",
        "What this East Asian herbal pharmacopeia draft collection cannot do: clinical advice, efficacy, or complete bibliography.",
    ),
}

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)
FIGURE_MARK = "<!-- eahp-figure:v1 -->"


def load_plates() -> dict[str, dict]:
    data = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for key, val in data.get("plates", {}).items():
        out[key] = val
    return out


def rights_line(plate: dict) -> str:
    return (
        f"{plate['license']}; {plate['institution']}; "
        f"<a href=\"{plate['source_page']}\">source</a>. {plate['credit']}"
    )


def figure_html(plate: dict, alt: str, caption: str) -> str:
    w = plate.get("width", 1200)
    h = plate.get("height", 900)
    rights = rights_line(plate)
    return (
        f"{FIGURE_MARK}\n"
        f'<figure class="eahp-figure">\n'
        f'  <img src="{plate["src"]}" alt="{alt}" width="{w}" height="{h}" '
        f'loading="lazy" decoding="async"/>\n'
        f"  <figcaption><strong>Fig. 1.</strong> {caption} "
        f"<em>Rights:</em> {rights}</figcaption>\n"
        f"</figure>\n"
    )


def patch_frontmatter(fm: str, essay_id: str, plate_key: str, meta: str) -> str:
    lines = fm.splitlines()
    kv = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M))
    kv["meta_description"] = meta.replace('"', '\\"')
    if not kv["meta_description"].startswith('"'):
        kv["meta_description"] = f'"{kv["meta_description"]}"'
    kv["figure_id"] = f"plates.{plate_key}"
    kv["image_rights"] = "documented"
    kv["image_pass"] = "2026-09-14"
    order = [
        "id",
        "collection",
        "title",
        "stage",
        "stage_name",
        "status",
        "sequence",
        "jurisdictions",
        "period",
        "claims_guard",
        "voice",
        "meta_description",
        "figure_id",
        "image_rights",
        "image_pass",
    ]
    seen = set()
    new_lines: list[str] = []
    for key in order:
        if key in kv:
            new_lines.append(f"{key}: {kv[key]}")
            seen.add(key)
    for key, val in kv.items():
        if key not in seen:
            new_lines.append(f"{key}: {val}")
    return "\n".join(new_lines)


def embed_file(path: Path, plates: dict[str, dict]) -> bool:
    raw = path.read_text(encoding="utf-8")
    m = FRONT.match(raw)
    if not m:
        print(f"skip (no frontmatter): {path}", file=sys.stderr)
        return False
    fm = m.group(1)
    body = raw[m.end() :]
    essay_id = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M)).get("id", "").strip()
    if essay_id not in ASSIGNMENTS:
        print(f"skip (no assignment): {essay_id} {path}", file=sys.stderr)
        return False
    plate_key, alt, caption, meta = ASSIGNMENTS[essay_id]
    plate = plates[plate_key]
    fig = figure_html(plate, alt, caption)
    if FIGURE_MARK in body:
        body = re.sub(
            rf"{re.escape(FIGURE_MARK)}.*?</figure>\n",
            fig,
            body,
            count=1,
            flags=re.S,
        )
    else:
        lines = body.splitlines()
        out: list[str] = []
        inserted = False
        for i, line in enumerate(lines):
            out.append(line)
            if not inserted and line.startswith("# "):
                out.append("")
                out.append(fig.rstrip())
                out.append("")
                inserted = True
        body = "\n".join(out) + ("\n" if body.endswith("\n") else "")
    new_fm = patch_frontmatter(fm, essay_id, plate_key, meta)
    path.write_text(f"---\n{new_fm}\n---{body}", encoding="utf-8")
    return True


def main() -> int:
    plates = load_plates()
    missing = {k for k, (pk, *_) in ASSIGNMENTS.items() if pk not in plates}
    if missing:
        print("registry missing plates for:", missing, file=sys.stderr)
        return 2
    n = 0
    for path in sorted(DRAFTS.rglob("*.md")):
        if embed_file(path, plates):
            n += 1
    print(f"embedded figures in {n} drafts")
    return 0 if n == len(ASSIGNMENTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
