/*
 * Auto-enrolment (MyFutureFund) engine: eligibility, contributions, opt-out windows and a projected pot.
 * Used by the calculator in the browser AND by tools/build_ae.py (through Node).
 * Uses the take-home pay engine (salary/js/tax.js → IETAX) when available.
 *
 * Sources (checked November 2026):
 *  - Citizens Information – Auto-enrolment pension – MyFutureFund (eligibility 23–60, €20,000; rates 1.5/1.5/0.5 rising to 6/6/2;
 *    €80,000 earnings limit; opt-out in months 7–8; suspension; re-enrolment after 2 years; State top-up = 25%, no tax relief)
 *  - MyFutureFund participant handbook – access at State Pension age (66), early access only for ill-health,
 *    tax-free growth, up to 25% tax-free lump sum, balance taxed as income.
 *  Projections are illustrations only: growth, charges and pay rises are assumptions the user can change.
 */
(function (root) {
  "use strict";
  var START = 2026;                         // scheme started 1 January 2026
  var STAGES = [[1, 3, 0.015, 0.015, 0.005], [4, 6, 0.03, 0.03, 0.01], [7, 9, 0.045, 0.045, 0.015], [10, 99, 0.06, 0.06, 0.02]];
  var CAP = 80000, MIN_PAY = 20000, AGE_MIN = 23, AGE_MAX = 60, PENSION_AGE = 66;

  function r0(x) { return Math.round(x); }
  function r2(x) { return Math.round(x * 100) / 100; }

  // Contribution rates for a calendar year (scheme year = calendar year − 2025).
  function ratesFor(year) {
    var sy = Math.max(1, year - START + 1);
    for (var i = 0; i < STAGES.length; i++) if (sy >= STAGES[i][0] && sy <= STAGES[i][1]) return { schemeYear: sy, employee: STAGES[i][2], employer: STAGES[i][3], state: STAGES[i][4], stage: i + 1 };
  }
  function stageYears() {
    return STAGES.map(function (s) { return { from: START + s[0] - 1, to: s[1] === 99 ? null : START + s[1] - 1, employee: s[2], employer: s[3], state: s[4] }; });
  }

  function contributions(salary, year) {
    var r = ratesFor(year), pay = Math.min(Math.max(0, salary), CAP);
    var e = pay * r.employee, er = pay * r.employer, s = pay * r.state;
    return { year: year, rates: r, pay: pay, employee: r2(e), employer: r2(er), state: r2(s), total: r2(e + er + s), capped: salary > CAP };
  }

  function eligibility(o) {
    var age = +o.age, pay = +o.salary;
    if (o.payrollPension) return { status: "exempt", text: "You're not auto-enrolled for a job where you already pay into a pension through payroll." };
    if (age >= AGE_MIN && age <= AGE_MAX && pay >= MIN_PAY) return { status: "auto", text: "You'll be automatically enrolled: you're aged 23–60, earn €20,000 or more and don't pay into a pension through payroll." };
    if (age >= 18 && age < PENSION_AGE) return { status: "optin", text: age < AGE_MIN || age > AGE_MAX ? "You're outside the 23–60 age range, so you're not auto-enrolled – but you can choose to join (opt in) as an employee up to age 66." : "You earn under €20,000, so you're not auto-enrolled – but you can choose to join (opt in)." };
    return { status: "none", text: "MyFutureFund is for employees aged 18 up to the pension age of 66." };
  }

  // Opt-out windows: months 7–8 after enrolment, and months 7–8 after each rate increase.
  function windows(enrolISO) {
    var p = enrolISO.split("-"), y = +p[0], m = +p[1] - 1;
    function add(yy, mm, n) { var d = new Date(Date.UTC(yy, mm + n, 1)); return d.toISOString().slice(0, 7); }
    var out = [{ reason: "After joining", from: add(y, m, 6), to: add(y, m, 7) }];
    [2029, 2032, 2035].forEach(function (yr) { if (yr > y || (yr === y && m === 0)) out.push({ reason: "After the " + yr + " rate increase", from: yr + "-07", to: yr + "-08" }); });
    return out;
  }

  /* Projection.
   * o = { salary, age, startYear (default this year), growth (% a year, default 4), payRise (% a year, default 2.5), charge (% a year, default 0.5),
   *       inflation (% a year, default 2), existing (current pot) } */
  function project(o) {
    var age = +o.age, salary = +o.salary, yr = +o.startYear || new Date().getFullYear();
    var g = (o.growth == null ? 4 : +o.growth) / 100, pr = (o.payRise == null ? 2.5 : +o.payRise) / 100, ch = (o.charge == null ? 0.5 : +o.charge) / 100, inf = (o.inflation == null ? 2 : +o.inflation) / 100;
    var pot = +o.existing || 0, paidIn = { employee: 0, employer: 0, state: 0 }, rows = [], years = Math.max(0, PENSION_AGE - age);
    for (var i = 0; i < years; i++) {
      var c = contributions(salary, yr + i);
      pot = pot * (1 + g - ch) + c.total * (1 + (g - ch) / 2); // contributions spread through the year
      paidIn.employee += c.employee; paidIn.employer += c.employer; paidIn.state += c.state;
      rows.push({ age: age + i + 1, year: yr + i, salary: r0(salary), contrib: r2(c.total), pot: r0(pot) });
      salary *= 1 + pr;
    }
    var real = pot / Math.pow(1 + inf, years);
    var lump = pot * 0.25;
    return { years: years, pot: r0(pot), potToday: r0(real), employee: r0(paidIn.employee), employer: r0(paidIn.employer), state: r0(paidIn.state),
             growth: r0(pot - paidIn.employee - paidIn.employer - paidIn.state - (+o.existing || 0)), lumpSum: r0(lump), rest: r0(pot - lump), rows: rows };
  }

  // Effect on take-home pay (contributions come from pay after tax – no tax relief).
  function payImpact(salary, year) {
    var c = contributions(salary, year);
    var T = root.IETAX || null;
    if (!T && typeof require === "function") { try { T = require("../../salary/js/tax.js"); } catch (e) { T = null; } }
    var net = T ? T.calc({ year: Math.min(Math.max(year, 2025), 2027), gross: salary }).net : null;
    var marginal = T ? T.calc({ year: Math.min(Math.max(year, 2025), 2027), gross: salary }).marginalRate : null;
    // A workplace pension with tax relief: the same employee contribution costs (1 - income tax rate) of itself.
    var band = year <= 2026 ? 44000 : 46500, taxRate = salary > band ? 0.4 : 0.2;
    return { contributions: c, netBefore: net ? r0(net) : null, netAfter: net ? r0(net - c.employee) : null, perMonth: r2(c.employee / 12), perWeek: r2(c.employee / 52),
             addedPerMonth: r2((c.employer + c.state) / 12), marginal: marginal, reliefEquivalent: r2(c.employee * taxRate), stateTopUp: c.state, higherRate: salary > band };
  }

  var API = { START: START, STAGES: STAGES, CAP: CAP, MIN_PAY: MIN_PAY, AGE_MIN: AGE_MIN, AGE_MAX: AGE_MAX, PENSION_AGE: PENSION_AGE,
              ratesFor: ratesFor, stageYears: stageYears, contributions: contributions, eligibility: eligibility, windows: windows, project: project, payImpact: payImpact };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.IEAE = API;
})(this);
