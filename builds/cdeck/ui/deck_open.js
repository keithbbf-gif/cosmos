"use strict";
// deck_open.js — Open tab: OpenWork display (Core GET /api/v1/openwork)
(function () {
  var hdr = window.cdeckHeader || {};
  var apiGet = hdr.apiGet;
  var apiPost = hdr.apiPost;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function liveLabel(rec) {
    if (rec && rec.live) return "LIVE";
    if (rec && rec.kind === "NO_SOURCE") return "UNMEASURED";
    return "DOWN";
  }

  function paintOpen(stage) {
    if (!stage || typeof apiGet !== "function") return;
    stage.innerHTML = '<p class="dim">measuring OpenWork…</p>';
    apiGet("/api/v1/openwork")
      .then(function (rec) {
        var chip = liveLabel(rec);
        var note = (rec && rec.note) ? String(rec.note) : "";
        var ports = (rec && rec.workspace_ports) || [];
        var probes = (rec && rec.health_probes) || [];
        var exe = (rec && rec.exe) || {};
        var h = "";
        h += '<div class="open-hd"><span class="chip open-live">' + esc(chip) + "</span>";
        h += ' <button type="button" class="studio-go" id="owFocusBtn">OPEN (focus live)</button></div>';
        h += '<p class="dim tiny">' + esc(note) + "</p>";
        h += "<p>exe: " + esc(exe.present ? "present" : "UNMEASURED") + "</p>";
        if (ports.length) {
          h += "<ul>";
          ports.forEach(function (row, i) {
            var pr = probes[i] || {};
            h += "<li>" + esc(row.workspace) + " : " + esc(row.port);
            h += pr.ok ? " /health ok" : " /health down";
            h += "</li>";
          });
          h += "</ul>";
        } else {
          h += '<p class="dim">No workspacePorts in state — port UNMEASURED (not :8770).</p>';
        }
        stage.innerHTML = h;
        var btn = document.getElementById("owFocusBtn");
        if (btn && typeof apiPost === "function") {
          btn.addEventListener("click", function () {
            apiPost("/api/v1/openwork", { action: "focus" }).then(function (ans) {
              var msg = (ans && ans.detail) ? String(ans.detail) : JSON.stringify(ans);
              stage.insertAdjacentHTML("beforeend", "<p class=\"tiny\">" + esc(msg) + "</p>");
            }).catch(function (e) {
              stage.insertAdjacentHTML(
                "beforeend",
                "<p class=\"tiny err\">" + esc(e.message || String(e)) + "</p>"
              );
            });
          });
        }
      })
      .catch(function (e) {
        stage.innerHTML = "<p class=\"err\">" + esc(e.message || String(e)) + "</p>";
      });
  }

  window.cdeckPaneOpen = { paint: paintOpen };
})();
