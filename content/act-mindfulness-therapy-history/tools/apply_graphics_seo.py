#!/usr/bin/env python3
"""One-shot SEO + figure embed pass. Idempotent if re-run (skips existing figures)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)

FIG01 = """<figure class="wow-act-figure wow-act-figure--timeline">
  <img
    src="../../graphics/fig-01-document-milestones.svg"
    alt="Timeline of selected publications and programs from 1979 to 2009 in ACT and mindfulness-based therapy history."
    width="1200"
    height="520"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 1</strong> — Selected document and program dates (not treatment-outcome claims).
    <span class="figure-credit">Original diagram, WOW Therapies educational series.</span>
  </figcaption>
</figure>"""

FIG02 = """<figure class="wow-act-figure wow-act-figure--map">
  <img
    src="../../graphics/fig-02-clinic-places-map.svg"
    alt="Schematic map labeling Worcester, Barre, Reno, London, and Almería as places named in this essay series."
    width="1200"
    height="560"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 2</strong> — Places the essays name (schematic, not a travel map).
    <span class="figure-credit">Original diagram, WOW Therapies educational series.</span>
  </figcaption>
</figure>"""

FIG03 = """<figure class="wow-act-figure wow-act-figure--timeline">
  <img
    src="../../graphics/fig-03-act-naming-dates.svg"
    alt="Sequence from 1980s comprehensive distancing through 1991 talk title, 1994 journal article, 1999 book, and 2005 society membership."
    width="1200"
    height="480"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 3</strong> — How the name ACT entered the public record.
    <span class="figure-credit">Original diagram, WOW Therapies educational series.</span>
  </figcaption>
</figure>"""

TYPE = """<figure class="wow-act-figure wow-act-figure--type">
  <img
    src="../../assets/_shared/type-plate-essay.svg"
    alt="Type-only plate for a WOW Therapies ACT and mindfulness history essay; no portrait embedded."
    width="960"
    height="540"
    loading="lazy"
  />
  <figcaption>
    <strong>ACT &amp; mindfulness history</strong> — educational draft; no likeness. See <code>RIGHTS.md</code>.
    <span class="figure-credit">Original type plate, WOW Therapies educational series.</span>
  </figcaption>
</figure>"""


def portrait_pending(subject: str, dates: str, plate_id: str) -> str:
    return f"""<figure class="wow-act-figure wow-act-figure--portrait wow-act-figure--portrait-pending">
  <img
    src="../../assets/_shared/portrait-pending.svg"
    alt="Portrait placeholder — rights not cleared for {subject}."
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>{subject}</strong> ({dates}) — <em>Portrait placeholder; rights not cleared.</em>
    See <code>plates/{plate_id}/RIGHTS.md</code> and <code>PORTRAIT_SOURCES.md</code>.
  </figcaption>
</figure>"""


META: dict[str, str] = {
    "what-this-folder-refuses": "What this ACT and mindfulness history pack refuses to claim: no diagnosis, no worksheets, no borrowed cushions sold as treatment. Educational WOW Therapies draft.",
    "how-to-read-a-therapy-history-claim": "How to read a therapy-history claim: trials as events, guidelines as committees, and why a mindfulness headline is not homework. Educational draft.",
    "third-wave-is-a-nickname": "Why “third wave” is a nickname, not geology — Hayes 2004, Hofmann 2008, and the family argument over CBT and ACT. Educational therapy history.",
    "sister-pack-different-job": "How this ACT and mindfulness pack differs from the WOW Therapies counseling heritage series and the SLPWOW speech-history lane. Educational draft.",
    "attention-is-older-than-a-clinic": "Attention practices predate hospital mindfulness programs: a dated look at clinics, texts, and borrowed vocabulary. Not treatment advice.",
    "satipatthana-as-a-textual-object": "Satipaṭṭhāna as a textual object with translators and arguments — not a 1979 medical syllabus. Educational Buddhist-history frame.",
    "american-zendo-after-1950": "American zendos after 1950: Suzuki, Watts, and the sitting rooms that shaped clinicians — without a portrait we have not cleared.",
    "ims-1975": "Insight Meditation Society, 1975: Barre, a Catholic novitiate, and the retreat town that fed hospital mindfulness programs. Educational history.",
    "thich-nhat-hanh-in-the-west": "Thích Nhất Hạnh in Western public life: engaged Buddhism as history, not a clinic script. Portrait placeholder; rights not cleared.",
    "benson-1975-relaxation-response": "Herbert Benson’s 1975 relaxation-response book as a medical object — not a meditation prescription. Educational draft; no cleared portrait.",
    "langers-other-mindfulness": "Ellen Langer’s 1989 social-psychology mindfulness: same English word, different job from hospital MBSR. Educational history essay.",
    "morita-naikan-cousin-rooms": "Morita therapy, Naikan, and cousin rooms to ACT talk — Japanese clinical history without a conversion story. Portrait not cleared.",
    "verbal-behavior-and-the-clinic": "Skinner’s 1957 Verbal Behavior and the clinic that walked past it toward cognitive models. Educational behavior-analysis history.",
    "rule-governed-behavior-1980s": "Rule-governed behavior in 1980s ACT precursors: when following language saves a life and when it ruins one. Educational draft.",
    "comprehensive-distancing": "Comprehensive distancing in the lab before the marketable ACT name — 1980s behavior-analytic history, not a how-to.",
    "relational-frame-theory-2001": "Relational frame theory, 2001: a research program behind ACT, not a personality quiz. Educational psychotherapy history draft.",
    "why-the-treatment-was-named-act": "Why the treatment was named ACT: 1991 talk, 1994 article, and the rejected synonyms — a naming chain, not brand myth.",
    "hayes-before-the-1999-book": "Steven C. Hayes before the 1999 Guilford volume: two decades of papers, not an overnight brand. No portrait; living author.",
    "the-1999-guilford-volume": "The 1999 Guilford ACT book as an orderable hospital object — history of a manual, not a session script. Educational essay.",
    "strosahl-and-the-primary-care-door": "Kirk Strosahl and primary-care ACT dissemination — how a school left the university lab. Educational history; no portrait.",
    "kelly-wilson-and-the-values-sentence": "Kelly G. Wilson and the values sentence in ACT history — language with a past, not a card sort. Educational draft.",
    "acbs-2005": "Association for Contextual Behavioral Science, 2005: listserv culture, a Swedish conference, then bylaws. Educational society history.",
    "a-diagram-that-escaped-the-workshop": "The hexaflex as workshop teaching lore — why this series will not reprint it as a consumer worksheet. Educational ACT history.",
    "the-workshop-economy": "How ACT became a workshop economy: training travel, listservs, and workforce history without inventing attendance counts.",
    "kabat-zinn-1979": "Jon Kabat-Zinn and the 1979 Worcester stress-reduction clinic — a dated hospital program, not a meditation course for readers.",
    "full-catastrophe-living-1990": "Full Catastrophe Living, 1990: the public book that carried MBSR out of Worcester — a bibliographic object, not instruction.",
    "three-cognitive-therapists-wanted-a-cushion": "Why Segal, Williams, and Teasdale wanted mindfulness in MBCT — relapse prevention history, not religion. Educational draft.",
    "teasdale-et-al-2000": "Teasdale, Segal, and Williams, 2000 JCCP trial: sample, follow-up, and episode split as historical facts — not enrollment advice.",
    "the-2002-mbct-book": "The 2002 MBCT Guilford manual as an object the NHS could name — committee history, not a reader workbook.",
    "marlatt-and-mbrp": "Alan Marlatt and mindfulness-based relapse prevention — adjacent program history without teaching either MBRP or relapse skills.",
    "linehans-mindfulness-this-angle": "Marsha Linehan’s mindfulness only where it meets hospital staffing — full biography stays in the sister counseling pack.",
    "neighbors-fap-cft-compassion": "FAP, CFT, and the compassion boom as neighboring rooms — not a merger into one third-wave brand. Educational history.",
    "hayes-2004-wave-essay": "Hayes 2004 Behavior Therapy “third wave” essay as a public nickname — geology metaphor meets the record. Educational draft.",
    "ost-2008": "Lars-Göran Öst, 2008: a review that refused an easy victory lap for early ACT trials. Educational evidence history.",
    "hofmann-and-the-family-quarrel": "Stefan Hofmann and the 2008 family quarrel over new-wave labels — debate history, not a treatment verdict.",
    "guidelines-as-historical-objects": "NICE and other guidelines as committee objects — MBCT named in CG90 is a fact about policy, not this site enrolling readers.",
    "mcmindfulness": "McMindfulness criticism: Purser, Loy, and corporate flattening of a hospital vocabulary — cultural history, not a boycott list.",
    "when-acceptance-sounds-like-a-muzzle": "When acceptance language sounds like a muzzle — justice critiques ACT must answer. Educational argument history.",
    "apps-yogurt-corporate-retreats": "Mindfulness after the clinic room: apps, yogurt lids, and corporate retreats as reception history — not endorsements.",
    "how-to-read-a-mindfulness-works-headline": "How to read a “mindfulness works” headline: sample, comparator, duration, and who paid — a reader tool, not medical advice.",
    "living-people-public-documents": "Living ACT and mindfulness authors in public documents only — no gossip dressed as context. Educational ethics note.",
    "what-a-small-city-clinic-inherited": "What a small-city clinic inherits from third-wave vocabulary without a trained team — scope honesty for readers.",
    "what-we-opened": "Bibliography honesty list for the ACT and mindfulness history pack — what these forty-five drafts actually opened.",
    "map-to-the-sister-packs": "Where to send readers who want Freud, Van Riper, or full Linehan — map to sister WOW Therapies and SLPWOW packs.",
    "portraits-we-will-not-fake": "Portraits we will not fake: type plates, title pages, and a refuse list for AI faces in therapy history thumbnails.",
}

EMBED: dict[str, str] = {
    "what-this-folder-refuses": TYPE,
    "attention-is-older-than-a-clinic": FIG01,
    "american-zendo-after-1950": portrait_pending(
        "Shunryu Suzuki", "1904–1971", "shunryu-suzuki"
    ),
    "ims-1975": FIG02,
    "thich-nhat-hanh-in-the-west": portrait_pending(
        "Thích Nhất Hạnh", "1926–2022", "thich-nhat-hanh"
    ),
    "benson-1975-relaxation-response": portrait_pending(
        "Herbert Benson", "1935–2022", "herbert-benson"
    ),
    "morita-naikan-cousin-rooms": portrait_pending(
        "Shōma Morita", "1874–1938", "shoma-morita"
    ),
    "why-the-treatment-was-named-act": FIG03,
    "hayes-before-the-1999-book": FIG03,
    "acbs-2005": FIG03,
    "kabat-zinn-1979": FIG02,
    "hayes-2004-wave-essay": FIG01,
    "what-we-opened": FIG01,
    "portraits-we-will-not-fake": TYPE,
}

KIND: dict[str, str] = {}
for slug in META:
    KIND[slug] = "essay"
for slug in EMBED:
    if "portrait-pending" in EMBED[slug]:
        KIND[slug] = "portrait-pending"
    elif "fig-01" in EMBED[slug]:
        KIND[slug] = "timeline"
    elif "fig-02" in EMBED[slug]:
        KIND[slug] = "map"
    elif "type-plate" in EMBED[slug]:
        KIND[slug] = "type"

FEATURED = "assets/_shared/series-featured.svg"


def parse_front(text: str) -> tuple[dict[str, str], str, str]:
    m = FM_RE.match(text)
    if not m:
        raise ValueError("no frontmatter")
    raw_fm, body = m.group(1), m.group(2)
    meta: dict[str, str] = {}
    for line in raw_fm.splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body, raw_fm


def render_front(meta: dict[str, str]) -> str:
    order = [
        "id",
        "slug",
        "title",
        "stage",
        "stage_name",
        "voice",
        "claims_posture",
        "audience",
        "status",
        "meta_description",
        "featured_image",
        "graphic_kind",
        "last_verified",
    ]
    lines = ["---"]
    for key in order:
        if key in meta:
            val = meta[key]
            if key in ("title", "meta_description") and '"' not in val:
                lines.append(f'{key}: "{val}"')
            else:
                lines.append(f"{key}: {val}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def main() -> None:
    for path in sorted(ROOT.glob("stage-*/[0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body, _ = parse_front(text)
        slug = meta.get("slug", "")
        if slug not in META:
            raise SystemExit(f"no META for {slug}")
        meta["meta_description"] = META[slug]
        meta["featured_image"] = FEATURED
        meta["graphic_kind"] = KIND.get(slug, "essay")
        meta["last_verified"] = "2026-09-14"

        if slug in EMBED and "wow-act-figure" not in body:
            block = EMBED[slug]
            needle = "**Educational note.**"
            if needle not in body:
                raise SystemExit(f"{path}: no educational note")
            prefix, rest = body.split(needle, 1)
            split = rest.split("\n\n", 1)
            first_para = split[0]
            after = split[1] if len(split) > 1 else ""
            body = f"{prefix}{needle}{first_para}\n\n{block}\n\n{after}"

        new_text = render_front(meta) + body
        path.write_text(new_text, encoding="utf-8")
        print(f"updated {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
