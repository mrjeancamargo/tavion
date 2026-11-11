/*
 * Tavion site-wide script: Google Tag Manager / Google Analytics 4 + AdSense loader + click tracking.
 * Loaded on EVERY page. Your IDs go here — this is the only place they need to go.
 *
 * Use EITHER gtmId (Google Tag Manager) OR gaId (Google Analytics directly), not both,
 * otherwise every visit is counted twice.
 */
window.TAVION = {
  gtmId: "",                                 // Google Tag Manager container ID (e.g. "GTM-N3GQGR49") – leave empty while using gaId
  gaId: "G-Q9DV6F3296",                      // Google Analytics 4 Measurement ID (stream "tavion", https://tavion.ie)
  adsenseClient: "ca-pub-1290266452162223"   // Google AdSense publisher ID
};

(function () {
  var CFG = window.TAVION;

  // Which part of the site this page belongs to ("home", "services", "driving", ...).
  // Lets you compare apps against each other in Google Analytics.
  var seg = location.pathname.split("/").filter(Boolean)[0] || "home";
  var section = /\.html$/.test(seg) ? seg.replace(/\.html$/, "") : seg;
  if (section === "index") section = "home";

  // ---- Consent Mode v2 ----
  // EU/EEA/UK/Swiss visitors: nothing is stored until they accept in Google's consent
  // banner (turn it on in AdSense > Privacy & messaging). Everyone else: allowed by default.
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  var EEA = ["AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE","IS","LI","NO","GB","CH"];
  gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: "denied", region: EEA, wait_for_update: 500 });
  gtag("consent", "default", { ad_storage: "granted", ad_user_data: "granted", ad_personalization: "granted", analytics_storage: "granted" });

  // Available in Tag Manager as a Data Layer Variable named "app_section".
  window.dataLayer.push({ app_section: section });

  function load(src) {
    var s = document.createElement("script");
    s.async = true; s.src = src;
    document.head.appendChild(s);
    return s;
  }

  // ---- Google Tag Manager ----
  if (CFG.gtmId) {
    window.dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
    load("https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(CFG.gtmId));
  }

  // ---- Google Analytics 4 (direct, without Tag Manager) ----
  if (CFG.gaId && !CFG.gtmId) {
    load("https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(CFG.gaId));
    gtag("js", new Date());
    gtag("set", { app_section: section });
    gtag("config", CFG.gaId);
  }

  // ---- Google AdSense ----
  // Loaded once per page. Needed on every page for AdSense site approval and its consent banner.
  if (CFG.adsenseClient) {
    load("https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(CFG.adsenseClient)).crossOrigin = "anonymous";
  }

  // ---- Event tracking ----
  // TAVION.track("exam_start", { test: "car" })
  // With Tag Manager, each call becomes a dataLayer event: { event: "exam_start", test: "car", ... }
  var KEYS = ["label", "method", "link_url", "test", "mode", "topic", "question_id", "correct", "score", "total", "answered", "percent", "result", "time_up", "minutes", "tax_year", "status", "salary_band", "period", "advanced"];
  CFG.track = function (name, params) {
    params = params || {};
    params.app_section = section;
    if (CFG.gtmId) {
      var msg = { event: name };
      KEYS.forEach(function (k) { msg[k] = undefined; }); // clear values left over from earlier events
      for (var k in params) msg[k] = params[k];
      window.dataLayer.push(msg);
    } else if (CFG.gaId) {
      gtag("event", name, params);
    }
    if (/localhost|127\.0\.0\.1/.test(location.hostname)) console.info("[track]", name, params);
  };

  // Any element with data-track="event_name" (and optional data-label="...") is tracked when clicked.
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("[data-track]");
    if (!el) return;
    var p = {};
    if (el.getAttribute("data-label")) p.label = el.getAttribute("data-label");
    if (el.getAttribute("data-method")) p.method = el.getAttribute("data-method");
    if (el.href) p.link_url = el.href;
    CFG.track(el.getAttribute("data-track"), p);
  }, true);
})();

/*
 * Installable app (PWA): manifest + service worker + a small, dismissible install bar.
 * Android/desktop Chrome & Edge: uses the browser's own install prompt.
 * iPhone/iPad Safari: shows a one-line tip (Share → Add to Home Screen) – Apple has no install prompt.
 * Shown from the 2nd page view, never inside the installed app, and hidden for 21 days after "Not now".
 */
(function () {
  var head = document.head;
  function add(tag, attrs) { var el = document.createElement(tag); for (var k in attrs) el.setAttribute(k, attrs[k]); head.appendChild(el); }
  if (!document.querySelector('link[rel="manifest"]')) add("link", { rel: "manifest", href: "/manifest.webmanifest" });
  add("meta", { name: "apple-mobile-web-app-capable", content: "yes" });
  add("meta", { name: "mobile-web-app-capable", content: "yes" });
  add("meta", { name: "apple-mobile-web-app-title", content: "Tavion" });
  add("meta", { name: "apple-mobile-web-app-status-bar-style", content: "black-translucent" });

  if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
    window.addEventListener("load", function () { navigator.serviceWorker.register("/sw.js").catch(function () {}); });
  }

  var track = function (n, p) { if (window.TAVION && TAVION.track) TAVION.track(n, p || {}); };
  var standalone = (window.matchMedia && matchMedia("(display-mode: standalone)").matches) || navigator.standalone === true;
  if (standalone) { track("app_open", { label: location.pathname }); return; }

  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  var views = (+store.get("tavion_views") || 0) + 1; store.set("tavion_views", views);
  var snoozed = (+store.get("tavion_install_snooze") || 0) > Date.now();
  var ua = navigator.userAgent, ios = /iphone|ipad|ipod/i.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  var safari = ios && !/crios|fxios|edgios|fban|fbav|instagram/i.test(ua);
  var deferred = null;

  function css() {
    if (document.getElementById("tv-inst-css")) return;
    var s = document.createElement("style"); s.id = "tv-inst-css";
    s.textContent = ".tv-inst{position:fixed;left:12px;right:12px;bottom:12px;z-index:9999;max-width:520px;margin:0 auto;display:flex;gap:10px;align-items:center;" +
      "background:#0f1726;color:#f1f5f9;border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:10px 10px 10px 12px;box-shadow:0 10px 30px rgba(0,0,0,.35);" +
      "font:15px/1.35 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}.tv-inst img{width:40px;height:40px;border-radius:10px;flex:0 0 40px}" +
      ".tv-inst p{margin:0;flex:1}.tv-inst b{display:block}.tv-inst small{color:#94a3b8}.tv-inst button{font:inherit;font-weight:700;border:0;border-radius:10px;cursor:pointer;min-height:40px}" +
      ".tv-inst .go{background:#38bdf8;color:#06121c;padding:0 14px}.tv-inst .x{background:transparent;color:#94a3b8;padding:0 8px;font-size:22px;line-height:1}" +
      ".tv-share{display:inline-block;width:14px;height:16px;vertical-align:-2px;margin:0 2px}";
    head.appendChild(s);
  }
  function bar(html, onGo) {
    if (document.querySelector(".tv-inst")) return;
    css();
    var b = document.createElement("div"); b.className = "tv-inst"; b.setAttribute("role", "dialog"); b.setAttribute("aria-label", "Install Tavion");
    b.innerHTML = '<img src="/images/icon-192.png" alt="">' + html + '<button class="x" aria-label="Not now">×</button>';
    document.body.appendChild(b);
    b.querySelector(".x").addEventListener("click", function () { b.remove(); store.set("tavion_install_snooze", Date.now() + 21 * 864e5); track("install_dismiss"); });
    var go = b.querySelector(".go"); if (go) go.addEventListener("click", function () { onGo(b); });
    track("install_bar_shown", { label: ios ? "ios" : "prompt" });
  }

  // Android / desktop: the browser tells us when the app can be installed.
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault(); deferred = e;
    document.querySelectorAll("[data-install]").forEach(function (el) { el.hidden = false; });
    if (views >= 2 && !snoozed) bar('<p><b>Get the Tavion app</b><small>Free, no sign-up – opens from your home screen</small></p><button class="go">Install</button>', function (b) { install(); b.remove(); });
  });
  window.addEventListener("appinstalled", function () { track("app_installed"); var b = document.querySelector(".tv-inst"); if (b) b.remove(); });

  function install() {
    if (!deferred) return;
    deferred.prompt(); track("install_prompt");
    deferred.userChoice.then(function (c) { track("install_choice", { result: c.outcome }); deferred = null; });
  }
  window.TAVION = window.TAVION || {}; window.TAVION.install = install;

  // iPhone / iPad Safari: no prompt exists, so show how to do it.
  var shareIcon = '<svg class="tv-share" viewBox="0 0 14 16" aria-hidden="true"><path fill="#38bdf8" d="M7 0l3.5 3.5-1 1L7.7 2.7V10H6.3V2.7L4.5 4.5l-1-1zM1 6h3v1.4H2.4v7.2h9.2V7.4H10V6h3v10H1z"/></svg>';
  function iosTip() { bar('<p><b>Add Tavion to your home screen</b><small>Tap ' + shareIcon + ' Share, then <b style="display:inline">Add to Home Screen</b></small></p>'); }
  document.addEventListener("DOMContentLoaded", function () {
    // Any element with data-install becomes an "Install" button (shown when installing is possible).
    document.querySelectorAll("[data-install]").forEach(function (el) {
      if (safari) el.hidden = false;
      el.addEventListener("click", function (e) { e.preventDefault(); if (deferred) install(); else if (safari) iosTip(); });
    });
    if (safari && views >= 2 && !snoozed) setTimeout(iosTip, 4000);
  });
})();
