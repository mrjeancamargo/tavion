/*
 * Tavion service worker – makes the site installable and usable offline.
 * Pages: network first (always fresh), falling back to the last saved copy, then /offline.html.
 * CSS/JS/images on tavion.ie: network first too, with the saved copy used only when offline.
 * Other sites (Google Analytics, AdSense, fonts) are never touched.
 * Bump VERSION whenever this file changes.
 */
var VERSION = "tavion-v1";
var CORE = ["/", "/offline.html", "/assets/tavion.js", "/images/icon-192.png", "/images/favicon.png", "/manifest.webmanifest"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== VERSION; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== self.location.origin) return;

  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then(function (res) {
      var copy = res.clone();
      if (res.ok) caches.open(VERSION).then(function (c) { c.put(req, copy); });
      return res;
    }).catch(function () {
      return caches.match(req).then(function (hit) { return hit || caches.match("/offline.html"); });
    }));
    return;
  }

  // Rates and rules live in the JS files, so always try the network first – never show an old calculator.
  if (/\.(css|js|png|svg|jpg|jpeg|webp|json|webmanifest)$/.test(url.pathname)) {
    e.respondWith(fetch(req).then(function (res) {
      var copy = res.clone();
      if (res.ok) caches.open(VERSION).then(function (c) { c.put(req, copy); });
      return res;
    }).catch(function () { return caches.match(req); }));
  }
});
