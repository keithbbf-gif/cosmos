(function () {
  function mount(root) {
  if (!root || root.getAttribute("data-ready")) return;
  root.setAttribute("data-ready", "1");
  var game = root.getAttribute("data-game") || "higher";
  var KEY = "lmn-pid";
  var pid = localStorage.getItem(KEY);
  if (!pid) {
    pid = "p" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    localStorage.setItem(KEY, pid);
  }
  window.LMN_PID = pid;
  var timer = null;
  var matched = false;

  root.innerHTML = '<section class="card" aria-label="Queue"><h2>Queue</h2>' +
    '<p class="secondary">Pick who sits with you and who sits across. Human waits for another phone. Either takes a human if one is already waiting, and an AI after 8 seconds. Every bout is saved for the catalog. Player names are not.</p>' +
    '<label class="secondary">Name <input id="q-name" maxlength="16" value="Player" style="margin-left:8px;min-height:44px;border-radius:8px;padding:8px;background:#0B1220;color:#F6F2EA;border:1px solid rgba(255,255,255,.2)"></label>' +
    '<p><strong>Teammate</strong></p><div class="pit-bar">' +
    '<label class="btn thumb" style="background:transparent;color:#F6F2EA;border:1px solid rgba(246,242,234,.28)"><input type="checkbox" id="q-th"> Human</label>' +
    '<label class="btn thumb" style="background:#A5BB00;color:#070B14"><input type="checkbox" id="q-ta" checked> AI</label></div>' +
    '<p><strong>Enemy</strong></p><div class="pit-bar">' +
    '<label class="btn thumb" style="background:transparent;color:#F6F2EA;border:1px solid rgba(246,242,234,.28)"><input type="checkbox" id="q-eh"> Human</label>' +
    '<label class="btn thumb" style="background:#A5BB00;color:#070B14"><input type="checkbox" id="q-ea" checked> AI</label></div>' +
    '<p><button type="button" class="btn thumb" id="q-go">Play</button></p>' +
    '<p class="secondary" id="q-status" role="status"></p></section>';

  function mode(humanId, aiId) {
    var h = document.getElementById(humanId).checked;
    var a = document.getElementById(aiId).checked;
    if (h && a) return "either";
    if (h) return "human";
    return "ai";
  }

  function say(text) {
    document.getElementById("q-status").textContent = text;
  }

  function post(body) {
    body.pid = pid;
    return fetch("queue.php", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(body)
    }).then(function (res) { return res.json(); });
  }

  function showMatch(match) {
    if (matched) return;
    matched = true;
    if (timer) clearInterval(timer);
    var names = (match.seats || []).map(function (s) {
      return s.role + ": " + s.name + (s.kind === "human" ? "" : " (AI)");
    }).join(" · ");
    say("Matched. " + names);
    var board = document.getElementById("match-board");
    if (board) board.hidden = false;
    window.LMN_MATCH = match;
    if (window.LMN_BEGIN) window.LMN_BEGIN(match);
  }

  function poll() {
    post({ op: "poll" }).then(function (data) {
      if (!data) return;
      if (data.status === "matched" && data.match) showMatch(data.match);
      else say("In queue " + (data.wait || 0) + "s. " + (data.queued || 1) + " waiting on this game.");
    }).catch(function () { say("The queue did not answer."); });
  }

  document.getElementById("q-go").onclick = function () {
    if (!document.getElementById("q-th").checked && !document.getElementById("q-ta").checked) {
      document.getElementById("q-ta").checked = true;
    }
    if (!document.getElementById("q-eh").checked && !document.getElementById("q-ea").checked) {
      document.getElementById("q-ea").checked = true;
    }
    matched = false;
    say("Joining the queue.");
    post({
      op: "join",
      game: game,
      name: document.getElementById("q-name").value,
      teammate: mode("q-th", "q-ta"),
      enemy: mode("q-eh", "q-ea")
    }).then(function (data) {
      if (data && data.status === "matched" && data.match) showMatch(data.match);
      else {
        say("Waiting for a human seat.");
        if (timer) clearInterval(timer);
        timer = setInterval(poll, 1500);
      }
    }).catch(function () { say("The queue did not answer."); });
  };
  }
  window.LMN_MOUNT_LOBBY = mount;
  var first = document.getElementById("lobby");
  if (first) mount(first);
})();
