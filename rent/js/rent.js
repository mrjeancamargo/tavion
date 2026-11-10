// Rent increase calculator UI. Rules live in rules.js (window.IERENT).
(function () {
  "use strict";
  var R = window.IERENT, KEY = "tavion_rent_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("rentForm"), out = $("result");
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function eur(n) { return "€" + n.toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function nice(iso) { var p = iso.split("-"); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])).toLocaleDateString("en-IE", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }); }
  function radio(n) { var r = form.querySelector('input[name="' + n + '"]:checked'); return r ? r.value : null; }
  function setRadio(n, v) { var r = form.querySelector('input[name="' + n + '"][value="' + v + '"]'); if (r) r.checked = true; }
  var FIELDS = ["county", "rent", "lastSet", "tenancyStart", "ptype", "noticeDate", "effective", "cpiMode", "cpi", "proposed"];

  function syncArea() {
    var c = R.COUNTIES[$("county").value];
    var part = c && !c.whole && c.lea.length;
    $("leaBox").hidden = !part;
    if (part) $("leaList").textContent = c.lea.join(", ");
    $("cpiBox").hidden = $("cpiMode").value !== "known";
  }
  function save() { var s = { inLea: radio("inLea") }; FIELDS.forEach(function (k) { s[k] = $(k).value; }); try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {} }
  function restore() {
    var s = null; try { s = JSON.parse(localStorage.getItem(KEY)); } catch (e) {}
    if (s) { FIELDS.forEach(function (k) { if (s[k] != null) $(k).value = s[k]; }); if (s.inLea) setRadio("inLea", s.inLea);
      if (s.tenancyStart || s.proposed || (s.ptype && s.ptype !== "standard") || s.effective || s.cpiMode === "known") $("adv").open = true; }
    var q = new URLSearchParams(location.search);
    if (q.get("county") && R.COUNTIES[q.get("county")]) $("county").value = q.get("county");
    if (q.get("lea")) setRadio("inLea", q.get("lea"));
  }

  function render() {
    syncArea(); save();
    var county = $("county").value, rent = num($("rent").value), last = $("lastSet").value;
    if (!county || !rent || !last) { out.innerHTML = ""; return null; }
    var lea = radio("inLea");
    var r = R.rentReview({ rent: rent, lastSet: last, tenancyStart: $("tenancyStart").value || null, county: county,
      inLea: lea === "yes" ? true : lea === "no" ? false : null, type: $("ptype").value, noticeDate: $("noticeDate").value || null,
      effective: $("effective").value || null, cpi: $("cpiMode").value === "known" && $("cpi").value !== "" ? num($("cpi").value) : null,
      proposed: num($("proposed").value) || null });
    var h = "";
    if (r.excluded) { out.innerHTML = '<div class="verdict-box warn"><h2>Rent control doesn\'t apply</h2><p>' + r.notes[0] + '</p></div>'; return r; }
    if (!r.ok) { out.innerHTML = '<div class="verdict-box warn"><p>' + r.warnings.join("<br>") + '</p></div>'; return r; }

    if (r.proposed) {
      h += '<div class="verdict-box ' + (r.proposedOk ? "good" : "bad") + '"><h2>' + (r.proposedOk ? "✅ This increase looks within the rules" : "❌ This increase looks too high or too early") + '</h2><p>' +
        eur(r.proposed) + ' is a ' + r.proposedPct + '% increase. ' + (r.overBy > 0 ? 'It is <strong>' + eur(r.overBy) + ' a month above</strong> the maximum of ' + eur(r.maxRent) + '. ' : '') +
        (r.warnings.length ? r.warnings.join(" ") : "") + '</p></div>';
    }
    h += '<div class="net-hero"><div class="tl">Maximum new rent</div><div class="amt">' + eur(r.maxRent) + '</div><p>a month · up to +' + eur(r.maxIncrease) + ' (' + r.maxPct + '%) · earliest from ' + nice(r.earliest) + '</p></div>';
    h += '<div class="card"><dl class="dl">' +
      '<dt>Current rent</dt><dd>' + eur(rent) + '</dd>' +
      '<dt>Rent last set</dt><dd>' + nice(last) + '</dd>' +
      '<dt>New rent would start</dt><dd>' + nice(r.effective) + '</dd>' +
      '<dt>Time since rent was set</dt><dd>' + r.years + ' years</dd>' +
      '<dt>Cap used</dt><dd>' + (r.basis === "2pct" ? "2% a year, pro rata" : r.basis === "cpi" ? "CPI change" : "CPI (estimate)") + '</dd>' +
      '<dt>Maximum increase</dt><dd>' + eur(r.maxIncrease) + ' a month</dd>' +
      '<dt>Extra per year</dt><dd>' + eur(r.maxIncrease * 12) + '</dd>' +
      '<dt>Earliest date (review gap)</dt><dd>' + nice(r.earliestByGap) + '</dd>' +
      '<dt>Earliest date (90 days\' notice)</dt><dd>' + nice(r.earliestByNotice) + '</dd></dl></div>';
    var issues = [];
    if (r.rule24) issues.push(["warn", "Your area became a Rent Pressure Zone on 20 June 2025, so the first review must wait <strong>24 months</strong> from " + nice(last) + " (not 12)."]);
    r.warnings.forEach(function (w) { if (!r.proposed) issues.push(["bad", w]); });
    r.notes.forEach(function (n) { issues.push(["", n]); });
    if (r.newRules === false && $("tenancyStart").value === "") issues.push(["", "Tip: add the tenancy start date in Advanced options – tenancies from 1 March 2026 have different reset rules."]);
    h += '<ul class="issues">' + issues.map(function (i) { return '<li class="' + i[0] + '">' + i[1] + '</li>'; }).join("") + '</ul>';
    h += '<h3>For the increase to be valid, the notice must:</h3><ul class="todo">' +
      ['Be in writing and give at least <strong>90 days\' notice</strong> before the new rent starts',
       'Be sent to the tenant <strong>and the RTB on the same day</strong> (RTB Notice of Rent Review template)',
       'Include the last rent and the date it was set, a printout from the <a href="https://rtb.ie/" target="_blank" rel="noopener">RTB Rent Calculator</a> and 3 comparable rents from the RTB Rent Register',
       'Tell the tenant they can refer a dispute to the RTB – before the new rent starts or within 28 days of getting the notice, whichever is later'].map(function (t) { return "<li>" + t + "</li>"; }).join("") + '</ul>';
    h += '<p class="muted small">Estimate based on the RTB rules. Confirm the exact figure with the official RTB Rent Calculator, which uses the CSO\'s monthly CPI.</p>';
    h += '<div class="res-actions"><a class="btn" href="notice-period.html">Check a notice to leave →</a><a class="btn wa" target="_blank" rel="noopener" data-track="share" data-method="whatsapp" data-label="rent_result" href="https://wa.me/?text=' +
      encodeURIComponent("Check if a rent increase is legal in Ireland – free calculator with the 2026 rules: " + location.origin + location.pathname) + '">Share on WhatsApp</a></div>';
    out.innerHTML = h;
    return r;
  }

  var tracked = "";
  function go(scroll) {
    var r = render(); if (!r) return;
    var key = $("county").value + "|" + Math.round(num($("rent").value) / 100);
    if (scroll || key !== tracked) {
      tracked = key;
      if (window.TAVION && TAVION.track) TAVION.track("rent_calc", { label: $("county").value, mode: $("ptype").value, result: r.proposed ? (r.proposedOk ? "ok" : "too_high") : "max", advanced: $("adv").open ? "yes" : "no" });
    }
    if (scroll) out.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  restore(); syncArea();
  var t = null;
  form.addEventListener("input", function (e) {
    if (e.target.id === "rent" || e.target.id === "proposed") {
      var el = e.target, raw = el.value.replace(/[^\d.]/g, ""), p = raw.split(".");
      if (p[0]) { var f = Number(p[0]).toLocaleString("en-IE") + (p.length > 1 ? "." + p[1].slice(0, 2) : ""); if (f !== el.value) el.value = f; }
    }
    clearTimeout(t); t = setTimeout(function () { render(); }, 300);
  });
  form.addEventListener("change", function () { render(); });
  form.addEventListener("submit", function (e) { e.preventDefault(); go(true); });
  $("resetAdv").addEventListener("click", function () {
    ["tenancyStart", "noticeDate", "effective", "cpi", "proposed"].forEach(function (k) { $(k).value = ""; });
    $("ptype").value = "standard"; $("cpiMode").value = "above"; render();
  });
  render();
})();
