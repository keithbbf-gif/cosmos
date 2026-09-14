"use strict";
// Sessions shell. Same-origin: this page and its JSON come from sessions_app.py,
// which reads Core server-side. The page never talks to Core directly and never
// invents a count - a null count renders UNMEASURED, never 0.

const $ = (id) => document.getElementById(id);

function esc(s) {
  return String(s === null || s === undefined ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function setCount(el, n, unit) {
  if (n === null || n === undefined) {
    el.textContent = "";
    el.className = "count unmeasured";
    return;
  }
  el.textContent = n + (unit ? " " + unit : "");
  el.className = "count";
}

function refusalHTML(body) {
  return '<div class="refusal"><span class="rkind">' + esc(body.kind || body.error) +
    "</span> " + esc(body.detail || "") + "</div>";
}

async function getJSON(path) {
  const r = await fetch(path, { headers: { Accept: "application/json" } });
  return { http: r.status, body: await r.json() };
}

// ---------------------------------------------------------------- sessions
let selected = null;

function renderSessions(http, b) {
  $("src").textContent = "source " + (b.source || "—");
  const tree = $("tree");
  tree.textContent = "tree " + (b.tree_id || "—");
  tree.className = "pill " + (b.tree_id ? "ok" : "bad");
  if (b.error) {
    setCount($("c-sessions"), null);
    $("omission").textContent = "legal omission UNMEASURED — Core was not read";
    $("rows").innerHTML = refusalHTML(b);
    return;
  }
  setCount($("c-sessions"), b.n_shown, "shown");
  const om = b.omission || {};
  const counted = (om.counted === null || om.counted === undefined)
    ? "UNMEASURED" : om.counted;
  $("omission").textContent = "legal " + esc(om.reason) + " — counted " + counted +
    ", opened " + om.opened + " (counted, never opened here)";
  if (!b.available) {
    $("rows").innerHTML = '<div class="refusal"><span class="rkind">' +
      esc(b.kind) + "</span> " + esc(b.detail || "no recents feed on Core") + "</div>";
    return;
  }
  if (!b.rows.length) {
    $("rows").innerHTML = '<div class="empty">feed is available and holds no ' +
      "session (measured empty)</div>";
    return;
  }
  $("rows").innerHTML = b.rows.map((r) =>
    '<div class="srow" data-id="' + esc(r.id) + '">' +
      '<span class="sid">' + esc(r.id) + "</span>" +
      '<span class="sdate">' + esc(r.date || "—") + "</span>" +
      '<span class="stitle">' + esc(r.title || "—") +
        ' <span class="sstream">' + esc(r.stream || "") + "</span></span>" +
    "</div>").join("");
  for (const el of document.querySelectorAll(".srow")) {
    el.addEventListener("click", () => openSession(el.dataset.id));
  }
}

async function openSession(id) {
  selected = id;
  for (const el of document.querySelectorAll(".srow")) {
    el.classList.toggle("sel", el.dataset.id === id);
  }
  $("detail").innerHTML = '<div class="empty">opening ' + esc(id) + " …</div>";
  const { body: b } = await getJSON("/api/sessions/open?id=" + encodeURIComponent(id));
  setCount($("c-detail"), b.text_len, "chars");
  if (b.error || !b.ok) {
    $("detail").innerHTML = refusalHTML(b) +
      (b.omission
        ? '<div class="note">counted ' + b.omission.counted + ", opened " +
          b.omission.opened + "</div>"
        : "");
    return;
  }
  $("detail").innerHTML = '<div class="note">' + esc(b.id) + " · " +
    esc(b.opencode_id || "no opencode id") + " · " + esc(b.title || "") + "</div>" +
    "<pre>" + esc((b.text || "").slice(0, 4000)) + "</pre>";
}

// ------------------------------------------------------------------- verbs
function renderVerbs(http, b) {
  if (b.error) {
    setCount($("c-verbs"), null);
    $("verbs").innerHTML = refusalHTML(b);
    return;
  }
  setCount($("c-verbs"), b.n_bound, "of " + b.n_verbs + " bound");
  $("engine").textContent = "engine " + b.engine + " · " + b.canonical;
  $("verbs").innerHTML = b.verbs.map((v) =>
    '<div class="vrow"><span class="vst ' + esc(v.status) + '">' + esc(v.status) +
    '</span><span class="vname">' + esc(v.verb) + '</span>' +
    '<span class="vdoes">' + esc(v.status === "BOUND" ? v.does : v.gate) +
    "</span></div>").join("");
  $("btnScan").disabled = !b.store_declared;
  if (!b.store_declared) {
    $("scan").innerHTML = '<div class="empty">no --store declared at serve time — ' +
      "a browser does not supply a filesystem path</div>";
  }
}

async function runScan() {
  $("scan").innerHTML = '<div class="empty">scanning …</div>';
  const { body: b } = await getJSON("/api/verbs/scan");
  if (b.error) {
    $("scan").innerHTML = refusalHTML(b);
    return;
  }
  const fams = (b.gate && b.gate.families) || [];
  $("scan").innerHTML = '<div class="note">' + esc(b.kind) + " · legal_omitted " +
    esc(b.legal_omitted) + " · " + esc(b.upstream_schema) + "</div>" +
    fams.map((f) =>
      '<div class="vrow"><span class="vst ' +
      (f.status === "OK" ? "BOUND" : "DECLARED") + '">' + esc(f.status) +
      '</span><span class="vname">' + esc(f.family) + '</span>' +
      '<span class="vdoes">' + (f.n === null || f.n === undefined ? "UNMEASURED" : esc(f.n)) +
      " · " + esc(f.path || "no path") + "</span></div>").join("");
}

// ---------------------------------------------------------------- timeline
function renderTimeline(http, b) {
  if (b.error) {
    setCount($("c-timeline"), null);
    $("timeline").innerHTML = refusalHTML(b);
    return;
  }
  setCount($("c-timeline"), b.n, "milestones");
  $("feedsrc").textContent = b.event_schema + " · " + b.source;
  if (!b.rows.length) {
    $("timeline").innerHTML = '<div class="' +
      (b.kind === "NO_SOURCE" ? "refusal" : "empty") + '">' +
      (b.kind === "NO_SOURCE" ? '<span class="rkind">NO_SOURCE</span> ' : "") +
      esc(b.detail || "no milestones") + "</div>";
    return;
  }
  $("timeline").innerHTML = b.rows.map((r) =>
    '<div class="trow"><span class="tt">' + esc(r.t === null ? "UNMEASURED" : r.t) +
    '</span><span class="tseat">' + esc(r.seat || "—") + '</span>' +
    '<span class="tkind">' + esc(r.kind || "—") + '</span>' +
    '<span class="ttitle">' + esc(r.title || "—") +
    ' <span class="tref">' + esc(r.ref || "") + "</span></span></div>").join("");
}

async function reload() {
  $("btnReload").disabled = true;
  try {
    const s = await getJSON("/api/sessions");
    renderSessions(s.http, s.body);
    const v = await getJSON("/api/verbs");
    renderVerbs(v.http, v.body);
    const t = await getJSON("/api/timeline");
    renderTimeline(t.http, t.body);
    if (selected) { await openSession(selected); }
  } finally {
    $("btnReload").disabled = false;
  }
}

$("btnReload").addEventListener("click", reload);
$("btnScan").addEventListener("click", runScan);
reload();
