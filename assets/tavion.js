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
  var KEYS = ["label", "method", "link_url", "test", "mode", "topic", "question_id", "correct", "score", "total", "answered", "percent", "result", "time_up", "minutes"];
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
