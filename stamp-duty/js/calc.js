// Stamp duty / buying costs and LPT calculators. Rules live in property.js (window.IEPROP).
(function () {
  "use strict";
  var P = window.IEPROP;
  var $ = function (id) { return document.getElementById(id); };
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function eur(n, dp) { dp = dp || 0; return "€" + n.toLocaleString("en-IE", { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function money(el) {
    el.addEventListener("input", function () {
      var raw = el.value.replace(/[^\d.]/g, ""), p = raw.split(".");
      if (p[0]) { var f = Number(p[0]).toLocaleString("en-IE") + (p.length > 1 ? "." + p[1].slice(0, 2) : ""); if (f !== el.value) el.value = f; }
    });
  }
  function track(name, params) { if (window.TAVION && TAVION.track) TAVION.track(name, params); }
  function band(x) { return x < 250000 ? "<250k" : x < 400000 ? "250-400k" : x < 600000 ? "400-600k" : x < 1000000 ? "600k-1m" : "1m+"; }

  // ---------------- stamp duty & buying costs
  var form = $("sdForm");
  if (form) {
    var KEY = "tavion_stamp_v1", out = $("result");
    var F = ["price", "solicitor", "council", "depPct"], C = ["mortgage", "survey", "extras", "bulk"];
    var surveyTouched = false;
    function kind() { return form.querySelector('input[name="kind"]:checked').value; }
    function save() { var s = { kind: kind() }; F.forEach(function (k) { s[k] = $(k).value; }); C.forEach(function (k) { s[k] = $(k).checked; }); try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {} }
    function restore() {
      var s = null; try { s = JSON.parse(localStorage.getItem(KEY)); } catch (e) {}
      if (s) { F.forEach(function (k) { if (s[k]) $(k).value = s[k]; }); C.forEach(function (k) { if (s[k] != null) $(k).checked = s[k]; });
        var r = form.querySelector('input[name="kind"][value="' + s.kind + '"]'); if (r) r.checked = true;
        if (s.council || s.solicitor || s.extras || s.bulk || s.depPct) $("adv").open = true; }
      var q = new URLSearchParams(location.search);
      if (q.get("price")) $("price").value = Number(num(q.get("price"))).toLocaleString("en-IE");
      if (q.get("new") === "1") form.querySelector('input[name="kind"][value="new"]').checked = true;
    }
    function render() {
      save();
      var price = num($("price").value); if (!price) { out.innerHTML = ""; return null; }
      var nb = kind() === "new";
      var c = P.buyingCosts(price, { newBuild: nb, mortgage: $("mortgage").checked, survey: $("survey").checked, extras: $("extras").checked, bulk: $("bulk").checked,
        solicitor: $("solicitor").value === "" ? null : num($("solicitor").value), council: $("council").value || null, year: 2027 });
      var dep = price * ($("depPct").value === "" ? 10 : num($("depPct").value)) / 100;
      var sd = c.stamp, h = "";
      h += '<div class="net-hero"><div class="tl">Stamp duty</div><div class="amt">' + eur(sd.total) + '</div><p>' + sd.effective + '% of the price' + (nb ? ' · charged on ' + eur(sd.base) + ' (excl. ' + eur(sd.vat) + ' VAT)' : '') + '</p></div>';
      h += '<div class="card"><div class="tl">How it\'s worked out</div><ul class="notes" style="margin-top:6px">' + sd.rows.map(function (r) { return "<li>" + (r.rate * 100) + "% on " + eur(r.on) + " = <strong>" + eur(r.tax) + "</strong></li>"; }).join("") + '</ul></div>';
      var t = '<h2>Total cost of buying at ' + eur(price) + '</h2><div class="table-wrap"><table class="sumtab"><tbody>';
      c.items.forEach(function (x) { t += '<tr' + (x.group === "stamp" ? "" : ' class="sub"') + '><th scope="row">' + x.name + '</th><td>' + eur(x.amount) + '</td></tr>'; });
      t += '<tr class="total"><th scope="row">Buying costs</th><td>' + eur(c.total) + '</td></tr>';
      t += '<tr><th scope="row">Deposit (' + Math.round(dep / price * 100) + '%)</th><td>' + eur(dep) + '</td></tr>';
      t += '<tr class="total"><th scope="row">Cash you need</th><td>' + eur(dep + c.total) + '</td></tr></tbody></table></div>';
      h += t;
      h += '<div class="periods" style="grid-template-columns:repeat(3,1fr)"><div><b>' + c.pctOfPrice + '%</b><span>costs as % of price</span></div><div><b>' + eur(price - dep) + '</b><span>mortgage needed</span></div><div><b>' +
        eur((price - dep) / 4) + '</b><span>income needed (4×)</span></div></div>';
      if (c.lpt) h += '<div class="card"><div class="tl">Local Property Tax 2027</div><p class="small" style="margin:6px 0 0">' + (c.lpt.band ? 'Band ' + c.lpt.band : 'Over €2.1m') + ' · ' + c.lpt.council + ' (' + (c.lpt.laf >= 0 ? '+' : '') + c.lpt.laf +
        '%): <strong>' + eur(c.lpt.annual) + ' a year</strong> (' + eur(c.lpt.monthly, 2) + ' a month). Your band is based on the value on 1 November 2025 – if you buy after 1 November, the seller pays next year\'s LPT. <a href="lpt.html">LPT calculator →</a></p></div>';
      var tips = [];
      if (price > 1500000) tips.push(["warn", "The part of the price above €1.5m is taxed at 6%."]);
      else if (price > 1000000) tips.push(["", "The part of the price above €1m is taxed at 2%."]);
      if (!nb && !$("survey").checked) tips.push(["warn", "Skipping the survey on a second-hand home is risky – it's cheap compared with a surprise roof or damp repair."]);
      if (nb) tips.push(["ok", "New home? First-time buyers may get <strong>up to €35,000 from Help to Buy</strong> towards the deposit. <a href='../mortgage/schemes.html'>How it works →</a>"]);
      tips.push(["", "Stamp duty and fees come from your savings – lenders don't add them to the mortgage."]);
      h += '<ul class="issues">' + tips.map(function (i) { return '<li class="' + i[0] + '">' + i[1] + '</li>'; }).join("") + '</ul>';
      h += '<div class="cta"><h2>Can you borrow ' + eur(price - dep) + '?</h2><p>See your maximum mortgage, repayments and Help to Buy.</p><a class="btn" href="../mortgage/?price=' + price + '" data-track="cross_app" data-label="mortgage_from_stamp">How much could I borrow?</a></div>';
      h += '<p class="muted small">Fees are typical estimates – get quotes. Stamp duty rates from Revenue. Not tax advice.</p>';
      out.innerHTML = h;
      return c;
    }
    var tracked = "";
    function go(scroll) {
      var c = render(); if (!c) return;
      var key = band(c.price) + kind();
      if (scroll || key !== tracked) { tracked = key; track("stamp_calc", { label: band(c.price), mode: kind(), advanced: $("adv").open ? "yes" : "no" }); }
      if (scroll) out.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    restore(); money($("price")); money($("solicitor"));
    var t = null;
    form.addEventListener("input", function () { clearTimeout(t); t = setTimeout(function () { go(false); }, 300); });
    form.addEventListener("change", function (e) {
      if (e.target.name === "kind" && !surveyTouched) $("survey").checked = kind() !== "new";
      if (e.target.id === "survey") surveyTouched = true;
      go(false);
    });
    form.addEventListener("submit", function (e) { e.preventDefault(); go(true); });
    $("resetAdv").addEventListener("click", function () { $("mortgage").checked = true; $("survey").checked = kind() !== "new"; $("extras").checked = false; $("bulk").checked = false;
      $("solicitor").value = ""; $("council").value = ""; $("depPct").value = ""; render(); });
    render();
  }

  // ---------------- LPT
  var lf = $("lptForm");
  if (lf) {
    var LKEY = "tavion_lpt_v1", lo = $("lptOut");
    try { var s = JSON.parse(localStorage.getItem(LKEY)); if (s) { $("lptVal").value = s.v || ""; if (s.c) $("lptCouncil").value = s.c; } } catch (e) {}
    function lrender(scroll) {
      var v = num($("lptVal").value), c = $("lptCouncil").value, y = +lf.querySelector('input[name="lptYear"]:checked').value;
      try { localStorage.setItem(LKEY, JSON.stringify({ v: $("lptVal").value, c: c })); } catch (e) {}
      if (!v) { lo.innerHTML = ""; return; }
      var r = P.lpt(v, c, y), other = P.lpt(v, c, y === 2026 ? 2027 : 2026);
      var h = '<div class="net-hero"><div class="tl">Local Property Tax ' + y + '</div><div class="amt">' + eur(r.annual) + '</div><p>a year · ' + eur(r.monthly, 2) + ' a month</p></div>';
      h += '<div class="card"><dl class="dl"><dt>Band</dt><dd>' + (r.band ? r.band + ' (' + eur(r.lower) + ' – ' + eur(r.upper) + ')' : 'Over €2.1m') + '</dd><dt>Basic charge</dt><dd>' + eur(r.basic) + '</dd><dt>' + r.council + ' adjustment</dt><dd>' +
        (r.laf >= 0 ? '+' : '') + r.laf + '%</dd><dt>' + other.year + '</dt><dd>' + eur(other.annual) + '</dd></dl></div>';
      h += '<p class="muted small">Band set by the value on 1 November 2025, fixed until 2030. Confirm with <a href="https://lpt.revenue.ie/lpt-web/reckoner/lpt.html" target="_blank" rel="noopener">Revenue\'s LPT calculator</a>. ' +
        (r.band ? '<a href="lpt-band-' + r.band + '.html">Band ' + r.band + ' in every council →</a>' : '') + '</p>';
      lo.innerHTML = h;
      if (scroll) { lo.scrollIntoView({ behavior: "smooth", block: "start" }); track("lpt_calc", { label: c, mode: String(y), result: r.band ? "band_" + r.band : "over_2_1m" }); }
    }
    money($("lptVal"));
    lf.addEventListener("input", function () { lrender(false); });
    lf.addEventListener("change", function () { lrender(false); });
    lf.addEventListener("submit", function (e) { e.preventDefault(); lrender(true); });
    lrender(false);
  }
})();
