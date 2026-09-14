/* deck_forge.js — Forge pane write paths with REFUSED surfacing.
 *
 * Every POST (studio save, profiles engine save, profiles/bg stage run,
 * profiles/bg facilitate) detects a REFUSED response and surfaces it in
 * two places:
 *   1. The pane – an .errbox is rendered inside the forge status element.
 *   2. addConsole – addConsole("err", "REFUSED", label, detail) is called.
 *
 * A REFUSED response arrives as an HTTP 4xx body {error:"REFUSED", detail:…}
 * (thrown by the shared apiCall helper as Error with .json attached) OR,
 * for endpoints that inline the refusal at HTTP 200, as d.error==="REFUSED"
 * in the resolved value.  Both cases are handled by _forgeWrite.
 *
 * Do NOT touch: JACK'S MESH, Signal Core, RING_NODES, kdash_native.js.
 */

(function (global) {
  "use strict";

  /* ------------------------------------------------------------------ *
   * Internal helpers                                                    *
   * ------------------------------------------------------------------ */

  /**
   * Render a refusal error box inside a pane status element and log to
   * the shared console.  `label` identifies which write path refused;
   * `err` is the raw Error (with optional .json) or a plain string.
   */
  function _surfaceRefused(ctx, label, err) {
    var detail = "";
    var jsonBody = null;

    if (err && err.json) {
      detail = String(err.json.detail || err.json.error || err.message || err);
      jsonBody = JSON.stringify(err.json, null, 2);
    } else if (typeof err === "string") {
      detail = err;
    } else if (err && err.message) {
      detail = err.message;
    }

    /* 1. Pane: inject an .errbox into the forge status container. */
    var statusEl = global.document
      ? global.document.getElementById("forge-status")
      : null;
    if (statusEl) {
      var box = global.document.createElement("div");
      box.className = "errbox";
      box.innerHTML =
        "<b>REFUSED</b> " +
        _esc(label) +
        (detail ? " — " + _esc(detail) : "");
      /* Replace any prior refusal box so stale errors don't accumulate. */
      var prior = statusEl.querySelector(".errbox");
      if (prior) {
        statusEl.replaceChild(box, prior);
      } else {
        statusEl.insertBefore(box, statusEl.firstChild);
      }
    }

    /* 2. Console: addConsole is injected via ctx or falls back to window. */
    var ac = (ctx && ctx.addConsole) || (global.addConsole);
    if (typeof ac === "function") {
      ac("err", "REFUSED", label + (detail ? " — " + detail : ""), jsonBody);
    }
  }

  /** Minimal HTML-escape for .errbox text. */
  function _esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  /**
   * Shared write helper.  Issues a POST and surfaces REFUSED responses.
   *
   * @param {object}   ctx      - deck context: {addConsole, apiPost, …}
   * @param {string}   path     - API path, e.g. "/api/v1/studio"
   * @param {object}   body     - request payload
   * @param {string}   label    - human-readable write-path label for errors
   * @param {function} onOk     - called with the parsed response on success
   * @returns {Promise}
   */
  function _forgeWrite(ctx, path, body, label, onOk) {
    var post = (ctx && ctx.apiPost) || (global.apiPost);
    if (typeof post !== "function") {
      _surfaceRefused(ctx, label, "apiPost not available");
      return Promise.resolve();
    }

    return post(path, body)
      .then(function (d) {
        /* Some endpoints return HTTP 200 with an inline refusal. */
        if (d && (d.error === "REFUSED" || d.kind === "REFUSED")) {
          var inlineErr = { message: d.error, json: d };
          _surfaceRefused(ctx, label, inlineErr);
          return;
        }
        if (typeof onOk === "function") {
          onOk(d);
        }
      })
      .catch(function (e) {
        /* HTTP 4xx throws: check whether this is a REFUSED refusal. */
        var isRefused =
          e &&
          e.json &&
          (e.json.error === "REFUSED" || e.json.kind === "REFUSED");
        if (isRefused) {
          _surfaceRefused(ctx, label, e);
        } else {
          /* Surface non-REFUSED errors via console only; don't swallow them. */
          var ac = (ctx && ctx.addConsole) || (global.addConsole);
          if (typeof ac === "function") {
            var detail = (e && e.message) || String(e);
            var jb = (e && e.json) ? JSON.stringify(e.json, null, 2) : null;
            ac("err", e && e.json && e.json.error
              ? String(e.json.error).toUpperCase()
              : "FORGE_WRITE",
              label + " — " + detail, jb);
          }
        }
      });
  }

  /* ------------------------------------------------------------------ *
   * Public write-path API                                               *
   * ------------------------------------------------------------------ */

  var DeckForge = {

    /**
     * Save the DEFINE statement (and/or RESEARCH config) to the studio.
     * POST /api/v1/studio — StudioError REFUSED when text > MAX_DEFINE or
     * research models > MAX_RESEARCH.
     */
    saveStudio: function (ctx, pack, onOk) {
      return _forgeWrite(ctx, "/api/v1/studio", pack,
        "Forge save studio", onOk);
    },

    /**
     * Save the Forge profile engine (problem, dest, stage notes).
     * POST /api/v1/profiles — ProfileError REFUSED when define text is
     * too long.
     */
    saveProfiles: function (ctx, pack, onOk) {
      return _forgeWrite(ctx, "/api/v1/profiles", pack,
        "Forge save profiles", onOk);
    },

    /**
     * Launch a background free-CLI stage (RESEARCH / ARCH / CONSENSUS).
     * POST /api/v1/profiles/bg — ForgeBgError REFUSED when stage is not
     * in BG_STAGES or the DEFINE statement is empty.
     */
    runBgStage: function (ctx, stage, n, onOk) {
      var body = { stage: stage };
      if (n != null) { body.n = n; }
      return _forgeWrite(ctx, "/api/v1/profiles/bg", body,
        "Forge bg " + stage, onOk);
    },

    /**
     * Facilitate (read back) a completed background stage result.
     * POST /api/v1/profiles/bg {action:"facilitate"} — ForgeBgError
     * REFUSED when the stage is not a bg stage.
     */
    facilitateBgStage: function (ctx, stage, onOk) {
      var body = { action: "facilitate", stage: stage };
      return _forgeWrite(ctx, "/api/v1/profiles/bg", body,
        "Forge facilitate " + stage, onOk);
    },

  };

  /* Attach to the global so the cDeck app can call DeckForge.*. */
  global.DeckForge = DeckForge;

}(typeof globalThis !== "undefined" ? globalThis : this));
