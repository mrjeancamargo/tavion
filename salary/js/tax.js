/*
 * Irish take-home pay engine (income tax, USC, PRSI) for 2025, 2026 and 2027.
 * Used by the calculator in the browser AND by tools/build_salary.py (through Node)
 * to pre-compute the static salary pages, so both always show the same numbers.
 *
 * To add a new tax year: copy the latest entry in YEARS, change the figures, and
 * re-run `python tools/build_salary.py`.
 *
 * Sources (checked November 2026): Revenue tax credit & rate charts (2025, 2026),
 * Budget 2027 (6 October 2026) – KPMG Budget 2027 tax tables, Citizens Information.
 */
(function (root) {
  "use strict";

  var YEARS = {
    2025: {
      label: "2025", budget: "Budget 2025",
      band: { single: 44000, parent: 48000, married: 53000, secondMax: 35000 },
      credits: { personal: 2000, married: 4000, widowed: 2540, employee: 2000, earned: 2000,
                 homeCarer: 1950, spccc: 1900, age: 245, ageMarried: 490, blind: 1950,
                 incapChild: 3800, depRelative: 305, rentSingle: 1000, rentCouple: 2000 },
      // USC: [upper limit of band, rate]
      usc: [[12012, 0.005], [27382, 0.02], [70044, 0.03], [Infinity, 0.08]],
      // Employee PRSI (Class A): rate Jan–Sep, rate from 1 October
      prsi: { jan: 0.041, oct: 0.042 },
      minWage: 13.50
    },
    2026: {
      label: "2026", budget: "Budget 2026",
      band: { single: 44000, parent: 48000, married: 53000, secondMax: 35000 },
      credits: { personal: 2000, married: 4000, widowed: 2540, employee: 2000, earned: 2000,
                 homeCarer: 1950, spccc: 1900, age: 245, ageMarried: 490, blind: 1950,
                 incapChild: 3800, depRelative: 305, rentSingle: 1000, rentCouple: 2000 },
      usc: [[12012, 0.005], [28700, 0.02], [70044, 0.03], [Infinity, 0.08]],
      prsi: { jan: 0.042, oct: 0.0435 },
      minWage: 14.15
    },
    2027: {
      label: "2027", budget: "Budget 2027",
      band: { single: 46500, parent: 50500, married: 55500, secondMax: 37500 },
      credits: { personal: 2125, married: 4250, widowed: 2540, employee: 2125, earned: 2125,
                 homeCarer: 2050, spccc: 1900, age: 245, ageMarried: 490, blind: 1950,
                 incapChild: 3800, depRelative: 305, rentSingle: 1150, rentCouple: 2300 },
      usc: [[12012, 0.005], [30300, 0.02], [70044, 0.03], [Infinity, 0.08]],
      prsi: { jan: 0.0435, oct: 0.045 },
      minWage: 14.94
    }
  };

  var USC_EXEMPT = 13000;          // total income at or below this pays no USC
  var USC_REDUCED_LIMIT = 60000;   // 70+ or full medical card: max 2% if income <= this
  var USC_SURCHARGE = 0.03;        // self-employed income over €100,000
  var HOME_CARER_LIMIT = 7200;     // carer's own income for the full Home Carer credit
  var PENSION_CAP = 115000;        // earnings limit for pension tax relief
  var PRSI_WEEKLY_EXEMPT = 352, PRSI_CREDIT_MAX = 12, PRSI_CREDIT_TOP = 424;
  var WEEKS_JAN_SEP = 39, WEEKS = 52;

  function r2(n) { return Math.round(n * 100) / 100; }

  function pensionLimit(age) {
    return age < 30 ? 0.15 : age < 40 ? 0.20 : age < 50 ? 0.25 : age < 55 ? 0.30 : age < 60 ? 0.35 : 0.40;
  }

  // USC for one person
  function usc(Y, gross, o) {
    if (gross <= USC_EXEMPT) return { total: 0, rows: [], note: "exempt" };
    var bands = Y.usc, reduced = false;
    if ((o.age >= 70 || o.medicalCard) && gross <= USC_REDUCED_LIMIT) {
      bands = [[12012, 0.005], [Infinity, 0.02]]; reduced = true;
    }
    var prev = 0, total = 0, rows = [];
    for (var i = 0; i < bands.length; i++) {
      var top = bands[i][0], rate = bands[i][1];
      if (gross <= prev) break;
      var part = Math.min(gross, top) - prev;
      var amt = part * rate;
      rows.push({ rate: rate, amount: part, tax: amt });
      total += amt; prev = top;
    }
    if (o.selfEmployed && gross > 100000) {
      var s = (gross - 100000) * USC_SURCHARGE;
      rows.push({ rate: USC_SURCHARGE, amount: gross - 100000, tax: s, surcharge: true });
      total += s;
    }
    return { total: total, rows: rows, note: reduced ? "reduced" : "" };
  }

  // Weekly employee PRSI at one rate (Class A1, with the PRSI credit)
  function prsiWeek(weekly, rate) {
    if (weekly <= PRSI_WEEKLY_EXEMPT) return 0;
    var p = weekly * rate;
    if (weekly <= PRSI_CREDIT_TOP) p -= Math.max(0, PRSI_CREDIT_MAX - (weekly - PRSI_WEEKLY_EXEMPT) / 6);
    return Math.max(0, p);
  }

  // Annual PRSI for one person. The rate changes every 1 October, so 39 weeks at the
  // January rate and 13 weeks at the October rate.
  function prsi(Y, gross, o) {
    if (o.age >= 66) return { total: 0, note: "66+" };
    if (o.selfEmployed) { // Class S
      if (gross <= 5000) return { total: 0, note: "under5000" };
      var rS = (Y.prsi.jan * WEEKS_JAN_SEP + Y.prsi.oct * (WEEKS - WEEKS_JAN_SEP)) / WEEKS;
      return { total: Math.max(650, gross * rS), note: "classS" };
    }
    var w = gross / WEEKS;
    var t = prsiWeek(w, Y.prsi.jan) * WEEKS_JAN_SEP + prsiWeek(w, Y.prsi.oct) * (WEEKS - WEEKS_JAN_SEP);
    return { total: t, note: w <= PRSI_WEEKLY_EXEMPT ? "exempt" : "" };
  }

  /*
   * calc(input) – everything is per year (annual euro amounts).
   * input = {
   *   year: 2026, gross: 45000,
   *   status: "single" | "parent" | "widowed" | "married1" | "married2" | "separate",
   *   partnerGross: 0,           // married2 only
   *   age: 35, partnerAge: 35,
   *   medicalCard: false, partnerMedicalCard: false,
   *   selfEmployed: false,
   *   pensionPct: 0,             // your pension contribution, % of gross (tax relief at your marginal rate)
   *   rentPaid: 0,               // rent paid in the year (Rent Tax Credit = 20%, capped)
   *   homeCarer: false,          // married1: partner cares for a dependant at home
   *   blind: 0,                  // number of blind people (you / partner) 0–2
   *   incapChildren: 0, depRelatives: 0
   * }
   */
  function calc(inp) {
    var Y = YEARS[inp.year] || YEARS[2026], C = Y.credits;
    var st = inp.status || "single";
    var gross = Math.max(0, +inp.gross || 0);
    var married = st === "married1" || st === "married2";
    var partnerGross = st === "married2" ? Math.max(0, +inp.partnerGross || 0) : 0;
    var age = +inp.age || 35, pAge = +inp.partnerAge || age;
    var me = { age: age, medicalCard: !!inp.medicalCard, selfEmployed: !!inp.selfEmployed };
    var pt = { age: pAge, medicalCard: !!inp.partnerMedicalCard, selfEmployed: false };

    // Pension contributions reduce income for income tax only (not USC or PRSI).
    var pensionPct = Math.max(0, Math.min(+inp.pensionPct || 0, 100)) / 100;
    var pension = gross * pensionPct;
    var pensionRelief = Math.min(pension, Math.min(gross, PENSION_CAP) * pensionLimit(age));
    var taxable = Math.max(0, gross - pensionRelief);
    var pTaxable = partnerGross;
    var combined = taxable + pTaxable;

    // ---- standard-rate band
    var band;
    if (st === "married2") band = Y.band.married + Math.min(Y.band.secondMax, Math.min(taxable, pTaxable));
    else if (st === "married1") band = Y.band.married;
    else if (st === "parent") band = Y.band.parent;
    else band = Y.band.single;

    // ---- credits
    var credits = [];
    function add(name, v) { if (v > 0) credits.push({ name: name, amount: v }); }
    if (married) add("Married person's credit", C.married);
    else if (st === "widowed") add("Widowed person's credit", C.widowed);
    else add("Personal credit", C.personal);
    if (st === "parent") add("Single Person Child Carer credit", C.spccc);
    // Employee (PAYE) credit is capped at 20% of employment income; Earned Income credit for self-employed.
    if (me.selfEmployed) add("Earned Income credit", Math.min(C.earned, gross * 0.2));
    else add("Employee (PAYE) credit", Math.min(C.employee, gross * 0.2));
    if (st === "married2") add("Partner's Employee (PAYE) credit", Math.min(C.employee, partnerGross * 0.2));
    if (age >= 65 || (married && pAge >= 65)) add("Age credit", married ? C.ageMarried : C.age);
    if (inp.blind) add("Blind person's credit", C.blind * Math.min(2, +inp.blind || 0));
    if (inp.incapChildren) add("Incapacitated child credit", C.incapChild * (+inp.incapChildren || 0));
    if (inp.depRelatives) add("Dependent relative credit", C.depRelative * (+inp.depRelatives || 0));
    if (inp.rentPaid > 0) add("Rent Tax Credit", Math.min(inp.rentPaid * 0.2, married ? C.rentCouple : C.rentSingle));

    function incomeTax(bandAmt, extraCredit) {
      var at20 = Math.min(combined, bandAmt), at40 = Math.max(0, combined - bandAmt);
      var gt = at20 * 0.2 + at40 * 0.4;
      var cr = credits.reduce(function (s, c) { return s + c.amount; }, 0) + (extraCredit || 0);
      return { at20: at20, at40: at40, gross: gt, credits: cr, net: Math.max(0, gt - cr) };
    }
    var it = incomeTax(band, 0), homeCarerUsed = 0;
    // Home Carer credit: married couples where the carer earns little. Can't be combined with
    // the increased band for a second earner, so use whichever is better.
    if (inp.homeCarer && married) {
      var carerInc = st === "married2" ? partnerGross : 0;
      var hc = Math.max(0, C.homeCarer - Math.max(0, carerInc - HOME_CARER_LIMIT) / 2);
      if (hc > 0) {
        var alt = incomeTax(Y.band.married, hc);
        if (alt.net < it.net) { it = alt; band = Y.band.married; homeCarerUsed = hc; }
      }
    }
    if (homeCarerUsed) add("Home Carer credit", homeCarerUsed);

    var uMe = usc(Y, gross, me), pMe = prsi(Y, gross, me);
    var uPt = st === "married2" ? usc(Y, partnerGross, pt) : { total: 0, rows: [] };
    var pPt = st === "married2" ? prsi(Y, partnerGross, pt) : { total: 0 };

    var householdGross = gross + partnerGross;
    var totalDeductions = it.net + uMe.total + uPt.total + pMe.total + pPt.total + pension;
    var net = householdGross - totalDeductions;

    // Split joint income tax between partners by share of tax before credits (for display only).
    var myTax = it.net;
    if (st === "married2" && combined > 0) myTax = it.net * (taxable / combined);
    var myNet = gross - myTax - uMe.total - pMe.total - pension;

    // Marginal rate on the next euro you earn
    var marg = (combined >= band ? 0.4 : 0.2);
    if (it.net === 0 && it.gross < it.credits) marg = 0;
    var uscBands = (uMe.note === "reduced") ? [[12012, 0.005], [Infinity, 0.02]] : Y.usc, um = 0;
    if (gross > USC_EXEMPT) for (var i = 0; i < uscBands.length; i++) { if (gross <= uscBands[i][0]) { um = uscBands[i][1]; break; } }
    if (me.selfEmployed && gross > 100000) um += USC_SURCHARGE;
    var pm = (age >= 66) ? 0 : (me.selfEmployed ? Y.prsi.oct : (gross / WEEKS > PRSI_WEEKLY_EXEMPT ? Y.prsi.oct : 0));

    return {
      year: +inp.year, status: st,
      gross: r2(gross), partnerGross: r2(partnerGross), householdGross: r2(householdGross),
      pension: r2(pension), pensionRelief: r2(pensionRelief),
      band: band, at20: r2(it.at20), at40: r2(it.at40), taxBeforeCredits: r2(it.gross),
      credits: credits.map(function (c) { return { name: c.name, amount: r2(c.amount) }; }),
      creditsTotal: r2(it.credits), incomeTax: r2(it.net), myIncomeTax: r2(myTax),
      usc: r2(uMe.total), uscRows: uMe.rows, uscNote: uMe.note || "", partnerUsc: r2(uPt.total),
      prsi: r2(pMe.total), prsiNote: pMe.note || "", partnerPrsi: r2(pPt.total),
      totalDeductions: r2(totalDeductions), net: r2(net), myNet: r2(myNet),
      effectiveRate: householdGross ? r2((totalDeductions - pension) / householdGross * 100) : 0,
      marginalRate: r2((marg + um + pm) * 100)
    };
  }

  // Convert an amount in a period to a year. hours = hours per week, days = days per week.
  function toYear(amount, period, hours, days) {
    amount = +amount || 0; hours = +hours || 39; days = +days || 5;
    switch (period) {
      case "month": return amount * 12;
      case "fortnight": return amount * 26;
      case "week": return amount * 52;
      case "day": return amount * days * 52;
      case "hour": return amount * hours * 52;
      default: return amount;
    }
  }

  // Break an annual amount into periods.
  function periods(annual, hours, days) {
    hours = +hours || 39; days = +days || 5;
    return { year: annual, month: annual / 12, fortnight: annual / 26, week: annual / 52,
             day: annual / (days * 52), hour: annual / (hours * 52) };
  }

  var API = { YEARS: YEARS, calc: calc, toYear: toYear, periods: periods,
              USC_EXEMPT: USC_EXEMPT, USC_REDUCED_LIMIT: USC_REDUCED_LIMIT };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.IETAX = API;
})(this);
