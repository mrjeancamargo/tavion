// Auto-enrolment (MyFutureFund) calculator UI. Rules live in ae.js (window.IEAE); net pay uses salary/js/tax.js.
(function () {
  "use strict";
  var A = window.IEAE, KEY = "tavion_ae_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("aeForm"), out = $("result");
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function eur(n, dp) { dp = dp || 0; return "€" + n.toLocaleString("en-IE", { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function pct(x) { return (x * 100).toString() + "%"; }
  var F = ["salary", "age", "enrol", "growth", "payRise", "charge"];
  try { var s = JSON.parse(localStorage.getItem(KEY)); if (s) { F.forEach(function (k) { if (s[k]) $(k).value = s[k]; }); $("payroll").checked = !!s.payroll; if (s.growth || s.payRise || s.charge || s.payroll) $("adv").open = true; } } catch (e) {}
  var q = new URLSearchParams(location.search);
  if (q.get("salary")) $("salary").value = Number(num(q.get("salary"))).toLocaleString("en-IE");
  if (q.get("age")) $("age").value = num(q.get("age"));

  function render() {
    var st = { payroll: $("payroll").checked }; F.forEach(function (k) { st[k] = $(k).value; }); try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
    var sal = num($("salary").value), age = num($("age").value);
    if (!sal || !age) { out.innerHTML = ""; return null; }
    var yr = new Date().getFullYear();
    var el = A.eligibility({ age: age, salary: sal, payrollPension: $("payroll").checked });
    var im = A.payImpact(sal, yr), c = im.contributions;
    var pr = A.project({ salary: sal, age: age, startYear: yr, growth: $("growth").value === "" ? null : num($("growth").value),
      payRise: $("payRise").value === "" ? null : num($("payRise").value), charge: $("charge").value === "" ? null : num($("charge").value) });
    var cls = el.status === "auto" ? "good" : el.status === "optin" ? "warn" : "bad";
    var h = '<div class="verdict-box ' + cls + '"><h2>' + (el.status === "auto" ? "✅ You're auto-enrolled" : el.status === "optin" ? "ℹ️ Not auto-enrolled – you can opt in" : el.status === "exempt" ? "ℹ️ Not auto-enrolled" : "❌ Not eligible") + '</h2><p>' + el.text + '</p></div>';
    h += '<div class="net-hero"><div class="tl">You pay in ' + yr + ' (' + pct(c.rates.employee) + ')</div><div class="amt">' + eur(c.employee / 12, 2) + '</div><p>a month · your employer and the State add <strong>' + eur((c.employer + c.state) / 12, 2) + '</strong> a month</p></div>';
    h += '<div class="periods" style="grid-template-columns:repeat(3,1fr)"><div><b>' + eur(c.employee) + '</b><span>you / year</span></div><div><b>' + eur(c.employer) + '</b><span>employer / year</span></div><div><b>' + eur(c.state) + '</b><span>State / year</span></div></div>';
    if (c.capped) h += '<p class="muted small">Contributions are on pay up to €80,000.</p>';
    if (im.netBefore) h += '<div class="card"><div class="tl">Your take-home pay</div><p class="small" style="margin:6px 0 0">' + eur(im.netBefore) + ' → <strong>' + eur(im.netAfter) + '</strong> a year (' + eur(im.perWeek, 2) +
      ' a week less). There\'s no tax relief – contributions come from pay after tax. <a href="../salary/?gross=' + sal + '">See your full payslip breakdown →</a></p></div>';
    h += '<h2>What you could have at 66</h2><div class="hero-num"><div><span class="tl">Projected pot</span><strong>' + eur(pr.pot) + '</strong><span class="muted">' + eur(pr.potToday) + ' in today\'s money</span></div><div><span class="tl">Tax-free lump sum</span><strong>' + eur(pr.lumpSum) + '</strong><span class="muted">up to 25%</span></div></div>';
    var tot = pr.employee + pr.employer + pr.state + Math.max(0, pr.growth);
    h += '<div class="card"><div class="tl">Where it comes from (' + pr.years + ' years)</div><div class="stack"><span class="c-net" style="width:' + (pr.employee / tot * 100).toFixed(1) + '%"></span><span class="c-tax" style="width:' + (pr.employer / tot * 100).toFixed(1) + '%"></span><span class="c-usc" style="width:' + (pr.state / tot * 100).toFixed(1) + '%"></span><span class="c-pen" style="width:' + (Math.max(0, pr.growth) / tot * 100).toFixed(1) + '%"></span></div>' +
      '<ul class="legend"><li><i class="c-net"></i>You ' + eur(pr.employee) + '</li><li><i class="c-tax"></i>Employer ' + eur(pr.employer) + '</li><li><i class="c-usc"></i>State ' + eur(pr.state) + '</li><li><i class="c-pen"></i>Growth ' + eur(Math.max(0, pr.growth)) + '</li></ul></div>';
    var stages = A.stageYears().map(function (sg) { var cc = A.contributions(sal, sg.from); return '<tr><th scope="row">' + sg.from + (sg.to ? '–' + sg.to : '+') + '</th><td>' + eur(cc.employee / 12, 2) + '</td><td>' + eur(cc.total) + '</td></tr>'; }).join("");
    h += '<h2>Your contributions by year</h2><div class="table-wrap"><table class="sumtab"><thead><tr><th>Years</th><th>You / month</th><th>Total in / year</th></tr></thead><tbody>' + stages + '</tbody></table></div>';
    var en = $("enrol").value || "2026-01";
    var w = A.windows(en + "-01");
    h += '<div class="card"><div class="tl">Your opt-out windows</div><ul class="notes" style="margin-top:6px">' + w.map(function (x) { return '<li>' + x.reason + ': <strong>' + x.from + ' to ' + x.to + '</strong></li>'; }).join("") +
      '</ul><p class="small" style="margin:6px 0 0">Outside these windows you can pause (after 6 months). <a href="opt-out.html">How opting out works →</a></p></div>';
    var tips = [];
    if (im.higherRate) tips.push(["warn", "You pay 40% tax: a workplace pension with tax relief (worth " + eur(im.reliefEquivalent) + " on your contribution vs a " + eur(im.stateTopUp) + " State top-up) may be better. <a href='vs-workplace-pension.html'>Compare →</a>"]);
    if (sal >= 50000) tips.push(["ok", "On " + eur(sal) + " you could borrow up to " + eur(sal * 4) + " for a first home. <a href='../mortgage/?inc1=" + sal + "' data-track='cross_app' data-label='mortgage_from_ae'>How much could I borrow? →</a>"]);
    tips.push(["", "MyFutureFund is paid on top of your State Pension – €309.30 a week (Contributory) from 2027. <a href='../welfare/state-pension-contributory.html'>State Pension rates →</a>"]);
    h += '<ul class="issues">' + tips.map(function (t) { return '<li class="' + t[0] + '">' + t[1] + '</li>'; }).join("") + '</ul>';
    h += '<p class="muted small">Projection is an illustration (growth ' + ($("growth").value || 4) + '%, charges ' + ($("charge").value || 0.5) + '%, pay rises ' + ($("payRise").value || 2.5) + '%, inflation 2%). Investments can fall as well as rise. Check your real fund in the MyFutureFund portal.</p>';
    out.innerHTML = h;
    return { sal: sal, el: el };
  }
  function band(x) { return x < 30000 ? "<30k" : x < 45000 ? "30-45k" : x < 60000 ? "45-60k" : x < 80000 ? "60-80k" : "80k+"; }
  form.addEventListener("input", function () { render(); });
  form.addEventListener("change", function () { render(); });
  form.addEventListener("submit", function (e) { e.preventDefault(); var r = render(); if (!r) return;
    if (window.TAVION && TAVION.track) TAVION.track("ae_calc", { salary_band: band(r.sal), result: r.el.status, advanced: $("adv").open ? "yes" : "no" });
    out.scrollIntoView({ behavior: "smooth", block: "start" }); });
  var se = $("salary"); se.addEventListener("input", function () { var raw = se.value.replace(/[^\d]/g, ""); if (raw) se.value = Number(raw).toLocaleString("en-IE"); });
  $("resetAdv").addEventListener("click", function () { ["growth", "payRise", "charge"].forEach(function (k) { $(k).value = ""; }); $("payroll").checked = false; $("enrol").value = "2026-01"; render(); });
  render();
})();
