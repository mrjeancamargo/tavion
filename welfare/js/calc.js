// Social welfare calculator and Christmas Bonus checker. Rates live in welfare.js (window.IEWELF).
(function () {
  "use strict";
  var W = window.IEWELF, P = W.PAYMENTS;
  var $ = function (id) { return document.getElementById(id); };
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function eur(n, dp) { dp = dp == null ? 2 : dp; return "€" + n.toLocaleString("en-IE", { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function track(n, p) { if (window.TAVION && TAVION.track) TAVION.track(n, p); }

  var form = $("wForm");
  if (form) {
    var KEY = "tavion_welfare_v1", out = $("result");
    var F = ["pay", "k1", "k2", "age"], C = ["adult", "adult66", "u25", "alone", "fuel"];
    function year() { return +form.querySelector('input[name="year"]:checked').value; }
    try { var s = JSON.parse(localStorage.getItem(KEY)); if (s) { F.forEach(function (k) { if (s[k]) $(k).value = s[k]; }); C.forEach(function (k) { $(k).checked = !!s[k]; }); if (C.some(function (k) { return s[k]; }) || s.age) $("adv").open = true; } } catch (e) {}
    var q = new URLSearchParams(location.search);
    if (q.get("p") && P[q.get("p")] && $("pay").querySelector('option[value="' + q.get("p") + '"]')) $("pay").value = q.get("p");
    function render() {
      var st = {}; F.forEach(function (k) { st[k] = $(k).value; }); C.forEach(function (k) { st[k] = $(k).checked; }); try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
      var key = $("pay").value, y = year();
      var r = W.weekly(key, { year: y, age: num($("age").value), under25: $("u25").checked, adult: $("adult").checked, adultAge66: $("adult66").checked,
        kidsUnder12: num($("k1").value), kids12: num($("k2").value), livingAlone: $("alone").checked, fuel: $("fuel").checked });
      var h = "";
      if (r.missing) h += '<div class="callout warn">The ' + y + ' rate for ' + r.name + ' isn\'t confirmed in the Department\'s Budget 2027 tables – showing what we have. Try 2027.</div>';
      h += '<div class="net-hero"><div class="tl">' + r.name + ' · ' + y + '</div><div class="amt">' + eur(r.weekly) + '</div><p>a week · ' + eur(r.monthly, 0) + ' a month · ' + eur(r.yearly, 0) + ' a year</p></div>';
      h += '<div class="table-wrap"><table class="sumtab"><tbody>' + r.rows.map(function (x) { return '<tr><th scope="row">' + x.name + '</th><td>' + eur(x.amount) + '</td></tr>'; }).join("") +
        '<tr class="total"><th scope="row">Total per week</th><td>' + eur(r.weekly) + '</td></tr></tbody></table></div>';
      if (y === 2026 && ($("adult").checked)) h += '<p class="muted small">Qualified adult rates are shown for 2027 only.</p>';
      if (r.fuel) h += '<div class="card"><div class="tl">Fuel Allowance</div><p class="small" style="margin:6px 0 0">' + eur(r.fuel.weekly) + ' a week during the season – about ' + eur(r.fuel.season, 0) + ' over 28 weeks. <a href="fuel-allowance.html">More →</a></p></div>';
      var x = r.xmas;
      if (x.eligible) h += '<div class="better"><div class="em">🎄</div><p>Christmas Bonus 2026: <strong class="n">' + eur(W.xmasBonus(key, W.weekly(key, { year: 2026, age: num($("age").value), under25: $("u25").checked, kidsUnder12: num($("k1").value), kids12: num($("k2").value), livingAlone: $("alone").checked }).weekly).amount) +
        '</strong> in the week starting 7 December' + (x.condition ? ', ' + x.condition : '') + '. <a href="christmas-bonus.html">Details →</a></p></div>';
      else h += '<div class="better worse"><div class="em">ℹ️</div><p>' + r.name + ' doesn\'t get the Christmas Bonus. <a href="christmas-bonus.html">Who does →</a></p></div>';
      if (y === 2027 && P[key].r26 != null) { var o = W.weekly(key, { year: 2026, kidsUnder12: num($("k1").value), kids12: num($("k2").value), livingAlone: $("alone").checked, age: num($("age").value) });
        if (!o.missing && !$("adult").checked) h += '<p>That\'s <strong>' + eur(r.weekly - o.weekly) + ' a week more</strong> than in 2026 (' + eur((r.weekly - o.weekly) * 52, 0) + ' a year).</p>'; }
      h += '<ul class="issues"><li><a href="' + key + '.html">Who qualifies for ' + r.name + ', how long it lasts and how to apply →</a></li>' +
        (num($("k1").value) + num($("k2").value) > 0 ? '<li class="ok">You may also get <a href="child-benefit.html">Child Benefit</a> (€140 a month per child) and the <a href="back-to-school-allowance.html">Back to School Allowance</a>.</li>' : '') +
        '<li>Thinking about work? <a href="jobseekers-vs-working.html">Compare welfare with take-home pay →</a></li></ul>';
      h += '<p class="muted small">Maximum rates – you may get less depending on your PRSI record or means. Confirm with the Department of Social Protection or on MyWelfare.ie.</p>';
      out.innerHTML = h;
      return r;
    }
    form.addEventListener("input", render); form.addEventListener("change", render);
    form.addEventListener("submit", function (e) { e.preventDefault(); var r = render(); track("welfare_calc", { label: r.key, mode: String(r.year), advanced: $("adv").open ? "yes" : "no" }); out.scrollIntoView({ behavior: "smooth", block: "start" }); });
    $("resetAdv").addEventListener("click", function () { C.forEach(function (k) { $(k).checked = false; }); $("age").value = ""; render(); });
    render();
  }

  var xf = $("xForm");
  if (xf) {
    function xr(scroll) {
      var key = $("xPay").value, amt = num($("xAmt").value) || W.weekly(key, { year: 2026 }).weekly;
      var b = W.xmasBonus(key, amt), h;
      if (!b.eligible) h = '<div class="verdict-box warn"><p>' + P[key].name + ' doesn\'t qualify for the Christmas Bonus.</p></div>';
      else h = '<div class="net-hero"><div class="tl">Your Christmas Bonus 2026</div><div class="amt">' + eur(b.amount) + '</div><p>paid in the week starting Monday 7 December 2026, on your usual payment day' + (b.condition ? ' – ' + b.condition : '') + '</p></div>';
      $("xOut").innerHTML = h;
      if (scroll) { $("xOut").scrollIntoView({ behavior: "smooth", block: "start" }); track("xmas_bonus_calc", { label: key }); }
    }
    xf.addEventListener("input", function () { xr(false); }); xf.addEventListener("change", function () { xr(false); });
    xf.addEventListener("submit", function (e) { e.preventDefault(); xr(true); });
    var amtEl = $("xAmt"); amtEl.addEventListener("input", function () { var raw = amtEl.value.replace(/[^\d.]/g, ""); if (raw && raw.indexOf(".") < 0) amtEl.value = Number(raw).toLocaleString("en-IE"); });
    xr(false);
  }
})();
