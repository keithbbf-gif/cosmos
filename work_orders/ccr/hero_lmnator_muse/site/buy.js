(function () {
  var API = "https://api.tokenctr.com";
  var KEY = "lmnator-tc-key";
  var NONCE = "lmnator-buy-nonce";
  var PURSE = "lmnator-game-tokens";

  function purse() {
    var raw = localStorage.getItem(PURSE);
    if (raw == null) {
      localStorage.setItem(PURSE, "40");
      return 40;
    }
    var n = parseInt(raw, 10);
    return isFinite(n) && n >= 0 ? n : 0;
  }

  function paint(n) {
    var nodes = document.querySelectorAll(".game-purse");
    for (var i = 0; i < nodes.length; i++) nodes[i].textContent = "Game tokens: " + n;
  }

  function setPurse(n) {
    localStorage.setItem(PURSE, String(n));
    paint(n);
  }

  function say(text) {
    var nodes = document.querySelectorAll("#buy-msg");
    for (var i = 0; i < nodes.length; i++) nodes[i].textContent = text;
  }

  function post(path, body, key) {
    var headers = { "Accept": "application/json", "Content-Type": "application/json" };
    if (key) headers.Authorization = "Bearer " + key;
    return fetch(API + path, { method: "POST", headers: headers, body: JSON.stringify(body || {}) }).then(function (res) {
      return res.text().then(function (t) {
        var data = null;
        try { data = JSON.parse(t); } catch (e) { data = null; }
        return { status: res.status, body: data };
      });
    });
  }

  function showKey(key) {
    return new Promise(function (resolve) {
      var box = document.createElement("div");
      box.className = "shop-card";
      box.innerHTML = "<p>TokenCenter made a key for this checkout. It is shown once. AI tokens land on it. Save it, then continue. LMNator does not keep a copy on the server.</p>";
      var ta = document.createElement("textarea");
      ta.readOnly = true;
      ta.rows = 2;
      ta.value = key;
      ta.style.cssText = "width:100%;box-sizing:border-box;margin:8px 0;font-family:ui-monospace,monospace;";
      var go = document.createElement("button");
      go.type = "button";
      go.className = "btn thumb";
      go.textContent = "I saved it. Continue to checkout.";
      go.addEventListener("click", function () {
        if (box.parentNode) box.parentNode.removeChild(box);
        resolve();
      });
      box.appendChild(ta);
      box.appendChild(go);
      var msg = document.getElementById("buy-msg");
      (msg ? msg.parentNode : document.body).appendChild(box);
    });
  }

  function ensureKey() {
    var existing = "";
    try { existing = localStorage.getItem(KEY) || ""; } catch (e) { existing = ""; }
    if (existing) return Promise.resolve(existing);
    say("Asking TokenCenter for a key.");
    return post("/v1/account/anonymous", {}, "").then(function (r) {
      var key = r.body && (r.body.api_key || r.body.key);
      if (r.status !== 200 || typeof key !== "string" || !key) {
        throw new Error("TokenCenter did not create a key. Nothing was charged.");
      }
      localStorage.setItem(KEY, key);
      return showKey(key).then(function () { return key; });
    });
  }

  function checkoutUrl(body) {
    return body && body.checkout && (body.checkout.url || body.checkout.checkout_url);
  }

  function start(btn) {
    if (btn.disabled) return;
    var kind = btn.getAttribute("data-lmn-buy");
    var amount = Number(btn.getAttribute("data-amount"));
    var grant = Number(btn.getAttribute("data-grant") || "0");
    var pack = btn.getAttribute("data-pack") || "";
    var nonce = Math.random().toString(36).slice(2) + Date.now().toString(36);
    sessionStorage.setItem(NONCE, JSON.stringify({ nonce: nonce, kind: kind, grant: grant }));
    var back = "https://lmnator.com/account.html?back=1&kind=" + encodeURIComponent(kind) + "&n=" + encodeURIComponent(nonce);
    var cancel = "https://lmnator.com/derby.html?back=cancel";
    btn.disabled = true;
    ensureKey().then(function (key) {
      var body = { amount_usd: amount, processor: "stripe", success_url: back, cancel_url: cancel };
      if (kind === "game") body.pack_id = "lmnator-game";
      if (pack) body.pack_id = pack;
      say("TokenCenter is opening checkout for $" + amount + ".");
      return post("/v1/credits/purchase", body, key).then(function (r) {
        if (r.status !== 200) return post("/v1/credits/purchase", { amount_usd: amount, processor: "stripe", success_url: back, cancel_url: cancel }, key);
        return r;
      });
    }).then(function (r) {
      var url = checkoutUrl(r.body);
      if (r.status === 200 && typeof url === "string" && url.indexOf("https://") === 0) {
        window.location.assign(url);
        return;
      }
      btn.disabled = false;
      say("Checkout did not open. Nothing was charged.");
    }).catch(function (e) {
      btn.disabled = false;
      say((e && e.message) || "TokenCenter did not answer. Nothing was charged.");
    });
  }

  function land() {
    var q = new URLSearchParams(location.search);
    if (q.get("back") !== "1") return;
    var saved = null;
    try { saved = JSON.parse(sessionStorage.getItem(NONCE) || "null"); } catch (e) { saved = null; }
    if (saved && saved.nonce && saved.nonce === q.get("n")) {
      sessionStorage.removeItem(NONCE);
      if (saved.kind === "game" && saved.grant > 0) {
        setPurse(purse() + saved.grant);
        say("Game tokens are on this account. TokenCenter charged the card. Their site does not list this pack.");
      } else if (saved.kind === "ai") {
        say("AI tokens are call credit on the TokenCenter key from checkout. They are not game tokens.");
      }
    }
    if (window.history && history.replaceState) history.replaceState({}, "", location.pathname);
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target && ev.target.closest ? ev.target.closest("[data-lmn-buy]") : null;
    if (!btn) return;
    ev.preventDefault();
    start(btn);
  });

  paint(purse());
  land();
  window.LMNPurse = { get: purse, set: setPurse };
})();
