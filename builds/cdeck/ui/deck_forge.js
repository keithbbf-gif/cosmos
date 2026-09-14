/* deck_forge.js — Forge tab: CCr seat, adversarial seats, job estimate, porosity.
 *
 * Wire paths (Core contract):
 *   GET  /api/v1/model_rater        — paint forge.ccr + forge.adv_* seats
 *   POST /api/v1/model_rater/seat   — assign | action add | action remove
 *   POST /api/v1/model_rater/job_estimate — token estimate + override
 *   GET  /api/v1/porosity?profile=forge — pair tensor fold; UNMEASURED when empty
 *
 * REFUSED (HTTP 4xx or inline error) surfaces in the target pane and addConsole.
 * Do NOT touch: JACK'S MESH, Signal Core, RING_NODES, kdash_native.js.
 */
(function (global) {
  "use strict";

  var PROFILE = "forge";

  function $(id) {
    if (typeof global.$ === "function") return global.$(id);
    return global.document ? global.document.getElementById(id) : null;
  }

  function esc(s) {
    if (typeof global.esc === "function") return global.esc(s);
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function apiGet(path) {
    var fn = global.apiGet || global.apiCall;
    if (typeof fn !== "function") {
      return Promise.reject(new Error("apiGet unavailable"));
    }
    return fn(path);
  }

  function apiPost(path, body) {
    if (typeof global.apiPost !== "function") {
      return Promise.reject(new Error("apiPost unavailable"));
    }
    return global.apiPost(path, body);
  }

  function addConsole(kind, title, detail, pretty) {
    if (typeof global.addConsole === "function") {
      global.addConsole(kind, title, detail, pretty);
    }
  }

  function panelBusy(pane, on) {
    if (typeof global.panelBusy === "function") {
      global.panelBusy(pane, on);
    }
    var el = $("panel-forge-" + pane);
    if (el) el.classList.toggle("busy", !!on);
  }

  function paneForSeat(seat) {
    return seat === "ccr" ? "ccr" : "adv";
  }

  function _surfaceRefused(pane, label, err) {
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
    var host = $("panel-forge-" + pane);
    if (host) {
      var box = global.document.createElement("div");
      box.className = "errbox";
      box.innerHTML =
        "<b>REFUSED</b> " +
        esc(label) +
        (detail ? " — " + esc(detail) : "");
      var prior = host.querySelector(".errbox");
      if (prior) {
        host.replaceChild(box, prior);
      } else {
        host.insertBefore(box, host.firstChild);
      }
    }
    addConsole(
      "err",
      "REFUSED",
      label + (detail ? " — " + detail : ""),
      jsonBody
    );
  }

  function _inlineRefused(rec) {
    return rec && (rec.error === "REFUSED" || rec.kind === "REFUSED");
  }

  function _forgeSeats(rec) {
    return (rec && rec.seats) || [];
  }

  function paintCcr(seats) {
    var el = $("panel-forge-ccr");
    if (!el) return;
    var ccr = (seats || []).filter(function (s) {
      return s.profile === PROFILE && s.seat === "ccr";
    })[0];
    if (!ccr) {
      el.textContent = PROFILE + ".ccr — UNMEASURED";
      return;
    }
    var model = ccr.model || "unassigned";
    var via = ccr.via ? " via " + ccr.via : "";
    el.textContent = PROFILE + ".ccr = " + model + via;
  }

  function paintAdv(seats) {
    var el = $("panel-forge-adv");
    if (!el) return;
    var adv = (seats || []).filter(function (s) {
      return s.profile === PROFILE && String(s.seat || "").indexOf("adv_") === 0;
    });
    if (!adv.length) {
      el.textContent = "No adversarial seats — add via Core POST seat action add";
      return;
    }
    var lines = adv.map(function (s) {
      var m = s.model || "unassigned";
      var v = s.via ? " via " + s.via : "";
      return (s.label || s.seat) + ": " + PROFILE + "." + s.seat + " = " + m + v;
    });
    el.textContent = lines.join("\n");
  }

  function paintJob(snapshot) {
    var el = $("panel-forge-job");
    if (!el) return;
    var est = snapshot && snapshot.job_estimate;
    var costs = snapshot && snapshot.job_costs;
    if (!est && !costs) {
      el.textContent = "Job estimate — UNMEASURED (POST /api/v1/model_rater/job_estimate)";
      return;
    }
    var tin = (est && est.tokens_in) != null ? est.tokens_in : (costs && costs.tokens_in);
    var tout =
      (est && est.tokens_out) != null ? est.tokens_out : (costs && costs.tokens_out);
    var total = costs && costs.total_usd != null ? costs.total_usd : null;
    el.textContent =
      "tokens_in=" +
      tin +
      " tokens_out=" +
      tout +
      (total != null ? " total_usd=" + total : "");
  }

  function paintPorosity(rec) {
    var el = $("panel-forge-porosity");
    if (!el) return;
    if (!rec) {
      el.textContent = "porosity — UNMEASURED";
      return;
    }
    var kind = rec.kind || "UNMEASURED";
    var nObs = rec.n_obs != null ? rec.n_obs : 0;
    var schema = rec.schema || "";
    el.textContent =
      "kind=" +
      kind +
      " n_obs=" +
      nObs +
      (schema ? " schema=" + schema : "");
  }

  function paintIndependenceFromNodemap(nm) {
    var el = $("panel-forge-adv");
    if (!el || !nm) return;
    var nodes = ((nm.topology || {}).nodes) || [];
    var notes = nodes
      .filter(function (n) {
        return n.independence_note && String(n.independence_note).trim();
      })
      .map(function (n) {
        return n.id + ": " + n.independence_note;
      });
    var host = el.querySelector(".indep-notes");
    if (!notes.length) {
      if (host) host.remove();
      return;
    }
    if (!host) {
      host = global.document.createElement("p");
      host.className = "tiny dim indep-notes";
      el.appendChild(host);
    }
    host.textContent = notes.join(" ");
  }

  function paintFromSnapshot(snapshot) {
    var seats = _forgeSeats(snapshot);
    paintCcr(seats);
    paintAdv(seats);
    paintJob(snapshot);
  }

  function seatPost(body, pane, label, onOk) {
    panelBusy(pane, true);
    return apiPost("/api/v1/model_rater/seat", body)
      .then(function (rec) {
        panelBusy(pane, false);
        if (rec && rec.error != null && rec.error !== "") {
          if (_inlineRefused(rec) || String(rec.error).toUpperCase() === "REFUSED") {
            _surfaceRefused(pane, label, { message: rec.error, json: rec });
          } else {
            var detail =
              rec.detail != null && String(rec.detail) !== ""
                ? String(rec.detail)
                : String(rec.error);
            addConsole("err", String(rec.error).toUpperCase(), detail, JSON.stringify(rec, null, 2));
            var el = $("panel-forge-" + pane);
            if (el) el.innerHTML = esc(detail);
          }
          return rec;
        }
        if (typeof onOk === "function") onOk(rec);
        else paintFromSnapshot(rec);
        return rec;
      })
      .catch(function (e) {
        panelBusy(pane, false);
        var j = e && e.json;
        var isRefused =
          j && (j.error === "REFUSED" || j.kind === "REFUSED");
        if (isRefused) {
          _surfaceRefused(pane, label, e);
        } else {
          var kind = j && j.error ? String(j.error).toUpperCase() : "FORGE_SEAT";
          var detail =
            j && j.detail != null && String(j.detail) !== ""
              ? String(j.detail)
              : e.message || String(e);
          addConsole("err", kind, label + " — " + detail, j ? JSON.stringify(j, null, 2) : null);
          var el = $("panel-forge-" + pane);
          if (el) el.innerHTML = esc(detail);
        }
      });
  }

  function assign(profile, seat, model, where, via) {
    if (!seat) return;
    var prof = profile || PROFILE;
    var pane = where || paneForSeat(seat);
    var body = { profile: prof, seat: seat, model: model || "" };
    if (via) body.via = via;
    return seatPost(body, pane, "Forge seat assign " + prof + "." + seat, function (rec) {
      var got = _forgeSeats(rec).filter(function (s) {
        return s.profile === prof && s.seat === seat;
      })[0];
      var now = (got && got.model) || model || "unassigned";
      var nowVia = (got && got.via) || via || "";
      var msg =
        prof +
        "." +
        seat +
        " = " +
        now +
        (nowVia ? " via " + nowVia : "") +
        (model && now !== model ? " — Core kept its own model, not " + model : "");
      var el2 = $("panel-forge-" + pane);
      if (el2) el2.textContent = msg;
      paintFromSnapshot(rec);
    });
  }

  function addAdversary(model, label, via) {
    var body = { action: "add" };
    if (model) body.model = model;
    if (label) body.label = label;
    if (via) body.via = via;
    return seatPost(body, "adv", "Forge adversary add", function (rec) {
      paintFromSnapshot(rec);
    });
  }

  function removeAdversary(seat) {
    return seatPost(
      { action: "remove", seat: seat },
      "adv",
      "Forge adversary remove " + seat,
      function (rec) {
        paintFromSnapshot(rec);
      }
    );
  }

  function saveJobEstimate(tokensIn, tokensOut, override) {
    panelBusy("job", true);
    var body = {
      tokens_in: tokensIn,
      tokens_out: tokensOut,
      override: override !== false,
    };
    return apiPost("/api/v1/model_rater/job_estimate", body)
      .then(function (rec) {
        panelBusy("job", false);
        if (_inlineRefused(rec) || (rec && rec.error === "REFUSED")) {
          _surfaceRefused("job", "Forge job estimate", { message: "REFUSED", json: rec });
          return rec;
        }
        if (rec && rec.error) {
          addConsole(
            "err",
            String(rec.error).toUpperCase(),
            String(rec.detail || rec.error),
            JSON.stringify(rec, null, 2)
          );
          return rec;
        }
        paintJob(rec);
        return rec;
      })
      .catch(function (e) {
        panelBusy("job", false);
        var j = e && e.json;
        if (j && (j.error === "REFUSED" || j.kind === "REFUSED")) {
          _surfaceRefused("job", "Forge job estimate", e);
        } else {
          addConsole(
            "err",
            (j && j.error) ? String(j.error).toUpperCase() : "JOB_ESTIMATE",
            (j && j.detail) || e.message || String(e),
            j ? JSON.stringify(j, null, 2) : null
          );
        }
      });
  }

  function refreshPorosity() {
    return apiGet("/api/v1/porosity?profile=forge").then(function (rec) {
      paintPorosity(rec);
      return rec;
    });
  }

  function refresh() {
    return apiGet("/api/v1/model_rater")
      .then(function (snap) {
        paintFromSnapshot(snap);
        return apiGet("/api/v1/nodemap")
          .then(function (nm) {
            paintIndependenceFromNodemap(nm);
            return refreshPorosity().then(function (por) {
              return { snapshot: snap, porosity: por, nodemap: nm };
            });
          })
          .catch(function () {
            return refreshPorosity().then(function (por) {
              return { snapshot: snap, porosity: por };
            });
          });
      })
      .catch(function (e) {
        var j = e && e.json;
        addConsole(
          "err",
          (j && j.error) ? String(j.error).toUpperCase() : "FORGE_REFRESH",
          (j && j.detail) || e.message || String(e),
          j ? JSON.stringify(j, null, 2) : null
        );
      });
  }

  var DeckForge = {
    refresh: refresh,
    refreshPorosity: refreshPorosity,
    assign: assign,
    addAdversary: addAdversary,
    removeAdversary: removeAdversary,
    saveJobEstimate: saveJobEstimate,
    paintCcr: paintCcr,
    paintAdv: paintAdv,
    paintJob: paintJob,
    paintPorosity: paintPorosity,
  };

  global.DeckForge = DeckForge;
  global.forgeAssign = assign;
})(typeof globalThis !== "undefined" ? globalThis : this);
