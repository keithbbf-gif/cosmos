/* kdash_sw.js - COSMOS app-shell service worker (PWA installability + offline shell).
 *
 * SCOPE OF CACHING - deliberately tiny, and the exclusion is the point:
 *   CACHED (cache-first): the app SHELL only - the mobile page, the manifest,
 *     and this worker. That is what makes the client installable and lets the
 *     shell open on a dead connection.
 *   NEVER CACHED: anything under /api/ . Data must always be LIVE - a cached
 *     /api/v1/* response is the frozen-dashboard scar (a panel showing stale
 *     numbers with no age). API requests fall through to the network untouched
 *     (Authorization: Bearer header passes through; nothing is stored).
 *   Non-GET requests (POST /api/v1/command etc.) are never intercepted at all.
 *
 * Self-contained: no external URLs, no script imports of any kind.
 */
"use strict";

var CACHE = "cosmos-shell-v1";
/* the shell allowlist - note there is NO /api/ path in it, by design */
var SHELL = ["/m", "/kdash_manifest.webmanifest", "/kdash_sw.js"];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE)
      .then(function (c) { return c.addAll(SHELL); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; })
                             .map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") {
    return;                       /* POSTs (commands) go straight to the network */
  }
  var url = new URL(e.request.url);
  if (url.pathname.indexOf("/api/") === 0) {
    return;                       /* NEVER cache /api/ - data stays live, always */
  }
  /* shell: cache-first, network fallback; only allowlisted paths are ever put */
  e.respondWith(
    caches.match(e.request).then(function (hit) {
      if (hit) { return hit; }
      return fetch(e.request).then(function (resp) {
        if (resp && resp.ok && SHELL.indexOf(url.pathname) !== -1) {
          var copy = resp.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
        }
        return resp;
      });
    })
  );
});
