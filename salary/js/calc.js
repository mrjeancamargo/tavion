// Take-home pay calculator UI. The tax rules live in tax.js (window.IETAX).
(function () {
  "use strict";
  var T = window.IETAX, YEARS = T.YEARS;
  var KEY = "tavion_salary_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("calc"), out = $("result");
  var yearList = Object.keys(YEARS).map(Number).sort();

  // ---------- helpers
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function fmt(n, dp) {
    if (dp == null) dp = Math.abs(n) < 1000 ? 2 : 0;
    return (n < 0 ? "−" : "") + "€" + Math.abs(n).toLocaleString("en-IE", { minimumFractionDigits: dp, maximumFractionDigits: dp });
  }
  function f2(n) { return fmt(n, 2); }
  function radio(name) { var r = form.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : null; }
  function setRadio(name, v) { var r = form.querySelector('input[name="' + name + '"][value="' + v + '"]'); if (r) r.checked = true; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  var ADV = ["partnerGross", "partnerAge", "age", "employment", "pensionPct", "rent", "blind", "incap", "depRel", "hours", "days"];
  var CHK = ["medicalCard", "partnerMedicalCard", "homeCarer"];

  function readInputs() {
    var hours = num($("hours").value) || 39, days = num($("days").value) || 5;
    var period = $("period").value;
    var amount = num($("gross").value);
    return {
      amount: amount, period: period, hours: hours, days: days,
      calc: {
        year: +radio("year"), gross: T.toYear(amount, period, hours, days), status: radio("status"),
        partnerGross: num($("partnerGross").value), age: num($("age").value) || 35, partnerAge: num($("partnerAge").value) || 0,
        medicalCard: $("medicalCard").checked, partnerMedicalCard: $("partnerMedicalCard").checked,
        selfEmployed: $("employment").value === "self", pensionPct: num($("pensionPct").value),
        rentPaid: num($("rent").value) * 12, homeCarer: $("homeCarer").checked, blind: +$("blind").value,
        incapChildren: num($("incap").value), depRelatives: num($("depRel").value)
      }
    };
  }

  function syncVisibility() {
    var st = radio("status");
    $("partnerBox").hidden = st !== "married2";
    $("homeCarerRow").hidden = !(st === "married1" || st === "married2");
    var adv = ADV.some(function (k) { var e = $(k); return e.value && e.value !== "0" && e.value !== "employee"; }) ||
              CHK.some(function (k) { return $(k).checked; }) || (st && st !== "single");
    $("adv").classList.toggle("has-values", adv);
  }

  // ---------- persistence (advanced options only, on this device)
  function save() {
    var s = { status: radio("status"), period: $("period").value };
    ADV.forEach(function (k) { s[k] = $(k).value; });
    CHK.forEach(function (k) { s[k] = $(k).checked; });
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {}
  }
  function restore() {
    var s = null;
    try { s = JSON.parse(localStorage.getItem(KEY)); } catch (e) {}
    if (s) {
      if (s.status) setRadio("status", s.status);
      if (s.period) $("period").value = s.period;
      ADV.forEach(function (k) { if (s[k] != null) $(k).value = s[k]; });
      CHK.forEach(function (k) { $(k).checked = !!s[k]; });
      if (s.status && s.status !== "single" || ADV.some(function (k) { return s[k] && s[k] !== "0" && s[k] !== "employee"; })) $("adv").open = true;
    }
    // URL wins (shared links and salary pages link here with ?gross=)
    var q = new URLSearchParams(location.search);
    if (q.get("gross")) $("gross").value = Number(num(q.get("gross"))).toLocaleString("en-IE");
    if (q.get("period")) $("period").value = q.get("period");
    var thisYear = new Date().getFullYear();
    var y = +q.get("year") || (YEARS[thisYear] ? thisYear : yearList[yearList.length - 1]);
    setRadio("year", YEARS[y] ? y : yearList[1]);
    if (q.get("status")) { setRadio("status", q.get("status")); $("adv").open = true; }
  }

  function updateUrl(inp) {
    var q = new URLSearchParams();
    if (inp.amount) q.set("gross", inp.amount);
    if (inp.period !== "year") q.set("period", inp.period);
    q.set("year", inp.calc.year);
    if (inp.calc.status && inp.calc.status !== "single") q.set("status", inp.calc.status);
    try { history.replaceState(null, "", location.pathname + "?" + q.toString()); } catch (e) {}
  }

  // ---------- render
  function compareYear(y) {
    var i = yearList.indexOf(y);
    if (i < yearList.length - 1 && y === new Date().getFullYear()) return { y: yearList[i + 1], dir: "next" };
    if (i > 0) return { y: yearList[i - 1], dir: "prev" };
    return { y: yearList[i + 1], dir: "next" };
  }

  function render(inp) {
    var r = T.calc(inp.calc), c = inp.calc;
    var married2 = r.status === "married2";
    var mine = married2 ? r.myNet : r.net;
    var P = T.periods(mine, inp.hours, inp.days);
    var cmp = compareYear(c.year), rc = T.calc(Object.assign({}, c, { year: cmp.y }));
    var other = married2 ? rc.myNet : rc.net;
    var diff = cmp.dir === "next" ? other - mine : mine - other;
    var later = cmp.dir === "next" ? cmp.y : c.year, earlier = cmp.dir === "next" ? c.year : cmp.y;

    var h = '<div class="net-hero"><div class="tl">Your take-home pay · ' + c.year + '</div><div class="amt">' + fmt(P.month, 2) + '</div><p>a month · ' + fmt(P.year, 0) + ' a year</p></div>';
    h += '<div class="periods">' + [["year", "Year"], ["month", "Month"], ["fortnight", "Fortnight"], ["week", "Week"], ["day", "Day"], ["hour", "Hour"]].map(function (p) {
      return '<div><b>' + fmt(P[p[0]], P[p[0]] >= 1000 ? 0 : 2) + '</b><span>per ' + p[1].toLowerCase() + '</span></div>';
    }).join("") + '</div>';

    // better off / worse off
    var up = diff >= 0, ytxt = later + (YEARS[later] && YEARS[later].budget ? " (" + YEARS[later].budget + ")" : "");
    h += '<div class="better' + (up ? "" : " worse") + '"><div class="em">' + (up ? "📈" : "📉") + '</div><p>' +
      (cmp.dir === "next" ? 'In ' + ytxt + ' you\'ll take home ' : 'Compared with ' + earlier + ', you take home ') +
      '<strong class="n">' + fmt(Math.abs(diff / 12), 2) + ' ' + (up ? "more" : "less") + ' a month</strong>' +
      ' <span class="muted">(' + (up ? "+" : "−") + fmt(Math.abs(diff), 0) + ' a year, ' + (up ? "+" : "−") + fmt(Math.abs(diff / 52), 2) + ' a week)</span>' +
      (cmp.dir === "next" ? '. <a href="#" id="seeNext" data-y="' + cmp.y + '">Show ' + cmp.y + ' →</a>' : '') + '</p></div>';

    // where the money goes
    var g = married2 ? r.gross : r.householdGross;
    var tax = married2 ? r.myIncomeTax : r.incomeTax;
    var parts = [["Take-home", mine, "c-net"], ["Income tax", tax, "c-tax"], ["USC", r.usc, "c-usc"], ["PRSI", r.prsi, "c-prsi"], ["Pension", r.pension, "c-pen"]]
      .filter(function (p) { return p[1] > 0.005; });
    if (g > 0) {
      h += '<div class="card"><div class="tl">Where your pay goes</div><div class="stack">' + parts.map(function (p) {
        return '<span class="' + p[2] + '" style="width:' + (p[1] / g * 100).toFixed(2) + '%" title="' + p[0] + '"></span>';
      }).join("") + '</div><ul class="legend">' + parts.map(function (p) {
        return '<li><i class="' + p[2] + '"></i>' + p[0] + ' ' + Math.round(p[1] / g * 100) + '%</li>';
      }).join("") + '</ul></div>';
    }

    // breakdown table
    function row(label, v, cls) {
      return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th scope="row">' + label + '</th><td class="num">' + f2(v) + '</td><td class="num">' + f2(v / 12) + '</td><td class="num">' + f2(v / 52) + '</td></tr>';
    }
    var t = '<h2>Your breakdown</h2><div class="table-wrap"><table><thead><tr><th></th><th class="num">Year</th><th class="num">Month</th><th class="num">Week</th></tr></thead><tbody>';
    t += row("Gross pay", r.gross);
    if (r.pension) t += row("Pension contribution", -r.pension);
    t += row(married2 ? "Income tax (your share)" : "Income tax (PAYE)", -tax);
    t += row("USC", -r.usc) + row("PRSI", -r.prsi);
    t += row("Take-home pay", mine, "total");
    if (married2) {
      t += row("Partner's gross pay", r.partnerGross, "sub") + row("Partner's take-home", r.net - r.myNet, "sub") + row("Household take-home", r.net, "total");
    }
    t += '</tbody></table></div>';
    h += t;

    // detail
    var credits = r.credits.map(function (x) { return '<tr class="sub"><th scope="row">' + esc(x.name) + '</th><td class="num">−' + f2(x.amount) + '</td></tr>'; }).join("");
    var uscRows = r.uscRows.map(function (u) { return '<tr class="sub"><th scope="row">' + (u.rate * 100).toFixed(1).replace(/\.0$/, "") + '% on ' + fmt(u.amount, 0) + (u.surcharge ? ' (self-employed surcharge)' : '') + '</th><td class="num">' + f2(u.tax) + '</td></tr>'; }).join("");
    var Y = YEARS[c.year];
    h += '<details class="faq"><summary>How your tax is worked out</summary><div><div class="table-wrap"><table><tbody>' +
      (r.pensionRelief ? '<tr class="sub"><th scope="row">Pension relief (taken off taxable income)</th><td class="num">−' + f2(r.pensionRelief) + '</td></tr>' : '') +
      '<tr class="sub"><th scope="row">20% on ' + fmt(r.at20, 0) + (married2 ? ' (joint)' : '') + '</th><td class="num">' + f2(r.at20 * 0.2) + '</td></tr>' +
      '<tr class="sub"><th scope="row">40% on ' + fmt(r.at40, 0) + '</th><td class="num">' + f2(r.at40 * 0.4) + '</td></tr>' +
      '<tr><th scope="row">Tax before credits</th><td class="num">' + f2(r.taxBeforeCredits) + '</td></tr>' + credits +
      '<tr class="total"><th scope="row">Income tax' + (married2 ? ' (couple)' : '') + '</th><td class="num">' + f2(r.incomeTax) + '</td></tr>' +
      uscRows + '<tr class="total"><th scope="row">USC</th><td class="num">' + f2(r.usc) + '</td></tr>' +
      '<tr class="total"><th scope="row">PRSI</th><td class="num">' + f2(r.prsi) + '</td></tr>' +
      '</tbody></table></div>';
    var notes = [];
    notes.push("Your 20% band: " + fmt(r.band, 0) + ". Effective rate " + r.effectiveRate.toFixed(1) + "% · marginal rate on your next €1: " + r.marginalRate + "%.");
    if (r.uscNote === "exempt") notes.push("You pay no USC because your income is " + fmt(T.USC_EXEMPT, 0) + " or less.");
    if (r.uscNote === "reduced") notes.push("Reduced USC applies (full medical card or aged 70+, income " + fmt(T.USC_REDUCED_LIMIT, 0) + " or less).");
    if (c.medicalCard && r.uscNote !== "reduced" && r.gross > T.USC_REDUCED_LIMIT) notes.push("Your income is over €60,000, so the medical card USC rate doesn't apply.");
    if (r.prsiNote === "exempt") notes.push("No PRSI – you earn €352 a week or less.");
    if (r.prsiNote === "66+") notes.push("No employee PRSI at 66 or over.");
    if (r.prsiNote === "classS") notes.push("Self-employed Class S PRSI (minimum €650 a year).");
    notes.push("PRSI is " + (Y.prsi.jan * 100).toFixed(2).replace(/0$/, "") + "% from January and " + (Y.prsi.oct * 100).toFixed(2).replace(/0$/, "") + "% from 1 October " + c.year + ", averaged over the year.");
    if (inp.period === "hour" && inp.amount && inp.amount < Y.minWage) notes.push("⚠️ " + f2(inp.amount) + " an hour is below the " + c.year + " minimum wage of " + f2(Y.minWage) + " (lower rates apply under 20).");
    if (r.taxBeforeCredits < r.creditsTotal && r.gross > 0) notes.push(f2(r.creditsTotal - r.taxBeforeCredits) + " of your tax credits are unused – credits can't be refunded.");
    h += '<ul class="notes">' + notes.map(function (n) { return "<li>" + n + "</li>"; }).join("") + '</ul></div></details>';

    h += '<div class="res-actions"><button type="button" class="btn" id="copyLink">🔗 Copy link to this result</button>' +
      '<a class="btn wa" target="_blank" rel="noopener" data-track="share" data-method="whatsapp" data-label="salary_result" href="https://wa.me/?text=' +
      encodeURIComponent("I worked out my take-home pay for " + c.year + " with this free Irish calculator: " + location.origin + location.pathname) + '">Share on WhatsApp</a></div>';
    h += '<p class="muted small">Estimate for a full tax year. Your payslip can differ (emergency tax, benefit-in-kind, health insurance, overtime, starting mid-year).</p>';
    out.innerHTML = h;

    var sn = $("seeNext");
    if (sn) sn.addEventListener("click", function (e) { e.preventDefault(); setRadio("year", sn.getAttribute("data-y")); go(true); });
    $("copyLink").addEventListener("click", function () {
      var b = this, u = location.href;
      var done = function () { b.textContent = "✓ Link copied"; setTimeout(function () { b.textContent = "🔗 Copy link to this result"; }, 2000); };
      if (navigator.clipboard) navigator.clipboard.writeText(u).then(done, function () { prompt("Copy this link:", u); });
      else prompt("Copy this link:", u);
      track("salary_link_copy", r);
    });
    return r;
  }

  function band(g) { return g < 20000 ? "<20k" : g < 30000 ? "20-30k" : g < 40000 ? "30-40k" : g < 50000 ? "40-50k" : g < 60000 ? "50-60k" : g < 80000 ? "60-80k" : g < 100000 ? "80-100k" : "100k+"; }
  function track(name, r) {
    if (window.TAVION && TAVION.track) TAVION.track(name, { tax_year: r.year, status: r.status, salary_band: band(r.gross), period: $("period").value,
      advanced: $("adv").open ? "yes" : "no" });
  }

  var lastTracked = "", timer = null;
  function go(scroll, explicit) {
    syncVisibility(); save();
    var inp = readInputs();
    if (!inp.amount) { out.innerHTML = ""; return; }
    updateUrl(inp);
    var r = render(inp);
    var key = [r.year, r.status, Math.round(r.gross)].join("|");
    if (explicit || key !== lastTracked) {
      clearTimeout(timer);
      // live typing: only count it once the user stops for a moment
      timer = setTimeout(function () { if (key !== lastTracked || explicit) { lastTracked = key; track("salary_calc", r); } }, explicit ? 0 : 1500);
    }
    if (scroll) out.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // ---------- wire up
  restore(); syncVisibility();
  var debounce = null;
  form.addEventListener("input", function (e) {
    if (e.target.id === "gross" || e.target.id === "partnerGross") {
      // keep thousands separators as you type
      var el = e.target, raw = el.value.replace(/[^\d.]/g, ""), parts = raw.split(".");
      if (parts[0]) {
        var formatted = Number(parts[0]).toLocaleString("en-IE") + (parts.length > 1 ? "." + parts[1].slice(0, 2) : "");
        if (formatted !== el.value) { el.value = formatted; try { el.setSelectionRange(formatted.length, formatted.length); } catch (x) {} }
      }
    }
    clearTimeout(debounce); debounce = setTimeout(function () { go(false); }, 250);
  });
  form.addEventListener("change", function () { go(false); });
  form.addEventListener("submit", function (e) { e.preventDefault(); go(true, true); });
  $("resetAdv").addEventListener("click", function () {
    setRadio("status", "single");
    ADV.forEach(function (k) { var el = $(k); el.value = el.tagName === "SELECT" ? el.options[0].value : ""; });
    CHK.forEach(function (k) { $(k).checked = false; });
    go(false);
  });
  $("adv").addEventListener("toggle", function () { if ($("adv").open && window.TAVION && TAVION.track) TAVION.track("salary_advanced_open", {}); });
  if (num($("gross").value)) go(false);
})();
