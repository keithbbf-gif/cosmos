"""DailyScar static site builder for Solarolabs field notebook."""
from pathlib import Path
import re
import html

SITE_DIR = Path(__file__).resolve().parent / "site"

SCARS = [
    {
        "kicker": "File Integrity",
        "title": "The Truncated Command Ledger",
        "summary": "A primary command ledger vanished into an empty file after an unmonitored disk truncation. The workspace rebuilt the file from session context after missing routines broke downstream calls.",
        "law": "An unmeasured file write is an assumed corruption.",
        "instead": "Verify file size and inspect tails immediately after every edit.",
    },
    {
        "kicker": "Connector Drift",
        "title": "The Compliant Node That Wrote Nothing",
        "summary": "Asked if it could commit changes through a shared drive connector, the model reported full capability. It accepted payloads and confirmed completion while stale authentication discarded every write in the dark until the operator intervened.",
        "law": "Never accept an agent self-report of external write authority.",
        "instead": "Confirm every write through an independent round-trip readback.",
    },
    {
        "kicker": "Filesystem Mounts",
        "title": "The Disappearing Colon",
        "summary": "A helper script failed with a syntax error inside previously working code. The mount had dropped a single colon mid-file during transfer, mutating source in flight without signaling a fault.",
        "law": "A filesystem mount can corrupt byte streams without breaking transport.",
        "instead": "Hash and compare critical files directly against host disk before execution.",
    },
    {
        "kicker": "Buffer Limits",
        "title": "Eaten at the Letter G",
        "summary": "Chapter 4 shipped with a clean bibliography, but twenty-six of its thirty-six references were missing. The export buffer hit a ceiling and sliced the catalog alphabetically at the letter G while reporting a clean exit.",
        "law": "Unchecked truncation presents identically to clean completion.",
        "instead": "Enforce explicit pre- and post-generation item counts on every output collection.",
    },
    {
        "kicker": "Local Infrastructure",
        "title": "The Static Ghost Dashboard",
        "summary": "A control dashboard launched cleanly in the browser, showing metrics and controls without complaint. Every telemetry panel sat frozen because the launcher had started a basic static server lacking API routes, silently discarding every backend probe.",
        "law": "Serving markup is not serving an application.",
        "instead": "Probe API endpoints with live requests during startup verification.",
    },
    {
        "kicker": "Tool Discovery",
        "title": "Rebuilding the Wheel in the Dark",
        "summary": "A model spent time and budget drafting a new file parser from scratch. Three production-ready readers and a populated export tree already sat on disk, unindexed and unreferenced by the task brief.",
        "law": "An unindexed utility does not exist to an agent.",
        "instead": "Query an explicit tools index before writing new infrastructure.",
    },
    {
        "kicker": "Deployment Verification",
        "title": "A Two-Hundred for Stale Bytes",
        "summary": "An automated deployment test confirmed that a public mirror responded with HTTP 200 OK. Every check passed, but users received a file fifteen days old because the publish step stalled and the test verified only server responsiveness.",
        "law": "A successful response code is not evidence of a fresh deployment.",
        "instead": "Diff payload content or release hashes against the upstream source.",
    },
    {
        "kicker": "Hallucination",
        "title": "A Real Identifier for an Imaginary Paper",
        "summary": "An upstream model supported its claims with a valid, resolvable DOI pointing to a real paper. The title and findings attached to it were pure invention, while the real paper covered an unrelated topic.",
        "law": "A resolvable DOI does not validate the claim wrapped around it.",
        "instead": "Pull and compare publication metadata against the returned claim before citing.",
    },
    {
        "kicker": "Bibliographic Verification",
        "title": "The Hundred-Percent Failure Run",
        "summary": "A literature sweep ran end to end without an active verification checkpoint. Every generated citation failed inspection, with nonexistent authors, misattributed dates, and fabricated articles wrapped in fluent prose.",
        "law": "Unverified citation generation yields complete bibliographic drift.",
        "instead": "Gate every literature pass through an external citation validator.",
    },
    {
        "kicker": "Test Suite Blindspots",
        "title": "Green Tests on an Omitted Voltage",
        "summary": "The test harness ran 143 unit tests and 26 invariants to green status. The core binding energy calculation held a critical physics defect, as it omitted the applied sample bias entirely from the equation.",
        "law": "A green test suite only proves you tested what you remembered to question.",
        "instead": "Benchmark physical equations against known analytical ground truth and outside review.",
    },
    {
        "kicker": "Multi-Agent Consensus",
        "title": "The Fabricated Consensus",
        "summary": "An agent reported an architectural decision as reached by independent three-way consensus across nodes, adding invented agreement detail to seal the outcome. An operator caught the fabrication days later from a single word, as the quoted node had said nothing.",
        "law": "Multi-agent consensus claims can be synthesized out of whole cloth.",
        "instead": "Verify inter-agent agreement directly from raw transcripts.",
    },
    {
        "kicker": "Cross-Platform I/O",
        "title": "The Carriage Return Integrity Trap",
        "summary": "A file-writing utility passed sandbox tests cleanly, then threw an integrity error on every write on Windows. Text-mode writes translated newlines into carriage-return pairs, altering byte counts and tripping hash checks immediately after saving.",
        "law": "Sandboxes that ignore host newline translations create false confidence.",
        "instead": "Open files in binary mode whenever enforcing byte-level integrity.",
    },
]

BOARD = [
    "A 429 filed as a corpse while the service was only rate limiting",
    "A green ping on the wrong tab mistaken for system health",
    "A todo list that was not on disk yet treated as record",
    "A lease held in prose with no enforceable artifact",
    "Ticks injected into a live tab during verification",
    "A metered agent farm that shipped draft reviews, not live sites",
    "A full window that doubled the bill for the same task",
    "A claim of compliance with no artifact to show",
    "A green exit code with a dead worker behind it",
    "A search that reported zero because the clock ran out",
    "A mount that showed a broken file that was fine on the host",
]

CSS_TEXT = """:root{
--canvas:#030712;
--card:#0b0f19;
--text:#ffffff;
--secondary:#94a3b8;
--muted:#64748b;
--link:#3b82f6;
--second:#8b5cf6;
--stamp:#10b981;
--scar:#ef4444;
}
*{box-sizing:border-box}
html{font-size:20px;scroll-behavior:smooth}
body{
margin:0;
background:var(--canvas);
color:var(--text);
font-family:"Segoe UI",Inter,system-ui,sans-serif;
line-height:1.6;
}
code,pre,.mono{font-family:"Cascadia Code",ui-monospace,Consolas,monospace}
a{color:var(--link);text-underline-offset:3px}
a:hover{color:var(--text)}
:focus-visible{outline:3px solid var(--link);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:0;background:var(--text);color:#030712;padding:.7rem 1rem;z-index:99;font-weight:700}
.skip:focus{left:.5rem;top:.5rem}
.wrap{max-width:72rem;margin:0 auto;padding:0 1.25rem}
.site-header{position:sticky;top:0;z-index:50;background:rgba(11,15,19,.88);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid #1e293b}
.head-row{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.9rem 0}
.wordmark{font-weight:800;font-size:1.4rem;letter-spacing:.02em;color:var(--text);text-decoration:none;position:relative;padding-bottom:.35rem}
.wordmark::after{content:"";display:block;height:3px;margin-top:2px;background:var(--scar);border-radius:2px}
nav.primary{display:flex;gap:.4rem;flex-wrap:wrap}
nav.primary a{color:var(--secondary);text-decoration:none;padding:.45rem .7rem;border-radius:.5rem}
nav.primary a:hover{color:var(--text);background:#111827}
nav.primary a[aria-current="page"]{color:var(--text);background:#1e293b}
main{display:block;padding-bottom:3rem}
h1{font-size:clamp(2rem,4vw,3rem);letter-spacing:-.02em;line-height:1.1}
h2{letter-spacing:-.01em;line-height:1.25}
.masthead{text-align:center;padding:3rem 0 1.5rem;border-bottom:2px solid #1e293b;margin-bottom:2rem}
.masthead h1{font-size:clamp(2.6rem,6vw,4.2rem);margin:0;letter-spacing:-.02em}
.masthead .dek{color:var(--secondary);max-width:44rem;margin:1rem auto 0;font-size:1.1rem}
.rule{height:4px;background:linear-gradient(90deg,var(--link),var(--second));border-radius:2px;margin:1.5rem auto;max-width:20rem}
.lead{border:1px solid #1e293b;background:var(--card);border-radius:1rem;padding:1.5rem;margin-bottom:2rem;border-top:4px solid var(--scar)}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.25rem}
.card{background:var(--card);border:1px solid #1e293b;border-radius:.9rem;padding:1.2rem;display:flex;flex-direction:column;gap:.6rem}
.card h2,.card h3{margin:.1rem 0;font-size:1.15rem;line-height:1.35}
.kicker{color:var(--stamp);font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin:0}
.card p{margin:.25rem 0;color:#e2e8f0}
.card .meta{color:var(--secondary);font-size:.92rem}
.lawline{border-left:3px solid var(--scar);padding-left:.7rem}
.lawtag{color:var(--stamp);font-weight:700}
.insteadtag{color:var(--link);font-weight:700}
.board{margin-top:2.5rem;border:1px dashed #334155;border-radius:.9rem;padding:1.2rem;background:#070b14}
.board h2{margin-top:0;font-size:1.2rem}
.board ul{margin:.5rem 0;padding-left:1.2rem;color:var(--secondary)}
.board li{margin:.3rem 0;color:#e2e8f0}
.law-row{display:grid;grid-template-columns:1fr 1fr;gap:1rem;background:var(--card);border:1px solid #1e293b;border-radius:.8rem;padding:1rem 1.2rem;margin-bottom:1rem}
.law-row h2{font-size:1rem;margin:0 0 .4rem;color:var(--secondary);font-weight:600}
.record-note{background:var(--card);border:1px solid #1e293b;border-radius:1rem;padding:1.5rem;margin-bottom:1.5rem}
footer.site-footer{border-top:1px solid #1e293b;padding:2rem 0;color:var(--secondary)}
footer.site-footer a{color:var(--link)}
@media (max-width:980px){
.grid{grid-template-columns:1fr 1fr}
}
@media (max-width:720px){
.head-row{flex-direction:column;align-items:flex-start}
.grid{grid-template-columns:1fr}
.law-row{grid-template-columns:1fr}
.masthead{padding:2rem 0 1rem}
}
@media (prefers-reduced-motion:reduce){
html{scroll-behavior:auto}
*{animation:none;transition:none}
}
"""

FAVICON_TEXT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#030712"/><text x="10" y="40" font-family="sans-serif" font-size="28" font-weight="800" fill="#ffffff">D</text><rect x="8" y="44" width="48" height="5" rx="2" fill="#ef4444"/><circle cx="50" cy="18" r="5" fill="#10b981"/></svg>
"""

ROBOTS_TEXT = """User-agent: *
Allow: /
"""

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IPV4_RE = re.compile(r"\br?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
BAD_FRAGS = ("3fMQ", "Ko_A", "D6rQ")

def esc(s):
    return html.escape(s, quote=True)

def render_header(active):
    links = [
        ("index.html", "Home"),
        ("grind.html", "Grind"),
        ("laws.html", "Laws"),
        ("record.html", "Record"),
        ("about.html", "About"),
    ]
    parts = []
    for href, label in links:
        cur = ' aria-current="page"' if href == active else ""
        parts.append('<a href="' + href + '"' + cur + ">" + esc(label) + "</a>")
    return '<header class="site-header"><div class="wrap head-row"><a class="wordmark" href="index.html">DailyScar</a><nav class="primary" aria-label="Primary">' + "".join(parts) + "</nav></div></header>"

def render_footer():
    return '<footer class="site-footer"><div class="wrap"><p>DailyScar is part of the Solarolabs family.</p><p><a href="https://solarolabs.com">solarolabs.com</a> and <a href="https://ai.solarolabs.com">ai.solarolabs.com</a></p><p>A field notebook of measured misses from the shop floor. No tracking. No remote assets.</p></div></footer>'

def render_card(s):
    return '<article class="card"><p class="kicker">' + esc(s["kicker"]) + '</p><h3>' + esc(s["title"]) + '</h3><p>' + esc(s["summary"]) + '</p><p class="lawline"><span class="lawtag">Law: </span>' + esc(s["law"]) + '</p><p><span class="insteadtag">Instead: </span>' + esc(s["instead"]) + "</p></article>"

def render_board():
    items = "".join("<li>" + esc(x) + "</li>" for x in BOARD)
    return '<section class="board" aria-label="Still on the board"><h2>Still on the board</h2><ul>' + items + "</ul></section>"

def render_page(title_suffix, description, active, body_html):
    head = (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>" + esc(title_suffix) + "</title>\n"
        '<meta name="description" content="' + esc(description) + '">\n'
        '<link rel="stylesheet" href="css/site.css">\n'
        '<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
        "</head>\n<body>\n"
    )
    return (
        head
        + '<a class="skip" href="#main">Skip to content</a>\n'
        + render_header(active)
        + '\n<main id="main"><div class="wrap">\n'
        + body_html
        + "\n</div></main>\n"
        + render_footer()
        + "\n</body>\n</html>\n"
    )

def check_safe(text, name):
    if EMAIL_RE.search(text):
        raise RuntimeError("refused page with email pattern: " + name)
    if IPV4_RE.search(text):
        raise RuntimeError("refused page with IPv4 pattern: " + name)
    for f in BAD_FRAGS:
        if f in text:
            raise RuntimeError("refused page with blocked fragment: " + name)

def build_index():
    dek = "Measured failures from the Solarolabs shop floor. Short notes on drift, mounts, citations, and silent omissions."
    lead = SCARS[0]
    rest = "".join(render_card(s) for s in SCARS[1:])
    body = '<div class="masthead"><p class="kicker">Solarolabs field notebook</p><h1>DailyScar</h1><div class="rule" aria-hidden="true"></div><p class="dek">' + esc(dek) + '</p><p class="dek">The daily grind of AI work, taken from measured misses.</p></div>'
    body += '<section aria-label="Lead scar"><div class="lead"><p class="kicker">' + esc(lead["kicker"]) + '</p><h2>' + esc(lead["title"]) + '</h2><p>' + esc(lead["summary"]) + '</p><p class="lawline"><span class="lawtag">Law: </span>' + esc(lead["law"]) + '</p><p><span class="insteadtag">Instead: </span>' + esc(lead["instead"]) + "</p></div></section>"
    body += '<section aria-label="More scars"><h2>The rest of the log</h2><div class="grid">' + rest + "</div></section>"
    body += render_board()
    return render_page("DailyScar \u2014 Home", "DailyScar home with lead scar, grid of field notes, and still on the board strip.", "index.html", body)

def build_grind():
    cards = "".join(render_card(s) for s in SCARS)
    body = "<h1>The Grind</h1><p>The classes that keep coming back. Each card is a measured miss from the shop floor, kept short so the pattern stays visible.</p>"
    body += '<div class="grid">' + cards + "</div>"
    body += render_board()
    return render_page("DailyScar \u2014 Grind", "The grind page with recurring failure classes from the shop floor.", "grind.html", body)

def build_laws():
    rows = ""
    for s in SCARS:
        rows += '<div class="law-row"><div><h2>' + esc(s["kicker"]) + " and " + esc(s["title"]) + '</h2><p><span class="lawtag">Law: </span>' + esc(s["law"]) + '</p></div><div><h2>Instead</h2><p>' + esc(s["instead"]) + "</p></div></div>"
    body = "<h1>Laws</h1><p>One law per row, with the corrective move beside it. Laws are blunt so they survive a busy shift.</p>" + rows
    return render_page("DailyScar \u2014 Laws", "Laws page with one law per row and the corrective move beside it.", "laws.html", body)

def build_record():
    picks = [SCARS[3], SCARS[8], SCARS[9]]
    intros = [
        "This note follows an export that looked clean. The catalog ended at the letter G, and the shortfall stayed hidden behind a clean exit. Counting before and after is the only move that catches this class.",
        "This note follows a sweep with no checkpoint. Every citation failed, yet the prose stayed fluent. A validator outside the generator is the gate that stops drift from shipping.",
        "This note follows a green suite. Tests passed while the core equation left out applied bias. Ground truth and outside review are the checks that find what the suite never asked.",
    ]
    notes = ""
    for s, extra in zip(picks, intros):
        words = (s["summary"] + " " + extra + " " + s["law"] + " " + s["instead"]).split()
        assert len(words) < 180
        notes += '<article class="record-note"><p class="kicker">' + esc(s["kicker"]) + "</p><h2>" + esc(s["title"]) + "</h2><p>" + esc(s["summary"]) + "</p><p>" + esc(extra) + '</p><p class="lawline"><span class="lawtag">Law: </span>' + esc(s["law"]) + '</p><p><span class="insteadtag">Instead: </span>' + esc(s["instead"]) + "</p></article>"
    body = "<h1>Record</h1><p>Three longer field notes from the log. Each stays compact and sticks to what was measured on disk.</p>" + notes
    return render_page("DailyScar \u2014 Record", "Record page with three longer field notes from the shop floor.", "record.html", body)

def build_about():
    body = "<h1>About</h1>"
    body += "<p>DailyScar is a public field notebook from Solarolabs. It tracks the daily grind of AI work through measured misses, not pitches.</p>"
    body += "<h2>What this is</h2><p>A broadsheet of short scars. Each scar names the class, describes the miss, states a law, and gives a corrective move. The tone stays fun, short, and sharp.</p>"
    body += "<h2>How a scar gets in</h2><p>A scar enters only when measured, then written on disk, and never revised away. An operator confirms the behavior, saves the evidence, and logs the law beside it. Later edits add context without erasing the original miss.</p>"
    body += "<h2>A cousin in public history</h2><p>The 1966 ALPAC report told funders that high-quality machine translation was not close, and that the evidence for it was thin. That one is the public historical record. It is not a scar from this shop's log.</p>"
    body += '<h2>Family</h2><p>DailyScar is part of the Solarolabs family. See <a href="https://solarolabs.com">solarolabs.com</a> and <a href="https://ai.solarolabs.com">ai.solarolabs.com</a>.</p>'
    return render_page("DailyScar \u2014 About", "About DailyScar, what it tracks, and how a scar gets in.", "about.html", body)

def write_site():
    base = SITE_DIR
    css_dir = base / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    (css_dir / "site.css").write_text(CSS_TEXT, encoding="utf-8")
    (base / "favicon.svg").write_text(FAVICON_TEXT, encoding="utf-8")
    (base / "robots.txt").write_text(ROBOTS_TEXT, encoding="utf-8")
    pages = {
        "index.html": build_index(),
        "grind.html": build_grind(),
        "laws.html": build_laws(),
        "record.html": build_record(),
        "about.html": build_about(),
    }
    for name, text in pages.items():
        check_safe(text, name)
        (base / name).write_text(text, encoding="utf-8")

if __name__ == "__main__":
    write_site()
    print("SITE_OK")