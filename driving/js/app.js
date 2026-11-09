// Shared helpers. The current exam lives in sessionStorage only: it survives
// page loads but is gone when the tab closes. Nothing is stored long-term.
(function () {
  var KEY = "dtt_session_v1";

  var store = {
    get: function () { try { return JSON.parse(sessionStorage.getItem(KEY)); } catch (e) { return null; } },
    set: function (s) { try { sessionStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {} },
    clear: function () { try { sessionStorage.removeItem(KEY); } catch (e) {} }
  };

  var byId = {};
  (window.QUESTION_BANK || []).forEach(function (q) { byId[q.id] = q; });

  function shuffle(a) {
    a = a.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function pool(test, topic) {
    return window.QUESTION_BANK.filter(function (q) {
      return q.tests.indexOf(test) > -1 && (!topic || q.topic === topic);
    });
  }

  function startExam(test) {
    var t = window.TESTS[test];
    var ids = shuffle(pool(test)).slice(0, t.examSize).map(function (q) { return q.id; });
    store.set({ test: test, mode: "exam", ids: ids, answers: {}, flags: {}, start: Date.now(), minutes: t.minutes });
    location.href = "question.html?n=1";
  }

  function startPractice(test, topic) {
    var ids = shuffle(pool(test, topic)).map(function (q) { return q.id; });
    if (!ids.length) return;
    store.set({ test: test, mode: "practice", topic: topic || null, ids: ids, answers: {}, flags: {}, start: Date.now() });
    location.href = "question.html?n=1";
  }

  function score(s) {
    var correct = 0, topics = {};
    s.ids.forEach(function (id) {
      var q = byId[id]; if (!q) return;
      var ok = s.answers[id] === q.a;
      if (ok) correct++;
      var t = topics[q.topic] || (topics[q.topic] = { total: 0, correct: 0 });
      t.total++; if (ok) t.correct++;
    });
    return { correct: correct, total: s.ids.length, answered: Object.keys(s.answers).length, topics: topics };
  }

  function esc(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function siteUrl() {
    var u = window.SITE.url;
    // Fallback: the folder this page is in, so it works at / or under a subfolder like /driving/
    return (!u || u.indexOf("example") > -1) ? location.origin + location.pathname.replace(/[^\/]*$/, "") : u;
  }

  function shareLinks(text) {
    var url = siteUrl();
    return {
      whatsapp: "https://wa.me/?text=" + encodeURIComponent(text + " " + url),
      facebook: "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(url)
    };
  }

  // ---- Ads ----
  // One responsive ad unit per page. Space is reserved in CSS so the layout
  // doesn't jump when the ad loads, and it sits away from the answer buttons
  // to avoid accidental clicks (an AdSense policy requirement).
  var client = window.SITE.adsenseClient;
  if (client) {
    var s = document.createElement("script");
    s.async = true; s.crossOrigin = "anonymous";
    s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(client);
    document.head.appendChild(s);
  }

  function renderAd(elId, slotKey) {
    var el = document.getElementById(elId);
    if (!el) return;
    var slot = window.SITE.adSlots[slotKey];
    if (!client || !slot) {
      el.innerHTML = '<span class="ad-label">Advertisement</span><div class="ad-ph">Ad space</div>';
      return;
    }
    el.innerHTML = '<span class="ad-label">Advertisement</span><ins class="adsbygoogle" style="display:block" data-ad-client="' +
      esc(client) + '" data-ad-slot="' + esc(slot) + '" data-ad-format="auto" data-full-width-responsive="true"></ins>';
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
  }

  // In-page confirm dialog. Native confirm()/alert() are blocked or auto-dismissed
  // in some in-app browsers (Facebook, Instagram, embedded webviews), so we never use them.
  function ask(message, okLabel, cancelLabel) {
    return new Promise(function (resolve) {
      var d = document.createElement("div");
      d.className = "modal";
      d.setAttribute("role", "dialog");
      d.setAttribute("aria-modal", "true");
      d.innerHTML = '<div class="modal-box"><p>' + esc(message) + '</p><div class="btn-row">' +
        '<button class="btn" data-r="0">' + esc(cancelLabel || "Cancel") + '</button>' +
        '<button class="btn primary" data-r="1">' + esc(okLabel || "OK") + '</button></div></div>';
      function close(r) { d.remove(); document.removeEventListener("keydown", onKey); resolve(r); }
      function onKey(e) { if (e.key === "Escape") close(false); }
      d.addEventListener("click", function (e) {
        var b = e.target.closest("[data-r]");
        if (b) close(b.getAttribute("data-r") === "1");
        else if (e.target === d) close(false);
      });
      document.addEventListener("keydown", onKey);
      document.body.appendChild(d);
      d.querySelector(".primary").focus();
    });
  }

  window.DTT = {
    store: store, byId: byId, shuffle: shuffle, pool: pool, startExam: startExam,
    startPractice: startPractice, score: score, esc: esc, shareLinks: shareLinks, renderAd: renderAd, ask: ask
  };
})();
