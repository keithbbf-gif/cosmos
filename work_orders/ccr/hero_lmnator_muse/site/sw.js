var CACHE = "lmnator-arcade-1";
var FILES = ["arcade.html", "arcade.js", "engines.js", "save.js", "buy.js", "lobby.js", "board.json", "favicon.svg", "site.css", "family.css", "manifest.webmanifest"];
self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) { return cache.addAll(FILES); }));
  self.skipWaiting();
});
self.addEventListener("activate", function (event) { event.waitUntil(self.clients.claim()); });
self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") return;
  event.respondWith(caches.match(event.request).then(function (hit) { return hit || fetch(event.request); }));
});
