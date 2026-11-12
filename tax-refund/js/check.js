// Tax refund checker UI. Rules live in refund.js (window.IEREF); job amounts in jobs.js (window.IEJOBS).
(function () {
  "use strict";
  var R = window.IEREF, KEY = "tavion_refund_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("refForm"), out = $("result");
  var NUM = ["rentMonthly", "studentRentMonthly", "mortgageIncrease", "medical", "prescriptions", "dental", "therapy", "glutenFree", "nursingHome", "wfhDays", "wfhBills", "tuitionFees", "carerIncome"];
  var BOX = ["higherRate", "hap", "mortgage", "landlord", "emergencyTax", "unemployed", "taxableWelfare", "tuitionPT", "homeCarer", "singleParent", "incapChild", "dependent", "over65", "blind", "guideDog"];
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function eur(n) { return "€" + Math.round(n).toLocaleString("en-IE"); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  var sel = $("job");
  (window.IEJOBS || []).forEach(function (j, i) { var o = document.createElement("option"); o.value = i; o.textContent = j[0] + " – €" + j[1]; sel.appendChild(o); });

  try { var s = JSON.parse(localStorage.getItem(KEY)); if (s) { NUM.forEach(function (k) { if (s[k]) $(k).value = s[k]; }); BOX.forEach(function (k) { $(k).checked = !!s[k]; });
    if (s.job) sel.value = s.job; if (s.status) { var r = form.querySelector('input[name=status][value="' + s.status + '"]'); if (r) r.checked = true; } } } catch (e) {}

  function toggles() { $("mortgageRow").hidden = !$("mortgage").checked; $("carerIncomeRow").hidden = !$("homeCarer").checked; }
  function answers() {
    var o = { couple: form.querySelector("input[name=status]:checked").value === "couple" };
    NUM.forEach(function (k) { o[k] = num($(k).value); });
    BOX.forEach(function (k) { o[k] = $(k).checked; });
    if (!o.mortgage) o.mortgageIncrease = 0;
    var j = (window.IEJOBS || [])[sel.value]; o.flatRate = j ? j[1] : 0; o.jobPage = j ? j[2] : "";
    return o;
  }
  function render(scroll) {
    toggles();
    var o = answers(), st = { status: o.couple ? "couple" : "single", job: sel.value };
    NUM.forEach(function (k) { st[k] = $(k).value; }); BOX.forEach(function (k) { st[k] = $(k).checked; });
    try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
    var r = R.check(o);
    if (!r.items.length) { out.innerHTML = scroll ? '<div class="callout">Fill in at least one thing you pay for – rent, health, working from home or your job – to see an estimate.</div>' : ""; return r; }
    var h = '<div class="net-hero"><div class="tl">You could be owed up to</div><div class="amt">' + eur(r.total) + '</div><p>for ' + r.years[0] + '–' + r.years[r.years.length - 1] + (r.items.some(function (i) { return i.unknown; }) ? ", plus the items below we can't estimate" : "") + '</p></div>';
    if (r.deadlineDays > 0) h += '<div class="callout warn">⏰ <strong>' + r.deadlineDays + ' days left</strong> to claim anything for 2022 (deadline 31 December 2026).</div>';
    h += '<div class="table-wrap"><table><thead><tr><th>What you can claim</th><th class="num">Up to</th></tr></thead><tbody>' + r.items.map(function (i) {
      var years = i.byYear.length ? '<br><small class="muted">' + i.byYear.map(function (y) { return y.year + ": " + eur(y.amount); }).join(" · ") + "</small>" : "";
      var page = i.key === "fre" && o.jobPage ? o.jobPage : i.page;
      return '<tr><td><a href="' + page + '" data-track="refund_item" data-label="' + i.key + '">' + esc(i.name) + '</a><br><small>' + esc(i.note) + "</small>" + years + '</td><td class="num">' + (i.unknown ? "Check" : eur(i.total)) + "</td></tr>";
    }).join("") + '<tr class="total"><th>Total estimate</th><td class="num">' + eur(r.total) + "</td></tr></tbody></table></div>";
    h += '<p class="muted small">This assumes the same costs each year you tick – change the figures to match a single year if they differ. These are the most you could get: a credit can\'t give back more Income Tax than you paid that year, and amounts already on your tax credits don\'t count twice.</p>';
    h += '<div class="cta"><h2>Claim it in about 15 minutes</h2><p>myAccount → Review your tax for the previous 4 years → Statement of Liability → Income Tax Return.</p><a class="btn" href="how-to-claim.html">Step-by-step guide</a></div>';
    var tips = [];
    if (o.rentMonthly > 0) tips.push("Is your rent going up? <a href='../rent/' data-track='cross_app' data-label='rent_from_refund'>Check the increase is legal →</a>");
    if (o.taxableWelfare || o.unemployed) tips.push("See the 2027 rates: <a href='../welfare/' data-track='cross_app' data-label='welfare_from_refund'>social welfare rates →</a>");
    tips.push("See your Budget 2027 take-home pay: <a href='../salary/' data-track='cross_app' data-label='salary_from_refund'>pay calculator →</a>");
    h += '<ul class="issues">' + tips.map(function (t) { return "<li>" + t + "</li>"; }).join("") + "</ul>";
    out.innerHTML = h;
    if (scroll) out.scrollIntoView({ behavior: "smooth", block: "start" });
    return r;
  }
  function band(x) { return x < 250 ? "<250" : x < 1000 ? "250-999" : x < 3000 ? "1000-2999" : "3000+"; }
  form.addEventListener("input", function () { render(); });
  form.addEventListener("change", function () { render(); });
  form.addEventListener("submit", function (e) { e.preventDefault(); var r = render(true);
    if (window.TAVION && TAVION.track) TAVION.track("refund_check", { result: band(r.total), total: r.items.length, label: r.items.map(function (i) { return i.key; }).join(",") }); });
  render();
})();
