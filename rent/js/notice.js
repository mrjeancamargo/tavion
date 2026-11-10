// Notice of termination calculator UI. Rules live in rules.js (window.IERENT).
(function () {
  "use strict";
  var R = window.IERENT, KEY = "tavion_notice_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("noticeForm"), out = $("result");
  function nice(iso) { var p = iso.split("-"); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])).toLocaleDateString("en-IE", { weekday: "short", day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }); }
  function who() { return form.querySelector('input[name="who"]:checked').value; }
  var F = ["start", "served", "reasonLandlord", "reasonTenant", "size", "endDate"], C = ["hardship", "familyClose", "copied", "ssa"];
  var REGIME = { "new": "created on or after 1 March 2026 (new rules)", "2022": "created between 11 June 2022 and 28 February 2026", "2016": "created between 24 December 2016 and 10 June 2022", "old": "created before 24 December 2016" };

  function sync() {
    var l = who() === "landlord";
    $("reasonL").hidden = !l; $("reasonT").hidden = l; $("llOnly").hidden = !l;
    var r = $("reasonLandlord").value;
    $("hardship").closest("label").hidden = r !== "sale";
    $("familyClose").closest("label").hidden = r !== "family";
  }
  function save() { var s = { who: who() }; F.forEach(function (k) { s[k] = $(k).value; }); C.forEach(function (k) { s[k] = $(k).checked; }); try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {} }
  function restore() {
    var s = null; try { s = JSON.parse(localStorage.getItem(KEY)); } catch (e) {}
    if (s) { F.forEach(function (k) { if (s[k] != null) $(k).value = s[k]; }); C.forEach(function (k) { if (s[k] != null) $(k).checked = s[k]; });
      var w = form.querySelector('input[name="who"][value="' + s.who + '"]'); if (w) w.checked = true; }
    if (!$("served").value) $("served").value = R.iso(R.today());
    var q = new URLSearchParams(location.search);
    if (q.get("who")) { var x = form.querySelector('input[name="who"][value="' + q.get("who") + '"]'); if (x) x.checked = true; }
    if (q.get("reason") && $("reasonLandlord").querySelector('option[value="' + q.get("reason") + '"]')) $("reasonLandlord").value = q.get("reason");
  }

  function render() {
    sync(); save();
    if (!$("start").value) { out.innerHTML = ""; return null; }
    var w = who();
    var o = R.notice({ who: w, start: $("start").value, served: $("served").value || null, reason: w === "landlord" ? $("reasonLandlord").value : $("reasonTenant").value,
      landlordSize: $("size").value, hardship: $("hardship").checked, familyClose: $("familyClose").checked, endDate: $("endDate").value || null,
      copiedRtb: w === "landlord" ? $("copied").checked : null, ssa: $("ssa").checked });
    if (o.warnings.length && o.days === undefined) { out.innerHTML = '<div class="verdict-box warn"><p>' + o.warnings.join("<br>") + '</p></div>'; return o; }
    var bad = !o.allowed || o.endDateOk === false || (w === "landlord" && !$("copied").checked);
    var h = '<div class="verdict-box ' + (bad ? "bad" : "good") + '"><h2>' + (!o.allowed ? "❌ This reason isn't allowed for this tenancy" : bad ? "⚠️ The notice has a problem" : "✅ Notice period: " + o.days + " days") + '</h2><p>' + o.reasonLabel + '.</p></div>';
    if (o.allowed || o.endAt)
      h += '<div class="net-hero"><div class="tl">' + (o.allowed ? "Earliest termination date" : "Earliest date this reason could apply") + '</div><div class="amt" style="font-size:clamp(28px,8vw,40px)">' + nice(o.earliestEnd) + '</div><p>' + (o.allowed ? o.days + ' days\' notice from ' + nice(o.served) : 'end of the tenancy cycle – notice of ' + o.days + ' days or more, served before then') + '</p></div>';
    h += '<div class="card"><dl class="dl">' +
      '<dt>Tenancy</dt><dd>' + REGIME[o.regime] + '</dd>' +
      '<dt>Tenancy length when served</dt><dd>' + (o.monthsAtService >= 12 ? Math.floor(o.monthsAtService / 12) + " yr " + (o.monthsAtService % 12) + " mo" : o.monthsAtService + " months") + '</dd>' +
      '<dt>Notice band</dt><dd>' + o.band + '</dd>' +
      (o.cycleEnd ? '<dt>' + (o.regime === "new" ? "Current 6-year cycle ends" : "Part 4 term end") + '</dt><dd>' + nice(o.cycleEnd) + '</dd>' : '') +
      (o.endDate ? '<dt>Date on the notice</dt><dd>' + nice(o.endDate) + (o.endDateOk ? " ✅" : " ❌") + '</dd>' : '') + '</dl></div>';
    var items = [];
    o.warnings.forEach(function (x) { items.push(["bad", x]); });
    o.why.forEach(function (x) { items.push([o.allowed ? "ok" : "warn", x]); });
    if (o.under6 && w === "landlord") items.push(["", "The tenant doesn't have security of tenure yet (under 6 months). A no-fault ending in the first 6 months still stops the landlord resetting to market rent for the next tenancy."]);
    if (items.length) h += '<ul class="issues">' + items.map(function (i) { return '<li class="' + i[0] + '">' + i[1] + '</li>'; }).join("") + '</ul>';
    h += '<h3>Checklist for a valid notice</h3><ul class="todo">' + o.todo.map(function (t) { return "<li>" + t + "</li>"; }).join("") + '</ul>';
    h += '<p class="muted small">General information, not legal advice. Use the <a href="https://rtb.ie/renting/ending-a-tenancy/notice-of-termination-guides/" target="_blank" rel="noopener">RTB Notice of Termination templates</a>. Tenants can get free advice from Threshold on 1800 454 454.</p>';
    h += '<div class="res-actions"><a class="btn" href="./">Check a rent increase →</a><a class="btn wa" target="_blank" rel="noopener" data-track="share" data-method="whatsapp" data-label="notice_result" href="https://wa.me/?text=' +
      encodeURIComponent("Got a notice to leave? Check if it's valid – free Irish notice period calculator (2026 rules): " + location.origin + location.pathname) + '">Share on WhatsApp</a></div>';
    out.innerHTML = h;
    return o;
  }
  function go() {
    var o = render(); if (!o) return;
    if (window.TAVION && TAVION.track) TAVION.track("notice_calc", { label: who(), method: who() === "landlord" ? $("reasonLandlord").value : $("reasonTenant").value,
      result: o.allowed ? "allowed" : "not_allowed", mode: o.regime, advanced: $("adv").open ? "yes" : "no" });
    out.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  restore(); sync();
  form.addEventListener("change", render);
  form.addEventListener("input", render);
  form.addEventListener("submit", function (e) { e.preventDefault(); go(); });
  $("resetAdv").addEventListener("click", function () { $("size").value = "small"; $("hardship").checked = false; $("familyClose").checked = false; $("copied").checked = true; $("ssa").checked = false; $("endDate").value = ""; render(); });
  render();
})();
