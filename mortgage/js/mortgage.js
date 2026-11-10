/*
 * Irish mortgage engine: how much you can borrow (Central Bank mortgage measures), repayments,
 * deposit, stamp duty, fees, Help to Buy, First Home Scheme and mover equity.
 * Used by the calculator in the browser AND by tools/build_mortgage.py (through Node).
 * If the take-home pay engine (salary/js/tax.js → IETAX) is loaded, it is used for net pay.
 *
 * Sources (checked November 2026):
 *  - Central Bank of Ireland – Mortgage measures (LTI 4x FTB / 3.5x SSB; LTV 90%; allowances 15%; bridging-loan change April 2026)
 *  - Central Bank retail interest rate statistics – new mortgages August 2026: 3.53% average (fixed 3.49%)
 *  - Revenue / Citizens Information – Help to Buy (max €35,000 from 7 Oct 2026, 10% of price, new homes ≤ €500,000, LTV ≥ 70%)
 *  - First Home Scheme – property price ceilings (Citizens Information, 2026)
 *  - Revenue – stamp duty on residential property: 1% to €1m, 2% €1m–€1.5m, 6% above €1.5m
 *  - RTB Rent Index Q1 2026 – standardised average rent, new tenancies, by county
 */
(function (root) {
  "use strict";
  var RULES = {
    lti: { ftb: 4, mover: 3.5 }, ltv: { ftb: 0.9, mover: 0.9 }, allowanceLti: 0.5, // illustrative: lenders' allowance can lift LTI (e.g. to 4.5x)
    htbMax: 35000, htbPct: 0.10, htbPriceCap: 500000, htbMinLtv: 0.70,
    fhsMax: 0.30, fhsMaxWithHtb: 0.20,
    avgRate: 3.53, avgFixed: 3.49, rateMonth: "August 2026",
    vat: 0.135, maxTerm: 35
  };
  // RTB Rent Index Q1 2026 – standardised average monthly rent, new tenancies. National €1,839.
  var RENT = { national: 1839, dublin: 2335, wicklow: 1888, kildare: 1852, limerick: 1744, galway: 1718, meath: 1706, cork: 1678, louth: 1526,
    laois: 1408, westmeath: 1379, waterford: 1371, carlow: 1357, clare: 1333, kerry: 1311, kilkenny: 1298, sligo: 1290, wexford: 1231,
    longford: 1215, offaly: 1212, cavan: 1204, tipperary: 1204, mayo: 1153, roscommon: 1132, donegal: 1107, monaghan: 1081, leitrim: 1040 };
  // First Home Scheme price ceilings (house / apartment), by county. Some counties have several local authorities – the main one is used.
  var FHS = { dublin: [500000, 500000], wicklow: [500000, 500000], cork: [450000, 450000], corkcity: [500000, 500000], kildare: [475000, 475000], meath: [475000, 475000],
    galway: [450000, 450000], galwaycity: [475000, 475000], limerick: [450000, 450000], kerry: [425000, 425000], louth: [425000, 425000], mayo: [425000, 425000],
    waterford: [400000, 450000], clare: [400000, 400000], donegal: [400000, 400000], kilkenny: [400000, 400000], laois: [400000, 400000], leitrim: [400000, 400000],
    roscommon: [400000, 400000], sligo: [400000, 400000], westmeath: [400000, 400000], wexford: [400000, 400000], carlow: [375000, 375000], cavan: [375000, 375000],
    longford: [375000, 375000], monaghan: [375000, 375000], offaly: [375000, 375000], tipperary: [375000, 375000] };
  var COUNTY_NAMES = { carlow: "Carlow", cavan: "Cavan", clare: "Clare", cork: "Cork", donegal: "Donegal", dublin: "Dublin", galway: "Galway", kerry: "Kerry",
    kildare: "Kildare", kilkenny: "Kilkenny", laois: "Laois", leitrim: "Leitrim", limerick: "Limerick", longford: "Longford", louth: "Louth", mayo: "Mayo",
    meath: "Meath", monaghan: "Monaghan", offaly: "Offaly", roscommon: "Roscommon", sligo: "Sligo", tipperary: "Tipperary", waterford: "Waterford",
    westmeath: "Westmeath", wexford: "Wexford", wicklow: "Wicklow" };
  // Typical fees (estimates, incl. VAT where it applies). Real quotes vary.
  var FEES = { solicitor: 3075, landRegistry: 975, searches: 300, valuation: 185, survey: 500, mortgageReg: 175 };
  var SELL = { agentPct: 0.015, legal: 1845 }; // estate agent 1.5% + VAT, solicitor on the sale

  function r0(x) { return Math.round(x); }
  function r2(x) { return Math.round(x * 100) / 100; }

  function payment(loan, ratePct, years) {
    if (loan <= 0) return 0;
    var r = ratePct / 100 / 12, n = years * 12;
    return r === 0 ? loan / n : loan * r / (1 - Math.pow(1 + r, -n));
  }
  function loanFromPayment(pmt, ratePct, years) {
    var r = ratePct / 100 / 12, n = years * 12;
    return r === 0 ? pmt * n : pmt * (1 - Math.pow(1 + r, -n)) / r;
  }
  function stampDuty(price, newBuild) {
    var p = newBuild ? price / (1 + RULES.vat) : price; // stamp duty is charged on the VAT-exclusive price
    var d = Math.min(p, 1000000) * 0.01 + Math.max(0, Math.min(p, 1500000) - 1000000) * 0.02 + Math.max(0, p - 1500000) * 0.06;
    return r0(d);
  }

  // Net take-home pay per month (uses the salary engine when available).
  function netMonthly(year, incomes, joint) {
    var T = root.IETAX || (typeof require === "function" ? (function () { try { return require("../../salary/js/tax.js"); } catch (e) { return null; } })() : null);
    if (!T) return null;
    var a = incomes[0] || 0, b = incomes[1] || 0, net;
    if (joint && b > 0) net = T.calc({ year: year, gross: a, status: "married2", partnerGross: b }).net;
    else net = T.calc({ year: year, gross: a }).net + (b > 0 ? T.calc({ year: year, gross: b }).net : 0);
    return net / 12;
  }

  /*
   * inp = {
   *   buyer: "ftb" | "mover", incomes: [gross1, gross2], variable: [bonus/overtime1, 2], variablePct: 50 (share lenders count),
   *   joint: true (married/civil partners – joint tax assessment for net pay), savings: deposit saved,
   *   price: target price (optional), county, apartment: false, newBuild: false, htb: false, htbTaxPaid: (optional, tax paid in last 4 years),
   *   fhs: false, fhsPct: up to 30, rate: 3.53, term: 30,
   *   // movers
   *   currentValue, currentMortgage, selling: true, otherDebts: monthly car loan / credit, monthlySavings (to estimate time to save)
   * }
   */
  function calc(inp) {
    var o = { notes: [], warnings: [], tips: [] };
    var buyer = inp.buyer === "mover" ? "mover" : "ftb";
    var inc = (inp.incomes || []).map(function (x) { return Math.max(0, +x || 0); });
    var vari = (inp.variable || []).map(function (x) { return Math.max(0, +x || 0); });
    var vPct = inp.variablePct == null ? 50 : Math.max(0, Math.min(100, +inp.variablePct));
    var basic = inc.reduce(function (s, x) { return s + x; }, 0);
    var variable = vari.reduce(function (s, x) { return s + x; }, 0) * vPct / 100;
    var income = basic + variable;
    var rate = +inp.rate || RULES.avgRate, term = Math.min(RULES.maxTerm, Math.max(5, +inp.term || 30));
    var mult = RULES.lti[buyer];
    o.buyer = buyer; o.income = r0(income); o.basicIncome = r0(basic); o.variableCounted = r0(variable); o.multiple = mult;
    o.maxLoanLTI = r0(income * mult);
    o.maxLoanException = r0(income * (mult + RULES.allowanceLti));
    o.rate = rate; o.term = term;

    // ---- funds available for the deposit
    var savings = Math.max(0, +inp.savings || 0), equity = 0, sellCosts = 0;
    if (buyer === "mover") {
      var cv = Math.max(0, +inp.currentValue || 0), cm = Math.max(0, +inp.currentMortgage || 0);
      if (inp.selling !== false && cv > 0) {
        sellCosts = r0(cv * SELL.agentPct * 1.23 + SELL.legal);
        equity = cv - cm - sellCosts;
        if (equity < 0) o.warnings.push("Your home is worth less than the mortgage plus selling costs (negative equity). Borrowers in negative equity are exempt from the LTV limit but not the income limit – talk to your lender.");
      } else if (cv > 0) {
        o.notes.push("You're keeping your current home: lenders will count its mortgage repayments when they check affordability, and you'll pay stamp duty and fees on the new home as normal. A bridging loan (up to 18 months) is exempt from the income limit since April 2026.");
      }
      o.currentValue = cv; o.currentMortgage = cm; o.sellCosts = sellCosts; o.equity = r0(equity);
    }
    var funds = savings + Math.max(0, equity);

    // ---- Help to Buy estimate (new builds only, first-time buyers)
    var htbOn = !!inp.htb && buyer === "ftb";
    var htbCapTax = inp.htbTaxPaid ? +inp.htbTaxPaid : null;
    if (htbCapTax === null) { // estimate income tax paid in the last 4 years from the salary engine
      var T = root.IETAX || null;
      if (!T && typeof require === "function") { try { T = require("../../salary/js/tax.js"); } catch (e) { T = null; } }
      if (T) htbCapTax = inc.reduce(function (s, x) { return s + (x > 0 ? T.calc({ year: 2026, gross: x }).incomeTax * 4 : 0); }, 0);
    }

    // ---- First Home Scheme
    var fhsOn = !!inp.fhs && (buyer === "ftb" || inp.fhsMover);
    var fhsShare = fhsOn ? Math.min(+inp.fhsPct || 30, htbOn ? RULES.fhsMaxWithHtb * 100 : RULES.fhsMax * 100) / 100 : 0;
    var ceil = FHS[inp.county] ? FHS[inp.county][inp.apartment ? 1 : 0] : null;

    // ---- maximum price you could reach
    var maxLoan = o.maxLoanLTI;
    function htbFor(price) {
      if (!htbOn || !inp.newBuild || price > RULES.htbPriceCap) return 0;
      var v = Math.min(RULES.htbMax, price * RULES.htbPct);
      if (htbCapTax !== null) v = Math.min(v, htbCapTax);
      return r0(v);
    }
    function costsFor(price) {
      return stampDuty(price, inp.newBuild) + FEES.solicitor + FEES.landRegistry + FEES.mortgageReg + FEES.searches + FEES.valuation + (inp.newBuild ? 0 : FEES.survey);
    }
    // Split a price into loan, deposit, Help to Buy and First Home Scheme equity.
    // The First Home Scheme only fills the gap between (mortgage + deposit) and the price, up to its share.
    function split(price) {
      var h = htbFor(price), depFunds = Math.max(0, funds - costsFor(price));
      var loanCap = Math.min(maxLoan, price * RULES.ltv[buyer]);
      var gap = price - depFunds - h - loanCap;
      var eq = fhsShare ? Math.max(0, Math.min(price * fhsShare, gap)) : 0;
      var loanNeed = Math.max(0, price - depFunds - h - eq);
      return { h: h, eq: eq, loan: Math.min(loanNeed, loanCap), loanNeed: loanNeed, depFunds: depFunds, loanCap: loanCap };
    }
    function reach(price) {
      var s = split(price);
      return s.loanNeed <= s.loanCap + 0.5 && (s.depFunds + s.h) >= price * (1 - RULES.ltv[buyer]) - 0.5;
    }
    var lo = 0, hi = 5000000;
    for (var i = 0; i < 60; i++) { var mid = (lo + hi) / 2; if (reach(mid)) lo = mid; else hi = mid; }
    o.maxPrice = Math.floor(lo / 1000) * 1000;
    if (fhsOn && ceil && o.maxPrice > ceil) { o.maxPrice = ceil; o.notes.push("Capped at the First Home Scheme price ceiling for this area (€" + ceil.toLocaleString("en-IE") + ")."); }
    var sMax = split(o.maxPrice);
    o.depositLimited = sMax.loan < maxLoan - 1000; // the deposit, not the income limit, is what holds you back
    var fullPrice = maxLoan / RULES.ltv[buyer];
    o.fullPrice = r0(fullPrice);
    o.savingsForMax = r0(Math.max(0, fullPrice * (1 - RULES.ltv[buyer]) + costsFor(fullPrice) - htbFor(fullPrice) - Math.max(0, equity)));

    // ---- the purchase we work out costs for (target price, or the maximum)
    var price = +inp.price > 0 ? +inp.price : o.maxPrice;
    o.price = r0(price); o.usingTarget = +inp.price > 0;
    var sp = split(price), htb = sp.h, fhsEq = r0(sp.eq);
    if (htbOn && !inp.newBuild) o.warnings.push("Help to Buy is only for new homes (or self-builds). It isn't included for a second-hand home.");
    if (htbOn && inp.newBuild && price > RULES.htbPriceCap) o.warnings.push("Help to Buy only applies to new homes costing €500,000 or less.");
    if (fhsOn && ceil && price > ceil) o.warnings.push("This price is above the First Home Scheme ceiling for the area (€" + ceil.toLocaleString("en-IE") + ").");
    var minDeposit = r0(price * (1 - RULES.ltv[buyer]));
    // Mortgage: what's needed after the deposit you can put down, never above 90% of the price.
    var loan = Math.min(sp.loanNeed, price * RULES.ltv[buyer]);
    var depositFromYou = Math.max(0, price - loan - htb - fhsEq);
    o.htb = htb; o.fhsEquity = fhsEq; o.fhsShare = fhsShare; o.fhsCeiling = ceil;
    o.loan = r0(loan); o.ltv = price ? r2(loan / price * 100) : 0; o.lti = income ? r2(loan / income) : 0;
    o.minDeposit = minDeposit; o.deposit = r0(depositFromYou);
    o.loanOverLti = loan > o.maxLoanLTI + 1;
    if (o.loanOverLti) o.warnings.push("This needs a mortgage of " + r0(loan).toLocaleString("en-IE") + ", above the " + mult + "× income limit (" + o.maxLoanLTI.toLocaleString("en-IE") + "). You'd need a lender's exception (they can lend above the limit for a share of their loans) or a bigger deposit.");
    if (fhsOn && htbOn && htb > 0 && htb < RULES.htbMax && price * RULES.htbPct > htb + 1) o.notes.push("Help to Buy is limited by the income tax you paid in the last 4 years – we estimated it from your salary. Check your exact figure in Revenue myAccount.");
    if (htbOn && inp.newBuild && loan < price * RULES.htbMinLtv) o.warnings.push("Help to Buy needs a mortgage of at least 70% of the price.");

    // ---- costs
    var fees = { solicitor: FEES.solicitor, landRegistry: FEES.landRegistry + FEES.mortgageReg, searches: FEES.searches, valuation: FEES.valuation, survey: inp.newBuild ? 0 : FEES.survey };
    var feeTotal = Object.keys(fees).reduce(function (s, k) { return s + fees[k]; }, 0);
    var stamp = stampDuty(price, inp.newBuild);
    o.stampDuty = stamp; o.fees = fees; o.feesTotal = feeTotal;
    o.cashNeeded = r0(depositFromYou + stamp + feeTotal);         // money you need from savings / equity
    o.cashShortfall = r0(Math.max(0, o.cashNeeded - funds));
    o.funds = r0(funds); o.savings = r0(savings);
    if (inp.monthlySavings > 0 && o.cashShortfall > 0) o.monthsToSave = Math.ceil(o.cashShortfall / inp.monthlySavings);

    // ---- repayments
    var pm = payment(loan, rate, term);
    o.monthly = r2(pm); o.totalRepaid = r0(pm * term * 12); o.totalInterest = r0(pm * term * 12 - loan);
    o.monthlyPlus2 = r2(payment(loan, rate + 2, term));
    o.monthly35 = r2(payment(loan, rate, 35)); o.monthly25 = r2(payment(loan, rate, 25));
    var netM = netMonthly(new Date().getFullYear() >= 2027 ? 2027 : 2026, inc.map(function (x, i) { return x + (vari[i] || 0); }), inp.joint !== false);
    if (netM) {
      o.netMonthly = r0(netM);
      o.repaymentShare = r2(pm / netM * 100);
      var other = Math.max(0, +inp.otherDebts || 0);
      o.debtShare = r2((pm + other) / netM * 100);
      if (o.debtShare > 40) o.warnings.push("Your mortgage" + (other ? " plus other loans" : "") + " would take " + Math.round(o.debtShare) + "% of your take-home pay. Lenders usually want this well below 40% – it may be hard to get approval.");
      else if (o.debtShare > 33) o.tips.push("Repayments would be " + Math.round(o.debtShare) + "% of your take-home pay – manageable, but lenders will look closely at your spending and savings record.");
      if (other) o.notes.push("Other loans (" + other + " a month) don't change the Central Bank income limit, but lenders take them off what you can afford – clear them before applying if you can.");
    }
    // ---- rent comparison
    var avgRent = RENT[inp.county] || RENT.national;
    o.avgRent = avgRent; o.rentDiff = r0(avgRent - pm);
    o.countyName = COUNTY_NAMES[inp.county] || "Ireland";
    if (buyer === "ftb" && !(inp.incomes && inp.incomes[1] > 0)) o.notes.push("Buying with a partner? Two incomes are added together for the 4× limit.");
    return o;
  }

  // Simple helper for the static pages: maximum borrowing for an income.
  function borrow(income, buyer) { return r0(income * RULES.lti[buyer === "mover" ? "mover" : "ftb"]); }

  var API = { RULES: RULES, RENT: RENT, FHS: FHS, COUNTY_NAMES: COUNTY_NAMES, FEES: FEES, calc: calc, payment: payment, loanFromPayment: loanFromPayment,
              stampDuty: stampDuty, borrow: borrow, netMonthly: netMonthly };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.IEMORT = API;
})(this);
