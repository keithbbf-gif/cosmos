/* builds/cdeck/ui/app.js — COSMOS cDeck UI
 * One writer at a time. Do not touch JACK'S MESH / Signal Core / RING_NODES /
 * kdash_native.js from here.
 */
"use strict";

/* ── constants ────────────────────────────────────────────────────────────── */
var DEFAULT_URL = "http://127.0.0.1:8770";
var POLL_MS     = 10000;   /* health + feed poll cadence */
var RECENTS_MS  = 30000;   /* recents list refresh cadence */

/* ── XSS escape ───────────────────────────────────────────────────────────── */
function esc(s) {
  if (s == null) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* ── runtime state ────────────────────────────────────────────────────────── */
var _state = {
  baseUrl: DEFAULT_URL,
  token: "",
  treeId: null,
  /* last result from GET /recents?open=1&id=... */
  lastOpenResult: null,
};

/* ── API helpers ──────────────────────────────────────────────────────────── */
function api(path, opts) {
  opts = opts || {};
  var url = _state.baseUrl + path;
  var headers = {};
  if (_state.token) headers["Authorization"] = "Bearer " + _state.token;
  return fetch(url, {
    method: opts.method || "GET",
    headers: headers,
    body: opts.body != null ? JSON.stringify(opts.body) : undefined,
  })
    .then(function (r) { return r.json().then(function (j) { return { code: r.status, body: j }; }); })
    .catch(function (e) { return { code: 0, body: { error: String(e) } }; });
}

/* ── element helpers ──────────────────────────────────────────────────────── */
function el(id) { return document.getElementById(id); }

function setHtml(id, html) {
  var e = el(id);
  if (e) e.innerHTML = html;
}

function setText(id, text) {
  var e = el(id);
  if (e) e.textContent = text;
}

/* ── Recents pane ─────────────────────────────────────────────────────────── */

/**
 * paintCoworkRecents — render the Recents pane.
 *
 * When _state.lastOpenResult has kind === "OPENED", an OPENED card (title +
 * transcript head) is shown at the top of the pane above the session list.
 * All data text is passed through esc().
 *
 * @param {object|null} listBody  - parsed body from GET /recents (list)
 */
function paintCoworkRecents(listBody) {
  var pane = el("recents-pane");
  if (!pane) return;

  var html = "";

  /* ── OPENED card: shown when last open result is a success ── */
  var openResult = _state.lastOpenResult;
  if (openResult && openResult.kind === "OPENED") {
    var title = esc(openResult.title || openResult.id || "Session");
    /* transcript head: first 400 chars of text */
    var rawText = openResult.text || "";
    var head = rawText.slice(0, 400);
    var headEsc = esc(head);
    if (rawText.length > 400) headEsc += "<span class='recents-ellipsis'>\u2026</span>";

    html += "<div class='recents-opened-card' aria-label='Opened session'>"
      + "<div class='recents-opened-title'>" + title + "</div>"
      + "<div class='recents-opened-head'>" + headEsc + "</div>"
      + "<button class='recents-close-btn' onclick='clearOpenResult()'>&#x2715;</button>"
      + "</div>";
  }

  /* ── error / unavailable state ── */
  if (!listBody || listBody.ok === false) {
    var errMsg = esc((listBody && (listBody.error || listBody.kind)) || "unavailable");
    html += "<div class='recents-status recents-error'>" + errMsg + "</div>";
    pane.innerHTML = html;
    return;
  }

  /* ── NO_SOURCE: recents store not yet populated ── */
  if (listBody.kind === "NO_SOURCE" || !listBody.available) {
    html += "<div class='recents-status'>No sessions recorded yet.</div>";
    pane.innerHTML = html;
    return;
  }

  /* ── session list ── */
  var rows = listBody.rows || [];
  if (rows.length === 0) {
    html += "<div class='recents-status'>No sessions (legal omitted).</div>";
    pane.innerHTML = html;
    return;
  }

  html += "<ul class='recents-list'>";
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var id   = esc(row.id || "");
    var date = esc(row.date || "");
    var strm = esc(row.stream || "");
    var ttl  = esc(row.title || row.id || "untitled");
    var data = "data-id='" + id + "'";
    html += "<li class='recents-row' " + data + " onclick='openRecentsSession(this)'>"
      + "<span class='recents-date'>" + date + "</span>"
      + "<span class='recents-stream'>" + strm + "</span>"
      + "<span class='recents-title'>" + ttl + "</span>"
      + "</li>";
  }
  html += "</ul>";

  var omitted = listBody.n_omitted_legal;
  if (omitted) {
    html += "<div class='recents-omitted'>" + esc(String(omitted)) + " legal session(s) omitted.</div>";
  }

  pane.innerHTML = html;
}

/**
 * openRecentsSession — called when a list row is clicked.
 * Fetches GET /recents?open=1&id=<id>, stores result, repaints.
 */
function openRecentsSession(rowEl) {
  var id = rowEl && rowEl.getAttribute("data-id");
  if (!id) return;

  /* mark row loading */
  rowEl.classList.add("recents-loading");

  api("/api/v1/recents?open=1&id=" + encodeURIComponent(id))
    .then(function (res) {
      _state.lastOpenResult = res.body || null;
      /* repaint with current list + new open result */
      paintCoworkRecents(_state.lastRecentsBody);
    })
    .catch(function () {
      _state.lastOpenResult = null;
      paintCoworkRecents(_state.lastRecentsBody);
    });
}

/**
 * clearOpenResult — dismiss the OPENED card.
 */
function clearOpenResult() {
  _state.lastOpenResult = null;
  paintCoworkRecents(_state.lastRecentsBody);
}

/* ── recents polling ─────────────────────────────────────────────────────── */
var _recentsTimer = null;
_state.lastRecentsBody = null;

function refreshRecents() {
  api("/api/v1/recents")
    .then(function (res) {
      _state.lastRecentsBody = res.code === 200 ? res.body : null;
      paintCoworkRecents(_state.lastRecentsBody);
    });
}

function startRecentsPolling() {
  refreshRecents();
  _recentsTimer = setInterval(refreshRecents, RECENTS_MS);
}

function stopRecentsPolling() {
  if (_recentsTimer) { clearInterval(_recentsTimer); _recentsTimer = null; }
}

/* ── status / health panel ───────────────────────────────────────────────── */
function paintStatus(body) {
  var s = body && body.ok ? "READY" : ((body && body.error) || "?");
  setText("status-label", esc(s));
}

function refreshStatus() {
  api("/api/v1/status")
    .then(function (res) { paintStatus(res.body); });
}

/* ── tab switching ───────────────────────────────────────────────────────── */
function showTab(tabId) {
  var tabs = document.querySelectorAll(".cdeck-pane");
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].style.display = tabs[i].id === tabId ? "" : "none";
  }
  var navItems = document.querySelectorAll(".cdeck-nav-item");
  for (var j = 0; j < navItems.length; j++) {
    var ni = navItems[j];
    ni.classList.toggle("active", ni.getAttribute("data-pane") === tabId);
  }
  if (tabId === "recents-pane") {
    refreshRecents();
  }
}

/* ── init ─────────────────────────────────────────────────────────────────── */
function init() {
  /* read base URL from meta tag or default */
  var meta = document.querySelector("meta[name='cdeck-base']");
  if (meta && meta.content) _state.baseUrl = meta.content;

  /* wire nav */
  var navItems = document.querySelectorAll(".cdeck-nav-item");
  for (var i = 0; i < navItems.length; i++) {
    (function (ni) {
      ni.addEventListener("click", function () {
        showTab(ni.getAttribute("data-pane"));
      });
    })(navItems[i]);
  }

  /* start polling */
  refreshStatus();
  setInterval(refreshStatus, POLL_MS);

  /* show recents pane by default */
  showTab("recents-pane");
  startRecentsPolling();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
