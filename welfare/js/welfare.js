/*
 * Irish social welfare rates (2026 and Budget 2027), Christmas Bonus and payment-date helpers.
 * Used by the calculators in the browser AND by tools/build_welfare.py (through Node).
 *
 * Sources (checked November 2026):
 *  - Department of Social Protection – Budget 2027 factsheet: maximum weekly rates from January 2027
 *  - Citizens Information – Social welfare rates 2026; Christmas Bonus (100%, week starting 7 December 2026); Child Benefit (€140, first Tuesday)
 *  - 2026 personal rates = 2027 rate minus the €10 Budget 2027 increase, where the Department confirms a €10 increase;
 *    otherwise the 2026 rate is left blank (null) rather than guessed.
 */
(function (root) {
  "use strict";
  // freq: "week" | "month" | "year" | "once"; xmas: gets the Christmas Bonus; iqa: increase for a qualified adult (2027)
  // r26/r27: personal rate; qc: gets Child Support Payment for each child
  var P = {
    "state-pension-contributory": { name: "State Pension (Contributory)", cat: "Pensions", r26: 299.30, r26_80: 309.30, r27: 309.30, r27_80: 319.30, iqa: 206.10, iqa66: 277.40, qc: true, xmas: true, prsi: true },
    "state-pension-non-contributory": { name: "State Pension (Non-Contributory)", cat: "Pensions", r26: 288, r26_80: 298, r27: 298, r27_80: 308, iqa: 196.80, qc: true, xmas: true, means: true },
    "jobseekers-allowance": { name: "Jobseeker's Allowance", cat: "Jobseekers", r26: 254, r27: 264, u25: 173.70, iqa: 175.20, qc: true, xmas: "12m", means: true },
    "jobseekers-benefit": { name: "Jobseeker's Benefit", cat: "Jobseekers", r26: 254, r27: 264, iqa: 175.20, qc: true, xmas: false, prsi: true },
    "jobseekers-pay-related-benefit": { name: "Jobseeker's Pay-Related Benefit", cat: "Jobseekers", r26: null, r27: null, xmas: false, prsi: true, special: "jprb" },
    "jobseekers-transitional-payment": { name: "Jobseeker's Transitional Payment", cat: "Families", r26: 254, r27: 264, qc: true, xmas: true, means: true, note: "Paid at the same rate as Jobseeker's Allowance." },
    "illness-benefit": { name: "Illness Benefit", cat: "Illness & disability", r26: 254, r27: 264, iqa: 175.20, qc: true, xmas: "12m", prsi: true },
    "invalidity-pension": { name: "Invalidity Pension", cat: "Illness & disability", r26: 259.50, r27: 269.50, iqa: 192.50, qc: true, xmas: true, prsi: true },
    "disability-allowance": { name: "Disability Allowance", cat: "Illness & disability", r26: 254, r27: 264, iqa: 175.20, qc: true, xmas: true, means: true },
    "blind-pension": { name: "Blind Pension", cat: "Illness & disability", r26: 254, r27: 264, iqa: 175.20, qc: true, xmas: true, means: true },
    "disablement-benefit": { name: "Disablement Benefit", cat: "Illness & disability", r26: null, r27: 295, qc: true, xmas: true, prsi: true },
    "carers-allowance": { name: "Carer's Allowance", cat: "Carers", r26: 270, r26_66: 308, r27: 280, r27_66: 318, qc: true, xmas: true, means: true },
    "carers-benefit": { name: "Carer's Benefit", cat: "Carers", r26: 271, r27: 281, qc: true, xmas: true, prsi: true },
    "carers-support-grant": { name: "Carer's Support Grant", cat: "Carers", r26: 2000, r27: 2000, freq: "year", xmas: false },
    "domiciliary-care-allowance": { name: "Domiciliary Care Allowance", cat: "Carers", r26: null, r27: 380, freq: "month", xmas: true },
    "one-parent-family-payment": { name: "One-Parent Family Payment", cat: "Families", r26: 254, r27: 264, qc: true, xmas: true, means: true },
    "working-family-payment": { name: "Working Family Payment", cat: "Families", r26: null, r27: null, xmas: false, special: "wfp" },
    "child-benefit": { name: "Child Benefit", cat: "Families", r26: 140, r27: 140, freq: "month", xmas: false, perChild: true },
    "child-support-payment": { name: "Child Support Payment", cat: "Families", r26: 58, r27: 64, r26_12: 78, r27_12: 84, perChild: true, xmas: false },
    "maternity-benefit": { name: "Maternity Benefit", cat: "Families", r26: 299, r27: 309, xmas: false, prsi: true },
    "paternity-benefit": { name: "Paternity Benefit", cat: "Families", r26: 299, r27: 309, xmas: false, prsi: true },
    "parents-benefit": { name: "Parent's Benefit", cat: "Families", r26: 299, r27: 309, xmas: false, prsi: true },
    "adoptive-benefit": { name: "Adoptive Benefit", cat: "Families", r26: 299, r27: 309, xmas: false, prsi: true },
    "guardians-payment": { name: "Guardian's Payment", cat: "Families", r26: null, r27: 247, xmas: true },
    "bereaved-partners-pension": { name: "Bereaved Partner's Pension (Contributory)", cat: "Pensions", r26: 259.50, r27: 269.50, r27_66: 309.30, r27_80: 319.30, qc: true, xmas: true, prsi: true },
    "farm-assist": { name: "Farm Assist", cat: "Jobseekers", r26: 254, r27: 264, iqa: 175.20, qc: true, xmas: true, means: true },
    "supplementary-welfare-allowance": { name: "Supplementary Welfare Allowance", cat: "Jobseekers", r26: null, r27: 262, u25: 173.70, iqa: 175.20, qc: true, xmas: "12m", means: true },
    "fuel-allowance": { name: "Fuel Allowance", cat: "Extras", r26: 38, r27: 43, xmas: false, means: true, season: true },
    "living-alone-increase": { name: "Living Alone Increase", cat: "Extras", r26: 22, r27: 25, xmas: false },
    "cost-of-disability-payment": { name: "Cost of Disability Payment", cat: "Illness & disability", r26: null, r27: 500, freq: "once", xmas: false }
  };
  Object.keys(P).forEach(function (k) { P[k].freq = P[k].freq || "week"; P[k].slug = k; });

  var XMAS = { year: 2026, pct: 100, min: 20, week: "2026-12-07" };
  var JPRB = [{ weeks: "1–13", pct: 60, cap: 450 }, { weeks: "14–26", pct: 55, cap: 375 }, { weeks: "27–39", pct: 50, cap: 300 }];
  var JPRB_SHORT = { pct: 50, cap: 300, weeks: 26 }, JPRB_MIN = 125;
  var WFP = { 2027: [795, 896, 997, 1088, 1214, 1330, 1466, 1562] };

  function r2(x) { return Math.round(x * 100) / 100; }

  /* Weekly amount for a payment.
   * o = { year: 2026|2027, age (for 80+ / 66+ rates), under25, adult: bool (qualified adult), adultAge66, kidsUnder12, kids12, livingAlone, fuel } */
  function weekly(key, o) {
    var p = P[key]; o = o || {};
    var y = o.year === 2026 ? 2026 : 2027, rows = [], missing = false;
    var base = y === 2026 ? p.r26 : p.r27;
    if (y === 2027 && o.age >= 80 && p.r27_80) base = p.r27_80;
    else if (y === 2027 && o.age >= 66 && p.r27_66) base = p.r27_66;
    else if (y === 2026 && o.age >= 80 && p.r26_80) base = p.r26_80;
    else if (y === 2026 && o.age >= 66 && p.r26_66) base = p.r26_66;
    if (y === 2027 && o.under25 && p.u25) base = p.u25;
    if (base == null) { missing = true; base = 0; }
    rows.push({ name: p.name + " (personal rate)", amount: base });
    if (o.adult && p.iqa && y === 2027) rows.push({ name: "Increase for a Qualified Adult", amount: (o.adultAge66 && p.iqa66) ? p.iqa66 : p.iqa });
    if (p.qc) {
      var cu = y === 2026 ? 58 : 64, co = y === 2026 ? 78 : 84;
      if (o.kidsUnder12) rows.push({ name: "Child Support Payment – " + o.kidsUnder12 + " under 12", amount: cu * o.kidsUnder12 });
      if (o.kids12) rows.push({ name: "Child Support Payment – " + o.kids12 + " aged 12+", amount: co * o.kids12 });
    }
    if (o.livingAlone && (p.cat === "Pensions" || key === "disability-allowance" || key === "invalidity-pension" || key === "blind-pension"))
      rows.push({ name: "Living Alone Increase", amount: y === 2026 ? 22 : 25 });
    var total = rows.reduce(function (s, x) { return s + x.amount; }, 0);
    var out = { key: key, name: p.name, year: y, rows: rows, weekly: r2(total), missing: missing };
    if (p.freq === "week") { out.monthly = r2(total * 52 / 12); out.yearly = r2(total * 52); }
    if (o.fuel) out.fuel = { weekly: y === 2026 ? 38 : 43, season: r2((y === 2026 ? 38 : 43) * 28) };
    out.xmas = xmasBonus(key, total);
    return out;
  }

  // Christmas Bonus: 100% of the normal weekly payment (minimum €20) for qualifying long-term payments.
  function xmasBonus(key, weeklyAmount) {
    var p = P[key], q = p.xmas;
    if (!q) return { eligible: false };
    var amt = Math.max(XMAS.min, weeklyAmount * XMAS.pct / 100);
    if (key === "domiciliary-care-allowance") amt = Math.max(XMAS.min, (p.r27 * 12 / 52));
    return { eligible: q === true ? true : "conditional", condition: q === "12m" ? "if you've been getting it for 12 months or more" : "", amount: r2(amt), week: XMAS.week };
  }

  // Jobseeker's Pay-Related Benefit for average weekly earnings and number of PRSI years.
  function jprb(avgWeekly, prsiYears) {
    if (prsiYears >= 5) return JPRB.map(function (b) { return { weeks: b.weeks, pct: b.pct, amount: r2(Math.max(JPRB_MIN, Math.min(b.cap, avgWeekly * b.pct / 100))) }; });
    if (prsiYears >= 2) return [{ weeks: "1–26", pct: JPRB_SHORT.pct, amount: r2(Math.max(JPRB_MIN, Math.min(JPRB_SHORT.cap, avgWeekly * JPRB_SHORT.pct / 100))) }];
    return [];
  }

  // Working Family Payment (2027): 60% of the gap between family income and the threshold.
  function wfp(kids, familyWeekly) {
    var t = WFP[2027][Math.max(1, Math.min(8, kids)) - 1];
    var gap = t - familyWeekly;
    return { threshold: t, weekly: gap > 0 ? r2(gap * 0.6) : 0 };
  }

  // Child Benefit: first Tuesday of each month.
  function childBenefitDates(year) {
    var out = [];
    for (var m = 0; m < 12; m++) {
      var d = new Date(Date.UTC(year, m, 1));
      while (d.getUTCDay() !== 2) d.setUTCDate(d.getUTCDate() + 1);
      out.push(d.toISOString().slice(0, 10));
    }
    return out;
  }

  var API = { PAYMENTS: P, XMAS: XMAS, JPRB: JPRB, JPRB_SHORT: JPRB_SHORT, JPRB_MIN: JPRB_MIN, WFP: WFP, weekly: weekly, xmasBonus: xmasBonus, jprb: jprb, wfp: wfp, childBenefitDates: childBenefitDates };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.IEWELF = API;
})(this);
