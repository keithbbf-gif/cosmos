/* XTalk standalone page. Same Core routes as the cDeck tab.
   Served at /xtalk/ (same origin) so fetch works. No iframe. No pen.
   Empty = UNMEASURED. Transport A is a typed hole, never a fake inject. */
(function (global) {
  "use strict";

  var POLL_MS = 4000;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c];
    });
  }

  function $(id, root) {
    return (root || document).getElementById(id);
  }

  function coreBase() {
    if (location.protocol === "http:" || location.protocol === "https:") {
      if (location.port === "8770" || location.pathname.indexOf("/xtalk") === 0
          || location.pathname.indexOf("/cdeck") === 0) {
        return location.origin;
      }
    }
    return "http://127.0.0.1:8770";
  }

  function XTalkPage(opts) {
    this.opts = opts || {};
    this.ids = this.opts.ids || {
      honesty: "xtHonesty",
      age: "xtAge",
      bind: "xtBind",
      roles: "xtRoles",
      log: "xtLog",
      empty: "xtEmpty",
      verify: "xtVerify",
      from: "xtFrom",
      to: "xtTo",
      body: "xtBody",
      send: "xtSend",
      err: "xtErr"
    };
    this.api = this.opts.api || null;
    this.rec = null;
    this.err = "";
    this.inflight = false;
    this.timer = null;
    this.bind = this.opts.bind || "";
    this.notice = "";
  }

  XTalkPage.prototype.tabOn = function () {
    if (typeof this.opts.tabOn === "function") return this.opts.tabOn();
    return true;
  };

  XTalkPage.prototype.get = function (path) {
    if (typeof this.api === "function") return this.api(path);
    var url = coreBase() + path;
    return fetch(url, { headers: { Accept: "application/json" } }).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) {
          var e = new Error((j && (j.error || j.detail)) || ("HTTP " + r.status));
          e.status = r.status;
          e.body = j;
          throw e;
        }
        return j;
      });
    });
  };

  XTalkPage.prototype.post = function (path, body) {
    if (typeof this.api === "function") {
      return this.api(path, { method: "POST", body: body });
    }
    return fetch(coreBase() + path, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body)
    }).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) {
          var e = new Error((j && (j.error || j.detail)) || ("HTTP " + r.status));
          e.status = r.status;
          e.body = j;
          throw e;
        }
        return j;
      });
    });
  };

  XTalkPage.prototype.fillTo = function (roles) {
    var sel = $(this.ids.to);
    if (!sel) return;
    var names = Object.keys(roles || {});
    if (!names.length) return;
    var cur = sel.value;
    sel.innerHTML = names.map(function (n) {
      var t = (roles[n] || {}).transport || "?";
      return "<option value=\"" + esc(n) + "\">" + esc(n) + " · " + t + "</option>";
    }).join("");
    if (cur && roles[cur]) sel.value = cur;
    else {
      var b = names.filter(function (n) { return (roles[n] || {}).transport === "B"; })[0];
      sel.value = b || names[0];
    }
  };

  XTalkPage.prototype.qs = function () {
    var role = (this.opts.role || "").trim();
    var bindEl = $(this.ids.bind);
    var bind = (bindEl && bindEl.value) || this.bind || "";
    var q = "/api/v1/xtalk?tail=80&verify=1";
    if (role) q += "&role=" + encodeURIComponent(role);
    if (bind) q += "&bind=" + encodeURIComponent(bind);
    return q;
  };

  XTalkPage.prototype.paint = function () {
    var honesty = $(this.ids.honesty);
    var age = $(this.ids.age);
    var log = $(this.ids.log);
    var empty = $(this.ids.empty);
    var rolesEl = $(this.ids.roles);
    var verEl = $(this.ids.verify);
    var errEl = $(this.ids.err);
    if (this.err) {
      if (honesty) honesty.textContent = "UNMEASURED";
      if (age) age.textContent = this.err;
      if (empty) {
        empty.classList.remove("hidden");
        empty.innerHTML = "<div>UNMEASURED</div><div class=\"hint\">" + esc(this.err) + "</div>";
      }
      if (verEl) {
        verEl.textContent = "";
        verEl.className = "tiny dim";
      }
      if (errEl) errEl.textContent = this.err;
      return;
    }
    var rec = this.rec || {};
    var kind = rec.kind || "UNMEASURED";
    if (honesty) honesty.textContent = kind;
    if (age) age.textContent = (rec.bind || "local") + " · n " +
      (rec.n == null ? "UNMEASURED" : rec.n) +
      (rec.seq != null ? " · seq " + rec.seq : "") +
      (rec.writable === false ? " · read-only" : "");
    if (errEl) errEl.textContent = this.notice || "";
    if (verEl) {
      var v = rec.verify || [];
      verEl.textContent = v.length ? v.join(" · ") : "";
      verEl.className = "tiny " + (v[0] && String(v[0]).indexOf("chain clean") === 0 ? "ok" : "dim");
    }
    if (rolesEl) {
      var roles = rec.roles || {};
      var names = Object.keys(roles);
      if (!names.length) {
        rolesEl.textContent = "roles UNMEASURED";
      } else {
        rolesEl.innerHTML = names.map(function (n) {
          var r = roles[n] || {};
          var t = r.transport || "?";
          var cls = t === "B" ? "ok" : (t === "A" ? "warn" : "dim");
          return "<button type=\"button\" class=\"chip " + cls +
            "\" data-xt-to=\"" + esc(n) + "\">" + esc(n) + " · " + esc(t) +
            " · " + esc(r.harness || "") + "</button>";
        }).join(" ");
        this.fillTo(roles);
      }
    }
    var lines = rec.lines || [];
    if (!lines.length) {
      if (empty) {
        empty.classList.remove("hidden");
        empty.innerHTML = "<div>" + esc(kind) + "</div><div class=\"hint\">" +
          esc(rec.note || "no lines. POST Transport B when a live owner is seated.") +
          "</div>";
      }
      if (log) {
        var kids = log.querySelectorAll(".xt-turn");
        for (var i = 0; i < kids.length; i++) kids[i].remove();
      }
      return;
    }
    if (empty) empty.classList.add("hidden");
    if (!log) return;
    var stale = log.querySelectorAll(".xt-turn");
    for (var s = 0; s < stale.length; s++) stale[s].remove();
    var html = lines.map(function (row) {
      row = row || {};
      var m = row.msg || {};
      return "<div class=\"xt-turn t-" + esc(row.transport || "") + "\">" +
        "<span class=\"tiny dim\">#" + esc(row.seq) + " · " +
        esc(m.from) + " → " + esc(m.to) + " · " + esc(row.transport) + "</span>" +
        "<div>" + esc(m.body) + "</div></div>";
    }).join("");
    // #xtEmpty is a child of #xtLog. Do not replace the parent's innerHTML.
    if (empty && empty.parentNode === log) empty.insertAdjacentHTML("beforebegin", html);
    else log.insertAdjacentHTML("beforeend", html);
    log.scrollTop = log.scrollHeight;
  };

  XTalkPage.prototype.tick = function () {
    var self = this;
    if (!this.tabOn()) return;
    if (this.inflight) return;
    this.inflight = true;
    this.get(this.qs()).then(function (rec) {
      self.rec = rec;
      self.err = "";
      self.paint();
    }).catch(function (e) {
      self.notice = "";
      self.err = String(e && e.message || e);
      self.paint();
    }).then(function () { self.inflight = false; });
  };

  XTalkPage.prototype.send = function () {
    var self = this;
    var frm = $(this.ids.from);
    var to = $(this.ids.to);
    var body = $(this.ids.body);
    var text = body && body.value ? String(body.value).trim() : "";
    var fromV = frm && frm.value ? String(frm.value).trim() : "captain";
    var toV = to && to.value ? String(to.value).trim() : "";
    if (!text || !toV) return;
    this.notice = "";
    this.post("/api/v1/xtalk", { from: fromV, to: toV, body: text, role: "captain" })
      .then(function (rec) {
        if (body) body.value = "";
        if (rec && rec.kind === "DRY_RUN") {
          // DRY_RUN is a notice, not a failed GET.
          self.err = "";
          self.notice = "DRY_RUN A · " + (rec.harness || "") + " · no inject · no append";
          self.tick();
          return;
        }
        self.notice = "";
        self.tick();
      })
      .catch(function (e) {
        self.err = String(e && e.message || e);
        self.paint();
      });
  };

  XTalkPage.prototype.mount = function () {
    var self = this;
    this.tick();
    if (this.timer) clearInterval(this.timer);
    this.timer = setInterval(function () { self.tick(); }, POLL_MS);
    var btn = $(this.ids.send);
    if (btn && !btn._xtBound) {
      btn._xtBound = true;
      btn.addEventListener("click", function () { self.send(); });
    }
    var body = $(this.ids.body);
    if (body && !body._xtBound) {
      body._xtBound = true;
      body.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" && (ev.ctrlKey || ev.metaKey)) {
          ev.preventDefault();
          self.send();
        }
      });
    }
    var bindEl = $(this.ids.bind);
    if (bindEl && !bindEl._xtBound) {
      bindEl._xtBound = true;
      bindEl.addEventListener("change", function () { self.tick(); });
    }
    var rolesEl = $(this.ids.roles);
    if (rolesEl && !rolesEl._xtBound) {
      rolesEl._xtBound = true;
      rolesEl.addEventListener("click", function (ev) {
        var t = ev.target && ev.target.closest && ev.target.closest("[data-xt-to]");
        if (!t) return;
        var sel = $(self.ids.to);
        if (sel) sel.value = t.getAttribute("data-xt-to");
      });
    }
  };

  global.XTalkPage = XTalkPage;
  global.initXTalkStandalone = function () {
    var page = new XTalkPage({});
    page.mount();
    return page;
  };
})(typeof window !== "undefined" ? window : this);
