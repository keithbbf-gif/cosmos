/* builds/cdeck/ui/sw.js — cDeck service worker (cdeck-shell-v12)
 * Handles offline fallback for the cDeck shell.
 */
"use strict";

var CACHE = "cdeck-shell-v12";
var SHELL = [
  "/cdeck/",
  "/cdeck/index.html",
  "/cdeck/app.js",
  "/cdeck/app.css",
  "/cdeck/cdeck.webmanifest",
  "/cdeck/sw.js",
  "/cdeck/header.js",
  "/cdeck/deck_more.html",
  "/cdeck/deck_tabs.js",
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) { return c.addAll(SHELL); })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE; })
            .map(function (k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", function (e) {
  var url = e.request.url;
  /* pass API calls through; only cache shell */
  if (url.indexOf("/api/") !== -1) return;
  e.respondWith(
    fetch(e.request)
      .catch(function () { return caches.match(e.request); })
  );
});
