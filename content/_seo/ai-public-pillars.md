# AI public — industry blog + history retrospective

**Map index:** [INDEX.md](INDEX.md) (linking rules for every lane).  
**Surface:** a public blog that is **not** COSMOS, not cDeck, not KDash, not the mesh. Domain TBD. Until it has a name, write as if it will be a clean two-hub site.

**Job:** say true things about the industry people already see (products, labor, regulation, research that shipped) and keep a sourced history that a non-specialist can read in order.

**Who writes:** Keith, as an engineer who uses these tools and has opinions. First person is fine. “We” meaning a secret OS is not.

This lane is **novelty-safe**. That is a hard constraint, not a vibe.

---

## Novelty-safe — do not publish

If a sentence would help a stranger reconstruct *how this household runs models*, it belongs in a private tree, not here.

**Never name or describe on this blog:**

- COSMOS, BTS_MESH, cDeck, Gitur, MOTIF, Crucible, ROLD, SEED manifests, fencing tokens, the signed ledger, spend gates, WD2, dual-lane critics, porosity/tensors, ThinkFast, ChatBot-phone architecture
- File paths, ports, lease files, bearer tokens, rail names as implemented
- Patent-docket contents, provisional theories, “the new way to run reliable AI”
- Prompt templates, critic rubrics, dispatch rules
- Anything the IP docket already said to keep off X / LinkedIn / arXiv until counsel files

**Safe:** public products (ChatGPT, Gemini, Claude, Grok, Copilot, open weights on Hugging Face, vLLM, etc.) as *a user and a reader of their docs*; history before and after 2022 that is in books and papers; labor and regulation that are in the news; your experience as a *customer* (“this model refused the job / cost X / hallucinated a citation”).

If you have to ask “is this COSMOS-shaped?”, it is. Cut it.

Also do not: fake benchmarks; “I asked 5 AIs” stunts with no method; affiliate GPU lists; medical or legal advice.

---

## Already live

None. There is no public Keith AI blog to inventory. Do not back-fill with COSMOS README language.

---

## Pillar A — Industry (what is happening)

**Hub:** `/industry/` — a short standing page: what this blog will cover (products, work, money, law, research-that-shipped) and what it will not (this household’s orchestration internals). Updated quarterly, not daily.

Industry pieces are **dated**. The hub lists the last six. Older notes stay URL-stable.

### Industry clusters (standing series, not a dump)

| Series | Intent | Cadence | Link rules |
|---|---|---|---|
| **What shipped** | One vendor or one model release, from the primary blog/docs, then what changed for a practitioner | When something real ships — not a weekly empty roundup | Link the vendor post. Link a history page only if the release *repeats an old pattern* (another winter warning, another scaling claim). |
| **What it costs** | API vs subscription vs “free” with a capture; who pays when the demo is free | Occasional | No live prices copied from a screenshot that will rot — describe the *shape* (seat, token, compute). |
| **Labor** | Who is hired, who is laid off, labeling, contractors, “AI engineer” as a job ad | When there is a primary source | Do not turn it into a COSMOS hiring narrative. |
| **Regulation and court** | US/EU actions, copyright suits, safety bills — what the text says | When a docket or bill moves | Link the filing. No legal advice. |
| **Open weights** | A model you actually ran, hardware you actually have | When you ran it | Method: name, quant, box, what broke. No mesh diagram. |
| **Refusal and error** | A concrete failure (bad cite, silent skip, sycophancy) | When you have the transcript *sanitized* | Do not include internal prompts from COSMOS rails. |

**Avoid the weekly “AI news” sausage.** If nothing shipped, skip. Two honest notes a month beat eight paraphrases of the same launch.

---

## Pillar B — History retrospective

**Hub:** `/history/` — a chronological spine with **anchors that do not move**:

1. Myths and automata (brief; do not live here)
2. 1940s–50s: Turing, Dartmouth 1956, the name
3. 1960s: optimism, early NLP, perceptron critique
4. First winter
5. Expert systems and the second boom
6. Second winter
7. Statistical turn, corpora, ImageNet, deep learning
8. Sequence models → Transformers (2017 paper)
9. Large public chat (2022– ) as *a chapter, not the whole book*
10. What we still cannot do (a standing, dated section)

Each node is a cluster. The hub is the spine plus one paragraph each, then “read”.

Cite: original papers, a university lecture, a contemporary news piece. Nilsson, Russell & Norvig, Wooldridge, or a museum exhibit beat a listicle. If you have not read the paper, do not summarize it from memory of a thread.

### History clusters (write in order; skip ahead only if a news piece *needs* the backstory)

| Working title | Spine # | Notes |
|---|---|---|
| Dartmouth 1956: what they actually proposed | 2 | McCarthy et al. — the proposal, not the myth. |
| Turing’s question, and what he did not claim | 2 | Primary essay. |
| Perceptrons and the hangover | 3–4 | Minsky/Papert as *a* cause, not the only one. |
| Expert systems: what worked in the plant | 5 | One real deployment story from the public record (MYCIN, XCON) — limits included. |
| Why it stopped, twice | 4, 6 | Money, compute, promises. Link industry “what it costs” when a modern parallel is earned. |
| ImageNet and the second sight | 7 | Fei-Fei Li / ILSVRC as public history. |
| Attention is all you need — the paper, not the brand | 8 | What the paper is. What it is not (a product). |
| Corpora, consent, and the training pile | 7–9 | Books, web scrapes, lawsuits — history of *inputs*. |
| Chat as a product, 2022–2026 | 9 | Dated. You will rewrite the last section every year; keep old dates. |
| Robotics and “AI” that touches the bench | 7–10 | Only public systems. No household automation map. |
| What “general” has meant in each decade | 10 | Stops the 2026 hype from eating the archive. |

---

## Linking

- Industry hub → last six notes. A note links the history node **only** when the analogy is the point of the piece (e.g. a funding winter), one link.
- History hub → the next and previous spine node (series navigation). That is sequential, not reciprocal spam. Do not also dump “related: 8 other centuries”.
- Do not link FigRoots, furniture, therapy, or supplements unless the article is *literally* about a public model mis-labeling a fig variety or a wood species — and then it is an industry-error piece, not a funnel.
- **Zero links** to github.com/keithbbf-gif/cosmos, GitLab cosmos, KDash, or any `docs/` filename.

---

## Cadence

**Default:** one industry note + one history cluster per month. If a month is all fire-drill news, ship two industry and slip history. If a month is quiet, ship history and skip industry.

Do not “catch up” with five history posts in a weekend. The spine is better slow and cited.

### October 2026 – September 2027

| Month | Industry | History |
|---|---|---|
| 2026-10 | Hub `/industry/` (scope + refusals) + one *What shipped* if something did | Hub `/history/` spine (stubs OK if the first two nodes are real) |
| 2026-11 | Costs / seats / tokens (shape, not a price list) | Turing essay |
| 2026-12 | Regulation or court — only with a filing | Dartmouth 1956 |
| 2027-01 | Open weight you actually ran over the holiday, or skip | Perceptrons / first winter |
| 2027-02 | Labor / job ads | Expert systems (one system) |
| 2027-03 | What shipped (spring model cycle) | Second winter / funding |
| 2027-04 | Refusal-and-error note (sanitized) | Statistical turn + corpora |
| 2027-05 | Skip or a short court follow-up | ImageNet |
| 2027-06 | Open weights or hardware | Transformers paper |
| 2027-07 | Quiet month: one short shipped-or-skip | Training pile / consent |
| 2027-08 | Labor or campus/research news | Chat as a product 2022–26 (dated) |
| 2027-09 | Year’s industry hub refresh (kill dead links) | “What general meant” + refresh spine dates |

---

## Measurement

- Return visits to `/history/` (it is a course, not bait).
- Industry notes cited or emailed because a *fact* was right (a date, a filing, a method).
- If the blog starts ranking for “COSMOS AI” or house internals, something leaked — take it down.

This lane succeeds when a stranger learns a true industry or history thing and never hears the name of the OS.
