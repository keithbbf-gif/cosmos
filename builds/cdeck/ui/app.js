/* builds/cdeck/ui/app.js — MESH widgets + jukebox job projection for Runs. */
(function () {
  "use strict";

  var RUNS_POLL_MS = 10000;
  var lastJukeboxBody = null;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function $(id) { return document.getElementById(id); }

  /** Normalize jukebox GET body → job rows (never GET /api/v1/jobs for Runs). */
  function jobsFromJukebox(d) {
    if (!d || typeof d !== "object") return [];
    var q = d.queue;
    if (q && Array.isArray(q.jobs)) return q.jobs.slice();
    if (Array.isArray(d.jobs)) return d.jobs.slice();
    if (Array.isArray(d.shown)) return d.shown.slice();
    return [];
  }

  /**
   * renderJobs — paint hook for jukebox fold (list+detail source is GET /jukebox).
   * Legacy { jobs: { id: st } } maps are accepted for MESH summary only.
   */
  function renderJobs(d) {
    if (!d) return;
    lastJukeboxBody = d;
    window.__lastJukeboxBody = d;

    var rows = jobsFromJukebox(d);
    if (rows.length === 0 && d.jobs && typeof d.jobs === "object" && !Array.isArray(d.jobs)) {
      rows = Object.keys(d.jobs).map(function (id) {
        return { job_id: id, st: d.jobs[id] };
      });
    }

    var el = $("mesh-jobs-summary");
    if (!el) return;

    if (rows.length === 0) {
      el.innerHTML = '<span class="dim">no jobs in jukebox fold</span>';
      return;
    }
    var by = {};
    rows.forEach(function (j) {
      var st = String(j.st || j.state || "UNMEASURED").toUpperCase();
      by[st] = (by[st] || 0) + 1;
    });
    var parts = Object.keys(by).sort().map(function (st) {
      return esc(st) + "×" + by[st];
    });
    el.innerHTML = parts.join(" · ");
  }

  function pollJukebox() {
    return apiGet("/api/v1/jukebox").then(function (body) {
      renderJobs(body);
      if (window.deckStudio && typeof window.deckStudio.paintRunsList === "function") {
        window.deckStudio.paintRunsList(body);
      }
      return body;
    });
  }

  function startJukeboxPoll() {
    if (window.__jukeboxPollStarted) return;
    window.__jukeboxPollStarted = true;
    pollJukebox().catch(function () { /* pane shows last-good or empty */ });
    setInterval(function () {
      pollJukebox().catch(function () { /* keep filter chip state in deck_studio */ });
    }, RUNS_POLL_MS);
  }

  window.RUNS_POLL_MS = RUNS_POLL_MS;
  window.renderJobs = renderJobs;
  window.jobsFromJukebox = jobsFromJukebox;
  window.pollJukebox = pollJukebox;
  window.startJukeboxPoll = startJukeboxPoll;
  window.cdeckEsc = esc;
  window.cdeck$ = $;

  /* --- MESH music jukebox (Holst planets mp3; not YouTube) --- */
  var PLANET_TRACKS = [
    { id: "mercury", label: "Mercury", src: "planets/mercury.mp3" },
    { id: "venus", label: "Venus", src: "planets/venus.mp3" },
    { id: "mars", label: "Mars", src: "planets/mars.mp3" },
    { id: "jupiter", label: "Jupiter", src: "planets/jupiter.mp3" },
    { id: "saturn", label: "Saturn", src: "planets/saturn.mp3" },
    { id: "uranus", label: "Uranus", src: "planets/uranus.mp3" },
    { id: "neptune", label: "Neptune", src: "planets/neptune.mp3" }
  ];
  var jukeIdx = 0;
  var jukeAudio = null;

  function planetSrc(rel) {
    if (!rel || String(rel).indexOf("planets/") !== 0) return "";
    var base = window.location.pathname || "";
    if (base.indexOf("/cdeck") === -1) base = "/cdeck/";
    else if (!base.endsWith("/")) base = base.replace(/\/[^/]*$/, "/");
    return base + rel;
  }

  function paintNowPlaying() {
    var el = $("jukeNowPlaying");
    if (!el || !jukeAudio) return;
    var tr = PLANET_TRACKS[jukeIdx];
    if (!tr) {
      el.textContent = "UNMEASURED";
      return;
    }
    var state = "stopped";
    if (!jukeAudio.paused && !jukeAudio.ended && jukeAudio.currentTime > 0) {
      state = "playing";
    } else if (!jukeAudio.paused && jukeAudio.readyState >= 2) {
      state = "playing";
    } else if (jukeAudio.currentTime > 0 && jukeAudio.paused) {
      state = "paused";
    }
    el.textContent = tr.label + " · " + state;
  }

  function paintVolumePct() {
    var pct = $("jukeVolumePct");
    if (!pct || !jukeAudio) return;
    pct.textContent = String(Math.round(jukeAudio.volume * 100)) + "%";
  }

  function loadPlanet(idx, autoplay) {
    if (!PLANET_TRACKS.length) return;
    jukeIdx = ((idx % PLANET_TRACKS.length) + PLANET_TRACKS.length) % PLANET_TRACKS.length;
    var tr = PLANET_TRACKS[jukeIdx];
    jukeAudio.src = planetSrc(tr.src);
    jukeAudio.load();
    paintNowPlaying();
    if (autoplay) {
      jukeAudio.play().catch(function () { paintNowPlaying(); });
    }
  }

  function wireJukeboxControls(host) {
    if (host && host.dataset.jukeWired) return;
    if (host) host.dataset.jukeWired = "1";
    jukeAudio = $("jukeAudio");
    if (!jukeAudio) return;

    jukeAudio.addEventListener("play", paintNowPlaying);
    jukeAudio.addEventListener("pause", paintNowPlaying);
    jukeAudio.addEventListener("ended", function () {
      loadPlanet(jukeIdx + 1, true);
    });
    jukeAudio.addEventListener("error", paintNowPlaying);

    var vol = $("jukeVolume");
    if (vol) {
      vol.addEventListener("input", function () {
        var v = Number(vol.value);
        if (Number.isFinite(v)) {
          jukeAudio.volume = Math.min(1, Math.max(0, v / 100));
        }
        paintVolumePct();
      });
      jukeAudio.volume = Math.min(1, Math.max(0, Number(vol.value) / 100));
      paintVolumePct();
    }

    var playBtn = $("btnJukePlay");
    if (playBtn) {
      playBtn.addEventListener("click", function () {
        if (!jukeAudio.src) loadPlanet(jukeIdx, false);
        jukeAudio.play().catch(function () { paintNowPlaying(); });
      });
    }
    var pauseBtn = $("btnJukePause");
    if (pauseBtn) {
      pauseBtn.addEventListener("click", function () {
        jukeAudio.pause();
        paintNowPlaying();
      });
    }
    var nextBtn = $("btnJukeNext");
    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        loadPlanet(jukeIdx + 1, !jukeAudio.paused);
      });
    }

    loadPlanet(0, false);
  }

  /** Build / refresh MESH jukebox chrome (audio element only — no iframe). */
  function renderJukebox() {
    var host = $("jukeEl");
    if (!host) return;
    if (!host.dataset.jukeBuilt) {
      host.dataset.jukeBuilt = "1";
      host.innerHTML =
        '<div class="mesh-juke-hd"><h2>Jukebox</h2>' +
        '<span class="dim tiny">planets/*.mp3 on Core /cdeck/</span></div>' +
        '<div id="ytwrap" class="juke-audio-wrap">' +
        '<audio id="jukeAudio" preload="metadata"></audio></div>' +
        '<div class="juke-controls">' +
        '<button type="button" id="btnJukePlay">PLAY</button>' +
        '<button type="button" id="btnJukePause">PAUSE</button>' +
        '<button type="button" id="btnJukeNext">NEXT</button>' +
        '<label class="juke-vol">Vol <input type="range" id="jukeVolume" min="0" max="100" value="80">' +
        '<span id="jukeVolumePct">80%</span></label></div>' +
        '<p class="juke-now" id="jukeNowPlaying">—</p>' +
        '<p class="dim tiny" id="mesh-jobs-summary"></p>';
    }
    wireJukeboxControls(host);
  }

  function initMeshJukebox() {
    renderJukebox();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMeshJukebox);
  } else {
    initMeshJukebox();
  }

  window.renderJukebox = renderJukebox;
  window.PLANET_TRACKS = PLANET_TRACKS;
}());
