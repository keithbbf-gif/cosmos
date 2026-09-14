#!/usr/bin/env python3
"""Download cleared portrait plates, write RIGHTS.md, embed SEO <figure> blocks."""
from __future__ import annotations

import re
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLATES = ROOT / "plates"
ART = ROOT / "articles"
SHARED_PENDING = ROOT / "assets" / "_shared" / "portrait-plate-pending.svg"
UA = "SLPWOW-AphasiaFigures/1.0 (educational pack; contact keith.bbf@gmail.com)"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_RE = re.compile(
    r"\n<figure class=\"slpwow-figure.*?</figure>\n",
    re.S,
)


@dataclass
class PlateSpec:
    plate_id: str
    cleared: bool
    download_url: str | None = None
    ext: str = "jpg"
    license: str = ""
    source_url: str = ""
    credit: str = ""
    figure_name: str = ""
    era_label: str = ""
    seo_sentence: str = ""
    alt: str = ""


# Cleared from Commons / NLM / Wellcome / BIU file pages (2026-09-14 pass).
CLEARED: dict[str, PlateSpec] = {
    "franz-joseph-gall": PlateSpec(
        plate_id="franz-joseph-gall",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/8/83/Franz_Joseph_Gall.jpg",
        license="Public domain",
        source_url="https://commons.wikimedia.org/wiki/File:Franz_Joseph_Gall.jpg",
        credit="Stipple engraving lettered “Le Dr Franc.-Jos. Gall.” Wikimedia Commons. Public domain.",
        figure_name="Franz Joseph Gall",
        era_label="late Enlightenment–Restoration era",
        seo_sentence="phrenology’s founder and the organology that preceded lesion neurology.",
        alt="Stipple engraving portrait of Franz Joseph Gall, late eighteenth-century physician.",
    ),
    "jean-baptiste-bouillaud": PlateSpec(
        plate_id="jean-baptiste-bouillaud",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/2/20/Bouillaud%2C_Jean-Baptiste_%281796-1881%29_CIPN21514.jpg",
        license="Licence Ouverte (BIU Santé)",
        source_url="https://commons.wikimedia.org/wiki/File:Bouillaud,_Jean-Baptiste_(1796-1881)_CIPN21514.jpg",
        credit="BIU Santé, Paris (CIPN21514). Licence Ouverte / Wikimedia Commons.",
        figure_name="Jean-Baptiste Bouillaud",
        era_label="July Monarchy era",
        seo_sentence="the clinician who argued speech sat in the frontal lobes before Broca’s 1861 autopsy.",
        alt="Portrait of Jean-Baptiste Bouillaud, nineteenth-century French physician.",
    ),
    "paul-broca": PlateSpec(
        plate_id="paul-broca",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/5/56/Paul_Broca.jpg",
        license="Public domain",
        source_url="https://commons.wikimedia.org/wiki/File:Paul_Broca.jpg",
        credit="Photograph by Pierre Petit. Wellcome Collection / Wikimedia Commons. Public domain.",
        figure_name="Pierre Paul Broca",
        era_label="Second Empire era",
        seo_sentence="surgeon-anthropologist tied to Leborgne’s 1861 Bicêtre autopsy and the third frontal convolution.",
        alt="Studio photograph of Paul Broca in dark coat, Second Empire style, by Pierre Petit.",
    ),
    "carl-wernicke": PlateSpec(
        plate_id="carl-wernicke",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/f/fe/C._Wernicke.jpg",
        license="Public domain (NLM IHM)",
        source_url="https://commons.wikimedia.org/wiki/File:C._Wernicke.jpg",
        credit="Published J. F. Lehmann, Munich. NLM Images from the History of Medicine. Public domain.",
        figure_name="Carl Wernicke",
        era_label="German Empire era",
        seo_sentence="author of the 1874 Breslau pamphlet that named sensory aphasia for the temporal lobe.",
        alt="Portrait photograph of Carl Wernicke, published by J. F. Lehmann.",
    ),
    "ludwig-lichtheim": PlateSpec(
        plate_id="ludwig-lichtheim",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/9/98/Ludwig_Lichtheim.jpg",
        license="Public domain (NLM IHM; pub. 1925 U.S.)",
        source_url="https://commons.wikimedia.org/wiki/File:Ludwig_Lichtheim.jpg",
        credit="J. F. Lehmann, Munich, 1925. NLM IHM. Public domain in the United States.",
        figure_name="Ludwig Lichtheim",
        era_label="Wilhelmine–Weimar era",
        seo_sentence="Breslau professor whose 1885 “house diagram” mapped conduction aphasia.",
        alt="Portrait of Ludwig Lichtheim, early twentieth-century German neurologist.",
    ),
    "john-hughlings-jackson": PlateSpec(
        plate_id="john-hughlings-jackson",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/3/3e/John_Hughlings_Jackson.jpg",
        license="Public domain (NLM IHM)",
        source_url="https://commons.wikimedia.org/wiki/File:John_Hughlings_Jackson.jpg",
        credit="Photogravure after Lance Calkin, 1895. NLM / Wikimedia Commons. Public domain.",
        figure_name="John Hughlings Jackson",
        era_label="Victorian neurology era",
        seo_sentence="Queen Square neurologist who reframed language as hierarchical nervous process.",
        alt="Photogravure portrait of John Hughlings Jackson after Lance Calkin, 1895.",
    ),
    "henry-head": PlateSpec(
        plate_id="henry-head",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/c/cb/Henry_Head.jpg",
        license="Public domain (Commons; NLM IHM)",
        source_url="https://commons.wikimedia.org/wiki/File:Henry_Head.jpg",
        credit="Theodore C. Marceau (1859–1922). NLM IHM. Stated public domain on Wikimedia Commons.",
        figure_name="Henry Head",
        era_label="Edwardian neurology era",
        seo_sentence="physician who paired nerve injury with aphasia studies alongside W.H.R. Rivers.",
        alt="Portrait photograph of Henry Head by Theodore C. Marceau.",
    ),
    "pierre-marie": PlateSpec(
        plate_id="pierre-marie",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/d/d1/Pierre_Marie.jpg",
        license="CC BY-SA 4.0",
        source_url="https://commons.wikimedia.org/wiki/File:Pierre_Marie.jpg",
        credit="Wikimedia Commons contributors. CC BY-SA 4.0 — attribute on reuse; share alike if adapted.",
        figure_name="Pierre Marie",
        era_label="Third Republic–early twentieth century",
        seo_sentence="Salpêtrière neurologist whose 1906 revision challenged narrow Broca–Wernicke maps.",
        alt="Portrait photograph of Pierre Marie, French neurologist, early twentieth century.",
    ),
    "jules-dejerine": PlateSpec(
        plate_id="jules-dejerine",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/3/3b/Jules_Dejerine.jpg",
        license="Public domain",
        source_url="https://commons.wikimedia.org/wiki/File:Jules_Dejerine.jpg",
        credit="Wikimedia Commons. Public domain.",
        figure_name="Jules Déjerine",
        era_label="Belle Époque neurology era",
        seo_sentence="anatomist-clinician of the Déjerine clinic and alexia without agraphia.",
        alt="Portrait of Jules Déjerine, French neurologist, late nineteenth century.",
    ),
    "augusta-dejerine-klumpke": PlateSpec(
        plate_id="augusta-dejerine-klumpke",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/7/7b/Augusta_D%C3%A9jerine-Klumpke.jpg",
        license="Public domain (NLM IHM)",
        source_url="https://commons.wikimedia.org/wiki/File:Augusta_D%C3%A9jerine-Klumpke.jpg",
        credit="NLM Images from the History of Medicine. Wikimedia Commons. Public domain.",
        figure_name="Augusta Déjerine-Klumpke",
        era_label="Belle Époque–early twentieth century",
        seo_sentence="neurologist and co-director of the Déjerine clinic, not merely “Mrs. Déjerine.”",
        alt="Portrait of Augusta Déjerine-Klumpke, neurologist, late nineteenth century.",
    ),
    "jacques-lordat": PlateSpec(
        plate_id="jacques-lordat",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/8/8f/Jacques_Lordat.jpg",
        license="CC BY-SA 4.0",
        source_url="https://commons.wikimedia.org/wiki/File:Jacques_Lordat.jpg",
        credit="Jean-Baptiste-Adolphe Lafosse, after an earlier plate. Wikimedia Commons. CC BY-SA 4.0.",
        figure_name="Jacques Lordat",
        era_label="Restoration–July Monarchy era",
        seo_sentence="Montpellier professor who published one of the first modern aphasia self-reports (1843).",
        alt="Engraved portrait of Jacques Lordat by Jean-Baptiste-Adolphe Lafosse.",
    ),
    "theophile-alajouanine": PlateSpec(
        plate_id="theophile-alajouanine",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/8/80/Th%C3%A9ophile_Alajouanine.png",
        ext="png",
        license="CC0 1.0",
        source_url="https://commons.wikimedia.org/wiki/File:Th%C3%A9ophile_Alajouanine.png",
        credit="Courrier royal, via Retronews / Wikimedia Commons. CC0 1.0.",
        figure_name="Théophile Alajouanine",
        era_label="interwar French neurology era",
        seo_sentence="Salpêtrière clinician linked to transcortical aphasia and wartime rehabilitation.",
        alt="Portrait of Théophile Alajouanine from Courrier royal, 1930s press plate.",
    ),
    "aleksandr-luria": PlateSpec(
        plate_id="aleksandr-luria",
        cleared=True,
        download_url="https://upload.wikimedia.org/wikipedia/commons/6/67/Alexander_Luria.jpg",
        license="Public domain (Commons-stated; photographer unknown)",
        source_url="https://commons.wikimedia.org/wiki/File:Alexander_Luria.jpg",
        credit="c. 1940s. Photographer unknown. Wikimedia Commons. Stated public domain.",
        figure_name="Aleksandr R. Luria",
        era_label="Soviet–postwar neuropsychology era",
        seo_sentence="neuropsychologist who rebuilt aphasia assessment after wartime brain injuries.",
        alt="Portrait photograph of Aleksandr Luria, circa 1940s.",
    ),
}

# Article slug -> plate_id (defaults to slug)
SLUG_TO_PLATE: dict[str, str] = {
    "weisenburg-and-mcbride": "weisenburg-and-mcbride",
}

PLACEHOLDER_SEO: dict[str, tuple[str, str, str]] = {
    "johann-gesner": (
        "Johann A. P. Gesner",
        "Enlightenment medicine era",
        "eighteenth-century Göttingen professor who named early speech-loss cases.",
    ),
    "kurt-goldstein": (
        "Kurt Goldstein",
        "interwar organismic neurology era",
        "Berlin–New York neurologist of holistic brain injury and language loss.",
    ),
    "weisenburg-and-mcbride": (
        "Theodore Weisenburg and Katharine McBride",
        "interwar American aphasiology era",
        "Philadelphia neurologist and Bryn Mawr psychologist behind the 1935 *Aphasia* volume.",
    ),
    "joseph-wepman": (
        "Joseph M. Wepman",
        "mid-century Chicago assessment era",
        "psychologist who shaped naming and repetition tests after World War II.",
    ),
    "hildred-schuell": (
        "Hildred Schuell",
        "Minnesota VA postwar era",
        "clinician whose stimulation hierarchy dominated U.S. aphasia therapy for decades.",
    ),
    "jon-eisenson": (
        "Jon Eisenson",
        "mid-century diagnostic batteries era",
        "author of early standardized aphasia examinations used in training clinics.",
    ),
    "harold-goodglass": (
        "Harold Goodglass",
        "Boston VA aphasia research era",
        "co-creator of the Boston Diagnostic Aphasia Examination and the Aphasia Bank.",
    ),
    "edith-kaplan": (
        "Edith Kaplan",
        "Boston process neuropsychology era",
        "clinician who argued tests must be interpreted as process, not single scores.",
    ),
    "norman-geschwind": (
        "Norman Geschwind",
        "1960s–1970s disconnection neurology era",
        "Harvard neurologist who revived associationist maps for language and alexia.",
    ),
    "andrew-kertesz": (
        "Andrew Kertesz",
        "late twentieth-century Western aphasia battery era",
        "neurologist behind the Western Aphasia Battery and aphasia classification work.",
    ),
    "martha-taylor-sarno": (
        "Martha Taylor Sarno",
        "NYU Rusk rehabilitation era",
        "speech-language pathologist who documented long-term aphasia recovery.",
    ),
    "audrey-holland": (
        "Audrey Holland",
        "life-participation aphasia era",
        "researcher who moved aphasia outcomes toward communication in daily life.",
    ),
    "macdonald-critchley": (
        "Macdonald Critchley",
        "Queen Square twentieth-century era",
        "British neurologist and historian of aphasia and parietal syndromes.",
    ),
    "wilder-penfield": (
        "Wilder Penfield",
        "Montreal cortical stimulation era",
        "neurosurgeon whose mapped cortex linked language to exposed brain in the OR.",
    ),
    "marsel-mesulam": (
        "M. Marsel Mesulam",
        "primary progressive aphasia era",
        "Northwestern neurologist who framed PPA as a clinicopathologic syndrome.",
    ),
    "roman-jakobson": (
        "Roman Jakobson",
        "structural linguistics era",
        "linguist whose aphasia typology influenced neurology and speech pathology.",
    ),
}


def parse_front(text: str) -> tuple[dict[str, str], str, str]:
    m = FRONT_RE.match(text)
    if not m:
        return {}, text, ""
    block = m.group(1)
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    rest = text[m.end() :]
    return data, rest, m.group(0)


def write_rights(path: Path, spec: PlateSpec, life_dates: str, status: str) -> None:
    lines = [
        f"# Rights — {spec.plate_id} plate",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| figure | {spec.figure_name} |",
        f"| life_dates | {life_dates} |",
        f"| era | {spec.era_label} |",
        f"| status | {status} |",
        f"| file | plate.{spec.ext if spec.cleared else 'svg'} |",
        f"| ai_generated | no |",
        f"| ingested | 2026-09-14 |",
    ]
    if spec.cleared:
        lines.extend(
            [
                f"| license | {spec.license} |",
                f"| source | Wikimedia Commons / NLM / Wellcome / BIU (see source_url) |",
                f"| source_url | {spec.source_url} |",
                f"| credit_line | {spec.credit} |",
            ]
        )
    else:
        lines.extend(
            [
                "| license | not cleared for redistribution |",
                "| source | — |",
                "| source_url | — |",
                "| credit_line | Portrait placeholder — hunt open in PORTRAIT_SOURCES.md |",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    dest.write_bytes(data)


def figure_html(spec: PlateSpec, life_dates: str, cleared: bool) -> str:
    if cleared:
        src = f"../plates/{spec.plate_id}/plate.{spec.ext}"
        return f"""
<figure class="slpwow-figure slpwow-figure--portrait">
  <img
    src="{src}"
    alt="{spec.alt}"
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>{spec.figure_name}</strong> ({life_dates}), {spec.era_label} — {spec.seo_sentence}
    <span class="figure-credit">{spec.credit}</span>
  </figcaption>
</figure>
"""
    src = f"../plates/{spec.plate_id}/plate.svg"
    name = spec.figure_name
    return f"""
<figure class="slpwow-figure slpwow-figure--portrait slpwow-figure--portrait-pending">
  <img
    src="{src}"
    alt="Portrait pending — rights not cleared for {name}."
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>{spec.figure_name}</strong> ({life_dates}), {spec.era_label} — {spec.seo_sentence}
    <em>Portrait placeholder — rights not cleared.</em>
    See <code>plates/{spec.plate_id}/RIGHTS.md</code> and <code>PORTRAIT_SOURCES.md</code>.
  </figcaption>
</figure>
"""


def placeholder_spec(plate_id: str, life_dates: str) -> PlateSpec:
    name, era, seo = PLACEHOLDER_SEO[plate_id]
    return PlateSpec(
        plate_id=plate_id,
        cleared=False,
        figure_name=name,
        era_label=era,
        seo_sentence=seo,
        alt="",
    )


def ingest_plates() -> None:
    PLATES.mkdir(parents=True, exist_ok=True)
    for plate_id, spec in CLEARED.items():
        folder = PLATES / plate_id
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / f"plate.{spec.ext}"
        if spec.download_url:
            print(f"download {plate_id} …")
            download(spec.download_url, dest)
        write_rights(folder / "RIGHTS.md", spec, "see article figure_dates", "cleared")

    for plate_id in PLACEHOLDER_SEO:
        if plate_id in CLEARED:
            continue
        folder = PLATES / plate_id
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SHARED_PENDING, folder / "plate.svg")
        spec = placeholder_spec(plate_id, "")
        write_rights(folder / "RIGHTS.md", spec, "see article figure_dates", "placeholder — rights not cleared")


def patch_articles() -> None:
    for path in sorted(ART.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, body, front_block = parse_front(text)
        if fm.get("type") != "profile":
            continue
        slug = fm.get("slug", "")
        plate_id = SLUG_TO_PLATE.get(slug, slug)
        life_dates = fm.get("figure_dates", "")
        if plate_id in CLEARED:
            spec = CLEARED[plate_id]
            cleared = True
            portrait_val = f"plates/{plate_id}/plate.{spec.ext}"
            status = "cleared"
        elif plate_id in PLACEHOLDER_SEO:
            spec = placeholder_spec(plate_id, life_dates)
            cleared = False
            portrait_val = f"plates/{plate_id}/plate.svg"
            status = "placeholder"
        else:
            print(f"skip unknown profile {path.name}")
            continue

        write_rights(PLATES / plate_id / "RIGHTS.md", spec, life_dates, status)

        fig = figure_html(spec, life_dates, cleared)
        body = FIGURE_RE.sub("\n", body)
        needle = "not a substitute for care with a licensed clinician."
        idx = body.find(needle)
        if idx == -1:
            print(f"WARN no disclaimer in {path.name}")
            continue
        insert_at = idx + len(needle)
        body = body[:insert_at] + "\n" + fig + body[insert_at:]

        new_front = front_block
        new_front = re.sub(
            r"^portrait:.*$",
            f'portrait: "{portrait_val}"',
            new_front,
            count=1,
            flags=re.M,
        )
        new_front = re.sub(
            r"^portrait_status:.*$",
            f"portrait_status: {status}",
            new_front,
            count=1,
            flags=re.M,
        )
        path.write_text(new_front + body, encoding="utf-8")
        print(f"patched {path.name}")


def main() -> None:
    if not SHARED_PENDING.is_file():
        raise SystemExit("missing shared pending SVG")
    ingest_plates()
    patch_articles()
    print("done")


if __name__ == "__main__":
    main()
