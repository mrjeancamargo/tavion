// Mortgage calculator UI. The rules live in mortgage.js (window.IEMORT); net pay uses salary/js/tax.js.
(function () {
  "use strict";
  var M = window.IEMORT, KEY = "tavion_mortgage_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("mortForm"), out = $("result");
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function eur(n, dp) { dp = dp || 0; return (n < 0 ? "−" : "") + "€" + Math.abs(n).toLocaleString("en-IE", { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function radio(n) { var r = form.querySelector('input[name="' + n + '"]:checked'); return r ? r.value : null; }
  function setRadio(n, v) { var r = form.querySelector('input[name="' + n + '"][value="' + v + '"]'); if (r) r.checked = true; }
  var MONEY = ["inc1", "inc2", "savings", "price", "htbTax", "curVal", "curMort", "var1", "var2"];
  var OTHER = ["county", "varPct", "rate", "term", "debts", "mSave"], CHK = ["newBuild", "apartment", "htb", "fhs", "joint"];

  function sync() {
    var two = radio("who") === "2", mover = radio("buyer") === "mover";
    $("inc2Box").hidden = !two; $("var2Row").hidden = !two; $("jointRow").hidden = !two;
    $("moverBox").hidden = !mover; $("ftbOnly").hidden = mover;
    $("htbTaxRow").hidden = !$("htb").checked;
  }
  function save() {
    var s = { buyer: radio("buyer"), who: radio("who"), selling: radio("selling") };
    MONEY.concat(OTHER).forEach(function (k) { s[k] = $(k).value; }); CHK.forEach(function (k) { s[k] = $(k).checked; });
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {}
  }
  function restore() {
    var s = null; try { s = JSON.parse(localStorage.getItem(KEY)); } catch (e) {}
    if (s) {
      MONEY.concat(OTHER).forEach(function (k) { if (s[k] != null && s[k] !== "") $(k).value = s[k]; });
      CHK.forEach(function (k) { if (s[k] != null) $(k).checked = s[k]; });
      ["buyer", "who", "selling"].forEach(function (k) { if (s[k]) setRadio(k, s[k]); });
      if (s.price || s.newBuild || s.htb || s.fhs || s.var1 || s.rate || s.term || s.debts || s.buyer === "mover") $("adv").open = true;
    }
    var q = new URLSearchParams(location.search);
    if (q.get("inc1")) $("inc1").value = Number(num(q.get("inc1"))).toLocaleString("en-IE");
    if (q.get("price")) { $("price").value = Number(num(q.get("price"))).toLocaleString("en-IE"); $("adv").open = true; }
    if (q.get("county") && M.COUNTY_NAMES[q.get("county")]) $("county").value = q.get("county");
    if (q.get("buyer") === "mover") { setRadio("buyer", "mover"); $("adv").open = true; }
  }

  function input() {
    var two = radio("who") === "2";
    return {
      buyer: radio("buyer"), incomes: [num($("inc1").value), two ? num($("inc2").value) : 0], variable: [num($("var1").value), two ? num($("var2").value) : 0],
      variablePct: $("varPct").value === "" ? 50 : num($("varPct").value), joint: two ? $("joint").checked : false,
      savings: num($("savings").value), price: num($("price").value), county: $("county").value, apartment: $("apartment").checked, newBuild: $("newBuild").checked,
      htb: $("htb").checked, htbTaxPaid: num($("htbTax").value) || null, fhs: $("fhs").checked,
      rate: num($("rate").value) || M.RULES.avgRate, term: num($("term").value) || 30,
      currentValue: num($("curVal").value), currentMortgage: num($("curMort").value), selling: radio("selling") !== "no",
      otherDebts: num($("debts").value), monthlySavings: num($("mSave").value)
    };
  }

  function row(l, v, cls) { return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th scope="row">' + l + '</th><td>' + v + '</td></tr>'; }

  function render() {
    sync(); save();
    var inp = input();
    if (!inp.incomes[0]) { out.innerHTML = ""; return null; }
    var o = M.calc(inp), h = "";
    var who = radio("who") === "2" ? "you can borrow together" : "you can borrow";
    h += '<div class="net-hero"><div class="tl">Up to · ' + (o.buyer === "ftb" ? "first-time buyer, 4×" : "mover, 3.5×") + ' income</div><div class="amt">' + eur(o.maxLoanLTI) + '</div><p>' + who +
      ' · homes up to about <strong>' + eur(o.maxPrice) + '</strong>' + (o.usingTarget ? '' : ' with your savings') + '</p></div>';
    if (o.depositLimited && !o.usingTarget) {
      h += '<div class="callout warn">💡 <strong>Your savings are what hold you back, not your income.</strong> To use your full ' + eur(o.maxLoanLTI) + ' mortgage (a home of about ' + eur(o.fullPrice) +
        ') you\'d need about <strong>' + eur(o.savingsForMax) + '</strong> for the deposit and costs' + (o.buyer === "ftb" && !inp.newBuild ? ' – or less with Help to Buy on a new home' : '') + '.</div>';
    }
    // purchase summary
    var t = '<h2>' + (o.usingTarget ? 'Buying at ' + eur(o.price) : 'Buying at your maximum (' + eur(o.price) + ')') + '</h2><div class="table-wrap"><table class="sumtab"><tbody>';
    t += row("Price", eur(o.price)) + row("Mortgage (" + o.ltv + "% LTV, " + o.lti + "× income)", eur(o.loan));
    if (o.htb) t += row("Help to Buy", eur(o.htb));
    if (o.fhsEquity) t += row("First Home Scheme equity (" + Math.round(o.fhsEquity / o.price * 100) + "%)", eur(o.fhsEquity));
    t += row("Your deposit", eur(o.deposit)) + row("Stamp duty", eur(o.stampDuty));
    t += row("Solicitor (incl. VAT)", eur(o.fees.solicitor), "sub") + row("Land Registry + mortgage registration", eur(o.fees.landRegistry), "sub") + row("Searches", eur(o.fees.searches), "sub") +
      row("Valuation", eur(o.fees.valuation), "sub") + (o.fees.survey ? row("Structural survey", eur(o.fees.survey), "sub") : "");
    t += row("Total cash you need", eur(o.cashNeeded), "total");
    if (o.buyer === "mover" && o.equity) t += row("Equity from your sale (after " + eur(o.sellCosts) + " selling costs)", eur(o.equity), "sub");
    t += row("You have" + (o.buyer === "mover" && o.equity > 0 ? " (savings + equity)" : ""), eur(o.funds));
    t += row(o.cashShortfall ? "Still to save" : "Left over", o.cashShortfall ? '<strong style="color:var(--bad)">' + eur(o.cashShortfall) + '</strong>' : eur(Math.max(0, o.funds - o.cashNeeded)));
    if (o.monthsToSave) t += row("Time to save it", o.monthsToSave + " months");
    t += '</tbody></table></div>';
    h += t;
    // repayments
    h += '<div class="periods" style="grid-template-columns:repeat(3,1fr)"><div><b>' + eur(o.monthly, 2) + '</b><span>per month · ' + o.term + ' yrs</span></div><div><b>' + eur(o.totalInterest) +
      '</b><span>total interest</span></div><div><b>' + eur(o.monthlyPlus2, 2) + '</b><span>if rates +2%</span></div></div>';
    h += '<p class="muted small" style="margin-top:0">At ' + o.rate + '% (average new mortgage rate ' + M.RULES.avgRate + '%, ' + M.RULES.rateMonth + '). Over 25 years: ' + eur(o.monthly25) + ' · over 35 years: ' + eur(o.monthly35) + ' a month.</p>';
    // affordability vs take-home pay
    if (o.netMonthly) {
      var sh = o.debtShare || o.repaymentShare, cls = sh > 40 ? "bad" : sh > 33 ? "warn" : "";
      h += '<div class="card"><div class="tl">Repayment vs take-home pay</div><div class="meter ' + cls + '"><span style="width:' + Math.min(100, sh) + '%"></span></div><p class="small" style="margin:0">' +
        eur(o.monthly) + (inp.otherDebts ? ' + ' + eur(inp.otherDebts) + ' other loans' : '') + ' is <strong>' + Math.round(sh) + '%</strong> of your take-home pay of about ' + eur(o.netMonthly) + ' a month. <a href="../salary/?gross=' + (inp.incomes[0] || "") + '">See your take-home pay →</a></p></div>';
    }
    // rent comparison
    var cheaper = o.rentDiff > 0;
    h += '<div class="better' + (cheaper ? "" : " worse") + '"><div class="em">' + (cheaper ? "🏡" : "📊") + '</div><p>Your repayment of <strong>' + eur(o.monthly) + '</strong> is <strong class="n">' + eur(Math.abs(o.rentDiff)) + ' ' + (cheaper ? "less" : "more") +
      '</strong> than the average new rent in ' + (o.countyName === "Ireland" ? "Ireland" : "County " + o.countyName) + ' (' + eur(o.avgRent) + ' a month, RTB Q1 2026). <a href="../rent/">Renting now? Check your rent increase →</a></p></div>';
    var items = [];
    o.warnings.forEach(function (w) { items.push(["bad", w]); });
    o.tips.forEach(function (w) { items.push(["warn", w]); });
    o.notes.forEach(function (w) { items.push(["", w]); });
    if (o.buyer === "ftb" && !inp.htb && inp.newBuild) items.push(["ok", "Buying new? Tick <strong>Help to Buy</strong> – up to €35,000 towards your deposit."]);
    if (o.buyer === "ftb" && !inp.newBuild) items.push(["", "Help to Buy and the First Home Scheme are for new homes. Second-hand? Look at the <a href='https://localauthorityhomeloan.ie/' target='_blank' rel='noopener'>Local Authority Home Loan</a> if your income is lower."]);
    items.push(["", "Lenders can lend above " + o.multiple + "× income for a limited number of borrowers – up to about " + eur(o.maxLoanException) + " for you. Don't count on it."]);
    h += '<ul class="issues">' + items.map(function (i) { return '<li class="' + i[0] + '">' + i[1] + '</li>'; }).join("") + '</ul>';
    h += '<p class="muted small">An estimate, not a mortgage offer. Fees are typical amounts – get quotes. Compare lenders on <a href="https://www.ccpc.ie/consumers/money/mortgages/" target="_blank" rel="noopener">ccpc.ie</a>.</p>';
    h += '<div class="res-actions"><a class="btn" href="../stamp-duty/?price=' + o.price + (inp.newBuild ? "&new=1" : "") + '" data-track="cross_app" data-label="stamp_from_mortgage">Stamp duty &amp; fees breakdown →</a><a class="btn wa" target="_blank" rel="noopener" data-track="share" data-method="whatsapp" data-label="mortgage_result" href="https://wa.me/?text=' +
      encodeURIComponent("See how much you can borrow for a mortgage in Ireland – free calculator: " + location.origin + location.pathname) + '">Share on WhatsApp</a></div>';
    out.innerHTML = h;
    return o;
  }

  function band(x) { return x < 40000 ? "<40k" : x < 60000 ? "40-60k" : x < 80000 ? "60-80k" : x < 100000 ? "80-100k" : x < 150000 ? "100-150k" : "150k+"; }
  var tracked = "";
  function go(scroll) {
    var o = render(); if (!o) return;
    var key = radio("buyer") + radio("who") + band(o.income);
    if (scroll || key !== tracked) {
      tracked = key;
      if (window.TAVION && TAVION.track) TAVION.track("mortgage_calc", { label: $("county").value, mode: radio("buyer"), status: radio("who") === "2" ? "joint" : "sole",
        salary_band: band(o.income), result: o.cashShortfall ? "shortfall" : "ok", advanced: $("adv").open ? "yes" : "no" });
    }
    if (scroll) out.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  restore(); sync();
  var t = null;
  form.addEventListener("input", function (e) {
    if (MONEY.indexOf(e.target.id) >= 0) {
      var el = e.target, raw = el.value.replace(/[^\d.]/g, ""), p = raw.split(".");
      if (p[0]) { var f = Number(p[0]).toLocaleString("en-IE") + (p.length > 1 ? "." + p[1].slice(0, 2) : ""); if (f !== el.value) el.value = f; }
    }
    clearTimeout(t); t = setTimeout(function () { go(false); }, 350);
  });
  form.addEventListener("change", function () { go(false); });
  form.addEventListener("submit", function (e) { e.preventDefault(); go(true); });
  $("resetAdv").addEventListener("click", function () {
    ["price", "htbTax", "curVal", "curMort", "var1", "var2", "varPct", "rate", "term", "debts", "mSave"].forEach(function (k) { $(k).value = ""; });
    ["newBuild", "apartment", "htb", "fhs"].forEach(function (k) { $(k).checked = false; }); render();
  });
  render();
})();
